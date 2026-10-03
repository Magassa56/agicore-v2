"""Causal composition of distinct V2 impulse and reversal event labels.

Event detection is intentionally outside this module until each predicate is
formally specified. This module creates no entry order or performance result.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum


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


__all__ = [
    "RegimeContextEvaluation",
    "RegimeContextStatus",
    "RegimeContextV2Error",
    "RegimeDirection",
    "RegimeEvent",
    "RegimeEventType",
    "compose_regime_context_v2",
]
