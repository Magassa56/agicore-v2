"""Full native V2 lifecycle on invented OHLCV only, twice from independent state."""

from __future__ import annotations

import ast
import hashlib
import importlib
import json
from dataclasses import FrozenInstanceError, replace
from datetime import timedelta
from decimal import Decimal as D
from fractions import Fraction as F
from pathlib import Path

import pytest

from agicore.trading import ema_pullback_regime_gated_baseline_v2 as assembly
from agicore.trading.ema_pullback_entry_execution_v2 import EntryExecutionStateV2
from agicore.trading.ema_pullback_exit_policy_v2 import (
    EMA20ExitExecutionStateV2,
    ExitPolicyEndStateV2,
)
from agicore.trading.ema_pullback_pending_opportunity_policy_v2 import (
    PendingOpportunityPolicyV2Error,
    PendingOpportunityStateV2,
    PendingSignalAdmissionStatusV2,
)
from agicore.trading.ema_pullback_risk_position_sizing_v2 import RiskSizingDecisionV2
from agicore.trading.ema_pullback_structural_stop_trigger_fill_v2 import (
    StructuralStopTriggerPhaseV2,
)
from agicore.trading.regime_context_v2 import (
    RegimeContextLifetimeState,
    RegimeContextStatus,
    RegimeDirection,
    RegimeEvent,
    RegimeEventType,
    compose_regime_context_v2,
)
from agicore.trading.reversal_transition_v2 import OppositeTransitionStatus
from tests.unit.trading.test_ema_pullback_v2_pending_opportunity_audit import (
    COMPONENTS,
    SERIES,
    STRATEGY,
    _bars,
    _raw,
    _time,
)

MANIFEST = Path("docs/evidence/EMA_PULLBACK_V2_REGIME_GATED_BASELINE_MANIFEST.json")
AUDIT_MANIFEST = Path("docs/evidence/EMA_PULLBACK_V2_FROZEN_COMPONENTS_AUDIT_MANIFEST.json")
AUDIT_SHA = "82694c53879a145024b288a53649179bb6484b10757882c8955700bfbe1f4ef6"
State = PendingOpportunityStateV2
Admission = PendingSignalAdmissionStatusV2


def _mirror(raw):
    return {
        i: replace(
            b,
            open=D(40000) - b.open,
            high=D(40000) - b.low,
            low=D(40000) - b.high,
            close=D(40000) - b.close,
        )
        for i, b in raw.items()
    }


def _reversal(dual=False):
    raw = {i: _raw(i, ("20000", "20000.25", "19999.75", "20000")) for i in range(27)}
    for i in range(27, 32):
        c = D(20032 - i)
        o = c + D(1)
        raw[i] = _raw(i, tuple(map(str, (o, o + D(".25"), c - D(".25"), c))))
    rows = {
        32: ("20001", "20002", "19999", "20001.5"),
        33: ("20001.5", "20004.25", "20001.25", "20004"),
        34: ("20004", "20004.25", "20000.75", "20003.5"),
        35: ("20003.5", "20006.25", "20003.25", "20006"),
        36: ("20006.25", "20006.5", "20005.75", "20006"),
    }
    raw.update({i: _raw(i, row, 150 if dual and i == 33 else 100) for i, row in rows.items()})
    return raw


def _profit_tail(raw):
    for i in range(37, 55):
        c = D(20006 + 2 * (i - 36))
        o = raw[i - 1].close
        raw[i] = _raw(i, tuple(map(str, (o, c + D(".25"), o - D(".25"), c))))
    raw[55] = _raw(55, ("20042", "20042.25", "20019.75", "20020"))
    raw[56] = _raw(56, ("20020.25", "20020.5", "20019.75", "20020.25"))
    return raw


