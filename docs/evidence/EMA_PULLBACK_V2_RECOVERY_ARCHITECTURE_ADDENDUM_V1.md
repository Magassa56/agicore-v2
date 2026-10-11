# V2 recovery architecture addendum V1

PHASE = EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_RECOVERY_ARCHITECTURE_ADDENDUM.
STATUS = PASS_PRECOMMITTED. This approves a documentary computational exception in principle.
A new engine remains **BLOCKED_PENDING_NEW_IMPLEMENTATION**, equivalence NOT_PROVEN,
scalability NOT_RUN. No runtime is implemented or executed by this addendum.

ADDENDUM_SHA256 = b36c1631308ea746a66d0c2312ad50796725957eef0e9e60d52a26c771bd3cc8

Parent: EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_RECOVERY_PROTOCOL_V1,
SHA-256 a0588f0df41f409456330553de5fb9720bce4297676b0bc85137edd64ebd6db4, unchanged.
Base main: f48990d5ec579e5bf7e516ad5587103d094a68ce after PR #312.
Authorization: the two identical architecture attachments, SHA-256
b0c878c6686980ddfe8eb3c8961ef161951c14cafd4441e751771af565a999d7.

## Formal exception and preserved work

The earlier orchestration-only composition contract cannot provide an incremental
EMA/MACD value to the unchanged consumers. This addendum records an **explicit
exception**, rather than claiming literal compatibility with that composition
contract. It permits a separately versioned recovery engine to compute exact
mathematical equivalents of pure indicators and replay/consumer transitions in a
future explicitly authorized implementation gate. All other recovery-protocol
requirements remain binding. No historical protocol or source bytes are changed.

The original frozen source hashes remain the specification. The 13 components,
assembly, original runner, screening implementation, strategy manifest, dataset,
DEVELOPMENT protocol and thresholds retain their hashes. No monkeypatch, dynamic
rebinding, AST replacement, altered constants or tolerance predicate is allowed.
The future engine must be attributed as a distinct runtime; it must not claim
that the original assembly executed recovery if it served only as a reference.

The previous worktree contained current-state edits, two untracked documentary
implementation records and the original claim. Exact snapshots were preserved
before the dedicated branch was created. The two blocked implementation records
are retained byte-identically and included as historical evidence; their status
is not rewritten as PASS. Their JSON SHA-256 is
4b86ad9ce46a6f033447a79e393c4dfbc92bd7af78df725786d415cc969a954d.
The claim remains at its existing path, immutable and untracked, 371 bytes,
SHA-256 d2eb78fb5a1b97e71fcc323b71da216449b35e4298729a26d6d052f4f26f00f4.

## Source-supported conflict and cost

ARCHITECTURE_ROOT_CONFLICT = FROZEN_INDICATOR_CONSUMERS_HAVE_NO_INCREMENTAL_INJECTION_INTERFACE.
The JSON binds exact source hashes, AST symbols, line ranges and signatures.

| Reference consumer | Internal evaluator | Consequence |
| --- | --- | --- |
| evaluate_ema20_pullback_v2 | evaluate_ema20_v2(k-1) | No precomputed reference/state parameter |
| _evaluate_candidate | evaluate_macd_v2(q) | No incremental MACD parameter |
| process_exit_policy_close_v2 | evaluate_ema20_v2(r) | No incremental exit EMA parameter |

Both evaluators start from index zero. The preserved eight synthetic access probes
confirm complete prefix reads, including adjacent terminal indices. A whole-call
cache does not reuse a recurrence for a new terminal index. Assembly also rebuilds
RAW/price/rejection views and immutable tuples at each Close. Position/pending/risk
books revalidate histories and join nested provenance. The runner re-sums realized
trades on each mark; native conversion, large integer decimal encoding, hashing
and schema validation traverse complete nested output. Fixing only the indicator
interface cannot establish full scalability.

Static cost evidence does **not** diagnose the lost original session. Its cause
and exact post-claim progress remain UNKNOWN.

## Exact arithmetic and evidence growth

EMA20 remains seeded at index 19 by the exact mean of 20 actual closes; subsequent
values are (2*Close + 19*previous)/21. MACD remains EMA12/EMA26/signal9 with the
frozen seed at zero, exact recurrences and 35 actual closed bars of warmup.
No rounding, float, tolerance, truncation or session/gap reset is permitted.

