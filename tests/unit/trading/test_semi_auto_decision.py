"""Unit tests for offline semi-auto decision assistant."""
from __future__ import annotations

from datetime import datetime

from agicore.trading.adaptive_memory_models import TraderMemoryProfile
from agicore.trading.behavior_intelligence import analyze_behavior
from agicore.trading.context_scoring import compute_trade_context_score
from agicore.trading.context_scoring_models import ContextScoringInput
from agicore.trading.import_nt8_csv import NormalizedTrade
from agicore.trading.market_regime import detect_market_regime
from agicore.trading.semi_auto_decision import (
    build_semi_auto_decision,
    render_semi_auto_decision_markdown,
)
from agicore.trading.semi_auto_decision_models import (
    SemiAutoAction,
    SemiAutoDecision,
    SemiAutoDecisionInput,
)
from agicore.trading.session_coach_models import LiveSessionCoachResult, SessionCoachDecision
from agicore.trading.session_replay import replay_trading_sessions
from agicore.trading.session_replay_models import SessionReplayConfig
from agicore.trading.strategy_dna_models import StrategyDNA, TradeDirection


def _trade(day: int, hour: int, minute: int, pnl: float) -> NormalizedTrade:
    return NormalizedTrade(
        entry_time=datetime(2026, 5, day, hour, minute),
        exit_time=datetime(2026, 5, day, hour, minute + 1),
        pnl=pnl,
    )


def _strategy() -> StrategyDNA:
    return StrategyDNA(
        name="EMA20_Pullback_Pro",
        description="offline pullback setup",
        allowed_direction=TradeDirection.BOTH,
        allowed_hours=(9, 10),
        ema_filter="price aligned with EMA20",
        entry_conditions=("pullback",),
    )


def _strong_context():
    strategy = _strategy()
    market = detect_market_regime(
        prices=(100.0, 101.0, 102.0, 103.0, 104.0, 103.4, 103.8),
        ema_fast=(100.1, 100.8, 101.6, 102.5, 103.2, 103.4, 103.6),
        ema_slow=(99.8, 100.2, 100.9, 101.6, 102.3, 102.8, 103.1),
        atr=(1.0, 1.0, 1.1, 1.0, 1.1, 1.05, 1.15),
        ranges=(2.0, 2.1, 2.0, 2.2, 2.1, 2.0, 2.2),
        timestamps=(datetime(2026, 5, 18, 10, index) for index in range(7)),
        strategy_dna=strategy,
    )
    replay = replay_trading_sessions(
        [_trade(18, 9, 0, 100.0), _trade(18, 10, 0, -20.0), _trade(18, 10, 20, 80.0)]
    )
    behavior = analyze_behavior(replay)
    context = compute_trade_context_score(
        ContextScoringInput(
            market_regime=market,
            behavior_result=behavior,
            session_replay_result=replay,
            memory_profile=TraderMemoryProfile(
                sessions_count=6,
                average_discipline_score=90.0,
                average_emotional_risk_score=86.0,
                average_consistency_score=88.0,
                favorable_contexts=("EMA20 trend pullback",),
            ),
            strategy_dna=strategy,
        )
    )
    return context, market, behavior, strategy


def test_build_semi_auto_decision_approves_strong_context_preview_only() -> None:
    context, market, behavior, strategy = _strong_context()

    result = build_semi_auto_decision(
        SemiAutoDecisionInput(
            context_score=context,
            coach_decision=SessionCoachDecision.CONTINUE,
            market_regime=market,
            behavior_result=behavior,
            strategy_dna=strategy,
        )
    )

    assert result.decision == SemiAutoDecision.APPROVE_TRADE
    assert result.action == SemiAutoAction.PREPARE_ORDER_PREVIEW
    assert result.context_score >= 80
    assert "no order will be sent" in result.trader_message
    assert result.blocking_reasons == ()


