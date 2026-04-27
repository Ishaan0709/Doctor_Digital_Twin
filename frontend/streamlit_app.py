import streamlit as st
from frontend.ui import apply_theme, render_top_nav, section_card

st.set_page_config(page_title="CardioTwin AI", layout="wide", initial_sidebar_state="expanded")
apply_theme()
render_top_nav("1 Intake")

st.markdown("""
<style>
/* Page-specific tuning only; base theme is in frontend/ui.py */
</style>
""", unsafe_allow_html=True)

st.sidebar.title("CardioTwin AI")
st.sidebar.caption("Elite Cardiology Reasoning Platform")
st.sidebar.success("Use Streamlit page navigation in the sidebar to access all screens.")
st.sidebar.markdown("### Quick Path")
st.sidebar.write("1) Intake  ->  2) Generic Baseline  ->  3) Vimlesh Twin  ->  4) GPT vs Twin Difference  ->  Evidence")
st.sidebar.caption("Tip: start from Patient Analysis for best flow.")

st.markdown("""
<div class='hero'>
    <h1>CardioTwin AI</h1>
    <p style='font-size:1.1rem;'>Scaling the reasoning of elite cardiologists using AI Digital Twins</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("AI Modes", "2", "Generic + Twin")
c2.metric("Reasoning Layers", "3", "Patient + RAG + GraphRAG")
c3.metric("Audience", "3", "Teachers, Company Heads, Doctors")

section_card(
    "What problem it solves",
    "CardioTwin AI standardizes expert preventive cardiology reasoning into an auditable intelligence layer for high-stakes decision support.",
)
section_card(
    "Why doctors need it",
    "It accelerates triage quality, risk interpretation, and follow-up planning while keeping physician judgment central.",
)
section_card(
    "Why hospitals need it",
    "It improves consistency, governance visibility, and scalable specialist-aligned care pathways.",
)
section_card(
    "Key features",
    "Patient intake, generic consultation, digital twin consultation, historical case intelligence, graph evidence reasoning, executive comparison, and recommendation traceability.",
)

c4, c5 = st.columns(2)
with c4:
    st.markdown(
        "<div class='diff-card'><h4 style='margin-top:0'>Clinical Intelligence Layers</h4>"
        "<ul><li>Patient-first reasoning</li><li>Historical case retrieval (RAG)</li><li>Graph-linked evidence (GraphRAG)</li></ul></div>",
        unsafe_allow_html=True,
    )
with c5:
    st.markdown(
        "<div class='diff-card'><h4 style='margin-top:0'>Built for Clarity</h4>"
        "<ul><li>Direct GPT vs Twin comparison</li><li>Confidence and similarity explanation tooltips</li><li>Backend story page with full traceability</li></ul></div>",
        unsafe_allow_html=True,
    )

if st.button("Start Analysis", type="primary"):
    st.switch_page("pages/1_Patient_Analysis.py")

if st.button("Open Consultation Portal"):
    st.switch_page("pages/0_Consultation_Portal.py")
