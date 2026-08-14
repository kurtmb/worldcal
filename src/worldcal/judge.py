from __future__ import annotations

import json
import re
from typing import Any

from worldcal.models import JUDGE_MODEL
from worldcal.schemas import (
    AnnotationRecord,
    EvidenceSpan,
    GenerationRecord,
    NameGuess,
    PromptRecord,
    RelationshipLabel,
    SamplingConfig,
)

JUDGE_SAMPLING = SamplingConfig(temperature=0.0, top_p=0.9, max_tokens=800, seed=None)


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def parse_judge_json(text: str) -> dict[str, Any]:
    raw = _strip_fences(text)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def annotation_from_payload(generation_id: str, payload: dict[str, Any]) -> AnnotationRecord:
    spans = [
        EvidenceSpan(field=str(item.get("field", "")), quote=str(item.get("quote", "")))
        for item in payload.get("evidence_spans") or []
    ]
    return AnnotationRecord(
        generation_id=generation_id,
        relationship=RelationshipLabel(payload["relationship"]),
        partnership_term=payload.get("partnership_term"),
        adult1_name=payload.get("adult1_name"),
        adult2_name=payload.get("adult2_name"),
        name_guess=NameGuess(payload.get("name_guess") or "MISSING"),
        explicit_lgbtq=bool(payload.get("explicit_lgbtq", False)),
        evidence_spans=spans,
        notes=str(payload.get("notes") or ""),
    )


def judge_story(client, story: str, generation_id: str, run_id: str) -> tuple[AnnotationRecord, GenerationRecord]:
    from worldcal.judge_prompt import JUDGE_SYSTEM, JUDGE_USER_TEMPLATE

    prompt = PromptRecord(
        id="judge-extract-v0",
        scenario="judge",
        text=JUDGE_USER_TEMPLATE.format(story=story.strip()),
        version="DRAFT",
    )
    # Converse system prompt via extra kw by wrapping generate? generate() doesn't take system.
    # Put rules in the user prompt for v0, plus a system message through a thin wrapper.
    rec = _converse_with_system(client, prompt, JUDGE_SYSTEM, run_id, generation_id)
    if not rec.succeeded:
        raise RuntimeError(f"judge failed: {rec.error}")
    payload = parse_judge_json(rec.raw_text)
    return annotation_from_payload(generation_id, payload), rec


def _converse_with_system(client, prompt, system: str, run_id: str, generation_id: str) -> GenerationRecord:
    """One judge call. Temperature 0. Not a study story generation."""
    from worldcal.generate import _extract_text, _inference_config
    import time

    model = JUDGE_MODEL
    sampling = JUDGE_SAMPLING
    kwargs = {
        "modelId": model.bedrock_model_id,
        "system": [{"text": system}],
        "messages": [{"role": "user", "content": [{"text": prompt.text}]}],
        "inferenceConfig": _inference_config(sampling, model),
    }
    started = time.perf_counter()
    response = client.converse(**kwargs)
    text = _extract_text(response)
    usage = response.get("usage") or {}
    meta = response.get("ResponseMetadata") or {}
    return GenerationRecord(
        id=generation_id + "-judge",
        run_id=run_id,
        model_id=model.id,
        prompt_id=prompt.id,
        prompt_hash=prompt.sha256,
        raw_text=text,
        input_tokens=usage.get("inputTokens"),
        output_tokens=usage.get("outputTokens"),
        latency_ms=int((time.perf_counter() - started) * 1000),
        request_id=meta.get("RequestId"),
        stop_reason=response.get("stopReason"),
        sampling=sampling,
    )
