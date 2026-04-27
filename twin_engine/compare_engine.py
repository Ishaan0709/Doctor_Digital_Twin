def _score(text: str, keywords):
    t = text.lower()
    return min(100, sum(15 for k in keywords if k in t) + 25)


def generate_comparison_metrics(generic, twin):
    g_text = " ".join([generic.get("consultation_summary", ""), " ".join(generic.get("possible_concerns", [])), " ".join(generic.get("suggested_next_steps", []))])
    t_text = " ".join([twin.get("assessment", ""), " ".join(twin.get("recommended_tests", [])), " ".join(twin.get("immediate_actions", [])), " ".join(twin.get("follow_up_plan", []))])
    return {
        "Personalization Score": _score(t_text, ["patient", "history", "family", "diabetes", "ldl", "bp"]),
        "Use of Historical Evidence": _score(t_text, ["case", "historical", "pattern", "outcome"]),
        "Risk Sensitivity": _score(t_text, ["risk", "urgent", "warning", "monitor", "escalate"]),
        "Explainability": _score(t_text, ["because", "therefore", "based on", "evidence"]),
        "Actionability": _score(t_text, ["test", "follow-up", "start", "adjust", "refer"]),
        "Specialist Alignment": _score(t_text, ["preventive", "cardiology", "lipid", "ecg", "echo"]),
        "Generic Context Depth": _score(g_text, ["patient", "risk", "test"]),
    }
