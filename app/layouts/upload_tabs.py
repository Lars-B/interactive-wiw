import dash_bootstrap_components as dbc
from dash import dcc, html

upload_tabs = dbc.Tabs(
    children=
    [
        dbc.Tab(
            label="Upload Dataset",
            tab_id="tab-upload-dataset",
            children=[
                html.Div([
                    dcc.Upload(
                        id="upload-trees-data",
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
                    html.Div(id="selected-trees-filename",
                             style={"marginBottom": "10px",
                                    "fontStyle": "italic"}),

                    html.Div([
                        html.Label("Burn-in choose [0.0, 1.0):",
                                   htmlFor="burn-in-selection",
                                   style={"width": "200px",
                                          "display": "inline-block"}),
                        dcc.Input(
                            id="burn-in-selection",
                            type="number",
                            min=0,
                            max=0.99,
                            step=0.01,
                            value=0.1,
                            debounce=True,
                            style={"width": "200px"},
                        ),
                    ], style={"margin-bottom": "10px"}),

                    dbc.Input(id="trees-dataset-label",
                              placeholder="Enter dataset label...",
                              type="text",
                              style={"marginBottom": "10px"}),
                    dbc.Button("Confirm Dataset", id="confirm-dataset-btn",
                               color="primary"),
                    dcc.Store(id="uploaded-datasets-store"),
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
                        id="upload-node-annotations",
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
                        id="selected-node-annotations-file",
                        style={"marginBottom": "10px",
                               "fontStyle": "italic"}
                    ),
                    dbc.Button(
                        "Confirm File",
                        id="confirm-node-annotation-btn",
                        color="primary"
                    ),
                    dcc.Store(id="uploaded-node-annotations-store"),
                ],
                    style={"paddingTop": "1.5rem"}
                )
            ]
        )
    ],
    id="upload-tabs",
    active_tab="tab-upload-dataset",
)
