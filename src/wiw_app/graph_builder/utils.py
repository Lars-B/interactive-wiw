import base64
import os
import tempfile

import rdata
from networkx.algorithms.tree.branchings import maximum_spanning_arborescence
from networkx.exception import NetworkXException

from wiw_app.dash_logger import logger


def _decode_rds_to_tempfile(base64_content):
    if "," in base64_content:
        base64_content = base64_content.split(",", 1)[1]

    file_bytes = base64.b64decode(base64_content)

    with tempfile.NamedTemporaryFile(suffix=".rds", delete=False) as tmp:
        tmp.write(file_bytes)
        return tmp.name


def load_rds_object_pyreadr(base64_content):
    """Load an RDS file via pyreadr. Only supports simple/data.frame-like R objects."""
    import pyreadr

    tmp_path = _decode_rds_to_tempfile(base64_content)

    try:
        result = pyreadr.read_r(tmp_path)

        if not result:
            raise ValueError("No objects found in RDS file")

        return next(iter(result.values()))

    finally:
        os.remove(tmp_path)


def load_rds_object_rdata(base64_content):
    """Load an RDS file via rdata. Supports complex/nested R objects (lists, S4, etc.)."""

    tmp_path = _decode_rds_to_tempfile(base64_content)

    try:
        logger.info("Parsing the rdata")
        parsed = rdata.parser.parse_file(tmp_path)
        logger.info("Successfully parsed the rdata.")

        logger.info("Converting the Rdata to a python object")
        converted = rdata.conversion.convert(parsed)
        logger.info("Successfully converted the Rdata to a python object.")

        if not converted:
            raise ValueError("No objects found in RDS file")

        return converted

    finally:
        os.remove(tmp_path)


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
