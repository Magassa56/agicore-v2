"""Unit tests for MockBroker."""
from __future__ import annotations

import threading

import pytest

from agicore.l5_action.broker_mock import MockBroker
from agicore.l5_action.broker_models import (
    Broker,
    InvalidOrderError,
    OrderNotFoundError,
    OrderRequest,
    OrderSide,
    OrderStatus,
    OrderType,
)


# ---------------------------------------------------------------- Submit MARKET
def test_market_buy_no_price_is_rejected() -> None:
    b = MockBroker()
    rep = b.submit_order(OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=1.0))
    assert rep.status == OrderStatus.REJECTED
    assert "no market price" in rep.message


def test_market_buy_fills_immediately() -> None:
    b = MockBroker(initial_prices={"ES": 100.0})
    rep = b.submit_order(OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=2.0))
    assert rep.status == OrderStatus.FILLED
    assert rep.filled_price == 100.0
    assert rep.filled_quantity == 2.0
    pos = b.get_position("ES")
    assert pos is not None
    assert pos.quantity == 2.0
    assert pos.avg_entry_price == 100.0


def test_market_buy_two_fills_weighted_average() -> None:
    b = MockBroker(initial_prices={"ES": 100.0})
    b.submit_order(OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=10.0))
    b.set_market_price("ES", 110.0)
    b.submit_order(OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=10.0))
    pos = b.get_position("ES")
    assert pos.quantity == 20.0
    # (10 * 100 + 10 * 110) / 20 = 105
    assert pos.avg_entry_price == pytest.approx(105.0)


def test_market_sell_without_position_rejected() -> None:
    b = MockBroker(initial_prices={"ES": 100.0})
    rep = b.submit_order(OrderRequest(symbol="ES", side=OrderSide.SELL, quantity=1.0))
    assert rep.status == OrderStatus.REJECTED
    assert "insufficient position" in rep.message


def test_market_sell_oversize_rejected() -> None:
    b = MockBroker(initial_prices={"ES": 100.0})
    b.submit_order(OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=2.0))
    rep = b.submit_order(OrderRequest(symbol="ES", side=OrderSide.SELL, quantity=5.0))
    assert rep.status == OrderStatus.REJECTED


def test_market_sell_full_close_realizes_pnl() -> None:
    b = MockBroker(initial_prices={"ES": 100.0})
    b.submit_order(OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=4.0))
    b.set_market_price("ES", 120.0)
    b.submit_order(OrderRequest(symbol="ES", side=OrderSide.SELL, quantity=4.0))
    pos = b.get_position("ES")
    assert pos.quantity == 0.0
    assert pos.realized_pnl == pytest.approx(80.0)  # (120 - 100) * 4


def test_market_sell_partial_keeps_position() -> None:
    b = MockBroker(initial_prices={"ES": 100.0})
    b.submit_order(OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=10.0))
    b.set_market_price("ES", 110.0)
    b.submit_order(OrderRequest(symbol="ES", side=OrderSide.SELL, quantity=4.0))
    pos = b.get_position("ES")
    assert pos.quantity == 6.0
    assert pos.avg_entry_price == 100.0  # unchanged for the residual
    assert pos.realized_pnl == pytest.approx(40.0)


# ---------------------------------------------------------------- LIMIT
def test_limit_buy_resting_until_crossed() -> None:
    b = MockBroker(initial_prices={"ES": 100.0})
    rep = b.submit_order(OrderRequest(
        symbol="ES", side=OrderSide.BUY, quantity=1.0,
        order_type=OrderType.LIMIT, limit_price=95.0,
    ))
    assert rep.status == OrderStatus.PENDING
    assert b.get_open_orders() != []

    # Move below limit → fills
    b.set_market_price("ES", 94.0)
    open_orders = b.get_open_orders()
    assert open_orders == []  # was filled
    pos = b.get_position("ES")
    assert pos.quantity == 1.0
    assert pos.avg_entry_price == 94.0  # actual fill price


