# R1a carrier proposition — structural certificates for GRACE selective writes

**Status:** carrier-level result for the registered GRACE-style native write program.  
**Not:** a theorem about arbitrary model editors or representation-level impossibility.

## 1. Carrier state and retrieval

Let the persistent routed-memory state be

\[
z=(K,V,\varepsilon,L),
\]

with keys \(K=(k_i)\), values \(V=(v_i)\), radii \(\varepsilon=(\varepsilon_i)\), and stored labels \(L\).
For query \(q\), define the nearest key

\[
r_z(q)=\arg\min_i d(q,k_i)
\]

and coverage indicator

\[
c_z(q)=\mathbf 1\{d(q,k_{r_z(q)})\le \varepsilon_{r_z(q)}\}.
\]

The GRACE adapter returns the stored value \(v_{r_z(q)}\) when \(c_z(q)=1\); otherwise it falls through to the frozen base-layer output.

A native future write \(\tau=(q_\tau,y_\tau)\) first performs one deterministic structural update

\[
z\mapsto \Psi_\tau(z),
\]

which may add a key, split a radius, expand a radius, or reuse existing topology. After iteration 0, the registered program leaves keys and radii fixed and optimizes one value row, denoted \(t_z(\tau)\).

For a protected obligation \(o=(q_o,y_o)\), write its retrieval signature as

\[
\sigma_z(o)=\big(r_z(q_o),c_z(q_o)\big).
\]

## 2. Structural failure certificate

### Proposition 1 — support-loss forces protected failure

Suppose a protected obligation \(o=(q_o,y_o)\) satisfies:

1. \(o\) is currently satisfied in state \(z\);
2. it is retrieval-covered before the future write:
   \[
   c_z(q_o)=1;
   \]
3. after GRACE's exact iteration-0 structural projection it is uncovered:
   \[
   c_{\Psi_\tau(z)}(q_o)=0;
   \]
4. the frozen no-retrieval/base fallback is incorrect on \(o\):
   \[
   \hat y_{\mathrm{base}}(q_o)\ne y_o.
   \]

Then \(o\) is false after the structural step and remains false throughout all later value-optimization iterations of this registered native write.

### Proof sketch

After iteration 0, GRACE does not modify \(K\) or \(\varepsilon\). Hence the protected query remains uncovered. An uncovered query never consumes any stored value row, so later optimization of \(t_z(\tau)\) cannot affect its adapter output. The base network is frozen. Its fallback prediction is incorrect by assumption. Therefore the protected obligation cannot be restored by any number of later value-optimization steps within this native write execution. \(\square\)

For protected set \(P\), define

\[
H_P(z,\tau)
=
\{o\in P:c_z(q_o)=1,\ c_{\Psi_\tau(z)}(q_o)=0\}.
\]

Any base-wrong member of \(H_P(z,\tau)\) is thus an exact carrier-level obstruction to selective preservation for that native write.

## 3. Structural preservation certificate

### Proposition 2 — route/value-row separation certifies preservation

Suppose for every protected obligation \(o\in P\):

1. its retrieval signature is unchanged by the structural projection:
   \[
   \sigma_z(o)=\sigma_{\Psi_\tau(z)}(o);
   \]
2. if it is covered, its selected value row is not the row optimized by the future write:
   \[
   r_{\Psi_\tau(z)}(q_o)\ne t_z(\tau).
   \]

Then every protected adapter output is invariant throughout all later value-optimization iterations of the registered GRACE write. Consequently, if all protected obligations are correct before the write, they remain correct during and after that future write.

### Proof sketch

The structural projection leaves each protected query on the same covered/uncovered branch and, when covered, on the same value row. Later iterations leave keys/radii fixed. By assumption the only value row being optimized is not selected by any protected query. All quantities consumed by each protected query therefore remain fixed. \(\square\)

This is stronger than merely observing no protected failure after optimization: it gives a carrier-native reason why no protected failure can occur along the registered value-training trajectory.

## 4. Read-matched selective-write separation

Let \(z\) and \(z'\) be persistent states before and after a committed anchor write. Suppose:

\[
F_{\mathrm{read}}(z)=F_{\mathrm{read}}(z')
\]

on the frozen non-anchor current-read family and on the future candidate itself.

For a future write \(\tau\), suppose:

- \(z\) has a Proposition-1 failure certificate for some protected obligation;
- \(z'\) has a Proposition-2 preservation certificate for the whole protected set;
- the future target is realized in both branches under the same registered write program.

Then the two persistent states are current-read matched for the declared family but differ in selective future WRITE behavior:

\[
W(z,\tau\mid P)=0,
\qquad
W(z',\tau\mid P)=1.
\]

The separation is therefore not reducible to current target accuracy, current protected accuracy, branch RNG, or whether the future target itself is reachable.

## 5. Mapping to the six current strict witnesses

| seed | anchor -> future | pre native mode | post native mode | pre forced-loss obligation | post preservation certificate |
|---|---|---|---|---:|---|
| 211 | 905 -> 784 | add_conflict_split | expand_same_label | 2 | yes |
| 211 | 1582 -> 480 | add_conflict_split | add_far | 2 | yes |
| 211 | 1552 -> 480 | add_conflict_split | add_far | 2 | yes |
| 907 | 5 -> 1658 | add_conflict_split | add_conflict_split on a different nearest key | 2 | yes |
| 907 | 5 -> 37 | add_conflict_split | add_far | 2 | yes |
| 2503 | 489 -> 1197 | add_conflict_split | add_far | 2 | yes |

The affected obligation is base-wrong in every witness:

- seed 211: obligation index 2 is dataset item 1765, true class 3, base prediction 5;
- seed 907: obligation index 2 is dataset item 643, true class 8, base prediction 1;
- seed 2503: obligation index 2 is dataset item 69, true class 9, base prediction 7.

For all six post branches, the protected retrieval signatures are structurally invariant and no protected query uses the value row optimized by the future write.

## 6. Prospective use

The official GRACE+SCOTUS protocol should therefore predict future selective divergence before future execution by checking:

1. anchor succeeds and preserves fixed obligations;
2. current candidate and protected READ signatures match pre/post;
3. pre branch has at least one support-loss obligation whose retrieval-disabled fallback is wrong;
4. post branch satisfies the route/value-row preservation certificate.

The future-write execution then tests the remaining empirical condition: whether the target is realized in both branches. Prediction and execution must remain separate files/stages.

## 7. Scope boundary

These propositions exploit exact properties of the registered GRACE native program: nearest-key routing, epsilon coverage, deterministic iteration-0 topology update, frozen topology thereafter, and single selected-value optimization. They should not be presented as general WRITE theorems. Their role is to show how the broader WRITE object can admit carrier-specific certificates rather than being evaluated only by aggregate sequential-edit accuracy.