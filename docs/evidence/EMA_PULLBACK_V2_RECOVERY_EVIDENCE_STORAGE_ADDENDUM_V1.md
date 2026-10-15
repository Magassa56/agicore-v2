# V2 recovery evidence storage addendum V1

**PASS_PRECOMMITTED — documentary design only.** Option B is selected for design.
The corrected recovery implementation remains **BLOCKED_TECHNICAL_FEASIBILITY**.
Storage reconstruction, independent verification and resource compliance have not
been implemented or demonstrated by this addendum. No real recovery is authorized.

Canonical JSON SHA-256:
`9f0752d90f8cec746addcb97ded86664f9739e727951d47d9a04eeb29243b019`.

The JSON is the normative versioned contract. It uses sorted compact UTF-8 JSON,
no floats or nonfinite numbers, and one final LF. Its digest is published here,
in current state and in documentary tests, never inside its own hashed payload.

## Preserved work and authority

This gate follows the explicit 2026-10-14 AGIcoreManager attachment, SHA-256
`102fedefd0b47998eb430b2f22501f46c8c7c212ead8cc027c09d889662692bc`.
Verified remote main/base: `8eafe91c434468ead9c57731775ad186c9733751`.
The local `main` ref was stale and was not changed; a separate documentary
worktree was created from the verified remote commit.

The existing implementation branch is preserved:
`feature/ema-pullback-v2-recovery-optimized-engine-v1`.

| Preservation item | Identity |
| --- | --- |
| Local WIP commit | `273579e3643de5bce6d66f75524b3179972d3acc` |
| Published WIP commit | `f40445911d3b8c8599c0228d1342fdba0a4aecff` |
| Identical Git tree | `9283af6eeb9458913681cd1b615f82baf87ff5f4` |
| Corrected candidate source | `854a6cbe7b89f3c6f0e9f49a8a5095745baf20693c2e89b115dfcadbfacbdf56` |
| Unapproved source closure | `a9954c13d1fd39b52ce4283f47f745c09c4bbcb145707a62ecd09bc2d264f3cf` |
| Semantic repair/triage evidence | `e728ed5cd3fbde38f1284fd8e2af7cc2ffafbfcf99fe977599cb264263aa45ef` |

The terminal had no Git push credentials. The GitHub connector published the
exact same tree with the required WIP message; author/committer metadata gives
the remote commit a different identity. Neither local history nor prior files
were rewritten. No implementation PR was created. The JSON inventories all 21
preexisting changed/untracked files by path, size and SHA: 20 entered the WIP;
the original 371-byte claim stayed untracked at its original path, with SHA
`d2eb78fb5a1b97e71fcc323b71da216449b35e4298729a26d6d052f4f26f00f4`.
No RAW, OOS file, credential, temporary process file or large benchmark output
entered the commit. Existing external proof archives remain separate and bound
by their previous hashes. Historical blocked documents retain their old bytes
and statements as historical snapshots, not current approval.

The 2026-10-15 preservation recheck found the local blocked-proof ZIP incomplete:
97,961,984 bytes, SHA `d04df19467b298ab35b15df0009e79e4383bd829befa0691afb274f0d9ed5e15`.
Its cause is unknown. These bytes were preserved without overwrite. A separate
copy of the original durable archive was retrieved and independently hashed:
161,219,941 bytes, SHA `3f42cdd83d5fe2a12232e8acd10cf581f20515485df91e44de9a5d25ac517980`,
exactly matching the original persistence receipt. The incomplete local bytes
are an exact prefix of that complete archive. The JSON records both paths and
identities; no proof archive was regenerated and no benchmark was rerun. All 21
WIP inventory files and the original claim still match their recorded identities.

Prior recovery protocol:
`a0588f0df41f409456330553de5fb9720bce4297676b0bc85137edd64ebd6db4`.
Architecture addendum:
`b36c1631308ea746a66d0c2312ad50796725957eef0e9e60d52a26c771bd3cc8`.
The original strategy manifest, DEVELOPMENT protocol, lineage, result schema,
screening source and all 16 frozen reference files remain unchanged and hash-bound.

The invalid Close correction has 22 focused passing tests. There are 63 bounded
native cases compared twice, 126 exact receipts. The bulk 168-test invocation
lacks a terminal summary: **complete full-suite PASS is not certified** for the
WIP implementation. Documentary CI on this separate branch does not certify it.

