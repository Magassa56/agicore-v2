"""Unit tests for the offline Executive Decision Brain."""
from __future__ import annotations

from agicore.trading.adaptive_policy_memory_models import (
    AdaptivePolicyMemory,
    PolicyMemoryEntry,
    PolicyMemoryRecommendation,
)
from agicore.trading.context_scoring_models import ContextScoreBreakdown, ContextScoringResult, TradeContextDecision
from agicore.trading.executive_brain import (
    decide_executive_action,
    evaluate_executive_state,
    render_executive_brain_markdown,
    update_executive_state,
)
from agicore.trading.executive_brain_models import (
    ExecutiveIntent,
    ExecutiveMode,
    ExecutiveRiskAppetite,
)
from agicore.trading.hierarchical_supervisor_models import (
    SupervisorDecision,
    SupervisorOverride,
    SupervisorResult,
)
from agicore.trading.meta_strategy_models import MetaStrategyDecision, MetaStrategySelectionResult
from agicore.trading.multi_agent_models import AgentConsensusStatus, AgentCoordinationResult, AgentVote
from agicore.trading.reward_models import RewardBreakdown, RewardComponent, RewardEvaluationResult, RewardLabel
from agicore.trading.safe_rl_models import SafeRLExperimentResult, SafeRLStatus


def _context(decision: TradeContextDecision = TradeContextDecision.TRADE_ALLOWED, score: int = 80) -> ContextScoringResult:
    return ContextScoringResult(
        global_score=score,
        decision=decision,
        breakdown=ContextScoreBreakdown(score, score, score, score, score, score, score),
        favorable_factors=(),
        risk_factors=(),
        recommendations=(),
        strategy_regime_notes=(),
    )


def _supervisor(decision: SupervisorDecision = SupervisorDecision.APPROVE_SYSTEM_DECISION, executable: bool = True) -> SupervisorResult:
    return SupervisorResult(
        decision=decision,
        final_executable=executable,
        applied_overrides=(SupervisorOverride.NONE,),
        reliability_scores=(),
        trusted_agents=(),
        agents_to_watch=(),
        conflicts_detected=(),
        critical_risks=(),
        events=(),
        recommendation="supervisor",
    )


def _safe(status: SafeRLStatus = SafeRLStatus.SAFE) -> SafeRLExperimentResult:
    return SafeRLExperimentResult(
        status=status,
        validations=(),
        active_guardrails=(),
        risks_detected=(),
        allowed_experiments=(),
        blocked_experiments=(),
        recommendations=(),
        safety_summary="safe",
    )


def _reward(label: RewardLabel = RewardLabel.GOOD_DECISION, normalized: int = 75, total: int = 20) -> RewardEvaluationResult:
    c = RewardComponent("x", 0, "x")
    return RewardEvaluationResult(
        total_reward=total,
        normalized_reward=normalized,
        reward_label=label,
        breakdown=RewardBreakdown(c, c, c, c, c, c, c, c, c, c, c),
        learning_notes=(),
        improvement_actions=(),
    )


