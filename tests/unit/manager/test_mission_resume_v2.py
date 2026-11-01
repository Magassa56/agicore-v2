"""Crash recovery is bounded to proven, durable mission checkpoints."""

from __future__ import annotations

import json
import os
import signal
import sqlite3
import subprocess
import sys
import time

import pytest

from agicore.manager import mission_cycle_v2 as manager


class SimulatedPowerLoss(BaseException):
    pass


@pytest.mark.parametrize(
    "checkpoint,prior,after",
    [
        ("contract_bound", [], ["worker", "verifier"]),
        ("worker_submitted", [], ["worker", "verifier"]),
        ("worker_completed", ["worker"], ["verifier"]),
        ("verifier_submitted", ["worker"], ["verifier"]),
        ("verifier_completed", ["worker", "verifier"], []),
        ("before_report", ["worker", "verifier"], []),
        ("after_report_event", ["worker", "verifier"], []),
    ],
)
def test_resume_only_runs_unstarted_roles(tmp_path, monkeypatch, checkpoint, prior, after):
    root = tmp_path / "mission"
    calls = []
    run_process = manager._run_process

    def track(root, module, role, observations, timeout, stage):
        calls.append(role)
        return run_process(root, module, role, observations, timeout, stage)

    def crash(name):
        if name == checkpoint:
            raise SimulatedPowerLoss(name)

    monkeypatch.setattr(manager, "_run_process", track)
    monkeypatch.setattr(manager, "_checkpoint", crash)
    with pytest.raises(SimulatedPowerLoss):
        manager.run_mission(root, 64, timeout_seconds=20)
    assert calls == prior
    assert not (root / "report.json").exists()
    monkeypatch.setattr(manager, "_checkpoint", lambda name: None)
    report = manager.resume_mission(root)
    assert report["status"] == "PASS"
    assert calls == prior + after
    before = (root / "report.json").read_bytes()
    assert manager.resume_mission(root) == report
    assert calls == prior + after
    assert (root / "report.json").read_bytes() == before
    rows = [json.loads(row) for row in (root / "events.jsonl").read_bytes().splitlines()]
    assert sum(row.get("agent_id") == "manager" and row.get("state") == "PASS" for row in rows) == 1


def test_legacy_missing_lock_is_refused_without_mutating_it(tmp_path):
    root = tmp_path / "legacy"
    root.mkdir()
    (root / "mission.json").write_text("{}\n")
    before = sorted(p.name for p in root.iterdir())
    with pytest.raises(manager.ResumeBlockedError, match="lock"):
        manager.resume_mission(root)
    assert sorted(p.name for p in root.iterdir()) == before


def test_unsealed_database_is_refused_without_touching_report(tmp_path):
    root = tmp_path / "legacy-db"
    report = manager.run_mission(root, 32, timeout_seconds=20)
    assert report["status"] == "PASS"
    with sqlite3.connect(root / "orchestrator.sqlite3") as db:
        db.execute("drop table mission_contract_binding")
    before = (root / "report.json").read_bytes()
    with pytest.raises(manager.ResumeBlockedError, match="unsealed"):
        manager.resume_mission(root)
    assert (root / "report.json").read_bytes() == before


def test_pending_task_without_durable_creation_event_is_not_dispatched(tmp_path, monkeypatch):
    root = tmp_path / "mission"

    def crash(name):
        if name == "worker_submitted":
            raise SimulatedPowerLoss(name)

    monkeypatch.setattr(manager, "_checkpoint", crash)
    with pytest.raises(SimulatedPowerLoss):
        manager.run_mission(root, 64, timeout_seconds=20)
    with sqlite3.connect(root / "orchestrator.sqlite3") as db:
        db.execute("delete from events where event_type = 'task.created'")
    monkeypatch.setattr(manager, "_run_process", lambda *args: pytest.fail("must not dispatch"))
    with pytest.raises(manager.ResumeBlockedError, match="lifecycle"):
        manager.resume_mission(root)
    assert not (root / "worker.stdout").exists()


@pytest.mark.parametrize("observations,forged", [(1, True), (64, 64.0)])
def test_forged_pending_task_payload_type_is_rejected(tmp_path, monkeypatch, observations, forged):
    root = tmp_path / "mission"

    def crash(name):
        if name == "worker_submitted":
            raise SimulatedPowerLoss(name)

    monkeypatch.setattr(manager, "_checkpoint", crash)
    with pytest.raises(SimulatedPowerLoss):
        manager.run_mission(root, observations, timeout_seconds=20)
    with sqlite3.connect(root / "orchestrator.sqlite3") as db:
        task_id, encoded = db.execute("select id,payload from tasks").fetchone()
        payload = json.loads(encoded)
        payload["observations"] = forged
        db.execute("update tasks set payload = ? where id = ?", (json.dumps(payload), task_id))
    monkeypatch.setattr(manager, "_run_process", lambda *args: pytest.fail("must not dispatch"))
    with pytest.raises(manager.ResumeBlockedError, match="contract"):
        manager.resume_mission(root)
    assert not (root / "worker.stdout").exists()


