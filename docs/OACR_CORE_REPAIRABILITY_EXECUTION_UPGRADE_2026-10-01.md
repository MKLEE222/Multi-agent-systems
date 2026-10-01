# OACR core upgrade: available information, executable repair, residual contracts

Date: 2026-10-01
Status: WORKING PROOF + EXECUTED SYNTHETIC AUDIT. Novelty and manuscript promotion remain OPEN.

## Decision

The existing GRACE/RippleEdits dev smoke is an ancillary learned branch, not a
prerequisite for core development and not evidence that the central representation
claim has been established. Do not change its running head retrospectively.
Do not unlock the 512-unit evaluation bank based on a smoke success.
Existing frozen graph measurements are not retracted or newly reverified here.

This audit replaces the previous optimism about a nearly closed theory gate with
specific proof obligations. Finding that several ingredients have different names
from prior work is not a novelty proof; neither is their conjunction.

## 1. Seven concrete attacks

### A1. A coarse representation cannot recover erased state identity

The existing one-delta note defines R_coarse(x) as constant and describes adding
active-delta identities to it. The static graph quotient theorem can be correct
while an online-repair reading of this arrow is false.

Let Q(x) denote the target contract class and Z(x) the complete authorized view
available at the moment of repair. For unrestricted finite deterministic encoders,

    exists g with ker(g o Z) = ker(Q)
    iff Z(x)=Z(y) implies Q(x)=Q(y).

Necessity: equal inputs to g have equal outputs. Sufficiency: define g on each
Z-fiber by its unique Q label. Sufficiency assumes arbitrary encodings and does
NOT prove an efficient or allowed constructor, a native decoder, or cross-instance
uniform learnability.

In particular, two states with R_coarse(x)=R_coarse(y) and Q(x)!=Q(y) cannot be
repaired from R_coarse and a shared contract alone. Access to the candidate
universe D does not identify which candidate belongs to the current state.

The correct executable arrow is

    (R_coarse(x), W(x), public contract) -> repaired representation,

where W is an explicitly available statewise source witness: original assertions,
retained log, external evidence, or paid reacquisition. If W is the entire raw
state, describe the operation as source-backed recompilation, not recovery of
information from an already lossy stored state.

A fixed-length supplementary witness needs at least

    ceil(log2(max_r |{Q(x): R(x)=r}|))

bits in the unrestricted finite encoding problem. This is an elementary
information bound, not new information theory. Physical storage, acquisition cost,
and computational complexity require separate accounting.

### A2. Exact partitions do not certify a native decoder

A two-state encoder can have U=E=0 while its decoder swaps the states and gets
both native outcomes wrong. Therefore require TWO tests:

    ker(Enc) = ker(B_C),
    B_C(Dec(Enc(x))) = B_C(x).

The graph replay results already contain useful evidence for the second test.
The general working specification must not silently identify the two tests.

### A3. There are four cases, not three

Crossing representation and target partitions can have U>0 AND E>0. Example:
R=(0,0,1,1), Q=(0,1,0,1) gives U=E=1 bit under uniform weights.
The comparable coarse/exact/fine chain is a special case, not a complete taxonomy.
Extra distinctions are contract-relative excess; they become a practical defect
only under an explicit cost, privacy, interference, or canonicality objective.

### A4. Finite-horizon equivalence is not a reusable stationary state

For a deterministic transition T, H-step equality generally yields equality of
successor behavior for H-1 remaining steps, not a fresh H steps.
A six-state counterexample with two initially indistinguishable chains exposes
this failure at depth two. A maintained representation needs residual contract
state (including remaining horizon and action legality), or a stronger congruence
proof on a transition-closed domain.

### A5. Accuracy improvement is not quotient repair

The inspected N1 runner reports mean_future_accuracy after one edit and additional
keys. It does not compute a representation kernel or a common native behavior
partition over a state bank. Equal aggregate accuracy can hide different behavior
vectors. Improved task accuracy can also intentionally CHANGE original native
behavior instead of preserving it.

Treat the current smoke as a task-performance/intervention feasibility branch.
Any later quotient claim needs a declared reference behavior, state bank,
representation map, common comparison panel, decoder, and native replay.

