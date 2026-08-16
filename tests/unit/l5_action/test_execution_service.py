from __future__ import annotations

from datetime import timedelta

import pytest

from agicore.core.events import EventBus
from agicore.l5_action.broker_models import OrderRequest, OrderSide, OrderStatus, OrderType
from agicore.l5_action.execution_service import (
    CanonicalL5CancellationRequest,
    CanonicalL5ExecutionRequest,
    L5CanonicalExecutionError,
    L5RiskGateRequiredError,
)
from agicore.risk.exposure_models import (
    EVT_RISK_BLOCKED,
    EVT_RISK_PASSED,
    ExecutionIntent,
    IntentSide,
)
from tests.l5_secure_helpers import TEST_TIME, make_execution_service


def _request(*, suffix="one", order_type=OrderType.MARKET, limit_price=None):
    authorized_price = limit_price if order_type == OrderType.LIMIT else 100.0
    return CanonicalL5ExecutionRequest(
        intent=ExecutionIntent(
            intent_id=f"intent-{suffix}", symbol="ES", side=IntentSide.BUY,
            quantity=1.0, estimated_price=authorized_price, timestamp=TEST_TIME,
        ),
        order_type=order_type, operation_id=f"operation-{suffix}",
        order_id=f"order-{suffix}", report_id=f"report-{suffix}",
        submitted_at=TEST_TIME, limit_price=limit_price,
        fill_id=f"fill-{suffix}" if order_type == OrderType.MARKET else None,
        filled_at=TEST_TIME if order_type == OrderType.MARKET else None,
    )


def test_submit_market_buy_helper() -> None:
    svc = make_execution_service()
    result = svc.execute(_request())
    assert result.status == OrderStatus.FILLED and result.committed


def test_submit_limit_helper() -> None:
    svc = make_execution_service()
    result = svc.execute(_request(order_type=OrderType.LIMIT, limit_price=90.0))
    assert result.status == OrderStatus.PENDING and svc.state.fills == {}


def test_submit_arbitrary_request() -> None:
    svc = make_execution_service()
    with pytest.raises(L5RiskGateRequiredError):
        svc.submit(OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=1.0))
    assert svc.state.orders == {}


def test_cancel_via_service() -> None:
    svc = make_execution_service()
    svc.execute(_request(order_type=OrderType.LIMIT, limit_price=90.0))
    result = svc.cancel_limit(CanonicalL5CancellationRequest(
        order_id="order-one", operation_id="operation-cancel",
        report_id="report-cancel", cancelled_at=TEST_TIME + timedelta(seconds=1),
    ))
    assert result.status == OrderStatus.CANCELLED


def test_get_position_via_service() -> None:
    svc = make_execution_service()
    svc.execute(_request())
    position = svc.get_position("ES")
    assert position is not None and position.quantity == 1.0


def test_position_last_update_comes_only_from_fill() -> None:
    svc = make_execution_service()
    svc.execute(_request(suffix="filled"))
    assert svc.get_position("ES").last_update == TEST_TIME

    later = TEST_TIME + timedelta(seconds=5)
    svc.execute(CanonicalL5ExecutionRequest(
        intent=ExecutionIntent(
            intent_id="intent-pending", symbol="ES", side=IntentSide.BUY,
            quantity=1.0, estimated_price=90.0, timestamp=later,
        ),
        order_type=OrderType.LIMIT, operation_id="operation-pending",
        order_id="order-pending", report_id="report-pending",
        submitted_at=later, limit_price=90.0,
    ))
    svc.cancel_limit(CanonicalL5CancellationRequest(
        order_id="order-pending", operation_id="operation-cancel-pending",
        report_id="report-cancel-pending",
        cancelled_at=later + timedelta(seconds=1),
    ))
    assert svc.get_position("ES").last_update == TEST_TIME


def test_get_open_orders_via_service() -> None:
    svc = make_execution_service()
    svc.execute(_request(order_type=OrderType.LIMIT, limit_price=90.0))
    assert [item.order_id for item in svc.get_open_orders()] == ["order-one"]


def test_broker_property_exposes_underlying() -> None:
    svc = make_execution_service()
    with pytest.raises(L5RiskGateRequiredError):
        _ = svc.broker


