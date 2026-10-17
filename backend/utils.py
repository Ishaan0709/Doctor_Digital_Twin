from typing import Any, Dict, Iterator, List, Optional

from openai import OpenAI

from backend.context import (
    DISCLAIMER,
    clarifying_questions,
    dataset_counts,
    profile_context,
    style_rules_text,
    timeline_context,
)
from config import OPENAI_API_KEY, OPENAI_MODEL
from graph_rag.build_graph import get_cached_graph, graph_as_payload
from graph_rag.reasoning import graph_reasoning
from rag.rerank import rerank_cases
from rag.retrieve import retrieve_similar_cases
from twin_engine.personalization import extract_uniqueness_flags
from twin_engine.twin_prompt import build_twin_prompt, load_prompt

_CLIENT: Optional[OpenAI] = None


def confidence_breakdown(retrieved_count: int, graph_link_count: int) -> Dict[str, Any]:
    base = 0.60
    retrieval_component = 0.07 * retrieved_count
    graph_component = 0.03 * graph_link_count
    raw = base + retrieval_component + graph_component
    final = round(min(0.98, raw), 2)
    return {
        "base": round(base, 2),
        "retrieval_component": round(retrieval_component, 2),
        "graph_component": round(graph_component, 2),
        "raw_score": round(raw, 2),
        "final_score": final,
    }


def _client() -> OpenAI:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = OpenAI(api_key=OPENAI_API_KEY)
    return _CLIENT


def _safe_openai_chat(system_prompt: str, user_prompt: str) -> str:
    if not OPENAI_API_KEY:
        return "OpenAI API key not configured. Add OPENAI_API_KEY in .env to enable live AI generation."
    try:
        response = _client().chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.2,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        return f"AI generation temporarily unavailable: {exc}"


def iter_openai_chat(system_prompt: str, user_prompt: str) -> Iterator[str]:
    if not OPENAI_API_KEY:
        yield "OpenAI API key not configured. Add OPENAI_API_KEY in .env to enable live AI generation."
        return
    try:
        stream = _client().chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.2,
            stream=True,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        )
        for chunk in stream:
            if not chunk.choices:
                continue
            text = chunk.choices[0].delta.content
            if text:
                yield text
    except Exception as exc:
        yield f"AI generation temporarily unavailable: {exc}"


def patient_to_text(patient: Dict[str, Any]) -> str:
    return (
        f"Name: {patient.get('name')}\nAge: {patient.get('age')}\nGender: {patient.get('gender')}\n"
        f"Height(cm): {patient.get('height_cm')} Weight(kg): {patient.get('weight_kg')}\n"
        f"Symptoms: {patient.get('symptoms')}\nDuration: {patient.get('symptom_duration')}\n"
        f"Medical history: {patient.get('medical_history')}\nFamily history: {patient.get('family_history')}\n"
        f"Lifestyle: {patient.get('lifestyle')}\nCurrent medications: {patient.get('current_medications')}\n"
        f"BP: {patient.get('bp')} LDL: {patient.get('ldl')} HbA1c: {patient.get('hba1c')}\nOptional notes: {patient.get('optional_notes', '')}"
    )


def summarize_patient(patient: Dict[str, Any]) -> Dict[str, Any]:
    bmi = float(patient["weight_kg"]) / max((float(patient["height_cm"]) / 100.0) ** 2, 0.1)
    return {
        "patient": patient["name"],
        "age": patient["age"],
        "bmi": round(bmi, 1),
        "risk_markers": {"BP": patient["bp"], "LDL": patient["ldl"], "HbA1c": patient["hba1c"]},
    }


def _case_line(case: Dict[str, Any]) -> str:
    score = case.get("final_match_score", case.get("match_score", 0))
    try:
        score_text = f"{float(score):.2f}"
    except (TypeError, ValueError):
        score_text = "NA"
    return (
        f"Case {case.get('case_id')} | similarity {score_text} | "
        f"Symptoms: {case.get('symptoms')} | Risks: {case.get('risk_factors')} | "
        f"Tests: {case.get('tests')} | Dx: {case.get('diagnosis')} | "
        f"Decision: {case.get('decision')} | Outcome: {case.get('outcome')}"
    )


