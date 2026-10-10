# V2 DEVELOPMENT — original execution failed without a result

Status: FAILED_ORIGINAL_EXECUTION_CLAIMED. The original strategy was invoked once.
The original result status is FAILED_NO_RESULT and its verdict is NOT_AVAILABLE.

Canonical failure evidence SHA-256: 6ac29d1c3703891726d882c3b128925c2232bd3d14e73d69ad24dd8be4d0544e
Original run ID: d2eb78fb5a1b97e71fcc323b71da216449b35e4298729a26d6d052f4f26f00f4
Original runner SHA-256: c25000d5c180cceb0ed54fa12b5654c608936ae0c817b15e78fd9533e0467f92

## Evidence preserved

The operational claim remains untracked and immutable at /workspace/scratch/889b77c10552/agicore-d003-bundle-audit-main/docs/evidence/EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_IMPLEMENTATION.json.original-execution-claim.
Its 371 exact bytes have SHA-256 d2eb78fb5a1b97e71fcc323b71da216449b35e4298729a26d6d052f4f26f00f4. It is not added to Git.
The external start receipt remains at /workspace/scratch/889b77c10552/EMA_PULLBACK_V2_DEVELOPMENT_ORIGINAL_d2eb78fb5a1b97e7.execution-start.json.
An exact-byte copy is preserved in docs/evidence/EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_ORIGINAL_START_RECEIPT.json; its SHA-256 is ef0330ff0fa4f3116ab6b39ac736d7211cd39235904262696b1f55fea04e3574.
Neither original artifact is moved, rewritten, renamed or deleted.

The original invocation started at 2026-10-10T15:10:21.578136Z. The last historical
RUNNING observation is 2026-10-10T15:48:27.150Z; it records process liveness, not
bar progress. The original process is inactive. No completed/partial result,
completion receipt, application traceback or exit code was recovered.
The expected result path /workspace/scratch/889b77c10552/EMA_PULLBACK_V2_DEVELOPMENT_ORIGINAL_d2eb78fb5a1b97e7.json is absent.

## Forensic classification and limits

WORK_SESSION_LOST is supported by environment_offline and Unknown process id 53360,
the absent historical PID 1121, and the replacement environment's later startup.
The exact root cause and termination time are UNKNOWN. The claim's current
filesystem birth time is not the original claim creation time.

Registration verification precedes claim creation. RAW loading and strategy
processing follow it. Therefore the claim does not prove that the RAW was parsed,
that any particular number of bars was processed, or that a verdict was computed.
REAL_DEVELOPMENT_EXECUTION_PROGRESS = UNKNOWN_AFTER_CLAIM.
REAL_PERFORMANCE_EXPOSURE = NONE_FOUND_NOT_PROVEN_IMPOSSIBLE.
No actual trade count, PnL or verdict is reported; none is replaced with zero.
Preflight identity checks do not prove historical loader progress.
The available local Work logs do not cover the lost invocation.

All strategy/protocol/lineage/dataset bindings are carried by the canonical JSON.
OOS_ACCESSED = FALSE. SECOND_EXECUTION_AUTHORIZED = FALSE.
This historical failure remains in provenance permanently and can never become
an authoritative DEVELOPMENT result.
