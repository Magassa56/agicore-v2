"""Models for the offline Autonomous Cognitive Stability Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from .behavioral_stability_models import BehavioralStabilityResult
from .cognitive_adaptation_models import CognitiveAdaptationResult
from .cognitive_governance_models import CognitiveGovernanceResult
from .cognitive_policy_models import CognitivePolicyResult
from .collective_consensus_models import ConsensusResult
from .global_orchestrator_models import GlobalOrchestratorResult
from .intent_alignment_models import IntentAlignmentResult
from .mission_continuity_models import MissionContinuityResult
from .operational_awareness_models import OperationalAwarenessResult
from .recursive_world_model_models import RecursiveWorldModelResult
from .recovery_resilience_models import RecoveryResilienceResult
from .self_reflection_audit_models import SelfReflectionAuditResult
from .strategic_arbitration_models import ArbitrationResult
from .system_integrity_models import SystemIntegrityResult


class CognitiveStabilityState(StrEnum):
    """Current cognitive stability state."""

    STABLE = "STABLE"
    WATCH = "WATCH"
    DEGRADED = "DEGRADED"
    UNSTABLE = "UNSTABLE"
    CRITICAL = "CRITICAL"
    COLLAPSING = "COLLAPSING"
    RECOVERY_STABILIZING = "RECOVERY_STABILIZING"


class CognitiveStabilityMode(StrEnum):
    """Operating mode for cognitive stability supervision."""

    NORMAL_STABILITY = "NORMAL_STABILITY"
    MONITORING_MODE = "MONITORING_MODE"
    STABILIZATION_MODE = "STABILIZATION_MODE"
    SAFE_STABILITY_MODE = "SAFE_STABILITY_MODE"
    RECOVERY_STABILITY_MODE = "RECOVERY_STABILITY_MODE"
    EMERGENCY_STABILIZATION = "EMERGENCY_STABILIZATION"
    LOCKED_STABILITY = "LOCKED_STABILITY"


class CognitiveStabilityRisk(StrEnum):
    """Risks that degrade cognitive stability."""

    COGNITIVE_DRIFT = "COGNITIVE_DRIFT"
    RECURSIVE_INSTABILITY = "RECURSIVE_INSTABILITY"
    DECISION_OSCILLATION = "DECISION_OSCILLATION"
    POLICY_FRAGMENTATION = "POLICY_FRAGMENTATION"
    CONSENSUS_CONFLICT = "CONSENSUS_CONFLICT"
    ORCHESTRATOR_OVERLOAD = "ORCHESTRATOR_OVERLOAD"
    WORLD_MODEL_INCOHERENCE = "WORLD_MODEL_INCOHERENCE"
    BEHAVIORAL_INSTABILITY = "BEHAVIORAL_INSTABILITY"
    RUNAWAY_RECURSION = "RUNAWAY_RECURSION"
    SYSTEM_COLLAPSE_RISK = "SYSTEM_COLLAPSE_RISK"


class CognitiveStabilitySignal(StrEnum):
    """Signals emitted by the stability engine."""

    STABILITY_CONFIRMED = "STABILITY_CONFIRMED"
    EARLY_DRIFT_WARNING = "EARLY_DRIFT_WARNING"
    OSCILLATION_DETECTED = "OSCILLATION_DETECTED"
    POLICY_CONFLICT_DETECTED = "POLICY_CONFLICT_DETECTED"
    CONSENSUS_UNSTABLE = "CONSENSUS_UNSTABLE"
    WORLD_MODEL_UNSTABLE = "WORLD_MODEL_UNSTABLE"
    ORCHESTRATION_STRESS = "ORCHESTRATION_STRESS"
    RECURSIVE_LOOP_WARNING = "RECURSIVE_LOOP_WARNING"
    COLLAPSE_WARNING = "COLLAPSE_WARNING"
    RECOVERY_STABILIZATION_DETECTED = "RECOVERY_STABILIZATION_DETECTED"


class CognitiveStabilityRecommendation(StrEnum):
    """Recommended stability controls."""

    CONTINUE_MONITORING = "CONTINUE_MONITORING"
    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    FREEZE_RECURSIVE_UPDATES = "FREEZE_RECURSIVE_UPDATES"
    STABILIZE_POLICY_SET = "STABILIZE_POLICY_SET"
    REBUILD_CONSENSUS = "REBUILD_CONSENSUS"
    PROTECT_WORLD_MODEL = "PROTECT_WORLD_MODEL"
    ENTER_SAFE_STABILITY_MODE = "ENTER_SAFE_STABILITY_MODE"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    INITIATE_RECOVERY_STABILIZATION = "INITIATE_RECOVERY_STABILIZATION"
    LOCK_SYSTEM_STABILITY = "LOCK_SYSTEM_STABILITY"


class StabilityTrend(StrEnum):
    """Trend observed across the stability window."""

    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    WATCH = "WATCH"
    DEGRADING = "DEGRADING"
    OSCILLATING = "OSCILLATING"
    COLLAPSING = "COLLAPSING"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class StabilityWindow:
    """Temporal stability window built from current and historical snapshots."""

    snapshots_count: int
    decision_sequence: tuple[str, ...]
    score_sequence: tuple[int, ...]
    risk_sequence: tuple[tuple[str, ...], ...]
    oscillation_count: int
    average_score: int
    latest_score: int


@dataclass(frozen=True)
class CognitiveStabilityScore:
    """Stability component scores normalized to 0..100."""

    governance_stability_score: int
    policy_stability_score: int
    consensus_stability_score: int
    orchestration_stability_score: int
    world_model_stability_score: int
    behavioral_stability_score: int
    recursive_safety_score: int


@dataclass(frozen=True)
class CognitiveStabilityInput:
    """Inputs consumed by the offline cognitive stability engine."""

    cognitive_policy: CognitivePolicyResult | None = None
    cognitive_governance: CognitiveGovernanceResult | None = None
    self_reflection_audit: SelfReflectionAuditResult | None = None
    recursive_world_model: RecursiveWorldModelResult | None = None
    global_orchestrator: GlobalOrchestratorResult | None = None
    collective_consensus: ConsensusResult | None = None
    strategic_arbitration: ArbitrationResult | None = None
    intent_alignment: IntentAlignmentResult | None = None
    operational_awareness: OperationalAwarenessResult | None = None
    behavioral_stability: BehavioralStabilityResult | None = None
    cognitive_adaptation: CognitiveAdaptationResult | None = None
    system_integrity: SystemIntegrityResult | None = None
    mission_continuity: MissionContinuityResult | None = None
    recovery_resilience: RecoveryResilienceResult | None = None
    historical_snapshots: tuple[Any, ...] = ()


@dataclass(frozen=True)
class CognitiveStabilityEvent:
    """Auditable cognitive stability event."""

    state: CognitiveStabilityState
    mode: CognitiveStabilityMode
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class CognitiveStabilityResult:
    """Final autonomous cognitive stability result."""

    state: CognitiveStabilityState
    mode: CognitiveStabilityMode
    stability_score: int
    score_breakdown: CognitiveStabilityScore
    trend: StabilityTrend
    stability_window: StabilityWindow
    signals: tuple[CognitiveStabilitySignal, ...]
    risks: tuple[CognitiveStabilityRisk, ...]
    recommendations: tuple[CognitiveStabilityRecommendation, ...]
    events: tuple[CognitiveStabilityEvent, ...]
    summary: str


__all__ = [
    "CognitiveStabilityEvent",
    "CognitiveStabilityInput",
    "CognitiveStabilityMode",
    "CognitiveStabilityRecommendation",
    "CognitiveStabilityResult",
    "CognitiveStabilityRisk",
    "CognitiveStabilityScore",
    "CognitiveStabilitySignal",
    "CognitiveStabilityState",
    "StabilityTrend",
    "StabilityWindow",
]
