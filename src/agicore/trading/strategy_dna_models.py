"""Dataclasses for declared offline strategy DNA and variant results."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class TradeDirection(StrEnum):
    """Allowed direction for a declared strategy."""

    LONG_ONLY = "LONG_ONLY"
    SHORT_ONLY = "SHORT_ONLY"
    BOTH = "BOTH"


@dataclass(frozen=True)
class StrategyRiskRules:
    """Risk settings declared for a strategy."""

    max_daily_loss: float | None = None
    max_trades_per_day: int | None = None
    max_consecutive_losses: int | None = None
    risk_per_trade: float | None = None


@dataclass(frozen=True)
class StrategyDNA:
    """Declared strategy specification used by the offline lab."""

    name: str
    description: str
    allowed_direction: TradeDirection
    allowed_hours: tuple[int, ...] = ()
    trend_filter: str | None = None
    ema_filter: str | None = None
    entry_conditions: tuple[str, ...] = ()
    exit_conditions: tuple[str, ...] = ()
    risk_rules: StrategyRiskRules = field(default_factory=StrategyRiskRules)


@dataclass(frozen=True)
class StrategyVariant:
    """A testable strategy variant with simple parameter overrides."""

    name: str
    strategy_name: str
    allowed_hours: tuple[int, ...]
    profit_target: float | None = None
    stop_atr: float | None = None
    shorts_enabled: bool = True
    notes: str | None = None


@dataclass(frozen=True)
class StrategyVariantResult:
    """Comparable result for one offline strategy variant."""

    variant_name: str
    strategy_name: str
    profit_factor: float
    total_pnl: float
    win_rate: float
    average_trade: float
    max_drawdown: float
    trade_count: int


__all__ = [
    "StrategyDNA",
    "StrategyRiskRules",
    "StrategyVariant",
    "StrategyVariantResult",
    "TradeDirection",
]
