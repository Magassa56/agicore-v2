"""Models for the offline Autonomous Operational Awareness Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .behavioral_stability_models import BehavioralStabilityResult
from .cognitive_adaptation_models import CognitiveAdaptationResult
from .executive_brain_models import ExecutiveBrainResult
from .hierarchical_supervisor_models import SupervisorResult
from .mission_continuity_models import MissionContinuityResult
from .multi_agent_models import AgentCoordinationResult
from .recursive_self_evaluation_models import SelfEvaluationResult
from .recovery_resilience_models import RecoveryResilienceResult
from .strategic_memory_models import StrategicTimelineAnalysis
from .system_integrity_models import SystemIntegrityResult


class OperationalAwarenessMode(StrEnum):
    """Operational awareness mode for the offline trading stack."""

    OPTIMAL = "OPTIMAL"
    STABLE = "STABLE"
    DEGRADED = "DEGRADED"
    HIGH_LOAD = "HIGH_LOAD"
    FRAGMENTED = "FRAGMENTED"
    UNSTABLE = "UNSTABLE"
    CRITICAL = "CRITICAL"
    RECOVERY_OBSERVATION = "RECOVERY_OBSERVATION"


class OperationalHealthStatus(StrEnum):
    """Operational health bucket."""

    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    COLLAPSING = "COLLAPSING"


class OperationalRisk(StrEnum):
    """Operational risks detected by awareness monitoring."""

    SILENT_DEGRADATION = "SILENT_DEGRADATION"
    AGENT_COORDINATION_DRIFT = "AGENT_COORDINATION_DRIFT"
    EXECUTIVE_INSTABILITY = "EXECUTIVE_INSTABILITY"
    MEMORY_FRAGMENTATION = "MEMORY_FRAGMENTATION"
    COGNITIVE_SATURATION = "COGNITIVE_SATURATION"
    STRATEGIC_INCONSISTENCY = "STRATEGIC_INCONSISTENCY"
    RECOVERY_STAGNATION = "RECOVERY_STAGNATION"
    AUTONOMY_DRIFT = "AUTONOMY_DRIFT"
    DECISION_LATENCY = "DECISION_LATENCY"
    SYSTEM_FATIGUE = "SYSTEM_FATIGUE"


class OperationalSignal(StrEnum):
    """Signals emitted by operational awareness."""

    SYSTEM_HEALTH_STRONG = "SYSTEM_HEALTH_STRONG"
    SYSTEM_HEALTH_WEAK = "SYSTEM_HEALTH_WEAK"
    LOAD_NORMAL = "LOAD_NORMAL"
    LOAD_ELEVATED = "LOAD_ELEVATED"
    LOAD_CRITICAL = "LOAD_CRITICAL"
    COORDINATION_ALIGNED = "COORDINATION_ALIGNED"
    COORDINATION_DRIFTING = "COORDINATION_DRIFTING"
    EXECUTIVE_STABLE = "EXECUTIVE_STABLE"
    EXECUTIVE_UNSTABLE = "EXECUTIVE_UNSTABLE"
    MEMORY_STABLE = "MEMORY_STABLE"
    MEMORY_FRAGMENTED = "MEMORY_FRAGMENTED"
    RECOVERY_PROGRESSING = "RECOVERY_PROGRESSING"
    RECOVERY_STALLED = "RECOVERY_STALLED"
    AUTONOMY_STABLE = "AUTONOMY_STABLE"
    AUTONOMY_DRIFTING = "AUTONOMY_DRIFTING"


class OperationalRecommendation(StrEnum):
    """Recommended operational adjustments."""

    REDUCE_COMPLEXITY = "REDUCE_COMPLEXITY"
    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    STABILIZE_COORDINATION = "STABILIZE_COORDINATION"
    FREEZE_LEARNING = "FREEZE_LEARNING"
    PRIORITIZE_CRITICAL_SYSTEMS = "PRIORITIZE_CRITICAL_SYSTEMS"
    INITIATE_RECOVERY = "INITIATE_RECOVERY"
    REQUIRE_SUPERVISION = "REQUIRE_SUPERVISION"
    CONTINUE_MONITORING = "CONTINUE_MONITORING"
    REBUILD_STABILITY = "REBUILD_STABILITY"
    MAINTAIN_OPERATION = "MAINTAIN_OPERATION"


@dataclass(frozen=True)
class OperationalMetric:
    """One named operational metric normalized to 0..100 unless noted."""

    name: str
    value: float
    status: OperationalHealthStatus
    note: str


@dataclass(frozen=True)
class OperationalConfidenceScore:
    """Operational confidence component scores normalized to 0..100."""

    system_health_score: int
    continuity_score: int
    recovery_score: int
    coordination_score: int
    executive_score: int
    memory_score: int
    cognitive_load_score: int
    behavioral_stability_score: int
    autonomy_score: int


@dataclass(frozen=True)
class OperationalAwarenessInput:
    """Inputs consumed by the offline operational awareness engine."""

    mission_continuity: MissionContinuityResult | None = None
    recovery_resilience: RecoveryResilienceResult | None = None
    system_integrity: SystemIntegrityResult | None = None
    executive_result: ExecutiveBrainResult | None = None
    agent_coordination: AgentCoordinationResult | None = None
    supervisor_result: SupervisorResult | None = None
    cognitive_adaptation: CognitiveAdaptationResult | None = None
    behavioral_stability: BehavioralStabilityResult | None = None
    self_evaluation: SelfEvaluationResult | None = None
    strategic_timeline_analysis: StrategicTimelineAnalysis | None = None


@dataclass(frozen=True)
class OperationalEvent:
    """Auditable operational awareness event."""

    mode: OperationalAwarenessMode
    health_status: OperationalHealthStatus
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class OperationalAwarenessResult:
    """Final operational awareness output."""

    mode: OperationalAwarenessMode
    health_status: OperationalHealthStatus
    operational_confidence_score: int
    confidence_breakdown: OperationalConfidenceScore
    signals: tuple[OperationalSignal, ...]
    risks: tuple[OperationalRisk, ...]
    metrics: tuple[OperationalMetric, ...]
    recommendations: tuple[OperationalRecommendation, ...]
    system_load_score: int
    coordination_quality_score: int
    monitoring_state: str
    events: tuple[OperationalEvent, ...]
    summary: str


__all__ = [
    "OperationalAwarenessInput",
    "OperationalAwarenessMode",
    "OperationalAwarenessResult",
    "OperationalConfidenceScore",
    "OperationalEvent",
    "OperationalHealthStatus",
    "OperationalMetric",
    "OperationalRecommendation",
    "OperationalRisk",
    "OperationalSignal",
]
