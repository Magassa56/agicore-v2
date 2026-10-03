"""Synthetic complete reversal assembly, provenance and composition integration."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal, localcontext
from itertools import product

import pytest

from agicore.trading.regime_context_v2 import (
    RegimeContextStatus,
    RegimeContextV2Error,
    RegimeDirection,
    RegimeEvent,
    RegimeEventType,
    compose_regime_context_v2,
)
from agicore.trading.reversal_transition_v2 import (
    OppositeTransitionStatus,
    RejectionBarStatus,
    RejectionBarV2,
    ReversalPriorDirection,
    ReversalTransitionV2Error,
    evaluate_reversal_opposite_transition_v2,
    evaluate_reversal_transition_event_v2,
)

START = datetime(2026, 10, 3, 15, tzinfo=UTC)


def _bars(*, mirror: bool = False, t: int = 5):
    bars = {
        index: RejectionBarV2(
            index,
            START + timedelta(minutes=index),
            Decimal(offset + 1),
            True,
            Decimal(offset + 1),
            Decimal(10),
            Decimal(0),
        )
        for offset, index in enumerate(range(t - 5, t))
    }
    bars[t] = RejectionBarV2(
        t, START + timedelta(minutes=t), Decimal(8), True, Decimal(6), Decimal(12), Decimal(2)
    )
    bars[t + 1] = RejectionBarV2(
        t + 1, START + timedelta(minutes=t + 1), Decimal(5), True, Decimal(7), None, None
    )
    if mirror:
        bars = _mirror(bars)
    return bars


def _mirror(bars):
    return {
        index: replace(
            bar,
            open=bar.open.copy_negate(),
            close=bar.close.copy_negate(),
            high=None if bar.low is None else bar.low.copy_negate(),
            low=None if bar.high is None else bar.high.copy_negate(),
        )
        for index, bar in bars.items()
    }


def _evaluate(bars, *, t: int = 5, clock: int | None = None, end: bool = False):
    return evaluate_reversal_transition_event_v2(
        rejection_candidate_bar_index=t,
        closed_bar_index=t + 1 if clock is None else clock,
        bars_by_index=bars,
        end_of_data=end,
    )


@pytest.mark.parametrize("mirror", [False, True], ids=["UP-to-SHORT", "DOWN-to-LONG"])
def test_complete_event_retains_exact_source_label_and_separate_timestamps(mirror: bool) -> None:
    bars = _bars(mirror=mirror)
    with localcontext() as context:
        context.prec = 2
        result = _evaluate(bars)
    event = result.event
    assert result.reversal_transition_event_qualified is True
    assert event.event_type == "REVERSAL_TRANSITION"
    assert event.event_direction is (RegimeDirection.LONG if mirror else RegimeDirection.SHORT)
    assert event.prior_direction is (
        ReversalPriorDirection.DOWN if mirror else ReversalPriorDirection.UP
    )
    assert event.rejection_bar_index == 5
    assert event.event_bar_index == 6
    assert event.rejection_timestamp == bars[5].timestamp_utc
    assert event.event_timestamp == bars[6].timestamp_utc
    assert result.prior_direction.known_at_bar_index == 4
    assert result.rejection.known_at_bar_index == 5
    assert result.opposite_transition.known_at_bar_index == 6
    assert result.opposite_transition == evaluate_reversal_opposite_transition_v2(
        rejection_candidate_bar_index=5, closed_bar_index=6, bars_by_index=bars
    )


@pytest.mark.parametrize("mirror", [False, True])
@pytest.mark.parametrize(
    ("direction_ok", "rejection_ok", "transition_ok"), list(product([False, True], repeat=3))
)
def test_strict_three_component_conjunction(
    mirror, direction_ok, rejection_ok, transition_ok
) -> None:
    bars = _bars()
    if not direction_ok:
        bars[4] = replace(bars[4], close=Decimal(1))
    if not rejection_ok:
        bars[0] = replace(bars[0], high=Decimal(12))
    if not transition_ok:
        bars[6] = replace(bars[6], close=Decimal(7))
    if mirror:
        bars = _mirror(bars)
    result = _evaluate(bars)
    assert result.reversal_transition_event_qualified is all(
        (direction_ok, rejection_ok, transition_ok)
    )
    assert (result.event is not None) is all((direction_ok, rejection_ok, transition_ok))


@pytest.mark.parametrize(
    ("cause", "transition_status", "rejection_status"),
    [
        (
            "warmup",
            OppositeTransitionStatus.REJECTION_NOT_QUALIFIED,
            RejectionBarStatus.INSUFFICIENT_WARMUP,
        ),
        (
            "invalid-prior-close",
            OppositeTransitionStatus.REJECTION_NOT_QUALIFIED,
            RejectionBarStatus.INVALID_PRIOR_DIRECTION_INPUT,
        ),
        (
            "invalid-extreme",
            OppositeTransitionStatus.REJECTION_NOT_QUALIFIED,
            RejectionBarStatus.INVALID_PRIOR_EXTREMA,
        ),
        (
            "invalid-ohlc",
            OppositeTransitionStatus.REJECTION_NOT_QUALIFIED,
            RejectionBarStatus.INVALID_OHLC,
        ),
        (
            "zero-range",
            OppositeTransitionStatus.REJECTION_NOT_QUALIFIED,
            RejectionBarStatus.INVALID_CANDIDATE_RANGE,
        ),
        (
            "missing-confirmation",
            OppositeTransitionStatus.INCOMPLETE_CONFIRMATION,
            RejectionBarStatus.EVALUATED,
        ),
        (
            "unclosed-confirmation",
            OppositeTransitionStatus.INCOMPLETE_CONFIRMATION,
            RejectionBarStatus.EVALUATED,
        ),
        (
            "invalid-confirmation",
            OppositeTransitionStatus.INVALID_CONFIRMATION_INPUT,
            RejectionBarStatus.EVALUATED,
        ),
        ("expired", OppositeTransitionStatus.EXPIRED_NO_TRANSITION, RejectionBarStatus.EVALUATED),
    ],
)
def test_failure_statuses_remain_visible_without_any_event(
    cause, transition_status, rejection_status
) -> None:
    bars = _bars()
    if cause == "warmup":
        del bars[0]
    elif cause == "invalid-prior-close":
        bars[0] = replace(bars[0], close=None)
    elif cause == "invalid-extreme":
        bars[0] = replace(bars[0], high=None)
    elif cause == "invalid-ohlc":
        bars[5] = replace(bars[5], open=Decimal(13))
    elif cause == "zero-range":
        bars[5] = replace(bars[5], open=Decimal(8), high=Decimal(8), low=Decimal(8))
    elif cause == "missing-confirmation":
        del bars[6]
    elif cause == "unclosed-confirmation":
        bars[6] = replace(bars[6], is_closed=False)
    elif cause == "invalid-confirmation":
        bars[6] = replace(bars[6], close=Decimal("NaN"))
    else:
        bars[6] = replace(bars[6], close=Decimal(6))
    result = _evaluate(bars)
    assert result.event is None
    assert result.reversal_transition_event_qualified is False
    assert result.opposite_transition.status is transition_status
    assert result.rejection.status is rejection_status


def test_no_event_at_close_t_even_when_source_contains_qualified_future_confirmation() -> None:
    class RejectionOnly(dict):
        def __contains__(self, index):
            assert 0 <= index <= 5
            return super().__contains__(index)

        def __getitem__(self, index):
            assert 0 <= index <= 5
            return super().__getitem__(index)

    result = _evaluate(RejectionOnly(_bars()), clock=5)
    assert result.event is None
    assert result.opposite_transition.state is OppositeTransitionStatus.AWAITING_OPPOSITE_TRANSITION
    assert result.rejection.rejection_qualified is True
    assert result.opposite_transition.transition_confirmed is False


def test_end_of_data_without_t_plus_one_never_creates_event() -> None:
    bars = _bars()
    del bars[6]
    result = _evaluate(bars, clock=5, end=True)
    assert result.opposite_transition.status is OppositeTransitionStatus.INCOMPLETE_CONFIRMATION
    assert result.event is None


@pytest.mark.parametrize("mirror", [False, True])
def test_valid_t_plus_two_cannot_rescue_expired_rejection(mirror: bool) -> None:
    bars = _bars()
    bars[7] = replace(bars[6], bar_index=7, timestamp_utc=START + timedelta(minutes=7))
    bars[6] = replace(bars[6], close=Decimal(7))
    if mirror:
        bars = _mirror(bars)
    assert _evaluate(bars, clock=7).event is None
    assert (
        _evaluate(bars, clock=7).opposite_transition.status
        is OppositeTransitionStatus.EXPIRED_NO_TRANSITION
    )


@pytest.mark.parametrize("mirror", [False, True])
def test_future_mutation_has_no_effect_on_complete_event(mirror: bool) -> None:
    class WindowOnly(dict):
        def __contains__(self, index):
            assert 10 <= index <= 16
            return super().__contains__(index)

        def __getitem__(self, index):
            assert 10 <= index <= 16
            return super().__getitem__(index)

        def __iter__(self):
            pytest.fail("event assembly must not iterate unrelated observations")

    bars = WindowOnly(_bars(mirror=mirror, t=15))
    before = _evaluate(bars, t=15)
    bars[9], bars[17], bars[18] = object(), object(), object()
    assert _evaluate(bars, t=15, clock=18) == before
    bars[9], bars[17], bars[18] = None, None, None
    assert _evaluate(bars, t=15, clock=18) == before
    assert before.event.event_bar_index == 16
    assert before.event.rejection_bar_index == 15


def test_mirror_symmetry_including_event_provenance() -> None:
    first, mirrored = _evaluate(_bars()), _evaluate(_bars(mirror=True))
    assert first.event.event_direction is RegimeDirection.SHORT
    assert mirrored.event.event_direction is RegimeDirection.LONG
    assert first.event.event_type == mirrored.event.event_type
    assert first.event.event_bar_index == mirrored.event.event_bar_index
    assert first.event.rejection_bar_index == mirrored.event.rejection_bar_index
    assert first.event.event_timestamp == mirrored.event.event_timestamp
    assert first.event.rejection_timestamp == mirrored.event.rejection_timestamp


@pytest.mark.parametrize("open_", ["6", "8"])
def test_rejection_color_is_not_reintroduced_during_event_assembly(open_) -> None:
    bars = _bars()
    bars[5] = replace(bars[5], open=Decimal(open_), close=Decimal("6" if open_ == "8" else "8"))
    assert _evaluate(bars).event is not None


def test_complete_event_adapter_integrates_with_unchanged_distinct_family_composer() -> None:
    source = _evaluate(_bars()).event
    reversal = source.as_regime_event()
    assert source.event_type == "REVERSAL_TRANSITION"
    assert reversal == RegimeEvent(
        RegimeEventType.REVERSAL_TRANSITION_EVENT, RegimeDirection.SHORT, 6, source.event_timestamp
    )

    def compose(impulse):
        return compose_regime_context_v2(
            closed_bar_index=6,
            closed_bar_timestamp=source.event_timestamp,
            source_bar_closed=True,
            directional_impulse_event=impulse,
            reversal_transition_event=reversal,
        )

    assert compose(None).status is RegimeContextStatus.QUALIFIED
    same = RegimeEvent(
        RegimeEventType.DIRECTIONAL_IMPULSE_EVENT, RegimeDirection.SHORT, 6, source.event_timestamp
    )
    same_result = compose(same)
    assert same_result.status is RegimeContextStatus.QUALIFIED
    assert len(same_result.events) == 2
    opposite = replace(same, event_direction=RegimeDirection.LONG)
    assert compose(opposite).status is RegimeContextStatus.AMBIGUOUS
    assert compose(opposite).entry_blocked_by_context is True


def test_later_evaluation_cannot_retimestamp_event_or_make_it_an_active_context() -> None:
    bars = _bars()
    first = _evaluate(bars)
    later = _evaluate(bars, clock=7)
    assert first == later
    assert later.event.event_bar_index == 6
    with pytest.raises(RegimeContextV2Error, match="current closed bar"):
        compose_regime_context_v2(
            closed_bar_index=7,
            closed_bar_timestamp=START + timedelta(minutes=7),
            source_bar_closed=True,
            directional_impulse_event=None,
            reversal_transition_event=later.event.as_regime_event(),
        )


@pytest.mark.parametrize(
    ("field", "invalid", "message"),
    [
        ("prior_direction", ReversalPriorDirection.NONE, "UP or DOWN"),
        ("prior_direction", "UP", "UP or DOWN"),
        ("event_direction", RegimeDirection.LONG, "oppose"),
        ("event_bar_index", 5, "t\\+1"),
        ("event_bar_index", 7, "t\\+1"),
        ("rejection_bar_index", True, "nonnegative integer"),
        ("event_timestamp", START + timedelta(minutes=5), "follow"),
        ("rejection_timestamp", START.replace(minute=5, tzinfo=None), "aware UTC"),
    ],
)
def test_event_metadata_cannot_invent_direction_or_violate_t_plus_one(
    field, invalid, message
) -> None:
    event = _evaluate(_bars()).event
    with pytest.raises(ReversalTransitionV2Error, match=message):
        replace(event, **{field: invalid})


def test_evaluation_and_event_are_repeatable_and_immutable() -> None:
    result = _evaluate(_bars())
    assert result == _evaluate(_bars())
    with pytest.raises(AttributeError):
        result.event = None
    with pytest.raises(AttributeError):
        result.event.event_timestamp = START
    with pytest.raises(ValueError):
        replace(result.event, event_type="OTHER")
