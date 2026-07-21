import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from .ids import UploadIDs

cyto.load_extra_layouts()

from dash import html, dcc, Dash
from dash_bootstrap_templates import ThemeSwitchAIO

from .graph_elements import get_cytoscape_style
from .layouts import *

from dash_resizable_panels import PanelGroup, Panel, PanelResizeHandle

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
    suppress_callback_exceptions=True
)

app.layout = html.Div([
    dcc.Store(id="graph-store"),
    data_loading_modal,
    data_loading_modal_tp,
    data_loading_modal_outbreaker,

    PanelGroup(
        id="panel-group",
        direction="horizontal",
        children=[

            # Sidebar
            Panel(
                id="sidebar-panel",
                collapsible=True,
                defaultSizePercentage=20,
                minSizePercentage=10,
                maxSizePercentage=50,
                children=[
                    html.Div(
                        [
                            ThemeSwitchAIO(
                                aio_id="theme",
                                themes=[url_theme1, url_theme2],
                                switch_props={"value": False}
                            ),

                            html.Div([
                                html.Hr(),
                                dbc.InputGroup([
                                    dbc.InputGroupText("Upload type"),
                                    upload_mode_selector
                                ]),
                                html.Hr(),
                                html.Div(id="upload-ui-container")
                            ]),

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

                            html.Hr(),
                            html.H2("Graph Controls", className="mt-2"),
                            html.Hr(),

                            html.Div([graph_option_tabs]),

                            html.Hr(),
                            html.H2(
                                "Download Network Image",
                                style={"marginBottom": "15px"}
                            ),
                            html.Hr(),

                            download_layout,

                            html.Hr(),
                        ],
                        style={
                            "padding": "15px",
                            "height": "100vh",
                            "overflowY": "auto"
                        }
                    )
                ]
            ),

            PanelResizeHandle(
                html.Div(
                    style={
                        "width": "5px",
                        "height": "100%",
                        "backgroundColor": "#ccc",
                        "cursor": "col-resize"
                    }
                )
            ),

            # Cytoscape panel
            Panel(
                id="graph-panel",
                children=[
                    cyto.Cytoscape(
                        id="cytoscape",
                        elements=[],
                        layout={"name": "cose"},
                        style=get_cytoscape_style(False),
                        zoom=1,
                        pan={"x": 0, "y": 0},
                        clearOnUnhover=True,
                        responsive=True
                    )
                ]
            ),
        ]
    ),

    html.Div(
        id="node-tooltip",
        style={
            "display": "none",
            "position": "absolute",
            "padding": "10px",
            "zIndex": 1000,
        },
    ),

], style={"height": "100vh"})
