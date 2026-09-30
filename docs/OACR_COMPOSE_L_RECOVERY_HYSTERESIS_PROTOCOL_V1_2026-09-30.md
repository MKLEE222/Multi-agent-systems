# OACR-COMPOSE-L v1 — Learned Recovery Hysteresis Protocol

**Date:** 2026-09-30  
**Status:** prospectively frozen before any recovery-state future-write outcome is inspected  
**Carrier:** frozen SCOTUS/BERT direct-parameter Finetune ecology used by L2/L2b  
**Scientific target:** restoration without restoration of future update response

## 1. Primary question

Can a native edit followed by a native counter-edit restore the registered present while leaving a persistent parameter state that responds differently to a later common write?

The target witness is:

\[
R_0(X_{\mathrm{base}})
=
R_0(X_{\mathrm{recovered}})
\]

with

\[
P(X_{\mathrm{base}})
\ne
P(X_{\mathrm{recovered}}),
\]

followed by at least one frozen future write \(w\) such that

\[
R_0(W_w(X_{\mathrm{base}}))
\ne
R_0(W_w(X_{\mathrm{recovered}})).
\]

Interpretation:

> restoring the registered present does not necessarily restore the object's future update response.

This is a recovery/continuation result, not a claim that the full parameter state was restored.

## 2. Frozen native mechanism

Reuse exactly:

