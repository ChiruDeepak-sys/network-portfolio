"""Validate a small leaf-spine design described in JSON."""

import argparse
import json
import sys
from pathlib import Path


def validate(data):
    errors = []
    nodes = {node.get("name"): node for node in data.get("nodes", []) if node.get("name")}
    links = data.get("links", [])

    if not nodes:
        return ["Topology has no named nodes."]

    subnets = set()
    pairs = set()
    neighbors = {name: set() for name in nodes}

    for index, link in enumerate(links, start=1):
        a, b = link.get("a"), link.get("b")
        subnet = link.get("subnet")
        if a not in nodes or b not in nodes:
            errors.append("Link {} references an unknown node ({} - {}).".format(index, a, b))
            continue
        pair = tuple(sorted((a, b)))
        if pair in pairs:
            errors.append("Duplicate physical link between {} and {}.".format(a, b))
        pairs.add(pair)
        neighbors[a].add(b)
        neighbors[b].add(a)
        if not subnet:
            errors.append("Link {} has no subnet.".format(index))
        elif subnet in subnets:
            errors.append("Subnet {} is reused.".format(subnet))
        else:
            subnets.add(subnet)

    spines = {name for name, node in nodes.items() if node.get("role") == "spine"}
    leaves = {name for name, node in nodes.items() if node.get("role") == "leaf"}
    if len(spines) < 2:
        errors.append("Design should include at least two spines for redundancy.")
    if not leaves:
        errors.append("Design has no leaf nodes.")

    for leaf in sorted(leaves):
        connected_spines = neighbors[leaf] & spines
        if len(connected_spines) < 2:
            errors.append("Leaf {} has fewer than two spine uplinks.".format(leaf))

    for name, node in nodes.items():
        peers = set(node.get("bgp_peers", []))
        for peer in peers:
            if peer not in nodes:
                errors.append("Node {} lists unknown BGP peer {}.".format(name, peer))
                continue
            reciprocal = set(nodes[peer].get("bgp_peers", []))
            if name not in reciprocal:
                errors.append("BGP peer definition is not reciprocal: {} <-> {}.".format(name, peer))
            if node.get("asn") == nodes[peer].get("asn"):
                errors.append("{} and {} use the same ASN; review the intended peering model.".format(name, peer))

    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topology", required=True, type=Path, help="Path to the topology JSON file")
    args = parser.parse_args()

    try:
        with args.topology.open("r", encoding="utf-8") as stream:
            data = json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        print("ERROR: Could not read topology: {}".format(exc), file=sys.stderr)
        return 2

    errors = validate(data)
    if errors:
        print("Topology review: {} issue(s)".format(len(errors)))
        for error in errors:
            print("REVIEW {}".format(error))
        return 1

    print("PASS Leaf-spine redundancy, link subnets, and reciprocal BGP peer definitions look consistent.")
    print("Note: This validates the design file only; it does not test device configuration or packet forwarding.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
