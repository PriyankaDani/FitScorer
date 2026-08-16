from dataclasses import dataclass, field
from datetime import datetime

from fitscorer.models import FitScore, JobPosting, RepositioningSuggestion, SkillVerdict


@dataclass
class SessionEntry:
    job_posting: JobPosting
    verdicts: list[SkillVerdict]
    fit_score: FitScore
    repositioning: RepositioningSuggestion
    timestamp: datetime


@dataclass
class Session:
    entries: list[SessionEntry] = field(default_factory=list)

    def add_run(
        self,
        job_posting: JobPosting,
        verdicts: list[SkillVerdict],
        fit_score: FitScore,
        repositioning: RepositioningSuggestion,
    ) -> SessionEntry:
        entry = SessionEntry(
            job_posting=job_posting,
            verdicts=verdicts,
            fit_score=fit_score,
            repositioning=repositioning,
            timestamp=datetime.now(),
        )
        self.entries.append(entry)
        return entry
