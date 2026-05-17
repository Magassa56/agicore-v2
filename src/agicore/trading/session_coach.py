"""Offline pre-, in-, and post-session coaching for AGIcore Trading."""
from __future__ import annotations

from datetime import date

from .adaptive_memory import compare_session_to_memory
from .adaptive_memory_models import TraderMemoryProfile
from .behavior_models import (
    BehaviorAnalysisResult,
    BehaviorPattern,
    BehaviorRecommendation,
    SessionBehaviorClass,
)
from .daily_report_models import DailyTradingReport
from .playbook_models import TraderProfile
from .session_coach_models import (
    LiveSessionCoachResult,
    PostSessionReview,
    PreSessionChecklist,
    SessionCoachDecision,
    SessionRiskLevel,
)
from .session_replay_models import ReplayViolationType, SessionReplayResult, SessionReplaySummary
from .strategy_dna_models import StrategyDNA


def build_pre_session_checklist(
    *,
    memory_profile: TraderMemoryProfile | None = None,
    trader_profile: TraderProfile | None = None,
    strategy_dna: StrategyDNA | None = None,
    daily_report: DailyTradingReport | None = None,
) -> PreSessionChecklist:
    """Build an offline checklist before the next trading session."""
    discipline_state = _discipline_state(memory_profile, daily_report)
    dangerous_hours = _dangerous_hours(memory_profile, daily_report)
    dangerous_contexts = _dangerous_contexts(memory_profile, daily_report)
    playbook_rules = _playbook_rules(trader_profile, strategy_dna)
    daily_limits = _daily_limits(trader_profile, strategy_dna)
    reminders = _emotional_reminders(memory_profile, daily_report)
    risk_level = _pre_session_risk_level(memory_profile, daily_report)

    return PreSessionChecklist(
        discipline_state=discipline_state,
        recurring_dangerous_contexts=dangerous_contexts,
        dangerous_hours=dangerous_hours,
        playbook_rules=playbook_rules,
        daily_limits=daily_limits,
        emotional_reminders=reminders,
        recommended_risk_level=risk_level,
        decision=_decision_for_risk(risk_level),
    )


def evaluate_live_session_state(
    *,
    replay_result: SessionReplayResult,
    behavior_result: BehaviorAnalysisResult | None = None,
    memory_profile: TraderMemoryProfile | None = None,
    trader_profile: TraderProfile | None = None,
    strategy_dna: StrategyDNA | None = None,
    daily_report: DailyTradingReport | None = None,
    session_date: date | None = None,
) -> LiveSessionCoachResult:
    """Evaluate the current offline session state and emit coaching guidance."""
    session = _select_session(replay_result, session_date)
    alerts: list[str] = []
    recommendations: list[str] = []

    if session is not None:
        alerts.extend(_session_alerts(session, memory_profile))
        recommendations.extend(_session_recommendations(session, trader_profile, strategy_dna))
    if behavior_result is not None:
        alerts.extend(_behavior_alerts(behavior_result))
        recommendations.extend(_behavior_recommendations(behavior_result))
    if daily_report is not None:
        alerts.extend(_daily_report_alerts(daily_report))

    stop_recommended = _has_stop_signal(alerts, recommendations, session, behavior_result, daily_report)
    break_recommended = _has_break_signal(alerts, recommendations, behavior_result)
    reduce_size = _has_reduce_size_signal(alerts, recommendations, behavior_result)
    decision = _live_decision(stop_recommended, break_recommended, reduce_size, alerts)

    return LiveSessionCoachResult(
        alerts=_unique(alerts) or ("No live session alert detected",),
        recommendations=_unique(recommendations) or ("Keep current rules and monitor replay state",),
        stop_recommended=stop_recommended,
        break_recommended=break_recommended,
        reduce_size=reduce_size,
        decision=decision,
    )


