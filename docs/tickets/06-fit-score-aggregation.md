# 06 — Fit Score Aggregation

**Status:** Done — `test_scoring.py` (7 tests) and `scoring.py` implemented, `uv run pytest` green (33/33).

## Goal

Deterministically aggregate `SkillVerdict`s into a single `FitScore` — pure function, no LLM involved (ADR 0001). This is the TDD centerpiece of the pipeline.

## Test file first (TDD)

`tests/unit/test_scoring.py`, written first, covers:

- All-match → `100.0`.
- All-missing → `0.0`.
- Required-only (no Preferred) → `value` equals exact `required_coverage * 100`, `preferred_coverage is None`.
- Mixed Required + all-missing Preferred → score below the Required-only case.
- Empty `required` list → `ValueError`.
- Rounding to 1dp.
- Sanity check: `REQUIRED_WEIGHT + PREFERRED_WEIGHT == 1.0`.

## Implementation file

`src/fitscorer/scoring.py` — `compute_fit_score(verdicts: list[SkillVerdict]) -> FitScore`, pure function:

```python
VERDICT_POINTS = {"match": 1.0, "partial": 0.5, "missing": 0.0}
REQUIRED_WEIGHT = 0.8
PREFERRED_WEIGHT = 0.2

def compute_fit_score(verdicts: list[SkillVerdict]) -> FitScore:
    required = [v for v in verdicts if v.skill_type == "required"]
    preferred = [v for v in verdicts if v.skill_type == "preferred"]
    if not required:
        raise ValueError("Fit Score requires at least one Required Skill Verdict")
    required_coverage = sum(VERDICT_POINTS[v.verdict] for v in required) / len(required)
    if preferred:
        preferred_coverage = sum(VERDICT_POINTS[v.verdict] for v in preferred) / len(preferred)
        raw = REQUIRED_WEIGHT * required_coverage + PREFERRED_WEIGHT * preferred_coverage
    else:
        preferred_coverage = None
        raw = required_coverage
    return FitScore(
        value=round(raw * 100, 1),
        required_coverage=round(required_coverage * 100, 1),
        preferred_coverage=None if preferred_coverage is None else round(preferred_coverage * 100, 1),
    )
```

No LLM import anywhere in this file — the only import path into scoring is `models.py`.

## Verification

`uv run pytest` — unit suite green.
