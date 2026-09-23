"""Synthetic tests for the frozen EMA_PULLBACK_V1_MNQ predicates."""

from __future__ import annotations

from decimal import Decimal

import pytest

from agicore.trading.ema_pullback_v1_mnq import (
    CONFIRMATION_CLOSE_CORRECT_SIDE_REQUIRED,
    EARLIEST_EXECUTION_BAR_OFFSET,
    EMA_SEED_CONVENTION,
    EMA_SLOPE_LOOKBACK_BARS,
    EMA_SLOPE_REQUIRED,
    MACD_CROSS_REQUIRED,
    MACD_CROSS_VALIDITY_BARS,
    MACD_FAST_PERIOD,
    MACD_LINE_MA_TYPE,
    MACD_REQUIRED_CLOSED_BARS,
    MACD_SIGNAL_LINE_MA_TYPE,
    MACD_SIGNAL_PERIOD,
    MACD_SLOW_PERIOD,
    MAX_PULLBACK_DISTANCE_POINTS,
    MAX_PULLBACK_DISTANCE_TICKS,
    MINIMUM_EMA_SLOPE_POINTS_PER_BAR,
    PULLBACK_LOOKBACK_BARS,
    SIGNAL_DECISION_ON_CLOSED_BAR,
    WICK_CROSS_EMA20_ALLOWED,
    ClosedBarEMA20,
    EntrySignal,
    MACDStatus,
    PullbackContractError,
    PullbackSide,
    evaluate_ema20_slope,
    evaluate_ema_pullback_entry_signal,
    evaluate_macd_confirmation,
    evaluate_pullback_confirmation,
)


def _bar(
    sequence: int,
    *,
    low: str,
    high: str,
    close: str,
    ema20: str = "100.00",
) -> ClosedBarEMA20:
    return ClosedBarEMA20(
        sequence=sequence,
        low=Decimal(low),
        high=Decimal(high),
        close=Decimal(close),
        ema20=Decimal(ema20),
    )


def _far_preceding_bars() -> tuple[ClosedBarEMA20, ...]:
    return (
        _bar(7, low="103.00", high="104.00", close="103.50"),
        _bar(8, low="103.25", high="104.25", close="103.75"),
        _bar(9, low="103.50", high="104.50", close="104.00"),
    )


def _closed_price_bar(
    sequence: int,
    close: str,
    *,
    ema20: str = "100.00",
) -> ClosedBarEMA20:
    price = Decimal(close)
    return _bar(
        sequence,
        low=str(price - Decimal("0.50")),
        high=str(price + Decimal("0.50")),
        close=close,
        ema20=ema20,
    )


def _macd_history(
    *,
    confirmation_close: str,
    previous_close: str = "100",
) -> tuple[ClosedBarEMA20, ...]:
    closes = ["100"] * 33 + [previous_close, confirmation_close]
    return tuple(_closed_price_bar(sequence, close) for sequence, close in enumerate(closes))


def test_contract_freezes_owner_declared_initial_parameters() -> None:
    assert PULLBACK_LOOKBACK_BARS == 3
    assert MAX_PULLBACK_DISTANCE_TICKS == 8
    assert MAX_PULLBACK_DISTANCE_POINTS == Decimal("2.00")
    assert EMA_SLOPE_REQUIRED is True
    assert MACD_CROSS_REQUIRED is True
    assert WICK_CROSS_EMA20_ALLOWED is True
    assert CONFIRMATION_CLOSE_CORRECT_SIDE_REQUIRED is True
    assert SIGNAL_DECISION_ON_CLOSED_BAR is True
    assert EARLIEST_EXECUTION_BAR_OFFSET == 1
    assert EMA_SLOPE_LOOKBACK_BARS == 3
    assert MINIMUM_EMA_SLOPE_POINTS_PER_BAR == Decimal("0.0")
    assert MACD_FAST_PERIOD == 12
    assert MACD_SLOW_PERIOD == 26
    assert MACD_SIGNAL_PERIOD == 9
    assert MACD_LINE_MA_TYPE == "EMA"
    assert MACD_SIGNAL_LINE_MA_TYPE == "EMA"
    assert MACD_CROSS_VALIDITY_BARS == 1
    assert MACD_REQUIRED_CLOSED_BARS == 35
    assert EMA_SEED_CONVENTION == "FIRST_CLOSE_ALPHA_2_OVER_PERIOD_PLUS_1"