- Thartvigsen/GRACE commit \`f674183f17a995d109e10ee6140d4c3e6d016115\`;
- official \`grace.editors.ft.Finetune\`;
- frozen SCOTUS/BERT model/tokenizer assets;
- target parameter \`bert.encoder.layer[10].output.dense.weight\`;
- Adam recreated per write;
- \`edit_lr = 1e-2\`;
- \`n_iter = 100\`;
- dropout 0;
- deterministic CPU execution.

Only the registered target parameter may change.

## 3. Deterministic folds

Use the same eight deterministic circular dataset folds:

\[
f\in\{0,\ldots,7\}.
\]

For dataset length \(N\),

\[
s_f=\left\lfloor\frac{fN}{8}\right\rfloor.
\]

Traversal is circular from \(s_f\).

No fold may be replaced.

## 4. Base state

Unlike L2b, the recovery study begins from the frozen unedited model state in each fresh fold job.

Record:

- exact target-parameter hash;
- full frozen current-task READ panel;
- diagnostic logits.

The same initial model bytes are required across folds; fold only changes deterministic candidate/panel ordering.

## 5. Outcome-blind future action bank

Before any recovery candidate is written:

1. traverse the fold order;
2. collect the first 512 examples currently misclassified by the base model;
3. group them by true target label;
4. choose three unique future actions by deterministic label-balanced round robin;
5. freeze their dataset IDs.

These future action IDs are removed from all anchor/sentinel banks.

No future write is executed during selection.

## 6. Outcome-blind current READ panel

Before any recovery candidate is written, freeze:

- the 3 future-action examples;
- 32 deterministic sentinel examples taken from fold order outside all future-action IDs and anchor-candidate bank;
- the anchor text itself for each candidate when that candidate is evaluated.

Primary current equivalence \(R_0\) uses exact task-level tuples:

- predicted class;
- registered target class;
- correctness.

Diagnostic logits/probabilities/margins are stored separately and do not define the primary positive.

## 7. Recovery candidate bank

Construct before any candidate write:

- first 256 examples in fold traversal that are **correctly classified** by the base model;
- exclude future-action IDs and sentinel IDs.

Let the dataset true label be \(y\).

Let \(K\) be the number of distinct dataset labels, computed from the frozen dataset before writes.

Define the forward counterfactual label outcome-blindly as:

\[
y^+=(y+1)\bmod K.
\]

No alternative target is chosen from model outcomes.

## 8. Native edit -> counter-edit construction

For each frozen anchor candidate in order:

### Forward write

From the exact base target-parameter tensor:

1. clone the anchor request with the same text and target label \(y^+\);
2. execute official Finetune;
3. require the counterfactual target to be realized;
4. require parameter hash differs from base.

If either fails, serialize and continue.

### Counter-edit

Without resetting after the forward write:

1. clone the same text with its original dataset target \(y\);
2. execute official Finetune;
3. require the original target to be realized.

This is the native recovery path.

No custom inverse optimizer, interpolation, or direct weight restoration is permitted.

## 9. Recovered-state acceptance

A candidate becomes \(X_{\rm recovered}\) only if all are true:

1. anchor original target is realized after counter-edit;
2. the complete frozen current-task READ panel, augmented with the anchor item, equals the corresponding base READ exactly;
3. target-parameter hash differs from the base hash;
4. the recovered tensor is finite;
5. two immediate READ evaluations without mutation agree exactly.

Diagnostic logit equality is reported but not required.

Retain at most four recovered states per fold.

Stopping rule:

- stop after four recovered states;
- otherwise exhaust all 256 frozen anchor candidates.

All attempts before stopping are serialized.

## 10. Future-write probe

Only after the recovered state bank is fixed for the fold:

For base and every retained recovered state, execute each of the three frozen future writes from the exact corresponding pre-write tensor.

Record:

- native write status;
- target realization;
- complete registered task READ after the write;
- diagnostic logits;
- post-write target-parameter hash.

A base/recovered pair separates under action \(w\) iff either:

- native status/target-realization differs; or
- any primary task READ tuple differs.

No tolerance is used for the primary task relation.

## 11. Primary positive

A prospectively registered positive exists if at least one accepted recovered state satisfies:

\[
R_0(X_{\rm base})=R_0(X_{\rm recovered})
\]

but for at least one frozen future action:

\[
R_0(W_w(X_{\rm base}))
\ne
R_0(W_w(X_{\rm recovered})).
\]

Promotion requires independent targeted native replay from fresh model/editor initialization.

## 12. Stronger diagnostic classes

Report separately:

### H0 recovery only

Current task READ restored, parameter state differs.

### Recovery hysteresis positive

Current task READ restored, common future write separates.

### Diagnostic logit recovery

Whether current logits also match within:

- atol \(10^{-6}\);
- rtol \(10^{-5}\).

### Selective future response

Whether some frozen future writes separate while others remain equivalent.

Selectivity is descriptive unless replicated.

## 13. Negative / underpower rules

### Strong recovery-future negative

May be claimed only if:

- at least 4/8 folds produce accepted recovered states;
- aggregate accepted recovered states >= 20;
- all three future branches execute for every accepted state;
- exact reconstruction/determinism controls pass;
- future separations = 0.

### Recovery-construction boundary

If at least 1024 aggregate recovery candidates are attempted and fewer than 8 accepted recovered states are produced, report:

\`RECOVERY_STATE_UNDERPOWERED\`

and do not interpret absence of future separation.

### Other engineering failure

Retain separately and do not count as scientific negative.

## 14. Determinism controls

Per COMPLETE fold:

1. reconstruct base READ and base parameter hash twice from fresh initialization;
2. replay the first accepted recovery path twice;
3. replay base + first future action twice;
4. replay first recovered state + first future action twice.

Require exact parameter hashes and primary task READs.

## 15. Representation consequence

If a recovery hysteresis positive exists, the current-task representation is sufficient for the restored present but not closed under the frozen future-write contract:

\[
R_0(X_{\rm base})=R_0(X_{\rm recovered})
\]

while

\[
O_W(X_{\rm base})\ne O_W(X_{\rm recovered}).
\]

This directly returns the result to OACR:

> a representation can certify present recovery while omitting a historical/parameter distinction required for future continuation.

A later redesign must identify a prospective certificate for the necessary distinction; full parameter identity is not automatically accepted as the scientific solution.

## 16. Boundaries

A positive result does not establish:

- semantic or cognitive memory;
- universal irreversibility of model editing;
- failure of machine unlearning;
- universal optimizer path dependence;
- population prevalence across models/tasks.

Preferred language is:

- latent history dependence;
- recovery hysteresis;
- history-conditioned update response.

## 17. Relation to COMPOSE

This protocol is intentionally not a generic H2 sequence search.

The composition is structurally meaningful:

\[
\text{forward edit}
\rightarrow
\text{counter-edit/recovery}
\rightarrow
\text{future write}.
\]

The first two writes are required to return the object to the same registered present. The third tests whether continuation has also been restored.
