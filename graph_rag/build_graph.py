import json
import networkx as nx
import pandas as pd
from config import DATA_RAW_DIR, DATA_PROCESSED_DIR


def build_knowledge_graph() -> nx.DiGraph:
    nodes_df = pd.read_csv(DATA_RAW_DIR / "graph_nodes.csv")
    edges_df = pd.read_csv(DATA_RAW_DIR / "graph_edges.csv")
    g = nx.DiGraph()

    node_id_col = "node_id" if "node_id" in nodes_df.columns else nodes_df.columns[0]
    node_name_col = "name" if "name" in nodes_df.columns else ("label" if "label" in nodes_df.columns else node_id_col)
    node_type_col = "type" if "type" in nodes_df.columns else ("category" if "category" in nodes_df.columns else None)

    for _, row in nodes_df.iterrows():
        node_id = str(row[node_id_col])
        node_name = str(row[node_name_col])
        node_type = str(row[node_type_col]) if node_type_col else "clinical"
        g.add_node(node_id, name=node_name, label=node_name, category=node_type)

    src_col = "source_id" if "source_id" in edges_df.columns else ("source" if "source" in edges_df.columns else edges_df.columns[0])
    tgt_col = "target_id" if "target_id" in edges_df.columns else ("target" if "target" in edges_df.columns else edges_df.columns[1])
    relation_col = "relation" if "relation" in edges_df.columns else None
    weight_col = "weight" if "weight" in edges_df.columns else None

    for _, row in edges_df.iterrows():
        relation = str(row[relation_col]) if relation_col else "linked_to"
        weight = float(row[weight_col]) if weight_col else 1.0
        g.add_edge(str(row[src_col]), str(row[tgt_col]), relation=relation, weight=weight)
    export = {"nodes": [{"id": n, **g.nodes[n]} for n in g.nodes], "edges": [{"source": u, "target": v, **g.edges[u, v]} for u, v in g.edges]}
    with open(DATA_PROCESSED_DIR / "graph_export.json", "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2)
    return g


def graph_as_payload(g: nx.DiGraph):
    return {"nodes": [{"id": n, **g.nodes[n]} for n in g.nodes], "edges": [{"source": u, "target": v, **g.edges[u, v]} for u, v in g.edges]}
