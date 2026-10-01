# OACR takeover: proof scope and actual runtime status

Date: 2026-10-01 (Asia/Shanghai)
Baseline: `c10d23ca9c0d19fae97566ea15704b7a6b380308`, `MKLEE222/Multi-agent-systems`.
Sole acceptance gate: `OACR_FINAL_UPGRADE_ACCEPTANCE_GATE_2026-09-30.md` at that baseline.

## Verdict

The one-delta budgeted deletion construction survives this fresh-reading proof
audit under its stated assumptions. The prior finite audit was reproduced with
identical JSON content. This does not close the nontrivial theory/novelty gate.
Natural learned evidence remains absent from the inherited N1 run: it failed
during checkpoint loading before any factual edit or variant outcome.

This audit was performed by the same assistant, without a proof assistant or a
second reviewer. Neither rereading nor a different algorithm creates independent
human review, statistical replication, or prospective empirical authority.

## 1. General proof checked separately from finite enumeration

Fix a residual DAG `G`, deletion bank `A subset E(G)`, budget `0 <= h <= |A|`,
and candidate edges that preserve the original DAG topological order. Observe
full reachability at every legal prefix. A legal history deletes distinct base
edges and has length at most `h`; no state-dependent action legality is allowed.

**Activation.** A candidate `e=(u,v)` differs from the base at some allowed
prefix iff a set `F subset A`, `|F| <= h`, disconnects its endpoints in `G-F`.
This is precisely `lambda_A^G(e) <= h`. The empty set must be included: candidates
can already be nonredundant at a residual context.

**Distinct active candidates.** Suppose two distinct additions `e=(u,v)` and
`f=(a,b)` had equal full closures at a witnessing residual base `H` where `e`
is nonredundant. If `f` is redundant there, its closure is the base closure and
cannot equal the closure with `e`. Otherwise both are nonredundant. A path
from `u` to `v` in `H+f` must use `f`, so `u ->* a` and `b ->* v` in `H`.
Likewise `a ->* u` and `v ->* b` in `H`. Acyclicity forces `u=a` and `v=b`,
contradicting distinctness. Thus each active candidate is a singleton class;
inactive candidates share the base class.

**Decoder.** An inactive `e` is reachable in `G-F` for every allowed `F`.
Adding a reachability-redundant edge changes no reachability pair. Therefore
decoding bottom as `G` preserves the entire residual behavior. This is a
pointwise native statement, separate from equality of representation kernels.

**No resurrection.** If `lambda_A^G(e)>h`, delete a legal prefix `F`. A remaining
cut `J` of size at most `h-|F|` would imply an original allowed cut `F union J`
of size at most `h`, a contradiction. Consequently an updater receiving only
bottom and shared residual context need never reconstruct `e`. Stored active
edges can be retained or dropped by reevaluating their residual thresholds.

These arguments establish the commuting update by induction over legal histories.
They do not reset the horizon. The residual action set and budget are part of
the operational context, with storage and update costs of their own.

## 2. Cost and objective qualifications

The reference uses a dense residual-capacity matrix. Each augmenting BFS scans
at most `O(n^2)` entries; integer capacities and stopping at `|A|+1` bound the
number of augmentations by `|A|+1`. Thus a conservative bound per threshold
query is `O(n+m+(|A|+1)n^2)` time and `O(n^2+n+m)` space, ignoring Python object
overhead and memoization. Initial compilation over all candidates multiplies
the query cost by `|D|`. A stored active edge requires one threshold query per
update; bottom requires none. The updater still updates shared `G,A,h`.

Do not quote adjacency-list Edmonds-Karp complexity as the cost of this dense
implementation. Do not hide the separately bounded caches or count all nested
graphs/contracts as independent observations.

Exactness minimizes the number of distinct representation labels under this
finite contract. It does not prove that the literal two-endpoint encoding uses
the fewest physical bits, or that source acquisition, shared graph storage,
compilation and replay are free. A native decoder requires the shared base.
Initial compilation requires an available per-state edge witness. Increasing
the budget after real erasure can require reacquisition.

## 3. Explicit scope regressions

`experiments/oacr_theory/check_budget_boundaries_v1.py` uses bitset Warshall
reachability, separate from the inherited BFS verifier and flow constructor.

- Partial output: on `0->1->2->3`, deleting `(1,2)`, candidates `(0,2)` and
  `(0,3)` are distinct under full reachability but coincide if only `(0,3)`
  is observed. Retaining both identities still preserves outputs but is no
  longer quotient-exact. A restricted-output exact compiler is unresolved.
