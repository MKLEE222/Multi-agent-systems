# DEV24 recovery index 1: cold transport audit

Date: 2026-10-04. Scope: infrastructure and actor-legal transport evidence only.

## Finding

Index 1 is a **transport-confounded native attempt**, with an independently evidenced mailbox replay and a terminal controller response-publication failure. It must not be presented as a clean actor failure or evidence for a research R1/R3 residual. The terminal evaluated failure remains the frozen recorded outcome; this audit does not change its grade, denominator, producer, or native state.

The same execute request UUID was processed **three times**, producing native steps 4, 5, and 6. Its UUID SHA256 is `4bc5c8f5a70ea9f3368a8724cef79461087c2f352d625c5b2fa218faca38c5fa` (SHA256 of the UUID string, excluding the mailbox suffix). All three canonical request payloads have SHA256 `82099af835592706a472d92fbe28f61c9b6dc98b7c96550f779ab4a377f42014`. This conclusion follows from the local chained request/execute events, independently of the actor's reported send count.

The exact low-level cause of the request file's retention or reappearance is **unresolved within the permitted evidence**. The bridge nevertheless has a definite admission defect: it selects a pending request again without claiming it or checking whether its UUID has already executed. File existence at response publication detects the problem only after another native execution has happened. This is avoidable transport behavior, not an unavoidable native-task limitation.

## Evidence boundary and integrity

Inspected:

- Public `experiments/oacr_residual_discovery/native_batch_bridge.py` and `actor_client.py`.
- Public initial `freeze.json`, `recovery/freeze.json`, and `recovery/task_1_summary.json` in that experiment directory.
- Local `residual_dev24_recovery_private/events_1.jsonl` and `native_host_1.log`, including the controller traceback stored in the event log.
- Relevant public SDK guard and logging paths: `src/appworld/common/safety_guard.py`, `src/appworld/environment.py`, and `src/appworld/requester.py`.

No task gold, evaluator report, database, private native state, other trajectories, test examples, task/world/API execution, grading invocation, actor-model invocation, or downstream delegation was used. No actor task text, raw task identity, credentials, raw actor code, raw receipt, or raw UUID is reproduced here. Only this audit document was written.

The event file contains 64 events. Its sequence is contiguous, and every `previous_sha256` matches the SHA256 of the preceding stored line, starting from the all-zero initial value. Its byte hash and final chain hash match the public summary. The host log is empty and provides no additional failure explanation.

| Artifact | SHA256 |
| --- | --- |
| Frozen public bridge, matching both freezes | `d762eba3dd71bcd34e01c481af72ca82e7581778be238ac5f36ef946b8220b7f` |
| Frozen public client, matching both freezes | `4a9b2182a0998d06294e477d5f0aca66c61ec41671e1ec65f36df2de4b7f46df` |
| Initial freeze | `cf9530a3fe8e5d9c87a17113d3f15356e77d97c66fd848e48434ab3845b15648` |
| Recovery freeze, matching summary reference | `7d2cb3c3ef337b2f0a7186db3e75e421045a871de6f4077a11c8a9f75ede3bb9` |
| Recovery index-1 summary | `6858c08ef49856b15db76f5dfddb9e5dd87b224d36a0614aec2c477542afe328` |
| Actor-legal event file | `e202c52a20eb1497ebb7ac8cb9044b230915754168e902d32514e5d2d7e15e46` |
| Final event-chain link | `486d05cb1642016a0f40f9fba2007cfc40867b0c9e4195195966dba98cf250b6` |
| Empty native host log | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Public SDK safety guard, matching recovery freeze | `fa105c1bc55bc9fc3dba70f414bdfcb43e05fcede06e63477ceb712037044da7` |
| Public SDK environment, matching recovery freeze | `f1ede383bc5833af31c3af1d99d987b8cbdd49c2f7a0bdda227b5e006e70c618` |

Both freezes retain identical implementation hashes and actor/transport budgets: 40 execute requests, 20 seconds per native code execution, 1200 seconds for the actor endpoint, and 2000 characters per page. Recovery explicitly discloses an infrastructure reattempt; it records no task replacement, score-conditioned retry, or OACR intervention. This audit evaluates the recovery attempt without treating it as an undisclosed clean first attempt.

## Reconstructed operation sequence

There are 27 request events but only **25 distinct observed mailbox request UUIDs**: 15 start UUIDs, 6 receipt-page UUIDs, and 4 execute UUIDs. The only repeated UUID is the fourth execute UUID above. No finish request appears.

