"""Synthetic confirmation/MACD tests; no market dataset or performance replay."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal, Inexact, localcontext
from fractions import Fraction

import pytest

from agicore.trading.ema20_pullback_v2 import (
    EMA20PullbackBarV2,
    advance_ema20_pullback_v2,
)
from agicore.trading.ema_pullback_entry_confirmation_v2 import (
    MACD_FAST,
    MACD_SESSION_RESET,
    MACD_SIGNAL,
    MACD_SLOW,
    MACD_WARMUP_CLOSED_BARS,
    MAX_CONFIRMATION_AGE_CLOSED_BARS,
    MAX_CONFIRMATION_ELAPSED_TIME,
    NO_MACD_CROSS_REQUIRED,
    NO_MACD_MAGNITUDE_THRESHOLD,
    EntryConfirmationV2Error,
    MACDEvaluationV2,
    MACDStatusV2,
    advance_entry_confirmation_momentum_v2,
    begin_entry_confirmation_momentum_v2,
    evaluate_macd_momentum_v2,
    evaluate_macd_v2,
)
from agicore.trading.ema_pullback_entry_confirmation_v2 import (
    EntryConfirmationStateV2 as State,
)
from agicore.trading.ema_pullback_entry_confirmation_v2 import (
    EntryConfirmationStatusV2 as Status,
)
from agicore.trading.regime_context_v2 import (
    RegimeContextLifetimeState,
    RegimeDirection,
    RegimeEvent,
    RegimeEventType,
    advance_regime_context_v2,
)

START = datetime(2026, 10, 3, 12, tzinfo=UTC)
DIRECTIONS = list(RegimeDirection)
FAMILIES = list(RegimeEventType)


def _timestamp(index):
    return START + timedelta(minutes=index)


def _bar(index, open_=10, high=10, low=10, close=10, timestamp=None):
    return EMA20PullbackBarV2(
        index,
        _timestamp(index) if timestamp is None else timestamp,
        open_,
        high,
        low,
        close,
        True,
    )


def _mirror(bar):
    def reflected(value):
        return None if value is None else Fraction(20) - Fraction(value)

    return replace(
        bar,
        open=reflected(bar.open),
        high=reflected(bar.low),
        low=reflected(bar.high),
        close=reflected(bar.close),
    )


def _history(k=33):
    bars = {i: _bar(i) for i in range(k - 1)}
    bars[k - 1] = _bar(k - 1, 12, 12, 12, 12)
    bars[k] = _bar(k, 12, 15, 10, 11)  # Bearish LONG pullback is permitted.
    bars[k + 1] = _bar(k + 1, 11, 14, 10, 13)
    bars[k + 2] = _bar(k + 2, 13, 15, 12, 14)
    bars[k + 3] = _bar(k + 3, 14, 17, 13, 16)
    return bars


def _start(bars=None, k=33, direction=RegimeDirection.LONG, families=(FAMILIES[0],)):
    bars = _history(k) if bars is None else bars
    events = {f: RegimeEvent(f, direction, k - 1, bars[k - 1].timestamp_utc) for f in families}
    active = advance_regime_context_v2(
        previous=None,
        closed_bar_index=k - 1,
        closed_bar_timestamp=bars[k - 1].timestamp_utc,
        source_bar_closed=True,
        directional_impulse_event=events.get(FAMILIES[0]),
        reversal_transition_event=events.get(FAMILIES[1]),
    )
    pullback = advance_ema20_pullback_v2(
        previous=active,
        closed_bar_index=k,
        closed_bar_timestamp=bars[k].timestamp_utc,
        source_bar_closed=True,
        bars_by_index=ClosedPrefix(bars, k),
    )
    assert pullback.pullback.pullback_qualified is True
    assert pullback.lifetime.context.state is RegimeContextLifetimeState.CONSUMED
    pending = begin_entry_confirmation_momentum_v2(pullback=pullback, pullback_bar=bars[k])
    return pending, pullback


def _setup(direction=RegimeDirection.LONG, k=33, families=(FAMILIES[0],), bars=None):
    bars = _history(k) if bars is None else bars
    if direction is RegimeDirection.SHORT:
        bars = {i: _mirror(bar) for i, bar in bars.items()}
    pending, pullback = _start(bars, k, direction, families)
    return bars, pending, pullback


def _advance(previous, bars, q, timestamp=None, closed=True):
    return advance_entry_confirmation_momentum_v2(
        previous=previous,
        closed_bar_index=q,
        closed_bar_timestamp=_timestamp(q) if timestamp is None else timestamp,
        source_bar_closed=closed,
        bars_by_index=bars,
    )


class ClosedPrefix(Mapping):
    """Reject future reads, key enumeration and inspection of future lengths."""

    def __init__(self, bars, last):
        self.bars, self.last, self.reads = bars, last, []

    def __getitem__(self, index):
        assert index <= self.last, "future observation must not be read"
        self.reads.append(index)
        return self.bars[index]

    def __iter__(self):
        pytest.fail("confirmation/MACD must not enumerate possibly future bars")

    def __len__(self):
        raise AssertionError("confirmation/MACD must not inspect future collection length")


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_baseline_starts_awaiting_with_consumed_context_and_no_self_confirmation(direction) -> None:
    _, pending, pullback = _setup(direction)
    assert MAX_CONFIRMATION_AGE_CLOSED_BARS == 2
    assert MAX_CONFIRMATION_ELAPSED_TIME == timedelta(minutes=2)
    assert pending.state is State.AWAITING_CONFIRMATION
    assert pending.status is Status.NOT_EVALUATED
    assert pending.entry_confirmation is False
    assert pending.confirmation is None
    assert pending.opportunity.consumed_context is pullback.lifetime.context
    assert pending.opportunity.first_confirmation_bar == 34
    assert pending.opportunity.last_confirmation_bar == 35
    guarded = ClosedPrefix({}, -1)
    repeated = _advance(pending, guarded, 33)
    assert repeated is pending
    assert guarded.reads == []


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("families", [(FAMILIES[0],), (FAMILIES[1],), tuple(FAMILIES)])
def test_first_valid_candidate_wins_and_preserves_full_source_metadata(direction, families) -> None:
    bars, pending, pullback = _setup(direction, families=families)
    guarded = ClosedPrefix(bars, 34)
    result = _advance(pending, guarded, 34)
    assert result.state is State.CONFIRMED
    assert result.status is Status.EVALUATED
    assert result.entry_confirmation is True
    assert result.candidate.price_qualified is True
    assert result.candidate.momentum_qualified is True
    record = result.confirmation
    context = pullback.lifetime.context
    assert record.source_regime_event_types == families
    assert record.source_regime_event_direction is direction
    assert record.source_regime_event_bar_index == 32
    assert record.source_regime_event_timestamp == _timestamp(32)
    assert record.pullback_bar_index == 33
    assert record.pullback_timestamp == _timestamp(33)
    assert record.ema_reference == context.ema_reference
    assert record.confirmation_bar_index == 34
    assert record.confirmation_timestamp == _timestamp(34)
    macd = evaluate_macd_v2(through_bar_index=34, bars_by_index=bars)
    assert (
        record.macd,
        record.signal,
        record.histogram,
        record.previous_macd,
        record.previous_histogram,
    ) == (macd.macd, macd.signal, macd.histogram, macd.previous_macd, macd.previous_histogram)
    assert all(
        isinstance(value, Fraction)
        for value in (
            record.ema_reference,
            record.macd,
            record.signal,
            record.histogram,
            record.previous_macd,
            record.previous_histogram,
        )
    )
    assert max(guarded.reads) == 34
    unread = ClosedPrefix({}, -1)
    assert _advance(result, unread, 35) is result
    assert unread.reads == []
    assert result.opportunity.consumed_context is context
    assert context.state is RegimeContextLifetimeState.CONSUMED


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_first_failure_then_second_valid_candidate_confirms(direction) -> None:
    bars = _history()
    bars[34] = replace(bars[34], open=14)  # Wrong confirmation color.
    bars, pending, pullback = _setup(direction, bars=bars)
    first = _advance(pending, ClosedPrefix(bars, 34), 34)
    assert first.state is State.AWAITING_CONFIRMATION
    assert first.entry_confirmation is False
    assert first.candidate.price_qualified is False
    assert first.candidate.momentum_qualified is True
    second = _advance(first, ClosedPrefix(bars, 35), 35)
    assert second.state is State.CONFIRMED
    assert second.confirmation.confirmation_bar_index == 35
    assert second.opportunity.consumed_context is pullback.lifetime.context


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_both_failures_expire_and_later_valid_bar_cannot_resurrect(direction) -> None:
    bars = _history()
    bars[34] = replace(bars[34], open=14)
    bars[35] = replace(bars[35], open=15)
    bars, pending, pullback = _setup(direction, bars=bars)
    first = _advance(pending, bars, 34)
    second = _advance(first, bars, 35)
    assert second.state is State.EXPIRED_NO_ENTRY_CONFIRMATION
    assert second.status is Status.EVALUATED
    assert second.candidate.confirmation_bar_index == 35  # Evaluated before expiry.
    assert second.entry_confirmation is False
    assert second.confirmation is None
    unread = ClosedPrefix({}, -1)
    assert _advance(second, unread, 36) is second
    assert unread.reads == []
    context = pullback.lifetime.context
    assert second.opportunity.consumed_context is context
    assert context.state is RegimeContextLifetimeState.CONSUMED
    assert (
        bars[36].close > bars[36].open
        if direction is RegimeDirection.LONG
        else (bars[36].close < bars[36].open)
    )
    assert (
        evaluate_macd_momentum_v2(
            direction=direction,
            macd=evaluate_macd_v2(through_bar_index=36, bars_by_index=bars),
        )
        is True
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_exact_two_minutes_first_candidate_is_eligible(direction) -> None:
    bars, pending, _ = _setup(direction)
    timestamp = _timestamp(33) + timedelta(minutes=2)
    bars[34] = replace(bars[34], timestamp_utc=timestamp)
    result = _advance(pending, ClosedPrefix(bars, 34), 34, timestamp)
    assert result.state is State.CONFIRMED
    assert result.confirmation.confirmation_timestamp == timestamp


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("extra", [timedelta(microseconds=1), timedelta(minutes=50)])
def test_elapsed_time_expiry_precedes_all_price_and_macd_reads(direction, extra) -> None:
    _, pending, pullback = _setup(direction)
    unread = ClosedPrefix({}, -1)
    result = _advance(pending, unread, 34, _timestamp(33) + timedelta(minutes=2) + extra)
    assert result.state is State.EXPIRED_CONFIRMATION_ELAPSED_TIME
    assert result.status is Status.NOT_EVALUATED
    assert result.candidate is None
    assert result.entry_confirmation is False
    assert unread.reads == []
    assert result.opportunity.consumed_context is pullback.lifetime.context


def test_bar_age_expiry_cannot_evaluate_third_candidate_even_inside_elapsed_limit() -> None:
    _, pending, _ = _setup()
    unread = ClosedPrefix({}, -1)
    result = _advance(pending, unread, 36, _timestamp(33) + timedelta(minutes=2))
    assert result.state is State.EXPIRED_NO_ENTRY_CONFIRMATION
    assert result.entry_confirmation is False
    assert unread.reads == []


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize(
    ("open_", "close", "qualified"),
    [
        (11, 13, True),
        (11, 12, False),  # Exact equality at the pullback body edge.
        (11, Fraction(12) + Fraction(1, 10**40), True),
        (14, 13, False),  # Wrong candle color.
        (13, 13, False),  # Doji.
        (11, Fraction(12) - Fraction(1, 10**40), False),
    ],
)
def test_strict_price_boundaries_and_directional_color(direction, open_, close, qualified) -> None:
    bars = _history()
    bars[34] = replace(bars[34], open=open_, close=close)
    bars, pending, _ = _setup(direction, bars=bars)
    result = _advance(pending, ClosedPrefix(bars, 34), 34)
    assert result.candidate.price_qualified is qualified
    assert result.entry_confirmation is qualified


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_no_pullback_extreme_break_and_no_confirmation_high_low_requirement(direction) -> None:
    bars, pending, _ = _setup(direction)
    if direction is RegimeDirection.LONG:
        assert bars[34].close < bars[33].high
    else:
        assert bars[34].close > bars[33].low
    bars[34] = replace(bars[34], high=None, low=None)
    result = _advance(pending, bars, 34)
    assert result.entry_confirmation is True


def _momentum(direction=RegimeDirection.LONG, **changes):
    values = {
        "macd": Fraction(2),
        "signal": Fraction(0),
        "histogram": Fraction(2),
        "previous_macd": Fraction(1),
        "previous_histogram": Fraction(1),
    }
    values.update(changes)
    if direction is RegimeDirection.SHORT:
        values = {key: -value if value is not None else None for key, value in values.items()}
    return MACDEvaluationV2(MACDStatusV2.EVALUATED, 34, **values)


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({}, True),
        ({"previous_histogram": Fraction(3)}, False),
        ({"previous_histogram": Fraction(2)}, False),
        ({"previous_macd": Fraction(3)}, False),
        ({"previous_macd": Fraction(2)}, False),
        ({"signal": Fraction(2), "histogram": Fraction(0)}, False),
        ({"histogram": Fraction(0)}, False),
        ({"signal": Fraction(3), "histogram": Fraction(-1)}, False),
        ({"previous_macd": None}, False),
        ({"previous_histogram": None}, False),
    ],
)
def test_each_strict_momentum_condition_is_required_in_both_directions(
    direction, changes, expected
):
    # Isolated predicate snapshots retain the explicit line-direction check,
    # including the synthetic strengthening-histogram/falling-line case.
    macd = _momentum(direction, **changes)
    assert evaluate_macd_momentum_v2(direction=direction, macd=macd) is expected


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_already_correct_side_of_signal_needs_no_new_crossover(direction) -> None:
    bars, pending, _ = _setup(direction)
    before = evaluate_macd_v2(through_bar_index=33, bars_by_index=bars)
    if direction is RegimeDirection.LONG:
        assert before.macd > before.signal
    else:
        assert before.macd < before.signal
    result = _advance(pending, bars, 34)
    assert result.entry_confirmation is True
    assert NO_MACD_CROSS_REQUIRED is True


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_exact_tiny_positive_momentum_has_no_magnitude_threshold(direction) -> None:
    bars = _history()
    if direction is RegimeDirection.SHORT:
        bars = {i: _mirror(bar) for i, bar in bars.items()}
    scale = Fraction(Decimal("1e-100"))
    bars = {
        i: replace(
            bar,
            open=Fraction(bar.open) * scale,
            high=Fraction(bar.high) * scale,
            low=Fraction(bar.low) * scale,
            close=Fraction(bar.close) * scale,
        )
        for i, bar in bars.items()
    }
    pending, _ = _start(bars, direction=direction)
    result = _advance(pending, bars, 34)
    assert result.entry_confirmation is True
    assert 0 < abs(result.confirmation.histogram) < scale
    assert NO_MACD_MAGNITUDE_THRESHOLD is True


@pytest.mark.parametrize(
    ("index", "values"),
    [
        (0, (Fraction(1, 10), Fraction(1, 10), Fraction(0), Fraction(0), Fraction(0))),
        (
            1,
            (
                Fraction(33, 130),
                Fraction(47, 270),
                Fraction(28, 351),
                Fraction(28, 1755),
                Fraction(112, 1755),
            ),
        ),
        (
            2,
            (
                Fraction(389, 1690),
                Fraction(1229, 7290),
                Fraction(7588, 123201),
                Fraction(77252, 3080025),
                Fraction(112448, 3080025),
            ),
        ),
    ],
)
def test_exact_macd_initialization_and_recurrence_golden_values(index, values) -> None:
    closes = [Decimal("0.1"), Decimal("1.1"), Decimal("0.1")]
    bars = {i: _bar(i, close=close) for i, close in enumerate(closes)}
    guarded = ClosedPrefix(bars, index)
    with localcontext() as arithmetic:
        arithmetic.prec = 2
        arithmetic.traps[Inexact] = True
        result = evaluate_macd_v2(through_bar_index=index, bars_by_index=guarded)
    assert (MACD_FAST, MACD_SLOW, MACD_SIGNAL) == (12, 26, 9)
    assert MACD_WARMUP_CLOSED_BARS == MACD_SLOW + MACD_SIGNAL == 35
    assert MACD_SESSION_RESET is False
    assert result.status is MACDStatusV2.INSUFFICIENT_MACD_WARMUP
    assert (result.ema12, result.ema26, result.macd, result.signal, result.histogram) == values
    assert result.known_at_timestamp == _timestamp(index)
    assert guarded.reads == list(range(index + 1))
    if index == 0:
        assert result.previous_macd is result.previous_histogram is None
    elif index == 1:
        assert result.previous_macd == result.previous_histogram == 0
    else:
        assert result.previous_macd == Fraction(28, 351)
        assert result.previous_histogram == Fraction(112, 1755)


@pytest.mark.parametrize("index", [0, 1, 25, 32, 33, 34])
def test_mechanical_warmup_counts_actual_closed_bars_including_candidate(index) -> None:
    bars = {i: _bar(i) for i in range(index + 1)}
    result = evaluate_macd_v2(through_bar_index=index, bars_by_index=ClosedPrefix(bars, index))
    expected = MACDStatusV2.EVALUATED if index == 34 else MACDStatusV2.INSUFFICIENT_MACD_WARMUP
    assert result.status is expected
    assert result.macd == result.signal == result.histogram == 0
    assert evaluate_macd_momentum_v2(direction=RegimeDirection.LONG, macd=result) is False


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_warmup_failure_at_first_candidate_can_pass_at_second(direction) -> None:
    bars, pending, _ = _setup(direction, k=32)
    first = _advance(pending, bars, 33)
    assert first.candidate.price_qualified is True
    assert first.candidate.momentum_qualified is False
    assert first.status is Status.INSUFFICIENT_MACD_WARMUP
    assert first.state is State.AWAITING_CONFIRMATION
    second = _advance(first, bars, 34)
    assert second.entry_confirmation is True
    assert second.confirmation.confirmation_bar_index == 34


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_insufficient_macd_warmup_cannot_extend_confirmation_window(direction) -> None:
    bars, pending, pullback = _setup(direction, k=31)
    first = _advance(pending, bars, 32)
    second = _advance(first, bars, 33)
    assert second.status is Status.INSUFFICIENT_MACD_WARMUP
    assert second.state is State.EXPIRED_NO_ENTRY_CONFIRMATION
    assert second.entry_confirmation is False
    assert second.opportunity.consumed_context is pullback.lifetime.context
    assert _advance(second, ClosedPrefix({}, -1), 34) is second


def test_macd_only_uses_closes_and_does_not_reset_or_fill_clock_gaps() -> None:
    original = _history()
    expected = evaluate_macd_v2(through_bar_index=34, bars_by_index=original)
    bars = {
        i: replace(
            bar,
            open=None,
            high=None,
            low=None,
            timestamp_utc=bar.timestamp_utc + (timedelta(days=2) if i >= 16 else timedelta(0)),
        )
        for i, bar in original.items()
    }
    result = evaluate_macd_v2(through_bar_index=34, bars_by_index=ClosedPrefix(bars, 34))
    assert replace(result, known_at_timestamp=expected.known_at_timestamp) == expected
    assert result.known_at_timestamp == _timestamp(34) + timedelta(days=2)
    assert len(bars) == len(original)


@pytest.mark.parametrize("index", [0, 12, 33, 34])
@pytest.mark.parametrize("close", [None, Decimal("NaN"), Decimal("Infinity"), 10.0, True])
def test_missing_nonfinite_or_inexact_macd_input_fails_closed(index, close) -> None:
    bars, pending, _ = _setup()
    bars[index] = replace(bars[index], close=close)
    result = _advance(pending, ClosedPrefix(bars, 34), 34)
    assert result.status is Status.INVALID_MACD_INPUT
    assert result.entry_confirmation is False
    assert result.state is State.AWAITING_CONFIRMATION


@pytest.mark.parametrize("index", [0, 10, 34])
@pytest.mark.parametrize("missing", [True, False])
def test_absent_or_unclosed_required_bar_cannot_enter_macd(index, missing) -> None:
    bars = _history()
    if missing:
        del bars[index]
    else:
        bars[index] = replace(bars[index], is_closed=False)
    result = evaluate_macd_v2(through_bar_index=34, bars_by_index=bars)
    assert result.status is MACDStatusV2.INVALID_MACD_INPUT
    assert result.macd is None


@pytest.mark.parametrize("open_", [None, Decimal("NaN"), Decimal("Infinity"), 11.0, True])
def test_invalid_confirmation_open_cannot_qualify(open_) -> None:
    bars, pending, _ = _setup()
    bars[34] = replace(bars[34], open=open_)
    result = _advance(pending, bars, 34)
    assert result.status is Status.INVALID_CONFIRMATION_INPUT
    assert result.entry_confirmation is False


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_future_mutation_has_no_effect_before_that_close(direction) -> None:
    bars, pending, _ = _setup(direction)
    original = _advance(pending, ClosedPrefix(bars, 34), 34)
    altered = dict(bars)
    altered[35] = replace(bars[35], open=None, close=Decimal("NaN"), is_closed=False)
    altered[36] = replace(bars[36], timestamp_utc=_timestamp(34), close=10**100)
    altered[10**6] = _bar(10**6, close=None)
    assert _advance(pending, ClosedPrefix(altered, 34), 34) == original
    assert evaluate_macd_v2(through_bar_index=34, bars_by_index=ClosedPrefix(altered, 34)) == (
        evaluate_macd_v2(through_bar_index=34, bars_by_index=ClosedPrefix(bars, 34))
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_pullback_body_is_captured_once_at_consumption(direction) -> None:
    bars, pending, _ = _setup(direction)
    original = _advance(pending, bars, 34)
    altered = dict(bars)
    altered[33] = replace(bars[33], open=10**100, high=None, low=None)
    assert _advance(pending, altered, 34) == original  # MACD still reads only Close[k].
    with pytest.raises(FrozenInstanceError):
        pending.opportunity.pullback_body_high = Fraction(0)


def test_long_short_mirror_symmetry_preserves_clocks_states_and_exact_indicator_signs() -> None:
    long_bars, long_pending, _ = _setup()
    short_bars, short_pending, _ = _setup(RegimeDirection.SHORT)
    long = _advance(long_pending, long_bars, 34)
    short = _advance(short_pending, short_bars, 34)
    assert long.state is short.state is State.CONFIRMED
    assert long.entry_confirmation is short.entry_confirmation is True
    assert long.confirmation.confirmation_bar_index == short.confirmation.confirmation_bar_index
    assert long.confirmation.confirmation_timestamp == short.confirmation.confirmation_timestamp
    assert long.confirmation.ema_reference + short.confirmation.ema_reference == 20
    for field in ("macd", "signal", "histogram", "previous_macd", "previous_histogram"):
        assert getattr(long.confirmation, field) == -getattr(short.confirmation, field)
    assert (
        long_pending.opportunity.pullback_body_high + short_pending.opportunity.pullback_body_low
        == 20
    )


def test_candidates_cannot_be_skipped_or_reordered() -> None:
    bars, pending, _ = _setup()
    with pytest.raises(EntryConfirmationV2Error, match="processed in order"):
        _advance(pending, ClosedPrefix({}, -1), 35)
    bars[34] = replace(bars[34], open=14)
    first = _advance(pending, bars, 34)
    for q in (32, 33, 34):
        with pytest.raises(EntryConfirmationV2Error, match="advance causally"):
            _advance(first, ClosedPrefix({}, -1), q)


@pytest.mark.parametrize("closed", [False, 1, None])
def test_unclosed_candidate_clock_cannot_trigger_confirmation(closed) -> None:
    _, pending, _ = _setup()
    with pytest.raises(EntryConfirmationV2Error, match="closed observation"):
        _advance(pending, ClosedPrefix({}, -1), 34, closed=closed)


def test_candidate_and_history_metadata_must_be_causal_and_consistent() -> None:
    bars, pending, _ = _setup()
    with pytest.raises(EntryConfirmationV2Error, match="observed close"):
        _advance(pending, bars, 34, _timestamp(34) + timedelta(seconds=1))
    for index, replacement, message in (
        (1, replace(bars[1], bar_index=2), "requested index"),
        (1, replace(bars[1], timestamp_utc=_timestamp(0)), "causal and increasing"),
        (1, replace(bars[1], timestamp_utc=_timestamp(35)), "causal and increasing"),
    ):
        altered = dict(bars)
        altered[index] = replacement
        with pytest.raises(EntryConfirmationV2Error, match=message):
            _advance(pending, altered, 34)


def test_only_formal_qualified_consumption_can_start_confirmation() -> None:
    bars, _, pullback = _setup()
    with pytest.raises(EntryConfirmationV2Error, match="formal pullback transition"):
        begin_entry_confirmation_momentum_v2(pullback=pullback.lifetime, pullback_bar=bars[33])
    with pytest.raises(EntryConfirmationV2Error, match="newly qualified"):
        begin_entry_confirmation_momentum_v2(
            pullback=replace(
                pullback, pullback=replace(pullback.pullback, pullback_qualified=False)
            ),
            pullback_bar=bars[33],
        )
    with pytest.raises(EntryConfirmationV2Error, match="provenance"):
        begin_entry_confirmation_momentum_v2(pullback=pullback, pullback_bar=bars[34])
    with pytest.raises(EntryConfirmationV2Error, match="provenance"):
        begin_entry_confirmation_momentum_v2(
            pullback=replace(
                pullback, pullback=replace(pullback.pullback, ema_reference=Fraction(0))
            ),
            pullback_bar=bars[33],
        )


def test_end_of_available_data_never_synthesizes_confirmation_or_reactivates_context() -> None:
    bars, pending, pullback = _setup()
    bars[34] = replace(bars[34], open=14)
    first = _advance(pending, ClosedPrefix(bars, 34), 34)
    assert first.state is State.AWAITING_CONFIRMATION
    assert first.entry_confirmation is False
    assert first.confirmation is None
    assert first.opportunity.consumed_context is pullback.lifetime.context
    assert first.opportunity.consumed_context.state is RegimeContextLifetimeState.CONSUMED
