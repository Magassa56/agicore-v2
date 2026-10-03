"""Exact closed-close EMA20 and causal V2 pullback, without entry execution.

Bar indices enumerate actual observations from zero, including across clock
gaps. EMA history is never reset or filled with synthetic observations. The
candidate uses the exact EMA of its prior bar throughout its own price test.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from fractions import Fraction

from .regime_context_v2 import (
    MAX_CONTEXT_ELAPSED_TIME,
    RegimeContextLifetimeEvaluation,
    RegimeContextLifetimeState,
    RegimeDirection,
    RegimeEvent,
    RegimeEventContextV2,
    RegimeEventType,
    advance_regime_context_v2,
)

EMA_PERIOD = 20
ALPHA = Fraction(2, 21)
EMA_RESET_AT_SESSION = False


class EMA20PullbackV2Error(ValueError):
    """Reject inconsistent or noncausal observation metadata."""


class EMA20StatusV2(StrEnum):
    """Exact EMA availability, independent of context and candidate geometry."""

    INSUFFICIENT_EMA_WARMUP = "INSUFFICIENT_EMA_WARMUP"
    INVALID_EMA_INPUT = "INVALID_EMA_INPUT"
    EVALUATED = "EVALUATED"


class EMA20PullbackStatusV2(StrEnum):
    """Distinguish context eligibility, data validity and evaluated geometry."""

    INELIGIBLE_CONTEXT = "INELIGIBLE_CONTEXT"
    INSUFFICIENT_EMA_WARMUP = "INSUFFICIENT_EMA_WARMUP"
    INVALID_EMA_INPUT = "INVALID_EMA_INPUT"
    INVALID_OHLC = "INVALID_OHLC"
    EVALUATED = "EVALUATED"


@dataclass(frozen=True)
class EMA20PullbackBarV2:
    """OHLC observation; invalid prices reach explicit evaluator statuses.

    Decimal, integer and Fraction prices preserve their exact values. Binary
    floats are rejected rather than interpreted as decimal market prices.
    Historical EMA computation reads only close and causal metadata.
    """

    bar_index: int
    timestamp_utc: datetime
    open: Decimal | int | Fraction | None
    high: Decimal | int | Fraction | None
    low: Decimal | int | Fraction | None
    close: Decimal | int | Fraction | None
    is_closed: bool

    def __post_init__(self) -> None:
        if type(self.bar_index) is not int or self.bar_index < 0:
            raise EMA20PullbackV2Error("bar_index must be a nonnegative integer")
        if (
            not isinstance(self.timestamp_utc, datetime)
            or self.timestamp_utc.tzinfo is None
            or self.timestamp_utc.utcoffset() != timedelta(0)
        ):
            raise EMA20PullbackV2Error("bar timestamp must be aware UTC")
        if type(self.is_closed) is not bool:
            raise EMA20PullbackV2Error("is_closed must be a boolean")


@dataclass(frozen=True)
class EMA20EvaluationV2:
    """EMA known at the last required close, without reading any later bar."""

    status: EMA20StatusV2
    through_bar_index: int
    ema20: Fraction | None = None
    last_close: Fraction | None = None
    known_at_timestamp: datetime | None = None


@dataclass(frozen=True)
class EMA20PullbackEvaluationV2:
    """Closed-bar pullback decision with exact reference and source provenance."""

    status: EMA20PullbackStatusV2
    pullback_qualified: bool
    pullback_bar_index: int
    pullback_timestamp: datetime
    context_source_event_types: tuple[RegimeEventType, ...]
    context_direction: RegimeDirection | None
    context_event_bar_index: int | None
    context_event_timestamp: datetime | None
    ema_reference: Fraction | None


@dataclass(frozen=True)
class EMA20PullbackContextEvaluationV2:
    """Frozen lifetime transition plus the formal pullback decision, if eligible."""

    lifetime: RegimeContextLifetimeEvaluation
    pullback: EMA20PullbackEvaluationV2 | None


def _exact_price(value: object) -> Fraction | None:
    if isinstance(value, Fraction) or type(value) is int:
        return Fraction(value)
    if isinstance(value, Decimal) and value.is_finite():
        return Fraction(value)
    return None


def evaluate_ema20_v2(
    *,
    through_bar_index: int,
    bars_by_index: Mapping[int, EMA20PullbackBarV2],
    before_timestamp: datetime | None = None,
) -> EMA20EvaluationV2:
    """Compute seed at 19 and exact recurrence through the requested closed bar.

    Only explicit indices 0..through_bar_index are read. Missing required bars,
    unclosed observations or invalid closes make the EMA unavailable; they are
    never skipped, substituted or used to start a later seed. Clock gaps are
    allowed and do not create observations. before_timestamp, when supplied,
    rejects prior observations not known before the candidate opens.
    """
    if type(through_bar_index) is not int or through_bar_index < 0:
        raise EMA20PullbackV2Error("through_bar_index must be a nonnegative integer")
    if before_timestamp is not None and (
        not isinstance(before_timestamp, datetime)
        or before_timestamp.tzinfo is None
        or before_timestamp.utcoffset() != timedelta(0)
    ):
        raise EMA20PullbackV2Error("before_timestamp must be aware UTC")
    if through_bar_index < EMA_PERIOD - 1:
        return EMA20EvaluationV2(EMA20StatusV2.INSUFFICIENT_EMA_WARMUP, through_bar_index)

    seed_sum = Fraction(0)
    ema = None
    previous_timestamp = None
    for index in range(through_bar_index + 1):
        bar = bars_by_index.get(index)
        if not isinstance(bar, EMA20PullbackBarV2) or not bar.is_closed:
            return EMA20EvaluationV2(EMA20StatusV2.INVALID_EMA_INPUT, through_bar_index)
        if bar.bar_index != index:
            raise EMA20PullbackV2Error("EMA history bar must match its requested index")
        if (previous_timestamp is not None and bar.timestamp_utc <= previous_timestamp) or (
            before_timestamp is not None and bar.timestamp_utc >= before_timestamp
        ):
            raise EMA20PullbackV2Error("EMA history timestamps must be causal and increasing")
        close = _exact_price(bar.close)
        if close is None:
            return EMA20EvaluationV2(EMA20StatusV2.INVALID_EMA_INPUT, through_bar_index)
        if index < EMA_PERIOD:
            seed_sum += close
            if index == EMA_PERIOD - 1:
                ema = seed_sum / EMA_PERIOD
        else:
            ema = (2 * close + 19 * ema) / 21
        previous_timestamp = bar.timestamp_utc
    return EMA20EvaluationV2(
        EMA20StatusV2.EVALUATED, through_bar_index, ema, close, previous_timestamp
    )


def evaluate_ema20_pullback_v2(
    *,
    pullback_candidate_bar_index: int,
    bars_by_index: Mapping[int, EMA20PullbackBarV2],
    context: RegimeEventContextV2,
) -> EMA20PullbackEvaluationV2:
    """Evaluate only EMA20[k-1] geometry for an already ACTIVE eligible context.

    This pure decision neither creates nor refreshes nor consumes context.
    advance_ema20_pullback_v2 applies its result through the frozen lifecycle.
    """
    k = pullback_candidate_bar_index
    if type(k) is not int or k < 0:
        raise EMA20PullbackV2Error("pullback candidate index must be a nonnegative integer")
    if not isinstance(context, RegimeEventContextV2):
        raise EMA20PullbackV2Error("pullback requires a regime context record")
    candidate = bars_by_index.get(k)
    if (
        not isinstance(candidate, EMA20PullbackBarV2)
        or candidate.bar_index != k
        or candidate.is_closed is not True
    ):
        raise EMA20PullbackV2Error("pullback requires the indexed closed candidate bar")

    def result(status, qualified=False, reference=None):
        return EMA20PullbackEvaluationV2(
            status,
            qualified,
            k,
            candidate.timestamp_utc,
            context.source_event_types,
            context.source_event_direction,
            context.source_event_bar_index,
            context.source_event_timestamp,
            reference,
        )

    if (
        context.state is not RegimeContextLifetimeState.ACTIVE
        or not context.first_eligible_pullback_bar <= k <= context.last_eligible_pullback_bar
        or not timedelta(0)
        < candidate.timestamp_utc - context.source_event_timestamp
        <= MAX_CONTEXT_ELAPSED_TIME
    ):
        return result(EMA20PullbackStatusV2.INELIGIBLE_CONTEXT)
    if k < EMA_PERIOD:
        return result(EMA20PullbackStatusV2.INSUFFICIENT_EMA_WARMUP)
    ema = evaluate_ema20_v2(
        through_bar_index=k - 1,
        bars_by_index=bars_by_index,
        before_timestamp=candidate.timestamp_utc,
    )
    if ema.status is not EMA20StatusV2.EVALUATED:
        return result(EMA20PullbackStatusV2(ema.status.value))
    reference = ema.ema20
    close = _exact_price(candidate.close)
    if close is None:
        return result(EMA20PullbackStatusV2.INVALID_EMA_INPUT, reference=reference)
    open_, high, low = (
        _exact_price(value) for value in (candidate.open, candidate.high, candidate.low)
    )
    if (
        open_ is None
        or high is None
        or low is None
        or high < max(open_, close)
        or low > min(open_, close)
        or high < low
    ):
        return result(EMA20PullbackStatusV2.INVALID_OHLC, reference=reference)
    if context.source_event_direction is RegimeDirection.LONG:
        qualified = (
            ema.last_close > reference
            and open_ >= reference
            and low <= reference
            and close > reference
        )
    else:
        qualified = (
            ema.last_close < reference
            and open_ <= reference
            and high >= reference
            and close < reference
        )
    return result(EMA20PullbackStatusV2.EVALUATED, qualified, reference)


def advance_ema20_pullback_v2(
    *,
    previous: RegimeContextLifetimeEvaluation | None,
    closed_bar_index: int,
    closed_bar_timestamp: datetime,
    source_bar_closed: bool,
    bars_by_index: Mapping[int, EMA20PullbackBarV2],
    directional_impulse_event: RegimeEvent | None = None,
    reversal_transition_event: RegimeEvent | None = None,
    end_of_data: bool = False,
) -> EMA20PullbackContextEvaluationV2:
    """Apply expiry/composition before formal geometry and one-shot consumption.

    Store EMA20[k-1] in the consumed source record without altering the frozen
    lifetime rules. An ineligible, invalidated or consumed context never calls
    the price predicate. This function emits no confirmation or entry order.
    """
    pullback = None

    def predicate(context, k, timestamp):
        nonlocal pullback
        candidate = bars_by_index.get(k)
        if isinstance(candidate, EMA20PullbackBarV2) and candidate.timestamp_utc != timestamp:
            raise EMA20PullbackV2Error("candidate timestamp must match the lifetime closed bar")
        pullback = evaluate_ema20_pullback_v2(
            pullback_candidate_bar_index=k, bars_by_index=bars_by_index, context=context
        )
        return pullback.pullback_qualified

    lifetime = advance_regime_context_v2(
        previous=previous,
        closed_bar_index=closed_bar_index,
        closed_bar_timestamp=closed_bar_timestamp,
        source_bar_closed=source_bar_closed,
        directional_impulse_event=directional_impulse_event,
        reversal_transition_event=reversal_transition_event,
        ema20_pullback_qualified=predicate,
        end_of_data=end_of_data,
    )
    if pullback is not None and pullback.pullback_qualified:
        lifetime = replace(
            lifetime, context=replace(lifetime.context, ema_reference=pullback.ema_reference)
        )
    return EMA20PullbackContextEvaluationV2(lifetime, pullback)


__all__ = [
    "ALPHA",
    "EMA_PERIOD",
    "EMA_RESET_AT_SESSION",
    "EMA20EvaluationV2",
    "EMA20PullbackBarV2",
    "EMA20PullbackContextEvaluationV2",
    "EMA20PullbackEvaluationV2",
    "EMA20PullbackStatusV2",
    "EMA20PullbackV2Error",
    "EMA20StatusV2",
    "advance_ema20_pullback_v2",
    "evaluate_ema20_pullback_v2",
    "evaluate_ema20_v2",
]
