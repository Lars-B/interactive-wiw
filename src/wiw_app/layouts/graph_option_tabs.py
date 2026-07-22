import dash_bootstrap_components as dbc
from dash import html, dcc
from dash_iconify import DashIconify

from wiw_app.config import EdgeConfig, NodeConfig, GraphConfig
from wiw_app.ids import GraphOptions

graph_option_tabs = dbc.Tabs(
    children=
    [
        dbc.Tab(
            label="Graph",
            tab_id=GraphOptions.Graph.TAB,
            children=[
                html.Div([
                    html.Label("Graph Layout:",
                               htmlFor=GraphOptions.Graph.LAYOUT_SELECTOR,
                               style={"fontWeight": "bold",
                                      "marginBottom": "5px"}),
                    dcc.Dropdown(
                        id=GraphOptions.Graph.LAYOUT_SELECTOR,
                        options=[
                            {
                                "label": "Dagre (Hierarchical) [best Graphviz alt]",
                                "value": "dagre"
                            },
                            {"label": "Breadthfirst (Hierarchical)",
                             "value": "breadthfirst"},
                            {"label": "Cose (Spring)", "value": "cose"},
                            {"label": "Cose-Bilkent (improved force)",
                             "value": "cose-bilkent"},
                            {"label": "Euler (force-directed)",
                             "value": "euler"},
                            {"label": "Grid (rows/columns)", "value": "grid"},
                            {"label": "Circle (circular node layout)",
                             "value": "circle"},
                            {"label": "Cola (constraint-based)",
                             "value": "cola"},
                            {"label": "Spread (hybrid layout)",
                             "value": "spread"},
                            {"label": "Klay (layered)", "value": "klay"},
                        ],
                        value=GraphConfig.DEFAULT_LAYOUT,
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
                    ),
                    dbc.ButtonGroup([
                        dbc.Button([
                            DashIconify(icon="mdi:eye-plus",
                                        width=16),
                            " Legend"
                        ],
                            id=GraphOptions.Legend.ADD_LEG_NODE,
                            n_clicks=0,
                            color="primary", outline=True
                        ),
                        dbc.Button(
                            [
                                DashIconify(
                                    icon="mdi:eye-minus",
                                    width=16),
                                " Legend"
                            ],
                            id=GraphOptions.Legend.REMOVE_LEG_NODE,
                            n_clicks=0,
                            color="primary",
                            outline=True
                        )
                    ]),
                ], style={"marginBottom": "15px"}),

                html.Div([
                    dbc.Button(
                        [
                            DashIconify(icon="mdi:alert-octagon-outline", width=16,
                                        style={"marginRight": "6px"}),
                            "Danger Zone"
                        ],
                        id="danger-zone-toggle",
                        n_clicks=0,
                        color="danger",
                        outline=True,
                        size="sm",
                        style={"marginBottom": "8px"}
                    ),
                    dbc.Collapse(
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
                        ], style={
                            "border": "1px solid #dc3545",
                            "borderRadius": "6px",
                            "padding": "10px",
                            "display": "flex"
                        }),
                        id="danger-zone-collapse",
                        is_open=False,
                    ),
                ],
                    style={"marginBottom": "10px"}
                )
            ]
        ),
        dbc.Tab(
            label="Edges",
            tab_id=GraphOptions.Edges.TAB,
            children=[
                html.Div([
                    html.Label("Edge label sets to display:",
                               htmlFor=GraphOptions.Edges.DISPLAY_FILTER,
                               style={"fontWeight": "bold",
                                      "marginBottom": "5px"}),
                    dcc.Dropdown(
                        id=GraphOptions.Edges.DISPLAY_FILTER,
                        options=[],
                        value=[],
                        multi=True,
                        style={"marginBottom": "10px"}
                    )
                ], style={"marginBottom": "15px"}),
                html.Div([
                    html.Label("Edge Annotation:",
                               htmlFor=GraphOptions.Edges.ANNOTATION_SELECTOR,
                               style={"fontWeight": "bold",
                                      "marginBottom": "5px"}),
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
                    html.Label("Edge Label Position:",
                               htmlFor=GraphOptions.Edges.LABEL_POSITION,
                               style={"fontWeight": "bold",
                                      "marginBottom": "5px"}),
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
                                        htmlFor=GraphOptions.Edges.DISPLAY_EDGE_THRESHOLD,
                                        style={
                                            "display": "block",
                                            "marginBottom": "0.5rem",
                                            "fontWeight": "bold",
                                            "text-align": "left"
                                        }
                                    ),
                                    dcc.Slider(
                                        id=GraphOptions.Edges.DISPLAY_EDGE_THRESHOLD,
                                        min=EdgeConfig.THRESHOLD_MIN,
                                        max=EdgeConfig.THRESHOLD_MAX,
                                        step=EdgeConfig.THRESHOLD_STEP,
                                        value=EdgeConfig.THRESHOLD_DEFAULT,
                                        marks=EdgeConfig.THRESHOLD_MARKS,
                                        tooltip={"placement": "bottom",
                                                 "always_visible": True},
                                    )
                                ], style={"width": "100%",
                                          "marginBottom": "1rem",
                                          "marginTop": "1rem"}),

                                html.Div([
                                    html.Label(
                                        "Edge label font size:",
                                        htmlFor=GraphOptions.Edges.LABEL_FONT_SIZE,
                                        style={
                                            "display": "block",
                                            "marginBottom": "0.5rem",
                                            "fontWeight": "bold",
                                            "text-align": "left"
                                        }
                                    ),
                                    dcc.Slider(
                                        id=GraphOptions.Edges.LABEL_FONT_SIZE,
                                        min=EdgeConfig.LABEL_FONT_MIN,
                                        max=EdgeConfig.LABEL_FONT_MAX,
                                        step=EdgeConfig.LABEL_FONT_STEP,
                                        value=EdgeConfig.LABEL_FONT_DEFAULT,
                                        marks=EdgeConfig.LABEL_FONT_MARKS,
                                        tooltip={"placement": "bottom",
                                                 "always_visible": True},
                                    )
                                ], style={"width": "100%",
                                          "marginBottom": "1rem",
                                          "marginTop": "1rem"}),

                                html.Div([
                                    html.Label("Edge Curve Styles",
                                               htmlFor=GraphOptions.Edges.CURVE_STYLE_SELECTOR,
                                               style={"fontWeight": "bold",
                                                      "marginBottom": "5px"}),
                                    dcc.Dropdown(
                                        id=GraphOptions.Edges.CURVE_STYLE_SELECTOR,
                                        options=[
                                            {
                                                "label": "Bezier",
                                                "value": "bezier"
                                            },
                                            {
                                                "label": "Unbundled Bezier",
                                                "value": "unbundled-bezier"
                                            },
                                            {
                                                "label": "Straight",
                                                "value": "straight"
                                            },
                                            {
                                                "label": "Straight Triangle",
                                                "value": "straight-triangle"
                                            },
                                            {
                                                "label": "Segments",
                                                "value": "segments"
                                            },
                                            {
                                                "label": "Taxi",
                                                "value": "taxi"
                                            },
                                        ],
                                        value=EdgeConfig.DEFAULT_EDGE_CURVE_STYLE,
                                        clearable=False,
                                        style={"marginBottom": "15px"}
                                    )
                                ]),

                                html.Div([
                                    dcc.Checklist(
                                        id=GraphOptions.Edges.TOGGLE_ARROWS,
                                        options=[{"label": "Hide edge arrows",
                                                  "value": "toggle"}],
                                        value=[],
                                        inline=True,
                                        style={"marginBottom": "10px"},
                                        # TODO this color is not nice, but fixes the visibility
                                        labelStyle={'color': 'gray'}
                                    )
                                ], style={"width": "100%",
                                          "marginBottom": "1rem"})
                            ]),
                            id=GraphOptions.Edges.ADVANCED_OPTIONS_COLLAPSE,
                            is_open=False
                        )
                    ]
                ),

                html.Div([
                    html.Div([
                        dcc.Checklist(
                            id=GraphOptions.Edges.SCALE_WIDTH_BY_WEIGHT,
                            options=[{"label": "Scale edge width by weight",
                                      "value": "scale"}],
                            value=["scale"],
                            inline=True,
                            style={"marginBottom": "10px"},
                            # TODO this color is not nice, but fixes the visibility
                            labelStyle={'color': 'gray'}
                        ),

                        dcc.Input(
                            id=GraphOptions.Edges.SCALE_VALUE_INPUT,
                            type="number",
                            value=EdgeConfig.SCALE_DEFAULT,
                            min=EdgeConfig.SCALE_MIN,
                            max=EdgeConfig.SCALE_MAX,
                            step=EdgeConfig.SCALE_STEP,
                            style={"width": "80px", "marginLeft": "10px"},
                            debounce=True,
                        ),
                    ], style={"display": "flex", "alignItems": "center"}),

                    dcc.Checklist(
                        id=GraphOptions.Edges.COLOR_BY_LABEL,
                        options=[{"label": "Color edges by label",
                                  "value": "color"}],
                        value=[],
                        inline=True,
                        style={"marginBottom": "10px"},
                        # TODO this color is not nice, but fixes the visibility
                        labelStyle={'color': 'gray'}
                    ),
                ]),

                dcc.Store(id=GraphOptions.Edges.COLOR_STORE),
                dbc.Collapse(
                    html.Div(
                        [
                            html.Div(id=GraphOptions.Edges.LABEL_RENAME_ERROR,
                                     style={"color": "red",
                                            "marginBottom": "10px"}),
                            html.Div(
                                id=GraphOptions.Edges.COLOR_PICKER_CONTAINERS,
                                style={"marginTop": "10px"})
                        ]
                    ),
                    id=GraphOptions.Edges.COLOR_PICKERS_COLLAPSE,
                    is_open=False
                ),
            ]
        ),
        dbc.Tab(
            label="Nodes",
            tab_id=GraphOptions.Nodes.TAB,
            children=[
                html.Div([
                    html.Label("Node Annotation:",
                               htmlFor=GraphOptions.Nodes.LABEL_ANNOTATION_SELECTOR,
                               style={"fontWeight": "bold",
                                      "marginBottom": "5px"}),
                    dcc.Dropdown(
                        id=GraphOptions.Nodes.LABEL_ANNOTATION_SELECTOR,
                        options=[
                            # dynamically updated via callback...
                        ],
                        value="id",
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
                                        min=NodeConfig.LABEL_FONT_MIN,
                                        max=NodeConfig.LABEL_FONT_MAX,
                                        step=NodeConfig.LABEL_FONT_STEP,
                                        value=NodeConfig.LABEL_FONT_DEFAULT,
                                        marks=NodeConfig.LABEL_FONT_MARKS,
                                        tooltip={"placement": "bottom",
                                                 "always_visible": True},
                                    )
                                ], style={"width": "100%",
                                          "marginBottom": "1rem"}),
                                html.Div([
                                    html.Label(
                                        "Node size:",
                                        htmlFor=GraphOptions.Nodes.SIZE_SELECTOR,
                                        style={
                                            "display": "block",
                                            "marginBottom": "0.5rem",
                                            "fontWeight": "bold",
                                            "textAlign": "left"
                                        }
                                    ),
                                    dcc.Slider(
                                        id=GraphOptions.Nodes.SIZE_SELECTOR,
                                        min=NodeConfig.SIZE_MIN,
                                        max=NodeConfig.SIZE_MAX,
                                        step=NodeConfig.SIZE_STEP,
                                        value=NodeConfig.SIZE_DEFAULT,
                                        marks=NodeConfig.SIZE_MARKS,
                                        tooltip={"placement": "bottom",
                                                 "always_visible": True},
                                    )
                                ], style={"width": "100%",
                                          "marginBottom": "1rem"}),
                                html.Div([
                                    html.Label("Node Shapes",
                                               htmlFor=GraphOptions.Nodes.SHAPE_SELECTOR,
                                               style={"fontWeight": "bold",
                                                      "marginBottom": "5px"}),
                                    dcc.Dropdown(
                                        id=GraphOptions.Nodes.SHAPE_SELECTOR,
                                        options=[
                                            {"label": k, "value": v}
                                            for k, v in NodeConfig.NODE_SHAPE_MODES.items()
                                        ],
                                        value=NodeConfig.DEFAULT_SHAPE_SELECTION,
                                        clearable=False,
                                        style={"marginBottom": "15px"}
                                    )
                                ]),
                                html.Div([
                                    dcc.Checklist(
                                        id=GraphOptions.Nodes.SUPPRESS_SINGLETONS,
                                        options=[
                                            {"label": "Suppress Singletons",
                                             "value": "on"}],
                                        value=[],
                                        inline=True,
                                        style={"marginBottom": "10px"},
                                        # TODO this color is not nice, but fixes the visibility
                                        labelStyle={'color': 'gray'}
                                    ),
                                ])
                            ]),
                            id=GraphOptions.Nodes.ADVANCED_OPTIONS_COLLAPSE,
                            is_open=False
                        ),
                        html.Div([
                            dcc.Checklist(
                                id=GraphOptions.Nodes.COLOR_BY_LABEL,
                                options=[
                                    {"label": "Color nodes by label",
                                     "value": "color"}
                                ],
                                value=[],
                                inline=True,
                                style={"marginBottom": "10px"},
                                # TODO this color is not nice, but fixes the visibility
                                labelStyle={'color': 'gray'}
                            ),
                            dcc.Store(id=GraphOptions.Nodes.COLOR_STORE),
                            dbc.Collapse(
                                html.Div(
                                    [
                                        dbc.RadioItems(
                                            id=GraphOptions.Nodes.COLOR_MODE,
                                            options=[
                                                {
                                                    "label": "Categorical",
                                                    "value": "categorical"
                                                },
                                                {
                                                    "label": "Heatmap",
                                                    "value": "continuous"
                                                },
                                            ],
                                            value="categorical",
                                            inline=True,
                                        ),

                                        # shared node color attribute selector
                                        html.Label(
                                            "Color Nodes by:",
                                            htmlFor=GraphOptions.Nodes.COLOR_LABEL_SELECTOR,
                                            style={
                                                "fontWeight": "bold",
                                                "marginBottom": "5px"
                                            }
                                        ),
                                        dcc.Dropdown(
                                            id=GraphOptions.Nodes.COLOR_LABEL_SELECTOR,
                                            options=[
                                                {
                                                    "label": "Label",
                                                    "value": "label"
                                                }
                                            ],
                                            value="label",
                                            clearable=False,
                                        ),

                                        # categorical options
                                        dbc.Collapse(
                                            html.Div(
                                                [
                                                    html.Div(
                                                        id=GraphOptions.Nodes.COLOR_PICKER_CONTAINERS,
                                                        style={"marginTop": "10px"}
                                                    )
                                                ]
                                            ),
                                            id=GraphOptions.Nodes.CATEGORICAL_COLOR_OPTIONS,
                                            is_open=True,
                                        ),

                                        # heatmap options
                                        dbc.Collapse(
                                            html.Div(
                                                [
                                                    html.Label(
                                                        "Colormap:",
                                                        style={"fontWeight": "bold"}
                                                    ),
                                                    dcc.Dropdown(
                                                        id=GraphOptions.Nodes.COLORMAP_SELECTOR,
                                                        options=[
                                                            {
                                                                "label": str.capitalize(cmap),
                                                                "value": cmap
                                                            }
                                                            for cmap in
                                                            NodeConfig.AVAILABLE_HEATMAP_COLORMAPS
                                                        ],
                                                        value="viridis",
                                                        clearable=False,
                                                    )
                                                ]
                                            ),
                                            id=GraphOptions.Nodes.HEATMAP_OPTIONS_COLLAPSE,
                                            is_open=False,
                                        ),
                                    ]
                                ),
                                id=GraphOptions.Nodes.COLOR_PICKERS_COLLAPSE,
                                is_open=False,
                            )
                        ])
                    ]
                ),
            ]
        )
    ],
    id=GraphOptions.TABS,
    active_tab=GraphOptions.Graph.TAB,
    style={
        "width": "fit-content",
        "display": "flex"
    }
)
