import dash_bootstrap_components as dbc
from dash import dcc, html


def build_upload_panel(ids, accepted_files="*", include_burnin_slider=False):
    children = [
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
    ]

    if include_burnin_slider:
        children.append(
            html.Div([
                html.Label(
                    "Burn-in:",
                    htmlFor=ids.BURN_IN_SELECTION,
                    style={"width": "200px"},
                ),
                dcc.Slider(
                    id=ids.BURN_IN_SELECTION,
                    min=0,
                    max=0.99,
                    step=0.01,
                    value=0.1,
                    marks={i: str(i) for i in [i / 10 for i in range(11)]},
                    tooltip={
                        "placement": "bottom",
                        "always_visible": True,
                    },
                ),
            ], style={"marginBottom": "1rem"})
        )

    children.extend([
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
    ])

    return html.Div(
        children,
        style={"paddingTop": "1.5rem"},
    )
