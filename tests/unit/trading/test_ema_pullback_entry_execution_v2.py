"""Synthetic offline execution tests, with guarded opening-only market reads."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, dataclass, fields, replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal, Inexact, localcontext
from fractions import Fraction

import pytest

from agicore.trading.ema20_pullback_v2 import (
    EMA20PullbackBarV2,
    advance_ema20_pullback_v2,
)
from agicore.trading.ema_pullback_entry_confirmation_v2 import (
    advance_entry_confirmation_momentum_v2,
    begin_entry_confirmation_momentum_v2,
)
from agicore.trading.ema_pullback_entry_execution_v2 import (
    ENTRY_DECISION_MOMENT,
    EXECUTION_POINT,
    MAX_EXECUTION_AGE_CLOSED_BARS,
    MAX_EXECUTION_ELAPSED_TIME,
    NO_FILL_ON_CONFIRMATION_BAR,
    NO_MAX_ENTRY_GAP_FILTER,
    ORDER_SEMANTICS,
    EntryExecutionActionV2,
    EntryExecutionBookV2,
    EntryExecutionOpenV2,
    EntryExecutionV2Error,
    execute_entry_open_v2,
    register_entry_execution_v2,
)
from agicore.trading.ema_pullback_entry_execution_v2 import (
    EntryExecutionStateV2 as State,
)
from agicore.trading.ema_pullback_entry_execution_v2 import (
    EntryExecutionStatusV2 as Status,
)
from agicore.trading.regime_context_v2 import (
    RegimeContextLifetimeState,
    RegimeDirection,
    RegimeEvent,
    RegimeEventType,
    advance_regime_context_v2,
)

START = datetime(2026, 10, 4, 8, tzinfo=UTC)
OPEN_TIMESTAMP = START + timedelta(minutes=35)
DIRECTIONS = list(RegimeDirection)
FAMILIES = list(RegimeEventType)


def _timestamp(index):
    return START + timedelta(minutes=index)


def _bar(index, open_=10, high=10, low=10, close=10):
    return EMA20PullbackBarV2(index, _timestamp(index), open_, high, low, close, True)


def _confirmation(direction=RegimeDirection.LONG, families=(FAMILIES[0],), second=False):
    bars = {i: _bar(i) for i in range(32)}
    bars[32] = _bar(32, 12, 12, 12, 12)
    bars[33] = _bar(33, 12, 15, 10, 11)
    bars[34] = _bar(34, 14 if second else 11, 14, 10, 13)
    bars[35] = _bar(35, 13, 15, 12, 14)
    if direction is RegimeDirection.SHORT:
        bars = {
            i: replace(
                bar,
                open=Fraction(20) - bar.open,
                high=Fraction(20) - bar.low,
                low=Fraction(20) - bar.high,
                close=Fraction(20) - bar.close,
            )
            for i, bar in bars.items()
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
    return decision


def _pending(decision):
    return register_entry_execution_v2(previous=EntryExecutionBookV2(), confirmation=decision)


def _open(decision, price=Decimal("13.125"), index=None, timestamp=None):
    q = decision.confirmation.confirmation_bar_index
    return EntryExecutionOpenV2(
        q + 1 if index is None else index,
        _timestamp(q + 1) if timestamp is None else timestamp,
        price,
    )


def _execute(book, decision, opening):
    return execute_entry_open_v2(
        previous=book, confirmation=decision.confirmation, opening_bar=opening
    )


@dataclass(frozen=True)
class CompleteSyntheticBar:
    """A full OHLCV observation already resident in offline memory."""

    bar_index: int = 35
    timestamp_utc: datetime = OPEN_TIMESTAMP
    open: object = Decimal("13.125")
    high: object = 100
    low: object = 1
    close: object = 20
    volume: object = 1000
    is_closed: object = True


class ReadGuard:
    """Raise on any access beyond fields explicitly available at the Open."""

    def __init__(self, bar=None, allowed=("bar_index", "timestamp_utc", "open")):
        self.bar, self.allowed, self.reads = bar, allowed, []

    def __getattr__(self, name):
        assert name in self.allowed, f"forbidden market read: {name}"
        self.reads.append(name)
        return getattr(self.bar, name)


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_registration_at_confirmation_close_never_fills_same_bar(direction) -> None:
    decision = _confirmation(direction)
    book = _pending(decision)
    pending = book.for_confirmation(decision.confirmation)
    assert pending.execution_state is State.PENDING_NEXT_BAR_OPEN
    assert pending.status is Status.NOT_EVALUATED
    assert pending.execution is None
    assert pending.expected_execution_bar_index == 35
    same_bar = ReadGuard(
        _open(decision, index=34, timestamp=_timestamp(34)),
        allowed=("bar_index", "timestamp_utc"),
    )
    assert _execute(book, decision, same_bar) is book
    assert same_bar.reads == ["bar_index", "timestamp_utc"]
    assert MAX_EXECUTION_AGE_CLOSED_BARS == 1
    assert MAX_EXECUTION_ELAPSED_TIME == timedelta(minutes=1)
    assert ENTRY_DECISION_MOMENT == "Close[q]"
    assert EXECUTION_POINT == "Open[q+1]"
    assert ORDER_SEMANTICS == "MARKET"
    assert NO_FILL_ON_CONFIRMATION_BAR is True


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("second", [False, True])
def test_valid_next_open_fills_exactly_once_for_either_confirmation_candidate(direction, second):
    decision = _confirmation(direction, second=second)
    opening = _open(decision)
    guarded = ReadGuard(opening)
    book = _execute(_pending(decision), decision, guarded)
    entry = book.for_confirmation(decision.confirmation)
    assert entry.execution_state is State.FILLED
    assert entry.status is Status.EVALUATED
    assert entry.execution.execution_price_before_costs == Fraction(105, 8)
    assert entry.execution.execution_side is direction
    assert entry.execution.execution_action is (
        EntryExecutionActionV2.BUY
        if direction is RegimeDirection.LONG
        else EntryExecutionActionV2.SELL_SHORT
    )
    assert entry.execution.execution_bar_index == decision.confirmation.confirmation_bar_index + 1
    assert entry.execution.execution_bar_timestamp == opening.timestamp_utc
    assert guarded.reads == ["bar_index", "timestamp_utc", "open"]
    repeated = _execute(book, decision, ReadGuard(allowed=()))
    assert repeated is book
    assert repeated.for_confirmation(decision.confirmation).execution is entry.execution
    assert len(repeated.entries) == 1


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("field", ["high", "low", "close", "volume", "is_closed"])
@pytest.mark.parametrize("value", [None, Decimal("NaN"), 10**50])
def test_other_complete_ohlcv_fields_are_never_read_and_mutations_have_no_effect(
    direction, field, value
):
    decision = _confirmation(direction)
    pending = _pending(decision)
    initial = CompleteSyntheticBar()
    expected = _execute(pending, decision, ReadGuard(initial))
    changed = replace(initial, **{field: value})
    guarded = ReadGuard(changed)
    actual = _execute(pending, decision, guarded)
    assert actual == expected
    assert guarded.reads == ["bar_index", "timestamp_utc", "open"]


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_open_mutation_changes_only_the_base_fill_price(direction) -> None:
    decision = _confirmation(direction)
    pending = _pending(decision)
    first = _execute(pending, decision, _open(decision, price=Decimal("0.123456789012345678901")))
    second = _execute(pending, decision, _open(decision, price=Fraction(5000, 3)))
    a = first.for_confirmation(decision.confirmation).execution
    b = second.for_confirmation(decision.confirmation).execution
    assert a.execution_price_before_costs == Fraction(Decimal("0.123456789012345678901"))
    assert b.execution_price_before_costs == Fraction(5000, 3)
    assert replace(a, execution_price_before_costs=b.execution_price_before_costs) == b
    assert a.confirmation is b.confirmation is decision.confirmation


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize(
    "price", [Decimal("0.000000000000000000000001"), 10**50, Fraction(1000, 3)]
)
def test_large_valid_price_gaps_never_add_a_cancellation_filter(direction, price) -> None:
    decision = _confirmation(direction)
    result = _execute(_pending(decision), decision, _open(decision, price=price))
    entry = result.for_confirmation(decision.confirmation)
    assert entry.execution_state is State.FILLED
    assert entry.execution.execution_price_before_costs == Fraction(price)
    assert NO_MAX_ENTRY_GAP_FILTER is True


def test_exact_decimal_open_is_unchanged_by_ambient_rounding() -> None:
    decision = _confirmation()
    with localcontext() as arithmetic:
        arithmetic.prec = 2
        arithmetic.traps[Inexact] = True
        result = _execute(
            _pending(decision), decision, _open(decision, price=Decimal("13.1234567890123456789"))
        )
    assert result.for_confirmation(
        decision.confirmation
    ).execution.execution_price_before_costs == Fraction(Decimal("13.1234567890123456789"))


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_missing_next_bar_and_end_of_data_expire_without_synthetic_fill(direction) -> None:
    decision = _confirmation(direction)
    result = _execute(_pending(decision), decision, None)
    entry = result.for_confirmation(decision.confirmation)
    assert entry.execution_state is State.EXPIRED_NO_EXECUTION
    assert entry.execution is None
    assert _execute(result, decision, ReadGuard(allowed=())) is result


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("index", [36, 37, 10**6])
def test_missing_next_bar_followed_by_later_bar_cannot_carry_execution(direction, index) -> None:
    decision = _confirmation(direction)
    guarded = ReadGuard(_open(decision, index=index), allowed=("bar_index",))
    result = _execute(_pending(decision), decision, guarded)
    assert (
        result.for_confirmation(decision.confirmation).execution_state is State.EXPIRED_NO_EXECUTION
    )
    assert result.for_confirmation(decision.confirmation).execution is None
    assert guarded.reads == ["bar_index"]


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize(
    "delta", [timedelta(microseconds=1), timedelta(seconds=30), timedelta(minutes=1)]
)
def test_positive_elapsed_time_up_to_exact_one_minute_is_inclusive(direction, delta) -> None:
    decision = _confirmation(direction)
    timestamp = decision.confirmation.confirmation_timestamp + delta
    result = _execute(_pending(decision), decision, _open(decision, timestamp=timestamp))
    assert result.for_confirmation(decision.confirmation).execution_state is State.FILLED


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize(
    "delta", [timedelta(minutes=1, microseconds=1), timedelta(hours=2), timedelta(days=1)]
)
def test_elapsed_gap_expires_before_any_open_price_read(direction, delta) -> None:
    decision = _confirmation(direction)
    timestamp = decision.confirmation.confirmation_timestamp + delta
    guarded = ReadGuard(
        _open(decision, timestamp=timestamp), allowed=("bar_index", "timestamp_utc")
    )
    result = _execute(_pending(decision), decision, guarded)
    entry = result.for_confirmation(decision.confirmation)
    assert entry.execution_state is State.EXPIRED_EXECUTION_GAP
    assert entry.execution is None
    assert guarded.reads == ["bar_index", "timestamp_utc"]


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize(
    "timestamp", [_timestamp(33), _timestamp(34), None, _timestamp(35).replace(tzinfo=None)]
)
def test_noncausal_or_invalid_timestamp_fails_closed_without_open_read(
    direction, timestamp
) -> None:
    decision = _confirmation(direction)
    opening = replace(_open(decision), timestamp_utc=timestamp)
    guarded = ReadGuard(opening, allowed=("bar_index", "timestamp_utc"))
    result = _execute(_pending(decision), decision, guarded)
    entry = result.for_confirmation(decision.confirmation)
    assert entry.status is Status.INVALID_EXECUTION_CLOCK
    assert entry.execution_state is State.FAILED_INVALID_EXECUTION_CLOCK
    assert entry.execution is None
    assert guarded.reads == ["bar_index", "timestamp_utc"]


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize(
    "price",
    [
        None,
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
        0,
        -1,
        Fraction(-1, 3),
        True,
        13.125,
        "13.125",
    ],
)
def test_missing_nonfinite_nonpositive_or_inexact_open_cannot_be_substituted(direction, price):
    decision = _confirmation(direction)
    result = _execute(_pending(decision), decision, _open(decision, price=price))
    entry = result.for_confirmation(decision.confirmation)
    assert entry.status is Status.INVALID_EXECUTION_INPUT
    assert entry.execution_state is State.FAILED_INVALID_EXECUTION_INPUT
    assert entry.execution is None


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("outcome", ["fill", "missing", "gap", "invalid_open", "invalid_clock"])
def test_terminal_outcomes_and_reregistration_are_idempotent_without_new_market_reads(
    direction, outcome
):
    decision = _confirmation(direction)
    pending = _pending(decision)
    opening = {
        "fill": _open(decision),
        "missing": None,
        "gap": _open(decision, timestamp=_timestamp(36)),
        "invalid_open": _open(decision, price=0),
        "invalid_clock": _open(decision, timestamp=_timestamp(34)),
    }[outcome]
    resolved = _execute(pending, decision, opening)
    assert (
        resolved.for_confirmation(decision.confirmation).execution_state
        is not State.PENDING_NEXT_BAR_OPEN
    )
    for _ in range(3):
        guarded = ReadGuard(allowed=())
        assert _execute(resolved, decision, guarded) is resolved
        assert guarded.reads == []
        assert register_entry_execution_v2(previous=resolved, confirmation=decision) is resolved
        cloned = replace(decision, confirmation=replace(decision.confirmation))
        assert register_entry_execution_v2(previous=resolved, confirmation=cloned) is resolved
    assert len(resolved.entries) == 1


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_future_q_plus_two_mutations_have_no_effect_on_canonical_fill(direction) -> None:
    decision = _confirmation(direction)
    q = decision.confirmation.confirmation_bar_index
    result = _execute(_pending(decision), decision, _open(decision))
    initial = result.for_confirmation(decision.confirmation).execution
    for later in (
        CompleteSyntheticBar(q + 2, _timestamp(q + 2), open=None, close=Decimal("NaN")),
        CompleteSyntheticBar(q + 2, _timestamp(q - 1), open=10**50, volume=None),
    ):
        guarded = ReadGuard(later, allowed=())
        assert _execute(result, decision, guarded) is result
        assert guarded.reads == []
        assert result.for_confirmation(decision.confirmation).execution is initial


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("families", [(FAMILIES[0],), (FAMILIES[1],), tuple(FAMILIES)])
def test_provenance_preserved_exactly_and_all_records_remain_immutable(direction, families) -> None:
    decision = _confirmation(direction, families)
    pending = _pending(decision)
    book = _execute(pending, decision, _open(decision))
    record = book.for_confirmation(decision.confirmation).execution
    source = decision.confirmation
    for name in (
        "source_regime_event_types",
        "source_regime_event_bar_index",
        "source_regime_event_timestamp",
        "source_regime_event_direction",
        "pullback_bar_index",
        "pullback_timestamp",
        "ema_reference",
        "confirmation_bar_index",
        "confirmation_timestamp",
    ):
        assert getattr(record, name) == getattr(source, name)
    assert record.confirmation is source
    assert record.source_regime_event_types == families
    assert record.order_semantics == "MARKET"
    assert decision.opportunity.consumed_context.state is RegimeContextLifetimeState.CONSUMED
    assert pending.for_confirmation(source).execution is None  # Prior snapshot untouched.
    names = {field.name for field in fields(record)}
    assert not names.intersection(
        {"quantity", "slippage", "commission", "spread", "stop", "take_profit"}
    )
    with pytest.raises(FrozenInstanceError):
        record.execution_price_before_costs = Fraction(0)
    with pytest.raises(FrozenInstanceError):
        source.confirmation_bar_index = 0
    with pytest.raises(FrozenInstanceError):
        book.entries = ()


def test_long_short_execution_symmetry() -> None:
    long = _confirmation(RegimeDirection.LONG)
    short = _confirmation(RegimeDirection.SHORT)
    a = (
        _execute(_pending(long), long, _open(long, price=13))
        .for_confirmation(long.confirmation)
        .execution
    )
    b = (
        _execute(_pending(short), short, _open(short, price=7))
        .for_confirmation(short.confirmation)
        .execution
    )
    assert a.execution_price_before_costs + b.execution_price_before_costs == 20
    assert a.execution_bar_index == b.execution_bar_index
    assert a.execution_bar_timestamp == b.execution_bar_timestamp
    assert a.confirmation_timestamp == b.confirmation_timestamp
    assert a.execution_side is RegimeDirection.LONG
    assert b.execution_side is RegimeDirection.SHORT
    assert a.execution_action is EntryExecutionActionV2.BUY
    assert b.execution_action is EntryExecutionActionV2.SELL_SHORT


def test_multiple_distinct_confirmations_have_independent_states_without_a_position_policy() -> (
    None
):
    long = _confirmation(RegimeDirection.LONG)
    short = _confirmation(RegimeDirection.SHORT)
    book = register_entry_execution_v2(previous=_pending(long), confirmation=short)
    filled = _execute(book, long, _open(long))
    assert filled.for_confirmation(long.confirmation).execution_state is State.FILLED
    assert (
        filled.for_confirmation(short.confirmation).execution_state is State.PENDING_NEXT_BAR_OPEN
    )
    resolved = _execute(filled, short, None)
    assert resolved.for_confirmation(long.confirmation) is filled.for_confirmation(
        long.confirmation
    )
    assert (
        resolved.for_confirmation(short.confirmation).execution_state is State.EXPIRED_NO_EXECUTION
    )


def test_only_qualified_confirmation_can_be_registered_and_provenance_cannot_change() -> None:
    decision = _confirmation()
    empty = EntryExecutionBookV2()
    with pytest.raises(EntryExecutionV2Error, match="qualified closed confirmation"):
        register_entry_execution_v2(
            previous=empty, confirmation=replace(decision, confirmation=None)
        )
    altered = replace(
        decision, confirmation=replace(decision.confirmation, ema_reference=Fraction(0))
    )
    with pytest.raises(EntryExecutionV2Error, match="match its consumed source"):
        register_entry_execution_v2(previous=empty, confirmation=altered)
    pending = _pending(decision)
    altered = replace(decision, confirmation=replace(decision.confirmation, signal=Fraction(0)))
    with pytest.raises(EntryExecutionV2Error, match="provenance cannot change"):
        register_entry_execution_v2(previous=pending, confirmation=altered)
    with pytest.raises(EntryExecutionV2Error, match="registered at its qualified close"):
        _execute(empty, decision, ReadGuard(allowed=()))
    with pytest.raises(EntryExecutionV2Error, match="must not duplicate"):
        EntryExecutionBookV2((pending.entries[0], pending.entries[0]))


@pytest.mark.parametrize("index", [-1, None, True, 35.0, "35"])
def test_invalid_index_metadata_cannot_trigger_a_price_read(index) -> None:
    decision = _confirmation()
    guarded = ReadGuard(
        _open(decision, index=index)
        if index is not None
        else replace(_open(decision), bar_index=None),
        allowed=("bar_index",),
    )
    result = _execute(_pending(decision), decision, guarded)
    entry = result.for_confirmation(decision.confirmation)
    assert entry.execution_state is State.FAILED_INVALID_EXECUTION_INPUT
    assert entry.status is Status.INVALID_EXECUTION_INPUT
    assert entry.execution is None
    assert guarded.reads == ["bar_index"]
