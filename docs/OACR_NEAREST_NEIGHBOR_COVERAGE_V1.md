# OACR nearest-neighbor coverage audit v1

**Date:** 2026-09-28  
**Mother project:** Operational Adequacy of Computational Representations (OACR)  
**Purpose:** map mature theories onto OACR without treating every nearby result as a novelty threat.

## 1. Frozen mother question

> What makes a computational representation adequate for the observations and operations required by inquiry?

Working decomposition:

- READ — preservation of currently relevant consequences.
- PROBE — preservation of distinctions recoverable by admissible tests/interventions.
- WRITE — preservation of admissible future transformation behavior.
- COMPOSE — preservation of operation semantics across translations/compositions.
- COMPUTE — preservation of usability under resource bounds.

The audit classifies neighboring work as **INHERIT**, **EXTEND**, **SPECIAL CASE**, or **DIRECT COVERAGE**.

## 2. Coverage matrix

| Theory / literature | Core object already studied | OACR projection | Classification | What OACR should inherit |
|---|---|---|---|---|
| Computational adequacy / full abstraction / contextual equivalence | agreement between semantic and operational observations; equality under all program contexts | READ, COMPOSE | INHERIT | adequacy relative to an observation interface; contextual equivalence; preservation/reflection |
| Representation independence / abstract data types | different internal implementations are indistinguishable when exported operations preserve a representation relation | READ, WRITE, COMPOSE | INHERIT / EXTEND | operation-preserved relations, client-relative equivalence |
| Abstract interpretation / strong preservation | minimal refinement of an abstraction so formulas/operators are strongly preserved | READ, WRITE | INHERIT / EXTEND | property-relative adequacy, completeness, minimal refinement / complete shell |
| Bisimulation / coalgebra / behavioral equivalence | equality of future observable behavior under transitions | WRITE, PROBE | INHERIT | action-sensitive behavioral equivalence and quotient construction |
| SOS congruence formats | conditions under which bisimilarity is a congruence for system operators | WRITE, COMPOSE | INHERIT | the exact congruence question: does an equivalence survive admissible operations? |
| Testing equivalence / conformance testing / active automata learning | which experiments distinguish states and whether a learned transition model conforms | PROBE, WRITE | INHERIT / SPECIAL CASE | distinguishability by experiments, finite test families, counterexamples to equivalence |
| Dynamic epistemic logic / update expressivity | model-transforming actions and which model transformers an update language can express | WRITE | INHERIT / SPECIAL CASE | action semantics; update expressivity as a property distinct from static expressivity |
| Lenses / bidirectional transformations | get/put pairs and laws guaranteeing update propagation and consistency | WRITE, COMPOSE | INHERIT / SPECIAL CASE | update laws, round-trip laws, compositional update semantics |
| Knowledge compilation | representation languages compared by supported queries, supported transformations, and succinctness | READ, WRITE, COMPUTE | VERY CLOSE INHERIT / EXTEND | representation-relative query/transform capability maps; resource-aware support |
| Dynamic complexity | resources needed to maintain queries under a stream of updates | WRITE, COMPUTE | INHERIT / SPECIAL CASE | maintenance cost under updates; auxiliary state as operationally necessary memory |
| Control / reachability / approximate bisimulation | abstractions preserving reachable behavior and controller synthesis guarantees | WRITE, COMPUTE | INHERIT / SPECIAL CASE | reachability/viability and approximate behavioral equivalence |
| MDP state abstraction / bisimulation metrics | state aggregation preserving rewards, transitions, values, policies, or behavioral metrics | READ, WRITE, COMPUTE | INHERIT / EXTEND | task-relative state quotients and quantitative approximate equivalence |
| Causal abstraction / interchange interventions | whether a high-level representation preserves intervention-induced counterfactual behavior of a low-level neural system | PROBE, COMPOSE, learned-system bridge | VERY CLOSE INHERIT / EXTEND | intervention commutation diagrams; empirical validation of abstraction by interventions |
| Lifelong / sequential model editing | concrete learned writable carriers with retention, routing, memory, and update interference | WRITE carrier literature | SPECIAL CASE | realistic native write operators and failure mechanisms, not the mother theory |

## 3. Canonical sources checked

### Semantics, abstraction, and representation independence

- Abramsky, *Games, Full Abstraction and Full Completeness* (SEP): contextual equivalence, compositionality, computational adequacy, full abstraction.  
  https://plato.stanford.edu/entries/games-abstraction/
- Mitchell (POPL 1986), *Representation Independence and Data Abstraction*.  
  DOI: 10.1145/512644.512669
