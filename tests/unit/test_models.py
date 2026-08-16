import pytest
from pydantic import ValidationError

from fitscorer.models import (
    CertificationEntry,
    EducationEntry,
    ExperienceEntry,
    FitScore,
    JobPosting,
    LanguageEntry,
    PreferredSkill,
    Profile,
    RepositioningSuggestion,
    RequiredSkill,
    SkillEntry,
    SkillVerdict,
)


# --- PII-guard regression tests (ADR 0002) ---


def test_experience_entry_rejects_employer_field():
    with pytest.raises(ValidationError):
        ExperienceEntry(
            employer="Acme Corp",
            role_title="Software Engineer",
            start_date="2020-01",
            end_date=None,
            description="Built things.",
        )


def test_education_entry_rejects_institute_field():
    with pytest.raises(ValidationError):
        EducationEntry(
            institute="Acme University",
            degree="BSc",
            field_of_study="Computer Science",
            start_date="2016-09",
            end_date="2020-06",
            grade=None,
            thesis_title=None,
        )


# --- SkillEntry ---


def test_skill_entry_valid_proficiency():
    entry = SkillEntry(name="Python", category="Programming", proficiency="advanced")
    assert entry.proficiency == "advanced"


def test_skill_entry_rejects_invalid_proficiency():
    with pytest.raises(ValidationError):
        SkillEntry(name="Python", category="Programming", proficiency="guru")


def test_skill_entry_rejects_extra_fields():
    with pytest.raises(ValidationError):
        SkillEntry(name="Python", category="Programming", proficiency="advanced", years=5)


# --- ExperienceEntry ---


def test_experience_entry_valid():
    entry = ExperienceEntry(
        role_title="Software Engineer",
        start_date="2020-01",
        end_date=None,
        description="Built things.",
    )
    assert entry.role_title == "Software Engineer"
    assert entry.key_skills_demonstrated == []


def test_experience_entry_accepts_key_skills_demonstrated():
    entry = ExperienceEntry(
        role_title="Software Engineer",
        start_date="2020-01",
        end_date="2022-05",
        description="Built things.",
        key_skills_demonstrated=["Python", "SQL"],
    )
    assert entry.key_skills_demonstrated == ["Python", "SQL"]


# --- EducationEntry ---


def test_education_entry_valid():
    entry = EducationEntry(
        degree="BSc",
        field_of_study="Computer Science",
        start_date="2016-09",
        end_date="2020-06",
        grade=None,
        thesis_title=None,
    )
    assert entry.degree == "BSc"
    assert entry.notable_coursework == []


# --- CertificationEntry ---


def test_certification_entry_defaults_distinction_false():
    cert = CertificationEntry(name="AWS Certified", year="2023")
    assert cert.distinction is False


# --- LanguageEntry ---


def test_language_entry_valid():
    lang = LanguageEntry(language="English", proficiency="fluent")
    assert lang.language == "English"


# --- Profile ---


def test_profile_valid_with_defaults():
    profile = Profile(
        schema_version=1,
        summary="A software engineer.",
        skills=[SkillEntry(name="Python", category="Programming", proficiency="advanced")],
        experience=[
            ExperienceEntry(
                role_title="Software Engineer",
                start_date="2020-01",
                end_date=None,
                description="Built things.",
            )
        ],
        education=[
            EducationEntry(
                degree="BSc",
                field_of_study="Computer Science",
                start_date="2016-09",
                end_date="2020-06",
                grade=None,
                thesis_title=None,
            )
        ],
    )
    assert profile.certifications == []
    assert profile.languages == []


def test_profile_rejects_extra_fields():
    with pytest.raises(ValidationError):
        Profile(
            schema_version=1,
            summary="A software engineer.",
            skills=[],
            experience=[],
            education=[],
            employer="Acme Corp",
        )


# --- JobPosting / RequiredSkill / PreferredSkill ---


def test_job_posting_valid():
    posting = JobPosting(
        raw_text="We are hiring a Senior Software Engineer...",
        role_title="Senior Software Engineer",
        company="Acme Corp",
        seniority_level="Senior",
        required_skills=[RequiredSkill(name="Python")],
        preferred_skills=[PreferredSkill(name="Kubernetes")],
    )
    assert posting.company == "Acme Corp"
    assert posting.required_skills[0].name == "Python"


def test_job_posting_company_optional():
    posting = JobPosting(
        raw_text="We are hiring...",
        role_title="Engineer",
        company=None,
        seniority_level=None,
        required_skills=[RequiredSkill(name="Python")],
        preferred_skills=[],
    )
    assert posting.company is None


# --- SkillVerdict ---


def test_skill_verdict_valid():
    verdict = SkillVerdict(
        skill_name="Python",
        skill_type="required",
        verdict="match",
        rationale="Extensive Python experience across multiple roles.",
    )
    assert verdict.verdict == "match"


def test_skill_verdict_rejects_invalid_verdict():
    with pytest.raises(ValidationError):
        SkillVerdict(
            skill_name="Python",
            skill_type="required",
            verdict="excellent",
            rationale="...",
        )


def test_skill_verdict_rejects_invalid_skill_type():
    with pytest.raises(ValidationError):
        SkillVerdict(
            skill_name="Python",
            skill_type="bonus",
            verdict="match",
            rationale="...",
        )


# --- FitScore ---


def test_fit_score_valid():
    score = FitScore(value=87.5, required_coverage=90.0, preferred_coverage=75.0)
    assert score.value == 87.5


def test_fit_score_preferred_coverage_optional():
    score = FitScore(value=90.0, required_coverage=90.0, preferred_coverage=None)
    assert score.preferred_coverage is None


# --- RepositioningSuggestion ---


def test_repositioning_suggestion_text_only():
    suggestion = RepositioningSuggestion(text="Emphasize your cloud migration work.")
    assert suggestion.text == "Emphasize your cloud migration work."


def test_repositioning_suggestion_rejects_numeric_field():
    with pytest.raises(ValidationError):
        RepositioningSuggestion(text="Emphasize your cloud migration work.", score=80)
