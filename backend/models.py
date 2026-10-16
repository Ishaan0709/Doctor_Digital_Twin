from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class PatientInput(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    age: int = Field(ge=1, le=120)
    gender: str = Field(min_length=1, max_length=40)
    height_cm: float = Field(ge=50, le=260)
    weight_kg: float = Field(ge=20, le=350)
    symptoms: str = ""
    symptom_duration: str = ""
    medical_history: str = ""
    family_history: str = ""
    lifestyle: str = ""
    current_medications: str = ""
    bp: str = ""
    ldl: float = Field(ge=0, le=400)
    hba1c: float = Field(ge=0, le=20)
    optional_notes: str = ""
    profile_id: Optional[str] = None


class GenericResponse(BaseModel):
    consultation_summary: str
    possible_concerns: List[str]
    suggested_next_steps: List[str]
    risk_notes: List[str]
    clarifying_questions: List[str] = []
    disclaimer: str = ""
    sources: List[Dict[str, Any]] = []


class TwinResponse(BaseModel):
    assessment: str
    unique_factors: List[str]
    historical_patterns: List[Dict[str, Any]]
    recommended_tests: List[str]
    immediate_actions: List[str]
    follow_up_plan: List[str]
    confidence_score: float
    confidence_breakdown: Dict[str, Any] = {}
    graph_evidence: Dict[str, Any] = {}
    sources: List[Dict[str, Any]] = []
    clarifying_questions: List[str] = []
    disclaimer: str = ""
    timeline_context: str = ""


class AnalyzeResponse(BaseModel):
    patient_summary: Dict[str, Any]
    generic: GenericResponse
    twin: TwinResponse


class CasesResponse(BaseModel):
    matches: List[Dict[str, Any]]


class GraphResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    evidence_summary: List[str]


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=20000)


class FollowupRequest(BaseModel):
    mode: Literal["general", "specialist"] = "general"
    patient: PatientInput
    user_question: str = Field(min_length=1, max_length=4000)
    twin: Optional[Dict[str, Any]] = None
    history: List[ChatTurn] = []


class FollowupResponse(BaseModel):
    reply: str
    disclaimer: str
    sources: List[Dict[str, Any]] = []
    clarifying_questions: List[str] = []


class StreamRequest(BaseModel):
    kind: Literal["generic", "twin", "followup"]
    patient: PatientInput
    user_question: str = ""
    twin: Optional[Dict[str, Any]] = None
    history: List[ChatTurn] = []
    mode: Literal["general", "specialist"] = "general"


class CompareRequest(BaseModel):
    generic: Dict[str, Any]
    twin: Dict[str, Any]