def test_long_qualifies_after_prior_pullback_and_strict_close_above_ema20() -> None:
    preceding = (
        _bar(7, low="103.00", high="104.00", close="103.50"),
        _bar(8, low="101.50", high="103.00", close="102.50"),
        _bar(9, low="103.00", high="104.00", close="103.50"),
    )
    confirmation = _bar(10, low="99.75", high="101.25", close="100.75")

    result = evaluate_pullback_confirmation(
        side=PullbackSide.LONG,
        preceding_bars=preceding,
        confirmation_bar=confirmation,
    )

    assert result.pullback_confirmation_qualifies is True
    assert result.pullback_found is True
    assert result.confirmation_close_correct_side is True
    assert result.qualifying_bar_sequence == 8


def test_short_qualifies_after_prior_pullback_and_strict_close_below_ema20() -> None:
    preceding = (
        _bar(7, low="96.00", high="97.00", close="96.50"),
        _bar(8, low="97.00", high="98.50", close="97.50"),
        _bar(9, low="95.50", high="96.50", close="96.00"),
    )
    confirmation = _bar(10, low="98.75", high="100.25", close="99.25")

    result = evaluate_pullback_confirmation(
        side=PullbackSide.SHORT,
        preceding_bars=preceding,
        confirmation_bar=confirmation,
    )

    assert result.pullback_confirmation_qualifies is True
    assert result.pullback_found is True
    assert result.confirmation_close_correct_side is True
    assert result.qualifying_bar_sequence == 8


@pytest.mark.parametrize(
    ("side", "low", "high", "confirmation_close"),
    [
        (PullbackSide.LONG, "102.00", "103.00", "100.25"),
        (PullbackSide.SHORT, "97.00", "98.00", "99.75"),
    ],
)
def test_exact_eight_tick_distance_is_inclusive(
    side: PullbackSide,
    low: str,
    high: str,
    confirmation_close: str,
) -> None:
    preceding = list(_far_preceding_bars())
    preceding[-1] = _bar(9, low=low, high=high, close=low)
    confirmation = _bar(
        10,
        low="99.50",
        high="100.50",
        close=confirmation_close,
    )

    result = evaluate_pullback_confirmation(
        side=side,
        preceding_bars=preceding,
        confirmation_bar=confirmation,
    )

    assert result.pullback_confirmation_qualifies is True
    assert result.minimum_distance_points == Decimal("2.00")
    assert result.minimum_distance_ticks == Decimal(8)


@pytest.mark.parametrize(
    ("side", "low", "high", "close", "confirmation_close"),
    [
        (PullbackSide.LONG, "102.25", "103.25", "102.75", "100.25"),
        (PullbackSide.SHORT, "96.75", "97.75", "97.25", "99.75"),
    ],
)
def test_nine_tick_distance_is_rejected(
    side: PullbackSide,
    low: str,
    high: str,
    close: str,
    confirmation_close: str,
) -> None:
    preceding = (
        _bar(7, low=low, high=high, close=close),
        _bar(8, low=low, high=high, close=close),
        _bar(9, low=low, high=high, close=close),
    )
    confirmation = _bar(
        10,
        low="99.50",
        high="100.50",
        close=confirmation_close,
    )

    result = evaluate_pullback_confirmation(
        side=side,
        preceding_bars=preceding,
        confirmation_bar=confirmation,
    )

    assert result.pullback_confirmation_qualifies is False
    assert result.pullback_found is False
    assert result.minimum_distance_points == Decimal("2.25")
    assert result.minimum_distance_ticks == Decimal(9)


