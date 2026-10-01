# Multi-addition conditional-cut compiler

Date: 2026-10-01. Status: mathematically derived and synthetically checked T3
candidate; same-assistant work, independent review outstanding. T2/T5 remain open.

## Change in the structural boundary

The old componentwise rule tests each addition against the base graph alone. It
over-refines interacting additions. Test an addition instead against the base
graph plus every other persistent addition. In the acyclic, full-reachability,
base-edge-failure setting this produces the unique least retained subset of the
available additions, an exact behavior partition, and a source-free residual
updater. This extension directly uses classical DAG transitive reduction and
restricted mincuts; it is not asserted as a new graph algorithm.

## Inputs and candidate statement

Fix G, A contained in G and h<=|A|. A concrete state has addition set B disjoint
from G, with G union B acyclic. For the executed bank, B ranges over all subsets
of D=TC(G) minus G. The derivation also allows initially nonredundant additions as
long as the augmented graph is acyclic. Only base edges in A can fail. Additions
persist. The contract observes full TC after every F contained in A with |F|<=h,
including F empty. Ordered histories consume budget and do not reset it.

For e=(u,v) in B, define lambda_A(G union (B minus {e}),e) as the minimum number
of edges from A whose deletion destroys all u-to-v paths. Other edges have
infinite capacity; a disconnected pair has cut zero. Set

    R_C(B) = { e in B : lambda_A(G union (B minus {e}),e) <= h }.

The initial constructor reads the available B witness. It reads no realized
future observation matrix. Later updates read only the stored subset, residual
shared graph, remaining action bank and budget.

## Proof by classical transitive reduction

For each failure set F, let H_F=(G minus F) union B and let TR(H_F) be its unique
DAG transitive reduction. An addition e belongs to TR(H_F) exactly when its
endpoints have no alternative path in H_F minus e. Therefore

    R_C(B) = union over legal F of (TR(H_F) minus (G minus F)).

The cut condition is exactly existential membership in this union: every
alternative path must be cut using at most h allowed base edges.

Necessity: if a stored subset C of B omits an edge from this union, it omits a
mandatory cover edge for some H_F. No other path in H_F connects its endpoints,
so the native decoded reachability differs at that F.

Sufficiency: (G minus F) union R_C(B) contains TR(H_F) and is contained in H_F,
so it has exactly H_F's reachability. This simultaneously justifies dropping all
excluded additions; individual redundancy tests without DAG uniqueness would
not suffice. Within subsets C of B, adequacy is equivalent to R_C(B) contained
in C. Hence R_C(B) is the unique least subset and minimizes any strictly positive
additive retained-edge cost. This is a restricted-family result, not minimum
bits among arbitrary encodings.

Partition exactness: equal R gives equal full continuation outputs by the native
decoder. Conversely, if two addition sets have equal TC(H_F) for every F, then
their unique transitive reductions at each F are equal because a DAG transitive
reduction is determined by its reachability relation. Subtracting the same
remaining base graph and taking the union gives equal R. Thus ker(R_C) equals
the full registered behavior kernel even across interacting addition sets.

Residual update: after prefix F, use G minus F, A minus F and h-|F|. Original B
and initially stored R_C(B) have equal behavior for every F union J with legal
remaining J. Exactness of the residual compiler implies

    R_(C/F)(B) = R_(C/F)(R_C(B)).

Every initially omitted edge has an alternative path after all original legal
failures, so none can become mandatory under the smaller residual continuation
bank. Hence the residual representation is a subset of R_C(B). One-step update
is compile_multi on the stored subset after deleting the named base edge. The
commuting square and native decoder correctness follow. There is no read of
discarded additions.

## Interaction witness resolved

On chain 0->1->2->3, only (1,2) may fail, h=1. The old rule independently retains
e1=(0,2) and e2=(0,3). But B={e1} and B={e1,e2} have the same full behavior.
The conditional compiler maps both to {e1}, since the persistent e1 followed by
(2,3) makes e2 unnecessary after either legal failure set. The old counterexample
remains valid against the old rule; its boundary is not erased.

## Execution and cost

Code: `experiments/oacr_theory/multi_delta_budget_audit_v1.py`.
Result: `docs/OACR_MULTI_DELTA_CONDITIONAL_CUT_RESULT_2026-10-01.json`.

Enumerated 2–4 node graphs respecting a fixed vertex order, all redundant-addition
subsets, all deletable base-edge banks, budgets, legal failures and alternative
stored subsets. Independent native path: bitset Warshall; constructor path:
inherited restricted maxflow.

| Check | Count | Result |
|---|---:|---|
| Graph/action/budget banks | 940 | Exact partition in every bank |
| Addition-state partition and idempotence checks | 2,368 each | Zero failures |
| Alternative stored-subset minimality checks | 4,404 | Adequate iff contains R |
| Native decode / residual no-resurrection checks | 9,708 each | Zero failures |
| Commuting updates at residual prefixes | 11,762 | Zero failures |

The encoder also rejects cyclic augmented inputs. Enumeration is proof debugging,
not a general proof or independent confirmation. The observations are correlated
synthetic checks. Coverage beyond four nodes and initially nonredundant banks is
not supplied by this executed report.

Let b=|B|, a=|A| and m=|G|. Compilation checks acyclicity and performs b restricted
cuts on graphs with at most m+b-1 edges. With the dense capped-flow reference,
O(n+m+b + b*(n+m+b+(a+1)n^2)) is a conservative time bound, excluding caching.
Each cut uses O(n^2+n+m+b) working space. Update recomputes at most |stored R|
cuts on the residual graph; no incremental optimality is asserted. Stored edge
records cost O(|R| log n) bits in a straightforward encoding, plus shared context,
source-witness acquisition and compiler cache. Native decode/replay cost is
separate. No future failure-set enumeration is needed by the constructor.

Reproduce:

```bash
python experiments/oacr_theory/multi_delta_budget_audit_v1.py --max-n 4 --out /tmp/oacr_multi_delta.json
```

## Scope and novelty obligations

Partial output, cycles, deletable additions, future insertions, expanded budgets,
and arbitrary action constraints require separate proofs. An expanded contract
can again require erased source data. In a cyclic graph, individually redundant
edges may all be removable one at a time while simultaneous removal destroys
reachability; the present compiler deliberately rejects that carrier.

Classical reduction and cut theory are load-bearing, not decorative citations.
The union identity above is our specialization. It fixes an implementation/theorem
scope gap without automatically satisfying T2/T5. Compare against fault-tolerant
reachability preservation and reduction algorithms under the same encoded graph,
failure model and retained-subset cost before promoting an independent result.

Primary background: Goranci et al., *Fully Dynamic Algorithms for Transitive
Reduction*, ICALP 2025, Section 2 and Theorem 2.1 (attributing classical DAG
uniqueness to Aho–Garey–Ullman 1972):
https://arxiv.org/html/2504.18161v1
