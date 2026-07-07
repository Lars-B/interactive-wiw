import dash_bootstrap_components as dbc
from dash import Input, Output, State
from dash import html
from dash.dependencies import ALL

from wiw_app.app import app as myapp
from wiw_app.dash_logger import logger
from wiw_app.ids import GraphOptions
from wiw_app.callbacks.coloring.palettes import assign_default_colors, natural_sort_key


@myapp.callback(
    Output(GraphOptions.Nodes.COLOR_PICKER_CONTAINERS, "children"),
    Input("graph-store", "data"),
    Input(GraphOptions.Nodes.COLOR_LABEL_SELECTOR, "value"),
)
def create_nodes_color_picker_panel(graph_data, color_label_selection):
    if not graph_data:
        return html.Div("No node data loaded.")

    nodes = graph_data.get("nodes", [])

    labels = sorted(
        set(node["data"][color_label_selection] for node in nodes),
        key=natural_sort_key
    )

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
                            style={"width": 120, "height": 40,
                                   "marginLeft": "10px",
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
def update_node_label_color_store(values, ids):
    return {id["index"]: val for id, val in zip(ids, values)}
