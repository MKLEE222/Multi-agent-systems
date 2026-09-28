# OACR-R1 Protocol v1 — Relational Support / Retraction Congruence

**Date:** 2026-09-28  
**Status:** preregistered first cross-system relational experiment  
**Carrier:** graph derived from frozen Wikidata P279 assertions  
**Relation token:** `P279`  
**Registered L1 semantics:** transitive closure over the prepared finite graph; explicit-edge deletion as the registered write operator  
**Boundary:** this protocol does not claim to model the full native semantics or edit policy of Wikidata or RDFS

## 1. Purpose

OACR-W1 studies a learned routed-memory representation. OACR-R1 deliberately changes both the system form and the relation semantics.

The raw carrier data are frozen Wikidata P279 assertions. The experiment then registers a deliberately narrower graph semantics: reachability/transitive closure for READ and explicit-edge deletion for WRITE. This registered semantics is the experimental object; broader Wikidata, Wikibase, and RDFS semantics are not silently imported.

The experiment asks whether **complete current reachability/closure equivalence under this registered semantics** is sufficient for future retraction behavior.

This is a cross-system realization / positive-control experiment, not a claim that database provenance or truth maintenance is new.

## 2. Formal object

Let (G=(V,E)) be the asserted subclass graph and let

[
TC(G)
]

be its transitive closure.

The declared READ interface is the **entire finite closure**, not a sampled query panel:

[
F_{mathrm{READ}}(G)=TC(G).
]

Two graph states are read-equivalent iff

[
G_1equiv_{mathrm{READ}}G_2
iff
TC(G_1)=TC(G_2).
]

The native write family in v1 is explicit edge retraction:

[
Phi_{mathrm{del}(f)}(G)=Gsetminus{f}.
]

The primary question is whether closure equivalence is a congruence for retraction:

[
TC(G_1)=TC(G_2)
stackrel{?}{Longrightarrow}
TC(G_1-{f})=TC(G_2-{f}).
]

## 3. Exact witness construction

From a frozen real asserted graph (G), find a pair (u,v) such that:

1. (v) is reachable from (u);
2. ((u,v)
otin E);
3. there is a path of length at least two from (u) to (v).

Define the semantically redundant explicit assertion

[
e=(u,v)
]

and two states:

[
G_0=G,qquad
G_1=Gcup{e}.
]

Because (e) is already entailed,

[
TC(G_0)=TC(G_1)
]

exactly over the complete finite carrier.

Select an asserted edge (fin E) on a support path from (u) to (v) such that:

[
(u,v)
otin TC(G_0-{f}).
]

Apply the same future retraction (mathrm{del}(f)) to both states.

Then (G_1-{f}) retains the direct support (e), so:

[
(u,v)in TC(G_1-{f}),
]

while by construction:

[
(u,v)
otin TC(G_0-{f}).
]

Therefore the current entailment quotient is not a congruence for deletion.

The experiment searches for many such witnesses in a real Wikidata-derived graph; it does not fabricate the underlying subclass relations.

## 4. Why this experiment matters for OACR

The result is deliberately expected from mature truth-maintenance / incremental-view / provenance theory.

Its role is to show that the OACR abstraction can be instantiated in a system whose semantics are **exact, relational, and non-neural**.

The key distinction is:

[
	ext{current consequences}

eq
	ext{support structure required for future revision}.
]

A closure-only representation may be adequate for current entailment queries while being inadequate for retraction.

## 5. Refinement ladder

For each state pair and future deletion, evaluate:

### A0 — closure only

[
A_0(G)=TC(G).
]

By construction the two states collide at A0.

### A1 — closure + support multiplicity

For every entailed pair ((x,y)), record the capped number of distinct simple support paths up to the registered cap (K).

The pair is separated if the relevant entailment has different support multiplicity.

### A2 — closure + direct/asserted support relation

Record whether each entailed edge is explicitly asserted in (E) in addition to being derivable.

### A3 — closure + minimal support provenance

Record minimal edge-support sets for the affected entailments, up to the registered enumeration cap.

A3 is intended as a bridge toward provenance-semiring / truth-maintenance representations.

