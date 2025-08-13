import re

import dash_bootstrap_components as dbc
from dash import Input, Output, State
from dash import callback_context
from dash import html
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate

from wiw_app.app import app as myapp
from wiw_app.dash_logger import logger
from wiw_app.ids import UploadIDs, GraphOptions
from wiw_app.utils import assign_default_colors


@myapp.callback(
    Output("loading-modal", "is_open"),
    [
        Input(UploadIDs.CONFIRM_TREES_DATASET_BTN, "n_clicks"),
        Input(UploadIDs.CONFIRM_NODE_ANNOTATIONS_BTN, "n_clicks"),
        # Input("graph-store", "data"),
    ],
    [
        State("loading-modal", "is_open"),
        State(UploadIDs.UPLOAD_TREES_DATA, "contents"),
        State(UploadIDs.UPLOAD_NODE_ANNOTATIONS, "contents"),
    ],
    prevent_initial_call=True,
)
def toggle_loading_modal(n_clicks_trees, n_clicks_nodeann, is_open, trees_contents,
                         nodeann_contents):
    triggered_id = callback_context.triggered_id

    # from ..dash_logger import logger
    # logger.debug(f"The triggered id is: {triggered_id}")
    # logger.debug(f"The nodeann_contents is: {nodeann_contents}")

    if triggered_id == UploadIDs.CONFIRM_TREES_DATASET_BTN and trees_contents:
        return True
    elif triggered_id == UploadIDs.CONFIRM_NODE_ANNOTATIONS_BTN and nodeann_contents:
        return True
    # todo i think this is pointless
    # elif triggered_id in ["graph-store", UploadIDs.UPLOADED_NODE_ANNOTATIONS_STORE]:
    #     return False  # close modal when graph data updated

    return is_open  # default: no change


@myapp.callback(
    Output(GraphOptions.Edges.ADVANCED_OPTIONS_COLLAPSE, "is_open"),
    Output(GraphOptions.Edges.ADVANCED_OPTIONS_ICON, "icon"),
    Input(GraphOptions.Edges.ADVANCED_OPTION_TOGGLE_BTN, "n_clicks"),
    State(GraphOptions.Edges.ADVANCED_OPTIONS_COLLAPSE, "is_open"),
    prevent_initial_call=True
)
def toggle_advanced_edge_options(n_clicks, is_open):
    if n_clicks is None:
        raise PreventUpdate
    new_is_open = not is_open
    new_icon = "mdi:cheese" if new_is_open else "mdi:cheese-off"
    return new_is_open, new_icon


@myapp.callback(
    Output(GraphOptions.Nodes.ADVANCED_OPTIONS_COLLAPSE, "is_open"),
    Output(GraphOptions.Nodes.ADVANCED_OPTIONS_ICON, "icon"),
    Input(GraphOptions.Nodes.ADVANCED_OPTION_TOGGLE_BTN, "n_clicks"),
    State(GraphOptions.Nodes.ADVANCED_OPTIONS_COLLAPSE, "is_open"),
    prevent_initial_call=True
)
def toggle_advanced_node_options(n_clicks, is_open):
    if n_clicks is None:
        raise PreventUpdate
    new_is_open = not is_open
    new_icon = "mdi:cheese" if new_is_open else "mdi:cheese-off"
    return new_is_open, new_icon


@myapp.callback(
    Output(GraphOptions.Edges.COLOR_PICKERS_COLLAPSE, "is_open"),
    Input(GraphOptions.Edges.COLOR_BY_LABEL, "value"),
)
def toggle_edge_color_pickers(toggle_values):
    # Show if 'color' is in checklist values, else hide
    return "color" in toggle_values


@myapp.callback(
    Output(GraphOptions.Edges.COLOR_PICKER_CONTAINERS, "children"),
    Input("graph-store", "data")
)
def create_edge_color_picker_panel(graph_data, label_colors=None):
    if not graph_data:
        return html.Div("No graph data loaded.")

    edges = graph_data.get("edges", [])
    labels = sorted(set(edge["data"]["label"] for edge in edges))

    # Get dynamic default colors
    # todo this redundant can just do the default colors here?...
    default_colors = assign_default_colors(labels)

    # Override with edge_label_colors if given
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
    Output(GraphOptions.Edges.COLOR_STORE, "data"),
    Input({"type": "color-input", "index": ALL}, "value"),
    State({"type": "color-input", "index": ALL}, "id")
)
def update_label_color_store(values, ids):
    return {id["index"]: val for id, val in zip(ids, values)}


@myapp.callback(
    Output(GraphOptions.Nodes.COLOR_PICKERS_COLLAPSE, "is_open"),
    Input(GraphOptions.Nodes.COLOR_BY_LABEL, "value"),
)
def toggle_node_color_pickers(toggle_values):
    # Show if 'color' is in checklist values, else hide
    return "color" in toggle_values


@myapp.callback(
    Output(GraphOptions.Nodes.COLOR_PICKER_CONTAINERS, "children"),
    Input("graph-store", "data"),
    Input(GraphOptions.Nodes.COLOR_LABEL_SELECTOR, "value"),
)
def create_nodes_color_picker_panel(graph_data, color_label_selection):
    if not graph_data:
        return html.Div("No node data loaded.")

    nodes = graph_data.get("nodes", [])

    labels = sorted(set(node["data"][color_label_selection] for node in nodes))

    # Get dynamic default colors
    # todo this redundant can just do the default colors here?...
    default_colors = assign_default_colors(labels)

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
                        dbc.Label(
                            label,
                            style={"width": 120, "height": 40, "marginLeft": "10px",
                                   "lineHeight": "40px"}
                        ),
                        width="auto"
                    )
                ],
                align="center",
                style={"marginBottom": "8px"},
                key=label
            )
            for label in labels
        ]
    )


@myapp.callback(
    Output(GraphOptions.Nodes.COLOR_STORE, "data"),
    Input({"type": "color-input", "index": ALL}, "value"),
    State({"type": "color-input", "index": ALL}, "id")
)
def update_label_color_store(values, ids):
    return {id["index"]: val for id, val in zip(ids, values)}


@myapp.callback(
    Output(UploadIDs.NODE_ANNOTATIONS_LABEL, "value", allow_duplicate=True),
    Output("node-annotations-label-warning", "children"),
    Output(UploadIDs.CONFIRM_NODE_ANNOTATIONS_BTN, "disabled"),
    Output(UploadIDs.UPLOAD_NODE_ANNOTATIONS, "disabled"),
    Output(UploadIDs.NODE_ANNOTATIONS_LABEL, "disabled"),
    Input(UploadIDs.NODE_ANNOTATIONS_LABEL, "value"),
    Input("graph-store", "data"),
    prevent_initial_call=True
)
def sanitize_node_annotations_label(label, graph_data):
    if not graph_data or not graph_data.get("nodes"):
        return "", "Please Upload a graph before using this feature!", True, True, True

    DEFAULT_LABEL = "Cheese"
    if not label:
        # raise PreventUpdate
        logger.info("No label provided, setting default value")
        return DEFAULT_LABEL, f"No label provided - defaulting to '{DEFAULT_LABEL}'", False, False, False

    sanitized_label = re.sub(r'[^a-zA-Z0-9_]', '', label)

    if sanitized_label != label:
        if sanitized_label == "":
            sanitized_label = DEFAULT_LABEL
        logger.info(f"Invalid characters removed from '{label}', new label: {sanitized_label}")
        return sanitized_label, f"Invalid characters removed - {sanitized_label}", False, False, False

    return label, "", False, False, False
