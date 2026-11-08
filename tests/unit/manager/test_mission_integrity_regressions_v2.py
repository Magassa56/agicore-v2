"""Independent regressions for durable evidence and child lifetime protection."""

from __future__ import annotations

import hashlib
import inspect
import json
import os
import signal
import sqlite3
import subprocess
import sys
import time
from contextlib import suppress
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from agicore.manager import mission_cycle_v2 as manager
from agicore.trading import ema_pullback_fees_and_slippage_v2 as accounting
from agicore.trading import synthetic_entry_replay_v2 as entry_replay
from agicore.trading import synthetic_exit_replay_v2 as exit_replay
from agicore.trading import synthetic_risk_replay_v2 as risk_replay
from agicore.trading.synthetic_confirmation_fixture_v2 import generate_confirmation_fixture


class SimulatedPowerLoss(BaseException):
    """Interrupt after a durable checkpoint without creating a failure report."""


def _interrupt_at(name):
    def interrupt(checkpoint):
        if checkpoint == name:
            raise SimulatedPowerLoss(name)

    return interrupt


@pytest.mark.skipif(
    sys.platform != "linux", reason="requires Linux signal masks and process groups"
)
def test_interruption_after_popen_before_wait_cleans_up_child(tmp_path, monkeypatch):
    """The child is owned even before entering the wait loop."""
    original_popen, original_wait4 = subprocess.Popen, os.wait4
    before_mask = signal.pthread_sigmask(signal.SIG_BLOCK, set())
    source, first_line = inspect.getsourcelines(manager._run_process)
    spawn = next(i for i, line in enumerate(source) if "child = subprocess.Popen(" in line)
    boundary = next(
        first_line + i
        for i in range(spawn + 1, len(source))
        if "signal.pthread_sigmask(signal.SIG_SETMASK, parent_signal_mask)" in source[i]
    )
    original_error = KeyboardInterrupt("interruption after Popen")
    old_trace = sys.gettrace()
    child = None

    def sleeping_child(_command, **kwargs):
        nonlocal child
        child = original_popen(
            [sys.executable, "-B", "-c", "import time; time.sleep(30)"], **kwargs
        )
        return child

    def interrupt_at_boundary(frame, event, arg):
        if (
            frame.f_code is manager._run_process.__code__
            and event == "line"
            and frame.f_lineno == boundary
        ):
            raise original_error
        return interrupt_at_boundary

    try:
        with monkeypatch.context() as scoped:
            scoped.setattr(manager.subprocess, "Popen", sleeping_child)
            try:
                sys.settrace(interrupt_at_boundary)
                with pytest.raises(KeyboardInterrupt) as caught:
                    manager._run_process(tmp_path, manager.WORKER, "worker", 1, 5, "events")
            finally:
                sys.settrace(old_trace)
        assert caught.value is original_error
        assert child is not None and child.returncode == -signal.SIGKILL
        with pytest.raises(ChildProcessError):
            original_wait4(child.pid, os.WNOHANG)
        assert signal.pthread_sigmask(signal.SIG_BLOCK, set()) == before_mask
    finally:
        if child is not None and child.returncode is None:
            with suppress(ProcessLookupError):
                os.killpg(child.pid, signal.SIGKILL)
            with suppress(ChildProcessError):
                original_wait4(child.pid, 0)


