# OACR Natural Learned Evidence Protocol v1 — RippleEdits Structural Preflight

Date: 2026-10-01

Status: **FROZEN BEFORE ANY NEW NATURAL-LEARNED MODEL/EDITOR OUTCOME**

Pre-outcome structural correction: the first N0 run revealed that the repository README example misspells the first criterion as `Relation_Specifity`, while the released JSON loader and `src/benchmark.py` use `Relation_Specificity`. This schema correction was made before any model/editor execution and changes no sampling, eligibility, split, authority, repair, or evaluation rule.

Purpose: open the Natural Evidence Gate without rescuing or retuning the frozen COMPOSE-L recovery experiment.

## 1. Prior learned boundary

The COMPOSE-L recovery-hysteresis route is not extended.

Its already frozen post-recovery decision gate states that if at least 1024 recovery candidates are attempted and fewer than 8 accepted recovered states are obtained, the route is classified as recovery-state construction underpower and any successor must be a new preregistered carrier/mechanism.

The new Natural Learned line therefore does not relax:
- present-recovery criteria;
- parameter-inequality criteria;
- COMPOSE-L action panels;
- COMPOSE-L thresholds.

No COMPOSE-L outcome may be used to select individual RippleEdits examples.

## 2. Primary and secondary natural benchmarks

### Primary

RippleEdits official repository:

- repository: edenbiran/RippleEdits;
- frozen commit: 54f3b88af4895a3aacb580ec63ce7ae857185040;
- subsets:
  - data/benchmark/recent.json;
  - data/benchmark/random.json;
  - data/benchmark/popular.json.

RippleEdits is the primary benchmark because it supplies thousands of factual edits and six structured downstream criteria per edit, with explicit test and condition query structure.

### Secondary confirmation

MQuAKE official repository:

- repository: princeton-nlp/MQuAKE;
- frozen commit: fb43dadc2d8cd19d08ce81c63d957b59deb3f3cd;
- primary frozen file for later confirmation:
  datasets/MQuAKE-CF-3k-v2.json.

MQuAKE is not run in parallel during N0. It is retained as a second natural confirmation line after the primary protocol is stable.

## 3. Learned representation substrate

The intended constructive carrier is the explicit GRACE key-value adaptor:

- repository: Thartvigsen/GRACE;
- frozen commit: f674183f17a995d109e10ee6140d4c3e6d016115.

GRACE is chosen because the persistent learned representation is inspectable and manipulable:
- keys;
- values;
- epsilons;
- key labels.

The future N1 experiment will hold the base model, native GRACE editing procedure, and read executor fixed while changing only this persistent adaptor representation.

No N1 model outcome is authorized by this N0 protocol.

## 4. N0 is structural only

N0 may:
- clone frozen benchmark repositories;
- parse JSON;
- hash files;
- count edits, relations, criteria, condition queries, and test queries;
- construct deterministic development/evaluation manifests;
- verify disjointness and scale;
- inspect benchmark schema.

N0 may not:
- load an LM;
- load GRACE weights;
- execute a model query;
- perform a knowledge edit;
- evaluate an answer;
- inspect model logits;
- choose examples based on any learned-system outcome.

Therefore N0 cannot create model-outcome leakage into the later evaluation split.

## 5. RippleEdits contract schema

The six frozen criterion names are:

- Relation_Specificity;
- Logical_Generalization;
- Subject_Aliasing;
- Compositionality_I;
- Compositionality_II;
- Forgetfulness.

The spelling `Relation_Specificity` follows the released benchmark JSON and `src/benchmark.py`. The README example contains the typo `Relation_Specifity`; OACR follows executable source/data rather than the example typo.

For every candidate edit, N0 records only structural counts.

A candidate is structurally eligible when:

1. edit metadata contains:
   - prompt;
   - subject_id;
   - relation;
   - target_id;
2. all six criterion keys exist;
3. at least three criteria contain at least one test block;
4. at least one condition-query prompt exists;
5. at least four test-query prompts remain after exact normalized removal of prompts also appearing among condition queries.

