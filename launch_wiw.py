import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import Input, Output, State
from dash import html, dcc
from dash_bootstrap_templates import ThemeSwitchAIO

dcc.Store(id="graph-store")

# todo read input tree file
# todo use pyccd package to compute wiw from posterior, ccd
# todo option to add a true tree, copy paste input
# todo dark and light mode cytoscope background is wrong....

template_theme1 = "morph"
template_theme2 = "slate"
url_theme1 = dbc.themes.MORPH
url_theme2 = dbc.themes.SLATE

dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css"
)


def build_graph(scale_factor=1):
    edges = [
        {"data": {
            "source": "A", "target": "B", "label": "set1",
            "weight": 0.01,  # original semantic value
            "penwidth": 0.01 * scale_factor,
            "id": "e1"
        }},
        {"data": {
            "source": "A", "target": "B", "label": "set2",
            "weight": 0.5,
            "penwidth": 0.5 * scale_factor,
            "id": "e2"
        }},
        {"data": {
            "source": "B", "target": "C", "label": "set1",
            "weight": 0.3,
            "penwidth": 0.3 * scale_factor,
            "id": "e3"
        }},
    ]
    nodes = [{"data": {"id": node, "label": node}} for node in {"A", "B", "C"}]
    return nodes, edges


app = dash.Dash(__name__, external_stylesheets=[url_theme1, dbc_css])



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
                    style={"margin-bottom": "10px"}
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
                    style={"margin-bottom": "10px"}
                ),
                dcc.Checklist(
                    id="scale-width-toggle",
                    options=[{"label": "Scale edge width by weight", "value": "scale"}],
                    value=["scale"],
                    inline=True,
                    style={"margin-bottom": "10px"}
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
                    style={"margin-bottom": "10px"}
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
                    style={"margin-bottom": "10px"}
                ),
                html.Button("Recenter Graph", id="recenter-btn",
                            style={"margin-bottom": "10px"}),
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
                style={'width': '100%', 'height': '100vh', 'background-color': '#ffffff'},
                zoom=1,
                pan={'x': 0, 'y': 0}
            ),
            width=9,
            style={"padding": "0"}  # Remove padding for full-width visualization
        )
    ], style={"margin": "0", "width": "100%", "height": "100vh", "overflow": "hidden"})
])


@app.callback(
    Output('cytoscape', 'elements'),
    Output('cytoscape', 'layout'),
    Output('cytoscape', 'stylesheet'),
    Output('cytoscape', 'style'),
    Input('label-filter', 'value'),
    Input('layout-selector', 'value'),
    Input('scale-width-toggle', 'value'),
    Input('edge-annotation-selector', 'value'),
    Input("edge-label-position", "value"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def update_elements(selected_labels, selected_layout, scale_toggle, annotation_field,
                    label_position, toggle):
    template = template_theme1 if toggle else template_theme2
    cy_style = {
        "width": "100%",
        "height": "100%",
        "background-color": "#ffffff" if toggle else "#1e1e1e",
    }

    scale_edges = "scale" in scale_toggle
    scale = 5 if scale_edges else 1
    nodes, edges = build_graph(scale_factor=scale)

    filtered_edges = [e for e in edges if e["data"]["label"] in selected_labels]
    elements = nodes + filtered_edges
    layout = {'name': selected_layout}

    edge_style = {
        "curve-style": "bezier",
        "control-point-step-size": 20,
        "target-arrow-shape": "triangle-backcurve",
        "color": "#fff" if not toggle else "#000",
        "text-outline-width": 0.2,
        "text-outline-color": "#000" if toggle else "#ccc",
    }

    # Control the edge label based on dropdown
    if annotation_field == "none":
        edge_style["label"] = ""
    else:
        edge_style["label"] = f"data({annotation_field})"

    # Width and arrow scaling
    if scale_edges:
        edge_style["width"] = "data(penwidth)"
        edge_style["arrow-scale"] = "data(penwidth)"
    else:
        edge_style["width"] = 2
        edge_style["arrow-scale"] = 1

    if label_position == "above":
        edge_style["text-margin-y"] = -10
    elif label_position == "below":
        edge_style["text-margin-y"] = 10
    elif label_position == "autorotate":
        edge_style["edge-text-rotation"] = "autorotate"
    else:
        edge_style["text-margin-y"] = 0
        edge_style["edge-text-rotation"] = "none"

    node_style = {
        "label": "data(label)",
        "text-valign": "center",
        "text-halign": "center",
        "text-outline-width": 1,
        "text-outline-color": "#888",
        "background-color": "#555",
        "color": "#fff",
        "font-size": 12,
    }

    stylesheet = [
        {"selector": "node", "style": node_style},
        {"selector": "edge", "style": edge_style},
    ]

    return elements, layout, stylesheet, cy_style


app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            const container = document.querySelector('[id="cytoscape"]');
            const cy = container && container._cyreg && container._cyreg.cy;
            if (cy) {
                cy.fit();
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('cytoscape', 'elements', allow_duplicate=True),
    Input('recenter-btn', 'n_clicks'),
    prevent_initial_call=True
)

if __name__ == '__main__':
    app.run(debug=True)
