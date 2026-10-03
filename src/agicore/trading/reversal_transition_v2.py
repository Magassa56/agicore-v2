"""Independent, causal prior-direction prerequisite for the V2 reversal family.

Only closes of the five completed bars before candidate t are used. This
module neither reads t nor emits a reversal event or an entry signal.
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


__all__ = [
    "PRIOR_DIRECTION_LOOKBACK",
    "PRIOR_DIRECTION_MIN_STEPS",
    "PriorDirectionBarV2",
    "PriorDirectionStatus",
    "ReversalPriorDirection",
    "ReversalPriorDirectionEvaluation",
    "ReversalTransitionV2Error",
    "evaluate_reversal_prior_direction_v2",
]
