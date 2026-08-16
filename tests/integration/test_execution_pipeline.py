from __future__ import annotations

from datetime import timedelta

from agicore.l5_action.broker_models import OrderStatus, OrderType
from agicore.l5_action.execution_service import (
    CanonicalL5ExecutionRequest,
    CanonicalL5LimitFillRequest,
)
from agicore.risk.exposure_models import ExecutionIntent, IntentSide
from tests.l5_secure_helpers import TEST_TIME, make_execution_service


def _market(suffix, side, quantity, price):
    return CanonicalL5ExecutionRequest(
        intent=ExecutionIntent(
            intent_id=f"intent-{suffix}", symbol="ES", side=side,
            quantity=quantity, estimated_price=price, timestamp=TEST_TIME,
        ),
        order_type=OrderType.MARKET, operation_id=f"operation-{suffix}",
        order_id=f"order-{suffix}", fill_id=f"fill-{suffix}",
        report_id=f"report-{suffix}", submitted_at=TEST_TIME,
        filled_at=TEST_TIME + timedelta(seconds=1),
    )


def test_round_trip_with_pnl() -> None:
    service = make_execution_service()
    service.execute(_market("buy", IntentSide.BUY, 10.0, 100.0))
    service.price_provider.set_market_price(
        "ES", 110.0, observed_at=TEST_TIME
    )
    service.execute(_market("sell-part", IntentSide.SELL, 4.0, 110.0))
    service.price_provider.set_market_price(
        "ES", 120.0, observed_at=TEST_TIME
    )
    service.execute(_market("sell-rest", IntentSide.SELL, 6.0, 120.0))
    position = service.state.positions["ES"]
    assert position.quantity == 0.0
    assert position.realized_pnl == 160.0
    assert service.state.risk_context.daily_realized_pnl == 160.0
    assert len(service.state.fills) == 3


def test_rejected_order_does_not_change_position() -> None:
    service = make_execution_service()
    before = service.state
    result = service.execute(_market("sell", IntentSide.SELL, 5.0, 100.0))
    assert result.status == OrderStatus.REJECTED
    assert service.state is before and service.state.fills == {}


def test_limit_placement_then_fresh_authorized_fill() -> None:
    service = make_execution_service()
    placement = CanonicalL5ExecutionRequest(
        intent=ExecutionIntent(
            intent_id="intent-place", symbol="ES", side=IntentSide.BUY,
            quantity=2.0, estimated_price=90.0, timestamp=TEST_TIME,
        ),
        order_type=OrderType.LIMIT, operation_id="operation-place",
        order_id="order-limit", report_id="report-place",
        submitted_at=TEST_TIME, limit_price=90.0,
    )
    assert service.execute(placement).status == OrderStatus.PENDING
    service.price_provider.set_market_price(
        "ES", 89.0, observed_at=TEST_TIME + timedelta(seconds=1)
    )
    fill_intent = ExecutionIntent(
        intent_id="intent-fill", symbol="ES", side=IntentSide.BUY,
        quantity=2.0, estimated_price=89.0,
        timestamp=TEST_TIME + timedelta(seconds=2),
    )
    result = service.fill_limit(CanonicalL5LimitFillRequest(
        intent=fill_intent, order_id="order-limit", eligibility_id="eligibility",
        operation_id="operation-fill", fill_id="fill-limit", report_id="report-fill",
        market_price=89.0, observed_at=TEST_TIME + timedelta(seconds=1),
        filled_at=TEST_TIME + timedelta(seconds=3),
    ))
    assert result.status == OrderStatus.FILLED
    assert len(service.consumptions) == 2
    assert service.state.positions["ES"].quantity == 2.0


def test_multi_symbol_isolation() -> None:
    service = make_execution_service()
    es = _market("es", IntentSide.BUY, 1.0, 100.0)
    nq = CanonicalL5ExecutionRequest(
        intent=ExecutionIntent(
            intent_id="intent-nq", symbol="NQ", side=IntentSide.BUY,
            quantity=2.0, estimated_price=200.0, timestamp=TEST_TIME,
        ),
        order_type=OrderType.MARKET, operation_id="operation-nq", order_id="order-nq",
        fill_id="fill-nq", report_id="report-nq", submitted_at=TEST_TIME, filled_at=TEST_TIME,
    )
    service.execute(es)
    service.execute(nq)
    assert service.state.positions["ES"].quantity == 1.0
    assert service.state.positions["NQ"].quantity == 2.0
