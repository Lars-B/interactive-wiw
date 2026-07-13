import dash_bootstrap_components as dbc
from dash import html, dcc
from dash_iconify import DashIconify

from wiw_app.ids import DOWNLOAD

DOWNLOAD_BUTTONS = {
    "image": [
        {"id": DOWNLOAD.GET_JPG_BUTTON, "icon": "mdi-download", "label": "JPG"},
        {"id": DOWNLOAD.GET_PNG_BUTTON, "icon": "mdi-download", "label": "PNG"},
        {"id": DOWNLOAD.GET_SVG_BUTTON, "icon": "mdi-download", "label": "SVG"},
        {"id": DOWNLOAD.GET_DOT_BUTTON, "icon": "mdi-download", "label": "DOT"},
    ],
    "extras": [
        {"id": DOWNLOAD.GET_PNG_WITH_LEGEND, "icon": "mdi:map-legend", "label": "PNG+"},
        {"id": DOWNLOAD.GET_LEGEND_SVG_BUTTON, "icon": "mdi:map-marker", "label": "Legend SVG"},
    ]
}


def make_download_button(spec, color="secondary"):
    return dbc.Button(
        [DashIconify(icon=spec["icon"], width=16), f" {spec["label"]}"],
        id=spec["id"], n_clicks=0,
        color=color,
        outline=True
    )


def make_download_button_group(section_key, color="secondary"):
    return dbc.ButtonGroup(
        [make_download_button(spec, color) for spec in DOWNLOAD_BUTTONS[section_key]],
    )


download_layout = html.Div(
    className="four columns",
    children=[
        # Hidden download triggers / state
        dcc.Download(id="download-dot"),
        dcc.Download(id="download-pngplus"),
        dcc.Download(id="download-legend"),
        dcc.Store(id="pngplus-requested", data=False),

        # UI for download buttons
        dbc.Card(
            dbc.CardBody(
                [
                    html.Div(
                        style={"display": "flex", "alignItems": "center",
                               "gap": "10px", "marginBottom": "15px"},
                        children=[
                            html.Div("Filename:",
                                     style={"whiteSpace": "nowrap", "fontWeight": "500"}),
                            dcc.Input(
                                id=DOWNLOAD.FILENAME_INPUT,
                                type="text",
                                value="wiw-network",
                                debounce=True,
                                style={"width": "100%"},
                            ),
                        ],
                    ),

                    html.Div("Network Image Export", style={
                        "fontSize": "12px", "fontWeight": "600", "color": "primary",
                        "textTransform": "uppercase", "marginBottom": "6px",
                    }),
                    html.Div(make_download_button_group("image"), style={"marginBottom": "15px"}),

                    html.Div("Network and Legend", style={
                        "fontSize": "12px", "fontWeight": "600", "color": "primary",
                        "textTransform": "uppercase", "marginBottom": "6px",
                    }),
                    html.Div(make_download_button_group("extras")),
                ]
            ),
            style={"marginBottom": "10px"},
        ),
    ],
)
