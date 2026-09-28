# OACR Red-Team Retrospective v1

**Date:** 2026-09-28  
**Purpose:** re-evaluate current evidence after R2/G3/G4 before promoting any result into a paper-level claim.

## 1. Executive correction

The current results are useful, but several clean-looking numbers are partly or largely induced by the registered construction.

Therefore the project must distinguish:

1. **natural occurrence evidence** — a relevant state configuration occurs in an unmodified real system;
2. **operational execution evidence** — the native system actually realizes the registered consequence;
3. **construction-implied consequence** — the result follows almost directly from how the candidate/action was defined;
4. **discriminative evidence** — a candidate representation feature distinguishes required from non-required pairs under the *same* contract;
5. **design evidence** — changing the representation improves adequacy.

Only (4) and (5), plus a genuinely surviving formal extension, can carry the strongest OACR claims.

---

## 2. G3 — important, but 29/29 must be demoted

### What is genuinely natural

The public `git/git` history contains 29 naturally occurring two-parent merge commits in the frozen first-10,000-merge window such that:

- (B) is a merge commit with first parent (A) and second parent (T);
- (operatorname{tree}(A)=operatorname{tree}(B));
- (T
otpreceq A);
- (Tpreceq B).

The existence of these 29 tree-preserving history changes is genuine natural-history evidence.

### What is largely implied by the registered action

G3 then executes the pair-specific action `git merge T` from both states.

By candidate definition:

- from (B), (T) is already an ancestor, so Git should take the already-up-to-date path;
- from (A), (T) is explicitly not an ancestor, so Git cannot take that same already-up-to-date path.

Because `already_up_to_date` is part of the registered outcome signature, an outcome difference is close to structurally guaranteed.

Therefore:

[
29/29
]

is best interpreted as:

> all 29 naturally occurring structural candidates were confirmed by the native Git executable and no implementation/pathological exception invalidated the witness construction.

It is **not** strong evidence that an independently chosen future-operation contract frequently distinguishes same-content histories.

### Revised role

G3 is:
- strong natural-occurrence evidence for the *state configuration*;
- exact execution validation;
- a naturalized positive control.

It is **not yet** a discriminative representation benchmark.

---

## 3. G4 — more discriminative, but still narrow

G4 samples 32 natural same-tree commit pairs and evaluates a shared four-target merge alphabet.

Result:

- 32/32 behaviorally equivalent under that finite contract;
- full commit/history identity separates all 32 — therefore over-refines this finite contract;
- target-ancestry vector separates 0/32;
- merge-base vector separates 24/32.

### What this genuinely shows

Under one independently frozen four-target action family, internal history distinctions can be irrelevant to future registered behavior.

This is a valid finite-contract over-refinement demonstration.

### Limitations

1. The 32 pairs are the deterministic first 32 of 198 available pairs, not the complete bank.
2. The four targets were selected from the first four G2 structural candidates; they may provide weak coverage of the histories in the control bank.
3. Because there are zero required separations in this G4 bank, feature **under-refinement cannot be assessed**.
4. G3 positives and G4 controls cannot be combined into one confusion matrix because their action contracts differ.

### Revised role

G4 is the strongest current natural evidence for over-refinement, but it requires:
- all 198 pairs or a stronger preregistered sampling scheme;
- a richer shared action alphabet;
- positives and negatives under the *same* contract.

---

## 4. R2 — exact, but candidate features are nearly construction-identifying

R2 constructs:

[
G_0=G,qquad G_1=Gcup{e}
]

for every entailed-but-unasserted edge (e).

The candidate refinements are:

- A1 support multiplicity;
- A2 explicit assertion;
- A3 shortest-support provenance.

### Structural issue

For every constructed pair:

- A2 differs **by definition**, because (e) is absent in (G_0) and present in (G_1);
- A1 normally differs by construction because adding the direct support creates an additional path;
- A3 normally differs by construction because the direct edge changes the minimal/shortest support structure.

Therefore the fact that A1/A2/A3 separate all 271 state pairs is not an empirical discovery.

The useful observation is instead that the frozen future-deletion rule produces:

- 267 required separations;
- 4 non-required pairs.

Thus the construction-identifying features over-refine those four controls.

### Revised role

R2 is:
- an exact theorem-friendly sanity carrier;
- a demonstration that “store every support difference” can be too fine for a particular future-action contract.

