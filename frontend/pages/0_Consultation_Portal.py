import streamlit as st

from backend.utils import generate_followup_reply, generate_generic_consultation, generate_twin_consultation, summarize_patient
from frontend.ui import apply_theme, render_top_nav, section_card


st.set_page_config(page_title="Consultation Portal", layout="wide")
apply_theme()
render_top_nav("1 Intake")

st.title("Consultation Portal")
st.caption("One-on-one consultation experience with guided intake, live chat, and clinician review workflow.")

# ChatGPT-like UX tweaks for this page only
st.markdown(
    """
<style>
/* Keep chat input visually stable */
div[data-testid="stChatInput"] textarea {
  border-radius: 14px !important;
}
/* Slightly tighter chat message spacing */
div[data-testid="stChatMessage"] {
  padding-top: 0.15rem;
  padding-bottom: 0.15rem;
}
</style>
""",
    unsafe_allow_html=True,
)

section_card(
    "How this works",
    "Fill the guided intake, choose a consultation style (General AI or Specialist Twin), then continue the conversation in chat. "
    "A clinician review panel is available to accept, reject, or edit the draft before it is shared back to the patient.",
)


def _init_state() -> None:
    st.session_state.setdefault("portal_patient", None)
    st.session_state.setdefault("portal_mode", None)  # "general" | "specialist"
    st.session_state.setdefault("portal_chat", [])  # list[dict(role, content)]
    st.session_state.setdefault("portal_draft", None)  # str
    st.session_state.setdefault("portal_original_draft", None)  # str
    st.session_state.setdefault("portal_twin", None)  # dict
    st.session_state.setdefault("portal_approved", None)  # str
    st.session_state.setdefault("portal_rejected", False)
    st.session_state.setdefault("portal_doctor_status", None)  # "approved" | "edited_approved" | "rejected"
    st.session_state.setdefault("portal_view", "Patient")  # "Patient" | "Doctor"


_init_state()

is_specialist_mode = st.session_state.get("portal_mode") == "specialist"

top_left, top_right = st.columns([1, 1], gap="large")
with top_left:
    if is_specialist_mode:
        st.session_state.portal_view = st.radio(
            "View",
            ["Patient", "Doctor"],
            horizontal=True,
            label_visibility="collapsed",
            index=0 if st.session_state.portal_view == "Patient" else 1,
        )
    else:
        st.session_state.portal_view = "Patient"
        st.radio(
            "View",
            ["Patient"],
            horizontal=True,
            label_visibility="collapsed",
            index=0,
            disabled=True,
        )
with top_right:
    st.markdown(
        "<div class='glass-card'><strong>Demo flow:</strong> Intake → Choose consultation → Chat → Doctor review → Patient sees clinician action</div>",
        unsafe_allow_html=True,
    )

