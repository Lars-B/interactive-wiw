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
        mst = None
        try:
            mst = maximum_spanning_arborescence(net, attr="posterior", preserve_attrs=True)
        except NetworkXException:
            logger.info("Maximum spanning arborescence failed and will be ignored...")

        if mst:
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
                        "id": f'MST-{edge_count}'
                    }
                })
                edge_count += 1

            edges.extend(mst_edges)

    return nodes, edges, num_trees


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


def get_node_style(annotation_field, font_size, color_by_label) -> dict:
    return {
        "label": f"data({annotation_field})",
        "text-valign": "center",
        "text-halign": "center",
        "text-outline-width": 1,
        "text-outline-color": "#888",
        "backgroundColor": "data(color)" if color_by_label else "#555",
        "shape": "data(shape)",
        "color": "#fff",
        "font-size": font_size,
    }


def get_edge_style(annotation_field, label_position, scale_edges,
                   color_by_label, is_light_theme, font_size, toggle_arrows) -> dict:
    edge_style = {
        "curve-style": "bezier",
        "control-point-step-size": 20,
        "color": "#000" if is_light_theme else "#fff",
        "text-outline-width": 0.2,
        "text-outline-color": "#000" if is_light_theme else "#ccc",
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
        edge_style["width"] = 2

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
    fieldname_map = dict(zip(normalized_fieldnames, reader.fieldnames))
    taxon_column_normalized = _normalize_column_name(taxon_column)

    if taxon_column_normalized not in fieldname_map:
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
        taxon = row.get(fieldname_map.get(taxon_column))
        if not taxon:
            continue

        uploaded_map[taxon] = {
            col: (row[fieldname_map.get(col)] if row[fieldname_map.get(col)] is not None else "")
            for col in annotation_columns
        }

    return uploaded_map


def build_graph_from_rds(file_content, label):
    logger.debug("custom_csv file parsing and graph construction...")
    new_nodes, new_edges = handle_uploaded_rds_file(file_content, label)
    return new_nodes, new_edges


def handle_uploaded_rds_file(base64_content, label):
    logger.debug("Parsing uploaded RDS file...")

    # todo should be at top and new requirement
    import pyreadr

    # remove header if present
    if "," in base64_content:
        base64_content = base64_content.split(",")[1]

    file_bytes = base64.b64decode(base64_content)

    with tempfile.NamedTemporaryFile(suffix=".rds", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        result = pyreadr.read_r(tmp_path)

        obj = next(iter(result.values()))

        logger.debug(f"Loaded R object type: {type(obj)}")

        return build_graph_from_datframe(obj, label)

    finally:
        os.remove(tmp_path)


def build_graph_from_datframe(res, label):
    alpha_prefix = "alpha"  # outbreaker specific...

    alpha_cols = [c for c in res.columns if c.startswith(alpha_prefix)]

    alpha_mat = res[alpha_cols]

    n_states = len(alpha_cols)
    n_samples = len(alpha_mat)

    # todo should be at top and new requirement
    from collections import Counter

    # -------------------------
    # edges
    # -------------------------
    edge_counter = Counter()

    for state_idx, col in enumerate(alpha_cols, start=1):
        for source in alpha_mat[col]:
            if pd.isna(source):
                continue

            source = int(source)
            target = state_idx

            edge_counter[(source, target)] += 1

    edges = []
    node_strength = Counter()

    for edge_id, ((source, target), count) in enumerate(edge_counter.items()):
        weight = count / n_samples

        edges.append({
            "data": {
                "source": str(source),
                "target": str(target),
                "label": label,
                "posterior": round(weight, 2),  # todo think about making this an input value?
                "weight": round(weight, 2),
                "color": "black",
                "id": f"{label}-{edge_id}",
            }
        })

        node_strength[source] += weight

    # -------------------------
    # nodes
    # -------------------------
    nodes = []

    for node_id in range(1, n_states + 1):
        nodes.append({
            "data": {
                "id": str(node_id),
                "label": str(node_id),
                "strength": round(node_strength[node_id], 4),
            }
        })

    return nodes, edges
