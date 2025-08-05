import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import html, dcc
from dash_bootstrap_templates import ThemeSwitchAIO
from dash_iconify import DashIconify

from .graph_elements import get_cytoscape_style

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

                        html.Div([
                            html.Label("Burn-in choose [0.0, 1.0):",
                                       htmlFor="burn-in-selection",
                                       style={"width": "200px", "display": "inline-block"}),
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

                        dbc.Input(id="dataset-label", placeholder="Enter dataset label...",
                                  type="text",
                                  style={"marginBottom": "10px"}),
                        dbc.Button("Confirm Dataset", id="confirm-dataset-btn", color="primary"),
                        dcc.Store(id="uploaded-datasets-store"),
                    ])
                ]),

                html.H2("Graph Controls", className="mt-2"),

                html.Div([
                    html.Div([
                        dbc.Button(
                            [
                                DashIconify(icon="mdi:crosshairs-gps", width=16,
                                            style={"marginRight": "6px"}),
                                "Recenter Graph"
                            ],
                            id="recenter-btn",
                            n_clicks=0,
                            color="primary",
                            outline=True,
                            style={"marginRight": "10px"}
                        )
                    ], style={"marginBottom": "15px"}),

                    html.Div([
                        html.Label("Edge label sets to display:", htmlFor="label-filter",
                                   style={"fontWeight": "bold", "marginBottom": "5px"}),
                        dcc.Dropdown(
                            id="label-filter",
                            options=[],
                            value=[],
                            multi=True,
                            style={"marginBottom": "10px"}
                        )
                    ], style={"marginBottom": "15px"}),

                    html.Div([
                        html.Label("Graph Layout:", htmlFor="layout-selector",
                                   style={"fontWeight": "bold", "marginBottom": "5px"}),
                        dcc.Dropdown(
                            id="layout-selector",
                            options=[
                                {"label": "Dagre (Hierarchical) [best Graphviz alt]", "value":
                                    "dagre"},
                                {"label": "Breadthfirst (Hierarchical)", "value": "breadthfirst"},
                                {"label": "Cose (Spring)", "value": "cose"},
                                {"label": "Cose-Bilkent (improved force)", "value": "cose-bilkent"},
                                {"label": "Euler (force-directed)", "value": "euler"},
                                {"label": "Grid (rows/columns)", "value": "grid"},
                                {"label": "Circle (circular node layout)", "value": "circle"},
                                {"label": "Cola (constraint-based)", "value": "cola"},
                                {"label": "Spread (hybrid layout)", "value": "spread"},
                                {"label": "Klay (layered)", "value": "klay"},
                            ],
                            value="dagre",
                            clearable=False,
                            style={"marginBottom": "15px"}
                        )
                    ]),

                    html.Div([
                        html.Label("Edge Annotation:", htmlFor="edge-annotation-selector",
                                   style={"fontWeight": "bold", "marginBottom": "5px"}),
                        dcc.Dropdown(
                            id="edge-annotation-selector",
                            options=[
                                {"label": "None", "value": "none"},
                                {"label": "Label", "value": "label"},
                                {"label": "Posterior", "value": "posterior"}
                            ],
                            value="label",
                            clearable=False,
                            style={"marginBottom": "15px"}
                        )
                    ]),

                    html.Div([
                        html.Label("Edge Label Position:", htmlFor="edge-label-position",
                                   style={"fontWeight": "bold", "marginBottom": "5px"}),
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
                            style={"marginBottom": "15px"}
                        )
                    ])
                ]),
                html.Hr(),
                html.Div([
                    html.Div([
                        html.Label("Edge weight threshold:", htmlFor="weight-threshold",
                                   style={"width": "200px", "display": "inline-block"}),
                        dcc.Input(
                            id="weight-threshold",
                            type="number",
                            min=0,
                            max=1,
                            step=0.01,
                            value=0.0,
                            debounce=True,
                            style={"width": "200px"},
                        ),
                    ], style={"margin-bottom": "10px"}),

                    html.Div([
                        html.Label("Edge label font size:", htmlFor="edge-label-font-size",
                                   style={"width": "200px", "display": "inline-block"}),
                        dcc.Input(
                            id="edge-label-font-size",
                            type="number",
                            min=1,
                            max=30,
                            step=1,
                            value=5,
                            debounce=True,
                            style={"width": "200px"},
                        ),
                    ])
                ]),
                html.Hr(),
                html.Div([
                    dcc.Checklist(
                        id="scale-width-toggle",
                        options=[{"label": "Scale edge width by weight", "value": "scale"}],
                        value=["scale"],
                        inline=True,
                        style={"marginBottom": "10px"}
                    ),
                    dcc.Checklist(
                        id="color-by-label-toggle",
                        options=[{"label": "Color edges by label", "value": "color"}],
                        value=[],
                        inline=True,
                        style={"marginBottom": "10px"}
                    )
                ]),
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

                html.Div(
                    className='four columns',
                    children=[
                        html.H4("Export Graph", style={"marginBottom": "15px"}),

                        html.Div(
                            style={"display": "flex", "alignItems": "center", "gap": "10px",
                                   "marginBottom": "15px"},
                            children=[
                                html.Div("Filename:",
                                         style={"whiteSpace": "nowrap", "fontWeight": "500"}),
                                dcc.Input(
                                    id="image-filename-input",
                                    type="text",
                                    value="wiw-network",
                                    debounce=True,
                                    style={"width": "100%"}
                                )
                            ]
                        ),
                        html.Div(
                            children=[
                                dbc.ButtonGroup([
                                    dbc.Button([
                                        DashIconify(icon="mdi:download", width=16),
                                        " JPG"
                                    ], id="btn-get-jpg", n_clicks=0,
                                        color="secondary", outline=True),

                                    dbc.Button([
                                        DashIconify(icon="mdi:download", width=16),
                                        " PNG"
                                    ], id="btn-get-png", n_clicks=0,
                                        color="secondary", outline=True),

                                    dbc.Button([
                                        DashIconify(icon="mdi:download", width=16),
                                        " SVG"
                                    ], id="btn-get-svg", n_clicks=0,
                                        color="secondary", outline=True)
                                ])
                            ])
                    ]
                ),

                html.Hr(),
                html.Div([
                    html.Div([
                        dcc.ConfirmDialog(
                            id="confirm-reset",
                            message="Do you really want to reset the graph to be empty?"
                        ),
                        dbc.Button(
                            [
                                DashIconify(icon="mdi:restart-alert", width=16,
                                            style={"marginRight": "6px"}),
                                "Reset Graph"
                            ],
                            id="reset-graph-btn",
                            n_clicks=0,
                            color="danger",
                            outline=True,
                            style={"marginRight": "10px"}
                        )
                    ]),
                ], style={"display": "flex", "marginBottom": "10px"}),

                html.Hr(),
                html.Div([
                    html.H5("Log Information:"),
                    html.Pre(id="log-output", style={
                        "maxHeight": "400px",
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
                style=get_cytoscape_style(False),
                zoom=1,
                pan={'x': 0, 'y': 0}
            ),
            width=10,
            style={"padding": "0"}  # Remove padding for full-width visualization
        )
    ], style={"margin": "0", "width": "100%", "height": "100vh", "overflow": "hidden"})
])
