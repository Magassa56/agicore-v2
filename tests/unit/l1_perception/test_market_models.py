"""Unit tests for market_models DTOs."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from agicore.l1_perception.market_models import (
    ALLOWED_PATTERNS,
    EVT_MARKET_TICK,
    MarketTick,
    TickPattern,
)


def test_canonical_event_constant() -> None:
    assert EVT_MARKET_TICK == "market.tick"


def test_pattern_enum_values() -> None:
    assert TickPattern.OSCILLATING.value == "oscillating"
    assert TickPattern.RISING.value == "rising"
    assert TickPattern.FALLING.value == "falling"
    assert TickPattern.CONSTANT.value == "constant"
    assert "oscillating" in ALLOWED_PATTERNS
    assert "rising" in ALLOWED_PATTERNS
    assert "falling" in ALLOWED_PATTERNS
    assert "constant" in ALLOWED_PATTERNS


def test_market_tick_minimal() -> None:
    t = MarketTick(
        symbol="ES", timestamp=datetime.now(timezone.utc),
        sequence=0, price=100.0, bid=99.95, ask=100.05,
    )
    assert t.symbol == "ES"
    assert t.volume == 0.0


def test_market_tick_frozen() -> None:
    t = MarketTick(
        symbol="ES", timestamp=datetime.now(timezone.utc),
        sequence=0, price=100.0, bid=99.95, ask=100.05,
    )
    with pytest.raises(Exception):
        t.price = 200.0  # type: ignore[misc]


def test_market_tick_validates_positives() -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        MarketTick(symbol="ES", timestamp=now, sequence=0,
                   price=0, bid=99.95, ask=100.05)
    with pytest.raises(ValidationError):
        MarketTick(symbol="ES", timestamp=now, sequence=-1,
                   price=100.0, bid=99.95, ask=100.05)


def test_market_tick_with_pattern() -> None:
    t = MarketTick(
        symbol="ES", timestamp=datetime.now(timezone.utc),
        sequence=0, price=100.0, bid=99.95, ask=100.05,
        pattern="oscillating",
    )
    assert t.pattern == "oscillating"
