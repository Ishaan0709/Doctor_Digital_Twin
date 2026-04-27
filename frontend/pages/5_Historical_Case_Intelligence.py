import streamlit as st
from backend.utils import get_case_matches
from frontend.ui import apply_theme, render_top_nav, section_card

st.set_page_config(page_title="Historical Case Intelligence", layout="wide")
apply_theme()
render_top_nav("4 Cases")
st.title("Historical Case Intelligence")
st.caption("Top similar historical specialist cardiology cases")
section_card(
    "How to use these matches",
    "These cases are evidence references showing similar symptom-risk patterns. They support reasoning context and should not override current patient specifics.",
)

patient = st.session_state.get("patient")
if not patient:
    st.warning("Please complete Patient Intake first.")
    st.stop()

matches = get_case_matches(patient)
if not matches:
    st.info("No cases retrieved yet.")
else:
    for m in matches:
        with st.expander(f"Case {m.get('case_id')} | Match Score: {m.get('match_score', 0):.2f}"):
            st.write(f"**Symptoms:** {m.get('symptoms', 'NA')}")
            st.write(f"**Risk factors:** {m.get('risk_factors', 'NA')}")
            st.write(f"**Tests:** {m.get('tests', 'NA')}")
            st.write(f"**Diagnosis:** {m.get('diagnosis', 'NA')}")
            st.write(f"**Decision:** {m.get('decision', 'NA')}")
            st.write(f"**Outcome:** {m.get('outcome', 'NA')}")

if st.button("Open Graph Intelligence", type="primary"):
    st.switch_page("pages/6_Graph_Intelligence.py")
