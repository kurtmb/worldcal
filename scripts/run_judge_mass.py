#!/usr/bin/env python3
"""Run Sonnet 4.5 judge on every unlabeled study story; write data/annotations/judge.jsonl."""

from __future__ import annotations

import json
from pathlib import Path

import boto3

from worldcal.judge import judge_story
from worldcal.packet import PACKET_ROOT, ROOT
from worldcal.queue import load_saved_annotations, parse_story_file
from worldcal.schemas import new_id

OUT = ROOT / "data" / "annotations" / "judge.jsonl"
SKIP_PACKETS = {"judge-eval"}


def main() -> None:
    human = load_saved_annotations()
    already = set()
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            if line.strip():
                already.add(json.loads(line)["generation_id"])
    client = boto3.client("bedrock-runtime", region_name="us-west-2")
    run_id = f"judge-mass-{new_id()[:8]}"
    n = 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("a", encoding="utf-8") as handle:
        for path in sorted(PACKET_ROOT.glob("*/*.txt")):
            story = parse_story_file(path)
            gid = story["generation_id"]
            if story["packet"] in SKIP_PACKETS:
                continue
            if gid in already:
                continue
            ann, rec = judge_story(client, story["story"], gid, run_id)
            row = ann.model_dump()
            row["judge_model"] = "sonnet-4.5"
            row["request_id"] = rec.request_id
            row["human_relationship"] = (human.get(gid) or {}).get("relationship")
            handle.write(json.dumps(row) + "\n")
            n += 1
            print(n, gid[:8], ann.relationship.value, story["packet"])
    print("wrote", n, "judge rows")


if __name__ == "__main__":
    main()