def test_build_semi_auto_decision_blocks_no_trade_context() -> None:
    strategy = _strategy()
    market = detect_market_regime(
        prices=(100.0, 100.5, 100.2, 100.7, 106.5),
        ema_fast=(100.0, 100.2, 100.3, 100.5, 103.0),
        ema_slow=(100.0, 100.1, 100.2, 100.3, 101.0),
        atr=(1.0, 1.1, 1.0, 1.1, 2.6),
        ranges=(2.0, 2.1, 1.9, 2.0, 5.2),
        volume=(1000.0, 950.0, 1050.0, 980.0, 2500.0),
        strategy_dna=strategy,
    )
    replay = replay_trading_sessions(
        [_trade(18, 20, 0, 100.0), _trade(18, 20, 3, -260.0), _trade(18, 20, 5, -120.0)],
        config=SessionReplayConfig(
            max_trades_per_day=2,
            max_daily_loss=250.0,
            max_unit_loss=200.0,
            allowed_hours=(9, 10),
            revenge_trade_window_minutes=5,
        ),
    )
    behavior = analyze_behavior(replay)
    context = compute_trade_context_score(
        market_regime=market,
        behavior_result=behavior,
        session_replay_result=replay,
        strategy_dna=strategy,
    )

    result = build_semi_auto_decision(
        context_score=context,
        market_regime=market,
        behavior_result=behavior,
        strategy_dna=strategy,
    )

    assert result.decision == SemiAutoDecision.STOP_SESSION
    assert result.action == SemiAutoAction.RECOMMEND_STOP_SESSION
    assert any("NO_TRADE" in item for item in result.blocking_reasons)
    assert any("dangerous" in item.lower() for item in result.detected_risks)


def test_build_semi_auto_decision_stops_when_coach_stops() -> None:
    context, market, behavior, strategy = _strong_context()

    result = build_semi_auto_decision(
        context_score=context,
        coach_decision=SessionCoachDecision.STOP_TRADING,
        market_regime=market,
        behavior_result=behavior,
        strategy_dna=strategy,
    )

    assert result.decision == SemiAutoDecision.STOP_SESSION
    assert result.action == SemiAutoAction.RECOMMEND_STOP_SESSION
    assert "STOP_TRADING" in " ".join(result.blocking_reasons)


def test_build_semi_auto_decision_approves_reduced_risk_from_coach_output() -> None:
    context, market, behavior, strategy = _strong_context()
    coach = LiveSessionCoachResult(
        alerts=("minor volatility expansion",),
        recommendations=("reduce size",),
        stop_recommended=False,
        break_recommended=False,
        reduce_size=True,
        decision=SessionCoachDecision.REDUCE_RISK,
    )

    result = build_semi_auto_decision(
        context_score=context,
        coach_output=coach,
        market_regime=market,
        behavior_result=behavior,
        strategy_dna=strategy,
    )

    assert result.decision == SemiAutoDecision.APPROVE_REDUCED_RISK
    assert result.action == SemiAutoAction.REDUCE_SIZE
    assert any("Reduced size" in item for item in result.manual_confirmation_conditions)


def test_build_semi_auto_decision_requires_confirmation_for_memory_errors() -> None:
    context, market, behavior, strategy = _strong_context()

    result = build_semi_auto_decision(
        context_score=context,
        coach_decision=SessionCoachDecision.CONTINUE,
        market_regime=market,
        behavior_result=behavior,
        memory_profile=TraderMemoryProfile(
            sessions_count=5,
            average_discipline_score=80.0,
            average_emotional_risk_score=75.0,
            average_consistency_score=76.0,
            recurring_patterns=behavior.patterns or ("TRADE_FREQUENCY_ACCELERATION",),
        ),
        strategy_dna=strategy,
    )

    assert result.decision == SemiAutoDecision.REQUIRE_CONFIRMATION
    assert result.action == SemiAutoAction.REQUEST_MANUAL_CONFIRMATION
    assert any("memory" in item.lower() for item in result.manual_confirmation_conditions)


def test_render_semi_auto_decision_markdown_contains_required_sections() -> None:
    context, market, behavior, strategy = _strong_context()
    result = build_semi_auto_decision(
        context_score=context,
        market_regime=market,
        behavior_result=behavior,
        strategy_dna=strategy,
    )

    markdown = render_semi_auto_decision_markdown(result)

    assert "# Semi-Auto Decision Assistant" in markdown
    assert "## Decision finale" in markdown
    assert "## Action recommandee" in markdown
    assert "## Score contexte" in markdown
    assert "## Raisons d'approbation ou blocage" in markdown
    assert "## Risques detectes" in markdown
    assert "## Conditions de confirmation manuelle" in markdown
    assert "## Message trader clair" in markdown
