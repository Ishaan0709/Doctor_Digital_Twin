from config import PROMPTS_DIR


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def build_twin_prompt(patient_text: str, retrieved_cases: str, graph_summary: str, uniqueness: str) -> str:
    base = load_prompt("doctor_twin.txt")
    return base.format(
        patient_context=patient_text,
        retrieved_cases=retrieved_cases,
        graph_summary=graph_summary,
        uniqueness_factors=uniqueness,
    )
