"""Models for the offline Autonomous Global Orchestrator Core."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .behavioral_stability_models import BehavioralStabilityResult
from .collective_consensus_models import ConsensusResult
from .executive_brain_models import ExecutiveBrainResult
from .hierarchical_supervisor_models import SupervisorResult
from .intent_alignment_models import IntentAlignmentResult
from .learning_governance_models import LearningGovernanceResult
from .meta_cognition_models import MetaCognitionResult
from .mission_continuity_models import MissionContinuityResult
from .operational_awareness_models import OperationalAwarenessResult
from .recovery_resilience_models import RecoveryResilienceResult
from .recursive_self_evaluation_models import SelfEvaluationResult
from .strategic_arbitration_models import ArbitrationResult
from .strategic_planning_models import StrategicPlanningResult
from .system_integrity_models import SystemIntegrityResult
from .tactical_execution_models import TacticalExecutionResult


class OrchestratorMode(StrEnum):
    """Global orchestration mode."""

    NORMAL_OPERATION = "NORMAL_OPERATION"
    COORDINATED_OPERATION = "COORDINATED_OPERATION"
    SAFE_GLOBAL_MODE = "SAFE_GLOBAL_MODE"
    RECOVERY_COORDINATION = "RECOVERY_COORDINATION"
    LEARNING_COORDINATION = "LEARNING_COORDINATION"
    SUPERVISED_GLOBAL_MODE = "SUPERVISED_GLOBAL_MODE"
    DEGRADED_OPERATION = "DEGRADED_OPERATION"
    EMERGENCY_ORCHESTRATION = "EMERGENCY_ORCHESTRATION"
    SURVIVAL_ORCHESTRATION = "SURVIVAL_ORCHESTRATION"


class OrchestratorPriority(StrEnum):
    """Global priority hierarchy."""

    SURVIVAL = "SURVIVAL"
    SYSTEM_INTEGRITY = "SYSTEM_INTEGRITY"
    SAFETY = "SAFETY"
    MISSION = "MISSION"
    CONTINUITY = "CONTINUITY"
    CONSENSUS = "CONSENSUS"
    SUPERVISION = "SUPERVISION"
    STRATEGY = "STRATEGY"
    PERFORMANCE = "PERFORMANCE"
    LEARNING = "LEARNING"


class OrchestratorDecision(StrEnum):
    """Decision emitted by the global orchestrator."""

    CONTINUE_COORDINATED_OPERATION = "CONTINUE_COORDINATED_OPERATION"
    ENTER_SAFE_GLOBAL_MODE = "ENTER_SAFE_GLOBAL_MODE"
    ENABLE_RECOVERY_COORDINATION = "ENABLE_RECOVERY_COORDINATION"
    ENABLE_LEARNING_COORDINATION = "ENABLE_LEARNING_COORDINATION"
    REQUIRE_HUMAN_SUPERVISION = "REQUIRE_HUMAN_SUPERVISION"
    FREEZE_LEARNING = "FREEZE_LEARNING"
    ISOLATE_UNSTABLE_MODULES = "ISOLATE_UNSTABLE_MODULES"
    ACTIVATE_SURVIVAL_MODE = "ACTIVATE_SURVIVAL_MODE"
    EMERGENCY_HALT_ROUTING = "EMERGENCY_HALT_ROUTING"


class OrchestratorSignal(StrEnum):
    """Signals emitted while coordinating engines."""

    ENGINES_ALIGNED = "ENGINES_ALIGNED"
    SAFE_MODE_SIGNAL = "SAFE_MODE_SIGNAL"
    RECOVERY_SIGNAL = "RECOVERY_SIGNAL"
    LEARNING_SIGNAL = "LEARNING_SIGNAL"
    SUPERVISION_SIGNAL = "SUPERVISION_SIGNAL"
    INTEGRITY_SIGNAL = "INTEGRITY_SIGNAL"
    CONSENSUS_SIGNAL = "CONSENSUS_SIGNAL"
    SURVIVAL_SIGNAL = "SURVIVAL_SIGNAL"
    DESYNCHRONIZATION_SIGNAL = "DESYNCHRONIZATION_SIGNAL"


class OrchestratorRisk(StrEnum):
    """Global orchestration risks."""

    GLOBAL_INSTABILITY = "GLOBAL_INSTABILITY"
    ORCHESTRATION_FRAGMENTATION = "ORCHESTRATION_FRAGMENTATION"
    UNSAFE_COORDINATION = "UNSAFE_COORDINATION"
    CROSS_LAYER_CONFLICT = "CROSS_LAYER_CONFLICT"
    CRITICAL_MODE_TRANSITION = "CRITICAL_MODE_TRANSITION"
    CONSENSUS_BREAKDOWN = "CONSENSUS_BREAKDOWN"
    EXECUTION_DESYNCHRONIZATION = "EXECUTION_DESYNCHRONIZATION"
    AUTONOMY_ESCALATION = "AUTONOMY_ESCALATION"
    GLOBAL_SAFE_MODE_REQUIRED = "GLOBAL_SAFE_MODE_REQUIRED"
    SURVIVAL_PRIORITY_TRIGGERED = "SURVIVAL_PRIORITY_TRIGGERED"


class OrchestratorRecommendation(StrEnum):
    """Recommended global orchestration controls."""

    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    ENTER_GLOBAL_SAFE_MODE = "ENTER_GLOBAL_SAFE_MODE"
    FREEZE_LEARNING = "FREEZE_LEARNING"
    ENABLE_RECOVERY_COORDINATION = "ENABLE_RECOVERY_COORDINATION"
    REQUIRE_HUMAN_SUPERVISION = "REQUIRE_HUMAN_SUPERVISION"
    REBALANCE_PRIORITIES = "REBALANCE_PRIORITIES"
    ISOLATE_UNSTABLE_MODULES = "ISOLATE_UNSTABLE_MODULES"
    ACTIVATE_SURVIVAL_MODE = "ACTIVATE_SURVIVAL_MODE"
    CONTINUE_COORDINATED_OPERATION = "CONTINUE_COORDINATED_OPERATION"
    HALT_HIGH_RISK_ROUTING = "HALT_HIGH_RISK_ROUTING"


@dataclass(frozen=True)
class SystemHealthSnapshot:
    """Snapshot of global health metrics normalized to 0..100."""

    integrity_score: int
    consensus_score: int
    alignment_score: int
    operational_score: int
    continuity_score: int
    recovery_score: int
    cognitive_score: int
    behavioral_score: int
    orchestration_confidence: int


@dataclass(frozen=True)
class GlobalSystemState:
    """Current global state inferred from all compatible engines."""

    mode: OrchestratorMode
    dominant_priority: OrchestratorPriority
    health_snapshot: SystemHealthSnapshot
    active_engines: tuple[str, ...]
    degraded_engines: tuple[str, ...]
    isolated_engines: tuple[str, ...]
    signals: tuple[OrchestratorSignal, ...]
    risks: tuple[OrchestratorRisk, ...]


@dataclass(frozen=True)
class OrchestratorRoute:
    """One route between engines in the orchestration graph."""

    source: str
    target: str
    priority: OrchestratorPriority
    enabled: bool
    reason: str


@dataclass(frozen=True)
class OrchestrationGraph:
    """Graph of active engine routes and priorities."""

    engines: tuple[str, ...]
    routes: tuple[OrchestratorRoute, ...]
    dominant_engine: str | None
    isolated_engines: tuple[str, ...]
    critical_routes: tuple[OrchestratorRoute, ...]


@dataclass(frozen=True)
class OrchestratorTransition:
    """Global mode transition."""

    from_mode: OrchestratorMode
    to_mode: OrchestratorMode
    reason: str
    priority: OrchestratorPriority


@dataclass(frozen=True)
class OrchestratorCycle:
    """Scheduled offline coordination cycle."""

    cycle_id: str
    mode: OrchestratorMode
    priority: OrchestratorPriority
    routes: tuple[OrchestratorRoute, ...]
    actions: tuple[str, ...]
    safe_mode: bool
    requires_supervision: bool


@dataclass(frozen=True)
class CoordinationState:
    """Internal coordination state before final result."""

    mode: OrchestratorMode
    priority: OrchestratorPriority
    confidence_score: int
    risks: tuple[OrchestratorRisk, ...]
    signals: tuple[OrchestratorSignal, ...]


@dataclass(frozen=True)
class CoordinationResult:
    """Final coordination result for active engines."""

    state: CoordinationState
    decision: OrchestratorDecision
    transitions: tuple[OrchestratorTransition, ...]
    cycle: OrchestratorCycle
    recommendations: tuple[OrchestratorRecommendation, ...]
    summary: str


@dataclass(frozen=True)
class OrchestratorEvent:
    """Auditable global orchestration event."""

    mode: OrchestratorMode
    decision: OrchestratorDecision
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class GlobalOrchestratorInput:
    """Inputs consumed by the offline global orchestrator."""

    strategic_arbitration: ArbitrationResult | None = None
    collective_consensus: ConsensusResult | None = None
    intent_alignment: IntentAlignmentResult | None = None
    meta_cognition: MetaCognitionResult | None = None
    operational_awareness: OperationalAwarenessResult | None = None
    mission_continuity: MissionContinuityResult | None = None
    recovery_resilience: RecoveryResilienceResult | None = None
    system_integrity: SystemIntegrityResult | None = None
    learning_governance: LearningGovernanceResult | None = None
    self_evaluation: SelfEvaluationResult | None = None
    supervisor_result: SupervisorResult | None = None
    executive_result: ExecutiveBrainResult | None = None
    strategic_result: StrategicPlanningResult | None = None
    tactical_execution: TacticalExecutionResult | None = None
    behavioral_stability: BehavioralStabilityResult | None = None


@dataclass(frozen=True)
class GlobalOrchestratorResult:
    """Final autonomous global orchestration result."""

    system_state: GlobalSystemState
    graph: OrchestrationGraph
    coordination: CoordinationResult
    decision: OrchestratorDecision
    confidence_score: int
    recommendations: tuple[OrchestratorRecommendation, ...]
    events: tuple[OrchestratorEvent, ...]
    final_message: str


__all__ = [
    "CoordinationResult",
    "CoordinationState",
    "GlobalOrchestratorInput",
    "GlobalOrchestratorResult",
    "GlobalSystemState",
    "OrchestrationGraph",
    "OrchestratorCycle",
    "OrchestratorDecision",
    "OrchestratorEvent",
    "OrchestratorMode",
    "OrchestratorPriority",
    "OrchestratorRecommendation",
    "OrchestratorRisk",
    "OrchestratorRoute",
    "OrchestratorSignal",
    "OrchestratorTransition",
    "SystemHealthSnapshot",
]
