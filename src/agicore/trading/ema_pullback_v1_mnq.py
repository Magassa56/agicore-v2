"""Deterministic pullback predicate for ``EMA_PULLBACK_V1_MNQ``.

This module freezes only the strategy rules that the owner has explicitly defined.  It
does not compute EMA20, does not emit a broker-executable order, and never reads market or
OOS data.  The EMA20 slope uses caller-supplied closed-bar EMA20 values; MACD reuses the
deterministic replay EMA implementation.  Entry and primary EMA20-exit decisions can be
mapped to an offline bar-based simulated fill at ``Open[t+1]``.  The initial structural
stop is frozen from the required ``t-2`` bar.  V1 explicitly has no take-profit,
breakeven, or trailing stop; exit priority at one shared bar open is structural stop
first, then a pending EMA20 exit.  V1 adds no strategy-level session filter: the
upstream ``CME US Index Futures ETH`` source calendar remains mandatory, and every
closed valid source bar keeps entries and both existing exits eligible.
While a position is open at a close, all new entry signals are discarded, including
those formed on the close that schedules a next-bar EMA20 exit.
Each accepted entry requests exactly one MNQ contract; the strategy never varies this
quantity from risk, volatility, stop distance, PnL, or prior trade outcomes.
The V1 cost layer keeps the causal bar-based prices as explicit ``base_fill_price``
values, then embeds exactly one adverse MNQ tick in every actual simulated fill and
charges the versioned per-side commission once.  It never charges rejected, ignored,
expired, or end-of-data mark events and never adds a second spread/slippage debit.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
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
SLIPPAGE_MODELED = True
BID_ASK_SPREAD_MODELED = False
LATENCY_MODELED = False
TICK_REALISTIC_FILL_MODELED = False
INITIAL_STOP_SOURCE_BAR_OFFSET = 2
INITIAL_STOP_BUFFER_TICKS = 1
INITIAL_STOP_BUFFER_POINTS = MNQ_TICK_SIZE_POINTS * INITIAL_STOP_BUFFER_TICKS
INITIAL_STOP_IS_IMMUTABLE = True
GAP_THROUGH_STOP_FILLS_AT_BAR_OPEN = True
STOP_INTRABAR_SLIPPAGE_MODELED = True
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
BREAKEVEN = "NONE"
INITIAL_STRUCTURAL_STOP_IS_IMMUTABLE = INITIAL_STOP_IS_IMMUTABLE
MOVE_STOP_TO_ENTRY = False
BREAKEVEN_TRIGGER = None
BREAKEVEN_PRICE = None
BREAKEVEN_FAVORABLE_TICKS_TRIGGER = None
BREAKEVEN_R_MULTIPLE_TRIGGER = None
BREAKEVEN_MONETARY_PNL_TRIGGER = None
BREAKEVEN_DURATION_BARS_TRIGGER = None
TRAILING_STOP = "NONE"
TRAILING_STOP_ENABLED = False
TRAILING_ACTIVATION = None
TRAILING_DISTANCE = None
TRAILING_STEP = None
TRAILING_UPDATE_FREQUENCY = None
TRAILING_REFERENCE = None
SESSION_FILTER = "NONE"
STRATEGY_ENTRY_SESSION_FILTER_ENABLED = False
ALLOWED_WEEKDAYS = None
SESSION_START = None
SESSION_END = None
STRATEGY_TIMEZONE = None
DST_RULE = None
SOURCE_TRADING_HOURS_TEMPLATE = "CME US Index Futures ETH"
SOURCE_CALENDAR_REQUIRED = True
OPEN_POSITION_SIGNAL_POLICY = "IGNORE_ALL_NEW_SIGNALS_UNTIL_FLAT"
ADD_TO_POSITION = False
SCALE_IN = False
REVERSE_POSITION = False
CLOSE_AND_REVERSE = False
QUEUE_SIGNAL_UNTIL_FLAT = False
DEFERRED_ENTRY = False
POSITION_SIZE_MODE = "FIXED"
INITIAL_POSITION_SIZE = 1
MAX_POSITION_SIZE = 1
RISK_PERCENT_SIZING = False
VOLATILITY_SIZING = False
STOP_DISTANCE_SIZING = False
PNL_BASED_SIZING = False
MARTINGALE = False
ANTI_MARTINGALE = False
END_OF_DATA_POSITION_POLICY = "KEEP_OPEN_UNREALIZED"
END_OF_DATA_ACCOUNTING_UNIT = "MNQ_POINTS"
END_OF_DATA_FORCED_EXIT = False
END_OF_DATA_SYNTHETIC_FILL = False
UNREALIZED_PNL_IS_REALIZED = False
UNREALIZED_PNL_AFFECTS_CLOSED_TRADE_METRICS = False
COST_MODEL_ID = "EMA_PULLBACK_V1_MNQ_COSTS_2026_09_27"
COST_MODEL_VERSION = "1.0"
COST_MODEL_REFERENCE_DATE = "2026-09-27"
COST_MODEL_CLASSIFICATION = "VERSIONED_V1_COST_ASSUMPTION"
COMMISSION_PER_SIDE_USD = Decimal("0.51")
ENTRY_SLIPPAGE_TICKS = 1
EMA20_EXIT_SLIPPAGE_TICKS = 1
STRUCTURAL_STOP_SLIPPAGE_TICKS = 1
SPREAD_MODEL = "ABSORBED_IN_FIXED_SLIPPAGE"
EXPLICIT_BID_ASK_SPREAD_CHARGE = False
FEE_APPLICATION = "EACH_FILL"
ROUNDING_POLICY = "DECIMAL_EXACT_TICK_GRID_AND_USD_CENTS_HALF_UP"
USD_CENT = Decimal("0.01")
MNQ_POINT_VALUE_USD = Decimal("2.00")
MNQ_TICK_VALUE_USD = MNQ_TICK_SIZE_POINTS * MNQ_POINT_VALUE_USD
SLIPPAGE_EMBEDDED_IN_EXECUTION_PRICE = True
SEPARATE_SLIPPAGE_CHARGE_USD = Decimal("0.00")
SEPARATE_SPREAD_CHARGE_USD = Decimal("0.00")
COMMISSION_SOURCE_URL = (
    "https://apextraderfunding.com/help-center/rithmic/rithmic-commissions-instruments/"
)
MNQ_CONTRACT_SPEC_SOURCE_URL = (
    "https://www.cmegroup.com/markets/equities/nasdaq/micro-e-mini-nasdaq-100.html"
)


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


class OpenPositionSignalAction(StrEnum):
    """Eligibility of a fresh entry signal on the current closed bar."""

    ALLOW = "ALLOW"
    IGNORE = "IGNORE"
    NO_SIGNAL = "NO_SIGNAL"


class PositionState(StrEnum):
    """Actual position state at the entry-decision close."""

    FLAT = "FLAT"
    LONG = "LONG"
    SHORT = "SHORT"


class PositionSizeTransition(StrEnum):
    """Lifecycle transition represented by the fixed one-contract result."""

    ENTRY = "ENTRY"
    HOLD = "HOLD"
    EXIT = "EXIT"
    FLAT = "FLAT"


class EndOfDataPositionState(StrEnum):
    """Position state reported after the final valid closed source bar."""

    FLAT = "FLAT"
    OPEN_AT_END_OF_DATA = "OPEN_AT_END_OF_DATA"


class CostEventKind(StrEnum):
    """Execution or non-execution event evaluated by the V1 cost layer."""

    ENTRY = "ENTRY"
    EMA20_EXIT = "EMA20_EXIT"
    STRUCTURAL_STOP = "STRUCTURAL_STOP"
    IGNORED_SIGNAL = "IGNORED_SIGNAL"
    END_OF_DATA_MARK = "END_OF_DATA_MARK"


class CostApplicationStatus(StrEnum):
    """Whether one source event created an actual cost-bearing simulated fill."""

    FILLED = "FILLED"
    NO_FILL = "NO_FILL"


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
class BreakevenEvaluationResult:
    """Explicit proof that V1 keeps the original structural stop unchanged."""

    position_side: PullbackSide
    initial_stop: InitialStructuralStop
    active_stop: InitialStructuralStop
    breakeven: str = BREAKEVEN
    initial_structural_stop_is_immutable: bool = INITIAL_STRUCTURAL_STOP_IS_IMMUTABLE
    move_stop_to_entry: bool = MOVE_STOP_TO_ENTRY
    breakeven_trigger: None = BREAKEVEN_TRIGGER
    breakeven_price: None = BREAKEVEN_PRICE
    favorable_ticks_trigger: None = BREAKEVEN_FAVORABLE_TICKS_TRIGGER
    risk_multiple_trigger: None = BREAKEVEN_R_MULTIPLE_TRIGGER
    monetary_pnl_trigger: None = BREAKEVEN_MONETARY_PNL_TRIGGER
    duration_bars_trigger: None = BREAKEVEN_DURATION_BARS_TRIGGER

    def __post_init__(self) -> None:
        if not isinstance(self.position_side, PullbackSide):
            raise PullbackContractError("breakeven position side must be explicitly LONG or SHORT")
        if not isinstance(self.initial_stop, InitialStructuralStop):
            raise PullbackContractError("breakeven requires the initial structural stop")
        if self.initial_stop.side is not self.position_side:
            raise PullbackContractError("breakeven position and initial stop sides must match")
        if self.active_stop is not self.initial_stop:
            raise PullbackContractError("breakeven must retain the exact initial stop object")
        if (
            self.breakeven != BREAKEVEN
            or self.initial_structural_stop_is_immutable is not True
            or self.move_stop_to_entry is not False
            or self.breakeven_trigger is not None
            or self.breakeven_price is not None
            or self.favorable_ticks_trigger is not None
            or self.risk_multiple_trigger is not None
            or self.monetary_pnl_trigger is not None
            or self.duration_bars_trigger is not None
        ):
            raise PullbackContractError("V1 breakeven contract must remain explicitly disabled")


@dataclass(frozen=True)
class TrailingStopEvaluationResult:
    """Explicit proof that V1 never trails the original structural stop."""

    position_side: PullbackSide
    initial_stop: InitialStructuralStop
    active_stop: InitialStructuralStop
    trailing_stop: str = TRAILING_STOP
    initial_structural_stop_is_immutable: bool = INITIAL_STRUCTURAL_STOP_IS_IMMUTABLE
    trailing_stop_enabled: bool = TRAILING_STOP_ENABLED
    trailing_activation: None = TRAILING_ACTIVATION
    trailing_distance: None = TRAILING_DISTANCE
    trailing_step: None = TRAILING_STEP
    trailing_update_frequency: None = TRAILING_UPDATE_FREQUENCY
    trailing_reference: None = TRAILING_REFERENCE

    def __post_init__(self) -> None:
        if not isinstance(self.position_side, PullbackSide):
            raise PullbackContractError("trailing position side must be explicitly LONG or SHORT")
        if not isinstance(self.initial_stop, InitialStructuralStop):
            raise PullbackContractError("trailing evaluation requires the initial structural stop")
        if self.initial_stop.side is not self.position_side:
            raise PullbackContractError("trailing position and initial stop sides must match")
        if self.active_stop is not self.initial_stop:
            raise PullbackContractError("trailing must retain the exact initial stop object")
        if (
            self.trailing_stop != TRAILING_STOP
            or self.initial_structural_stop_is_immutable is not True
            or self.trailing_stop_enabled is not False
            or self.trailing_activation is not None
            or self.trailing_distance is not None
            or self.trailing_step is not None
            or self.trailing_update_frequency is not None
            or self.trailing_reference is not None
        ):
            raise PullbackContractError("V1 trailing stop contract must remain explicitly disabled")


@dataclass(frozen=True)
class SessionFilterEvaluationResult:
    """Eligibility on one closed bar already admitted by the source calendar.

    Strategy V1 owns no clock, weekday, timezone, DST, RTH, or ETH filtering logic.
    The explicit source fields prevent ``SESSION_FILTER = NONE`` from bypassing the
    upstream Trading Hours calendar.  Both existing exits remain eligible everywhere
    an entry may be evaluated.
    """

    source_bar_sequence: int
    source_trading_hours_template: str
    source_bar_closed: bool = True
    source_bar_valid: bool = True
    entry_allowed: bool = True
    structural_stop_active: bool = True
    ema20_exit_active: bool = True
    source_calendar_required: bool = SOURCE_CALENDAR_REQUIRED
    session_filter: str = SESSION_FILTER
    strategy_entry_session_filter_enabled: bool = STRATEGY_ENTRY_SESSION_FILTER_ENABLED
    allowed_weekdays: None = ALLOWED_WEEKDAYS
    session_start: None = SESSION_START
    session_end: None = SESSION_END
    strategy_timezone: None = STRATEGY_TIMEZONE
    dst_rule: None = DST_RULE

    def __post_init__(self) -> None:
        if (
            isinstance(self.source_bar_sequence, bool)
            or not isinstance(self.source_bar_sequence, int)
            or self.source_bar_sequence < 0
        ):
            raise PullbackContractError("source bar sequence must be a non-negative integer")
        if self.source_trading_hours_template != SOURCE_TRADING_HOURS_TEMPLATE:
            raise PullbackContractError("source Trading Hours template must remain exact")
        if (
            self.source_bar_closed is not True
            or self.source_bar_valid is not True
            or self.source_calendar_required is not True
        ):
            raise PullbackContractError("strategy requires a closed valid source-calendar bar")
        if (
            self.entry_allowed is not True
            or self.structural_stop_active is not True
            or self.ema20_exit_active is not True
        ):
            raise PullbackContractError("session filtering cannot disable V1 entries or exits")
        if (
            self.session_filter != SESSION_FILTER
            or self.strategy_entry_session_filter_enabled is not False
            or self.allowed_weekdays is not None
            or self.session_start is not None
            or self.session_end is not None
            or self.strategy_timezone is not None
            or self.dst_rule is not None
        ):
            raise PullbackContractError("V1 session filter must remain explicitly disabled")


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


@dataclass(frozen=True)
class OpenPositionSignalPolicyResult:
    """One close's entry eligibility; ignored signals cannot be replayed or queued."""

    position_state: PositionState
    action: OpenPositionSignalAction
    decision_bar_sequence: int
    accepted_signal: EMAPullbackEntrySignalResult | None
    pending_ema20_exit: bool = False
    queued_signal: None = None
    add_to_position: bool = ADD_TO_POSITION
    scale_in: bool = SCALE_IN
    reverse_position: bool = REVERSE_POSITION
    close_and_reverse: bool = CLOSE_AND_REVERSE
    queue_signal_until_flat: bool = QUEUE_SIGNAL_UNTIL_FLAT
    deferred_entry: bool = DEFERRED_ENTRY

    def __post_init__(self) -> None:
        if not isinstance(self.position_state, PositionState) or not isinstance(
            self.action, OpenPositionSignalAction
        ):
            raise PullbackContractError("position state and entry action must be explicit")
        if (
            type(self.decision_bar_sequence) is not int
            or self.decision_bar_sequence < 0
            or type(self.pending_ema20_exit) is not bool
        ):
            raise PullbackContractError("entry policy requires a valid closed-bar sequence")
        if (
            self.queued_signal is not None
            or self.add_to_position is not False
            or self.scale_in is not False
            or self.reverse_position is not False
            or self.close_and_reverse is not False
            or self.queue_signal_until_flat is not False
            or self.deferred_entry is not False
        ):
            raise PullbackContractError("V1 cannot add, reverse, defer, or queue entry signals")
        if self.action is OpenPositionSignalAction.ALLOW:
            signal = self.accepted_signal
            if (
                self.position_state is not PositionState.FLAT
                or self.pending_ema20_exit
                or not isinstance(signal, EMAPullbackEntrySignalResult)
                or not isinstance(signal.side, PullbackSide)
                or signal.entry_signal_qualifies is not True
                or signal.signal is not EntrySignal(signal.side.value)
                or signal.confirmation_bar_sequence != self.decision_bar_sequence
            ):
                raise PullbackContractError("only a fresh qualified signal while flat is allowed")
        elif (
            self.accepted_signal is not None
            or (self.action is OpenPositionSignalAction.IGNORE)
            != (self.position_state is not PositionState.FLAT)
            or (self.pending_ema20_exit and self.position_state is PositionState.FLAT)
        ):
            raise PullbackContractError("signals while open must be ignored, never deferred")


