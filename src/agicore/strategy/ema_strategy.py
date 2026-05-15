"""EMA crossover strategy — minimal long-only sandbox implementation.

Bullish cross  (fast crosses above slow) → BUY  (open long if flat)
Bearish cross  (fast crosses below slow) → SELL (close long if open)
Otherwise                                → HOLD

No look-ahead bias : decision uses EMAs computed up to and including the
current bar's close, signal applies at the same bar's close. The backtest
runner uses that same close for execution to keep accounting trivial.
"""
from __future__ import annotations

import structlog

from .signal_models import Action, OHLCV, Signal

logger = structlog.get_logger(__name__)


class EMACrossoverStrategy:
    """Long-only EMA crossover.

    Parameters
    ----------
    fast_period : int
        Period of the fast EMA. Must be >= 1 and < slow_period.
    slow_period : int
        Period of the slow EMA. Must be > fast_period.
    name : str
        Optional override for the strategy name (used in BacktestResult).
    """

    DEFAULT_NAME: str = "ema_crossover"

    def __init__(
        self,
        *,
        fast_period: int = 12,
        slow_period: int = 26,
        name: str | None = None,
    ) -> None:
        if fast_period < 1 or slow_period < 1:
            raise ValueError("periods must be >= 1")
        if fast_period >= slow_period:
            raise ValueError("fast_period must be < slow_period")

        self.fast_period = fast_period
        self.slow_period = slow_period
        self.name = name or f"{self.DEFAULT_NAME}({fast_period},{slow_period})"

        self._closes: list[float] = []
        self._fast_ema: float | None = None
        self._slow_ema: float | None = None
        self._prev_fast_ema: float | None = None
        self._prev_slow_ema: float | None = None
        self._position_open: bool = False

    # ------------------------------------------------------------------ State
    @property
    def position_open(self) -> bool:
        return self._position_open

    @property
    def fast_ema(self) -> float | None:
        return self._fast_ema

    @property
    def slow_ema(self) -> float | None:
        return self._slow_ema

    def reset(self) -> None:
        """Clear all state. Useful between backtest runs."""
        self._closes.clear()
        self._fast_ema = None
        self._slow_ema = None
        self._prev_fast_ema = None
        self._prev_slow_ema = None
        self._position_open = False

    # ------------------------------------------------------------------ Step
    def on_bar(self, bar: OHLCV) -> Signal:
        """Process one bar and return a Signal."""
        self._closes.append(bar.close)

        new_fast = self._step_ema(self._fast_ema, self.fast_period)
        new_slow = self._step_ema(self._slow_ema, self.slow_period)

        action = Action.HOLD
        reason = "warming_up"

        if new_fast is not None and new_slow is not None:
            if self._prev_fast_ema is not None and self._prev_slow_ema is not None:
                bullish = (
                    self._prev_fast_ema <= self._prev_slow_ema
                    and new_fast > new_slow
                )
                bearish = (
                    self._prev_fast_ema >= self._prev_slow_ema
                    and new_fast < new_slow
                )
                if bullish and not self._position_open:
                    action = Action.BUY
                    reason = "bullish_cross"
                    self._position_open = True
                elif bearish and self._position_open:
                    action = Action.SELL
                    reason = "bearish_cross"
                    self._position_open = False
                else:
                    reason = "no_cross"
            else:
                reason = "no_cross"

            self._prev_fast_ema = new_fast
            self._prev_slow_ema = new_slow

        self._fast_ema = new_fast
        self._slow_ema = new_slow

        signal = Signal(
            timestamp=bar.timestamp,
            action=action,
            price=bar.close,
            reason=reason,
        )
        if action != Action.HOLD:
            logger.info(
                "ema_strategy.signal",
                action=action.value,
                price=bar.close,
                fast=new_fast,
                slow=new_slow,
                reason=reason,
            )
        return signal

    # ------------------------------------------------------------------ EMA
    def _step_ema(self, prev_ema: float | None, period: int) -> float | None:
        """Standard EMA with SMA seed at index ``period``."""
        n = len(self._closes)
        if n < period:
            return None
        if n == period or prev_ema is None:
            # SMA seed
            return sum(self._closes[-period:]) / period
        alpha = 2.0 / (period + 1.0)
        return alpha * self._closes[-1] + (1.0 - alpha) * prev_ema


__all__ = ["EMACrossoverStrategy"]
