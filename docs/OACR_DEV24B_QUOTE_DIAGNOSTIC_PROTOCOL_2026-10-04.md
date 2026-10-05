# DEV24-B paired quote diagnostic — 2026-10-04

This is a prospective, single-task native diagnostic. It tests whether changing only data-field quoting changes producer acceptance. It is not a new actor, an original-batch retry, a modification of original results, or an OCAR survival claim. No world, API, model, evaluator, or diagnostic experiment was started while authoring the runner and this protocol.

| Scope | Registration |
| --- | --- |
| Task SHA-256 | `ea980c2b3fe30c2479b7eeec44e1abfba374a3b34b0811d567fe70de3ee51086` |
| Family SHA-256 | `6410b74c66b363243f508ed0e1dd0c943cb54b8155d25a1c68fba349c70e80a0` |
| Arms / fresh worlds | 2 / 2 |
| Tasks / families | 1 / 1 |
| Actor model calls | 0 |
| Ground truth during native execution | Disabled |
| Native parameters | Seed 123; 40 interactions; 20-second native code timeout |
| Controller budgets | 1,200 seconds through native/barrier phases; 120-second producer grading deadline |
| Grade attempts | Once per arm, only after both worlds have closed |
| Replacements / reruns | None; a failed attempt is terminal |

Execution registration is completed on 2026-10-05 after the single-agent restart. All twelve canonical shared asset hashes are checked in preparation, parent verification, and each fresh worker before any world is initialized. A newly mismatched shared asset was restored from locally verified author bytes before registration; no diagnostic had started. Its cause is unknown and its hash/size-only record is separate.

Native-step elapsed time, requester records and generated receipt bytes are retained, including observable work in failed steps. Public results report known subtotals, completeness flags, parent elapsed time and grading attempts. The fixed diagnostic executes zero actor-model calls; root code authoring/review uses a model and its tokens/billing are unexposed. These scopes must not be combined into a zero-cost project claim.

## Legal derivation and private payloads

The public runner contains generic templates and hashes. It derives task identity only from the explicitly authorized index in the original private selection mapping, and verifies that identity and family against the original recovery freeze. It reads only the original rendered prompt and selected actor-native code/receipts at events 32, 45, 48, 56, 61, 69, 72, 75, and 78. Selected code/receipt hashes must match the already audited values. Reading stops before original grading events; nonselected event JSON is not decoded.

The runner never reads task gold, expected answers, evaluator reports, private databases/state, separate task examples, or another task's trace. The original private artifacts and original producer/results are immutable. Author core-source hashes and the frozen original bridge are verified. The installed native API modules are pinned by their actual SHA256 bytes during preparation and execution. If tracked by the author revision, they must also match its Git blobs. These installed app modules are not tracked in the ACE checkout used here; their hash pin is not a Git provenance proof. Both arms use these same registered native bytes.

Private generated payloads preserve the complete legal native snippets, including their original task literals. Original supervisor credential discovery and public API discovery/login code are reused without adding private facts. The original task's column contract is extracted only from its actual instruction suffix and embedded in the private validation snippet. The public runner and freeze contain no task text, destination, identity, credential, record names/IDs, or raw actor code/receipt. Private directories are outside both repositories, mode 0700; files are mode 0600. Native output namespaces are new and never overwrite original worlds.

## Arms and exact scope of change

**A: quote-all reproduction.** Execute the original nine accepted native snippets byte-for-byte, excluding the two original bridge-rejected attempts. This reproduces the original data-field serializer. Rejected original snippets had zero native calls and do not affect the native mutation sequence.

**B: minimal quoting.** Execute the same snippets, changing only the complete `csv_quote` function source region at event 69. The replacement quotes a field only if it contains a comma, quotation mark, carriage return, or newline, and doubles embedded quotation marks. Code outside that function remains byte-for-byte identical; an AST comparison also verifies that every other statement is unchanged.

Both arms preserve source selection, pagination and empty-page termination, record-ID union, missing-record retrieval, record order, artist order and separator, header bytes, line terminator, destination, overwrite behavior, directory creation, file creation/read-back, account deletion, and completion sequence. The added parser/check snippet is identical in both arms and makes no business API call. Consequently each arm has the original nine native steps plus one additional check step, with the same original business API sequence. Acknowledgments are not treated as independent state truth.

## Preparation and Git freeze

`--prepare` verifies public source and legal provenance, performs the frozen bridge's `check_actor_ast` on every generated native snippet, creates private A/B payloads and metadata, and writes a public freeze. It does not import AppWorld or Task, initialize a world, or call any API/evaluator. It refuses an existing new private directory or freeze.

Use a new private root and set `--public-root` to `experiments/oacr_residual_dev24b/diagnostic/`. The generated public freeze is `diagnostic/freeze.json`; the terminal public record is `diagnostic/RESULT_2026-10-04.json`. The freeze contains the runner/protocol/original-bridge/source hashes, original recovery-freeze hash, private metadata/payload hashes, budgets, ordering barriers, and all four interpretation branches.

