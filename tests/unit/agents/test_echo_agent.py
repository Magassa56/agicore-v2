"""Unit tests for EchoAgent."""
from __future__ import annotations

from agicore.agents.echo_agent import (
    AGENT_ID,
    EVT_ECHO_PROCESSED,
    TASK_TYPE_ECHO,
    EchoAgent,
)
from agicore.core.events import EventBus
from agicore.l2_memory.services.memory_service import MemoryService


def test_returns_structured_feedback(memory: MemoryService, make_task) -> None:
    agent = EchoAgent(memory)
    task = make_task(task_id="t-1", payload={"hello": "world", "n": 42})

    feedback = agent(task)

    assert feedback["echoed"] == {"hello": "world", "n": 42}
    assert feedback["task_id"] == "t-1"
    assert feedback["agent_id"] == AGENT_ID
    assert feedback["processed_count"] == 1
    assert "started_at" in feedback
    assert "finished_at" in feedback
    assert isinstance(feedback["latency_ms"], float)
    assert feedback["latency_ms"] >= 0
    assert len(feedback["payload_hash"]) == 16


def test_persists_event_in_memory(memory: MemoryService, make_task) -> None:
    agent = EchoAgent(memory)
    agent(make_task(task_id="t-7", payload={"x": 1}))

    events = memory.get_recent_events(event_type=EVT_ECHO_PROCESSED, limit=10)
    assert len(events) == 1
    ev = events[0]
    assert ev.task_id == "t-7"
    assert ev.agent_id == AGENT_ID
    assert ev.payload["input_keys"] == ["x"]
    assert "input_hash" in ev.payload


def test_emits_bus_event_when_bus_provided(
    memory: MemoryService, event_bus: EventBus, make_task
) -> None:
    seen: list[str] = []
    event_bus.subscribe(EVT_ECHO_PROCESSED, lambda ev: seen.append(ev.payload["task_id"]))

    agent = EchoAgent(memory, event_bus)
    agent(make_task(task_id="t-bus", payload={}))

    assert seen == ["t-bus"]


def test_works_without_bus(memory: MemoryService, make_task) -> None:
    """Bus is optional — handler must function without it."""
    agent = EchoAgent(memory, event_bus=None)
    feedback = agent(make_task())
    assert feedback["task_id"] == "t-1"


def test_payload_hash_is_deterministic(memory: MemoryService, make_task) -> None:
    agent = EchoAgent(memory)
    h1 = agent(make_task(task_id="a", payload={"a": 1, "b": 2}))["payload_hash"]
    h2 = agent(make_task(task_id="b", payload={"b": 2, "a": 1}))["payload_hash"]
    assert h1 == h2  # même contenu, ordre des clés différent → même hash


def test_payload_hash_differs_for_different_inputs(
    memory: MemoryService, make_task
) -> None:
    agent = EchoAgent(memory)
    h1 = agent(make_task(task_id="a", payload={"a": 1}))["payload_hash"]
    h2 = agent(make_task(task_id="b", payload={"a": 2}))["payload_hash"]
    assert h1 != h2


def test_processed_count_increments(memory: MemoryService, make_task) -> None:
    agent = EchoAgent(memory)
    assert agent.processed_count == 0
    agent(make_task(task_id="t-1"))
    agent(make_task(task_id="t-2"))
    agent(make_task(task_id="t-3"))
    assert agent.processed_count == 3


def test_empty_payload_supported(memory: MemoryService, make_task) -> None:
    agent = EchoAgent(memory)
    feedback = agent(make_task(task_id="t-empty", payload={}))
    assert feedback["echoed"] == {}
    assert feedback["payload_hash"]  # non-vide même pour {}


def test_canonical_constants_exported() -> None:
    """Garantir la stabilité des identifiants publics."""
    assert TASK_TYPE_ECHO == "agent.echo"
    assert EVT_ECHO_PROCESSED == "agent.echo.processed"
    assert AGENT_ID == "echo_agent"
