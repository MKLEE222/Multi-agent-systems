# OACR-COMPOSE-G Engineering Record — 2026-09-29

**Scientific protocol:** \`docs/OACR_COMPOSE_G_GIT_DEPTH2_PROTOCOL_V1_2026-09-29.md\`  
**Frozen protocol commit:** \`449fcf31d4f102e43f14c207e562ce08f5c94c83\`

This record separates workflow/runtime repair from scientific outcome.

## 1. Original full-H1 reconstruction run

Run:

- \`36563926836\`
- workflow: \`OACR COMPOSE-G Depth-2\`
- trigger issue: #47

Design:

- rebuild the accepted G5 validation H1 contract directly from pinned \`git/git\`;
- then execute the frozen H2 protocol;
- independently replay selected H1/H2 pairs.

This run remains active at the time this record is written. No protocol change is authorized from its outcome.

## 2. Fast run attempt 1 — workflow-expression failure

Run:

- \`36564726128\`
- trigger issue: #48

Purpose:

- engineering optimization only;
- use the already accepted G5 held-out artifact as the frozen H1 input;
- retain independent native H1 replay for selected pairs.

Failure:

The YAML file contained an escaped GitHub expression, yielding a repository argument with a leading backslash and invalid authentication context.

The job failed in:

- \`Download accepted G5 held-out artifact\`.

It did **not** clone \`git/git\`.
It did **not** execute the COMPOSE producer.
It did **not** execute any H2 outcome.

Repair:

- remove the unintended backslash from GitHub expressions;
- workflow-only commit \`c0fab05ad30e1dca1acc355e60fb019b8f9daaf0\`.

Scientific protocol unchanged.

## 3. Fast run attempt 2 — parser plumbing failure

Run:

- \`36564840832\`
- trigger issue: #49

The accepted G5 artifact download, pinned \`git/git\` clone, and Python compilation succeeded.

Failure:

The runner contained the fast-path implementation internally but the \`argparse\` declaration for \`--g5_json\` had not been persisted.

The job failed immediately with:

\`unrecognized arguments: --g5_json ...\`

It did **not** enter the COMPOSE producer body.
It did **not** execute any H2 outcome.

Repair:

- add the missing parser argument;
- runner commit \`79da53830c097fa48385b3006585d29df22b7adc\`.

Scientific protocol unchanged.

## 4. Fast run attempt 3 — post-outcome serialization failure

Run:

- \`36564936169\`
- trigger issue: #50

The following completed:

- accepted G5 artifact download;
- pinned \`git/git\` clone;
- compile;
- COMPOSE producer execution through pair selection, H1 composability checks, step-1 materialization, and H2 branch execution.

Failure occurred only while constructing the final summary object:

\`UnboundLocalError: commits\`

The fast path had already stored the accepted artifact counts in \`commits_count\` and \`validation_count\`, but two summary fields still referenced slow-path local variables:

- \`len(commits)\`;
- \`len(validation)\`.

Consequences:

- H2 scientific branches **were executed** in this run;
- the result JSON was not written;
- no artifact was uploaded;
- producer stdout did not print the H2 summary before the exception;
- therefore no positive/negative H2 result was exposed through the persisted record or workflow log.

From this point onward, scientific rules are locked even more strictly: no pair, target, eligibility, signature, or acceptance change is permitted.

Allowed repair:

- replace only the two invalid summary references with the already computed count variables.

Repair commit:

- \`70bac5ae0e2ea3431026f7dbf6840e0473527922\`.

## 5. Clean persistence rerun

Run:

- \`36565160746\`
- trigger issue: #51

This rerun uses:

- the same frozen scientific protocol;
- the same accepted G5 artifact;
- the same deterministic selection;
- the same H1 composability checks;
- the same deterministic merge-commit construction;
- the same H2 signature definition;
- the same independent verifier.

Its purpose is to persist and verify the already authorized scientific execution after the serialization-only repair.

## 6. Governance conclusion

The first two fast failures occurred before any H2 scientific outcome.

The third fast failure occurred after H2 execution, so only post-outcome engineering repair is allowed afterward.

No scientific parameter or selection rule has been changed after H2 execution.


## 7. Final verified v1 disposition

Final clean run:

- `36565553671`;
- artifact `oacr-compose-g-depth2-v1-fast`;
- artifact ID `11032161050`;
- artifact digest `sha256:129b8e7439a350c39627070b013229a1e211e1de498a0e12945ee3f1cc5a55c6`.

Verified summary:

- G5 validation pairs: 48;
- accepted H1-equivalent pairs: 46;
- H1-equivalent pairs with merge-base differences: 39;
- selected v1 pairs: 16;
- `H1_NOT_COMPOSABLE`: 16;
- H2-separated: 0;
- H2-equivalent: 0;
- **H2 outcomes executed: 0**.

Independent verifier:

- checked H2 pairs: 0;
- failure count: 0;
- pass: true.

Scientific classification:

> **COMPOSE-G v1 is a verified construction/preflight underpower result, not a COMPOSE negative.**

The v1 restriction requiring the first action itself to come from the current merge-base-difference coordinates prevented all selected natural pairs from materializing a shared real first merge. The permitted successor is an outcome-blind structural preflight that broadens only first-action construction while preserving the same source, pair bank, and frozen target panel.
