import streamlit as st
from backend.utils import generate_generic_consultation
from frontend.ui import apply_theme, render_top_nav, section_card

st.set_page_config(page_title="Generic GPT Consultation", layout="wide")
apply_theme()
render_top_nav("2 Generic")
st.title("Generic GPT Clinical Baseline")
st.caption("Initial reasoning generated from the current patient profile only")
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
c1, c2 = st.columns([1.35, 1.0], gap="large")
with c1:
    st.subheader("Generic Model Summary")
    st.info(r.get("consultation_summary", ""))
with c2:
    st.subheader("Possible Concerns")
    for item in r.get("possible_concerns", []):
        st.write(f"- {item}")

c3, c4 = st.columns(2, gap="large")
with c3:
    steps = r.get("suggested_next_steps", [])
    steps_html = "".join([f"<li>{item}</li>" for item in steps])
    st.markdown(
        "<div class='diff-card'>"
        "<h4 style='margin-top:0'>Suggested Next Steps</h4>"
        f"<ul style='margin:0.25rem 0 0 1.15rem'>{steps_html}</ul>"
        "</div>",
        unsafe_allow_html=True,
    )
with c4:
    notes = r.get("risk_notes", [])
    notes_html = "".join([f"<li>{item}</li>" for item in notes])
    st.markdown(
        "<div class='diff-card'>"
        "<h4 style='margin-top:0'>Risk Notes</h4>"
        f"<ul style='margin:0.25rem 0 0 1.15rem'>{notes_html}</ul>"
        "</div>",
        unsafe_allow_html=True,
    )

st.markdown(
    "<div class='glass-card'><strong>Next step:</strong> move to the specialist twin consultation, then open the difference dashboard.</div>",
    unsafe_allow_html=True,
)

if st.button("Open Dr. Vimlesh Pandey Twin Consultation", type="primary"):
    st.switch_page("pages/3_Vimlesh_Twin.py")
