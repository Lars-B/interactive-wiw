import base64
import csv
import io
import os
import tempfile
from collections import defaultdict
from io import StringIO

import networkx as nx
import pandas as pd
from brokilon.ccd.domain.transmission import read_breath_nexus
from brokilon.ccd.domain.transmission.find_infectors import find_infector
from networkx.algorithms.tree.branchings import maximum_spanning_arborescence
from networkx.exception import NetworkXException

from wiw_app.config import EdgeConfig, NodeConfig
from wiw_app.dash_logger import logger
from wiw_app.utils import log_time


def decode_base64_content(base64_content: str) -> bytes:
    content_type, content_string = base64_content.split(",", 1)
    decoded_content = base64.b64decode(content_string)
    return decoded_content


def handle_uploaded_nexus_file(base64_content, burn_in):
    tmp = tempfile.NamedTemporaryFile(mode='wb', suffix=".nex", delete=False)
    try:
        _, content = base64_content.split(",", 1)

        chunk_size = 1024 * 1024
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            tmp.write(base64.b64decode(chunk))
        tmp.flush()
        tmp.close()

        trees, taxon_map = read_breath_nexus(
            tmp.name,
            parse_taxon_map=True,
            burn_in=burn_in
        )

    finally:
        os.remove(tmp.name)
    return trees, taxon_map


def build_graph_from_custom_csv_file(file_content, label):
    logger.debug("custom_csv file parsing and graph construction...")
    new_nodes, new_edges = handle_uploaded_custom_csv_file(file_content, label)
    return new_nodes, new_edges


def handle_uploaded_custom_csv_file(base64_content, label):
    _, content = base64_content.split(",", 1)

    decoded = base64.b64decode(content).decode("utf-8")

    df = pd.read_csv(
        StringIO(decoded),
        dtype={
            "id": str,
            "from": str,
            "to": str,
            "type": str
        }
    )

    nodes, edges = parse_custom_csv_dataframe(df, label)

    return nodes, edges


def parse_custom_csv_dataframe(df, label):
    node_df = df[df["type"] == "node"]
    edge_df = df[df["type"] == "edge"]

    nodes = []
    for _, row in node_df.iterrows():
        nodes.append({
            "data": {
                "id": str(row["id"]),
                "label": str(row["id"]),
                "strength": row["strength"]
            }
        })

    edges = []
    for _, row in edge_df.iterrows():
        edges.append({
            "data": {
                "source": str(row["from"]),
                "target": str(row["to"]),
                "label": label,
                "posterior": row["weight"],
                "weight": round(row["weight"], 2),
                "penwidth": 1,
                "color": "black"
            }
        })
    # todo could add mst here too, not supported for now...

    return nodes, edges


class NoTreesFoundError(Exception):
    pass


def build_graph_from_breath_tree_file(file_content, label, burn_in):
    logger.info("Processing file content and building WIW network...")

    with log_time("Handling and reading uploaded nexus file"):
        trees, taxon_map = handle_uploaded_nexus_file(file_content, burn_in)

    logger.info(f"Found {len(trees)} trees")
    logger.info(f"Extracted taxon map of size: {len(taxon_map)}")

    num_trees = len(trees)

    if num_trees == 0:
        raise NoTreesFoundError("No trees were found after burn-in!")

    logger.info(f"After burn-in there are {num_trees} trees")

    logger.info("Processing trees...")

    posterior_wiw_edges = defaultdict(lambda: defaultdict(int))
    posterior_wiw_edges_indirect = defaultdict(lambda: defaultdict(int))

    with log_time("Processing trees"):
        for tree in trees:
            for leaf in tree.get_leaves():
                leaf_name = leaf.name

                infector = find_infector(leaf)
                posterior_wiw_edges[leaf_name][infector] += 1

                if not infector.startswith("Unknown"):
                    continue

                indirect_infector = find_infector(leaf, indirect=True)
                posterior_wiw_edges_indirect[leaf_name][indirect_infector] += 1

    logger.info("Trees processed, now building the WIW network to add...")

    nodes = []
    for leaf in trees[0].get_leaves():
        nodes.append({"data": {
            "id": leaf.name,
            "label": leaf.name,
            "taxon": taxon_map[int(leaf.name)]
        }})

    edges = []
    edge_count = 1

    net = nx.DiGraph()

    edge_count = add_posterior_edges(
        posterior_wiw_edges,
        edges,
        label=label,
        num_trees=num_trees,
        edge_count=edge_count,
        net=net,
    )

    edge_count = add_posterior_edges(
        posterior_wiw_edges_indirect,
        edges,
        label=f"Indirect-{label}",
        num_trees=num_trees,
        edge_count=edge_count,
    )

    logger.info(f"Added {edge_count} edges to network...")

    if num_trees > 1 and net.number_of_nodes() > 1:
        mst_edges = generate_mst_edges_from_network(net, label)
        edges.extend(mst_edges)

    return nodes, edges, num_trees