@pytest.mark.skipif(
    sys.platform != "linux", reason="requires Linux signal masks and process groups"
)
@pytest.mark.parametrize("signum", [signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT])
def test_signal_during_popen_is_deferred_until_child_is_owned(tmp_path, monkeypatch, signum):
    """Handled termination signals during spawn must not orphan a child."""
    original_popen, original_wait4 = subprocess.Popen, os.wait4
    original_handler = signal.getsignal(signum)
    before_mask = signal.pthread_sigmask(signal.SIG_BLOCK, set())
    if signum in before_mask:
        pytest.skip("signal is already blocked by the test environment")
    child = None

    def raise_interruption(_signum, _frame):
        raise KeyboardInterrupt("handled termination signal")

    def signal_before_return(_command, **kwargs):
        nonlocal child
        child = original_popen(
            [sys.executable, "-B", "-c", "import time; time.sleep(30)"], **kwargs
        )
        os.kill(os.getpid(), signum)
        return child

    try:
        signal.signal(signum, raise_interruption)
        with monkeypatch.context() as scoped:
            scoped.setattr(manager.subprocess, "Popen", signal_before_return)
            with pytest.raises(KeyboardInterrupt):
                manager._run_process(tmp_path, manager.WORKER, "worker", 1, 5, "events")
        assert child is not None and child.returncode == -signal.SIGKILL
        with pytest.raises(ChildProcessError):
            original_wait4(child.pid, os.WNOHANG)
        assert signal.pthread_sigmask(signal.SIG_BLOCK, set()) == before_mask
    finally:
        signal.signal(signum, original_handler)
        if child is not None and child.returncode is None:
            with suppress(ProcessLookupError):
                os.killpg(child.pid, signal.SIGKILL)
            with suppress(ChildProcessError):
                original_wait4(child.pid, 0)


@pytest.mark.skipif(sys.platform != "linux", reason="requires Linux signal masks")
def test_spawn_does_not_leave_termination_signals_blocked_in_child(tmp_path, monkeypatch):
    original_popen = subprocess.Popen
    before_mask = signal.pthread_sigmask(signal.SIG_BLOCK, set())
    script = (
        "import json, signal; "
        "print(json.dumps(sorted(int(s) for s in signal.pthread_sigmask(signal.SIG_BLOCK, set()))))"
    )

    def inspect_child_mask(_command, **kwargs):
        return original_popen([sys.executable, "-B", "-c", script], **kwargs)

    monkeypatch.setattr(manager.subprocess, "Popen", inspect_child_mask)
    outcome = manager._run_process(tmp_path, manager.WORKER, "worker", 1, 5, "events")
    assert outcome["exit_code"] == 0
    child_mask = set(json.loads((tmp_path / "worker.stdout").read_text()))
    assert child_mask == {int(sig) for sig in before_mask}


@pytest.mark.skipif(sys.platform != "linux", reason="requires Linux waitid and process groups")
@pytest.mark.parametrize("error_type", [KeyboardInterrupt, SystemExit, RuntimeError])
@pytest.mark.parametrize("group_lookup_fails", [False, True])
def test_wait_interruption_kills_and_reaps_child_while_parent_lives(
    tmp_path, monkeypatch, error_type, group_lookup_fails
):
    """An embedded caller may catch the interruption and keep running."""
    original_popen = subprocess.Popen
    original_wait4 = os.wait4
    original_killpg = os.killpg
    child = None
    interrupted = False
    original_error = error_type("simulated wait interruption")

    def start_sleeping_child(_command, **kwargs):
        nonlocal child
        child = original_popen(
            [sys.executable, "-B", "-c", "import time; time.sleep(30)"], **kwargs
        )
        return child

    def interrupt_once(pid, options):
        nonlocal interrupted
        if not interrupted:
            interrupted = True
            raise original_error
        return original_wait4(pid, options)

    try:
        with monkeypatch.context() as scoped:
            scoped.setattr(manager.subprocess, "Popen", start_sleeping_child)
            scoped.setattr(manager.os, "wait4", interrupt_once)
            if group_lookup_fails:

                def no_group(*_args):
                    raise ProcessLookupError("simulated group race")

                scoped.setattr(manager.os, "killpg", no_group)
            with pytest.raises(error_type) as caught:
                manager._run_process(tmp_path, manager.WORKER, "worker", 1, 5, "events")
        assert caught.value is original_error
        assert child is not None and child.returncode == -signal.SIGKILL
        with pytest.raises(ChildProcessError):
            original_wait4(child.pid, os.WNOHANG)
    finally:
        # The test cleans up its own child even if the implementation regresses.
        if child is not None and child.returncode is None:
            with suppress(ProcessLookupError):
                original_killpg(child.pid, signal.SIGKILL)
            with suppress(ChildProcessError):
                original_wait4(child.pid, 0)


