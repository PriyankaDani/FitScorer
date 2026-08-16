# FitScorer

A personal tool that compares a job posting against your own career profile and reports how well you fit it, where the gaps are, and how to reposition around them.

You paste a job posting, load your Profile once, and get back a Fit Score, per-skill Verdicts (match / partial / missing), and a narrative Repositioning Suggestion — automating the gap analysis that's otherwise done by hand. See [CONTEXT.md](CONTEXT.md) for the project's vocabulary (Profile, JobPosting, Skill Verdict, Fit Score, Repositioning Suggestion, Session, Session History, Report) and [docs/adr/](docs/adr/) for the architectural decisions behind it.

## Status: v1 complete

The full pipeline is built and wired into the Streamlit GUI: Profile load → JobPosting extraction → Skill Verdicts → Fit Score → Repositioning Suggestion → Session History → optional Report save. See `docs/tickets/` for the phase-by-phase build history.

- **Manual smoke tests passed** end-to-end against both providers — `LLM_PROVIDER=ollama` (`llama3.2:latest`) and `LLM_PROVIDER=gemini` — confirming no code outside `config.py` / `llm/provider.py` needed to change between them.
- **Integration tests were not written for v1.** `tests/integration/` is scaffolded (pytest marker, Ollama-reachability skip) but has no test files yet — deferred to v2. The unit suite (LLM calls mocked with a fake chat model) is the sole automated coverage today.
- **Playwright GUI acceptance testing** remains deferred until the Streamlit UI has stabilized further (a user call, not a technical blocker) — see [ADR 0003](docs/adr/0003-streamlit-for-single-user-session-based-gui.md).

## Running it

```
uv sync
cp .env.example .env   # fill in GOOGLE_API_KEY if using LLM_PROVIDER=gemini
uv run streamlit run src/fitscorer/app.py
```

Load a Profile from the sidebar (`data/profile.example.json` for a quick try, or your own `data/profile.json`), paste a JobPosting, click Score. Reports are only written to `reports/` when you click "Save Report" — never automatically.

## Testing

```
uv run pytest              # fast unit suite, offline, LLM calls mocked
uv run pytest -m integration  # real Ollama required; skipped automatically if unreachable
```

TDD was mandatory for the core pipeline (extraction, Skill Verdict aggregation, Fit Score, Report generation) — see `docs/tickets/` for each phase's test-first history.

## Dependencies

Managed with [uv](https://docs.astral.sh/uv/); Python >=3.14.

- **[LangChain](https://python.langchain.com/)** (`langchain`, `langchain-core`) — LLM calls for extraction and Skill Verdicts.
- **`langchain-ollama`** — local provider for iterative dev (`llama3.2:latest` via [Ollama](https://ollama.com/)).
- **`langchain-google-genai`** — Gemini API provider for final testing.
- **[Streamlit](https://streamlit.io/)** — single-user, session-based GUI.
- **[Pydantic](https://docs.pydantic.dev/) / `pydantic-settings`** — data models and typed, validated config (`LLM_PROVIDER`, model names, API keys) via `.env`.
- **`python-dotenv`** — `.env` loading.

Dev-only: **pytest**, **pytest-mock**, **httpx** (used to probe Ollama reachability in integration tests).

Install and run everything through `uv` (`uv sync`, `uv add`, `uv run ...`) — not `pip` or `poetry` directly.

## Design, by decision

- The Fit Score is **always computed deterministically** from LLM-produced Skill Verdicts — an LLM never outputs the score directly ([ADR 0001](docs/adr/0001-hybrid-scoring-llm-verdicts-deterministic-aggregation.md)). Skill Verdicts also cover Preferred Skills, weighted lower than Required ([ADR 0005](docs/adr/0005-skill-verdicts-cover-preferred-skills-too.md)).
- The Profile schema **excludes employer and institute names at the type level** — there's no field to redact at runtime, so no unscrubbed CV or PII is ever sent to an LLM ([ADR 0002](docs/adr/0002-pii-designed-out-at-profile-schema.md)).
- The GUI is single-user and session-based (Streamlit); Session History lives only in memory for the current session and is lost on close unless a Report is explicitly saved ([ADR 0003](docs/adr/0003-streamlit-for-single-user-session-based-gui.md)).
- JobPosting input, Profile ingestion, and the interface are three swappable seams around a scoring/aggregation core that depends only on Profile and JobPosting as data ([ADR 0004](docs/adr/0004-three-swappable-input-and-ingestion-seams.md)).
- Extraction, Skill Verdict, and Repositioning prompts all standardize on English output, regardless of the JobPosting's source language — a JobPosting pasted in German (or any other language) still returns English Verdicts and Repositioning text.
- Since Skill Verdicts are LLM-judged, Fit Scores can legitimately differ between providers (e.g. Ollama vs Gemini) for the same JobPosting and Profile — this is expected model-to-model variance in subjective judgment, not a scoring bug; only the aggregation math is deterministic and provider-independent.
- No web-scraper input source, no freeform-CV auto-extraction, and no multi-user deployment — each is a gated future extension (see below); none of their gates are currently satisfied.

## Gated future extensions

See [CLAUDE.md](CLAUDE.md) for the gate each requires before work can start:

- **Web-scraper JobPosting input source** — gated on re-verifying the injection-defense stance against scraped HTML, not just pasted text.
- **Freeform CV → structured Profile auto-extraction** — gated on a new ADR guaranteeing no PII reaches any LLM during extraction from raw CV text.
- **Multi-user web deployment** — gated on a new ADR for per-user Profile storage/isolation and auth.
- **Playwright GUI acceptance testing** — gated on the user confirming the Streamlit UI has stabilized.
- **Integration test suite** (v2) — write `tests/integration/test_extraction_ollama.py` and `test_verdicts_ollama.py` against real Ollama; no formal gate, just deferred out of v1 scope.
