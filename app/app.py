import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import html, dcc
from dash_bootstrap_templates import ThemeSwitchAIO

dcc.Store(id="graph-store")
template_theme1 = "morph"
template_theme2 = "slate"
url_theme1 = dbc.themes.MORPH
url_theme2 = dbc.themes.SLATE

dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css"
)

app = dash.Dash(__name__,
                external_stylesheets=[url_theme1, dbc_css],
                assets_folder="../assets",
                )
app.layout = html.Div([
    dcc.Store(id="graph-store"),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Processing Dataset")),
            dbc.ModalBody([
                html.P("Please wait while we process your file..."),
                dbc.Spinner(size="md", color="primary", type="border"),
            ]),
        ],
        id="loading-modal",
        is_open=False,
        backdrop="static",  # prevents closing by clicking outside
        keyboard=False,  # disables Esc key
        centered=True,
    ),
    dbc.Row([
        # Sidebar
        dbc.Col(
            [
                ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2],
                               switch_props={"value": False}),
                html.Hr(),
                html.Button("Reset Graph", id="reset-graph-btn", n_clicks=0),
                dbc.Card([
                    dbc.CardHeader("Upload Dataset"),
                    dbc.CardBody([
                        dcc.Upload(
                            id="upload-data",
                            children=html.Div(["Click to upload or drag a file here"]),
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
                        html.Div(id="selected-filename", style={"marginBottom": "10px",
                                                                "fontStyle": "italic"}),
                        dbc.Input(id="dataset-label", placeholder="Enter dataset label...",
                                  type="text",
                                  style={"marginBottom": "10px"}),
                        dbc.Button("Confirm Dataset", id="confirm-dataset-btn", color="primary"),
                        dcc.Store(id="uploaded-datasets-store"),
                    ])
                ]),

                html.H5("Graph Controls", className="mt-2"),

                dcc.Dropdown(
                    id="label-filter",
                    options=[{"label": "set1", "value": "set1"},
                             {"label": "set2", "value": "set2"}],
                    value=["set1", "set2"],
                    multi=True,
                    style={"marginBottom": "10px"}
                ),
                dcc.Dropdown(
                    id="layout-selector",
                    options=[
                        {"label": "Cose (Spring)", "value": "cose"},
                        {"label": "Dot (Hierarchical)", "value": "breadthfirst"},
                        {"label": "Grid", "value": "grid"},
                        {"label": "Circle", "value": "circle"},
                    ],
                    value="cose",
                    clearable=False,
                    style={"marginBottom": "10px"}
                ),
                dcc.Checklist(
                    id="scale-width-toggle",
                    options=[{"label": "Scale edge width by weight", "value": "scale"}],
                    value=["scale"],
                    inline=True,
                    style={"marginBottom": "10px"}
                ),
                dcc.Dropdown(
                    id="edge-annotation-selector",
                    options=[
                        {"label": "None", "value": "none"},
                        {"label": "Label", "value": "label"},
                        {"label": "Weight", "value": "weight"},
                    ],
                    value="label",
                    clearable=False,
                    style={"marginBottom": "10px"}
                ),
                dcc.Dropdown(
                    id="edge-label-position",
                    options=[
                        {"label": "Centered", "value": "center"},
                        {"label": "Above Edge", "value": "above"},
                        {"label": "Below Edge", "value": "below"},
                        {"label": "Follow Edge", "value": "autorotate"},
                    ],
                    value="center",
                    clearable=False,
                    style={"marginBottom": "10px"}
                ),
                html.Button("Recenter Graph", id="recenter-btn",
                            style={"marginBottom": "10px"}),
                dcc.Input(
                    id="weight-threshold",
                    type="number",
                    min=0,
                    max=1,
                    step=0.01,
                    value=0.0,  # Default threshold
                    debounce=True,  # Only trigger callback when user stops typing
                    style={"width": "200px", "margin-bottom": "10px"},
                    placeholder="Edge weight threshold"
                ),
                dcc.Checklist(
                    id="color-by-label-toggle",
                    options=[{"label": "Color edges by label", "value": "color"}],
                    value=[],
                    inline=True,
                    style={"margin-bottom": "10px"}
                ),
                dcc.Store(id="label-color-store"),
                dbc.Collapse(
                    html.Div(
                        [
                            html.Div(id="rename-error",
                                     style={"color": "red", "marginBottom": "10px"}),
                            html.Div(id="color-pickers-container", style={"marginTop": "10px"})
                        ]
                    ),
                    id="color-pickers-collapse",
                    is_open=False
                ),
                html.Div([
                    html.H5("Log Information:"),
                    html.Pre(id="log-output", style={
                        "maxHeight": "250px",
                        "overflowY": "auto",
                        "whiteSpace": "pre-wrap",
                        "backgroundColor": "#111",
                        "color": "#0f0",
                        "padding": "10px",
                        "borderRadius": "8px"
                    })
                ])
            ],
            width=2,  # out of 12 total columns
            style={
                "padding": "15px",
                "height": "100vh",
                "overflowY": "auto"
            }
        ),
        # Graph Area
        dbc.Col(
            cyto.Cytoscape(
                id='cytoscape',
                elements=[],
                layout={'name': 'cose'},
                style={'width': '100%', 'height': '100vh',
                       'backgroundColor': '#1e1e1e'},
                zoom=1,
                pan={'x': 0, 'y': 0}
            )
            # ])
            ,
            width=10,
            style={"padding": "0"}  # Remove padding for full-width visualization
        )
    ], style={"margin": "0", "width": "100%", "height": "100vh", "overflow": "hidden"})
])
