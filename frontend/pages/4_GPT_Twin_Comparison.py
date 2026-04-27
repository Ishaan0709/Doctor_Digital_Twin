import streamlit as st

from backend.utils import generate_twin_consultation
from frontend.ui import apply_theme, render_top_nav, section_card

st.set_page_config(page_title="GPT vs Twin Diagnosis Difference", layout="wide")
apply_theme()
render_top_nav("4 Difference")
st.title("GPT vs Twin Diagnosis Difference")
st.caption("Premium side-by-side view of baseline AI vs specialist twin reasoning")

patient = st.session_state.get("patient")
if not patient:
    st.warning("Please complete Patient Intake first.")
    st.stop()

generic = st.session_state.get("generic_result")
if not generic:
    st.warning("Please run Generic consultation first.")
    st.stop()

if "twin_result" not in st.session_state:
    with st.spinner("Preparing specialist twin consultation for side-by-side difference..."):
        st.session_state.twin_result = generate_twin_consultation(patient)

twin = st.session_state.twin_result

section_card(
    "How to read this comparison",
    "Left side is generic AI output from current patient details only. Right side is Dr. Pandey twin output using patient context + retrieved specialist cases + graph reasoning.",
)

left, right = st.columns(2, gap="large")
with left:
    st.markdown("<div class='diff-card'><h3 style='margin-top:0'>Generic GPT</h3>", unsafe_allow_html=True)
    st.write(generic.get("consultation_summary", ""))
    st.markdown("**Approach**")
    st.write("- Uses only direct patient text context.")
    st.write("- Does not reference specialist case memory.")
    st.write("- Does not apply graph relationship reasoning.")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='diff-card'><h3 style='margin-top:0'>Dr. Pandey AI Twin</h3>", unsafe_allow_html=True)
    st.write(twin.get("assessment", ""))
    st.markdown("**Approach**")
    st.write("- Uses patient-first specialist framing.")
    st.write("- Adds retrieved historical case patterns.")
    st.write("- Adds GraphRAG links for risk/decision context.")
    st.markdown("</div>", unsafe_allow_html=True)

st.subheader("Difference Snapshot")
col1, col2, col3 = st.columns(3)
col1.metric("Historical Cases Used", len(twin.get("historical_patterns", [])))
col2.metric("Graph Links Triggered", len(twin.get("graph_evidence", {}).get("links", [])))
col3.metric(
    "Twin Confidence",
    f"{twin.get('confidence_score', 0) * 100:.0f}%",
    help="Calculated as min(0.98, 0.60 + 0.07*retrieved_cases + 0.03*graph_links).",
)

if st.button("Continue to Evidence Center", type="primary"):
    st.switch_page("pages/5_Evidence_Panel.py")
