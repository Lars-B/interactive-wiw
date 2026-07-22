from dash import Input, Output, State

from dash.dependencies import ALL
from dash.exceptions import PreventUpdate

from wiw_app.app import app as myapp
from wiw_app.dash_logger import logger
from wiw_app.ids import UploadIDs, GraphOptions
from wiw_app.utils import humanize_label


@myapp.callback(
    Output(GraphOptions.Edges.ADVANCED_OPTIONS_COLLAPSE, "is_open"),
    Output(GraphOptions.Edges.ADVANCED_OPTIONS_ICON, "icon"),
    Input(GraphOptions.Edges.ADVANCED_OPTION_TOGGLE_BTN, "n_clicks"),
    State(GraphOptions.Edges.ADVANCED_OPTIONS_COLLAPSE, "is_open"),
    prevent_initial_call=True
)
def toggle_advanced_edge_options(n_clicks, is_open):
    if n_clicks is None:
        raise PreventUpdate
    new_is_open = not is_open
    new_icon = "mdi:cheese" if new_is_open else "mdi:cheese-off"
    return new_is_open, new_icon


@myapp.callback(
    Output(GraphOptions.Nodes.ADVANCED_OPTIONS_COLLAPSE, "is_open"),
    Output(GraphOptions.Nodes.ADVANCED_OPTIONS_ICON, "icon"),
    Input(GraphOptions.Nodes.ADVANCED_OPTION_TOGGLE_BTN, "n_clicks"),
    State(GraphOptions.Nodes.ADVANCED_OPTIONS_COLLAPSE, "is_open"),
    prevent_initial_call=True
)
def toggle_advanced_node_options(n_clicks, is_open):
    if n_clicks is None:
        raise PreventUpdate
    new_is_open = not is_open
    new_icon = "mdi:cheese" if new_is_open else "mdi:cheese-off"
    return new_is_open, new_icon


@myapp.callback(
    Output(GraphOptions.Nodes.COLOR_PICKERS_COLLAPSE, "is_open"),
    Input(GraphOptions.Nodes.COLOR_BY_LABEL, "value"),
)
def toggle_node_color_pickers(toggle_values):
    # Show if 'color' is in checklist values, else hide
    return "color" in toggle_values


@myapp.callback(
    Output(GraphOptions.Nodes.CATEGORICAL_COLOR_OPTIONS, "is_open"),
    Output(GraphOptions.Nodes.HEATMAP_OPTIONS_COLLAPSE, "is_open"),
    Input(GraphOptions.Nodes.COLOR_MODE, "value"),
)
def toggle_node_color_mode(mode):
    return (
        mode == "categorical",
        mode == "continuous",
    )


@myapp.callback(
    Output(GraphOptions.Edges.COLOR_PICKERS_COLLAPSE, "is_open"),
    Input(GraphOptions.Edges.COLOR_BY_LABEL, "value"),
)
def toggle_edge_color_pickers(toggle_values):
    # Show if 'color' is in checklist values, else hide
    return "color" in toggle_values


@myapp.callback(
    Output(GraphOptions.Edges.COLOR_STORE, "data"),
    Input({"type": "color-input", "index": ALL}, "value"),
    State({"type": "color-input", "index": ALL}, "id")
)
def update_edge_label_color_store(values, ids):
    return {id["index"]: val for id, val in zip(ids, values)}


@myapp.callback(
    Output(UploadIDs.metadata.UPLOAD_COLUMN_NAME, "value",
           allow_duplicate=True),
    Output(UploadIDs.metadata.NODE_ANNOTATIONS_LABEL_WARNING, "children"),
    Output(UploadIDs.metadata.CONFIRM_NODE_ANNOTATIONS_BTN, "disabled"),
    Output(UploadIDs.metadata.UPLOAD_DATA, "disabled"),
    Output(UploadIDs.metadata.UPLOAD_COLUMN_NAME, "disabled"),
    Output(UploadIDs.metadata.GRAPH_NODE_INFO_NAME, "disabled"),
    Input(UploadIDs.metadata.UPLOAD_COLUMN_NAME, "value"),
    Input("graph-store", "data"),
    prevent_initial_call="initial_duplicate",
    allow_duplicate=True,
)
def sanitize_node_annotations_label(label, graph_data):
    # ----------------------------
    # 1. No graph loaded yet, lock this input
    # ----------------------------
    if not graph_data or not graph_data.get("nodes"):
        return (
            "",
            "Please upload a graph before using this feature!",
            True,
            True,
            True,
            True,
        )

    # ----------------------------
    # 2. Default column name, enabling buttons
    # ----------------------------
    default_column_label = "taxon"

    if not label:
        logger.info("No label provided, setting default value")

        return (
            default_column_label,
            f"No label provided - defaulting to '{default_column_label}'",
            False,
            False,
            False,
            False,
        )

    # ----------------------------
    # 3. Enabling all the buttons
    # ----------------------------
    return (
        label,
        "",
        False,
        False,
        False,
        False,
    )


@myapp.callback(
    Output(GraphOptions.Edges.SCALE_VALUE_INPUT, "disabled"),
    Input(GraphOptions.Edges.SCALE_WIDTH_BY_WEIGHT, "value"),
)
def toggle_edge_scale_input(value):
    return "scale" not in (value or [])


@myapp.callback(
    Output(UploadIDs.transphylo_rds.BURN_IN_CONTAINER, "style"),
    Input(UploadIDs.transphylo_rds.INPUT_TYPE, "value"),
)
def toggle_burnin_visibility(input_type):
    if input_type == "wiw_matrix":
        return {"display": "none"}

    return {"marginBottom": "1rem"}


@myapp.callback(
    Output(UploadIDs.metadata.GRAPH_NODE_INFO_NAME, "options"),
    Input("graph-store", "data")
)
def update_dropdown_metadata_upload(graph_data):
    if not graph_data or not graph_data.get("nodes"):
        return []

    fields = set()
    for n in graph_data.get("nodes"):
        fields.update(n.get("data", {}).keys())

    return [{"label": f, "value": f} for f in sorted(fields)]


@myapp.callback(
    Output(GraphOptions.Nodes.LABEL_ANNOTATION_SELECTOR, "options"),
    Output(GraphOptions.Nodes.LABEL_ANNOTATION_SELECTOR, "value"),
    Output(GraphOptions.Nodes.COLOR_LABEL_SELECTOR, "options"),
    Input("graph-store", "data"),
    State(GraphOptions.Nodes.LABEL_ANNOTATION_SELECTOR, "value"),
)
def update_node_label_annotation_dropdown(graph_data, current_selection):
    options = [{"label": "None", "value": "none"}]
    col_options = [{"label": "Id", "value": "id"}]

    if not graph_data or not graph_data.get("nodes"):
        return options, "none", col_options

    # collect unique annotation keys
    keys = {
        key
        for n in graph_data["nodes"]
        for key in n.get("data", {})
    }

    # build dropdown options
    options.extend(
        {"label": humanize_label(key), "value": key}
        for key in sorted(keys)
    )

    col_options.extend(
        {"label": humanize_label(key), "value": key}
        for key in sorted(keys)
        if key != "id"  # avoid duplicate ID option
    )

    preferred_order = ("taxon", "id")

    if current_selection and current_selection != "none":
        new_selection = current_selection
    else:
        new_selection = next(
            (p for p in preferred_order if p in keys or p == "id"),
            "none"
        )

    return options, new_selection, col_options
