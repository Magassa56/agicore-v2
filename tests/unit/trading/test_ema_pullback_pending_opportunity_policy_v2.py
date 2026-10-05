"""Synthetic causal lock tests, including the actual PR #298 counterexample."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import timedelta
from decimal import Decimal

import pytest

from agicore.trading import ema_pullback_pending_opportunity_policy_v2 as gate
from agicore.trading.directional_impulse_v2 import evaluate_directional_impulse_event_v2
from agicore.trading.ema_pullback_entry_confirmation_v2 import (
    EntryConfirmationStateV2,
    EntryConfirmationV2Error,
)
from agicore.trading.ema_pullback_entry_execution_v2 import EntryExecutionOpenV2
from agicore.trading.ema_pullback_entry_execution_v2 import EntryExecutionStateV2 as Execution
from agicore.trading.ema_pullback_open_position_signal_policy_v2 import PositionStateV2 as Position
from agicore.trading.ema_pullback_open_position_signal_policy_v2 import (
    advance_open_position_signal_policy_v2,
    resolve_position_stop_v2,
)
from agicore.trading.ema_pullback_risk_position_sizing_v2 import (
    RiskSizingDecisionV2 as Risk,
)
from agicore.trading.ema_pullback_structural_stop_trigger_fill_v2 import (
    StructuralStopTriggerPhaseV2 as StopPhase,
)
from agicore.trading.regime_context_v2 import (
    RegimeContextLifetimeState,
    RegimeDirection,
    RegimeEvent,
    RegimeEventType,
)
from agicore.trading.reversal_transition_v2 import (
    RejectionBarV2,
    evaluate_reversal_transition_event_v2,
)
from tests.unit.trading.test_ema_pullback_risk_position_sizing_v2 import GuardedBars, NoReads
from tests.unit.trading.test_ema_pullback_v2_pending_opportunity_audit import (
    SERIES,
    STRATEGY,
    _bars,
    _canonical,
    _ema_bars,
    _time,
)

State = gate.PendingOpportunityStateV2
Admission = gate.PendingSignalAdmissionStatusV2
DIRECTIONS = list(RegimeDirection)


def _event_pair(index, direction, kind="same", timestamp=None):
    timestamp = _time(index) if timestamp is None else timestamp
    opposite = RegimeDirection.SHORT if direction is RegimeDirection.LONG else RegimeDirection.LONG
    impulse = RegimeEvent(
        RegimeEventType.DIRECTIONAL_IMPULSE_EVENT,
        opposite if kind == "opposite" else direction,
        index,
        timestamp,
    )
    reversal = (
        RegimeEvent(
            RegimeEventType.REVERSAL_TRANSITION_EVENT,
            opposite if kind == "ambiguous" else direction,
            index,
            timestamp,
        )
        if kind in ("ambiguous", "dual")
        else None
    )
    return impulse, reversal


def _actual_events(raw, index):
    impulse = evaluate_directional_impulse_event_v2(
        impulse_candidate_bar_index=index, bars_by_index=GuardedBars(raw, range(index + 1))
    )
    prior = {}
    for i in range(index + 1):
        b = raw[i]
        prior[i] = RejectionBarV2(i, b.timestamp_utc, b.close, b.is_closed, b.open, b.high, b.low)
    reversal = evaluate_reversal_transition_event_v2(
        rejection_candidate_bar_index=index - 1,
        closed_bar_index=index,
        bars_by_index=GuardedBars(prior, range(index + 1)),
    )
    return impulse.event, None if reversal.event is None else reversal.event.as_regime_event()


def _close(book, raw, ema, index, *, events=None, timestamp=None, observation=None):
    return gate.advance_pending_opportunity_close_v2(
        previous=book,
        closed_bar_index=index,
        closed_bar_timestamp=_time(index) if timestamp is None else timestamp,
        source_bar_closed=True,
        bars_by_index=GuardedBars(ema, range(index + 1)),
        regime_events_at_close=lambda: _actual_events(raw, index) if events is None else events,
        stop_observation=observation,
    )


def _setup(direction, *, through=35, low=None, fail_last=False, future_poison=False):
    raw = _bars(direction)
    if low is not None:
        key = "low" if direction is RegimeDirection.LONG else "high"
        price = Decimal(low)
        raw[33] = replace(raw[33], **{key: price if key == "low" else Decimal(40000) - price})
    if fail_last:
        price = Decimal("20003.75")
        raw[35] = replace(
            raw[35], close=price if direction is RegimeDirection.LONG else Decimal(40000) - price
        )
    ema = _ema_bars(raw)
    if future_poison:
        for index in range(36, 39):
            raw[index] = ema[index] = NoReads()
    book = gate.begin_pending_opportunity_policy_v2(strategy_instance_id=STRATEGY, series_id=SERIES)
    for index in range(32, through + 1):
        book = _close(book, raw, ema, index)
    return book, raw, ema


def _assert_identical(*outputs):
    assert all(output == outputs[0] for output in outputs)
    assert all(_canonical(output) == _canonical(outputs[0]) for output in outputs)


def test_frozen_pending_constants():
    assert gate.MAX_ACTIONABLE_PENDING_OPPORTUNITIES_PER_SERIES == 1
    assert gate.PENDING_OPPORTUNITY_LOCK == "FIRST_CONSUMED_PULLBACK_LOCKS"
    assert gate.PENDING_OPPORTUNITY_QUEUE is False
    assert gate.PENDING_OPPORTUNITY_REPLACEMENT is False
    assert gate.OPPOSITE_EVENT_CANCELS_PENDING is False
    assert gate.SAME_DIRECTION_EVENT_REFRESHES_PENDING is False


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_lock_is_acquired_only_by_formal_consumption(direction):
    outcomes = []
    for _ in range(2):
        book, raw, ema = _setup(direction, through=32)
        assert book.state is State.IDLE
        assert book.active_opportunity is None
        assert book.positions.context.state is RegimeContextLifetimeState.ACTIVE
        book = _close(book, raw, ema, 33)
        assert book.state is State.AWAITING_CONFIRMATION
        assert book.positions.context.state is RegimeContextLifetimeState.CONSUMED
        assert len(book.opportunities) == 1
        assert book.active_opportunity.consumed_context.pullback_bar_index == 33
        assert (
            gate.execute_pending_opportunity_open_v2(previous=book, opening_bar=NoReads()) is book
        )
        outcomes.append(book)
    _assert_identical(*outcomes)


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("kind", ["same", "opposite", "ambiguous", "dual"])
def test_before_consumption_original_context_policy_is_preserved(direction, kind):
    book, raw, ema = _setup(direction, through=32)
    events = _event_pair(33, direction, kind)
    expected = advance_open_position_signal_policy_v2(
        previous=book.positions,
        closed_bar_index=33,
        closed_bar_timestamp=_time(33),
        source_bar_closed=True,
        bars_by_index=GuardedBars(ema, range(34)),
        directional_impulse_event=events[0],
        reversal_transition_event=events[1],
    )
    outputs = [_close(book, raw, ema, 33, events=events) for _ in range(2)]
    _assert_identical(*outputs)
    assert outputs[0].positions == expected
    assert (outputs[0].active_opportunity is not None) == (kind in ("same", "dual"))


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("kind", ["same", "opposite", "ambiguous", "dual"])
def test_pending_confirmation_suppresses_all_events_without_replacing_a(direction, kind):
    outputs = []
    for _ in range(2):
        before, raw, ema = _setup(direction, through=33)
        events = _event_pair(34, direction, kind)
        book = _close(before, raw, ema, 34, events=events)
        assert book.state is State.AWAITING_CONFIRMATION
        assert book.active_opportunity.confirmation.candidate.price_qualified is False
        assert (
            book.active_opportunity.consumed_context == before.active_opportunity.consumed_context
        )
        assert book.positions.context == before.positions.context
        assert len(book.opportunities) == 1
        decision = book.signal_decisions[-1]
        assert decision.status is Admission.SUPPRESSED_PENDING_OPPORTUNITY
        assert decision.suppressions
        for suppressed in decision.suppressions:
            assert suppressed.suppressed_event_bar_index == 34
            assert suppressed.suppressed_event_timestamp == _time(34)
            assert suppressed.active_opportunity_source_event_bar == 32
            assert suppressed.active_opportunity_pullback_bar == 33
            assert suppressed.active_opportunity_direction is direction
            assert suppressed.active_opportunity_state is State.AWAITING_CONFIRMATION
            assert suppressed.suppression_reason == "PENDING_OPPORTUNITY_ALREADY_ACTIVE"
        outputs.append(book)
    _assert_identical(*outputs)


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_pr298_actual_counterexample_cannot_construct_b_with_the_new_boundary(direction):
    outputs = [_setup(direction)[0] for _ in range(2)]
    _assert_identical(*outputs)
    book = outputs[0]
    assert book.signal_decisions[2].composition.events[0].event_bar_index == 34
    assert book.signal_decisions[2].status is Admission.SUPPRESSED_PENDING_OPPORTUNITY
    assert book.state is State.PENDING_ENTRY_EXECUTION
    assert (
        len(book.opportunities)
        == len(book.risks.decisions)
        == len(book.risks.executions.entries)
        == 1
    )
    assert book.opportunities[0].consumed_context.source_event_bar_index == 32
    assert book.opportunities[0].consumed_context.pullback_bar_index == 33
    assert book.risks.decisions[0].decision is Risk.APPROVE
    assert book.risks.decisions[0].approved_quantity == 2
    assert book.risks.executions.entries[0].expected_execution_bar_index == 36
    assert book.positions.context.source_event_bar_index != 34
    assert book.positions.signal_decisions[-1].pullback.pullback is None


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_approved_a_suppresses_new_same_close_event(direction):
    outputs = []
    for _ in range(2):
        book, raw, ema = _setup(direction, through=34)
        book = _close(book, raw, ema, 35, events=_event_pair(35, direction, "ambiguous"))
        assert book.state is State.PENDING_ENTRY_EXECUTION
        assert book.signal_decisions[-1].status is Admission.SUPPRESSED_PENDING_OPPORTUNITY
        assert len(book.opportunities) == 1
        assert book.positions.context.source_event_bar_index == 32
        outputs.append(book)
    _assert_identical(*outputs)


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("outcome", ["last_confirmation_fail", "risk_reject"])
def test_normal_terminal_close_releases_before_same_close_regime_admission(direction, outcome):
    outputs = []
    for _ in range(2):
        book, raw, ema = _setup(
            direction,
            through=34,
            low="19900" if outcome == "risk_reject" else None,
            fail_last=outcome == "last_confirmation_fail",
        )
        book = _close(book, raw, ema, 35, events=_event_pair(35, direction))
        assert book.state is State.IDLE
        assert book.active_opportunity is None
        expected = (
            State.TERMINAL_RISK_REJECTED
            if outcome == "risk_reject"
            else State.TERMINAL_CONFIRMATION_EXPIRED
        )
        assert book.opportunities[-1].state is expected
        assert book.signal_decisions[-1].state_at_signal_decision is State.IDLE
        assert book.signal_decisions[-1].status is Admission.ADMITTED
        assert book.positions.context.state is RegimeContextLifetimeState.ACTIVE
        assert book.positions.context.source_event_bar_index == 35
        assert book.positions.signal_decisions[-1].pullback.pullback is None
        assert not book.risks.executions.entries
        outputs.append(book)
    _assert_identical(*outputs)


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_confirmation_elapsed_expiry_releases_before_reads_and_raw_admission(direction):
    outputs = []
    for _ in range(2):
        book, _, _ = _setup(direction, through=33)
        timestamp = _time(33) + timedelta(minutes=3)
        book = gate.advance_pending_opportunity_close_v2(
            previous=book,
            closed_bar_index=34,
            closed_bar_timestamp=timestamp,
            source_bar_closed=True,
            bars_by_index=NoReads(),
            regime_events_at_close=lambda _ts=timestamp: _event_pair(34, direction, timestamp=_ts),
        )
        assert book.state is State.IDLE
        assert book.opportunities[-1].state is State.TERMINAL_CONFIRMATION_EXPIRED
        assert (
            book.opportunities[-1].confirmation.state
            is EntryConfirmationStateV2.EXPIRED_CONFIRMATION_ELAPSED_TIME
        )
        assert book.signal_decisions[-1].status is Admission.ADMITTED
        assert book.positions.context.source_event_bar_index == 34
        outputs.append(book)
    _assert_identical(*outputs)


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("expiry", ["missing", "gap", "only_later_bar"])
def test_normal_execution_expiry_releases_lock_without_a_deferred_b(direction, expiry):
    outputs = []
    for _ in range(2):
        book, raw, ema = _setup(direction)
        opening = {
            "missing": None,
            "gap": EntryExecutionOpenV2(36, _time(35) + timedelta(minutes=2), ema[36].open),
            "only_later_bar": EntryExecutionOpenV2(37, _time(37), ema[37].open),
        }[expiry]
        book = gate.execute_pending_opportunity_open_v2(previous=book, opening_bar=opening)
        assert book.state is State.IDLE
        assert book.opportunities[-1].state is State.TERMINAL_EXECUTION_NOT_FILLED
        assert not book.positions.positions
        assert not book.risks.filled_entries
        assert (
            gate.execute_pending_opportunity_open_v2(previous=book, opening_bar=NoReads()) is book
        )
        book = _close(book, raw, ema, 37)
        book = _close(book, raw, ema, 38)
        assert len(book.opportunities) == len(book.risks.decisions) == 1
        assert book.positions.context.source_event_bar_index == 32
        assert book.signal_decisions[2].suppressions[0].suppressed_event_bar_index == 34
        outputs.append(book)
    _assert_identical(*outputs)


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_execution_expiry_allows_only_a_new_event_at_a_later_close(direction):
    outputs = []
    for _ in range(2):
        book, raw, ema = _setup(direction)
        book = gate.execute_pending_opportunity_open_v2(previous=book, opening_bar=None)
        book = _close(book, raw, ema, 37, events=_event_pair(37, direction))
        assert book.signal_decisions[-1].status is Admission.ADMITTED
        assert book.positions.context.source_event_bar_index == 37
        assert book.positions.context.state is RegimeContextLifetimeState.ACTIVE
        assert book.active_opportunity is None
        outputs.append(book)
    _assert_identical(*outputs)


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("breach", [False, True])
def test_fill_transfers_ownership_atomically_including_immediate_breached_exit(direction, breach):
    outputs = []
    for _ in range(2):
        book, raw, ema = _setup(direction)
        price = book.risks.decisions[-1].initial_stop_price if breach else ema[36].open
        book = gate.execute_pending_opportunity_open_v2(
            previous=book, opening_bar=EntryExecutionOpenV2(36, _time(36), price)
        )
        assert len(book.positions.positions) == len(book.risks.filled_entries) == 1
        assert book.active_opportunity is None
        assert book.opportunities[-1].state is State.POSITION_OWNED
        assert book.risks.executions.entries[-1].execution_state is Execution.FILLED
        assert (
            gate.execute_pending_opportunity_open_v2(previous=book, opening_bar=NoReads()) is book
        )
        position = book.positions.positions[-1]
        if breach:
            assert book.state is State.IDLE
            assert position.exit.trigger_phase is StopPhase.ENTRY_OPEN
            assert (
                position.exit.base_stop_fill_price
                == position.entry.execution_price_before_costs
                == price
            )
        else:
            assert book.state is State.POSITION_OWNED
            assert position.exit is None
        book = _close(book, raw, ema, 36, events=_event_pair(36, direction), observation=ema[36])
        assert book.signal_decisions[-1].status is (
            Admission.ADMITTED if breach else Admission.SUPPRESSED_POSITION_OPEN
        )
        assert book.active_opportunity is None
        if breach:
            assert book.positions.context.source_event_bar_index == 36
        else:
            assert book.positions.context is None
        outputs.append(book)
    _assert_identical(*outputs)


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_frozen_position_exit_returns_to_idle_without_restoring_suppressed_sources(direction):
    book, raw, ema = _setup(direction)
    book = gate.execute_pending_opportunity_open_v2(
        previous=book, opening_bar=EntryExecutionOpenV2(36, _time(36), ema[36].open)
    )
    stop = book.risks.decisions[-1].initial_stop_price
    observation = replace(ema[36], **{"low" if direction is RegimeDirection.LONG else "high": stop})
    positions = resolve_position_stop_v2(
        previous=book.positions,
        known_bar_index=36,
        known_bar_timestamp=_time(36),
        observation=observation,
    )
    book = gate.adopt_pending_position_resolution_v2(previous=book, positions=positions)
    assert book.state is State.IDLE
    assert book.positions.position_state is Position.FLAT
    assert book.positions.context is None
    assert book.active_opportunity is None
    book = _close(book, raw, ema, 36, events=_event_pair(36, direction))
    assert book.positions.context.source_event_bar_index == 36
    assert len(book.opportunities) == 1


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_duplicate_close_and_future_mutation_have_no_effect(direction):
    book, _, _ = _setup(direction)
    poisoned, _, _ = _setup(direction, future_poison=True)
    _assert_identical(book, poisoned)
    duplicate = gate.advance_pending_opportunity_close_v2(
        previous=book,
        closed_bar_index=35,
        closed_bar_timestamp=_time(35),
        source_bar_closed=True,
        bars_by_index=NoReads(),
        regime_events_at_close=lambda: NoReads().forbidden,
    )
    assert duplicate is book
    assert len(duplicate.opportunities) == len(duplicate.risks.decisions) == 1


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("failure", ["clock", "missing_open", "nonfinite_open"])
def test_execution_failures_keep_lock_and_frozen_failure_evidence(direction, failure):
    before, _, ema = _setup(direction)
    opening = EntryExecutionOpenV2(
        36,
        _time(35) if failure == "clock" else _time(36),
        None
        if failure == "missing_open"
        else Decimal("NaN")
        if failure == "nonfinite_open"
        else ema[36].open,
    )
    with pytest.raises(gate.PendingOpportunityPolicyV2Error, match="fail-closed") as caught:
        gate.execute_pending_opportunity_open_v2(previous=before, opening_bar=opening)
    assert before.state is State.PENDING_ENTRY_EXECUTION
    assert len(before.opportunities) == 1
    result = caught.value.module_result
    assert result.executions.entries[-1].execution_state is (
        Execution.FAILED_INVALID_EXECUTION_CLOCK
        if failure == "clock"
        else Execution.FAILED_INVALID_EXECUTION_INPUT
    )
    assert not result.filled_entries


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_skipped_confirmation_and_changed_provenance_fail_closed(direction):
    book, raw, ema = _setup(direction, through=33)
    with pytest.raises(EntryConfirmationV2Error, match="processed in order"):
        _close(book, raw, ema, 35)
    assert book.state is State.AWAITING_CONFIRMATION
    with pytest.raises(gate.PendingOpportunityPolicyV2Error, match="repeat|backward"):
        replace(book, opportunities=(*book.opportunities, book.opportunities[0]))
    opportunity = book.opportunities[0]
    source = replace(opportunity.consumed_context, source_event_bar_index=31)
    forged = replace(opportunity.confirmation.opportunity, consumed_context=source)
    altered = replace(
        opportunity, confirmation=replace(opportunity.confirmation, opportunity=forged)
    )
    with pytest.raises(gate.PendingOpportunityPolicyV2Error, match="second context|consumption"):
        replace(book, opportunities=(altered,))
    with pytest.raises(FrozenInstanceError):
        opportunity.state = State.IDLE


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_skipped_stop_observation_does_not_admit_or_release(direction):
    book, raw, ema = _setup(direction)
    book = gate.execute_pending_opportunity_open_v2(
        previous=book, opening_bar=EntryExecutionOpenV2(36, _time(36), ema[36].open)
    )
    with pytest.raises(
        gate.PendingOpportunityPolicyV2Error, match="FAILED_INCOMPLETE_STOP_OBSERVATION"
    ) as caught:
        _close(book, raw, ema, 37, events=_event_pair(37, direction), observation=ema[37])
    assert book.state is State.POSITION_OWNED
    assert caught.value.module_result.position_state is not Position.FLAT


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("through", [33, 35])
def test_end_of_data_is_terminal_without_synthetic_confirmation_or_fill(direction, through):
    outputs = []
    for _ in range(2):
        book, _, _ = _setup(direction, through=through)
        finished = gate.finish_pending_opportunity_policy_v2(previous=book)
        assert finished.end_of_data
        assert finished.state is State.IDLE
        assert finished.active_opportunity is None
        assert not finished.positions.positions
        expected = (
            State.TERMINAL_INCOMPLETE_CONFIRMATION
            if through == 33
            else State.TERMINAL_EXECUTION_NOT_FILLED
        )
        assert finished.opportunities[-1].state is expected
        assert gate.finish_pending_opportunity_policy_v2(previous=finished) is finished
        assert (
            gate.execute_pending_opportunity_open_v2(previous=finished, opening_bar=NoReads())
            is finished
        )
        assert (
            gate.advance_pending_opportunity_close_v2(
                previous=finished,
                closed_bar_index=99,
                closed_bar_timestamp=_time(99),
                source_bar_closed=True,
                bars_by_index=NoReads(),
                regime_events_at_close=lambda: NoReads().forbidden,
            )
            is finished
        )
        outputs.append(finished)
    _assert_identical(*outputs)


def test_raw_supplier_is_evaluated_after_confirmation_stop_and_risk(monkeypatch):
    trace = []
    for name, label in (
        ("advance_entry_confirmation_momentum_v2", "confirmation"),
        ("register_initial_stop_v2", "stop"),
        ("register_risk_position_sizing_v2", "risk"),
    ):
        original = getattr(gate, name)

        def spy(*, _original=original, _label=label, **kwargs):
            result = _original(**kwargs)
            trace.append(_label)
            return result

        monkeypatch.setattr(gate, name, spy)
    outputs = []
    for _ in range(2):
        book, raw, ema = _setup(RegimeDirection.LONG, through=34)
        trace.clear()

        def supplier(_raw=raw):
            assert trace == ["confirmation", "stop", "risk"]
            trace.append("raw")
            return _actual_events(_raw, 35)

        output = gate.advance_pending_opportunity_close_v2(
            previous=book,
            closed_bar_index=35,
            closed_bar_timestamp=_time(35),
            source_bar_closed=True,
            bars_by_index=GuardedBars(ema, range(36)),
            regime_events_at_close=supplier,
        )
        assert trace == ["confirmation", "stop", "risk", "raw"]
        outputs.append(output)
    _assert_identical(*outputs)


def test_books_are_scoped_to_one_instance_and_series():
    first, _, _ = _setup(RegimeDirection.LONG, through=33)
    second, _, _ = _setup(RegimeDirection.SHORT, through=33)
    assert first.active_opportunity is not None and second.active_opportunity is not None
    with pytest.raises(gate.PendingOpportunityPolicyV2Error, match="one scope"):
        replace(first, risks=replace(first.risks, series_id="different-series"))


def test_long_short_exact_mirror_for_pending_risk_fill_and_stop():
    outputs = []
    for _ in range(2):
        long, _, long_bars = _setup(RegimeDirection.LONG)
        short, _, short_bars = _setup(RegimeDirection.SHORT)
        assert long.state is short.state is State.PENDING_ENTRY_EXECUTION
        long_risk, short_risk = long.risks.decisions[0], short.risks.decisions[0]
        assert long_risk.approved_quantity == short_risk.approved_quantity
        assert long_risk.risk_per_contract_usd == short_risk.risk_per_contract_usd
        assert long_risk.planned_total_risk_usd == short_risk.planned_total_risk_usd
        assert long_risk.initial_stop_price + short_risk.initial_stop_price == 40000
        assert long_risk.sizing_reference_price + short_risk.sizing_reference_price == 40000
        assert long_risk.confirmation.macd == -short_risk.confirmation.macd
        assert long_risk.confirmation.histogram == -short_risk.confirmation.histogram
        long = gate.execute_pending_opportunity_open_v2(
            previous=long, opening_bar=EntryExecutionOpenV2(36, _time(36), long_bars[36].open)
        )
        short = gate.execute_pending_opportunity_open_v2(
            previous=short, opening_bar=EntryExecutionOpenV2(36, _time(36), short_bars[36].open)
        )
        assert long.state is short.state is State.POSITION_OWNED
        long_entry, short_entry = long.risks.filled_entries[0], short.risks.filled_entries[0]
        assert (
            long_entry.execution.execution_price_before_costs
            + short_entry.execution.execution_price_before_costs
            == 40000
        )
        assert long_entry.risk_decision == long_risk
        assert short_entry.risk_decision == short_risk
        outputs.append((long, short))
    _assert_identical(*outputs)


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_end_of_data_with_position_cannot_accept_a_later_exit_or_synthetic_action(direction):
    outputs = []
    for _ in range(2):
        book, _, ema = _setup(direction)
        book = gate.execute_pending_opportunity_open_v2(
            previous=book, opening_bar=EntryExecutionOpenV2(36, _time(36), ema[36].open)
        )
        finished = gate.finish_pending_opportunity_policy_v2(previous=book)
        assert finished.state is State.POSITION_OWNED
        assert finished.positions.positions[-1].exit is None
        assert finished.active_opportunity is None
        assert (
            gate.adopt_pending_position_resolution_v2(previous=finished, positions=NoReads())
            is finished
        )
        outputs.append(finished)
    _assert_identical(*outputs)
