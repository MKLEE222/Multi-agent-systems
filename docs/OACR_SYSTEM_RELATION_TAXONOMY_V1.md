# OACR System / Relation Taxonomy v1

**Date:** 2026-09-28  
**Status:** frozen working taxonomy for experiment selection  
**Mother project:** Operational Adequacy of Computational Representations (OACR)

## 1. Purpose

OACR is not restricted to neural model editing. A representation is operationally adequate only relative to the semantics of the system in which it participates.

For a system family (S), instantiate

[
mathcal S
=
(X,mathcal O,mathcal A,mathcal R,mathcal I,mathcal C),
]

where:

- (X): admissible system states;
- (mathcal O): declared observation/query family;
- (mathcal A): admissible state-changing operations;
- (mathcal R): relations whose semantics make the state meaningful;
- (mathcal I): invariants/obligations that legal operations should preserve;
- (mathcal C): computational/resource constraints.

A computational representation is

[
mathfrak R=(Z,ho,widehat{mathcal O},widehat{mathcal A},Phi,mathrm{Cost}).
]

The project asks which distinctions in (X) must survive through (ho) so that the relevant observations, operations, relations, invariants, and resource guarantees remain valid.

## 2. Three axes that must not be conflated

### 2.1 Candidate semantic dimensions

These are diagnostic dimensions, not an ontology and not labels to impose on a carrier. They are non-exclusive, non-exhaustive, and revisable. A relation receives one of these descriptions only after its native/registered operational semantics has been established.

1. **Extensional factual** — stored facts / tuples.
2. **Logical / entailment** — relations imply other relations through inference rules.
3. **Dependency / derivational** — a consequence may have one or more supports/justifications.
4. **Temporal** — truth or validity depends on time, interval, or version.
5. **Causal / interventional** — meaning is defined through intervention and counterfactual behavior.
6. **Procedural** — knowledge is a policy, program, workflow, or executable procedure.
7. **Probabilistic / uncertain** — relations carry likelihood, confidence, or epistemic uncertainty.
8. **Provenance / attribution** — origin, derivation, responsibility, and source identity matter.
9. **Normative / authority** — permissions, obligations, roles, delegation, and legitimacy matter.
10. **Identity / continuity** — persistence through copy, fork, merge, replacement, or lineage matters.

### 2.2 System form

1. relational database;
2. deductive database / Datalog system;
3. RDF/OWL knowledge graph;
4. temporal / versioned database;
5. event-sourced state machine;
6. version-control / branch-and-merge system;
7. replicated / CRDT system;
8. structural causal model;
9. parametric neural network;
10. external or routed neural memory;
11. retrieval-augmented system;
12. agent memory / tool-using agent;
13. multi-agent shared state;
14. institutional / provenance-aware knowledge system;
15. hybrid symbolic-neural representation.

### 2.3 Representation form

1. base facts only;
2. materialized consequences;
3. facts plus support counts;
4. facts plus full derivation/provenance polynomials;
5. graph topology;
6. temporal/event history;
7. checkpoints plus deltas;
8. distributed vectors;
9. model parameters;
10. key-value memories;
11. latent state plus external symbolic memory;
12. hybrid representations.

Operational adequacy is not expected to order these representations globally. Adequacy is contract-relative.

## 3. Relation-to-operation matrix

| Relation semantics | Native observations | Native writes | Characteristic invariant | Hidden distinction likely to matter |
|---|---|---|---|---|
| factual | lookup / selection | insert, delete, update | tuple correctness | existence / multiplicity |
| logical | entailment / query answering | assert, retract, revise | logical closure / consistency | rule support, alternative derivations |
| dependency | explanation / why query | invalidate, replace support | surviving justification | provenance / support multiplicity |
| temporal | time-slice / interval query | retroactive correction, append event | valid-time / transaction-time consistency | history and interval structure |
| causal | observational + interventional query | intervene, mechanism replacement | intervention semantics | causal graph / mechanism identity |
| procedural | execution / reachability | patch, compose, replace procedure | trace/property preservation | control state, latent branch structure |
| probabilistic | posterior / predictive query | evidence update, parameter update | calibration / coherent update | latent dependence structure |
| provenance | derivation / source / responsibility query | revise, invalidate, reattribute | derivation/attribution integrity | history, source identity |
| normative | permission / obligation / role query | grant, revoke, delegate | authorization / policy consistency | authority chain, scope, role |
| identity | continuity / lineage query | copy, fork, merge, rollback | identity/continuity conditions | history and ancestry |

