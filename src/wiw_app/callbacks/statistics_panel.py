from dash import Output, Input, State, html

from wiw_app.app import app as myapp
from wiw_app.dash_logger import logger
from wiw_app.ids import GraphStatistics


@myapp.callback(
    Output(GraphStatistics.PANEL, "is_open"),
    Input(GraphStatistics.SHOW_STATS_PANEL_BUTTON, "n_clicks"),
    State(GraphStatistics.PANEL, "is_open"),
)
def toggle_statistics_panel(n_clicks, is_open):
    if n_clicks:
        return not is_open

    return is_open


@myapp.callback(
    Output(GraphStatistics.PANEL_CONTENT, "children"),
    Input("cytoscape", "elements"),
)
def update_statistics(elements):
    nodes = [
        e for e in elements
        if "source" not in e["data"]
    ]

    edges = [
        e for e in elements
        if "source" in e["data"]
    ]

    # todo this is where we need to compute the relevant stats for all nodes/edges and metadata...
    logger.debug(f"This is where we need to compute stuff...")

    n_nodes = len(nodes)
    n_edges = len(edges)

    return [
        html.P(f"Nodes: {n_nodes}"),
        html.P(f"Edges: {n_edges}")
    ]
