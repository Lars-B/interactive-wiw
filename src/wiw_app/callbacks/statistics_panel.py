from dash import Output, Input, State
from dash import html

from wiw_app.app import app as myapp
from wiw_app.graph_statistics import build_graph, calculate_graph_statistics, \
    calculate_metadata_statistics, graph_statistics_component, metadata_statistics_components
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
    Input(GraphStatistics.PANEL, "is_open"),
    State("cytoscape", "elements"),
)
def update_statistics(is_open, elements):
    if not is_open:
        return []

    graph = build_graph(elements)

    graph_stats = calculate_graph_statistics(graph)
    metadata_stats = calculate_metadata_statistics(graph)

    return [
        html.H3("Graph Statistics"),
        graph_statistics_component(graph_stats),

        html.Br(),
        html.Hr(),
        html.H3("Metadata"),
        *metadata_statistics_components(metadata_stats),
    ]
