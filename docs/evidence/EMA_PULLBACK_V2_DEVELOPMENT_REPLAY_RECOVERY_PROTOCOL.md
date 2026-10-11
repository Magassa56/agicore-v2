# V2 DEVELOPMENT — precommitted recovery protocol

Protocol: EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_RECOVERY_PROTOCOL_V1.
Role: PRECOMMITTED_INFRASTRUCTURE_RECOVERY_EXCEPTION.
Status: PASS_PRECOMMITTED. This gate authorizes documents and synthetic repository
checks only. Recovery implementation and real recovery execution remain forbidden.

RECOVERY_PROTOCOL_SHA256 = a0588f0df41f409456330553de5fb9720bce4297676b0bc85137edd64ebd6db4
ORIGINAL_FAILURE_EVIDENCE_SHA256 = 6ac29d1c3703891726d882c3b128925c2232bd3d14e73d69ad24dd8be4d0544e

## Frozen bindings

| Binding | Exact value |
| --- | --- |
| Strategy | 965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a |
| DEVELOPMENT protocol | 68dc6e6409aea4efb88e4a19e09a7ba17a68043a79f14ec23e569d3353267402 |
| Dataset lineage | d9a5d15a8746491391ba13417a099801ba6add44be1f275d2ca9e699adf56b89 |
| Dataset ID | mnq-09-26-minute-last-development-ee6eeed4-v1 |
| Dataset RAW | ee6eeed4871947b1fabe3c85bf4b5b319dc0d68e86edec7d2000815e22b2a126 |
| Failed original run | d2eb78fb5a1b97e71fcc323b71da216449b35e4298729a26d6d052f4f26f00f4 |
| Failed original runner | c25000d5c180cceb0ed54fa12b5654c608936ae0c817b15e78fd9533e0467f92 |

The JSON files use sorted keys, compact separators, UTF-8 and one final LF.
Hashes cover their exact bytes; self-hashes are published outside the JSON.
The start-receipt copy preserves the original bytes without reserialization.

## Explicit exception, not a reinterpretation of ONCE

The base DEVELOPMENT protocol remains immutable and its original limit remains
ONCE. That original invocation has been consumed: CLAIMED / FAILED_NO_RESULT /
NOT_AVAILABLE. The observed classification is WORK_SESSION_LOST; root cause UNKNOWN.
No recoverable result, real performance value or verdict was found or used.
NONE_FOUND does not prove that exposure was impossible.

MAX_RECOVERY_ATTEMPTS = 1. Current strategy invocations = 1; if a recovery is later
authorized and invoked, total strategy invocations = 2. Original result count = 0.
MAX_AUTHORITATIVE_DEVELOPMENT_RESULTS = 1. The failed original remains permanently
in provenance. Its claim stays at its existing path, unchanged and outside Git.
No strategy, parameter, dataset selection, screening threshold or session filter
changes are allowed. OOS remains sealed; broker, paper/live orders and optimization
are forbidden. No recovery execution is authorized by this protocol gate.

## Future implementation and exact equivalence

A separate implementation gate must create a NEW runner source file and source
hash. The original runner and all 13 strategy components listed in the JSON must
remain unchanged. The strategy manifest remains unchanged. Only replay/orchestration
execution may be replaced for computational/runtime reliability.

On identical synthetic inputs, the new and original runners must agree exactly on
lifecycle, events, contexts, pullbacks, confirmations, stops, risk decisions, entries,
exits, suppressions, terminal states, quantities, base/effective fills, fees,
slippage, closed/open records, equity marks, segment attribution, every metric,
failed criteria, mechanical verdict and next gate. No tolerance or float comparison.

Only the runner source hash and its derived run ID may be normalized. Each original
output integrity hash must first validate; normalized canonical payloads and their
recomputed hashes must then agree. An identity-dependent output hash is not grounds
to ignore a strategy/result field. Recovery-specific provenance belongs in separate
evidence. Failure to prove equality means BLOCKED_SEMANTIC_EQUIVALENCE and no execution.

The engine must avoid repeated full-prefix reconstruction/copying per bar.
The implementation gate must measure 1000, 5000, 10000 and 20000 synthetic bars,
reporting runtime and peak memory where measurable. No real DEVELOPMENT benchmarking
or trading-outcome-based implementation choice. No benchmarks run in this gate.

## Future identity, claim and authoritative result

The run identity retains exactly four fields: strategy_manifest_sha256,
development_protocol_sha256, dataset_raw_sha256 and the NEW runner_source_sha256.
Compute its SHA-256 over sorted compact UTF-8 JSON plus final LF only after the
new source is final, and register it before real execution. The recovery evidence
must also bind this protocol hash, the failed original run ID, the failure-evidence
hash, the recovery source hash and the recovery run ID.
RECOVERY_RUN_ID_SHA256 = NOT_REGISTERED_YET.

A distinct ONE_TIME_EXCLUSIVE_RECOVERY_EXECUTION_CLAIM for RECOVERY_ATTEMPT = 1
must be created before real recovery data processing. No original-claim mutation,
claim deletion after creation, automatic retry or third execution is authorized.
If the consumed recovery attempt fails, stop for AGIcoreManager governance.

Only one completed immutable recovery result satisfying every frozen binding,
semantic-equivalence gate and result-schema invariant, following separate explicit
execution authorization, may become authoritative. The failed original never can.
Competing completed recovery results or selection between profit results are forbidden.

NEXT = EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_RECOVERY_IMPLEMENTATION_REQUIRED.
REAL_RECOVERY_EXECUTION = NOT_EXECUTED. Stop after this protocol gate.

## Validation

85 targeted evidence/DEVELOPMENT protocol tests pass, including 14 new canonical
evidence and frozen-binding checks. The full repository suite passes: 8456 tests,
six existing SQLite deprecation warnings, 92.33 seconds on Python 3.12.14.
Ruff check/format and diff whitespace checks pass. These checks use synthetic
fixtures and metadata; they do not execute a real DEVELOPMENT replay.
Green GitHub CI on the exact PR head remains required before merge.
