"""In-process event bus for AGIcore-v2 runtime.

Lightweight pub/sub. Synchronous by default — future versions can swap the
implementation for an async or remote bus while keeping the same interface.

Events are propagated to the LTM event log in parallel via the
`MemoryService` if a sink is registered.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import structlog

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
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def with_payload(self, **kwargs: Any) -> "Event":
        merged = dict(self.payload)
        merged.update(kwargs)
        return Event(event_type=self.event_type, payload=merged)


Handler = Callable[[Event], None]


class EventBus:
    """Synchronous in-process event bus.

    Methods are thread-safe enough for the simple synchronous use case but
    are NOT designed for high-concurrency async usage in Phase 3.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Handler]] = defaultdict(list)

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
                logger.error(
                    "event_bus.handler_failed",
                    event_type=event.event_type,
                    event_id=event.event_id,
                    error=str(exc),
                    exc_info=True,
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
    "Event",
    "EventBus",
    "Handler",
    "WILDCARD",
    "EVT_TASK_CREATED",
    "EVT_TASK_DISPATCHED",
    "EVT_TASK_STARTED",
    "EVT_TASK_COMPLETED",
    "EVT_TASK_FAILED",
    "EVT_TASK_RETRIED",
    "EVT_TASK_CANCELLED",
]
