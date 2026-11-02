"""Handoff from native V2 confirmation and initial stop to an immutable risk decision.

This adapter operates on already invented, validated observations. It reads no
file or external service and produces no entry execution, order, position or fill.
"""

from __future__ import annotations

from dataclasses import dataclass

from .ema_pullback_entry_confirmation_v2 import EntryConfirmationEvaluationV2
from .ema_pullback_initial_stop_v2 import (
    InitialStopEvaluationV2,
    InitialStopRecordV2,
    InitialStopStatusV2,
)
from .ema_pullback_risk_position_sizing_v2 import (
    INSTRUMENT,
    PositionStateV2,
    RiskPositionSizingV2Error,
    RiskSizingCloseInputV2,
    RiskSizingDecisionRecordV2,
    evaluate_risk_position_sizing_v2,
)
from .synthetic_stop_handoff_v2 import _validate_native_confirmation


def _validate_native_stop(
    stop: InitialStopEvaluationV2, confirmation: EntryConfirmationEvaluationV2
) -> None:
    """Ensure stop evaluation is native, evaluated, entry-unbound, and provenance-consistent."""
    if not isinstance(stop, InitialStopEvaluationV2):
        raise TypeError("initial stop must be an InitialStopEvaluationV2 instance")
    if stop.status is not InitialStopStatusV2.EVALUATED or stop.initial_stop_record is None:
        raise RiskPositionSizingV2Error("initial stop must be evaluated before risk sizing")
    if stop.at_entry is not None:
        raise ValueError("entry-bound initial stops are forbidden before risk decision")
    record = stop.initial_stop_record
    if not isinstance(record, InitialStopRecordV2):
        raise TypeError("stop record must be an InitialStopRecordV2 instance")
    expected_confirmation = confirmation.confirmation
    if stop.confirmation != expected_confirmation or record.confirmation != expected_confirmation:
        raise RiskPositionSizingV2Error("initial stop confirmation provenance does not match")


@dataclass(frozen=True)
class SyntheticRiskHandoffV2:
    """The immutable risk sizing decision record for one confirmed opportunity."""

    decision: RiskSizingDecisionRecordV2


def capture_synthetic_risk_v2(
    *,
    confirmation: EntryConfirmationEvaluationV2,
    initial_stop: InitialStopEvaluationV2,
    closed_candidate: RiskSizingCloseInputV2,
    position_state: PositionStateV2 = PositionStateV2.FLAT,
    instrument: str = INSTRUMENT,
) -> SyntheticRiskHandoffV2:
    """Evaluate planned structural risk at Close[q] before any next-bar input.

    Validates native provenance of confirmation and initial stop. Fails closed if
    metadata is contradictory, incomplete or already entry-bound.
    """
    if (
        not isinstance(confirmation, EntryConfirmationEvaluationV2)
        or not confirmation.entry_confirmation
    ):
        raise ValueError("a native, qualified confirmation is required")
    _validate_native_confirmation(confirmation)
    _validate_native_stop(initial_stop, confirmation)

    record = confirmation.confirmation
    q = record.confirmation_bar_index
    if (
        getattr(closed_candidate, "bar_index", None) != q
        or getattr(closed_candidate, "timestamp_utc", None) != record.confirmation_timestamp
        or getattr(closed_candidate, "is_closed", None) is not True
    ):
        raise ValueError("closed candidate bar must match confirmation Close[q] clock")

    decision = evaluate_risk_position_sizing_v2(
        instrument=instrument,
        closed_bar_index=q,
        closed_bar_timestamp=record.confirmation_timestamp,
        source_bar_closed=True,
        confirmation=confirmation,
        initial_stop=initial_stop,
        position_state=position_state,
        bars_by_index={q: closed_candidate},
    )
    return SyntheticRiskHandoffV2(decision)
