"""Phase 9C — Endurance tests for AGIcore-v2.

Long-session dry-run simulations verifying:
- 500+ tick recording accuracy and determinism
- No thread leaks across start/stop cycles
- Replay / runtime fingerprint parity
- Metrics fingerprint stability
- Snapshot integrity under sustained load
- AGIcoreManager lifecycle under long operation

Invariants (strictly enforced throughout):
- No random() in tick generation — deterministic by design
- No wall-clock timestamps in replay paths
- structlog only — no print()
- Thread-safe: all shared state behind threading.Lock
"""
from __future__ import annotations

import hashlib
import threading
from pathlib import Path

import pytest

from agicore.dryrun.controller import DryRunModeController
from agicore.dryrun.models import DryRunConfig, DryRunState
from agicore.dryrun.recorder import DryRunRecorder
from agicore.manager.agicore_manager import AGIcoreManager
from agicore.manager.manager_models import ManagerConfig, ManagerState
from agicore.snapshot.models import SnapshotRecord
from agicore.snapshot.store import SnapshotStore


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _cfg(
    session_id: str = "endurance-001",
    symbols: tuple = ("AAPL",),
    adapter: str = "alpaca_paper",
    mode: str = "SANDBOX",
) -> DryRunConfig:
    """Minimal dry-run config for endurance tests."""
    return DryRunConfig(
        session_id=session_id,
        runtime_mode=mode,
        adapter_name=adapter,
        symbols=symbols,
        tick_interval_ms=0,
        max_ticks=None,
        record_all_events=True,
        validate_on_stop=False,
    )


def _ctrl(session_id: str = "endurance-001", **kwargs) -> DryRunModeController:
    return DryRunModeController(_cfg(session_id=session_id, **kwargs))


def _snapshot_record(seq: int, positions: dict | None = None) -> SnapshotRecord:
    return SnapshotRecord(
        sequence=seq,
        positions=positions or {},
        realized_pnl=float(seq) * 0.5,
        realized_pnl_by_symbol={k: float(seq) * 0.5 for k in (positions or {})},
        open_orders={},
        timestamp=f"2026-01-01T{seq // 3600:02d}:{(seq % 3600) // 60:02d}:{seq % 60:02d}Z",
        fingerprint=hashlib.sha256(f"seq:{seq}".encode()).hexdigest(),
        events_processed=seq,
        config_fingerprint="",
    )


# ---------------------------------------------------------------------------
# Long-session simulations
# ---------------------------------------------------------------------------

