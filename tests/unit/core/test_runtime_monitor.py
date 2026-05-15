"""Unit tests for RuntimeMonitor."""
from __future__ import annotations

import threading
import time
from collections.abc import Iterator

import pytest

from agicore.core.events import (
    EVT_TASK_COMPLETED,
    EVT_TASK_CREATED,
    EVT_TASK_DISPATCHED,
    EVT_TASK_FAILED,
    EVT_TASK_RETRIED,
    EVT_TASK_STARTED,
    Event,
    EventBus,
)
from agicore.core.runtime_monitor import HEARTBEAT_EVENT_TYPE, RuntimeMonitor
from agicore.core.shutdown import ShutdownHandler
from agicore.core.task_queue import TaskQueue
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.init_schema import init_schema
from agicore.l2_memory.services.memory_service import MemoryService


# ---------------------------------------------------------------- Fixtures
@pytest.fixture()
def engine() -> Iterator[SqlAlchemyEngine]:
    eng = SqlAlchemyEngine("sqlite:///:memory:")
    init_schema(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def memory(engine: SqlAlchemyEngine) -> MemoryService:
    return MemoryService(engine)


@pytest.fixture()
def event_bus() -> EventBus:
    return EventBus()


@pytest.fixture()
def monitor(
    memory: MemoryService, event_bus: EventBus, engine: SqlAlchemyEngine
) -> Iterator[RuntimeMonitor]:
    m = RuntimeMonitor(memory=memory, event_bus=event_bus, engine=engine)
    yield m
    m.detach()


# ---------------------------------------------------------------- get_runtime_status
def test_get_runtime_status_basic(monitor: RuntimeMonitor) -> None:
    s = monitor.get_runtime_status()
    assert "started_at_utc" in s
    assert s["uptime_s"] >= 0.0
    assert s["is_stopping"] is False
    assert s["handlers_registered"] == []
    assert s["queue_enqueued_total"] is None
    assert s["queue_depth_pending"] == 0
    assert s["last_event_at_utc"] is None
    assert s["last_heartbeat_at_utc"] is None
    assert s["last_heartbeat_counter"] is None


def test_get_runtime_status_uptime_increases(monitor: RuntimeMonitor) -> None:
    u1 = monitor.get_runtime_status()["uptime_s"]
    time.sleep(0.05)
    u2 = monitor.get_runtime_status()["uptime_s"]
    assert u2 > u1


def test_runtime_status_with_shutdown_handler(
    memory: MemoryService, event_bus: EventBus
) -> None:
    sh = ShutdownHandler()
    m = RuntimeMonitor(memory=memory, event_bus=event_bus, shutdown=sh)
    try:
        assert m.get_runtime_status()["is_stopping"] is False
        sh.trigger()
        assert m.get_runtime_status()["is_stopping"] is True
    finally:
        m.detach()


def test_runtime_status_handlers_listed_via_registry(
    memory: MemoryService, event_bus: EventBus
) -> None:
    """Registry duck-typed via list_types(). Use a stub to avoid l4_planning import."""
    class _StubRegistry:
        def list_types(self):
            return ["agent.echo", "agent.heartbeat"]

    m = RuntimeMonitor(memory=memory, event_bus=event_bus, registry=_StubRegistry())  # type: ignore[arg-type]
    try:
        assert m.get_runtime_status()["handlers_registered"] == [
            "agent.echo",
            "agent.heartbeat",
        ]
    finally:
        m.detach()


# ---------------------------------------------------------------- Counters
def test_counters_initially_zero(monitor: RuntimeMonitor) -> None:
    metrics = monitor.get_metrics()
    assert metrics["tasks_created"] == 0
    assert metrics["tasks_dispatched"] == 0
    assert metrics["tasks_started"] == 0
    assert metrics["tasks_completed"] == 0
    assert metrics["tasks_failed"] == 0
    assert metrics["tasks_retried"] == 0
    assert metrics["tasks_cancelled"] == 0
    assert metrics["events_total"] == 0
    assert metrics["events_by_type"] == {}
    assert metrics["last_error"] is None


def test_counters_increment_on_lifecycle_events(
    monitor: RuntimeMonitor, event_bus: EventBus
) -> None:
    event_bus.emit(EVT_TASK_CREATED, task_id="t-1")
    event_bus.emit(EVT_TASK_DISPATCHED, task_id="t-1")
    event_bus.emit(EVT_TASK_STARTED, task_id="t-1")
    event_bus.emit(EVT_TASK_RETRIED, task_id="t-1", attempt=2)
    event_bus.emit(EVT_TASK_COMPLETED, task_id="t-1")

    m = monitor.get_metrics()
    assert m["tasks_created"] == 1
    assert m["tasks_dispatched"] == 1
    assert m["tasks_started"] == 1
    assert m["tasks_retried"] == 1
    assert m["tasks_completed"] == 1
    assert m["events_total"] == 5
    assert m["events_by_type"][EVT_TASK_CREATED] == 1


def test_last_error_captured_on_failure(
    monitor: RuntimeMonitor, event_bus: EventBus
) -> None:
    event_bus.emit(EVT_TASK_FAILED, task_id="t-1", error="boom")
    m = monitor.get_metrics()
    assert m["tasks_failed"] == 1
    assert m["last_error"] is not None
    assert m["last_error"]["task_id"] == "t-1"
    assert m["last_error"]["error"] == "boom"


def test_heartbeat_tracking(
    monitor: RuntimeMonitor, event_bus: EventBus
) -> None:
    event_bus.emit(HEARTBEAT_EVENT_TYPE, task_id="hb-1", counter=1)
    event_bus.emit(HEARTBEAT_EVENT_TYPE, task_id="hb-2", counter=2)
    s = monitor.get_runtime_status()
    assert s["last_heartbeat_counter"] == 2
    assert s["last_heartbeat_at_utc"] is not None


def test_heartbeat_invalid_counter_ignored(
    monitor: RuntimeMonitor, event_bus: EventBus
) -> None:
    event_bus.emit(HEARTBEAT_EVENT_TYPE, task_id="hb-1", counter="not-a-number")
    s = monitor.get_runtime_status()
    # last_heartbeat_at est défini, last_heartbeat_counter reste None
    assert s["last_heartbeat_at_utc"] is not None
    assert s["last_heartbeat_counter"] is None


def test_unknown_events_still_tallied_in_total(
    monitor: RuntimeMonitor, event_bus: EventBus
) -> None:
    event_bus.emit("custom.event", x=1)
    event_bus.emit("custom.event", x=2)
    m = monitor.get_metrics()
    assert m["events_total"] == 2
    assert m["events_by_type"]["custom.event"] == 2


# ---------------------------------------------------------------- reset_metrics
def test_reset_metrics_zeros_counters(
    monitor: RuntimeMonitor, event_bus: EventBus
) -> None:
    event_bus.emit(EVT_TASK_CREATED, task_id="t-1")
    event_bus.emit(EVT_TASK_FAILED, task_id="t-1", error="x")
    event_bus.emit(HEARTBEAT_EVENT_TYPE, task_id="hb-1", counter=5)

    monitor.reset_metrics()
    m = monitor.get_metrics()
    s = monitor.get_runtime_status()
    assert m["tasks_created"] == 0
    assert m["tasks_failed"] == 0
    assert m["last_error"] is None
    assert m["events_total"] == 0
    assert s["last_heartbeat_counter"] is None
    assert s["last_heartbeat_at_utc"] is None


def test_reset_preserves_uptime(monitor: RuntimeMonitor) -> None:
    time.sleep(0.05)
    u_before = monitor.get_runtime_status()["uptime_s"]
    monitor.reset_metrics()
    u_after = monitor.get_runtime_status()["uptime_s"]
    assert u_after >= u_before  # uptime continue à monter


# ---------------------------------------------------------------- get_recent_activity
def test_recent_activity_includes_persisted_events(
    monitor: RuntimeMonitor, memory: MemoryService
) -> None:
    memory.create_event("custom.x", task_id="t-1", payload={"v": 1})
    memory.create_event("custom.x", task_id="t-2", payload={"v": 2})
    activity = monitor.get_recent_activity(limit=10)
    assert activity["limit"] == 10
    assert len(activity["events"]) == 2
    assert activity["events"][0]["event_type"] == "custom.x"
    assert activity["pending_tasks"] == []
    assert activity["completed_tasks"] == []
    assert activity["failed_tasks"] == []


def test_recent_activity_invalid_limit() -> None:
    bus = EventBus()
    eng = SqlAlchemyEngine("sqlite:///:memory:")
    init_schema(eng)
    mem = MemoryService(eng)
    m = RuntimeMonitor(memory=mem, event_bus=bus)
    try:
        with pytest.raises(ValueError):
            m.get_recent_activity(limit=0)
        with pytest.raises(ValueError):
            m.get_recent_activity(limit=-1)
    finally:
        m.detach()
        eng.dispose()


# ---------------------------------------------------------------- detach
def test_detach_stops_receiving_events(
    memory: MemoryService, event_bus: EventBus
) -> None:
    m = RuntimeMonitor(memory=memory, event_bus=event_bus)
    event_bus.emit(EVT_TASK_CREATED, task_id="t-1")
    assert m.get_metrics()["tasks_created"] == 1
    m.detach()
    event_bus.emit(EVT_TASK_CREATED, task_id="t-2")
    assert m.get_metrics()["tasks_created"] == 1  # n'a pas augmenté


def test_detach_idempotent(memory: MemoryService, event_bus: EventBus) -> None:
    m = RuntimeMonitor(memory=memory, event_bus=event_bus)
    m.detach()
    m.detach()  # idempotent — pas d'exception


def test_context_manager_auto_detach(
    memory: MemoryService, event_bus: EventBus
) -> None:
    with RuntimeMonitor(memory=memory, event_bus=event_bus) as m:
        event_bus.emit(EVT_TASK_CREATED, task_id="t-1")
        assert m.get_metrics()["tasks_created"] == 1
    # Après __exit__ : aucune mise à jour de métrique
    event_bus.emit(EVT_TASK_CREATED, task_id="t-2")
    assert m.get_metrics()["tasks_created"] == 1


# ---------------------------------------------------------------- Concurrence
def test_concurrent_metric_updates_are_consistent(
    memory: MemoryService, event_bus: EventBus
) -> None:
    """Plusieurs threads émettent des events ; le moniteur doit aboutir à un
    compte cohérent et exact, sans data race."""
    monitor = RuntimeMonitor(memory=memory, event_bus=event_bus)
    try:
        N_THREADS = 8
        N_EMITS = 250
        barrier = threading.Barrier(N_THREADS + 1)

        def worker(thread_id: int) -> None:
            barrier.wait()
            for i in range(N_EMITS):
                event_bus.emit(EVT_TASK_CREATED, task_id=f"t-{thread_id}-{i}")

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(N_THREADS)]
        for t in threads:
            t.start()
        barrier.wait()  # libère tous les workers en même temps

        # Pendant les écritures, on lit les métriques en boucle pour forcer la
        # contention. On vérifie juste l'absence d'exception.
        for _ in range(50):
            _ = monitor.get_metrics()
            _ = monitor.get_runtime_status()

        for t in threads:
            t.join(timeout=10.0)

        m = monitor.get_metrics()
        assert m["tasks_created"] == N_THREADS * N_EMITS
        assert m["events_total"] == N_THREADS * N_EMITS
    finally:
        monitor.detach()


def test_handler_exception_does_not_break_subscription(
    memory: MemoryService, event_bus: EventBus
) -> None:
    """Une exception côté EventBus ne doit pas désabonner le moniteur."""
    monitor = RuntimeMonitor(memory=memory, event_bus=event_bus)
    try:
        # Un autre handler qui crash
        event_bus.subscribe(EVT_TASK_CREATED, lambda ev: (_ for _ in ()).throw(RuntimeError("x")))
        event_bus.emit(EVT_TASK_CREATED, task_id="t-1")
        event_bus.emit(EVT_TASK_CREATED, task_id="t-2")
        # Le moniteur compte malgré l'exception du voisin
        assert monitor.get_metrics()["tasks_created"] == 2
    finally:
        monitor.detach()
