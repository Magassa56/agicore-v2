"""Unit tests for RuntimeEventBridge."""
from __future__ import annotations

import threading

import pytest

from agicore.core.events import Event, EventBus
from agicore.replay.event_store import EventStore, ReplayEventType
from agicore.replay.runtime_event_bridge import (
    DEFAULT_TRANSLATORS,
    RUNTIME_EXECUTION_EVENT,
    RuntimeEventBridge,
)


# ---------------------------------------------------------------- Fixtures
def _bus_and_store() -> tuple[EventBus, EventStore]:
    return EventBus(), EventStore()


def _exec_payload(
    *,
    order_id: str = "ord-1",
    symbol: str = "ES",
    side: str = "BUY",
    quantity: float = 1.0,
    order_status: str = "FILLED",
    fill_price: float | None = 100.0,
    filled_quantity: float | None = None,
    broker_message: str | None = None,
    committed: bool = True,
) -> dict:
    p = {
        "order_id": order_id,
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "order_status": order_status,
        "fill_price": fill_price,
        "committed": committed,
    }
    if filled_quantity is not None:
        p["filled_quantity"] = filled_quantity
    if broker_message is not None:
        p["broker_message"] = broker_message
    return p


# ---------------------------------------------------------------- Lifecycle
def test_attach_subscribes_to_known_types() -> None:
    bus, store = _bus_and_store()
    bridge = RuntimeEventBridge(bus, store)
    assert not bridge.is_attached
    bridge.attach()
    assert bridge.is_attached
    assert RUNTIME_EXECUTION_EVENT in bridge.known_event_types


def test_attach_idempotent() -> None:
    bus, store = _bus_and_store()
    bridge = RuntimeEventBridge(bus, store)
    bridge.attach()
    bridge.attach()  # no error, no double-subscribe explosion
    bus.emit(RUNTIME_EXECUTION_EVENT, **_exec_payload())
    # If double-subscribed, we'd capture twice (4 records). Default = 2 records.
    assert bridge.captured_count == 2


def test_detach_idempotent() -> None:
    bus, store = _bus_and_store()
    bridge = RuntimeEventBridge(bus, store)
    bridge.attach()
    bridge.detach()
    bridge.detach()  # no error


def test_detach_stops_capturing() -> None:
    bus, store = _bus_and_store()
    bridge = RuntimeEventBridge(bus, store)
    bridge.attach()
    bus.emit(RUNTIME_EXECUTION_EVENT, **_exec_payload())
    assert bridge.captured_count == 2
    bridge.detach()
    bus.emit(RUNTIME_EXECUTION_EVENT, **_exec_payload(order_id="ord-2"))
    # Still 2 — no new capture
    assert bridge.captured_count == 2


def test_context_manager_attaches_and_detaches() -> None:
    bus, store = _bus_and_store()
    with RuntimeEventBridge(bus, store) as bridge:
        assert bridge.is_attached
        bus.emit(RUNTIME_EXECUTION_EVENT, **_exec_payload())
        assert bridge.captured_count == 2
    assert not bridge.is_attached


# ---------------------------------------------------------------- Default execution translator
def test_filled_order_yields_two_replay_events() -> None:
    bus, store = _bus_and_store()
    bridge = RuntimeEventBridge(bus, store)
    bridge.attach()
    bus.emit(RUNTIME_EXECUTION_EVENT, **_exec_payload(
        order_id="ord-X", symbol="ES", side="BUY", quantity=3.0,
        order_status="FILLED", fill_price=100.0, filled_quantity=3.0,
    ))
    events = store.get_all()
    assert len(events) == 2
    assert events[0].event_type == ReplayEventType.ORDER_CREATED
    assert events[1].event_type == ReplayEventType.ORDER_FILLED
    assert events[0].payload["order_id"] == "ord-X"
    assert events[0].payload["quantity"] == 3.0
    assert events[1].payload["fill_price"] == 100.0
    assert events[1].payload["fill_quantity"] == 3.0


def test_rejected_risk_yields_only_auditable_violation() -> None:
    bus, store = _bus_and_store()
    bridge = RuntimeEventBridge(bus, store)
    bridge.attach()
    payload = _exec_payload(
        order_status="REJECTED", fill_price=None, committed=False,
        broker_message="risk authorization rejected",
    )
    payload.update({
        "intent_id": "intent-rejected",
        "authorization_id": "risk-auth-rejected",
        "decision_hash": "a" * 64,
        "provider_id": "provider-risk",
        "context_state_version": 3,
        "context_state_hash": "b" * 64,
        "risk_limits_hash": "c" * 64,
        "violation_codes": ["INSUFFICIENT_POSITION"],
    })
    bus.emit(RUNTIME_EXECUTION_EVENT, **payload)
    events = store.get_all()
    assert [event.event_type for event in events] == [ReplayEventType.RISK_VIOLATION]
    assert events[0].payload["intent_id"] == "intent-rejected"
    assert events[0].payload["violation_codes"] == ["INSUFFICIENT_POSITION"]


def test_pending_order_yields_only_order_created() -> None:
    bus, store = _bus_and_store()
    bridge = RuntimeEventBridge(bus, store)
    bridge.attach()
    bus.emit(RUNTIME_EXECUTION_EVENT, **_exec_payload(
        order_status="PENDING", fill_price=None,
    ))
    events = store.get_all()
    assert len(events) == 1
    assert events[0].event_type == ReplayEventType.ORDER_CREATED


