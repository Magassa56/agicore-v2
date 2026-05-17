"""Offline replay and learning helpers for normalized trading sessions."""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from datetime import date

from .import_nt8_csv import NormalizedTrade
from .playbook_models import TraderProfile
from .session_replay_models import (
    ReplayEvent,
    ReplayEventType,
    ReplayViolation,
    ReplayViolationType,
    SessionReplayConfig,
    SessionReplayResult,
    SessionReplaySummary,
)
from .strategy_dna_models import StrategyDNA


def replay_trading_sessions(
    trades: Sequence[NormalizedTrade],
    *,
    config: SessionReplayConfig | None = None,
    trader_profile: TraderProfile | None = None,
    strategy_dna: StrategyDNA | None = None,
) -> SessionReplayResult:
    """Replay normalized trades by day and detect simple discipline issues."""
    effective_config = _merge_config(config or SessionReplayConfig(), trader_profile, strategy_dna)
    sessions_by_day = group_trades_by_session(trades)
    events: list[ReplayEvent] = []
    summaries: list[SessionReplaySummary] = []

    for session_day in sorted(sessions_by_day):
        session_trades = sorted(sessions_by_day[session_day], key=lambda trade: trade.entry_time)
        summary, session_events = _replay_session(
            session_day,
            session_trades,
            effective_config,
            trader_profile=trader_profile,
            strategy_dna=strategy_dna,
        )
        summaries.append(summary)
        events.extend(session_events)

    score = _average_score(summary.discipline_score for summary in summaries)
    return SessionReplayResult(
        sessions=tuple(summaries),
        events=tuple(events),
        discipline_score=score,
        comparison_notes=_comparison_notes(trader_profile, strategy_dna, effective_config),
    )


def group_trades_by_session(
    trades: Sequence[NormalizedTrade],
) -> dict[date, tuple[NormalizedTrade, ...]]:
    """Group trades by exit date, used as the realized session day."""
    grouped: defaultdict[date, list[NormalizedTrade]] = defaultdict(list)
    for trade in trades:
        grouped[trade.exit_time.date()].append(trade)
    return {
        session_day: tuple(sorted(day_trades, key=lambda trade: trade.entry_time))
        for session_day, day_trades in grouped.items()
    }