def evaluate_open_position_signal_policy(
    *,
    candidate_signal: EMAPullbackEntrySignalResult | None,
    decision_bar: ClosedBarEMA20,
    position_at_close: ProtectedEntryExecutionResult | None,
    last_exit: ExitPriorityExecutionResult | InitialStopBarExecutionResult | None = None,
    pending_ema20_exit: EMA20PositionExitResult | None = None,
) -> OpenPositionSignalPolicyResult:
    """Discard new signals if the position is still open at ``Close[t]``.

    A pending EMA20 exit cannot make the position flat before its actual next-bar
    fill.  Once an exit has filled, only a freshly formed signal at or after that
    execution bar's close may be considered.  No signal, order, or price is kept
    for later execution.  Source-calendar eligibility remains an upstream gate.
    """
    if not isinstance(decision_bar, ClosedBarEMA20):
        raise PullbackContractError("entry policy requires a closed decision bar")
    if candidate_signal is not None:
        if not isinstance(candidate_signal, EMAPullbackEntrySignalResult):
            raise PullbackContractError("entry policy requires a qualified signal result")
        if (
            not isinstance(candidate_signal.side, PullbackSide)
            or candidate_signal.entry_signal_qualifies is not True
            or candidate_signal.signal is not EntrySignal(candidate_signal.side.value)
            or candidate_signal.pullback_confirmation_qualifies is not True
            or candidate_signal.ema20_slope_qualifies is not True
            or candidate_signal.macd_cross_qualifies is not True
            or candidate_signal.macd_status is not MACDStatus.READY
            or candidate_signal.confirmation_bar_sequence != decision_bar.sequence
        ):
            raise PullbackContractError("entry signal must form on this exact closed bar")
    if position_at_close is not None:
        position = position_at_close
        if (
            not isinstance(position, ProtectedEntryExecutionResult)
            or not isinstance(position.side, PullbackSide)
            or position.status is not SimulatedExecutionStatus.FILLED
            or position.position_opened is not True
            or position.execution_bar_sequence is None
            or position.execution_bar_sequence != position.decision_bar_sequence + 1
            or position.execution_bar_sequence > decision_bar.sequence
            or position.entry_price is None
            or not isinstance(position.initial_stop, InitialStructuralStop)
            or position.initial_stop.side is not position.side
            or position.initial_stop.decision_bar_sequence != position.decision_bar_sequence
        ):
            raise PullbackContractError("open state requires an already filled protected position")
        if last_exit is not None:
            raise PullbackContractError("position cannot be open after a recorded closing fill")
    elif last_exit is not None:
        if isinstance(last_exit, ExitPriorityExecutionResult):
            exit_bar_sequence = last_exit.execution_bar_sequence
        elif (
            isinstance(last_exit, InitialStopBarExecutionResult)
            and last_exit.status is InitialStopTriggerStatus.STOP_TRIGGERED
            and last_exit.position_closed is True
            and last_exit.fill_price is not None
        ):
            exit_bar_sequence = last_exit.evaluated_bar_sequence
        else:
            raise PullbackContractError("flat transition requires a filled closing exit")
        if (
            type(exit_bar_sequence) is not int
            or exit_bar_sequence < 0
            or exit_bar_sequence > decision_bar.sequence
        ):
            raise PullbackContractError("an old signal cannot execute after returning to flat")

    if pending_ema20_exit is not None and (
        position_at_close is None
        or not isinstance(pending_ema20_exit, EMA20PositionExitResult)
        or not isinstance(pending_ema20_exit.position_side, PullbackSide)
        or pending_ema20_exit.position_side is not position_at_close.side
        or pending_ema20_exit.exit_qualifies is not True
        or pending_ema20_exit.action
        is not PositionExitAction(f"EXIT_{position_at_close.side.value}")
        or pending_ema20_exit.decision_bar_sequence != decision_bar.sequence
        or pending_ema20_exit.earliest_execution_bar_sequence != decision_bar.sequence + 1
        or pending_ema20_exit.same_bar_execution_allowed is not False
    ):
        raise PullbackContractError("pending exit must be for this open position and close")

    if position_at_close is not None:
        state = PositionState(position_at_close.side.value)
        action = OpenPositionSignalAction.IGNORE
    else:
        state = PositionState.FLAT
        action = (
            OpenPositionSignalAction.ALLOW
            if candidate_signal is not None
            else OpenPositionSignalAction.NO_SIGNAL
        )
    return OpenPositionSignalPolicyResult(
        position_state=state,
        action=action,
        decision_bar_sequence=decision_bar.sequence,
        accepted_signal=candidate_signal if action is OpenPositionSignalAction.ALLOW else None,
        pending_ema20_exit=pending_ema20_exit is not None,
    )


