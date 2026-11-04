"""Handoff from native V2 confirmation, entry and initial stop to exit execution.

This adapter operates on already invented, validated observations. It reads no
file or external service, connects no broker and submits no live orders.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import SimpleNamespace

from .ema20_pullback_v2 import EMA20PullbackBarV2
from .ema_pullback_entry_confirmation_v2 import EntryConfirmationEvaluationV2
from .ema_pullback_entry_execution_v2 import (
    EntryExecutionBookV2,
    EntryExecutionEvaluationV2,
    EntryExecutionStateV2,
)
from .ema_pullback_exit_policy_v2 import (
    EMA20ExitFillRecordV2,
    ExitPolicyBookV2,
    ExitPolicyEndStateV2,
    begin_exit_policy_v2,
    finish_exit_policy_v2,
    process_exit_policy_close_v2,
    process_exit_policy_open_v2,
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
    StructuralStopFillRecordV2,
    register_structural_stop_execution_v2,
)
from .regime_context_v2 import RegimeDirection
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
class SyntheticExitHandoffV2:
    """The immutable exit policy result for one confirmed opportunity."""

    exit_book: ExitPolicyBookV2 | None
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
    if sized_entry is None or not isinstance(sized_entry, RiskSizedEntryRecordV2):
        raise ValueError("approved risk requires a RiskSizedEntryRecordV2 instance")

    if entry_execution.execution_state is not EntryExecutionStateV2.FILLED:
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

    if entry_execution.execution is None:
        raise ValueError("filled execution must contain execution record")
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
    exit_book = begin_exit_policy_v2(positions=positions, risk_sizing=risk_sizing)

    is_long = conf_rec.source_regime_event_direction is RegimeDirection.LONG
    adverse_name = "low" if is_long else "high"

    for idx in sorted(bars_by_index):
        if idx < e:
            continue
        bar = bars_by_index[idx]
        open_obs = SimpleNamespace(
            bar_index=idx,
            timestamp_utc=bar.timestamp_utc,
            open=bar.open,
        )
        exit_book = process_exit_policy_open_v2(previous=exit_book, observation=open_obs)
        close_obs = SimpleNamespace(
            bar_index=idx,
            timestamp_utc=bar.timestamp_utc,
            **{adverse_name: getattr(bar, adverse_name)},
        )
        exit_book = process_exit_policy_close_v2(
            previous=exit_book,
            closed_bar_index=idx,
            closed_bar_timestamp=bar.timestamp_utc,
            source_bar_closed=True,
            bars_by_index=bars_by_index,
            stop_observation=close_obs,
        )

    exit_book = finish_exit_policy_v2(previous=exit_book)
    terminal_exit = exit_book.positions.positions[-1].exit
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
