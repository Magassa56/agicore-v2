"""Models for the offline Autonomous Learning Governance Core."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .adaptive_policy_memory_models import AdaptivePolicyMemory
from .behavioral_stability_models import BehavioralStabilityResult
from .cognitive_adaptation_models import CognitiveAdaptationResult
from .executive_brain_models import ExecutiveBrainResult
from .meta_strategy_models import MetaStrategySelectionResult
from .offline_dataset_models import DatasetQualityReport
from .reward_models import RewardEvaluationResult
from .rl_playground_models import RLPlaygroundResult
from .safe_rl_models import SafeRLExperimentResult
from .strategic_memory_models import StrategicTimelineAnalysis
from .strategic_planning_models import StrategicPlanningResult
from .tactical_execution_models import TacticalExecutionResult


class LearningGovernanceMode(StrEnum):
    """Learning governance operating mode."""

    LEARN = "LEARN"
    OBSERVE_ONLY = "OBSERVE_ONLY"
    FREEZE_LEARNING = "FREEZE_LEARNING"
    REDUCE_ADAPTATION = "REDUCE_ADAPTATION"
    EXPLOIT_ONLY = "EXPLOIT_ONLY"
    RECOVERY_MODE = "RECOVERY_MODE"
    SAFETY_LOCKDOWN = "SAFETY_LOCKDOWN"


class LearningGovernanceDecision(StrEnum):
    """Final learning governance decision."""

    ALLOW_LEARNING = "ALLOW_LEARNING"
    ALLOW_LIMITED_LEARNING = "ALLOW_LIMITED_LEARNING"
    PAUSE_LEARNING = "PAUSE_LEARNING"
    FREEZE_POLICY_UPDATE = "FREEZE_POLICY_UPDATE"
    LOCK_DANGEROUS_POLICY = "LOCK_DANGEROUS_POLICY"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    ENTER_SAFETY_LOCKDOWN = "ENTER_SAFETY_LOCKDOWN"


class LearningGovernanceRisk(StrEnum):
    """Risks detected before allowing autonomous learning updates."""

    OVERFITTING_RISK = "OVERFITTING_RISK"
    POLICY_DRIFT_RISK = "POLICY_DRIFT_RISK"
    REWARD_HACKING_RISK = "REWARD_HACKING_RISK"
    BEHAVIORAL_INSTABILITY = "BEHAVIORAL_INSTABILITY"
    COGNITIVE_OVERLOAD = "COGNITIVE_OVERLOAD"
    LOW_DATASET_QUALITY = "LOW_DATASET_QUALITY"
    UNSAFE_RL_STATUS = "UNSAFE_RL_STATUS"
    STRATEGIC_DEGRADATION = "STRATEGIC_DEGRADATION"
    TACTICAL_DETERIORATION = "TACTICAL_DETERIORATION"
    EXCESSIVE_ADAPTATION = "EXCESSIVE_ADAPTATION"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class LearningCycleStatus(StrEnum):
    """Status of the governed offline learning cycle."""

    READY = "READY"
    LIMITED = "LIMITED"
    OBSERVING = "OBSERVING"
    FROZEN = "FROZEN"
    RECOVERY = "RECOVERY"
    LOCKED_DOWN = "LOCKED_DOWN"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"


@dataclass(frozen=True)
class LearningGovernanceInput:
    """Inputs consumed by the offline learning governance core."""

    cognitive_adaptation: CognitiveAdaptationResult | None = None
    behavioral_stability: BehavioralStabilityResult | None = None
    strategic_timeline_analysis: StrategicTimelineAnalysis | None = None
    strategic_result: StrategicPlanningResult | None = None
    safe_rl_result: SafeRLExperimentResult | None = None
    rl_playground: RLPlaygroundResult | None = None
    dataset_quality: DatasetQualityReport | None = None
    policy_memory: AdaptivePolicyMemory | None = None
    meta_strategy: MetaStrategySelectionResult | None = None
    reward_evaluation: RewardEvaluationResult | None = None
    tactical_execution: TacticalExecutionResult | None = None
    executive_result: ExecutiveBrainResult | None = None


@dataclass(frozen=True)
class LearningGovernanceEvent:
    """Auditable learning governance event."""

    decision: LearningGovernanceDecision
    mode: LearningGovernanceMode
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class LearningGovernanceResult:
    """Final governance result for offline autonomous learning."""

    decision: LearningGovernanceDecision
    mode: LearningGovernanceMode
    cycle_status: LearningCycleStatus
    risks: tuple[LearningGovernanceRisk, ...]
    locked_policies: tuple[str, ...]
    learning_conditions: tuple[str, ...]
    recommended_actions: tuple[str, ...]
    events: tuple[LearningGovernanceEvent, ...]
    safety_summary: str


__all__ = [
    "LearningCycleStatus",
    "LearningGovernanceDecision",
    "LearningGovernanceEvent",
    "LearningGovernanceInput",
    "LearningGovernanceMode",
    "LearningGovernanceResult",
    "LearningGovernanceRisk",
]