- Multi-delta: the already documented `(0,2)` versus `{(0,2),(0,3)}` witness
  has equal full behavior under this contract. Independent activity retains
  an unnecessary identity. This is a regression of an existing boundary.
- Expansion: the diamond erases `(0,3)` at budget one and needs it at budget
  two. Source-backed recompilation is required after the identity is lost.
- Maintenance: all ordered two-deletion histories on that diamond are checked,
  using only stored representation and residual context for online updates.

These are proof-debugging fixtures, not a new carrier, benchmark, or novelty claim.

## 4. Reproduction

Executed against the unchanged inherited source:

```sh
python experiments/oacr_theory/contract_budget_audit_v1.py --max-n 5 --out reproduced.json
python experiments/oacr_theory/check_budget_boundaries_v1.py --out boundaries.json
```

The first report matches the handoff report exactly as a JSON object:
182,104 exact quotient checks; 1,453,876 commuting squares; 6,234,453 decoder
checks; 6,234,453 residual checks; 72,364 min-cut comparisons; 256 factorization
cases; seven existing attacks. Reproduced report SHA-256:
`0c2f81705c97de343aa951e4ae222d2605cc58f358a8bf0cd13c92363c23287a`.

## 5. Inherited N1 failed before outcomes

Live run `36818820271`, source `16bcfc10e22c99e78954170a7a40a5cf4d419b45`:
prepare-dev succeeded; dev-smoke failed during `QAModel` initialization.
Transformers 4.20.1 passed a relative Hub resolve-cache URL to Requests,
which raised `MissingSchema`. Only the dev manifest artifact was present.
There is no smoke-result artifact and no scientific positive/negative verdict.

Source inspection found a second pre-outcome interface defect: auxiliary-key
capture invoked full T5 without decoder inputs. The registered layer lives
in the encoder, so the recovery invokes `get_encoder()` and guarantees hook
cleanup. An offline tiny-T5/official-GRACE check exercises editing, capture,
key insertion and restoration before benchmark execution.

Recovery stages the same `google/t5-small-ssm-nq` checkpoint at immutable
revision `4371c64b6f65176f6663af43066bd094597b1116`, confirmed by the failed
run URL and the model repository API. Hub 0.36.2 downloads the listed files;
legacy Transformers then loads from an absolute local directory with offline
mode set. Per-file hashes and model revision are recorded in the smoke output.
No model/editor substitution, sample change, hyperparameter change, or outcome
selection was made. Model snapshot hashes are provenance/integrity records,
not an independent publisher-signature certificate.

Local validation: syntax compilation, snapshot-corruption rejection, wrong
revision rejection, YAML parsing and diff checks. The tiny-T5/GRACE integration
test and actual eight-unit run require the cloud runtime; local checks alone
must not be reported as their success. A narrowly scoped push trigger on
`work/ocar-takeover-20261001` permits this isolated recovery execution.

Remaining scientific limitations are unchanged: accuracy is not quotient repair;
the A0 prompt-key heuristic is not an optimized oracle upper bound; unit-ID
separation is not cluster independence; matched intervention cost must be
checked on actual outputs. No automatic 512-unit evaluation unlock is permitted.

## 6. Load-bearing next gate

The budget extension cannot by itself establish independent novelty: min-cut,
finite observation equivalence and the union-of-prefix argument use classical
ingredients. A same-input nearest-neighbor reduction/comparison remains needed.
The earlier complete-core/shell work already treats both extension and restriction;
observational completeness directly treats observation-relative adequacy.

Primary anchors to recheck, not novelty clearance:
- Giacobazzi, Ranzato, Scozzari (2000), author-hosted paper:
  https://www.sci.unich.it/~scozzari/paper/JACM00.pdf
- Amato, Scozzari (2011), author-hosted paper:
  https://www.sci.unich.it/~amato/papers/fi11.pdf
- Hugging Face official checkpoint-download API:
  https://huggingface.co/docs/huggingface_hub/guides/download

The next main-track task is to compare explicit input availability, admissible
repair language, decoder/updater obligations and charged costs against the
strongest existing construction on the same mathematical input. Any surviving
contribution must identify a result that this reduction does not already give.
Until then, T2/T5 stay open and manuscript promotion remains blocked by the
upgrade gate, even if N1 runs successfully.
