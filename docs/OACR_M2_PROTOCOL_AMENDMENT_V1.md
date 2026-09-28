# OACR-M2 Protocol Amendment v1 — Reproducibility and Order-Robust Contract Analysis

**Date:** 2026-09-28  
**Status:** frozen after M2 v1 registration and before inspection of any M2 v1 scientific outcome.  
**Supersedes for new runs:** analysis/reporting rules in `OACR_M2_NESTED_CONTRACT_TRAJECTORY_PROTOCOL_V1.md`.  
**Does not delete or reinterpret:** M2 v1 protocol, implementation, workflow, issues, or any resulting artifacts.

## 1. Reason for amendment

A protocol audit identified four structural deficiencies that must be corrected before M2 is used as evidence:

1. a single nested action order does not separate contract-size effects from action-content/order effects;
2. summary-only artifacts are insufficient for independent recomputation of partitions and directional adequacy gaps;
3. `first adequate prefix` is not an informative transition statistic for a fixed representation under monotonically strengthening contracts;
4. the current experiment varies action-family breadth only and must not be described as a general contract-strength or learned-system result.

These are protocol-discipline corrections. They are made without inspecting M2 v1 scientific outcomes.

## 2. Scope of M2 v2

M2 v2 studies **action-family breadth and content** at fixed:

- state bank;
- observation family;
- horizon \(H=1\);
- legality/status semantics;
- outcome encoding;
- state weights;
- implemented representation partition.

Thus the varying contract is explicitly

\[
\mathcal C_A=(\mathcal O, A, H=1,\mathsf{Legal},\mathsf{Cost}),
\]

with only \(A\) changing.

M2 v2 does not by itself establish a horizon law, a learned-representation law, or a universal cross-system law.

## 3. Raw recomputation requirement

Every M2 v2 artifact must contain enough information to recompute all reported partitions and metrics without rerunning the native carrier.

Required fields:

1. complete state manifest;
2. complete action manifest and immutable action IDs;
3. declared state weights;
4. fixed representation signatures for every registered state;
5. complete state-by-action native outcome-signature matrix;
6. every analyzed contract subset as action IDs or indices;
7. operational partition assignment for every analyzed contract;
8. directional gap outputs derived from those partitions;
9. deterministic manifest hashes for states, actions, representations, and outcome matrix;
10. runtime manifest.

Summary-only artifacts are invalid.

## 4. Contract-content/order robustness

### 4.1 Git: exact contract lattice

For the frozen G5 12-action panel, enumerate **all**

\[
2^{12}=4096
\]

action subsets.

