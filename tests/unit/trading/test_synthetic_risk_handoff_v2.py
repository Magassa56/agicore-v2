"""Unit tests for synthetic confirmation and stop handoff to risk decision."""

from __future__ import annotations

from dataclasses import replace
from fractions import Fraction

import pytest

from agicore.trading.ema20_pullback_v2 import EMA20PullbackBarV2
from agicore.trading.ema_pullback_initial_stop_v2 import (
    InitialStopAtEntryV2,
    InitialStopEvaluationV2,
    InitialStopStatusV2,
)
from agicore.trading.ema_pullback_risk_position_sizing_v2 import (
    INSTRUMENT,
    PositionStateV2,
    RiskPositionSizingV2Error,
    RiskSizingDecisionV2,
    RiskSizingRejectionReasonV2,
)
from agicore.trading.synthetic_confirmation_fixture_v2 import generate_confirmation_fixture
from agicore.trading.synthetic_confirmation_replay_v2 import replay_confirmation_native
from agicore.trading.synthetic_risk_handoff_v2 import (
    SyntheticRiskHandoffV2,
    capture_synthetic_risk_v2,
)
from agicore.trading.synthetic_stop_handoff_v2 import capture_synthetic_stop_v2
from agicore.trading.ema_pullback_v2_development_replay import parse_ninjatrader_last_rows_v2


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
    return signal, stop_eval, candidate_bar


def test_long_accepted_scenario():
    signal, stop_eval, candidate_bar = _setup_handoff("confirmation-long-v1")
    handoff = capture_synthetic_risk_v2(
        confirmation=signal,
        initial_stop=stop_eval,
        closed_candidate=candidate_bar,
    )
    assert isinstance(handoff, SyntheticRiskHandoffV2)
    decision = handoff.decision
    assert decision.decision is RiskSizingDecisionV2.APPROVE
    assert decision.rejection_reason is None
    assert decision.approved_quantity == 2
    assert decision.planned_total_risk_usd == Fraction(17, 1)
    assert decision.stop_distance_points == Fraction(17, 4)
    assert decision.instrument == INSTRUMENT
    assert decision.position_state_at_sizing is PositionStateV2.FLAT


def test_short_accepted_scenario():
    signal, stop_eval, candidate_bar = _setup_handoff("confirmation-short-v1")
    handoff = capture_synthetic_risk_v2(
        confirmation=signal,
        initial_stop=stop_eval,
        closed_candidate=candidate_bar,
    )
    assert isinstance(handoff, SyntheticRiskHandoffV2)
    decision = handoff.decision
    assert decision.decision is RiskSizingDecisionV2.APPROVE
    assert decision.rejection_reason is None
    assert decision.approved_quantity == 2
    assert decision.planned_total_risk_usd == Fraction(17, 1)
    assert decision.stop_distance_points == Fraction(17, 4)


def test_long_rejected_scenario():
    signal, stop_eval, candidate_bar = _setup_handoff("confirmation-long-rejected-v1")
    handoff = capture_synthetic_risk_v2(
        confirmation=signal,
        initial_stop=stop_eval,
        closed_candidate=candidate_bar,
    )
    decision = handoff.decision
    assert decision.decision is RiskSizingDecisionV2.REJECT
    assert decision.rejection_reason is RiskSizingRejectionReasonV2.RISK_PER_CONTRACT_EXCEEDS_BUDGET
    assert decision.approved_quantity == 0
    assert decision.planned_total_risk_usd is None
    assert decision.stop_distance_points == Fraction(129, 2)
    assert decision.risk_per_contract_usd == Fraction(129, 1)


def test_short_rejected_scenario():
    signal, stop_eval, candidate_bar = _setup_handoff("confirmation-short-rejected-v1")
    handoff = capture_synthetic_risk_v2(
        confirmation=signal,
        initial_stop=stop_eval,
        closed_candidate=candidate_bar,
    )
    decision = handoff.decision
    assert decision.decision is RiskSizingDecisionV2.REJECT
    assert decision.rejection_reason is RiskSizingRejectionReasonV2.RISK_PER_CONTRACT_EXCEEDS_BUDGET
    assert decision.approved_quantity == 0
    assert decision.planned_total_risk_usd is None
    assert decision.stop_distance_points == Fraction(129, 2)
    assert decision.risk_per_contract_usd == Fraction(129, 1)


def test_reject_already_open_position():
    signal, stop_eval, candidate_bar = _setup_handoff("confirmation-long-v1")
    handoff = capture_synthetic_risk_v2(
        confirmation=signal,
        initial_stop=stop_eval,
        closed_candidate=candidate_bar,
        position_state=PositionStateV2.OPEN_LONG,
    )
    assert handoff.decision.decision is RiskSizingDecisionV2.REJECT
    assert handoff.decision.rejection_reason is RiskSizingRejectionReasonV2.POSITION_ALREADY_OPEN


def test_reject_unclosed_candidate_bar():
    signal, stop_eval, candidate_bar = _setup_handoff("confirmation-long-v1")
    unclosed = replace(candidate_bar, is_closed=False)
    with pytest.raises(ValueError, match="closed candidate bar"):
        capture_synthetic_risk_v2(
            confirmation=signal,
            initial_stop=stop_eval,
            closed_candidate=unclosed,
        )


def test_reject_mismatched_candidate_clock():
    signal, stop_eval, candidate_bar = _setup_handoff("confirmation-long-v1")
    wrong_bar = replace(candidate_bar, bar_index=candidate_bar.bar_index + 1)
    with pytest.raises(ValueError, match="closed candidate bar"):
        capture_synthetic_risk_v2(
            confirmation=signal,
            initial_stop=stop_eval,
            closed_candidate=wrong_bar,
        )


def test_reject_entry_bound_stop():
    signal, stop_eval, candidate_bar = _setup_handoff("confirmation-long-v1")
    mock_entry = replace(stop_eval, at_entry=object())
    with pytest.raises(ValueError, match="entry-bound"):
        capture_synthetic_risk_v2(
            confirmation=signal,
            initial_stop=mock_entry,
            closed_candidate=candidate_bar,
        )


def test_reject_unevaluated_stop():
    signal, stop_eval, candidate_bar = _setup_handoff("confirmation-long-v1")
    uneval = replace(stop_eval, status=InitialStopStatusV2.INVALID_STRUCTURAL_STOP_INPUT)
    with pytest.raises(RiskPositionSizingV2Error, match="must be evaluated"):
        capture_synthetic_risk_v2(
            confirmation=signal,
            initial_stop=uneval,
            closed_candidate=candidate_bar,
        )


def test_reject_mismatched_stop_confirmation():
    signal_long, stop_long, candidate_long = _setup_handoff("confirmation-long-v1")
    signal_short, stop_short, _ = _setup_handoff("confirmation-short-v1")
    with pytest.raises(RiskPositionSizingV2Error, match="confirmation provenance"):
        capture_synthetic_risk_v2(
            confirmation=signal_long,
            initial_stop=stop_short,
            closed_candidate=candidate_long,
        )
