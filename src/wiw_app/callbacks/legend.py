import re
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
    State(GraphOptions.Nodes.SHAPE_SELECTOR, "value"),
    State(GraphOptions.Edges.COLOR_PICKER_CONTAINERS, "children"),
    State(GraphOptions.Edges.COLOR_BY_LABEL, "value"),
    State(GraphOptions.Edges.DISPLAY_FILTER, "value"),
    prevent_initial_call=True,
)
def toggle_legend(
        add_clicks,
        remove_clicks,
        node_size,
        elements, stylesheet,
        node_color_container, node_color_toggle, node_color_title,
        node_color_options, node_shape_selector,
        edge_color_container, edge_color_toggle, edge_display_filter
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
            node_shape_selector,
            edge_color_toggle,
            edge_color_container,
            edge_display_filter,
            svg=True
        )

        if not legend_svg:
            # Legend would be empty, do nothing else
            logger.info(f"Legend node was found to be empty.")
            return elements, stylesheet

        encoded_svg = urllib.parse.quote(legend_svg)
        width = int(re.search(r'width="(\d+)"', legend_svg).group(1))
        height = int(re.search(r'height="(\d+)"', legend_svg).group(1))

        legend_node = {
            "data": {
                "id": LEGEND_NODE_ID,
                "legend": f"data:image/svg+xml;utf8,{encoded_svg}",
            },
            "position": {"x": 1000, "y": 100},
            "grabbable": True,
            "style": {
                "width": width,
                "height": height,
            }
        }
        logger.debug(f"Adding legend node to graph.")
        return elements + [legend_node], stylesheet + legend_styles
    return elements, stylesheet
