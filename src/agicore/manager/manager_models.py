"""ManagerConfig and ManagerState — Phase 9B.

Immutable configuration contract and state enum for AGIcoreManager.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ManagerState(str, Enum):
    """Lifecycle states for AGIcoreManager."""

    RUNNING = "RUNNING"
    """Manager is active and processing."""

    PAUSED = "PAUSED"
    """Manager is suspended but recoverable."""

    STOPPED = "STOPPED"
    """Manager has shut down (terminal state)."""


@dataclass
class ManagerConfig:
    """Configuration contract for AGIcoreManager.

    All fields with defaults may be omitted; only *manager_id* is required.

    Parameters
    ----------
    manager_id : str
        Unique identifier for this manager instance.
    runtime_mode : str
        Broker runtime mode (SANDBOX / PAPER / DRY_RUN / REPLAY /
        LIVE_DISABLED). Default: "SANDBOX".
    adapter_name : str
        Registered broker adapter. Default: "alpaca_paper".
    symbols : tuple[str, ...]
        Trading symbols to track. Default: ("AAPL",).
    enable_dry_run : bool
        Attach a DryRunModeController to the manager. Default: False.
    enable_snapshots : bool
        Persist SnapshotRecords to *snapshot_dir*. Default: False.
    enable_metrics : bool
        Enable metrics collection. Default: False.
    enable_health : bool
        Enable health reporting. Default: False.
    snapshot_interval : int
        Ticks between automatic snapshots. Default: 100.
    metrics_interval : int
        Ticks between metrics sampling. Default: 50.
    """

    manager_id: str
    runtime_mode: str = "SANDBOX"
    adapter_name: str = "alpaca_paper"
    symbols: tuple = field(default_factory=lambda: ("AAPL",))
    enable_dry_run: bool = False
    enable_snapshots: bool = False
    enable_metrics: bool = False
    enable_health: bool = False
    snapshot_interval: int = 100
    metrics_interval: int = 50


__all__ = ["ManagerConfig", "ManagerState"]
