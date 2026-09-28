# OACR T1 — Mother-Level Theory Ledger v1

**Date:** 2026-09-28  
**Status:** first theorem-level novelty audit; hard gate for OACR claim freezing

## 1. Rule

Each OACR formal statement is classified as one of:

- **INHERITED** — mature theory already contains the mathematical result/object.
- **DIRECT REFORMULATION** — OACR changes notation/application domain but not the underlying theorem.
- **CANDIDATE EXTENSION** — the exact OACR object appears broader/different, but a proof and exhaustive coverage audit are still required.
- **DELETE AS NOVELTY** — may be used as background or a special case, but must not be presented as an OACR invention.

The purpose of this ledger is not to make OACR sound isolated from prior theory. It is to determine exactly what can be inherited and where a genuine contribution must live.

## 2. Myhill–Nerode / automata minimization

### Mature object
Histories/prefixes are equivalent when every possible continuation has the same acceptance consequence. The right-invariant equivalence classes induce the unique minimal DFA when the index is finite.

### OACR overlap
The deterministic finite-horizon object

[
zequiv_H z'
]

defined by equality of registered observations under all action sequences up to horizon (H) is a bounded continuation-equivalence construction.

### Classification
- continuation-induced state equivalence: **INHERITED**
- quotient/minimal-state intuition: **DELETE AS NOVELTY**
- horizon monotonicity under longer continuation sets: **DIRECT REFORMULATION**

### Surviving OACR question
OACR does not study recognition of one formal language. It studies whether an **implemented computational representation** is adequate for a registered family of state-changing native operations, legality/status semantics, observations, and eventually cost/composition. Whether this yields a genuinely new formal object rather than a product construction remains open.

## 3. Bisimulation / coalgebra / behavioral equivalence

### Mature object
Transition systems and coalgebras are compared by behavioral equivalence/bisimilarity; quotients identify states with the same observable behavior. Congruence questions ask whether an equivalence is preserved by operators.

### OACR overlap
The claim that current observation equality may fail under future transitions, and that a behavior-preserving quotient is required, is squarely inside this mature tradition.

### Classification
- behavioral equivalence: **INHERITED**
- congruence under operations: **INHERITED**
- partition refinement by successor behavior: **DELETE AS NOVELTY**

### Surviving OACR question
The candidate contribution is not a new bisimulation. It is a representation-adequacy framework that compares the partition actually encoded by a learned/symbolic/versioned representation with the partition required by a declared native-operation contract.

## 4. Computational mechanics / causal states

### Mature object
Causal states group past histories that induce the same conditional distribution over futures. They are minimal sufficient predictive states; the resulting (epsilon)-machine is a minimal optimal predictor.

### OACR overlap
The principle

[
	ext{future predictive behavior}
ightarrow
	ext{necessary state distinctions}
]

is already mature.

### Classification
- minimal sufficient predictive state: **INHERITED**
- “future behavior determines what must be remembered”: **DELETE AS NOVELTY**
- information content of a minimal predictive state: **INHERITED IN SPIRIT; exact OACR measure still requires derivation**

### Surviving OACR question
OACR includes explicit native **state-changing operations** whose effects may include legality, merge/revision status, persistent mutation, and cost. The relation between OACR operational contracts and causal-state constructions must be stated as a reduction/special-case theorem, not by rhetoric.

## 5. Epsilon-transducers / input–output computational mechanics

### Mature object
The (epsilon)-transducer extends causal-state ideas to stochastic input–output processes and gives an optimal model of a stochastic mapping conditioned on inputs.

### OACR overlap
An external action alphabet and future output behavior are already part of this theory. This is one of the strongest threats to any claim that OACR newly introduces “actions into predictive equivalence.”

### Classification
- action/input-conditioned predictive equivalence: **INHERITED**
- minimal input–output predictive state: **INHERITED**
- OACR action-horizon quotient as a general novelty: **DELETE AS NOVELTY**

### Surviving OACR question
OACR must distinguish **interventions that mutate the represented computational artifact itself** from ordinary exogenous inputs to a fixed stochastic channel, or else formally show that the distinction does real work. This is a **CANDIDATE EXTENSION**, not yet established.

