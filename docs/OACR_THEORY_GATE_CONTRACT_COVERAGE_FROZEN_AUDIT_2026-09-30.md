# OACR Theory Gate — Frozen Contract-Coverage Audit

Date: 2026-09-30

Status: **PASS on frozen R3/R4 artifacts**

This note verifies that the contract-lattice / coverage theorem family reproduces the already accepted R3/R4 results without fitting to their final operational partitions.

## 1. R4 source

Frozen artifact:

- workflow run: 36438278451;
- artifact ID: 11003190307;
- states: 272;
- candidate deltas: 271;
- registered deletion actions: 64;
- accepted active deltas: 22;
- accepted operational classes: 23.

For every action \(f\), define its activation set

\[
W_f
=
\{e\in D:e\notin TC(G-f)\}.
\]

The full contract prediction is

\[
D^+(A)=\bigcup_{f\in A}W_f
\]

and

\[
|O_A|=1+|D^+(A)|.
\]

## 2. R4 full-contract result

The union of all 64 frozen action activation sets contains exactly:

\[
22
\]

candidate deltas.

Therefore the theorem predicts:

\[
|O_A|=1+22=23.
\]

Frozen native replay reports exactly:

\[
23
\]

operational classes.

The predicted active set equals the accepted 22-state active set exactly.

## 3. R4 exhaustive registered-subcontract checks

The frozen producer already recorded:

- all 64 singleton contracts;
- all
  \[
  \binom{64}{2}=2016
  \]
  action-pair contracts;
- all 64 leave-one-out contracts.

For each recorded subcontract, the audit recomputed only the union of the corresponding \(W_f\) activation sets and predicted:

\[
|O_A|
=
1+\left|\bigcup_{f\in A}W_f\right|.
\]

Results:

- singleton mismatches: **0 / 64**;
- pair mismatches: **0 / 2016**;
- leave-one-out mismatches: **0 / 64**.

For every leave-one-out contract, the theorem's criterion

\[
\bigcup_{f\in A\setminus\{g\}}W_f
=
\bigcup_{f\in A}W_f
\]

also matched the frozen producer's full-partition-preserved-by-omission flag exactly.

Thus the action-content theory reproduces every subcontract result already present in the frozen R4 artifact.

## 4. R4 action-content geometry

Only:

\[
5/64
\]

registered deletion actions have nonempty activation sets.

Their activation-set cardinalities are:

- 19;
- 1;
- 1;
- 1;
- 1.

The remaining:

\[
59/64
\]

actions activate no candidate delta.

The largest single action therefore yields:

\[
1+19=20
\]

operational classes by itself, matching the accepted statement that one action produces 20 of the full panel's 23 classes.

This gives a precise explanation of why action count is a poor proxy for contract demand.

## 5. R4 minimum contract basis

Among the five nonempty actions, exhaustive subset search over the frozen activation matrix found a unique minimum action subset whose activation union equals the full 22-delta active set.

Minimum contract-basis size:

\[
\boxed{4}.
\]

Number of minimum bases:

\[
\boxed{1}.
\]

The unique four-action basis is:

- del:Q1689156>Q12518;
- del:Q1341387>Q785952;
- del:Q2038454>Q489357;
- del:Q3947>Q11755880.

This is a post-hoc theorem audit of the already frozen action matrix. It is **not** a prospectively registered empirical claim and must be labelled exploratory if used in the manuscript.

The important theoretical point is that contract-basis search reduces to coverage over the frozen activation matrix.

## 6. R4 closed-form directional gaps

Let

\[
n=272,
\qquad
m=22,
\qquad
n-m=250.
\]

The contract theorem predicts, under uniform state weights:

\[
U_{\rm coarse}
=
\log_2 272
-
\frac{250}{272}\log_2 250
=
0.7659699325535687\text{ bits},
\]

and

\[
E_{\rm full}
=
\frac{250}{272}\log_2 250
=
7.32149290869677\text{ bits}.
\]

Frozen artifact values:

\[
U_{\rm coarse}
=
0.7659699325535673,
\]

\[
E_{\rm full}
=
7.321492908696782.
\]

The differences are floating-point rounding only.

Also:

\[
U_{\rm coarse}+E_{\rm full}
=
\log_2 272.
\]

## 7. R3 source and prediction

Frozen R3 artifact:

- artifact ID: 10954033797;
- states: 272;
- operational classes: 101;
- accepted partition structure:
  - 100 singleton active classes;
  - one 172-state inactive/base class.

Thus:

\[
n=272,
\qquad
m=100,
\qquad
n-m=172.
\]

The theorem predicts:

\[
|O_A|=1+100=101.
\]

It also predicts:

\[
U_{\rm coarse}
=
\log_2 272
-
\frac{172}{272}\log_2 172
=
3.3914424816593067,
\]

and

\[
E_{\rm full}
=
\frac{172}{272}\log_2 172
=
4.696020359591032.
\]

Frozen artifact values are:

\[
U_{\rm coarse}
=
3.391442481659308,
\]

\[
E_{\rm full}
=
4.69602035959104.
\]

Again the differences are only floating-point rounding.

## 8. Consequence

R3 and R4 no longer need to be described as two unrelated empirical partition shapes.

They instantiate one common theory:

\[
\boxed{
\text{contract action content}
\to
\text{activation union}
\to
\text{operational quotient}
\to
\text{directional gaps}
\to
\text{unique exact gated representation}
}
\]

within the one-delta DAG carrier class.

R4 additionally supplies the prospectively cleaner, independently replayed exact repair result.

## 9. Authority boundary

The following are theorem-derived from frozen base structure and the registered action panel:

- activation sets \(W_f\);
- active union \(D^+(A)\);
- predicted class count;
- exact gated representation in the one-delta theorem class.

The following remain verification-only:

- augmented-state native outcome matrices;
- final producer partition hashes;
- producer/verifier matrix agreement.

The current audit used verification outcomes only to test the theorem's predictions after the fact.
