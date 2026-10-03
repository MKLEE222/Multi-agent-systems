# N1 routing and gate diagnosis

Date: 2026-10-01. Authority: retrospective diagnosis of the eight-unit development
smoke. The 512-unit evaluation bank remained sealed in both runs.

## Verdict

The inherited B1 and sham constructors never activated the adapter on their 66
future queries. Temporarily opening every gate makes the inherited edited value
affect every query and improves pooled correctness from 3 to 7, with 6 gains and
2 losses. Forced B0, B1, sham and A0 have identical predictions. Therefore the
current auxiliary keys have not demonstrated a semantic advantage beyond gate
coverage. Copied values have a limited effect on this panel, with substantial
errors and observed damage. There is no constructor acceptance or family-level
impossibility result.

## Observer replay

Run: https://github.com/MKLEE222/Multi-agent-systems/actions/runs/36827221730
Frozen source: `35addf0c4f6ea6dfb18037e75a83a48d89331fb4`.
Protocol: `docs/OACR_N1_OBSERVER_REPLAY_PROTOCOL_2026-10-01.md`.

All summary and unit records exactly match recovery run 36824729008. The synthetic
official-GRACE/tiny-T5 fixture matched native logits, RNG and codebook, and detected
an auxiliary route. Native inference's unused cold-value RNG draws are retained;
the observer itself adds none. Every real variant evaluation preserves stored
keys, values, radii and labels.

| Variant | Queries | Gate active | Auxiliary active | Layer output changed |
|---|---:|---:|---:|---:|
| B0 base | 66 | 0 | 0 | 0 |
| B1 predictive | 66 | 0 | 0 | 0 |
| B2 sham | 66 | 0 | 0 | 0 |
| A0 test-prompt heuristic | 66 | 16 | 16 | 16 |

Every added value is an exact copy of the base edited value. A0 reaches exactly
its two test-prompt anchors per unit, demonstrating input-level controllability,
not an optimized oracle ceiling. Routing zero explains output identity in the
recorded native B1/sham run; it does not alone assess the value pathway.

## Frozen all-key gate ablation

Run: https://github.com/MKLEE222/Multi-agent-systems/actions/runs/36828185349
Frozen source: `6816674d0ecfaf4d1182ff39660dd7e7e1708b59`.
Protocol: `docs/OACR_N1_GATE_ABLATION_PROTOCOL_2026-10-01.md`.

After each unchanged native evaluation, an extra pass temporarily sets all radii
to 1,000,000. It restores original radii and CPU/Python RNG before the next native
operation. Keys/values are unchanged. The entire original native report again
matches the recovery report exactly. All 264 counterfactual query forwards activate
the gate and change layer output. Each variant retains its own native comparator.

| Variant | Forced correct / 66 | Mean unit accuracy | Changed predictions | Gains | Losses |
|---|---:|---:|---:|---:|---:|
| B0 base | 7 | 0.13690476190476192 | 65 | 6 | 2 |
| B1 predictive | 7 | 0.13690476190476192 | 65 | 6 | 2 |
| B2 sham | 7 | 0.13690476190476192 | 65 | 6 | 2 |
| A0 test-prompt heuristic | 7 | 0.13690476190476192 | 49 | 5 | 2 |

All forced prediction strings and pass cells match across variants, as expected
when copied values, replacement masks and open gates are identical. Pooled scores
are descriptive (native B0: 3/66=4.55%; forced: 7/66=10.61%). Macro accuracy averages
eight unit accuracies and is not interchangeable with that denominator. No failed
unit or query was removed; cluster independence and answer-scoring semantics are
not certified by this diagnosis. Counts are not independent sample sizes.

The ablation is a severe runtime intervention on already exposed development
queries. No deployable radius was selected and no confirmatory evidence was
created. The auxiliary-key versus sham separation remains zero. Raising radii
and declaring B1 successful would misattribute a common base-value effect.

## Evidence integrity

Original runner SHA-256:
`928aa6434bc4b31fa2e011f15f2d0e1be05fe7a7e04b37df0332941d0b98e91b`.
Reference report SHA-256:
`6d8267b2da83c30ba871cc02c34b97d6f858b0b6661611cf63d7be369c6a19c3`.

Observer artifact `11146125012`, ZIP digest matched GitHub:
`36e9c73f3f8d817431fdc50d150ec7d0690981a113a8827ebfd7cead74f98fd7`.
Routing JSON digest:
`4a4ec678ebe19acc449fcb1274890f7c0b30d3cda2fd3f1f6744e2c2c6d1d0c9`.

Ablation artifact `11146385728`, ZIP digest matched GitHub:
`72115f45e579e5556314b3e8b21f90ebcabca6a94b39a7ef53d99cb23346f02b`.
Ablation JSON digest:
`6539350f5246fd3b6c77da475b939e53d2b092733ea5a6bab2a1c8dc258ee72f`.

Raw JSON, original checksum, exact native replay and model-file provenance are
retained in `results/oacr_natural_learned_n1/routing_36827221730/` and
`results/oacr_natural_learned_n1/gate_36828185349/`, with `SHA256SUMS` in each.
Use `sha256sum -c SHA256SUMS` within its directory. Weights are not committed.

Next development protocol: `docs/OACR_NEXT_DEVELOPMENT_PROTOCOL_2026-10-01.md`.