def build_post_session_review(
    *,
    replay_result: SessionReplayResult,
    behavior_result: BehaviorAnalysisResult,
    memory_profile: TraderMemoryProfile | None = None,
    trader_profile: TraderProfile | None = None,
    strategy_dna: StrategyDNA | None = None,
    daily_report: DailyTradingReport | None = None,
    session_date: date | None = None,
) -> PostSessionReview:
    """Build an offline post-session coaching review."""
    session = _select_session(replay_result, session_date)
    score = session.discipline_score if session is not None else replay_result.discipline_score
    violations = _violated_rules(session)
    errors = _detected_errors(session, behavior_result, daily_report)
    strengths = _strengths(behavior_result, score)
    improvements = _improvement_areas(errors, behavior_result, trader_profile, strategy_dna)
    memory_lines = _memory_comparison(behavior_result, memory_profile, daily_report)

    return PostSessionReview(
        discipline_summary=_post_session_summary(session, score),
        detected_errors=errors,
        violated_rules=violations,
        strengths=strengths,
        improvement_areas=improvements,
        session_score=score,
        memory_comparison=memory_lines,
        decision=_post_session_decision(score, errors, violations),
    )


def _select_session(
    replay_result: SessionReplayResult,
    session_date: date | None,
) -> SessionReplaySummary | None:
    if not replay_result.sessions:
        return None
    if session_date is None:
        return replay_result.sessions[-1]
    for session in replay_result.sessions:
        if session.session_day == session_date:
            return session
    return None


def _discipline_state(
    memory_profile: TraderMemoryProfile | None,
    daily_report: DailyTradingReport | None,
) -> str:
    if daily_report is not None:
        return f"Last daily discipline score: {daily_report.discipline_score}/100"
    if memory_profile is None or memory_profile.sessions_count == 0:
        return "No historical discipline memory available"
    return (
        f"Historical discipline average: {memory_profile.average_discipline_score:.1f}/100 "
        f"over {memory_profile.sessions_count} sessions"
    )


def _dangerous_hours(
    memory_profile: TraderMemoryProfile | None,
    daily_report: DailyTradingReport | None,
) -> tuple[int, ...]:
    hours = set(memory_profile.recurring_dangerous_hours if memory_profile is not None else ())
    if daily_report is not None:
        for item in daily_report.memory_comparison:
            if "dangerous hours" in item.lower():
                hours.update(_parse_hours(item))
    return tuple(sorted(hours))


def _parse_hours(value: str) -> tuple[int, ...]:
    hours: list[int] = []
    for token in value.replace(",", " ").split():
        if ":" not in token:
            continue
        try:
            hours.append(int(token.split(":", maxsplit=1)[0]))
        except ValueError:
            continue
    return tuple(hours)


def _dangerous_contexts(
    memory_profile: TraderMemoryProfile | None,
    daily_report: DailyTradingReport | None,
) -> tuple[str, ...]:
    contexts: list[str] = []
    if memory_profile is not None:
        contexts.extend(memory_profile.worst_contexts)
    if daily_report is not None:
        contexts.extend(item for item in daily_report.memory_comparison if "risk" in item.lower())
    return _unique(contexts) or ("No recurring dangerous context detected",)


def _playbook_rules(
    trader_profile: TraderProfile | None,
    strategy_dna: StrategyDNA | None,
) -> tuple[str, ...]:
    rules: list[str] = []
    if trader_profile is not None:
        rules.extend(trader_profile.entry_conditions)
        rules.extend(trader_profile.exit_conditions)
        rules.extend(f"Forbidden: {item}" for item in trader_profile.forbidden_conditions)
    if strategy_dna is not None:
        rules.extend(strategy_dna.entry_conditions)
        rules.extend(strategy_dna.exit_conditions)
    return _unique(rules) or ("No playbook or Strategy DNA rules provided",)


def _daily_limits(
    trader_profile: TraderProfile | None,
    strategy_dna: StrategyDNA | None,
) -> tuple[str, ...]:
    limits: list[str] = []
    if trader_profile is not None:
        rules = trader_profile.risk_rules
        if rules.max_daily_loss is not None:
            limits.append(f"Trader max daily loss: {abs(rules.max_daily_loss):.2f}")
        if rules.max_trades_per_day is not None:
            limits.append(f"Trader max trades/day: {rules.max_trades_per_day}")
        if rules.max_consecutive_losses is not None:
            limits.append(f"Trader max consecutive losses: {rules.max_consecutive_losses}")
    if strategy_dna is not None:
        rules = strategy_dna.risk_rules
        if rules.max_daily_loss is not None:
            limits.append(f"Strategy max daily loss: {abs(rules.max_daily_loss):.2f}")
        if rules.max_trades_per_day is not None:
            limits.append(f"Strategy max trades/day: {rules.max_trades_per_day}")
        if rules.max_consecutive_losses is not None:
            limits.append(f"Strategy max consecutive losses: {rules.max_consecutive_losses}")
    return _unique(limits) or ("No daily limit provided",)