| Event sequence | Operation or outcome | Native step | Observed requester-call delta |
| --- | --- | --- | --- |
| 1 | Ready | — | — |
| 2–31 | 15 distinct start requests and 15 responses; complete prompt delivered | — | 0 native executions |
| 32 / 33 / 34 | First execute UUID: request / native execution / response | 1 | 3 |
| 35–42 | Four receipt-page requests and responses | — | 0 native executions |
| 43 / 44 / 45 | Second execute UUID: request / native execution / response | 2 | 7 |
| 46–49 | Two receipt-page requests and responses | — | 0 native executions |
| 50 / 51 / 52 | Third execute UUID: request / native execution / response | 3 | 6 |
| 53 / 54 / 55 | Fourth execute UUID: request / native execution / response | 4 | 20 |
| 56 / 57 / 58 | **Same fourth UUID**: request / native execution / response again | 5 | 20 |
| 59 / 60 | **Same fourth UUID**: request / native execution again | 6 | 20 |
| 61 | `FileExistsError`, controller actor phase, while publishing step-6 response | — | — |
| 62 | `FileExistsError` again while attempting final termination response | — | — |
| 63 | Actor stop: `controller_error`, 6 execute requests | — | — |
| 64 | Recorded terminal grade: evaluated once, success false | — | — |

The first three execute UUID SHA256 values are, in order:

1. `2cb99559ce4b0e18d21b8390a9d885621e3557be8b893f9fc03e766bf48c4dbc`
2. `6a5bbdeeb7273aa376d258279fd1b1dcc9c66221173f8897e5decc0cbf672bd6`
3. `3d8031bac214517e1e92107be571e53ee7796876292f94d27770353ac0a7638d`

The repeated request is logged at actor elapsed times approximately 177.914, 181.126, and 184.284 seconds. Endpoint stop is approximately 185.876 seconds. Every native row has one environment-interaction delta, native execution true, and no parse, AST, or native-execution error. Steps 4–6 have identical code hash, receipt hash, and byte counts; identical receipts do not establish that repeated APIs were harmless or that the final state matches a once-only trajectory.

Response events total 26: 15 prompt responses, 6 receipt-page responses, and 5 native-receipt responses. Steps 4 and 5 each publish a first receipt page with further pagination available. There is no later receipt-page request for either, no response event for step 6, and no observed actor finish declaration. Publishing a response is not evidence that the actor read it.

## Failure location and boundary behavior

Relevant public bridge functions and line locations:

| Path and function | Lines | Relevance |
| --- | --- | --- |
| `native_batch_bridge.py::write_json_new` | 115–128 | Refuses an existing response target at line 119; otherwise writes a temporary file, links the response exclusively, then unlinks the temporary file. |
| `native_batch_bridge.py::serve` pending selection | 541–550 | Polls all pending request files and selects the oldest. No atomic claim, executing/consumed UUID registry, or replay check precedes dispatch. |
| `native_batch_bridge.py::serve` execute dispatch | 582–656 | Increments execution accounting and invokes native execution before response publication. Logs each completed native attempt durably. |
| `native_batch_bridge.py::serve/respond` | 484–501 | Publishes the response, updates transport counters, logs it, then unlinks the request at line 501. The response log does not verify request removal. |
| `native_batch_bridge.py::serve` response and exception handling | 690–713 | Response failure exits the actor loop; final response uses the same request/response paths and can fail again. |
| `native_batch_bridge.py::serve` endpoint closure and counts | 699–719, 752–795 | Stops watchdog, disables guard, closes actor endpoint, then records native counts and fixed outcomes. |

The controller traceback at event 61 contains the call chain `serve` line 690 → `respond` line 488 → `write_json_new` line 119. Thus the terminal exception is the **pre-existing response destination check**, after the sixth native execution, rather than an exception inside native execution, an exclusive temporary-file collision, or an actor budget limit. Event 62 shows the final-response attempt hits the same exception class. The recorded elapsed time and request count are well below the frozen endpoint limits.

A successful `respond` logs its response before `request_path.unlink()`. The same request path is selected afterward at events 56 and 59. Therefore the earlier deletion did not make that request permanently absent from pending selection. The logs do not record unlink return behavior, post-delete existence, filesystem mutation provenance, response consumption, or raw filesystem-function identity. They cannot distinguish silent ineffective deletion from another process recreating the same path.

