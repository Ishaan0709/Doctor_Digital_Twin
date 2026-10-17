import pytest
from fastapi.testclient import TestClient

PATIENT = {
    "name": "Aarav Mehta",
    "age": 52,
    "gender": "Male",
    "height_cm": 170,
    "weight_kg": 78,
    "symptoms": "Exertional chest pain radiating to left arm",
    "symptom_duration": "2 weeks",
    "medical_history": "Type 2 diabetes, hypertension",
    "family_history": "Father had MI at 54",
    "lifestyle": "Smoker, sedentary",
    "current_medications": "Metformin, Amlodipine",
    "bp": "154/96",
    "ldl": 186,
    "hba1c": 8.4,
    "optional_notes": "Anxious about symptoms",
}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr("backend.utils._safe_openai_chat", lambda *_a, **_k: "Grounded test assessment citing case 1.")
    monkeypatch.setattr("backend.utils.iter_openai_chat", lambda *_a, **_k: iter(["Hello ", "clinician"]))
    monkeypatch.setattr(
        "backend.utils.retrieve_similar_cases",
        lambda *_a, **_k: [
            {
                "case_id": "1",
                "symptoms": "chest pain",
                "risk_factors": "diabetes",
                "tests": "ECG",
                "diagnosis": "possible CAD",
                "decision": "ECG",
                "outcome": "improved",
                "match_score": 0.82,
            }
        ],
    )
    from backend.app import app

    with TestClient(app) as test_client:
        yield test_client


def test_eval_results_shape(client):
    body = client.get("/api/eval/results").json()
    assert body["holdout_size"] == 30 or body.get("available") is True
    assert "summary" in body


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_datasets(client):
    response = client.get("/api/datasets")
    assert response.status_code == 200
    body = response.json()
    assert body["stats"]["doctor_cases"] > 0
    assert len(body["registry"]) == 6


def test_validation_message(client):
    response = client.post("/api/consult/generic", json={"name": ""})
    assert response.status_code == 422
    assert "Please check the form" in response.json()["detail"]


def test_generic_and_twin_shape(client):
    generic = client.post("/api/consult/generic", json=PATIENT)
    assert generic.status_code == 200
    assert "case 1" in generic.json()["consultation_summary"]
    assert generic.json()["disclaimer"]
    assert generic.json()["sources"][0]["type"] == "patient"

    twin = client.post("/api/consult/twin", json=PATIENT)
    assert twin.status_code == 200
    body = twin.json()
    assert body["confidence_score"] > 0
    assert body["sources"][0]["id"] == "1"
    assert body["historical_patterns"]
    assert "not a substitute" in body["disclaimer"]


def test_stream_generic(client):
    response = client.post("/api/consult/stream", json={"kind": "generic", "patient": PATIENT})
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert "Hello" in response.text
    assert "clinician" in response.text


def test_compare_and_summary(client):
    summary = client.post("/api/patient/summary", json=PATIENT)
    assert summary.status_code == 200
    assert summary.json()["bmi"] > 0

    compared = client.post(
        "/api/compare",
        json={
            "generic": {"consultation_summary": "basic risk", "possible_concerns": [], "suggested_next_steps": []},
            "twin": {
                "assessment": "patient historical case evidence follow-up",
                "recommended_tests": ["ECG"],
                "immediate_actions": ["monitor"],
                "follow_up_plan": ["review"],
                "historical_patterns": [{"case_id": "1"}],
                "graph_evidence": {"links": [{"source": "a", "target": "b"}]},
                "unique_factors": ["ldl"],
            },
        },
    )
    assert compared.status_code == 200
    assert "Personalization Score" in compared.json()["metrics"]


def test_followup_and_cases(client):
    cases = client.post("/api/evidence/cases", json=PATIENT)
    assert cases.status_code == 200
    assert cases.json()["matches"][0]["case_id"] == "1"

    follow = client.post(
        "/api/consult/followup",
        json={"mode": "general", "patient": PATIENT, "user_question": "Is this urgent?"},
    )
    assert follow.status_code == 200
    assert follow.json()["reply"]
    assert follow.json()["disclaimer"]
