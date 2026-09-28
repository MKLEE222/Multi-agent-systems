# OACR-R4 v2 Engineering Failure Record — 2026-09-28

## Status

The first R4-v2 paginated execution, workflow run 36437114034, is an **engineering failure with zero scientific carrier outcomes**.

It is not a negative or positive result about the contract-gated representation.

## Frozen authority before the run

- protocol: docs/OACR_R4_V2_PAGINATED_REDESIGN_PROTOCOL.md
- protocol commit: 6795a534415e4f7270f2b25aca3522b653e413d3
- workflow commit: 1f43e8ff1dc528bb62b8023ef3013afe2c8e49b9

The five frozen roots, page size 2000, maximum 20 pages, state-bank rule, action-panel rule, Rgate transform, and replay requirements were all frozen before the run.

## Failure

All five matrix jobs failed in the producer on the first retrieved page with:

RuntimeError: page ordering violation at page 0

The failing assertion compared the SPARQL result order after QID normalization against Python string ordering.

The query used:

ORDER BY ?child ?parent

SPARQL RDF-term ordering is not a valid contract for Python lexical ordering of normalized QID strings.

## Scientific non-exposure

For all five roots, failure occurred before:

- complete paginated retrieval;
- graph completion;
- candidate-state selection;
- action-panel selection;
- contract-active classification;
- any augmented-state deletion outcome;
- any Rgate replay;
- any U/E computation.

Therefore the run reveals no scientific result about the fresh carriers.

## Allowed engineering correction

Without changing any scientific selection rule, the query ordering may be made explicit as string ordering:

ORDER BY STR(?child) STR(?parent)

The producer and verifier may continue to enforce exact page order and cross-page monotonicity under that explicit ordering.

No root, page size, max-page count, structural gate, state rule, action rule, representation, metric, or stopping rule may change.

The failed run remains retained in Actions history.
