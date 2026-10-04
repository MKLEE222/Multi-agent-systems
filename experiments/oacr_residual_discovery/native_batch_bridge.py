#!/usr/bin/env python3
"""Frozen train-only residual discovery via the native actor file mailbox.

``--prepare`` reads the train manifest and public implementation files only. It
does not instantiate AppWorld. Selection identities, rendered prompts, complete
requests and receipts are private local artifacts; public results contain only
hashes, counts and fixed vocabulary outcomes. No OACR control is applied.
"""
from __future__ import annotations

import argparse
import ast
from contextlib import contextmanager, redirect_stderr, redirect_stdout
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import threading
import time
import traceback
from typing import Any, Callable


AUTHOR_SHA = "9f3e92155345a9159f3a8b25abc334eeca05b545"
PROTOCOL = "oacr_residual_dev24_v1"
PROTOCOL_COMMIT = "9276445530198098e986f72b822843a7bb3bec9f"
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
TASK_COUNT = 24
REQUEST_BUDGET = 40
CODE_TIMEOUT = 20
ACTOR_TIMEOUT = 1200
GRADE_TIMEOUT = 120
PAGE_CHARS = 2000
ENVIRONMENT_SEED = 123
MODEL = "inherited ChatGPT subagent backend; exact version, seed, tokens and billing not exposed"
EXPOSURE_FREEZE = REPO_ROOT / "experiments/oacr_moe/subagent_actor/freeze.json"
PROTOCOL_PATH = REPO_ROOT / "docs/OACR_RESIDUAL_DISCOVERY_PROTOCOL_2026-10-04.md"
EXECUTION_PROTOCOL_PATH = REPO_ROOT / "docs/OACR_RESIDUAL_DEV24_EXECUTION_PROTOCOL_2026-10-04.md"
ACTOR_INSTRUCTIONS_PATH = HERE / "actor_instructions.md"
HIGH_COST_THRESHOLDS = {"native_api_calls": 100, "execute_requests": 20,
                        "generated_native_receipt_bytes": 100000, "actor_elapsed_seconds": 600}