No claim of global minimality is permitted from this finite experiment.

## 6. Data acquisition and freezing

First-run domain:

- Wikidata root: **disease (Q12136)**
- relation: P279 only
- depth: up to three asserted subclass hops below the root
- maximum returned asserted edges: 1500

The workflow queries Wikidata Query Service over HTTPS with a fixed query string and explicit user agent.

Before witness search, the raw response is frozen and hashed:

- query text;
- retrieval timestamp;
- SHA256 of raw SPARQL JSON response;
- number of unique nodes and asserted edges.

If the endpoint fails or returns fewer than 50 unique asserted edges, the run fails. There is no silent fallback to another dataset.

## 7. Graph hygiene

Before analysis:

1. deduplicate edges;
2. remove self-loops;
3. retain the largest weakly connected component containing Q12136 when present;
4. detect directed cycles.

Because subclass cycles complicate partial-order interpretation, v1 handles them conservatively:

- if cycles are present, collapse strongly connected components before computing reachability;
- record every collapsed SCC and its size;
- do not interpret SCC-internal pairs as subclass witnesses.

## 8. Candidate selection

Enumerate candidate entailed-but-unasserted pairs ((u,v)) in deterministic lexical order.

For each candidate:

1. choose the lexicographically first shortest support path;
2. test each asserted edge (f) on that path in order;
3. accept the first (f) whose deletion breaks (uleadsto v) in (G_0);
4. construct (G_1=G_0cup{(u,v)});
5. verify exact current closure equality;
6. execute deletion of (f) in both states;
7. verify exact post-write closure divergence.

Freeze at most 64 witnesses.

## 9. Primary outcomes

Report:

- number of graph nodes / asserted edges;
- closure size;
- number of entailed-but-unasserted candidate pairs;
- number of exact A0 congruence violations found;
- distribution of post-deletion closure symmetric-difference sizes;
- which refinement level first separates each pair;
- number of witnesses still indistinguishable through A3.

The study is not a prevalence estimate of Wikidata editing behavior. Witness selection is purposive and theory-led.

## 10. Strong validity conditions

A witness is valid only if all hold exactly:

1. (TC(G_0)=TC(G_1));
2. (fin E(G_0)cap E(G_1));
3. the same deletion (f) is applied to both states;
4. ((u,v)
otin TC(G_0-{f}));
5. ((u,v)in TC(G_1-{f}));
6. full post-write closures differ;
7. adding (e=(u,v)) is the only pre-write graph difference.

## 11. Relation to prior theory

This experiment explicitly inherits:

- truth-maintenance systems: beliefs/consequences require recorded reasons for revision;
- incremental materialized-view maintenance: alternative derivation counts matter under insert/delete/update;
- provenance semirings: derivational provenance is richer than present query answers.

Those theories are not novelty threats to the experiment. They make the expected failure principled.

The OACR question is the cross-system one:

> which representation distinctions are sufficient for the observation and operation contract of this system, and how does that requirement compare with learned, causal, temporal, provenance, and compositional systems?

## 12. Boundary for v1

v1 covers only transitive relational entailment and deletion.

It does **not** yet model:

- Wikidata qualifiers;
- references/ranks;
- temporal validity;
- P31 instance propagation;
- inverse/subproperty semantics;
- contributor authority;
- actual Wikibase backend edit policy.

Those are explicit deepening stages rather than omissions to be silently ignored.


### Transport correction (2026-09-28)

The preregistered scientific query and graph semantics are unchanged. WDQS content negotiation returned XML under the initial TSV transport request, so the workflow was corrected before any analyzable carrier was produced to request SPARQL Results JSON explicitly. The raw response is still frozen and SHA256-hashed before graph construction.


## 13. Relation-semantics discipline

This protocol is governed by `docs/OACR_RELATION_SEMANTICS_DISCIPLINE_V1.md`. RDFS, truth-maintenance, view-maintenance, and provenance theories are comparators and sources of formal tools. They do not define the carrier's semantics. All v1 claims stay at the registered L1 graph semantics unless separately justified at L2.
