# DEV24B transport admission fix and synthetic stress result

Date: 2026-10-04. This is a new transport implementation and a transport-only diagnostic. The frozen `experiments/oacr_residual_discovery/` producer was not edited or rerun. Native bridge integration, later freezing, and native task controls are outside this diagnostic.

## Result

The new transport implements durable **at-most-once callback admission per mailbox UUID**. A response publication or request cleanup failure cannot authorize another callback. A restarted controller may only republish an authenticated executed result; a claimed UUID without a durable executed result fails closed. This is not a general exactly-once execution guarantee.

The synthetic suite passed **26/26 tests**, with no AppWorld import, world construction, task/API/model/evaluator call, or real task data. The batch stress case admitted 128 distinct synthetic UUIDs, invoked its callback once for each, and processed 2,048 subsequent cached deliveries using eight threads and fresh controller objects. The complete suite entered callback admission for 154 UUIDs and observed exactly 154 callbacks, one per UUID. These counts are synthetic transport behavior, not native API calls or model usage.

There were 155 new claims in total. One additional new claim was deliberately abandoned after persistence but before its callback, to simulate a crash at that boundary. It had zero callbacks and stayed inflight after restart. One harmful pre-existing response was rejected before new admission and also had zero callbacks. The result file lists these cases separately; it does not hide the possible zero-execution outcome of at-most-once admission.

Public deliverables:

- `experiments/oacr_residual_dev24b/transport_once.py`
- `experiments/oacr_residual_dev24b/test_transport_only.py`
- `experiments/oacr_residual_dev24b/TRANSPORT_STRESS_RESULT_2026-10-04.json`

| Tested source | SHA256 |
| --- | --- |
| `transport_once.py` | `a9ade88c9bbc95a61afd101e3f6fd378127b28e3316db4136cb47e9c20b225a9` |
| `test_transport_only.py` | `1a3bcc561042fa52e830abc7a08b80fe4e45cbe34418b32d5fb4ea3f43fca207` |
| Stress result JSON | `f36fbc46bccc52989b70f421c8fad65cec262a09d52e31642751c90545f65433` |

