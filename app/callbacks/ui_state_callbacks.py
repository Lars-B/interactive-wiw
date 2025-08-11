import dash_bootstrap_components as dbc
from dash import Input, Output, State
from dash import callback_context
from dash import html
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate

from ..app import app as myapp
from ..ids import UploadIDs, GraphOptions
from ..utils import assign_default_colors


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
    Output("color-pickers-collapse", "is_open"),
    Input("color-by-label-toggle", "value"),
)
def toggle_color_pickers(toggle_values):
    # Show if 'color' is in checklist values, else hide
    return "color" in toggle_values


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
    Output("label-color-store", "data"),
    Input({"type": "color-input", "index": ALL}, "value"),
    State({"type": "color-input", "index": ALL}, "id")
)
def update_label_color_store(values, ids):
    return {id["index"]: val for id, val in zip(ids, values)}
