"""Causal pre-impulse direction predicate for the V2 research contract.

The emerging direction inspects only the three closed bars before candidate
``t``. The independent range and trade-volume predicates inspect the closed
candidate and the preceding 20 closed bars. Body/wick qualification inspects
only the closed candidate with the already established emerging direction.
None emits an impulse or entry signal.
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
IMPULSE_VOLUME_MEASURE = "BAR_TRADE_VOLUME"
IMPULSE_VOLUME_LOOKBACK = 20
IMPULSE_VOLUME_MULTIPLIER = Decimal("1.50")
MIN_BODY_TO_RANGE_RATIO = Decimal("0.60")
MAX_TERMINAL_WICK_TO_RANGE_RATIO = Decimal("0.20")


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


class ImpulseVolumeStatus(StrEnum):
    """State of the independent candidate-bar trade-volume predicate."""

    INSUFFICIENT_WARMUP = "INSUFFICIENT_WARMUP"
    INVALID_CANDIDATE_VOLUME = "INVALID_CANDIDATE_VOLUME"
    INVALID_REFERENCE_VOLUME = "INVALID_REFERENCE_VOLUME"
    INVALID_VOLUME = "INVALID_VOLUME"
    EVALUATED = "EVALUATED"


class ImpulseBodyWickStatus(StrEnum):
    """Distinguish malformed OHLC and zero range from an evaluated predicate."""

    INVALID_OHLC = "INVALID_OHLC"
    INVALID_CANDIDATE_RANGE = "INVALID_CANDIDATE_RANGE"
    EVALUATED = "EVALUATED"


@dataclass(frozen=True)
class BodyWickBarV2:
    """Candidate OHLC; malformed values reach the evaluator's error status."""

    bar_index: int
    timestamp_utc: datetime
    open: Decimal
    high: Decimal
    low: Decimal
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
        if type(self.is_closed) is not bool:
            raise EmergingDirectionV2Error("is_closed must be a boolean")


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
class TradeVolumeBarV2:
    """Aggregated trade volume of a one-minute Last bar, without prices.

    Missing or invalid volume remains observable so the evaluator can return
    the specified error status. Source metadata is mandatory; it is an input
    constraint, not a replacement for dataset lineage evidence.
    """

    bar_index: int
    timestamp_utc: datetime
    volume: Decimal | int | None
    is_closed: bool
    volume_measure: str
    interval_minutes: int
    data_type: str

    def __post_init__(self) -> None:
        if type(self.bar_index) is not int or self.bar_index < 0:
            raise EmergingDirectionV2Error("bar_index must be a nonnegative integer")
        if (
            not isinstance(self.timestamp_utc, datetime)
            or self.timestamp_utc.tzinfo is None
            or self.timestamp_utc.utcoffset() != timedelta(0)
        ):
            raise EmergingDirectionV2Error("bar timestamp must be aware UTC")
        if type(self.is_closed) is not bool:
            raise EmergingDirectionV2Error("is_closed must be a boolean")
        if self.volume_measure != IMPULSE_VOLUME_MEASURE:
            raise EmergingDirectionV2Error("volume_measure must be BAR_TRADE_VOLUME")
        if type(self.interval_minutes) is not int or self.interval_minutes != 1:
            raise EmergingDirectionV2Error("volume bar interval must be one minute")
        if self.data_type != "Last":
            raise EmergingDirectionV2Error("volume bar data_type must be Last")


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


@dataclass(frozen=True)
class ImpulseVolumeEvaluation:
    """Candidate volume and exact prior median, without direction or entry."""

    status: ImpulseVolumeStatus
    volume_qualified: bool
    impulse_candidate_bar_index: int
    candidate_volume: Decimal | None
    reference_volume: Decimal | None
    required_volume: Decimal | None


@dataclass(frozen=True)
class ImpulseBodyWickEvaluation:
    """Exact candidate geometry, qualified only in the supplied emerging direction."""

    status: ImpulseBodyWickStatus
    body_wick_qualified: bool
    impulse_candidate_bar_index: int
    emerging_direction: RegimeDirection | None
    candidate_range: Decimal | None
    body: Decimal | None
    upper_wick: Decimal | None
    lower_wick: Decimal | None


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


def _normalized_trade_volume(value: Decimal | int | None) -> Decimal | None:
    if type(value) is int:
        return Decimal(value)
    if isinstance(value, Decimal) and value.is_finite():
        return value
    return None


