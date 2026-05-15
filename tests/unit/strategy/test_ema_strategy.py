"""Unit tests for EMACrossoverStrategy."""
from __future__ import annotations

import pytest

from agicore.strategy.ema_strategy import EMACrossoverStrategy
from agicore.strategy.signal_models import Action


def _signals_for(strategy, bars):
    return [strategy.on_bar(b) for b in bars]


def test_invalid_periods_rejected() -> None:
    with pytest.raises(ValueError):
        EMACrossoverStrategy(fast_period=0, slow_period=10)
    with pytest.raises(ValueError):
        EMACrossoverStrategy(fast_period=10, slow_period=10)
    with pytest.raises(ValueError):
        EMACrossoverStrategy(fast_period=20, slow_period=10)


def test_warming_up_returns_hold(make_bars) -> None:
    strategy = EMACrossoverStrategy(fast_period=3, slow_period=8)
    bars = make_bars([100.0] * 5)
    signals = _signals_for(strategy, bars)
    assert all(s.action == Action.HOLD for s in signals)
    assert all(s.reason == "warming_up" for s in signals)


def test_constant_prices_produce_no_cross(make_bars, constant_series) -> None:
    strategy = EMACrossoverStrategy(fast_period=3, slow_period=8)
    signals = _signals_for(strategy, make_bars(constant_series))
    assert all(s.action == Action.HOLD for s in signals)


def test_rising_series_produces_one_buy_no_sell(make_bars, rising_series) -> None:
    strategy = EMACrossoverStrategy(fast_period=3, slow_period=10)
    signals = _signals_for(strategy, make_bars(rising_series))
    buys = [s for s in signals if s.action == Action.BUY]
    sells = [s for s in signals if s.action == Action.SELL]
    assert len(buys) == 1, f"expected 1 BUY in rising series, got {len(buys)}"
    assert len(sells) == 0
    assert buys[0].reason == "bullish_cross"


def test_falling_series_produces_no_signals(make_bars, falling_series) -> None:
    """No prior BUY → no SELL emitted (long-only)."""
    strategy = EMACrossoverStrategy(fast_period=3, slow_period=10)
    signals = _signals_for(strategy, make_bars(falling_series))
    actions = {s.action for s in signals}
    assert Action.BUY not in actions
    assert Action.SELL not in actions


def test_oscillating_series_produces_multiple_round_trips(
    make_bars, oscillating_series
) -> None:
    strategy = EMACrossoverStrategy(fast_period=3, slow_period=10)
    signals = _signals_for(strategy, make_bars(oscillating_series))
    buys = [s for s in signals if s.action == Action.BUY]
    sells = [s for s in signals if s.action == Action.SELL]
    assert len(buys) >= 2
    # Le nombre de SELL est <= au nombre de BUY (la dernière position peut être ouverte)
    assert len(sells) >= 1
    assert len(sells) <= len(buys)


def test_position_open_state_tracking(make_bars, oscillating_series) -> None:
    strategy = EMACrossoverStrategy(fast_period=3, slow_period=10)
    signals = []
    for b in make_bars(oscillating_series):
        sig = strategy.on_bar(b)
        signals.append(sig)
        if sig.action == Action.BUY:
            assert strategy.position_open is True
        elif sig.action == Action.SELL:
            assert strategy.position_open is False


def test_no_buy_when_already_long(make_bars) -> None:
    """Une fois LONG, un second bullish cross hypothétique ne re-buy pas."""
    strategy = EMACrossoverStrategy(fast_period=2, slow_period=4)
    # Force ouverture de position via une montée
    bars = make_bars([100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110])
    sigs = _signals_for(strategy, bars)
    buys = [s for s in sigs if s.action == Action.BUY]
    assert len(buys) == 1


def test_reset_clears_state(make_bars, rising_series) -> None:
    strategy = EMACrossoverStrategy(fast_period=3, slow_period=10)
    _signals_for(strategy, make_bars(rising_series))
    assert strategy.fast_ema is not None
    strategy.reset()
    assert strategy.fast_ema is None
    assert strategy.slow_ema is None
    assert strategy.position_open is False


def test_strategy_name_includes_periods() -> None:
    s = EMACrossoverStrategy(fast_period=5, slow_period=20)
    assert "(5,20)" in s.name


def test_explicit_name_override() -> None:
    s = EMACrossoverStrategy(fast_period=5, slow_period=20, name="my_strat")
    assert s.name == "my_strat"
