"""Unit tests for the offline hierarchical supervisor system."""
from __future__ import annotations

from agicore.trading.context_scoring_models import ContextScoreBreakdown, ContextScoringResult, TradeContextDecision
from agicore.trading.hierarchical_supervisor import (
    apply_supervisor_override,
    compute_agent_reliability,
    evaluate_supervisor_decision,
    render_supervisor_markdown,
)
from agicore.trading.hierarchical_supervisor_models import (
    SupervisorDecision,
    SupervisorInput,
    SupervisorOverride,
)
from agicore.trading.multi_agent_models import (
    AgentConfidence,
    AgentConsensusStatus,
    AgentCoordinationEvent,
    AgentCoordinationResult,
    AgentVote,
    TradingAgentRole,
)
from agicore.trading.reward_models import RewardBreakdown, RewardComponent, RewardEvaluationResult, RewardLabel
from agicore.trading.safe_rl_models import SafeRLExperimentResult, SafeRLStatus
from agicore.trading.semi_auto_decision_models import SemiAutoAction, SemiAutoDecision, SemiAutoDecisionResult


def _coordination(
    vote: AgentVote = AgentVote.APPROVE,
    *,
    score: int = 85,
    disagreements: tuple[str, ...] = (),
    blockers: tuple[TradingAgentRole, ...] = (),
) -> AgentCoordinationResult:
    status = {
        AgentVote.APPROVE: AgentConsensusStatus.CONSENSUS_APPROVE,
        AgentVote.APPROVE_REDUCED_RISK: AgentConsensusStatus.CONSENSUS_REDUCED_RISK,
        AgentVote.REQUIRE_REVIEW: AgentConsensusStatus.CONSENSUS_REVIEW,
        AgentVote.BLOCK: AgentConsensusStatus.CONSENSUS_BLOCK,
        AgentVote.STOP_SESSION: AgentConsensusStatus.CONSENSUS_STOP_SESSION,
        AgentVote.NO_OPINION: AgentConsensusStatus.NO_CONSENSUS,
    }[vote]
    votes = (
        AgentCoordinationEvent(TradingAgentRole.MARKET_ANALYST, AgentVote.APPROVE, AgentConfidence.HIGH, 2, ("ok",), ()),
        AgentCoordinationEvent(TradingAgentRole.RISK_GUARDIAN, vote, AgentConfidence.HIGH, 4, ("risk",), ("risk note",) if vote in {AgentVote.BLOCK, AgentVote.STOP_SESSION} else ()),
    )
    return AgentCoordinationResult(
        final_vote=vote,
        consensus_status=status,
        consensus_score=score,
        votes=votes,
        disagreements=disagreements,
        blocking_agents=blockers,
        risks_detected=("coordination risk",) if blockers else (),
        recommendation="coordination",
    )


def _safe(status: SafeRLStatus = SafeRLStatus.SAFE) -> SafeRLExperimentResult:
    return SafeRLExperimentResult(
        status=status,
        validations=(),
        active_guardrails=(),
        risks_detected=("safe blocked",) if status == SafeRLStatus.BLOCKED else (),
        allowed_experiments=(),
        blocked_experiments=(),
        recommendations=(),
        safety_summary="safe summary",
    )


def _context(decision: TradeContextDecision = TradeContextDecision.TRADE_ALLOWED) -> ContextScoringResult:
    return ContextScoringResult(
        global_score=80,
        decision=decision,
        breakdown=ContextScoreBreakdown(80, 80, 80, 80, 80, 80, 80),
        favorable_factors=(),
        risk_factors=(),
        recommendations=(),
        strategy_regime_notes=(),
    )


def _semi(decision: SemiAutoDecision = SemiAutoDecision.APPROVE_TRADE) -> SemiAutoDecisionResult:
    return SemiAutoDecisionResult(
        decision=decision,
        action=SemiAutoAction.PREPARE_ORDER_PREVIEW,
        context_score=80,
        approval_reasons=(),
        blocking_reasons=("semi block",) if decision == SemiAutoDecision.BLOCK_TRADE else (),
        detected_risks=(),
        manual_confirmation_conditions=(),
        trader_message="message",
    )


def _reward(label: RewardLabel, normalized: int) -> RewardEvaluationResult:
    c = RewardComponent("x", 0, "x")
    return RewardEvaluationResult(
        total_reward=0,
        normalized_reward=normalized,
        reward_label=label,
        breakdown=RewardBreakdown(c, c, c, c, c, c, c, c, c, c, c),
        learning_notes=(),
        improvement_actions=("reward risk",),
    )


def test_evaluate_supervisor_blocks_when_safe_rl_blocked() -> None:
    result = evaluate_supervisor_decision(
        SupervisorInput(
            coordination_result=_coordination(),
            safe_rl_result=_safe(SafeRLStatus.BLOCKED),
        )
    )

    assert result.decision == SupervisorDecision.OVERRIDE_TO_BLOCK
    assert SupervisorOverride.BLOCK_SAFE_RL in result.applied_overrides
    assert result.final_executable is False


