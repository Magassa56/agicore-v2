"""Synthetic structural stops, guarded closed-window reads and actual V2 fills."""

from __future__ import annotations

from collections.abc import Mapping
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
    STOP_BUFFER,
    STOP_BUFFER_TICKS,
    STOP_KNOWN_AT,
    TICK_SIZE,
    InitialStopBookV2,
    InitialStopV2Error,
    bind_initial_stop_to_entry_v2,
    evaluate_initial_stop_v2,
    register_initial_stop_v2,
)
from agicore.trading.ema_pullback_initial_stop_v2 import InitialStopStateV2 as State
from agicore.trading.ema_pullback_initial_stop_v2 import InitialStopStatusV2 as Status
from agicore.trading.regime_context_v2 import (
    RegimeContextLifetimeState,
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
    10.0,
    "10",
    True,
]


def _timestamp(index):
    return START + timedelta(minutes=index)


def _bar(index, open_=10, high=10, low=10, close=10):
    return EMA20PullbackBarV2(index, _timestamp(index), open_, high, low, close, True)


def _confirmation(direction=RegimeDirection.LONG, *, second=False, families=(FAMILIES[0],)):
    """Real consumption, exact MACD confirmation and immutable source provenance."""
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
    assert pullback.lifetime.context.state is RegimeContextLifetimeState.CONSUMED
    return decision, bars


def _evaluate(decision, bars):
    return evaluate_initial_stop_v2(confirmation=decision, bars_by_index=bars)


def _register(decision, bars, previous=None):
    return register_initial_stop_v2(
        previous=InitialStopBookV2() if previous is None else previous,
        confirmation=decision,
        bars_by_index=bars,
    )


def _executions(decision, price=None, *, fill=True):
    pending = register_entry_execution_v2(previous=EntryExecutionBookV2(), confirmation=decision)
    if not fill:
        return pending
    q = decision.confirmation.confirmation_bar_index
    opening = EntryExecutionOpenV2(q + 1, _timestamp(q + 1), price)
    return execute_entry_open_v2(
        previous=pending, confirmation=decision.confirmation, opening_bar=opening
    )


def _bind(book, decision, executions):
    return bind_initial_stop_to_entry_v2(
        previous=book, confirmation=decision.confirmation, executions=executions
    )


@dataclass(frozen=True)
class StructuralBar:
    bar_index: int
    timestamp_utc: datetime
    high: object
    low: object
    is_closed: object = True


class ReadGuard:
    def __init__(self, bar):
        self.bar = bar
        self.reads = []

    def __getattr__(self, name):
        assert name in {"bar_index", "timestamp_utc", "is_closed", "high", "low"}, name
        self.reads.append(name)
        return getattr(self.bar, name)


class WindowGuard(Mapping):
    def __init__(self, bars, first, last):
        self.bars, self.first, self.last = bars, first, last
        self.reads = []

    def __getitem__(self, index):
        assert self.first <= index <= self.last, index
        self.reads.append(index)
        return self.bars[index]

    def __iter__(self):
        raise AssertionError("window keys must not be inspected")

    def __len__(self):
        raise AssertionError("future dataset length must not be inspected")


class NoReads(Mapping):
    def __getitem__(self, index):
        raise AssertionError(f"immutable stop must not be recalculated: {index}")

    def __iter__(self):
        raise AssertionError("no iteration")

    def __len__(self):
        raise AssertionError("no dataset length")


