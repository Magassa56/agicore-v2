"""Unit tests for offline strategy DNA lab helpers."""
from __future__ import annotations

import pytest

from agicore.trading.strategy_dna import (
    build_strategy_variant,
    build_strategy_variants,
    compare_variant_results,
    define_strategy,
    evaluate_variant,
)
from agicore.trading.strategy_dna_models import StrategyRiskRules, TradeDirection


def test_define_strategy_normalizes_declared_strategy() -> None:
    strategy = define_strategy(
        name=" EMA20 Pullback Pro ",
        description=" Pullback into EMA20 with trend confirmation ",
        allowed_direction="BOTH",
        allowed_hours=[20, 18, 18, 19],
        trend_filter=" higher timeframe aligned ",
        ema_filter=" price above EMA20 ",
        entry_conditions=["pullback", " ", "reclaim trigger"],
        exit_conditions=("profit target", "ATR stop"),
        risk_rules=StrategyRiskRules(max_daily_loss=900.0, max_trades_per_day=10),
    )

    assert strategy.name == "EMA20 Pullback Pro"
    assert strategy.description == "Pullback into EMA20 with trend confirmation"
    assert strategy.allowed_direction == TradeDirection.BOTH
    assert strategy.allowed_hours == (18, 19, 20)
    assert strategy.trend_filter == "higher timeframe aligned"
    assert strategy.ema_filter == "price above EMA20"
    assert strategy.entry_conditions == ("pullback", "reclaim trigger")
    assert strategy.exit_conditions == ("profit target", "ATR stop")
    assert strategy.risk_rules.max_daily_loss == 900.0
    assert strategy.risk_rules.max_trades_per_day == 10


def test_define_strategy_validates_required_fields_and_hours() -> None:
    with pytest.raises(ValueError, match="name"):
        define_strategy(name=" ", description="x", allowed_direction=TradeDirection.LONG_ONLY)

    with pytest.raises(ValueError, match="description"):
        define_strategy(name="x", description=" ", allowed_direction=TradeDirection.LONG_ONLY)

    with pytest.raises(ValueError, match="Invalid trading hour"):
        define_strategy(
            name="x",
            description="x",
            allowed_direction=TradeDirection.LONG_ONLY,
            allowed_hours=[24],
        )


def test_build_strategy_variant_applies_overrides_and_disables_shorts_for_long_only() -> None:
    strategy = define_strategy(
        name="EMA20 Pullback Pro",
        description="Long only setup",
        allowed_direction=TradeDirection.LONG_ONLY,
        allowed_hours=[9, 10],
    )

    variant = build_strategy_variant(
        strategy,
        name=" morning PT500 ",
        allowed_hours=[10, 9],
        profit_target=500.0,
        stop_atr=1.5,
        shorts_enabled=True,
        notes=" test shorts override ",
    )

    assert variant.name == "morning PT500"
    assert variant.strategy_name == "EMA20 Pullback Pro"
    assert variant.allowed_hours == (9, 10)
    assert variant.profit_target == 500.0
    assert variant.stop_atr == 1.5
    assert variant.shorts_enabled is False
    assert variant.notes == "test shorts override"


def test_build_strategy_variants_creates_parameter_grid() -> None:
    strategy = define_strategy(
        name="EMA20 Pullback Pro",
        description="Bidirectional setup",
        allowed_direction=TradeDirection.BOTH,
        allowed_hours=[18, 19, 20],
    )

    variants = build_strategy_variants(
        strategy,
        allowed_hours_options=([18, 19], [20, 21]),
        profit_targets=(300.0, 500.0),
        stop_atrs=(1.0, 1.5),
        shorts_enabled_options=(True, False),
    )

    assert len(variants) == 16
    assert variants[0].allowed_hours == (18, 19)
    assert variants[0].profit_target == 300.0
    assert variants[0].stop_atr == 1.0
    assert variants[0].shorts_enabled is True
    assert variants[1].shorts_enabled is False


def test_evaluate_variant_computes_required_metrics() -> None:
    strategy = define_strategy(
        name="EMA20 Pullback Pro",
        description="Offline test",
        allowed_direction=TradeDirection.BOTH,
    )
    variant = build_strategy_variant(strategy, name="baseline")

    result = evaluate_variant(variant, [100.0, -50.0, 150.0, -25.0])

    assert result.variant_name == "baseline"
    assert result.strategy_name == "EMA20 Pullback Pro"
    assert result.profit_factor == pytest.approx(250.0 / 75.0)
    assert result.total_pnl == 175.0
    assert result.win_rate == 0.5
    assert result.average_trade == 43.75
    assert result.max_drawdown == 50.0
    assert result.trade_count == 4


def test_compare_variant_results_ranks_best_variant_first() -> None:
    strategy = define_strategy(
        name="EMA20 Pullback Pro",
        description="Offline test",
        allowed_direction=TradeDirection.BOTH,
    )
    weak = evaluate_variant(build_strategy_variant(strategy, name="weak"), [100.0, -100.0])
    strong = evaluate_variant(build_strategy_variant(strategy, name="strong"), [200.0, -50.0])
    flat = evaluate_variant(build_strategy_variant(strategy, name="flat"), [0.0, 0.0])

    ranked = compare_variant_results([weak, strong, flat])

    assert [result.variant_name for result in ranked] == ["strong", "weak", "flat"]


def test_evaluate_variant_handles_empty_and_no_loss_results() -> None:
    strategy = define_strategy(
        name="EMA20 Pullback Pro",
        description="Offline test",
        allowed_direction=TradeDirection.BOTH,
    )
    variant = build_strategy_variant(strategy, name="baseline")

    empty = evaluate_variant(variant, [])
    winner = evaluate_variant(variant, [100.0, 50.0])

    assert empty.profit_factor == 0.0
    assert empty.trade_count == 0
    assert empty.win_rate == 0.0
    assert winner.profit_factor == float("inf")
    assert winner.total_pnl == 150.0
