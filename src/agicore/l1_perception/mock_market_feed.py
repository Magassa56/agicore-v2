"""MockMarketFeed — deterministic offline market data feed.

Phase 8A. Generates ``MarketTick`` events on the Runtime EventBus at a
configurable interval. Single daemon thread, idempotent start/stop, no
networking, no broker, no websocket.

Patterns
--------
- ``oscillating`` : ``base + 12 * sin(0.30 * i)``
- ``rising``      : ``base + 0.5 * i``
- ``falling``     : ``max(0.01, base - 0.5 * i)``
- ``constant``    : ``base``

For full control, callers can pass a ``price_provider`` callable that
maps the tick index to a price ; the feed will then ignore ``pattern``.

Every tick :
- increments a monotonic ``sequence``
- emits ``EVT_MARKET_TICK`` on the EventBus with a ``MarketTick`` payload
- optionally stops automatically after ``max_ticks`` ticks
"""
from __future__ import annotations

import math
import threading
import time
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

import structlog

from agicore.core.events import EventBus

from .market_models import (
    ALLOWED_PATTERNS,
    EVT_MARKET_TICK,
    MarketTick,
    TickPattern,
)

logger = structlog.get_logger(__name__)


# Defaults — kept module-level so they can be reused by tests / docs
DEFAULT_TICK_INTERVAL_S: float = 1.0
DEFAULT_POLL_RESOLUTION_S: float = 0.1
DEFAULT_BASE_PRICE: float = 100.0
DEFAULT_BID_ASK_SPREAD: float = 0.10
DEFAULT_PATTERN: str = TickPattern.OSCILLATING.value


PriceProvider = Callable[[int], float]


def _builtin_price(pattern: str, base: float, idx: int) -> float:
    """Deterministic price from a built-in pattern."""
    if pattern == TickPattern.OSCILLATING.value:
        return base + 12.0 * math.sin(idx * 0.30)
    if pattern == TickPattern.RISING.value:
        return base + 0.5 * idx
    if pattern == TickPattern.FALLING.value:
        return max(0.01, base - 0.5 * idx)
    return base  # CONSTANT


