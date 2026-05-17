"""Unit tests for offline daily trading reports."""
from __future__ import annotations

from datetime import datetime

from agicore.trading.adaptive_memory import update_trader_memory
from agicore.trading.behavior_intelligence import analyze_behavior
from agicore.trading.daily_report import (
    build_daily_trading_report,
    render_daily_trading_report_markdown,
)
from agicore.trading.import_nt8_csv import NormalizedTrade
from agicore.trading.playbook_models import RiskRules, TraderProfile
from agicore.trading.session_replay import replay_trading_sessions
from agicore.trading.session_replay_models import SessionReplayConfig
from agicore.trading.strategy_dna_models import StrategyDNA, StrategyRiskRules, TradeDirection


def _trade(day: int, hour: int, minute: int, pnl: float) -> NormalizedTrade:
    return NormalizedTrade(
        entry_time=datetime(2026, 5, day, hour, minute),
        exit_time=datetime(2026, 5, day, hour, minute + 1),
        pnl=pnl,
    )


def test_build_daily_trading_report_aggregates_session_behavior_and_memory() -> None:
    report_date = datetime(2026, 5, 1).date()
    replay = replay_trading_sessions(
        [
            _trade(1, 18, 0, 100.0),
            _trade(1, 18, 4, -250.0),
            _trade(1, 20, 0, -50.0),
        ],
        config=SessionReplayConfig(
            max_trades_per_day=2,
            overtrading_threshold=2,
            max_daily_loss=200.0,
            max_unit_loss=200.0,
            allowed_hours=(18, 19),
        ),
    )
    behavior = analyze_behavior(replay)
    memory = update_trader_memory(behavior)
    trader_profile = TraderProfile(
        name="BAMA",
        style_detected="scalping",
        risk_rules=RiskRules(max_daily_loss=150.0, max_trades_per_day=2),
    )
    strategy = StrategyDNA(
        name="EMA20_Pullback_Pro",
        description="offline strategy",
        allowed_direction=TradeDirection.LONG_ONLY,
        allowed_hours=(18,),
        risk_rules=StrategyRiskRules(max_trades_per_day=2),
    )

    report = build_daily_trading_report(
        report_date=report_date,
        replay_result=replay,
        behavior_result=behavior,
        memory_profile=memory,
        trader_profile=trader_profile,
        strategy_dna=strategy,
    )

    assert report.report_date == report_date
    assert report.total_pnl == -200.0
    assert report.trade_count == 3
    assert report.win_rate == 1 / 3
    assert report.discipline_score < 100
    assert report.emotional_risk_score < 100
    assert "OVERTRADING" in report.behavior_classifications
    assert any("DAILY_LOSS_EXCEEDED" in item for item in report.rule_violations)
    assert any("STRENGTHEN_MAX_TRADES_LIMIT" in item for item in report.recommendations)
    assert any("Historical sessions: 1" in item for item in report.memory_comparison)
    assert any("Max daily loss 150.00: VIOLATION" in item for item in report.playbook_alignment)
    assert any("Strategy max trades/day 2: VIOLATION" in item for item in report.strategy_alignment)


def test_render_daily_trading_report_markdown_contains_required_sections() -> None:
    report_date = datetime(2026, 5, 1).date()
    replay = replay_trading_sessions([_trade(1, 9, 0, 100.0)])
    behavior = analyze_behavior(replay)
    report = build_daily_trading_report(
        report_date=report_date,
        replay_result=replay,
        behavior_result=behavior,
    )

    markdown = render_daily_trading_report_markdown(report)

    assert "# Daily Trading Report - 2026-05-01" in markdown
    assert "## Resume du jour" in markdown
    assert "## Resultats trading" in markdown
    assert "## Discipline & comportement" in markdown
    assert "## Violations detectees" in markdown
    assert "## Recommandations AGIcore" in markdown
    assert "## Comparaison avec memoire historique" in markdown
    assert "## Respect playbook / Strategy DNA" in markdown
    assert "## Plan d'action pour la prochaine session" in markdown
    assert "- PnL total: 100.00" in markdown
    assert "- No historical memory available" in markdown
    assert "- Playbook: No trader playbook provided" in markdown
    assert "- Strategy DNA: No Strategy DNA provided" in markdown


def test_build_daily_trading_report_handles_missing_session_date() -> None:
    report_date = datetime(2026, 5, 2).date()
    replay = replay_trading_sessions([_trade(1, 9, 0, 100.0)])
    behavior = analyze_behavior(replay)

    report = build_daily_trading_report(
        report_date=report_date,
        replay_result=replay,
        behavior_result=behavior,
    )

    assert report.session_summary == "No replayed session for this date"
    assert report.total_pnl == 0.0
    assert report.trade_count == 0
    assert report.win_rate == 0.0
    assert report.rule_violations == ("No rule violations detected",)


def test_daily_report_action_plan_reflects_risky_recommendations() -> None:
    report_date = datetime(2026, 5, 1).date()
    replay = replay_trading_sessions(
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
    behavior = analyze_behavior(replay)
    report = build_daily_trading_report(
        report_date=report_date,
        replay_result=replay,
        behavior_result=behavior,
    )

    assert "Respect mandatory stop/break rules before the next entry" in report.next_session_action_plan
    assert "Set a hard maximum trade count before the session starts" in report.next_session_action_plan
    assert "Block or avoid recurring dangerous hours" in report.next_session_action_plan
    assert "Reduce size until risk escalation disappears from replay" in report.next_session_action_plan
    assert "Review every rule violation before the next session" in report.next_session_action_plan
