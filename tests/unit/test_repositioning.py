import pytest

from fitscorer.models import FitScore, RepositioningSuggestion, SkillVerdict
from fitscorer.repositioning import RepositioningError, generate_repositioning_suggestion


class FakeStructuredOutput:
    """Stands in for the object returned by chat_model.with_structured_output(schema)."""

    def __init__(self, return_value=None, raise_exc=None):
        self.return_value = return_value
        self.raise_exc = raise_exc
        self.invoke_calls = []

    def invoke(self, prompt):
        self.invoke_calls.append(prompt)
        if self.raise_exc is not None:
            raise self.raise_exc
        return self.return_value


class FakeChatModel:
    """Small hand-written fake for chat_model.with_structured_output(schema).invoke(...)."""

    def __init__(self, return_value=None, raise_exc=None):
        self.structured_output = FakeStructuredOutput(return_value, raise_exc)
        self.schemas_requested = []

    def with_structured_output(self, schema):
        self.schemas_requested.append(schema)
        return self.structured_output


@pytest.fixture
def sample_verdicts() -> list[SkillVerdict]:
    return [
        SkillVerdict(
            skill_name="Python",
            skill_type="required",
            verdict="match",
            rationale="matches profile evidence",
        ),
        SkillVerdict(
            skill_name="Kubernetes",
            skill_type="preferred",
            verdict="missing",
            rationale="no supporting evidence in Profile",
        ),
    ]


@pytest.fixture
def sample_fit_score() -> FitScore:
    return FitScore(value=72.5, required_coverage=100.0, preferred_coverage=0.0)


# prompt includes the already-computed fit_score.value
def test_prompt_includes_fit_score_value(sample_verdicts, sample_fit_score):
    chat_model = FakeChatModel(return_value={"text": "Lean on adjacent evidence for Kubernetes."})

    generate_repositioning_suggestion(sample_verdicts, sample_fit_score, chat_model)

    prompt_sent = str(chat_model.structured_output.invoke_calls[0])
    assert str(sample_fit_score.value) in prompt_sent


# prompt includes the verdict gaps (missing/partial), narrating what phases 05/06 already found
def test_prompt_includes_verdict_gaps(sample_verdicts, sample_fit_score):
    chat_model = FakeChatModel(return_value={"text": "Lean on adjacent evidence for Kubernetes."})

    generate_repositioning_suggestion(sample_verdicts, sample_fit_score, chat_model)

    prompt_sent = str(chat_model.structured_output.invoke_calls[0])
    assert "Kubernetes" in prompt_sent


# return type carries no numeric field - structurally, only a `text` attribute
def test_return_type_has_only_text_attribute(sample_verdicts, sample_fit_score):
    chat_model = FakeChatModel(return_value={"text": "Lean on adjacent evidence for Kubernetes."})

    result = generate_repositioning_suggestion(sample_verdicts, sample_fit_score, chat_model)

    assert isinstance(result, RepositioningSuggestion)
    assert set(RepositioningSuggestion.model_fields.keys()) == {"text"}
    assert result.text == "Lean on adjacent evidence for Kubernetes."


# malformed LLM output cases mirror extraction/verdicts error handling
def test_missing_text_key_raises_repositioning_error(sample_verdicts, sample_fit_score):
    chat_model = FakeChatModel(return_value={})

    with pytest.raises(RepositioningError):
        generate_repositioning_suggestion(sample_verdicts, sample_fit_score, chat_model)


def test_wrong_shaped_output_raises_repositioning_error(sample_verdicts, sample_fit_score):
    chat_model = FakeChatModel(return_value="not a structured payload at all")

    with pytest.raises(RepositioningError):
        generate_repositioning_suggestion(sample_verdicts, sample_fit_score, chat_model)


def test_none_output_raises_repositioning_error(sample_verdicts, sample_fit_score):
    chat_model = FakeChatModel(return_value=None)

    with pytest.raises(RepositioningError):
        generate_repositioning_suggestion(sample_verdicts, sample_fit_score, chat_model)