@pytest.mark.parametrize(
    ("side", "confirmation_close"),
    [
        (PullbackSide.LONG, "100.25"),
        (PullbackSide.SHORT, "99.75"),
    ],
)
def test_wick_may_cross_ema20(side: PullbackSide, confirmation_close: str) -> None:
    preceding = list(_far_preceding_bars())
    preceding[0] = _bar(7, low="99.00", high="101.00", close="100.50")
    confirmation = _bar(
        10,
        low="99.50",
        high="100.50",
        close=confirmation_close,
    )

    result = evaluate_pullback_confirmation(
        side=side,
        preceding_bars=preceding,
        confirmation_bar=confirmation,
    )

    assert result.pullback_confirmation_qualifies is True
    assert result.minimum_distance_points == Decimal(0)
    assert result.qualifying_bar_sequence == 7


@pytest.mark.parametrize("side", [PullbackSide.LONG, PullbackSide.SHORT])
def test_confirmation_close_equal_to_ema20_is_rejected(side: PullbackSide) -> None:
    preceding = list(_far_preceding_bars())
    preceding[1] = _bar(8, low="99.75", high="101.00", close="100.50")
    confirmation = _bar(10, low="99.50", high="100.50", close="100.00")

    result = evaluate_pullback_confirmation(
        side=side,
        preceding_bars=preceding,
        confirmation_bar=confirmation,
    )

    assert result.pullback_confirmation_qualifies is False
    assert result.pullback_found is True
    assert result.confirmation_close_correct_side is False


def test_confirmation_bar_is_not_counted_as_one_of_the_three_pullback_bars() -> None:
    confirmation = _bar(10, low="99.00", high="101.00", close="100.25")

    result = evaluate_pullback_confirmation(
        side=PullbackSide.LONG,
        preceding_bars=_far_preceding_bars(),
        confirmation_bar=confirmation,
    )

    assert result.pullback_confirmation_qualifies is False
    assert result.pullback_found is False


def test_window_must_contain_exactly_three_immediately_preceding_closed_bars() -> None:
    confirmation = _bar(10, low="99.50", high="100.50", close="100.25")

    with pytest.raises(PullbackContractError, match="exactly 3"):
        evaluate_pullback_confirmation(
            side=PullbackSide.LONG,
            preceding_bars=_far_preceding_bars()[:2],
            confirmation_bar=confirmation,
        )
    with pytest.raises(PullbackContractError, match="three causal bars"):
        evaluate_pullback_confirmation(
            side=PullbackSide.LONG,
            preceding_bars=(
                _bar(7, low="99.00", high="101.00", close="100.50"),
                _bar(8, low="103.00", high="104.00", close="103.50"),
                _bar(11, low="103.00", high="104.00", close="103.50"),
            ),
            confirmation_bar=confirmation,
        )


def test_invalid_closed_bar_fails_closed() -> None:
    with pytest.raises(PullbackContractError, match="close must be inside"):
        _bar(1, low="99.00", high="101.00", close="102.00")


def test_long_ema20_slope_uses_t_and_t_minus_three_closed_values() -> None:
    result = evaluate_ema20_slope(
        side=PullbackSide.LONG,
        lookback_bar=_bar(7, low="99", high="101", close="100", ema20="99"),
        confirmation_bar=_bar(10, low="99", high="101", close="100", ema20="102"),
    )

    assert result.ema20_slope_qualifies is True
    assert result.slope_points_per_bar == Decimal(1)
    assert result.lookback_bar_sequence == 7
    assert result.confirmation_bar_sequence == 10


def test_short_ema20_slope_uses_t_and_t_minus_three_closed_values() -> None:
    result = evaluate_ema20_slope(
        side=PullbackSide.SHORT,
        lookback_bar=_bar(7, low="99", high="101", close="100", ema20="102"),
        confirmation_bar=_bar(10, low="99", high="101", close="100", ema20="99"),
    )

    assert result.ema20_slope_qualifies is True
    assert result.slope_points_per_bar == Decimal(-1)


