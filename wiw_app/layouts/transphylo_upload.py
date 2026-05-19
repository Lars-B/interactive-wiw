import dash_bootstrap_components as dbc
from dash import dcc, html

from wiw_app.ids import UploadIDs

TODO = "ID.TODO"

transphylo_upload = html.Div(
    children=[
        html.Div(
            [
                dcc.Upload(
                    id=TODO,
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
                ),

                html.Div(
                    id=TODO,
                    style={
                        "marginBottom": "10px",
                        "fontStyle": "italic",
                    },
                ),

                dbc.Input(
                    id=TODO,
                    placeholder="Enter dataset label...",
                    type="text",
                    style={"marginBottom": "10px"},
                ),

                dbc.Button(
                    "Confirm Dataset",
                    id=TODO,
                    color="primary",
                ),

                dcc.Store(
                    id=TODO
                ),
            ],
            style={"paddingTop": "1.5rem"},
        )
    ],
)