def _scenario(name, direction):
    raw = (
        _reversal(name == "dual_probe")
        if name in ("reversal_profit", "dual_probe", "rejection_eof")
        else _bars(RegimeDirection.LONG)
    )
    raw = _profit_tail(raw)
    last = 56
    if name in ("qty1_profit", "breached_1"):
        raw[33] = replace(raw[33], low=D(19970))
    if name == "risk_reject":
        raw[33] = replace(raw[33], low=D(19900))
        last = 38
    if name == "first_confirmation":
        raw[33] = replace(raw[33], open=D("20002.5"))
    if name in ("intrabar_stop", "gap_stop", "exit_regime_admitted"):
        last = 40
        if name == "intrabar_stop":
            raw[40] = replace(raw[40], low=D(20000), close=D("20000.25"))
        elif name == "gap_stop":
            raw[40] = _raw(40, ("19998.5", "19999", "19998", "19998.75"))
        else:
            raw[40] = _raw(40, ("20012", "20041", "20000", "20040"), 150)
    if name in ("breached_1", "breached_2"):
        level = D("19969.75") if name == "breached_1" else D(20000)
        raw[36] = _raw(36, tuple(map(str, (level, level + D(".25"), level - D(".25"), level))))
        last = 36
    if name == "stop_wins":
        raw[56] = _raw(56, ("19998.5", "19999", "19998", "19998.75"))
    if name == "position_suppressed":
        raw[40] = replace(raw[40], volume=150)
        last = 40
    if name == "context_age":
        last = 41
        for i in range(33, 42):
            c = D(20005 + i - 33)
            raw[i] = _raw(i, tuple(map(str, (c, c + D(".25"), c - D(".25"), c))))
    if name == "context_elapsed":
        last = 33
        raw[33] = replace(raw[33], timestamp_utc=_time(42))
    if name == "confirmation_no":
        last = 38
        raw[35] = replace(raw[35], close=D("20003.75"))
    if name == "confirmation_elapsed":
        last = 34
        raw[34] = replace(raw[34], timestamp_utc=_time(36))
    if name in ("entry_gap", "ema_gap"):
        last = 36 if name == "entry_gap" else 56
        raw[last] = replace(raw[last], timestamp_utc=_time(last + 2))
    if name == "entry_missing":
        del raw[36]
        last = 37
    last = {
        "context_eof": 32,
        "confirmation_eof": 33,
        "entry_eof": 35,
        "open_eof": 36,
        "ema_eof": 55,
        "rejection_eof": 32,
    }.get(name, last)
    raw = {i: b for i, b in raw.items() if i <= last}
    return _mirror(raw) if direction is RegimeDirection.SHORT else raw


def _through(raw, last=None, duplicate=False):
    book = assembly.begin_regime_gated_baseline_v2(strategy_instance_id=STRATEGY, series_id=SERIES)
    snapshots = []
    for index, bar in raw.items():
        if last is not None and index > last:
            break
        book = assembly.process_baseline_open_v2(previous=book, opening_bar=bar)
        if duplicate:
            assert (
                assembly.process_baseline_open_v2(previous=book, opening_bar=Poison(index)) is book
            )
        book = assembly.process_baseline_close_v2(previous=book, closed_bar=bar)
        if duplicate:
            assert (
                assembly.process_baseline_close_v2(previous=book, closed_bar=Poison(index)) is book
            )
        assert (
            len(
                [
                    o
                    for o in book.policy.opportunities
                    if o.state in (State.AWAITING_CONFIRMATION, State.PENDING_ENTRY_EXECUTION)
                ]
            )
            <= 1
        )
        assert sum(pos.exit is None for pos in book.policy.positions.positions) <= 1
        assert book.policy.positions == book.exits.positions
        assert book.policy.risks == book.exits.risk_sizing
        snapshots.append(book)
    return book, tuple(snapshots)


class Poison:
    def __init__(self, index=None):
        self.bar_index = index

    def __getattr__(self, name):
        raise AssertionError(f"forbidden unavailable/duplicate field read: {name}")


SCENARIOS = (
    "impulse_profit",
    "reversal_profit",
    "qty1_profit",
    "first_confirmation",
    "risk_reject",
    "intrabar_stop",
    "gap_stop",
    "breached_1",
    "breached_2",
    "stop_wins",
    "position_suppressed",
    "exit_regime_admitted",
    "context_age",
    "context_elapsed",
    "confirmation_no",
    "confirmation_elapsed",
    "entry_gap",
    "entry_missing",
    "ema_gap",
    "context_eof",
    "confirmation_eof",
    "entry_eof",
    "open_eof",
    "ema_eof",
    "rejection_eof",
)


