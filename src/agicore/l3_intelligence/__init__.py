"""AGIcore-v2 — L3 Intelligence layer.

Phase 8B : SignalLoopOrchestrator — passive event-driven coordinator.
Phase 8D : optional pre-submit risk gate via RiskManager + snapshot_provider.
"""
from .signal_loop_orchestrator import (
    EVT_SIGNAL_BLOCKED,
    EVT_SIGNAL_GENERATED,
    ORCHESTRATOR_ID,
    SignalLoopOrchestrator,
    SnapshotProvider,
)

__all__ = [
    "SignalLoopOrchestrator",
    "SnapshotProvider",
    "ORCHESTRATOR_ID",
    "EVT_SIGNAL_GENERATED",
    "EVT_SIGNAL_BLOCKED",
]
