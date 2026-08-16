import re
from datetime import datetime
from pathlib import Path

from fitscorer.models import FitScore, JobPosting, RepositioningSuggestion, SkillVerdict


def _slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return value.strip("-")


def build_report_markdown(
    job_posting: JobPosting,
    verdicts: list[SkillVerdict],
    fit_score: FitScore,
    repositioning: RepositioningSuggestion,
) -> str:
    required = [v for v in verdicts if v.skill_type == "required"]
    preferred = [v for v in verdicts if v.skill_type == "preferred"]

    lines = [
        f"# Fit Report: {job_posting.role_title}",
        "",
        f"**Fit Score:** {fit_score.value}",
        f"**Required Coverage:** {fit_score.required_coverage}",
        f"**Preferred Coverage:** {fit_score.preferred_coverage}",
        "",
        "## Required Skill Verdicts",
        "",
    ]
    for v in required:
        lines.append(f"- **{v.skill_name}** — {v.verdict}: {v.rationale}")

    lines += ["", "## Preferred Skill Verdicts", ""]
    for v in preferred:
        lines.append(f"- **{v.skill_name}** — {v.verdict}: {v.rationale}")

    lines += [
        "",
        "## Repositioning Suggestion",
        "",
        repositioning.text,
    ]

    return "\n".join(lines) + "\n"


def save_report(
    markdown: str, job_posting: JobPosting, *, directory: Path = Path("reports")
) -> Path:
    directory.mkdir(parents=True, exist_ok=True)

    parts = [_slugify(job_posting.role_title)]
    if job_posting.company:
        parts.append(_slugify(job_posting.company))
    parts.append(datetime.now().strftime("%Y%m%d-%H%M%S"))

    filename = "_".join(parts) + ".md"
    path = directory / filename
    path.write_text(markdown, encoding="utf-8")
    return path
