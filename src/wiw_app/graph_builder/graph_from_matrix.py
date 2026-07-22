from collections import Counter

from wiw_app.dash_logger import logger
import pandas as pd
import networkx as nx

from wiw_app.graph_builder.utils import generate_mst_edges_from_network


def build_graph_from_wiw_matrix(mat, label):
    logger.info("Building WIW network graph from matrix data...")

    # -------------------------
    # handle DataFrame or ndarray
    # -------------------------
    if isinstance(mat, pd.DataFrame):
        node_ids = list(mat.index)
        mat = mat.values
    else:
        node_ids = list(range(1, mat.shape[0] + 1))

    n = mat.shape[0]

    # -------------------------
    # edges
    # -------------------------
    edges = []
    node_strength = Counter()
    edge_id = 0
    net = nx.DiGraph()

    for i in range(n):  # infector
        for j in range(n):  # infectee
            weight = mat[i, j]

            if weight == 0:
                continue

            source = i + 1
            target = j + 1

            edges.append({
                "data": {
                    "source": str(source),
                    "target": str(target),
                    "label": label,
                    "posterior": round(float(weight), 4),
                    "weight": round(float(weight), 4),
                    "color": "black",
                    "id": f"{label}-{edge_id}",
                }
            })

            net.add_edge(
                str(source),
                str(target),
                weight=round(float(weight), 4),
                posterior=round(float(weight), 4),
            )
            node_strength[source] += float(weight)
            edge_id += 1

    # Construct MST if possible
    if net.number_of_nodes() > 0:
        mst_edges = generate_mst_edges_from_network(net, label)
        edges.extend(mst_edges)

    # -------------------------
    # nodes
    # -------------------------
    nodes = []

    for i in range(n):
        node_id = i + 1

        nodes.append({
            "data": {
                "id": str(node_id),
                "taxon": str(node_id) if node_ids is None else str(node_ids[i])
                # todo this could possibly be used to size the nodes
                # "strength": round(node_strength[node_id], 6),
            }
        })

    return nodes, edges