@dataclass(frozen=True)
class FixedPositionSizeResult:
    """Fail-closed signed MNQ position under the fixed one-contract V1 rule."""

    transition: PositionSizeTransition
    position_state: PositionState
    side: PullbackSide | None
    signed_contracts: int
    absolute_contracts: int
    requested_entry_contracts: int
    instrument: str = INSTRUMENT
    position_size_mode: str = POSITION_SIZE_MODE
    initial_position_size: int = INITIAL_POSITION_SIZE
    max_position_size: int = MAX_POSITION_SIZE
    risk_percent_sizing: bool = RISK_PERCENT_SIZING
    volatility_sizing: bool = VOLATILITY_SIZING
    stop_distance_sizing: bool = STOP_DISTANCE_SIZING
    pnl_based_sizing: bool = PNL_BASED_SIZING
    martingale: bool = MARTINGALE
    anti_martingale: bool = ANTI_MARTINGALE

    def __post_init__(self) -> None:
        if not isinstance(self.transition, PositionSizeTransition) or not isinstance(
            self.position_state, PositionState
        ):
            raise PullbackContractError("position size transition and state must be explicit")
        if (
            self.instrument != INSTRUMENT
            or self.position_size_mode != POSITION_SIZE_MODE
            or type(self.initial_position_size) is not int
            or self.initial_position_size != INITIAL_POSITION_SIZE
            or type(self.max_position_size) is not int
            or self.max_position_size != MAX_POSITION_SIZE
        ):
            raise PullbackContractError("V1 position size must remain fixed at exactly one MNQ")
        if (
            self.risk_percent_sizing is not False
            or self.volatility_sizing is not False
            or self.stop_distance_sizing is not False
            or self.pnl_based_sizing is not False
            or self.martingale is not False
            or self.anti_martingale is not False
        ):
            raise PullbackContractError("V1 cannot enable hidden or dynamic position sizing")
        if (
            type(self.signed_contracts) is not int
            or type(self.absolute_contracts) is not int
            or self.signed_contracts not in (-MAX_POSITION_SIZE, 0, MAX_POSITION_SIZE)
            or self.absolute_contracts != abs(self.signed_contracts)
        ):
            raise PullbackContractError("absolute V1 position cannot exceed one MNQ contract")
        if type(
            self.requested_entry_contracts
        ) is not int or self.requested_entry_contracts not in (
            0,
            INITIAL_POSITION_SIZE,
        ):
            raise PullbackContractError("entry request must be zero or exactly one MNQ contract")

        if self.signed_contracts == 0:
            if (
                self.position_state is not PositionState.FLAT
                or self.side is not None
                or self.transition not in (PositionSizeTransition.EXIT, PositionSizeTransition.FLAT)
                or self.requested_entry_contracts != 0
            ):
                raise PullbackContractError("zero contracts must represent a coherent flat state")
            return

        expected_side = PullbackSide.LONG if self.signed_contracts > 0 else PullbackSide.SHORT
        if (
            self.side is not expected_side
            or self.position_state is not PositionState(expected_side.value)
            or self.transition not in (PositionSizeTransition.ENTRY, PositionSizeTransition.HOLD)
            or self.requested_entry_contracts
            != (INITIAL_POSITION_SIZE if self.transition is PositionSizeTransition.ENTRY else 0)
        ):
            raise PullbackContractError("signed quantity, side, state, and transition must agree")