def _emotional_reminders(
    memory_profile: TraderMemoryProfile | None,
    daily_report: DailyTradingReport | None,
) -> tuple[str, ...]:
    reminders: list[str] = []
    if memory_profile is not None:
        if any("REVENGE" in item.value for item in memory_profile.recurring_behavior_classes):
            reminders.append("Take a mandatory pause after each losing trade")
        if memory_profile.average_emotional_risk_score < 70:
            reminders.append("Start with reduced size because emotional risk memory is elevated")
    if daily_report is not None:
        for recommendation in daily_report.recommendations:
            if "BREAK" in recommendation or "STOP" in recommendation or "SIZE" in recommendation:
                reminders.append(recommendation)
    return _unique(reminders) or ("Follow planned rules before reacting to PnL",)


def _pre_session_risk_level(
    memory_profile: TraderMemoryProfile | None,
    daily_report: DailyTradingReport | None,
) -> SessionRiskLevel:
    if daily_report is not None and (
        daily_report.discipline_score < 50 or daily_report.emotional_risk_score < 50
    ):
        return SessionRiskLevel.CRITICAL
    if memory_profile is not None and (
        memory_profile.average_discipline_score < 60
        or memory_profile.average_emotional_risk_score < 60
    ):
        return SessionRiskLevel.HIGH
    if memory_profile is not None and (
        memory_profile.recurring_patterns or memory_profile.recurring_dangerous_hours
    ):
        return SessionRiskLevel.MODERATE
    return SessionRiskLevel.LOW


def _decision_for_risk(risk_level: SessionRiskLevel) -> SessionCoachDecision:
    if risk_level == SessionRiskLevel.CRITICAL:
        return SessionCoachDecision.REVIEW_REQUIRED
    if risk_level == SessionRiskLevel.HIGH:
        return SessionCoachDecision.REDUCE_RISK
    return SessionCoachDecision.CONTINUE


def _session_alerts(
    session: SessionReplaySummary,
    memory_profile: TraderMemoryProfile | None,
) -> list[str]:
    alerts: list[str] = []
    kinds = {violation.kind for violation in session.violations}
    if ReplayViolationType.REVENGE_TRADING_PROBABLE in kinds:
        alerts.append("Revenge trading risk detected")
    if ReplayViolationType.OVERTRADING in kinds or ReplayViolationType.MAX_TRADES_PER_DAY in kinds:
        alerts.append("Overtrading detected")
    if ReplayViolationType.DAILY_LOSS_EXCEEDED in kinds:
        alerts.append("Daily loss limit exceeded or too close")
    if ReplayViolationType.OUTSIDE_ALLOWED_HOURS in kinds:
        alerts.append("Trading inside dangerous or unauthorized hours")
    if ReplayViolationType.EXCESSIVE_UNIT_LOSS in kinds:
        alerts.append("Unit loss is excessive")
    if session.max_loss_streak >= 2:
        alerts.append(f"Loss streak detected: {session.max_loss_streak}")
    if memory_profile is not None and session.start_time is not None:
        if session.start_time.hour in memory_profile.recurring_dangerous_hours:
            alerts.append(f"Session started in recurring dangerous hour {session.start_time.hour:02d}:00")
    return alerts


def _session_recommendations(
    session: SessionReplaySummary,
    trader_profile: TraderProfile | None,
    strategy_dna: StrategyDNA | None,
) -> list[str]:
    recommendations: list[str] = []
    max_trades = _max_trade_limit(trader_profile, strategy_dna)
    if max_trades is not None and session.trade_count >= max_trades:
        recommendations.append("Do not add another trade after reaching the daily trade limit")
    max_loss = _max_daily_loss(trader_profile, strategy_dna)
    if max_loss is not None and session.total_pnl <= -abs(max_loss) * 0.8:
        recommendations.append("Stop or pause because daily loss is near the limit")
    if session.max_loss_streak >= 2:
        recommendations.append("Take a break after the loss streak before any new entry")
    return recommendations


