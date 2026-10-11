# V2 recovery implementation — frozen indicator interface conflict

STATUS = BLOCKED_ARCHITECTURE_CONFLICT.
Base main: f48990d5ec579e5bf7e516ad5587103d094a68ce, after PR #312.
Recovery protocol: a0588f0df41f409456330553de5fb9720bce4297676b0bc85137edd64ebd6db4.
Canonical implementation evidence SHA-256: 4b86ad9ce46a6f033447a79e393c4dfbc92bd7af78df725786d415cc969a954d

No recovery runner, executable recovery identity, execution authorization or
recovery claim has been created. The source audit and synthetic indicator probes
are completed work; they are not runner equivalence or scalability measurements.

## Smallest conflict

The three frozen consumers call the full-prefix indicator functions internally:

| Frozen consumer | Internal dependency | Missing integration interface |
| --- | --- | --- |
| `ema20_pullback_v2.evaluate_ema20_pullback_v2` | `evaluate_ema20_v2(k-1)` | No exact precomputed EMA, prior EMA state or evaluator argument |
| `ema_pullback_entry_confirmation_v2._evaluate_candidate` | `evaluate_macd_v2(q)` | No exact precomputed MACD, prior MACD state or evaluator argument |
| `ema_pullback_exit_policy_v2.process_exit_policy_close_v2` | `evaluate_ema20_v2(r)` | No exact precomputed EMA, prior EMA state or evaluator argument |

Both evaluators traverse `range(through_bar_index + 1)` and reseed from history.
A caller-owned cache cannot be consumed through these existing signatures.
Memoizing a completed request does not reuse its calculation for a different
terminal index. Dropping the prefix makes required inputs missing and fails closed.

Removing this repeated work through those consumers requires an explicit decision
on an exact incremental indicator interface. Modifying their internals, rebinding
their function globals, or copying their price predicates into the runner is not
performed. This is a conflict in the authorized composition path, not a proof
that every possible computational architecture is infeasible.

## Synthetic interface evidence

A separate Python process used 257 invented minute observations dated 2099-01-01:
O=20000, H=20001, L=19999, C=20000+(index mod 3)/4, exact Decimal inputs.
A mapping recorded every `get` requested by each unchanged indicator evaluator.

| Requested index | EMA20 reads | MACD reads | Read range for each |
| --- | ---: | ---: | --- |
| 63 | 64 | 64 | 0 through 63 |
| 127 | 128 | 128 | 0 through 127 |
| 255 | 256 | 256 | 0 through 255 |
| 256, immediately after 255 | 257 | 257 | 0 through 256 again |

All eight evaluations read each index exactly once in order. No actual strategy
dataset, signal chain, trade or PnL was used. No runtime or memory benchmark is
inferred from these access counts.

## Other computational growth and legal cache candidates

The assembly rebuilds full RAW, price and rejection mappings per Close and appends
immutable tuples. Frozen position/pending books revalidate cumulative histories;
pending provenance also searches historical consumptions. Risk, cost and exit
books perform historical searches. The original runner recomputes the sum of
closed-trade realized PnL per mark. Its final canonical conversion, validation and
hashing repeatedly traverse nested records and increasingly large rational values.
The JSON binds exact source hashes, symbols, signatures and line locations.

Append-only source/view storage, accumulated realized equity, invocation-local
metadata caches and cached canonical bytes can reduce adapter overhead without
new business rules. They do not supply the missing indicator interface. An exact
indicator continuation cache is mathematically reusable but needs an explicitly
authorized path into the three existing consumers.

EMA20's seed and all preceding closes, MACD's initial seed and complete recurrence,
actual observation clocks, ownership, immutable fill provenance, every equity mark
and exit-timestamp segmentation must retain full historical semantics. No window
truncation, approximate arithmetic, float, reset or synthetic observation is proposed.
Growing exact numerators/denominators also make constant-price timings insufficient
to establish nonconstant-input feasibility.

## Feasibility and governance

The 1000/5000/10000/20000 recovery benchmarks are NOT_RUN_ARCHITECTURE_CONFLICT.
No compliant candidate runner exists to benchmark. Runtime and peak memory for
89,841 observations are NOT_ESTIMATED; completion feasibility is NOT_ESTABLISHED.
Full result equivalence, fresh-process runner determinism and future authorization
safety tests are not claimed to pass.

The original invocation remains 1 / FAILED_NO_RESULT / NOT_AVAILABLE with progress
UNKNOWN_AFTER_CLAIM. WORK_SESSION_LOST remains the observed classification;
its exact termination mechanism is UNKNOWN. The original claim is unchanged and
untracked. Recovery attempts used = 0; maximum = 1. No real RAW or OOS was accessed.

NEXT = EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_RECOVERY_IMPLEMENTATION_REQUIRED,
blocked pending an explicit AGIcoreManager decision on the indicator interface.
No readiness gate, implementation workaround or real recovery execution is opened.

## Validation of preserved work

2168 existing V2/protocol regression tests pass (14.37 seconds). The full existing
repository suite passes: 8456 tests, six SQLite deprecation warnings, 91.25 seconds.
Canonical evidence and inspected source hashes pass; diff whitespace checks pass.
No Python source was added or modified, so new-source lint is not applicable.
No new-runner equivalence, safety or scalability test is presented as passing.
No PR, commit, GitHub CI request or merge was made for this blocked implementation.
