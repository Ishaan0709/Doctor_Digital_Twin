import streamlit as st
import plotly.graph_objects as go
import networkx as nx
from backend.utils import get_graph_payload
from frontend.ui import apply_theme, render_top_nav, section_card

st.set_page_config(page_title="Graph Intelligence", layout="wide")
apply_theme()
render_top_nav("6 Graph")
st.title("Graph Intelligence")
st.caption("NetworkX + Plotly risk relationship intelligence")
section_card(
    "How to interpret the graph",
    "Nodes represent symptoms, risk factors, tests, and decisions from your uploaded graph. Edges show relationship direction and type used in reasoning summaries.",
)

patient = st.session_state.get("patient")
if not patient:
    st.warning("Please complete Patient Intake first.")
    st.stop()

payload = get_graph_payload(patient)
G = nx.DiGraph()
for n in payload.get("nodes", []):
    G.add_node(n["id"], label=n.get("label", n["id"]))
for e in payload.get("edges", []):
    G.add_edge(e["source"], e["target"], relation=e.get("relation", "linked_to"))

pos = nx.spring_layout(G, seed=42)
edge_x, edge_y = [], []
for src, tgt in G.edges():
    x0, y0 = pos[src]
    x1, y1 = pos[tgt]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])

node_x, node_y, node_text = [], [], []
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(G.nodes[node].get("label", node))

fig = go.Figure()
fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=1.4, color="#94a3b8"), hoverinfo="none"))
fig.add_trace(go.Scatter(x=node_x, y=node_y, mode="markers+text", marker=dict(size=22, color="#1d4ed8"), text=node_text, textposition="top center", hoverinfo="text"))
fig.update_layout(height=650, showlegend=False, margin=dict(l=0, r=0, t=20, b=0))
st.plotly_chart(fig, use_container_width=True)

st.subheader("Graph Evidence Summary")
for line in payload.get("evidence_summary", []):
    st.write(f"- {line}")

st.markdown("**Highlighted Links (derived from your uploaded graph data)**")
if payload.get("edges"):
    preview = payload["edges"][:5]
    for edge in preview:
        src = next((n.get("name", n.get("label", n["id"])) for n in payload["nodes"] if n["id"] == edge["source"]), edge["source"])
        tgt = next((n.get("name", n.get("label", n["id"])) for n in payload["nodes"] if n["id"] == edge["target"]), edge["target"])
        st.write(f"- {src} -> {tgt} ({edge.get('relation', 'linked_to')})")

if st.button("Open Comparison Insights", type="primary"):
    st.switch_page("pages/8_Comparison_Insights.py")