@pytest.mark.parametrize("side", [PullbackSide.LONG, PullbackSide.SHORT])
def test_zero_ema20_slope_is_rejected(side: PullbackSide) -> None:
    result = evaluate_ema20_slope(
        side=side,
        lookback_bar=_bar(7, low="99", high="101", close="100"),
        confirmation_bar=_bar(10, low="99", high="101", close="100"),
    )

    assert result.slope_points_per_bar == Decimal(0)
    assert result.ema20_slope_qualifies is False


def test_ema20_slope_equal_to_minimum_threshold_is_rejected() -> None:
    result = evaluate_ema20_slope(
        side=PullbackSide.LONG,
        lookback_bar=_bar(7, low="99", high="101", close="100"),
        confirmation_bar=_bar(10, low="99", high="101", close="100"),
    )

    assert result.slope_points_per_bar == MINIMUM_EMA_SLOPE_POINTS_PER_BAR
    assert result.ema20_slope_qualifies is False


def test_very_small_positive_ema20_slope_qualifies_long_only() -> None:
    long_result = evaluate_ema20_slope(
        side=PullbackSide.LONG,
        lookback_bar=_bar(7, low="99", high="101", close="100", ema20="100"),
        confirmation_bar=_bar(
            10,
            low="99",
            high="101",
            close="100",
            ema20="100.000000000000000000000003",
        ),
    )
    short_result = evaluate_ema20_slope(
        side=PullbackSide.SHORT,
        lookback_bar=_bar(7, low="99", high="101", close="100", ema20="100"),
        confirmation_bar=_bar(
            10,
            low="99",
            high="101",
            close="100",
            ema20="100.000000000000000000000003",
        ),
    )

    assert long_result.slope_points_per_bar == Decimal("0.000000000000000000000001")
    assert long_result.ema20_slope_qualifies is True
    assert short_result.ema20_slope_qualifies is False


def test_very_small_negative_ema20_slope_qualifies_short_only() -> None:
    long_result = evaluate_ema20_slope(
        side=PullbackSide.LONG,
        lookback_bar=_bar(7, low="99", high="101", close="100", ema20="100"),
        confirmation_bar=_bar(
            10,
            low="99",
            high="101",
            close="100",
            ema20="99.999999999999999999999997",
        ),
    )
    short_result = evaluate_ema20_slope(
        side=PullbackSide.SHORT,
        lookback_bar=_bar(7, low="99", high="101", close="100", ema20="100"),
        confirmation_bar=_bar(
            10,
            low="99",
            high="101",
            close="100",
            ema20="99.999999999999999999999997",
        ),
    )

    assert short_result.slope_points_per_bar == Decimal("-0.000000000000000000000001")
    assert short_result.ema20_slope_qualifies is True
    assert long_result.ema20_slope_qualifies is False


def test_ema20_slope_rejects_insufficient_warmup() -> None:
    with pytest.raises(PullbackContractError, match="3 closed warmup bars"):
        evaluate_ema20_slope(
            side=PullbackSide.LONG,
            lookback_bar=_bar(0, low="99", high="101", close="100"),
            confirmation_bar=_bar(2, low="99", high="101", close="100"),
        )


@pytest.mark.parametrize("non_causal_sequence", [6, 8, 10, 11])
def test_ema20_slope_rejects_any_bar_other_than_exact_t_minus_three(
    non_causal_sequence: int,
) -> None:
    with pytest.raises(PullbackContractError, match="exactly t-3"):
        evaluate_ema20_slope(
            side=PullbackSide.LONG,
            lookback_bar=_bar(
                non_causal_sequence,
                low="99",
                high="101",
                close="100",
            ),
            confirmation_bar=_bar(10, low="99", high="101", close="100"),
        )


