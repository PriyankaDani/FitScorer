# 07 — Repositioning Suggestion

## Goal

Generate narrative advice for how the user could present their existing Profile to better fit a JobPosting's gaps — narrates a gap already determined by phases 05/06, doesn't determine it itself.

## Test file first (TDD)

`tests/unit/test_repositioning.py`, using the same fake-chat-model pattern. Covers:

- The prompt sent to the fake chat model includes the already-computed `fit_score.value`.
- Return type (`RepositioningSuggestion`) carries no numeric field — asserted structurally (only a `text` attribute), reinforcing that repositioning narrates, it doesn't re-score.

## Implementation file

`src/fitscorer/repositioning.py` — `generate_repositioning_suggestion(verdicts: list[SkillVerdict], fit_score: FitScore, chat_model) -> RepositioningSuggestion`.

- Takes the already-computed `SkillVerdict`s and `FitScore` as input — never recomputes or second-guesses the score.
- Calls `chat_model.with_structured_output(RepositioningSuggestion)` (or equivalent), prompt includes `fit_score.value` plus verdict gaps.

## Also in this phase

Beyond the ticket's original scope, `generate_repositioning_suggestion` is gated and tiered by `fit_score.value`, deterministically (not by LLM judgment) — see `docs/adr/0006-tiered-repositioning-suggestion-thresholds.md`:

- **< 60**: no LLM call — returns a fixed "too low for a meaningful suggestion" text.
- **60–84.9**: prompt asks for key arguments and concrete advice ("substantial ground" tier).
- **≥ 85**: prompt narrows to only missing Required Skills ("near-complete" tier) — no manufactured broader advice.

## Verification

`uv run pytest` — unit suite green, offline. ✅ Done — `tests/unit/test_repositioning.py` (13 tests: prompt includes `fit_score.value` and verdict gaps, return type structurally carries only `text`, malformed/missing-key/wrong-shaped/None output, LLM-call-failure wrapping, happy path, sub-60 skip with zero LLM calls, at-threshold-60 still calls the LLM, mid-tier and high-tier prompt framing, 85.0 boundary belongs to the high tier) passes alongside the full unit suite (73 passed).

## Status

**Test file, implementation, and ADR all complete.** `tests/unit/test_repositioning.py` and `src/fitscorer/repositioning.py` are written and green; `docs/adr/0006-tiered-repositioning-suggestion-thresholds.md` records the threshold-gating and tiering decision, including the rejected alternative of letting the LLM decide for itself whether to suggest anything.

No open items for this phase — the project plan doesn't require a real-Ollama integration test for repositioning (unlike extraction/verdicts in phase 3's verification step).
