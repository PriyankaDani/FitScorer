import pytest

from fitscorer.models import SkillVerdict
from fitscorer.scoring import compute_fit_score, REQUIRED_WEIGHT, PREFERRED_WEIGHT

#all-match
def test_all_skills_match():
    # Arrange: one required + one preferred SkillVerdict, both "match".
    # skill_name/rationale are irrelevant to aggregation, so keep them minimal.
    verdicts = [
        SkillVerdict(
            skill_name="Python",
            skill_type="required",
            verdict="match",
            rationale="Profile lists 5 years of Python experience.",
        ),
        SkillVerdict(
            skill_name="Docker",
            skill_type="preferred",
            verdict="match",
            rationale="Profile lists Docker under skills.",
        ),
    ]

    # Act: run the function under test.
    result = compute_fit_score(verdicts)

    # Assert: check the returned FitScore's fields, not just that it ran.
    assert result.value == 100.0
    assert result.required_coverage == 100.0
    assert result.preferred_coverage == 100.0

#all-missing
def test_all_skills_missing():
    verdicts = [
        SkillVerdict(
            skill_name="Python",
            skill_type="required",
            verdict="missing",
            rationale="Profile doesn't mention Python.",
        ),
        SkillVerdict(
            skill_name="Docker",
            skill_type="preferred",
            verdict="missing",
            rationale="Profile doesn't mention Docker.",
        ),
    ]

    result = compute_fit_score(verdicts)

    assert result.value == 0.0
    assert result.required_coverage == 0.0
    assert result.preferred_coverage == 0.0

#required-only
def test_all_required_match_no_preferred_skill():
    verdicts = [
        SkillVerdict(
            skill_name = "Python",
            skill_type = "required",
            verdict = "match",
            rationale = "Profile lists 5 years of Python experience.",
        )
    ]

    result = compute_fit_score(verdicts)

    assert result.value == 100.0
    assert result.required_coverage == 100.0
    assert result.preferred_coverage is None

#mixed Required+all-missing-preferred
def test_mixed_required_and_missing_preferred():
    verdicts = [
        SkillVerdict(
            skill_name = "Python",
            skill_type = "required",
            verdict = "match",
            rationale = "Profile lists 5 years of Python experience.",
        ),
        SkillVerdict(
            skill_name = "Java",
            skill_type = "required",
            verdict = "missing",
            rationale = "Profile doesn't mention Java.",
        ),
        SkillVerdict(
            skill_name = "C++",
            skill_type = "required",
            verdict = "partial",            
            rationale = "Profile lists some C++ experience, but not enough.",
        ),
        SkillVerdict(
            skill_name = "Docker",
            skill_type = "preferred",
            verdict = "missing",
            rationale = "Profile doesnt mention Docker",
        )
    ]

    result = compute_fit_score(verdicts)

    assert result.value < 100.0
    assert result.required_coverage < 100.0
    assert result.preferred_coverage == 0.0

#empty required
def test_empty_required_skills():
    verdicts = [
        SkillVerdict(
            skill_name = "Docker",
            skill_type = "preferred",
            verdict = "match",
            rationale = "Profile lists Docker under skills.",
        ),
        SkillVerdict(
            skill_name = "Kubernetes",
            skill_type = "preferred",
            verdict = "missing",
            rationale = "Profile doesn't mention Kubernetes.",
        ),
    ]

    with pytest.raises(ValueError):
        compute_fit_score(verdicts) 

#rounding
def test_rounding_behavior():
    verdicts = [
        SkillVerdict(
            skill_name = "Python",
            skill_type = "required",
            verdict = "match",
            rationale = "Profile lists 5 years of Python experience.",
        ),
        SkillVerdict(
            skill_name = "Java",
            skill_type = "required",
            verdict = "missing",
            rationale = "Profile doesn't mention Java.",
        ),
        SkillVerdict(
            skill_name = "TypeScript",
            skill_type = "required",
            verdict = "missing",
            rationale = "Profile doesnt list TypeScript experience.",
        ),
        SkillVerdict(
            skill_name = "Docker",
            skill_type = "preferred",
            verdict = "match",
            rationale = "Profile lists Docker under skills.",
        ),
        SkillVerdict(
            skill_name = "Kubernetes",
            skill_type = "preferred",
            verdict = "missing",
            rationale = "Profile doesn't mention Kubernetes.",
        ),
    ]

    result = compute_fit_score(verdicts)

    # The expected values are based on the scoring logic and rounding behavior.
    assert result.value == 36.7
    assert result.required_coverage == 33.3
    assert result.preferred_coverage== 50.0

#sanity-check -REQUIRED_WEIGHT + PREFERRED_WEIGHT == 1.0 sanity check.
def test_sanity_check_weights():
    total_weight = REQUIRED_WEIGHT + PREFERRED_WEIGHT
    assert total_weight == 1.0