"""Deterministic pullback predicate for ``EMA_PULLBACK_V1_MNQ``.

This module freezes only the strategy rules that the owner has explicitly defined.  It
does not compute EMA20, does not emit an executable trading order, and never reads market
or OOS data.  The EMA20 slope uses caller-supplied closed-bar EMA20 values; MACD reuses
the deterministic replay EMA implementation.  Position exits remain fail-closed until
their strategy rules are specified.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from .market_replay import calculate_ema

STRATEGY_ID = "EMA_PULLBACK_V1_MNQ"
INSTRUMENT = "MNQ"
TIMEFRAME_MINUTES = 1
EMA_PERIOD = 20
EMA_SLOPE_LOOKBACK_BARS = 3
MINIMUM_EMA_SLOPE_POINTS_PER_BAR = Decimal("0.0")
MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9
MACD_LINE_MA_TYPE = "EMA"
MACD_SIGNAL_LINE_MA_TYPE = "EMA"
MACD_CROSS_VALIDITY_BARS = 1
MACD_REQUIRED_CLOSED_BARS = MACD_SLOW_PERIOD + MACD_SIGNAL_PERIOD
EMA_SEED_CONVENTION = "FIRST_CLOSE_ALPHA_2_OVER_PERIOD_PLUS_1"
MNQ_TICK_SIZE_POINTS = Decimal("0.25")
PULLBACK_LOOKBACK_BARS = 3
MAX_PULLBACK_DISTANCE_TICKS = 8
MAX_PULLBACK_DISTANCE_POINTS = Decimal("2.00")
WICK_CROSS_EMA20_ALLOWED = True
CONFIRMATION_CLOSE_CORRECT_SIDE_REQUIRED = True
EMA_SLOPE_REQUIRED = True
MACD_CROSS_REQUIRED = True
SIGNAL_DECISION_ON_CLOSED_BAR = True
EARLIEST_EXECUTION_BAR_OFFSET = 1


class PullbackContractError(ValueError):
    """Raised when a pullback evaluation would require an implicit assumption."""


class PullbackSide(StrEnum):
    """Direction being evaluated by the fixed pullback predicate."""

    LONG = "LONG"
    SHORT = "SHORT"


class MACDStatus(StrEnum):
    """Availability of the deterministic MACD values at confirmation."""

    READY = "READY"
    INSUFFICIENT_WARMUP = "INSUFFICIENT_WARMUP"


class EntrySignal(StrEnum):
    """Non-executable strategy signal emitted by the assembled predicates."""

    LONG = "LONG"
    SHORT = "SHORT"
    NONE = "NONE"


@dataclass(frozen=True)
class ClosedBarEMA20:
    """Closed-bar values available at one causal sequence index.

    ``ema20`` is the EMA20 value computed at this bar's close.  Decimal values are
    required so the inclusive eight-tick boundary is evaluated without float drift.
    """

    sequence: int
    low: Decimal
    high: Decimal
    close: Decimal
    ema20: Decimal

    def __post_init__(self) -> None:
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int):
            raise PullbackContractError("sequence must be an integer")
        if self.sequence < 0:
            raise PullbackContractError("sequence must be non-negative")
        for field_name in ("low", "high", "close", "ema20"):
            value = getattr(self, field_name)
            if not isinstance(value, Decimal) or not value.is_finite():
                raise PullbackContractError(f"{field_name} must be a finite Decimal")
            if value < 0:
                raise PullbackContractError(f"{field_name} must be non-negative")
        if self.low > self.high:
            raise PullbackContractError("low must be less than or equal to high")
        if not self.low <= self.close <= self.high:
            raise PullbackContractError("close must be inside the closed bar range")


@dataclass(frozen=True)
class PullbackPredicateResult:
    """Result of the frozen pullback plus confirmation-close predicate only."""

    side: PullbackSide
    pullback_confirmation_qualifies: bool
    pullback_found: bool
    confirmation_close_correct_side: bool
    minimum_distance_points: Decimal
    minimum_distance_ticks: Decimal
    qualifying_bar_sequence: int | None
    confirmation_bar_sequence: int


@dataclass(frozen=True)
class EMA20SlopeResult:
    """Result of the frozen causal EMA20 slope predicate only."""

    side: PullbackSide
    ema20_slope_qualifies: bool
    slope_points_per_bar: Decimal
    lookback_bar_sequence: int
    confirmation_bar_sequence: int


@dataclass(frozen=True)
class MACDCrossResult:
    """MACD cross result at one explicit closed confirmation bar."""

    side: PullbackSide
    status: MACDStatus
    signal: EntrySignal
    macd_cross_qualifies: bool
    previous_macd_line: Decimal | None
    previous_signal_line: Decimal | None
    current_macd_line: Decimal | None
    current_signal_line: Decimal | None
    previous_bar_sequence: int | None
    confirmation_bar_sequence: int
    observed_closed_bars: int
    required_closed_bars: int = MACD_REQUIRED_CLOSED_BARS


@dataclass(frozen=True)
class EMAPullbackEntrySignalResult:
    """Fail-closed assembly of pullback, EMA20 slope and MACD predicates."""

    side: PullbackSide
    signal: EntrySignal
    entry_signal_qualifies: bool
    pullback_confirmation_qualifies: bool
    ema20_slope_qualifies: bool
    macd_cross_qualifies: bool
    macd_status: MACDStatus
    confirmation_bar_sequence: int


def distance_from_bar_range_to_ema20(bar: ClosedBarEMA20) -> Decimal:
    """Return the non-negative distance from a closed bar's full range to EMA20.

    A range that touches or crosses EMA20 has zero distance.  This is the exact
    implementation of ``wick_cross_ema20 = ALLOWED``.
    """
    if bar.low <= bar.ema20 <= bar.high:
        return Decimal(0)
    return min(abs(bar.low - bar.ema20), abs(bar.high - bar.ema20))


def evaluate_pullback_confirmation(
    *,
    side: PullbackSide,
    preceding_bars: Sequence[ClosedBarEMA20],
    confirmation_bar: ClosedBarEMA20,
) -> PullbackPredicateResult:
    """Evaluate the owner-defined pullback window and strict confirmation close.

    Exactly the three immediately preceding closed bars are accepted.  The confirmation
    bar is excluded from the pullback search.  No future bar is accepted by the sequence
    check, and this function does not expose execution at the confirmation close.

    This function deliberately evaluates only its own component.  The assembled entry
    evaluator separately requires the frozen EMA20 slope and MACD predicates.
    """
    if not isinstance(side, PullbackSide):
        raise PullbackContractError("side must be explicitly LONG or SHORT")

    bars = tuple(preceding_bars)
    if len(bars) != PULLBACK_LOOKBACK_BARS:
        raise PullbackContractError(
            f"exactly {PULLBACK_LOOKBACK_BARS} preceding closed bars are required"
        )
    expected_sequences = tuple(
        range(
            confirmation_bar.sequence - PULLBACK_LOOKBACK_BARS,
            confirmation_bar.sequence,
        )
    )
    actual_sequences = tuple(bar.sequence for bar in bars)
    if actual_sequences != expected_sequences:
        raise PullbackContractError(
            "preceding bars must be the three causal bars immediately before confirmation"
        )

    distances = tuple(distance_from_bar_range_to_ema20(bar) for bar in bars)
    minimum_distance = min(distances)
    qualifying_index = next(
        (
            index
            for index, distance in enumerate(distances)
            if distance <= MAX_PULLBACK_DISTANCE_POINTS
        ),
        None,
    )
    pullback_found = qualifying_index is not None
    close_correct = (
        confirmation_bar.close > confirmation_bar.ema20
        if side is PullbackSide.LONG
        else confirmation_bar.close < confirmation_bar.ema20
    )

    return PullbackPredicateResult(
        side=side,
        pullback_confirmation_qualifies=pullback_found and close_correct,
        pullback_found=pullback_found,
        confirmation_close_correct_side=close_correct,
        minimum_distance_points=minimum_distance,
        minimum_distance_ticks=minimum_distance / MNQ_TICK_SIZE_POINTS,
        qualifying_bar_sequence=(
            bars[qualifying_index].sequence if qualifying_index is not None else None
        ),
        confirmation_bar_sequence=confirmation_bar.sequence,
    )


def evaluate_ema20_slope(
    *,
    side: PullbackSide,
    lookback_bar: ClosedBarEMA20,
    confirmation_bar: ClosedBarEMA20,
) -> EMA20SlopeResult:
    """Evaluate the owner-defined EMA20 slope at a closed confirmation bar.

    The fixed formula is ``(EMA20[t] - EMA20[t-3]) / 3``.  Only the two
    caller-supplied, already-closed bars participate in the calculation.  Their sequence
    indices must prove that exact causal relationship; missing warmup or any other gap
    fails closed.  Zero/equality never qualifies either direction.
    """
    if not isinstance(side, PullbackSide):
        raise PullbackContractError("side must be explicitly LONG or SHORT")
    if confirmation_bar.sequence < EMA_SLOPE_LOOKBACK_BARS:
        raise PullbackContractError(
            f"at least {EMA_SLOPE_LOOKBACK_BARS} closed warmup bars are required"
        )

    expected_lookback_sequence = confirmation_bar.sequence - EMA_SLOPE_LOOKBACK_BARS
    if lookback_bar.sequence != expected_lookback_sequence:
        raise PullbackContractError("lookback bar must be the causal closed bar exactly t-3")

    slope = (confirmation_bar.ema20 - lookback_bar.ema20) / Decimal(EMA_SLOPE_LOOKBACK_BARS)
    qualifies = (
        slope > MINIMUM_EMA_SLOPE_POINTS_PER_BAR
        if side is PullbackSide.LONG
        else slope < -MINIMUM_EMA_SLOPE_POINTS_PER_BAR
    )
    return EMA20SlopeResult(
        side=side,
        ema20_slope_qualifies=qualifies,
        slope_points_per_bar=slope,
        lookback_bar_sequence=lookback_bar.sequence,
        confirmation_bar_sequence=confirmation_bar.sequence,
    )


def evaluate_macd_confirmation(
    *,
    side: PullbackSide,
    closed_bars: Sequence[ClosedBarEMA20],
    confirmation_bar_sequence: int,
) -> MACDCrossResult:
    """Calculate and evaluate the fixed MACD cross on one closed bar.

    EMA12, EMA26 and the EMA9 signal line reuse the public deterministic replay
    implementation, including its first-close seed and ``alpha=2/(period+1)``.  Values
    after ``confirmation_bar_sequence`` are deliberately ignored.  The signal-line
    warmup plus the prior point needed for a cross require 35 causal closed bars.
    """
    if not isinstance(side, PullbackSide):
        raise PullbackContractError("side must be explicitly LONG or SHORT")
    if (
        isinstance(confirmation_bar_sequence, bool)
        or not isinstance(confirmation_bar_sequence, int)
        or confirmation_bar_sequence < 0
    ):
        raise PullbackContractError("confirmation_bar_sequence must be a non-negative integer")

    causal_bars = tuple(bar for bar in closed_bars if bar.sequence <= confirmation_bar_sequence)
    if not causal_bars or causal_bars[-1].sequence != confirmation_bar_sequence:
        raise PullbackContractError("closed bars must contain the confirmation bar")
    actual_sequences = tuple(bar.sequence for bar in causal_bars)
    expected_sequences = tuple(range(causal_bars[0].sequence, confirmation_bar_sequence + 1))
    if actual_sequences != expected_sequences:
        raise PullbackContractError(
            "closed MACD bars through confirmation must be ordered and contiguous"
        )

    observed = len(causal_bars)
    if observed < MACD_REQUIRED_CLOSED_BARS:
        return MACDCrossResult(
            side=side,
            status=MACDStatus.INSUFFICIENT_WARMUP,
            signal=EntrySignal.NONE,
            macd_cross_qualifies=False,
            previous_macd_line=None,
            previous_signal_line=None,
            current_macd_line=None,
            current_signal_line=None,
            previous_bar_sequence=None,
            confirmation_bar_sequence=confirmation_bar_sequence,
            observed_closed_bars=observed,
        )

    closes = [float(bar.close) for bar in causal_bars]
    if any(not math.isfinite(close) for close in closes):
        raise PullbackContractError("closed-bar values exceed finite EMA precision")
    fast_ema = calculate_ema(closes, MACD_FAST_PERIOD)
    slow_ema = calculate_ema(closes, MACD_SLOW_PERIOD)
    first_warmed_index = MACD_SLOW_PERIOD - 1
    macd_line = [fast_ema[index] - slow_ema[index] for index in range(first_warmed_index, observed)]
    signal_line = calculate_ema(macd_line, MACD_SIGNAL_PERIOD)

    previous_macd = Decimal(str(macd_line[-2]))
    current_macd = Decimal(str(macd_line[-1]))
    previous_signal = Decimal(str(signal_line[-2]))
    current_signal = Decimal(str(signal_line[-1]))
    bullish_cross = previous_macd <= previous_signal and current_macd > current_signal
    bearish_cross = previous_macd >= previous_signal and current_macd < current_signal
    qualifies = bullish_cross if side is PullbackSide.LONG else bearish_cross
    signal = EntrySignal(side.value) if qualifies else EntrySignal.NONE

    return MACDCrossResult(
        side=side,
        status=MACDStatus.READY,
        signal=signal,
        macd_cross_qualifies=qualifies,
        previous_macd_line=previous_macd,
        previous_signal_line=previous_signal,
        current_macd_line=current_macd,
        current_signal_line=current_signal,
        previous_bar_sequence=confirmation_bar_sequence - 1,
        confirmation_bar_sequence=confirmation_bar_sequence,
        observed_closed_bars=observed,
    )


def assemble_ema_pullback_entry_signal(
    *,
    side: PullbackSide,
    pullback: PullbackPredicateResult,
    slope: EMA20SlopeResult,
    macd: MACDCrossResult,
) -> EMAPullbackEntrySignalResult:
    """Combine all mandatory V1 entry predicates without executing a trade."""
    if not isinstance(side, PullbackSide):
        raise PullbackContractError("side must be explicitly LONG or SHORT")
    if any(result_side is not side for result_side in (pullback.side, slope.side, macd.side)):
        raise PullbackContractError("all entry predicates must evaluate the same side")
    confirmation_sequences = {
        pullback.confirmation_bar_sequence,
        slope.confirmation_bar_sequence,
        macd.confirmation_bar_sequence,
    }
    if len(confirmation_sequences) != 1:
        raise PullbackContractError("all entry predicates must evaluate the same confirmation bar")

    qualifies = (
        pullback.pullback_confirmation_qualifies
        and slope.ema20_slope_qualifies
        and macd.status is MACDStatus.READY
        and macd.macd_cross_qualifies
    )
    return EMAPullbackEntrySignalResult(
        side=side,
        signal=EntrySignal(side.value) if qualifies else EntrySignal.NONE,
        entry_signal_qualifies=qualifies,
        pullback_confirmation_qualifies=pullback.pullback_confirmation_qualifies,
        ema20_slope_qualifies=slope.ema20_slope_qualifies,
        macd_cross_qualifies=macd.macd_cross_qualifies,
        macd_status=macd.status,
        confirmation_bar_sequence=confirmation_sequences.pop(),
    )


def evaluate_ema_pullback_entry_signal(
    *,
    side: PullbackSide,
    closed_bars: Sequence[ClosedBarEMA20],
    confirmation_bar_sequence: int,
) -> EMAPullbackEntrySignalResult:
    """Evaluate the assembled entry contract from one coherent closed-bar history."""
    macd = evaluate_macd_confirmation(
        side=side,
        closed_bars=closed_bars,
        confirmation_bar_sequence=confirmation_bar_sequence,
    )
    causal_bars = tuple(bar for bar in closed_bars if bar.sequence <= confirmation_bar_sequence)
    if len(causal_bars) < PULLBACK_LOOKBACK_BARS + 1:
        raise PullbackContractError(
            "assembled entry requires confirmation plus three preceding closed bars"
        )
    confirmation_bar = causal_bars[-1]
    preceding_bars = causal_bars[-(PULLBACK_LOOKBACK_BARS + 1) : -1]
    pullback = evaluate_pullback_confirmation(
        side=side,
        preceding_bars=preceding_bars,
        confirmation_bar=confirmation_bar,
    )
    slope = evaluate_ema20_slope(
        side=side,
        lookback_bar=preceding_bars[0],
        confirmation_bar=confirmation_bar,
    )
    return assemble_ema_pullback_entry_signal(
        side=side,
        pullback=pullback,
        slope=slope,
        macd=macd,
    )


__all__ = [
    "CONFIRMATION_CLOSE_CORRECT_SIDE_REQUIRED",
    "EARLIEST_EXECUTION_BAR_OFFSET",
    "EMA_PERIOD",
    "EMA_SEED_CONVENTION",
    "EMA_SLOPE_LOOKBACK_BARS",
    "EMA_SLOPE_REQUIRED",
    "INSTRUMENT",
    "MACD_CROSS_REQUIRED",
    "MACD_CROSS_VALIDITY_BARS",
    "MACD_FAST_PERIOD",
    "MACD_LINE_MA_TYPE",
    "MACD_REQUIRED_CLOSED_BARS",
    "MACD_SIGNAL_LINE_MA_TYPE",
    "MACD_SIGNAL_PERIOD",
    "MACD_SLOW_PERIOD",
    "MAX_PULLBACK_DISTANCE_POINTS",
    "MAX_PULLBACK_DISTANCE_TICKS",
    "MINIMUM_EMA_SLOPE_POINTS_PER_BAR",
    "MNQ_TICK_SIZE_POINTS",
    "PULLBACK_LOOKBACK_BARS",
    "SIGNAL_DECISION_ON_CLOSED_BAR",
    "STRATEGY_ID",
    "TIMEFRAME_MINUTES",
    "WICK_CROSS_EMA20_ALLOWED",
    "ClosedBarEMA20",
    "EMA20SlopeResult",
    "EMAPullbackEntrySignalResult",
    "EntrySignal",
    "MACDCrossResult",
    "MACDStatus",
    "PullbackContractError",
    "PullbackPredicateResult",
    "PullbackSide",
    "assemble_ema_pullback_entry_signal",
    "distance_from_bar_range_to_ema20",
    "evaluate_ema20_slope",
    "evaluate_ema_pullback_entry_signal",
    "evaluate_macd_confirmation",
    "evaluate_pullback_confirmation",
]
