def _clamp(value: float, low: int = 0, high: int = 100) -> int:
    return int(max(low, min(high, round(value))))


def _hits(text: str, words) -> int:
    folded = text.lower()
    return sum(1 for word in words if word in folded)


def _signals(twin: dict) -> dict:
    links = (twin.get("graph_evidence") or {}).get("links") or []
    return {
        "cases": len(twin.get("historical_patterns") or []),
        "links": len(links),
        "unique": len(twin.get("unique_factors") or []),
        "plans": len(twin.get("recommended_tests") or []) + len(twin.get("immediate_actions") or []) + len(twin.get("follow_up_plan") or []),
    }


# Personalization counts intake words for both answers, then caps the generic side.
# Repeating the form (age, diabetes, LDL) is real, and it is not the same as a plan
# that changes because of a uniqueness flag. Explainability and accuracy add the
# retrieved graph links and cases only on the Doctor's Twin, and only when those
# objects were actually returned.
FACTORS = [
    {
        "name": "Personalization",
        "meaning": "How far the answer goes past repeating the intake form. Naming age, diabetes, or LDL counts for both sides, and that part is capped for Generic GPT. Doctor's Twin goes higher only when uniqueness flags from this patient's own numbers change the plan.",
    },
    {
        "name": "Historical evidence",
        "meaning": "Whether the answer uses this doctor's past cases as references. Generic GPT is not given those cases.",
    },
    {
        "name": "Risk sensitivity",
        "meaning": "Whether the answer names the risk and says when to escalate, such as pain at rest, fainting, or severe breathlessness. A calm answer that misses this can reassure someone who should seek care now.",
    },
    {
        "name": "Clinician supervision",
        "meaning": "Whether a doctor remains responsible. Both sides stay high. The Doctor's Twin is a second view of this doctor's reasoning. It does not replace the clinician who examines the patient.",
    },
    {
        "name": "Explainability",
        "meaning": "Whether each step says why. A retrieved graph link counts only for Doctor's Twin, because that link is a finding, a relation, and a next step. A lone 'because' in Generic GPT is not tied to a retrieved link.",
    },
    {
        "name": "Actionability",
        "meaning": "Whether the next tests, actions, and follow-up are concrete enough to carry out.",
    },
    {
        "name": "Specialist alignment",
        "meaning": "Whether the answer stays in this doctor's preventive-cardiology frame: lipids, ECG, echo, and a follow-up, rather than a general medical note.",
    },
    {
        "name": "Accuracy",
        "meaning": "How much of the answer can be checked against a retrieved case or a graph link. A grounded Doctor's Twin lands near 95. Generic GPT lands near 40, because it has no retrieved case or graph link. Neither score means a diagnosis is certain.",
    },
]


def _personalization(text: str, signals: dict, twin_side: bool) -> int:
    form_hits = _hits(text, ["patient", "age", "history", "name"])
    specific_hits = _hits(
        text,
        ["diabetes", "ldl", "hba1c", "family", "bp", "blood pressure", "hypertension", "statin", "smok", "chest", "exertion", "medication"],
    )
    score = 18 + form_hits * 4 + specific_hits * 6
    if twin_side:
        score += min(42, signals["unique"] * 18)
        if _hits(text, ["increases", "raises", "because", "further", "burden"]):
            score += 8
        return _clamp(score)
    # Repeating the supplied form cannot occupy the same range as a plan changed by uniqueness flags.
    return _clamp(min(58, score))


def _historical(text: str, signals: dict, twin_side: bool) -> int:
    score = 16 + _hits(text, ["case", "historical", "pattern", "outcome", "similar"]) * 8
    if twin_side:
        score += min(36, signals["cases"] * 7)
    return _clamp(score)


def _risk(text: str, signals: dict, twin_side: bool) -> int:
    score = 16 + _hits(text, ["risk", "urgent", "warning", "monitor", "escalate", "emergency", "rest pain", "faint", "breathless"]) * 8
    if twin_side:
        score += min(12, signals["links"])
    return _clamp(score)


def _explainability(text: str, signals: dict, twin_side: bool) -> int:
    score = 16 + _hits(text, ["because", "therefore", "based on", "evidence", "reason", "increases", "raises", "given"]) * 7
    if twin_side:
        # Each retrieved relation is one checkable reason: source, relation, target.
        score += min(60, signals["links"] * 5)
    return _clamp(score)


def _actionability(text: str, signals: dict, twin_side: bool) -> int:
    score = 16 + _hits(text, ["test", "follow-up", "follow up", "start", "adjust", "refer", "ecg", "echo"]) * 7
    if twin_side:
        score += min(28, signals["plans"] * 3)
    return _clamp(score)