### A6. Freezing choices does not rule out exhaustive answer computation

A frozen deterministic simulator can recompute the entire target partition from
allowed raw inputs without reading a stored evaluation-output file. It satisfies
a no-adaptive-feedback rule but does not thereby demonstrate a new representation
principle or an efficient constructor.

Track separate dimensions:
- provenance/freshness of rule choices;
- actual available information at construction and deployment;
- oracle calls, simulation and computational cost;
- semantic correctness and objective value.

An outcome-aware verified synthesis algorithm is not scientifically worthless.
It simply does not establish outcome-independent discovery on those same data.
An A0 branch that merely adds two test-prompt keys is not an optimized oracle
upper bound; its failure cannot prove the representation family insufficient.

### A7. Safe forgetting under one contract may block later expansion

A four-node diamond has two edge-disjoint paths from a to d. The redundant delta
(a,d) is invisible under every single base-edge deletion, but becomes essential
under a registered two-edge deletion. Once its identity has really been discarded,
expanding the contract cannot recreate that identity without a statewise witness.

Thus identical FINAL contracts give the same source-backed canonical encoder, but
NOT automatically a reversible online update path after destructive compression.
The earlier path-independence claim needs this availability qualification.

## 2. Constructive upgrade: budgeted native deletion contracts

This extension stays inside the one-delta DAG class and does not claim to solve
multi-delta interaction. It strengthens a single-deletion replay result into an
executable residual-contract result.

### Setup

Let G0=(V,E0) be a DAG and D a set of distinct candidate edges in TC(G0) minus E0.
Each state is G0 or G0+e for exactly one e in D. The deletion alphabet A is a
subset of E0; candidate edges are never deletion targets. The contract allows
all sequences of distinct deletions from A of length at most h, and observes full
reachability including the present state. All histories are legal in the same way
for all candidate states. Repeated deletions, adaptive legality, partial outputs,
stochastic execution and multi-delta states are outside this theorem.

At a residual context, the shared base is G, remaining action set is A, and
remaining budget is h. A candidate e may now be nonredundant. Define

    lambda_A^G(u,v) = min{|F|: F subset A, (u,v) not in TC(G-F)},

with infinity if there is no such F, and zero if reachability is already absent.

### Proposition B1: exact activation threshold

    e is distinguishable from the base under the residual contract
    iff lambda_A^G(e) <= h.

This is immediate from the allowed deletion family. The nontrivial connection
needed for the quotient is the earlier one-edge DAG injectivity lemma: at any
witness F, two distinct nonredundant additions to G-F have different transitive
closures. If the other edge is redundant there, it instead has the base outcome.
Hence all active states are singletons, while all inactive states join the base.

Therefore

    O_(A,h) = {base + inactive states} union {one block per active delta},
    |O_(A,h)| = 1 + |{e in D: lambda_A^G(e) <= h}|.

### Construction without augmented-state outcome enumeration

Give every edge in A capacity 1 and every other base edge capacity |A|+1. A
minimum u-v cut below |A|+1 is exactly a permitted deletion cut; a larger cut
means no allowed subset suffices. Max-flow/min-cut is classical infrastructure.
The reference compiler invokes this computation per candidate, rather than
building the augmented-state outcome matrix over all deletion subsets.

The number of possible final deletion sets is sum_{j=0}^h binomial(|A|,j).
Deletion order does not affect a final graph; the family of permitted prefixes is
also covered. Do not count commutative permutations as independent evidence.
No claim of superiority over mature fault-tolerance algorithms is established.

### Encoder and decoder

For an available statewise delta witness e:

    Enc_(G,A,h)(e) = e if lambda_A^G(e)<=h, otherwise bottom;
    Dec_G(bottom) = G;
    Dec_G(e) = G+e.

By B1 and injectivity, the encoder realizes the exact quotient. If an edge is
omitted, it is redundant after EVERY allowed remaining deletion set, so the native
decoder preserves the entire residual behavior. These are separate conclusions.
Initialization requires the per-state edge witness. This is NOT coarse-only
information recovery.

### Proposition B2: no resurrection while the budget is consumed

