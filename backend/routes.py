import json
from typing import Any, Dict, Iterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.context import DISCLAIMER, clarifying_questions, dataset_counts, dataset_registry, list_cases, list_profiles, list_timeline
from backend.models import (
    AnalyzeResponse,
    CasesResponse,
    CompareRequest,
    FollowupRequest,
    FollowupResponse,
    GenericResponse,
    GraphResponse,
    PatientInput,
    StreamRequest,
    TwinResponse,
)
from backend.utils import (
    generate_followup_reply,
    generate_generic_consultation,
    generate_twin_consultation,
    get_case_matches,
    get_graph_payload,
    iter_openai_chat,
    prepare_generic_bundle,
    prepare_twin_bundle,
    summarize_patient,
)
from config import BASE_DIR
from twin_engine.compare_engine import generate_comparison_metrics
from twin_engine.doctor_profile import DOCTOR_PROFILE

router = APIRouter()


def _patient(payload: PatientInput) -> Dict[str, Any]:
    return payload.model_dump()


def _guard(fn, patient: Dict[str, Any]):
    try:
        return fn(patient)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Consultation failed: {exc}") from exc


def _sse(payload: Dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False, default=str)}\n\n"


def _public_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    hidden = {"system_prompt", "user_prompt"}
    return {key: value for key, value in bundle.items() if key not in hidden}


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "CardioTwin AI"}


@router.get("/api/health")
def api_health() -> dict:
    counts = dataset_counts()
    return {"status": "ok", "service": "CardioTwin AI", "datasets": counts}


@router.get("/api/bootstrap")
def bootstrap() -> dict:
    return {
        "doctor": DOCTOR_PROFILE,
        "disclaimer": DISCLAIMER,
        "datasets": dataset_counts(),
        "registry": dataset_registry(),
    }


@router.get("/api/datasets")
def datasets() -> dict:
    return {"stats": dataset_counts(), "registry": dataset_registry()}


@router.get("/api/patients")
def patients() -> dict:
    return {"patients": list_profiles()}


@router.get("/api/patients/{patient_id}/timeline")
def patient_timeline(patient_id: str) -> dict:
    return {"patient_id": patient_id, "timeline": list_timeline(patient_id)}


@router.get("/api/cases/catalog")
def case_catalog() -> dict:
    return {"cases": list_cases()}


@router.post("/api/patient/summary")
def patient_summary(payload: PatientInput) -> dict:
    return summarize_patient(_patient(payload))


@router.post("/analyze", response_model=AnalyzeResponse)
@router.post("/api/consult/analyze", response_model=AnalyzeResponse)
def analyze(payload: PatientInput):
    patient = _patient(payload)
    try:
        generic = _public_bundle(generate_generic_consultation(patient))
        twin = _public_bundle(generate_twin_consultation(patient))
        return {"patient_summary": summarize_patient(patient), "generic": generic, "twin": twin}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Consultation failed: {exc}") from exc


@router.post("/generic", response_model=GenericResponse)
@router.post("/api/consult/generic", response_model=GenericResponse)
def generic(payload: PatientInput):
    return _public_bundle(_guard(generate_generic_consultation, _patient(payload)))


@router.post("/twin", response_model=TwinResponse)
@router.post("/api/consult/twin", response_model=TwinResponse)
def twin(payload: PatientInput):
    return _public_bundle(_guard(generate_twin_consultation, _patient(payload)))


@router.post("/graph", response_model=GraphResponse)
@router.post("/api/evidence/graph", response_model=GraphResponse)
def graph(payload: PatientInput):
    result = _guard(get_graph_payload, _patient(payload))
    return {"nodes": result.get("nodes", []), "edges": result.get("edges", []), "evidence_summary": result.get("evidence_summary", [])}


@router.post("/cases", response_model=CasesResponse)
@router.post("/api/evidence/cases", response_model=CasesResponse)
def cases(payload: PatientInput):
    return {"matches": _guard(get_case_matches, _patient(payload))}