@pytest.mark.skipif(sys.platform != "linux", reason="requires Linux waitid and process groups")
def test_interruption_after_reap_does_not_signal_a_reused_pid(tmp_path, monkeypatch):
    original_popen, original_wait4 = subprocess.Popen, os.wait4
    child = None
    reaped = False
    original_error = KeyboardInterrupt("interrupt after wait4 reaped child")

    def start_short_child(_command, **kwargs):
        nonlocal child
        child = original_popen([sys.executable, "-B", "-c", "pass"], **kwargs)
        return child

    def reap_then_interrupt(pid, _options):
        nonlocal reaped
        original_wait4(pid, 0)
        reaped = True
        raise original_error

    def must_not_signal(*_args):
        pytest.fail("the child PID was already reaped and could have been reused")

    try:
        with monkeypatch.context() as scoped:
            scoped.setattr(manager.subprocess, "Popen", start_short_child)
            scoped.setattr(manager.os, "wait4", reap_then_interrupt)
            scoped.setattr(manager.os, "killpg", must_not_signal)
            with pytest.raises(KeyboardInterrupt) as caught:
                manager._run_process(tmp_path, manager.WORKER, "worker", 1, 5, "events")
        assert caught.value is original_error
        assert reaped is True
    finally:
        if child is not None and not reaped:
            with suppress(ProcessLookupError):
                os.killpg(child.pid, signal.SIGKILL)
            with suppress(ChildProcessError):
                original_wait4(child.pid, 0)


@pytest.mark.parametrize(
    "replay_function,validator",
    [
        (risk_replay.replay_risk_native, manager._valid_risk_replay),
        (entry_replay.replay_entry_native, manager._valid_entry_replay),
        (exit_replay.replay_exit_native, manager._valid_exit_replay),
    ],
)
@pytest.mark.parametrize(
    "field,kind",
    [
        ("approved_quantity", "bool"),
        ("approved_quantity", "float"),
        ("confirmation_bar_index", "float"),
        ("sizing_decision_known_at_bar", "float"),
    ],
)
def test_rejected_risk_evidence_requires_exact_json_integer_types(
    replay_function, validator, field, kind
):
    # A rejected profile never enters the synthetic position/accounting path.
    raw = generate_confirmation_fixture("confirmation-long-rejected-v1", 39)
    replay = replay_function(raw)
    worker = {"input_sha256": hashlib.sha256(raw).hexdigest()}
    assert replay["risk"]["decision"] == "REJECT"
    assert validator(replay, worker) is True
    altered = json.loads(json.dumps(replay))
    original = altered["risk"][field]
    assert type(original) is int
    altered["risk"][field] = bool(original) if kind == "bool" else float(original)
    assert validator(altered, worker) is False


@pytest.fixture
def blocked_accounting(monkeypatch):
    """These synthetic boundary tests may not calculate costs or PnL."""

    def forbidden(*_args, **_kwargs):
        pytest.fail("synthetic validation called the accounting layer")

    for name in (
        "calculate_fill_cost_v2",
        "account_entry_fill_v2",
        "account_structural_stop_fill_v2",
        "account_ema20_exit_fill_v2",
        "report_usd_cents_v2",
    ):
        monkeypatch.setattr(accounting, name, forbidden)
    for record in (
        accounting.FillCostRecordV2,
        accounting.TradeCostRecordV2,
        accounting.FeesAndSlippageBookV2,
    ):
        monkeypatch.setattr(record, "__post_init__", forbidden)


