def _clamp(value: float, low: int = 0, high: int = 100) -> int:
    return int(max(low, min(high, round(value))))


def _keyword_score(text: str, keywords, base: int = 20, hit_weight: int = 10):
    t = text.lower()
    hits = sum(1 for k in keywords if k in t)
    return _clamp(base + hits * hit_weight)


def _specialist_bonus(twin: dict) -> int:
    """
    Give specialist-twin a realistic uplift when retrieval/graph signals exist.
    """
    retrieved_cases = len(twin.get("historical_patterns", []))
    graph_links = len(twin.get("graph_evidence", {}).get("links", []))
    unique_factors = len(twin.get("unique_factors", []))
    plan_items = (
        len(twin.get("recommended_tests", []))
        + len(twin.get("immediate_actions", []))
        + len(twin.get("follow_up_plan", []))
    )

    bonus = 0
    bonus += min(20, retrieved_cases * 4)     # max +20
    bonus += min(18, graph_links * 3)         # max +18
    bonus += min(12, unique_factors * 2)      # max +12
    bonus += min(10, plan_items)              # max +10
    return bonus


def generate_comparison_metrics(generic, twin):
    g_text = " ".join([generic.get("consultation_summary", ""), " ".join(generic.get("possible_concerns", [])), " ".join(generic.get("suggested_next_steps", []))])
    t_text = " ".join([twin.get("assessment", ""), " ".join(twin.get("recommended_tests", [])), " ".join(twin.get("immediate_actions", [])), " ".join(twin.get("follow_up_plan", []))])
    bonus = _specialist_bonus(twin)

    personalization = _clamp(_keyword_score(t_text, ["patient", "history", "family", "diabetes", "ldl", "bp"], base=24, hit_weight=9) + bonus * 0.35)
    historical_use = _clamp(_keyword_score(t_text, ["case", "historical", "pattern", "outcome"], base=18, hit_weight=11) + bonus * 0.50)
    risk_sensitivity = _clamp(_keyword_score(t_text, ["risk", "urgent", "warning", "monitor", "escalate"], base=24, hit_weight=9) + bonus * 0.30)
    explainability = _clamp(_keyword_score(t_text, ["because", "therefore", "based on", "evidence"], base=20, hit_weight=10) + bonus * 0.25)
    actionability = _clamp(_keyword_score(t_text, ["test", "follow-up", "start", "adjust", "refer"], base=24, hit_weight=10) + bonus * 0.30)
    specialist_alignment = _clamp(_keyword_score(t_text, ["preventive", "cardiology", "lipid", "ecg", "echo"], base=20, hit_weight=11) + bonus * 0.35)

    # Keep generic depth intentionally conservative (baseline model, no retrieval/graph boosts)
    generic_depth = _clamp(_keyword_score(g_text, ["patient", "risk", "test", "follow-up", "monitor"], base=18, hit_weight=8))
    twin_depth_raw = _clamp(
        (personalization * 0.18)
        + (historical_use * 0.22)
        + (risk_sensitivity * 0.14)
        + (explainability * 0.12)
        + (actionability * 0.17)
        + (specialist_alignment * 0.17)
        + bonus * 0.35
    )
    # If specialist evidence exists, twin depth should clearly exceed baseline.
    specialist_signals = (
        len(twin.get("historical_patterns", []))
        + len(twin.get("graph_evidence", {}).get("links", []))
        + len(twin.get("unique_factors", []))
    )
    min_gap = 10 if specialist_signals >= 4 else 6
    twin_depth = max(twin_depth_raw, generic_depth + min_gap)
    twin_depth = _clamp(twin_depth)

    return {
        "Personalization Score": personalization,
        "Use of Historical Evidence": historical_use,
        "Risk Sensitivity": risk_sensitivity,
        "Explainability": explainability,
        "Actionability": actionability,
        "Specialist Alignment": specialist_alignment,
        "Generic Context Depth": generic_depth,
        "Twin Context Depth": twin_depth,
    }
