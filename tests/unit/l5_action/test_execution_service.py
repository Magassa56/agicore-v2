"""Unit tests for ExecutionService."""
from __future__ import annotations

import pytest

from agicore.l5_action.broker_mock import MockBroker
from agicore.l5_action.broker_models import (
    OrderRequest,
    OrderSide,
    OrderStatus,
    OrderType,
)
from agicore.l5_action.execution_service import ExecutionService


def _service() -> ExecutionService:
    return ExecutionService(MockBroker(initial_prices={"ES": 100.0}))


def test_submit_market_buy_helper() -> None:
    svc = _service()
    rep = svc.submit_market_order("ES", OrderSide.BUY, 1.0)
    assert rep.status == OrderStatus.FILLED
    assert rep.filled_price == 100.0


def test_submit_limit_helper() -> None:
    svc = _service()
    rep = svc.submit_limit_order("ES", OrderSide.BUY, 1.0, 90.0)
    assert rep.status == OrderStatus.PENDING


def test_submit_arbitrary_request() -> None:
    svc = _service()
    rep = svc.submit(OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=1.0))
    assert rep.status == OrderStatus.FILLED


def test_cancel_via_service() -> None:
    svc = _service()
    rep = svc.submit_limit_order("ES", OrderSide.BUY, 1.0, 50.0)
    cancel = svc.cancel(rep.order_id)
    assert cancel.status == OrderStatus.CANCELLED


def test_get_position_via_service() -> None:
    svc = _service()
    assert svc.get_position("ES") is None
    svc.submit_market_order("ES", OrderSide.BUY, 1.0)
    pos = svc.get_position("ES")
    assert pos is not None and pos.quantity == 1.0


def test_get_open_orders_via_service() -> None:
    svc = _service()
    svc.submit_limit_order("ES", OrderSide.BUY, 1.0, 50.0)
    opens = svc.get_open_orders()
    assert len(opens) == 1
    assert opens[0].order_type == OrderType.LIMIT


def test_broker_property_exposes_underlying() -> None:
    broker = MockBroker()
    svc = ExecutionService(broker)
    assert svc.broker is broker
