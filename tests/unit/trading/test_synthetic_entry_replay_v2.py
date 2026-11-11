"""Tests for synthetic entry replay, independent reconstruction and tampering detection."""

from __future__ import annotations

import json

import pytest

from agicore.trading.synthetic_confirmation_fixture_v2 import generate_confirmation_fixture
from agicore.trading.synthetic_entry_replay_v2 import SCHEMA as ENTRY_SCHEMA, replay_entry_native
from agicore.trading.synthetic_mission_storage_v2 import canonical, produce
from agicore.trading.synthetic_mission_verify_v2 import reconstruct_entry_native, verify


@pytest.mark.parametrize(
    "profile,expected_reason,expected_action,expected_price,expected_qty",
    [
        (
            "confirmation-long-v1",
            "ENTRY_FILLED_BEFORE_EXIT",
            "BUY",
            {"numerator": 40009, "denominator": 2},
            2,
        ),
        (
            "confirmation-short-v1",
            "ENTRY_FILLED_BEFORE_EXIT",
            "SELL_SHORT",
            {"numerator": 39991, "denominator": 2},
            2,
        ),
        (
            "confirmation-long-rejected-v1",
            "ENTRY_REJECTED_BY_RISK",
            None,
            None,
            0,
        ),
        (
            "confirmation-short-rejected-v1",
            "ENTRY_REJECTED_BY_RISK",
            None,
            None,
            0,
        ),
    ],
)
def test_entry_native_replay_four_scenarios(
    profile, expected_reason, expected_action, expected_price, expected_qty
):
    raw = generate_confirmation_fixture(profile, 39)
    result = replay_entry_native(raw)
    assert result["schema"] == ENTRY_SCHEMA
    assert result["stop_reason"] == expected_reason

    entry = result["entry"]
    sized = result["sized_entry"]
    stop = result["stop"]
    risk = result["risk"]

    if expected_action is not None:
        assert entry is not None
        assert entry["execution_state"] == "FILLED"
        assert entry["status"] == "EVALUATED"
        execution = entry["execution"]
        assert execution["execution_action"] == expected_action
        assert execution["execution_price_before_costs"] == expected_price
        assert execution["execution_bar_index"] == 36
        assert execution["order_semantics"] == "MARKET"

        assert sized is not None
        assert sized["risk_decision"]["approved_quantity"] == expected_qty
        assert sized["execution"]["execution_price_before_costs"] == expected_price

        assert stop["at_entry"] is not None
        assert stop["at_entry"]["stop_state"] == "ARMED"
        assert stop["at_entry"]["entry_price"] == expected_price
        assert stop["at_entry"]["entry_bar_index"] == 36
    else:
        assert entry is None
        assert sized is None
        assert stop["at_entry"] is None
        assert risk["decision"] == "REJECT"
        assert risk["approved_quantity"] == 0


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
    worker_receipt = produce(bundle, 39, stage="entry", profile=profile)
    verifier_receipt = verify(bundle, 39, stage="entry", profile=profile)

    assert verifier_receipt["status"] == "PASS"
    assert verifier_receipt["stage"] == "entry"
    assert verifier_receipt["replay"] == worker_receipt["replay"]

    raw = generate_confirmation_fixture(profile, 39)
    direct_reconstruct = reconstruct_entry_native(raw)
    assert direct_reconstruct == worker_receipt["replay"]


def test_verifier_detects_falsified_entry_price(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 39, stage="entry", profile="confirmation-long-v1")

    worker_file = bundle / "worker.json"
    worker_data = json.loads(worker_file.read_bytes())
    # Falsify execution price before costs
    worker_data["replay"]["entry"]["execution"]["execution_price_before_costs"] = {
        "numerator": 21000,
        "denominator": 1,
    }
    worker_file.write_bytes(canonical(worker_data))

    with pytest.raises(ValueError, match="worker output does not match independent verification"):
        verify(bundle, 39, stage="entry", profile="confirmation-long-v1")


def test_verifier_detects_falsified_execution_action(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 39, stage="entry", profile="confirmation-long-v1")

    worker_file = bundle / "worker.json"
    worker_data = json.loads(worker_file.read_bytes())
    worker_data["replay"]["entry"]["execution"]["execution_action"] = "SELL_SHORT"
    worker_file.write_bytes(canonical(worker_data))

    with pytest.raises(ValueError, match="worker output does not match independent verification"):
        verify(bundle, 39, stage="entry", profile="confirmation-long-v1")


def test_verifier_detects_falsified_stop_at_entry_state(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 39, stage="entry", profile="confirmation-long-v1")

    worker_file = bundle / "worker.json"
    worker_data = json.loads(worker_file.read_bytes())
    worker_data["replay"]["stop"]["at_entry"]["stop_state"] = "BREACHED_AT_ENTRY_OPEN"
    worker_file.write_bytes(canonical(worker_data))

    with pytest.raises(ValueError, match="worker output does not match independent verification"):
        verify(bundle, 39, stage="entry", profile="confirmation-long-v1")


def test_verifier_detects_falsified_approved_quantity(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 39, stage="entry", profile="confirmation-long-v1")

    worker_file = bundle / "worker.json"
    worker_data = json.loads(worker_file.read_bytes())
    worker_data["replay"]["risk"]["approved_quantity"] = 5
    worker_data["replay"]["sized_entry"]["risk_decision"]["approved_quantity"] = 5
    worker_file.write_bytes(canonical(worker_data))

    with pytest.raises(ValueError, match="worker output does not match independent verification"):
        verify(bundle, 39, stage="entry", profile="confirmation-long-v1")


def test_verifier_detects_tampered_chunk(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 39, stage="entry", profile="confirmation-long-v1")

    chunk_file = bundle / "chunks" / "0000.zlib"
    raw_chunk = bytearray(chunk_file.read_bytes())
    raw_chunk[-1] ^= 0xFF
    chunk_file.write_bytes(bytes(raw_chunk))

    with pytest.raises(ValueError, match="stored chunk digest mismatch"):
        verify(bundle, 39, stage="entry", profile="confirmation-long-v1")


def test_verifier_detects_missing_chunk(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 39, stage="entry", profile="confirmation-long-v1")

    (bundle / "chunks" / "0000.zlib").unlink()

    with pytest.raises(ValueError, match="unexpected chunk inventory"):
        verify(bundle, 39, stage="entry", profile="confirmation-long-v1")
