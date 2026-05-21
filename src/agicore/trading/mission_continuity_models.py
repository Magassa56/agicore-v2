"""Models for the offline Autonomous Mission Continuity Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .adaptive_policy_memory_models import AdaptivePolicyMemory
from .executive_brain_models import ExecutiveBrainResult
from .hierarchical_supervisor_models import SupervisorResult
from .learning_governance_models import LearningGovernanceResult
from .multi_agent_models import AgentCoordinationResult
from .recursive_self_evaluation_models import SelfEvaluationResult
from .recovery_resilience_models import RecoveryResilienceResult
from .strategic_memory_models import StrategicTimelineAnalysis
from .system_integrity_models import SystemIntegrityResult


class MissionContinuityMode(StrEnum):
    """Operating mode selected to preserve mission continuity."""

    FULL_OPERATION = "FULL_OPERATION"
    DEGRADED_OPERATION = "DEGRADED_OPERATION"
    ESSENTIAL_ONLY = "ESSENTIAL_ONLY"
    SURVIVAL_CONTINUITY = "SURVIVAL_CONTINUITY"
    ISOLATED_OPERATION = "ISOLATED_OPERATION"
    SAFE_PAUSE = "SAFE_PAUSE"
    RECOVERY_TRANSITION = "RECOVERY_TRANSITION"


class MissionCriticality(StrEnum):
    """Criticality level for one module or service."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"
    OPTIONAL = "OPTIONAL"


class ContinuityAction(StrEnum):
    """Actions available to preserve offline mission continuity."""

    KEEP_CORE_RUNNING = "KEEP_CORE_RUNNING"
    DISABLE_NON_CRITICAL = "DISABLE_NON_CRITICAL"
    PRESERVE_MEMORY = "PRESERVE_MEMORY"
    FREEZE_LEARNING = "FREEZE_LEARNING"
    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    ACTIVATE_SAFE_MODE = "ACTIVATE_SAFE_MODE"
    ISOLATE_FAILURE_DOMAIN = "ISOLATE_FAILURE_DOMAIN"
    RESTORE_ESSENTIAL_SERVICES = "RESTORE_ESSENTIAL_SERVICES"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    PREPARE_RECOVERY_PHASE = "PREPARE_RECOVERY_PHASE"


class ContinuityRisk(StrEnum):
    """Risks that can break continuity under degraded operation."""

    CORE_FAILURE = "CORE_FAILURE"
    MEMORY_RISK = "MEMORY_RISK"
    CASCADING_FAILURE = "CASCADING_FAILURE"
    EXECUTIVE_COLLAPSE = "EXECUTIVE_COLLAPSE"
    STRATEGIC_MEMORY_LOSS = "STRATEGIC_MEMORY_LOSS"
    AUTONOMY_UNSTABLE = "AUTONOMY_UNSTABLE"
    RECOVERY_LOOP = "RECOVERY_LOOP"
    SUPERVISION_FAILURE = "SUPERVISION_FAILURE"
    RESOURCE_EXHAUSTION = "RESOURCE_EXHAUSTION"
    CONTINUITY_BREAKDOWN = "CONTINUITY_BREAKDOWN"


@dataclass(frozen=True)
class MissionContinuityScore:
    """Mission continuity component scores normalized to 0..100."""

    core_continuity_score: int
    memory_preservation_score: int
    supervision_score: int
    autonomy_stability_score: int
    recovery_readiness_score: int
    service_availability_score: int
    cascading_failure_resistance_score: int


@dataclass(frozen=True)
class ContinuityModuleState:
    """State of one module under continuity planning."""

    module_name: str
    criticality: MissionCriticality
    enabled: bool
    isolated: bool
    preserved: bool
    reason: str


@dataclass(frozen=True)
class ContinuityEvent:
    """Auditable continuity event."""

    mode: MissionContinuityMode
    action: ContinuityAction
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class MissionContinuityInput:
    """Inputs consumed by the offline mission continuity engine."""

    recovery_resilience: RecoveryResilienceResult | None = None
    system_integrity: SystemIntegrityResult | None = None
    executive_result: ExecutiveBrainResult | None = None
    strategic_timeline_analysis: StrategicTimelineAnalysis | None = None
    learning_governance: LearningGovernanceResult | None = None
    self_evaluation: SelfEvaluationResult | None = None
    agent_coordination: AgentCoordinationResult | None = None
    supervisor_result: SupervisorResult | None = None
    policy_memory: AdaptivePolicyMemory | None = None


@dataclass(frozen=True)
class MissionContinuityResult:
    """Final mission continuity output."""

    mode: MissionContinuityMode
    continuity_score: int
    score_breakdown: MissionContinuityScore
    risks: tuple[ContinuityRisk, ...]
    actions: tuple[ContinuityAction, ...]
    module_states: tuple[ContinuityModuleState, ...]
    critical_modules: tuple[str, ...]
    disabled_modules: tuple[str, ...]
    recovery_preparation: tuple[str, ...]
    recommendations: tuple[str, ...]
    events: tuple[ContinuityEvent, ...]
    summary: str


__all__ = [
    "ContinuityAction",
    "ContinuityEvent",
    "ContinuityModuleState",
    "ContinuityRisk",
    "MissionContinuityInput",
    "MissionContinuityMode",
    "MissionContinuityResult",
    "MissionContinuityScore",
    "MissionCriticality",
]
