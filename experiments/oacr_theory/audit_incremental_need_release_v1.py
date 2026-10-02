"""Bounded native audit for the Need/Release operator and strong controls."""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
import hashlib
import json
from pathlib import Path

from audit_joint_certificate_maintenance_v1 import (
    bank, initial, literal_bfs, native_check,
)
from joint_certificate_maintenance_v1 import contract_token
from incremental_need_release_v1 import (
    METHODS, check, initialize, sizes, update,
)


def process(base, actual, identity, counters, initialization, audit, digest):
    states = {m: initialize(base, m, initialization[m]) for m in METHODS}
    stack = [((), states)]
    while stack:
        history, current = stack.pop()
        canonical = [current[m].base.stored for m in METHODS if m != "persistent_flat"]
        assert all(r == canonical[0] for r in canonical)
        assert current["residual_need_dag"] == current["generic_indexed_flow_dag"]
        audit["candidate_generic_identical_states"] += 1
        audit["history_states"] += 1
        ledger = []
        for method, state in current.items():
            native_check(state.base, actual, audit, method != "persistent_flat")
            assert check(state, method)
            resource = sizes(state)
            for name,value in resource.items():
                counters[method]["state_sum_"+name] += value
                counters[method]["state_max_"+name] = max(counters[method]["state_max_"+name], value)
            counters[method]["state_observations"] += 1
            ledger.append([method,sorted(state.base.stored),resource["complete_bundle_bytes"]])
        digest.update(json.dumps([identity,history,ledger], separators=(",", ":")).encode()+b"\n")
        anchor = current["residual_need_dag"].base
        for action in sorted(anchor.actions) if anchor.budget else ():
            successors = {}
            for method,state in current.items():
                local = Counter()
                successors[method] = update(state, action, method, "joint_v1",
                                            contract_token(state.base), local)
                if method in ("residual_need_dag", "generic_indexed_flow_dag"):
                    positive = len(state.incidence.get(action, ()))
                    assert local["repair_searches"] <= positive
                    assert local["cold_flow_requests"] == 0
                    assert local["need_edge_visits"] == len(
                        state.buckets.get(state.base.budget, frozenset()) |
                        state.incidence.get(action, frozenset()))
                    audit["local_workset_checks"] += 1
                assert local["source_queries"] == 0
                counters[method].update(local)
            audit["transitions"] += 1
            stack.append((history+(action,),successors))


def fixed_cases():
    return [
        ("budget_only",6,{(0,1),(1,2),(2,3),(4,5)}, {(0,1),(4,5)},
         {(0,2)}, {(0,3)}, (4,5)),
        ("alternative_cut",4,{(0,1),(1,2),(2,3)}, {(0,1),(1,2)},
         {(0,3)}, set(), (1,2)),
        ("rerouting",5,{(0,1),(1,2),(1,3),(2,4),(3,4)}, {(0,1),(1,2)},
         {(0,4)}, set(), (1,2)),
        ("joint_release",7,{(0,1),(1,2),(2,3),(3,4),(5,6)}, {(0,1),(2,3),(5,6)},
         {(0,2),(2,4)}, {(0,4)}, (5,6)),
    ]


def mechanisms():
    result, audit = [], Counter()
    for name,n,g,a,k,u,action in fixed_cases():
        for extra in (frozenset(),frozenset(u)) if u else (frozenset(),):
            actual = frozenset(k)|extra
            base = initial(n,frozenset(g),frozenset(a),1,frozenset(k),frozenset(u),actual,Counter())
            row = {"case":name,"unknown_present":bool(extra),"methods":{}}
            for method in METHODS:
                init_counts, local = Counter(), Counter()
                state = initialize(base,method,init_counts)
                new = update(state,action,method,"joint_v1",contract_token(base),local)
                native_check(new.base,actual,audit,method != "persistent_flat")
                row["methods"][method] = {"initialization":dict(init_counts),"counts":dict(local),
                                          "stored":sorted(new.base.stored),"sizes":sizes(new)}
                if method == "residual_need_dag":
                    if name == "budget_only":
                        assert not state.incidence.get(action) and not new.base.stored
                        row["flow_incidence_only_localizer_fails"] = True
                    if name == "alternative_cut":
                        cap = state.capsules[(0,3)]
                        assert not (action[0] in cap.side and action[1] not in cap.side)
                        assert new.base.stored == {(0,3)} and local["one_unit_losses"] == 1
                        row["invalid_old_cut_does_not_imply_release"] = True
                    if name == "rerouting":
                        assert local["successful_reroutes"] == 1 and not new.base.stored
                    if name == "joint_release":
                        assert local["released_components"] == 2 and not new.base.stored
            result.append(row)
    # Native counterexample to jointly deleting all individually safe supports.
    graph, b, c = frozenset({(0,1),(1,0)}), (0,2), (1,2)
    full = literal_bfs(3,graph|{b,c})
    assert literal_bfs(3,graph|{b}) == full
    assert literal_bfs(3,graph|{c}) == full
    assert literal_bfs(3,graph) != full
    result.append({"case":"outside_DAG_mutual_support","single_releases_safe":True,
                   "joint_release_safe":False,"scope":"native cyclic counterexample"})
    return result,dict(audit)


