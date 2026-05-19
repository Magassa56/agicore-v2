"""Offline policy evaluation sandbox for AGIcore Trading."""
from __future__ import annotations

from dataclasses import replace
from statistics import mean

from .behavior_models import BehaviorAnalysisResult
from .context_scoring_models import ContextScoringResult, TradeContextDecision
from .market_regime_models import MarketRegimeAnalysis
from .paper_execution_loop import run_paper_execution_loop
from .paper_execution_models import PaperExecutionDecision, PaperExecutionLoopConfig, PaperExecutionRequest
from .paper_trading_adapter import MockPaperTradingAdapter
from .paper_trading_models import PaperOrderRequest, PaperOrderSide
from .policy_evaluation_models import (
    PolicyComparisonResult,
    PolicyEvaluationResult,
    PolicyEvaluationScenario,
    PolicyRule,
    TradingPolicy,
)
from .reward_function import evaluate_trading_reward
from .reward_models import RewardEvaluationResult, RewardLabel
from .semi_auto_decision_models import SemiAutoAction, SemiAutoDecision, SemiAutoDecisionResult
from .strategy_dna_models import StrategyDNA, TradeDirection


def evaluate_policy(
    policy: TradingPolicy | str,
    scenarios: tuple[PolicyEvaluationScenario, ...] | list[PolicyEvaluationScenario],
) -> PolicyEvaluationResult:
    """Evaluate one deterministic offline trading policy over scenarios."""
    trading_policy = _policy(policy)
    rule = _rule_for_policy(trading_policy)
    scenario_tuple = tuple(scenarios)
    semi_results: list[SemiAutoDecisionResult] = []
    paper_results = []
    reward_results: list[RewardEvaluationResult] = []
    risk_notes: list[str] = []

    for scenario in scenario_tuple:
        semi = _build_policy_decision(rule, scenario, risk_notes)
        order_request = _order_for_policy(rule, semi, scenario.order_request)
        config = PaperExecutionLoopConfig(
            allow_high_risk_override=rule.allow_high_risk_override,
        )
        paper = run_paper_execution_loop(
            PaperExecutionRequest(
                semi_auto_decision=semi,
                context_score=scenario.context_score,
                order_request=order_request,
                strategy_dna=scenario.strategy_dna,
                config=config,
            ),
            adapter=MockPaperTradingAdapter(),
        )
        reward = evaluate_trading_reward(
            paper_execution_result=paper,
            semi_auto_decision=semi,
            context_score=scenario.context_score,
            session_replay_result=scenario.session_replay_result,
            behavior_result=scenario.behavior_result,
            memory_profile=scenario.memory_profile,
            market_regime=scenario.market_regime,
            strategy_dna=scenario.strategy_dna,
        )
        semi_results.append(semi)
        paper_results.append(paper)
        reward_results.append(reward)

    accepted = sum(1 for result in paper_results if result.decision == PaperExecutionDecision.PAPER_ORDER_FILLED)
    blocked = sum(1 for decision in semi_results if decision.decision in _blocking_decisions())
    reduced = sum(1 for decision in semi_results if decision.decision == SemiAutoDecision.APPROVE_REDUCED_RISK)
    dangerous = sum(
        1
        for scenario, paper, reward, semi in zip(scenario_tuple, paper_results, reward_results, semi_results, strict=True)
        if _dangerous_decision(scenario, paper, reward, semi)
    )
    total_reward = sum(reward.total_reward for reward in reward_results)
    normalized = _clamp(round(mean(reward.normalized_reward for reward in reward_results))) if reward_results else 50
    avg_context = mean(scenario.context_score.global_score for scenario in scenario_tuple) if scenario_tuple else 0.0
    avg_reward = mean(reward.total_reward for reward in reward_results) if reward_results else 0.0

    return PolicyEvaluationResult(
        policy=trading_policy,
        rule=rule,
        total_reward=total_reward,
        normalized_reward=normalized,
        accepted_trades=accepted,
        blocked_trades=blocked,
        reduced_risk_trades=reduced,
        dangerous_decisions=dangerous,
        average_context_score=round(avg_context, 2),
        average_reward=round(avg_reward, 2),
        best_policy=False,
        best_policy_reason="Policy has not been compared yet.",
        scenario_count=len(scenario_tuple),
        semi_auto_decisions=tuple(semi_results),
        paper_execution_results=tuple(paper_results),
        reward_results=tuple(reward_results),
        risk_notes=tuple(dict.fromkeys(risk_notes)),
    )


