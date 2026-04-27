import streamlit as st
from backend.utils import generate_generic_consultation
from frontend.ui import apply_theme, render_top_nav, section_card

st.set_page_config(page_title="Generic GPT Consultation", layout="wide")
apply_theme()
render_top_nav("2 Generic")
st.title("Generic GPT Consultation")
st.caption("Consultation from current patient input only")
section_card(
    "Interpretation note",
    "This baseline output does not use Dr. Pandey's historical case memory or graph evidence. Use it as a neutral reference before specialist-twin reasoning.",
)

patient = st.session_state.get("patient")
if not patient:
    st.warning("Please complete Patient Intake first.")
    st.stop()

if "generic_result" not in st.session_state:
    with st.spinner("Generating generic consultation..."):
        st.session_state.generic_result = generate_generic_consultation(patient)

r = st.session_state.generic_result
c1, c2 = st.columns(2)
c1.subheader("Consultation Summary")
c1.info(r.get("consultation_summary", ""))
c2.subheader("Possible Concerns")
for item in r.get("possible_concerns", []):
    c2.write(f"- {item}")

c3, c4 = st.columns(2)
c3.subheader("Suggested Next Steps")
for item in r.get("suggested_next_steps", []):
    c3.write(f"- {item}")
c4.subheader("Risk Notes")
for item in r.get("risk_notes", []):
    c4.write(f"- {item}")

if st.button("Open Dr. Pandey AI Twin", type="primary"):
    st.switch_page("pages/3_Graph_View.py")
