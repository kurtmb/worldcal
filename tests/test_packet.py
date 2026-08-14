from pathlib import Path

from worldcal.packet import a09_jobs, load_a09_prompts


def test_a09_is_eight_independent_draws() -> None:
    jobs = a09_jobs()
    assert len(jobs) == 8
    seeds = [sampling.seed for _, _, sampling in jobs]
    assert all(seed is None for seed in seeds)
    models = [model.id for model, _, _ in jobs]
    prompts = [prompt.id for _, prompt, _ in jobs]
    assert models.count("nova-micro") == 4
    assert models.count("haiku-4.5") == 4
    assert prompts.count("family_school_morning_v0") == 4
    assert prompts.count("couple_first_home_v0") == 4


def test_prompts_load_from_private_dir() -> None:
    prompts = load_a09_prompts()
    assert len(prompts) == 2
    assert all(p.text.strip() for p in prompts)
    assert prompts[0].sha256 != prompts[1].sha256
    private = Path(__file__).resolve().parents[1] / "prompts" / "private"
    assert (private / "family_school_morning_v0.txt").is_file()
