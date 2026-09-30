# OACR R4 Fast Independent Verifier Optimization Record

Date: 2026-09-30

Status: **ENGINEERING-ONLY VERIFIER OPTIMIZATION — building regression required before fresh-carrier acceptance**

## 1. Motivation

The frozen organization producer run completed successfully, but the unchanged v2 verifier hit its 360-minute job limit while independently recomputing Q43229.

The cancellation occurred inside the scientific verification step after:
- producer artifact download succeeded;
- verifier compilation succeeded;
- the verifier had run for essentially the full six-hour job limit.

No verifier PASS artifact was produced. Therefore Q43229 remains unaccepted.

## 2. Scientific semantics remain unchanged

The optimized verifier still independently reconstructs:

- raw page hashes and pagination order;
- exact combined JSON;
- prepared DAG;
- frozen candidate state bank;
- frozen 64-action panel;
- active/inactive matrix;
- every stored original state-action outcome signature;
- every stored compressed state-action outcome signature;
- operational partition;
- R0/Rfull/Rgate directional gaps;
- singleton, pair, and leave-one-out subcontract summaries.

It does not trust producer outcome labels when reconstructing these objects.

## 3. Optimization A — action-impact reconstruction

The producer selects actions by:

\[
J(f)=|TC(G)\triangle TC(G-f)|.
\]

Because deleting an edge from a DAG cannot create new reachability,

\[
TC(G-f)\subseteq TC(G),
\]

so:

\[
J(f)=|TC(G)|-|TC(G-f)|.
\]

The fast verifier computes these exact counts for every asserted base edge using an independent reverse-topological bitset dynamic program.

After selecting the same 64 actions, it recomputes their full post-deletion closures with NetworkX and uses those closures for all downstream checks.

Thus the bitset implementation accelerates action ranking without replacing the native closure semantics used for registered actions.

## 4. Optimization B — avoid redundant augmented closures

For a registered candidate delta \(e=(u,v)\) and registered deletion \(f\):

### Contract-inactive cell

If

\[
e\in TC(G-f),
\]

then adding the direct edge \(e\) cannot change reachability:

\[
TC((G+e)-f)=TC(G-f).
\]

The verifier therefore uses its independently computed base-after closure as the exact expected original outcome.

### Contract-active cell

If

\[
e\notin TC(G-f),
\]

the verifier explicitly constructs \((G+e)-f\) and recomputes its full NetworkX transitive closure.

Therefore every genuinely behavior-changing cell remains an explicit augmented native replay.

## 5. Compressed-side reconstruction

For a globally active Rgate state, decode(Rgate) is exactly the original \(G+e\), so the independently reconstructed original outcome is also the compressed outcome.

For base/inactive states, decode(Rgate) is exactly \(G\), so the independently reconstructed base-after closure is the compressed outcome.

All 17,408 stored compressed signatures are still checked exactly.

## 6. Q43229 expected computational reduction

The already frozen producer artifact reports:

- states: 272;
- actions: 64;
- total registered cells: 17,408;
- globally active augmented states: 26;
- action-specific active cells: 26;
- nonempty activation actions: 1/64.

Thus only 26 augmented cells require explicit post-deletion closure recomputation after the 64 independently reconstructed base-after closures.

This observation is used only to estimate engineering benefit; it does not determine which cells the verifier marks active.

## 7. Acceptance order

The new verifier cannot be used to accept Q43229 until:

1. it reproduces the already accepted building artifact exactly;
2. the building regression checks all matrices, metrics, and subcontract summaries without mismatch;
3. only then may the same verifier commit be applied unchanged to the frozen Q43229 producer artifact.

The CI workflow must enforce this order as a dependency.

## 8. Authority boundary

This is a runtime optimization after the Q43229 producer outcome exists.

It is not additional scientific evidence and must not alter:
- state selection;
- action selection;
- Rgate definition;
- native outcome schema;
- acceptance thresholds;
- claim boundaries.

Q43229 becomes scientifically accepted only if the optimized independent verifier passes unchanged after the accepted-building regression.
