# Same-input residual-state comparison

Date: 2026-10-01. Authority: same-assistant mathematical reduction and executed
synthetic differential audit. No independent review or novelty clearance.

## Decision

The budgeted one-addition quotient and its executable residual updates have a
standard finite-state realization on exactly the same graph contracts. The
restricted-cut implementation avoids explicit continuation expansion, but this
alone does not distinguish it from classical graph sensitivity methods. T2/T5
remain open. This supersedes the 2026-09-30 source audit's “T5 WORKING PASS” and
its ingredient-based argument for an independent semantic object.

## Equal inputs and observable context

Fix a DAG G, D=TC(G) minus G, deletable base edges A contained in G, and h between
zero and |A|. Concrete initial states are no-addition and each single e in D.
The implementation has the graph/action/budget context and a per-state addition
witness at compilation. The comparison gives both implementations these inputs.

Build a finite deterministic system with states (F,e), where F is a subset of A,
|F|<=h, and e is no-addition or a candidate. Its observation is

    (F, TC((G minus F) union {e})).

The context F is included so states from different residual contracts are not
pooled. Within a fixed F it adds no distinction between candidates. Legal actions
delete a in A minus F when |F|<h, taking (F,e) to (F union {a},e). The remaining
budget is h-|F|. Illegal actions have the same explicit undefined marker for all
states with that context. Equivalently they can be totalized with an observable
reject sink. No finite horizon is reset after a transition.

Every legal word corresponds to a failure set J contained in A minus F with
|J|<=h-|F|; every such set has a legal ordering. Order does not change the final
graph. Thus equality of all finite residual observation words is exactly equality
of the registered failure-set behavior signatures at that context.

## Standard partition refinement and executable updates

Begin with current-observation equality. Repeatedly split a class when one action
has destinations in different classes. In this finite deterministic system the
stable partition is the coarsest observation-preserving transition congruence.
Proof: every stable class preserves each observation word by induction. Conversely,
word-equivalent states have equal current observations and word-equivalent action
destinations, so no refinement separates them.

For any final class q and legal action a, choose any member s and return the class
of T_a(s). Congruence makes the choice independent of s. This is an executable
quotient update table with the same commuting square as the graph compiler.
Consequently, implemented updates and residual budgets do not by themselves
establish a semantic object absent from standard state minimization.

The graph compiler uses e when the A-restricted cut between its endpoints is at
most the residual budget, otherwise no-addition. The earlier structural proof
establishes that this labels the same partition. This audit executes both routes,
without giving the graph compiler the baseline's observation matrix.

## Constructive abstract-interpretation instance

This translation is our derivation, not a claim that the cited papers analyzed
this graph carrier. Let S be the residual system, C be its finite powerset lattice,
and lift each partial action to an additive image function f_a, mapping an invalid
state to the empty set. Let rho saturate subsets by the stable partition P, and pi
by current-observation equality. Since P refines observations, pi rho = pi.
Since P is a deterministic congruence with homogeneous legality,

    rho f_a rho = rho f_a.

This is the backward-completeness equation for successor image functions. It must
not be mislabeled forward completeness: forward completeness would additionally
ask that images of saturated sets are saturated. For example a constant function
inside a two-member block is a congruence but its singleton image is not saturated.
Induction over a word gives observationally identical results after abstraction
at every step: pi applied to the abstract computation equals pi applied to the
concrete computation. The residual quotient therefore supplies an observationally
complete partitioning abstraction in this finite instance.

This is a sufficient constructive instance. It does not claim that all general
observationally complete domains are partitioning, or that their least domain is
always this partition closure. Amato–Scozzari explicitly distinguish observational
completeness from ordinary completeness and their least-domain constructions.

The complete core/shell literature already treats both domain extension and
restriction. Its lattice optimization objective is not identical to retaining
physical edge records. That difference must be stated through a restricted repair
language and an actual cost result, rather than claiming bidirectionality itself
is absent from the prior framework. A source witness is charged equally to both
routes: neither can recover distinctions erased from its only available input.

