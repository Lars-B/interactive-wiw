import dash_bootstrap_components as dbc
from dash import dcc, html

from ..ids import UploadIDs

upload_tabs = dbc.Tabs(
    children=
    [
        dbc.Tab(
            label="Upload Dataset",
            tab_id="tab-upload-dataset",
            children=[
                html.Div([
                    dcc.Upload(
                        id=UploadIDs.UPLOAD_TREES_DATA,
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
                    ),
                    html.Div(id=UploadIDs.SELECTED_TREES_FILENAME,
                             style={"marginBottom": "10px",
                                    "fontStyle": "italic"}),

                    html.Div([
                        html.Label("Burn-in choose [0.0, 1.0):",
                                   htmlFor=UploadIDs.BURN_IN_SELECTION,
                                   style={"width": "200px",
                                          "display": "inline-block"}),
                        dcc.Input(
                            id=UploadIDs.BURN_IN_SELECTION,
                            type="number",
                            min=0,
                            max=0.99,
                            step=0.01,
                            value=0.1,
                            debounce=True,
                            style={"width": "200px"},
                        ),
                    ], style={"margin-bottom": "10px"}),

                    dbc.Input(id=UploadIDs.TREES_DATASET_LABEL,
                              placeholder="Enter dataset label...",
                              type="text",
                              style={"marginBottom": "10px"}),
                    dbc.Button("Confirm Dataset",
                               id=UploadIDs.CONFIRM_TREES_DATASET_BTN,
                               color="primary"),
                    dcc.Store(id=UploadIDs.UPLOADED_TREES_DATA_STORE),
                ],
                    style={"paddingTop": "1.5rem"}
                )
            ],
        ),
        dbc.Tab(
            label="Upload Node Annotations",
            tab_id="tab-node-annotations",
            children=[
                html.Div([
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
                    ),
                    html.Div(
                        id=UploadIDs.SELECTED_NODE_ANNOTATIONS_FILENAME,
                        style={"marginBottom": "10px",
                               "fontStyle": "italic"}
                    ),
                    dbc.Button(
                        "Confirm File",
                        id=UploadIDs.CONFIRM_NODE_ANNOTATIONS_BTN,
                        color="primary"
                    ),
                    dcc.Store(id=UploadIDs.UPLOADED_NODE_ANNOTATIONS_STORE),
                ],
                    style={"paddingTop": "1.5rem"}
                )
            ]
        )
    ],
    id="upload-tabs",
    active_tab="tab-upload-dataset",
)
