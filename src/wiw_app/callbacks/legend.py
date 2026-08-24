import urllib.parse

from dash import Input, Output, State, callback, ctx

from wiw_app.dash_logger import logger
from wiw_app.ids import GraphOptions
from wiw_app.plotting_utils import draw_legend

# Stylesheet fixed for the legend that can be added now
LEGEND_NODE_ID = "__legend__"
legend_styles = [
    {
        "selector": f"#{LEGEND_NODE_ID}",
        "style": {
            "shape": "rectangle",
            "width": "150px",
            "height": "150px",
            "background-image": "data(legend)",
            # Cytoscape picks up legend SVG from node data
            "background-fit": "contain",
            "background-repeat": "no-repeat",
            "border-width": 1,
            "border-color": "#999",
        }
    }
]


@callback(
    Output("cytoscape", "elements", allow_duplicate=True),
    Output("cytoscape", "stylesheet", allow_duplicate=True),
    Input(GraphOptions.Legend.ADD_LEG_NODE, "n_clicks"),
    Input(GraphOptions.Legend.REMOVE_LEG_NODE, "n_clicks"),
    Input(GraphOptions.Nodes.SIZE_SELECTOR, "value"),
    State("cytoscape", "elements"),
    State("cytoscape", "stylesheet"),
    State(GraphOptions.Nodes.COLOR_PICKER_CONTAINERS, "children"),
    State(GraphOptions.Nodes.COLOR_BY_LABEL, "value"),
    State(GraphOptions.Nodes.COLOR_LABEL_SELECTOR, "value"),
    State(GraphOptions.Nodes.COLOR_LABEL_SELECTOR, "options"),
    State(GraphOptions.Edges.COLOR_PICKER_CONTAINERS, "children"),
    State(GraphOptions.Edges.COLOR_BY_LABEL, "value"),
    prevent_initial_call=True,
)
def toggle_legend(
        add_clicks,
        remove_clicks,
        node_size,
        elements, stylesheet,
        node_color_container, node_color_toggle, node_color_title,
        node_color_options,
        edge_color_container, edge_color_toggle
):
    if not elements and not stylesheet:
        logger.debug(f"No elements in the graph yet, returning nothing")
        return elements or [], stylesheet or []

    if ctx.triggered_id == GraphOptions.Legend.REMOVE_LEG_NODE:
        logger.debug(f"Removing legend node.")
        return [el for el in elements if el["data"]["id"] != LEGEND_NODE_ID], stylesheet

    # Add legend
    if ctx.triggered_id == GraphOptions.Legend.ADD_LEG_NODE:
        if any(el["data"]["id"] == LEGEND_NODE_ID for el in elements):
            logger.debug(f"Legend node already exists, doing nothing.")
            return elements, stylesheet

        legend_svg = draw_legend(
            node_color_options,
            node_color_title,
            node_color_toggle,
            node_color_container,
            edge_color_toggle,
            edge_color_container,
            svg=True
        )

        encoded_svg = urllib.parse.quote(legend_svg)
        legend_node_size = node_size * 4

        legend_node = {
            "data": {
                "id": LEGEND_NODE_ID,
                "legend": f"data:image/svg+xml;utf8,{encoded_svg}",
            },
            "position": {"x": 1000, "y": 100},
            "grabbable": True,
            "style": {
                "width": legend_node_size,
                "height": legend_node_size,
            }
        }
        logger.debug(f"Adding legend node to graph.")
        return elements + [legend_node], stylesheet + legend_styles
    return elements, stylesheet
