"""Integration test — RuntimeMonitor wired to a real RuntimeEngine."""
from __future__ import annotations

import threading
import time

from agicore.agents.echo_agent import TASK_TYPE_ECHO, EchoAgent
from agicore.agents.heartbeat_agent import (
    EVT_HEARTBEAT_TICK,
    TASK_TYPE_HEARTBEAT,
    HeartbeatAgent,
    HeartbeatScheduler,
)
from agicore.core.runtime_monitor import HEARTBEAT_EVENT_TYPE, RuntimeMonitor
from agicore.core.retry import RetryPolicy
from agicore.l2_memory.schemas.task import TaskCreate
from agicore.l4_planning.runtime import RuntimeEngine


def _build_monitor(rt: RuntimeEngine) -> RuntimeMonitor:
    return RuntimeMonitor(
        memory=rt.memory,
        event_bus=rt.event_bus,
        engine=rt.orchestrator._engine,  # type: ignore[attr-defined]
        queue=rt.queue,
        registry=rt.registry,
        shutdown=rt.shutdown_handler,
    )


def test_monitor_reflects_runtime_lifecycle() -> None:
    """End-to-end : run a few tasks and verify all metrics are coherent."""
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    monitor = _build_monitor(rt)
    try:
        rt.register_handler(TASK_TYPE_ECHO, EchoAgent(rt.memory, rt.event_bus))

        # Status initial
        s0 = monitor.get_runtime_status()
        assert TASK_TYPE_ECHO in s0["handlers_registered"]
        assert s0["queue_enqueued_total"] == 0
        assert s0["queue_depth_pending"] == 0

        # Submit + execute 3 tasks
        for i in range(3):
            rt.submit(TaskCreate(id=f"t-{i}", task_type=TASK_TYPE_ECHO, payload={"i": i}))

        # Avant exécution : 3 pending
        s_before = monitor.get_runtime_status()
        assert s_before["queue_enqueued_total"] == 3
        assert s_before["queue_depth_pending"] == 3

        rt.run_once()

        # Après exécution
        s_after = monitor.get_runtime_status()
        assert s_after["queue_depth_pending"] == 0
        assert s_after["uptime_s"] > 0

        m = monitor.get_metrics()
        assert m["tasks_created"] == 3
        assert m["tasks_started"] == 3
        assert m["tasks_completed"] == 3
        assert m["tasks_failed"] == 0
        assert m["events_total"] >= 3 * 3  # created + started + completed minimum

        activity = monitor.get_recent_activity(limit=10)
        assert len(activity["completed_tasks"]) == 3
        assert all(t["task_type"] == TASK_TYPE_ECHO for t in activity["completed_tasks"])
        assert len(activity["pending_tasks"]) == 0
        assert len(activity["failed_tasks"]) == 0
    finally:
        monitor.detach()
        rt.shutdown()


def test_monitor_captures_failure() -> None:
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    monitor = _build_monitor(rt)
    try:
        rt.register_handler("tx.boom", lambda t: (_ for _ in ()).throw(RuntimeError("doom")))
        rt.submit(TaskCreate(id="t-fail", task_type="tx.boom"))
        rt.run_once()

        m = monitor.get_metrics()
        assert m["tasks_failed"] == 1
        assert m["last_error"] is not None
        assert m["last_error"]["task_id"] == "t-fail"
        assert "doom" in (m["last_error"]["error"] or "")

        activity = monitor.get_recent_activity(limit=10)
        assert len(activity["failed_tasks"]) == 1
        assert activity["failed_tasks"][0]["id"] == "t-fail"
    finally:
        monitor.detach()
        rt.shutdown()


def test_monitor_observes_heartbeat() -> None:
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.5,
    )
    monitor = _build_monitor(rt)
    try:
        rt.register_handler(
            TASK_TYPE_HEARTBEAT, HeartbeatAgent(rt.memory, rt.event_bus)
        )

        scheduler = HeartbeatScheduler(rt.queue, interval_s=0.04, poll_resolution_s=0.01)
        consumer = threading.Thread(
            target=lambda: rt.run_forever(max_iterations=200),
            name="runtime-consumer",
        )
        consumer.start()
        scheduler.start()
        time.sleep(0.2)
        scheduler.stop()
        rt.stop()
        consumer.join(timeout=5.0)

        s = monitor.get_runtime_status()
        assert s["last_heartbeat_counter"] is not None
        assert s["last_heartbeat_counter"] >= 2
        assert s["last_heartbeat_at_utc"] is not None

        m = monitor.get_metrics()
        assert m["events_by_type"].get(EVT_HEARTBEAT_TICK, 0) >= 2
        assert HEARTBEAT_EVENT_TYPE == EVT_HEARTBEAT_TICK
    finally:
        monitor.detach()
        rt.shutdown()


def test_monitor_visibility_during_graceful_shutdown() -> None:
    """is_stopping must flip True the moment shutdown is triggered."""
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    monitor = _build_monitor(rt)
    try:
        assert monitor.get_runtime_status()["is_stopping"] is False
        rt.stop()  # triggers shutdown handler
        assert monitor.get_runtime_status()["is_stopping"] is True
    finally:
        monitor.detach()
        rt.shutdown()


def test_reset_metrics_keeps_runtime_observability_alive() -> None:
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    monitor = _build_monitor(rt)
    try:
        rt.register_handler(TASK_TYPE_ECHO, EchoAgent(rt.memory, rt.event_bus))
        rt.submit(TaskCreate(id="t-1", task_type=TASK_TYPE_ECHO))
        rt.run_once()
        assert monitor.get_metrics()["tasks_completed"] == 1

        monitor.reset_metrics()
        assert monitor.get_metrics()["tasks_completed"] == 0

        # Le moniteur reste abonné — un nouvel event est compté
        rt.submit(TaskCreate(id="t-2", task_type=TASK_TYPE_ECHO))
        rt.run_once()
        assert monitor.get_metrics()["tasks_completed"] == 1
    finally:
        monitor.detach()
        rt.shutdown()
