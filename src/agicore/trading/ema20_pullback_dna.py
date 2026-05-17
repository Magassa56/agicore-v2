"""Declared EMA20 Pullback Pro strategy DNA.

This module is offline-only. It documents the NinjaTrader strategy shape so
future analysis can compare realized trades against the declared playbook.
"""
from __future__ import annotations

from collections.abc import Sequence

from .strategy_dna import build_strategy_variant, define_strategy
from .strategy_dna_models import StrategyDNA, StrategyRiskRules, StrategyVariant, TradeDirection


DEFAULT_ALLOWED_HOURS = (18, 19, 20, 21)
RECOMMENDED_HOUR_SETS = (
    (9, 10, 11),
    (14, 15, 16),
    (18, 19, 20, 21),
)
RECOMMENDED_PROFIT_TARGETS = (100.0, 150.0, 200.0)
RECOMMENDED_MAX_DISTANCES = (2.0, 3.0, 5.0)
RECOMMENDED_ATR_STOPS = (1.0, 1.5, 2.0)


def create_ema20_pullback_pro_dna(
    *,
    allowed_hours: Sequence[int] = DEFAULT_ALLOWED_HOURS,
    direction: TradeDirection = TradeDirection.LONG_ONLY,
    max_trades_per_day: int = 1,
) -> StrategyDNA:
    """Create the declared EMA20 Pullback Pro strategy profile."""
    return define_strategy(
        name="EMA20_Pullback_Pro",
        description=(
            "Declarative EMA20 pullback strategy for offline comparison: trade with "
            "EMA200 trend alignment, wait for a controlled pullback into EMA20, "
            "confirm with a candle trigger, then exit by USD target, ATR stop, "
            "or end-of-session rule."
        ),
        allowed_direction=direction,
        allowed_hours=allowed_hours,
        trend_filter="EMA200 trend filter: longs only above EMA200, shorts only below EMA200.",
        ema_filter=(
            "EMA20 pullback filter: setup is valid only when price pulls back near EMA20 "
            "without exceeding the declared max distance."
        ),
        entry_conditions=(
            "EMA200 trend alignment is present.",
            "Price pulls back into EMA20.",
            "Confirmation candle closes back in the trade direction.",
            "Distance from entry trigger to EMA20 is within MaxDistance.",
        ),
        exit_conditions=(
            "Exit at declared profit target in USD.",
            "Exit at declared ATR stop.",
            "Exit before end of session.",
        ),
        risk_rules=StrategyRiskRules(max_trades_per_day=max_trades_per_day),
    )


def build_ema20_pullback_variants(
    *,
    allowed_hours_options: Sequence[Sequence[int]] = RECOMMENDED_HOUR_SETS,
    profit_targets: Sequence[float] = RECOMMENDED_PROFIT_TARGETS,
    max_distances: Sequence[float] = RECOMMENDED_MAX_DISTANCES,
    atr_stops: Sequence[float] = RECOMMENDED_ATR_STOPS,
) -> tuple[StrategyVariant, ...]:
    """Build recommended offline EMA20 Pullback Pro variants."""
    long_strategy = create_ema20_pullback_pro_dna(direction=TradeDirection.LONG_ONLY)
    both_strategy = create_ema20_pullback_pro_dna(direction=TradeDirection.BOTH)
    variants: list[StrategyVariant] = []

    for strategy in (long_strategy, both_strategy):
        for hours in allowed_hours_options:
            hour_label = "-".join(f"{int(hour):02d}" for hour in sorted(set(hours))) or "all"
            for profit_target in profit_targets:
                for max_distance in max_distances:
                    for atr_stop in atr_stops:
                        direction_label = strategy.allowed_direction.value
                        variants.append(
                            build_strategy_variant(
                                strategy,
                                name=(
                                    "EMA20_Pullback_Pro "
                                    f"{direction_label} H{hour_label} "
                                    f"PT{profit_target:g} MD{max_distance:g} ATR{atr_stop:g}"
                                ),
                                allowed_hours=hours,
                                profit_target=profit_target,
                                stop_atr=atr_stop,
                                shorts_enabled=strategy.allowed_direction == TradeDirection.BOTH,
                                notes=(
                                    f"direction={direction_label}; "
                                    f"MaxDistance={max_distance:g}; "
                                    "EMA200 trend filter; EMA20 pullback; candle confirmation"
                                ),
                            )
                        )
    return tuple(variants)


__all__ = [
    "DEFAULT_ALLOWED_HOURS",
    "RECOMMENDED_ATR_STOPS",
    "RECOMMENDED_HOUR_SETS",
    "RECOMMENDED_MAX_DISTANCES",
    "RECOMMENDED_PROFIT_TARGETS",
    "build_ema20_pullback_variants",
    "create_ema20_pullback_pro_dna",
]
