# OACR N1 development recovery verdict

Date: 2026-10-01 (Asia/Shanghai)
Run: https://github.com/MKLEE222/Multi-agent-systems/actions/runs/36824729008
Source: `1cecafd7aea00fac34c9e44f88df90fe11593b25`
PR: https://github.com/MKLEE222/Multi-agent-systems/pull/89 (draft)

## Verdict

**ENGINEERING PASS / CURRENT CONSTRUCTOR DEV GATES NOT PASSED.**

All eight frozen smoke units completed; all eight immediate factual edits passed.
The synthetic T5/official-GRACE interface check and pinned checkpoint staging
passed. These establish executable task-performance feasibility. They do not
establish quotient repair or operational maintenance.

## Results and denominators

The runner's primary score is the unweighted mean of eight per-unit accuracies.
The pooled score below is descriptive and uses 66 future-query rows. The eight
units and 66 rows are development observations with unverified cluster independence.
No significance test or natural-scale independent replication is claimed.

| Variant | Auxiliary keys per unit | Mean unit accuracy | Pooled correct / 66 | Changed predictions vs B0 |
|---|---:|---:|---:|---:|
| B0 base | 0 | 0.025595238095238095 | 3 | 0 |
| B1 predictive | 2 | 0.025595238095238095 | 3 | 0 |
| B2 sham | 2 | 0.025595238095238095 | 3 | 0 |
| A0 test-prompt heuristic | 2 | 0.04345238095238095 | 4 | 16 |

B1 and B2 match B0 on every prediction string and every pass/fail cell in the
common panel. A0 gains one correct cell and loses none. Row alignment was checked
by criterion and prompt. No incomplete/unparsable unit was removed (counts: zero).

### Frozen dev gates

- D1: **PASS in the declared key-count intervention sense**, two added keys.
- D2: **NOT PASSED**, B1 future accuracy improvement equals zero.
- D3: **NOT PASSED**, B1 minus sham improvement equals zero.
- Evaluation unlock: **NO**, 512-unit bank remains sealed.

Successful CI means execution and assertions passed; it does not imply D2/D3
passed. The weak A0 is not a family-level upper bound. No impossibility claim
about GRACE, learned representations or representation repair follows.

## What the failure identifies

Follow-up completed: exact observer replay found zero B1/sham gate activation,
and a frozen all-key gate ablation found a common base-value effect with no
auxiliary-key separation. The uncertainty and proposed priority below describe
the recovery run before those diagnoses. Current localization and raw evidence:
`docs/OACR_N1_ROUTING_AND_GATE_VERDICT_2026-10-01.md`.

The current rule copies the first edited value into at most two condition-prompt
keys, at the inherited radius. On this panel it produced no output change.
The missing diagnostic is whether those keys cover the future queries internally,
and whether the copied value is suitable for them. Output equality alone cannot
distinguish non-activation from activation with ineffective values. The low
baseline score also warrants an edit-target/query semantics check.

Priority for this ancillary branch is an observer-only replay with routing,
distance/radius and key/value telemetry, plus a check of the primary-edit and
future-query relationship. Such replay is retrospective development analysis;
it must reproduce these predictions before supporting a failure-localization
claim. Do not tune a radius or discard failed units and reuse this smoke as fresh
confirmation. Any constructor change starts an explicitly recorded new dev round.

Core theory work continues independently, with T2/T5 open and the same-input
nearest-neighbor comparison as the main unresolved contribution gate.

## Evidence integrity

Artifact ID: `11145276631`, name `oacr-natural-learned-n1-dev-smoke`.
Downloaded ZIP SHA-256 (matched GitHub artifact digest):
`172be2de969011c4ad1ac3814a4123177dc12500d50db19b412daf92905e6c7f`.

Raw JSON SHA-256 (matched the runner's checksum):
`6d8267b2da83c30ba871cc02c34b97d6f858b0b6661611cf63d7be369c6a19c3`.

Retained raw files:

```text
results/oacr_natural_learned_n1/recovery_36824729008/
  n1_dev_smoke.json
  n1_dev_smoke.sha256
  oacr_snapshot_provenance.json
  SHA256SUMS
```

The inherited checksum file contains its original runner-relative path. For the
retained directory use `sha256sum -c SHA256SUMS` inside that directory. The model
snapshot revision is `4371c64b6f65176f6663af43066bd094597b1116`, with individual
file hashes in both the JSON report and snapshot provenance. Model weights are
not committed to this repository. Earlier failed run `36818820271` is retained
as an engineering failure and is not overwritten by this successful recovery.
