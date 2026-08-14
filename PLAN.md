# WorldCal — living project plan

**Project:** WorldCal  
**Study 1:** Implicit LGBTQ representation and demographic calibration in open-ended LLM generation (United States)  
**Public site:** https://worldcal.org (to be registered)  
**Public repo:** https://github.com/kurtmb/worldcal  
**AWS account:** `689640939726` (IAM user `sfkurt27`)  
**Default region:** `us-west-2`  
**Inference path (first build):** Amazon Bedrock in `us-west-2` — no separate OpenAI/Anthropic keys required  
**Plan version:** 0.2 • 2026-08-14  
**Current milestone:** A — First readable stories  
**When to talk to Kurt:** at the end of a milestone, or if a purchase / permission / scientific fork blocks progress. Do not pause after each small infra step.

This file is the operational tracker. `docs/research-spec.md` is the scientific source of truth.

---

## What you can actually evaluate, and when

| When | What exists | What you can judge | What you cannot judge yet |
| --- | --- | --- | --- |
| **End of Milestone A** (first pause) | Repo, site, Bedrock adapter, draft prompts, **~50–100 real stories** from 2–3 models | Is the prompt scorable? Do stories look like ordinary family/couple scenes? Can a human see gender/relationship evidence? Did the prompt accidentally leak the study? | Census calibration, model ranking, “is this under-representation?” |
| **End of Milestone B** | ~1,000 generations on the primary cheap model + small comparison sets | Event rates, indeterminate rate, duplicates, cost per story, whether 5,000/model is necessary | Trusted labels, scientific claims |
| **End of Milestone C** | Human labels + automated judge metrics | Whether SAME_SEX can be detected without swamping false positives | Confirmatory multi-model results |
| **End of Milestone D** | Frozen protocol, prompt hashes, preregistration | The study design is locked | Results |
| **End of Milestone E** | ~10 models, frozen analysis, public data, leaderboard | Calibration vs matched U.S. baselines, model differences, geographic responsiveness | Causal “why” (training data, RLHF, regulation) |

**Bottom line:** you should be reading model output at the **first** pause, not the third. The *finding* (rates vs Census) is Milestone E. That gap is labeling, volume, and freeze discipline — not more AWS accounts.

---

## First models (spec’d)

All first generation goes through **Bedrock `us-west-2`**. This account can already `Converse` / `InvokeModel`. There are no OpenAI/Anthropic API keys in the environment; we are not waiting on them.

### Milestone A — stories you will read

| Role | Bedrock ID | Why |
| --- | --- | --- |
| Primary (volume) | `amazon.nova-micro-v1:0` (profile `us.amazon.nova-micro-v1:0`) | Cheapest text model on the account. Used for the 50-story packet and, if quality is acceptable, the 1,000-gen pilot. |
| Quality / other-lab check | `anthropic.claude-haiku-4-5-20251001-v1:0` (profile `us.anthropic.claude-haiku-4-5-20251001-v1:0`) | Different provider, still cheap. Lets you compare whether “ordinary story” quality and relationship explicitness differ. |
| Open-model sniff test | `qwen.qwen3-32b-v1:0` and `deepseek.v3-v1:0` | Spec called out Qwen / DeepSeek / Kimi. **10–20 stories each**, not 1,000. Enough to read, not enough to rank. |

If Nova Micro stories are too thin to score (no eligible couple, too short, too templated), the primary volume model becomes **`amazon.nova-2-lite-v1:0`** after you look at the packet. That is a quality call from reading, not a new research design.

Do **not** spend the first packet on Opus, Sonnet, or GPT-5.6 frontier IDs. Those wait for the confirmatory roster.

### Later confirmatory roster (not started now)

Target ~10 models across capability tiers, frozen by exact snapshot immediately before preregistration, for example:

- Amazon: Nova Micro or Nova 2 Lite, plus one larger Nova
- Anthropic: Haiku 4.5, plus one Sonnet
- OpenAI on Bedrock: one GPT-5.6 tier (cheap or mid, not the most expensive by default)
- Qwen, DeepSeek, Kimi (as terms and price allow)

Final list is a Milestone D decision after we know cost per story.

---

## Shared decisions

| Topic | Decision |
| --- | --- |
| Public name | **WorldCal**. LGBTQ is Study 1. |
| GitHub | Public `kurtmb/worldcal`. Solo. |
| Prompts | Draft and frozen prompt **text** stay out of git until after confirmatory collection. Hashes at preregistration; literal prompts after collection. |
| License | Apache-2.0 for code. |
| Website v0 | Project home + study explanation + this plan. No leaderboard yet. |
| Hosting | S3 + CloudFront + Route 53. If domain contact/purchase lags, ship on the CloudFront URL first. |
| Domain | Buy `worldcal.org` when we hit that step. Account already has a Route 53-usable registrant contact. |
| AWS spend guard | $20/month budget alarm for **non-inference** (`Project=WorldCal`). |
| Inference spend | Bedrock, tagged separately. Pilot packet should be a few dollars. Hard stop before anything that looks like a $1,000 confirmatory run. |
| Pause rule | End of milestone, or a real blocker. Not after every IAM/S3 click. |

---

## How each step is done

For each numbered step: investigate → temp plan in `docs/steps/` → execute → test → clean up and mark this file. Keep going inside the milestone unless blocked.

---

## Milestone A — First readable stories

**Goal:** Public repo, basic AWS project plumbing, a site (domain or CloudFront URL), a working Bedrock generator, draft prompts on disk (private), and a **private packet of real stories** for Kurt to read.  
**Pause:** after A.12, when the packet exists.  
**Not in this milestone:** 1,000-gen pilot, human annotation, judge, preregistration, leaderboard.

