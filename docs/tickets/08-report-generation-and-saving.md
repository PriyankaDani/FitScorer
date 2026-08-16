# 08 — Report Generation & Saving

## Goal

Persist one scored JobPosting's full result (Fit Score, Skill Verdicts, Repositioning Suggestion) to a Markdown file — only on explicit user action (the Save button in phase 10), never automatically.

## Test file first (TDD)

`tests/unit/test_report.py`, written first, covers:

- `build_report_markdown(...)` content checks — Fit Score, Skill Verdicts (Required/Preferred), Repositioning Suggestion text all present in the output.
- `save_report(...)` filename convention: `<role-title>_<company>_<timestamp>.md`, slugified.
- `save_report` isolated via `tmp_path` (no writes to the real `reports/` dir in unit tests).
- `company is None` case produces no dangling separator in the filename (e.g. not `role-title__timestamp.md`).

## Implementation file

`src/fitscorer/report.py`:

- `build_report_markdown(job_posting, verdicts, fit_score, repositioning) -> str`
- `save_report(markdown: str, job_posting: JobPosting, *, directory: Path = Path("reports")) -> Path` — real save path defaults to `reports/`, overridable (used by tests via `tmp_path`).

Filename: `<role-title>_<company-if-extracted>_<timestamp>.md`. A Report is only ever written on explicit user action (the Save button in `app.py`), never automatically — this file only builds/writes when called, it doesn't decide when to call itself.

## Verification

`uv run pytest` — unit suite green, no writes outside `tmp_path`. ✅ Done — `tests/unit/test_report.py` (7 tests: `build_report_markdown` content checks for Fit Score, Required/Preferred Skill Verdicts, and Repositioning Suggestion text; `save_report` filename convention including timestamp; write confined to the given `directory`; `company is None` produces no dangling separator; default directory resolves to `reports/`) passes alongside the full unit suite (80 passed).

## Status

**Test file and implementation both complete.** `tests/unit/test_report.py` and `src/fitscorer/report.py` are written and green. No slugify dependency was added — `report.py` implements a small internal `_slugify` helper (lowercase, non-alphanumeric runs collapsed to `-`, trimmed) since no such library was already in `pyproject.toml`; not ADR-worthy on its own, no rejected alternative or binding tradeoff involved.

No open items for this phase.
