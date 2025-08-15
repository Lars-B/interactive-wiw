import base64
import networkx as nx
import os
import tempfile
from collections import defaultdict
from networkx.algorithms.tree.branchings import maximum_spanning_arborescence
from pyccd.read_nexus import read_nexus_trees
from pyccd.wiw_network import find_infector

from wiw_app.dash_logger import logger
from wiw_app.utils import log_time


def decode_base64_content(base64_content: str) -> bytes:
    content_type, content_string = base64_content.split(",", 1)
    decoded_content = base64.b64decode(content_string)
    return decoded_content

def handle_uploaded_nexus_file(base64_content):
    decoded_content = decode_base64_content(base64_content)
    tmp = tempfile.NamedTemporaryFile(mode='wb', suffix=".nex", delete=False)
    try:
        tmp.write(decoded_content)
        tmp.flush()
        tmp.close()
        trees, taxon_map = read_nexus_trees(
            tmp.name,
            breath_trees=True,
            label_transm_history=True,
            parse_taxon_map=True
        )
    finally:
        os.remove(tmp.name)
    return trees, taxon_map


def build_graph_from_file(file_content, label, burn_in):
    EDGE_SCALE = 10

    logger.info("Processing file content and building WIW network...")

    with log_time("Handling and reading uploaded nexus file"):
        trees, taxon_map = handle_uploaded_nexus_file(file_content)

    logger.info(f"Found {len(trees)} trees")
    logger.info(f"Extracted taxon map of size: {len(taxon_map)}")

    trees = trees[int(burn_in * len(trees)):]
    num_trees = len(trees)
    logger.info(f"After burn-in there are {num_trees} trees")

    logger.info("Processing trees...")
    with log_time("Processing trees"):
        posterior_wiw_edges = defaultdict(lambda: defaultdict(int))
        for t in trees:
            for leaf in t.get_leaves():
                cur_infector = find_infector(leaf)
                posterior_wiw_edges[leaf.name][cur_infector] += 1

    logger.info("Trees processed, now building the WIW network to add...")

    nodes = []
    for leaf in trees[0].get_leaves():
        nodes.append({"data": {
            "id": leaf.name,
            "label": leaf.name,
            "taxon": taxon_map[int(leaf.name)]
        }})

    edges = []
    edge_count = 1

    net = nx.DiGraph()

    for leaf in posterior_wiw_edges:
        for transm_ancestor in posterior_wiw_edges[leaf]:
            if not transm_ancestor.startswith("Unknown"):
                if not transm_ancestor == leaf:
                    posterior_support = round(posterior_wiw_edges[leaf][transm_ancestor] /
                                              num_trees, 2)

                    edges.append(
                        {"data": {
                            "source": transm_ancestor,
                            "target": leaf,
                            "label": label,
                            "posterior": posterior_support,
                            "weight": round(posterior_support * EDGE_SCALE, 2),
                            "penwidth": 1,
                            'color': "black",
                            'id': f'{label}-{edge_count}'}}
                    )
                    net.add_edge(transm_ancestor, leaf,
                                 weight=round(posterior_support * EDGE_SCALE, 2),
                                 posterior=posterior_support)
                    edge_count += 1

    if num_trees > 1:
        mst = maximum_spanning_arborescence(net, attr="posterior", preserve_attrs=True)
        mst_edges = []
        edge_count = 1
        for u, v, data in mst.edges(data=True):
            mst_edges.append({
                "data": {
                    "source": u,
                    "target": v,
                    "label": f"MST-{label}",
                    "posterior": round(data["posterior"], 2),
                    "weight": data["weight"],
                    "penwidth": 1,
                    "color": "black",
                    "id": f'MST-{edge_count}'
                }
            })
            edge_count += 1

        edges.extend(mst_edges)

    return nodes, edges


def get_cytoscape_style(is_light_theme: bool) -> dict:
    return {
        "width": "100%",
        "height": "100%",
        "backgroundColor": "#ffffff" if is_light_theme else "#1e1e1e",
    }


def get_node_style(annotation_field, font_size, color_by_label) -> dict:
    return {
        "label": f"data({annotation_field})",
        "text-valign": "center",
        "text-halign": "center",
        "text-outline-width": 1,
        "text-outline-color": "#888",
        "backgroundColor": "data(color)" if color_by_label else "#555",
        "color": "#fff",
        "font-size": font_size,
    }


def get_edge_style(annotation_field, label_position, scale_edges,
                   color_by_label, is_light_theme, font_size) -> dict:
    edge_style = {"curve-style": "bezier",
                  "control-point-step-size": 20,
                  "target-arrow-shape": "triangle-backcurve",
                  "color": "#000" if is_light_theme else "#fff",
                  "text-outline-width": 0.2,
                  "text-outline-color": "#000" if is_light_theme else "#ccc",
                  "label": f"data({annotation_field})",
                  "font-size": font_size
                  }

    if scale_edges:
        edge_style["width"] = "data(weight)"
        edge_style["arrow-scale"] = "mapData(data(weight), 0, 1, 0.5, 2)"
    else:
        edge_style["width"] = 2
        edge_style["arrow-scale"] = 1

    if label_position == "above":
        edge_style["text-margin-y"] = -10
    elif label_position == "below":
        edge_style["text-margin-y"] = 10
    elif label_position == "autorotate":
        edge_style["edge-text-rotation"] = "autorotate"
    else:
        edge_style["text-margin-y"] = 0
        edge_style["edge-text-rotation"] = "none"

    if color_by_label:
        # edge_style["color"] = "data(color)"  # this is the label text color
        edge_style["line-color"] = "data(color)"  # this is the edge color
        edge_style["target-arrow-color"] = "data(color)"

    return edge_style


def process_node_annotations_file(file_content):
    logger.info(f"Processing file content for node annotations...")
    decoded_content = decode_base64_content(file_content)

    NODE_ANNOTATIONS_SEPARATOR = "\t"

    node_annotations_map = {}

    for line in decoded_content.decode("UTF-8").strip().split("\n"):
        key, val = line.split(NODE_ANNOTATIONS_SEPARATOR)
        val = val.strip('"').strip("'")
        node_annotations_map[key] = val

    return node_annotations_map
