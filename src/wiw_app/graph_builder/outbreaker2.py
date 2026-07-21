from collections import Counter

import networkx as nx
import pandas as pd

from wiw_app.graph_builder.utils import load_rds_object_pyreadr
from wiw_app.graph_elements import generate_mst_edges_from_network


def build_graph_from_outbreaker_rds(file_content, label):
    obj = load_rds_object_pyreadr(file_content)
    new_nodes, new_edges = build_graph_from_outbreaker_datframe(obj, label)
    return new_nodes, new_edges


def build_graph_from_outbreaker_datframe(res, label):
    alpha_prefix = "alpha"  # outbreaker2 specific...

    alpha_cols = [c for c in res.columns if c.startswith(alpha_prefix)]

    alpha_mat = res[alpha_cols]

    n_states = len(alpha_cols)
    n_samples = len(alpha_mat)

    # -------------------------
    # edges
    # -------------------------
    edge_counter = Counter()

    for state_idx, col in enumerate(alpha_cols, start=1):
        for source in alpha_mat[col]:
            if pd.isna(source):
                continue

            source = int(source)
            target = state_idx

            edge_counter[(source, target)] += 1

    edges = []
    node_strength = Counter()
    net = nx.DiGraph()

    for edge_id, ((source, target), count) in enumerate(edge_counter.items()):
        weight = count / n_samples

        edges.append({
            "data": {
                "source": str(source),
                "target": str(target),
                "label": label,
                "posterior": round(weight, 2),
                # todo think about making this round an input value?
                "weight": round(weight, 2),
                "color": "black",
                "id": f"{label}-{edge_id}",
            }
        })

        net.add_edge(
            str(source),
            str(target),
            weight=round(weight, 2),
            posterior=round(weight, 2)
        )
        node_strength[source] += weight

    # Construct MST if possible:
    if net.number_of_nodes() > 1:
        mst_edges = generate_mst_edges_from_network(net, label)
        edges.extend(mst_edges)

    # -------------------------
    # nodes
    # -------------------------
    nodes = []

    for node_id in range(1, n_states + 1):
        nodes.append({
            "data": {
                "id": str(node_id),
                "label": str(node_id),
            }
        })

    return nodes, edges
