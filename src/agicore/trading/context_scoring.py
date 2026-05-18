"""Offline context scoring engine for AGIcore Trading."""
from __future__ import annotations

from .adaptive_memory_models import TraderMemoryProfile
from .behavior_models import BehaviorAnalysisResult
from .context_scoring_models import (
    ContextScoreBreakdown,
    ContextScoringInput,
    ContextScoringResult,
    TradeContextDecision,
)
from .daily_report_models import DailyTradingReport
from .market_regime_models import MarketRegimeAnalysis, VolatilityRegime
from .playbook_models import TraderProfile
from .session_replay_models import SessionReplayResult
from .strategy_dna_models import StrategyDNA
from .trade_journal_models import JournalAnalysisResult


def compute_trade_context_score(
    context: ContextScoringInput | None = None,
    *,
    market_regime: MarketRegimeAnalysis | None = None,
    behavior_result: BehaviorAnalysisResult | None = None,
    session_replay_result: SessionReplayResult | None = None,
    memory_profile: TraderMemoryProfile | None = None,
    trader_profile: TraderProfile | None = None,
    strategy_dna: StrategyDNA | None = None,
    daily_report: DailyTradingReport | None = None,
    journal_result: JournalAnalysisResult | None = None,
) -> ContextScoringResult:
    """Compute a deterministic offline context score from available trading signals."""
    if context is not None:
        market_regime = context.market_regime
        behavior_result = context.behavior_result
        session_replay_result = context.session_replay_result
        memory_profile = context.memory_profile
        trader_profile = context.trader_profile
        strategy_dna = context.strategy_dna
        daily_report = context.daily_report
        journal_result = context.journal_result

    favorable: list[str] = []
    risks: list[str] = []
    no_trade_reasons: list[str] = []

    market_score = _market_score(market_regime, favorable, risks, no_trade_reasons)
    behavior_score = _behavior_score(behavior_result, daily_report, favorable, risks, no_trade_reasons)
    discipline_score = _discipline_score(
        session_replay_result,
        daily_report,
        journal_result,
        favorable,
        risks,
    )
    memory_score = _memory_score(memory_profile, favorable, risks)
    emotional_score = _emotional_score(behavior_result, daily_report, journal_result, favorable, risks)
    volatility_score = _volatility_score(market_regime, favorable, risks)
    compatibility_score = _strategy_regime_score(
        market_regime,
        strategy_dna,
        trader_profile,
        daily_report,
        favorable,
        risks,
        no_trade_reasons,
    )

    breakdown = ContextScoreBreakdown(
        market_score=market_score,
        behavior_score=behavior_score,
        discipline_score=discipline_score,
        memory_score=memory_score,
        emotional_score=emotional_score,
        volatility_score=volatility_score,
        strategy_regime_compatibility_score=compatibility_score,
    )
    global_score = _weighted_global_score(breakdown)
    decision = build_context_decision(
        global_score=global_score,
        breakdown=breakdown,
        no_trade_reasons=tuple(no_trade_reasons),
        market_regime=market_regime,
    )
    recommendations = _recommendations(decision, breakdown, tuple(risks), market_regime)

    return ContextScoringResult(
        global_score=global_score,
        decision=decision,
        breakdown=breakdown,
        favorable_factors=tuple(dict.fromkeys(favorable)),
        risk_factors=tuple(dict.fromkeys(risks)),
        recommendations=recommendations,
        strategy_regime_notes=_strategy_regime_notes(market_regime, strategy_dna, trader_profile),
        no_trade_reasons=tuple(dict.fromkeys(no_trade_reasons)),
    )


