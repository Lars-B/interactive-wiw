import dash_bootstrap_components as dbc
from dash import dcc, html

from wiw_app.ids import UploadIDs

metadata = html.Div([
    dcc.Upload(
        id=UploadIDs.metadata.UPLOAD_DATA,
        children=html.Div(
            ["Click to upload or drag a file here"]),
        style={
            "width": "100%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
            "margin-bottom": "10px"
        },
        multiple=False,
        accept=".csv, .tsv, .xsv",
    ),
    html.Div(
        id=UploadIDs.metadata.SELECTED_FILENAME,
        style={"marginBottom": "10px",
               "fontStyle": "italic"}
    ),

    html.Div(
        [
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Upload"),
                    dbc.Input(
                        id=UploadIDs.metadata.UPLOAD_COLUMN_NAME,
                        placeholder="Enter column name containing taxon names...",
                        type="text",
                    ),
                ],
                className="mb-1",
            ),

            html.Small(
                id=UploadIDs.metadata.NODE_ANNOTATIONS_LABEL_WARNING,
                style={"color": "red", "display": "block", "marginBottom": "2px"},
            ),

            html.Small(
                "Enter column name containing taxon names...",
                style={"fontStyle": "italic", "color": "#666"},
            ),

            dbc.InputGroup(
                [
                    dbc.InputGroupText("Graph"),
                    dbc.Select(
                        id=UploadIDs.metadata.GRAPH_NODE_INFO_NAME,
                        options=[],
                        placeholder="Select node annotation field",
                    ),
                ],
                className="mb-1",
            )
        ],
        style={"marginBottom": "15px"},
    ),

    dbc.Button(
        "Confirm File",
        id=UploadIDs.metadata.CONFIRM_NODE_ANNOTATIONS_BTN,
        color="primary"
    ),
],
    style={"paddingTop": "1.5rem"}
)
