"""Precommitted UTC End-of-Bar window filter; no strategy or replay imports.

Real execution belongs to the separate TRANSFORMATION_EXECUTION gate. The CLI
defaults to verifying the protocol only. Tests transform invented byte strings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path

from tools.ema_pullback_v2_development_protocol import (
    ProtocolError,
    canonical_bytes,
    verify_protocol,
)

SOURCE_PATH = "tools/ema_pullback_v2_dataset_transformation.py"
PROTOCOL_PATH = "docs/evidence/EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION.json"
EXECUTION_GATE = "EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION_EXECUTION"
TIMESTAMP_SEMANTICS = "NINJATRADER_END_OF_BAR"
TIMESTAMP_TIMEZONE = "UTC"


class TransformationError(ValueError):
    """Fail closed on any identity, semantics, structure or count mismatch."""


def _utc(value: datetime) -> None:
    if not isinstance(value, datetime) or value.utcoffset() != timedelta(0):
        raise TransformationError("timezone-aware UTC timestamps required")
    if value.second or value.microsecond:
        raise TransformationError("one-minute timestamp alignment required")


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class TimestampWindow:
    """Inclusive UTC End-of-Bar boundaries; the only row-selection predicate."""

    first: datetime
    last: datetime

    def __post_init__(self) -> None:
        _utc(self.first)
        _utc(self.last)
        if self.first > self.last:
            raise TransformationError("reversed timestamp window")


@dataclass(frozen=True)
class ParentExpectation:
    """Exact byte identity and audit invariants, never performance metrics."""

    sha256: str
    size_bytes: int
    rows: int
    first: datetime
    last: datetime
    removed_before: int
    retained: int
    removed_after: int

    def __post_init__(self) -> None:
        if re.fullmatch(r"[0-9a-f]{64}", self.sha256) is None:
            raise TransformationError("exact lowercase parent SHA-256 required")
        _utc(self.first)
        _utc(self.last)
        if self.first > self.last:
            raise TransformationError("reversed parent timestamp bounds")
        for value in (
            self.size_bytes,
            self.rows,
            self.removed_before,
            self.retained,
            self.removed_after,
        ):
            if type(value) is not int or value < 0:
                raise TransformationError("nonnegative integer audit counts required")
        if not self.size_bytes or not self.rows:
            raise TransformationError("nonempty parent required")
        if self.removed_before + self.retained + self.removed_after != self.rows:
            raise TransformationError("row partition does not reconcile")


PRECOMMITTED_WINDOW = TimestampWindow(
    datetime(2026, 6, 18, 22, 1, tzinfo=UTC),
    datetime(2026, 9, 18, 13, 30, tzinfo=UTC),
)
PRECOMMITTED_PARENT = ParentExpectation(
    "6e20320e06184673c745c1069753c77151fdccd4505b863210f6d63f3ff5fcd5",
    5416523,
    101962,
    datetime(2026, 6, 7, 22, 1, tzinfo=UTC),
    datetime(2026, 9, 18, 13, 31, tzinfo=UTC),
    12120,
    89841,
    1,
)


def precommitted_predicate() -> dict:
    """Return a fresh canonical description of the one approved predicate."""
    return {
        "field": "timestamp",
        "timezone": TIMESTAMP_TIMEZONE,
        "semantics": TIMESTAMP_SEMANTICS,
        "lower_operator": ">=",
        "lower_utc": _iso(PRECOMMITTED_WINDOW.first),
        "upper_operator": "<=",
        "upper_utc": _iso(PRECOMMITTED_WINDOW.last),
        "combination": "AND",
        "additional_predicates": [],
    }


def precommitted_parent() -> dict:
    """Return a fresh description of the immutable production input identity."""
    parent = PRECOMMITTED_PARENT
    return {
        "filename": "MNQ 09-26.Last.txt",
        "sha256": parent.sha256,
        "size_bytes": parent.size_bytes,
        "data_rows": parent.rows,
        "first_timestamp_utc": _iso(parent.first),
        "last_timestamp_utc": _iso(parent.last),
        "timestamp_semantics": TIMESTAMP_SEMANTICS,
        "timestamp_timezone": TIMESTAMP_TIMEZONE,
    }


def precommitted_counts() -> dict:
    """Return the frozen expected partition counts without reading any data."""
    parent = PRECOMMITTED_PARENT
    return {
        "parent_rows": parent.rows,
        "rows_removed_before_window": parent.removed_before,
        "rows_removed_after_window": parent.removed_after,
        "expected_retained_rows": parent.retained,
    }


@dataclass(frozen=True)
class ParentAudit:
    """Successful input validation; an invalid row aborts rather than being removed."""

    parent_sha256: str
    parent_size_bytes: int
    parent_rows: int
    first_timestamp_utc: str
    last_timestamp_utc: str
    removed_before: int
    retained: int
    removed_after: int
    gap_intervals_over_one_minute: int
    structural_integrity: str = "PASS"


@dataclass(frozen=True)
class TransformationResult:
    """Exact retained original line bytes and their immutable audit provenance."""

    output_bytes: bytes
    output_sha256: str
    audit: ParentAudit
    changed_retained_rows: int = 0


def _exact_number(value: bytes, row: int) -> Fraction:
    try:
        text = value.decode("ascii")
        if not text or text.strip() != text or "_" in text:
            raise ValueError("malformed numeric literal")
        number = Decimal(text)
        if not number.is_finite():
            raise TransformationError(f"nonfinite OHLCV on row {row}")
        return Fraction(number)
    except (UnicodeError, InvalidOperation, ValueError) as exc:
        raise TransformationError(f"invalid OHLCV on row {row}") from exc


def _parse_row(line: bytes, row: int) -> datetime:
    body = line[:-2] if line.endswith(b"\r\n") else line[:-1] if line.endswith(b"\n") else line
    if b"\r" in body or b"\n" in body:
        raise TransformationError(f"malformed line terminator on row {row}")
    fields = body.split(b";")
    if len(fields) != 6 or re.fullmatch(rb"[0-9]{8} [0-9]{6}", fields[0]) is None:
        raise TransformationError(f"malformed row {row}")
    try:
        at = datetime.strptime(fields[0].decode("ascii"), "%Y%m%d %H%M%S").replace(tzinfo=UTC)
        _utc(at)
    except ValueError as exc:
        raise TransformationError(f"invalid timestamp on row {row}") from exc
    opened, high, low, close, volume = (_exact_number(value, row) for value in fields[1:])
    if high < max(opened, close) or low > min(opened, close) or high < low:
        raise TransformationError(f"invalid OHLC on row {row}")
    if volume < 0 or volume.denominator != 1:
        raise TransformationError(f"nonnegative integer volume required on row {row}")
    if any((price * 4).denominator != 1 for price in (opened, high, low, close)):
        raise TransformationError(f"off MNQ quarter-point tick grid on row {row}")
    return at


def _inspect(
    parent: bytes,
    expectation: ParentExpectation,
    window: TimestampWindow,
    timestamp_semantics: str,
    timestamp_timezone: str,
) -> tuple[ParentAudit, tuple[tuple[datetime, bytes], ...]]:
    if timestamp_semantics != TIMESTAMP_SEMANTICS or timestamp_timezone != TIMESTAMP_TIMEZONE:
        raise TransformationError("UTC NinjaTrader End-of-Bar evidence required")
    if type(parent) is not bytes or hashlib.sha256(parent).hexdigest() != expectation.sha256:
        raise TransformationError("parent SHA-256 mismatch")
    if len(parent) != expectation.size_bytes:
        raise TransformationError("parent byte size mismatch")
    lines = parent.splitlines(keepends=True)
    if len(lines) != expectation.rows:
        raise TransformationError("parent row count mismatch")
    parsed = []
    before = within = after = gaps = 0
    previous = None
    for row, line in enumerate(lines, 1):
        at = _parse_row(line, row)
        if previous is not None:
            if at <= previous:
                raise TransformationError(f"duplicate or non-chronological timestamp on row {row}")
            if at - previous > timedelta(minutes=1):
                gaps += 1
        previous = at
        parsed.append((at, line))
        if at < window.first:
            before += 1
        elif at > window.last:
            after += 1
        else:
            within += 1
    if parsed[0][0] != expectation.first or parsed[-1][0] != expectation.last:
        raise TransformationError("parent timestamp bounds mismatch")
    if (before, within, after) != (
        expectation.removed_before,
        expectation.retained,
        expectation.removed_after,
    ):
        raise TransformationError("before/retained/after row count mismatch")
    audit = ParentAudit(
        expectation.sha256,
        len(parent),
        len(lines),
        _iso(parsed[0][0]),
        _iso(parsed[-1][0]),
        before,
        within,
        after,
        gaps,
    )
    return audit, tuple(parsed)


def audit_parent_bytes(
    parent: bytes,
    *,
    expectation: ParentExpectation,
    window: TimestampWindow,
    timestamp_semantics: str,
    timestamp_timezone: str,
) -> ParentAudit:
    """Validate identity, every row and partition counts without constructing a subset."""
    return _inspect(parent, expectation, window, timestamp_semantics, timestamp_timezone)[0]


def transform_bytes(
    parent: bytes,
    *,
    expectation: ParentExpectation,
    window: TimestampWindow,
    timestamp_semantics: str,
    timestamp_timezone: str,
) -> TransformationResult:
    """After complete validation, keep iff the timestamp is in the inclusive window.

    No price/volume predicate selects rows. Invalid structure aborts the entire
    operation; valid retained lines are joined without decoding or reformatting.
    """
    audit, rows = _inspect(parent, expectation, window, timestamp_semantics, timestamp_timezone)
    output = b"".join(line for at, line in rows if window.first <= at <= window.last)
    return TransformationResult(output, hashlib.sha256(output).hexdigest(), audit)


@dataclass(frozen=True)
class VerifiedTransformationProtocol:
    """Verified immutable document bytes; callers receive fresh parsed metadata."""

    protocol_bytes: bytes
    protocol_sha256: str
    source_sha256: str

    def __post_init__(self) -> None:
        if type(self.protocol_bytes) is not bytes:
            raise TransformationError("immutable protocol bytes required")
        if hashlib.sha256(self.protocol_bytes).hexdigest() != self.protocol_sha256:
            raise TransformationError("immutable protocol SHA-256 mismatch")
        if re.fullmatch(r"[0-9a-f]{64}", self.source_sha256) is None:
            raise TransformationError("transformation source SHA-256 required")

    @property
    def document(self) -> dict:
        """Return an independent document copy, preserving the original bytes."""
        return json.loads(self.protocol_bytes)


def verify_transformation_protocol(
    protocol_bytes: bytes,
    *,
    claimed_sha256: str,
    source_bytes: bytes,
    strategy_manifest_bytes: bytes,
    development_protocol_bytes: bytes,
) -> VerifiedTransformationProtocol:
    """Verify the external protocol digest, source digest and every frozen binding."""
    if type(protocol_bytes) is not bytes or type(source_bytes) is not bytes:
        raise TransformationError("immutable protocol and source bytes required")
    if hashlib.sha256(protocol_bytes).hexdigest() != claimed_sha256:
        raise TransformationError("transformation protocol SHA-256 mismatch")
    try:
        document = json.loads(protocol_bytes)
        if canonical_bytes(document) != protocol_bytes:
            raise TransformationError("noncanonical transformation protocol")
        verify_protocol(
            development_protocol_bytes,
            strategy_manifest_bytes,
            claimed_protocol_sha256=document["development_protocol_sha256"],
            claimed_strategy_manifest_sha256=document["strategy_manifest_sha256"],
        )
        source_sha = hashlib.sha256(source_bytes).hexdigest()
        if document["transformation_source"] != {"path": SOURCE_PATH, "sha256": source_sha}:
            raise TransformationError("transformation source SHA-256 mismatch")
        if document["parent_raw"] != precommitted_parent():
            raise TransformationError("frozen parent identity or semantics mismatch")
        if document["timestamp_predicate"] != precommitted_predicate():
            raise TransformationError("frozen timestamp predicate mismatch")
        if document["expected_row_counts"] != precommitted_counts():
            raise TransformationError("frozen expected row counts mismatch")
        if document["retained_row_policy"] != "ORIGINAL_LINE_BYTES_INCLUDING_TERMINATOR":
            raise TransformationError("retained row preservation policy mismatch")
        if document["phase"] != "EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION":
            raise TransformationError("wrong transformation phase")
        if document["status"] != "PASS_PRECOMMITTED":
            raise TransformationError("protocol has not passed precommitment")
    except (KeyError, TypeError, json.JSONDecodeError, ProtocolError) as exc:
        raise TransformationError("invalid protocol or strategy/development binding") from exc
    return VerifiedTransformationProtocol(protocol_bytes, claimed_sha256, source_sha)


def main(argv: list[str] | None = None) -> int:
    """Verify by default; real file execution requires the separately authorized gate.

    The explicit gate flag records caller intent; it is not an authorization by
    itself. This gate's documentation forbids calling the execution branch now.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--protocol", type=Path, default=Path(PROTOCOL_PATH))
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--execution-gate")
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.execute:
            if args.execution_gate != EXECUTION_GATE or args.input is None or args.output is None:
                raise TransformationError("separate execution gate and input/output required")
        elif args.execution_gate is not None or args.input is not None or args.output is not None:
            raise TransformationError("default verification may not read or transform a RAW")
        root = Path(__file__).resolve().parents[1]
        protocol = verify_transformation_protocol(
            args.protocol.read_bytes(),
            claimed_sha256=args.protocol_sha256,
            source_bytes=Path(__file__).read_bytes(),
            strategy_manifest_bytes=(
                root / "docs/evidence/EMA_PULLBACK_V2_REGIME_GATED_BASELINE_MANIFEST.json"
            ).read_bytes(),
            development_protocol_bytes=(
                root / "docs/evidence/EMA_PULLBACK_V2_DEVELOPMENT_PROTOCOL.json"
            ).read_bytes(),
        )
        if not args.execute:
            sys.stdout.buffer.write(
                canonical_bytes(
                    {
                        "status": "VERIFIED_PRECOMMITMENT_ONLY",
                        "protocol_sha256": protocol.protocol_sha256,
                        "real_transformation": "NOT_EXECUTED",
                    }
                )
            )
            return 0
        incoming, outgoing = args.input.resolve(), args.output.resolve()
        forbidden = (root / "data").resolve()
        if any(path == forbidden or forbidden in path.parents for path in (incoming, outgoing)):
            raise TransformationError("repository data/ access forbidden")
        if incoming == outgoing or outgoing.exists():
            raise TransformationError("output must be new and may not overwrite the parent")
        parent = incoming.read_bytes()
        result = transform_bytes(
            parent,
            expectation=PRECOMMITTED_PARENT,
            window=PRECOMMITTED_WINDOW,
            timestamp_semantics=TIMESTAMP_SEMANTICS,
            timestamp_timezone=TIMESTAMP_TIMEZONE,
        )
        if incoming.read_bytes() != parent:
            raise TransformationError("parent changed during execution")
        with outgoing.open("xb") as stream:
            stream.write(result.output_bytes)
        sys.stdout.buffer.write(
            canonical_bytes(
                {
                    "execution_gate": args.execution_gate,
                    "protocol_sha256": protocol.protocol_sha256,
                    "transformation_source_sha256": protocol.source_sha256,
                    "audit": asdict(result.audit),
                    "output_sha256": result.output_sha256,
                    "output_size_bytes": len(result.output_bytes),
                    "changed_retained_rows": result.changed_retained_rows,
                }
            )
        )
        return 0
    except (TransformationError, OSError) as exc:
        print(f"FAIL_CLOSED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