def build_context_decision(
    *,
    global_score: int,
    breakdown: ContextScoreBreakdown,
    no_trade_reasons: tuple[str, ...] = (),
    market_regime: MarketRegimeAnalysis | None = None,
) -> TradeContextDecision:
    """Build an offline context decision from score and blocking risks."""
    if no_trade_reasons:
        return TradeContextDecision.NO_TRADE
    if market_regime is not None and market_regime.dangerous_market and global_score < 45:
        return TradeContextDecision.NO_TRADE
    if global_score >= 82 and breakdown.strategy_regime_compatibility_score >= 75:
        return TradeContextDecision.STRONG_TRADE_ALLOWED
    if global_score >= 68:
        return TradeContextDecision.TRADE_ALLOWED
    if global_score >= 52:
        return TradeContextDecision.REDUCE_RISK
    if global_score >= 35:
        return TradeContextDecision.HIGH_RISK_CONTEXT
    return TradeContextDecision.NO_TRADE


def render_context_score_markdown(result: ContextScoringResult) -> str:
    """Render the context scoring result as Markdown."""
    lines = [
        "# Context Scoring Engine",
        "",
        "## Score global",
        "",
        f"- Score: {result.global_score}/100",
        "",
        "## Decision AGIcore",
        "",
        f"- Decision: {result.decision.value}",
        "",
        "## Detail des scores",
        "",
        f"- Market: {result.breakdown.market_score}/100",
        f"- Behavior: {result.breakdown.behavior_score}/100",
        f"- Discipline: {result.breakdown.discipline_score}/100",
        f"- Memory: {result.breakdown.memory_score}/100",
        f"- Emotional: {result.breakdown.emotional_score}/100",
        f"- Volatility: {result.breakdown.volatility_score}/100",
        f"- Strategy/regime compatibility: {result.breakdown.strategy_regime_compatibility_score}/100",
        "",
        "## Facteurs favorables",
        "",
        *_bullet_lines(result.favorable_factors),
        "",
        "## Facteurs de risque",
        "",
        *_bullet_lines(result.risk_factors),
        "",
        "## Recommandations",
        "",
        *_bullet_lines(result.recommendations),
        "",
        "## Compatibilite Strategy DNA / Market Regime",
        "",
        *_bullet_lines(result.strategy_regime_notes),
        "",
    ]
    return "\n".join(lines)


def _market_score(
    market: MarketRegimeAnalysis | None,
    favorable: list[str],
    risks: list[str],
    no_trade_reasons: list[str],
) -> int:
    if market is None:
        risks.append("No market regime analysis provided.")
        return 50
    score = market.context_quality_score
    if market.dangerous_market:
        score -= 30
        risks.append("Market regime is flagged as dangerous.")
    if market.favorable_for_pullback_strategy:
        score += 18
        favorable.append("Market is favorable for EMA20 pullback strategy.")
    else:
        score -= 18
        risks.append("Market is not favorable for EMA20 pullback strategy.")
        if market.dangerous_market:
            no_trade_reasons.append("Dangerous market is incompatible with EMA20 pullback.")
    if market.confidence >= 75 and not market.dangerous_market:
        favorable.append("Market regime confidence is high.")
    return _clamp(score)


def _behavior_score(
    behavior: BehaviorAnalysisResult | None,
    report: DailyTradingReport | None,
    favorable: list[str],
    risks: list[str],
    no_trade_reasons: list[str],
) -> int:
    if behavior is None:
        return _score_from_report(report, default=60)
    score = behavior.scores.consistency_score
    classes = {_value(item) for item in behavior.classifications}
    if "REVENGE_TRADING_PROBABLE" in classes:
        score -= 35
        risks.append("Revenge trading probable.")
    if "OVERTRADING" in classes:
        score -= 25
        risks.append("Overtrading detected.")
    if "HIGH_RISK" in classes:
        score -= 20
        risks.append("Behavior analysis marks the session high risk.")
    if "DISCIPLINED" in classes and "CONSISTENT" in classes:
        score += 15
        favorable.append("Behavior is disciplined and consistent.")
    if any(_value(item) == "STOP_TRADING" for item in behavior.recommendations):
        no_trade_reasons.append("Behavior layer recommends STOP_TRADING.")
    return _clamp(score)