SOURCE_FILES = {
    "author_prompt": "experiments/prompts/appworld_react_generator_prompt.txt",
    "initial_playbook": "experiments/playbooks/appworld_initial_playbook.txt",
    "evaluator": "src/appworld/evaluator.py",
    "environment": "src/appworld/environment.py",
    "native_safety_guard": "src/appworld/common/safety_guard.py",
    "task_loader": "src/appworld/task.py",
    "package_init": "src/appworld/__init__.py",
}
# This is an additional host boundary. AppWorld's original syntax guard and
# unsafe-execution patches remain enabled and unchanged for accepted code.
SAFE_IMPORTS = frozenset({
    "array", "bisect", "calendar", "collections", "copy", "csv", "datetime",
    "difflib", "enum", "fractions", "functools", "heapq", "itertools", "json",
    "math", "numbers", "operator", "pendulum", "pprint", "random", "re",
    "string", "textwrap", "time", "typing", "uuid",
})
FORBIDDEN_NAMES = frozenset({
    "AppWorld", "Task", "ApiCollection", "Requester", "world", "ground_truth", "required_apis", "private_data",
    "reference_actions", "evaluation_module", "evaluate", "evaluate_task",
    "evaluate_tasks", "evaluate_dataset", "model_collection", "models", "requester",
    "shell", "user_ns", "safety_guard", "environment_io", "expose_internals",
    "load_state", "save_state", "task_completed", "path_store", "appworld",
    "builtins", "sys", "os", "pathlib", "inspect", "importlib", "subprocess",
    "ctypes", "pickle", "marshal", "shelve", "socket", "multiprocessing",
    "threading", "signal", "gc", "resource", "import_module", "open", "input",
    "eval", "exec", "compile", "globals", "locals", "vars", "getattr",
    "setattr", "delattr", "dir", "help", "breakpoint", "exit", "quit",
    "attrgetter", "methodcaller", "Formatter", "get_field", "format", "format_map",
    "Path", "PurePath", "read_text", "read_bytes", "write_text", "write_bytes",
    "read_file", "read_json", "write_file", "write_json", "listdir", "glob", "rglob",
    "walk", "chdir", "getcwd", "environ", "getenv", "sqlite3", "connect",
    "BaseException", "KeyboardInterrupt", "SystemExit",
})
SAFE_FINISH_REASONS = frozenset({
    "actor_declared_finished", "task_completed", "blocked", "unresolved",
    "budget_exhausted", "wall_clock_exhausted",
})
LOG_SCHEMA = {
    "version": 1,
    "private_events": {
        "format": "JSONL, canonical sorted JSON, SHA256 chain over UTF-8 line without newline",
        "chain_fields": ["sequence", "previous_sha256"],
        "events": ["ready", "request", "execute", "response", "actor_stop", "controller_error", "grade"],
        "retention": "every request, full code, receipt, response, rejection and exception; local only",
    },
    "public_step_fields": [
        "request_index", "code_sha256", "code_bytes", "receipt_sha256", "receipt_bytes",
        "native_executed", "native_interactions_delta", "native_api_calls",
        "elapsed_seconds", "parse_error", "ast_rejection", "execution_error", "error_class", "receipt_source",
    ],
    "public_results": "hashes, numeric counts and fixed vocabulary outcomes; no identities, task text, credentials or code",
    "execute_requests": "every execute request after start, including malformed code, parse errors and AST rejections",
    "native_interactions": "actual AppWorld environment_io entries; zero for bridge parse/AST rejections",
    "native_execute_attempts": "calls actually made to unchanged AppWorld.execute, even if interrupted",
    "receipt_cost": "generated native/bridge receipt bytes and mailbox-delivered page bytes are separate; actor/model-visible bytes unknown",
    "pagination": "2000 Unicode characters per prompt/receipt page; duplicate pages count again; no native action for page retrieval",
}
_HOST_KILL = os.kill  # Keep the controller watchdog outside native monkeypatches.
_HOST_SLEEP = time.sleep


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_json_new(path: Path, value: Any, private: bool = False) -> None:
    """Atomic first-write; never replace an earlier run or partial first write."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError("refuse artifact overwrite")
    temporary = path.with_name(path.name + ".tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600 if private else 0o644)
    with os.fdopen(descriptor, "w") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    # link is exclusive at the destination, unlike replace().
    os.link(temporary, path)
    temporary.unlink()


def private_directory(path: Path) -> None:
    if path.resolve().is_relative_to(REPO_ROOT):
        raise ValueError("protected artifacts must be outside the repository")
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path, 0o700)


def source_head(root: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True,
                                   stderr=subprocess.DEVNULL).strip()


def manifest(root: Path) -> tuple[bytes, list[str]]:
    # Do not call Task.load, inspect data/tasks, or use difficulty/gold metadata.
    raw = (root / "data/datasets/train.txt").read_bytes()
    lines = raw.decode("utf-8").splitlines()
    ids = [line.strip().split(":")[0] for line in lines if line.strip()]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate normalized identities in train manifest")
    if any(value.count("_") != 1 or not value.rsplit("_", 1)[1].isdigit() for value in ids):
        raise ValueError("manifest does not expose a consistent generator-family structure")
    return raw, ids


def select(ids: list[str], excluded: set[str]) -> list[dict[str, Any]]:
    selected, families = [], set()
    for manifest_index, identity in enumerate(ids):
        family = identity.split("_")[0]
        if sha(identity.encode()) in excluded or family in families:
            continue
        families.add(family)
        selected.append({"index": len(selected), "manifest_index": manifest_index,
                         "task_id": identity, "family": family,
                         "task_sha256": sha(identity.encode()), "family_sha256": sha(family.encode())})
        if len(selected) == TASK_COUNT:
            break
    if len(selected) != TASK_COUNT or len(families) != TASK_COUNT:
        raise ValueError("fewer than 24 distinct remaining manifest families; do not resample")
    return selected


def source_version(root: Path) -> str:
    tree = ast.parse((root / SOURCE_FILES["package_init"]).read_text())
    for statement in tree.body:
        if isinstance(statement, ast.Assign) and any(isinstance(target, ast.Name) and
                target.id == "__version__" for target in statement.targets):
            value = ast.literal_eval(statement.value)
            if isinstance(value, str):
                return value
    raise ValueError("author environment version is not exposed as a constant")


def prepare(root: Path, freeze_path: Path, private_root: Path, exposure_path: Path) -> None:
    if source_head(root) != AUTHOR_SHA:
        raise ValueError("author source revision changed")
    raw, ids = manifest(root)
    exposure_raw = exposure_path.read_bytes()
    exposure = json.loads(exposure_raw)
    excluded_list = exposure["selected_task_hashes"]
    if len(excluded_list) != 3 or len(set(excluded_list)) != 3:
        raise ValueError("exposure freeze must identify exactly the previous three tasks")
    selected = select(ids, set(excluded_list))
    source_hashes = {name: sha((root / relative).read_bytes()) for name, relative in SOURCE_FILES.items()}
    frozen = {
        "protocol": PROTOCOL, "protocol_commit": PROTOCOL_COMMIT,
        "protocol_sha256": sha(PROTOCOL_PATH.read_bytes()), "source_ref": AUTHOR_SHA,
        "execution_protocol_sha256": sha(EXECUTION_PROTOCOL_PATH.read_bytes()),
        "actor_instructions_sha256": sha(ACTOR_INSTRUCTIONS_PATH.read_bytes()),
        "environment_version": source_version(root), "dataset": "train", "train_count": len(ids),
        "train_manifest_file_sha256": sha(raw), "train_manifest_sha256": sha("\n".join(ids).encode()),
        "selection": "scan unchanged manifest; exclude three exposed hashes; first remaining task per family; first 24 families",
        "excluded_exposed_task_hashes": excluded_list, "exposure_freeze_sha256": sha(exposure_raw),
        "selected_manifest_indices": [row["manifest_index"] for row in selected],
        "selected_task_hashes": [row["task_sha256"] for row in selected],
        "selected_family_hashes": [row["family_sha256"] for row in selected],
        "actors": TASK_COUNT, "distinct_families": TASK_COUNT, "fresh_worlds": True,
        "experiment_name_pattern": PROTOCOL + "_{index}",
        "max_execute_requests_per_actor": REQUEST_BUDGET,
        "code_timeout_seconds": CODE_TIMEOUT, "actor_wall_clock_seconds": ACTOR_TIMEOUT,
        "grade_timeout_seconds": GRADE_TIMEOUT, "transport_page_characters": PAGE_CHARS,
        "high_cost_thresholds": HIGH_COST_THRESHOLDS,
        "wall_clock_origin": "first start request accepted; waiting before start does not consume actor budget",
        "environment_random_seed": ENVIRONMENT_SEED,
        "actor_context": "unchanged author-rendered public task and generator context + fixed initial playbook + own legal receipts available by pagination while endpoint active",
        "prompt_read_requirement": "all prompt characters must have been delivered by sequential pages before native execution; actual model reading is unexposed",
        "termination_pagination_boundary": "no page retrieval after endpoint closes; last execute receipt may have unread pages when request or wall budget closes endpoint",
        "actor_ground_truth_loaded": False, "actor_evaluator_feedback": False,
        "task_prior_or_feedback": False, "oacr_intervention": False,
        "model": MODEL, "model_calls_tokens_cost": "not exposed; never inferred from native API calls",
        "grading": "unchanged author evaluate_task once after actor endpoint closes; no feedback, retry or task replacement",
        "retries_or_task_replacement": False,
        "protected_content": "selection identities, prompts and complete trajectories stay in local private artifacts outside repository",
        "transport": "atomic local file mailbox; start/execute/receipt_page/finish; complete own prompt/receipt pagination",
        "implementation_sha256": {name: sha((HERE / name).read_bytes()) for name in
                                  ("native_batch_bridge.py", "actor_client.py")},
        "source_file_sha256": source_hashes,
        "author_prompt_sha256": source_hashes["author_prompt"],
        "initial_playbook_sha256": source_hashes["initial_playbook"],
        "evaluator_sha256": source_hashes["evaluator"],
        "logging_schema": LOG_SCHEMA,
        "native_api_calls_measurement": "requester records observed while actor endpoint open; not a count of unobserved hidden/server attempts",
        "interpretation": "fixed development discovery batch; no test, novelty, mechanism or generalization claim",
    }
    if freeze_path.exists() or (private_root / "selection_mapping.json").exists():
        raise FileExistsError("refuse preparation overwrite")
    private_directory(private_root)
    write_json_new(private_root / "selection_mapping.json", {
        "protocol": PROTOCOL, "train_manifest_sha256": frozen["train_manifest_sha256"],
        "selection": selected,
    }, private=True)
    write_json_new(freeze_path, frozen)
    print(canonical({"status": "frozen", "selected": TASK_COUNT,
                     "distinct_families": TASK_COUNT, "tasks_loaded": 0}))


def verify_freeze(root: Path, freeze_path: Path, private_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frozen = json.loads(freeze_path.read_text())
    if frozen["protocol"] != PROTOCOL or source_head(root) != AUTHOR_SHA:
        raise ValueError("protocol/source revision differs from freeze")
    if sha(PROTOCOL_PATH.read_bytes()) != frozen["protocol_sha256"]:
        raise ValueError("frozen protocol changed")
    if (sha(EXECUTION_PROTOCOL_PATH.read_bytes()) != frozen["execution_protocol_sha256"] or
            sha(ACTOR_INSTRUCTIONS_PATH.read_bytes()) != frozen["actor_instructions_sha256"]):
        raise ValueError("frozen execution protocol/actor instructions changed")
    for name, expected in frozen["implementation_sha256"].items():
        if sha((HERE / name).read_bytes()) != expected:
            raise ValueError("frozen implementation changed")
    for name, expected in frozen["source_file_sha256"].items():
        if sha((root / SOURCE_FILES[name]).read_bytes()) != expected:
            raise ValueError("frozen author implementation changed")
    raw, ids = manifest(root)
    if sha(raw) != frozen["train_manifest_file_sha256"] or sha("\n".join(ids).encode()) != frozen["train_manifest_sha256"]:
        raise ValueError("frozen train manifest changed")
    selected = select(ids, set(frozen["excluded_exposed_task_hashes"]))
    if ([row["manifest_index"] for row in selected] != frozen["selected_manifest_indices"] or
            [row["task_sha256"] for row in selected] != frozen["selected_task_hashes"] or
            [row["family_sha256"] for row in selected] != frozen["selected_family_hashes"]):
        raise ValueError("frozen deterministic selection changed")
    mapping = json.loads((private_root / "selection_mapping.json").read_text())
    if mapping["selection"] != selected or mapping["train_manifest_sha256"] != frozen["train_manifest_sha256"]:
        raise ValueError("private selection mapping differs from frozen manifest")
    if (frozen["max_execute_requests_per_actor"], frozen["code_timeout_seconds"],
            frozen["actor_wall_clock_seconds"], frozen["environment_random_seed"],
            frozen["actors"]) != (REQUEST_BUDGET, CODE_TIMEOUT, ACTOR_TIMEOUT, ENVIRONMENT_SEED, TASK_COUNT):
        raise ValueError("frozen actor budget changed")
    if (frozen["grade_timeout_seconds"], frozen["transport_page_characters"]) != (GRADE_TIMEOUT, PAGE_CHARS):
        raise ValueError("frozen controller/transport budget changed")
    if frozen["high_cost_thresholds"] != HIGH_COST_THRESHOLDS:
        raise ValueError("frozen high-cost screen changed")
    return frozen, selected


def check_actor_ast(code: str) -> None:
    """Permit public API computation; reject host/evaluator access before native execution."""
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            raise PermissionError("bare exception handlers may suppress the controller deadline")
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                modules = [item.name for item in node.names]
            else:
                if node.level or not node.module:
                    raise PermissionError("relative imports are not public API execution")
                modules = [node.module]
                if any(item.name == "*" for item in node.names):
                    raise PermissionError("wildcard imports are not permitted")
            if any(module.split(".")[0] not in SAFE_IMPORTS for module in modules):
                raise PermissionError("host/backend imports are not permitted")
        identifiers = []
        if isinstance(node, ast.Name):
            if node.id == "_":
                continue  # Ordinary ignored loop/unpack variable.
            identifiers.append(node.id)
        elif isinstance(node, ast.Attribute):
            identifiers.append(node.attr)
        elif isinstance(node, ast.alias):
            identifiers.extend([node.name.split(".")[-1], node.asname or ""])
        if any(value.startswith("_") or value in FORBIDDEN_NAMES for value in identifiers if value):
            raise PermissionError("private/backend access is not permitted")


class ActorWallClockExpired(BaseException):
    """Escapes native Exception handlers; handled only by the controller."""


class GradeTimeout(BaseException):
    """A controller-only timeout, never returned to the actor."""


@contextmanager
def grade_deadline():
    previous_handler = signal.getsignal(signal.SIGALRM)

    def expire(_signal: int, _frame: Any) -> None:
        raise GradeTimeout()

    signal.signal(signal.SIGALRM, expire)
    previous_timer = signal.setitimer(signal.ITIMER_REAL, GRADE_TIMEOUT)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
        if previous_timer[0] > 0:
            signal.setitimer(signal.ITIMER_REAL, *previous_timer)


@contextmanager
def ledger_deadline_barrier(watchdog: Watchdog):
    """Defer only the actor deadline while its completed request is durably logged.

    Pending SIGUSR1 is delivered on unmasking; the outer controller then stops
    the endpoint before another native action. This region performs no actor
    code, API operation, or grading.
    """
    previous_protection = watchdog.ledger_protected
    watchdog.ledger_protected = True
    previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGUSR1})
    try:
        yield
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
        watchdog.ledger_protected = previous_protection
        # A process signal may have landed on an unmasked background thread.
        # Its Python handler is deferred by the explicit flag, so there may be
        # no OS signal pending when the main thread unmasks. Enforce it here.
        if (not previous_protection and watchdog.active and
                (watchdog.expired or (watchdog.deadline is not None and
                                     watchdog.clock() >= watchdog.deadline))):
            raise ActorWallClockExpired()


@contextmanager
def native_deadline_window(watchdog: Watchdog):
    """Unprotect only the native call, while its caller's try/finally is armed."""
    previous_mask = signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGUSR1})
    watchdog.ledger_protected = False
    try:
        if (watchdog.expired or (watchdog.deadline is not None and
                                watchdog.clock() >= watchdog.deadline)):
            raise ActorWallClockExpired()
        yield
    finally:
        watchdog.ledger_protected = True
        signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)


