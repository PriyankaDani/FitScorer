from pathlib import Path

import streamlit as st

from fitscorer.config import Settings
from fitscorer.extraction import ExtractionError, extract_job_posting
from fitscorer.llm.provider import get_chat_model
from fitscorer.models import Profile
from fitscorer.repositioning import RepositioningError, generate_repositioning_suggestion
from fitscorer.report import build_report_markdown, save_report
from fitscorer.scoring import compute_fit_score
from fitscorer.session import Session, SessionEntry
from fitscorer.verdicts import VerdictsError, generate_skill_verdicts

DEFAULT_PROFILE_PATH = Path("data/profile.json")


@st.cache_resource
def _get_chat_model():
    return get_chat_model(Settings())


def _load_profile(raw_json: str) -> Profile:
    return Profile.model_validate_json(raw_json)


def _render_verdicts(verdicts, skill_type: str, heading: str) -> None:
    st.markdown(f"**{heading}**")
    matching = [v for v in verdicts if v.skill_type == skill_type]
    if not matching:
        st.caption("None.")
        return
    for v in matching:
        st.markdown(f"- **{v.skill_name}** — {v.verdict}: {v.rationale}")


def _render_result(entry: SessionEntry, *, key_prefix: str) -> None:
    st.markdown(f"### {entry.job_posting.role_title}")
    st.metric("Fit Score", entry.fit_score.value)
    st.caption(
        f"Required coverage: {entry.fit_score.required_coverage} · "
        f"Preferred coverage: {entry.fit_score.preferred_coverage}"
    )
    _render_verdicts(entry.verdicts, "required", "Required Skills")
    _render_verdicts(entry.verdicts, "preferred", "Preferred Skills")
    st.markdown("**Repositioning Suggestion**")
    st.write(entry.repositioning.text)

    if st.button("Save Report", key=f"{key_prefix}-save"):
        markdown = build_report_markdown(
            entry.job_posting, entry.verdicts, entry.fit_score, entry.repositioning
        )
        path = save_report(markdown, entry.job_posting)
        st.success(f"Report saved to {path}")


def main() -> None:
    st.set_page_config(page_title="FitScorer", layout="wide")
    st.title("FitScorer")

    if "session" not in st.session_state:
        st.session_state["session"] = Session()
    if "profile" not in st.session_state:
        st.session_state["profile"] = None

    with st.sidebar:
        st.header("Profile")
        uploaded = st.file_uploader("Upload profile.json", type="json")
        if uploaded is not None:
            try:
                st.session_state["profile"] = _load_profile(uploaded.getvalue().decode("utf-8-sig"))
                st.success("Profile loaded from upload.")
            except Exception as e:
                st.error(f"Could not load uploaded Profile: {e}")
        elif st.session_state["profile"] is None and DEFAULT_PROFILE_PATH.exists():
            try:
                st.session_state["profile"] = _load_profile(
                    DEFAULT_PROFILE_PATH.read_text(encoding="utf-8-sig")
                )
                st.success(f"Profile loaded from {DEFAULT_PROFILE_PATH}.")
            except Exception as e:
                st.error(f"Could not load {DEFAULT_PROFILE_PATH}: {e}")

        if st.session_state["profile"] is not None:
            st.caption(st.session_state["profile"].summary)
        else:
            st.warning("No Profile loaded. Place one at data/profile.json or upload one above.")

    st.header("Score a Job Posting")
    raw_text = st.text_area("Paste JobPosting text", height=250)
    score_clicked = st.button("Score", type="primary")

    if score_clicked:
        profile = st.session_state["profile"]
        if profile is None:
            st.error("Load a Profile before scoring.")
        else:
            chat_model = _get_chat_model()
            try:
                with st.spinner("Extracting JobPosting..."):
                    job_posting = extract_job_posting(raw_text, chat_model)
                with st.spinner("Generating Skill Verdicts..."):
                    verdicts = generate_skill_verdicts(profile, job_posting, chat_model)
                fit_score = compute_fit_score(verdicts)
                with st.spinner("Generating Repositioning Suggestion..."):
                    repositioning = generate_repositioning_suggestion(verdicts, fit_score, chat_model)
                st.session_state["session"].add_run(job_posting, verdicts, fit_score, repositioning)
            except ExtractionError as e:
                st.error(f"Could not extract JobPosting: {e}")
            except VerdictsError as e:
                st.error(f"Could not generate Skill Verdicts: {e}")
            except RepositioningError as e:
                st.error(f"Could not generate Repositioning Suggestion: {e}")
            except ValueError as e:
                st.error(f"Could not compute Fit Score: {e}")

    session: Session = st.session_state["session"]

    if session.entries:
        st.header("Latest Result")
        _render_result(session.entries[-1], key_prefix=f"latest-{len(session.entries) - 1}")

        st.header("Session History")
        st.dataframe(
            [
                {
                    "Role": e.job_posting.role_title,
                    "Company": e.job_posting.company,
                    "Fit Score": e.fit_score.value,
                    "Timestamp": e.timestamp,
                }
                for e in session.entries
            ],
            use_container_width=True,
        )

        with st.expander("Browse past runs"):
            for i, entry in enumerate(reversed(session.entries)):
                idx = len(session.entries) - 1 - i
                with st.container(border=True):
                    _render_result(entry, key_prefix=f"history-{idx}")


if __name__ == "__main__":
    main()