def generate_mst_edges_from_network(network, label):
    try:
        mst = maximum_spanning_arborescence(network, attr="posterior",
                                            preserve_attrs=True)
    except NetworkXException:
        logger.info(
            "Maximum spanning arborescence failed and will be ignored...")
        return []

    if mst is None:
        logger.debug(
            "Maximum spanning tree didn't fail but returned None, will be ignored...")
        return []

    mst_edges = []
    edge_count = 1
    for u, v, data in mst.edges(data=True):
        mst_edges.append({
            "data": {
                "source": u,
                "target": v,
                "label": f"MST-{label}",
                "posterior": round(data["posterior"], 2),
                "weight": data["weight"],
                "penwidth": 1,
                "color": "black",
                "id": f'MST-{label}-{edge_count}'
            }
        })
        edge_count += 1
    return mst_edges


def add_posterior_edges(
        edges_dict,
        edges,
        label,
        num_trees,
        edge_count,
        *,
        net=None,
):
    for target in edges_dict:
        for source in edges_dict[target]:

            if source.startswith("Unknown"):
                continue

            if source == target:
                continue

            posterior_support = round(
                edges_dict[target][source] / num_trees,
                2
            )

            if posterior_support == 0.00:
                continue

            weight = round(posterior_support, 2)

            edge_data = {
                "source": source,
                "target": target,
                "label": label,
                "posterior": posterior_support,
                "weight": weight,
                "penwidth": 1,
                "color": "black",
                "id": f"{label}-{edge_count}"
            }

            edges.append({"data": edge_data})

            if net is not None:
                net.add_edge(
                    source,
                    target,
                    weight=weight,
                    posterior=posterior_support
                )
            edge_count += 1
    return edge_count


def get_cytoscape_style(is_light_theme: bool) -> dict:
    return {
        "width": "100%",
        "height": "100%",
        "backgroundColor": "#ffffff" if is_light_theme else "#1e1e1e",
    }


def get_node_style(annotation_field, font_size, color_by_label,
                   node_size, is_light_theme) -> dict:
    return {
        "label": f"data({annotation_field})",
        "text-valign": "center",
        "text-halign": "center",
        "text-outline-width": NodeConfig.LABEL_OUTLINE_WIDTH,
        "text-outline-color":
            NodeConfig.LightMode.LABEL_OUTLINE_COLOR if is_light_theme
            else NodeConfig.DarkMode.LABEL_OUTLINE_COLOR,
        "backgroundColor":
            "data(color)" if color_by_label else
            (NodeConfig.LightMode.DEFAULT_NODE_COLOR if is_light_theme
             else NodeConfig.DarkMode.DEFAULT_NODE_COLOR),
        "shape": "data(shape)",
        "color":
            NodeConfig.LightMode.LABEL_COLOR if is_light_theme
            else NodeConfig.DarkMode.LABEL_COLOR,
        "font-size": font_size,
        "width": node_size,
        "height": node_size,
    }


def apply_node_styles(
        nodes,
        node_shape_mode,
        node_color_label_selection,
        node_label_colors,
        terminal_nodes,
        seen_nodes,
):
    for node in nodes:
        label = node["data"][node_color_label_selection]

        node["data"]["color"] = node_label_colors.get(label, "green")

        node["data"]["shape"] = resolve_node_shape(
            node=node,
            mode=node_shape_mode,
            terminal_nodes=terminal_nodes,
            seen_nodes=seen_nodes,
        )


def resolve_node_shape(node, mode, terminal_nodes, seen_nodes):
    node_id = node["data"]["id"]

    # special case: adaptive logic
    if mode == "adaptive":
        if node_id in terminal_nodes:
            return "rectangle"
        if node_id not in seen_nodes:
            return "triangle"
        return "ellipse"

    # direct mapping for everything else
    try:
        return mode
    except KeyError:
        raise NotImplementedError(f"Unknown node shape mode: {mode}")


