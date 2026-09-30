# OACR Theory — Graph Prior-Art Boundary

Date: 2026-09-30

Status: **CLAIM BOUNDARY — graph-theoretic novelty must remain conservative**

The one-delta DAG carrier gives OACR an exact tractable theorem class. This does not imply that its underlying reachability facts are new graph theory.

## 1. Classical transitive reduction

Aho, Garey, and Ullman, "The Transitive Reduction of a Directed Graph," SIAM Journal on Computing 1(2), 131–137 (1972), DOI 10.1137/0201008.

Established object:

> an economical directed-graph representation preserving exactly the same reachability relation.

For DAGs, the transitive reduction is unique.

Therefore OACR must not claim novelty for:
- redundant-edge elimination;
- minimal reachability-preserving graph representation in a DAG;
- the fact that an asserted edge can be unnecessary when another path exists.

## 2. Reachability under single failures

The directed-graph literature already studies whether reachability survives edge/vertex failures.

Relevant examples include:

- Georgiadis et al., "All-Pairs 2-Reachability in O(n^w log n) Time," ICALP 2017;
- work on pairwise reachability oracles and preservers under failures;
- fault-tolerant reachability preservers for directed graphs.

These lines explicitly consider questions of the form:

\[
\text{is }v\text{ reachable from }u\text{ after edge }f\text{ fails?}
\]

and may produce separating-edge witnesses or sparse structures preserving such reachability.

Therefore OACR must not claim novelty for:
- computing whether a base reachability pair survives one deletion;
- edge-failure sensitivity;
- preserving reachability under registered failures;
- using separating edges as witnesses.

## 3. What the OACR one-delta theorem actually contributes

The graph facts become useful only after they are embedded in the OACR representation problem.

For each future deletion action \(f\), define:

\[
W_f
=
\{e=(u,v)\in D:
(u,v)\notin TC(G-f)
\}.
\]

For a registered contract \(A\):

\[
D^+(A)
=
\bigcup_{f\in A}W_f.
\]

The OACR theorem then connects this classical reachability-sensitivity object to a different target:

\[
\boxed{
\text{future native contract}
\to
\text{operational quotient}
\to
\text{persistent representation}
}
\]

Specifically, in the one-delta state family:

- inactive delta states collapse with base;
- every active delta state becomes an operational singleton;
- therefore:
  \[
  |O_A|=1+|D^+(A)|.
  \]

The contract-gated representation retaining exactly \(D^+(A)\) satisfies:

\[
P_{R_{\rm gate}}=O_A.
\]

The novelty claim, if any, belongs to this **representation-adequacy consequence**, not to the reachability query itself.

## 4. Contract evolution consequence

Because:

\[
D^+(A)=\bigcup_{f\in A}W_f,
\]

the exact representation changes with the registered future-use contract.

Within the declared identity-gated representation family:

\[
R^\star_A=R_{D^+(A)}.
\]

For two contracts \(A,B\):

\[
c_{\min}(A\to B)
=
|D^+(A)\triangle D^+(B)|
\]

under delta-record Hamming cost.

This gives OACR's specific bidirectional interpretation:

- new future operations may require adding distinctions;
- removed future obligations may justify deleting distinctions;
- the same native carrier can move in either direction as the contract changes.

This is not a claim about a new fault-tolerant reachability algorithm.

## 5. Relation to fault-tolerant reachability preservers

Fault-tolerant reachability preserver work asks for a sparse subgraph that continues to preserve selected reachability pairs under failures.

OACR asks a different question:

> when alternative persistent states are currently observationally equivalent, which distinctions between those states must the representation preserve so that future native actions remain behaviorally distinguishable?

The graph carrier makes these two questions touch, but they are not identical.

A reachability preserver changes/stores graph edges to preserve reachability properties.

OACR's representation layer may retain **identity of a currently redundant delta** because that identity predicts a future difference after a registered operation, even though it contributes no present reachability distinction.

## 6. Important negative boundary

The four-node multi-delta counterexample proves that componentwise activity does not remain exact when multiple deltas coexist.

This is consistent with the broader graph literature: interaction among paths/failures can require structures beyond independent single-pair/single-delta tests.

OACR therefore does not claim:

\[
\text{local edge sensitivity}
\Rightarrow
\text{universal exact representation repair}.
\]

Instead:

\[
\boxed{
\text{one-delta separable class}
\Rightarrow
\text{exact local gate}
}
\]

and:

\[
\boxed{
\text{multi-delta interaction}
\Rightarrow
\text{set-level closure/generator problem}
}
\]

## 7. Claim discipline

Safe:

> In a one-delta DAG carrier, standard single-edge reachability sensitivity induces an exact OACR operational quotient and therefore an exact contract-gated persistent representation.

Unsafe:

> We introduce a new algorithm for fault-tolerant reachability.

Unsafe:

> We discover that redundant graph edges can matter after failures.

Unsafe:

> The active-edge test is a new graph-theoretic notion.

Safe:

> The graph carrier provides a tractable theorem class in which the OACR native-contract, non-anticipating, bidirectional representation-repair object can be solved exactly.

## 8. Theory-Gate consequence

The graph prior-art audit strengthens rather than weakens the intended paper structure.

The theoretical contribution should be layered:

1. general OACR representation object;
2. exact structural theorem class built on known reachability facts;
3. interaction counterexample showing the local rule's boundary;
4. closure-system generalization for multi-delta states;
5. natural carriers testing whether the representation principle transfers beyond the exact structural class.

The graph lemma is infrastructure. The representation theorem is the OACR object.
