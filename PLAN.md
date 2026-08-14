# WorldCal — living project plan

**Project:** WorldCal  
**Study 1:** Implicit LGBTQ representation and demographic calibration in open-ended LLM generation (United States)  
**Public site:** https://worldcal.org (to be registered)  
**Public repo:** https://github.com/kurtmb/worldcal  
**AWS account:** `689640939726` (IAM user `sfkurt27`)  
**Default region:** `us-west-2`  
**Inference path (first build):** Amazon Bedrock in `us-west-2`  
**Language:** Python 3.11+  
**Plan version:** 0.4 • 2026-08-14  
**Current step:** A.9 — eight stories ready; waiting on Kurt review  
**How Kurt is pulled in:** prompts (A.8), then a tiny story packet (A.9). Not 100 stories before the first read.

Scientific source of truth: `docs/research-spec.md`.  
How to read prompts and stories: `docs/review-guide.md`.

---

## Mandatory loop — every numbered step

Do not skip this. Do not batch three steps into one “while we’re here.”

1. **Investigate** the current codebase and infrastructure. Note what already exists (files, AWS resources, schemas, prompts). If the step is already done, mark it and stop.
2. **Write a temp plan** at `docs/steps/_temp/<step-id>.md` with: goal, files to touch, commands, acceptance checks, and what *not* to do. Temp plans are gitignored.
3. **Execute** only that temp plan.
4. **Test** if possible (pytest, a mocked generate, a single live Bedrock call, `curl`, an `aws` lookup). Record pass/fail in the temp doc.
5. **Clean up:** delete the temp plan (or empty `_temp/`), update this file’s status table, commit if the repo changed, then start the next step at (1).

**Hard stops for Kurt** (do not generate past these):

- After **A.8**: draft prompts exist → **Hey Kurt, you need to evaluate this** (prompts). No generation until he says the wording is okay to try.
- After **A.9**: about **8 stories**, not 80 → **Hey Kurt, you need to evaluate this** (stories). No 1,000-gen run until that packet is discussed.

Site/domain/OIDC is real work but **not** on the critical path to first stories. It waits until after the first prompt+story review unless we are blocked on Python.

---

## What is being measured (Study 1)

You are not scoring writing quality as the main outcome. You are checking whether a *sexuality-neutral* story even gives us evidence about a relationship, and what kind.

| Field | Question | Primary for the paper? |
| --- | --- | --- |
| Eligible relationship | Are there two parents / a couple as prompted? | Yes (inclusion) |
| Who the adults are | Gender/sex of each adult from **explicit text** (pronouns, mom/dad, husband/wife, “the two mothers”) | Yes |
| Partnership status | How the bond is named: married, husband/wife, boyfriend/girlfriend, partner, unnamed | Yes (explicitness) |
| Relationship composition | `SAME_SEX` / `DIFFERENT_SEX` / `INDETERMINATE` from explicit evidence only | **Yes — Endpoint A** |
| Names | Store the two adults’ given names. Optionally *guess* gender from names as a **sensitivity** check | **No** — never the official label |
| Explicit LGBTQ mention | Words like gay, lesbian, bisexual, transgender, “her wife,” “two dads” | Endpoint B (descriptive unless a matched baseline exists) |

Names can *suggest* a gay or heterosexual couple (Michael + David vs Sarah + Mike). Alex + Jordan suggests nothing. That guess is allowed as a side column so we can see whether name-inference would change conclusions. It is not ground truth. Ambiguous names stay ambiguous; we do not force a binary.

Full reading instructions: `docs/review-guide.md`.

---

## What you can evaluate, and when

| When | What exists | What you judge | What you cannot judge |
| --- | --- | --- | --- |
| **A.8 prompt review** | Two DRAFT prompts | Do they create a scorable couple/parents without leaking the study or requesting diversity? | Model behavior |
| **A.9 tiny packet (~8 stories)** | 2 prompts × 2 models × 2 samples | Scorability, evidence type (pronouns vs names vs nothing), whether Nova Micro is too thin | Census calibration, rankings |
| **B ~1,000** | Volume on the cheap model | Rates, cost, duplicates | Trusted labels |
| **C labels** | Humans + judge | Whether SAME_SEX detection is real | Confirmatory result |
| **D freeze** | Locked protocol | Design | Findings |
| **E confirmatory** | ~10 models | Calibration vs matched U.S. baselines | Causal “why” |

---

## First models

Bedrock `us-west-2`. This account can already invoke.

| Role | ID | A.9 tiny packet |
| --- | --- | --- |
| Primary | `us.amazon.nova-micro-v1:0` | 2 prompts × 2 stories |
| Other lab | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | 2 prompts × 2 stories |
| Open sniff | Qwen / DeepSeek | **Not in A.9.** Add after Kurt reads the first 8. |

If Nova Micro is too thin to score, switch volume to `us.amazon.nova-2-lite-v1:0` after the A.9 read.

