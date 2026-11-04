"""Unit tests for synthetic confirmation, stop, risk and entry handoff to exit execution."""

from __future__ import annotations

from dataclasses import replace
from fractions import Fraction

import pytest

from agicore.trading.ema20_pullback_v2 import EMA20PullbackBarV2
from agicore.trading.ema_pullback_entry_execution_v2 import (
    EntryExecutionOpenV2,
)
from agicore.trading.ema_pullback_exit_policy_v2 import (
    EMA20ExitFillRecordV2,
    ExitPolicyEndStateV2,
)
from agicore.trading.ema_pullback_structural_stop_trigger_fill_v2 import (
    StructuralStopFillRecordV2,
)
from agicore.trading.ema_pullback_v2_development_replay import parse_ninjatrader_last_rows_v2
from agicore.trading.synthetic_confirmation_fixture_v2 import generate_confirmation_fixture
from agicore.trading.synthetic_confirmation_replay_v2 import replay_confirmation_native
from agicore.trading.synthetic_entry_handoff_v2 import capture_synthetic_entry_v2
from agicore.trading.synthetic_exit_handoff_v2 import (
    SyntheticExitHandoffV2,
    capture_synthetic_exit_v2,
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
    entry_handoff = capture_synthetic_entry_v2(
        confirmation=signal,
        initial_stop=stop_eval,
        risk_decision=risk_dec,
        opening_bar=opening_bar,
    )
    bars_by_index = {
        b.bar_index: EMA20PullbackBarV2(b.bar_index, b.timestamp_utc, b.open, b.high, b.low, b.close, True)
        for b in bars
    }
    return signal, entry_handoff, risk_dec, bars_by_index


def test_long_unrealized_scenario():
    signal, entry_handoff, risk_dec, bars_by_index = _setup_handoff("confirmation-long-v1")
    exit_handoff = capture_synthetic_exit_v2(
        confirmation=signal,
        initial_stop=entry_handoff.bound_initial_stop,
        risk_decision=risk_dec,
        entry_execution=entry_handoff.execution_evaluation,
        sized_entry=entry_handoff.sized_entry,
        bars_by_index=bars_by_index,
    )
    assert isinstance(exit_handoff, SyntheticExitHandoffV2)
    assert exit_handoff.stop_reason == "OPEN_UNREALIZED_END_OF_DATA"
    assert exit_handoff.terminal_exit is None
    assert exit_handoff.end_state is ExitPolicyEndStateV2.OPEN_UNREALIZED
    assert exit_handoff.exit_book is not None


def test_short_unrealized_scenario():
    signal, entry_handoff, risk_dec, bars_by_index = _setup_handoff("confirmation-short-v1")
    exit_handoff = capture_synthetic_exit_v2(
        confirmation=signal,
        initial_stop=entry_handoff.bound_initial_stop,
        risk_decision=risk_dec,
        entry_execution=entry_handoff.execution_evaluation,
        sized_entry=entry_handoff.sized_entry,
        bars_by_index=bars_by_index,
    )
    assert isinstance(exit_handoff, SyntheticExitHandoffV2)
    assert exit_handoff.stop_reason == "OPEN_UNREALIZED_END_OF_DATA"
    assert exit_handoff.terminal_exit is None
    assert exit_handoff.end_state is ExitPolicyEndStateV2.OPEN_UNREALIZED


def test_long_rejected_scenario():
    signal, entry_handoff, risk_dec, bars_by_index = _setup_handoff("confirmation-long-rejected-v1")
    exit_handoff = capture_synthetic_exit_v2(
        confirmation=signal,
        initial_stop=entry_handoff.bound_initial_stop,
        risk_decision=risk_dec,
        entry_execution=entry_handoff.execution_evaluation,
        sized_entry=entry_handoff.sized_entry,
        bars_by_index=bars_by_index,
    )
    assert isinstance(exit_handoff, SyntheticExitHandoffV2)
    assert exit_handoff.stop_reason == "ENTRY_REJECTED_BY_RISK"
    assert exit_handoff.terminal_exit is None
    assert exit_handoff.end_state is None
    assert exit_handoff.exit_book is None


def test_short_rejected_scenario():
    signal, entry_handoff, risk_dec, bars_by_index = _setup_handoff("confirmation-short-rejected-v1")
    exit_handoff = capture_synthetic_exit_v2(
        confirmation=signal,
        initial_stop=entry_handoff.bound_initial_stop,
        risk_decision=risk_dec,
        entry_execution=entry_handoff.execution_evaluation,
        sized_entry=entry_handoff.sized_entry,
        bars_by_index=bars_by_index,
    )
    assert isinstance(exit_handoff, SyntheticExitHandoffV2)
    assert exit_handoff.stop_reason == "ENTRY_REJECTED_BY_RISK"
    assert exit_handoff.terminal_exit is None
    assert exit_handoff.end_state is None


def test_long_stop_exit_scenario():
    signal, entry_handoff, risk_dec, bars_by_index = _setup_handoff("confirmation-long-exit-stop-v1")
    exit_handoff = capture_synthetic_exit_v2(
        confirmation=signal,
        initial_stop=entry_handoff.bound_initial_stop,
        risk_decision=risk_dec,
        entry_execution=entry_handoff.execution_evaluation,
        sized_entry=entry_handoff.sized_entry,
        bars_by_index=bars_by_index,
    )
    assert isinstance(exit_handoff, SyntheticExitHandoffV2)
    assert exit_handoff.stop_reason == "EXIT_STRUCTURAL_STOP_FILLED"
    assert isinstance(exit_handoff.terminal_exit, StructuralStopFillRecordV2)
    assert exit_handoff.end_state is ExitPolicyEndStateV2.FLAT
    assert exit_handoff.terminal_exit.trigger_bar_index == 37
    assert exit_handoff.terminal_exit.base_stop_fill_price == Fraction(20000, 1)


def test_short_stop_exit_scenario():
    signal, entry_handoff, risk_dec, bars_by_index = _setup_handoff("confirmation-short-exit-stop-v1")
    exit_handoff = capture_synthetic_exit_v2(
        confirmation=signal,
        initial_stop=entry_handoff.bound_initial_stop,
        risk_decision=risk_dec,
        entry_execution=entry_handoff.execution_evaluation,
        sized_entry=entry_handoff.sized_entry,
        bars_by_index=bars_by_index,
    )
    assert isinstance(exit_handoff, SyntheticExitHandoffV2)
    assert exit_handoff.stop_reason == "EXIT_STRUCTURAL_STOP_FILLED"
    assert isinstance(exit_handoff.terminal_exit, StructuralStopFillRecordV2)
    assert exit_handoff.end_state is ExitPolicyEndStateV2.FLAT
    assert exit_handoff.terminal_exit.trigger_bar_index == 37
    assert exit_handoff.terminal_exit.base_stop_fill_price == Fraction(20000, 1)


def test_long_ema_exit_scenario():
    signal, entry_handoff, risk_dec, bars_by_index = _setup_handoff("confirmation-long-exit-ema-v1")
    exit_handoff = capture_synthetic_exit_v2(
        confirmation=signal,
        initial_stop=entry_handoff.bound_initial_stop,
        risk_decision=risk_dec,
        entry_execution=entry_handoff.execution_evaluation,
        sized_entry=entry_handoff.sized_entry,
        bars_by_index=bars_by_index,
    )
    assert isinstance(exit_handoff, SyntheticExitHandoffV2)
    assert exit_handoff.stop_reason == "EXIT_EMA20_FILLED"
    assert isinstance(exit_handoff.terminal_exit, EMA20ExitFillRecordV2)
    assert exit_handoff.end_state is ExitPolicyEndStateV2.FLAT
    assert exit_handoff.terminal_exit.exit_execution_bar_index == 37
    assert exit_handoff.terminal_exit.base_exit_fill_price == Fraction(20001, 1)


def test_short_ema_exit_scenario():
    signal, entry_handoff, risk_dec, bars_by_index = _setup_handoff("confirmation-short-exit-ema-v1")
    exit_handoff = capture_synthetic_exit_v2(
        confirmation=signal,
        initial_stop=entry_handoff.bound_initial_stop,
        risk_decision=risk_dec,
        entry_execution=entry_handoff.execution_evaluation,
        sized_entry=entry_handoff.sized_entry,
        bars_by_index=bars_by_index,
    )
    assert isinstance(exit_handoff, SyntheticExitHandoffV2)
    assert exit_handoff.stop_reason == "EXIT_EMA20_FILLED"
    assert isinstance(exit_handoff.terminal_exit, EMA20ExitFillRecordV2)
    assert exit_handoff.end_state is ExitPolicyEndStateV2.FLAT
    assert exit_handoff.terminal_exit.exit_execution_bar_index == 37
    assert exit_handoff.terminal_exit.base_exit_fill_price == Fraction(19999, 1)


def test_reject_unbound_initial_stop():
    signal, entry_handoff, risk_dec, bars_by_index = _setup_handoff("confirmation-long-v1")
    unbound_stop = replace(entry_handoff.bound_initial_stop, at_entry=None)
    with pytest.raises(ValueError, match="must be bound to entry"):
        capture_synthetic_exit_v2(
            confirmation=signal,
            initial_stop=unbound_stop,
            risk_decision=risk_dec,
            entry_execution=entry_handoff.execution_evaluation,
            sized_entry=entry_handoff.sized_entry,
            bars_by_index=bars_by_index,
        )


def test_reject_mismatched_stop_execution():
    signal, entry_handoff, risk_dec, bars_by_index = _setup_handoff("confirmation-long-v1")
    mismatched_at_entry = replace(
        entry_handoff.bound_initial_stop.at_entry,
        execution=replace(entry_handoff.bound_initial_stop.at_entry.execution, execution_bar_index=99),
    )
    mismatched_stop = replace(entry_handoff.bound_initial_stop, at_entry=mismatched_at_entry)
    with pytest.raises(ValueError, match="does not match execution record"):
        capture_synthetic_exit_v2(
            confirmation=signal,
            initial_stop=mismatched_stop,
            risk_decision=risk_dec,
            entry_execution=entry_handoff.execution_evaluation,
            sized_entry=entry_handoff.sized_entry,
            bars_by_index=bars_by_index,
        )


def test_reject_mismatched_sized_entry():
    signal, entry_handoff, risk_dec, bars_by_index = _setup_handoff("confirmation-long-v1")
    mismatched_sized = replace(
        entry_handoff.sized_entry,
        execution=replace(entry_handoff.sized_entry.execution, execution_bar_index=99),
    )
    with pytest.raises(ValueError, match="does not match execution record"):
        capture_synthetic_exit_v2(
            confirmation=signal,
            initial_stop=entry_handoff.bound_initial_stop,
            risk_decision=risk_dec,
            entry_execution=entry_handoff.execution_evaluation,
            sized_entry=mismatched_sized,
            bars_by_index=bars_by_index,
        )
