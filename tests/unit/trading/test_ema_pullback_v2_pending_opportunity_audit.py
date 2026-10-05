"""Synthetic pending-chain audit; compose frozen gates without an A/B policy.

This is a formalization counterexample harness, not a strategy or replay runner.
All prices are invented. No event, confirmation, stop or risk record is forged.
"""

from __future__ import annotations

import hashlib
import importlib
import json
from dataclasses import dataclass, fields, is_dataclass, replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import Enum
from fractions import Fraction
from pathlib import Path

import pytest

from agicore.trading.directional_impulse_v2 import (
    DirectionalImpulseBarV2,
    evaluate_directional_impulse_event_v2,
)
from agicore.trading.ema20_pullback_v2 import EMA20PullbackBarV2
from agicore.trading.ema_pullback_entry_confirmation_v2 import (
    MAX_CONFIRMATION_AGE_CLOSED_BARS,
    EntryConfirmationStateV2,
    advance_entry_confirmation_momentum_v2,
    begin_entry_confirmation_momentum_v2,
)
from agicore.trading.ema_pullback_entry_execution_v2 import (
    EntryExecutionOpenV2,
    EntryExecutionStateV2,
)
from agicore.trading.ema_pullback_initial_stop_v2 import (
    InitialStopBookV2,
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
    RiskPositionSizingBookV2,
    RiskSizingDecisionV2,
    RiskSizingRejectionReasonV2,
    execute_risk_approved_entry_open_v2,
    register_risk_position_sizing_v2,
)
from agicore.trading.ema_pullback_structural_stop_trigger_fill_v2 import (
    StructuralStopExecutionBookV2,
    register_structural_stop_execution_v2,
)
from agicore.trading.regime_context_v2 import (
    MAX_CONTEXT_AGE_CLOSED_BARS,
    RegimeContextLifetimeState,
    RegimeDirection,
)
from agicore.trading.reversal_transition_v2 import (
    RejectionBarV2,
    evaluate_reversal_transition_event_v2,
)
from tests.unit.trading.test_ema_pullback_risk_position_sizing_v2 import GuardedBars, NoReads

START = datetime(2026, 10, 5, 8, tzinfo=UTC)
STRATEGY = "EMA_PULLBACK_V2_REGIME_GATED_BASELINE"
SERIES = "SYNTHETIC_ONLY_MNQ_1_MINUTE"
COMPONENTS = (
    "directional_impulse_v2",
    "reversal_transition_v2",
    "regime_context_v2",
    "ema20_pullback_v2",
    "ema_pullback_entry_confirmation_v2",
    "ema_pullback_risk_position_sizing_v2",
    "ema_pullback_initial_stop_v2",
    "ema_pullback_entry_execution_v2",
    "ema_pullback_structural_stop_trigger_fill_v2",
    "ema_pullback_open_position_signal_policy_v2",
    "ema_pullback_fees_and_slippage_v2",
    "ema_pullback_exit_policy_v2",
)
MANIFEST_PATH = Path("docs/evidence/EMA_PULLBACK_V2_FROZEN_COMPONENTS_AUDIT_MANIFEST.json")


def _time(index):
    return START + timedelta(minutes=index)


def _raw(index, values, volume=100):
    return DirectionalImpulseBarV2(
        index,
        _time(index),
        *(Decimal(value) for value in values),
        True,
        volume,
        "BAR_TRADE_VOLUME",
        1,
        "Last",
    )


def _bars(direction):
    # Baseline/narrow history, two genuine impulses, then two distinct pullbacks.
    bars = {i: _raw(i, ("20000", "20000.25", "19999.75", "20000")) for i in range(29)}
    values = {
        29: ("20000", "20000.25", "19999.25", "20000.25"),
        30: ("20000.25", "20000.50", "19999.50", "20000.50"),
        31: ("20000.50", "20000.75", "19999.75", "20000.75"),
        32: ("20000.25", "20002", "20000", "20001.75"),
        33: ("20004", "20004.25", "20000.25", "20002"),
        34: ("20002", "20003.25", "20001.75", "20003"),
        35: ("20002.50", "20004.50", "20000.25", "20004.25"),
        36: ("20004.50", "20006.25", "20004", "20006"),
        37: ("20006", "20008.25", "20005.75", "20008"),
        38: ("20008.25", "20009", "20007.75", "20008.50"),
    }
    bars.update({i: _raw(i, row, 150 if i in (32, 34) else 100) for i, row in values.items()})
    if direction is RegimeDirection.SHORT:
        bars = {
            i: replace(
                bar,
                open=Decimal(40000) - bar.open,
                high=Decimal(40000) - bar.low,
                low=Decimal(40000) - bar.high,
                close=Decimal(40000) - bar.close,
            )
            for i, bar in bars.items()
        }
    return bars


