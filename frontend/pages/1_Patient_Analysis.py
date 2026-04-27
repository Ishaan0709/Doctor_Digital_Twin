import streamlit as st
from frontend.ui import apply_theme, render_top_nav, section_card

st.set_page_config(page_title="Patient Intake | CardioTwin AI", layout="wide")
apply_theme()
render_top_nav("1 Intake")
st.title("Patient Intake")
st.caption("Enter current patient context for this consultation run")
section_card(
    "What this page means",
    "This is the live input for the current analysis session. It is not automatically an existing patient file of Dr. Pandey unless your entered details match a historical case.",
)

if "patient" not in st.session_state:
    st.session_state.patient = {}

with st.form("patient_intake_form"):
    st.markdown("#### Core Demographics & Vitals")
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("Name", value=st.session_state.patient.get("name", ""))
        age = st.number_input("Age", min_value=1, max_value=120, value=int(st.session_state.patient.get("age", 45)))
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0)
    with c2:
        height_cm = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=float(st.session_state.patient.get("height_cm", 170.0)))
        weight_kg = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=float(st.session_state.patient.get("weight_kg", 75.0)))
        symptom_duration = st.text_input("Duration of symptoms", value=st.session_state.patient.get("symptom_duration", "2 weeks"))
    with c3:
        bp = st.text_input("BP", value=st.session_state.patient.get("bp", "130/85"))
        ldl = st.number_input("LDL", min_value=0.0, max_value=400.0, value=float(st.session_state.patient.get("ldl", 140.0)))
        hba1c = st.number_input("HbA1c", min_value=0.0, max_value=20.0, value=float(st.session_state.patient.get("hba1c", 6.8)))

    symptoms = st.text_area("Symptoms", value=st.session_state.patient.get("symptoms", "Exertional chest discomfort, fatigue"))
    medical_history = st.text_area("Medical history", value=st.session_state.patient.get("medical_history", "Type 2 diabetes for 8 years"))
    family_history = st.text_area("Family history", value=st.session_state.patient.get("family_history", "Father had CAD at 52"))
    lifestyle = st.text_area("Lifestyle", value=st.session_state.patient.get("lifestyle", "Sedentary, moderate stress, occasional smoking"))
    current_medications = st.text_area("Current medications", value=st.session_state.patient.get("current_medications", "Metformin, statin irregularly"))
    optional_notes = st.text_area("Optional notes", value=st.session_state.patient.get("optional_notes", ""))

    submitted = st.form_submit_button("Analyze Patient", type="primary")

if submitted:
    st.session_state.patient = {
        "name": name,
        "age": int(age),
        "gender": gender,
        "height_cm": float(height_cm),
        "weight_kg": float(weight_kg),
        "symptoms": symptoms,
        "symptom_duration": symptom_duration,
        "medical_history": medical_history,
        "family_history": family_history,
        "lifestyle": lifestyle,
        "current_medications": current_medications,
        "bp": bp,
        "ldl": float(ldl),
        "hba1c": float(hba1c),
        "optional_notes": optional_notes,
    }
    st.success("Patient profile saved.")
    st.info("Next: review what a generic model says before opening the specialist twin.")
    st.switch_page("pages/2_GPT_vs_Twin.py")