def test_baseline_constants_are_exact_and_not_optimized():
    assert TICK_SIZE == STOP_BUFFER == Fraction(1, 4)
    assert isinstance(TICK_SIZE, Fraction)
    assert STOP_BUFFER_TICKS == 1
    assert STOP_KNOWN_AT == "Close[q]"
    assert INITIAL_STOP_RECALCULATION == "FORBIDDEN"


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("second", [False, True])
def test_exact_structural_stop_for_both_confirmation_windows(direction, second):
    decision, bars = _confirmation(direction, second=second)
    k, q = decision.confirmation.pullback_bar_index, decision.confirmation.confirmation_bar_index
    lows = [20000, 19998, 19999]
    for offset, index in enumerate(range(k, q + 1)):
        bars[index] = StructuralBar(index, _timestamp(index), 20005, lows[offset])
        if direction is RegimeDirection.SHORT:
            bars[index] = replace(bars[index], high=40000 - lows[offset], low=19995)
    result = _evaluate(decision, bars)
    assert result.status is Status.EVALUATED
    expected = Fraction(79991, 4) if direction is RegimeDirection.LONG else Fraction(80009, 4)
    assert result.initial_stop == expected
    assert result.stop_state is None
    assert result.initial_stop_record.structural_window_first_bar == k
    assert result.initial_stop_record.structural_window_last_bar == q
    assert q - k == (2 if second else 1)


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("extreme_offset", [0, 1, 2])
def test_each_bar_can_supply_the_structural_extreme(direction, extreme_offset):
    decision, bars = _confirmation(direction, second=True)
    k = decision.confirmation.pullback_bar_index
    for offset in range(3):
        low, high = (8, 15) if offset == extreme_offset else (10, 13)
        if direction is RegimeDirection.SHORT:
            low, high = 20 - high, 20 - low
        bars[k + offset] = StructuralBar(k + offset, _timestamp(k + offset), high, low)
    result = _evaluate(decision, bars)
    assert result.initial_stop_record.structural_extreme == (
        8 if direction is RegimeDirection.LONG else 12
    )
    assert result.initial_stop == (
        Fraction(31, 4) if direction is RegimeDirection.LONG else Fraction(49, 4)
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_exact_fraction_prices_and_buffer_ignore_decimal_context(direction):
    decision, bars = _confirmation(direction)
    k, q = decision.confirmation.pullback_bar_index, decision.confirmation.confirmation_bar_index
    extreme = Fraction(1, 3) if direction is RegimeDirection.LONG else Fraction(2, 3)
    bars[k] = StructuralBar(k, _timestamp(k), Fraction(2, 3), Fraction(1, 3))
    bars[q] = StructuralBar(
        q, _timestamp(q), Decimal("0.6000000000000000000000000001"), Decimal("0.4")
    )
    with localcontext() as context:
        context.prec = 2
        context.traps[Inexact] = True
        result = _evaluate(decision, bars)
    assert result.initial_stop == extreme + (
        -STOP_BUFFER if direction is RegimeDirection.LONG else STOP_BUFFER
    )
    assert type(result.initial_stop) is Fraction


def test_decimal_extreme_is_converted_exactly_without_tick_rounding():
    decision, bars = _confirmation()
    k = decision.confirmation.pullback_bar_index
    decimal_low = Decimal("9.12345678901234567890123456789")
    bars[k] = replace(bars[k], low=decimal_low)
    result = _evaluate(decision, bars)
    assert result.initial_stop == Fraction(decimal_low) - Fraction(1, 4)
    assert result.initial_stop.denominator > 4


@pytest.mark.parametrize("missing_offset", [0, 1, 2])
def test_missing_required_bar_including_intermediate_is_incomplete(missing_offset):
    decision, bars = _confirmation(second=True)
    del bars[decision.confirmation.pullback_bar_index + missing_offset]
    result = _evaluate(decision, bars)
    assert result.status is Status.INCOMPLETE_STRUCTURAL_STOP_WINDOW
    assert result.initial_stop is result.initial_stop_record is result.at_entry is None


@pytest.mark.parametrize("field", ["low", "high"])
@pytest.mark.parametrize("value", INVALID_PRICES)
@pytest.mark.parametrize("offset", [0, 1, 2])
def test_every_required_high_and_low_must_be_exact_and_finite(field, value, offset):
    decision, bars = _confirmation(second=True)
    index = decision.confirmation.pullback_bar_index + offset
    bars[index] = replace(bars[index], **{field: value})
    result = _evaluate(decision, bars)
    assert result.status is Status.INVALID_STRUCTURAL_STOP_INPUT
    assert result.initial_stop is None


@pytest.mark.parametrize("offset", [0, 1, 2])
def test_high_below_low_is_invalid_on_each_required_bar(offset):
    decision, bars = _confirmation(second=True)
    index = decision.confirmation.pullback_bar_index + offset
    bars[index] = replace(bars[index], high=8, low=9)
    assert _evaluate(decision, bars).status is Status.INVALID_STRUCTURAL_STOP_INPUT


def test_zero_range_and_wide_or_negative_structural_levels_add_no_filter():
    decision, bars = _confirmation()
    k = decision.confirmation.pullback_bar_index
    for low, high in [(0, 0), (-1000000, 1000000), (10, 10)]:
        candidate = dict(bars)
        candidate[k] = StructuralBar(k, _timestamp(k), high, low)
        result = _evaluate(decision, candidate)
        assert result.status is Status.EVALUATED
        assert result.initial_stop == Fraction(min(low, 10)) - STOP_BUFFER


@pytest.mark.parametrize("second", [False, True])
@pytest.mark.parametrize("direction", DIRECTIONS)
def test_only_closed_high_low_in_exact_window_are_read(direction, second):
    decision, bars = _confirmation(direction, second=second)
    k, q = decision.confirmation.pullback_bar_index, decision.confirmation.confirmation_bar_index
    guarded = {index: ReadGuard(bars[index]) for index in range(k, q + 1)}
    window = WindowGuard(guarded, k, q)
    result = _evaluate(decision, window)
    assert result.status is Status.EVALUATED
    assert window.reads == list(range(k, q + 1))
    for guard in guarded.values():
        assert {"high", "low", "is_closed", "bar_index", "timestamp_utc"} == set(guard.reads)


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize(
    "side",
    ["before_k", "after_q", "entry_open", "entry_high", "entry_low", "entry_close", "entry_volume"],
)
def test_mutations_outside_window_cannot_change_stop(direction, side):
    decision, bars = _confirmation(direction)
    baseline = _evaluate(decision, bars)
    k, q = decision.confirmation.pullback_bar_index, decision.confirmation.confirmation_bar_index
    mutated = dict(bars)
    index = k - 1 if side == "before_k" else q + 1
    # No attributes are readable, covering arbitrary OHLCV/Open mutation.
    mutated[index] = NoReads()
    if side == "after_q":
        mutated[q + 2] = NoReads()
    assert _evaluate(decision, mutated) == baseline


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("relation", ["valid", "equal", "beyond"])
def test_binding_preserves_entry_and_classifies_exact_relation(direction, relation):
    decision, bars = _confirmation(direction)
    known = _register(decision, bars)
    original = known.for_confirmation(decision.confirmation)
    stop = original.initial_stop
    offset = {"valid": 1, "equal": 0, "beyond": -1}[relation]
    entry = stop + offset if direction is RegimeDirection.LONG else stop - offset
    executions = _executions(decision, entry)
    fill = executions.for_confirmation(decision.confirmation).execution
    bound = _bind(known, decision, executions).for_confirmation(decision.confirmation)
    assert bound.initial_stop_record is original.initial_stop_record
    assert bound.initial_stop == stop
    assert bound.stop_state is (
        State.ARMED if relation == "valid" else State.BREACHED_AT_ENTRY_OPEN
    )
    assert bound.at_entry.entry_price == entry
    assert bound.at_entry.entry_bar_index == decision.confirmation.confirmation_bar_index + 1
    assert bound.at_entry.execution is fill
    assert (
        executions.for_confirmation(decision.confirmation).execution_state
        is EntryExecutionStateV2.FILLED
    )
    assert original.at_entry is None


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_open_changes_only_entry_binding_not_known_stop(direction):
    decision, bars = _confirmation(direction)
    known = _register(decision, bars)
    original = known.for_confirmation(decision.confirmation)
    first = _bind(known, decision, _executions(decision, Fraction(9))).for_confirmation(
        decision.confirmation
    )
    second = _bind(known, decision, _executions(decision, Fraction(12))).for_confirmation(
        decision.confirmation
    )
    assert first.initial_stop_record is second.initial_stop_record is original.initial_stop_record
    assert first.at_entry.entry_price == 9
    assert second.at_entry.entry_price == 12
    assert first.stop_state is not second.stop_state


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_entry_relation_has_no_artificial_stop_distance_limit(direction):
    decision, bars = _confirmation(direction)
    known = _register(decision, bars)
    price = Fraction(1000000000) if direction is RegimeDirection.LONG else Fraction(1, 1000000000)
    result = _bind(known, decision, _executions(decision, price)).for_confirmation(
        decision.confirmation
    )
    assert result.stop_state is State.ARMED
    assert result.at_entry.entry_price == price


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("outcome", ["armed", "breached", "invalid", "incomplete"])
def test_repeated_registration_never_recalculates_or_replaces_stop(direction, outcome):
    decision, bars = _confirmation(direction, second=True)
    k = decision.confirmation.pullback_bar_index
    if outcome == "invalid":
        bars[k] = replace(bars[k], low=None)
    elif outcome == "incomplete":
        del bars[k + 1]
    book = _register(decision, bars)
    if outcome in {"armed", "breached"}:
        stop = book.for_confirmation(decision.confirmation).initial_stop
        offset = 1 if outcome == "armed" else -1
        price = stop + offset if direction is RegimeDirection.LONG else stop - offset
        executions = _executions(decision, price)
        book = _bind(book, decision, executions)
        assert _bind(book, decision, executions) is book
    snapshot = book.for_confirmation(decision.confirmation)
    assert _register(replace(decision), NoReads(), book) is book
    assert book.for_confirmation(replace(decision.confirmation)) is snapshot


@pytest.mark.parametrize("execution_outcome", ["pending", "missing", "invalid", "gap"])
def test_no_arm_without_a_fill_and_no_synthetic_action(execution_outcome):
    decision, bars = _confirmation()
    book = _register(decision, bars)
    executions = _executions(decision, fill=False)
    q = decision.confirmation.confirmation_bar_index
    if execution_outcome != "pending":
        opening = (
            None
            if execution_outcome == "missing"
            else EntryExecutionOpenV2(q + 1, _timestamp(q + 1), None)
        )
        if execution_outcome == "gap":
            opening = EntryExecutionOpenV2(q + 1, _timestamp(q + 2), 13)
        executions = execute_entry_open_v2(
            previous=executions, confirmation=decision.confirmation, opening_bar=opening
        )
    assert _bind(book, decision, executions) is book
    assert book.for_confirmation(decision.confirmation).stop_state is None


@pytest.mark.parametrize("failure", ["invalid", "incomplete"])
def test_unavailable_stop_does_not_change_or_cancel_existing_fill(failure):
    decision, bars = _confirmation(second=True)
    k = decision.confirmation.pullback_bar_index
    if failure == "invalid":
        bars[k] = replace(bars[k], high=Decimal("Infinity"))
    else:
        del bars[k + 1]
    book = _register(decision, bars)
    executions = _executions(decision, 13)
    assert _bind(book, decision, executions) is book
    assert book.for_confirmation(decision.confirmation).initial_stop is None
    assert (
        executions.for_confirmation(decision.confirmation).execution_state
        is EntryExecutionStateV2.FILLED
    )


@pytest.mark.parametrize("second", [False, True])
@pytest.mark.parametrize("families", [(FAMILIES[0],), (FAMILIES[1],), tuple(FAMILIES)])
def test_full_provenance_known_at_confirmation_and_preserved_at_fill(second, families):
    decision, bars = _confirmation(second=second, families=families)
    source = decision.confirmation
    known = _register(decision, bars)
    stop = known.for_confirmation(source).initial_stop_record
    for name in [
        "source_regime_event_types",
        "source_regime_event_bar_index",
        "source_regime_event_timestamp",
        "source_regime_event_direction",
        "pullback_bar_index",
        "pullback_timestamp",
        "confirmation_bar_index",
        "confirmation_timestamp",
        "ema_reference",
    ]:
        assert getattr(stop, name) == getattr(source, name)
    assert stop.confirmation is source
    assert stop.stop_known_at_bar_index == source.confirmation_bar_index
    assert stop.stop_known_at_timestamp == source.confirmation_timestamp
    assert stop.structural_window_first_bar == source.pullback_bar_index
    assert stop.structural_window_last_bar == source.confirmation_bar_index
    assert stop.tick_size == Fraction(1, 4)
    assert stop.stop_buffer_ticks == 1
    executions = _executions(decision, 13)
    bound = _bind(known, decision, executions).for_confirmation(source)
    assert bound.at_entry.initial_stop_record is stop
    assert bound.at_entry.entry_bar_timestamp == _timestamp(source.confirmation_bar_index + 1)
    assert bound.at_entry.execution.confirmation is source
    for record in [stop, bound, bound.at_entry, bound.at_entry.execution, source]:
        for field in fields(record):
            with pytest.raises(FrozenInstanceError):
                setattr(record, field.name, None)


@pytest.mark.parametrize("second", [False, True])
@pytest.mark.parametrize("entry", [Fraction(9), Fraction(39, 4), Fraction(13)])
def test_long_short_mirror_symmetry(second, entry):
    long_decision, long_bars = _confirmation(second=second)
    short_decision, short_bars = _confirmation(RegimeDirection.SHORT, second=second)
    long_known, short_known = (
        _register(long_decision, long_bars),
        _register(short_decision, short_bars),
    )
    long = _bind(long_known, long_decision, _executions(long_decision, entry)).for_confirmation(
        long_decision.confirmation
    )
    short = _bind(
        short_known, short_decision, _executions(short_decision, 20 - entry)
    ).for_confirmation(short_decision.confirmation)
    assert short.initial_stop == 20 - long.initial_stop
    assert (
        short.initial_stop_record.structural_extreme
        == 20 - long.initial_stop_record.structural_extreme
    )
    assert short.stop_state is long.stop_state


@pytest.mark.parametrize("field", ["macd", "ema_reference", "source_regime_event_types"])
def test_same_identity_cannot_change_registered_provenance(field):
    decision, bars = _confirmation()
    book = _register(decision, bars)
    value = (FAMILIES[1],) if field == "source_regime_event_types" else Fraction(999)
    altered = replace(decision.confirmation, **{field: value})
    with pytest.raises(InitialStopV2Error, match="provenance cannot change"):
        book.for_confirmation(altered)
    if field == "macd":
        with pytest.raises(InitialStopV2Error, match="provenance cannot change"):
            _register(replace(decision, confirmation=altered), NoReads(), book)


def test_bound_stop_never_replaces_fill_or_disarms_from_an_old_pending_snapshot():
    decision, bars = _confirmation()
    known = _register(decision, bars)
    first_execution = _executions(decision, 13)
    bound = _bind(known, decision, first_execution)
    assert _bind(bound, decision, _executions(decision, fill=False)) is bound
    with pytest.raises(InitialStopV2Error, match="cannot replace"):
        _bind(bound, decision, _executions(decision, 14))


@pytest.mark.parametrize("offset", [0, 1, 2])
def test_unclosed_required_bar_cannot_determine_a_stop(offset):
    decision, bars = _confirmation(second=True)
    index = decision.confirmation.pullback_bar_index + offset
    bars[index] = replace(bars[index], is_closed=False)
    assert _evaluate(decision, bars).status is Status.INVALID_STRUCTURAL_STOP_INPUT


@pytest.mark.parametrize("field", ["bar_index", "timestamp_utc"])
def test_inconsistent_structural_metadata_is_rejected(field):
    decision, bars = _confirmation(second=True)
    index = decision.confirmation.pullback_bar_index + 1
    value = index + 1 if field == "bar_index" else _timestamp(index - 1)
    bars[index] = replace(bars[index], **{field: value})
    with pytest.raises(InitialStopV2Error, match="metadata"):
        _evaluate(decision, bars)


def test_unqualified_or_unknown_sources_and_duplicate_book_are_rejected():
    decision, bars = _confirmation()
    with pytest.raises(InitialStopV2Error, match="qualified closed confirmation"):
        _evaluate(replace(decision, confirmation=None), bars)
    book = _register(decision, bars)
    other, _ = _confirmation(second=True)
    with pytest.raises(InitialStopV2Error, match="registered"):
        book.for_confirmation(other.confirmation)
    with pytest.raises(InitialStopV2Error, match="duplicate"):
        InitialStopBookV2((book.entries[0], book.entries[0]))
    with pytest.raises(InitialStopV2Error, match="immutable tuple"):
        InitialStopBookV2(list(book.entries))


def test_distinct_confirmations_keep_independent_immutable_stops():
    first, first_bars = _confirmation()
    second, second_bars = _confirmation(second=True)
    before = _register(first, first_bars)
    after = _register(second, second_bars, before)
    assert len(before.entries) == 1
    assert len(after.entries) == 2
    assert after.for_confirmation(first.confirmation) is before.entries[0]
    assert after.for_confirmation(second.confirmation).stop_state is None
