"""Classical receipt-driven reference, not a new OACR algorithm.

Scope: initial cwd is the root; monitored single-level navigation and confirmed
file moves; no unobserved writers. Directory moves invalidate this fragment.
The producer receives only calls and receipts, never native backend objects.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Fact:
    kind: str
    content: str | None = None


class FileBindingReference:
    def __init__(self) -> None:
        self.root: tuple[str, ...] | None = None
        self.cwd: tuple[str, ...] | None = None
        self.facts: dict[tuple[str, ...], Fact] = {}
        self.unsupported: str | None = None
        self.events = 0

    @staticmethod
    def supported_name(value: Any) -> bool:
        return isinstance(value, str) and bool(re.fullmatch(r"[A-Za-z0-9_.-]+", value)) and value not in {".", ".."}

    def observe(self, method: str, args: dict[str, Any], receipt: Any) -> None:
        self.events += 1
        if self.unsupported:
            return
        if method == "pwd":
            value = receipt.get("current_working_directory") if isinstance(receipt, dict) else None
            if not isinstance(value, str) or not value.startswith("/"):
                self.unsupported = "unrecognized pwd receipt"
                return
            self.cwd = tuple(part for part in value.split("/") if part)
            if self.root is None:
                self.root = self.cwd  # Declared initialization starts at root.
            return
        if self.cwd is None:
            self.unsupported = "cwd not established"
            return
        if isinstance(receipt, dict) and "error" in receipt and method != "cat":
            # Only named fragment methods have inspected no-write error branches.
            if method not in {"cd", "mv", "touch", "mkdir", "echo"}:
                self.unsupported = "uninspected error branch"
            return
        if method == "cd":
            folder = args["folder"].rstrip("/") or "/"
            if folder == "/":
                self.cwd = self.root
            elif folder == "..":
                self.cwd = self.cwd[:-1]
            elif folder != "." and self.supported_name(folder):
                self.cwd += (folder,)
                self.facts[self.cwd] = Fact("directory")
            elif folder != ".":
                self.unsupported = "navigation outside fragment"
            return
        if method == "ls":
            # Listing is intentionally not treated as a file/type/value oracle.
            return
        if method in {"cat", "touch", "echo", "mkdir"}:
            name = args.get("dir_name") if method == "mkdir" else args.get("file_name")
            if method == "echo" and (name is None or name == ""):
                return
            if not self.supported_name(name):
                self.unsupported = "name outside fragment"
                return
            key = self.cwd + (name,)
            if method == "cat":
                if isinstance(receipt, dict) and "file_content" in receipt:
                    self.facts[key] = Fact("file", receipt["file_content"])
                elif receipt == {"error": f"cat: '{name}': No such file or directory"}:
                    self.facts[key] = Fact("absent")
                elif receipt == {"error": f"cat: '{name}': Is a directory"}:
                    self.facts[key] = Fact("directory")
                else:
                    self.unsupported = "unrecognized cat receipt"
            elif receipt is None:
                if method == "touch":
                    self.facts[key] = Fact("file", "")
                elif method == "mkdir":
                    self.facts[key] = Fact("directory")
                else:
                    self.facts[key] = Fact("file", args["content"])
            else:
                self.unsupported = "unrecognized write receipt"
            return
        if method == "mv":
            source, dest = args["source"], args["destination"]
            if not self.supported_name(source) or not self.supported_name(dest):
                self.unsupported = "move outside name fragment"
                return
            old = self.cwd + (source,)
            fact = self.facts.get(old)
            if fact is None or fact.kind != "file":
                self.unsupported = "successful move without confirmed file type"
                return
            if receipt == {"result": f"'{source}' moved to '{dest}/{source}'"}:
                target = self.cwd + (dest, source)
                self.facts[self.cwd + (dest,)] = Fact("directory")
            elif receipt == {"result": f"'{source}' moved to '{dest}'"}:
                target = self.cwd + (dest,)
            else:
                self.unsupported = "unrecognized move receipt"
                return
            self.facts[target] = fact
            self.facts[old] = Fact("absent")
            return
        self.unsupported = "operation outside declared fragment"

    def prepare_move(self, source: str) -> dict[str, str]:
        if self.unsupported or self.cwd is None:
            return {"status": "UNSUPPORTED"}
        fact = self.facts.get(self.cwd + (source,))
        if fact is None:
            return {"status": "NEED_EVIDENCE", "missing": "source type"}
        if fact.kind == "file":
            return {"status": "KNOWN_FILE"}
        return {"status": "UNSUPPORTED", "reason": fact.kind}

    def answer_cat(self, name: str) -> dict[str, Any]:
        if self.unsupported or self.cwd is None or not self.supported_name(name):
            return {"status": "UNSUPPORTED"}
        fact = self.facts.get(self.cwd + (name,))
        if fact is None:
            return {"status": "NEED_EVIDENCE"}
        if fact.kind == "file":
            value = {"file_content": fact.content}
        elif fact.kind == "directory":
            value = {"error": f"cat: '{name}': Is a directory"}
        else:
            value = {"error": f"cat: '{name}': No such file or directory"}
        return {"status": "KNOWN", "response": value}

    def snapshot(self) -> dict[str, Any]:
        return {
            "root": self.root, "cwd": self.cwd, "unsupported": self.unsupported,
            "events": self.events,
            "facts": {"/" + "/".join(k): asdict(v) for k, v in sorted(self.facts.items())},
        }

    def stored_bytes(self) -> int:
        return len(json.dumps(self.snapshot(), sort_keys=True, separators=(",", ":")).encode())