@pytest.mark.parametrize("direction", list(RegimeDirection))
@pytest.mark.parametrize("name", SCENARIOS)
def test_full_synthetic_lifecycle_twice(name, direction):
    outputs = []
    for _ in range(2):
        raw = _scenario(name, direction)
        book, history = _through(raw)
        book = assembly.finish_regime_gated_baseline_v2(previous=book)
        assert assembly.finish_regime_gated_baseline_v2(previous=book) is book
        assert assembly.process_baseline_open_v2(previous=book, opening_bar=Poison()) is book
        assert assembly.process_baseline_close_v2(previous=book, closed_bar=Poison()) is book
        assert book.policy.active_opportunity is None
        assert book.policy.end_of_data and book.exits.end_of_data and book.end_of_data
        assert len(book.closed_bars) == len(raw)
        if name.endswith("profit") or name == "first_confirmation":
            record = book.final_positions[0]
            assert record.accounting.exit_type == "EMA20_POSITION_EXIT"
            assert record.net_realized_pnl_usd > 0
            assert record.approved_quantity == (1 if name == "qty1_profit" else 2)
            assert record.total_fees_usd == F(102, 100) * record.approved_quantity
            assert record.accounting.diagnostic_total_slippage_cost_usd == F(
                record.approved_quantity
            )
            if name in ("impulse_profit", "qty1_profit"):
                assert record.gross_price_pnl_usd == F(61, 2) * record.approved_quantity
                assert record.net_realized_pnl_usd == F(1474, 50) * record.approved_quantity
            if name == "reversal_profit":
                assert record.net_realized_pnl_usd == F(2598, 100) * record.approved_quantity
                assert record.position.entry.source_regime_event_bar_index == 33
                assert record.position.entry.pullback_bar_index == 34
                assert record.position.entry.confirmation_bar_index == 35
                assert (
                    book.raw_decisions[32].current_rejection.opposite_transition.status
                    is OppositeTransitionStatus.AWAITING_OPPOSITE_TRANSITION
                )
            if name == "first_confirmation":
                assert record.position.entry.confirmation_bar_index == 34
                assert record.position.entry.execution_bar_index == 35
                assert (
                    history[35].policy.opportunities[0].confirmation
                    == history[34].policy.opportunities[0].confirmation
                )
            else:
                assert record.position.entry.confirmation_bar_index == 35
                assert record.position.entry.execution_bar_index == 36
        elif name == "risk_reject":
            assert book.policy.opportunities[0].state is State.TERMINAL_RISK_REJECTED
            assert book.policy.risks.decisions[0].decision is RiskSizingDecisionV2.REJECT
            assert not book.policy.risks.executions.entries
            assert not book.final_positions
        elif name in ("breached_1", "breached_2"):
            record = book.final_positions[0]
            assert (
                record.position.entry.execution_price_before_costs
                == record.accounting.stop_fill.base_stop_fill_price
            )
            assert (
                record.accounting.stop_fill.trigger_phase is StructuralStopTriggerPhaseV2.ENTRY_OPEN
            )
            assert record.net_realized_pnl_usd == -F(202, 100) * record.approved_quantity
            assert record.approved_quantity == (1 if name == "breached_1" else 2)
            assert len(book.policy.risks.filled_entries) == 1
        elif name in ("intrabar_stop", "gap_stop", "stop_wins", "exit_regime_admitted"):
            record = book.final_positions[0]
            assert record.accounting.exit_type == "STRUCTURAL_STOP"
            fill = record.accounting.stop_fill
            assert fill.trigger_phase is (
                StructuralStopTriggerPhaseV2.BAR_OPEN_GAP
                if name in ("gap_stop", "stop_wins")
                else StructuralStopTriggerPhaseV2.INTRABAR
            )
            if name == "stop_wins":
                assert (
                    book.exits.ema_executions[0].state
                    is EMA20ExitExecutionStateV2.CANCELLED_STRUCTURAL_STOP
                )
                assert all(e.fill is None for e in book.exits.ema_executions)
            if name == "intrabar_stop":
                assert all(
                    decision.closed_bar_index != 40 for decision in book.exits.close_decisions
                )
            if name == "exit_regime_admitted":
                assert book.policy.signal_decisions[-1].status is Admission.ADMITTED
                assert book.policy.positions.context.source_event_bar_index == 40
                assert (
                    book.policy.positions.context.state
                    is RegimeContextLifetimeState.EXPIRED_END_OF_DATA
                )
                assert len(book.policy.opportunities) == 1
        elif name == "position_suppressed":
            assert book.policy.signal_decisions[-1].status is Admission.SUPPRESSED_POSITION_OPEN
            assert book.raw_decisions[-1].impulse.event is not None
            assert len(book.policy.opportunities) == 1
            assert book.final_positions[0].net_realized_pnl_usd is None
        elif name in ("context_age", "context_elapsed", "context_eof"):
            expected = {
                "context_age": RegimeContextLifetimeState.EXPIRED_MAX_AGE,
                "context_elapsed": RegimeContextLifetimeState.EXPIRED_ELAPSED_TIME,
                "context_eof": RegimeContextLifetimeState.EXPIRED_END_OF_DATA,
            }[name]
            assert book.policy.positions.context.state is expected
            assert not book.policy.opportunities
        elif name in ("confirmation_no", "confirmation_elapsed"):
            assert book.policy.opportunities[0].state is State.TERMINAL_CONFIRMATION_EXPIRED
            assert not book.final_positions
        elif name == "confirmation_eof":
            assert book.policy.opportunities[0].state is State.TERMINAL_INCOMPLETE_CONFIRMATION
            assert not book.final_positions
        elif name in ("entry_eof", "entry_missing", "entry_gap"):
            expected = (
                EntryExecutionStateV2.EXPIRED_EXECUTION_GAP
                if name == "entry_gap"
                else EntryExecutionStateV2.EXPIRED_NO_EXECUTION
            )
            assert book.policy.risks.executions.entries[0].execution_state is expected
            assert not book.final_positions
        elif name in ("open_eof", "ema_eof", "ema_gap"):
            assert book.exits.end_state is ExitPolicyEndStateV2.OPEN_UNREALIZED
            assert book.final_positions[0].net_realized_pnl_usd is None
            assert book.final_positions[0].accounting.exit is None
            if name == "ema_gap":
                assert (
                    book.exits.ema_executions[0].state is EMA20ExitExecutionStateV2.EXPIRED_EXIT_GAP
                )
            if name == "ema_eof":
                assert (
                    book.exits.ema_executions[0].state
                    is EMA20ExitExecutionStateV2.EXPIRED_NO_EXIT_EXECUTION
                )
        elif name == "rejection_eof":
            assert (
                book.raw_decisions[-1].current_rejection.opposite_transition.status
                is OppositeTransitionStatus.INCOMPLETE_CONFIRMATION
            )
            assert not book.final_positions
        outputs.append(book)
    assert outputs[0] == outputs[1]
    assert assembly.deterministic_baseline_snapshot_v2(
        outputs[0]
    ) == assembly.deterministic_baseline_snapshot_v2(outputs[1])