The SDK provides a concrete reason to treat host transport and native execution as separate boundaries. `SafetyGuard.enable` (`safety_guard.py`, lines 258–309) patches process-global functions to silent no-ops, including `os.unlink` (listed at line 37) and `Path.unlink` (line 81). `SafetyGuard.disable` (311–319) restores functions captured during guard construction (209–224). Native `AppWorld.execute` enables/disables this guard (`environment.py`, 478–479 and 548–554), and the bridge additionally calls disable before responding (641–642). Consequently it would be an **overclaim** to assert from these logs that the guard was definitely still enabled, that its captured unlink was definitely poisoned, or that this was the precise retention mechanism. The source establishes a shared-process filesystem hazard; the event trace establishes the replay and missing admission protection.

Client behavior is also explicit. `actor_client.py::main` assigns a fresh UUID once per invocation (34–43), waits for that UUID's response (44–55), reads and removes its response (56–58), and contains no execute retry loop. A communication timeout reports `retry_authorized: false` (51–54). Termination checks (31–33 and 46–50) return an actor-terminated response with grading feedback withheld. The event log's four distinct execute UUIDs support four distinct observed submitted mailbox identities; it does not independently expose every client invocation or prove what response any invocation read. Repeated response publication can race with response removal. An existing response must never become permission to repeat a native action.

## Counts and scientific attribution

The frozen summary correctly describes the actual bridge-observed work: **6 native execute attempts, 6 environment interactions, and 76 observed requester records**. The event ledger agrees: 3 + 7 + 6 + 20 + 20 + 20 = 76. Of those records, **40 occurred during the two extra invocations of an already-processed UUID**. Requester count refers to observed records, not billing, distinct effects, or all hidden server work: `RequestTracker.add_request` appends its tracked request records (`requester.py`, 75–84), while request-count reset changes an offset rather than discarding history (90–91); `Requester.requests` exposes that history (340–348).

Do not silently replace six attempts with four, or relabel 36 as a measured corrected-run cost. The first invocation per UUID has a descriptive sum of 36 requester records, but no once-only counterfactual run was observed. Replays may affect native state and subsequent behavior; this audit did not inspect state or API effects. Keep the original 76 and disclose the 40 replay-associated records separately.

The summary records 23,122 generated native-receipt bytes, 19,664 mailbox-delivered receipt-text bytes, 61,212 mailbox-response bytes, and 5.374 seconds of native execute elapsed time. These include the recorded repeated work and publications. Actor-visible receipt bytes, client timeout counts, model calls, tokens, and model cost are unexposed. Mailbox publication counters do not establish model consumption. No frozen high-cost threshold is triggered, but that does not make the work transport-clean.

The actor endpoint was cut off by a controller failure, with `actor_finish_reason` null and no finish event. The recorded failed final grade is therefore **infrastructure-confounded**. Neither a particular research mechanism nor a claim that infrastructure was the sole cause of the grade follows. The permitted evidence establishes transport disruption and repeated native invocation; it does not establish what a correct once-only execution would have scored. Overall batch totals and the other failing index were not independently audited here.

## Proposed future transport control — not implemented or tested

The minimal required property is **at most one native invocation per accepted mailbox UUID**, even if a request remains/reappears or a response is consumed before cleanup. Preserve the native task, safety guard, evaluator, action rules, and budgets.

1. Claim the request atomically outside the native monkeypatch boundary before execution, removing it from the pending glob. Register its UUID as accepted/executing before invoking native code; retain a consumed-UUID/result record afterward. A duplicate UUID must return a cached transport result or close the endpoint without another native invocation. Never infer action authorization from absence of a response file.
2. Use controller-owned filesystem operations whose behavior cannot be changed by the actor/native guard. A separate controller/native worker process boundary is the stronger option. A smaller in-process diagnostic can retain original host filesystem functions before native imports/patches, use those only for transport, and verify the claim/removal postcondition. An ineffective claim/removal must stop dispatch before another native action. Merely adding another guard-disable call is insufficient as an at-most-once guarantee.
3. Publish each execution's cached response without rerunning execution; log claim, execution-start/completion, publication result, verified cleanup, and endpoint closure using non-sensitive UUID hashes. Treat a publication error as a transport error after executed work, preserving the ledger and preventing redelivery from becoming re-execution. Preserve the client prohibition on retrying execute after timeout.

A future transport-only diagnostic should use a synthetic execution stub and exercise ineffective unlink, repeated pending UUID, delayed response removal, duplicate delivery, and publication failure. Its observable criterion is one stub invocation per UUID and no native-task/API invocation. Any later native comparison requires a separately disclosed, newly frozen control; the existing attempt must not be rerun or repaired in place. No such diagnostic, control, implementation change, or new native attempt was performed by this audit.
