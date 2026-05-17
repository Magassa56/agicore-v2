"""Unit tests for offline trading session replay."""
from __future__ import annotations

from datetime import datetime

from agicore.trading.import_nt8_csv import NormalizedTrade
from agicore.trading.playbook_models import RiskRules, TraderProfile
from agicore.trading.session_replay import group_trades_by_session, replay_trading_sessions
from agicore.trading.session_replay_models import (
    ReplayEventType,
    ReplayViolationType,
    SessionReplayConfig,
)
from agicore.trading.strategy_dna_models import StrategyDNA, StrategyRiskRules, TradeDirection


def _trade(
    day: int,
    entry_hour: int,
    entry_minute: int,
    pnl: float,
    *,
    exit_minute: int | None = None,
) -> NormalizedTrade:
    exit_minute = entry_minute + 1 if exit_minute is None else exit_minute
    return NormalizedTrade(
        entry_time=datetime(2026, 5, day, entry_hour, entry_minute),
        exit_time=datetime(2026, 5, day, entry_hour, exit_minute),
        pnl=pnl,
    )


def test_group_trades_by_session_uses_exit_day() -> None:
    trades = [
        _trade(2, 10, 0, 50.0),
        _trade(1, 9, 0, 100.0),
        _trade(1, 10, 0, -25.0),
    ]

    grouped = group_trades_by_session(trades)

    assert tuple(grouped) == (datetime(2026, 5, 2).date(), datetime(2026, 5, 1).date())
    assert [trade.pnl for trade in grouped[datetime(2026, 5, 1).date()]] == [100.0, -25.0]


def test_replay_trading_sessions_computes_session_metrics_and_events() -> None:
    trades = [
        _trade(1, 9, 0, 100.0),
        _trade(1, 10, 0, -50.0),
        _trade(1, 11, 0, -25.0),
        _trade(1, 12, 0, 75.0),
    ]

    result = replay_trading_sessions(trades)
    session = result.sessions[0]
    event_types = [event.event_type for event in result.events]

    assert session.session_day == datetime(2026, 5, 1).date()
    assert session.total_pnl == 100.0
    assert session.trade_count == 4
    assert session.win_rate == 0.5
    assert session.largest_loss == -50.0
    assert session.largest_gain == 100.0
    assert session.max_loss_streak == 2
    assert session.start_time == datetime(2026, 5, 1, 9, 0)
    assert session.end_time == datetime(2026, 5, 1, 12, 1)
    assert session.discipline_score == 100
    assert event_types[0] == ReplayEventType.SESSION_STARTED
    assert event_types.count(ReplayEventType.TRADE_OPENED) == 4
    assert event_types.count(ReplayEventType.TRADE_CLOSED) == 4
    assert event_types[-1] == ReplayEventType.SESSION_ENDED


def test_replay_detects_risk_behaviors_and_recommends_stop() -> None:
    trades = [
        _trade(1, 18, 0, -250.0),
        _trade(1, 18, 2, -100.0),
        _trade(1, 20, 0, -40.0),
        _trade(1, 18, 10, 20.0),
    ]
    config = SessionReplayConfig(
        max_trades_per_day=3,
        overtrading_threshold=3,
        max_daily_loss=300.0,
        max_unit_loss=200.0,
        allowed_hours=(18, 19),
        revenge_trade_window_minutes=5,
    )

    result = replay_trading_sessions(trades, config=config)
    kinds = {violation.kind for violation in result.sessions[0].violations}
    event_types = [event.event_type for event in result.events]

    assert kinds == {
        ReplayViolationType.EXCESSIVE_UNIT_LOSS,
        ReplayViolationType.DAILY_LOSS_EXCEEDED,
        ReplayViolationType.REVENGE_TRADING_PROBABLE,
        ReplayViolationType.OUTSIDE_ALLOWED_HOURS,
        ReplayViolationType.OVERTRADING,
        ReplayViolationType.MAX_TRADES_PER_DAY,
    }
    assert ReplayEventType.RULE_VIOLATION in event_types
    assert ReplayEventType.SESSION_STOP_RECOMMENDED in event_types
    assert result.sessions[0].discipline_score < 100
    assert result.discipline_score == result.sessions[0].discipline_score


def test_replay_compares_with_trader_profile_risk_rules() -> None:
    trades = [
        _trade(1, 18, 0, -100.0),
        _trade(1, 18, 10, -80.0),
    ]
    profile = TraderProfile(
        name="BAMA",
        style_detected="scalping",
        risk_rules=RiskRules(max_daily_loss=150.0, max_trades_per_day=1),
    )

    result = replay_trading_sessions(trades, trader_profile=profile)
    kinds = {violation.kind for violation in result.sessions[0].violations}

    assert ReplayViolationType.DAILY_LOSS_EXCEEDED in kinds
    assert ReplayViolationType.MAX_TRADES_PER_DAY in kinds
    assert "Compared with trader profile: BAMA" in result.comparison_notes


def test_replay_compares_with_strategy_dna_allowed_hours_and_risk_rules() -> None:
    trades = [
        _trade(1, 18, 0, 100.0),
        _trade(1, 20, 0, -50.0),
    ]
    strategy = StrategyDNA(
        name="EMA20_Pullback_Pro",
        description="offline strategy",
        allowed_direction=TradeDirection.LONG_ONLY,
        allowed_hours=(18,),
        risk_rules=StrategyRiskRules(max_trades_per_day=1),
    )

    result = replay_trading_sessions(trades, strategy_dna=strategy)
    kinds = {violation.kind for violation in result.sessions[0].violations}

    assert ReplayViolationType.OUTSIDE_ALLOWED_HOURS in kinds
    assert ReplayViolationType.MAX_TRADES_PER_DAY in kinds
    assert "Compared with strategy DNA: EMA20_Pullback_Pro" in result.comparison_notes
    assert "Allowed hours applied: 18:00" in result.comparison_notes


def test_replay_empty_input_returns_empty_result_with_full_score() -> None:
    result = replay_trading_sessions([])

    assert result.sessions == ()
    assert result.events == ()
    assert result.discipline_score == 100
    assert result.comparison_notes == ()