**If the first packet is all `INDETERMINATE`** on who the adults are (no pronouns, no mom/dad, no husband/wife — every story unscorable for Endpoint A), do **not** immediately rewrite the prompts and do **not** jump to 1,000 generations. Run a tiny follow-up on a larger model (Nova 2 Lite, and if still empty, one Sonnet-class call) with the **same** prompts. That tells us whether the instrument failed or Nova Micro just will not gender anyone.

---

## Sampling and independence (do not stray from spec §9)

The scientific unit is **one independent draw** from the model’s generative distribution under a frozen prompt and frozen sampling config (temperature, top_p, max tokens, etc.). We need *different* stories from the same prompt, not a replay of one story.

**Parallel vs sequential does not change that estimand.** Bedrock’s next-token randomness lives on the provider side, per API request. Running eight HTTP calls at once does not share one “run seed” unless *we* send the same seed on every request.

| Design | Independent stories? | Matches spec §9? |
| --- | --- | --- |
| Sequential calls, no seed (or unique seed per generation), same temperature/top_p | Yes | Yes |
| Concurrent calls, each a separate `generate()`, no shared seed | Yes | Yes — this is only faster I/O |
| One seed (e.g. `42`) reused on every call, parallel or sequential | **No** — copies / near-copies | **No** |
| Retry a successful story because we did not like it | **No** | **No** |

**Frozen infrastructure rules**

1. `generate()` is one request → one generation. Parallelism, if used, is only a pool of those independent requests.
2. Do **not** set a run-level seed that is reused. That would destroy independence.
3. If Bedrock exposes `seed` for that model: either omit it (provider stochasticity) **or** assign a **unique** seed per `generation_id` and log it. Never reuse a seed inside a condition when we want another independent draw.
4. Always log: temperature, top_p, max tokens, seed (or `null` if omitted), request id. Spec §9.
5. Do not test randomness by asking the model for a random number. Measure duplicate/near-duplicate rates on actual stories.
6. Retries only for transport/provider failure. Never regenerate a successful response.
7. **A.9 (~8 stories): sequential.** Easier to watch, nothing to gain from parallel. Optional bounded concurrency is allowed from B onward, under rules 1–6.

Reproducibility in this project means: same config, same code commit, traceable metadata, repeated *samples* from the same distribution. It does not mean bit-identical stories on replay (the spec says serving can be nondeterministic even with seeds).

---

## Shared decisions

| Topic | Decision |
| --- | --- |
| Public name | WorldCal. LGBTQ is Study 1. |
| GitHub | Public `kurtmb/worldcal`. |
| Prompts | Text stays out of git until after confirmatory collection. Kurt reviews drafts in chat / `prompts/private/`. |
| License | Apache-2.0. |
| Code | Python package under `src/worldcal`. |
| First pause | Prompts, then ~8 stories. Not 80–100 before a human read. |
| Site | S3 + CloudFront + `worldcal.org`, **after** A.9 unless Python is blocked. |
| AWS non-inference budget | $20/month tagged `Project=WorldCal` (exists). |
| Names | Stored; sensitivity only; not primary gender. |

---

## Milestone A — First readable stories

**Goal:** Python generator on Bedrock, two draft prompts Kurt has approved, ~8 stories to read.  
**Not in the first pass:** 1,000-gen pilot, judge, leaderboard, domain (can follow).

| Step | Name | Status |
| --- | --- | --- |
| A.1 | Investigate accounts / collisions | done |
| A.2 | Create public `kurtmb/worldcal` | done |
| A.3 | Bootstrap skeleton, license, this plan, prompt policy | done |
| A.4 | Convert research spec to `docs/research-spec.md` | done |
| A.5 | AWS tags + $20/month non-inference budget | done |
| A.6 | Python package: schemas + append-only storage | done |
| A.7 | Bedrock `generate()` (independent draws; sequential first) | done |
| A.8 | Two DRAFT prompts → **Kurt prompt review (stop)** | done (approved) |
| A.9 | Tiny packet (~8 stories) → **Kurt story review (stop)** | waiting on Kurt |
| A.10 | Site / domain / OIDC (after first reads) | pending |

### A.6 Python package: schemas + append-only storage

1. Investigate `src/`, `pyproject.toml`, existing schemas.
2. Temp plan: `docs/steps/_temp/A.06.md`
3. Execute: `pyproject.toml`, `src/worldcal` pydantic models (run, prompt, model, generation, annotation fields including names + evidence tiers), SQLite+JSONL storage that never overwrites a successful generation.
4. Test: pytest for validation, append-only, hashes.
5. Clean up; mark this row done.

### A.7 Bedrock `generate()` (independent draws; sequential first)

1. Investigate schemas, boto3/Bedrock, and the sampling policy above.
2. Temp plan: `docs/steps/_temp/A.07.md`
3. Execute: single `generate()` = one independent API call. Log sampling params and seed-or-null. Sequential runner for A.9. Optional later: concurrent pool of the *same* `generate()`, unique seed per id if a seed is used, no shared seed.
4. Test: two mocked sequential calls with the same prompt must not be forced to identical seed; optional one live Nova Micro call.
5. Clean up; mark done. **Do not** run a story batch.