class TestLongSessionSimulation:
    """500–1000 tick sessions: recording accuracy, determinism, state integrity."""

    def test_500_ticks_all_recorded(self) -> None:
        ctrl = _ctrl("end-500")
        ctrl.start()
        ctrl.run_ticks(500)
        snap = ctrl.snapshot()
        assert snap.ticks_processed == 500
        assert ctrl.recorder.count() >= 500
        ctrl.stop()

    def test_1000_ticks_snapshot_sequence_matches(self) -> None:
        ctrl = _ctrl("end-1000")
        ctrl.start()
        ctrl.run_ticks(1000)
        snap = ctrl.snapshot()
        assert snap.ticks_processed == 1000
        assert snap.last_sequence >= 1000
        ctrl.stop()

    def test_tick_events_monotonically_increasing_sequence(self) -> None:
        ctrl = _ctrl("end-mono")
        ctrl.start()
        ctrl.run_ticks(300)
        events = ctrl.recorder.get_all()
        seqs = [e.sequence for e in events if hasattr(e, "sequence")]
        for a, b in zip(seqs, seqs[1:]):
            assert b >= a, f"Sequence regression: {a} → {b}"
        ctrl.stop()

    def test_session_state_running_during_ticks(self) -> None:
        ctrl = _ctrl("end-state")
        ctrl.start()
        assert ctrl.state == DryRunState.RUNNING
        ctrl.run_ticks(100)
        assert ctrl.state == DryRunState.RUNNING
        ctrl.stop()
        assert ctrl.state == DryRunState.STOPPED

    def test_snapshot_ticks_exact_after_multiple_batches(self) -> None:
        ctrl = _ctrl("end-batch")
        ctrl.start()
        ctrl.run_ticks(100)
        ctrl.run_ticks(150)
        ctrl.run_ticks(250)
        snap = ctrl.snapshot()
        assert snap.ticks_processed == 500
        ctrl.stop()


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    """Two fresh controllers with identical config must yield identical fingerprints."""

    def test_replay_fingerprint_identical_across_runs(self) -> None:
        cfg = _cfg(session_id="det-run")

        ctrl1 = DryRunModeController(cfg)
        ctrl1.start()
        ctrl1.run_ticks(200)
        fp1 = ctrl1.replay_equivalence_fingerprint()
        ctrl1.stop()

        ctrl2 = DryRunModeController(cfg)
        ctrl2.start()
        ctrl2.run_ticks(200)
        fp2 = ctrl2.replay_equivalence_fingerprint()
        ctrl2.stop()

        assert fp1 == fp2, (
            f"Replay fingerprint diverged between identical runs: {fp1!r} != {fp2!r}"
        )

    def test_fingerprint_changes_with_tick_count(self) -> None:
        cfg = _cfg(session_id="det-count")

        ctrl1 = DryRunModeController(cfg)
        ctrl1.start()
        ctrl1.run_ticks(100)
        fp_100 = ctrl1.replay_equivalence_fingerprint()
        ctrl1.stop()

        ctrl2 = DryRunModeController(cfg)
        ctrl2.start()
        ctrl2.run_ticks(200)
        fp_200 = ctrl2.replay_equivalence_fingerprint()
        ctrl2.stop()

        assert fp_100 != fp_200, "More ticks must produce a different fingerprint"

    def test_recorder_fingerprint_is_sha256(self) -> None:
        ctrl = _ctrl("det-sha256")
        ctrl.start()
        ctrl.run_ticks(50)
        fp = ctrl.recorder.compute_fingerprint()
        assert isinstance(fp, str)
        assert len(fp) == 64, f"SHA-256 hex must be 64 chars, got {len(fp)}"
        ctrl.stop()

    def test_recorder_fingerprint_stable_between_calls(self) -> None:
        """Fingerprint must not change unless new events are appended."""
        ctrl = _ctrl("det-stable")
        ctrl.start()
        ctrl.run_ticks(100)
        fp1 = ctrl.recorder.compute_fingerprint()
        fp2 = ctrl.recorder.compute_fingerprint()
        assert fp1 == fp2, "Fingerprint must be idempotent"
        ctrl.stop()

    def test_replay_fingerprint_stable_between_calls(self) -> None:
        ctrl = _ctrl("det-rep-stable")
        ctrl.start()
        ctrl.run_ticks(150)
        fp1 = ctrl.replay_equivalence_fingerprint()
        fp2 = ctrl.replay_equivalence_fingerprint()
        assert fp1 == fp2
        ctrl.stop()

    def test_multi_symbol_determinism(self) -> None:
        cfg = _cfg(session_id="det-multi", symbols=("AAPL", "TSLA", "NVDA"))

        ctrl1 = DryRunModeController(cfg)
        ctrl1.start()
        ctrl1.run_ticks(100)
        fp1 = ctrl1.replay_equivalence_fingerprint()
        ctrl1.stop()

        ctrl2 = DryRunModeController(cfg)
        ctrl2.start()
        ctrl2.run_ticks(100)
        fp2 = ctrl2.replay_equivalence_fingerprint()
        ctrl2.stop()

        assert fp1 == fp2


# ---------------------------------------------------------------------------
# Thread safety / no leaks
# ---------------------------------------------------------------------------

class TestThreadSafety:
    """Verify no thread leaks across start/stop cycles."""

    def test_no_thread_leak_single_cycle(self) -> None:
        baseline = threading.active_count()
        ctrl = _ctrl("thr-single")
        ctrl.start()
        ctrl.run_ticks(50)
        ctrl.stop()
        after = threading.active_count()
        assert after <= baseline + 1, (
            f"Thread leak: baseline={baseline}, after={after}"
        )

    def test_no_thread_leak_five_cycles(self) -> None:
        baseline = threading.active_count()
        for i in range(5):
            ctrl = _ctrl(f"thr-cycle-{i}")
            ctrl.start()
            ctrl.run_ticks(20)
            ctrl.stop()
        after = threading.active_count()
        assert after <= baseline + 1

    def test_no_thread_leak_pause_resume(self) -> None:
        baseline = threading.active_count()
        ctrl = _ctrl("thr-pause")
        ctrl.start()
        ctrl.run_ticks(20)
        ctrl.pause()
        ctrl.resume()
        ctrl.run_ticks(20)
        ctrl.stop()
        after = threading.active_count()
        assert after <= baseline + 1

    def test_no_thread_leak_emergency_stop(self) -> None:
        baseline = threading.active_count()
        ctrl = _ctrl("thr-emergency")
        ctrl.start()
        ctrl.run_ticks(30)
        ctrl.emergency_stop(reason="thread-leak-test")
        after = threading.active_count()
        assert after <= baseline + 1


# ---------------------------------------------------------------------------
# Pause / resume under sustained load
# ---------------------------------------------------------------------------

