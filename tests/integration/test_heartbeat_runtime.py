"""Integration test — HeartbeatAgent + HeartbeatScheduler through the full
Runtime Engine pipeline.

Validates the success criteria of Phase 5 :
- Runtime can stay alive
- Process periodic work
- Emit lifecycle events
- Persist heartbeat state
- Shutdown cleanly without architecture changes.
"""
from __future__ import annotations

import threading
import time

from agicore.agents.heartbeat_agent import (
    EVT_HEARTBEAT_TICK,
    RUNTIME_STATE_ACTIVE,
    RUNTIME_STATE_STOPPING,
    TASK_TYPE_HEARTBEAT,
    HeartbeatAgent,
    HeartbeatScheduler,
)
from agicore.core.events import (
    EVT_TASK_COMPLETED,
    EVT_TASK_CREATED,
    EVT_TASK_STARTED,
)
from agicore.core.retry import RetryPolicy
from agicore.l4_planning.runtime import RuntimeEngine


def _runtime_state(rt: RuntimeEngine) -> str:
    """Bridge the agent's state provider to the runtime shutdown handler."""
    return RUNTIME_STATE_STOPPING if rt.shutdown_handler.is_stopping() else RUNTIME_STATE_ACTIVE


def test_heartbeat_periodic_full_pipeline() -> None:
    """Multiple heartbeat tasks flow end-to-end and persist correctly."""
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.5,  # long — scheduler wakes via TaskQueue wakeup
    )
    try:
        agent = HeartbeatAgent(
            rt.memory, rt.event_bus,
            runtime_state_provider=lambda: _runtime_state(rt),
        )
        rt.register_handler(TASK_TYPE_HEARTBEAT, agent)

        # Capture all bus events
        seen: list[str] = []
        observed_two_heartbeats = threading.Event()

        def capture_event(ev) -> None:
            seen.append(ev.event_type)
            if (
                ev.event_type == EVT_HEARTBEAT_TICK
                and int(ev.payload.get("counter", 0)) >= 2
            ):
                observed_two_heartbeats.set()

        rt.subscribe("*", capture_event)

        # Producer thread = scheduler; consumer thread = runtime loop
        scheduler = HeartbeatScheduler(
            rt.queue, interval_s=0.04, poll_resolution_s=0.01
        )
        consumer = threading.Thread(
            target=lambda: rt.run_forever(max_iterations=200),
            name="runtime-consumer",
        )

        consumer.start()
        scheduler.start()
        try:
            assert observed_two_heartbeats.wait(timeout=5.0)
            enqueue_deadline = time.monotonic() + 1.0
            while scheduler.enqueued_count < 3 and time.monotonic() < enqueue_deadline:
                time.sleep(0.005)
            assert scheduler.enqueued_count >= 3, scheduler.enqueued_count
        finally:
            scheduler.stop()
            rt.stop()
            consumer.join(timeout=5.0)

        # Le consumer doit avoir terminé proprement
        assert not consumer.is_alive(), "runtime consumer did not exit"

        # Le scheduler a produit plusieurs ticks
        assert scheduler.enqueued_count >= 3, scheduler.enqueued_count

        # Au moins une tâche heartbeat est complétée
        assert agent.counter >= 2

        # Lifecycle events présents pour les heartbeats
        assert EVT_TASK_CREATED in seen
        assert EVT_TASK_STARTED in seen
        assert EVT_TASK_COMPLETED in seen
        assert EVT_HEARTBEAT_TICK in seen

        # LTM contient au moins N events agent.heartbeat.tick
        events = rt.memory.get_recent_events(
            event_type=EVT_HEARTBEAT_TICK, limit=50
        )
        assert len(events) == agent.counter
        # Les compteurs sur les events sont monotones (1..N)
        counters_seen = sorted(int(e.payload["counter"]) for e in events)
        assert counters_seen == list(range(1, agent.counter + 1))
    finally:
        rt.shutdown()


def test_heartbeat_graceful_shutdown_drains_in_flight() -> None:
    """When shutdown is triggered, the runtime+scheduler exit cleanly without
    leaving threads alive."""
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.05,
    )
    try:
        rt.register_handler(
            TASK_TYPE_HEARTBEAT,
            HeartbeatAgent(
                rt.memory, rt.event_bus,
                runtime_state_provider=lambda: _runtime_state(rt),
            ),
        )

        scheduler = HeartbeatScheduler(rt.queue, interval_s=0.03, poll_resolution_s=0.01)
        consumer = threading.Thread(
            target=lambda: rt.run_forever(max_iterations=100),
            name="runtime-consumer",
        )

        consumer.start()
        scheduler.start()
        time.sleep(0.1)

        # Trigger shutdown
        scheduler.stop()
        rt.stop()
        consumer.join(timeout=5.0)

        assert not consumer.is_alive()
        assert not scheduler.is_running()

        # Aucun thread heartbeat-scheduler ni runtime résiduel
        residual = [
            t for t in threading.enumerate()
            if t.name in ("heartbeat-scheduler", "runtime-consumer") and t.is_alive()
        ]
        assert residual == []
    finally:
        rt.shutdown()


def test_heartbeat_counter_persists_across_ticks() -> None:
    """Le compteur agent + les events LTM forment une chaîne monotone."""
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    try:
        agent = HeartbeatAgent(rt.memory, rt.event_bus)
        rt.register_handler(TASK_TYPE_HEARTBEAT, agent)

        scheduler = HeartbeatScheduler(rt.queue, interval_s=0.02, poll_resolution_s=0.01)
        scheduler.start()
        time.sleep(0.15)
        scheduler.stop()

        # Drain : exécuter tout ce qui est en attente
        for _ in range(30):
            n = rt.run_once()
            if n == 0:
                break

        events = rt.memory.get_recent_events(
            event_type=EVT_HEARTBEAT_TICK, limit=100
        )
        assert len(events) == agent.counter
        # Counters monotones
        counters = [int(e.payload["counter"]) for e in events]
        # Les events sont triés desc par created_at par get_recent_events,
        # donc on s'attend à voir counter décroissant
        assert counters == sorted(counters, reverse=True)
    finally:
        rt.shutdown()