## 6. Predictive State Representations (PSRs)

### Mature object
PSRs represent dynamical state using multi-step, action-conditional predictions of future observations; the 2001 formulation explicitly includes actions/controls and stochasticity.

### OACR overlap
Representing a state by the consequences of future action-observation tests is mature.

### Classification
- multi-step action-conditional predictive representation: **INHERITED**
- finite action-observation test signatures: **INHERITED**
- “operation horizon reveals hidden state distinctions”: **DIRECT REFORMULATION** unless OACR's mutation semantics yields a formal difference.

### Surviving OACR question
OACR evaluates existing representations as under-/over-refined relative to **native write contracts** and may include legality, status, persistent mutation, and representation cost. The novelty cannot be “predictive representation of state.”

## 7. State abstraction for MDPs

### Mature object
MDP abstraction/state aggregation studies which ground states may be combined while preserving rewards, transitions, values, policies, or related decision-relevant properties.

### OACR overlap
Task/contract-relative state aggregation and approximate abstraction are mature.

### Classification
- task-relative state abstraction: **INHERITED**
- approximate state aggregation as a general principle: **INHERITED**
- cross-system adequacy diagnosis of an implemented representation: **CANDIDATE EXTENSION / empirical framework**

### Surviving OACR question
OACR's target systems need not share an MDP reward/control semantics. The shared object is the adequacy comparison between an implemented representation and a native operation contract.

## 8. Strong preservation / complete shells in abstract interpretation

### Mature object
Strong preservation requires concrete and abstract models to agree on a specification language. Ranzato–Tapparo relate strong preservation to completeness and formulate minimal refinement to a strongly preserving abstraction; simulation/bisimulation can be characterized in this framework.

### OACR overlap
This is the strongest direct threat to the language of “under-refinement,” “minimal refinement,” and “coarsest adequate abstraction.”

### Classification
- minimal refinement for preservation of declared operators/properties: **INHERITED**
- coarsest strongly preserving partition/domain: **INHERITED**
- candidate-feature refinement until operational distinctions are preserved: **DIRECT REFORMULATION**
- using “complete shell” ideas as OACR theory without extension: **DELETE AS NOVELTY**

### Surviving OACR question
OACR must show what changes when the specification object is a family of **native mutating operations on computational representations**, with explicit legality/status/cost and heterogeneous carrier semantics. A formal translation to/from strong preservation is required.

## 9. Contextual equivalence / full abstraction

### Mature object
Programs are contextually equivalent when no admissible program context distinguishes them. Full abstraction asks for denotational equality to coincide with operational/contextual equivalence.

### OACR overlap
The distinction between internal representation equality and equality under all allowed contexts/operations is mature. Representation adequacy relative to an interface has a close full-abstraction flavor.

### Classification
- observer/context-relative equivalence: **INHERITED**
- equality of semantic and operational equivalences as an adequacy criterion: **INHERITED**
- OACR as “full abstraction for arbitrary representations”: **DELETE unless a precise reduction shows a different object**

### Surviving OACR question
OACR evaluates persistent data/model representations and their native writes, rather than only denotational models of programming languages. The value may lie in operationalization across representation systems, not a new full-abstraction theorem.

## 10. Representation independence / data refinement

### Mature object
Two implementations of an abstract data type can be contextually equivalent when a relation between their representations is preserved by exported operations. State-dependent representation independence extends this reasoning to mutable/stateful representations.

### OACR overlap
“Different internal states/implementations are interchangeable if their operation interface cannot distinguish them” is mature.

### Classification
- operation-preserved representation relation: **INHERITED**
- client/interface-relative representation independence: **INHERITED**
- state-dependent relation preserved by mutable operations: **INHERITED**

### Surviving OACR question
OACR's empirical under-/over-refinement audit of existing learned and data representations is not supplied by these theorems automatically. A framework contribution may remain, but the formal principle is inherited.

## 11. Knowledge compilation

### Mature object
Knowledge compilation compares representation languages by succinctness and by the queries and transformations they support efficiently.

