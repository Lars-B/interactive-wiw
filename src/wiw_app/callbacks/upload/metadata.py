import time

from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate

from wiw_app.app import app as myapp
from wiw_app.dash_logger import logger
from wiw_app.graph_elements import process_node_annotations_file, AnnotationFileError
from wiw_app.ids import UploadIDs


@myapp.callback(
    Output(UploadIDs.metadata.SELECTED_FILENAME, "children"),
    Input(UploadIDs.metadata.UPLOAD_DATA, "filename"),
)
def display_metadata_file_name(filename):
    if filename:
        return f"Selected file: {filename}"
    return "No file selected yet. (.csv|.tsv|.xsv)"


@myapp.callback(
    Output("graph-store", "data", allow_duplicate=True),
    Output(UploadIDs.INFO_TOAST, "children", allow_duplicate=True),
    Output(UploadIDs.INFO_TOAST, "is_open", allow_duplicate=True),
    Output(UploadIDs.INFO_TOAST, "duration", allow_duplicate=True),
    Output(UploadIDs.INFO_TOAST, "icon", allow_duplicate=True),
    # Input below...
    Input(UploadIDs.metadata.CONFIRM_NODE_ANNOTATIONS_BTN, "n_clicks"),
    State("graph-store", "data"),
    State(UploadIDs.metadata.UPLOAD_DATA, "contents"),
    State(UploadIDs.metadata.UPLOAD_COLUMN_NAME, "value"),
    State(UploadIDs.metadata.GRAPH_NODE_INFO_NAME, "value"),
    prevent_initial_call=True
)
def update_nodes_with_metadata(
        n_clicks,
        graph_data,
        contents,
        upload_column_name,
        existing_node_name,
):
    if not contents or not n_clicks:
        raise PreventUpdate

    if not graph_data:
        logger.info("No graph data loaded, nothing happens.")
        time.sleep(0.1)
        return (
            no_update,
            # Info toast related stuff
            f"No metadata was uploaded or found in the file!",
            True,
            7000,
            "danger"
        )

    logger.info(
        f"User selection: **{upload_column_name}** for upload column "
        f"and **{existing_node_name}** for existing graph-node info."
    )

    try:
        uploaded_map = process_node_annotations_file(contents, upload_column_name)
    except AnnotationFileError as e:
        return (
            no_update,
            str(e),
            True,
            7000,
            "danger"
        )

    # merge uploaded data into existing graph
    nodes = graph_data.get("nodes", [])

    logger.debug(f"We picked this taxon: {upload_column_name}")
    for n in nodes:
        for new_label, value in uploaded_map.get(n['data'][existing_node_name],
                                                 {}).items():
            if not new_label in n['data']:
                # Adding the new annotation to the node
                n['data'][new_label] = value
            else:
                raise ValueError(f"Label name {new_label} already exists,"
                                 f" needs to be renamed in the uploaded file!")

    updated_graph_data = {
        "nodes": nodes,
        "edges": graph_data.get("edges", [])
    }

    # todo this seems to happen even if it should not work?
    return (
        updated_graph_data,  # Info toast related stuff
        f"Successfully uploaded metadata.",
        True,
        5000,
        "info"
    )
