"""AGIcore-v2 — L1 Perception layer.

Phase 8A : MockMarketFeed — deterministic offline market data feed.
Future phases : real adapters (broker feeds, websocket bridges) plug
in here under the same EventBus contract.
"""
from .market_models import (
    ALLOWED_PATTERNS,
    EVT_MARKET_TICK,
    MarketTick,
    TickPattern,
)
from .mock_market_feed import (
    DEFAULT_BASE_PRICE,
    DEFAULT_BID_ASK_SPREAD,
    DEFAULT_PATTERN,
    DEFAULT_POLL_RESOLUTION_S,
    DEFAULT_TICK_INTERVAL_S,
    MockMarketFeed,
    PriceProvider,
)

__all__ = [
    "MarketTick",
    "TickPattern",
    "EVT_MARKET_TICK",
    "ALLOWED_PATTERNS",
    "MockMarketFeed",
    "PriceProvider",
    "DEFAULT_TICK_INTERVAL_S",
    "DEFAULT_POLL_RESOLUTION_S",
    "DEFAULT_BASE_PRICE",
    "DEFAULT_BID_ASK_SPREAD",
    "DEFAULT_PATTERN",
]
