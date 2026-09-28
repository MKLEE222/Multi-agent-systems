"""OACR-R1 v1: relational support / retraction congruence on Wikidata-derived subclass graphs.

This is a cross-system realization experiment. It deliberately instantiates a
mature truth-maintenance / provenance phenomenon inside the OACR framework; it
is not presented as a new database-theory result.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import networkx as nx
import requests

WDQS = "https://query.wikidata.org/sparql"
ROOT = "Q12136"  # disease
QUERY = """SELECT DISTINCT ?child ?parent WHERE {
  {
    ?child wdt:P279 wd:Q12136 .
    BIND(wd:Q12136 AS ?parent)
  }
  UNION
  {
    ?mid wdt:P279 wd:Q12136 .
    ?child wdt:P279 ?mid .
    BIND(?mid AS ?parent)
  }
  UNION
  {
    ?top wdt:P279 wd:Q12136 .
    ?mid wdt:P279 ?top .
    ?child wdt:P279 ?mid .
    BIND(?mid AS ?parent)
  }
}
ORDER BY ?child ?parent
LIMIT 1500
"""


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--raw_tsv", required=True)
    p.add_argument("--max_witnesses", type=int, default=64)
    p.add_argument("--timeout", type=int, default=120)
    p.add_argument("--retries", type=int, default=4)
    return p.parse_args()


def qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1].strip()


def fetch_tsv(timeout: int, retries: int) -> bytes:
    headers = {
        "Accept": "text/tab-separated-values",
        "User-Agent": "OACR-research/1.0 (GitHub Actions; reproducibility audit)",
    }
    last = None
    for attempt in range(retries):
        try:
            r = requests.get(
                WDQS,
                params={"query": QUERY, "format": "tsv"},
                headers=headers,
                timeout=timeout,
            )
            r.raise_for_status()
            data = r.content
            if len(data) < 100:
                raise RuntimeError(f"WDQS response unexpectedly small: {len(data)} bytes")
            return data
        except Exception as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"WDQS fetch failed after {retries} attempts: {last}")


def parse_edges(raw: bytes) -> List[Tuple[str, str]]:
    text = raw.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    if not reader.fieldnames:
        raise RuntimeError("WDQS TSV response has no header")
    fields = {name.lstrip("?"): name for name in reader.fieldnames}
    if "child" not in fields or "parent" not in fields:
        raise RuntimeError(f"Unexpected WDQS TSV header: {reader.fieldnames!r}")
    edges = set()
    for row in reader:
        c, p = qid(row[fields["child"]]), qid(row[fields["parent"]])
        if c and p and c != p and c.startswith("Q") and p.startswith("Q"):
            edges.add((c, p))
    return sorted(edges)


def prepare_graph(edges: List[Tuple[str, str]]):
    g = nx.DiGraph()
    g.add_edges_from(edges)
    if g.number_of_edges() < 50:
        raise RuntimeError(f"Too few unique asserted edges: {g.number_of_edges()}")

    if ROOT in g:
        comp_nodes = nx.node_connected_component(g.to_undirected(), ROOT)
    else:
        comp_nodes = max(nx.weakly_connected_components(g), key=len)
    g = g.subgraph(comp_nodes).copy()

    sccs = list(nx.strongly_connected_components(g))
    cyclic = [sorted(c) for c in sccs if len(c) > 1]

    if cyclic:
        c = nx.condensation(g, sccs)
        mapping = c.graph["mapping"]
        members = {
            int(node): sorted(c.nodes[node]["members"])
            for node in c.nodes
        }
        cg = nx.DiGraph()
        for a, b in c.edges:
            if a != b:
                cg.add_edge(int(a), int(b))
        label = {
            int(node): (
                members[int(node)][0]
                if len(members[int(node)]) == 1
                else "SCC[" + ",".join(members[int(node)]) + "]"
            )
            for node in cg.nodes
        }
        return cg, cyclic, label

    label = {n: n for n in g.nodes}
    return g, [], label


def closure_edges(g: nx.DiGraph) -> set:
    if not nx.is_directed_acyclic_graph(g):
        raise RuntimeError("Prepared graph must be a DAG")
    tc = nx.transitive_closure_dag(g)
    return set(tc.edges())


def path_count_dag(g: nx.DiGraph, source, target) -> int:
    """Exact number of directed paths source -> target in a DAG."""
    if source == target:
        return 1
    if source not in g or target not in g:
        return 0
    topo = list(nx.topological_sort(g))
    pos = {n: i for i, n in enumerate(topo)}
    if pos[source] >= pos[target]:
        return 0
    ways: Dict[object, int] = {source: 1}
    for n in topo[pos[source]: pos[target] + 1]:
        w = ways.get(n, 0)
        if not w:
            continue
        for nxt in g.successors(n):
            if pos[nxt] <= pos[target]:
                ways[nxt] = ways.get(nxt, 0) + w
    return int(ways.get(target, 0))


def minimal_path_edge_sets(g: nx.DiGraph, u, v, cap: int = 64):
    """Enumerate shortest-path edge support sets, bounded for artifact size."""
    try:
        length = nx.shortest_path_length(g, u, v)
    except nx.NetworkXNoPath:
        return []
    out = []
    for p in nx.all_simple_paths(g, u, v, cutoff=length):
        if len(p) - 1 != length:
            continue
        out.append([[str(p[i]), str(p[i + 1])] for i in range(len(p) - 1)])
        if len(out) >= cap:
            break
    return out


def main():
    args = parse_args()
    out_path = Path(args.out).resolve()
    raw_path = Path(args.raw_tsv).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    retrieved_at = datetime.now(timezone.utc).isoformat()
    raw = fetch_tsv(args.timeout, args.retries)
    raw_path.write_bytes(raw)
    raw_sha = hashlib.sha256(raw).hexdigest()

    edges = parse_edges(raw)
    g, cyclic_sccs, labels = prepare_graph(edges)
    base_edges = set(g.edges())
    base_closure = closure_edges(g)

    candidates = sorted(base_closure - base_edges, key=lambda x: (str(x[0]), str(x[1])))
    witnesses = []

    for u, v in candidates:
        if len(witnesses) >= args.max_witnesses:
            break

        try:
            p = nx.shortest_path(g, u, v)
        except nx.NetworkXNoPath:
            continue
        if len(p) < 3:
            continue

        future_edge: Optional[Tuple[object, object]] = None
        for f in zip(p[:-1], p[1:]):
            h = g.copy()
            h.remove_edge(*f)
            if not nx.has_path(h, u, v):
                future_edge = f
                break
        if future_edge is None:
            continue

        e = (u, v)
        g1 = g.copy()
        g1.add_edge(*e)
        closure1 = closure_edges(g1)
        if closure1 != base_closure:
            raise RuntimeError("Adding an already entailed edge changed current closure")

        g0_post = g.copy()
        g1_post = g1.copy()
        g0_post.remove_edge(*future_edge)
        g1_post.remove_edge(*future_edge)
        post0 = closure_edges(g0_post)
        post1 = closure_edges(g1_post)

        if (u, v) in post0:
            continue
        if (u, v) not in post1:
            continue
        if post0 == post1:
            continue

        count0 = path_count_dag(g, u, v)
        count1 = path_count_dag(g1, u, v)
        a1_separates = count0 != count1
        a2_separates = (e in base_edges) != (e in set(g1.edges()))
        prov0 = minimal_path_edge_sets(g, u, v)
        prov1 = minimal_path_edge_sets(g1, u, v)
        a3_separates = prov0 != prov1

        diff_added = sorted(post1 - post0, key=lambda x: (str(x[0]), str(x[1])))
        diff_removed = sorted(post0 - post1, key=lambda x: (str(x[0]), str(x[1])))

        first = (
            "A1_SUPPORT_MULTIPLICITY" if a1_separates
            else "A2_ASSERTED_SUPPORT" if a2_separates
            else "A3_MINIMAL_PROVENANCE" if a3_separates
            else "UNSEPARATED_THROUGH_A3"
        )

        witnesses.append({
            "u": labels[u],
            "v": labels[v],
            "redundant_added_assertion": [labels[u], labels[v]],
            "future_delete_edge": [labels[future_edge[0]], labels[future_edge[1]]],
            "shortest_support_path": [labels[x] for x in p],
            "pre_full_closure_equal": True,
            "pre_closure_size": len(base_closure),
            "post_full_closure_equal": False,
            "post_closure_size_g0": len(post0),
            "post_closure_size_g1": len(post1),
            "post_symmetric_difference_size": len(post0 ^ post1),
            "target_entailment_after_delete_g0": False,
            "target_entailment_after_delete_g1": True,
            "A1_support_count_g0": str(count0),
            "A1_support_count_g1": str(count1),
            "A1_separates": a1_separates,
            "A2_separates": a2_separates,
            "A3_separates": a3_separates,
            "first_separating_refinement": first,
            "minimal_shortest_supports_g0": prov0,
            "minimal_shortest_supports_g1": prov1,
            "post_added_entailments_sample": [
                [labels[a], labels[b]] for a, b in diff_added[:20]
            ],
            "post_removed_entailments_sample": [
                [labels[a], labels[b]] for a, b in diff_removed[:20]
            ],
        })

    if not witnesses:
        raise RuntimeError("No exact relational congruence witness found in frozen carrier")

    summary = {
        "root": ROOT,
        "raw_tsv_sha256": raw_sha,
        "unique_asserted_edges_raw": len(edges),
        "prepared_nodes": g.number_of_nodes(),
        "prepared_asserted_edges": g.number_of_edges(),
        "closure_size": len(base_closure),
        "cyclic_scc_count": len(cyclic_sccs),
        "entailed_unasserted_candidates": len(candidates),
        "valid_exact_witnesses": len(witnesses),
        "A1_separates": sum(int(w["A1_separates"]) for w in witnesses),
        "A2_separates": sum(int(w["A2_separates"]) for w in witnesses),
        "A3_separates": sum(int(w["A3_separates"]) for w in witnesses),
        "unseparated_through_A3": sum(
            int(w["first_separating_refinement"] == "UNSEPARATED_THROUGH_A3")
            for w in witnesses
        ),
        "post_symmetric_difference_min": min(
            w["post_symmetric_difference_size"] for w in witnesses
        ),
        "post_symmetric_difference_max": max(
            w["post_symmetric_difference_size"] for w in witnesses
        ),
    }

    artifact = {
        "protocol": "OACR_R1_RELATIONAL_RETRACTION_V1",
        "carrier": "Wikidata-derived P279 subclass graph",
        "wikidata_root": {"qid": ROOT, "label": "disease"},
        "relation": "P279",
        "semantic_read": "complete transitive closure of prepared finite carrier",
        "native_write": "explicit asserted-edge deletion",
        "wdqs_endpoint": WDQS,
        "query": QUERY,
        "retrieved_at_utc": retrieved_at,
        "raw_tsv_sha256": raw_sha,
        "graph_hygiene": {
            "self_loops_removed": True,
            "duplicates_removed": True,
            "component_rule": "component containing Q12136 when present; otherwise largest weak component",
            "cycle_rule": "collapse SCCs before reachability analysis",
            "collapsed_sccs": cyclic_sccs,
        },
        "summary": summary,
        "witnesses": witnesses,
    }
    out_path.write_text(json.dumps(artifact, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
