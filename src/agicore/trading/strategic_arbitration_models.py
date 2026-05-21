"""Models for the offline Autonomous Strategic Arbitration Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .behavioral_stability_models import BehavioralStabilityResult
from .executive_brain_models import ExecutiveBrainResult
from .hierarchical_supervisor_models import SupervisorResult
from .intent_alignment_models import IntentAlignmentResult
from .learning_governance_models import LearningGovernanceResult
from .meta_cognition_models import MetaCognitionResult
from .mission_continuity_models import MissionContinuityResult
from .operational_awareness_models import OperationalAwarenessResult
from .recovery_resilience_models import RecoveryResilienceResult
from .recursive_self_evaluation_models import SelfEvaluationResult
from .strategic_planning_models import StrategicPlanningResult
from .system_integrity_models import SystemIntegrityResult
from .tactical_execution_models import TacticalExecutionResult


class ArbitrationMode(StrEnum):
    """Operating mode selected by strategic arbitration."""

    NORMAL_OPERATION = "NORMAL_OPERATION"
    SAFE_COORDINATION = "SAFE_COORDINATION"
    PROTECTIVE_ARBITRATION = "PROTECTIVE_ARBITRATION"
    SURVIVAL_MODE = "SURVIVAL_MODE"
    MISSION_PRIORITY = "MISSION_PRIORITY"
    INTEGRITY_PRIORITY = "INTEGRITY_PRIORITY"
    SUPERVISED_MODE = "SUPERVISED_MODE"
    EMERGENCY_LOCKDOWN = "EMERGENCY_LOCKDOWN"


class ArbitrationPriority(StrEnum):
    """Hard priority hierarchy used to resolve strategic conflicts."""

    SURVIVAL = "SURVIVAL"
    INTEGRITY = "INTEGRITY"
    SAFETY = "SAFETY"
    MISSION = "MISSION"
    CONTINUITY = "CONTINUITY"
    SUPERVISION = "SUPERVISION"
    STRATEGY = "STRATEGY"
    PERFORMANCE = "PERFORMANCE"
    LEARNING = "LEARNING"


class ArbitrationSeverity(StrEnum):
    """Severity assigned to a strategic conflict or final state."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ArbitrationDecision(StrEnum):
    """Final decision emitted by the arbitrator."""

    CONTINUE_OPERATION = "CONTINUE_OPERATION"
    REDUCE_RISK = "REDUCE_RISK"
    ENABLE_SAFE_MODE = "ENABLE_SAFE_MODE"
    FREEZE_LEARNING = "FREEZE_LEARNING"
    REQUIRE_SUPERVISION = "REQUIRE_SUPERVISION"
    ROLLBACK_STRATEGY = "ROLLBACK_STRATEGY"
    STOP_EXECUTION = "STOP_EXECUTION"
    EMERGENCY_LOCKDOWN = "EMERGENCY_LOCKDOWN"


class ArbitrationConflictType(StrEnum):
    """Strategic conflict types recognized by the arbitrator."""

    PROFIT_VS_SAFETY = "PROFIT_VS_SAFETY"
    LEARNING_VS_STABILITY = "LEARNING_VS_STABILITY"
    MISSION_VS_EXECUTION = "MISSION_VS_EXECUTION"
    AUTONOMY_VS_SUPERVISION = "AUTONOMY_VS_SUPERVISION"
    SPEED_VS_INTEGRITY = "SPEED_VS_INTEGRITY"
    RECOVERY_VS_CONTINUITY = "RECOVERY_VS_CONTINUITY"
    COGNITION_VS_RISK = "COGNITION_VS_RISK"
    STRATEGY_VS_DISCIPLINE = "STRATEGY_VS_DISCIPLINE"
    EXECUTION_VS_ALIGNMENT = "EXECUTION_VS_ALIGNMENT"
    SURVIVAL_VS_PERFORMANCE = "SURVIVAL_VS_PERFORMANCE"


class ArbitrationRecommendation(StrEnum):
    """Recommended controls after arbitration."""

    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    FREEZE_LEARNING = "FREEZE_LEARNING"
    ENABLE_SAFE_MODE = "ENABLE_SAFE_MODE"
    REQUIRE_HUMAN_SUPERVISION = "REQUIRE_HUMAN_SUPERVISION"
    ROLLBACK_STRATEGY = "ROLLBACK_STRATEGY"
    ISOLATE_MODULE = "ISOLATE_MODULE"
    PROTECT_MEMORY = "PROTECT_MEMORY"
    SLOW_EXECUTION = "SLOW_EXECUTION"
    LOCK_HIGH_RISK_ACTIONS = "LOCK_HIGH_RISK_ACTIONS"
    CONTINUE_OPERATION = "CONTINUE_OPERATION"


