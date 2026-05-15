"""Tests for EventBus."""
from __future__ import annotations

from agicore.core.events import (
    EVT_TASK_COMPLETED,
    EVT_TASK_CREATED,
    WILDCARD,
    Event,
    EventBus,
)


def test_event_immutable_with_payload_returns_new() -> None:
    e1 = Event(event_type="t.x", payload={"a": 1})
    e2 = e1.with_payload(b=2)
    assert e1.payload == {"a": 1}
    assert e2.payload == {"a": 1, "b": 2}
    assert e1.event_id != e2.event_id


def test_event_bus_publish_calls_subscribers() -> None:
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(EVT_TASK_CREATED, received.append)

    invoked = bus.emit(EVT_TASK_CREATED, task_id="t-1")

    assert invoked == 1
    assert len(received) == 1
    assert received[0].event_type == EVT_TASK_CREATED
    assert received[0].payload == {"task_id": "t-1"}


def test_event_bus_wildcard_subscriber() -> None:
    bus = EventBus()
    seen: list[str] = []
    bus.subscribe(WILDCARD, lambda ev: seen.append(ev.event_type))

    bus.emit(EVT_TASK_CREATED, task_id="t-1")
    bus.emit(EVT_TASK_COMPLETED, task_id="t-1")

    assert seen == [EVT_TASK_CREATED, EVT_TASK_COMPLETED]


def test_event_bus_unsubscribe() -> None:
    bus = EventBus()
    received: list[Event] = []
    unsub = bus.subscribe(EVT_TASK_CREATED, received.append)

    bus.emit(EVT_TASK_CREATED, task_id="t-1")
    unsub()
    bus.emit(EVT_TASK_CREATED, task_id="t-2")

    assert len(received) == 1


def test_event_bus_handler_failure_is_isolated() -> None:
    bus = EventBus()
    received: list[Event] = []

    def boom(ev: Event) -> None:
        raise RuntimeError("handler bug")

    bus.subscribe(EVT_TASK_CREATED, boom)
    bus.subscribe(EVT_TASK_CREATED, received.append)

    invoked = bus.emit(EVT_TASK_CREATED, task_id="t-1")

    assert invoked == 1  # le handler en échec n'est pas compté
    assert len(received) == 1  # l'autre handler a quand même reçu


def test_event_bus_clear_removes_all() -> None:
    bus = EventBus()
    seen: list[Event] = []
    bus.subscribe(EVT_TASK_CREATED, seen.append)
    bus.clear()
    bus.emit(EVT_TASK_CREATED, task_id="t-1")
    assert seen == []
