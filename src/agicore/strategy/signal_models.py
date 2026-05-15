"""Strategy sandbox — data models.

Pydantic DTOs for the offline trading sandbox. No broker, no live data —
purely deterministic structures shared between the strategy, the runner,
and the metrics module.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Action(str, Enum):
    """Canonical signal action."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class OHLCV(BaseModel):
    """One OHLCV bar. Source-agnostic — provided by mock dataset."""
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    open: float = Field(..., ge=0)
    high: float = Field(..., ge=0)
    low: float = Field(..., ge=0)
    close: float = Field(..., ge=0)
    volume: float = Field(default=0.0, ge=0)


class Signal(BaseModel):
    """Output of a strategy on a single bar."""
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    action: Action
    price: float = Field(..., ge=0)
    reason: str = Field(default="", max_length=128)


class TradeRecord(BaseModel):
    """Closed round-trip trade. Long-only in this sandbox."""
    model_config = ConfigDict(frozen=True)

    entry_time: datetime
    entry_price: float = Field(..., ge=0)
    exit_time: datetime
    exit_price: float = Field(..., ge=0)
    quantity: float = Field(..., gt=0)
    pnl: float
    pnl_pct: float


class StrategyMetrics(BaseModel):
    """Aggregated performance metrics for a backtest run."""
    model_config = ConfigDict(frozen=True)

    total_trades: int = Field(..., ge=0)
    wins: int = Field(..., ge=0)
    losses: int = Field(..., ge=0)
    win_rate: float = Field(..., ge=0, le=1)
    total_pnl: float
    max_drawdown: float = Field(..., ge=0, le=1)
    final_equity: float = Field(..., ge=0)
    initial_equity: float = Field(..., gt=0)


class BacktestResult(BaseModel):
    """Full output of a single backtest run."""
    model_config = ConfigDict(frozen=True)

    strategy_name: str
    bars_processed: int = Field(..., ge=0)
    signals: list[Signal]
    trades: list[TradeRecord]
    metrics: StrategyMetrics
    equity_curve: list[float]


__all__ = [
    "Action",
    "OHLCV",
    "Signal",
    "TradeRecord",
    "StrategyMetrics",
    "BacktestResult",
]
