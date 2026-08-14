from __future__ import annotations

from worldcal.models import NOVA_2_LITE, SONNET_46
from worldcal.packet import A09_SAMPLING, load_a09_prompts


def sniff_jobs() -> list[tuple]:
    """Larger-model sniff: Nova 2 Lite × 2 prompts × 2, Sonnet 4.6 × 2 prompts × 1. Seed always None."""
    prompts = load_a09_prompts()
    jobs = []
    for prompt in prompts:
        jobs.append((NOVA_2_LITE, prompt, A09_SAMPLING))
        jobs.append((NOVA_2_LITE, prompt, A09_SAMPLING))
    for prompt in prompts:
        jobs.append((SONNET_46, prompt, A09_SAMPLING))
    return jobs
