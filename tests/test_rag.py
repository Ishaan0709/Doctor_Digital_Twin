from rag.retrieve import retrieve_similar_cases


def test_retrieval_returns_list():
    out = retrieve_similar_cases("56M chest pain high LDL diabetes", top_k=3)
    assert isinstance(out, list)
