# OACR-SQEC Vendored Execution Record

**Date:** 2026-09-30  
**Scientific protocol:** \`qualification_opportunity_compiler/01_protocol/OACR_SQEC_CONTINUATION_REPAIR_PROTOCOL_V1_20260930.md\`  
**Protocol commit:** \`83091035685b8d11fc1b293051285835d9c1feb7\`  
**Frozen SQEC source snapshot:** \`4f37a0af1c2cb44b2eb7eb1b187d96a2ebd34295\`

## Reason for vendoring

The first SQEC Actions run \`36666435504\` and its rerun failed before any workflow step received a hosted runner:

- \`runner_id = 0\`;
- zero executed steps;
- no producer invocation;
- no scientific outcome exposed.

The scientific code did not fail.

To avoid making the OACR paper depend on repository-level Actions availability, the exact minimum import closure required by the frozen producer/verifier was copied byte-for-byte into:

\`external/sqec_snapshot_4f37a0af/\`

in the main OACR repository.

## Integrity rule

Each vendored file is pinned by its original Git blob SHA from the SQEC source repository.

The authoritative manifest is:

\`external/sqec_snapshot_4f37a0af/SNAPSHOT_MANIFEST.json\`.

The main-repository workflow must recompute \`git hash-object\` for every vendored file and require exact equality with the original SQEC blob SHA before execution.

Any mismatch blocks the run.

## Scientific invariants

Vendoring does not change:

- the 8 frozen variants;
- positive-control variants 0/2/4/6;
- no-divergence controls 1/3/5/7;
- root guard;
- event alphabet;
- length-1 and length-2 continuation sequence bank;
- FULL / PROJECTED / GUARD-REPAIRED definitions;
- H1 gate;
- H2 delayed-divergence criterion;
- guard-repair coordinate;
- producer/verifier source bytes.

The main repository is only an execution host.

## Acceptance

Acceptance still requires:

\[
mismatch_1(FULL,PROJECTED)=0
\]

for all variants,

predeclared delayed H2 mismatches only in the positive-control family,

\[
mismatch_{\le2}(FULL,GUARD\text{-}REPAIRED)=0,
\]

and exact independent verifier agreement with the producer matrix.