class Watchdog:
    """Independent real-clock hard deadline; native SIGALRM remains untouched."""
    def __init__(self, clock: Callable[[], float]):
        self.clock = clock
        self.active = False
        self.ledger_protected = False
        self.expired = False
        self.deadline: float | None = None
        self.cancel = threading.Event()
        self.thread: threading.Thread | None = None
        self.previous_handler = signal.getsignal(signal.SIGUSR1)
        signal.signal(signal.SIGUSR1, self._expire)

    def _expire(self, _signal: int, _frame: Any) -> None:
        if self.active and self.deadline is not None and self.clock() >= self.deadline:
            self.expired = True
            main_mask = signal.pthread_sigmask(signal.SIG_BLOCK, set())
            if self.ledger_protected or signal.SIGUSR1 in main_mask:
                return
            raise ActorWallClockExpired()

    def start(self, started: float) -> None:
        self.deadline = started + ACTOR_TIMEOUT
        self.active = True
        self.thread = threading.Thread(target=self._watch, daemon=True)
        self.thread.start()

    def _watch(self) -> None:
        while not self.cancel.wait(0.05):
            if self.active and self.deadline is not None and self.clock() >= self.deadline:
                _HOST_KILL(os.getpid(), signal.SIGUSR1)
                return

    def stop(self) -> None:
        self.active = False
        self.cancel.set()
        if self.thread is not None:
            self.thread.join(timeout=0.2)
        # Keep our now-inactive handler installed until this one-shot server
        # exits. A queued watchdog signal must never regain SIGUSR1's default
        # process-termination behavior while the controller saves or grades.