## Four separate contracts

1. **Strategy:** preserve every frozen predicate, exact recurrence, invalid-input
   contract, causal field restriction, transition, risk decision, fill and cost.
2. **Metrics/screening:** preserve the frozen metric, segment and verdict contracts.
   No replacement thresholds or alternate screening are introduced.
3. **Logical native evidence:** retain every field and ordered record of the
   original result, including repeated nested provenance and complete rational
   numerators/denominators. No reduced schema is represented as equivalent.
4. **Physical storage:** propose a separate versioned lossless bundle and a
   convenience decision summary. Neither wrapper is the original native schema.

## Explicit exception, with no automatic activation

The proposed exception changes physical delivery from one persisted monolithic
native JSON file to immutable shards that reconstruct that file exactly. It also
proposes applying the unchanged **8 GiB** ceiling to the complete physical evidence
workspace, including temporary files, rather than to the length of the decoded
logical stream. This is a **governance change in cap interpretation**, not an
optimization that already satisfies the former native-byte cap.

The old 8 GiB native-byte interpretation still applies until explicit activation.
Activation requires this merged precommit, separately authorized synthetic proof,
an independently verified storage/validator implementation, complete recovery and
resource acceptance, explicit manager acceptance of physical cap accounting,
final source/run registration, readiness, and separate execution authorization.
Every other parent requirement remains binding. There is no exception for logical
omission, symbolic native placeholders, numerical tolerances, trading changes,
additional attempts or unmeasured resource claims.

The 4 GiB memory and 8 GiB storage numbers do not change. A larger environment or
a larger cap would require a different, separately approved amendment.

## Two evidence layers

**Layer 1: decision summary.** A small canonical JSON projects the complete native
identity, dataset bounds/role, all metrics, all three segment objects, failed
criteria, verdict and next gate. It includes exact realized/unrealized values,
fees, diagnostic slippage, counts, PF, drawdown and losing streak. Extra wrapper
fields bind the complete source closure, verifier closure, storage addendum,
bundle-manifest SHA and complete logical-native file SHA/size.

The summary is never sufficient on its own for an authoritative verdict. It is
accepted only after every detailed audit record is recoverable and independently
reconciled. No actual summary or performance values are generated in this gate.

**Layer 2: complete audit.** The native-result stream contains every byte required
by the original schema: all lifecycle arrays, closed/open trades, full provenance,
marks, metrics, segments and diagnostics. Physical sharing can reference an
identical stored chunk more than once, but cannot remove repeated logical records
or nested values. Exact native rationals remain fully decoded integer tokens.

A separate additive `mark_source_witnesses` stream records one source-bound Close
per actual observation, with index, UTC timestamp, original decimal text, exact
rational Close, input-row byte offset/size/SHA. The original native mark schema
contains equities but not its marking Close; without this witness, an independent
verifier could only check the arithmetic identity of reported marks. This sidecar
does not alter the native result. In a separately authorized verification gate,
each witness must be compared to the immutable source row/RAW identity. A hash of
an unverified claimed price is not proof of origin. Missing source verification
leaves mark provenance INCOMPLETE.

Producer staging may use an append-only immutable version journal and disk-backed
indexes. Final iterators must reproduce the original final-record selection and
order exactly. Journals and intermediate versions are operational evidence, not
a substitute for the required native arrays. Source observations remain unchanged:
no session filter, no removal of the July 4 row, no repair of the 71 gaps, and no
synthetic observations.

## Concrete physical profile

Profile: `EXACT_NATIVE_BYTE_SHARDS_DEFLATE_V1`.

- Split each canonical byte stream at deterministic **1,048,576-byte** offsets.
  Every nonfinal shard has that decoded size; the final shard is nonempty and no
  larger. Chunks may split UTF-8, JSON records or large integer tokens.
- Independently compress each chunk with raw DEFLATE: level 9, window bits -15,
  memory level 8, default strategy, no metadata headers. Use identity encoding
  if compressed size is greater than or equal to decoded size. This decision is
  about byte lengths only; no trading content or performance is examined.
- Bind exact codec/runtime versions and source/binary identities before future
  proof. Cross-version compressed-byte identity and any compression ratio are
  unproven. These settings are an initial storage convention, not measured tuning.
