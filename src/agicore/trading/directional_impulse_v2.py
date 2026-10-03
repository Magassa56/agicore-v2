"""Causal pre-impulse direction predicate for the V2 research contract.

Only the three closed bars before candidate ``t`` are inspected. This does not
detect an impulse event or produce an entry signal.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum

from .regime_context_v2 import RegimeDirection

EMERGING_DIRECTION_LOOKBACK = 3


class EmergingDirectionV2Error(ValueError):
    """Reject inconsistent or noncausal pre-impulse observations."""


class EmergingDirectionStatus(StrEnum):
    """Separate incomplete history from an evaluated predicate with no direction."""

    INSUFFICIENT_WARMUP = "INSUFFICIENT_WARMUP"
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


__all__ = [
    "EMERGING_DIRECTION_LOOKBACK",
    "EmergingDirectionEvaluation",
    "EmergingDirectionStatus",
    "EmergingDirectionV2Error",
    "StructuralBarV2",
    "evaluate_emerging_direction_v2",
]