if st.session_state.portal_view == "Patient":
    st.subheader("Guided Patient Intake")

    with st.form("portal_intake"):
        c1, c2, c3 = st.columns(3, gap="large")
        with c1:
            name = st.text_input("Patient name", value="Aarav Mehta")
            age = st.number_input("Age", min_value=1, max_value=120, value=52)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0)
        with c2:
            height_cm = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0)
            weight_kg = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=78.0)
            symptom_duration = st.selectbox(
                "Duration",
                ["1-2 days", "1 week", "2 weeks", "1 month", "3 months", "6+ months"],
                index=2,
                help="Approximate duration helps urgency framing.",
            )
        with c3:
            bp = st.text_input("BP (e.g., 130/85)", value="154/96")
            ldl = st.number_input("LDL", min_value=0.0, max_value=400.0, value=186.0, help="Higher LDL increases long-term atherosclerotic risk.")
            hba1c = st.number_input("HbA1c", min_value=0.0, max_value=20.0, value=8.4, help="Higher HbA1c suggests higher cardiometabolic risk.")

        symptom_type = st.selectbox(
            "Main symptom pattern",
            [
                "Chest pain / pressure on exertion",
                "Breathlessness on exertion",
                "Palpitations / irregular heartbeat",
                "Fatigue / reduced exercise tolerance",
                "Atypical discomfort (jaw/back/epigastric)",
                "No symptoms (preventive check)",
            ],
            index=0,
            help="Choose the closest match; you can add details below.",
        )
        symptom_details = st.text_area(
            "Symptom details (simple words)",
            value="Exertional chest pain radiating to left arm, improves with rest.",
        )

        risk_factors = st.multiselect(
            "Risk factors (select all that apply)",
            ["Diabetes", "Hypertension", "Smoking", "Family history of early CAD", "Obesity", "High stress", "High cholesterol", "CKD"],
            default=["Diabetes", "Hypertension", "Smoking", "Family history of early CAD", "High cholesterol"],
        )

        medical_history = st.text_area(
            "Medical history",
            value="Type 2 diabetes for 9 years, hypertension for 6 years.",
        )
        family_history = st.text_area(
            "Family history",
            value="Father had MI at 54.",
        )
        lifestyle = st.text_area(
            "Lifestyle",
            value="Sedentary job, smoker 8 cigarettes/day, low exercise.",
        )
        current_medications = st.text_area(
            "Current medications",
            value="Metformin, Amlodipine, statin irregularly.",
        )
        optional_notes = st.text_area(
            "Optional notes",
            value="Pain worse after heavy meals; anxious about heart attack.",
        )

        submitted = st.form_submit_button("Save Intake", type="primary")

    if submitted:
        portal_payload = {
            "name": name,
            "age": int(age),
            "gender": gender,
            "height_cm": float(height_cm),
            "weight_kg": float(weight_kg),
            "symptoms": f"{symptom_type}. {symptom_details}".strip(),
            "symptom_duration": symptom_duration,
            "medical_history": f"{medical_history}\nRisk factors selected: {', '.join(risk_factors)}".strip(),
            "family_history": family_history,
            "lifestyle": lifestyle,
            "current_medications": current_medications,
            "bp": bp,
            "ldl": float(ldl),
            "hba1c": float(hba1c),
            "optional_notes": optional_notes,
        }
        st.session_state.portal_patient = portal_payload
        # Keep legacy workflow in sync: Patient Analysis auto-fills from portal intake.
        st.session_state.patient = dict(portal_payload)
        st.session_state.portal_chat = []
        st.session_state.portal_draft = None
        st.session_state.portal_original_draft = None
        st.session_state.portal_approved = None
        st.session_state.portal_rejected = False
        st.session_state.portal_twin = None
        st.session_state.portal_mode = None
        st.session_state.portal_doctor_status = None
        st.success("Intake saved. Choose a consultation type to begin.")

    st.divider()
    st.subheader("Choose Consultation Type")

    patient = st.session_state.portal_patient
    if not patient:
        st.info("Save the intake first to start a consultation.")
    else:
        if st.session_state.portal_chat:
            mode = st.session_state.portal_mode or "general"
            st.markdown(
                f"<div class='glass-card'><strong>Active consultation:</strong> {('General AI' if mode=='general' else 'Dr. Vimlesh Pandey Specialist Twin')} "
                f"&nbsp;&nbsp; <span class='muted'>(you can switch to Doctor view anytime)</span></div>",
                unsafe_allow_html=True,
            )
        else:
            b1, b2 = st.columns(2, gap="large")
            with b1:
                with st.container(border=True):
                    st.subheader("General AI Consultation")
                    st.caption("Broad clinical guidance based only on your inputs. Good for baseline clarity.")
                    if st.button("Start General Consultation", type="primary", use_container_width=True, key="portal_start_general"):
                        st.session_state.portal_mode = "general"
                        g = generate_generic_consultation(patient)
                        draft = g.get("consultation_summary", "")
                        st.session_state.portal_draft = draft
                        st.session_state.portal_original_draft = draft
                        st.session_state.portal_doctor_status = None
                        st.session_state.portal_chat = [{"role": "assistant", "content": draft}]

            with b2:
                with st.container(border=True):
                    st.subheader("Dr. Vimlesh Pandey Specialist Twin")
                    st.caption("Specialist reasoning enriched with historical case evidence and graph relationships.")
                    if st.button("Start Specialist Consultation", type="primary", use_container_width=True, key="portal_start_specialist"):
                        st.session_state.portal_mode = "specialist"
                        t = generate_twin_consultation(patient)
                        st.session_state.portal_twin = t
                        draft = t.get("assessment", "")
                        st.session_state.portal_draft = draft
                        st.session_state.portal_original_draft = draft
                        st.session_state.portal_doctor_status = None
                        st.session_state.portal_chat = [{"role": "assistant", "content": draft}]

    st.divider()
    st.subheader("Consultation Chat")

    if st.session_state.portal_chat:
        # Doctor status banner (patient-facing)
        if st.session_state.portal_doctor_status == "approved":
            st.success("Doctor has reviewed and approved the consultation.")
        elif st.session_state.portal_doctor_status == "edited_approved":
            st.success("Doctor has edited and approved the consultation (updated guidance shared below).")
        elif st.session_state.portal_doctor_status == "rejected":
            st.warning("Doctor has rejected this draft. Please schedule a direct clinical review.")

        quick_left, quick_right = st.columns([1, 1], gap="large")
        with quick_left:
            if st.session_state.portal_mode == "specialist":
                if st.button("Open Doctor Review", use_container_width=True, key="portal_open_doctor"):
                    st.session_state.portal_view = "Doctor"
                    st.rerun()
            else:
                st.button("Doctor Review (Specialist only)", use_container_width=True, key="portal_open_doctor_disabled", disabled=True)
        with quick_right:
            if st.button("Reset Consultation", use_container_width=True, key="portal_reset"):
                st.session_state.portal_chat = []
                st.session_state.portal_draft = None
                st.session_state.portal_original_draft = None
                st.session_state.portal_twin = None
                st.session_state.portal_mode = None
                st.session_state.portal_approved = None
                st.session_state.portal_rejected = False
                st.session_state.portal_doctor_status = None
                st.success("Reset done.")
                st.rerun()

        for msg in st.session_state.portal_chat:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if st.session_state.portal_mode == "specialist" and st.session_state.portal_twin:
            with st.expander("Immediate actions and next steps (specialist view)", expanded=True):
                t = st.session_state.portal_twin
                st.markdown("**Immediate actions**")
                for x in t.get("immediate_actions", []):
                    st.write(f"- {x}")
                st.markdown("**Recommended tests**")
                for x in t.get("recommended_tests", []):
                    st.write(f"- {x}")
                st.markdown("**Follow-up plan**")
                for x in t.get("follow_up_plan", []):
                    st.write(f"- {x}")
                if st.session_state.portal_doctor_status in ("approved", "edited_approved"):
                    st.success("Doctor review completed for this consultation.")
                elif st.session_state.portal_doctor_status == "rejected":
                    st.warning("Doctor rejected this draft. Clinical review is required.")
                else:
                    st.info("Pending doctor review (recommended for specialist consultations).")

        user_msg = st.chat_input("Ask a follow-up question (e.g., 'What should I do today?' / 'Is this urgent?')")
        if user_msg:
            st.session_state.portal_chat.append({"role": "user", "content": user_msg})
            with st.chat_message("user"):
                st.write(user_msg)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    reply = generate_followup_reply(
                        mode=st.session_state.portal_mode or "general",
                        patient=st.session_state.portal_patient,
                        user_question=user_msg,
                        twin=st.session_state.portal_twin,
                    )
                st.write(reply)
            st.session_state.portal_chat.append({"role": "assistant", "content": reply})
    else:
        st.info("Start a consultation to enable chat.")

