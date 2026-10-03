"""Synthetic exact-EMA/pullback tests; no market data or performance replay."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal, Inexact, localcontext
from fractions import Fraction

import pytest

from agicore.trading.ema20_pullback_v2 import (
    ALPHA,
    EMA_PERIOD,
    EMA_RESET_AT_SESSION,
    EMA20PullbackBarV2,
    EMA20PullbackV2Error,
    EMA20StatusV2,
    advance_ema20_pullback_v2,
    evaluate_ema20_pullback_v2,
    evaluate_ema20_v2,
)
from agicore.trading.ema20_pullback_v2 import (
    EMA20PullbackStatusV2 as Status,
)
from agicore.trading.regime_context_v2 import (
    RegimeContextLifetimeState as State,
)
from agicore.trading.regime_context_v2 import (
    RegimeContextV2Error,
    RegimeDirection,
    RegimeEvent,
    RegimeEventContextV2,
    RegimeEventType,
    advance_regime_context_v2,
    finish_regime_context_v2,
)

START = datetime(2026, 10, 3, 12, tzinfo=UTC)
DIRECTIONS = list(RegimeDirection)
FAMILIES = list(RegimeEventType)


def _timestamp(index):
    return START + timedelta(minutes=index)


def _price(value):
    return Decimal(value) if isinstance(value, str) else value


def _bar(index=20, open_=12, high=14, low=10, close=11, timestamp=None):
    return EMA20PullbackBarV2(
        index,
        _timestamp(index) if timestamp is None else timestamp,
        _price(open_),
        _price(high),
        _price(low),
        _price(close),
        True,
    )


def _flat(index, close):
    return _bar(index, close, close, close, close)


def _history(last=20, previous_close=12):
    bars = {i: _flat(i, 10) for i in range(min(last + 1, 20))}
    bars[0] = _flat(0, Fraction(20) - Fraction(_price(previous_close)))
    if last >= 19:
        bars[19] = _flat(19, previous_close)
    for i in range(20, last + 1):
        bars[i] = _bar(i)
    return bars


def _mirror(bar):
    def reflected(value):
        return Fraction(20) - Fraction(value)

    return replace(
        bar,
        open=reflected(bar.open),
        high=reflected(bar.low),
        low=reflected(bar.high),
        close=reflected(bar.close),
    )


def _side(bars, direction):
    return bars if direction is RegimeDirection.LONG else {i: _mirror(b) for i, b in bars.items()}


def _event(index, direction=RegimeDirection.LONG, family=FAMILIES[0], timestamp=None):
    return RegimeEvent(
        family, direction, index, _timestamp(index) if timestamp is None else timestamp
    )


def _active(direction=RegimeDirection.LONG, e=19, families=(FAMILIES[0],)):
    events = {f: _event(e, direction, f) for f in families}
    return advance_regime_context_v2(
        previous=None,
        closed_bar_index=e,
        closed_bar_timestamp=_timestamp(e),
        source_bar_closed=True,
        directional_impulse_event=events.get(FAMILIES[0]),
        reversal_transition_event=events.get(FAMILIES[1]),
    )


def _evaluate(bars, direction=RegimeDirection.LONG, k=20, context=None):
    return evaluate_ema20_pullback_v2(
        pullback_candidate_bar_index=k,
        bars_by_index=bars,
        context=_active(direction).context if context is None else context,
    )


def _advance(previous, bars, k=20, events=(), timestamp=None, end=False):
    by_family = {event.event_type: event for event in events}
    return advance_ema20_pullback_v2(
        previous=previous,
        closed_bar_index=k,
        closed_bar_timestamp=_timestamp(k) if timestamp is None else timestamp,
        source_bar_closed=True,
        bars_by_index=bars,
        directional_impulse_event=by_family.get(FAMILIES[0]),
        reversal_transition_event=by_family.get(FAMILIES[1]),
        end_of_data=end,
    )


class ClosedPrefix(Mapping):
    """Fail if an evaluator scans keys or accesses a future observation."""

    def __init__(self, bars, last):
        self.bars = bars
        self.last = last
        self.reads = []

    def __getitem__(self, index):
        assert index <= self.last, "future bar must not be read"
        self.reads.append(index)
        return self.bars[index]

    def __iter__(self):
        pytest.fail("EMA/pullback must not enumerate possibly future observations")

    def __len__(self):
        raise AssertionError("EMA/pullback must not inspect future collection length")


def test_exact_baseline_seed_after_twenty_closed_closes() -> None:
    bars = {i: _flat(i, Decimal(f"{i + 1}.125")) for i in range(20)}
    before = evaluate_ema20_v2(through_bar_index=18, bars_by_index=bars)
    with localcontext() as arithmetic:
        arithmetic.prec = 2
        arithmetic.traps[Inexact] = True
        seeded = evaluate_ema20_v2(through_bar_index=19, bars_by_index=bars)
    assert EMA_PERIOD == 20
    assert ALPHA == Fraction(2, 21)
    assert EMA_RESET_AT_SESSION is False
    assert before.status is EMA20StatusV2.INSUFFICIENT_EMA_WARMUP
    assert before.ema20 is None
    assert seeded.status is EMA20StatusV2.EVALUATED
    assert seeded.ema20 == Fraction(85, 8)
    assert seeded.last_close == Fraction(161, 8)
    assert seeded.known_at_timestamp == _timestamp(19)


@pytest.mark.parametrize("k", [1, 5, 18, 19])
def test_fewer_than_twenty_prior_closes_has_insufficient_ema_warmup(k) -> None:
    result = _evaluate(_history(k), k=k, context=_active(e=k - 1).context)
    assert result.status is Status.INSUFFICIENT_EMA_WARMUP
    assert result.pullback_qualified is False
    assert result.ema_reference is None


def _recurrence_history():
    bars = {i: _flat(i, 0) for i in range(19)}
    bars[19] = _flat(19, 21)
    bars[20] = _flat(20, 0)
    bars[21] = _flat(21, 21)
    bars[22] = _flat(22, Decimal("0.1"))
    return bars


@pytest.mark.parametrize(
    ("index", "expected"),
    [
        (19, Fraction(21, 20)),
        (20, Fraction(19, 20)),
        (21, Fraction(1201, 420)),
        (22, Fraction(22903, 8820)),
    ],
)
def test_exact_recurrence_has_hand_calculated_rational_values(index, expected) -> None:
    guarded = ClosedPrefix(_recurrence_history(), index)
    with localcontext() as arithmetic:
        arithmetic.prec = 2
        arithmetic.traps[Inexact] = True
        result = evaluate_ema20_v2(through_bar_index=index, bars_by_index=guarded)
    assert result.status is EMA20StatusV2.EVALUATED
    assert result.ema20 == expected
    assert guarded.reads == list(range(index + 1))


def test_ema_uses_only_closes_and_continues_across_day_and_session_gaps() -> None:
    original = _recurrence_history()
    bars = {}
    for index, bar in original.items():
        timestamp = bar.timestamp_utc + (timedelta(days=2) if index >= 20 else timedelta(0))
        bars[index] = replace(bar, open=None, high=None, low=None, timestamp_utc=timestamp)
    result = evaluate_ema20_v2(through_bar_index=22, bars_by_index=bars)
    assert result.ema20 == Fraction(22903, 8820)
    assert result.known_at_timestamp == bars[22].timestamp_utc
    assert len(bars) == 23  # No invented bars in the two-day clock gap.


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize(
    ("open_", "high", "low", "close", "previous_close", "expected"),
    [
        (12, 14, 10, 11, 12, True),  # Exact touch; LONG candle is bearish.
        (12, 14, 9, 11, 12, True),  # Penetration and recovery.
        (12, 14, "10.0000000000000000000000000000000000000001", 11, 12, False),
        (12, 14, 10, 10, 12, False),  # Candidate equality fails.
        (12, 14, 8, 9, 12, False),  # Closes on wrong side.
        (12, 14, 10, 11, 10, False),  # Previous equality fails.
        (12, 14, 10, 11, 9, False),  # Previous close on wrong side.
        (9, 14, 8, 11, 12, False),  # Open on wrong side.
        ("9.9999999999999999999999999999999999999999", 14, 8, 11, 12, False),
        (10, 14, 10, 11, 12, True),  # Open equality allowed.
        (12, 14, 10, 12, 12, True),  # Doji can satisfy EMA geometry.
        (11, 14, 10, 12, 12, True),  # Bullish candle also allowed.
        (12, 14, 10, "10.0000000000000000000000000000000000000001", 12, True),
        (12, 14, "9.9999999999999999999999999999999999999999", 11, 12, True),
    ],
)
def test_long_short_exact_geometry_frontiers_and_no_candle_color_requirement(
    direction, open_, high, low, close, previous_close, expected
) -> None:
    bars = _history(previous_close=previous_close)
    bars[20] = _bar(open_=open_, high=high, low=low, close=close)
    bars = _side(bars, direction)
    with localcontext() as arithmetic:
        arithmetic.prec = 2
        arithmetic.traps[Inexact] = True
        result = _evaluate(bars, direction)
    assert result.status is Status.EVALUATED
    assert result.pullback_qualified is expected
    assert result.ema_reference == Fraction(10)


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize(
    ("low", "close", "expected"),
    [
        ("2.8595238095238095238095238095", 3, True),
        ("2.8595238095238095238095238096", 3, False),
        (2, "2.8595238095238095238095238095", False),
        (2, "2.8595238095238095238095238096", True),
    ],
)
def test_nonterminating_ema_is_never_rounded_before_touch_or_close_comparison(
    direction, low, close, expected
) -> None:
    bars = _recurrence_history()
    bars[22] = _bar(22, open_=4, high=5, low=low, close=close)
    with localcontext() as arithmetic:
        arithmetic.prec = 2
        arithmetic.traps[Inexact] = True
        result = _evaluate(
            _side(bars, direction), direction, k=22, context=_active(direction, e=21).context
        )
    assert result.status is Status.EVALUATED
    assert result.pullback_qualified is expected
    assert result.ema_reference == (
        Fraction(1201, 420)
        if direction is RegimeDirection.LONG
        else Fraction(20) - Fraction(1201, 420)
    )


@pytest.mark.parametrize("field", ["open", "high", "low"])
@pytest.mark.parametrize("invalid", [None, Decimal("NaN"), Decimal("Infinity"), 10.0])
def test_missing_nonfinite_or_binary_float_ohl_fields_are_invalid_ohlc(field, invalid) -> None:
    bars = _history()
    bars[20] = replace(bars[20], **{field: invalid})
    result = _evaluate(bars)
    assert result.status is Status.INVALID_OHLC
    assert result.pullback_qualified is False


@pytest.mark.parametrize(
    "candidate",
    [_bar(high=10), _bar(low=12), _bar(open_=15), _bar(open_=9), _bar(high=9, low=15)],
)
def test_malformed_candidate_ohlc_is_invalid(candidate) -> None:
    bars = _history()
    bars[20] = candidate
    result = _evaluate(bars)
    assert result.status is Status.INVALID_OHLC
    assert result.pullback_qualified is False


@pytest.mark.parametrize("index", [0, 19, 20])
@pytest.mark.parametrize(
    "invalid",
    [None, Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity"), Decimal("-Infinity"), 11.0, True],
)
def test_missing_or_nonfinite_required_close_is_invalid_ema_input(index, invalid) -> None:
    bars = _history()
    bars[index] = replace(bars[index], close=invalid)
    result = _evaluate(bars)
    assert result.status is Status.INVALID_EMA_INPUT
    assert result.pullback_qualified is False


@pytest.mark.parametrize("index", [0, 19, 20])
def test_missing_or_unclosed_ema_observation_is_not_skipped_or_reseeded(index) -> None:
    bars = _recurrence_history()
    del bars[index]
    result = evaluate_ema20_v2(through_bar_index=21, bars_by_index=bars)
    assert result.status is EMA20StatusV2.INVALID_EMA_INPUT
    assert result.ema20 is None
    bars = _recurrence_history()
    bars[index] = replace(bars[index], is_closed=False)
    assert (
        evaluate_ema20_v2(through_bar_index=21, bars_by_index=bars).status
        is EMA20StatusV2.INVALID_EMA_INPUT
    )


def test_candidate_close_mutation_changes_decision_but_not_prior_ema_reference() -> None:
    bars = _history()
    before = _evaluate(bars)
    bars[20] = replace(bars[20], close=10)
    after = _evaluate(bars)
    bars[20] = replace(bars[20], close=None)
    missing = _evaluate(bars)
    assert before.ema_reference == after.ema_reference == missing.ema_reference == Fraction(10)
    assert before.pullback_qualified is True
    assert after.pullback_qualified is False
    assert missing.status is Status.INVALID_EMA_INPUT
    assert (
        evaluate_ema20_v2(through_bar_index=20, bars_by_index=_history()).ema20
        != before.ema_reference
    )


def test_future_mutation_has_no_effect_and_no_future_bar_is_read() -> None:
    bars = _history(24)
    guarded = ClosedPrefix(bars, 20)
    first = _evaluate(guarded)
    bars[21] = object()
    bars[24] = object()
    assert _evaluate(guarded) == first
    assert max(guarded.reads) == 20
    assert (
        evaluate_ema20_v2(through_bar_index=19, bars_by_index=ClosedPrefix(bars, 19)).ema20
        == first.ema_reference
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("families", [(FAMILIES[0],), (FAMILIES[1],), tuple(FAMILIES)])
def test_formal_pullback_consumes_once_and_keeps_all_source_and_exact_reference_metadata(
    direction, families
) -> None:
    bars = _side(_history(22), direction)
    active = _active(direction, families=families)
    evaluated = _advance(active, bars)
    result = evaluated.pullback
    consumed = evaluated.lifetime.context
    assert result.status is Status.EVALUATED and result.pullback_qualified is True
    assert consumed.state is State.CONSUMED
    assert result.context_source_event_types == consumed.source_event_types == families
    assert result.context_direction is consumed.source_event_direction is direction
    assert result.context_event_bar_index == consumed.source_event_bar_index == 19
    assert result.context_event_timestamp == consumed.source_event_timestamp == _timestamp(19)
    assert result.pullback_bar_index == consumed.pullback_bar_index == 20
    assert result.pullback_timestamp == consumed.pullback_timestamp == _timestamp(20)
    assert result.ema_reference == consumed.ema_reference == Fraction(10)
    assert active.context.state is State.ACTIVE and active.context.ema_reference is None
    later = _advance(evaluated.lifetime, ClosedPrefix({}, -1), k=21)
    assert later.pullback is None
    assert later.lifetime.context == consumed
    # There is no input that reactivates consumption after failed entry confirmation.
    assert finish_regime_context_v2(later.lifetime).context == consumed


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_first_qualified_pullback_after_a_failed_touch_consumes_without_refresh(direction) -> None:
    bars = _history(22)
    bars[20] = _bar(low="10.01")
    bars = _side(bars, direction)
    first = _advance(_active(direction), bars)
    assert first.pullback.pullback_qualified is False
    assert first.lifetime.state is State.ACTIVE
    second = _advance(first.lifetime, bars, k=21, events=(_event(21, direction, FAMILIES[1]),))
    assert second.pullback.pullback_qualified is True
    assert second.lifetime.state is State.CONSUMED
    assert second.lifetime.context.source_event_bar_index == 19
    assert second.lifetime.context.source_event_types == (FAMILIES[0],)
    assert second.lifetime.context.pullback_bar_index == 21
    assert second.lifetime.context.ema_reference == (
        Fraction(212, 21) if direction is RegimeDirection.LONG else Fraction(208, 21)
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_event_bar_itself_cannot_qualify_or_call_formal_pullback(direction) -> None:
    bars = _side(_history(), direction)
    pure = _evaluate(bars, direction, context=_active(direction, e=20).context)
    assert pure.status is Status.INELIGIBLE_CONTEXT and pure.pullback_qualified is False
    advanced = _advance(None, ClosedPrefix({}, -1), events=(_event(20, direction),))
    assert advanced.pullback is None
    assert advanced.lifetime.state is State.ACTIVE
    assert advanced.lifetime.context.first_eligible_pullback_bar == 21


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("age", [1, 8])
def test_first_and_eighth_eligible_bar_can_consume(direction, age) -> None:
    k = 19 + age
    result = _advance(_active(direction), _side(_history(k), direction), k=k)
    assert result.lifetime.state is State.CONSUMED
    assert result.pullback.pullback_qualified is True


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_exact_eight_minute_gap_is_eligible_without_synthetic_bars(direction) -> None:
    timestamp = _timestamp(19) + timedelta(minutes=8)
    bars = _history()
    bars[20] = replace(bars[20], timestamp_utc=timestamp)
    result = _advance(_active(direction), _side(bars, direction), timestamp=timestamp)
    assert result.lifetime.state is State.CONSUMED
    assert result.pullback.ema_reference == Fraction(10)
    assert result.lifetime.context.pullback_timestamp == timestamp
    assert len(bars) == 21


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("expiry", ["age", "time"])
def test_outside_bar_age_or_elapsed_window_cannot_evaluate_or_consume(direction, expiry) -> None:
    k = 28 if expiry == "age" else 20
    timestamp = _timestamp(19) + timedelta(minutes=8, microseconds=0 if expiry == "age" else 1)
    bars = _history(k)
    bars[k] = replace(bars[k], timestamp_utc=timestamp)
    pure = _evaluate(_side(bars, direction), direction, k=k)
    assert pure.status is Status.INELIGIBLE_CONTEXT and pure.pullback_qualified is False
    result = _advance(_active(direction), ClosedPrefix({}, -1), k=k, timestamp=timestamp)
    assert result.pullback is None
    assert result.lifetime.state is (
        State.EXPIRED_MAX_AGE if expiry == "age" else State.EXPIRED_ELAPSED_TIME
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("ambiguous", [False, True])
def test_opposite_or_ambiguous_event_wins_over_same_bar_qualified_old_pullback(
    direction, ambiguous
) -> None:
    bars = _side(_history(), direction)
    assert _evaluate(bars, direction).pullback_qualified is True
    opposite = RegimeDirection.SHORT if direction is RegimeDirection.LONG else RegimeDirection.LONG
    events = (_event(20, opposite),)
    if ambiguous:
        events += (_event(20, direction, FAMILIES[1]),)
    result = _advance(_active(direction), ClosedPrefix({}, -1), events=events)
    assert result.pullback is None
    assert result.lifetime.retired_contexts[0].state is (
        State.INVALIDATED_AMBIGUOUS_EVENT if ambiguous else State.INVALIDATED_OPPOSITE_EVENT
    )
    if ambiguous:
        assert result.lifetime.state is State.INVALIDATED_AMBIGUOUS_EVENT
    else:
        assert result.lifetime.state is State.ACTIVE
        assert result.lifetime.context.source_event_bar_index == 20
        assert result.lifetime.context.source_event_direction is opposite
        assert result.lifetime.context.ema_reference is None


def test_pullback_cannot_create_context_and_terminal_context_cannot_qualify() -> None:
    result = _advance(None, ClosedPrefix({}, -1))
    assert result.lifetime.state is State.INACTIVE
    assert result.pullback is None
    pure = _evaluate(_history(), context=RegimeEventContextV2())
    assert pure.status is Status.INELIGIBLE_CONTEXT
    expired = replace(_active().context, state=State.EXPIRED_END_OF_DATA)
    assert _evaluate(_history(), context=expired).pullback_qualified is False


def test_new_event_after_consumption_keeps_retired_exact_reference_and_creates_fresh_source() -> (
    None
):
    consumed = _advance(_active(), _history()).lifetime
    fresh = _advance(consumed, ClosedPrefix({}, -1), k=21, events=(_event(21),)).lifetime
    assert fresh.state is State.ACTIVE and fresh.context.source_event_bar_index == 21
    assert fresh.context.ema_reference is None
    assert fresh.retired_contexts == (consumed.context,)
    assert fresh.retired_contexts[0].state is State.CONSUMED
    assert fresh.retired_contexts[0].ema_reference == Fraction(10)


def test_long_short_mirror_symmetry_of_full_decision_and_consumption() -> None:
    bars = _recurrence_history()
    bars[22] = _bar(22, open_=4, high=5, low=2, close=3)
    long = _advance(_active(RegimeDirection.LONG, e=21), bars, k=22)
    short = _advance(_active(RegimeDirection.SHORT, e=21), _side(bars, RegimeDirection.SHORT), k=22)
    assert long.lifetime.state is short.lifetime.state is State.CONSUMED
    assert long.pullback.pullback_qualified is short.pullback.pullback_qualified is True
    assert long.pullback.ema_reference + short.pullback.ema_reference == 20
    assert long.lifetime.context.pullback_bar_index == short.lifetime.context.pullback_bar_index
    assert long.lifetime.context.pullback_timestamp == short.lifetime.context.pullback_timestamp


def test_end_of_data_preserves_consumption_reference_without_synthetic_action() -> None:
    result = _advance(_active(), _history(), end=True)
    assert result.lifetime.state is State.CONSUMED
    assert result.lifetime.context.ema_reference == Fraction(10)
    assert result.lifetime.end_of_data is True
    assert finish_regime_context_v2(result.lifetime) == result.lifetime


@pytest.mark.parametrize("bad_index", [-1, True, 20.0])
def test_noninteger_or_negative_requested_index_is_rejected(bad_index) -> None:
    with pytest.raises(EMA20PullbackV2Error, match="nonnegative integer"):
        evaluate_ema20_v2(through_bar_index=bad_index, bars_by_index={})
    with pytest.raises(EMA20PullbackV2Error, match="nonnegative integer"):
        _evaluate({}, k=bad_index)


def test_unclosed_or_misindexed_candidate_and_noncausal_history_are_rejected() -> None:
    bars = _history()
    bars[20] = replace(bars[20], is_closed=False)
    with pytest.raises(EMA20PullbackV2Error, match="indexed closed candidate"):
        _evaluate(bars)
    bars = _history()
    bars[20] = replace(bars[20], bar_index=21)
    with pytest.raises(EMA20PullbackV2Error, match="indexed closed candidate"):
        _evaluate(bars)
    bars = _history()
    bars[19] = replace(bars[19], timestamp_utc=_timestamp(21))
    with pytest.raises(EMA20PullbackV2Error, match="causal and increasing"):
        _evaluate(bars)
    bars = _history()
    bars[10] = replace(bars[10], bar_index=11)
    with pytest.raises(EMA20PullbackV2Error, match="requested index"):
        _evaluate(bars)


def test_candidate_timestamp_must_match_lifetime_clock() -> None:
    bars = _history()
    bars[20] = replace(bars[20], timestamp_utc=_timestamp(20) + timedelta(seconds=1))
    guarded = ClosedPrefix(bars, 20)
    with pytest.raises(EMA20PullbackV2Error, match="timestamp must match"):
        _advance(_active(), guarded)
    assert guarded.reads == [20]  # Reject metadata before reading price history.


def test_exact_reference_metadata_belongs_only_to_consumed_context() -> None:
    consumed = _advance(_active(), _history()).lifetime.context
    with pytest.raises(RegimeContextV2Error, match="exact Fraction"):
        replace(consumed, ema_reference=Decimal(10))
    with pytest.raises(RegimeContextV2Error, match="only consumed"):
        replace(_active().context, ema_reference=Fraction(10))
    with pytest.raises(RegimeContextV2Error, match="inactive context"):
        RegimeEventContextV2(ema_reference=Fraction(10))
    with pytest.raises(AttributeError):
        consumed.ema_reference = Fraction(11)
