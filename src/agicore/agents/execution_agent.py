"""Execution agent for explicit, canonical, risk-gated L5 tasks."""
from __future__ import annotations

import time
from datetime import datetime
from typing import Any

import structlog

from agicore.core.events import EventBus
from agicore.l2_memory.schemas.task import TaskRead
from agicore.l2_memory.services.memory_service import MemoryService
from agicore.l5_action.broker_models import OrderSide, OrderType
from agicore.l5_action.execution_service import (
    CanonicalL5ExecutionRequest,
    ExecutionService,
    L5CanonicalExecutionError,
)
from agicore.risk.exposure_models import ExecutionIntent, IntentSide

logger = structlog.get_logger(__name__)

TASK_TYPE_ORDER = "execution.order"
EVT_ORDER_PROCESSED = "agent.execution.order.processed"
AGENT_ID = "execution_agent"


class ExecutionAgent:
    """Validate an explicit TaskQueue proposal and invoke only ExecutionService."""

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
        t0 = time.monotonic()
        request = self._build_execution_request(dict(task.payload or {}))
        result = self._svc.execute(request)
        position = self._svc.state.positions.get(request.intent.symbol)
        runtime_duration_ms = max(round((time.monotonic() - t0) * 1000.0, 3), 0.001)
        feedback: dict[str, Any] = {
            "order_id": result.order_id,
            "symbol": request.intent.symbol,
            "side": request.intent.side.value,
            "quantity": request.intent.quantity,
            "order_status": result.status.value,
            "committed": result.committed,
            "fill_price": (
                result.execution_price
                if result.status.value == "FILLED"
                else None
            ),
            "filled_quantity": (
                request.intent.quantity if result.status.value == "FILLED" else None
            ),
            "realized_pnl": position.realized_pnl if position else 0.0,
            "position_quantity": position.quantity if position else 0.0,
            "runtime_duration_ms": runtime_duration_ms,
            "order_type": request.order_type.value,
            "limit_price": request.limit_price,
            "broker_message": result.message,
            "violation_codes": list(result.violation_codes),
            "intent_id": request.intent.intent_id,
            "operation_id": result.operation_id,
            "authorization_id": result.authorization_id,
            "decision_hash": result.decision_hash,
            "consumption_id": result.consumption_id,
            "consumption_hash": result.consumption_hash,
            "aggregate_state_version": result.aggregate_state_version,
            "aggregate_state_hash": result.aggregate_state_hash,
            "context_state_version": result.context_state_version,
            "context_state_hash": result.context_state_hash,
            "provider_id": result.provider_id,
            "risk_limits_hash": result.risk_limits_hash,
            "price_provider_id": result.price_provider_id,
            "price_version": result.price_version,
            "price_observation_hash": result.price_observation_hash,
            "task_id": task.id,
            "agent_id": AGENT_ID,
            "started_at": request.intent.timestamp.isoformat(),
        }
        self._memory.create_event(
            EVT_ORDER_PROCESSED,
            task_id=task.id,
            agent_id=AGENT_ID,
            payload=dict(feedback),
        )
        if self._bus is not None:
            self._bus.emit(EVT_ORDER_PROCESSED, **dict(feedback))
        self._processed_count += 1
        feedback["processed_count"] = self._processed_count
        logger.info(
            "execution_agent.order_processed",
            task_id=task.id,
            intent_id=request.intent.intent_id,
            order_id=result.order_id,
            status=result.status.value,
            committed=result.committed,
        )
        return feedback

    @staticmethod
    def _build_execution_request(payload: dict[str, Any]) -> CanonicalL5ExecutionRequest:
        required = (
            "intent_id",
            "symbol",
            "side",
            "quantity",
            "estimated_price",
            "timestamp",
            "order_type",
            "operation_id",
            "order_id",
            "report_id",
            "submitted_at",
        )
        missing = [name for name in required if name not in payload]
        if missing:
            raise L5CanonicalExecutionError(
                "INVALID_TASK_PAYLOAD",
                f"missing required payload fields: {missing}",
            )
        try:
            side = IntentSide(str(payload["side"]).upper())
            order_type = OrderType(str(payload["order_type"]).upper())
            if order_type == OrderType.MARKET:
                missing_market = [name for name in ("fill_id", "filled_at") if name not in payload]
                if missing_market:
                    raise L5CanonicalExecutionError(
                        "INVALID_TASK_PAYLOAD",
                        f"missing required MARKET payload fields: {missing_market}",
                    )
            timestamp = ExecutionAgent._parse_time(payload["timestamp"], "timestamp")
            submitted_at = ExecutionAgent._parse_time(payload["submitted_at"], "submitted_at")
            intent = ExecutionIntent(
                intent_id=payload["intent_id"],
                symbol=payload["symbol"],
                side=side,
                quantity=payload["quantity"],
                estimated_price=payload["estimated_price"],
                timestamp=timestamp,
            )
            return CanonicalL5ExecutionRequest(
                intent=intent,
                order_type=order_type,
                operation_id=payload["operation_id"],
                order_id=payload["order_id"],
                report_id=payload["report_id"],
                submitted_at=submitted_at,
                limit_price=payload.get("limit_price"),
                fill_id=payload.get("fill_id"),
                filled_at=(
                    ExecutionAgent._parse_time(payload["filled_at"], "filled_at")
                    if "filled_at" in payload
                    else None
                ),
            )
        except L5CanonicalExecutionError:
            raise
        except Exception as exc:
            raise L5CanonicalExecutionError("INVALID_TASK_PAYLOAD", "task payload is invalid") from exc

    @staticmethod
    def _parse_time(value: object, name: str) -> datetime:
        if isinstance(value, datetime):
            parsed = value
        elif isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value)
            except ValueError as exc:
                raise L5CanonicalExecutionError("INVALID_TASK_PAYLOAD", f"{name} is invalid") from exc
        else:
            raise L5CanonicalExecutionError("INVALID_TASK_PAYLOAD", f"{name} is invalid")
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise L5CanonicalExecutionError("INVALID_TASK_PAYLOAD", f"{name} must be timezone-aware")
        return parsed


__all__ = ["ExecutionAgent", "TASK_TYPE_ORDER", "EVT_ORDER_PROCESSED", "AGENT_ID"]
