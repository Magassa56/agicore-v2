"""Tests for synthetic exit replay, independent reconstruction and tampering detection."""

from __future__ import annotations

import json

import pytest

from agicore.trading.synthetic_confirmation_fixture_v2 import generate_confirmation_fixture
from agicore.trading.synthetic_exit_replay_v2 import SCHEMA as EXIT_SCHEMA, replay_exit_native
from agicore.trading.synthetic_mission_storage_v2 import canonical, produce
from agicore.trading.synthetic_mission_verify_v2 import reconstruct_exit_native, verify


@pytest.mark.parametrize(
    "profile,expected_reason,expected_order_semantics,expected_end_state",
    [
        (
            "confirmation-long-v1",
            "OPEN_UNREALIZED_END_OF_DATA",
            None,
            "OPEN_UNREALIZED",
        ),
        (
            "confirmation-short-v1",
            "OPEN_UNREALIZED_END_OF_DATA",
            None,
            "OPEN_UNREALIZED",
        ),
        (
            "confirmation-long-rejected-v1",
            "ENTRY_REJECTED_BY_RISK",
            None,
            None,
        ),
        (
            "confirmation-short-rejected-v1",
            "ENTRY_REJECTED_BY_RISK",
            None,
            None,
        ),
        (
            "confirmation-long-exit-stop-v1",
            "EXIT_STRUCTURAL_STOP_FILLED",
            "STOP_MARKET",
            "FLAT",
        ),
        (
            "confirmation-short-exit-stop-v1",
            "EXIT_STRUCTURAL_STOP_FILLED",
            "STOP_MARKET",
            "FLAT",
        ),
        (
            "confirmation-long-exit-ema-v1",
            "EXIT_EMA20_FILLED",
            "MARKET",
            "FLAT",
        ),
        (
            "confirmation-short-exit-ema-v1",
            "EXIT_EMA20_FILLED",
            "MARKET",
            "FLAT",
        ),
    ],
)
def test_exit_native_replay_eight_scenarios(
    profile, expected_reason, expected_order_semantics, expected_end_state
):
    raw = generate_confirmation_fixture(profile, 39)
    result = replay_exit_native(raw)
    assert result["schema"] == EXIT_SCHEMA
    assert result["stop_reason"] == expected_reason
    assert result["end_state"] == expected_end_state

    exit_record = result["exit"]
    if expected_order_semantics is not None:
        assert exit_record is not None
        assert exit_record["order_semantics"] == expected_order_semantics
    else:
        assert exit_record is None


@pytest.mark.parametrize(
    "profile",
    [
        "confirmation-long-v1",
        "confirmation-short-v1",
        "confirmation-long-rejected-v1",
        "confirmation-short-rejected-v1",
        "confirmation-long-exit-stop-v1",
        "confirmation-short-exit-stop-v1",
        "confirmation-long-exit-ema-v1",
        "confirmation-short-exit-ema-v1",
    ],
)
def test_producer_and_verifier_independent_reconstruction(profile, tmp_path):
    bundle = tmp_path / "bundle"
    worker_receipt = produce(bundle, 39, stage="exit", profile=profile)
    verifier_receipt = verify(bundle, 39, stage="exit", profile=profile)

    assert verifier_receipt["status"] == "PASS"
    assert verifier_receipt["stage"] == "exit"
    assert verifier_receipt["replay"] == worker_receipt["replay"]

    raw = generate_confirmation_fixture(profile, 39)
    direct_reconstruct = reconstruct_exit_native(raw)
    assert direct_reconstruct == worker_receipt["replay"]


def test_verifier_detects_falsified_exit_type(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 39, stage="exit", profile="confirmation-long-exit-stop-v1")

    worker_file = bundle / "worker.json"
    worker_data = json.loads(worker_file.read_bytes())
    # Falsify order semantics
    worker_data["replay"]["exit"]["order_semantics"] = "MARKET"
    worker_file.write_bytes(canonical(worker_data))

    with pytest.raises(ValueError, match="worker output does not match independent verification"):
        verify(bundle, 39, stage="exit", profile="confirmation-long-exit-stop-v1")


def test_verifier_detects_falsified_end_state(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 39, stage="exit", profile="confirmation-long-v1")

    worker_file = bundle / "worker.json"
    worker_data = json.loads(worker_file.read_bytes())
    worker_data["replay"]["end_state"] = "FLAT"
    worker_file.write_bytes(canonical(worker_data))

    with pytest.raises(ValueError, match="worker output does not match independent verification"):
        verify(bundle, 39, stage="exit", profile="confirmation-long-v1")


def test_verifier_detects_falsified_exit_price(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 39, stage="exit", profile="confirmation-long-exit-ema-v1")

    worker_file = bundle / "worker.json"
    worker_data = json.loads(worker_file.read_bytes())
    worker_data["replay"]["exit"]["base_exit_fill_price"] = {
        "numerator": 99999,
        "denominator": 1,
    }
    worker_file.write_bytes(canonical(worker_data))

    with pytest.raises(ValueError, match="worker output does not match independent verification"):
        verify(bundle, 39, stage="exit", profile="confirmation-long-exit-ema-v1")


def test_verifier_detects_tampered_chunk(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 39, stage="exit", profile="confirmation-long-v1")

    chunk_file = bundle / "chunks" / "0000.zlib"
    raw_chunk = bytearray(chunk_file.read_bytes())
    raw_chunk[-1] ^= 0xFF
    chunk_file.write_bytes(bytes(raw_chunk))

    with pytest.raises(ValueError, match="stored chunk digest mismatch"):
        verify(bundle, 39, stage="exit", profile="confirmation-long-v1")


def test_verifier_detects_missing_chunk(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 39, stage="exit", profile="confirmation-long-v1")

    (bundle / "chunks" / "0000.zlib").unlink()

    with pytest.raises(ValueError, match="unexpected chunk inventory"):
        verify(bundle, 39, stage="exit", profile="confirmation-long-v1")
