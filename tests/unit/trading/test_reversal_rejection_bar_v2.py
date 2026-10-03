"""Synthetic rejection geometry and causal-window tests; no replay or dataset."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal, localcontext

import pytest

from agicore.trading.regime_context_v2 import RegimeDirection
from agicore.trading.reversal_transition_v2 import (
    MIN_REJECTION_WICK_RATIO,
    PriorDirectionStatus,
    RejectionBarStatus,
    RejectionBarV2,
    ReversalPriorDirection,
    ReversalTransitionV2Error,
    evaluate_reversal_prior_direction_v2,
    evaluate_reversal_rejection_bar_v2,
)

START = datetime(2026, 10, 3, 15, tzinfo=UTC)
CASES = [
    pytest.param(("6", "12", "2", "8"), True, id="exact-40-percent"),
    pytest.param(
        ("6", "12", "2", "7.9999999999999999999999999999999999999999"),
        True,
        id="just-above-40-percent",
    ),
    pytest.param(
        ("6", "12", "2", "8.0000000000000000000000000000000000000001"),
        False,
        id="just-below-40-percent",
    ),
    pytest.param(("6", "10", "0", "6"), False, id="equal-prior-extreme"),
    pytest.param(("5", "9", "-1", "5"), False, id="no-sweep"),
    pytest.param(("8", "16", "6", "10"), False, id="close-equal-prior-extreme"),
    pytest.param(("8", "16", "6", "11"), False, id="close-still-outside"),
    pytest.param(("8", "12", "2", "6"), True, id="opposite-color-allowed"),
    pytest.param(("8", "12", "2", "8"), True, id="doji-allowed"),
    pytest.param(("-4", "12", "-8", "-2"), True, id="close-through-other-extreme-allowed"),
]


def _bars(
    ohlc: tuple[str, str, str, str] = ("6", "12", "2", "8"), *, t: int = 5
) -> dict[int, RejectionBarV2]:
    prior = {
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
    open_, high, low, close = map(Decimal, ohlc)
    prior[t] = RejectionBarV2(
        bar_index=t,
        timestamp_utc=START + timedelta(minutes=t),
        close=close,
        is_closed=True,
        open=open_,
        high=high,
        low=low,
    )
    return prior


def _mirror(bars: dict[int, RejectionBarV2]) -> dict[int, RejectionBarV2]:
    return {
        index: replace(
            bar,
            open=bar.open.copy_negate(),
            high=bar.low.copy_negate(),
            low=bar.high.copy_negate(),
            close=bar.close.copy_negate(),
        )
        for index, bar in bars.items()
    }


def _evaluate(bars, t: int = 5):
    return evaluate_reversal_rejection_bar_v2(rejection_candidate_bar_index=t, bars_by_index=bars)


@pytest.mark.parametrize("mirror", [False, True], ids=["UP-to-SHORT", "DOWN-to-LONG"])
@pytest.mark.parametrize(("ohlc", "qualified"), CASES)
def test_sweep_return_wick_boundaries_and_no_body_direction(mirror, ohlc, qualified) -> None:
    bars = _bars(ohlc)
    if mirror:
        bars = _mirror(bars)
    result = _evaluate(bars)
    assert result.status is RejectionBarStatus.EVALUATED
    assert result.rejection_qualified is qualified
    assert result.prior_direction.prior_direction is (
        ReversalPriorDirection.DOWN if mirror else ReversalPriorDirection.UP
    )
    expected_side = RegimeDirection.LONG if mirror else RegimeDirection.SHORT
    assert result.rejection_direction is (expected_side if qualified else None)


@pytest.mark.parametrize("mirror", [False, True], ids=["UP-to-SHORT", "DOWN-to-LONG"])
def test_exact_geometry_and_availability_use_closed_candidate(mirror: bool) -> None:
    bars = _bars()
    if mirror:
        bars = _mirror(bars)
    result = _evaluate(bars)
    assert MIN_REJECTION_WICK_RATIO == Decimal("0.40")
    assert isinstance(MIN_REJECTION_WICK_RATIO, Decimal)
    assert result.prior_high == Decimal(0 if mirror else 10)
    assert result.prior_low == Decimal(-10 if mirror else 0)
    assert result.candidate_range == Decimal(10)
    assert result.upper_wick == Decimal(4)
    assert result.lower_wick == Decimal(4)
    assert result.required_rejection_wick == Decimal(4)
    assert result.rejection_qualified is True
    assert result.rejection_candidate_bar_index == 5
    assert result.known_at_bar_index == 5
    assert result.known_at_timestamp == bars[5].timestamp_utc
    assert result.prior_direction.known_at_bar_index == 4
    assert result.prior_direction.known_at_timestamp == bars[4].timestamp_utc
    assert result.prior_direction == evaluate_reversal_prior_direction_v2(
        reversal_candidate_bar_index=5, bars_by_index=bars
    )


@pytest.mark.parametrize(("ohlc", "qualified"), CASES)
def test_long_short_mirror_symmetry(ohlc, qualified) -> None:
    bars = _bars(ohlc)
    first, mirrored = _evaluate(bars), _evaluate(_mirror(bars))
    assert first.rejection_qualified is mirrored.rejection_qualified is qualified
    assert first.status is mirrored.status
    assert mirrored.candidate_range == first.candidate_range
    assert mirrored.required_rejection_wick == first.required_rejection_wick
    assert mirrored.upper_wick == first.lower_wick
    assert mirrored.lower_wick == first.upper_wick
    assert mirrored.prior_high == first.prior_low.copy_negate()
    assert mirrored.prior_low == first.prior_high.copy_negate()
    assert mirrored.prior_direction.up_steps == first.prior_direction.down_steps
    assert mirrored.prior_direction.down_steps == first.prior_direction.up_steps


@pytest.mark.parametrize("mirror", [False, True])
@pytest.mark.parametrize(
    ("close", "qualified"),
    [
        ("8", True),
        ("8.0000000000000000000000000000000000000001", False),
        ("7.9999999999999999999999999999999999999999", True),
    ],
)
def test_no_rounding_under_reduced_ambient_decimal_precision(mirror, close, qualified) -> None:
    bars = _bars(("6", "12", "2", close))
    if mirror:
        bars = _mirror(bars)
    with localcontext() as context:
        context.prec = 2
        result = _evaluate(bars)
    assert result.rejection_qualified is qualified
    assert result.required_rejection_wick == Decimal(4)
    terminal_wick = result.lower_wick if mirror else result.upper_wick
    expected = {
        "8": Decimal(4),
        "8.0000000000000000000000000000000000000001": Decimal(
            "3.9999999999999999999999999999999999999999"
        ),
        "7.9999999999999999999999999999999999999999": Decimal(
            "4.0000000000000000000000000000000000000001"
        ),
    }
    assert terminal_wick == expected[close]


def test_integer_prices_have_exact_decimal_geometry() -> None:
    bars = {
        index: replace(
            bar, open=int(bar.open), high=int(bar.high), low=int(bar.low), close=int(bar.close)
        )
        for index, bar in _bars().items()
    }
    result = _evaluate(bars)
    assert result.rejection_qualified is True
    assert result.required_rejection_wick == Decimal(4)


@pytest.mark.parametrize("mirror", [False, True])
@pytest.mark.parametrize("extreme_index", range(5))
def test_prior_extreme_uses_every_bar_in_the_same_five_bar_window(mirror, extreme_index) -> None:
    bars = _bars()
    bars[extreme_index] = replace(bars[extreme_index], high=Decimal(12), low=Decimal(-2))
    if mirror:
        bars = _mirror(bars)
    result = _evaluate(bars)
    assert result.prior_high == Decimal(2 if mirror else 12)
    assert result.prior_low == Decimal(-12 if mirror else -2)
    assert result.rejection_qualified is False  # Candidate equals the prior extreme.


@pytest.mark.parametrize("closes", [("1", "4", "3", "6", "5"), ("3",) * 5])
def test_none_prior_direction_cannot_qualify_even_with_valid_rejection_geometry(closes) -> None:
    bars = _bars()
    for index, close in enumerate(closes):
        bars[index] = replace(bars[index], close=Decimal(close), open=Decimal(close))
    result = _evaluate(bars)
    assert result.status is RejectionBarStatus.EVALUATED
    assert result.prior_direction.prior_direction is ReversalPriorDirection.NONE
    assert result.rejection_qualified is False
    assert result.rejection_direction is None


def test_three_of_four_prior_direction_is_reused_without_impulse_requirement() -> None:
    bars = _bars()
    bars[3] = replace(bars[3], close=Decimal(6), open=Decimal(6))
    result = _evaluate(bars)
    assert result.prior_direction.up_steps == 3
    assert result.prior_direction.down_steps == 1
    assert result.prior_direction.prior_direction is ReversalPriorDirection.UP
    assert result.rejection_qualified is True


@pytest.mark.parametrize("count", range(5))
def test_fewer_than_five_completed_prior_bars_is_insufficient(count: int) -> None:
    result = _evaluate(_bars(t=count), count)
    assert result.status is RejectionBarStatus.INSUFFICIENT_WARMUP
    assert result.prior_direction.prior_direction is ReversalPriorDirection.NONE
    assert result.rejection_qualified is False
    assert result.rejection_direction is None


@pytest.mark.parametrize("index", range(5))
def test_missing_or_unclosed_prior_bar_cannot_be_replaced_with_candidate(index: int) -> None:
    bars = _bars()
    bars[index] = replace(bars[index], is_closed=False)
    assert _evaluate(bars).status is RejectionBarStatus.INSUFFICIENT_WARMUP
    del bars[index]
    assert _evaluate(bars).status is RejectionBarStatus.INSUFFICIENT_WARMUP


@pytest.mark.parametrize("invalid", [None, Decimal("NaN"), Decimal("Infinity")])
def test_invalid_required_close_retains_frozen_prior_direction_status(invalid) -> None:
    bars = _bars()
    bars[2] = replace(bars[2], close=invalid)
    result = _evaluate(bars)
    assert result.status is RejectionBarStatus.INVALID_PRIOR_DIRECTION_INPUT
    assert result.prior_direction.status is PriorDirectionStatus.INVALID_PRIOR_DIRECTION_INPUT
    assert result.rejection_qualified is False
    assert result.rejection_direction is None


@pytest.mark.parametrize("field", ["high", "low"])
@pytest.mark.parametrize("invalid", [None, Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity")])
def test_invalid_prior_extrema_fail_closed_with_explicit_status(field, invalid) -> None:
    bars = _bars()
    bars[2] = replace(bars[2], **{field: invalid})
    result = _evaluate(bars)
    assert result.status is RejectionBarStatus.INVALID_PRIOR_EXTREMA
    assert result.prior_direction.prior_direction is ReversalPriorDirection.UP
    assert result.rejection_qualified is False
    assert result.rejection_direction is None


def test_inverted_prior_extrema_are_invalid() -> None:
    bars = _bars()
    bars[2] = replace(bars[2], high=Decimal(-1), low=Decimal(0))
    assert _evaluate(bars).status is RejectionBarStatus.INVALID_PRIOR_EXTREMA


@pytest.mark.parametrize("field", ["open", "high", "low", "close"])
@pytest.mark.parametrize("invalid", [None, Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity")])
def test_missing_or_nonfinite_candidate_price_is_invalid_ohlc(field, invalid) -> None:
    bars = _bars()
    bars[5] = replace(bars[5], **{field: invalid})
    result = _evaluate(bars)
    assert result.status is RejectionBarStatus.INVALID_OHLC
    assert result.rejection_qualified is False
    assert result.rejection_direction is None


@pytest.mark.parametrize("invalid", [True, "8", 8.0, float("nan"), float("inf")])
def test_inexact_or_nonprice_candidate_types_are_not_silently_coerced(invalid) -> None:
    bars = _bars()
    bars[5] = replace(bars[5], close=invalid)
    assert _evaluate(bars).status is RejectionBarStatus.INVALID_OHLC


@pytest.mark.parametrize(
    "ohlc",
    [
        ("13", "12", "2", "8"),
        ("6", "12", "2", "13"),
        ("1", "12", "2", "8"),
        ("6", "12", "2", "1"),
        ("6", "2", "12", "8"),
    ],
)
def test_malformed_candidate_ohlc_is_rejected_before_range(ohlc) -> None:
    result = _evaluate(_bars(ohlc))
    assert result.status is RejectionBarStatus.INVALID_OHLC
    assert result.rejection_qualified is False


@pytest.mark.parametrize("mirror", [False, True])
def test_valid_zero_range_has_explicit_range_status(mirror: bool) -> None:
    bars = _bars(("8", "8", "8", "8"))
    if mirror:
        bars = _mirror(bars)
    result = _evaluate(bars)
    assert result.status is RejectionBarStatus.INVALID_CANDIDATE_RANGE
    assert result.candidate_range == Decimal(0)
    assert result.rejection_qualified is False
    assert result.rejection_direction is None


def test_candidate_mutation_changes_rejection_only_not_prior_direction_or_extrema() -> None:
    bars = _bars()
    before = _evaluate(bars)
    bars[5] = replace(bars[5], close=Decimal("8.1"))
    after = _evaluate(bars)
    assert before.rejection_qualified is True
    assert after.rejection_qualified is False
    assert before.prior_direction == after.prior_direction
    assert before.prior_high == after.prior_high == Decimal(10)
    assert before.prior_low == after.prior_low == Decimal(0)
    assert before.candidate_range == after.candidate_range
    assert before.upper_wick != after.upper_wick


def test_future_and_older_bars_are_never_read_or_iterated() -> None:
    class WindowOnly(dict):
        def __contains__(self, index):
            assert 10 <= index <= 15
            return super().__contains__(index)

        def __getitem__(self, index):
            assert 10 <= index <= 15
            return super().__getitem__(index)

        def __iter__(self):
            pytest.fail("source mapping iteration could expose future or older bars")

        def values(self):
            pytest.fail("source mapping values could expose future or older bars")

    bars = WindowOnly(_bars(t=15))
    before = _evaluate(bars, 15)
    bars[9] = object()
    bars[16] = object()
    after = _evaluate(bars, 15)
    bars[9] = None
    bars[16] = None
    assert before == after == _evaluate(bars, 15)


def test_unused_historical_open_is_not_an_extra_market_condition() -> None:
    bars = _bars()
    expected = _evaluate(bars)
    bars[2] = replace(bars[2], open=None)
    assert _evaluate(bars) == expected


@pytest.mark.parametrize("index", [-1, True, 5.0])
def test_invalid_candidate_index_is_rejected(index) -> None:
    with pytest.raises(ReversalTransitionV2Error, match="candidate index"):
        _evaluate({}, index)


def test_missing_or_unclosed_candidate_is_rejected() -> None:
    bars = _bars()
    bars[5] = replace(bars[5], is_closed=False)
    with pytest.raises(ReversalTransitionV2Error, match="candidate must be closed"):
        _evaluate(bars)
    del bars[5]
    with pytest.raises(ReversalTransitionV2Error, match="closed rejection candidate is required"):
        _evaluate(bars)


@pytest.mark.parametrize("index", [2, 5])
def test_inconsistent_bar_index_is_rejected(index) -> None:
    bars = _bars()
    bars[index] = replace(bars[index], bar_index=index + 1)
    with pytest.raises(ReversalTransitionV2Error, match="index is inconsistent"):
        _evaluate(bars)


@pytest.mark.parametrize("candidate_time_index", [3, 4])
def test_candidate_timestamp_must_follow_prior_window(candidate_time_index: int) -> None:
    bars = _bars()
    bars[5] = replace(bars[5], timestamp_utc=bars[candidate_time_index].timestamp_utc)
    with pytest.raises(ReversalTransitionV2Error, match="candidate must follow"):
        _evaluate(bars)


def test_result_is_repeatable_immutable_and_not_a_confirmed_reversal_event() -> None:
    result = _evaluate(_bars())
    assert result == _evaluate(_bars())
    with pytest.raises(AttributeError):
        result.rejection_qualified = False
    assert not hasattr(result, "event")
