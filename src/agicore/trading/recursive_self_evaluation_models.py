"""Models for the offline Recursive Self-Evaluation Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .behavioral_stability_models import BehavioralStabilityResult
from .cognitive_adaptation_models import CognitiveAdaptationResult
from .executive_brain_models import ExecutiveBrainResult
from .hierarchical_supervisor_models import SupervisorResult
from .learning_governance_models import LearningGovernanceResult
from .meta_strategy_models import MetaStrategySelectionResult
from .multi_agent_models import AgentCoordinationResult
from .reward_models import RewardEvaluationResult
from .scenario_replay_models import ReplayArenaResult
from .strategic_memory_models import StrategicTimelineAnalysis
from .strategic_planning_models import StrategicPlanningResult
from .tactical_execution_models import TacticalExecutionResult


class SelfEvaluationStatus(StrEnum):
    """System self-evaluation status."""

    STABLE = "STABLE"
    DEGRADED = "DEGRADED"
    UNSTABLE = "UNSTABLE"
    CONTRADICTORY = "CONTRADICTORY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    AUTONOMY_REDUCED = "AUTONOMY_REDUCED"


class SystemAutonomyRecommendation(StrEnum):
    """Recommended system autonomy level."""

    MAINTAIN_AUTONOMY = "MAINTAIN_AUTONOMY"
    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    OBSERVE_ONLY = "OBSERVE_ONLY"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    FREEZE_AUTONOMY = "FREEZE_AUTONOMY"
    RECALIBRATE_SYSTEM = "RECALIBRATE_SYSTEM"


class SelfEvaluationSignal(StrEnum):
    """Signals emitted by recursive self-evaluation."""

    DECISION_COHERENCE_STRONG = "DECISION_COHERENCE_STRONG"
    DECISION_COHERENCE_WEAK = "DECISION_COHERENCE_WEAK"
    INTERNAL_CONTRADICTION = "INTERNAL_CONTRADICTION"
    STRATEGIC_INSTABILITY = "STRATEGIC_INSTABILITY"
    BEHAVIORAL_INSTABILITY = "BEHAVIORAL_INSTABILITY"
    COGNITIVE_OVERLOAD = "COGNITIVE_OVERLOAD"
    AGENT_CONSENSUS_WEAK = "AGENT_CONSENSUS_WEAK"
    SUPERVISOR_OVERRIDE_ACTIVE = "SUPERVISOR_OVERRIDE_ACTIVE"
    LEARNING_GOVERNANCE_BLOCK = "LEARNING_GOVERNANCE_BLOCK"
    LOW_CONFIDENCE_SYSTEM = "LOW_CONFIDENCE_SYSTEM"
    HIGH_CONFIDENCE_SYSTEM = "HIGH_CONFIDENCE_SYSTEM"
    RECALIBRATION_NEEDED = "RECALIBRATION_NEEDED"
    AUTONOMY_SAFE = "AUTONOMY_SAFE"
    AUTONOMY_UNSAFE = "AUTONOMY_UNSAFE"


@dataclass(frozen=True)
class SelfEvaluationScore:
    """Self-evaluation component scores normalized to 0..100."""

    decision_coherence_score: int
    strategic_stability_score: int
    behavioral_stability_score: int
    cognitive_stability_score: int
    agent_consensus_score: int
    governance_safety_score: int
    autonomy_readiness_score: int


@dataclass(frozen=True)
class SelfEvaluationInput:
    """Inputs consumed by the offline recursive self-evaluation engine."""

    learning_governance: LearningGovernanceResult | None = None
    cognitive_adaptation: CognitiveAdaptationResult | None = None
    behavioral_stability: BehavioralStabilityResult | None = None
    executive_result: ExecutiveBrainResult | None = None
    supervisor_result: SupervisorResult | None = None
    agent_coordination: AgentCoordinationResult | None = None
    strategic_timeline_analysis: StrategicTimelineAnalysis | None = None
    strategic_result: StrategicPlanningResult | None = None
    meta_strategy: MetaStrategySelectionResult | None = None
    reward_evaluation: RewardEvaluationResult | None = None
    tactical_execution: TacticalExecutionResult | None = None
    replay_arena: ReplayArenaResult | None = None


@dataclass(frozen=True)
class SelfEvaluationEvent:
    """Auditable self-evaluation event."""

    status: SelfEvaluationStatus
    autonomy_recommendation: SystemAutonomyRecommendation
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class SelfEvaluationResult:
    """Final recursive self-evaluation output."""

    status: SelfEvaluationStatus
    autonomy_recommendation: SystemAutonomyRecommendation
    confidence_score: int
    score_breakdown: SelfEvaluationScore
    signals: tuple[SelfEvaluationSignal, ...]
    contradictions: tuple[str, ...]
    recommended_actions: tuple[str, ...]
    events: tuple[SelfEvaluationEvent, ...]
    summary: str


__all__ = [
    "SelfEvaluationEvent",
    "SelfEvaluationInput",
    "SelfEvaluationResult",
    "SelfEvaluationScore",
    "SelfEvaluationSignal",
    "SelfEvaluationStatus",
    "SystemAutonomyRecommendation",
]
