import streamlit as st
import plotly.express as px
import pandas as pd
from pathlib import Path
from backend.utils import dataset_stats
from frontend.ui import apply_theme, render_top_nav, section_card

st.set_page_config(page_title="Admin / Dataset", layout="wide")
apply_theme()
render_top_nav("8 Admin")
st.title("Admin / Dataset")
st.caption("Operational intelligence for CardioTwin AI data assets")
section_card(
    "Patient Analysis clarification",
    "Patient Analysis is the live input form for the current session. It is not automatically a pre-existing Dr. Pandey patient record. The system then matches that input against historical datasets for evidence support.",
)

stats = dataset_stats()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Doctor Cases", stats.get("doctor_cases", 0))
c2.metric("Patient Profiles", stats.get("patient_profiles", 0))
c3.metric("Graph Nodes", stats.get("graph_nodes", 0))
c4.metric("Graph Edges", stats.get("graph_edges", 0))

chart_df = pd.DataFrame({"Dataset": ["Doctor Cases", "Patient Profiles", "Graph Nodes", "Graph Edges"], "Count": [stats.get("doctor_cases", 0), stats.get("patient_profiles", 0), stats.get("graph_nodes", 0), stats.get("graph_edges", 0)]})
fig = px.pie(chart_df, names="Dataset", values="Count", hole=0.55, height=420)
st.plotly_chart(fig, use_container_width=True)

st.success("CardioTwin AI dataset pipeline is active and ready for expansion.")

st.subheader("Dataset Registry")
base = Path(__file__).resolve().parents[2]
datasets = [
    ("Doctor Cases", base / "data" / "raw" / "doctor_cases_vimlesh_pandey.csv", "Historical specialist consultation cases used for RAG retrieval."),
    ("Patient Profiles", base / "data" / "raw" / "patient_profiles.csv", "Structured patient profile table used for cohort-style context."),
    ("Patient Timelines", base / "data" / "raw" / "patient_timelines.csv", "Longitudinal vitals and progression snapshots."),
    ("Graph Nodes", base / "data" / "raw" / "graph_nodes.csv", "Knowledge-graph entities for GraphRAG."),
    ("Graph Edges", base / "data" / "raw" / "graph_edges.csv", "Knowledge-graph relationships used in graph reasoning."),
    ("Doctor Style Rules", base / "data" / "raw" / "doctor_style_examples.csv", "Style guidance patterns for specialist tone and behavior."),
]

for title, path, desc in datasets:
    exists = path.exists()
    row = st.columns([2, 5, 3])
    row[0].markdown(f"**{title}**")
    row[1].caption(desc)
    if exists:
        row[2].markdown(f"[Open file](file:///{str(path).replace('\\\\', '/')})")
    else:
        row[2].warning("Missing")
