from collections import Counter

from dash import Input, Output, State, ALL, no_update, callback
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO

from wiw_app.app import app as myapp
from wiw_app.graph_elements import get_node_style, get_edge_style, get_cytoscape_style
from wiw_app.ids import GraphOptions
from wiw_app.plotting_utils import draw_legend


# Stylesheet fixed for the legend that can be added now
LEGEND_NODE_ID = "__legend__"
legend_styles = [
    {
        "selector": f"#{LEGEND_NODE_ID}",
        "style": {
            "shape": "rectangle",
            "width": "200px",
            "height": "300px",
            "background-image": "data(legend)",  # Cytoscape picks up legend SVG from node data
            "background-fit": "contain",
            "background-repeat": "no-repeat",
            "border-width": 1,
            "border-color": "#999",
        }
    }
]


@myapp.callback(
    Output('cytoscape', 'elements'),
    Output('cytoscape', 'layout'),
    Output('cytoscape', 'stylesheet'),
    Input("graph-store", "data"),
    Input('label-filter', 'value'),
    Input('layout-selector', 'value'),
    Input('scale-width-toggle', 'value'),
    Input('edge-annotation-selector', 'value'),
    Input("edge-label-position", "value"),
    Input('weight-threshold', 'value'),
    Input('edge-label-font-size', 'value'),
    Input('node-label-font-size', 'value'),
    Input(GraphOptions.Edges.COLOR_BY_LABEL, "value"),
    Input(GraphOptions.Edges.COLOR_STORE, "data"),
    Input(GraphOptions.Nodes.COLOR_BY_LABEL, "value"),
    Input(GraphOptions.Nodes.COLOR_STORE, "data"),
    Input(GraphOptions.Nodes.COLOR_LABEL_SELECTOR, "value"),
    Input(GraphOptions.Nodes.SUPRESS_SINGLETONS, "value"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    Input(GraphOptions.Nodes.LABEL_ANNOTATION_SELECTOR, "value")
)
def update_elements(graph_data, selected_labels, selected_layout,
                    scale_toggle, annotation_field, label_position, threshold,
                    edge_label_font_size, node_label_font_size, edge_color_toggle,
                    edge_label_colors, node_color_toggle, node_label_colors,
                    node_color_label_selection, supress_singletons,
                    is_light_theme, node_annotation_selection):
    scale_edges = "scale" in scale_toggle

    threshold = min(max(threshold or 0, 0), 1)

    if not graph_data:
        raise PreventUpdate

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    filtered_edges = []
    seen_nodes_source = set()
    seen_nodes_target = set()
    for e in edges:
        if e["data"]["label"] in selected_labels and e["data"].get("posterior", 0) >= threshold:
            filtered_edges.append(e)
            seen_nodes_source.add(e["data"]["source"])
            seen_nodes_target.add(e["data"]["target"])

    supress_singletons_bool = "on" in supress_singletons
    filtered_nodes = nodes

    seen_nodes = seen_nodes_target | seen_nodes_source
    terminal_nodes = (
            (seen_nodes_source - seen_nodes_target) |
            (seen_nodes_target - seen_nodes_source)
    )

    if supress_singletons_bool:
        filtered_nodes = []
        for n in nodes:
            if n["data"]["id"] in seen_nodes:
                filtered_nodes.append(n)

    for node in filtered_nodes:
        label = node["data"][node_color_label_selection]
        node["data"]["color"] = node_label_colors.get(label, "green")
        if node["data"]["id"] in terminal_nodes:
            node["data"]["shape"] = "rectangle"
        elif node["data"]["id"] not in seen_nodes:
            node["data"]["shape"] = "triangle"
        else:
            node["data"]["shape"] = "ellipse"

    # this updates to the correct colors
    for edge in filtered_edges:
        label = edge["data"]["label"]
        edge["data"]["color"] = edge_label_colors.get(label, "purple")

    elements = filtered_nodes + filtered_edges
    layout = {"name": selected_layout}

    stylesheet = [
        {"selector": "node",
         "style": get_node_style(node_annotation_selection,
                                 node_label_font_size,
                                 node_color_toggle)},
        {"selector": "edge",
         "style": get_edge_style(annotation_field,
                                 label_position,
                                 scale_edges,
                                 edge_color_toggle,
                                 is_light_theme,
                                 edge_label_font_size)},
    ] + legend_styles

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
    Output(GraphOptions.Edges.LABEL_RENAME_ERROR, "children"),
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


@callback(
    Output("cytoscape", "elements", allow_duplicate=True),
    Input("btn-add-legend-node", "n_clicks"),
    Input("btn-remove-legend-node", "n_clicks"),
    State("cytoscape", "elements"),
    State(GraphOptions.Nodes.COLOR_PICKER_CONTAINERS, "children"),
    State(GraphOptions.Nodes.COLOR_BY_LABEL, "value"),
    State(GraphOptions.Nodes.COLOR_LABEL_SELECTOR, "value"),
    State(GraphOptions.Nodes.COLOR_LABEL_SELECTOR, "options"),
    State(GraphOptions.Edges.COLOR_PICKER_CONTAINERS, "children"),
    State(GraphOptions.Edges.COLOR_BY_LABEL, "value"),
    prevent_initial_call=True,
)
def toggle_legend(
        add_clicks,
        remove_clicks,
        elements,
        node_color_container, node_color_toggle, node_color_title, node_color_options,
        edge_color_container, edge_color_toggle
):
    import dash

    ctx = dash.callback_context
    if not ctx.triggered:
        return elements

    trigger = ctx.triggered[0]["prop_id"].split(".")[0]

    # Remove legend
    if trigger == "btn-remove-legend-node":
        return [el for el in elements if el["data"]["id"] != LEGEND_NODE_ID]

    # Add legend
    if trigger == "btn-add-legend-node":
        if any(el["data"]["id"] == LEGEND_NODE_ID for el in elements):
            return elements  # already exists

        legend_svg = draw_legend(
            node_color_options,
            node_color_title,
            node_color_toggle,
            node_color_container,
            edge_color_toggle,
            edge_color_container,
            svg=True
        )

        import urllib.parse

        # todo needs some more features, like resizing option
        #  and shouldn't be removed with update graph

        encoded_svg = urllib.parse.quote(legend_svg)
        legend_node = {
            "data": {
                "id": LEGEND_NODE_ID,
                "legend": f"data:image/svg+xml;utf8,{encoded_svg}"
            },
            "position": {"x": 1000, "y": 100},
            "grabbable": True,
        }

        return elements + [legend_node]

    return elements
