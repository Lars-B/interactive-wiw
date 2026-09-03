from collections import Counter

import networkx as nx
import numpy as np
from dash import dash_table, html

from wiw_app.config import StatsPanelConfig


def build_graph(elements):
    """Build a directed NetworkX graph from Cytoscape elements."""

    graph = nx.DiGraph()

    for element in elements:
        data = element["data"]

        if "source" in data:
            graph.add_edge(
                data["source"],
                data["target"],
                **data,
            )
        else:
            graph.add_node(
                data["id"],
                **data,
            )

    return graph


def calculate_graph_statistics(graph):
    """Calculate statistics for a directed graph."""

    n_nodes = graph.number_of_nodes()
    n_edges = graph.number_of_edges()

    # ------------------------------------------------------------------
    # Basic statistics
    # ------------------------------------------------------------------

    density = nx.density(graph)

    components = list(
        nx.weakly_connected_components(graph)
    )

    n_components = len(components)

    component_sizes = [
        len(component)
        for component in components
    ]

    # ------------------------------------------------------------------
    # Degree statistics
    # ------------------------------------------------------------------

    in_degrees = dict(graph.in_degree())
    out_degrees = dict(graph.out_degree())

    in_degree_values = list(in_degrees.values())
    out_degree_values = list(out_degrees.values())

    mean_in_degree = (
        np.mean(in_degree_values)
        if in_degree_values
        else 0
    )

    mean_out_degree = (
        np.mean(out_degree_values)
        if out_degree_values
        else 0
    )

    max_in_degree = max(
        in_degree_values,
        default=0,
    )

    max_out_degree = max(
        out_degree_values,
        default=0,
    )

    # ------------------------------------------------------------------
    # Special node types
    # ------------------------------------------------------------------

    source_nodes = [
        node
        for node, degree in in_degrees.items()
        if degree == 0
    ]

    terminal_nodes = [
        node
        for node, degree in out_degrees.items()
        if degree == 0
    ]

    isolated_nodes = [
        node
        for node in graph.nodes
        if graph.in_degree(node) == 0
        and graph.out_degree(node) == 0
    ]

    # ------------------------------------------------------------------
    # Hubs
    # ------------------------------------------------------------------

    max_out_nodes = [
        node
        for node, degree in out_degrees.items()
        if degree == max_out_degree
    ]

    max_in_nodes = [
        node
        for node, degree in in_degrees.items()
        if degree == max_in_degree
    ]

    # ------------------------------------------------------------------
    # Path statistics
    # ------------------------------------------------------------------

    component_lengths = []

    for component in components:

        subgraph = graph.subgraph(component)

        if len(subgraph) <= 1:
            continue

        undirected = subgraph.to_undirected()

        try:
            component_lengths.append(
                nx.average_shortest_path_length(
                    undirected
                )
            )
        except nx.NetworkXError:
            pass

    mean_path_length = (
        np.mean(component_lengths)
        if component_lengths
        else 0
    )

    # ------------------------------------------------------------------
    # Cycles
    # ------------------------------------------------------------------

    cycles = list(nx.simple_cycles(graph))

    # ------------------------------------------------------------------
    # Return
    # ------------------------------------------------------------------

    return {
        "n_nodes": n_nodes,
        "n_edges": n_edges,
        "density": density,
        "n_components": n_components,
        "component_sizes": component_sizes,

        "in_degrees": in_degrees,
        "out_degrees": out_degrees,

        "mean_in_degree": mean_in_degree,
        "mean_out_degree": mean_out_degree,
        "max_in_degree": max_in_degree,
        "max_out_degree": max_out_degree,

        "source_nodes": source_nodes,
        "terminal_nodes": terminal_nodes,
        "isolated_nodes": isolated_nodes,

        "max_out_nodes": max_out_nodes,
        "max_in_nodes": max_in_nodes,

        "mean_path_length": mean_path_length,

        "cycles": cycles,
    }

# ---------------------------
# Helper function here for now:
# ---------------------------

