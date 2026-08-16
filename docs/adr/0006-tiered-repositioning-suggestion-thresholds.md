# Repositioning Suggestion is gated and tiered by Fit Score

A Repositioning Suggestion narrates the gap already computed by the Fit Score and Skill Verdicts ([0001](0001-hybrid-scoring-llm-verdicts-deterministic-aggregation.md)) — it never re-scores. Left unconstrained, the LLM would write the same style of narrative advice regardless of how large or small the gap actually is, which is both wasteful (an LLM call for a Profile that already matches almost everything) and misleading (forced "advice" for a Profile that fundamentally doesn't fit, where the honest answer is that presentation isn't the problem). We decided to gate and tier `generate_repositioning_suggestion` deterministically by `fit_score.value`, using fixed thresholds rather than letting the LLM decide when advice is warranted:

- **< 60**: no repositioning is attempted. The function returns early with a fixed `NO_SUGGESTION_TEXT` and never calls the chat model — the gap is too large for presentation-level advice to be honest or useful.
- **60–84.9**: the "substantial ground" tier. The prompt instructs the LLM to make key arguments for why existing Profile evidence fits and give concrete advice on reframing it against the gaps.
- **≥ 85**: the "near-complete" tier. The prompt narrows the LLM to addressing only missing Required Skills among the gaps, explicitly instructing it not to manufacture broader repositioning advice where the fit is already strong.

The threshold check and tier selection both happen in `repositioning.py` before any prompt is built, so the LLM never has agency over whether repositioning is skipped — only the wording within a tier the deterministic code already picked.

## Considered Options

- **Let the LLM decide whether to suggest anything** (single prompt, instruct the LLM to decline when it judges the gap unfixable by repositioning) — rejected: reintroduces exactly the non-determinism [0001](0001-hybrid-scoring-llm-verdicts-deterministic-aggregation.md) rejected for the Fit Score itself. Whether repositioning is attempted at all should be reproducible and testable without mocking LLM judgment calls.
- **Single prompt for all Fit Score ranges** — rejected: produces the same verbose "make the case" narrative for a Profile that's already a 95% fit, which reads as padding rather than useful advice, and burns an LLM call below 60 where there's no honest case to make.
- **More than three tiers / a continuous scoring-based prompt** — rejected as premature complexity: three tiers (skip / substantial / narrow) map directly to the three qualitatively different actions a user takes (don't bother, actively reposition, patch remaining required gaps), and finer gradations aren't grounded in any evidence they'd change the advice's usefulness.

## Consequences

`REPOSITIONING_MIN_SCORE` (60.0) and `REPOSITIONING_HIGH_SCORE` (85.0) are the two threshold constants in `repositioning.py`; changing tier boundaries means changing these constants and their tests, not the LLM prompt's judgment. `test_repositioning.py` asserts the skip case makes zero calls to `chat_model.with_structured_output(...).invoke(...)`, and asserts tier-specific prompt content for the mid and high tiers — the boundary at exactly 85.0 belongs to the high tier.
