# OACR-R4 v1 Underpowered Replication Record — 2026-09-28

## Status

R4 v1 is **underpowered with zero included carriers**.

This is a valid protocol outcome, not a negative result about the contract-gated representation.

## Frozen protocol

- file: `docs/OACR_R4_FRESH_RELATIONAL_REDESIGN_PROTOCOL_V1.md`
- commit: `8af77e7fa2d31f0b1b8ee2b5bcebded98b56a237`

The protocol froze five Wikidata P279 roots and required exclusion whenever the retrieval returned exactly the 2,500-row hard limit.

## Runs

### Engineering-failed first trigger

Run `36433760547` failed before any carrier retrieval or native-operation outcome because of a stale Python import path.

No scientific result was produced.

The import was repaired without changing:

- roots;
- retrieval query;
- row limit;
- structural gates;
- state-bank rule;
- action-panel rule;
- representation transform.

### Clean rerun

Run `36434133658` completed successfully for all five frozen roots.

Every result and structural-exclusion artifact passed its independent verifier.

## Frozen-root outcomes

### Q11173 — chemical compound

- binding count: 2,500;
- row limit: 2,500;
- truncated: true;
- prepared nodes from partial response: 2,037;
- prepared asserted edges from partial response: 2,036;
- redundant candidates from partial response: 19.

Exclusion reasons:

- query_truncated;
- redundant_candidates_lt_64.

### Q618123 — geographical feature

- binding count: 2,500;
- truncated: true;
- prepared nodes from partial response: 1,457;
- prepared asserted edges: 1,510;
- redundant candidates: 446.

Exclusion reason:

- query_truncated.

### Q42889 — vehicle

- binding count: 2,500;
- truncated: true;
- prepared nodes from partial response: 34;
- prepared asserted edges: 33;
- redundant candidates: 4.

Exclusion reasons:

- query_truncated;
- prepared_nodes_lt_100;
- prepared_edges_lt_128;
- redundant_candidates_lt_64;
- asserted_edges_lt_64.

The very small connected component cannot be interpreted independently of truncation because lexical truncation may omit ancestor-linking rows.

### Q41176 — building

- binding count: 2,500;
- truncated: true;
- prepared nodes from partial response: 1,965;
- prepared asserted edges: 2,056;
- redundant candidates: 532.

Exclusion reason:

- query_truncated.

### Q43229 — organization

- binding count: 2,500;
- truncated: true;
- prepared nodes from partial response: 1,369;
- prepared asserted edges: 1,425;
- redundant candidates: 242.

Exclusion reason:

- query_truncated.

## Scientific interpretation

Because all five roots hit the preregistered truncation gate:

[
N_{m included}=0.
]

Therefore R4 v1 provides **no confirmatory native-operation evidence** for or against the contract-gated redesign.

The partial graph statistics are diagnostic only and may not be used as if they were complete carriers.

In particular, the apparent low redundancy of Q11173 or small connected component of Q42889 cannot be treated as scientific carrier properties because the raw responses were incomplete.

## Next allowed step

A new retrieval protocol may be frozen because the failure mode is now known to be transport/completeness rather than native-outcome failure.

The new protocol must:

1. keep the same five roots rather than selecting replacements using partial outcomes;
2. retrieve the complete ordered result by deterministic pagination;
3. retain an explicit maximum-page completeness gate;
4. preserve all scientific state/action/representation rules unless separately justified;
5. remain prospectively blind to augmented-state deletion outcomes.

R4 v1 remains permanently recorded as underpowered.
