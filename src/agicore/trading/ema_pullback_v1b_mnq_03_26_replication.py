"""Fail-closed loader for the single precommitted MNQ 03-26 V1B replication.

The private RAW is verified before parsing. The replay delegates every strategy rule,
cost, fill, exit, and session decision to the already-frozen V1B implementation and
the shared deterministic runner. This module performs no network, broker, OOS, or
real-trading operation.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .ema_pullback_v1_mnq_development import (
    REPLICATION_DATASET_ROLE,
    DevelopmentVerdict,
)
from .ema_pullback_v1_mnq_development_replay import (
    DevelopmentReplayBar,
    DevelopmentReplayError,
    DevelopmentReplayResult,
    _run_bars,
    parse_ninjatrader_last_rows,
)
from .ema_pullback_v1a_mnq import evaluate_v1a_ema20_slope
from .ema_pullback_v1b_mnq import (
    VARIANT_ID,
    VARIANT_PROTOCOL_SHA256,
    v1b_entry_session_allows,
)

EXPERIMENT_ID = "EMA_PULLBACK_V1B_MNQ_CROSS_CONTRACT_REPLICATION_03_26"
REPLICATION_PROTOCOL_SHA256 = "c431c991c290f000bfdd9f39f01372ccfc05c963911e11534184d1ab95b07d37"
CLEAN_LINEAGE_MANIFEST_SHA256 = "b22371ac3be30952ae58f4b5a8a5d6261b688583bce31ed2dd6c958f7c4b7c80"
DATASET_ID = "mnq-03-26-minute-last-development-replication-2122722f-v1"
DATASET_ROLE = REPLICATION_DATASET_ROLE
SOURCE_RAW_FILENAME = "MNQ 03-26.Last.txt"
SOURCE_RAW_SHA256 = "2122722f25dbc865dad154905309b5e76d2190561ffc64acdaa955365ccb9efc"
EXPECTED_RAW_SIZE_BYTES = 3_946_060
EXPECTED_RAW_ROW_COUNT = 74_308
EXPECTED_FIRST_TIMESTAMP_UTC = datetime(2026, 1, 1, 1, 22, tzinfo=UTC)
EXPECTED_LAST_TIMESTAMP_UTC = datetime(2026, 3, 20, 13, 30, tzinfo=UTC)
RUNNER_ID = "EMA_PULLBACK_V1B_MNQ_03_26_REPLICATION_V1"
RUNNER_VERSION = "1.0"


@dataclass(frozen=True)
class VerifiedReplicationDataset:
    """Exact private replication dataset retained only in process memory."""

    bars: tuple[DevelopmentReplayBar, ...]
    source_raw_sha256: str
    source_size_bytes: int
    source_row_count: int
    dataset_id: str = DATASET_ID
    dataset_role: str = DATASET_ROLE
    oos_accessed: bool = False

    def __post_init__(self) -> None:
        if (
            self.source_raw_sha256 != SOURCE_RAW_SHA256
            or self.source_size_bytes != EXPECTED_RAW_SIZE_BYTES
            or self.source_row_count != EXPECTED_RAW_ROW_COUNT
            or self.dataset_id != DATASET_ID
            or self.dataset_role != DATASET_ROLE
            or self.oos_accessed is not False
        ):
            raise DevelopmentReplayError("MNQ 03-26 replication identity or boundary mismatch")
        if len(self.bars) != EXPECTED_RAW_ROW_COUNT:
            raise DevelopmentReplayError("MNQ 03-26 replication row count mismatch")
        if (
            self.bars[0].timestamp_utc != EXPECTED_FIRST_TIMESTAMP_UTC
            or self.bars[-1].timestamp_utc != EXPECTED_LAST_TIMESTAMP_UTC
        ):
            raise DevelopmentReplayError("MNQ 03-26 replication temporal bounds mismatch")


def load_preserved_replication_raw(path: str | Path) -> VerifiedReplicationDataset:
    """Verify the exact private RAW bytes before parsing the precommitted replication."""
    raw_path = Path(path)
    try:
        raw = raw_path.read_bytes()
    except OSError as exc:
        raise DevelopmentReplayError("preserved MNQ 03-26 replication RAW is unavailable") from exc
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SOURCE_RAW_SHA256:
        raise DevelopmentReplayError("preserved MNQ 03-26 replication RAW SHA-256 mismatch")
    if len(raw) != EXPECTED_RAW_SIZE_BYTES:
        raise DevelopmentReplayError("preserved MNQ 03-26 replication RAW size mismatch")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DevelopmentReplayError(
            "preserved MNQ 03-26 replication RAW encoding is invalid"
        ) from exc
    bars = parse_ninjatrader_last_rows(text)
    return VerifiedReplicationDataset(
        bars=bars,
        source_raw_sha256=digest,
        source_size_bytes=len(raw),
        source_row_count=len(bars),
    )


def run_preserved_v1b_mnq_03_26_replication(path: str | Path) -> DevelopmentReplayResult:
    """Run the only authorized V1B MNQ 03-26 exposed-development replication."""
    dataset = load_preserved_replication_raw(path)
    return _run_bars(
        dataset.bars,
        source_raw_sha256=dataset.source_raw_sha256,
        source_size_bytes=dataset.source_size_bytes,
        slope_evaluator=evaluate_v1a_ema20_slope,
        runner_id=RUNNER_ID,
        runner_version=RUNNER_VERSION,
        variant_id=VARIANT_ID,
        variant_protocol_sha256=VARIANT_PROTOCOL_SHA256,
        no_go_verdict=DevelopmentVerdict.NO_GO_VARIANT,
        entry_eligibility_evaluator=v1b_entry_session_allows,
        dataset_id=dataset.dataset_id,
        dataset_role=dataset.dataset_role,
    )


__all__ = [
    "CLEAN_LINEAGE_MANIFEST_SHA256",
    "DATASET_ID",
    "DATASET_ROLE",
    "EXPECTED_FIRST_TIMESTAMP_UTC",
    "EXPECTED_LAST_TIMESTAMP_UTC",
    "EXPECTED_RAW_ROW_COUNT",
    "EXPECTED_RAW_SIZE_BYTES",
    "EXPERIMENT_ID",
    "REPLICATION_PROTOCOL_SHA256",
    "RUNNER_ID",
    "RUNNER_VERSION",
    "SOURCE_RAW_FILENAME",
    "SOURCE_RAW_SHA256",
    "VerifiedReplicationDataset",
    "load_preserved_replication_raw",
    "run_preserved_v1b_mnq_03_26_replication",
]
