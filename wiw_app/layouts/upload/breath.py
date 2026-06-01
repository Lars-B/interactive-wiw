import dash_bootstrap_components as dbc
from dash import dcc, html

from wiw_app.ids import UploadIDs

breath = html.Div([
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
        accept=".tree, .trees, .tre",
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
