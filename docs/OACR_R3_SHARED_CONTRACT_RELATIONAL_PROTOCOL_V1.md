# OACR-R3 Protocol v1 — Shared-Contract Relational Adequacy Matrix

**Date:** 2026-09-28  
**Status:** preregistered exact same-contract experiment  
**Carrier:** frozen OACR-R1 raw graph response  
**Raw carrier SHA256:** `3d3852ff72382c171e3a5496336767809b9455541fa2604f7b6857a8e69457df`

## 1. Purpose

R2 used one future deletion chosen separately for each constructed state pair. R3 removes that coupling.

All states are evaluated under the **same globally frozen deletion alphabet**. The experiment derives the operational partition first and only then compares candidate representation partitions against it.

## 2. State bank

Reconstruct the prepared DAG (G) exactly as in R1/R2.

Let

[
E_{m cand}=TC(G)setminus E(G).
]

Create one base state plus one state for every redundant entailed edge:

[
S_0=G,
qquad
S_e=Gcup{e},quad ein E_{m cand}.
]

On the frozen carrier this should produce 272 states.

Verify for every state:

[
TC(S_e)=TC(G).
]

Thus the complete registered current-closure READ interface is identical across the entire state bank.

## 3. One shared action alphabet

For every asserted base edge (fin E(G)), compute its **base deletion impact**

[
J(f)=|TC(G)	riangle TC(G-{f})|.
]

Sort all asserted edges by:

1. (J(f));
2. lexical edge identity as deterministic tie-break.

Select 64 unique edges at evenly spaced indices across this sorted list.

The selected action alphabet:

[
mathcal A={operatorname{del}(f_1),ldots,operatorname{del}(f_{64})}
]

is determined only from the base graph, before any augmented-state outcomes are inspected.

Every action edge is present in every registered state.

## 4. Exact H=1 operational signature

For each state (S) and each action edge (f_k), compute the complete post-deletion transitive closure:

[
TC(S-{f_k}).
]

The exact H=1 operational signature is the ordered vector of closure hashes.

Two states are H=1 equivalent iff all 64 complete post-deletion closures are exactly equal.

This yields the required operational partition (O_1).

## 5. Candidate representation partitions

### R0 — current semantic closure only

All states are represented only by the complete current transitive closure.

By construction this is one representation class.

### Rfull — full asserted-edge identity

Use the complete asserted edge set of each state.

This separates all distinct augmented states.

### Rsupport — action-endpoint support profile

For every selected action edge (f_k=(x_k,y_k)), record the exact number of directed paths from (x_k) to (y_k) in the current state.

The 64-dimensional path-count vector is computed before deletions and without inspecting deletion outcomes.

This is an intermediate candidate representation motivated by revision support, not an operational signature.

## 6. Directional adequacy gap

Under the uniform distribution over registered states, compute for each candidate representation (R):

[
U(R)=H(O_1mid R),
]

[
E(R)=H(Rmid O_1).
]

Also report:

- representation class count;
- operational class count;
- pairwise under-refinement;
- pairwise over-refinement;
- variation of information (U+E).

Interpretation:

- (U>0): representation is too coarse for this shared deletion contract;
- (E>0): representation retains distinctions unnecessary for this shared deletion contract.

## 7. Strong target

The strongest possible exact result is an intermediate operational partition:

[
1 < |O_1| < 272.
]

Then on the *same contract*:

- R0 must under-refine if (|O_1|>1);
- Rfull must over-refine if (|O_1|<272).

This would establish both directional errors without pair-specific action selection.

## 8. Boundaries

R3 is still a controlled graph construction.

It does not establish:
- prevalence in Wikidata;
- natural historical evolution of P279;
- universal necessity of path counts;
- novelty of conditional entropy / partition comparison.

Its role is to provide an exact same-contract adequacy matrix against which the OACR measurement object can be audited.
