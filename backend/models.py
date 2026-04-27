from typing import Any, Dict, List
from pydantic import BaseModel, Field


class PatientInput(BaseModel):
    name: str
    age: int = Field(ge=1, le=120)
    gender: str
    height_cm: float = Field(gt=50, lt=260)
    weight_kg: float = Field(gt=20, lt=350)
    symptoms: str
    symptom_duration: str
    medical_history: str
    family_history: str
    lifestyle: str
    current_medications: str
    bp: str
    ldl: float = Field(ge=0, le=400)
    hba1c: float = Field(ge=0, le=20)
    optional_notes: str = ""


class AnalyzeResponse(BaseModel):
    patient_summary: Dict[str, Any]
    generic: Dict[str, Any]
    twin: Dict[str, Any]


class GenericResponse(BaseModel):
    consultation_summary: str
    possible_concerns: List[str]
    suggested_next_steps: List[str]
    risk_notes: List[str]


class TwinResponse(BaseModel):
    assessment: str
    unique_factors: List[str]
    historical_patterns: List[Dict[str, Any]]
    recommended_tests: List[str]
    immediate_actions: List[str]
    follow_up_plan: List[str]
    confidence_score: float


class CasesResponse(BaseModel):
    matches: List[Dict[str, Any]]


class GraphResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    evidence_summary: List[str]
