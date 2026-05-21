"""Models for the offline Cognitive Adaptation Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .behavioral_stability_models import BehavioralStabilityResult
from .context_scoring_models import ContextScoringResult
from .executive_brain_models import ExecutiveBrainResult
from .hierarchical_supervisor_models import SupervisorResult
from .meta_strategy_models import MetaStrategySelectionResult
from .reward_models import RewardEvaluationResult
from .scenario_replay_models import ReplayArenaResult
from .strategic_memory_models import StrategicTimelineAnalysis
from .strategic_planning_models import StrategicPlanningResult
from .tactical_execution_models import TacticalExecutionResult


class CognitiveLoadLevel(StrEnum):
    """Cognitive load bucket."""

    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    OVERLOADED = "OVERLOADED"


class CognitiveAdaptationMode(StrEnum):
    """Recommended cognitive adaptation mode."""

    OBSERVE = "OBSERVE"
    ADAPT = "ADAPT"
    SLOW_DOWN = "SLOW_DOWN"
    RECOVER = "RECOVER"
    PAUSE = "PAUSE"
    EXPLOIT_STABLE_PATTERN = "EXPLOIT_STABLE_PATTERN"


class CognitiveAdaptationSignal(StrEnum):
    """Signals emitted by cognitive adaptation analysis."""

    STRATEGIC_CLARITY_HIGH = "STRATEGIC_CLARITY_HIGH"
    STRATEGIC_CLARITY_LOW = "STRATEGIC_CLARITY_LOW"
    DECISION_CONFUSION = "DECISION_CONFUSION"
    COGNITIVE_OVERLOAD = "COGNITIVE_OVERLOAD"
    RIGID_POLICY_USE = "RIGID_POLICY_USE"
    FLEXIBLE_ADAPTATION = "FLEXIBLE_ADAPTATION"
    CONTEXT_SHIFT_DETECTED = "CONTEXT_SHIFT_DETECTED"
    ADAPTATION_SUCCESS = "ADAPTATION_SUCCESS"
    ADAPTATION_FAILURE = "ADAPTATION_FAILURE"
    OVER_REACTION_RISK = "OVER_REACTION_RISK"
    UNDER_REACTION_RISK = "UNDER_REACTION_RISK"
    OBSERVATION_MODE_RECOMMENDED = "OBSERVATION_MODE_RECOMMENDED"
    STABLE_PATTERN_EXPLOITABLE = "STABLE_PATTERN_EXPLOITABLE"


@dataclass(frozen=True)
class CognitiveFlexibilityScore:
    """Cognitive component scores normalized to 0..100."""

    strategic_clarity_score: int
    decision_flexibility_score: int
    cognitive_load_score: int
    context_adaptation_score: int
    policy_adaptation_score: int
    recovery_learning_score: int


@dataclass(frozen=True)
class CognitiveAdaptationInput:
    """Inputs consumed by the offline Cognitive Adaptation Engine."""

    behavioral_stability: BehavioralStabilityResult | None = None
    strategic_timeline_analysis: StrategicTimelineAnalysis | None = None
    strategic_result: StrategicPlanningResult | None = None
    executive_result: ExecutiveBrainResult | None = None
    supervisor_result: SupervisorResult | None = None
    meta_strategy: MetaStrategySelectionResult | None = None
    replay_arena: ReplayArenaResult | None = None
    tactical_execution: TacticalExecutionResult | None = None
    context_score: ContextScoringResult | None = None
    reward_evaluation: RewardEvaluationResult | None = None


@dataclass(frozen=True)
class CognitiveAdaptationEvent:
    """Auditable cognitive adaptation event."""

    mode: CognitiveAdaptationMode
    load_level: CognitiveLoadLevel
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class CognitiveAdaptationResult:
    """Final offline cognitive adaptation output."""

    adaptation_mode: CognitiveAdaptationMode
    load_level: CognitiveLoadLevel
    global_score: int
    flexibility_score: CognitiveFlexibilityScore
    signals: tuple[CognitiveAdaptationSignal, ...]
    risks: tuple[str, ...]
    recommendations: tuple[str, ...]
    events: tuple[CognitiveAdaptationEvent, ...]


__all__ = [
    "CognitiveAdaptationEvent",
    "CognitiveAdaptationInput",
    "CognitiveAdaptationMode",
    "CognitiveAdaptationResult",
    "CognitiveAdaptationSignal",
    "CognitiveFlexibilityScore",
    "CognitiveLoadLevel",
]
