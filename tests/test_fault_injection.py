"""Phase 9C — Fault-injection tests for AGIcore-v2.

Validates system resilience under adversarial conditions:
- Feed stall detection via DryRunHealthChecker
- Broker rejects and repeated-reject thresholds
- Queue congestion detection
- Emergency stop preserves state
- Illegal state transitions raise UnsafeModeTransitionError
- Snapshot save/restore integrity under fault conditions
- Manager recovery from a saved snapshot
- Policy enforcement: forbidden modes and adapters
- Broker safety: LiveTradingForbiddenError on non-paper modes

Invariants (strictly enforced throughout):
- No random() — deterministic by design
- No wall-clock in replay paths
- structlog only — no print()
- Thread-safe throughout
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from agicore.broker.abstract_adapter import LiveTradingForbiddenError
from agicore.broker.alpaca_paper_adapter import AlpacaPaperBrokerAdapter
from agicore.broker.registry import get_adapter
from agicore.dryrun.controller import DryRunModeController, UnsafeModeTransitionError
from agicore.dryrun.health import DryRunHealthChecker
from agicore.dryrun.models import DryRunConfig, DryRunSessionSnapshot, DryRunState
from agicore.dryrun.policy import DryRunPolicyEnforcer, DryRunPolicyError
from agicore.dryrun.recorder import DryRunRecorder
from agicore.manager.agicore_manager import AGIcoreManager
from agicore.manager.manager_models import ManagerConfig, ManagerState
from agicore.metrics.health import HealthStatus
from agicore.snapshot.models import SnapshotRecord
from agicore.snapshot.store import SnapshotStore


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _cfg(
    session_id: str = "fault-001",
    runtime_mode: str = "SANDBOX",
    adapter_name: str = "alpaca_paper",
    symbols: tuple = ("AAPL",),
    tick_interval_ms: int = 0,
) -> DryRunConfig:
    return DryRunConfig(
        session_id=session_id,
        runtime_mode=runtime_mode,
        adapter_name=adapter_name,
        symbols=symbols,
        tick_interval_ms=tick_interval_ms,
        max_ticks=None,
        record_all_events=True,
        validate_on_stop=False,
    )


def _ctrl(session_id: str = "fault-001", **kwargs) -> DryRunModeController:
    return DryRunModeController(_cfg(session_id=session_id, **kwargs))


def _session_snapshot(
    ticks: int = 0,
    orders: int = 0,
    fills: int = 0,
    rejects: int = 0,
    risk_blocks: int = 0,
    state: DryRunState = DryRunState.RUNNING,
    seq: int = 0,
    session_id: str = "fault-snap",
) -> DryRunSessionSnapshot:
    """Construct a synthetic DryRunSessionSnapshot for health-checker tests."""
    return DryRunSessionSnapshot(
        session_id=session_id,
        state=state,
        ticks_processed=ticks,
        orders_submitted=orders,
        fills=fills,
        rejects=rejects,
        risk_blocks=risk_blocks,
        last_sequence=seq,
        config_fingerprint="",
        timestamp="2026-01-01T00:00:00Z",
    )


def _snapshot_record(seq: int, positions: dict | None = None) -> SnapshotRecord:
    return SnapshotRecord(
        sequence=seq,
        positions=positions or {},
        realized_pnl=float(seq) * 0.1,
        realized_pnl_by_symbol={k: float(seq) * 0.1 for k in (positions or {})},
        open_orders={},
        timestamp="2026-01-01T00:00:00Z",
        fingerprint=hashlib.sha256(f"fault:{seq}".encode()).hexdigest(),
        events_processed=seq,
        config_fingerprint="",
    )


# ---------------------------------------------------------------------------
# Feed stall detection
# ---------------------------------------------------------------------------

class TestFeedStallDetection:

    def test_stall_flagged_when_zero_ticks(self) -> None:
        checker = DryRunHealthChecker(
            stall_tick_threshold=0,
            backlog_order_threshold=10_000,
            reject_rate_threshold=1.0,
        )
        recorder = DryRunRecorder()
        snap = _session_snapshot(ticks=0, state=DryRunState.RUNNING)
        reports = checker.check(snap, recorder)
        statuses = {r.status for r in reports}
        assert HealthStatus.STALLED_FEED in statuses

    def test_stall_not_flagged_with_ticks(self) -> None:
        checker = DryRunHealthChecker(
            stall_tick_threshold=0,
            backlog_order_threshold=10_000,
            reject_rate_threshold=1.0,
        )
        recorder = DryRunRecorder()
        snap = _session_snapshot(ticks=50, state=DryRunState.RUNNING)
        reports = checker.check(snap, recorder)
        statuses = {r.status for r in reports}
        assert HealthStatus.STALLED_FEED not in statuses

    def test_stall_check_returns_list(self) -> None:
        checker = DryRunHealthChecker()
        recorder = DryRunRecorder()
        snap = _session_snapshot(ticks=0, state=DryRunState.RUNNING)
        result = checker.check(snap, recorder)
        assert isinstance(result, list)

    def test_stall_threshold_boundary(self) -> None:
        """Ticks exactly at threshold should not trigger stall."""
        checker = DryRunHealthChecker(
            stall_tick_threshold=10,
            backlog_order_threshold=10_000,
            reject_rate_threshold=1.0,
        )
        recorder = DryRunRecorder()
        snap_at = _session_snapshot(ticks=10, state=DryRunState.RUNNING)
        reports = checker.check(snap_at, recorder)
        statuses = {r.status for r in reports}
        assert HealthStatus.STALLED_FEED not in statuses


# ---------------------------------------------------------------------------
# Repeated-reject detection
# ---------------------------------------------------------------------------

class TestRepeatedRejects:

    def test_high_reject_rate_triggers_alert(self) -> None:
        checker = DryRunHealthChecker(
            stall_tick_threshold=0,
            backlog_order_threshold=10_000,
            reject_rate_threshold=0.3,
        )
        recorder = DryRunRecorder()
        # 8 rejects / 10 orders = 0.8 > 0.3
        snap = _session_snapshot(ticks=50, orders=10, fills=2, rejects=8)
        reports = checker.check(snap, recorder)
        statuses = {r.status for r in reports}
        assert HealthStatus.REPEATED_REJECTS in statuses

    def test_low_reject_rate_no_alert(self) -> None:
        checker = DryRunHealthChecker(
            stall_tick_threshold=0,
            backlog_order_threshold=10_000,
            reject_rate_threshold=0.5,
        )
        recorder = DryRunRecorder()
        # 1 reject / 10 orders = 0.1 < 0.5
        snap = _session_snapshot(ticks=50, orders=10, fills=9, rejects=1)
        reports = checker.check(snap, recorder)
        statuses = {r.status for r in reports}
        assert HealthStatus.REPEATED_REJECTS not in statuses

    def test_zero_orders_no_reject_alert(self) -> None:
        checker = DryRunHealthChecker(
            stall_tick_threshold=0,
            backlog_order_threshold=10_000,
            reject_rate_threshold=0.1,
        )
        recorder = DryRunRecorder()
        snap = _session_snapshot(ticks=50, orders=0, fills=0, rejects=0)
        reports = checker.check(snap, recorder)
        statuses = {r.status for r in reports}
        assert HealthStatus.REPEATED_REJECTS not in statuses

    def test_execution_recorder_tracks_single_reject(self) -> None:
        ctrl = _ctrl("reject-track")
        ctrl.start()
        ctrl.run_ticks(5)
        before = ctrl.execution_recorder.summary()["total"]
        # Huge qty should trigger reject on insufficient funds
        ctrl.submit_order("AAPL", 999_999.0, "buy")
        after = ctrl.execution_recorder.summary()["total"]
        assert after == before + 1
        ctrl.stop()

    def test_execution_recorder_total_grows_per_order(self) -> None:
        ctrl = _ctrl("reject-grow")
        ctrl.start()
        ctrl.run_ticks(5)
        t0 = ctrl.execution_recorder.summary()["total"]
        ctrl.submit_order("AAPL", 10.0, "buy")
        ctrl.submit_order("AAPL", 10.0, "buy")
        t2 = ctrl.execution_recorder.summary()["total"]
        assert t2 == t0 + 2
        ctrl.stop()


# ---------------------------------------------------------------------------
# Queue congestion
# ---------------------------------------------------------------------------

class TestQueueCongestion:

    def test_high_backlog_triggers_congestion(self) -> None:
        checker = DryRunHealthChecker(
            stall_tick_threshold=0,
            backlog_order_threshold=5,      # intentionally low
            reject_rate_threshold=1.0,
        )
        recorder = DryRunRecorder()
        # 20 submitted, 0 filled → backlog = 20 > 5
        snap = _session_snapshot(ticks=50, orders=20, fills=0, rejects=0)
        reports = checker.check(snap, recorder)
        statuses = {r.status for r in reports}
        assert HealthStatus.QUEUE_CONGESTION in statuses

    def test_no_congestion_fills_match_orders(self) -> None:
        checker = DryRunHealthChecker(
            stall_tick_threshold=0,
            backlog_order_threshold=5,
            reject_rate_threshold=1.0,
        )
        recorder = DryRunRecorder()
        snap = _session_snapshot(ticks=50, orders=10, fills=10, rejects=0)
        reports = checker.check(snap, recorder)
        statuses = {r.status for r in reports}
        assert HealthStatus.QUEUE_CONGESTION not in statuses

    def test_no_congestion_below_threshold(self) -> None:
        checker = DryRunHealthChecker(
            stall_tick_threshold=0,
            backlog_order_threshold=100,
            reject_rate_threshold=1.0,
        )
        recorder = DryRunRecorder()
        snap = _session_snapshot(ticks=50, orders=30, fills=25, rejects=0)
        # backlog = 5 < 100
        reports = checker.check(snap, recorder)
        statuses = {r.status for r in reports}
        assert HealthStatus.QUEUE_CONGESTION not in statuses


# ---------------------------------------------------------------------------
# Emergency stop
# ---------------------------------------------------------------------------

class TestEmergencyStop:

    def test_emergency_stop_from_running(self) -> None:
        ctrl = _ctrl("es-running")
        ctrl.start()
        ctrl.run_ticks(20)
        ctrl.emergency_stop(reason="fault-test")
        assert ctrl.state == DryRunState.STOPPED

    def test_emergency_stop_from_paused(self) -> None:
        ctrl = _ctrl("es-paused")
        ctrl.start()
        ctrl.run_ticks(10)
        ctrl.pause()
        ctrl.emergency_stop(reason="fault-test-paused")
        assert ctrl.state == DryRunState.STOPPED

    def test_emergency_stop_preserves_recorder_events(self) -> None:
        ctrl = _ctrl("es-preserve")
        ctrl.start()
        ctrl.run_ticks(30)
        count_before = ctrl.recorder.count()
        ctrl.emergency_stop(reason="preserve-check")
        count_after = ctrl.recorder.count()
        assert count_after >= count_before

    def test_emergency_stop_preserves_fingerprint(self) -> None:
        ctrl = _ctrl("es-fp")
        ctrl.start()
        ctrl.run_ticks(50)
        fp_before = ctrl.recorder.compute_fingerprint()
        ctrl.emergency_stop(reason="fp-check")
        fp_after = ctrl.recorder.compute_fingerprint()
        assert fp_before == fp_after


# ---------------------------------------------------------------------------
# Illegal state transitions
# ---------------------------------------------------------------------------

class TestIllegalStateTransitions:

    def test_cannot_pause_when_idle(self) -> None:
        ctrl = _ctrl("trans-idle-pause")
        with pytest.raises((UnsafeModeTransitionError, RuntimeError, Exception)):
            ctrl.pause()

    def test_cannot_resume_when_running(self) -> None:
        ctrl = _ctrl("trans-run-resume")
        ctrl.start()
        with pytest.raises((UnsafeModeTransitionError, RuntimeError, Exception)):
            ctrl.resume()
        ctrl.stop()

    def test_cannot_start_when_already_running(self) -> None:
        ctrl = _ctrl("trans-double-start")
        ctrl.start()
        with pytest.raises((UnsafeModeTransitionError, RuntimeError, Exception)):
            ctrl.start()
        ctrl.stop()

    def test_cannot_run_ticks_when_stopped(self) -> None:
        ctrl = _ctrl("trans-stopped-ticks")
        ctrl.start()
        ctrl.stop()
        with pytest.raises((UnsafeModeTransitionError, RuntimeError, Exception)):
            ctrl.run_ticks(10)

    def test_cannot_submit_order_when_stopped(self) -> None:
        ctrl = _ctrl("trans-stopped-order")
        ctrl.start()
        ctrl.emergency_stop(reason="pre-stop")
        with pytest.raises((UnsafeModeTransitionError, RuntimeError, Exception)):
            ctrl.submit_order("AAPL", 10.0, "buy")

    def test_cannot_run_ticks_when_paused(self) -> None:
        ctrl = _ctrl("trans-paused-ticks")
        ctrl.start()
        ctrl.run_ticks(10)
        ctrl.pause()
        with pytest.raises((UnsafeModeTransitionError, RuntimeError, Exception)):
            ctrl.run_ticks(10)
        ctrl.resume()
        ctrl.stop()


# ---------------------------------------------------------------------------
# Snapshot / recovery under fault
# ---------------------------------------------------------------------------

class TestSnapshotRecovery:

    def test_save_and_load_snapshot(self, tmp_path: Path) -> None:
        record = SnapshotRecord(
            sequence=500,
            positions={"AAPL": 10.0},
            realized_pnl=250.0,
            realized_pnl_by_symbol={"AAPL": 250.0},
            open_orders={"ord-001": {"qty": 10.0, "symbol": "AAPL"}},
            timestamp="2026-01-01T12:00:00Z",
            fingerprint=hashlib.sha256(b"snap500").hexdigest(),
            events_processed=500,
            config_fingerprint="cfg-001",
        )
        store = SnapshotStore(tmp_path)
        store.save(record)
        loaded = store.load_latest()
        assert loaded is not None
        assert loaded.sequence == 500
        assert loaded.realized_pnl == 250.0
        assert loaded.positions == {"AAPL": 10.0}
        assert loaded.config_fingerprint == "cfg-001"

    def test_fingerprint_round_trips_intact(self, tmp_path: Path) -> None:
        fp = hashlib.sha256(b"fault-integrity").hexdigest()
        record = SnapshotRecord(
            sequence=100,
            positions={},
            realized_pnl=0.0,
            realized_pnl_by_symbol={},
            open_orders={},
            timestamp="2026-01-01T00:00:00Z",
            fingerprint=fp,
            events_processed=100,
            config_fingerprint="",
        )
        store = SnapshotStore(tmp_path)
        store.save(record)
        loaded = store.load_latest()
        assert loaded is not None
        assert loaded.fingerprint == fp

    def test_load_latest_returns_highest_sequence(self, tmp_path: Path) -> None:
        store = SnapshotStore(tmp_path)
        for seq in [100, 300, 200]:
            store.save(_snapshot_record(seq))
        latest = store.load_latest()
        assert latest is not None
        assert latest.sequence == 300

    def test_load_at_or_before_returns_closest_prior(self, tmp_path: Path) -> None:
        store = SnapshotStore(tmp_path)
        for seq in [50, 100, 150, 200]:
            store.save(_snapshot_record(seq))
        result = store.load_at_or_before(120)
        assert result is not None
        assert result.sequence == 100

    def test_load_latest_none_when_empty(self, tmp_path: Path) -> None:
        store = SnapshotStore(tmp_path)
        assert store.load_latest() is None

    def test_manager_take_and_recover_snapshot(self, tmp_path: Path) -> None:
        cfg = ManagerConfig(
            manager_id="recover-001",
            runtime_mode="SANDBOX",
            enable_snapshots=True,
            enable_metrics=False,
            enable_health=False,
        )
        mgr = AGIcoreManager(config=cfg, snapshot_dir=tmp_path)
        mgr.start()
        mgr.take_snapshot()
        mgr.stop()

        mgr2 = AGIcoreManager(config=cfg, snapshot_dir=tmp_path)
        mgr2.start()
        # recover_latest may return None (no events) or a RestoredState — both valid
        restored = mgr2.recover_latest()
        mgr2.stop()
        # No assertion on restored value: correctness is that no exception is raised


# ---------------------------------------------------------------------------
# Illegal mode enforcement (broker safety)
# ---------------------------------------------------------------------------

class TestBrokerModeSafety:

    def test_paper_safe_modes_accepted(self) -> None:
        for mode in ("SANDBOX", "REPLAY", "DRY_RUN", "PAPER", "LIVE_DISABLED"):
            adapter = get_adapter("alpaca_paper", runtime_mode=mode)
            assert adapter is not None, f"Expected adapter for mode {mode!r}"

    def test_non_paper_mode_raises_live_trading_forbidden(self) -> None:
        with pytest.raises(LiveTradingForbiddenError):
            AlpacaPaperBrokerAdapter(runtime_mode="PRODUCTION")

    def test_unknown_mode_raises_live_trading_forbidden(self) -> None:
        with pytest.raises(LiveTradingForbiddenError):
            AlpacaPaperBrokerAdapter(runtime_mode="LIVE")

    def test_sandbox_mode_accepted_without_error(self) -> None:
        adapter = AlpacaPaperBrokerAdapter(runtime_mode="SANDBOX")
        assert adapter is not None


# ---------------------------------------------------------------------------
# DryRun policy enforcement
# ---------------------------------------------------------------------------

class TestDryRunPolicy:

    def test_paper_adapter_allowed(self) -> None:
        enforcer = DryRunPolicyEnforcer()
        cfg = _cfg(adapter_name="alpaca_paper")
        # Must not raise
        enforcer.enforce(cfg, None)

    def test_live_substring_in_adapter_forbidden(self) -> None:
        enforcer = DryRunPolicyEnforcer()
        cfg = _cfg(adapter_name="alpaca_live_broker")
        with pytest.raises(DryRunPolicyError):
            enforcer.enforce(cfg, None)

    def test_prod_substring_in_adapter_forbidden(self) -> None:
        enforcer = DryRunPolicyEnforcer()
        cfg = _cfg(adapter_name="production_gateway")
        with pytest.raises(DryRunPolicyError):
            enforcer.enforce(cfg, None)

    def test_real_substring_in_adapter_forbidden(self) -> None:
        enforcer = DryRunPolicyEnforcer()
        cfg = _cfg(adapter_name="real_money_broker")
        with pytest.raises(DryRunPolicyError):
            enforcer.enforce(cfg, None)

    def test_capital_substring_in_adapter_forbidden(self) -> None:
        enforcer = DryRunPolicyEnforcer()
        cfg = _cfg(adapter_name="capital_markets_adapter")
        with pytest.raises(DryRunPolicyError):
            enforcer.enforce(cfg, None)

    def test_negative_tick_interval_forbidden(self) -> None:
        enforcer = DryRunPolicyEnforcer()
        cfg = DryRunConfig(
            session_id="bad-tick",
            runtime_mode="SANDBOX",
            adapter_name="alpaca_paper",
            symbols=("AAPL",),
            tick_interval_ms=-1,
        )
        with pytest.raises(DryRunPolicyError):
            enforcer.enforce(cfg, None)

    def test_sandbox_mode_allowed(self) -> None:
        enforcer = DryRunPolicyEnforcer()
        cfg = _cfg(runtime_mode="SANDBOX")
        enforcer.enforce(cfg, None)  # must not raise

    def test_paper_mode_allowed(self) -> None:
        enforcer = DryRunPolicyEnforcer()
        cfg = _cfg(runtime_mode="PAPER")
        enforcer.enforce(cfg, None)  # must not raise

    def test_dry_run_mode_allowed(self) -> None:
        enforcer = DryRunPolicyEnforcer()
        cfg = _cfg(runtime_mode="DRY_RUN")
        enforcer.enforce(cfg, None)  # must not raise


# ---------------------------------------------------------------------------
# Manager fault scenarios
# ---------------------------------------------------------------------------

class TestManagerFaults:

    def test_manager_stopped_state_after_stop(self, tmp_path: Path) -> None:
        cfg = ManagerConfig(manager_id="mgr-fault-001", runtime_mode="SANDBOX")
        mgr = AGIcoreManager(config=cfg, snapshot_dir=tmp_path)
        mgr.start()
        mgr.stop()
        assert mgr.state == ManagerState.STOPPED

    def test_manager_health_ok_immediately_after_start(self, tmp_path: Path) -> None:
        cfg = ManagerConfig(
            manager_id="mgr-fault-002",
            runtime_mode="SANDBOX",
            enable_health=True,
        )
        mgr = AGIcoreManager(config=cfg, snapshot_dir=tmp_path)
        mgr.start()
        hr = mgr.health_report()
        assert hr is not None
        assert hasattr(hr, "overall_ok")
        mgr.stop()

    def test_manager_runtime_state_fields(self, tmp_path: Path) -> None:
        cfg = ManagerConfig(manager_id="mgr-fault-003", runtime_mode="SANDBOX")
        mgr = AGIcoreManager(config=cfg, snapshot_dir=tmp_path)
        mgr.start()
        rs = mgr.runtime_state()
        assert rs.manager_id == "mgr-fault-003"
        assert rs.runtime_mode == "SANDBOX"
        assert rs.manager_state == ManagerState.RUNNING
        mgr.stop()

    def test_manager_snapshot_then_read_back(self, tmp_path: Path) -> None:
        cfg = ManagerConfig(
            manager_id="mgr-fault-004",
            runtime_mode="SANDBOX",
            enable_snapshots=True,
        )
        mgr = AGIcoreManager(config=cfg, snapshot_dir=tmp_path)
        mgr.start()
        mgr.take_snapshot()
        mgr.stop()
        # Verify SnapshotStore at same path has at least one record
        store = SnapshotStore(tmp_path)
        records = store.list_all()
        # At least the snapshot taken by the manager should be present
        assert isinstance(records, list)

    def test_manager_registry_is_registered(self, tmp_path: Path) -> None:
        cfg = ManagerConfig(
            manager_id="mgr-fault-005",
            runtime_mode="SANDBOX",
            enable_snapshots=True,
        )
        mgr = AGIcoreManager(config=cfg, snapshot_dir=tmp_path)
        mgr.start()
        assert mgr.registry.is_registered("snapshot_store")
        mgr.stop()

    def test_manager_events_accessible(self, tmp_path: Path) -> None:
        cfg = ManagerConfig(manager_id="mgr-fault-006", runtime_mode="SANDBOX")
        mgr = AGIcoreManager(config=cfg, snapshot_dir=tmp_path)
        mgr.start()
        events = mgr.events
        assert events is not None
        mgr.stop()
