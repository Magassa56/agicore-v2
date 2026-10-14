# EMA_PULLBACK_V2_RECOVERY_SEMANTIC_REPAIR_AND_FEASIBILITY_TRIAGE

**STATUS: BLOCKED_TECHNICAL_FEASIBILITY.** The isolated Close error is repaired. The declared bounded native comparisons are exact, but complete recovery under the frozen memory/native-output limits is not demonstrated. No real recovery is authorized, registered or executed.

Triage JSON SHA-256: `e728ed5cd3fbde38f1284fd8e2af7cc2ffafbfcf99fe977599cb264263aa45ef`.
Updated implementation JSON SHA-256: `e91ca2d4de3d2182f1bba667cb9e34b95c00b25e5731dea20445c41fca16ce65`.
Source closure SHA-256: `a9954c13d1fd39b52ce4283f47f745c09c4bbcb145707a62ecd09bc2d264f3cf` (unapproved).

## Repair and preserved evidence

The reference `process_baseline_close_v2` performs, in order: end-of-data return; `getattr(bar, "bar_index", None)`; duplicate-index return; source-type validation; `is_closed is True`; existence of the own Open; matching index/timestamp; matching Open. The recovery reducer now follows that order before touching its indicators or ledgers. It does not catch or translate arbitrary AttributeErrors.

| Counterexample outcome | Before repair | After repair |
| --- | --- | --- |
| Frozen reference exception | `BaselineAssemblyV2Error` | `BaselineAssemblyV2Error` |
| Candidate exception | `AttributeError` | `BaselineAssemblyV2Error` |
| Correct message | `the completed bar must retain its own earlier Open` | identical |

The guard preserves the reference's duplicate/end-of-data precedence even for malformed duplicate arguments. Rejected/no-op cases leave live state, indicators and every version ledger unchanged. Tests compare exact exception class, message and field-read order. The intentional poisoned synthetic instances affect only test-owned objects; no frozen constructor/global or real observation is modified.

| Source identity | Previous | Revised |
| --- | --- | --- |
| Entrypoint | `a7d358bfd3069e9ca58943aae7aa52faf714f859e6b9eaed9c8f64615fbfde04` | `854a6cbe7b89f3c6f0e9f49a8a5095745baf20693c2e89b115dfcadbfacbdf56` |
| Reducer | `e314f6b1cc911f1c9ff6b8c6a7ed8dcf076e85d65c42849bf3d0e03b8c25190c` | `ec154f8d33c1092575cb96f2e4d2ddaea7aab5156e67eedb953b3db768a8b422` |

The executable repair is in `ema_pullback_v2_recovery_lifecycle.py`; the entrypoint documentation identifies the repaired validation/dependency boundary. The old implementation JSON/MD/closure are retained byte-for-byte in `EMA_PULLBACK_V2_RECOVERY_OPTIMIZED_ENGINE_V1_HISTORY/blocked_semantic_9427fdd8/`. Historical invalid-input counterexamples, resource outputs and source snapshots remain preserved.

## Revised-source validation

- **22 focused tests PASS**: None, incorrect type, unclosed/truthy flags, wrong index/timestamp/Open, missing own Open, duplicate and end-of-data precedence, permitted reads and rejection atomicity.
- **63 native case/input pairs PASS twice**: 60 current cases and 3 preserved historical generator variants. All 126 receipts are newly produced on the revised source.
- Original/candidate native integrity hashes are checked before normalizing only `run_identity.runner_source_sha256` and `run_id_sha256`; the derived `output_sha256` is recomputed. Every strategy, lifecycle, execution, cost, accounting, segment and verdict field remains in exact normalized byte comparison.
- The bulk command collected 168 tests and reported exit 0, but its retained log has no terminal pytest summary. It is **not certified as a full-suite PASS**. Its complete receipts cover 59 native cases; the absent `dual_probeSHORT` proof was checked once separately under a 30-second limit: **1 PASS**, two exact receipts. The bulk command was not restarted.
- The bulk rerun included the 19 indicator checks and 52 per-Open/Close/end scenarios. The terminal-summary limitation remains explicit.
- A test-spy constructor failure happened before reducer comparison; its log is retained. The constructor instrumentation was fixed, with no second change to the repaired reducer.
- Ruff passes for modified recovery source/tests. Full repository CI and publication are not started while resource feasibility is blocked.

## Existing measurements and read-only structure audit

No unfinished dense 10,000 trial or 20,000 trial was run. Existing measurements belong to the previous candidate source and remain historical; they are not new timing/RSS proof for the revised engine.

| Prior dense invented stream | Complete native bytes | Maximum observed RSS | Wall time | Combined validation | Serialization |
| --- | --- | --- | --- | --- | --- |
| 1,000 observations | 6,771,181 | 65,380,352 bytes | about 2.1 s | about 1.16 s | about 0.11 s |
| 5,000 observations | 186,680,777 | 549,150,720 bytes | about 113 s | about 103 s | about 1.25 s |

A predeclared read-only diagnostic scanned the already-existing outputs only: **1.64 seconds**, **21,315,584 bytes peak RSS**, zero trading imports/calls and no financial-value recomputation. It verified their existing byte hashes.

