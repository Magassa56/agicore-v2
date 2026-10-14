# EMA_PULLBACK_V2_RECOVERY_OPTIMIZED_ENGINE_IMPLEMENTATION_V1

**Status: BLOCKED_SEMANTIC_EQUIVALENCE.** The candidate is retained on `feature/ema-pullback-v2-recovery-optimized-engine-v1`, based on `8eafe91c434468ead9c57731775ad186c9733751`. No commit, PR, merge or approved recovery run registration was created. No real recovery, DEVELOPMENT dataset read or OOS access occurred in this gate.

Implementation evidence SHA-256: `9427fdd8b0d8cd182013606cf8d9acd67490f45762cb91b043601c59d1451577`.
Entrypoint SHA-256: `a7d358bfd3069e9ca58943aae7aa52faf714f859e6b9eaed9c8f64615fbfde04`.
Unapproved source-closure manifest SHA-256: `c16d8ac79fe2b0d2c95e4d08563c6587e0789bf4faaa3fc31a9edb71add228b5`.
Registered recovery run ID: **NONE**.

## Exact blocker and mandatory stop

After processing exactly one invented, valid observation, the following call is rejected differently:

```python
reference.process_baseline_close_v2(previous=reference_book, closed_bar=None)
candidate.process_close(None)
```

| Runtime | Exception | Exact message |
| --- | --- | --- |
| Frozen reference | `BaselineAssemblyV2Error` | `the completed bar must retain its own earlier Open` |
| Candidate | `AttributeError` | `'NoneType' object has no attribute 'bar_index'` |

The candidate checks `bar.bar_index` for duplicate processing before the frozen type-validation guard. The typed books are equal immediately before this rejected input. Even though the RAW parser would reject malformed data upstream, the required reducer input/status/error contract cannot ignore this discrepancy.

The added regression `test_malformed_close_preserves_reference_error_contract_after_one_observation` fails. Exact fixture bytes, input descriptor, both pre-error native state snapshots, exception records, hashes and log are preserved in `/workspace/scratch/889b77c10552/v2-recovery-optimized-v1-checkpoints` and bound by the JSON evidence. The candidate has **not** been fixed. PR #313 requires STOP on an exact equivalence failure.

The resource supervisor was stopped using its existing session, with exit status **130**. Read-only process inventory confirmed no remaining benchmark process. Its partial progress is preserved, never marked PASS. This was an intentional protocol stop, not an infrastructure crash, a resource-cap failure or a real recovery invocation.

## Frozen bindings and existing failed attempt

| Binding | SHA-256 |
| --- | --- |
| Recovery protocol | `a0588f0df41f409456330553de5fb9720bce4297676b0bc85137edd64ebd6db4` |
| Architecture addendum | `b36c1631308ea746a66d0c2312ad50796725957eef0e9e60d52a26c771bd3cc8` |
| Strategy manifest | `965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a` |
| DEVELOPMENT protocol | `68dc6e6409aea4efb88e4a19e09a7ba17a68043a79f14ec23e569d3353267402` |
| Dataset lineage | `d9a5d15a8746491391ba13417a099801ba6add44be1f275d2ca9e699adf56b89` |
| Original failed run / preserved original claim | `d2eb78fb5a1b97e71fcc323b71da216449b35e4298729a26d6d052f4f26f00f4` |

The original claim remains untracked at its original path, with size 371 bytes and unchanged SHA-256/mtime. The historical `BLOCKED_ARCHITECTURE_CONFLICT` evidence remains unchanged. The original invocation count stays **1**, original result `FAILED_NO_RESULT`, original verdict `NOT_AVAILABLE`. Recovery invocation count stays **0**. Canonical real RAW identity is metadata only.

## Distinct implementation and contracts

Runtime: `EMA_PULLBACK_V2_RECOVERY_OPTIMIZED_ENGINE_V1`. The optimized Close paths are explicit computational equivalents, not execution of the original frozen assembly. Frozen Open execution, pure regime/context gates, initial stop, risk, protective stop, costs, record constructors and screening dependencies are reused unchanged. No monkeypatch, runtime rebind, AST rewrite, source mutation or tolerance is used by the engine.

| Candidate symbol | New source | Current acceptance |
| --- | --- | --- |
| `ExactIncrementalIndicatorsV1.ema20/macd` | `src/agicore/trading/ema_pullback_v2_recovery_indicators.py` | PASS_BOUNDED_TESTS |
| `RecoveryLifecycleV1.process_open/process_close/finish/snapshot` | `src/agicore/trading/ema_pullback_v2_recovery_lifecycle.py` | BLOCKED_SEMANTIC_EQUIVALENCE |
| `RecoveryMarksV1/build_native_result_v1` | `src/agicore/trading/ema_pullback_v2_recovery_accounting.py` | PASS_COMPLETED_BOUNDED_CASES_NOT_GLOBAL_APPROVAL |
| `CanonicalEncoderV1/validate_native_result_v1` | `src/agicore/trading/ema_pullback_v2_recovery_evidence.py` | PASS_COMPLETED_BOUNDED_CASES_NOT_RESOURCE_ACCEPTANCE |
| `run_synthetic_native_v1/evaluate_synthetic_recovery_v1` | `src/agicore/trading/ema_pullback_v2_recovery_optimized.py` | UNAPPROVED_BLOCKED_IMPLEMENTATION |

