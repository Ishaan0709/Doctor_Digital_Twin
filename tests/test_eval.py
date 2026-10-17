from eval.run_eval import (
    HOLDOUT_N,
    answer_followup,
    answer_risk,
    gold_followup,
    gold_risk,
    gold_tests,
    precision_recall,
    select_holdout,
    named_tests,
)
from rag.retrieve import _without_excluded


def test_holdout_is_thirty_and_stable():
    ids = [str(i) for i in range(1, 501)]
    first = select_holdout(ids)
    second = select_holdout(ids)
    assert first == second
    assert len(first) == HOLDOUT_N
    assert len(set(first)) == HOLDOUT_N
    assert set(first).isdisjoint(set(ids) - set(first))


def test_gold_labels_follow_the_recorded_decision():
    row = {"tests": "Troponin negative, Echo reduced EF", "treatment_decision": "ECG + stress test"}
    assert gold_tests(row) == {"troponin", "echo", "ecg", "stress"}
    assert gold_risk("Urgent ER referral") == "urgent"
    assert gold_risk("CT coronary angiography") == "investigate"
    assert gold_risk("Follow-up in 2 weeks") == "routine"
    assert gold_followup("Urgent ER referral") == "immediate"
    assert gold_followup("Follow-up in 2 weeks") == "2 weeks"
    assert gold_followup("Lifestyle counseling") == "unspecified"


def test_answer_overlap_and_exclusion():
    assert named_tests("Order a 12-lead ECG and a lipid panel") == {"ecg", "lipid"}
    assert answer_risk("Send the patient to the emergency room right away") == "urgent"
    assert answer_followup("Follow-up in 2 weeks") == "2 weeks"
    assert answer_followup("Follow-up within 3-7 days") == "other"
    precision, recall = precision_recall({"ecg", "echo"}, {"ecg"})
    assert precision == 0.5
    assert recall == 1.0
    hits = [{"case_id": "1"}, {"case_id": "2"}, {"case_id": "3"}]
    assert [item["case_id"] for item in _without_excluded(hits, {"1", "3"}, 2)] == ["2"]
    assert [item["case_id"] for item in _without_excluded(hits, None, 2)] == ["1", "2"]