def evaluate_fixed_position_size(
    *,
    signal_policy: OpenPositionSignalPolicyResult | None,
    entry_execution: ProtectedEntryExecutionResult | None = None,
    open_position: FixedPositionSizeResult | None = None,
    closing_exit: ExitPriorityExecutionResult | InitialStopBarExecutionResult | None = None,
) -> FixedPositionSizeResult:
    """Apply entry, hold, and exit transitions under the exact one-MNQ baseline.

    The API intentionally accepts no balance, PnL, volatility, stop-distance, risk
    percentage, or trade-history input.  An allowed flat-state signal plus its exact
    next-bar fill opens one signed contract; an ignored signal preserves the existing
    one-contract position; and a verified closing fill returns the position to zero.
    """
    if open_position is None:
        if closing_exit is not None:
            raise PullbackContractError("cannot close a position when the strategy is already flat")
        if not isinstance(signal_policy, OpenPositionSignalPolicyResult):
            raise PullbackContractError("flat sizing requires the current entry-signal policy")
        if signal_policy.position_state is not PositionState.FLAT:
            raise PullbackContractError("flat sizing requires a flat signal-policy state")
        if signal_policy.action is OpenPositionSignalAction.NO_SIGNAL:
            if entry_execution is not None:
                raise PullbackContractError("an entry fill requires a fresh allowed signal")
            return FixedPositionSizeResult(
                transition=PositionSizeTransition.FLAT,
                position_state=PositionState.FLAT,
                side=None,
                signed_contracts=0,
                absolute_contracts=0,
                requested_entry_contracts=0,
            )
        if (
            signal_policy.action is not OpenPositionSignalAction.ALLOW
            or not isinstance(signal_policy.accepted_signal, EMAPullbackEntrySignalResult)
            or not isinstance(signal_policy.accepted_signal.side, PullbackSide)
        ):
            raise PullbackContractError("one-contract entry requires a fresh allowed signal")
        side = signal_policy.accepted_signal.side
        if (
            not isinstance(entry_execution, ProtectedEntryExecutionResult)
            or entry_execution.side is not side
            or entry_execution.status is not SimulatedExecutionStatus.FILLED
            or entry_execution.position_opened is not True
            or entry_execution.entry_price is None
            or entry_execution.decision_bar_sequence != signal_policy.decision_bar_sequence
            or entry_execution.execution_bar_sequence != signal_policy.decision_bar_sequence + 1
            or not isinstance(entry_execution.initial_stop, InitialStructuralStop)
            or entry_execution.initial_stop.side is not side
        ):
            raise PullbackContractError(
                "one-contract position requires its exact next-bar entry fill"
            )
        signed_contracts = (
            INITIAL_POSITION_SIZE if side is PullbackSide.LONG else -INITIAL_POSITION_SIZE
        )
        return FixedPositionSizeResult(
            transition=PositionSizeTransition.ENTRY,
            position_state=PositionState(side.value),
            side=side,
            signed_contracts=signed_contracts,
            absolute_contracts=INITIAL_POSITION_SIZE,
            requested_entry_contracts=INITIAL_POSITION_SIZE,
        )

    if (
        not isinstance(open_position, FixedPositionSizeResult)
        or open_position.signed_contracts == 0
        or open_position.side is None
        or open_position.position_state is PositionState.FLAT
    ):
        raise PullbackContractError("position sizing transition requires one open MNQ contract")
    if entry_execution is not None:
        raise PullbackContractError("an open position cannot accept another entry fill")

    if closing_exit is not None:
        if signal_policy is not None:
            raise PullbackContractError(
                "a closing fill and close-time entry policy cannot be combined"
            )
        if isinstance(closing_exit, ExitPriorityExecutionResult):
            valid_close = closing_exit.position_closed is True
            closing_side = closing_exit.side
        elif isinstance(closing_exit, InitialStopBarExecutionResult):
            valid_close = (
                closing_exit.status is InitialStopTriggerStatus.STOP_TRIGGERED
                and closing_exit.position_closed is True
                and closing_exit.fill_price is not None
            )
            closing_side = closing_exit.side
        else:
            raise PullbackContractError("position size exit requires a verified V1 closing fill")
        if not valid_close or closing_side is not open_position.side:
            raise PullbackContractError("closing fill must match the open one-contract position")
        return FixedPositionSizeResult(
            transition=PositionSizeTransition.EXIT,
            position_state=PositionState.FLAT,
            side=None,
            signed_contracts=0,
            absolute_contracts=0,
            requested_entry_contracts=0,
        )

    if (
        not isinstance(signal_policy, OpenPositionSignalPolicyResult)
        or signal_policy.action is not OpenPositionSignalAction.IGNORE
        or signal_policy.position_state is not open_position.position_state
        or signal_policy.accepted_signal is not None
    ):
        raise PullbackContractError("open position must ignore every new entry signal")
    return FixedPositionSizeResult(
        transition=PositionSizeTransition.HOLD,
        position_state=open_position.position_state,
        side=open_position.side,
        signed_contracts=open_position.signed_contracts,
        absolute_contracts=open_position.absolute_contracts,
        requested_entry_contracts=0,
    )


@dataclass(frozen=True)
class EndOfDataPositionResult:
    """Informational final-close mark with no synthetic position-closing event."""

    position_state: EndOfDataPositionState
    position_side: PullbackSide | None
    signed_contracts: int
    entry_price: Decimal | None
    mark_price: Decimal
    mark_bar_sequence: int
    realized_pnl: Decimal
    realized_pnl_change: Decimal
    unrealized_pnl_at_end: Decimal
    realized_equity: Decimal
    marked_equity_at_end: Decimal
    closed_trade_count: int
    closed_trade_count_change: int
    open_position_at_end: bool
    end_of_data_position_policy: str = END_OF_DATA_POSITION_POLICY
    accounting_unit: str = END_OF_DATA_ACCOUNTING_UNIT
    forced_exit: bool = END_OF_DATA_FORCED_EXIT
    synthetic_fill: bool = END_OF_DATA_SYNTHETIC_FILL
    fill_price: None = None
    unrealized_pnl_is_realized: bool = UNREALIZED_PNL_IS_REALIZED
    unrealized_pnl_affects_closed_trade_metrics: bool = UNREALIZED_PNL_AFFECTS_CLOSED_TRADE_METRICS

    def __post_init__(self) -> None:
        if not isinstance(self.position_state, EndOfDataPositionState):
            raise PullbackContractError("end-of-data position state must be explicit")
        if (
            self.end_of_data_position_policy != END_OF_DATA_POSITION_POLICY
            or self.accounting_unit != END_OF_DATA_ACCOUNTING_UNIT
            or self.forced_exit is not False
            or self.synthetic_fill is not False
            or self.fill_price is not None
            or self.unrealized_pnl_is_realized is not False
            or self.unrealized_pnl_affects_closed_trade_metrics is not False
        ):
            raise PullbackContractError("end-of-data accounting cannot fabricate a realized exit")
        if type(self.mark_bar_sequence) is not int or self.mark_bar_sequence < 0:
            raise PullbackContractError("end-of-data mark sequence must be non-negative")
        for field_name in (
            "mark_price",
            "realized_pnl",
            "realized_pnl_change",
            "unrealized_pnl_at_end",
            "realized_equity",
            "marked_equity_at_end",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Decimal) or not value.is_finite():
                raise PullbackContractError(f"{field_name} must be a finite Decimal")
        if self.mark_price < 0:
            raise PullbackContractError("end-of-data mark price must be non-negative")
        if self.realized_pnl_change != Decimal(0):
            raise PullbackContractError("end-of-data marking cannot change realized PnL")
        if (
            type(self.closed_trade_count) is not int
            or self.closed_trade_count < 0
            or type(self.closed_trade_count_change) is not int
            or self.closed_trade_count_change != 0
        ):
            raise PullbackContractError("end-of-data marking cannot add a closed trade")
        if self.marked_equity_at_end != self.realized_equity + self.unrealized_pnl_at_end:
            raise PullbackContractError(
                "marked equity must separate realized and unrealized values"
            )
        if type(self.open_position_at_end) is not bool:
            raise PullbackContractError("open_position_at_end must be bool")
        if type(self.signed_contracts) is not int or self.signed_contracts not in (-1, 0, 1):
            raise PullbackContractError("end-of-data signed position must be zero or one MNQ")

        if not self.open_position_at_end:
            if (
                self.position_state is not EndOfDataPositionState.FLAT
                or self.position_side is not None
                or self.signed_contracts != 0
                or self.entry_price is not None
                or self.unrealized_pnl_at_end != Decimal(0)
            ):
                raise PullbackContractError("flat end-of-data accounting must remain exactly flat")
            return

        if (
            self.position_state is not EndOfDataPositionState.OPEN_AT_END_OF_DATA
            or not isinstance(self.position_side, PullbackSide)
            or type(self.signed_contracts) is not int
            or self.signed_contracts != (1 if self.position_side is PullbackSide.LONG else -1)
            or not isinstance(self.entry_price, Decimal)
            or not self.entry_price.is_finite()
            or self.entry_price < 0
        ):
            raise PullbackContractError("open end-of-data state must retain exactly one MNQ")
        expected_unrealized = (self.mark_price - self.entry_price) * self.signed_contracts
        if self.unrealized_pnl_at_end != expected_unrealized:
            raise PullbackContractError("unrealized PnL must use only the final valid close")


