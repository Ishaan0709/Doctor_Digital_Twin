import streamlit as st

from frontend.ui import apply_theme, render_top_nav, section_card

st.set_page_config(page_title="Backend Story", layout="wide")
apply_theme()
render_top_nav("10 Story")
st.title("How The Recommendation Was Produced")
st.caption("Plain-language, step-by-step story of what happened in the backend")

patient = st.session_state.get("patient")
generic = st.session_state.get("generic_result")
twin = st.session_state.get("twin_result")
if not patient or not generic or not twin:
    st.warning("Please complete Intake, Generic, and Twin pages first.")
    st.stop()

history_count = len(twin.get("historical_patterns", []))
graph_links = len(twin.get("graph_evidence", {}).get("links", []))
cb = twin.get("confidence_breakdown", {})

section_card(
    "Story mode",
    "This screen translates the technical pipeline into a friendly clinical narrative: what data was used, what each engine did, and why the final recommendation looks the way it does.",
)

st.subheader("The Story")
st.markdown(
    f"""
1. **Patient context entered**  
   The intake details created the base patient narrative (symptoms, vitals, history, medications, risk labs, and notes).

2. **Generic AI baseline generated**  
   A general LLM produced an initial consultation from only this patient context.  
   This is the neutral reference point before specialist memory.

3. **Historical case memory retrieval (RAG)**  
   The system embedded patient text and searched the doctor-case index to fetch the most similar historical cases.  
   Retrieved specialist cases used in this run: **{history_count}**.

4. **Graph evidence reasoning (GraphRAG)**  
   Patient clues were matched with graph nodes and then expanded through clinical relationships (symptom -> risk -> test/decision links).  
   Graph links activated for this run: **{graph_links}**.

5. **Specialist twin synthesis**  
   The twin prompt combined: patient-first framing + RAG evidence + GraphRAG evidence + uniqueness flags.  
   Then the doctor-twin LLM generated the specialist assessment, tests, immediate actions, and follow-up plan.

6. **Confidence score computed**  
   Formula: `min(0.98, 0.60 + 0.07*retrieved_cases + 0.03*graph_links)`  
   This run: base `{cb.get("base", 0.6):.2f}` + retrieval `{cb.get("retrieval_component", 0):.2f}` + graph `{cb.get("graph_component", 0):.2f}` = final `{cb.get("final_score", twin.get("confidence_score", 0)):.2f}`.
"""
)

st.subheader("Generic GPT vs Twin - Why outputs differ")
left, right = st.columns(2, gap="large")
with left:
    st.markdown("<div class='diff-card'><h4 style='margin-top:0'>Generic GPT</h4>", unsafe_allow_html=True)
    st.write("- No specialist historical case memory.")
    st.write("- No graph relationship traversal.")
    st.write("- Broad guidance quality, lower personalization depth.")
    st.markdown("</div>", unsafe_allow_html=True)
with right:
    st.markdown("<div class='diff-card'><h4 style='margin-top:0'>Dr. Pandey Twin</h4>", unsafe_allow_html=True)
    st.write("- Uses specialist historical decisions and outcomes.")
    st.write("- Uses graph-based evidence links for richer causality.")
    st.write("- Produces more context-aware and specialist-aligned pathways.")
    st.markdown("</div>", unsafe_allow_html=True)

if st.button("Return to Why This Recommendation", type="primary"):
    st.switch_page("pages/9_Why_This_Recommendation.py")