def _ema_bars(raw):
    return {
        i: EMA20PullbackBarV2(i, b.timestamp_utc, b.open, b.high, b.low, b.close, b.is_closed)
        for i, b in raw.items()
    }


def _close_policy(policy, index, raw, ema):
    # Both raw event engines see only their already-closed prefixes.
    impulse = evaluate_directional_impulse_event_v2(
        impulse_candidate_bar_index=index, bars_by_index=GuardedBars(raw, range(index + 1))
    )
    reversal_bars = {}
    for i in range(index + 1):
        b = raw[i]
        reversal_bars[i] = RejectionBarV2(
            i, b.timestamp_utc, b.close, b.is_closed, b.open, b.high, b.low
        )
    reversal = evaluate_reversal_transition_event_v2(
        rejection_candidate_bar_index=index - 1,
        closed_bar_index=index,
        bars_by_index=GuardedBars(reversal_bars, range(index + 1)),
    )
    policy = advance_open_position_signal_policy_v2(
        previous=policy,
        closed_bar_index=index,
        closed_bar_timestamp=_time(index),
        source_bar_closed=True,
        bars_by_index=GuardedBars(ema, range(index + 1)),
        directional_impulse_event=impulse.event,
        reversal_transition_event=None
        if reversal.event is None
        else reversal.event.as_regime_event(),
    )
    return policy, impulse, reversal


def _advance(confirmation, index, ema):
    return advance_entry_confirmation_momentum_v2(
        previous=confirmation,
        closed_bar_index=index,
        closed_bar_timestamp=_time(index),
        source_bar_closed=True,
        bars_by_index=GuardedBars(ema, range(index + 1)),
    )


def _authorize(risk, policy, confirmation, stops, index, ema):
    stops = register_initial_stop_v2(
        previous=stops,
        confirmation=confirmation,
        bars_by_index=GuardedBars(
            ema, range(confirmation.opportunity.consumed_context.pullback_bar_index, index + 1)
        ),
    )
    risk = register_risk_position_sizing_v2(
        previous=risk,
        position_policy=policy,
        instrument="MNQ",
        closed_bar_index=index,
        closed_bar_timestamp=_time(index),
        source_bar_closed=True,
        confirmation=confirmation,
        initial_stop=stops.for_confirmation(confirmation.confirmation),
        bars_by_index=GuardedBars(ema, [index]),
    )
    return risk, stops


@dataclass(frozen=True)
class Audit:
    raw: dict
    ema: dict
    policy_after_a_pullback: object
    policy_after_b_event: object
    policy: object
    a_before_last_candidate: object
    a: object
    b: object
    risk: object
    stops: object
    raw_decisions: tuple


def _audit(direction, mutate_future=False):
    raw = _bars(direction)
    ema = _ema_bars(raw)
    if mutate_future:
        for index in range(36, 39):
            raw[index] = NoReads()
            ema[index] = NoReads()
    policy = OpenPositionSignalPolicyBookV2(STRATEGY, SERIES)
    decisions = []
    policy, impulse, reversal = _close_policy(policy, 32, raw, ema)
    decisions.append((impulse, reversal))
    policy, impulse, reversal = _close_policy(policy, 33, raw, ema)
    decisions.append((impulse, reversal))
    after_a = policy
    a = begin_entry_confirmation_momentum_v2(
        pullback=policy.signal_decisions[-1].pullback, pullback_bar=ema[33]
    )
    policy, impulse, reversal = _close_policy(policy, 34, raw, ema)
    decisions.append((impulse, reversal))
    after_b_event = policy
    a = _advance(a, 34, ema)
    before_last = a
    policy, impulse, reversal = _close_policy(policy, 35, raw, ema)
    decisions.append((impulse, reversal))
    b = begin_entry_confirmation_momentum_v2(
        pullback=policy.signal_decisions[-1].pullback, pullback_bar=ema[35]
    )
    a = _advance(a, 35, ema)
    risk, stops = _authorize(
        RiskPositionSizingBookV2(STRATEGY, SERIES), policy, a, InitialStopBookV2(), 35, ema
    )
    return Audit(
        raw, ema, after_a, after_b_event, policy, before_last, a, b, risk, stops, tuple(decisions)
    )


