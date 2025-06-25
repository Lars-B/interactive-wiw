import dash
import dash_cytoscape as cyto
from dash import Input, Output
from dash import html, dcc

dcc.Store(id="graph-store")


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


app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Store(id="graph-store"),  # <-- moved inside layout
    dcc.Checklist(
        id="darkmode-toggle",
        options=[{"label": "Dark mode", "value": "dark"}],
        value=[],  # or ["dark"] if you want it on by default
        inline=True,
        style={"margin-bottom": "10px"}
    ),

    dcc.Dropdown(
        id="label-filter",
        options=[{"label": "set1", "value": "set1"}, {"label": "set2", "value": "set2"}],
        value=["set1", "set2"],
        multi=True
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
        style={"width": "200px", "margin-bottom": "10px"}
    ),
    dcc.Checklist(  # <-- moved inside layout
        id="scale-width-toggle",
        options=[{"label": "Scale edge width by weight", "value": "scale"}],
        value=["scale"],  # checked by default
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
        style={"width": "250px", "margin-bottom": "10px"},
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
        style={"width": "250px", "margin-bottom": "10px"},
    ),
    html.Button("Recenter Graph", id="recenter-btn", style={"margin-bottom": "10px"}),
    cyto.Cytoscape(
        id='cytoscape',
        elements=build_graph()[0] + build_graph()[1],
        layout={'name': 'cose'},
        # style={'width': '100%', 'height': '100%'},
        style={'width': '100%', 'height': '100%', 'background-color': '#ffffff'},
        zoom=1,
        pan={'x': 0, 'y': 0}
    )
], style={'height': '100vh', 'display': 'flex', 'flexDirection': 'column'})


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
    Input('darkmode-toggle', 'value')
)
def update_elements(selected_labels, selected_layout, scale_toggle, annotation_field,
                    label_position, darkmode_toggle):
    is_dark = "dark" in darkmode_toggle
    cy_style = {
        "width": "100%",
        "height": "100%",
        "background-color": "#1e1e1e" if is_dark else "#ffffff",
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
        "color": "#fff" if is_dark else "#000",
        "text-outline-width": 0.2,
        "text-outline-color": "#000" if not is_dark else "#ccc",
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
    # todo works but scaling of view window off, parallel edges not properly shown
    # todo lots of work to be done for testing if this will be useful...
    app.run(debug=True)