Each replacement's input/output/status/error and causal availability contract is recorded in the JSON, with source SHA and original reference symbols. The complete local dependency closure includes all reachable first-party imports and runtime version/direct standard-library source bindings. It is explicitly **unapproved**. Validation source files have separate hash bindings.

### Indicator induction and exact decoding

For tick prices `p_i=4 Close_i`, let `D_i=4*1755**i`, `A_i=D_i*EMA12_i`, `B_i=D_i*EMA26_i`, `M_i=A_i-B_i` and `C_i=D_i*SIGNAL_i`. Multiplying the frozen recurrences gives:

```text
A_i = 1485*A_(i-1) + 270*p_i*(D_(i-1)/4)
B_i = 1625*B_(i-1) + 130*p_i*(D_(i-1)/4)
C_i = 1404*C_(i-1) + M_i/5
```

The initial values are `A_0=B_0=p_0`, `C_0=0`; every positive-index `M_i` is divisible by five. These are algebraic equivalents of the original periods, not configurable strategy thresholds. Previous MACD/histogram state is retained before append. EMA20 begins with `sum(p_0..p_19)/80`, then `n'=19n+2p_i(d/4)`, `d'=21d`. The previous EMA is retained for pullback, the current EMA for exit.

Removing exact common prime powers from fully factored positive denominators yields coprime native Fractions. General rational inputs use an exact Fraction lane. Invalid histories delegate to frozen prefix functions without reseeding, preserving warmup/status/error precedence. No float, rounded indicator, symbolic placeholder or session reset is introduced.

The independent balanced-polynomial oracle satisfies:

```text
SIGNAL = (11/3)*EMA12 - (25/17)*EMA26 - (112/51)*EMA9(price)
```

It has the frozen zero seed and signal recurrence. Frozen-prefix equality is tested at the declared checkpoints through 1,000 observations; completed long synthetic workers also check exact endpoint values against this independent polynomial oracle.

### Reducer, accounting and native serialization

The reducer retains bounded live records and append-only immutable versions, reconstructing every required native history in original key insertion order. The Open phase uses metadata/Open only. Close resolves adverse stop before EMA signal, resolves the pending owner before raw-event admission, and keeps first-consumed-pullback ownership, immutable stop/risk/quantity and one-position policy. The invalid-input counterexample above prevents a global equivalence PASS.

One mark is appended per actual Close. Closed net equity is accumulated once; open marks use effective entry and only the actually paid entry fee. There is no hypothetical exit cost or end liquidation. The unchanged frozen screening evaluator supplies PF, loss streak, segmentation and criteria; trades are attributed by exit-fill timestamp.

The exact streaming encoder emits sorted compact UTF-8 JSON plus final LF, including fully reduced rational numerator/denominator records. Divide-and-conquer integer conversion and a bounded per-encoder cache preserve integer spelling. Candidate native identity/hash/schema are checked first; the legacy validator receives only a transparent two-identity-field projection and recomputed derived hash. No strategy/accounting field is normalized or omitted.

## Completed validation and retained failures

| Check | Result |
| --- | --- |
| Initial full targeted suite | 146 PASS in 72.06 s |
| Additional rejected-input contract test | **1 FAIL**, exact mismatch above |
| Frozen V2 regression suite | 2,232 PASS in 15.06 s |
| Per-Open/Close/EOD typed-book comparisons | 52 valid LONG/SHORT scenarios, twice |
| Complete native comparisons | 60 current labels, plus 3 preserved prior-generator input variants; 63 input/case pairs, each twice |
| Completed native byte equality | 126 receipts, all exact after permitted normalization only |
| Complete repository CI | NOT EXECUTED after semantic STOP |
| GitHub CI / publication | NOT STARTED; no PR |

Old dense fixtures were preserved when they did not exercise required coverage. The final fixed invented pulse/touch fixtures were predeclared before rerunning synthetic validation. Their inputs were selected for lifecycle coverage, not profitability; all earlier inputs/receipts/logs remain bound. This does not remove the failing error-contract case.

## Resource validation — partial, not approved

All declared caps remain unchanged: 4 GiB per worker, 8 GiB complete output, deadlines 120/600/1800/3600 seconds. Each accepted family/size was run in two fresh supervised processes with identical complete output SHA. Every actual source row was kept, including invented clock gaps and off-session observations.

| Actual observations | Result |
| --- | --- |
| 1,000 | Four families PASS twice |
| 5,000 | Four families PASS twice |
| 10,000 | Three families PASS twice; dense repeat 1 stopped during validation after bar 9999; repeat 2 not started |
| 20,000 | NOT EXECUTED after semantic STOP |

There are **22 completed workers out of 32 mandatory workers**. No omitted or interrupted workload is accepted as PASS. All START/progress/END/log/input/output/source hash evidence is indexed in the JSON. Bit-length measurements in completed receipts cover final indicator components; a stream-wide checkpoint/maxima proof remains incomplete.