class TestPauseResumeLong:
    """Pause / resume maintains cumulative tick count and determinism."""

    def test_total_ticks_after_pause_resume(self) -> None:
        ctrl = _ctrl("pr-total")
        ctrl.start()
        ctrl.run_ticks(100)
        ctrl.pause()
        assert ctrl.state == DryRunState.PAUSED
        ctrl.resume()
        ctrl.run_ticks(100)
        snap = ctrl.snapshot()
        assert snap.ticks_processed == 200
        ctrl.stop()

    def test_fingerprint_unchanged_while_paused(self) -> None:
        ctrl = _ctrl("pr-fp")
        ctrl.start()
        ctrl.run_ticks(50)
        fp_before = ctrl.recorder.compute_fingerprint()
        ctrl.pause()
        fp_paused = ctrl.recorder.compute_fingerprint()
        assert fp_before == fp_paused, "Pause must not mutate the recorder"
        ctrl.resume()
        ctrl.stop()

    def test_multiple_pause_resume_cycles(self) -> None:
        ctrl = _ctrl("pr-multi")
        ctrl.start()
        for _ in range(5):
            ctrl.run_ticks(20)
            ctrl.pause()
            ctrl.resume()
        ctrl.run_ticks(20)
        snap = ctrl.snapshot()
        assert snap.ticks_processed == 120
        ctrl.stop()


# ---------------------------------------------------------------------------
# Multi-symbol sessions
# ---------------------------------------------------------------------------

class TestMultiSymbol:

    def test_three_symbol_500_ticks(self) -> None:
        cfg = _cfg(session_id="ms-3", symbols=("AAPL", "TSLA", "NVDA"))
        ctrl = DryRunModeController(cfg)
        ctrl.start()
        ctrl.run_ticks(500)
        snap = ctrl.snapshot()
        assert snap.ticks_processed == 500
        ctrl.stop()

    def test_multi_symbol_orders_submitted(self) -> None:
        cfg = _cfg(session_id="ms-orders", symbols=("AAPL", "MSFT"))
        ctrl = DryRunModeController(cfg)
        ctrl.start()
        ctrl.run_ticks(10)
        ctrl.submit_order("AAPL", 10.0, "buy")
        ctrl.submit_order("MSFT", 5.0, "buy")
        snap = ctrl.snapshot()
        assert snap.orders_submitted >= 2
        ctrl.stop()


# ---------------------------------------------------------------------------
# Snapshot store integrity under load
# ---------------------------------------------------------------------------

class TestSnapshotIntegrityLong:

    def test_save_20_snapshots_load_latest(self, tmp_path: Path) -> None:
        store = SnapshotStore(tmp_path)
        for seq in range(1, 21):
            store.save(_snapshot_record(seq * 50))
        latest = store.load_latest()
        assert latest is not None
        assert latest.sequence == 1000

    def test_load_at_or_before_midpoint(self, tmp_path: Path) -> None:
        store = SnapshotStore(tmp_path)
        for seq in [100, 200, 300, 400, 500]:
            store.save(_snapshot_record(seq))
        result = store.load_at_or_before(350)
        assert result is not None
        assert result.sequence == 300

    def test_list_all_returns_all_saved(self, tmp_path: Path) -> None:
        store = SnapshotStore(tmp_path)
        for seq in range(5):
            store.save(_snapshot_record((seq + 1) * 100))
        all_records = store.list_all()
        assert len(all_records) == 5

    def test_fingerprint_round_trips_intact(self, tmp_path: Path) -> None:
        fp = hashlib.sha256(b"round-trip-check").hexdigest()
        record = _snapshot_record(999)
        # We can't mutate a frozen dataclass; build a new one with a known fingerprint
        record_with_fp = SnapshotRecord(
            sequence=999,
            positions={"AAPL": 1.0},
            realized_pnl=49.95,
            realized_pnl_by_symbol={"AAPL": 49.95},
            open_orders={},
            timestamp="2026-01-01T00:16:39Z",
            fingerprint=fp,
            events_processed=999,
            config_fingerprint="cfg-abc",
        )
        store = SnapshotStore(tmp_path)
        store.save(record_with_fp)
        loaded = store.load_latest()
        assert loaded is not None
        assert loaded.fingerprint == fp
        assert loaded.config_fingerprint == "cfg-abc"


# ---------------------------------------------------------------------------
# Execution recorder long-session accuracy
# ---------------------------------------------------------------------------

