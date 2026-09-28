# OACR Relation-Semantics Discipline v1

**Date:** 2026-09-28  
**Status:** frozen methodological constraint  
**Scope:** all OACR experiments that attribute semantics to relations, states, or operations

## 1. Core rule

OACR does **not** infer relation semantics from a relation name, a neighboring theory, or a convenient mathematical category.

Neighboring theories may provide:

- formal vocabulary;
- candidate invariants;
- candidate equivalence notions;
- probes and counterexamples;
- refinement constructions;
- known sufficient/necessary conditions.

They do **not** determine what a relation means in a target carrier.

The target carrier's semantics must be established from the carrier itself: its documented rules, executable operations, state transitions, constraints, and observable consequences.

## 2. Three levels that must remain separate

### L0 — syntactic relation

A token, edge type, field, label, parameter, memory slot, or other stored relation.

Examples: a P279 edge, a database foreign key, an attention connection, an authorization record.

L0 alone carries no OACR semantic claim.

### L1 — registered operational semantics

The exact semantics OACR registers for an experiment:

- what observations are admitted;
- what transformations are admitted;
- what consequences are computed;
- what invariants are checked;
- what context/history is included;
- what is explicitly excluded.

All experimental claims must be valid at least at L1.

### L2 — domain / native-system semantics

A stronger claim about what the relation means in the full real system or domain.

An L2 claim requires independent support from the system's authoritative specification, implementation, governance rules, or domain evidence. It may not be inferred merely because an L1 model resembles a familiar theory.

OACR experiments must not silently promote L1 results to L2 claims.

## 3. Native-first semantics workflow

For every new carrier:

1. **Recover the native state object.**  
   Identify what is actually stored or persisted.

2. **Recover the native observation interface.**  
   Determine what the system can actually reveal or answer.

3. **Recover the native operation family.**  
   Determine which writes, updates, interventions, merges, deletions, or transformations the system actually implements.

4. **Recover operational consequences.**  
   Determine how those operations change subsequent observations and legal operations.

5. **Register an experimental semantics.**  
   State exactly which subset of the native system is modeled and what is omitted.

6. **Only then map to theory.**  
   Compare the registered object with bisimulation, abstract interpretation, provenance, causal semantics, lenses, temporal logic, database maintenance, or other mature theories.

The order may not be reversed.

## 4. Relation semantics card

Every OACR carrier that uses a semantically meaningful relation must include a relation-semantics card with at least:

- carrier / system;
- relation token or state component;
- evidence for the relation's meaning;
- registered observation semantics;
- registered write semantics;
- registered consequence / propagation rules;
- context or history dependence;
- invariants / obligations;
- composition behavior if known;
- explicit exclusions;
- nearest theoretical analogues;
- whether each claim is L0, L1, or L2.

## 5. Anti-leading rule for nearest neighbors

A neighboring theory may suggest a question such as:

- is the relation transitive?
- does provenance matter under retraction?
- is observational equivalence a congruence?
- does intervention commute with abstraction?
- does merge preserve a declared invariant?

But the answer must be obtained from the carrier or from an explicitly registered abstraction of the carrier.

We do not select or redefine carrier semantics merely to instantiate a known theorem.

## 6. Anti-taxonomy rule

The current OACR categories such as factual, logical, temporal, causal, provenance, normative, identity, and procedural are **candidate semantic dimensions**, not an ontology of knowledge systems.

They are:

- non-exclusive;
- non-exhaustive;
- revisable;
- permitted to overlap;
- permitted to disappear if a carrier's native semantics does not support them.

A real relation may combine several dimensions or fit none cleanly.

## 7. Carrier-selection rule

New experiments are selected from an unresolved OACR adequacy question first, then from a carrier whose native semantics can test it.

Bad selection order:

theory category -> convenient carrier -> force interpretation.

Required selection order:

OACR question -> real carrier -> native semantics recovery -> registered experimental semantics -> theory comparison.

## 8. Current correction: OACR-R1

OACR-R1 must not be described as testing the full semantics of Wikidata P279 or the full semantics of RDFS.

Its registered L1 object is:

> a frozen graph derived from Wikidata P279 assertions, interpreted under an explicitly registered transitive-closure read semantics and explicit-edge deletion write semantics.

Therefore:

- the raw assertions are real carrier data;
- the registered transitive closure is the experiment's semantic model;
- SCC handling is an experimental graph-normalization rule;
- the added redundant edge is an experimental state construction;
- explicit-edge deletion is the registered write operator;
- qualifiers, ranks, references, Wikibase edit policy, and broader Wikidata semantics are outside v1.

The result may be compared with RDFS, truth maintenance, view maintenance, and provenance theory, but those theories do not define the empirical carrier.

## 9. Consequence for OACR

OACR seeks a cross-system adequacy framework without flattening heterogeneous systems into one semantics.

The shared object is not a universal relation ontology. The shared object is the disciplined question:

> Given this system's registered observations and operations, which representational distinctions are necessary to preserve the consequences that matter?

Cross-system generalization must therefore be demonstrated at the level of adequacy structure, not by assuming identical relation semantics across systems.