## 4. OACR modules under different system semantics

### 4.1 Relational / deductive knowledge systems

- **READ:** current query answers and entailments.
- **PROBE:** distinguishing queries, explanation/why-provenance queries.
- **WRITE:** insert/delete/revise base facts and rules.
- **COMPOSE:** ontology alignment, view composition, graph merge.
- **COMPUTE:** query and maintenance complexity.

Key mature foundations:
- RDF/RDFS entailment regimes;
- OWL profiles and reasoning/complexity tradeoffs;
- truth maintenance systems;
- incremental materialized-view maintenance;
- provenance semirings.

### 4.2 Temporal / versioned / event-sourced systems

- **READ:** snapshot or historical query.
- **PROBE:** provenance/history queries.
- **WRITE:** append event, retroactive correction, commit.
- **COMPOSE:** branch, merge, replay, rollback.
- **COMPUTE:** incremental replay/maintenance cost.

Key hidden state:
- event order;
- transaction time versus valid time;
- branch ancestry;
- dependency between revisions.

### 4.3 Causal systems

- **READ:** observational distributions / predictions.
- **PROBE:** interventions and counterfactual probes.
- **WRITE:** intervention or mechanism replacement.
- **COMPOSE:** abstraction between causal levels, modular composition.
- **COMPUTE:** identification and inference complexity.

Key hidden distinction:
two systems can agree observationally while disagreeing interventionally.

### 4.4 Learned parametric representations

- **READ:** outputs, logits, generated behavior.
- **PROBE:** prompts, activation interventions, causal scrubbing/interchange.
- **WRITE:** gradient edits, parameter patches, fine-tuning.
- **COMPOSE:** merge, adapter composition, transfer.
- **COMPUTE:** inference/edit cost and identification cost.

Key hidden distinction:
parameter states can be read-equivalent on a declared family while responding differently to future updates.

### 4.5 Learned routed / external memory

- **READ:** model output after retrieval.
- **PROBE:** routing queries / memory inspection.
- **WRITE:** key/value insertion, radius/topology update, replacement.
- **COMPOSE:** memory merge, shard migration, retrieval translation.
- **COMPUTE:** routing and storage complexity.

Current OACR-W1 carrier: official GRACE + SCOTUS/BERT.

### 4.6 Provenance / institutional / authority-aware systems

- **READ:** accepted fact/practice plus attribution/authority state.
- **PROBE:** who supplied, derived, authorized, or delegated a statement/action.
- **WRITE:** assert, retract, reattribute, delegate, revoke.
- **COMPOSE:** transfer, merge institutions, fork authority, inherit roles.
- **COMPUTE:** provenance maintenance and policy checking.

W3C PROV gives explicit semantic objects for entities, activities, agents, derivation, attribution, association, role, and delegation. This is a concrete computational bridge toward the later OACR questions about provenance, authority, representation, and continuity.

## 5. Canonical theory support

### Logical / relational
- W3C RDF 1.1 Semantics: precise entailment regimes for RDF/RDFS.
- W3C OWL 2 profiles: explicit expressivity/computational tradeoffs.
- Jon Doyle (1979), *A Truth Maintenance System*: stores reasons/justifications so beliefs can be revised when assumptions change.
- Gupta, Mumick & Subrahmanian (SIGMOD 1993), *Maintaining Views Incrementally*: maintains derived views under insertions/deletions/updates and explicitly tracks alternative derivation counts.
- Green, Karvounarakis & Tannen (PODS 2007), *Provenance Semirings*: algebraic provenance for relational algebra and Datalog.

