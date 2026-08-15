from __future__ import annotations

import json
from pathlib import Path

from worldcal.packet import PACKET_ROOT, ROOT
from worldcal.schemas import AnnotationRecord, NameGuess, RelationshipLabel

ANNOTATION_PATH = ROOT / "data" / "annotations" / "human.jsonl"

SCENE = {
    "family_school_morning_v0": "Two parents, first day of school",
    "couple_first_home_v0": "A couple moving into a first home",
}

GOLD_FILES = (
    PACKET_ROOT / "a09" / "human_labels.json",
    PACKET_ROOT / "a09-sniff" / "human_labels.json",
)


def parse_story_file(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    header, sep, body = raw.partition("---")
    if not sep:
        raise ValueError(f"no header separator in {path}")
    meta: dict[str, str] = {}
    for line in header.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    prompt_id = meta.get("prompt_id", "")
    packet = meta.get("packet", path.parent.name)
    scene = SCENE.get(prompt_id)
    if not scene:
        scene = prompt_id.replace("_", " ")
    return {
        "generation_id": meta.get("generation_id", ""),
        "prompt_id": prompt_id,
        "scene": scene,
        "story": body.strip(),
        "path": str(path),
        "packet": packet,
        "model": meta.get("model", ""),
        "word_count": len(body.split()),
        "queue_set": "challenge" if packet == "judge-eval" else "study",
    }


def list_story_files() -> list[Path]:
    files = sorted(
        p
        for p in PACKET_ROOT.glob("*/*.txt")
        if p.is_file() and not p.name.startswith(".")
    )
    return files


def load_saved_annotations(path: Path = ANNOTATION_PATH) -> dict[str, dict]:
    if not path.exists():
        return {}
    saved: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        gid = row.get("generation_id")
        if gid:
            saved[gid] = row
    return saved


def import_gold_into(path: Path = ANNOTATION_PATH) -> int:
    """Copy packet human_labels.json into the canonical JSONL once."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_saved_annotations(path)
    added = 0
    with path.open("a", encoding="utf-8") as handle:
        for gold_path in GOLD_FILES:
            if not gold_path.exists():
                continue
            payload = json.loads(gold_path.read_text(encoding="utf-8"))
            for label in payload.get("labels", []):
                gid = label["generation_id"]
                if gid in existing:
                    continue
                record = AnnotationRecord(
                    generation_id=gid,
                    relationship=RelationshipLabel(label["relationship"]),
                    partnership_term=label.get("partnership_term"),
                    adult1_name=label.get("adult1_name"),
                    adult2_name=label.get("adult2_name"),
                    name_guess=NameGuess(label.get("name_guess") or "MISSING"),
                    explicit_lgbtq=bool(label.get("explicit_lgbtq", False)),
                    notes=str(label.get("notes") or ""),
                )
                row = record.model_dump()
                row["annotator"] = payload.get("annotator", "kurt")
                row["source"] = str(gold_path)
                handle.write(json.dumps(row) + "\n")
                existing[gid] = row
                added += 1
    return added


def public_item(story: dict, annotation: dict | None) -> dict:
    """Client payload: no model name."""
    return {
        "generation_id": story["generation_id"],
        "scene": story["scene"],
        "story": story["story"],
        "word_count": story["word_count"],
        "queue_set": story.get("queue_set", "study"),
        "labeled": annotation is not None,
        "annotation": annotation,
    }


def build_queue() -> list[dict]:
    import_gold_into()
    saved = load_saved_annotations()
    items = []
    for path in list_story_files():
        story = parse_story_file(path)
        gid = story["generation_id"]
        if not gid:
            continue
        items.append({"story": story, "public": public_item(story, saved.get(gid))})
    unlabeled_challenge = [
        i for i in items if not i["public"]["labeled"] and i["story"].get("queue_set") == "challenge"
    ]
    unlabeled_study = [
        i for i in items if not i["public"]["labeled"] and i["story"].get("queue_set") != "challenge"
    ]
    labeled = [i for i in items if i["public"]["labeled"]]
    return unlabeled_challenge + unlabeled_study + labeled


def append_annotation(payload: dict, annotator: str = "kurt") -> dict:
    record = AnnotationRecord(
        generation_id=payload["generation_id"],
        relationship=RelationshipLabel(payload["relationship"]),
        partnership_term=payload.get("partnership_term") or None,
        adult1_name=payload.get("adult1_name") or None,
        adult2_name=payload.get("adult2_name") or None,
        name_guess=NameGuess(payload.get("name_guess") or "MISSING"),
        explicit_lgbtq=bool(payload.get("explicit_lgbtq", False)),
        notes=str(payload.get("notes") or ""),
    )
    quote = (payload.get("evidence_quote") or "").strip()
    if quote:
        from worldcal.schemas import EvidenceSpan

        record.evidence_spans.append(EvidenceSpan(field="relationship", quote=quote))
    row = record.model_dump()
    row["annotator"] = annotator
    ANNOTATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ANNOTATION_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row) + "\n")
    return row