Suppose e is omitted at budget h, i.e. lambda_A^G(e)>h, and a legal prefix deletes
F with |F|<=h. Then

    lambda_(A-F)^(G-F)(e) > h-|F|.

Proof: otherwise a remaining cut J of size at most h-|F| would make F union J an
allowed cut of size at most h in the original context, a contradiction.

Thus a forgotten delta never becomes necessary within the ORIGINAL remaining
budget. This is the key maintenance guarantee, not merely a static quotient.

### Corollary: executable commuting update

For a legal deletion f, update the shared context to (G-f,A-{f},h-1). If the stored
representation is bottom, leave it bottom. If it stores e, reevaluate the threshold
and either retain or drop e. The updater sees ONLY stored representation and
shared context, not the original erased witness. B2 proves

    Update_f(Enc_(G,A,h)(x)) = Enc_(G-f,A-f,h-1)(T_f(x))

in the natural representation coordinates. By induction, every permitted history
is executable and behavior-preserving after compression.

### Boundary: expansion differs from consumption

Increasing h or adding new permitted actions need not preserve B2. The diamond
counterexample forces reacquisition. Therefore the object has a meaningful
operational asymmetry: safely coarsening a consumed contract can be irreversible
when future obligations expand. Bidirectional design does not imply reversible
online execution.

## 3. Executed proof debugging

The dependency-free reference script uses Edmonds-Karp for construction and a
separate BFS/failure-enumeration path for verification. Both implementations were
written in this audit; this is not an independent human or prover review.

Complete enumeration through five topologically labelled vertices:
- 1,098 DAGs enumerated; 692 have candidate redundant edges;
- 42,284 graph/action-bank configurations (including empty action banks);
- 72,364 restricted min-cut versus brute-force endpoint checks;
- 182,104 graph/action-bank/budget contracts; every predicted quotient matched;
- 1,453,876 one-step commuting update checks;
- 6,234,453 state/failure decoder-replay checks;
- 6,234,453 residual no-resurrection checks;
- 256 small view/target factorization cases;
- seven explicit failure demonstrations.

All passed. Counts reuse graphs, candidates and nested contracts; NONE are
independent natural systems or statistical samples. This verifies implementation
examples and searches for small countermodels, not the general proof or novelty.

## 4. Immediate acceptance changes

- Suspend unrestricted coarse-only additive repair and reversible contract-change
  claims until source-witness availability and acquisition cost are explicit.
- Preserve the original static one-delta exactness result with its actual scope.
- Reopen T5. Source-level work from 1997/2000 already gives complete extensions
  AND restrictions, and observational completeness is directly adjacent.
- Preserve I5 as an executable demonstration, not proof of independent novelty.
- Treat current N1 smoke as ancillary task-performance feasibility. Its success
  cannot automatically promote U/E claims or unlock held-out evaluation.
- Promote this budget extension only as a WORKING theorem/algorithm candidate.
  Require a cold proof audit, same-input prior-art comparison, restricted-output
  and multi-delta boundaries, and cost accounting before publication claims.

## 5. Prior-art anchors (not a novelty clearance)

Giacobazzi, Ranzato, Scozzari. Making Abstract Interpretations Complete. JACM
47(2):361-416, 2000. DOI 10.1145/333979.333989. Constructive complete extensions
and restrictions already exist under their stated assumptions.

Ranzato, Tapparo. Generalized Strong Preservation by Abstract Interpretation.
Journal of Logic and Computation 17(1):157-197, 2007.
DOI 10.1093/logcom/exl035. Semantics-relative equivalences and refinement are
established; OACR must not claim these notions alone.

Amato, Scozzari. Observational Completeness on Abstract Interpretation.
Fundamenta Informaticae 106(2-4):149-173, 2011. DOI 10.3233/FI-2011-381.
The observation-relative completeness framework is a required stronger neighbor.

Angluin. Learning Regular Sets from Queries and Counterexamples. Information and
Computation 75(2):87-106, 1987. DOI 10.1016/0890-5401(87)90052-6.
Treat automata/observation-table consistency as established background, not a new
name for the residual-contract issue.

Max-flow/min-cut and failure-sensitive reachability are classical. This audit's
candidate contribution must be assessed at the executable representation and
information-availability level, NOT at the min-cut lemma level.
