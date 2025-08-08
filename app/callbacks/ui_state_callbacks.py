import dash_bootstrap_components as dbc
from dash import Input, Output, State
from dash import callback_context
from dash import html
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate

from ..app import app as myapp
from ..utils import assign_default_colors


@myapp.callback(
    Output("loading-modal", "is_open"),
    [
        Input("confirm-dataset-btn", "n_clicks"),
        Input("graph-store", "data"),  # closes modal after dataset loads
    ],
    [
        State("loading-modal", "is_open"),
        State("upload-trees-data", "contents"),
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
    Output("slider-collapse", "is_open"),
    Output("value-selections-button-icon", "icon"),
    Input("toggle-sliders-btn", "n_clicks"),
    State("slider-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_slider_section(n_clicks, is_open):
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
