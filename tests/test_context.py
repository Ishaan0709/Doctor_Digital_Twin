from backend.context import clarifying_questions, style_rules, timeline_context


def test_clarifying_questions_when_fields_missing():
    questions = clarifying_questions({"symptoms": "", "symptom_duration": "2 weeks", "bp": "", "current_medications": ""})
    assert len(questions) == 3
    assert any("blood pressure" in q.lower() for q in questions)


def test_style_rules_come_from_csv():
    rules = style_rules()
    assert any("prevention" in rule.lower() for rule in rules)


def test_timeline_context_for_known_profile():
    text = timeline_context("P001")
    assert "P001" in text
    assert "visits" in text
