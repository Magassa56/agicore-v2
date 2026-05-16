"""Unit tests for HeartbeatAgent and HeartbeatScheduler."""
from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock

import pytest

from agicore.agents.heartbeat_agent import (
    AGENT_ID,
    EVT_HEARTBEAT_TICK,
    RUNTIME_STATE_ACTIVE,
    RUNTIME_STATE_DEGRADED,
    RUNTIME_STATE_STOPPING,
    TASK_TYPE_HEARTBEAT,
    HeartbeatAgent,
    HeartbeatScheduler,
)
from agicore.core.events import EventBus
from agicore.core.task_queue import TaskQueue
from agicore.l2_memory.schemas.task import TaskCreate, TaskRead
from agicore.l2_memory.services.memory_service import MemoryService


# ============================================================================
# HeartbeatAgent tests
# ============================================================================
class TestHeartbeatAgent:
    def test_returns_structured_feedback(
        self, memory: MemoryService, make_task
    ) -> None:
        agent = HeartbeatAgent(memory)
        task = make_task(task_id="t-1", task_type=TASK_TYPE_HEARTBEAT)

        feedback = agent(task)

        # Required fields per spec
        assert "tick_id" in feedback and feedback["tick_id"].startswith("hb-tick-")
        assert "timestamp" in feedback
        assert "counter" in feedback and feedback["counter"] == 1
        assert "latency_ms" in feedback and feedback["latency_ms"] >= 0
        assert "runtime_state" in feedback
        # Bonus identifiers
        assert feedback["agent_id"] == AGENT_ID
        assert feedback["task_id"] == "t-1"

    def test_counter_increments(self, memory: MemoryService, make_task) -> None:
        agent = HeartbeatAgent(memory)
        for i in range(5):
            agent(make_task(task_id=f"t-{i}"))
        assert agent.counter == 5

    def test_tick_id_unique_per_call(
        self, memory: MemoryService, make_task
    ) -> None:
        agent = HeartbeatAgent(memory)
        ids = {agent(make_task(task_id=f"t-{i}"))["tick_id"] for i in range(10)}
        assert len(ids) == 10

    def test_persists_event_in_memory(
        self, memory: MemoryService, make_task
    ) -> None:
        agent = HeartbeatAgent(memory)
        agent(make_task(task_id="t-7"))

        events = memory.get_recent_events(event_type=EVT_HEARTBEAT_TICK, limit=10)
        assert len(events) == 1
        ev = events[0]
        assert ev.task_id == "t-7"
        assert ev.agent_id == AGENT_ID
        assert ev.payload["counter"] == 1
        assert ev.payload["runtime_state"] == RUNTIME_STATE_ACTIVE
        assert ev.payload["tick_id"].startswith("hb-tick-")

    def test_emits_bus_event(
        self, memory: MemoryService, event_bus: EventBus, make_task
    ) -> None:
        seen = []
        event_bus.subscribe(EVT_HEARTBEAT_TICK, lambda ev: seen.append(ev))

        agent = HeartbeatAgent(memory, event_bus)
        agent(make_task())

        assert len(seen) == 1
        assert seen[0].payload["counter"] == 1
        assert seen[0].payload["tick_id"].startswith("hb-tick-")

    def test_works_without_bus(
        self, memory: MemoryService, make_task
    ) -> None:
        agent = HeartbeatAgent(memory, event_bus=None)
        feedback = agent(make_task())
        assert feedback["counter"] == 1

    def test_runtime_state_provider_called(
        self, memory: MemoryService, make_task
    ) -> None:
        states = iter(["warming_up", "active", "stopping"])
        agent = HeartbeatAgent(
            memory, runtime_state_provider=lambda: next(states)
        )
        f1 = agent(make_task(task_id="t-1"))
        f2 = agent(make_task(task_id="t-2"))
        f3 = agent(make_task(task_id="t-3"))
        assert f1["runtime_state"] == "warming_up"
        assert f2["runtime_state"] == "active"
        assert f3["runtime_state"] == "stopping"

    def test_default_runtime_state_is_active(
        self, memory: MemoryService, make_task
    ) -> None:
        agent = HeartbeatAgent(memory)
        f = agent(make_task())
        assert f["runtime_state"] == RUNTIME_STATE_ACTIVE

    def test_state_provider_failure_falls_back_to_degraded(
        self, memory: MemoryService, make_task
    ) -> None:
        def boom():
            raise RuntimeError("provider broken")

        agent = HeartbeatAgent(memory, runtime_state_provider=boom)
        f = agent(make_task())
        assert f["runtime_state"] == RUNTIME_STATE_DEGRADED

    def test_canonical_constants(self) -> None:
        assert TASK_TYPE_HEARTBEAT == "agent.heartbeat"
        assert EVT_HEARTBEAT_TICK == "agent.heartbeat.tick"
        assert AGENT_ID == "heartbeat_agent"
        assert RUNTIME_STATE_ACTIVE == "active"
        assert RUNTIME_STATE_STOPPING == "stopping"


