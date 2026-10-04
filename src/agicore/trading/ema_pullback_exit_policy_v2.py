"""Two deterministic offline exits: the frozen stop and a next-Open EMA20 exit.

Call the Open phase before the completed adverse-range/Close phase. A stop
opening gap wins before a pending MARKET exit; an actual EMA fill prevents
reading the later range. This boundary does not assemble or replay a strategy.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from enum import StrEnum
from fractions import Fraction
from types import SimpleNamespace
from typing import TYPE_CHECKING

from .ema20_pullback_v2 import (
    EMA20EvaluationV2,
    EMA20PullbackBarV2,
    EMA20StatusV2,
    _exact_price,
    evaluate_ema20_v2,
)
from .ema_pullback_entry_execution_v2 import _confirmation_key, _valid_utc
from .ema_pullback_initial_stop_v2 import InitialStopAtEntryV2
from .ema_pullback_structural_stop_trigger_fill_v2 import (
    ProtectiveStopActionV2,
    StructuralStopExecutionBookV2,
    StructuralStopExecutionStateV2,
    StructuralStopOpenInputV2,
)
from .regime_context_v2 import RegimeDirection

if TYPE_CHECKING:
    from .ema_pullback_fees_and_slippage_v2 import FeesAndSlippageBookV2
    from .ema_pullback_open_position_signal_policy_v2 import OpenPositionSignalPolicyBookV2
    from .ema_pullback_risk_position_sizing_v2 import RiskPositionSizingBookV2

EXIT_1 = "IMMUTABLE_STRUCTURAL_STOP"
EXIT_2 = "EMA20_POSITION_EXIT"
TAKE_PROFIT = None
BREAKEVEN = None
TRAILING_STOP = None
TIME_EXIT = None
SESSION_EXIT = None
MAX_EXIT_EXECUTION_AGE_CLOSED_BARS = 1
MAX_EXIT_EXECUTION_ELAPSED_TIME = timedelta(minutes=1)
EXIT_ORDER_SEMANTICS = "MARKET"


class ExitPolicyV2Error(ValueError):
    """Refuse inconsistent position provenance or out-of-order phase processing."""


class EMA20ExitExecutionStateV2(StrEnum):
    """One signal authorizes only its next observed index, without resurrection."""

    PENDING_EMA20_EXIT = "PENDING_EMA20_EXIT"
    FILLED_EMA20_EXIT = "FILLED_EMA20_EXIT"
    CANCELLED_STRUCTURAL_STOP = "CANCELLED_STRUCTURAL_STOP"
    EXPIRED_NO_EXIT_EXECUTION = "EXPIRED_NO_EXIT_EXECUTION"
    EXPIRED_EXIT_GAP = "EXPIRED_EXIT_GAP"
    FAILED_INVALID_EXIT_INPUT = "FAILED_INVALID_EXIT_INPUT"
    FAILED_STOP_OBSERVATION = "FAILED_STOP_OBSERVATION"


class ExitPolicyEndStateV2(StrEnum):
    FLAT = "FLAT"
    OPEN_UNREALIZED = "OPEN_UNREALIZED"


@dataclass(frozen=True)
class EMA20ExitSignalRecordV2:
    """Strict current-Close/current-EMA signal with the complete immutable source."""

    initial_stop_at_entry: InitialStopAtEntryV2
    quantity: int
    exit_signal_bar_index: int
    exit_signal_timestamp: datetime
    close_at_signal: Fraction
    ema20_at_signal: Fraction
    exit_signal_type: str = EXIT_2

    def __post_init__(self) -> None:
        bound = self.initial_stop_at_entry
        if (
            not isinstance(bound, InitialStopAtEntryV2)
            or type(self.quantity) is not int
            or self.quantity not in (1, 2)
            or type(self.exit_signal_bar_index) is not int
            or self.exit_signal_bar_index < bound.entry_bar_index
            or not _valid_utc(self.exit_signal_timestamp)
            or self.exit_signal_timestamp < bound.entry_bar_timestamp
            or not isinstance(self.close_at_signal, Fraction)
            or not isinstance(self.ema20_at_signal, Fraction)
            or self.exit_signal_type != EXIT_2
        ):
            raise ExitPolicyV2Error("EMA signal requires its exact known position and Close")
        is_long = bound.execution.execution_side is RegimeDirection.LONG
        if not (
            self.close_at_signal < self.ema20_at_signal
            if is_long
            else self.close_at_signal > self.ema20_at_signal
        ):
            raise ExitPolicyV2Error("an EMA exit signal requires the strict directional comparison")


@dataclass(frozen=True)
class EMA20ExitFillRecordV2:
    """Actual sole next-Open MARKET exit, distinct from its signal and stop fill."""

    signal: EMA20ExitSignalRecordV2
    exit_execution_bar_index: int
    exit_execution_timestamp: datetime
    base_exit_fill_price: Fraction
    exit_reason: str = EXIT_2
    order_semantics: str = EXIT_ORDER_SEMANTICS

    def __post_init__(self) -> None:
        if (
            not isinstance(self.signal, EMA20ExitSignalRecordV2)
            or type(self.exit_execution_bar_index) is not int
            or self.exit_execution_bar_index != self.signal.exit_signal_bar_index + 1
            or not _valid_utc(self.exit_execution_timestamp)
            or not timedelta(0)
            < self.exit_execution_timestamp - self.signal.exit_signal_timestamp
            <= MAX_EXIT_EXECUTION_ELAPSED_TIME
            or not isinstance(self.base_exit_fill_price, Fraction)
            or self.base_exit_fill_price <= 0
            or self.exit_reason != EXIT_2
            or self.order_semantics != EXIT_ORDER_SEMANTICS
        ):
            raise ExitPolicyV2Error("EMA fill must be the valid next Open of the original signal")

    @property
    def initial_stop_at_entry(self) -> InitialStopAtEntryV2:
        """Retain entry and structural-stop provenance without changing either."""
        return self.signal.initial_stop_at_entry

    @property
    def quantity(self) -> int:
        """The approved quantity frozen before entry, unchanged by the exit."""
        return self.signal.quantity

    @property
    def protective_action(self) -> ProtectiveStopActionV2:
        """Close LONG by SELL and SHORT by BUY_TO_COVER, offline only."""
        return (
            ProtectiveStopActionV2.SELL
            if self.initial_stop_at_entry.execution.execution_side is RegimeDirection.LONG
            else ProtectiveStopActionV2.BUY_TO_COVER
        )


@dataclass(frozen=True)
class EMA20ExitExecutionEvaluationV2:
    """Terminal signal outcomes never become pending again."""

    signal: EMA20ExitSignalRecordV2
    state: EMA20ExitExecutionStateV2 = EMA20ExitExecutionStateV2.PENDING_EMA20_EXIT
    fill: EMA20ExitFillRecordV2 | None = None

    def __post_init__(self) -> None:
        if (
            not isinstance(self.signal, EMA20ExitSignalRecordV2)
            or not isinstance(self.state, EMA20ExitExecutionStateV2)
            or (self.state is EMA20ExitExecutionStateV2.FILLED_EMA20_EXIT)
            != (isinstance(self.fill, EMA20ExitFillRecordV2))
            or (self.fill is not None and self.fill.signal != self.signal)
        ):
            raise ExitPolicyV2Error("EMA execution must retain its original signal and actual fill")


@dataclass(frozen=True)
class EMA20PositionExitCloseV2:
    """An evaluated HOLD or signal; EMA warmup/invalid inputs cannot signal."""

    initial_stop_at_entry: InitialStopAtEntryV2
    closed_bar_index: int
    closed_bar_timestamp: datetime
    ema: EMA20EvaluationV2
    signal: EMA20ExitSignalRecordV2 | None = None

    def __post_init__(self) -> None:
        if (
            not isinstance(self.initial_stop_at_entry, InitialStopAtEntryV2)
            or type(self.closed_bar_index) is not int
            or self.closed_bar_index < self.initial_stop_at_entry.entry_bar_index
            or not _valid_utc(self.closed_bar_timestamp)
            or not isinstance(self.ema, EMA20EvaluationV2)
            or self.ema.through_bar_index != self.closed_bar_index
        ):
            raise ExitPolicyV2Error("Close decision must retain its own indexed EMA and position")
        if self.ema.status is not EMA20StatusV2.EVALUATED:
            if self.signal is not None:
                raise ExitPolicyV2Error("an unavailable EMA cannot create an exit signal")
            return
        is_long = self.initial_stop_at_entry.execution.execution_side is RegimeDirection.LONG
        qualifies = (
            self.ema.last_close < self.ema.ema20
            if is_long
            else self.ema.last_close > self.ema.ema20
        )
        if self.ema.known_at_timestamp != self.closed_bar_timestamp or qualifies != (
            self.signal is not None
        ):
            raise ExitPolicyV2Error("HOLD/signal must use this current Close and exact EMA")
        if self.signal is not None and (
            self.signal.initial_stop_at_entry != self.initial_stop_at_entry
            or self.signal.exit_signal_bar_index != self.closed_bar_index
            or self.signal.exit_signal_timestamp != self.closed_bar_timestamp
            or self.signal.close_at_signal != self.ema.last_close
            or self.signal.ema20_at_signal != self.ema.ema20
        ):
            raise ExitPolicyV2Error("signal provenance must match the evaluated Close")


@dataclass(frozen=True)
class ExitPolicyOpenSnapshotV2:
    """Only opening metadata and price cross into the next completed-range phase."""

    bar_index: int
    timestamp_utc: datetime
    open: Fraction


@dataclass(frozen=True)
class ExitPolicyBookV2:
    """Position, accounting and exit history for one immutable strategy/series scope."""

    positions: OpenPositionSignalPolicyBookV2
    risk_sizing: RiskPositionSizingBookV2
    costs: FeesAndSlippageBookV2
    close_decisions: tuple[EMA20PositionExitCloseV2, ...] = ()
    ema_executions: tuple[EMA20ExitExecutionEvaluationV2, ...] = ()
    latest_open: ExitPolicyOpenSnapshotV2 | None = None
    end_of_data: bool = False

    def __post_init__(self) -> None:
        from .ema_pullback_fees_and_slippage_v2 import FeesAndSlippageBookV2
        from .ema_pullback_open_position_signal_policy_v2 import OpenPositionSignalPolicyBookV2
        from .ema_pullback_risk_position_sizing_v2 import RiskPositionSizingBookV2

        if (
            not (
                isinstance(self.positions, OpenPositionSignalPolicyBookV2)
                and isinstance(self.risk_sizing, RiskPositionSizingBookV2)
                and isinstance(self.costs, FeesAndSlippageBookV2)
            )
            or len(
                {
                    (book.strategy_instance_id, book.series_id)
                    for book in (self.positions, self.risk_sizing, self.costs)
                }
            )
            != 1
        ):
            raise ExitPolicyV2Error("position, risk and costs must retain one canonical scope")
        for position in self.positions.positions:
            if not any(
                sized.execution == position.entry
                and sized.risk_decision.initial_stop_record
                == position.initial_stop_at_entry.initial_stop_record
                for sized in self.risk_sizing.filled_entries
            ):
                raise ExitPolicyV2Error("exit policy requires the actual risk-approved entry")
        if (
            not isinstance(self.close_decisions, tuple)
            or not isinstance(self.ema_executions, tuple)
            or not all(isinstance(item, EMA20PositionExitCloseV2) for item in self.close_decisions)
            or not all(
                isinstance(item, EMA20ExitExecutionEvaluationV2) for item in self.ema_executions
            )
        ):
            raise ExitPolicyV2Error("exit histories must be immutable canonical tuples")
        keys = [
            (
                _confirmation_key(item.signal.initial_stop_at_entry.execution.confirmation),
                item.signal.exit_signal_bar_index,
            )
            for item in self.ema_executions
        ]
        if len(keys) != len(set(keys)):
            raise ExitPolicyV2Error("one signal cannot create duplicate EMA exits")
        pending = [
            item
            for item in self.ema_executions
            if item.state is EMA20ExitExecutionStateV2.PENDING_EMA20_EXIT
        ]
        if len(pending) > 1:
            raise ExitPolicyV2Error("a position cannot stack pending EMA exits")
        for item in self.ema_executions:
            signal = item.signal
            if not any(
                sized.execution == signal.initial_stop_at_entry.execution
                and sized.quantity == signal.quantity
                and sized.risk_decision.initial_stop_record
                == signal.initial_stop_at_entry.initial_stop_record
                for sized in self.risk_sizing.filled_entries
            ) or not any(decision.signal == signal for decision in self.close_decisions):
                raise ExitPolicyV2Error(
                    "EMA execution must retain its evaluated Close and frozen quantity"
                )
        if pending and (
            self.positions.active_position is None
            or pending[0].signal.initial_stop_at_entry
            != self.positions.active_position.initial_stop_at_entry
        ):
            raise ExitPolicyV2Error("a pending EMA exit requires its still-open position")

    @property
    def pending_ema_exit(self) -> EMA20ExitExecutionEvaluationV2 | None:
        """At most one pending order, tied to the current open position."""
        return next(
            (
                item
                for item in reversed(self.ema_executions)
                if item.state is EMA20ExitExecutionStateV2.PENDING_EMA20_EXIT
            ),
            None,
        )

    @property
    def end_state(self) -> ExitPolicyEndStateV2:
        """An unfilled open position never becomes a synthetic realized trade."""
        return (
            ExitPolicyEndStateV2.OPEN_UNREALIZED
            if self.positions.active_position is not None
            else ExitPolicyEndStateV2.FLAT
        )


def begin_exit_policy_v2(
    *,
    positions: OpenPositionSignalPolicyBookV2,
    risk_sizing: RiskPositionSizingBookV2,
    costs: FeesAndSlippageBookV2 | None = None,
) -> ExitPolicyBookV2:
    """Bind actual position/risk provenance and account its already-realized entry fill."""
    from .ema_pullback_fees_and_slippage_v2 import FeesAndSlippageBookV2, account_entry_fill_v2

    costs = (
        costs
        if costs is not None
        else FeesAndSlippageBookV2(positions.strategy_instance_id, positions.series_id)
    )
    book = ExitPolicyBookV2(positions, risk_sizing, costs)
    if positions.active_position is not None:
        sized = _sized_entry(book)
        costs = account_entry_fill_v2(
            previous=costs, risk_sizing=risk_sizing, decision=sized.risk_decision
        )
    return replace(book, costs=costs)


def _sized_entry(book: ExitPolicyBookV2):
    position = book.positions.active_position
    return next(
        item for item in book.risk_sizing.filled_entries if item.execution == position.entry
    )


def _finish_pending(book, state, fill=None):
    pending = book.pending_ema_exit
    if pending is None:
        return book
    updated = replace(pending, state=state, fill=fill)
    return replace(
        book,
        ema_executions=tuple(updated if item is pending else item for item in book.ema_executions),
    )


def _resolve_stop(book, index, timestamp, observation=None):
    from .ema_pullback_fees_and_slippage_v2 import account_structural_stop_fill_v2
    from .ema_pullback_open_position_signal_policy_v2 import resolve_position_stop_v2
    from .ema_pullback_structural_stop_trigger_fill_v2 import observe_structural_stop_v2

    sized = _sized_entry(book)
    stop = observe_structural_stop_v2(
        previous=StructuralStopExecutionBookV2((book.positions.active_stop,)),
        confirmation=book.positions.active_position.entry.confirmation,
        observation=observation,
    ).entries[0]
    positions = resolve_position_stop_v2(
        previous=replace(book.positions, active_stop=stop),
        known_bar_index=index,
        known_bar_timestamp=timestamp,
    )
    if positions.active_position is None:
        costs = account_structural_stop_fill_v2(
            previous=book.costs,
            risk_sizing=book.risk_sizing,
            decision=sized.risk_decision,
            stops=StructuralStopExecutionBookV2((stop,)),
        )
        book = _finish_pending(book, EMA20ExitExecutionStateV2.CANCELLED_STRUCTURAL_STOP)
        return replace(book, positions=positions, costs=costs)
    book = replace(book, positions=positions)
    if positions.active_stop.stop_execution_state is not StructuralStopExecutionStateV2.ARMED:
        return _finish_pending(book, EMA20ExitExecutionStateV2.FAILED_STOP_OBSERVATION)
    return book


def _fail_stop_observation(book, observation):
    from .ema_pullback_structural_stop_trigger_fill_v2 import observe_structural_stop_v2

    stop = observe_structural_stop_v2(
        previous=StructuralStopExecutionBookV2((book.positions.active_stop,)),
        confirmation=book.positions.active_position.entry.confirmation,
        observation=observation,
    ).entries[0]
    current = replace(book, positions=replace(book.positions, active_stop=stop))
    return _finish_pending(current, EMA20ExitExecutionStateV2.FAILED_STOP_OBSERVATION)


def process_exit_policy_open_v2(
    *,
    previous: ExitPolicyBookV2,
    observation: StructuralStopOpenInputV2 | None,
) -> ExitPolicyBookV2:
    """Stop gap -> pending EMA fill -> leave the adverse range for its later phase.

    No High/Low/Close/Volume is read here, even when the complete OHLC is in
    memory. Missing next index expires its MARKET signal; the frozen stop's
    own indexed-observation and clock rules still apply. Time gaps never expire
    the stop. Identical repeated phase processing cannot create another fill.
    """
    if not isinstance(previous, ExitPolicyBookV2):
        raise ExitPolicyV2Error("Open processing requires the current exit policy book")
    position = previous.positions.active_position
    if position is None or previous.end_of_data:
        return previous
    stop = previous.positions.active_stop
    if stop.stop_execution_state is StructuralStopExecutionStateV2.FILLED_STOP:
        return _resolve_stop(
            previous, position.entry.execution_bar_index, position.entry.execution_bar_timestamp
        )
    if stop.stop_execution_state is not StructuralStopExecutionStateV2.ARMED:
        return previous
    if observation is None:
        return _finish_pending(previous, EMA20ExitExecutionStateV2.EXPIRED_NO_EXIT_EXECUTION)
    index = getattr(observation, "bar_index", None)
    if previous.latest_open is not None and index == previous.latest_open.bar_index:
        return previous
    pending = previous.pending_ema_exit
    if (
        pending is not None
        and type(index) is int
        and index > pending.signal.exit_signal_bar_index + 1
    ):
        previous = _finish_pending(previous, EMA20ExitExecutionStateV2.EXPIRED_NO_EXIT_EXECUTION)
    if type(index) is not int or index != stop.next_observation_bar_index:
        # Let PR #293 record the same terminal indexed-observation failure.
        return _fail_stop_observation(previous, SimpleNamespace(bar_index=index))
    timestamp = getattr(observation, "timestamp_utc", None)
    if (
        not _valid_utc(timestamp)
        or (
            index == position.entry.execution_bar_index
            and timestamp != position.entry.execution_bar_timestamp
        )
        or (
            stop.last_observed_bar_timestamp is not None
            and timestamp <= stop.last_observed_bar_timestamp
        )
    ):
        # Validation failures are terminal in the existing stop observer.
        return _fail_stop_observation(
            previous, SimpleNamespace(bar_index=index, timestamp_utc=timestamp)
        )
    opening = (
        position.entry.execution_price_before_costs
        if index == position.entry.execution_bar_index
        else _exact_price(getattr(observation, "open", None))
    )
    safe_open = SimpleNamespace(bar_index=index, timestamp_utc=timestamp, open=opening)
    if opening is None:
        previous = _finish_pending(previous, EMA20ExitExecutionStateV2.FAILED_INVALID_EXIT_INPUT)
        return _resolve_stop(previous, index, timestamp, safe_open)
    is_long = position.entry.execution_side is RegimeDirection.LONG
    level = position.initial_stop_at_entry.initial_stop_record.initial_stop_price
    if index > position.entry.execution_bar_index and (
        opening <= level if is_long else opening >= level
    ):
        return _resolve_stop(previous, index, timestamp, safe_open)
    current = replace(previous, latest_open=ExitPolicyOpenSnapshotV2(index, timestamp, opening))
    pending = current.pending_ema_exit
    if pending is None:
        return current
    if timestamp - pending.signal.exit_signal_timestamp > MAX_EXIT_EXECUTION_ELAPSED_TIME:
        return _finish_pending(current, EMA20ExitExecutionStateV2.EXPIRED_EXIT_GAP)
    if opening <= 0:
        return _finish_pending(current, EMA20ExitExecutionStateV2.FAILED_INVALID_EXIT_INPUT)
    fill = EMA20ExitFillRecordV2(pending.signal, index, timestamp, opening)
    from .ema_pullback_fees_and_slippage_v2 import account_ema20_exit_fill_v2

    sized = _sized_entry(current)
    closed = replace(position, exit=fill)
    positions = replace(
        current.positions, positions=(*current.positions.positions[:-1], closed), active_stop=None
    )
    costs = account_ema20_exit_fill_v2(
        previous=current.costs,
        risk_sizing=current.risk_sizing,
        decision=sized.risk_decision,
        positions=positions,
    )
    current = _finish_pending(current, EMA20ExitExecutionStateV2.FILLED_EMA20_EXIT, fill)
    return replace(current, positions=positions, costs=costs)


def process_exit_policy_close_v2(
    *,
    previous: ExitPolicyBookV2,
    closed_bar_index: int,
    closed_bar_timestamp: datetime,
    source_bar_closed: bool,
    bars_by_index: Mapping[int, EMA20PullbackBarV2],
    stop_observation: object,
) -> ExitPolicyBookV2:
    """Complete the stop observation first, then signal using Close[r]/EMA20[r]."""
    if not isinstance(previous, ExitPolicyBookV2):
        raise ExitPolicyV2Error("Close processing requires the current exit policy book")
    position = previous.positions.active_position
    if position is None or previous.end_of_data:
        return previous
    if previous.close_decisions and (
        previous.close_decisions[-1].closed_bar_index == closed_bar_index
        and previous.close_decisions[-1].closed_bar_timestamp == closed_bar_timestamp
    ):
        return previous
    opening = previous.latest_open
    if (
        source_bar_closed is not True
        or opening is None
        or (opening.bar_index != closed_bar_index or opening.timestamp_utc != closed_bar_timestamp)
    ):
        raise ExitPolicyV2Error("a closed exit observation must follow its own processed Open")
    if (
        previous.positions.active_stop.stop_execution_state
        is not StructuralStopExecutionStateV2.ARMED
    ):
        return previous
    is_long = position.entry.execution_side is RegimeDirection.LONG
    # The adverse extreme is available now. Open is the immutable earlier snapshot.
    adverse_name = "low" if is_long else "high"
    if (
        getattr(stop_observation, "bar_index", None) != closed_bar_index
        or getattr(stop_observation, "timestamp_utc", None) != closed_bar_timestamp
    ):
        raise ExitPolicyV2Error("the completed stop observation must belong to this exact bar")
    observation = SimpleNamespace(
        bar_index=closed_bar_index,
        timestamp_utc=closed_bar_timestamp,
        open=opening.open,
        **{adverse_name: getattr(stop_observation, adverse_name, None)},
    )
    current = _resolve_stop(previous, closed_bar_index, closed_bar_timestamp, observation)
    if current.positions.active_position is None or (
        current.positions.active_stop.stop_execution_state
        is not StructuralStopExecutionStateV2.ARMED
    ):
        return current
    ema = evaluate_ema20_v2(through_bar_index=closed_bar_index, bars_by_index=bars_by_index)
    signal = None
    if ema.status is EMA20StatusV2.EVALUATED:
        if ema.known_at_timestamp != closed_bar_timestamp:
            raise ExitPolicyV2Error("the current EMA must be known at this exact Close")
        qualifies = ema.last_close < ema.ema20 if is_long else ema.last_close > ema.ema20
        if qualifies:
            signal = EMA20ExitSignalRecordV2(
                position.initial_stop_at_entry,
                _sized_entry(current).quantity,
                closed_bar_index,
                closed_bar_timestamp,
                ema.last_close,
                ema.ema20,
            )
    decision = EMA20PositionExitCloseV2(
        position.initial_stop_at_entry, closed_bar_index, closed_bar_timestamp, ema, signal
    )
    return replace(
        current,
        close_decisions=(*current.close_decisions, decision),
        ema_executions=current.ema_executions
        if signal is None
        else (*current.ema_executions, EMA20ExitExecutionEvaluationV2(signal)),
    )


def finish_exit_policy_v2(*, previous: ExitPolicyBookV2) -> ExitPolicyBookV2:
    """Expire an unexecuted EMA order at end of data, preserving an unrealized position."""
    if not isinstance(previous, ExitPolicyBookV2):
        raise ExitPolicyV2Error("end of data requires the current exit policy book")
    if previous.end_of_data:
        return previous
    if (
        previous.positions.active_position is not None
        and previous.positions.active_stop.stop_triggered
    ):
        fill = previous.positions.active_stop.fill
        previous = _resolve_stop(previous, fill.trigger_bar_index, fill.trigger_bar_timestamp)
    current = _finish_pending(previous, EMA20ExitExecutionStateV2.EXPIRED_NO_EXIT_EXECUTION)
    return replace(current, end_of_data=True)


__all__ = [
    "BREAKEVEN",
    "EXIT_1",
    "EXIT_2",
    "EXIT_ORDER_SEMANTICS",
    "MAX_EXIT_EXECUTION_AGE_CLOSED_BARS",
    "MAX_EXIT_EXECUTION_ELAPSED_TIME",
    "SESSION_EXIT",
    "TAKE_PROFIT",
    "TIME_EXIT",
    "TRAILING_STOP",
    "EMA20ExitExecutionEvaluationV2",
    "EMA20ExitExecutionStateV2",
    "EMA20ExitFillRecordV2",
    "EMA20ExitSignalRecordV2",
    "EMA20PositionExitCloseV2",
    "ExitPolicyBookV2",
    "ExitPolicyEndStateV2",
    "ExitPolicyV2Error",
    "begin_exit_policy_v2",
    "finish_exit_policy_v2",
    "process_exit_policy_close_v2",
    "process_exit_policy_open_v2",
]
