"""Synthetic one-shot context lifetime tests; no EMA rule, data or replay."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from agicore.trading.directional_impulse_v2 import (
    DirectionalImpulseBarV2,
    evaluate_directional_impulse_event_v2,
)
from agicore.trading.regime_context_v2 import (
    CONTEXT_REUSE,
    MAX_CONTEXT_AGE_CLOSED_BARS,
    MAX_CONTEXT_ELAPSED_TIME,
    SAME_DIRECTION_REFRESH,
    RegimeContextLifetimeNotice,
    RegimeContextV2Error,
    RegimeDirection,
    RegimeEvent,
    RegimeEventContextV2,
    RegimeEventType,
    advance_regime_context_v2,
    finish_regime_context_v2,
)
from agicore.trading.regime_context_v2 import (
    RegimeContextLifetimeState as State,
)
from agicore.trading.reversal_transition_v2 import (
    RejectionBarV2,
    evaluate_reversal_transition_event_v2,
)

E = 10
START = datetime(2026, 10, 3, 20, tzinfo=UTC)
FAMILIES = list(RegimeEventType)
DIRECTIONS = list(RegimeDirection)


def _timestamp(index: int) -> datetime:
    return START + timedelta(minutes=index - E)


def _opposite(direction: RegimeDirection) -> RegimeDirection:
    return RegimeDirection.SHORT if direction is RegimeDirection.LONG else RegimeDirection.LONG


def _event(index: int, direction: RegimeDirection, family=FAMILIES[0], timestamp=None):
    return RegimeEvent(
        family, direction, index, _timestamp(index) if timestamp is None else timestamp
    )


def _step(
    previous, index: int, *, events=(), timestamp=None, qualified=None, end=False, closed=True
):
    callback = qualified
    if type(qualified) is bool:
        callback = lambda context, k, ts: qualified
    by_family = {event.event_type: event for event in events}
    return advance_regime_context_v2(
        previous=previous,
        closed_bar_index=index,
        closed_bar_timestamp=_timestamp(index) if timestamp is None else timestamp,
        source_bar_closed=closed,
        directional_impulse_event=by_family.get(RegimeEventType.DIRECTIONAL_IMPULSE_EVENT),
        reversal_transition_event=by_family.get(RegimeEventType.REVERSAL_TRANSITION_EVENT),
        ema20_pullback_qualified=callback,
        end_of_data=end,
    )


def _initial(direction=RegimeDirection.LONG, family=FAMILIES[0]):
    return _step(None, E, events=(_event(E, direction, family),))


def _must_not_evaluate(context, k, timestamp):
    pytest.fail("ineligible, invalidated or terminal context must not evaluate pullback")


def test_baseline_and_exact_state_vocabulary_are_frozen() -> None:
    assert MAX_CONTEXT_AGE_CLOSED_BARS == 8
    assert MAX_CONTEXT_ELAPSED_TIME == timedelta(minutes=8)
    assert CONTEXT_REUSE == "ONE_SHOT"
    assert SAME_DIRECTION_REFRESH == "DISABLED"
    assert {state.value for state in State} == {
        "INACTIVE",
        "ACTIVE",
        "CONSUMED",
        "EXPIRED_MAX_AGE",
        "EXPIRED_ELAPSED_TIME",
        "INVALIDATED_OPPOSITE_EVENT",
        "INVALIDATED_AMBIGUOUS_EVENT",
        "EXPIRED_END_OF_DATA",
    }


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("family", FAMILIES)
def test_source_event_bar_cannot_consume_its_new_context(direction, family) -> None:
    result = _step(None, E, events=(_event(E, direction, family),), qualified=_must_not_evaluate)
    assert result.state is State.ACTIVE
    assert result.context.source_event_types == (family,)
    assert result.context.source_event_direction is direction
    assert result.context.source_event_bar_index == E
    assert result.context.source_event_timestamp == START
    assert result.context.first_eligible_pullback_bar == E + 1
    assert result.context.last_eligible_pullback_bar == E + 8
    assert result.context.pullback_bar_index is None
    assert result.pullback_evaluated is False


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("age", [1, 4, 8])
def test_inclusive_eligible_bars_consume_and_keep_full_provenance(direction, family, age) -> None:
    initial = _initial(direction, family)
    result = _step(initial, E + age, qualified=True)
    assert result.state is State.CONSUMED
    assert result.pullback_evaluated is True
    assert result.context.source_event_types == (family,)
    assert result.context.source_event_direction is direction
    assert result.context.source_event_bar_index == E
    assert result.context.source_event_timestamp == START
    assert result.context.pullback_bar_index == E + age
    assert result.context.pullback_timestamp == _timestamp(E + age)
    assert initial.state is State.ACTIVE  # Previous snapshot is immutable.


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_eighth_bar_false_expires_only_after_its_pullback_evaluation(direction) -> None:
    calls = []

    def false_predicate(context, k, timestamp):
        assert context.state is State.ACTIVE
        assert context.source_event_bar_index == E
        assert k == E + 8 and timestamp == START + timedelta(minutes=8)
        calls.append(k)
        return False

    result = _step(_initial(direction), E + 8, qualified=false_predicate)
    assert calls == [E + 8]
    assert result.pullback_evaluated is True
    assert result.state is State.EXPIRED_MAX_AGE
    assert result.context.pullback_bar_index is None


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_ninth_bar_expires_by_age_before_evaluation_even_within_eight_minutes(direction) -> None:
    result = _step(
        _initial(direction),
        E + 9,
        timestamp=START + timedelta(minutes=8),
        qualified=_must_not_evaluate,
    )
    assert result.state is State.EXPIRED_MAX_AGE
    assert result.pullback_evaluated is False


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("age", [1, 8])
def test_exactly_eight_minutes_is_inclusive(direction, age) -> None:
    result = _step(
        _initial(direction), E + age, timestamp=START + timedelta(minutes=8), qualified=True
    )
    assert result.state is State.CONSUMED


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("age", [1, 3, 9])
def test_gap_over_eight_minutes_expires_before_any_pullback(direction, age) -> None:
    result = _step(
        _initial(direction),
        E + age,
        timestamp=START + timedelta(minutes=8, microseconds=1),
        qualified=_must_not_evaluate,
    )
    assert result.state is State.EXPIRED_ELAPSED_TIME
    assert result.pullback_evaluated is False
    assert result.context.source_event_bar_index == E


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_first_qualified_pullback_consumes_and_failed_later_confirmation_cannot_reactivate(
    direction,
) -> None:
    active = _step(_initial(direction), E + 1, qualified=False)
    assert active.state is State.ACTIVE
    consumed = _step(active, E + 2, qualified=True)
    assert consumed.state is State.CONSUMED
    # Future confirmation/execution outcomes have no reactivation input here.
    later = _step(consumed, E + 3, qualified=_must_not_evaluate)
    much_later = _step(later, E + 20, qualified=_must_not_evaluate)
    assert later.context == much_later.context == consumed.context
    assert later.state is much_later.state is State.CONSUMED
    assert later.pullback_evaluated is much_later.pullback_evaluated is False


def test_raw_ema_touch_without_formal_qualification_does_not_consume() -> None:
    result = _initial()
    raw_touches = {E + 1: True, E + 2: True, E + 3: True}
    for index, touched in raw_touches.items():
        assert touched is True
        result = _step(result, index, qualified=False)
        assert result.state is State.ACTIVE
        assert result.context.pullback_bar_index is None
    assert _step(result, E + 4).state is State.ACTIVE


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_same_direction_event_never_refreshes_replaces_or_stacks(direction) -> None:
    original = _initial(direction, FAMILIES[0])
    result = _step(
        original, E + 2, events=(_event(E + 2, direction, FAMILIES[1]),), qualified=False
    )
    assert result.context == original.context
    assert result.notices == (RegimeContextLifetimeNotice.SAME_DIRECTION_EVENT_IGNORED_NO_REFRESH,)
    assert result.retired_contexts == ()
    result = _step(result, E + 7, events=(_event(E + 7, direction),), qualified=False)
    assert result.context == original.context
    expired = _step(result, E + 8, qualified=False)
    assert expired.state is State.EXPIRED_MAX_AGE
    assert expired.context.source_event_bar_index == E


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_same_direction_event_on_last_eligible_bar_is_ignored_then_old_context_expires(
    direction,
) -> None:
    result = _step(_initial(direction), E + 8, events=(_event(E + 8, direction),), qualified=False)
    assert result.state is State.EXPIRED_MAX_AGE
    assert result.context.source_event_bar_index == E
    assert result.notices == (RegimeContextLifetimeNotice.SAME_DIRECTION_EVENT_IGNORED_NO_REFRESH,)


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_same_direction_event_still_allows_consumption_of_original_context(direction) -> None:
    result = _step(
        _initial(direction), E + 3, events=(_event(E + 3, direction, FAMILIES[1]),), qualified=True
    )
    assert result.state is State.CONSUMED
    assert result.context.source_event_bar_index == E
    assert result.context.source_event_types == (FAMILIES[0],)
    assert result.context.pullback_bar_index == E + 3


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_opposite_event_invalidates_old_context_before_pullback_and_creates_fresh_source(
    direction,
) -> None:
    k = E + 3
    result = _step(
        _initial(direction),
        k,
        events=(_event(k, _opposite(direction), FAMILIES[1]),),
        qualified=_must_not_evaluate,
    )
    assert result.state is State.ACTIVE
    assert result.context.source_event_direction is _opposite(direction)
    assert result.context.source_event_bar_index == k
    assert result.context.first_eligible_pullback_bar == k + 1
    assert result.pullback_evaluated is False
    assert len(result.retired_contexts) == 1
    old = result.retired_contexts[0]
    assert old.state is State.INVALIDATED_OPPOSITE_EVENT
    assert old.source_event_bar_index == E and old.pullback_bar_index is None
    assert _step(result, k + 1, qualified=True).state is State.CONSUMED


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_ambiguous_event_wins_over_old_pullback_without_replacement(direction) -> None:
    k = E + 2
    events = (
        _event(k, RegimeDirection.LONG, FAMILIES[0]),
        _event(k, RegimeDirection.SHORT, FAMILIES[1]),
    )
    result = _step(_initial(direction), k, events=events, qualified=_must_not_evaluate)
    assert result.state is State.INVALIDATED_AMBIGUOUS_EVENT
    assert result.context.source_event_bar_index == E
    assert result.context.pullback_bar_index is None
    assert result.pullback_evaluated is False
    assert result.retired_contexts == (result.context,)
    assert _step(result, k + 1, qualified=_must_not_evaluate).context == result.context


def test_ambiguous_composition_without_active_source_stays_inactive() -> None:
    events = (
        _event(E, RegimeDirection.LONG, FAMILIES[0]),
        _event(E, RegimeDirection.SHORT, FAMILIES[1]),
    )
    result = _step(None, E, events=events, qualified=_must_not_evaluate)
    assert result.state is State.INACTIVE
    assert result.context.source_event_types == ()


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("expiry", ["age", "elapsed"])
def test_expiry_precedes_new_composition_and_fresh_context_cannot_consume_itself(
    direction, expiry
) -> None:
    k = E + 9 if expiry == "age" else E + 1
    timestamp = START + timedelta(minutes=8 if expiry == "age" else 9)
    event = _event(k, _opposite(direction), timestamp=timestamp)
    result = _step(
        _initial(direction), k, timestamp=timestamp, events=(event,), qualified=_must_not_evaluate
    )
    assert result.state is State.ACTIVE
    assert result.context.source_event_bar_index == k
    assert result.retired_contexts[0].state is (
        State.EXPIRED_MAX_AGE if expiry == "age" else State.EXPIRED_ELAPSED_TIME
    )


def test_same_direction_event_after_expiry_is_a_new_source_not_a_refresh() -> None:
    k = E + 9
    result = _step(
        _initial(), k, events=(_event(k, RegimeDirection.LONG),), qualified=_must_not_evaluate
    )
    assert result.state is State.ACTIVE
    assert result.context.source_event_bar_index == k
    assert result.retired_contexts[0].state is State.EXPIRED_ELAPSED_TIME
    assert result.notices == ()


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_consumed_context_needs_new_event_and_keeps_old_consumption_record(direction) -> None:
    consumed = _step(_initial(direction), E + 1, qualified=True)
    fresh = _step(consumed, E + 2, events=(_event(E + 2, direction),), qualified=_must_not_evaluate)
    assert fresh.state is State.ACTIVE
    assert fresh.context.source_event_bar_index == E + 2
    assert fresh.retired_contexts == (consumed.context,)
    assert consumed.state is State.CONSUMED
    assert _step(fresh, E + 3, qualified=True).context.pullback_bar_index == E + 3


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_two_same_direction_source_families_are_retained_on_consumption(direction) -> None:
    events = tuple(_event(E, direction, family) for family in FAMILIES)
    initial = _step(None, E, events=events)
    consumed = _step(initial, E + 1, qualified=True)
    assert consumed.context.source_event_types == tuple(FAMILIES)
    assert consumed.context.source_event_direction is direction
    assert consumed.context.source_event_bar_index == E


def test_end_of_data_expires_active_without_fabricated_bar_or_pullback() -> None:
    active = _initial()
    finished = finish_regime_context_v2(active)
    assert finished.state is State.EXPIRED_END_OF_DATA
    assert finished.closed_bar_index == E
    assert finished.closed_bar_timestamp == START
    assert finished.context.pullback_bar_index is None
    assert finished.pullback_evaluated is False
    assert finished.end_of_data is True
    assert finish_regime_context_v2(finished) == finished
    assert active.state is State.ACTIVE


@pytest.mark.parametrize("qualified", [False, True])
def test_last_available_bar_can_consume_then_only_remaining_active_context_expires(
    qualified,
) -> None:
    result = _step(_initial(), E + 1, qualified=qualified, end=True)
    assert result.state is (State.CONSUMED if qualified else State.EXPIRED_END_OF_DATA)
    assert result.context.pullback_bar_index == (E + 1 if qualified else None)


def test_event_on_last_dataset_bar_expires_without_own_bar_consumption() -> None:
    result = _step(
        None, E, events=(_event(E, RegimeDirection.LONG),), qualified=_must_not_evaluate, end=True
    )
    assert result.state is State.EXPIRED_END_OF_DATA
    assert result.pullback_evaluated is False


def test_ended_series_cannot_carry_context_to_next_bar_or_other_series() -> None:
    finished = finish_regime_context_v2(_initial())
    with pytest.raises(RegimeContextV2Error, match="ended series"):
        _step(finished, E + 1)
    assert _step(None, E + 1).state is State.INACTIVE


def test_end_of_data_never_changes_consumed_or_invalidated_records() -> None:
    consumed = _step(_initial(), E + 1, qualified=True)
    assert finish_regime_context_v2(consumed).context == consumed.context
    events = (
        _event(E + 1, RegimeDirection.LONG, FAMILIES[0]),
        _event(E + 1, RegimeDirection.SHORT, FAMILIES[1]),
    )
    invalid = _step(_initial(), E + 1, events=events)
    assert finish_regime_context_v2(invalid).context == invalid.context


def test_long_short_mirror_symmetry_for_all_core_transitions() -> None:
    def trace(direction):
        initial = _initial(direction)
        same = _step(
            initial, E + 1, events=(_event(E + 1, direction, FAMILIES[1]),), qualified=False
        )
        opposite = _step(
            same, E + 2, events=(_event(E + 2, _opposite(direction)),), qualified=_must_not_evaluate
        )
        consumed = _step(opposite, E + 3, qualified=True)
        return initial, same, opposite, consumed

    for first, mirrored in zip(
        trace(RegimeDirection.LONG), trace(RegimeDirection.SHORT), strict=True
    ):
        assert first.state is mirrored.state
        assert first.context.source_event_direction is _opposite(
            mirrored.context.source_event_direction
        )
        assert first.context.source_event_types == mirrored.context.source_event_types
        assert first.context.source_event_bar_index == mirrored.context.source_event_bar_index
        assert first.context.source_event_timestamp == mirrored.context.source_event_timestamp
        assert first.context.pullback_bar_index == mirrored.context.pullback_bar_index
        assert first.notices == mirrored.notices


def test_future_event_mutation_has_no_effect_before_that_bar_closes() -> None:
    source = {E: (_event(E, RegimeDirection.LONG),), E + 4: ()}

    def until(last):
        previous = None
        for k in range(E, last + 1):
            previous = _step(previous, k, events=source.get(k, ()), qualified=False)
        return previous

    before = until(E + 3)
    source[E + 4] = (_event(E + 4, RegimeDirection.SHORT),)
    source[E + 5] = object()  # Reading any later value would fail.
    assert until(E + 3) == before
    after_close = until(E + 4)
    assert after_close.context.source_event_direction is RegimeDirection.SHORT
    assert after_close.context.source_event_bar_index == E + 4


@pytest.mark.parametrize("family", FAMILIES)
def test_real_frozen_detector_outputs_anchor_lifetime_on_complete_event_bar(family) -> None:
    if family is RegimeEventType.REVERSAL_TRANSITION_EVENT:
        bars = {
            i: RejectionBarV2(
                i, _timestamp(i), Decimal(i + 1), True, Decimal(i + 1), Decimal(10), Decimal(0)
            )
            for i in range(5)
        }
        bars[5] = RejectionBarV2(
            5, _timestamp(5), Decimal(8), True, Decimal(6), Decimal(12), Decimal(2)
        )
        bars[6] = RejectionBarV2(6, _timestamp(6), Decimal(5), True, Decimal(7), None, None)
        event = evaluate_reversal_transition_event_v2(
            rejection_candidate_bar_index=5, closed_bar_index=6, bars_by_index=bars
        ).event.as_regime_event()
        assert event.event_bar_index == 6  # Confirmation, not rejection bar 5.
    else:

        def bar(i, o, h, l, c, volume=100):
            return DirectionalImpulseBarV2(
                i,
                _timestamp(i),
                Decimal(o),
                Decimal(h),
                Decimal(l),
                Decimal(c),
                True,
                volume,
                "BAR_TRADE_VOLUME",
                1,
                "Last",
            )

        bars = {i: bar(i, "5", "10", "0", "5") for i in range(17)}
        bars[17] = bar(17, "5", "11", "1", "6")
        bars[18] = bar(18, "6", "12", "2", "7")
        bars[19] = bar(19, "7", "13", "3", "8")
        bars[20] = bar(20, "6", "18", "3", "15", 150)
        event = evaluate_directional_impulse_event_v2(
            impulse_candidate_bar_index=20, bars_by_index=bars
        ).event
    e = event.event_bar_index
    active = _step(None, e, events=(event,), qualified=_must_not_evaluate)
    assert active.state is State.ACTIVE
    assert active.context.source_event_types == (family,)
    assert active.context.source_event_timestamp == event.event_timestamp
    consumed = _step(active, e + 1, qualified=True)
    assert consumed.state is State.CONSUMED
    assert consumed.context.pullback_bar_index == e + 1


@pytest.mark.parametrize("closed", [False, None, 1])
def test_unclosed_bar_cannot_advance_context(closed) -> None:
    with pytest.raises(RegimeContextV2Error, match="closed source bar"):
        _step(_initial(), E + 1, closed=closed)


@pytest.mark.parametrize("index", [-1, True, 11.0, E, E - 1])
def test_bar_clock_must_be_valid_and_strictly_forward(index) -> None:
    with pytest.raises(RegimeContextV2Error, match="closed_bar_index|strictly increase"):
        _step(_initial(), index, timestamp=START + timedelta(minutes=1))


@pytest.mark.parametrize(
    "timestamp", [START, START - timedelta(minutes=1), START.replace(tzinfo=None)]
)
def test_timestamp_must_be_utc_and_strictly_forward(timestamp) -> None:
    with pytest.raises(RegimeContextV2Error, match="strictly increase|aware UTC"):
        _step(_initial(), E + 1, timestamp=timestamp)


@pytest.mark.parametrize("value", [1, None, "true"])
def test_predicate_nonboolean_result_is_rejected(value) -> None:
    with pytest.raises(RegimeContextV2Error, match="must be a boolean"):
        _step(_initial(), E + 1, qualified=lambda context, k, timestamp: value)


def test_current_event_cannot_be_from_a_future_bar() -> None:
    with pytest.raises(RegimeContextV2Error, match="current closed bar"):
        _step(_initial(), E + 1, events=(_event(E + 2, RegimeDirection.SHORT),))


def test_malformed_prior_frame_with_future_source_is_rejected() -> None:
    initial = _initial()
    future = replace(
        initial.context, source_event_bar_index=E + 2, source_event_timestamp=_timestamp(E + 2)
    )
    with pytest.raises(RegimeContextV2Error, match="future provenance"):
        _step(replace(initial, context=future), E + 1)


def test_consumed_metadata_cannot_claim_event_bar_or_outside_lifetime() -> None:
    consumed = _step(_initial(), E + 1, qualified=True).context
    with pytest.raises(RegimeContextV2Error, match="e\\+1..e\\+8"):
        replace(consumed, pullback_bar_index=E)
    with pytest.raises(RegimeContextV2Error, match="e\\+1..e\\+8"):
        replace(consumed, pullback_bar_index=E + 9)
    with pytest.raises(RegimeContextV2Error, match="eight minutes"):
        replace(consumed, pullback_timestamp=START + timedelta(minutes=8, microseconds=1))


def test_inactive_without_event_and_immutable_deterministic_snapshots() -> None:
    inactive = _step(None, E, qualified=_must_not_evaluate)
    assert inactive.state is State.INACTIVE
    assert inactive.context == RegimeEventContextV2()
    assert inactive.context.first_eligible_pullback_bar is None
    active = _initial()
    assert _step(active, E + 1, qualified=True) == _step(active, E + 1, qualified=True)
    with pytest.raises(AttributeError):
        active.context.state = State.CONSUMED
    with pytest.raises(AttributeError):
        active.context = RegimeEventContextV2()