def attacks():
    base = initial(6,frozenset({(0,1),(1,2),(2,3),(4,5)}),
                   frozenset({(0,1),(4,5)}),1,frozenset({(0,2)}),
                   frozenset({(0,3)}),frozenset({(0,2)}),Counter())
    state = initialize(base,"residual_need_dag",Counter())
    edge = (0,2)
    cap = state.capsules[edge]
    cases = {
        "wrong_value": replace(state,capsules={edge:replace(cap,value=0)}),
        "wrong_cut": replace(state,capsules={edge:replace(cap,side=frozenset())}),
        "over_capacity_flow": replace(state,capsules={edge:replace(cap,flow={(0,1):2,(1,2):2})}),
        "missing_flow_incidence": replace(state,incidence={}),
        "missing_value_bucket": replace(state,buckets={}),
        "unsupported_frozen_prefix": replace(state,capsules={edge:replace(cap,prefix=frozenset({(3,5)}))}),
    }
    reject = {}
    for name,bad in cases.items():
        assert not check(bad,"residual_need_dag")
        try:
            update(bad,(4,5),"residual_need_dag","joint_v1",contract_token(base),Counter())
        except ValueError:
            reject[name] = True
        else:
            raise AssertionError(name)
    for name,action,epoch,token in (
        ("stale_epoch",(4,5),"stale",contract_token(base)),
        ("wrong_predecessor",(4,5),"joint_v1","wrong"),
        ("illegal_action",(1,2),"joint_v1",contract_token(base)),
    ):
        try:
            update(state,action,"residual_need_dag",epoch,token,Counter())
        except ValueError:
            reject[name] = True
        else:
            raise AssertionError(name)
    after = update(state,(4,5),"residual_need_dag","joint_v1",contract_token(base),Counter())
    try:
        update(after,(0,1),"residual_need_dag","joint_v1",contract_token(after.base),Counter())
    except ValueError:
        reject["exhausted_budget"] = True
    else:
        raise AssertionError("exhausted_budget")
    return reject


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    args = parser.parse_args()
    root = Path(__file__).parent
    protocol_path = root/"incremental_need_release_v1.json"
    protocol = json.loads(protocol_path.read_text())
    inputs = [Path(__file__),protocol_path,root/"incremental_need_release_v1.py",
              root/"audit_joint_certificate_maintenance_v1.py",
              root/"joint_certificate_maintenance_v1.py",root/"ordered_source_compile_v1.py",
              root/"available_source_repair_v1.py",root/"contract_budget_audit_v1.py"]
    hashes = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    counters = {m:Counter() for m in METHODS}
    initialization = {m:Counter() for m in METHODS}
    shared, audit, digest = Counter(), Counter(), hashlib.sha256()
    configs = set()
    for case,n,g,a,h,k,u,actual in bank(20261002):
        base = initial(n,g,a,h,k,u,actual,shared)
        process(base,actual,[case,sorted(actual)],counters,initialization,audit,digest)
        configs.add(case)
        audit["source_worlds"] += 1
    assert len(configs) == 60 and audit["source_worlds"] == 744
    assert audit["history_states"] == 7068 and audit["transitions"] == 6324
    assert all(c["updates"] == 6324 for c in counters.values())
    # The generic construction is independently sequenced, with the same
    # classical primitive, certificate language and unrestricted index access.
    assert counters["residual_need_dag"] == counters["generic_indexed_flow_dag"]
    cases,case_audit = mechanisms()
    rejected = attacks()
    assert hashes == {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    result = {"protocol_id":protocol["protocol_id"],"parent_commit":protocol["parent_commit"],
              "input_sha256":hashes,"audit_counts":dict(audit),"shared_initialization":dict(shared),
              "additional_initialization":{m:dict(c) for m,c in initialization.items()},
              "methods":{m:dict(c) for m,c in counters.items()},"mechanism_cases":cases,
              "mechanism_audit":case_audit,"attacks":rejected,"ledger_sha256":digest.hexdigest(),
              "verdict":"Bounded joint Need/Release correctness and local primal/dual reuse checked; generic classical flow/proof composition matches. Extra initialization and complete state bytes are charged. No independent novelty or natural/full-cost superiority established."}
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"audit":dict(audit),"methods":{m:{k:c[k] for k in
                      ("cold_flow_requests","repair_searches","need_edge_visits","skipped_need_edges",
                       "state_sum_complete_bundle_bytes")} for m,c in counters.items()},
                      "ledger_sha256":digest.hexdigest(),"attacks":rejected},indent=2))


if __name__ == "__main__":
    main()