It is **not** evidence that A1/A2/A3 are empirically strong predictors of necessity.

A stronger relational experiment needs naturally or independently generated closure-equivalent state pairs, or candidate features that are not guaranteed to encode the construction label.

---

## 5. M1 — tooling, not scientific evidence

The exact partition utilities passing a self-test establish implementation correctness only.

They contribute no empirical support to OACR claims.

Also:

[
log_2 N_H
]

must be described carefully.

For (N_H) required equivalence classes, it is a **worst-case fixed-length distinguishability/cardinality bound** (up to ceiling), not a general Shannon information measure.

Expected coding cost would require a distribution over operational equivalence classes.

Therefore avoid calling (log_2 N_H) a general “information law” until a probabilistic formulation is registered.

---

## 6. L1 — important but currently a diagnostic-scale learned experiment

The running GRACE H=2 design has at most:

- 5 seeds;
- 4 states/seed;
- 6 state pairs/seed;
- 3 actions;
- 12 action trajectories/state through H=2.

Maximum pair bank is only 30 pairs before filtering for H0 collisions.

Therefore L1 should be treated as:

> a prospective horizon diagnostic on a serious learned carrier,

not yet the final learned-system empirical scale.

If L1 yields a clean H1-to-H2 separation, it motivates a larger L1b.
If L1 is negative, preserve it and move to a second learned write ecology rather than tuning the bank until positive.

---

## 7. Theory — current novelty risk remains high

T1 already shows that the following are mature:

- future/continuation-induced equivalence;
- behavior-preserving quotients;
- minimal predictive states;
- input–output predictive states;
- minimal strong-preserving refinements;
- representation independence under mutable interfaces;
- query/transform/cost tradeoffs.

Therefore the statement

> “static equality is insufficient; future operations determine necessary distinctions”

is **not** an OACR novelty claim.

The formal core survives only if OACR can establish something materially stronger around:

- auditing **implemented computational representations** rather than defining an abstract behavioral state;
- native **artifact-mutating** operations and persistent representation change;
- measurable under-/over-refinement of real representations;
- contract expansion and representation burden;
- constructive augmentation/compression.

The first two items alone may still be a synthesis rather than a theorem-level extension.

---

## 8. Current evidence roles after demotion

### W1
Useful negative learned pilot:
internal routing distinction did not produce registered one-step necessity.

### R2
Exact constructed sanity carrier:
operational necessity and over-refinement can coexist, but feature separation is construction-coupled.

### G1
Exact native positive control:
same tree can have different merge behavior.

### G3
Natural occurrence of the G1 structural pattern:
29 natural cases; operational divergence is largely entailed by pair-specific action choice.

### G4
Natural finite-contract over-refinement control:
32 behaviorally equivalent pairs despite history differences; strongest current non-constructed negative evidence.

### L1
Prospective learned horizon experiment:
still running; current scale is diagnostic, not final.

---

## 9. Revised next gates

### Gate A — same-contract discrimination

Before claiming that OACR identifies useful representation refinements, create at least one carrier where the **same frozen action family** contains:

- current-read collision pairs that require separation;
- current-read collision pairs that do not;
- candidate features that make nontrivial TP/FP/FN/TN predictions.

This is currently missing.

### Gate B — natural relational states

Replace or complement the synthetic (G) versus (G+e) construction with naturally generated or historical relational states that have the same registered current consequences but different support structures.

### Gate C — stronger Git contract

Expand G4 beyond the first 32 pairs and four targets. Prefer a globally frozen action set selected by structural coverage without using pair outcomes.

### Gate D — learned scale

Treat L1 as a mechanism/horizon probe. A paper-level learned block requires a larger bank and at least one materially different write ecology.

### Gate E — constructive result

Do not promote OACR to a representation-design theory until augmentation or compression is actually demonstrated prospectively.

---

## 10. Current paper-level statement that remains safe

At present the strongest defensible summary is:

> Existing computational representations can preserve distinctions that are irrelevant to a finite native-operation contract, while current observable equality can also hide distinctions that become relevant under future operations. OACR is being developed as a theory-grounded audit framework for measuring this mismatch across heterogeneous implemented representations.

Even this is currently supported unevenly across carriers.

The project is **not yet** entitled to claim:
- a new behavioral quotient theory;
- a general information law;
- a general cross-system hierarchy;
- a validated representation-design principle.

Those remain targets.
