import dash_bootstrap_components as dbc
from dash import dcc, html

from wiw_app.ids import UploadIDs

custom_csv_upload = html.Div(
    children=[
        html.Div(
            [
                dcc.Upload(
                    id=UploadIDs.custom_csv.UPLOAD_GRAPH_DATA,
                    children=html.Div(
                        ["Click to upload or drag a file here"]
                    ),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "marginBottom": "10px",
                    },
                    multiple=False,
                    accept=".csv",
                ),

                html.Div(
                    id=UploadIDs.custom_csv.SELECTED_GRAPH_FILENAME,
                    style={
                        "marginBottom": "10px",
                        "fontStyle": "italic",
                    },
                ),

                dbc.Input(
                    id=UploadIDs.custom_csv.DATASET_LABEL,
                    placeholder="Enter dataset label...",
                    type="text",
                    style={"marginBottom": "10px"},
                ),

                dbc.Button(
                    "Confirm Dataset",
                    id=UploadIDs.custom_csv.CONFIRM_BUTTON,
                    color="primary",
                ),

                dcc.Store(
                    id=UploadIDs.custom_csv.UPLOADED_GRAPH_STORE
                ),
            ],
            style={"paddingTop": "1.5rem"},
        )
    ],
)