## Executed same-input comparison

Code: `experiments/oacr_theory/compare_residual_partition_v1.py`.
Result: `docs/OACR_SAME_INPUT_RESIDUAL_PARTITION_RESULT_2026-10-01.json`.

The independent observation path uses bitset Warshall, while the unchanged
compiler uses restricted flow. Enumerated exactly the inherited candidate bank:
all edge subsets respecting a fixed vertex order on 2–5 nodes; skip graphs without
redundant candidates; every A and h; every legal residual context. These are not
all possible vertex relabelings or independent statistical samples.

| Check | Count | Result |
|---|---:|---|
| Graph/action/budget contracts | 182,104 | Matches inherited audit denominator |
| Expanded residual states / native observation calls | 6,234,453 | Charged to baseline |
| Residual contexts across contracts | 2,441,430 | Contexts kept distinct |
| Same-context candidate partition pairs | 11,761,605 | Zero mismatches |
| Standard quotient transition checks | 13,703,208 | Well-defined and commuting |
| Stored-representation transition checks | 13,703,208 | Equal to full-state compiler |

The larger transition count than the inherited 1,453,876 is caused by checking
each residual prefix, not just the initial one-step square. It is not new sample
independence. Candidate-bank preparation requires 1,098 current-graph closures;
the baseline's additional continuation observations are recorded separately.

Reproduce from the repository root:

```bash
python experiments/oacr_theory/compare_residual_partition_v1.py --max-n 5 --out /tmp/oacr_same_input.json
```

## Cost comparison and remaining claim

Write d=|D|, a=|A| and M=(d+1) sum_{j=0}^h binomial(a,j). An explicit baseline
builds M observations and at most aM transition entries per initial contract;
stored observation matrices add up to O(M n^2) bits. This reference refinement is
intentionally simple, not the fastest known minimizer. Its reported state counts
are summed over contracts and do not represent peak resident memory.

The graph compiler needs one restricted-cut query per witness, plus the shared
graph, action bank and budget. The dense capped-flow reference has the conservative
per-query bound O(n+m+(a+1)n^2), with O(n^2+n+m) working space, excluding its Python
cache. Decoder/native closure calls and source acquisition/storage are separate.
Its benefit over explicit expansion is a specialized implementation fact.

Do not use explicit expansion as the only strong baseline for efficiency novelty.
Classical cut/sensitivity algorithms work directly on G too. Further, dynamic
transitive-reduction algorithms already maintain reachability-preserving subgraphs
under graph changes. Their present-state objective is distinct from preserving
all bounded future failures, so runtime bounds are not automatically comparable;
they nevertheless prevent a claim that executable graph maintenance is new.

The surviving deliverable is a precise, source-backed, tractable graph realization
with independent replay checks. Promotion needs an independently delimited result
under equal encoded inputs and resources, or a substantive identification/natural
evidence result. The existing semantic definition and protocol checklist do not
meet that obligation alone.

## Primary sources inspected

- Giacobazzi, Ranzato and Scozzari, *Making Abstract Interpretations Complete*,
  JACM 47(2), 2000, Section 5.1, Definitions 5.1–5.2 and Theorem 5.3:
  https://www.sci.unich.it/~scozzari/paper/JACM00.pdf
- Ranzato and Tapparo, *Generalized Strong Preservation by Abstract Interpretation*,
  JLC 17(1), 2007; author preprint Sections 5–7:
  https://arxiv.org/abs/cs/0401016
- Amato and Scozzari, *Observational Completeness on Abstract Interpretation*,
  2011, Definitions 3.1–3.3, Theorem 3.3 and Section 4:
  https://www.sci.unich.it/~amato/papers/fi11.pdf
- Goranci, Karczmarz, Momeni and Parotsidis, *Fully Dynamic Algorithms for
  Transitive Reduction*, ICALP 2025, Theorems 1.1 and 2.1:
  https://arxiv.org/html/2504.18161v1
