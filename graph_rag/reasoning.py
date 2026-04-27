def graph_reasoning(patient_text: str, graph):
    text = patient_text.lower()
    links = []
    evidence = []

    matched_nodes = []
    for node_id, attrs in graph.nodes(data=True):
        node_name = str(attrs.get("name", attrs.get("label", node_id))).lower()
        if node_name and node_name in text:
            matched_nodes.append(node_id)

    heuristics = {
        "diabetes": "diabetes",
        "chest pain": "chest pain on exertion",
        "family history": "family history CAD",
        "ldl": "high LDL",
        "exertional": "chest pain on exertion",
    }
    for token, node_name in heuristics.items():
        if token in text:
            hit = next((n for n, d in graph.nodes(data=True) if str(d.get("name", "")).lower() == node_name.lower()), None)
            if hit is not None and hit not in matched_nodes:
                matched_nodes.append(hit)

    for source in matched_nodes:
        for _, target, edge in graph.out_edges(source, data=True):
            source_name = graph.nodes[source].get("name", graph.nodes[source].get("label", source))
            target_name = graph.nodes[target].get("name", graph.nodes[target].get("label", target))
            link = {
                "source": source_name,
                "target": target_name,
                "relation": edge.get("relation", "linked_to"),
                "weight": float(edge.get("weight", 1.0)),
            }
            if link not in links:
                links.append(link)
                evidence.append(f"{source_name} -> {target_name} ({edge.get('relation', 'linked_to')})")

    if not links:
        evidence.append("No high-confidence graph trigger found. Continue baseline preventive stratification.")

    return {"links": links, "evidence_summary": evidence}
