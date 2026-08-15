#!/usr/bin/env python3
"""Study mass run: 50+50 per model for Nova Micro, Nova 2 Lite, Sonnet 4.5. Seed omitted. Packet mass-v1."""

from __future__ import annotations

import boto3

from worldcal.generate import generate_pool
from worldcal.models import NOVA_2_LITE, NOVA_MICRO, SONNET_45
from worldcal.packet import A09_SAMPLING, load_a09_prompts
from worldcal.packet_io import write_packet
from worldcal.schemas import new_id

PACKET_ID = "mass-v1"
REPEATS = 50
MODELS = (NOVA_MICRO, NOVA_2_LITE, SONNET_45)


def jobs():
    prompts = load_a09_prompts()
    sampling = A09_SAMPLING.model_copy(update={"seed": None})
    out = []
    for model in MODELS:
        for prompt in prompts:
            for _ in range(REPEATS):
                out.append((model, prompt, sampling))
    return out


def main() -> None:
    batch = jobs()
    print(f"mass jobs: {len(batch)} (expect {len(MODELS) * 2 * REPEATS})")
    client = boto3.client("bedrock-runtime", region_name="us-west-2")
    run_id = f"{PACKET_ID}-{new_id()[:8]}"
    records = generate_pool(client, batch, run_id=run_id, max_workers=5)
    write_packet(PACKET_ID, batch, records)
    print("done", PACKET_ID, run_id)


if __name__ == "__main__":
    main()
