# OACR Theory Gate T2/T4 Working Note

Date: 2026-09-30

Status: **THEOREM CANDIDATES — proof-audit required before manuscript promotion**

This note develops two load-bearing theoretical directions for the frozen OACR upgrade gate:

1. complexity of minimum exact contract-adequate representation repair;
2. the relation between bidirectional repair and non-anticipating construction.

The point is not to add theorem count. The target is to explain why exact representation repair is nontrivial in general, why R3/R4 can be tractable, and why verification-outcome access would make exact repair scientifically circular.

---

## 1. Finite contract-adequate feature repair

Let (X) be a finite registered state bank and let the frozen continuation contract (mathcal C) induce the operational quotient

[
O = O_{mathcal C}=X/{sim_{mathcal C}}.
]

Let

[
mathcal F={f_1,ldots,f_m}
]

be a finite family of admissible representation features, with each

[
f_i:X	o V_i.
]

For a subset (Ssubseteqmathcal F), define the induced representation

[
R_S(x)=(f(x))_{fin S}
]

and its induced partition (P_S).

### Definition 1 — O-safe feature

A feature (f) is **O-safe** when it is constant on every operational equivalence class:

[
xsim_{mathcal C} y
implies
f(x)=f(y).
]

Equivalently, the partition induced by (f) does not split any block of (O).

An O-safe feature can refine a representation toward the operational quotient without introducing over-refinement relative to that quotient.

### Definition 2 — Exact adequate feature set

A subset (Ssubseteqmathcal F) is **exactly adequate** when

[
P_S=O.
]

When every feature in (S) is O-safe, exact adequacy is equivalent to separation of every pair of distinct operational classes.

### Problem — Minimum Exact Adequacy Repair (MEAR)

**Input.**
- a finite operational quotient (O={C_1,ldots,C_n});
- a finite family (mathcal F) of O-safe binary features;
- an integer (k).

**Question.** Does there exist (Ssubseteqmathcal F) with (|S|le k) such that

[
P_S=O?
]

---

## 2. Candidate Theorem T2.1 — MEAR is NP-complete

### Statement

**The decision version of Minimum Exact Adequacy Repair is NP-complete, even when every admissible feature is binary and O-safe.**

### Proof sketch

**Membership in NP.**
Given (S), compute the feature vector of each operational class under the selected features. Because every selected feature is O-safe, no class can be split internally. Check in polynomial time that every pair of distinct operational classes receives a different selected-feature vector. This is equivalent to (P_S=O).

**NP-hardness.**
Reduce from **MINIMUM TEST SET**.

An instance of MINIMUM TEST SET consists of:
- a finite set of objects (U={u_1,ldots,u_n});
- a collection of binary tests (mathcal T={T_1,ldots,T_m}), where test (T_jsubseteq U);
- an integer (k);

and asks whether at most (k) tests can distinguish every pair of distinct objects: for every (u_p
e u_q), at least one selected test contains exactly one of them.

Construct an MEAR instance as follows.

For every object (u_i), create one operational class (C_i). It is sufficient to let each (C_i) contain one state, or arbitrarily many indistinguishable states.

For each test (T_j), create a binary feature

[
f_j(C_i)=
egin{cases}
1,&u_iin T_j,\
0,&u_i
otin T_j.
end{cases}
]

Extend (f_j) constantly to every state inside (C_i). Therefore every (f_j) is O-safe.

Now a subset (S) of features induces exactly the operational quotient iff every distinct pair (C_p,C_q) has different selected-feature vectors, which holds iff the corresponding tests distinguish every pair (u_p,u_q).

Thus there exists an exact adequate feature set of size at most (k) iff the original MINIMUM TEST SET instance has a solution of size at most (k).

MINIMUM TEST SET is NP-complete (Garey and Johnson, problem SP6). Therefore MEAR is NP-hard, and together with membership in NP, NP-complete. (square)

### Consequence

Exact finite-bank repair is not generally reduced to “retain every feature that ever matters.” Even after excluding features that would over-refine the target, choosing a minimum exact adequate representation can remain combinatorially hard.

This provides the general hardness baseline against which R3/R4 should be understood.

---

## 3. Weighted extension

### Corollary candidate T2.2

If every admissible feature has a positive integer cost (w_i), the minimum-cost exact adequacy problem is NP-hard.

The unweighted problem is the special case (w_i=1).

A stronger approximation analysis may follow from the relation to minimum test set / set cover, but no approximation claim is authorized yet.

---

## 4. Structural tractability target for R3/R4

The R3/R4 graph family does not solve arbitrary MEAR.

Its admissible distinctions have special structure:

- all states share one base graph (G);
- each non-base state differs by one currently redundant edge (e=(u,v));
- the action contract is a common singleton-deletion family (Asubseteq E(G));
- a candidate edge is active exactly when
  [
  alpha_A(e)=
  mathbf 1[
  exists fin A:(u,v)
otin TC(G-f)
  ].
  ]

Proposition 2 in the manuscript already proves the **individual safety/necessity** test:
- (alpha_A(e)=0) implies the delta is inert under every registered deletion;
- (alpha_A(e)=1) implies at least one registered deletion separates the augmented state from the base state.

The missing Theory-Gate result is stronger.

### Target theorem T3

Identify sufficient structural conditions on a one-delta-per-state carrier under which:

1. every inactive delta may be removed without changing (O_{mathcal C});
2. every active delta is required to separate its state from the coarse endpoint;
3. the active deltas do not induce accidental over-refinement among states that remain operationally equivalent;
4. consequently, the local activity gate realizes the exact operational quotient in polynomial time.

