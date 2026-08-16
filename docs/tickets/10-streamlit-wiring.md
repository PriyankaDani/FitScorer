# 10 — Streamlit Wiring

## Goal

Wire the full pipeline (phases 04→07) plus Session History and Report saving into a Streamlit GUI (ADR 0003). No unit tests for this phase — Playwright/GUI acceptance testing is explicitly deferred until the user confirms UI stability (ADR 0003, CLAUDE.md Testing section); that's the user's call to make, not to be declared here.

## Implementation file

`src/fitscorer/app.py` — Streamlit entrypoint:

- Sidebar: Profile load (from `data/profile.json` or upload) into `st.session_state`.
- Chat model cached via `st.cache_resource`, built once via `get_chat_model(settings)` (phase 03) — `app.py` never imports a provider SDK directly.
- JobPosting paste box + "Score" button, chaining: `extract_job_posting` (04) → `generate_skill_verdicts` (05) → `compute_fit_score` (06) → `generate_repositioning_suggestion` (07).
- Results view: Fit Score, Skill Verdicts split into Required/Preferred sections, Repositioning Suggestion text.
- Session History table (backed by `session.py`, phase 09), accumulating across multiple JobPosting pastes in the same Session.
- Per-run "Save Report" button that calls `save_report` (phase 08) **only on click** — never automatically.

## Verification (manual — no automated GUI tests this phase)

- `uv run streamlit run src/fitscorer/app.py` end-to-end against Ollama with `data/profile.example.json`: load Profile, paste a real job posting, verify Fit Score/Verdicts/Repositioning render, Session History accumulates across multiple pastes, Save Report writes a correctly-named file under `reports/`.
- Before calling v1 done: switch `LLM_PROVIDER=gemini` in `.env` (with a real `GOOGLE_API_KEY`) and repeat the smoke test, confirming no code outside `config.py`/`llm/provider.py` needed to change.

## Status

✅ Done — Ollama smoke test passed manually (Profile load, JobPosting scoring, Session History accumulation, Save Report all verified). The Gemini switch-over smoke test is still outstanding and tracked separately as a pre-v1 gate, not part of this ticket's completion.
