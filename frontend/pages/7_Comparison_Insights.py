import streamlit as st
import plotly.graph_objects as go
from twin_engine.compare_engine import generate_comparison_metrics
from frontend.ui import apply_theme, render_top_nav, section_card

st.set_page_config(page_title="Comparison Insights", layout="wide")
apply_theme()
render_top_nav("6 Insights")
st.title("Comparison Insights")
st.caption("Executive dashboard (no raw side-by-side transcript)")
section_card(
    "What this dashboard shows",
    "Scores summarize depth of personalization, evidence usage, risk framing, and actionability to compare baseline AI reasoning versus specialist digital twin behavior.",
)

generic = st.session_state.get("generic_result")
twin = st.session_state.get("twin_result")
if not generic or not twin:
    st.warning("Please run Generic and Twin consultations first.")
    st.stop()

metrics = generate_comparison_metrics(generic, twin)
keys = ["Personalization Score", "Use of Historical Evidence", "Risk Sensitivity", "Explainability", "Actionability", "Specialist Alignment"]
cols = st.columns(6)
for i, k in enumerate(keys):
    cols[i].metric(k, f"{metrics.get(k, 0)}")

scores = [metrics[k] for k in keys]
fig = go.Figure(
    data=[
        go.Bar(
            x=keys,
            y=scores,
            marker=dict(
                color=scores,
                colorscale="Blues",
                showscale=True,
                colorbar=dict(title="Score"),
            ),
        )
    ]
)
fig.update_layout(height=420, xaxis_title="Metric", yaxis_title="Score")
st.plotly_chart(fig, use_container_width=True)

st.info("Twin consultation is more context-aware through patient-first reasoning, specialist historical evidence, and graph-based risk links.")

if st.button("Open Why This Recommendation", type="primary"):
    st.switch_page("pages/8_Why_This_Recommendation.py")
