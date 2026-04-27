import streamlit as st
from frontend.ui import apply_theme, render_top_nav, section_card

st.set_page_config(page_title="Evidence Panel", layout="centered")
apply_theme()
render_top_nav("4 Cases")
st.title("Evidence Panel")
section_card(
    "Evidence Center",
    "Evidence has three focused screens for clarity: Historical Cases, Graph Intelligence, and Why This Recommendation. This avoids clutter and keeps each evidence type easy to understand.",
)
if st.button("Go to Historical Case Intelligence", type="primary"):
    st.switch_page("pages/5_Historical_Case_Intelligence.py")
