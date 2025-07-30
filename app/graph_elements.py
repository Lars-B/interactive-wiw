import base64
from collections import defaultdict

from .dash_logger import logger


def build_graph(scale_factor=1):
    # todo this should be a selection when inputting the trees later on, give a color...
    # todo figure out how to  make this dccStore default without calling the function
    #  this is for testing the update function and making it work with file input...
    label_colors = defaultdict(lambda: "purple", {})

    edges = [
        {"data": {
            "source": "A", "target": "B", "label": "set1",
            "weight": 0.01,  # original semantic value
            "penwidth": 0.01 * scale_factor,
            "color": label_colors["set1"],
            "id": "e1"
        }},
        {"data": {
            "source": "A", "target": "B", "label": "set2",
            "weight": 0.5,
            "penwidth": 0.5 * scale_factor,
            "color": label_colors["set2"],
            "id": "e2"
        }},
        {"data": {
            "source": "B", "target": "C", "label": "set1",
            "weight": 0.3,
            "penwidth": 0.3 * scale_factor,
            "color": label_colors["set1"],
            "id": "e3"
        }},
    ]
    nodes = [{"data": {"id": node, "label": node}} for node in {"A", "B", "C"}]
    return nodes, edges


def build_graph_from_file(file_content, label):

    logger.info("Testing this")

    content_type, content_string = file_content.split(",")
    decoded_content = base64.b64decode(content_string)

    logger.warning("This is a warning...")

    # todo need to read this to compute the real network...
    # print("-------- build_graph_from_file start --------\n")
    # print(decoded_content.decode("utf-8")[1:30])
    # print("-------- build_graph_from_file end --------\n")

    # todo figure out how to add a spinner for progress, make a little wait thing here for testing
    # todo return a new node and new edges for current easy graph here, print the file out to
    #  somehting....
    # with open(file_path, "r") as f:
    #     data = json.load(f)  # Or replace with csv.DictReader, etc.
    #
    # for row in data["edges"]:  # customize to match your data structure
    #     source = row["source"]
    #     target = row["target"]
    #     weight = row.get("weight", 1)
    #
    #     nodes.extend([
    #         {"data": {"id": source, "label": source}},
    #         {"data": {"id": target, "label": target}},
    #     ])
    #     edges.append({
    #         "data": {
    #             "source": source,
    #             "target": target,
    #             "label": label,
    #             "weight": weight,
    #             "penwidth": weight * 5,
    #             "color": color,
    #             "id": f"{source}-{target}-{label}"
    #         }
    #     })
    #
    # # De-duplicate nodes
    # seen = set()
    # unique_nodes = []
    # for node in nodes:
    #     if node["data"]["id"] not in seen:
    #         seen.add(node["data"]["id"])
    #         unique_nodes.append(node)
    #
    # return unique_nodes, edges
    nodes = [{"data": {"id": node, "label": node}} for node in {"C", "D", "E"}]
    edges = [{"data": {"source": "C", "target": "D", "label": label, "weight": 0.1,
                       "penwidth": 1, 'color': "black", 'id': 'e10'}},
             {"data": {"source": "E", "target": "D", "label": label, "weight": 0.1,
                       "penwidth": 1, 'color': "black", 'id': 'e11'}}]

    return nodes, edges


def get_cytoscape_style(is_light_theme: bool) -> dict:
    return {
        "width": "100%",
        "height": "100%",
        "backgroundColor": "#ffffff" if is_light_theme else "#1e1e1e",
    }


def get_node_style() -> dict:
    return {
        "label": "data(label)",
        "text-valign": "center",
        "text-halign": "center",
        "text-outline-width": 1,
        "text-outline-color": "#888",
        "backgroundColor": "#555",
        "color": "#fff",
        "font-size": 12,
    }


def get_edge_style(annotation_field, label_position, scale_edges,
                   color_by_label, is_light_theme) -> dict:
    edge_style = {"curve-style": "bezier", "control-point-step-size": 20,
                  "target-arrow-shape": "triangle-backcurve",
                  "color": "#000" if is_light_theme else "#fff", "text-outline-width": 0.2,
                  "text-outline-color": "#000" if is_light_theme else "#ccc",
                  "label": f"data({annotation_field})" if annotation_field != "none" else ""}

    if scale_edges:
        edge_style["width"] = "data(penwidth)"
        edge_style["arrow-scale"] = "data(penwidth)"
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

    return edge_style
