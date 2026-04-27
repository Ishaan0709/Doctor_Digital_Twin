from fastapi import APIRouter, HTTPException

from backend.models import AnalyzeResponse, CasesResponse, GenericResponse, GraphResponse, PatientInput, TwinResponse
from backend.utils import generate_generic_consultation, generate_twin_consultation, get_case_matches, get_graph_payload, summarize_patient

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "CardioTwin AI"}


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: PatientInput):
    patient = payload.model_dump()
    try:
        return {
            "patient_summary": summarize_patient(patient),
            "generic": generate_generic_consultation(patient),
            "twin": generate_twin_consultation(patient),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/generic", response_model=GenericResponse)
def generic(payload: PatientInput):
    return generate_generic_consultation(payload.model_dump())


@router.post("/twin", response_model=TwinResponse)
def twin(payload: PatientInput):
    return generate_twin_consultation(payload.model_dump())


@router.post("/graph", response_model=GraphResponse)
def graph(payload: PatientInput):
    result = get_graph_payload(payload.model_dump())
    return {"nodes": result.get("nodes", []), "edges": result.get("edges", []), "evidence_summary": result.get("evidence_summary", [])}


@router.post("/cases", response_model=CasesResponse)
def cases(payload: PatientInput):
    return {"matches": get_case_matches(payload.model_dump())}
