# OACR-COMPOSE-R Building Preliminary Result

**Date:** 2026-09-29  
**Protocol:** \`docs/OACR_COMPOSE_R_MINCUT_PROTOCOL_V1_2026-09-29.md\`  
**Protocol commit:** \`e382f12b7f446fc727aa72d8f374c656ffb005fc\`  
**Carrier:** accepted R4-building artifact \`oacr-r4-v2-building\`, artifact ID \`11003190307\`  
**Status:** structural result reproduced locally from the frozen artifact; GitHub-workflow acceptance record still pending

## 1. Primary result

The accepted H1 R4-building state bank contains:

- 271 redundant augmented distinctions;
- 64 frozen registered deletion actions;
- 22 H1-active distinctions;
- 249 H1-inactive distinctions.

The prospective COMPOSE depth audit found:

\[
d_A(e)=1 \quad\text{for }22\text{ distinctions},
\]

and

\[
d_A(e)=\infty \quad\text{for }249\text{ distinctions}.
\]

No registered distinction has

\[
d_A(e)=2.
\]

Therefore the frozen building carrier contains no minimum depth-2 COMPOSE activation witness under the existing 64-action deletion universe.

## 2. Independent monotonic verification

A second verification avoids minimum-cut computation.

For every one of the 249 H1-inactive distinctions, remove **all 64 registered deletion edges simultaneously** from the base graph.

All 249 candidate endpoints remain reachable.

Because deletion is monotone, if a candidate remains reachable after deleting the entire registered action set, it remains reachable after deleting any subset of that set.

Therefore every H1-inactive distinction is inert under every finite composition drawn solely from the registered action universe.

Combined with the already accepted H1-active set:

- 22 distinctions have registered-action cut depth 1;
- 249 have infinite registered-action cut depth.

This independently excludes depth 2, depth 3, and every higher finite depth for this carrier/action universe.

## 3. Relation to developmental R3

The exploratory developmental R3 scan showed the analogous split:

- 100 distinctions: cut depth 1;
- 171 distinctions: not disconnectable by the registered 64-action universe;
- no finite cut depth greater than 1.

Thus both exact relational carriers inspected so far have the same qualitative structure:

\[
\text{WRITE-active at H1}
\quad\text{or}\quad
\text{compositionally inert forever under the frozen panel}.
\]

This is not promoted as a cross-domain law. It is a carrier/mechanism boundary result.

## 4. Scientific interpretation

The relational deletion mechanism is now better treated as:

- a strong exact WRITE / WACT carrier;
- an exact representation-redesign carrier;
- a negative/control carrier for delayed COMPOSE activation.

It should **not** be expanded or retuned merely to manufacture an H2 positive.

The negative result is informative because it rejects a trivial story:

> longer action sequences automatically expose every hidden relational distinction.

They do not on these frozen action universes.

## 5. Planning consequence

Primary COMPOSE search moves to carriers where earlier transformations can change the semantic interface of later transformations:

1. SQEC-style dynamic qualification / legality / recoverability;
2. Git/history operations with state-dependent later semantics;
3. learned persistent state under sequential edits.

The relational carrier remains as the exact commutative control.

## 6. Acceptance boundary

This record does not yet claim final workflow-level acceptance for the new COMPOSE-R scan.

For final acceptance:

- persist the structural scan implementation;
- run it against the frozen R4-building artifact in GitHub Actions;
- independently verify the all-64-deletions monotonic certificate;
- record hashes and run IDs.

No scientific rule may change based on this preliminary result.
