# OACR Journal / Special-Issue Deep Dive — 2026-09-30

## Executive conclusion

For the current OACR manuscript, the financially safe journal strategy is:

1. **JLAMP subscription publication** — no author publication charge if the article is accepted under the subscription model.
2. **LMCS regular paper** — diamond open access; no author charges.
3. Treat the two currently listed JLAMP special issues as **eligibility-dependent**, not as ordinary open calls until guest editors confirm.

The special issues are:

- **Reconfigurable Transition Systems: Semantics, Logics and Applications** — deadline 30 Nov 2026; guest editors José Proença and Umberto Rivieccio.
- **Components Operationally: Reversibility and System Engineering** — deadline 31 Jan 2027; guest editor Claudio Antares Mezzina.

---

## 1. JLAMP publishing-cost status

JLAMP is an Elsevier hybrid journal.

Elsevier's current policy for hybrid journals is explicit:

- Gold OA requires an APC unless an institutional agreement covers it;
- subscription publication charges the reader/institution rather than the author;
- authors publishing under the subscription model can publish **at no cost**.

Therefore OACR can be submitted to JLAMP without committing to an APC.

The current OA list price is irrelevant to the zero-budget route because Gold OA is optional.

Practical rule:

[
oxed{
	ext{JLAMP subscription route} Rightarrow 	ext{author APC}=0.
}
]

Do not select Gold OA unless an institutional agreement explicitly covers it.

---

## 2. ReacTS 2025 JLAMP special issue

### Public ScienceDirect listing

Current ScienceDirect Calls for Papers lists:

**Special Issue on Reconfigurable Transition Systems: Semantics, Logics and Applications**

- Journal: JLAMP
- guest editors: José Proença; Umberto Rivieccio
- submission deadline: 30 Nov 2026

ScienceDirect also lists an item titled:

**JLAMP_ReacTS 2025**

with the same guest editors and same deadline.

### Provenance

The official ReacTS 2025 Call for Papers says:

> a selection of contributions will be invited to submit an extended version to a special issue.

The workshop accepted papers were already published through its LNCS workshop proceedings route.

This creates strong evidence that the current JLAMP call is a **selected-contribution / invited-extension issue associated with ReacTS 2025**, rather than an ordinary thematic call open to any original manuscript.

JLAMP's own special-issue policy distinguishes:

- thematic special issues;
- selected papers of symposia;
- invited contributions;
- festschriften.

The ReacTS evidence fits the selected-papers category.

### Eligibility verdict

[
oxed{
	extbf{Do not assume direct eligibility.}
}
]

Current status:

**LIKELY WORKSHOP-LINKED / INVITATION-DEPENDENT.**

A non-ReacTS-2025 original submission should be sent only if the guest editors explicitly confirm that external original manuscripts are accepted.

### Scientific fit if eligibility were confirmed

Fit is good but not exact.

ReacTS defines reconfigurable transition systems as relational structures whose accessibility relation, node set, or labels can change during execution. Its topics include:

- formal models for reconfigurable systems;
- dynamic logics;
- bisimulation;
- algebraic constructions;
- model checking;
- reactive systems/process algebra;
- AI applications.

OACR overlaps through:

- state-dependent continuation structure;
- fixed transition/interpreter semantics;
- representation objects controlling future operations;
- composition;
- bisimulation/strong-preservation ancestry.

However, OACR's scientific object is **representation adequacy and repair**, not a novel reconfigurable-transition-system formalism.

Fit score conditional on eligibility:

**moderate–strong**, but would require framing around continuation-interface reconfiguration rather than around generic representation methodology.

### Contacts

Official ReacTS 2025 contact:

- José Proença — jose.proenca@fc.up.pt
- Umberto Rivieccio — umberto@fsof.uned.es

---

## 3. Components Operationally: Reversibility and System Engineering

### Public ScienceDirect listing

Current ScienceDirect Calls for Papers lists:

**Components Operationally: Reversibility and System Engineering**

- Journal: JLAMP
- guest editor: Claudio Antares Mezzina
- submission deadline: 31 Jan 2027.

### Provenance

The title exactly matches:

**Components Operationally: Reversibility and System Engineering: Essays Dedicated to Jean-Bernard Stefani on the Occasion of His 65th Birthday**

published as LNCS volume 16065.

The underlying CORSE 2025 workshop was a DisCoTec 2025 satellite explicitly organized to celebrate Jean-Bernard Stefani's 65th birthday.

The Springer volume describes itself as a Festschrift and focuses on:

- reversibility;
- concurrency;
- operational semantics;
- process calculi;
- distributed/reactive systems;
- component-based software engineering;
- causal analysis.

JLAMP's special-issue policy explicitly recognizes **festschrift** as a distinct special-issue category.

### Eligibility verdict

The public ScienceDirect CFP confirms that the issue exists and has a submission deadline, but available public material does **not** explicitly say whether completely new authors outside CORSE/Festschrift invitees may submit.

Because the issue title exactly matches the existing CORSE/Festschrift and the guest editor is one of the Festschrift editors, the prior probability of an invitation/community-linked issue is high.

Current status:

[
oxed{
	extbf{ELIGIBILITY UNRESOLVED; ASK BEFORE WRITING TO THE SI.}
}
]

This is less conclusively closed than ReacTS because no public source found explicitly says "selected CORSE papers only."

### Scientific fit if open

This is the more interesting SI for OACR.

Strong overlaps:

- reversibility / rollback;
- operational semantics;
- causal/history-sensitive system behavior;
- system engineering;
- fixed operational semantics;
- restoration of present state vs restoration of future continuation;
- representation state needed to support reversible/adaptive behavior.

