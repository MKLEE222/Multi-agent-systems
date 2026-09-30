# OACR Natural Learned N0 Acceptance — RippleEdits

Date: 2026-10-01

Status: **PASS — structural-only, zero model/editor outcomes**

Workflow:
- OACR Natural Learned N0 Structural Preflight
- successful run: 36743639626
- head commit: 2dcb9d4dd6892363744677d2177d23b03876da48
- artifact ID: 11111701511
- artifact digest:
  sha256:4278fb519de4a10e1fe2dd5545088bd2eea2268264c4abf53c09facdea26e51e

Frozen sources:
- RippleEdits commit 54f3b88af4895a3aacb580ec63ce7ae857185040
- MQuAKE commit fb43dadc2d8cd19d08ce81c63d957b59deb3f3cd
- GRACE commit f674183f17a995d109e10ee6140d4c3e6d016115

## Structural result

RippleEdits released entries:
- recent: 1,948
- random: 1,922
- popular: 885
- total: 4,755

Structurally eligible under the prospectively frozen rule:

\[
\boxed{1,462}
\]

This exceeds the preregistered minimum of 1,024.

Frozen development bank:

\[
\boxed{128}
\]

with:
- recent 64
- random 32
- popular 32
- 35 distinct edit relations

Frozen evaluation bank:

\[
\boxed{512}
\]

with:
- recent 256
- random 128
- popular 128
- 27 distinct edit relations

Development/evaluation overlap:

\[
\boxed{0}
\]

Duplicate unit IDs:

\[
\boxed{0}
\]

## Future-contract size

Across the 128 development units:
- construction-visible condition prompts: 2,177
- all test prompts: 2,253
- held-out test prompts after exact condition/test overlap removal: 1,174

Across the 512 evaluation units:
- construction-visible condition prompts: 7,158
- all test prompts: 7,582
- held-out test prompts after exact condition/test overlap removal:
  \[
  \boxed{4,212}
  \]
- minimum held-out test prompts per evaluation unit: 4
- median: 7
- maximum: 45

Therefore the future verification contract is not a small witness set. It contains thousands of withheld natural-language continuation probes over hundreds of frozen edit units.

## Secondary benchmark

MQuAKE-CF-3k-v2:
- entries: 3,000
- SHA256:
  f82091cbb668cef8f2537f79f1768af1840184450b347ff8c344336090ddc71e

MQuAKE remains a secondary confirmation line and was not used to choose RippleEdits evaluation units.

## Authority result

N0 imported no torch, transformers, datasets, GRACE, or EasyEdit.

It generated no model/editor outcome.

Thus the 512 evaluation unit IDs were frozen before any new Natural Learned model execution.

## Schema correction record

The first N0 run failed structurally because the RippleEdits README example uses the typo Relation_Specifity, while the released data loader and benchmark source use Relation_Specificity.

The correction:
- occurred before model/editor execution;
- changed no eligibility threshold;
- changed no split quota;
- changed no authority boundary;
- changed no repair design;
- changed no evaluation rule.

## Natural Evidence consequences

### N1 — mature benchmark

\[
\boxed{\text{STRUCTURAL PASS}}
\]

RippleEdits is frozen as the primary natural learned benchmark.

### N2 — shared continuation contract

\[
\boxed{\text{STRUCTURAL PASS}}
\]

All units use the same six criterion families, while held-out test prompts are kept outside constructor access.

### N3 — scale

\[
\boxed{\text{MANIFEST PASS}}
\]

512 untouched evaluation edits are frozen, with 4,212 held-out future prompts.

Actual learned-system execution is still required before N3 is fully empirical.

### N4 — constructive repair

OPEN.

The frozen target is GRACE adaptor representation repair:
- base codebook;
- contract-relevant auxiliary keys derived from condition prompts;
- same-cost sham auxiliary keys from matched irrelevant units;
- fixed model/editor and shared learned value.

### N5 — negative boundary

OPEN, but governance is frozen:
- no evaluation-tuned rescue;
- a failed repair is reportable as a learned representation boundary.

## Verdict

\[
\boxed{\text{N0 PASS}}
\]

The Natural Learned line is now formally open. The next authorized action is dev-only N1 implementation/calibration on the frozen 128-unit development bank. The 512-unit evaluation bank must remain untouched until the N1 numerical and implementation gates are frozen.
