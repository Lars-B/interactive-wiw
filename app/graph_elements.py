from collections import defaultdict


def build_graph(scale_factor=1, label_colors=None):
    # todo this should be a selection when inputting the trees later on, give a color...
    label_colors = defaultdict(lambda: "purple", label_colors or {})

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
    # for edge in edges:
    #     label = edge["data"].get("label")
    #     edge["data"]["color"] = LABEL_COLORS.get(label, "gray")
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