def _replay_session(
    session_day: date,
    trades: Sequence[NormalizedTrade],
    config: SessionReplayConfig,
    *,
    trader_profile: TraderProfile | None,
    strategy_dna: StrategyDNA | None,
) -> tuple[SessionReplaySummary, tuple[ReplayEvent, ...]]:
    events: list[ReplayEvent] = []
    violations: list[ReplayViolation] = []
    first_trade = trades[0] if trades else None
    last_trade = trades[-1] if trades else None
    start_time = first_trade.entry_time if first_trade else None
    end_time = last_trade.exit_time if last_trade else None

    if start_time is not None:
        events.append(
            ReplayEvent(
                event_type=ReplayEventType.SESSION_STARTED,
                timestamp=start_time,
                session_day=session_day,
                message=f"Session started on {session_day.isoformat()}",
            )
        )

    running_pnl = 0.0
    previous_trade: NormalizedTrade | None = None
    max_loss_streak = 0
    current_loss_streak = 0

    for index, trade in enumerate(trades, start=1):
        events.append(
            ReplayEvent(
                event_type=ReplayEventType.TRADE_OPENED,
                timestamp=trade.entry_time,
                session_day=session_day,
                message=f"Trade {index} opened",
                trade_index=index,
            )
        )
        running_pnl += trade.pnl
        if trade.pnl > 0:
            current_loss_streak = 0
        else:
            current_loss_streak += 1
            max_loss_streak = max(max_loss_streak, current_loss_streak)

        new_violations = _detect_trade_violations(
            trade,
            index,
            running_pnl,
            previous_trade,
            config,
        )
        violations.extend(new_violations)

        events.append(
            ReplayEvent(
                event_type=ReplayEventType.TRADE_CLOSED,
                timestamp=trade.exit_time,
                session_day=session_day,
                message=f"Trade {index} closed with PnL {trade.pnl:.2f}",
                trade_index=index,
            )
        )
        for violation in new_violations:
            events.append(_violation_event(session_day, violation))
        if any(_should_stop_session(violation) for violation in new_violations):
            events.append(
                ReplayEvent(
                    event_type=ReplayEventType.SESSION_STOP_RECOMMENDED,
                    timestamp=trade.exit_time,
                    session_day=session_day,
                    message="Session stop recommended after rule violation",
                    trade_index=index,
                )
            )
        previous_trade = trade

    session_violations = _detect_session_violations(trades, config, end_time)
    violations.extend(session_violations)
    for violation in session_violations:
        events.append(_violation_event(session_day, violation))
    if session_violations and end_time is not None:
        events.append(
            ReplayEvent(
                event_type=ReplayEventType.SESSION_STOP_RECOMMENDED,
                timestamp=end_time,
                session_day=session_day,
                message="Session stop recommended after session-level violation",
            )
        )

    total_pnl = sum(trade.pnl for trade in trades)
    wins = sum(1 for trade in trades if trade.pnl > 0)
    summary = SessionReplaySummary(
        session_day=session_day,
        total_pnl=total_pnl,
        trade_count=len(trades),
        win_rate=(wins / len(trades)) if trades else 0.0,
        largest_loss=min((trade.pnl for trade in trades), default=0.0),
        largest_gain=max((trade.pnl for trade in trades), default=0.0),
        max_loss_streak=max_loss_streak,
        start_time=start_time,
        end_time=end_time,
        discipline_score=_discipline_score(violations),
        violations=tuple(violations),
    )

    if end_time is not None:
        events.append(
            ReplayEvent(
                event_type=ReplayEventType.SESSION_ENDED,
                timestamp=end_time,
                session_day=session_day,
                message=f"Session ended with PnL {total_pnl:.2f}",
            )
        )
    return summary, tuple(events)


def _detect_trade_violations(
    trade: NormalizedTrade,
    index: int,
    running_pnl: float,
    previous_trade: NormalizedTrade | None,
    config: SessionReplayConfig,
) -> list[ReplayViolation]:
    violations: list[ReplayViolation] = []
    if config.allowed_hours and trade.entry_time.hour not in config.allowed_hours:
        violations.append(
            ReplayViolation(
                kind=ReplayViolationType.OUTSIDE_ALLOWED_HOURS,
                message=f"Trade opened outside allowed hours at {trade.entry_time.hour:02d}:00",
                timestamp=trade.entry_time,
                trade_index=index,
            )
        )
    if config.max_daily_loss is not None and running_pnl <= -abs(config.max_daily_loss):
        violations.append(
            ReplayViolation(
                kind=ReplayViolationType.DAILY_LOSS_EXCEEDED,
                message=f"Running daily loss exceeded {abs(config.max_daily_loss):.2f}",
                timestamp=trade.exit_time,
                trade_index=index,
                penalty=20,
            )
        )
    if config.max_unit_loss is not None and trade.pnl <= -abs(config.max_unit_loss):
        violations.append(
            ReplayViolation(
                kind=ReplayViolationType.EXCESSIVE_UNIT_LOSS,
                message=f"Trade loss exceeded {abs(config.max_unit_loss):.2f}",
                timestamp=trade.exit_time,
                trade_index=index,
                penalty=15,
            )
        )
    if _is_revenge_trade(previous_trade, trade, config.revenge_trade_window_minutes):
        violations.append(
            ReplayViolation(
                kind=ReplayViolationType.REVENGE_TRADING_PROBABLE,
                message="New trade opened shortly after a losing trade",
                timestamp=trade.entry_time,
                trade_index=index,
                penalty=15,
            )
        )
    return violations


