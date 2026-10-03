"""Predeclared artificial mutation suite, independent source-body verifier.

Run from anywhere: python /absolute/path/run_mutation_suite.py --freeze
/absolute/path/freeze.json --output /absolute/path/result.json
No model/API calls, official task labels, benchmark database, or hidden state is
given to either maintainer. Auditor-only fresh clones independently replay the
original native function body to check every compiled prediction.
"""
from __future__ import annotations

import argparse
import ast
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time
from types import SimpleNamespace

from core import (Action, ClassicalAuthority, Confirmation, EffectBoundTransport,
                  Scope, encode)
from native_retail import (NativeRetailTools, Order, Product, User)

HERE = Path(__file__).resolve().parent
SCOPE = Scope("session-1", "u1")
ADDRESS = {"address1": "1 Example Street", "address2": "", "city": "Example",
           "country": "USA", "state": "CA", "zip": "00001"}


def fixture():
    # Synthetic public fixture input, not any benchmark task/database row.
    item = lambda ident, price, color: {"name": "shirt", "product_id": "p1",
        "item_id": ident, "price": price, "options": {"color": color}}
    variant = lambda ident, price, color: {"item_id": ident, "price": price,
        "options": {"color": color}, "available": True}
    return {"orders": {"#O": {"order_id": "#O", "user_id": "u1", "address": ADDRESS,
        "items": [item("a", 10.0, "black"), item("b", 20.0, "gray")],
        "status": "pending", "fulfillments": [],
        "payment_history": [{"transaction_type": "payment", "amount": 30.0,
                             "payment_method_id": "gift"}]}},
        "users": {"u1": {"user_id": "u1", "name": {"first_name": "Test", "last_name": "User"},
            "address": ADDRESS, "email": "test@example.invalid", "orders": ["#O"],
            "payment_methods": {"gift": {"id": "gift", "source": "gift_card", "balance": 100.0},
                "cc": {"id": "cc", "source": "credit_card", "brand": "visa", "last_four": "0000"}}}},
        "products": {"p1": {"name": "shirt", "product_id": "p1", "variants": {
            "a": variant("a", 10.0, "black"), "b": variant("b", 20.0, "gray"),
            "n1": variant("n1", 12.0, "blue"), "n2": variant("n2", 22.0, "red")}},
            "p2": {"name": "shoe", "product_id": "p2", "variants": {
                "q": variant("q", 9.0, "white")}}}}


def native(payload):
    return NativeRetailTools(SimpleNamespace(
        orders={k: Order.model_validate(deepcopy(v)) for k, v in payload["orders"].items()},
        users={k: User.model_validate(deepcopy(v)) for k, v in payload["users"].items()},
        products={k: Product.model_validate(deepcopy(v)) for k, v in payload["products"].items()}))


def state(tool):
    return {kind: {k: v.model_dump(mode="json") for k, v in getattr(tool.db, kind).items()}
            for kind in ["orders", "users", "products"]}


def source_effect(before, after, action):
    order_before, order_after = before["orders"][action.order_id], after["orders"][action.order_id]
    payment_id = action.payment_method_id
    owner = order_before["user_id"]
    payment_before = before["users"][owner]["payment_methods"][payment_id]
    payment_after = after["users"][owner]["payment_methods"][payment_id]
    # Independent frame audit: native modifies only declared target fields and
    # optional selected gift balance; existing payment entries must persist.
    if len(order_after["payment_history"]) != len(order_before["payment_history"])+1 or order_after["payment_history"][:-1] != order_before["payment_history"]:
        raise AssertionError("Native payment-history frame mismatch")
    frame_before,frame_after=deepcopy(before),deepcopy(after)
    for key in ["status","items","payment_history"]:
        frame_after["orders"][action.order_id][key]=frame_before["orders"][action.order_id][key]
    if payment_before["source"]=="gift_card":
        frame_after["users"][owner]["payment_methods"][payment_id]["balance"]=payment_before["balance"]
    if frame_before != frame_after:
        raise AssertionError("Native writes outside declared effect footprint")
    return {"order_id": action.order_id, "user_id": owner, "status": order_after["status"],
        "items": order_after["items"], "appended_payment": order_after["payment_history"][-1],
        "gift_card_delta": payment_after["balance"] - payment_before["balance"]
            if payment_before["source"] == "gift_card" else None}


