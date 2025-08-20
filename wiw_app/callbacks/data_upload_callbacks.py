import time

from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate

from wiw_app.app import app as myapp
from wiw_app.dash_logger import logger
from wiw_app.graph_elements import build_graph_from_file, process_node_annotations_file, \
    NoTreesFoundError
from wiw_app.ids import UploadIDs, GraphOptions


@myapp.callback(
    Output("graph-store", "data", allow_duplicate=True),
    Output("loading-modal", "is_open", allow_duplicate=True),
    Output(UploadIDs.INFO_TOAST, "children"),
    Output(UploadIDs.INFO_TOAST, "is_open"),
    Output(UploadIDs.INFO_TOAST, "duration"),
    Output(UploadIDs.INFO_TOAST, "icon"),
    Input("confirm-dataset-btn", "n_clicks"),
    State("upload-trees-data", "contents"),
    State("upload-trees-data", "filename"),
    State(UploadIDs.TREES_DATASET_LABEL, "value"),
    State("burn-in-selection", "value"),
    State("graph-store", "data"),
    prevent_initial_call=True
)
def update_graph_with_dataset(n_clicks, contents, filename, label, burnin, current_graph_data):
    if not contents:
        raise PreventUpdate

    effective_label = label or filename
    # Merge with current graph (if any)
    current_graph_data = current_graph_data or {"nodes": [], "edges": []}

    try:
        new_nodes, new_edges, num_trees = build_graph_from_file(contents, effective_label, burnin)
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

    logger.info("Finished updating the graph.")

    return (
        {"nodes": current_graph_data["nodes"] + new_nodes,
         "edges": current_graph_data["edges"] + new_edges},
        False,
        # Info toast related stuff
        f"Successfully parsed {num_trees} trees.",
        True,
        3000,
        "info"
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
    Output(UploadIDs.TREES_DATASET_LABEL, "value"),
    Input("upload-trees-data", "filename"),
)
def display_tree_file_name(filename):
    if filename:
        return f"Selected file: {filename}", filename
    return "No file selected yet.", ""


@myapp.callback(
    Output("selected-node-annotations-file", "children"),
    Output(UploadIDs.NODE_ANNOTATIONS_LABEL, "value"),
    Input("upload-node-annotations", "filename"),
)
def display_node_annotation_file_name(filename):
    if filename:
        return f"Selected file: {filename}", filename.split(".")[0]
    return "No file selected yet.", ""


@myapp.callback(
    Output("graph-store", "data", allow_duplicate=True),
    Output(GraphOptions.Nodes.LABEL_ANNOTATION_SELECTOR, "options"),
    Output(GraphOptions.Nodes.COLOR_LABEL_SELECTOR, "options"),
    Output("loading-modal", "is_open", allow_duplicate=True),
    Input(UploadIDs.CONFIRM_NODE_ANNOTATIONS_BTN, "n_clicks"),
    Input("graph-store", "data"),
    State(UploadIDs.UPLOAD_NODE_ANNOTATIONS, "contents"),
    State(UploadIDs.UPLOAD_NODE_ANNOTATIONS, "filename"),
    State(UploadIDs.NODE_ANNOTATIONS_LABEL, "value"),
    State(GraphOptions.Nodes.LABEL_ANNOTATION_SELECTOR, "options"),
    State(GraphOptions.Nodes.COLOR_LABEL_SELECTOR, "options"),
    prevent_initial_call=True
)
def update_node_annotations(n_clicks, graph_data, contents, filename, annotation_label,
                            node_label_annotation_selector,
                            node_color_label_selector):
    if not contents or not n_clicks:
        raise PreventUpdate

    if not graph_data:
        logger.info("No graph data loaded, nothing happens.")
        time.sleep(0.1)
        return no_update, no_update, no_update, False

    logger.info(f"Node annotations from file {filename} are being processed....")

    uploaded_map = process_node_annotations_file(contents)

    # merge uploaded data into existing graph
    nodes = graph_data.get("nodes", [])
    for n in nodes:
        n["data"][annotation_label] = uploaded_map.get(n["data"]["taxon"], "")

    updated_graph_data = {
        "nodes": nodes,
        "edges": graph_data["edges"]
    }

    new_dropdown_option = {"label": annotation_label, "value": f"{annotation_label}"}
    if (new_dropdown_option in node_label_annotation_selector or
            new_dropdown_option in node_color_label_selector):
        logger.info(f"This label ({annotation_label}) option already exists!"
                    f"Not supported at the moment!")
    else:
        node_label_annotation_selector.append(new_dropdown_option)
        node_color_label_selector.append(new_dropdown_option)

    # delay for loading modal to close... dash scheduling/ race condition problem.
    time.sleep(0.1)
    logger.info(f"Graph-store updated wit hnew annotation label: {annotation_label}")

    return (
        updated_graph_data,
        node_label_annotation_selector,
        node_color_label_selector,
        False
    )
