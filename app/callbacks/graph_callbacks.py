from collections import Counter

from dash import Input, Output, State, ALL, no_update
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO

from ..app import app as myapp
from ..ids import UploadIDs
from ..graph_elements import get_node_style, get_edge_style, get_cytoscape_style


@myapp.callback(
    Output('cytoscape', 'elements'),
    Output('cytoscape', 'layout'),
    Output('cytoscape', 'stylesheet'),
    Input("graph-store", "data"),
    Input(UploadIDs.UPLOADED_NODE_ANNOTATIONS_STORE, "data"),
    Input('label-filter', 'value'),
    Input('layout-selector', 'value'),
    Input('scale-width-toggle', 'value'),
    Input('edge-annotation-selector', 'value'),
    Input("edge-label-position", "value"),
    Input('weight-threshold', 'value'),
    Input('edge-label-font-size', 'value'),
    Input('node-label-font-size', 'value'),
    Input("color-by-label-toggle", "value"),
    Input("label-color-store", "data"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    Input("node-annotation-selector", "value")
)
def update_elements(graph_data, uploaded_node_annotation_data, selected_labels, selected_layout,
                    scale_toggle, annotation_field, label_position, threshold,
                    edge_label_font_size, node_label_font_size, color_toggle, label_colors,
                    is_light_theme, node_annotation_selection):
    scale_edges = "scale" in scale_toggle

    threshold = min(max(threshold or 0, 0), 1)

    if not graph_data:
        raise PreventUpdate

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    filtered_edges = [e for e in edges if e["data"]["label"] in selected_labels
                      and e["data"].get("posterior", 0) >= threshold]

    # this adds the user uploaded node annotation map to the nodes of the graph:
    if uploaded_node_annotation_data:
        uploaded_map = uploaded_node_annotation_data["map"]
        uploaded_label = uploaded_node_annotation_data["label"]
        for n in nodes:
            new_data = uploaded_map.get(n["data"]["taxon"], "")
            n["data"][uploaded_label] = new_data

    # this updates to the correct colors
    for edge in filtered_edges:
        label = edge["data"]["label"]
        edge["data"]["color"] = label_colors.get(label, "purple")

    elements = nodes + filtered_edges
    layout = {"name": selected_layout}

    stylesheet = [
        {"selector": "node",
         "style": get_node_style(node_annotation_selection,
                                 node_label_font_size)},
        {"selector": "edge",
         "style": get_edge_style(annotation_field,
                                 label_position,
                                 scale_edges,
                                 color_toggle,
                                 is_light_theme,
                                 edge_label_font_size)},
    ]

    return elements, layout, stylesheet


@myapp.callback(
    Output("cytoscape", "style", allow_duplicate=True),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    prevent_initial_call=True
)
def update_cytoscape_style(is_light_theme):
    return get_cytoscape_style(is_light_theme)


@myapp.callback(
    Output("confirm-reset", "displayed"),
    Input("reset-graph-btn", "n_clicks"),
    prevent_initial_call=True
)
def show_reset_popup(_):
    return True


@myapp.callback(
    Output("graph-store", "data"),
    Input("confirm-reset", "submit_n_clicks"),
    prevent_initial_call=True
)
def reset_graph(_):
    return {"nodes": [], "edges": []}


@myapp.callback(
    Output("label-filter", "options"),
    Output("label-filter", "value"),
    Input("graph-store", "data"),
    prevent_initial_call=True
)
def update_label_filter_options(graph_data):
    if not graph_data:
        raise PreventUpdate

    edges = graph_data.get("edges", [])
    labels = sorted({edge["data"].get("label") for edge in edges if "label" in edge["data"]})

    options = [{"label": label, "value": label} for label in labels]
    return options, labels


@myapp.callback(
    Output("graph-store", "data", allow_duplicate=True),
    Output("rename-error", "children"),
    Input({"type": "label-rename-input", "index": ALL}, "value"),
    State({"type": "label-rename-input", "index": ALL}, "id"),
    State("graph-store", "data"),
    prevent_initial_call=True
)
def rename_labels(new_labels, ids, graph_data):
    if not graph_data:
        raise PreventUpdate

    label_map = {id_["index"]: new_label for id_, new_label in zip(ids, new_labels)}

    # Validate: check for duplicates in target new labels
    label_counts = Counter(label_map.values())
    duplicates = [label for label, count in label_counts.items() if count > 1]

    if duplicates:
        return no_update, f"Error: Duplicate label names are not allowed: {', '.join(duplicates)}"

    # Proceed with update
    updated_edges = []
    for edge in graph_data["edges"]:
        old_label = edge["data"]["label"]
        new_label = label_map.get(old_label, old_label)
        edge["data"]["label"] = new_label
        updated_edges.append(edge)

    return {
        "nodes": graph_data["nodes"],
        "edges": updated_edges
    }, ""
