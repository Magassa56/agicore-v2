"""Handoff from native V2 confirmation, entry and initial stop to exit execution.

This adapter operates on already invented, validated observations. It reads no
file or external service, connects no broker and submits no live orders.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from fractions import Fraction
from types import SimpleNamespace

from .ema20_pullback_v2 import EMA20PullbackBarV2, EMA20StatusV2, _exact_price, evaluate_ema20_v2
from .ema_pullback_entry_confirmation_v2 import EntryConfirmationEvaluationV2
from .ema_pullback_entry_execution_v2 import (
    EntryExecutionBookV2,
    EntryExecutionEvaluationV2,
    EntryExecutionStateV2,
    EntryExecutionStatusV2,
    _valid_utc,
)
from .ema_pullback_exit_policy_v2 import (
    MAX_EXIT_EXECUTION_ELAPSED_TIME,
    EMA20ExitExecutionEvaluationV2,
    EMA20ExitExecutionStateV2,
    EMA20ExitFillRecordV2,
    EMA20ExitSignalRecordV2,
    EMA20PositionExitCloseV2,
    ExitPolicyEndStateV2,
    ExitPolicyV2Error,
)
from .ema_pullback_initial_stop_v2 import (
    InitialStopBookV2,
    InitialStopEvaluationV2,
    InitialStopRecordV2,
    InitialStopStatusV2,
)
from .ema_pullback_open_position_signal_policy_v2 import (
    OpenPositionSignalPolicyBookV2,
    PositionRecordV2,
    resolve_position_stop_v2,
)
from .ema_pullback_risk_position_sizing_v2 import (
    RiskPositionSizingBookV2,
    RiskPositionSizingV2Error,
    RiskSizedEntryRecordV2,
    RiskSizingDecisionRecordV2,
    RiskSizingDecisionV2,
)
from .ema_pullback_structural_stop_trigger_fill_v2 import (
    StructuralStopExecutionBookV2,
    StructuralStopExecutionStateV2,
    StructuralStopFillRecordV2,
    register_structural_stop_execution_v2,
)
from .regime_context_v2 import RegimeDirection
from .synthetic_confirmation_replay_v2 import ClosedPrefix
from .synthetic_entry_handoff_v2 import _validate_risk_decision
from .synthetic_stop_handoff_v2 import _validate_native_confirmation


def _validate_exit_stop(
    stop: InitialStopEvaluationV2, confirmation: EntryConfirmationEvaluationV2
) -> None:
    """Ensure stop evaluation is native, evaluated, and provenance-consistent."""
    if not isinstance(stop, InitialStopEvaluationV2):
        raise TypeError("initial stop must be an InitialStopEvaluationV2 instance")
    if stop.status is not InitialStopStatusV2.EVALUATED or stop.initial_stop_record is None:
        raise RiskPositionSizingV2Error("initial stop must be evaluated before exit")
    record = stop.initial_stop_record
    if not isinstance(record, InitialStopRecordV2):
        raise TypeError("stop record must be an InitialStopRecordV2 instance")
    expected_conf = confirmation.confirmation
    if stop.confirmation != expected_conf or record.confirmation != expected_conf:
        raise RiskPositionSizingV2Error("initial stop confirmation provenance does not match")


@dataclass(frozen=True)
class SyntheticExitBookV2:
    """Cost-free retained state of the frozen stop and EMA exit predicates."""

    positions: OpenPositionSignalPolicyBookV2
    risk_sizing: RiskPositionSizingBookV2
    close_decisions: tuple[EMA20PositionExitCloseV2, ...] = ()
    ema_executions: tuple[EMA20ExitExecutionEvaluationV2, ...] = ()
    end_of_data: bool = False

    @property
    def end_state(self) -> ExitPolicyEndStateV2:
        return (
            ExitPolicyEndStateV2.OPEN_UNREALIZED
            if self.positions.active_position is not None
            else ExitPolicyEndStateV2.FLAT
        )


@dataclass(frozen=True)
class SyntheticExitHandoffV2:
    """The immutable exit policy result for one confirmed opportunity."""

    exit_book: SyntheticExitBookV2 | None
    terminal_exit: StructuralStopFillRecordV2 | EMA20ExitFillRecordV2 | None
    end_state: ExitPolicyEndStateV2 | None
    bound_initial_stop: InitialStopEvaluationV2
    risk_decision: RiskSizingDecisionRecordV2
    execution_evaluation: EntryExecutionEvaluationV2 | None
    sized_entry: RiskSizedEntryRecordV2 | None
    stop_reason: str


def capture_synthetic_exit_v2(
    *,
    confirmation: EntryConfirmationEvaluationV2,
    initial_stop: InitialStopEvaluationV2,
    risk_decision: RiskSizingDecisionRecordV2,
    entry_execution: EntryExecutionEvaluationV2 | None,
    sized_entry: RiskSizedEntryRecordV2 | None,
    bars_by_index: Mapping[int, EMA20PullbackBarV2],
) -> SyntheticExitHandoffV2:
    """Execute causal exit policy over subsequent bars following entry execution.

    Validates native provenance of confirmation, structural stop, risk decision,
    and entry execution.
    If risk was rejected, exit policy is not initialized.
    If risk was approved, initializes the two-exit policy (structural stop and EMA20
    next-Open exit) and causally steps through the bars following entry.
    """
    if (
        not isinstance(confirmation, EntryConfirmationEvaluationV2)
        or not confirmation.entry_confirmation
    ):
        raise ValueError("a native, qualified confirmation is required")
    _validate_native_confirmation(confirmation)
    _validate_exit_stop(initial_stop, confirmation)
    _validate_risk_decision(risk_decision, confirmation, initial_stop)

    if risk_decision.decision is RiskSizingDecisionV2.REJECT:
        if entry_execution is not None or sized_entry is not None:
            raise ValueError("rejected risk cannot have entry execution or sizing")
        if initial_stop.at_entry is not None:
            raise ValueError("rejected risk cannot bind initial stop to entry")
        return SyntheticExitHandoffV2(
            exit_book=None,
            terminal_exit=None,
            end_state=None,
            bound_initial_stop=initial_stop,
            risk_decision=risk_decision,
            execution_evaluation=None,
            sized_entry=None,
            stop_reason="ENTRY_REJECTED_BY_RISK",
        )

    if entry_execution is None or not isinstance(entry_execution, EntryExecutionEvaluationV2):
        raise ValueError("approved risk requires an EntryExecutionEvaluationV2 instance")

    expected_status = {
        EntryExecutionStateV2.PENDING_NEXT_BAR_OPEN: EntryExecutionStatusV2.NOT_EVALUATED,
        EntryExecutionStateV2.FILLED: EntryExecutionStatusV2.EVALUATED,
        EntryExecutionStateV2.EXPIRED_NO_EXECUTION: EntryExecutionStatusV2.EVALUATED,
        EntryExecutionStateV2.EXPIRED_EXECUTION_GAP: EntryExecutionStatusV2.EVALUATED,
        EntryExecutionStateV2.FAILED_INVALID_EXECUTION_INPUT: (
            EntryExecutionStatusV2.INVALID_EXECUTION_INPUT
        ),
        EntryExecutionStateV2.FAILED_INVALID_EXECUTION_CLOCK: (
            EntryExecutionStatusV2.INVALID_EXECUTION_CLOCK
        ),
    }
    if (
        not isinstance(entry_execution.execution_state, EntryExecutionStateV2)
        or entry_execution.status is not expected_status[entry_execution.execution_state]
        or entry_execution.confirmation != confirmation.confirmation
    ):
        raise ValueError("entry execution state or confirmation provenance is inconsistent")

    if entry_execution.execution_state is not EntryExecutionStateV2.FILLED:
        if (
            entry_execution.execution is not None
            or sized_entry is not None
            or initial_stop.at_entry is not None
        ):
            raise ValueError("unfilled execution cannot have an entry, sizing or bound stop")
        return SyntheticExitHandoffV2(
            exit_book=None,
            terminal_exit=None,
            end_state=None,
            bound_initial_stop=initial_stop,
            risk_decision=risk_decision,
            execution_evaluation=entry_execution,
            sized_entry=sized_entry,
            stop_reason=f"ENTRY_{entry_execution.execution_state.value}",
        )

    if sized_entry is None or not isinstance(sized_entry, RiskSizedEntryRecordV2):
        raise ValueError("filled execution requires a RiskSizedEntryRecordV2 instance")
    if entry_execution.execution is None:
        raise ValueError("filled execution must contain execution record")
    if entry_execution.execution.confirmation != confirmation.confirmation:
        raise ValueError("filled execution confirmation provenance does not match")
    if initial_stop.at_entry is None:
        raise ValueError("initial stop must be bound to entry execution for exit policy")
    if initial_stop.at_entry.execution != entry_execution.execution:
        raise ValueError("stop at entry does not match execution record")
    if sized_entry.execution != entry_execution.execution:
        raise ValueError("sized entry does not match execution record")
    if sized_entry.risk_decision != risk_decision:
        raise ValueError("sized entry does not match risk decision record")

    conf_rec = confirmation.confirmation
    e = entry_execution.execution.execution_bar_index
    if e != conf_rec.confirmation_bar_index + 1:
        raise ValueError("entry bar index must be immediately after confirmation")

    stop_book = InitialStopBookV2(entries=(initial_stop,))
    stop_executions = register_structural_stop_execution_v2(
        previous=StructuralStopExecutionBookV2(),
        initial_stops=stop_book,
        confirmation=conf_rec,
    )
    active_stop = stop_executions.for_confirmation(conf_rec)
    position = PositionRecordV2(
        entry=entry_execution.execution,
        initial_stop_at_entry=initial_stop.at_entry,
    )
    positions = OpenPositionSignalPolicyBookV2(
        strategy_instance_id="synthetic-strategy",
        series_id="synthetic-series",
        positions=(position,),
        active_stop=active_stop,
    )
    risk_sizing = RiskPositionSizingBookV2(
        strategy_instance_id="synthetic-strategy",
        series_id="synthetic-series",
        decisions=(risk_decision,),
        executions=EntryExecutionBookV2(entries=(entry_execution,)),
        filled_entries=(sized_entry,),
    )
    is_long = conf_rec.source_regime_event_direction is RegimeDirection.LONG
    adverse_name = "low" if is_long else "high"
    close_decisions: list[EMA20PositionExitCloseV2] = []
    ema_executions: list[EMA20ExitExecutionEvaluationV2] = []
    pending: EMA20ExitExecutionEvaluationV2 | None = None

    # A stop breached by the entry open is already filled by the frozen stop
    # registration. Resolve it without consulting any later observation.
    if active_stop.stop_execution_state is StructuralStopExecutionStateV2.FILLED_STOP:
        positions = resolve_position_stop_v2(
            previous=positions,
            known_bar_index=e,
            known_bar_timestamp=entry_execution.execution.execution_bar_timestamp,
        )
    for idx in sorted(bars_by_index):
        if idx < e or positions.active_position is None:
            continue
        bar = bars_by_index[idx]
        current_stop = positions.active_stop
        if (
            type(idx) is not int
            or getattr(bar, "bar_index", None) != idx
            or current_stop.stop_execution_state is not StructuralStopExecutionStateV2.ARMED
            or idx != current_stop.next_observation_bar_index
        ):
            raise ExitPolicyV2Error("invalid or missing indexed stop observation")
        timestamp = bar.timestamp_utc
        if (
            not _valid_utc(timestamp)
            or (idx == e and timestamp != entry_execution.execution.execution_bar_timestamp)
            or (
                current_stop.last_observed_bar_timestamp is not None
                and timestamp <= current_stop.last_observed_bar_timestamp
            )
        ):
            raise ExitPolicyV2Error("noncausal stop observation clock")
        opening = (
            entry_execution.execution.execution_price_before_costs
            if idx == e
            else _exact_price(bar.open)
        )
        if not isinstance(opening, Fraction) or opening <= 0:
            raise ExitPolicyV2Error("invalid exit opening price")
        level = initial_stop.initial_stop_record.initial_stop_price
        if idx > e and (opening <= level if is_long else opening >= level):
            positions = resolve_position_stop_v2(
                previous=positions,
                known_bar_index=idx,
                known_bar_timestamp=timestamp,
                observation=SimpleNamespace(bar_index=idx, timestamp_utc=timestamp, open=opening),
            )
            if positions.active_position is not None:
                raise ExitPolicyV2Error("opening stop gap failed to resolve")
            if pending is not None:
                ema_executions[-1] = replace(
                    pending, state=EMA20ExitExecutionStateV2.CANCELLED_STRUCTURAL_STOP
                )
            break

        # A pending EMA exit is checked only after the opening stop gap.
        if pending is not None:
            signal = pending.signal
            if idx != signal.exit_signal_bar_index + 1:
                raise ExitPolicyV2Error("EMA exit requires the next indexed open")
            elapsed = timestamp - signal.exit_signal_timestamp
            if elapsed > MAX_EXIT_EXECUTION_ELAPSED_TIME:
                ema_executions[-1] = replace(
                    pending, state=EMA20ExitExecutionStateV2.EXPIRED_EXIT_GAP
                )
                pending = None
            else:
                fill = EMA20ExitFillRecordV2(signal, idx, timestamp, opening)
                ema_executions[-1] = replace(
                    pending, state=EMA20ExitExecutionStateV2.FILLED_EMA20_EXIT, fill=fill
                )
                closed = replace(positions.active_position, exit=fill)
                positions = replace(
                    positions, positions=(*positions.positions[:-1], closed), active_stop=None
                )
                break

        # Only this bar's adverse extreme is read after its own open.
        if getattr(bar, "is_closed", None) is not True:
            raise ExitPolicyV2Error("exit close requires a closed observation")
        observation = SimpleNamespace(
            bar_index=idx,
            timestamp_utc=timestamp,
            open=opening,
            **{adverse_name: getattr(bar, adverse_name, None)},
        )
        positions = resolve_position_stop_v2(
            previous=positions,
            known_bar_index=idx,
            known_bar_timestamp=timestamp,
            observation=observation,
        )
        if positions.active_position is None:
            break
        if positions.active_stop.stop_execution_state is not StructuralStopExecutionStateV2.ARMED:
            raise ExitPolicyV2Error("invalid adverse stop observation")
        ema = evaluate_ema20_v2(
            through_bar_index=idx, bars_by_index=ClosedPrefix(bars_by_index, idx)
        )
        signal = None
        if ema.status is EMA20StatusV2.EVALUATED:
            if ema.known_at_timestamp != timestamp:
                raise ExitPolicyV2Error("EMA must be known at this close")
            qualifies = ema.last_close < ema.ema20 if is_long else ema.last_close > ema.ema20
            if qualifies:
                signal = EMA20ExitSignalRecordV2(
                    initial_stop.at_entry,
                    sized_entry.quantity,
                    idx,
                    timestamp,
                    ema.last_close,
                    ema.ema20,
                )
        close_decisions.append(
            EMA20PositionExitCloseV2(initial_stop.at_entry, idx, timestamp, ema, signal)
        )
        if signal is not None:
            pending = EMA20ExitExecutionEvaluationV2(signal)
            ema_executions.append(pending)

    if pending is not None and positions.active_position is not None:
        ema_executions[-1] = replace(
            pending, state=EMA20ExitExecutionStateV2.EXPIRED_NO_EXIT_EXECUTION
        )
    exit_book = SyntheticExitBookV2(
        positions, risk_sizing, tuple(close_decisions), tuple(ema_executions), True
    )
    terminal_exit = positions.positions[-1].exit
    end_state = exit_book.end_state

    if isinstance(terminal_exit, StructuralStopFillRecordV2):
        stop_reason = "EXIT_STRUCTURAL_STOP_FILLED"
    elif isinstance(terminal_exit, EMA20ExitFillRecordV2):
        stop_reason = "EXIT_EMA20_FILLED"
    elif end_state is ExitPolicyEndStateV2.OPEN_UNREALIZED:
        stop_reason = "OPEN_UNREALIZED_END_OF_DATA"
    else:
        stop_reason = f"EXIT_{end_state.value}"

    return SyntheticExitHandoffV2(
        exit_book=exit_book,
        terminal_exit=terminal_exit,
        end_state=end_state,
        bound_initial_stop=initial_stop,
        risk_decision=risk_decision,
        execution_evaluation=entry_execution,
        sized_entry=sized_entry,
        stop_reason=stop_reason,
    )
