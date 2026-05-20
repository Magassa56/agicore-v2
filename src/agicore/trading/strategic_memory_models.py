"""Models for the offline Strategic Memory Timeline."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class StrategicCyclePhase(StrEnum):
    """Strategic multi-session cycle phase."""

    GROWTH = "GROWTH"
    RECOVERY = "RECOVERY"
    DEFENSIVE = "DEFENSIVE"
    SURVIVAL = "SURVIVAL"
    PAUSED = "PAUSED"
    LEARNING = "LEARNING"
    POLICY_VALIDATION = "POLICY_VALIDATION"
    UNKNOWN = "UNKNOWN"


class StrategicDriftSignal(StrEnum):
    """Signals detected when strategic memory degrades or improves."""

    STRATEGIC_IMPROVEMENT = "STRATEGIC_IMPROVEMENT"
    STRATEGIC_DEGRADATION = "STRATEGIC_DEGRADATION"
    BEHAVIORAL_DRIFT = "BEHAVIORAL_DRIFT"
    VIOLATIONS_INCREASE = "VIOLATIONS_INCREASE"
    REWARD_DECLINE = "REWARD_DECLINE"
    STABILITY_DECLINE = "STABILITY_DECLINE"
    PERSISTENT_DRAWDOWN = "PERSISTENT_DRAWDOWN"
    DANGEROUS_POLICY = "DANGEROUS_POLICY"
    CAPITAL_RECOVERY = "CAPITAL_RECOVERY"
    CONSISTENCY_GAIN = "CONSISTENCY_GAIN"


@dataclass(frozen=True)
class StrategicMemorySnapshot:
    """One offline strategic memory snapshot for a session or step."""

    timestamp: datetime
    session_id: str
    capital_estimate: float
    drawdown_estimate: float
    executive_mode: str
    strategic_objective: str
    risk_appetite: str
    selected_policy: str | None
    average_reward: float
    consistency_score: float
    safety_violations: int
    blocked_trades: int
    executed_trades: int
    market_regime_summary: str
    behavior_summary: str
    notes: str = ""


@dataclass(frozen=True)
class StrategicTimelineEvent:
    """Auditable event emitted while updating or analyzing the timeline."""

    event_type: str
    message: str
    timestamp: datetime
    session_id: str | None = None


@dataclass(frozen=True)
class StrategicTimeline:
    """Offline-only strategic memory timeline."""

    snapshots: tuple[StrategicMemorySnapshot, ...]
    events: tuple[StrategicTimelineEvent, ...] = ()
    name: str = "agicore_strategic_memory_timeline"
    version: str = "1.0"


@dataclass(frozen=True)
class StrategicTimelineAnalysis:
    """Strategic timeline analysis and health metrics."""

    snapshots_count: int
    cycle_phases: tuple[StrategicCyclePhase, ...]
    drift_signals: tuple[StrategicDriftSignal, ...]
    best_period: StrategicMemorySnapshot | None
    worst_period: StrategicMemorySnapshot | None
    stability_score: int
    strategic_health_score: int
    improvement_detected: bool
    degradation_detected: bool
    recommendations: tuple[str, ...]
    summary: str


__all__ = [
    "StrategicCyclePhase",
    "StrategicDriftSignal",
    "StrategicMemorySnapshot",
    "StrategicTimeline",
    "StrategicTimelineAnalysis",
    "StrategicTimelineEvent",
]
