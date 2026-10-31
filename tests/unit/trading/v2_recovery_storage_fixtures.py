"""Predeclared invented inputs; no market file, result selection or optimization."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from datetime import UTC, datetime, timedelta

from agicore.trading.regime_context_v2 import RegimeDirection
from tests.unit.trading.test_ema_pullback_regime_gated_baseline_v2 import (
    SCENARIOS,
    _scenario,
)

CHUNK_SIZE = 1_048_576
NATIVE_IDS = tuple(f"{name}_{side}" for name in SCENARIOS for side in ("LONG", "SHORT")) + (
    "constant_control", "off_session_LONG", "off_session_SHORT",
    "dense_gapped_LONG", "dense_gapped_SHORT",
)
BYTE_IDS = (
    "chunk_minus_one", "chunk_exact", "chunk_plus_one", "repeated_chunks",
    "incompressible", "utf8_crossing", "integer_crossing",
)
TAMPER_IDS = (
    "MISSING_SHARD", "REORDERED_SHARDS", "DUPLICATE_ORDINAL", "OVERLAPPING_OFFSET",
    "TRUNCATED_COMPRESSED_OBJECT", "TRUNCATED_FINAL_RECORD", "WRONG_STORED_HASH",
    "WRONG_DECODED_HASH", "WRONG_DECODED_SIZE", "WRONG_CODEC_VERSION",
    "DECOMPRESSION_OVER_LIMIT", "TRAILING_COMPRESSED_BYTES", "DUPLICATE_JSON_KEYS",
    "NONCANONICAL_JSON", "MISSING_FINAL_LF", "OMITTED_LIFECYCLE_RECORD",
    "CHANGED_RATIONAL_DIGIT", "SWAPPED_TRADE_PROVENANCE", "SUMMARY_METRIC_MISMATCH",
    "SUMMARY_VERDICT_MISMATCH", "SOURCE_CLOSE_WITNESS_MISMATCH", "WRONG_RUN_IDENTITY",
    "WRONG_SOURCE_CLOSURE", "MISSING_COMPLETION_SEAL", "PARTIAL_JOURNAL_LABELED_COMPLETE",
)
STATISTICS_CASES = ((), (0,), (-1, -2, 0, -3), (1, 2, 3), (-1, -2), (3, -2, 0, 5))


def synthetic_raw(fixture_id: str) -> bytes:
    """Generate only the declared literal scenarios inherited from frozen unit tests."""
    if fixture_id not in NATIVE_IDS:
        raise ValueError("unregistered invented fixture")
    if fixture_id == "constant_control":
        start = datetime(2099, 1, 1, tzinfo=UTC)
        return b"".join(
            (f"{start + timedelta(minutes=i):%Y%m%d %H%M%S};20000;20000.25;"
             "19999.75;20000;100\n").encode("ascii") for i in range(36)
        )
    name, side = fixture_id.rsplit("_", 1)
    direction = RegimeDirection(side)
    special = name in ("off_session", "dense_gapped")
    bars = list(_scenario("impulse_profit" if special else name, direction).values())
    if name == "off_session":
        start = datetime(2099, 1, 3, 12, tzinfo=UTC)
        bars = [replace(b, timestamp_utc=start + timedelta(minutes=i)) for i, b in enumerate(bars)]
    if name == "dense_gapped":
        first = bars[0].timestamp_utc
        count = len(bars)
        bars = [replace(bars[i % count], timestamp_utc=first + timedelta(
            minutes=i + (15 if i >= count else 0))) for i in range(count * 2)]
    return b"".join(
        (";".join((b.timestamp_utc.strftime("%Y%m%d %H%M%S"),
                    *(str(getattr(b, name)) for name in ("open", "high", "low", "close")),
                    str(b.volume))) + "\n").encode("ascii") for b in bars
    )


def synthetic_byte_stream(fixture_id: str) -> bytes:
    """Codec-only streams are explicitly distinct from valid native result fixtures."""
    if fixture_id == "chunk_minus_one":
        return b"a" * (CHUNK_SIZE - 1)
    if fixture_id == "chunk_exact":
        return b"b" * CHUNK_SIZE
    if fixture_id == "chunk_plus_one":
        return b"c" * (CHUNK_SIZE + 1)
    if fixture_id == "repeated_chunks":
        return b"d" * (CHUNK_SIZE * 2 + 1)
    if fixture_id == "incompressible":
        return b"".join(hashlib.sha256(b"storage-v1-counter:" + i.to_bytes(8, "big")).digest()
                        for i in range(CHUNK_SIZE // 32))
    if fixture_id == "utf8_crossing":
        return b'{"a":"' + b"x" * (CHUNK_SIZE - 8) + "é🙂".encode() + b'"}\n'
    if fixture_id == "integer_crossing":
        return b'{"a":"' + b"x" * (CHUNK_SIZE - 32) + b'","b":' + b"7" * 8192 + b"}\n"
    raise ValueError("unregistered codec fixture")