def _sources_from_cases(cases: List[Dict[str, Any]], graph_lines: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    sources: List[Dict[str, Any]] = []
    for case in cases:
        sources.append(
            {
                "type": "case",
                "id": str(case.get("case_id", "")),
                "diagnosis": case.get("diagnosis", ""),
                "decision": case.get("decision", ""),
                "outcome": case.get("outcome", ""),
                "score": case.get("final_match_score", case.get("match_score")),
            }
        )
    for line in graph_lines or []:
        sources.append({"type": "graph", "text": line})
    return sources


def _generic_lists() -> Dict[str, List[str]]:
    return {
        "possible_concerns": [
            "Possible ischemic symptoms requiring proper triage.",
            "Cardiometabolic burden from LDL/HbA1c may elevate long-term risk.",
            "Family-history and lifestyle factors may compound baseline risk.",
        ],
        "suggested_next_steps": [
            "Obtain ECG and baseline cardiac enzymes where clinically indicated.",
            "Assess blood pressure trend and optimize risk-factor control.",
            "Arrange physician follow-up for risk stratification and test planning.",
        ],
        "risk_notes": [
            "Guidance is informational and should be validated by a licensed clinician.",
            "Escalate immediately if chest pain worsens, rest pain appears, or dyspnea increases.",
        ],
    }


def prepare_generic_bundle(patient: Dict[str, Any]) -> Dict[str, Any]:
    questions = clarifying_questions(patient)
    profile = profile_context(patient.get("profile_id"))
    timeline = timeline_context(patient.get("profile_id"))
    weighing = load_prompt("patient_summary.txt").strip()
    user_prompt = patient_to_text(patient)
    if profile:
        user_prompt += "\n\n" + profile
    user_prompt += f"\n\nTimeline context:\n{timeline}\n\nHow to weigh this patient:\n{weighing}"
    if questions:
        user_prompt += "\n\nPlease ask these clarifying questions as well:\n" + "\n".join(f"- {q}" for q in questions)
    user_prompt += f"\n\n{DISCLAIMER}"
    payload = {
        "consultation_summary": "",
        "system_prompt": load_prompt("generic_gpt.txt"),
        "user_prompt": user_prompt,
        "clarifying_questions": questions,
        "disclaimer": DISCLAIMER,
        "sources": [{"type": "patient", "text": "Current patient intake only. Historical cases were not used."}],
        "timeline_context": timeline,
    }
    payload.update(_generic_lists())
    return payload


def generate_generic_consultation(patient: Dict[str, Any]) -> Dict[str, Any]:
    bundle = prepare_generic_bundle(patient)
    narrative = _safe_openai_chat(bundle["system_prompt"], bundle["user_prompt"])
    bundle["consultation_summary"] = narrative
    return bundle


def _twin_plan_lists() -> Dict[str, List[str]]:
    return {
        "recommended_tests": [
            "12-lead ECG and high-sensitivity troponin if active chest symptoms.",
            "2D Echo for structural and functional baseline.",
            "Stress imaging / TMT where symptom pattern and risk profile support ischemia workup.",
            "Fasting lipid profile and renal panel before medication adjustment.",
        ],
        "immediate_actions": [
            "Prioritize symptom safety triage and red-flag counseling.",
            "Start or optimize preventive risk control in clinician-supervised plan.",
            "Reconcile medications for conflict and adherence.",
        ],
        "follow_up_plan": [
            "Follow-up within 3-7 days for response and risk review.",
            "Escalate earlier if rest pain, syncope, or worsening dyspnea appears.",
            "Reassess LDL/HbA1c trajectory and prevention targets in 6-12 weeks.",
        ],
    }


def prepare_twin_bundle(patient: Dict[str, Any], exclude_ids=None) -> Dict[str, Any]:
    patient_text = patient_to_text(patient)
    profile = profile_context(patient.get("profile_id"))
    if profile:
        patient_text += "\n\n" + profile
    timeline = timeline_context(patient.get("profile_id"))
    questions = clarifying_questions(patient)
    retrieved = rerank_cases(retrieve_similar_cases(patient_text, top_k=5, exclude_ids=exclude_ids), patient_text)
    graph = get_cached_graph()
    graph_result = graph_reasoning(patient_text, graph)
    uniqueness_flags = extract_uniqueness_flags(patient)
    retrieved_text = "\n".join(_case_line(case) for case in retrieved) or "No similar cases retrieved."
    prompt = build_twin_prompt(
        patient_text,
        retrieved_text,
        "\n".join(graph_result["evidence_summary"]),
        "\n".join(uniqueness_flags),
        style_rules=style_rules_text(),
        timeline_context=timeline,
        clarifying_questions="\n".join(f"- {q}" for q in questions) if questions else "None flagged from empty fields.",
        patient_weighing=load_prompt("patient_summary.txt").strip(),
        reasoning_guidance=load_prompt("graph_reasoning.txt").strip(),
    )
    system = (
        "You are Dr. Vimlesh Pandey's specialist digital twin for preventive cardiology. "
        "Follow the doctor style rules in the user message. "
        "Current patient first. Historical cases are references only. "
        f"{DISCLAIMER}"
    )
    confidence = confidence_breakdown(len(retrieved), len(graph_result["links"]))
    payload = {
        "assessment": "",
        "unique_factors": uniqueness_flags,
        "historical_patterns": retrieved,
        "confidence_score": confidence["final_score"],
        "confidence_breakdown": confidence,
        "graph_evidence": graph_result,
        "sources": _sources_from_cases(retrieved, graph_result.get("evidence_summary", [])),
        "clarifying_questions": questions,
        "disclaimer": DISCLAIMER,
        "timeline_context": timeline,
        "system_prompt": system,
        "user_prompt": prompt,
    }
    payload.update(_twin_plan_lists())
    return payload


def generate_twin_consultation(patient: Dict[str, Any], exclude_ids=None) -> Dict[str, Any]:
    bundle = prepare_twin_bundle(patient, exclude_ids=exclude_ids)
    bundle["assessment"] = _safe_openai_chat(bundle["system_prompt"], bundle["user_prompt"])
    return bundle


def _history_block(history: Optional[List[Dict[str, str]]]) -> str:
    if not history:
        return ""
    lines = []
    for turn in history[-8:]:
        lines.append(f"{turn.get('role', 'user')}: {turn.get('content', '')}")
    return "Conversation so far:\n" + "\n".join(lines)


def generate_followup_reply(
    mode: str,
    patient: Dict[str, Any],
    user_question: str,
    twin: Optional[Dict[str, Any]] = None,
    history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    mode: "general" or "specialist"
    Returns a single assistant message continuing the consultation.
    """
    patient_text = patient_to_text(patient)
    questions = clarifying_questions(patient)
    extra = _history_block(history)
    question_block = "\n".join(f"- {q}" for q in questions)
    if mode == "specialist":
        twin_context = ""
        if twin:
            case_lines = "\n".join(_case_line(case) for case in twin.get("historical_patterns", []))
            twin_context = (
                "Specialist assessment:\n"
                f"{twin.get('assessment', '')}\n\n"
                "Immediate actions:\n"
                + "\n".join([f"- {x}" for x in twin.get("immediate_actions", [])])
                + "\n\nFollow-up plan:\n"
                + "\n".join([f"- {x}" for x in twin.get("follow_up_plan", [])])
                + "\n\nHistorical cases already retrieved:\n"
                + (case_lines or "None")
            )
        system = (
            "You are Dr. Vimlesh Pandey's AI Specialist Twin. "
            "Write in a calm, professional clinical tone. "
            "Be patient-first, explain reasoning simply, and be precise. "
            "Never claim certainty; include safety escalation advice when needed. "
            "Do not mention GPT or OpenAI. "
            "If a clinician is required, clearly say so. "
            "Cite case ids when you rely on the retrieved historical patterns. "
            "If information is missing, ask a short clarifying question. "
            f"Doctor style rules:\n{style_rules_text()}\n{DISCLAIMER}"
        )
        user = (
            f"{patient_text}\n\n{timeline_context(patient.get('profile_id'))}\n\n{twin_context}\n\n"
            f"{extra}\n\nClarifying gaps:\n{question_block or 'None'}\n\nPatient question:\n{user_question}"
        )
        return _safe_openai_chat(system, user)

    system = (
        "You are a general medical AI assistant for decision-support. "
        "Write in a clear, friendly, non-alarming tone. "
        "Explain step-by-step, but keep it practical. "
        "Never mention GPT or OpenAI. "
        "Do not use historical specialist cases in this mode. "
        "Always include: when to seek urgent care if symptoms suggest an emergency. "
        "If information is missing, ask a short clarifying question. "
        f"{DISCLAIMER}"
    )
    user = f"{patient_text}\n\n{extra}\n\nClarifying gaps:\n{question_block or 'None'}\n\nPatient question:\n{user_question}"
    return _safe_openai_chat(system, user)


def get_case_matches(patient: Dict[str, Any]) -> List[Dict[str, Any]]:
    return retrieve_similar_cases(patient_to_text(patient), top_k=8)


def get_graph_payload(patient: Dict[str, Any]) -> Dict[str, Any]:
    graph = get_cached_graph()
    reasoning = graph_reasoning(patient_to_text(patient), graph)
    payload = graph_as_payload(graph)
    payload["evidence_summary"] = reasoning["evidence_summary"]
    return payload


def dataset_stats() -> Dict[str, int]:
    return dataset_counts()
