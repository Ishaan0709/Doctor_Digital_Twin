import streamlit as st
from backend.utils import generate_twin_consultation
from frontend.ui import apply_theme, render_top_nav, section_card

st.set_page_config(page_title="Dr. Vimlesh Pandey AI Twin", layout="wide")
apply_theme()
render_top_nav("3 Twin")
st.title("Dr. Vimlesh Pandey AI Twin")
st.caption("Patient-first + historical RAG + GraphRAG specialist reasoning")
section_card(
    "How to read this page",
    "Assessment is generated with current patient priority, then enriched with similar historical patterns and graph relationships. Historical cases are references, not copy-paste prescriptions.",
)

patient = st.session_state.get("patient")
if not patient:
    st.warning("Please complete Patient Intake first.")
    st.stop()

if "twin_result" not in st.session_state:
    with st.spinner("Generating specialist twin consultation..."):
        st.session_state.twin_result = generate_twin_consultation(patient)

r = st.session_state.twin_result
st.subheader("Dr. Pandey's Assessment")
st.success(r.get("assessment", ""))

c1, c2 = st.columns(2)
c1.subheader("Why This Patient Is Unique")
for item in r.get("unique_factors", []):
    c1.write(f"- {item}")
c2.subheader("Historical Patterns Considered")
for c in r.get("historical_patterns", []):
    c2.write(f"- Case {c.get('case_id')}: {c.get('diagnosis')} ({c.get('match_score', 0):.2f})")

c3, c4, c5 = st.columns(3)
c3.subheader("Recommended Tests")
for x in r.get("recommended_tests", []):
    c3.write(f"- {x}")
c4.subheader("Immediate Actions")
for x in r.get("immediate_actions", []):
    c4.write(f"- {x}")
c5.subheader("Follow-up Plan")
for x in r.get("follow_up_plan", []):
    c5.write(f"- {x}")

st.metric("Confidence Score", f"{r.get('confidence_score', 0) * 100:.0f}%")

if st.button("View Historical Case Intelligence", type="primary"):
    st.switch_page("pages/5_Historical_Case_Intelligence.py")
