# MNQ 06-26 development evidence

## Verdict

- Phase: `DATASET_LINEAGE_MANIFEST_V1`
- Gate: `CLEAN_LINEAGE_SOURCE_EVIDENCE`
- Status: `BLOCKED_HUMAN_GATE`
- Authorized use: `BAR_ONLY_DEVELOPMENT`
- Exposure: `EXPOSED_DEVELOPMENT`
- OOS: `false`; the reserved OOS boundary was not opened or inspected.

The private source was inspected locally without publishing any market row or price. It is
structurally compatible with a one-minute OHLCV export, but the file contains no header,
instrument identifier or provenance metadata. Its filename and the supplied declaration do not
independently prove `MNQ 06-26`.

## Verified private-source facts

| Field | Verified value |
|---|---|
| Source filename | `MNQ 06-26.Last.txt` |
| SHA-256, stable on two reads | `46f2e42304573bd5e9a6c8c78a83a3cd655d493c9c1c0dc66fa2ed7406793b40` |
| Size | 2,265,516 bytes |
| Rows | 42,541 non-empty rows |
| Encoding / line endings | ASCII, CRLF, no BOM, final newline |
| Layout | Six semicolon-separated fields; no header |
| Timestamp format | `yyyyMMdd HHmmss`, without offset or zone |
| Timestamp coverage | `2026-04-29 22:01:00` through `2026-06-11 21:00:00` (source-naive) |
| Ordering | Strictly increasing; zero duplicate or out-of-order timestamps |
| Interval structure | 42,510 one-minute transitions and 30 larger gaps |
| Numeric structure | Zero parse failures; OHLC invariants passed; non-negative integral volume |
| Legacy hash search | Zero exact match in the available sanitized D003 manifest and current repository |

`OHLC_PRESENT = true` and `VOLUME_PRESENT = true` describe the observed six-field structure.
They do not prove provider semantics, trade source, execution quality, Bid/Ask, tick history or
Market Replay.

## Declared but not independently attested

The supplied instruction declares `MNQ`, `MNQ 06-26`, `Minute`, `Last`, `DEVELOPMENT` and
`DoNotMerge`. Its SHA-256 is
`b46d27aff83e3ef4337018b95cd2ec1aeb456709a65cd2e0c71725fb44c0e322`.
That instruction is a governance declaration, not hashed contract-identity evidence from the
export source.

## Missing source evidence

The contract cannot yet establish the actual provider, exact NinjaTrader version, UTC export
timestamp, contract identity linked to this exact source hash, bar timestamp semantics,
exported-file timezone/DST policy, Trading Hours template, holiday calendar, effective
`DoNotMerge` setting, rollover policy, or whether the current bytes are the untouched export.
Consequently no canonical `DatasetLineageManifest` was prepared and no structural validator PASS
is claimed.

## One human action

Provide one sanitized evidence bundle for this exact file/hash containing the original
full-resolution NinjaTrader screens for: Historical Data export (`MNQ 06-26`, Minute, Last),
Help/About (exact version), the data-provider connection, platform/export timezone, instrument
Merge Policy and Trading Hours template. In the same bundle, include a short export receipt that
binds those screens to the RAW SHA-256 and records UTC export time, bar timestamp semantics,
exported-file IANA timezone/DST policy, holiday calendar, OHLC/volume semantics and whether the
file was rewritten after export. Account identifiers and prices must be masked. After receipt,
AGIcore can hash the evidence files, populate the missing fields and rerun the fail-closed contract.

## Privacy and non-claims

The RAW file is not tracked by Git. This dossier contains no OHLCV row, price, secret, broker
credential or OOS datum. It does not validate a strategy, replay, execution quality, profitability,
paper trading or `V1_VALIDATED_OFFLINE_PAPER`.
