"""Deterministic pullback predicate for ``EMA_PULLBACK_V1_MNQ``.

This module freezes only the strategy rules that the owner has explicitly defined.  It
does not compute EMA20, does not emit a broker-executable order, and never reads market or
OOS data.  The EMA20 slope uses caller-supplied closed-bar EMA20 values; MACD reuses the
deterministic replay EMA implementation.  Entry and primary EMA20-exit decisions can be
mapped to an offline bar-based simulated fill at ``Open[t+1]``.  Protective and
profit-taking exits remain deliberately undefined.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from .market_replay import calculate_ema

STRATEGY_ID = "EMA_PULLBACK_V1_MNQ"
INSTRUMENT = "MNQ"
TIMEFRAME_MINUTES = 1
EMA_PERIOD = 20
EMA_SLOPE_LOOKBACK_BARS = 3
MINIMUM_EMA_SLOPE_POINTS_PER_BAR = Decimal("0.0")
MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9
MACD_LINE_MA_TYPE = "EMA"
MACD_SIGNAL_LINE_MA_TYPE = "EMA"
MACD_CROSS_VALIDITY_BARS = 1
MACD_REQUIRED_CLOSED_BARS = MACD_SLOW_PERIOD + MACD_SIGNAL_PERIOD
EMA_SEED_CONVENTION = "FIRST_CLOSE_ALPHA_2_OVER_PERIOD_PLUS_1"
MNQ_TICK_SIZE_POINTS = Decimal("0.25")
PULLBACK_LOOKBACK_BARS = 3
# The three-bar window is ordered ``t-3, t-2, t-1``.  The owner requires the
# second bar in that window, exactly ``t-2``, to meet the distance boundary.
PULLBACK_REQUIRED_TOUCH_BAR_OFFSET = 2
MAX_PULLBACK_DISTANCE_TICKS = 8
MAX_PULLBACK_DISTANCE_POINTS = Decimal("2.00")
PULLBACK_PROXIMITY_QUALIFIES = True
WICK_CROSS_EMA20_ALLOWED = True
CONFIRMATION_CLOSE_CORRECT_SIDE_REQUIRED = True
EMA_SLOPE_REQUIRED = True
MACD_CROSS_REQUIRED = True
SIGNAL_DECISION_ON_CLOSED_BAR = True
EARLIEST_EXECUTION_BAR_OFFSET = 1
POSITION_EXIT_EQUALITY_TRIGGERS_EXIT = False
POSITION_EXIT_WICK_ONLY_TRIGGERS_EXIT = False
EXECUTION_SIGNAL_TIME = "CLOSE_T"
EXECUTION_PRICE_SOURCE = "OPEN_T_PLUS_1"
BAR_BASED_EXECUTION_MODEL = True
SLIPPAGE_MODELED = False
BID_ASK_SPREAD_MODELED = False
LATENCY_MODELED = False
TICK_REALISTIC_FILL_MODELED = False


class PullbackContractError(ValueError):
    """Raised when a pullback evaluation would require an implicit assumption."""


class PullbackSide(StrEnum):
    """Direction being evaluated by the fixed pullback predicate."""

    LONG = "LONG"
    SHORT = "SHORT"


class MACDStatus(StrEnum):
    """Availability of the deterministic MACD values at confirmation."""

    READY = "READY"
    INSUFFICIENT_WARMUP = "INSUFFICIENT_WARMUP"


class EntrySignal(StrEnum):
    """Non-executable strategy signal emitted by the assembled predicates."""

    LONG = "LONG"
    SHORT = "SHORT"
    NONE = "NONE"


class PositionExitAction(StrEnum):
    """Non-executable action produced by the primary EMA20 exit predicate."""

    EXIT_LONG = "EXIT_LONG"
    EXIT_SHORT = "EXIT_SHORT"
    HOLD = "HOLD"


class SimulatedOrderPurpose(StrEnum):
    """Purpose of an offline bar-based simulated order."""

    ENTRY = "ENTRY"
    EXIT = "EXIT"


class SimulatedOrderType(StrEnum):
    """Order type supported by the initial deterministic execution model."""

    MARKET = "MARKET"


class SimulatedExecutionStatus(StrEnum):
    """Terminal status of one offline bar-based execution attempt."""

    FILLED = "FILLED"
    EXPIRED_NO_EXECUTION = "EXPIRED_NO_EXECUTION"


@dataclass(frozen=True)
class ClosedBarEMA20:
    """Closed-bar values available at one causal sequence index.

    ``ema20`` is the EMA20 value computed at this bar's close.  Decimal values keep
    the inclusive eight-tick boundary deterministic and free from float drift.
    """

    sequence: int
    low: Decimal
    high: Decimal
    close: Decimal
    ema20: Decimal

    def __post_init__(self) -> None:
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int):
            raise PullbackContractError("sequence must be an integer")
        if self.sequence < 0:
            raise PullbackContractError("sequence must be non-negative")
        for field_name in ("low", "high", "close", "ema20"):
            value = getattr(self, field_name)
            if not isinstance(value, Decimal) or not value.is_finite():
                raise PullbackContractError(f"{field_name} must be a finite Decimal")
            if value < 0:
                raise PullbackContractError(f"{field_name} must be non-negative")
        if self.low > self.high:
            raise PullbackContractError("low must be less than or equal to high")
        if not self.low <= self.close <= self.high:
            raise PullbackContractError("close must be inside the closed bar range")


@dataclass(frozen=True)
class PullbackPredicateResult:
    """Result of the frozen pullback plus confirmation-close predicate only."""

    side: PullbackSide
    pullback_confirmation_qualifies: bool
    pullback_found: bool
    confirmation_close_correct_side: bool
    minimum_distance_points: Decimal
    minimum_distance_ticks: Decimal
    required_touch_distance_points: Decimal
    required_touch_distance_ticks: Decimal
    qualifying_bar_sequence: int | None
    confirmation_bar_sequence: int


@dataclass(frozen=True)
class EMA20SlopeResult:
    """Result of the frozen causal EMA20 slope predicate only."""

    side: PullbackSide
    ema20_slope_qualifies: bool
    slope_points_per_bar: Decimal
    lookback_bar_sequence: int
    confirmation_bar_sequence: int


@dataclass(frozen=True)
class MACDCrossResult:
    """MACD cross result at one explicit closed confirmation bar."""

    side: PullbackSide
    status: MACDStatus
    signal: EntrySignal
    macd_cross_qualifies: bool
    previous_macd_line: Decimal | None
    previous_signal_line: Decimal | None
    current_macd_line: Decimal | None
    current_signal_line: Decimal | None
    previous_bar_sequence: int | None
    confirmation_bar_sequence: int
    observed_closed_bars: int
    required_closed_bars: int = MACD_REQUIRED_CLOSED_BARS


@dataclass(frozen=True)
class EMAPullbackEntrySignalResult:
    """Fail-closed assembly of pullback, EMA20 slope and MACD predicates."""

    side: PullbackSide
    signal: EntrySignal
    entry_signal_qualifies: bool
    pullback_confirmation_qualifies: bool
    ema20_slope_qualifies: bool
    macd_cross_qualifies: bool
    macd_status: MACDStatus
    confirmation_bar_sequence: int


@dataclass(frozen=True)
class EMA20PositionExitResult:
    """Result of the strict close-relative-to-EMA20 position exit predicate."""

    position_side: PullbackSide
    action: PositionExitAction
    exit_qualifies: bool
    decision_bar_sequence: int
    earliest_execution_bar_sequence: int
    same_bar_execution_allowed: bool = False


@dataclass(frozen=True)
class NextBarOpen:
    """Open price observed for one candidate execution bar."""

    sequence: int
    open: Decimal

    def __post_init__(self) -> None:
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int):
            raise PullbackContractError("execution bar sequence must be an integer")
        if self.sequence < 0:
            raise PullbackContractError("execution bar sequence must be non-negative")
        if not isinstance(self.open, Decimal) or not self.open.is_finite() or self.open < 0:
            raise PullbackContractError("execution bar open must be a finite non-negative Decimal")


@dataclass(frozen=True)
class NextBarExecutionResult:
    """Deterministic result of one offline next-bar MARKET execution attempt."""

    purpose: SimulatedOrderPurpose
    side: PullbackSide
    order_type: SimulatedOrderType
    status: SimulatedExecutionStatus
    decision_bar_sequence: int
    execution_bar_sequence: int | None
    execution_price: Decimal | None
    position_opened: bool
    position_closed: bool
    signal_time: str = EXECUTION_SIGNAL_TIME
    execution_price_source: str = EXECUTION_PRICE_SOURCE
    same_bar_execution_allowed: bool = False


def distance_from_bar_range_to_ema20(bar: ClosedBarEMA20) -> Decimal:
    """Return the non-negative distance from a closed bar's full range to EMA20.

    A range that touches or crosses EMA20 has zero distance.  This is the exact
    implementation of ``wick_cross_ema20 = ALLOWED``.
    """
    if bar.low <= bar.ema20 <= bar.high:
        return Decimal(0)
    return min(abs(bar.low - bar.ema20), abs(bar.high - bar.ema20))


def evaluate_pullback_confirmation(
    *,
    side: PullbackSide,
    preceding_bars: Sequence[ClosedBarEMA20],
    confirmation_bar: ClosedBarEMA20,
) -> PullbackPredicateResult:
    """Evaluate the owner-defined pullback window and strict confirmation close.

    Exactly the three immediately preceding closed bars are accepted.  The second one,
    exactly ``t-2``, must touch/cross its own EMA20 or place its closed range no more
    than eight MNQ ticks away.  The confirmation bar is excluded from the pullback
    search.  No future bar is accepted by the sequence check, and this function does
    not expose execution at the confirmation close.

    This function deliberately evaluates only its own component.  The assembled entry
    evaluator separately requires the frozen EMA20 slope and MACD predicates.
    """
    if not isinstance(side, PullbackSide):
        raise PullbackContractError("side must be explicitly LONG or SHORT")

    bars = tuple(preceding_bars)
    if len(bars) != PULLBACK_LOOKBACK_BARS:
        raise PullbackContractError(
            f"exactly {PULLBACK_LOOKBACK_BARS} preceding closed bars are required"
        )
    expected_sequences = tuple(
        range(
            confirmation_bar.sequence - PULLBACK_LOOKBACK_BARS,
            confirmation_bar.sequence,
        )
    )
    actual_sequences = tuple(bar.sequence for bar in bars)
    if actual_sequences != expected_sequences:
        raise PullbackContractError(
            "preceding bars must be the three causal bars immediately before confirmation"
        )

    distances = tuple(distance_from_bar_range_to_ema20(bar) for bar in bars)
    minimum_distance = min(distances)
    required_touch_sequence = confirmation_bar.sequence - PULLBACK_REQUIRED_TOUCH_BAR_OFFSET
    required_touch_index = actual_sequences.index(required_touch_sequence)
    required_touch_distance = distances[required_touch_index]
    pullback_found = required_touch_distance <= MAX_PULLBACK_DISTANCE_POINTS
    close_correct = (
        confirmation_bar.close > confirmation_bar.ema20
        if side is PullbackSide.LONG
        else confirmation_bar.close < confirmation_bar.ema20
    )

    return PullbackPredicateResult(
        side=side,
        pullback_confirmation_qualifies=pullback_found and close_correct,
        pullback_found=pullback_found,
        confirmation_close_correct_side=close_correct,
        minimum_distance_points=minimum_distance,
        minimum_distance_ticks=minimum_distance / MNQ_TICK_SIZE_POINTS,
        required_touch_distance_points=required_touch_distance,
        required_touch_distance_ticks=required_touch_distance / MNQ_TICK_SIZE_POINTS,
        qualifying_bar_sequence=(required_touch_sequence if pullback_found else None),
        confirmation_bar_sequence=confirmation_bar.sequence,
    )


def evaluate_ema20_slope(
    *,
    side: PullbackSide,
    lookback_bar: ClosedBarEMA20,
    confirmation_bar: ClosedBarEMA20,
) -> EMA20SlopeResult:
    """Evaluate the owner-defined EMA20 slope at a closed confirmation bar.

    The fixed formula is ``(EMA20[t] - EMA20[t-3]) / 3``.  Only the two
    caller-supplied, already-closed bars participate in the calculation.  Their sequence
    indices must prove that exact causal relationship; missing warmup or any other gap
    fails closed.  Zero/equality never qualifies either direction.
    """
    if not isinstance(side, PullbackSide):
        raise PullbackContractError("side must be explicitly LONG or SHORT")
    if confirmation_bar.sequence < EMA_SLOPE_LOOKBACK_BARS:
        raise PullbackContractError(
            f"at least {EMA_SLOPE_LOOKBACK_BARS} closed warmup bars are required"
        )

    expected_lookback_sequence = confirmation_bar.sequence - EMA_SLOPE_LOOKBACK_BARS
    if lookback_bar.sequence != expected_lookback_sequence:
        raise PullbackContractError("lookback bar must be the causal closed bar exactly t-3")

    slope = (confirmation_bar.ema20 - lookback_bar.ema20) / Decimal(EMA_SLOPE_LOOKBACK_BARS)
    qualifies = (
        slope > MINIMUM_EMA_SLOPE_POINTS_PER_BAR
        if side is PullbackSide.LONG
        else slope < -MINIMUM_EMA_SLOPE_POINTS_PER_BAR
    )
    return EMA20SlopeResult(
        side=side,
        ema20_slope_qualifies=qualifies,
        slope_points_per_bar=slope,
        lookback_bar_sequence=lookback_bar.sequence,
        confirmation_bar_sequence=confirmation_bar.sequence,
    )


def evaluate_macd_confirmation(
    *,
    side: PullbackSide,
    closed_bars: Sequence[ClosedBarEMA20],
    confirmation_bar_sequence: int,
) -> MACDCrossResult:
    """Calculate and evaluate the fixed MACD cross on one closed bar.

    EMA12, EMA26 and the EMA9 signal line reuse the public deterministic replay
    implementation, including its first-close seed and ``alpha=2/(period+1)``.  Values
    after ``confirmation_bar_sequence`` are deliberately ignored.  The signal-line
    warmup plus the prior point needed for a cross require 35 causal closed bars.
    """
    if not isinstance(side, PullbackSide):
        raise PullbackContractError("side must be explicitly LONG or SHORT")
    if (
        isinstance(confirmation_bar_sequence, bool)
        or not isinstance(confirmation_bar_sequence, int)
        or confirmation_bar_sequence < 0
    ):
        raise PullbackContractError("confirmation_bar_sequence must be a non-negative integer")

    causal_bars = tuple(bar for bar in closed_bars if bar.sequence <= confirmation_bar_sequence)
    if not causal_bars or causal_bars[-1].sequence != confirmation_bar_sequence:
        raise PullbackContractError("closed bars must contain the confirmation bar")
    actual_sequences = tuple(bar.sequence for bar in causal_bars)
    expected_sequences = tuple(range(causal_bars[0].sequence, confirmation_bar_sequence + 1))
    if actual_sequences != expected_sequences:
        raise PullbackContractError(
            "closed MACD bars through confirmation must be ordered and contiguous"
        )

    observed = len(causal_bars)
    if observed < MACD_REQUIRED_CLOSED_BARS:
        return MACDCrossResult(
            side=side,
            status=MACDStatus.INSUFFICIENT_WARMUP,
            signal=EntrySignal.NONE,
            macd_cross_qualifies=False,
            previous_macd_line=None,
            previous_signal_line=None,
            current_macd_line=None,
            current_signal_line=None,
            previous_bar_sequence=None,
            confirmation_bar_sequence=confirmation_bar_sequence,
            observed_closed_bars=observed,
        )

    closes = [float(bar.close) for bar in causal_bars]
    if any(not math.isfinite(close) for close in closes):
        raise PullbackContractError("closed-bar values exceed finite EMA precision")
    fast_ema = calculate_ema(closes, MACD_FAST_PERIOD)
    slow_ema = calculate_ema(closes, MACD_SLOW_PERIOD)
    first_warmed_index = MACD_SLOW_PERIOD - 1
    macd_line = [fast_ema[index] - slow_ema[index] for index in range(first_warmed_index, observed)]
    signal_line = calculate_ema(macd_line, MACD_SIGNAL_PERIOD)

    previous_macd = Decimal(str(macd_line[-2]))
    current_macd = Decimal(str(macd_line[-1]))
    previous_signal = Decimal(str(signal_line[-2]))
    current_signal = Decimal(str(signal_line[-1]))
    bullish_cross = previous_macd <= previous_signal and current_macd > current_signal
    bearish_cross = previous_macd >= previous_signal and current_macd < current_signal
    qualifies = bullish_cross if side is PullbackSide.LONG else bearish_cross
    signal = EntrySignal(side.value) if qualifies else EntrySignal.NONE

    return MACDCrossResult(
        side=side,
        status=MACDStatus.READY,
        signal=signal,
        macd_cross_qualifies=qualifies,
        previous_macd_line=previous_macd,
        previous_signal_line=previous_signal,
        current_macd_line=current_macd,
        current_signal_line=current_signal,
        previous_bar_sequence=confirmation_bar_sequence - 1,
        confirmation_bar_sequence=confirmation_bar_sequence,
        observed_closed_bars=observed,
    )


def assemble_ema_pullback_entry_signal(
    *,
    side: PullbackSide,
    pullback: PullbackPredicateResult,
    slope: EMA20SlopeResult,
    macd: MACDCrossResult,
) -> EMAPullbackEntrySignalResult:
    """Combine all mandatory V1 entry predicates without executing a trade."""
    if not isinstance(side, PullbackSide):
        raise PullbackContractError("side must be explicitly LONG or SHORT")
    if any(result_side is not side for result_side in (pullback.side, slope.side, macd.side)):
        raise PullbackContractError("all entry predicates must evaluate the same side")
    confirmation_sequences = {
        pullback.confirmation_bar_sequence,
        slope.confirmation_bar_sequence,
        macd.confirmation_bar_sequence,
    }
    if len(confirmation_sequences) != 1:
        raise PullbackContractError("all entry predicates must evaluate the same confirmation bar")

    qualifies = (
        pullback.pullback_confirmation_qualifies
        and slope.ema20_slope_qualifies
        and macd.status is MACDStatus.READY
        and macd.macd_cross_qualifies
    )
    return EMAPullbackEntrySignalResult(
        side=side,
        signal=EntrySignal(side.value) if qualifies else EntrySignal.NONE,
        entry_signal_qualifies=qualifies,
        pullback_confirmation_qualifies=pullback.pullback_confirmation_qualifies,
        ema20_slope_qualifies=slope.ema20_slope_qualifies,
        macd_cross_qualifies=macd.macd_cross_qualifies,
        macd_status=macd.status,
        confirmation_bar_sequence=confirmation_sequences.pop(),
    )


def evaluate_ema_pullback_entry_signal(
    *,
    side: PullbackSide,
    closed_bars: Sequence[ClosedBarEMA20],
    confirmation_bar_sequence: int,
) -> EMAPullbackEntrySignalResult:
    """Evaluate the assembled entry contract from one coherent closed-bar history."""
    macd = evaluate_macd_confirmation(
        side=side,
        closed_bars=closed_bars,
        confirmation_bar_sequence=confirmation_bar_sequence,
    )
    causal_bars = tuple(bar for bar in closed_bars if bar.sequence <= confirmation_bar_sequence)
    if len(causal_bars) < PULLBACK_LOOKBACK_BARS + 1:
        raise PullbackContractError(
            "assembled entry requires confirmation plus three preceding closed bars"
        )
    confirmation_bar = causal_bars[-1]
    preceding_bars = causal_bars[-(PULLBACK_LOOKBACK_BARS + 1) : -1]
    pullback = evaluate_pullback_confirmation(
        side=side,
        preceding_bars=preceding_bars,
        confirmation_bar=confirmation_bar,
    )
    slope = evaluate_ema20_slope(
        side=side,
        lookback_bar=preceding_bars[0],
        confirmation_bar=confirmation_bar,
    )
    return assemble_ema_pullback_entry_signal(
        side=side,
        pullback=pullback,
        slope=slope,
        macd=macd,
    )


def evaluate_ema20_position_exit(
    *,
    position_side: PullbackSide,
    closed_bars: Sequence[ClosedBarEMA20],
    decision_bar_sequence: int,
) -> EMA20PositionExitResult:
    """Evaluate the frozen primary exit on one explicit closed bar.

    A LONG exits only when ``Close[t] < EMA20[t]``; a SHORT exits only when
    ``Close[t] > EMA20[t]``.  Equality and wick-only crossings hold the position.
    Only the bar whose sequence is exactly ``decision_bar_sequence`` is inspected, so
    future values cannot affect the decision.  This function emits no order or price;
    execution is forbidden on ``t`` and becomes eligible no earlier than ``t+1``.
    """
    if not isinstance(position_side, PullbackSide):
        raise PullbackContractError("position_side must be explicitly LONG or SHORT")
    if (
        isinstance(decision_bar_sequence, bool)
        or not isinstance(decision_bar_sequence, int)
        or decision_bar_sequence < 0
    ):
        raise PullbackContractError("decision_bar_sequence must be a non-negative integer")

    matching_bars = tuple(bar for bar in closed_bars if bar.sequence == decision_bar_sequence)
    if len(matching_bars) != 1:
        raise PullbackContractError("closed bars must contain exactly one decision bar")
    decision_bar = matching_bars[0]

    exit_qualifies = (
        decision_bar.close < decision_bar.ema20
        if position_side is PullbackSide.LONG
        else decision_bar.close > decision_bar.ema20
    )
    action = (
        PositionExitAction(f"EXIT_{position_side.value}")
        if exit_qualifies
        else PositionExitAction.HOLD
    )
    return EMA20PositionExitResult(
        position_side=position_side,
        action=action,
        exit_qualifies=exit_qualifies,
        decision_bar_sequence=decision_bar_sequence,
        earliest_execution_bar_sequence=(decision_bar_sequence + EARLIEST_EXECUTION_BAR_OFFSET),
    )


def simulate_next_bar_market_execution(
    *,
    decision: EMAPullbackEntrySignalResult | EMA20PositionExitResult,
    decision_bar: ClosedBarEMA20,
    available_bar_opens: Sequence[NextBarOpen],
) -> NextBarExecutionResult:
    """Apply the frozen offline MARKET-at-``Open[t+1]`` execution convention.

    ``decision`` must already be a qualified entry or primary EMA20 exit formed on the
    closed ``decision_bar``.  Exactly ``t+1`` may fill the simulated MARKET order.  If
    that bar is absent, the attempt expires without inventing a price from ``Close[t]``,
    the last known price, or a later bar.  Bars after ``t+1`` are intentionally ignored,
    making their mutation irrelevant.  This function performs no broker or live action.
    """
    if isinstance(decision, EMAPullbackEntrySignalResult):
        expected_signal = EntrySignal(decision.side.value)
        if not decision.entry_signal_qualifies or decision.signal is not expected_signal:
            raise PullbackContractError("entry execution requires a qualified directional signal")
        purpose = SimulatedOrderPurpose.ENTRY
        side = decision.side
        decision_sequence = decision.confirmation_bar_sequence
    elif isinstance(decision, EMA20PositionExitResult):
        expected_action = PositionExitAction(f"EXIT_{decision.position_side.value}")
        if not decision.exit_qualifies or decision.action is not expected_action:
            raise PullbackContractError("exit execution requires a qualified directional exit")
        purpose = SimulatedOrderPurpose.EXIT
        side = decision.position_side
        decision_sequence = decision.decision_bar_sequence
    else:
        raise PullbackContractError("decision must be a qualified entry or EMA20 exit result")

    if decision_bar.sequence != decision_sequence:
        raise PullbackContractError("decision bar must match the qualified decision sequence")

    execution_bars = tuple(available_bar_opens)
    if any(not isinstance(bar, NextBarOpen) for bar in execution_bars):
        raise PullbackContractError("available execution bars must be NextBarOpen values")
    expected_execution_sequence = decision_sequence + EARLIEST_EXECUTION_BAR_OFFSET
    matching_bars = tuple(
        bar for bar in execution_bars if bar.sequence == expected_execution_sequence
    )
    if len(matching_bars) > 1:
        raise PullbackContractError("available execution bars contain duplicate t+1 values")

    if not matching_bars:
        return NextBarExecutionResult(
            purpose=purpose,
            side=side,
            order_type=SimulatedOrderType.MARKET,
            status=SimulatedExecutionStatus.EXPIRED_NO_EXECUTION,
            decision_bar_sequence=decision_sequence,
            execution_bar_sequence=None,
            execution_price=None,
            position_opened=False,
            position_closed=False,
        )

    execution_bar = matching_bars[0]
    return NextBarExecutionResult(
        purpose=purpose,
        side=side,
        order_type=SimulatedOrderType.MARKET,
        status=SimulatedExecutionStatus.FILLED,
        decision_bar_sequence=decision_sequence,
        execution_bar_sequence=execution_bar.sequence,
        execution_price=execution_bar.open,
        position_opened=purpose is SimulatedOrderPurpose.ENTRY,
        position_closed=purpose is SimulatedOrderPurpose.EXIT,
    )


__all__ = [
    "BAR_BASED_EXECUTION_MODEL",
    "BID_ASK_SPREAD_MODELED",
    "CONFIRMATION_CLOSE_CORRECT_SIDE_REQUIRED",
    "EARLIEST_EXECUTION_BAR_OFFSET",
    "EMA_PERIOD",
    "EMA_SEED_CONVENTION",
    "EMA_SLOPE_LOOKBACK_BARS",
    "EMA_SLOPE_REQUIRED",
    "EXECUTION_PRICE_SOURCE",
    "EXECUTION_SIGNAL_TIME",
    "INSTRUMENT",
    "LATENCY_MODELED",
    "MACD_CROSS_REQUIRED",
    "MACD_CROSS_VALIDITY_BARS",
    "MACD_FAST_PERIOD",
    "MACD_LINE_MA_TYPE",
    "MACD_REQUIRED_CLOSED_BARS",
    "MACD_SIGNAL_LINE_MA_TYPE",
    "MACD_SIGNAL_PERIOD",
    "MACD_SLOW_PERIOD",
    "MAX_PULLBACK_DISTANCE_POINTS",
    "MAX_PULLBACK_DISTANCE_TICKS",
    "MINIMUM_EMA_SLOPE_POINTS_PER_BAR",
    "MNQ_TICK_SIZE_POINTS",
    "POSITION_EXIT_EQUALITY_TRIGGERS_EXIT",
    "POSITION_EXIT_WICK_ONLY_TRIGGERS_EXIT",
    "PULLBACK_LOOKBACK_BARS",
    "PULLBACK_PROXIMITY_QUALIFIES",
    "PULLBACK_REQUIRED_TOUCH_BAR_OFFSET",
    "SIGNAL_DECISION_ON_CLOSED_BAR",
    "SLIPPAGE_MODELED",
    "STRATEGY_ID",
    "TICK_REALISTIC_FILL_MODELED",
    "TIMEFRAME_MINUTES",
    "WICK_CROSS_EMA20_ALLOWED",
    "ClosedBarEMA20",
    "EMA20PositionExitResult",
    "EMA20SlopeResult",
    "EMAPullbackEntrySignalResult",
    "EntrySignal",
    "MACDCrossResult",
    "MACDStatus",
    "NextBarExecutionResult",
    "NextBarOpen",
    "PositionExitAction",
    "PullbackContractError",
    "PullbackPredicateResult",
    "PullbackSide",
    "SimulatedExecutionStatus",
    "SimulatedOrderPurpose",
    "SimulatedOrderType",
    "assemble_ema_pullback_entry_signal",
    "distance_from_bar_range_to_ema20",
    "evaluate_ema20_position_exit",
    "evaluate_ema20_slope",
    "evaluate_ema_pullback_entry_signal",
    "evaluate_macd_confirmation",
    "evaluate_pullback_confirmation",
    "simulate_next_bar_market_execution",
]
