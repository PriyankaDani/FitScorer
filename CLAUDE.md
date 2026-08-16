# FitScorer

A personal tool that compares a job posting against the user's own career profile and reports fit, gaps, and repositioning advice.

## Stack

- **Python**, managed with **uv** — use `uv add`/`uv sync`/`uv run`, not pip or poetry directly.
- **LangChain** for the LLM calls (Skill Verdicts, Repositioning Suggestion) — see [0001](docs/adr/0001-hybrid-scoring-llm-verdicts-deterministic-aggregation.md) for what may and may not go through the LLM.
- **Streamlit** for the GUI, using `st.session_state` for the Session/Session History — see [0003](docs/adr/0003-streamlit-for-single-user-session-based-gui.md).
- **pytest** for the test suite.
- Two LLM providers, selected via a config/env-var flag (e.g. `LLM_PROVIDER=ollama|gemini`) — app code stays provider-agnostic, never branching on provider inside scoring/aggregation logic. **Ollama** (local, `llama3.2:latest`) for iterative dev; **Gemini API** for final testing — both are required, not a matter of preference. Model names live in config, never hardcoded in source.

## Testing & TDD

- TDD is mandatory for the core pipeline (extraction, Skill Verdict aggregation, Fit Score, Report generation): write the component test before the implementation code, not after.
- Mock/stub the LLM at the extraction and Skill Verdict boundaries for component tests, so the suite stays fast and deterministic. A separate, thinner integration-test layer runs against real Ollama — run manually, not part of the default test loop.
- If a test fails, do not unilaterally decide whether it's a bug or the test is wrong — that call must be signed off by the user before changing either the test or the implementation.
- Playwright/GUI acceptance testing is deferred past v1 ([0003](docs/adr/0003-streamlit-for-single-user-session-based-gui.md)) — don't add it unless asked.

## Git commits

- Commit only when explicitly asked; push only when explicitly asked. After a commit, offer to push, then wait for confirmation.
- Default to committing step-by-step: stage only the files modified or relevant to the step just completed. If the user doesn't name which files, ask which files to commit before staging anything.
- Commit messages use `PREFIX: description`. Prefixes in use in this repo: `FEAT` (new implementation code), `TEST` (test files), `SETUP` (scaffolding/project setup), `DOC` (documentation, including ticket files under `docs/tickets/`).
- Determine the prefix from the staged changes yourself, then state the chosen prefix and full commit message and wait for the user's confirmation before committing. If no single prefix clearly fits, ask instead of guessing.

## Read first

- **[CONTEXT.md](CONTEXT.md)** — the project's vocabulary (Profile, JobPosting, Skill Verdict, Fit Score, Repositioning Suggestion, Session, Session History, Report). Use these terms exactly as defined there; don't substitute synonyms like "resume", "match score", or "recommendation" — CONTEXT.md lists what each term displaces and why.
- **[docs/adr/](docs/adr/)** — architectural decisions already made. Read the relevant ADR before touching the area it covers, and check whether a new decision contradicts an existing one before making it:
  - [0001](docs/adr/0001-hybrid-scoring-llm-verdicts-deterministic-aggregation.md) — the LLM produces per-skill Verdicts only; the Fit Score is always aggregated by deterministic code, never by an LLM directly.
  - [0002](docs/adr/0002-pii-designed-out-at-profile-schema.md) — PII (employer/institute names) is excluded at the Profile schema level, not filtered at runtime. Never add employer/institute name fields to the Profile schema, and never build runtime PII redaction as a substitute.
  - [0003](docs/adr/0003-streamlit-for-single-user-session-based-gui.md) — Streamlit is the v1 GUI, chosen so the same codebase can later become a shared multi-user web app.
  - [0004](docs/adr/0004-three-swappable-input-and-ingestion-seams.md) — three deliberate module boundaries: JobPosting input source, Profile ingestion, and interface. The scoring/aggregation core must depend only on Profile and JobPosting as data, never on how either was produced.

## Future Extensions

Each item below is a planned, not-yet-built extension with a **gate**: a hard prerequisite, not a suggestion. When asked to implement one of these, check its gate first. An unmet gate is a hard block — refuse to implement the extension, state which gate is unmet, and propose closing that gate as the next step. Do not implement partially or work around the gate. Only a satisfied gate is a green light. If current work closes a gate or otherwise sets one up, mention the now-unblocked extension as a possible next step.

- **Web-scraper JobPosting input source** (fills the input-source seam from [0004](docs/adr/0004-three-swappable-input-and-ingestion-seams.md)). Gate: re-verify the injection-defense stance ([0001](docs/adr/0001-hybrid-scoring-llm-verdicts-deterministic-aggregation.md)) against scraped HTML/markup, not just pasted plain text — scraped pages carry more untrusted structure than a paste.
- **Freeform CV → structured Profile auto-extraction** (fills the ingestion seam from [0004](docs/adr/0004-three-swappable-input-and-ingestion-seams.md); deferred by [0002](docs/adr/0002-pii-designed-out-at-profile-schema.md)). Gate: a new ADR, signed off before implementation starts, deciding how this module guarantees no PII reaches any LLM while extracting from raw, unscrubbed CV text — [0002](docs/adr/0002-pii-designed-out-at-profile-schema.md)'s schema-level guarantee does not automatically cover this.
- **Multi-user web deployment** (the reason [0003](docs/adr/0003-streamlit-for-single-user-session-based-gui.md) picked Streamlit). Gate: a new ADR deciding per-user Profile storage/isolation and auth — today's Profile is a single local file with no multi-user concept.
- **Playwright GUI acceptance testing** (deferred by [0003](docs/adr/0003-streamlit-for-single-user-session-based-gui.md) and the Testing section above). Gate: the user confirms the Streamlit UI has stabilized — this is the user's call, not Claude's to declare.

## Rules

- Never send a raw/un-scrubbed CV or any employer/institute name to an LLM call ([0002](docs/adr/0002-pii-designed-out-at-profile-schema.md)).
- Never have an LLM compute the Fit Score directly — only Skill Verdicts feed the deterministic aggregator ([0001](docs/adr/0001-hybrid-scoring-llm-verdicts-deterministic-aggregation.md)).
- Keep the scoring/aggregation core free of input-source, ingestion, or interface specifics — those live behind the seams in [0004](docs/adr/0004-three-swappable-input-and-ingestion-seams.md).
- A Report is only written on explicit user action (the Save button), never automatically — save to `reports/`, filenamed `<role-title>_<company-if-extracted>_<timestamp>.md`.
- When you make a decision worth an ADR (a rejected alternative, a non-obvious tradeoff), add a new numbered file to `docs/adr/`, following the existing files' format — don't edit past ADRs' decisions in place.
- When you introduce or rename a domain term, update CONTEXT.md in the same change.
