"""In-process event bus for AGIcore-v2 runtime.

Lightweight pub/sub. Synchronous by default — future versions can swap the
implementation for an async or remote bus while keeping the same interface.

Events are propagated to the LTM event log in parallel via the
`MemoryService` if a sink is registered.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Protocol
from uuid import uuid4

import structlog

if TYPE_CHECKING:
    from agicore.core.event_delivery_contracts import EmissionApplyResult


class CanonicalEventDelivery(Protocol):
    """Narrow durable authority consumed by the canonical bus path."""

    def accept_emission(
        self,
        *,
        source_identity: str,
        consumer_id: str,
        outcome_id: str,
        outcome_hash: str,
        receipt_hash: str,
        source_sequence: int,
        event_type: str,
        occurred_at: datetime,
        accepted_at: datetime,
        payload: Mapping[str, object],
    ) -> EmissionApplyResult: ...

logger = structlog.get_logger(__name__)


# Lifecycle event types — canonical names propagated through the system
EVT_TASK_CREATED = "task.created"
EVT_TASK_DISPATCHED = "task.dispatched"
EVT_TASK_STARTED = "task.started"
EVT_TASK_COMPLETED = "task.completed"
EVT_TASK_FAILED = "task.failed"
EVT_TASK_RETRIED = "task.retried"
EVT_TASK_CANCELLED = "task.cancelled"

# Wildcard subscription
WILDCARD = "*"


@dataclass(frozen=True)
class Event:
    """Immutable event record."""

    event_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def with_payload(self, **kwargs: Any) -> Event:
        merged = dict(self.payload)
        merged.update(kwargs)
        return Event(event_type=self.event_type, payload=merged)


Handler = Callable[[Event], None]


class EventBus:
    """Synchronous in-process event bus.

    Methods are thread-safe enough for the simple synchronous use case but
    are NOT designed for high-concurrency async usage in Phase 3.
    """

    def __init__(
        self,
        *,
        canonical_delivery: CanonicalEventDelivery | None = None,
        acceptance_clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._subscribers: dict[str, list[Handler]] = defaultdict(list)
        self._canonical_delivery = canonical_delivery
        self._acceptance_clock = acceptance_clock or (lambda: datetime.now(UTC))

    @property
    def canonical_delivery_enabled(self) -> bool:
        """Whether the durable canonical publishing path was injected."""
        return self._canonical_delivery is not None

    def accept_idempotent(
        self,
        *,
        source_identity: str,
        event_type: str,
        occurred_at: datetime,
        payload: Mapping[str, object],
    ) -> EmissionApplyResult:
        """Durably accept one emission before legacy best-effort propagation.

        Handler identities are intentionally absent from this API. The durable
        authority resolves its registered manifest. Gate linkage values live in
        the canonical payload and are validated again by that authority.
        """
        if self._canonical_delivery is None:
            raise RuntimeError("canonical EventBus delivery authority is not configured")
        if not isinstance(payload, Mapping):
            raise TypeError("canonical EventBus payload must be a mapping")
        required = (
            "consumer_id",
            "outcome_id",
            "outcome_hash",
            "receipt_hash",
            "source_sequence",
        )
        missing = tuple(name for name in required if name not in payload)
        if missing:
            raise ValueError(f"canonical EventBus payload is missing linkage fields: {missing}")
        result = self._canonical_delivery.accept_emission(
            source_identity=source_identity,
            consumer_id=payload["consumer_id"],
            outcome_id=payload["outcome_id"],
            outcome_hash=payload["outcome_hash"],
            receipt_hash=payload["receipt_hash"],
            source_sequence=payload["source_sequence"],
            event_type=event_type,
            occurred_at=occurred_at,
            accepted_at=self._acceptance_clock(),
            payload=payload,
        )
        from agicore.core.event_delivery_contracts import ApplyStatus

        if result.status == ApplyStatus.APPLIED_NEW:
            self.publish(
                Event(
                    event_type=event_type,
                    payload=dict(payload),
                    event_id=result.emission.emission_effect_id,
                    timestamp=occurred_at,
                )
            )
        return result

    def subscribe(self, event_type: str, handler: Handler) -> Callable[[], None]:
        """Register a handler. Returns an unsubscribe function."""
        self._subscribers[event_type].append(handler)
        logger.debug("event_bus.subscribed", event_type=event_type)

        def _unsubscribe() -> None:
            try:
                self._subscribers[event_type].remove(handler)
                logger.debug("event_bus.unsubscribed", event_type=event_type)
            except ValueError:
                pass

        return _unsubscribe

    def publish(self, event: Event) -> int:
        """Publish an event to all subscribers. Returns number of handlers invoked.

        A handler that raises is logged but does NOT abort the propagation.
        """
        direct = list(self._subscribers.get(event.event_type, []))
        wildcard = list(self._subscribers.get(WILDCARD, []))
        invoked = 0
        for handler in direct + wildcard:
            try:
                handler(event)
                invoked += 1
            except Exception as exc:
                logger.exception(
                    "event_bus.handler_failed",
                    event_type=event.event_type,
                    event_id=event.event_id,
                    error=str(exc),
                )
        logger.debug(
            "event_bus.published",
            event_type=event.event_type,
            event_id=event.event_id,
            handlers=invoked,
        )
        return invoked

    def emit(self, event_type: str, **payload: Any) -> int:
        """Convenience: build an Event from kwargs and publish."""
        return self.publish(Event(event_type=event_type, payload=payload))

    def clear(self) -> None:
        """Remove all subscriptions. For tests."""
        self._subscribers.clear()


__all__ = [
    "EVT_TASK_CANCELLED",
    "EVT_TASK_COMPLETED",
    "EVT_TASK_CREATED",
    "EVT_TASK_DISPATCHED",
    "EVT_TASK_FAILED",
    "EVT_TASK_RETRIED",
    "EVT_TASK_STARTED",
    "WILDCARD",
    "CanonicalEventDelivery",
    "Event",
    "EventBus",
    "Handler",
]
