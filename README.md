# WorldCal

WorldCal measures **demographic calibration** in ordinary, open-ended LLM generation: when a model is asked to write a normal social story, what population does the generated world look like, and how does that compare to a matched real-world baseline?

This is a measurement project. A model can deviate from a census baseline without that fact implying a single correct moral output policy.

**Study 1** (in progress) asks whether sexuality-neutral U.S. family and couple stories spontaneously contain same-sex relationships at rates that can be compared to American Community Survey and Williams Institute denominators. Details: [docs/research-spec.md](docs/research-spec.md). Operating tracker: [PLAN.md](PLAN.md).

Site: [worldcal.org](https://worldcal.org) (being stood up).

## Status

First public milestone is a working generator on Amazon Bedrock and a private packet of stories to inspect. There is no leaderboard yet. Draft prompts and raw generations are not in this repository ([docs/prompt-policy.md](docs/prompt-policy.md)).

## License

Apache License 2.0. See [LICENSE](LICENSE).
