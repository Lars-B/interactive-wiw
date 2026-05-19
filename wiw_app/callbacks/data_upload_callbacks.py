import time

from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate

from wiw_app.app import app as myapp
from wiw_app.dash_logger import logger
from wiw_app.graph_elements import build_graph_from_breath_tree_file, process_node_annotations_file, \
    NoTreesFoundError, build_graph_from_outbreaker_csv_file
from wiw_app.ids import UploadIDs, GraphOptions


@myapp.callback(
    Output("graph-store", "data", allow_duplicate=True),
    Output("loading-modal", "is_open", allow_duplicate=True),
    Output(UploadIDs.INFO_TOAST, "children"),
    Output(UploadIDs.INFO_TOAST, "is_open"),
    Output(UploadIDs.INFO_TOAST, "duration"),
    Output(UploadIDs.INFO_TOAST, "icon"),
    Input(UploadIDs.CONFIRM_TREES_DATASET_BTN, "n_clicks"),
    State(UploadIDs.UPLOAD_TREES_DATA, "contents"),
    State(UploadIDs.UPLOAD_TREES_DATA, "filename"),
    State(UploadIDs.TREES_DATASET_LABEL, "value"),
    State(UploadIDs.BURN_IN_SELECTION, "value"),
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


@myapp.callback(
    Output(UploadIDs.UPLOADED_TREES_DATA_STORE, "data", allow_duplicate=True),
    Input(UploadIDs.CONFIRM_TREES_DATASET_BTN, "n_clicks"),
    State(UploadIDs.UPLOAD_TREES_DATA, "contents"),
    State(UploadIDs.UPLOAD_TREES_DATA, "filename"),
    State(UploadIDs.TREES_DATASET_LABEL, "value"),
    State(UploadIDs.UPLOADED_TREES_DATA_STORE, "data"),
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
    Output(UploadIDs.SELECTED_TREES_FILENAME, "children"),
    Output(UploadIDs.TREES_DATASET_LABEL, "value"),
    Input(UploadIDs.UPLOAD_TREES_DATA, "filename"),
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
    Output("graph-store", "data", allow_duplicate=True),
    Output(GraphOptions.Nodes.LABEL_ANNOTATION_SELECTOR, "options"),
    Output(GraphOptions.Nodes.COLOR_LABEL_SELECTOR, "options"),
    Input(UploadIDs.CONFIRM_NODE_ANNOTATIONS_BTN, "n_clicks"),
    State("graph-store", "data"),
    State(UploadIDs.UPLOAD_NODE_ANNOTATIONS, "contents"),
    State(UploadIDs.NODE_ANNOTATIONS_TAXON_COL, "value"),
    State(GraphOptions.Nodes.LABEL_ANNOTATION_SELECTOR, "options"),
    State(GraphOptions.Nodes.COLOR_LABEL_SELECTOR, "options"),
    prevent_initial_call=True
)
def update_node_annotations(n_clicks, graph_data,
                            contents, taxon_column,
                            node_label_annotation_selector,
                            node_color_label_selector):
    if not contents or not n_clicks:
        raise PreventUpdate

    if not graph_data:
        logger.info("No graph data loaded, nothing happens.")
        time.sleep(0.1)
        return no_update, no_update, no_update, False

    uploaded_map = process_node_annotations_file(contents, taxon_column)

    # merge uploaded data into existing graph
    nodes = graph_data.get("nodes", [])

    # Todo make "taxon" an input and then raise warning if two input columns don't match
    #  This will allow more general inputs
    #  can we somehow use index to simply upload a list of things without a column? check...

    for n in nodes:
        for new_label, value in uploaded_map.get(n['data']['taxon'], {}).items():
            if not new_label in n['data']:
                # Adding the new annotation to the node
                n['data'][new_label] = value

                # adding the new label to the dropdown menu
                new_dropdown_option = {"label": new_label,
                                       "value": f"{new_label}"}
                if not (new_dropdown_option in node_label_annotation_selector or
                        new_dropdown_option in node_color_label_selector):
                    node_label_annotation_selector.append(new_dropdown_option)
                    node_color_label_selector.append(new_dropdown_option)

            else:
                raise ValueError(f"Label name {new_label} already exists,"
                                 f" needs to be renamed in the uploaded file!")

    updated_graph_data = {
        "nodes": nodes,
        "edges": graph_data["edges"]
    }

    return (
        updated_graph_data,
        node_label_annotation_selector,
        node_color_label_selector,
    )


# Outbreaker part below


@myapp.callback(
    Output(UploadIDs.Outbreaker.SELECTED_GRAPH_FILENAME, "children"),
    Output(UploadIDs.Outbreaker.DATASET_LABEL, "value"),
    Input(UploadIDs.Outbreaker.UPLOAD_GRAPH_DATA, "filename")
)
def display_outbreaker_file_name(filename):
    if filename:
        return f"Selected file: {filename}", filename
    return "No file selected yet.", ""


@myapp.callback(
    Output("graph-store", "data", allow_duplicate=True),
    Input(UploadIDs.Outbreaker.CONFIRM_BUTTON, "n_clicks"),
    State(UploadIDs.Outbreaker.UPLOAD_GRAPH_DATA, "contents"),
    State(UploadIDs.Outbreaker.UPLOAD_GRAPH_DATA, "filename"),
    State(UploadIDs.Outbreaker.DATASET_LABEL, "value"),
    State("graph-store", "data"),
    prevent_initial_call=True
)
def update_graph_with_dataset(n_clicks, contents, filename, label, current_graph_data):
    if not contents:
        raise PreventUpdate

    logger.debug("We are in the outbreaker upload trigger")

    current_graph_data = current_graph_data or {"nodes": [], "edges": []}

    effective_label = label or filename
    new_nodes, new_edges = build_graph_from_outbreaker_csv_file(contents, effective_label)

    # todo this is simply copied from the other upload, should probably be refactored/refined
    existing_ids = {n["data"]["id"] for n in current_graph_data["nodes"]}
    true_new_nodes = [
        n for n in new_nodes
        if n["data"]["id"] not in existing_ids
    ]
    merged_nodes = current_graph_data["nodes"] + true_new_nodes

    logger.info("Finished updating the graph.")

    return (
        {
            "nodes": merged_nodes,
            "edges": current_graph_data["edges"] + new_edges
        }
    )
