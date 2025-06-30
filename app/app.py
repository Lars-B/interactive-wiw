import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import html, dcc
from dash_bootstrap_templates import ThemeSwitchAIO

from .graph_elements import build_graph

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
    dbc.Row([
        # Sidebar
        dbc.Col(
            [
                html.H5("Graph Controls", className="mt-2"),
                ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2],
                               switch_props={"value": False}),
                html.Hr(),

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
                    value=[],  # default: unchecked
                    inline=True,
                    style={"margin-bottom": "10px"}
                ),
                dcc.Store(id="label-color-store"),
                dbc.Collapse(
                    html.Div(id="color-pickers-container", style={"marginTop": "20px"}),
                    id="color-pickers-collapse",
                    is_open=False
                )
            ],
            width=3,  # 3 of 12 columns
            style={
                # "backgroundColor": "#f8f9fa",
                "padding": "15px",
                "height": "100vh",
                "overflowY": "auto"
            }
        ),
        # Graph Area
        dbc.Col(
            cyto.Cytoscape(
                id='cytoscape',
                elements=build_graph()[0] + build_graph()[1],
                layout={'name': 'cose'},
                style={'width': '100%', 'height': '100vh', 'backgroundColor': '#ffffff'},
                zoom=1,
                pan={'x': 0, 'y': 0}
            ),
            width=9,
            style={"padding": "0"}  # Remove padding for full-width visualization
        )
    ], style={"margin": "0", "width": "100%", "height": "100vh", "overflow": "hidden"})
])
