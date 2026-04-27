import streamlit as st

from frontend.ui import apply_theme, render_top_nav, section_card

st.set_page_config(page_title="Backend Story", layout="wide")
apply_theme()
render_top_nav("10 Explainability")
st.title("Clinical Explainability Report")
st.caption("Full technical trace, written in simple language, from raw datasets to final recommendation")

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
    "Purpose of this report",
    "This page is designed for complete transparency. It explains exactly what data was used, how each engine contributed, where each score came from, and why the final specialist recommendation took its current shape.",
)

st.subheader("End-to-End Pipeline (Simple but Complete)")
st.markdown(
    f"""
1. **Data collection from intake form**  
   The current patient details are captured (symptoms, duration, medical/family history, lifestyle, medications, BP, LDL, HbA1c, optional notes).  
   This becomes the run-specific input context.

2. **Generic baseline generation (General LLM)**  
   The baseline output is generated using only the patient context and the generic prompt (`prompts/generic_gpt.txt`).  
   This gives a neutral consultation summary before specialist memory and graph evidence are introduced.

3. **Case retrieval from specialist dataset (RAG stage)**  
   The system converts the patient text into an embedding and searches the indexed specialist case dataset.  
   Data source includes doctor cases such as diagnosis, decision, and outcome fields.  
   Retrieved specialist cases in this run: **{history_count}**.

4. **Case reranking for clinical relevance**  
   Retrieved matches are re-ranked with clinical bonuses (for overlap signals like chest pain, LDL, diabetes, BP, CAD patterns).  
   This ensures retrieved evidence is not just mathematically similar but also clinically aligned.

5. **Graph-based reasoning (GraphRAG stage)**  
   The knowledge graph (nodes + edges from graph datasets) is traversed based on matched patient cues.  
   It expands reasoning through relationships such as symptom -> risk -> test/decision pathways.  
   Graph links activated in this run: **{graph_links}**.

6. **Specialist twin synthesis**  
   A specialist prompt is built with four inputs:
   - patient-first clinical context
   - retrieved historical case evidence
   - graph relationship evidence
   - uniqueness flags (what is specific to this patient)
   
   The specialist model then produces the final assessment, tests, immediate actions, and follow-up plan.

7. **Confidence computation**  
   Confidence is intentionally transparent and formula-driven:  
   `final_confidence = min(0.98, 0.60 + 0.07*retrieved_cases + 0.03*graph_links)`  
   For this run: base `{cb.get("base", 0.6):.2f}` + retrieval `{cb.get("retrieval_component", 0):.2f}` + graph `{cb.get("graph_component", 0):.2f}` = final `{cb.get("final_score", twin.get("confidence_score", 0)):.2f}`.
"""
)

st.subheader("Technology Components and Exactly What Each One Does")
with st.expander("1) Datasets and what help they provide", expanded=True):
    st.write("- **Doctor cases dataset**: provides real specialist historical patterns (symptoms, diagnosis, decision, outcome).")
    st.write("- **Graph nodes dataset**: defines important clinical entities (risk factors, symptoms, tests, conditions).")
    st.write("- **Graph edges dataset**: defines relationship logic used for evidence chaining.")
    st.write("- **Patient input**: provides live case context for the current run.")

with st.expander("2) How Generic GPT output is produced", expanded=False):
    st.write("- Uses patient context + generic system prompt.")
    st.write("- Does not use specialist historical retrieval.")
    st.write("- Does not use graph relationship traversal.")
    st.write("- Purpose: baseline reference before specialist enrichment.")

with st.expander("3) How similarity score is computed for historical cases", expanded=False):
    st.write("- Patient and case texts are embedded into vectors.")
    st.write("- FAISS vector search returns cosine similarity values.")
    st.write("- Higher value means case context is closer to current patient context.")
    st.write("- Re-rank layer adds targeted clinical overlap bonus for safer, more relevant ordering.")

with st.expander("4) How GraphRAG contributes", expanded=False):
    st.write("- Patient clues are mapped to graph nodes.")
    st.write("- Outgoing edges are followed to capture related risks/tests/decisions.")
    st.write("- These links create explainable evidence traces used in the twin prompt.")
    st.write("- Result: stronger causal chain instead of generic recommendation text.")

with st.expander("5) How comparison scores are calculated", expanded=False):
    st.write("- Comparison metrics use rule-based keyword heuristics to make scoring transparent.")
    st.write("- Base score starts at 25, each matched indicator keyword adds 15, score is capped at 100.")
    st.write("- Metrics include personalization, historical evidence use, risk sensitivity, explainability, actionability, and specialist alignment.")
    st.write("- These are explainability metrics, not diagnostic truth metrics.")

st.subheader("Generic GPT vs Twin - Why outputs differ")
left, right = st.columns(2, gap="large")
with left:
    st.markdown("<div class='diff-card'><h4 style='margin-top:0'>Generic GPT</h4>", unsafe_allow_html=True)
    st.write("- Built for broad medical language generation.")
    st.write("- No specialist memory retrieval layer.")
    st.write("- No graph-driven evidence expansion.")
    st.write("- Useful as neutral baseline, but less specialized.")
    st.markdown("</div>", unsafe_allow_html=True)
with right:
    st.markdown("<div class='diff-card'><h4 style='margin-top:0'>Dr. Pandey Twin</h4>", unsafe_allow_html=True)
    st.write("- Uses specialist historical decisions and outcomes.")
    st.write("- Uses graph-based evidence links for explicit clinical paths.")
    st.write("- Generates more personalized, specialist-aligned recommendations.")
    st.write("- Improves transparency with measurable confidence components.")
    st.markdown("</div>", unsafe_allow_html=True)

st.subheader("Interpretation Guidance")
st.info(
    "This platform is decision-support infrastructure, not an autonomous diagnosis engine. "
    "The strongest value comes from combining patient context, specialist historical evidence, graph-backed reasoning, and clinician oversight."
)

if st.button("Return to Why This Recommendation", type="primary"):
    st.switch_page("pages/9_Why_This_Recommendation.py")
