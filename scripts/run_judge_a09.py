#!/usr/bin/env python3
"""Run Sonnet 4.5 judge on A.9 stories and compare to Kurt's gold labels. Wiring test only."""

from __future__ import annotations

import json
from pathlib import Path

import boto3

from worldcal.judge import judge_story
from worldcal.schemas import new_id

PACKET = Path("data/packets/a09")


def story_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text.split("---", 1)[-1].strip()


def main() -> None:
    gold = json.loads((PACKET / "human_labels.json").read_text(encoding="utf-8"))
    index = json.loads((PACKET / "index.json").read_text(encoding="utf-8"))
    by_id = {row["generation_id"]: row for row in index}
    client = boto3.client("bedrock-runtime", region_name="us-west-2")
    run_id = f"judge-a09-{new_id()[:8]}"
    rows = []
    for label in gold["labels"]:
        meta = by_id[label["generation_id"]]
        path = PACKET / meta["file"]
        ann, rec = judge_story(client, story_body(path), label["generation_id"], run_id)
        agree = ann.relationship.value == label["relationship"]
        rows.append(
            {
                "n": label["n"],
                "file": meta["file"],
                "human": label["relationship"],
                "judge": ann.relationship.value,
                "agree": agree,
                "judge_names": [ann.adult1_name, ann.adult2_name],
                "judge_name_guess": ann.name_guess.value,
                "human_name_guess": label["name_guess"],
                "quotes": [s.quote for s in ann.evidence_spans],
                "judge_notes": ann.notes,
                "request_id": rec.request_id,
            }
        )
        print(f"{label['n']} human={label['relationship']} judge={ann.relationship.value} agree={agree}")
    out = PACKET / "judge_vs_human.json"
    out.write_text(json.dumps({"run_id": run_id, "judge_model": "sonnet-4.5", "rows": rows}, indent=2) + "\n")
    n_agree = sum(1 for r in rows if r["agree"])
    print(f"agreement {n_agree}/{len(rows)} -> {out}")


if __name__ == "__main__":
    main()
