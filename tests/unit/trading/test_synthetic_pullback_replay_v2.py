"""Compare incremental synthetic pullback with the frozen reference."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from random import Random

import pytest

from agicore.trading import ema20_pullback_v2 as frozen
from agicore.trading import regime_context_v2 as regime
from agicore.trading.synthetic_pullback_replay_v2 import IncrementalEMA20, advance_pullback


@pytest.mark.parametrize("direction", list(regime.RegimeDirection))
def test_exact_incremental_pullback_matches_full_history_and_qualifies(direction):
    start = datetime(2099, 1, 1, tzinfo=UTC)
    bars = []
    for i in range(20):
        close = 8 if i == 0 else 12 if i == 19 else 10
        if direction is regime.RegimeDirection.SHORT:
            close = 20 - close
        bars.append(
            frozen.EMA20PullbackBarV2(
                i, start + timedelta(minutes=i), close, close, close, close, True
            )
        )
    candidate = (12, 14, 10, 11) if direction is regime.RegimeDirection.LONG else (8, 10, 6, 9)
    bars.append(frozen.EMA20PullbackBarV2(20, start + timedelta(minutes=20), *candidate, True))
    fast_ema = IncrementalEMA20()
    fast_previous = reference_previous = None
    history = {}
    for bar in bars:
        history[bar.bar_index] = bar
        event = None
        if bar.bar_index == 19:
            event = regime.RegimeEvent(
                regime.RegimeEventType.DIRECTIONAL_IMPULSE_EVENT,
                direction,
                bar.bar_index,
                bar.timestamp_utc,
            )
        fast = advance_pullback(
            fast_previous,
            bar,
            fast_ema,
            directional_impulse_event=event,
            reversal_transition_event=None,
        )
        expected = frozen.advance_ema20_pullback_v2(
            previous=reference_previous,
            closed_bar_index=bar.bar_index,
            closed_bar_timestamp=bar.timestamp_utc,
            source_bar_closed=True,
            bars_by_index=history,
            directional_impulse_event=event,
        )
        assert fast == expected
        fast_previous, reference_previous = fast.lifetime, expected.lifetime
        fast_ema.append(bar)
    assert fast.pullback is not None and fast.pullback.pullback_qualified
    assert fast.lifetime.context.state is regime.RegimeContextLifetimeState.CONSUMED


def test_inexact_or_noncausal_inputs_fail_closed():
    clock = datetime(2099, 1, 1, tzinfo=UTC)
    ema = IncrementalEMA20()
    with pytest.raises(ValueError):
        ema.append(frozen.EMA20PullbackBarV2(1, clock, 1, 1, 1, 1, True))
    with pytest.raises(ValueError):
        ema.append(frozen.EMA20PullbackBarV2(0, clock, 1, 1, 1, Decimal("NaN"), True))


def test_exact_ema_matches_full_history_at_multiple_checkpoints():
    rng = Random(827)
    start = datetime(2099, 1, 1, tzinfo=UTC)
    ema = IncrementalEMA20()
    history = {}
    for i in range(1_000):
        close = Decimal(rng.randrange(100, 1_000)) / 4
        bar = frozen.EMA20PullbackBarV2(
            i, start + timedelta(minutes=i + 7 * (i // 53)), close, close, close, close, True
        )
        history[i] = bar
        ema.append(bar)
        if i in (19, 20, 21, 39, 100, 255, 511, 999):
            reference = frozen.evaluate_ema20_v2(through_bar_index=i, bars_by_index=history)
            assert ema.reference == reference.ema20
            assert ema.last_close == reference.last_close


def test_incremental_matches_frozen_across_mixed_events_and_clock_gaps():
    rng = Random(937)
    start = datetime(2099, 1, 1, tzinfo=UTC)
    fast_ema = IncrementalEMA20()
    fast_previous = reference_previous = None
    history = {}
    for i in range(350):
        mid = Decimal(rng.randrange(375, 425)) / 4
        close = mid + Decimal(rng.randrange(-4, 5)) / 4
        bar = frozen.EMA20PullbackBarV2(
            i,
            start + timedelta(minutes=i + 10 * (i // 37)),
            mid,
            max(mid, close) + 1,
            min(mid, close) - 1,
            close,
            True,
        )
        history[i] = bar
        direction = regime.RegimeDirection.LONG if (i // 13) % 2 else regime.RegimeDirection.SHORT
        event = (
            regime.RegimeEvent(
                regime.RegimeEventType.DIRECTIONAL_IMPULSE_EVENT, direction, i, bar.timestamp_utc
            )
            if i % 13 == 0
            else None
        )
        opposite = (
            regime.RegimeEvent(
                regime.RegimeEventType.REVERSAL_TRANSITION_EVENT,
                regime.RegimeDirection.SHORT
                if direction is regime.RegimeDirection.LONG
                else regime.RegimeDirection.LONG,
                i,
                bar.timestamp_utc,
            )
            if i % 39 == 0
            else None
        )
        actual = advance_pullback(
            fast_previous,
            bar,
            fast_ema,
            directional_impulse_event=event,
            reversal_transition_event=opposite,
        )
        expected = frozen.advance_ema20_pullback_v2(
            previous=reference_previous,
            closed_bar_index=i,
            closed_bar_timestamp=bar.timestamp_utc,
            source_bar_closed=True,
            bars_by_index=history,
            directional_impulse_event=event,
            reversal_transition_event=opposite,
        )
        assert actual == expected
        fast_previous, reference_previous = actual.lifetime, expected.lifetime
        fast_ema.append(bar)
