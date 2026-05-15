"""Unit tests for MockMarketFeed."""
from __future__ import annotations

import threading
import time

import pytest

from agicore.core.events import EventBus
from agicore.l1_perception.market_models import EVT_MARKET_TICK
from agicore.l1_perception.mock_market_feed import (
    DEFAULT_PATTERN,
    MockMarketFeed,
)


# ---------------------------------------------------------------- Validation
class TestValidation:
    def test_invalid_tick_interval(self) -> None:
        bus = EventBus()
        with pytest.raises(ValueError):
            MockMarketFeed(bus, "ES", tick_interval_s=0)
        with pytest.raises(ValueError):
            MockMarketFeed(bus, "ES", tick_interval_s=-1.0)

    def test_invalid_base_price(self) -> None:
        with pytest.raises(ValueError):
            MockMarketFeed(EventBus(), "ES", base_price=0)
        with pytest.raises(ValueError):
            MockMarketFeed(EventBus(), "ES", base_price=-1)

    def test_invalid_spread(self) -> None:
        with pytest.raises(ValueError):
            MockMarketFeed(EventBus(), "ES", bid_ask_spread=-0.1)

    def test_invalid_max_ticks(self) -> None:
        with pytest.raises(ValueError):
            MockMarketFeed(EventBus(), "ES", max_ticks=-1)

    def test_invalid_poll_resolution(self) -> None:
        with pytest.raises(ValueError):
            MockMarketFeed(EventBus(), "ES", poll_resolution_s=0)

    def test_invalid_pattern(self) -> None:
        with pytest.raises(ValueError):
            MockMarketFeed(EventBus(), "ES", pattern="absurd")

    def test_invalid_symbol(self) -> None:
        with pytest.raises(ValueError):
            MockMarketFeed(EventBus(), "")


# ---------------------------------------------------------------- Lifecycle
class TestLifecycle:
    def _build(self, **kw) -> MockMarketFeed:
        defaults = dict(tick_interval_s=0.03, poll_resolution_s=0.01)
        defaults.update(kw)
        return MockMarketFeed(EventBus(), "ES", **defaults)

    def test_initial_state(self) -> None:
        f = self._build()
        assert not f.is_running()
        assert f.published_count == 0

    def test_start_stop(self) -> None:
        f = self._build()
        f.start()
        assert f.is_running()
        f.stop()
        assert not f.is_running()

    def test_start_idempotent(self) -> None:
        f = self._build()
        f.start()
        f.start()  # no second thread
        assert f.is_running()
        f.stop()

    def test_stop_idempotent_when_never_started(self) -> None:
        f = self._build()
        f.stop()  # no crash

    def test_context_manager(self) -> None:
        with self._build() as f:
            assert f.is_running()
            time.sleep(0.05)
        assert not f.is_running()

    def test_no_thread_leak_after_repeated_start_stop(self) -> None:
        f = self._build()
        for _ in range(5):
            f.start()
            time.sleep(0.02)
            f.stop()
        alive = [t for t in threading.enumerate()
                 if t.name == "mock-market-feed:ES" and t.is_alive()]
        assert alive == []


# ---------------------------------------------------------------- Emission
class TestEmission:
    def test_emits_market_tick_events(self) -> None:
        bus = EventBus()
        received: list = []
        bus.subscribe(EVT_MARKET_TICK, lambda ev: received.append(ev))

        feed = MockMarketFeed(bus, "ES",
                              tick_interval_s=0.03, poll_resolution_s=0.01)
        feed.start()
        time.sleep(0.18)
        feed.stop()

        assert len(received) >= 3
        assert all(ev.event_type == EVT_MARKET_TICK for ev in received)
        # payload contient les champs canoniques
        first = received[0]
        for k in ("symbol", "timestamp", "sequence", "price", "bid", "ask"):
            assert k in first.payload

    def test_sequence_monotonic(self) -> None:
        bus = EventBus()
        seqs: list[int] = []
        bus.subscribe(EVT_MARKET_TICK, lambda ev: seqs.append(ev.payload["sequence"]))

        feed = MockMarketFeed(bus, "ES",
                              tick_interval_s=0.02, poll_resolution_s=0.01)
        feed.start()
        time.sleep(0.15)
        feed.stop()

        assert seqs == sorted(seqs)
        assert seqs == list(range(len(seqs)))

    def test_max_ticks_auto_stops(self) -> None:
        bus = EventBus()
        feed = MockMarketFeed(
            bus, "ES",
            tick_interval_s=0.01, poll_resolution_s=0.005, max_ticks=5,
        )
        feed.start()
        time.sleep(0.3)
        # Loop must have stopped on its own
        assert not feed.is_running() or feed.published_count == 5
        feed.stop()
        assert feed.published_count == 5

    def test_bid_ask_spread_applied(self) -> None:
        bus = EventBus()
        captured: list = []
        bus.subscribe(EVT_MARKET_TICK, lambda ev: captured.append(ev))
        feed = MockMarketFeed(bus, "ES",
                              tick_interval_s=0.02, poll_resolution_s=0.01,
                              pattern="constant", base_price=100.0,
                              bid_ask_spread=2.0, max_ticks=2)
        feed.start()
        time.sleep(0.15)
        feed.stop()
        for ev in captured:
            assert ev.payload["bid"] == pytest.approx(99.0)
            assert ev.payload["ask"] == pytest.approx(101.0)
            assert ev.payload["price"] == 100.0


