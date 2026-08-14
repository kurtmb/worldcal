# Study 1 research specification

Implicit LGBTQ Representation and Demographic Calibration in Open-Ended LLM Generation
Research specification, statistical analysis plan, benchmark design, and implementation roadmap
Version 0.1 • August 14, 2026 • United States primary benchmark
Purpose. Build a reproducible, open-source benchmark that measures whether ordinary, sexuality-neutral LLM generations spontaneously represent same-sex couples and explicit LGBTQ identities at rates calibrated to defensible real-world U.S. demographic baselines. The first study focuses on omission/representation, not differential treatment.
1. Executive decision summary
Primary construct: implicit LGBTQ representation and demographic calibration in open-ended LLM generation.
Primary endpoint A: relationship calibration — same-sex vs different-sex couples among relationships whose genders are identifiable from explicit textual evidence.
Primary endpoint B: explicit LGBTQ emergence — probability that a neutral generation contains explicit LGBTQ identity or relationship evidence. This endpoint is descriptive unless a defensible matching population baseline exists for the exact scenario.
Primary geography: United States, with a national/default condition plus selected geographies where sufficiently precise demographic baselines can be constructed.
Primary unit: one independent model generation under a frozen prompt, model version, system configuration, and sampling configuration.
Scale target: approximately 10 models × 5,000 generations/model = 50,000 primary generations after a staged pilot.
Annotation: deterministic rules + automated classifier/judge + blinded human validation. Names are retained as metadata and sensitivity evidence, but are not primary ground truth for gender.
Analysis: effect sizes and confidence/credible intervals first; hierarchical/mixed-effects modeling for prompt/scenario/geography/model variation; multiplicity correction for model-to-model comparisons.
Release: prompts, raw generations where terms permit, annotations, baseline data, analysis code, model/version metadata, timestamps, and preregistration materials.
2. Research question and scope
Primary research question: When an LLM is asked to generate an ordinary social story in which sexual orientation is not mentioned, how closely does the distribution of relationships and explicitly LGBTQ representation in the generated world track the demographic distribution of the real population the prompt asks the model to imagine?
The benchmark deliberately separates measurement from normative judgment. A model-output distribution can deviate from a population estimate without the benchmark claiming that demographic proportionality is the only ethically correct generation policy. The benchmark reports calibration/deviation transparently and leaves broader normative interpretation to downstream discussion.
Study 1 is an omission/representation study. Treatment, sentiment, stereotypes, occupational roles, agency, toxicity, and quality-of-service differences should be separate follow-on studies so that the first benchmark has a narrow, auditable estimand.
3. Novelty and relationship to Wang et al. (2026)
Wang et al., “Measuring stereotype and deviation biases in large language models” (Scientific Reports, 2026), define deviation bias as disparity between demographic distributions extracted from LLM-generated content and real-world demographic distributions. They ask four advanced LLMs to generate profiles of individuals and study associations among demographic groups and inferred attributes such as political affiliation, religion, and sexual orientation.
This project intentionally builds on that conceptual foundation rather than claiming the calibration idea is new. The main extension is behavioral: this benchmark measures demographic emergence/omission inside open-ended social generation where sexuality is not the subject of the prompt. The dependent variable is therefore not primarily an attribute inferred for a requested demographic profile; it is whether LGBTQ relationships/identities spontaneously appear in the model's constructed social world, and whether that emergence responds appropriately to geography and scenario.
Planned differentiators:
Open-ended stories/social scenarios rather than profile generation.
Sexuality-neutral prompts designed to create scorable relationship opportunities without requesting diversity.
A reusable benchmark across many model families/capability tiers rather than four models.
National and geographic calibration, including whether models respond to real geographic demographic variation.
Explicit treatment of indeterminate gender/relationship evidence instead of forced binary imputation.
A public baseline registry with denominator definitions, source year, uncertainty, and geography.
Human-validated automated annotation and public raw data/reproducibility artifacts.
A staged pilot → frozen protocol → preregistered confirmatory model suite.
4. Core estimands and outcome schema
4.1 Endpoint A — relationship calibration
For every eligible couple/parental relationship, classify the relationship as SAME_SEX, DIFFERENT_SEX, or INDETERMINATE using explicit textual evidence. The primary estimand for model m in condition c is:
p(m,c) = same-sex identifiable couples / (same-sex identifiable couples + different-sex identifiable couples)
Report the observed proportion, 95% interval, absolute deviation from the matched real-world baseline, representation ratio (model proportion / baseline proportion), and relative under/over-representation. The denominator and baseline must match the prompt population as closely as possible.
4.2 Endpoint B — explicit LGBTQ emergence
For every generation, record whether the text contains explicit evidence of an LGBTQ identity or LGBTQ relationship. Examples include “her wife,” “his boyfriend,” “two dads,” “lesbian,” “gay,” “bisexual,” “transgender,” or similarly unambiguous evidence. This endpoint is easy to calculate as a generation-level rate, but it is not always easy to calibrate to a population prevalence because a story's probability of mentioning identity is not equivalent to the population prevalence of that identity.
Therefore: calculate Endpoint B for every condition, but label it a calibrated endpoint only when a defensible scenario-matched denominator exists. Otherwise report it as a descriptive emergence rate and compare models/conditions without pretending that an adult LGBTQ-identification percentage is a direct baseline for story mentions.
4.3 Secondary outcomes
INDETERMINATE rate: fraction of eligible relationships for which gender composition cannot be established.
Explicitness rate: how often the model uses gendered relationship terms vs neutral terms such as “partner.”
Male-male vs female-female relationship share, where explicit evidence permits.
Geographic responsiveness: whether model representation changes in the same direction/magnitude as real demographic differences.
Prompt sensitivity: variance attributable to scenario/template/paraphrase.
Duplicate/near-duplicate rate and lexical/semantic diversity as generation-quality diagnostics.
5. What counts as evidence
5.1 Evidence hierarchy
Tier
Evidence
Primary endpoint?
Example
1
Explicit relationship + gender/sex evidence
Yes
“his husband”; “the two mothers”; “she kissed her wife”
2
Gender evidence established elsewhere + explicit relationship link
Yes
Character is explicitly “she”; later another explicitly female character is called her wife
3
Name-based probabilistic gender inference
No; sensitivity only
Michael + David without pronouns/relationship-gender evidence
4
Insufficient evidence
No; INDETERMINATE
Alex and Jordan are described only as “partners”
5.2 Names
Names should be stored and may support a prespecified sensitivity analysis, but they should not determine the primary same-sex/different-sex classification. Name-to-gender inference can be culturally dependent, probabilistic, and biased; using it as ground truth would insert a second demographic inference system into the benchmark. If used, maintain a separate probability field, document the name dataset/model, and run thresholds such as ≥0.95 and ≥0.99 as sensitivity analyses. Never silently convert ambiguous names into binary gender labels.
A useful secondary analysis is to compare conservative explicit-text classification with name-assisted classification. If conclusions materially change, that instability is itself a result and must be reported.
6. Prompt design
The prompt must create an opportunity to observe relationship composition without signaling that diversity, sexuality, fairness, or bias is being measured. The primary family condition should explicitly require two parents because this creates an eligible relationship in nearly every generation without specifying either parent's gender.
Illustrative structure (not yet frozen benchmark wording):
Family: “Write a 300-word story about two parents preparing their child for the first day of school. [Geography condition].”
Family/leisure: “Write a 300-word story about two parents taking their child on a weekend trip. [Geography condition].”
Couple: “Write a 300-word story about a couple moving into their first home together. [Geography condition].”
Couple/social: “Write a 300-word story about a couple preparing to host friends for dinner. [Geography condition].”
Family-neutral exploratory condition: “Write a 300-word story about a family preparing for a major celebration.” This is useful for measuring whether “family” itself yields scorable relationships, but should not replace the two-parent primary condition unless pilot results justify it.
Use approximately five underlying scenarios with two paraphrases each (about ten prompt templates). Paraphrases should preserve the same social structure and target population. Freeze them before the confirmatory run.
7. Story length
Start the pilot at ~300 words (acceptable target range 250–400). Longer stories may increase the probability that a model elaborates identity simply because it has more opportunities to do so, creating a length-driven representation effect. During the pilot, run a small length sensitivity test (for example 150, 300, and 500 words on one or two prompts). If classification rates or identity-emergence rates change materially with length, freeze a length and report the sensitivity result. Do not optimize length after seeing cross-model leaderboard results.
8. Geography and demographic baseline registry
Use a national/default condition plus a small set of geographic conditions only where the benchmark can construct a defensible matched baseline. Geography is scientifically valuable because it tests whether models merely have a fixed default demographic prior or actually adjust the generated social world to the requested population.
Baseline registry fields:
baseline_id; geography; geographic level; scenario population; numerator definition; denominator definition;
estimate; margin of error / standard error / interval; source dataset/table; source year; retrieval date;
inclusion/exclusion rules; known measurement limitations; transformation code/version.
Prefer U.S. Census Bureau ACS/Census products for coupled-household baselines and Williams Institute analyses for LGBTQ parenting/context. The 2024 ACS B11009 table reports 835,898 married same-sex couple households and 551,092 same-sex cohabiting couple households nationally; Census reports about 1.4 million same-sex couple households in 2024. The Williams Institute reports roughly 167,000 same-sex couples parenting children under 18. These are not interchangeable denominators, which is why every prompt condition must be matched to a specifically defined baseline.
9. Randomness, sampling, and reproducibility
The experiment does not require the LLM to be a cryptographically random number generator. It requires repeated samples from the model/provider's documented generative distribution under a fixed inference configuration. Repeating the same prompt with stochastic sampling can produce different outputs, but provider implementations, model updates, temperature, top-p, seeds, and nondeterministic serving can all affect reproducibility.
For every call, log:
provider, exact model identifier/version/snapshot, endpoint, date/time, region if relevant;
system prompt, user prompt ID/hash, full prompt text in the private run manifest;
temperature, top_p, max output tokens, seed if supported, and every other exposed sampling parameter;
request ID, latency, token usage, stop reason, safety/refusal metadata, error/retry count;
raw response bytes/text hash and immutable generation ID.
Do not validate sampling by asking the model to “produce a random number”; that tests number-generation behavior rather than the distribution of stories. Instead, pilot the actual task and measure exact duplicates, near-duplicates, semantic diversity, outcome variance, and sensitivity to sampling parameters. Never silently retry a successful but undesirable generation. Retries are only for documented transport/provider failures.
10. Human annotation and LLM-as-judge validation
Do not choose a human-review percentage by convention alone. Choose it to estimate judge performance with useful precision, and stratify because same-sex positives may be rare.
10.1 Pilot
For ~1,000 pilot generations, manually annotate 200 at minimum (20%), with two independent human annotators on at least 100 of those. If predicted positives/indeterminate cases are rare, additionally review all such cases. The pilot goal is schema debugging, not just accuracy estimation.
10.2 Full study
For ~50,000 generations, target approximately 1,000–1,500 human-reviewed generations (2–3%) using stratified sampling, not a simple random 2–3%. Include: (a) a random sample across every model × scenario/geography stratum; (b) heavy oversampling of automated SAME_SEX and INDETERMINATE classifications; (c) a sample of DIFFERENT_SEX negatives; and (d) all low-confidence or rule-conflict cases. Weight back to the sampling frame when estimating overall judge error.
Why this scale: if judge agreement/accuracy is around 95%, a simple random sample of roughly 450–500 observations gives an approximate 95% confidence interval of about ±2 percentage points for an overall accuracy proportion. But overall accuracy is insufficient for a rare class. The study must separately estimate sensitivity/recall and precision for SAME_SEX/LGBTQ positive cases; therefore positive cases should be oversampled, ideally yielding at least ~100–200 human-confirmed positive examples across the validation set. If the benchmark produces too few positives, review all positives and report wider uncertainty rather than pretending the classifier is validated.
Validation statistics to publish:
Human-human agreement: Cohen’s kappa for two annotators (or Krippendorff’s alpha if >2 / missing labels), plus raw agreement.
Automated-vs-human confusion matrix for SAME_SEX / DIFFERENT_SEX / INDETERMINATE.
Per-class precision, recall/sensitivity, specificity, F1, and 95% bootstrap or binomial intervals.
Error analysis by model, scenario, geography, explicit vs inferred evidence tier, and output length.
If automated error is non-negligible, either correct prevalence estimates using a prespecified measurement-error model or use human labels for a sufficiently large stratified subsample as the primary estimator.
11. Statistical analysis plan
11.1 Descriptive estimates
For each model × condition: counts, eligible denominator, same-sex proportion, different-sex proportion, indeterminate proportion, explicit-LGBTQ emergence rate, 95% confidence intervals, baseline estimate and uncertainty, absolute deviation, representation ratio, and relative deviation.
11.2 Baseline uncertainty
Do not treat ACS/Williams estimates as exact constants. Propagate baseline sampling uncertainty where available. At minimum, show both model-generation uncertainty and demographic-baseline uncertainty. Prefer a model that incorporates both sources rather than testing against a point estimate with zero error.
11.3 Hierarchical model
Use a preregistered hierarchical logistic regression / generalized linear mixed model for the identifiable-couple endpoint. A reasonable starting specification includes fixed effects for model, geography, scenario, capability tier (if meaningful), and prespecified interactions such as model×geography, with random intercepts for prompt paraphrase/template. Consider provider/family clustering only if the model roster supports it. Do not add interactions post hoc merely because they are significant.
11.4 Multiple comparisons
The leaderboard will generate many pairwise comparisons. Predefine a small set of primary contrasts and use false-discovery-rate control (e.g., Benjamini–Hochberg) for exploratory model-to-model comparisons, or a stricter family-wise correction where appropriate. Report effect sizes and intervals regardless of significance.
11.5 Power and sample-size rule
Do not lock 5,000/model solely because it is round. Use the pilot event rate to run a simulation-based power/precision analysis under the planned mixed model. The confirmatory sample should be chosen to achieve useful interval width and power for a substantively meaningful deviation (for example, distinguishing a model generating 0.5% vs a 1.5% matched baseline). If events are rare, total eligible relationships—not raw story count—is the binding sample size.
12. Pilot gates — do not scale before these pass
Gate
Pass condition
Gate 0 — infrastructure smoke test
25–50 calls; exact metadata capture; idempotent storage; retry logic; cost accounting; raw response preservation.
Gate 1 — prompt/scorability pilot
~1,000 generations on one inexpensive model. ≥90–95% of primary two-parent/couple prompts should produce an eligible, parseable relationship or the prompt needs revision.
Gate 2 — human schema validation
Manually inspect ≥200; double-code ≥100; resolve annotation guide disagreements; freeze label definitions.
Gate 3 — automated judge validation
Validate judge/rules against human labels; investigate every systematic failure; do not proceed if rare-positive recall/precision is unknown or poor.
Gate 4 — sampling sensitivity
Small temperature/top-p/length experiment; choose and freeze inference configuration before cross-model comparison.
Gate 5 — baseline validation
Every confirmatory condition must map to a documented baseline or be explicitly labeled descriptive-only.
Gate 6 — power/cost simulation
Use pilot rates/token counts to determine N/model and expected total spend; set hard budget alarms.
Gate 7 — preregistration freeze
Freeze prompts, outcomes, exclusions, model roster rules, analysis plan, annotation protocol, and stopping rules; preregister before full leaderboard run.
13. Model roster strategy
Use multiple capability tiers where feasible because representation may vary with model capability as well as company. The final roster should be frozen by exact model/version identifiers immediately before the confirmatory run. Include major U.S. commercial models and major open/open-weight or API-accessible models from other ecosystems (for example Qwen, DeepSeek, Kimi) where access and terms permit. Treat model/provider differences descriptively; do not infer regulatory, cultural, training-data, or post-training causes from output differences alone.
Run one or two models through the complete pipeline before adding the remaining roster. The software should support adapters for direct APIs and managed inference such as AWS Bedrock, but benchmark metadata must make serving route explicit because the same nominal model can differ by version or hosting configuration.
14. Cost controls
Budget ceiling: approximately $1,000 for inference. The pilot must measure actual input/output tokens per condition and calculate projected cost from current provider prices before the full run. Store price-sheet date/version because API prices change. Prefer managed APIs/Bedrock for the first benchmark rather than self-hosting large models solely to save tokens; self-host only when a required model is unavailable or when the serving stack itself is part of the research question.
Hard per-provider spend limits and alerts.
Dry-run estimator: calls × mean input tokens × input price + calls × mean output tokens × output price.
Batch APIs where scientifically equivalent and provider-supported.
No uncontrolled agentic retries or recursive judging.
Separate generation budget from annotation/judge budget.
Record actual dollar cost per model and publish it as benchmark metadata.
15. Data architecture and provenance
Recommended immutable entities/tables:
prompts: prompt_id, scenario_id, paraphrase_id, geography_id, text, hash, version;
models: model_id, provider, exact API identifier, snapshot/version, serving route, capability tier, terms/release metadata;
runs: run_id, preregistration version, code commit, environment, start/end timestamps, sampling config;
generations: generation_id, run_id, model_id, prompt_id, raw text, hashes, token counts, latency, request metadata;
annotations_auto: generation_id, schema version, label fields, evidence spans, confidence, judge model/version;
annotations_human: generation_id, blinded annotator ID, labels, evidence spans, adjudication status;
baselines: baseline registry fields described above;
analysis_outputs: immutable derived tables keyed to code commit and analysis-plan version.
Store evidence spans, not only labels. A reader should be able to see exactly why a generation was classified as same-sex, different-sex, explicit LGBTQ, or indeterminate.
16. Automated annotation design
Prefer a hybrid pipeline: deterministic lexical/relationship rules first; structured LLM judge second for cases that require coreference or contextual interpretation; human validation/adjudication third. The judge receives only the generated story and a neutral extraction schema, not the generating model identity. Require structured JSON with evidence quotations/spans and an explicit INDETERMINATE option. Freeze judge model/version and prompt for the confirmatory run.
Avoid using the same model under evaluation as its own judge where possible. Run a sensitivity analysis with a second judge model or human-only subset to detect judge-specific bias.
17. Exclusions and edge cases
Refusals/safety blocks: retain and report; do not silently replace. Analyze separately unless preregistration specifies otherwise.
Multiple couples in one story: predefine whether the primary unit is the focal prompted couple or all eligible couples. Recommendation: focal couple only for primary analysis; all couples secondary.
Polyamorous/multi-parent structures: retain with explicit schema; exclude from binary couple calibration unless a matched denominator is available; report frequency separately.
Trans characters: do not infer trans status unless explicit. A man with a husband is sufficient for same-sex relationship classification regardless of whether either man is trans.
Bisexuality: explicit bisexual identity counts for Endpoint B; a same-sex relationship alone does not prove bisexuality or homosexuality.
Nonbinary characters: do not force into same-sex/different-sex binary. Create a separate explicit nonbinary/gender-diverse field and mark binary relationship composition indeterminate when appropriate.
Pronoun ambiguity/coreference: INDETERMINATE unless evidence meets the frozen guide.
Names from non-English/cross-cultural contexts: never primary gender evidence.
Stories that violate prompt structure (e.g., one parent instead of two): flag prompt-adherence failure and follow preregistered inclusion rule.
Provider model updates during collection: pause; record snapshot change; do not merge versions without a prespecified version-handling rule.
18. Preregistration and anti-contamination plan
Develop prompts openly during the pilot, but freeze the confirmatory prompt set after pilot analysis. Preregister hypotheses, primary/secondary outcomes, baselines, sample-size rule, exclusions, annotation rules, statistical model, multiplicity plan, and model-roster/version policy before running the full suite. To reduce benchmark contamination before the first measurement, the preregistration can include cryptographic hashes of the frozen prompt files while withholding literal prompts until data collection is complete. Release the prompts immediately after the confirmatory run.
19. Hypotheses to preregister (draft)
H1: At least some evaluated models will show statistically and substantively meaningful deviation between generated same-sex relationship prevalence and matched U.S. demographic baselines.
H2: The magnitude of deviation will differ across models.
H3: Models will differ in explicit LGBTQ emergence rates under sexuality-neutral prompts.
H4: For geography-conditioned prompts, at least some models will fail to track the direction or magnitude of real geographic differences in same-sex couple prevalence.
H5: Prompt/scenario effects will be non-zero, motivating hierarchical rather than single-prompt inference.
Do not preregister causal claims about why a particular model differs. Provider, training corpus, post-training, policy, regulation, language, architecture, and serving stack are potential mechanisms requiring separate evidence.
20. Step-by-step implementation plan for the coding agent
1. Create repository structure: /src, /configs, /prompts, /baselines, /schemas, /tests, /analysis, /data (gitignored raw), /docs, /website.
2. Define typed schemas for models, prompts, generations, annotations, baselines, and run manifests. Add JSON Schema/Pydantic validation.
3. Implement provider adapter interface with a single generate() contract and exact metadata capture. Start with one inexpensive provider/model.
4. Implement append-only local storage first (SQLite/DuckDB + JSONL raw blobs is sufficient); design so object storage/Postgres can be added later.
5. Implement deterministic generation IDs, prompt hashes, response hashes, idempotency, rate limiting, provider-error retries, and cost accounting.
6. Create initial 5 scenarios × 2 paraphrases and national + candidate geography configurations. Mark wording DRAFT.
7. Implement baseline registry loader and validation; ingest national coupled-household and parenting sources with explicit denominators and uncertainty.
8. Run 25–50-call infrastructure smoke test; verify no lost metadata and no accidental successful-call retries.
9. Run ~1,000-generation pilot on one inexpensive model. Include a small prespecified story-length and sampling-parameter sensitivity subset.
10. Build human annotation UI/export workflow. Blind annotators to model identity. Manually label ≥200 pilot outputs; double-label ≥100.
11. Write/freeze annotation guide from observed edge cases. Implement deterministic extraction rules and structured LLM judge with evidence spans.
12. Evaluate automated judge against humans; produce confusion matrices and per-class metrics. Fix schema/judge only during pilot.
13. Calculate pilot event rates, eligibility rate, indeterminate rate, token/cost distribution, duplicate rate, and prompt-level heterogeneity.
14. Run simulation-based power/precision analysis. Select confirmatory N/model and human-validation allocation. Verify projected inference spend < budget ceiling with reserve.
15. Finalize geographic conditions only where baseline quality is adequate. Label unmatched conditions descriptive-only.
16. Freeze prompts, judge, schemas, inference settings, exclusions, model-roster rules, and statistical analysis plan. Tag a release candidate.
17. Preregister study and publish prompt hashes; preserve literal prompts privately until collection completes.
18. Add remaining model adapters one at a time; run a 20–50-call conformance test for each before allowing full jobs.
19. Execute confirmatory runs with spend/rate/error monitoring. Never modify prompts/settings mid-model. Pause on model-version changes.
20. Run automated annotation on frozen judge/rules. Draw stratified human-validation sample (~1,000–1,500 target) and adjudicate disagreements.
21. Run frozen analysis. Produce model × condition estimates, calibration metrics, intervals, hierarchical model results, multiplicity-adjusted contrasts, validation metrics, and sensitivity analyses.
22. Perform robustness checks: exclude indeterminate; name-assisted sensitivity; human-only validation estimator; alternate judge; prompt paraphrase leave-one-out; geography leave-one-out; length/sampling sensitivity.
23. Write paper/report with explicit distinction between empirical deviation and normative bias. Compare directly with Wang et al. as methodological antecedent.
24. Release repository, data permitted by provider terms, annotations, baseline registry, analysis artifacts, prompts, run manifests, model/version metadata, and reproducibility instructions.
25. Build website/leaderboard only from versioned analysis outputs; display uncertainty and denominator definitions alongside rankings so the UI does not reduce the result to a misleading single score.
21. Minimum software acceptance criteria
A run can be reproduced from a versioned config without editing code.
Every generation is traceable to exact prompt, model/version, sampling settings, code commit, and timestamp.
Successful responses are never silently regenerated.
Costs and token counts reconcile to provider billing within a documented tolerance.
Annotation labels always retain evidence spans and schema version.
The analysis pipeline is deterministic from frozen input tables.
Tests cover adapters, retries, idempotency, parsing, annotation schema, baseline matching, and exclusion logic.
Leaderboard cannot mix different model snapshots under one displayed model result.
22. Publication/reporting principles
Say “underrepresented relative to the matched demographic baseline,” not “the model hates/erases group X.”
Always show raw counts and denominators with percentages.
Always show uncertainty; avoid ranking tiny differences as meaningful.
Separate confirmatory hypotheses from exploratory findings.
Report failed/refused generations and indeterminate cases.
Do not imply same-sex relationship evidence uniquely determines an individual's sexual identity.
Do not treat population proportionality as the only possible normative ideal; describe the benchmark as demographic calibration.
Document data-source limitations, especially household-based Census measures that do not enumerate every LGBTQ person or every relationship.
23. Recommended first-week work package
Day 1: repository + schemas + one provider adapter + immutable run manifest.
Day 2: draft prompts + baseline registry + 25–50-call smoke test.
Day 3: first 250 pilot generations; inspect failures/duplicates/scorability before continuing.
Day 4: reach ~1,000 pilot generations; manually annotate first 100–200; write annotation guide.
Day 5: implement judge/rules; validation metrics; pilot cost/event-rate report.
Day 6: power simulation + baseline audit + final prompt revisions.
Day 7: freeze protocol candidate and prepare preregistration. Do not start the full model suite until all pilot gates pass.
24. Key references and baseline sources
Wang, D., Brignac, E., Mao, M., et al. (2026). Measuring stereotype and deviation biases in large language models. Scientific Reports 16, 23661. DOI: 10.1038/s41598-026-52923-8. Published May 23, 2026; version of record July 31, 2026.
U.S. Census Bureau (2026). More Female Than Male Same-Sex Couple Households in the United States in 2024. Reports ~1.4 million same-sex couple households in 2024 and documents ACS basis/limitations.
U.S. Census Bureau, 2024 American Community Survey, Table B11009: Coupled Households by Type. National counts for married/cohabiting same-sex and opposite-sex households with margins of error.
Williams Institute (2024). LGBTQ Parenting in the US. Reports ~2.6 million LGBTQ adults parenting minors, ~167,000 same-sex couples parenting children under 18, and ~300,000 children being raised by same-sex couples.
Williams Institute (2025). U.S. Census Snapshots 2020: Same-Sex Couples. National/state/county same-sex couple data and interactive methodology.
25. Open decisions to resolve during pilot — not before coding
Exact five scenarios and two paraphrases per scenario.
Exact geography set and which conditions have sufficiently matched baseline denominators.
Final story length after sensitivity pilot.
Final sampling parameters per provider, balancing comparability with provider-specific API constraints.
Exact confirmatory N/model after pilot event-rate and power simulation.
Whether a name-assisted sensitivity analysis is worth maintaining after observing how often explicit evidence is sufficient.
Final model roster based on available snapshots, terms, and cost immediately before preregistration.

Bottom line: The first benchmark should be intentionally conservative. Its strongest claim is not that proportional representation is the uniquely correct moral output. Its strongest claim is empirical: under neutral social-generation prompts, a model constructs a measurable demographic world, and we can rigorously quantify how that world differs from a matched observed population and from other models. If the pilot proves the labels and denominators are reliable, that framework is reusable for many other demographic groups and future model generations.
