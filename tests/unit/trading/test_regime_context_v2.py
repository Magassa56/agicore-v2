"""Synthetic V2 event composition tests without market data or event thresholds."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

import pytest

from agicore.trading.regime_context_v2 import (
    RegimeContextStatus,
    RegimeContextV2Error,
    RegimeDirection,
    RegimeEvent,
    RegimeEventType,
    compose_regime_context_v2,
)

BAR_INDEX = 17
BAR_TIMESTAMP = datetime(2026, 10, 3, 14, 17, tzinfo=UTC)


def _event(event_type: RegimeEventType, direction: RegimeDirection) -> RegimeEvent:
    return RegimeEvent(event_type, direction, BAR_INDEX, BAR_TIMESTAMP)


def _compose(
    impulse: RegimeEvent | None = None,
    reversal: RegimeEvent | None = None,
    *,
    index: int = BAR_INDEX,
    timestamp: datetime = BAR_TIMESTAMP,
    closed: bool = True,
):
    return compose_regime_context_v2(
        closed_bar_index=index,
        closed_bar_timestamp=timestamp,
        source_bar_closed=closed,
        directional_impulse_event=impulse,
        reversal_transition_event=reversal,
    )


@pytest.mark.parametrize("direction", [RegimeDirection.LONG, RegimeDirection.SHORT])
@pytest.mark.parametrize(
    "family",
    [RegimeEventType.DIRECTIONAL_IMPULSE_EVENT, RegimeEventType.REVERSAL_TRANSITION_EVENT],
)
def test_either_independent_family_qualifies_by_itself(
    family: RegimeEventType, direction: RegimeDirection
) -> None:
    event = _event(family, direction)
    result = _compose(
        impulse=event if family is RegimeEventType.DIRECTIONAL_IMPULSE_EVENT else None,
        reversal=event if family is RegimeEventType.REVERSAL_TRANSITION_EVENT else None,
    )

    assert result.status is RegimeContextStatus.QUALIFIED
    assert result.event_direction is direction
    assert result.events == (event,)
    assert result.regime_context_qualified is True
    assert result.entry_blocked_by_context is False
    assert result.closed_bar_index == BAR_INDEX
    assert result.closed_bar_timestamp == BAR_TIMESTAMP


@pytest.mark.parametrize("direction", [RegimeDirection.LONG, RegimeDirection.SHORT])
def test_same_direction_collision_preserves_both_labels_without_priority(
    direction: RegimeDirection,
) -> None:
    impulse = _event(RegimeEventType.DIRECTIONAL_IMPULSE_EVENT, direction)
    reversal = _event(RegimeEventType.REVERSAL_TRANSITION_EVENT, direction)

    result = _compose(impulse, reversal)

    assert result.status is RegimeContextStatus.QUALIFIED
    assert result.regime_context_qualified is True
    assert result.event_direction is direction
    assert result.events == (impulse, reversal)
    assert {event.event_type for event in result.events} == {
        RegimeEventType.DIRECTIONAL_IMPULSE_EVENT,
        RegimeEventType.REVERSAL_TRANSITION_EVENT,
    }


@pytest.mark.parametrize(
    ("impulse_direction", "reversal_direction"),
    [
        (RegimeDirection.LONG, RegimeDirection.SHORT),
        (RegimeDirection.SHORT, RegimeDirection.LONG),
    ],
)
def test_opposite_direction_collision_blocks_context_and_entry(
    impulse_direction: RegimeDirection, reversal_direction: RegimeDirection
) -> None:
    impulse = _event(RegimeEventType.DIRECTIONAL_IMPULSE_EVENT, impulse_direction)
    reversal = _event(RegimeEventType.REVERSAL_TRANSITION_EVENT, reversal_direction)

    result = _compose(impulse, reversal)

    assert result.status is RegimeContextStatus.AMBIGUOUS
    assert result.event_direction is None
    assert result.regime_context_qualified is False
    assert result.entry_blocked_by_context is True
    assert result.events == (impulse, reversal)


def test_absent_events_do_not_qualify() -> None:
    result = _compose()

    assert result.status is RegimeContextStatus.UNQUALIFIED
    assert result.events == ()
    assert result.event_direction is None
    assert result.entry_blocked_by_context is True


def test_repeated_composition_is_deterministic_and_keeps_source_events_immutable() -> None:
    impulse = _event(RegimeEventType.DIRECTIONAL_IMPULSE_EVENT, RegimeDirection.LONG)
    reversal = _event(RegimeEventType.REVERSAL_TRANSITION_EVENT, RegimeDirection.LONG)

    assert _compose(impulse, reversal) == _compose(impulse, reversal)
    assert impulse.event_type is RegimeEventType.DIRECTIONAL_IMPULSE_EVENT
    assert reversal.event_type is RegimeEventType.REVERSAL_TRANSITION_EVENT


@pytest.mark.parametrize("closed", [False, None, 1])
def test_unclosed_or_invalid_bar_is_rejected(closed: object) -> None:
    with pytest.raises(RegimeContextV2Error, match="closed source bar"):
        _compose(
            _event(RegimeEventType.DIRECTIONAL_IMPULSE_EVENT, RegimeDirection.LONG), closed=closed
        )


@pytest.mark.parametrize("index", [True, -1, 18])
def test_wrong_or_future_bar_index_is_rejected(index: object) -> None:
    with pytest.raises(RegimeContextV2Error, match="closed_bar_index|current closed bar"):
        _compose(
            _event(RegimeEventType.DIRECTIONAL_IMPULSE_EVENT, RegimeDirection.LONG), index=index
        )


@pytest.mark.parametrize(
    "timestamp",
    [
        BAR_TIMESTAMP + timedelta(minutes=1),
        BAR_TIMESTAMP.replace(tzinfo=None),
        BAR_TIMESTAMP.replace(tzinfo=timezone(timedelta(hours=1))),
    ],
)
def test_timestamp_mismatch_or_non_utc_is_rejected(timestamp: datetime) -> None:
    with pytest.raises(RegimeContextV2Error, match="aware UTC|current closed bar"):
        _compose(
            _event(RegimeEventType.DIRECTIONAL_IMPULSE_EVENT, RegimeDirection.LONG),
            timestamp=timestamp,
        )


@pytest.mark.parametrize(
    ("event_type", "direction", "index", "timestamp"),
    [
        ("DIRECTIONAL_IMPULSE_EVENT", RegimeDirection.LONG, BAR_INDEX, BAR_TIMESTAMP),
        (RegimeEventType.DIRECTIONAL_IMPULSE_EVENT, "LONG", BAR_INDEX, BAR_TIMESTAMP),
        (RegimeEventType.DIRECTIONAL_IMPULSE_EVENT, RegimeDirection.LONG, True, BAR_TIMESTAMP),
        (
            RegimeEventType.DIRECTIONAL_IMPULSE_EVENT,
            RegimeDirection.LONG,
            BAR_INDEX,
            BAR_TIMESTAMP.replace(tzinfo=None),
        ),
    ],
)
def test_event_metadata_is_fail_closed(
    event_type: object, direction: object, index: object, timestamp: object
) -> None:
    with pytest.raises(RegimeContextV2Error):
        RegimeEvent(event_type, direction, index, timestamp)


def test_family_substitution_and_wrong_event_object_are_rejected() -> None:
    impulse = _event(RegimeEventType.DIRECTIONAL_IMPULSE_EVENT, RegimeDirection.LONG)
    reversal = _event(RegimeEventType.REVERSAL_TRANSITION_EVENT, RegimeDirection.LONG)

    with pytest.raises(RegimeContextV2Error, match="independent family"):
        _compose(reversal, None)
    with pytest.raises(RegimeContextV2Error, match="independent family"):
        _compose(None, impulse)
    with pytest.raises(RegimeContextV2Error, match="independent family"):
        _compose("LONG", None)
