"""Unit tests for offline multi-agent trading coordination."""
from __future__ import annotations

from agicore.trading.adaptive_policy_memory_models import (
    AdaptivePolicyMemory,
    PolicyMemoryEntry,
    PolicyMemoryRecommendation,
)
from agicore.trading.context_scoring_models import ContextScoreBreakdown, ContextScoringResult, TradeContextDecision
from agicore.trading.market_regime_models import (
    MarketRegime,
    MarketRegimeAnalysis,
    RegimeStrength,
    SessionCondition,
    VolatilityRegime,
)
from agicore.trading.meta_strategy_models import MetaStrategyDecision, MetaStrategySelectionResult
from agicore.trading.multi_agent_coordination import (
    build_agent_vote,
    compute_agent_consensus,
    coordinate_trading_agents,
    render_agent_coordination_markdown,
)
from agicore.trading.multi_agent_models import (
    AgentConfidence,
    AgentConsensusStatus,
    AgentCoordinationEvent,
    AgentCoordinationInput,
    AgentVote,
    TradingAgentRole,
)
from agicore.trading.reward_models import RewardBreakdown, RewardComponent, RewardEvaluationResult, RewardLabel
from agicore.trading.safe_rl_models import SafeRLExperimentResult, SafeRLStatus
from agicore.trading.semi_auto_decision_models import SemiAutoAction, SemiAutoDecision, SemiAutoDecisionResult


def _context(decision: TradeContextDecision = TradeContextDecision.TRADE_ALLOWED, score: int = 82) -> ContextScoringResult:
    return ContextScoringResult(
        global_score=score,
        decision=decision,
        breakdown=ContextScoreBreakdown(score, score, score, score, score, score, score),
        favorable_factors=(),
        risk_factors=(),
        recommendations=(),
        strategy_regime_notes=(),
    )


def _market(*, dangerous: bool = False) -> MarketRegimeAnalysis:
    return MarketRegimeAnalysis(
        primary_regime=MarketRegime.NEWS_RISK if dangerous else MarketRegime.TRENDING_UP,
        confidence=80,
        strength=RegimeStrength.STRONG,
        volatility=VolatilityRegime.EXTREME if dangerous else VolatilityRegime.NORMAL,
        session_condition=SessionCondition.DANGEROUS if dangerous else SessionCondition.FAVORABLE,
        context_quality_score=20 if dangerous else 85,
        favorable_for_pullback_strategy=not dangerous,
        dangerous_market=dangerous,
        detected_regimes=(MarketRegime.NEWS_RISK if dangerous else MarketRegime.TRENDING_UP,),
        warnings=(),
        recommendations=(),
    )


def _semi(decision: SemiAutoDecision = SemiAutoDecision.APPROVE_TRADE) -> SemiAutoDecisionResult:
    return SemiAutoDecisionResult(
        decision=decision,
        action=SemiAutoAction.PREPARE_ORDER_PREVIEW,
        context_score=80,
        approval_reasons=("ok",),
        blocking_reasons=("blocked",) if decision == SemiAutoDecision.BLOCK_TRADE else (),
        detected_risks=(),
        manual_confirmation_conditions=(),
        trader_message="message",
    )


def _meta(decision: MetaStrategyDecision = MetaStrategyDecision.SELECT_POLICY) -> MetaStrategySelectionResult:
    return MetaStrategySelectionResult(
        selected_policy_name="BALANCED",
        decision=decision,
        confidence_score=80,
        ranked_candidates=(),
        reasons=(),
        risk_notes=("policy risk",) if decision == MetaStrategyDecision.REQUIRE_REVIEW else (),
        required_manual_review=decision == MetaStrategyDecision.REQUIRE_REVIEW,
        recommendation="policy recommendation",
    )


def _safe(status: SafeRLStatus = SafeRLStatus.SAFE) -> SafeRLExperimentResult:
    return SafeRLExperimentResult(
        status=status,
        validations=(),
        active_guardrails=(),
        risks_detected=("safe rl blocked",) if status == SafeRLStatus.BLOCKED else (),
        allowed_experiments=("offline",),
        blocked_experiments=(),
        recommendations=(),
        safety_summary="safe summary",
    )


def _reward(label: RewardLabel = RewardLabel.GOOD_DECISION, normalized: int = 75) -> RewardEvaluationResult:
    c = RewardComponent("x", 0, "x")
    return RewardEvaluationResult(
        total_reward=20,
        normalized_reward=normalized,
        reward_label=label,
        breakdown=RewardBreakdown(c, c, c, c, c, c, c, c, c, c, c),
        learning_notes=(),
        improvement_actions=("improve",) if normalized < 50 else (),
    )


