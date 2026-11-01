"""Small invented-only stop missions, independent reconstruction and tampering."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
import hashlib
import json
import sqlite3
import zlib

import pytest

from agicore.manager import mission_cycle_v2 as manager
from agicore.trading import synthetic_mission_storage_v2 as producer
from agicore.trading import synthetic_mission_verify_v2 as verifier
from agicore.trading import synthetic_stop_replay_v2 as stop_replay
from agicore.trading.synthetic_confirmation_fixture_v2 import generate_confirmation_fixture
from tools.agicore_v2_synthetic_scale_probe import generate_observations


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


@pytest.mark.parametrize("direction", ["long", "short"])
def test_stop_mission_runs_verifies_and_resumes(direction, tmp_path):
    profile = f"confirmation-{direction}-v1"
    root = tmp_path / direction
    report = manager.run_mission(root, 39, stage="stop", profile=profile, timeout_seconds=20)
    assert report["status"] == "PASS"
    assert report["orchestrator"] == "AgentOrchestrator+Dispatcher"
    receipt = report["verification"]
    replay = receipt["replay"]
    raw = generate_confirmation_fixture(profile, 39)
    assert receipt["input_sha256"] == replay["input_sha256"] == _sha(raw)
    assert replay["window"] == {
        "first_bar_index": 33,
        "last_bar_index": 35,
        "raw_rows_sha256": _sha(b"".join(raw.splitlines(keepends=True)[33:36])),
    }
    assert replay["confirmation_replay"]["processed_observations"] == 36
    assert replay["confirmation"]["source_regime_event_direction"] == direction.upper()
    assert replay["stop"]["status"] == "EVALUATED"
    assert replay["stop"]["initial_stop_record"]["initial_stop_price"] == {
        "numerator": 20000,
        "denominator": 1,
    }
    assert replay["stop"]["confirmation"] == replay["confirmation"]
    assert replay["stop"]["at_entry"] is None
    assert replay["stop_reason"] == "STOP_CAPTURED_BEFORE_RISK"
    mission = json.loads((root / "mission.json").read_bytes())
    assert mission["authorizations"]["initial_stop"] is True
    assert mission["authorizations"]["orders"] is False
    assert mission["authorizations"]["broker"] is False
    assert mission["authorizations"]["profitability"] is False
    assert mission["authorizations"]["real_data"] is False
    with sqlite3.connect(root / "orchestrator.sqlite3") as database:
        tasks = database.execute("select assigned_to, status from tasks order by assigned_to")
        assert tasks.fetchall() == [("verifier", "completed"), ("worker", "completed")]
    assert manager.resume_mission(root) == report


def test_verifier_reconstructs_without_calling_producer_stop_or_handoff(tmp_path, monkeypatch):
    profile = "confirmation-long-v1"
    bundle = tmp_path / "bundle"
    producer.produce(bundle, 39, stage="stop", profile=profile)
    monkeypatch.setattr(
        stop_replay, "replay_confirmation_native", lambda *_: pytest.fail("producer replay used")
    )
    monkeypatch.setattr(
        stop_replay, "capture_synthetic_stop_v2", lambda **_: pytest.fail("producer handoff used")
    )
    receipt = verifier.verify(bundle, 39, stage="stop", profile=profile)
    assert receipt["status"] == "PASS"


@pytest.mark.parametrize("direction", ["long", "short"])
def test_repeated_stop_missions_have_identical_evidence(direction, tmp_path):
    profile = f"confirmation-{direction}-v1"
    receipts = []
    for name in ("first", "second"):
        bundle = tmp_path / name
        producer.produce(bundle, 39, stage="stop", profile=profile)
        receipts.append(verifier.verify(bundle, 39, stage="stop", profile=profile))
    assert receipts[0] == receipts[1]


@pytest.mark.parametrize("field", ["window", "input", "confirmation", "stop", "number_type"])
def test_tampered_stop_receipt_is_rejected(tmp_path, field):
    profile = "confirmation-long-v1"
    bundle = tmp_path / "bundle"
    worker = producer.produce(bundle, 39, stage="stop", profile=profile)
    replay = worker["replay"]
    if field == "window":
        replay["window"]["raw_rows_sha256"] = "0" * 64
    elif field == "input":
        replay["input_sha256"] = "0" * 64
    elif field == "confirmation":
        replay["confirmation"]["confirmation_bar_index"] += 1
    elif field == "stop":
        replay["stop"]["initial_stop_record"]["initial_stop_price"]["numerator"] += 1
    else:
        replay["window"]["last_bar_index"] = 35.0
    (bundle / "worker.json").write_bytes(producer.canonical(worker))
    with pytest.raises(ValueError, match="worker output"):
        verifier.verify(bundle, 39, stage="stop", profile=profile)
    assert not (bundle / "verification.json").exists()


def test_changed_window_is_rejected_even_if_manifest_and_worker_are_rehashed(tmp_path):
    profile = "confirmation-long-v1"
    bundle = tmp_path / "bundle"
    worker = producer.produce(bundle, 39, stage="stop", profile=profile)
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    rows = generate_confirmation_fixture(profile, 39).splitlines(keepends=True)
    rows[34] = rows[34].replace(b"20001.75", b"20001.50")
    changed_raw = b"".join(rows)
    compressed = zlib.compress(changed_raw, level=9)
    (bundle / "chunks" / "0000.zlib").write_bytes(compressed)
    entry = manifest["chunks"][0]
    entry.update(
        raw_sha256=_sha(changed_raw), stored_sha256=_sha(compressed), stored_bytes=len(compressed)
    )
    manifest["raw_sha256"] = _sha(changed_raw)
    manifest_path.write_bytes(producer.canonical(manifest))
    worker["manifest_sha256"] = _sha(manifest_path.read_bytes())
    worker["input_sha256"] = _sha(changed_raw)
    worker["replay"]["input_sha256"] = _sha(changed_raw)
    (bundle / "worker.json").write_bytes(producer.canonical(worker))
    with pytest.raises(ValueError, match="bundle identity mismatch"):
        verifier.verify(bundle, 39, stage="stop", profile=profile)
    assert not (bundle / "verification.json").exists()


def test_untrusted_window_tuple_cannot_replace_generated_input(monkeypatch):
    raw = generate_confirmation_fixture("confirmation-long-v1", 39)
    real = stop_replay.replay_confirmation_native(raw)
    bad = list(real.stop_window)
    bad[1] = replace(bad[1], low=bad[1].low - 1)
    monkeypatch.setattr(
        stop_replay, "replay_confirmation_native", lambda _: replace(real, stop_window=tuple(bad))
    )
    with pytest.raises(ValueError, match="window differs from input bytes"):
        stop_replay.replay_stop_native(raw)


@pytest.mark.parametrize("direction", ["long", "short"])
def test_future_rows_change_input_identity_but_not_the_stop(direction):
    raw = generate_confirmation_fixture(f"confirmation-{direction}-v1", 39)
    rows = raw.splitlines(keepends=True)
    fields = rows[-1].decode().strip().split(";")
    fields[1:5] = [str(Decimal(value) + 10) for value in fields[1:5]]
    rows[-1] = (";".join(fields) + "\n").encode()
    changed = b"".join(rows)
    before = stop_replay.replay_stop_native(raw)
    after = stop_replay.replay_stop_native(changed)
    assert before == verifier.recompute_stop_events(raw)
    assert after == verifier.recompute_stop_events(changed)
    assert before["input_sha256"] != after["input_sha256"]
    assert before["window"] == after["window"]
    assert before["confirmation"] == after["confirmation"]
    assert before["stop"] == after["stop"]


def test_interrupted_stop_worker_can_resume_only_from_sealed_completion(tmp_path, monkeypatch):
    class Interruption(BaseException):
        pass

    root = tmp_path / "interrupted"

    def crash(name):
        if name == "worker_completed":
            raise Interruption()

    monkeypatch.setattr(manager, "_checkpoint", crash)
    with pytest.raises(Interruption):
        manager.run_mission(
            root, 39, stage="stop", profile="confirmation-long-v1", timeout_seconds=20
        )
    assert not (root / "bundle" / "verification.json").exists()
    monkeypatch.setattr(manager, "_checkpoint", lambda _: None)
    report = manager.resume_mission(root)
    assert report["status"] == "PASS"
    assert report["verification"]["replay"]["stop_reason"] == "STOP_CAPTURED_BEFORE_RISK"


def test_no_stop_is_invented_without_confirmation():
    raw = generate_observations(39)
    with pytest.raises(ValueError, match="did not confirm"):
        stop_replay.replay_stop_native(raw)
    with pytest.raises(ValueError, match="did not confirm"):
        verifier.recompute_stop_events(raw)


def test_no_stop_is_invented_when_confirmation_expires():
    raw = generate_confirmation_fixture("confirmation-long-v1", 39)
    rows = raw.splitlines(keepends=True)
    for index in (34, 35):
        fields = rows[index].decode().strip().split(";")
        fields[4] = fields[1]
        rows[index] = (";".join(fields) + "\n").encode()
    raw = b"".join(rows)
    confirmation = verifier.recompute_confirmation_events(raw)
    assert confirmation["counts"]["confirmations_expired"] == 1
    assert confirmation["counts"]["confirmations_qualified"] == 0
    with pytest.raises(ValueError, match="did not confirm"):
        stop_replay.replay_stop_native(raw)
    with pytest.raises(ValueError, match="did not confirm"):
        verifier.recompute_stop_events(raw)


@pytest.mark.parametrize("field", ["profile", "window", "receipt"])
def test_resume_rejects_modified_profile_window_or_receipt(tmp_path, field):
    root = tmp_path / "completed"
    report = manager.run_mission(
        root, 39, stage="stop", profile="confirmation-long-v1", timeout_seconds=20
    )
    assert report["status"] == "PASS"
    if field == "profile":
        path = root / "mission.json"
        changed = json.loads(path.read_bytes())
        changed["profile"] = "confirmation-short-v1"
    elif field == "window":
        path = root / "bundle" / "worker.json"
        changed = json.loads(path.read_bytes())
        changed["replay"]["window"]["raw_rows_sha256"] = "0" * 64
    else:
        path = root / "bundle" / "verification.json"
        changed = json.loads(path.read_bytes())
        changed["replay"]["stop"]["initial_stop_record"]["initial_stop_price"]["numerator"] += 1
    path.write_bytes(producer.canonical(changed))
    with pytest.raises(manager.ResumeBlockedError):
        manager.resume_mission(root)


@pytest.mark.parametrize("profile,count", [("standard", 39), ("confirmation-long-v1", 38)])
def test_stop_rejects_unregistered_inputs_before_any_write(tmp_path, profile, count):
    root = tmp_path / "forbidden"
    with pytest.raises(ValueError):
        manager.run_mission(root, count, stage="stop", profile=profile)
    assert not root.exists()
