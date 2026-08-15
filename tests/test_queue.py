from pathlib import Path

from worldcal.packet import PACKET_ROOT
from worldcal.queue import parse_story_file


def test_parse_sniff_story() -> None:
    path = PACKET_ROOT / "a09-sniff" / "01_nova-2-lite_family_school_morning_v0_b7705e48.txt"
    story = parse_story_file(path)
    assert story["generation_id"].startswith("b7705e48")
    assert "mom" in story["story"].lower()
    assert story["scene"].startswith("Two parents")
    assert "Nova" not in story["scene"]


def test_queue_hides_model_and_imports_gold(tmp_path: Path, monkeypatch) -> None:
    import worldcal.queue as q

    monkeypatch.setattr(q, "ANNOTATION_PATH", tmp_path / "human.jsonl")
    queue = q.build_queue()
    assert len(queue) >= 14
    public = queue[0]["public"]
    assert "model" not in public
    assert "story" in public
    labeled = [item for item in queue if item["public"]["labeled"]]
    assert len(labeled) >= 14


def test_append_annotation_roundtrip(tmp_path: Path, monkeypatch) -> None:
    import worldcal.queue as q

    monkeypatch.setattr(q, "ANNOTATION_PATH", tmp_path / "human.jsonl")
    row = q.append_annotation(
        {
            "generation_id": "abc",
            "relationship": "INDETERMINATE",
            "adult1_name": "Alex",
            "adult2_name": "Jordan",
            "name_guess": "NAME_AMBIGUOUS",
            "evidence_quote": "partners",
            "notes": "names only",
        }
    )
    assert row["relationship"] == "INDETERMINATE"
    saved = q.load_saved_annotations(tmp_path / "human.jsonl")
    assert saved["abc"]["adult1_name"] == "Alex"
    assert saved["abc"]["evidence_spans"][0]["quote"] == "partners"
