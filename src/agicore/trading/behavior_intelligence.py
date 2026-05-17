"""Offline behavior intelligence for replayed trading sessions."""
from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable

from .behavior_models import (
    BehaviorAnalysisResult,
    BehaviorPattern,
    BehaviorRecommendation,
    BehaviorScores,
    BehaviorSummary,
    SessionBehaviorClass,
)
from .playbook_models import TraderProfile
from .session_replay_models import (
    ReplayEvent,
    ReplayEventType,
    ReplayViolationType,
    SessionReplayResult,
    SessionReplaySummary,
)
from .strategy_dna_models import StrategyDNA


def analyze_behavior(
    replay: SessionReplayResult,
    *,
    trader_profile: TraderProfile | None = None,
    strategy_dna: StrategyDNA | None = None,
) -> BehaviorAnalysisResult:
    """Classify replayed trading behavior and produce discipline guidance."""
    classifications = _classify_sessions(replay.sessions)
    patterns = _detect_patterns(replay)
    scores = _score_behavior(replay, patterns)
    recommendations = _recommend(classifications, patterns, replay)
    summary = _summarize(replay, classifications, patterns, scores)

    return BehaviorAnalysisResult(
        classifications=classifications,
        patterns=patterns,
        scores=scores,
        recommendations=recommendations,
        summary=summary,
        comparison_notes=_comparison_notes(replay, trader_profile, strategy_dna),
    )


def _classify_sessions(
    sessions: tuple[SessionReplaySummary, ...],
) -> tuple[SessionBehaviorClass, ...]:
    if not sessions:
        return (SessionBehaviorClass.DISCIPLINED, SessionBehaviorClass.CONSISTENT)

    classes: set[SessionBehaviorClass] = set()
    avg_score = sum(session.discipline_score for session in sessions) / len(sessions)
    pnl_values = [session.total_pnl for session in sessions]
    profitable_sessions = sum(1 for pnl in pnl_values if pnl > 0)
    losing_sessions = sum(1 for pnl in pnl_values if pnl < 0)
    trade_counts = [session.trade_count for session in sessions]

    if avg_score >= 85:
        classes.add(SessionBehaviorClass.DISCIPLINED)
    if _is_consistent(pnl_values, profitable_sessions, losing_sessions):
        classes.add(SessionBehaviorClass.CONSISTENT)
    if _is_unstable(pnl_values):
        classes.add(SessionBehaviorClass.UNSTABLE)
    if max(trade_counts, default=0) >= 8:
        classes.add(SessionBehaviorClass.AGGRESSIVE)

    violation_kinds = _violation_kinds(sessions)
    if ReplayViolationType.OVERTRADING in violation_kinds or ReplayViolationType.MAX_TRADES_PER_DAY in violation_kinds:
        classes.add(SessionBehaviorClass.OVERTRADING)
    if ReplayViolationType.REVENGE_TRADING_PROBABLE in violation_kinds:
        classes.add(SessionBehaviorClass.REVENGE_TRADING_PROBABLE)
    if {
        ReplayViolationType.DAILY_LOSS_EXCEEDED,
        ReplayViolationType.EXCESSIVE_UNIT_LOSS,
    } & violation_kinds:
        classes.add(SessionBehaviorClass.HIGH_RISK)

    if not classes:
        classes.add(SessionBehaviorClass.DISCIPLINED)
    return tuple(sorted(classes, key=lambda value: value.value))


def _detect_patterns(replay: SessionReplayResult) -> tuple[BehaviorPattern, ...]:
    patterns: set[BehaviorPattern] = set()
    sessions = replay.sessions
    events = replay.events
    violation_kinds = _violation_kinds(sessions)

    if ReplayViolationType.REVENGE_TRADING_PROBABLE in violation_kinds:
        patterns.add(BehaviorPattern.TRADE_FREQUENCY_ACCELERATION)
    if ReplayViolationType.EXCESSIVE_UNIT_LOSS in violation_kinds and any(
        session.max_loss_streak >= 2 for session in sessions
    ):
        patterns.add(BehaviorPattern.SIZE_INCREASE_AFTER_LOSSES)
    if _has_loss_after_winning_streak(events):
        patterns.add(BehaviorPattern.LOSS_AFTER_WINNING_STREAK)
    if _has_continued_after_stop_recommendation(events):
        patterns.add(BehaviorPattern.CONTINUED_AFTER_LIMIT_BREACH)
    if _late_trading_degraded(sessions):
        patterns.add(BehaviorPattern.LATE_TRADING_DEGRADATION)
    if _has_disciplined_recovery(sessions):
        patterns.add(BehaviorPattern.DISCIPLINED_RECOVERY_AFTER_LOSS)

    return tuple(sorted(patterns, key=lambda value: value.value))