def serve(root: Path, freeze_path: Path, index: int, mailbox: Path,
          private_root: Path, summary_path: Path) -> None:
    frozen, selected = verify_freeze(root, freeze_path, private_root)
    identity = selected[index]["task_id"]
    experiment = f"{PROTOCOL}_{index}"
    events_path = private_root / f"events_{index}.jsonl"
    host_path = private_root / f"native_host_{index}.log"
    prompt_path = private_root / f"actor_prompt_{index}.txt"
    lock_path = private_root / f"run_{index}.lock"
    output_path = root / "experiments/outputs" / experiment
    if any(path.exists() for path in (events_path, host_path, prompt_path, lock_path, mailbox, summary_path, output_path)):
        raise FileExistsError("refuse reuse, retry or overwrite of a first-run world")
    if mailbox.resolve().is_relative_to(REPO_ROOT):
        raise ValueError("mailbox contains protected actor data and must be outside repository")
    private_directory(private_root)
    descriptor = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(descriptor)
    event_stream = events_path.open("x")
    os.chmod(events_path, 0o600)
    host_stream = host_path.open("x")
    os.chmod(host_path, 0o600)
    chain, sequence = "0" * 64, 0
    steps: list[dict[str, Any]] = []
    receipts: dict[int, str] = {}
    world = None
    watchdog = None
    started = None
    actor_elapsed = 0.0
    execute_requests = native_execute_attempts = rejected = parse_errors = native_errors = 0
    prompt_page_requests = receipt_page_requests = 0
    prompt_pages_delivered = receipt_pages_delivered = 0
    transport_prompt_text_bytes = transport_receipt_text_bytes = mailbox_response_bytes = 0
    delivered_prompt_end = bridge_request_errors = 0
    native_interactions = native_calls = 0
    finish_reason = "controller_initialization_error"
    actor_finish_reason = None
    actor_finish_reason_hash = None
    controller_error = None
    cleanup_errors: list[dict[str, str]] = []
    native_task_completed = None
    grade: dict[str, Any] = {"status": "not_run", "attempts": 0}
    prompt = ""
    active_request: Path | None = None
    clock = time.monotonic

    def log(event: dict[str, Any]) -> None:
        nonlocal chain, sequence
        sequence += 1
        event.update({"sequence": sequence, "previous_sha256": chain})
        line = canonical(event)
        chain = sha(line.encode())
        event_stream.write(line + "\n")
        event_stream.flush()
        os.fsync(event_stream.fileno())

    def native_call(function: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        with redirect_stdout(host_stream), redirect_stderr(host_stream):
            try:
                return function(*args, **kwargs)
            finally:
                host_stream.flush()

    def respond(request_path: Path, response: dict[str, Any]) -> None:
        nonlocal prompt_pages_delivered, receipt_pages_delivered, delivered_prompt_end
        nonlocal transport_prompt_text_bytes, transport_receipt_text_bytes, mailbox_response_bytes, bridge_request_errors
        response_path = request_path.with_name(request_path.name.replace(".request.json", ".response.json"))
        write_json_new(response_path, response, private=True)
        mailbox_response_bytes += response_path.stat().st_size
        if "prompt" in response:
            prompt_pages_delivered += 1
            transport_prompt_text_bytes += len(response["prompt"].encode())
            if response["offset"] <= delivered_prompt_end:
                delivered_prompt_end = max(delivered_prompt_end, response["offset"] + len(response["prompt"]))
        if "receipt" in response:
            receipt_pages_delivered += 1
            transport_receipt_text_bytes += len(response["receipt"].encode())
        if response.get("status") == "bridge_error":
            bridge_request_errors += 1
        log({"op": "response", "request_file": request_path.name, "response": response})
        request_path.unlink()

    def page(text: str, key: str, offset: Any) -> dict[str, Any]:
        if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0 or offset > len(text):
            raise ValueError("page offset must be within this actor's existing text")
        end = min(offset + PAGE_CHARS, len(text))
        return {key: text[offset:end], "offset": offset, "total_chars": len(text),
                "next_offset": end if end < len(text) else None, "page_char_limit": PAGE_CHARS}

    try:
        # The package's __init__ imports the evaluator module, but no evaluator
        # is called and no ground truth is loaded until after actor termination.
        with redirect_stdout(host_stream), redirect_stderr(host_stream):
            os.environ["APPWORLD_ROOT"] = str(root)
            os.environ["APPWORLD_PROJECT_PATH"] = str(root)
            from appworld import AppWorld
            from appworld.common.path_store import path_store
            from freezegun.api import real_perf_counter
            from jinja2 import Template
            path_store.update_root(str(root))
            clock = real_perf_counter
            watchdog = Watchdog(clock)
            world = AppWorld(task_id=identity, experiment_name=experiment,
                load_ground_truth=False, random_seed=ENVIRONMENT_SEED,
                max_interactions=REQUEST_BUDGET, timeout_seconds=CODE_TIMEOUT,
                raise_on_unsafe_syntax=True, null_patch_unsafe_execution=True)
            prompt = Template((root / SOURCE_FILES["author_prompt"]).read_text()).render(
                input_str=world.task.instruction, main_user=world.task.supervisor,
                app_descriptions=json.dumps([{"name": key, "description": value}
                    for key, value in world.task.app_descriptions.items()], indent=1),
                playbook=(root / SOURCE_FILES["initial_playbook"]).read_text())
        prompt_path.write_text(prompt)
        os.chmod(prompt_path, 0o600)
        mailbox.mkdir(parents=True, mode=0o700)
        os.chmod(mailbox, 0o700)
        log({"op": "ready", "prompt": prompt, "index": index,
             "actor_ground_truth_loaded": False, "actor_evaluator_feedback": False})
        print(canonical({"status": "native_actor_ready", "index": index}), flush=True)
        finish_reason = "unresolved"
        done = False
        while not done:
            if started is not None and clock() - started >= ACTOR_TIMEOUT:
                finish_reason = "wall_clock_exhausted"
                break
            pending = sorted(mailbox.glob("*.request.json"), key=lambda path: (path.stat().st_mtime_ns, path.name))
            if not pending:
                _HOST_SLEEP(0.05)
                continue
            active_request = pending[0]
            raw_request = active_request.read_text()
            try:
                request = json.loads(raw_request)
                if not isinstance(request, dict):
                    raise TypeError("request must be a JSON object")
            except (ValueError, TypeError) as exc:
                log({"op": "request", "request_file": active_request.name,
                     "raw_request": raw_request, "parse_error": type(exc).__name__})
                respond(active_request, {"status": "bridge_error", "error_class": type(exc).__name__})
                active_request = None
                continue
            op = request.get("op")
            start_offset = request.get("offset", 0)
            valid_start = (op == "start" and isinstance(start_offset, int) and
                           not isinstance(start_offset, bool) and 0 <= start_offset <= delivered_prompt_end)
            if valid_start and started is None:
                started = clock()
                watchdog.start(started)
            log({"op": "request", "request_file": active_request.name,
                 "request": request, "actor_elapsed_seconds": None if started is None else clock() - started})
            if op == "start":
                prompt_page_requests += 1
                if not valid_start:
                    response = {"status": "bridge_error", "error_class": "InvalidPromptOffset"}
                else:
                    response = {"status": "actor_task", "index": index,
                        "max_execute_requests": REQUEST_BUDGET, "code_timeout_seconds": CODE_TIMEOUT,
                        "actor_wall_clock_seconds": ACTOR_TIMEOUT,
                        "permitted_endpoint": "execute public APIs in the persistent native REPL; own receipts only"}
                    response.update(page(prompt, "prompt", start_offset))
            elif started is None:
                response = {"status": "bridge_error", "error_class": "StartRequired"}
            elif op == "execute":
                with ledger_deadline_barrier(watchdog):
                    raw_code = request.get("code")
                    code = raw_code if isinstance(raw_code, str) else canonical(raw_code)
                    receipt = "Bridge rejected malformed code; code must be a string."
                    receipt_source = "bridge"
                    error_class = None
                    was_native = ast_rejected = parse_error = execution_error = False
                    before_interactions, before_calls = len(world.environment_io), len(world.requester.requests)
                    begin = clock()
                    wall_expired = False
                    try:
                        execute_requests += 1
                        if delivered_prompt_end != len(prompt):
                            receipt = "Bridge rejected execute: retrieve all initial prompt pages before native execution."
                            error_class = "PromptReadIncomplete"
                            ast_rejected = True
                            rejected += 1
                        elif not isinstance(raw_code, str):
                            error_class = "TypeError"
                            ast_rejected = True
                            rejected += 1
                        else:
                            check_actor_ast(code)
                            with native_deadline_window(watchdog):
                                was_native = True
                                native_execute_attempts += 1
                                receipt = native_call(world.execute, code)
                            receipt_source = "native"
                            if not isinstance(receipt, str):
                                receipt = str(receipt)
                            execution_error = receipt.startswith("Execution failed")
                    except SyntaxError as exc:
                        parse_error = True
                        parse_errors += 1
                        error_class = type(exc).__name__
                        receipt = "Bridge rejected code: Python syntax error. " + exc.msg
                    except PermissionError as exc:
                        ast_rejected = True
                        rejected += 1
                        error_class = type(exc).__name__
                        receipt = "Bridge rejected nonpublic host/backend/evaluator access."
                    except ActorWallClockExpired:
                        watchdog.stop()
                        wall_expired = True
                        execution_error = was_native
                        error_class = "ActorWallClockExpired"
                        receipt = "Actor wall-clock budget exhausted; actor endpoint terminated."
                    except Exception as exc:
                        if was_native:
                            world.safety_guard.disable()
                        execution_error = True
                        error_class = type(exc).__name__
                        receipt = "Native execution raised a controller-visible exception: " + error_class
                        log({"op": "controller_error", "phase": "execute", "traceback": traceback.format_exc()})
                    finally:
                        # Native BaseException interruption can bypass its normal
                        # guard cleanup. No async deadline may drop this ledger row.
                        with ledger_deadline_barrier(watchdog):
                            if was_native:
                                world.safety_guard.disable()
                            delta_interactions = len(world.environment_io) - before_interactions
                            delta_calls = len(world.requester.requests) - before_calls
                            if execution_error and was_native:
                                native_errors += 1
                            row = {"request_index": execute_requests, "code_sha256": sha(code.encode()),
                                "code_bytes": len(code.encode()), "receipt_sha256": sha(receipt.encode()),
                                "receipt_bytes": len(receipt.encode()), "native_executed": was_native,
                                "native_interactions_delta": delta_interactions, "native_api_calls": delta_calls,
                                "elapsed_seconds": clock() - begin, "parse_error": parse_error,
                                "ast_rejection": ast_rejected, "execution_error": execution_error,
                                "error_class": error_class, "receipt_source": receipt_source}
                            steps.append(row)
                            receipts[execute_requests] = receipt
                            log({"op": "execute", "code": raw_code, "receipt": receipt, "metrics": row})
                response = {"status": "native_receipt", "step": execute_requests,
                            "remaining_execute_requests": REQUEST_BUDGET - execute_requests}
                response.update(page(receipt, "receipt", 0))
                if wall_expired or clock() - started >= ACTOR_TIMEOUT:
                    finish_reason, done = "wall_clock_exhausted", True
                elif execute_requests == REQUEST_BUDGET:
                    finish_reason, done = "budget_exhausted", True
                if done:
                    response.update({"actor_terminated": True, "finish_reason": finish_reason,
                                     "grading_feedback": "withheld"})
            elif op == "receipt_page":
                receipt_page_requests += 1
                step = request.get("step")
                offset = request.get("offset", 0)
                if isinstance(step, bool) or not isinstance(step, int) or step not in receipts:
                    response = {"status": "bridge_error", "error_class": "UnknownOwnReceiptStep"}
                else:
                    try:
                        response = {"status": "receipt_page", "step": step,
                                    "remaining_execute_requests": REQUEST_BUDGET - execute_requests}
                        response.update(page(receipts[step], "receipt", offset))
                    except ValueError:
                        response = {"status": "bridge_error", "error_class": "InvalidReceiptOffset"}
            elif op == "finish":
                reason = request.get("reason", "actor_declared_finished")
                text = reason if isinstance(reason, str) else canonical(reason)
                actor_finish_reason = text if text in SAFE_FINISH_REASONS else "actor_declared_finished"
                actor_finish_reason_hash = sha(text.encode())
                finish_reason = actor_finish_reason
                response = {"status": "actor_terminated", "grading_feedback": "withheld"}
                done = True
            else:
                response = {"status": "bridge_error", "error_class": "UnknownOperation"}
            respond(active_request, response)
            active_request = None
    except ActorWallClockExpired:
        finish_reason = "wall_clock_exhausted"
    except BaseException as exc:
        controller_error = type(exc).__name__
        finish_reason = "controller_initialization_error" if started is None else "controller_error"
        log({"op": "controller_error", "phase": "actor", "error_class": controller_error,
             "traceback": traceback.format_exc()})
    finally:
        if watchdog is not None:
            watchdog.stop()
        if world is not None:
            world.safety_guard.disable()
        actor_elapsed = 0.0 if started is None else clock() - started
        # Close the actor endpoint before querying completion or grading. Any
        # abandoned queued requests are retained in the private mailbox.
        if mailbox.exists():
            if active_request is not None and active_request.exists():
                try:
                    respond(active_request, {"status": "actor_terminated", "finish_reason": finish_reason,
                                             "grading_feedback": "withheld"})
                except Exception as exc:
                    log({"op": "controller_error", "phase": "final_response", "error_class": type(exc).__name__})
            (mailbox / "terminated.txt").write_text("Actor endpoint terminated; grading feedback withheld.\n")
            os.chmod(mailbox / "terminated.txt", 0o600)
        log({"op": "actor_stop", "finish_reason": finish_reason, "actor_started": started is not None,
             "execute_requests": execute_requests, "actor_elapsed_seconds": actor_elapsed})
        if world is not None:
            native_interactions, native_calls = len(world.environment_io), len(world.requester.requests)
            try:
                native_task_completed = native_call(world.task_completed)
            except BaseException as exc:
                cleanup_errors.append({"phase": "completion_check", "error_class": type(exc).__name__})
                log({"op": "controller_error", "phase": "completion_check", "error_class": type(exc).__name__})
            try:
                # Preserve the actual final native state even if the hard actor
                # deadline interrupted execute before its ordinary state save.
                native_call(world._save_state, world.output_db_home_path_on_disk)
                native_call(world.save_logs)
                native_call(world.close)
            except BaseException as exc:
                cleanup_errors.append({"phase": "world_close", "error_class": type(exc).__name__})
                log({"op": "controller_error", "phase": "world_close", "error_class": type(exc).__name__})
            # Exactly one controller-only call, regardless of success, finish
            # claims, budget exhaustion or execution/controller errors.
            grade = {"status": "evaluator_error", "attempts": 1}
            try:
                with grade_deadline(), redirect_stdout(host_stream), redirect_stderr(host_stream):
                    from appworld.evaluator import evaluate_task
                    tracker, _ = evaluate_task(task_id=identity, experiment_name=experiment,
                                               suppress_errors=True, save_report=True)
                grade.update({"status": "evaluated", "success": tracker.success,
                              "num_tests": tracker.num_tests, "pass_count": tracker.pass_count,
                              "fail_count": tracker.fail_count})
            except BaseException as exc:
                grade["error_class"] = type(exc).__name__
                log({"op": "controller_error", "phase": "grading", "error_class": type(exc).__name__,
                     "traceback": traceback.format_exc()})
            log({"op": "grade", "grade": grade})
        event_stream.close()
        host_stream.close()
        result = {
            "protocol": PROTOCOL, "index": index, "batch_denominator": TASK_COUNT,
            "task_id_sha256": selected[index]["task_sha256"],
            "family_sha256": selected[index]["family_sha256"],
            "manifest_index": selected[index]["manifest_index"],
            "actor_started": started is not None, "actor_terminated": True,
            "finish_reason": finish_reason, "actor_finish_reason": actor_finish_reason,
            "actor_finish_reason_sha256": actor_finish_reason_hash,
            "native_task_completed": native_task_completed, "controller_error_class": controller_error,
            "controller_cleanup_errors": cleanup_errors,
            "actor_ground_truth_loaded": False, "actor_evaluator_feedback": False,
            "oacr_intervention": False, "execute_requests": execute_requests,
            "native_execute_attempts": native_execute_attempts, "native_interactions": native_interactions,
            "native_api_calls": native_calls, "bridge_rejections": rejected,
            "native_api_calls_measurement": frozen["native_api_calls_measurement"],
            "parse_errors": parse_errors, "native_execution_errors": native_errors,
            "generated_receipt_bytes": sum(row["receipt_bytes"] for row in steps),
            "generated_native_receipt_bytes": sum(row["receipt_bytes"] for row in steps if row["receipt_source"] == "native"),
            "generated_bridge_receipt_bytes": sum(row["receipt_bytes"] for row in steps if row["receipt_source"] != "native"),
            "transport_prompt_text_bytes": transport_prompt_text_bytes,
            "transport_receipt_text_bytes": transport_receipt_text_bytes,
            "mailbox_response_bytes": mailbox_response_bytes,
            "prompt_page_requests": prompt_page_requests, "receipt_page_requests": receipt_page_requests,
            "prompt_pages_delivered": prompt_pages_delivered, "receipt_pages_delivered": receipt_pages_delivered,
            "prompt_delivered_unique_chars": delivered_prompt_end,
            "complete_prompt_delivered": delivered_prompt_end == len(prompt),
            "actor_visible_prompt_bytes": None, "actor_visible_receipt_bytes": None,
            "bridge_request_errors": bridge_request_errors,
            "client_communication_timeouts": None,
            "actor_elapsed_seconds": actor_elapsed, "steps": steps, "grade": grade,
            "native_execute_elapsed_seconds": sum(row["elapsed_seconds"] for row in steps if row["native_executed"]),
            "events_sha256": sha(events_path.read_bytes()), "events_chain_final_sha256": chain,
            "events_count": sequence, "native_host_log_sha256": sha(host_path.read_bytes()),
            "prompt_sha256": sha(prompt.encode()), "prompt_bytes": len(prompt.encode()),
            "freeze_sha256": sha(freeze_path.read_bytes()),
            "external_provider_model_calls": 0,
            "actor_invocations": 1 if started is not None else 0,
            "subagent_model_calls": None, "subagent_model_tokens": None, "subagent_model_cost": None,
            "subagent_model_usage": "inherited actor backend; not exposed to controller",
            "failure_attribution": "pending evidence-backed local review",
            "interpretation": frozen["interpretation"],
        }
        result["high_cost_flags"] = {name: result[name] >= threshold for name, threshold in HIGH_COST_THRESHOLDS.items()}
        result["high_cost_screen_triggered"] = any(result["high_cost_flags"].values())
        write_json_new(summary_path, result)
        print(canonical({"status": "actor_run_complete", "index": index,
                         "actor_started": started is not None, "finish_reason": finish_reason,
                         "execute_requests": execute_requests, "native_interactions": native_interactions,
                         "grade_status": grade["status"], "success": grade.get("success")}), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--exposure-freeze", type=Path, default=EXPOSURE_FREEZE)
    parser.add_argument("--index", type=int, choices=range(TASK_COUNT))
    parser.add_argument("--mailbox", type=Path)
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()
    root = args.source_root.resolve()
    if not args.prepare and any(value is None for value in (args.index, args.mailbox, args.summary)):
        parser.error("serve requires --index, --mailbox and --summary")
    try:
        if args.prepare:
            prepare(root, args.freeze, args.private_root.resolve(), args.exposure_freeze)
        else:
            serve(root, args.freeze, args.index, args.mailbox.resolve(), args.private_root.resolve(), args.summary)
    except BaseException as exc:
        # Never print exception text: author paths/messages may contain identities.
        print(canonical({"status": "bridge_failed", "index": args.index,
                         "error_class": type(exc).__name__}), flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
