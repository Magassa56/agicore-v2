"""Market data domain models — Phase 8A L1 Perception.

Pure data, fully offline. The MarketTick is the canonical observation
unit emitted by any market feed (mock today, future adapters later).
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Canonical event type emitted on the Runtime EventBus
# ============================================================================
EVT_MARKET_TICK: str = "market.tick"


# ============================================================================
# Tick generation patterns (deterministic, offline)
# ============================================================================
class TickPattern(str, Enum):
    OSCILLATING = "oscillating"
    RISING = "rising"
    FALLING = "falling"
    CONSTANT = "constant"


# Allowed pattern strings — accepted by MockMarketFeed
ALLOWED_PATTERNS: tuple[str, ...] = tuple(p.value for p in TickPattern)


# ============================================================================
# MarketTick — the immutable observation record
# ============================================================================
class MarketTick(BaseModel):
    """Single tick of market data. Frozen Pydantic — immutable."""
    model_config = ConfigDict(frozen=True)

    symbol: str = Field(..., min_length=1, max_length=32)
    timestamp: datetime
    sequence: int = Field(..., ge=0)
    price: float = Field(..., gt=0)
    bid: float = Field(..., gt=0)
    ask: float = Field(..., gt=0)
    volume: float = Field(default=0.0, ge=0)
    pattern: str | None = Field(default=None, max_length=32)


__all__ = [
    "MarketTick",
    "TickPattern",
    "EVT_MARKET_TICK",
    "ALLOWED_PATTERNS",
]