def evaluate_end_of_data_position(
    *,
    final_valid_bar: ClosedBarEMA20,
    position: FixedPositionSizeResult | None,
    entry_execution: ProtectedEntryExecutionResult | None,
    costed_entry_fill: V1CostedFillResult | None,
    realized_pnl: Decimal,
    realized_equity: Decimal,
    closed_trade_count: int,
) -> EndOfDataPositionResult:
    """Report final state without a forced exit, fill, or closed-trade mutation.

    Values remain normalized MNQ points, but the mark starts from the already-slipped
    entry execution.  The entry commission is an upstream realized fill expense and
    this mark creates no new charge.  Only ``final_valid_bar.close`` marks an open
    position; High, Low, Open, EMA20, reconstructed quotes, and future bars are excluded.
    """
    if not isinstance(final_valid_bar, ClosedBarEMA20):
        raise PullbackContractError("end-of-data reporting requires the final valid closed bar")
    for field_name, value in (
        ("realized_pnl", realized_pnl),
        ("realized_equity", realized_equity),
    ):
        if not isinstance(value, Decimal) or not value.is_finite():
            raise PullbackContractError(f"{field_name} must be a finite Decimal")
    if type(closed_trade_count) is not int or closed_trade_count < 0:
        raise PullbackContractError("closed_trade_count must be a non-negative integer")

    mark_price = final_valid_bar.close
    if position is None and entry_execution is None and costed_entry_fill is None:
        unrealized_pnl_at_end = Decimal(0)
        return EndOfDataPositionResult(
            position_state=EndOfDataPositionState.FLAT,
            position_side=None,
            signed_contracts=0,
            entry_price=None,
            mark_price=mark_price,
            mark_bar_sequence=final_valid_bar.sequence,
            realized_pnl=realized_pnl,
            realized_pnl_change=Decimal(0),
            unrealized_pnl_at_end=unrealized_pnl_at_end,
            realized_equity=realized_equity,
            marked_equity_at_end=realized_equity,
            closed_trade_count=closed_trade_count,
            closed_trade_count_change=0,
            open_position_at_end=False,
        )
    if position is None or entry_execution is None or costed_entry_fill is None:
        raise PullbackContractError(
            "open end-of-data reporting requires position, entry fill, and costed entry"
        )
    if (
        not isinstance(position, FixedPositionSizeResult)
        or position.position_state is PositionState.FLAT
        or position.transition not in (PositionSizeTransition.ENTRY, PositionSizeTransition.HOLD)
        or position.side is None
        or abs(position.signed_contracts) != 1
    ):
        raise PullbackContractError("end-of-data reporting requires one open MNQ position")
    if (
        not isinstance(entry_execution, ProtectedEntryExecutionResult)
        or entry_execution.status is not SimulatedExecutionStatus.FILLED
        or entry_execution.position_opened is not True
        or entry_execution.side is not position.side
        or entry_execution.order_type is not SimulatedOrderType.MARKET
        or entry_execution.entry_price is None
        or not isinstance(entry_execution.entry_price, Decimal)
        or not entry_execution.entry_price.is_finite()
        or entry_execution.entry_price < 0
        or entry_execution.execution_bar_sequence is None
        or entry_execution.execution_bar_sequence != entry_execution.decision_bar_sequence + 1
        or entry_execution.execution_bar_sequence > final_valid_bar.sequence
        or not isinstance(entry_execution.initial_stop, InitialStructuralStop)
        or entry_execution.initial_stop.side is not position.side
    ):
        raise PullbackContractError("end-of-data position requires its causal filled entry")

    if (
        not isinstance(costed_entry_fill, V1CostedFillResult)
        or costed_entry_fill.status is not CostApplicationStatus.FILLED
        or costed_entry_fill.event_kind is not CostEventKind.ENTRY
        or costed_entry_fill.side is not position.side
        or costed_entry_fill.fill_quantity != 1
        or costed_entry_fill.base_fill_price != entry_execution.entry_price
        or costed_entry_fill.execution_price is None
    ):
        raise PullbackContractError("end-of-data mark requires the exact costed entry fill")

    unrealized_pnl_at_end = (
        mark_price - costed_entry_fill.execution_price
    ) * position.signed_contracts
    return EndOfDataPositionResult(
        position_state=EndOfDataPositionState.OPEN_AT_END_OF_DATA,
        position_side=position.side,
        signed_contracts=position.signed_contracts,
        entry_price=costed_entry_fill.execution_price,
        mark_price=mark_price,
        mark_bar_sequence=final_valid_bar.sequence,
        realized_pnl=realized_pnl,
        realized_pnl_change=Decimal(0),
        unrealized_pnl_at_end=unrealized_pnl_at_end,
        realized_equity=realized_equity,
        marked_equity_at_end=realized_equity + unrealized_pnl_at_end,
        closed_trade_count=closed_trade_count,
        closed_trade_count_change=0,
        open_position_at_end=True,
    )


def _is_on_mnq_tick_grid(price: Decimal) -> bool:
    return price % MNQ_TICK_SIZE_POINTS == 0


def _round_usd(amount: Decimal) -> Decimal:
    return amount.quantize(USD_CENT, rounding=ROUND_HALF_UP)


def _slippage_ticks_for_event(event_kind: CostEventKind) -> int:
    mapping = {
        CostEventKind.ENTRY: ENTRY_SLIPPAGE_TICKS,
        CostEventKind.EMA20_EXIT: EMA20_EXIT_SLIPPAGE_TICKS,
        CostEventKind.STRUCTURAL_STOP: STRUCTURAL_STOP_SLIPPAGE_TICKS,
    }
    try:
        return mapping[event_kind]
    except KeyError as exc:
        raise PullbackContractError("non-fill events cannot receive slippage") from exc


@dataclass(frozen=True)
class V1CostedFillResult:
    """One costed fill, or explicit proof that a source event created no fill."""

    event_kind: CostEventKind
    status: CostApplicationStatus
    side: PullbackSide | None
    fill_quantity: int
    base_fill_price: Decimal | None
    execution_price: Decimal | None
    slippage_ticks: int
    slippage_points: Decimal
    commission_usd: Decimal
    cost_model_id: str = COST_MODEL_ID
    cost_model_version: str = COST_MODEL_VERSION
    cost_model_reference_date: str = COST_MODEL_REFERENCE_DATE
    cost_model_classification: str = COST_MODEL_CLASSIFICATION
    commission_per_side_usd: Decimal = COMMISSION_PER_SIDE_USD
    tick_size_points: Decimal = MNQ_TICK_SIZE_POINTS
    point_value_usd: Decimal = MNQ_POINT_VALUE_USD
    spread_model: str = SPREAD_MODEL
    explicit_bid_ask_spread_charge: bool = EXPLICIT_BID_ASK_SPREAD_CHARGE
    fee_application: str = FEE_APPLICATION
    rounding_policy: str = ROUNDING_POLICY
    slippage_embedded_in_execution_price: bool = SLIPPAGE_EMBEDDED_IN_EXECUTION_PRICE
    separate_slippage_charge_usd: Decimal = SEPARATE_SLIPPAGE_CHARGE_USD
    separate_spread_charge_usd: Decimal = SEPARATE_SPREAD_CHARGE_USD

    def __post_init__(self) -> None:
        if not isinstance(self.event_kind, CostEventKind) or not isinstance(
            self.status, CostApplicationStatus
        ):
            raise PullbackContractError("cost event and application status must be explicit")
        if (
            self.cost_model_id != COST_MODEL_ID
            or self.cost_model_version != COST_MODEL_VERSION
            or self.cost_model_reference_date != COST_MODEL_REFERENCE_DATE
            or self.cost_model_classification != COST_MODEL_CLASSIFICATION
            or self.commission_per_side_usd != COMMISSION_PER_SIDE_USD
            or self.tick_size_points != MNQ_TICK_SIZE_POINTS
            or self.point_value_usd != MNQ_POINT_VALUE_USD
            or self.spread_model != SPREAD_MODEL
            or self.explicit_bid_ask_spread_charge is not False
            or self.fee_application != FEE_APPLICATION
            or self.rounding_policy != ROUNDING_POLICY
            or self.slippage_embedded_in_execution_price is not True
            or self.separate_slippage_charge_usd != Decimal("0.00")
            or self.separate_spread_charge_usd != Decimal("0.00")
        ):
            raise PullbackContractError("V1 cost configuration cannot be changed implicitly")
        for field_name in (
            "commission_per_side_usd",
            "tick_size_points",
            "point_value_usd",
            "slippage_points",
            "commission_usd",
            "separate_slippage_charge_usd",
            "separate_spread_charge_usd",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Decimal) or not value.is_finite() or value < 0:
                raise PullbackContractError(f"{field_name} must be a finite non-negative Decimal")
        if type(self.fill_quantity) is not int or self.fill_quantity not in (0, 1):
            raise PullbackContractError("V1 cost fills must contain zero or one MNQ")
        if type(self.slippage_ticks) is not int or self.slippage_ticks < 0:
            raise PullbackContractError("slippage ticks must be a non-negative integer")
        if self.commission_usd != _round_usd(self.commission_usd):
            raise PullbackContractError("commission must use USD cents ROUND_HALF_UP")
        if self.side is not None and not isinstance(self.side, PullbackSide):
            raise PullbackContractError("cost event side must be explicitly LONG, SHORT, or absent")

        if self.status is CostApplicationStatus.NO_FILL:
            if (
                self.fill_quantity != 0
                or self.base_fill_price is not None
                or self.execution_price is not None
                or self.slippage_ticks != 0
                or self.slippage_points != Decimal(0)
                or self.commission_usd != Decimal("0.00")
            ):
                raise PullbackContractError("a non-fill event cannot incur cost or execution price")
            return

        if self.event_kind not in (
            CostEventKind.ENTRY,
            CostEventKind.EMA20_EXIT,
            CostEventKind.STRUCTURAL_STOP,
        ):
            raise PullbackContractError("only actual entry or exit fills may incur V1 costs")
        if not isinstance(self.side, PullbackSide) or self.fill_quantity != 1:
            raise PullbackContractError("a costed V1 fill must identify one MNQ side")
        if (
            not isinstance(self.base_fill_price, Decimal)
            or not self.base_fill_price.is_finite()
            or self.base_fill_price < 0
            or not _is_on_mnq_tick_grid(self.base_fill_price)
            or not isinstance(self.execution_price, Decimal)
            or not self.execution_price.is_finite()
            or self.execution_price < 0
            or not _is_on_mnq_tick_grid(self.execution_price)
        ):
            raise PullbackContractError(
                "base and execution prices must use the exact MNQ tick grid"
            )
        expected_ticks = _slippage_ticks_for_event(self.event_kind)
        expected_points = MNQ_TICK_SIZE_POINTS * expected_ticks
        if self.slippage_ticks != expected_ticks or self.slippage_points != expected_points:
            raise PullbackContractError("every V1 fill must embed exactly one configured tick")
        is_entry = self.event_kind is CostEventKind.ENTRY
        adverse_sign = (
            Decimal(1)
            if (is_entry and self.side is PullbackSide.LONG)
            or (not is_entry and self.side is PullbackSide.SHORT)
            else Decimal(-1)
        )
        expected_execution_price = self.base_fill_price + adverse_sign * expected_points
        if self.execution_price != expected_execution_price:
            raise PullbackContractError("V1 slippage must be strictly adverse and embedded once")
        expected_commission = _round_usd(COMMISSION_PER_SIDE_USD * self.fill_quantity)
        if self.commission_usd != expected_commission:
            raise PullbackContractError("commission must be charged once per actual fill")


