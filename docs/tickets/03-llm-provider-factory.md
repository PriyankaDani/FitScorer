# 03 — LLM Provider Factory

## Goal

A single seam through which the app selects Ollama or Gemini, so no other module ever imports a provider SDK directly — provider-agnosticism in scoring/aggregation becomes structurally enforced, not just a convention.

## Test file first (TDD)

`tests/unit/test_provider.py` — asserts `get_chat_model(settings)` picks the right constructor for `settings.llm_provider == "ollama"` vs `"gemini"`, via monkeypatched constructors. No real network calls in unit tests.

## Implementation file

`src/fitscorer/llm/provider.py` — `get_chat_model(settings) -> BaseChatModel` factory. **The only file in the codebase that imports `langchain_ollama` or `langchain_google_genai`.**

- Ollama branch: model name from `settings.ollama_model`, base URL from `settings.ollama_base_url`.
- Gemini branch: model name from `settings.gemini_model`, API key from `settings.google_api_key`.
- Model names always come from `config.py`/`.env` — never hardcoded here.

## Verification

- `uv run pytest` — unit suite green, offline. ✅ Done — `tests/unit/test_provider.py` (4 tests: ollama, ollama default provider, gemini, invalid provider) passes alongside the full unit suite (37 passed).
- With real Ollama running locally: `uv run pytest -m integration` exercises `get_chat_model` against `llama3.2:latest` (paired with extraction/verdicts integration tests from later phases). ⬜ Not done — no integration test file exists yet, and this item is meant to run paired with extraction/verdicts integration tests from later phases (04+), which aren't built.

## Status

**Test file and implementation complete.** `tests/unit/test_provider.py` and `src/fitscorer/llm/provider.py` are written and green.

Note: importing `langchain_google_genai` (via `provider.py`) surfaces one `DeprecationWarning` from the `google-genai` package itself (`_UnionGenericAlias` deprecated, slated for removal in Python 3.17) — it's upstream, not from this repo's code, and doesn't fail the suite. No action needed; revisit only if `google-genai` hasn't fixed it by the time Python 3.17 ships.

Remaining open item: the real-Ollama integration verification step above — deferred until extraction/verdicts (phases 4+) exist, per the plan's suggestion to pair it with those.
