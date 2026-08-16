from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class SkillEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    category: str
    proficiency: Literal["familiar", "intermediate", "advanced", "expert"]


class ExperienceEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role_title: str
    start_date: str
    end_date: Optional[str] = None
    description: str
    key_skills_demonstrated: list[str] = []


class EducationEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    degree: str
    field_of_study: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    grade: Optional[str] = None
    thesis_title: Optional[str] = None
    notable_coursework: list[str] = []


class CertificationEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    year: Optional[str] = None
    distinction: bool = False


class LanguageEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    language: str
    proficiency: str


class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: int
    summary: str
    skills: list[SkillEntry]
    experience: list[ExperienceEntry]
    education: list[EducationEntry]
    certifications: list[CertificationEntry] = []
    languages: list[LanguageEntry] = []


class RequiredSkill(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str


class PreferredSkill(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str


class JobPosting(BaseModel):
    model_config = ConfigDict(extra="forbid")

    raw_text: str
    role_title: str
    company: Optional[str] = None
    seniority_level: Optional[str] = None
    required_skills: list[RequiredSkill]
    preferred_skills: list[PreferredSkill]


class SkillVerdict(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_name: str
    skill_type: Literal["required", "preferred"]
    verdict: Literal["match", "partial", "missing"]
    rationale: str


class FitScore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: float
    required_coverage: float
    preferred_coverage: Optional[float] = None


class RepositioningSuggestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
