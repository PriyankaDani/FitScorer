# Hybrid scoring: LLM produces per-skill verdicts, deterministic code aggregates the Fit Score

We need to judge how well a Profile fits a JobPosting's Required Skills. A pure keyword/string match against the Profile's skill list would miss semantic and adjacent matches (e.g. a JobPosting asking for "Kubernetes" when the Profile only lists "Docker/container orchestration" experience), but letting an LLM produce the Fit Score directly would make the score non-reproducible and hard to unit test. We decided the LLM produces a Skill Verdict (match/partial/missing + rationale) per Required Skill — reading the *entire* Profile, not just its skills section, so Experience and Education Entries can serve as evidence — and deterministic code aggregates all Verdicts into the numeric Fit Score. The Repositioning Suggestion is a further, separate LLM call that narrates the already-computed gap; it never invents its own score.

## Considered Options

- **Pure deterministic matching** (string/fuzzy match against the Profile's skill list only) — rejected: misses semantic matches and ignores Experience/Education as evidence.
- **LLM produces the Fit Score directly** — rejected: score becomes non-deterministic and effectively untestable with plain unit tests, undermining the brief's TDD requirement.
- **Separate scoring passes for skills vs. education vs. experience, then weighted-summed** — rejected: double-counts the same evidence (an Experience Entry that justifies a skill match would also inflate a parallel "experience" score) and adds complexity without a clear benefit over folding that evidence into the per-skill Verdict.

## Consequences

Skill Verdicts must be treated as the seam between the LLM boundary and deterministic code, both for testing (mock at the Verdict boundary) and for future changes (e.g. new Verdict values or aggregation weights don't require touching the LLM call).