def approved(payload, rows, difference, payment="gift"):
    """Independent explicit confirmation payload, never native verifier output.

    rows lists (old slot, new ID, approved price, approved color). This is the
    concrete declared effect contract; fixture expectations are public.
    """
    after = deepcopy(payload["orders"]["#O"]["items"])
    for slot, new, price, color in rows:
        after[slot].update(item_id=new, price=price, options={"color": color})
    pm = payload["users"]["u1"]["payment_methods"][payment]
    return {"order_id": "#O", "user_id": "u1", "status": "pending (item modified)",
        "items": after, "appended_payment": {"transaction_type": "payment" if difference > 0 else "refund",
        "amount": abs(difference), "payment_method_id": payment},
        "gift_card_delta": round(pm["balance"] - difference, 2) - pm["balance"]
            if pm["source"] == "gift_card" else None}


def cases():
    anchor = Action("#O", ("a",), ("n1",), "gift")
    def make(name, payload=None, action=None, effect=None, expected=True, **kw):
        p = deepcopy(payload or fixture())
        return {"name": name, "payload": p, "action": action or anchor,
            "anchor": kw.pop("anchor", anchor),
            "effect": effect if effect is not None else approved(fixture(), [(0, "n1", 12.0, "blue")], 2.0),
            "expected_admitted": expected, **kw}
    yield make("single_write")
    yield make("exact_intent_version_cache", repeat_prepare=True)
    p = fixture(); p["products"]["p1"]["variants"]["n1"].update(price=15.0, options={"color": "green"})
    p["products"]["p1"]["variants"]["n2"].update(price=15.0, options={"color": "green"})
    pair_anchor = Action("#O", ("a", "b"), ("n1", "n2"), "gift")
    yield make("equivalent_reordered_pair", p, Action("#O", ("b", "a"), ("n2", "n1"), "gift"),
               approved(p, [(0, "n1", 15.0, "green"), (1, "n2", 15.0, "green")], 0.0), anchor=pair_anchor)
    yield make("terminal_variant_violates_pair_intent", action=pair_anchor,
               effect=approved(fixture(), [(0, "n1", 12.0, "blue"), (1, "n2", 22.0, "red")], 4.0), expected=False)
    yield make("sequential_collision_violates_simultaneous_intent", action=Action("#O", ("a", "b"), ("b", "n1"), "gift"),
               effect=approved(fixture(), [(0, "b", 20.0, "gray"), (1, "n1", 12.0, "blue")], 2.0), expected=False)
    yield make("payment_id_changed", action=Action("#O", ("a",), ("n1",), "cc"), expected=False)
    yield make("confirmation_session_mismatch", query_scope=Scope("session-2", "u1"), expected=False)
    yield make("owner_scope_mismatch", confirmation_scope=Scope("session-1", "u2"), query_scope=Scope("session-1", "u2"), expected=False)
    p=fixture(); p["products"]["p1"]["variants"]["n1"]["available"]=False
    yield make("unavailable_variant", p, expected=False)
    yield make("wrong_product_variant", action=Action("#O", ("a",), ("q",), "gift"), expected=False)
    p=fixture(); p["users"]["u1"]["payment_methods"]["gift"]["balance"]=1.0
    yield make("insufficient_gift_balance", p, expected=False)
    yield make("excess_duplicate_count", action=Action("#O", ("a", "a"), ("n1", "n1"), "gift"), expected=False)
    p=fixture(); p["orders"]["#O"]["items"][1]=deepcopy(p["orders"]["#O"]["items"][0])
    yield make("valid_duplicate_count", p, Action("#O", ("a", "a"), ("n1", "n1"), "gift"),
               approved(p, [(0, "n1", 12.0, "blue"), (1, "n1", 12.0, "blue")], 4.0))
    yield make("same_old_new", action=Action("#O", ("a",), ("a",), "gift"), expected=False)
    yield make("list_cardinality_mismatch", action=Action("#O", ("a", "b"), ("n1",), "gift"), expected=False)
    yield make("unrelated_observed_user_address", refresh="address")
    yield make("observed_variant_price_changed", refresh="price", expected=False)
    yield make("uncertified_interference_window", interference=True, expected=False)
    yield make("stale_epoch_even_with_serial_window", interference=True, serial_again=True, expected=False)
    yield make("reobserve_then_serial_window", interference=True, serial_again=True, reobserve=True)
    yield make("incomplete_batch_confirmation", closed=False, expected=False)
    yield make("consumed_success_not_reusable", completion="success", expected=False)
    yield make("uncertain_write_not_retried", completion="uncertain", expected=False)
    yield make("audited_no_write_failure_not_consumed", completion="no_write")
    yield make("new_confirmation_does_not_restore_consumed_guard", completion="success", reconfirm=True, expected=False)
    yield make("no_confirmation", confirm=False, expected=False)
    yield make("missing_product_observation", omit_product=True, expected=False)
    p=fixture(); p["users"]["u1"]["orders"]=[]
    yield make("policy_order_membership_mismatch", p, expected=False)
    p=fixture(); p["orders"]["#O"]["status"]="pending (item modified)"
    yield make("pending_substring_not_strict_guard", p, expected=False)
    p=fixture(); p["users"]["u1"]["payment_methods"].pop("gift")
    yield make("missing_payment_method", p, expected=False)
    yield make("empty_list_source_boundary", action=Action("#O", (), (), "gift"),
               effect=approved(fixture(), [], 0.0))


