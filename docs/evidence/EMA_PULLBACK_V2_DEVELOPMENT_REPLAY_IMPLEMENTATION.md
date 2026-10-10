# EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_IMPLEMENTATION

PHASE: EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_IMPLEMENTATION
STATUS: PASS
Scope: implementation and synthetic testing only, on main after merged PR #309.

The separate repository adapter delegates every strategy transition to the frozen
assembly. All 13 frozen components and the assembly retain their source bindings;
the existing assembly remains SYNTHETIC_ONLY. This evidence contains no real
DEVELOPMENT result and does not authorize execution.

## Frozen bindings

| Binding | Exact value |
| --- | --- |
| Strategy | EMA_PULLBACK_V2_REGIME_GATED_BASELINE, formalization version 1 |
| Strategy manifest SHA-256 | 965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a |
| DEVELOPMENT protocol SHA-256 | 68dc6e6409aea4efb88e4a19e09a7ba17a68043a79f14ec23e569d3353267402 |
| Dataset lineage manifest SHA-256 | d9a5d15a8746491391ba13417a099801ba6add44be1f275d2ca9e699adf56b89 |
| Canonical dataset ID | mnq-09-26-minute-last-development-ee6eeed4-v1 |
| Canonical RAW SHA-256 | ee6eeed4871947b1fabe3c85bf4b5b319dc0d68e86edec7d2000815e22b2a126 |
| Canonical RAW size / rows | 4785270 bytes / 89841 actual observations |
| Canonical first / last UTC | 2026-06-18T22:01:00Z / 2026-09-18T13:30:00Z |
| Dataset role | EXPOSED_DEVELOPMENT |
| Final runner source SHA-256 | c25000d5c180cceb0ed54fa12b5654c608936ae0c817b15e78fd9533e0467f92 |
| ORIGINAL_DEVELOPMENT_RUN_ID SHA-256 | d2eb78fb5a1b97e71fcc323b71da216449b35e4298729a26d6d052f4f26f00f4 |

These dataset facts were verified against lineage metadata. The real RAW was not
opened. The JSON evidence stores the single original run identity before any real
execution. Its four keys are serialized with sorted keys, compact JSON, UTF-8 and
one final LF; SHA-256 covers those exact identity bytes. The implementation-evidence
file itself is canonical JSON plus LF and is not part of the four-key run identity.

## Adapter and causal clock

`src/agicore/trading/ema_pullback_v2_development_replay.py` exposes immutable verified
bindings, exact RAW parsing, synthetic evaluation, result validation and a future
registered execution boundary. Strategy behavior comes exclusively from:

- `begin_regime_gated_baseline_v2`;
- `process_baseline_open_v2`;
- `process_baseline_close_v2`;
- `finish_regime_gated_baseline_v2`.

Each source row becomes one sequential observation. Open receives only index, UTC
timestamp and Open; Close receives the closed OHLCV afterward. The UTC NinjaTrader
End-of-Bar metadata is preserved without timestamp shifting. Native gap and intrabar
stop priority, risk decisions, entry timing and EMA exit timing remain unchanged.
An exact intrabar trigger time is never invented.

The parser accepts `YYYYMMDD HHMMSS;Open;High;Low;Close;Volume`, including native LF
or CRLF record separators. It uses finite Decimal OHLC and nonnegative integer
volume. It checks exact MNQ tick alignment and OHLC validity, then rejects duplicate
or nonchronological timestamps. It performs no price correction, deduplication,
sorting, forward filling or synthetic minute construction. Gaps do not reset native
EMA/MACD. An invented observation at 2026-07-04T14:40:00Z is explicitly tested as
processed, with an off-session diagnostic label. No session filter is introduced.

## Accounting, metrics and records

The adapter retains the native event, context, consumed pullback, confirmation,
initial stop, risk, entry, exit, suppression and terminal histories. Trade provenance
also contains the native cost record. It reconstructs counters from those histories
and verifies the frozen protocol result schema and cross-record invariants.

All calculation and result values remain exact Fractions. Canonical JSON encodes
rational numerators/denominators exactly, including integers beyond Python's default
decimal-string digit limit, without changing any global interpreter setting. No
float or intermediate rounding is used. Monetary display rounding, if later needed,
remains a reporting boundary under the frozen HALF_UP convention.

There is exactly one marked sample per actual closed bar. Marked equity equals
closed-trade net realized equity plus the currently open position marked at raw
Close against effective entry, less its actually paid entry fee. An open position
has no hypothetical exit fee or exit slippage. Drawdown includes the zero starting
baseline and native unrealized equity. End-of-data never manufactures a fill or
liquidation; an open trade retains realized PnL NONE.

The adapter delegates thresholds, profit-factor edge cases, loss streaks, verdict
ordering and exact elapsed-time segment metrics to the precommitted protocol helper.
S1/S2 are half-open, S3 includes the final source timestamp. Both trade costs are
assigned to the segment containing the native EXIT fill timestamp, with no liquidation
at a segment boundary. Session counts use the lineage-bound calendar/gap evidence
for diagnostics only and do not enter screening.

## Future execution guard

Real loading and execution are denied by default before any RAW path access. A
future explicitly authorized `EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_EXECUTION` gate
must use the canonical implementation registration. The source hash and all four
identity bindings must still match. A copied registration path is rejected.

An exclusive original-run claim is written before RAW access. Duplicate claims,
including after a failed integrity check, fail closed without an automatic retry.
An existing output is never overwritten. The loader then verifies canonical ID,
role, exact bytes SHA-256, size, row count and first/last timestamps before calling
any strategy function. Synthetic temporary files test these guards; the real RAW
was never used. A later authorized determinism proof must retain identical input,
code and output hashes and may not replace the original verdict.

## Synthetic verification

The new unit tests exercise exact parsing, float rejection, identity mismatches,
chronology, gaps, off-session processing, the Open facade, next-Open execution,
stop and EMA priority, one/two-contract sizing, risk rejection, exact fees/slippage,
open end-of-data accounting, marked drawdown, loss streaks, PF infinity/zero,
elapsed-time segments and exit attribution, schema failures and history counts.

The 25 existing invented lifecycle scenarios run LONG and SHORT twice from fresh
state. Complete output bytes and payload hashes match exactly; the JSON evidence
records all 50 scenario pairs. Additional tests preserve native phase idempotence,
prevent future mutations from changing earlier decisions, confirm that suppressed
pending signals do not replace source provenance, and deny real access by default.
Verification: 146 adapter tests are included in 328 focused tests (PASS, 12.40s);
full repository suite PASS: 8442 tests, six existing SQLite warnings, 97.68s. Ruff
check/format, diff-check and frozen bindings PASS. The GitHub CI on the exact PR
head is additionally required before merge. The JSON evidence records these checks.

## Gate outcome

REAL_DEVELOPMENT_DATA_ACCESSED: FALSE
REAL_STRATEGY_REPLAY: NOT_EXECUTED
REAL_TRADE_COUNT: NOT_COMPUTED
REAL_PNL: NOT_COMPUTED
REAL_DEVELOPMENT_VERDICT: NOT_PRODUCED
OOS_ACCESSED: FALSE
BROKER_ACCESSED: FALSE
PARAMETER_CHANGES: FALSE
NEXT: EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_EXECUTION_REQUIRED

The next gate requires separate explicit authorization. No real execution is
performed or scheduled by this implementation.

Implementation evidence SHA-256: d9a0fa3d6776a109d9b373deb9563afd760744e7a65146ca65c96ecbc3727a0b.