def test_bullish_macd_cross_allows_equality_at_t_minus_one() -> None:
    result = evaluate_macd_confirmation(
        side=PullbackSide.LONG,
        closed_bars=_macd_history(confirmation_close="101"),
        confirmation_bar_sequence=34,
    )

    assert result.status is MACDStatus.READY
    assert result.previous_macd_line == result.previous_signal_line
    assert result.current_macd_line is not None
    assert result.current_signal_line is not None
    assert result.current_macd_line > result.current_signal_line
    assert result.macd_cross_qualifies is True
    assert result.signal is EntrySignal.LONG
    assert result.previous_bar_sequence == 33


def test_bearish_macd_cross_allows_equality_at_t_minus_one() -> None:
    result = evaluate_macd_confirmation(
        side=PullbackSide.SHORT,
        closed_bars=_macd_history(confirmation_close="99"),
        confirmation_bar_sequence=34,
    )

    assert result.status is MACDStatus.READY
    assert result.previous_macd_line == result.previous_signal_line
    assert result.current_macd_line is not None
    assert result.current_signal_line is not None
    assert result.current_macd_line < result.current_signal_line
    assert result.macd_cross_qualifies is True
    assert result.signal is EntrySignal.SHORT


@pytest.mark.parametrize("side", [PullbackSide.LONG, PullbackSide.SHORT])
def test_macd_equality_at_confirmation_is_rejected(side: PullbackSide) -> None:
    result = evaluate_macd_confirmation(
        side=side,
        closed_bars=_macd_history(confirmation_close="100"),
        confirmation_bar_sequence=34,
    )

    assert result.status is MACDStatus.READY
    assert result.current_macd_line == result.current_signal_line
    assert result.macd_cross_qualifies is False
    assert result.signal is EntrySignal.NONE


@pytest.mark.parametrize(
    ("side", "previous_close", "confirmation_close"),
    [
        (PullbackSide.LONG, "101", "102"),
        (PullbackSide.SHORT, "99", "98"),
    ],
)
def test_macd_requires_a_new_cross_on_current_closed_bar(
    side: PullbackSide,
    previous_close: str,
    confirmation_close: str,
) -> None:
    result = evaluate_macd_confirmation(
        side=side,
        closed_bars=_macd_history(
            previous_close=previous_close,
            confirmation_close=confirmation_close,
        ),
        confirmation_bar_sequence=34,
    )

    assert result.status is MACDStatus.READY
    assert result.macd_cross_qualifies is False
    assert result.signal is EntrySignal.NONE


@pytest.mark.parametrize("side", [PullbackSide.LONG, PullbackSide.SHORT])
def test_macd_insufficient_warmup_returns_none(side: PullbackSide) -> None:
    history = _macd_history(confirmation_close="101")[:-1]

    result = evaluate_macd_confirmation(
        side=side,
        closed_bars=history,
        confirmation_bar_sequence=33,
    )

    assert result.status is MACDStatus.INSUFFICIENT_WARMUP
    assert result.signal is EntrySignal.NONE
    assert result.macd_cross_qualifies is False
    assert result.observed_closed_bars == 34
    assert result.required_closed_bars == 35
    assert result.current_macd_line is None
    assert result.current_signal_line is None


def test_macd_rejects_non_contiguous_causal_history() -> None:
    history = list(_macd_history(confirmation_close="101"))
    del history[10]

    with pytest.raises(PullbackContractError, match="ordered and contiguous"):
        evaluate_macd_confirmation(
            side=PullbackSide.LONG,
            closed_bars=history,
            confirmation_bar_sequence=34,
        )


def test_mutating_t_plus_one_has_no_effect_on_macd_confirmation() -> None:
    causal_history = _macd_history(confirmation_close="101")
    low_future = causal_history + (_closed_price_bar(35, "50"),)
    high_future = causal_history + (_closed_price_bar(35, "500"),)

    low_result = evaluate_macd_confirmation(
        side=PullbackSide.LONG,
        closed_bars=low_future,
        confirmation_bar_sequence=34,
    )
    high_result = evaluate_macd_confirmation(
        side=PullbackSide.LONG,
        closed_bars=high_future,
        confirmation_bar_sequence=34,
    )

    assert low_result == high_result
    assert low_result.signal is EntrySignal.LONG


