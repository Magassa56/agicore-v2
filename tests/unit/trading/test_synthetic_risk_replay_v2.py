"""Tests for synthetic risk replay, independent reconstruction and tampering detection."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agicore.trading.synthetic_confirmation_fixture_v2 import generate_confirmation_fixture
from agicore.trading.synthetic_mission_storage_v2 import canonical, produce
from agicore.trading.synthetic_mission_verify_v2 import reconstruct_risk_native, verify
from agicore.trading.synthetic_risk_replay_v2 import SCHEMA as RISK_SCHEMA, replay_risk_native


@pytest.mark.parametrize(
    "profile,expected_decision,expected_qty,expected_reason",
    [
        ("confirmation-long-v1", "APPROVE", 2, None),
        ("confirmation-short-v1", "APPROVE", 2, None),
        ("confirmation-long-rejected-v1", "REJECT", 0, "RISK_PER_CONTRACT_EXCEEDS_BUDGET"),
        ("confirmation-short-rejected-v1", "REJECT", 0, "RISK_PER_CONTRACT_EXCEEDS_BUDGET"),
    ],
)
def test_risk_native_replay_four_scenarios(profile, expected_decision, expected_qty, expected_reason):
    raw = generate_confirmation_fixture(profile, 39)
    result = replay_risk_native(raw)
    assert result["schema"] == RISK_SCHEMA
    assert result["stop_reason"] == "RISK_DECIDED_BEFORE_ENTRY"
    risk = result["risk"]
    assert risk["decision"] == expected_decision
    assert risk["approved_quantity"] == expected_qty
    assert risk["rejection_reason"] == expected_reason
    if expected_decision == "APPROVE":
        assert risk["planned_total_risk_usd"] == {"numerator": 17, "denominator": 1}
    else:
        assert risk["planned_total_risk_usd"] is None


@pytest.mark.parametrize(
    "profile",
    [
        "confirmation-long-v1",
        "confirmation-short-v1",
        "confirmation-long-rejected-v1",
        "confirmation-short-rejected-v1",
    ],
)
def test_producer_and_verifier_independent_reconstruction(profile, tmp_path):
    bundle = tmp_path / "bundle"
    worker_receipt = produce(bundle, 39, stage="risk", profile=profile)
    verifier_receipt = verify(bundle, 39, stage="risk", profile=profile)

    assert verifier_receipt["status"] == "PASS"
    assert verifier_receipt["stage"] == "risk"
    assert verifier_receipt["replay"] == worker_receipt["replay"]

    # Independent reconstruction via verifier direct call
    raw = generate_confirmation_fixture(profile, 39)
    direct_reconstruct = reconstruct_risk_native(raw)
    assert direct_reconstruct == worker_receipt["replay"]


def test_verifier_detects_falsified_approved_quantity(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 39, stage="risk", profile="confirmation-long-v1")

    # Tamper with approved_quantity in worker.json
    worker_file = bundle / "worker.json"
    worker_data = json.loads(worker_file.read_bytes())
    worker_data["replay"]["risk"]["approved_quantity"] = 5  # Falsify to 5 contracts
    worker_file.write_bytes(canonical(worker_data))

    with pytest.raises(ValueError, match="worker output does not match independent verification"):
        verify(bundle, 39, stage="risk", profile="confirmation-long-v1")


def test_verifier_detects_falsified_rejection_overturn(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 39, stage="risk", profile="confirmation-long-rejected-v1")

    # Attempt to overturn rejection in worker.json
    worker_file = bundle / "worker.json"
    worker_data = json.loads(worker_file.read_bytes())
    worker_data["replay"]["risk"]["decision"] = "APPROVE"
    worker_data["replay"]["risk"]["rejection_reason"] = None
    worker_data["replay"]["risk"]["approved_quantity"] = 1
    worker_file.write_bytes(canonical(worker_data))

    with pytest.raises(ValueError, match="worker output does not match independent verification"):
        verify(bundle, 39, stage="risk", profile="confirmation-long-rejected-v1")


def test_verifier_detects_falsified_stop_price(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 39, stage="risk", profile="confirmation-long-v1")

    # Tamper with stop record inside risk
    worker_file = bundle / "worker.json"
    worker_data = json.loads(worker_file.read_bytes())
    worker_data["replay"]["risk"]["initial_stop_price"] = {"numerator": 19900, "denominator": 1}
    worker_file.write_bytes(canonical(worker_data))

    with pytest.raises(ValueError, match="worker output does not match independent verification"):
        verify(bundle, 39, stage="risk", profile="confirmation-long-v1")


def test_verifier_detects_tampered_chunk(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 39, stage="risk", profile="confirmation-long-v1")

    chunk_file = bundle / "chunks" / "0000.zlib"
    raw_chunk = bytearray(chunk_file.read_bytes())
    raw_chunk[-1] ^= 0xFF
    chunk_file.write_bytes(bytes(raw_chunk))

    with pytest.raises(ValueError, match="stored chunk digest mismatch"):
        verify(bundle, 39, stage="risk", profile="confirmation-long-v1")


def test_verifier_detects_missing_chunk(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 39, stage="risk", profile="confirmation-long-v1")

    (bundle / "chunks" / "0000.zlib").unlink()

    with pytest.raises(ValueError, match="unexpected chunk inventory"):
        verify(bundle, 39, stage="risk", profile="confirmation-long-v1")
