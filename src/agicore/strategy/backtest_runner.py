"""Strategy sandbox — minimal backtest loop.

Long-only, single-position. On each bar :
- ask the strategy for a Signal
- BUY  (when flat) → buy as many units as cash allows at the bar's close
- SELL (when long) → close the entire position at the bar's close
- HOLD → no change

The equity curve is marked-to-market on the bar's close. If a position is
still open at the last bar, it is force-closed at that bar's close.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

import structlog

from .metrics import compute_metrics
from .signal_models import Action, BacktestResult, OHLCV, Signal, TradeRecord

logger = structlog.get_logger(__name__)


class _StrategyProtocol(Protocol):
    """Minimal strategy interface for backtest runner."""

    name: str

    def on_bar(self, bar: OHLCV) -> Signal: ...


class BacktestRunner:
    """Stateless runner — call ``run(strategy, data)``."""

    def __init__(self, *, initial_capital: float = 10_000.0) -> None:
        if initial_capital <= 0:
            raise ValueError("initial_capital must be > 0")
        self._initial_capital = float(initial_capital)

    @property
    def initial_capital(self) -> float:
        return self._initial_capital

    def run(
        self,
        strategy: _StrategyProtocol,
        ohlcv: Iterable[OHLCV],
    ) -> BacktestResult:
        bars = list(ohlcv)
        signals: list[Signal] = []
        trades: list[TradeRecord] = []
        equity_curve: list[float] = [self._initial_capital]

        cash: float = self._initial_capital
        position_qty: float = 0.0
        entry_price: float = 0.0
        entry_time = None

        for bar in bars:
            sig = strategy.on_bar(bar)
            signals.append(sig)

            if sig.action == Action.BUY and position_qty == 0.0 and bar.close > 0:
                position_qty = cash / bar.close
                entry_price = bar.close
                entry_time = bar.timestamp
                cash = 0.0
            elif sig.action == Action.SELL and position_qty > 0.0:
                exit_value = position_qty * bar.close
                pnl = exit_value - (position_qty * entry_price)
                pnl_pct = pnl / (position_qty * entry_price) if entry_price > 0 else 0.0
                trades.append(
                    TradeRecord(
                        entry_time=entry_time,
                        entry_price=entry_price,
                        exit_time=bar.timestamp,
                        exit_price=bar.close,
                        quantity=position_qty,
                        pnl=pnl,
                        pnl_pct=pnl_pct,
                    )
                )
                cash = exit_value
                position_qty = 0.0
                entry_price = 0.0
                entry_time = None

            equity_curve.append(cash + position_qty * bar.close)

        # Force-close any open position at the last bar
        if position_qty > 0.0 and bars:
            last = bars[-1]
            exit_value = position_qty * last.close
            pnl = exit_value - (position_qty * entry_price)
            pnl_pct = pnl / (position_qty * entry_price) if entry_price > 0 else 0.0
            trades.append(
                TradeRecord(
                    entry_time=entry_time,
                    entry_price=entry_price,
                    exit_time=last.timestamp,
                    exit_price=last.close,
                    quantity=position_qty,
                    pnl=pnl,
                    pnl_pct=pnl_pct,
                )
            )
            cash = exit_value
            position_qty = 0.0
            # Do NOT re-append to equity_curve — already marked at this bar

        metrics = compute_metrics(
            trades, equity_curve, initial_equity=self._initial_capital
        )
        result = BacktestResult(
            strategy_name=strategy.name,
            bars_processed=len(bars),
            signals=signals,
            trades=trades,
            metrics=metrics,
            equity_curve=equity_curve,
        )
        logger.info(
            "backtest.completed",
            strategy=strategy.name,
            bars=len(bars),
            trades=len(trades),
            total_pnl=metrics.total_pnl,
            win_rate=metrics.win_rate,
            max_dd=metrics.max_drawdown,
            final_equity=metrics.final_equity,
        )
        return result


__all__ = ["BacktestRunner"]