def compare_policies(
    scenarios: tuple[PolicyEvaluationScenario, ...] | list[PolicyEvaluationScenario],
    policies: tuple[TradingPolicy | str, ...] | list[TradingPolicy | str] = (
        TradingPolicy.CONSERVATIVE,
        TradingPolicy.BALANCED,
        TradingPolicy.AGGRESSIVE,
        TradingPolicy.LONG_ONLY_STRICT,
        TradingPolicy.NO_TRADE_ON_HIGH_RISK,
    ),
) -> PolicyComparisonResult:
    """Compare multiple deterministic policies on the same offline scenarios."""
    results = tuple(evaluate_policy(policy, scenarios) for policy in policies)
    if not results:
        return PolicyComparisonResult(
            results=(),
            best_policy=None,
            best_policy_reason="No policy was evaluated.",
            recommendation="Provide at least one policy and one scenario.",
            risks_detected=(),
        )

    best = max(results, key=lambda result: (result.normalized_reward, -result.dangerous_decisions, result.accepted_trades))
    reason = (
        f"{best.policy.value} has the best normalized reward "
        f"({best.normalized_reward}/100) with {best.dangerous_decisions} dangerous decision(s)."
    )
    marked_results = tuple(
        replace(
            result,
            best_policy=result.policy == best.policy,
            best_policy_reason=reason if result.policy == best.policy else "Another policy scored higher.",
        )
        for result in results
    )
    risks = tuple(dict.fromkeys(note for result in marked_results for note in result.risk_notes))
    recommendation = _comparison_recommendation(best)
    return PolicyComparisonResult(
        results=marked_results,
        best_policy=best.policy,
        best_policy_reason=reason,
        recommendation=recommendation,
        risks_detected=risks,
    )


def render_policy_comparison_markdown(result: PolicyComparisonResult) -> str:
    """Render an offline policy comparison as Markdown."""
    lines = [
        "# Policy Evaluation Sandbox",
        "",
        "## Resume des politiques",
        "",
        *_summary_lines(result.results),
        "",
        "## Meilleure politique",
        "",
        f"- Policy: {result.best_policy.value if result.best_policy is not None else 'None'}",
        f"- Reason: {result.best_policy_reason}",
        "",
        "## Tableau comparatif",
        "",
        "| Policy | Normalized | Total reward | Accepted | Blocked | Reduced risk | Dangerous | Avg context | Avg reward |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        *_table_lines(result.results),
        "",
        "## Risques detectes",
        "",
        *_bullet_lines(result.risks_detected),
        "",
        "## Recommandation AGIcore",
        "",
        f"- {result.recommendation}",
        "",
        "## Utilisation future pour Offline RL",
        "",
        "- This sandbox compares deterministic policy outputs and reward targets offline.",
        "- No real RL training, broker access, market API call, or real order execution is performed.",
        "",
    ]
    return "\n".join(lines)


def _build_policy_decision(
    rule: PolicyRule,
    scenario: PolicyEvaluationScenario,
    risk_notes: list[str],
) -> SemiAutoDecisionResult:
    context = scenario.context_score
    behavior_classes = _behavior_classes(scenario.behavior_result)
    blocking: list[str] = []
    risks: list[str] = []
    approvals: list[str] = []
    confirmations: list[str] = []

    if context.decision == TradeContextDecision.NO_TRADE:
        blocking.append("Context decision is NO_TRADE.")
    if context.global_score < rule.min_context_score:
        blocking.append(f"Context score {context.global_score} is below policy threshold {rule.min_context_score}.")
    if context.decision == TradeContextDecision.HIGH_RISK_CONTEXT:
        risks.append("Context decision is HIGH_RISK_CONTEXT.")
        if rule.block_high_risk_context:
            blocking.append("Policy blocks HIGH_RISK_CONTEXT.")
    if "REVENGE_TRADING_PROBABLE" in behavior_classes:
        risks.append("Revenge trading behavior detected.")
        risk_notes.append(f"{rule.policy.value}: revenge trading risk detected.")
        if rule.block_revenge_trading:
            blocking.append("Policy blocks revenge trading.")
    if "OVERTRADING" in behavior_classes:
        risks.append("Overtrading behavior detected.")
        risk_notes.append(f"{rule.policy.value}: overtrading risk detected.")
        if rule.block_overtrading:
            blocking.append("Policy blocks overtrading.")
    if scenario.market_regime is not None and scenario.market_regime.dangerous_market:
        risks.append("Market regime is dangerous.")
        risk_notes.append(f"{rule.policy.value}: dangerous market regime detected.")
    if _strategy_incompatible(rule, scenario.order_request, scenario.strategy_dna):
        blocking.append("Policy/StrategyDNA direction is incompatible with requested side.")

    if blocking:
        return SemiAutoDecisionResult(
            decision=SemiAutoDecision.BLOCK_TRADE,
            action=SemiAutoAction.BLOCK_TRADE,
            context_score=context.global_score,
            approval_reasons=(),
            blocking_reasons=tuple(blocking),
            detected_risks=tuple(risks),
            manual_confirmation_conditions=tuple(confirmations),
            trader_message="Policy blocks this offline paper scenario.",
        )

    if context.global_score < rule.reduce_risk_below_score or (
        context.decision == TradeContextDecision.HIGH_RISK_CONTEXT and rule.allow_high_risk_override
    ):
        confirmations.append("Manual review required before using this policy in a real workflow.")
        return SemiAutoDecisionResult(
            decision=SemiAutoDecision.APPROVE_REDUCED_RISK,
            action=SemiAutoAction.REDUCE_SIZE,
            context_score=context.global_score,
            approval_reasons=("Policy allows trade only with reduced simulated size.",),
            blocking_reasons=(),
            detected_risks=tuple(risks),
            manual_confirmation_conditions=tuple(confirmations),
            trader_message="Policy approves reduced-risk paper scenario only.",
        )

    approvals.append("Policy threshold and compatibility checks passed.")
    return SemiAutoDecisionResult(
        decision=SemiAutoDecision.APPROVE_TRADE,
        action=SemiAutoAction.PREPARE_ORDER_PREVIEW,
        context_score=context.global_score,
        approval_reasons=tuple(approvals),
        blocking_reasons=(),
        detected_risks=tuple(risks),
        manual_confirmation_conditions=tuple(confirmations),
        trader_message="Policy approves offline paper scenario.",
    )