# ---------------------------------------------------------------- Patterns
class TestPatterns:
    def _capture_n(self, pattern: str, n: int) -> list[float]:
        bus = EventBus()
        prices: list[float] = []
        bus.subscribe(EVT_MARKET_TICK, lambda ev: prices.append(ev.payload["price"]))
        feed = MockMarketFeed(
            bus, "ES",
            pattern=pattern,
            tick_interval_s=0.01, poll_resolution_s=0.005, max_ticks=n,
        )
        feed.start()
        time.sleep(0.5)
        feed.stop()
        return prices

    def test_constant_pattern(self) -> None:
        prices = self._capture_n("constant", 5)
        assert all(p == 100.0 for p in prices)

    def test_rising_pattern_monotonic(self) -> None:
        prices = self._capture_n("rising", 5)
        assert prices == sorted(prices)
        assert prices[-1] > prices[0]

    def test_falling_pattern_monotonic(self) -> None:
        prices = self._capture_n("falling", 5)
        assert prices == sorted(prices, reverse=True)

    def test_oscillating_visits_above_and_below(self) -> None:
        prices = self._capture_n("oscillating", 30)
        assert max(prices) > 100.0
        assert min(prices) < 100.0


# ---------------------------------------------------------------- Custom provider
class TestCustomProvider:
    def test_custom_price_provider_called(self) -> None:
        captured: list[float] = []
        bus = EventBus()
        bus.subscribe(EVT_MARKET_TICK, lambda ev: captured.append(ev.payload["price"]))

        seen_indices: list[int] = []
        def provider(idx: int) -> float:
            seen_indices.append(idx)
            return 50.0 + idx

        feed = MockMarketFeed(
            bus, "ES",
            tick_interval_s=0.01, poll_resolution_s=0.005,
            max_ticks=4, price_provider=provider,
        )
        feed.start()
        time.sleep(0.3)
        feed.stop()

        assert seen_indices == [0, 1, 2, 3]
        assert captured == [50.0, 51.0, 52.0, 53.0]

    def test_provider_failure_skips_tick_but_loop_continues(self) -> None:
        bus = EventBus()
        captured: list[float] = []
        bus.subscribe(EVT_MARKET_TICK, lambda ev: captured.append(ev.payload["price"]))

        def provider(idx: int) -> float:
            if idx == 1:
                raise RuntimeError("boom")
            return 100.0 + idx

        feed = MockMarketFeed(
            bus, "ES",
            tick_interval_s=0.01, poll_resolution_s=0.005,
            max_ticks=4, price_provider=provider,
        )
        feed.start()
        time.sleep(0.3)
        feed.stop()

        # Tick 1 skipped → 3 emits among 4 attempts
        # max_ticks counts published — can be 3 ou plus selon timing
        assert 100.0 in captured
        assert 102.0 in captured
        assert 103.0 in captured
        assert 101.0 not in captured  # le tick fautif a été sauté


# ---------------------------------------------------------------- Concurrence
def test_emit_failure_does_not_crash_loop() -> None:
    """Un subscriber qui crash doit pas tuer le feed."""
    bus = EventBus()
    bus.subscribe(EVT_MARKET_TICK, lambda ev: (_ for _ in ()).throw(RuntimeError("x")))
    feed = MockMarketFeed(bus, "ES",
                          tick_interval_s=0.01, poll_resolution_s=0.005,
                          max_ticks=3)
    feed.start()
    time.sleep(0.2)
    feed.stop()
    # Le feed continue malgré l'exception côté subscriber
    assert feed.published_count == 3