| Structural measure | 1,000 output | 5,000 output |
| --- | --- | --- |
| Repeated native rational occurrences | 7,672 | 37,802 |
| Numerator decimal digits | 2,969,731 | 91,288,765 |
| Denominator decimal digits | 2,956,314 | 91,216,240 |
| Maximum digits in a numeric component | 2,982 | 16,112 |

At 5,000 observations, decimal rational digits alone occupy approximately **97.8%** of native bytes. At 1,000, `immutable_lifecycle_records` occupies 4,214,860 bytes and `closed_trade_records` 2,325,703 bytes: together approximately **96.6%**. These are structural byte counts on invented outputs, not real trades or PnL.

## Six sources of cost

| Cost | Required native content / avoidable work |
| --- | --- |
| A — exact operands | Numerator/denominator bit lengths grow with index; even one tick followed by constant prices retains nonconstant exact fractions. Arithmetic and decimal rendering cost depend on those bits. |
| B — immutable provenance | Confirmation/EMA/MACD/risk/entry ancestry is repeated by the frozen records. Required output repetitions cannot be replaced with aliases. Internal references may be shared. |
| C — serialization | Sorted compact UTF-8 canonical JSON plus LF has a unique byte sequence for fixed fields/values. Streaming reduces buffers, not its byte count. |
| D — history | Actual-bar marks and complete required lifecycle/trade/terminal records cannot be truncated. Disk-backed versions may reduce RAM if final ordering/statuses remain identical. |
| E — materialization | Full typed snapshots, recursively rebuilt native dictionaries/lists, whole text strings and UTF-8 byte copies create avoidable simultaneous memory use. |
| F — validation | Candidate digest/schema, identity-projection digest, then frozen complete canonical/schema/provenance validation repeat passes. The measured combined validation dominates the old dense runtime; individual operation costs remain unmeasured. |

For parser-valid immutable stock bars, the old/repaired guard follows the same valid path. Native fields/values therefore remain equal except the permitted fixed-width identity/digest strings. Their lengths remain 64 hex characters. Native byte length is invariant; this is a mathematical statement, **not** a fresh timing/memory benchmark.

## Streaming assessment and output limit

A schema-preserving candidate design could spool immutable versions with deterministic latest-record indexes, lazily iterate final native fields in frozen order, and use two streaming passes to compute the omitted-field payload digest and then emit the final digest-bearing JSON. A new exact recovery validator would need to preserve every reference schema/provenance/error rule and be differentially proved, replacing repeated whole-tree materialization without modifying the frozen validator.

That design is an **unimplemented, unproved option**. Cross-record joins, latest terminal states, ordering, exact integer decoding and validation require complete proofs. No symbolic rational, reference alias, omitted field, deduplicated required record, float/scientific-notation approximation or compressed-size substitution is permitted.

For a fixed unchanged native result, **byte-size reduction is impossible**: the canonical bytes are fixed. Caching, sharing and disk streaming may reduce work/RAM but still emit all repeated numeric text. A compressed archive is a backup artifact, never native JSON or evidence that the native cap was met.

## 89,841-observation feasibility

The following remain **conditional ESTIMATES** from old-source dense synthetic measurements, not real dataset measurements:

| Resource | ESTIMATE |
| --- | --- |
| Wall time | 10.1–182.3 hours |
| Peak memory | 9.87–177.30 GB |
| Complete native output | 60.27 GB |
| Serialization | 404–7,257 seconds |

Frozen caps remain **4,294,967,296 bytes memory** and **8,589,934,592 native output bytes**. The dense estimates exceed those limits. Real event density/cancellation and exact real output size remain UNKNOWN; no RAW was opened to determine them. No 89,841-observation completion/capacity/headroom proof exists. **EXACT_NATIVE_OUTPUT_FEASIBLE = NOT_PROVEN**.

## Options requiring AGIcoreManager decision

| Option | Decision/proof still required |
| --- | --- |
| A | A demonstrably more efficient exact engine retaining all frozen output bytes, with complete validation and resource feasibility proofs. Memory savings alone do not establish native output feasibility. |
| B | A separately precommitted explicit evidence/storage/result-contract change and corresponding new hash/equivalence authority. Not authorized here. |
| C | A independently demonstrated durable execution environment plus any necessary explicit infrastructure-limit amendment. A larger host alone does not waive the native output cap. |
| D | An explicit decision to terminate the present recovery path while retaining all scientific evidence. Not selected automatically. |

**No option is selected or claimed feasible.**

## Preservation and execution boundary

The original claim's SHA/371-byte size/mtime are unchanged; original failure evidence and all frozen strategy/protocol/lineage/threshold hashes remain unchanged. Original real invocations = **1**. Recovery invocations = **0**. No real authorization, claim, executable run registration, DEVELOPMENT/OOS read, broker or paper order was created. REAL_PNL and DEVELOPMENT_VERDICT remain **NOT_AVAILABLE**.

**NEXT: AGICOREMANAGER_DECISION_REQUIRED_ON_EXACT_NATIVE_EVIDENCE_RESOURCE_FEASIBILITY_OPTIONS_A_B_C_D.** No real recovery, full scalability run or execution-readiness gate begins automatically.
