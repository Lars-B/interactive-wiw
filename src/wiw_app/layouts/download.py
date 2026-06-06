import dash_bootstrap_components as dbc
from dash import html, dcc
from dash_iconify import DashIconify
from wiw_app.ids import GraphOptions

download_layout = html.Div(
    className='four columns',
    children=[
        html.Div(
            style={"display": "flex", "alignItems": "center",
                   "gap": "10px",
                   "marginBottom": "15px"},
            children=[
                html.Div("Filename:",
                         style={"whiteSpace": "nowrap",
                                "fontWeight": "500"}),
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
        dcc.Download(id="download-pngplus"),
        # todo what is that for?
        dcc.Store(id="pngplus-requested", data=False),
        dcc.Download(id="download-legend"),
        html.Div(
            children=[
                html.Div(
                    children=[
                        dbc.ButtonGroup([
                            dbc.Button([
                                DashIconify(icon="mdi:download",
                                            width=16),
                                " JPG"
                            ], id="btn-get-jpg", n_clicks=0,
                                color="secondary",
                                outline=True),

                            dbc.Button([
                                DashIconify(icon="mdi:download",
                                            width=16),
                                " PNG"
                            ], id="btn-get-png", n_clicks=0,
                                color="secondary",
                                outline=True),

                            dbc.Button([
                                DashIconify(icon="mdi:download",
                                            width=16),
                                " SVG"
                            ], id="btn-get-svg", n_clicks=0,
                                color="secondary",
                                outline=True),

                            dbc.Button([
                                DashIconify(
                                    icon="mdi:code-tags",
                                    width=16),
                                " DOT"
                            ], id="btn-get-dot", n_clicks=0,
                                color="secondary",
                                outline=True),
                        ])
                    ]),
                html.Div(
                    children=[
                        dbc.Button([
                            DashIconify(icon="mdi:map-legend",
                                        width=16),
                            " PNG+"
                        ], id="btn-get-pngplus", n_clicks=0,
                            color="secondary", outline=True),
                        dbc.Button(
                            [
                                DashIconify(
                                    icon="mdi:map-marker",
                                    width=16),
                                " Legend (SVG)"
                            ], id=GraphOptions.Legend.GET_SVG_BUTTON,
                            n_clicks=0,
                            color="secondary", outline=True),
                        dbc.Button([
                            DashIconify(icon="mdi:eye-plus",
                                        width=16),
                            " "
                        ], id=GraphOptions.Legend.ADD_LEG_NODE,
                            n_clicks=0,
                            color="secondary", outline=True),
                        dbc.Button(
                            [
                                DashIconify(
                                    icon="mdi:eye-minus",
                                    width=16),
                                " "
                            ], id=GraphOptions.Legend.REMOVE_LEG_NODE,
                            n_clicks=0,
                            color="secondary", outline=True),
                    ]
                )

            ]
        )
    ]
)
