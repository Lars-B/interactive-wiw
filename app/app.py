import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import html, dcc
from dash_bootstrap_templates import ThemeSwitchAIO
from dash_iconify import DashIconify

from . import app, url_theme1, url_theme2
from .graph_elements import get_cytoscape_style
from .layouts import *

dcc.Store(id="graph-store")

app.layout = html.Div([
    dcc.Store(id="graph-store"),
    data_loading_modal,
    dbc.Row([
        # Sidebar
        dbc.Col(
            [
                ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2],
                               switch_props={"value": False}),

                html.H2("Upload Data", className="mt-2"),
                html.Hr(),
                html.Div([upload_tabs]),

                html.H2("Graph Controls", className="mt-2"),

                html.Hr(),

                html.Div([graph_option_tabs]),

                html.H2("Export Graph", style={"marginBottom": "15px"}),
                html.Hr(),
                html.Div(
                    className='four columns',
                    children=[
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
                        dcc.Download(id="download-dot"),
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
                                        color="secondary", outline=True),

                                    dbc.Button([
                                        DashIconify(icon="mdi:code-tags", width=16),
                                        " DOT"
                                    ], id="btn-get-dot", n_clicks=0,
                                        color="secondary", outline=True),
                                ])
                            ])
                    ]
                ),
                html.Hr(),
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
