"""Synthetic tests for the frozen EMA_PULLBACK_V1_MNQ predicates."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from decimal import Decimal

import pytest

from agicore.trading.ema_pullback_v1_mnq import (
    BAR_BASED_EXECUTION_MODEL,
    BID_ASK_SPREAD_MODELED,
    BREAKEVEN,
    BREAKEVEN_DURATION_BARS_TRIGGER,
    BREAKEVEN_FAVORABLE_TICKS_TRIGGER,
    BREAKEVEN_MONETARY_PNL_TRIGGER,
    BREAKEVEN_PRICE,
    BREAKEVEN_R_MULTIPLE_TRIGGER,
    BREAKEVEN_TRIGGER,
    CONFIRMATION_CLOSE_CORRECT_SIDE_REQUIRED,
    EARLIEST_EXECUTION_BAR_OFFSET,
    EMA_SEED_CONVENTION,
    EMA_SLOPE_LOOKBACK_BARS,
    EMA_SLOPE_REQUIRED,
    EXECUTION_PRICE_SOURCE,
    EXECUTION_SIGNAL_TIME,
    EXIT_PRIORITY,
    GAP_THROUGH_STOP_FILLS_AT_BAR_OPEN,
    INITIAL_STOP_BUFFER_POINTS,
    INITIAL_STOP_BUFFER_TICKS,
    INITIAL_STOP_IS_IMMUTABLE,
    INITIAL_STOP_SOURCE_BAR_OFFSET,
    INITIAL_STRUCTURAL_STOP_IS_IMMUTABLE,
    LATENCY_MODELED,
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
    MOVE_STOP_TO_ENTRY,
    POSITION_EXIT_EQUALITY_TRIGGERS_EXIT,
    POSITION_EXIT_WICK_ONLY_TRIGGERS_EXIT,
    PULLBACK_LOOKBACK_BARS,
    PULLBACK_PROXIMITY_QUALIFIES,
    PULLBACK_REQUIRED_TOUCH_BAR_OFFSET,
    SIGNAL_DECISION_ON_CLOSED_BAR,
    SLIPPAGE_MODELED,
    STOP_INTRABAR_SLIPPAGE_MODELED,
    STRUCTURAL_STOP_FIRST,
    TAKE_PROFIT,
    TAKE_PROFIT_ENABLED,
    TAKE_PROFIT_MONETARY_AMOUNT,
    TAKE_PROFIT_PNL_EXIT_ENABLED,
    TAKE_PROFIT_POINTS,
    TAKE_PROFIT_PRICE,
    TAKE_PROFIT_R_MULTIPLE,
    TAKE_PROFIT_TICKS,
    TICK_REALISTIC_FILL_MODELED,
    TRAILING_ACTIVATION,
    TRAILING_DISTANCE,
    TRAILING_REFERENCE,
    TRAILING_STEP,
    TRAILING_STOP,
    TRAILING_STOP_ENABLED,
    TRAILING_UPDATE_FREQUENCY,
    WICK_CROSS_EMA20_ALLOWED,
    BreakevenEvaluationResult,
    ClosedBarEMA20,
    EMA20PositionExitResult,
    EMAPullbackEntrySignalResult,
    EntrySignal,
    ExitPriorityExecutionResult,
    InitialStopFillSource,
    InitialStopTriggerStatus,
    MACDStatus,
    NextBarOpen,
    PositionExitAction,
    PositionExitReason,
    ProtectedEntryExecutionResult,
    PullbackContractError,
    PullbackSide,
    SimulatedExecutionStatus,
    SimulatedOrderPurpose,
    SimulatedOrderType,
    StopEvaluationBar,
    TakeProfitEvaluationResult,
    TrailingStopEvaluationResult,
    arbitrate_exit_at_open,
    construct_initial_structural_stop,
    evaluate_disabled_breakeven,
    evaluate_disabled_take_profit,
    evaluate_disabled_trailing_stop,
    evaluate_ema20_position_exit,
    evaluate_ema20_slope,
    evaluate_ema_pullback_entry_signal,
    evaluate_initial_stop_on_bar,
    evaluate_macd_confirmation,
    evaluate_pullback_confirmation,
    initial_stop_triggered_by_market_price,
    simulate_entry_with_initial_structural_stop,
    simulate_next_bar_market_execution,
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


def _qualified_entry(
    side: PullbackSide,
    *,
    sequence: int = 20,
) -> EMAPullbackEntrySignalResult:
    return EMAPullbackEntrySignalResult(
        side=side,
        signal=EntrySignal(side.value),
        entry_signal_qualifies=True,
        pullback_confirmation_qualifies=True,
        ema20_slope_qualifies=True,
        macd_cross_qualifies=True,
        macd_status=MACDStatus.READY,
        confirmation_bar_sequence=sequence,
    )


def _qualified_exit(
    side: PullbackSide,
    *,
    sequence: int = 20,
) -> EMA20PositionExitResult:
    return EMA20PositionExitResult(
        position_side=side,
        action=PositionExitAction(f"EXIT_{side.value}"),
        exit_qualifies=True,
        decision_bar_sequence=sequence,
        earliest_execution_bar_sequence=sequence + 1,
    )


def _protected_position(side: PullbackSide):
    decision_close = "100.75" if side is PullbackSide.LONG else "99.25"
    entry_open = Decimal("101.25") if side is PullbackSide.LONG else Decimal("98.75")
    return simulate_entry_with_initial_structural_stop(
        decision=_qualified_entry(side),
        decision_bar=_bar(20, low="99", high="101", close=decision_close),
        required_touch_bar=_bar(18, low="99", high="101", close="100"),
        available_bar_opens=[NextBarOpen(sequence=21, open=entry_open)],
    )


def _evaluate_no_breakeven(
    side: PullbackSide,
    *,
    observed_market_price: str,
    favorable_ticks: str = "0",
    favorable_r_multiple: str = "0",
    unrealized_pnl: str = "0",
    elapsed_closed_bars: int = 0,
) -> tuple[ProtectedEntryExecutionResult, BreakevenEvaluationResult]:
    position = _protected_position(side)
    result = evaluate_disabled_breakeven(
        position=position,
        observed_market_price=Decimal(observed_market_price),
        favorable_ticks=Decimal(favorable_ticks),
        favorable_r_multiple=Decimal(favorable_r_multiple),
        unrealized_pnl=Decimal(unrealized_pnl),
        elapsed_closed_bars=elapsed_closed_bars,
    )
    return position, result


def _evaluate_no_trailing(
    side: PullbackSide,
    *,
    observed_high: str = "102",
    observed_low: str = "98",
    observed_close: str = "100",
    observed_ema20: str = "100",
    favorable_ticks: str = "0",
    favorable_r_multiple: str = "0",
    unrealized_pnl: str = "0",
    elapsed_closed_bars: int = 0,
) -> tuple[ProtectedEntryExecutionResult, TrailingStopEvaluationResult]:
    position = _protected_position(side)
    result = evaluate_disabled_trailing_stop(
        position=position,
        observed_high=Decimal(observed_high),
        observed_low=Decimal(observed_low),
        observed_close=Decimal(observed_close),
        observed_ema20=Decimal(observed_ema20),
        favorable_ticks=Decimal(favorable_ticks),
        favorable_r_multiple=Decimal(favorable_r_multiple),
        unrealized_pnl=Decimal(unrealized_pnl),
        elapsed_closed_bars=elapsed_closed_bars,
    )
    return position, result


def test_contract_freezes_owner_declared_initial_parameters() -> None:
    assert PULLBACK_LOOKBACK_BARS == 3
    assert PULLBACK_REQUIRED_TOUCH_BAR_OFFSET == 2
    assert MAX_PULLBACK_DISTANCE_TICKS == 8
    assert MAX_PULLBACK_DISTANCE_POINTS == Decimal("2.00")
    assert PULLBACK_PROXIMITY_QUALIFIES is True
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
    assert POSITION_EXIT_EQUALITY_TRIGGERS_EXIT is False
    assert POSITION_EXIT_WICK_ONLY_TRIGGERS_EXIT is False
    assert EXECUTION_SIGNAL_TIME == "CLOSE_T"
    assert EXECUTION_PRICE_SOURCE == "OPEN_T_PLUS_1"
    assert BAR_BASED_EXECUTION_MODEL is True
    assert SLIPPAGE_MODELED is False
    assert BID_ASK_SPREAD_MODELED is False
    assert LATENCY_MODELED is False
    assert TICK_REALISTIC_FILL_MODELED is False
    assert INITIAL_STOP_SOURCE_BAR_OFFSET == 2
    assert INITIAL_STOP_BUFFER_TICKS == 1
    assert INITIAL_STOP_BUFFER_POINTS == Decimal("0.25")
    assert INITIAL_STOP_IS_IMMUTABLE is True
    assert GAP_THROUGH_STOP_FILLS_AT_BAR_OPEN is True
    assert STOP_INTRABAR_SLIPPAGE_MODELED is False
    assert TAKE_PROFIT == "NONE"
    assert TAKE_PROFIT_ENABLED is False
    assert TAKE_PROFIT_PRICE is None
    assert TAKE_PROFIT_MONETARY_AMOUNT is None
    assert TAKE_PROFIT_TICKS is None
    assert TAKE_PROFIT_POINTS is None
    assert TAKE_PROFIT_R_MULTIPLE is None
    assert TAKE_PROFIT_PNL_EXIT_ENABLED is False
    assert STRUCTURAL_STOP_FIRST is True
    assert EXIT_PRIORITY == ("STRUCTURAL_STOP", "EMA20_EXIT")
    assert BREAKEVEN == "NONE"
    assert INITIAL_STRUCTURAL_STOP_IS_IMMUTABLE is True
    assert MOVE_STOP_TO_ENTRY is False
    assert BREAKEVEN_TRIGGER is None
    assert BREAKEVEN_PRICE is None
    assert BREAKEVEN_FAVORABLE_TICKS_TRIGGER is None
    assert BREAKEVEN_R_MULTIPLE_TRIGGER is None
    assert BREAKEVEN_MONETARY_PNL_TRIGGER is None
    assert BREAKEVEN_DURATION_BARS_TRIGGER is None
    assert TRAILING_STOP == "NONE"
    assert TRAILING_STOP_ENABLED is False
    assert TRAILING_ACTIVATION is None
    assert TRAILING_DISTANCE is None
    assert TRAILING_STEP is None
    assert TRAILING_UPDATE_FREQUENCY is None
    assert TRAILING_REFERENCE is None


def test_long_qualifies_after_prior_pullback_and_strict_close_above_ema20() -> None:
    preceding = (
        _bar(7, low="103.00", high="104.00", close="103.50"),
        _bar(8, low="99.75", high="101.00", close="100.50"),
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
        _bar(8, low="99.00", high="100.25", close="99.50"),
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
def test_exact_eight_tick_proximity_on_required_t_minus_two_qualifies(
    side: PullbackSide,
    low: str,
    high: str,
    confirmation_close: str,
) -> None:
    preceding = list(_far_preceding_bars())
    preceding[1] = _bar(8, low=low, high=high, close=low)
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
    assert result.pullback_found is True
    assert result.minimum_distance_points == Decimal("2.00")
    assert result.minimum_distance_ticks == Decimal(8)
    assert result.required_touch_distance_points == Decimal("2.00")
    assert result.required_touch_distance_ticks == Decimal(8)
    assert result.qualifying_bar_sequence == 8


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
    preceding[1] = _bar(8, low="99.00", high="101.00", close="100.50")
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
    assert result.required_touch_distance_points == Decimal(0)
    assert result.qualifying_bar_sequence == 8


@pytest.mark.parametrize("touch_sequence", [7, 9])
def test_touch_on_another_preceding_bar_does_not_replace_t_minus_two(
    touch_sequence: int,
) -> None:
    preceding = list(_far_preceding_bars())
    touch_index = touch_sequence - 7
    preceding[touch_index] = _bar(
        touch_sequence,
        low="99.00",
        high="101.00",
        close="100.50",
    )
    confirmation = _bar(10, low="99.50", high="100.50", close="100.25")

    result = evaluate_pullback_confirmation(
        side=PullbackSide.LONG,
        preceding_bars=preceding,
        confirmation_bar=confirmation,
    )

    assert result.minimum_distance_points == Decimal(0)
    assert result.required_touch_distance_points == Decimal("3.25")
    assert result.pullback_found is False
    assert result.pullback_confirmation_qualifies is False
    assert result.qualifying_bar_sequence is None


@pytest.mark.parametrize(
    ("low", "high", "close"),
    [
        ("100.00", "101.00", "100.50"),
        ("99.00", "100.00", "99.50"),
    ],
)
def test_required_t_minus_two_endpoint_contact_qualifies(
    low: str,
    high: str,
    close: str,
) -> None:
    preceding = list(_far_preceding_bars())
    preceding[1] = _bar(8, low=low, high=high, close=close)

    result = evaluate_pullback_confirmation(
        side=PullbackSide.LONG,
        preceding_bars=preceding,
        confirmation_bar=_bar(10, low="99.50", high="100.50", close="100.25"),
    )

    assert result.pullback_found is True
    assert result.pullback_confirmation_qualifies is True
    assert result.required_touch_distance_points == Decimal(0)
    assert result.qualifying_bar_sequence == 8


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


def test_long_position_exits_only_after_strict_close_below_ema20() -> None:
    result = evaluate_ema20_position_exit(
        position_side=PullbackSide.LONG,
        closed_bars=[_bar(20, low="98.50", high="100.50", close="99.75")],
        decision_bar_sequence=20,
    )

    assert result.exit_qualifies is True
    assert result.action is PositionExitAction.EXIT_LONG
    assert result.decision_bar_sequence == 20
    assert result.earliest_execution_bar_sequence == 21
    assert result.same_bar_execution_allowed is False


def test_short_position_exits_only_after_strict_close_above_ema20() -> None:
    result = evaluate_ema20_position_exit(
        position_side=PullbackSide.SHORT,
        closed_bars=[_bar(20, low="99.50", high="101.50", close="100.25")],
        decision_bar_sequence=20,
    )

    assert result.exit_qualifies is True
    assert result.action is PositionExitAction.EXIT_SHORT
    assert result.earliest_execution_bar_sequence == 21
    assert result.same_bar_execution_allowed is False


@pytest.mark.parametrize("position_side", [PullbackSide.LONG, PullbackSide.SHORT])
def test_position_exit_equality_at_close_holds(position_side: PullbackSide) -> None:
    result = evaluate_ema20_position_exit(
        position_side=position_side,
        closed_bars=[_bar(20, low="99.50", high="100.50", close="100.00")],
        decision_bar_sequence=20,
    )

    assert result.exit_qualifies is False
    assert result.action is PositionExitAction.HOLD


@pytest.mark.parametrize(
    ("position_side", "low", "high", "close"),
    [
        (PullbackSide.LONG, "99.00", "101.00", "100.25"),
        (PullbackSide.SHORT, "99.00", "101.00", "99.75"),
    ],
)
def test_wick_crossing_ema20_without_wrong_side_close_holds(
    position_side: PullbackSide,
    low: str,
    high: str,
    close: str,
) -> None:
    result = evaluate_ema20_position_exit(
        position_side=position_side,
        closed_bars=[_bar(20, low=low, high=high, close=close)],
        decision_bar_sequence=20,
    )

    assert result.exit_qualifies is False
    assert result.action is PositionExitAction.HOLD


def test_position_exit_uses_only_closed_decision_bar_and_ignores_t_plus_one() -> None:
    history = (
        _bar(19, low="99.00", high="101.00", close="100.50"),
        _bar(20, low="98.50", high="100.50", close="99.75"),
    )
    future_above = history + (_bar(21, low="499", high="501", close="500", ema20="400"),)
    future_below = history + (_bar(21, low="49", high="51", close="50", ema20="100"),)

    above_result = evaluate_ema20_position_exit(
        position_side=PullbackSide.LONG,
        closed_bars=future_above,
        decision_bar_sequence=20,
    )
    below_result = evaluate_ema20_position_exit(
        position_side=PullbackSide.LONG,
        closed_bars=future_below,
        decision_bar_sequence=20,
    )

    assert above_result == below_result
    assert above_result.action is PositionExitAction.EXIT_LONG
    assert above_result.earliest_execution_bar_sequence == 21


def test_position_exit_fails_closed_when_decision_bar_is_missing() -> None:
    with pytest.raises(PullbackContractError, match="exactly one decision bar"):
        evaluate_ema20_position_exit(
            position_side=PullbackSide.LONG,
            closed_bars=[_bar(19, low="99", high="101", close="100")],
            decision_bar_sequence=20,
        )


def test_position_exit_fails_closed_when_decision_bar_is_duplicated() -> None:
    decision_bar = _bar(20, low="99", high="101", close="100")

    with pytest.raises(PullbackContractError, match="exactly one decision bar"):
        evaluate_ema20_position_exit(
            position_side=PullbackSide.SHORT,
            closed_bars=[decision_bar, decision_bar],
            decision_bar_sequence=20,
        )


def test_long_entry_fills_at_open_t_plus_one() -> None:
    result = simulate_next_bar_market_execution(
        decision=_qualified_entry(PullbackSide.LONG),
        decision_bar=_bar(20, low="99", high="101", close="100.75"),
        available_bar_opens=[NextBarOpen(sequence=21, open=Decimal("101.25"))],
    )

    assert result.purpose is SimulatedOrderPurpose.ENTRY
    assert result.side is PullbackSide.LONG
    assert result.order_type is SimulatedOrderType.MARKET
    assert result.status is SimulatedExecutionStatus.FILLED
    assert result.execution_bar_sequence == 21
    assert result.execution_price == Decimal("101.25")
    assert result.position_opened is True
    assert result.position_closed is False
    assert result.same_bar_execution_allowed is False


def test_short_entry_fills_at_open_t_plus_one() -> None:
    result = simulate_next_bar_market_execution(
        decision=_qualified_entry(PullbackSide.SHORT),
        decision_bar=_bar(20, low="99", high="101", close="99.25"),
        available_bar_opens=[NextBarOpen(sequence=21, open=Decimal("98.75"))],
    )

    assert result.purpose is SimulatedOrderPurpose.ENTRY
    assert result.side is PullbackSide.SHORT
    assert result.status is SimulatedExecutionStatus.FILLED
    assert result.execution_price == Decimal("98.75")
    assert result.position_opened is True


def test_long_exit_fills_at_open_t_plus_one() -> None:
    result = simulate_next_bar_market_execution(
        decision=_qualified_exit(PullbackSide.LONG),
        decision_bar=_bar(20, low="98", high="100", close="99.25"),
        available_bar_opens=[NextBarOpen(sequence=21, open=Decimal("99.00"))],
    )

    assert result.purpose is SimulatedOrderPurpose.EXIT
    assert result.side is PullbackSide.LONG
    assert result.order_type is SimulatedOrderType.MARKET
    assert result.status is SimulatedExecutionStatus.FILLED
    assert result.execution_price == Decimal("99.00")
    assert result.position_opened is False
    assert result.position_closed is True


def test_short_exit_fills_at_open_t_plus_one() -> None:
    result = simulate_next_bar_market_execution(
        decision=_qualified_exit(PullbackSide.SHORT),
        decision_bar=_bar(20, low="100", high="102", close="100.75"),
        available_bar_opens=[NextBarOpen(sequence=21, open=Decimal("101.00"))],
    )

    assert result.purpose is SimulatedOrderPurpose.EXIT
    assert result.side is PullbackSide.SHORT
    assert result.status is SimulatedExecutionStatus.FILLED
    assert result.execution_price == Decimal("101.00")
    assert result.position_closed is True


@pytest.mark.parametrize(
    "decision",
    [
        _qualified_entry(PullbackSide.LONG),
        _qualified_exit(PullbackSide.LONG),
    ],
)
def test_missing_t_plus_one_expires_without_execution(
    decision: EMAPullbackEntrySignalResult | EMA20PositionExitResult,
) -> None:
    result = simulate_next_bar_market_execution(
        decision=decision,
        decision_bar=_bar(20, low="99", high="101", close="100.25"),
        available_bar_opens=[NextBarOpen(sequence=22, open=Decimal(500))],
    )

    assert result.status is SimulatedExecutionStatus.EXPIRED_NO_EXECUTION
    assert result.execution_bar_sequence is None
    assert result.execution_price is None
    assert result.position_opened is False
    assert result.position_closed is False


def test_mutating_bars_after_t_plus_one_has_no_effect() -> None:
    decision = _qualified_entry(PullbackSide.LONG)
    decision_bar = _bar(20, low="99", high="101", close="100.25")
    low_future = (
        NextBarOpen(sequence=21, open=Decimal("101.25")),
        NextBarOpen(sequence=22, open=Decimal(50)),
    )
    high_future = (
        NextBarOpen(sequence=21, open=Decimal("101.25")),
        NextBarOpen(sequence=22, open=Decimal(500)),
    )

    low_result = simulate_next_bar_market_execution(
        decision=decision,
        decision_bar=decision_bar,
        available_bar_opens=low_future,
    )
    high_result = simulate_next_bar_market_execution(
        decision=decision,
        decision_bar=decision_bar,
        available_bar_opens=high_future,
    )

    assert low_result == high_result
    assert low_result.execution_price == Decimal("101.25")


def test_execution_never_uses_close_t_as_fill_price() -> None:
    decision_bar = _bar(20, low="99", high="101", close="99.75")
    result = simulate_next_bar_market_execution(
        decision=_qualified_entry(PullbackSide.LONG),
        decision_bar=decision_bar,
        available_bar_opens=[NextBarOpen(sequence=21, open=Decimal("101.25"))],
    )

    assert result.signal_time == "CLOSE_T"
    assert result.execution_price_source == "OPEN_T_PLUS_1"
    assert result.execution_price == Decimal("101.25")
    assert result.execution_price != decision_bar.close


def test_same_bar_open_cannot_fill_and_order_expires_without_t_plus_one() -> None:
    result = simulate_next_bar_market_execution(
        decision=_qualified_entry(PullbackSide.SHORT),
        decision_bar=_bar(20, low="99", high="101", close="99.25"),
        available_bar_opens=[NextBarOpen(sequence=20, open=Decimal("99.25"))],
    )

    assert result.status is SimulatedExecutionStatus.EXPIRED_NO_EXECUTION
    assert result.same_bar_execution_allowed is False
    assert result.execution_price is None


def test_repeated_next_bar_execution_is_deterministic() -> None:
    arguments = {
        "decision": _qualified_exit(PullbackSide.SHORT),
        "decision_bar": _bar(20, low="100", high="102", close="100.75"),
        "available_bar_opens": (NextBarOpen(sequence=21, open=Decimal("101.00")),),
    }

    first = simulate_next_bar_market_execution(**arguments)
    second = simulate_next_bar_market_execution(**arguments)

    assert first == second
    assert first.status is SimulatedExecutionStatus.FILLED


def test_duplicate_t_plus_one_bars_fail_closed() -> None:
    next_bar = NextBarOpen(sequence=21, open=Decimal("101.00"))

    with pytest.raises(PullbackContractError, match=r"duplicate t\+1"):
        simulate_next_bar_market_execution(
            decision=_qualified_entry(PullbackSide.LONG),
            decision_bar=_bar(20, low="99", high="101", close="100.25"),
            available_bar_opens=[next_bar, next_bar],
        )


def test_unqualified_decision_cannot_reach_execution_model() -> None:
    unqualified = EMAPullbackEntrySignalResult(
        side=PullbackSide.LONG,
        signal=EntrySignal.NONE,
        entry_signal_qualifies=False,
        pullback_confirmation_qualifies=False,
        ema20_slope_qualifies=True,
        macd_cross_qualifies=True,
        macd_status=MACDStatus.READY,
        confirmation_bar_sequence=20,
    )

    with pytest.raises(PullbackContractError, match="qualified directional signal"):
        simulate_next_bar_market_execution(
            decision=unqualified,
            decision_bar=_bar(20, low="99", high="101", close="100.25"),
            available_bar_opens=[NextBarOpen(sequence=21, open=Decimal("101.00"))],
        )


@pytest.mark.parametrize(
    ("side", "expected_stop"),
    [
        (PullbackSide.LONG, Decimal("98.75")),
        (PullbackSide.SHORT, Decimal("101.25")),
    ],
)
def test_initial_stop_uses_t_minus_two_extreme_plus_one_tick_buffer(
    side: PullbackSide,
    expected_stop: Decimal,
) -> None:
    stop = construct_initial_structural_stop(
        decision=_qualified_entry(side),
        decision_bar=_bar(20, low="99", high="101", close="100"),
        required_touch_bar=_bar(18, low="99", high="101", close="100"),
    )

    assert stop.stop_price == expected_stop
    assert stop.source_bar_sequence == 18
    assert stop.decision_bar_sequence == 20
    assert stop.buffer_ticks == 1
    assert stop.buffer_points == Decimal("0.25")
    assert stop.immutable is True


@pytest.mark.parametrize(
    ("side", "market_price", "not_triggered_price"),
    [
        (PullbackSide.LONG, Decimal("98.75"), Decimal("99.00")),
        (PullbackSide.SHORT, Decimal("101.25"), Decimal("101.00")),
    ],
)
def test_initial_stop_market_price_trigger_is_inclusive(
    side: PullbackSide,
    market_price: Decimal,
    not_triggered_price: Decimal,
) -> None:
    stop = _protected_position(side).initial_stop

    assert initial_stop_triggered_by_market_price(
        initial_stop=stop,
        market_price=market_price,
    )
    assert not initial_stop_triggered_by_market_price(
        initial_stop=stop,
        market_price=not_triggered_price,
    )


@pytest.mark.parametrize(
    ("side", "bar"),
    [
        (
            PullbackSide.LONG,
            StopEvaluationBar(
                sequence=22,
                open=Decimal("99.50"),
                low=Decimal("98.75"),
                high=Decimal("100.00"),
            ),
        ),
        (
            PullbackSide.SHORT,
            StopEvaluationBar(
                sequence=22,
                open=Decimal("100.50"),
                low=Decimal("100.00"),
                high=Decimal("101.25"),
            ),
        ),
    ],
)
def test_exact_stop_touch_fills_at_stop_price(
    side: PullbackSide,
    bar: StopEvaluationBar,
) -> None:
    result = evaluate_initial_stop_on_bar(position=_protected_position(side), bar=bar)

    assert result.status is InitialStopTriggerStatus.STOP_TRIGGERED
    assert result.fill_source is InitialStopFillSource.STOP_PRICE
    assert result.fill_price == result.stop_price
    assert result.position_closed is True


@pytest.mark.parametrize(
    ("side", "bar"),
    [
        (
            PullbackSide.LONG,
            StopEvaluationBar(
                sequence=22,
                open=Decimal("99.50"),
                low=Decimal("99.00"),
                high=Decimal("100.00"),
            ),
        ),
        (
            PullbackSide.SHORT,
            StopEvaluationBar(
                sequence=22,
                open=Decimal("100.50"),
                low=Decimal("100.00"),
                high=Decimal("101.00"),
            ),
        ),
    ],
)
def test_one_tick_before_initial_stop_does_not_trigger(
    side: PullbackSide,
    bar: StopEvaluationBar,
) -> None:
    result = evaluate_initial_stop_on_bar(position=_protected_position(side), bar=bar)

    assert result.status is InitialStopTriggerStatus.NOT_TRIGGERED
    assert result.fill_source is InitialStopFillSource.NONE
    assert result.fill_price is None
    assert result.position_closed is False


@pytest.mark.parametrize(
    ("side", "bar", "expected_fill"),
    [
        (
            PullbackSide.LONG,
            StopEvaluationBar(
                sequence=22,
                open=Decimal("98.50"),
                low=Decimal("98.00"),
                high=Decimal("99.00"),
            ),
            Decimal("98.50"),
        ),
        (
            PullbackSide.SHORT,
            StopEvaluationBar(
                sequence=22,
                open=Decimal("101.50"),
                low=Decimal("101.00"),
                high=Decimal("102.00"),
            ),
            Decimal("101.50"),
        ),
    ],
)
def test_gap_through_initial_stop_fills_at_bar_open(
    side: PullbackSide,
    bar: StopEvaluationBar,
    expected_fill: Decimal,
) -> None:
    result = evaluate_initial_stop_on_bar(position=_protected_position(side), bar=bar)

    assert result.status is InitialStopTriggerStatus.STOP_TRIGGERED
    assert result.fill_source is InitialStopFillSource.BAR_OPEN_GAP
    assert result.fill_price == expected_fill
    assert result.fill_price != result.stop_price


def test_initial_stop_is_immutable_after_position_creation() -> None:
    position = _protected_position(PullbackSide.LONG)

    with pytest.raises(FrozenInstanceError):
        position.initial_stop.stop_price = Decimal(0)  # type: ignore[misc]

    assert position.initial_stop.stop_price == Decimal("98.75")


@pytest.mark.parametrize(
    ("side", "touch_low", "touch_high", "candidate_entry"),
    [
        (PullbackSide.LONG, "100.00", "101.00", Decimal("99.75")),
        (PullbackSide.LONG, "100.00", "101.00", Decimal("99.50")),
        (PullbackSide.SHORT, "99.00", "100.00", Decimal("100.25")),
        (PullbackSide.SHORT, "99.00", "100.00", Decimal("100.50")),
    ],
)
def test_invalid_initial_stop_relative_to_entry_rejects_position(
    side: PullbackSide,
    touch_low: str,
    touch_high: str,
    candidate_entry: Decimal,
) -> None:
    result = simulate_entry_with_initial_structural_stop(
        decision=_qualified_entry(side),
        decision_bar=_bar(20, low="99", high="101", close="100"),
        required_touch_bar=_bar(
            18,
            low=touch_low,
            high=touch_high,
            close=touch_low,
        ),
        available_bar_opens=[NextBarOpen(sequence=21, open=candidate_entry)],
    )

    assert result.status is SimulatedExecutionStatus.REJECT_ENTRY
    assert result.candidate_entry_price == candidate_entry
    assert result.entry_price is None
    assert result.position_opened is False


def test_missing_t_plus_one_expires_protected_entry_without_position() -> None:
    result = simulate_entry_with_initial_structural_stop(
        decision=_qualified_entry(PullbackSide.LONG),
        decision_bar=_bar(20, low="99", high="101", close="100.75"),
        required_touch_bar=_bar(18, low="99", high="101", close="100"),
        available_bar_opens=[NextBarOpen(sequence=22, open=Decimal("101.25"))],
    )

    assert result.status is SimulatedExecutionStatus.EXPIRED_NO_EXECUTION
    assert result.entry_price is None
    assert result.position_opened is False
    assert result.initial_stop.stop_price == Decimal("98.75")


def test_later_bars_cannot_mutate_frozen_initial_stop() -> None:
    position = _protected_position(PullbackSide.LONG)
    original_stop = position.initial_stop

    evaluate_initial_stop_on_bar(
        position=position,
        bar=StopEvaluationBar(
            sequence=22,
            open=Decimal(100),
            low=Decimal(99),
            high=Decimal(500),
        ),
    )
    evaluate_initial_stop_on_bar(
        position=position,
        bar=StopEvaluationBar(
            sequence=23,
            open=Decimal("98.50"),
            low=Decimal(50),
            high=Decimal(99),
        ),
    )

    assert position.initial_stop is original_stop
    assert position.initial_stop.stop_price == Decimal("98.75")
    assert position.initial_stop.source_bar_sequence == 18


def test_initial_stop_rejects_noncausal_source_bar() -> None:
    with pytest.raises(PullbackContractError, match="causal closed bar t-2"):
        construct_initial_structural_stop(
            decision=_qualified_entry(PullbackSide.LONG),
            decision_bar=_bar(20, low="99", high="101", close="100.75"),
            required_touch_bar=_bar(19, low="99", high="101", close="100"),
        )


def test_initial_stop_rejects_decision_bar_not_matching_signal() -> None:
    with pytest.raises(PullbackContractError, match="must match the entry signal"):
        construct_initial_structural_stop(
            decision=_qualified_entry(PullbackSide.SHORT),
            decision_bar=_bar(21, low="99", high="101", close="99.25"),
            required_touch_bar=_bar(19, low="99", high="101", close="100"),
        )


@pytest.mark.parametrize(
    ("side", "observed_market_price", "unrealized_pnl"),
    [
        (PullbackSide.LONG, Decimal(1000000), Decimal(999999)),
        (PullbackSide.SHORT, Decimal(0), Decimal(999999)),
    ],
)
def test_arbitrary_favorable_price_never_creates_take_profit_exit(
    side: PullbackSide,
    observed_market_price: Decimal,
    unrealized_pnl: Decimal,
) -> None:
    result = evaluate_disabled_take_profit(
        position_side=side,
        observed_market_price=observed_market_price,
        unrealized_pnl=unrealized_pnl,
    )

    assert result.action is PositionExitAction.HOLD
    assert result.exit_qualifies is False
    assert result.position_closed is False
    assert result.take_profit_enabled is False
    assert result.take_profit_price is None


def test_no_take_profit_dimension_or_hidden_target_is_configured() -> None:
    result = evaluate_disabled_take_profit(
        position_side=PullbackSide.LONG,
        observed_market_price=Decimal(1000000),
        unrealized_pnl=Decimal(1000000),
    )

    assert result.take_profit == "NONE"
    assert result.monetary_amount is None
    assert result.ticks is None
    assert result.points is None
    assert result.risk_multiple is None
    assert result.pnl_exit_enabled is False


@pytest.mark.parametrize("unrealized_pnl", ["0", "100", "500", "1000000000"])
def test_unrealized_pnl_threshold_never_triggers_take_profit(unrealized_pnl: str) -> None:
    result = evaluate_disabled_take_profit(
        position_side=PullbackSide.LONG,
        observed_market_price=Decimal(1000000),
        unrealized_pnl=Decimal(unrealized_pnl),
    )

    assert result.exit_qualifies is False
    assert result.action is PositionExitAction.HOLD
    assert result.position_closed is False


def test_take_profit_contract_rejects_any_attempt_to_enable_hidden_target() -> None:
    with pytest.raises(PullbackContractError, match="must remain explicitly disabled"):
        TakeProfitEvaluationResult(
            position_side=PullbackSide.SHORT,
            take_profit_enabled=True,
        )


def test_disabled_take_profit_is_deterministic_for_repeated_observation() -> None:
    arguments = {
        "position_side": PullbackSide.SHORT,
        "observed_market_price": Decimal(1),
        "unrealized_pnl": Decimal(999999),
    }

    assert evaluate_disabled_take_profit(**arguments) == evaluate_disabled_take_profit(**arguments)


@pytest.mark.parametrize(
    ("side", "open_price"),
    [
        (PullbackSide.LONG, Decimal("98.50")),
        (PullbackSide.SHORT, Decimal("101.50")),
    ],
)
def test_structural_stop_wins_collision_with_pending_ema20_exit_at_same_open(
    side: PullbackSide,
    open_price: Decimal,
) -> None:
    result = arbitrate_exit_at_open(
        position=_protected_position(side),
        pending_ema20_exit=_qualified_exit(side, sequence=21),
        execution_bar=NextBarOpen(sequence=22, open=open_price),
    )

    assert result.exit_reason is PositionExitReason.STRUCTURAL_STOP
    assert result.fill_price == open_price
    assert result.structural_stop_executed is True
    assert result.ema20_exit_executed is False
    assert result.cancel_pending_ema20_exit is True
    assert result.cancel_structural_stop is False
    assert result.fill_count == 1
    assert result.position_close_count == 1
    assert result.position_closed is True


@pytest.mark.parametrize(
    ("side", "stop_price"),
    [
        (PullbackSide.LONG, Decimal("98.75")),
        (PullbackSide.SHORT, Decimal("101.25")),
    ],
)
def test_exact_stop_boundary_has_priority_over_pending_ema20_exit(
    side: PullbackSide,
    stop_price: Decimal,
) -> None:
    result = arbitrate_exit_at_open(
        position=_protected_position(side),
        pending_ema20_exit=_qualified_exit(side, sequence=21),
        execution_bar=NextBarOpen(sequence=22, open=stop_price),
    )

    assert result.exit_reason is PositionExitReason.STRUCTURAL_STOP
    assert result.fill_price == stop_price
    assert result.cancel_pending_ema20_exit is True


@pytest.mark.parametrize(
    ("side", "open_price"),
    [
        (PullbackSide.LONG, Decimal("99.00")),
        (PullbackSide.SHORT, Decimal("101.00")),
    ],
)
def test_pending_ema20_exit_executes_when_stop_is_not_triggered_at_open(
    side: PullbackSide,
    open_price: Decimal,
) -> None:
    result = arbitrate_exit_at_open(
        position=_protected_position(side),
        pending_ema20_exit=_qualified_exit(side, sequence=21),
        execution_bar=NextBarOpen(sequence=22, open=open_price),
    )

    assert result.exit_reason is PositionExitReason.EMA20_EXIT
    assert result.fill_price == open_price
    assert result.structural_stop_executed is False
    assert result.ema20_exit_executed is True
    assert result.cancel_pending_ema20_exit is False
    assert result.cancel_structural_stop is True
    assert result.fill_count == 1
    assert result.position_close_count == 1
    assert result.position_closed is True


def test_exit_priority_result_rejects_two_fills_or_two_position_closes() -> None:
    common = {
        "side": PullbackSide.LONG,
        "exit_reason": PositionExitReason.STRUCTURAL_STOP,
        "execution_bar_sequence": 22,
        "fill_price": Decimal("98.50"),
        "structural_stop_executed": True,
        "ema20_exit_executed": False,
        "cancel_pending_ema20_exit": True,
        "cancel_structural_stop": False,
    }

    with pytest.raises(PullbackContractError, match="exactly one fill and one close"):
        ExitPriorityExecutionResult(**common, fill_count=2)
    with pytest.raises(PullbackContractError, match="exactly one fill and one close"):
        ExitPriorityExecutionResult(**common, position_close_count=2)


def test_exit_priority_result_rejects_executing_both_exit_paths() -> None:
    with pytest.raises(PullbackContractError, match="execute one exit and cancel the other"):
        ExitPriorityExecutionResult(
            side=PullbackSide.SHORT,
            exit_reason=PositionExitReason.STRUCTURAL_STOP,
            execution_bar_sequence=22,
            fill_price=Decimal("101.50"),
            structural_stop_executed=True,
            ema20_exit_executed=True,
            cancel_pending_ema20_exit=True,
            cancel_structural_stop=False,
        )


def test_exit_priority_rejects_position_and_pending_exit_side_mismatch() -> None:
    with pytest.raises(PullbackContractError, match="sides must match"):
        arbitrate_exit_at_open(
            position=_protected_position(PullbackSide.LONG),
            pending_ema20_exit=_qualified_exit(PullbackSide.SHORT, sequence=21),
            execution_bar=NextBarOpen(sequence=22, open=Decimal("98.50")),
        )


def test_exit_priority_requires_exact_pending_exit_execution_bar() -> None:
    with pytest.raises(PullbackContractError, match="exact next bar"):
        arbitrate_exit_at_open(
            position=_protected_position(PullbackSide.LONG),
            pending_ema20_exit=_qualified_exit(PullbackSide.LONG, sequence=21),
            execution_bar=NextBarOpen(sequence=23, open=Decimal("98.50")),
        )


@pytest.mark.parametrize(
    ("side", "open_price"),
    [
        (PullbackSide.LONG, Decimal("98.50")),
        (PullbackSide.LONG, Decimal("99.00")),
        (PullbackSide.SHORT, Decimal("101.50")),
        (PullbackSide.SHORT, Decimal("101.00")),
    ],
)
def test_exit_priority_is_reproducible(
    side: PullbackSide,
    open_price: Decimal,
) -> None:
    arguments = {
        "position": _protected_position(side),
        "pending_ema20_exit": _qualified_exit(side, sequence=21),
        "execution_bar": NextBarOpen(sequence=22, open=open_price),
    }

    assert arbitrate_exit_at_open(**arguments) == arbitrate_exit_at_open(**arguments)


@pytest.mark.parametrize(
    ("side", "favorable_price"),
    [
        (PullbackSide.LONG, "120.00"),
        (PullbackSide.SHORT, "80.00"),
    ],
)
def test_favorable_profit_never_moves_initial_stop(
    side: PullbackSide,
    favorable_price: str,
) -> None:
    position, result = _evaluate_no_breakeven(
        side,
        observed_market_price=favorable_price,
        favorable_ticks="200",
        favorable_r_multiple="10",
        unrealized_pnl="5000",
        elapsed_closed_bars=100,
    )

    assert result.position_side is side
    assert result.initial_stop is position.initial_stop
    assert result.active_stop is position.initial_stop
    assert result.active_stop.stop_price == position.initial_stop.stop_price
    assert result.move_stop_to_entry is False
    assert result.breakeven_price is None


@pytest.mark.parametrize(
    ("side", "favorable_price", "retracement_price"),
    [
        (PullbackSide.LONG, "120.00", "100.00"),
        (PullbackSide.SHORT, "80.00", "100.00"),
    ],
)
def test_price_exceeds_entry_then_retraces_without_moving_stop(
    side: PullbackSide,
    favorable_price: str,
    retracement_price: str,
) -> None:
    position = _protected_position(side)
    original_stop = position.initial_stop
    common = {
        "position": position,
        "favorable_ticks": Decimal(80),
        "favorable_r_multiple": Decimal(4),
        "unrealized_pnl": Decimal(2000),
    }

    favorable_result = evaluate_disabled_breakeven(
        **common,
        observed_market_price=Decimal(favorable_price),
        elapsed_closed_bars=10,
    )
    retracement_result = evaluate_disabled_breakeven(
        **common,
        observed_market_price=Decimal(retracement_price),
        elapsed_closed_bars=11,
    )

    assert favorable_result.active_stop is original_stop
    assert retracement_result.active_stop is original_stop
    assert position.initial_stop is original_stop
    assert retracement_result.active_stop.stop_price == original_stop.stop_price


@pytest.mark.parametrize("side", [PullbackSide.LONG, PullbackSide.SHORT])
@pytest.mark.parametrize(
    ("favorable_ticks", "favorable_r_multiple"),
    [("4", "1"), ("8", "2"), ("1000", "25")],
)
def test_one_r_two_r_or_any_tick_profit_never_triggers_breakeven(
    side: PullbackSide,
    favorable_ticks: str,
    favorable_r_multiple: str,
) -> None:
    favorable_price = "1000" if side is PullbackSide.LONG else "1"
    position, result = _evaluate_no_breakeven(
        side,
        observed_market_price=favorable_price,
        favorable_ticks=favorable_ticks,
        favorable_r_multiple=favorable_r_multiple,
        unrealized_pnl="1000000",
        elapsed_closed_bars=1000,
    )

    assert result.active_stop is position.initial_stop
    assert result.breakeven_trigger is None
    assert result.favorable_ticks_trigger is None
    assert result.risk_multiple_trigger is None
    assert result.monetary_pnl_trigger is None
    assert result.duration_bars_trigger is None


def test_breakeven_contract_exposes_no_hidden_trigger_or_price() -> None:
    _, result = _evaluate_no_breakeven(
        PullbackSide.LONG,
        observed_market_price="1000000",
        favorable_ticks="1000000",
        favorable_r_multiple="1000000",
        unrealized_pnl="1000000",
        elapsed_closed_bars=1000000,
    )

    assert result.breakeven == "NONE"
    assert result.initial_structural_stop_is_immutable is True
    assert result.move_stop_to_entry is False
    assert result.breakeven_trigger is None
    assert result.breakeven_price is None


def test_breakeven_contract_rejects_hidden_activation() -> None:
    position = _protected_position(PullbackSide.SHORT)
    common = {
        "position_side": PullbackSide.SHORT,
        "initial_stop": position.initial_stop,
        "active_stop": position.initial_stop,
    }

    with pytest.raises(PullbackContractError, match="must remain explicitly disabled"):
        BreakevenEvaluationResult(**common, move_stop_to_entry=True)
    with pytest.raises(PullbackContractError, match="must remain explicitly disabled"):
        BreakevenEvaluationResult(**common, breakeven_trigger="1R")  # type: ignore[arg-type]


@pytest.mark.parametrize("side", [PullbackSide.LONG, PullbackSide.SHORT])
def test_later_observations_cannot_mutate_prior_breakeven_result_or_stop(
    side: PullbackSide,
) -> None:
    position = _protected_position(side)
    original_stop = position.initial_stop
    baseline = evaluate_disabled_breakeven(
        position=position,
        observed_market_price=position.entry_price,
        favorable_ticks=Decimal(0),
        favorable_r_multiple=Decimal(0),
        unrealized_pnl=Decimal(0),
        elapsed_closed_bars=0,
    )
    future_price = Decimal(1000000) if side is PullbackSide.LONG else Decimal(0)

    evaluate_disabled_breakeven(
        position=position,
        observed_market_price=future_price,
        favorable_ticks=Decimal(1000000),
        favorable_r_multiple=Decimal(1000000),
        unrealized_pnl=Decimal(1000000),
        elapsed_closed_bars=1000000,
    )

    assert baseline.active_stop is original_stop
    assert baseline.active_stop.stop_price == original_stop.stop_price
    assert position.initial_stop is original_stop


@pytest.mark.parametrize("side", [PullbackSide.LONG, PullbackSide.SHORT])
def test_disabled_breakeven_is_deterministic(side: PullbackSide) -> None:
    position = _protected_position(side)
    arguments = {
        "position": position,
        "observed_market_price": Decimal(100),
        "favorable_ticks": Decimal(50),
        "favorable_r_multiple": Decimal(2),
        "unrealized_pnl": Decimal(500),
        "elapsed_closed_bars": 50,
    }

    first = evaluate_disabled_breakeven(**arguments)
    second = evaluate_disabled_breakeven(**arguments)

    assert first == second
    assert first.active_stop is second.active_stop is position.initial_stop


@pytest.mark.parametrize(
    ("side", "observed_high", "observed_low", "observed_close"),
    [
        (PullbackSide.LONG, "150", "100", "140"),
        (PullbackSide.SHORT, "100", "50", "60"),
    ],
)
def test_new_highs_or_lows_never_move_initial_stop(
    side: PullbackSide,
    observed_high: str,
    observed_low: str,
    observed_close: str,
) -> None:
    position, result = _evaluate_no_trailing(
        side,
        observed_high=observed_high,
        observed_low=observed_low,
        observed_close=observed_close,
        favorable_ticks="200",
        favorable_r_multiple="10",
        unrealized_pnl="5000",
        elapsed_closed_bars=100,
    )

    assert result.position_side is side
    assert result.initial_stop is position.initial_stop
    assert result.active_stop is position.initial_stop
    assert result.active_stop.stop_price == position.initial_stop.stop_price


@pytest.mark.parametrize("side", [PullbackSide.LONG, PullbackSide.SHORT])
def test_large_profit_never_activates_trailing_stop(side: PullbackSide) -> None:
    position, result = _evaluate_no_trailing(
        side,
        observed_high="1000001",
        observed_low="0",
        observed_close="1000000" if side is PullbackSide.LONG else "1",
        observed_ema20="500000",
        favorable_ticks="1000000",
        favorable_r_multiple="1000000",
        unrealized_pnl="1000000",
        elapsed_closed_bars=1000000,
    )

    assert result.active_stop is position.initial_stop
    assert result.trailing_stop_enabled is False
    assert result.trailing_activation is None


@pytest.mark.parametrize("side", [PullbackSide.LONG, PullbackSide.SHORT])
@pytest.mark.parametrize(
    ("favorable_ticks", "favorable_r_multiple"),
    [("4", "1"), ("8", "2"), ("1000", "25")],
)
def test_one_r_two_r_or_any_tick_profit_never_activates_trailing(
    side: PullbackSide,
    favorable_ticks: str,
    favorable_r_multiple: str,
) -> None:
    position, result = _evaluate_no_trailing(
        side,
        observed_high="1001",
        observed_low="0",
        observed_close="1000" if side is PullbackSide.LONG else "1",
        favorable_ticks=favorable_ticks,
        favorable_r_multiple=favorable_r_multiple,
        unrealized_pnl="1000000",
        elapsed_closed_bars=1000,
    )

    assert result.active_stop is position.initial_stop
    assert result.trailing_activation is None
    assert result.trailing_distance is None
    assert result.trailing_step is None
    assert result.trailing_reference is None


@pytest.mark.parametrize("side", [PullbackSide.LONG, PullbackSide.SHORT])
def test_new_closed_bars_never_recalculate_initial_stop(side: PullbackSide) -> None:
    position = _protected_position(side)
    original_stop = position.initial_stop
    first = evaluate_disabled_trailing_stop(
        position=position,
        observed_high=Decimal(120),
        observed_low=Decimal(80),
        observed_close=Decimal(110),
        observed_ema20=Decimal(100),
        favorable_ticks=Decimal(80),
        favorable_r_multiple=Decimal(4),
        unrealized_pnl=Decimal(2000),
        elapsed_closed_bars=10,
    )
    second = evaluate_disabled_trailing_stop(
        position=position,
        observed_high=Decimal(200),
        observed_low=Decimal(50),
        observed_close=Decimal(150),
        observed_ema20=Decimal(125),
        favorable_ticks=Decimal(400),
        favorable_r_multiple=Decimal(20),
        unrealized_pnl=Decimal(10000),
        elapsed_closed_bars=11,
    )

    assert first.active_stop is original_stop
    assert second.active_stop is original_stop
    assert position.initial_stop is original_stop


def test_trailing_contract_exposes_no_hidden_configuration() -> None:
    _, result = _evaluate_no_trailing(PullbackSide.LONG)

    assert result.trailing_stop == "NONE"
    assert result.initial_structural_stop_is_immutable is True
    assert result.trailing_stop_enabled is False
    assert result.trailing_activation is None
    assert result.trailing_distance is None
    assert result.trailing_step is None
    assert result.trailing_update_frequency is None
    assert result.trailing_reference is None


@pytest.mark.parametrize(
    "override",
    [
        {"trailing_stop_enabled": True},
        {"trailing_activation": "1R"},
        {"trailing_distance": "8_TICKS"},
        {"trailing_step": "1_TICK"},
        {"trailing_update_frequency": "EACH_BAR"},
        {"trailing_reference": "HIGH_LOW"},
    ],
)
def test_trailing_contract_rejects_hidden_configuration(override: dict[str, object]) -> None:
    position = _protected_position(PullbackSide.SHORT)
    common = {
        "position_side": PullbackSide.SHORT,
        "initial_stop": position.initial_stop,
        "active_stop": position.initial_stop,
    }

    with pytest.raises(PullbackContractError, match="must remain explicitly disabled"):
        TrailingStopEvaluationResult(**common, **override)  # type: ignore[arg-type]


def test_trailing_contract_rejects_equal_but_distinct_stop_object() -> None:
    position = _protected_position(PullbackSide.LONG)

    with pytest.raises(PullbackContractError, match="exact initial stop object"):
        TrailingStopEvaluationResult(
            position_side=PullbackSide.LONG,
            initial_stop=position.initial_stop,
            active_stop=replace(position.initial_stop),
        )


@pytest.mark.parametrize("side", [PullbackSide.LONG, PullbackSide.SHORT])
def test_future_observations_cannot_mutate_prior_trailing_result_or_stop(
    side: PullbackSide,
) -> None:
    position = _protected_position(side)
    original_stop = position.initial_stop
    baseline = evaluate_disabled_trailing_stop(
        position=position,
        observed_high=Decimal(102),
        observed_low=Decimal(98),
        observed_close=Decimal(100),
        observed_ema20=Decimal(100),
        favorable_ticks=Decimal(0),
        favorable_r_multiple=Decimal(0),
        unrealized_pnl=Decimal(0),
        elapsed_closed_bars=0,
    )

    evaluate_disabled_trailing_stop(
        position=position,
        observed_high=Decimal(1000000),
        observed_low=Decimal(0),
        observed_close=Decimal(500000),
        observed_ema20=Decimal(250000),
        favorable_ticks=Decimal(1000000),
        favorable_r_multiple=Decimal(1000000),
        unrealized_pnl=Decimal(1000000),
        elapsed_closed_bars=1000000,
    )

    assert baseline.active_stop is original_stop
    assert baseline.active_stop.stop_price == original_stop.stop_price
    assert position.initial_stop is original_stop


@pytest.mark.parametrize("side", [PullbackSide.LONG, PullbackSide.SHORT])
def test_disabled_trailing_stop_is_deterministic(side: PullbackSide) -> None:
    position = _protected_position(side)
    arguments = {
        "position": position,
        "observed_high": Decimal(150),
        "observed_low": Decimal(50),
        "observed_close": Decimal(100),
        "observed_ema20": Decimal(100),
        "favorable_ticks": Decimal(200),
        "favorable_r_multiple": Decimal(10),
        "unrealized_pnl": Decimal(5000),
        "elapsed_closed_bars": 100,
    }

    first = evaluate_disabled_trailing_stop(**arguments)
    second = evaluate_disabled_trailing_stop(**arguments)

    assert first == second
    assert first.active_stop is second.active_stop is position.initial_stop
