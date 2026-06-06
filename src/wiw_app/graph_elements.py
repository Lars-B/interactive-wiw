import base64
import csv
import io
import os
import tempfile
from collections import defaultdict, Counter
from io import StringIO

import networkx as nx
import numpy as np
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
        mst_edges = generate_mst_edges_from_network(net, label)
        edges.extend(mst_edges)

    return nodes, edges, num_trees


def generate_mst_edges_from_network(network, label):
    try:
        mst = maximum_spanning_arborescence(network, attr="posterior", preserve_attrs=True)
    except NetworkXException:
        logger.info("Maximum spanning arborescence failed and will be ignored...")
        return []

    if mst is None:
        logger.debug("Maximum spanning tree didn't fail but returned None, will be ignored...")
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
                "id": f'MST-{edge_count}'
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
            col: (row[fieldnames_map.get(col)] if row[fieldnames_map.get(col)] is not None else "")
            for col in annotation_columns
        }

    return uploaded_map


def build_graph_from_outbreaker_rds(file_content, label):
    obj = load_rds_object(file_content)
    new_nodes, new_edges = build_graph_from_outbreaker_datframe(obj, label)
    return new_nodes, new_edges


def load_rds_object(base64_content):
    import pyreadr

    if "," in base64_content:
        base64_content = base64_content.split(",", 1)[1]

    file_bytes = base64.b64decode(base64_content)

    with tempfile.NamedTemporaryFile(suffix=".rds", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        result = pyreadr.read_r(tmp_path)

        if not result:
            raise ValueError("No objects found in RDS file")

        return next(iter(result.values()))

    finally:
        os.remove(tmp_path)


def build_graph_from_outbreaker_datframe(res, label):
    alpha_prefix = "alpha"  # outbreaker2 specific...

    alpha_cols = [c for c in res.columns if c.startswith(alpha_prefix)]

    alpha_mat = res[alpha_cols]

    n_states = len(alpha_cols)
    n_samples = len(alpha_mat)

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
    net = nx.DiGraph()

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

        net.add_edge(
            str(source),
            str(target),
            weight=round(weight, 2),
            posterior=round(weight, 2)
        )
        node_strength[source] += weight

    # Construct MST if possible:
    if net.number_of_nodes() > 1:
        mst_edges = generate_mst_edges_from_network(net, label)
        edges.extend(mst_edges)

    # -------------------------
    # nodes
    # -------------------------
    nodes = []

    for node_id in range(1, n_states + 1):
        nodes.append({
            "data": {
                "id": str(node_id),
                "label": str(node_id),
            }
        })

    return nodes, edges


def load_rds_object2(base64_content):
    # todo this should be an alternative version to the load_rds_object function...

    # import pyreadr
    import rdata

    if "," in base64_content:
        base64_content = base64_content.split(",", 1)[1]

    file_bytes = base64.b64decode(base64_content)

    with tempfile.NamedTemporaryFile(suffix=".rds", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        # result = pyreadr.read_r(tmp_path)
        logger.info("Parsing the rdata")
        parsed = rdata.parser.parse_file(tmp_path)
        logger.info("Successfully parsed the rdata.")

        logger.info("Converting the Rdata to a python object")
        # Convert the parsed data into native Python objects
        converted = rdata.conversion.convert(parsed)
        logger.info("Successfully converted the Rdata to a python object.")

        if not converted:
            raise ValueError("No objects found in RDS file")

        return converted

    finally:
        os.remove(tmp_path)


def build_graph_from_transphylo_rds(file_content, label, burnin, input_type):
    logger.info(f"We are using this input_type: {input_type}")

    match input_type:
        case "mcmc":
            obj = load_rds_object2(file_content)
            logger.info(f"Loaded R object type: {type(obj)}")

            wiw_matrix, num_samples = compute_mat_wiw_transphylo_mcmc_rds(obj, burnin=burnin)

            names = obj[0]["ctree"]["nam"]
            wiw_matrix = pd.DataFrame(
                wiw_matrix,
                index=names,
                columns=names,
            )

        case "wiw_matrix":
            wiw_matrix = load_rds_object(file_content)
            logger.debug(f"Loaded R object type: {type(wiw_matrix)}")

            num_samples = 1
        case _:
            raise ValueError(
                f"Unsupported TransPhylo input type: {input_type!r}. "
                "Expected 'mcmc' or 'wiw_matrix'."
            )

    # This should happen if no samples left after burnin...
    if wiw_matrix is None:
        return [], [], num_samples

    new_nodes, new_edges = build_graph_from_wiw_matrix(wiw_matrix, label)

    return new_nodes, new_edges, num_samples


def compute_mat_wiw_transphylo_mcmc_rds(record, burnin):
    logger.info("Computing WIW matrix from transphylo MCMC output...")

    if burnin > 0:
        start = round(len(record) * burnin)
        record = record[start:]

    m = len(record)

    if m == 0:
        logger.info("No samples left after burnin, please reduce!")
        return None, m
    logger.info(f"{m} samples found after burnin")

    first_ctree = record[0]["ctree"]["ctree"]

    sampled_mask = (
            (first_ctree[:, 1] == 0) &
            (first_ctree[:, 2] == 0)
    )

    n = int(sampled_mask.sum())

    mat = np.zeros((n, n), dtype=float)

    for sample in record:

        ctree = sample["ctree"]["ctree"]

        host = ctree[:, 3].astype(int)

        # ----------------------------
        # build parent pointer (0-based)
        # parent[child] = parent node
        # ----------------------------
        n_nodes = ctree.shape[0]
        parent = np.full(n_nodes, -1, dtype=int)

        for p in range(n_nodes):
            left = int(ctree[p, 1])
            right = int(ctree[p, 2])

            if left > 0:
                parent[left - 1] = p
            if right > 0:
                parent[right - 1] = p

        # ----------------------------
        # host → index map
        # ----------------------------
        maxs = np.zeros(n, dtype=int) - 1

        for i, h in enumerate(host):
            h = int(h)
            if 1 <= h <= n:
                maxs[h - 1] = i

        # ----------------------------
        # ttree equivalent (only what we need: infectors)
        # ----------------------------
        infectors = np.zeros(n, dtype=int)

        for i in range(n):
            j = maxs[i]
            if j < 0:
                continue

            p = parent[j]
            if p < 0:
                continue

            infector = host[p]
            infectors[i] = infector

        infecteds = np.arange(1, n + 1)

        keep = (infectors > 0) & (infectors <= n)

        mat[infectors[keep] - 1, infecteds[keep] - 1] += 1.0 / m

    return mat, m


def build_graph_from_wiw_matrix(mat, label):
    logger.info("Building WIW network graph from matrix data...")

    # -------------------------
    # handle DataFrame or ndarray
    # -------------------------
    if isinstance(mat, pd.DataFrame):
        node_ids = list(mat.index)
        mat = mat.values
    else:
        node_ids = list(range(1, mat.shape[0] + 1))

    n = mat.shape[0]

    # -------------------------
    # edges
    # -------------------------
    edges = []
    node_strength = Counter()
    edge_id = 0
    net = nx.DiGraph()

    for i in range(n):  # infector
        for j in range(n):  # infectee
            weight = mat[i, j]

            if weight == 0:
                continue

            source = i + 1
            target = j + 1

            edges.append({
                "data": {
                    "source": str(source),
                    "target": str(target),
                    "label": label,
                    "posterior": round(float(weight), 4),
                    "weight": round(float(weight), 4),
                    "color": "black",
                    "id": f"{label}-{edge_id}",
                }
            })

            net.add_edge(
                str(source),
                str(target),
                weight=round(float(weight), 4),
                posterior=round(float(weight), 4),
            )
            node_strength[source] += float(weight)
            edge_id += 1

    # Construct MST if possible
    if net.number_of_nodes() > 0:
        mst_edges = generate_mst_edges_from_network(net, label)
        edges.extend(mst_edges)

    # -------------------------
    # nodes
    # -------------------------
    nodes = []

    for i in range(n):
        node_id = i + 1

        nodes.append({
            "data": {
                "id": str(node_id),
                "label": str(node_id),
                "taxon": str(node_id) if node_ids is None else str(node_ids[i])
                # todo this could possibly be used to size the nodes
                # "strength": round(node_strength[node_id], 6),
            }
        })

    return nodes, edges