@pytest.mark.parametrize("direction", list(RegimeDirection))
def test_original_native_concurrency_counterexample_is_impossible(direction):
    raw = _scenario("impulse_profit", direction)
    book, history = _through(raw, 35)
    assert len(history[33].policy.opportunities) == 1
    assert history[34].raw_decisions[-1].impulse.event is not None
    assert (
        history[34].policy.signal_decisions[-1].status is Admission.SUPPRESSED_PENDING_OPPORTUNITY
    )
    assert history[34].policy.positions.context.source_event_bar_index == 32
    assert history[35].policy.positions.context.pullback_bar_index == 33
    assert book.policy.active_opportunity.state is State.PENDING_ENTRY_EXECUTION
    assert len(book.policy.opportunities) == len(book.policy.risks.executions.entries) == 1
    assert not book.policy.positions.positions
    assert book.policy.risks.decisions[0].approved_quantity == 2
    assert book.policy.positions.context.state is RegimeContextLifetimeState.CONSUMED


@pytest.mark.parametrize("direction", list(RegimeDirection))
def test_open_phase_cannot_read_any_nonopening_field(direction):
    raw = _scenario("impulse_profit", direction)
    book, _ = _through(raw, 35)
    bar = raw[36]

    class OpenOnly(Poison):
        timestamp_utc = bar.timestamp_utc
        open = bar.open

    opening = OpenOnly(36)
    filled = assembly.process_baseline_open_v2(previous=book, opening_bar=opening)
    expected = assembly.process_baseline_open_v2(previous=book, opening_bar=bar)
    assert filled == expected
    assert filled.final_positions[0].accounting.entry.base_fill_price == F(bar.open)
    assert filled.final_positions[0].net_realized_pnl_usd is None
    for field in ("high", "low", "close", "volume"):
        mutated = replace(bar, **{field: D(99999)})
        assert assembly.process_baseline_open_v2(previous=book, opening_bar=mutated) == filled
    moved = replace(bar, open=bar.open + (D(1) if direction is RegimeDirection.LONG else -D(1)))
    alternate = assembly.process_baseline_open_v2(previous=book, opening_bar=moved)
    assert alternate.policy.risks.decisions == filled.policy.risks.decisions
    assert (
        alternate.policy.initial_stops.entries[0].initial_stop_record
        == filled.policy.initial_stops.entries[0].initial_stop_record
    )
    assert (
        alternate.final_positions[0].approved_quantity
        == filled.final_positions[0].approved_quantity
    )
    assert (
        alternate.final_positions[0].accounting.entry.base_fill_price
        != filled.final_positions[0].accounting.entry.base_fill_price
    )