def _discipline_score(
    replay: SessionReplayResult | None,
    report: DailyTradingReport | None,
    journal: JournalAnalysisResult | None,
    favorable: list[str],
    risks: list[str],
) -> int:
    scores: list[int] = []
    if replay is not None:
        scores.append(int(replay.discipline_score))
        violations = sum(len(session.violations) for session in replay.sessions)
        if violations:
            risks.append(f"Replay contains {violations} rule violation(s).")
            scores[-1] -= min(35, violations * 8)
    if report is not None:
        scores.append(int(report.discipline_score))
        bad_violations = [item for item in report.rule_violations if "No rule violations" not in item]
        if bad_violations:
            risks.append("Daily report contains playbook or risk violations.")
            scores[-1] -= min(25, len(bad_violations) * 7)
    if journal is not None:
        compliance = (journal.playbook_compliance_rate + journal.risk_rules_compliance_rate) / 2
        journal_score = int(compliance * 100)
        scores.append(journal_score)
        if compliance < 0.8:
            risks.append("Journal compliance with playbook/risk rules is weak.")
    if not scores:
        return 60
    score = int(sum(scores) / len(scores))
    if score >= 85:
        favorable.append("Discipline score is high.")
    return _clamp(score)


def _memory_score(
    memory: TraderMemoryProfile | None,
    favorable: list[str],
    risks: list[str],
) -> int:
    if memory is None or memory.sessions_count == 0:
        return 55
    score = int(
        (
            memory.average_discipline_score
            + memory.average_emotional_risk_score
            + memory.average_consistency_score
        )
        / 3
    )
    if memory.recurring_dangerous_hours:
        score -= min(25, len(memory.recurring_dangerous_hours) * 8)
        risks.append("Memory contains recurring dangerous hours.")
    if memory.favorable_contexts:
        score += 10
        favorable.append("Adaptive memory contains favorable contexts.")
    if memory.average_discipline_score >= 80:
        favorable.append("Adaptive memory shows strong discipline.")
    return _clamp(score)


def _emotional_score(
    behavior: BehaviorAnalysisResult | None,
    report: DailyTradingReport | None,
    journal: JournalAnalysisResult | None,
    favorable: list[str],
    risks: list[str],
) -> int:
    score = 70
    if behavior is not None:
        score = behavior.scores.emotional_risk_score
    elif report is not None:
        score = report.emotional_risk_score
    if journal is not None:
        if journal.keyword_flags:
            score -= min(30, len(journal.keyword_flags) * 8)
            risks.append("Journal contains tilt/fatigue/revenge/peur/euphorie keywords.")
        risky_emotions = {"TILT", "FATIGUE", "ANGER", "FRUSTRATION", "FEAR", "EUPHORIA"}
        if any(name in risky_emotions for name, _count in journal.dominant_emotions[:2]):
            score -= 15
            risks.append("Journal dominant emotions are risky.")
    if score >= 80:
        favorable.append("Emotional risk score is strong.")
    elif score < 60:
        risks.append("Emotional risk score is elevated.")
    return _clamp(score)


def _volatility_score(
    market: MarketRegimeAnalysis | None,
    favorable: list[str],
    risks: list[str],
) -> int:
    if market is None:
        return 60
    if market.volatility == VolatilityRegime.NORMAL:
        favorable.append("Volatility is normal.")
        return 82
    if market.volatility == VolatilityRegime.LOW:
        risks.append("Volatility is too low for clean execution.")
        return 55
    if market.volatility == VolatilityRegime.HIGH:
        risks.append("Volatility is high; size should be reduced.")
        return 58
    risks.append("Volatility is extreme.")
    return 25


