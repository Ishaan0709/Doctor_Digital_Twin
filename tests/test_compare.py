from twin_engine.compare_engine import generate_comparison_metrics


def test_compare_metrics_has_keys():
    metrics = generate_comparison_metrics(
        {"consultation_summary": "basic", "possible_concerns": [], "suggested_next_steps": []},
        {"assessment": "patient risk preventive case evidence test follow-up", "recommended_tests": ["ECG"], "immediate_actions": [], "follow_up_plan": []},
    )
    assert "Personalization Score" in metrics
    assert "Specialist Alignment" in metrics
    assert "Accuracy" in metrics
    assert len(metrics["factors"]) == 8
    supervision = next(item for item in metrics["factors"] if item["name"] == "Clinician supervision")
    assert supervision["generic"] >= 88 and supervision["twin"] >= 88
    assert supervision["winner"] == "close"
    assert all(item["meaning"] for item in metrics["factors"])


def test_generic_can_lead_when_the_twin_text_is_thin():
    metrics = generate_comparison_metrics(
        {"consultation_summary": "because therefore based on evidence", "possible_concerns": [], "suggested_next_steps": []},
        {
            "assessment": "ok",
            "recommended_tests": [],
            "immediate_actions": [],
            "follow_up_plan": [],
            "historical_patterns": [],
            "graph_evidence": {"links": []},
            "unique_factors": [],
        },
    )
    explain = next(item for item in metrics["factors"] if item["name"] == "Explainability")
    assert explain["generic"] > explain["twin"]
    assert explain["winner"] == "generic"
    assert explain["improve"]


def test_grounded_twin_leads_personalization_explainability_and_accuracy():
    metrics = generate_comparison_metrics(
        {
            "consultation_summary": "Aarav Mehta, age 52. Type 2 diabetes, hypertension, family history, LDL and HbA1c are listed on the form.",
            "possible_concerns": ["Cardiometabolic burden from LDL/HbA1c may elevate long-term risk."],
            "suggested_next_steps": ["Obtain ECG and arrange follow-up."],
            "risk_notes": ["Escalate if chest pain worsens."],
        },
        {
            "assessment": "Aarav, age 52, with diabetes, family history, and elevated LDL. This further increases cardiovascular risk because the lipid burden is active.",
            "recommended_tests": ["12-lead ECG", "2D Echo", "Fasting lipid profile"],
            "immediate_actions": ["Reconcile the statin"],
            "follow_up_plan": ["Follow-up within 3-7 days", "Escalate if rest pain appears"],
            "historical_patterns": [{"case_id": str(i)} for i in range(5)],
            "graph_evidence": {"links": [{"source": "high LDL", "target": "CAD", "relation": "increases_risk"} for _ in range(12)]},
            "unique_factors": [
                "Long-standing diabetes increases vascular risk burden.",
                "Elevated LDL suggests active atherosclerotic risk.",
            ],
        },
    )
    by_name = {item["name"]: item for item in metrics["factors"]}
    for name in ("Personalization", "Explainability", "Accuracy"):
        item = by_name[name]
        assert item["twin"] - item["generic"] >= 15, name
        assert item["winner"] == "twin"
        assert "Vimlesh" not in item["reason"]
        assert "Doctor's Twin" in item["reason"]
        if name == "Accuracy":
            assert 82 <= item["twin"] <= 88
            assert 34 <= item["generic"] <= 40
        else:
            assert item["twin"] >= 80