- Ahmed, Dreyer, Rossberg (POPL 2009), *State-Dependent Representation Independence*.  
  DOI: 10.1145/1480881.1480925
- Ranzato & Tapparo (ESOP 2004), *Strong Preservation as Completeness in Abstract Interpretation*.  
  DOI: 10.1007/978-3-540-24725-8_3

### Behavioral equivalence, testing, and congruence

- Groote & Vaandrager (Information and Computation 1992), *Structured Operational Semantics and Bisimulation as a Congruence*.  
  DOI: 10.1016/0890-5401(92)90013-6
- Sokolova (TCS 2011), *Probabilistic Systems Coalgebraically: A Survey*.  
  DOI: 10.1016/j.tcs.2011.05.008
- Abramsky (TCS 1987), *Observation Equivalence as a Testing Equivalence*.  
  DOI: 10.1016/0304-3975(87)90065-X
- Tretmans (1996), *Conformance Testing with Labelled Transition Systems: Implementation Relations and Test Generation*.
- Muškardin et al. (2022), *AALpy: an active automata learning library*.  
  DOI: 10.1007/s11334-022-00449-3

### Updates and composition

- Castañeda et al. (2023), *Comparing the Update Expressivity of Communication Patterns and Action Models*.  
  arXiv:2307.05057
- Foster et al. (TOPLAS 2007), *Combinators for Bidirectional Tree Transformations*.  
  DOI: 10.1145/1232420.1232424
- Foster et al. / Cheney et al. lens and bidirectional-programming literature: update propagation and well-behaved get/put laws.

### Operations plus computational cost

- Darwiche & Marquis, *A Knowledge Compilation Map*, JAIR 17 (2002), later arXiv:1106.1819. The map explicitly compares representation languages by succinctness and the queries/transformations they support in polynomial time.
- Patnaik & Immerman (JCSS 1997), *Dyn-FO: A Parallel, Dynamic Complexity Class*.  
  DOI: 10.1006/jcss.1997.1520
- Schwentick & Zeume (2016), *Dynamic Complexity: Recent Updates*.

### Control and learned representations

- Girard (Automatica 2012), *Controller Synthesis for Safety and Reachability via Approximate Bisimulation*.  
  DOI: 10.1016/j.automatica.2012.02.037
- Li, Walsh, Littman (2006), *Towards a Unified Theory of State Abstraction for MDPs*.
- Ferns, Panangaden, Precup (SIAM J. Comput. 2011), *Bisimulation Metrics for Continuous Markov Decision Processes*.  
  DOI: 10.1137/10080484X
- Geiger et al. (NeurIPS 2021), *Causal Abstractions of Neural Networks*.  
  arXiv:2106.02997
- Geiger et al. (ICML 2022), *Inducing Causal Structure for Interpretable Neural Networks*.  
  https://proceedings.mlr.press/v162/geiger22a.html

### Learned writable carriers

- GRACE (NeurIPS 2023): discrete key/value/radius lifelong editing.
- Sequential-edit degradation / lifelong-editing literature.
- DKME (ACL Findings 2026): addressing/storage coupling in lifelong editing.
- RippleEdits (TACL 2024): semantic ripple obligations after an edit.

## 4. Coverage conclusion

### 4.1 What is already mature

The following are not new in isolation:

1. equivalence relative to observations;
2. future-behavior equivalence;
3. congruence under operations;
4. minimal abstraction refinement needed for strong preservation;
5. update laws;
6. representation comparison by supported queries and transformations;
7. reachability-preserving abstraction;
8. intervention-preserving abstraction;
9. maintenance cost under repeated updates.

OACR must explicitly inherit these rather than rediscover them.

### 4.2 What this search did not find as a single existing object

No source in this audit was found that simultaneously treats a **computational representation** as adequate relative to a declared family of:

1. current observations,
2. active probes/interventions,
3. native writes / future transformations,
4. cross-representation composition,
5. resource-bounded computation,

and then studies the relationships and strict separations among these five adequacy notions for modern learned representations.

This is **not yet a novelty claim**. It is a coverage result from the present search pass. The closest foundations are distributed across full abstraction/representation independence, strong preservation, bisimulation/congruence, knowledge compilation, lenses, control/state abstraction, causal abstraction, and dynamic complexity.

## 5. Consequence for experiments

The first theory-led empirical question should not be “does edit history affect later edits?”

It should test a classical structural requirement in a learned writable carrier:

> **Is the equivalence induced by a declared current observation family a congruence of the system's native write operator? If not, what additional state distinctions are required to refine the quotient until the observed violations disappear?**

This directly motivates OACR-W1.
