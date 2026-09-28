# OACR Measurement Note — Conditional Operational Demand and Contract Basis

**Date:** 2026-09-28  
**Status:** interpretation correction after M2 second audit  
**Role:** prevent total operational entropy and action count from being misused as cross-carrier demand measures.

## 1. Conditional operational demand

Let (O_0) be the partition induced by the registered current observation before future actions are added.

For an action contract (A), let (O_A) be the resulting operational partition.

Because (O_A) refines (O_0) in the registered finite setting, define the descriptive conditional demand:

[
D(A)=H(O_Amid O_0).
]

Interpretation:

> additional class information required by the future action contract beyond the distinctions already supplied by the current observation.

When the baseline candidate representation (R_0) is exactly the current-observation partition,

[
D(A)=U_A(R_0).
]

This equality is inherited conditional-entropy algebra, not a new theorem.

## 2. Why total operational entropy is not the cross-carrier demand quantity

In M2-R all 272 registered states have the same current complete closure.

Therefore:

[
H(O_0)=0
]

and total operational entropy happens to equal conditional future demand.

In G5, the 48 same-tree groups have different tree IDs across groups.

Therefore (H(O_A)) is dominated by distinctions already visible at (H=0).

For the full G5 validation panel:

- (O_0) already has 48 classes;
- the future merge panel refines this to 50 classes;
- only two within-tree pairs require new separation.

Thus raw (H(O_A)) should not be read as “future demand.”
The relevant future increment is (H(O_Amid O_0)), which is exactly the tree-only omission gap.

## 3. Cross-carrier use

Report:

1. (H(O_0)) — baseline current-observation class information;
2. (D(A)=H(O_Amid O_0)) — future-contract increment;
3. (U_A(R)), (E_A(R)) for candidate implemented representations;
4. state-bank size and declared weights.

Do not compare raw bit magnitudes across carriers as effect sizes without accounting for different state banks and sampling laws.

## 4. Action cardinality is not demand magnitude

M2-R shows that equal-cardinality action sets can induce sharply different operational partitions.

Therefore:

[
|A_1|=|A_2|
]

does not imply comparable (D(A_1)) and (D(A_2)).

Action count is an index of contract breadth, not an equal-interval operational-demand scale.

Primary M2 summaries should therefore report the distribution of (D(A')) over action subsets of the same cardinality.

## 5. Panel-relative distinguishing basis

For a frozen state bank (X) and registered full action panel (A), define:

[
b(X,A)
=
min_{Ssubseteq A}
{|S|:O_S=O_A}.
]

This quantity is explicitly:

- state-bank relative;
- action-panel relative;
- observation-contract relative;
- horizon relative.

It is not a universal property of the carrier.

The object is closely related to mature characterization-set / state-identification / conformance-testing ideas.
OACR must not claim invention of minimal distinguishing test sets.

The empirical OACR question is instead:

> In a real implemented artifact under native mutating operations, how large and how stable is a panel-relative action basis, and how does it relate to the distinctions preserved by the implemented representation?

## 6. Current R3 developmental result

Post-hoc exact audit of the 64-action R3 panel:

- 51 actions are redundant for the full 101-class partition;
- 13 actions are individually indispensable under leave-one-out;
- those same 13 actions jointly reproduce all 101 classes.

Therefore:

[
b(X,A)=13
]

for this frozen finite panel.

This result is exploratory until prospectively replicated on fresh carriers.

## 7. Paper implication

The empirical M2 block should not be titled or framed as an “information growth law.”

A more defensible framing is:

> **Contract content determines which additional state distinctions become operationally necessary.**

Supporting measurements:

- conditional demand (D(A));
- subset-lattice variation at fixed breadth;
- marginal refinement events;
- panel-relative distinguishing basis;
- adequacy of candidate state representations relative to those distinctions.

The inherited monotonicity theorem remains background structure.