| Step | Name | Status |
| --- | --- | --- |
| A.1 | Investigate accounts / collisions | pending |
| A.2 | Create public `kurtmb/worldcal` | pending |
| A.3 | Bootstrap skeleton, license, this plan, prompt policy | pending |
| A.4 | Convert research spec to `docs/research-spec.md` | pending |
| A.5 | AWS tags + $20/month non-inference budget | pending |
| A.6 | GitHub → AWS OIDC deploy role | pending |
| A.7 | Register `worldcal.org` + ACM + S3 + CloudFront + DNS (or CloudFront-only if purchase is delayed) | pending |
| A.8 | Website v0 + CI deploy | pending |
| A.9 | Typed schemas + local append-only storage | pending |
| A.10 | Bedrock `generate()` adapter for the four first-model IDs | pending |
| A.11 | Two private DRAFT prompts (two-parent family; couple) + national baseline stub | pending |
| A.12 | Generate and export the first reading packet | pending |

### A.12 reading packet (the first result you will see)

Private, not in public git:

- ~40 generations: Nova Micro × 2 prompts × ~20
- ~20 generations: Haiku 4.5 × 2 prompts × ~10
- ~10 Qwen + ~10 DeepSeek

Export as a local folder of `.txt`/`.jsonl` plus a one-page index (model, prompt id, word count, whether a couple is even present). You read those. We do not compute Census calibration on this packet.

**Milestone A acceptance:**

- [ ] Public repo exists, Apache-2.0, prompts not in git
- [ ] Site is reachable (worldcal.org or CloudFront)
- [ ] A generation is reproducible from config (model, prompt hash, sampling, commit)
- [ ] You have a packet of real stories from Nova Micro and Haiku, plus a small open-model sample

---

## Milestone B — Pilot volume (~1,000)

**Goal:** Gate 1 on the primary cheap model. Learn scorability, duplicates, cost, length sensitivity.  
**Pause:** after B.5.

| Step | Name | Status |
| --- | --- | --- |
| B.1 | Length/sampling sensitivity subset | pending |
| B.2 | 250 generations; inspect before continuing | pending |
| B.3 | Continue to ~1,000 on the primary model | pending |
| B.4 | Diagnostics: eligibility, indeterminate, duplicates, tokens, $ | pending |
| B.5 | Prompt revision only if scorability is poor | pending |

---

## Milestone C — Labels you can trust

**Goal:** Annotation guide + human labels + judge validation. Stop the study if rare-class precision/recall is bad.  
**Pause:** after C.7.

| Step | Name | Status |
| --- | --- | --- |
| C.1 | Blind annotation export/UI | pending |
| C.2 | Label ≥200; double-label ≥100 | pending |
| C.3 | Freeze annotation guide | pending |
| C.4 | Deterministic rules + evidence spans | pending |
| C.5 | Structured LLM judge (not the model under test, if possible) | pending |
| C.6 | Judge vs human, especially SAME_SEX | pending |
| C.7 | Missingness/bounds plan for INDETERMINATE | pending |

---

## Milestone D — Freeze and preregister

**Goal:** Lock N, prompts, judge, roster rules. Publish hashes, not prompt text.  
**Pause:** after D.6. No full model suite before this.

| Step | Name | Status |
| --- | --- | --- |
| D.1 | Power/precision simulation from pilot rates | pending |
| D.2 | Confirm inference budget vs projected spend | pending |
| D.3 | Freeze prompts, judge, sampling, exclusions | pending |
| D.4 | Hash frozen prompts; keep text private | pending |
| D.5 | Preregister (effect sizes / calibration, not trivial existence tests) | pending |
| D.6 | Tag a release candidate | pending |

---

## Milestone E — Confirmatory results

**Goal:** Frozen multi-model run, analysis, paper, public data, leaderboard with uncertainty and denominators.  
**Pause:** after E.8.

| Step | Name | Status |
| --- | --- | --- |
| E.1 | Remaining adapters; 20–50 call conformance each | pending |
| E.2 | Confirmatory generation with spend alarms | pending |
| E.3 | Frozen automated annotation | pending |
| E.4 | Stratified human validation (~1,000–1,500) | pending |
| E.5 | Frozen analysis + robustness | pending |
| E.6 | Paper/report | pending |
| E.7 | Public release of permitted artifacts | pending |
| E.8 | Leaderboard on worldcal.org | pending |

---

## Work left after A vs after A+B

After **Milestone A** you have plumbing **and** stories. Still left: the actual pilot volume, labeling, judge, freeze, ~10-model confirmatory run, paper, leaderboard. That is most of the scientific work.

After **A + B** you still have not labeled, have not proven the judge, and have not measured calibration. You *have* decided whether the prompt and cheap model are worth scaling.

Phases 0–1 in plan v0.1 were only A.1–A.10 without A.11–A.12. That was too small a first pause. v0.2 does not stop until there is output to read.

---

## What we will not do

- Put draft/frozen prompt text on GitHub
- Mix parenting baselines with couple-household baselines
- Use names as primary gender evidence
- Treat identity-mention rate as a population prevalence
- Rank models on this first packet
- Infer *why* a model differs from rates alone
- Start Opus/Sonnet/GPT-5.6 volume runs in Milestone A

---

## Change log

| Date | Change |
| --- | --- |
| 2026-08-14 | v0.1 — infra-first phases; pause after each phase. |
| 2026-08-14 | v0.2 — five milestones; first pause after readable Bedrock stories; first-model IDs specified. |