def get_edge_style(annotation_field, label_position, scale_edges,
                   color_by_label, is_light_theme, font_size,
                   toggle_arrows, edge_curve_style) -> dict:
    edge_style = {
        "curve-style": edge_curve_style,
        "control-point-step-size": 20,
        "color":
            EdgeConfig.LightMode.LABEL_COLOR if is_light_theme
            else EdgeConfig.DarkMode.LABEL_COLOR,
        "text-outline-width": 0.2,
        "text-outline-color":
            EdgeConfig.LightMode.LABEL_OUTLINE_COLOR if is_light_theme
            else EdgeConfig.DarkMode.LABEL_OUTLINE_COLOR,
        "label": f"data({annotation_field})",
        "font-size": font_size,
    }

    arrows_enabled = not toggle_arrows

    # Arrow styling
    if arrows_enabled:
        edge_style["target-arrow-shape"] = "triangle-backcurve"

    # Edge width / arrow scaling
    if scale_edges:
        edge_style["width"] = "data(weight)"

        if arrows_enabled:
            edge_style["arrow-scale"] = (
                "mapData(data(weight), 0, 1, 0.5, 2)"
            )
    else:
        edge_style["width"] = EdgeConfig.NO_SCALE_DEFAULT

        if arrows_enabled:
            edge_style["arrow-scale"] = 1

    # Label positioning
    position_styles = {
        "above": {"text-margin-y": -10},
        "below": {"text-margin-y": 10},
        "autorotate": {"edge-text-rotation": "autorotate"},
    }

    edge_style.update(
        position_styles.get(
            label_position,
            {
                "text-margin-y": 0,
                "edge-text-rotation": "none",
            },
        )
    )

    # Edge coloring
    if color_by_label:
        edge_style["line-color"] = "data(color)"

        if arrows_enabled:
            edge_style["target-arrow-color"] = "data(color)"

    return edge_style


def _normalize_column_name(name: str) -> str:
    """Lowercase + strip whitespace + remove surrounding quotes."""
    return name.strip().strip('"').strip("'").lower()


def process_node_annotations_file(file_content, taxon_column):
    logger.info(f"Processing file content for node annotations...")
    decoded_content = decode_base64_content(file_content).decode("UTF8")

    logger.debug(f"Uploaded metadata with column name {taxon_column}...")

    def detect_delimiter(text: str):
        sample = text[:4096]

        try:
            dialect = csv.Sniffer().sniff(
                sample,
                delimiters=(",", "\t", ";", "|"),
            )
            return dialect.delimiter
        except csv.Error:
            pass

        # fallback in case the above fails
        first_lines = sample.splitlines()[:10]

        counts = {
            ",": sum(line.count(",") for line in first_lines),
            "\t": sum(line.count("\t") for line in first_lines),
            ";": sum(line.count(";") for line in first_lines),
            "|": sum(line.count("|") for line in first_lines),
        }

        return max(counts, key=counts.get)

    delimiter = detect_delimiter(decoded_content)

    logger.debug(f"Detected delimiter '{delimiter}'")

    reader = csv.DictReader(io.StringIO(decoded_content), delimiter=delimiter)

    if not reader.fieldnames:
        raise ValueError("No header found in annotation file.")

        # Normalize header names
    normalized_fieldnames = [
        _normalize_column_name(col) for col in reader.fieldnames
    ]
    fieldnames_map = dict(zip(normalized_fieldnames, reader.fieldnames))
    taxon_column_normalized = _normalize_column_name(taxon_column)

    if taxon_column_normalized not in fieldnames_map:
        # todo make this an info toast popup...
        raise ValueError(
            f"Taxon column '{taxon_column}' not found.\n"
            f"Available columns: {normalized_fieldnames}"
        )

    annotation_columns = [
        col for col in normalized_fieldnames
        if col != taxon_column_normalized
    ]

    if not annotation_columns:
        raise ValueError("No annotation columns found in file.")

    uploaded_map = {}

    for row in reader:
        taxon = row.get(fieldnames_map.get(taxon_column))
        if not taxon:
            continue

        uploaded_map[taxon] = {
            col: (row[fieldnames_map.get(col)] if row[fieldnames_map.get(
                col)] is not None else "")
            for col in annotation_columns
        }

    return uploaded_map
