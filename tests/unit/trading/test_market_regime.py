"""Unit tests for offline market regime detection."""
from __future__ import annotations

from datetime import datetime

from agicore.trading.behavior_intelligence import analyze_behavior
from agicore.trading.import_nt8_csv import NormalizedTrade
from agicore.trading.market_regime import (
    detect_market_regime,
    render_market_regime_markdown,
)
from agicore.trading.market_regime_models import (
    MarketRegime,
    SessionCondition,
    VolatilityRegime,
)
from agicore.trading.session_replay import replay_trading_sessions
from agicore.trading.session_replay_models import SessionReplayConfig
from agicore.trading.strategy_dna_models import StrategyDNA, TradeDirection


def test_detect_market_regime_classifies_ema_trending_up_pullback_context() -> None:
    analysis = detect_market_regime(
        prices=(100.0, 101.0, 102.0, 103.0, 104.0, 103.4, 103.8),
        ema_fast=(100.1, 100.8, 101.6, 102.5, 103.2, 103.4, 103.6),
        ema_slow=(99.8, 100.2, 100.9, 101.6, 102.3, 102.8, 103.1),
        atr=(1.0, 1.0, 1.1, 1.0, 1.1, 1.05, 1.15),
        ranges=(2.0, 2.1, 2.0, 2.2, 2.1, 2.0, 2.2),
        timestamps=(datetime(2026, 5, 18, 10, index) for index in range(7)),
    )

    assert analysis.primary_regime == MarketRegime.TRENDING_UP
    assert MarketRegime.TRENDING_UP in analysis.detected_regimes
    assert analysis.volatility == VolatilityRegime.NORMAL
    assert analysis.favorable_for_pullback_strategy is True
    assert analysis.dangerous_market is False
    assert analysis.context_quality_score >= 70


def test_detect_market_regime_prioritizes_breakout_and_news_risk() -> None:
    analysis = detect_market_regime(
        prices=(100.0, 100.5, 100.2, 100.7, 106.5),
        ema_fast=(100.0, 100.2, 100.3, 100.5, 103.0),
        ema_slow=(100.0, 100.1, 100.2, 100.3, 101.0),
        atr=(1.0, 1.1, 1.0, 1.1, 2.6),
        ranges=(2.0, 2.1, 1.9, 2.0, 5.2),
        volume=(1000.0, 950.0, 1050.0, 980.0, 2500.0),
    )

    assert analysis.primary_regime == MarketRegime.NEWS_RISK
    assert MarketRegime.BREAKOUT in analysis.detected_regimes
    assert MarketRegime.HIGH_VOLATILITY in analysis.detected_regimes
    assert analysis.volatility == VolatilityRegime.EXTREME
    assert analysis.dangerous_market is True
    assert any("news" in item.lower() for item in analysis.recommendations)


def test_detect_market_regime_detects_dead_market() -> None:
    analysis = detect_market_regime(
        prices=(100.00, 100.03, 100.02, 100.01, 100.04),
        ema_fast=(100.01, 100.01, 100.02, 100.02, 100.02),
        ema_slow=(100.00, 100.01, 100.01, 100.02, 100.02),
        atr=(1.0, 0.9, 0.85, 0.8, 0.55),
        ranges=(1.0, 0.9, 0.85, 0.8, 0.5),
        volume=(1000.0, 980.0, 950.0, 920.0, 650.0),
    )

    assert analysis.primary_regime == MarketRegime.DEAD_MARKET
    assert MarketRegime.LOW_VOLATILITY in analysis.detected_regimes
    assert analysis.session_condition == SessionCondition.DANGEROUS
    assert analysis.favorable_for_pullback_strategy is False
    assert any("dead market" in item.lower() for item in analysis.warnings)


def test_render_market_regime_markdown_contains_required_sections() -> None:
    analysis = detect_market_regime(
        prices=(100.0, 101.0, 102.0, 103.0),
        ema_fast=(100.2, 100.8, 101.6, 102.4),
        ema_slow=(99.8, 100.2, 100.9, 101.7),
        atr=(1.0, 1.0, 1.1, 1.1),
        ranges=(2.0, 2.1, 2.0, 2.2),
    )

    markdown = render_market_regime_markdown(analysis)

    assert "# Market Regime Detection" in markdown
    assert "## Regime detecte" in markdown
    assert "## Volatilite" in markdown
    assert "## Qualite du marche" in markdown
    assert "## Risque contexte" in markdown
    assert "## Compatibilite EMA20 pullback" in markdown
    assert "## Recommandations" in markdown
    assert "- Principal: TRENDING_UP" in markdown


def test_detect_market_regime_adds_optional_strategy_replay_behavior_context() -> None:
    strategy = StrategyDNA(
        name="EMA20_Pullback_Pro",
        description="offline setup",
        allowed_direction=TradeDirection.LONG_ONLY,
        allowed_hours=(9, 10),
    )
    replay = replay_trading_sessions(
        [
            NormalizedTrade(
                entry_time=datetime(2026, 5, 18, 20, 0),
                exit_time=datetime(2026, 5, 18, 20, 1),
                pnl=-300.0,
            ),
            NormalizedTrade(
                entry_time=datetime(2026, 5, 18, 20, 2),
                exit_time=datetime(2026, 5, 18, 20, 3),
                pnl=-100.0,
            ),
        ],
        config=SessionReplayConfig(
            max_trades_per_day=1,
            max_daily_loss=250.0,
            allowed_hours=(9, 10),
        ),
    )
    behavior = analyze_behavior(replay)

    analysis = detect_market_regime(
        prices=(100.0, 101.0, 102.0, 103.0, 104.0),
        ema_fast=(100.2, 100.8, 101.6, 102.5, 103.4),
        ema_slow=(99.8, 100.2, 100.9, 101.7, 102.6),
        atr=(1.0, 1.0, 1.1, 1.1, 1.2),
        ranges=(2.0, 2.1, 2.0, 2.2, 2.3),
        timestamps=(datetime(2026, 5, 18, 20, index) for index in range(5)),
        strategy_dna=strategy,
        session_replay_result=replay,
        behavior_result=behavior,
    )

    assert analysis.dangerous_market is True
    assert analysis.favorable_for_pullback_strategy is False
    assert "Strategy DNA loaded: EMA20_Pullback_Pro" in analysis.compatibility_notes
    assert any("Replay discipline score:" in item for item in analysis.compatibility_notes)
    assert any("Behavior emotional risk score:" in item for item in analysis.compatibility_notes)
    assert any("allowed hours" in item for item in analysis.warnings)


def test_detect_market_regime_handles_insufficient_price_history() -> None:
    analysis = detect_market_regime(prices=(100.0,))

    assert analysis.primary_regime == MarketRegime.DEAD_MARKET
    assert analysis.confidence == 40
    assert analysis.context_quality_score == 20
    assert analysis.dangerous_market is True