These rules are fixed before any model outcome.

## 6. Deterministic split

Frozen quotas:

### Development
- recent: 64;
- random: 32;
- popular: 32;
- total: 128.

### Evaluation
- recent: 256;
- random: 128;
- popular: 128;
- total: 512.

Within each subset:
- eligible units are grouped by edit relation;
- each relation group is deterministically hash-sorted;
- relation groups are deterministically ordered;
- round-robin selection is used to reduce concentration;
- development units are selected first;
- evaluation units are selected from the remaining units.

The development and evaluation unit IDs must be disjoint.

No learned-system result may alter these manifests.

## 7. N0 acceptance gate

N0 passes only if all of the following hold:

- at least 1024 structurally eligible RippleEdits units;
- all development quotas are filled;
- all evaluation quotas are filled;
- development/evaluation overlap is zero;
- evaluation contains at least 24 distinct edit relations;
- development contains at least 16 distinct edit relations;
- all three source subsets contribute their frozen quotas;
- MQuAKE-CF-3k-v2 is present and parseable as a secondary benchmark;
- no model/editor package is invoked.

If N0 fails, a structural protocol revision is allowed because no model outcome has been generated. Any revision must be committed before N1 begins.

## 8. N1 constructor authority — frozen design direction

N1 will compare representation variants while keeping the native model/editor fixed.

### Base representation

The ordinary GRACE adaptor after applying the registered factual edit.

### Contract-relevant representation repair

The repair constructor may read:
- the edit request;
- subject/relation metadata;
- condition-query prompt strings from the frozen benchmark contract;
- the fixed base model's hidden activation at the GRACE key layer.

It may not read:
- answers to condition queries for constructor choice;
- held-out test-query prompts;
- held-out test answers;
- held-out model outputs;
- whether a held-out query later succeeds.

The intended repair adds auxiliary adaptor keys derived from construction-visible condition prompts while reusing the already learned edit value. It does not retrain the base LM and does not learn a new answer value from held-out outcomes.

### Matched sham

For every repaired unit, a same-cost sham will add the same number of auxiliary adaptor keys derived from deterministically matched condition prompts belonging to other units with different subject identity and relation, selected without learned-system outcomes.

### Oracle diagnostic

A test-query-visible repair may be implemented only as A0 oracle diagnostics. It can never count as confirmatory evidence.

## 9. Held-out future contract

The confirmatory future contract is the set of benchmark test queries that are not exposed to the repair constructor.

Condition queries and test queries therefore play different authority roles:

- condition-query prompts: construction-visible contract structure;
- test-query prompts and answers: verification-only.

If an exact normalized test prompt duplicates a condition prompt, that prompt is excluded from the held-out future set by the frozen structural rule.

## 10. Denominator discipline

Evaluation units are never dropped because:
- the base LM did not know a prerequisite;
- the native edit failed;
- a future query failed;
- the repair did not help.

Instead, the 512 evaluation units remain the master denominator.

Outcome-conditioned strata such as:
- immediate edit success;
- benchmark precondition success;
- future-query executable/valid status;

are reported as nested denominators, not used to replace the master evaluation bank.

## 11. N1 numerical gates are not yet authorized

N0 freezes the dataset, information boundary, representation intervention family, and sham logic.

Exact numerical N1 effect/closure thresholds will be frozen only after N0 structural results are available and before any N1 model/editor execution.

This is permitted because N0 contains no learned-system outcomes.

## 12. Natural Evidence mapping

If N0 passes:

- N1 benchmark maturity: RippleEdits primary;
- N2 shared continuation contract: six fixed criterion families with held-out test prompts;
- N3 scale: 512 untouched evaluation edits;
- N4 constructive repair: GRACE adaptor key repair vs same-cost sham;
- N5 negative boundary: if the frozen repair fails, report the failure without tuning on evaluation outcomes.

The experiment is allowed to be negative.
