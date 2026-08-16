# 05 — Skill Verdicts (incl. Preferred)

## Goal

Produce a per-skill `SkillVerdict` for every Required **and** Preferred Skill on a JobPosting, judged against the whole Profile as evidence (ADR 0001) — not just the skills section, so an Experience Entry or Education Entry can serve as evidence even when the skill isn't listed verbatim.

This phase is a deliberate, sign-off'd extension beyond CONTEXT.md's original Skill Verdict definition (Required Skills only) — see the new ADR below.

## Test file first (TDD)

`tests/unit/test_verdicts.py`, using the same hand-written fake chat model pattern as extraction. Covers:

- Verdict count returned == `len(required_skills) + len(preferred_skills)`.
- Each verdict's `skill_type` correctly tagged `"required"` vs `"preferred"`.
- Malformed LLM output case (mirrors extraction's error handling).

## Implementation file

`src/fitscorer/verdicts.py` — `generate_skill_verdicts(profile: Profile, job_posting: JobPosting, chat_model) -> list[SkillVerdict]`.

- Passes the **whole** Profile as evidence per ADR 0001 (not just `skills`).
- Calls the LLM once (or per-skill — implementer's choice) via `chat_model.with_structured_output(...)`, never lets the LLM compute a score, only verdicts (ADR 0001).

## Also in this phase

- `docs/adr/0005-skill-verdicts-cover-preferred-skills-too.md` — records this as a deliberate extension. Rejected alternative: flat keyword-based bonus for Preferred Skills — rejected for reintroducing the same semantic-matching gap ADR 0001 rejected pure keyword matching for.
- Update CONTEXT.md's **Skill Verdict** entry with one sentence noting it also covers Preferred Skills, weighted lower (weighting itself lives in `scoring.py`, phase 06).

## Verification

- `uv run pytest` — unit suite green, offline. ✅ Done — `tests/unit/test_verdicts.py` (9 tests: verdict count == required+preferred, correct `skill_type` tagging, malformed/missing-key/wrong-shaped/None output, LLM-call-failure wrapping, whole-Profile-as-evidence, happy path) passes alongside the full unit suite (60 passed).
- `uv run pytest -m integration` (manual, Ollama running) — `tests/integration/test_verdicts_ollama.py` against real `llama3.2:latest`. ⬜ Not done — no integration test file exists yet.

## Status

**Test file, implementation, ADR, and CONTEXT.md update all complete.** `tests/unit/test_verdicts.py` and `src/fitscorer/verdicts.py` are written and green; `docs/adr/0005-skill-verdicts-cover-preferred-skills-too.md` records the Preferred-Skills extension; CONTEXT.md's Skill Verdict entry now links to it.

`generate_skill_verdicts` uses a single LLM call with an internal `_SkillVerdictsResult` wrapper model (`verdicts: list[SkillVerdict]`) passed to `with_structured_output`, since LangChain's structured-output methods require one schema object per call rather than a bare `list[...]`. The prompt enumerates Required and Preferred Skill names explicitly (rather than re-deriving them from a dumped `JobPosting`) and states the exact verdict count expected, to reduce miscounted/hallucinated output.

Remaining open item: the real-Ollama integration test above — left open per plan, to be picked up later alongside the provider factory's and extraction's own deferred integration items ([03](03-llm-provider-factory.md), [04](04-extraction.md)).