OACR's strongest bridge is not generic "reversibility" but:

[
	ext{restore/correct representation}

eq
	ext{change native semantics}
]

and the broader continuation claim:

[
	ext{present equivalence need not determine continuation equivalence}.
]

The newly accepted identity:

[
	ext{native-contract adequacy audit}
ightarrow
	ext{certificate-constrained bidirectional representation repair}
ightarrow
	ext{native closure verification}
]

can be made legible to this community through:

- operational semantics;
- state representation;
- history;
- reversibility;
- continuation closure.

### Main fit risk

The current OACR manuscript is broader than the CORSE/Festschrift core:

- graph/relational representation;
- Git history;
- learned parameter state;
- dynamic qualification.

If submitted here, the Introduction should foreground:

1. persistent state under reversible/state-changing operations;
2. operational semantics and continuation;
3. representation distinctions required for future operations;

and treat learned/Git carriers as validation substrates.

Do not foreground entropy metrics or cross-domain generality before the operational-semantics problem is established.

### Contact

Official University of Urbino contact:

- Claudio Antares Mezzina — claudio.mezzina@uniurb.it

---

## 4. JLAMP regular paper

If the special-issue eligibility answer is no, **JLAMP regular remains a legitimate target**.

JLAMP scope explicitly includes:

- theory and foundations;
- implementation issues;
- programming models;
- process calculi;
- quantitative methods for system analysis;
- specification and verification of systems;
- novel applications of logical/algebraic methods to trustworthy computing systems.

OACR currently contains:

- a formal adequacy object;
- directional information measures;
- representation repair operators;
- fixed interpreters;
- native execution;
- independent verification;
- multiple computational carriers.

Thus the paper does not need a special issue to be in JLAMP scope.

Main risk for regular JLAMP:

the current manuscript must make its **logical/formal method** more central than its empirical cross-domain breadth.

Recommended JLAMP-regular paper shape:

[
oxed{
	ext{formal audit object}
ightarrow
	ext{repair obligations}
ightarrow
	ext{two constructive substrates}
ightarrow
	ext{additional carrier validation}
}
]

rather than:

[
	ext{many domains}
ightarrow
	ext{common empirical pattern}.
]

---

## 5. LMCS regular fallback

LMCS is financially cleaner than every commercial-journal route:

[
oxed{
	ext{author fees}=0,quad
	ext{reader fees}=0.
}
]

The journal states explicitly:

- entirely open access;
- no page charges for authors;
- copyright retained by authors;
- CC-BY publication.

It accepts original research in theoretical and practical computer science involving logical methods broadly construed.

Relevant topic areas include:

- computer-aided verification;
- concurrency theory;
- coalgebraic methods;
- logic and verification;
- logics of programs;
- process algebra;
- program analysis;
- program development and specification;
- semantics of programming languages.

Submission constraints:

- manuscript must first be posted to CoRR/arXiv;
- it must include at least cs.LO;
- normal maximum is 50 pages;
- high acceptance standard, generally two or three referees.

### Fit verdict

[
oxed{
	extbf{LMCS is the safest zero-cost serious-journal fallback.}
}
]

But it has the strongest formal-expectation pressure.

For LMCS, the manuscript should foreground:

- finite full-support exactness proposition;
- contract-relative quotient;
- repair operator (Phi_{mathcal C,kappa});
- soundness theorem(s);
- bidirectional repair;
- fixed-interpreter/sham-control theorem-like result.

Empirical carriers should support the formal method, not substitute for it.

---

## 6. Decision matrix

| Route | Eligibility | Deadline | Author cost | Current OACR fit | Main risk |
|---|---|---:|---:|---|---|
| JLAMP ReacTS 2025 SI | probably invitation/selected-workshop linked | 30 Nov 2026 | $0 under subscription | moderate–strong if eligible | likely not eligible directly |
| JLAMP Components Operationally SI | unresolved; invitation/Festschrift linkage likely | 31 Jan 2027 | $0 under subscription | **strong if open** | eligibility + component/reversibility framing |
| JLAMP regular | open regular submission | rolling | $0 under subscription | **strong** | formal story must dominate cross-domain story |
| LMCS regular | open regular submission | rolling | **$0, diamond OA** | **strong with more formalization** | highest theorem/formal-method expectation |

---

## 7. Recommended strategy

### Step 1 — send two short presubmission eligibility inquiries

Do not send abstracts longer than ~150 words.

Question only:

1. whether an original manuscript not presented at the associated workshop/Festschrift event is eligible;
2. whether the described native-contract / reversible-continuation representation problem is within scope.

### Step 2 — do not pause manuscript construction

Write the manuscript in a **JLAMP-regular-compatible form** now.

That form can be adapted to Components Operationally if the editor says yes.

It also keeps LMCS viable if the formal layer is strengthened.

### Step 3 — decision after responses

If Components Operationally says **yes**:

- target that SI first;
- emphasize operational semantics, reversibility, continuation, system state representation;
- deadline 31 Jan 2027 gives adequate writing time.

If Components says **no** but ReacTS says **yes**:

- assess whether reconfigurable-transition framing is natural enough;
- do not force a new RTS formalism solely for the SI.

If both say **no**:

- choose between JLAMP regular and LMCS regular;
- no scientific work is lost.

---

## 8. Financial conclusion

The crucial financial result is independent of special-issue eligibility:

[
oxed{
	ext{JLAMP subscription publication can be $0 to the author.}
}
]

Elsevier explicitly states that authors in hybrid journals may publish under the subscription model at no cost.

LMCS is also:

[
oxed{
	ext{APC}=0
}
]

while remaining fully open access.

Therefore there is no financial reason to force the paper into a conference cycle.
