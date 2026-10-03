"""Causal V2 event composition and bounded, one-shot context lifetime.

Event detection and the formal EMA20 pullback predicate remain external.
This module creates no entry order or performance result.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from enum import StrEnum

MAX_CONTEXT_AGE_CLOSED_BARS = 8
MAX_CONTEXT_ELAPSED_TIME = timedelta(minutes=8)
CONTEXT_REUSE = "ONE_SHOT"
SAME_DIRECTION_REFRESH = "DISABLED"


class RegimeContextV2Error(ValueError):
    """Reject malformed or noncausal V2 event composition inputs."""


class RegimeEventType(StrEnum):
    """Independent event families permitted by the V2 architecture."""

    DIRECTIONAL_IMPULSE_EVENT = "DIRECTIONAL_IMPULSE_EVENT"
    REVERSAL_TRANSITION_EVENT = "REVERSAL_TRANSITION_EVENT"


class RegimeDirection(StrEnum):
    """Direction implied by an already qualified source event."""

    LONG = "LONG"
    SHORT = "SHORT"


class RegimeContextStatus(StrEnum):
    """Outcome before momentum, trend acceptance, pullback, or entry rules."""

    UNQUALIFIED = "UNQUALIFIED"
    QUALIFIED = "QUALIFIED"
    AMBIGUOUS = "AMBIGUOUS"


def _require_closed_utc_timestamp(value: datetime) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise RegimeContextV2Error("event timestamp must be aware UTC")


@dataclass(frozen=True)
class RegimeEvent:
    """One event emitted from a closed bar by a future dedicated predicate."""

    event_type: RegimeEventType
    event_direction: RegimeDirection
    event_bar_index: int
    event_timestamp: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.event_type, RegimeEventType):
            raise RegimeContextV2Error("event_type must name one V2 event family")
        if not isinstance(self.event_direction, RegimeDirection):
            raise RegimeContextV2Error("event_direction must be LONG or SHORT")
        if type(self.event_bar_index) is not int or self.event_bar_index < 0:
            raise RegimeContextV2Error("event_bar_index must be a nonnegative integer")
        _require_closed_utc_timestamp(self.event_timestamp)


@dataclass(frozen=True)
class RegimeContextEvaluation:
    """Event composition only; qualification is not a complete entry signal."""

    closed_bar_index: int
    closed_bar_timestamp: datetime
    status: RegimeContextStatus
    event_direction: RegimeDirection | None
    events: tuple[RegimeEvent, ...]

    @property
    def regime_context_qualified(self) -> bool:
        """Whether event composition may advance to later V2 context stages."""
        return self.status is RegimeContextStatus.QUALIFIED

    @property
    def entry_blocked_by_context(self) -> bool:
        """Block entries on absent or conflicting context; other gates still apply."""
        return not self.regime_context_qualified


def compose_regime_context_v2(
    *,
    closed_bar_index: int,
    closed_bar_timestamp: datetime,
    source_bar_closed: bool,
    directional_impulse_event: RegimeEvent | None,
    reversal_transition_event: RegimeEvent | None,
) -> RegimeContextEvaluation:
    """Compose at most one event of each family on the same known closed bar."""
    if type(closed_bar_index) is not int or closed_bar_index < 0:
        raise RegimeContextV2Error("closed_bar_index must be a nonnegative integer")
    _require_closed_utc_timestamp(closed_bar_timestamp)
    if source_bar_closed is not True:
        raise RegimeContextV2Error("V2 event composition requires a closed source bar")

    for event, required_type in (
        (directional_impulse_event, RegimeEventType.DIRECTIONAL_IMPULSE_EVENT),
        (reversal_transition_event, RegimeEventType.REVERSAL_TRANSITION_EVENT),
    ):
        if event is None:
            continue
        if not isinstance(event, RegimeEvent) or event.event_type is not required_type:
            raise RegimeContextV2Error("event must match its independent family")
        if (
            event.event_bar_index != closed_bar_index
            or event.event_timestamp != closed_bar_timestamp
        ):
            raise RegimeContextV2Error("event must belong to the current closed bar")

    events = tuple(
        event
        for event in (directional_impulse_event, reversal_transition_event)
        if event is not None
    )
    if not events:
        status = RegimeContextStatus.UNQUALIFIED
        direction = None
    elif len(events) == 2 and events[0].event_direction is not events[1].event_direction:
        status = RegimeContextStatus.AMBIGUOUS
        direction = None
    else:
        status = RegimeContextStatus.QUALIFIED
        direction = events[0].event_direction

    return RegimeContextEvaluation(
        closed_bar_index=closed_bar_index,
        closed_bar_timestamp=closed_bar_timestamp,
        status=status,
        event_direction=direction,
        events=events,
    )


class RegimeContextLifetimeState(StrEnum):
    """Current or terminal state of one source context, never an entry order."""

    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"
    CONSUMED = "CONSUMED"
    EXPIRED_MAX_AGE = "EXPIRED_MAX_AGE"
    EXPIRED_ELAPSED_TIME = "EXPIRED_ELAPSED_TIME"
    INVALIDATED_OPPOSITE_EVENT = "INVALIDATED_OPPOSITE_EVENT"
    INVALIDATED_AMBIGUOUS_EVENT = "INVALIDATED_AMBIGUOUS_EVENT"
    EXPIRED_END_OF_DATA = "EXPIRED_END_OF_DATA"


class RegimeContextLifetimeNotice(StrEnum):
    """Audit notice that preserves the original source and age."""

    SAME_DIRECTION_EVENT_IGNORED_NO_REFRESH = "SAME_DIRECTION_EVENT_IGNORED_NO_REFRESH"


@dataclass(frozen=True)
class RegimeEventContextV2:
    """Immutable provenance of one context, including its one qualified pullback."""

    state: RegimeContextLifetimeState = RegimeContextLifetimeState.INACTIVE
    source_event_types: tuple[RegimeEventType, ...] = ()
    source_event_direction: RegimeDirection | None = None
    source_event_bar_index: int | None = None
    source_event_timestamp: datetime | None = None
    pullback_bar_index: int | None = None
    pullback_timestamp: datetime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.state, RegimeContextLifetimeState):
            raise RegimeContextV2Error("context state must name a lifetime state")
        if not isinstance(self.source_event_types, tuple):
            raise RegimeContextV2Error("source event types must be an immutable tuple")
        if self.state is RegimeContextLifetimeState.INACTIVE:
            if self.source_event_types or any(
                value is not None
                for value in (
                    self.source_event_direction,
                    self.source_event_bar_index,
                    self.source_event_timestamp,
                    self.pullback_bar_index,
                    self.pullback_timestamp,
                )
            ):
                raise RegimeContextV2Error("inactive context cannot carry source or pullback")
            return
        if (
            not self.source_event_types
            or any(not isinstance(family, RegimeEventType) for family in self.source_event_types)
            or len(set(self.source_event_types)) != len(self.source_event_types)
        ):
            raise RegimeContextV2Error("context needs distinct source event families")
        for family in self.source_event_types:
            RegimeEvent(
                family,
                self.source_event_direction,
                self.source_event_bar_index,
                self.source_event_timestamp,
            )
        if self.state is RegimeContextLifetimeState.CONSUMED:
            if (
                type(self.pullback_bar_index) is not int
                or not self.first_eligible_pullback_bar
                <= self.pullback_bar_index
                <= self.last_eligible_pullback_bar
            ):
                raise RegimeContextV2Error("consumed pullback must belong to e+1..e+8")
            _require_closed_utc_timestamp(self.pullback_timestamp)
            if (
                not timedelta(0)
                < self.pullback_timestamp - self.source_event_timestamp
                <= MAX_CONTEXT_ELAPSED_TIME
            ):
                raise RegimeContextV2Error(
                    "consumed pullback must be within eight minutes after source"
                )
        elif self.pullback_bar_index is not None or self.pullback_timestamp is not None:
            raise RegimeContextV2Error("only consumed context may carry a qualified pullback")

    @property
    def first_eligible_pullback_bar(self) -> int | None:
        """Exclude the source event's own bar from pullback eligibility."""
        return None if self.source_event_bar_index is None else self.source_event_bar_index + 1

    @property
    def last_eligible_pullback_bar(self) -> int | None:
        """Keep the eighth subsequent closed bar inclusive."""
        return (
            None
            if self.source_event_bar_index is None
            else self.source_event_bar_index + MAX_CONTEXT_AGE_CLOSED_BARS
        )


