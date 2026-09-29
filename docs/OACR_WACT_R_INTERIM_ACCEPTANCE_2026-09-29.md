# OACR-WACT-R Interim Acceptance — 2026-09-29

## Status

**PRIMARY CROSS-CARRIER PROMOTION GATE PASSED EARLY.**

This is an interim acceptance because the frozen eight-root workflow is still completing remaining roots.

Authoritative protocol:

docs/OACR_WACT_R_WRITE_ACTIVATION_FLIP_PROTOCOL_V1.md

Protocol commit:

6a616ae39ac065908d6a650869eb20f38ff335ff

Workflow run:

36526302297

## 1. Promotion gate

The preregistered primary gate required:

- at least 3 INCLUDED roots;
- at least 32 total prospective witnesses;
- zero inert-write native prediction failures;
- zero activating-write native prediction failures;
- zero representation-flip failures.

The first three completed INCLUDED roots already satisfy the gate:

### Q28640 — profession

- eligible distinctions: 29;
- prospective witnesses: 16;
- native causal failures: 0;
- exact representation flips: 16/16.

### Q7397 — software

- eligible distinctions: 33;
- prospective witnesses: 16;
- native causal failures: 0;
- exact representation flips: 16/16.

### Q34379 — musical instrument

- eligible distinctions: 26;
- prospective witnesses: 16;
- native causal failures: 0;
- exact representation flips: 16/16.

Aggregate:

\[
3\text{ INCLUDED carriers},
\qquad
48\text{ prospectively selected witnesses}.
\]

For all 48 witnesses:

\[
x\equiv_{\mathcal W^-}y
\]

but after adding exactly one preregistered native WRITE,

\[
x\not\equiv_{\mathcal W^+}y.
\]

The contract-gated representation flips accordingly:

\[
\phi_{\mathcal W^-}(x)=\phi_{\mathcal W^-}(y)
\]

and

\[
\phi_{\mathcal W^+}(x)\neq\phi_{\mathcal W^+}(y),
\]

with

\[
U=E=0
\]

under both nested contracts.

All three artifacts passed the independent verifier, which reconstructed the carrier, action panel, activation matrix, witness selection, and native causal replay from raw carrier data.

## 2. Accepted empirical statement

The current accepted relational-family statement is:

> In multiple prospectively sampled native relational carriers, the operational necessity of a fixed stored distinction can be switched solely by changing the declared future WRITE contract, while the states and current READ remain fixed. The same WRITE intervention determines whether the distinction may be erased or must be retained in an exact sufficient representation.

This is stronger than a compression statement.

The measured storage reduction is a consequence of which distinctions remain WRITE-inert; it is not the defining phenomenon.

## 3. Activation concentration — secondary observation

The three accepted roots also show highly concentrated WRITE-activation load.

### Profession

- 47/64 writes activate zero registered distinctions;
- Gini of activation load: 0.8422;
- top 10% of writes account for 67.74% of activation events;
- top 25% account for 96.77%.

### Software

- 53/64 writes activate zero registered distinctions;
- Gini: 0.9338;
- top 10% account for 88.24% of activation events;
- top 25% account for 100%.

### Musical instrument

- 58/64 writes activate zero registered distinctions;
- Gini: 0.9663;
- top 10% account for 100% of activation events;
- top 25% account for 100%.

However, base deletion impact and activation load are also strongly correlated on these carriers.

Therefore activation concentration is retained as a secondary structural result and is **not** yet promoted as a general independent law.

## 4. Important boundary

The relational WACT-R flip is structurally predicted by the registered reachability certificate.

Therefore this block alone cannot establish that WRITE-induced representational relevance is a general computational phenomenon rather than a property of graph deletion/redundancy.

The next critical gate is cross-substrate replication under a materially different native WRITE semantics.

Priority:

1. Git merge/history;
2. learned persistent-state editing.

## 5. Continuing frozen roots

The remaining preregistered WACT-R jobs continue unchanged.

No root is replaced because of truncation, exclusion, weak activation, or inconvenient results.

Final WACT-R acceptance will aggregate all eight frozen roots after workflow completion.