def test_evaluate_supervisor_blocks_risk_guardian_block_vote() -> None:
    result = evaluate_supervisor_decision(
        coordination_result=_coordination(
            AgentVote.BLOCK,
            blockers=(TradingAgentRole.RISK_GUARDIAN,),
        ),
        safe_rl_result=_safe(),
    )

    assert result.decision == SupervisorDecision.OVERRIDE_TO_BLOCK
    assert SupervisorOverride.BLOCK_RISK_AGENT in result.applied_overrides


def test_evaluate_supervisor_stops_session_on_emergency_signal() -> None:
    result = evaluate_supervisor_decision(
        coordination_result=_coordination(AgentVote.STOP_SESSION),
        semi_auto_decision=_semi(SemiAutoDecision.STOP_SESSION),
        safe_rl_result=_safe(),
    )

    assert result.decision == SupervisorDecision.OVERRIDE_TO_STOP_SESSION
    assert SupervisorOverride.STOP_SESSION in result.applied_overrides
    assert result.final_executable is False


def test_evaluate_supervisor_reduces_risk_on_conflict() -> None:
    result = evaluate_supervisor_decision(
        coordination_result=_coordination(
            AgentVote.APPROVE,
            score=55,
            disagreements=("approve conflicts with review",),
        ),
        safe_rl_result=_safe(),
    )

    assert result.decision == SupervisorDecision.APPROVE_WITH_REDUCED_RISK
    assert SupervisorOverride.REDUCE_RISK_CONFLICT in result.applied_overrides
    assert result.final_executable is True


def test_compute_agent_reliability_marks_weak_agent_to_watch() -> None:
    votes = (
        AgentCoordinationEvent(
            TradingAgentRole.POLICY_SELECTOR,
            AgentVote.APPROVE,
            AgentConfidence.LOW,
            1,
            (),
            ("risk1", "risk2", "risk3", "risk4"),
        ),
    )

    scores = compute_agent_reliability(votes, coordination_result=_coordination(AgentVote.BLOCK))
    policy_score = next(score for score in scores if score.role == TradingAgentRole.POLICY_SELECTOR)

    assert policy_score.trusted is False
    assert policy_score.reliability_score < 60


def test_apply_supervisor_override_prioritizes_emergency_halt() -> None:
    decision = apply_supervisor_override(
        SupervisorDecision.APPROVE_SYSTEM_DECISION,
        (SupervisorOverride.REDUCE_RISK_CONFLICT, SupervisorOverride.EMERGENCY_HALT),
    )

    assert decision == SupervisorDecision.EMERGENCY_HALT


def test_evaluate_supervisor_approves_clean_decision() -> None:
    result = evaluate_supervisor_decision(
        coordination_result=_coordination(),
        safe_rl_result=_safe(),
        context_score=_context(),
    )

    assert result.decision == SupervisorDecision.APPROVE_SYSTEM_DECISION
    assert result.final_executable is True
    assert result.applied_overrides == (SupervisorOverride.NONE,)


def test_evaluate_supervisor_requires_review_on_low_consensus() -> None:
    result = evaluate_supervisor_decision(
        coordination_result=_coordination(AgentVote.REQUIRE_REVIEW, score=40),
        safe_rl_result=_safe(),
    )

    assert result.decision == SupervisorDecision.REQUIRE_HUMAN_REVIEW
    assert SupervisorOverride.REQUIRE_REVIEW_LOW_CONFIDENCE in result.applied_overrides


def test_evaluate_supervisor_blocks_no_trade_context_and_dangerous_reward() -> None:
    result = evaluate_supervisor_decision(
        coordination_result=_coordination(),
        context_score=_context(TradeContextDecision.NO_TRADE),
        reward_evaluation=_reward(RewardLabel.DANGEROUS_DECISION, 20),
        safe_rl_result=_safe(),
    )

    assert result.decision == SupervisorDecision.OVERRIDE_TO_BLOCK
    assert SupervisorOverride.BLOCK_DANGEROUS_CONSENSUS in result.applied_overrides


def test_render_supervisor_markdown_contains_required_sections() -> None:
    result = evaluate_supervisor_decision(
        coordination_result=_coordination(),
        safe_rl_result=_safe(),
        context_score=_context(),
    )

    markdown = render_supervisor_markdown(result)

    assert "# Hierarchical Supervisor System" in markdown
    assert "## Decision superviseur" in markdown
    assert "## Overrides appliques" in markdown
    assert "## Agents fiables / agents a surveiller" in markdown
    assert "## Conflits detectes" in markdown
    assert "## Risques critiques" in markdown
    assert "## Decision finale executable" in markdown
    assert "## Recommandation AGIcore" in markdown
    assert "no broker" in markdown