### A.8 Two DRAFT prompts → Kurt review

1. Investigate spec §6 and `prompts/private/`.
2. Temp plan: `docs/steps/_temp/A.08.md`
3. Execute: write two private drafts (two-parent school morning; couple moving in). US/national only. No diversity/sexuality/fairness cues. No gender specified for the adults.
4. Test: none beyond “these files exist and are gitignored.”
5. Clean up, then **stop.** Message: **Hey Kurt, you need to evaluate this** — prompts. Use `docs/review-guide.md` §Prompts.

### A.9 Tiny packet (~8 stories) → Kurt review

1. Investigate that A.8 was approved.
2. Temp plan: `docs/steps/_temp/A.09.md`
3. Execute: 2 prompts × Nova Micro × 2 + 2 prompts × Haiku 4.5 × 2, **sequentially**. Write `data/packets/a09/` (gitignored) with text + index (model, prompt, word count, names spotted, whether a couple is present, seed or null).
4. Test: eight files on disk, metadata complete, no silent retries.
5. Clean up, then **stop.** Message: **Hey Kurt, you need to evaluate this** — stories. Use `docs/review-guide.md` §Stories.

Do **not** add Qwen/DeepSeek or scale to 40–100 until this packet is discussed.

### A.10 Site / domain / OIDC

Same five-part loop. Parked until after A.9 unless we need a public URL sooner.

**Milestone A acceptance:**

- [x] Public repo, Apache-2.0, prompts not in git
- [x] Python `generate()` with tests; independent draws; sequential for the first packet
- [ ] Kurt has approved two DRAFT prompts
- [ ] Kurt has read ~8 stories
- [ ] Site URL (can lag)

---

## Milestone B — Pilot volume (~1,000)

Only after A.9 review. Still inspect at 250 before continuing to 1,000.

| Step | Name | Status |
| --- | --- | --- |
| B.1 | Length/sampling sensitivity subset | pending |
| B.2 | 250 generations; **Kurt glance** before continuing | pending |
| B.3 | Continue to ~1,000 on the primary model | pending |
| B.4 | Diagnostics: eligibility, indeterminate, duplicates, tokens, $ | pending |
| B.5 | Prompt revision only if scorability is poor | pending |

Each step uses the mandatory loop. B.2 is another **Hey Kurt, you need to evaluate this** if anything looks off in the first 250.

---

## Milestone C — Labels you can trust

| Step | Name | Status |
| --- | --- | --- |
| C.1 | Blind annotation export/UI | pending |
| C.2 | Label ≥200; double-label ≥100 | pending |
| C.3 | Freeze annotation guide | pending |
| C.4 | Deterministic rules + evidence spans | pending |
| C.5 | Structured LLM judge | pending |
| C.6 | Judge vs human, especially SAME_SEX | pending |
| C.7 | Missingness/bounds for INDETERMINATE + name-sensitivity | pending |

---

## Milestone D — Freeze and preregister

| Step | Name | Status |
| --- | --- | --- |
| D.1 | Power/precision simulation | pending |
| D.2 | Confirm inference budget | pending |
| D.3 | Freeze prompts, judge, sampling, exclusions | pending |
| D.4 | Hash frozen prompts; keep text private | pending |
| D.5 | Preregister | pending |
| D.6 | Tag a release candidate | pending |

---

## Milestone E — Confirmatory results

| Step | Name | Status |
| --- | --- | --- |
| E.1 | Remaining adapters; 20–50 call conformance each | pending |
| E.2 | Confirmatory generation with spend alarms | pending |
| E.3 | Frozen automated annotation | pending |
| E.4 | Stratified human validation (~1,000–1,500) | pending |
| E.5 | Frozen analysis + robustness (including names vs explicit text) | pending |
| E.6 | Paper/report | pending |
| E.7 | Public release of permitted artifacts | pending |
| E.8 | Leaderboard on worldcal.org | pending |

---

## What we will not do

- Put draft/frozen prompt text on GitHub
- Generate 80–1,000 stories before Kurt has seen prompts and a tiny packet
- Mix parenting baselines with couple-household baselines
- Use names as primary gender evidence
- Treat identity-mention rate as a population prevalence
- Rank models on the first packet
- Silently retry successful generations
- Reuse one seed across generations (that would make “parallel” or sequential runs produce copies, not samples)

---

## Change log

| Date | Change |
| --- | --- |
| 2026-08-14 | v0.1 — infra-first phases. |
| 2026-08-14 | v0.2 — five milestones; first pause after Bedrock stories. |
| 2026-08-14 | v0.3 — mandatory 5-part loop on every step; Python first; Kurt prompt review then ~8 stories; names as sensitivity; site deferred. |
| 2026-08-14 | v0.4 — freeze sampling/independence: no shared seed; sequential for A.9; parallel later is only concurrent independent API calls. |
