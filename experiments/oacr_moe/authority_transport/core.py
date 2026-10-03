"""Observable-prefix authority adapter, with a matched classical control.

The fixed guard/effect summary is hand implemented from reviewed native source,
then audited against the independent source-body verifier. It is not an automatic
Python semantics extractor, natural-language parser, or official tau2 agent.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import asdict, dataclass
import hashlib
import json


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(encode(value).encode()).hexdigest()


@dataclass(frozen=True)
class Scope:
    session: str
    user_id: str


@dataclass(frozen=True)
class Action:
    order_id: str
    item_ids: tuple[str, ...]
    new_item_ids: tuple[str, ...]
    payment_method_id: str

    def native_args(self):
        return {"order_id": self.order_id, "item_ids": list(self.item_ids),
                "new_item_ids": list(self.new_item_ids),
                "payment_method_id": self.payment_method_id}


@dataclass(frozen=True)
class Confirmation:
    """Explicit structured confirmation; no implicit NL interpretation.

    approved_effect is independently supplied by the fixture/user. It covers
    final order item fields, status, appended payment, and gift-card delta.
    anchor records the concrete initially discussed call. Equality of actual
    approved effects, not syntax alone, is the declared authority contract.
    """
    confirmation_id: str
    scope: Scope
    order_id: str
    anchor: Action
    approved_effect: dict
    all_current_changes_confirmed: bool = True


@dataclass
class Fact:
    value: dict
    version: int
    epoch: int


@dataclass
class Obligation:
    native_guard: str
    effect: dict | None
    supports: tuple[tuple[str, str, int], ...]
    work: int
    missing: tuple[str, ...] = ()


@dataclass
class Decision:
    admitted: bool
    reason: str
    obligation: Obligation | None
    work: int
    transported: bool = False
    cache_hit: bool = False


class Observations:
    """Only copied public READ receipts, tagged by visible observation epoch.

    open_interference is an explicit protocol event, never a hidden update feed.
    Without a certified no-interference interval this adapter cannot issue a
    sound current-state admission. No timestamp/unchanged-history inference.
    """
    def __init__(self):
        self.facts = {}
        self.epoch = 0
        self.window_certified = False
        self.reads = 0

    def observe(self, kind, key, receipt):
        receipt = deepcopy(receipt)
        old = self.facts.get((kind, key))
        version = 1 if old is None else old.version + (old.value != receipt)
        self.facts[(kind, key)] = Fact(receipt, version, self.epoch)
        self.reads += 1

    def get(self, kind, key):
        fact = self.facts.get((kind, key))
        return fact if fact is not None and fact.epoch == self.epoch else None

    def open_interference(self):
        self.epoch += 1
        self.window_certified = False

    def certify_serial_window(self):
        """Called only when the declared execution protocol excludes interference."""
        self.window_certified = True


def compile_obligation(observed: Observations, scope: Scope, action: Action):
    """Fixed source-faithful guard/effect summary; no backend instance input."""
    work = 0
    supports = []

    def fact(kind, key):
        nonlocal work
        work += 1
        value = observed.get(kind, key)
        if value is not None:
            supports.append((kind, key, value.version))
            return value.value
        return None

    def fail(reason, missing=()):
        return Obligation(reason, None, tuple(supports), work, missing)

    if not observed.window_certified:
        return fail("uncertified_interference_window")
    order = fact("order", action.order_id)
    if order is None:
        return fail("needs_observation", ("order:" + action.order_id,))
    if order["user_id"] != scope.user_id:
        return fail("scope_owner_mismatch")
    if order["status"] != "pending":
        return fail("Non-pending order cannot be modified")
    user = fact("user", scope.user_id)
    if user is None:
        return fail("needs_observation", ("user:" + scope.user_id,))
    if action.order_id not in user["orders"]:
        return fail("scope_order_membership_mismatch")
    all_ids = [item["item_id"] for item in order["items"]]
    work += len(all_ids)
    # Use source count semantics, including duplicate IDs, and the source order.
    for item_id in action.item_ids:
        work += len(action.item_ids) + len(all_ids)
        if action.item_ids.count(item_id) > all_ids.count(item_id):
            return fail(f"{item_id} not found")
    if len(action.item_ids) != len(action.new_item_ids):
        return fail("The number of items to be exchanged should match")
    diff_price = 0
    last_variant = None
    for item_id, new_id in zip(action.item_ids, action.new_item_ids):
        work += 1
        if item_id == new_id:
            return fail("The new item id should be different from the old item id")
        item = next((i for i in order["items"] if i["item_id"] == item_id), None)
        work += len(order["items"])
        if item is None:
            return fail(f"Item {item_id} not found")
        product = fact("product", item["product_id"])
        if product is None:
            return fail("needs_observation", ("product:" + item["product_id"],))
        if new_id not in product["variants"]:
            return fail("Variant not found")
        last_variant = product["variants"][new_id]
        if not last_variant["available"]:
            return fail(f"New item {new_id} not found or available")
        diff_price += last_variant["price"] - item["price"]
    work += 1
    payment = user["payment_methods"].get(action.payment_method_id)
    if payment is None:
        return fail("Payment method not found")
    if payment["source"] == "gift_card" and payment["balance"] < diff_price:
        return fail("Insufficient gift card balance to pay for the new item")
    after_items = deepcopy(order["items"])
    for item_id, new_id in zip(action.item_ids, action.new_item_ids):
        work += len(after_items)
        item = next((i for i in after_items if i["item_id"] == item_id), None)
        if item is None:
            # The summary exposes this path rather than treating all exceptions
            # as no-write. The suite checks that supported inputs match native.
            return fail("post_write_exception:Item " + item_id + " not found")
        item["item_id"] = new_id
        # Deliberately retain upstream terminal-variant semantics.
        item["price"] = last_variant["price"]
        item["options"] = deepcopy(last_variant["options"])
    event = {"transaction_type": "payment" if diff_price > 0 else "refund",
             "amount": abs(diff_price), "payment_method_id": action.payment_method_id}
    gift_delta = (round(payment["balance"] - diff_price, 2) - payment["balance"]
                  if payment["source"] == "gift_card" else None)
    effect = {"order_id": action.order_id, "user_id": order["user_id"],
              "status": "pending (item modified)", "items": after_items,
              "appended_payment": event, "gift_card_delta": gift_delta}
    return Obligation("pass", effect, tuple(sorted(set(supports))), work)


class AuthorityBase:
    def __init__(self):
        self.observed = Observations()
        self.confirmations = {}
        self.ledger = {}  # (session, user, order) -> ready/spent/uncertain
        self.cache = {}
        self.work = Counter()

    def key(self, scope, order_id):
        return (scope.session, scope.user_id, order_id)

    def confirm(self, confirmation):
        self.confirmations[confirmation.confirmation_id] = deepcopy(confirmation)
        self.ledger.setdefault(self.key(confirmation.scope, confirmation.order_id), "ready")
        self.work["confirmation_writes"] += 1

    def observe(self, kind, key, receipt):
        self.observed.observe(kind, key, receipt)
        self.work["read_receipts"] += 1

    def prepare(self, scope, action, confirmation_id):
        self.work["prepare_calls"] += 1
        conf = self.confirmations.get(confirmation_id)
        if conf is None:
            return Decision(False, "no_confirmation", None, 1)
        if conf.scope != scope or conf.order_id != action.order_id:
            return Decision(False, "confirmation_scope_mismatch", None, 1)
        if not conf.all_current_changes_confirmed:
            return Decision(False, "scope_not_closed", None, 1)
        state = self.ledger[self.key(scope, action.order_id)]
        if state != "ready":
            return Decision(False, "authority_" + state, None, 1)
        # Exact-intent/version cache is available to BOTH methods. Semantic
        # equivalence fallback prevents an intentionally weak classical control.
        exact = digest([asdict(scope), asdict(action)])
        cached = self.cache.get(exact)
        if cached is not None and self.observed.window_certified and all(
            (f := self.observed.get(kind, key)) is not None and f.version == version
            for kind, key, version in cached.supports
        ):
            obligation, cache_hit = cached, True
            query_work = 1 + len(cached.supports)
        else:
            obligation = compile_obligation(self.observed, scope, action)
            cache_hit = False
            query_work = 1 + obligation.work
            if obligation.native_guard == "pass":
                self.cache[exact] = obligation
                self.work["cache_writes"] += 1
        self.work["guard_lookup_visits"] += query_work
        if obligation.native_guard != "pass":
            return Decision(False, obligation.native_guard, obligation, query_work, cache_hit=cache_hit)
        admitted = self.authority_matches(conf, obligation)
        self.work["effect_comparisons"] += 1
        return Decision(admitted, "admitted" if admitted else "effect_not_confirmed",
                        obligation, query_work + 1,
                        admitted and action != conf.anchor, cache_hit)

    def authority_matches(self, confirmation, obligation):
        raise NotImplementedError

    def observe_write_completion(self, scope, order_id, outcome):
        """Receipt status, not speculative prepare, updates affine eligibility.

        Only audited no-write native guard failures can be marked no_write.
        Transport/network exceptions are uncertain, never safe retries.
        """
        if outcome not in {"success", "no_write", "uncertain"}:
            raise ValueError(outcome)
        if outcome != "no_write":
            self.ledger[self.key(scope, order_id)] = "spent" if outcome == "success" else "uncertain"
        self.work["completion_writes"] += 1

    def snapshot(self):
        return {"facts": [(kind, key, asdict(f)) for (kind, key), f in sorted(self.observed.facts.items())],
                "epoch": self.observed.epoch, "window_certified": self.observed.window_certified,
                "confirmations": [asdict(v) for _, v in sorted(self.confirmations.items())],
                "ledger": [(key, value) for key, value in sorted(self.ledger.items())],
                "cache": [(key, asdict(value)) for key, value in sorted(self.cache.items())]}

    def state_bytes(self):
        return len(encode(self.snapshot()).encode())


class ClassicalAuthority(AuthorityBase):
    """Exact-intent/version/affine control plus compiled semantic fallback.

    The declared authority is extensional effect equality. A correct strong
    classical control can evaluate that predicate for nonidentical calls too.
    Omitting this fallback would artificially lower its admitted-action coverage.
    """
    def authority_matches(self, confirmation, obligation):
        return obligation.effect == confirmation.approved_effect


class EffectBoundTransport(AuthorityBase):
    """Candidate effect-bound transport, deliberately unpromoted.

    In this frozen exact-effect fragment its proposed transport condition is
    exactly the classical compiled authority predicate. Equality of guarantees
    and resources here retires the candidate's independent-kernel claim.
    """
    def authority_matches(self, confirmation, obligation):
        return obligation.effect == confirmation.approved_effect
