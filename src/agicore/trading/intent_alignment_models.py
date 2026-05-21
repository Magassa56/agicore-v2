"""Models for the offline Autonomous Intent Alignment Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .executive_brain_models import ExecutiveBrainResult
from .hierarchical_supervisor_models import SupervisorResult
from .learning_governance_models import LearningGovernanceResult
from .meta_cognition_models import MetaCognitionResult
from .mission_continuity_models import MissionContinuityResult
from .operational_awareness_models import OperationalAwarenessResult
from .recovery_resilience_models import RecoveryResilienceResult
from .recursive_self_evaluation_models import SelfEvaluationResult
from .strategic_planning_models import StrategicPlanningResult
from .system_integrity_models import SystemIntegrityResult


class IntentAlignmentMode(StrEnum):
    """Global intent alignment mode for the offline trading stack."""

    FULLY_ALIGNED = "FULLY_ALIGNED"
    STABLE_ALIGNMENT = "STABLE_ALIGNMENT"
    PARTIAL_DRIFT = "PARTIAL_DRIFT"
    PRIORITY_CONFLICT = "PRIORITY_CONFLICT"
    AUTONOMY_DRIFT = "AUTONOMY_DRIFT"
    STRATEGIC_DIVERGENCE = "STRATEGIC_DIVERGENCE"
    MISALIGNED = "MISALIGNED"
    CRITICAL_REALIGNMENT = "CRITICAL_REALIGNMENT"


class IntentAlignmentState(StrEnum):
    """Coarse alignment state."""

    ALIGNED = "ALIGNED"
    MONITORED = "MONITORED"
    DRIFTING = "DRIFTING"
    CONFLICTED = "CONFLICTED"
    MISALIGNED = "MISALIGNED"
    CRITICAL = "CRITICAL"


class IntentConflict(StrEnum):
    """Intent conflicts detected between autonomous layers."""

    EXECUTIVE_GOVERNANCE_CONFLICT = "EXECUTIVE_GOVERNANCE_CONFLICT"
    EXECUTIVE_SUPERVISOR_CONFLICT = "EXECUTIVE_SUPERVISOR_CONFLICT"
    STRATEGY_GOVERNANCE_CONFLICT = "STRATEGY_GOVERNANCE_CONFLICT"
    SAFETY_MISSION_CONFLICT = "SAFETY_MISSION_CONFLICT"
    AUTONOMY_SUPERVISION_CONFLICT = "AUTONOMY_SUPERVISION_CONFLICT"
    PRIORITY_COLLISION = "PRIORITY_COLLISION"
    OFFLINE_BOUNDARY_CONFLICT = "OFFLINE_BOUNDARY_CONFLICT"


class IntentDrift(StrEnum):
    """Intent drifts detected before they become hard conflicts."""

    AUTONOMY_EXPANDING = "AUTONOMY_EXPANDING"
    MISSION_DIVERGING = "MISSION_DIVERGING"
    STRATEGY_DIVERGING = "STRATEGY_DIVERGING"
    SAFETY_BOUNDARY_WEAKENING = "SAFETY_BOUNDARY_WEAKENING"
    GOVERNANCE_DRIFTING = "GOVERNANCE_DRIFTING"
    PRIORITY_FRAGMENTING = "PRIORITY_FRAGMENTING"
    RECURSIVE_GOAL_DRIFT = "RECURSIVE_GOAL_DRIFT"


class IntentPriority(StrEnum):
    """Ordered intent priorities used by alignment checks."""

    SAFETY = "SAFETY"
    OFFLINE_ONLY = "OFFLINE_ONLY"
    CAPITAL_PRESERVATION = "CAPITAL_PRESERVATION"
    GOVERNANCE = "GOVERNANCE"
    STRATEGIC_CONSISTENCY = "STRATEGIC_CONSISTENCY"
    LEARNING = "LEARNING"
    AUTONOMY = "AUTONOMY"
    EXECUTION = "EXECUTION"


class IntentRisk(StrEnum):
    """Risks that can break mission and safety alignment."""

    GOAL_FRAGMENTATION = "GOAL_FRAGMENTATION"
    AUTONOMY_EXPANSION = "AUTONOMY_EXPANSION"
    PRIORITY_COLLISION = "PRIORITY_COLLISION"
    STRATEGIC_MISALIGNMENT = "STRATEGIC_MISALIGNMENT"
    SAFETY_BOUNDARY_DRIFT = "SAFETY_BOUNDARY_DRIFT"
    REASONING_OBJECTIVE_CONFLICT = "REASONING_OBJECTIVE_CONFLICT"
    EXECUTIVE_PRIORITY_DRIFT = "EXECUTIVE_PRIORITY_DRIFT"
    RECURSIVE_GOAL_INSTABILITY = "RECURSIVE_GOAL_INSTABILITY"
    MISSION_DIVERGENCE = "MISSION_DIVERGENCE"
    ALIGNMENT_COLLAPSE = "ALIGNMENT_COLLAPSE"


class IntentRecommendation(StrEnum):
    """Recommended controls to restore or preserve alignment."""

    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    REQUIRE_ALIGNMENT_REVIEW = "REQUIRE_ALIGNMENT_REVIEW"
    RESTORE_PRIORITY_ORDER = "RESTORE_PRIORITY_ORDER"
    REINFORCE_SAFETY_CONSTRAINTS = "REINFORCE_SAFETY_CONSTRAINTS"
    FREEZE_OBJECTIVE_EXPANSION = "FREEZE_OBJECTIVE_EXPANSION"
    RECALIBRATE_STRATEGIC_GOALS = "RECALIBRATE_STRATEGIC_GOALS"
    REQUIRE_SUPERVISION = "REQUIRE_SUPERVISION"
    ENTER_ALIGNMENT_SAFE_MODE = "ENTER_ALIGNMENT_SAFE_MODE"
    CONTINUE_MONITORING = "CONTINUE_MONITORING"
    MAINTAIN_ALIGNMENT = "MAINTAIN_ALIGNMENT"


@dataclass(frozen=True)
class IntentConfidence:
    """Alignment component scores normalized to 0..100."""

    mission_alignment_score: int
    safety_alignment_score: int
    governance_alignment_score: int
    strategic_alignment_score: int
    priority_stability_score: int
    autonomy_alignment_score: int
    offline_boundary_score: int


@dataclass(frozen=True)
class IntentAlignmentInput:
    """Inputs consumed by the offline intent alignment engine."""

    meta_cognition: MetaCognitionResult | None = None
    operational_awareness: OperationalAwarenessResult | None = None
    mission_continuity: MissionContinuityResult | None = None
    recovery_resilience: RecoveryResilienceResult | None = None
    system_integrity: SystemIntegrityResult | None = None
    executive_result: ExecutiveBrainResult | None = None
    strategic_result: StrategicPlanningResult | None = None
    learning_governance: LearningGovernanceResult | None = None
    self_evaluation: SelfEvaluationResult | None = None
    supervisor_result: SupervisorResult | None = None


@dataclass(frozen=True)
class IntentAlignmentEvent:
    """Auditable intent alignment event."""

    mode: IntentAlignmentMode
    state: IntentAlignmentState
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class IntentAlignmentResult:
    """Final intent alignment assessment."""

    mode: IntentAlignmentMode
    state: IntentAlignmentState
    alignment_confidence: int
    confidence_breakdown: IntentConfidence
    priority_order: tuple[IntentPriority, ...]
    conflicts: tuple[IntentConflict, ...]
    drifts: tuple[IntentDrift, ...]
    risks: tuple[IntentRisk, ...]
    recommendations: tuple[IntentRecommendation, ...]
    mission_status: str
    strategic_goal_stability_score: int
    events: tuple[IntentAlignmentEvent, ...]
    summary: str


__all__ = [
    "IntentAlignmentEvent",
    "IntentAlignmentInput",
    "IntentAlignmentMode",
    "IntentAlignmentResult",
    "IntentAlignmentState",
    "IntentConfidence",
    "IntentConflict",
    "IntentDrift",
    "IntentPriority",
    "IntentRecommendation",
    "IntentRisk",
]
