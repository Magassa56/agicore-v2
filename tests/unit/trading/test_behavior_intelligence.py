"""Unit tests for offline behavior intelligence."""
from __future__ import annotations

from datetime import datetime

from agicore.trading.behavior_intelligence import analyze_behavior
from agicore.trading.behavior_models import (
    BehaviorPattern,
    BehaviorRecommendation,
    SessionBehaviorClass,
)
from agicore.trading.import_nt8_csv import NormalizedTrade
from agicore.trading.playbook_models import RiskRules, TraderProfile
from agicore.trading.session_replay import replay_trading_sessions
from agicore.trading.session_replay_models import SessionReplayConfig
from agicore.trading.strategy_dna_models import StrategyDNA, StrategyRiskRules, TradeDirection


def _trade(
    day: int,
    hour: int,
    minute: int,
    pnl: float,
    *,
    exit_minute: int | None = None,
) -> NormalizedTrade:
    exit_minute = minute + 1 if exit_minute is None else exit_minute
    return NormalizedTrade(
        entry_time=datetime(2026, 5, day, hour, minute),
        exit_time=datetime(2026, 5, day, hour, exit_minute),
        pnl=pnl,
    )


def test_analyze_behavior_classifies_disciplined_consistent_session() -> None:
    replay = replay_trading_sessions(
        [
            _trade(1, 9, 0, 100.0),
            _trade(1, 10, 0, -25.0),
            _trade(1, 11, 0, 75.0),
        ]
    )

    result = analyze_behavior(replay)

    assert SessionBehaviorClass.DISCIPLINED in result.classifications
    assert result.scores.discipline_score == 100
    assert result.scores.emotional_risk_score == 100
    assert result.scores.risk_escalation_score == 100
    assert result.recommendations == (BehaviorRecommendation.KEEP_CURRENT_RULES,)
    assert "High replay discipline score" in result.summary.strengths
    assert result.summary.probable_trader_profile == "Rule-following consistent trader"


def test_analyze_behavior_detects_high_risk_overtrading_and_revenge_patterns() -> None:
    trades = [
        _trade(1, 18, 0, 100.0),
        _trade(1, 18, 4, 120.0),
        _trade(1, 18, 8, -40.0),
        _trade(1, 18, 10, -260.0),
        _trade(1, 18, 12, -100.0),
        _trade(1, 20, 0, -30.0),
    ]
    replay = replay_trading_sessions(
        trades,
        config=SessionReplayConfig(
            max_trades_per_day=3,
            overtrading_threshold=3,
            max_daily_loss=250.0,
            max_unit_loss=200.0,
            allowed_hours=(18, 19),
            revenge_trade_window_minutes=5,
        ),
    )

    result = analyze_behavior(replay)

    assert SessionBehaviorClass.HIGH_RISK in result.classifications
    assert SessionBehaviorClass.OVERTRADING in result.classifications
    assert SessionBehaviorClass.REVENGE_TRADING_PROBABLE in result.classifications
    assert BehaviorPattern.SIZE_INCREASE_AFTER_LOSSES in result.patterns
    assert BehaviorPattern.TRADE_FREQUENCY_ACCELERATION in result.patterns
    assert BehaviorPattern.LOSS_AFTER_WINNING_STREAK in result.patterns
    assert BehaviorPattern.CONTINUED_AFTER_LIMIT_BREACH in result.patterns
    assert BehaviorPattern.LATE_TRADING_DEGRADATION in result.patterns
    assert BehaviorRecommendation.STOP_TRADING in result.recommendations
    assert BehaviorRecommendation.REDUCE_SIZE in result.recommendations
    assert BehaviorRecommendation.TAKE_BREAK in result.recommendations
    assert BehaviorRecommendation.LIMIT_MAX_TRADES in result.recommendations
    assert BehaviorRecommendation.AVOID_SPECIFIC_HOURS in result.recommendations
    assert result.scores.discipline_score < 100
    assert result.scores.emotional_risk_score < 100
    assert result.scores.risk_escalation_score < 100
    assert 20 in result.summary.dangerous_hours


def test_analyze_behavior_detects_disciplined_recovery_after_loss() -> None:
    replay = replay_trading_sessions(
        [
            _trade(1, 9, 0, -100.0),
            _trade(2, 9, 0, 150.0),
            _trade(2, 10, 0, 50.0),
        ]
    )

    result = analyze_behavior(replay)

    assert BehaviorPattern.DISCIPLINED_RECOVERY_AFTER_LOSS in result.patterns
    assert "Recovered after a loss without immediate escalation" in result.summary.strengths
    assert result.summary.favorable_context.startswith("Best observed start-hour context")


def test_analyze_behavior_marks_unstable_multi_session_results() -> None:
    replay = replay_trading_sessions(
        [
            _trade(1, 9, 0, 1000.0),
            _trade(2, 9, 0, -100.0),
            _trade(3, 9, 0, 50.0),
        ]
    )

    result = analyze_behavior(replay)

    assert SessionBehaviorClass.UNSTABLE in result.classifications
    assert result.scores.consistency_score < 100


def test_analyze_behavior_keeps_profile_and_strategy_context_notes() -> None:
    profile = TraderProfile(
        name="BAMA",
        style_detected="scalping",
        risk_rules=RiskRules(max_trades_per_day=1),
    )
    strategy = StrategyDNA(
        name="EMA20_Pullback_Pro",
        description="offline strategy",
        allowed_direction=TradeDirection.LONG_ONLY,
        allowed_hours=(18,),
        risk_rules=StrategyRiskRules(max_trades_per_day=1),
    )
    replay = replay_trading_sessions(
        [_trade(1, 18, 0, 100.0)],
        trader_profile=profile,
        strategy_dna=strategy,
    )

    result = analyze_behavior(replay, trader_profile=profile, strategy_dna=strategy)

    assert "Compared with trader profile: BAMA" in result.comparison_notes
    assert "Compared with strategy DNA: EMA20_Pullback_Pro" in result.comparison_notes
    assert "Behavior compared with trader profile: BAMA" in result.comparison_notes
    assert "Behavior compared with strategy DNA: EMA20_Pullback_Pro" in result.comparison_notes


def test_analyze_behavior_empty_replay_returns_stable_defaults() -> None:
    replay = replay_trading_sessions([])

    result = analyze_behavior(replay)

    assert result.classifications == (
        SessionBehaviorClass.DISCIPLINED,
        SessionBehaviorClass.CONSISTENT,
    )
    assert result.patterns == ()
    assert result.scores.discipline_score == 100
    assert result.scores.consistency_score == 100
    assert result.recommendations == (BehaviorRecommendation.KEEP_CURRENT_RULES,)
    assert result.summary.favorable_context == "Insufficient replay history"
