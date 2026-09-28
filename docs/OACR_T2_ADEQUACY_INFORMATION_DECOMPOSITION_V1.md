# OACR T2 — Contract-Relative Adequacy Gap and Information Decomposition v1

**Date:** 2026-09-28  
**Status:** formal upgrade after the R2/G3/G4 red-team  
**Role:** recover strong quantitative claims without rebranding mature behavioral-equivalence theory as novel

## 1. Why the formal object changes

The red-team showed that witness counts are too sensitive to candidate construction and action choice.

The next OACR object therefore compares **two partitions on the same frozen state distribution and the same operation contract**:

1. the partition induced by a representation;
2. the partition induced by future registered operational behavior.

This makes under-refinement and over-refinement jointly measurable.

## 2. Finite exact setting

Let:

- (X) be a finite registered state bank;
- (mu) be a declared distribution over (X) (uniform by default unless another sampling law is justified);
- (mathcal C_H) be a frozen observation/action contract through horizon (H);
- (O_H(X)) be the operational-equivalence class induced by exact registered behavior (B_H);
- (R(X)) be the equivalence class induced by a candidate representation or abstraction.

Both (O_H) and (R) are random variables under (Xsimmu).

## 3. Dual adequacy gap

Define the **operational omission gap**

[
U_H(R)=H(O_Hmid R),
]

and the **representational excess gap**

[
E_H(R)=H(Rmid O_H).
]

Interpretation:

- (U_H>0): the representation merges states whose registered operational classes differ;
- (E_H>0): the representation distinguishes states that belong to the same registered operational class.

The symmetric sum

[
V_H(R)=U_H(R)+E_H(R)
]

is exactly the variation of information between the two induced partitions. Variation of information itself is mature and is not an OACR invention.

OACR's use of the two directional terms is operational:

- (U_H) measures missing contract-relevant class information;
- (E_H) measures extra class information retained beyond the contract.

## 4. Exact adequacy and exact minimality

### Proposition 1 — adequacy

On the support of (mu),

[
U_H(R)=0
]

iff (O_H) is a deterministic function of (R).

Equivalently, every representation class lies inside one operational class.

Thus (U_H=0) is the exact finite-distribution form of contract adequacy.

### Proposition 2 — partition match

[
U_H(R)=E_H(R)=0
]

iff the representation and operational partitions coincide almost surely up to relabeling of classes.

This is a partition-level minimality condition, not a physical-storage minimality theorem.

## 5. Contract-expansion monotonicity

Suppose contract (mathcal C') is stronger than (mathcal C) in the precise sense that its operational partition refines the old one:

[
O_{mathcal C}=f(O_{mathcal C'})
]

for some deterministic map (f).

This occurs, for example, when:

- horizon increases while the observation/action semantics are unchanged;
- the registered action family expands;
- the registered observation family expands.

Then for any fixed representation (R):

[
H(O_{mathcal C}mid R)
le
H(O_{mathcal C'}mid R),
]

so the omission gap cannot decrease.

Also:

[
H(Rmid O_{mathcal C'})
le
H(Rmid O_{mathcal C}),
]

so the excess gap cannot increase.

Therefore:

[
oxed{
	ext{stronger contract}
Rightarrow
U	ext{ nondecreasing},quad
E	ext{ nonincreasing}
}
]

for any fixed representation partition.

This is a direct consequence of standard conditional-entropy monotonicity under deterministic refinement. The information-theoretic theorem is inherited; the OACR contribution target is to make it measurable and useful for real computational representations.

The total variation-of-information gap (U+E) need not be monotone.

## 6. Coding interpretation — narrow and explicit

For i.i.d. draws from (mu), (H(O_Hmid R)) has the standard conditional source-coding interpretation: it is the asymptotic expected number of additional bits per sample needed to specify the operational class when the representation class is already known.

Similarly, (H(Rmid O_H)) measures class-label variability retained by the representation after the operational class is known.

These are **class-information quantities**, not claims about the physical number of bits in model parameters, graph files, or commit objects.

Therefore OACR must stop using (log_2 N_H) as a general “information law.” It remains only a cardinality/worst-case distinguishability quantity.

## 7. Stochastic extension

For stochastic systems, replace the exact class variable by the registered future-outcome law.

A representation (R) is contract-sufficient when the future registered outcome (Y_{mathcal C}) is conditionally independent of the full state (X) given (R):

[
Y_{mathcal C}perp Xmid R.
]

This is standard statistical sufficiency / Blackwell-style territory and is not claimed as a new theorem.

OACR's open problem is how to operationalize this criterion for persistent computational artifacts whose native writes change the artifact itself.

## 8. Strong claims this formalization can recover if empirically supported

### S1 — directional adequacy gap
Real implemented representations can be quantitatively too coarse and too fine relative to the same native-operation contract.

Required evidence:
- same state bank;
- same action family;
- both required and non-required pairs;
- nonzero (U) and/or (E) measured without construction leakage.

### S2 — contract expansion law
For a fixed implemented representation, empirical (U) should rise and (E) should fall as the registered operation contract becomes stronger, consistent with the theorem.

Required evidence:
- at least two materially different carriers;
- nested action/horizon contracts;
- fixed representation features.

### S3 — operationally matched redesign
A representation can be changed so that (U) decreases without gratuitously increasing (E), or (E) decreases while keeping (U=0).

This is the constructive design target.

## 9. Immediate experimental consequences

### Relational
Replace pair-specific deletion with one globally frozen deletion alphabet across all closure-equivalent states.

Compare:
- closure-only representation;
- full asserted-edge identity;
- intermediate candidate abstractions.

Measure (U,E) under the same contract.

### Git
Replace pair-specific targets with a global merge-action panel shared by all same-tree natural state pairs.

Use one panel for discovery/stress testing and a separately frozen held-out panel for validation.

### Learned
For GRACE, derive an exact categorical operational signature in parallel with continuous/logit diagnostics so that partition-level (U,E) can be computed without pretending tolerance matching is automatically transitive.

## 10. Novelty boundary

The following are **not** new:
- variation of information;
- conditional entropy;
- statistical sufficiency;
- behavioral quotients;
- monotonic refinement under larger test families.

The candidate OACR contribution is the combination of:

1. a contract-relative audit of **implemented computational representations**;
2. directional omission/excess diagnosis against **native mutating operations**;
3. the same measurement object across heterogeneous carriers without flattening their semantics;
4. prospective representation redesign using the diagnosed gap.

That contribution must be earned empirically.
