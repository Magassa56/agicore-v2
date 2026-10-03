"""Independent, causal prior-direction and rejection prerequisites for V2.

Prior direction reads only the five closes before t. Rejection reads OHLC of
closed t and the extrema of those same five bars, with no candle-color filter.
Neither prerequisite emits a reversal event or an entry signal.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import MAX_EMAX, MIN_EMIN, Decimal, Inexact, localcontext
from enum import StrEnum
from itertools import pairwise

from .regime_context_v2 import RegimeDirection

PRIOR_DIRECTION_LOOKBACK = 5
PRIOR_DIRECTION_MIN_STEPS = 3
MIN_REJECTION_WICK_RATIO = Decimal("0.40")


class ReversalTransitionV2Error(ValueError):
    """Reject inconsistent or noncausal reversal observation metadata."""


class ReversalPriorDirection(StrEnum):
    """Direction of the established prior move, distinct from reversal direction."""

    UP = "UP"
    DOWN = "DOWN"
    NONE = "NONE"


class PriorDirectionStatus(StrEnum):
    """Separate incomplete history and invalid closes from an evaluated direction."""

    INSUFFICIENT_WARMUP = "INSUFFICIENT_WARMUP"
    INVALID_PRIOR_DIRECTION_INPUT = "INVALID_PRIOR_DIRECTION_INPUT"
    EVALUATED = "EVALUATED"


class RejectionBarStatus(StrEnum):
    """Validation outcomes of the closed candidate rejection predicate."""

    INSUFFICIENT_WARMUP = "INSUFFICIENT_WARMUP"
    INVALID_PRIOR_DIRECTION_INPUT = "INVALID_PRIOR_DIRECTION_INPUT"
    INVALID_PRIOR_EXTREMA = "INVALID_PRIOR_EXTREMA"
    INVALID_OHLC = "INVALID_OHLC"
    INVALID_CANDIDATE_RANGE = "INVALID_CANDIDATE_RANGE"
    EVALUATED = "EVALUATED"


@dataclass(frozen=True)
class PriorDirectionBarV2:
    """Close-only prior observation; missing/nonfinite prices retain their status."""

    bar_index: int
    timestamp_utc: datetime
    close: Decimal | int | None
    is_closed: bool

    def __post_init__(self) -> None:
        if type(self.bar_index) is not int or self.bar_index < 0:
            raise ReversalTransitionV2Error("bar_index must be a nonnegative integer")
        if (
            not isinstance(self.timestamp_utc, datetime)
            or self.timestamp_utc.tzinfo is None
            or self.timestamp_utc.utcoffset() != timedelta(0)
        ):
            raise ReversalTransitionV2Error("bar timestamp must be aware UTC")
        if type(self.is_closed) is not bool:
            raise ReversalTransitionV2Error("is_closed must be a boolean")


@dataclass(frozen=True)
class RejectionBarV2(PriorDirectionBarV2):
    """OHLC observation that supplies both frozen prior closes and extrema."""

    open: Decimal | int | None
    high: Decimal | int | None
    low: Decimal | int | None


@dataclass(frozen=True)
class ReversalPriorDirectionEvaluation:
    """Prior direction known at Close[t-1], without a qualified reversal event."""

    status: PriorDirectionStatus
    prior_direction: ReversalPriorDirection
    reversal_candidate_bar_index: int
    close_steps: tuple[Decimal, ...] | None = None
    up_steps: int | None = None
    down_steps: int | None = None
    flat_steps: int | None = None
    known_at_bar_index: int | None = None
    known_at_timestamp: datetime | None = None

    @property
    def reversal_direction(self) -> RegimeDirection | None:
        """Return the only eligible future reversal side, never an event by itself."""
        if self.prior_direction is ReversalPriorDirection.UP:
            return RegimeDirection.SHORT
        if self.prior_direction is ReversalPriorDirection.DOWN:
            return RegimeDirection.LONG
        return None


@dataclass(frozen=True)
class ReversalRejectionEvaluation:
    """Rejection only, without any subsequent opposite-transition confirmation."""

    status: RejectionBarStatus
    rejection_qualified: bool
    rejection_candidate_bar_index: int
    prior_direction: ReversalPriorDirectionEvaluation
    prior_high: Decimal | None = None
    prior_low: Decimal | None = None
    candidate_range: Decimal | None = None
    upper_wick: Decimal | None = None
    lower_wick: Decimal | None = None
    required_rejection_wick: Decimal | None = None
    known_at_bar_index: int | None = None
    known_at_timestamp: datetime | None = None

    @property
    def rejection_direction(self) -> RegimeDirection | None:
        """Return the rejection's eligible reversal side only when qualified."""
        return self.prior_direction.reversal_direction if self.rejection_qualified else None


