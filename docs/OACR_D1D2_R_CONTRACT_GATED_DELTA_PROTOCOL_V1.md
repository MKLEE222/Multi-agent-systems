# OACR-D1/D2-R Protocol v1 — Contract-Gated Delta Representation

**Date:** 2026-09-28  
**Status:** theorem-driven developmental constructive experiment after R3/M2 outcomes are known  
**Carrier:** frozen R3 relational state family  
**Role:** test whether OACR diagnosis can be turned into an actual contract-preserving representation compression/augmentation rather than remaining a partition audit.

## 1. Scope and epistemic status

This protocol is frozen **after** R3 and M2-R results were observed.

Therefore:

- it is not a prospective confirmation of the R3 operational quotient;
- any exact partition match on R3 is developmental evidence;
- the structural adequacy proposition below is proved independently of the observed R3 class structure;
- fresh carriers are required before promoting empirical compression magnitude or exact-match behavior to a general claim.

## 2. Frozen carrier family

Reuse the exact R3 construction.

Let (G=(V,E)) be the frozen prepared DAG.

Let

[
C=TC(G)setminus E
]

be the set of entailed-but-unasserted redundant edges.

Registered states are

[
X={G}cup{G+e:ein C}.
]

On the frozen carrier:

- (|X|=272);
- (|C|=271);
- every state has the same complete current transitive closure.

Reuse the exact frozen R3 64-action deletion panel

[
A={operatorname{del}(f):fin Fsubseteq E}.
]

The registered operational observation for action (f) is the complete post-deletion transitive closure.

## 3. Contract-active redundant edge

For a candidate redundant edge

[
e=(u,v)in C,
]

define it to be **contract-active** iff

[
exists fin F:
v
otin operatorname{Reach}_{G-f}(u).
]

Equivalently, at least one registered deletion makes the relation (uleadsto v) cease to be supported by the base graph.

Define

[
alpha_A(e)=
mathbf 1left[
exists fin F:
v
otin operatorname{Reach}_{G-f}(u)
ight].
]

This criterion is computed from:

- the base graph (G);
- the declared action panel (F);
- the endpoints of the currently stored redundant edge.

It does **not** execute the post-deletion outcome of the evaluated augmented state (G+e).

## 4. Contract-gated delta representation

Represent every state as a shared base graph identifier plus an optional retained delta:

[
phi_A(G)=ot,
]

[
phi_A(G+e)=
egin{cases}
ot,&alpha_A(e)=0,\
e,&alpha_A(e)=1.
end{cases}
]

Operationally:

- (ot) means “use shared base graph (G)”;
- retained (e) means “reconstruct (G+e)” before applying a registered deletion.

Thus inactive redundant-edge identities are physically omitted from the per-state delta representation.

## 5. Structural adequacy proposition

### Proposition

For every registered state (Sin X) and every registered deletion (fin F), the representation (phi_A(S)) is sufficient to reproduce the complete registered post-deletion transitive closure.

### Proof obligation

For (S=G), trivial.

For (S=G+e):

#### Case 1 — (alpha_A(e)=1)

The representation retains (e), so the original state (G+e) is reconstructed exactly before deletion.

#### Case 2 — (alpha_A(e)=0)

For every registered (f),

[
uleadsto vquad	ext{in }G-f.
]

Therefore (e=(u,v)) is still transitively redundant in (G-f).

Adding (e) to (G-f) cannot create any new reachability relation, so

[
TC((G+e)-f)=TC(G-f).
]

Hence replacing (G+e) by the shared base representation produces exactly the same registered outcome.

Therefore (phi_A) is contract-adequate on the entire registered state family:

[
U_A(phi_A)=0.
]

This proposition does not assert that (phi_A) is always partition-minimal. Active edges may still over-refine if two distinct active edges induce identical registered behavior.

## 6. Bidirectional redesign interpretation

### From closure-only under-refinement

The current-closure-only representation is augmented by one optional contract-active delta edge:

[
R_0
longrightarrow
R_0+phi_A.
]

The registered test is whether omission drops from the frozen R3 value to zero.

### From full asserted identity over-refinement

The full state representation is compressed by quotienting away all redundant-edge identities with (alpha_A(e)=0):

[
R_{m full}
longrightarrow
phi_A.
]

Adequacy is theorem-protected.
The empirical question is how much excess (E) remains.

## 7. Physical representation measurement

Because all states share the same base (G), measure per-state delta storage separately from shared-base storage.

Report:

- number of augmented states: 271;
- number of retained contract-active delta edges;
- number of omitted contract-inactive delta edges;
- mean delta-edge records per state before compression;
- mean delta-edge records per state after compression;
- percentage reduction in per-state delta-edge records.

This is a concrete physical record-count measure for this delta encoding.

Do not translate it into byte savings unless an explicit serialization format is frozen and measured.

## 8. Registered outputs

The experiment must report:

1. active/inactive classification for every redundant edge;
2. action(s) making each active edge necessary;
3. exact representation partition induced by (phi_A);
4. (U,E) against the frozen full operational partition;
5. pairwise under-/over-refinement counts;
6. physical delta-edge record reduction;
7. complete action-by-edge reachability matrix used to compute (alpha_A);
8. endpoint regression against frozen R3 operational outcomes;
9. independent replay verifier from the compressed representation.

## 9. Independent replay requirement

For every state and every registered action:

1. decode (phi_A(S)) into either (G) or (G+e);
2. execute the registered deletion;
3. compute the complete transitive closure;
4. compare with the frozen R3 native outcome signature.

All

[
272	imes64=17,408
]

state-action outcomes must match exactly.

A summary-level partition match is insufficient.

## 10. Acceptance gates

### Gate A — theorem implementation
The active-edge classifier must use only base-graph post-deletion reachability of the redundant edge endpoints.

### Gate B — no under-refinement
Require

[
U_A(phi_A)=0.
]

Failure invalidates either the proof implementation or assumptions.

### Gate C — exact native replay
Require 17,408/17,408 compressed-representation replays to match frozen R3 outcomes.

### Gate D — empirical excess
Report (E_A(phi_A)) without requiring it to be zero.

If (E=0), classify the result as a developmental exact match on this carrier, not a general minimality theorem.

### Gate E — physical compression
Report actual retained/omitted delta record counts.

## 11. Boundaries

This experiment does not establish:

- a universal graph representation;
- a universal minimal provenance structure;
- that edge identity is optimal for active states;
- physical memory optimality;
- natural prevalence in Wikidata;
- prospective generalization.

It does establish, if all gates pass, that OACR diagnosis can be converted into a concrete contract-specific representation transform whose adequacy is structurally justified and whose native outcomes are exactly replayed.

## 12. Fresh-carrier continuation

On a fresh relational carrier, freeze the same transform before inspecting augmented-state outcomes.

The confirmatory questions are:

1. does theorem-protected (U=0) replay exactly?
2. how much (E) remains among active edges?
3. how much physical delta compression is obtained?
4. does the transform remain useful when the state family contains multiple simultaneous redundant deltas rather than exactly one?