def test_limit_buy_already_crossed_fills_immediately() -> None:
    b = MockBroker(initial_prices={"ES": 90.0})
    rep = b.submit_order(OrderRequest(
        symbol="ES", side=OrderSide.BUY, quantity=1.0,
        order_type=OrderType.LIMIT, limit_price=95.0,
    ))
    assert rep.status == OrderStatus.FILLED


def test_limit_sell_crossed_when_price_rises() -> None:
    b = MockBroker(initial_prices={"ES": 100.0})
    b.submit_order(OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=2.0))
    rep = b.submit_order(OrderRequest(
        symbol="ES", side=OrderSide.SELL, quantity=2.0,
        order_type=OrderType.LIMIT, limit_price=120.0,
    ))
    assert rep.status == OrderStatus.PENDING
    b.set_market_price("ES", 125.0)  # crosses the SELL limit
    pos = b.get_position("ES")
    assert pos.quantity == 0.0


# ---------------------------------------------------------------- Cancel / inspect
def test_cancel_pending_order() -> None:
    b = MockBroker(initial_prices={"ES": 100.0})
    rep = b.submit_order(OrderRequest(
        symbol="ES", side=OrderSide.BUY, quantity=1.0,
        order_type=OrderType.LIMIT, limit_price=50.0,
    ))
    assert rep.status == OrderStatus.PENDING
    cancel = b.cancel_order(rep.order_id)
    assert cancel.status == OrderStatus.CANCELLED
    assert b.get_open_orders() == []


def test_cancel_filled_order_no_op() -> None:
    b = MockBroker(initial_prices={"ES": 100.0})
    rep = b.submit_order(OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=1.0))
    assert rep.status == OrderStatus.FILLED
    cancel = b.cancel_order(rep.order_id)
    assert cancel.status == OrderStatus.FILLED  # already filled, returned as-is
    assert "cannot cancel" in cancel.message


def test_cancel_unknown_order_raises() -> None:
    b = MockBroker()
    with pytest.raises(OrderNotFoundError):
        b.cancel_order("nope")


def test_get_open_orders_returns_only_pending() -> None:
    b = MockBroker(initial_prices={"ES": 100.0})
    # 1 filled
    b.submit_order(OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=1.0))
    # 1 pending
    b.submit_order(OrderRequest(
        symbol="ES", side=OrderSide.BUY, quantity=1.0,
        order_type=OrderType.LIMIT, limit_price=50.0,
    ))
    open_orders = b.get_open_orders()
    assert len(open_orders) == 1
    assert open_orders[0].status == OrderStatus.PENDING


def test_set_market_price_negative_rejected() -> None:
    b = MockBroker()
    with pytest.raises(InvalidOrderError):
        b.set_market_price("ES", -5)


def test_protocol_compliance() -> None:
    """MockBroker must satisfy the Broker Protocol (structural)."""
    b: Broker = MockBroker()
    assert b is not None


def test_client_order_id_used_as_id() -> None:
    b = MockBroker(initial_prices={"ES": 100.0})
    rep = b.submit_order(OrderRequest(
        symbol="ES", side=OrderSide.BUY, quantity=1.0,
        client_order_id="my-coid-1",
    ))
    assert rep.order_id == "my-coid-1"


def test_reset_clears_state() -> None:
    b = MockBroker(initial_prices={"ES": 100.0})
    b.submit_order(OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=1.0))
    b.reset()
    assert b.get_position("ES") is None
    assert b.get_open_orders() == []
    assert b.get_market_price("ES") is None


# ---------------------------------------------------------------- Concurrency
def test_concurrent_submits_consistent() -> None:
    b = MockBroker(initial_prices={"ES": 100.0})
    N = 50

    def submit_one():
        b.submit_order(OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=1.0))

    threads = [threading.Thread(target=submit_one) for _ in range(N)]
    for t in threads: t.start()
    for t in threads: t.join()

    pos = b.get_position("ES")
    assert pos.quantity == float(N)
    # Toutes au même prix → average = 100
    assert pos.avg_entry_price == pytest.approx(100.0)