@pytest.mark.parametrize("direction", list(RegimeDirection))
def test_duplicate_processing_and_future_mutation_have_no_effect_before_availability(direction):
    raw = _scenario("impulse_profit", direction)
    a, _ = _through(raw, 35, duplicate=True)
    future = dict(raw)
    future[36] = replace(
        future[36], open=D(99999), high=D(100000), low=D(99998), close=D(99999), volume=999999
    )
    b, _ = _through(future, 35)
    assert a == b
    assert assembly.deterministic_baseline_snapshot_v2(
        a
    ) == assembly.deterministic_baseline_snapshot_v2(b)
    complete, _ = _through(raw, duplicate=True)
    native = assembly.evaluate_synthetic_scenario_v2(
        strategy_instance_id=STRATEGY, series_id=SERIES, closed_bars=iter(raw.values())
    )
    assert assembly.finish_regime_gated_baseline_v2(previous=complete) == native


@pytest.mark.parametrize("name", SCENARIOS)
def test_long_short_complete_mirror(name):
    long = assembly.evaluate_synthetic_scenario_v2(
        strategy_instance_id=STRATEGY,
        series_id=SERIES,
        closed_bars=_scenario(name, RegimeDirection.LONG).values(),
    )
    short = assembly.evaluate_synthetic_scenario_v2(
        strategy_instance_id=STRATEGY,
        series_id=SERIES,
        closed_bars=_scenario(name, RegimeDirection.SHORT).values(),
    )
    assert len(long.final_positions) == len(short.final_positions)
    assert [d.approved_quantity for d in long.policy.risks.decisions] == [
        d.approved_quantity for d in short.policy.risks.decisions
    ]
    assert [d.state for d in long.policy.opportunities] == [
        d.state for d in short.policy.opportunities
    ]
    for a, b in zip(long.final_positions, short.final_positions, strict=True):
        assert a.net_realized_pnl_usd == b.net_realized_pnl_usd
        assert a.total_fees_usd == b.total_fees_usd
        assert (
            a.position.entry.execution_price_before_costs
            + b.position.entry.execution_price_before_costs
            == 40000
        )
        assert (
            a.position.initial_stop_at_entry.initial_stop_record.initial_stop_price
            + b.position.initial_stop_at_entry.initial_stop_record.initial_stop_price
            == 40000
        )


def test_manifest_is_new_canonical_snapshot_of_every_frozen_component():
    manifest = assembly.build_strategy_manifest_v2()
    assert manifest.canonical_utf8 == MANIFEST.read_bytes()
    assert manifest.sha256 == hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    assert hashlib.sha256(AUDIT_MANIFEST.read_bytes()).hexdigest() == AUDIT_SHA
    previous = json.loads(AUDIT_MANIFEST.read_bytes())
    assert previous["manifest_role"] == "FROZEN_COMPONENT_SNAPSHOT_NOT_APPROVED_STRATEGY"
    current = json.loads(manifest.canonical_utf8)
    assert current["strategy_id"] == STRATEGY
    assert current["formalization_version"] == 1 and current["mode"] == "OFFLINE_DETERMINISTIC"
    assert current["semantics"]["pending_opportunity_policy"] == "FIRST_CONSUMED_PULLBACK_LOCKS"
    assert all(v == "FORBIDDEN" for v in current["prohibitions"].values())
    assert [c["name"] for c in current["components"]] == [
        name + ".py" for name in (*COMPONENTS, "ema_pullback_pending_opportunity_policy_v2")
    ]
    assert current["components"][: len(COMPONENTS)] == previous["components"]
    assert sum(len(c["constants"]) for c in current["components"]) == 86
    for c in current["components"]:
        module = importlib.import_module("agicore.trading." + c["name"][:-3])
        assert c["source_sha256"] == hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
    assert (
        current["assembly_source_sha256"]
        == hashlib.sha256(Path(assembly.__file__).read_bytes()).hexdigest()
    )
    assert all(
        current[name] is None
        for name in ("TAKE_PROFIT", "BREAKEVEN", "TRAILING_STOP", "TIME_EXIT", "SESSION_EXIT")
    )
    with pytest.raises(FrozenInstanceError):
        manifest.canonical_utf8 = b"{}\n"


