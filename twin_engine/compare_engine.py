def _signals(twin: dict) -> dict:
    links = (twin.get("graph_evidence") or {}).get("links") or []
    return {
        "cases": len(twin.get("historical_patterns") or []),
        "links": len(links),
        "unique": len(twin.get("unique_factors") or []),
        "plans": len(twin.get("recommended_tests") or []) + len(twin.get("immediate_actions") or []) + len(twin.get("follow_up_plan") or []),
    }


# Each factor is the percent of the same checks that the written answer passes.
# There is no starting offset, no bonus, and no cap that holds one side at a chosen number.
# A check the answer does not meet scores 0. 100 means every check on that list passed.
FACTORS = [
    {
        "name": "Personalization",
        "meaning": "How many of this patient's own markers appear in the written answer. The same marker list is used for both answers. A uniqueness flag counts only when the answer repeats it.",
    },
    {
        "name": "Historical evidence",
        "meaning": "Whether the written answer uses a retrieved past case as a reference. Naming the word 'case' is one check. Citing a case that was actually retrieved is another. Generic GPT is not given the case file, so the citation checks fail unless the text itself contains them.",
    },
    {
        "name": "Risk sensitivity",
        "meaning": "Whether the written answer names the risk and the moments to escalate: pain at rest, fainting, or severe breathlessness. A calm answer that misses these checks can reassure someone who should seek care now.",
    },
    {
        "name": "Clinician supervision",
        "meaning": "Whether the written answer says a doctor remains responsible. The score is the share of supervision phrases that actually appear. It is not assumed.",
    },
    {
        "name": "Explainability",
        "meaning": "Whether the written answer says why. A graph link counts only when the answer quotes that link's finding and its next step. A 'because' with no attached link still passes the word check, and it does not pass the link check.",
    },
    {
        "name": "Actionability",
        "meaning": "Whether the written answer names a test, an action, a follow-up, and a time. Each of those is one check.",
    },
    {
        "name": "Specialist alignment",
        "meaning": "Whether the written answer stays in this doctor's preventive-cardiology frame: ECG, echo, lipids, a follow-up, and ischemic disease, rather than a general medical note.",
    },
    {
        "name": "Evidence grounding",
        "meaning": "How much of the written answer can be traced to a retrieved case or a graph link. This is traceability, not clinical correctness. A similar case is not this patient, and a graph link is not a confirmed diagnosis.",
    },
]

TRACEABILITY_NOTE = (
    "These scores measure traceability, not clinical correctness. "
    "Each number is the percent of checks the written answer passed. "
    "Nothing is added before the answer is read, and neither side is held at a fixed score."
)


def _has(text: str, phrases: list[str]) -> str:
    folded = text.lower()
    for phrase in phrases:
        if phrase in folded:
            return phrase
    return ""


def _check(label: str, passed: bool, found: str, missing: str) -> dict:
    return {"label": label, "detail": found if passed else missing, "value": 1 if passed else 0}