R3/R4 may then instantiate this tractable class rather than serve as the theorem statement themselves.

The key unresolved point is item 3. Current R3/R4 exactness establishes it empirically; a general condition must be formulated without inspecting the held-out operational outcome matrix.

---

## 5. Partition-lattice view of bidirectional repair

Use the manuscript order

[
Ppreceq Q
]

to mean that (P) is coarser than or equal to (Q).

Suppose

[
P_{m coarse}preceq Opreceq P_{m fine}.
]

If the operational quotient (O) itself is available to the repair constructor, exact bidirectional correction is algebraically immediate.

Let (ee) denote common refinement (join under this order) and (wedge) common coarsening (meet).

Then

[
P_{m coarse}ee O = O
]

and

[
P_{m fine}wedge O = O.
]

This motivates a crucial distinction.

### Proposition candidate T4.1 — Oracle triviality of quotient-visible repair

If a repair constructor may directly inspect the complete target operational partition (O), then for every pair

[
P_{m coarse}preceq Opreceq P_{m fine}
]

there exist trivial exact partition repairs from both endpoints, namely join with (O) from below and meet with (O) from above.

### Interpretation

The proposition is mathematically elementary, but methodologically important:

> exact repair success alone is not evidence of a predictive representation principle if the target quotient was visible during construction.

This is the formal motivation for the OACR information-authority boundary.

---

## 6. Non-anticipating realizability

Let

[
Y_{mathcal C}^{m verify}
]

denote the verification-only native outcome matrix whose equality classes induce (O_{mathcal C}).

Let

[
mathcal I_{m construct}
]

contain only information declared available before those outcomes are revealed.

### Definition 3 — Non-anticipating constructor

A repair constructor is non-anticipating when

[
kappa
=
g(mathcal C,mathcal I_{m construct})
]

and (g) is forbidden from reading (Y_{mathcal C}^{m verify}) or any object computed from it that exposes the target partition.

The resulting representation

[
R'=\Phi(R,kappa)
]

is accepted only after verification-only native replay.

### Definition 4 — Non-anticipating exact realizability

A target quotient (O_{mathcal C}) is non-anticipatingly realizable in an admissible repair family when there exists an allowed constructor (g) satisfying the declared information boundary such that native replay of the resulting (R') yields

[
P_{R'}=O_{mathcal C}.
]

This is a stronger scientific condition than mere existence of some representation whose partition equals (O_{mathcal C}).

---

## 7. Candidate separation theorem for the OACR methodology

### Theorem target T4.2 — Oracle repair versus predictive repair

The intended theorem should separate two statements:

1. **oracle realizability:** exact bidirectional partition repair is trivial when (O_{mathcal C}) is directly visible;
2. **non-anticipating realizability:** producing the same exact quotient from a restricted information boundary is a substantive prediction problem and can inherit the complexity of MEAR or become tractable only under additional carrier structure.

The first statement is already immediate from lattice identities.

The second needs a precise computational model of the information boundary before theorem promotion.

R4 is a candidate positive instance:
- constructor-visible: base graph, deletion alphabet, candidate delta endpoint;
- forbidden: augmented-state post-deletion outcome matrix and target operational partition;
- verification: all 17,408 native outcomes.

This makes R4 scientifically stronger than an oracle repair that simply reads the quotient and encodes it.

---

## 8. Relation to AIR / CEGAR

Abstract Interpretation Repair (Bruni, Giacobazzi, Gori, Ranzato, PLDI 2022, DOI 10.1145/3519939.3523453) studies local completeness of abstract domains and proves necessary and sufficient conditions for an optimal locally complete refinement (the pointed shell), with forward and backward repair strategies.

OACR must not claim novelty for the general idea that an abstraction can be repaired relative to required semantics.

The candidate independent theoretical object is instead:

> finite persistent representations whose target partition is induced by a registered family of future native transformations, where both under- and over-refinement count as errors and where the target native outcome partition is withheld from the repair constructor.

The main theoretical contrast to pursue is therefore not “AIR refines, OACR repairs.” It is:

- AIR: optimal refinement of an abstract domain to restore local completeness of an abstract computation;
- OACR: exact or minimum-cost realization of a future-operation-induced quotient by an admissible persistent representation under an explicit information-authority boundary, permitting correction from either coarse or unnecessarily fine endpoints.

This distinction must survive a hostile AIR-aware review before Theory Gate T passes.

---

## 9. Immediate proof-audit tasks

1. Check the exact formulation and citation of MINIMUM TEST SET and whether a cleaner modern reduction/reference is preferable.
2. Verify partition-lattice join/meet notation against the manuscript's reversed refinement order.
3. Formalize a non-oracle input model: if (O_{mathcal C}) is part of the computational input, hardness and anti-circularity address different questions and must not be conflated.
4. Search for existing “minimum reduct / discernibility / test set” results in rough sets, feature selection, state minimization, and automata so MEAR is not renamed prior work.
5. Derive or refute a structural condition that upgrades R3/R4's empirical exactness to a carrier-class theorem.
6. Only after 1–5 pass should T2.1/T4.1 be promoted into the manuscript.

## References for this working note

- Bruni, R.; Giacobazzi, R.; Gori, R.; Ranzato, F. “Abstract Interpretation Repair.” PLDI 2022. DOI: 10.1145/3519939.3523453.
- Garey, M. R.; Johnson, D. S. *Computers and Intractability*. MINIMUM TEST SET, SP6.

