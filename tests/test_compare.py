from twin_engine.compare_engine import TRACEABILITY_NOTE, generate_comparison_metrics


def _sides(metrics):
    for item in metrics["factors"]:
        assert item["calculation"]["formula"]
        assert "stops at" not in item["calculation"]["formula"].lower()
        for side in ("generic", "twin"):
            work = item["calculation"][side]
            assert work["checks"] > 0
            assert work["passed"] == sum(line["value"] for line in work["lines"])
            assert all(line["value"] in (0, 1) for line in work["lines"])
            assert work["total"] == item[side]
            assert work["total"] == ((100 * work["passed"]) + (work["checks"] // 2)) // work["checks"]


def test_compare_metrics_are_percents_of_checks():
    metrics = generate_comparison_metrics(
        {"consultation_summary": "basic", "possible_concerns": [], "suggested_next_steps": []},
        {"assessment": "patient risk preventive case evidence test follow-up", "recommended_tests": ["ECG"], "immediate_actions": [], "follow_up_plan": []},
    )
    assert "Personalization Score" in metrics
    assert "Evidence grounding" in metrics
    assert "Accuracy" not in metrics
    assert len(metrics["factors"]) == 8
    assert "traceability" in TRACEABILITY_NOTE.lower()
    assert "not clinical correctness" in TRACEABILITY_NOTE.lower()
    names = [item["name"] for item in metrics["factors"]]
    assert "Evidence grounding" in names
    assert "Accuracy" not in names
    supervision = next(item for item in metrics["factors"] if item["name"] == "Clinician supervision")
    assert supervision["generic"] == 0
    assert supervision["twin"] == 0
    assert "tells you to check with a clinician" not in supervision["reason"].lower()
    assert "none of the supervision phrases" in supervision["reason"]
    _sides(metrics)
    assert metrics["depth"]["twin"]["total"] == metrics["Twin Context Depth"]
    assert metrics["depth"]["generic"]["total"] == metrics["Generic Context Depth"]


def test_supervision_counts_physician_and_clinician():
    metrics = generate_comparison_metrics(
        {"consultation_summary": "Please check with a physician. A licensed clinician still decides.", "possible_concerns": [], "suggested_next_steps": []},
        {"assessment": "The plan can wait.", "recommended_tests": [], "immediate_actions": [], "follow_up_plan": []},
    )
    supervision = next(item for item in metrics["factors"] if item["name"] == "Clinician supervision")
    assert supervision["generic"] > supervision["twin"]
    assert "physician" in supervision["reason"].lower() or "clinician" in supervision["reason"].lower()
    assert "tells you to check with a clinician" not in supervision["reason"].lower()


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


def test_grounded_twin_leads_when_it_cites_the_evidence():
    metrics = generate_comparison_metrics(
        {
            "consultation_summary": "Aarav Mehta, age 52. Type 2 diabetes, hypertension, family history, LDL and HbA1c are listed on the form.",
            "possible_concerns": ["Cardiometabolic burden from LDL/HbA1c may elevate long-term risk."],
            "suggested_next_steps": ["Obtain ECG and arrange follow-up."],
            "risk_notes": ["Escalate if chest pain worsens."],
        },
        {
            "assessment": "Aarav, age 52, with diabetes and elevated LDL. Case 3, possible CAD, is a similar reference, not this patient, and it does not confirm a diagnosis. High LDL increases CAD risk.",
            "recommended_tests": ["12-lead ECG", "2D Echo", "Fasting lipid profile"],
            "immediate_actions": ["Reconcile the statin"],
            "follow_up_plan": ["Follow-up within 3-7 days", "Escalate if rest pain appears"],
            "historical_patterns": [{"case_id": "3", "diagnosis": "possible CAD", "decision": "ECG + stress test"}],
            "graph_evidence": {"links": [{"source": "high LDL", "target": "CAD", "relation": "increases_risk"}]},
            "unique_factors": ["Long-standing diabetes increases vascular risk burden."],
        },
    )
    by_name = {item["name"]: item for item in metrics["factors"]}
    grounding = by_name["Evidence grounding"]
    assert grounding["twin"] > grounding["generic"]
    assert grounding["winner"] == "twin"
    assert grounding["twin"] != 95 or grounding["calculation"]["twin"]["passed"] == grounding["calculation"]["twin"]["checks"]
    assert "Vimlesh" not in grounding["reason"]
    assert "Doctor's Twin" in grounding["reason"]
    assert "correct diagnoses" in grounding["reason"]
    _sides(metrics)