def observe_visible(method, native_tool, omit_product=False):
    receipts = [("order", "#O", native_tool.get_order_details("#O")),
                ("user", "u1", native_tool.get_user_details("u1"))]
    if not omit_product:
        receipts.append(("product", "p1", native_tool.get_product_details("p1")))
    total = 0
    for kind, key, value in receipts:
        receipt = value.model_dump(mode="json")
        method.observe(kind, key, receipt)
        total += len(encode(receipt).encode())
    return len(receipts), total


def verify_capsule(freeze):
    config = json.loads(freeze.read_text())
    for name, expected in config["implementation_sha256"].items():
        actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError("Frozen implementation mismatch: " + name)
    manifest = json.loads((HERE / "source_manifest.json").read_text())
    tree = ast.parse((HERE / "native_retail.py").read_text())
    cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == "NativeRetailTools")
    methods = {x.name:x for x in cls.body if isinstance(x, ast.FunctionDef)}
    for entry in manifest["methods"]:
        function = methods[entry["name"]]
        body_hash = hashlib.sha256(ast.dump(ast.Module(body=function.body, type_ignores=[]), include_attributes=False).encode()).hexdigest()
        if body_hash != entry["ast_body_sha256"]:
            raise ValueError("Upstream method body changed: " + entry["name"])
    return config, manifest


