#!/usr/bin/env python3
"""40 Nova Micro stories (20 per prompt), sequential, seed omitted. Packet b40."""

from __future__ import annotations

import json
from pathlib import Path

import boto3

from worldcal.b40 import b40_jobs
from worldcal.generate import generate_sequential
from worldcal.packet import A09_SAMPLING, PACKET_ROOT
from worldcal.schemas import new_id
from worldcal.storage import Storage

PACKET_ID = "b40"


def main() -> None:
    jobs = b40_jobs()
    if len(jobs) != 40:
        raise SystemExit(f"expected 40 jobs, got {len(jobs)}")
    out_dir = PACKET_ROOT / PACKET_ID
    out_dir.mkdir(parents=True, exist_ok=True)
    client = boto3.client("bedrock-runtime", region_name="us-west-2")
    run_id = f"{PACKET_ID}-{new_id()[:8]}"
    store = Storage(Path("data") / "worldcal.sqlite", Path("data") / "raw")
    records = generate_sequential(client, jobs, run_id=run_id)
    lines = [
        f"# Packet {PACKET_ID}",
        "",
        f"run_id: `{run_id}`",
        f"sampling: temperature={A09_SAMPLING.temperature}, seed={A09_SAMPLING.seed}",
        "",
        "| # | file | prompt | words | ok |",
        "| --- | --- | --- | --- | --- |",
    ]
    meta = []
    failed = []
    for i, ((model, prompt, sampling), rec) in enumerate(zip(jobs, records, strict=True), start=1):
        store.insert_generation(rec)
        stem = f"{i:02d}_{model.id}_{prompt.id}_{rec.id[:8]}"
        path = out_dir / f"{stem}.txt"
        header = (
            f"packet: {PACKET_ID}\n"
            f"generation_id: {rec.id}\n"
            f"run_id: {rec.run_id}\n"
            f"model: {model.display_name} ({model.bedrock_model_id})\n"
            f"prompt_id: {prompt.id}\n"
            f"seed: {sampling.seed}\n"
            f"request_id: {rec.request_id}\n"
            f"error: {rec.error}\n"
            f"---\n\n"
        )
        body = rec.raw_text if rec.succeeded else f"[FAILED] {rec.error}"
        path.write_text(header + body + "\n", encoding="utf-8")
        words = len(body.split()) if rec.succeeded else 0
        lines.append(f"| {i} | `{path.name}` | {prompt.id} | {words} | {rec.succeeded} |")
        row = {
            "n": i,
            "file": path.name,
            "generation_id": rec.id,
            "model_id": model.id,
            "prompt_id": prompt.id,
            "word_count": words,
            "succeeded": rec.succeeded,
            "error": rec.error,
        }
        meta.append(row)
        print(i, prompt.id, rec.succeeded, words, rec.error)
        if not rec.succeeded:
            failed.append(row)
    (out_dir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_dir / "index.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    if failed:
        raise SystemExit(f"failures: {len(failed)}")
    print(f"wrote {out_dir} run_id={run_id}")


if __name__ == "__main__":
    main()
