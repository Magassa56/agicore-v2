"""Offline daily trading report generation."""
from __future__ import annotations

from datetime import date

from .adaptive_memory import compare_session_to_memory, generate_adaptive_recommendations
from .adaptive_memory_models import TraderMemoryProfile
from .behavior_models import BehaviorAnalysisResult
from .daily_report_models import DailyTradingReport
from .playbook_models import TraderProfile
from .session_replay_models import SessionReplayResult, SessionReplaySummary
from .strategy_dna_models import StrategyDNA


def build_daily_trading_report(
    *,
    report_date: date,
    replay_result: SessionReplayResult,
    behavior_result: BehaviorAnalysisResult,
    memory_profile: TraderMemoryProfile | None = None,
    trader_profile: TraderProfile | None = None,
    strategy_dna: StrategyDNA | None = None,
) -> DailyTradingReport:
    """Build an offline daily trading report from existing analysis results."""
    session = _find_session(replay_result, report_date)
    memory_lines = _memory_comparison_lines(behavior_result, memory_profile)
    recommendations = _recommendation_lines(behavior_result, memory_profile)
    playbook_alignment = _playbook_alignment(session, trader_profile)
    strategy_alignment = _strategy_alignment(session, strategy_dna)
    violations = _violation_lines(session)

    return DailyTradingReport(
        report_date=report_date,
        session_summary=_session_summary(session),
        total_pnl=session.total_pnl if session else 0.0,
        trade_count=session.trade_count if session else 0,
        win_rate=session.win_rate if session else 0.0,
        discipline_score=session.discipline_score if session else replay_result.discipline_score,
        emotional_risk_score=behavior_result.scores.emotional_risk_score,
        consistency_score=behavior_result.scores.consistency_score,
        behavior_classifications=tuple(item.value for item in behavior_result.classifications),
        rule_violations=violations,
        recommendations=recommendations,
        memory_comparison=memory_lines,
        playbook_alignment=playbook_alignment,
        strategy_alignment=strategy_alignment,
        next_session_action_plan=_action_plan(recommendations, violations, behavior_result),
    )


def render_daily_trading_report_markdown(report: DailyTradingReport) -> str:
    """Render a readable Markdown daily trading report."""
    lines = [
        f"# Daily Trading Report - {report.report_date.isoformat()}",
        "",
        "## Resume du jour",
        "",
        f"- Session: {report.session_summary}",
        f"- Discipline score: {report.discipline_score}/100",
        f"- Emotional risk score: {report.emotional_risk_score}/100",
        f"- Consistency score: {report.consistency_score}/100",
        "",
        "## Resultats trading",
        "",
        f"- PnL total: {_money(report.total_pnl)}",
        f"- Nombre de trades: {report.trade_count}",
        f"- Win rate: {report.win_rate:.2%}",
        "",
        "## Discipline & comportement",
        "",
        *_bullet_list(report.behavior_classifications),
        "",
        "## Violations detectees",
        "",
        *_bullet_list(report.rule_violations),
        "",
        "## Recommandations AGIcore",
        "",
        *_bullet_list(report.recommendations),
        "",
        "## Comparaison avec memoire historique",
        "",
        *_bullet_list(report.memory_comparison),
        "",
        "## Respect playbook / Strategy DNA",
        "",
        *(_prefixed("Playbook", report.playbook_alignment) + _prefixed("Strategy DNA", report.strategy_alignment)),
        "",
        "## Plan d'action pour la prochaine session",
        "",
        *_bullet_list(report.next_session_action_plan),
        "",
    ]
    return "\n".join(lines)


def _find_session(
    replay_result: SessionReplayResult,
    report_date: date,
) -> SessionReplaySummary | None:
    for session in replay_result.sessions:
        if session.session_day == report_date:
            return session
    return None


def _session_summary(session: SessionReplaySummary | None) -> str:
    if session is None:
        return "No replayed session for this date"
    start = session.start_time.strftime("%H:%M") if session.start_time else "n/a"
    end = session.end_time.strftime("%H:%M") if session.end_time else "n/a"
    return f"{start}-{end}, {session.trade_count} trades, PnL {_money(session.total_pnl)}"


def _violation_lines(session: SessionReplaySummary | None) -> tuple[str, ...]:
    if session is None or not session.violations:
        return ("No rule violations detected",)
    return tuple(
        f"{violation.kind.value}: {violation.message}"
        for violation in session.violations
    )