@dataclass(frozen=True)
class RegimeContextLifetimeEvaluation:
    """One closed-bar transition and any retired source records for caller audit."""

    closed_bar_index: int
    closed_bar_timestamp: datetime
    composition: RegimeContextEvaluation
    context: RegimeEventContextV2
    retired_contexts: tuple[RegimeEventContextV2, ...] = ()
    notices: tuple[RegimeContextLifetimeNotice, ...] = ()
    pullback_evaluated: bool = False
    end_of_data: bool = False

    @property
    def state(self) -> RegimeContextLifetimeState:
        """Expose the current source's lifetime state."""
        return self.context.state


def advance_regime_context_v2(
    *,
    previous: RegimeContextLifetimeEvaluation | None,
    closed_bar_index: int,
    closed_bar_timestamp: datetime,
    source_bar_closed: bool,
    directional_impulse_event: RegimeEvent | None = None,
    reversal_transition_event: RegimeEvent | None = None,
    ema20_pullback_qualified: Callable[[RegimeEventContextV2, int, datetime], bool] | None = None,
    end_of_data: bool = False,
) -> RegimeContextLifetimeEvaluation:
    """Advance expiry, composition, invalidation, no-refresh, then qualified pullback.

    Only current closed-bar inputs are accepted. The future formal pullback
    callback is invoked only for an eligible surviving context, never its event
    bar. No callback means no qualified pullback. At e+8, failed qualification
    expires after this opportunity; elapsed time >8 minutes expires beforehand.
    Terminal source records remain terminal and new events create new records.
    """
    if type(closed_bar_index) is not int or closed_bar_index < 0:
        raise RegimeContextV2Error("closed_bar_index must be a nonnegative integer")
    _require_closed_utc_timestamp(closed_bar_timestamp)
    if source_bar_closed is not True:
        raise RegimeContextV2Error("context lifetime requires a closed source bar")
    if type(end_of_data) is not bool:
        raise RegimeContextV2Error("end_of_data must be a boolean")
    if ema20_pullback_qualified is not None and not callable(ema20_pullback_qualified):
        raise RegimeContextV2Error("formal pullback evaluator must be callable")
    if previous is not None:
        if not isinstance(previous, RegimeContextLifetimeEvaluation) or not isinstance(
            previous.context, RegimeEventContextV2
        ):
            raise RegimeContextV2Error("previous must be a context lifetime evaluation")
        if previous.end_of_data:
            raise RegimeContextV2Error("ended series cannot carry context to another bar or series")
        if (
            closed_bar_index <= previous.closed_bar_index
            or closed_bar_timestamp <= previous.closed_bar_timestamp
        ):
            raise RegimeContextV2Error("closed bar index and timestamp must strictly increase")
        if previous.context.source_event_bar_index is not None and (
            previous.context.source_event_bar_index > previous.closed_bar_index
            or previous.context.source_event_timestamp > previous.closed_bar_timestamp
            or (
                previous.context.pullback_bar_index is not None
                and previous.context.pullback_bar_index > previous.closed_bar_index
            )
            or (
                previous.context.pullback_timestamp is not None
                and previous.context.pullback_timestamp > previous.closed_bar_timestamp
            )
        ):
            raise RegimeContextV2Error("previous context contains future provenance")

    context = RegimeEventContextV2() if previous is None else previous.context
    retired: list[RegimeEventContextV2] = []
    notices: list[RegimeContextLifetimeNotice] = []
    if context.state is RegimeContextLifetimeState.ACTIVE:
        if closed_bar_timestamp - context.source_event_timestamp > MAX_CONTEXT_ELAPSED_TIME:
            context = replace(context, state=RegimeContextLifetimeState.EXPIRED_ELAPSED_TIME)
            retired.append(context)
        elif closed_bar_index - context.source_event_bar_index > MAX_CONTEXT_AGE_CLOSED_BARS:
            context = replace(context, state=RegimeContextLifetimeState.EXPIRED_MAX_AGE)
            retired.append(context)

    composition = compose_regime_context_v2(
        closed_bar_index=closed_bar_index,
        closed_bar_timestamp=closed_bar_timestamp,
        source_bar_closed=source_bar_closed,
        directional_impulse_event=directional_impulse_event,
        reversal_transition_event=reversal_transition_event,
    )
    if composition.status is RegimeContextStatus.AMBIGUOUS:
        if context.state is RegimeContextLifetimeState.ACTIVE:
            context = replace(context, state=RegimeContextLifetimeState.INVALIDATED_AMBIGUOUS_EVENT)
            retired.append(context)
    elif composition.status is RegimeContextStatus.QUALIFIED:
        if (
            context.state is RegimeContextLifetimeState.ACTIVE
            and context.source_event_direction is composition.event_direction
        ):
            notices.append(RegimeContextLifetimeNotice.SAME_DIRECTION_EVENT_IGNORED_NO_REFRESH)
        else:
            if context.state is RegimeContextLifetimeState.ACTIVE:
                context = replace(
                    context, state=RegimeContextLifetimeState.INVALIDATED_OPPOSITE_EVENT
                )
            if context.state is not RegimeContextLifetimeState.INACTIVE and context not in retired:
                retired.append(context)
            context = RegimeEventContextV2(
                state=RegimeContextLifetimeState.ACTIVE,
                source_event_types=tuple(event.event_type for event in composition.events),
                source_event_direction=composition.event_direction,
                source_event_bar_index=closed_bar_index,
                source_event_timestamp=closed_bar_timestamp,
            )

    evaluated = False
    if (
        context.state is RegimeContextLifetimeState.ACTIVE
        and closed_bar_index > context.source_event_bar_index
    ):
        if ema20_pullback_qualified is not None:
            evaluated = True
            qualified = ema20_pullback_qualified(context, closed_bar_index, closed_bar_timestamp)
            if type(qualified) is not bool:
                raise RegimeContextV2Error("formal pullback qualification must be a boolean")
            if qualified:
                context = replace(
                    context,
                    state=RegimeContextLifetimeState.CONSUMED,
                    pullback_bar_index=closed_bar_index,
                    pullback_timestamp=closed_bar_timestamp,
                )
        if (
            context.state is RegimeContextLifetimeState.ACTIVE
            and closed_bar_index == context.last_eligible_pullback_bar
        ):
            context = replace(context, state=RegimeContextLifetimeState.EXPIRED_MAX_AGE)
            retired.append(context)
    if end_of_data and context.state is RegimeContextLifetimeState.ACTIVE:
        context = replace(context, state=RegimeContextLifetimeState.EXPIRED_END_OF_DATA)
        retired.append(context)
    return RegimeContextLifetimeEvaluation(
        closed_bar_index,
        closed_bar_timestamp,
        composition,
        context,
        tuple(retired),
        tuple(notices),
        evaluated,
        end_of_data,
    )


