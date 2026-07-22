import base64
import os
import tempfile
from collections import defaultdict
from typing import Any

import networkx as nx

from wiw_app.dash_logger import logger
from brokilon.core.taxon_map_utils import get_mapping_dict

from wiw_app.graph_elements import generate_mst_edges_from_network


def build_graph_from_scotti_tree_file(file_content, label, burn_in):
    # ---------------------------------------------------------------- #
    # 1. Normalize input into a list of text lines
    # ---------------------------------------------------------------- #
    if isinstance(file_content, bytes):
        raw_bytes = file_content
    elif isinstance(file_content, str):
        if file_content.startswith("data:") and ";base64," in file_content:
            _, b64data = file_content.split(";base64,", 1)
            raw_bytes = base64.b64decode(b64data)
        else:
            raw_bytes = file_content.encode("utf-8")
    else:
        raise TypeError("file_content must be bytes or str")

    text = raw_bytes.decode("utf-8", errors="replace")
    lines = text.splitlines()

    # ---------------------------------------------------------------- #
    # 2. Parsing helpers (ported from the original script)
    # ---------------------------------------------------------------- #
    def extractInfo(string):
        index = 0
        while string[index] != "[":
            index += 1
        index2 = len(string) - 1
        while string[index2] != "]":
            index2 -= 1
        subString = string[index + 1:index2]
        listTraits = subString.split(",")
        host = "-1"
        numT = "-1"
        for t in listTraits:
            trait = t.split("=")[0]
            if trait == "&host":
                host = t.split("=")[1]
            if trait == "numTransmissions":
                numT = t.split("=")[1]
        if host == "-1" or numT == "-1":
            raise ValueError(
                "Traits in tree are not recognised: could not find host or "
                "numTransmissions along branch: " + string
            )
        return [host, int(numT)]

    def splitTree(tree):
        if tree[0] != "(" or tree[-1] != ")":
            raise ValueError("Tree does not start or end in parenthesis: " + tree)
        openCount = 0
        index = 0
        while tree[index] != "," or openCount != 1:
            if tree[index] == "(" or tree[index] == "[":
                openCount += 1
            elif tree[index] == ")" or tree[index] == "]":
                openCount -= 1
            index += 1
            if index == len(tree):
                return [tree]
        return [tree[1:index], tree[index + 1:-1]]

    def metaData(tree):
        index = len(tree) - 1
        while tree[index] != ")":
            index -= 1
            if index == 0:
                return [tree]
        return [tree[0:index + 1], tree[index + 1:]]

    def recurFindHosts(tree, hosts):
        mt = metaData(tree)
        if len(mt) > 1:
            host = extractInfo(mt[1])[0]
        else:
            host = extractInfo(mt[0])[0]
        if host != "Unsampled" and host not in hosts:
            hosts.append(host)
        if len(mt) > 1:
            splitT = splitTree(mt[0])
            recurFindHosts(splitT[0], hosts)
            recurFindHosts(splitT[1], hosts)

    def handleTree(mt, root, parentHost, numTransParent, directTrans,
                   indirectTrans, metAlready, metAlreadyInd, origins):
        if root[1] == 0:  # no change
            if len(mt) > 1:
                recurTransm(mt[0], parentHost, numTransParent, directTrans,
                            indirectTrans, metAlready, metAlreadyInd, origins)

        elif root[0] == "Unsampled":  # going to an unsampled node
            if len(mt) > 1:
                recurTransm(mt[0], parentHost, numTransParent + root[1],
                            directTrans, indirectTrans, metAlready,
                            metAlreadyInd, origins)

        elif parentHost == "Unsampled":  # coming from an unsampled node
            if root[0] != "Unsampled":
                if root[0] not in origins:
                    origins[root[0]] = "Unsampled"
            if len(mt) > 1:
                recurTransm(mt[0], root[0], 0, directTrans, indirectTrans,
                            metAlready, metAlreadyInd, origins)

        elif parentHost != root[0]:  # one sampled host to a different one
            if (root[1] + numTransParent) == 1:  # direct transmission
                if ((root[0] not in metAlready[parentHost]) and
                        (root[0] not in metAlreadyInd[parentHost])):
                    metAlready[parentHost].append(root[0])
                    directTrans[parentHost][root[0]] += 1
                if root[0] in origins:
                    if origins[root[0]] != parentHost and origins[root[0]] != "Unsampled":
                        origins[root[0]] = "doubleOrigin"
                    else:
                        origins[root[0]] = parentHost
                else:
                    origins[root[0]] = parentHost
            elif (root[1] + numTransParent) > 1:  # indirect transmission
                if ((root[0] not in metAlready[parentHost]) and
                        (root[0] not in metAlreadyInd[parentHost])):
                    metAlreadyInd[parentHost].append(root[0])
                    indirectTrans[parentHost][root[0]].append(root[1] + numTransParent)
                if root[0] not in origins:
                    origins[root[0]] = "Unsampled"
            else:
                raise ValueError(
                    "Unexpected transmission count of 0 between different hosts."
                )
            if len(mt) > 1:
                recurTransm(mt[0], root[0], 0, directTrans, indirectTrans,
                            metAlready, metAlreadyInd, origins)

        else:  # from one host back to itself
            if root[1] + numTransParent == 1:
                raise ValueError(
                    "Unexpected transmission count of 1 for a self-loop."
                )
            if ((root[0] not in metAlready[parentHost]) and
                    (root[0] not in metAlreadyInd[parentHost])):
                metAlreadyInd[parentHost].append(root[0])
                indirectTrans[parentHost][root[0]].append(root[1] + numTransParent)
            if root[0] not in origins:
                origins[root[0]] = "Unsampled"
            if len(mt) > 1:
                recurTransm(mt[0], root[0], 0, directTrans, indirectTrans,
                            metAlready, metAlreadyInd, origins)

    def recurTransm(tree, parentHost, numTransParent, directTrans,
                     indirectTrans, metAlready, metAlreadyInd, origins):
        splitT = splitTree(tree)
        mt = metaData(splitT[0])
        root = extractInfo(mt[-1])
        handleTree(mt, root, parentHost, numTransParent, directTrans,
                   indirectTrans, metAlready, metAlreadyInd, origins)
        mt = metaData(splitT[1])
        root = extractInfo(mt[-1])
        handleTree(mt, root, parentHost, numTransParent, directTrans,
                   indirectTrans, metAlready, metAlreadyInd, origins)

    # ---------------------------------------------------------------- #
    # 3. Locate the tree lines and figure out the burn-in cutoff
    # ---------------------------------------------------------------- #
    candidate_lines = [l for l in lines if len(l.split()) > 0 and l.split()[0] == "tree"]
    if not candidate_lines:
        raise ValueError("Incorrect input file: is this a BEAST2/SCOTTI .trees output file?")

    normal_l = len(candidate_lines[0].split())
    tree_lines = [l for l in candidate_lines if len(l.split()) == normal_l]

    num_trees_total = len(tree_lines)
    burned = int(burn_in * num_trees_total)

    # ---------------------------------------------------------------- #
    # 4. Walk every post-burn-in tree, accumulating transmission counts
    # ---------------------------------------------------------------- #
    hosts = []
    direct_trans = defaultdict(lambda: defaultdict(int))
    indirect_trans = defaultdict(lambda: defaultdict(list))
    roots = defaultdict(int)

    for i, line in enumerate(tree_lines):
        if i < burned:
            continue

        tree = line.split()[3]
        recurFindHosts(tree, hosts)

        mt = metaData(tree)
        root = extractInfo(mt[1])
        roots[root[0]] += 1

        met_already = defaultdict(list)
        met_already_ind: defaultdict[Any, list] = defaultdict(list)
        origins = {}
        if root[0] != "Unsampled":
            origins[root[0]] = "Unsampled"

        recurTransm(mt[0], root[0], 0, direct_trans, indirect_trans,
                    met_already, met_already_ind, origins)

    num_trees_used = num_trees_total - burned
    if num_trees_used <= 0:
        raise ValueError("No trees remain after applying the burn-in percentage.")

    # Extract the taxon map dictionary from given tree file
    tmp = tempfile.NamedTemporaryFile(mode='wb', suffix=".nex", delete=False)
    try:
        _, content = file_content.split(",", 1)

        chunk_size = 1024 * 1024
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            tmp.write(base64.b64decode(chunk))
        tmp.flush()
        tmp.close()

        taxon_map = get_mapping_dict(tmp.name)

    finally:
        os.remove(tmp.name)

    logger.info(f"Extracted a taxon map from the scotti file: {taxon_map}")
    reversed_taxon_map = {v: k for k,v in taxon_map.items()}
    host_taxon_map = {h: lookup_taxon_via_host(reversed_taxon_map, h) for h in hosts}

    # ---------------------------------------------------------------- #
    # 5. Build cytoscape elements (all non-zero edges, no threshold)
    # ---------------------------------------------------------------- #
    nodes = []
    for h in hosts:
        nodes.append({
            "data": {
                "id": host_taxon_map[h],
                "label": host_taxon_map[h],
                "taxon": taxon_map[int(host_taxon_map[h])],
                "host": h,
            }
        })

    edges = []

    direct_net = nx.DiGraph()

    for h1 in hosts:
        for h2 in hosts:
            if h1 == h2:
                continue

            direct_count = direct_trans[h1][h2]
            if direct_count:
                posterior_support = direct_count / num_trees_used
                edges.append({
                    "data": {
                        "id": f"{label}-direct-{h1}-{h2}",
                        "source": host_taxon_map[h1],
                        "target": host_taxon_map[h2],
                        "weight": round(posterior_support, 2),
                        "posterior": round(posterior_support, 3),
                        "label": f"{label}",
                    }
                })

                direct_net.add_edge(
                    host_taxon_map[h1],
                    host_taxon_map[h2],
                    weight=round(posterior_support, 2),
                    posterior=round(posterior_support, 3)
                )

            indirect_count = len(indirect_trans[h1][h2])
            if indirect_count:
                posterior_support = indirect_count / num_trees_used
                edges.append({
                    "data": {
                        "id": f"{label}-indirect-{h1}-{h2}",
                        "source": host_taxon_map[h1],
                        "target": host_taxon_map[h2],
                        "weight": round(posterior_support, 2),
                        "posterior": round(posterior_support, 3),
                        "label": f"Indirect-{label}",
                    }
                })

    if num_trees_used > 0 and direct_net.number_of_nodes() > 1:
        mst_edges = generate_mst_edges_from_network(direct_net, label)
        edges.extend(mst_edges)

    return nodes, edges, num_trees_used


def lookup_taxon_via_host(reversed_taxon_map, host):
    if host in reversed_taxon_map:
        return str(reversed_taxon_map[host])

    matches = [
        k for k in reversed_taxon_map
        if host in k or k in host
    ]

    if len(matches) == 1:
        logger.info(f"Found and will use a partial match...{matches[0]} for {host}")
        return str(reversed_taxon_map[matches[0]])
    elif len(matches) == 0:
        logger.warning(f"Found no matches for {host}...")
        return host
    else:
        logger.warning(f"Found {len(matches)} matches for {host}...using the first match")
        return str(reversed_taxon_map[matches[0]])
