import numpy as np
import pandas as pd

from wiw_app.dash_logger import logger
from wiw_app.graph_builder.graph_from_matrix import build_graph_from_wiw_matrix
from wiw_app.graph_builder.utils import load_rds_object_rdata, load_rds_object_pyreadr


def build_graph_from_transphylo_rds(file_content, label, burnin, input_type):
    logger.info(f"We are using this input_type: {input_type}")

    match input_type:
        case "mcmc":
            obj = load_rds_object_rdata(file_content)
            logger.info(f"Loaded R object type: {type(obj)}")

            wiw_matrix, num_samples = compute_mat_wiw_transphylo_mcmc_rds(
                obj,
                burnin=burnin
            )

            names = obj[0]["ctree"]["nam"]
            wiw_matrix = pd.DataFrame(
                wiw_matrix,
                index=names,
                columns=names,
            )

        case "wiw_matrix":
            wiw_matrix = load_rds_object_pyreadr(file_content)
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

    # ctree column layout
    col_left, col_right, col_host = 1, 2, 3

    first_ctree = record[0]["ctree"]["ctree"]

    sampled_mask = (
            (first_ctree[:, col_left] == 0) &
            (first_ctree[:, col_right] == 0)
    )

    n = int(sampled_mask.sum())

    mat = np.zeros((n, n), dtype=float)

    for sample in record:

        ctree = sample["ctree"]["ctree"]

        host = ctree[:, col_host].astype(int)

        # ----------------------------
        # build parent pointer (0-based), vectorized
        # parent[child] = parent node
        # ----------------------------
        n_nodes = ctree.shape[0]
        parent = np.full(n_nodes, -1, dtype=int)

        left = ctree[:, col_left].astype(int)
        right = ctree[:, col_right].astype(int)

        has_left = left > 0
        has_right = right > 0

        parent[left[has_left] - 1] = np.where(has_left)[0]
        parent[right[has_right] - 1] = np.where(has_right)[0]

        # ----------------------------
        # host → node index map, vectorized
        # ----------------------------
        host_to_node = np.full(n, -1, dtype=int)

        valid_host = (host >= 1) & (host <= n)
        host_to_node[host[valid_host] - 1] = np.where(valid_host)[0]

        # ----------------------------
        # ttree equivalent (only what we need: infectors)
        # ----------------------------
        infectors = np.zeros(n, dtype=int)

        for i in range(n):
            j = host_to_node[i]
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