The completed dense 5,000-bar pair took about 113 seconds, peaked at 549,150,720 bytes, and each produced 186,680,777 complete canonical bytes. Validation alone took about 103 seconds. The mandatory remaining workload is not retried.

### 89,841-observation estimates only

Extrapolating the completed dense family with exact size ratios gives the following **conditional ESTIMATES**, not real dataset measurements or guaranteed durations:

| Resource | ESTIMATE |
| --- | --- |
| Wall time | 10.1–182.3 hours (quadratic/cubic models) |
| CPU time | 10.2–182.6 CPU hours (quadratic/cubic models) |
| Peak memory | 9.87–177.30 GB (linear/quadratic models) |
| Complete output | 60.27 GB (quadratic model) |
| Serialization | 404–7,257 seconds (quadratic/cubic models) |

The measured host has 9 reported CPUs and 10,451,464,192 bytes physical memory. The native output estimate exceeds the precommitted output cap and measured available disk; even the linear memory estimate exceeds the worker cap. Operand growth and repeated exact native provenance prevent assuming incremental recurrence alone solves feasibility. Real lifecycle density/cancellation is unknown and was not inspected. Confidence for real execution is **NOT ESTABLISHED**; conservative capacity with at least 2x headroom is unproven. Estimates cannot authorize any real run.

## Execution governance

The real entrypoint currently always denies. A pure future authorization verifier checks explicit protocol/addendum/implementation/source/strategy/development/lineage/RAW/run/attempt/path bindings, but creates no authorization, claim or execution. A usable real boundary is **not approved** in this blocked candidate. No real recovery authorization artifact or claim exists.

Strategy components, protocol thresholds, lineage and dataset remain unchanged. Costs, quantities and exits remain frozen. REAL_TRADE_COUNT, REAL_PNL and DEVELOPMENT_VERDICT remain **NOT_AVAILABLE**.

**NEXT: BLOCKED_SEMANTIC_EQUIVALENCE — invalid Close error-contract discrepancy requires a new AGIcoreManager decision.** No repair, source registration, additional benchmark, CI publication, execution-readiness gate or real recovery is started.

## Frozen reference source identities

| Source | SHA-256 |
| --- | --- |
| src/agicore/trading/directional_impulse_v2.py | `7cd03b0385a409478134d6855d3f4bf51aef589b91657e753b878029858f95f8` |
| src/agicore/trading/reversal_transition_v2.py | `72d11ae348470bcb4a56b89473848524ab4ca23f670e532a557424d3e89d5a28` |
| src/agicore/trading/regime_context_v2.py | `2086f3573ae43a0254fbfd69ae5b3a3acde02fd3c8c3b38d8c412e4c720f13a2` |
| src/agicore/trading/ema20_pullback_v2.py | `6eb8db9aa65d88e740e855489ed323a3a863360663188a9de2833c8d28ccf4a2` |
| src/agicore/trading/ema_pullback_entry_confirmation_v2.py | `d21e767d569609995ebf4ef289eda041619744f2cfa3b357d2b072ee479e70b6` |
| src/agicore/trading/ema_pullback_risk_position_sizing_v2.py | `36002943acdd56a4600209c701f80a04f855a5b27450bf55ce85c934686b549a` |
| src/agicore/trading/ema_pullback_initial_stop_v2.py | `533643ea6efa9ba13972b10f86555e7dd5dcf7e10bfa5ea6b76af740d08846b4` |
| src/agicore/trading/ema_pullback_entry_execution_v2.py | `87e32388c022b66cb3b5583b9399fc1091f1bc449c3d58e35466b5a6d1224998` |
| src/agicore/trading/ema_pullback_structural_stop_trigger_fill_v2.py | `1bc60d1fac22d1c6b5a3ed44023051a1bfce8a066ce5617b64b4ea35316f3efd` |
| src/agicore/trading/ema_pullback_open_position_signal_policy_v2.py | `23be07a150feb11a693257d54dfa24f14e7d28b945906813a225b98f0aa39095` |
| src/agicore/trading/ema_pullback_fees_and_slippage_v2.py | `f68ae2feb6eb37e1f1ad5707aae1e8317abc2888deb24478a831711634aee12d` |
| src/agicore/trading/ema_pullback_exit_policy_v2.py | `ddac039586bf4fe0ec5fbe9b55607aecdc42836066d11f0fe5fb257c45a2cac7` |
| src/agicore/trading/ema_pullback_pending_opportunity_policy_v2.py | `ac5530a32df90076d4266a3495d3d60c9fcb99d90f1c4ec0af5e90413a8a8037` |
| src/agicore/trading/ema_pullback_regime_gated_baseline_v2.py | `28470b4275e889b753f3e478439fa7d5e46bf0ff394df23ba10eb8cdc29dbb76` |
| src/agicore/trading/ema_pullback_v2_development_replay.py | `c25000d5c180cceb0ed54fa12b5654c608936ae0c817b15e78fd9533e0467f92` |
| tools/ema_pullback_v2_development_protocol.py | `55673813d9d716303aec2ad24fda425ca22d52a186e3b2e071653cfb81e4e1ec` |
