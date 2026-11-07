"""Links taken only from retrieved case rows.

A link is added when a symptom or risk written on that case also appears in
this patient's text, and the case records a decision. The case id stays on
the link so the answer can be traced. Nothing is added that the row does not say.
"""

from __future__ import annotations


def _parts(value: str) -> list[str]:
    return [part.strip() for part in str(value or "").split(",") if part.strip()]


def history_links(patient_text: str, cases: list[dict] | None, limit: int = 8) -> list[dict]:
    folded = (patient_text or "").lower()
    links: list[dict] = []
    seen: set[tuple] = set()
    for case in cases or []:
        if len(links) >= limit:
            break
        case_id = str(case.get("case_id") or "").strip()
        decision = str(case.get("decision") or case.get("treatment_decision") or "").strip()
        if not decision:
            continue
        matched = ""
        relation = ""
        for symptom in _parts(case.get("symptoms") or ""):
            if symptom.lower() in folded:
                matched = symptom
                relation = "observation_relates_to"
                break
        if not matched:
            for risk in _parts(case.get("risk_factors") or ""):
                if risk.lower() in folded:
                    matched = risk
                    relation = "risk_relates_to"
                    break
        if not matched:
            continue
        key = (matched.lower(), decision.lower(), case_id)
        if key in seen:
            continue
        seen.add(key)
        links.append(
            {
                "source": matched,
                "target": decision,
                "relation": relation,
                "weight": 1.0,
                "case_id": case_id,
            }
        )
    return links


def evidence_line(link: dict) -> str:
    case_id = link.get("case_id") or ""
    provenance = f" [case {case_id}]" if case_id else ""
    return f"{link['source']} -> {link['target']} ({link['relation']}){provenance}"
