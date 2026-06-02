import time

from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from wiw_app.app import app as myapp
from wiw_app.dash_logger import logger
from wiw_app.graph_elements import build_graph_from_transphylo_rds
from wiw_app.ids import UploadIDs


@myapp.callback(
    Output("graph-store", "data", allow_duplicate=True),
    Output("loading-modal-tp", "is_open", allow_duplicate=True),
    Output(UploadIDs.INFO_TOAST, "children", allow_duplicate=True),
    Output(UploadIDs.INFO_TOAST, "is_open", allow_duplicate=True),
    Output(UploadIDs.INFO_TOAST, "duration", allow_duplicate=True),
    Output(UploadIDs.INFO_TOAST, "icon", allow_duplicate=True),
    Input(UploadIDs.transphylo_rds.CONFIRM_BUTTON, "n_clicks"),
    State(UploadIDs.transphylo_rds.UPLOAD_DATA, "contents"),
    State(UploadIDs.transphylo_rds.UPLOAD_DATA, "filename"),
    State(UploadIDs.transphylo_rds.DATASET_LABEL, "value"),
    State(UploadIDs.transphylo_rds.BURN_IN_SELECTION, "value"),
    Input(UploadIDs.transphylo_rds.INPUT_TYPE, "value"),
    State("graph-store", "data"),
    prevent_initial_call=True
)
def update_graph_with_transphylo_rds_data(
        n_clicks, contents, filename, label, burnin, input_type, current_graph_data):
    if not contents:
        raise PreventUpdate

    logger.debug("We are in the new transphylo_rds upload trigger")

    logger.info("Start with parsing the transphylo input...")

    current_graph_data = current_graph_data or {"nodes": [], "edges": []}

    effective_label = label or filename
    new_nodes, new_edges, num_samples = build_graph_from_transphylo_rds(
        contents,
        effective_label,
        burnin,
        input_type
    )
    if num_samples == 0:
        time.sleep(0.1)

        return (
            current_graph_data,
            False,
            # Info toast related stuff
            "No samples in input file. Reduce burnin?",
            True,
            7000,
            "danger"
        )

    existing_ids = {n["data"]["id"] for n in current_graph_data["nodes"]}
    true_new_nodes = [
        n for n in new_nodes
        if n["data"]["id"] not in existing_ids
    ]
    merged_nodes = current_graph_data["nodes"] + true_new_nodes

    logger.info("Finished updating the graph with the .rds data.")

    return (
        {"nodes": merged_nodes,
         "edges": current_graph_data["edges"] + new_edges},
        False,
        # Info toast related stuff
        f"Successfully parsed {num_samples} samples.",
        True,
        4000,
        "info"
    )
