from graph_rag.build_graph import build_knowledge_graph
from graph_rag.reasoning import graph_reasoning


def test_graph_reasoning_has_summary():
    g = build_knowledge_graph()
    result = graph_reasoning("chest pain with diabetes and high ldl", g)
    assert "evidence_summary" in result
