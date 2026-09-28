# OACR-R4 Protocol v2 — Complete Paginated Fresh Relational Redesign Replication

**Date:** 2026-09-28
**Status:** prospectively frozen before any complete-carrier augmented-state deletion outcome is inspected
**Supersedes for fresh-carrier execution:** R4 v1 retrieval layer only
**Preserves:** frozen roots, structural inclusion gates, state-bank rule, action-panel rule, contract-gated representation, replay requirements, and scientific outputs from R4 v1.

## 1. Reason for v2

R4 v1 froze five Wikidata P279 roots but every root returned exactly the registered 2,500-row limit.

The v1 protocol therefore excluded all five carriers before any augmented-state future-deletion outcome was executed.

R4 v2 repairs **retrieval completeness only**.

No root is replaced.

No partial-v1 carrier statistic is used to choose a root, state, action, or representation.

## 2. Frozen root list

Use the same five roots as R4 v1:

1. Q11173 — chemical compound;
2. Q618123 — geographical feature;
3. Q42889 — vehicle;
4. Q41176 — building;
5. Q43229 — organization.

## 3. Base query semantics

For each root, retrieve the same three-level P279 edge union as R4 v1:

- direct child to root;
- second-level child to direct child;
- third-level child to second-level parent.

The logical result is ordered by child then parent.

## 4. Deterministic pagination

Freeze:

- page size: 2,000 rows;
- maximum pages: 20;
- maximum registered rows before truncation: 40,000.

For page index j = 0,...,19, execute the same ordered query with:

LIMIT = 2000

OFFSET = 2000 * j

Stop only when a page returns **strictly fewer than 2,000 bindings**.

A carrier is retrieval-complete iff:

1. a short page occurs within 20 pages;
2. every page parses successfully;
3. the concatenated ordered child-parent sequence is nondecreasing;
4. after exact de-duplication, no page-boundary ordering inversion is observed.

If all 20 pages contain exactly 2,000 bindings, classify the carrier as PAGINATION_TRUNCATED and exclude it without replacement.

A retrieval/network failure after registered retries is an infrastructure failure, not a scientific exclusion.

## 5. Retrieval artifact

Preserve for every page:

- page index;
- OFFSET;
- binding count;
- raw response SHA256;
- first parsed edge when present;
- last parsed edge when present.

Also preserve:

- concatenated binding count;
- de-duplicated edge count;
- combined canonical edge-list SHA256;
- completion page index.

The raw page JSON responses must be uploaded in the workflow artifact.

## 6. Snapshot limitation

WDQS does not provide a repository snapshot transaction across paginated HTTP requests.

Therefore R4-v2 must explicitly report that the carrier is a deterministic ordered retrieval performed over one run, not a transactional Wikidata snapshot.

To detect gross pagination instability, the runner must fail if:

- page order regresses;
- an identical ordered page is repeated at two different offsets;
- de-duplicated edge count is implausibly smaller than concatenated parsed edge count due repeated pages.

No silent retry with different page size or ordering is permitted after scientific execution begins.

## 7. Graph hygiene

After complete retrieval:

1. remove self-loops and duplicate edges;
2. retain the component containing the root when present, otherwise largest weak component;
3. collapse nontrivial SCCs exactly as R1/R4-v1;
4. require a DAG after condensation.

Record:

- complete retrieved edge count;
- prepared nodes;
- prepared asserted edges;
- SCC count;
- closure size;
- entailed-but-unasserted redundant candidate count.

## 8. Outcome-blind structural inclusion gates

Preserve R4-v1 gates exactly.

A complete carrier enters primary analysis iff:

- prepared nodes >= 100;
- prepared asserted edges >= 128;
- redundant candidates >= 64;
- at least 64 asserted edges available for the shared action panel.

A carrier failing any gate is reported and not replaced.

Primary R4-v2 replication requires at least two included roots.

If fewer than two pass, R4-v2 is underpowered.

## 9. State-bank rule

Preserve R4-v1 exactly.

Let

C = TC(G) minus E(G).

If |C| <= 271, use all candidates.

If |C| > 271:

1. sort candidates lexically by endpoint identity;
2. choose exactly 271 candidates at evenly spaced indices.

Create base G plus one G+e state for every registered candidate.

Selection occurs before augmented-state future outcomes are executed.

## 10. Action-panel rule

Preserve R4-v1 / R3 exactly.

For every asserted base edge f compute from the base graph only:

J(f) = |TC(G) symmetric-difference TC(G-f)|.

Sort by:

1. base deletion impact J(f);
2. lexical edge identity.

Choose 64 unique actions at evenly spaced indices.

No augmented-state outcome participates in action selection.

## 11. Contract-gated representation

Preserve the frozen D1/D2 transform.

For redundant edge e=(u,v), define alpha_A(e)=1 iff at least one registered deletion makes u no longer reach v in the base graph.

Represent base G by the shared base marker.

Represent G+e by:

- shared base only when alpha_A(e)=0;
- shared base plus e when alpha_A(e)=1.

The active classifier is computed from base-graph post-deletion reachability before executing augmented-state outcomes.

## 12. Comparison representations and primary metrics

Compare:

- R0 — complete current closure;
- Rfull — complete asserted-edge identity;
- Rgate — shared base plus optional contract-active delta.

Report under uniform registered-state weights:

U = H(O_A | R)

E = H(R | O_A)

Also report conditional future demand:

D(A) = H(O_A | O_0).

Report exact pairwise under-/over-refinement.

## 13. Exact native replay

For every included root, every registered state, and every registered deletion:

1. execute from the original full state;
2. execute from the decoded Rgate state;
3. compare complete post-deletion transitive closure.

All registered cells must match exactly.

Any mismatch invalidates the root result.

## 14. Primary empirical outputs

Per included root:

1. state count;
2. full operational class count;
3. D(A);
4. R0 U/E;
5. Rfull U/E;
6. Rgate U/E;
7. active delta count;
8. inactive delta count;
9. active fraction;
10. physical delta-record reduction;
11. Rgate exact partition-match bit;
12. active-edge equivalence-group structure if E(Rgate)>0.

No minimum compression effect is required.

## 15. Frozen secondary action-content analysis

Preserve R4-v1:

- all 64 singleton action contracts;
- all C(64,2)=2016 action pairs;
- all 64 leave-one-action-out contracts;
- exact operational-partition hashes.

Panel-relative basis analysis remains secondary and explicitly related to mature characterization-set/testing ideas.

## 16. Confirmation logic

R4-v2 is fresh with respect to augmented-state future-deletion outcomes because:

- the five roots were frozen before R4-v1;
- R4-v1 excluded all roots before executing augmented-state outcomes;
- v2 changes retrieval completeness only;
- state/action/representation rules are unchanged.

R4-v2 can prospectively test:

- exact transfer of theorem-protected Rgate adequacy;
- whether Rgate exact partition matching recurs;
- carrier variation in active/inactive deltas;
- physical delta-record compression;
- action-content anisotropy.

## 17. Failure retention

Retain:

- pagination truncation;
- structural exclusion;
- fewer than two included roots;
- zero inactive deltas;
- nonzero Rgate excess;
- replay failure;
- near-uniform action contribution;
- highly concentrated action contribution.

No root may be replaced within R4-v2.