@pytest.mark.parametrize("direction", ["long", "short"])
@pytest.mark.parametrize(
    ("field", "forged"),
    [
        ("trigger_bar_index", True),
        ("trigger_bar_index", 37.0),
        ("trigger_bar_index", 35),
        ("trigger_bar_index", 39),
        ("entry_bar_index", 36.0),
        ("confirmation_bar_index", 35.0),
        ("trigger_phase", "ENTRY_OPEN"),
        ("trigger_known_at", "Open[e]"),
        ("exact_intrabar_timestamp", "2026-01-01T00:00:00Z"),
    ],
)
def test_exit_precheck_rejects_forged_stop_timing(direction, field, forged, blocked_accounting):
    raw = generate_confirmation_fixture(f"confirmation-{direction}-exit-stop-v1", 39)
    replay = exit_replay.replay_exit_native(raw)
    worker = {"input_sha256": hashlib.sha256(raw).hexdigest()}
    assert replay["stop_reason"] == "EXIT_STRUCTURAL_STOP_FILLED"
    assert manager._valid_exit_replay(replay, worker) is True
    altered = json.loads(json.dumps(replay))
    altered["exit"][field] = forged
    assert manager._valid_exit_replay(altered, worker) is False


@pytest.mark.parametrize("direction", ["long", "short"])
@pytest.mark.parametrize(
    ("location", "field", "forged"),
    [
        ("signal", "exit_signal_bar_index", True),
        ("signal", "exit_signal_bar_index", 36.0),
        ("signal", "exit_signal_bar_index", 35),
        ("exit", "exit_execution_bar_index", True),
        ("exit", "exit_execution_bar_index", 37.0),
        ("exit", "exit_execution_bar_index", 38),
        ("exit", "exit_execution_bar_index", 39),
        ("signal", "quantity", True),
        ("signal", "quantity", 2.0),
        ("signal", "quantity", 1),
        ("signal", "quantity", 3),
    ],
)
def test_exit_precheck_rejects_forged_ema_fill(
    direction, location, field, forged, blocked_accounting
):
    raw = generate_confirmation_fixture(f"confirmation-{direction}-exit-ema-v1", 39)
    replay = exit_replay.replay_exit_native(raw)
    worker = {"input_sha256": hashlib.sha256(raw).hexdigest()}
    assert replay["stop_reason"] == "EXIT_EMA20_FILLED"
    assert manager._valid_exit_replay(replay, worker) is True
    altered = json.loads(json.dumps(replay))
    target = altered["exit"]["signal"] if location == "signal" else altered["exit"]
    target[field] = forged
    assert manager._valid_exit_replay(altered, worker) is False


@pytest.mark.parametrize("case", ["missing", "late"])
def test_exit_precheck_fails_closed_for_unapproved_entry_expirations(case, blocked_accounting):
    rows = generate_confirmation_fixture("confirmation-long-v1", 39).decode("ascii").splitlines()
    if case == "missing":
        rows = rows[:36]
    else:
        for index in (36, 37, 38):
            fields = rows[index].split(";")
            timestamp = datetime.strptime(fields[0], "%Y%m%d %H%M%S") + timedelta(minutes=1)
            fields[0] = timestamp.strftime("%Y%m%d %H%M%S")
            rows[index] = ";".join(fields)
    raw = ("\n".join(rows) + "\n").encode("ascii")
    replay = exit_replay.replay_exit_native(raw)
    worker = {"input_sha256": hashlib.sha256(raw).hexdigest()}
    assert (
        replay["stop_reason"]
        == {
            "missing": "ENTRY_EXPIRED_NO_EXECUTION",
            "late": "ENTRY_EXPIRED_EXECUTION_GAP",
        }[case]
    )
    # No allowed fixed Manager profile produces an expiration.  A future
    # extension must validate its complete invariants before accepting one.
    assert manager._valid_exit_replay(replay, worker) is False


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
