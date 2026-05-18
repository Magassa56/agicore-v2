"""Unit tests for offline context scoring."""
from __future__ import annotations

from datetime import datetime

from agicore.trading.adaptive_memory_models import TraderMemoryProfile
from agicore.trading.behavior_intelligence import analyze_behavior
from agicore.trading.context_scoring import (
    build_context_decision,
    compute_trade_context_score,
    render_context_score_markdown,
)
from agicore.trading.context_scoring_models import (
    ContextScoreBreakdown,
    ContextScoringInput,
    TradeContextDecision,
)
from agicore.trading.import_nt8_csv import NormalizedTrade
from agicore.trading.market_regime import detect_market_regime
from agicore.trading.session_replay import replay_trading_sessions
from agicore.trading.session_replay_models import SessionReplayConfig
from agicore.trading.strategy_dna_models import StrategyDNA, TradeDirection
from agicore.trading.trade_journal import analyze_trade_journal
from agicore.trading.trade_journal_models import (
    JournalEmotion,
    JournalMistakeType,
    TradeJournalEntry,
)


def _trade(day: int, hour: int, minute: int, pnl: float) -> NormalizedTrade:
    return NormalizedTrade(
        entry_time=datetime(2026, 5, day, hour, minute),
        exit_time=datetime(2026, 5, day, hour, minute + 1),
        pnl=pnl,
    )


def _ema20_strategy() -> StrategyDNA:
    return StrategyDNA(
        name="EMA20_Pullback_Pro",
        description="offline pullback setup",
        allowed_direction=TradeDirection.BOTH,
        allowed_hours=(9, 10),
        ema_filter="price aligned with EMA20",
        entry_conditions=("pullback", "reclaim trigger"),
    )


def test_compute_trade_context_score_allows_strong_favorable_context() -> None:
    market = detect_market_regime(
        prices=(100.0, 101.0, 102.0, 103.0, 104.0, 103.4, 103.8),
        ema_fast=(100.1, 100.8, 101.6, 102.5, 103.2, 103.4, 103.6),
        ema_slow=(99.8, 100.2, 100.9, 101.6, 102.3, 102.8, 103.1),
        atr=(1.0, 1.0, 1.1, 1.0, 1.1, 1.05, 1.15),
        ranges=(2.0, 2.1, 2.0, 2.2, 2.1, 2.0, 2.2),
        timestamps=(datetime(2026, 5, 18, 10, index) for index in range(7)),
        strategy_dna=_ema20_strategy(),
    )
    replay = replay_trading_sessions(
        [_trade(18, 9, 0, 100.0), _trade(18, 10, 0, -20.0), _trade(18, 10, 5, 80.0)]
    )
    behavior = analyze_behavior(replay)
    memory = TraderMemoryProfile(
        sessions_count=8,
        average_discipline_score=88.0,
        average_emotional_risk_score=84.0,
        average_consistency_score=86.0,
        favorable_contexts=("EMA20 pullback trend day",),
    )

    result = compute_trade_context_score(
        ContextScoringInput(
            market_regime=market,
            behavior_result=behavior,
            session_replay_result=replay,
            memory_profile=memory,
            strategy_dna=_ema20_strategy(),
        )
    )

    assert result.global_score >= 80
    assert result.decision == TradeContextDecision.STRONG_TRADE_ALLOWED
    assert result.breakdown.market_score >= 80
    assert result.breakdown.strategy_regime_compatibility_score >= 90
    assert "Market is favorable for EMA20 pullback strategy." in result.favorable_factors
    assert result.no_trade_reasons == ()


def test_compute_trade_context_score_blocks_dangerous_unfavorable_context() -> None:
    market = detect_market_regime(
        prices=(100.0, 100.5, 100.2, 100.7, 106.5),
        ema_fast=(100.0, 100.2, 100.3, 100.5, 103.0),
        ema_slow=(100.0, 100.1, 100.2, 100.3, 101.0),
        atr=(1.0, 1.1, 1.0, 1.1, 2.6),
        ranges=(2.0, 2.1, 1.9, 2.0, 5.2),
        volume=(1000.0, 950.0, 1050.0, 980.0, 2500.0),
        strategy_dna=_ema20_strategy(),
    )
    replay = replay_trading_sessions(
        [
            _trade(18, 20, 0, 100.0),
            _trade(18, 20, 3, -260.0),
            _trade(18, 20, 5, -120.0),
        ],
        config=SessionReplayConfig(
            max_trades_per_day=2,
            max_daily_loss=250.0,
            max_unit_loss=200.0,
            allowed_hours=(9, 10),
            revenge_trade_window_minutes=5,
        ),
    )
    behavior = analyze_behavior(replay)
    journal = analyze_trade_journal(
        (
            TradeJournalEntry(
                trade_id="T1",
                session_date=datetime(2026, 5, 18).date(),
                instrument="NQ",
                direction="LONG",
                setup_name="EMA20 pullback",
                entry_reason="chased entry",
                exit_reason="stop",
                emotion_before=JournalEmotion.FEAR,
                emotion_during=JournalEmotion.TILT,
                emotion_after=JournalEmotion.FRUSTRATION,
                mistake_types=(JournalMistakeType.REVENGE_TRADING,),
                notes="revenge and tilt",
                followed_playbook=False,
                followed_risk_rules=False,
            ),
        )
    )

    result = compute_trade_context_score(
        market_regime=market,
        behavior_result=behavior,
        session_replay_result=replay,
        memory_profile=TraderMemoryProfile(
            sessions_count=5,
            average_discipline_score=55.0,
            average_emotional_risk_score=45.0,
            average_consistency_score=50.0,
            recurring_dangerous_hours=(20, 21),
        ),
        strategy_dna=_ema20_strategy(),
        journal_result=journal,
    )

    assert result.decision == TradeContextDecision.NO_TRADE
    assert result.global_score < 45
    assert any("Dangerous market" in item for item in result.no_trade_reasons)
    assert "Revenge trading probable." in result.risk_factors
    assert "Overtrading detected." in result.risk_factors
    assert any("Journal contains" in item for item in result.risk_factors)


def test_build_context_decision_maps_scores_and_hard_blocks() -> None:
    breakdown = ContextScoreBreakdown(
        market_score=90,
        behavior_score=90,
        discipline_score=90,
        memory_score=85,
        emotional_score=88,
        volatility_score=82,
        strategy_regime_compatibility_score=92,
    )

    assert (
        build_context_decision(global_score=86, breakdown=breakdown)
        == TradeContextDecision.STRONG_TRADE_ALLOWED
    )
    assert (
        build_context_decision(
            global_score=86,
            breakdown=breakdown,
            no_trade_reasons=("blocking reason",),
        )
        == TradeContextDecision.NO_TRADE
    )
    assert (
        build_context_decision(global_score=55, breakdown=breakdown)
        == TradeContextDecision.REDUCE_RISK
    )


def test_render_context_score_markdown_contains_required_sections() -> None:
    result = compute_trade_context_score()

    markdown = render_context_score_markdown(result)

    assert "# Context Scoring Engine" in markdown
    assert "## Score global" in markdown
    assert "## Decision AGIcore" in markdown
    assert "## Detail des scores" in markdown
    assert "## Facteurs favorables" in markdown
    assert "## Facteurs de risque" in markdown
    assert "## Recommandations" in markdown
    assert "## Compatibilite Strategy DNA / Market Regime" in markdown
    assert "- Score:" in markdown
