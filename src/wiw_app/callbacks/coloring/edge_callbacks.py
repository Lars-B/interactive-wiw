import dash_bootstrap_components as dbc
from dash import Input, Output
from dash import html

from wiw_app.app import app as myapp
from wiw_app.ids import GraphOptions
from wiw_app.callbacks.coloring.palettes import assign_default_colors


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
                            style={"width": 120, "height": 40,
                                   "marginLeft": "10px"}
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
