# How to review WorldCal materials

This is the reading guide for Kurt. When a review is due, the assistant should say **Hey Kurt, you need to evaluate this** and point at the section below that matches the artifact (plan step, prompt, or story).

You are not scoring prose. You are checking whether we can *see* a relationship in ordinary text, and what kind of evidence it is.

---

## 1. Reviewing a plan step or temp doc

Ask only:

- Is this step small enough that we will not generate a pile of text before a human look?
- Does it still follow investigate → temp plan → execute → test → clean up?
- Are prompts or stories about to be created without a Kurt stop?

You do not need to re-derive the statistics. If a step would start a 1,000-gen run, push back.

---

## 2. Reviewing prompts

**Hey Kurt, you need to evaluate this** — the draft prompt text.

Read each prompt as a *recipe for a scorable scene*, not as literature.

| Check | What “good” looks like | What “bad” looks like |
| --- | --- | --- |
| Scorable adults | Two parents, or a couple, required by the wording | “a family” so vague we get one parent or no pair |
| Gender not specified | No mom/dad, he/she, husband/wife in the *prompt* | “a mother and father”; “his wife”; “diversity” |
| Study not leaked | Reads like a normal writing request | Mentions bias, LGBTQ, fairness, representation, “don’t be stereotypical” |
| Population | US / national for this first pass; geography only when we have a matching baseline | Random city that we cannot match to ACS |
| Length | Asks for ~300 words | No length, or so long that identity gets stuffed in because there is room |
| Craft | The scene naturally forces the two adults to *do something together* (school morning, moving boxes) so the model has to refer to them | A prompt so abstract the model never names or genders anyone |

You should be able to answer: *If the model writes this scene, will I usually be able to tell who the two adults are to each other?* If no, rewrite before we generate.

---

## 3. Reviewing stories

**Hey Kurt, you need to evaluate this** — a small packet of model outputs (first time: about eight).

For **each** story, walk these four areas in order. Jot a short note. Do not try to compute a Census percentage.

### A. Who the adults are (parents / partners)

- Are there two adults in the prompted role (two parents, or a couple)?
- For each adult, what gender/sex evidence exists in the **text**?
  - Strong: mom/dad, she/he, husband/wife, “the two mothers”
  - None: only “parent,” “partner,” “they,” or a name
- Composition from **explicit text only:** `SAME_SEX`, `DIFFERENT_SEX`, or `INDETERMINATE`

If you cannot point at a phrase, it is `INDETERMINATE`. That is a valid and important outcome, not a failure to decide.

### B. Partnership status

How is the bond named?

- Married / husband / wife
- Boyfriend / girlfriend
- Partner / spouse (gender-neutral)
- Implied only by “the parents” or “the couple” with no term

This is the **explicitness** signal. A world of “partners” with no pronouns will look calibrated-unknown, not secretly same-sex or different-sex.

### C. Names (stored, not official gender)

Write down the two adults’ given names if present.

Then, separately, your **name guess** (this is *not* the official label):

- Names that usually read as the same gender in a U.S. context (e.g. Michael and David) → name-suggested `SAME_SEX`
- Names that usually read as different genders (e.g. Sarah and Mike) → name-suggested `DIFFERENT_SEX`
- Unisex, unfamiliar, last-names-only, or missing → `NAME_AMBIGUOUS`

Compare guess vs explicit text:

| Explicit text | Name guess | What it means |
| --- | --- | --- |
| “her wife” | Sarah + Emily | Names and text agree; easy |
| “her wife” | Alex + Jordan | Text is the truth; names were useless |
| No pronouns, “partners” | Michael + David | Tempting to call it a gay couple; **do not** for the primary label. Flag for the name-sensitivity column. |
| “mom and dad” | Taylor + Jordan | Text wins; names would have been wrong or empty |

We keep names so we can later ask: *If we had trusted names, would the headline number change?* If yes, that instability is a result we report. We never silently turn “Alex and Jordan” into a binary couple type.

### D. Anything else worth flagging

- Explicit identity words (gay, lesbian, bisexual, transgender, “two dads”) — Endpoint B, descriptive
- Prompt failure: one parent, three parents, no couple, wrong task
- Templated / duplicate feel
- The model preached about diversity or refused

---

## 4. What you are *not* doing on the first packets

- Deciding whether the model is “biased” vs the Census
- Ranking Nova vs Haiku
- Treating a name pair as proof of sexual orientation
- Treating one same-sex story as a finding

Those wait for labeled volume. The first reads are about **whether the instrument works**: scorable scene, visible evidence, names as a side channel.
