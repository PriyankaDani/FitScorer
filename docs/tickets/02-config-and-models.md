# 02 — Config & Models

**Status:** Done

## Goal

Typed, validated app config, and the full Pydantic domain model — including the PII-exclusion guarantee from ADR 0002 made testable, not just documented.

## Test files first (TDD)

- `tests/unit/test_config.py`
- `tests/unit/test_models.py` — includes the regression tests proving `ExperienceEntry(employer=...)` and `EducationEntry(institute=...)` raise `ValidationError`.

## Implementation files

- `src/fitscorer/config.py` — `Settings` (`pydantic-settings`): `LLM_PROVIDER` (`Literal["ollama","gemini"]`), `OLLAMA_MODEL`, `OLLAMA_BASE_URL`, `GEMINI_MODEL`, `GOOGLE_API_KEY`. Loads from `.env`; rejects an invalid `LLM_PROVIDER` at startup rather than a plain `os.environ` read.
- `src/fitscorer/models.py`

## Schema detail (ADR 0002 enforcement)

All models are `pydantic.BaseModel` with `model_config = ConfigDict(extra="forbid")`.

- `Profile`: `schema_version`, `summary`, `skills: list[SkillEntry]`, `experience: list[ExperienceEntry]`, `education: list[EducationEntry]`, `certifications: list[CertificationEntry] = []`, `languages: list[LanguageEntry] = []`
- `SkillEntry`: `name`, `category`, `proficiency: Literal["familiar","intermediate","advanced","expert"]`
- `ExperienceEntry` (**no employer field**): `role_title`, `start_date`, `end_date: str|None`, `description` (genericized, user's responsibility), `key_skills_demonstrated: list[str] = []`
- `EducationEntry` (**no institute field**): `degree`, `field_of_study: str|None`, `start_date`, `end_date: str|None`, `grade: str|None`, `thesis_title: str|None`, `notable_coursework: list[str] = []`
- `CertificationEntry`: `name`, `year: str|None`, `distinction: bool = False`
- `LanguageEntry`: `language`, `proficiency`
- `JobPosting`: `raw_text`, `role_title`, `company: str|None` (fine to appear in Report filenames — ADR 0002 only concerns the user's own Profile PII), `seniority_level: str|None`, `required_skills: list[RequiredSkill]`, `preferred_skills: list[PreferredSkill]`
- `SkillVerdict`: `skill_name`, `skill_type: Literal["required","preferred"]`, `verdict: Literal["match","partial","missing"]`, `rationale`
- `FitScore`: `value: float` (0–100, 1dp), `required_coverage: float`, `preferred_coverage: float|None`
- `RepositioningSuggestion`: `text` only — structurally cannot carry a numeric field

**Scope cut:** Research Projects and Publications (present in `jane_doe_profile.md`) are not modeled as separate schema entities — that evidence folds into `ExperienceEntry.description` / `key_skills_demonstrated` instead.

## Also in this phase

`tests/conftest.py` — `sample_profile()`, `sample_job_posting()` fixtures, reused by later test files.

## Verification

`uv run pytest` — full unit suite green.
