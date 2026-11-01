"""Independent regressions for durable evidence and child lifetime protection."""

from __future__ import annotations

import json
import os
import signal
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest

from agicore.manager import mission_cycle_v2 as manager


class SimulatedPowerLoss(BaseException):
    """Interrupt after a durable checkpoint without creating a failure report."""


def _interrupt_at(name):
    def interrupt(checkpoint):
        if checkpoint == name:
            raise SimulatedPowerLoss(name)

    return interrupt


def test_altered_worker_stderr_blocks_resume_without_changing_report(tmp_path, monkeypatch):
    root = tmp_path / "mission"
    assert manager.run_mission(root, 32, timeout_seconds=20)["status"] == "PASS"
    report_before = (root / "report.json").read_bytes()
    log = root / "worker.stderr"
    log.write_bytes(log.read_bytes() + b"forged log line\n")
    monkeypatch.setattr(manager, "_run_process", lambda *a, **k: pytest.fail("must not dispatch"))
    with pytest.raises(manager.ResumeBlockedError):
        manager.resume_mission(root)
    assert (root / "report.json").read_bytes() == report_before


@pytest.mark.parametrize("checkpoint", ["worker_completed", "complete"])
def test_altered_event_timestamp_blocks_resume(tmp_path, monkeypatch, checkpoint):
    root = tmp_path / "mission"
    if checkpoint == "complete":
        assert manager.run_mission(root, 32, timeout_seconds=20)["status"] == "PASS"
    else:
        monkeypatch.setattr(manager, "_checkpoint", _interrupt_at(checkpoint))
        with pytest.raises(SimulatedPowerLoss):
            manager.run_mission(root, 32, timeout_seconds=20)
        monkeypatch.setattr(manager, "_checkpoint", lambda _name: None)
    events = root / "events.jsonl"
    rows = [json.loads(row) for row in events.read_bytes().splitlines()]
    assert rows[1]["agent_id"] == "worker"
    rows[1]["timestamp_utc"] = "2000-01-01T00:00:00+00:00"
    events.write_bytes(b"".join(manager.canonical(row) for row in rows))
    monkeypatch.setattr(manager, "_run_process", lambda *a, **k: pytest.fail("must not dispatch"))
    with pytest.raises(manager.ResumeBlockedError):
        manager.resume_mission(root)


@pytest.mark.parametrize("field", ["wall_ns", "peak_rss_bytes"])
def test_altered_process_measurement_blocks_resume_before_report(tmp_path, monkeypatch, field):
    root = tmp_path / "mission"
    monkeypatch.setattr(manager, "_checkpoint", _interrupt_at("before_report"))
    with pytest.raises(SimulatedPowerLoss):
        manager.run_mission(root, 32, timeout_seconds=20)
    assert not (root / "report.json").exists()
    with sqlite3.connect(root / "orchestrator.sqlite3") as db:
        task_id, encoded = db.execute(
            "SELECT id, result FROM tasks WHERE assigned_to = 'worker'"
        ).fetchone()
        outcome = json.loads(encoded)
        assert type(outcome[field]) is int
        outcome[field] += 1
        db.execute("UPDATE tasks SET result = ? WHERE id = ?", (json.dumps(outcome), task_id))
    monkeypatch.setattr(manager, "_checkpoint", lambda _name: None)
    monkeypatch.setattr(manager, "_run_process", lambda *a, **k: pytest.fail("must not dispatch"))
    with pytest.raises(manager.ResumeBlockedError):
        manager.resume_mission(root)
    assert not (root / "report.json").exists()


def _proc_status(pid):
    """Return Linux state, parent PID and start time; None when absent."""
    try:
        record = Path(f"/proc/{pid}/stat").read_text()
    except FileNotFoundError:
        return None
    fields = record.rsplit(")", 1)[1].split()
    return fields[0], int(fields[1]), fields[19]


@pytest.mark.skipif(sys.platform != "linux", reason="requires Linux prctl and /proc")
def test_sigkill_supervisor_kills_real_run_process_child_and_blocks_resume(tmp_path):
    root = tmp_path / "mission"
    code = r"""import subprocess, sys
from pathlib import Path
from agicore.manager import mission_cycle_v2 as m
root = Path(sys.argv[1])
real_popen = subprocess.Popen
def replace_command(command, *args, **kwargs):
    assert kwargs.get("start_new_session") is True
    assert callable(kwargs.get("preexec_fn"))
    child_code = ("import json,os,sys,time\nfrom pathlib import Path\n"
                  "p=Path(sys.argv[1]); t=p.with_suffix('.tmp')\n"
                  "t.write_text(json.dumps({'pid':os.getpid(),'ppid':os.getppid(),"
                  "'proc_pid':int(os.readlink('/proc/self'))})); t.replace(p)\n"
                  "while not p.with_name('release').exists(): time.sleep(.01)\n"
                  "time.sleep(.5); p.with_name('survived').write_text('unexpected')\n"
                  "time.sleep(120)\n")
    return real_popen([sys.executable, "-B", "-c", child_code, str(root / "child.pid")], *args, **kwargs)
m.subprocess.Popen = replace_command
m.run_mission(root, 32, timeout_seconds=20)
"""
    supervisor = subprocess.Popen(
        [sys.executable, "-B", "-c", code, str(root)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    child_pid = None
    child_proc_pid = None
    child_start = None
    try:
        marker = root / "child.pid"
        deadline = time.monotonic() + 20
        while not marker.exists() and time.monotonic() < deadline:
            if supervisor.poll() is not None:
                pytest.fail("supervisor exited before the real child became ready")
            time.sleep(0.02)
        assert marker.exists(), "real child did not become ready"
        identity = json.loads(marker.read_text())
        child_pid = identity["pid"]
        child_proc_pid = identity["proc_pid"]
        assert identity["ppid"] == supervisor.pid
        state = _proc_status(child_proc_pid)
        if state is not None:
            child_start = state[2]
        assert state is not None and state[0] != "Z"
        os.kill(supervisor.pid, signal.SIGKILL)
        supervisor.wait(timeout=5)
        (root / "release").write_text("attempt to release orphan")
        witness_deadline = time.monotonic() + 1.5
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            state = _proc_status(child_proc_pid)
            if state is None or state[0] == "Z" or state[2] != child_start:
                break
            time.sleep(0.02)
        else:
            pytest.fail("direct child survived its supervisor's death")
        while time.monotonic() < witness_deadline:
            time.sleep(0.02)
        assert not (root / "survived").exists(), "orphan wrote the delayed witness"
        with pytest.raises(manager.ResumeBlockedError, match="running.*ambiguous"):
            manager.resume_mission(root)
        assert not (root / "verifier.stdout").exists()
    finally:
        if supervisor.poll() is None:
            supervisor.kill()
            supervisor.wait(timeout=5)
        if child_pid is not None and child_start is not None:
            state = _proc_status(child_proc_pid)
            if state is not None and state[0] != "Z" and state[2] == child_start:
                os.kill(child_pid, signal.SIGKILL)