def _pack(lines: list[dict]) -> dict:
    passed = sum(line["value"] for line in lines)
    checks = len(lines)
    # Half rounds up, so 1 of 8 (12.5) is 13, which is what a person does on a calculator.
    total = ((100 * passed) + (checks // 2)) // checks if checks else 0
    return {"lines": lines, "passed": passed, "checks": checks, "total": total}


def _marker(text: str, label: str, phrases: list[str]) -> dict:
    found = _has(text, phrases)
    return _check(
        label,
        bool(found),
        f"Found “{found}”.",
        f"None of these appear: {', '.join(phrases)}.",
    )


def _flag_check(text: str, flag: str) -> dict:
    words = [word for word in flag.lower().replace(",", " ").split() if len(word) > 3]
    folded = text.lower()
    hit = sum(1 for word in words if word in folded)
    needed = max(1, (len(words) + 1) // 2)
    passed = bool(words) and hit >= needed
    return _check(
        "Uniqueness flag repeated",
        passed,
        f"The answer repeats “{flag}”.",
        f"The answer does not repeat “{flag}”.",
    )


def _case_cited(text: str, cases: list) -> str:
    folded = text.lower()
    for case in cases:
        cid = str(case.get("case_id") or "").strip()
        if cid and f"case {cid}".lower() in folded:
            return f"case {cid}"
        for key in ("diagnosis", "decision"):
            phrase = str(case.get(key) or "").strip()
            if len(phrase) >= 4 and phrase.lower() in folded:
                return phrase
    return ""


def _link_quoted(text: str, links: list) -> str:
    folded = text.lower()
    for link in links:
        source = [tok for tok in str(link.get("source") or "").lower().split() if len(tok) >= 3]
        target = [tok for tok in str(link.get("target") or "").lower().split() if len(tok) >= 3]
        if source and target and any(tok in folded for tok in source) and any(tok in folded for tok in target):
            return f"{link.get('source')} → {link.get('target')}"
    return ""


def _personalization(text: str, twin: dict) -> dict:
    lines = [
        _marker(text, "Age", ["age"]),
        _marker(text, "Diabetes", ["diabetes"]),
        _marker(text, "LDL or cholesterol", ["ldl", "cholesterol"]),
        _marker(text, "HbA1c", ["hba1c", "a1c"]),
        _marker(text, "Family history", ["family"]),
        _marker(text, "Blood pressure", ["blood pressure", "hypertension", " bp"]),
        _marker(text, "Smoking", ["smok"]),
        _marker(text, "Chest symptom", ["chest", "exertion"]),
        _marker(text, "Medication", ["medication", "medicine", "statin"]),
    ]
    for flag in twin.get("unique_factors") or []:
        lines.append(_flag_check(text, str(flag)))
    return _pack(lines)


def _historical(text: str, twin: dict, attached: bool) -> dict:
    cases = twin.get("historical_patterns") or []
    cited = _case_cited(text, cases)
    lines = [
        _marker(text, "Says this is a past case", ["case", "historical"]),
        _marker(text, "Says the case is a reference", ["similar", "reference", "not this patient"]),
        _marker(text, "Mentions an outcome", ["outcome", "improved", "resolved"]),
        _check(
            "Cites a retrieved case",
            bool(cited),
            f"The answer cites {cited}.",
            "No retrieved case id, diagnosis, or decision appears in this answer." if cases else "No case was retrieved, so there is nothing to cite.",
        ),
        _check(
            "A case is attached",
            attached and bool(cases),
            f"{len(cases)} retrieved case{'s' if len(cases) != 1 else ''} {'are' if len(cases) != 1 else 'is'} attached to this answer.",
            "No retrieved case is attached to this answer.",
        ),
    ]
    return _pack(lines)


def _risk(text: str) -> dict:
    return _pack(
        [
            _marker(text, "Names the risk", ["risk"]),
            _marker(text, "Says when to escalate", ["escalate", "urgent", "emergency"]),
            _marker(text, "Pain at rest", ["rest pain", "pain at rest"]),
            _marker(text, "Fainting", ["faint", "syncope"]),
            _marker(text, "Severe breathlessness", ["breathless", "dyspnea", "short of breath", "shortness of breath"]),
        ]
    )


def _supervision(text: str) -> dict:
    return _pack(
        [
            _marker(text, "Doctor or physician", ["doctor", "physician", " dr."]),
            _marker(text, "Clinician", ["clinician", "licensed"]),
            _marker(text, "Not a substitute", ["not a substitute", "does not replace", "decision support"]),
            _marker(text, "In person", ["in person", "in-person", "come in"]),
            _marker(text, "Supervision", ["supervision", "supervised"]),
        ]
    )


def _explainability(text: str, links: list) -> dict:
    quoted = _link_quoted(text, links)
    return _pack(
        [
            _marker(text, "Gives a reason", ["because", "therefore", "based on"]),
            _marker(text, "Names the evidence", ["evidence", "reason"]),
            _marker(text, "Says what the finding does", ["increases", "raises", "given"]),
            _check(
                "Quotes a retrieved graph link",
                bool(quoted),
                f"The answer quotes {quoted}.",
                "No retrieved graph link is quoted." if links else "No graph link was attached, so none can be quoted.",
            ),
        ]
    )


def _actionability(text: str) -> dict:
    return _pack(
        [
            _marker(text, "Names a test", ["ecg", "echo", "lipid", "troponin", "holter", "stress", "test"]),
            _marker(text, "Names a follow-up", ["follow-up", "follow up"]),
            _marker(text, "Names an action", ["start", "adjust", "refer", "optim"]),
            _marker(text, "Names a time", ["day", "week"]),
        ]
    )


def _alignment(text: str) -> dict:
    return _pack(
        [
            _marker(text, "ECG", ["ecg"]),
            _marker(text, "Echo", ["echo"]),
            _marker(text, "Lipids", ["lipid", "statin"]),
            _marker(text, "Preventive frame", ["preventive", "cardiology"]),
            _marker(text, "Follow-up", ["follow-up", "follow up"]),
            _marker(text, "Ischemic disease", ["angina", "ischemi"]),
        ]
    )


def _grounding(text: str, twin: dict) -> dict:
    # Both answers are checked against the same retrieved objects. A side passes only when its own text cites them.
    cases = twin.get("historical_patterns") or []
    links = (twin.get("graph_evidence") or {}).get("links") or []
    cited = _case_cited(text, cases)
    quoted = _link_quoted(text, links)
    return _pack(
        [
            _check(
                "Cites a retrieved case",
                bool(cited),
                f"The answer cites {cited}.",
                "This answer does not cite a retrieved case id, diagnosis, or decision." if cases else "No case was retrieved for this run.",
            ),
            _marker(text, "Calls the case a reference", ["reference", "similar", "not this patient", "not a diagnosis"]),
            _check(
                "Quotes a graph link",
                bool(quoted),
                f"The answer quotes {quoted}.",
                "This answer does not quote a retrieved graph link." if links else "No graph link was retrieved for this run.",
            ),
            _marker(text, "Stops short of a confirmed diagnosis", ["not a confirmed", "not certain", "does not confirm", "reference only"]),
        ]
    )


FORMULAS = {
    "Personalization": "The same marker list is checked in both written answers. Each marker that appears passes. Each uniqueness flag passes only when the answer repeats it. The score is passes ÷ checks × 100.",
    "Historical evidence": "Five checks, the same ones for both answers: past-case wording, reference wording, an outcome, a citation of a case that was retrieved, and whether a retrieved case is attached. The score is passes ÷ checks × 100.",
    "Risk sensitivity": "Five checks: the word risk, an escalation word, pain at rest, fainting, and severe breathlessness. The score is passes ÷ checks × 100.",
    "Clinician supervision": "Five phrases: doctor or physician, clinician or licensed, not a substitute, in person, and supervision. A phrase counts only when it appears. The score is passes ÷ checks × 100.",
    "Explainability": "Four checks: a reason word, an evidence word, a word for what the finding does, and a quotation of a retrieved graph link. The score is passes ÷ checks × 100.",
    "Actionability": "Four checks: a test, a follow-up, an action, and a time. The score is passes ÷ checks × 100.",
    "Specialist alignment": "Six checks: ECG, echo, lipids, the preventive frame, a follow-up, and ischemic disease. The score is passes ÷ checks × 100.",
    "Evidence grounding": "Four checks: the answer cites a retrieved case, calls it a reference, quotes a graph link, and stops short of a confirmed diagnosis. The score is passes ÷ checks × 100. This measures traceability, not whether the clinical decision is right.",
}


def _texts(generic: dict, twin: dict) -> tuple[str, str]:
    generic_text = " ".join(
        [
            generic.get("consultation_summary", ""),
            " ".join(generic.get("possible_concerns") or []),
            " ".join(generic.get("suggested_next_steps") or []),
            " ".join(generic.get("risk_notes") or []),
            generic.get("disclaimer", ""),
        ]
    )
    twin_text = " ".join(
        [
            twin.get("assessment", ""),
            " ".join(twin.get("recommended_tests") or []),
            " ".join(twin.get("immediate_actions") or []),
            " ".join(twin.get("follow_up_plan") or []),
            twin.get("disclaimer", ""),
        ]
    )
    return generic_text, twin_text


def _passed_labels(side: dict) -> list[str]:
    return [line["label"] for line in side["lines"] if line["value"]]


def _reason(name: str, winner: str, generic_side: dict, twin_side: dict, signals: dict) -> str:
    if name == "Clinician supervision":
        generic_hits = _passed_labels(generic_side)
        twin_hits = _passed_labels(twin_side)
        generic_text = ", ".join(generic_hits) if generic_hits else "none of the supervision phrases"
        twin_text = ", ".join(twin_hits) if twin_hits else "none of the supervision phrases"
        return (
            f"Generic GPT's written answer contains {generic_text}. "
            f"Doctor's Twin's written answer contains {twin_text}. "
            "A phrase counts only when it is written down."
        )
    if name == "Evidence grounding":
        return (
            f"Doctor's Twin passed {twin_side['passed']} of {twin_side['checks']} traceability checks. "
            f"Generic GPT passed {generic_side['passed']} of {generic_side['checks']}. "
            f"The retrieved evidence on this run is {signals['cases']} case{'s' if signals['cases'] != 1 else ''} and {signals['links']} graph link{'s' if signals['links'] != 1 else ''}. "
            "The score is that share. It is not a rate of correct diagnoses."
        )
    if name == "Personalization":
        if winner == "twin":
            return "Doctor's Twin's written answer contains more of this patient's markers, or it repeats a uniqueness flag the other answer does not."
        if winner == "generic":
            return "Generic GPT's written answer contains more of this patient's markers on this run."
        return "Both written answers cover a similar share of this patient's markers."
    if name == "Historical evidence":
        if winner == "twin":
            return f"Doctor's Twin has {signals['cases']} retrieved case{'s' if signals['cases'] != 1 else ''} and its written answer passes more of the citation checks."
        if winner == "generic":
            return "Generic GPT's written answer passes more of the case-wording checks. Doctor's Twin did not cite a retrieved case on this run."
        return "Neither written answer clearly cites a retrieved case."
    if name == "Risk sensitivity":
        if winner == "twin":
            return "Doctor's Twin's written answer names more of the escalation checks."
        if winner == "generic":
            return "Generic GPT's written answer names more of the escalation checks."
        return "Both written answers pass a similar share of the escalation checks. A missing rest-pain, fainting, or breathlessness line can reassure the wrong person."
    if name == "Explainability":
        if winner == "twin":
            return "Doctor's Twin's written answer gives more checkable reasons, including a quoted graph link when one was retrieved."
        if winner == "generic":
            return "Generic GPT's written answer gives more reason words. Doctor's Twin does not quote a retrieved graph link on this run."
        return "Both written answers pass a similar share of the reason checks."
    if name == "Actionability":
        if winner == "twin":
            return "Doctor's Twin's written answer names more of the test, action, follow-up, and time checks."
        if winner == "generic":
            return "Generic GPT's written answer names more of those next-step checks."
        return "Both written answers name a similar share of the next-step checks."
    if name == "Specialist alignment":
        if winner == "twin":
            return "Doctor's Twin's written answer uses more of this doctor's preventive-cardiology words."
        if winner == "generic":
            return "Generic GPT's written answer uses more of those specialist words on this run."
        return "Both written answers sit at a similar distance from this doctor's preventive frame."
    return ""


def _improve(name: str, twin_score: int, gap: int) -> str:
    if twin_score >= 100:
        return ""
    if twin_score >= 75 and gap >= 10:
        return ""
    if name == "Personalization":
        return "Repeat this patient's age, conditions, and the uniqueness flags in the paragraph, in the same words."
    if name == "Historical evidence":
        return "Name the retrieved case id and its decision, and say it is a reference rather than this patient."
    if name == "Risk sensitivity":
        return "Write one line for pain at rest, fainting, or severe breathlessness."
    if name == "Clinician supervision":
        return "Write that a doctor or clinician still decides, and that the answer is not a substitute for that visit."
    if name == "Explainability":
        return "For one recommendation, write the finding, the graph relation, and the action in the same sentence."
    if name == "Actionability":
        return "Name the test, the action, the follow-up, and when to return."
    if name == "Specialist alignment":
        return "Use the names ECG, echo, lipid, and follow-up when those are the next steps."
    if name == "Evidence grounding":
        return "Put the retrieved case id and the graph link next to the step they support, and say they do not confirm a diagnosis."
    return ""


def _depth(scores: list[int]) -> tuple[int, dict]:
    total = sum(scores)
    count = len(scores)
    raw = total / count if count else 0
    value = (total + (count // 2)) // count if count else 0
    return value, {"sum": total, "count": count, "raw": f"{raw:.2f}", "total": value}


def generate_comparison_metrics(generic, twin):
    generic = generic or {}
    twin = twin or {}
    generic_text, twin_text = _texts(generic, twin)
    signals = _signals(twin)
    links = (twin.get("graph_evidence") or {}).get("links") or []
    built = {
        "Personalization": (_personalization(generic_text, twin), _personalization(twin_text, twin)),
        "Historical evidence": (_historical(generic_text, twin, False), _historical(twin_text, twin, True)),
        "Risk sensitivity": (_risk(generic_text), _risk(twin_text)),
        "Clinician supervision": (_supervision(generic_text), _supervision(twin_text)),
        "Explainability": (_explainability(generic_text, links), _explainability(twin_text, links)),
        "Actionability": (_actionability(generic_text), _actionability(twin_text)),
        "Specialist alignment": (_alignment(generic_text), _alignment(twin_text)),
        "Evidence grounding": (_grounding(generic_text, twin), _grounding(twin_text, twin)),
    }
    factors = []
    generic_scores = []
    twin_scores = []
    for spec in FACTORS:
        generic_side, twin_side = built[spec["name"]]
        generic_score = generic_side["total"]
        twin_score = twin_side["total"]
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
                "reason": _reason(spec["name"], winner, generic_side, twin_side, signals),
                "improve": _improve(spec["name"], twin_score, gap),
                "calculation": {"formula": FORMULAS[spec["name"]], "generic": generic_side, "twin": twin_side},
            }
        )
        generic_scores.append(generic_score)
        twin_scores.append(twin_score)

    by_name = {item["name"]: item for item in factors}
    generic_depth, generic_depth_work = _depth(generic_scores)
    twin_depth, twin_depth_work = _depth(twin_scores)
    return {
        "Personalization Score": by_name["Personalization"]["twin"],
        "Use of Historical Evidence": by_name["Historical evidence"]["twin"],
        "Risk Sensitivity": by_name["Risk sensitivity"]["twin"],
        "Clinician Supervision": by_name["Clinician supervision"]["twin"],
        "Explainability": by_name["Explainability"]["twin"],
        "Actionability": by_name["Actionability"]["twin"],
        "Specialist Alignment": by_name["Specialist alignment"]["twin"],
        "Evidence grounding": by_name["Evidence grounding"]["twin"],
        "Generic Context Depth": generic_depth,
        "Twin Context Depth": twin_depth,
        "traceability_note": TRACEABILITY_NOTE,
        "factors": factors,
        "depth": {"generic": generic_depth_work, "twin": twin_depth_work},
    }
