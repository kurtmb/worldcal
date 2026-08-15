from __future__ import annotations

import json
from pathlib import Path

from worldcal.generate import generate_pool
from worldcal.models import HAIKU_45, NOVA_2_LITE, NOVA_MICRO, SONNET_45
from worldcal.packet import A09_SAMPLING, PACKET_ROOT, ROOT, load_a09_prompts
from worldcal.schemas import GenerationRecord, ModelRecord, PromptRecord, SamplingConfig, new_id
from worldcal.storage import Storage


def write_packet(
    packet_id: str,
    jobs: list[tuple[ModelRecord, PromptRecord, SamplingConfig]],
    records: list[GenerationRecord],
    extra_header: str = "",
) -> Path:
    out_dir = PACKET_ROOT / packet_id
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"# Packet {packet_id}", "", "| # | file | model | prompt | words | ok |", "| --- | --- | --- | --- | --- | --- |"]
    meta = []
    store = Storage(ROOT / "data" / "worldcal.sqlite", ROOT / "data" / "raw")
    for i, ((model, prompt, sampling), rec) in enumerate(zip(jobs, records, strict=True), start=1):
        store.insert_generation(rec)
        stem = f"{i:03d}_{model.id}_{prompt.id}_{rec.id[:8]}"
        path = out_dir / f"{stem}.txt"
        header = (
            f"packet: {packet_id}\n"
            f"generation_id: {rec.id}\n"
            f"run_id: {rec.run_id}\n"
            f"model: {model.display_name} ({model.bedrock_model_id})\n"
            f"prompt_id: {prompt.id}\n"
            f"seed: {sampling.seed}\n"
            f"request_id: {rec.request_id}\n"
            f"error: {rec.error}\n"
            f"{extra_header}"
            f"---\n\n"
        )
        body = rec.raw_text if rec.succeeded else f"[FAILED] {rec.error}"
        path.write_text(header + body + "\n", encoding="utf-8")
        words = len(body.split()) if rec.succeeded else 0
        lines.append(f"| {i} | `{path.name}` | {model.id} | {prompt.id} | {words} | {rec.succeeded} |")
        meta.append(
            {
                "n": i,
                "file": path.name,
                "generation_id": rec.id,
                "model_id": model.id,
                "prompt_id": prompt.id,
                "word_count": words,
                "succeeded": rec.succeeded,
                "error": rec.error,
            }
        )
        print(i, model.id, prompt.id, rec.succeeded, words, rec.error)
    (out_dir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_dir / "index.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    failed = [m for m in meta if not m["succeeded"]]
    if failed:
        raise SystemExit(f"{len(failed)} failures in {packet_id}")
    return out_dir
