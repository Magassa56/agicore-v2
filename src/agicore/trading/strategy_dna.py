"""Offline strategy DNA lab helpers."""
from __future__ import annotations

from collections.abc import Iterable, Sequence

from .strategy_dna_models import (
    StrategyDNA,
    StrategyRiskRules,
    StrategyVariant,
    StrategyVariantResult,
    TradeDirection,
)


def define_strategy(
    *,
    name: str,
    description: str,
    allowed_direction: TradeDirection | str,
    allowed_hours: Sequence[int] = (),
    trend_filter: str | None = None,
    ema_filter: str | None = None,
    entry_conditions: Sequence[str] = (),
    exit_conditions: Sequence[str] = (),
    risk_rules: StrategyRiskRules | None = None,
) -> StrategyDNA:
    """Create a normalized declared strategy."""
    if not name.strip():
        raise ValueError("Strategy name is required")
    if not description.strip():
        raise ValueError("Strategy description is required")
    return StrategyDNA(
        name=name.strip(),
        description=description.strip(),
        allowed_direction=_coerce_direction(allowed_direction),
        allowed_hours=_clean_hours(allowed_hours),
        trend_filter=_clean_optional_text(trend_filter),
        ema_filter=_clean_optional_text(ema_filter),
        entry_conditions=_clean_texts(entry_conditions),
        exit_conditions=_clean_texts(exit_conditions),
        risk_rules=risk_rules or StrategyRiskRules(),
    )


def build_strategy_variant(
    strategy: StrategyDNA,
    *,
    name: str,
    allowed_hours: Sequence[int] | None = None,
    profit_target: float | None = None,
    stop_atr: float | None = None,
    shorts_enabled: bool | None = None,
    notes: str | None = None,
) -> StrategyVariant:
    """Create one testable variant from a declared strategy."""
    if not name.strip():
        raise ValueError("Strategy variant name is required")
    effective_shorts = strategy.allowed_direction in (TradeDirection.SHORT_ONLY, TradeDirection.BOTH)
    if shorts_enabled is not None:
        effective_shorts = bool(shorts_enabled)
    if strategy.allowed_direction == TradeDirection.LONG_ONLY:
        effective_shorts = False
    return StrategyVariant(
        name=name.strip(),
        strategy_name=strategy.name,
        allowed_hours=_clean_hours(allowed_hours if allowed_hours is not None else strategy.allowed_hours),
        profit_target=profit_target,
        stop_atr=stop_atr,
        shorts_enabled=effective_shorts,
        notes=_clean_optional_text(notes),
    )


def build_strategy_variants(
    strategy: StrategyDNA,
    *,
    allowed_hours_options: Sequence[Sequence[int]],
    profit_targets: Sequence[float],
    stop_atrs: Sequence[float],
    shorts_enabled_options: Sequence[bool] = (True, False),
) -> tuple[StrategyVariant, ...]:
    """Build a small grid of strategy variants."""
    variants: list[StrategyVariant] = []
    for hours in allowed_hours_options:
        for target in profit_targets:
            for stop_atr in stop_atrs:
                for shorts_enabled in shorts_enabled_options:
                    short_label = "shorts_on" if shorts_enabled else "shorts_off"
                    hour_label = "-".join(f"{hour:02d}" for hour in _clean_hours(hours)) or "all"
                    variants.append(
                        build_strategy_variant(
                            strategy,
                            name=f"{strategy.name} {hour_label} PT{target:g} ATR{stop_atr:g} {short_label}",
                            allowed_hours=hours,
                            profit_target=target,
                            stop_atr=stop_atr,
                            shorts_enabled=shorts_enabled,
                        )
                    )
    return tuple(variants)


def evaluate_variant(
    variant: StrategyVariant,
    trade_pnls: Sequence[float],
) -> StrategyVariantResult:
    """Evaluate one variant from offline trade PnL samples."""
    total_pnl = sum(trade_pnls)
    wins = [pnl for pnl in trade_pnls if pnl > 0]
    losses = [pnl for pnl in trade_pnls if pnl < 0]
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    trade_count = len(trade_pnls)
    return StrategyVariantResult(
        variant_name=variant.name,
        strategy_name=variant.strategy_name,
        profit_factor=_profit_factor(gross_profit, gross_loss, trade_count),
        total_pnl=total_pnl,
        win_rate=(len(wins) / trade_count) if trade_count else 0.0,
        average_trade=(total_pnl / trade_count) if trade_count else 0.0,
        max_drawdown=_max_drawdown(trade_pnls),
        trade_count=trade_count,
    )


def compare_variant_results(
    results: Iterable[StrategyVariantResult],
) -> tuple[StrategyVariantResult, ...]:
    """Rank variants by profit factor, then PnL, then drawdown."""
    return tuple(
        sorted(
            results,
            key=lambda result: (
                result.profit_factor,
                result.total_pnl,
                -result.max_drawdown,
                result.win_rate,
            ),
            reverse=True,
        )
    )


def _profit_factor(gross_profit: float, gross_loss: float, trade_count: int) -> float:
    if trade_count == 0:
        return 0.0
    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0
    return gross_profit / gross_loss


def _max_drawdown(trade_pnls: Sequence[float]) -> float:
    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for pnl in trade_pnls:
        equity += pnl
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, peak - equity)
    return max_drawdown


def _coerce_direction(value: TradeDirection | str) -> TradeDirection:
    if isinstance(value, TradeDirection):
        return value
    try:
        return TradeDirection(value)
    except ValueError as exc:
        raise ValueError(f"Invalid trade direction: {value}") from exc


def _clean_hours(hours: Sequence[int]) -> tuple[int, ...]:
    cleaned = tuple(sorted({int(hour) for hour in hours}))
    invalid = [hour for hour in cleaned if hour < 0 or hour > 23]
    if invalid:
        raise ValueError(f"Invalid trading hour(s): {invalid}")
    return cleaned


def _clean_texts(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(value.strip() for value in values if value.strip())


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


__all__ = [
    "build_strategy_variant",
    "build_strategy_variants",
    "compare_variant_results",
    "define_strategy",
    "evaluate_variant",
]