def _score_behavior(
    replay: SessionReplayResult,
    patterns: tuple[BehaviorPattern, ...],
) -> BehaviorScores:
    discipline_score = _clamp(replay.discipline_score)
    emotional_penalty = 0
    escalation_penalty = 0

    for session in replay.sessions:
        for violation in session.violations:
            if violation.kind in {
                ReplayViolationType.REVENGE_TRADING_PROBABLE,
                ReplayViolationType.OVERTRADING,
                ReplayViolationType.MAX_TRADES_PER_DAY,
            }:
                emotional_penalty += violation.penalty
            if violation.kind in {
                ReplayViolationType.DAILY_LOSS_EXCEEDED,
                ReplayViolationType.EXCESSIVE_UNIT_LOSS,
            }:
                escalation_penalty += violation.penalty

    if BehaviorPattern.LOSS_AFTER_WINNING_STREAK in patterns:
        emotional_penalty += 10
    if BehaviorPattern.SIZE_INCREASE_AFTER_LOSSES in patterns:
        escalation_penalty += 15
    if BehaviorPattern.CONTINUED_AFTER_LIMIT_BREACH in patterns:
        escalation_penalty += 20

    return BehaviorScores(
        discipline_score=discipline_score,
        emotional_risk_score=_clamp(100 - emotional_penalty),
        consistency_score=_consistency_score(replay.sessions),
        risk_escalation_score=_clamp(100 - escalation_penalty),
    )


def _recommend(
    classifications: tuple[SessionBehaviorClass, ...],
    patterns: tuple[BehaviorPattern, ...],
    replay: SessionReplayResult,
) -> tuple[BehaviorRecommendation, ...]:
    recommendations: set[BehaviorRecommendation] = set()

    if SessionBehaviorClass.HIGH_RISK in classifications or BehaviorPattern.CONTINUED_AFTER_LIMIT_BREACH in patterns:
        recommendations.add(BehaviorRecommendation.STOP_TRADING)
    if BehaviorPattern.SIZE_INCREASE_AFTER_LOSSES in patterns:
        recommendations.add(BehaviorRecommendation.REDUCE_SIZE)
    if (
        SessionBehaviorClass.REVENGE_TRADING_PROBABLE in classifications
        or BehaviorPattern.TRADE_FREQUENCY_ACCELERATION in patterns
    ):
        recommendations.add(BehaviorRecommendation.TAKE_BREAK)
    if SessionBehaviorClass.OVERTRADING in classifications:
        recommendations.add(BehaviorRecommendation.LIMIT_MAX_TRADES)
    if _dangerous_hours(replay.sessions):
        recommendations.add(BehaviorRecommendation.AVOID_SPECIFIC_HOURS)
    if not recommendations:
        recommendations.add(BehaviorRecommendation.KEEP_CURRENT_RULES)

    return tuple(sorted(recommendations, key=lambda value: value.value))


def _summarize(
    replay: SessionReplayResult,
    classifications: tuple[SessionBehaviorClass, ...],
    patterns: tuple[BehaviorPattern, ...],
    scores: BehaviorScores,
) -> BehaviorSummary:
    dangerous_hours = _dangerous_hours(replay.sessions)
    strengths: list[str] = []
    weaknesses: list[str] = []

    if scores.discipline_score >= 85:
        strengths.append("High replay discipline score")
    if SessionBehaviorClass.CONSISTENT in classifications:
        strengths.append("Consistent session outcomes")
    if BehaviorPattern.DISCIPLINED_RECOVERY_AFTER_LOSS in patterns:
        strengths.append("Recovered after a loss without immediate escalation")
    if not strengths:
        strengths.append("No durable strength detected yet")

    if SessionBehaviorClass.OVERTRADING in classifications:
        weaknesses.append("Trade count exceeded declared limits")
    if SessionBehaviorClass.REVENGE_TRADING_PROBABLE in classifications:
        weaknesses.append("Probable revenge trading sequence detected")
    if SessionBehaviorClass.HIGH_RISK in classifications:
        weaknesses.append("Daily or unit loss limits were breached")
    if BehaviorPattern.LATE_TRADING_DEGRADATION in patterns:
        weaknesses.append("Late-session performance degraded")
    if not weaknesses:
        weaknesses.append("No major behavioral weakness detected")

    favorable_context = _favorable_context(replay.sessions)
    probable_profile = _probable_profile(classifications, patterns)
    return BehaviorSummary(
        strengths=tuple(strengths),
        weaknesses=tuple(weaknesses),
        dangerous_hours=dangerous_hours,
        favorable_context=favorable_context,
        probable_trader_profile=probable_profile,
    )


def _violation_kinds(sessions: Iterable[SessionReplaySummary]) -> set[ReplayViolationType]:
    return {violation.kind for session in sessions for violation in session.violations}


def _is_consistent(pnls: list[float], profitable_sessions: int, losing_sessions: int) -> bool:
    if not pnls:
        return True
    return profitable_sessions == len(pnls) or losing_sessions == len(pnls)


