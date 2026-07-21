import numpy as np
import pandas as pd

from wiw_app.dash_logger import logger
from wiw_app.graph_builder.graph_from_matrix import build_graph_from_wiw_matrix
from wiw_app.graph_builder.utils import load_rds_object_rdata, load_rds_object_pyreadr


def build_graph_from_transphylo_rds(file_content, label, burnin, input_type):
    logger.info(f"We are using this input_type: {input_type}")

    wiw_indirect = None

    match input_type:
        case "mcmc":
            obj = load_rds_object_rdata(file_content)
            logger.info(f"Loaded R object type: {type(obj)}")

            wiw_direct, wiw_indirect, num_samples = compute_mat_wiw_transphylo_mcmc_rds(
                obj,
                burnin=burnin
            )

            names = obj[0]["ctree"]["nam"]
            wiw_direct = pd.DataFrame(
                wiw_direct,
                index=names,
                columns=names,
            )

            wiw_indirect = pd.DataFrame(
                wiw_indirect,
                index=names,
                columns=names,
            )

        case "wiw_matrix":
            wiw_direct = load_rds_object_pyreadr(file_content)
            logger.debug(f"Loaded R object type: {type(wiw_direct)}")

            num_samples = 1

        case _:
            raise ValueError(
                f"Unsupported TransPhylo input type: {input_type!r}. "
                "Expected 'mcmc' or 'wiw_matrix'."
            )

    # This should happen if no samples left after burnin...
    if wiw_direct is None:
        return [], [], num_samples

    new_nodes, new_edges = build_graph_from_wiw_matrix(wiw_direct, label)

    if wiw_indirect is not None:
        new_nodes_indirect, new_edges_indirect = build_graph_from_wiw_matrix(
            wiw_direct, f"indirect-{label}"
        )

    # merging the nodes and edges direct + indirect
    merged_nodes = new_nodes + new_nodes_indirect
    merged_edges = new_edges + new_edges_indirect

    return merged_nodes, merged_edges, num_samples


def compute_mat_wiw_transphylo_mcmc_rds(record, burnin):
    logger.info("Computing WIW matrix from transphylo MCMC output...")

    if burnin > 0:
        start = round(len(record) * burnin)
        record = record[start:]

    m = len(record)

    if m == 0:
        logger.info("No samples left after burnin, please reduce!")
        return None, None, m
    logger.info(f"{m} samples found after burnin")

    # ctree column layout
    COL_LEFT, COL_RIGHT, COL_HOST = 1, 2, 3

    first_ctree = record[0]["ctree"]["ctree"]

    sampled_mask = (
            (first_ctree[:, COL_LEFT] == 0) &
            (first_ctree[:, COL_RIGHT] == 0)
    )

    n = int(sampled_mask.sum())

    mat_direct = np.zeros((n, n), dtype=float)
    mat_indirect = np.zeros((n, n), dtype=float)

    for sample_idx, sample in enumerate(record):

        ctree = sample["ctree"]["ctree"]

        host = ctree[:, COL_HOST].astype(int)

        # ----------------------------
        # build parent pointer (0-based), vectorized
        # parent[child] = parent node
        # ----------------------------
        n_nodes = ctree.shape[0]
        parent = np.full(n_nodes, -1, dtype=int)

        left = ctree[:, COL_LEFT].astype(int)
        right = ctree[:, COL_RIGHT].astype(int)

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
        # ttree equivalent: infectors, split into direct / indirect
        # direct: immediate parent host is itself a sampled case
        # indirect: walked up through one or more unsampled hosts
        # ----------------------------
        infectors_direct = np.zeros(n, dtype=int)
        infectors_indirect = np.zeros(n, dtype=int)

        for i in range(n):
            j = host_to_node[i]
            if j < 0:
                continue

            p = parent[j]
            if p < 0:
                continue

            first_candidate = host[p]

            if 1 <= first_candidate <= n:
                infectors_direct[i] = first_candidate
                continue

            p = parent[p]

            while p >= 0:
                candidate = host[p]

                if 1 <= candidate <= n:
                    infectors_indirect[i] = candidate
                    logger.debug(
                        f"[sample {sample_idx}] indirect infector found:"
                        f" {candidate} -> {i + 1}"
                    )

                    break

                p = parent[p]

        infecteds = np.arange(1, n + 1)

        keep_direct = (infectors_direct > 0) & (infectors_direct <= n)
        keep_indirect = (infectors_indirect > 0) & (infectors_indirect <= n)

        mat_direct[infectors_direct[keep_direct] - 1, infecteds[keep_direct] - 1] += 1.0 / m
        mat_indirect[infectors_indirect[keep_indirect] - 1, infecteds[keep_indirect] - 1] += 1.0 / m

    return mat_direct, mat_indirect, m