def test_completed_task_without_audit_projection_is_not_reused(tmp_path, monkeypatch):
    root = tmp_path / "mission"

    def crash(name):
        if name == "worker_completed":
            raise SimulatedPowerLoss(name)

    monkeypatch.setattr(manager, "_checkpoint", crash)
    with pytest.raises(SimulatedPowerLoss):
        manager.run_mission(root, 64, timeout_seconds=20)
    events = root / "events.jsonl"
    rows = events.read_bytes().splitlines(keepends=True)
    events.write_bytes(b"".join(row for row in rows if json.loads(row).get("state") != "COMPLETED"))
    monkeypatch.setattr(manager, "_run_process", lambda *args: pytest.fail("must not dispatch"))
    with pytest.raises(manager.ResumeBlockedError, match="lifecycle"):
        manager.resume_mission(root)
    assert not (root / "verifier.stdout").exists()


def test_concurrent_resume_is_refused(tmp_path):
    root = tmp_path / "mission"
    assert manager.run_mission(root, 32, timeout_seconds=20)["status"] == "PASS"
    with manager._mission_lock(root):
        with pytest.raises(manager.ResumeBlockedError, match="already active"):
            manager.resume_mission(root)


def test_contract_tampering_is_rejected_before_any_work(tmp_path, monkeypatch):
    root = tmp_path / "mission"
    monkeypatch.setattr(
        manager,
        "_checkpoint",
        lambda n: (_ for _ in ()).throw(SimulatedPowerLoss()) if n == "worker_completed" else None,
    )
    with pytest.raises(SimulatedPowerLoss):
        manager.run_mission(root, 64, timeout_seconds=20)
    mission_path = root / "mission.json"
    mission = json.loads(mission_path.read_bytes())
    mission["observations"] = 65
    mission_path.write_bytes(manager.canonical(mission))
    before = mission_path.read_bytes()
    monkeypatch.setattr(manager, "_run_process", lambda *args: pytest.fail("must not launch"))
    with pytest.raises(manager.ResumeBlockedError, match="binding"):
        manager.resume_mission(root)
    assert mission_path.read_bytes() == before
    assert not (root / "verifier.stdout").exists()


@pytest.mark.parametrize("artifact", ["worker.json", "manifest.json"])
def test_tampered_completed_worker_evidence_blocks_resume(tmp_path, monkeypatch, artifact):
    root = tmp_path / "mission"
    monkeypatch.setattr(
        manager,
        "_checkpoint",
        lambda n: (_ for _ in ()).throw(SimulatedPowerLoss()) if n == "worker_completed" else None,
    )
    with pytest.raises(SimulatedPowerLoss):
        manager.run_mission(root, 64, timeout_seconds=20)
    path = root / "bundle" / artifact
    obj = json.loads(path.read_bytes())
    obj["invented_tampering"] = True
    path.write_bytes(manager.canonical(obj))
    monkeypatch.setattr(manager, "_run_process", lambda *args: pytest.fail("must not launch"))
    with pytest.raises(manager.ResumeBlockedError):
        manager.resume_mission(root)
    assert not (root / "verifier.stdout").exists()


def test_changed_source_blocks_resume(tmp_path, monkeypatch):
    root = tmp_path / "mission"
    monkeypatch.setattr(
        manager,
        "_checkpoint",
        lambda n: (_ for _ in ()).throw(SimulatedPowerLoss()) if n == "worker_completed" else None,
    )
    with pytest.raises(SimulatedPowerLoss):
        manager.run_mission(root, 64, timeout_seconds=20)
    monkeypatch.setattr(manager, "_source_hashes", lambda: {"different": "source"})
    with pytest.raises(manager.ResumeBlockedError, match="sources"):
        manager.resume_mission(root)


