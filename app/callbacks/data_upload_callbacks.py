from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from ..app import app as myapp
from ..dash_logger import logger
from ..graph_elements import build_graph_from_file, process_node_annotations_file
from ..ids import UploadIDs


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


@myapp.callback(
    Output(UploadIDs.UPLOADED_NODE_ANNOTATIONS_STORE, "data", allow_duplicate=True),
    Output("node-annotation-selector", "options"),
    Output("loading-modal", "is_open", allow_duplicate=True),
    Input(UploadIDs.CONFIRM_NODE_ANNOTATIONS_BTN, "n_clicks"),
    State(UploadIDs.UPLOAD_NODE_ANNOTATIONS, "contents"),
    State(UploadIDs.UPLOAD_NODE_ANNOTATIONS, "filename"),
    State(UploadIDs.UPLOADED_NODE_ANNOTATIONS_STORE, "data"),
    State("node-annotation-selector", "options"),
    prevent_initial_call=True
)
def update_node_annotations(n_clicks, contents, filename, current_node_annotations_data,
                            node_label_dropdown):
    if not contents or not n_clicks:
        raise PreventUpdate

    # todo could add label based on filename in the future for multiple annotations to switch?
    cur_label = "uploaded-annotations"

    # todo this should be checked in the input of the label option...
    import re
    new_label = re.sub(r'[^a-zA-Z0-9_]', '', cur_label)
    if new_label != cur_label:
        logger.info(f"There were symbols that are not allowed, removing them will change the "
                    f"label to: {new_label}")

    cur_label = new_label

    logger.info(f"Node annotations from file {filename} are being processed....")

    # todo currently we are simply overwriting existing node annotation maps!
    updated_data = process_node_annotations_file(
        contents, current_node_annotations_data
    )

    # logger.debug(f"Current node annotations: {node_label_dropdown}")

    new_dropdown_option = {"label": cur_label, "value": f"{cur_label}"}
    if new_dropdown_option not in node_label_dropdown:
        node_label_dropdown.append(new_dropdown_option)
    else:
        # todo could have a popup for that and then return here without updating anything?
        # todo if above we need to move this to the top of the thing to check that the label is
        #  unique
        logger.info("This label option already exists! not supported")

    # delay for loading modal to close... dash scheduling/ race condition problem.
    import time
    time.sleep(0.1)

    logger.info(f"Got updated data: {updated_data}")
    return (
        {"label": cur_label, "map": updated_data},
        node_label_dropdown,
        False
    )