For an invented series with P=20000 through index 19, P+1/4 at index 20, and P
thereafter, EMA20[20+m] is exactly P + 19**m/(42*21**m). Its reduced denominator is
42*21**m: 19 is coprime to 42*21. Even one pulse followed by constant closes keeps
growing the exact representation; a constant-from-seed benchmark misses this risk.

For tick-grid closes, reduced denominators divide 80*21**(i-19) for EMA20,
4*13**i for EMA12, 4*27**i for EMA26, 4*(13*27)**i for MACD and
4*(5*13*27)**i for signal/histogram. At 89,841 observations the EMA20 divisor
envelope has 394,529 bits and the signal/histogram envelope 968,231 bits.
These values are exact integer-power bit lengths, **not** observations of real
market data, actual reduced MACD denominators, runtime timings or memory estimates.
The JSON records the same symbolic envelopes at all four future benchmark sizes.

GCD/cross-products/decimal conversion become more costly with operand size.
An O(n) number of recurrence steps therefore does not prove O(n) runtime.
If linearly many required snapshots contain linearly growing rational encodings,
complete numeric text can grow quadratically; nested provenance may add further
repetition. That conditional workload bound does not describe a measured result.
Internal sharing or streaming cannot remove required native output fields.

## Proposed design options, not implementations

| Option | Exact contract | Remaining risk |
| --- | --- | --- |
| Incremental reduced Fraction | Same seed, recurrence, prior/current values and fail-closed statuses | Big-integer growth remains |
| Scaled integers and factored denominator | Exact decoder to reduced Fraction; exact cross-products or common denominator | Unreduced values can be larger; native expansion remains |
| Persistent exact rational expression DAG | Acyclic versioned nodes; terminating exact decoder and sign/equality procedure | Compact storage does not prove fast comparison or decoding |
| Append-only snapshots and streamed native JSON | Reconstruct every reference record in the same order and canonical spelling | Complete output size and validation still need measurement |

No symbolic encoding may replace a native numerator/denominator in the frozen
result schema. No required history may be silently dropped, deduplicated or
compressed into references. If exact complete evidence cannot be produced within
demonstrated resources, return BLOCKED_TECHNICAL_FEASIBILITY; do not shrink schema.

The proposed runtime has a default-deny boundary, exact per-observation indicator
state, a lifecycle reducer with equivalent invariant checks and append-only
provenance, exact reporting and a complete streaming serializer. All state is
invocation-owned. Each new kernel/reducer/serializer needs a frozen-symbol
contract, proof of equivalence, independent differential cases and a source hash.
The entire local executable dependency closure and runtime versions must be bound
by a canonical source-bundle manifest in evidence/readiness/authorization. The
four-field run identity stays unchanged structurally and uses the new entrypoint
SHA; helper hashes are additional required bindings. Dependency drift fails closed.

## Five independent acceptance properties

| Property | Required evidence |
| --- | --- |
| A: formula equivalence | Algebra/induction, exact initialization and recurrence |
| B: predicate equivalence | Exact boundaries, statuses/errors, allowed-field and timing comparisons |
| C: immutable result equivalence | Full snapshots, provenance and canonical normalized result equality |
| D: computation feasibility | Bounded nonconstant and dense synthetic workloads, actual resource measurements |
| E: serialization feasibility | Complete native evidence produced and validated, output bytes and encoding cost |

Neither plausible metrics nor a fast constant stream establishes all five.

## Differential-test precommitment

Compare the hashed original runner/components with the future candidate using only
invented inputs. Hash the scenario generator, fixed seeds, lengths and inventory
before outputs are known; do not select fixtures by profitability. Cover all
indicator states, every predicate/status/error, regime events, contexts, pending
ownership, confirmations, risk, quantity, entries/exits/stops/costs, all closed/open
records, marks, lifecycle histories, segments, metrics, failed criteria and verdict.

The JSON inventories threshold equality and adjacent values, warmup, LONG/SHORT
mirrors, impulse/reversal, ambiguous events, pending competition, expiry, clock
gaps/missing indexed observations, opening stop priority, intrabar/breached stops,
entry-bar EMA exits, malformed/unclosed inputs, off-session rows, end-of-data,
PF/streak/drawdown/accounting and arithmetic-growth inputs. Availability sentinels,
future mutations and duplicate processing must preserve exact behavior.