@dataclass(frozen=True)
class V1RealizedTradePnL:
    """Net USD result from two already-slipped fills and their commissions only."""

    side: PullbackSide
    quantity: int
    entry_execution_price: Decimal
    exit_execution_price: Decimal
    gross_price_pnl_points: Decimal
    gross_price_pnl_usd: Decimal
    total_commission_usd: Decimal
    net_realized_pnl_usd: Decimal
    point_value_usd: Decimal = MNQ_POINT_VALUE_USD
    slippage_already_embedded: bool = SLIPPAGE_EMBEDDED_IN_EXECUTION_PRICE
    separate_slippage_charge_usd: Decimal = SEPARATE_SLIPPAGE_CHARGE_USD
    separate_spread_charge_usd: Decimal = SEPARATE_SPREAD_CHARGE_USD
    rounding_policy: str = ROUNDING_POLICY

    def __post_init__(self) -> None:
        if not isinstance(self.side, PullbackSide) or self.quantity != 1:
            raise PullbackContractError("realized V1 PnL requires exactly one MNQ")
        if (
            self.point_value_usd != MNQ_POINT_VALUE_USD
            or self.slippage_already_embedded is not True
            or self.separate_slippage_charge_usd != Decimal("0.00")
            or self.separate_spread_charge_usd != Decimal("0.00")
            or self.rounding_policy != ROUNDING_POLICY
        ):
            raise PullbackContractError("realized PnL cannot double-count costs")
        for field_name in (
            "entry_execution_price",
            "exit_execution_price",
            "gross_price_pnl_points",
            "gross_price_pnl_usd",
            "total_commission_usd",
            "net_realized_pnl_usd",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Decimal) or not value.is_finite():
                raise PullbackContractError(f"{field_name} must be a finite Decimal")
        if self.total_commission_usd < 0:
            raise PullbackContractError("realized commission cannot be negative")
        if not _is_on_mnq_tick_grid(self.entry_execution_price) or not _is_on_mnq_tick_grid(
            self.exit_execution_price
        ):
            raise PullbackContractError("realized trade prices must remain on the MNQ tick grid")
        expected_points = (
            self.exit_execution_price - self.entry_execution_price
            if self.side is PullbackSide.LONG
            else self.entry_execution_price - self.exit_execution_price
        )
        expected_gross_usd = _round_usd(expected_points * MNQ_POINT_VALUE_USD * self.quantity)
        expected_commission = _round_usd(COMMISSION_PER_SIDE_USD * self.quantity * 2)
        if (
            self.gross_price_pnl_points != expected_points
            or self.gross_price_pnl_usd != expected_gross_usd
            or self.total_commission_usd != expected_commission
            or self.net_realized_pnl_usd
            != _round_usd(expected_gross_usd - self.total_commission_usd)
        ):
            raise PullbackContractError("net PnL must use slipped prices minus commissions only")


def _no_fill_cost_result(
    *,
    event_kind: CostEventKind,
    side: PullbackSide | None,
) -> V1CostedFillResult:
    return V1CostedFillResult(
        event_kind=event_kind,
        status=CostApplicationStatus.NO_FILL,
        side=side,
        fill_quantity=0,
        base_fill_price=None,
        execution_price=None,
        slippage_ticks=0,
        slippage_points=Decimal(0),
        commission_usd=Decimal("0.00"),
    )


def _filled_cost_result(
    *,
    event_kind: CostEventKind,
    side: PullbackSide,
    base_fill_price: Decimal,
) -> V1CostedFillResult:
    if not isinstance(base_fill_price, Decimal) or not base_fill_price.is_finite():
        raise PullbackContractError("cost application requires a finite Decimal base fill")
    if base_fill_price < 0 or not _is_on_mnq_tick_grid(base_fill_price):
        raise PullbackContractError("base fill price must use the exact MNQ tick grid")
    slippage_ticks = _slippage_ticks_for_event(event_kind)
    slippage_points = MNQ_TICK_SIZE_POINTS * slippage_ticks
    is_entry = event_kind is CostEventKind.ENTRY
    adverse_sign = (
        Decimal(1)
        if (is_entry and side is PullbackSide.LONG) or (not is_entry and side is PullbackSide.SHORT)
        else Decimal(-1)
    )
    execution_price = base_fill_price + adverse_sign * slippage_points
    if execution_price < 0:
        raise PullbackContractError("adverse slippage cannot create a negative execution price")
    return V1CostedFillResult(
        event_kind=event_kind,
        status=CostApplicationStatus.FILLED,
        side=side,
        fill_quantity=1,
        base_fill_price=base_fill_price,
        execution_price=execution_price,
        slippage_ticks=slippage_ticks,
        slippage_points=slippage_points,
        commission_usd=_round_usd(COMMISSION_PER_SIDE_USD),
    )


def apply_v1_execution_costs(
    event: (
        NextBarExecutionResult
        | ProtectedEntryExecutionResult
        | InitialStopBarExecutionResult
        | ExitPriorityExecutionResult
        | OpenPositionSignalPolicyResult
        | EndOfDataPositionResult
    ),
) -> V1CostedFillResult:
    """Apply fixed adverse slippage and commission to an existing causal fill only."""
    if isinstance(event, NextBarExecutionResult):
        if not isinstance(event.purpose, SimulatedOrderPurpose) or not isinstance(
            event.side, PullbackSide
        ):
            raise PullbackContractError("next-bar cost event must identify purpose and side")
        event_kind = (
            CostEventKind.ENTRY
            if event.purpose is SimulatedOrderPurpose.ENTRY
            else CostEventKind.EMA20_EXIT
        )
        if event.status is SimulatedExecutionStatus.EXPIRED_NO_EXECUTION:
            if (
                event.execution_bar_sequence is not None
                or event.execution_price is not None
                or event.position_opened
                or event.position_closed
            ):
                raise PullbackContractError("expired execution cannot contain a hidden fill")
            return _no_fill_cost_result(event_kind=event_kind, side=event.side)
        if (
            event.status is not SimulatedExecutionStatus.FILLED
            or event.order_type is not SimulatedOrderType.MARKET
            or event.execution_bar_sequence != event.decision_bar_sequence + 1
            or not isinstance(event.execution_price, Decimal)
            or event.position_opened is not (event_kind is CostEventKind.ENTRY)
            or event.position_closed is not (event_kind is CostEventKind.EMA20_EXIT)
        ):
            raise PullbackContractError("next-bar event must be one coherent causal fill")
        return _filled_cost_result(
            event_kind=event_kind,
            side=event.side,
            base_fill_price=event.execution_price,
        )

    if isinstance(event, ProtectedEntryExecutionResult):
        if (
            not isinstance(event.side, PullbackSide)
            or event.order_type is not SimulatedOrderType.MARKET
        ):
            raise PullbackContractError("protected entry cost event must identify side and MARKET")
        if event.status in (
            SimulatedExecutionStatus.EXPIRED_NO_EXECUTION,
            SimulatedExecutionStatus.REJECT_ENTRY,
        ):
            if event.entry_price is not None or event.position_opened:
                raise PullbackContractError("rejected or expired entry cannot contain a fill")
            return _no_fill_cost_result(event_kind=CostEventKind.ENTRY, side=event.side)
        if (
            event.status is not SimulatedExecutionStatus.FILLED
            or event.position_opened is not True
            or event.execution_bar_sequence != event.decision_bar_sequence + 1
            or not isinstance(event.entry_price, Decimal)
        ):
            raise PullbackContractError("protected entry must be one coherent causal fill")
        return _filled_cost_result(
            event_kind=CostEventKind.ENTRY,
            side=event.side,
            base_fill_price=event.entry_price,
        )

    if isinstance(event, InitialStopBarExecutionResult):
        if not isinstance(event.side, PullbackSide) or not isinstance(
            event.fill_source, InitialStopFillSource
        ):
            raise PullbackContractError("stop cost event must identify side and fill source")
        if event.status is InitialStopTriggerStatus.NOT_TRIGGERED:
            if event.fill_price is not None or event.position_closed:
                raise PullbackContractError("inactive stop cannot contain a hidden fill")
            return _no_fill_cost_result(
                event_kind=CostEventKind.STRUCTURAL_STOP,
                side=event.side,
            )
        if (
            event.status is not InitialStopTriggerStatus.STOP_TRIGGERED
            or event.position_closed is not True
            or not isinstance(event.fill_price, Decimal)
            or event.fill_source is InitialStopFillSource.NONE
        ):
            raise PullbackContractError("triggered stop must contain one coherent fill")
        return _filled_cost_result(
            event_kind=CostEventKind.STRUCTURAL_STOP,
            side=event.side,
            base_fill_price=event.fill_price,
        )

    if isinstance(event, ExitPriorityExecutionResult):
        event_kind = (
            CostEventKind.STRUCTURAL_STOP
            if event.exit_reason is PositionExitReason.STRUCTURAL_STOP
            else CostEventKind.EMA20_EXIT
        )
        return _filled_cost_result(
            event_kind=event_kind,
            side=event.side,
            base_fill_price=event.fill_price,
        )

    if isinstance(event, OpenPositionSignalPolicyResult):
        if event.action is not OpenPositionSignalAction.IGNORE:
            raise PullbackContractError("cost layer accepts only the explicit ignored-signal case")
        side = PullbackSide(event.position_state.value)
        return _no_fill_cost_result(event_kind=CostEventKind.IGNORED_SIGNAL, side=side)

    if isinstance(event, EndOfDataPositionResult):
        if event.synthetic_fill or event.fill_price is not None:
            raise PullbackContractError("end-of-data mark cannot contain a hidden fill")
        return _no_fill_cost_result(
            event_kind=CostEventKind.END_OF_DATA_MARK,
            side=event.position_side,
        )

    raise PullbackContractError("unsupported event cannot enter the V1 cost layer")


