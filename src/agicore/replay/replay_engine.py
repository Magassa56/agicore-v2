"""ReplayEngine — orchestrates EventStore + StateBuilder.

Reconstructs ``ReplayState`` from an immutable event log. Provides
helpers for time-bounded replay and deterministic-equivalence checks.
"""
from __future__ import annotations

from datetime import datetime

import structlog

from .event_store import EventStore
from .state_builder import ReplayState, StateBuilder

logger = structlog.get_logger(__name__)


class ReplayEngine:
    """Orchestrator. Holds a reference to a store and a stateless builder."""

    def __init__(
        self,
        store: EventStore,
        builder: StateBuilder | None = None,
    ) -> None:
        self._store = store
        self._builder = builder or StateBuilder()

    @property
    def store(self) -> EventStore:
        return self._store

    @property
    def builder(self) -> StateBuilder:
        return self._builder

    # ------------------------------------------------------------------ Replay
    def replay(self) -> ReplayState:
        """Reconstruct full state from all events in the store."""
        return self._builder.build(self._store.get_all())

    def replay_until(self, timestamp: datetime) -> ReplayState:
        """Reconstruct state at a specific point in time."""
        return self._builder.build(self._store.get_until(timestamp))

    def replay_in_range(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> ReplayState:
        """Reconstruct state across an explicit time window."""
        return self._builder.build(self._store.get_in_range(start, end))

    # ------------------------------------------------------------------ Determinism
    def is_deterministic(self, *, n_runs: int = 3) -> bool:
        """Validate that ``replay()`` returns the same state across N runs.

        Pydantic frozen models implement structural equality, so a direct
        ``==`` comparison is sufficient.
        """
        if n_runs < 2:
            raise ValueError("n_runs must be >= 2 to validate determinism")
        first = self.replay()
        for _ in range(n_runs - 1):
            other = self.replay()
            if other != first:
                logger.error("replay.determinism_violation")
                return False
        return True


__all__ = ["ReplayEngine"]
