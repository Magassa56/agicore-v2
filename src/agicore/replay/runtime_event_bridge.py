"""RuntimeEventBridge — passive bridge from Runtime EventBus to Replay EventStore.

Phase 7F : a one-way pipe that captures lifecycle events flowing on the
in-process EventBus (Phase 3) and appends them as immutable ReplayEvents
to the EventStore (Phase 7E). The bridge is :

- **passive**     : observes only, never injects events back into the bus.
- **append-only** : never mutates existing replay records.
- **deterministic ordering** : leverages the EventBus's synchronous
                                propagation + the EventStore's monotonic
                                sequence assignment. No background threads.
- **agent-agnostic**          : the only knowledge it has of agents is via
                                pluggable translators. Default translators
                                cover the canonical ExecutionAgent event ;
                                custom ones can be registered before
                                attaching.
- **structlog only**          : zero ``print()``.

The bridge intentionally does NOT modify or extend any agent. If a runtime
event payload lacks fields needed for full state reconstruction (e.g. the
ExecutionAgent emits an order_status without a quantity on the bus), the
default translator records what it can ; the replay state will reflect
exactly what was visible on the bus at runtime.
"""
from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any

import structlog

from agicore.core.events import Event, EventBus

from .event_store import EventStore, ReplayEventType

logger = structlog.get_logger(__name__)


# ============================================================================
# Translator type alias (no new architectural abstraction)
# ============================================================================
RuntimeToReplayTranslator = Callable[
    [Event], list[tuple[ReplayEventType, dict[str, Any]]]
]


# Canonical runtime event types we know how to translate
RUNTIME_EXECUTION_EVENT: str = "agent.execution.order.processed"


# ============================================================================
# Default translators
# ============================================================================
def _default_execution_translator(
    event: Event,
) -> list[tuple[ReplayEventType, dict[str, Any]]]:
    """Translate ExecutionAgent's bus emit into ReplayEvents.

    Always emits ``OrderCreated`` for an executed task. Then, depending on
    the order status :
        - FILLED               → also emits ``OrderFilled``
        - REJECTED / CANCELLED → also emits ``OrderCancelled``
        - PENDING (limit rest) → only ``OrderCreated``
    """
    p = event.payload
    order_id = p.get("order_id")
    symbol = p.get("symbol")
    side = p.get("side")
    if not order_id or not symbol or not side:
        return []

    order_status = str(p.get("order_status", "")).upper()
    committed = p.get("committed") is True
    if order_status == "REJECTED" and not committed:
        required_audit = (
            "intent_id",
            "authorization_id",
            "decision_hash",
            "provider_id",
            "context_state_version",
            "context_state_hash",
            "risk_limits_hash",
        )
        if any(not p.get(name) and p.get(name) != 0 for name in required_audit):
            return []
        return [(
            ReplayEventType.RISK_VIOLATION,
            {
                "intent_id": p["intent_id"],
                "authorization_id": p["authorization_id"],
                "decision_hash": p["decision_hash"],
                "provider_id": p["provider_id"],
                "context_state_version": p["context_state_version"],
                "context_state_hash": p["context_state_hash"],
                "risk_limits_hash": p["risk_limits_hash"],
                "violation_codes": list(p.get("violation_codes") or ()),
                "order_id": order_id,
                "symbol": symbol,
                "side": side,
            },
        )]
    if not committed:
        return []
    quantity = p.get("quantity")
    if quantity is None:
        # Best-effort fallback if the bus emit doesn't carry it
        quantity = p.get("filled_quantity", 0.0)

    base_payload: dict[str, Any] = {
        "order_id": order_id,
        "symbol": symbol,
        "side": side,
        "quantity": float(quantity),
    }

    out: list[tuple[ReplayEventType, dict[str, Any]]] = [
        (ReplayEventType.ORDER_CREATED, dict(base_payload)),
    ]

    if order_status == "FILLED":
        fill_payload = dict(base_payload)
        fill_payload["fill_price"] = p.get("fill_price")
        if p.get("filled_quantity") is not None:
            fill_payload["fill_quantity"] = float(p["filled_quantity"])
        out.append((ReplayEventType.ORDER_FILLED, fill_payload))
    elif order_status == "CANCELLED":
        out.append((
            ReplayEventType.ORDER_CANCELLED,
            {
                "order_id": order_id,
                "reason": p.get("broker_message", order_status.lower()),
            },
        ))
    # PENDING → only OrderCreated, the eventual fill will arrive later
    return out


