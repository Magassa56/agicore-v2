# AGIcoreManager V2: bounded synthetic mission

This is a local Linux engineering candidate. It runs fixed Python producer and
verifier adapters via the existing `AgentOrchestrator` and `Dispatcher`; it does
not call Terra, Sol, Astra or any other model API.

With the project dependencies installed, run one invented confirmation profile
into a new absolute directory whose parent already exists:

```sh
PYTHONPATH=src:. python -m agicore.manager.mission_cycle_v2 \
  --output-dir /tmp/agicore-mission-long \
  --observations 39 --stage confirmation --profile confirmation-long-v1
```

Use `confirmation-short-v1` for the second fixed 39-row profile. Other stages
use the `standard` generator; the default count is 64, and a larger count must
be requested explicitly. Confirmation stops at the first qualified signal,
before risk or any position, and distinguishes input rows from processed rows.
No external market input, broker, order or profit calculation is accepted by
these mission adapters.

To continue a fresh mission only as far as the frozen structural stop, use a
separate new directory and `--stage stop` with either fixed confirmation profile
and exactly 39 observations. The receipt records the complete input hash, the
indices and exact-row hash for the pullback-through-confirmation window, the
native confirmation and stop. No entry, position or target is created. The verifier
regenerates the profile, validates stored chunks, rebuilds the confirmation and
its window in a separate process, and calls the same frozen stop predicate.
The input is parsed in full before the causal decision loop; malformed later
rows can therefore reject the input, even though later valid prices cannot
change the already-confirmed stop.

For an interrupted mission, use its existing directory and no overrides:

```sh
PYTHONPATH=src:. python -m agicore.manager.mission_cycle_v2 \
  --output-dir /tmp/agicore-mission-long --resume
```

Resume rechecks the contract, source snapshot, selected runtime versions,
completed task checkpoints, bundle, receipts, process logs and events. It
refuses running, failed, ambiguous, altered or old unsealed missions; it never
relaunches an uncertain task. Preserve the directory for review on refusal.
Completed evidence and the final report are not overwritten.

`mission.json`, `report.json`, `events.jsonl`, `orchestrator.sqlite3`, the
per-process outputs and `bundle/` form the local evidence. The Manager records
resource usage measured by `wait4`; worker-reported timings are not independent
measurements. The verifier independently reconstructs storage and control flow,
but shares the fixed generator and V2 predicates with the producer.

The fingerprints provide relative local integrity, not a signature against
someone able to rewrite both the evidence and its anchors. External packages
are checked by version, not by wheel bytes. The Linux limits and parent-death
signal cover the trusted direct child; they are not a network sandbox and do
not supervise arbitrary grandchildren. The synchronous supervisor must remain
single-threaded while launching children. Human review and approval remain
required before merge, publication or deployment.

The historical `engineering_mission.py` Codex contract and its original evidence
package were not recovered from the accessible locations. This implementation
must not be represented as a recovered copy of that contract.