def evaluate_impulse_volume_v2(
    *,
    impulse_candidate_bar_index: int,
    bars_by_index: Mapping[int, TradeVolumeBarV2],
) -> ImpulseVolumeEvaluation:
    """Compare Last trade volume with 1.50 times the exact prior-20 median.

    Only the closed candidate t and t-20 through t-1 are accessed. Incomplete
    closed history takes precedence; with complete history, negative volume
    precedes candidate and reference missing/invalid-volume statuses.
    """
    if type(impulse_candidate_bar_index) is not int or impulse_candidate_bar_index < 0:
        raise EmergingDirectionV2Error("candidate index must be a nonnegative integer")
    if not isinstance(bars_by_index, Mapping):
        raise EmergingDirectionV2Error("bars_by_index must be a mapping")

    t = impulse_candidate_bar_index
    if t not in bars_by_index:
        raise EmergingDirectionV2Error("closed candidate bar is required")
    candidate = bars_by_index[t]
    if not isinstance(candidate, TradeVolumeBarV2) or candidate.bar_index != t:
        raise EmergingDirectionV2Error("candidate bar index is inconsistent")
    if candidate.is_closed is not True:
        raise EmergingDirectionV2Error("candidate bar must be closed")

    if t < IMPULSE_VOLUME_LOOKBACK:
        return ImpulseVolumeEvaluation(
            ImpulseVolumeStatus.INSUFFICIENT_WARMUP, False, t, None, None, None
        )
    indices = range(t - IMPULSE_VOLUME_LOOKBACK, t)
    if any(index not in bars_by_index for index in indices):
        return ImpulseVolumeEvaluation(
            ImpulseVolumeStatus.INSUFFICIENT_WARMUP, False, t, None, None, None
        )

    prior = tuple(bars_by_index[index] for index in indices)
    for index, bar in zip(indices, prior, strict=True):
        if not isinstance(bar, TradeVolumeBarV2) or bar.bar_index != index:
            raise EmergingDirectionV2Error("prior volume bar index is inconsistent")
        if bar.is_closed is not True:
            return ImpulseVolumeEvaluation(
                ImpulseVolumeStatus.INSUFFICIENT_WARMUP, False, t, None, None, None
            )
    if any(earlier.timestamp_utc >= later.timestamp_utc for earlier, later in pairwise(prior)):
        raise EmergingDirectionV2Error("prior volume timestamps must increase")
    if prior[-1].timestamp_utc >= candidate.timestamp_utc:
        raise EmergingDirectionV2Error("candidate must follow the prior closed bars")

    candidate_volume = _normalized_trade_volume(candidate.volume)
    reference_volumes = tuple(_normalized_trade_volume(bar.volume) for bar in prior)
    values = (candidate_volume, *reference_volumes)
    if any(value is not None and value < 0 for value in values):
        return ImpulseVolumeEvaluation(
            ImpulseVolumeStatus.INVALID_VOLUME, False, t, candidate_volume, None, None
        )
    if candidate_volume is None:
        return ImpulseVolumeEvaluation(
            ImpulseVolumeStatus.INVALID_CANDIDATE_VOLUME, False, t, None, None, None
        )
    if any(value is None for value in reference_volumes):
        return ImpulseVolumeEvaluation(
            ImpulseVolumeStatus.INVALID_REFERENCE_VOLUME, False, t, candidate_volume, None, None
        )

    valid_references = tuple(value for value in reference_volumes if value is not None)
    exact_values = (candidate_volume, *valid_references)
    precision = max(
        28,
        max(value.adjusted() for value in exact_values)
        - min(value.as_tuple().exponent for value in exact_values)
        + 10,
    )
    with localcontext() as context:
        context.prec = precision
        context.Emax = MAX_EMAX
        context.Emin = MIN_EMIN
        context.traps[Inexact] = True
        ordered_volumes = sorted(valid_references)
        reference_volume = (ordered_volumes[9] + ordered_volumes[10]) / Decimal(2)
        if reference_volume <= 0:
            return ImpulseVolumeEvaluation(
                ImpulseVolumeStatus.INVALID_REFERENCE_VOLUME,
                False,
                t,
                candidate_volume,
                reference_volume,
                None,
            )
        required_volume = IMPULSE_VOLUME_MULTIPLIER * reference_volume
        qualified = candidate_volume >= required_volume

    return ImpulseVolumeEvaluation(
        ImpulseVolumeStatus.EVALUATED,
        qualified,
        t,
        candidate_volume,
        reference_volume,
        required_volume,
    )