- Address immutable objects as
  `objects/<first-two-hash-characters>/<stored-sha256>.blob`.
- The ordered manifest binds every ordinal, decoded offset/length/SHA, codec,
  stored length/SHA, stream size/SHA and required logical record count.
  Missing, reordered, conflicting, truncated or unbound data fails closed.

The manifest is canonical sorted compact UTF-8 JSON plus LF. Its ordered SHA-256
commitment supplies integrity; an unordered set of hashes cannot prove order or
completeness. All referenced bytes must exist and remain retrievable. Paths are
hash-derived regular files; traversal, symlink/hardlink tricks and overwriting
existing content are forbidden. Reuse of identical objects requires verification.

## Exact reconstruction and hash definitions

For a finite canonical byte sequence B and chunk width m, the intervals
`[j*m, min((j+1)*m, len(B)))` partition B. Concatenating their exact decoded bytes
returns B. A lossless codec preserves this identity. This is an algebraic
partition argument, **not** a producer/verifier implementation or feasibility
proof.

Reconstruction verifies bindings, all manifest descriptors, stored/decoded hashes,
lengths and codec bounds, then streams every decoded chunk in ordinal order into
an incremental hash and JSON-validation sink. It does not rewrite values. The
sink must validate canonical encoding, unique sorted keys, exact integer/rational
tokens, array order, schema, cross-field invariants and complete EOF/final LF.
Decoded-size limits and rejection of trailing compressed bytes prevent hidden
extra data and unbounded expansion.

Two native hashes are intentionally distinct:

| Hash | Exact preimage |
| --- | --- |
| Existing `output_sha256` | Canonical native object with only the top-level `output_sha256` field omitted, including final LF |
| `logical_native_file_sha256` | Full canonical native JSON including `output_sha256` and final LF |

The omitted-field payload must be generated with an exact streaming parser and
canonical emitter, never regex deletion. Both definitions remain unchanged through
storage. **No identity normalization is permitted in a storage round trip.** The
separate reference-versus-new-engine test may retain only its previously approved
two-field normalization; it cannot excuse a storage difference.

Commitments are acyclic: objects → manifest → summary → independent verification
receipt → completion seal. No artifact contains its own hash or a hash of a later
artifact. The final seal binds successful verification, both native hashes, sizes,
counts and durable artifact identities. A START/END receipt or a summary without
complete audit bytes never means COMPLETE.

An expanded monolithic file need not be persisted, but **all its logical bytes
must be reconstructible and actually decoded/verified**. Hashing symbolic nodes
instead of generating required digits is not reconstruction.

## Independent verification proposal

The future verifier is separate from strategy execution. It does not call the
runner or use cached summary aggregates as an oracle. Its source closure and
storage codec dependencies are independently registered. It must:

1. Verify every shard, manifest, canonical stream, schema and provenance join.
2. Reconcile all lifecycle counts, directions, quantities, fills, terminal states,
   closed/open records and original historical ordering.
3. Independently derive effective fills, actual fees and net closed-trade PnL
   from base fills/actions/quantities under the frozen cost contract. Slippage is
   embedded once; its diagnostic cost is never subtracted again.
4. Recompute each actual-bar mark from closed net equity plus current open net
   unrealized PnL using the source Close witness, effective entry and paid entry
   fee. No hypothetical exit costs or final liquidation. Start drawdown peak at 0.
5. Recompute exact average/median, PF including ZERO/POSITIVE_INFINITY, win rate,
   zero-reset loss streak and all three equal-elapsed-time segments. Segment
   boundaries use exact rational microseconds and EXIT-fill attribution.
6. Apply frozen sample-first screening and compare every summary field, failed
   criterion and next gate with the independently audited native result.

Independent schema/metric validation must itself be compared exactly with the
frozen authority on predeclared synthetic cases. Large integer parsing, provenance
joins and median calculation may need bounded buffers and external storage; no
constant-memory claim is made. Missing source witnesses, missing audit bytes or
failed reconciliation prevents an authoritative result and never authorizes a
second strategy execution.

## Resources and alternatives

The earlier dense synthetic extrapolation remains conditional: 10.1–182.3 hours,
9.87–177.30 decimal GB memory, 60.27 decimal GB logical output and 404–7257 seconds
serialization for 89,841 observations. These are not actual DEVELOPMENT results
and are not measurements of this storage proposal.