For each subset \(A'\subseteq A\), derive the exact operational partition and fixed-representation diagnostics.

Aggregate by subset cardinality \(|A'|=k\), reporting the complete distribution across all subsets of that size.

The original G5 target order remains available as a canonical chain for interpretability, but no scientific conclusion about trajectory shape may depend on that one chain.

### 4.2 Relational: deterministic order-robust ensemble

The R3 action panel has 64 actions and cannot be exhaustively enumerated.

Freeze 64 deterministic, outcome-blind action permutations. For permutation seed \(j\in\{0,\ldots,63\}\), order actions by

\[
\mathrm{SHA256}(\texttt{"OACR-M2-R-V2|"}j\texttt{"|"}\mathrm{actionID})
\]

with action ID as lexical tie-break.

For every \(k\in\{0,\ldots,64\}\), analyze the unique size-\(k\) prefixes induced by these 64 permutations.

The original maximin-rank chain is retained as a canonical descriptive chain but is not the only trajectory evidence.

The deterministic ensemble is a sensitivity design, not a random-sampling estimator of all \(\binom{64}{k}\) subsets.

## 5. Fixed representations

All primary representation partitions are fixed before any contract-subset analysis.

### M2-R
- R0-fixed: complete current closure;
- Rfull-fixed: complete asserted-edge identity;
- Rsupport64-fixed: full 64-action endpoint path-count vector.

### M2-G
- R0-fixed: current tree;
- Rfull-fixed: commit identity;
- R1-fixed12: tree + full 12-target ancestry vector;
- R2-fixed12: tree + full 12-target merge-base vector.

Rsupport64, R1-fixed12, and R2-fixed12 are explicitly classified as **full-panel contract-aware fixed representations**. They may demonstrate adequacy relative to the frozen panel but must not be described as contract-independent representations.

Any representation whose coordinates change with the analyzed subset is exploratory only.

## 6. Correct transition statistics

For the canonical chain, report for each fixed representation:

- **first_inadequate_prefix:** smallest \(k\) with \(U_k>0\), if any;
- **last_adequate_prefix:** largest \(k\) with \(U_k=0\);
- **first_zero_excess_prefix:** smallest \(k\) with \(E_k=0\), if any;
- **exact_match_prefixes:** all \(k\) with \(U_k=E_k=0\);
- **exact_match_interval:** the contiguous interval of exact matches when one exists.

Do not use `first adequate prefix` as a primary statistic.

For the lattice/ensemble analysis at each cardinality \(k\), report:

- operational class-count distribution;
- operational entropy distribution;
- \(U\) distribution;
- \(E\) distribution;
- pairwise under-/over-refinement distributions;
- fraction of analyzed subsets with \(U=0\);
- fraction with \(U=E=0\).

For Git these fractions are exact over all size-\(k\) subsets.  
For R3 they are deterministic ensemble fractions and receive no probabilistic population interpretation.

## 7. Refinement-event metrics

Action count is not treated as a metric of equal operational demand.

For every edge in a canonical chain, report:

\[
\Delta |O|_k=|O_k|-|O_{k-1}|,
\]

\[
\Delta H(O)_k=H(O_k)-H(O_{k-1}),
\]

and for each fixed representation:

\[
\Delta U_k=U_k-U_{k-1},
\qquad
\Delta E_k=E_k-E_{k-1}.
\]

This distinguishes redundant added actions from actions that induce new operational distinctions.

## 8. Identity and endpoint regression

A valid v2 run must record and hash:

- exact state manifest;
- exact full action panel;
- exact fixed representation signatures;
- exact state-by-action outcome matrix.

The full-contract endpoint must reproduce frozen R3/G5 metrics.

G5 **discovery and validation** endpoints both receive hard regression checks.

Matching summary numbers without matching the deterministically reconstructed state/action identities is insufficient for v2 artifact validity.

## 9. Runtime freeze

### Relational
Record:
- Python version;
- NetworkX version;
- raw Wikidata carrier SHA256;
- script/protocol commit SHA when available.

### Git
Require:
- source HEAD `34f06850c16c7f7ac822b1adc71354f11b0f2ca3`;
- Git version exactly `2.55.0`;
- `GIT_CONFIG_NOSYSTEM=1`;
- `GIT_CONFIG_GLOBAL=/dev/null`;
- fixed locale and timezone;
- clean checkout before every native action.

A runtime-version mismatch invalidates the run instead of silently changing semantics.

## 10. Information quantities

Every analyzed contract must report explicitly:

- \(H(R)\);
- \(H(O)\);
- \(H(R,O)\);
- \(I(R;O)\);
- \(U=H(O\mid R)\);
- \(E=H(R\mid O)\);
- variation of information.

These are class-information quantities, not physical storage, parameter, runtime, or update-cost burdens.

The terms **representation burden** and **operational information law** are not used for M2 v2 unless a separate physical-cost variable is measured.

## 11. Interpretation status

M2-R/G v2 remains a post-R3/G5 **developmental characterization** because the full-contract endpoints were known before M2 was conceived.

The exact Git lattice and deterministic relational ensemble correct order/content dependence but do not make the existing carriers confirmatory.

Fresh-carrier confirmation requires a separately frozen M2b protocol before those carrier outcomes are inspected.

Learned/horizon evidence requires a separately frozen M2-L/L1b protocol. M2 v2 must not use relational + Git evidence to imply a learned-system trajectory.

## 12. Failure retention

All outcomes are retained, including:

- trajectory concentrated in one action;
- large order/content sensitivity;
- no nontrivial refinement over most subsets;
- intermediate representation always over-refining;
- intermediate representation becoming inadequate;
- failure of endpoint regression;
- runtime mismatch;
- raw-artifact hash mismatch.

Protocol repair precedes outcome interpretation.
