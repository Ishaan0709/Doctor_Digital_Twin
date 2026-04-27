from twin_engine.compare_engine import generate_comparison_metrics


def test_compare_metrics_has_keys():
    metrics = generate_comparison_metrics(
        {"consultation_summary": "basic", "possible_concerns": [], "suggested_next_steps": []},
        {"assessment": "patient risk preventive case evidence test follow-up", "recommended_tests": ["ECG"], "immediate_actions": [], "follow_up_plan": []},
    )
    assert "Personalization Score" in metrics
    assert "Specialist Alignment" in metrics