| Option | Evidence and limitation | Selection |
| --- | --- | --- |
| A: monolithic native with better streaming | May reduce copies/RAM; fixed canonical bytes remain unchanged | Not selected |
| B: logical-native lossless bundle | Exact partition identity is defensible; compression, independent verifier and resource fit remain unmeasured | Design selected |
| C: larger durable environment | Could provide capacity; cannot silently waive current caps | Requires separate decision |
| D: terminate recovery path | Preserves research without another execution | Requires separate decision |

No compression ratio is assumed. A 60 GB logical result may still exceed 8 GiB
physically. Final compressed object size alone is insufficient: staging journals,
indexes, witnesses, logs, checkpoints, partial writes, verification spills and
coexisting copies all count toward peak storage across every output/temp root.
Track both logical lengths and allocated bytes conservatively, including directory
metadata; no sparse-file or hardlink accounting shortcut. The immutable input and
read-only code are outside newly produced output, but consume host capacity.

The **4 GiB** memory bound covers the complete supervised process tree, including
producer, serializer and verifier. Streaming avoids a requirement to materialize
60 GB at once, but does not prove that live exact operands, indexes, validation,
output or runtime fit. Every decoded logical byte still costs work. Codec ratio,
temporary storage, revised peak memory and independent verification cost are
**UNKNOWN**. Existing mandatory resource tests and conservative host/headroom
requirements are not waived. No large benchmark is run by this gate.

## Future synthetic proof and stopping rule

The next gate must separately authorize and predeclare generator/source hashes,
seeds, scenario inventory, counts, resource limits, commands, codec versions and
the independent oracle. It must cover all required native fields and bounded
LONG/SHORT lifecycle cases, large exact rationals, null/PF edge cases, open trades,
gaps/off-session rows and chunk-boundary cases. Each completed fixture requires:

1. Frozen reference validation before storage.
2. Proposed bundle generation.
3. Independent complete reconstruction.
4. Schema and cross-field validation.
5. Exact canonical-byte and both native-hash equality.
6. Independent audit-to-summary accounting, marks, segment and screening checks.

Repeat in fresh processes and retain every failed fixture. Tamper tests must
reject missing/reordered/truncated shards, wrong offsets/hashes/codecs, excessive
expansion, extra compressed bytes, duplicate keys, missing LF, changed rational
digits, omitted records, changed provenance, incorrect witnesses/summary/verdict,
wrong source/run bindings and incomplete outputs labeled COMPLETE.

**SYNTHETIC_STORAGE_PROOF = NOT_RUN.** This gate runs documentary/schema tests and
existing repository CI only. A failed reconstruction must yield
`BLOCKED_STORAGE_CONTRACT_EQUIVALENCE`; missing cap/capacity proof keeps
`BLOCKED_TECHNICAL_FEASIBILITY`. No automatic alternative, limit relaxation,
parameter change, execution authorization or retry follows.

## Resulting governance state

```text
RECOVERY_EVIDENCE_STORAGE_ADDENDUM = PASS_PRECOMMITTED
RECOVERY_SEMANTIC_REPAIR = PASS_FOR_COMPLETED_SYNTHETIC_CASES
COMPLETE_RECOVERY_IMPLEMENTATION = BLOCKED_TECHNICAL_FEASIBILITY
RESOURCE_FEASIBILITY = NOT_PROVEN
ORIGINAL_INVOCATIONS = 1
RECOVERY_INVOCATIONS = 0
RECOVERY_RUN_ID = NOT_REGISTERED
REAL_RECOVERY_EXECUTION = NOT_EXECUTED
DEVELOPMENT_VERDICT = NOT_AVAILABLE
OOS_ACCESSED = FALSE
NEXT = EMA_PULLBACK_V2_RECOVERY_STORAGE_SYNTHETIC_PROOF_REQUIRED
```

The failed original result remains FAILED_NO_RESULT with verdict NOT_AVAILABLE
and unknown failure cause/progress. This addendum cannot retroactively make it
successful. The four-field run identity is unchanged; future storage/verifier
closure and addendum bindings belong in separate authorization/evidence. No new
run ID, authorization artifact or recovery claim is created now. Stop after the
documentary publication; the next gate requires a new AGIcoreManager decision.
