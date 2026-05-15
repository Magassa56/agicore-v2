"""Fixtures and mock data helpers for the strategy sandbox."""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

import pytest

from agicore.strategy.signal_models import OHLCV


def _bar(ts: datetime, close: float, *, vol: float = 1000.0) -> OHLCV:
    """Convenience : OHLC all equal to `close` for deterministic testing."""
    return OHLCV(
        timestamp=ts,
        open=close,
        high=close,
        low=close,
        close=close,
        volume=vol,
    )


@pytest.fixture()
def make_bars():
    """Factory : produce N OHLCV bars from a list of close prices."""
    def _factory(closes: list[float], *, start_ts: datetime | None = None) -> list[OHLCV]:
        ts0 = start_ts or datetime(2026, 1, 1, tzinfo=timezone.utc)
        return [
            _bar(ts0 + timedelta(minutes=i), c) for i, c in enumerate(closes)
        ]
    return _factory


@pytest.fixture()
def rising_series() -> list[float]:
    """Strictly monotonic rising prices — guarantees one bullish cross then no other."""
    return [100.0 + 0.5 * i for i in range(60)]


@pytest.fixture()
def falling_series() -> list[float]:
    """Strictly monotonic falling — bearish-only, no BUY (no prior bullish cross)."""
    return [200.0 - 0.5 * i for i in range(60)]


@pytest.fixture()
def oscillating_series() -> list[float]:
    """Sine wave around 100 — guarantees several BUY/SELL round-trips."""
    return [100.0 + 8.0 * math.sin(i * 0.35) for i in range(80)]


@pytest.fixture()
def constant_series() -> list[float]:
    """Flat prices — fast and slow EMA should converge, no cross."""
    return [100.0] * 60
