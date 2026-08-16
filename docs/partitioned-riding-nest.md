# FitScorer v1 — Project Creation Plan

## Context

`D:\FitScorer` currently holds only `CLAUDE.md`, `CONTEXT.md`, and `docs/` (four ADRs, a project brief, and a mock master-profile file) — no code yet. This plan scaffolds the project from scratch and builds the full v1 pipeline described in the brief: load a Profile once, paste JobPostings repeatedly, get a Fit Score + Skill Verdicts + Repositioning Suggestion for each, browse the Session History, and optionally save a Report. The design must stay inside four binding ADRs already on disk (hybrid LLM/deterministic scoring, PII excluded at the schema level, Streamlit GUI, three swappable seams) and CLAUDE.md's rules (uv, LangChain, pytest, TDD-mandatory for the core pipeline, provider-agnostic LLM selection).

User has confirmed: (1) initialize git with an initial commit, (2) plan the full v1 pipeline not just scaffolding, (3) Skill Verdicts extend to cover Preferred Skills too (not just Required), weighted lower in the Fit Score — this is a deliberate, sign-off'd extension to CONTEXT.md's current Verdict definition and gets its own ADR.

## Layout

`src/` layout via `uv init --package .`: keeps the installable `fitscorer` package separate from `docs/`, `data/`, `reports/` at the repo root, and matches uv's own scaffold so `uv run` / `uv run pytest` resolve `import fitscorer` consistently.

```
D:\FitScorer\
├── pyproject.toml, uv.lock, .python-version, .gitignore, .env.example
├── data/profile.example.json          (fictitious sample Profile, committed)
├── reports/.gitkeep                   (dir tracked; generated .md files gitignored)
├── src/fitscorer/
│   ├── __init__.py
│   ├── config.py                      Settings (pydantic-settings): LLM_PROVIDER, model names
│   ├── models.py                      Profile, SkillEntry, ExperienceEntry, EducationEntry,
│   │                                   CertificationEntry, LanguageEntry, JobPosting,
│   │                                   RequiredSkill, PreferredSkill, SkillVerdict, FitScore,
│   │                                   RepositioningSuggestion
│   ├── llm/provider.py                get_chat_model(settings) factory (Ollama vs Gemini) —
│   │                                   the ONLY file that imports langchain-ollama /
│   │                                   langchain-google-genai
│   ├── extraction.py                  extract_job_posting(raw_text, chat_model)
│   ├── verdicts.py                    generate_skill_verdicts(profile, job_posting, chat_model)
│   ├── scoring.py                     compute_fit_score(verdicts) — pure, deterministic
│   ├── repositioning.py               generate_repositioning_suggestion(verdicts, fit_score, chat_model)
│   ├── report.py                      build_report_markdown(...), save_report(...)
│   ├── session.py                     Session, SessionEntry — plain, no Streamlit imports
│   └── app.py                         Streamlit entrypoint
└── tests/
    ├── conftest.py                    sample_profile(), sample_job_posting() fixtures
    ├── unit/                          test_config, test_models, test_provider, test_extraction,
    │                                  test_verdicts, test_scoring, test_repositioning,
    │                                  test_report, test_session
    └── integration/                   test_extraction_ollama.py, test_verdicts_ollama.py,
                                        marker "integration", skipped by default and if Ollama
                                        isn't reachable
```

LLM-touching unit tests use a small hand-written fake chat model implementing `.with_structured_output(schema).invoke(...)` — not deep-patched LangChain mocks — so tests stay fast, offline, and don't break on unrelated LangChain internals.

## Profile schema (ADR 0002 enforcement)

All models are `pydantic.BaseModel` with `model_config = ConfigDict(extra="forbid")`. `test_models.py` includes a regression test proving `ExperienceEntry(employer=...)` / `EducationEntry(institute=...)` raise `ValidationError` — this makes the PII-exclusion guarantee testable, not just documented.

