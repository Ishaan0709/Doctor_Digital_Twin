import pandas as pd

from eval.run_eval import (
    BASELINE_TESTS,
    HOLDOUT_N,
    exclusion_audit,
    exclusion_from_disk,
    f1_score,
    gold_followup,
    gold_risk,
    gold_tests,
    precision_recall,
    select_holdout,
    named_tests,
    summarize_rows,
    _markdown,
    _rows_for_baseline,
)
from rag.retrieve import _without_excluded
from backend.context import style_rules_text


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
    precision, recall = precision_recall({"ecg", "echo"}, {"ecg"})
    assert precision == 0.5
    assert recall == 1.0
    assert f1_score(0.5, 1.0) == 2 / 3
    assert f1_score(0.0, 0.0) == 0.0
    assert f1_score(None, 1.0) is None
    hits = [{"case_id": "1"}, {"case_id": "2"}, {"case_id": "3"}]
    assert [item["case_id"] for item in _without_excluded(hits, {"1", "3"}, 2)] == ["2"]
    assert [item["case_id"] for item in _without_excluded(hits, None, 2)] == ["1", "2"]


def test_bootstrap_interval_collapses_when_every_case_matches():
    rows = [{"precision": 1.0, "recall": 1.0, "f1": 1.0, "n_tests": 3} for _ in range(10)]
    summary = summarize_rows(rows, n_boot=200, seed=1)
    assert summary["n"] == 10
    assert summary["f1"] == 1.0
    assert summary["f1_ci"] == [1.0, 1.0]
    assert summary["avg_tests"] == 3.0
    assert summary["avg_tests_ci"] == [3.0, 3.0]
    assert "risk_agreement" not in summary
    assert "followup_agreement" not in summary


def test_baseline_recommends_ecg_echo_and_lipid():
    assert BASELINE_TESTS == frozenset({"ecg", "echo", "lipid"})
    rows = _rows_for_baseline([{"gold": {"tests": ["ecg", "stress"]}}])
    assert rows[0]["n_tests"] == 3
    assert rows[0]["precision"] == 1 / 3
    assert rows[0]["recall"] == 0.5
    assert rows[0]["f1"] == 0.4


def test_report_lists_f1_baseline_interval_and_exclusion():
    item = {
        "n": 2,
        "test_precision": 0.5,
        "test_precision_ci": [0.25, 0.75],
        "test_recall": 0.5,
        "test_recall_ci": [0.25, 0.75],
        "f1": 0.5,
        "f1_ci": [0.25, 0.75],
        "avg_tests": 2.0,
        "avg_tests_ci": [1.0, 3.0],
    }
    report = {
        "holdout_size": 2,
        "seed": 17,
        "source": "data/raw/doctor_cases_vimlesh_pandey.csv",
        "holdout_case_ids": ["1", "2"],
        "summary": {key: item for key in ("generic", "rag", "twin", "baseline")},
        "bootstrap": {"samples": 2000, "level": 0.95, "seed": 17},
        "excluded": {
            "retrieval": "These case ids are passed to retrieval as exclude_ids.",
            "rule": "A node is removed when its name appears in a held-out case and in no training case.",
            "graph_nodes_removed": [],
            "graph_edges_removed": [],
            "style_rules_removed": [],
            "graph_nodes_kept": 34,
            "graph_edges_kept": 116,
            "style_rules_kept": 8,
            "nodes_not_in_any_case": ["prefers preventive care"],
        },
        "judge": None,
        "cases": [],
        "label_audit": None,
    }
    text = _markdown(report)
    assert "Sample size: 2" in text
    assert "95% percentile bootstrap" in text
    assert "Always ECG + echo + lipid panel" in text
    assert "What was excluded" in text
    assert "Graph nodes: none removed." in text
    assert "| Risk agreement |" not in text
    assert "| Follow-up agreement |" not in text


