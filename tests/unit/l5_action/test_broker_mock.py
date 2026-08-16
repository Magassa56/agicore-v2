from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest

from agicore.l5_action.broker_mock import MockBroker
from agicore.l5_action.broker_models import Broker, OrderRequest, OrderSide, OrderType
from agicore.l5_action.execution_service import L5RiskGateRequiredError


def _market() -> OrderRequest:
    return OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=1.0)


NOW = datetime(2026, 8, 15, 10, 0, tzinfo=timezone.utc)


def _broker_with_price() -> MockBroker:
    broker = MockBroker()
    broker.set_market_price("ES", 100.0, observed_at=NOW)
    return broker


@pytest.mark.parametrize("order_request", [
    _market(),
    OrderRequest(symbol="ES", side=OrderSide.SELL, quantity=1.0),
    OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=1.0, order_type=OrderType.LIMIT, limit_price=90.0),
])
def test_raw_orders_cannot_create_orders_fills_or_positions(order_request) -> None:
    broker = _broker_with_price()
    with pytest.raises(L5RiskGateRequiredError):
        broker.submit_order(order_request)
    assert broker.get_all_orders() == []
    assert broker.get_open_orders() == []
    assert broker.get_position("ES") is None


def test_set_market_price_never_auto_fills_limit() -> None:
    broker = _broker_with_price()
    broker.set_market_price("ES", 80.0, observed_at=NOW + timedelta(seconds=1))
    assert broker.get_market_price("ES") == 80.0
    assert broker.get_all_orders() == []


def test_cancel_and_internal_fill_paths_fail_closed() -> None:
    broker = _broker_with_price()
    with pytest.raises(L5RiskGateRequiredError):
        broker.cancel_order("order-raw")
    with pytest.raises(L5RiskGateRequiredError):
        broker._fill_order("order-raw", fill_price=100.0)
    with pytest.raises(L5RiskGateRequiredError):
        broker._apply_fill_to_position(None)


@pytest.mark.parametrize("price", [-1.0, 0.0, float("nan"), float("inf"), True])
def test_set_market_price_invalid_rejected(price) -> None:
    broker = MockBroker()
    with pytest.raises(ValueError):
        broker.set_market_price("ES", price, observed_at=NOW)


def test_protocol_compliance() -> None:
    broker: Broker = MockBroker()
    assert isinstance(broker, MockBroker)


def test_reset_clears_only_price_fixture_state() -> None:
    broker = _broker_with_price()
    broker.reset()
    assert broker.get_market_price("ES") is None
    assert broker.get_all_orders() == []


def test_concurrent_price_updates_never_create_execution_state() -> None:
    broker = _broker_with_price()
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(
            lambda price: broker.set_market_price(
                "ES", price, observed_at=NOW + timedelta(seconds=price)
            ),
            range(1, 41),
        ))
    assert broker.get_market_price("ES") in {float(value) for value in range(1, 41)}
    assert broker.get_all_orders() == [] and broker.get_position("ES") is None