def test_existing_report_with_pending_task_never_relaunches(tmp_path, monkeypatch):
    root = tmp_path / "mission"

    def crash(name):
        if name == "worker_submitted":
            raise SimulatedPowerLoss(name)

    monkeypatch.setattr(manager, "_checkpoint", crash)
    with pytest.raises(SimulatedPowerLoss):
        manager.run_mission(root, 64, timeout_seconds=20)
    report_path = root / "report.json"
    report_path.write_bytes(manager.canonical({"status": "PASS", "not": "trusted"}))
    before = report_path.read_bytes()
    monkeypatch.setattr(manager, "_run_process", lambda *args: pytest.fail("must not relaunch"))
    with pytest.raises(manager.ResumeBlockedError, match="existing report"):
        manager.resume_mission(root)
    assert report_path.read_bytes() == before
    assert not (root / "worker.stdout").exists()


def test_changed_chunk_after_verification_blocks_finalization(tmp_path, monkeypatch):
    root = tmp_path / "mission"

    def crash(name):
        if name == "verifier_completed":
            raise SimulatedPowerLoss(name)

    monkeypatch.setattr(manager, "_checkpoint", crash)
    with pytest.raises(SimulatedPowerLoss):
        manager.run_mission(root, 64, timeout_seconds=20)
    chunk = root / "bundle" / "chunks" / "0000.zlib"
    raw = chunk.read_bytes()
    chunk.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
    monkeypatch.setattr(manager, "_run_process", lambda *args: pytest.fail("must not relaunch"))
    with pytest.raises(manager.ResumeBlockedError, match="stored chunk altered"):
        manager.resume_mission(root)
    assert not (root / "report.json").exists()


@pytest.mark.parametrize("kind", ["bool_count", "float_observations"])
def test_forged_receipt_numeric_types_are_rejected(tmp_path, monkeypatch, kind):
    root = tmp_path / "mission"

    def crash(name):
        if name == "verifier_completed":
            raise SimulatedPowerLoss(name)

    monkeypatch.setattr(manager, "_checkpoint", crash)
    with pytest.raises(SimulatedPowerLoss):
        manager.run_mission(root, 64, timeout_seconds=20)
    path = root / "bundle" / "verification.json"
    receipt = json.loads(path.read_bytes())
    if kind == "bool_count":
        assert receipt["replay"]["counts"]["impulses"] == 1
        receipt["replay"]["counts"]["impulses"] = True
    else:
        receipt["observations"] = 64.0
    path.write_bytes(manager.canonical(receipt))
    with pytest.raises(manager.ResumeBlockedError, match="receipt"):
        manager.resume_mission(root)


def test_forged_report_numeric_type_is_rejected(tmp_path):
    root = tmp_path / "mission"
    report = manager.run_mission(root, 64, timeout_seconds=20)
    assert report["status"] == "PASS"
    report["observations"] = 64.0
    (root / "report.json").write_bytes(manager.canonical(report))
    with pytest.raises(manager.ResumeBlockedError, match="report"):
        manager.resume_mission(root)


def test_sigkill_supervisor_leaves_live_child_and_resume_fails_closed(tmp_path):
    root = tmp_path / "mission"
    code = r"""import subprocess,sys
from pathlib import Path
from agicore.manager import mission_cycle_v2 as m
root=Path(sys.argv[1])
def fake(root,module,role,observations,timeout,stage):
    heartbeat="import sys,time\nwhile True:\n open(sys.argv[1],'a').write('x')\n time.sleep(.05)"
    child=subprocess.Popen([sys.executable,"-c",heartbeat,str(root/"heartbeat")],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    (root/"synthetic-child.pid").write_text(str(child.pid))
    child.wait()
    raise AssertionError("child should be terminated by the test")
m._run_process=fake
m.run_mission(root,64,timeout_seconds=20)
"""
    process = subprocess.Popen(
        [sys.executable, "-B", "-c", code, str(root)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    child_pid = None
    try:
        deadline = time.monotonic() + 15
        marker = root / "synthetic-child.pid"
        while not marker.exists() and time.monotonic() < deadline:
            if process.poll() is not None:
                pytest.fail("synthetic supervisor ended before child launch")
            time.sleep(0.05)
        assert marker.exists()
        child_pid = int(marker.read_text())
        os.kill(process.pid, signal.SIGKILL)
        process.wait(timeout=5)
        os.kill(child_pid, 0)
        heartbeat = root / "heartbeat"
        deadline = time.monotonic() + 5
        while not heartbeat.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        assert heartbeat.exists()
        size = heartbeat.stat().st_size
        while heartbeat.stat().st_size == size and time.monotonic() < deadline:
            time.sleep(0.05)
        assert heartbeat.stat().st_size > size  # Child ran after supervisor death.
        with pytest.raises(manager.ResumeBlockedError, match="running.*ambiguous"):
            manager.resume_mission(root)
        assert not (root / "verifier.stdout").exists()
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        if child_pid is not None:
            try:
                os.killpg(child_pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
