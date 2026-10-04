"""Synthetic causal STOP_MARKET fills from actual V2 confirmation/entry/stop records."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, dataclass, fields, replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal, Inexact, localcontext
from fractions import Fraction

import pytest

from agicore.trading.ema20_pullback_v2 import EMA20PullbackBarV2, advance_ema20_pullback_v2
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
    INITIAL_STOP_RECALCULATION,
    InitialStopBookV2,
    bind_initial_stop_to_entry_v2,
    register_initial_stop_v2,
)
from agicore.trading.ema_pullback_structural_stop_trigger_fill_v2 import (
    STOP_EXPIRES_AT_SESSION_BOUNDARY,
    STOP_EXPIRES_ON_TIME_GAP,
    STOP_ORDER_SEMANTICS,
    STOP_TOUCH_IS_TRIGGER,
    ProtectiveStopActionV2,
    StructuralStopExecutionBookV2,
    StructuralStopExecutionV2Error,
    observe_structural_stop_v2,
    register_structural_stop_execution_v2,
)
from agicore.trading.ema_pullback_structural_stop_trigger_fill_v2 import (
    StructuralStopExecutionStateV2 as State,
)
from agicore.trading.ema_pullback_structural_stop_trigger_fill_v2 import (
    StructuralStopExecutionStatusV2 as Status,
)
from agicore.trading.ema_pullback_structural_stop_trigger_fill_v2 import (
    StructuralStopTriggerPhaseV2 as Phase,
)
from agicore.trading.regime_context_v2 import (
    RegimeDirection,
    RegimeEvent,
    RegimeEventType,
    advance_regime_context_v2,
)

START = datetime(2026, 10, 4, 8, tzinfo=UTC)
DIRECTIONS = list(RegimeDirection)
FAMILIES = list(RegimeEventType)
INVALID_PRICES = [
    None,
    Decimal("NaN"),
    Decimal("sNaN"),
    Decimal("Infinity"),
    Decimal("-Infinity"),
    12.0,
    "12",
    True,
]


def _timestamp(index):
    return START + timedelta(minutes=index)


def _bar(index, open_=10, high=10, low=10, close=10):
    return EMA20PullbackBarV2(index, _timestamp(index), open_, high, low, close, True)


def _setup(
    direction=RegimeDirection.LONG, *, entry_relation="valid", second=False, families=(FAMILIES[0],)
):
    """Actual qualified pullback, momentum confirmation, next Open and structural stop."""
    bars = {index: _bar(index) for index in range(32)}
    bars[32] = _bar(32, 12, 12, 12, 12)
    bars[33] = _bar(33, 12, 15, 10, 11)
    bars[34] = _bar(34, 14 if second else 11, 14, 10, 13)
    bars[35] = _bar(35, 13, 15, 12, 14)
    if direction is RegimeDirection.SHORT:
        bars = {
            index: replace(
                bar, open=20 - bar.open, high=20 - bar.low, low=20 - bar.high, close=20 - bar.close
            )
            for index, bar in bars.items()
        }
    events = {family: RegimeEvent(family, direction, 32, _timestamp(32)) for family in families}
    active = advance_regime_context_v2(
        previous=None,
        closed_bar_index=32,
        closed_bar_timestamp=_timestamp(32),
        source_bar_closed=True,
        directional_impulse_event=events.get(FAMILIES[0]),
        reversal_transition_event=events.get(FAMILIES[1]),
    )
    pullback = advance_ema20_pullback_v2(
        previous=active,
        closed_bar_index=33,
        closed_bar_timestamp=_timestamp(33),
        source_bar_closed=True,
        bars_by_index=bars,
    )
    pending = begin_entry_confirmation_momentum_v2(pullback=pullback, pullback_bar=bars[33])
    decision = advance_entry_confirmation_momentum_v2(
        previous=pending,
        closed_bar_index=34,
        closed_bar_timestamp=_timestamp(34),
        source_bar_closed=True,
        bars_by_index=bars,
    )
    if second:
        decision = advance_entry_confirmation_momentum_v2(
            previous=decision,
            closed_bar_index=35,
            closed_bar_timestamp=_timestamp(35),
            source_bar_closed=True,
            bars_by_index=bars,
        )
    assert decision.entry_confirmation is True
    stops = register_initial_stop_v2(
        previous=InitialStopBookV2(), confirmation=decision, bars_by_index=bars
    )
    level = stops.for_confirmation(decision.confirmation).initial_stop
    offset = {"valid": Fraction(13, 4), "equal": Fraction(0), "beyond": Fraction(-5, 4)}[
        entry_relation
    ]
    entry_price = _relative(level, direction, offset)
    executions = register_entry_execution_v2(previous=EntryExecutionBookV2(), confirmation=decision)
    e = decision.confirmation.confirmation_bar_index + 1
    executions = execute_entry_open_v2(
        previous=executions,
        confirmation=decision.confirmation,
        opening_bar=EntryExecutionOpenV2(e, _timestamp(e), entry_price),
    )
    stops = bind_initial_stop_to_entry_v2(
        previous=stops, confirmation=decision.confirmation, executions=executions
    )
    return decision, stops, executions


def _relative(level, direction, offset):
    return level + offset if direction is RegimeDirection.LONG else level - offset


def _register(decision, stops, previous=None):
    return register_structural_stop_execution_v2(
        previous=StructuralStopExecutionBookV2() if previous is None else previous,
        initial_stops=stops,
        confirmation=decision.confirmation,
    )


def _state(book, decision):
    return book.for_confirmation(decision.confirmation)


def _observe(book, decision, observation):
    return observe_structural_stop_v2(
        previous=book, confirmation=decision.confirmation, observation=observation
    )


@dataclass(frozen=True)
class CompleteBar:
    bar_index: int
    timestamp_utc: datetime
    open: object
    high: object
    low: object
    close: object = Decimal(12)
    volume: object = 1000
    is_closed: object = True


def _observation(source, offset=0, *, opening=None, adverse=None, timestamp=None):
    bound = source.initial_stop_at_entry
    direction = bound.initial_stop_record.source_regime_event_direction
    level = bound.initial_stop_record.initial_stop_price
    index = bound.entry_bar_index + offset
    opening = bound.entry_price if opening is None else opening
    adverse = _relative(level, direction, Fraction(1)) if adverse is None else adverse
    return CompleteBar(
        index,
        _timestamp(index) if timestamp is None else timestamp,
        opening,
        100 if direction is RegimeDirection.LONG else adverse,
        adverse if direction is RegimeDirection.LONG else 0,
    )


class ReadGuard:
    def __init__(self, bar, allowed):
        self.bar, self.allowed, self.reads = bar, allowed, []

    def __getattr__(self, name):
        assert name in self.allowed, name
        self.reads.append(name)
        return getattr(self.bar, name)


class NoReads:
    def __getattr__(self, name):
        raise AssertionError(f"terminal stop must not read {name}")


def _after_entry(decision, stops):
    book = _register(decision, stops)
    return _observe(book, decision, _observation(_state(book, decision)))


def test_exact_baseline_has_no_time_or_session_expiration():
    assert STOP_ORDER_SEMANTICS == "STOP_MARKET"
    assert STOP_TOUCH_IS_TRIGGER is True
    assert STOP_EXPIRES_ON_TIME_GAP is False
    assert STOP_EXPIRES_AT_SESSION_BOUNDARY is False
    assert INITIAL_STOP_RECALCULATION == "FORBIDDEN"


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("relation", ["equal", "beyond"])
def test_breached_entry_fills_same_open_without_cancelling_entry_or_reading_range(
    direction, relation
):
    decision, stops, executions = _setup(direction, entry_relation=relation)
    original_entry = executions.for_confirmation(decision.confirmation)
    bound = stops.for_confirmation(decision.confirmation).at_entry
    book = _register(decision, stops)
    result = _state(book, decision)
    assert result.stop_triggered is True
    assert result.stop_execution_state is State.FILLED_STOP
    assert result.fill.trigger_phase is Phase.ENTRY_OPEN
    assert result.fill.trigger_known_at == "Open[e]"
    assert result.fill.base_stop_fill_price == result.fill.entry_price == bound.entry_price
    assert result.fill.trigger_bar_index == bound.entry_bar_index
    assert result.fill.trigger_bar_timestamp == bound.entry_bar_timestamp
    assert result.fill.protective_action is (
        ProtectiveStopActionV2.SELL
        if direction is RegimeDirection.LONG
        else ProtectiveStopActionV2.BUY_TO_COVER
    )
    if relation == "beyond":
        assert result.fill.base_stop_fill_price != bound.initial_stop_record.initial_stop_price
    assert executions.for_confirmation(decision.confirmation) is original_entry
    assert original_entry.execution_state is EntryExecutionStateV2.FILLED
    assert result.fill.initial_stop_at_entry.execution is original_entry.execution
    assert _observe(book, decision, NoReads()) is book
    assert _register(decision, stops, book) is book


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("distance", [Fraction(1), Fraction(0), Fraction(-1)])
def test_armed_entry_bar_is_protected_without_another_gap_test(direction, distance):
    decision, stops, _ = _setup(direction)
    before = _register(decision, stops)
    source = _state(before, decision)
    bound = source.initial_stop_at_entry
    level = bound.initial_stop_record.initial_stop_price
    adverse = _relative(level, direction, distance)
    field = "low" if direction is RegimeDirection.LONG else "high"
    observation = ReadGuard(
        _observation(source, adverse=adverse), {"bar_index", "timestamp_utc", field}
    )
    after = _observe(before, decision, observation)
    result = _state(after, decision)
    assert source.monitoring_first_bar == source.next_observation_bar_index == bound.entry_bar_index
    assert "open" not in observation.reads
    if distance > 0:
        assert result.stop_execution_state is State.ARMED
        assert result.fill is None
        assert result.next_observation_bar_index == bound.entry_bar_index + 1
    else:
        assert result.stop_execution_state is State.FILLED_STOP
        assert result.fill.trigger_phase is Phase.INTRABAR
        assert result.fill.base_stop_fill_price == level
        assert result.fill.trigger_bar_index == bound.entry_bar_index
        assert result.fill.trigger_known_at == "NO_LATER_THAN_CLOSE[r]"
        assert result.fill.exact_intrabar_timestamp is None
    assert source.stop_execution_state is State.ARMED


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("distance", [Fraction(0), Fraction(-3, 2)])
def test_later_open_touch_or_gap_fills_open_before_any_extreme_read(direction, distance):
    decision, stops, _ = _setup(direction)
    book = _after_entry(decision, stops)
    source = _state(book, decision)
    level = source.initial_stop_at_entry.initial_stop_record.initial_stop_price
    opening = _relative(level, direction, distance)
    observation = ReadGuard(
        _observation(source, 1, opening=opening), {"bar_index", "timestamp_utc", "open"}
    )
    result = _state(_observe(book, decision, observation), decision)
    assert observation.reads == ["bar_index", "timestamp_utc", "open"]
    assert result.stop_execution_state is State.FILLED_STOP
    assert result.fill.trigger_phase is Phase.BAR_OPEN_GAP
    assert result.fill.base_stop_fill_price == opening
    assert result.fill.trigger_known_at == "Open[r]"
    if distance < 0:
        assert result.fill.base_stop_fill_price != level


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("distance", [Fraction(1), Fraction(0), Fraction(-1)])
def test_later_no_gap_uses_adverse_touch_and_fixed_stop_level(direction, distance):
    decision, stops, _ = _setup(direction)
    book = _after_entry(decision, stops)
    source = _state(book, decision)
    level = source.initial_stop_at_entry.initial_stop_record.initial_stop_price
    field = "low" if direction is RegimeDirection.LONG else "high"
    observation = ReadGuard(
        _observation(source, 1, adverse=_relative(level, direction, distance)),
        {"bar_index", "timestamp_utc", "open", field},
    )
    result = _state(_observe(book, decision, observation), decision)
    assert observation.reads == ["bar_index", "timestamp_utc", "open", field]
    if distance > 0:
        assert result.stop_execution_state is State.ARMED
        assert result.fill is None
    else:
        assert result.fill.trigger_phase is Phase.INTRABAR
        assert result.fill.base_stop_fill_price == level
        assert result.fill.exact_intrabar_timestamp is None


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("adverse", [None, Decimal("NaN"), Decimal("Infinity")])
def test_gap_fill_does_not_depend_on_unavailable_or_malformed_later_range(direction, adverse):
    decision, stops, _ = _setup(direction)
    book = _after_entry(decision, stops)
    source = _state(book, decision)
    level = source.initial_stop_at_entry.initial_stop_record.initial_stop_price
    observation = _observation(source, 1, opening=_relative(level, direction, -1))
    observation = replace(
        observation, **{"low" if direction is RegimeDirection.LONG else "high": adverse}
    )
    result = _state(_observe(book, decision, observation), decision)
    assert result.fill.trigger_phase is Phase.BAR_OPEN_GAP
    assert result.fill.base_stop_fill_price == observation.open


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("hours", [1, 16, 72])
@pytest.mark.parametrize("gap_fill", [False, True])
def test_sequential_next_bar_survives_large_time_or_session_gap(direction, hours, gap_fill):
    decision, stops, _ = _setup(direction)
    book = _after_entry(decision, stops)
    source = _state(book, decision)
    level = source.initial_stop_at_entry.initial_stop_record.initial_stop_price
    next_time = source.last_observed_bar_timestamp + timedelta(hours=hours)
    opening = _relative(level, direction, -1) if gap_fill else None
    observation = _observation(source, 1, opening=opening, timestamp=next_time)
    after = _observe(book, decision, observation)
    result = _state(after, decision)
    if gap_fill:
        assert result.fill.trigger_phase is Phase.BAR_OPEN_GAP
        assert result.fill.base_stop_fill_price == observation.open
    else:
        assert result.stop_execution_state is State.ARMED
        assert result.last_observed_bar_timestamp == next_time
        next_observation = _observation(result, 2, timestamp=next_time + timedelta(minutes=1))
        assert (
            _state(_observe(after, decision, next_observation), decision).stop_execution_state
            is State.ARMED
        )


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("skip_entry", [False, True])
def test_skipped_index_fails_before_price_or_clock_reads_and_never_synthesizes_fill(
    direction, skip_entry
):
    decision, stops, _ = _setup(direction)
    book = _register(decision, stops) if skip_entry else _after_entry(decision, stops)
    source = _state(book, decision)
    observation = replace(_observation(source), bar_index=source.next_observation_bar_index + 1)
    guarded = ReadGuard(observation, {"bar_index"})
    failed = _observe(book, decision, guarded)
    result = _state(failed, decision)
    assert result.status is Status.FAILED_INCOMPLETE_STOP_OBSERVATION
    assert result.stop_execution_state is State.FAILED_INCOMPLETE_STOP_OBSERVATION
    assert result.fill is None
    assert result.stop_triggered is False
    assert result.last_observed_bar_index == source.last_observed_bar_index
    assert _observe(failed, decision, NoReads()) is failed
    assert _register(decision, stops, failed) is failed


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("phase", ["entry", "no_gap", "gap"])
@pytest.mark.parametrize("field", ["close", "volume", "opposite_extreme", "is_closed"])
def test_forbidden_fields_can_mutate_without_affecting_stop(direction, phase, field):
    decision, stops, _ = _setup(direction)
    book = _register(decision, stops) if phase == "entry" else _after_entry(decision, stops)
    source = _state(book, decision)
    level = source.initial_stop_at_entry.initial_stop_record.initial_stop_price
    observation = _observation(
        source,
        0 if phase == "entry" else 1,
        opening=_relative(level, direction, -1) if phase == "gap" else None,
    )
    baseline = _state(_observe(book, decision, observation), decision)
    actual_field = (
        ("high" if direction is RegimeDirection.LONG else "low")
        if field == "opposite_extreme"
        else field
    )
    mutated = replace(observation, **{actual_field: Decimal("NaN")})
    assert _state(_observe(book, decision, mutated), decision) == baseline


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("value", INVALID_PRICES)
@pytest.mark.parametrize("entry_bar", [False, True])
def test_required_adverse_extreme_is_validated_and_failure_is_terminal(direction, value, entry_bar):
    decision, stops, _ = _setup(direction)
    book = _register(decision, stops) if entry_bar else _after_entry(decision, stops)
    source = _state(book, decision)
    observation = _observation(source, 0 if entry_bar else 1)
    observation = replace(
        observation, **{"low" if direction is RegimeDirection.LONG else "high": value}
    )
    failed = _observe(book, decision, observation)
    result = _state(failed, decision)
    assert result.status is Status.FAILED_INVALID_STOP_OBSERVATION
    assert result.stop_execution_state is State.FAILED_INVALID_STOP_OBSERVATION
    assert result.fill is None
    assert _observe(failed, decision, NoReads()) is failed
    assert _register(decision, stops, failed) is failed


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("value", INVALID_PRICES)
def test_later_open_must_be_exact_finite_and_is_validated_before_extreme(direction, value):
    decision, stops, _ = _setup(direction)
    book = _after_entry(decision, stops)
    observation = replace(_observation(_state(book, decision), 1), open=value)
    guarded = ReadGuard(observation, {"bar_index", "timestamp_utc", "open"})
    result = _state(_observe(book, decision, guarded), decision)
    assert result.status is Status.FAILED_INVALID_STOP_OBSERVATION
    assert result.fill is None


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("entry_bar", [False, True])
def test_adverse_extreme_must_enclose_the_known_open(direction, entry_bar):
    decision, stops, _ = _setup(direction)
    book = _register(decision, stops) if entry_bar else _after_entry(decision, stops)
    source = _state(book, decision)
    opening = source.initial_stop_at_entry.entry_price
    malformed = _relative(opening, direction, 1)
    result = _state(
        _observe(book, decision, _observation(source, 0 if entry_bar else 1, adverse=malformed)),
        decision,
    )
    assert result.status is Status.FAILED_INVALID_STOP_OBSERVATION
    assert result.fill is None


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_equal_adverse_extreme_and_open_is_valid_without_full_ohlc_validation(direction):
    decision, stops, _ = _setup(direction)
    book = _after_entry(decision, stops)
    source = _state(book, decision)
    price = source.initial_stop_at_entry.entry_price
    result = _state(
        _observe(book, decision, _observation(source, 1, opening=price, adverse=price)), decision
    )
    assert result.stop_execution_state is State.ARMED


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("phase", ["entry_breach", "entry_touch", "gap", "later_touch"])
def test_filled_stop_is_terminal_and_idempotent_without_future_reads(direction, phase):
    decision, stops, _ = _setup(
        direction, entry_relation="beyond" if phase == "entry_breach" else "valid"
    )
    book = _register(decision, stops)
    if phase != "entry_breach":
        if phase != "entry_touch":
            book = _observe(book, decision, _observation(_state(book, decision)))
        source = _state(book, decision)
        level = source.initial_stop_at_entry.initial_stop_record.initial_stop_price
        observation = _observation(
            source,
            0 if phase == "entry_touch" else 1,
            opening=_relative(level, direction, -1) if phase == "gap" else None,
            adverse=level,
        )
        book = _observe(book, decision, observation)
    filled = _state(book, decision)
    assert filled.stop_execution_state is State.FILLED_STOP
    for _ in range(3):
        assert _observe(book, decision, NoReads()) is book
        assert _register(decision, stops, book) is book
        assert _state(book, decision).fill is filled.fill


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_future_mutation_has_no_effect_until_that_observation_is_processed(direction):
    decision, stops, _ = _setup(direction)
    book = _register(decision, stops)
    source = _state(book, decision)
    current = _observation(source)
    future = _observation(source, 1)
    baseline = _observe(book, decision, current)
    level = source.initial_stop_at_entry.initial_stop_record.initial_stop_price
    mutated_future = replace(future, open=_relative(level, direction, -1))
    assert _observe(book, decision, current) == baseline
    assert _state(baseline, decision).stop_execution_state is State.ARMED
    assert (
        _state(_observe(baseline, decision, future), decision).stop_execution_state is State.ARMED
    )
    assert (
        _state(_observe(baseline, decision, mutated_future), decision).fill.trigger_phase
        is Phase.BAR_OPEN_GAP
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("processed_bars", [0, 1, 3])
def test_end_of_data_never_creates_a_fill_or_expires_an_armed_stop(direction, processed_bars):
    decision, stops, _ = _setup(direction)
    book = _register(decision, stops)
    for offset in range(processed_bars):
        book = _observe(book, decision, _observation(_state(book, decision), offset))
    result = _state(book, decision)
    assert _observe(book, decision, None) is book
    assert result.stop_execution_state is State.ARMED
    assert result.stop_triggered is False
    assert result.fill is None


@pytest.mark.parametrize("phase", ["entry_breach", "entry_touch", "gap", "later_touch", "armed"])
def test_long_short_mirror_symmetry(phase):
    results = []
    for direction in DIRECTIONS:
        decision, stops, _ = _setup(
            direction, entry_relation="beyond" if phase == "entry_breach" else "valid"
        )
        book = _register(decision, stops)
        if phase != "entry_breach":
            if phase not in {"entry_touch", "armed"}:
                book = _observe(book, decision, _observation(_state(book, decision)))
            source = _state(book, decision)
            level = source.initial_stop_at_entry.initial_stop_record.initial_stop_price
            observation = _observation(
                source,
                0 if phase in {"entry_touch", "armed"} else 1,
                opening=_relative(level, direction, -1) if phase == "gap" else None,
                adverse=None if phase == "armed" else level,
            )
            book = _observe(book, decision, observation)
        results.append(_state(book, decision))
    long, short = results
    assert short.stop_execution_state is long.stop_execution_state
    assert short.status is long.status
    if long.fill is not None:
        assert short.fill.base_stop_fill_price == 20 - long.fill.base_stop_fill_price
        assert short.fill.initial_stop_price == 20 - long.fill.initial_stop_price
        assert short.fill.trigger_phase is long.fill.trigger_phase
        assert short.fill.trigger_bar_index == long.fill.trigger_bar_index
        assert short.fill.trigger_bar_timestamp == long.fill.trigger_bar_timestamp


@pytest.mark.parametrize("families", [(FAMILIES[0],), (FAMILIES[1],), tuple(FAMILIES)])
@pytest.mark.parametrize("second", [False, True])
def test_provenance_is_preserved_and_all_snapshots_remain_immutable(families, second):
    decision, stops, executions = _setup(second=second, families=families)
    book = _register(decision, stops)
    source = _state(book, decision)
    bound = source.initial_stop_at_entry
    level = bound.initial_stop_record.initial_stop_price
    result = _state(_observe(book, decision, _observation(source, adverse=level)), decision)
    record = result.fill
    for name in [
        "source_regime_event_types",
        "source_regime_event_bar_index",
        "source_regime_event_timestamp",
        "source_regime_event_direction",
        "pullback_bar_index",
        "pullback_timestamp",
        "ema_reference",
        "confirmation_bar_index",
        "confirmation_timestamp",
    ]:
        assert getattr(record, name) == getattr(decision.confirmation, name)
    for name in ["initial_stop_price", "structural_extreme", "tick_size", "stop_buffer_ticks"]:
        assert getattr(record, name) == getattr(bound.initial_stop_record, name)
    assert record.entry_bar_index == bound.entry_bar_index
    assert record.entry_bar_timestamp == bound.entry_bar_timestamp
    assert record.entry_price == bound.entry_price
    assert record.stop_state_at_entry is bound.stop_state
    assert record.initial_stop_at_entry is bound
    assert bound.execution is executions.for_confirmation(decision.confirmation).execution
    assert record.order_semantics == "STOP_MARKET"
    assert source.fill is None
    for snapshot in [
        record,
        result,
        book,
        bound,
        bound.initial_stop_record,
        bound.execution,
        decision.confirmation,
    ]:
        for field in fields(snapshot):
            with pytest.raises(FrozenInstanceError):
                setattr(snapshot, field.name, None)


def test_exact_decimal_gap_fill_has_no_rounding_or_cost_adjustment():
    decision, stops, _ = _setup()
    book = _after_entry(decision, stops)
    source = _state(book, decision)
    exact_open = Decimal("8.12345678901234567890123456789")
    with localcontext() as context:
        context.prec = 2
        context.traps[Inexact] = True
        result = _state(
            _observe(book, decision, _observation(source, 1, opening=exact_open)), decision
        )
    assert result.fill.base_stop_fill_price == Fraction(exact_open)
    assert type(result.fill.base_stop_fill_price) is Fraction


@pytest.mark.parametrize("bad_timestamp", [None, "invalid", START, START.replace(tzinfo=None)])
def test_invalid_or_noncausal_clock_fails_closed(bad_timestamp):
    decision, stops, _ = _setup()
    book = _after_entry(decision, stops)
    observation = replace(_observation(_state(book, decision), 1), timestamp_utc=bad_timestamp)
    guarded = ReadGuard(observation, {"bar_index", "timestamp_utc"})
    result = _state(_observe(book, decision, guarded), decision)
    assert result.status is Status.FAILED_INVALID_STOP_OBSERVATION
    assert result.fill is None


@pytest.mark.parametrize("bad_index", [None, True, -1, 36.0])
def test_invalid_index_fails_before_price_reads(bad_index):
    decision, stops, _ = _setup()
    book = _register(decision, stops)
    observation = replace(_observation(_state(book, decision)), bar_index=bad_index)
    result = _state(_observe(book, decision, ReadGuard(observation, {"bar_index"})), decision)
    assert result.status is Status.FAILED_INVALID_STOP_OBSERVATION


def test_repeated_or_out_of_order_active_observation_cannot_rewrite_closed_history():
    decision, stops, _ = _setup()
    book = _after_entry(decision, stops)
    source = _state(book, decision)
    old = _observation(source)
    result = _state(_observe(book, decision, ReadGuard(old, {"bar_index"})), decision)
    assert result.status is Status.FAILED_INVALID_STOP_OBSERVATION
    assert result.fill is None


def test_registration_requires_bound_stop_and_refuses_changed_level_entry_or_confirmation():
    decision, stops, _ = _setup()
    empty = StructuralStopExecutionBookV2()
    unbound = InitialStopBookV2((replace(stops.entries[0], at_entry=None),))
    with pytest.raises(StructuralStopExecutionV2Error, match="bound to its entry"):
        _register(decision, unbound)
    book = _register(decision, stops)
    altered_record = replace(decision.confirmation, macd=Fraction(999))
    with pytest.raises(StructuralStopExecutionV2Error, match="provenance cannot change"):
        book.for_confirmation(altered_record)
    old = stops.entries[0]
    altered_stop = replace(old.initial_stop_record, initial_stop_price=Fraction(9))
    altered_bound = replace(old.at_entry, initial_stop_record=altered_stop)
    altered_stops = InitialStopBookV2(
        (replace(old, initial_stop_record=altered_stop, at_entry=altered_bound),)
    )
    with pytest.raises(StructuralStopExecutionV2Error, match="provenance cannot change"):
        _register(decision, altered_stops, book)
    another_decision, another_stops, _ = _setup(entry_relation="equal")
    with pytest.raises(StructuralStopExecutionV2Error, match="provenance cannot change"):
        _register(another_decision, another_stops, book)
    with pytest.raises(StructuralStopExecutionV2Error, match="registered"):
        empty.for_confirmation(decision.confirmation)


def test_duplicate_book_is_rejected_and_distinct_confirmations_are_independent():
    first, first_stops, _ = _setup()
    book = _register(first, first_stops)
    with pytest.raises(StructuralStopExecutionV2Error, match="duplicate"):
        StructuralStopExecutionBookV2((book.entries[0], book.entries[0]))
    with pytest.raises(StructuralStopExecutionV2Error, match="immutable tuple"):
        StructuralStopExecutionBookV2(list(book.entries))
    second, second_stops, _ = _setup(second=True)
    extended = _register(second, second_stops, book)
    assert len(extended.entries) == 2
    assert _state(extended, first) is book.entries[0]
    assert _state(extended, second).stop_execution_state is State.ARMED
