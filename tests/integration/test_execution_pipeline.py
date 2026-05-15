"""Integration test — full execution pipeline through ExecutionService.

Validates that AGIcore can simulate a complete trading scenario safely
using the mock broker and the service façade. All deterministic, offline.
"""
from __future__ import annotations

import pytest

from agicore.l5_action.broker_mock import MockBroker
from agicore.l5_action.broker_models import (
    OrderSide,
    OrderStatus,
    OrderType,
)
from agicore.l5_action.execution_service import ExecutionService


def test_round_trip_with_pnl() -> None:
    """Full long round-trip : open, partial close, full close, with PnL."""
    broker = MockBroker(initial_prices={"ES": 100.0})
    svc = ExecutionService(broker)

    # 1. Open long 10 units @ 100
    open_rep = svc.submit_market_order("ES", OrderSide.BUY, 10.0)
    assert open_rep.status == OrderStatus.FILLED
    assert svc.get_position("ES").quantity == 10.0

    # 2. Price moves up → partial close 4 @ 110
    broker.set_market_price("ES", 110.0)
    partial = svc.submit_market_order("ES", OrderSide.SELL, 4.0)
    assert partial.status == OrderStatus.FILLED
    pos = svc.get_position("ES")
    assert pos.quantity == 6.0
    assert pos.realized_pnl == pytest.approx(40.0)  # (110-100)*4

    # 3. Resting LIMIT SELL @ 120 → does not fill yet
    rest = svc.submit_limit_order("ES", OrderSide.SELL, 6.0, 120.0)
    assert rest.status == OrderStatus.PENDING
    assert len(svc.get_open_orders()) == 1

    # 4. Price crosses 120 → resting order fills
    broker.set_market_price("ES", 121.0)
    pos = svc.get_position("ES")
    assert pos.quantity == 0.0
    assert pos.realized_pnl == pytest.approx(40.0 + (120.0 - 100.0) * 6.0)
    assert svc.get_open_orders() == []


def test_rejected_order_does_not_change_position() -> None:
    broker = MockBroker(initial_prices={"ES": 100.0})
    svc = ExecutionService(broker)
    rep = svc.submit_market_order("ES", OrderSide.SELL, 5.0)
    assert rep.status == OrderStatus.REJECTED
    assert svc.get_position("ES") is None  # jamais créée


def test_cancel_then_resubmit_then_fill() -> None:
    broker = MockBroker(initial_prices={"ES": 100.0})
    svc = ExecutionService(broker)

    r1 = svc.submit_limit_order("ES", OrderSide.BUY, 2.0, 90.0)
    assert r1.status == OrderStatus.PENDING

    c = svc.cancel(r1.order_id)
    assert c.status == OrderStatus.CANCELLED

    r2 = svc.submit_market_order("ES", OrderSide.BUY, 2.0)
    assert r2.status == OrderStatus.FILLED
    assert svc.get_position("ES").quantity == 2.0


def test_multi_symbol_isolation() -> None:
    broker = MockBroker(initial_prices={"ES": 100.0, "NQ": 200.0})
    svc = ExecutionService(broker)
    svc.submit_market_order("ES", OrderSide.BUY, 1.0)
    svc.submit_market_order("NQ", OrderSide.BUY, 2.0)
    assert svc.get_position("ES").quantity == 1.0
    assert svc.get_position("NQ").quantity == 2.0
    assert svc.get_position("XYZ") is None
