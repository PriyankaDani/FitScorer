# 04 — Extraction

## Goal

Turn a JobPosting's pasted `raw_text` into structured data (`role_title`, `required_skills`, `preferred_skills`, `seniority_level`) via the LLM, with a baseline injection defense since `raw_text` is untrusted external text (ADR 0004's input-source seam).

## Test file first (TDD)

`tests/unit/test_extraction.py`, using a small hand-written fake chat model implementing `.with_structured_output(schema).invoke(...)` (not deep-patched LangChain mocks, so tests stay fast/offline/resilient to unrelated LangChain internals). Covers:

- Empty/whitespace `raw_text` is rejected **before** any LLM call.
- Malformed/incomplete structured output from the LLM raises a clear `ExtractionError`.
- Happy path: fake model returns a valid `JobPosting`-shaped payload, function returns a `JobPosting`.

## Implementation file

`src/fitscorer/extraction.py` — `extract_job_posting(raw_text: str, chat_model) -> JobPosting`.

- Prompt treats `raw_text` strictly as **data**, never as instructions — the baseline defense against prompt injection from scraped/pasted job posting text.
- Uses `chat_model.with_structured_output(...)` against the `JobPosting` schema (or an extraction-specific schema mapped to it).
- Raises `ExtractionError` (new exception type in this module) on malformed output rather than propagating a raw parsing exception.

## Verification

- `uv run pytest` — unit suite green, offline (fake chat model only). ✅ Done — `tests/unit/test_extraction.py` (14 tests: empty/whitespace rejection, malformed/wrong-shaped/None output, LLM-call-failure wrapping, happy path with dict and pre-parsed output, and prompt-injection baseline defense) passes alongside the full unit suite (51 passed).
- `uv run pytest -m integration` (manual, Ollama running) — `tests/integration/test_extraction_ollama.py` against real `llama3.2:latest`. ⬜ Not done — no integration test file exists yet.

## Status

**Test file and implementation complete.** `tests/unit/test_extraction.py` and `src/fitscorer/extraction.py` are written and green.

Remaining open item: the real-Ollama integration test above — left open per plan, to be picked up later alongside the provider factory's own deferred integration item ([03](03-llm-provider-factory.md)).
