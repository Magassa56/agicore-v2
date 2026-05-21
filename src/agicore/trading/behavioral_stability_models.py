"""Models for the offline Behavioral Stability Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .context_scoring_models import ContextScoringResult
from .executive_brain_models import ExecutiveBrainResult
from .reward_models import RewardEvaluationResult
from .scenario_replay_models import ReplayArenaResult
from .session_coach_models import LiveSessionCoachResult
from .strategic_memory_models import StrategicTimelineAnalysis
from .strategic_planning_models import StrategicPlanningResult
from .tactical_execution_models import TacticalExecutionResult
from .trade_journal_models import JournalAnalysisResult


class BehavioralPressureLevel(StrEnum):
    """Psychological pressure bucket."""

    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class BehavioralRiskSignal(StrEnum):
    """Behavioral and psychological risk signals."""

    TILT_RISK = "TILT_RISK"
    REVENGE_RISK = "REVENGE_RISK"
    DISCIPLINE_DECAY = "DISCIPLINE_DECAY"
    FATIGUE_RISK = "FATIGUE_RISK"
    OVERCONFIDENCE_RISK = "OVERCONFIDENCE_RISK"
    FEAR_BLOCK = "FEAR_BLOCK"
    HESITATION_SPIRAL = "HESITATION_SPIRAL"
    EMOTIONAL_INSTABILITY = "EMOTIONAL_INSTABILITY"
    RECOVERY_IN_PROGRESS = "RECOVERY_IN_PROGRESS"
    STABLE_BEHAVIOR = "STABLE_BEHAVIOR"
    PSYCHOLOGICAL_PRESSURE_HIGH = "PSYCHOLOGICAL_PRESSURE_HIGH"
    SESSION_OVERLOAD = "SESSION_OVERLOAD"
    CONSISTENT_DISCIPLINE = "CONSISTENT_DISCIPLINE"


class BehavioralRecoveryState(StrEnum):
    """Recovery state after behavioral pressure or drawdown."""

    STABLE = "STABLE"
    RECOVERING = "RECOVERING"
    FRAGILE = "FRAGILE"
    DETERIORATING = "DETERIORATING"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class BehavioralStabilityScore:
    """Behavioral component scores normalized to 0..100."""

    discipline_score: int
    emotional_control_score: int
    fatigue_score: int
    pressure_resilience_score: int
    recovery_score: int
    consistency_score: int


@dataclass(frozen=True)
class BehavioralStabilityInput:
    """Inputs consumed by the offline Behavioral Stability Engine."""

    tactical_execution: TacticalExecutionResult | None = None
    strategic_timeline_analysis: StrategicTimelineAnalysis | None = None
    strategic_result: StrategicPlanningResult | None = None
    reward_evaluation: RewardEvaluationResult | None = None
    journal_result: JournalAnalysisResult | None = None
    session_coach_result: LiveSessionCoachResult | None = None
    executive_result: ExecutiveBrainResult | None = None
    context_score: ContextScoringResult | None = None
    replay_arena: ReplayArenaResult | None = None


@dataclass(frozen=True)
class BehavioralStabilityEvent:
    """Auditable behavioral stability event."""

    pressure_level: BehavioralPressureLevel
    recovery_state: BehavioralRecoveryState
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class BehavioralStabilityResult:
    """Final offline behavioral stability result."""

    stability_score: int
    pressure_level: BehavioralPressureLevel
    recovery_state: BehavioralRecoveryState
    score_breakdown: BehavioralStabilityScore
    signals: tuple[BehavioralRiskSignal, ...]
    risks: tuple[str, ...]
    recommendations: tuple[str, ...]
    events: tuple[BehavioralStabilityEvent, ...]


__all__ = [
    "BehavioralPressureLevel",
    "BehavioralRecoveryState",
    "BehavioralRiskSignal",
    "BehavioralStabilityEvent",
    "BehavioralStabilityInput",
    "BehavioralStabilityResult",
    "BehavioralStabilityScore",
]
