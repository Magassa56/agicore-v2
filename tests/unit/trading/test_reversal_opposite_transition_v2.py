"""Synthetic strict body acceptance on t+1 only; no dataset or replay."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal, localcontext

import pytest

from agicore.trading.reversal_transition_v2 import (
    CONFIRMATION_WINDOW_CLOSED_BARS,
    OppositeTransitionStatus,
    RejectionBarStatus,
    RejectionBarV2,
    ReversalPriorDirection,
    ReversalTransitionV2Error,
    evaluate_reversal_opposite_transition_v2,
    evaluate_reversal_rejection_bar_v2,
)

START = datetime(2026, 10, 3, 15, tzinfo=UTC)
CASES = [
    pytest.param("7", "5", True, id="bearish-beyond-body-without-low-break"),
    pytest.param("8", "7", False, id="bearish-inside-body"),
    pytest.param("4", "5", False, id="bullish-even-beyond-body"),
    pytest.param("7", "6", False, id="equal-body-low"),
    pytest.param("7", "7", False, id="doji-inside"),
    pytest.param("5", "5", False, id="doji-beyond-body"),
    pytest.param("100", "5", True, id="large-body-allowed"),
    pytest.param("5.0000000000000000000000000000000000000001", "5", True, id="tiny-body-allowed"),
    pytest.param("7", "5.9999999999999999999999999999999999999999", True, id="just-beyond-body"),
    pytest.param("7", "6.0000000000000000000000000000000000000001", False, id="just-inside-body"),
    pytest.param("7", "-1", True, id="beyond-rejection-low-allowed"),
]


def _bars(open_: str = "7", close: str = "5", *, t: int = 5):
    bars = {
        index: RejectionBarV2(
            bar_index=index,
            timestamp_utc=START + timedelta(minutes=index),
            close=Decimal(offset + 1),
            is_closed=True,
            open=Decimal(offset + 1),
            high=Decimal(10),
            low=Decimal(0),
        )
        for offset, index in enumerate(range(max(0, t - 5), t))
    }
    bars[t] = RejectionBarV2(
        t, START + timedelta(minutes=t), Decimal(8), True, Decimal(6), Decimal(12), Decimal(2)
    )
    # Confirmation needs only Open/Close; High/Low are deliberately absent.
    bars[t + 1] = RejectionBarV2(
        t + 1, START + timedelta(minutes=t + 1), Decimal(close), True, Decimal(open_), None, None
    )
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
    return evaluate_reversal_opposite_transition_v2(
        rejection_candidate_bar_index=t,
        closed_bar_index=t + 1 if clock is None else clock,
        bars_by_index=bars,
        end_of_data=end,
    )


@pytest.mark.parametrize("mirror", [False, True], ids=["SHORT", "LONG"])
@pytest.mark.parametrize(("open_", "close", "qualified"), CASES)
def test_confirmation_color_and_strict_body_boundary(mirror, open_, close, qualified) -> None:
    bars = _bars(open_, close)
    if mirror:
        bars = _mirror(bars)
    with localcontext() as context:
        context.prec = 2
        result = _evaluate(bars)
    assert CONFIRMATION_WINDOW_CLOSED_BARS == 1
    assert result.rejection_qualified is True
    assert result.transition_confirmed is qualified
    assert result.status is (
        OppositeTransitionStatus.CONFIRMED
        if qualified
        else OppositeTransitionStatus.EXPIRED_NO_TRANSITION
    )
    assert result.state is result.status
    assert result.confirmation_bar_index == 6
    assert result.known_at_bar_index == 6
    assert result.known_at_timestamp == bars[6].timestamp_utc
    assert result.rejection_body_low == Decimal(-8 if mirror else 6)
    assert result.rejection_body_high == Decimal(-6 if mirror else 8)


@pytest.mark.parametrize(("open_", "close", "qualified"), CASES)
def test_long_short_mirror_symmetry(open_, close, qualified) -> None:
    bars = _bars(open_, close)
    first, mirrored = _evaluate(bars), _evaluate(_mirror(bars))
    assert first.status is mirrored.status
    assert first.transition_confirmed is mirrored.transition_confirmed is qualified
    assert mirrored.rejection_body_low == first.rejection_body_high.copy_negate()
    assert mirrored.rejection_body_high == first.rejection_body_low.copy_negate()
    assert mirrored.rejection.prior_direction.prior_direction is ReversalPriorDirection.DOWN
    assert first.rejection.prior_direction.prior_direction is ReversalPriorDirection.UP
    assert mirrored.known_at_timestamp == first.known_at_timestamp


def test_close_t_waits_and_cannot_read_confirmation_present_in_historical_mapping() -> None:
    class RejectionOnly(dict):
        def __contains__(self, index):
            assert 0 <= index <= 5
            return super().__contains__(index)

        def __getitem__(self, index):
            assert 0 <= index <= 5
            return super().__getitem__(index)

    bars = RejectionOnly(_bars())
    result = _evaluate(bars, clock=5)
    assert result.rejection_qualified is True
    assert result.transition_confirmed is False
    assert result.state is OppositeTransitionStatus.AWAITING_OPPOSITE_TRANSITION
    assert result.known_at_bar_index is None
    assert result.known_at_timestamp is None
    assert result.rejection.known_at_bar_index == 5
    assert result.rejection == evaluate_reversal_rejection_bar_v2(
        rejection_candidate_bar_index=5, bars_by_index=bars
    )
    assert not hasattr(result, "event")


def test_end_of_data_at_close_t_changes_waiting_to_incomplete_without_future_reads() -> None:
    bars = _bars()
    del bars[6]
    assert _evaluate(bars, clock=5).state is OppositeTransitionStatus.AWAITING_OPPOSITE_TRANSITION
    result = _evaluate(bars, clock=5, end=True)
    assert result.status is OppositeTransitionStatus.INCOMPLETE_CONFIRMATION
    assert result.transition_confirmed is False
    assert result.known_at_timestamp is None


@pytest.mark.parametrize("mirror", [False, True])
def test_missing_or_unclosed_t_plus_one_is_incomplete(mirror: bool) -> None:
    bars = _bars()
    if mirror:
        bars = _mirror(bars)
    bars[6] = replace(bars[6], is_closed=False)
    assert _evaluate(bars).status is OppositeTransitionStatus.INCOMPLETE_CONFIRMATION
    del bars[6]
    result = _evaluate(bars)
    assert result.status is OppositeTransitionStatus.INCOMPLETE_CONFIRMATION
    assert result.transition_confirmed is False
    assert result.known_at_timestamp is None


@pytest.mark.parametrize("mirror", [False, True])
def test_t_plus_two_cannot_confirm_failed_or_missing_t_plus_one(mirror: bool) -> None:
    bars = _bars("8", "7")
    bars[7] = replace(_bars()[6], bar_index=7, timestamp_utc=START + timedelta(minutes=7))
    if mirror:
        bars = _mirror(bars)
    before = _evaluate(bars)
    assert before.status is OppositeTransitionStatus.EXPIRED_NO_TRANSITION
    assert _evaluate(bars, clock=7) == before
    del bars[6]
    assert _evaluate(bars, clock=7).status is OppositeTransitionStatus.INCOMPLETE_CONFIRMATION


@pytest.mark.parametrize("mirror", [False, True])
def test_t_plus_two_and_future_mutation_has_no_effect(mirror: bool) -> None:
    class WindowOnly(dict):
        def __contains__(self, index):
            assert 10 <= index <= 16
            return super().__contains__(index)

        def __getitem__(self, index):
            assert 10 <= index <= 16
            return super().__getitem__(index)

        def __iter__(self):
            pytest.fail("source mapping iteration could read future bars")

        def values(self):
            pytest.fail("source mapping values could read future bars")

    bars = _bars(t=15)
    if mirror:
        bars = _mirror(bars)
    bars = WindowOnly(bars)
    before = _evaluate(bars, t=15)
    bars[9], bars[17], bars[18] = object(), object(), object()
    assert _evaluate(bars, t=15, clock=18) == before
    bars[9], bars[17], bars[18] = None, None, None
    assert _evaluate(bars, t=15, clock=18) == before


def test_confirmation_mutation_changes_transition_only() -> None:
    bars = _bars()
    before = _evaluate(bars)
    bars[6] = replace(bars[6], close=Decimal(7))
    after = _evaluate(bars)
    assert before.transition_confirmed is True
    assert after.transition_confirmed is False
    assert before.rejection == after.rejection
    assert before.rejection_body_low == after.rejection_body_low
    assert before.rejection_body_high == after.rejection_body_high


@pytest.mark.parametrize("open_", ["6", "8"])
def test_rejection_body_bounds_use_min_max_independent_of_rejection_color(open_) -> None:
    bars = _bars()
    bars[5] = replace(bars[5], open=Decimal(open_), close=Decimal("6" if open_ == "8" else "8"))
    result = _evaluate(bars)
    assert result.rejection_body_low == Decimal(6)
    assert result.rejection_body_high == Decimal(8)
    assert result.transition_confirmed is True


@pytest.mark.parametrize("field", ["open", "close"])
@pytest.mark.parametrize(
    "invalid", [None, Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity"), True, 5.0, "5"]
)
def test_missing_nonfinite_or_inexact_confirmation_price_is_invalid(field, invalid) -> None:
    bars = _bars()
    bars[6] = replace(bars[6], **{field: invalid})
    result = _evaluate(bars)
    assert result.status is OppositeTransitionStatus.INVALID_CONFIRMATION_INPUT
    assert result.transition_confirmed is False
    assert result.known_at_timestamp is None


def test_integer_confirmation_prices_are_exact() -> None:
    bars = _bars()
    bars[6] = replace(bars[6], open=7, close=5)
    assert _evaluate(bars).transition_confirmed is True


@pytest.mark.parametrize("cause", ["no-sweep", "no-direction", "warmup", "invalid-close"])
def test_unqualified_rejection_preserves_its_status_and_never_reads_confirmation(cause) -> None:
    class NoConfirmation(dict):
        def __contains__(self, index):
            assert index <= 5
            return super().__contains__(index)

        def __getitem__(self, index):
            assert index <= 5
            return super().__getitem__(index)

    bars = NoConfirmation(_bars())
    if cause == "no-sweep":
        bars[0] = replace(bars[0], high=Decimal(12))
    elif cause == "no-direction":
        bars[3] = replace(bars[3], close=Decimal(2))
        bars[4] = replace(bars[4], close=Decimal(1))
    elif cause == "warmup":
        del bars[0]
    else:
        bars[0] = replace(bars[0], close=None)
    result = _evaluate(bars)
    assert result.status is OppositeTransitionStatus.REJECTION_NOT_QUALIFIED
    assert result.transition_confirmed is False
    assert result.rejection_qualified is False
    expected = {
        "no-sweep": RejectionBarStatus.EVALUATED,
        "no-direction": RejectionBarStatus.EVALUATED,
        "warmup": RejectionBarStatus.INSUFFICIENT_WARMUP,
        "invalid-close": RejectionBarStatus.INVALID_PRIOR_DIRECTION_INPUT,
    }
    assert result.rejection.status is expected[cause]


@pytest.mark.parametrize("clock", [-1, True, 6.0, 4])
def test_clock_must_be_a_closed_index_at_or_after_rejection(clock) -> None:
    with pytest.raises(ReversalTransitionV2Error, match="closed_bar_index|already be closed"):
        _evaluate({}, clock=clock)


@pytest.mark.parametrize("index", [-1, True, 5.0])
def test_rejection_index_must_be_valid(index) -> None:
    with pytest.raises(ReversalTransitionV2Error, match="candidate index"):
        _evaluate({}, t=index, clock=6)


def test_end_of_data_flag_must_be_boolean() -> None:
    with pytest.raises(ReversalTransitionV2Error, match="end_of_data"):
        _evaluate({}, end=1)


def test_confirmation_metadata_must_match_its_index_and_follow_rejection() -> None:
    bars = _bars()
    bars[6] = replace(bars[6], bar_index=7)
    with pytest.raises(ReversalTransitionV2Error, match="confirmation bar index"):
        _evaluate(bars)
    bars = _bars()
    bars[6] = replace(bars[6], timestamp_utc=bars[5].timestamp_utc)
    with pytest.raises(ReversalTransitionV2Error, match="confirmation must follow"):
        _evaluate(bars)


def test_result_is_immutable_repeatable_and_only_a_confirmation() -> None:
    result = _evaluate(_bars())
    assert result == _evaluate(_bars())
    with pytest.raises(AttributeError):
        result.transition_confirmed = False
    assert not hasattr(result, "event")
