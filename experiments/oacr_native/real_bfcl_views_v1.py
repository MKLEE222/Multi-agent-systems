"""Observable query views on real BFCL prefixes; no hidden initial state.

IndexedViews is a classical incremental materialized-view control. DemandViews
is a classical backward evidence compiler, an unpromoted OACR execution candidate.
Both share inspected native operation summaries, not private backend objects.
Unknown/directory transfers fall back to global invalidation and fresh navigation
namespaces because native directory copying/moving is not ordinary OS semantics.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

READS = {"cat", "grep", "wc", "sort", "tail", "diff"}
WRITES = {"touch", "echo", "mkdir", "mv", "cp", "rm", "rmdir"}
FS_METHODS = READS | WRITES | {"cd", "pwd", "ls", "find", "du"}
SUCCESS_FIELD = {"cat": "file_content", "grep": "matching_lines", "wc": "count",
                 "sort": "sorted_content", "tail": "last_lines", "diff": "diff_lines"}


def operands(method: str, args: dict) -> tuple[str, ...]:
    return ((args["file_name1"], args["file_name2"]) if method == "diff"
            else (args["file_name"],))


def evaluate_read(method: str, args: dict, contents: list[str]) -> dict:
    """Inspected BFCL semantics, independently checked by the unmodified backend."""
    s = contents[0]
    if method == "cat":
        return {"file_content": s}
    if method == "grep":
        return {"matching_lines": [x for x in s.splitlines() if args["pattern"] in x]}
    if method == "sort":
        return {"sorted_content": "\n".join(sorted(s.splitlines()))}
    if method == "tail":
        lines = s.splitlines()
        n = min(args.get("lines", 10), len(lines))
        return {"last_lines": "\n".join(lines[-n:])}
    if method == "wc":
        mode = args.get("mode", "l")
        if mode not in {"l", "w", "c"}:
            return {"error": f"wc: invalid mode '{mode}'"}
        count = len(s.splitlines()) if mode == "l" else len(s.split()) if mode == "w" else len(s)
        return {"count": count, "type": {"l": "lines", "w": "words", "c": "characters"}[mode]}
    return {"diff_lines": "\n".join(f"- {a}\n+ {b}" for a, b in
                                   zip(s.splitlines(), contents[1].splitlines()) if a != b)}


def params(method: str, args: dict) -> str:
    d = {k: v for k, v in args.items() if k not in {"file_name", "file_name1", "file_name2"}}
    if method == "wc":
        d.setdefault("mode", "l")
    if method == "tail":
        d.setdefault("lines", 10)
    return json.dumps(d, sort_keys=True)


class ObservableNamespace:
    """Logical names from visible calls. IDs here are not native inodes."""
    def __init__(self):
        self.cwd = ("ROOT",)  # Public BFCL initialization protocol, not root data.
        self.kinds = {}
        self.conservative = False
        self.serial = 0
        self.navigation = []
        self.work = 0

    def path(self, name):
        return self.cwd + (name,)

    def event(self, index: int, method: str, args: dict, receipt: Any) -> dict:
        self.work += 1
        e = {"index": index, "method": method, "args": args, "cwd": self.cwd,
             "effect": "none", "barrier": False}
        error = isinstance(receipt, dict) and "error" in receipt
        exception = isinstance(receipt, str) and receipt.startswith("Error during execution:")
        if method in READS and isinstance(receipt, dict) and SUCCESS_FIELD[method] in receipt:
            for name in operands(method, args):
                self.kinds[self.path(name)] = "file"
            e["read_success"] = True
        if method == "cd" and not error and not exception:
            self.navigation.append(index)
            folder = args["folder"].rstrip("/") or "/"
            if folder == ".":
                pass
            elif self.conservative:
                self.serial += 1
                self.cwd = ("UNKNOWN_LOCATION", str(self.serial))
            elif folder == "/":
                self.cwd = ("ROOT",)
            elif folder == "..":
                self.cwd = self.cwd[:-1]
            else:
                self.cwd += (folder,)
                self.kinds[self.cwd] = "directory"
        if method not in WRITES or error:
            return e
        # An exception is distinct from an inspected no-write error receipt.
        if exception:
            self.conservative = True
            self.kinds.clear()
            e["barrier"] = True
            return e
        if method == "echo" and not args.get("file_name"):
            return e
        if self.conservative:
            e["barrier"] = True
            self.kinds.clear()
        if method in {"touch", "echo"} and receipt is None:
            e.update(effect="set", target=self.path(args["file_name"]),
                     value="empty" if method == "touch" else "argument")
            self.kinds[e["target"]] = "file"
        elif method == "mkdir" and receipt is None:
            e.update(effect="remove", target=self.path(args["dir_name"]))
            self.kinds[e["target"]] = "directory"
        elif method in {"rm", "rmdir"} and isinstance(receipt, dict) and "result" in receipt:
            name = args["file_name"] if method == "rm" else args["dir_name"]
            target = self.path(name)
            e.update(effect="remove", target=target)
            self.work += len(self.kinds)
            self.kinds = {p: k for p, k in self.kinds.items() if p[:len(target)] != target}
        elif method in {"mv", "cp"} and isinstance(receipt, dict) and "result" in receipt:
            source, dest = args["source"], args["destination"]
            src = self.path(source)
            verb = "moved" if method == "mv" else "copied"
            target = self.path(dest) + (source,) if receipt["result"] == f"'{source}' {verb} to '{dest}/{source}'" else self.path(dest)
            if self.kinds.get(src) != "file":
                self.conservative = True
                self.kinds.clear()
                e["barrier"] = True
            else:
                e.update(effect="transfer", source=src, target=target, move=method == "mv")
                self.kinds[target] = "file"
                if method == "mv":
                    self.kinds.pop(src, None)
        return e

    def snapshot(self):
        return {"cwd": self.cwd, "conservative": self.conservative, "serial": self.serial,
                "navigation": self.navigation,
                "kinds": [(p, k) for p, k in sorted(self.kinds.items())]}


def content_at(history: list[dict], ref: tuple[int, str]) -> str:
    i, field = ref
    if field == "empty":
        return ""
    if field == "argument":
        return history[i]["args"]["content"]
    return history[i]["receipt"]["file_content"]


@dataclass
class Answer:
    response: dict | None
    evidence: tuple[int, ...] = ()
    work: int = 0


class IndexedViews:
    """Classical effect-indexed value/query materialization with visible provenance."""
    def __init__(self, history):
        self.history = history
        self.ns = ObservableNamespace()
        self.values = {}  # path -> (raw value reference, lineage)
        self.views = {}   # path -> query -> (receipt index, lineage)
        self.path_index = {}  # prefix -> affected materialized paths
        self.exact_pairs = {}  # Conservatively invalidated on every write.
        self.work = 0

    def observe(self, index, method, args, receipt):
        e = self.ns.event(index, method, args, receipt)
        self.work += 1
        if method in WRITES and e["effect"] != "none" or e["barrier"]:
            self.exact_pairs.clear()
        if e["barrier"]:
            self.work += len(self.values) + sum(map(len, self.views.values())) + len(self.path_index)
            self.values.clear()
            self.views.clear()
            self.path_index.clear()
        effect = e["effect"]
        if effect == "set":
            self._delete(e["target"])
            self.values[e["target"]] = ((index, e["value"]), (index,))
            self._register(e["target"])
        elif effect == "remove":
            self._delete(e["target"])
        elif effect == "transfer":
            src, dst = e["source"], e["target"]
            value = self.values.get(src)
            views = dict(self.views.get(src, {}))
            self.work += len(views) + 1
            self._delete(dst)
            if value:
                self.values[dst] = (value[0], value[1] + (index,))
            if views:
                self.views[dst] = {key: (ref, proof + (index,)) for key, (ref, proof) in views.items()}
            if value or views:
                self._register(dst)
            if e["move"]:
                self._delete(src)
        if e.get("read_success"):
            if method == "cat":
                self.values[e["cwd"] + (args["file_name"],)] = ((index, "receipt"), (index,))
            if method != "diff":
                path = e["cwd"] + (args["file_name"],)
                self.views.setdefault(path, {})[(method, params(method, args))] = (index, (index,))
                self._register(path)
            else:
                self.exact_pairs[(e["cwd"], json.dumps(args, sort_keys=True))] = index

    def _register(self, path):
        for n in range(1, len(path) + 1):
            self.path_index.setdefault(path[:n], set()).add(path)
            self.work += 1

    def _delete(self, target):
        affected = list(self.path_index.get(target, ()))
        self.work += 1
        for path in affected:
            self.work += 1 + len(self.views.get(path, {}))
            self.values.pop(path, None)
            self.views.pop(path, None)
            for n in range(1, len(path) + 1):
                prefix = path[:n]
                self.path_index[prefix].discard(path)
                if not self.path_index[prefix]:
                    self.path_index.pop(prefix)
                self.work += 1

    def prepare(self, method, args):
        ps = [self.ns.path(n) for n in operands(method, args)]
        facts = [self.values.get(p) for p in ps]
        if all(facts):
            proof = tuple(sorted(set(self.ns.navigation).union(*(f[1] for f in facts))))
            return Answer(evaluate_read(method, args, [content_at(self.history, f[0]) for f in facts]), proof, len(ps))
        if method != "diff":
            v = self.views.get(ps[0], {}).get((method, params(method, args)))
            if v:
                return Answer(self.history[v[0]]["receipt"], tuple(sorted(set(v[1]) | set(self.ns.navigation))), 1)
        else:
            i = self.exact_pairs.get((self.ns.cwd, json.dumps(args, sort_keys=True)))
            if i is not None:
                return Answer(self.history[i]["receipt"], tuple(sorted({i} | set(self.ns.navigation))), 1)
        return Answer(None, work=len(ps))

    def snapshot(self):
        return {"namespace": self.ns.snapshot(), "values": list(self.values.items()),
                "views": [(p, list(v.items())) for p, v in self.views.items()],
                "path_index": [(p, sorted(v)) for p, v in self.path_index.items()],
                "pairs": list(self.exact_pairs.items())}


class DemandViews:
    """Backward operation-demand transport; no forward value/view table."""
    def __init__(self, history):
        self.history = history
        self.ns = ObservableNamespace()
        self.events = []
        self.work = 0

    def observe(self, index, method, args, receipt):
        e = self.ns.event(index, method, args, receipt)
        # Raw arguments/receipts already live in the common charged archive.
        e.pop("args")
        self.events.append(e)
        self.work += 1

    def _resolve(self, path, method, args):
        chain = []
        work = 0
        for e in reversed(self.events):
            work += 1
            i, kind = e["index"], e["effect"]
            h = self.history[i]
            if e.get("read_success") and h["method"] != "diff":
                observed = e["cwd"] + (h["args"]["file_name"],)
                if observed == path:
                    if h["method"] == "cat":
                        return ("content", (i, "receipt"), tuple(chain + [i]), work)
                    if h["method"] == method and params(method, args) == params(method, h["args"]):
                        return ("response", i, tuple(chain + [i]), work)
            if kind == "set" and e["target"] == path:
                return ("content", (i, e["value"]), tuple(chain + [i]), work)
            if kind == "transfer":
                if e["target"] == path:
                    path = e["source"]
                    chain.append(i)
                elif e["move"] and path[:len(e["source"])] == e["source"]:
                    return ("unknown", None, (), work)
            elif kind in {"set", "remove"} and path[:len(e["target"])] == e["target"]:
                return ("unknown", None, (), work)
            if e["barrier"]:
                return ("unknown", None, (), work)
        return ("unknown", None, (), work)

    def prepare(self, method, args):
        ps = [self.ns.path(n) for n in operands(method, args)]
        pair_work = 0
        if method == "diff":
            # Exact repeated diff is valid across read/navigation events only.
            for e in reversed(self.events):
                pair_work += 1
                h = self.history[e["index"]]
                if e["barrier"] or e["effect"] != "none":
                    break
                if h["method"] == "diff" and e.get("read_success") and e["cwd"] == self.ns.cwd and h["args"] == args:
                    proof = tuple(sorted(set(self.ns.navigation) | {e["index"]}))
                    return Answer(h["receipt"], proof, pair_work)
        results = [self._resolve(p, "cat" if method == "diff" else method, args) for p in ps]
        work = pair_work + sum(r[3] for r in results)
        if any(r[0] == "unknown" for r in results):
            return Answer(None, work=work)
        proof = tuple(sorted(set(self.ns.navigation).union(*(r[2] for r in results))))
        if len(results) == 1 and results[0][0] == "response":
            return Answer(self.history[results[0][1]]["receipt"], proof, work)
        return Answer(evaluate_read(method, args, [content_at(self.history, r[1]) for r in results]), proof, work)

    def snapshot(self):
        return {"namespace": self.ns.snapshot(), "events": self.events}
