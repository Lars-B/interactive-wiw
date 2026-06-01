import dash_bootstrap_components as dbc
from dash import dcc, html


def build_simple_upload_panel(ids, accepted_files="*"):
    return html.Div([
        dcc.Upload(
            id=ids.UPLOAD_DATA,
            children=html.Div(["Click to upload or drag a file here"]),
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
            accept=accepted_files,
        ),

        html.Div(
            id=ids.SELECTED_FILENAME,
            style={"marginBottom": "10px", "fontStyle": "italic"},
        ),

        dbc.Input(
            id=ids.DATASET_LABEL,
            placeholder="Enter dataset label...",
            type="text",
            style={"marginBottom": "10px"},
        ),

        dbc.Button(
            "Confirm Dataset",
            id=ids.CONFIRM_BUTTON,
            color="primary",
        ),

        # dcc.Store(id=ids.UPLOADED_GRAPH_STORE),
    ], style={"paddingTop": "1.5rem"})
