import dash_bootstrap_components as dbc
from dash import dcc, html

from wiw_app.ids import UploadIDs

upload_tabs = dbc.Tabs(
    children=
    [
        dbc.Tab(
            label="Trees",
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
                        html.Label("Burn-in:",
                                   htmlFor=UploadIDs.BURN_IN_SELECTION,
                                   style={"width": "200px",
                                          }),
                        dcc.Slider(
                            id=UploadIDs.BURN_IN_SELECTION,
                            min=0,
                            max=0.99,
                            step=0.01,
                            value=0.1,
                            marks={i: str(i) for i in [i / 10 for i in range(0, 11, 1)]},
                            tooltip={"placement": "bottom", "always_visible": True},
                        ),
                    ], style={"margin-bottom": "1rem"}),

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
            label="Node Annotations",
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
                    html.Div(
                        [
                            dbc.Input(
                                id=UploadIDs.NODE_ANNOTATIONS_LABEL,
                                placeholder="Enter node annotation label...",
                                type="text",
                                style={"marginBottom": "5px"},
                            ),
                            html.Div(
                                [
                                    html.Small(
                                        id="node-annotations-label-warning",
                                        style={"color": "red", "display": "block",
                                               "marginBottom": "2px"},
                                    ),
                                    html.Small(
                                        "Only letters, digits, and underscores are allowed. "
                                        "Other characters will be removed automatically!",
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
            ]
        )
    ],
    id="upload-tabs",
    active_tab="tab-upload-dataset",
)
