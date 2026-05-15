"""EventStore — immutable append-only log of replay events.

Phase 7E core invariant : events are the ONLY source of truth. State is
always recomputed from this log. The store offers no mutation API beyond
``append`` and ``clear`` (the latter is reserved for tests/resets).

Sequence numbers are assigned by the store at append time and provide a
canonical total ordering even when timestamps tie.
"""
from __future__ import annotations

import threading
from collections.abc import Iterator
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

import structlog
from pydantic import BaseModel, ConfigDict, Field

logger = structlog.get_logger(__name__)


# ============================================================================
# Event types
# ============================================================================
class ReplayEventType(str, Enum):
    """Canonical event types supported by the replay subsystem."""
    ORDER_CREATED = "OrderCreated"
    ORDER_FILLED = "OrderFilled"
    ORDER_CANCELLED = "OrderCancelled"
    POSITION_OPENED = "PositionOpened"
    POSITION_CLOSED = "PositionClosed"
    PNL_UPDATED = "PnLUpdated"
    MARKET_TICK = "MarketTick"
    RISK_VIOLATION = "RiskViolation"


# ============================================================================
# Immutable event record
# ============================================================================
class ReplayEvent(BaseModel):
    """One immutable event in the replay log.

    Frozen Pydantic — instances cannot be mutated after creation.
    """
    model_config = ConfigDict(frozen=True)

    event_id: str = Field(..., min_length=1, max_length=64)
    event_type: ReplayEventType
    timestamp: datetime
    sequence: int = Field(..., ge=0)
    payload: dict[str, Any]


# ============================================================================
# EventStore
# ============================================================================
class EventStore:
    """Thread-safe append-only event log.

    The store only exposes ``append`` for mutation. ``clear`` is provided
    for tests and explicit resets ; production code should never call it.
    All read accessors return defensive copies so external code cannot
    accidentally mutate internal state.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._events: list[ReplayEvent] = []
        self._next_sequence: int = 0

    # ------------------------------------------------------------------ Mutation
    def append(
        self,
        event_type: ReplayEventType,
        payload: dict[str, Any],
        *,
        timestamp: datetime | None = None,
        event_id: str | None = None,
    ) -> ReplayEvent:
        """Append a new event. Returns the immutable ``ReplayEvent`` record."""
        if not isinstance(event_type, ReplayEventType):
            event_type = ReplayEventType(event_type)
        ts = timestamp if timestamp is not None else datetime.now(timezone.utc)
        eid = event_id or str(uuid4())
        with self._lock:
            seq = self._next_sequence
            self._next_sequence += 1
            event = ReplayEvent(
                event_id=eid,
                event_type=event_type,
                timestamp=ts,
                sequence=seq,
                payload=dict(payload),  # defensive copy
            )
            self._events.append(event)
        logger.debug(
            "event_store.appended",
            event_id=event.event_id,
            event_type=event.event_type.value,
            sequence=event.sequence,
        )
        return event

    def clear(self) -> None:
        """Reset the log. Reserved for tests / explicit resets only."""
        with self._lock:
            self._events.clear()
            self._next_sequence = 0
        logger.warning("event_store.cleared")

    # ------------------------------------------------------------------ Read
    def get_all(self) -> list[ReplayEvent]:
        """Return a defensive copy of all events ordered by sequence."""
        with self._lock:
            return list(self._events)

    def get_until(self, timestamp: datetime) -> list[ReplayEvent]:
        """Return events whose timestamp is <= the given cutoff."""
        with self._lock:
            return [e for e in self._events if e.timestamp <= timestamp]

    def get_in_range(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[ReplayEvent]:
        """Return events whose timestamp is in [start, end]. None = open bound."""
        with self._lock:
            return [
                e for e in self._events
                if (start is None or e.timestamp >= start)
                and (end is None or e.timestamp <= end)
            ]

    def get_by_type(self, event_type: ReplayEventType) -> list[ReplayEvent]:
        with self._lock:
            return [e for e in self._events if e.event_type == event_type]

    def count(self) -> int:
        with self._lock:
            return len(self._events)

    def __len__(self) -> int:
        return self.count()

    def __iter__(self) -> Iterator[ReplayEvent]:
        # Iterate over a snapshot so the lock isn't held during iteration
        return iter(self.get_all())


__all__ = ["EventStore", "ReplayEvent", "ReplayEventType"]
