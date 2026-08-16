# Skill Verdicts extend to cover Preferred Skills too, weighted lower

CONTEXT.md originally defined a Skill Verdict as judging a Profile against a JobPosting's Required Skills only. We decided to extend Skill Verdict generation to also cover Preferred Skills, using the same LLM-judged, whole-Profile-as-evidence process as Required Skills ([0001](0001-hybrid-scoring-llm-verdicts-deterministic-aggregation.md)). Preferred Skills are weighted lower than Required Skills when the deterministic aggregator computes the Fit Score (`scoring.py`), but the judgment mechanism itself — match/partial/missing + rationale, read against the whole Profile — is identical for both.

## Considered Options

- **Flat keyword-based bonus for Preferred Skills** (e.g. +X points per Preferred Skill found verbatim in the Profile's skills list, no LLM judgment) — rejected: reintroduces the same semantic-matching gap that [0001](0001-hybrid-scoring-llm-verdicts-deterministic-aggregation.md) rejected pure keyword matching for. A Preferred Skill like "Kubernetes" would miss a Profile's "Docker/container orchestration" Experience Entry evidence just as a Required Skill would.
- **Ignore Preferred Skills entirely** (CONTEXT.md's original scope) — rejected: JobPostings' Preferred Skills carry real signal for repositioning advice and fit nuance; dropping them loses information the user would otherwise have to read the full JobPosting text to recover themselves.

## Consequences

`generate_skill_verdicts` produces one `SkillVerdict` per Required Skill and per Preferred Skill, tagged by `skill_type`. `scoring.py`'s aggregation must weight `required` and `preferred` verdicts differently (`REQUIRED_WEIGHT` / `PREFERRED_WEIGHT`), and must treat an empty Preferred Skills list as a valid case (`preferred_coverage: None`), since not every JobPosting lists Preferred Skills.
