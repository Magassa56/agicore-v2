"""DryRunRecorder and ExecutionRecorder — Phase 8H / 9A.

DryRunRecorder stores all tick events in-order and produces a
deterministic SHA-256 fingerprint of the entire event stream.

ExecutionRecorder tracks order execution statistics separately.

Invariants:
- No random() — all data is deterministic.
- Thread-safe: all shared state behind threading.RLock.
- Fingerprint is idempotent: repeated calls without new events return
  the same value.
"""
from __future__ import annotations

import hashlib
import threading
from dataclasses import dataclass


@dataclass
class TickEvent:
    """A single synthetic market tick event.

    Attributes
    ----------
    sequence:
        Monotonically increasing event counter (1-based).
    session_id:
        Copied from DryRunConfig for determinism.
    symbol:
        The symbol this tick belongs to.
    tick_data:
        Deterministic hex string derived from session_id + symbol + sequence.
    """

    sequence: int
    session_id: str
    symbol: str
    tick_data: str


class DryRunRecorder:
    """Thread-safe, append-only event recorder for dry-run sessions.

    All events are stored in insertion order. The fingerprint is the
    SHA-256 hex digest of all tick_data values concatenated in order.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._events: list[TickEvent] = []
        self._cached_fp: str | None = None
        self._fp_up_to: int = -1  # index fingerprint was computed at

    # ---------------------------------------------------------------- write

    def record(self, event: TickEvent) -> None:
        """Append *event* to the log. Invalidates the cached fingerprint."""
        with self._lock:
            self._events.append(event)
            self._cached_fp = None  # invalidate

    # ---------------------------------------------------------------- read

    def count(self) -> int:
        """Return the number of recorded events."""
        with self._lock:
            return len(self._events)

    def get_all(self) -> list[TickEvent]:
        """Return a snapshot copy of all events in insertion order."""
        with self._lock:
            return list(self._events)

    def compute_fingerprint(self) -> str:
        """Return the SHA-256 fingerprint of the entire event stream.

        Idempotent: repeated calls without new events return the same value.
        Returns a 64-character hex string.
        """
        with self._lock:
            if self._cached_fp is None:
                self._cached_fp = self._compute()
            return self._cached_fp

    # ---------------------------------------------------------------- internals

    def _compute(self) -> str:
        """SHA-256 over all tick_data values, joined by newline."""
        h = hashlib.sha256()
        for ev in self._events:
            h.update(ev.tick_data.encode())
            h.update(b"\n")
        return h.hexdigest()


@dataclass
class _OrderRecord:
    """Internal record for one submitted order."""
    symbol: str
    quantity: float
    side: str
    status: str  # "FILL" | "REJECT" | "PARTIAL" | "CANCEL"
    latency_ms: float


class ExecutionRecorder:
    """Thread-safe statistics tracker for order execution.

    Tracks totals, fills, rejects, partials, cancels, and average latency.
    The ``summary()`` method returns a plain dict consumed by tests and the
    health checker.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._records: list[_OrderRecord] = []

    def record_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        *,
        status: str = "FILL",
        latency_ms: float = 0.0,
    ) -> None:
        """Append one order result. Called by DryRunModeController."""
        rec = _OrderRecord(
            symbol=symbol,
            quantity=quantity,
            side=side,
            status=status,
            latency_ms=latency_ms,
        )
        with self._lock:
            self._records.append(rec)

    def summary(self) -> dict:
        """Return execution statistics as a plain dict.

        Keys: total, fills, rejects, partials, cancels, avg_latency_ms.
        """
        with self._lock:
            total = len(self._records)
            fills = sum(1 for r in self._records if r.status == "FILL")
            rejects = sum(1 for r in self._records if r.status == "REJECT")
            partials = sum(1 for r in self._records if r.status == "PARTIAL")
            cancels = sum(1 for r in self._records if r.status == "CANCEL")
            if total > 0:
                avg_lat = sum(r.latency_ms for r in self._records) / total
            else:
                avg_lat = 0.0
        return {
            "total": total,
            "fills": fills,
            "rejects": rejects,
            "partials": partials,
            "cancels": cancels,
            "avg_latency_ms": avg_lat,
        }


__all__ = ["DryRunRecorder", "ExecutionRecorder", "TickEvent"]
