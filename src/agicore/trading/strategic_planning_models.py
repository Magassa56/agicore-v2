"""Models for the offline Strategic Planning Engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from .adaptive_memory_models import TraderMemoryProfile
from .adaptive_policy_memory_models import AdaptivePolicyMemory
from .context_scoring_models import ContextScoringResult
from .executive_brain_models import ExecutiveBrainResult
from .hierarchical_supervisor_models import SupervisorResult
from .offline_dataset_models import DatasetQualityReport
from .reward_models import RewardEvaluationResult
from .rl_playground_models import RLPlaygroundResult
from .scenario_replay_models import ReplayArenaResult


class StrategicHorizon(StrEnum):
    """Planning horizon for offline strategic trading decisions."""

    SINGLE_SESSION = "SINGLE_SESSION"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    EVALUATION_ACCOUNT = "EVALUATION_ACCOUNT"
    PROP_FIRM_CHALLENGE = "PROP_FIRM_CHALLENGE"
    LONG_TERM_GROWTH = "LONG_TERM_GROWTH"


class StrategicObjective(StrEnum):
    """Primary objective pursued by the strategic plan."""

    CAPITAL_PRESERVATION = "CAPITAL_PRESERVATION"
    DRAWDOWN_RECOVERY = "DRAWDOWN_RECOVERY"
    CONTROLLED_GROWTH = "CONTROLLED_GROWTH"
    POLICY_VALIDATION = "POLICY_VALIDATION"
    CONSISTENCY_BUILDING = "CONSISTENCY_BUILDING"
    RISK_REDUCTION = "RISK_REDUCTION"
    LEARNING_PHASE = "LEARNING_PHASE"
    PAUSE_AND_REVIEW = "PAUSE_AND_REVIEW"


class StrategicPlanStatus(StrEnum):
    """Operational status of an offline strategic plan."""

    ACTIVE = "ACTIVE"
    DEFENSIVE = "DEFENSIVE"
    RECOVERY = "RECOVERY"
    PAUSED = "PAUSED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    COMPLETED = "COMPLETED"


@dataclass(frozen=True)
class StrategicPlan:
    """Multi-session strategic plan. It never authorizes real trading."""

    horizon: StrategicHorizon
    primary_objective: StrategicObjective
    status: StrategicPlanStatus
    session_objectives: tuple[str, ...]
    risk_constraints: tuple[str, ...]
    max_trades_per_session: int
    max_session_loss_r: float
    focus_behavior: str
    policy_to_test: str | None = None
    progress_metrics: dict[str, float] = field(default_factory=dict)
    long_term_risks: tuple[str, ...] = ()
    recommendations: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class StrategicPlanningInput:
    """Inputs consumed by the offline strategic planning engine."""

    executive_result: ExecutiveBrainResult | None = None
    supervisor_result: SupervisorResult | None = None
    replay_arena: ReplayArenaResult | None = None
    rl_playground: RLPlaygroundResult | None = None
    policy_memory: AdaptivePolicyMemory | None = None
    dataset_quality: DatasetQualityReport | None = None
    reward_evaluation: RewardEvaluationResult | None = None
    context_score: ContextScoringResult | None = None
    trader_memory_profile: TraderMemoryProfile | None = None
    previous_plan: StrategicPlan | None = None
    horizon: StrategicHorizon = StrategicHorizon.WEEKLY


@dataclass(frozen=True)
class StrategicPlanningEvent:
    """Auditable strategic planning event."""

    status: StrategicPlanStatus
    objective: StrategicObjective
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class StrategicPlanningResult:
    """Final output from the offline Strategic Planning Engine."""

    plan: StrategicPlan
    progress_score: int
    progress_notes: tuple[str, ...]
    events: tuple[StrategicPlanningEvent, ...]
    recommendation: str


__all__ = [
    "StrategicHorizon",
    "StrategicObjective",
    "StrategicPlan",
    "StrategicPlanStatus",
    "StrategicPlanningEvent",
    "StrategicPlanningInput",
    "StrategicPlanningResult",
]
