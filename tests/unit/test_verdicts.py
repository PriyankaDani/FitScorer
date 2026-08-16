import pytest

from fitscorer.models import SkillVerdict
from fitscorer.verdicts import VerdictsError, generate_skill_verdicts


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


def verdict_payload(skill_name, skill_type, verdict="match", rationale="matches profile evidence"):
    return {
        "skill_name": skill_name,
        "skill_type": skill_type,
        "verdict": verdict,
        "rationale": rationale,
    }


def valid_verdicts_payload_for(job_posting):
    return {
        "verdicts": [
            verdict_payload(s.name, "required") for s in job_posting.required_skills
        ]
        + [verdict_payload(s.name, "preferred") for s in job_posting.preferred_skills]
    }


# verdict count == required + preferred skill count
def test_verdict_count_matches_required_plus_preferred_skills(sample_profile, sample_job_posting):
    payload = valid_verdicts_payload_for(sample_job_posting)
    chat_model = FakeChatModel(return_value=payload)

    result = generate_skill_verdicts(sample_profile, sample_job_posting, chat_model)

    expected_count = len(sample_job_posting.required_skills) + len(sample_job_posting.preferred_skills)
    assert len(result) == expected_count
    assert all(isinstance(v, SkillVerdict) for v in result)


# each verdict correctly tagged required vs preferred
def test_skill_type_tagged_correctly_for_required_and_preferred(sample_profile, sample_job_posting):
    payload = valid_verdicts_payload_for(sample_job_posting)
    chat_model = FakeChatModel(return_value=payload)

    result = generate_skill_verdicts(sample_profile, sample_job_posting, chat_model)

    required_names = {s.name for s in sample_job_posting.required_skills}
    preferred_names = {s.name for s in sample_job_posting.preferred_skills}

    for v in result:
        if v.skill_name in required_names:
            assert v.skill_type == "required"
        elif v.skill_name in preferred_names:
            assert v.skill_type == "preferred"
        else:
            pytest.fail(f"unexpected skill_name in verdicts: {v.skill_name}")


# malformed LLM output cases mirror extraction's error handling
def test_missing_verdicts_key_raises_verdicts_error(sample_profile, sample_job_posting):
    chat_model = FakeChatModel(return_value={})

    with pytest.raises(VerdictsError):
        generate_skill_verdicts(sample_profile, sample_job_posting, chat_model)


def test_verdict_with_missing_fields_raises_verdicts_error(sample_profile, sample_job_posting):
    payload = {"verdicts": [{"skill_name": "Python", "skill_type": "required"}]}
    chat_model = FakeChatModel(return_value=payload)

    with pytest.raises(VerdictsError):
        generate_skill_verdicts(sample_profile, sample_job_posting, chat_model)


def test_wrong_shaped_output_raises_verdicts_error(sample_profile, sample_job_posting):
    chat_model = FakeChatModel(return_value="not a structured payload at all")

    with pytest.raises(VerdictsError):
        generate_skill_verdicts(sample_profile, sample_job_posting, chat_model)


def test_none_output_raises_verdicts_error(sample_profile, sample_job_posting):
    chat_model = FakeChatModel(return_value=None)

    with pytest.raises(VerdictsError):
        generate_skill_verdicts(sample_profile, sample_job_posting, chat_model)


def test_llm_invocation_failure_raises_verdicts_error_not_raw_exception(sample_profile, sample_job_posting):
    chat_model = FakeChatModel(raise_exc=RuntimeError("model unavailable"))

    with pytest.raises(VerdictsError):
        generate_skill_verdicts(sample_profile, sample_job_posting, chat_model)


# whole Profile passed as evidence (ADR 0001) - not just the skills section
def test_whole_profile_passed_as_evidence(sample_profile, sample_job_posting):
    payload = valid_verdicts_payload_for(sample_job_posting)
    chat_model = FakeChatModel(return_value=payload)

    generate_skill_verdicts(sample_profile, sample_job_posting, chat_model)

    prompt_sent = str(chat_model.structured_output.invoke_calls[0])
    # evidence beyond the skills list must be present, e.g. Experience description
    assert sample_profile.experience[0].description in prompt_sent
    assert sample_profile.summary in prompt_sent


# output-language standardization: rationale must be English regardless of JobPosting's language
def test_prompt_instructs_english_output_regardless_of_job_posting_language(sample_profile, sample_job_posting):
    payload = valid_verdicts_payload_for(sample_job_posting)
    chat_model = FakeChatModel(return_value=payload)

    generate_skill_verdicts(sample_profile, sample_job_posting, chat_model)

    prompt_sent = str(chat_model.structured_output.invoke_calls[0]).lower()
    assert "english" in prompt_sent


# happy path
def test_happy_path_returns_skill_verdicts(sample_profile, sample_job_posting):
    payload = valid_verdicts_payload_for(sample_job_posting)
    chat_model = FakeChatModel(return_value=payload)

    result = generate_skill_verdicts(sample_profile, sample_job_posting, chat_model)

    assert all(isinstance(v, SkillVerdict) for v in result)
    assert chat_model.structured_output.invoke_calls  # LLM was actually called