def evaluate_impulse_body_wick_v2(
    *,
    impulse_candidate_bar_index: int,
    bars_by_index: Mapping[int, BodyWickBarV2],
    emerging_direction: RegimeDirection | None,
) -> ImpulseBodyWickEvaluation:
    """Require a directional body >= 60% and its terminal wick <= 20% of range.

    Only the closed candidate t is read. OHLC is checked before positive range;
    finite Decimal calculations use exact arithmetic without ratio division or
    pre-comparison rounding. No separate nonterminal-wick bound is imposed.
    """
    if type(impulse_candidate_bar_index) is not int or impulse_candidate_bar_index < 0:
        raise EmergingDirectionV2Error("candidate index must be a nonnegative integer")
    if not isinstance(bars_by_index, Mapping):
        raise EmergingDirectionV2Error("bars_by_index must be a mapping")
    if emerging_direction is not None and not isinstance(emerging_direction, RegimeDirection):
        raise EmergingDirectionV2Error("emerging_direction must be LONG, SHORT or None")

    t = impulse_candidate_bar_index
    if t not in bars_by_index:
        raise EmergingDirectionV2Error("closed candidate bar is required")
    candidate = bars_by_index[t]
    if not isinstance(candidate, BodyWickBarV2) or candidate.bar_index != t:
        raise EmergingDirectionV2Error("candidate bar index is inconsistent")
    if candidate.is_closed is not True:
        raise EmergingDirectionV2Error("candidate bar must be closed")

    values = (candidate.open, candidate.high, candidate.low, candidate.close)
    if not all(isinstance(value, Decimal) and value.is_finite() for value in values) or not (
        candidate.high >= max(candidate.open, candidate.close)
        and candidate.low <= min(candidate.open, candidate.close)
        and candidate.high >= candidate.low
    ):
        return ImpulseBodyWickEvaluation(
            ImpulseBodyWickStatus.INVALID_OHLC,
            False,
            t,
            emerging_direction,
            None,
            None,
            None,
            None,
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
        body = (candidate.close - candidate.open).copy_abs()
        upper_wick = candidate.high - max(candidate.open, candidate.close)
        lower_wick = min(candidate.open, candidate.close) - candidate.low
        if candidate_range <= 0:
            return ImpulseBodyWickEvaluation(
                ImpulseBodyWickStatus.INVALID_CANDIDATE_RANGE,
                False,
                t,
                emerging_direction,
                candidate_range,
                body,
                upper_wick,
                lower_wick,
            )
        strong_body = body >= MIN_BODY_TO_RANGE_RATIO * candidate_range
        terminal_wick_limit = MAX_TERMINAL_WICK_TO_RANGE_RATIO * candidate_range
        qualified = (
            emerging_direction is RegimeDirection.LONG
            and candidate.close > candidate.open
            and strong_body
            and upper_wick <= terminal_wick_limit
        ) or (
            emerging_direction is RegimeDirection.SHORT
            and candidate.close < candidate.open
            and strong_body
            and lower_wick <= terminal_wick_limit
        )

    return ImpulseBodyWickEvaluation(
        ImpulseBodyWickStatus.EVALUATED,
        qualified,
        t,
        emerging_direction,
        candidate_range,
        body,
        upper_wick,
        lower_wick,
    )


__all__ = [
    "EMERGING_DIRECTION_LOOKBACK",
    "IMPULSE_RANGE_LOOKBACK",
    "IMPULSE_RANGE_MULTIPLIER",
    "IMPULSE_VOLUME_LOOKBACK",
    "IMPULSE_VOLUME_MEASURE",
    "IMPULSE_VOLUME_MULTIPLIER",
    "MAX_TERMINAL_WICK_TO_RANGE_RATIO",
    "MIN_BODY_TO_RANGE_RATIO",
    "BodyWickBarV2",
    "EmergingDirectionEvaluation",
    "EmergingDirectionStatus",
    "EmergingDirectionV2Error",
    "ImpulseBodyWickEvaluation",
    "ImpulseBodyWickStatus",
    "ImpulseRangeEvaluation",
    "ImpulseRangeStatus",
    "ImpulseVolumeEvaluation",
    "ImpulseVolumeStatus",
    "StructuralBarV2",
    "TradeVolumeBarV2",
    "evaluate_emerging_direction_v2",
    "evaluate_impulse_body_wick_v2",
    "evaluate_impulse_range_v2",
    "evaluate_impulse_volume_v2",
]
