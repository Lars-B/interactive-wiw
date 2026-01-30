import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from wiw_app.ids import UploadIDs

cyto.load_extra_layouts()

from dash import html, dcc, Dash
from dash_bootstrap_templates import ThemeSwitchAIO
from dash_iconify import DashIconify

from wiw_app.graph_elements import get_cytoscape_style
from wiw_app.layouts import *

dcc.Store(id="graph-store")

template_theme1 = "morph"
template_theme2 = "slate"
url_theme1 = dbc.themes.MORPH
url_theme2 = dbc.themes.SLATE

dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css"
)

app = Dash(
    __name__,
    external_stylesheets=[url_theme1, dbc_css],
    assets_folder="../assets",
)

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

                dbc.Toast(
                    id=UploadIDs.INFO_TOAST,
                    header="Upload Info",
                    is_open=False,
                    dismissable=True,
                    style={
                        "position": "fixed",
                        "top": 66,
                        "right": "50%",
                        "width": 350,
                        "zIndex": 2000
                    },
                ),

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
                        dcc.Download(id="download-pngplus"),  # todo what is that for?
                        dcc.Store(id="pngplus-requested", data=False),
                        dcc.Download(id="download-legend"),
                        html.Div(
                            children=[
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
                                    ]),
                                html.Div(
                                    children=[
                                        dbc.Button([
                                            DashIconify(icon="mdi:map-legend", width=16),
                                            " PNG+"
                                        ], id="btn-get-pngplus", n_clicks=0,
                                            color="secondary", outline=True),
                                        dbc.Button([
                                            DashIconify(icon="mdi:map-marker", width=16),
                                            " Legend (SVG)"
                                        ], id="btn-get-legend", n_clicks=0,
                                            color="secondary", outline=True),
                                    ]
                                )

                            ])
                    ]
                ),
                html.Hr(),
            ],
            xs=6,
            sm=6,
            md=5,
            lg=4,
            xl=3,
            xxl=2,
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
            xs=6,
            sm=6,
            md=7,
            lg=8,
            xl=9,
            xxl=10,
            style={"padding": "0"}  # Remove padding for full-width visualization
        )
    ], style={"margin": "0", "width": "100%", "height": "100vh", "overflow": "hidden"})
])
