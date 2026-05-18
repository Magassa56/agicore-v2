"""Offline semi-auto decision assistant for AGIcore Trading."""
from __future__ import annotations

from typing import Any

from .adaptive_memory_models import TraderMemoryProfile
from .behavior_models import BehaviorAnalysisResult
from .context_scoring_models import ContextScoringResult, TradeContextDecision
from .daily_report_models import DailyTradingReport
from .market_regime_models import MarketRegimeAnalysis
from .playbook_models import TraderProfile
from .semi_auto_decision_models import (
    SemiAutoAction,
    SemiAutoDecision,
    SemiAutoDecisionInput,
    SemiAutoDecisionResult,
)
from .session_coach_models import SessionCoachDecision
from .strategy_dna_models import StrategyDNA


def build_semi_auto_decision(
    decision_input: SemiAutoDecisionInput | None = None,
    *,
    context_score: ContextScoringResult | None = None,
    coach_decision: SessionCoachDecision | None = None,
    coach_output: Any | None = None,
    market_regime: MarketRegimeAnalysis | None = None,
    behavior_result: BehaviorAnalysisResult | None = None,
    memory_profile: TraderMemoryProfile | None = None,
    trader_profile: TraderProfile | None = None,
    strategy_dna: StrategyDNA | None = None,
    daily_report: DailyTradingReport | None = None,
) -> SemiAutoDecisionResult:
    """Build an offline assisted decision without placing or routing orders."""
    if decision_input is not None:
        context_score = decision_input.context_score
        coach_decision = decision_input.coach_decision
        coach_output = decision_input.coach_output
        market_regime = decision_input.market_regime
        behavior_result = decision_input.behavior_result
        memory_profile = decision_input.memory_profile
        trader_profile = decision_input.trader_profile
        strategy_dna = decision_input.strategy_dna
        daily_report = decision_input.daily_report
    if context_score is None:
        raise ValueError("context_score is required")

    effective_coach_decision = _effective_coach_decision(coach_decision, coach_output)
    approvals = list(context_score.favorable_factors)
    risks = list(context_score.risk_factors)
    blocks = list(context_score.no_trade_reasons)
    confirmations: list[str] = []

    _collect_context_risks(
        context_score=context_score,
        coach_decision=effective_coach_decision,
        coach_output=coach_output,
        market_regime=market_regime,
        behavior_result=behavior_result,
        memory_profile=memory_profile,
        trader_profile=trader_profile,
        strategy_dna=strategy_dna,
        daily_report=daily_report,
        risks=risks,
        blocks=blocks,
        confirmations=confirmations,
        approvals=approvals,
    )

    decision, action = _choose_decision(
        context_score=context_score,
        coach_decision=effective_coach_decision,
        blocks=tuple(blocks),
        risks=tuple(risks),
        confirmations=tuple(confirmations),
    )

    return SemiAutoDecisionResult(
        decision=decision,
        action=action,
        context_score=context_score.global_score,
        approval_reasons=tuple(dict.fromkeys(approvals)),
        blocking_reasons=tuple(dict.fromkeys(blocks)),
        detected_risks=tuple(dict.fromkeys(risks)),
        manual_confirmation_conditions=tuple(dict.fromkeys(confirmations)),
        trader_message=_trader_message(decision, action, context_score.global_score),
    )


def render_semi_auto_decision_markdown(result: SemiAutoDecisionResult) -> str:
    """Render the semi-auto assisted decision as Markdown."""
    lines = [
        "# Semi-Auto Decision Assistant",
        "",
        "## Decision finale",
        "",
        f"- Decision: {result.decision.value}",
        "",
        "## Action recommandee",
        "",
        f"- Action: {result.action.value}",
        "",
        "## Score contexte",
        "",
        f"- Score: {result.context_score}/100",
        "",
        "## Raisons d'approbation ou blocage",
        "",
        *_combined_reason_lines(result.approval_reasons, result.blocking_reasons),
        "",
        "## Risques detectes",
        "",
        *_bullet_lines(result.detected_risks),
        "",
        "## Conditions de confirmation manuelle",
        "",
        *_bullet_lines(result.manual_confirmation_conditions),
        "",
        "## Message trader clair",
        "",
        result.trader_message,
        "",
    ]
    return "\n".join(lines)