@pytest.mark.parametrize(
    ("side", "confirmation_close", "lookback_ema20", "confirmation_ema20", "signal"),
    [
        (PullbackSide.LONG, "101", "99.00", "100.50", EntrySignal.LONG),
        (PullbackSide.SHORT, "99", "101.00", "99.50", EntrySignal.SHORT),
    ],
)
def test_assembled_entry_requires_pullback_slope_and_same_bar_macd_cross(
    side: PullbackSide,
    confirmation_close: str,
    lookback_ema20: str,
    confirmation_ema20: str,
    signal: EntrySignal,
) -> None:
    history = list(_macd_history(confirmation_close=confirmation_close))
    history[31] = _closed_price_bar(31, "100", ema20=lookback_ema20)
    history[34] = _closed_price_bar(
        34,
        confirmation_close,
        ema20=confirmation_ema20,
    )

    result = evaluate_ema_pullback_entry_signal(
        side=side,
        closed_bars=history,
        confirmation_bar_sequence=34,
    )

    assert result.entry_signal_qualifies is True
    assert result.pullback_confirmation_qualifies is True
    assert result.ema20_slope_qualifies is True
    assert result.macd_cross_qualifies is True
    assert result.macd_status is MACDStatus.READY
    assert result.signal is signal
    assert result.confirmation_bar_sequence == 34


def test_assembled_entry_returns_none_when_one_mandatory_predicate_fails() -> None:
    history = list(_macd_history(confirmation_close="101"))
    history[31] = _closed_price_bar(31, "100", ema20="90")
    history[32] = _closed_price_bar(32, "100", ema20="90")
    history[33] = _closed_price_bar(33, "100", ema20="90")
    history[34] = _closed_price_bar(34, "101", ema20="100.50")

    result = evaluate_ema_pullback_entry_signal(
        side=PullbackSide.LONG,
        closed_bars=history,
        confirmation_bar_sequence=34,
    )

    assert result.pullback_confirmation_qualifies is False
    assert result.ema20_slope_qualifies is True
    assert result.macd_cross_qualifies is True
    assert result.entry_signal_qualifies is False
    assert result.signal is EntrySignal.NONE


def test_assembled_entry_preserves_insufficient_macd_warmup_status() -> None:
    history = list(_macd_history(confirmation_close="101")[:-1])
    history[30] = _closed_price_bar(30, "100", ema20="99.00")
    history[33] = _closed_price_bar(33, "100", ema20="99.50")

    result = evaluate_ema_pullback_entry_signal(
        side=PullbackSide.LONG,
        closed_bars=history,
        confirmation_bar_sequence=33,
    )

    assert result.pullback_confirmation_qualifies is True
    assert result.ema20_slope_qualifies is True
    assert result.macd_status is MACDStatus.INSUFFICIENT_WARMUP
    assert result.macd_cross_qualifies is False
    assert result.entry_signal_qualifies is False
    assert result.signal is EntrySignal.NONE


def test_assembled_entry_ignores_t_plus_one_values() -> None:
    history = list(_macd_history(confirmation_close="101"))
    history[31] = _closed_price_bar(31, "100", ema20="99.00")
    history[34] = _closed_price_bar(34, "101", ema20="100.50")

    low_future = history + [_closed_price_bar(35, "50", ema20="50")]
    high_future = history + [_closed_price_bar(35, "500", ema20="500")]
    low_result = evaluate_ema_pullback_entry_signal(
        side=PullbackSide.LONG,
        closed_bars=low_future,
        confirmation_bar_sequence=34,
    )
    high_result = evaluate_ema_pullback_entry_signal(
        side=PullbackSide.LONG,
        closed_bars=high_future,
        confirmation_bar_sequence=34,
    )

    assert low_result == high_result
    assert low_result.signal is EntrySignal.LONG
