"""Synthetic five-bar reversal direction tests; no market data or replay."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal, localcontext

import pytest

from agicore.trading.regime_context_v2 import RegimeDirection
from agicore.trading.reversal_transition_v2 import (
    PRIOR_DIRECTION_LOOKBACK,
    PRIOR_DIRECTION_MIN_STEPS,
    PriorDirectionBarV2,
    PriorDirectionStatus,
    ReversalPriorDirection,
    ReversalTransitionV2Error,
    evaluate_reversal_prior_direction_v2,
)

START = datetime(2026, 10, 3, 15, tzinfo=UTC)


def _bars(closes: list[str], *, start_index: int = 0) -> dict[int, PriorDirectionBarV2]:
    return {
        index: PriorDirectionBarV2(index, START + timedelta(minutes=index), Decimal(close), True)
        for index, close in enumerate(closes, start_index)
    }


def _evaluate(bars, t: int = 5):
    return evaluate_reversal_prior_direction_v2(reversal_candidate_bar_index=t, bars_by_index=bars)


@pytest.mark.parametrize("mirror", [False, True], ids=["UP-to-SHORT", "DOWN-to-LONG"])
@pytest.mark.parametrize(
    ("closes", "qualified", "up", "down", "flat"),
    [
        (["1", "2", "3", "4", "5"], True, 4, 0, 0),
        (["1", "3", "2", "4", "5"], True, 3, 1, 0),
        (["1", "2", "4", "3", "5"], True, 3, 1, 0),
        (["1", "2", "3", "5", "4"], True, 3, 1, 0),
        (["1", "4", "3", "6", "5"], False, 2, 2, 0),
        (["5", "6", "7", "8", "1"], False, 3, 1, 0),
        (["1", "2", "3", "4", "1"], False, 3, 1, 0),
        (["1", "1", "2", "3", "4"], True, 3, 0, 1),
        (["1", "2", "2", "3", "4"], True, 3, 0, 1),
        (["1", "2", "3", "4", "4"], True, 3, 0, 1),
        (["1", "2", "2", "2", "3"], False, 2, 0, 2),
        (["3", "3", "3", "3", "3"], False, 0, 0, 4),
    ],
)
def test_signed_transitions_and_strict_endpoint(
    mirror: bool, closes: list[str], qualified: bool, up: int, down: int, flat: int
) -> None:
    bars = _bars(closes)
    if mirror:
        bars = {index: replace(bar, close=bar.close.copy_negate()) for index, bar in bars.items()}
    result = _evaluate(bars)
    direction = ReversalPriorDirection.DOWN if mirror else ReversalPriorDirection.UP
    reversal = RegimeDirection.LONG if mirror else RegimeDirection.SHORT
    assert PRIOR_DIRECTION_LOOKBACK == 5
    assert PRIOR_DIRECTION_MIN_STEPS == 3
    assert result.status is PriorDirectionStatus.EVALUATED
    assert result.prior_direction is (direction if qualified else ReversalPriorDirection.NONE)
    assert result.reversal_direction is (reversal if qualified else None)
    assert result.up_steps == (down if mirror else up)
    assert result.down_steps == (up if mirror else down)
    assert result.flat_steps == flat
    assert sum((result.up_steps, result.down_steps, result.flat_steps)) == 4
    assert result.known_at_bar_index == 4
    assert result.known_at_timestamp == bars[4].timestamp_utc
    assert result.reversal_candidate_bar_index == 5


def test_close_steps_are_the_four_exact_adjacent_differences() -> None:
    result = _evaluate(_bars(["10", "12", "11.25", "14", "16.5"]))
    assert result.close_steps == (Decimal(2), Decimal("-0.75"), Decimal("2.75"), Decimal("2.5"))
    assert result.prior_direction is ReversalPriorDirection.UP


def test_tiny_steps_remain_exact_under_reduced_decimal_precision() -> None:
    closes = [
        "1.0000000000000000000000000000000000000000",
        "1.0000000000000000000000000000000000000001",
        "1.0000000000000000000000000000000000000002",
        "1.0000000000000000000000000000000000000003",
        "1.0000000000000000000000000000000000000004",
    ]
    with localcontext() as context:
        context.prec = 2
        result = _evaluate(_bars(closes))
    assert result.close_steps == (Decimal("1e-40"),) * 4
    assert result.up_steps == 4 and result.flat_steps == 0
    assert result.prior_direction is ReversalPriorDirection.UP


@pytest.mark.parametrize("count", range(5))
def test_fewer_than_five_prior_bars_is_insufficient(count: int) -> None:
    bars = _bars([str(i) for i in range(count)])
    # Candidate presence cannot supplement the required prior window.
    bars[count] = object()
    result = _evaluate(bars, count)
    assert result.status is PriorDirectionStatus.INSUFFICIENT_WARMUP
    assert result.prior_direction is ReversalPriorDirection.NONE
    assert result.reversal_direction is None
    assert result.close_steps is None
    assert result.known_at_bar_index is None


@pytest.mark.parametrize("missing", range(5))
def test_gap_inside_five_bar_window_cannot_be_filled_with_older_bars(missing: int) -> None:
    bars = _bars(["1", "2", "3", "4", "5"], start_index=10)
    del bars[10 + missing]
    bars[9] = PriorDirectionBarV2(9, START + timedelta(minutes=9), Decimal(0), True)
    result = _evaluate(bars, 15)
    assert result.status is PriorDirectionStatus.INSUFFICIENT_WARMUP
    assert result.prior_direction is ReversalPriorDirection.NONE


@pytest.mark.parametrize("index", [0, 2, 4])
def test_unclosed_prior_bar_is_insufficient_completed_history(index: int) -> None:
    bars = _bars(["1", "2", "3", "4", "5"])
    bars[index] = replace(bars[index], is_closed=False)
    result = _evaluate(bars)
    assert result.status is PriorDirectionStatus.INSUFFICIENT_WARMUP
    assert result.reversal_direction is None


@pytest.mark.parametrize("index", range(5))
@pytest.mark.parametrize(
    "invalid", [None, Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity"), Decimal("-Infinity")]
)
def test_missing_or_nonfinite_required_close_has_explicit_invalid_status(index, invalid) -> None:
    bars = _bars(["1", "2", "3", "4", "5"])
    bars[index] = replace(bars[index], close=invalid)
    result = _evaluate(bars)
    assert result.status is PriorDirectionStatus.INVALID_PRIOR_DIRECTION_INPUT
    assert result.prior_direction is ReversalPriorDirection.NONE
    assert result.reversal_direction is None
    assert result.close_steps is None
    assert result.known_at_timestamp is None


@pytest.mark.parametrize("invalid", [True, "3", 3.0, float("inf"), float("nan")])
def test_inexact_or_nonprice_types_are_invalid_without_silent_coercion(invalid) -> None:
    bars = _bars(["1", "2", "3", "4", "5"])
    bars[2] = replace(bars[2], close=invalid)
    assert _evaluate(bars).status is PriorDirectionStatus.INVALID_PRIOR_DIRECTION_INPUT


def test_integer_closes_have_exact_decimal_steps() -> None:
    bars = _bars(["1", "2", "3", "4", "5"])
    bars = {index: replace(bar, close=index + 1) for index, bar in bars.items()}
    assert _evaluate(bars).close_steps == (Decimal(1),) * 4


def test_warmup_precedes_price_validation_when_history_is_incomplete() -> None:
    bars = _bars(["1", "2", "3", "4", "5"])
    bars[0] = replace(bars[0], is_closed=False)
    bars[4] = replace(bars[4], close=None)
    assert _evaluate(bars).status is PriorDirectionStatus.INSUFFICIENT_WARMUP


def test_candidate_future_and_older_bars_are_never_read_or_iterated() -> None:
    class PriorOnly(dict):
        def __contains__(self, index):
            assert 10 <= index <= 14
            return super().__contains__(index)

        def __getitem__(self, index):
            assert 10 <= index <= 14
            return super().__getitem__(index)

        def __iter__(self):
            pytest.fail("mapping iteration could expose unrelated bars")

    bars = PriorOnly(_bars(["1", "2", "3", "4", "5"], start_index=10))
    before = _evaluate(bars, 15)
    bars[9] = object()
    bars[15] = object()
    bars[16] = object()
    after = _evaluate(bars, 15)
    bars[15] = None
    bars[16] = None
    assert before == after == _evaluate(bars, 15)


@pytest.mark.parametrize(
    "closes",
    [
        ["1", "2", "3", "4", "5"],
        ["1", "3", "2", "4", "5"],
        ["1", "2", "3", "5", "4"],
        ["1", "1", "2", "3", "4"],
        ["5", "6", "7", "8", "1"],
        ["1", "2", "3", "4", "1"],
    ],
)
def test_up_down_mirror_symmetry(closes: list[str]) -> None:
    bars = _bars(closes)
    opposite = {index: replace(bar, close=bar.close.copy_negate()) for index, bar in bars.items()}
    first, mirrored = _evaluate(bars), _evaluate(opposite)
    assert first.up_steps == mirrored.down_steps
    assert first.down_steps == mirrored.up_steps
    assert first.flat_steps == mirrored.flat_steps
    assert mirrored.close_steps == tuple(step.copy_negate() for step in first.close_steps)
    expected = {
        ReversalPriorDirection.UP: ReversalPriorDirection.DOWN,
        ReversalPriorDirection.DOWN: ReversalPriorDirection.UP,
        ReversalPriorDirection.NONE: ReversalPriorDirection.NONE,
    }
    assert mirrored.prior_direction is expected[first.prior_direction]


def test_reversal_prior_direction_accepts_a_pullback_in_last_three_closes() -> None:
    # Last three 3 -> 5 -> 4 are not a strict emerging impulse direction.
    result = _evaluate(_bars(["1", "2", "3", "5", "4"]))
    assert result.prior_direction is ReversalPriorDirection.UP
    assert result.reversal_direction is RegimeDirection.SHORT


def test_inconsistent_prior_metadata_is_rejected() -> None:
    bars = _bars(["1", "2", "3", "4", "5"])
    bars[2] = replace(bars[2], bar_index=3)
    with pytest.raises(ReversalTransitionV2Error, match="index is inconsistent"):
        _evaluate(bars)
    bars = _bars(["1", "2", "3", "4", "5"])
    bars[2] = replace(bars[2], timestamp_utc=bars[1].timestamp_utc)
    with pytest.raises(ReversalTransitionV2Error, match="timestamps must increase"):
        _evaluate(bars)


@pytest.mark.parametrize("index", [-1, True, 5.0])
def test_invalid_candidate_index_is_rejected_without_reading_any_bar(index) -> None:
    with pytest.raises(ReversalTransitionV2Error, match="candidate index"):
        _evaluate({}, index)


def test_result_is_repeatable_immutable_and_only_a_prerequisite() -> None:
    result = _evaluate(_bars(["1", "2", "3", "4", "5"]))
    assert result == _evaluate(_bars(["1", "2", "3", "4", "5"]))
    with pytest.raises(AttributeError):
        result.prior_direction = ReversalPriorDirection.NONE
    assert not hasattr(result, "event")
