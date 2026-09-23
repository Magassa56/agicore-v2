"""Deterministic pullback predicate for ``EMA_PULLBACK_V1_MNQ``.

This module freezes only the strategy rules that the owner has explicitly defined.  It
does not compute EMA20 or MACD, does not emit an executable trading signal, and never
reads market or OOS data.  The EMA20 slope is evaluated from caller-supplied closed-bar
EMA20 values.  A complete signal remains fail-closed until the remaining strategy rules
are specified.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

STRATEGY_ID = "EMA_PULLBACK_V1_MNQ"
INSTRUMENT = "MNQ"
TIMEFRAME_MINUTES = 1
EMA_PERIOD = 20
EMA_SLOPE_LOOKBACK_BARS = 3
MINIMUM_EMA_SLOPE_POINTS_PER_BAR = Decimal("0.0")
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


@dataclass(frozen=True)
class EMA20SlopeResult:
    """Result of the frozen causal EMA20 slope predicate only."""

    side: PullbackSide
    ema20_slope_qualifies: bool
    slope_points_per_bar: Decimal
    lookback_bar_sequence: int
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

    This function deliberately does not evaluate EMA slope or MACD.  Both remain mandatory
    for a full strategy signal, but their machine definitions are not yet authorized.
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


__all__ = [
    "CONFIRMATION_CLOSE_CORRECT_SIDE_REQUIRED",
    "EARLIEST_EXECUTION_BAR_OFFSET",
    "EMA_PERIOD",
    "EMA_SLOPE_LOOKBACK_BARS",
    "EMA_SLOPE_REQUIRED",
    "INSTRUMENT",
    "MACD_CROSS_REQUIRED",
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
    "PullbackContractError",
    "PullbackPredicateResult",
    "PullbackSide",
    "distance_from_bar_range_to_ema20",
    "evaluate_ema20_slope",
    "evaluate_pullback_confirmation",
]
