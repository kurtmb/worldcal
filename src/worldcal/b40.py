from __future__ import annotations

from worldcal.models import NOVA_MICRO
from worldcal.packet import A09_SAMPLING, load_a09_prompts

B40_REPEATS = 20  # per prompt → 40 stories


def b40_jobs() -> list[tuple]:
    prompts = load_a09_prompts()
    jobs = []
    for prompt in prompts:
        for _ in range(B40_REPEATS):
            jobs.append((NOVA_MICRO, prompt, A09_SAMPLING))
    return jobs