class MockMarketFeed:
    """Deterministic mock market feed.

    Parameters
    ----------
    event_bus : EventBus
        Required. ``EVT_MARKET_TICK`` events are emitted here.
    symbol : str
        Required. Symbol the feed produces ticks for.
    tick_interval_s : float
        Seconds between ticks. Must be > 0.
    pattern : str
        One of ``ALLOWED_PATTERNS``. Ignored if ``price_provider`` is set.
    base_price : float
        Reference price for built-in patterns. Must be > 0.
    bid_ask_spread : float
        Total spread ; bid = price - spread/2, ask = price + spread/2.
    max_ticks : int | None
        If set, the feed stops after producing this many ticks.
    poll_resolution_s : float | None
        Sleep granularity for the loop. Smaller values shorten stop()
        latency at the cost of slightly more CPU. Defaults to 0.1 s
        (or ``tick_interval_s`` if smaller).
    price_provider : Callable[[int], float] | None
        Optional override : given the tick index, return the price.
        Use for fully-scripted scenarios.
    """

    def __init__(
        self,
        event_bus: EventBus,
        symbol: str,
        *,
        tick_interval_s: float = DEFAULT_TICK_INTERVAL_S,
        pattern: str = DEFAULT_PATTERN,
        base_price: float = DEFAULT_BASE_PRICE,
        bid_ask_spread: float = DEFAULT_BID_ASK_SPREAD,
        max_ticks: int | None = None,
        poll_resolution_s: float | None = None,
        price_provider: PriceProvider | None = None,
    ) -> None:
        if tick_interval_s <= 0:
            raise ValueError("tick_interval_s must be > 0")
        if base_price <= 0:
            raise ValueError("base_price must be > 0")
        if bid_ask_spread < 0:
            raise ValueError("bid_ask_spread must be >= 0")
        if max_ticks is not None and max_ticks < 0:
            raise ValueError("max_ticks must be >= 0 or None")
        if poll_resolution_s is not None and poll_resolution_s <= 0:
            raise ValueError("poll_resolution_s must be > 0")
        if pattern not in ALLOWED_PATTERNS:
            raise ValueError(
                f"unknown pattern={pattern!r}, allowed: {ALLOWED_PATTERNS}"
            )
        if not symbol:
            raise ValueError("symbol must be non-empty")

        self._bus = event_bus
        self._symbol = symbol
        self._interval = float(tick_interval_s)
        self._pattern = pattern
        self._base = float(base_price)
        self._spread = float(bid_ask_spread)
        self._max_ticks = max_ticks
        self._poll = float(poll_resolution_s) if poll_resolution_s is not None \
            else min(DEFAULT_POLL_RESOLUTION_S, self._interval)
        self._price_provider = price_provider

        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._published_count = 0
        self._next_sequence = 0

    # ------------------------------------------------------------------ Read
    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def tick_interval_s(self) -> float:
        return self._interval

    @property
    def published_count(self) -> int:
        with self._lock:
            return self._published_count

    @property
    def next_sequence(self) -> int:
        with self._lock:
            return self._next_sequence

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    # ------------------------------------------------------------------ Lifecycle
    def start(self) -> None:
        """Start the background producer thread. Idempotent."""
        if self.is_running():
            logger.debug("mock_market_feed.already_running", symbol=self._symbol)
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop,
            name=f"mock-market-feed:{self._symbol}",
            daemon=True,
        )
        self._thread.start()
        logger.info(
            "mock_market_feed.started",
            symbol=self._symbol,
            interval_s=self._interval,
            pattern=self._pattern,
            max_ticks=self._max_ticks,
        )

    def stop(self, *, timeout_s: float = 5.0) -> None:
        """Signal the loop and join the thread. Idempotent."""
        if self._thread is None:
            return
        self._stop.set()
        self._thread.join(timeout=timeout_s)
        joined = not self._thread.is_alive()
        logger.info(
            "mock_market_feed.stopped",
            symbol=self._symbol,
            joined=joined,
            published_count=self._published_count,
        )
        self._thread = None

    def __enter__(self) -> "MockMarketFeed":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()

    # ------------------------------------------------------------------ Loop
    def _loop(self) -> None:
        next_tick_at = time.monotonic()
        while not self._stop.is_set():
            now = time.monotonic()
            if now >= next_tick_at:
                self._emit_one_tick()
                if self._max_ticks is not None and self._published_count >= self._max_ticks:
                    logger.info(
                        "mock_market_feed.max_ticks_reached",
                        symbol=self._symbol,
                        max_ticks=self._max_ticks,
                    )
                    self._stop.set()
                    break
                next_tick_at = now + self._interval
            sleep_for = max(0.0, min(self._poll, next_tick_at - time.monotonic()))
            if sleep_for > 0:
                self._stop.wait(sleep_for)

    def _emit_one_tick(self) -> None:
        with self._lock:
            idx = self._next_sequence
            self._next_sequence += 1
        try:
            price = self._compute_price(idx)
        except Exception as exc:
            logger.error(
                "mock_market_feed.price_provider_failed",
                symbol=self._symbol, idx=idx, error=str(exc),
            )
            return
        if price <= 0:
            logger.warning(
                "mock_market_feed.skipped_non_positive_price",
                symbol=self._symbol, idx=idx, price=price,
            )
            return

        half = self._spread / 2.0
        bid = max(0.0001, price - half)
        ask = price + half

        tick = MarketTick(
            symbol=self._symbol,
            timestamp=datetime.now(timezone.utc),
            sequence=idx,
            price=price,
            bid=bid,
            ask=ask,
            volume=0.0,
            pattern=self._pattern if self._price_provider is None else None,
        )
        try:
            self._bus.emit(
                EVT_MARKET_TICK,
                symbol=tick.symbol,
                timestamp=tick.timestamp.isoformat(),
                sequence=tick.sequence,
                price=tick.price,
                bid=tick.bid,
                ask=tick.ask,
                volume=tick.volume,
                pattern=tick.pattern,
            )
        except Exception as exc:
            logger.error(
                "mock_market_feed.emit_failed",
                symbol=self._symbol, idx=idx, error=str(exc),
            )
            return

        with self._lock:
            self._published_count += 1
        logger.debug(
            "mock_market_feed.tick_emitted",
            symbol=self._symbol, idx=idx, price=price,
        )

    def _compute_price(self, idx: int) -> float:
        if self._price_provider is not None:
            return float(self._price_provider(idx))
        return _builtin_price(self._pattern, self._base, idx)


__all__ = [
    "MockMarketFeed",
    "PriceProvider",
    "DEFAULT_TICK_INTERVAL_S",
    "DEFAULT_POLL_RESOLUTION_S",
    "DEFAULT_BASE_PRICE",
    "DEFAULT_BID_ASK_SPREAD",
    "DEFAULT_PATTERN",
]