def _frames():
    nodes = pd.DataFrame(
        [
            {"node_id": 1, "name": "only hold", "type": "Symptom"},
            {"node_id": 2, "name": "shared", "type": "Test"},
            {"node_id": 3, "name": "train only", "type": "Decision"},
        ]
    )
    edges = pd.DataFrame(
        [
            {"source_id": 1, "target_id": 2, "relation": "suggests"},
            {"source_id": 2, "target_id": 3, "relation": "linked_to"},
            {"source_id": 2, "target_id": 1, "relation": "preferred_for"},
        ]
    )
    style = pd.DataFrame(
        [
            {"example_id": 1, "style_rule": "Calm tone"},
            {"example_id": 2, "style_rule": "See case 9 before deciding"},
            {"example_id": 3, "style_rule": "See case 14, which is not the held-out id 1"},
        ]
    )
    cases = pd.DataFrame(
        [
            {
                "case_id": "1",
                "symptoms": "shared",
                "risk_factors": "",
                "tests": "",
                "diagnosis": "",
                "treatment_decision": "train only",
                "reasoning_notes": "",
                "outcome": "",
            },
            {
                "case_id": "9",
                "symptoms": "only hold shared",
                "risk_factors": "",
                "tests": "",
                "diagnosis": "",
                "treatment_decision": "",
                "reasoning_notes": "",
                "outcome": "",
            },
        ]
    )
    return cases, nodes, edges, style


def test_holdout_only_graph_support_is_removed():
    cases, nodes, edges, style = _frames()
    audit = exclusion_audit(cases, {"9"}, nodes, edges, style)
    assert audit["graph_nodes_removed"] == ["only hold"]
    assert {item["source"] for item in audit["graph_edges_removed"]} >= {"only hold"}
    assert audit["graph_edges_kept"] == 1
    assert "See case 9 before deciding" in audit["style_rules_removed"]
    assert "Calm tone" not in audit["style_rules_removed"]
    assert all("case 14" not in rule for rule in audit["style_rules_removed"])
    names = {data["name"] for _, data in audit["graph"].nodes(data=True)}
    assert "only hold" not in names
    assert "shared" in names
    prefix = exclusion_audit(cases, {"1"}, nodes, edges, style)
    assert "See case 14, which is not the held-out id 1" not in prefix["style_rules_removed"]


def test_edge_that_co_occurs_only_in_the_holdout_is_removed():
    nodes = pd.DataFrame(
        [
            {"node_id": 1, "name": "alpha", "type": "Symptom"},
            {"node_id": 2, "name": "beta", "type": "Test"},
        ]
    )
    edges = pd.DataFrame([{"source_id": 1, "target_id": 2, "relation": "suggests"}])
    style = pd.DataFrame([{"example_id": 1, "style_rule": "Calm tone"}])
    cases = pd.DataFrame(
        [
            {"case_id": "1", "symptoms": "alpha", "risk_factors": "", "tests": "", "diagnosis": "", "treatment_decision": "", "reasoning_notes": "", "outcome": ""},
            {"case_id": "2", "symptoms": "beta", "risk_factors": "", "tests": "", "diagnosis": "", "treatment_decision": "", "reasoning_notes": "", "outcome": ""},
            {"case_id": "9", "symptoms": "alpha beta", "risk_factors": "", "tests": "", "diagnosis": "", "treatment_decision": "", "reasoning_notes": "", "outcome": ""},
        ]
    )
    audit = exclusion_audit(cases, {"9"}, nodes, edges, style)
    assert audit["graph_nodes_removed"] == []
    assert audit["graph_edges_removed"] == [{"source": "alpha", "target": "beta", "relation": "suggests"}]
    assert audit["graph_edges_kept"] == 0


def test_saved_holdout_does_not_exclusively_support_the_graph():
    from eval.run_eval import case_file

    frame = pd.read_csv(case_file()).fillna("")
    holdout = select_holdout(frame["case_id"].astype(str).tolist())
    audit = exclusion_from_disk(frame, set(holdout))
    assert audit["graph_nodes_removed"] == []
    assert audit["graph_edges_removed"] == []
    assert audit["style_rules_removed"] == []
    assert audit["graph_nodes_kept"] == 34
    assert audit["graph_edges_kept"] == 116
    assert audit["style_text"] == style_rules_text()
    assert set(audit["nodes_not_in_any_case"]) == {"prefers preventive care", "escalates exertional pain"}
