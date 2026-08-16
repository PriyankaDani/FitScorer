from fitscorer.models import (
    SkillVerdict,
    FitScore,
)

REQUIRED_WEIGHT = 0.8
PREFERRED_WEIGHT = 0.2
VERDICT_POINTS = {"match": 1.0, "partial": 0.5, "missing": 0.0}

def compute_fit_score(verdicts: list[SkillVerdict]) -> FitScore:
    required = [v for v in verdicts if v.skill_type == "required"]
    preferred = [v for v in verdicts if v.skill_type == "preferred"]

    if not required:
        raise ValueError("At least one required skill is needed to compute fit score.")

    required_coverage = sum(VERDICT_POINTS[v.verdict] for v in required)/len(required)

    if preferred:
        preferred_coverage = sum(VERDICT_POINTS[v.verdict] for v in preferred)/len(preferred)
        raw = REQUIRED_WEIGHT * required_coverage + PREFERRED_WEIGHT * preferred_coverage
    else:
        preferred_coverage = None
        raw = required_coverage  # If no preferred skills, fit score is just required coverage.

    return FitScore(
        value = round(raw*100, 1),
        required_coverage = round(required_coverage*100, 1),
        preferred_coverage = None if preferred_coverage is None else round(preferred_coverage*100, 1)
    )