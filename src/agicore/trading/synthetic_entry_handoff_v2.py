"""Handoff from native V2 confirmation, initial stop and risk decision to entry execution.

This adapter operates on already invented, validated observations. It reads no
file or external service, connects no broker and submits no live orders.
"""

from __future__ import annotations

from dataclasses import dataclass

from .ema_pullback_entry_confirmation_v2 import EntryConfirmationEvaluationV2
from .ema_pullback_entry_execution_v2 import (
    EntryExecutionBookV2,
    EntryExecutionEvaluationV2,
    EntryExecutionOpenInputV2,
    EntryExecutionOpenV2,
    EntryExecutionStateV2,
    execute_entry_open_v2,
    register_entry_execution_v2,
)
from .ema_pullback_initial_stop_v2 import (
    InitialStopBookV2,
    InitialStopEvaluationV2,
    bind_initial_stop_to_entry_v2,
)
from .ema_pullback_risk_position_sizing_v2 import (
    RiskPositionSizingV2Error,
    RiskSizedEntryRecordV2,
    RiskSizingDecisionRecordV2,
    RiskSizingDecisionV2,
)
from .synthetic_risk_handoff_v2 import _validate_native_stop
from .synthetic_stop_handoff_v2 import _validate_native_confirmation


def _validate_risk_decision(
    risk: RiskSizingDecisionRecordV2,
    confirmation: EntryConfirmationEvaluationV2,
    stop: InitialStopEvaluationV2,
) -> None:
    """Ensure risk sizing record matches native confirmation and evaluated stop provenance."""
    if not isinstance(risk, RiskSizingDecisionRecordV2):
        raise TypeError("risk decision must be a RiskSizingDecisionRecordV2 instance")
    expected_conf = confirmation.confirmation
    if risk.confirmation != expected_conf:
        raise RiskPositionSizingV2Error("risk decision confirmation provenance does not match")
    expected_stop = stop.initial_stop_record
    if risk.initial_stop_record != expected_stop:
        raise RiskPositionSizingV2Error("risk decision initial stop provenance does not match")
    if risk.confirmation_bar_index != expected_conf.confirmation_bar_index:
        raise RiskPositionSizingV2Error("risk decision bar index does not match confirmation")
    if risk.decision not in (RiskSizingDecisionV2.APPROVE, RiskSizingDecisionV2.REJECT):
        raise RiskPositionSizingV2Error("risk decision must be APPROVE or REJECT")


@dataclass(frozen=True)
class SyntheticEntryHandoffV2:
    """The immutable entry execution result for one confirmed opportunity."""

    execution_evaluation: EntryExecutionEvaluationV2 | None
    sized_entry: RiskSizedEntryRecordV2 | None
    bound_initial_stop: InitialStopEvaluationV2
    risk_decision: RiskSizingDecisionRecordV2
    stop_reason: str


def capture_synthetic_entry_v2(
    *,
    confirmation: EntryConfirmationEvaluationV2,
    initial_stop: InitialStopEvaluationV2,
    risk_decision: RiskSizingDecisionRecordV2,
    opening_bar: EntryExecutionOpenInputV2 | None,
) -> SyntheticEntryHandoffV2:
    """Execute entry at Open[q+1] following qualified confirmation and risk decision.

    Validates native provenance of confirmation, initial stop and risk decision.
    If risk was rejected, entry is not executed.
    If risk was approved, executes entry at the next bar's open, binds the structural stop,
    and returns sized entry record.
    """
    if (
        not isinstance(confirmation, EntryConfirmationEvaluationV2)
        or not confirmation.entry_confirmation
    ):
        raise ValueError("a native, qualified confirmation is required")
    _validate_native_confirmation(confirmation)
    _validate_native_stop(initial_stop, confirmation)
    _validate_risk_decision(risk_decision, confirmation, initial_stop)

    conf_record = confirmation.confirmation

    if risk_decision.decision is RiskSizingDecisionV2.REJECT:
        return SyntheticEntryHandoffV2(
            execution_evaluation=None,
            sized_entry=None,
            bound_initial_stop=initial_stop,
            risk_decision=risk_decision,
            stop_reason="ENTRY_REJECTED_BY_RISK",
        )

    # Risk is approved: register entry execution at Close[q]
    book = register_entry_execution_v2(previous=EntryExecutionBookV2(), confirmation=confirmation)

    open_input = None
    if opening_bar is not None:
        open_input = EntryExecutionOpenV2(
            bar_index=opening_bar.bar_index,
            timestamp_utc=opening_bar.timestamp_utc,
            open=opening_bar.open,
        )

    book_after = execute_entry_open_v2(
        previous=book,
        confirmation=conf_record,
        opening_bar=open_input,
    )
    outcome = book_after.for_confirmation(conf_record)

    if outcome.execution_state is not EntryExecutionStateV2.FILLED:
        return SyntheticEntryHandoffV2(
            execution_evaluation=outcome,
            sized_entry=None,
            bound_initial_stop=initial_stop,
            risk_decision=risk_decision,
            stop_reason=f"ENTRY_{outcome.execution_state.value}",
        )

    if outcome.execution is None:
        raise ValueError("filled execution must contain execution record")

    sized = RiskSizedEntryRecordV2(risk_decision=risk_decision, execution=outcome.execution)
    stop_book = InitialStopBookV2(entries=(initial_stop,))
    bound_stop_book = bind_initial_stop_to_entry_v2(
        previous=stop_book, confirmation=conf_record, executions=book_after
    )
    bound_stop = bound_stop_book.for_confirmation(conf_record)

    return SyntheticEntryHandoffV2(
        execution_evaluation=outcome,
        sized_entry=sized,
        bound_initial_stop=bound_stop,
        risk_decision=risk_decision,
        stop_reason="ENTRY_FILLED_BEFORE_EXIT",
    )