### OACR overlap
READ/WRITE/COMPUTE as query/transform/cost dimensions already has a close antecedent here.

### Classification
- compare representations by supported queries and transformations: **INHERITED**
- include computational tractability/succinctness in adequacy: **INHERITED**
- extending this map to arbitrary mutable learned/native representations: **CANDIDATE EXTENSION / synthesis**, not yet a theorem.

## 12. Dynamic complexity

### Mature object
Dynamic complexity studies the resources needed to maintain query answers under updates, often with auxiliary state.

### OACR overlap
The idea that current answers may be insufficient to support efficient future updates and that auxiliary maintained state matters is mature.

### Classification
- update-aware auxiliary representation state: **INHERITED**
- resource-sensitive maintenance under writes: **INHERITED**
- OACR COMPUTE layer: must explicitly reduce to or distinguish itself from this literature.

## 13. Current survival table

| OACR candidate statement | Status after T1 v1 |
|---|---|
| Future behavior can distinguish currently equal states | DELETE AS NOVELTY |
| Behavioral equivalence induces a quotient | DELETE AS NOVELTY |
| A coarsest/minimal behavior-preserving abstraction exists in standard finite settings | INHERITED |
| Longer horizons / broader action families refine behavioral equivalence | DIRECT REFORMULATION |
| Minimal predictive state / sufficient state is defined by future consequences | INHERITED |
| Adequacy is relative to an observation/operation interface | INHERITED IN MULTIPLE TRADITIONS |
| Query/transform/cost jointly characterize representation usefulness | INHERITED FROM KNOWLEDGE COMPILATION / DYNAMIC COMPLEXITY |
| An implemented representation can be empirically diagnosed as under- or over-refined relative to a native operation contract | **CANDIDATE OACR FRAMEWORK CONTRIBUTION** |
| The same adequacy audit can be instantiated across learned, relational, and native versioned systems without imposing shared domain semantics | **CANDIDATE CROSS-SYSTEM CONTRIBUTION** |
| Native mutating-operation contracts with legality/status/cost require a formal object not reducible to input–output transducers / strong preservation | **OPEN — MUST PROVE OR RETRACT** |
| OACR can guide augmentation/compression of real representations | **OPEN EMPIRICAL CONTRIBUTION** |
| A cross-system law of operational information demand (I_H) is new | **OPEN — strongest theory/measurement target; requires T2 and experiments** |

## 14. Provisional novelty boundary

After this first pass, the project should **not** sell a new equivalence relation.

The most defensible surviving contribution target is:

> A theory-grounded and empirically operationalized framework for auditing **implemented computational representations** against their **native mutating operation contracts**, diagnosing under- and over-refinement across heterogeneous systems, measuring how representational demand changes as the contract expands, and using that diagnosis to redesign representations.

The formal novelty is not yet established. The next T2 task is to determine whether native mutation + legality/status/cost yields a genuine extension or can be encoded without loss in existing transducer/abstract-interpretation/full-abstraction machinery.

## 15. Canonical sources for this ledger

- Littman & Sutton, *Predictive Representations of State*, NeurIPS 2001.
- Ranzato & Tapparo, *Strong Preservation as Completeness in Abstract Interpretation*, ESOP 2004.
- Darwiche & Marquis, *A Knowledge Compilation Map*, JAIR 2002.
- Mitchell, *Representation Independence and Data Abstraction*, POPL 1986.
- Ahmed, Dreyer & Rossberg, *State-Dependent Representation Independence*, POPL 2009.
- Barnett & Crutchfield, *Computational Mechanics of Input–Output Processes: Structured Transformations and the epsilon-Transducer*, J. Stat. Phys. 2015.
- Li, Walsh & Littman, *Towards a Unified Theory of State Abstraction for MDPs*, 2006.
- Standard full-abstraction/contextual-equivalence and coalgebraic behavioral-equivalence literature.

**T1 v1 conclusion:** the mother problem survives as a potentially valuable **representation-adequacy synthesis and empirical/design program**, but several apparent mathematical novelties are already mature. T2 must now focus only on the surviving extension points.