def _memory_comparison_lines(
    behavior_result: BehaviorAnalysisResult,
    memory_profile: TraderMemoryProfile | None,
) -> tuple[str, ...]:
    if memory_profile is None or memory_profile.sessions_count == 0:
        return ("No historical memory available",)
    comparison = compare_session_to_memory(behavior_result, memory_profile)
    lines = [
        f"Historical sessions: {memory_profile.sessions_count}",
        f"Discipline delta: {comparison.discipline_delta:.2f}",
        f"Emotional risk delta: {comparison.emotional_risk_delta:.2f}",
        f"Consistency delta: {comparison.consistency_delta:.2f}",
    ]
    if comparison.signals:
        lines.append("Signals: " + ", ".join(signal.value for signal in comparison.signals))
    if comparison.repeated_patterns:
        lines.append("Repeated patterns: " + ", ".join(item.value for item in comparison.repeated_patterns))
    if comparison.repeated_dangerous_hours:
        lines.append(
            "Repeated dangerous hours: "
            + ", ".join(f"{hour:02d}:00" for hour in comparison.repeated_dangerous_hours)
        )
    return tuple(lines)


def _recommendation_lines(
    behavior_result: BehaviorAnalysisResult,
    memory_profile: TraderMemoryProfile | None,
) -> tuple[str, ...]:
    recommendations = [item.value for item in behavior_result.recommendations]
    if memory_profile is not None and memory_profile.sessions_count > 0:
        comparison = compare_session_to_memory(behavior_result, memory_profile)
        recommendations.extend(
            item.value for item in generate_adaptive_recommendations(memory_profile, comparison)
        )
    if not recommendations:
        return ("KEEP_CURRENT_RULES",)
    return tuple(dict.fromkeys(recommendations))


def _playbook_alignment(
    session: SessionReplaySummary | None,
    trader_profile: TraderProfile | None,
) -> tuple[str, ...]:
    if trader_profile is None:
        return ("No trader playbook provided",)
    if session is None:
        return (f"Trader profile loaded: {trader_profile.name}", "No session to compare")

    lines = [f"Trader profile: {trader_profile.name}"]
    rules = trader_profile.risk_rules
    if rules.max_trades_per_day is not None:
        status = "OK" if session.trade_count <= rules.max_trades_per_day else "VIOLATION"
        lines.append(f"Max trades/day {rules.max_trades_per_day}: {status}")
    if rules.max_daily_loss is not None:
        status = "OK" if session.total_pnl >= -abs(rules.max_daily_loss) else "VIOLATION"
        lines.append(f"Max daily loss {abs(rules.max_daily_loss):.2f}: {status}")
    if rules.max_consecutive_losses is not None:
        status = "OK" if session.max_loss_streak <= rules.max_consecutive_losses else "VIOLATION"
        lines.append(f"Max loss streak {rules.max_consecutive_losses}: {status}")
    if len(lines) == 1:
        lines.append("No quantitative playbook rule provided")
    return tuple(lines)


def _strategy_alignment(
    session: SessionReplaySummary | None,
    strategy_dna: StrategyDNA | None,
) -> tuple[str, ...]:
    if strategy_dna is None:
        return ("No Strategy DNA provided",)
    if session is None:
        return (f"Strategy DNA loaded: {strategy_dna.name}", "No session to compare")

    lines = [f"Strategy DNA: {strategy_dna.name}"]
    if strategy_dna.allowed_hours and session.start_time is not None:
        status = "OK" if session.start_time.hour in strategy_dna.allowed_hours else "VIOLATION"
        hours = ", ".join(f"{hour:02d}:00" for hour in strategy_dna.allowed_hours)
        lines.append(f"Allowed hours ({hours}): {status}")
    if strategy_dna.risk_rules.max_trades_per_day is not None:
        limit = strategy_dna.risk_rules.max_trades_per_day
        status = "OK" if session.trade_count <= limit else "VIOLATION"
        lines.append(f"Strategy max trades/day {limit}: {status}")
    if len(lines) == 1:
        lines.append("No quantitative Strategy DNA rule provided")
    return tuple(lines)


def _action_plan(
    recommendations: tuple[str, ...],
    violations: tuple[str, ...],
    behavior_result: BehaviorAnalysisResult,
) -> tuple[str, ...]:
    actions: list[str] = []
    if any("STOP" in item or "BREAK" in item for item in recommendations):
        actions.append("Respect mandatory stop/break rules before the next entry")
    if any("TRADES" in item for item in recommendations):
        actions.append("Set a hard maximum trade count before the session starts")
    if any("HOURS" in item for item in recommendations):
        actions.append("Block or avoid recurring dangerous hours")
    if any("SIZE" in item for item in recommendations):
        actions.append("Reduce size until risk escalation disappears from replay")
    if violations and violations != ("No rule violations detected",):
        actions.append("Review every rule violation before the next session")
    if behavior_result.scores.discipline_score >= 85 and not actions:
        actions.append("Keep current rules and continue collecting replay evidence")
    return tuple(dict.fromkeys(actions or ["Keep current rules and monitor next replay"]))


def _bullet_list(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _prefixed(prefix: str, values: tuple[str, ...]) -> list[str]:
    return [f"- {prefix}: {value}" for value in values]


def _money(value: float) -> str:
    return f"{value:.2f}"


__all__ = [
    "build_daily_trading_report",
    "render_daily_trading_report_markdown",
]
