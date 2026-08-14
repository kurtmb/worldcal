#!/usr/bin/env python3
"""Run the A.9 eight-story packet sequentially. Writes gitignored files under data/packets/a09/."""

from __future__ import annotations

import json
from pathlib import Path

import boto3

from worldcal.generate import generate_sequential
from worldcal.packet import A09_SAMPLING, PACKET_ROOT, a09_jobs
from worldcal.schemas import new_id
from worldcal.storage import Storage

PACKET_ID = "a09"


def main() -> None:
    jobs = a09_jobs()
    if len(jobs) != 8:
        raise SystemExit(f"expected 8 jobs, got {len(jobs)}")
    out_dir = PACKET_ROOT / PACKET_ID
    out_dir.mkdir(parents=True, exist_ok=True)
    client = boto3.client("bedrock-runtime", region_name="us-west-2")
    run_id = f"{PACKET_ID}-{new_id()[:8]}"
    store = Storage(Path("data") / "worldcal.sqlite", Path("data") / "raw")
    records = generate_sequential(client, jobs, run_id=run_id)

    index_lines = [
        f"# Packet {PACKET_ID}",
        "",
        f"run_id: `{run_id}`",
        f"sampling: temperature={A09_SAMPLING.temperature}, top_p={A09_SAMPLING.top_p}, "
        f"max_tokens={A09_SAMPLING.max_tokens}, seed={A09_SAMPLING.seed}",
        "These are not official labels. Read with docs/review-guide.md §Stories.",
        "",
        "| # | file | model | prompt | words | seed | request_id | ok |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    meta = []
    for i, ((model, prompt, sampling), rec) in enumerate(zip(jobs, records, strict=True), start=1):
        store.insert_generation(rec)
        stem = f"{i:02d}_{model.id}_{prompt.id}_{rec.id[:8]}"
        text_path = out_dir / f"{stem}.txt"
        header = (
            f"packet: {PACKET_ID}\n"
            f"generation_id: {rec.id}\n"
            f"run_id: {rec.run_id}\n"
            f"model: {model.display_name} ({model.bedrock_model_id})\n"
            f"prompt_id: {prompt.id}\n"
            f"prompt_hash: {prompt.sha256}\n"
            f"seed: {sampling.seed}\n"
            f"request_id: {rec.request_id}\n"
            f"stop_reason: {rec.stop_reason}\n"
            f"error: {rec.error}\n"
            f"tokens: in={rec.input_tokens} out={rec.output_tokens}\n"
            f"---\n\n"
        )
        body = rec.raw_text if rec.succeeded else f"[FAILED] {rec.error}"
        text_path.write_text(header + body + "\n", encoding="utf-8")
        words = len(body.split()) if rec.succeeded else 0
        index_lines.append(
            f"| {i} | `{text_path.name}` | {model.id} | {prompt.id} | {words} | "
            f"{sampling.seed} | {rec.request_id} | {rec.succeeded} |"
        )
        meta.append(
            {
                "n": i,
                "file": text_path.name,
                "generation_id": rec.id,
                "model_id": model.id,
                "prompt_id": prompt.id,
                "word_count": words,
                "seed": sampling.seed,
                "request_id": rec.request_id,
                "succeeded": rec.succeeded,
            }
        )
    (out_dir / "index.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    (out_dir / "index.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    failed = [m for m in meta if not m["succeeded"]]
    print(f"wrote {out_dir} run_id={run_id} ok={len(meta) - len(failed)}/{len(meta)}")
    if failed:
        raise SystemExit(f"failures: {failed}")


if __name__ == "__main__":
    main()