def test_assembly_contains_no_redefined_business_numeric_constants_or_market_loaders():
    tree = ast.parse(Path(assembly.__file__).read_text())
    constants = {
        target.id: node.value.value
        for node in tree.body
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant)
        for target in node.targets
        if isinstance(target, ast.Name) and target.id.isupper()
    }
    assert {k: v for k, v in constants.items() if type(v) in (int, float)} == {
        "FORMALIZATION_VERSION": 1
    }
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    assert not any("replay" in name or "broker" in name for name in imports)


def test_complete_native_dual_events_are_unreachable_by_body_and_rejection_extreme():
    # Opposite sides contradict strict body color. Same sides contradict the
    # impulse's monotonic prior Low/High and the rejection's strict extreme sweep.
    for direction in RegimeDirection:
        raw = _scenario("dual_probe", direction)
        variants = [
            raw[33],
            replace(raw[33], open=raw[33].close),
            replace(
                raw[33], open=raw[33].close + (D(1) if direction is RegimeDirection.LONG else -D(1))
            ),
        ]
        for bar in variants:
            variant = dict(raw)
            variant[33] = bar
            book, _ = _through(variant, 33)
            decision = book.raw_decisions[-1]
            assert not (decision.impulse.event is not None and decision.reversal.event is not None)
            assert (
                book.policy.signal_decisions[-1].composition.status
                is not RegimeContextStatus.AMBIGUOUS
            )
        genuine, _ = _through(raw, 33)
        assert genuine.raw_decisions[-1].reversal.event is not None
        assert genuine.raw_decisions[-1].impulse.emerging_direction.emerging_direction is None
        rejection = genuine.raw_decisions[-1].reversal.rejection
        assert rejection.rejection_qualified
        if direction is RegimeDirection.LONG:
            assert raw[32].low < min(raw[30].low, raw[31].low)
        else:
            assert raw[32].high > max(raw[30].high, raw[31].high)


@pytest.mark.parametrize("direction", list(RegimeDirection))
@pytest.mark.parametrize("ambiguous", (False, True))
def test_defensive_dual_and_ambiguous_composer_contract(direction, ambiguous):
    other = RegimeDirection.SHORT if direction is RegimeDirection.LONG else RegimeDirection.LONG
    outputs = []
    for _ in range(2):
        composition = compose_regime_context_v2(
            closed_bar_index=33,
            closed_bar_timestamp=_time(33),
            source_bar_closed=True,
            directional_impulse_event=RegimeEvent(
                RegimeEventType.DIRECTIONAL_IMPULSE_EVENT, direction, 33, _time(33)
            ),
            reversal_transition_event=RegimeEvent(
                RegimeEventType.REVERSAL_TRANSITION_EVENT,
                other if ambiguous else direction,
                33,
                _time(33),
            ),
        )
        assert composition.status is (
            RegimeContextStatus.AMBIGUOUS if ambiguous else RegimeContextStatus.QUALIFIED
        )
        assert tuple(event.event_type for event in composition.events) == (
            RegimeEventType.DIRECTIONAL_IMPULSE_EVENT,
            RegimeEventType.REVERSAL_TRANSITION_EVENT,
        )
        assert composition.event_direction is (None if ambiguous else direction)
        outputs.append(composition)
    assert outputs[0] == outputs[1]


def test_phase_and_stop_observation_corruption_remain_fail_closed():
    raw = _scenario("impulse_profit", RegimeDirection.LONG)
    book, _ = _through(raw, 35)
    with pytest.raises(assembly.BaselineAssemblyV2Error):
        assembly.process_baseline_close_v2(previous=book, closed_bar=raw[36])
    opened = assembly.process_baseline_open_v2(previous=book, opening_bar=raw[36])
    with pytest.raises(assembly.BaselineAssemblyV2Error):
        assembly.process_baseline_open_v2(previous=opened, opening_bar=raw[37])
    with pytest.raises(assembly.BaselineAssemblyV2Error):
        assembly.finish_regime_gated_baseline_v2(previous=opened)
    with pytest.raises(assembly.BaselineAssemblyV2Error):
        assembly.process_baseline_close_v2(
            previous=opened, closed_bar=replace(raw[36], open=D(20005))
        )
    with pytest.raises(PendingOpportunityPolicyV2Error):
        assembly.process_baseline_close_v2(
            previous=opened, closed_bar=replace(raw[36], low=D(30000))
        )
    closed = assembly.process_baseline_close_v2(previous=opened, closed_bar=raw[36])
    with pytest.raises(PendingOpportunityPolicyV2Error):
        assembly.process_baseline_open_v2(previous=closed, opening_bar=raw[38])


