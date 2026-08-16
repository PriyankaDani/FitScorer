# 09 — Session / Session History

## Goal

In-memory record of every JobPosting scored during the current Session, in insertion order — plain Python, zero Streamlit imports, so it stays behind the interface seam (ADR 0004) and is independently testable.

## Test file first (TDD)

`tests/unit/test_session.py` — `Session.add_run(...)` appends a `SessionEntry` with a timestamp; insertion order is preserved across multiple `add_run` calls.

## Implementation file

`src/fitscorer/session.py`:

- `SessionEntry` — holds one scored JobPosting's result (JobPosting, verdicts, FitScore, RepositioningSuggestion, timestamp).
- `Session` — `add_run(...)` appends a `SessionEntry`; exposes the ordered history for display.

No Streamlit imports in this file — `app.py` (phase 10) owns `st.session_state` wiring; `session.py` only defines the plain data structure ADR 0004's interface seam requires.

## Verification

`uv run pytest` — unit suite green.

## Status

✅ Done