def test_llm_invocation_failure_raises_repositioning_error_not_raw_exception(sample_verdicts, sample_fit_score):
    chat_model = FakeChatModel(raise_exc=RuntimeError("model unavailable"))

    with pytest.raises(RepositioningError):
        generate_repositioning_suggestion(sample_verdicts, sample_fit_score, chat_model)


# happy path
def test_happy_path_returns_repositioning_suggestion(sample_verdicts, sample_fit_score):
    chat_model = FakeChatModel(return_value={"text": "Lean on adjacent evidence for Kubernetes."})

    result = generate_repositioning_suggestion(sample_verdicts, sample_fit_score, chat_model)

    assert isinstance(result, RepositioningSuggestion)
    assert chat_model.structured_output.invoke_calls  # LLM was actually called


# below the repositioning threshold: no LLM call, fixed "no suggestion" text instead
def test_below_threshold_score_skips_llm_and_returns_fixed_suggestion(sample_verdicts):
    low_fit_score = FitScore(value=59.9, required_coverage=50.0, preferred_coverage=0.0)
    chat_model = FakeChatModel(return_value={"text": "should never be reached"})

    result = generate_repositioning_suggestion(sample_verdicts, low_fit_score, chat_model)

    assert isinstance(result, RepositioningSuggestion)
    assert not chat_model.structured_output.invoke_calls  # LLM was never called
    assert result.text != "should never be reached"


# right at the threshold: still a normal LLM-backed suggestion (break is strictly below 60)
def test_at_threshold_score_still_calls_llm(sample_verdicts):
    at_threshold_fit_score = FitScore(value=60.0, required_coverage=60.0, preferred_coverage=None)
    chat_model = FakeChatModel(return_value={"text": "Lean on adjacent evidence for Kubernetes."})

    result = generate_repositioning_suggestion(sample_verdicts, at_threshold_fit_score, chat_model)

    assert chat_model.structured_output.invoke_calls  # LLM was actually called
    assert result.text == "Lean on adjacent evidence for Kubernetes."


# 60-85: substantial repositioning ground - prompt asks for key arguments and advice
def test_mid_tier_prompt_asks_for_key_arguments_and_advice(sample_verdicts):
    mid_tier_fit_score = FitScore(value=72.5, required_coverage=100.0, preferred_coverage=0.0)
    chat_model = FakeChatModel(return_value={"text": "some advice"})

    generate_repositioning_suggestion(sample_verdicts, mid_tier_fit_score, chat_model)

    prompt_sent = str(chat_model.structured_output.invoke_calls[0])
    assert "key argument" in prompt_sent.lower()
    assert "missing required skill" not in prompt_sent.lower()


# >=85: near-complete fit - prompt narrows to covering any missing Required Skills only
def test_high_tier_prompt_narrows_to_missing_required_skills(sample_verdicts):
    high_tier_fit_score = FitScore(value=90.0, required_coverage=90.0, preferred_coverage=100.0)
    chat_model = FakeChatModel(return_value={"text": "some advice"})

    generate_repositioning_suggestion(sample_verdicts, high_tier_fit_score, chat_model)

    prompt_sent = str(chat_model.structured_output.invoke_calls[0])
    assert "missing required skill" in prompt_sent.lower()
    assert "key argument" not in prompt_sent.lower()


# exactly at the mid/high boundary: high tier framing (boundary belongs to >=85)
def test_high_tier_boundary_at_85_uses_high_tier_prompt(sample_verdicts):
    boundary_fit_score = FitScore(value=85.0, required_coverage=85.0, preferred_coverage=85.0)
    chat_model = FakeChatModel(return_value={"text": "some advice"})

    generate_repositioning_suggestion(sample_verdicts, boundary_fit_score, chat_model)

    prompt_sent = str(chat_model.structured_output.invoke_calls[0])
    assert "missing required skill" in prompt_sent.lower()
