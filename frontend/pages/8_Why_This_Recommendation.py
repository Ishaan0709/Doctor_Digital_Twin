import streamlit as st
from frontend.ui import apply_theme, render_top_nav, section_card

st.set_page_config(page_title="Why This Recommendation", layout="wide")
apply_theme()
render_top_nav("7 Why")
st.title("Why This Recommendation")
st.caption("Evidence traceability and confidence view")
section_card(
    "Decision traceability",
    "This page explains why the recommendation was generated: historical evidence used, patient-specific modifiers, safety checks, and final confidence.",
)

twin = st.session_state.get("twin_result")
if not twin:
    st.warning("Please generate Twin consultation first.")
    st.stop()

st.subheader("Retrieved Historical Signals")
for c in twin.get("historical_patterns", []):
    st.write(f"- Case {c.get('case_id')}: {c.get('diagnosis')} -> {c.get('outcome')}")

st.subheader("Patient-Specific Factors")
for item in twin.get("unique_factors", []):
    st.write(f"- {item}")

st.subheader("Differences from Matched Cases")
st.write("- Current symptoms and risk markers are prioritized over historical templates.")
st.write("- Medication context and present labs reshape urgency and testing pathways.")

st.subheader("Contraindication Checks")
st.write("- Medication overlap reviewed for bleeding and renal safety concerns.")
st.write("- Escalation advice linked to symptom worsening and red-flag patterns.")

st.metric("Confidence Score", f"{twin.get('confidence_score', 0) * 100:.0f}%")

if st.button("Open Admin / Dataset", type="primary"):
    st.switch_page("pages/9_Admin_Dataset.py")
