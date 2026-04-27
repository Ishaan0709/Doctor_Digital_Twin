from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from openai import OpenAI

from config import DATA_RAW_DIR, OPENAI_API_KEY, OPENAI_MODEL, PROMPTS_DIR
from graph_rag.build_graph import build_knowledge_graph, graph_as_payload
from graph_rag.reasoning import graph_reasoning
from rag.rerank import rerank_cases
from rag.retrieve import retrieve_similar_cases
from twin_engine.personalization import extract_uniqueness_flags
from twin_engine.twin_prompt import build_twin_prompt


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


def _load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def _safe_openai_chat(system_prompt: str, user_prompt: str) -> str:
    if not OPENAI_API_KEY:
        return "OpenAI API key not configured. Add OPENAI_API_KEY in .env to enable live AI generation."
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.2,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        return f"AI generation temporarily unavailable: {exc}"


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
    return {"patient": patient["name"], "age": patient["age"], "bmi": round(bmi, 1), "risk_markers": {"BP": patient["bp"], "LDL": patient["ldl"], "HbA1c": patient["hba1c"]}}


def generate_generic_consultation(patient: Dict[str, Any]) -> Dict[str, Any]:
    patient_text = patient_to_text(patient)
    narrative = _safe_openai_chat(_load_prompt("generic_gpt.txt"), patient_text)
    return {
        "consultation_summary": narrative,
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


def generate_twin_consultation(patient: Dict[str, Any]) -> Dict[str, Any]:
    patient_text = patient_to_text(patient)
    retrieved = rerank_cases(retrieve_similar_cases(patient_text, top_k=5), patient_text)
    graph = build_knowledge_graph()
    graph_result = graph_reasoning(patient_text, graph)
    uniqueness_flags = extract_uniqueness_flags(patient)

    retrieved_text = "\n".join([f"Case {c.get('case_id')}: Dx {c.get('diagnosis')} | Decision {c.get('decision')} | Outcome {c.get('outcome')}" for c in retrieved])
    prompt = build_twin_prompt(patient_text, retrieved_text, "\n".join(graph_result["evidence_summary"]), "\n".join(uniqueness_flags))
    assessment = _safe_openai_chat(_load_prompt("doctor_twin.txt"), prompt)
    confidence = confidence_breakdown(len(retrieved), len(graph_result["links"]))

    return {
        "assessment": assessment,
        "unique_factors": uniqueness_flags,
        "historical_patterns": retrieved,
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
        "confidence_score": confidence["final_score"],
        "confidence_breakdown": confidence,
        "graph_evidence": graph_result,
        "graph_payload": graph_as_payload(graph),
    }


def generate_followup_reply(mode: str, patient: Dict[str, Any], user_question: str, twin: Optional[Dict[str, Any]] = None) -> str:
    """
    mode: "general" or "specialist"
    Returns a single assistant message continuing the consultation.
    """
    patient_text = patient_to_text(patient)
    if mode == "specialist":
        twin_context = ""
        if twin:
            twin_context = (
                "Specialist assessment:\n"
                f"{twin.get('assessment', '')}\n\n"
                "Immediate actions:\n"
                + "\n".join([f"- {x}" for x in twin.get("immediate_actions", [])])
                + "\n\nFollow-up plan:\n"
                + "\n".join([f"- {x}" for x in twin.get("follow_up_plan", [])])
            )
        system = (
            "You are Dr. Vimlesh Pandey's AI Specialist Twin. "
            "Write in a calm, professional clinical tone. "
            "Be patient-first, explain reasoning simply, and be precise. "
            "Never claim certainty; include safety escalation advice when needed. "
            "Do not mention GPT or OpenAI. "
            "If a clinician is required, clearly say so."
        )
        user = f"{patient_text}\n\n{twin_context}\n\nPatient question:\n{user_question}"
        return _safe_openai_chat(system, user)

    system = (
        "You are a general medical AI assistant for decision-support. "
        "Write in a clear, friendly, non-alarming tone. "
        "Explain step-by-step, but keep it practical. "
        "Never mention GPT or OpenAI. "
        "Always include: when to seek urgent care if symptoms suggest an emergency."
    )
    user = f"{patient_text}\n\nPatient question:\n{user_question}"
    return _safe_openai_chat(system, user)


def get_case_matches(patient: Dict[str, Any]) -> List[Dict[str, Any]]:
    return retrieve_similar_cases(patient_to_text(patient), top_k=8)


def get_graph_payload(patient: Dict[str, Any]) -> Dict[str, Any]:
    graph = build_knowledge_graph()
    reasoning = graph_reasoning(patient_to_text(patient), graph)
    payload = graph_as_payload(graph)
    payload["evidence_summary"] = reasoning["evidence_summary"]
    return payload


def dataset_stats() -> Dict[str, int]:
    def count_rows(name: str) -> int:
        path = DATA_RAW_DIR / name
        if not path.exists():
            return 0
        try:
            return len(pd.read_csv(path))
        except Exception:
            return 0

    return {
        "doctor_cases": count_rows("doctor_cases_vimlesh_pandey.csv"),
        "patient_profiles": count_rows("patient_profiles.csv"),
        "graph_nodes": count_rows("graph_nodes.csv"),
        "graph_edges": count_rows("graph_edges.csv"),
    }