class ArbitrationAuthority(StrEnum):
    """Authority that owns the winning priority."""

    SURVIVAL_CONTROLLER = "SURVIVAL_CONTROLLER"
    INTEGRITY_CONTROLLER = "INTEGRITY_CONTROLLER"
    SAFETY_GUARDIAN = "SAFETY_GUARDIAN"
    MISSION_GUARDIAN = "MISSION_GUARDIAN"
    CONTINUITY_MANAGER = "CONTINUITY_MANAGER"
    SUPERVISION_CONTROLLER = "SUPERVISION_CONTROLLER"
    STRATEGY_DIRECTOR = "STRATEGY_DIRECTOR"
    PERFORMANCE_MANAGER = "PERFORMANCE_MANAGER"
    LEARNING_GOVERNOR = "LEARNING_GOVERNOR"


class ArbitrationState(StrEnum):
    """Coarse state of the arbitration layer."""

    STABLE = "STABLE"
    CONFLICT_DETECTED = "CONFLICT_DETECTED"
    SAFE_MODE_REQUIRED = "SAFE_MODE_REQUIRED"
    SUPERVISION_REQUIRED = "SUPERVISION_REQUIRED"
    LOCKDOWN_REQUIRED = "LOCKDOWN_REQUIRED"


@dataclass(frozen=True)
class StrategicConflict:
    """One detected strategic conflict."""

    conflict_type: ArbitrationConflictType
    severity: ArbitrationSeverity
    priorities: tuple[ArbitrationPriority, ...]
    description: str


@dataclass(frozen=True)
class ArbitrationInput:
    """Inputs consumed by the offline strategic arbitration engine."""

    intent_alignment: IntentAlignmentResult | None = None
    meta_cognition: MetaCognitionResult | None = None
    operational_awareness: OperationalAwarenessResult | None = None
    mission_continuity: MissionContinuityResult | None = None
    recovery_resilience: RecoveryResilienceResult | None = None
    system_integrity: SystemIntegrityResult | None = None
    learning_governance: LearningGovernanceResult | None = None
    self_evaluation: SelfEvaluationResult | None = None
    executive_result: ExecutiveBrainResult | None = None
    supervisor_result: SupervisorResult | None = None
    strategic_result: StrategicPlanningResult | None = None
    tactical_execution: TacticalExecutionResult | None = None
    behavioral_stability: BehavioralStabilityResult | None = None


@dataclass(frozen=True)
class ArbitrationResolution:
    """Resolution selected for one conflict."""

    conflict_type: ArbitrationConflictType
    winning_priority: ArbitrationPriority
    authority: ArbitrationAuthority
    decision: ArbitrationDecision
    reason: str


@dataclass(frozen=True)
class PriorityGraph:
    """Static priority graph used for explainable arbitration."""

    ordered_priorities: tuple[ArbitrationPriority, ...]
    edges: tuple[tuple[ArbitrationPriority, ArbitrationPriority], ...]
    active_priorities: tuple[ArbitrationPriority, ...]
    dominant_priority: ArbitrationPriority


@dataclass(frozen=True)
class ArbitrationEvent:
    """Auditable arbitration event."""

    mode: ArbitrationMode
    decision: ArbitrationDecision
    severity: ArbitrationSeverity
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class ArbitrationResult:
    """Final strategic arbitration result."""

    mode: ArbitrationMode
    state: ArbitrationState
    decision: ArbitrationDecision
    severity: ArbitrationSeverity
    confidence_score: int
    dominant_priority: ArbitrationPriority
    active_authorities: tuple[ArbitrationAuthority, ...]
    conflicts: tuple[StrategicConflict, ...]
    resolutions: tuple[ArbitrationResolution, ...]
    priority_graph: PriorityGraph
    recommendations: tuple[ArbitrationRecommendation, ...]
    emergency_lockdown: bool
    final_message: str
    events: tuple[ArbitrationEvent, ...]


__all__ = [
    "ArbitrationAuthority",
    "ArbitrationConflictType",
    "ArbitrationDecision",
    "ArbitrationEvent",
    "ArbitrationInput",
    "ArbitrationMode",
    "ArbitrationPriority",
    "ArbitrationRecommendation",
    "ArbitrationResolution",
    "ArbitrationResult",
    "ArbitrationSeverity",
    "ArbitrationState",
    "PriorityGraph",
    "StrategicConflict",
]
