# N1 observer-only retrospective replay

Freeze date: 2026-10-01, before observing routing telemetry.
Authority: retrospective development diagnosis of run 36824729008.

Reference JSON SHA-256: `6d8267b2da83c30ba871cc02c34b97d6f858b0b6661611cf63d7be369c6a19c3`.
Inherited runner SHA-256: `928aa6434bc4b31fa2e011f15f2d0e1be05fe7a7e04b37df0332941d0b98e91b`.

Replay uses the same eight units, same unit/variant/query order, official GRACE
source, checkpoint revision, seed, CPU, 100 edit steps, radius and two-key budget.
No constructor output is changed. Hooks read codebook and encoder activation
state; telemetry arithmetic consumes no random draws. A synthetic integration
fixture must match native logits, RNG and stored codebook, and detect an auxiliary
route. Real replay must match the reference summary and every complete unit record.
If that check fails, telemetry is not interpreted as a localization of the
recorded failure. Differences remain diagnostic engineering failures.

For every future query/variant, record nearest key, distance, radius, gate result,
auxiliary-key activation and the layer output difference against its original
linear output. Record whether all stored values are copies of the base value.
No inference of an optimized oracle ceiling or representation-family impossibility
is allowed. Additional arithmetic is charged to diagnosis, not constructor cost.

Registered interpretations:
- zero auxiliary activation and zero layer-output difference: this constructor
  does not reach these future queries at the registered radius;
- auxiliary activation with layer-output difference but no answer improvement:
  activation alone does not validate the copied value or semantic target;
- successful A0 routing with poor correctness: the weak test-prompt heuristic
  demonstrates controllability, not an optimized upper bound;
- a replay mismatch: preserve and investigate before using routing statistics.

The 512-unit evaluation bank remains sealed. This replay cannot create fresh
confirmatory authority. Any constructor modification starts a separate dev round.