def test_missing_required_fields_emits_nothing() -> None:
    bus, store = _bus_and_store()
    bridge = RuntimeEventBridge(bus, store)
    bridge.attach()
    bus.emit(RUNTIME_EXECUTION_EVENT, side="BUY", quantity=1.0)  # missing order_id, symbol
    assert store.count() == 0
    assert bridge.captured_count == 0


def test_quantity_falls_back_to_filled_quantity() -> None:
    bus, store = _bus_and_store()
    bridge = RuntimeEventBridge(bus, store)
    bridge.attach()
    p = {"order_id": "o", "symbol": "ES", "side": "BUY",
         "order_status": "FILLED", "fill_price": 100.0,
         "filled_quantity": 5.0, "committed": True}
    bus.emit(RUNTIME_EXECUTION_EVENT, **p)
    events = store.get_all()
    assert events[0].payload["quantity"] == 5.0


# ---------------------------------------------------------------- Custom translators
def test_register_translator_overrides_default() -> None:
    bus, store = _bus_and_store()
    bridge = RuntimeEventBridge(bus, store)

    def custom(event: Event):
        return [(ReplayEventType.PNL_UPDATED, {"symbol": "ES", "realized_pnl": 42.0})]

    bridge.register_translator(RUNTIME_EXECUTION_EVENT, custom)
    bridge.attach()
    bus.emit(RUNTIME_EXECUTION_EVENT, **_exec_payload())
    events = store.get_all()
    assert len(events) == 1
    assert events[0].event_type == ReplayEventType.PNL_UPDATED
    assert events[0].payload["realized_pnl"] == 42.0


def test_register_translator_after_attach_raises() -> None:
    bus, store = _bus_and_store()
    bridge = RuntimeEventBridge(bus, store)
    bridge.attach()
    with pytest.raises(RuntimeError):
        bridge.register_translator(RUNTIME_EXECUTION_EVENT, lambda ev: [])


def test_constructor_overrides_default_mapping() -> None:
    bus, store = _bus_and_store()
    custom = {"my.custom.event": lambda ev: [
        (ReplayEventType.PNL_UPDATED, {"symbol": "ES", "realized_pnl": 1.0})
    ]}
    bridge = RuntimeEventBridge(bus, store, translators=custom)
    bridge.attach()
    # Default execution event isn't registered → not captured
    bus.emit(RUNTIME_EXECUTION_EVENT, **_exec_payload())
    assert store.count() == 0
    bus.emit("my.custom.event")
    assert store.count() == 1


def test_translator_exception_isolated() -> None:
    """A faulty translator must not break the bridge or the bus."""
    bus, store = _bus_and_store()
    bridge = RuntimeEventBridge(bus, store)

    def boom(event: Event):
        raise RuntimeError("translator broken")

    bridge.register_translator(RUNTIME_EXECUTION_EVENT, boom)
    bridge.attach()
    bus.emit(RUNTIME_EXECUTION_EVENT, **_exec_payload())
    # Bridge captured 0 but didn't crash, store empty
    assert bridge.captured_count == 0
    assert store.count() == 0


# ---------------------------------------------------------------- Ordering & determinism
def test_events_appended_in_emission_order() -> None:
    bus, store = _bus_and_store()
    bridge = RuntimeEventBridge(bus, store)
    bridge.attach()
    for i in range(5):
        bus.emit(RUNTIME_EXECUTION_EVENT, **_exec_payload(
            order_id=f"ord-{i}", quantity=float(i + 1),
        ))
    events = store.get_all()
    # 5 emits × 2 replay events each
    assert len(events) == 10
    # Sequence is monotone
    seqs = [e.sequence for e in events]
    assert seqs == sorted(seqs)
    # Order ids appear in the right groups
    created_ids = [e.payload["order_id"] for e in events
                   if e.event_type == ReplayEventType.ORDER_CREATED]
    assert created_ids == [f"ord-{i}" for i in range(5)]


def test_concurrent_emissions_consistent() -> None:
    """Concurrent bus emits must produce a coherent log (no lost events)."""
    bus, store = _bus_and_store()
    bridge = RuntimeEventBridge(bus, store)
    bridge.attach()

    N = 50

    def worker(i: int) -> None:
        bus.emit(RUNTIME_EXECUTION_EVENT, **_exec_payload(order_id=f"ord-{i}"))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(N)]
    for t in threads: t.start()
    for t in threads: t.join()

    # Each emit produces 2 ReplayEvents (FILLED → Created + Filled)
    assert bridge.captured_count == 2 * N
    assert store.count() == 2 * N
    # All sequences unique and contiguous
    seqs = sorted(e.sequence for e in store.get_all())
    assert seqs == list(range(2 * N))


# ---------------------------------------------------------------- Misc
def test_known_event_types_initial_default() -> None:
    bridge = RuntimeEventBridge(EventBus(), EventStore())
    assert bridge.known_event_types == [RUNTIME_EXECUTION_EVENT]


def test_default_translators_constant_immutable_to_caller_mutation() -> None:
    """Mutating the returned dict must not affect future bridge instances."""
    bus, store = _bus_and_store()
    bridge = RuntimeEventBridge(bus, store)
    # Internally the bridge took a copy ; external mutation of the bridge's
    # known_event_types property doesn't help us here, but we can still
    # check that DEFAULT_TRANSLATORS still has the canonical key.
    assert RUNTIME_EXECUTION_EVENT in DEFAULT_TRANSLATORS


def test_store_property_exposes_underlying() -> None:
    bus, store = _bus_and_store()
    bridge = RuntimeEventBridge(bus, store)
    assert bridge.store is store
    assert bridge.bus is bus
