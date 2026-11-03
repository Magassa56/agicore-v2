"""Unit tests for synthetic confirmation, stop and risk handoff to entry execution."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from fractions import Fraction

import pytest

from agicore.trading.ema20_pullback_v2 import EMA20PullbackBarV2
from agicore.trading.ema_pullback_entry_execution_v2 import (
    EntryExecutionActionV2,
    EntryExecutionOpenV2,
    EntryExecutionStateV2,
    EntryExecutionStatusV2,
)
from agicore.trading.ema_pullback_initial_stop_v2 import (
    InitialStopAtEntryV2,
    InitialStopStateV2,
)
from agicore.trading.ema_pullback_risk_position_sizing_v2 import (
    RiskPositionSizingV2Error,
    RiskSizedEntryRecordV2,
    RiskSizingDecisionV2,
)
from agicore.trading.ema_pullback_v2_development_replay import parse_ninjatrader_last_rows_v2
from agicore.trading.regime_context_v2 import RegimeDirection
from agicore.trading.synthetic_confirmation_fixture_v2 import generate_confirmation_fixture
from agicore.trading.synthetic_confirmation_replay_v2 import replay_confirmation_native
from agicore.trading.synthetic_entry_handoff_v2 import (
    SyntheticEntryHandoffV2,
    capture_synthetic_entry_v2,
)
from agicore.trading.synthetic_risk_handoff_v2 import capture_synthetic_risk_v2
from agicore.trading.synthetic_stop_handoff_v2 import capture_synthetic_stop_v2


def _setup_handoff(profile: str):
    raw = generate_confirmation_fixture(profile, 39)
    outcome = replay_confirmation_native(raw)
    signal = outcome.native_confirmation
    bars = parse_ninjatrader_last_rows_v2(raw)
    k, q = signal.confirmation.pullback_bar_index, signal.confirmation.confirmation_bar_index
    selected = tuple(
        EMA20PullbackBarV2(b.bar_index, b.timestamp_utc, b.open, b.high, b.low, b.close, True)
        for b in bars[k : q + 1]
    )
    stop_eval = capture_synthetic_stop_v2(confirmation=signal, closed_window=selected).evaluation
    candidate_bar = selected[-1]
    risk_dec = capture_synthetic_risk_v2(
        confirmation=signal, initial_stop=stop_eval, closed_candidate=candidate_bar
    ).decision
    next_bar = bars[q + 1] if q + 1 < len(bars) else None
    opening_bar = (
        EntryExecutionOpenV2(next_bar.bar_index, next_bar.timestamp_utc, next_bar.open)
        if next_bar is not None
        else None
    )
    return signal, stop_eval, risk_dec, opening_bar


def test_long_accepted_scenario():
    signal, stop_eval, risk_dec, opening_bar = _setup_handoff("confirmation-long-v1")
    handoff = capture_synthetic_entry_v2(
        confirmation=signal,
        initial_stop=stop_eval,
        risk_decision=risk_dec,
        opening_bar=opening_bar,
    )
    assert isinstance(handoff, SyntheticEntryHandoffV2)
    assert handoff.stop_reason == "ENTRY_FILLED_BEFORE_EXIT"
    assert handoff.execution_evaluation is not None
    assert handoff.execution_evaluation.execution_state is EntryExecutionStateV2.FILLED
    assert handoff.execution_evaluation.status is EntryExecutionStatusV2.EVALUATED

    exec_rec = handoff.execution_evaluation.execution
    assert exec_rec is not None
    assert exec_rec.execution_bar_index == 36
    assert exec_rec.execution_action is EntryExecutionActionV2.BUY
    assert exec_rec.execution_side is RegimeDirection.LONG
    assert exec_rec.execution_price_before_costs == Fraction(40009, 2)  # 20004.50
    assert exec_rec.order_semantics == "MARKET"

    sized = handoff.sized_entry
    assert isinstance(sized, RiskSizedEntryRecordV2)
    assert sized.quantity == 2
    assert sized.actual_entry_price == Fraction(40009, 2)
    assert sized.actual_entry_to_stop_distance_points == Fraction(9, 2)  # 20004.50 - 20000.00 = 4.50

    bound_stop = handoff.bound_initial_stop
    assert bound_stop.at_entry is not None
    assert bound_stop.at_entry.stop_state is InitialStopStateV2.ARMED
    assert bound_stop.at_entry.entry_price == Fraction(40009, 2)
    assert bound_stop.at_entry.entry_bar_index == 36


def test_short_accepted_scenario():
    signal, stop_eval, risk_dec, opening_bar = _setup_handoff("confirmation-short-v1")
    handoff = capture_synthetic_entry_v2(
        confirmation=signal,
        initial_stop=stop_eval,
        risk_decision=risk_dec,
        opening_bar=opening_bar,
    )
    assert isinstance(handoff, SyntheticEntryHandoffV2)
    assert handoff.stop_reason == "ENTRY_FILLED_BEFORE_EXIT"
    assert handoff.execution_evaluation is not None
    assert handoff.execution_evaluation.execution_state is EntryExecutionStateV2.FILLED

    exec_rec = handoff.execution_evaluation.execution
    assert exec_rec is not None
    assert exec_rec.execution_bar_index == 36
    assert exec_rec.execution_action is EntryExecutionActionV2.SELL_SHORT
    assert exec_rec.execution_side is RegimeDirection.SHORT
    assert exec_rec.execution_price_before_costs == Fraction(39991, 2)  # 19995.50

    sized = handoff.sized_entry
    assert isinstance(sized, RiskSizedEntryRecordV2)
    assert sized.quantity == 2
    assert sized.actual_entry_price == Fraction(39991, 2)
    assert sized.actual_entry_to_stop_distance_points == Fraction(9, 2)  # 20000.00 - 19995.50 = 4.50

    bound_stop = handoff.bound_initial_stop
    assert bound_stop.at_entry is not None
    assert bound_stop.at_entry.stop_state is InitialStopStateV2.ARMED
    assert bound_stop.at_entry.entry_price == Fraction(39991, 2)


def test_long_rejected_scenario():
    signal, stop_eval, risk_dec, opening_bar = _setup_handoff("confirmation-long-rejected-v1")
    assert risk_dec.decision is RiskSizingDecisionV2.REJECT
    handoff = capture_synthetic_entry_v2(
        confirmation=signal,
        initial_stop=stop_eval,
        risk_decision=risk_dec,
        opening_bar=opening_bar,
    )
    assert handoff.stop_reason == "ENTRY_REJECTED_BY_RISK"
    assert handoff.execution_evaluation is None
    assert handoff.sized_entry is None
    assert handoff.bound_initial_stop.at_entry is None


def test_short_rejected_scenario():
    signal, stop_eval, risk_dec, opening_bar = _setup_handoff("confirmation-short-rejected-v1")
    assert risk_dec.decision is RiskSizingDecisionV2.REJECT
    handoff = capture_synthetic_entry_v2(
        confirmation=signal,
        initial_stop=stop_eval,
        risk_decision=risk_dec,
        opening_bar=opening_bar,
    )
    assert handoff.stop_reason == "ENTRY_REJECTED_BY_RISK"
    assert handoff.execution_evaluation is None
    assert handoff.sized_entry is None
    assert handoff.bound_initial_stop.at_entry is None


def test_reject_missing_opening_bar():
    signal, stop_eval, risk_dec, _ = _setup_handoff("confirmation-long-v1")
    handoff = capture_synthetic_entry_v2(
        confirmation=signal,
        initial_stop=stop_eval,
        risk_decision=risk_dec,
        opening_bar=None,
    )
    assert handoff.stop_reason == "ENTRY_EXPIRED_NO_EXECUTION"
    assert handoff.execution_evaluation is not None
    assert handoff.execution_evaluation.execution_state is EntryExecutionStateV2.EXPIRED_NO_EXECUTION
    assert handoff.sized_entry is None
    assert handoff.bound_initial_stop.at_entry is None


def test_reject_clock_gap():
    signal, stop_eval, risk_dec, opening_bar = _setup_handoff("confirmation-long-v1")
    # Time gap > 1 minute (2 minutes later)
    gap_bar = EntryExecutionOpenV2(
        bar_index=opening_bar.bar_index,
        timestamp_utc=opening_bar.timestamp_utc + timedelta(minutes=1),
        open=opening_bar.open,
    )
    handoff = capture_synthetic_entry_v2(
        confirmation=signal,
        initial_stop=stop_eval,
        risk_decision=risk_dec,
        opening_bar=gap_bar,
    )
    assert handoff.stop_reason == "ENTRY_EXPIRED_EXECUTION_GAP"
    assert handoff.execution_evaluation is not None
    assert handoff.execution_evaluation.execution_state is EntryExecutionStateV2.EXPIRED_EXECUTION_GAP


def test_reject_invalid_clock():
    signal, stop_eval, risk_dec, opening_bar = _setup_handoff("confirmation-long-v1")
    # Non-causal clock: timestamp earlier than confirmation timestamp
    invalid_clock_bar = EntryExecutionOpenV2(
        bar_index=opening_bar.bar_index,
        timestamp_utc=signal.confirmation.confirmation_timestamp - timedelta(minutes=1),
        open=opening_bar.open,
    )
    handoff = capture_synthetic_entry_v2(
        confirmation=signal,
        initial_stop=stop_eval,
        risk_decision=risk_dec,
        opening_bar=invalid_clock_bar,
    )
    assert handoff.stop_reason == "ENTRY_FAILED_INVALID_EXECUTION_CLOCK"
    assert handoff.execution_evaluation is not None
    assert (
        handoff.execution_evaluation.execution_state
        is EntryExecutionStateV2.FAILED_INVALID_EXECUTION_CLOCK
    )


def test_reject_invalid_price():
    signal, stop_eval, risk_dec, opening_bar = _setup_handoff("confirmation-long-v1")
    invalid_price_bar = EntryExecutionOpenV2(
        bar_index=opening_bar.bar_index,
        timestamp_utc=opening_bar.timestamp_utc,
        open=Fraction(-10, 1),
    )
    handoff = capture_synthetic_entry_v2(
        confirmation=signal,
        initial_stop=stop_eval,
        risk_decision=risk_dec,
        opening_bar=invalid_price_bar,
    )
    assert handoff.stop_reason == "ENTRY_FAILED_INVALID_EXECUTION_INPUT"
    assert handoff.execution_evaluation is not None
    assert (
        handoff.execution_evaluation.execution_state
        is EntryExecutionStateV2.FAILED_INVALID_EXECUTION_INPUT
    )


def test_reject_entry_bound_stop():
    signal, stop_eval, risk_dec, opening_bar = _setup_handoff("confirmation-long-v1")
    tampered_stop = replace(
        stop_eval,
        at_entry=InitialStopAtEntryV2(
            initial_stop_record=stop_eval.initial_stop_record,
            execution=None,
            entry_bar_index=36,
            entry_bar_timestamp=datetime(2099, 1, 4, 8, 36, tzinfo=UTC),
            entry_price=Fraction(20000, 1),
            stop_state=InitialStopStateV2.ARMED,
        ),
    )
    with pytest.raises(ValueError, match="entry-bound initial stops are forbidden"):
        capture_synthetic_entry_v2(
            confirmation=signal,
            initial_stop=tampered_stop,
            risk_decision=risk_dec,
            opening_bar=opening_bar,
        )


def test_reject_mismatched_risk_confirmation():
    signal_long, stop_eval, risk_dec, opening_bar = _setup_handoff("confirmation-long-v1")
    signal_short, _, _, _ = _setup_handoff("confirmation-short-v1")
    with pytest.raises(RiskPositionSizingV2Error, match="confirmation provenance does not match"):
        capture_synthetic_entry_v2(
            confirmation=signal_short,
            initial_stop=stop_eval,
            risk_decision=risk_dec,
            opening_bar=opening_bar,
        )


def test_reject_mismatched_risk_stop():
    signal, stop_eval_long, risk_dec_long, opening_bar = _setup_handoff("confirmation-long-v1")
    _, stop_eval_short, _, _ = _setup_handoff("confirmation-short-v1")
    with pytest.raises(RiskPositionSizingV2Error, match="initial stop.*provenance does not match"):
        capture_synthetic_entry_v2(
            confirmation=signal,
            initial_stop=stop_eval_short,
            risk_decision=risk_dec_long,
            opening_bar=opening_bar,
        )


def test_double_execution_refused_or_idempotent():
    from agicore.trading.ema_pullback_entry_execution_v2 import (
        EntryExecutionBookV2,
        execute_entry_open_v2,
    )

    signal, stop_eval, risk_dec, opening_bar = _setup_handoff("confirmation-long-v1")
    handoff = capture_synthetic_entry_v2(
        confirmation=signal,
        initial_stop=stop_eval,
        risk_decision=risk_dec,
        opening_bar=opening_bar,
    )
    assert handoff.execution_evaluation is not None
    assert handoff.execution_evaluation.execution_state is EntryExecutionStateV2.FILLED

    book = EntryExecutionBookV2((handoff.execution_evaluation,))
    second_book = execute_entry_open_v2(
        previous=book,
        confirmation=signal.confirmation,
        opening_bar=opening_bar,
    )
    assert second_book is book
    assert second_book.entries[0] is handoff.execution_evaluation