def _memory(confidence: int = 80, dangerous: float = 0.0) -> AdaptivePolicyMemory:
    return AdaptivePolicyMemory(
        entries={
            "BALANCED": PolicyMemoryEntry(
                policy_name="BALANCED",
                total_evaluations=4,
                average_reward=20,
                average_context_score=82,
                dangerous_decision_rate=dangerous,
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


def _coordination(score: int = 80, disagreements: tuple[str, ...] = ()) -> AgentCoordinationResult:
    return AgentCoordinationResult(
        final_vote=AgentVote.APPROVE,
        consensus_status=AgentConsensusStatus.CONSENSUS_APPROVE,
        consensus_score=score,
        votes=(),
        disagreements=disagreements,
        blocking_agents=(),
        risks_detected=(),
        recommendation="coordination",
    )


def _meta(decision: MetaStrategyDecision = MetaStrategyDecision.SELECT_POLICY) -> MetaStrategySelectionResult:
    return MetaStrategySelectionResult(
        selected_policy_name="BALANCED",
        decision=decision,
        confidence_score=80,
        ranked_candidates=(),
        reasons=(),
        risk_notes=(),
        required_manual_review=False,
        recommendation="meta",
    )


def test_evaluate_executive_state_pauses_on_supervisor_block() -> None:
    state = evaluate_executive_state(
        supervisor_result=_supervisor(SupervisorDecision.OVERRIDE_TO_BLOCK, executable=False),
        context_score=_context(),
    )

    assert state.mode == ExecutiveMode.PAUSED
    assert state.intent == ExecutiveIntent.SESSION_STOP
    assert state.risk_appetite == ExecutiveRiskAppetite.NONE


def test_evaluate_executive_state_survival_on_safe_rl_blocked() -> None:
    state = evaluate_executive_state(
        supervisor_result=_supervisor(),
        safe_rl_result=_safe(SafeRLStatus.BLOCKED),
        context_score=_context(),
    )

    assert state.mode == ExecutiveMode.SURVIVAL
    assert state.intent == ExecutiveIntent.CAPITAL_PRESERVATION


def test_evaluate_executive_state_defensive_on_high_risk_context() -> None:
    state = evaluate_executive_state(
        supervisor_result=_supervisor(),
        context_score=_context(TradeContextDecision.HIGH_RISK_CONTEXT, 45),
    )

    assert state.mode == ExecutiveMode.DEFENSIVE
    assert state.intent == ExecutiveIntent.RISK_REDUCTION
    assert state.risk_appetite == ExecutiveRiskAppetite.LOW


def test_evaluate_executive_state_recovery_on_negative_reward() -> None:
    state = evaluate_executive_state(
        supervisor_result=_supervisor(),
        context_score=_context(),
        reward_evaluation=_reward(RewardLabel.BAD_DECISION, 35, -20),
    )

    assert state.mode == ExecutiveMode.RECOVERY
    assert state.intent == ExecutiveIntent.LEARNING_ONLY


def test_evaluate_executive_state_opportunity_on_strong_context() -> None:
    state = evaluate_executive_state(
        supervisor_result=_supervisor(),
        context_score=_context(TradeContextDecision.STRONG_TRADE_ALLOWED, 90),
        safe_rl_result=_safe(),
        reward_evaluation=_reward(RewardLabel.GOOD_DECISION, 80, 30),
        policy_memory=_memory(),
    )

    assert state.mode == ExecutiveMode.OPPORTUNITY
    assert state.intent == ExecutiveIntent.CONTROLLED_GROWTH
    assert state.risk_appetite == ExecutiveRiskAppetite.ELEVATED


def test_decide_executive_action_reduced_risk_for_defensive() -> None:
    state = evaluate_executive_state(
        context_score=_context(TradeContextDecision.REDUCE_RISK, 60),
        safe_rl_result=_safe(SafeRLStatus.WARNING),
    )

    decision = decide_executive_action(state)

    assert decision.allow_execution is True
    assert decision.allow_reduced_risk_only is True
    assert decision.require_human_review is True


def test_update_executive_state_uses_previous_survival_for_recovery() -> None:
    previous = evaluate_executive_state(safe_rl_result=_safe(SafeRLStatus.BLOCKED))

    result = update_executive_state(
        previous_state=previous,
        supervisor_result=_supervisor(),
        safe_rl_result=_safe(),
        context_score=_context(),
    )

    assert result.state.mode == ExecutiveMode.RECOVERY
    assert result.decision.allow_execution is False


def test_evaluate_executive_state_pauses_on_no_trade_or_meta_block() -> None:
    no_trade = evaluate_executive_state(context_score=_context(TradeContextDecision.NO_TRADE, 20))
    meta_block = evaluate_executive_state(
        context_score=_context(),
        meta_strategy=_meta(MetaStrategyDecision.BLOCK_ALL_POLICIES),
    )

    assert no_trade.mode == ExecutiveMode.PAUSED
    assert meta_block.mode == ExecutiveMode.PAUSED


def test_update_executive_state_returns_result_and_events() -> None:
    result = update_executive_state(
        supervisor_result=_supervisor(),
        agent_coordination=_coordination(),
        context_score=_context(),
        safe_rl_result=_safe(),
        reward_evaluation=_reward(),
        policy_memory=_memory(),
    )

    assert result.state.mode in {ExecutiveMode.NORMAL, ExecutiveMode.OPPORTUNITY}
    assert result.events
    assert result.recommendation


def test_render_executive_brain_markdown_contains_required_sections() -> None:
    result = update_executive_state(
        supervisor_result=_supervisor(),
        context_score=_context(),
        safe_rl_result=_safe(),
        reward_evaluation=_reward(),
        policy_memory=_memory(),
    )

    markdown = render_executive_brain_markdown(result)

    assert "# Executive Decision Brain" in markdown
    assert "## Mode executif" in markdown
    assert "## Intention strategique" in markdown
    assert "## Appetit au risque" in markdown
    assert "## Decision executive" in markdown
    assert "## Raisons" in markdown
    assert "## Contraintes actives" in markdown
    assert "## Objectif de session" in markdown
    assert "## Recommandation AGIcore" in markdown
    assert "no broker" in markdown
