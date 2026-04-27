def rerank_cases(cases, patient_text: str):
    t = patient_text.lower()

    def score(c):
        bonus = 0.0
        s = str(c.get("symptoms", "")).lower()
        d = str(c.get("diagnosis", "")).lower()
        if any(k in t and k in s for k in ["chest pain", "ldl", "diabetes", "bp"]):
            bonus += 0.08
        if "cad" in t and "cad" in d:
            bonus += 0.1
        return float(c.get("match_score", 0.0)) + bonus

    return sorted(cases, key=score, reverse=True)
