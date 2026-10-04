"""Synthetic position admission using actual qualified V2 chains and stop fills."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import FrozenInstanceError, dataclass, fields, replace
from datetime import UTC, datetime, timedelta
from fractions import Fraction

import pytest

from agicore.trading.ema20_pullback_v2 import EMA20PullbackBarV2
from agicore.trading.ema_pullback_entry_confirmation_v2 import (
    advance_entry_confirmation_momentum_v2,
    begin_entry_confirmation_momentum_v2,
)
from agicore.trading.ema_pullback_entry_execution_v2 import (
    EntryExecutionBookV2,
    EntryExecutionOpenV2,
    EntryExecutionStateV2,
    execute_entry_open_v2,
    register_entry_execution_v2,
)
from agicore.trading.ema_pullback_initial_stop_v2 import (
    InitialStopBookV2,
    bind_initial_stop_to_entry_v2,
    register_initial_stop_v2,
)
from agicore.trading.ema_pullback_open_position_signal_policy_v2 import (
    FLIP_ON_OPPOSITE_SIGNAL,
    HEDGING,
    MAX_SIMULTANEOUS_POSITIONS_PER_SERIES,
    PYRAMIDING,
    SCALE_IN,
    SIGNAL_QUEUE_WHILE_OPEN,
    OpenPositionSignalPolicyBookV2,
    OpenPositionSignalPolicyV2Error,
    advance_open_position_signal_policy_v2,
    apply_position_entry_fill_v2,
    resolve_position_stop_v2,
)
from agicore.trading.ema_pullback_open_position_signal_policy_v2 import (
    PositionSignalAdmissionStatusV2 as Admission,
)
from agicore.trading.ema_pullback_open_position_signal_policy_v2 import PositionStateV2 as State
from agicore.trading.ema_pullback_structural_stop_trigger_fill_v2 import (
    StructuralStopExecutionBookV2,
    observe_structural_stop_v2,
    register_structural_stop_execution_v2,
)
from agicore.trading.ema_pullback_structural_stop_trigger_fill_v2 import (
    StructuralStopExecutionStateV2 as StopState,
)
from agicore.trading.ema_pullback_structural_stop_trigger_fill_v2 import (
    StructuralStopTriggerPhaseV2 as Phase,
)
from agicore.trading.regime_context_v2 import (
    RegimeContextLifetimeState,
    RegimeDirection,
    RegimeEvent,
    RegimeEventType,
)

START = datetime(2026, 10, 4, 8, tzinfo=UTC)
DIRECTIONS = list(RegimeDirection)
FAMILIES = [
    (RegimeEventType.DIRECTIONAL_IMPULSE_EVENT,),
    (RegimeEventType.REVERSAL_TRANSITION_EVENT,),
    tuple(RegimeEventType),
]


def _time(index):
    return START + timedelta(minutes=index)


def _bar(index, open_=10, high=10, low=10, close=10):
    return EMA20PullbackBarV2(index, _time(index), open_, high, low, close, True)


def _events(index, direction, families=FAMILIES[0]):
    events = {family: RegimeEvent(family, direction, index, _time(index)) for family in families}
    return {
        "directional_impulse_event": events.get(RegimeEventType.DIRECTIONAL_IMPULSE_EVENT),
        "reversal_transition_event": events.get(RegimeEventType.REVERSAL_TRANSITION_EVENT),
    }


def _close(policy, index, bars, *, observation=None, direction=None, families=FAMILIES[0]):
    return advance_open_position_signal_policy_v2(
        previous=policy,
        closed_bar_index=index,
        closed_bar_timestamp=_time(index),
        source_bar_closed=True,
        bars_by_index=bars,
        stop_observation=observation,
        **(_events(index, direction, families) if direction is not None else {}),
    )


@dataclass(frozen=True)
class Observation:
    bar_index: int
    timestamp_utc: datetime
    open: object
    high: object
    low: object
    close: object = 10
    volume: object = 1000


class NoReads:
    def __getattr__(self, name):
        raise AssertionError(f"forbidden market read: {name}")


class GuardedBars(Mapping):
    def __init__(self, bars, through):
        self.bars, self.through, self.reads = bars, through, []

    def __getitem__(self, index):
        assert index <= self.through, f"future bar {index}"
        self.reads.append(index)
        return self.bars[index]

    def __iter__(self):
        raise AssertionError("must not scan the series/future")

    def __len__(self):
        raise AssertionError("must not count future bars")


@dataclass(frozen=True)
class Setup:
    before_entry: OpenPositionSignalPolicyBookV2
    policy: OpenPositionSignalPolicyBookV2
    executions: EntryExecutionBookV2
    stops: StructuralStopExecutionBookV2
    decision: object
    bars: dict
    e: int


def _setup(
    direction=RegimeDirection.LONG,
    *,
    families=FAMILIES[0],
    event_index=32,
    previous=None,
    history=None,
    relation="armed",
):
    """Actual admitted context -> consumed pullback -> confirmation -> next Open."""
    bars = {index: _bar(index) for index in range(event_index)}
    if history is not None:
        bars.update({index: bar for index, bar in history.items() if index < event_index})
    stage = {
        event_index: _bar(event_index, 12, 12, 12, 12),
        event_index + 1: _bar(event_index + 1, 12, 15, 10, 11),
        event_index + 2: _bar(event_index + 2, 11, 14, 10, 13),
        event_index + 3: _bar(event_index + 3, 13, 15, 12, 14),
    }
    if direction is RegimeDirection.SHORT:
        stage = {
            index: replace(
                bar, open=20 - bar.open, high=20 - bar.low, low=20 - bar.high, close=20 - bar.close
            )
            for index, bar in stage.items()
        }
    bars.update(stage)
    policy = (
        OpenPositionSignalPolicyBookV2("synthetic-strategy", "synthetic-series")
        if previous is None
        else previous
    )
    policy = _close(
        policy, event_index, GuardedBars(bars, event_index), direction=direction, families=families
    )
    policy = _close(policy, event_index + 1, GuardedBars(bars, event_index + 1))
    pullback = policy.signal_decisions[-1].pullback
    assert pullback.pullback.pullback_qualified is True
    pending = begin_entry_confirmation_momentum_v2(
        pullback=pullback, pullback_bar=bars[event_index + 1]
    )
    q = event_index + 2
    decision = advance_entry_confirmation_momentum_v2(
        previous=pending,
        closed_bar_index=q,
        closed_bar_timestamp=_time(q),
        source_bar_closed=True,
        bars_by_index=GuardedBars(bars, q),
    )
    assert decision.entry_confirmation is True
    policy = _close(policy, q, GuardedBars(bars, q))
    initial_stops = register_initial_stop_v2(
        previous=InitialStopBookV2(), confirmation=decision, bars_by_index=GuardedBars(bars, q)
    )
    stop_price = initial_stops.for_confirmation(decision.confirmation).initial_stop
    offset = {"armed": Fraction(13, 4), "equal": Fraction(0), "beyond": Fraction(-1)}[relation]
    entry_price = stop_price + offset if direction is RegimeDirection.LONG else stop_price - offset
    executions = register_entry_execution_v2(previous=EntryExecutionBookV2(), confirmation=decision)
    e = q + 1
    executions = execute_entry_open_v2(
        previous=executions,
        confirmation=decision.confirmation,
        opening_bar=EntryExecutionOpenV2(e, _time(e), entry_price),
    )
    initial_stops = bind_initial_stop_to_entry_v2(
        previous=initial_stops, confirmation=decision.confirmation, executions=executions
    )
    stops = register_structural_stop_execution_v2(
        previous=StructuralStopExecutionBookV2(),
        initial_stops=initial_stops,
        confirmation=decision.confirmation,
    )
    opened = apply_position_entry_fill_v2(
        previous=policy, executions=executions, stops=stops, confirmation=decision.confirmation
    )
    return Setup(policy, opened, executions, stops, decision, bars, e)


def _observation(policy, index, *, outcome="untouched"):
    position = policy.active_position
    direction = position.entry.execution_side
    level = position.initial_stop_at_entry.initial_stop_record.initial_stop_price
    sign = 1 if direction is RegimeDirection.LONG else -1
    opening = (
        position.entry.execution_price_before_costs
        if index == position.entry.execution_bar_index
        else level + sign * 3
    )
    adverse = level + sign
    if outcome == "gap":
        opening, adverse = level - sign, NoReads()
    elif outcome == "touch":
        adverse = level
    elif outcome == "invalid":
        adverse = opening + sign
    return Observation(
        index, _time(index), opening, 100 if sign == 1 else adverse, adverse if sign == 1 else 0
    )


def _entry_close(setup):
    return _close(setup.policy, setup.e, NoReads(), observation=_observation(setup.policy, setup.e))


def test_initial_constants_are_frozen_without_queue_or_position_expansion():
    assert MAX_SIMULTANEOUS_POSITIONS_PER_SERIES == 1
    assert (PYRAMIDING, HEDGING, FLIP_ON_OPPOSITE_SIGNAL, SCALE_IN, SIGNAL_QUEUE_WHILE_OPEN) == (
        False,
    ) * 5


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("families", FAMILIES)
def test_flat_admits_regime_context_then_actual_fill_opens_position(direction, families):
    setup = _setup(direction, families=families)
    first = setup.before_entry.signal_decisions[0]
    assert first.status is Admission.ADMITTED
    assert first.position_state_at_signal_decision is State.FLAT
    assert first.pullback.lifetime.context.source_event_types == families
    assert first.pullback.lifetime.context.source_event_direction is direction
    assert first.pullback.pullback is None  # Event bar cannot consume itself.
    assert (
        setup.before_entry.position_state is State.FLAT
    )  # Context/pullback/confirmation are not fills.
    assert setup.policy.position_state is (
        State.OPEN_LONG if direction is RegimeDirection.LONG else State.OPEN_SHORT
    )
    assert len(setup.policy.positions) == 1
    assert setup.policy.context is None
    assert (
        setup.policy.positions[0].entry
        is setup.executions.for_confirmation(setup.decision.confirmation).execution
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("terminal", [False, True])
def test_pending_or_expired_execution_does_not_open_position(direction, terminal):
    setup = _setup(direction)
    executions = register_entry_execution_v2(
        previous=EntryExecutionBookV2(), confirmation=setup.decision
    )
    if terminal:
        executions = execute_entry_open_v2(
            previous=executions, confirmation=setup.decision.confirmation, opening_bar=None
        )
    result = apply_position_entry_fill_v2(
        previous=setup.before_entry,
        executions=executions,
        stops=NoReads(),
        confirmation=setup.decision.confirmation,
    )
    assert result is setup.before_entry
    assert result.position_state is State.FLAT
    assert not result.positions


@pytest.mark.parametrize("position_direction", DIRECTIONS)
@pytest.mark.parametrize("signal_direction", DIRECTIONS)
@pytest.mark.parametrize("families", FAMILIES)
def test_open_suppresses_every_direction_before_context_or_pullback_creation(
    position_direction, signal_direction, families
):
    setup = _setup(position_direction)
    policy = _close(
        setup.policy,
        setup.e,
        NoReads(),
        observation=_observation(setup.policy, setup.e),
        direction=signal_direction,
        families=families,
    )
    decision = policy.signal_decisions[-1]
    assert decision.status is Admission.SUPPRESSED_POSITION_OPEN
    assert decision.position_state_at_signal_decision is setup.policy.position_state
    assert policy.position_state is setup.policy.position_state
    assert policy.positions == setup.policy.positions
    assert policy.context is None and policy.lifetime is None and decision.pullback is None
    assert tuple(event.event_type for event in decision.composition.events) == families
    assert len(decision.suppressions) == 1
    notice = decision.suppressions[0]
    assert notice.signal_bar_index == setup.e and notice.signal_timestamp == _time(setup.e)
    assert notice.signal_direction is signal_direction and notice.source_event_types == families
    assert notice.active_position_entry_bar_index == setup.e
    assert notice.active_position_direction is position_direction
    assert notice.position_state is setup.policy.position_state
    assert notice.suppression_reason == "POSITION_ALREADY_OPEN"


@pytest.mark.parametrize("position_direction", DIRECTIONS)
@pytest.mark.parametrize("new_direction", DIRECTIONS)
def test_bypassed_second_fill_cannot_pyramid_hedge_flip_or_scale_in(
    position_direction, new_direction
):
    setup, other = _setup(position_direction), _setup(new_direction, event_index=40)
    snapshot = setup.policy
    with pytest.raises(OpenPositionSignalPolicyV2Error, match="one-position"):
        apply_position_entry_fill_v2(
            previous=snapshot,
            executions=other.executions,
            stops=other.stops,
            confirmation=other.decision.confirmation,
        )
    assert len(snapshot.positions) == 1
    assert (
        snapshot.positions[0].entry.execution_price_before_costs
        == setup.policy.positions[0].entry.execution_price_before_costs
    )
    assert not {"quantity", "average_entry_price", "pending_reverse", "signal_queue"} & {
        field.name for field in fields(snapshot)
    }


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_suppressed_signal_is_permanently_lost_after_exit(direction):
    setup = _setup(direction)
    policy = _entry_close(setup)
    opposite = RegimeDirection.SHORT if direction is RegimeDirection.LONG else RegimeDirection.LONG
    policy = _close(
        policy,
        setup.e + 1,
        NoReads(),
        observation=_observation(policy, setup.e + 1),
        direction=opposite,
    )
    suppressed = policy.signal_decisions[-1]
    policy = _close(
        policy,
        setup.e + 2,
        NoReads(),
        observation=_observation(policy, setup.e + 2, outcome="touch"),
    )
    assert policy.position_state is State.FLAT
    assert policy.context.state is RegimeContextLifetimeState.INACTIVE
    policy = _close(policy, setup.e + 3, NoReads())
    assert policy.signal_decisions[-1].pullback.pullback is None
    assert policy.context.state is RegimeContextLifetimeState.INACTIVE
    assert (
        suppressed in policy.signal_decisions
        and suppressed.status is Admission.SUPPRESSED_POSITION_OPEN
    )
    assert len(policy.positions) == 1
    # Even an externally constructed complete chain from the suppressed source cannot enter.
    stale = _setup(opposite, event_index=setup.e + 1)
    with pytest.raises(OpenPositionSignalPolicyV2Error, match="fresh admitted"):
        apply_position_entry_fill_v2(
            previous=policy,
            executions=stale.executions,
            stops=stale.stops,
            confirmation=stale.decision.confirmation,
        )


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("outcome,phase", [("gap", Phase.BAR_OPEN_GAP), ("touch", Phase.INTRABAR)])
@pytest.mark.parametrize("families", FAMILIES)
def test_exit_resolves_before_same_bar_fresh_regime_admission(direction, outcome, phase, families):
    setup = _setup(direction)
    policy = _entry_close(setup)
    index = setup.e + 1
    policy = _close(
        policy,
        index,
        NoReads(),
        observation=_observation(policy, index, outcome=outcome),
        direction=direction,
        families=families,
    )
    assert policy.position_state is State.FLAT
    assert policy.positions[-1].exit.trigger_phase is phase
    assert policy.positions[-1].exit.trigger_bar_index == index
    assert policy.signal_decisions[-1].position_state_at_signal_decision is State.FLAT
    assert policy.signal_decisions[-1].status is Admission.ADMITTED
    assert policy.context.state is RegimeContextLifetimeState.ACTIVE
    assert policy.context.source_event_bar_index == index
    assert policy.context.first_eligible_pullback_bar == index + 1
    assert policy.signal_decisions[-1].pullback.pullback is None
    assert setup.policy.positions[0].exit is None  # Earlier snapshots remain open.


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("relation", ["equal", "beyond"])
@pytest.mark.parametrize("families", FAMILIES)
def test_breached_entry_exists_then_immediately_exits_then_new_close_event_allowed(
    direction, relation, families
):
    setup = _setup(direction, relation=relation, families=families)
    assert setup.policy.position_state is not State.FLAT
    assert setup.policy.active_stop.stop_execution_state is StopState.FILLED_STOP
    flat = resolve_position_stop_v2(
        previous=setup.policy,
        known_bar_index=setup.e,
        known_bar_timestamp=_time(setup.e),
        observation=NoReads(),
    )
    assert flat.position_state is State.FLAT
    assert len(flat.positions) == 1
    assert flat.positions[0].entry is setup.policy.positions[0].entry
    assert flat.positions[0].exit.trigger_phase is Phase.ENTRY_OPEN
    assert (
        flat.positions[0].exit.base_stop_fill_price
        == flat.positions[0].entry.execution_price_before_costs
    )
    assert flat.positions[0].exit.trigger_bar_index == setup.e
    assert (
        setup.executions.for_confirmation(setup.decision.confirmation).execution_state
        is EntryExecutionStateV2.FILLED
    )
    policy = _close(flat, setup.e, NoReads(), direction=direction, families=families)
    assert policy.signal_decisions[-1].status is Admission.ADMITTED
    assert policy.context.source_event_bar_index == setup.e


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_duplicate_fill_repeated_close_and_terminal_exit_are_idempotent(direction):
    setup = _setup(direction)
    duplicate = apply_position_entry_fill_v2(
        previous=setup.policy,
        executions=setup.executions,
        stops=NoReads(),
        confirmation=setup.decision.confirmation,
    )
    assert duplicate is setup.policy
    policy = _close(
        setup.policy,
        setup.e,
        NoReads(),
        observation=_observation(setup.policy, setup.e),
        direction=direction,
    )
    assert _close(policy, setup.e, NoReads(), observation=NoReads(), direction=direction) is policy
    exited = _close(
        policy,
        setup.e + 1,
        NoReads(),
        observation=_observation(policy, setup.e + 1, outcome="touch"),
    )
    assert _close(exited, setup.e + 1, NoReads(), observation=NoReads()) is exited
    assert (
        resolve_position_stop_v2(
            previous=exited,
            known_bar_index=setup.e + 1,
            known_bar_timestamp=_time(setup.e + 1),
            observation=NoReads(),
        )
        is exited
    )
    assert (
        apply_position_entry_fill_v2(
            previous=exited,
            executions=setup.executions,
            stops=NoReads(),
            confirmation=setup.decision.confirmation,
        )
        is exited
    )
    assert len(exited.positions) == 1
    assert exited.positions[0].exit is not None
    assert sum(position.exit is not None for position in exited.positions) == 1


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_entry_bar_intrabar_exit_allows_new_event_at_its_close(direction):
    setup = _setup(direction)
    policy = _close(
        setup.policy,
        setup.e,
        NoReads(),
        observation=_observation(setup.policy, setup.e, outcome="touch"),
        direction=direction,
    )
    assert policy.position_state is State.FLAT
    assert policy.positions[0].exit.trigger_phase is Phase.INTRABAR
    assert policy.signal_decisions[-1].status is Admission.ADMITTED


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_failed_stop_observation_does_not_make_flat_or_admit_new_context(direction):
    setup = _setup(direction)
    policy = _close(
        setup.policy,
        setup.e,
        NoReads(),
        observation=_observation(setup.policy, setup.e, outcome="invalid"),
        direction=direction,
    )
    assert policy.active_stop.stop_execution_state is StopState.FAILED_INVALID_STOP_OBSERVATION
    assert policy.position_state is setup.policy.position_state
    assert policy.positions[0].exit is None
    assert policy.signal_decisions[-1].status is Admission.SUPPRESSED_POSITION_OPEN
    assert policy.context is None
    policy = _close(policy, setup.e + 1, NoReads(), observation=NoReads(), direction=direction)
    assert policy.active_stop.stop_execution_state is StopState.FAILED_INVALID_STOP_OBSERVATION
    assert policy.position_state is setup.policy.position_state


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_missing_stop_observation_never_synthesizes_an_exit(direction):
    setup = _setup(direction)
    policy = _close(setup.policy, setup.e, NoReads(), direction=direction)
    assert policy.position_state is setup.policy.position_state
    assert policy.active_stop.stop_execution_state is StopState.ARMED
    assert policy.positions[0].exit is None
    policy = _close(
        policy,
        setup.e + 1,
        NoReads(),
        observation=_observation(policy, setup.e + 1),
        direction=direction,
    )
    assert policy.active_stop.stop_execution_state is StopState.FAILED_INCOMPLETE_STOP_OBSERVATION
    assert policy.position_state is setup.policy.position_state
    assert policy.context is None


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_ambiguous_raw_telemetry_while_open_neither_flips_nor_creates_context(direction):
    setup = _setup(direction)
    events = {
        "directional_impulse_event": RegimeEvent(
            RegimeEventType.DIRECTIONAL_IMPULSE_EVENT, RegimeDirection.LONG, setup.e, _time(setup.e)
        ),
        "reversal_transition_event": RegimeEvent(
            RegimeEventType.REVERSAL_TRANSITION_EVENT,
            RegimeDirection.SHORT,
            setup.e,
            _time(setup.e),
        ),
    }
    policy = advance_open_position_signal_policy_v2(
        previous=setup.policy,
        closed_bar_index=setup.e,
        closed_bar_timestamp=_time(setup.e),
        source_bar_closed=True,
        bars_by_index=NoReads(),
        stop_observation=_observation(setup.policy, setup.e),
        **events,
    )
    assert policy.signal_decisions[-1].composition.status.value == "AMBIGUOUS"
    assert policy.signal_decisions[-1].status is Admission.SUPPRESSED_POSITION_OPEN
    assert len(policy.signal_decisions[-1].suppressions) == 2
    assert policy.positions == setup.policy.positions and policy.context is None


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_only_fresh_post_exit_chain_can_create_second_position(direction):
    setup = _setup(direction)
    flat = _close(
        setup.policy,
        setup.e,
        NoReads(),
        observation=_observation(setup.policy, setup.e, outcome="touch"),
    )
    next_setup = _setup(direction, event_index=80, previous=flat, history=setup.bars)
    assert len(next_setup.policy.positions) == 2
    assert next_setup.policy.positions[0] == flat.positions[0]
    assert next_setup.policy.positions[1].entry.source_regime_event_bar_index == 80
    assert next_setup.policy.position_state is setup.policy.position_state


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_old_pre_entry_admitted_chain_cannot_be_restored_after_exit(direction):
    setup = _setup(direction)
    flat = _close(
        setup.policy,
        setup.e,
        NoReads(),
        observation=_observation(setup.policy, setup.e, outcome="touch"),
    )
    # A different fill cannot borrow the old consumed source after eligibility returns.
    changed_record = replace(
        setup.decision.confirmation,
        confirmation_bar_index=setup.e + 1,
        confirmation_timestamp=_time(setup.e + 1),
    )
    changed_fill = replace(
        setup.policy.positions[0].entry,
        confirmation=changed_record,
        confirmation_bar_index=setup.e + 1,
        confirmation_timestamp=_time(setup.e + 1),
        execution_bar_index=setup.e + 2,
        execution_bar_timestamp=_time(setup.e + 2),
    )
    flat = _close(flat, setup.e + 1, NoReads())
    execution = replace(
        setup.executions.entries[0], confirmation=changed_record, execution=changed_fill
    )
    with pytest.raises(OpenPositionSignalPolicyV2Error, match="fresh admitted"):
        apply_position_entry_fill_v2(
            previous=flat,
            executions=EntryExecutionBookV2((execution,)),
            stops=NoReads(),
            confirmation=changed_record,
        )


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_separate_series_and_strategy_instances_have_no_global_position_limit(direction):
    setup = _setup(direction)
    for strategy, series in [
        ("synthetic-strategy", "other-series"),
        ("other-strategy", "synthetic-series"),
    ]:
        other = OpenPositionSignalPolicyBookV2(strategy, series)
        admitted = _close(other, setup.e, NoReads(), direction=direction)
        assert admitted.position_state is State.FLAT
        assert admitted.signal_decisions[-1].status is Admission.ADMITTED
        assert setup.policy.position_state is not State.FLAT


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_provenance_and_suppression_snapshots_are_immutable(direction):
    setup = _setup(direction, families=FAMILIES[2])
    policy = _close(
        setup.policy,
        setup.e,
        NoReads(),
        observation=_observation(setup.policy, setup.e),
        direction=direction,
    )
    suppressed = policy.signal_decisions[-1].suppressions[0]
    with pytest.raises(FrozenInstanceError):
        suppressed.signal_direction = None
    with pytest.raises(FrozenInstanceError):
        policy.positions[0].entry.execution_price_before_costs = Fraction(99)
    with pytest.raises(FrozenInstanceError):
        policy.positions = ()
    flat = _close(
        policy,
        setup.e + 1,
        NoReads(),
        observation=_observation(policy, setup.e + 1, outcome="touch"),
    )
    position = flat.positions[0]
    assert position.entry is setup.policy.positions[0].entry
    assert position.exit.initial_stop_at_entry is position.initial_stop_at_entry
    assert position.exit.initial_stop_at_entry.execution is position.entry
    assert position.entry.confirmation is setup.decision.confirmation
    assert position.entry.source_regime_event_types == FAMILIES[2]
    assert policy.positions[0].exit is None


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_altered_duplicate_fill_provenance_is_rejected(direction):
    setup = _setup(direction)
    execution = setup.executions.entries[0]
    altered = replace(
        execution, execution=replace(execution.execution, execution_price_before_costs=Fraction(99))
    )
    with pytest.raises(OpenPositionSignalPolicyV2Error, match="cannot change"):
        apply_position_entry_fill_v2(
            previous=setup.policy,
            executions=EntryExecutionBookV2((altered,)),
            stops=NoReads(),
            confirmation=setup.decision.confirmation,
        )


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_future_market_mutations_have_no_effect_before_processing_that_bar(direction):
    setup = _setup(direction)
    future = {**setup.bars, setup.e + 1: NoReads(), setup.e + 9: NoReads()}
    left = _close(
        setup.policy,
        setup.e,
        GuardedBars(setup.bars, setup.e),
        observation=_observation(setup.policy, setup.e),
        direction=direction,
    )
    right = _close(
        setup.policy,
        setup.e,
        GuardedBars(future, setup.e),
        observation=_observation(setup.policy, setup.e),
        direction=direction,
    )
    assert left == right
    # The FLAT event-admission path also never scans future bars.
    flat = OpenPositionSignalPolicyBookV2("synthetic-strategy", "synthetic-series")
    assert _close(flat, 32, GuardedBars(setup.bars, 32), direction=direction) == _close(
        flat, 32, GuardedBars(future, 32), direction=direction
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_future_stop_observation_cannot_close_current_position_early(direction):
    setup = _setup(direction)
    with pytest.raises(OpenPositionSignalPolicyV2Error, match="current bar"):
        _close(
            setup.policy,
            setup.e,
            NoReads(),
            observation=_observation(setup.policy, setup.e + 1, outcome="touch"),
            direction=direction,
        )
    assert setup.policy.positions[0].exit is None


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("outcome", ["untouched", "touch", "invalid", "future_gap"])
def test_entry_open_cannot_import_already_observed_or_future_stop_state(direction, outcome):
    setup = _setup(direction)
    stops = observe_structural_stop_v2(
        previous=setup.stops,
        confirmation=setup.decision.confirmation,
        observation=_observation(
            setup.policy, setup.e, outcome="untouched" if outcome == "future_gap" else outcome
        ),
    )
    if outcome == "future_gap":
        stops = observe_structural_stop_v2(
            previous=stops,
            confirmation=setup.decision.confirmation,
            observation=_observation(setup.policy, setup.e + 1, outcome="gap"),
        )
    with pytest.raises(OpenPositionSignalPolicyV2Error, match="known at entry Open"):
        apply_position_entry_fill_v2(
            previous=setup.before_entry,
            executions=setup.executions,
            stops=stops,
            confirmation=setup.decision.confirmation,
        )
    assert setup.before_entry.position_state is State.FLAT


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_future_confirmation_fill_requires_its_closed_policy_decision(direction):
    setup = _setup(direction)
    before_confirmation = replace(
        setup.before_entry,
        signal_decisions=setup.before_entry.signal_decisions[:-1],
        lifetime=setup.before_entry.signal_decisions[-2].pullback.lifetime,
    )
    with pytest.raises(OpenPositionSignalPolicyV2Error, match="known confirmation Close"):
        apply_position_entry_fill_v2(
            previous=before_confirmation,
            executions=setup.executions,
            stops=setup.stops,
            confirmation=setup.decision.confirmation,
        )


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_session_time_gap_does_not_expire_open_position_or_stop(direction):
    setup = _setup(direction)
    policy = _entry_close(setup)
    index = setup.e + 1
    later = _time(index) + timedelta(days=1)
    observation = replace(_observation(policy, index, outcome="gap"), timestamp_utc=later)
    event = RegimeEvent(RegimeEventType.DIRECTIONAL_IMPULSE_EVENT, direction, index, later)
    policy = advance_open_position_signal_policy_v2(
        previous=policy,
        closed_bar_index=index,
        closed_bar_timestamp=later,
        source_bar_closed=True,
        bars_by_index=NoReads(),
        stop_observation=observation,
        directional_impulse_event=event,
    )
    assert policy.position_state is State.FLAT
    assert policy.positions[-1].exit.trigger_phase is Phase.BAR_OPEN_GAP
    assert policy.positions[-1].exit.trigger_bar_timestamp == later
    assert policy.signal_decisions[-1].status is Admission.ADMITTED
    assert policy.context.source_event_timestamp == later


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_noncausal_or_changed_close_cannot_rewrite_admission(direction):
    setup = _setup(direction)
    policy = _entry_close(setup)
    with pytest.raises(OpenPositionSignalPolicyV2Error, match="strictly increase"):
        _close(policy, setup.e - 1, NoReads())
    with pytest.raises(OpenPositionSignalPolicyV2Error, match="cannot change"):
        _close(policy, setup.e, NoReads(), direction=direction)
    with pytest.raises(OpenPositionSignalPolicyV2Error, match="precede"):
        resolve_position_stop_v2(
            previous=policy,
            known_bar_index=setup.e,
            known_bar_timestamp=_time(setup.e),
            observation=NoReads(),
        )


@pytest.mark.parametrize("families", FAMILIES)
def test_long_short_mirror_state_admission_and_fill_symmetry(families):
    long, short = (
        _setup(RegimeDirection.LONG, families=families),
        _setup(RegimeDirection.SHORT, families=families),
    )
    assert (
        long.policy.positions[0].entry.execution_price_before_costs
        + short.policy.positions[0].entry.execution_price_before_costs
        == 20
    )
    results = []
    for setup in (long, short):
        direction = setup.policy.positions[0].entry.execution_side
        policy = _close(
            setup.policy,
            setup.e,
            NoReads(),
            observation=_observation(setup.policy, setup.e),
            direction=direction,
        )
        assert policy.signal_decisions[-1].status is Admission.SUPPRESSED_POSITION_OPEN
        policy = _close(
            policy,
            setup.e + 1,
            NoReads(),
            observation=_observation(policy, setup.e + 1, outcome="touch"),
            direction=direction,
        )
        results.append(policy)
    left, right = results
    assert left.position_state is right.position_state is State.FLAT
    assert left.context.state is right.context.state is RegimeContextLifetimeState.ACTIVE
    assert (
        left.positions[0].exit.base_stop_fill_price + right.positions[0].exit.base_stop_fill_price
        == 20
    )
    assert left.positions[0].exit.trigger_bar_index == right.positions[0].exit.trigger_bar_index
    assert [decision.status for decision in left.signal_decisions] == [
        decision.status for decision in right.signal_decisions
    ]