def _alignment(text: str, signals: dict, twin_side: bool) -> int:
    score = 16 + _hits(text, ["preventive", "cardiology", "lipid", "ecg", "echo", "statin", "angina"]) * 8
    if twin_side:
        score += min(20, signals["plans"] * 2 + (6 if signals["links"] else 0))
    return _clamp(score)


def _supervision(text: str, signals: dict, twin_side: bool) -> int:
    # Both answers are decision support. The band is tight so neither can "win" by replacing a doctor.
    mentioned = _hits(text, ["doctor", "clinician", "not a substitute", "supervision", "in-person"])
    return _clamp(90 + min(4, mentioned))


def _accuracy(text: str, signals: dict, twin_side: bool) -> int:
    # Grounding only. A similar case is not this patient, so the twin stays near 95 and generic stays near 40.
    words = ["case", "ecg", "echo", "ldl", "graph", "follow-up", "follow up"]
    hits = _hits(text, words)
    if twin_side:
        score = 30 + hits * 2
        score += min(22, signals["cases"] * 4)
        score += min(16, signals["links"])
        if signals["cases"] >= 3 and signals["links"] >= 4:
            score += 21
        return _clamp(min(score, 95))
    return _clamp(min(34 + hits * 2, 40))


_SCORERS = {
    "Personalization": _personalization,
    "Historical evidence": _historical,
    "Risk sensitivity": _risk,
    "Clinician supervision": _supervision,
    "Explainability": _explainability,
    "Actionability": _actionability,
    "Specialist alignment": _alignment,
    "Accuracy": _accuracy,
}


def _texts(generic: dict, twin: dict) -> tuple[str, str]:
    generic_text = " ".join(
        [
            generic.get("consultation_summary", ""),
            " ".join(generic.get("possible_concerns") or []),
            " ".join(generic.get("suggested_next_steps") or []),
            " ".join(generic.get("risk_notes") or []),
        ]
    )
    evidence = (twin.get("graph_evidence") or {}).get("evidence_summary") or []
    twin_text = " ".join(
        [
            twin.get("assessment", ""),
            " ".join(twin.get("recommended_tests") or []),
            " ".join(twin.get("immediate_actions") or []),
            " ".join(twin.get("follow_up_plan") or []),
            " ".join(twin.get("unique_factors") or []),
            " ".join(str(line) for line in evidence),
        ]
    )
    return generic_text, twin_text


def _reason(name: str, winner: str, signals: dict) -> str:
    unique = signals["unique"]
    links = signals["links"]
    cases = signals["cases"]
    if name == "Personalization":
        if winner == "twin" and unique:
            return (
                f"Generic GPT repeats the intake, so that bar is real, and it is capped because a form recap does not change the plan. "
                f"Doctor's Twin adds {unique} uniqueness judgment{'s' if unique != 1 else ''} from this patient's own numbers, and those judgments change the prevention steps."
            )
        if winner == "twin":
            return "Doctor's Twin ties more of the written answer to this patient's own markers. Generic GPT mostly repeats the intake, and that recap is capped."
        if winner == "generic":
            return "Generic GPT names more of this patient's own markers in the written answer. Doctor's Twin did not add uniqueness judgments on this run."
        return "Both answers mention this patient, and Doctor's Twin did not pull ahead with uniqueness judgments."
    if name == "Historical evidence":
        if winner == "twin":
            return f"Doctor's Twin retrieved {cases} past case{'s' if cases != 1 else ''} and can use them as references. Generic GPT is not given the case file."
        if winner == "generic":
            return "Generic GPT happens to use case-like wording. Doctor's Twin did not retrieve cases on this run."
        return "Past cases were not clearly used by either answer."
    if name == "Risk sensitivity":
        if winner == "twin":
            return "Doctor's Twin is more explicit about the risk and when to escalate."
        if winner == "generic":
            return "Generic GPT uses clearer warning language on this run. Doctor's Twin did not add a stronger escalation line."
        return (
            "The scores sit together because Generic GPT already carries a fixed warning about worsening pain, and the Doctor's Twin does not yet write a stronger one. "
            "If this factor stays weak, a calm paragraph can reassure someone who should seek care now, and the project fails at the job that matters most. A doctor still has to see the patient."
        )
    if name == "Clinician supervision":
        return (
            "Both stay high because neither answer is allowed to replace a doctor. "
            "Generic GPT tells you to check with a clinician. The Doctor's Twin prepares this doctor's reasoning, and the doctor who sees the patient decides."
        )
    if name == "Explainability":
        if winner == "twin":
            return (
                f"Doctor's Twin has {links} retrieved graph relation{'s' if links != 1 else ''}. "
                "Each one is a finding, the relation, and a next step, so the reason can be checked. "
                "Generic GPT can write 'because', and that sentence is not tied to a retrieved link."
            )
        if winner == "generic":
            return "Generic GPT explains itself with because or based-on language. Doctor's Twin has no retrieved graph relation to cite on this run."
        return "Both give a reason, or neither ties a step to a retrieved graph relation."
    if name == "Actionability":
        if winner == "twin":
            return "Doctor's Twin names tests, actions, and follow-up, and the plan lists back that up. Generic GPT gives broader next steps."
        if winner == "generic":
            return "Generic GPT gives clearer next steps on this run. Doctor's Twin plan lists are thin."
        return "Both suggest something to do, and the plans are not clearly stronger on one side."
    if name == "Specialist alignment":
        if winner == "twin":
            return "Doctor's Twin stays in this doctor's preventive frame and uses the tests the graph tends to suggest. Generic GPT stays more general."
        if winner == "generic":
            return "Generic GPT uses more of those specialist words on this run."
        return "Both sound generally medical, and neither is clearly in this doctor's preventive frame."
    if name == "Accuracy":
        if winner == "twin":
            return (
                f"Doctor's Twin can be checked against {cases} retrieved case{'s' if cases != 1 else ''} and {links} graph link{'s' if links != 1 else ''}, so the score sits near 95. "
                "It does not reach 100, because those cases are partial matches and one graph step is not a confirmed diagnosis. Generic GPT has neither source, so it stays near 40."
            )
        if winner == "generic":
            return "Generic GPT is more specific in the written answer. Doctor's Twin retrieved nothing to check this run against."
        return "Neither answer is clearly anchored to retrieved cases and graph links."
    return ""


