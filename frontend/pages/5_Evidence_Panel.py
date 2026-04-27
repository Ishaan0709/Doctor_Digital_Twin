import streamlit as st
from frontend.ui import apply_theme, render_top_nav, section_card

st.set_page_config(page_title="Evidence Panel", layout="wide")
apply_theme()
render_top_nav("5 Cases")
st.title("Evidence Center")
st.caption("Explore the three evidence layers used by the specialist twin.")
section_card(
    "Evidence Center",
    "Evidence has three focused screens for clarity: Historical Cases, Graph Intelligence, and Why This Recommendation. This avoids clutter and keeps each evidence type easy to understand.",
)

c1, c2, c3 = st.columns(3, gap="large")
with c1:
    st.markdown("<div class='diff-card'><h4 style='margin-top:0'>Historical Case Intelligence</h4>", unsafe_allow_html=True)
    st.write("Review similar specialist cases, diagnosis patterns, decisions, and outcomes.")
    if st.button("Open Historical Cases", use_container_width=True, key="e_hist"):
        st.switch_page("pages/6_Historical_Case_Intelligence.py")
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='diff-card'><h4 style='margin-top:0'>Graph Intelligence</h4>", unsafe_allow_html=True)
    st.write("Inspect graph relationships used to connect symptoms, risks, tests, and decisions.")
    if st.button("Open Graph Intelligence", use_container_width=True, key="e_graph"):
        st.switch_page("pages/7_Graph_Intelligence.py")
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown("<div class='diff-card'><h4 style='margin-top:0'>Why This Recommendation</h4>", unsafe_allow_html=True)
    st.write("Understand confidence, evidence traceability, and recommendation rationale.")
    if st.button("Open Explainability", use_container_width=True, key="e_why"):
        st.switch_page("pages/9_Why_This_Recommendation.py")
    st.markdown("</div>", unsafe_allow_html=True)
