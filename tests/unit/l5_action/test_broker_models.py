"""Unit tests for broker_models DTOs and enums."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from agicore.l5_action.broker_models import (
    ExecutionReport,
    Order,
    OrderRequest,
    OrderSide,
    OrderStatus,
    OrderType,
    Position,
    utcnow,
)


def test_enum_values() -> None:
    assert OrderSide.BUY.value == "BUY"
    assert OrderSide.SELL.value == "SELL"
    assert OrderType.MARKET.value == "MARKET"
    assert OrderType.LIMIT.value == "LIMIT"
    assert OrderStatus.PENDING.value == "PENDING"
    assert OrderStatus.FILLED.value == "FILLED"
    assert OrderStatus.CANCELLED.value == "CANCELLED"
    assert OrderStatus.REJECTED.value == "REJECTED"


def test_order_request_market_basic() -> None:
    r = OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=2.0)
    assert r.order_type == OrderType.MARKET
    assert r.limit_price is None


def test_order_request_limit_requires_price() -> None:
    with pytest.raises(ValidationError):
        OrderRequest(
            symbol="ES", side=OrderSide.BUY, quantity=1.0,
            order_type=OrderType.LIMIT,  # missing limit_price
        )


def test_order_request_market_rejects_limit_price() -> None:
    with pytest.raises(ValidationError):
        OrderRequest(
            symbol="ES", side=OrderSide.BUY, quantity=1.0,
            order_type=OrderType.MARKET, limit_price=100.0,
        )


def test_order_request_quantity_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=0)
    with pytest.raises(ValidationError):
        OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=-1)


def test_order_minimal() -> None:
    o = Order(
        order_id="ord-1", symbol="ES", side=OrderSide.BUY,
        quantity=1.0, order_type=OrderType.MARKET,
        created_at=utcnow(),
    )
    assert o.status == OrderStatus.PENDING
    assert o.filled_price is None


def test_position_long_only() -> None:
    Position(
        symbol="ES", quantity=5.0, avg_entry_price=100.0,
        last_update=utcnow(),
    )
    with pytest.raises(ValidationError):
        Position(
            symbol="ES", quantity=-1, avg_entry_price=100.0,
            last_update=utcnow(),
        )


def test_execution_report_basic() -> None:
    r = ExecutionReport(
        order_id="ord-1", status=OrderStatus.FILLED,
        filled_price=100.0, filled_quantity=1.0,
        timestamp=utcnow(), message="ok",
    )
    assert r.status == OrderStatus.FILLED


def test_utcnow_returns_aware() -> None:
    n = utcnow()
    assert n.tzinfo is not None
