from dash import Input, Output, callback_context, State

from ..app import app as myapp


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