def _encoded(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, Decimal):
        return {"decimal": str(value)}
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, timedelta):
        return {"microseconds": (value.days * 86400 + value.seconds) * 1000000 + value.microseconds}
    if is_dataclass(value):
        return {field.name: _encoded(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, dict):
        return {str(key): _encoded(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_encoded(item) for item in value]
    return value


def _canonical(value):
    return (
        json.dumps(
            _encoded(value),
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode()


@pytest.mark.parametrize("direction", list(RegimeDirection))
def test_actual_frozen_gates_admit_two_live_chains_before_the_first_fill(direction):
    first, second = _audit(direction), _audit(direction)
    assert first == second
    assert _canonical(first) == _canonical(second)
    assert first.policy_after_a_pullback.context.state is RegimeContextLifetimeState.CONSUMED
    assert first.policy_after_b_event.position_state is PositionStateV2.FLAT
    assert first.policy_after_b_event.context.state is RegimeContextLifetimeState.ACTIVE
    assert first.policy_after_b_event.context.source_event_bar_index == 34
    assert first.a_before_last_candidate.state is EntryConfirmationStateV2.AWAITING_CONFIRMATION
    assert first.a_before_last_candidate.candidate.price_qualified is False
    assert first.a.state is EntryConfirmationStateV2.CONFIRMED
    assert first.b.state is EntryConfirmationStateV2.AWAITING_CONFIRMATION
    assert first.a.opportunity.consumed_context.source_event_bar_index == 32
    assert first.b.opportunity.consumed_context.source_event_bar_index == 34
    assert first.a.opportunity.consumed_context.pullback_bar_index == 33
    assert first.b.opportunity.consumed_context.pullback_bar_index == 35
    assert first.a.opportunity.consumed_context != first.b.opportunity.consumed_context
    assert first.risk.decisions[0].decision is RiskSizingDecisionV2.APPROVE
    assert first.risk.decisions[0].approved_quantity == 2
    assert (
        first.risk.executions.entries[0].execution_state
        is EntryExecutionStateV2.PENDING_NEXT_BAR_OPEN
    )
    assert first.risk.executions.entries[0].expected_execution_bar_index == 36
    assert first.b.opportunity.first_confirmation_bar == 36
    assert first.policy.position_state is PositionStateV2.FLAT
    for index, (impulse, reversal) in zip(range(32, 36), first.raw_decisions, strict=True):
        assert reversal.event is None
        assert (impulse.event is not None) == (index in (32, 34))
        if impulse.event is not None:
            assert impulse.event.event_direction is direction
            assert impulse.emerging_direction.emerging_direction is direction
            assert impulse.range.range_qualified and impulse.volume.volume_qualified
            assert impulse.body_wick.body_wick_qualified


@pytest.mark.parametrize("direction", list(RegimeDirection))
def test_b_is_actionable_not_just_telemetry_if_a_fails_to_fill(direction):
    first, second = _audit(direction), _audit(direction)
    results = []
    for audit in (first, second):
        risk = execute_risk_approved_entry_open_v2(
            previous=audit.risk,
            decision=audit.risk.decisions[0],
            opening_bar=EntryExecutionOpenV2(36, _time(36), None),
        )
        assert (
            risk.executions.entries[0].execution_state
            is EntryExecutionStateV2.FAILED_INVALID_EXECUTION_INPUT
        )
        # Deliver the same invalid opening into the later complete OHLC observation.
        ema = dict(audit.ema)
        ema[36] = replace(ema[36], open=None)
        raw = dict(audit.raw)
        raw[36] = replace(raw[36], open=None)
        policy, _, _ = _close_policy(audit.policy, 36, raw, ema)
        b = _advance(audit.b, 36, ema)
        assert b.state is EntryConfirmationStateV2.AWAITING_CONFIRMATION
        policy, _, _ = _close_policy(policy, 37, raw, ema)
        b = _advance(b, 37, ema)
        assert b.state is EntryConfirmationStateV2.CONFIRMED
        risk, stops = _authorize(risk, policy, b, audit.stops, 37, ema)
        assert risk.decisions[-1].decision is RiskSizingDecisionV2.APPROVE
        assert risk.executions.entries[-1].expected_execution_bar_index == 38
        risk = execute_risk_approved_entry_open_v2(
            previous=risk,
            decision=risk.decisions[-1],
            opening_bar=EntryExecutionOpenV2(38, _time(38), ema[38].open),
        )
        assert len(risk.filled_entries) == 1
        assert risk.filled_entries[0].execution.confirmation == b.confirmation
        results.append((risk, stops, policy, b))
    assert results[0] == results[1]
    assert _canonical(results[0]) == _canonical(results[1])


@pytest.mark.parametrize("direction", list(RegimeDirection))
@pytest.mark.parametrize("stop_closes_a", [False, True])
def test_filled_a_blocks_stale_b_without_authoring_a_pending_priority(direction, stop_closes_a):
    outcomes = []
    for _ in range(2):
        audit = _audit(direction)
        decision = audit.risk.decisions[0]
        risk = execute_risk_approved_entry_open_v2(
            previous=audit.risk,
            decision=decision,
            opening_bar=EntryExecutionOpenV2(36, _time(36), audit.ema[36].open),
        )
        stops = bind_initial_stop_to_entry_v2(
            previous=audit.stops, confirmation=audit.a.confirmation, executions=risk.executions
        )
        monitor = register_structural_stop_execution_v2(
            previous=StructuralStopExecutionBookV2(),
            initial_stops=stops,
            confirmation=audit.a.confirmation,
        )
        policy = apply_position_entry_fill_v2(
            previous=audit.policy,
            executions=risk.executions,
            stops=monitor,
            confirmation=audit.a.confirmation,
        )
        ema = dict(audit.ema)
        raw = dict(audit.raw)
        if stop_closes_a:
            extreme = "low" if direction is RegimeDirection.LONG else "high"
            level = decision.initial_stop_price
            ema[36] = replace(ema[36], **{extreme: level})
            raw[36] = replace(
                raw[36], **{extreme: Decimal(level.numerator) / Decimal(level.denominator)}
            )
        policy = resolve_position_stop_v2(
            previous=policy, known_bar_index=36, known_bar_timestamp=_time(36), observation=ema[36]
        )
        policy, _, _ = _close_policy(policy, 36, raw, ema)
        b = _advance(audit.b, 36, ema)
        assert b.state is EntryConfirmationStateV2.CONFIRMED
        risk, stops = _authorize(risk, policy, b, stops, 36, ema)
        assert risk.decisions[-1].decision is RiskSizingDecisionV2.REJECT
        expected = (
            RiskSizingRejectionReasonV2.INVALID_POSITION_POLICY_INPUT
            if stop_closes_a
            else RiskSizingRejectionReasonV2.POSITION_ALREADY_OPEN
        )
        assert risk.decisions[-1].rejection_reason is expected
        assert len(risk.executions.entries) == len(risk.filled_entries) == 1
        assert policy.position_state is (
            PositionStateV2.FLAT
            if stop_closes_a
            else PositionStateV2.OPEN_LONG
            if direction is RegimeDirection.LONG
            else PositionStateV2.OPEN_SHORT
        )
        assert (
            execute_risk_approved_entry_open_v2(
                previous=risk, decision=risk.decisions[-1], opening_bar=NoReads()
            )
            is risk
        )
        outcomes.append((risk, stops, policy, b))
    assert outcomes[0] == outcomes[1]
    assert _canonical(outcomes[0]) == _canonical(outcomes[1])


def test_different_consumptions_cannot_target_the_same_open_under_current_windows():
    # A consumed at k; B's earliest new source is k+1 and earliest pullback k+2.
    # This proves a narrower timing property; it does not select a pending-chain policy.
    k = 33
    for b_event in range(k + 1, k + 1 + MAX_CONTEXT_AGE_CLOSED_BARS):
        for b_pullback in range(b_event + 1, b_event + 1 + MAX_CONTEXT_AGE_CLOSED_BARS):
            for a_q in range(k + 1, k + 1 + MAX_CONFIRMATION_AGE_CLOSED_BARS):
                for b_q in range(b_pullback + 1, b_pullback + 1 + MAX_CONFIRMATION_AGE_CLOSED_BARS):
                    assert a_q + 1 < b_q + 1


@pytest.mark.parametrize("direction", list(RegimeDirection))
def test_unavailable_future_values_do_not_change_the_concurrency_verdict(direction):
    normal = _audit(direction)
    mutated = _audit(direction, mutate_future=True)
    names = (
        "policy_after_a_pullback",
        "policy_after_b_event",
        "policy",
        "a_before_last_candidate",
        "a",
        "b",
        "risk",
        "stops",
        "raw_decisions",
    )
    assert tuple(getattr(normal, name) for name in names) == tuple(
        getattr(mutated, name) for name in names
    )
    for audit in (normal, mutated):
        assert _advance(audit.b, 35, NoReads()) is audit.b
        assert _advance(audit.a, 36, NoReads()) is audit.a
        cached = register_risk_position_sizing_v2(
            previous=audit.risk,
            position_policy=audit.policy,
            instrument="MNQ",
            closed_bar_index=35,
            closed_bar_timestamp=_time(35),
            source_bar_closed=True,
            confirmation=audit.a,
            initial_stop=None,
            bars_by_index=NoReads(),
        )
        assert cached is audit.risk
        filled = execute_risk_approved_entry_open_v2(
            previous=cached,
            decision=cached.decisions[0],
            opening_bar=EntryExecutionOpenV2(36, _time(36), Fraction(20000)),
        )
        assert (
            execute_risk_approved_entry_open_v2(
                previous=filled, decision=filled.decisions[0], opening_bar=NoReads()
            )
            is filled
        )
        assert len(filled.filled_entries) == 1


def test_long_short_mirror_retains_symmetric_distinct_sources_and_risk():
    for _ in range(2):
        long, short = _audit(RegimeDirection.LONG), _audit(RegimeDirection.SHORT)
        assert long.a.confirmation.macd == -short.a.confirmation.macd
        assert long.a.confirmation.histogram == -short.a.confirmation.histogram
        assert (
            long.a.opportunity.consumed_context.ema_reference
            + short.a.opportunity.consumed_context.ema_reference
            == 40000
        )
        assert (
            long.risk.decisions[0].initial_stop_price + short.risk.decisions[0].initial_stop_price
            == 40000
        )
        assert long.risk.decisions[0].approved_quantity == short.risk.decisions[0].approved_quantity
        assert (
            long.risk.decisions[0].risk_per_contract_usd
            == short.risk.decisions[0].risk_per_contract_usd
        )
        assert (
            long.b.opportunity.consumed_context.pullback_bar_index
            == short.b.opportunity.consumed_context.pullback_bar_index
        )


def _manifest():
    components = []
    for name in COMPONENTS:
        module = importlib.import_module("agicore.trading." + name)
        components.append(
            {
                "name": name + ".py",
                "source_sha256": hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest(),
                "constants": {
                    key: _encoded(getattr(module, key))
                    for key in getattr(module, "__all__", vars(module))
                    if key.isupper() and not key.startswith("_") and key != "TYPE_CHECKING"
                },
            }
        )
    return {
        "strategy_id": STRATEGY,
        "formalization_version": 1,
        "mode": "OFFLINE_DETERMINISTIC",
        "instrument": "MNQ",
        "timeframe": "1 minute",
        "timeframe_minutes": 1,
        "formalization_status": "BLOCKED_HUMAN_GATE",
        "next_gate": "EMA_PULLBACK_V2_PENDING_OPPORTUNITY_POLICY_REQUIRED",
        "manifest_role": "FROZEN_COMPONENT_SNAPSHOT_NOT_APPROVED_STRATEGY",
        "components": components,
        "prohibitions": {
            name: "FORBIDDEN"
            for name in (
                "REAL_DATA_ACCESS",
                "OOS_ACCESS",
                "REPLAY",
                "BROKER_ACCESS",
                "PAPER_TRADING",
                "PARAMETER_OPTIMIZATION",
            )
        },
        "semantics": {
            "entry": "NEXT_BAR_OPEN_MARKET",
            "stop": "IMMUTABLE_STOP_MARKET",
            "exit": ["STRUCTURAL_STOP", "EMA20_POSITION_EXIT"],
            "opening_exit_priority": "STRUCTURAL_STOP_BEFORE_PENDING_EMA20_EXIT",
            "risk": "CLOSE_CONFIRMATION_PLANNED_STRUCTURAL_PRICE_RISK",
            "costs": "EFFECTIVE_FILL_PRICE_SLIPPAGE_ONCE_PLUS_PER_FILL_FEES",
            "pending_opportunity_policy": "UNRESOLVED",
        },
        "TAKE_PROFIT": None,
        "BREAKEVEN": None,
        "TRAILING_STOP": None,
        "TIME_EXIT": None,
        "SESSION_EXIT": None,
    }


def test_component_snapshot_is_canonical_and_frozen_not_an_approved_strategy():
    first, second = _canonical(_manifest()), _canonical(_manifest())
    assert first == second
    assert first == MANIFEST_PATH.read_bytes()
    assert hashlib.sha256(first).hexdigest() == hashlib.sha256(second).hexdigest()
    value = json.loads(first)
    assert value["formalization_status"] == "BLOCKED_HUMAN_GATE"
    assert value["semantics"]["pending_opportunity_policy"] == "UNRESOLVED"
    assert all(value["prohibitions"][key] == "FORBIDDEN" for key in value["prohibitions"])
