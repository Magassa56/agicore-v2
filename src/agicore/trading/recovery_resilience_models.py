"""Models for the offline Autonomous Recovery & Resilience Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .adaptive_policy_memory_models import AdaptivePolicyMemory
from .behavioral_stability_models import BehavioralStabilityResult
from .cognitive_adaptation_models import CognitiveAdaptationResult
from .learning_governance_models import LearningGovernanceResult
from .recursive_self_evaluation_models import SelfEvaluationResult
from .scenario_replay_models import ReplayArenaResult
from .strategic_memory_models import StrategicTimelineAnalysis
from .strategic_planning_models import StrategicPlanningResult
from .system_integrity_models import SystemIntegrityResult


class RecoveryMode(StrEnum):
    """Recovery mode selected for the offline autonomous stack."""

    NORMAL = "NORMAL"
    STABILIZE = "STABILIZE"
    REDUCE_COMPLEXITY = "REDUCE_COMPLEXITY"
    ISOLATE_MODULES = "ISOLATE_MODULES"
    STRATEGIC_ROLLBACK = "STRATEGIC_ROLLBACK"
    SURVIVAL_MODE = "SURVIVAL_MODE"
    REBUILD_CONFIDENCE = "REBUILD_CONFIDENCE"
    PAUSED_RECOVERY = "PAUSED_RECOVERY"


class RecoveryAction(StrEnum):
    """Actions available to the recovery engine."""

    KEEP_RUNNING = "KEEP_RUNNING"
    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    FREEZE_LEARNING = "FREEZE_LEARNING"
    DISABLE_DANGEROUS_POLICY = "DISABLE_DANGEROUS_POLICY"
    ISOLATE_UNSTABLE_MODULE = "ISOLATE_UNSTABLE_MODULE"
    ENTER_SURVIVAL_MODE = "ENTER_SURVIVAL_MODE"
    RESTORE_LAST_STABLE_STATE = "RESTORE_LAST_STABLE_STATE"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    REBUILD_GRADUALLY = "REBUILD_GRADUALLY"


class RecoveryRisk(StrEnum):
    """Risks that can trigger autonomous recovery controls."""

    SYSTEM_COMPROMISED = "SYSTEM_COMPROMISED"
    MODULE_INSTABILITY = "MODULE_INSTABILITY"
    STRATEGIC_COLLAPSE = "STRATEGIC_COLLAPSE"
    BEHAVIORAL_SPIRAL = "BEHAVIORAL_SPIRAL"
    COGNITIVE_OVERLOAD = "COGNITIVE_OVERLOAD"
    POLICY_FAILURE = "POLICY_FAILURE"
    GOVERNANCE_LOCKDOWN = "GOVERNANCE_LOCKDOWN"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"
    RECOVERY_FAILURE = "RECOVERY_FAILURE"


@dataclass(frozen=True)
class ResilienceScore:
    """Recovery resilience component scores normalized to 0..100."""

    system_integrity_score: int
    module_stability_score: int
    strategic_resilience_score: int
    behavioral_resilience_score: int
    cognitive_resilience_score: int
    governance_resilience_score: int
    policy_resilience_score: int


@dataclass(frozen=True)
class RecoveryStep:
    """One ordered step in the offline recovery plan."""

    order: int
    action: RecoveryAction
    target: str
    reason: str
    completed: bool = False


@dataclass(frozen=True)
class RecoveryResilienceInput:
    """Inputs consumed by the offline recovery and resilience engine."""

    system_integrity: SystemIntegrityResult | None = None
    self_evaluation: SelfEvaluationResult | None = None
    learning_governance: LearningGovernanceResult | None = None
    cognitive_adaptation: CognitiveAdaptationResult | None = None
    behavioral_stability: BehavioralStabilityResult | None = None
    strategic_timeline_analysis: StrategicTimelineAnalysis | None = None
    strategic_result: StrategicPlanningResult | None = None
    policy_memory: AdaptivePolicyMemory | None = None
    replay_arena: ReplayArenaResult | None = None


@dataclass(frozen=True)
class RecoveryEvent:
    """Auditable recovery event."""

    mode: RecoveryMode
    action: RecoveryAction
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class RecoveryResilienceResult:
    """Final autonomous recovery and resilience output."""

    mode: RecoveryMode
    resilience_score: int
    score_breakdown: ResilienceScore
    risks: tuple[RecoveryRisk, ...]
    actions: tuple[RecoveryAction, ...]
    recovery_plan: tuple[RecoveryStep, ...]
    isolated_modules: tuple[str, ...]
    disabled_policies: tuple[str, ...]
    recommendations: tuple[str, ...]
    events: tuple[RecoveryEvent, ...]
    summary: str


__all__ = [
    "RecoveryAction",
    "RecoveryEvent",
    "RecoveryMode",
    "RecoveryResilienceInput",
    "RecoveryResilienceResult",
    "RecoveryRisk",
    "RecoveryStep",
    "ResilienceScore",
]
