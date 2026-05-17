"""Unit tests for the declared EMA20 Pullback Pro strategy DNA."""
from __future__ import annotations

from agicore.trading.ema20_pullback_dna import (
    build_ema20_pullback_variants,
    create_ema20_pullback_pro_dna,
)
from agicore.trading.strategy_dna_models import TradeDirection


def test_create_ema20_pullback_pro_dna_defaults_to_long_only() -> None:
    strategy = create_ema20_pullback_pro_dna()

    assert strategy.name == "EMA20_Pullback_Pro"
    assert strategy.allowed_direction == TradeDirection.LONG_ONLY
    assert strategy.allowed_hours == (18, 19, 20, 21)
    assert strategy.risk_rules.max_trades_per_day == 1


def test_create_ema20_pullback_pro_dna_contains_entry_and_exit_conditions() -> None:
    strategy = create_ema20_pullback_pro_dna(allowed_hours=(9, 10))
    entry_text = " ".join(strategy.entry_conditions)
    exit_text = " ".join(strategy.exit_conditions)

    assert strategy.allowed_hours == (9, 10)
    assert "EMA200" in strategy.trend_filter
    assert "EMA20" in strategy.ema_filter
    assert "EMA200" in entry_text
    assert "EMA20" in entry_text
    assert "Confirmation candle" in entry_text
    assert "MaxDistance" in entry_text
    assert "profit target" in exit_text
    assert "ATR stop" in exit_text
    assert "end of session" in exit_text


def test_build_ema20_pullback_variants_generates_recommended_grid() -> None:
    variants = build_ema20_pullback_variants(
        allowed_hours_options=((18, 19),),
        profit_targets=(100.0, 150.0, 200.0),
        max_distances=(2.0, 3.0, 5.0),
        atr_stops=(1.0, 1.5, 2.0),
    )

    assert len(variants) == 54
    assert {variant.profit_target for variant in variants} == {100.0, 150.0, 200.0}
    assert {variant.stop_atr for variant in variants} == {1.0, 1.5, 2.0}
    assert all(variant.strategy_name == "EMA20_Pullback_Pro" for variant in variants)
    assert all(variant.allowed_hours == (18, 19) for variant in variants)
    assert any("MaxDistance=2" in variant.notes for variant in variants)
    assert any("MaxDistance=3" in variant.notes for variant in variants)
    assert any("MaxDistance=5" in variant.notes for variant in variants)


def test_shorts_are_enabled_only_for_both_variants() -> None:
    variants = build_ema20_pullback_variants(
        allowed_hours_options=((18, 19),),
        profit_targets=(100.0,),
        max_distances=(2.0,),
        atr_stops=(1.0,),
    )

    long_only_variants = [variant for variant in variants if "direction=LONG_ONLY" in variant.notes]
    both_variants = [variant for variant in variants if "direction=BOTH" in variant.notes]

    assert len(long_only_variants) == 1
    assert len(both_variants) == 1
    assert all(variant.shorts_enabled is False for variant in long_only_variants)
    assert all(variant.shorts_enabled is True for variant in both_variants)
