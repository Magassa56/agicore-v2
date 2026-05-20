"""Models for offline multi-agent trading coordination."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .adaptive_policy_memory_models import AdaptivePolicyMemory
from .context_scoring_models import ContextScoringResult
from .market_regime_models import MarketRegimeAnalysis
from .meta_strategy_models import MetaStrategySelectionResult
from .paper_execution_models import PaperExecutionResult
from .reward_models import RewardEvaluationResult
from .safe_rl_models import SafeRLExperimentResult
from .scenario_replay_models import ReplayArenaResult, ReplayScenarioResult
from .semi_auto_decision_models import SemiAutoDecisionResult


class TradingAgentRole(StrEnum):
    """Specialized offline agents used by the coordination layer."""

    MARKET_ANALYST = "MARKET_ANALYST"
    RISK_GUARDIAN = "RISK_GUARDIAN"
    POLICY_SELECTOR = "POLICY_SELECTOR"
    REWARD_ANALYST = "REWARD_ANALYST"
    SAFE_RL_SUPERVISOR = "SAFE_RL_SUPERVISOR"
    EXECUTION_SUPERVISOR = "EXECUTION_SUPERVISOR"
    MEMORY_CURATOR = "MEMORY_CURATOR"


class AgentVote(StrEnum):
    """Possible votes emitted by specialized trading agents."""

    APPROVE = "APPROVE"
    APPROVE_REDUCED_RISK = "APPROVE_REDUCED_RISK"
    REQUIRE_REVIEW = "REQUIRE_REVIEW"
    BLOCK = "BLOCK"
    STOP_SESSION = "STOP_SESSION"
    NO_OPINION = "NO_OPINION"


class AgentConfidence(StrEnum):
    """Confidence bucket for an agent vote."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AgentConsensusStatus(StrEnum):
    """Final consensus status emitted by the coordination layer."""

    CONSENSUS_APPROVE = "CONSENSUS_APPROVE"
    CONSENSUS_REDUCED_RISK = "CONSENSUS_REDUCED_RISK"
    CONSENSUS_REVIEW = "CONSENSUS_REVIEW"
    CONSENSUS_BLOCK = "CONSENSUS_BLOCK"
    CONSENSUS_STOP_SESSION = "CONSENSUS_STOP_SESSION"
    NO_CONSENSUS = "NO_CONSENSUS"


@dataclass(frozen=True)
class AgentCoordinationEvent:
    """One vote/event emitted by a specialized offline agent."""

    role: TradingAgentRole
    vote: AgentVote
    confidence: AgentConfidence
    weight: int
    reasons: tuple[str, ...]
    risk_notes: tuple[str, ...]
    timestamp: datetime | None = None


@dataclass(frozen=True)
class AgentCoordinationInput:
    """Optional inputs consumed by the offline coordination layer."""

    market_regime: MarketRegimeAnalysis | None = None
    context_score: ContextScoringResult | None = None
    meta_strategy: MetaStrategySelectionResult | None = None
    semi_auto_decision: SemiAutoDecisionResult | None = None
    paper_execution: PaperExecutionResult | None = None
    reward_evaluation: RewardEvaluationResult | None = None
    policy_memory: AdaptivePolicyMemory | None = None
    safe_rl_result: SafeRLExperimentResult | None = None
    scenario_result: ReplayScenarioResult | None = None
    arena_result: ReplayArenaResult | None = None


@dataclass(frozen=True)
class AgentCoordinationResult:
    """Final multi-agent coordination output."""

    final_vote: AgentVote
    consensus_status: AgentConsensusStatus
    consensus_score: int
    votes: tuple[AgentCoordinationEvent, ...]
    disagreements: tuple[str, ...]
    blocking_agents: tuple[TradingAgentRole, ...]
    risks_detected: tuple[str, ...]
    recommendation: str


__all__ = [
    "AgentConfidence",
    "AgentConsensusStatus",
    "AgentCoordinationEvent",
    "AgentCoordinationInput",
    "AgentCoordinationResult",
    "AgentVote",
    "TradingAgentRole",
]