def test_complete_provenance_and_entry_stop_costs_are_immutable():
    book = assembly.evaluate_synthetic_scenario_v2(
        strategy_instance_id=STRATEGY,
        series_id=SERIES,
        closed_bars=_scenario("impulse_profit", RegimeDirection.LONG).values(),
    )
    result = book.final_positions[0]
    risk = book.policy.risks.decisions[0]
    fill = result.position.entry
    assert result.accounting.sized_entry.risk_decision == risk
    assert fill.confirmation == risk.confirmation
    assert fill.source_regime_event_bar_index == 32
    assert fill.pullback_bar_index == 33
    assert fill.confirmation_bar_index == 35
    assert fill.execution_bar_index == 36
    assert result.position.initial_stop_at_entry.initial_stop_record == risk.initial_stop_record
    assert risk.initial_stop_record.stop_known_at_bar_index == 35
    assert (
        result.accounting.ema_exit_fill.signal.initial_stop_at_entry
        == result.position.initial_stop_at_entry
    )
    assert result.accounting.ema_exit_fill.exit_execution_bar_index == 56
    with pytest.raises(FrozenInstanceError):
        result.position.entry.execution_bar_index = 99
    with pytest.raises(FrozenInstanceError):
        risk.approved_quantity = 99
    with pytest.raises(FrozenInstanceError):
        result.net_realized_pnl_usd = F(0)
    with pytest.raises(assembly.BaselineAssemblyV2Error):
        replace(result, net_realized_pnl_usd=F(0))
    with pytest.raises(assembly.BaselineAssemblyV2Error):
        replace(book, exits=replace(book.exits, costs=replace(book.exits.costs, trades=())))


@pytest.mark.parametrize("direction", list(RegimeDirection))
def test_eighth_context_bar_at_exactly_eight_minutes_can_still_consume(direction):
    outputs = []
    for _ in range(2):
        raw = _bars(RegimeDirection.LONG)
        for i in range(33, 40):
            raw[i] = _raw(i, ("20002", "20002.25", "20001.75", "20002"))
        raw[40] = _raw(40, ("20004", "20004.25", "20000.25", "20002.5"))
        if direction is RegimeDirection.SHORT:
            raw = _mirror(raw)
        book, history = _through(raw, 40)
        assert history[-2].policy.positions.context.state is RegimeContextLifetimeState.ACTIVE
        assert book.policy.positions.context.state is RegimeContextLifetimeState.CONSUMED
        assert book.policy.active_opportunity.consumed_context.pullback_bar_index == 40
        assert book.policy.active_opportunity.consumed_context.source_event_bar_index == 32
        assert raw[40].timestamp_utc - raw[32].timestamp_utc == timedelta(minutes=8)
        outputs.append(book)
    assert assembly.deterministic_baseline_snapshot_v2(
        outputs[0]
    ) == assembly.deterministic_baseline_snapshot_v2(outputs[1])


@pytest.mark.parametrize("direction", list(RegimeDirection))
def test_entry_bar_itself_can_schedule_an_ema_exit_but_cannot_fill_it(direction):
    outputs = []
    for _ in range(2):
        raw = _scenario("impulse_profit", RegimeDirection.LONG)
        raw[36] = _raw(36, ("20004.5", "20004.75", "20000.25", "20000.5"))
        raw[37] = _raw(37, ("20000.75", "20001", "20000.5", "20000.75"))
        if direction is RegimeDirection.SHORT:
            raw = _mirror(raw)
        book, history = _through(raw, 37)
        assert history[-2].exits.pending_ema_exit.signal.exit_signal_bar_index == 36
        assert history[-2].policy.positions.active_position is not None
        assert history[-2].final_positions[0].net_realized_pnl_usd is None
        assert book.final_positions[0].accounting.ema_exit_fill.exit_execution_bar_index == 37
        assert book.final_positions[0].accounting.exit.base_fill_price == F(raw[37].open)
        outputs.append(book)
    assert outputs[0] == outputs[1]


