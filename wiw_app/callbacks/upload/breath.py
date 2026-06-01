import time

from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from wiw_app.app import app as myapp
from wiw_app.dash_logger import logger
from wiw_app.graph_elements import build_graph_from_breath_tree_file, NoTreesFoundError
from wiw_app.ids import UploadIDs


@myapp.callback(
    Output("graph-store", "data", allow_duplicate=True),
    Output("loading-modal", "is_open", allow_duplicate=True),
    Output(UploadIDs.INFO_TOAST, "children"),
    Output(UploadIDs.INFO_TOAST, "is_open"),
    Output(UploadIDs.INFO_TOAST, "duration"),
    Output(UploadIDs.INFO_TOAST, "icon"),
    Input(UploadIDs.breath_trees.CONFIRM_TREES_DATASET_BTN, "n_clicks"),
    State(UploadIDs.breath_trees.UPLOAD_DATA, "contents"),
    State(UploadIDs.breath_trees.UPLOAD_DATA, "filename"),
    State(UploadIDs.breath_trees.DATASET_LABEL, "value"),
    State(UploadIDs.breath_trees.BURN_IN_SELECTION, "value"),
    State("graph-store", "data"),
    prevent_initial_call=True
)
def update_graph_with_breath_trees(n_clicks, contents, filename, label, burnin, current_graph_data):
    if not contents:
        raise PreventUpdate

    effective_label = label or filename
    # Merge with current graph (if any)
    current_graph_data = current_graph_data or {"nodes": [], "edges": []}

    try:
        new_nodes, new_edges, num_trees = build_graph_from_breath_tree_file(contents,
                                                                            effective_label, burnin)
    except NoTreesFoundError as e:
        # delay for loading modal to close... dash scheduling/ race condition problem.
        time.sleep(0.1)

        return (
            current_graph_data,
            False,
            # Info toast related stuff
            str(e),
            True,
            5000,
            "danger"
        )

    # Extracting only new nodes, if there was additional node annotation data uploaded
    # this will still raise an Error because new nodes will miss the color by this new label
    existing_ids = {n["data"]["id"] for n in current_graph_data["nodes"]}
    true_new_nodes = [
        n for n in new_nodes
        if n["data"]["id"] not in existing_ids
    ]
    merged_nodes = current_graph_data["nodes"] + true_new_nodes

    logger.info("Finished updating the graph.")

    return (
        {"nodes": merged_nodes,
         "edges": current_graph_data["edges"] + new_edges},
        False,
        # Info toast related stuff
        f"Successfully parsed {num_trees} trees.",
        True,
        3000,
        "info"
    )
