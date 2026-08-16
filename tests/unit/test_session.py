from fitscorer.session import Session


def test_add_run_appends_session_entry_with_timestamp(
    sample_job_posting, sample_verdicts, sample_fit_score, sample_repositioning
):
    session = Session()

    session.add_run(sample_job_posting, sample_verdicts, sample_fit_score, sample_repositioning)

    assert len(session.entries) == 1
    entry = session.entries[0]
    assert entry.job_posting == sample_job_posting
    assert entry.verdicts == sample_verdicts
    assert entry.fit_score == sample_fit_score
    assert entry.repositioning == sample_repositioning
    assert entry.timestamp is not None


def test_add_run_preserves_insertion_order_across_multiple_calls(
    sample_job_posting, sample_verdicts, sample_fit_score, sample_repositioning
):
    session = Session()

    session.add_run(sample_job_posting, sample_verdicts, sample_fit_score, sample_repositioning)
    second_job_posting = sample_job_posting.model_copy(update={"role_title": "Staff Backend Engineer"})
    session.add_run(second_job_posting, sample_verdicts, sample_fit_score, sample_repositioning)

    assert [entry.job_posting.role_title for entry in session.entries] == [
        sample_job_posting.role_title,
        "Staff Backend Engineer",
    ]
