"""Exact incremental equivalents of the frozen EMA20 and MACD prefix evaluators.

The tick-grid lane keeps integers over factored common denominators. It performs
only integer operations, not a Fraction GCD at every recurrence. Native values
are fully reduced Fractions on demand. General rational inputs use Fraction;
invalid histories delegate to the unchanged reference for its error precedence.
No price field other than an actually closed observation's Close is read.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from fractions import Fraction

from . import ema20_pullback_v2 as ema_reference
from . import ema_pullback_entry_confirmation_v2 as macd_reference


def _reduced(n: int, d: int, factors: tuple[tuple[int, int], ...]) -> Fraction:
    """Reduce an integer ratio whose positive denominator is fully factored.

    Binary search finds the exact p-adic valuation, capped by the denominator's
    exponent. After removing every common prime power, numerator and denominator
    are coprime. The runtime's _from_coprime_ints avoids repeating a large GCD;
    runtimes without that constructor use the ordinary exact Fraction constructor.
    This is construction of a proven reduced value, never rebinding Fraction.
    """
    whole, remainder = divmod(n, d)
    if remainder == 0:
        return Fraction(whole)
    for prime, exponent in factors:
        if not exponent or n % prime:
            continue
        low, high = 1, exponent
        while low < high:
            middle = (low + high + 1) // 2
            if n % (prime ** middle) == 0:
                low = middle
            else:
                high = middle - 1
        common = prime ** low
        n //= common
        d //= common
    constructor = getattr(Fraction, "_from_coprime_ints", Fraction)
    return constructor(n, d)


@dataclass
class _TickLane:
    """Shared exact MACD denominator 4*1755**i; EMA20 80*21**(i-19)."""

    index: int = -1
    ticks_sum: int = 0
    ema_n: int | None = None
    ema_d: int = 80
    denominator: int = 4
    fast: int = 0
    slow: int = 0
    signal: int = 0
    previous_line: tuple[int, int, int] | None = None
    previous_hist: tuple[int, int, int] | None = None

    def append(self, ticks: int) -> None:
        self.index += 1
        i = self.index
        # Preserve k-1 reference before processing Close[k]. Materialize lazily.
        if i < 20:
            self.ticks_sum += ticks
            if i == 19:
                self.ema_n = self.ticks_sum
        else:
            self.ema_n = 19 * self.ema_n + 2 * ticks * (self.ema_d // 4)
            self.ema_d *= 21
        if i == 0:
            self.fast = self.slow = ticks
            return
        self.previous_line = (self.fast - self.slow, self.denominator, i - 1)
        self.previous_hist = (
            self.fast - self.slow - self.signal, self.denominator, i - 1
        )
        # 1755/13=135, 1755/27=65, 1755/5=351. All divisions exact.
        price_scale = self.denominator // 4
        self.fast = 1485 * self.fast + 270 * ticks * price_scale
        self.slow = 1625 * self.slow + 130 * ticks * price_scale
        line = self.fast - self.slow
        assert line % 5 == 0
        self.signal = 1404 * self.signal + line // 5
        self.denominator *= 1755

    @staticmethod
    def value(n: int, d: int, i: int) -> Fraction:
        return _reduced(n, d, ((2, 2), (3, 3 * i), (5, i), (13, i)))

    def ema(self) -> Fraction | None:
        if self.ema_n is None:
            return None
        steps = self.index - 19
        return _reduced(self.ema_n, self.ema_d, ((2, 4), (5, 1), (3, steps), (7, steps)))

    def values(self) -> tuple:
        i, d = self.index, self.denominator
        return (
            self.value(self.fast, d, i), self.value(self.slow, d, i),
            self.value(self.fast - self.slow, d, i), self.value(self.signal, d, i),
            self.value(self.fast - self.slow - self.signal, d, i),
            None if self.previous_line is None else self.value(*self.previous_line),
            None if self.previous_hist is None else self.value(*self.previous_hist),
        )


@dataclass
class _FractionLane:
    index: int = -1
    seed_sum: Fraction = Fraction()
    ema: Fraction | None = None
    fast: Fraction | None = None
    slow: Fraction | None = None
    signal: Fraction = Fraction()
    previous_macd: Fraction | None = None
    previous_histogram: Fraction | None = None

    def append(self, close: Fraction) -> None:
        self.index += 1
        if self.index < 20:
            self.seed_sum += close
            if self.index == 19:
                self.ema = self.seed_sum / 20
        else:
            self.ema = (2 * close + 19 * self.ema) / 21
        if self.index == 0:
            self.fast = self.slow = close
        else:
            self.previous_macd = self.fast - self.slow
            self.previous_histogram = self.previous_macd - self.signal
            self.fast += Fraction(2, 13) * (close - self.fast)
            self.slow += Fraction(2, 27) * (close - self.slow)
            self.signal += Fraction(1, 5) * (self.fast - self.slow - self.signal)

    def values(self) -> tuple:
        line = self.fast - self.slow
        return (self.fast, self.slow, line, self.signal, line - self.signal,
                self.previous_macd, self.previous_histogram)


class ExactIncrementalIndicatorsV1:
    """Append actual closed bars; query the current or prior exact prefix.

    For a valid contiguous history, queries match the frozen evaluation records
    exactly. Invalid/missing/unclosed/clock-inconsistent histories are retained
    and queried through the frozen functions, preserving their status/error
    precedence, including EMA's no-read warmup behavior. No invalid seed restart.
    """

    def __init__(self) -> None:
        self.bars: dict[int, ema_reference.EMA20PullbackBarV2] = {}
        self.index = -1
        self.lane: _TickLane | _FractionLane = _TickLane()
        self.valid = True
        self.previous_ema: ema_reference.EMA20EvaluationV2 | None = None
        self._macd_cache = None
        self._previous_raw_ema: tuple | None = None

    def append_closed_bar(self, bar: ema_reference.EMA20PullbackBarV2) -> None:
        """Store one known Close; no Open/High/Low or future bar is accessed."""
        index = bar.bar_index
        previous = self.bars.get(self.index)
        close = ema_reference._exact_price(bar.close)
        sequential = index == self.index + 1
        self.valid = self.valid and sequential and bar.is_closed and close is not None and (
            previous is None or bar.timestamp_utc > previous.timestamp_utc
        )
        if self.valid:
            if isinstance(self.lane, _TickLane):
                self._previous_raw_ema = (
                    self.lane.ema_n, self.lane.ema_d, self.lane.index
                )
                ticks = close * 4
                if ticks.denominator != 1:
                    self.previous_ema = self.ema20() if self.index >= 0 else None
                    lane = _FractionLane(index=self.lane.index)
                    lane.seed_sum = Fraction(self.lane.ticks_sum, 4)
                    lane.ema = self.lane.ema()
                    if self.index >= 0:
                        lane.fast, lane.slow, _, lane.signal, _, _, _ = self.lane.values()
                    self.lane = lane
            else:
                self.previous_ema = self.ema20()
            if isinstance(self.lane, _TickLane):
                self.lane.append(ticks.numerator)
            else:
                self.lane.append(close)
        self.bars[index] = bar
        self.index = index
        self._macd_cache = None

    def ema20(self, *, previous: bool = False, before_timestamp: datetime | None = None):
        """Return the identical EMA20EvaluationV2 with current/prior availability."""
        index = self.index - int(previous)
        if index < 0:
            return ema_reference.evaluate_ema20_v2(
                through_bar_index=index, bars_by_index=self.bars,
                before_timestamp=before_timestamp,
            )
        if not self.valid or (before_timestamp is not None and (
            not isinstance(before_timestamp, datetime)
            or before_timestamp.utcoffset() != timedelta(0)
            or self.bars[index].timestamp_utc >= before_timestamp
        )):
            return ema_reference.evaluate_ema20_v2(
                through_bar_index=index, bars_by_index=self.bars,
                before_timestamp=before_timestamp,
            )
        if index < 19:
            return ema_reference.EMA20EvaluationV2(
                ema_reference.EMA20StatusV2.INSUFFICIENT_EMA_WARMUP, index
            )
        bar = self.bars[index]
        if previous and isinstance(self.lane, _TickLane):
            n, d, i = self._previous_raw_ema
            steps = i - 19
            value = _reduced(n, d, ((2, 4), (5, 1), (3, steps), (7, steps)))
        elif previous:
            return self.previous_ema
        else:
            value = self.lane.ema() if isinstance(self.lane, _TickLane) else self.lane.ema
        return ema_reference.EMA20EvaluationV2(
            ema_reference.EMA20StatusV2.EVALUATED, index, value,
            ema_reference._exact_price(bar.close), bar.timestamp_utc
        )

    def macd(self, *, at_timestamp: datetime | None = None):
        """Return the identical MACDEvaluationV2, including pre-warmup values."""
        if not self.valid or (at_timestamp is not None and (
            not isinstance(at_timestamp, datetime)
            or at_timestamp != self.bars[self.index].timestamp_utc
        )):
            return macd_reference.evaluate_macd_v2(
                through_bar_index=self.index, bars_by_index=self.bars,
                at_timestamp=at_timestamp,
            )
        if self._macd_cache is None:
            self._macd_cache = macd_reference.MACDEvaluationV2(
                macd_reference.MACDStatusV2.EVALUATED if self.index >= 34
                else macd_reference.MACDStatusV2.INSUFFICIENT_MACD_WARMUP,
                self.index, *self.lane.values(), self.bars[self.index].timestamp_utc
            )
        return self._macd_cache
