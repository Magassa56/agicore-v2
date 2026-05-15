"""Unit tests for EventStore."""
from __future__ import annotations

import threading
from datetime import datetime, timezone

import pytest

from agicore.replay.event_store import (
    EventStore,
    ReplayEvent,
    ReplayEventType,
)


def test_append_and_count() -> None:
    s = EventStore()
    assert s.count() == 0
    s.append(ReplayEventType.ORDER_CREATED, {"order_id": "o-1", "symbol": "ES",
                                              "side": "BUY", "quantity": 1.0})
    assert s.count() == 1
    assert len(s) == 1


def test_append_returns_immutable_event() -> None:
    s = EventStore()
    ev = s.append(
        ReplayEventType.ORDER_FILLED,
        {"order_id": "o-1", "symbol": "ES", "side": "BUY",
         "quantity": 1.0, "fill_price": 100.0},
    )
    assert isinstance(ev, ReplayEvent)
    assert ev.sequence == 0
    with pytest.raises(Exception):
        ev.sequence = 99  # type: ignore[misc]


def test_sequence_is_monotonic() -> None:
    s = EventStore()
    seqs = []
    for i in range(5):
        ev = s.append(ReplayEventType.ORDER_CREATED, {"order_id": f"o-{i}",
                                                       "symbol": "ES",
                                                       "side": "BUY",
                                                       "quantity": 1.0})
        seqs.append(ev.sequence)
    assert seqs == [0, 1, 2, 3, 4]


def test_get_all_returns_defensive_copy() -> None:
    s = EventStore()
    s.append(ReplayEventType.ORDER_CREATED, {"order_id": "o-1", "symbol": "ES",
                                              "side": "BUY", "quantity": 1.0})
    snapshot = s.get_all()
    snapshot.clear()  # mutating the returned list must not affect the store
    assert s.count() == 1


def test_get_until_filters_by_timestamp() -> None:
    s = EventStore()
    t1 = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 1, 1, 10, 1, tzinfo=timezone.utc)
    t3 = datetime(2026, 1, 1, 10, 2, tzinfo=timezone.utc)
    s.append(ReplayEventType.ORDER_CREATED, {"order_id": "a", "symbol": "ES",
                                              "side": "BUY", "quantity": 1.0},
             timestamp=t1)
    s.append(ReplayEventType.ORDER_CREATED, {"order_id": "b", "symbol": "ES",
                                              "side": "BUY", "quantity": 1.0},
             timestamp=t2)
    s.append(ReplayEventType.ORDER_CREATED, {"order_id": "c", "symbol": "ES",
                                              "side": "BUY", "quantity": 1.0},
             timestamp=t3)
    until_t2 = s.get_until(t2)
    assert [e.payload["order_id"] for e in until_t2] == ["a", "b"]


def test_get_in_range_open_bounds() -> None:
    s = EventStore()
    t1 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    s.append(ReplayEventType.ORDER_CREATED, {"order_id": "o", "symbol": "ES",
                                              "side": "BUY", "quantity": 1.0},
             timestamp=t1)
    assert len(s.get_in_range()) == 1
    assert len(s.get_in_range(start=t1)) == 1
    assert len(s.get_in_range(end=t1)) == 1


def test_get_by_type_filters() -> None:
    s = EventStore()
    s.append(ReplayEventType.ORDER_CREATED, {"order_id": "a", "symbol": "ES",
                                              "side": "BUY", "quantity": 1.0})
    s.append(ReplayEventType.ORDER_FILLED, {"order_id": "a", "symbol": "ES",
                                             "side": "BUY", "quantity": 1.0,
                                             "fill_price": 100.0})
    fills = s.get_by_type(ReplayEventType.ORDER_FILLED)
    assert len(fills) == 1
    assert fills[0].event_type == ReplayEventType.ORDER_FILLED


def test_clear_resets_sequence() -> None:
    s = EventStore()
    s.append(ReplayEventType.ORDER_CREATED, {"order_id": "x", "symbol": "ES",
                                              "side": "BUY", "quantity": 1.0})
    s.clear()
    assert s.count() == 0
    ev = s.append(ReplayEventType.ORDER_CREATED, {"order_id": "y", "symbol": "ES",
                                                   "side": "BUY", "quantity": 1.0})
    assert ev.sequence == 0


def test_iteration_uses_snapshot() -> None:
    s = EventStore()
    for i in range(3):
        s.append(ReplayEventType.ORDER_CREATED, {"order_id": f"o-{i}",
                                                  "symbol": "ES",
                                                  "side": "BUY",
                                                  "quantity": 1.0})
    seen = [e.payload["order_id"] for e in s]
    assert seen == ["o-0", "o-1", "o-2"]


def test_concurrent_appends_consistent() -> None:
    s = EventStore()
    N = 100

    def worker():
        s.append(ReplayEventType.ORDER_CREATED, {"order_id": "x",
                                                  "symbol": "ES",
                                                  "side": "BUY",
                                                  "quantity": 1.0})

    threads = [threading.Thread(target=worker) for _ in range(N)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert s.count() == N
    seqs = [e.sequence for e in s.get_all()]
    assert sorted(seqs) == list(range(N))


def test_append_accepts_string_event_type() -> None:
    """Convenience : strings are coerced to the enum."""
    s = EventStore()
    ev = s.append("OrderCreated", {"order_id": "o", "symbol": "ES",
                                    "side": "BUY", "quantity": 1.0})
    assert ev.event_type == ReplayEventType.ORDER_CREATED


def test_payload_is_defensively_copied() -> None:
    s = EventStore()
    payload = {"order_id": "o", "symbol": "ES", "side": "BUY", "quantity": 1.0}
    ev = s.append(ReplayEventType.ORDER_CREATED, payload)
    payload["mutated"] = True
    assert "mutated" not in ev.payload