def _behavior_alerts(behavior_result: BehaviorAnalysisResult) -> list[str]:
    alerts: list[str] = []
    if SessionBehaviorClass.REVENGE_TRADING_PROBABLE in behavior_result.classifications:
        alerts.append("Behavior is classified as probable revenge trading")
    if SessionBehaviorClass.OVERTRADING in behavior_result.classifications:
        alerts.append("Behavior is classified as overtrading")
    if SessionBehaviorClass.HIGH_RISK in behavior_result.classifications:
        alerts.append("Behavior is classified as high risk")
    if BehaviorPattern.SIZE_INCREASE_AFTER_LOSSES in behavior_result.patterns:
        alerts.append("Position size appears to increase after losses")
    if BehaviorPattern.TRADE_FREQUENCY_ACCELERATION in behavior_result.patterns:
        alerts.append("Trade frequency accelerated after losses")
    return alerts


def _behavior_recommendations(behavior_result: BehaviorAnalysisResult) -> list[str]:
    values: list[str] = []
    for recommendation in behavior_result.recommendations:
        if recommendation == BehaviorRecommendation.STOP_TRADING:
            values.append("Stop trading for this session")
        elif recommendation == BehaviorRecommendation.TAKE_BREAK:
            values.append("Take a mandatory break before another trade")
        elif recommendation == BehaviorRecommendation.REDUCE_SIZE:
            values.append("Reduce size until behavior normalizes")
        elif recommendation == BehaviorRecommendation.LIMIT_MAX_TRADES:
            values.append("Lower or enforce the max trades/day limit")
        elif recommendation == BehaviorRecommendation.AVOID_SPECIFIC_HOURS:
            values.append("Avoid the detected dangerous hours")
        else:
            values.append("Keep current rules")
    return values


def _daily_report_alerts(daily_report: DailyTradingReport) -> list[str]:
    alerts: list[str] = []
    if daily_report.discipline_score < 70:
        alerts.append("Daily report discipline score is degraded")
    if daily_report.emotional_risk_score < 70:
        alerts.append("Daily report emotional risk score is degraded")
    return alerts


def _has_stop_signal(
    alerts: list[str],
    recommendations: list[str],
    session: SessionReplaySummary | None,
    behavior_result: BehaviorAnalysisResult | None,
    daily_report: DailyTradingReport | None,
) -> bool:
    if any("stop" in item.lower() for item in recommendations):
        return True
    if any("daily loss" in item.lower() or "high risk" in item.lower() for item in alerts):
        return True
    if session is not None and session.discipline_score < 40:
        return True
    if behavior_result is not None and behavior_result.scores.risk_escalation_score < 50:
        return True
    return daily_report is not None and daily_report.discipline_score < 40


def _has_break_signal(
    alerts: list[str],
    recommendations: list[str],
    behavior_result: BehaviorAnalysisResult | None,
) -> bool:
    if any("break" in item.lower() or "loss streak" in item.lower() for item in alerts + recommendations):
        return True
    return (
        behavior_result is not None
        and BehaviorRecommendation.TAKE_BREAK in behavior_result.recommendations
    )


def _has_reduce_size_signal(
    alerts: list[str],
    recommendations: list[str],
    behavior_result: BehaviorAnalysisResult | None,
) -> bool:
    if any("size" in item.lower() for item in alerts + recommendations):
        return True
    return (
        behavior_result is not None
        and BehaviorRecommendation.REDUCE_SIZE in behavior_result.recommendations
    )


def _live_decision(
    stop_recommended: bool,
    break_recommended: bool,
    reduce_size: bool,
    alerts: list[str],
) -> SessionCoachDecision:
    if stop_recommended:
        return SessionCoachDecision.STOP_TRADING
    if break_recommended:
        return SessionCoachDecision.TAKE_BREAK
    if reduce_size:
        return SessionCoachDecision.REDUCE_RISK
    if alerts:
        return SessionCoachDecision.REVIEW_REQUIRED
    return SessionCoachDecision.CONTINUE


def _violated_rules(session: SessionReplaySummary | None) -> tuple[str, ...]:
    if session is None or not session.violations:
        return ("No rule violated",)
    return tuple(f"{violation.kind.value}: {violation.message}" for violation in session.violations)


def _detected_errors(
    session: SessionReplaySummary | None,
    behavior_result: BehaviorAnalysisResult,
    daily_report: DailyTradingReport | None,
) -> tuple[str, ...]:
    errors: list[str] = []
    if session is not None:
        errors.extend(_session_alerts(session, None))
    errors.extend(
        weakness
        for weakness in behavior_result.summary.weaknesses
        if not weakness.lower().startswith("no major")
    )
    if daily_report is not None:
        errors.extend(
            violation
            for violation in daily_report.rule_violations
            if not violation.lower().startswith("no rule")
        )
    return _unique(errors) or ("No major error detected",)


