"""Invented-only exit execution missions, independent reconstruction and tampering detection."""

from __future__ import annotations

import hashlib
import json

import pytest

from agicore.manager import mission_cycle_v2 as manager
from agicore.trading import synthetic_exit_replay_v2 as exit_replay
from agicore.trading import synthetic_mission_storage_v2 as producer
from agicore.trading import synthetic_mission_verify_v2 as verifier
from agicore.trading.synthetic_confirmation_fixture_v2 import generate_confirmation_fixture


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


@pytest.mark.parametrize(
    "profile,expected_reason,expected_end_state",
    [
        ("confirmation-long-v1", "OPEN_UNREALIZED_END_OF_DATA", "OPEN_UNREALIZED"),
        ("confirmation-short-v1", "OPEN_UNREALIZED_END_OF_DATA", "OPEN_UNREALIZED"),
        ("confirmation-long-exit-stop-v1", "EXIT_STRUCTURAL_STOP_FILLED", "FLAT"),
        ("confirmation-short-exit-stop-v1", "EXIT_STRUCTURAL_STOP_FILLED", "FLAT"),
        ("confirmation-long-exit-ema-v1", "EXIT_EMA20_FILLED", "FLAT"),
        ("confirmation-short-exit-ema-v1", "EXIT_EMA20_FILLED", "FLAT"),
    ],
)
def test_repeated_exit_missions_have_identical_evidence(
    profile, expected_reason, expected_end_state, tmp_path
):
    receipts = []
    for name in ("first", "second"):
        bundle = tmp_path / name
        producer.produce(bundle, 39, stage="exit", profile=profile)
        receipts.append(verifier.verify(bundle, 39, stage="exit", profile=profile))
    assert receipts[0] == receipts[1]
    assert receipts[0]["status"] == "PASS"
    assert receipts[0]["stage"] == "exit"
    assert receipts[0]["replay"]["stop_reason"] == expected_reason
    assert receipts[0]["replay"]["end_state"] == expected_end_state


def test_verifier_reconstructs_without_calling_producer_exit_or_handoff(tmp_path, monkeypatch):
    profile = "confirmation-long-exit-stop-v1"
    bundle = tmp_path / "bundle"
    producer.produce(bundle, 39, stage="exit", profile=profile)
    monkeypatch.setattr(
        exit_replay, "replay_confirmation_native", lambda *_: pytest.fail("producer replay used")
    )
    monkeypatch.setattr(
        exit_replay, "capture_synthetic_exit_v2", lambda **_: pytest.fail("producer handoff used")
    )
    receipt = verifier.verify(bundle, 39, stage="exit", profile=profile)
    assert receipt["status"] == "PASS"


@pytest.mark.parametrize(
    "field",
    [
        "window",
        "input",
        "confirmation",
        "stop_at_entry",
        "entry_price",
        "exit_order_semantics",
        "end_state",
    ],
)
def test_tampered_exit_receipt_is_rejected(tmp_path, field):
    profile = "confirmation-long-exit-stop-v1"
    bundle = tmp_path / "bundle"
    worker = producer.produce(bundle, 39, stage="exit", profile=profile)
    replay = worker["replay"]

    if field == "window":
        replay["window"]["raw_rows_sha256"] = "0" * 64
    elif field == "input":
        replay["input_sha256"] = "0" * 64
    elif field == "confirmation":
        replay["confirmation"]["confirmation_bar_index"] += 1
    elif field == "stop_at_entry":
        replay["stop"]["at_entry"]["entry_bar_index"] += 1
    elif field == "entry_price":
        replay["entry"]["execution"]["execution_price_before_costs"]["numerator"] += 10
    elif field == "exit_order_semantics":
        replay["exit"]["order_semantics"] = "MARKET"
    elif field == "end_state":
        replay["end_state"] = "OPEN_UNREALIZED"

    worker_file = bundle / "worker.json"
    worker_file.unlink()
    with worker_file.open("xb") as stream:
        stream.write(manager.canonical(worker))

    with pytest.raises(ValueError):
        verifier.verify(bundle, 39, stage="exit", profile=profile)


def test_valid_exit_replay_function():
    raw = generate_confirmation_fixture("confirmation-long-exit-stop-v1", 39)
    worker_replay = exit_replay.replay_exit_native(raw)
    worker_envelope = {
        "schema": "agicore:invented-storage-replay-worker:v2",
        "input_sha256": _sha(raw),
        "replay": worker_replay,
    }
    assert manager._valid_exit_replay(worker_replay, worker_envelope) is True

    # Tampered envelope
    worker_envelope_tampered = {
        "schema": "agicore:invented-storage-replay-worker:v2",
        "input_sha256": "0" * 64,
        "replay": worker_replay,
    }
    assert manager._valid_exit_replay(worker_replay, worker_envelope_tampered) is False


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
def test_valid_exit_replay_for_all_scenarios(profile):
    raw = generate_confirmation_fixture(profile, 39)
    worker_replay = exit_replay.replay_exit_native(raw)
    worker_envelope = {
        "schema": "agicore:invented-storage-replay-worker:v2",
        "input_sha256": _sha(raw),
        "replay": worker_replay,
    }
    assert manager._valid_exit_replay(worker_replay, worker_envelope) is True


def test_valid_exit_replay_rejects_falsified_end_state():
    raw = generate_confirmation_fixture("confirmation-long-exit-stop-v1", 39)
    worker_replay = exit_replay.replay_exit_native(raw)
    worker_envelope = {
        "schema": "agicore:invented-storage-replay-worker:v2",
        "input_sha256": _sha(raw),
        "replay": worker_replay,
    }
    tampered_replay = json.loads(json.dumps(worker_replay))
    tampered_replay["end_state"] = "OPEN_UNREALIZED"
    assert manager._valid_exit_replay(tampered_replay, worker_envelope) is False


def test_valid_exit_replay_rejects_falsified_exit_semantics():
    raw = generate_confirmation_fixture("confirmation-long-exit-stop-v1", 39)
    worker_replay = exit_replay.replay_exit_native(raw)
    worker_envelope = {
        "schema": "agicore:invented-storage-replay-worker:v2",
        "input_sha256": _sha(raw),
        "replay": worker_replay,
    }
    tampered_replay = json.loads(json.dumps(worker_replay))
    tampered_replay["exit"]["order_semantics"] = "MARKET"
    assert manager._valid_exit_replay(tampered_replay, worker_envelope) is False
