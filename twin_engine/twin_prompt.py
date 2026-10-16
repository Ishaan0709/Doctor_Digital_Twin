from config import PROMPTS_DIR

_CACHE: dict[str, str] = {}


def load_prompt(name: str) -> str:
    if name not in _CACHE:
        _CACHE[name] = (PROMPTS_DIR / name).read_text(encoding="utf-8")
    return _CACHE[name]


def _plain(value: str) -> str:
    return (value or "").replace("{", "(").replace("}", ")")


def build_twin_prompt(
    patient_text: str,
    retrieved_cases: str,
    graph_summary: str,
    uniqueness: str,
    style_rules: str = "",
    timeline_context: str = "",
    clarifying_questions: str = "",
    patient_weighing: str = "",
    reasoning_guidance: str = "",
) -> str:
    base = load_prompt("doctor_twin.txt")
    return base.format(
        patient_context=_plain(patient_text),
        retrieved_cases=_plain(retrieved_cases),
        graph_summary=_plain(graph_summary),
        uniqueness_factors=_plain(uniqueness),
        style_rules=_plain(style_rules) or "- Calm, concise, preventive, plain language",
        timeline_context=_plain(timeline_context) or "No longitudinal timeline was selected.",
        clarifying_questions=_plain(clarifying_questions) or "None flagged from empty fields.",
        patient_weighing=_plain(patient_weighing),
        reasoning_guidance=_plain(reasoning_guidance),
    )