### Temporal / historical
- Özsoyoğlu & Snodgrass (TKDE 1995), *Temporal and Real-Time Databases: A Survey*: valid time, transaction time, temporal data models and query languages.
- Event sourcing: current state can be reconstructed from the full event sequence, so state and history are distinct representational objects.

### Causal
- Pearl's structural causal model tradition: causal meaning is tied to intervention, not observational association alone.
- Geiger et al. (2021), *Causal Abstractions of Neural Networks*: interchange interventions empirically test whether neural representations implement aligned high-level causal variables.

### Provenance / authority
- W3C PROV-O: Entity / Activity / Agent plus generation, use, derivation, attribution, association, roles, and delegation.

## 6. Carrier selection rule

OACR experiments must be selected by an **unresolved adequacy question plus native carrier semantics**, not by dataset availability and not by a desire to fill a pre-existing theory category.

A new carrier is justified when its native observation/write structure can test a materially new adequacy condition. The semantic dimensions above are retrospective comparison lenses, not experiment-generating labels.

### Current portfolio map

| Experiment | System form | Relation semantics | Native operation focus | Coverage role |
|---|---|---|---|---|
| OACR-W1 | learned routed memory | label/behavior + routing | key/value/radius write | learned writable state |
| OACR-R1 (next) | real relational knowledge graph | entailment + derivational support | edge deletion/retraction | exact relational semantics |
| Candidate H | to be selected from a real system | semantics to be recovered natively | history-sensitive operations if supported | tentative |
| Candidate C | to be selected from a real system | semantics to be recovered natively | interventions only if native/registered | tentative |
| Candidate I | to be selected from a real system | semantics to be recovered natively | authority/provenance operations only if supported | tentative |

## 7. First cross-system target: OACR-R1

The next carrier should deliberately differ from GRACE.

Use a **Wikidata-derived RDFS-style subclass graph**, exploiting documented Wikidata semantics for:

- `instance of (P31)`;
- `subclass of (P279)`;
- transitivity of subclass;
- propagation of instance membership through subclass.

The first experiment should not ask whether graph edits “hurt accuracy.” It should test whether a representation that preserves the complete current entailment relation is sufficient to preserve future retraction behavior.

The key configuration is:

[
TC(G)=TC(G-e)
]

for a redundant support edge (e), while for a shared later deletion (f),

[
TC(G-f)
eq TC(G-{e,f}).
]

Thus two graph states can be **fully equivalent under all current reachability/entailment reads over the finite carrier** while differing under the same future legal write.

This is an exact symbolic counterpart of OACR-W1's learned-state congruence audit.

## 8. Refinement hypothesis for OACR-R1

The closure-only abstraction

[
A_0(G)=TC(G)
]

may fail to be a congruence for edge deletion.

Candidate refinements:

- (A_1): closure + support multiplicity;
- (A_2): closure + minimal support sets / path provenance;
- (A_3): closure + full derivation provenance.

The experiment should report which refinement first separates every witnessed pair. This is explicitly connected to truth maintenance, incremental view maintenance, and provenance-semiring theory; those literatures are foundations and comparators, not novelty threats.

## 9. Boundary

This taxonomy does not assert that OACR has already unified all these system classes. It fixes the comparison interface and forces each future experiment to state:

1. what the system state means;
2. what observations count;
3. what operations are legal;
4. what relations carry semantic force;
5. what invariants must survive;
6. what computational constraints matter.

A carrier that cannot answer those six questions is not yet an OACR experiment.


## 10. Methodological constraint

Relation semantics are governed by `docs/OACR_RELATION_SEMANTICS_DISCIPLINE_V1.md`. The taxonomy is a comparison aid only. Nearest theories may suggest probes and refinements but may not define a carrier's semantics.
