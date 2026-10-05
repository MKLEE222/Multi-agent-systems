"""Durable at-most-once admission for a local JSON mailbox.

Import this module BEFORE native imports or monkeypatches. It imports no task
runtime. A claimed request without a durable execution result is never retried.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
import fcntl
import hashlib
import json
import os
import re
import stat
import uuid
from typing import Any, Callable, Iterator

# Controller capabilities are captured before the native execution boundary.
# Use these directly; Path methods and patched os functions are never used for IO.
_HOST_OPEN = os.open
_HOST_READ = os.read
_HOST_WRITE = os.write
_HOST_CLOSE = os.close
_HOST_FSYNC = os.fsync
_HOST_STAT = os.stat
_HOST_FSTAT = os.fstat
_HOST_MKDIR = os.mkdir
_HOST_RENAME = os.rename
_HOST_LINK = os.link
_HOST_UNLINK = os.unlink
_HOST_FLOCK = fcntl.flock
_HOST_UUID4 = uuid.uuid4
_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_DIRECTORY = getattr(os, "O_DIRECTORY", 0)
_NONBLOCK = getattr(os, "O_NONBLOCK", 0)
_REQUEST_NAME = re.compile(r"([0-9a-f]{32})\.request\.json\Z")


def _canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _exists(path: str) -> bool:
    try:
        _HOST_STAT(path, follow_symlinks=False)
        return True
    except FileNotFoundError:
        return False


def _mkdirs(path: str) -> None:
    path = os.fspath(path)
    parent = os.path.dirname(path)
    if parent != path and not _exists(parent):
        _mkdirs(parent)
    try:
        _HOST_MKDIR(path, 0o700)
    except FileExistsError:
        if not stat.S_ISDIR(_HOST_STAT(path, follow_symlinks=False).st_mode):
            raise OSError("controller directory is not a directory")


def _read(path: str) -> bytes:
    path = os.fspath(path)
    descriptor = _HOST_OPEN(path, os.O_RDONLY | _NOFOLLOW | _NONBLOCK)
    try:
        if not stat.S_ISREG(_HOST_FSTAT(descriptor).st_mode):
            raise OSError("controller input is not a regular file")
        pieces = []
        while True:
            piece = _HOST_READ(descriptor, 65536)
            if not piece:
                return b"".join(pieces)
            pieces.append(piece)
    finally:
        _HOST_CLOSE(descriptor)


def _sync_directory(path: str) -> None:
    path = os.fspath(path)
    descriptor = _HOST_OPEN(path, os.O_RDONLY | _DIRECTORY | _NOFOLLOW)
    try:
        _HOST_FSYNC(descriptor)
    finally:
        _HOST_CLOSE(descriptor)


def _remove_verified(path: str) -> None:
    path = os.fspath(path)
    if not _exists(path):
        return
    _HOST_UNLINK(path)
    if _exists(path):
        raise OSError("controller unlink had no effect")
    _sync_directory(os.path.dirname(path))


def _write_immutable(path: str, data: bytes, on_installed: Callable[[], None] | None = None) -> None:
    """Publish an immutable, fsynced file exclusively, then sync its directory."""
    path = os.fspath(path)
    temporary = path + ".tmp." + _HOST_UUID4().hex
    descriptor = _HOST_OPEN(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | _NOFOLLOW, 0o600)
    try:
        offset = 0
        while offset < len(data):
            written = _HOST_WRITE(descriptor, data[offset:])
            if written <= 0:
                raise OSError("controller write made no progress")
            offset += written
        _HOST_FSYNC(descriptor)
    finally:
        _HOST_CLOSE(descriptor)
    try:
        _HOST_LINK(temporary, path, follow_symlinks=False)
        if on_installed is not None:
            on_installed()  # Installation happened, even if fsync/cleanup fails.
        _sync_directory(os.path.dirname(path))
    finally:
        _remove_verified(temporary)


class TransportError(RuntimeError):
    """Close the endpoint on this error; never rerun a native callback."""
    def __init__(self, code: str, request_id: str | None = None,
                 publication: PublicationResult | None = None,
                 publication_state: str = "not_published"):
        super().__init__(code)  # Deliberately omit payloads and mailbox UUIDs.
        self.code = code
        self.request_id = request_id
        self.publication = publication
        self.publication_state = publication_state


@dataclass(frozen=True)
class ClaimResult:
    disposition: str  # new, cache, inflight, conflict
    request_id: str
    pending_path: str
    claimed_path: str
    payload: dict[str, Any] | None = field(default=None, repr=False)
    reason: str | None = None
    response: dict[str, Any] | None = field(default=None, repr=False)
    _token: str | None = field(default=None, repr=False, compare=False)


@dataclass(frozen=True)
class PublicationResult:
    request_id: str
    status: str  # published or already_published; this is not a read acknowledgment
    response: dict[str, Any] = field(repr=False)
    cleanup_complete: bool = True
    response_bytes: int = 0


class TransportOnce:
    """One controller mailbox, durable UUID records, no execution recovery.

    The ledger and mailbox must be on the same filesystem. The bridge should
    close on conflict/inflight/error and use execute() for callback admission.
    """
    def __init__(self, mailbox: os.PathLike[str] | str,
                 ledger_dir: os.PathLike[str] | str | None = None):
        self.mailbox = os.path.normpath(os.fspath(mailbox))
        self.ledger_dir = os.path.normpath(os.fspath(ledger_dir)) if ledger_dir is not None else os.path.join(self.mailbox, ".transport_once")
        if not os.path.isabs(self.mailbox) or not os.path.isabs(self.ledger_dir):
            raise ValueError("controller paths must be absolute")
        _mkdirs(self.mailbox)
        _mkdirs(self.ledger_dir)
        _sync_directory(self.mailbox)
        _sync_directory(self.ledger_dir)
        self._tokens: dict[str, tuple[str, str]] = {}

    def _paths(self, request_id: str) -> dict[str, str]:
        return {name: os.path.join(self.ledger_dir, request_id + suffix) for name, suffix in {
            "claimed": ".claimed.json", "input": ".claimed.request.json",
            "cache": ".cache.json", "executed": ".executed.json",
            "responded": ".responded.json", "lock": ".lock",
        }.items()}

    @contextmanager
    def _lock(self, request_id: str) -> Iterator[None]:
        descriptor = _HOST_OPEN(self._paths(request_id)["lock"], os.O_RDWR | os.O_CREAT | _NOFOLLOW, 0o600)
        try:
            _HOST_FLOCK(descriptor, fcntl.LOCK_EX)
            yield
        finally:
            _HOST_FLOCK(descriptor, fcntl.LOCK_UN)
            _HOST_CLOSE(descriptor)

    def _record(self, path: str, request_id: str, state: str) -> dict[str, Any]:
        try:
            value = json.loads(_read(path))
            if (not isinstance(value, dict) or value.get("schema_version") != 1 or
                    value.get("request_id") != request_id or value.get("state") != state):
                raise ValueError()
            return value
        except (OSError, ValueError, TypeError) as exc:
            raise TransportError("LedgerIntegrity", request_id) from exc

    def _cached(self, request_id: str, claimed: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
        paths = self._paths(request_id)
        executed = self._record(paths["executed"], request_id, "executed")
        try:
            data = _read(paths["cache"])
            response = json.loads(data)
            if (not isinstance(response, dict) or _canonical(response) != data or
                    executed.get("response_sha256") != _sha(data) or
                    executed.get("payload_sha256") != claimed.get("payload_sha256")):
                raise ValueError()
        except (OSError, ValueError, TypeError) as exc:
            raise TransportError("CacheIntegrity", request_id) from exc
        if _exists(paths["responded"]):
            responded = self._record(paths["responded"], request_id, "responded")
            if responded.get("response_sha256") != _sha(data):
                raise TransportError("LedgerIntegrity", request_id)
        return data, response

    def claim(self, pending_path: os.PathLike[str] | str) -> ClaimResult:
        pending = os.path.normpath(os.fspath(pending_path))
        matched = _REQUEST_NAME.fullmatch(os.path.basename(pending))
        if os.path.dirname(pending) != self.mailbox or matched is None:
            raise TransportError("InvalidPendingPath")
        request_id = matched.group(1)
        paths = self._paths(request_id)
        with self._lock(request_id):
            try:
                payload = json.loads(_read(pending))
                if not isinstance(payload, dict):
                    raise ValueError()
                payload_hash = _sha(_canonical(payload))
            except (OSError, ValueError, TypeError) as exc:
                raise TransportError("InvalidPendingPayload", request_id) from exc
            if _exists(paths["claimed"]):
                claimed = self._record(paths["claimed"], request_id, "claimed")
                if claimed.get("payload_sha256") != payload_hash:
                    return ClaimResult("conflict", request_id, pending, paths["input"], reason="PayloadChanged")
                if claimed.get("blocked_reason"):
                    return ClaimResult("conflict", request_id, pending, paths["input"], reason=claimed["blocked_reason"])
                if _exists(paths["executed"]):
                    _, response = self._cached(request_id, claimed)
                    return ClaimResult("cache", request_id, pending, paths["input"], response=response)
                return ClaimResult("inflight", request_id, pending, paths["input"], reason="ClaimedWithoutExecutedResult")
            if any(_exists(paths[name]) for name in ("input", "cache", "executed", "responded")):
                return ClaimResult("inflight", request_id, pending, paths["input"], reason="OrphanedDurableArtifact")
            response_path = os.path.join(self.mailbox, request_id + ".response.json")
            blocked = "UnexpectedExistingResponse" if _exists(response_path) else None
            claimed = {"schema_version": 1, "state": "claimed", "request_id": request_id,
                       "payload_sha256": payload_hash, "blocked_reason": blocked}
            try:
                _write_immutable(paths["claimed"], _canonical(claimed))
                # Per-UUID lock plus immutable ledger reserves the destination.
                # Rename removes the original pending name without using unlink.
                _HOST_RENAME(pending, paths["input"])
                _sync_directory(self.mailbox)
                _sync_directory(self.ledger_dir)
                if _exists(pending) or not _exists(paths["input"]):
                    raise OSError("controller claim rename had no effect")
                moved_payload = json.loads(_read(paths["input"]))
                if _sha(_canonical(moved_payload)) != payload_hash:
                    raise OSError("controller claimed input changed")
            except (OSError, ValueError, TypeError) as exc:
                raise TransportError("ClaimPersistenceFailed", request_id) from exc
            if blocked:
                return ClaimResult("conflict", request_id, pending, paths["input"], reason=blocked)
            token = _HOST_UUID4().hex
            self._tokens[token] = (request_id, "ready")
            return ClaimResult("new", request_id, pending, paths["input"], payload=payload, _token=token)

    def execute(self, claim: ClaimResult, callback: Callable[[dict[str, Any]], dict[str, Any]]) -> PublicationResult:
        """Consume the live new-claim capability once, then cache/publish result."""
        with self._lock(claim.request_id):
            if (claim.disposition != "new" or claim.payload is None or
                    self._tokens.get(claim._token or "") != (claim.request_id, "ready")):
                raise TransportError("CallbackNotAuthorized", claim.request_id)
            paths = self._paths(claim.request_id)
            claimed = self._record(paths["claimed"], claim.request_id, "claimed")
            if (claimed.get("blocked_reason") or _exists(paths["executed"]) or
                    _exists(paths["cache"]) or _sha(_canonical(claim.payload)) != claimed.get("payload_sha256")):
                raise TransportError("CallbackNotAuthorized", claim.request_id)
            self._tokens[claim._token] = (claim.request_id, "running")
        try:
            response = callback(claim.payload)
            return self.complete(claim, response)
        finally:
            self._tokens.pop(claim._token, None)

    def complete(self, claim: ClaimResult, response: dict[str, Any]) -> PublicationResult:
        """Durably cache result before publication. Never calls actor/native code."""
        token = claim._token or ""
        if (claim.disposition != "new" or self._tokens.get(token) not in
                {(claim.request_id, "ready"), (claim.request_id, "running")}):
            raise TransportError("CompletionNotAuthorized", claim.request_id)
        # Completion is one-shot even if persistence or publication raises.
        self._tokens.pop(token, None)
        if not isinstance(response, dict):
            raise TransportError("InvalidResponse", claim.request_id)
        try:
            data = _canonical(response)
        except (ValueError, TypeError) as exc:
            raise TransportError("InvalidResponse", claim.request_id) from exc
        paths = self._paths(claim.request_id)
        with self._lock(claim.request_id):
            claimed = self._record(paths["claimed"], claim.request_id, "claimed")
            if claimed.get("blocked_reason") or _exists(paths["executed"]) or _exists(paths["cache"]):
                raise TransportError("CompletionAlreadyRecorded", claim.request_id)
            try:
                _write_immutable(paths["cache"], data)
                _write_immutable(paths["executed"], _canonical({
                    "schema_version": 1, "state": "executed", "request_id": claim.request_id,
                    "payload_sha256": claimed["payload_sha256"], "response_sha256": _sha(data),
                }))
            except OSError as exc:
                raise TransportError("ResultPersistenceFailed", claim.request_id) from exc
            return self._publish_locked(claim, claimed)

    def publish_cached(self, claim: ClaimResult) -> PublicationResult:
        """Republish an authenticated durable result without any callback."""
        if claim.disposition != "cache":
            raise TransportError("CachedPublicationNotAuthorized", claim.request_id)
        with self._lock(claim.request_id):
            claimed = self._record(self._paths(claim.request_id)["claimed"], claim.request_id, "claimed")
            return self._publish_locked(claim, claimed)

    def _publish_locked(self, claim: ClaimResult, claimed: dict[str, Any]) -> PublicationResult:
        paths = self._paths(claim.request_id)
        data, response = self._cached(claim.request_id, claimed)
        response_path = os.path.join(self.mailbox, claim.request_id + ".response.json")
        status = "already_published"
        installed = verified_existing = attempted = False

        def installed_callback() -> None:
            nonlocal installed, status
            installed, status = True, "published"

        def observed_publication() -> PublicationResult | None:
            if installed or verified_existing:
                return PublicationResult(claim.request_id, status, response,
                                         cleanup_complete=False, response_bytes=len(data))
            return None

        def publication_state() -> str:
            if installed or verified_existing:
                return "known"
            return "unknown" if attempted else "not_published"

        try:
            if not _exists(response_path):
                attempted = True
                try:
                    # Publication is a separate inode: a consumer modifying its
                    # response must not mutate the durable cached execution result.
                    _write_immutable(response_path, data, on_installed=installed_callback)
                except FileExistsError:
                    pass  # Validate the winner; never replace it.
            if not installed:
                if _read(response_path) != data:
                    raise TransportError("ExistingResponseConflict", claim.request_id)
                verified_existing = True
            if not _exists(paths["responded"]):
                _write_immutable(paths["responded"], _canonical({
                    "schema_version": 1, "state": "responded", "request_id": claim.request_id,
                    "response_sha256": _sha(data), "meaning": "published_not_consumption_acknowledged",
                }))
        except TransportError as exc:
            exc.publication = observed_publication()
            exc.publication_state = publication_state()
            raise
        except OSError as exc:
            raise TransportError("PublicationFailed", claim.request_id, observed_publication(), publication_state()) from exc
        try:
            # Native work is already durably recorded; cleanup failure is fatal
            # to the endpoint but can never authorize callback re-execution.
            if _exists(claim.pending_path):
                pending_payload = json.loads(_read(claim.pending_path))
                if _sha(_canonical(pending_payload)) != claimed["payload_sha256"]:
                    raise TransportError("PayloadChangedDuringCleanup", claim.request_id)
                _remove_verified(claim.pending_path)
            _remove_verified(paths["input"])
        except TransportError as exc:
            exc.publication = observed_publication()
            exc.publication_state = publication_state()
            raise
        except (OSError, ValueError, TypeError) as exc:
            raise TransportError("CleanupFailed", claim.request_id, observed_publication(), publication_state()) from exc
        return PublicationResult(claim.request_id, status, response, response_bytes=len(data))