def graph_statistics_component(stats):
    """Create the graph statistics table."""

    data = [
        {
            "statistic": "Nodes",
            "value": stats["n_nodes"],
        },
        {
            "statistic": "Edges",
            "value": stats["n_edges"],
        },
        {
            "statistic": "Density",
            "value": f"{stats['density']:.4f}",
        },
        {
            "statistic": "Components",
            "value": stats["n_components"],
        },
        {
            "statistic": "Mean in-degree",
            "value": f"{stats['mean_in_degree']:.2f}",
        },
        {
            "statistic": "Mean out-degree",
            "value": f"{stats['mean_out_degree']:.2f}",
        },
        {
            "statistic": "Max in-degree",
            "value": stats["max_in_degree"],
        },
        {
            "statistic": "Max out-degree",
            "value": stats["max_out_degree"],
        },
        {
            "statistic": "Source nodes",
            "value": len(stats["source_nodes"]),
        },
        {
            "statistic": "Terminal nodes",
            "value": len(stats["terminal_nodes"]),
        },
        {
            "statistic": "Isolated nodes",
            "value": len(stats["isolated_nodes"]),
        },
        {
            "statistic": "Cycles",
            "value": len(stats["cycles"]),
        },
        {
            "statistic": "Mean path length",
            "value": f"{stats['mean_path_length']:.2f}",
        },
    ]

    return dash_table.DataTable(
        data=data,
        columns=[
            {
                "name": "Statistic",
                "id": "statistic",
            },
            {
                "name": "Value",
                "id": "value",
            },
        ],
        style_cell={
            "textAlign": "left",
            "padding": "5px",
        },
        style_header={
            "fontWeight": "bold",
        },
    )

def calculate_metadata_statistics(graph):
    metadata = {}

    for node, data in graph.nodes(data=True):

        for key, value in data.items():
            if key in ("id", "taxon", "color", "shape"):
                continue

            metadata.setdefault(key, []).append(value)

    metadata_summary = {}

    for key, values in metadata.items():

        # Remove missing values
        values = [
            value for value in values
            if value is not None
        ]

        categories = Counter(values)

        metadata_summary[key] = {
            "n_values": len(categories),
            "values": set(categories),
            "frequencies": dict(categories),
        }

        # Only calculate connectivity for annotations
        # with a small number of unique values
        if StatsPanelConfig.MIN_CATEGORIES <= len(categories) <= StatsPanelConfig.MAX_CATEGORIES:

            connectivity = Counter()

            for source, target in graph.edges:

                source_value = graph.nodes[source].get(key)
                target_value = graph.nodes[target].get(key)

                # Ignore edges where either node is missing
                # this annotation
                if source_value is None or target_value is None:
                    continue

                connectivity[(source_value, target_value)] += 1

            metadata_summary[key]["connectivity"] = dict(connectivity)

    return metadata_summary


def metadata_statistics_components(metadata_summary):
    """Create Dash components for the metadata statistics."""

    components = []

    for key, info in metadata_summary.items():

        # We only have connectivity statistics for these
        # annotations, so don't display the others for now.
        if "connectivity" not in info:
            continue

        categories = sorted(info["values"], key=str)

        # Separator between annotations
        if components:
            components.append(html.Br())
            components.append(html.Hr())

        components.append(
            html.H4(key.capitalize())
        )

        # ----------------------------------------------------------
        # Frequencies
        # ----------------------------------------------------------

        frequency_data = [
            {
                "category": str(category),
                "count": info["frequencies"][category],
            }
            for category in categories
        ]

        components.append(
            dash_table.DataTable(
                data=frequency_data,
                columns=[
                    {
                        "name": "Category",
                        "id": "category",
                    },
                    {
                        "name": "Count",
                        "id": "count",
                    },
                ],
                style_cell={
                    "textAlign": "left",
                    "padding": "4px",
                },
                style_header={
                    "fontWeight": "bold",
                },
                style_table={
                    "marginBottom": "15px",
                },
            )
        )

        # ----------------------------------------------------------
        # Connectivity
        # ----------------------------------------------------------

        connectivity = info["connectivity"]

        connectivity_data = []

        for source in categories:

            row = {
                "source": str(source),
            }

            for target in categories:
                row[str(target)] = connectivity.get(
                    (source, target),
                    0,
                )

            connectivity_data.append(row)

        components.append(
            html.P("Connectivity")
        )

        components.append(
            dash_table.DataTable(
                data=connectivity_data,
                columns=[
                    {
                        "name": "Source",
                        "id": "source",
                    },
                    *[
                        {
                            "name": str(category),
                            "id": str(category),
                        }
                        for category in categories
                    ],
                ],
                style_cell={
                    "textAlign": "center",
                    "padding": "4px",
                },
                style_header={
                    "fontWeight": "bold",
                },
                style_table={
                    "overflowX": "auto",
                    "marginBottom": "20px",
                },
            )
        )

    return components
