"""DryRun data models — Phase 8H.

DryRunConfig is the immutable configuration contract for a session.
DryRunState is the state machine enum.
DryRunSessionSnapshot is the lightweight read-only view emitted by the
controller and consumed by the health checker and the UI layer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DryRunState(str, Enum):
    """DryRun session lifecycle states."""

    IDLE = "IDLE"
    """Constructed but not yet started."""

    RUNNING = "RUNNING"
    """Active: ticks flowing, orders accepted."""

    PAUSED = "PAUSED"
    """Suspended: no ticks, no orders; can be resumed."""

    STOPPED = "STOPPED"
    """Terminal: no further state transitions allowed."""


@dataclass(frozen=True)
class DryRunConfig:
    """Immutable configuration for a single dry-run session.

    Attributes
    ----------
    session_id:
        Unique identifier; used as a determinism seed.
    runtime_mode:
        One of SANDBOX / PAPER / DRY_RUN / REPLAY / LIVE_DISABLED.
    adapter_name:
        Registered broker adapter name (e.g. "alpaca_paper").
    symbols:
        Ordered tuple of trading symbols — order is part of the
        determinism contract.
    tick_interval_ms:
        Milliseconds between synthetic ticks. 0 = as-fast-as-possible.
    max_ticks:
        Optional hard cap on tick count; *None* means unlimited.
    record_all_events:
        If True the recorder captures every event (not just orders).
    validate_on_stop:
        If True the controller validates replay fingerprint on stop.
    """

    session_id: str
    runtime_mode: str = "SANDBOX"
    adapter_name: str = "alpaca_paper"
    symbols: tuple = ("AAPL",)
    tick_interval_ms: int = 0
    max_ticks: int | None = None
    record_all_events: bool = True
    validate_on_stop: bool = False


@dataclass(frozen=True)
class DryRunSessionSnapshot:
    """Point-in-time read-only view of a DryRun session.

    Produced by ``DryRunModeController.snapshot()`` and consumed by
    ``DryRunHealthChecker``.
    """

    session_id: str
    state: DryRunState
    ticks_processed: int
    orders_submitted: int
    fills: int
    rejects: int
    risk_blocks: int
    last_sequence: int
    config_fingerprint: str
    timestamp: str


__all__ = ["DryRunConfig", "DryRunSessionSnapshot", "DryRunState"]