def run():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args=parser.parse_args()
    freeze, manifest = verify_capsule(args.freeze)
    rows=[]; total_native_writes=0; first=time.perf_counter_ns()
    for case in cases():
        outputs={}
        for name, cls in [("classical", ClassicalAuthority), ("candidate", EffectBoundTransport)]:
            native_tool=native(case["payload"])
            method=cls(); scope=case.get("query_scope",SCOPE)
            native_reads, receipt_bytes=observe_visible(method,native_tool,case.get("omit_product",False))
            # Explicit declared synthetic protocol: no external actors may write
            # between these READ receipts and the immediate audited decision.
            # This is harness scope, never inferred from absence of updates.
            method.observed.certify_serial_window()
            conf=Confirmation("confirm-1",case.get("confirmation_scope",SCOPE),"#O",case["anchor"],case["effect"],case.get("closed",True))
            if case.get("confirm",True): method.confirm(conf)
            if case.get("completion"):
                method.observe_write_completion(SCOPE,"#O",case["completion"])
            if case.get("reconfirm"): method.confirm(conf)
            if case.get("refresh"):
                if case["refresh"]=="address":
                    native_tool.db.users["u1"].address.address1="2 Example Street"
                    receipt=native_tool.get_user_details("u1").model_dump(mode="json")
                    method.observe("user","u1",receipt)
                else:
                    native_tool.db.products["p1"].variants["n1"].price=13.0
                    receipt=native_tool.get_product_details("p1").model_dump(mode="json")
                    method.observe("product","p1",receipt)
                native_reads+=1
                receipt_bytes+=len(encode(receipt).encode())
            if case.get("interference"):
                method.observed.open_interference()
                if case.get("reobserve"):
                    n,b=observe_visible(method,native_tool);native_reads+=n;receipt_bytes+=b
                if case.get("serial_again"): method.observed.certify_serial_window()
            start=time.process_time_ns(); decision=method.prepare(scope,case["action"],"confirm-1")
            elapsed=time.process_time_ns()-start
            if case.get("repeat_prepare"):
                repeated=method.prepare(scope,case["action"],"confirm-1")
                if repeated.admitted != decision.admitted or not repeated.cache_hit:
                    raise AssertionError("Exact/version cache did not preserve decision")
            # Independent auditor sees full constructed fixture. Neither method
            # receives this fresh clone or before/after data.
            probe=native(state(native_tool));before=state(probe);error=None
            try:
                probe.modify_pending_order_items(**case["action"].native_args())
            except ValueError as exc:
                error=str(exc)
            total_native_writes+=1
            after=state(probe); actual_effect=source_effect(before,after,case["action"]) if error is None else None
            summary=decision.obligation
            prediction_checked=summary is not None and summary.native_guard not in {
                "needs_observation","uncertified_interference_window","scope_owner_mismatch", "scope_order_membership_mismatch"}
            if prediction_checked:
                if summary.native_guard=="pass":
                    if error is not None or summary.effect != actual_effect:
                        raise AssertionError((case["name"],name,"native prediction mismatch",summary,actual_effect,error))
                elif summary.native_guard != error or before != after:
                    raise AssertionError((case["name"],name,"guard/no-write mismatch",summary.native_guard,error))
            if decision.admitted and (error is not None or actual_effect != conf.approved_effect):
                raise AssertionError((case["name"],name,"unsound authority admission"))
            if decision.admitted != case["expected_admitted"]:
                raise AssertionError((case["name"],name,"unexpected declared fixture decision",decision))
            outputs[name]={"decision":asdict(decision),"work":dict(method.work),"state_bytes":method.state_bytes(),
                "state_hash":hashlib.sha256(encode(method.snapshot()).encode()).hexdigest(),
                "native_guard_prediction_checked":prediction_checked,"native_error":error,
                "native_probe_effect":actual_effect,"public_read_calls":native_reads,"public_receipt_bytes":receipt_bytes,
                "prepare_cpu_ns":elapsed,"extensional_transport_beyond_anchor_syntax":int(decision.transported),
                "serial_window_provided_by_declared_harness_protocol":True}
        a,b=outputs["classical"],outputs["candidate"]
        equal=all(a[k]==b[k] for k in ["decision","work","state_bytes","state_hash","native_guard_prediction_checked",
                                      "native_error","native_probe_effect","public_read_calls","public_receipt_bytes"])
        if not equal: raise AssertionError((case["name"],"methods did not match"))
        rows.append({"name":case["name"],"expected_admitted":case["expected_admitted"],"methods":outputs,
                     "same_guarantee_and_counted_resources":equal})
    result={"protocol":"authority_transport_source_body_mutation_suite_v1","commit":manifest["commit"],
        "fixture_count":len(rows),"source_body_native_probe_calls":total_native_writes,
        "admitted_each":sum(r["expected_admitted"] for r in rows),
        "guard_effect_native_mismatches":0,"unsound_admissions":0,"all_counted_resources_matched":True,
        "independent_kernel_claim":"retired_in_this_exact_effect_fragment",
        "reason":"Candidate effect-bound transport is the same compiled predicate allowed to the strong classical control.",
        "scientific_scope":"synthetic fixtures/source-body native audit; no full tau2 runner, official tasks, model system, theorem or global priority claim",
        "guarantee_scope":"explicit structured exact-effect confirmation + declared serial no-interference interval; unknown interference invalidates epochs; no policy/effect guarantee across hidden updates",
        "cost_scope":"serialized retained facts/grants/ledger/cache, shared implementation/capsule bytes, receipt bytes, READ/probe counts, deterministic work counters; CPU/wall times measured separately, not asserted equal",
        "shared_costs":{"source_capsule_bytes":sum((HERE/f).stat().st_size for f in ["native_retail.py","source_manifest.json"]),
            "implementation_bytes":{f:(HERE/f).stat().st_size for f in freeze["implementation_sha256"]}},
        "freeze":freeze,"wall_time_ns":time.perf_counter_ns()-first,"cases":rows}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in {"cases","freeze"}},ensure_ascii=False,indent=2))


if __name__=="__main__": run()
