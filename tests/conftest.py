import pytest

from fitscorer.models import (
    EducationEntry,
    ExperienceEntry,
    JobPosting,
    PreferredSkill,
    Profile,
    RequiredSkill,
    SkillEntry,
)


@pytest.fixture
def sample_profile() -> Profile:
    return Profile(
        schema_version=1,
        summary="A backend engineer with a focus on distributed systems.",
        skills=[
            SkillEntry(name="Python", category="Programming", proficiency="expert"),
            SkillEntry(name="SQL", category="Data", proficiency="advanced"),
        ],
        experience=[
            ExperienceEntry(
                role_title="Backend Engineer",
                start_date="2020-01",
                end_date=None,
                description="Built and maintained backend services handling millions of requests per day.",
                key_skills_demonstrated=["Python", "SQL"],
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


@pytest.fixture
def sample_job_posting() -> JobPosting:
    return JobPosting(
        raw_text="We are hiring a Senior Backend Engineer with Python and Kubernetes experience.",
        role_title="Senior Backend Engineer",
        company="Acme Corp",
        seniority_level="Senior",
        required_skills=[RequiredSkill(name="Python"), RequiredSkill(name="SQL")],
        preferred_skills=[PreferredSkill(name="Kubernetes")],
    )
