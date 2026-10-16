"""Load heavy files once when the API process starts."""

from twin_engine.twin_prompt import load_prompt


def load_resources() -> None:
    from backend.context import warm_tables
    from graph_rag.build_graph import get_cached_graph
    from rag.retrieve import warm_index

    warm_tables()
    get_cached_graph()
    warm_index()
    for name in ("doctor_twin.txt", "generic_gpt.txt", "graph_reasoning.txt", "patient_summary.txt"):
        load_prompt(name)
