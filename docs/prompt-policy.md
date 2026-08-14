# Prompt and generation publication policy

WorldCal’s first measurement is only informative if models have not been trained or evaluated on the frozen confirmatory prompts.

Until confirmatory data collection is complete:

- **Do not** commit draft or frozen prompt *text* to git.
- **Do not** commit raw model generations to git.
- Store drafts in `prompts/private/` (gitignored) and generations under `data/` (gitignored).
- At preregistration, publish **cryptographic hashes** of the frozen prompt files, not the files.
- Immediately after confirmatory collection, publish the prompts, permitted generations, and run manifests.

Illustrative wording in `docs/research-spec.md` is **DRAFT** and is not the frozen benchmark.
