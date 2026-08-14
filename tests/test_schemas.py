from worldcal.schemas import (
    GenerationRecord,
    NameGuess,
    PromptRecord,
    RelationshipLabel,
    SamplingConfig,
    sha256_text,
)


def test_prompt_hash_is_stable() -> None:
    prompt = PromptRecord(id="p1", scenario="family", text="hello world")
    assert prompt.sha256 == sha256_text("hello world")
    again = PromptRecord(id="p1", scenario="family", text="hello world")
    assert prompt.sha256 == again.sha256


def test_sampling_for_generation_does_not_mutate_run_config() -> None:
    run = SamplingConfig(temperature=0.7, top_p=0.9, max_tokens=800, seed=None)
    one = run.for_generation(seed=None)
    two = run.for_generation(seed=123)
    assert run.seed is None
    assert one.seed is None
    assert two.seed == 123
    assert one.temperature == two.temperature == 0.7


def test_successful_generation_hashes_response() -> None:
    sampling = SamplingConfig()
    rec = GenerationRecord(
        id="g1",
        run_id="r1",
        model_id="nova-micro",
        prompt_id="p1",
        prompt_hash="abc",
        raw_text="A short story.",
        sampling=sampling,
    )
    assert rec.succeeded
    assert rec.response_hash == sha256_text("A short story.")
    assert rec.error is None


def test_annotation_name_guess_is_not_relationship_label() -> None:
    assert NameGuess.NAME_AMBIGUOUS.value == "NAME_AMBIGUOUS"
    assert RelationshipLabel.INDETERMINATE.value == "INDETERMINATE"
    assert set(NameGuess) != set(RelationshipLabel)