def _collect_context_risks(
    *,
    context_score: ContextScoringResult,
    coach_decision: SessionCoachDecision | None,
    coach_output: Any | None,
    market_regime: MarketRegimeAnalysis | None,
    behavior_result: BehaviorAnalysisResult | None,
    memory_profile: TraderMemoryProfile | None,
    trader_profile: TraderProfile | None,
    strategy_dna: StrategyDNA | None,
    daily_report: DailyTradingReport | None,
    risks: list[str],
    blocks: list[str],
    confirmations: list[str],
    approvals: list[str],
) -> None:
    if context_score.decision == TradeContextDecision.NO_TRADE:
        blocks.append("Context scoring decision is NO_TRADE.")
    if context_score.global_score < 35:
        blocks.append("Context score is very low.")
    if context_score.decision == TradeContextDecision.HIGH_RISK_CONTEXT:
        confirmations.append("High risk context requires manual confirmation.")
    if context_score.decision == TradeContextDecision.REDUCE_RISK:
        confirmations.append("Reduced risk context requires explicit size confirmation.")
    if coach_decision == SessionCoachDecision.STOP_TRADING:
        blocks.append("Session coach recommends STOP_TRADING.")
    elif coach_decision == SessionCoachDecision.TAKE_BREAK:
        risks.append("Session coach recommends TAKE_BREAK.")
        confirmations.append("Confirm break completion before any trade preview.")
    elif coach_decision == SessionCoachDecision.REDUCE_RISK:
        risks.append("Session coach recommends REDUCE_RISK.")
        confirmations.append("Confirm reduced size before preview.")
    elif coach_decision == SessionCoachDecision.REVIEW_REQUIRED:
        risks.append("Session coach requires review.")
        confirmations.append("Complete manual review before approval.")

    if _bool_attr(coach_output, "stop_recommended"):
        blocks.append("Coach output has stop_recommended=True.")
    if _bool_attr(coach_output, "break_recommended"):
        risks.append("Coach output has break_recommended=True.")
        confirmations.append("Manual confirmation required after break recommendation.")
    if _bool_attr(coach_output, "reduce_size"):
        risks.append("Coach output has reduce_size=True.")
        confirmations.append("Reduced size must be confirmed manually.")

    if market_regime is not None:
        if market_regime.dangerous_market:
            risks.append("Market regime is dangerous.")
        if market_regime.favorable_for_pullback_strategy:
            approvals.append("Market regime is compatible with pullback strategy.")
        else:
            confirmations.append("Market regime compatibility must be reviewed manually.")

    if behavior_result is not None:
        classes = {_value(item) for item in behavior_result.classifications}
        if "REVENGE_TRADING_PROBABLE" in classes or behavior_result.scores.emotional_risk_score < 50:
            blocks.append("Emotional or revenge-trading risk is too high.")
        elif behavior_result.scores.emotional_risk_score < 65:
            risks.append("Emotional risk is elevated.")
            confirmations.append("Trader must confirm emotional reset.")
        if "OVERTRADING" in classes:
            risks.append("Overtrading detected by behavior intelligence.")

    if memory_profile is not None and memory_profile.recurring_patterns:
        risks.append("Adaptive memory shows recurring error patterns.")
        confirmations.append("Recurring memory errors require manual confirmation.")
    if memory_profile is not None and memory_profile.recurring_dangerous_hours:
        risks.append("Adaptive memory shows recurring dangerous hours.")

    if daily_report is not None:
        violations = [item for item in daily_report.rule_violations if "No rule violations" not in item]
        if violations:
            blocks.append("Daily report contains playbook/risk violations.")
        if daily_report.emotional_risk_score < 55:
            risks.append("Daily report emotional risk score is weak.")

    if trader_profile is not None and trader_profile.risk_rules.forbidden_hours:
        confirmations.append("Check trader playbook forbidden hours before preview.")
    if strategy_dna is not None:
        approvals.append(f"Strategy DNA loaded: {strategy_dna.name}")


