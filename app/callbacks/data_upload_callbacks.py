from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from ..app import app as myapp
from ..dash_logger import logger
from ..graph_elements import build_graph_from_file


@myapp.callback(
    Output("graph-store", "data", allow_duplicate=True),
    Output("loading-modal", "is_open", allow_duplicate=True),
    # Output("log-output", "children"),
    Input("confirm-dataset-btn", "n_clicks"),
    State("upload-trees-data", "contents"),
    State("upload-trees-data", "filename"),
    State("trees-dataset-label", "value"),
    State("burn-in-selection", "value"),
    State("graph-store", "data"),
    prevent_initial_call=True
)
def update_graph_with_dataset(n_clicks, contents, filename, label, burnin, current_graph_data):
    if not contents:
        raise PreventUpdate

    # from .dash_logger import log_buffer
    # log_buffer.clear()

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
    Output("uploaded-datasets-store", "data", allow_duplicate=True),
    Input("confirm-dataset-btn", "n_clicks"),
    State("upload-trees-data", "contents"),
    State("upload-trees-data", "filename"),
    State("trees-dataset-label", "value"),
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
    Output("selected-trees-filename", "children"),
    Output("trees-dataset-label", "value"),
    Input("upload-trees-data", "filename"),
)
def display_tree_file_name(filename):
    if filename:
        return f"Selected file: {filename}", filename
    return "No file selected yet.", ""


@myapp.callback(
    Output("selected-node-annotations-file", "children"),
    Input("upload-node-annotations", "filename"),
)
def display_node_annotation_file_name(filename):
    if filename:
        return f"Selected file: {filename}"
    return "No file selected yet."
