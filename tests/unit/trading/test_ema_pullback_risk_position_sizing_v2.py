"""Synthetic exact sizing with actual V2 confirmation, stop and execution provenance."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import FrozenInstanceError, dataclass, replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal, Inexact, localcontext
from fractions import Fraction

import pytest

from agicore.trading.ema20_pullback_v2 import EMA20PullbackBarV2
from agicore.trading.ema_pullback_entry_confirmation_v2 import (
    EntryConfirmationStateV2,
    advance_entry_confirmation_momentum_v2,
    begin_entry_confirmation_momentum_v2,
)
from agicore.trading.ema_pullback_entry_execution_v2 import (
    EntryExecutionBookV2,
    EntryExecutionOpenV2,
    EntryExecutionStateV2,
    register_entry_execution_v2,
)
from agicore.trading.ema_pullback_initial_stop_v2 import (
    InitialStopBookV2,
    InitialStopStateV2,
    InitialStopStatusV2,
    bind_initial_stop_to_entry_v2,
    register_initial_stop_v2,
)
from agicore.trading.ema_pullback_open_position_signal_policy_v2 import (
    OpenPositionSignalPolicyBookV2,
    PositionStateV2,
    advance_open_position_signal_policy_v2,
    apply_position_entry_fill_v2,
    resolve_position_stop_v2,
)
from agicore.trading.ema_pullback_risk_position_sizing_v2 import (
    INSTRUMENT,
    MAX_CONTRACTS,
    MIN_CONTRACTS,
    NO_RESIZING_AFTER_CONFIRMATION,
    PLANNED_RISK_BUDGET_USD,
    POINT_VALUE_USD,
    RISK_BUDGET_KIND,
    TICK_SIZE,
    TICK_VALUE_USD,
    RiskPositionSizingBookV2,
    RiskPositionSizingV2Error,
    RiskSizingStateV2,
    evaluate_risk_position_sizing_v2,
    execute_risk_approved_entry_open_v2,
    register_risk_position_sizing_v2,
)
from agicore.trading.ema_pullback_risk_position_sizing_v2 import RiskSizingDecisionV2 as Decision
from agicore.trading.ema_pullback_risk_position_sizing_v2 import (
    RiskSizingRejectionReasonV2 as Reason,
)
from agicore.trading.ema_pullback_structural_stop_trigger_fill_v2 import (
    StructuralStopExecutionBookV2,
    register_structural_stop_execution_v2,
)
from agicore.trading.regime_context_v2 import RegimeDirection, RegimeEvent, RegimeEventType

START = datetime(2026, 10, 4, 8, tzinfo=UTC)
DIRECTIONS = list(RegimeDirection)
FAMILIES = [
    (RegimeEventType.DIRECTIONAL_IMPULSE_EVENT,),
    (RegimeEventType.REVERSAL_TRANSITION_EVENT,),
    tuple(RegimeEventType),
]
INVALID_PRICES = [
    None,
    Decimal("NaN"),
    Decimal("sNaN"),
    Decimal("Infinity"),
    Decimal("-Infinity"),
    float("nan"),
    float("inf"),
    20003.0,
    "20003",
    True,
]


def _time(index):
    return START + timedelta(minutes=index)


def _bar(index, open_=20000, high=20000, low=20000, close=20000):
    return EMA20PullbackBarV2(
        index, _time(index), Fraction(open_), Fraction(high), Fraction(low), Fraction(close), True
    )


class NoReads:
    def __getattr__(self, name):
        raise AssertionError(f"forbidden input read: {name}")


class GuardedBars(Mapping):
    def __init__(self, bars, allowed):
        self.bars, self.allowed, self.reads = bars, set(allowed), []

    def __getitem__(self, index):
        assert index in self.allowed, f"forbidden bar {index}"
        self.reads.append(index)
        return self.bars[index]

    def __iter__(self):
        raise AssertionError("cannot scan future bars")

    def __len__(self):
        raise AssertionError("cannot count future bars")


class ReadGuard:
    def __init__(self, bar, allowed):
        self.bar, self.allowed, self.reads = bar, set(allowed), []

    def __getattr__(self, name):
        assert name in self.allowed, f"forbidden bar field {name}"
        self.reads.append(name)
        return getattr(self.bar, name)


@dataclass(frozen=True)
class CompleteBar:
    bar_index: int
    timestamp_utc: datetime
    open: object
    high: object = 30000
    low: object = 10000
    close: object = 20000
    volume: object = 1000
    is_closed: object = True


@dataclass(frozen=True)
class Setup:
    policy: OpenPositionSignalPolicyBookV2
    confirmation: object
    initial_stops: InitialStopBookV2
    bars: dict
    q: int

    @property
    def stop(self):
        return self.initial_stops.for_confirmation(self.confirmation.confirmation)


def _policy_close(policy, index, bars, events=None):
    return advance_open_position_signal_policy_v2(
        previous=policy,
        closed_bar_index=index,
        closed_bar_timestamp=_time(index),
        source_bar_closed=True,
        bars_by_index=bars,
        **({} if events is None else events),
    )


def _setup(
    direction=RegimeDirection.LONG,
    *,
    risk=Fraction(50),
    families=FAMILIES[0],
    event_index=32,
    reference_shift=0,
):
    """Use valid closed OHLC and causal indicators; only the rejection-side wick varies."""
    distance = Fraction(risk) / POINT_VALUE_USD
    assert distance >= Fraction(13, 4)
    bars = {index: _bar(index) for index in range(event_index)}
    bars[event_index] = _bar(event_index, 20002, 20002, 20002, 20002)
    bars[event_index + 1] = _bar(
        event_index + 1, 20002, 20005, Fraction(20003) - distance + TICK_SIZE, 20001
    )
    q = event_index + 2
    bars[q] = _bar(q, 20001, 20004, 20000, 20003)
    if direction is RegimeDirection.SHORT:
        bars = {
            index: replace(
                bar,
                open=40000 - bar.open,
                high=40000 - bar.low,
                low=40000 - bar.high,
                close=40000 - bar.close,
            )
            for index, bar in bars.items()
        }
    if reference_shift:
        bars = {
            index: replace(
                bar,
                open=bar.open + reference_shift,
                high=bar.high + reference_shift,
                low=bar.low + reference_shift,
                close=bar.close + reference_shift,
            )
            for index, bar in bars.items()
        }
    bars[q + 1] = CompleteBar(q + 1, _time(q + 1), bars[q].close)
    events = {
        family: RegimeEvent(family, direction, event_index, _time(event_index))
        for family in families
    }
    policy = OpenPositionSignalPolicyBookV2("synthetic-strategy", "synthetic-series")
    policy = _policy_close(
        policy,
        event_index,
        bars,
        {
            "directional_impulse_event": events.get(RegimeEventType.DIRECTIONAL_IMPULSE_EVENT),
            "reversal_transition_event": events.get(RegimeEventType.REVERSAL_TRANSITION_EVENT),
        },
    )
    policy = _policy_close(policy, event_index + 1, bars)
    pullback = policy.signal_decisions[-1].pullback
    assert pullback.pullback.pullback_qualified is True
    pending = begin_entry_confirmation_momentum_v2(
        pullback=pullback, pullback_bar=bars[event_index + 1]
    )
    confirmation = advance_entry_confirmation_momentum_v2(
        previous=pending,
        closed_bar_index=q,
        closed_bar_timestamp=_time(q),
        source_bar_closed=True,
        bars_by_index=GuardedBars(bars, range(q + 1)),
    )
    assert confirmation.entry_confirmation is True
    policy = _policy_close(policy, q, bars)
    stops = register_initial_stop_v2(
        previous=InitialStopBookV2(),
        confirmation=confirmation,
        bars_by_index=GuardedBars(bars, [q - 1, q]),
    )
    return Setup(policy, confirmation, stops, bars, q)


def _evaluate(setup, **overrides):
    arguments = {
        "instrument": INSTRUMENT,
        "closed_bar_index": setup.q,
        "closed_bar_timestamp": _time(setup.q),
        "source_bar_closed": True,
        "confirmation": setup.confirmation,
        "initial_stop": setup.stop,
        "position_state": PositionStateV2.FLAT,
        "bars_by_index": GuardedBars(setup.bars, [setup.q]),
    }
    arguments.update(overrides)
    return evaluate_risk_position_sizing_v2(**arguments)


def _register(setup, previous=None, **overrides):
    arguments = {
        "previous": RiskPositionSizingBookV2("synthetic-strategy", "synthetic-series")
        if previous is None
        else previous,
        "position_policy": setup.policy,
        "instrument": INSTRUMENT,
        "closed_bar_index": setup.q,
        "closed_bar_timestamp": _time(setup.q),
        "source_bar_closed": True,
        "confirmation": setup.confirmation,
        "initial_stop": setup.stop,
        "bars_by_index": GuardedBars(setup.bars, [setup.q]),
    }
    arguments.update(overrides)
    return register_risk_position_sizing_v2(**arguments)


def _changed_stop(setup, price):
    return replace(
        setup.stop,
        initial_stop_record=replace(setup.stop.initial_stop_record, initial_stop_price=price),
    )


def _execute(book, decision, bar):
    return execute_risk_approved_entry_open_v2(previous=book, decision=decision, opening_bar=bar)


def test_frozen_mnq_budget_and_contract_values_are_exact():
    assert INSTRUMENT == "MNQ"
    assert TICK_SIZE == Fraction(1, 4)
    assert POINT_VALUE_USD == Fraction(2)
    assert TICK_VALUE_USD == Fraction(1, 2) == TICK_SIZE * POINT_VALUE_USD
    assert PLANNED_RISK_BUDGET_USD == Fraction(100)
    assert (MIN_CONTRACTS, MAX_CONTRACTS) == (1, 2)
    assert RISK_BUDGET_KIND == "PLANNED_STRUCTURAL_PRICE_RISK_BUDGET"
    assert NO_RESIZING_AFTER_CONFIRMATION is True


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize(
    "risk,quantity",
    [
        (25, 2),
        (50, 2),
        (Fraction(101, 2), 1),
        (70, 1),
        (Fraction(199, 2), 1),
        (100, 1),
        (Fraction(201, 2), 0),
    ],
)
def test_exact_risk_boundaries_and_floor(direction, risk, quantity):
    setup = _setup(direction, risk=Fraction(risk))
    result = _evaluate(setup)
    assert result.sizing_reference_price == setup.bars[setup.q].close
    assert result.initial_stop_price == setup.stop.initial_stop
    assert result.stop_distance_points == Fraction(risk) / 2
    assert result.risk_per_contract_usd == risk
    assert result.raw_quantity == 100 // Fraction(risk)
    assert result.approved_quantity == quantity
    if quantity:
        assert result.decision is Decision.APPROVE
        assert result.planned_total_risk_usd == quantity * Fraction(risk) <= 100
        assert result.rejection_reason is None
    else:
        assert result.decision is Decision.REJECT
        assert result.state is RiskSizingStateV2.REJECTED_BY_RISK_ENGINE
        assert result.rejection_reason is Reason.RISK_PER_CONTRACT_EXCEEDS_BUDGET
        assert result.planned_total_risk_usd is None


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize(
    "distance,raw,quantity,total", [(15, 3, 2, 60), (35, 1, 1, 70), (55, 0, 0, None)]
)
def test_owner_examples_use_floor_then_cap(direction, distance, raw, quantity, total):
    result = _evaluate(_setup(direction, risk=Fraction(distance * 2)))
    assert result.stop_distance_points == distance
    assert result.raw_quantity == raw and result.approved_quantity == quantity
    assert result.planned_total_risk_usd == total


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_exact_budget_and_quantity_invariants_over_tick_grid(direction):
    for ticks in range(13, 221):
        result = _evaluate(_setup(direction, risk=Fraction(ticks, 2)))
        assert result.approved_quantity <= 2
        if result.decision is Decision.APPROVE:
            assert 1 <= result.approved_quantity <= 2
            assert 0 < result.planned_total_risk_usd <= Fraction(100)
        else:
            assert result.approved_quantity == 0 and result.risk_per_contract_usd > 100


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("representation", [int, Decimal, Fraction])
def test_decimal_conversion_and_fraction_arithmetic_ignore_rounding_context(
    direction, representation
):
    setup = _setup(direction, risk=Fraction(30))
    reference = representation(int(setup.bars[setup.q].close))
    stop_price = (
        Decimal(str(setup.stop.initial_stop))
        if representation is Decimal
        else setup.stop.initial_stop
    )
    bars = {setup.q: replace(setup.bars[setup.q], close=reference)}
    with localcontext() as ctx:
        ctx.prec = 1
        ctx.traps[Inexact] = True
        result = _evaluate(setup, initial_stop=_changed_stop(setup, stop_price), bars_by_index=bars)
    assert result.raw_quantity == 3 and result.approved_quantity == 2
    assert result.planned_total_risk_usd == Fraction(60)
    for value in [
        result.sizing_reference_price,
        result.initial_stop_price,
        result.stop_distance_points,
        result.risk_per_contract_usd,
        result.planned_total_risk_usd,
    ]:
        assert isinstance(value, Fraction)


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("relation", ["equal", "wrong_side"])
def test_touching_or_wrong_side_stop_rejects(direction, relation):
    setup = _setup(direction)
    price = setup.bars[setup.q].close
    if relation == "wrong_side":
        price += TICK_SIZE if direction is RegimeDirection.LONG else -TICK_SIZE
    result = _evaluate(setup, initial_stop=_changed_stop(setup, price))
    assert result.decision is Decision.REJECT
    assert result.rejection_reason is Reason.INVALID_STRUCTURAL_RISK_DISTANCE
    assert result.approved_quantity == 0


@pytest.mark.parametrize("instrument", ["NQ", "ES", "MNQ 03-26", None])
def test_non_mnq_instrument_rejects_without_reading_prices(instrument):
    result = _evaluate(_setup(), instrument=instrument, bars_by_index=NoReads())
    assert (
        result.decision is Decision.REJECT and result.rejection_reason is Reason.INVALID_INSTRUMENT
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("target", ["reference", "stop"])
@pytest.mark.parametrize("invalid", INVALID_PRICES)
def test_missing_nonfinite_and_inexact_inputs_reject_without_fallback(direction, target, invalid):
    setup = _setup(direction)
    overrides = (
        {"initial_stop": _changed_stop(setup, invalid)}
        if target == "stop"
        else {"bars_by_index": {setup.q: replace(setup.bars[setup.q], close=invalid)}}
    )
    result = _evaluate(setup, **overrides)
    assert result.decision is Decision.REJECT and result.approved_quantity == 0
    assert result.rejection_reason is (
        Reason.INVALID_INITIAL_STOP_INPUT
        if target == "stop"
        else Reason.INVALID_SIZING_REFERENCE_INPUT
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("target", ["reference", "stop"])
@pytest.mark.parametrize("delta", [Fraction(1, 100), Fraction(1, 1000000)])
def test_off_tick_prices_are_rejected_without_silent_rounding(direction, target, delta):
    setup = _setup(direction)
    overrides = (
        {"initial_stop": _changed_stop(setup, setup.stop.initial_stop + delta)}
        if target == "stop"
        else {
            "bars_by_index": {
                setup.q: replace(setup.bars[setup.q], close=setup.bars[setup.q].close + delta)
            }
        }
    )
    result = _evaluate(setup, **overrides)
    assert (
        result.decision is Decision.REJECT
        and result.rejection_reason is Reason.INVALID_MNQ_TICK_GRID
    )
    assert result.approved_quantity == 0


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_unavailable_stop_and_missing_reference_reject(direction):
    setup = _setup(direction)
    assert (
        _evaluate(setup, initial_stop=None, bars_by_index=NoReads()).rejection_reason
        is Reason.INITIAL_STOP_UNAVAILABLE
    )
    missing = replace(setup.stop, initial_stop_record=None)
    assert (
        _evaluate(setup, initial_stop=missing, bars_by_index=NoReads()).decision is Decision.REJECT
    )
    assert (
        _evaluate(setup, bars_by_index={}).rejection_reason is Reason.INVALID_SIZING_REFERENCE_INPUT
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize(
    "status",
    [
        InitialStopStatusV2.INVALID_STRUCTURAL_STOP_INPUT,
        InitialStopStatusV2.INCOMPLETE_STRUCTURAL_STOP_WINDOW,
    ],
)
def test_stop_status_must_be_evaluated(direction, status):
    setup = _setup(direction)
    result = _evaluate(
        setup, initial_stop=replace(setup.stop, status=status), bars_by_index=NoReads()
    )
    assert (
        result.decision is Decision.REJECT
        and result.rejection_reason is Reason.INITIAL_STOP_NOT_EVALUATED
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("failure", ["missing", "awaiting", "candidate_fail"])
def test_confirmation_must_be_formally_qualified(direction, failure):
    setup = _setup(direction)
    confirmation = (
        None
        if failure == "missing"
        else (
            replace(setup.confirmation, state=EntryConfirmationStateV2.AWAITING_CONFIRMATION)
            if failure == "awaiting"
            else replace(
                setup.confirmation,
                candidate=replace(setup.confirmation.candidate, entry_confirmation=False),
            )
        )
    )
    result = _evaluate(setup, confirmation=confirmation, bars_by_index=NoReads())
    assert (
        result.decision is Decision.REJECT
        and result.rejection_reason is Reason.UNQUALIFIED_CONFIRMATION
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("state", [PositionStateV2.OPEN_LONG, PositionStateV2.OPEN_SHORT])
def test_open_position_rejects_before_reference_price_read(direction, state):
    result = _evaluate(_setup(direction), position_state=state, bars_by_index=NoReads())
    assert (
        result.decision is Decision.REJECT
        and result.rejection_reason is Reason.POSITION_ALREADY_OPEN
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("field_name", ["bar_index", "timestamp_utc", "is_closed"])
def test_current_reference_metadata_must_match_closed_q(direction, field_name):
    setup = _setup(direction)
    value = {"bar_index": setup.q + 1, "timestamp_utc": _time(setup.q + 1), "is_closed": False}[
        field_name
    ]
    result = _evaluate(
        setup, bars_by_index={setup.q: replace(setup.bars[setup.q], **{field_name: value})}
    )
    assert (
        result.decision is Decision.REJECT
        and result.rejection_reason is Reason.INVALID_SIZING_CLOCK
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize(
    "field_name",
    [
        "stop_known_at_bar_index",
        "stop_known_at_timestamp",
        "structural_window_last_bar",
        "source_regime_event_direction",
        "ema_reference",
    ],
)
def test_stop_must_retain_causal_qualified_provenance(direction, field_name):
    setup = _setup(direction)
    value = {
        "stop_known_at_bar_index": setup.q + 1,
        "stop_known_at_timestamp": _time(setup.q + 1),
        "structural_window_last_bar": setup.q + 1,
        "source_regime_event_direction": RegimeDirection.SHORT
        if direction is RegimeDirection.LONG
        else RegimeDirection.LONG,
        "ema_reference": Fraction(99),
    }[field_name]
    stop = replace(
        setup.stop,
        initial_stop_record=replace(setup.stop.initial_stop_record, **{field_name: value}),
    )
    result = _evaluate(setup, initial_stop=stop, bars_by_index=NoReads())
    assert (
        result.decision is Decision.REJECT
        and result.rejection_reason is Reason.INVALID_INITIAL_STOP_PROVENANCE
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_only_close_q_and_known_metadata_are_read(direction):
    setup = _setup(direction)
    candidate = ReadGuard(setup.bars[setup.q], ["bar_index", "timestamp_utc", "is_closed", "close"])
    bars = GuardedBars({setup.q: candidate, setup.q + 1: NoReads()}, [setup.q])
    result = _evaluate(setup, bars_by_index=bars)
    assert result.decision is Decision.APPROVE
    assert bars.reads == [setup.q]
    assert set(candidate.reads) == {"bar_index", "timestamp_utc", "is_closed", "close"}
    assert result.sizing_decision_known_at_bar == setup.q
    assert result.sizing_decision_known_at_timestamp == _time(setup.q)


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("field_name", ["open", "high", "low", "close", "volume"])
def test_every_future_entry_bar_mutation_leaves_risk_decision_unchanged(direction, field_name):
    setup = _setup(direction)
    baseline = _evaluate(setup)
    bars = {
        **setup.bars,
        setup.q + 1: replace(setup.bars[setup.q + 1], **{field_name: NoReads()}),
        setup.q + 2: NoReads(),
        setup.q + 9: NoReads(),
    }
    mutated = _evaluate(setup, bars_by_index=GuardedBars(bars, [setup.q]))
    assert mutated == baseline


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_approve_registers_execution_only_after_quantity_is_known(direction):
    setup = _setup(direction)
    book = _register(setup)
    decision = book.decisions[0]
    assert decision.decision is Decision.APPROVE and decision.approved_quantity == 2
    assert len(book.executions.entries) == 1
    assert book.executions.entries[0].execution_state is EntryExecutionStateV2.PENDING_NEXT_BAR_OPEN
    assert not book.filled_entries
    assert (
        _execute(book, decision, EntryExecutionOpenV2(setup.q, _time(setup.q), NoReads())) is book
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("gap", ["adverse", "favorable", "at_stop", "beyond_stop"])
def test_execution_gap_never_resizes_and_breached_entry_history_is_preserved(direction, gap):
    setup = _setup(direction)
    book = _register(setup)
    decision = book.decisions[0]
    sign = 1 if direction is RegimeDirection.LONG else -1
    opening = {
        "adverse": decision.sizing_reference_price + sign * 40,
        "favorable": decision.sizing_reference_price - sign * 10,
        "at_stop": decision.initial_stop_price,
        "beyond_stop": decision.initial_stop_price - sign * 10,
    }[gap]
    bar = ReadGuard(
        CompleteBar(setup.q + 1, _time(setup.q + 1), opening),
        ["bar_index", "timestamp_utc", "open"],
    )
    filled = _execute(book, decision, bar)
    assert filled.decisions[0] is decision
    assert filled.filled_entries[0].quantity == decision.approved_quantity == 2
    assert filled.filled_entries[0].actual_entry_price == opening
    assert set(bar.reads) == {"bar_index", "timestamp_utc", "open"}
    assert filled.filled_entries[0].actual_entry_to_stop_distance_points == sign * (
        opening - decision.initial_stop_price
    )
    assert decision.planned_total_risk_usd == 100
    if gap == "adverse":
        assert (
            filled.filled_entries[0].actual_entry_to_stop_distance_points * POINT_VALUE_USD * 2
            > 100
        )
    stops = bind_initial_stop_to_entry_v2(
        previous=setup.initial_stops,
        confirmation=setup.confirmation.confirmation,
        executions=filled.executions,
    )
    monitoring = register_structural_stop_execution_v2(
        previous=StructuralStopExecutionBookV2(),
        initial_stops=stops,
        confirmation=setup.confirmation.confirmation,
    )
    opened = apply_position_entry_fill_v2(
        previous=setup.policy,
        executions=filled.executions,
        stops=monitoring,
        confirmation=setup.confirmation.confirmation,
    )
    assert opened.position_state is not PositionStateV2.FLAT
    if gap in ("at_stop", "beyond_stop"):
        assert (
            stops.for_confirmation(setup.confirmation.confirmation).stop_state
            is InitialStopStateV2.BREACHED_AT_ENTRY_OPEN
        )
        flat = resolve_position_stop_v2(
            previous=opened,
            known_bar_index=setup.q + 1,
            known_bar_timestamp=_time(setup.q + 1),
            observation=NoReads(),
        )
        assert flat.position_state is PositionStateV2.FLAT
        assert flat.positions[0].entry is filled.filled_entries[0].execution
        assert flat.positions[0].exit.base_stop_fill_price == opening
        assert filled.filled_entries[0].quantity == 2
    else:
        assert (
            stops.for_confirmation(setup.confirmation.confirmation).stop_state
            is InitialStopStateV2.ARMED
        )
    assert _execute(filled, decision, NoReads()) is filled


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("failure", ["budget", "instrument", "unqualified"])
def test_rejected_opportunity_never_creates_execution_or_reconsiders_later(direction, failure):
    setup = _setup(direction, risk=Fraction(110) if failure == "budget" else Fraction(50))
    overrides = (
        {"instrument": "NQ"}
        if failure == "instrument"
        else (
            {
                "confirmation": replace(
                    setup.confirmation, state=EntryConfirmationStateV2.AWAITING_CONFIRMATION
                )
            }
            if failure == "unqualified"
            else {}
        )
    )
    book = _register(setup, **overrides)
    decision = book.decisions[0]
    assert decision.state is RiskSizingStateV2.REJECTED_BY_RISK_ENGINE
    assert not book.executions.entries and not book.filled_entries
    for offset in (1, 2, 3, 10):
        assert _execute(book, decision, NoReads()) is book
        assert (
            _execute(
                book,
                decision,
                EntryExecutionOpenV2(
                    setup.q + offset, _time(setup.q + offset), decision.initial_stop_price
                ),
            )
            is book
        )
        later = _register(
            setup,
            book,
            closed_bar_index=setup.q + offset,
            closed_bar_timestamp=_time(setup.q + offset),
            initial_stop=NoReads(),
            bars_by_index=NoReads(),
        )
        assert later is book and later.decisions[0] is decision


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("risk", [Fraction(50), Fraction(110)])
def test_duplicate_evaluation_retains_same_immutable_decision_without_reads(direction, risk):
    setup = _setup(direction, risk=risk)
    book = _register(setup)
    again = _register(setup, book, initial_stop=NoReads(), bars_by_index=NoReads())
    assert again is book and again.decisions[0] is book.decisions[0]
    assert len(again.decisions) == 1


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_no_execution_resurrection_after_absent_next_bar(direction):
    setup = _setup(direction)
    book = _register(setup)
    decision = book.decisions[0]
    expired = _execute(book, decision, None)
    assert (
        expired.executions.entries[0].execution_state is EntryExecutionStateV2.EXPIRED_NO_EXECUTION
    )
    assert not expired.filled_entries
    assert _execute(expired, decision, NoReads()) is expired
    assert expired.decisions[0] is decision


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_formal_confirmation_without_admitted_position_policy_cannot_bypass_gate(direction):
    setup = _setup(direction)
    empty = OpenPositionSignalPolicyBookV2("synthetic-strategy", "synthetic-series")
    book = _register(setup, position_policy=empty)
    assert book.decisions[0].rejection_reason is Reason.INVALID_POSITION_POLICY_INPUT
    assert book.decisions[0].approved_quantity == 0
    assert not book.executions.entries


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_registered_decision_and_execution_provenance_are_immutable(direction):
    setup = _setup(direction)
    book = _register(setup)
    decision = book.decisions[0]
    assert decision.initial_stop_record is setup.stop.initial_stop_record
    assert decision.confirmation is setup.confirmation.confirmation
    assert decision.consumed_context is setup.confirmation.opportunity.consumed_context
    assert (
        decision.source_regime_event_types
        == setup.confirmation.confirmation.source_regime_event_types
    )
    assert decision.source_regime_event_bar_index == 32
    assert decision.pullback_bar_index == 33 and decision.confirmation_bar_index == 34
    assert decision.ema_reference == setup.confirmation.confirmation.ema_reference
    with pytest.raises(FrozenInstanceError):
        decision.approved_quantity = 1
    with pytest.raises(FrozenInstanceError):
        book.decisions = ()
    with pytest.raises(RiskPositionSizingV2Error, match="provenance cannot change"):
        _execute(
            book,
            replace(
                decision,
                rejection_reason=Reason.INVALID_INSTRUMENT,
                decision=Decision.REJECT,
                approved_quantity=0,
                planned_total_risk_usd=None,
            ),
            NoReads(),
        )
    with pytest.raises(RiskPositionSizingV2Error, match="REJECT cannot create"):
        rejected = _register(_setup(direction, risk=Fraction(110)))
        replace(
            rejected,
            executions=register_entry_execution_v2(
                previous=EntryExecutionBookV2(), confirmation=setup.confirmation
            ),
        )


@pytest.mark.parametrize("families", FAMILIES)
def test_long_short_and_regime_family_symmetry(families):
    long, short = (
        _setup(RegimeDirection.LONG, risk=Fraction(70), families=families),
        _setup(RegimeDirection.SHORT, risk=Fraction(70), families=families),
    )
    left, right = _evaluate(long), _evaluate(short)
    assert left.sizing_reference_price + right.sizing_reference_price == 40000
    assert left.initial_stop_price + right.initial_stop_price == 40000
    assert left.stop_distance_points == right.stop_distance_points == 35
    assert left.approved_quantity == right.approved_quantity == 1
    assert left.risk_per_contract_usd == right.risk_per_contract_usd == 70
    assert left.planned_total_risk_usd == right.planned_total_risk_usd == 70
    assert left.source_regime_event_types == right.source_regime_event_types == families


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_previous_rejected_trade_and_event_family_do_not_change_identical_risk_quantity(direction):
    old_setup = _setup(direction, risk=Fraction(110))
    history = _register(old_setup)
    new_setup = _setup(direction, risk=Fraction(70), event_index=42, families=FAMILIES[1])
    fresh = _register(new_setup)
    with_history = _register(new_setup, history)
    assert fresh.decisions[0].approved_quantity == with_history.decisions[-1].approved_quantity == 1
    assert (
        fresh.decisions[0].risk_per_contract_usd
        == with_history.decisions[-1].risk_per_contract_usd
        == 70
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_twenty_point_example_uses_confirmation_close_and_exact_structural_stop(direction):
    setup = _setup(
        direction,
        risk=Fraction(40),
        reference_shift=7 if direction is RegimeDirection.LONG else 13,
    )
    decision = _evaluate(setup)
    assert decision.sizing_reference_price == 20010
    assert decision.initial_stop_price == (19990 if direction is RegimeDirection.LONG else 20030)
    assert decision.stop_distance_points == 20
    assert decision.risk_per_contract_usd == 40
    assert decision.approved_quantity == 2
    assert decision.planned_total_risk_usd == 80


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_real_open_position_blocks_new_risk_authorization_before_any_price_read(direction):
    setup = _setup(direction)
    book = _register(setup)
    filled = _execute(book, book.decisions[0], setup.bars[setup.q + 1])
    stops = bind_initial_stop_to_entry_v2(
        previous=setup.initial_stops,
        confirmation=setup.confirmation.confirmation,
        executions=filled.executions,
    )
    monitoring = register_structural_stop_execution_v2(
        previous=StructuralStopExecutionBookV2(),
        initial_stops=stops,
        confirmation=setup.confirmation.confirmation,
    )
    opened = apply_position_entry_fill_v2(
        previous=setup.policy,
        executions=filled.executions,
        stops=monitoring,
        confirmation=setup.confirmation.confirmation,
    )
    next_setup = _setup(direction, event_index=42)
    rejected = _register(
        next_setup,
        filled,
        position_policy=opened,
        bars_by_index=NoReads(),
    )
    assert rejected.decisions[-1].decision is Decision.REJECT
    assert rejected.decisions[-1].rejection_reason is Reason.POSITION_ALREADY_OPEN
    assert rejected.executions is filled.executions
    assert rejected.filled_entries is filled.filled_entries
    assert len(opened.positions) == 1