def _choose_decision(
    *,
    context_score: ContextScoringResult,
    coach_decision: SessionCoachDecision | None,
    blocks: tuple[str, ...],
    risks: tuple[str, ...],
    confirmations: tuple[str, ...],
) -> tuple[SemiAutoDecision, SemiAutoAction]:
    if coach_decision == SessionCoachDecision.STOP_TRADING:
        return SemiAutoDecision.STOP_SESSION, SemiAutoAction.RECOMMEND_STOP_SESSION
    if blocks:
        if context_score.global_score < 25:
            return SemiAutoDecision.STOP_SESSION, SemiAutoAction.RECOMMEND_STOP_SESSION
        return SemiAutoDecision.BLOCK_TRADE, SemiAutoAction.BLOCK_TRADE
    if context_score.decision == TradeContextDecision.HIGH_RISK_CONTEXT:
        return SemiAutoDecision.REVIEW_ONLY, SemiAutoAction.REQUIRE_REVIEW
    if context_score.decision == TradeContextDecision.REDUCE_RISK:
        return SemiAutoDecision.APPROVE_REDUCED_RISK, SemiAutoAction.REDUCE_SIZE
    if confirmations or risks:
        if any("memory" in item.lower() for item in confirmations):
            return SemiAutoDecision.REQUIRE_CONFIRMATION, SemiAutoAction.REQUEST_MANUAL_CONFIRMATION
        if context_score.global_score >= 70 and len(risks) <= 2:
            return SemiAutoDecision.APPROVE_REDUCED_RISK, SemiAutoAction.REDUCE_SIZE
        return SemiAutoDecision.REQUIRE_CONFIRMATION, SemiAutoAction.REQUEST_MANUAL_CONFIRMATION
    if (
        context_score.decision == TradeContextDecision.STRONG_TRADE_ALLOWED
        and context_score.breakdown.discipline_score >= 75
        and context_score.breakdown.strategy_regime_compatibility_score >= 75
    ):
        return SemiAutoDecision.APPROVE_TRADE, SemiAutoAction.PREPARE_ORDER_PREVIEW
    if context_score.decision == TradeContextDecision.TRADE_ALLOWED:
        return SemiAutoDecision.REQUIRE_CONFIRMATION, SemiAutoAction.REQUEST_MANUAL_CONFIRMATION
    return SemiAutoDecision.REVIEW_ONLY, SemiAutoAction.NO_ACTION


def _effective_coach_decision(
    explicit: SessionCoachDecision | None,
    coach_output: Any | None,
) -> SessionCoachDecision | None:
    if explicit is not None:
        return explicit
    value = getattr(coach_output, "decision", None)
    if value is None:
        return None
    if isinstance(value, SessionCoachDecision):
        return value
    try:
        return SessionCoachDecision(str(value))
    except ValueError:
        return None


def _trader_message(decision: SemiAutoDecision, action: SemiAutoAction, score: int) -> str:
    if decision == SemiAutoDecision.APPROVE_TRADE:
        return f"Trade preview allowed offline. Context score {score}/100; no order will be sent."
    if decision == SemiAutoDecision.APPROVE_REDUCED_RISK:
        return f"Only reduced-risk preview is acceptable. Context score {score}/100."
    if decision == SemiAutoDecision.REQUIRE_CONFIRMATION:
        return f"Manual confirmation is required before any offline preview. Context score {score}/100."
    if decision == SemiAutoDecision.BLOCK_TRADE:
        return f"Trade is blocked by the assistant. Action: {action.value}."
    if decision == SemiAutoDecision.STOP_SESSION:
        return "Session stop is recommended. Do not prepare a trade preview."
    return "Review only. No semi-auto trade preview should be prepared."


def _combined_reason_lines(approvals: tuple[str, ...], blocks: tuple[str, ...]) -> list[str]:
    lines: list[str] = []
    lines.extend(f"- Approval: {item}" for item in approvals)
    lines.extend(f"- Block: {item}" for item in blocks)
    return lines or ["- None"]


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _bool_attr(value: Any | None, name: str) -> bool:
    return bool(getattr(value, name, False))


def _value(value: object) -> str:
    return value.value if hasattr(value, "value") else str(value)


__all__ = [
    "build_semi_auto_decision",
    "render_semi_auto_decision_markdown",
]
