from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from contagion.app import app as myapp
from contagion.dash_logger import logger
from contagion.graph_elements import build_graph_from_dot_file
from contagion.ids import UploadIDs, GraphOptions


@myapp.callback(
    Output("graph-store", "data", allow_duplicate=True),
    Output(GraphOptions.Edges.DISPLAY_FILTER, "value", allow_duplicate=True),
    Input(UploadIDs.dot_file.CONFIRM_BUTTON, "n_clicks"),
    State(UploadIDs.dot_file.UPLOAD_DATA, "contents"),
    State(UploadIDs.dot_file.UPLOAD_DATA, "filename"),
    State(UploadIDs.dot_file.DATASET_LABEL, "value"),
    State(GraphOptions.Edges.DISPLAY_FILTER, "value"),
    State("graph-store", "data"),
    prevent_initial_call=True
)
def update_graph_with_dot_file(n_clicks, contents, filename, label, current_edge_selection, current_graph_data):
    if not contents:
        raise PreventUpdate

    logger.debug("We are in the dot file graph format callback....")

    current_graph_data = current_graph_data or {"nodes": [], "edges": []}

    effective_label = label or filename
    new_nodes, new_edges = build_graph_from_dot_file(contents, effective_label)

    # todo from here onwards

    existing_ids = {n["data"]["id"] for n in current_graph_data["nodes"]}
    true_new_nodes = [
        n for n in new_nodes
        if n["data"]["id"] not in existing_ids
    ]
    merged_nodes = current_graph_data["nodes"] + true_new_nodes

    logger.info("Finished updating the graph.")

    new_edge_labels = {e.get('data', {}).get('label', {}) for e in new_edges}
    new_edge_selection = current_edge_selection + list(new_edge_labels)

    return (
        {
            "nodes": merged_nodes,
            "edges": current_graph_data["edges"] + new_edges
        },
        new_edge_selection
    )