The root reviews preparation and stub results, then commits the runner, this protocol, and the generated freeze through Git. The root alone launches `--run --freeze <path> --freeze-commit <full-40-character-commit>`. Before any worker starts, the runner requires those public files and the original bridge to match their committed Git contents, rechecks source and original recovery freeze, rechecks all private hashes and frozen AST validation, and exclusively creates a first-attempt marker. Any later change requires a new registration; it does not resume this attempt.

Generic invocation, using root-selected local paths:

```bash
python experiments/oacr_residual_dev24b/paired_quote_diagnostic.py \
  --prepare --source-root "$DIAGNOSTIC_SOURCE_ROOT" \
  --original-private-root "$DIAGNOSTIC_ORIGINAL_PRIVATE_ROOT" \
  --private-root "$DIAGNOSTIC_NEW_PRIVATE_ROOT" \
  --public-root experiments/oacr_residual_dev24b/diagnostic
```

`--run` takes the same roots plus `--freeze` and `--freeze-commit`. The selected interpreter must provide the pinned native dependencies. Neither preparation nor execution accesses a model or spawns an agent.

## Independent verification and two barriers

Each arm runs in a separate persistent worker process, keeping AppWorld's process-global state isolated. The parent starts A and waits until A reaches the deletion barrier before starting B. A retains its own world while B executes; the workers do not replace one another's global world.

After the original public file read-back, an independently written, import-free CSV parser checks both prepared and saved contents. It handles quoted/unquoted fields, doubled quotation marks, embedded newlines, record boundaries, empty fields, and invalid transitions. It verifies the two requested columns, column widths, exact row order and row set, row count, unique output-pair count, union/record cardinality, and equality of prepared and saved bytes. A separate host standard-library parser must agree. Host reconstruction then verifies that each saved byte string follows its registered quote policy and unchanged header/line rules. Host-side helpers never become actor-visible native globals.

The public checkpoints contain only hashes/counts. Full parser payloads remain private. Before any account deletion, the parent requires equality across arms of source-class counts, source-component and union hashes, record-ID-order hash, parsed record-order/set hashes, header hash, saved-content parsed-order hash, native attempts, and native API-call counts. Raw saved bytes are expected to differ by quote policy; semantic read-back must match, and each byte string must independently satisfy its policy. The source union and record order therefore cannot silently differ between fresh worlds.

**Barrier 1: both pre-delete checkpoints and all paired invariants must pass.** Only then does the parent write immutable, freeze-bound deletion authorizations for both workers. Otherwise neither arm deletes or grades, even if the other arm passed locally. No score interpretation is permitted for a failed paired invariant.

Each authorized worker executes the original deletion and completion snippets, persists the actual native end state through the same producer controller cleanup operations, saves native logs, and closes its world. These host cleanup operations do not inspect state contents. Original native safety guards remain enabled with the original constructor settings.

**Barrier 2: both worlds must acknowledge successful close before either grade authorization is written.** Producer `evaluate_task` is then called once per closed arm, with the original error-suppression behavior. `save_report=False` avoids generating a report; it changes no scoring checks. Only the aggregate `tracker.success` bit is consumed as a success count. No actor can see grading feedback. A failed/timeout grading attempt is recorded once and never repeated or converted into an inferred outcome.

Before every `world.execute` and grading call, a private exclusive, fsynced ledger records the attempt. A timeout or interrupted call cannot trigger a compensating execution. Host file primitives are captured before native imports/guards; they are used only by the controller to retain artifacts and handoffs, never to grant native code filesystem access or bypass a native guard. Runtime failures, missing checkpoints, invalid authorizations, failed close, or exhausted budgets terminate the attempt without replacement.

## Pre-frozen interpretation branches

Only a fully valid pair with both independent checks, both cross-arm invariants, both deletion/completion sequences, both closes, and two returned producer grades enters this table. Entries are producer success **counts**, not evaluator labels or explanations.

| A count | B count | Registered interpretation |
| --- | --- | --- |
| 0 | 0 | Quote policy alone is insufficient. This kills the narrow quote-only explanation in this diagnostic; it does not establish a new core mechanism or OCAR residual. |
| 0 | 1 | Acceptance is sensitive to quote policy under the controlled record set and mutation sequence. This supports the narrow serialization/acceptance explanation; it does not establish an evaluator defect or generalize beyond this task. |
| 1 | 0 | Reverse sensitivity: minimal quoting does not fix this task. Do not infer support for the proposed correction. |
| 1 | 1 | Original failure is not reproduced in this pair; quote policy does not discriminate the outcomes. |

Any invalid or incomplete pair records `status: control_invalid`, `branch: control_invalid_no_quote_conclusion`, and fixed A/B statuses and native/deletion/grading attempt counts, including explicit `not_attempted` grades. It is not treated as a tested surviving control. Repairing a control requires a separate registration before deciding how to proceed with DEV24-B.

Every written terminal record includes `diagnostic_terminal_record: true`, `arms: 2`, and both arm statuses. This is a terminal-accounting field, not proof that the diagnostic was valid or that its conclusions qualify. The root's DEV24-B selection preparation can require the field while separately respecting invalid-control registration.

The diagnostic still covers only one task and one family. No branch meets the residual-first replication threshold, establishes an architecture-specific increment, or supports a novelty/generalization claim. A successful pre-delete check alone is not R3 survival evidence.
