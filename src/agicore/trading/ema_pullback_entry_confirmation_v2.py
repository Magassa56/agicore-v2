"""Closed-bar V2 entry confirmation and exact MACD; no entry execution.

An immutable opportunity starts from a formally qualified, consumed EMA20
pullback. Only its next two actual closed observations can confirm it. Prices
and indicator values use exact rationals, with no crossover or magnitude test.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from fractions import Fraction

from .ema20_pullback_v2 import (
    EMA20PullbackBarV2,
    EMA20PullbackContextEvaluationV2,
    EMA20PullbackStatusV2,
    _exact_price,
)
from .regime_context_v2 import (
    RegimeContextLifetimeState,
    RegimeDirection,
    RegimeEventContextV2,
    RegimeEventType,
)

MAX_CONFIRMATION_AGE_CLOSED_BARS = 2
MAX_CONFIRMATION_ELAPSED_TIME = timedelta(minutes=2)
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
MACD_WARMUP_CLOSED_BARS = MACD_SLOW + MACD_SIGNAL
MACD_SESSION_RESET = False
NO_MACD_CROSS_REQUIRED = True
NO_MACD_MAGNITUDE_THRESHOLD = True


class EntryConfirmationV2Error(ValueError):
    """Reject inconsistent source records or noncausal observation metadata."""


class MACDStatusV2(StrEnum):
    """Availability of exact closed-close MACD values."""

    INSUFFICIENT_MACD_WARMUP = "INSUFFICIENT_MACD_WARMUP"
    INVALID_MACD_INPUT = "INVALID_MACD_INPUT"
    EVALUATED = "EVALUATED"


class EntryConfirmationStatusV2(StrEnum):
    """Data availability for the most recently evaluated confirmation candidate."""

    NOT_EVALUATED = "NOT_EVALUATED"
    INSUFFICIENT_MACD_WARMUP = "INSUFFICIENT_MACD_WARMUP"
    INVALID_MACD_INPUT = "INVALID_MACD_INPUT"
    INVALID_CONFIRMATION_INPUT = "INVALID_CONFIRMATION_INPUT"
    EVALUATED = "EVALUATED"


class EntryConfirmationStateV2(StrEnum):
    """One-shot opportunity state, independent of the consumed regime context."""

    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
    CONFIRMED = "CONFIRMED"
    EXPIRED_NO_ENTRY_CONFIRMATION = "EXPIRED_NO_ENTRY_CONFIRMATION"
    EXPIRED_CONFIRMATION_ELAPSED_TIME = "EXPIRED_CONFIRMATION_ELAPSED_TIME"


def _validate_clock(index: int, timestamp: datetime, closed: bool) -> None:
    if type(index) is not int or index < 0:
        raise EntryConfirmationV2Error("closed bar index must be a nonnegative integer")
    if (
        not isinstance(timestamp, datetime)
        or timestamp.tzinfo is None
        or timestamp.utcoffset() != timedelta(0)
    ):
        raise EntryConfirmationV2Error("closed bar timestamp must be aware UTC")
    if closed is not True:
        raise EntryConfirmationV2Error("confirmation requires a closed observation")


@dataclass(frozen=True)
class MACDEvaluationV2:
    """Exact MACD prefix, including its previous line and histogram values.

    Early values are exposed for arithmetic verification, but remain ineligible
    for confirmation until 35 actual closed bars, including the candidate, exist.
    """

    status: MACDStatusV2
    through_bar_index: int
    ema12: Fraction | None = None
    ema26: Fraction | None = None
    macd: Fraction | None = None
    signal: Fraction | None = None
    histogram: Fraction | None = None
    previous_macd: Fraction | None = None
    previous_histogram: Fraction | None = None
    known_at_timestamp: datetime | None = None


@dataclass(frozen=True)
class EntryConfirmationOpportunityV2:
    """Preserve the consumed source and the accepted pullback body at Close[k]."""

    consumed_context: RegimeEventContextV2
    pullback_body_low: Fraction
    pullback_body_high: Fraction

    def __post_init__(self) -> None:
        context = self.consumed_context
        if (
            not isinstance(context, RegimeEventContextV2)
            or context.state is not RegimeContextLifetimeState.CONSUMED
            or not isinstance(context.ema_reference, Fraction)
        ):
            raise EntryConfirmationV2Error("opportunity requires a consumed formal EMA20 pullback")
        if (
            not isinstance(self.pullback_body_low, Fraction)
            or not isinstance(self.pullback_body_high, Fraction)
            or self.pullback_body_low > self.pullback_body_high
        ):
            raise EntryConfirmationV2Error("pullback body must have ordered exact bounds")

    @property
    def first_confirmation_bar(self) -> int:
        """First permitted bar; the pullback never confirms itself."""
        return self.consumed_context.pullback_bar_index + 1

    @property
    def last_confirmation_bar(self) -> int:
        """Last permitted bar, inclusive."""
        return self.consumed_context.pullback_bar_index + MAX_CONFIRMATION_AGE_CLOSED_BARS


@dataclass(frozen=True)
class EntryConfirmationCandidateV2:
    """Separate the price predicate from the strict directional momentum test."""

    status: EntryConfirmationStatusV2
    confirmation_bar_index: int
    confirmation_timestamp: datetime
    price_qualified: bool = False
    momentum_qualified: bool = False
    entry_confirmation: bool = False
    macd_evaluation: MACDEvaluationV2 | None = None


@dataclass(frozen=True)
class EntryConfirmationRecordV2:
    """Qualified confirmation provenance and exact values; no order or fill."""

    source_regime_event_types: tuple[RegimeEventType, ...]
    source_regime_event_direction: RegimeDirection
    source_regime_event_bar_index: int
    source_regime_event_timestamp: datetime
    pullback_bar_index: int
    pullback_timestamp: datetime
    ema_reference: Fraction
    confirmation_bar_index: int
    confirmation_timestamp: datetime
    macd: Fraction
    signal: Fraction
    histogram: Fraction
    previous_macd: Fraction
    previous_histogram: Fraction


@dataclass(frozen=True)
class EntryConfirmationEvaluationV2:
    """Streaming state after one known close, keeping its source consumed."""

    state: EntryConfirmationStateV2
    opportunity: EntryConfirmationOpportunityV2
    closed_bar_index: int
    closed_bar_timestamp: datetime
    candidate: EntryConfirmationCandidateV2 | None = None
    confirmation: EntryConfirmationRecordV2 | None = None

    @property
    def entry_confirmation(self) -> bool:
        """Only a terminal qualified record confirms the opportunity."""
        return self.state is EntryConfirmationStateV2.CONFIRMED and self.confirmation is not None

    @property
    def status(self) -> EntryConfirmationStatusV2:
        """Expose candidate availability without confusing it with expiration."""
        return (
            EntryConfirmationStatusV2.NOT_EVALUATED
            if self.candidate is None
            else self.candidate.status
        )


def evaluate_macd_v2(
    *,
    through_bar_index: int,
    bars_by_index: Mapping[int, EMA20PullbackBarV2],
    at_timestamp: datetime | None = None,
) -> MACDEvaluationV2:
    """Compute the exact causal prefix 0..q, never enumerating future bars.

    Seed both EMAs with Close[0], then seed the signal with their zero difference.
    Each recurrence uses Fraction, including exact Decimal conversion. Missing,
    nonfinite or unclosed required closes fail closed, without skipping or reset.
    Clock gaps advance by one actual observation and create no synthetic bars.
    """
    if type(through_bar_index) is not int or through_bar_index < 0:
        raise EntryConfirmationV2Error("MACD index must be a nonnegative integer")
    if at_timestamp is not None:
        _validate_clock(through_bar_index, at_timestamp, True)
    ema12 = ema26 = macd = signal = histogram = None
    previous_macd = previous_histogram = previous_timestamp = None
    for index in range(through_bar_index + 1):
        bar = bars_by_index.get(index)
        if not isinstance(bar, EMA20PullbackBarV2) or not bar.is_closed:
            return MACDEvaluationV2(MACDStatusV2.INVALID_MACD_INPUT, through_bar_index)
        if bar.bar_index != index:
            raise EntryConfirmationV2Error("MACD history bar must match its requested index")
        if (previous_timestamp is not None and bar.timestamp_utc <= previous_timestamp) or (
            at_timestamp is not None and bar.timestamp_utc > at_timestamp
        ):
            raise EntryConfirmationV2Error("MACD history timestamps must be causal and increasing")
        if (
            index == through_bar_index
            and at_timestamp is not None
            and (bar.timestamp_utc != at_timestamp)
        ):
            raise EntryConfirmationV2Error("MACD last bar must match the observed close timestamp")
        close = _exact_price(bar.close)
        if close is None:
            return MACDEvaluationV2(MACDStatusV2.INVALID_MACD_INPUT, through_bar_index)
        previous_macd, previous_histogram = macd, histogram
        if index == 0:
            ema12 = ema26 = close
            macd = signal = histogram = Fraction(0)
        else:
            ema12 += Fraction(2, MACD_FAST + 1) * (close - ema12)
            ema26 += Fraction(2, MACD_SLOW + 1) * (close - ema26)
            macd = ema12 - ema26
            signal += Fraction(2, MACD_SIGNAL + 1) * (macd - signal)
            histogram = macd - signal
        previous_timestamp = bar.timestamp_utc
    status = (
        MACDStatusV2.EVALUATED
        if through_bar_index + 1 >= MACD_WARMUP_CLOSED_BARS
        else MACDStatusV2.INSUFFICIENT_MACD_WARMUP
    )
    return MACDEvaluationV2(
        status,
        through_bar_index,
        ema12,
        ema26,
        macd,
        signal,
        histogram,
        previous_macd,
        previous_histogram,
        previous_timestamp,
    )


def evaluate_macd_momentum_v2(*, direction: RegimeDirection, macd: MACDEvaluationV2) -> bool:
    """Apply all four strict conditions; no crossover or magnitude threshold."""
    if not isinstance(direction, RegimeDirection) or not isinstance(macd, MACDEvaluationV2):
        raise EntryConfirmationV2Error("momentum requires a direction and MACD evaluation")
    if macd.status is not MACDStatusV2.EVALUATED or not all(
        isinstance(value, Fraction)
        for value in (
            macd.macd,
            macd.signal,
            macd.histogram,
            macd.previous_macd,
            macd.previous_histogram,
        )
    ):
        return False
    if direction is RegimeDirection.LONG:
        return (
            macd.macd > macd.signal
            and macd.histogram > 0
            and macd.histogram > macd.previous_histogram
            and macd.macd > macd.previous_macd
        )
    return (
        macd.macd < macd.signal
        and macd.histogram < 0
        and macd.histogram < macd.previous_histogram
        and macd.macd < macd.previous_macd
    )


def begin_entry_confirmation_momentum_v2(
    *,
    pullback: EMA20PullbackContextEvaluationV2,
    pullback_bar: EMA20PullbackBarV2,
) -> EntryConfirmationEvaluationV2:
    """Start AWAITING at Close[k] from the formal consuming pullback snapshot."""
    if not isinstance(pullback, EMA20PullbackContextEvaluationV2):
        raise EntryConfirmationV2Error("confirmation requires the formal pullback transition")
    decision, lifetime = pullback.pullback, pullback.lifetime
    context = lifetime.context
    if (
        decision is None
        or decision.status is not EMA20PullbackStatusV2.EVALUATED
        or decision.pullback_qualified is not True
        or context.state is not RegimeContextLifetimeState.CONSUMED
        or not isinstance(pullback_bar, EMA20PullbackBarV2)
    ):
        raise EntryConfirmationV2Error("confirmation requires a newly qualified consumed pullback")
    k, timestamp = context.pullback_bar_index, context.pullback_timestamp
    if (
        (decision.pullback_bar_index, decision.pullback_timestamp) != (k, timestamp)
        or (lifetime.closed_bar_index, lifetime.closed_bar_timestamp) != (k, timestamp)
        or (pullback_bar.bar_index, pullback_bar.timestamp_utc) != (k, timestamp)
        or decision.context_source_event_types != context.source_event_types
        or decision.context_direction is not context.source_event_direction
        or decision.context_event_bar_index != context.source_event_bar_index
        or decision.context_event_timestamp != context.source_event_timestamp
        or decision.ema_reference != context.ema_reference
    ):
        raise EntryConfirmationV2Error("pullback provenance must match its consumed context")
    _validate_clock(k, timestamp, pullback_bar.is_closed)
    open_, close = _exact_price(pullback_bar.open), _exact_price(pullback_bar.close)
    if open_ is None or close is None:
        raise EntryConfirmationV2Error("qualified pullback must have exact finite body prices")
    opportunity = EntryConfirmationOpportunityV2(context, min(open_, close), max(open_, close))
    return EntryConfirmationEvaluationV2(
        EntryConfirmationStateV2.AWAITING_CONFIRMATION, opportunity, k, timestamp
    )


def _evaluate_candidate(
    opportunity: EntryConfirmationOpportunityV2,
    index: int,
    timestamp: datetime,
    bars: Mapping[int, EMA20PullbackBarV2],
) -> EntryConfirmationCandidateV2:
    bar = bars.get(index)
    if not isinstance(bar, EMA20PullbackBarV2) or not bar.is_closed:
        return EntryConfirmationCandidateV2(
            EntryConfirmationStatusV2.INVALID_CONFIRMATION_INPUT, index, timestamp
        )
    if (bar.bar_index, bar.timestamp_utc) != (index, timestamp):
        raise EntryConfirmationV2Error("confirmation candidate must match the observed close")
    macd = evaluate_macd_v2(through_bar_index=index, bars_by_index=bars, at_timestamp=timestamp)
    open_, close = _exact_price(bar.open), _exact_price(bar.close)
    if open_ is None or close is None:
        status = (
            EntryConfirmationStatusV2.INVALID_MACD_INPUT
            if macd.status is MACDStatusV2.INVALID_MACD_INPUT
            else EntryConfirmationStatusV2.INVALID_CONFIRMATION_INPUT
        )
        return EntryConfirmationCandidateV2(status, index, timestamp, macd_evaluation=macd)
    direction = opportunity.consumed_context.source_event_direction
    price = (
        close > open_ and close > opportunity.pullback_body_high
        if direction is RegimeDirection.LONG
        else close < open_ and close < opportunity.pullback_body_low
    )
    momentum = evaluate_macd_momentum_v2(direction=direction, macd=macd)
    return EntryConfirmationCandidateV2(
        EntryConfirmationStatusV2(macd.status.value),
        index,
        timestamp,
        price,
        momentum,
        price and momentum,
        macd,
    )


def advance_entry_confirmation_momentum_v2(
    *,
    previous: EntryConfirmationEvaluationV2,
    closed_bar_index: int,
    closed_bar_timestamp: datetime,
    source_bar_closed: bool,
    bars_by_index: Mapping[int, EMA20PullbackBarV2],
) -> EntryConfirmationEvaluationV2:
    """Process each next known close in order, with expiry before any price read.

    The first qualifying candidate wins. Terminal opportunities return unchanged
    without reading later bars. Repeating Close[k] is a no-op. Eligible closes must
    be delivered sequentially so k+1 cannot be skipped in favor of k+2. An absent
    later close never produces a synthetic confirmation or reactivates context.
    """
    if not isinstance(previous, EntryConfirmationEvaluationV2):
        raise EntryConfirmationV2Error("advance requires a confirmation opportunity state")
    if previous.state is not EntryConfirmationStateV2.AWAITING_CONFIRMATION:
        return previous
    q, timestamp = closed_bar_index, closed_bar_timestamp
    _validate_clock(q, timestamp, source_bar_closed)
    opportunity = previous.opportunity
    context = opportunity.consumed_context
    k = context.pullback_bar_index
    if q == k and previous.closed_bar_index == k and timestamp == context.pullback_timestamp:
        return previous
    if q <= previous.closed_bar_index or timestamp <= previous.closed_bar_timestamp:
        raise EntryConfirmationV2Error("confirmation closes must advance causally")
    if timestamp - context.pullback_timestamp > MAX_CONFIRMATION_ELAPSED_TIME:
        return EntryConfirmationEvaluationV2(
            EntryConfirmationStateV2.EXPIRED_CONFIRMATION_ELAPSED_TIME,
            opportunity,
            q,
            timestamp,
        )
    if q > opportunity.last_confirmation_bar:
        return EntryConfirmationEvaluationV2(
            EntryConfirmationStateV2.EXPIRED_NO_ENTRY_CONFIRMATION, opportunity, q, timestamp
        )
    if q != previous.closed_bar_index + 1:
        raise EntryConfirmationV2Error(
            "eligible confirmation candidates must be processed in order"
        )
    candidate = _evaluate_candidate(opportunity, q, timestamp, bars_by_index)
    record = None
    if candidate.entry_confirmation:
        macd = candidate.macd_evaluation
        record = EntryConfirmationRecordV2(
            context.source_event_types,
            context.source_event_direction,
            context.source_event_bar_index,
            context.source_event_timestamp,
            k,
            context.pullback_timestamp,
            context.ema_reference,
            q,
            timestamp,
            macd.macd,
            macd.signal,
            macd.histogram,
            macd.previous_macd,
            macd.previous_histogram,
        )
        state = EntryConfirmationStateV2.CONFIRMED
    elif q == opportunity.last_confirmation_bar:
        state = EntryConfirmationStateV2.EXPIRED_NO_ENTRY_CONFIRMATION
    else:
        state = EntryConfirmationStateV2.AWAITING_CONFIRMATION
    return EntryConfirmationEvaluationV2(state, opportunity, q, timestamp, candidate, record)