def _is_unstable(pnls: list[float]) -> bool:
    if len(pnls) < 2:
        return False
    spread = max(pnls) - min(pnls)
    avg_abs = sum(abs(pnl) for pnl in pnls) / len(pnls)
    return avg_abs > 0 and spread > avg_abs * 2.5


def _has_loss_after_winning_streak(events: tuple[ReplayEvent, ...]) -> bool:
    win_streak = 0
    for event in events:
        if event.event_type != ReplayEventType.TRADE_CLOSED:
            continue
        pnl = _extract_closed_pnl(event.message)
        if pnl is None:
            continue
        if pnl > 0:
            win_streak += 1
            continue
        if pnl < 0 and win_streak >= 2:
            return True
        win_streak = 0
    return False


def _has_continued_after_stop_recommendation(events: tuple[ReplayEvent, ...]) -> bool:
    stop_seen = False
    for event in events:
        if event.event_type == ReplayEventType.SESSION_STOP_RECOMMENDED:
            stop_seen = True
        elif stop_seen and event.event_type == ReplayEventType.TRADE_OPENED:
            return True
    return False


def _late_trading_degraded(sessions: tuple[SessionReplaySummary, ...]) -> bool:
    late_sessions = [
        session for session in sessions if session.end_time is not None and session.end_time.hour >= 20
    ]
    return bool(late_sessions) and sum(session.total_pnl for session in late_sessions) < 0


def _has_disciplined_recovery(sessions: tuple[SessionReplaySummary, ...]) -> bool:
    ordered = sorted(sessions, key=lambda session: session.session_day)
    for previous, current in zip(ordered, ordered[1:]):
        if previous.total_pnl < 0 and current.total_pnl > 0 and current.discipline_score >= 85:
            return True
    return False


def _dangerous_hours(sessions: tuple[SessionReplaySummary, ...]) -> tuple[int, ...]:
    counts: Counter[int] = Counter()
    for session in sessions:
        if session.total_pnl >= 0:
            continue
        for violation in session.violations:
            if violation.timestamp is not None:
                counts[violation.timestamp.hour] += 1
        if session.end_time is not None and session.end_time.hour >= 20:
            counts[session.end_time.hour] += 1
    return tuple(sorted(hour for hour, count in counts.items() if count > 0))


def _favorable_context(sessions: tuple[SessionReplaySummary, ...]) -> str:
    pnl_by_start_hour: defaultdict[int, float] = defaultdict(float)
    for session in sessions:
        if session.start_time is not None:
            pnl_by_start_hour[session.start_time.hour] += session.total_pnl
    if not pnl_by_start_hour:
        return "Insufficient replay history"
    best_hour, best_pnl = max(pnl_by_start_hour.items(), key=lambda item: item[1])
    return f"Best observed start-hour context: {best_hour:02d}:00 with PnL {best_pnl:.2f}"


def _probable_profile(
    classifications: tuple[SessionBehaviorClass, ...],
    patterns: tuple[BehaviorPattern, ...],
) -> str:
    if SessionBehaviorClass.HIGH_RISK in classifications and SessionBehaviorClass.OVERTRADING in classifications:
        return "High-activity risk-seeking intraday trader"
    if SessionBehaviorClass.REVENGE_TRADING_PROBABLE in classifications:
        return "Emotion-sensitive reactive trader"
    if SessionBehaviorClass.DISCIPLINED in classifications and SessionBehaviorClass.CONSISTENT in classifications:
        return "Rule-following consistent trader"
    if BehaviorPattern.LATE_TRADING_DEGRADATION in patterns:
        return "Session-fatigue-sensitive trader"
    return "Mixed-profile discretionary trader"


def _consistency_score(sessions: tuple[SessionReplaySummary, ...]) -> int:
    if not sessions:
        return 100
    pnls = [session.total_pnl for session in sessions]
    if len(pnls) == 1:
        return 100 if sessions[0].discipline_score >= 80 else 70
    avg_abs = sum(abs(pnl) for pnl in pnls) / len(pnls)
    if avg_abs == 0:
        return 100
    spread = max(pnls) - min(pnls)
    return _clamp(round(100 - min(80, (spread / avg_abs) * 20)))


def _extract_closed_pnl(message: str) -> float | None:
    marker = "PnL "
    if marker not in message:
        return None
    try:
        return float(message.rsplit(marker, maxsplit=1)[1])
    except ValueError:
        return None


def _comparison_notes(
    replay: SessionReplayResult,
    trader_profile: TraderProfile | None,
    strategy_dna: StrategyDNA | None,
) -> tuple[str, ...]:
    notes = list(replay.comparison_notes)
    if trader_profile is not None:
        notes.append(f"Behavior compared with trader profile: {trader_profile.name}")
    if strategy_dna is not None:
        notes.append(f"Behavior compared with strategy DNA: {strategy_dna.name}")
    return tuple(dict.fromkeys(notes))


def _clamp(value: int | float) -> int:
    return max(0, min(100, round(value)))


__all__ = ["analyze_behavior"]