def calculate_v1_realized_trade_pnl(
    *,
    entry_fill: V1CostedFillResult,
    exit_fill: V1CostedFillResult,
) -> V1RealizedTradePnL:
    """Calculate net USD PnL without charging spread or slippage a second time."""
    if (
        not isinstance(entry_fill, V1CostedFillResult)
        or entry_fill.status is not CostApplicationStatus.FILLED
        or entry_fill.event_kind is not CostEventKind.ENTRY
        or not isinstance(entry_fill.side, PullbackSide)
        or entry_fill.execution_price is None
    ):
        raise PullbackContractError("realized trade requires one costed entry fill")
    if (
        not isinstance(exit_fill, V1CostedFillResult)
        or exit_fill.status is not CostApplicationStatus.FILLED
        or exit_fill.event_kind not in (CostEventKind.EMA20_EXIT, CostEventKind.STRUCTURAL_STOP)
        or exit_fill.side is not entry_fill.side
        or exit_fill.execution_price is None
    ):
        raise PullbackContractError("realized trade requires one matching costed exit fill")
    gross_points = (
        exit_fill.execution_price - entry_fill.execution_price
        if entry_fill.side is PullbackSide.LONG
        else entry_fill.execution_price - exit_fill.execution_price
    )
    gross_usd = _round_usd(gross_points * MNQ_POINT_VALUE_USD)
    total_commission = _round_usd(entry_fill.commission_usd + exit_fill.commission_usd)
    return V1RealizedTradePnL(
        side=entry_fill.side,
        quantity=1,
        entry_execution_price=entry_fill.execution_price,
        exit_execution_price=exit_fill.execution_price,
        gross_price_pnl_points=gross_points,
        gross_price_pnl_usd=gross_usd,
        total_commission_usd=total_commission,
        net_realized_pnl_usd=_round_usd(gross_usd - total_commission),
    )


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


def evaluate_disabled_breakeven(
    *,
    position: ProtectedEntryExecutionResult,
    observed_market_price: Decimal,
    favorable_ticks: Decimal,
    favorable_r_multiple: Decimal,
    unrealized_pnl: Decimal,
    elapsed_closed_bars: int,
) -> BreakevenEvaluationResult:
    """Keep the exact initial stop regardless of favorable movement or time.

    The observations make every prohibited implicit trigger directly testable.  They may
    describe profit, retracement, any tick distance, any ``R`` multiple, monetary PnL or
    elapsed closed bars, but none can replace or move the initial structural stop.  No bar
    after the current observation is accepted, so this pure rule has no lookahead input.
    """
    if not isinstance(position, ProtectedEntryExecutionResult):
        raise PullbackContractError("breakeven evaluation requires a protected entry result")
    if (
        position.status is not SimulatedExecutionStatus.FILLED
        or position.position_opened is not True
        or not isinstance(position.side, PullbackSide)
    ):
        raise PullbackContractError("breakeven evaluation requires an opened position")
    if (
        not isinstance(position.entry_price, Decimal)
        or not position.entry_price.is_finite()
        or position.entry_price < 0
    ):
        raise PullbackContractError("breakeven evaluation requires a valid entry price")
    if (
        not isinstance(position.initial_stop, InitialStructuralStop)
        or position.initial_stop.side is not position.side
        or position.initial_stop.immutable is not True
    ):
        raise PullbackContractError("breakeven evaluation requires the immutable initial stop")
    if (
        not isinstance(observed_market_price, Decimal)
        or not observed_market_price.is_finite()
        or observed_market_price < 0
    ):
        raise PullbackContractError("observed_market_price must be a finite non-negative Decimal")
    for field_name, value in (
        ("favorable_ticks", favorable_ticks),
        ("favorable_r_multiple", favorable_r_multiple),
    ):
        if not isinstance(value, Decimal) or not value.is_finite() or value < 0:
            raise PullbackContractError(f"{field_name} must be a finite non-negative Decimal")
    if not isinstance(unrealized_pnl, Decimal) or not unrealized_pnl.is_finite():
        raise PullbackContractError("unrealized_pnl must be a finite Decimal")
    if (
        isinstance(elapsed_closed_bars, bool)
        or not isinstance(elapsed_closed_bars, int)
        or elapsed_closed_bars < 0
    ):
        raise PullbackContractError("elapsed_closed_bars must be a non-negative integer")

    return BreakevenEvaluationResult(
        position_side=position.side,
        initial_stop=position.initial_stop,
        active_stop=position.initial_stop,
    )


def evaluate_disabled_trailing_stop(
    *,
    position: ProtectedEntryExecutionResult,
    observed_high: Decimal,
    observed_low: Decimal,
    observed_close: Decimal,
    observed_ema20: Decimal,
    favorable_ticks: Decimal,
    favorable_r_multiple: Decimal,
    unrealized_pnl: Decimal,
    elapsed_closed_bars: int,
) -> TrailingStopEvaluationResult:
    """Keep the exact initial stop regardless of closed-bar favorable observations.

    The scalar observations expose every prohibited implicit trailing source: new highs
    or lows, profit, ticks, ``R`` multiples, EMA20, and time.  No sequence or future bar
    collection is accepted, so the rule cannot scan ahead.  None of these inputs may
    replace, recalculate, or move the initial structural stop.
    """
    if not isinstance(position, ProtectedEntryExecutionResult):
        raise PullbackContractError("trailing evaluation requires a protected entry result")
    if (
        position.status is not SimulatedExecutionStatus.FILLED
        or position.position_opened is not True
        or not isinstance(position.side, PullbackSide)
    ):
        raise PullbackContractError("trailing evaluation requires an opened position")
    if (
        not isinstance(position.initial_stop, InitialStructuralStop)
        or position.initial_stop.side is not position.side
        or position.initial_stop.immutable is not True
    ):
        raise PullbackContractError("trailing evaluation requires the immutable initial stop")
    for field_name, value in (
        ("observed_high", observed_high),
        ("observed_low", observed_low),
        ("observed_close", observed_close),
        ("observed_ema20", observed_ema20),
    ):
        if not isinstance(value, Decimal) or not value.is_finite() or value < 0:
            raise PullbackContractError(f"{field_name} must be a finite non-negative Decimal")
    if observed_low > observed_high:
        raise PullbackContractError("observed_low must not exceed observed_high")
    if not observed_low <= observed_close <= observed_high:
        raise PullbackContractError("observed_close must be inside the observed range")
    for field_name, value in (
        ("favorable_ticks", favorable_ticks),
        ("favorable_r_multiple", favorable_r_multiple),
    ):
        if not isinstance(value, Decimal) or not value.is_finite() or value < 0:
            raise PullbackContractError(f"{field_name} must be a finite non-negative Decimal")
    if not isinstance(unrealized_pnl, Decimal) or not unrealized_pnl.is_finite():
        raise PullbackContractError("unrealized_pnl must be a finite Decimal")
    if (
        isinstance(elapsed_closed_bars, bool)
        or not isinstance(elapsed_closed_bars, int)
        or elapsed_closed_bars < 0
    ):
        raise PullbackContractError("elapsed_closed_bars must be a non-negative integer")

    return TrailingStopEvaluationResult(
        position_side=position.side,
        initial_stop=position.initial_stop,
        active_stop=position.initial_stop,
    )


