"""Synthetic exact accounting downstream of actual frozen V2 fills, never replay."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, dataclass, replace
from decimal import ROUND_HALF_UP, Decimal, Inexact, localcontext
from fractions import Fraction
from types import SimpleNamespace

import pytest

from agicore.trading.ema_pullback_entry_execution_v2 import EntryExecutionOpenV2
from agicore.trading.ema_pullback_fees_and_slippage_v2 import (
    ADVERSE_SLIPPAGE_POINTS_PER_FILL,
    ADVERSE_SLIPPAGE_TICKS_PER_FILL,
    EXTRA_SPREAD_CHARGE,
    FEE_PER_CONTRACT_PER_FILL_USD,
    NO_POST_CONFIRMATION_RESIZING,
    POINT_VALUE_USD,
    ROUND_TO_CENTS,
    SLIPPAGE_ACCOUNTED_EXACTLY_ONCE,
    SPREAD_MODEL,
    TICK_SIZE,
    TICK_VALUE_USD,
    FeesAndSlippageBookV2,
    FeesAndSlippageV2Error,
    FillActionV2,
    account_entry_fill_v2,
    account_structural_stop_fill_v2,
    calculate_fill_cost_v2,
    report_usd_cents_v2,
)
from agicore.trading.ema_pullback_initial_stop_v2 import bind_initial_stop_to_entry_v2
from agicore.trading.ema_pullback_structural_stop_trigger_fill_v2 import (
    StructuralStopExecutionBookV2,
    StructuralStopTriggerPhaseV2,
    observe_structural_stop_v2,
    register_structural_stop_execution_v2,
)
from agicore.trading.regime_context_v2 import RegimeDirection
from tests.unit.trading.test_ema_pullback_risk_position_sizing_v2 import (
    NoReads,
    _execute,
    _register,
    _setup,
    _time,
)

DIRECTIONS = list(RegimeDirection)


@dataclass(frozen=True)
class Flow:
    setup: object
    risk: object
    stops: object

    @property
    def decision(self):
        return self.risk.decisions[-1]

    @property
    def entry(self):
        return self.risk.filled_entries[-1]


def _filled(direction=RegimeDirection.LONG, quantity=2, base=Fraction(20000), shift=0):
    setup = _setup(direction, risk=Fraction(50 if quantity == 2 else 70), reference_shift=shift)
    risk = _register(setup)
    risk = _execute(
        risk, risk.decisions[0], EntryExecutionOpenV2(setup.q + 1, _time(setup.q + 1), base)
    )
    assert risk.filled_entries[0].quantity == quantity
    bound = bind_initial_stop_to_entry_v2(
        previous=setup.initial_stops,
        confirmation=setup.confirmation.confirmation,
        executions=risk.executions,
    )
    stops = register_structural_stop_execution_v2(
        previous=StructuralStopExecutionBookV2(),
        initial_stops=bound,
        confirmation=setup.confirmation.confirmation,
    )
    return Flow(setup, risk, stops)


def _account_entry(flow, previous=None):
    return account_entry_fill_v2(
        previous=FeesAndSlippageBookV2(flow.risk.strategy_instance_id, flow.risk.series_id)
        if previous is None
        else previous,
        risk_sizing=flow.risk,
        decision=flow.decision,
    )


def _account_exit(flow, previous=None, stops=None):
    return account_structural_stop_fill_v2(
        previous=_account_entry(flow) if previous is None else previous,
        risk_sizing=flow.risk,
        decision=flow.decision,
        stops=flow.stops if stops is None else stops,
    )


def _observe(flow, *, index, stops=None, **fields):
    return observe_structural_stop_v2(
        previous=flow.stops if stops is None else stops,
        confirmation=flow.entry.execution.confirmation,
        observation=SimpleNamespace(bar_index=index, timestamp_utc=_time(index), **fields),
    )


def _touch_on_entry(flow):
    extreme = "low" if flow.decision.direction is RegimeDirection.LONG else "high"
    return _observe(
        flow,
        index=flow.entry.execution.execution_bar_index,
        **{extreme: flow.decision.initial_stop_price},
    )


def test_constants_intentionally_match_v1_convention_without_reusing_v1_runtime():
    from agicore.trading.ema_pullback_v1_mnq import (
        COMMISSION_PER_SIDE_USD,
        ENTRY_SLIPPAGE_TICKS,
        STRUCTURAL_STOP_SLIPPAGE_TICKS,
    )

    assert TICK_SIZE == ADVERSE_SLIPPAGE_POINTS_PER_FILL == Fraction(1, 4)
    assert POINT_VALUE_USD == Fraction(2)
    assert TICK_VALUE_USD == TICK_SIZE * POINT_VALUE_USD == Fraction(1, 2)
    assert FEE_PER_CONTRACT_PER_FILL_USD == Fraction(COMMISSION_PER_SIDE_USD) == Fraction(51, 100)
    assert (
        ADVERSE_SLIPPAGE_TICKS_PER_FILL
        == ENTRY_SLIPPAGE_TICKS
        == STRUCTURAL_STOP_SLIPPAGE_TICKS
        == 1
    )
    assert SPREAD_MODEL == "ABSORBED_IN_SLIPPAGE" and EXTRA_SPREAD_CHARGE == Fraction(0)
    assert SLIPPAGE_ACCOUNTED_EXACTLY_ONCE is True
    assert NO_POST_CONFIRMATION_RESIZING is True
    assert ROUND_TO_CENTS == ROUND_HALF_UP


@pytest.mark.parametrize("quantity", [1, 2])
@pytest.mark.parametrize("action", list(FillActionV2))
def test_each_action_has_one_exact_adverse_tick_and_per_contract_fee(action, quantity):
    cost = calculate_fill_cost_v2(
        base_fill_price=Decimal("20000.00"), action=action, quantity=quantity
    )
    sign = 1 if action in (FillActionV2.BUY, FillActionV2.BUY_TO_COVER) else -1
    assert cost.base_fill_price == Fraction(20000)
    assert cost.effective_fill_price_after_slippage == Fraction(20000) + sign * Fraction(1, 4)
    assert cost.effective_fill_price_after_slippage != cost.base_fill_price
    assert cost.slippage_ticks == 1
    assert cost.fee_usd == Fraction(51 * quantity, 100)
    assert cost.slippage_cost_usd == Fraction(quantity, 2)
    for value in (
        cost.base_fill_price,
        cost.effective_fill_price_after_slippage,
        cost.fee_usd,
        cost.slippage_cost_usd,
    ):
        assert isinstance(value, Fraction)


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("quantity", [1, 2])
def test_actual_entry_immediately_pays_costs_but_open_trade_has_no_realized_pnl(
    direction, quantity
):
    flow = _filled(direction, quantity)
    book = _account_entry(flow)
    record = book.for_decision(flow.decision)
    assert record.sized_entry is flow.entry
    assert (
        record.entry.base_fill_price == flow.entry.execution.execution_price_before_costs == 20000
    )
    assert record.entry.fee_usd == record.total_fees_usd == Fraction(51 * quantity, 100)
    assert record.diagnostic_total_slippage_cost_usd == Fraction(quantity, 2)
    assert record.exit_type is record.exit is record.stop_fill is None
    assert record.gross_price_pnl_usd is record.net_realized_pnl_usd is None
    assert _account_exit(flow, book) is book  # ARMED is not an exit.
    assert flow.decision.planned_total_risk_usd == quantity * flow.decision.risk_per_contract_usd


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("quantity", [1, 2])
def test_round_trip_exact_pnl_fees_and_slippage_once(direction, quantity):
    flow = _filled(direction, quantity)
    open_book = _account_entry(flow)
    stops = _touch_on_entry(flow)
    closed = _account_exit(flow, open_book, stops)
    record = closed.trades[0]
    assert record.exit_type == "STRUCTURAL_STOP"
    assert record.stop_fill is stops.entries[0].fill
    assert (
        record.exit.base_fill_price
        == record.stop_fill.base_stop_fill_price
        == flow.decision.initial_stop_price
    )
    assert record.entry is open_book.trades[0].entry
    assert open_book.trades[0].exit is None
    assert record.quantity == flow.decision.approved_quantity == quantity
    sign = 1 if direction is RegimeDirection.LONG else -1
    base_pnl = sign * (record.exit.base_fill_price - record.entry.base_fill_price) * 2 * quantity
    diagnostic_slippage = Fraction(quantity)
    assert record.diagnostic_total_slippage_cost_usd == diagnostic_slippage
    assert record.gross_price_pnl_usd == base_pnl - diagnostic_slippage
    assert record.total_fees_usd == Fraction(102 * quantity, 100)
    assert record.net_realized_pnl_usd == base_pnl - diagnostic_slippage - Fraction(
        102 * quantity, 100
    )
    assert record.net_realized_pnl_usd == record.gross_price_pnl_usd - record.total_fees_usd
    assert (
        record.net_realized_pnl_usd
        != record.gross_price_pnl_usd - record.total_fees_usd - diagnostic_slippage
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_owner_entry_and_stop_price_examples_preserve_base_prices(direction):
    sign = 1 if direction is RegimeDirection.LONG else -1
    flow = _filled(direction, shift=sign * 12)
    book = _account_exit(flow, stops=_touch_on_entry(flow))
    record = book.trades[0]
    assert record.entry.base_fill_price == 20000
    assert record.entry.effective_fill_price_after_slippage == Fraction(20000) + sign * Fraction(
        1, 4
    )
    assert record.exit.base_fill_price == 20000 - sign * 10
    assert record.exit.effective_fill_price_after_slippage == Fraction(20000) - sign * Fraction(
        41, 4
    )
    assert flow.entry.execution.execution_price_before_costs == 20000
    assert record.stop_fill.base_stop_fill_price == 20000 - sign * 10
    with pytest.raises(FrozenInstanceError):
        record.entry.base_fill_price = Fraction(1)
    with pytest.raises(FrozenInstanceError):
        record.stop_fill.base_stop_fill_price = Fraction(1)


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_gap_stop_retains_gap_base_before_applying_slippage(direction):
    sign = 1 if direction is RegimeDirection.LONG else -1
    flow = _filled(direction, base=Fraction(20000 + sign * 30), shift=sign * 22)
    e = flow.entry.execution.execution_bar_index
    extreme = "low" if direction is RegimeDirection.LONG else "high"
    armed = _observe(flow, index=e, **{extreme: flow.entry.actual_entry_price})
    gap_base = Fraction(20000 - sign * 5)
    gap = _observe(flow, index=e + 1, stops=armed, open=gap_base, **{extreme: NoReads()})
    record = _account_exit(flow, stops=gap).trades[0]
    assert record.stop_fill.trigger_phase is StructuralStopTriggerPhaseV2.BAR_OPEN_GAP
    assert record.stop_fill.initial_stop_price == 20000
    assert record.exit.base_fill_price == gap_base
    assert record.exit.effective_fill_price_after_slippage == gap_base - sign * Fraction(1, 4)
    assert record.stop_fill.base_stop_fill_price == gap_base != record.stop_fill.initial_stop_price


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("quantity", [1, 2])
@pytest.mark.parametrize("beyond_stop", [False, True])
def test_breached_entry_pays_two_actual_fills_and_never_has_zero_net_pnl(
    direction, quantity, beyond_stop
):
    setup = _setup(direction, risk=Fraction(50 if quantity == 2 else 70))
    sign = 1 if direction is RegimeDirection.LONG else -1
    opening = setup.stop.initial_stop - (sign * 5 if beyond_stop else 0)
    flow = _filled(direction, quantity, base=opening)
    record = _account_exit(flow).trades[0]
    assert record.stop_fill.trigger_phase is StructuralStopTriggerPhaseV2.ENTRY_OPEN
    assert record.entry.base_fill_price == record.exit.base_fill_price == opening
    assert (
        record.entry.effective_fill_price_after_slippage
        - record.exit.effective_fill_price_after_slippage
        == sign * Fraction(1, 2)
    )
    assert record.gross_price_pnl_usd == -quantity
    assert record.total_fees_usd == Fraction(102 * quantity, 100)
    assert record.net_realized_pnl_usd == -Fraction(202 * quantity, 100)
    assert record.quantity == flow.decision.approved_quantity == quantity


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("gap", ["adverse", "favorable"])
def test_costs_never_resize_or_reject_an_already_filled_gap_trade(direction, gap):
    setup = _setup(direction)
    sign = 1 if direction is RegimeDirection.LONG else -1
    base = setup.bars[setup.q].close + sign * (40 if gap == "adverse" else -10)
    flow = _filled(direction, base=base)
    old_risk, old_entry, old_stop = (
        flow.decision,
        flow.entry.execution,
        flow.setup.stop.initial_stop_record,
    )
    record = _account_exit(flow, stops=_touch_on_entry(flow)).trades[0]
    assert record.quantity == old_risk.approved_quantity == 2
    assert record.sized_entry.risk_decision is old_risk
    assert record.sized_entry.execution is old_entry
    assert old_risk.initial_stop_record is old_stop
    assert old_risk.planned_total_risk_usd == 100
    if gap == "adverse":
        assert record.net_realized_pnl_usd < -100


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_costs_are_separate_from_exactly_100_dollar_planned_risk(direction):
    setup = _setup(direction)
    flow = _filled(direction, base=setup.bars[setup.q].close)
    record = _account_exit(flow, stops=_touch_on_entry(flow)).trades[0]
    assert record.sized_entry.risk_decision.planned_total_risk_usd == 100
    assert record.sized_entry.risk_decision.risk_budget_usd == 100
    assert record.net_realized_pnl_usd == -Fraction(10404, 100)


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_accounting_repeats_idempotently_without_changing_closed_or_open_snapshots(direction):
    flow = _filled(direction)
    opened = _account_entry(flow)
    for _ in range(3):
        assert _account_entry(flow, opened) is opened
    stopped = _touch_on_entry(flow)
    closed = _account_exit(flow, opened, stopped)
    for _ in range(3):
        assert _account_entry(flow, closed) is closed
        assert _account_exit(flow, closed, stopped) is closed
        assert _account_exit(flow, closed, flow.stops) is closed
    assert len(closed.trades) == 1
    assert opened.trades[0].net_realized_pnl_usd is None
    assert closed.trades[0].total_fees_usd == Fraction(204, 100)


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("field_name", ["open", "high", "low", "close", "volume"])
def test_future_market_mutations_cannot_change_costs_quantity_or_known_fills(direction, field_name):
    flow = _filled(direction)
    stopped = _touch_on_entry(flow)
    baseline = _account_exit(flow, stops=stopped)
    e = flow.entry.execution.execution_bar_index
    flow.setup.bars[e] = SimpleNamespace(**{field_name: NoReads()})
    flow.setup.bars[e + 1] = NoReads()
    flow.setup.bars[e + 9] = NoReads()
    mutated = _account_exit(flow, stops=stopped)
    assert mutated == baseline
    assert mutated.trades[0].quantity == flow.decision.approved_quantity == 2


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("non_fill", ["pending", "rejected", "expired", "invalid_open"])
def test_no_actual_entry_fill_pays_no_cost_or_synthetic_pnl(direction, non_fill):
    setup = _setup(direction, risk=Fraction(110 if non_fill == "rejected" else 50))
    risk = _register(setup)
    decision = risk.decisions[0]
    if non_fill in ("expired", "invalid_open"):
        risk = _execute(
            risk,
            decision,
            None
            if non_fill == "expired"
            else EntryExecutionOpenV2(setup.q + 1, _time(setup.q + 1), None),
        )
    empty = FeesAndSlippageBookV2(risk.strategy_instance_id, risk.series_id)
    assert account_entry_fill_v2(previous=empty, risk_sizing=risk, decision=decision) is empty
    assert (
        account_structural_stop_fill_v2(
            previous=empty, risk_sizing=risk, decision=decision, stops=None
        )
        is empty
    )
    assert not empty.trades


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("incomplete", [False, True])
def test_failed_stop_monitoring_never_invents_a_cost_bearing_exit(direction, incomplete):
    flow = _filled(direction)
    opened = _account_entry(flow)
    e = flow.entry.execution.execution_bar_index
    extreme = "low" if direction is RegimeDirection.LONG else "high"
    failed = _observe(flow, index=e + 1 if incomplete else e, **{extreme: None})
    assert failed.entries[0].fill is None
    assert _account_exit(flow, opened, failed) is opened
    assert opened.trades[0].net_realized_pnl_usd is None


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_full_provenance_and_all_cost_snapshots_are_immutable(direction):
    flow = _filled(direction)
    stopped = _touch_on_entry(flow)
    book = _account_exit(flow, stops=stopped)
    record = book.for_decision(flow.decision)
    assert record.sized_entry is flow.entry
    assert (
        record.sized_entry.risk_decision.consumed_context
        is flow.setup.confirmation.opportunity.consumed_context
    )
    assert record.sized_entry.risk_decision.confirmation is flow.setup.confirmation.confirmation
    assert (
        record.sized_entry.risk_decision.initial_stop_record is flow.setup.stop.initial_stop_record
    )
    assert record.stop_fill.initial_stop_at_entry.execution is flow.entry.execution
    assert record.stop_fill is stopped.entries[0].fill
    with pytest.raises(FrozenInstanceError):
        record.entry.fee_usd = Fraction(0)
    with pytest.raises(FrozenInstanceError):
        record.exit = None
    with pytest.raises(FrozenInstanceError):
        book.trades = ()
    with pytest.raises(FeesAndSlippageV2Error, match="duplicate"):
        replace(book, trades=(record, record))
    changed = replace(stopped.entries[0].fill, base_stop_fill_price=Fraction(1))
    changed_stops = replace(stopped, entries=(replace(stopped.entries[0], fill=changed),))
    with pytest.raises(FeesAndSlippageV2Error, match="stop provenance cannot change"):
        _account_exit(flow, book, changed_stops)


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_accounting_scope_and_unknown_source_are_rejected(direction):
    flow = _filled(direction)
    with pytest.raises(FeesAndSlippageV2Error, match="same scope"):
        _account_entry(flow, FeesAndSlippageBookV2("other-strategy", flow.risk.series_id))
    opened = _account_entry(flow)
    with pytest.raises(FeesAndSlippageV2Error, match="actual accounted fill"):
        opened.for_decision(_register(_setup(direction, event_index=42)).decisions[0])


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize(
    "field_name",
    [
        "source_regime_event_bar_index",
        "pullback_bar_index",
        "confirmation_bar_index",
        "entry_bar_index",
        "entry_bar_timestamp",
        "structural_extreme",
        "tick_size",
        "stop_buffer_ticks",
    ],
)
def test_exit_metadata_must_match_original_structural_stop_before_accounting(direction, field_name):
    flow = _filled(direction)
    opened = _account_entry(flow)
    stopped = _touch_on_entry(flow)
    original = stopped.entries[0].fill
    changed = replace(
        original,
        **{field_name: _time(500) if field_name == "entry_bar_timestamp" else Fraction(500)},
    )
    malformed = replace(stopped, entries=(replace(stopped.entries[0], fill=changed),))
    with pytest.raises(FeesAndSlippageV2Error, match="entry/stop provenance"):
        _account_exit(flow, opened, malformed)
    assert opened.trades[0].net_realized_pnl_usd is None
    assert opened.trades[0].total_fees_usd == Fraction(102, 100)


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_cost_record_cannot_change_frozen_risk_quantity(direction):
    flow = _filled(direction)
    record = _account_entry(flow).trades[0]
    wrong_quantity = calculate_fill_cost_v2(
        base_fill_price=record.entry.base_fill_price, action=record.entry.action, quantity=1
    )
    with pytest.raises(FeesAndSlippageV2Error, match="actual sized fill"):
        replace(record, entry=wrong_quantity)
    assert record.quantity == flow.decision.approved_quantity == 2


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_no_new_tick_repair_or_retroactive_rejection_is_added_after_entry(direction):
    flow = _filled(direction, base=Fraction(160001, 8))
    record = _account_entry(flow).trades[0]
    assert record.entry.base_fill_price == Fraction(160001, 8)
    assert record.quantity == 2
    assert record.entry.effective_fill_price_after_slippage.denominator == 8


@pytest.mark.parametrize(
    "invalid",
    [None, float("nan"), float("inf"), 20000.0, "20000", True, Decimal("NaN"), Decimal("Infinity")],
)
def test_invalid_or_inexact_pure_cost_input_has_no_fallback(invalid):
    with pytest.raises(FeesAndSlippageV2Error):
        calculate_fill_cost_v2(base_fill_price=invalid, action=FillActionV2.BUY, quantity=1)


@pytest.mark.parametrize("quantity", [0, 3, True, Fraction(1)])
def test_pure_cost_quantity_is_an_integer_approved_by_the_frozen_baseline(quantity):
    with pytest.raises(FeesAndSlippageV2Error):
        calculate_fill_cost_v2(base_fill_price=20000, action=FillActionV2.BUY, quantity=quantity)


@pytest.mark.parametrize(
    "value,expected",
    [
        (Fraction(1, 200), "0.01"),
        (Fraction(-1, 200), "-0.01"),
        (Fraction(3, 200), "0.02"),
        (Fraction(-3, 200), "-0.02"),
        (Fraction(201, 200), "1.01"),
        (Fraction(-201, 200), "-1.01"),
        (Fraction(1, 3), "0.33"),
        (Fraction(2, 3), "0.67"),
        (Fraction(-1, 1000), "-0.00"),
        (Fraction(10**40) + Fraction(1, 200), "1" + "0" * 40 + ".01"),
    ],
)
def test_reporting_half_up_occurs_only_at_boundary_even_with_repeating_rationals(value, expected):
    exact = value
    with localcontext() as context:
        context.prec = 1
        context.traps[Inexact] = True
        report = report_usd_cents_v2(exact)
    assert str(report) == expected
    assert isinstance(exact, Fraction) and exact == value


def test_exact_cost_arithmetic_ignores_decimal_context_and_preserves_repeating_prices():
    with localcontext() as context:
        context.prec = 1
        context.traps[Inexact] = True
        cost = calculate_fill_cost_v2(
            base_fill_price=Fraction(1, 3), action=FillActionV2.BUY, quantity=2
        )
        decimal_cost = calculate_fill_cost_v2(
            base_fill_price=Decimal("20000.125"), action=FillActionV2.SELL_SHORT, quantity=1
        )
    assert cost.effective_fill_price_after_slippage == Fraction(7, 12)
    assert cost.fee_usd == Fraction(102, 100)
    assert decimal_cost.base_fill_price == Fraction(160001, 8)
    assert decimal_cost.effective_fill_price_after_slippage == Fraction(159999, 8)
    with pytest.raises(FeesAndSlippageV2Error, match="exact frozen baseline"):
        replace(cost, effective_fill_price_after_slippage=cost.base_fill_price)
    with pytest.raises(FeesAndSlippageV2Error):
        report_usd_cents_v2(Decimal("1.005"))


@pytest.mark.parametrize("quantity", [1, 2])
def test_long_short_mirror_accounting_is_exactly_symmetric(quantity):
    long, short = _filled(RegimeDirection.LONG, quantity), _filled(RegimeDirection.SHORT, quantity)
    left = _account_exit(long, stops=_touch_on_entry(long)).trades[0]
    right = _account_exit(short, stops=_touch_on_entry(short)).trades[0]
    assert (
        left.entry.effective_fill_price_after_slippage
        + right.entry.effective_fill_price_after_slippage
        == 40000
    )
    assert (
        left.exit.effective_fill_price_after_slippage
        + right.exit.effective_fill_price_after_slippage
        == 40000
    )
    assert left.net_realized_pnl_usd == right.net_realized_pnl_usd
    assert left.total_fees_usd == right.total_fees_usd
    assert left.diagnostic_total_slippage_cost_usd == right.diagnostic_total_slippage_cost_usd
