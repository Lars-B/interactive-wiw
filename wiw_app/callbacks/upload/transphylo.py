from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from wiw_app.app import app as myapp
from wiw_app.dash_logger import logger
from wiw_app.graph_elements import build_graph_from_transphylo_rds
from wiw_app.ids import UploadIDs


@myapp.callback(
    Output("graph-store", "data", allow_duplicate=True),
    Input(UploadIDs.transphylo_rds.CONFIRM_BUTTON, "n_clicks"),
    State(UploadIDs.transphylo_rds.UPLOAD_DATA, "contents"),
    State(UploadIDs.transphylo_rds.UPLOAD_DATA, "filename"),
    State(UploadIDs.transphylo_rds.DATASET_LABEL, "value"),
    State("graph-store", "data"),
    prevent_initial_call=True
)
def update_graph_with_transphylo_rds_data(n_clicks, contents, filename, label, current_graph_data):
    if not contents:
        raise PreventUpdate

    logger.debug("We are in the new transphylo_rds upload trigger")


    current_graph_data = current_graph_data or {"nodes": [], "edges": []}

    # todo WIP implementation

    effective_label = label or filename
    new_nodes, new_edges = build_graph_from_transphylo_rds(contents, effective_label)

    # existing_ids = {n["data"]["id"] for n in current_graph_data["nodes"]}
    # true_new_nodes = [
    #     n for n in new_nodes
    #     if n["data"]["id"] not in existing_ids
    # ]
    # merged_nodes = current_graph_data["nodes"] + true_new_nodes
    #
    # logger.info("Finished updating the graph with the .rds data.")

    # todo
    merged_nodes = []
    new_edges = []

    return (
        {
            "nodes": merged_nodes,
            "edges": current_graph_data["edges"] + new_edges
        }
    )