Run each complete lifecycle scenario twice from fresh state/processes. Verify
**both original output hashes before normalization**. Normalize only
run_identity.runner_source_sha256 and run_id_sha256; mechanically recompute the
derived output_sha256. All other result fields remain equal. Compare the canonical
normalized bytes and hashes exactly. Keep pre-normalization hashes/source IDs in
separate evidence. Long fixed indicator checkpoints and algebraic invariants
supplement complete small-scenario runs; they are not an exhaustive 89,841-bar
reference replay. Any missing proof, mismatch or omitted field blocks PASS.

## Future scalability acceptance, not run here

Require fresh-process synthetic tests at 1000, 5000, 10000 and 20000 observations,
twice for each constant control, noncancelling pulse, drift/oscillation and dense
LONG/SHORT lifecycle family with gaps/off-session rows. Predeclared wall limits
are 120/600/1800/3600 seconds respectively, peak memory 4 GiB, output 8 GiB.
These are infrastructure safety caps, not trading parameters or a promise that
Work supplies a suitable durable host. Bounds must be enforceable and measured.

Persist START/progress/END/timeout logs with UTC, actual Open/Close phase, last
completed index, source/input/output/log hashes, wall and CPU time where measurable,
peak memory/method, rational bit lengths, complete output size, encoding/validation
time, observation count and exit status. Liveness is not bar progress. Logs must
survive session loss. Missing measurements, timeouts or omitted families block
feasibility; no automatic cap relaxation. Project 89,841-observation resources
using measured nonconstant/dense cases and symbolic bounds, label estimates and
uncertainty, and verify host capacity plus headroom before any recovery authorization.

All benchmark statuses here are NOT_RUN. Runtime/memory/output completion for
89,841 observations is NOT_ESTIMATED. Full exact native evidence feasibility
remains unproven; it is an explicit future acceptance gate, not an architectural PASS.

## Causal rules and safety

Every frozen causal rule remains: actual Open then Close; next-Open fills; immutable
k..q stop plus one tick; stop priority over pending EMA exit; one-shot contexts and
first-consumed pending lock; quantity 1–2 MNQ planned from Close[q] under the $100
structural budget; one adverse tick and $0.51 per contract/fill; no TP, breakeven,
trailing/time/session exit, forced end liquidation, interpolation or filtering of
the July 4 stored observation. All source constants, exact status precedence and
reference admission order control. Nothing in this document introduces parameters.

Original invocation count = 1, FAILED_NO_RESULT, verdict NOT_AVAILABLE; claim
unchanged. Maximum recovery attempts = 1; recovery invocation count = 0;
recovery identity NOT_REGISTERED, claim NOT_CREATED, second execution NOT_AUTHORIZED.
No authorization record is created. Real data, OOS and broker are not accessed.

A mismatch retains all synthetic counterexamples and rejects the candidate.
Resource failure returns BLOCKED_TECHNICAL_FEASIBILITY. A future consumed recovery
failure preserves its claim and stops for AGIcoreManager: no restart, automatic
retry or third invocation. Rollback means withholding candidate execution while
retaining evidence and the intact reference, never deleting claims or prior work.

NEXT = EMA_PULLBACK_V2_RECOVERY_OPTIMIZED_ENGINE_IMPLEMENTATION_REQUIRED.
A new explicit implementation authorization is required; real execution requires
its later separate gate. Stop after documentary validation/publication/merge.

## Documentary validation in this gate

- 393 targeted tests PASS in 12.88s, including 78 recovery-protocol/addendum tests
  (64 new documentary/AST/arithmetic/normalization checks).
- Full repository suite PASS: 8520 tests, six dependency deprecation warnings, 93.58s.
- Ruff check/format, canonical JSON/hash checks and diff whitespace checks PASS.
- Preserved blocked evidence and original claim match their saved bytes; claim mtime unchanged.
- No new runner, helper runtime, recovery identity, authorization or recovery claim exists.
- Complete future-engine equivalence/scalability are NOT_RUN, not claimed by these checks.
- Full local CI log SHA-256: ec18daa72cae3f91fa815249c9cdcfeedd6c9e63515d53efae182717224de059.

GitHub CI on the exact published PR head remains mandatory before merge.
