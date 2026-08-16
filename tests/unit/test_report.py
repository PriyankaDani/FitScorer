import re
from pathlib import Path

import pytest

from fitscorer.models import FitScore, JobPosting, PreferredSkill, RepositioningSuggestion, RequiredSkill, SkillVerdict
from fitscorer.report import build_report_markdown, save_report


@pytest.fixture
def sample_job_posting_with_company() -> JobPosting:
    return JobPosting(
        raw_text="We are hiring a Senior Backend Engineer with Python and Kubernetes experience.",
        role_title="Senior Backend Engineer",
        company="Acme Corp",
        seniority_level="Senior",
        required_skills=[RequiredSkill(name="Python"), RequiredSkill(name="SQL")],
        preferred_skills=[PreferredSkill(name="Kubernetes")],
    )


@pytest.fixture
def sample_job_posting_without_company() -> JobPosting:
    return JobPosting(
        raw_text="We are hiring a Senior Backend Engineer with Python and Kubernetes experience.",
        role_title="Senior Backend Engineer",
        company=None,
        seniority_level="Senior",
        required_skills=[RequiredSkill(name="Python"), RequiredSkill(name="SQL")],
        preferred_skills=[PreferredSkill(name="Kubernetes")],
    )


@pytest.fixture
def sample_verdicts() -> list[SkillVerdict]:
    return [
        SkillVerdict(
            skill_name="Python",
            skill_type="required",
            verdict="match",
            rationale="matches profile evidence",
        ),
        SkillVerdict(
            skill_name="SQL",
            skill_type="required",
            verdict="partial",
            rationale="some overlap with profile evidence",
        ),
        SkillVerdict(
            skill_name="Kubernetes",
            skill_type="preferred",
            verdict="missing",
            rationale="no supporting evidence in profile",
        ),
    ]


@pytest.fixture
def sample_fit_score() -> FitScore:
    return FitScore(value=72.5, required_coverage=75.0, preferred_coverage=0.0)


@pytest.fixture
def sample_repositioning() -> RepositioningSuggestion:
    return RepositioningSuggestion(text="Lean on adjacent evidence for Kubernetes.")


# build_report_markdown content checks


def test_report_contains_fit_score(
    sample_job_posting_with_company, sample_verdicts, sample_fit_score, sample_repositioning
):
    markdown = build_report_markdown(
        sample_job_posting_with_company, sample_verdicts, sample_fit_score, sample_repositioning
    )

    assert str(sample_fit_score.value) in markdown


def test_report_contains_required_and_preferred_verdicts(
    sample_job_posting_with_company, sample_verdicts, sample_fit_score, sample_repositioning
):
    markdown = build_report_markdown(
        sample_job_posting_with_company, sample_verdicts, sample_fit_score, sample_repositioning
    )

    assert "Python" in markdown
    assert "SQL" in markdown
    assert "Kubernetes" in markdown
    assert "Required" in markdown
    assert "Preferred" in markdown


def test_report_contains_repositioning_text(
    sample_job_posting_with_company, sample_verdicts, sample_fit_score, sample_repositioning
):
    markdown = build_report_markdown(
        sample_job_posting_with_company, sample_verdicts, sample_fit_score, sample_repositioning
    )

    assert sample_repositioning.text in markdown


# save_report filename convention


def test_save_report_filename_includes_role_title_company_and_timestamp(
    sample_job_posting_with_company, tmp_path
):
    path = save_report("# Report", sample_job_posting_with_company, directory=tmp_path)

    assert re.match(
        r"^senior-backend-engineer_acme-corp_\d{8}-\d{6}\.md$", path.name
    )


def test_save_report_writes_under_given_directory_only(sample_job_posting_with_company, tmp_path):
    path = save_report("# Report", sample_job_posting_with_company, directory=tmp_path)

    assert path.parent == tmp_path
    assert path.read_text() == "# Report"


def test_save_report_company_none_has_no_dangling_separator(
    sample_job_posting_without_company, tmp_path
):
    path = save_report("# Report", sample_job_posting_without_company, directory=tmp_path)

    assert "__" not in path.name
    assert re.match(r"^senior-backend-engineer_\d{8}-\d{6}\.md$", path.name)


def test_save_report_writes_utf8_regardless_of_platform_default_encoding(
    sample_job_posting_with_company, tmp_path
):
    markdown = "# Report\n\n- Käse — 100% passt: Erfahrung überzeugt."

    path = save_report(markdown, sample_job_posting_with_company, directory=tmp_path)

    assert path.read_text(encoding="utf-8") == markdown


def test_save_report_defaults_to_reports_directory(sample_job_posting_with_company, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    path = save_report("# Report", sample_job_posting_with_company)

    assert path.parent.resolve() == (tmp_path / "reports").resolve()
    assert path.parent.is_dir()
