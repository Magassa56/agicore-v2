"""Causal pre-impulse direction predicate for the V2 research contract.

The emerging direction inspects only the three closed bars before candidate
``t``. The independent range predicate inspects the closed candidate and the
preceding 20 closed bars. Neither predicate emits an impulse or entry signal.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import MAX_EMAX, MIN_EMIN, Decimal, Inexact, localcontext
from enum import StrEnum
from itertools import pairwise

from .regime_context_v2 import RegimeDirection

EMERGING_DIRECTION_LOOKBACK = 3
IMPULSE_RANGE_LOOKBACK = 20
IMPULSE_RANGE_MULTIPLIER = Decimal("1.50")


class EmergingDirectionV2Error(ValueError):
    """Reject inconsistent or noncausal pre-impulse observations."""


class EmergingDirectionStatus(StrEnum):
    """Separate incomplete history from an evaluated predicate with no direction."""

    INSUFFICIENT_WARMUP = "INSUFFICIENT_WARMUP"
    EVALUATED = "EVALUATED"


class ImpulseRangeStatus(StrEnum):
    """State of the independent candidate-bar range predicate."""

    INSUFFICIENT_WARMUP = "INSUFFICIENT_WARMUP"
    INVALID_REFERENCE_RANGE = "INVALID_REFERENCE_RANGE"
    EVALUATED = "EVALUATED"


@dataclass(frozen=True)
class StructuralBarV2:
    """Minimal structural observation; only closed bars may be used as history."""

    bar_index: int
    timestamp_utc: datetime
    low: Decimal
    high: Decimal
    close: Decimal
    is_closed: bool

    def __post_init__(self) -> None:
        if type(self.bar_index) is not int or self.bar_index < 0:
            raise EmergingDirectionV2Error("bar_index must be a nonnegative integer")
        if (
            not isinstance(self.timestamp_utc, datetime)
            or self.timestamp_utc.tzinfo is None
            or self.timestamp_utc.utcoffset() != timedelta(0)
        ):
            raise EmergingDirectionV2Error("bar timestamp must be aware UTC")
        for field in ("low", "high", "close"):
            value = getattr(self, field)
            if not isinstance(value, Decimal) or not value.is_finite():
                raise EmergingDirectionV2Error(f"{field} must be a finite Decimal")
        if not self.low <= self.close <= self.high:
            raise EmergingDirectionV2Error("close must be inside the low/high range")
        if type(self.is_closed) is not bool:
            raise EmergingDirectionV2Error("is_closed must be a boolean")


@dataclass(frozen=True)
class EmergingDirectionEvaluation:
    """Direction known by Close[t-1], before evaluating candidate bar t."""

    status: EmergingDirectionStatus
    emerging_direction: RegimeDirection | None
    impulse_candidate_bar_index: int
    known_at_bar_index: int | None
    known_at_timestamp: datetime | None


@dataclass(frozen=True)
class ImpulseRangeEvaluation:
    """Candidate range and exact prior median, without direction or entry."""

    status: ImpulseRangeStatus
    range_qualified: bool
    impulse_candidate_bar_index: int
    candidate_range: Decimal | None
    reference_range: Decimal | None
    required_range: Decimal | None


def evaluate_emerging_direction_v2(
    *,
    impulse_candidate_bar_index: int,
    bars_by_index: Mapping[int, StructuralBarV2],
) -> EmergingDirectionEvaluation:
    """Evaluate strict closes and nonstrict lows/highs on t-3, t-2, t-1 only.

    A missing prerequisite returns ``INSUFFICIENT_WARMUP``. Malformed or
    nonclosed prerequisites fail closed. The mapping may contain t or later
    bars; their values are never accessed.
    """
    if type(impulse_candidate_bar_index) is not int or impulse_candidate_bar_index < 0:
        raise EmergingDirectionV2Error("candidate index must be a nonnegative integer")
    if not isinstance(bars_by_index, Mapping):
        raise EmergingDirectionV2Error("bars_by_index must be a mapping")

    t = impulse_candidate_bar_index
    if t < EMERGING_DIRECTION_LOOKBACK:
        return EmergingDirectionEvaluation(
            EmergingDirectionStatus.INSUFFICIENT_WARMUP, None, t, None, None
        )

    indices = (t - 3, t - 2, t - 1)
    if any(index not in bars_by_index for index in indices):
        return EmergingDirectionEvaluation(
            EmergingDirectionStatus.INSUFFICIENT_WARMUP, None, t, None, None
        )

    prior = tuple(bars_by_index[index] for index in indices)
    for index, bar in zip(indices, prior, strict=True):
        if not isinstance(bar, StructuralBarV2) or bar.bar_index != index:
            raise EmergingDirectionV2Error("pre-impulse bar index is inconsistent")
        if bar.is_closed is not True:
            raise EmergingDirectionV2Error("pre-impulse bars must be closed")
    if not prior[0].timestamp_utc < prior[1].timestamp_utc < prior[2].timestamp_utc:
        raise EmergingDirectionV2Error("pre-impulse timestamps must increase")

    first, second, third = prior
    if first.close < second.close < third.close and first.low <= second.low <= third.low:
        direction = RegimeDirection.LONG
    elif first.close > second.close > third.close and first.high >= second.high >= third.high:
        direction = RegimeDirection.SHORT
    else:
        direction = None
    return EmergingDirectionEvaluation(
        EmergingDirectionStatus.EVALUATED,
        direction,
        t,
        t - 1,
        third.timestamp_utc,
    )


def evaluate_impulse_range_v2(
    *,
    impulse_candidate_bar_index: int,
    bars_by_index: Mapping[int, StructuralBarV2],
) -> ImpulseRangeEvaluation:
    """Compare High[t]-Low[t] with 1.50 times the exact prior-20 median.

    The candidate must be closed. Only t and indices t-20 through t-1 are
    accessed; earlier and future bars cannot influence this predicate.
    """
    if type(impulse_candidate_bar_index) is not int or impulse_candidate_bar_index < 0:
        raise EmergingDirectionV2Error("candidate index must be a nonnegative integer")
    if not isinstance(bars_by_index, Mapping):
        raise EmergingDirectionV2Error("bars_by_index must be a mapping")

    t = impulse_candidate_bar_index
    if t not in bars_by_index:
        raise EmergingDirectionV2Error("closed candidate bar is required")
    candidate = bars_by_index[t]
    if not isinstance(candidate, StructuralBarV2) or candidate.bar_index != t:
        raise EmergingDirectionV2Error("candidate bar index is inconsistent")
    if candidate.is_closed is not True:
        raise EmergingDirectionV2Error("candidate bar must be closed")

    if t < IMPULSE_RANGE_LOOKBACK:
        return ImpulseRangeEvaluation(
            ImpulseRangeStatus.INSUFFICIENT_WARMUP, False, t, None, None, None
        )

    indices = range(t - IMPULSE_RANGE_LOOKBACK, t)
    if any(index not in bars_by_index for index in indices):
        return ImpulseRangeEvaluation(
            ImpulseRangeStatus.INSUFFICIENT_WARMUP, False, t, None, None, None
        )

    prior = tuple(bars_by_index[index] for index in indices)
    for index, bar in zip(indices, prior, strict=True):
        if not isinstance(bar, StructuralBarV2) or bar.bar_index != index:
            raise EmergingDirectionV2Error("prior range bar index is inconsistent")
        if bar.is_closed is not True:
            return ImpulseRangeEvaluation(
                ImpulseRangeStatus.INSUFFICIENT_WARMUP, False, t, None, None, None
            )
    if any(earlier.timestamp_utc >= later.timestamp_utc for earlier, later in pairwise(prior)):
        raise EmergingDirectionV2Error("prior range timestamps must increase")
    if prior[-1].timestamp_utc >= candidate.timestamp_utc:
        raise EmergingDirectionV2Error("candidate must follow the prior closed bars")

    # Every Decimal input is finite. The chosen precision accommodates exact
    # subtraction, the even-sized median, and multiplication by 1.50, even if
    # the caller has lowered the ambient Decimal precision.
    values = (
        candidate.low,
        candidate.high,
        *(value for bar in prior for value in (bar.low, bar.high)),
    )
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
        candidate_range = candidate.high - candidate.low
        ordered_ranges = sorted(bar.high - bar.low for bar in prior)
        reference_range = (ordered_ranges[9] + ordered_ranges[10]) / Decimal(2)
        if reference_range <= 0:
            return ImpulseRangeEvaluation(
                ImpulseRangeStatus.INVALID_REFERENCE_RANGE,
                False,
                t,
                candidate_range,
                reference_range,
                None,
            )
        required_range = IMPULSE_RANGE_MULTIPLIER * reference_range
        qualified = candidate_range >= required_range

    return ImpulseRangeEvaluation(
        ImpulseRangeStatus.EVALUATED,
        qualified,
        t,
        candidate_range,
        reference_range,
        required_range,
    )


__all__ = [
    "EMERGING_DIRECTION_LOOKBACK",
    "IMPULSE_RANGE_LOOKBACK",
    "IMPULSE_RANGE_MULTIPLIER",
    "EmergingDirectionEvaluation",
    "EmergingDirectionStatus",
    "EmergingDirectionV2Error",
    "ImpulseRangeEvaluation",
    "ImpulseRangeStatus",
    "StructuralBarV2",
    "evaluate_emerging_direction_v2",
    "evaluate_impulse_range_v2",
]
