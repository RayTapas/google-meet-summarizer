from app import extractive_summary, make_report


def test_summary_keeps_key_sentence():
    text = "The team reviewed the launch plan. We agreed to ship on Friday. Priya will send the final checklist."
    assert "ship on Friday" in extractive_summary(text, max_sentences=3)


def test_report_has_sections():
    report = make_report("We agreed on the plan. Alex will email the customer by Friday.", "en")
    assert "## Decisions" in report
    assert "## Action items" in report
