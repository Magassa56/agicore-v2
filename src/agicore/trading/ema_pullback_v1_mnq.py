"""Deterministic pullback predicate for ``EMA_PULLBACK_V1_MNQ``.

This module freezes only the strategy rules that the owner has explicitly defined.  It
does not compute EMA20, does not emit a broker-executable order, and never reads market or
OOS data.  The EMA20 slope uses caller-supplied closed-bar EMA20 values; MACD reuses the
deterministic replay EMA implementation.  Entry and primary EMA20-exit decisions can be
mapped to an offline bar-based simulated fill at ``Open[t+1]``.  The initial structural
stop is frozen from the required ``t-2`` bar.  V1 explicitly has no take-profit; exit
priority at one shared bar open is structural stop first, then a pending EMA20 exit.
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
INITIAL_STOP_SOURCE_BAR_OFFSET = 2
INITIAL_STOP_BUFFER_TICKS = 1
INITIAL_STOP_BUFFER_POINTS = MNQ_TICK_SIZE_POINTS * INITIAL_STOP_BUFFER_TICKS
INITIAL_STOP_IS_IMMUTABLE = True
GAP_THROUGH_STOP_FILLS_AT_BAR_OPEN = True
STOP_INTRABAR_SLIPPAGE_MODELED = False
TAKE_PROFIT = "NONE"
TAKE_PROFIT_ENABLED = False
TAKE_PROFIT_PRICE = None
TAKE_PROFIT_MONETARY_AMOUNT = None
TAKE_PROFIT_TICKS = None
TAKE_PROFIT_POINTS = None
TAKE_PROFIT_R_MULTIPLE = None
TAKE_PROFIT_PNL_EXIT_ENABLED = False
STRUCTURAL_STOP_FIRST = True
EXIT_PRIORITY = ("STRUCTURAL_STOP", "EMA20_EXIT")


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
    REJECT_ENTRY = "REJECT_ENTRY"


class InitialStopTriggerStatus(StrEnum):
    """State of the immutable structural stop after one bar evaluation."""

    NOT_TRIGGERED = "NOT_TRIGGERED"
    STOP_TRIGGERED = "STOP_TRIGGERED"


class InitialStopFillSource(StrEnum):
    """Price source used by the deterministic bar-based stop convention."""

    NONE = "NONE"
    STOP_PRICE = "STOP_PRICE"
    BAR_OPEN_GAP = "BAR_OPEN_GAP"


class PositionExitReason(StrEnum):
    """Mutually exclusive reason that closed one V1 position."""

    STRUCTURAL_STOP = "STRUCTURAL_STOP"
    EMA20_EXIT = "EMA20_EXIT"


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
class TakeProfitEvaluationResult:
    """Explicit V1 result proving that no profit target can request an exit."""

    position_side: PullbackSide
    action: PositionExitAction = PositionExitAction.HOLD
    exit_qualifies: bool = False
    take_profit: str = TAKE_PROFIT
    take_profit_enabled: bool = TAKE_PROFIT_ENABLED
    take_profit_price: None = TAKE_PROFIT_PRICE
    monetary_amount: None = TAKE_PROFIT_MONETARY_AMOUNT
    ticks: None = TAKE_PROFIT_TICKS
    points: None = TAKE_PROFIT_POINTS
    risk_multiple: None = TAKE_PROFIT_R_MULTIPLE
    pnl_exit_enabled: bool = TAKE_PROFIT_PNL_EXIT_ENABLED
    position_closed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.position_side, PullbackSide):
            raise PullbackContractError("position_side must be explicitly LONG or SHORT")
        if (
            self.action is not PositionExitAction.HOLD
            or self.exit_qualifies is not False
            or self.take_profit != TAKE_PROFIT
            or self.take_profit_enabled is not False
            or self.take_profit_price is not None
            or self.monetary_amount is not None
            or self.ticks is not None
            or self.points is not None
            or self.risk_multiple is not None
            or self.pnl_exit_enabled is not False
            or self.position_closed is not False
        ):
            raise PullbackContractError("V1 take-profit contract must remain explicitly disabled")


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


@dataclass(frozen=True)
class InitialStructuralStop:
    """Immutable stop derived causally from the required closed ``t-2`` bar."""

    side: PullbackSide
    stop_price: Decimal
    source_bar_sequence: int
    decision_bar_sequence: int
    buffer_ticks: int = INITIAL_STOP_BUFFER_TICKS
    buffer_points: Decimal = INITIAL_STOP_BUFFER_POINTS
    immutable: bool = INITIAL_STOP_IS_IMMUTABLE

    def __post_init__(self) -> None:
        if not isinstance(self.side, PullbackSide):
            raise PullbackContractError("initial stop side must be explicitly LONG or SHORT")
        if any(
            isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0
            for sequence in (self.source_bar_sequence, self.decision_bar_sequence)
        ):
            raise PullbackContractError("initial stop sequences must be non-negative integers")
        if self.source_bar_sequence != self.decision_bar_sequence - INITIAL_STOP_SOURCE_BAR_OFFSET:
            raise PullbackContractError("initial stop source must be the causal closed bar t-2")
        if (
            not isinstance(self.stop_price, Decimal)
            or not self.stop_price.is_finite()
            or self.stop_price < 0
        ):
            raise PullbackContractError("initial stop price must be a finite non-negative Decimal")
        if self.buffer_ticks != INITIAL_STOP_BUFFER_TICKS:
            raise PullbackContractError("initial stop buffer must remain exactly one tick")
        if self.buffer_points != INITIAL_STOP_BUFFER_POINTS:
            raise PullbackContractError("initial stop buffer must remain exactly 0.25 point")
        if self.immutable is not True:
            raise PullbackContractError("initial structural stop must be immutable")


@dataclass(frozen=True)
class ProtectedEntryExecutionResult:
    """Final position-creation result after validating the precomputed initial stop."""

    side: PullbackSide
    order_type: SimulatedOrderType
    status: SimulatedExecutionStatus
    decision_bar_sequence: int
    execution_bar_sequence: int | None
    candidate_entry_price: Decimal | None
    entry_price: Decimal | None
    initial_stop: InitialStructuralStop
    position_opened: bool


@dataclass(frozen=True)
class StopEvaluationBar:
    """OHLC subset needed to simulate an immutable stop on one bar."""

    sequence: int
    open: Decimal
    low: Decimal
    high: Decimal

    def __post_init__(self) -> None:
        if (
            isinstance(self.sequence, bool)
            or not isinstance(self.sequence, int)
            or self.sequence < 0
        ):
            raise PullbackContractError("stop evaluation sequence must be a non-negative integer")
        for field_name in ("open", "low", "high"):
            value = getattr(self, field_name)
            if not isinstance(value, Decimal) or not value.is_finite() or value < 0:
                raise PullbackContractError(
                    f"stop evaluation {field_name} must be a finite non-negative Decimal"
                )
        if self.low > self.high:
            raise PullbackContractError("stop evaluation low must not exceed high")
        if not self.low <= self.open <= self.high:
            raise PullbackContractError("stop evaluation open must be inside the bar range")


@dataclass(frozen=True)
class InitialStopBarExecutionResult:
    """Deterministic outcome of evaluating the immutable stop on one bar."""

    side: PullbackSide
    status: InitialStopTriggerStatus
    fill_source: InitialStopFillSource
    stop_price: Decimal
    evaluated_bar_sequence: int
    fill_price: Decimal | None
    position_closed: bool


@dataclass(frozen=True)
class ExitPriorityExecutionResult:
    """Single-fill result of arbitrating stop and pending EMA20 exit at one open."""

    side: PullbackSide
    exit_reason: PositionExitReason
    execution_bar_sequence: int
    fill_price: Decimal
    structural_stop_executed: bool
    ema20_exit_executed: bool
    cancel_pending_ema20_exit: bool
    cancel_structural_stop: bool
    fill_count: int = 1
    position_close_count: int = 1
    position_closed: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.side, PullbackSide):
            raise PullbackContractError("exit priority side must be explicitly LONG or SHORT")
        if not isinstance(self.exit_reason, PositionExitReason):
            raise PullbackContractError("exit priority requires one explicit exit reason")
        if (
            isinstance(self.execution_bar_sequence, bool)
            or not isinstance(self.execution_bar_sequence, int)
            or self.execution_bar_sequence < 0
        ):
            raise PullbackContractError("exit priority sequence must be a non-negative integer")
        if (
            not isinstance(self.fill_price, Decimal)
            or not self.fill_price.is_finite()
            or self.fill_price < 0
        ):
            raise PullbackContractError("exit priority fill must be a finite non-negative Decimal")
        boolean_flags = (
            self.structural_stop_executed,
            self.ema20_exit_executed,
            self.cancel_pending_ema20_exit,
            self.cancel_structural_stop,
        )
        if any(type(flag) is not bool for flag in boolean_flags):
            raise PullbackContractError(
                "exit priority execution and cancellation flags must be bool"
            )
        if (
            type(self.fill_count) is not int
            or self.fill_count != 1
            or type(self.position_close_count) is not int
            or self.position_close_count != 1
            or self.position_closed is not True
        ):
            raise PullbackContractError("exit priority must produce exactly one fill and one close")
        executed_count = int(self.structural_stop_executed) + int(self.ema20_exit_executed)
        cancellation_count = int(self.cancel_pending_ema20_exit) + int(self.cancel_structural_stop)
        if executed_count != 1 or cancellation_count != 1:
            raise PullbackContractError("exit priority must execute one exit and cancel the other")
        if self.exit_reason is PositionExitReason.STRUCTURAL_STOP:
            valid = (
                self.structural_stop_executed is True
                and self.ema20_exit_executed is False
                and self.cancel_pending_ema20_exit is True
                and self.cancel_structural_stop is False
            )
        else:
            valid = (
                self.structural_stop_executed is False
                and self.ema20_exit_executed is True
                and self.cancel_pending_ema20_exit is False
                and self.cancel_structural_stop is True
            )
        if not valid:
            raise PullbackContractError("exit reason, execution and cancellation must be coherent")


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


def evaluate_disabled_take_profit(
    *,
    position_side: PullbackSide,
    observed_market_price: Decimal,
    unrealized_pnl: Decimal,
) -> TakeProfitEvaluationResult:
    """Return HOLD regardless of price or PnL because V1 has no take-profit.

    The observations are accepted only to make the fail-closed rule directly testable:
    no favorable price, monetary gain, tick/point distance, or implicit risk multiple can
    produce a take-profit exit.  This function emits no order and reads no future value.
    """
    if not isinstance(position_side, PullbackSide):
        raise PullbackContractError("position_side must be explicitly LONG or SHORT")
    if (
        not isinstance(observed_market_price, Decimal)
        or not observed_market_price.is_finite()
        or observed_market_price < 0
    ):
        raise PullbackContractError("observed_market_price must be a finite non-negative Decimal")
    if not isinstance(unrealized_pnl, Decimal) or not unrealized_pnl.is_finite():
        raise PullbackContractError("unrealized_pnl must be a finite Decimal")
    return TakeProfitEvaluationResult(position_side=position_side)


def construct_initial_structural_stop(
    *,
    decision: EMAPullbackEntrySignalResult,
    decision_bar: ClosedBarEMA20,
    required_touch_bar: ClosedBarEMA20,
) -> InitialStructuralStop:
    """Freeze the one-tick-buffered structural stop at the closed confirmation bar.

    The source must be exactly the already-closed ``t-2`` bar associated with a qualified
    entry signal on ``t``.  No value after ``t`` is accepted or needed.
    """
    if not isinstance(decision, EMAPullbackEntrySignalResult):
        raise PullbackContractError("initial stop requires an EMA pullback entry decision")
    expected_signal = EntrySignal(decision.side.value)
    if not decision.entry_signal_qualifies or decision.signal is not expected_signal:
        raise PullbackContractError("initial stop requires a qualified directional entry signal")
    if not isinstance(decision_bar, ClosedBarEMA20) or not isinstance(
        required_touch_bar, ClosedBarEMA20
    ):
        raise PullbackContractError("initial stop requires closed decision and t-2 bars")
    if decision_bar.sequence != decision.confirmation_bar_sequence:
        raise PullbackContractError("initial stop decision bar must match the entry signal")
    expected_source_sequence = decision_bar.sequence - INITIAL_STOP_SOURCE_BAR_OFFSET
    if required_touch_bar.sequence != expected_source_sequence:
        raise PullbackContractError("initial stop source must be the causal closed bar t-2")

    stop_price = (
        required_touch_bar.low - INITIAL_STOP_BUFFER_POINTS
        if decision.side is PullbackSide.LONG
        else required_touch_bar.high + INITIAL_STOP_BUFFER_POINTS
    )
    if stop_price < 0:
        raise PullbackContractError("initial structural stop cannot be negative")
    return InitialStructuralStop(
        side=decision.side,
        stop_price=stop_price,
        source_bar_sequence=required_touch_bar.sequence,
        decision_bar_sequence=decision_bar.sequence,
    )


def _select_exact_next_bar(
    *,
    decision_sequence: int,
    available_bar_opens: Sequence[NextBarOpen],
) -> NextBarOpen | None:
    execution_bars = tuple(available_bar_opens)
    if any(not isinstance(bar, NextBarOpen) for bar in execution_bars):
        raise PullbackContractError("available execution bars must be NextBarOpen values")
    expected_execution_sequence = decision_sequence + EARLIEST_EXECUTION_BAR_OFFSET
    matching_bars = tuple(
        bar for bar in execution_bars if bar.sequence == expected_execution_sequence
    )
    if len(matching_bars) > 1:
        raise PullbackContractError("available execution bars contain duplicate t+1 values")
    return matching_bars[0] if matching_bars else None


def simulate_entry_with_initial_structural_stop(
    *,
    decision: EMAPullbackEntrySignalResult,
    decision_bar: ClosedBarEMA20,
    required_touch_bar: ClosedBarEMA20,
    available_bar_opens: Sequence[NextBarOpen],
) -> ProtectedEntryExecutionResult:
    """Create a position only when ``Open[t+1]`` is valid relative to the frozen stop.

    The stop is constructed before inspecting the candidate entry open.  A missing
    ``t+1`` expires without execution.  A LONG stop at or above the candidate entry, or
    a SHORT stop at or below it, rejects the entry rather than opening an invalid position.
    """
    initial_stop = construct_initial_structural_stop(
        decision=decision,
        decision_bar=decision_bar,
        required_touch_bar=required_touch_bar,
    )
    execution_bar = _select_exact_next_bar(
        decision_sequence=decision.confirmation_bar_sequence,
        available_bar_opens=available_bar_opens,
    )
    if execution_bar is None:
        return ProtectedEntryExecutionResult(
            side=decision.side,
            order_type=SimulatedOrderType.MARKET,
            status=SimulatedExecutionStatus.EXPIRED_NO_EXECUTION,
            decision_bar_sequence=decision.confirmation_bar_sequence,
            execution_bar_sequence=None,
            candidate_entry_price=None,
            entry_price=None,
            initial_stop=initial_stop,
            position_opened=False,
        )

    invalid_stop = (
        initial_stop.stop_price >= execution_bar.open
        if decision.side is PullbackSide.LONG
        else initial_stop.stop_price <= execution_bar.open
    )
    return ProtectedEntryExecutionResult(
        side=decision.side,
        order_type=SimulatedOrderType.MARKET,
        status=(
            SimulatedExecutionStatus.REJECT_ENTRY
            if invalid_stop
            else SimulatedExecutionStatus.FILLED
        ),
        decision_bar_sequence=decision.confirmation_bar_sequence,
        execution_bar_sequence=execution_bar.sequence,
        candidate_entry_price=execution_bar.open,
        entry_price=None if invalid_stop else execution_bar.open,
        initial_stop=initial_stop,
        position_opened=not invalid_stop,
    )


def initial_stop_triggered_by_market_price(
    *,
    initial_stop: InitialStructuralStop,
    market_price: Decimal,
) -> bool:
    """Evaluate the owner-defined inclusive stop trigger at one observed market price."""
    if not isinstance(initial_stop, InitialStructuralStop):
        raise PullbackContractError("initial_stop must be an InitialStructuralStop")
    if not isinstance(market_price, Decimal) or not market_price.is_finite() or market_price < 0:
        raise PullbackContractError("market_price must be a finite non-negative Decimal")
    return (
        market_price <= initial_stop.stop_price
        if initial_stop.side is PullbackSide.LONG
        else market_price >= initial_stop.stop_price
    )


def evaluate_initial_stop_on_bar(
    *,
    position: ProtectedEntryExecutionResult,
    bar: StopEvaluationBar,
) -> InitialStopBarExecutionResult:
    """Evaluate one active immutable stop with the frozen bar-based fill convention.

    A strict gap through the stop fills at the bar open.  Otherwise an inclusive intrabar
    touch fills at the stop price.  This deterministic baseline does not model slippage.
    """
    if not isinstance(position, ProtectedEntryExecutionResult):
        raise PullbackContractError("stop evaluation requires a protected entry result")
    if position.status is not SimulatedExecutionStatus.FILLED or not position.position_opened:
        raise PullbackContractError("stop evaluation requires an opened protected position")
    if not isinstance(bar, StopEvaluationBar):
        raise PullbackContractError("bar must be a StopEvaluationBar")
    if position.execution_bar_sequence is None or bar.sequence < position.execution_bar_sequence:
        raise PullbackContractError("stop evaluation bar cannot precede position creation")

    stop = position.initial_stop
    gap_through = (
        bar.open < stop.stop_price if stop.side is PullbackSide.LONG else bar.open > stop.stop_price
    )
    if gap_through:
        return InitialStopBarExecutionResult(
            side=stop.side,
            status=InitialStopTriggerStatus.STOP_TRIGGERED,
            fill_source=InitialStopFillSource.BAR_OPEN_GAP,
            stop_price=stop.stop_price,
            evaluated_bar_sequence=bar.sequence,
            fill_price=bar.open,
            position_closed=True,
        )

    trigger_price = bar.low if stop.side is PullbackSide.LONG else bar.high
    if initial_stop_triggered_by_market_price(
        initial_stop=stop,
        market_price=trigger_price,
    ):
        return InitialStopBarExecutionResult(
            side=stop.side,
            status=InitialStopTriggerStatus.STOP_TRIGGERED,
            fill_source=InitialStopFillSource.STOP_PRICE,
            stop_price=stop.stop_price,
            evaluated_bar_sequence=bar.sequence,
            fill_price=stop.stop_price,
            position_closed=True,
        )

    return InitialStopBarExecutionResult(
        side=stop.side,
        status=InitialStopTriggerStatus.NOT_TRIGGERED,
        fill_source=InitialStopFillSource.NONE,
        stop_price=stop.stop_price,
        evaluated_bar_sequence=bar.sequence,
        fill_price=None,
        position_closed=False,
    )


def arbitrate_exit_at_open(
    *,
    position: ProtectedEntryExecutionResult,
    pending_ema20_exit: EMA20PositionExitResult,
    execution_bar: NextBarOpen,
) -> ExitPriorityExecutionResult:
    """Execute exactly one exit at ``Open[k]`` using structural-stop-first priority.

    A stop inclusively triggered by ``Open[k]`` wins and cancels the pending EMA20 exit.
    Otherwise the already-qualified EMA20 exit fills at the same open and cancels the
    structural stop.  No intrabar value after the open participates in this arbitration.
    """
    if not isinstance(position, ProtectedEntryExecutionResult):
        raise PullbackContractError("exit priority requires a protected entry result")
    if (
        position.status is not SimulatedExecutionStatus.FILLED
        or position.position_opened is not True
    ):
        raise PullbackContractError("exit priority requires an opened protected position")
    if not isinstance(position.side, PullbackSide):
        raise PullbackContractError("position side must be explicitly LONG or SHORT")
    if not isinstance(position.initial_stop, InitialStructuralStop):
        raise PullbackContractError("exit priority requires an immutable structural stop")
    if not isinstance(pending_ema20_exit, EMA20PositionExitResult):
        raise PullbackContractError("exit priority requires a pending EMA20 exit")
    if not isinstance(pending_ema20_exit.position_side, PullbackSide):
        raise PullbackContractError("pending EMA20 exit side must be explicitly LONG or SHORT")
    expected_action = PositionExitAction(f"EXIT_{pending_ema20_exit.position_side.value}")
    if (
        pending_ema20_exit.exit_qualifies is not True
        or pending_ema20_exit.action is not expected_action
        or pending_ema20_exit.same_bar_execution_allowed is not False
    ):
        raise PullbackContractError("exit priority requires a qualified next-bar EMA20 exit")
    if position.side is not pending_ema20_exit.position_side:
        raise PullbackContractError("position and pending EMA20 exit sides must match")
    if position.initial_stop.side is not position.side:
        raise PullbackContractError("position and structural stop sides must match")
    if (
        position.execution_bar_sequence is None
        or pending_ema20_exit.decision_bar_sequence < position.execution_bar_sequence
    ):
        raise PullbackContractError("pending EMA20 exit cannot precede position creation")
    if not isinstance(execution_bar, NextBarOpen):
        raise PullbackContractError("exit priority execution bar must be a NextBarOpen")
    expected_sequence = pending_ema20_exit.decision_bar_sequence + EARLIEST_EXECUTION_BAR_OFFSET
    if (
        pending_ema20_exit.earliest_execution_bar_sequence != expected_sequence
        or execution_bar.sequence != expected_sequence
    ):
        raise PullbackContractError("pending EMA20 exit must execute on its exact next bar")

    stop_triggered_at_open = initial_stop_triggered_by_market_price(
        initial_stop=position.initial_stop,
        market_price=execution_bar.open,
    )
    if stop_triggered_at_open:
        return ExitPriorityExecutionResult(
            side=position.side,
            exit_reason=PositionExitReason.STRUCTURAL_STOP,
            execution_bar_sequence=execution_bar.sequence,
            fill_price=execution_bar.open,
            structural_stop_executed=True,
            ema20_exit_executed=False,
            cancel_pending_ema20_exit=True,
            cancel_structural_stop=False,
        )
    return ExitPriorityExecutionResult(
        side=position.side,
        exit_reason=PositionExitReason.EMA20_EXIT,
        execution_bar_sequence=execution_bar.sequence,
        fill_price=execution_bar.open,
        structural_stop_executed=False,
        ema20_exit_executed=True,
        cancel_pending_ema20_exit=False,
        cancel_structural_stop=True,
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

    execution_bar = _select_exact_next_bar(
        decision_sequence=decision_sequence,
        available_bar_opens=available_bar_opens,
    )
    if execution_bar is None:
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
    "EXIT_PRIORITY",
    "GAP_THROUGH_STOP_FILLS_AT_BAR_OPEN",
    "INITIAL_STOP_BUFFER_POINTS",
    "INITIAL_STOP_BUFFER_TICKS",
    "INITIAL_STOP_IS_IMMUTABLE",
    "INITIAL_STOP_SOURCE_BAR_OFFSET",
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
    "STOP_INTRABAR_SLIPPAGE_MODELED",
    "STRATEGY_ID",
    "STRUCTURAL_STOP_FIRST",
    "TAKE_PROFIT",
    "TAKE_PROFIT_ENABLED",
    "TAKE_PROFIT_MONETARY_AMOUNT",
    "TAKE_PROFIT_PNL_EXIT_ENABLED",
    "TAKE_PROFIT_POINTS",
    "TAKE_PROFIT_PRICE",
    "TAKE_PROFIT_R_MULTIPLE",
    "TAKE_PROFIT_TICKS",
    "TICK_REALISTIC_FILL_MODELED",
    "TIMEFRAME_MINUTES",
    "WICK_CROSS_EMA20_ALLOWED",
    "ClosedBarEMA20",
    "EMA20PositionExitResult",
    "EMA20SlopeResult",
    "EMAPullbackEntrySignalResult",
    "EntrySignal",
    "ExitPriorityExecutionResult",
    "InitialStopBarExecutionResult",
    "InitialStopFillSource",
    "InitialStopTriggerStatus",
    "InitialStructuralStop",
    "MACDCrossResult",
    "MACDStatus",
    "NextBarExecutionResult",
    "NextBarOpen",
    "PositionExitAction",
    "PositionExitReason",
    "ProtectedEntryExecutionResult",
    "PullbackContractError",
    "PullbackPredicateResult",
    "PullbackSide",
    "SimulatedExecutionStatus",
    "SimulatedOrderPurpose",
    "SimulatedOrderType",
    "StopEvaluationBar",
    "TakeProfitEvaluationResult",
    "arbitrate_exit_at_open",
    "assemble_ema_pullback_entry_signal",
    "construct_initial_structural_stop",
    "distance_from_bar_range_to_ema20",
    "evaluate_disabled_take_profit",
    "evaluate_ema20_position_exit",
    "evaluate_ema20_slope",
    "evaluate_ema_pullback_entry_signal",
    "evaluate_initial_stop_on_bar",
    "evaluate_macd_confirmation",
    "evaluate_pullback_confirmation",
    "initial_stop_triggered_by_market_price",
    "simulate_entry_with_initial_structural_stop",
    "simulate_next_bar_market_execution",
]
