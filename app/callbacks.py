from collections import Counter

import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import networkx as nx
from dash import Input, Output, State, dash, no_update, callback_context, ctx, dcc
from dash import html
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO
from networkx.drawing.nx_pydot import to_pydot

from .app import app as myapp
from .dash_logger import logger
from .graph_elements import get_node_style, get_cytoscape_style, get_edge_style, \
    build_graph_from_file
from .utils import assign_default_colors

cyto.load_extra_layouts()


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
    Input("color-by-label-toggle", "value"),
    Input("label-color-store", "data"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def update_elements(graph_data, selected_labels, selected_layout, scale_toggle, annotation_field,
                    label_position, threshold, edge_label_font_size, color_toggle, label_colors,
                    is_light_theme):
    scale_edges = "scale" in scale_toggle

    threshold = min(max(threshold or 0, 0), 1)

    if not graph_data:
        raise PreventUpdate

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    filtered_edges = [e for e in edges if e["data"]["label"] in selected_labels
                      and e["data"].get("posterior", 0) >= threshold]

    # this updates to the correct colors
    for edge in filtered_edges:
        label = edge["data"]["label"]
        edge["data"]["color"] = label_colors.get(label, "purple")

    elements = nodes + filtered_edges
    layout = {"name": selected_layout}

    stylesheet = [
        {"selector": "node",
         "style": get_node_style()},
        {"selector": "edge", "style": get_edge_style(annotation_field,
                                                     label_position,
                                                     scale_edges,
                                                     color_toggle,
                                                     is_light_theme,
                                                     edge_label_font_size)},
    ]

    return elements, layout, stylesheet


myapp.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            const container = document.querySelector('[id="cytoscape"]');
            const cy = container && container._cyreg && container._cyreg.cy;
            if (cy) {
                cy.fit();
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('cytoscape', 'elements', allow_duplicate=True),
    Input('recenter-btn', 'n_clicks'),
    prevent_initial_call=True
)


@myapp.callback(
    Output("color-pickers-container", "children"),
    Input("graph-store", "data")  # or trigger when scale/layout/etc. change
)
def create_color_picker_panel(graph_data, label_colors=None):
    if not graph_data:
        return html.Div("No graph data loaded.")

    edges = graph_data.get("edges", [])
    labels = sorted(set(edge["data"]["label"] for edge in edges))

    # Get dynamic default colors
    # todo this redundant can just do the default colors here?...
    default_colors = assign_default_colors(labels)

    # Override with label_colors if given
    if label_colors:
        default_colors.update(label_colors)

    def color_dropdown(label):
        return dbc.Input(
            id={"type": "color-input", "index": label},
            type="color",
            value=default_colors[label],
            style={
                "width": 60,
                "height": 40,
                "marginBottom": "2px",
                "padding": 0,
                "border": "none"
            }
        )

    return html.Div(
        style={
            "maxHeight": "300px",
            "overflowY": "auto",
            "overflowX": "hidden",
            "width": "100%",
            "border": "1px solid #ddd",
            "padding": "5px"
        },
        children=[
            dbc.Row(
                [
                    dbc.Col(color_dropdown(label), width="auto"),
                    dbc.Col(
                        dbc.Input(
                            id={"type": "label-rename-input", "index": label},
                            type="text",
                            value=label,
                            debounce=True,
                            style={"width": 120, "height": 40, "marginLeft": "10px"}
                        ),
                        width="auto"),
                ],
                align="center",
                style={"marginBottom": "8px"},
                key=label
            )
            for label in labels
        ]
    )


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
        raise dash.exceptions.PreventUpdate

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


@myapp.callback(
    Output("label-color-store", "data"),
    Input({"type": "color-input", "index": ALL}, "value"),
    State({"type": "color-input", "index": ALL}, "id")
)
def update_label_color_store(values, ids):
    return {id["index"]: val for id, val in zip(ids, values)}


@myapp.callback(
    Output("color-pickers-collapse", "is_open"),
    Input("color-by-label-toggle", "value"),
)
def toggle_color_pickers(toggle_values):
    # Show if 'color' is in checklist values, else hide
    return "color" in toggle_values


@myapp.callback(
    Output("uploaded-datasets-store", "data", allow_duplicate=True),
    Input("confirm-dataset-btn", "n_clicks"),
    State("upload-data", "contents"),
    State("upload-data", "filename"),
    State("dataset-label", "value"),
    State("uploaded-datasets-store", "data"),
    prevent_initial_call=True
)
def store_uploaded_dataset(n_clicks, contents, filename, label, existing_data):
    if not contents or not label:
        raise PreventUpdate

    new_dataset = {
        "filename": filename,
        "contents": contents,  # base64 string
        "label": label,
    }

    existing_data = existing_data or []
    existing_data.append(new_dataset)
    return existing_data


@myapp.callback(
    Output("selected-filename", "children"),
    Input("upload-data", "filename"),
)
def display_filename(filename):
    if filename:
        return f"Selected file: {filename}"
    return "No file selected yet."


@myapp.callback(
    Output("graph-store", "data", allow_duplicate=True),
    Output("loading-modal", "is_open", allow_duplicate=True),
    # Output("log-output", "children"),
    Input("confirm-dataset-btn", "n_clicks"),
    State("upload-data", "contents"),
    State("upload-data", "filename"),
    State("dataset-label", "value"),
    State("burn-in-selection", "value"),
    State("graph-store", "data"),
    prevent_initial_call=True
)
def update_graph_with_dataset(n_clicks, contents, filename, label, burnin, current_graph_data):
    if not contents:
        raise PreventUpdate

    from .dash_logger import log_buffer
    log_buffer.clear()

    effective_label = label or filename

    new_nodes, new_edges = build_graph_from_file(contents, effective_label, burnin)

    # Merge with current graph (if any)
    current_graph_data = current_graph_data or {"nodes": [], "edges": []}

    logger.info("Finished updating the graph.")

    return (
        {"nodes": current_graph_data["nodes"] + new_nodes,
         "edges": current_graph_data["edges"] + new_edges},
        False,  # Close modal
        # "\n".join(log_buffer)
    )


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
    Output("loading-modal", "is_open"),
    [
        Input("confirm-dataset-btn", "n_clicks"),
        Input("graph-store", "data"),  # closes modal after dataset loads
    ],
    [
        State("loading-modal", "is_open"),
        State("upload-data", "contents"),
    ],
    prevent_initial_call=True,
)
def toggle_loading_modal(n_clicks, graph_data, is_open, contents):
    triggered_id = callback_context.triggered_id

    if triggered_id == "confirm-dataset-btn" and contents:
        return True  # show modal on button click
    elif triggered_id == "graph-store":
        return False  # hide modal when graph data is updated
    return is_open


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
    Output("cytoscape", "generateImage"),
    [
        Input("btn-get-jpg", "n_clicks"),
        Input("btn-get-png", "n_clicks"),
        Input("btn-get-svg", "n_clicks"),
        Input("image-filename-input", "value")
    ]
)
def get_image(get_jpg_clicks, get_png_clicks, get_svg_clicks, filename):
    action = 'store'
    ftype = 'png'
    filename = filename.strip()

    if ctx.triggered_id and ctx.triggered_id.startswith("btn-get-"):
        action = "download"
        ftype = ctx.triggered_id.split("-")[-1]

    return {
        'type': ftype,
        'action': action,
        "filename": filename
    }


@myapp.callback(
    Output("download-dot", 'data'),
    Input("btn-get-dot", "n_clicks"),
    Input("image-filename-input", "value"),
    State("cytoscape", "elements"),
    prevent_initial_call=True
)
def export_to_dot(n_clicks, filename, elements):
    logger.info("Exporting to dot...")
    G = nx.DiGraph()
    for el in elements:
        data = el.get("data", {})
        if "source" in data and "target" in data:
            G.add_edge(data["source"], data["target"], **data)
        elif "id" in data:
            G.add_node(data["id"], **data)
    logger.info("Writing current graph to dot string...")
    dot_str = to_pydot(G).to_string()
    logger.info("Returning dot string for download...")
    return dcc.send_string(dot_str, f"{filename}.dot")
