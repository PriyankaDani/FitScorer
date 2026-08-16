# 01 — Scaffold

**Status:** Done

## Goal

Create the installable `fitscorer` project skeleton — no pipeline code — so later phases have a package, dependencies, and test config to build against.

## Steps

- `uv init --package .` (`src/` layout — keeps `fitscorer` separate from `docs/`, `data/`, `reports/`).
- `uv add pydantic pydantic-settings python-dotenv langchain langchain-core langchain-ollama langchain-google-genai streamlit`
- `uv add --dev pytest pytest-mock`
- `.gitignore`:
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
  `data/profile.json` (the user's real Profile) is gitignored by name — only the fictitious `data/profile.example.json` is committed, belt-and-suspenders alongside the schema-level PII exclusion (ADR 0002).
- `.env.example` — placeholders for `LLM_PROVIDER`, `OLLAMA_MODEL`, `OLLAMA_BASE_URL`, `GEMINI_MODEL`, `GOOGLE_API_KEY`.
- `reports/.gitkeep` (dir tracked; generated `.md` files gitignored).
- `data/profile.example.json` — hand-written fictitious sample Profile, shaped like the schema in ticket 02, loosely structured like `jane_doe_profile.md` but invented content. The real `jane_doe_profile.md` is never ingested by the app.
- pytest config in `pyproject.toml`:
  ```toml
  [tool.pytest.ini_options]
  testpaths = ["tests"]
  markers = ["integration: hits real Ollama; run manually with `uv run pytest -m integration`"]
  addopts = "-m 'not integration'"
  ```
- `git init` + initial commit (scaffold only, no pipeline code).

## Implementation files

`pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, `.env.example`, `reports/.gitkeep`, `data/profile.example.json`

## Verification

`uv run pytest` collects zero tests but exits cleanly (no pipeline code yet).