def _finite_close(value: Decimal | int | None) -> Decimal | None:
    if type(value) is int:
        return Decimal(value)
    if isinstance(value, Decimal) and value.is_finite():
        return value
    return None


def evaluate_reversal_prior_direction_v2(
    *,
    reversal_candidate_bar_index: int,
    bars_by_index: Mapping[int, PriorDirectionBarV2],
) -> ReversalPriorDirectionEvaluation:
    """Require three of four signed close steps plus a strictly aligned endpoint.

    Read only t-5..t-1. Fewer than five completed observations gives insufficient
    warmup before price validation. Missing/nonfinite closes give invalid input.
    Malformed index/timestamp metadata raises a fail-closed input error. Signed
    steps use exact Decimal arithmetic even under reduced ambient precision.
    The impulse family's strict three-bar direction is not used or imported.
    """
    if type(reversal_candidate_bar_index) is not int or reversal_candidate_bar_index < 0:
        raise ReversalTransitionV2Error("candidate index must be a nonnegative integer")
    if not isinstance(bars_by_index, Mapping):
        raise ReversalTransitionV2Error("bars_by_index must be a mapping")

    t = reversal_candidate_bar_index
    indices = range(t - PRIOR_DIRECTION_LOOKBACK, t)
    if t < PRIOR_DIRECTION_LOOKBACK or any(index not in bars_by_index for index in indices):
        return ReversalPriorDirectionEvaluation(
            PriorDirectionStatus.INSUFFICIENT_WARMUP, ReversalPriorDirection.NONE, t
        )
    prior = tuple(bars_by_index[index] for index in indices)
    for index, bar in zip(indices, prior, strict=True):
        if not isinstance(bar, PriorDirectionBarV2) or bar.bar_index != index:
            raise ReversalTransitionV2Error("prior bar index is inconsistent")
    if any(bar.is_closed is not True for bar in prior):
        return ReversalPriorDirectionEvaluation(
            PriorDirectionStatus.INSUFFICIENT_WARMUP, ReversalPriorDirection.NONE, t
        )
    if any(earlier.timestamp_utc >= later.timestamp_utc for earlier, later in pairwise(prior)):
        raise ReversalTransitionV2Error("prior timestamps must increase")

    closes = tuple(_finite_close(bar.close) for bar in prior)
    if any(close is None for close in closes):
        return ReversalPriorDirectionEvaluation(
            PriorDirectionStatus.INVALID_PRIOR_DIRECTION_INPUT, ReversalPriorDirection.NONE, t
        )
    valid_closes = tuple(close for close in closes if close is not None)
    precision = max(
        28,
        max(value.adjusted() for value in valid_closes)
        - min(value.as_tuple().exponent for value in valid_closes)
        + 10,
    )
    with localcontext() as context:
        context.prec = precision
        context.Emax = MAX_EMAX
        context.Emin = MIN_EMIN
        context.traps[Inexact] = True
        steps = tuple(later - earlier for earlier, later in pairwise(valid_closes))
    up_steps = sum(step > 0 for step in steps)
    down_steps = sum(step < 0 for step in steps)
    flat_steps = sum(step == 0 for step in steps)
    if valid_closes[-1] > valid_closes[0] and up_steps >= PRIOR_DIRECTION_MIN_STEPS:
        direction = ReversalPriorDirection.UP
    elif valid_closes[-1] < valid_closes[0] and down_steps >= PRIOR_DIRECTION_MIN_STEPS:
        direction = ReversalPriorDirection.DOWN
    else:
        direction = ReversalPriorDirection.NONE
    return ReversalPriorDirectionEvaluation(
        PriorDirectionStatus.EVALUATED,
        direction,
        t,
        steps,
        up_steps,
        down_steps,
        flat_steps,
        t - 1,
        prior[-1].timestamp_utc,
    )