def evaluate_disabled_session_filter(
    *,
    source_bar_sequence: int,
    source_bar_closed: bool,
    source_bar_valid: bool,
    source_trading_hours_template: str,
) -> SessionFilterEvaluationResult:
    """Admit every closed valid source bar without consulting a strategy clock.

    The caller must first establish that the bar belongs to the governed source stream
    and its ``CME US Index Futures ETH`` calendar.  This function intentionally accepts
    no timestamp, weekday, local timezone, or DST input, and it performs no conversion.
    Consequently it cannot hide an additional strategy session boundary or look ahead
    to another bar.  It returns entry eligibility and keeps both V1 exits active.
    """
    return SessionFilterEvaluationResult(
        source_bar_sequence=source_bar_sequence,
        source_trading_hours_template=source_trading_hours_template,
        source_bar_closed=source_bar_closed,
        source_bar_valid=source_bar_valid,
    )


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
    "ADD_TO_POSITION",
    "ALLOWED_WEEKDAYS",
    "ANTI_MARTINGALE",
    "BAR_BASED_EXECUTION_MODEL",
    "BID_ASK_SPREAD_MODELED",
    "BREAKEVEN",
    "BREAKEVEN_DURATION_BARS_TRIGGER",
    "BREAKEVEN_FAVORABLE_TICKS_TRIGGER",
    "BREAKEVEN_MONETARY_PNL_TRIGGER",
    "BREAKEVEN_PRICE",
    "BREAKEVEN_R_MULTIPLE_TRIGGER",
    "BREAKEVEN_TRIGGER",
    "CLOSE_AND_REVERSE",
    "COMMISSION_PER_SIDE_USD",
    "COMMISSION_SOURCE_URL",
    "CONFIRMATION_CLOSE_CORRECT_SIDE_REQUIRED",
    "COST_MODEL_CLASSIFICATION",
    "COST_MODEL_ID",
    "COST_MODEL_REFERENCE_DATE",
    "COST_MODEL_VERSION",
    "DEFERRED_ENTRY",
    "DST_RULE",
    "EARLIEST_EXECUTION_BAR_OFFSET",
    "EMA20_EXIT_SLIPPAGE_TICKS",
    "EMA_PERIOD",
    "EMA_SEED_CONVENTION",
    "EMA_SLOPE_LOOKBACK_BARS",
    "EMA_SLOPE_REQUIRED",
    "END_OF_DATA_ACCOUNTING_UNIT",
    "END_OF_DATA_FORCED_EXIT",
    "END_OF_DATA_POSITION_POLICY",
    "END_OF_DATA_SYNTHETIC_FILL",
    "ENTRY_SLIPPAGE_TICKS",
    "EXECUTION_PRICE_SOURCE",
    "EXECUTION_SIGNAL_TIME",
    "EXIT_PRIORITY",
    "EXPLICIT_BID_ASK_SPREAD_CHARGE",
    "FEE_APPLICATION",
    "GAP_THROUGH_STOP_FILLS_AT_BAR_OPEN",
    "INITIAL_POSITION_SIZE",
    "INITIAL_STOP_BUFFER_POINTS",
    "INITIAL_STOP_BUFFER_TICKS",
    "INITIAL_STOP_IS_IMMUTABLE",
    "INITIAL_STOP_SOURCE_BAR_OFFSET",
    "INITIAL_STRUCTURAL_STOP_IS_IMMUTABLE",
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
    "MARTINGALE",
    "MAX_POSITION_SIZE",
    "MAX_PULLBACK_DISTANCE_POINTS",
    "MAX_PULLBACK_DISTANCE_TICKS",
    "MINIMUM_EMA_SLOPE_POINTS_PER_BAR",
    "MNQ_CONTRACT_SPEC_SOURCE_URL",
    "MNQ_POINT_VALUE_USD",
    "MNQ_TICK_SIZE_POINTS",
    "MNQ_TICK_VALUE_USD",
    "MOVE_STOP_TO_ENTRY",
    "OPEN_POSITION_SIGNAL_POLICY",
    "PNL_BASED_SIZING",
    "POSITION_EXIT_EQUALITY_TRIGGERS_EXIT",
    "POSITION_EXIT_WICK_ONLY_TRIGGERS_EXIT",
    "POSITION_SIZE_MODE",
    "PULLBACK_LOOKBACK_BARS",
    "PULLBACK_PROXIMITY_QUALIFIES",
    "PULLBACK_REQUIRED_TOUCH_BAR_OFFSET",
    "QUEUE_SIGNAL_UNTIL_FLAT",
    "REVERSE_POSITION",
    "RISK_PERCENT_SIZING",
    "ROUNDING_POLICY",
    "SCALE_IN",
    "SEPARATE_SLIPPAGE_CHARGE_USD",
    "SEPARATE_SPREAD_CHARGE_USD",
    "SESSION_END",
    "SESSION_FILTER",
    "SESSION_START",
    "SIGNAL_DECISION_ON_CLOSED_BAR",
    "SLIPPAGE_EMBEDDED_IN_EXECUTION_PRICE",
    "SLIPPAGE_MODELED",
    "SOURCE_CALENDAR_REQUIRED",
    "SOURCE_TRADING_HOURS_TEMPLATE",
    "SPREAD_MODEL",
    "STOP_DISTANCE_SIZING",
    "STOP_INTRABAR_SLIPPAGE_MODELED",
    "STRATEGY_ENTRY_SESSION_FILTER_ENABLED",
    "STRATEGY_ID",
    "STRATEGY_TIMEZONE",
    "STRUCTURAL_STOP_FIRST",
    "STRUCTURAL_STOP_SLIPPAGE_TICKS",
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
    "TRAILING_ACTIVATION",
    "TRAILING_DISTANCE",
    "TRAILING_REFERENCE",
    "TRAILING_STEP",
    "TRAILING_STOP",
    "TRAILING_STOP_ENABLED",
    "TRAILING_UPDATE_FREQUENCY",
    "UNREALIZED_PNL_AFFECTS_CLOSED_TRADE_METRICS",
    "UNREALIZED_PNL_IS_REALIZED",
    "USD_CENT",
    "VOLATILITY_SIZING",
    "WICK_CROSS_EMA20_ALLOWED",
    "BreakevenEvaluationResult",
    "ClosedBarEMA20",
    "CostApplicationStatus",
    "CostEventKind",
    "EMA20PositionExitResult",
    "EMA20SlopeResult",
    "EMAPullbackEntrySignalResult",
    "EndOfDataPositionResult",
    "EndOfDataPositionState",
    "EntrySignal",
    "ExitPriorityExecutionResult",
    "FixedPositionSizeResult",
    "InitialStopBarExecutionResult",
    "InitialStopFillSource",
    "InitialStopTriggerStatus",
    "InitialStructuralStop",
    "MACDCrossResult",
    "MACDStatus",
    "NextBarExecutionResult",
    "NextBarOpen",
    "OpenPositionSignalAction",
    "OpenPositionSignalPolicyResult",
    "PositionExitAction",
    "PositionExitReason",
    "PositionSizeTransition",
    "PositionState",
    "ProtectedEntryExecutionResult",
    "PullbackContractError",
    "PullbackPredicateResult",
    "PullbackSide",
    "SessionFilterEvaluationResult",
    "SimulatedExecutionStatus",
    "SimulatedOrderPurpose",
    "SimulatedOrderType",
    "StopEvaluationBar",
    "TakeProfitEvaluationResult",
    "TrailingStopEvaluationResult",
    "V1CostedFillResult",
    "V1RealizedTradePnL",
    "apply_v1_execution_costs",
    "arbitrate_exit_at_open",
    "assemble_ema_pullback_entry_signal",
    "calculate_v1_realized_trade_pnl",
    "construct_initial_structural_stop",
    "distance_from_bar_range_to_ema20",
    "evaluate_disabled_breakeven",
    "evaluate_disabled_session_filter",
    "evaluate_disabled_take_profit",
    "evaluate_disabled_trailing_stop",
    "evaluate_ema20_position_exit",
    "evaluate_ema20_slope",
    "evaluate_ema_pullback_entry_signal",
    "evaluate_end_of_data_position",
    "evaluate_fixed_position_size",
    "evaluate_initial_stop_on_bar",
    "evaluate_macd_confirmation",
    "evaluate_open_position_signal_policy",
    "evaluate_pullback_confirmation",
    "initial_stop_triggered_by_market_price",
    "simulate_entry_with_initial_structural_stop",
    "simulate_next_bar_market_execution",
]