@pytest.mark.parametrize("quantity", [0.0, -1.0, float("nan"), float("inf")])
def test_invalid_quantity_is_rejected(quantity) -> None:
    intent = ExecutionIntent.model_construct(
        intent_id="intent-invalid-quantity", symbol="ES", side=IntentSide.BUY,
        quantity=quantity, estimated_price=100.0, timestamp=TEST_TIME,
    )
    with pytest.raises((ValueError, L5CanonicalExecutionError)):
        CanonicalL5ExecutionRequest(
            intent=intent, order_type=OrderType.MARKET,
            operation_id="operation-invalid-quantity",
            order_id="order-invalid-quantity", report_id="report-invalid-quantity",
            submitted_at=TEST_TIME, fill_id="fill-invalid-quantity", filled_at=TEST_TIME,
        )


@pytest.mark.parametrize("price", [0.0, -1.0, float("nan"), float("inf")])
def test_invalid_price_is_rejected(price) -> None:
    intent = ExecutionIntent.model_construct(
        intent_id="intent-invalid-price", symbol="ES", side=IntentSide.BUY,
        quantity=1.0, estimated_price=price, timestamp=TEST_TIME,
    )
    with pytest.raises((ValueError, L5CanonicalExecutionError)):
        CanonicalL5ExecutionRequest(
            intent=intent, order_type=OrderType.MARKET,
            operation_id="operation-invalid-price", order_id="order-invalid-price",
            report_id="report-invalid-price", submitted_at=TEST_TIME,
            fill_id="fill-invalid-price", filled_at=TEST_TIME,
        )


def test_market_with_limit_fields_and_limit_without_price_are_rejected() -> None:
    with pytest.raises(L5CanonicalExecutionError):
        CanonicalL5ExecutionRequest(**{**_request().__dict__, "limit_price": 100.0})
    with pytest.raises(L5CanonicalExecutionError):
        CanonicalL5ExecutionRequest(
            intent=ExecutionIntent(
                intent_id="intent-limit-no-price", symbol="ES", side=IntentSide.BUY,
                quantity=1.0, estimated_price=100.0, timestamp=TEST_TIME,
            ),
            order_type=OrderType.LIMIT,
            operation_id="operation-limit-no-price",
            order_id="order-limit-no-price",
            report_id="report-limit-no-price",
            submitted_at=TEST_TIME,
            limit_price=None,
        )


def test_invalid_side_and_order_type_are_rejected() -> None:
    invalid_intent = ExecutionIntent.model_construct(
        intent_id="intent-invalid-side", symbol="ES", side="SIDEWAYS",
        quantity=1.0, estimated_price=100.0, timestamp=TEST_TIME,
    )
    with pytest.raises((ValueError, L5CanonicalExecutionError)):
        CanonicalL5ExecutionRequest(
            intent=invalid_intent, order_type=OrderType.MARKET,
            operation_id="operation-invalid-side", order_id="order-invalid-side",
            report_id="report-invalid-side", submitted_at=TEST_TIME,
            fill_id="fill-invalid-side", filled_at=TEST_TIME,
        )
    with pytest.raises(L5CanonicalExecutionError):
        CanonicalL5ExecutionRequest(**{**_request().__dict__, "order_type": "MARKET"})


def test_risk_passed_and_blocked_events_are_emitted_when_bus_is_configured() -> None:
    bus = EventBus()
    passed = []
    blocked = []
    bus.subscribe(EVT_RISK_PASSED, passed.append)
    bus.subscribe(EVT_RISK_BLOCKED, blocked.append)
    service = make_execution_service(max_position_size=1.0, event_bus=bus)
    assert service.execute(_request(suffix="risk-passed")).committed

    rejected = CanonicalL5ExecutionRequest(
        intent=ExecutionIntent(
            intent_id="intent-risk-blocked", symbol="ES", side=IntentSide.BUY,
            quantity=1.0, estimated_price=100.0, timestamp=TEST_TIME,
        ),
        order_type=OrderType.MARKET,
        operation_id="operation-risk-blocked", order_id="order-risk-blocked",
        report_id="report-risk-blocked", submitted_at=TEST_TIME,
        fill_id="fill-risk-blocked", filled_at=TEST_TIME,
    )
    assert service.execute(rejected).status == OrderStatus.REJECTED
    assert len(passed) == len(blocked) == 1
    assert passed[0].payload["intent_id"] == "intent-risk-passed"
    assert blocked[0].payload["intent_id"] == "intent-risk-blocked"
    assert "POSITION_SIZE_EXCEEDED" in blocked[0].payload["violation_codes"]