# ============================================================================
# HeartbeatScheduler tests
# ============================================================================
def _stub_orchestrator() -> MagicMock:
    """Minimal orchestrator stub so we can build a real TaskQueue."""
    from datetime import datetime, timezone
    orch = MagicMock()

    def submit(dto: TaskCreate) -> TaskRead:
        now = datetime.now(timezone.utc)
        return TaskRead(
            id=dto.id, task_type=dto.task_type, status="pending",
            assigned_to=dto.assigned_to, payload=dto.payload, result=None,
            error=None, created_at=now, updated_at=now,
        )

    orch.submit_task = submit
    return orch


class TestHeartbeatScheduler:
    def _build(self, *, interval_s: float = 0.05) -> tuple[HeartbeatScheduler, TaskQueue]:
        queue = TaskQueue(_stub_orchestrator())
        sch = HeartbeatScheduler(queue, interval_s=interval_s, poll_resolution_s=0.01)
        return sch, queue

    def test_invalid_args_rejected(self) -> None:
        queue = TaskQueue(_stub_orchestrator())
        with pytest.raises(ValueError):
            HeartbeatScheduler(queue, interval_s=0)
        with pytest.raises(ValueError):
            HeartbeatScheduler(queue, interval_s=-1.0)
        with pytest.raises(ValueError):
            HeartbeatScheduler(queue, interval_s=1.0, poll_resolution_s=0)

    def test_lifecycle_start_stop(self) -> None:
        sch, _ = self._build(interval_s=0.05)
        assert not sch.is_running()
        sch.start()
        assert sch.is_running()
        sch.stop()
        assert not sch.is_running()

    def test_start_idempotent(self) -> None:
        sch, _ = self._build()
        sch.start()
        sch.start()  # ne crée pas un second thread
        assert sch.is_running()
        sch.stop()

    def test_stop_idempotent_when_never_started(self) -> None:
        sch, _ = self._build()
        sch.stop()  # ne crash pas

    def test_periodic_enqueue_observed(self) -> None:
        sch, queue = self._build(interval_s=0.03)
        sch.start()
        time.sleep(0.18)  # ~6 ticks attendus, mais on accepte une marge
        sch.stop()

        # On accepte ≥ 3 ticks pour tolérer la latence du scheduler de l'OS
        assert sch.enqueued_count >= 3, sch.enqueued_count
        assert queue.enqueued_count == sch.enqueued_count

    def test_graceful_stop_joins_thread(self) -> None:
        sch, _ = self._build(interval_s=0.5)  # interval long
        sch.start()
        time.sleep(0.05)
        before_stop = time.monotonic()
        sch.stop(timeout_s=2.0)
        elapsed = time.monotonic() - before_stop
        # Doit s'arrêter rapidement grâce au poll_resolution_s court
        assert elapsed < 0.5, f"stop took {elapsed:.2f}s — should be fast"
        assert not sch.is_running()

    def test_context_manager(self) -> None:
        with self._build(interval_s=0.05)[0] as sch:
            assert sch.is_running()
            time.sleep(0.1)
        assert not sch.is_running()

    def test_enqueue_failure_does_not_kill_loop(self) -> None:
        """If enqueue raises once, the scheduler must keep going."""
        queue = MagicMock(spec=TaskQueue)
        calls = {"n": 0}

        def fail_then_ok(task: TaskCreate):
            calls["n"] += 1
            if calls["n"] == 1:
                raise RuntimeError("simulated enqueue failure")
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            return TaskRead(
                id=task.id, task_type=task.task_type, status="pending",
                assigned_to=task.assigned_to, payload=task.payload, result=None,
                error=None, created_at=now, updated_at=now,
            )

        queue.enqueue.side_effect = fail_then_ok

        sch = HeartbeatScheduler(queue, interval_s=0.03, poll_resolution_s=0.01)
        deadline = time.monotonic() + 1.0
        try:
            sch.start()
            while calls["n"] < 2 and time.monotonic() < deadline:
                time.sleep(0.01)
        finally:
            sch.stop()
        # on s'attend à plusieurs tentatives malgré le premier échec
        assert calls["n"] >= 2

    def test_only_one_thread_alive(self) -> None:
        """Sanity : pas de threading explosion sur start/stop répétés."""
        sch, _ = self._build(interval_s=0.05)
        for _ in range(5):
            sch.start()
            time.sleep(0.03)
            sch.stop()
        # Compter les threads "heartbeat-scheduler" actifs
        alive = [t for t in threading.enumerate() if t.name == "heartbeat-scheduler" and t.is_alive()]
        assert len(alive) == 0
