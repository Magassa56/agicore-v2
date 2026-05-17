"""Unit tests for the offline AGIcore session coach."""
from __future__ import annotations

from datetime import datetime

from agicore.trading.adaptive_memory import update_trader_memory
from agicore.trading.behavior_intelligence import analyze_behavior
from agicore.trading.daily_report import build_daily_trading_report
from agicore.trading.import_nt8_csv import NormalizedTrade
from agicore.trading.playbook_models import RiskRules, TraderProfile
from agicore.trading.session_coach import (
    build_post_session_review,
    build_pre_session_checklist,
    evaluate_live_session_state,
)
from agicore.trading.session_coach_models import SessionCoachDecision, SessionRiskLevel
from agicore.trading.session_replay import replay_trading_sessions
from agicore.trading.session_replay_models import SessionReplayConfig
from agicore.trading.strategy_dna_models import StrategyDNA, StrategyRiskRules, TradeDirection


def _trade(day: int, hour: int, minute: int, pnl: float) -> NormalizedTrade:
    return NormalizedTrade(
        entry_time=datetime(2026, 5, day, hour, minute),
        exit_time=datetime(2026, 5, day, hour, minute + 1),
        pnl=pnl,
    )


def _risky_replay():
    return replay_trading_sessions(
        [
            _trade(1, 18, 0, -260.0),
            _trade(1, 18, 2, -100.0),
            _trade(1, 20, 0, -30.0),
        ],
        config=SessionReplayConfig(
            max_trades_per_day=2,
            overtrading_threshold=2,
            max_daily_loss=250.0,
            max_unit_loss=200.0,
            allowed_hours=(18, 19),
            revenge_trade_window_minutes=5,
        ),
    )


def test_build_pre_session_checklist_uses_memory_playbook_and_strategy_limits() -> None:
    replay = _risky_replay()
    behavior = analyze_behavior(replay)
    memory = update_trader_memory(behavior)
    trader_profile = TraderProfile(
        name="BAMA",
        style_detected="scalping",
        entry_conditions=("EMA20 pullback",),
        exit_conditions=("Profit target or ATR stop",),
        forbidden_conditions=("No revenge trade",),
        risk_rules=RiskRules(max_daily_loss=200.0, max_trades_per_day=2),
    )
    strategy = StrategyDNA(
        name="EMA20_Pullback_Pro",
        description="offline strategy",
        allowed_direction=TradeDirection.LONG_ONLY,
        allowed_hours=(18, 19),
        risk_rules=StrategyRiskRules(max_daily_loss=250.0, max_trades_per_day=1),
        entry_conditions=("Trend above EMA200",),
        exit_conditions=("End of session",),
    )

    checklist = build_pre_session_checklist(
        memory_profile=memory,
        trader_profile=trader_profile,
        strategy_dna=strategy,
    )

    assert checklist.recommended_risk_level in {SessionRiskLevel.HIGH, SessionRiskLevel.CRITICAL}
    assert checklist.decision in {SessionCoachDecision.REDUCE_RISK, SessionCoachDecision.REVIEW_REQUIRED}
    assert 20 in checklist.dangerous_hours
    assert "EMA20 pullback" in checklist.playbook_rules
    assert "Trend above EMA200" in checklist.playbook_rules
    assert "Trader max daily loss: 200.00" in checklist.daily_limits
    assert "Strategy max trades/day: 1" in checklist.daily_limits
    assert any("pause" in item.lower() or "risk" in item.lower() for item in checklist.emotional_reminders)


def test_evaluate_live_session_state_detects_stop_break_and_reduce_size() -> None:
    replay = _risky_replay()
    behavior = analyze_behavior(replay)

    result = evaluate_live_session_state(
        replay_result=replay,
        behavior_result=behavior,
        trader_profile=TraderProfile(
            name="BAMA",
            style_detected="scalping",
            risk_rules=RiskRules(max_daily_loss=250.0, max_trades_per_day=2),
        ),
    )

    assert result.decision == SessionCoachDecision.STOP_TRADING
    assert result.stop_recommended is True
    assert result.break_recommended is True
    assert result.reduce_size is True
    assert any("Revenge trading" in item for item in result.alerts)
    assert any("Overtrading" in item for item in result.alerts)
    assert any("Reduce size" in item for item in result.recommendations)


def test_build_post_session_review_includes_errors_strengths_and_memory_comparison() -> None:
    replay = _risky_replay()
    behavior = analyze_behavior(replay)
    memory = update_trader_memory(behavior)
    daily_report = build_daily_trading_report(
        report_date=datetime(2026, 5, 1).date(),
        replay_result=replay,
        behavior_result=behavior,
        memory_profile=memory,
    )

    review = build_post_session_review(
        replay_result=replay,
        behavior_result=behavior,
        memory_profile=memory,
        daily_report=daily_report,
    )

    assert review.decision in {SessionCoachDecision.STOP_TRADING, SessionCoachDecision.REVIEW_REQUIRED}
    assert review.session_score < 100
    assert "2026-05-01 finished with PnL -390.00" in review.discipline_summary
    assert any("DAILY_LOSS_EXCEEDED" in item for item in review.violated_rules)
    assert any("revenge" in item.lower() for item in review.detected_errors)
    assert any("Discipline delta" in item or "Historical sessions" in item for item in review.memory_comparison)
    assert review.improvement_areas
    assert review.strengths


def test_clean_session_coach_allows_continue() -> None:
    replay = replay_trading_sessions([_trade(2, 9, 0, 100.0)])
    behavior = analyze_behavior(replay)

    live = evaluate_live_session_state(replay_result=replay, behavior_result=behavior)
    review = build_post_session_review(replay_result=replay, behavior_result=behavior)
    checklist = build_pre_session_checklist()

    assert live.decision == SessionCoachDecision.CONTINUE
    assert live.stop_recommended is False
    assert review.decision == SessionCoachDecision.CONTINUE
    assert checklist.decision == SessionCoachDecision.CONTINUE
    assert checklist.recommended_risk_level == SessionRiskLevel.LOW
