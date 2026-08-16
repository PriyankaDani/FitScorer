# FitScorer

A personal tool that compares a job posting against your own career profile and reports how well you fit it, where the gaps are, and how to reposition around them.

You paste a job posting, load your Profile once, and get back a Fit Score, per-skill Verdicts (match / partial / missing), and a narrative Repositioning Suggestion — automating the gap analysis that's otherwise done by hand. See [CONTEXT.md](CONTEXT.md) for the project's vocabulary (Profile, JobPosting, Skill Verdict, Fit Score, Repositioning Suggestion, Session, Session History, Report) and [docs/adr/](docs/adr/) for the architectural decisions behind it.

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

## Capabilities & limitations

**Current status: scaffold only.** The project skeleton, dependencies, and config are in place; no pipeline code (extraction, Skill Verdicts, scoring, reporting, or the Streamlit UI) has been written yet. Nothing is runnable end-to-end at this point.

Once built, by design:

- The Fit Score is **always computed deterministically** from LLM-produced Skill Verdicts — an LLM never outputs the score directly ([ADR 0001](docs/adr/0001-hybrid-scoring-llm-verdicts-deterministic-aggregation.md)).
- The Profile schema **excludes employer and institute names at the type level** — there's no field to redact at runtime, so no unscrubbed CV or PII is ever sent to an LLM ([ADR 0002](docs/adr/0002-pii-designed-out-at-profile-schema.md)).
- The GUI is single-user and session-based (Streamlit); Session History lives only in memory for the current session and is lost on close unless a Report is explicitly saved ([ADR 0003](docs/adr/0003-streamlit-for-single-user-session-based-gui.md)).
- JobPosting input, Profile ingestion, and the interface are three swappable seams around a scoring/aggregation core that depends only on Profile and JobPosting as data ([ADR 0004](docs/adr/0004-three-swappable-input-and-ingestion-seams.md)).
- No web-scraper input source, no freeform-CV auto-extraction, and no multi-user deployment — each is a gated future extension (see below); none of their gates are currently satisfied.
- No GUI acceptance testing (Playwright) — deferred until the Streamlit UI has stabilized.

## Planned

Build phases (TDD-first for extraction, Skill Verdict aggregation, Fit Score, and Report generation):

1. ~~Scaffold~~ — done.
2. Config & models (`Profile`, `JobPosting`, `SkillVerdict`, `FitScore`, etc., with PII-guard regression tests).
3. LLM provider factory (`get_chat_model`, Ollama/Gemini switch).
4. JobPosting extraction from pasted text.
5. Skill Verdicts (covering Required and Preferred Skills).
6. Deterministic Fit Score aggregation.
7. Repositioning Suggestion generation.
8. Report generation & saving.
9. Session / Session History.
10. Streamlit wiring (end-to-end UI).

Gated future extensions (see [CLAUDE.md](CLAUDE.md) for the gate each requires before work can start):

- **Web-scraper JobPosting input source** — gated on re-verifying the injection-defense stance against scraped HTML, not just pasted text.
- **Freeform CV → structured Profile auto-extraction** — gated on a new ADR guaranteeing no PII reaches any LLM during extraction from raw CV text.
- **Multi-user web deployment** — gated on a new ADR for per-user Profile storage/isolation and auth.
- **Playwright GUI acceptance testing** — gated on the user confirming the Streamlit UI has stabilized.
