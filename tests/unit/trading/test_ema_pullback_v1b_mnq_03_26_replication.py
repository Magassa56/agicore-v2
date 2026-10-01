"""Tests for the single fail-closed MNQ 03-26 V1B replication runner."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

import agicore.trading.ema_pullback_v1_mnq_development_replay as shared_replay
import agicore.trading.ema_pullback_v1b_mnq_03_26_replication as replication
from agicore.trading.ema_pullback_v1_mnq_development import (
    REPLICATION_DATASET_ROLE,
    DevelopmentProtocolError,
    DevelopmentVerdict,
)
from agicore.trading.ema_pullback_v1_mnq_development_replay import (
    DevelopmentReplayBar,
    DevelopmentReplayError,
)
from agicore.trading.ema_pullback_v1a_mnq import evaluate_v1a_ema20_slope
from agicore.trading.ema_pullback_v1b_mnq import (
    VARIANT_ID,
    VARIANT_PROTOCOL_SHA256,
    v1b_entry_session_allows,
)

ROOT = Path(__file__).resolve().parents[3]
START = datetime(2026, 1, 5, 14, 26, tzinfo=UTC)


def _bar(sequence: int) -> DevelopmentReplayBar:
    return DevelopmentReplayBar(
        sequence=sequence,
        timestamp_utc=START + timedelta(minutes=sequence),
        open=Decimal("100.00"),
        high=Decimal("100.50"),
        low=Decimal("99.50"),
        close=Decimal("100.00"),
        volume=100,
    )


def test_replication_identity_and_frozen_inputs_are_exact() -> None:
    assert replication.EXPERIMENT_ID == ("EMA_PULLBACK_V1B_MNQ_CROSS_CONTRACT_REPLICATION_03_26")
    assert replication.DATASET_ID == ("mnq-03-26-minute-last-development-replication-2122722f-v1")
    assert replication.DATASET_ROLE == REPLICATION_DATASET_ROLE
    assert replication.SOURCE_RAW_FILENAME == "MNQ 03-26.Last.txt"
    assert replication.SOURCE_RAW_SHA256 == (
        "2122722f25dbc865dad154905309b5e76d2190561ffc64acdaa955365ccb9efc"
    )
    assert replication.EXPECTED_RAW_SIZE_BYTES == 3_946_060
    assert replication.EXPECTED_RAW_ROW_COUNT == 74_308
    assert replication.EXPECTED_FIRST_TIMESTAMP_UTC.isoformat() == "2026-01-01T01:22:00+00:00"
    assert replication.EXPECTED_LAST_TIMESTAMP_UTC.isoformat() == "2026-03-20T13:30:00+00:00"

    protocol = ROOT / "docs/evidence/EMA_PULLBACK_V1B_MNQ_03_26_REPLICATION_PROTOCOL.json"
    manifest = ROOT / "docs/evidence/MNQ_03-26_CLEAN_LINEAGE/dataset_manifest.json"
    v1b = ROOT / "src/agicore/trading/ema_pullback_v1b_mnq.py"
    assert hashlib.sha256(protocol.read_bytes()).hexdigest() == (
        replication.REPLICATION_PROTOCOL_SHA256
    )
    assert replication.CLEAN_LINEAGE_MANIFEST_SHA256 == (
        "b22371ac3be30952ae58f4b5a8a5d6261b688583bce31ed2dd6c958f7c4b7c80"
    )
    assert hashlib.sha256(v1b.read_bytes()).hexdigest() == (
        "c61703033504539cda5067798c5b38832f406484e069228c9b6e3eb0533ee717"
    )

    manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert manifest_payload["manifest_sha256"] == replication.CLEAN_LINEAGE_MANIFEST_SHA256
    assert manifest_payload["gate_status"] == "PASS"


def test_private_loader_rejects_wrong_bytes_before_parsing(tmp_path, monkeypatch) -> None:
    candidate = tmp_path / replication.SOURCE_RAW_FILENAME
    candidate.write_text("not the preserved RAW", encoding="utf-8")
    monkeypatch.setattr(
        replication,
        "parse_ninjatrader_last_rows",
        lambda _: pytest.fail("parser must not see bytes with the wrong hash"),
    )

    with pytest.raises(DevelopmentReplayError, match="SHA-256 mismatch"):
        replication.load_preserved_replication_raw(candidate)


def test_private_loader_accepts_only_matching_hash_size_rows_and_bounds(
    tmp_path, monkeypatch
) -> None:
    candidate = tmp_path / replication.SOURCE_RAW_FILENAME
    candidate.write_text(
        "20260101 012200;100.00;100.50;99.50;100.25;12\n"
        "20260101 012300;100.25;101.00;100.00;100.75;15",
        encoding="utf-8",
    )
    raw = candidate.read_bytes()
    monkeypatch.setattr(replication, "SOURCE_RAW_SHA256", hashlib.sha256(raw).hexdigest())
    monkeypatch.setattr(replication, "EXPECTED_RAW_SIZE_BYTES", len(raw))
    monkeypatch.setattr(replication, "EXPECTED_RAW_ROW_COUNT", 2)
    monkeypatch.setattr(
        replication,
        "EXPECTED_FIRST_TIMESTAMP_UTC",
        datetime(2026, 1, 1, 1, 22, tzinfo=UTC),
    )
    monkeypatch.setattr(
        replication,
        "EXPECTED_LAST_TIMESTAMP_UTC",
        datetime(2026, 1, 1, 1, 23, tzinfo=UTC),
    )

    dataset = replication.load_preserved_replication_raw(candidate)

    assert dataset.source_raw_sha256 == hashlib.sha256(raw).hexdigest()
    assert dataset.source_size_bytes == len(raw)
    assert dataset.source_row_count == 2
    assert len(dataset.bars) == 2
    assert dataset.oos_accessed is False


def test_replication_runner_delegates_to_frozen_v1b_without_strategy_delta(monkeypatch) -> None:
    dataset = type(
        "Dataset",
        (),
        {
            "bars": (),
            "source_raw_sha256": replication.SOURCE_RAW_SHA256,
            "source_size_bytes": replication.EXPECTED_RAW_SIZE_BYTES,
            "dataset_id": replication.DATASET_ID,
            "dataset_role": replication.DATASET_ROLE,
        },
    )()
    captured: dict[str, object] = {}

    def fake_run_bars(*args: object, **kwargs: object) -> object:
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(replication, "load_preserved_replication_raw", lambda _: dataset)
    monkeypatch.setattr(replication, "_run_bars", fake_run_bars)

    replication.run_preserved_v1b_mnq_03_26_replication("private-raw")

    assert captured == {
        "source_raw_sha256": replication.SOURCE_RAW_SHA256,
        "source_size_bytes": replication.EXPECTED_RAW_SIZE_BYTES,
        "slope_evaluator": evaluate_v1a_ema20_slope,
        "runner_id": replication.RUNNER_ID,
        "runner_version": replication.RUNNER_VERSION,
        "variant_id": VARIANT_ID,
        "variant_protocol_sha256": VARIANT_PROTOCOL_SHA256,
        "no_go_verdict": DevelopmentVerdict.NO_GO_VARIANT,
        "entry_eligibility_evaluator": v1b_entry_session_allows,
        "dataset_id": replication.DATASET_ID,
        "dataset_role": replication.DATASET_ROLE,
    }


def test_shared_runner_binds_replication_identity_without_changing_screening() -> None:
    result = shared_replay._run_bars(
        tuple(_bar(sequence) for sequence in range(4)),
        source_raw_sha256=replication.SOURCE_RAW_SHA256,
        source_size_bytes=replication.EXPECTED_RAW_SIZE_BYTES,
        slope_evaluator=evaluate_v1a_ema20_slope,
        runner_id=replication.RUNNER_ID,
        runner_version=replication.RUNNER_VERSION,
        variant_id=VARIANT_ID,
        variant_protocol_sha256=VARIANT_PROTOCOL_SHA256,
        no_go_verdict=DevelopmentVerdict.NO_GO_VARIANT,
        entry_eligibility_evaluator=v1b_entry_session_allows,
        dataset_id=replication.DATASET_ID,
        dataset_role=replication.DATASET_ROLE,
    )

    assert result.dataset_id == replication.DATASET_ID
    assert result.dataset_role == replication.DATASET_ROLE
    assert result.source_raw_sha256 == replication.SOURCE_RAW_SHA256
    assert result.screening.dataset_id == replication.DATASET_ID
    assert result.screening.dataset_role == replication.DATASET_ROLE
    assert result.screening.source_raw_sha256 == replication.SOURCE_RAW_SHA256
    assert result.screening.verdict is DevelopmentVerdict.INSUFFICIENT_SAMPLE
    assert result.replay_count == 1
    assert result.deterministic is True
    assert result.oos_accessed is False


@pytest.mark.parametrize(
    ("dataset_id", "source_sha", "dataset_role", "message"),
    [
        ("", replication.SOURCE_RAW_SHA256, replication.DATASET_ROLE, "dataset_id"),
        (
            replication.DATASET_ID,
            replication.SOURCE_RAW_SHA256.upper(),
            replication.DATASET_ROLE,
            "lowercase SHA-256",
        ),
        (replication.DATASET_ID, replication.SOURCE_RAW_SHA256, "OOS", "only EXPOSED_DEVELOPMENT"),
    ],
)
def test_replication_identity_overrides_fail_closed(
    dataset_id: str,
    source_sha: str,
    dataset_role: str,
    message: str,
) -> None:
    with pytest.raises(DevelopmentProtocolError, match=message):
        shared_replay._run_bars(
            tuple(_bar(sequence) for sequence in range(4)),
            source_raw_sha256=source_sha,
            source_size_bytes=1,
            dataset_id=dataset_id,
            dataset_role=dataset_role,
        )


def test_replication_source_contains_no_execution_side_effect_or_private_path() -> None:
    source = Path(replication.__file__).read_text(encoding="utf-8")
    assert "if __name__" not in source
    assert "/workspace/" not in source
    assert "data/" not in source
    assert "broker" in replication.__doc__.lower()