def _detect_session_violations(
    trades: Sequence[NormalizedTrade],
    config: SessionReplayConfig,
    timestamp,
) -> list[ReplayViolation]:
    if not trades or timestamp is None:
        return []
    violations: list[ReplayViolation] = []
    trade_count = len(trades)
    if trade_count > config.overtrading_threshold:
        violations.append(
            ReplayViolation(
                kind=ReplayViolationType.OVERTRADING,
                message=f"Session traded {trade_count} times",
                timestamp=timestamp,
                penalty=15,
            )
        )
    if trade_count > config.max_trades_per_day:
        violations.append(
            ReplayViolation(
                kind=ReplayViolationType.MAX_TRADES_PER_DAY,
                message=f"Session exceeded max trades/day: {trade_count}",
                timestamp=timestamp,
                penalty=20,
            )
        )
    return violations


def _is_revenge_trade(
    previous_trade: NormalizedTrade | None,
    trade: NormalizedTrade,
    window_minutes: int,
) -> bool:
    if previous_trade is None or previous_trade.pnl >= 0:
        return False
    gap_seconds = (trade.entry_time - previous_trade.exit_time).total_seconds()
    return 0 <= gap_seconds <= window_minutes * 60


def _violation_event(session_day: date, violation: ReplayViolation) -> ReplayEvent:
    return ReplayEvent(
        event_type=ReplayEventType.RULE_VIOLATION,
        timestamp=violation.timestamp,
        session_day=session_day,
        message=violation.message,
        trade_index=violation.trade_index,
        violation=violation,
    )


def _should_stop_session(violation: ReplayViolation) -> bool:
    return violation.kind in {
        ReplayViolationType.DAILY_LOSS_EXCEEDED,
        ReplayViolationType.EXCESSIVE_UNIT_LOSS,
    }


def _discipline_score(violations: Sequence[ReplayViolation]) -> int:
    return max(0, 100 - sum(violation.penalty for violation in violations))


def _average_score(scores) -> int:
    values = list(scores)
    if not values:
        return 100
    return round(sum(values) / len(values))


def _merge_config(
    config: SessionReplayConfig,
    trader_profile: TraderProfile | None,
    strategy_dna: StrategyDNA | None,
) -> SessionReplayConfig:
    max_daily_loss = config.max_daily_loss
    max_trades_per_day = config.max_trades_per_day
    allowed_hours = config.allowed_hours

    if trader_profile is not None:
        rules = trader_profile.risk_rules
        max_daily_loss = _prefer(max_daily_loss, rules.max_daily_loss)
        max_trades_per_day = int(_prefer(max_trades_per_day, rules.max_trades_per_day))
        if rules.forbidden_hours and allowed_hours:
            allowed_hours = tuple(hour for hour in allowed_hours if hour not in rules.forbidden_hours)

    if strategy_dna is not None:
        max_trades_per_day = int(_prefer(max_trades_per_day, strategy_dna.risk_rules.max_trades_per_day))
        max_daily_loss = _prefer(max_daily_loss, strategy_dna.risk_rules.max_daily_loss)
        if strategy_dna.allowed_hours:
            allowed_hours = strategy_dna.allowed_hours

    return SessionReplayConfig(
        max_trades_per_day=max_trades_per_day,
        overtrading_threshold=config.overtrading_threshold,
        max_daily_loss=max_daily_loss,
        max_unit_loss=config.max_unit_loss,
        allowed_hours=allowed_hours,
        revenge_trade_window_minutes=config.revenge_trade_window_minutes,
    )


def _prefer(current, candidate):
    return current if candidate is None else candidate


def _comparison_notes(
    trader_profile: TraderProfile | None,
    strategy_dna: StrategyDNA | None,
    config: SessionReplayConfig,
) -> tuple[str, ...]:
    notes: list[str] = []
    if trader_profile is not None:
        notes.append(f"Compared with trader profile: {trader_profile.name}")
    if strategy_dna is not None:
        notes.append(f"Compared with strategy DNA: {strategy_dna.name}")
    if config.allowed_hours:
        hours = ", ".join(f"{hour:02d}:00" for hour in config.allowed_hours)
        notes.append(f"Allowed hours applied: {hours}")
    return tuple(notes)


__all__ = [
    "group_trades_by_session",
    "replay_trading_sessions",
]
