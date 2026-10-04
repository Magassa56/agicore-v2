"""Synthetic causal exit phases using actual V2 admission, risk, entry and stop links."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import timedelta
from decimal import Decimal, Inexact, localcontext
from fractions import Fraction
from types import SimpleNamespace

import pytest

from agicore.trading.ema20_pullback_v2 import (
    EMA20PullbackBarV2,
    EMA20StatusV2,
    evaluate_ema20_v2,
)
from agicore.trading.ema_pullback_exit_policy_v2 import (
    BREAKEVEN,
    EXIT_1,
    EXIT_2,
    EXIT_ORDER_SEMANTICS,
    MAX_EXIT_EXECUTION_AGE_CLOSED_BARS,
    MAX_EXIT_EXECUTION_ELAPSED_TIME,
    SESSION_EXIT,
    TAKE_PROFIT,
    TIME_EXIT,
    TRAILING_STOP,
    ExitPolicyEndStateV2,
    ExitPolicyV2Error,
    begin_exit_policy_v2,
    finish_exit_policy_v2,
    process_exit_policy_close_v2,
    process_exit_policy_open_v2,
)
from agicore.trading.ema_pullback_exit_policy_v2 import (
    EMA20ExitExecutionStateV2 as ExitState,
)
from agicore.trading.ema_pullback_fees_and_slippage_v2 import (
    FeesAndSlippageV2Error,
    account_ema20_exit_fill_v2,
    account_structural_stop_fill_v2,
)
from agicore.trading.ema_pullback_open_position_signal_policy_v2 import (
    PositionSignalAdmissionStatusV2,
    PositionStateV2,
    advance_open_position_signal_policy_v2,
    apply_position_entry_fill_v2,
)
from agicore.trading.ema_pullback_structural_stop_trigger_fill_v2 import (
    StructuralStopExecutionStateV2 as StopState,
)
from agicore.trading.ema_pullback_structural_stop_trigger_fill_v2 import (
    StructuralStopTriggerPhaseV2,
)
from agicore.trading.regime_context_v2 import RegimeDirection, RegimeEvent, RegimeEventType
from tests.unit.trading.test_ema_pullback_fees_and_slippage_v2 import _filled
from tests.unit.trading.test_ema_pullback_risk_position_sizing_v2 import (
    CompleteBar,
    GuardedBars,
    NoReads,
    ReadGuard,
    _time,
)

DIRECTIONS = list(RegimeDirection)


def _begin(direction=RegimeDirection.LONG, quantity=2, base=Fraction(20000)):
    flow = _filled(direction, quantity, base)
    positions = apply_position_entry_fill_v2(
        previous=flow.setup.policy,
        executions=flow.risk.executions,
        stops=flow.stops,
        confirmation=flow.entry.execution.confirmation,
    )
    return flow, begin_exit_policy_v2(positions=positions, risk_sizing=flow.risk)


def _open(book, index, price=Fraction(20000), timestamp=None):
    observation = ReadGuard(
        CompleteBar(index, _time(index) if timestamp is None else timestamp, price),
        {"bar_index", "timestamp_utc", "open"},
    )
    return process_exit_policy_open_v2(previous=book, observation=observation)


def _close(book, index, bars, adverse=None):
    bar = bars[index]
    is_long = book.positions.active_position.entry.execution_side is RegimeDirection.LONG
    extreme = "low" if is_long else "high"
    observation = ReadGuard(
        SimpleNamespace(
            bar_index=index,
            timestamp_utc=bar.timestamp_utc,
            **{extreme: getattr(bar, extreme) if adverse is None else adverse},
        ),
        {"bar_index", "timestamp_utc", extreme},
    )
    return process_exit_policy_close_v2(
        previous=book,
        closed_bar_index=index,
        closed_bar_timestamp=bar.timestamp_utc,
        source_bar_closed=True,
        bars_by_index=GuardedBars(bars, range(index + 1)),
        stop_observation=observation,
    )


def _candidate(flow, relation=-1, index=None, bars=None, timestamp=None):
    index = flow.entry.execution.execution_bar_index if index is None else index
    bars = dict(flow.setup.bars if bars is None else bars)
    prior = evaluate_ema20_v2(through_bar_index=index - 1, bars_by_index=bars).ema20
    sign = 1 if flow.decision.direction is RegimeDirection.LONG else -1
    close = prior + sign * relation
    opening = flow.entry.execution.execution_price_before_costs
    bars[index] = EMA20PullbackBarV2(
        index,
        _time(index) if timestamp is None else timestamp,
        opening,
        max(opening, close) + 1,
        min(opening, close) - 1,
        close,
        True,
    )
    return bars


def _pending(direction=RegimeDirection.LONG, quantity=2):
    flow, book = _begin(direction, quantity)
    e = flow.entry.execution.execution_bar_index
    bars = _candidate(flow)
    book = _close(_open(book, e), e, bars)
    assert book.pending_ema_exit is not None
    return flow, book, bars


def test_exactly_two_exits_without_additional_management_rules():
    assert (EXIT_1, EXIT_2) == ("IMMUTABLE_STRUCTURAL_STOP", "EMA20_POSITION_EXIT")
    assert TAKE_PROFIT is BREAKEVEN is TRAILING_STOP is TIME_EXIT is SESSION_EXIT is None
    assert EXIT_ORDER_SEMANTICS == "MARKET"
    assert MAX_EXIT_EXECUTION_AGE_CLOSED_BARS == 1
    assert MAX_EXIT_EXECUTION_ELAPSED_TIME == timedelta(minutes=1)


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("relation", [-1, 0, 1])
def test_strict_close_side_signals_and_equality_holds(direction, relation):
    flow, book = _begin(direction)
    e = flow.entry.execution.execution_bar_index
    bars = _candidate(flow, relation)
    result = _close(_open(book, e), e, bars)
    decision = result.close_decisions[-1]
    assert (decision.signal is not None) is (relation < 0)
    assert result.positions.position_state is (
        PositionStateV2.OPEN_LONG
        if direction is RegimeDirection.LONG
        else PositionStateV2.OPEN_SHORT
    )
    prior = evaluate_ema20_v2(through_bar_index=e - 1, bars_by_index=bars).ema20
    assert decision.ema.ema20 == prior + Fraction(2, 21) * (bars[e].close - prior)
    assert decision.ema.last_close == bars[e].close
    if relation == 0:
        assert decision.ema.ema20 == decision.ema.last_close


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_arbitrarily_small_strict_difference_is_not_rounded(direction):
    flow, book = _begin(direction)
    e = flow.entry.execution.execution_bar_index
    with localcontext() as context:
        context.prec = 2
        context.traps[Inexact] = True
        bars = _candidate(flow, -Fraction(1, 10**80))
        result = _close(_open(book, e), e, bars)
    assert result.pending_ema_exit is not None
    assert isinstance(result.pending_ema_exit.signal.ema20_at_signal, Fraction)


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("quantity", [1, 2])
def test_signal_on_entry_close_fills_only_at_next_open_and_costs_once(direction, quantity):
    flow, pending, bars = _pending(direction, quantity)
    r = flow.entry.execution.execution_bar_index
    signal = pending.pending_ema_exit.signal
    assert signal.exit_signal_bar_index == r
    assert signal.exit_signal_timestamp == _time(r)
    assert signal.initial_stop_at_entry == pending.positions.active_position.initial_stop_at_entry
    assert signal.close_at_signal == bars[r].close
    assert signal.ema20_at_signal == pending.close_decisions[-1].ema.ema20
    assert (
        process_exit_policy_open_v2(previous=pending, observation=SimpleNamespace(bar_index=r))
        is pending
    )
    assert pending.costs.trades[0].net_realized_pnl_usd is None
    base = Fraction(20002)
    result = _open(pending, r + 1, base)
    execution = result.ema_executions[-1]
    assert execution.state is ExitState.FILLED_EMA20_EXIT
    assert execution.fill.signal is signal
    assert execution.fill.exit_execution_bar_index == r + 1
    assert execution.fill.exit_execution_timestamp == _time(r + 1)
    assert execution.fill.base_exit_fill_price == base
    assert execution.fill.exit_reason == EXIT_2
    assert result.positions.position_state is PositionStateV2.FLAT
    assert result.positions.positions[-1].exit is execution.fill
    assert result.positions.active_stop is None
    record = result.costs.for_decision(flow.decision)
    sign = 1 if direction is RegimeDirection.LONG else -1
    assert record.exit_type == EXIT_2 and record.stop_fill is None
    assert record.ema_exit_fill is execution.fill
    assert record.quantity == flow.entry.quantity == quantity
    assert record.entry.base_fill_price == 20000
    assert record.exit.base_fill_price == base
    assert record.exit.effective_fill_price_after_slippage == base - sign * Fraction(1, 4)
    assert record.total_fees_usd == quantity * Fraction(102, 100)
    assert record.diagnostic_total_slippage_cost_usd == quantity
    assert record.gross_price_pnl_usd == (sign * (base - 20000) - Fraction(1, 2)) * 2 * quantity
    assert record.net_realized_pnl_usd == record.gross_price_pnl_usd - record.total_fees_usd
    assert _open(result, r + 2, NoReads()) is result
    assert (
        account_ema20_exit_fill_v2(
            previous=result.costs,
            risk_sizing=flow.risk,
            decision=flow.decision,
            positions=result.positions,
        )
        is result.costs
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("distance", [0, 3])
@pytest.mark.parametrize("gap", [timedelta(minutes=1), timedelta(hours=12)])
def test_stop_open_gap_beats_pending_market_exit_including_equal_stop(direction, distance, gap):
    flow, pending, _ = _pending(direction)
    r = flow.entry.execution.execution_bar_index
    sign = 1 if direction is RegimeDirection.LONG else -1
    base = flow.decision.initial_stop_price - sign * distance
    result = _open(pending, r + 1, base, _time(r) + gap)
    assert result.positions.position_state is PositionStateV2.FLAT
    assert result.ema_executions[-1].state is ExitState.CANCELLED_STRUCTURAL_STOP
    fill = result.positions.positions[-1].exit
    assert fill.trigger_phase is StructuralStopTriggerPhaseV2.BAR_OPEN_GAP
    assert fill.base_stop_fill_price == base
    assert result.costs.trades[0].exit_type == "STRUCTURAL_STOP"
    assert result.costs.trades[0].ema_exit_fill is None
    assert result.costs.trades[0].exit.base_fill_price == base
    assert result.costs.trades[0].total_fees_usd == Fraction(204, 100)
    assert (
        process_exit_policy_close_v2(
            previous=result,
            closed_bar_index=r + 1,
            closed_bar_timestamp=_time(r) + gap,
            source_bar_closed=True,
            bars_by_index=NoReads(),
            stop_observation=NoReads(),
        )
        is result
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("distance", [0, 2])
def test_intrabar_stop_closes_before_ema_evaluation_without_reading_close(direction, distance):
    flow, book = _begin(direction)
    e = flow.entry.execution.execution_bar_index
    book = _open(book, e)
    extreme = "low" if direction is RegimeDirection.LONG else "high"
    sign = 1 if direction is RegimeDirection.LONG else -1
    result = process_exit_policy_close_v2(
        previous=book,
        closed_bar_index=e,
        closed_bar_timestamp=_time(e),
        source_bar_closed=True,
        bars_by_index=NoReads(),
        stop_observation=SimpleNamespace(
            bar_index=e,
            timestamp_utc=_time(e),
            **{extreme: flow.decision.initial_stop_price - sign * distance},
        ),
    )
    assert result.positions.position_state is PositionStateV2.FLAT
    assert result.close_decisions == result.ema_executions == ()
    assert (
        result.positions.positions[-1].exit.trigger_phase is StructuralStopTriggerPhaseV2.INTRABAR
    )
    assert result.costs.trades[0].exit.base_fill_price == flow.decision.initial_stop_price


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_missing_next_bar_expires_without_fill_or_roll_forward(direction):
    flow, pending, _ = _pending(direction)
    r = flow.entry.execution.execution_bar_index
    expired = process_exit_policy_open_v2(previous=pending, observation=None)
    assert expired.ema_executions[-1].state is ExitState.EXPIRED_NO_EXIT_EXECUTION
    assert expired.positions.active_stop.stop_execution_state is StopState.ARMED
    assert expired.costs.trades[0].net_realized_pnl_usd is None
    assert process_exit_policy_open_v2(previous=expired, observation=None) is expired
    later = _open(expired, r + 2)
    assert (
        later.positions.active_stop.stop_execution_state
        is StopState.FAILED_INCOMPLETE_STOP_OBSERVATION
    )
    assert later.ema_executions[-1].state is ExitState.EXPIRED_NO_EXIT_EXECUTION
    assert later.positions.active_position is not None and later.costs.trades[0].exit is None


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize(
    "gap", [timedelta(minutes=1), timedelta(minutes=1, microseconds=1), timedelta(hours=16)]
)
def test_exact_minute_is_eligible_but_larger_gap_expires_ema_not_stop(direction, gap):
    flow, pending, bars = _pending(direction)
    r = flow.entry.execution.execution_bar_index
    timestamp = _time(r) + gap
    result = _open(pending, r + 1, timestamp=timestamp)
    if gap == timedelta(minutes=1):
        assert result.ema_executions[-1].state is ExitState.FILLED_EMA20_EXIT
        return
    assert result.ema_executions[-1].state is ExitState.EXPIRED_EXIT_GAP
    assert result.positions.active_stop.stop_execution_state is StopState.ARMED
    assert result.costs.trades[0].exit is None
    bars = _candidate(flow, relation=1, index=r + 1, bars=bars, timestamp=timestamp)
    result = _close(result, r + 1, bars)
    assert result.positions.active_stop.last_observed_bar_index == r + 1
    assert result.positions.active_stop.stop_execution_state is StopState.ARMED
    assert result.pending_ema_exit is None
    # The protective stop continues across the same session/data gap.
    sign = 1 if direction is RegimeDirection.LONG else -1
    stopped = _open(
        result, r + 2, flow.decision.initial_stop_price - sign, timestamp + timedelta(minutes=1)
    )
    assert stopped.positions.position_state is PositionStateV2.FLAT
    assert stopped.costs.trades[0].exit_type == "STRUCTURAL_STOP"


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_expired_market_order_does_not_fill_on_following_open(direction):
    flow, pending, bars = _pending(direction)
    r = flow.entry.execution.execution_bar_index
    timestamp = _time(r) + timedelta(hours=10)
    expired = _open(pending, r + 1, timestamp=timestamp)
    bars = _candidate(flow, relation=1, index=r + 1, bars=bars, timestamp=timestamp)
    expired = _close(expired, r + 1, bars)
    result = _open(expired, r + 2, timestamp=timestamp + timedelta(minutes=1))
    assert result.ema_executions[-1].state is ExitState.EXPIRED_EXIT_GAP
    assert result.positions.active_position is not None
    assert result.costs.trades[0].exit is None


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_no_session_reset_uses_the_identical_rational_ema_definition(direction):
    flow, book = _begin(direction)
    r = flow.entry.execution.execution_bar_index
    bars = _candidate(flow, relation=1)
    book = _close(_open(book, r), r, bars)
    timestamp = _time(r) + timedelta(hours=16)
    bars = _candidate(flow, index=r + 1, bars=bars, timestamp=timestamp)
    result = _close(_open(book, r + 1, timestamp=timestamp), r + 1, bars)
    expected = sum((bars[i].close for i in range(20)), Fraction(0)) / 20
    for index in range(20, r + 2):
        expected += Fraction(2, 21) * (bars[index].close - expected)
    assert result.close_decisions[-1].ema.ema20 == expected
    assert result.pending_ema_exit.signal.ema20_at_signal == expected
    assert len(result.close_decisions) == 2


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_first_and_repeated_phase_calls_are_idempotent_without_market_reads(direction):
    flow, book = _begin(direction)
    r = flow.entry.execution.execution_bar_index
    opened = _open(book, r)
    assert (
        process_exit_policy_open_v2(previous=opened, observation=SimpleNamespace(bar_index=r))
        is opened
    )
    bars = _candidate(flow)
    pending = _close(opened, r, bars)
    assert (
        process_exit_policy_close_v2(
            previous=pending,
            closed_bar_index=r,
            closed_bar_timestamp=_time(r),
            source_bar_closed=True,
            bars_by_index=NoReads(),
            stop_observation=NoReads(),
        )
        is pending
    )
    filled = _open(pending, r + 1)
    assert process_exit_policy_open_v2(previous=filled, observation=NoReads()) is filled
    assert finish_exit_policy_v2(
        previous=finish_exit_policy_v2(previous=filled)
    ) == finish_exit_policy_v2(previous=filled)
    assert len(filled.positions.positions) == len(filled.costs.trades) == 1


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("signal", [False, True])
def test_end_of_data_never_forces_an_exit_or_realized_pnl(direction, signal):
    flow, book = _begin(direction)
    r = flow.entry.execution.execution_bar_index
    bars = _candidate(flow, relation=-1 if signal else 1)
    book = _close(_open(book, r), r, bars)
    ended = finish_exit_policy_v2(previous=book)
    assert ended.end_state is ExitPolicyEndStateV2.OPEN_UNREALIZED
    assert ended.positions.active_position is not None
    assert ended.positions.active_stop.stop_execution_state is StopState.ARMED
    assert ended.costs.trades[0].exit is ended.costs.trades[0].net_realized_pnl_usd is None
    assert ended.costs.trades[0].entry.fee_usd == Fraction(102, 100)
    assert ended.pending_ema_exit is None
    if signal:
        assert ended.ema_executions[-1].state is ExitState.EXPIRED_NO_EXIT_EXECUTION
    assert process_exit_policy_open_v2(previous=ended, observation=NoReads()) is ended


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("quantity", [1, 2])
def test_breached_entry_remains_real_and_exits_same_open_without_ohlcv_reads(direction, quantity):
    base = Fraction(19900 if direction is RegimeDirection.LONG else 20100)
    flow, book = _begin(direction, quantity, base)
    assert book.positions.active_position is not None
    result = process_exit_policy_open_v2(previous=book, observation=NoReads())
    assert result.positions.positions[0].entry == flow.entry.execution
    assert result.positions.positions[0].exit.base_stop_fill_price == base
    assert result.positions.position_state is PositionStateV2.FLAT
    assert result.costs.trades[0].net_realized_pnl_usd == -quantity * Fraction(202, 100)
    assert result.ema_executions == ()


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_future_mutation_cannot_change_known_signal_or_execution(direction):
    flow, book = _begin(direction)
    r = flow.entry.execution.execution_bar_index
    bars = _candidate(flow)
    mutated = dict(bars)
    mutated[r + 1] = NoReads()
    mutated[r + 100] = NoReads()
    first = _close(_open(book, r), r, bars)
    second = _close(_open(book, r), r, mutated)
    assert first == second
    for field in ("high", "low", "close", "volume"):
        data = CompleteBar(r + 1, _time(r + 1), Fraction(20000))
        data = replace(data, **{field: NoReads()})
        observation = ReadGuard(data, {"bar_index", "timestamp_utc", "open"})
        assert process_exit_policy_open_v2(previous=first, observation=observation) == _open(
            first, r + 1
        )
    altered_open = _open(first, r + 1, Fraction(20001))
    assert altered_open.ema_executions[-1].fill.signal == first.pending_ema_exit.signal
    assert altered_open.ema_executions[-1].fill.base_exit_fill_price == 20001
    assert altered_open.costs.trades[0].quantity == flow.entry.quantity


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("invalid", [None, Decimal("NaN"), Decimal("Infinity"), 20000.0])
def test_invalid_required_close_fails_closed_without_ema_exit(direction, invalid):
    flow, book = _begin(direction)
    r = flow.entry.execution.execution_bar_index
    bars = _candidate(flow)
    bars[10] = replace(bars[10], close=invalid)
    result = _close(_open(book, r), r, bars)
    assert result.close_decisions[-1].ema.status is EMA20StatusV2.INVALID_EMA_INPUT
    assert result.pending_ema_exit is None
    assert result.positions.active_position is not None


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_ema_exit_returns_flat_for_fresh_close_regime_admission(direction):
    flow, pending, _ = _pending(direction)
    r = flow.entry.execution.execution_bar_index + 1
    result = _open(pending, r)
    event = RegimeEvent(RegimeEventType.DIRECTIONAL_IMPULSE_EVENT, direction, r, _time(r))
    positions = advance_open_position_signal_policy_v2(
        previous=result.positions,
        closed_bar_index=r,
        closed_bar_timestamp=_time(r),
        source_bar_closed=True,
        bars_by_index=NoReads(),
        directional_impulse_event=event,
    )
    assert positions.signal_decisions[-1].status is PositionSignalAdmissionStatusV2.ADMITTED
    assert positions.context.source_event_bar_index == r
    assert positions.context.first_eligible_pullback_bar == r + 1
    assert positions.positions[0].exit == result.positions.positions[0].exit


def test_long_short_mirror_has_equal_costs_pnl_and_phase_provenance():
    long_flow, long_pending, _ = _pending(RegimeDirection.LONG)
    short_flow, short_pending, _ = _pending(RegimeDirection.SHORT)
    r = long_flow.entry.execution.execution_bar_index + 1
    long = _open(long_pending, r, Fraction(20002))
    short = _open(short_pending, r, Fraction(19998))
    assert long.costs.trades[0].net_realized_pnl_usd == short.costs.trades[0].net_realized_pnl_usd
    assert long.costs.trades[0].total_fees_usd == short.costs.trades[0].total_fees_usd
    assert (
        long_pending.pending_ema_exit.signal.close_at_signal
        + short_pending.pending_ema_exit.signal.close_at_signal
        == 40000
    )
    assert (
        long_pending.pending_ema_exit.signal.ema20_at_signal
        + short_pending.pending_ema_exit.signal.ema20_at_signal
        == 40000
    )
    assert (
        long.positions.positions[0].exit.exit_execution_timestamp
        == short.positions.positions[0].exit.exit_execution_timestamp
    )
    assert long_flow.entry.quantity == short_flow.entry.quantity


def test_provenance_is_frozen_and_inconsistent_reaccounting_is_rejected():
    flow, pending, _ = _pending()
    result = _open(pending, flow.entry.execution.execution_bar_index + 1)
    fill = result.positions.positions[0].exit
    with pytest.raises(FrozenInstanceError):
        fill.base_exit_fill_price = Fraction(1)
    with pytest.raises(FrozenInstanceError):
        fill.signal.ema20_at_signal = Fraction(1)
    altered = replace(fill, base_exit_fill_price=fill.base_exit_fill_price + 1)
    positions = replace(
        result.positions, positions=(replace(result.positions.positions[0], exit=altered),)
    )
    with pytest.raises(FeesAndSlippageV2Error, match="provenance cannot change"):
        account_ema20_exit_fill_v2(
            previous=result.costs,
            risk_sizing=flow.risk,
            decision=flow.decision,
            positions=positions,
        )
    # A stale ARMED stop snapshot cannot add another exit or erase the EMA exit.
    assert (
        account_structural_stop_fill_v2(
            previous=result.costs, risk_sizing=flow.risk, decision=flow.decision, stops=flow.stops
        )
        is result.costs
    )


@pytest.mark.parametrize("closed", [False, True])
def test_close_requires_the_processed_open_of_the_same_bar(closed):
    flow, book = _begin()
    r = flow.entry.execution.execution_bar_index
    with pytest.raises(ExitPolicyV2Error, match="processed Open"):
        process_exit_policy_close_v2(
            previous=book,
            closed_bar_index=r,
            closed_bar_timestamp=_time(r),
            source_bar_closed=closed,
            bars_by_index=NoReads(),
            stop_observation=NoReads(),
        )


class CloseOnlyBar(EMA20PullbackBarV2):
    """EMA cannot inspect even historical Open/High/Low/Volume."""

    def __getattribute__(self, name):
        if name in {"open", "high", "low", "volume"}:
            raise AssertionError(f"EMA read forbidden field {name}")
        return super().__getattribute__(name)


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_ema_computation_reads_only_closed_closes_and_metadata(direction):
    flow, book = _begin(direction)
    r = flow.entry.execution.execution_bar_index
    bars = _candidate(flow)
    guarded = {
        index: CloseOnlyBar(
            bar.bar_index, bar.timestamp_utc, bar.open, bar.high, bar.low, bar.close, bar.is_closed
        )
        for index, bar in bars.items()
    }
    extreme = "low" if direction is RegimeDirection.LONG else "high"
    result = process_exit_policy_close_v2(
        previous=_open(book, r),
        closed_bar_index=r,
        closed_bar_timestamp=_time(r),
        source_bar_closed=True,
        bars_by_index=GuardedBars(guarded, range(r + 1)),
        stop_observation=SimpleNamespace(
            bar_index=r, timestamp_utc=_time(r), **{extreme: getattr(bars[r], extreme)}
        ),
    )
    assert result.pending_ema_exit is not None


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_completed_stop_observation_cannot_be_from_another_bar(direction):
    flow, book = _begin(direction)
    r = flow.entry.execution.execution_bar_index
    with pytest.raises(ExitPolicyV2Error, match="this exact bar"):
        process_exit_policy_close_v2(
            previous=_open(book, r),
            closed_bar_index=r,
            closed_bar_timestamp=_time(r),
            source_bar_closed=True,
            bars_by_index=NoReads(),
            stop_observation=SimpleNamespace(bar_index=r + 1, timestamp_utc=_time(r + 1)),
        )


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_invalid_adverse_extreme_prevents_ema_signal_fail_closed(direction):
    flow, book = _begin(direction)
    r = flow.entry.execution.execution_bar_index
    extreme = "low" if direction is RegimeDirection.LONG else "high"
    invalid = Fraction(20001 if direction is RegimeDirection.LONG else 19999)
    result = process_exit_policy_close_v2(
        previous=_open(book, r),
        closed_bar_index=r,
        closed_bar_timestamp=_time(r),
        source_bar_closed=True,
        bars_by_index=NoReads(),
        stop_observation=SimpleNamespace(bar_index=r, timestamp_utc=_time(r), **{extreme: invalid}),
    )
    assert (
        result.positions.active_stop.stop_execution_state
        is StopState.FAILED_INVALID_STOP_OBSERVATION
    )
    assert result.positions.active_position is not None
    assert result.ema_executions == () and result.costs.trades[0].exit is None
    assert process_exit_policy_open_v2(previous=result, observation=NoReads()) is result


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("invalid", [None, Decimal("NaN"), Decimal("Infinity"), 20000.0])
def test_invalid_next_open_cannot_create_an_ema_fill(direction, invalid):
    flow, pending, _ = _pending(direction)
    r = flow.entry.execution.execution_bar_index + 1
    result = _open(pending, r, invalid)
    assert result.ema_executions[-1].state is ExitState.FAILED_INVALID_EXIT_INPUT
    assert (
        result.positions.active_stop.stop_execution_state
        is StopState.FAILED_INVALID_STOP_OBSERVATION
    )
    assert result.positions.active_position is not None and result.costs.trades[0].exit is None
    assert process_exit_policy_open_v2(previous=result, observation=NoReads()) is result


@pytest.mark.parametrize("opening", [0, -1])
def test_nonpositive_short_market_exit_open_fails_without_replacing_the_price(opening):
    flow, pending, _ = _pending(RegimeDirection.SHORT)
    result = _open(pending, flow.entry.execution.execution_bar_index + 1, Fraction(opening))
    assert result.ema_executions[-1].state is ExitState.FAILED_INVALID_EXIT_INPUT
    assert result.positions.active_stop.stop_execution_state is StopState.ARMED
    assert result.costs.trades[0].exit is None


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("delta", [timedelta(0), timedelta(seconds=-1)])
def test_nonincreasing_clock_fails_closed_before_market_exit(direction, delta):
    flow, pending, _ = _pending(direction)
    r = flow.entry.execution.execution_bar_index
    result = _open(pending, r + 1, timestamp=_time(r) + delta)
    assert result.ema_executions[-1].state is ExitState.FAILED_STOP_OBSERVATION
    assert (
        result.positions.active_stop.stop_execution_state
        is StopState.FAILED_INVALID_STOP_OBSERVATION
    )
    assert result.costs.trades[0].exit is None


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_current_close_changes_current_ema_but_no_already_known_price(direction):
    flow, book = _begin(direction)
    r = flow.entry.execution.execution_bar_index
    first = _candidate(flow, relation=-1)
    second = _candidate(flow, relation=-2)
    a = _close(_open(book, r), r, first)
    b = _close(_open(book, r), r, second)
    assert (
        a.pending_ema_exit.signal.ema20_at_signal - b.pending_ema_exit.signal.ema20_at_signal
        == Fraction(2, 21) * (first[r].close - second[r].close)
    )
    assert a.positions.positions[0].entry == b.positions.positions[0].entry == flow.entry.execution
    assert (
        a.pending_ema_exit.signal.initial_stop_at_entry
        == b.pending_ema_exit.signal.initial_stop_at_entry
    )
    assert a.costs.trades[0].quantity == b.costs.trades[0].quantity


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_after_gap_expiry_only_a_new_close_signal_can_authorize_another_exit(direction):
    flow, pending, bars = _pending(direction)
    r = flow.entry.execution.execution_bar_index
    timestamp = _time(r) + timedelta(hours=12)
    expired = _open(pending, r + 1, timestamp=timestamp)
    bars = _candidate(flow, index=r + 1, bars=bars, timestamp=timestamp)
    new_pending = _close(expired, r + 1, bars)
    assert new_pending.ema_executions[0].state is ExitState.EXPIRED_EXIT_GAP
    assert new_pending.pending_ema_exit.signal.exit_signal_bar_index == r + 1
    filled = _open(new_pending, r + 2, timestamp=timestamp + timedelta(minutes=1))
    assert filled.ema_executions[0].state is ExitState.EXPIRED_EXIT_GAP
    assert filled.ema_executions[1].state is ExitState.FILLED_EMA20_EXIT
    assert filled.positions.positions[0].exit.signal == new_pending.pending_ema_exit.signal


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_pending_exit_quantity_and_close_provenance_cannot_be_changed(direction):
    _, pending, _ = _pending(direction)
    evaluation = pending.ema_executions[-1]
    altered = replace(evaluation, signal=replace(evaluation.signal, quantity=1))
    with pytest.raises(ExitPolicyV2Error, match="frozen quantity"):
        replace(pending, ema_executions=(altered,))
    with pytest.raises(ExitPolicyV2Error, match="evaluated Close"):
        replace(pending, close_decisions=())
    with pytest.raises(ExitPolicyV2Error, match="duplicate EMA exits"):
        replace(pending, ema_executions=(evaluation, evaluation))


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_end_of_data_retains_an_already_known_breached_entry_stop_fill(direction):
    _, book = _begin(
        direction, base=Fraction(19900 if direction is RegimeDirection.LONG else 20100)
    )
    ended = finish_exit_policy_v2(previous=book)
    assert ended.end_state is ExitPolicyEndStateV2.FLAT
    assert (
        ended.positions.positions[0].exit.trigger_phase is StructuralStopTriggerPhaseV2.ENTRY_OPEN
    )
    assert ended.costs.trades[0].net_realized_pnl_usd == -Fraction(404, 100)
