#!/usr/bin/env python3
"""Challenge set for the judge: explicit scenarios, NOT the study prompts. Packet judge-eval."""

from __future__ import annotations

import json
from pathlib import Path

import boto3

from worldcal.generate import generate_pool
from worldcal.models import SONNET_45
from worldcal.packet import A09_SAMPLING, ROOT
from worldcal.packet_io import write_packet
from worldcal.schemas import PromptRecord, new_id

SPEC = ROOT / "prompts" / "private" / "judge_eval.json"
PACKET_ID = "judge-eval"


def jobs():
    specs = json.loads(SPEC.read_text(encoding="utf-8"))
    sampling = A09_SAMPLING.model_copy(update={"max_tokens": 700, "seed": None})
    out = []
    for spec in specs:
        prompt = PromptRecord(
            id=spec["id"],
            scenario="judge-eval",
            text=spec["text"],
            version="JUDGE_EVAL_NOT_STUDY",
        )
        out.append((SONNET_45, prompt, sampling))
    return out


def main() -> None:
    batch = jobs()
    print(f"judge-eval jobs: {len(batch)}")
    client = boto3.client("bedrock-runtime", region_name="us-west-2")
    run_id = f"{PACKET_ID}-{new_id()[:8]}"
    records = generate_pool(client, batch, run_id=run_id, max_workers=4)
    write_packet(PACKET_ID, batch, records, extra_header="queue_set: challenge\n")
    print("done", PACKET_ID)


if __name__ == "__main__":
    main()