def finish_regime_context_v2(
    previous: RegimeContextLifetimeEvaluation,
) -> RegimeContextLifetimeEvaluation:
    """End the current series without a fabricated bar, pullback or entry."""
    if not isinstance(previous, RegimeContextLifetimeEvaluation):
        raise RegimeContextV2Error("previous must be a context lifetime evaluation")
    if previous.end_of_data:
        return previous
    context = previous.context
    retired = previous.retired_contexts
    if context.state is RegimeContextLifetimeState.ACTIVE:
        context = replace(context, state=RegimeContextLifetimeState.EXPIRED_END_OF_DATA)
        retired = (*retired, context)
    return replace(previous, context=context, retired_contexts=retired, end_of_data=True)


__all__ = [
    "CONTEXT_REUSE",
    "MAX_CONTEXT_AGE_CLOSED_BARS",
    "MAX_CONTEXT_ELAPSED_TIME",
    "SAME_DIRECTION_REFRESH",
    "RegimeContextEvaluation",
    "RegimeContextLifetimeEvaluation",
    "RegimeContextLifetimeNotice",
    "RegimeContextLifetimeState",
    "RegimeContextStatus",
    "RegimeContextV2Error",
    "RegimeDirection",
    "RegimeEvent",
    "RegimeEventContextV2",
    "RegimeEventType",
    "advance_regime_context_v2",
    "compose_regime_context_v2",
    "finish_regime_context_v2",
]
