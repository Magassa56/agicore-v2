"""Integration test — EchoAgent through the full Runtime Engine pipeline.

receive → enqueue → dispatch → execute → log → persist → feedback
"""
from __future__ import annotations

from agicore.agents.echo_agent import (
    AGENT_ID,
    EVT_ECHO_PROCESSED,
    TASK_TYPE_ECHO,
    EchoAgent,
)
from agicore.core.events import (
    EVT_TASK_COMPLETED,
    EVT_TASK_CREATED,
    EVT_TASK_STARTED,
)
from agicore.core.retry import RetryPolicy
from agicore.l2_memory.repositories.task_repository import TaskRepository
from agicore.l2_memory.schemas.task import TaskCreate
from agicore.l4_planning.runtime import RuntimeEngine


def test_echo_agent_runs_end_to_end() -> None:
    """Single happy-path run through Runtime Engine v1."""
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    try:
        # Wire the EchoAgent
        agent = EchoAgent(rt.memory, rt.event_bus)
        rt.register_handler(TASK_TYPE_ECHO, agent)

        # Capture all events flowing on the bus
        seen: list[str] = []
        rt.subscribe("*", lambda ev: seen.append(ev.event_type))

        # Submit a task
        submitted = rt.submit(
            TaskCreate(
                id="t-echo-1",
                task_type=TASK_TYPE_ECHO,
                payload={"msg": "hello", "n": 42},
            )
        )
        assert submitted.status == "pending"

        # Drain the loop — should pick up our task and run it
        executed = rt.run_once()
        assert executed == 1

        # 1. Feedback persisted on the task
        with rt.orchestrator._engine.session() as s:  # type: ignore[attr-defined]
            repo = TaskRepository(s)
            final = repo.get("t-echo-1")
        assert final is not None
        assert final.status == "completed"
        assert final.error is None
        assert final.result is not None
        assert final.result["echoed"] == {"msg": "hello", "n": 42}
        assert final.result["agent_id"] == AGENT_ID
        assert final.result["task_id"] == "t-echo-1"
        assert "payload_hash" in final.result
        assert final.result["processed_count"] == 1

        # 2. Lifecycle events propagated to the bus
        assert EVT_TASK_CREATED in seen
        assert EVT_TASK_STARTED in seen
        assert EVT_TASK_COMPLETED in seen
        assert EVT_ECHO_PROCESSED in seen  # domain event from EchoAgent

        # 3. Memory persistence — both lifecycle and domain events recorded
        events = rt.memory.get_recent_events(limit=20)
        types = [e.event_type for e in events]
        assert EVT_TASK_CREATED in types
        assert EVT_TASK_STARTED in types
        assert EVT_TASK_COMPLETED in types
        assert EVT_ECHO_PROCESSED in types

        # 4. Domain event carries the right metadata
        echo_events = rt.memory.get_recent_events(event_type=EVT_ECHO_PROCESSED)
        assert len(echo_events) == 1
        echo_ev = echo_events[0]
        assert echo_ev.task_id == "t-echo-1"
        assert echo_ev.agent_id == AGENT_ID
        assert echo_ev.payload["input_keys"] == ["msg", "n"]

        # 5. Agent's own counter
        assert agent.processed_count == 1
    finally:
        rt.shutdown()