def _memory(confidence: int = 80) -> AdaptivePolicyMemory:
    return AdaptivePolicyMemory(
        entries={
            "BALANCED": PolicyMemoryEntry(
                policy_name="BALANCED",
                total_evaluations=5,
                average_reward=20,
                average_context_score=80,
                dangerous_decision_rate=0.0,
                blocked_trade_rate=0.2,
                accepted_trade_rate=0.7,
                reduced_risk_rate=0.1,
                confidence_score=confidence,
                recommendation=PolicyMemoryRecommendation.KEEP_POLICY,
                best_contexts=(),
                worst_contexts=(),
            )
        }
    )


def test_build_agent_vote_market_blocks_dangerous_market() -> None:
    vote = build_agent_vote(TradingAgentRole.MARKET_ANALYST, market_regime=_market(dangerous=True))

    assert vote.role == TradingAgentRole.MARKET_ANALYST
    assert vote.vote == AgentVote.BLOCK
    assert vote.confidence == AgentConfidence.HIGH


def test_coordinate_trading_agents_blocks_when_safe_rl_blocks() -> None:
    result = coordinate_trading_agents(
        AgentCoordinationInput(
            market_regime=_market(),
            context_score=_context(),
            meta_strategy=_meta(),
            semi_auto_decision=_semi(),
            safe_rl_result=_safe(SafeRLStatus.BLOCKED),
            reward_evaluation=_reward(),
            policy_memory=_memory(),
        )
    )

    assert result.final_vote == AgentVote.BLOCK
    assert result.consensus_status == AgentConsensusStatus.CONSENSUS_BLOCK
    assert TradingAgentRole.SAFE_RL_SUPERVISOR in result.blocking_agents


def test_coordinate_trading_agents_stops_session_when_semi_auto_stops() -> None:
    result = coordinate_trading_agents(
        context_score=_context(),
        semi_auto_decision=_semi(SemiAutoDecision.STOP_SESSION),
        safe_rl_result=_safe(),
    )

    assert result.final_vote == AgentVote.STOP_SESSION
    assert result.consensus_status == AgentConsensusStatus.CONSENSUS_STOP_SESSION


def test_coordinate_trading_agents_reduces_risk_on_mixed_review_signals() -> None:
    result = coordinate_trading_agents(
        market_regime=_market(),
        context_score=_context(TradeContextDecision.REDUCE_RISK, 60),
        meta_strategy=_meta(MetaStrategyDecision.SELECT_REDUCED_RISK_POLICY),
        semi_auto_decision=_semi(SemiAutoDecision.APPROVE_REDUCED_RISK),
        safe_rl_result=_safe(SafeRLStatus.WARNING),
        reward_evaluation=_reward(RewardLabel.ACCEPTABLE, 55),
        policy_memory=_memory(),
    )

    assert result.final_vote == AgentVote.APPROVE_REDUCED_RISK
    assert result.consensus_status == AgentConsensusStatus.CONSENSUS_REDUCED_RISK
    assert result.consensus_score > 0


def test_compute_agent_consensus_detects_disagreements() -> None:
    result = compute_agent_consensus(
        (
            AgentCoordinationEvent(TradingAgentRole.MARKET_ANALYST, AgentVote.APPROVE, AgentConfidence.HIGH, 2, (), ()),
            AgentCoordinationEvent(TradingAgentRole.RISK_GUARDIAN, AgentVote.BLOCK, AgentConfidence.HIGH, 4, (), ("risk",)),
        )
    )

    assert result.final_vote == AgentVote.BLOCK
    assert result.disagreements
    assert result.risks_detected == ("risk",)


def test_coordinate_trading_agents_can_approve_clean_context() -> None:
    result = coordinate_trading_agents(
        market_regime=_market(),
        context_score=_context(),
        meta_strategy=_meta(),
        semi_auto_decision=_semi(),
        safe_rl_result=_safe(),
        reward_evaluation=_reward(),
        policy_memory=_memory(),
    )

    assert result.final_vote == AgentVote.APPROVE
    assert result.consensus_status == AgentConsensusStatus.CONSENSUS_APPROVE


def test_render_agent_coordination_markdown_contains_required_sections() -> None:
    result = coordinate_trading_agents(
        market_regime=_market(),
        context_score=_context(),
        meta_strategy=_meta(),
        semi_auto_decision=_semi(),
        safe_rl_result=_safe(),
        reward_evaluation=_reward(),
        policy_memory=_memory(),
    )

    markdown = render_agent_coordination_markdown(result)

    assert "# Multi-Agent Coordination Layer" in markdown
    assert "## Decision collective" in markdown
    assert "## Votes par agent" in markdown
    assert "## Consensus" in markdown
    assert "## Desaccords" in markdown
    assert "## Agents bloquants" in markdown
    assert "## Risques detectes" in markdown
    assert "## Recommandation finale AGIcore" in markdown
    assert "no broker" in markdown