DEFAULT_TRANSLATORS: dict[str, RuntimeToReplayTranslator] = {
    RUNTIME_EXECUTION_EVENT: _default_execution_translator,
}


# ============================================================================
# Bridge
# ============================================================================
class RuntimeEventBridge:
    """Subscribes to the Runtime EventBus and appends to the Replay EventStore.

    Parameters
    ----------
    event_bus : EventBus
        Required. The Runtime EventBus (Phase 3).
    event_store : EventStore
        Required. The Replay EventStore (Phase 7E). Append-only.
    translators : dict[str, RuntimeToReplayTranslator] | None
        Optional. Maps runtime event types to translation functions. The
        default mapping covers ``agent.execution.order.processed`` ; pass
        a fresh dict to override entirely, or use ``register_translator``
        to add/override individual entries before ``attach()``.
    """

    def __init__(
        self,
        event_bus: EventBus,
        event_store: EventStore,
        *,
        translators: dict[str, RuntimeToReplayTranslator] | None = None,
    ) -> None:
        self._bus = event_bus
        self._store = event_store
        self._translators: dict[str, RuntimeToReplayTranslator] = (
            dict(translators) if translators is not None
            else dict(DEFAULT_TRANSLATORS)
        )
        self._unsub: list[Callable[[], None]] = []
        self._lock = threading.RLock()
        self._captured_count = 0
        self._is_attached = False

    # ------------------------------------------------------------------ Inspection
    @property
    def store(self) -> EventStore:
        return self._store

    @property
    def bus(self) -> EventBus:
        return self._bus

    @property
    def captured_count(self) -> int:
        with self._lock:
            return self._captured_count

    @property
    def is_attached(self) -> bool:
        return self._is_attached

    @property
    def known_event_types(self) -> list[str]:
        return list(self._translators.keys())

    # ------------------------------------------------------------------ Configuration
    def register_translator(
        self,
        runtime_event_type: str,
        translator: RuntimeToReplayTranslator,
    ) -> None:
        """Register or override a translator. Must be called BEFORE attach()."""
        if self._is_attached:
            raise RuntimeError(
                "cannot register translator while the bridge is attached"
            )
        self._translators[runtime_event_type] = translator
        logger.info(
            "runtime_event_bridge.translator_registered",
            runtime_event_type=runtime_event_type,
        )

    # ------------------------------------------------------------------ Lifecycle
    def attach(self) -> None:
        """Subscribe to all configured runtime event types. Idempotent."""
        if self._is_attached:
            return
        for runtime_type in self._translators:
            unsub = self._bus.subscribe(runtime_type, self._on_event)
            self._unsub.append(unsub)
        self._is_attached = True
        logger.info(
            "runtime_event_bridge.attached",
            event_types=list(self._translators.keys()),
        )

    def detach(self) -> None:
        """Unsubscribe from all runtime event types. Idempotent."""
        if not self._is_attached:
            return
        for unsub in self._unsub:
            try:
                unsub()
            except Exception as exc:  # pragma: no cover
                logger.warning(
                    "runtime_event_bridge.unsubscribe_failed", error=str(exc)
                )
        self._unsub.clear()
        self._is_attached = False
        logger.info("runtime_event_bridge.detached")

    def __enter__(self) -> "RuntimeEventBridge":
        self.attach()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.detach()

    # ------------------------------------------------------------------ Event sink
    def _on_event(self, event: Event) -> None:
        """Bus subscriber. Translates and appends to the store."""
        translator = self._translators.get(event.event_type)
        if translator is None:  # pragma: no cover — defensive
            return
        try:
            replay_records = translator(event)
        except Exception as exc:
            logger.error(
                "runtime_event_bridge.translator_failed",
                runtime_event_type=event.event_type,
                error=str(exc),
                exc_info=True,
            )
            return

        for replay_type, payload in replay_records:
            self._store.append(replay_type, payload, timestamp=event.timestamp)

        with self._lock:
            self._captured_count += len(replay_records)

        logger.debug(
            "runtime_event_bridge.captured",
            runtime_event_type=event.event_type,
            replay_records=len(replay_records),
        )


__all__ = [
    "RuntimeEventBridge",
    "RuntimeToReplayTranslator",
    "RUNTIME_EXECUTION_EVENT",
    "DEFAULT_TRANSLATORS",
]