def _strengths(
    behavior_result: BehaviorAnalysisResult,
    score: int,
) -> tuple[str, ...]:
    strengths = list(behavior_result.summary.strengths)
    if score >= 85:
        strengths.append("Session discipline score stayed strong")
    return _unique(strengths) or ("No durable strength detected yet",)


def _improvement_areas(
    errors: tuple[str, ...],
    behavior_result: BehaviorAnalysisResult,
    trader_profile: TraderProfile | None,
    strategy_dna: StrategyDNA | None,
) -> tuple[str, ...]:
    areas: list[str] = []
    if any("overtrading" in item.lower() or "trade count" in item.lower() for item in errors):
        areas.append("Reduce trade count and enforce max trades/day")
    if any("revenge" in item.lower() or "frequency" in item.lower() for item in errors):
        areas.append("Add a mandatory pause after losing trades")
    if any("daily loss" in item.lower() or "unit loss" in item.lower() for item in errors):
        areas.append("Stop earlier when loss limits are approached")
    if behavior_result.scores.emotional_risk_score < 70:
        areas.append("Lower emotional risk before increasing size")
    if trader_profile is not None:
        areas.append(f"Review trader playbook: {trader_profile.name}")
    if strategy_dna is not None:
        areas.append(f"Review Strategy DNA: {strategy_dna.name}")
    return _unique(areas) or ("Keep current rules and continue collecting evidence",)


def _memory_comparison(
    behavior_result: BehaviorAnalysisResult,
    memory_profile: TraderMemoryProfile | None,
    daily_report: DailyTradingReport | None,
) -> tuple[str, ...]:
    if daily_report is not None and daily_report.memory_comparison:
        return daily_report.memory_comparison
    if memory_profile is None or memory_profile.sessions_count == 0:
        return ("No adaptive memory available",)
    comparison = compare_session_to_memory(behavior_result, memory_profile)
    lines = [
        f"Discipline delta: {comparison.discipline_delta:.2f}",
        f"Emotional risk delta: {comparison.emotional_risk_delta:.2f}",
        f"Consistency delta: {comparison.consistency_delta:.2f}",
    ]
    if comparison.signals:
        lines.append("Signals: " + ", ".join(signal.value for signal in comparison.signals))
    return tuple(lines)


def _post_session_summary(
    session: SessionReplaySummary | None,
    score: int,
) -> str:
    if session is None:
        return f"No replayed session found. Discipline score: {score}/100"
    return (
        f"{session.session_day.isoformat()} finished with PnL {session.total_pnl:.2f}, "
        f"{session.trade_count} trades, discipline score {score}/100"
    )


def _post_session_decision(
    score: int,
    errors: tuple[str, ...],
    violations: tuple[str, ...],
) -> SessionCoachDecision:
    if score < 40 or any("DAILY_LOSS_EXCEEDED" in item for item in violations):
        return SessionCoachDecision.STOP_TRADING
    if violations != ("No rule violated",) or errors != ("No major error detected",):
        return SessionCoachDecision.REVIEW_REQUIRED
    return SessionCoachDecision.CONTINUE


def _max_trade_limit(
    trader_profile: TraderProfile | None,
    strategy_dna: StrategyDNA | None,
) -> int | None:
    limits = []
    if trader_profile is not None and trader_profile.risk_rules.max_trades_per_day is not None:
        limits.append(trader_profile.risk_rules.max_trades_per_day)
    if strategy_dna is not None and strategy_dna.risk_rules.max_trades_per_day is not None:
        limits.append(strategy_dna.risk_rules.max_trades_per_day)
    return min(limits) if limits else None


def _max_daily_loss(
    trader_profile: TraderProfile | None,
    strategy_dna: StrategyDNA | None,
) -> float | None:
    limits = []
    if trader_profile is not None and trader_profile.risk_rules.max_daily_loss is not None:
        limits.append(abs(trader_profile.risk_rules.max_daily_loss))
    if strategy_dna is not None and strategy_dna.risk_rules.max_daily_loss is not None:
        limits.append(abs(strategy_dna.risk_rules.max_daily_loss))
    return min(limits) if limits else None


def _unique(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


__all__ = [
    "build_post_session_review",
    "build_pre_session_checklist",
    "evaluate_live_session_state",
]
