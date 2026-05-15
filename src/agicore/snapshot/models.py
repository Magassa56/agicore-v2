"""Snapshot data models — Phase 8E.

SnapshotRecord is a frozen dataclass representing a deterministic
point-in-time capture of the system state that can be serialised to
JSON and restored without ambiguity.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SnapshotRecord:
    """Immutable snapshot of a trading session at a specific sequence point.

    Attributes
    ----------
    sequence:
        Monotonically increasing tick/event counter at snapshot time.
    positions:
        Mapping symbol → quantity held.
    realized_pnl:
        Total realised P&L at snapshot time.
    realized_pnl_by_symbol:
        Per-symbol breakdown of realised P&L.
    open_orders:
        Mapping order_id → order metadata dict.
    timestamp:
        UTC ISO-8601 string for human reference only; not used in
        determinism checks.
    fingerprint:
        SHA-256 hex digest of the event stream at this sequence.
    events_processed:
        Total events ingested up to this snapshot.
    config_fingerprint:
        SHA-256 hex digest of the DryRunConfig that produced this session.
    """

    sequence: int
    positions: dict
    realized_pnl: float
    realized_pnl_by_symbol: dict
    open_orders: dict
    timestamp: str
    fingerprint: str
    events_processed: int
    config_fingerprint: str


__all__ = ["SnapshotRecord"]
