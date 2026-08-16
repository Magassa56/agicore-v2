"""Canonical, offline, risk-gated L5 execution service.

The service is the sole public L5 mutation entry.  It evaluates an explicit
``ExecutionIntent`` through ``RiskAuthorizationBoundary``, consumes an
allowed decision once, and publishes only through
``L5ExecutionTransactionStore``.  It does not own a second broker registry.
"""
from __future__ import annotations

import math
import threading
from dataclasses import dataclass
from datetime import datetime

from agicore.risk.exposure_models import ExecutionIntent, IntentSide
from agicore.risk.risk_execution_authorization import (
    RiskAuthorizationBoundary,
    RiskAuthorizationDecision,
)
from agicore.risk.risk_manager import RiskManager

from .broker_models import ExecutionReport, Order, OrderSide, OrderStatus, OrderType, Position
from .execution_transaction import (
    L5ExecutionAggregateState,
    L5ExecutionTransactionError,
    L5ExecutionTransactionStore,
)
from .price_provider import L5PriceObservation, L5PriceProvider, L5PriceProviderError


class L5RiskGateRequiredError(PermissionError):
    """An obsolete raw L5 mutation API was invoked."""

    code = "L5_RISK_GATE_REQUIRED"

    def __init__(self, message: str = "canonical L5 risk authorization is required") -> None:
        super().__init__(f"{self.code}: {message}")


