from __future__ import annotations

from pathlib import Path

from worldcal.models import HAIKU_45, NOVA_MICRO
from worldcal.schemas import PromptRecord, SamplingConfig

ROOT = Path(__file__).resolve().parents[2]
PRIVATE_PROMPTS = ROOT / "prompts" / "private"
PACKET_ROOT = ROOT / "data" / "packets"

A09_PROMPTS = (
    ("family_school_morning_v0", "family", PRIVATE_PROMPTS / "family_school_morning_v0.txt"),
    ("couple_first_home_v0", "couple", PRIVATE_PROMPTS / "couple_first_home_v0.txt"),
)

A09_MODELS = (NOVA_MICRO, HAIKU_45)
A09_REPEATS = 2

A09_SAMPLING = SamplingConfig(
    temperature=0.7,
    top_p=0.9,
    max_tokens=900,
    seed=None,
)


def load_a09_prompts() -> list[PromptRecord]:
    records: list[PromptRecord] = []
    for prompt_id, scenario, path in A09_PROMPTS:
        text = path.read_text(encoding="utf-8").strip() + "\n"
        records.append(
            PromptRecord(
                id=prompt_id,
                scenario=scenario,
                paraphrase="a",
                geography="us-national",
                text=text,
                version="DRAFT",
            )
        )
    return records


def a09_jobs() -> list[tuple]:
    """Sequential job list: each tuple is (model, prompt, sampling). Same sampling object, seed always None."""
    jobs = []
    prompts = load_a09_prompts()
    for model in A09_MODELS:
        for prompt in prompts:
            for _ in range(A09_REPEATS):
                jobs.append((model, prompt, A09_SAMPLING))
    return jobs
