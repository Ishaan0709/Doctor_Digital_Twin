def rerank_cases(cases, patient_text: str):
    t = patient_text.lower()

    def bonus_for_case(c):
        bonus = 0.0
        s = str(c.get("symptoms", "")).lower()
        d = str(c.get("diagnosis", "")).lower()
        if any(k in t and k in s for k in ["chest pain", "ldl", "diabetes", "bp"]):
            bonus += 0.08
        if "cad" in t and "cad" in d:
            bonus += 0.1
        return bonus

    enriched = []
    for c in cases:
        base = float(c.get("match_score", 0.0))
        bonus = bonus_for_case(c)
        updated = dict(c)
        updated["base_match_score"] = base
        updated["rerank_bonus"] = round(bonus, 3)
        updated["final_match_score"] = round(min(1.0, base + bonus), 3)
        enriched.append(updated)

    return sorted(enriched, key=lambda c: c["final_match_score"], reverse=True)