- `Profile`: `schema_version`, `summary`, `skills: list[SkillEntry]`, `experience: list[ExperienceEntry]`, `education: list[EducationEntry]`, `certifications: list[CertificationEntry] = []`, `languages: list[LanguageEntry] = []`
- `SkillEntry`: `name`, `category`, `proficiency: Literal["familiar","intermediate","advanced","expert"]`
- `ExperienceEntry` (**no employer field**): `role_title`, `start_date`, `end_date: str|None`, `description` (genericized, user's responsibility), `key_skills_demonstrated: list[str] = []`
- `EducationEntry` (**no institute field**): `degree`, `field_of_study: str|None`, `start_date`, `end_date: str|None`, `grade: str|None`, `thesis_title: str|None`, `notable_coursework: list[str] = []`
- `CertificationEntry`: `name`, `year: str|None`, `distinction: bool = False`
- `LanguageEntry`: `language`, `proficiency`

**Scope cut:** Research Projects and Publications (present in `jane_doe_profile.md`) are not modeled as separate schema entities — CONTEXT.md doesn't define those as terms; that evidence folds into `ExperienceEntry.description` / `key_skills_demonstrated` instead. `data/profile.example.json` is a hand-written fictitious profile shaped like this schema (loosely structured like `jane_doe_profile.md` but invented content) — the real `jane_doe_profile.md` is never ingested directly by the app; the user manually authors their own genericized `data/profile.json` (gitignored) from it.

**JobPosting / Verdict / Score:**
- `JobPosting`: `raw_text`, `role_title`, `company: str|None` (extraction from external text — fine to appear in Report filenames, ADR 0002 only concerns the user's own Profile PII), `seniority_level: str|None`, `required_skills: list[RequiredSkill]`, `preferred_skills: list[PreferredSkill]`
- `SkillVerdict`: `skill_name`, `skill_type: Literal["required","preferred"]`, `verdict: Literal["match","partial","missing"]`, `rationale`
- `FitScore`: `value: float` (0–100, 1dp), `required_coverage: float`, `preferred_coverage: float|None`
- `RepositioningSuggestion`: `text` only — structurally cannot carry a numeric field

## Fit Score formula (`scoring.py`, pure function, TDD centerpiece)

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

`test_scoring.py` (written first) covers: all-match→100.0; all-missing→0.0; Required-only (no Preferred)→exact `required_coverage*100`, `preferred_coverage is None`; mixed Required+all-missing-Preferred → score below the Required-only case; empty `required`→`ValueError`; rounding; `REQUIRED_WEIGHT + PREFERRED_WEIGHT == 1.0` sanity check.

## Dependencies

```
uv add pydantic pydantic-settings python-dotenv langchain langchain-core langchain-ollama langchain-google-genai streamlit
uv add --dev pytest pytest-mock
```

`pydantic-settings` + `.env` gives typed, validated config (rejects a bad `LLM_PROVIDER` at startup) rather than plain `os.environ`. `llm/provider.py` is the only file importing either provider SDK, so provider-agnosticism in scoring/aggregation is structurally enforced — no import path lets `scoring.py` reach a provider package.

## pytest config

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = ["integration: hits real Ollama; run manually with `uv run pytest -m integration`"]
addopts = "-m 'not integration'"
```
`tests/integration/conftest.py` additionally has an autouse fixture that skips if Ollama isn't reachable (quick `httpx.get("http://localhost:11434")`), so even an explicit `-m integration` run degrades gracefully. Default `uv run pytest` only runs `tests/unit/*`.

## Build phases (TDD-first for extraction / verdicts→aggregation / Fit Score / Report generation)

1. **Scaffold** — `uv init --package .`; `uv add` deps; `.gitignore`, `.env.example`, `reports/.gitkeep`, `data/profile.example.json`; pytest config in `pyproject.toml`; `git init` + initial commit (scaffold only, no pipeline code).
2. **Config & models** — `test_config.py` → `config.py`; `test_models.py` (incl. PII-guard regression tests) → `models.py`; add `tests/conftest.py` fixtures.
3. **LLM provider factory** — `test_provider.py` → `llm/provider.py` (`get_chat_model`, provider switch via monkeypatched constructors, no real network calls in unit tests).
4. **Extraction** — `test_extraction.py` first (fake chat model; empty/whitespace input rejected before any LLM call; malformed output → clear `ExtractionError`) → `extraction.py`. Prompt treats `raw_text` strictly as data, never instructions (baseline injection defense).
5. **Skill Verdicts (incl. Preferred)** — `test_verdicts.py` first (verdict count == required+preferred skills, correct `skill_type` tagging, malformed-output case) → `verdicts.py`, passing the **whole** Profile as evidence per ADR 0001. Add `docs/adr/0005-skill-verdicts-cover-preferred-skills-too.md` recording this as a deliberate extension (rejected alternative: flat keyword-based bonus for Preferred Skills — rejected for reintroducing the same semantic-matching gap ADR 0001 rejected pure keyword matching for). Update CONTEXT.md's Skill Verdict entry with one sentence noting it also covers Preferred Skills, weighted lower.
6. **Fit Score aggregation** — `test_scoring.py` first (full case list above) → `scoring.py`.
7. **Repositioning Suggestion** — `test_repositioning.py` first (asserts prompt includes the already-computed `fit_score.value`; return type carries no numeric field) → `repositioning.py`.
8. **Report generation & saving** — `test_report.py` first (`build_report_markdown` content checks; `save_report` filename `<role-title>_<company>_<timestamp>.md` slugified, `tmp_path`-isolated, `company is None` case has no dangling separator) → `report.py`. Real save path defaults to `reports/`, overridable for tests.
9. **Session / Session History** — `test_session.py` (`Session.add_run` appends `SessionEntry` with timestamp, insertion order preserved) → `session.py`, zero Streamlit imports (ADR 0004 interface seam).
10. **Streamlit wiring** (no unit tests; Playwright explicitly deferred until the user confirms UI stability) — `app.py`: sidebar Profile load into `st.session_state`, cached chat model via `st.cache_resource`, JobPosting paste + Score button chaining phases 4→5→6→7, results view (Fit Score, Verdicts split Required/Preferred, Repositioning text), Session History table, per-run "Save Report" button that calls `save_report` **only on click**. Manual smoke test: `uv run streamlit run src/fitscorer/app.py` end-to-end against Ollama with `data/profile.example.json`.

One commit per phase (red/green pairs) suggested for an inspectable TDD history.

## .gitignore

```
.venv/
venv/
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/
.env
reports/*.md
!reports/.gitkeep
data/profile.json
!data/profile.example.json
.streamlit/secrets.toml
*.egg-info/
dist/
build/
```
`data/profile.json` (the user's real Profile) is gitignored by name — only the fictitious `data/profile.example.json` is committed, as belt-and-suspenders alongside the schema-level PII exclusion.

## Tickets

Before any implementation starts, write one ticket per build phase (Scaffold, Config & models, LLM provider factory, Extraction, Skill Verdicts, Fit Score aggregation, Repositioning Suggestion, Report generation & saving, Session/Session History, Streamlit wiring) as local markdown files under `docs/tickets/`, e.g. `docs/tickets/01-scaffold.md`, `docs/tickets/02-config-and-models.md`, etc. Each ticket contains: goal, the test file(s) to write first (where TDD applies), the implementation file(s), and its slice of this plan's detail (schema fields, formula, filename convention, etc.) so it's actionable standalone without needing to re-read this whole plan. These are committed to the repo alongside the code they describe.

## Verification

- After each TDD phase: `uv run pytest` (fast unit suite, offline, must stay green).
- After Phase 3 (provider factory) with real Ollama running locally: `uv run pytest -m integration` for extraction/verdicts against `llama3.2:latest`.
- After Phase 10: manual end-to-end run — `uv run streamlit run src/fitscorer/app.py`, load `data/profile.example.json`, paste a real job posting, verify Fit Score/Verdicts/Repositioning render, Session History accumulates across multiple pastes, Save Report writes a correctly-named file under `reports/`.
- Before calling v1 done: switch `LLM_PROVIDER=gemini` in `.env` (with a real `GOOGLE_API_KEY`) and repeat the smoke test, confirming no code outside `config.py`/`llm/provider.py` needed to change.
