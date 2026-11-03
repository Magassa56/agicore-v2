"""Invented-only entry execution missions, independent reconstruction and tampering detection."""

from __future__ import annotations

import hashlib
import json

import pytest

from agicore.manager import mission_cycle_v2 as manager
from agicore.trading import synthetic_entry_replay_v2 as entry_replay
from agicore.trading import synthetic_mission_storage_v2 as producer
from agicore.trading import synthetic_mission_verify_v2 as verifier
from agicore.trading.synthetic_confirmation_fixture_v2 import generate_confirmation_fixture


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


@pytest.mark.parametrize("direction", ["long", "short"])
def test_repeated_entry_missions_have_identical_evidence(direction, tmp_path):
    profile = f"confirmation-{direction}-v1"
    receipts = []
    for name in ("first", "second"):
        bundle = tmp_path / name
        producer.produce(bundle, 39, stage="entry", profile=profile)
        receipts.append(verifier.verify(bundle, 39, stage="entry", profile=profile))
    assert receipts[0] == receipts[1]
    assert receipts[0]["status"] == "PASS"
    assert receipts[0]["stage"] == "entry"
    assert receipts[0]["replay"]["stop_reason"] == "ENTRY_FILLED_BEFORE_EXIT"


def test_verifier_reconstructs_without_calling_producer_entry_or_handoff(tmp_path, monkeypatch):
    profile = "confirmation-long-v1"
    bundle = tmp_path / "bundle"
    producer.produce(bundle, 39, stage="entry", profile=profile)
    monkeypatch.setattr(
        entry_replay, "replay_confirmation_native", lambda *_: pytest.fail("producer replay used")
    )
    monkeypatch.setattr(
        entry_replay, "capture_synthetic_entry_v2", lambda **_: pytest.fail("producer handoff used")
    )
    receipt = verifier.verify(bundle, 39, stage="entry", profile=profile)
    assert receipt["status"] == "PASS"


@pytest.mark.parametrize(
    "field",
    [
        "window",
        "input",
        "confirmation",
        "stop_at_entry",
        "entry_action",
        "entry_price",
        "sized_entry",
    ],
)
def test_tampered_entry_receipt_is_rejected(tmp_path, field):
    profile = "confirmation-long-v1"
    bundle = tmp_path / "bundle"
    worker = producer.produce(bundle, 39, stage="entry", profile=profile)
    replay = worker["replay"]

    if field == "window":
        replay["window"]["raw_rows_sha256"] = "0" * 64
    elif field == "input":
        replay["input_sha256"] = "0" * 64
    elif field == "confirmation":
        replay["confirmation"]["confirmation_bar_index"] += 1
    elif field == "stop_at_entry":
        replay["stop"]["at_entry"]["entry_bar_index"] += 1
    elif field == "entry_action":
        replay["entry"]["execution"]["execution_action"] = "SELL_SHORT"
    elif field == "entry_price":
        replay["entry"]["execution"]["execution_price_before_costs"]["numerator"] += 10
    elif field == "sized_entry":
        replay["sized_entry"]["execution"]["execution_action"] = "SELL_SHORT"

    worker_file = bundle / "worker.json"
    worker_file.unlink()
    with worker_file.open("xb") as stream:
        stream.write(manager.canonical(worker))

    with pytest.raises(ValueError):
        verifier.verify(bundle, 39, stage="entry", profile=profile)


def test_valid_entry_replay_function():
    raw = generate_confirmation_fixture("confirmation-long-v1", 39)
    worker_replay = entry_replay.replay_entry_native(raw)
    worker_envelope = {
        "schema": "agicore:invented-storage-replay-worker:v2",
        "input_sha256": _sha(raw),
        "replay": worker_replay,
    }
    assert manager._valid_entry_replay(worker_replay, worker_envelope) is True

    # Tampered envelope
    worker_envelope_tampered = {
        "schema": "agicore:invented-storage-replay-worker:v2",
        "input_sha256": "0" * 64,
        "replay": worker_replay,
    }
    assert manager._valid_entry_replay(worker_replay, worker_envelope_tampered) is False


def test_valid_entry_replay_rejects_tampered_entry_state():
    raw = generate_confirmation_fixture("confirmation-long-v1", 39)
    worker_replay = entry_replay.replay_entry_native(raw)
    worker_envelope = {
        "schema": "agicore:invented-storage-replay-worker:v2",
        "input_sha256": _sha(raw),
        "replay": worker_replay,
    }
    # Mutate entry execution state
    tampered_replay = json.loads(json.dumps(worker_replay))
    tampered_replay["entry"]["execution_state"] = "PENDING_NEXT_BAR_OPEN"
    assert manager._valid_entry_replay(tampered_replay, worker_envelope) is False


def test_valid_entry_replay_for_rejected_profile():
    raw = generate_confirmation_fixture("confirmation-long-rejected-v1", 39)
    worker_replay = entry_replay.replay_entry_native(raw)
    worker_envelope = {
        "schema": "agicore:invented-storage-replay-worker:v2",
        "input_sha256": _sha(raw),
        "replay": worker_replay,
    }
    assert manager._valid_entry_replay(worker_replay, worker_envelope) is True

    # Attempt to fake an entry on rejected profile
    tampered_replay = json.loads(json.dumps(worker_replay))
    tampered_replay["entry"] = {"execution_state": "FILLED"}
    assert manager._valid_entry_replay(tampered_replay, worker_envelope) is False


def test_valid_entry_replay_rejects_quantity_mismatch():
    raw = generate_confirmation_fixture("confirmation-long-v1", 39)
    worker_replay = entry_replay.replay_entry_native(raw)
    worker_envelope = {
        "schema": "agicore:invented-storage-replay-worker:v2",
        "input_sha256": _sha(raw),
        "replay": worker_replay,
    }
    tampered_replay = json.loads(json.dumps(worker_replay))
    tampered_replay["sized_entry"]["risk_decision"]["approved_quantity"] = 5
    assert manager._valid_entry_replay(tampered_replay, worker_envelope) is False


def test_valid_entry_replay_rejects_price_mismatch():
    raw = generate_confirmation_fixture("confirmation-long-v1", 39)
    worker_replay = entry_replay.replay_entry_native(raw)
    worker_envelope = {
        "schema": "agicore:invented-storage-replay-worker:v2",
        "input_sha256": _sha(raw),
        "replay": worker_replay,
    }
    tampered_replay = json.loads(json.dumps(worker_replay))
    tampered_replay["sized_entry"]["execution"]["execution_price_before_costs"]["numerator"] += 1
    assert manager._valid_entry_replay(tampered_replay, worker_envelope) is False