def _improve(name: str, twin_score: int, gap: int, signals: dict) -> str:
    if twin_score >= 75 and gap >= 10:
        return ""
    if name == "Personalization":
        return "Open Doctor's Twin with this patient's age, conditions, LDL, blood pressure, and medicines, and repeat each uniqueness flag in the paragraph as the reason the plan changes."
    if name == "Historical evidence":
        return "Name one or two retrieved case ids and what was decided, and say they are references rather than a copy of this patient." if signals["cases"] else "Retrieve similar cases before the assessment is written. Without cases, this factor cannot rise."
    if name == "Risk sensitivity":
        return "Require one explicit line for worsening pain, pain at rest, fainting, or severe breathlessness, and name the risk the graph actually linked."
    if name == "Clinician supervision":
        return ""
    if name == "Explainability":
        return "For each recommendation, write one sentence as the finding, then the graph relation, then the action. Do not add a reason the graph did not return." if signals["links"] else "This stays low until the graph returns relations for this patient. Do not invent a because."
    if name == "Actionability":
        return "Fill recommended tests, immediate actions, and follow-up from the graph targets that are tests or actions, then say when to return."
    if name == "Specialist alignment":
        return "When the graph suggests ECG, echo, a lipid panel, or a follow-up, use those exact names in the plan."
    if name == "Accuracy":
        return "Cite the case id and the graph relation next to the step they support. Accuracy here means the answer can be checked, not that a diagnosis is certain."
    return ""


def generate_comparison_metrics(generic, twin):
    generic_text, twin_text = _texts(generic or {}, twin or {})
    signals = _signals(twin or {})
    factors = []
    generic_scores = []
    twin_scores = []

    for spec in FACTORS:
        score = _SCORERS[spec["name"]]
        generic_score = score(generic_text, signals, False)
        twin_score = score(twin_text, signals, True)
        gap = twin_score - generic_score
        if gap >= 10:
            winner = "twin"
        elif gap <= -8:
            winner = "generic"
        else:
            winner = "close"
        factors.append(
            {
                "name": spec["name"],
                "meaning": spec["meaning"],
                "generic": generic_score,
                "twin": twin_score,
                "winner": winner,
                "reason": _reason(spec["name"], winner, signals),
                "improve": _improve(spec["name"], twin_score, gap, signals),
            }
        )
        generic_scores.append(generic_score)
        twin_scores.append(twin_score)

    by_name = {item["name"]: item for item in factors}
    generic_depth = _clamp(sum(generic_scores) / len(generic_scores))
    twin_depth = _clamp(sum(twin_scores) / len(twin_scores))

    return {
        "Personalization Score": by_name["Personalization"]["twin"],
        "Use of Historical Evidence": by_name["Historical evidence"]["twin"],
        "Risk Sensitivity": by_name["Risk sensitivity"]["twin"],
        "Clinician Supervision": by_name["Clinician supervision"]["twin"],
        "Explainability": by_name["Explainability"]["twin"],
        "Actionability": by_name["Actionability"]["twin"],
        "Specialist Alignment": by_name["Specialist alignment"]["twin"],
        "Accuracy": by_name["Accuracy"]["twin"],
        "Generic Context Depth": generic_depth,
        "Twin Context Depth": twin_depth,
        "factors": factors,
    }
