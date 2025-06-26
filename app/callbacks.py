from dash_bootstrap_templates import ThemeSwitchAIO
from dash import Output, Input

from .app import app as myapp
from .graph_elements import build_graph, get_node_style, get_cytoscape_style, get_edge_style


@myapp.callback(
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
                    label_position, is_light_theme):
    cy_style = get_cytoscape_style(is_light_theme)
    scale_edges = "scale" in scale_toggle
    scale = 5 if scale_edges else 1

    nodes, edges = build_graph(scale_factor=scale)
    filtered_edges = [e for e in edges if e["data"]["label"] in selected_labels]
    elements = nodes + filtered_edges
    layout = {"name": selected_layout}

    stylesheet = [
        {"selector": "node",
         "style": get_node_style()},
        {"selector": "edge", "style": get_edge_style(annotation_field,
                                                     label_position,
                                                     scale_edges,
                                                     is_light_theme)},
    ]

    # print("--- DEBUG ---")
    # print("Elements (first 2):", elements[:2])  # Show first two elements
    # print("Layout:", layout)
    # print("Stylesheet:", stylesheet)
    # print("Style:", cy_style)
    # print("------------------")

    return elements, layout, stylesheet, cy_style


myapp.clientside_callback(
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

