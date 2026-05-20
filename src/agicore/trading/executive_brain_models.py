"""Models for the offline Executive Decision Brain."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .adaptive_policy_memory_models import AdaptivePolicyMemory
from .autonomous_simulation_models import AutonomousSimulationResult
from .context_scoring_models import ContextScoringResult
from .hierarchical_supervisor_models import SupervisorResult
from .meta_strategy_models import MetaStrategySelectionResult
from .multi_agent_models import AgentCoordinationResult
from .reward_models import RewardEvaluationResult
from .safe_rl_models import SafeRLExperimentResult
from .scenario_replay_models import ReplayArenaResult


class ExecutiveMode(StrEnum):
    """Global operating mode for AGIcore Trading."""

    NORMAL = "NORMAL"
    DEFENSIVE = "DEFENSIVE"
    SURVIVAL = "SURVIVAL"
    RECOVERY = "RECOVERY"
    OPPORTUNITY = "OPPORTUNITY"
    PAUSED = "PAUSED"


class ExecutiveIntent(StrEnum):
    """Strategic intention selected by the executive brain."""

    CAPITAL_PRESERVATION = "CAPITAL_PRESERVATION"
    CONTROLLED_GROWTH = "CONTROLLED_GROWTH"
    LEARNING_ONLY = "LEARNING_ONLY"
    POLICY_TESTING = "POLICY_TESTING"
    RISK_REDUCTION = "RISK_REDUCTION"
    SESSION_STOP = "SESSION_STOP"


class ExecutiveRiskAppetite(StrEnum):
    """Dynamic executive risk appetite."""

    NONE = "NONE"
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MODERATE = "MODERATE"
    ELEVATED = "ELEVATED"


@dataclass(frozen=True)
class ExecutiveState:
    """Current executive state and active constraints."""

    mode: ExecutiveMode
    intent: ExecutiveIntent
    risk_appetite: ExecutiveRiskAppetite
    session_objective: str
    active_constraints: tuple[str, ...]
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ExecutiveDecision:
    """Executable executive-level decision."""

    allow_execution: bool
    allow_reduced_risk_only: bool
    require_human_review: bool
    stop_session: bool
    decision_label: str
    action: str


@dataclass(frozen=True)
class ExecutiveBrainInput:
    """Inputs consumed by the offline Executive Decision Brain."""

    supervisor_result: SupervisorResult | None = None
    agent_coordination: AgentCoordinationResult | None = None
    context_score: ContextScoringResult | None = None
    safe_rl_result: SafeRLExperimentResult | None = None
    reward_evaluation: RewardEvaluationResult | None = None
    replay_arena: ReplayArenaResult | None = None
    policy_memory: AdaptivePolicyMemory | None = None
    meta_strategy: MetaStrategySelectionResult | None = None
    autonomous_simulation: AutonomousSimulationResult | None = None
    previous_state: ExecutiveState | None = None


@dataclass(frozen=True)
class ExecutiveBrainEvent:
    """Auditable executive brain event."""

    mode: ExecutiveMode
    intent: ExecutiveIntent
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class ExecutiveBrainResult:
    """Final output from the offline Executive Decision Brain."""

    state: ExecutiveState
    decision: ExecutiveDecision
    events: tuple[ExecutiveBrainEvent, ...]
    recommendation: str


__all__ = [
    "ExecutiveBrainEvent",
    "ExecutiveBrainInput",
    "ExecutiveBrainResult",
    "ExecutiveDecision",
    "ExecutiveIntent",
    "ExecutiveMode",
    "ExecutiveRiskAppetite",
    "ExecutiveState",
]
