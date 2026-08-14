from pathlib import Path

import pytest

from worldcal.schemas import GenerationRecord, SamplingConfig
from worldcal.storage import Storage, StorageError


def _record(generation_id: str, text: str = "story", error: str | None = None) -> GenerationRecord:
    return GenerationRecord(
        id=generation_id,
        run_id="run1",
        model_id="nova-micro",
        prompt_id="p1",
        prompt_hash="ph",
        raw_text="" if error else text,
        error=error,
        sampling=SamplingConfig(),
    )


def test_insert_and_get(tmp_path: Path) -> None:
    store = Storage(tmp_path / "db.sqlite", tmp_path / "raw")
    rec = _record("g1")
    store.insert_generation(rec)
    got = store.get_generation("g1")
    assert got is not None
    assert got.raw_text == "story"
    assert got.succeeded
    jsonl = (tmp_path / "raw" / "run1.jsonl").read_text(encoding="utf-8")
    assert "story" in jsonl


def test_refuses_overwrite_of_successful_generation(tmp_path: Path) -> None:
    store = Storage(tmp_path / "db.sqlite", tmp_path / "raw")
    store.insert_generation(_record("g1", text="first"))
    with pytest.raises(StorageError, match="successful generation"):
        store.insert_generation(_record("g1", text="second"))
    assert store.get_generation("g1").raw_text == "first"


def test_failed_row_may_be_replaced(tmp_path: Path) -> None:
    store = Storage(tmp_path / "db.sqlite", tmp_path / "raw")
    store.insert_generation(_record("g1", error="timeout"))
    store.insert_generation(_record("g1", text="recovered"))
    got = store.get_generation("g1")
    assert got.succeeded
    assert got.raw_text == "recovered"
