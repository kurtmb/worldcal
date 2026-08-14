from botocore.exceptions import ClientError

from worldcal.generate import _inference_config, generate, generate_sequential
from worldcal.models import NOVA_MICRO
from worldcal.schemas import PromptRecord, SamplingConfig, sha256_text


class FakeConverse:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def converse(self, **kwargs):
        self.calls.append(kwargs)
        n = len(self.calls)
        return {
            "output": {"message": {"content": [{"text": f"story-{n}"}]}},
            "stopReason": "end_turn",
            "usage": {"inputTokens": 10, "outputTokens": 4},
            "ResponseMetadata": {"RequestId": f"req-{n}"},
        }


def _prompt() -> PromptRecord:
    return PromptRecord(id="p1", scenario="family", text="Write a story.")


def test_inference_config_omits_seed_by_default() -> None:
    sampling = SamplingConfig(seed=None)
    config = _inference_config(sampling, NOVA_MICRO)
    assert "seed" not in config
    assert config["temperature"] == 0.7
    assert config["topP"] == 0.9


def test_seed_not_sent_when_model_does_not_support_it() -> None:
    sampling = SamplingConfig(seed=99)
    config = _inference_config(sampling, NOVA_MICRO)
    assert NOVA_MICRO.seed_supported is False
    assert "seed" not in config


def test_sequential_calls_are_independent_and_not_forced_identical() -> None:
    client = FakeConverse()
    prompt = _prompt()
    sampling = SamplingConfig(seed=None)
    jobs = [
        (NOVA_MICRO, prompt, sampling),
        (NOVA_MICRO, prompt, sampling),
    ]
    results = generate_sequential(client, jobs, run_id="run1")
    assert len(results) == 2
    assert results[0].raw_text == "story-1"
    assert results[1].raw_text == "story-2"
    assert results[0].response_hash != results[1].response_hash
    assert "seed" not in client.calls[0]["inferenceConfig"]
    assert "seed" not in client.calls[1]["inferenceConfig"]
    assert results[0].sampling.seed is None
    assert results[1].sampling.seed is None


def test_runner_rejects_reused_numeric_seed() -> None:
    client = FakeConverse()
    prompt = _prompt()
    seeded = SamplingConfig(seed=42)
    try:
        generate_sequential(
            client,
            [(NOVA_MICRO, prompt, seeded), (NOVA_MICRO, prompt, seeded)],
            run_id="run1",
        )
        raise AssertionError("expected reused seed to fail")
    except Exception as exc:
        assert "reused seed" in str(exc)
    assert len(client.calls) == 1


def test_does_not_retry_successful_generation() -> None:
    client = FakeConverse()
    rec = generate(
        client,
        NOVA_MICRO,
        _prompt(),
        SamplingConfig(),
        run_id="run1",
    )
    assert rec.succeeded
    assert rec.retry_count == 0
    assert len(client.calls) == 1


def test_retries_only_throttling() -> None:
    class OnceThrottle:
        def __init__(self) -> None:
            self.n = 0

        def converse(self, **kwargs):
            self.n += 1
            if self.n == 1:
                raise ClientError(
                    {"Error": {"Code": "ThrottlingException", "Message": "slow"}},
                    "Converse",
                )
            return {
                "output": {"message": {"content": [{"text": "ok"}]}},
                "stopReason": "end_turn",
                "usage": {},
                "ResponseMetadata": {"RequestId": "r"},
            }

    rec = generate(
        OnceThrottle(),
        NOVA_MICRO,
        _prompt(),
        SamplingConfig(),
        run_id="run1",
    )
    assert rec.succeeded
    assert rec.raw_text == "ok"
    assert rec.retry_count == 1


def test_prompt_hash_logged() -> None:
    client = FakeConverse()
    prompt = _prompt()
    rec = generate(client, NOVA_MICRO, prompt, SamplingConfig(), run_id="run1")
    assert rec.prompt_hash == sha256_text(prompt.text)
