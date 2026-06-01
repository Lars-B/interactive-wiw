import dash_bootstrap_components as dbc
from dash import dcc, html

from wiw_app.ids import UploadIDs

metadata = html.Div([
    dcc.Upload(
        id=UploadIDs.UPLOAD_NODE_ANNOTATIONS,
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
        id=UploadIDs.SELECTED_NODE_ANNOTATIONS_FILENAME,
        style={"marginBottom": "10px",
               "fontStyle": "italic"}
    ),
    html.Div(
        [
            dbc.Input(
                id=UploadIDs.NODE_ANNOTATIONS_TAXON_COL,
                placeholder="Enter column name containing taxon names...",
                type="text",
                style={"marginBottom": "5px"},
            ),
            html.Div(
                [
                    html.Small(
                        id=UploadIDs.NODE_ANNOTATIONS_LABEL_WARNING,
                        style={"color": "red", "display": "block",
                               "marginBottom": "2px"},
                    ),
                    html.Small(
                        "Enter column name containing taxon names...",
                        style={"fontStyle": "italic", "color": "#666"},
                    ),
                ],
                style={"marginLeft": "2px"}  # slight indent from input
            ),
        ],
        style={"marginBottom": "15px"}
    ),
    dbc.Button(
        "Confirm File",
        id=UploadIDs.CONFIRM_NODE_ANNOTATIONS_BTN,
        color="primary"
    ),
],
    style={"paddingTop": "1.5rem"}
)
