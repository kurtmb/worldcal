from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from worldcal.schemas import GenerationRecord


class StorageError(Exception):
    pass


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS generations (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    model_id TEXT NOT NULL,
    prompt_id TEXT NOT NULL,
    prompt_hash TEXT NOT NULL,
    raw_text TEXT NOT NULL DEFAULT '',
    response_hash TEXT NOT NULL DEFAULT '',
    input_tokens INTEGER,
    output_tokens INTEGER,
    latency_ms INTEGER,
    request_id TEXT,
    stop_reason TEXT,
    error TEXT,
    sampling_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    retry_count INTEGER NOT NULL DEFAULT 0
);
"""


class Storage:
    """Append-only generation store. Successful rows are never overwritten."""

    def __init__(self, db_path: Path, raw_dir: Path) -> None:
        self.db_path = Path(db_path)
        self.raw_dir = Path(raw_dir)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(SCHEMA_SQL)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def insert_generation(self, record: GenerationRecord) -> None:
        existing = self.get_generation(record.id)
        if existing is not None and existing.succeeded:
            raise StorageError(
                f"refusing to overwrite successful generation {record.id}"
            )
        payload = (
            record.id,
            record.run_id,
            record.model_id,
            record.prompt_id,
            record.prompt_hash,
            record.raw_text,
            record.response_hash,
            record.input_tokens,
            record.output_tokens,
            record.latency_ms,
            record.request_id,
            record.stop_reason,
            record.error,
            record.sampling.model_dump_json(),
            record.created_at.isoformat(),
            record.retry_count,
        )
        with self._connect() as conn:
            if existing is None:
                conn.execute(
                    """
                    INSERT INTO generations (
                        id, run_id, model_id, prompt_id, prompt_hash, raw_text,
                        response_hash, input_tokens, output_tokens, latency_ms,
                        request_id, stop_reason, error, sampling_json, created_at,
                        retry_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    payload,
                )
            else:
                # Failed rows may be replaced after a transport retry of the same id.
                conn.execute(
                    """
                    UPDATE generations SET
                        run_id=?, model_id=?, prompt_id=?, prompt_hash=?, raw_text=?,
                        response_hash=?, input_tokens=?, output_tokens=?, latency_ms=?,
                        request_id=?, stop_reason=?, error=?, sampling_json=?,
                        created_at=?, retry_count=?
                    WHERE id=?
                    """,
                    payload[1:] + (record.id,),
                )
        if record.succeeded:
            self._append_jsonl(record)

    def get_generation(self, generation_id: str) -> GenerationRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM generations WHERE id = ?", (generation_id,)
            ).fetchone()
        if row is None:
            return None
        return _row_to_generation(row)

    def _append_jsonl(self, record: GenerationRecord) -> None:
        path = self.raw_dir / f"{record.run_id}.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(record.model_dump_json() + "\n")


def _row_to_generation(row: sqlite3.Row) -> GenerationRecord:
    from worldcal.schemas import SamplingConfig

    sampling = SamplingConfig.model_validate_json(row["sampling_json"])
    return GenerationRecord(
        id=row["id"],
        run_id=row["run_id"],
        model_id=row["model_id"],
        prompt_id=row["prompt_id"],
        prompt_hash=row["prompt_hash"],
        raw_text=row["raw_text"],
        response_hash=row["response_hash"],
        input_tokens=row["input_tokens"],
        output_tokens=row["output_tokens"],
        latency_ms=row["latency_ms"],
        request_id=row["request_id"],
        stop_reason=row["stop_reason"],
        error=row["error"],
        sampling=sampling,
        created_at=row["created_at"],
        retry_count=row["retry_count"],
    )