def _order_for_policy(
    rule: PolicyRule,
    semi: SemiAutoDecisionResult,
    request: PaperOrderRequest,
) -> PaperOrderRequest:
    if semi.decision != SemiAutoDecision.APPROVE_REDUCED_RISK or not rule.reduce_size_on_caution:
        return request
    return replace(request, quantity=max(0.01, round(request.quantity * 0.5, 8)))


def _rule_for_policy(policy: TradingPolicy) -> PolicyRule:
    if policy == TradingPolicy.CONSERVATIVE:
        return PolicyRule(policy, 75, 90, True, False, True, True, True)
    if policy == TradingPolicy.BALANCED:
        return PolicyRule(policy, 65, 75, True, False, True, True, True)
    if policy == TradingPolicy.AGGRESSIVE:
        return PolicyRule(policy, 50, 65, False, True, True, True, False)
    if policy == TradingPolicy.LONG_ONLY_STRICT:
        return PolicyRule(policy, 70, 80, True, False, True, True, True, long_only=True)
    return PolicyRule(policy, 60, 70, True, False, True, True, True)


def _dangerous_decision(
    scenario: PolicyEvaluationScenario,
    paper: object,
    reward: RewardEvaluationResult,
    semi: SemiAutoDecisionResult,
) -> bool:
    filled = getattr(paper, "decision", None) == PaperExecutionDecision.PAPER_ORDER_FILLED
    dangerous_context = scenario.context_score.decision in {
        TradeContextDecision.NO_TRADE,
        TradeContextDecision.HIGH_RISK_CONTEXT,
    }
    dangerous_market = bool(scenario.market_regime is not None and scenario.market_regime.dangerous_market)
    bad_reward = reward.reward_label == RewardLabel.DANGEROUS_DECISION
    unsafe_approval = semi.decision == SemiAutoDecision.APPROVE_TRADE and (dangerous_context or dangerous_market)
    return bool(bad_reward or (filled and dangerous_context) or unsafe_approval)


def _strategy_incompatible(
    rule: PolicyRule,
    request: PaperOrderRequest,
    strategy: StrategyDNA | None,
) -> bool:
    if rule.long_only and request.side == PaperOrderSide.SELL:
        return True
    if strategy is None:
        return False
    if strategy.allowed_direction == TradeDirection.LONG_ONLY and request.side == PaperOrderSide.SELL:
        return True
    if strategy.allowed_direction == TradeDirection.SHORT_ONLY and request.side == PaperOrderSide.BUY:
        return True
    return False


def _blocking_decisions() -> set[SemiAutoDecision]:
    return {
        SemiAutoDecision.BLOCK_TRADE,
        SemiAutoDecision.STOP_SESSION,
        SemiAutoDecision.REVIEW_ONLY,
    }


def _behavior_classes(behavior: BehaviorAnalysisResult | None) -> set[str]:
    if behavior is None:
        return set()
    return {_value(item) for item in behavior.classifications}


def _comparison_recommendation(best: PolicyEvaluationResult) -> str:
    if best.dangerous_decisions:
        return f"Use {best.policy.value} only for offline analysis; dangerous decisions remain present."
    if best.accepted_trades == 0:
        return f"{best.policy.value} is safest but blocks all trades in this scenario set."
    return f"Prefer {best.policy.value} for this offline scenario set."


def _summary_lines(results: tuple[PolicyEvaluationResult, ...]) -> list[str]:
    if not results:
        return ["- No policies evaluated."]
    return [
        (
            f"- {result.policy.value}: normalized={result.normalized_reward}/100, "
            f"accepted={result.accepted_trades}, blocked={result.blocked_trades}, "
            f"dangerous={result.dangerous_decisions}"
        )
        for result in results
    ]


def _table_lines(results: tuple[PolicyEvaluationResult, ...]) -> list[str]:
    return [
        (
            f"| {result.policy.value} | {result.normalized_reward} | {result.total_reward} | "
            f"{result.accepted_trades} | {result.blocked_trades} | {result.reduced_risk_trades} | "
            f"{result.dangerous_decisions} | {result.average_context_score:.2f} | {result.average_reward:.2f} |"
        )
        for result in results
    ]


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _policy(policy: TradingPolicy | str) -> TradingPolicy:
    return policy if isinstance(policy, TradingPolicy) else TradingPolicy(policy)


def _value(value: object) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "compare_policies",
    "evaluate_policy",
    "render_policy_comparison_markdown",
]
