"""OACR-R2 v1: full candidate/control audit on frozen R1 raw carrier."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple

import networkx as nx

ROOT = "Q12136"
EXPECTED_RAW_SHA256 = "3d3852ff72382c171e3a5496336767809b9455541fa2604f7b6857a8e69457df"


def qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1].strip()


def parse_edges(raw: bytes) -> List[Tuple[str, str]]:
    obj = json.loads(raw.decode("utf-8"))
    edges = set()
    for row in obj["results"]["bindings"]:
        if "child" not in row or "parent" not in row:
            continue
        c, p = qid(row["child"]["value"]), qid(row["parent"]["value"])
        if c and p and c != p and c.startswith("Q") and p.startswith("Q"):
            edges.add((c, p))
    return sorted(edges)


def prepare_graph(edges):
    g = nx.DiGraph()
    g.add_edges_from(edges)
    if ROOT in g:
        nodes = nx.node_connected_component(g.to_undirected(), ROOT)
    else:
        nodes = max(nx.weakly_connected_components(g), key=len)
    g = g.subgraph(nodes).copy()
    sccs = list(nx.strongly_connected_components(g))
    cyclic = [sorted(c) for c in sccs if len(c) > 1]
    if cyclic:
        c = nx.condensation(g, sccs)
        members = {int(n): sorted(c.nodes[n]["members"]) for n in c.nodes}
        cg = nx.DiGraph((int(a), int(b)) for a, b in c.edges if a != b)
        labels = {
            int(n): members[int(n)][0] if len(members[int(n)]) == 1
            else "SCC[" + ",".join(members[int(n)]) + "]"
            for n in cg.nodes
        }
        return cg, cyclic, labels
    return g, [], {n: n for n in g.nodes}


def closure(g):
    if not nx.is_directed_acyclic_graph(g):
        raise RuntimeError("prepared graph must be a DAG")
    return set(nx.transitive_closure_dag(g).edges())


def lex_first_shortest_path(g, u, v):
    paths = [tuple(p) for p in nx.all_shortest_paths(g, u, v)]
    if not paths:
        raise RuntimeError("no shortest path")
    return list(sorted(paths, key=lambda p: tuple(map(str, p)))[0])


def path_count(g, source, target):
    topo = list(nx.topological_sort(g))
    pos = {n: i for i, n in enumerate(topo)}
    if source not in pos or target not in pos or pos[source] >= pos[target]:
        return 0
    ways: Dict[object, int] = {source: 1}
    for n in topo[pos[source] : pos[target] + 1]:
        w = ways.get(n, 0)
        if not w:
            continue
        for nxt in g.successors(n):
            if pos[nxt] <= pos[target]:
                ways[nxt] = ways.get(nxt, 0) + w
    return int(ways.get(target, 0))


def minimal_shortest_supports(g, u, v, cap=128):
    length = nx.shortest_path_length(g, u, v)
    out = []
    for p in nx.all_simple_paths(g, u, v, cutoff=length):
        if len(p) - 1 != length:
            continue
        out.append(tuple((p[i], p[i + 1]) for i in range(len(p) - 1)))
        if len(out) >= cap:
            break
    return sorted(out, key=str)


def confusion(rows, key):
    tp=fp=fn=tn=0
    for r in rows:
        pred=bool(r[key])
        actual=bool(r["required_separation"])
        if pred and actual: tp += 1
        elif pred and not actual: fp += 1
        elif (not pred) and actual: fn += 1
        else: tn += 1
    return {
        "TP_required_separated": tp,
        "FP_over_refinement": fp,
        "FN_under_refinement": fn,
        "TN_nonrequired_merged": tn,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--raw_json", required=True)
    ap.add_argument("--out", required=True)
    args=ap.parse_args()

    raw_path=Path(args.raw_json)
    raw=raw_path.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if sha != EXPECTED_RAW_SHA256:
        raise RuntimeError(f"raw carrier hash mismatch: {sha}")

    edges=parse_edges(raw)
    g, cyclic, labels=prepare_graph(edges)
    base_edges=set(g.edges())
    base_closure=closure(g)
    candidates=sorted(base_closure-base_edges, key=lambda x:(str(x[0]),str(x[1])))

    rows=[]
    for u,v in candidates:
        e=(u,v)
        path=lex_first_shortest_path(g,u,v)
        if len(path)<3:
            raise RuntimeError("entailed-unasserted pair unexpectedly has path length <2")
        f=(path[0],path[1])

        g1=g.copy()
        g1.add_edge(*e)
        c1=closure(g1)
        if c1 != base_closure:
            raise RuntimeError("pre-write closure equality failed")

        post0g=g.copy()
        post1g=g1.copy()
        post0g.remove_edge(*f)
        post1g.remove_edge(*f)
        post0=closure(post0g)
        post1=closure(post1g)
        required=post0 != post1

        count0=path_count(g,u,v)
        count1=path_count(g1,u,v)
        a1=count0 != count1
        a2=(e in base_edges) != (e in set(g1.edges()))
        a3=minimal_shortest_supports(g,u,v) != minimal_shortest_supports(g1,u,v)

        rows.append({
            "u":labels[u],
            "v":labels[v],
            "future_delete_edge":[labels[f[0]],labels[f[1]]],
            "selected_shortest_path":[labels[x] for x in path],
            "pre_full_closure_equal":True,
            "required_separation":required,
            "post_symmetric_difference_size":len(post0 ^ post1),
            "target_survives_g0":(u,v) in post0,
            "target_survives_g1":(u,v) in post1,
            "A1_support_count_g0":str(count0),
            "A1_support_count_g1":str(count1),
            "A1_separates":a1,
            "A2_separates":a2,
            "A3_separates":a3,
        })

    summary={
        "raw_response_sha256":sha,
        "prepared_nodes":g.number_of_nodes(),
        "prepared_asserted_edges":g.number_of_edges(),
        "closure_size":len(base_closure),
        "cyclic_scc_count":len(cyclic),
        "candidate_universe":len(candidates),
        "required_separations":sum(int(r["required_separation"]) for r in rows),
        "nonrequired_controls":sum(int(not r["required_separation"]) for r in rows),
        "A1":confusion(rows,"A1_separates"),
        "A2":confusion(rows,"A2_separates"),
        "A3":confusion(rows,"A3_separates"),
        "post_symdiff_min":min(r["post_symmetric_difference_size"] for r in rows),
        "post_symdiff_max":max(r["post_symmetric_difference_size"] for r in rows),
    }
    out={
        "protocol":"OACR_R2_FULL_RELATIONAL_CANDIDATE_CONTROL_AUDIT_V1",
        "registered_action_rule":"delete first edge of lexicographically first shortest support path",
        "source":{"r1_run":36378905855,"raw_sha256":sha},
        "summary":summary,
        "rows":rows,
    }
    p=Path(args.out)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,indent=2))
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
