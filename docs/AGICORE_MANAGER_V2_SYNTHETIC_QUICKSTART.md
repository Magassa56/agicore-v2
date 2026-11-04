# AGIcoreManager V2: Bounded Synthetic Mission Quickstart

This is a local Linux engineering candidate. It runs fixed Python producer and
verifier adapters via the existing `AgentOrchestrator` and `Dispatcher`; it does
not call Terra, Sol, Astra or any remote model API.

All runs operate strictly in-memory on deterministic synthetic fixtures with
zero broker connection, zero real orders, zero account mutations, and zero PnL
claims.

---

## 1. Architecture of the Synthetic Cycle

The deterministic synthetic pipeline is strictly causal and partitioned into distinct stages:

```
[Signal Analysis Stages]
  ├── confirmation : Impulse, pullback & first causal confirmation (bar q)
  ├── stop         : Structural stop calculation anchored to window [k, q]
  └── risk         : Position sizing & risk gate evaluation (APPROVE / REJECT)

[Simulated Execution Stages]
  ├── entry        : Simulated next-bar Open market fill (bar e = q + 1)
  └── exit         : Simulated structural stop fill or next-open EMA20 market fill
```

### Signal Analysis Stages (`confirmation`, `stop`, `risk`)
- **`--stage confirmation`**: Identifies the impulse, pullback, and the first qualified confirmation signal at bar index $q$. Evaluation stops immediately upon qualification. No stop, risk decision, entry, or position is generated.
- **`--stage stop`**: Reconstructs the confirmation window $[k, q]$ and evaluates the frozen initial structural stop level. Stops before any risk evaluation or trade execution.
- **`--stage risk`**: Evaluates the pre-trade risk policy at bar $q$. Produces a deterministic decision: `APPROVE` with an approved contract quantity, or `REJECT` (with quantity 0). Stops before order execution.

### Simulated Execution Stages (`entry`, `exit`)
- **`--stage entry`**: Takes an approved risk decision and simulates entry execution at the subsequent bar's Open ($e = q + 1$) using `MARKET` order semantics. Creates an in-memory virtual open position record (`PositionRecordV2`) and arms the structural stop at entry.
- **`--stage exit`**: Causally evaluates the active virtual position across subsequent bars ($t \ge e$):
  - **Structural Stop Breach**: Triggers intrabar (gap open or adverse price penetration) as a `STOP_MARKET` order fill, returning the position to `FLAT`.
  - **EMA20 Reversal**: Triggers when a bar closes beyond the EMA20, executing a `MARKET` exit on the subsequent bar's Open, returning the position to `FLAT`.
  - **End of Observations**: If no exit condition is met within the available data, records the explicit state `OPEN_UNREALIZED_END_OF_DATA`.

---

## 2. Virtual Positions and Core Invariants

The synthetic cycle operates exclusively with simulated in-memory structures:
1. **Virtual Representation Only**: Positions are represented by frozen immutable data structures (`PositionRecordV2`, `ExitPolicyBookV2`). There is no persistent live portfolio state or external state sync.
2. **Strict Quantity Conservation**: The quantity approved by the risk policy at entry is strictly preserved upon exit. Partial fills or unauthorized quantity changes fail closed.
3. **No Double Closes (Idempotence)**: Once an exit trigger is filled, the position transitions irreversibly to `FLAT`. Subsequent bars leave the book in flat state idempotently.
4. **Upstream Rejection Invariant**: If the risk gate rejects an entry (`ENTRY_REJECTED_BY_RISK`), no simulated entry, position, or exit record is created.
5. **No Take-Profit or Trailing Rules**: Consistent with frozen V2 rules, exits only execute on structural stop triggers or EMA20 bar-close crossings; no fixed profit targets or trailing stops are invented.

---

## 3. Absolute Safety Boundaries

> [!IMPORTANT]
> - **No Real Broker**: No connection to Alpaca, NinjaTrader, Interactive Brokers, or any other broker.
> - **No Real Orders**: No financial orders are created, signed, or submitted to any exchange or gateway.
> - **No Account Access**: No account credentials, balances, or purchasing power are queried or modified.
> - **No PnL Claims**: No financial gain/loss, yield, or profitability metrics are tracked or claimed in this synthetic layer.
> - **100% Offline & Hermetic**: Runs entirely without external network access or external market data feeds.

---

## 4. Synthetic Data Validation Boundaries

> [!WARNING]
> - **Deterministic Scenarios**: Validation uses synthetic 39-bar fixtures designed to exercise specific deterministic execution branches.
> - **Integrity & Causality Testing**: These missions prove causal sequencing, producer/verifier bit-level reconstruction parity, and tamper detection.
> - **Not a Commercial Backtest**: Synthetic validation does **not** constitute a statistical backtest on historical Out-Of-Sample (OOS) market data, nor does it establish strategy profitability or live market performance.

---

## 5. Running Synthetic Missions

Execute a bounded synthetic mission using the canonical CLI:

```sh
# Signal Confirmation Stage (39 observations, LONG profile)
PYTHONPATH=src:. python -m agicore.manager.mission_cycle_v2 \
  --output-dir /tmp/mission-confirm-long \
  --observations 39 --stage confirmation --profile confirmation-long-v1

# Structural Stop Stage
PYTHONPATH=src:. python -m agicore.manager.mission_cycle_v2 \
  --output-dir /tmp/mission-stop-long \
  --observations 39 --stage stop --profile confirmation-long-v1

# Risk Allocation Stage
PYTHONPATH=src:. python -m agicore.manager.mission_cycle_v2 \
  --output-dir /tmp/mission-risk-long \
  --observations 39 --stage risk --profile confirmation-long-v1

# Simulated Entry Stage
PYTHONPATH=src:. python -m agicore.manager.mission_cycle_v2 \
  --output-dir /tmp/mission-entry-long \
  --observations 39 --stage entry --profile confirmation-long-v1

# Simulated Exit Stage (Structural Stop Exit profile)
PYTHONPATH=src:. python -m agicore.manager.mission_cycle_v2 \
  --output-dir /tmp/mission-exit-stop-long \
  --observations 39 --stage exit --profile confirmation-long-exit-stop-v1
```

Available fixed profiles include:
- `confirmation-long-v1` / `confirmation-short-v1` (unrealized at end of data)
- `confirmation-long-rejected-v1` / `confirmation-short-rejected-v1` (rejected by risk)
- `confirmation-long-exit-stop-v1` / `confirmation-short-exit-stop-v1` (structural stop exit)
- `confirmation-long-exit-ema-v1` / `confirmation-short-exit-ema-v1` (EMA20 market exit)

---

## 6. Resuming Interrupted Missions (`--resume`)

If a mission process is interrupted before final verification, resume it using the existing directory without modifying parameters:

```sh
PYTHONPATH=src:. python -m agicore.manager.mission_cycle_v2 \
  --output-dir /tmp/mission-exit-stop-long --resume
```

`--resume` verifies the existing SQLite orchestration state, sealed bundle hash, task audit trail, and receipts. It refuses to resume any task with incomplete or tampered checkpoints, guaranteeing strict fail-closed safety.