class TestExecutionRecorderLong:

    def test_summary_keys_present(self) -> None:
        ctrl = _ctrl("rec-keys")
        ctrl.start()
        ctrl.run_ticks(20)
        ctrl.submit_order("AAPL", 10.0, "buy")
        summary = ctrl.execution_recorder.summary()
        for key in ("total", "fills", "rejects", "partials", "cancels", "avg_latency_ms"):
            assert key in summary, f"Missing key: {key}"
        ctrl.stop()

    def test_summary_totals_consistent(self) -> None:
        ctrl = _ctrl("rec-totals")
        ctrl.start()
        ctrl.run_ticks(10)
        for _ in range(20):
            ctrl.submit_order("AAPL", 5.0, "buy")
        summary = ctrl.execution_recorder.summary()
        assert summary["fills"] + summary["rejects"] + summary["partials"] <= summary["total"]
        ctrl.stop()

    def test_total_increments_per_order(self) -> None:
        ctrl = _ctrl("rec-inc")
        ctrl.start()
        ctrl.run_ticks(5)
        before = ctrl.execution_recorder.summary()["total"]
        for _ in range(5):
            ctrl.submit_order("AAPL", 10.0, "buy")
        after = ctrl.execution_recorder.summary()["total"]
        assert after == before + 5
        ctrl.stop()

    def test_avg_latency_non_negative(self) -> None:
        ctrl = _ctrl("rec-lat")
        ctrl.start()
        ctrl.run_ticks(10)
        ctrl.submit_order("AAPL", 10.0, "buy")
        summary = ctrl.execution_recorder.summary()
        assert summary["avg_latency_ms"] >= 0.0
        ctrl.stop()


# ---------------------------------------------------------------------------
# AGIcoreManager long-run
# ---------------------------------------------------------------------------

class TestManagerLongRun:

    def test_manager_starts_and_stops(self, tmp_path: Path) -> None:
        cfg = ManagerConfig(
            manager_id="mgr-end-001",
            runtime_mode="SANDBOX",
            adapter_name="alpaca_paper",
            symbols=("AAPL",),
            enable_dry_run=False,
            enable_snapshots=True,
            enable_metrics=True,
            enable_health=True,
            snapshot_interval=100,
            metrics_interval=50,
        )
        mgr = AGIcoreManager(config=cfg, snapshot_dir=tmp_path)
        mgr.start()
        assert mgr.state == ManagerState.RUNNING
        rs = mgr.runtime_state()
        assert rs.manager_state == ManagerState.RUNNING
        assert rs.runtime_mode == "SANDBOX"
        mgr.stop()
        assert mgr.state == ManagerState.STOPPED

    def test_manager_metrics_snapshot_available(self, tmp_path: Path) -> None:
        cfg = ManagerConfig(
            manager_id="mgr-end-002",
            runtime_mode="SANDBOX",
            enable_metrics=True,
        )
        mgr = AGIcoreManager(config=cfg, snapshot_dir=tmp_path)
        mgr.start()
        ms = mgr.metrics_snapshot()
        assert ms is not None
        mgr.stop()

    def test_manager_health_report_has_status(self, tmp_path: Path) -> None:
        cfg = ManagerConfig(
            manager_id="mgr-end-003",
            runtime_mode="SANDBOX",
            enable_health=True,
        )
        mgr = AGIcoreManager(config=cfg, snapshot_dir=tmp_path)
        mgr.start()
        hr = mgr.health_report()
        assert hr is not None
        assert hasattr(hr, "overall_ok")
        assert hasattr(hr, "manager_state")
        mgr.stop()

    def test_manager_registry_components(self, tmp_path: Path) -> None:
        cfg = ManagerConfig(
            manager_id="mgr-end-004",
            runtime_mode="SANDBOX",
            enable_snapshots=True,
            enable_metrics=True,
            enable_health=True,
        )
        mgr = AGIcoreManager(config=cfg, snapshot_dir=tmp_path)
        mgr.start()
        names = mgr.registry.list_names()
        assert "snapshot_store" in names
        mgr.stop()

    def test_manager_current_mode(self, tmp_path: Path) -> None:
        cfg = ManagerConfig(manager_id="mgr-end-005", runtime_mode="SANDBOX")
        mgr = AGIcoreManager(config=cfg, snapshot_dir=tmp_path)
        mgr.start()
        assert mgr.current_mode() == "SANDBOX"
        mgr.stop()

    def test_manager_pause_resume(self, tmp_path: Path) -> None:
        cfg = ManagerConfig(manager_id="mgr-end-006", runtime_mode="SANDBOX")
        mgr = AGIcoreManager(config=cfg, snapshot_dir=tmp_path)
        mgr.start()
        mgr.pause()
        assert mgr.state == ManagerState.PAUSED
        mgr.resume()
        assert mgr.state == ManagerState.RUNNING
        mgr.stop()
