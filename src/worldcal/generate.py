from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any, Protocol

from botocore.exceptions import ClientError

from worldcal.schemas import (
    GenerationRecord,
    ModelRecord,
    PromptRecord,
    SamplingConfig,
    new_id,
    sha256_text,
)

RETRYABLE_ERROR_CODES = frozenset(
    {
        "ThrottlingException",
        "TooManyRequestsException",
        "ServiceUnavailableException",
        "InternalServerException",
        "ModelTimeoutException",
        "ModelErrorException",
    }
)


class ConverseClient(Protocol):
    def converse(self, **kwargs: Any) -> dict[str, Any]: ...


class GenerateError(Exception):
    pass


def _inference_config(sampling: SamplingConfig, model: ModelRecord) -> dict[str, Any]:
    config: dict[str, Any] = {"maxTokens": sampling.max_tokens}
    if model.sampling_knobs == "temperature_only":
        config["temperature"] = sampling.temperature
    elif model.sampling_knobs == "top_p_only":
        config["topP"] = sampling.top_p
    else:
        config["temperature"] = sampling.temperature
        config["topP"] = sampling.top_p
    if sampling.seed is not None and model.seed_supported:
        config["seed"] = sampling.seed
    return config


def _extract_text(response: dict[str, Any]) -> str:
    content = response.get("output", {}).get("message", {}).get("content", [])
    parts: list[str] = []
    for block in content:
        text = block.get("text")
        if text:
            parts.append(text)
    return "".join(parts)


def _is_retryable(error: ClientError) -> bool:
    code = error.response.get("Error", {}).get("Code", "")
    return code in RETRYABLE_ERROR_CODES


def generate(
    client: ConverseClient,
    model: ModelRecord,
    prompt: PromptRecord,
    sampling: SamplingConfig,
    run_id: str,
    generation_id: str | None = None,
    max_attempts: int = 3,
) -> GenerationRecord:
    """One independent draw. Do not reuse sampling.seed across generations."""
    gid = generation_id or new_id()
    inference = _inference_config(sampling, model)
    kwargs: dict[str, Any] = {
        "modelId": model.bedrock_model_id,
        "messages": [{"role": "user", "content": [{"text": prompt.text}]}],
        "inferenceConfig": inference,
    }
    last_error: str | None = None
    retry_count = 0
    for attempt in range(1, max_attempts + 1):
        started = time.perf_counter()
        try:
            response = client.converse(**kwargs)
        except ClientError as exc:
            last_error = str(exc)
            if _is_retryable(exc) and attempt < max_attempts:
                retry_count += 1
                time.sleep(min(2 ** attempt, 8))
                continue
            return GenerationRecord(
                id=gid,
                run_id=run_id,
                model_id=model.id,
                prompt_id=prompt.id,
                prompt_hash=prompt.sha256,
                raw_text="",
                error=last_error,
                sampling=sampling,
                retry_count=retry_count,
            )
        latency_ms = int((time.perf_counter() - started) * 1000)
        text = _extract_text(response)
        usage = response.get("usage") or {}
        meta = response.get("ResponseMetadata") or {}
        if not text:
            return GenerationRecord(
                id=gid,
                run_id=run_id,
                model_id=model.id,
                prompt_id=prompt.id,
                prompt_hash=prompt.sha256,
                raw_text="",
                error="empty_response",
                latency_ms=latency_ms,
                request_id=meta.get("RequestId"),
                stop_reason=response.get("stopReason"),
                sampling=sampling,
                retry_count=retry_count,
            )
        return GenerationRecord(
            id=gid,
            run_id=run_id,
            model_id=model.id,
            prompt_id=prompt.id,
            prompt_hash=prompt.sha256,
            raw_text=text,
            input_tokens=usage.get("inputTokens"),
            output_tokens=usage.get("outputTokens"),
            latency_ms=latency_ms,
            request_id=meta.get("RequestId"),
            stop_reason=response.get("stopReason"),
            sampling=sampling,
            retry_count=retry_count,
        )
    raise GenerateError(f"exhausted retries for {gid}: {last_error}")


def generate_sequential(
    client: ConverseClient,
    jobs: Sequence[tuple[ModelRecord, PromptRecord, SamplingConfig]],
    run_id: str,
) -> list[GenerationRecord]:
    """Independent draws in order. Caller must not pass the same seed twice."""
    results: list[GenerationRecord] = []
    seen_seeds: set[int] = set()
    for model, prompt, sampling in jobs:
        if sampling.seed is not None:
            if sampling.seed in seen_seeds:
                raise GenerateError(
                    f"refusing reused seed {sampling.seed}; that would not be an independent draw"
                )
            seen_seeds.add(sampling.seed)
        results.append(generate(client, model, prompt, sampling, run_id=run_id))
    return results


def prompt_hash_check(prompt: PromptRecord) -> str:
    return sha256_text(prompt.text)