else:
    st.subheader("Clinician Review & Control Panel")
    patient = st.session_state.portal_patient
    draft = st.session_state.portal_draft
    mode = st.session_state.portal_mode

    if mode != "specialist":
        st.info("Doctor Review is available only for Dr. Vimlesh Pandey Specialist Twin consultations.")
        if st.button("Back to Patient Chat", type="primary"):
            st.session_state.portal_view = "Patient"
            st.rerun()
        st.stop()

    if not patient or not draft or not mode:
        st.info("Start a consultation first. Then this panel will show the draft for clinician review.")
    else:
        summary = summarize_patient(patient)
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"**Patient:** {summary.get('patient')} &nbsp;&nbsp; **Age:** {summary.get('age')} &nbsp;&nbsp; **BMI:** {summary.get('bmi')}")
        rm = summary.get("risk_markers", {})
        st.markdown(f"**Risk markers:** BP {rm.get('BP')} | LDL {rm.get('LDL')} | HbA1c {rm.get('HbA1c')}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.caption("Edit the draft below. Accept will publish the clinician-approved response back to the patient chat.")
        edited = st.text_area("Clinician-edited consultation draft", value=draft, height=260)

        a1, a2, a3 = st.columns([1, 1, 1.5], gap="large")
        with a1:
            if st.button("Accept", type="primary", use_container_width=True):
                st.session_state.portal_approved = edited
                st.session_state.portal_rejected = False
                original = st.session_state.portal_original_draft or ""
                changed = edited.strip() != original.strip()
                st.session_state.portal_doctor_status = "edited_approved" if changed else "approved"
                if changed:
                    st.success("Accepted with edits. Patient chat will show the updated clinician-approved guidance.")
                    st.session_state.portal_chat.append(
                        {"role": "assistant", "content": f"Doctor update: Edited and approved.\n\n{edited}"}
                    )
                else:
                    st.success("Accepted. Patient chat will show doctor approval.")
                    st.session_state.portal_chat.append(
                        {"role": "assistant", "content": "Doctor update: Approved without changes."}
                    )
        with a2:
            if st.button("Reject", use_container_width=True):
                st.session_state.portal_rejected = True
                st.session_state.portal_approved = None
                st.session_state.portal_doctor_status = "rejected"
                st.warning("Rejected. Draft remains unapproved.")
                st.session_state.portal_chat.append(
                    {
                        "role": "assistant",
                        "content": "Doctor update: Rejected. Please schedule a direct clinical review.",
                    }
                )
        with a3:
            st.markdown(
                "<div class='glass-card'><strong>Safety note:</strong> This panel is a demo clinician workflow. "
                "In real deployments, access control, audit logs, and role-based approvals should be enforced.</div>",
                unsafe_allow_html=True,
            )

        st.divider()
        if st.button("Back to Patient Chat", type="primary"):
            st.session_state.portal_view = "Patient"
            st.rerun()