def evaluate_reversal_rejection_bar_v2(
    *,
    rejection_candidate_bar_index: int,
    bars_by_index: Mapping[int, RejectionBarV2],
) -> ReversalRejectionEvaluation:
    """Require a strict extreme sweep, strict failed hold and >= 40% rejection wick.

    The unchanged direction function and extrema use the same five prior bars.
    Only t-5..t are read; t must be closed. Incomplete/invalid prior direction
    returns its status, then candidate OHLC/range and prior extrema are checked.
    Missing/nonfinite/inverted prior extrema fail closed with an explicit status.
    All geometric arithmetic is exact. Neither body color nor t+1 is consulted.
    """
    if type(rejection_candidate_bar_index) is not int or rejection_candidate_bar_index < 0:
        raise ReversalTransitionV2Error("candidate index must be a nonnegative integer")
    if not isinstance(bars_by_index, Mapping):
        raise ReversalTransitionV2Error("bars_by_index must be a mapping")
    t = rejection_candidate_bar_index
    if t not in bars_by_index:
        raise ReversalTransitionV2Error("closed rejection candidate is required")
    candidate = bars_by_index[t]
    if not isinstance(candidate, RejectionBarV2) or candidate.bar_index != t:
        raise ReversalTransitionV2Error("candidate bar index is inconsistent")
    if candidate.is_closed is not True:
        raise ReversalTransitionV2Error("rejection candidate must be closed")

    prior: dict[int, RejectionBarV2] = {}
    for index in range(max(0, t - PRIOR_DIRECTION_LOOKBACK), t):
        if index not in bars_by_index:
            continue
        bar = bars_by_index[index]
        if not isinstance(bar, RejectionBarV2) or bar.bar_index != index:
            raise ReversalTransitionV2Error("prior bar index is inconsistent")
        prior[index] = bar
    direction = evaluate_reversal_prior_direction_v2(
        reversal_candidate_bar_index=t, bars_by_index=prior
    )
    if direction.status is not PriorDirectionStatus.EVALUATED:
        return ReversalRejectionEvaluation(
            RejectionBarStatus(direction.status.value), False, t, direction
        )
    if direction.known_at_timestamp >= candidate.timestamp_utc:
        raise ReversalTransitionV2Error("candidate must follow prior closed bars")

    ohlc = tuple(
        _finite_close(value)
        for value in (candidate.open, candidate.high, candidate.low, candidate.close)
    )
    if any(value is None for value in ohlc):
        return ReversalRejectionEvaluation(RejectionBarStatus.INVALID_OHLC, False, t, direction)
    open_, high, low, close = ohlc
    if not (high >= max(open_, close) and low <= min(open_, close) and high >= low):
        return ReversalRejectionEvaluation(RejectionBarStatus.INVALID_OHLC, False, t, direction)
    if high == low:
        return ReversalRejectionEvaluation(
            RejectionBarStatus.INVALID_CANDIDATE_RANGE,
            False,
            t,
            direction,
            candidate_range=Decimal(0),
            upper_wick=Decimal(0),
            lower_wick=Decimal(0),
        )

    extrema = tuple((_finite_close(bar.high), _finite_close(bar.low)) for bar in prior.values())
    if any(h is None or l is None or h < l for h, l in extrema):
        return ReversalRejectionEvaluation(
            RejectionBarStatus.INVALID_PRIOR_EXTREMA, False, t, direction
        )

    values = (*ohlc, *(value for pair in extrema for value in pair))
    precision = max(
        28,
        max(value.adjusted() for value in values)
        - min(value.as_tuple().exponent for value in values)
        + 10,
    )
    with localcontext() as context:
        context.prec = precision
        context.Emax = MAX_EMAX
        context.Emin = MIN_EMIN
        context.traps[Inexact] = True
        candidate_range = high - low
        upper_wick = high - max(open_, close)
        lower_wick = min(open_, close) - low
        prior_high = max(h for h, _ in extrema)
        prior_low = min(l for _, l in extrema)
        required_wick = MIN_REJECTION_WICK_RATIO * candidate_range
        qualified = (
            direction.prior_direction is ReversalPriorDirection.UP
            and high > prior_high
            and close < prior_high
            and upper_wick >= required_wick
        ) or (
            direction.prior_direction is ReversalPriorDirection.DOWN
            and low < prior_low
            and close > prior_low
            and lower_wick >= required_wick
        )
    return ReversalRejectionEvaluation(
        RejectionBarStatus.EVALUATED,
        qualified,
        t,
        direction,
        prior_high,
        prior_low,
        candidate_range,
        upper_wick,
        lower_wick,
        required_wick,
        t,
        candidate.timestamp_utc,
    )


__all__ = [
    "MIN_REJECTION_WICK_RATIO",
    "PRIOR_DIRECTION_LOOKBACK",
    "PRIOR_DIRECTION_MIN_STEPS",
    "PriorDirectionBarV2",
    "PriorDirectionStatus",
    "RejectionBarStatus",
    "RejectionBarV2",
    "ReversalPriorDirection",
    "ReversalPriorDirectionEvaluation",
    "ReversalRejectionEvaluation",
    "ReversalTransitionV2Error",
    "evaluate_reversal_prior_direction_v2",
    "evaluate_reversal_rejection_bar_v2",
]
