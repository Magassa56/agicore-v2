"""Models for the offline hierarchical supervisor system."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .adaptive_policy_memory_models import AdaptivePolicyMemory
from .context_scoring_models import ContextScoringResult
from .multi_agent_models import AgentCoordinationResult, TradingAgentRole
from .paper_execution_models import PaperExecutionResult
from .reward_models import RewardEvaluationResult
from .safe_rl_models import SafeRLExperimentResult
from .scenario_replay_models import ReplayArenaResult
from .semi_auto_decision_models import SemiAutoDecisionResult


class SupervisorRole(StrEnum):
    """Specialized supervisors above multi-agent coordination."""

    CHIEF_SUPERVISOR = "CHIEF_SUPERVISOR"
    RISK_SUPREME_CONTROLLER = "RISK_SUPREME_CONTROLLER"
    EMERGENCY_HALT_SUPERVISOR = "EMERGENCY_HALT_SUPERVISOR"
    CONFLICT_RESOLUTION_ENGINE = "CONFLICT_RESOLUTION_ENGINE"
    AGENT_TRUST_MONITOR = "AGENT_TRUST_MONITOR"
    EXECUTION_FINAL_APPROVER = "EXECUTION_FINAL_APPROVER"


class SupervisorDecision(StrEnum):
    """Final hierarchical supervisor decisions."""

    APPROVE_SYSTEM_DECISION = "APPROVE_SYSTEM_DECISION"
    APPROVE_WITH_REDUCED_RISK = "APPROVE_WITH_REDUCED_RISK"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    OVERRIDE_TO_BLOCK = "OVERRIDE_TO_BLOCK"
    OVERRIDE_TO_STOP_SESSION = "OVERRIDE_TO_STOP_SESSION"
    EMERGENCY_HALT = "EMERGENCY_HALT"
    NO_ACTION = "NO_ACTION"


class SupervisorOverride(StrEnum):
    """Safety overrides applied by the hierarchy."""

    NONE = "NONE"
    BLOCK_DANGEROUS_CONSENSUS = "BLOCK_DANGEROUS_CONSENSUS"
    BLOCK_SAFE_RL = "BLOCK_SAFE_RL"
    BLOCK_RISK_AGENT = "BLOCK_RISK_AGENT"
    STOP_SESSION = "STOP_SESSION"
    EMERGENCY_HALT = "EMERGENCY_HALT"
    REDUCE_RISK_CONFLICT = "REDUCE_RISK_CONFLICT"
    REQUIRE_REVIEW_LOW_CONFIDENCE = "REQUIRE_REVIEW_LOW_CONFIDENCE"
    BLOCK_EXECUTION_REJECTED = "BLOCK_EXECUTION_REJECTED"


@dataclass(frozen=True)
class AgentReliabilityScore:
    """Reliability estimate for one coordinated agent."""

    role: TradingAgentRole
    reliability_score: int
    votes_count: int
    coherent_votes: int
    blocking_votes: int
    risk_notes_count: int
    trusted: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class SupervisorInput:
    """Inputs consumed by the offline hierarchical supervisor."""

    coordination_result: AgentCoordinationResult | None = None
    safe_rl_result: SafeRLExperimentResult | None = None
    context_score: ContextScoringResult | None = None
    semi_auto_decision: SemiAutoDecisionResult | None = None
    paper_execution: PaperExecutionResult | None = None
    reward_evaluation: RewardEvaluationResult | None = None
    policy_memory: AdaptivePolicyMemory | None = None
    arena_result: ReplayArenaResult | None = None
    prior_reliability: tuple[AgentReliabilityScore, ...] = ()


@dataclass(frozen=True)
class SupervisorEvent:
    """One auditable supervisor decision event."""

    role: SupervisorRole
    decision: SupervisorDecision
    override: SupervisorOverride
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class SupervisorResult:
    """Final output from the hierarchical supervisor system."""

    decision: SupervisorDecision
    final_executable: bool
    applied_overrides: tuple[SupervisorOverride, ...]
    reliability_scores: tuple[AgentReliabilityScore, ...]
    trusted_agents: tuple[TradingAgentRole, ...]
    agents_to_watch: tuple[TradingAgentRole, ...]
    conflicts_detected: tuple[str, ...]
    critical_risks: tuple[str, ...]
    events: tuple[SupervisorEvent, ...]
    recommendation: str


__all__ = [
    "AgentReliabilityScore",
    "SupervisorDecision",
    "SupervisorEvent",
    "SupervisorInput",
    "SupervisorOverride",
    "SupervisorResult",
    "SupervisorRole",
]
