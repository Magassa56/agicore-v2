"""ExecutionAgent — bridges the broker mock layer to the AGIcore Runtime.

A ``TaskHandler`` for ``execution.order`` tasks. Validates the task
payload, submits the order through ``ExecutionService`` (which today wraps
``MockBroker`` and tomorrow will wrap NinjaTrader / Alpaca adapters),
persists a domain event in LTM, emits the same event on the EventBus,
and returns structured feedback.

Fully offline. No broker connection. No live execution. The agent only
talks to the ``ExecutionService`` instance it was given at construction.

Task payload contract
---------------------
- ``symbol``           : str  (required, 1-32 chars)
- ``side``             : str  (required, "BUY" or "SELL")
- ``quantity``         : float (required, > 0)
- ``order_type``       : str  (default "MARKET", or "LIMIT")
- ``limit_price``      : float (required iff order_type == "LIMIT")
- ``client_order_id``  : str  (optional)
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog

from agicore.core.events import EventBus
from agicore.l2_memory.schemas.task import TaskRead
from agicore.l2_memory.services.memory_service import MemoryService
from agicore.l5_action.broker_models import (
    InvalidOrderError,
    OrderRequest,
    OrderSide,
    OrderType,
)
from agicore.l5_action.execution_service import ExecutionService

logger = structlog.get_logger(__name__)


# Canonical identifiers
TASK_TYPE_ORDER: str = "execution.order"
EVT_ORDER_PROCESSED: str = "agent.execution.order.processed"
AGENT_ID: str = "execution_agent"


class ExecutionAgent:
    """``TaskHandler`` for ``execution.order`` tasks.

    Parameters
    ----------
    execution_service : ExecutionService
        Required. The service is broker-agnostic — Phase 7C ships a
        ``MockBroker`` ; future phases plug a real adapter.
    memory : MemoryService
        Required. Persists the domain event in LTM.
    event_bus : EventBus | None
        Optional. When provided, also publishes ``EVT_ORDER_PROCESSED``.

    Notes
    -----
    Final order statuses (FILLED / REJECTED / CANCELLED / PENDING) are
    NOT treated as task failures — they are valid outcomes of a successful
    submission. The task is FAILED only on payload validation errors.
    """

    def __init__(
        self,
        execution_service: ExecutionService,
        memory: MemoryService,
        event_bus: EventBus | None = None,
    ) -> None:
        self._svc = execution_service
        self._memory = memory
        self._bus = event_bus
        self._processed_count = 0

    @property
    def processed_count(self) -> int:
        return self._processed_count

    @property
    def agent_id(self) -> str:
        return AGENT_ID

    def __call__(self, task: TaskRead) -> dict[str, Any]:
        started_at = datetime.now(timezone.utc)
        t0 = time.monotonic()
        payload = dict(task.payload or {})

        # 1. Validate + parse payload (raises ValueError → task FAILED)
        request = self._build_order_request(payload)

        # 2. Submit to ExecutionService (never raises on REJECTED/PENDING)
        report = self._svc.submit(request)

        # 3. Look up post-execution position for realized PnL
        position = self._svc.get_position(request.symbol)
        realized_pnl = position.realized_pnl if position is not None else 0.0
        position_quantity = position.quantity if position is not None else 0.0

        runtime_duration_ms = max(round((time.monotonic() - t0) * 1000.0, 3), 0.001)

        feedback: dict[str, Any] = {
            "order_id": report.order_id,
            "symbol": request.symbol,
            "side": request.side.value,
            "quantity": request.quantity,
            "order_status": report.status.value,
            "fill_price": report.filled_price,
            "filled_quantity": report.filled_quantity,
            "realized_pnl": realized_pnl,
            "position_quantity": position_quantity,
            "runtime_duration_ms": runtime_duration_ms,
            "order_type": request.order_type.value,
            "limit_price": request.limit_price,
            "broker_message": report.message,
            "task_id": task.id,
            "agent_id": AGENT_ID,
            "started_at": started_at.isoformat(),
        }

        # 4. Persist event in LTM
        self._memory.create_event(
            EVT_ORDER_PROCESSED,
            task_id=task.id,
            agent_id=AGENT_ID,
            payload=dict(feedback),
        )

        # 5. Emit on bus
        if self._bus is not None:
            self._bus.emit(
                EVT_ORDER_PROCESSED,
                task_id=task.id,
                order_id=feedback["order_id"],
                symbol=feedback["symbol"],
                side=feedback["side"],
                quantity=feedback["quantity"],
                order_status=feedback["order_status"],
                fill_price=feedback["fill_price"],
                filled_quantity=feedback["filled_quantity"],
                realized_pnl=feedback["realized_pnl"],
                broker_message=feedback["broker_message"],
            )

        self._processed_count += 1
        feedback["processed_count"] = self._processed_count

        logger.info(
            "execution_agent.order_processed",
            task_id=task.id,
            order_id=feedback["order_id"],
            symbol=feedback["symbol"],
            side=feedback["side"],
            status=feedback["order_status"],
            fill_price=feedback["fill_price"],
            duration_ms=runtime_duration_ms,
        )
        return feedback

    # ------------------------------------------------------------------ Validation
    @staticmethod
    def _build_order_request(payload: dict[str, Any]) -> OrderRequest:
        # Required fields
        symbol = payload.get("symbol")
        side_raw = payload.get("side")
        quantity = payload.get("quantity")

        missing: list[str] = []
        if not symbol:
            missing.append("symbol")
        if side_raw is None:
            missing.append("side")
        if quantity is None:
            missing.append("quantity")
        if missing:
            raise InvalidOrderError(
                f"missing required payload fields: {missing}"
            )

        # Side enum
        try:
            side = OrderSide(str(side_raw).upper())
        except ValueError as exc:
            raise InvalidOrderError(
                f"invalid side={side_raw!r}, must be one of {[s.value for s in OrderSide]}"
            ) from exc

        # Type enum (default MARKET)
        order_type_raw = payload.get("order_type", OrderType.MARKET.value)
        try:
            order_type = OrderType(str(order_type_raw).upper())
        except ValueError as exc:
            raise InvalidOrderError(
                f"invalid order_type={order_type_raw!r}, must be one of {[o.value for o in OrderType]}"
            ) from exc

        limit_price = payload.get("limit_price")
        if order_type == OrderType.LIMIT and limit_price is None:
            raise InvalidOrderError("limit_price is required for LIMIT orders")
        if order_type == OrderType.MARKET and limit_price is not None:
            raise InvalidOrderError("limit_price must be omitted for MARKET orders")

        # Build the validated DTO (extra checks via Pydantic)
        return OrderRequest(
            symbol=str(symbol),
            side=side,
            quantity=float(quantity),
            order_type=order_type,
            limit_price=float(limit_price) if limit_price is not None else None,
            client_order_id=payload.get("client_order_id"),
        )


__all__ = [
    "ExecutionAgent",
    "TASK_TYPE_ORDER",
    "EVT_ORDER_PROCESSED",
    "AGENT_ID",
]
