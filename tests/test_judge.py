from worldcal.judge import annotation_from_payload, parse_judge_json
from worldcal.schemas import NameGuess, RelationshipLabel


def test_parse_judge_json_strips_fences() -> None:
    payload = parse_judge_json(
        '```json\n{"relationship": "INDETERMINATE", "name_guess": "DIFFERENT_SEX", "explicit_lgbtq": false, "evidence_spans": []}\n```'
    )
    ann = annotation_from_payload("g1", payload)
    assert ann.relationship is RelationshipLabel.INDETERMINATE
    assert ann.name_guess is NameGuess.DIFFERENT_SEX
    assert ann.explicit_lgbtq is False


def test_indeterminate_is_first_class() -> None:
    ann = annotation_from_payload(
        "g1",
        {
            "relationship": "INDETERMINATE",
            "adult1_name": "Sarah",
            "adult2_name": "Tom",
            "name_guess": "DIFFERENT_SEX",
            "explicit_lgbtq": False,
            "evidence_spans": [],
            "notes": "names only",
        },
    )
    assert ann.relationship is RelationshipLabel.INDETERMINATE
    assert ann.name_guess is NameGuess.DIFFERENT_SEX