Reproduce from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python experiments/oacr_residual_dev24b/test_transport_only.py --result experiments/oacr_residual_dev24b/TRANSPORT_STRESS_RESULT_2026-10-04.json
```

All test inputs are synthetic JSON written under temporary directories. The runner checks the imported module registry for AppWorld. Its separate-process restart test imports only standard-library modules and the new transport module. No live mailbox, frozen actor trajectory, native state, evaluator output, or task identity is used.

## Bridge API

Import `transport_once` **before any native imports or monkeypatches**. Construct `TransportOnce(mailbox, ledger_dir=None)` with absolute paths. The default ledger is the mailbox's `.transport_once` directory. Both directories must reside on the same local POSIX filesystem.

| Method | Return and behavior |
| --- | --- |
| `claim(pending_path)` | Returns `ClaimResult`. It reserves a UUID durably and atomically renames a new pending file into the claimed space before returning `new`. |
| `execute(claim, callback)` | Recommended dispatch entry point. Consumes the live new-claim capability once, invokes `callback(payload)` once, then internally completes and publishes its response. Callback must return a JSON object. |
| `complete(claim, response)` | For an existing bridge dispatch path: persist its JSON-object response cache, then the executed ledger record, then publish. This method itself invokes no callback. The caller remains responsible for dispatching exactly once when using this lower-level API. |
| `publish_cached(claim)` | Only accepts `cache` disposition; republishes its authenticated durable response without native or stub execution. |

`ClaimResult` fields are `disposition`, `request_id`, `pending_path`, `claimed_path`, `payload`, `reason`, `response`, and a private `_token`. `payload` is populated only for `new`; `response` only for `cache`. Do not log payload, response, or token in public artifacts. Use `pending_path` to retain the original mailbox request name in the private event log: after successful admission that original path has been renamed, so rereading or unlinking it as the execution source is incorrect.

| Disposition | Required bridge action |
| --- | --- |
| `new` | Dispatch its already-parsed payload once; count execution budget/native work only according to that dispatch's operation. |
| `cache` | Publish cached response. Do not increment execute budget, native invocation count, API count, or actor dispatch work. |
| `inflight` | Close the endpoint without callback execution. It means a claimed/orphaned durable artifact has no authenticated executed result; do not recover by replaying. |
| `conflict` | Close the endpoint without callback execution. Includes changed canonical payload under an existing UUID and unexpected existing response before first admission. |

Successful publication returns `PublicationResult(request_id, status, response, cleanup_complete=True, response_bytes)`, where `status` is `published` or `already_published`. This describes publication, not consumer/model acknowledgment. `TransportError` exposes `code`, `request_id`, `publication`, and `publication_state`; its exception text includes only the fixed error code. On any transport error the bridge must close the endpoint and preserve its own execution/event ledger. Do not treat an error as permission to call the native operation again.

Before closing on error, the bridge must record any attached `error.publication` just as it records a successful `PublicationResult`. A publication proven to have occurred carries its authenticated response, status, actual canonical response byte count, and `cleanup_complete=False`, even when later fsync, temporary-file cleanup, responded-record persistence, or request cleanup fails. A verified matching pre-existing destination carries `already_published` and is not charged as a newly published response. `publication_state` is `known`, `not_published`, or `unknown`; an unconfirmed publication attempt has `unknown` and no fabricated zero-cost publication. The bridge must preserve that cost uncertainty as unknown/null.

## Durable operation order

Per-UUID `flock` serializes cooperating controller operations. JSON payloads are bound by their canonical UTF-8 SHA256, so insignificant JSON formatting changes have the same identity; a semantic payload change under the same UUID is a conflict.

1. Write an immutable, fsynced `claimed` record and sync its directory. Reserve the UUID before native callback admission.
2. Use the previously captured host `os.rename` to move the pending request into `<uuid>.claimed.request.json`, then sync both directories and verify the moved input's payload binding. No unlink is needed to remove it from pending selection.
3. Admit the live callback capability once. Reentry and concurrent use of that capability are rejected. A restarted object/process has no live capability for an old claimed UUID.
4. After callback return, durably write the response cache before the immutable `executed` record. Only then attempt response publication.
5. Publish a separate response inode exclusively. Never replace an existing response. An existing target must exactly match the authenticated cache; a different target causes fail-closed `ExistingResponseConflict`. Persist `responded` after publication, then perform verified cleanup of duplicate pending input and claimed input.

Publication is observed immediately after successful exclusive link installation, before directory fsync or temporary cleanup. A newly installed response can be consumed and unlinked before the publisher finishes: it does not have to remain present for a second validation read. An existing target is still strictly validated against the cache. This avoids turning normal immediate consumer cleanup into a spurious controller failure while preserving the conflict rule.

`claimed`, `executed`, and `responded` are separate immutable UUID records. File publication uses exclusive temporary writes, file fsync, exclusive hard-link installation, and directory fsync. `responded` means a response was published, not read. The response is not hard-linked to the durable cache, so modifying a published response cannot modify that cache.

A failed publication leaves the executed result available for cache-only redelivery. A failed/no-op cleanup is detected by checking the removal postcondition and raises a transport error; the executed ledger still prevents callback replay. If response-cache persistence succeeds but executed-record persistence fails, restart treats the UUID as inflight and refuses execution or cache publication. A crash before callback can also leave an inflight UUID with zero executions: the safety choice is to refuse ambiguous work rather than guess whether it ran.

The module captures host open/read/write/close/fsync/stat/fstat/mkdir/rename/link/unlink and lock operations before the native boundary. Controller I/O directly uses those capabilities, rather than mutable `os` globals or `Path` methods. Tests verify that later simultaneous global `os.open/read/write/close/rename/unlink/mkdir`, `Path.open/write_text/mkdir/unlink/rename`, and built-in/IO open no-ops do not affect controller initialization, claim, callback completion, cache publication, or cleanup. The helper methods also accept path-like arguments for controller artifact integration.

Relevant implementation entry points are `claim` at line 224, `execute` at line 275, `complete` at line 293, `publish_cached` at line 322, and `_publish_locked` at line 330. `_write_immutable` at line 104 implements durable exclusive installation; `_remove_verified` at line 94 detects ineffective cleanup.

## Stress coverage

| Fault or boundary | Observed synthetic result |
| --- | --- |
| Repeated pending UUID during execution | Existing claim returns inflight; original callback runs once. |
| Duplicate delivery after completion | Only authenticated cache publication; no additional callback. |
| Unlink raises after accepted execution | Cleanup fails closed; duplicate remains cache-only. Callback count remains one. |
| Unlink silently has no effect after accepted execution | Postcondition detects failure; duplicate remains cache-only. Callback count remains one. |
| Delayed cleanup with concurrent duplicate delivery | UUID lock and executed record prevent a second callback; duplicate resolves to cache. |
| Matching response already present for an executed UUID | Accepted as the same cached publication; no replacement or callback. |
| Harmful response appears after callback | Cached result and executed ledger persist; conflicting target is preserved and publication fails closed. Callback count remains one. |
| Harmful response exists before first claim | UUID is blocked durably; no callback, including after the harmful response is removed and a controller restarts. |
| Response publication fails | Executed result exists before publication attempt; later delivery republishes cache only. |
| Response installed, then fsync or temporary cleanup fails | Error carries known newly published response and byte count; no callback replay. |
| Responded-record persistence fails after publication | Error carries known newly published response and byte count; no callback replay. |
| Matching existing response, then duplicate cleanup fails | Error carries `already_published`, preserving cost scope without charging a new response. |
| Consumer immediately reads/unlinks a new response | Publisher completes without a spurious missing-response error; authenticated publication bytes remain countable. |
| Same UUID with changed payload | Conflict; no callback or cached-publication authorization. |
| Full global filesystem monkeypatch | Captured host operations continue to work for initialization, claim, execution and cache; each callback runs once. |
| Restart after executed result | Cache-only behavior in a new object and an independent process. |
| Restart after callback but before result persistence | Inflight, no callback retry in a new object or independent process. |
| Restart after claim but before callback | Inflight with zero callbacks; intentionally abandoned claim is separately counted. |
| Cache persisted but executed-record publication fails | Inflight after restart; no guessed execution recovery. |
| Cache corruption | Integrity failure; no callback replay. |
| Response tampering | Existing-response conflict; durable cache remains unchanged. |
| Concurrent reuse of one live claim capability | One callback; second admission rejected. |
| Batch stress | 128 callback UUIDs; 2,048 cache deliveries across eight threads; no extra callbacks. |

## Limits and later validation

This implementation establishes at-most-once transport admission when the bridge honors the API and retains its ledger. It cannot atomically transact arbitrary native side effects with filesystem records. Ambiguous claimed states remain unavailable and may require a separately authorized diagnostic; automatically rerunning them would violate the guarantee. Exactly-once task completion, model consumption, native safety isolation, and algorithmic benefit are not established.

Durability relies on local POSIX rename/link/flock/fsync semantics and a retained, trusted controller ledger. Removing or replacing that ledger, using unsupported/network filesystems, importing after the guard has already patched functions, or bypassing the API removes the tested boundary assumptions. Tests simulate controlled fault windows and process/object restart; they are not a power-loss/filesystem-corruption certification.

The old DEV24 outcome and transport-confounded index remain unchanged. This diagnostic does not repair its grade or infer a once-only counterfactual score/cost. A separately frozen bridge integration is still needed before any new native run, and the narrow classical control and scientific R1/R3/R4 claims remain untested here.
