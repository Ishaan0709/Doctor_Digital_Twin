from graph_rag.build_graph import build_knowledge_graph
from graph_rag.history import history_links
from graph_rag.reasoning import graph_reasoning


def test_graph_reasoning_has_summary():
    g = build_knowledge_graph()
    result = graph_reasoning("chest pain with diabetes and high ldl", g)
    assert "evidence_summary" in result


def test_history_links_keep_the_case_id_and_skip_unrelated_rows():
    cases = [
        {"case_id": "14", "symptoms": "chest pain on exertion", "risk_factors": "diabetes", "decision": "ECG + stress test"},
        {"case_id": "15", "symptoms": "ankle swelling", "risk_factors": "obesity", "decision": "Holter monitor"},
    ]
    links = history_links("chest pain on exertion for two weeks", cases)
    assert len(links) == 1
    assert links[0]["case_id"] == "14"
    assert links[0]["target"] == "ECG + stress test"
    assert links[0]["relation"] == "observation_relates_to"
    assert history_links("mild headache only", cases) == []