@router.post("/api/consult/followup", response_model=FollowupResponse)
def followup(payload: FollowupRequest):
    patient = _patient(payload.patient)
    try:
        reply = generate_followup_reply(
            payload.mode,
            patient,
            payload.user_question,
            twin=payload.twin,
            history=[turn.model_dump() for turn in payload.history],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Consultation failed: {exc}") from exc
    sources = []
    if payload.mode == "specialist" and payload.twin:
        for case in payload.twin.get("historical_patterns", []):
            sources.append(
                {
                    "type": "case",
                    "id": str(case.get("case_id", "")),
                    "diagnosis": case.get("diagnosis", ""),
                    "score": case.get("final_match_score", case.get("match_score")),
                }
            )
    else:
        sources.append({"type": "patient", "text": "General consultation uses the current intake only."})
    return {
        "reply": reply,
        "disclaimer": DISCLAIMER,
        "sources": sources,
        "clarifying_questions": clarifying_questions(patient),
    }


@router.post("/api/compare")
def compare(payload: CompareRequest) -> dict:
    try:
        report = generate_comparison_metrics(payload.generic, payload.twin)
        factors = report.pop("factors")
        depth = report.pop("depth")
        note = report.pop("traceability_note", "")
        return {"metrics": report, "factors": factors, "depth": depth, "traceability_note": note}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {exc}") from exc


@router.get("/api/eval/results")
def eval_results() -> dict:
    path = BASE_DIR / "eval" / "results.json"
    if not path.is_file():
        return {"available": False, "holdout_size": 30, "summary": None}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "available": True,
        "holdout_size": data.get("holdout_size", 0),
        "seed": data.get("seed"),
        "source": data.get("source", ""),
        "summary": data.get("summary"),
        "gold": data.get("gold"),
        "judge": data.get("judge"),
        "systems": data.get("systems"),
    }


@router.post("/api/consult/stream")
def consult_stream(payload: StreamRequest):
    patient = _patient(payload.patient)

    def events() -> Iterator[str]:
        try:
            if payload.kind == "generic":
                bundle = prepare_generic_bundle(patient)
                yield _sse({"type": "meta", "result": _public_bundle(bundle)})
                parts: list[str] = []
                for token in iter_openai_chat(bundle["system_prompt"], bundle["user_prompt"]):
                    parts.append(token)
                    yield _sse({"type": "token", "text": token})
                yield _sse({"type": "done", "text": "".join(parts), "field": "consultation_summary"})
                return

            if payload.kind == "twin":
                bundle = prepare_twin_bundle(patient)
                yield _sse({"type": "meta", "result": _public_bundle(bundle)})
                parts = []
                for token in iter_openai_chat(bundle["system_prompt"], bundle["user_prompt"]):
                    parts.append(token)
                    yield _sse({"type": "token", "text": token})
                yield _sse({"type": "done", "text": "".join(parts), "field": "assessment"})
                return

            if payload.kind == "followup":
                if not payload.user_question.strip():
                    yield _sse({"type": "error", "detail": "Type a follow-up question first."})
                    return
                history = [turn.model_dump() for turn in payload.history]
                # Build the same prompt the non-streaming path uses, then stream it.
                from backend.utils import _history_block, patient_to_text
                from backend.context import style_rules_text, timeline_context

                questions = clarifying_questions(patient)
                if payload.mode == "specialist":
                    twin = payload.twin or {}
                    case_lines = "\n".join(
                        f"Case {c.get('case_id')}: {c.get('diagnosis')} | {c.get('decision')} | {c.get('outcome')}"
                        for c in twin.get("historical_patterns", [])
                    )
                    system = (
                        "You are Dr. Vimlesh Pandey's AI Specialist Twin. "
                        "Write in a calm, professional clinical tone. Be patient-first and precise. "
                        "Never claim certainty. Do not mention GPT or OpenAI. "
                        "Cite case ids when you use historical patterns. Ask a clarifying question if needed. "
                        f"Doctor style rules:\n{style_rules_text()}\n{DISCLAIMER}"
                    )
                    user = (
                        f"{patient_to_text(patient)}\n\n{timeline_context(patient.get('profile_id'))}\n\n"
                        f"Specialist assessment:\n{twin.get('assessment', '')}\n\n"
                        f"Historical cases:\n{case_lines or 'None'}\n\n"
                        f"{_history_block(history)}\n\nPatient question:\n{payload.user_question}"
                    )
                    sources = [
                        {"type": "case", "id": str(c.get("case_id", "")), "diagnosis": c.get("diagnosis", "")}
                        for c in twin.get("historical_patterns", [])
                    ]
                else:
                    system = (
                        "You are a general medical AI assistant for decision-support. "
                        "Be clear, practical, and non-alarming. Do not mention GPT or OpenAI. "
                        "Do not use historical specialist cases. "
                        "Say when to seek urgent care. Ask a clarifying question if information is missing. "
                        f"{DISCLAIMER}"
                    )
                    user = f"{patient_to_text(patient)}\n\n{_history_block(history)}\n\nPatient question:\n{payload.user_question}"
                    sources = [{"type": "patient", "text": "General consultation uses the current intake only."}]
                yield _sse({"type": "meta", "sources": sources, "disclaimer": DISCLAIMER, "clarifying_questions": questions})
                parts = []
                for token in iter_openai_chat(system, user):
                    parts.append(token)
                    yield _sse({"type": "token", "text": token})
                yield _sse({"type": "done", "text": "".join(parts), "field": "reply"})
                return

            yield _sse({"type": "error", "detail": "Unknown consultation type."})
        except Exception as exc:
            yield _sse({"type": "error", "detail": f"Consultation failed: {exc}"})

    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