def test_a_new_chain_after_exit_never_restores_old_pending_provenance():
    outputs = []
    for _ in range(2):
        raw = _scenario("impulse_profit", RegimeDirection.LONG)
        raw[57] = _raw(57, ("20020.25", "20023.5", "20020.25", "20023.25"))
        raw[58] = _raw(58, ("20023.25", "20026.5", "20020.5", "20026.25"))
        raw[59] = _raw(59, ("20021", "20031.25", "20020.75", "20031"), 150)
        raw[60] = _raw(60, ("20031", "20031.25", "20015", "20030"))
        raw[61] = _raw(61, ("20030", "20060.25", "20029.75", "20060"))
        raw[62] = _raw(62, ("20060.25", "20060.5", "20059.75", "20060.25"))
        book, history = _through(raw)
        assert history[56].policy.positions.active_position is None
        assert book.raw_decisions[59].impulse.event is not None
        assert len(book.policy.opportunities) == 2
        assert len(book.final_positions) == 2
        assert book.final_positions[0].position.exit is not None
        assert book.final_positions[1].position.exit is None
        assert book.final_positions[1].position.entry.source_regime_event_bar_index == 59
        assert book.final_positions[1].position.entry.pullback_bar_index == 60
        assert book.final_positions[1].position.entry.confirmation_bar_index == 61
        assert book.final_positions[1].position.entry.execution_bar_index == 62
        assert book.final_positions[0].net_realized_pnl_usd == F(1474, 25)
        assert book.final_positions[1].net_realized_pnl_usd is None
        outputs.append(book)
    assert assembly.deterministic_baseline_snapshot_v2(
        outputs[0]
    ) == assembly.deterministic_baseline_snapshot_v2(outputs[1])


@pytest.mark.parametrize("direction", list(RegimeDirection))
def test_sequential_stop_survives_a_large_session_timestamp_gap(direction):
    outputs = []
    for _ in range(2):
        raw = _scenario("gap_stop", direction)
        raw[40] = replace(raw[40], timestamp_utc=_time(40) + timedelta(hours=4))
        book, _ = _through(raw)
        fill = book.final_positions[0].accounting.stop_fill
        assert fill.trigger_bar_index == 40
        assert fill.trigger_phase is StructuralStopTriggerPhaseV2.BAR_OPEN_GAP
        assert fill.base_stop_fill_price == F(raw[40].open)
        outputs.append(book)
    assert outputs[0] == outputs[1]


def test_full_assembly_preserves_native_close_and_open_transition_order(monkeypatch):
    raw = _scenario("impulse_profit", RegimeDirection.LONG)
    book, _ = _through(raw, 34)
    trace = []
    functions = (
        (assembly.exits, "process_exit_policy_close_v2", "EXIT_RESOLUTION"),
        (assembly.pending, "advance_entry_confirmation_momentum_v2", "CONFIRMATION"),
        (assembly.pending, "register_initial_stop_v2", "INITIAL_STOP"),
        (assembly.pending, "register_risk_position_sizing_v2", "RISK_ENGINE"),
        (assembly.impulse, "evaluate_directional_impulse_event_v2", "RAW_IMPULSE"),
        (assembly.reversal, "evaluate_reversal_transition_event_v2", "RAW_REVERSAL"),
    )
    for module, name, label in functions:
        original = getattr(module, name)

        def forward(*args, _original=original, _label=label, **kwargs):
            trace.append(_label)
            return _original(*args, **kwargs)

        monkeypatch.setattr(module, name, forward)
    book = assembly.process_baseline_open_v2(previous=book, opening_bar=raw[35])
    book = assembly.process_baseline_close_v2(previous=book, closed_bar=raw[35])
    assert trace == [
        "EXIT_RESOLUTION",
        "CONFIRMATION",
        "INITIAL_STOP",
        "RISK_ENGINE",
        "RAW_IMPULSE",
        "RAW_REVERSAL",
        "RAW_REVERSAL",
    ]
    assert not book.final_positions
    trace.clear()
    for module, name, label in (
        (assembly.pending, "execute_risk_approved_entry_open_v2", "ENTRY_EXECUTION"),
        (assembly.pending, "bind_initial_stop_to_entry_v2", "BIND_STOP"),
        (assembly.pending, "register_structural_stop_execution_v2", "ACTIVATE_STOP"),
        (assembly.pending, "apply_position_entry_fill_v2", "POSITION_OPEN"),
        (assembly.exits, "process_exit_policy_open_v2", "OPEN_EXIT_RESOLUTION"),
    ):
        original = getattr(module, name)

        def forward_open(*args, _original=original, _label=label, **kwargs):
            trace.append(_label)
            return _original(*args, **kwargs)

        monkeypatch.setattr(module, name, forward_open)
    book = assembly.process_baseline_open_v2(previous=book, opening_bar=raw[36])
    assert trace == [
        "ENTRY_EXECUTION",
        "BIND_STOP",
        "ACTIVATE_STOP",
        "POSITION_OPEN",
        "OPEN_EXIT_RESOLUTION",
    ]
    assert len(book.final_positions) == 1
