import dash_bootstrap_components as dbc
from dash import html, dcc
from dash_iconify import DashIconify

from ..ids import GraphOptions

graph_option_tabs = dbc.Tabs(
    children=
    [
        dbc.Tab(
            label="Graph options",
            tab_id=GraphOptions.Graph.TAB,
            children=[
                html.Div([
                    html.Label("Graph Layout:", htmlFor=GraphOptions.Graph.LAYOUT_SELECTOR,
                               style={"fontWeight": "bold", "marginBottom": "5px"}),
                    dcc.Dropdown(
                        id=GraphOptions.Graph.LAYOUT_SELECTOR,
                        options=[
                            {"label": "Dagre (Hierarchical) [best Graphviz alt]", "value":
                                "dagre"},
                            {"label": "Breadthfirst (Hierarchical)",
                             "value": "breadthfirst"},
                            {"label": "Cose (Spring)", "value": "cose"},
                            {"label": "Cose-Bilkent (improved force)",
                             "value": "cose-bilkent"},
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
                    dbc.Button(
                        [
                            DashIconify(icon="mdi:crosshairs-gps", width=16,
                                        style={"marginRight": "6px"}),
                            "Recenter Graph"
                        ],
                        id=GraphOptions.Graph.RENCENTER_BTN,
                        n_clicks=0,
                        color="primary",
                        outline=True,
                        style={"marginRight": "10px"}
                    )
                ], style={"marginBottom": "15px"}),

                # todo this should be within a collapse DANGER ZONE...
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
            ]
        ),
        dbc.Tab(
            label="Edge options",
            tab_id=GraphOptions.Edges.TAB,
            children=[
                html.Div([
                    html.Label("Edge label sets to display:",
                               htmlFor=GraphOptions.Edges.DISPLAY_FILTER,
                               style={"fontWeight": "bold", "marginBottom": "5px"}),
                    dcc.Dropdown(
                        id=GraphOptions.Edges.DISPLAY_FILTER,
                        options=[],
                        value=[],
                        multi=True,
                        style={"marginBottom": "10px"}
                    )
                ], style={"marginBottom": "15px"}),
                html.Div([
                    html.Label("Edge Annotation:", htmlFor=GraphOptions.Edges.ANNOTATION_SELECTOR,
                               style={"fontWeight": "bold", "marginBottom": "5px"}),
                    dcc.Dropdown(
                        id=GraphOptions.Edges.ANNOTATION_SELECTOR,
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
                    html.Label("Edge Label Position:", htmlFor=GraphOptions.Edges.LABEL_POSITION,
                               style={"fontWeight": "bold", "marginBottom": "5px"}),
                    dcc.Dropdown(
                        id=GraphOptions.Edges.LABEL_POSITION,
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
                ]),

                html.Div(
                    [
                        dbc.Button([
                            DashIconify(icon="mdi:cheese-off",
                                        width=16,
                                        id=GraphOptions.Edges.ADVANCED_OPTIONS_ICON,
                                        style={"marginRight": "6px"}),
                            "Further Options: "
                        ],
                            id=GraphOptions.Edges.ADVANCED_OPTION_TOGGLE_BTN,
                            outline=True,
                            n_clicks=0,
                        ),
                        dbc.Collapse(
                            html.Div([
                                html.Div([
                                    html.Label(
                                        "Edge weight threshold:",
                                        htmlFor="weight-threshold",
                                        style={
                                            "display": "block",
                                            "marginBottom": "0.5rem",
                                            "fontWeight": "bold",
                                            "text-align": "left"
                                        }
                                    ),
                                    dcc.Slider(
                                        id="weight-threshold",
                                        min=0.0,
                                        max=0.99,
                                        step=0.01,
                                        value=0.0,
                                        marks={i: str(i) for i in
                                               [i / 10 for i in range(0, 11, 1)]},
                                        tooltip={"placement": "bottom", "always_visible": True},
                                    )
                                ], style={"width": "100%", "marginBottom": "1rem",
                                          "marginTop": "1rem"}),

                                html.Div([
                                    html.Label(
                                        "Edge label font size:",
                                        htmlFor="edge-label-font-size",
                                        style={
                                            "display": "block",
                                            "marginBottom": "0.5rem",
                                            "fontWeight": "bold",
                                            "text-align": "left"
                                        }
                                    ),
                                    dcc.Slider(
                                        id="edge-label-font-size",
                                        min=1,
                                        max=30,
                                        step=1,
                                        value=5,
                                        marks={i: str(i) for i in range(0, 31, 5)},
                                        tooltip={"placement": "bottom", "always_visible": True},
                                    )
                                ], style={"width": "100%", "marginBottom": "1rem",
                                          "marginTop": "1rem"}),
                            ]),
                            id=GraphOptions.Edges.ADVANCED_OPTIONS_COLLAPSE,
                            is_open=False
                        )
                    ]
                ),

                html.Div([
                    dcc.Checklist(
                        id=GraphOptions.Edges.SCALE_WIDTH_BY_WEIGHT,
                        options=[{"label": "Scale edge width by weight", "value": "scale"}],
                        value=["scale"],
                        inline=True,
                        style={"marginBottom": "10px"}
                    ),
                    dcc.Checklist(
                        id=GraphOptions.Edges.COLOR_BY_LABEL,
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
            ]
        ),
        dbc.Tab(
            label="Node options",
            tab_id=GraphOptions.Nodes.TAB,
            children=[
                html.Div([
                    html.Label("Node Annotation:", htmlFor="node-annotation-selector",
                               style={"fontWeight": "bold", "marginBottom": "5px"}),
                    dcc.Dropdown(
                        id="node-annotation-selector",
                        options=[
                            {"label": "None", "value": "none"},
                            {"label": "Label", "value": "label"},
                            {"label": "Taxon", "value": "taxon"}
                        ],
                        value="label",
                        clearable=False,
                        style={"marginBottom": "15px"}
                    )
                ]),
                html.Div(
                    [
                        dbc.Button([
                            DashIconify(icon="mdi:cheese-off",
                                        width=16,
                                        id=GraphOptions.Nodes.ADVANCED_OPTIONS_ICON,
                                        style={"marginRight": "6px"}),
                            "Further Options"
                        ],
                            id=GraphOptions.Nodes.ADVANCED_OPTION_TOGGLE_BTN,
                            outline=True,
                            n_clicks=0,
                        ),
                        dbc.Collapse(
                            html.Div([
                                html.Div([
                                    html.Label(
                                        "Node label font size:",
                                        htmlFor=GraphOptions.Nodes.LABEL_FONT_SIZE,
                                        style={
                                            "display": "block",
                                            "marginBottom": "0.5rem",
                                            "fontWeight": "bold",
                                            "text-align": "left"
                                        }
                                    ),
                                    dcc.Slider(
                                        id=GraphOptions.Nodes.LABEL_FONT_SIZE,
                                        min=1,
                                        max=30,
                                        step=1,
                                        value=12,
                                        marks={i: str(i) for i in range(0, 31, 5)},
                                        tooltip={"placement": "bottom", "always_visible": True},
                                    )
                                ], style={"width": "100%", "marginBottom": "1rem"})
                            ]),
                            id=GraphOptions.Nodes.ADVANCED_OPTIONS_COLLAPSE,
                            is_open=False
                        )
                    ]
                ),
            ]
        )
    ],
    id=GraphOptions.TABS,
    active_tab=GraphOptions.Graph.TAB,
)