class L5CanonicalExecutionError(ValueError):
    """Controlled failure of the canonical execution entry."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


def _identifier(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise L5CanonicalExecutionError("INVALID_EXECUTION_REQUEST", f"{name} must be non-blank")
    return value


def _time(value: object, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise L5CanonicalExecutionError("INVALID_EXECUTION_REQUEST", f"{name} must be timezone-aware")
    return value


def _price(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise L5CanonicalExecutionError("INVALID_EXECUTION_REQUEST", f"{name} must be finite and > 0")
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise L5CanonicalExecutionError("INVALID_EXECUTION_REQUEST", f"{name} must be finite and > 0")
    return result


def _intent(value: object) -> ExecutionIntent:
    if not isinstance(value, ExecutionIntent):
        raise L5CanonicalExecutionError("INVALID_EXECUTION_REQUEST", "intent must be ExecutionIntent")
    _identifier(value.intent_id, "intent_id")
    _identifier(value.symbol, "symbol")
    if not isinstance(value.side, IntentSide):
        raise L5CanonicalExecutionError("INVALID_EXECUTION_REQUEST", "intent.side is invalid")
    _time(value.timestamp, "intent.timestamp")
    _price(value.quantity, "intent.quantity")
    _price(value.estimated_price, "intent.estimated_price")
    return value


@dataclass(frozen=True)
class CanonicalL5ExecutionRequest:
    intent: ExecutionIntent
    order_type: OrderType
    operation_id: str
    order_id: str
    report_id: str
    submitted_at: datetime
    limit_price: float | None = None
    fill_id: str | None = None
    filled_at: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "intent", _intent(self.intent))
        if not isinstance(self.order_type, OrderType):
            raise L5CanonicalExecutionError("INVALID_EXECUTION_REQUEST", "order_type is invalid")
        for name in ("operation_id", "order_id", "report_id"):
            object.__setattr__(self, name, _identifier(getattr(self, name), name))
        object.__setattr__(self, "submitted_at", _time(self.submitted_at, "submitted_at"))
        if self.intent.timestamp > self.submitted_at:
            raise L5CanonicalExecutionError("INVALID_EXECUTION_REQUEST", "intent timestamp follows submission")
        if self.order_type == OrderType.MARKET:
            if self.limit_price is not None or self.fill_id is None or self.filled_at is None:
                raise L5CanonicalExecutionError("INVALID_EXECUTION_REQUEST", "MARKET identities/times are incomplete")
            object.__setattr__(self, "fill_id", _identifier(self.fill_id, "fill_id"))
            object.__setattr__(self, "filled_at", _time(self.filled_at, "filled_at"))
            if self.submitted_at > self.filled_at:
                raise L5CanonicalExecutionError("INVALID_EXECUTION_REQUEST", "MARKET fill precedes submission")
        else:
            object.__setattr__(self, "limit_price", _price(self.limit_price, "limit_price"))
            if float(self.intent.estimated_price) != self.limit_price:
                raise L5CanonicalExecutionError(
                    "AUTHORIZED_PRICE_MISMATCH",
                    "LIMIT placement intent price must equal limit_price",
                )
            if self.fill_id is not None or self.filled_at is not None:
                raise L5CanonicalExecutionError("INVALID_EXECUTION_REQUEST", "LIMIT placement cannot publish fill fields")


@dataclass(frozen=True)
class CanonicalL5LimitFillRequest:
    intent: ExecutionIntent
    order_id: str
    eligibility_id: str
    operation_id: str
    fill_id: str
    report_id: str
    market_price: float
    observed_at: datetime
    filled_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "intent", _intent(self.intent))
        for name in ("order_id", "eligibility_id", "operation_id", "fill_id", "report_id"):
            object.__setattr__(self, name, _identifier(getattr(self, name), name))
        object.__setattr__(self, "market_price", _price(self.market_price, "market_price"))
        object.__setattr__(self, "observed_at", _time(self.observed_at, "observed_at"))
        object.__setattr__(self, "filled_at", _time(self.filled_at, "filled_at"))
        if self.observed_at > self.intent.timestamp or self.intent.timestamp > self.filled_at:
            raise L5CanonicalExecutionError("INVALID_EXECUTION_REQUEST", "LIMIT fill chronology is invalid")
        if float(self.intent.estimated_price) != self.market_price:
            raise L5CanonicalExecutionError("AUTHORIZED_PRICE_MISMATCH", "fill intent price differs from market observation")


@dataclass(frozen=True)
class CanonicalL5CancellationRequest:
    order_id: str
    operation_id: str
    report_id: str
    cancelled_at: datetime

    def __post_init__(self) -> None:
        for name in ("order_id", "operation_id", "report_id"):
            object.__setattr__(self, name, _identifier(getattr(self, name), name))
        object.__setattr__(self, "cancelled_at", _time(self.cancelled_at, "cancelled_at"))


@dataclass(frozen=True)
class CanonicalL5ExecutionResult:
    order_id: str
    status: OrderStatus
    committed: bool
    message: str
    operation_id: str | None
    authorization_id: str | None
    decision_hash: str | None
    consumption_id: str | None
    consumption_hash: str | None
    aggregate_state_version: int
    aggregate_state_hash: str
    context_state_version: int
    context_state_hash: str
    provider_id: str
    risk_limits_hash: str | None
    price_provider_id: str | None = None
    price_version: int | None = None
    price_observation_hash: str | None = None
    execution_price: float | None = None
    violation_codes: tuple[str, ...] = ()


class ExecutionService:
    """Risk-gated authority for the canonical L5 path."""

    def __init__(
        self,
        transaction_store: L5ExecutionTransactionStore,
        risk_manager: RiskManager,
        price_provider: L5PriceProvider,
    ) -> None:
        if not isinstance(transaction_store, L5ExecutionTransactionStore):
            raise TypeError("transaction_store must be L5ExecutionTransactionStore")
        if not isinstance(risk_manager, RiskManager):
            raise TypeError("risk_manager must be RiskManager")
        if not isinstance(price_provider, L5PriceProvider):
            raise TypeError("price_provider must implement L5PriceProvider")
        if transaction_store.price_provider is not price_provider:
            raise ValueError("ExecutionService and transaction store must share one price provider")
        self._store = transaction_store
        self._price_provider = price_provider
        self._boundary = RiskAuthorizationBoundary(risk_manager, transaction_store.context_provider)
        self._lock = threading.RLock()

    @property
    def state(self) -> L5ExecutionAggregateState:
        return self._store.state

    @property
    def consumptions(self) -> tuple[object, ...]:
        return self._boundary.consumptions

    @property
    def price_provider(self) -> L5PriceProvider:
        return self._price_provider

    @property
    def broker(self) -> object:
        raise L5RiskGateRequiredError("mutable broker exposure is disabled")

    def execute(self, request: CanonicalL5ExecutionRequest) -> CanonicalL5ExecutionResult:
        if not isinstance(request, CanonicalL5ExecutionRequest):
            raise L5CanonicalExecutionError("INVALID_EXECUTION_REQUEST", "canonical request is required")
        with self._lock:
            self._require_unused_intent(request.intent.intent_id)
            return self._execute_locked(request)

    def _execute_locked(self, request: CanonicalL5ExecutionRequest) -> CanonicalL5ExecutionResult:
        observation = (
            self._price_snapshot(request.intent)
            if request.order_type == OrderType.MARKET
            else None
        )
        decision = self._authorize(request.intent)
        if not decision.allowed:
            return self._blocked_result(request.order_id, decision, observation)
        consumption = self._boundary.verify_for_execution(decision, request.intent)
        if request.order_type == OrderType.MARKET:
            transition = self._store.derive_fill_transition(
                intent=request.intent,
                fill_id=request.fill_id,
                fill_price=observation.price,
                filled_at=request.filled_at,
            )
            plan = self._store.prepare_market(
                boundary=self._boundary,
                intent=request.intent,
                consumption=consumption,
                operation_id=request.operation_id,
                order_id=request.order_id,
                fill_id=request.fill_id,
                report_id=request.report_id,
                submitted_at=request.submitted_at,
                fill_price=observation.price,
                filled_at=request.filled_at,
                transition=transition,
                price_observation=observation,
            )
        else:
            plan = self._store.prepare_limit_placement(
                boundary=self._boundary,
                intent=request.intent,
                consumption=consumption,
                operation_id=request.operation_id,
                order_id=request.order_id,
                report_id=request.report_id,
                limit_price=request.limit_price,
                submitted_at=request.submitted_at,
            )
        state = self._store.commit(plan, boundary=self._boundary)
        return self._committed_result(
            state,
            request.order_id,
            request.operation_id,
            decision,
            consumption,
            observation,
        )

    def fill_limit(self, request: CanonicalL5LimitFillRequest) -> CanonicalL5ExecutionResult:
        if not isinstance(request, CanonicalL5LimitFillRequest):
            raise L5CanonicalExecutionError("INVALID_EXECUTION_REQUEST", "canonical LIMIT fill request is required")
        with self._lock:
            self._require_unused_intent(request.intent.intent_id)
            return self._fill_limit_locked(request)

    def _fill_limit_locked(self, request: CanonicalL5LimitFillRequest) -> CanonicalL5ExecutionResult:
        observation = self._price_snapshot(request.intent)
        if (
            request.market_price != observation.price
            or request.observed_at != observation.observed_at
        ):
            raise L5CanonicalExecutionError(
                "AUTHORIZED_PRICE_MISMATCH",
                "LIMIT fill payload differs from authoritative price observation",
            )
        eligibility = self._store.evaluate_limit_eligibility(
            order_id=request.order_id,
            eligibility_id=request.eligibility_id,
            price_observation=observation,
        )
        if not eligibility.eligible:
            raise L5CanonicalExecutionError("LIMIT_NOT_ELIGIBLE", "limit price has not been crossed")
        decision = self._authorize(request.intent)
        if not decision.allowed:
            return self._blocked_result(request.order_id, decision, observation)
        consumption = self._boundary.verify_for_execution(decision, request.intent)
        transition = self._store.derive_fill_transition(
            intent=request.intent,
            fill_id=request.fill_id,
            fill_price=observation.price,
            filled_at=request.filled_at,
        )
        plan = self._store.prepare_limit_fill(
            boundary=self._boundary,
            intent=request.intent,
            consumption=consumption,
            eligibility=eligibility,
            operation_id=request.operation_id,
            fill_id=request.fill_id,
            report_id=request.report_id,
            filled_at=request.filled_at,
            transition=transition,
            price_observation=observation,
        )
        state = self._store.commit(plan, boundary=self._boundary)
        return self._committed_result(
            state,
            request.order_id,
            request.operation_id,
            decision,
            consumption,
            observation,
        )

    def cancel_limit(self, request: CanonicalL5CancellationRequest) -> CanonicalL5ExecutionResult:
        if not isinstance(request, CanonicalL5CancellationRequest):
            raise L5CanonicalExecutionError("INVALID_EXECUTION_REQUEST", "canonical cancellation request is required")
        with self._lock:
            state = self._store.cancel_limit(
                operation_id=request.operation_id,
                order_id=request.order_id,
                report_id=request.report_id,
                cancelled_at=request.cancelled_at,
            )
        return CanonicalL5ExecutionResult(
            order_id=request.order_id,
            status=OrderStatus.CANCELLED,
            committed=True,
            message="limit order cancelled",
            operation_id=request.operation_id,
            authorization_id=None,
            decision_hash=None,
            consumption_id=None,
            consumption_hash=None,
            aggregate_state_version=state.state_version,
            aggregate_state_hash=state.state_hash,
            context_state_version=state.risk_context.state_version,
            context_state_hash=state.risk_context.state_hash,
            provider_id=state.risk_context.provider_id,
            risk_limits_hash=None,
        )

    def _authorize(self, intent: ExecutionIntent) -> RiskAuthorizationDecision:
        context = self._store.state.risk_context
        return self._boundary.authorize(
            intent,
            expected_provider_id=context.provider_id,
            expected_context_state_version=context.state_version,
            expected_context_state_hash=context.state_hash,
        )

    def _price_snapshot(self, intent: ExecutionIntent) -> L5PriceObservation:
        try:
            observation = self._price_provider.snapshot(intent.symbol)
        except L5PriceProviderError as exc:
            raise L5CanonicalExecutionError(exc.code, exc.message) from exc
        except Exception as exc:
            raise L5CanonicalExecutionError(
                "PRICE_PROVIDER_ERROR",
                "authoritative price provider failed",
            ) from exc
        if observation.price != float(intent.estimated_price):
            raise L5CanonicalExecutionError(
                "AUTHORIZED_PRICE_MISMATCH",
                "intent price differs from authoritative price observation",
            )
        if observation.observed_at > intent.timestamp:
            raise L5CanonicalExecutionError(
                "INVALID_EXECUTION_REQUEST",
                "intent timestamp precedes authoritative price observation",
            )
        return observation

    def _require_unused_intent(self, intent_id: str) -> None:
        if any(record.intent_id == intent_id for record in self._boundary.consumptions):
            raise L5CanonicalExecutionError("INTENT_ALREADY_CONSUMED", "intent_id authorization is already consumed")
        for event in self._store.state.execution_journal[1:]:
            operation_inputs = event.payload.get("operation_inputs")
            if not isinstance(operation_inputs, dict) and not hasattr(operation_inputs, "get"):
                continue
            intent = operation_inputs.get("intent")
            if hasattr(intent, "get") and intent.get("intent_id") == intent_id:
                raise L5CanonicalExecutionError("DUPLICATE_INTENT", "intent_id already produced L5 state")

    def _blocked_result(
        self,
        order_id: str,
        decision: RiskAuthorizationDecision,
        observation: L5PriceObservation | None,
    ) -> CanonicalL5ExecutionResult:
        state = self._store.state
        codes = (*decision.guard_codes, *(item.code for item in decision.violations))
        return CanonicalL5ExecutionResult(
            order_id=order_id,
            status=OrderStatus.REJECTED,
            committed=False,
            message="risk authorization rejected",
            operation_id=None,
            authorization_id=decision.authorization_id,
            decision_hash=decision.decision_hash,
            consumption_id=None,
            consumption_hash=None,
            aggregate_state_version=state.state_version,
            aggregate_state_hash=state.state_hash,
            context_state_version=state.risk_context.state_version,
            context_state_hash=state.risk_context.state_hash,
            provider_id=decision.provider_id,
            risk_limits_hash=decision.risk_limits_hash,
            price_provider_id=(observation.provider_id if observation else None),
            price_version=(observation.price_version if observation else None),
            price_observation_hash=(observation.observation_hash if observation else None),
            violation_codes=tuple(codes),
        )

    @staticmethod
    def _committed_result(
        state,
        order_id,
        operation_id,
        decision,
        consumption,
        observation,
    ) -> CanonicalL5ExecutionResult:
        order = state.orders[order_id]
        return CanonicalL5ExecutionResult(
            order_id=order_id,
            status=order.status,
            committed=True,
            message="transaction committed",
            operation_id=operation_id,
            authorization_id=decision.authorization_id,
            decision_hash=decision.decision_hash,
            consumption_id=consumption.consumption_id,
            consumption_hash=consumption.consumption_hash,
            aggregate_state_version=state.state_version,
            aggregate_state_hash=state.state_hash,
            context_state_version=state.risk_context.state_version,
            context_state_hash=state.risk_context.state_hash,
            provider_id=decision.provider_id,
            risk_limits_hash=decision.risk_limits_hash,
            price_provider_id=(observation.provider_id if observation else None),
            price_version=(observation.price_version if observation else None),
            price_observation_hash=(observation.observation_hash if observation else None),
            execution_price=order.filled_price,
        )

    # Historical raw mutation APIs are retained only as fail-closed sentinels.
    def submit(self, request: object) -> ExecutionReport:
        raise L5RiskGateRequiredError()

    def submit_market_order(self, *args: object, **kwargs: object) -> ExecutionReport:
        raise L5RiskGateRequiredError()

    def submit_limit_order(self, *args: object, **kwargs: object) -> ExecutionReport:
        raise L5RiskGateRequiredError()

    def cancel(self, order_id: str) -> ExecutionReport:
        raise L5RiskGateRequiredError("canonical cancellation request is required")

    def get_position(self, symbol: str) -> Position | None:
        position = self._store.state.positions.get(symbol)
        if position is None or position.quantity == 0:
            return None
        fill_times = [
            fill.filled_at
            for fill in self._store.state.fills.values()
            if fill.symbol == symbol
        ]
        if not fill_times:
            raise L5CanonicalExecutionError("INVALID_AGGREGATE_STATE", "position lacks explicit update time")
        latest = max(fill_times)
        return Position(
            symbol=symbol,
            quantity=position.quantity,
            avg_entry_price=position.avg_entry_price,
            realized_pnl=position.realized_pnl,
            last_update=latest,
        )

    def get_open_orders(self) -> list[Order]:
        return [
            Order(
                order_id=order.order_id,
                client_order_id=None,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                order_type=order.order_type,
                limit_price=order.limit_price,
                status=order.status,
                filled_price=order.filled_price,
                filled_quantity=order.quantity if order.status == OrderStatus.FILLED else None,
                filled_at=order.filled_at,
                cancelled_at=order.cancelled_at,
                created_at=order.submitted_at,
            )
            for order in self._store.state.orders.values()
            if order.status == OrderStatus.PENDING
        ]


__all__ = [
    "CanonicalL5CancellationRequest",
    "CanonicalL5ExecutionRequest",
    "CanonicalL5ExecutionResult",
    "CanonicalL5LimitFillRequest",
    "ExecutionService",
    "L5CanonicalExecutionError",
    "L5RiskGateRequiredError",
]
