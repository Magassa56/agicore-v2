"""Handoff from native V2 confirmation and initial stop to an immutable risk decision.

This adapter operates on already invented, validated observations. It reads no
file or external service and produces no entry execution, order, position or fill.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import directional_impulse_v2 as impulse
from . import ema20_pullback_v2 as ema20
from . import ema_pullback_entry_confirmation_v2 as entry_confirmation
from . import ema_pullback_open_position_signal_policy_v2 as positions
from . import ema_pullback_pending_opportunity_policy_v2 as pending
from . import ema_pullback_v2_development_replay as replay
from . import reversal_transition_v2 as reversal
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
from .synthetic_confirmation_replay_v2 import ClosedPrefix
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
    metadata is contradictory, incomplete or already entry-bound. This low-level
    calculation does not establish policy admission or authorize an entry; the
    synthetic mission uses ``capture_admitted_synthetic_risk_v2`` instead.
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


def capture_admitted_synthetic_risk_v2(
    *,
    raw: bytes,
    confirmation: EntryConfirmationEvaluationV2,
    initial_stop: InitialStopEvaluationV2,
    closed_candidate: RiskSizingCloseInputV2,
) -> SyntheticRiskHandoffV2:
    """Require the frozen pending/admission gate before a fixed-profile decision.

    The synthetic mission starts with an empty position book and stops at its
    first confirmation. It does not claim to replay an existing position or
    later opportunities. No entry, position, costs or accounting are created.
    """
    _validate_native_confirmation(confirmation)
    record = confirmation.confirmation
    q = record.confirmation_bar_index
    bars = replay.parse_ninjatrader_last_rows_v2(raw)
    if type(q) is not int or not 0 <= q < len(bars):
        raise ValueError("invalid synthetic admission confirmation clock")
    policy = pending.begin_pending_opportunity_policy_v2(
        strategy_instance_id="AGICORE_SYNTHETIC", series_id="FIRST_POSITION_ONLY"
    )
    prices, impulse_bars, rejection_bars = {}, {}, {}
    for bar in bars[: q + 1]:
        i = bar.bar_index
        prices[i] = ema20.EMA20PullbackBarV2(
            i, bar.timestamp_utc, bar.open, bar.high, bar.low, bar.close, True
        )
        impulse_bars[i] = bar.closed_view()
        rejection_bars[i] = reversal.RejectionBarV2(
            i, bar.timestamp_utc, bar.close, True, bar.open, bar.high, bar.low
        )
        prefix = ClosedPrefix(prices, i)
        if (
            policy.risks.decisions
            or policy.risks.executions.entries
            or policy.positions.positions
            or policy.initial_stops.entries
        ):
            raise ValueError("synthetic admission requires an initially empty position book")
        active = policy.active_opportunity
        if active is not None:
            if active.state is not pending.PendingOpportunityStateV2.AWAITING_CONFIRMATION:
                raise ValueError("synthetic admission cannot follow a pending execution")
            candidate = entry_confirmation.advance_entry_confirmation_momentum_v2(
                previous=active.confirmation,
                closed_bar_index=i,
                closed_bar_timestamp=bar.timestamp_utc,
                source_bar_closed=True,
                bars_by_index=prefix,
            )
            if candidate.entry_confirmation:
                if i != q or candidate != confirmation or prices[i] != closed_candidate:
                    raise ValueError("synthetic admission confirmation disagrees with input")
                clock = positions.advance_open_position_signal_policy_v2(
                    previous=policy.positions,
                    closed_bar_index=i,
                    closed_bar_timestamp=bar.timestamp_utc,
                    source_bar_closed=True,
                    bars_by_index=prefix,
                )
                if (
                    clock.position_state is not positions.PositionStateV2.FLAT
                    or clock.positions
                    or not clock.signal_decisions
                    or (
                        clock.signal_decisions[-1].composition.closed_bar_index,
                        clock.signal_decisions[-1].composition.closed_bar_timestamp,
                    )
                    != (i, bar.timestamp_utc)
                ):
                    raise ValueError("synthetic admission policy is not flat at confirmation")
                positions._require_admitted_pullback(clock, record)
                return capture_synthetic_risk_v2(
                    confirmation=candidate,
                    initial_stop=initial_stop,
                    closed_candidate=closed_candidate,
                    position_state=clock.position_state,
                )
        if i == q:
            raise ValueError("synthetic confirmation lacks a native pending admission")

        def events_at_close(i=i):
            event = impulse.evaluate_directional_impulse_event_v2(
                impulse_candidate_bar_index=i, bars_by_index=impulse_bars
            ).event
            previous = i - reversal.CONFIRMATION_WINDOW_CLOSED_BARS
            reversed_event = (
                None
                if previous < 0
                else reversal.evaluate_reversal_transition_event_v2(
                    rejection_candidate_bar_index=previous,
                    closed_bar_index=i,
                    bars_by_index=rejection_bars,
                ).event
            )
            return event, None if reversed_event is None else reversed_event.as_regime_event()

        policy = pending.advance_pending_opportunity_close_v2(
            previous=policy,
            closed_bar_index=i,
            closed_bar_timestamp=bar.timestamp_utc,
            source_bar_closed=True,
            bars_by_index=prefix,
            regime_events_at_close=events_at_close,
        )
    raise ValueError("synthetic admission was not found")