def _strategy_regime_score(
    market: MarketRegimeAnalysis | None,
    strategy: StrategyDNA | None,
    profile: TraderProfile | None,
    report: DailyTradingReport | None,
    favorable: list[str],
    risks: list[str],
    no_trade_reasons: list[str],
) -> int:
    score = 60
    if market is not None:
        score = 85 if market.favorable_for_pullback_strategy else 35
        if market.favorable_for_pullback_strategy:
            favorable.append("Strategy/regime compatibility is positive.")
        else:
            risks.append("Strategy/regime compatibility is weak.")
    if strategy is not None:
        name = strategy.name.casefold()
        text = " ".join((strategy.entry_conditions + (strategy.ema_filter or "",))).casefold()
        if "ema20" in name or "pullback" in name or "ema20" in text or "pullback" in text:
            score += 8
            favorable.append("Strategy DNA references EMA20/pullback logic.")
        if market is not None and not market.favorable_for_pullback_strategy and "ema20" in name:
            no_trade_reasons.append("Strategy DNA requires EMA20 context but market regime is unfavorable.")
    if profile is not None and profile.forbidden_conditions:
        score -= 5
    if report is not None:
        if any("VIOLATION" in item for item in report.strategy_alignment):
            score -= 25
            risks.append("Daily report strategy alignment contains violations.")
        elif any("OK" in item for item in report.strategy_alignment):
            score += 10
            favorable.append("Daily report strategy alignment is coherent.")
    return _clamp(score)


def _weighted_global_score(breakdown: ContextScoreBreakdown) -> int:
    weighted = (
        breakdown.market_score * 0.20
        + breakdown.behavior_score * 0.15
        + breakdown.discipline_score * 0.18
        + breakdown.memory_score * 0.10
        + breakdown.emotional_score * 0.15
        + breakdown.volatility_score * 0.10
        + breakdown.strategy_regime_compatibility_score * 0.12
    )
    return _clamp(round(weighted))


def _score_from_report(report: DailyTradingReport | None, *, default: int) -> int:
    if report is None:
        return default
    return _clamp(int((report.consistency_score + report.discipline_score) / 2))


def _recommendations(
    decision: TradeContextDecision,
    breakdown: ContextScoreBreakdown,
    risks: tuple[str, ...],
    market: MarketRegimeAnalysis | None,
) -> tuple[str, ...]:
    items: list[str] = []
    if decision == TradeContextDecision.NO_TRADE:
        items.append("Do not trade until blocking context risks are cleared.")
    elif decision in (TradeContextDecision.REDUCE_RISK, TradeContextDecision.HIGH_RISK_CONTEXT):
        items.append("Reduce size and require a stricter entry trigger.")
    elif decision == TradeContextDecision.STRONG_TRADE_ALLOWED:
        items.append("Trade is allowed if the playbook trigger confirms.")
    else:
        items.append("Trade is allowed with normal risk controls.")
    if breakdown.emotional_score < 60:
        items.append("Pause and reset emotional state before any new entry.")
    if breakdown.discipline_score < 60:
        items.append("Review playbook and risk rules before continuing.")
    if breakdown.volatility_score < 50:
        items.append("Stand aside or widen execution assumptions for abnormal volatility.")
    if market is not None:
        items.extend(market.recommendations)
    if any("dangerous hours" in item.lower() for item in risks):
        items.append("Avoid recurring dangerous hours from memory.")
    return tuple(dict.fromkeys(items))


def _strategy_regime_notes(
    market: MarketRegimeAnalysis | None,
    strategy: StrategyDNA | None,
    profile: TraderProfile | None,
) -> tuple[str, ...]:
    notes: list[str] = []
    if strategy is not None:
        notes.append(f"Strategy DNA: {strategy.name}")
    if market is not None:
        notes.append(f"Market regime: {market.primary_regime.value}")
        notes.append(f"EMA20 pullback compatible: {market.favorable_for_pullback_strategy}")
    if profile is not None:
        notes.append(f"Trader profile: {profile.name}")
    return tuple(notes or ["No Strategy DNA / Market Regime compatibility context provided."])


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _value(value: object) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "build_context_decision",
    "compute_trade_context_score",
    "render_context_score_markdown",
]
