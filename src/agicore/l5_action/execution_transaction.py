"""Deterministic aggregate authority for canonical risk-gated L5 execution.

Economic state and local result-delivery state are published through one
immutable authority assignment.  Their hashes remain separate so an outbox
acknowledgement cannot alter the committed economic transaction identity.
"""
from __future__ import annotations

import hashlib
import json
import math
import threading
from collections.abc import Iterator, Mapping
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass, replace
from datetime import datetime
from types import MappingProxyType

from agicore.risk.exposure_models import (
    ExecutionIntent,
    ExposureSnapshot,
    IntentSide,
    RiskLimits,
    SymbolExposure,
)
from agicore.risk.risk_execution_authorization import (
    RiskAuthorizationBoundary,
    RiskAuthorizationConsumption,
    RiskAuthorizationDecision,
    RiskAuthorizationError,
    verify_blocked_decision_evidence,
)
from agicore.risk.risk_execution_context import (
    FillTransition,
    RiskContextError,
    RiskExecutionContext,
    RiskExecutionJournalEvent,
    replay_journal,
    validate_journal,
)
from agicore.risk.risk_manager import RiskManager

from .broker_models import OrderSide, OrderStatus, OrderType
from .execution_outbox import (
    L5ExecutionDeliveryAcknowledgement,
    L5ExecutionDeliveryError,
    L5ExecutionDeliveryEvent,
    L5ExecutionDeliveryState,
    L5ExecutionInboxEvent,
    L5ExecutionInboxReceipt,
    L5ExecutionInboxState,
    L5ExecutionOutcome,
    L5ExecutionOutcomeInbox,
    L5ExecutionOutcomeSpec,
    replay_delivery_journal,
    replay_inbox_journal,
)
from .price_provider import L5PriceObservation, L5PriceProvider, L5PriceProviderError

TRANSACTION_SCHEMA_VERSION = "l5-execution-transaction/1.1"
PLAN_SCHEMA_VERSION = "l5-execution-plan/1.1"
ELIGIBILITY_SCHEMA_VERSION = "l5-limit-eligibility/1.1"
GENESIS_TRANSACTION_HASH = hashlib.sha256(
    b'{"schema_version":"l5-execution-transaction/1.1","type":"GENESIS"}'
).hexdigest()
OPERATION_KINDS = frozenset({"MARKET", "LIMIT_PLACEMENT", "LIMIT_FILL"})
_AUTO_OUTCOME = object()
TRANSACTION_EVENT_TYPES = frozenset(
    {
        "AGGREGATE_INITIALIZED",
        "MARKET_COMMITTED",
        "LIMIT_PLACED",
        "LIMIT_FILLED",
        "LIMIT_CANCELLED",
    }
)


class L5ExecutionTransactionError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


def _canonical_json(value: object) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", "value is not canonically serializable") from exc


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _is_hash(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def _identifier(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", f"{name} must be non-blank")
    return value


def _number(value: object, name: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", f"{name} must be finite")
    result = float(value)
    if (positive and result <= 0) or (not positive and result < 0):
        comparator = "> 0" if positive else ">= 0"
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", f"{name} must be {comparator}")
    return result


def _explicit_time(value: object, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", f"{name} must be timezone-aware")
    return value


def _parse_explicit_time(value: object, name: str) -> datetime:
    if not isinstance(value, str):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", f"{name} must be an ISO timestamp")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", f"{name} is invalid") from exc
    return _explicit_time(parsed, name)


def _freeze_json(value: object) -> object:
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, nested in value.items():
            if not isinstance(key, str):
                raise L5ExecutionTransactionError(
                    "INVALID_TRANSACTION_DATA",
                    "payload mapping keys must be strings",
                )
            frozen[key] = _freeze_json(nested)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(item) for item in value)
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", "payload must contain canonical JSON values")


def _thaw_json(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _thaw_json(nested) for key, nested in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


def _intent_payload(intent: ExecutionIntent) -> dict[str, object]:
    if not isinstance(intent, ExecutionIntent):
        raise L5ExecutionTransactionError("INVALID_INTENT", "intent must be ExecutionIntent")
    if not isinstance(intent.side, IntentSide):
        raise L5ExecutionTransactionError("INVALID_INTENT", "intent side is invalid")
    return {
        "intent_id": _identifier(intent.intent_id, "intent_id"),
        "symbol": _identifier(intent.symbol, "symbol"),
        "side": intent.side.value,
        "quantity": _number(intent.quantity, "quantity", positive=True),
        "estimated_price": _number(intent.estimated_price, "estimated_price", positive=True),
        "timestamp": _explicit_time(intent.timestamp, "intent timestamp").isoformat(),
    }


def _intent_from_payload(value: object) -> ExecutionIntent:
    if not isinstance(value, Mapping):
        raise L5ExecutionTransactionError("INVALID_INTENT", "intent payload is missing")
    try:
        intent = ExecutionIntent(
            intent_id=value["intent_id"],
            symbol=value["symbol"],
            side=IntentSide(value["side"]),
            quantity=value["quantity"],
            estimated_price=value["estimated_price"],
            timestamp=_parse_explicit_time(value["timestamp"], "intent timestamp"),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise L5ExecutionTransactionError("INVALID_INTENT", "intent payload is invalid") from exc
    _intent_payload(intent)
    return intent


def _request_payload_from_plan(plan: L5ExecutionTransactionPlan) -> dict[str, object]:
    intent = _intent_payload(plan.intent)
    if plan.operation_kind in {"MARKET", "LIMIT_PLACEMENT"}:
        return {
            "request_type": "CanonicalL5ExecutionRequest", "intent": intent,
            "order_type": "MARKET" if plan.operation_kind == "MARKET" else "LIMIT",
            "operation_id": plan.operation_id, "order_id": plan.order_id,
            "report_id": plan.report_id, "submitted_at": plan.submitted_at.isoformat(),
            "limit_price": plan.limit_price, "fill_id": plan.fill_id,
            "filled_at": plan.filled_at.isoformat() if plan.filled_at else None,
        }
    if plan.operation_kind == "LIMIT_FILL" and plan.eligibility is not None and plan.filled_at is not None:
        return {
            "request_type": "CanonicalL5LimitFillRequest", "intent": intent,
            "order_id": plan.order_id, "eligibility_id": plan.eligibility.eligibility_id,
            "operation_id": plan.operation_id, "fill_id": plan.fill_id,
            "report_id": plan.report_id, "market_price": plan.eligibility.market_price,
            "observed_at": plan.eligibility.observed_at.isoformat(),
            "filled_at": plan.filled_at.isoformat(),
        }
    raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "request cannot be reconstructed")


def _cancellation_request_payload(*, operation_id: str, order_id: str, report_id: str, cancelled_at: datetime) -> dict[str, object]:
    return {
        "request_type": "CanonicalL5CancellationRequest", "order_id": order_id,
        "operation_id": operation_id, "report_id": report_id,
        "cancelled_at": cancelled_at.isoformat(),
    }


def _rejection_request_semantics(payload: Mapping[str, object]) -> tuple[ExecutionIntent, str, str, dict[str, object]]:
    intent = _intent_from_payload(payload.get("intent"))
    if payload.get("request_type") == "CanonicalL5ExecutionRequest":
        required = {"request_type", "intent", "order_type", "operation_id", "order_id", "report_id", "submitted_at", "limit_price", "fill_id", "filled_at"}
        if set(payload) != required:
            raise L5ExecutionTransactionError("INVALID_EXECUTION_REQUEST", "execution request fields differ")
        operation_kind = {"MARKET": "MARKET", "LIMIT": "LIMIT_PLACEMENT"}.get(payload.get("order_type"))
        if operation_kind is None:
            raise L5ExecutionTransactionError("INVALID_EXECUTION_REQUEST", "order type is invalid")
        submitted = _parse_explicit_time(payload.get("submitted_at"), "submitted_at")
        if intent.timestamp > submitted:
            raise L5ExecutionTransactionError("INVALID_EXECUTION_REQUEST", "submission chronology is invalid")
        explicit = {"intent_timestamp": intent.timestamp.isoformat(), "submitted_at": submitted.isoformat(), "filled_at": payload.get("filled_at")}
    elif payload.get("request_type") == "CanonicalL5LimitFillRequest":
        required = {"request_type", "intent", "order_id", "eligibility_id", "operation_id", "fill_id", "report_id", "market_price", "observed_at", "filled_at"}
        if set(payload) != required:
            raise L5ExecutionTransactionError("INVALID_EXECUTION_REQUEST", "LIMIT fill request fields differ")
        operation_kind = "LIMIT_FILL"
        observed = _parse_explicit_time(payload.get("observed_at"), "observed_at")
        filled = _parse_explicit_time(payload.get("filled_at"), "filled_at")
        if observed > intent.timestamp or intent.timestamp > filled:
            raise L5ExecutionTransactionError("INVALID_EXECUTION_REQUEST", "LIMIT fill chronology is invalid")
        explicit = {"intent_timestamp": intent.timestamp.isoformat(), "observed_at": observed.isoformat(), "filled_at": filled.isoformat()}
    else:
        raise L5ExecutionTransactionError("INVALID_EXECUTION_REQUEST", "request type is invalid")
    for name in ("operation_id", "order_id", "report_id"):
        _identifier(payload.get(name), name)
    return intent, operation_kind, str(payload["order_id"]), explicit


def _request_payload_from_transaction_event(event: L5ExecutionTransactionEvent) -> dict[str, object]:
    inputs = _thaw_json(event.payload.get("operation_inputs"))
    if not isinstance(inputs, Mapping):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "operation inputs are missing")
    if event.event_type in {"MARKET_COMMITTED", "LIMIT_PLACED"}:
        market = event.event_type == "MARKET_COMMITTED"
        return {
            "request_type": "CanonicalL5ExecutionRequest", "intent": inputs["intent"],
            "order_type": "MARKET" if market else "LIMIT", "operation_id": event.operation_id,
            "order_id": inputs["order_id"], "report_id": inputs["report_id"],
            "submitted_at": inputs["submitted_at"], "limit_price": None if market else inputs["limit_price"],
            "fill_id": inputs["fill_id"] if market else None, "filled_at": inputs["filled_at"] if market else None,
        }
    if event.event_type == "LIMIT_FILLED":
        eligibility = inputs["eligibility"]
        return {
            "request_type": "CanonicalL5LimitFillRequest", "intent": inputs["intent"],
            "order_id": inputs["order_id"], "eligibility_id": eligibility["eligibility_id"],
            "operation_id": event.operation_id, "fill_id": inputs["fill_id"],
            "report_id": inputs["report_id"], "market_price": eligibility["market_price"],
            "observed_at": eligibility["observed_at"], "filled_at": inputs["filled_at"],
        }
    if event.event_type == "LIMIT_CANCELLED":
        return {
            "request_type": "CanonicalL5CancellationRequest", "order_id": inputs["order_id"],
            "operation_id": event.operation_id, "report_id": inputs["report_id"],
            "cancelled_at": inputs["cancelled_at"],
        }
    raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "event request cannot be reconstructed")


def _price_observation_from_payload(payload: object) -> L5PriceObservation:
    if not isinstance(payload, Mapping):
        raise L5ExecutionTransactionError(
            "INVALID_PRICE_OBSERVATION",
            "price observation payload is missing",
        )
    try:
        observation = L5PriceObservation(
            schema_version=payload["schema_version"],
            provider_id=payload["provider_id"],
            symbol=payload["symbol"],
            price=payload["price"],
            price_version=payload["price_version"],
            observed_at=_parse_explicit_time(payload["observed_at"], "price observed_at"),
            observation_hash=payload["observation_hash"],
        )
    except (KeyError, TypeError, ValueError, L5PriceProviderError) as exc:
        raise L5ExecutionTransactionError(
            "INVALID_PRICE_OBSERVATION",
            "price observation payload is invalid",
        ) from exc
    if not observation.is_intact():
        raise L5ExecutionTransactionError(
            "INVALID_PRICE_OBSERVATION",
            "price observation hash is invalid",
        )
    return observation


def _require_price_observation(
    observation: object,
    *,
    intent: ExecutionIntent,
) -> L5PriceObservation:
    if not isinstance(observation, L5PriceObservation) or not observation.is_intact():
        raise L5ExecutionTransactionError(
            "INVALID_PRICE_OBSERVATION",
            "an intact authoritative price observation is required",
        )
    if observation.symbol != intent.symbol or observation.price != float(intent.estimated_price):
        raise L5ExecutionTransactionError(
            "AUTHORIZED_PRICE_MISMATCH",
            "intent price differs from the authoritative observation",
        )
    return observation


def _risk_event_payload(event: RiskExecutionJournalEvent) -> dict[str, object]:
    return {**event.fields_without_hash(), "event_hash": event.event_hash}


def _context_from_payload(data: Mapping[str, object]) -> RiskExecutionContext:
    try:
        return RiskExecutionContext(
            provider_id=data["provider_id"],
            state_version=data["state_version"],
            trading_day=data["trading_day"],
            risk_limits=RiskLimits.model_validate(data["risk_limits"]),
            exposure_snapshot=ExposureSnapshot.model_validate(data["exposure_snapshot"]),
            signed_positions=data["signed_positions"],
            daily_realized_pnl=data["daily_realized_pnl"],
            current_equity=data["current_equity"],
            peak_equity=data["peak_equity"],
            execution_enabled=data["execution_enabled"],
            kill_switch_active=data["kill_switch_active"],
            legacy_hard_deny=data["legacy_hard_deny"],
        )
    except (KeyError, TypeError, ValueError, RiskContextError) as exc:
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "risk context payload is invalid") from exc


def _risk_event_from_payload(data: Mapping[str, object]) -> RiskExecutionJournalEvent:
    try:
        return RiskExecutionJournalEvent(
            schema_version=data["schema_version"],
            sequence_number=data["sequence_number"],
            event_type=data["event_type"],
            provider_id=data["provider_id"],
            intent_id=data["intent_id"],
            state_version_before=data["state_version_before"],
            state_version_after=data["state_version_after"],
            context_hash_before=data["context_hash_before"],
            context_hash_after=data["context_hash_after"],
            payload=data["payload"],
            previous_event_hash=data["previous_event_hash"],
            event_hash=data["event_hash"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "risk event payload is invalid") from exc


@dataclass(frozen=True)
class L5TransactionPosition:
    symbol: str
    quantity: float
    avg_entry_price: float
    realized_pnl: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "symbol", _identifier(self.symbol, "position symbol"))
        object.__setattr__(self, "quantity", _number(self.quantity, "position quantity"))
        object.__setattr__(self, "avg_entry_price", _number(self.avg_entry_price, "average entry price"))
        if isinstance(self.realized_pnl, bool) or not isinstance(self.realized_pnl, (int, float)):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", "realized_pnl must be finite")
        realized = float(self.realized_pnl)
        if not math.isfinite(realized):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", "realized_pnl must be finite")
        object.__setattr__(self, "realized_pnl", realized)

    def canonical(self) -> dict[str, object]:
        return {
            "symbol": self.symbol,
            "quantity": self.quantity,
            "avg_entry_price": self.avg_entry_price,
            "realized_pnl": self.realized_pnl,
        }


@dataclass(frozen=True)
class L5TransactionOrder:
    order_id: str
    placement_intent_id: str
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType
    limit_price: float | None
    status: OrderStatus
    submitted_at: datetime
    filled_at: datetime | None = None
    filled_price: float | None = None
    cancelled_at: datetime | None = None

    def __post_init__(self) -> None:
        for name in ("order_id", "placement_intent_id", "symbol"):
            object.__setattr__(self, name, _identifier(getattr(self, name), name))
        if not isinstance(self.side, OrderSide) or not isinstance(self.order_type, OrderType):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", "order enums are invalid")
        if not isinstance(self.status, OrderStatus):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", "order status is invalid")
        object.__setattr__(self, "quantity", _number(self.quantity, "order quantity", positive=True))
        object.__setattr__(self, "submitted_at", _explicit_time(self.submitted_at, "submitted_at"))
        if self.order_type == OrderType.MARKET and self.limit_price is not None:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", "MARKET order cannot have limit_price")
        if self.order_type == OrderType.LIMIT:
            object.__setattr__(self, "limit_price", _number(self.limit_price, "limit_price", positive=True))
        if self.status == OrderStatus.FILLED:
            object.__setattr__(self, "filled_at", _explicit_time(self.filled_at, "filled_at"))
            object.__setattr__(self, "filled_price", _number(self.filled_price, "filled_price", positive=True))
            if self.cancelled_at is not None:
                raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", "filled order cannot be cancelled")
        elif self.status == OrderStatus.CANCELLED:
            object.__setattr__(self, "cancelled_at", _explicit_time(self.cancelled_at, "cancelled_at"))
            if self.filled_at is not None or self.filled_price is not None:
                raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", "cancelled order cannot publish fill fields")
        elif self.filled_at is not None or self.filled_price is not None:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", "non-filled order cannot publish fill fields")
        elif self.cancelled_at is not None:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", "non-cancelled order cannot publish cancelled_at")

    def canonical(self) -> dict[str, object]:
        return {
            "order_id": self.order_id,
            "placement_intent_id": self.placement_intent_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "quantity": self.quantity,
            "order_type": self.order_type.value,
            "limit_price": self.limit_price,
            "status": self.status.value,
            "submitted_at": self.submitted_at.isoformat(),
            "filled_at": self.filled_at.isoformat() if self.filled_at else None,
            "filled_price": self.filled_price,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
        }


@dataclass(frozen=True)
class L5TransactionFill:
    fill_id: str
    order_id: str
    intent_id: str
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    filled_at: datetime

    def __post_init__(self) -> None:
        for name in ("fill_id", "order_id", "intent_id", "symbol"):
            object.__setattr__(self, name, _identifier(getattr(self, name), name))
        if not isinstance(self.side, OrderSide):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", "fill side is invalid")
        object.__setattr__(self, "quantity", _number(self.quantity, "fill quantity", positive=True))
        object.__setattr__(self, "price", _number(self.price, "fill price", positive=True))
        object.__setattr__(self, "filled_at", _explicit_time(self.filled_at, "filled_at"))

    def canonical(self) -> dict[str, object]:
        return {
            "fill_id": self.fill_id,
            "order_id": self.order_id,
            "intent_id": self.intent_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "quantity": self.quantity,
            "price": self.price,
            "filled_at": self.filled_at.isoformat(),
        }


@dataclass(frozen=True)
class L5TransactionReport:
    report_id: str
    order_id: str
    status: OrderStatus
    occurred_at: datetime
    message: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "report_id", _identifier(self.report_id, "report_id"))
        object.__setattr__(self, "order_id", _identifier(self.order_id, "order_id"))
        if not isinstance(self.status, OrderStatus):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", "report status is invalid")
        object.__setattr__(self, "occurred_at", _explicit_time(self.occurred_at, "occurred_at"))
        if not isinstance(self.message, str):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", "report message must be a string")

    def canonical(self) -> dict[str, object]:
        return {
            "report_id": self.report_id,
            "order_id": self.order_id,
            "status": self.status.value,
            "occurred_at": self.occurred_at.isoformat(),
            "message": self.message,
        }


@dataclass(frozen=True)
class L5ExecutionTransactionEvent:
    schema_version: str
    sequence_number: int
    event_type: str
    operation_id: str | None
    state_version_before: int
    state_hash_before: str
    payload: Mapping[str, object]
    previous_event_hash: str
    event_hash: str

    def __post_init__(self) -> None:
        if self.schema_version != TRANSACTION_SCHEMA_VERSION:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_EVENT", "event schema is invalid")
        if isinstance(self.sequence_number, bool) or not isinstance(self.sequence_number, int) or self.sequence_number < 1:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_EVENT", "event sequence is invalid")
        if self.event_type not in TRANSACTION_EVENT_TYPES:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_EVENT", "event_type is not supported")
        if self.operation_id is not None:
            object.__setattr__(self, "operation_id", _identifier(self.operation_id, "operation_id"))
        if isinstance(self.state_version_before, bool) or not isinstance(self.state_version_before, int):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_EVENT", "before version is invalid")
        if not _is_hash(self.state_hash_before) or not _is_hash(self.previous_event_hash) or not _is_hash(self.event_hash):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_EVENT", "event hash field is invalid")
        object.__setattr__(self, "payload", _freeze_json(self.payload))

    @classmethod
    def create(
        cls,
        *,
        sequence_number: int,
        event_type: str,
        operation_id: str | None,
        state_version_before: int,
        state_hash_before: str,
        payload: Mapping[str, object],
        previous_event_hash: str,
    ) -> L5ExecutionTransactionEvent:
        fields = {
            "schema_version": TRANSACTION_SCHEMA_VERSION,
            "sequence_number": sequence_number,
            "event_type": _identifier(event_type, "event_type"),
            "operation_id": operation_id,
            "state_version_before": state_version_before,
            "state_hash_before": state_hash_before,
            "payload": _thaw_json(_freeze_json(payload)),
            "previous_event_hash": previous_event_hash,
        }
        return cls(event_hash=_sha256(fields), **fields)

    def fields_without_hash(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "sequence_number": self.sequence_number,
            "event_type": self.event_type,
            "operation_id": self.operation_id,
            "state_version_before": self.state_version_before,
            "state_hash_before": self.state_hash_before,
            "payload": _thaw_json(self.payload),
            "previous_event_hash": self.previous_event_hash,
        }

    def canonical(self) -> dict[str, object]:
        return {**self.fields_without_hash(), "event_hash": self.event_hash}


def _freeze_record_mapping(
    value: Mapping[str, object],
    expected_type: type,
    name: str,
    identity_attribute: str,
) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_STATE", f"{name} must be a mapping")
    copied: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key or not isinstance(item, expected_type):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_STATE", f"{name} mapping is invalid")
        if key != getattr(item, identity_attribute, None):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_STATE", f"{name} key differs from record identity")
        copied[key] = item
    return MappingProxyType(copied)


@dataclass(frozen=True)
class L5ExecutionAggregateState:
    state_version: int
    orders: Mapping[str, L5TransactionOrder]
    positions: Mapping[str, L5TransactionPosition]
    fills: Mapping[str, L5TransactionFill]
    reports: Mapping[str, L5TransactionReport]
    risk_context: RiskExecutionContext
    risk_journal: tuple[RiskExecutionJournalEvent, ...]
    execution_journal: tuple[L5ExecutionTransactionEvent, ...]

    def __post_init__(self) -> None:
        if isinstance(self.state_version, bool) or not isinstance(self.state_version, int) or self.state_version < 0:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_STATE", "state_version must be non-negative")
        object.__setattr__(
            self,
            "orders",
            _freeze_record_mapping(self.orders, L5TransactionOrder, "orders", "order_id"),
        )
        object.__setattr__(
            self,
            "positions",
            _freeze_record_mapping(self.positions, L5TransactionPosition, "positions", "symbol"),
        )
        object.__setattr__(
            self,
            "fills",
            _freeze_record_mapping(self.fills, L5TransactionFill, "fills", "fill_id"),
        )
        object.__setattr__(
            self,
            "reports",
            _freeze_record_mapping(self.reports, L5TransactionReport, "reports", "report_id"),
        )
        if not isinstance(self.risk_context, RiskExecutionContext):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_STATE", "risk_context is invalid")
        if not isinstance(self.risk_journal, tuple) or not isinstance(self.execution_journal, tuple):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_STATE", "journals must be tuples")
        try:
            risk_context, _ = replay_journal(self.risk_journal)
        except RiskContextError as exc:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_STATE", "risk journal is invalid") from exc
        if risk_context != self.risk_context:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_STATE", "risk journal does not match context")
        _validate_position_alignment(self.positions, self.risk_context)

    def components_payload(self) -> dict[str, object]:
        return {
            "state_version": self.state_version,
            "orders": {key: value.canonical() for key, value in sorted(self.orders.items())},
            "positions": {key: value.canonical() for key, value in sorted(self.positions.items())},
            "fills": {key: value.canonical() for key, value in sorted(self.fills.items())},
            "reports": {key: value.canonical() for key, value in sorted(self.reports.items())},
            "risk_context": self.risk_context.canonical(),
            "risk_journal": [_risk_event_payload(event) for event in self.risk_journal],
        }

    def canonical(self) -> dict[str, object]:
        return {
            **self.components_payload(),
            "execution_journal": [event.canonical() for event in self.execution_journal],
        }

    @property
    def state_hash(self) -> str:
        return _sha256(self.canonical())


@dataclass(frozen=True, eq=False)
class L5ExecutionAuthorityState:
    """Single published authority containing economics and local delivery."""

    aggregate_state: L5ExecutionAggregateState
    delivery_state: L5ExecutionDeliveryState

    def __post_init__(self) -> None:
        if not isinstance(self.aggregate_state, L5ExecutionAggregateState):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_STATE", "aggregate state is invalid")
        if not isinstance(self.delivery_state, L5ExecutionDeliveryState):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_STATE", "delivery state is invalid")

    @property
    def authority_hash(self) -> str:
        return _sha256(
            {
                "aggregate_state_hash": self.aggregate_state.state_hash,
                "delivery_state_hash": self.delivery_state.delivery_hash,
            }
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, L5ExecutionAuthorityState):
            return (
                self.aggregate_state == other.aggregate_state
                and self.delivery_state == other.delivery_state
            )
        if isinstance(other, L5ExecutionAggregateState):
            return self.aggregate_state == other
        return NotImplemented


def _validate_position_alignment(
    positions: Mapping[str, L5TransactionPosition],
    context: RiskExecutionContext,
    *,
    filled_symbol: str | None = None,
    fill_price: float | None = None,
) -> None:
    aggregate = {symbol: position for symbol, position in positions.items() if position.quantity > 0}
    risk = {symbol: quantity for symbol, quantity in context.signed_positions.items() if quantity > 0}
    snapshots = dict(context.exposure_snapshot.positions)
    if set(aggregate) != set(risk) or set(aggregate) != set(snapshots):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_STATE", "broker positions differ from risk context")
    for symbol, position in aggregate.items():
        snapshot_position = snapshots[symbol]
        if (
            snapshot_position.symbol != symbol
            or risk[symbol] != position.quantity
            or snapshot_position.quantity != position.quantity
            or snapshot_position.avg_entry_price != position.avg_entry_price
        ):
            raise L5ExecutionTransactionError(
                "INVALID_TRANSACTION_STATE",
                "broker position economics differ from risk snapshot",
            )
    realized_pnl_total = sum(position.realized_pnl for position in positions.values())
    if context.exposure_snapshot.realized_pnl_total != realized_pnl_total:
        raise L5ExecutionTransactionError(
            "INVALID_TRANSACTION_STATE",
            "realized PnL differs from aggregate positions",
        )
    if filled_symbol is not None:
        if fill_price is None:
            raise L5ExecutionTransactionError("INVALID_FILL_TRANSITION", "fill price is missing")
        if filled_symbol in snapshots and snapshots[filled_symbol].mark_price != fill_price:
            raise L5ExecutionTransactionError(
                "INVALID_FILL_TRANSITION",
                "filled symbol mark price must equal fill price",
            )


def _state_from_payload(
    payload: Mapping[str, object],
    execution_journal: tuple[L5ExecutionTransactionEvent, ...],
) -> L5ExecutionAggregateState:
    data = _thaw_json(payload)
    if not isinstance(data, dict):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "state payload is invalid")
    try:
        orders = {
            key: L5TransactionOrder(
                order_id=value["order_id"], placement_intent_id=value["placement_intent_id"],
                symbol=value["symbol"], side=OrderSide(value["side"]), quantity=value["quantity"],
                order_type=OrderType(value["order_type"]), limit_price=value["limit_price"],
                status=OrderStatus(value["status"]), submitted_at=datetime.fromisoformat(value["submitted_at"]),
                filled_at=datetime.fromisoformat(value["filled_at"]) if value["filled_at"] else None,
                filled_price=value["filled_price"],
                cancelled_at=(
                    datetime.fromisoformat(value["cancelled_at"])
                    if value.get("cancelled_at")
                    else None
                ),
            ) for key, value in data["orders"].items()
        }
        positions = {key: L5TransactionPosition(**value) for key, value in data["positions"].items()}
        fills = {
            key: L5TransactionFill(
                fill_id=value["fill_id"], order_id=value["order_id"], intent_id=value["intent_id"],
                symbol=value["symbol"], side=OrderSide(value["side"]), quantity=value["quantity"],
                price=value["price"], filled_at=datetime.fromisoformat(value["filled_at"]),
            ) for key, value in data["fills"].items()
        }
        reports = {
            key: L5TransactionReport(
                report_id=value["report_id"], order_id=value["order_id"],
                status=OrderStatus(value["status"]), occurred_at=datetime.fromisoformat(value["occurred_at"]),
                message=value["message"],
            ) for key, value in data["reports"].items()
        }
        context = _context_from_payload(data["risk_context"])
        risk_journal = tuple(_risk_event_from_payload(item) for item in data["risk_journal"])
        return L5ExecutionAggregateState(
            state_version=data["state_version"], orders=orders, positions=positions, fills=fills,
            reports=reports, risk_context=context, risk_journal=risk_journal,
            execution_journal=execution_journal,
        )
    except (KeyError, TypeError, ValueError, L5ExecutionTransactionError) as exc:
        if isinstance(exc, L5ExecutionTransactionError):
            raise
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "state payload is malformed") from exc


@dataclass(frozen=True)
class L5LimitFillEligibility:
    schema_version: str
    eligibility_id: str
    order_id: str
    aggregate_state_version: int
    aggregate_state_hash: str
    price_observation_hash: str
    market_price: float
    observed_at: datetime
    eligible: bool
    eligibility_hash: str

    def __post_init__(self) -> None:
        if self.schema_version != ELIGIBILITY_SCHEMA_VERSION:
            raise L5ExecutionTransactionError("INVALID_LIMIT_ELIGIBILITY", "eligibility schema is invalid")
        for name in ("eligibility_id", "order_id"):
            object.__setattr__(self, name, _identifier(getattr(self, name), name))
        if (
            isinstance(self.aggregate_state_version, bool)
            or not isinstance(self.aggregate_state_version, int)
            or self.aggregate_state_version < 0
        ):
            raise L5ExecutionTransactionError("INVALID_LIMIT_ELIGIBILITY", "state version is invalid")
        if (
            not _is_hash(self.aggregate_state_hash)
            or not _is_hash(self.price_observation_hash)
            or not _is_hash(self.eligibility_hash)
        ):
            raise L5ExecutionTransactionError("INVALID_LIMIT_ELIGIBILITY", "eligibility hash is invalid")
        object.__setattr__(self, "market_price", _number(self.market_price, "market_price", positive=True))
        object.__setattr__(self, "observed_at", _explicit_time(self.observed_at, "observed_at"))
        if not isinstance(self.eligible, bool):
            raise L5ExecutionTransactionError("INVALID_LIMIT_ELIGIBILITY", "eligible must be boolean")

    @classmethod
    def _create(
        cls,
        *,
        eligibility_id: str,
        order: L5TransactionOrder,
        state: L5ExecutionAggregateState,
        price_observation: L5PriceObservation,
    ) -> L5LimitFillEligibility:
        if not isinstance(price_observation, L5PriceObservation) or not price_observation.is_intact():
            raise L5ExecutionTransactionError(
                "INVALID_PRICE_OBSERVATION",
                "LIMIT eligibility requires an intact price observation",
            )
        if price_observation.symbol != order.symbol:
            raise L5ExecutionTransactionError(
                "INVALID_PRICE_OBSERVATION",
                "price observation symbol differs from LIMIT order",
            )
        price = price_observation.price
        observed = price_observation.observed_at
        if order.order_type != OrderType.LIMIT or order.status != OrderStatus.PENDING or order.limit_price is None:
            raise L5ExecutionTransactionError("INVALID_LIMIT_ORDER", "order is not a pending LIMIT")
        eligible = price <= order.limit_price if order.side == OrderSide.BUY else price >= order.limit_price
        fields = {
            "schema_version": ELIGIBILITY_SCHEMA_VERSION,
            "eligibility_id": _identifier(eligibility_id, "eligibility_id"),
            "order_id": order.order_id,
            "aggregate_state_version": state.state_version,
            "aggregate_state_hash": state.state_hash,
            "price_observation_hash": price_observation.observation_hash,
            "market_price": price,
            "observed_at": observed.isoformat(),
            "eligible": eligible,
        }
        return cls(eligibility_hash=_sha256(fields), observed_at=observed, **{key: value for key, value in fields.items() if key != "observed_at"})

    def fields_without_hash(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "eligibility_id": self.eligibility_id,
            "order_id": self.order_id,
            "aggregate_state_version": self.aggregate_state_version,
            "aggregate_state_hash": self.aggregate_state_hash,
            "price_observation_hash": self.price_observation_hash,
            "market_price": self.market_price,
            "observed_at": self.observed_at.isoformat(),
            "eligible": self.eligible,
        }

    def is_intact(self) -> bool:
        try:
            return (
                self.schema_version == ELIGIBILITY_SCHEMA_VERSION
                and _is_hash(self.aggregate_state_hash)
                and _is_hash(self.eligibility_hash)
                and self.eligibility_hash == _sha256(self.fields_without_hash())
            )
        except Exception:  # noqa: BLE001 - malformed persisted evidence must fail closed
            return False


def _eligibility_from_payload(payload: object) -> L5LimitFillEligibility:
    if not isinstance(payload, Mapping):
        raise L5ExecutionTransactionError("INVALID_LIMIT_ELIGIBILITY", "eligibility payload is invalid")
    try:
        return L5LimitFillEligibility(
            schema_version=payload["schema_version"],
            eligibility_id=payload["eligibility_id"],
            order_id=payload["order_id"],
            aggregate_state_version=payload["aggregate_state_version"],
            aggregate_state_hash=payload["aggregate_state_hash"],
            price_observation_hash=payload["price_observation_hash"],
            market_price=payload["market_price"],
            observed_at=_parse_explicit_time(payload["observed_at"], "eligibility observed_at"),
            eligible=payload["eligible"],
            eligibility_hash=payload["eligibility_hash"],
        )
    except (KeyError, TypeError, ValueError, L5ExecutionTransactionError) as exc:
        if isinstance(exc, L5ExecutionTransactionError) and exc.code == "INVALID_LIMIT_ELIGIBILITY":
            raise
        raise L5ExecutionTransactionError(
            "INVALID_LIMIT_ELIGIBILITY",
            "eligibility payload is invalid",
        ) from exc


def _require_authoritative_limit_eligibility(
    state: L5ExecutionAggregateState,
    order: L5TransactionOrder,
    eligibility: L5LimitFillEligibility,
    price_observation: L5PriceObservation,
) -> L5LimitFillEligibility:
    expected = L5LimitFillEligibility._create(
        eligibility_id=eligibility.eligibility_id,
        order=order,
        state=state,
        price_observation=price_observation,
    )
    if eligibility != expected:
        raise L5ExecutionTransactionError(
            "INVALID_LIMIT_ELIGIBILITY",
            "eligibility differs from the authoritative LIMIT evaluation",
        )
    return expected


@dataclass(frozen=True)
class L5ExecutionTransactionPlan:
    schema_version: str
    operation_id: str
    operation_kind: str
    expected_state_version: int
    expected_state_hash: str
    expected_context_version: int
    expected_context_hash: str
    intent: ExecutionIntent
    intent_hash: str
    order_id: str
    report_id: str
    submitted_at: datetime | None
    fill_id: str | None
    fill_price: float | None
    filled_at: datetime | None
    limit_price: float | None
    price_observation: L5PriceObservation | None
    eligibility: L5LimitFillEligibility | None
    transition: FillTransition | None
    consumption: RiskAuthorizationConsumption
    next_state: L5ExecutionAggregateState
    plan_hash: str

    def __post_init__(self) -> None:
        if self.schema_version != PLAN_SCHEMA_VERSION:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "plan schema is invalid")
        if self.operation_kind not in OPERATION_KINDS:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "operation_kind is not supported")
        for name in ("operation_id", "order_id", "report_id"):
            object.__setattr__(self, name, _identifier(getattr(self, name), name))
        for value, name in (
            (self.expected_state_version, "expected_state_version"),
            (self.expected_context_version, "expected_context_version"),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", f"{name} is invalid")
        for value, name in (
            (self.expected_state_hash, "expected_state_hash"),
            (self.expected_context_hash, "expected_context_hash"),
            (self.intent_hash, "intent_hash"),
            (self.plan_hash, "plan_hash"),
        ):
            if not _is_hash(value):
                raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", f"{name} is invalid")
        if not isinstance(self.intent, ExecutionIntent):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "intent is invalid")
        if not isinstance(self.consumption, RiskAuthorizationConsumption):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "consumption is invalid")
        if not isinstance(self.next_state, L5ExecutionAggregateState):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "next_state is invalid")
        self._validate_operation_fields()

    def _validate_operation_fields(self) -> None:
        if self.operation_kind == "MARKET":
            if (
                self.submitted_at is None
                or self.fill_id is None
                or self.fill_price is None
                or self.filled_at is None
                or self.transition is None
                or self.price_observation is None
                or self.limit_price is not None
                or self.eligibility is not None
            ):
                raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "MARKET fields are incomplete")
        elif self.operation_kind == "LIMIT_PLACEMENT":
            if (
                self.submitted_at is None
                or self.limit_price is None
                or self.fill_id is not None
                or self.fill_price is not None
                or self.filled_at is not None
                or self.price_observation is not None
                or self.eligibility is not None
                or self.transition is not None
            ):
                raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "LIMIT_PLACEMENT fields are invalid")
        elif self.operation_kind == "LIMIT_FILL" and (
                self.fill_id is None
                or self.filled_at is None
                or self.eligibility is None
                or self.transition is None
                or self.price_observation is None
                or self.submitted_at is not None
                or self.fill_price is not None
                or self.limit_price is not None
        ):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "LIMIT_FILL fields are incomplete")
        if self.submitted_at is not None:
            object.__setattr__(self, "submitted_at", _explicit_time(self.submitted_at, "submitted_at"))
        if self.filled_at is not None:
            object.__setattr__(self, "filled_at", _explicit_time(self.filled_at, "filled_at"))
        if self.fill_id is not None:
            object.__setattr__(self, "fill_id", _identifier(self.fill_id, "fill_id"))
        if self.fill_price is not None:
            object.__setattr__(self, "fill_price", _number(self.fill_price, "fill_price", positive=True))
        if self.limit_price is not None:
            object.__setattr__(self, "limit_price", _number(self.limit_price, "limit_price", positive=True))
        if self.price_observation is not None and (
            not isinstance(self.price_observation, L5PriceObservation)
            or not self.price_observation.is_intact()
        ):
            raise L5ExecutionTransactionError(
                "INVALID_TRANSACTION_PLAN",
                "price observation is invalid",
            )
        if self.eligibility is not None and (
            not isinstance(self.eligibility, L5LimitFillEligibility)
            or not self.eligibility.is_intact()
        ):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "eligibility is invalid")
        if self.transition is not None and not isinstance(self.transition, FillTransition):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "transition is invalid")

    @classmethod
    def _create(
        cls,
        *,
        operation_id: str,
        operation_kind: str,
        current: L5ExecutionAggregateState,
        intent: ExecutionIntent,
        order_id: str,
        report_id: str,
        consumption: RiskAuthorizationConsumption,
        next_state: L5ExecutionAggregateState,
        submitted_at: datetime | None = None,
        fill_id: str | None = None,
        fill_price: float | None = None,
        filled_at: datetime | None = None,
        limit_price: float | None = None,
        price_observation: L5PriceObservation | None = None,
        eligibility: L5LimitFillEligibility | None = None,
        transition: FillTransition | None = None,
    ) -> L5ExecutionTransactionPlan:
        intent_payload = _intent_payload(intent)
        fields = {
            "schema_version": PLAN_SCHEMA_VERSION,
            "operation_id": _identifier(operation_id, "operation_id"),
            "operation_kind": _identifier(operation_kind, "operation_kind"),
            "expected_state_version": current.state_version,
            "expected_state_hash": current.state_hash,
            "expected_context_version": current.risk_context.state_version,
            "expected_context_hash": current.risk_context.state_hash,
            "intent": intent_payload,
            "intent_hash": _sha256(intent_payload),
            "order_id": _identifier(order_id, "order_id"),
            "report_id": _identifier(report_id, "report_id"),
            "submitted_at": submitted_at.isoformat() if submitted_at is not None else None,
            "fill_id": fill_id,
            "fill_price": fill_price,
            "filled_at": filled_at.isoformat() if filled_at is not None else None,
            "limit_price": limit_price,
            "price_observation": (
                price_observation.canonical() if price_observation is not None else None
            ),
            "eligibility": eligibility.fields_without_hash() | {"eligibility_hash": eligibility.eligibility_hash}
            if eligibility is not None
            else None,
            "transition": transition.canonical() if transition is not None else None,
            "consumption_hash": consumption.consumption_hash,
            "next_state_hash": next_state.state_hash,
        }
        return cls(
            plan_hash=_sha256(fields),
            intent=intent,
            consumption=consumption,
            next_state=next_state,
            submitted_at=submitted_at,
            fill_id=fill_id,
            fill_price=fill_price,
            filled_at=filled_at,
            limit_price=limit_price,
            price_observation=price_observation,
            eligibility=eligibility,
            transition=transition,
            **{
                key: value
                for key, value in fields.items()
                if key
                not in {
                    "intent",
                    "consumption_hash",
                    "next_state_hash",
                    "submitted_at",
                    "fill_id",
                    "fill_price",
                    "filled_at",
                    "limit_price",
                    "price_observation",
                    "eligibility",
                    "transition",
                }
            },
        )

    def fields_without_hash(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "operation_id": self.operation_id,
            "operation_kind": self.operation_kind,
            "expected_state_version": self.expected_state_version,
            "expected_state_hash": self.expected_state_hash,
            "expected_context_version": self.expected_context_version,
            "expected_context_hash": self.expected_context_hash,
            "intent": _intent_payload(self.intent),
            "intent_hash": self.intent_hash,
            "order_id": self.order_id,
            "report_id": self.report_id,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "fill_id": self.fill_id,
            "fill_price": self.fill_price,
            "filled_at": self.filled_at.isoformat() if self.filled_at else None,
            "limit_price": self.limit_price,
            "price_observation": (
                self.price_observation.canonical() if self.price_observation else None
            ),
            "eligibility": (
                self.eligibility.fields_without_hash() | {"eligibility_hash": self.eligibility.eligibility_hash}
                if self.eligibility
                else None
            ),
            "transition": self.transition.canonical() if self.transition else None,
            "consumption_hash": self.consumption.consumption_hash,
            "next_state_hash": self.next_state.state_hash,
        }

    def is_intact(self) -> bool:
        try:
            return (
                self.schema_version == PLAN_SCHEMA_VERSION
                and self.consumption.is_intact()
                and _is_hash(self.expected_state_hash)
                and _is_hash(self.expected_context_hash)
                and _is_hash(self.intent_hash)
                and _is_hash(self.plan_hash)
                and self.operation_kind in OPERATION_KINDS
                and (
                    self.price_observation is None
                    or self.price_observation.is_intact()
                )
                and (self.eligibility is None or self.eligibility.is_intact())
                and (self.transition is None or isinstance(self.transition, FillTransition))
                and self.intent_hash == _sha256(_intent_payload(self.intent))
                and self.plan_hash == _sha256(self.fields_without_hash())
                and self.next_state.state_version == self.expected_state_version + 1
            )
        except Exception:  # noqa: BLE001 - malformed persisted evidence must fail closed
            return False


class AggregateRiskContextProvider:
    """Read-only RiskContextProvider view over the aggregate state."""

    def __init__(self, store: L5ExecutionTransactionStore) -> None:
        self._store = store

    def snapshot(self) -> RiskExecutionContext:
        return self._store.state.risk_context

    def assert_current(self, expected_version: int, expected_hash: str) -> None:
        current = self.snapshot()
        if current.state_version != expected_version or current.state_hash != expected_hash:
            raise RiskContextError("STALE_RISK_CONTEXT", "aggregate context changed")

    def commit_fill(self, expected_version: int, expected_hash: str, fill_transition: FillTransition) -> RiskExecutionContext:
        raise RiskContextError("TRANSACTION_REQUIRED", "fills must commit through the aggregate transaction store")

    def start_trading_day(self, expected_version: int, expected_hash: str, new_trading_day: str) -> RiskExecutionContext:
        raise RiskContextError("TRANSACTION_REQUIRED", "trading-day changes are outside this transaction contract")


class L5ExecutionTransactionStore:
    """Single-authority in-memory aggregate with prepare/CAS commit semantics."""

    def __init__(
        self,
        *,
        initial_context: RiskExecutionContext,
        initial_risk_journal: tuple[RiskExecutionJournalEvent, ...],
        price_provider: L5PriceProvider,
        initial_positions: Mapping[str, L5TransactionPosition] | None = None,
    ) -> None:
        if not isinstance(price_provider, L5PriceProvider):
            raise L5ExecutionTransactionError(
                "INVALID_PRICE_PROVIDER",
                "price_provider must implement L5PriceProvider",
            )
        positions = dict(initial_positions or {})
        base = L5ExecutionAggregateState(
            state_version=0, orders={}, positions=positions, fills={}, reports={},
            risk_context=initial_context, risk_journal=tuple(initial_risk_journal), execution_journal=(),
        )
        genesis = L5ExecutionTransactionEvent.create(
            sequence_number=1, event_type="AGGREGATE_INITIALIZED", operation_id=None,
            state_version_before=-1, state_hash_before=GENESIS_TRANSACTION_HASH,
            payload=base.components_payload(), previous_event_hash=GENESIS_TRANSACTION_HASH,
        )
        self._authority = L5ExecutionAuthorityState(
            aggregate_state=replace(base, execution_journal=(genesis,)),
            delivery_state=L5ExecutionDeliveryState.initial(),
        )
        self._lock = threading.RLock()
        self._context_provider = AggregateRiskContextProvider(self)
        self._price_provider = price_provider
        self._intent_locks: dict[str, threading.RLock] = {}
        self._evaluation_lock = threading.RLock()
        self._authorization_boundary: RiskAuthorizationBoundary | None = None
        self._risk_manager: RiskManager | None = None
        self._consumer_inboxes: dict[str, L5ExecutionOutcomeInbox] = {}

    @property
    def state(self) -> L5ExecutionAggregateState:
        with self._lock:
            return self._authority.aggregate_state

    @property
    def authority_state(self) -> L5ExecutionAuthorityState:
        with self._lock:
            return self._authority

    @property
    def delivery_state(self) -> L5ExecutionDeliveryState:
        with self._lock:
            return self._authority.delivery_state

    @property
    def context_provider(self) -> AggregateRiskContextProvider:
        return self._context_provider

    @property
    def price_provider(self) -> L5PriceProvider:
        return self._price_provider

    def authorization_boundary(self, risk_manager: RiskManager) -> RiskAuthorizationBoundary:
        """Return the one process-local risk boundary shared by this authority."""
        if not isinstance(risk_manager, RiskManager):
            raise L5ExecutionTransactionError("INVALID_RISK_MANAGER", "risk manager is invalid")
        with self._lock:
            if self._authorization_boundary is None:
                self._risk_manager = risk_manager
                self._authorization_boundary = RiskAuthorizationBoundary(
                    risk_manager,
                    self._context_provider,
                )
            elif self._risk_manager is not risk_manager:
                raise L5ExecutionTransactionError(
                    "RISK_BOUNDARY_CONFLICT",
                    "one transaction authority cannot use independent risk managers",
                )
            return self._authorization_boundary

    @contextmanager
    def intent_guard(self, intent_id: str) -> Iterator[None]:
        """Serialize one intent across every service sharing this store."""
        identity = _identifier(intent_id, "intent_id")
        with self._lock:
            guard = self._intent_locks.setdefault(identity, threading.RLock())
        with guard, self._evaluation_lock:
            yield

    def consumer_inbox(
        self,
        consumer_id: str,
        proposed: L5ExecutionOutcomeInbox | None = None,
    ) -> L5ExecutionOutcomeInbox:
        """Converge service consumers onto one in-process inbox authority."""
        identity = _identifier(consumer_id, "consumer_id")
        if proposed is not None and proposed.consumer_id != identity:
            raise L5ExecutionTransactionError(
                "CONSUMER_CONFIGURATION_CONFLICT",
                "proposed inbox belongs to another consumer",
            )
        with self._lock:
            existing = self._consumer_inboxes.get(identity)
            if existing is not None:
                if proposed is not None and proposed is not existing:
                    raise L5ExecutionTransactionError(
                        "CONSUMER_CONFIGURATION_CONFLICT",
                        "consumer already has another inbox authority",
                    )
                return existing
            inbox = proposed or L5ExecutionOutcomeInbox(identity)
            self._consumer_inboxes[identity] = inbox
            return inbox

    def prepare_market(
        self,
        *,
        boundary: RiskAuthorizationBoundary,
        intent: ExecutionIntent,
        consumption: RiskAuthorizationConsumption,
        operation_id: str,
        order_id: str,
        fill_id: str,
        report_id: str,
        submitted_at: datetime,
        fill_price: float,
        filled_at: datetime,
        transition: FillTransition,
        price_observation: L5PriceObservation | None = None,
    ) -> L5ExecutionTransactionPlan:
        self._validate_consumption_provenance(boundary, consumption)
        with self._lock:
            current = self._authority.aggregate_state
            self._ensure_consumption_unused(current, consumption)
            self._validate_consumption_identity(consumption, intent, current)
            return self._prepare_market_from_state(
                current=current,
                intent=intent,
                consumption=consumption,
                operation_id=operation_id,
                order_id=order_id,
                fill_id=fill_id,
                report_id=report_id,
                submitted_at=submitted_at,
                fill_price=fill_price,
                filled_at=filled_at,
                transition=transition,
                price_observation=(
                    price_observation
                    if price_observation is not None
                    else self._price_provider.snapshot(intent.symbol)
                ),
            )

    def prepare_limit_placement(
        self,
        *,
        boundary: RiskAuthorizationBoundary,
        intent: ExecutionIntent,
        consumption: RiskAuthorizationConsumption,
        operation_id: str,
        order_id: str,
        report_id: str,
        limit_price: float,
        submitted_at: datetime,
    ) -> L5ExecutionTransactionPlan:
        self._validate_consumption_provenance(boundary, consumption)
        with self._lock:
            current = self._authority.aggregate_state
            self._ensure_consumption_unused(current, consumption)
            self._validate_consumption_identity(consumption, intent, current)
            return self._prepare_limit_placement_from_state(
                current=current,
                intent=intent,
                consumption=consumption,
                operation_id=operation_id,
                order_id=order_id,
                report_id=report_id,
                limit_price=limit_price,
                submitted_at=submitted_at,
            )

    def evaluate_limit_eligibility(
        self,
        *,
        order_id: str,
        eligibility_id: str,
        price_observation: L5PriceObservation | None = None,
        market_price: float | None = None,
        observed_at: datetime | None = None,
    ) -> L5LimitFillEligibility:
        with self._lock:
            order = self._authority.aggregate_state.orders.get(order_id)
            if order is None:
                raise L5ExecutionTransactionError("ORDER_NOT_FOUND", "pending order does not exist")
            observation = (
                price_observation
                if price_observation is not None
                else self._price_provider.snapshot(order.symbol)
            )
            if market_price is not None and observation.price != float(market_price):
                raise L5ExecutionTransactionError(
                    "AUTHORIZED_PRICE_MISMATCH",
                    "caller market_price differs from authoritative observation",
                )
            if observed_at is not None and observation.observed_at != observed_at:
                raise L5ExecutionTransactionError(
                    "STALE_PRICE_OBSERVATION",
                    "caller observed_at differs from authoritative observation",
                )
            return L5LimitFillEligibility._create(
                eligibility_id=eligibility_id, order=order, state=self._authority.aggregate_state,
                price_observation=observation,
            )

    def derive_fill_transition(
        self,
        *,
        intent: ExecutionIntent,
        fill_id: str,
        fill_price: float,
        filled_at: datetime,
    ) -> FillTransition:
        """Derive accounting/risk state from the authoritative aggregate.

        Callers provide identities and the already-authorized execution price;
        they cannot provide post-fill positions or PnL.  A later CAS in
        :meth:`commit` rejects the plan if this source state changed.
        """
        _intent_payload(intent)
        price = _number(fill_price, "fill_price", positive=True)
        filled = _explicit_time(filled_at, "filled_at")
        with self._lock:
            current = self._authority.aggregate_state
            fill = L5TransactionFill(
                fill_id=fill_id,
                order_id="derived-transition-order",
                intent_id=intent.intent_id,
                symbol=intent.symbol,
                side=_order_side(intent.side),
                quantity=intent.quantity,
                price=price,
                filled_at=filled,
            )
            positions = dict(current.positions)
            positions[fill.symbol] = _next_position(positions.get(fill.symbol), fill)
            snapshot_positions: dict[str, SymbolExposure] = {}
            for symbol, position in positions.items():
                if position.quantity <= 0:
                    continue
                previous = current.risk_context.exposure_snapshot.positions.get(symbol)
                mark_price = price if symbol == fill.symbol else (
                    previous.mark_price if previous is not None else position.avg_entry_price
                )
                snapshot_positions[symbol] = SymbolExposure(
                    symbol=symbol,
                    quantity=position.quantity,
                    avg_entry_price=position.avg_entry_price,
                    mark_price=mark_price,
                )
            realized_total = sum(position.realized_pnl for position in positions.values())
            realized_delta = (
                realized_total
                - current.risk_context.exposure_snapshot.realized_pnl_total
            )
            daily_pnl = current.risk_context.daily_realized_pnl + realized_delta
            initial_equity = current.risk_context.exposure_snapshot.initial_equity
            current_equity = initial_equity + realized_total
            peak_equity = max(current.risk_context.peak_equity, current_equity)
            snapshot = ExposureSnapshot(
                positions=snapshot_positions,
                realized_pnl_total=realized_total,
                daily_pnl=daily_pnl,
                initial_equity=initial_equity,
                peak_equity=peak_equity,
            )
            return FillTransition(
                intent_id=intent.intent_id,
                fill_id=fill_id,
                signed_positions={
                    symbol: position.quantity
                    for symbol, position in positions.items()
                },
                exposure_snapshot=snapshot,
                daily_realized_pnl=daily_pnl,
                current_equity=current_equity,
                expected_peak_equity=peak_equity,
                payload={
                    "source": "l5-execution-transaction-store",
                    "aggregate_state_version": current.state_version,
                    "aggregate_state_hash": current.state_hash,
                },
            )

    def cancellation_outcome_spec(
        self,
        *,
        operation_id: str,
        order_id: str,
        report_id: str,
        cancelled_at: datetime,
    ) -> L5ExecutionOutcomeSpec:
        """Reconstruct the required cancellation outcome without mutation."""
        cancelled = _explicit_time(cancelled_at, "cancelled_at")
        with self._lock:
            current = self._authority.aggregate_state
            order = current.orders.get(_identifier(order_id, "order_id"))
            if order is None:
                raise L5ExecutionTransactionError("ORDER_NOT_FOUND", "pending order does not exist")
            request_payload = _cancellation_request_payload(
                operation_id=_identifier(operation_id, "operation_id"),
                order_id=order.order_id,
                report_id=_identifier(report_id, "report_id"),
                cancelled_at=cancelled,
            )
            return L5ExecutionOutcomeSpec(
                request_payload=request_payload,
                intent_id=f"cancellation:{operation_id}",
                intent_hash=_sha256(request_payload),
                operation_kind="LIMIT_CANCELLATION",
                final_status=OrderStatus.CANCELLED.value,
                committed=True,
                requested_order_id=order.order_id,
                operation_id=operation_id,
                order_id=order.order_id,
                fill_id=None,
                report_id=report_id,
                authorization_id=None,
                decision_hash=None,
                consumption_id=None,
                consumption_hash=None,
                provider_id=current.risk_context.provider_id,
                risk_limits_hash=None,
                context_state_version=current.risk_context.state_version,
                context_state_hash=current.risk_context.state_hash,
                aggregate_state_version_before=current.state_version,
                aggregate_state_hash_before=current.state_hash,
                decision_evidence=None,
                consumption_evidence=None,
                risk_context_evidence=current.risk_context.canonical(),
                explicit_times={"cancelled_at": cancelled.isoformat()},
                authorized_price=order.limit_price,
            )

    def cancel_limit(
        self,
        *,
        operation_id: str,
        order_id: str,
        report_id: str,
        cancelled_at: datetime,
        outcome_spec: L5ExecutionOutcomeSpec | object,
    ) -> L5ExecutionAggregateState:
        """Atomically cancel one pending LIMIT in the aggregate authority."""
        if not isinstance(outcome_spec, L5ExecutionOutcomeSpec):
            raise L5ExecutionTransactionError(
                "OUTCOME_REQUIRED",
                "LIMIT cancellation requires a canonical outcome",
            )
        cancelled = _explicit_time(cancelled_at, "cancelled_at")
        with self._lock:
            current = self._authority.aggregate_state
            self._require_new_ids(current, operation_id, None, None, report_id)
            order = current.orders.get(_identifier(order_id, "order_id"))
            if order is None:
                raise L5ExecutionTransactionError("ORDER_NOT_FOUND", "pending order does not exist")
            if order.order_type != OrderType.LIMIT or order.status != OrderStatus.PENDING:
                raise L5ExecutionTransactionError("INVALID_LIMIT_ORDER", "order is not a pending LIMIT")
            if cancelled < order.submitted_at:
                raise L5ExecutionTransactionError(
                    "INVALID_TRANSACTION_CHRONOLOGY",
                    "cancellation precedes LIMIT placement",
                )
            if outcome_spec != self.cancellation_outcome_spec(
                operation_id=operation_id,
                order_id=order_id,
                report_id=report_id,
                cancelled_at=cancelled,
            ):
                raise L5ExecutionTransactionError(
                    "INVALID_OUTCOME_SEMANTICS",
                    "cancellation outcome differs from authoritative reconstruction",
                )
            cancelled_order = replace(
                order,
                status=OrderStatus.CANCELLED,
                cancelled_at=cancelled,
            )
            report = L5TransactionReport(
                report_id=report_id,
                order_id=order.order_id,
                status=OrderStatus.CANCELLED,
                occurred_at=cancelled,
                message="limit order cancelled",
            )
            next_state = self._build_state(
                current=current,
                operation_id=operation_id,
                event_type="LIMIT_CANCELLED",
                orders={**current.orders, order.order_id: cancelled_order},
                positions=current.positions,
                fills=current.fills,
                reports={**current.reports, report.report_id: report},
                risk_context=current.risk_context,
                risk_journal=current.risk_journal,
                consumption=None,
                operation_inputs={
                    "order_id": order.order_id,
                    "report_id": report.report_id,
                    "cancelled_at": cancelled.isoformat(),
                },
            )
            _validate_transaction_delta(current, next_state, next_state.execution_journal[-1])
            _validate_execution_transaction_chain(
                next_state.execution_journal,
                expected_final_hash=next_state.execution_journal[-1].event_hash,
            )
            delivery_state = self._authority.delivery_state
            try:
                outcome = self._finalize_outcome(outcome_spec, next_state)
                self._validate_outcome_against_state(outcome, next_state)
                delivery_state = delivery_state.publish(outcome)
            except L5ExecutionDeliveryError as exc:
                raise L5ExecutionTransactionError(exc.code, exc.message) from exc
            try:
                self._publish_state(L5ExecutionAuthorityState(next_state, delivery_state))
            except (KeyboardInterrupt, SystemExit, MemoryError):
                raise
            except Exception as exc:
                raise L5ExecutionTransactionError(
                    "TRANSACTION_PUBLICATION_FAILED",
                    "aggregate publication failed",
                ) from exc
            return self._authority.aggregate_state

    def prepare_limit_fill(
        self,
        *,
        boundary: RiskAuthorizationBoundary,
        intent: ExecutionIntent,
        consumption: RiskAuthorizationConsumption | None,
        eligibility: L5LimitFillEligibility,
        operation_id: str,
        fill_id: str,
        report_id: str,
        filled_at: datetime,
        transition: FillTransition,
        price_observation: L5PriceObservation | None = None,
    ) -> L5ExecutionTransactionPlan:
        self._validate_consumption_provenance(boundary, consumption)
        with self._lock:
            current = self._authority.aggregate_state
            self._ensure_consumption_unused(current, consumption)
            self._validate_consumption_identity(consumption, intent, current)
            return self._prepare_limit_fill_from_state(
                current=current,
                intent=intent,
                consumption=consumption,
                eligibility=eligibility,
                operation_id=operation_id,
                fill_id=fill_id,
                report_id=report_id,
                filled_at=filled_at,
                transition=transition,
                price_observation=(
                    price_observation
                    if price_observation is not None
                    else self._price_provider.snapshot(intent.symbol)
                ),
            )

    def _prepare_market_from_state(
        self,
        *,
        current: L5ExecutionAggregateState,
        intent: ExecutionIntent,
        consumption: RiskAuthorizationConsumption,
        operation_id: str,
        order_id: str,
        fill_id: str,
        report_id: str,
        submitted_at: datetime,
        fill_price: float,
        filled_at: datetime,
        transition: FillTransition,
        price_observation: L5PriceObservation,
    ) -> L5ExecutionTransactionPlan:
        _intent_payload(intent)
        submitted = _explicit_time(submitted_at, "submitted_at")
        filled = _explicit_time(filled_at, "filled_at")
        price = _number(fill_price, "fill_price", positive=True)
        observation = _require_price_observation(price_observation, intent=intent)
        if intent.timestamp > submitted or submitted > filled:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_CHRONOLOGY", "MARKET chronology is invalid")
        if price != float(intent.estimated_price):
            raise L5ExecutionTransactionError("AUTHORIZED_PRICE_MISMATCH", "fill price differs from authorized price")
        if price != observation.price or observation.observed_at > intent.timestamp:
            raise L5ExecutionTransactionError(
                "AUTHORIZED_PRICE_MISMATCH",
                "MARKET fill differs from the authoritative observation",
            )
        self._require_new_ids(current, operation_id, order_id, fill_id, report_id)
        order = L5TransactionOrder(
            order_id=order_id,
            placement_intent_id=intent.intent_id,
            symbol=intent.symbol,
            side=_order_side(intent.side),
            quantity=intent.quantity,
            order_type=OrderType.MARKET,
            limit_price=None,
            status=OrderStatus.FILLED,
            submitted_at=submitted,
            filled_at=filled,
            filled_price=price,
        )
        fill = L5TransactionFill(
            fill_id=fill_id,
            order_id=order_id,
            intent_id=intent.intent_id,
            symbol=intent.symbol,
            side=order.side,
            quantity=intent.quantity,
            price=price,
            filled_at=filled,
        )
        report = L5TransactionReport(
            report_id=report_id,
            order_id=order_id,
            status=OrderStatus.FILLED,
            occurred_at=filled,
            message="filled",
        )
        next_state = self._build_fill_state(
            current,
            operation_id,
            "MARKET_COMMITTED",
            intent,
            consumption,
            order,
            fill,
            report,
            transition,
            operation_inputs={
                "intent": _intent_payload(intent),
                "order_id": order_id,
                "report_id": report_id,
                "fill_id": fill_id,
                "submitted_at": submitted.isoformat(),
                "fill_price": price,
                "filled_at": filled.isoformat(),
                "price_observation": observation.canonical(),
                "transition": transition.canonical(),
            },
        )
        return L5ExecutionTransactionPlan._create(
            operation_id=operation_id,
            operation_kind="MARKET",
            current=current,
            intent=intent,
            order_id=order_id,
            report_id=report_id,
            consumption=consumption,
            next_state=next_state,
            submitted_at=submitted,
            fill_id=fill_id,
            fill_price=price,
            filled_at=filled,
            price_observation=observation,
            transition=transition,
        )

    def _prepare_limit_placement_from_state(
        self,
        *,
        current: L5ExecutionAggregateState,
        intent: ExecutionIntent,
        consumption: RiskAuthorizationConsumption,
        operation_id: str,
        order_id: str,
        report_id: str,
        limit_price: float,
        submitted_at: datetime,
    ) -> L5ExecutionTransactionPlan:
        _intent_payload(intent)
        submitted = _explicit_time(submitted_at, "submitted_at")
        if intent.timestamp > submitted:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_CHRONOLOGY", "LIMIT placement chronology is invalid")
        price = _number(limit_price, "limit_price", positive=True)
        if float(intent.estimated_price) != price:
            raise L5ExecutionTransactionError(
                "AUTHORIZED_PRICE_MISMATCH",
                "LIMIT placement intent price must equal limit_price",
            )
        self._require_new_ids(current, operation_id, order_id, None, report_id)
        order = L5TransactionOrder(
            order_id=order_id,
            placement_intent_id=intent.intent_id,
            symbol=intent.symbol,
            side=_order_side(intent.side),
            quantity=intent.quantity,
            order_type=OrderType.LIMIT,
            limit_price=price,
            status=OrderStatus.PENDING,
            submitted_at=submitted,
        )
        report = L5TransactionReport(
            report_id=report_id,
            order_id=order_id,
            status=OrderStatus.PENDING,
            occurred_at=submitted,
            message="limit order pending",
        )
        next_state = self._build_state(
            current=current,
            operation_id=operation_id,
            event_type="LIMIT_PLACED",
            orders={**current.orders, order_id: order},
            positions=current.positions,
            fills=current.fills,
            reports={**current.reports, report_id: report},
            risk_context=current.risk_context,
            risk_journal=current.risk_journal,
            consumption=consumption,
            operation_inputs={
                "intent": _intent_payload(intent),
                "order_id": order_id,
                "report_id": report_id,
                "limit_price": price,
                "submitted_at": submitted.isoformat(),
            },
        )
        return L5ExecutionTransactionPlan._create(
            operation_id=operation_id,
            operation_kind="LIMIT_PLACEMENT",
            current=current,
            intent=intent,
            order_id=order_id,
            report_id=report_id,
            consumption=consumption,
            next_state=next_state,
            submitted_at=submitted,
            limit_price=price,
        )

    def _prepare_limit_fill_from_state(
        self,
        *,
        current: L5ExecutionAggregateState,
        intent: ExecutionIntent,
        consumption: RiskAuthorizationConsumption,
        eligibility: L5LimitFillEligibility,
        operation_id: str,
        fill_id: str,
        report_id: str,
        filled_at: datetime,
        transition: FillTransition,
        price_observation: L5PriceObservation,
    ) -> L5ExecutionTransactionPlan:
        _intent_payload(intent)
        filled = _explicit_time(filled_at, "filled_at")
        observation = _require_price_observation(price_observation, intent=intent)
        if not isinstance(eligibility, L5LimitFillEligibility) or not eligibility.is_intact():
            raise L5ExecutionTransactionError("INVALID_LIMIT_ELIGIBILITY", "eligibility is invalid")
        if (
            eligibility.aggregate_state_version != current.state_version
            or eligibility.aggregate_state_hash != current.state_hash
        ):
            raise L5ExecutionTransactionError("STALE_LIMIT_ELIGIBILITY", "eligibility is stale")
        order = current.orders.get(eligibility.order_id)
        if order is None or order.status != OrderStatus.PENDING or order.order_type != OrderType.LIMIT:
            raise L5ExecutionTransactionError("INVALID_LIMIT_ORDER", "pending LIMIT order is missing")
        authoritative_eligibility = _require_authoritative_limit_eligibility(
            current,
            order,
            eligibility,
            observation,
        )
        if not authoritative_eligibility.eligible:
            raise L5ExecutionTransactionError("LIMIT_NOT_ELIGIBLE", "limit price has not been crossed")
        if intent.intent_id == order.placement_intent_id:
            raise L5ExecutionTransactionError("FRESH_FILL_INTENT_REQUIRED", "LIMIT fill requires a new intent_id")
        self._validate_intent_matches_order(intent, order)
        if float(intent.estimated_price) != eligibility.market_price:
            raise L5ExecutionTransactionError(
                "AUTHORIZED_PRICE_MISMATCH",
                "fill intent price differs from observed eligible price",
            )
        if not (
            order.submitted_at <= eligibility.observed_at <= intent.timestamp <= filled
        ):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_CHRONOLOGY", "LIMIT fill chronology is invalid")
        self._require_new_ids(current, operation_id, None, fill_id, report_id)
        filled_order = replace(
            order,
            status=OrderStatus.FILLED,
            filled_at=filled,
            filled_price=eligibility.market_price,
        )
        fill = L5TransactionFill(
            fill_id=fill_id,
            order_id=order.order_id,
            intent_id=intent.intent_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=eligibility.market_price,
            filled_at=filled,
        )
        report = L5TransactionReport(
            report_id=report_id,
            order_id=order.order_id,
            status=OrderStatus.FILLED,
            occurred_at=filled,
            message="limit order filled",
        )
        next_state = self._build_fill_state(
            current,
            operation_id,
            "LIMIT_FILLED",
            intent,
            consumption,
            filled_order,
            fill,
            report,
            transition,
            operation_inputs={
                "intent": _intent_payload(intent),
                "order_id": order.order_id,
                "report_id": report_id,
                "fill_id": fill_id,
                "filled_at": filled.isoformat(),
                "eligibility": eligibility.fields_without_hash()
                | {"eligibility_hash": eligibility.eligibility_hash},
                "price_observation": observation.canonical(),
                "transition": transition.canonical(),
            },
        )
        return L5ExecutionTransactionPlan._create(
            operation_id=operation_id,
            operation_kind="LIMIT_FILL",
            current=current,
            intent=intent,
            order_id=order.order_id,
            report_id=report_id,
            consumption=consumption,
            next_state=next_state,
            fill_id=fill_id,
            filled_at=filled,
            price_observation=observation,
            eligibility=eligibility,
            transition=transition,
        )

    def outcome_spec_for_plan(
        self,
        plan: L5ExecutionTransactionPlan,
        *,
        boundary: RiskAuthorizationBoundary,
    ) -> L5ExecutionOutcomeSpec:
        """Purely reconstruct the only outcome specification valid for ``plan``."""
        if not isinstance(plan, L5ExecutionTransactionPlan) or not plan.is_intact():
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "plan integrity check failed")
        with self._lock:
            current = self._authority.aggregate_state
            if (
                plan.expected_state_version != current.state_version
                or plan.expected_state_hash != current.state_hash
            ):
                raise L5ExecutionTransactionError("STALE_AGGREGATE_STATE", "aggregate CAS failed")
            return self._committed_outcome_spec(plan, current, boundary)

    @staticmethod
    def _committed_outcome_spec(
        plan: L5ExecutionTransactionPlan,
        current: L5ExecutionAggregateState,
        boundary: RiskAuthorizationBoundary,
    ) -> L5ExecutionOutcomeSpec:
        try:
            decision = boundary.decision_for_consumption(plan.consumption)
        except RiskAuthorizationError as exc:
            raise L5ExecutionTransactionError(exc.code, exc.message) from exc
        request_payload = _request_payload_from_plan(plan)
        if plan.operation_kind == "MARKET":
            status = OrderStatus.FILLED
            explicit_times = {
                "intent_timestamp": plan.intent.timestamp.isoformat(),
                "submitted_at": plan.submitted_at.isoformat(),
                "filled_at": plan.filled_at.isoformat(),
            }
            execution_price = plan.fill_price
        elif plan.operation_kind == "LIMIT_PLACEMENT":
            status = OrderStatus.PENDING
            explicit_times = {
                "intent_timestamp": plan.intent.timestamp.isoformat(),
                "submitted_at": plan.submitted_at.isoformat(),
                "filled_at": None,
            }
            execution_price = None
        else:
            status = OrderStatus.FILLED
            explicit_times = {
                "intent_timestamp": plan.intent.timestamp.isoformat(),
                "observed_at": plan.eligibility.observed_at.isoformat(),
                "filled_at": plan.filled_at.isoformat(),
            }
            execution_price = plan.price_observation.price
        return L5ExecutionOutcomeSpec(
            request_payload=request_payload,
            intent_id=plan.intent.intent_id,
            intent_hash=plan.intent_hash,
            operation_kind=plan.operation_kind,
            final_status=status.value,
            committed=True,
            requested_order_id=plan.order_id,
            operation_id=plan.operation_id,
            order_id=plan.order_id,
            fill_id=plan.fill_id,
            report_id=plan.report_id,
            authorization_id=decision.authorization_id,
            decision_hash=decision.decision_hash,
            consumption_id=plan.consumption.consumption_id,
            consumption_hash=plan.consumption.consumption_hash,
            provider_id=decision.provider_id,
            risk_limits_hash=decision.risk_limits_hash,
            context_state_version=current.risk_context.state_version,
            context_state_hash=current.risk_context.state_hash,
            aggregate_state_version_before=current.state_version,
            aggregate_state_hash_before=current.state_hash,
            decision_evidence=dict(decision.canonical()),
            consumption_evidence=dict(plan.consumption.canonical()),
            risk_context_evidence=current.risk_context.canonical(),
            price_identity=(
                plan.price_observation.canonical()
                if plan.price_observation is not None
                else None
            ),
            explicit_times=explicit_times,
            execution_price=execution_price,
            authorized_price=float(plan.intent.estimated_price),
        )

    def commit(
        self,
        plan: L5ExecutionTransactionPlan,
        *,
        boundary: RiskAuthorizationBoundary,
        outcome_spec: L5ExecutionOutcomeSpec | object = _AUTO_OUTCOME,
    ) -> L5ExecutionAggregateState:
        if outcome_spec is not _AUTO_OUTCOME and not isinstance(outcome_spec, L5ExecutionOutcomeSpec):
            raise L5ExecutionTransactionError(
                "OUTCOME_REQUIRED",
                "every transaction commit requires a canonical outcome",
            )
        if not isinstance(plan, L5ExecutionTransactionPlan) or not plan.is_intact():
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "plan integrity check failed")
        self._validate_consumption_provenance(boundary, plan.consumption)
        with self._lock:
            current = self._authority.aggregate_state
            committed_operations = {
                event.operation_id for event in current.execution_journal if event.operation_id is not None
            }
            if plan.operation_id in committed_operations:
                raise L5ExecutionTransactionError("TRANSACTION_ALREADY_COMMITTED", "operation was already committed")
            self._ensure_consumption_unused(current, plan.consumption)
            if plan.expected_state_version != current.state_version or plan.expected_state_hash != current.state_hash:
                raise L5ExecutionTransactionError("STALE_AGGREGATE_STATE", "aggregate CAS failed")
            if (
                plan.expected_context_version != current.risk_context.state_version
                or plan.expected_context_hash != current.risk_context.state_hash
            ):
                raise L5ExecutionTransactionError("STALE_RISK_CONTEXT", "risk context CAS failed")
            self._validate_consumption_identity(plan.consumption, plan.intent, current)
            try:
                guard = (
                    self._price_provider.locked_current(plan.price_observation)
                    if plan.price_observation is not None
                    else nullcontext()
                )
                with guard:
                    return self._commit_plan_locked(plan, current, outcome_spec, boundary)
            except L5ExecutionTransactionError:
                raise
            except L5ExecutionDeliveryError as exc:
                raise L5ExecutionTransactionError(exc.code, exc.message) from exc
            except L5PriceProviderError as exc:
                raise L5ExecutionTransactionError(exc.code, exc.message) from exc
            except (KeyboardInterrupt, SystemExit, MemoryError):
                raise
            except Exception as exc:
                raise L5ExecutionTransactionError(
                    "PRICE_PROVIDER_ERROR",
                    "authoritative price verification failed",
                ) from exc

    def _commit_plan_locked(
        self,
        plan: L5ExecutionTransactionPlan,
        current: L5ExecutionAggregateState,
        outcome_spec: L5ExecutionOutcomeSpec | object,
        boundary: RiskAuthorizationBoundary,
    ) -> L5ExecutionAggregateState:
        expected_plan = self._reconstruct_plan(plan, current)
        if expected_plan != plan:
            raise L5ExecutionTransactionError(
                "INVALID_TRANSACTION_SEMANTICS",
                "plan differs from deterministic reconstruction",
            )
        self._validate_next_state(expected_plan, current)
        expected_spec = self._committed_outcome_spec(expected_plan, current, boundary)
        supplied_spec = expected_spec if outcome_spec is _AUTO_OUTCOME else outcome_spec
        if supplied_spec != expected_spec:
            raise L5ExecutionTransactionError(
                "INVALID_OUTCOME_SEMANTICS",
                "provided outcome differs from authoritative reconstruction",
            )
        delivery_state = self._authority.delivery_state
        outcome = self._finalize_outcome(supplied_spec, expected_plan.next_state)
        self._validate_outcome_against_state(outcome, expected_plan.next_state)
        delivery_state = delivery_state.publish(outcome)
        try:
            self._publish_state(L5ExecutionAuthorityState(expected_plan.next_state, delivery_state))
        except (KeyboardInterrupt, SystemExit, MemoryError):
            raise
        except Exception as exc:
            raise L5ExecutionTransactionError(
                "TRANSACTION_PUBLICATION_FAILED",
                "aggregate publication failed",
            ) from exc
        return self._authority.aggregate_state

    def _publish_state(
        self,
        next_state: L5ExecutionAggregateState | L5ExecutionAuthorityState,
    ) -> None:
        self._authority = (
            next_state
            if isinstance(next_state, L5ExecutionAuthorityState)
            else L5ExecutionAuthorityState(next_state, self._authority.delivery_state)
        )

    def outcome_for_intent(self, intent_id: str) -> L5ExecutionOutcome | None:
        """Return the canonical finalized outcome, if any, without mutation."""
        identity = _identifier(intent_id, "intent_id")
        with self._lock:
            outcome_id = self._authority.delivery_state.intent_outcomes.get(identity)
            return (
                self._authority.delivery_state.outcomes[outcome_id]
                if outcome_id is not None
                else None
            )

    def pending_outcomes(self, consumer_id: str) -> tuple[L5ExecutionOutcome, ...]:
        with self._lock:
            return self._authority.delivery_state.pending_for(consumer_id)

    def publish_rejection_outcome(
        self,
        *,
        request_payload: Mapping[str, object],
        price_observation: L5PriceObservation | None,
        boundary: RiskAuthorizationBoundary,
        decision: RiskAuthorizationDecision,
        expected_aggregate_version: int,
        expected_aggregate_hash: str,
        expected_delivery_version: int,
        expected_delivery_hash: str,
    ) -> L5ExecutionOutcome:
        """Publish an evaluated risk rejection without economic L5 mutation."""
        try:
            issued = boundary.verify_decision_evidence(decision)
        except RiskAuthorizationError as exc:
            raise L5ExecutionTransactionError(exc.code, exc.message) from exc
        if issued.allowed:
            raise L5ExecutionTransactionError(
                "INVALID_REJECTION_OUTCOME",
                "rejection decision is not blocked",
            )
        intent, operation_kind, requested_order_id, explicit_times = _rejection_request_semantics(
            request_payload
        )
        with self._lock:
            aggregate = self._authority.aggregate_state
            delivery = self._authority.delivery_state
            existing_id = delivery.intent_outcomes.get(intent.intent_id)
            if existing_id is not None:
                existing = delivery.outcomes[existing_id]
                if existing.request_hash != _sha256(_thaw_json(request_payload)):
                    raise L5ExecutionTransactionError(
                        "INTENT_OUTCOME_CONFLICT",
                        "intent already has a different outcome",
                    )
                return existing
            if (
                aggregate.state_version != expected_aggregate_version
                or aggregate.state_hash != expected_aggregate_hash
                or decision.context_state_version != aggregate.risk_context.state_version
                or decision.context_state_hash != aggregate.risk_context.state_hash
                or decision.provider_id != aggregate.risk_context.provider_id
            ):
                raise L5ExecutionTransactionError("STALE_AGGREGATE_STATE", "rejection aggregate CAS failed")
            if (
                delivery.delivery_version != expected_delivery_version
                or delivery.delivery_hash != expected_delivery_hash
            ):
                raise L5ExecutionTransactionError("STALE_DELIVERY_STATE", "delivery CAS failed")
            try:
                verify_blocked_decision_evidence(decision, intent, aggregate.risk_context)
            except RiskAuthorizationError as exc:
                raise L5ExecutionTransactionError(exc.code, exc.message) from exc
            observation = (
                _require_price_observation(price_observation, intent=intent)
                if price_observation is not None
                else None
            )
            outcome_spec = L5ExecutionOutcomeSpec(
                request_payload=request_payload,
                intent_id=intent.intent_id,
                intent_hash=_sha256(_intent_payload(intent)),
                operation_kind=operation_kind,
                final_status=OrderStatus.REJECTED.value,
                committed=False,
                requested_order_id=requested_order_id,
                operation_id=None,
                order_id=None,
                fill_id=None,
                report_id=None,
                authorization_id=decision.authorization_id,
                decision_hash=decision.decision_hash,
                consumption_id=None,
                consumption_hash=None,
                provider_id=decision.provider_id,
                risk_limits_hash=decision.risk_limits_hash,
                context_state_version=aggregate.risk_context.state_version,
                context_state_hash=aggregate.risk_context.state_hash,
                aggregate_state_version_before=aggregate.state_version,
                aggregate_state_hash_before=aggregate.state_hash,
                decision_evidence=dict(decision.canonical()),
                consumption_evidence=None,
                risk_context_evidence=aggregate.risk_context.canonical(),
                violation_codes=(*decision.guard_codes, *(item.code for item in decision.violations)),
                price_identity=observation.canonical() if observation else None,
                explicit_times=explicit_times,
                authorized_price=float(intent.estimated_price),
            )
            outcome = self._finalize_outcome(outcome_spec, aggregate)
            self._validate_outcome_against_state(outcome, aggregate)
            try:
                next_delivery = delivery.publish(outcome)
            except L5ExecutionDeliveryError as exc:
                raise L5ExecutionTransactionError(exc.code, exc.message) from exc
            self._publish_state(
                L5ExecutionAuthorityState(aggregate, next_delivery)
            )
            return outcome

    def acknowledge_outcome(
        self,
        *,
        receipt: L5ExecutionInboxReceipt,
        inbox: L5ExecutionOutcomeInbox,
        expected_delivery_version: int,
        expected_delivery_hash: str,
    ) -> L5ExecutionDeliveryAcknowledgement:
        """CAS-acknowledge a locally accepted outcome; repeated ack is a no-op."""
        if inbox.consumer_id != receipt.consumer_id:
            raise L5ExecutionTransactionError(
                "UNISSUED_RECEIPT",
                "receipt was not issued by this consumer inbox",
            )
        try:
            authority = self.consumer_inbox(receipt.consumer_id, inbox)
            authority.verify_receipt(receipt)
        except L5ExecutionDeliveryError as exc:
            raise L5ExecutionTransactionError(exc.code, exc.message) from exc
        except L5ExecutionTransactionError:
            raise
        with self._lock:
            delivery = self._authority.delivery_state
            existing_for_outcome = next((
                item
                for item in delivery.acknowledgements.values()
                if item.consumer_id == receipt.consumer_id
                and item.outcome_id == receipt.outcome_id
            ), None)
            if existing_for_outcome is not None:
                if existing_for_outcome.receipt_hash != receipt.receipt_hash:
                    raise L5ExecutionTransactionError(
                        "ACKNOWLEDGEMENT_CONFLICT",
                        "acknowledgement differs from the authoritative record",
                    )
                return existing_for_outcome
            if (
                delivery.delivery_version != expected_delivery_version
                or delivery.delivery_hash != expected_delivery_hash
            ):
                raise L5ExecutionTransactionError("STALE_DELIVERY_STATE", "delivery CAS failed")
            try:
                acknowledgement = authority.acknowledgement_for(receipt)
                next_delivery = delivery.acknowledge(acknowledgement)
            except L5ExecutionDeliveryError as exc:
                raise L5ExecutionTransactionError(exc.code, exc.message) from exc
            self._publish_state(
                L5ExecutionAuthorityState(self._authority.aggregate_state, next_delivery)
            )
            return acknowledgement

    @staticmethod
    def _finalize_outcome(
        outcome_spec: L5ExecutionOutcomeSpec,
        state: L5ExecutionAggregateState,
    ) -> L5ExecutionOutcome:
        event = state.execution_journal[-1] if outcome_spec.committed else None
        return L5ExecutionOutcome.from_spec(
            outcome_spec,
            aggregate_state_version=state.state_version,
            aggregate_state_hash=state.state_hash,
            transaction_event_hash=event.event_hash if event else None,
            transaction_sequence_number=event.sequence_number if event else None,
            transaction_event_type=event.event_type if event else None,
            context_state_version_after=state.risk_context.state_version,
            context_state_hash_after=state.risk_context.state_hash,
        )

    @staticmethod
    def _validate_outcome_against_state(
        outcome: L5ExecutionOutcome,
        state: L5ExecutionAggregateState,
    ) -> None:
        if not outcome.is_intact():
            raise L5ExecutionTransactionError("INVALID_OUTCOME", "outcome integrity failed")
        if (
            outcome.aggregate_state_version != state.state_version
            or outcome.aggregate_state_hash != state.state_hash
            or outcome.context_state_version_after != state.risk_context.state_version
            or outcome.context_state_hash_after != state.risk_context.state_hash
        ):
            raise L5ExecutionTransactionError("INVALID_OUTCOME", "outcome state identity differs")
        try:
            evidence_context = _context_from_payload(outcome.risk_context_evidence)
        except L5ExecutionTransactionError as exc:
            raise L5ExecutionTransactionError("INVALID_OUTCOME", "risk context evidence is invalid") from exc
        if (
            evidence_context.state_version != outcome.context_state_version
            or evidence_context.state_hash != outcome.context_state_hash
            or evidence_context.provider_id != outcome.provider_id
        ):
            raise L5ExecutionTransactionError("INVALID_OUTCOME", "outcome context evidence differs")
        if not outcome.committed:
            if (
                outcome.transaction_event_hash is not None
                or outcome.order_id is not None
                or outcome.aggregate_state_version_before != state.state_version
                or outcome.aggregate_state_hash_before != state.state_hash
                or evidence_context != state.risk_context
            ):
                raise L5ExecutionTransactionError("INVALID_OUTCOME", "rejection outcome contains transaction state")
            try:
                intent, operation_kind, order_id, explicit_times = _rejection_request_semantics(
                    outcome.request_payload
                )
                decision = RiskAuthorizationDecision.from_canonical(outcome.decision_evidence)
                verify_blocked_decision_evidence(decision, intent, evidence_context)
            except (RiskAuthorizationError, L5ExecutionTransactionError) as exc:
                raise L5ExecutionTransactionError("INVALID_OUTCOME", "rejection evidence differs") from exc
            codes = (*decision.guard_codes, *(item.code for item in decision.violations))
            if (
                outcome.intent_id != intent.intent_id
                or outcome.intent_hash != _sha256(_intent_payload(intent))
                or outcome.operation_kind != operation_kind
                or outcome.requested_order_id != order_id
                or dict(outcome.explicit_times) != explicit_times
                or outcome.authorization_id != decision.authorization_id
                or outcome.decision_hash != decision.decision_hash
                or outcome.risk_limits_hash != decision.risk_limits_hash
                or outcome.violation_codes != codes
                or outcome.authorized_price != float(intent.estimated_price)
                or outcome.consumption_evidence is not None
            ):
                raise L5ExecutionTransactionError("INVALID_OUTCOME", "rejection semantics differ")
            return
        event = state.execution_journal[-1]
        event_by_kind = {
            "MARKET": "MARKET_COMMITTED",
            "LIMIT_PLACEMENT": "LIMIT_PLACED",
            "LIMIT_FILL": "LIMIT_FILLED",
            "LIMIT_CANCELLATION": "LIMIT_CANCELLED",
        }
        if (
            outcome.transaction_event_hash != event.event_hash
            or outcome.transaction_sequence_number != event.sequence_number
            or outcome.transaction_event_type != event.event_type
            or outcome.operation_id != event.operation_id
            or event.event_type != event_by_kind[outcome.operation_kind]
        ):
            raise L5ExecutionTransactionError("INVALID_OUTCOME", "outcome transaction identity differs")
        try:
            before, _ = _replay_execution_transaction_journal(
                state.execution_journal[:-1],
                expected_final_hash=event.previous_event_hash,
            )
        except L5ExecutionTransactionError as exc:
            raise L5ExecutionTransactionError("INVALID_OUTCOME", "transaction before-state cannot be reconstructed") from exc
        if (
            outcome.aggregate_state_version_before != before.state_version
            or outcome.aggregate_state_hash_before != before.state_hash
            or evidence_context != before.risk_context
        ):
            raise L5ExecutionTransactionError("INVALID_OUTCOME", "outcome before-state differs")
        expected_request = _request_payload_from_transaction_event(event)
        if dict(_thaw_json(outcome.request_payload)) != expected_request:
            raise L5ExecutionTransactionError("INVALID_OUTCOME", "outcome request differs from transaction")
        order = state.orders.get(outcome.order_id)
        report = state.reports.get(outcome.report_id)
        if order is None or report is None or order.status.value != outcome.final_status:
            raise L5ExecutionTransactionError("INVALID_OUTCOME", "outcome order or report differs")
        if outcome.fill_id is not None:
            fill = state.fills.get(outcome.fill_id)
            if fill is None or fill.order_id != outcome.order_id or fill.intent_id != outcome.intent_id:
                raise L5ExecutionTransactionError("INVALID_OUTCOME", "outcome fill differs")
        if outcome.operation_kind == "LIMIT_CANCELLATION":
            if (
                outcome.intent_id != f"cancellation:{event.operation_id}"
                or outcome.intent_hash != _sha256(expected_request)
                or any(value is not None for value in (
                    outcome.authorization_id,
                    outcome.decision_hash,
                    outcome.consumption_id,
                    outcome.consumption_hash,
                    outcome.risk_limits_hash,
                    outcome.decision_evidence,
                    outcome.consumption_evidence,
                ))
                or dict(outcome.explicit_times) != {"cancelled_at": expected_request["cancelled_at"]}
                or outcome.authorized_price != order.limit_price
            ):
                raise L5ExecutionTransactionError("INVALID_OUTCOME", "cancellation outcome semantics differ")
            return
        try:
            intent = _intent_from_payload(expected_request["intent"])
            decision = RiskAuthorizationDecision.from_canonical(outcome.decision_evidence)
            consumption = RiskAuthorizationConsumption.from_canonical(outcome.consumption_evidence)
            expected_consumption = RiskAuthorizationConsumption._from_decision(decision)
        except (RiskAuthorizationError, L5ExecutionTransactionError) as exc:
            raise L5ExecutionTransactionError("INVALID_OUTCOME", "risk evidence is invalid") from exc
        if (
            not decision.allowed
            or decision.intent_id != intent.intent_id
            or decision.intent_hash != _sha256(_intent_payload(intent))
            or decision.provider_id != evidence_context.provider_id
            or decision.context_state_version != evidence_context.state_version
            or decision.context_state_hash != evidence_context.state_hash
            or decision.risk_limits_hash != _sha256(evidence_context.risk_limits.model_dump(mode="json"))
            or consumption != expected_consumption
            or event.payload.get("consumption_hash") != consumption.consumption_hash
            or outcome.intent_id != intent.intent_id
            or outcome.intent_hash != decision.intent_hash
            or outcome.authorization_id != decision.authorization_id
            or outcome.decision_hash != decision.decision_hash
            or outcome.consumption_id != consumption.consumption_id
            or outcome.consumption_hash != consumption.consumption_hash
            or outcome.risk_limits_hash != decision.risk_limits_hash
            or outcome.authorized_price != float(intent.estimated_price)
        ):
            raise L5ExecutionTransactionError("INVALID_OUTCOME", "outcome risk semantics differ")
        request_intent = expected_request["intent"]
        if outcome.operation_kind == "MARKET":
            expected_times = {
                "intent_timestamp": request_intent["timestamp"],
                "submitted_at": expected_request["submitted_at"],
                "filled_at": expected_request["filled_at"],
            }
            expected_price = expected_request["intent"]["estimated_price"]
            expected_price_identity = _thaw_json(event.payload["operation_inputs"])["price_observation"]
        elif outcome.operation_kind == "LIMIT_PLACEMENT":
            expected_times = {
                "intent_timestamp": request_intent["timestamp"],
                "submitted_at": expected_request["submitted_at"],
                "filled_at": None,
            }
            expected_price = None
            expected_price_identity = None
        else:
            expected_times = {
                "intent_timestamp": request_intent["timestamp"],
                "observed_at": expected_request["observed_at"],
                "filled_at": expected_request["filled_at"],
            }
            expected_price = expected_request["market_price"]
            expected_price_identity = _thaw_json(event.payload["operation_inputs"])["price_observation"]
        if (
            dict(outcome.explicit_times) != expected_times
            or outcome.execution_price != expected_price
            or (
                None if outcome.price_identity is None else _thaw_json(outcome.price_identity)
            ) != expected_price_identity
        ):
            raise L5ExecutionTransactionError("INVALID_OUTCOME", "outcome price or time semantics differ")

    def _validate_consumption_provenance(
        self,
        boundary: RiskAuthorizationBoundary,
        consumption: RiskAuthorizationConsumption,
    ) -> None:
        try:
            boundary.verify_consumption_evidence(consumption)
        except Exception as exc:
            raise L5ExecutionTransactionError("INVALID_RISK_CONSUMPTION", "consumption provenance failed") from exc

    def _validate_consumption_identity(
        self,
        consumption: RiskAuthorizationConsumption,
        intent: ExecutionIntent,
        state: L5ExecutionAggregateState,
    ) -> None:
        intent_payload = _intent_payload(intent)
        context = state.risk_context
        limits_hash = _sha256(context.risk_limits.model_dump(mode="json"))
        if consumption.intent_id != intent.intent_id or consumption.intent_hash != _sha256(intent_payload):
            raise L5ExecutionTransactionError("CONSUMPTION_INTENT_MISMATCH", "consumption does not match intent")
        if consumption.provider_id != context.provider_id:
            raise L5ExecutionTransactionError("CONSUMPTION_PROVIDER_MISMATCH", "consumption provider differs")
        if (
            consumption.context_state_version != context.state_version
            or consumption.context_state_hash != context.state_hash
        ):
            raise L5ExecutionTransactionError("STALE_RISK_CONSUMPTION", "consumption context is stale")
        if consumption.risk_limits_hash != limits_hash:
            raise L5ExecutionTransactionError("CONSUMPTION_LIMITS_MISMATCH", "consumption limits differ")

    def _ensure_consumption_unused(
        self,
        state: L5ExecutionAggregateState,
        consumption: RiskAuthorizationConsumption,
    ) -> None:
        used_hashes = {
            event.payload.get("consumption_hash")
            for event in state.execution_journal
            if event.operation_id is not None
        }
        if consumption.consumption_hash in used_hashes:
            raise L5ExecutionTransactionError(
                "RISK_CONSUMPTION_ALREADY_USED",
                "risk consumption is already bound to a committed transaction",
            )

    def _reconstruct_plan(
        self,
        plan: L5ExecutionTransactionPlan,
        current: L5ExecutionAggregateState,
    ) -> L5ExecutionTransactionPlan:
        if plan.operation_kind == "MARKET":
            return self._prepare_market_from_state(
                current=current,
                intent=plan.intent,
                consumption=plan.consumption,
                operation_id=plan.operation_id,
                order_id=plan.order_id,
                fill_id=plan.fill_id,
                report_id=plan.report_id,
                submitted_at=plan.submitted_at,
                fill_price=plan.fill_price,
                filled_at=plan.filled_at,
                transition=plan.transition,
                price_observation=plan.price_observation,
            )
        if plan.operation_kind == "LIMIT_PLACEMENT":
            return self._prepare_limit_placement_from_state(
                current=current,
                intent=plan.intent,
                consumption=plan.consumption,
                operation_id=plan.operation_id,
                order_id=plan.order_id,
                report_id=plan.report_id,
                limit_price=plan.limit_price,
                submitted_at=plan.submitted_at,
            )
        if plan.operation_kind == "LIMIT_FILL":
            return self._prepare_limit_fill_from_state(
                current=current,
                intent=plan.intent,
                consumption=plan.consumption,
                eligibility=plan.eligibility,
                operation_id=plan.operation_id,
                fill_id=plan.fill_id,
                report_id=plan.report_id,
                filled_at=plan.filled_at,
                transition=plan.transition,
                price_observation=plan.price_observation,
            )
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "operation_kind is not supported")

    def _require_new_ids(
        self,
        current: L5ExecutionAggregateState,
        operation_id: str,
        order_id: str | None,
        fill_id: str | None,
        report_id: str,
    ) -> None:
        _identifier(operation_id, "operation_id")
        if any(event.operation_id == operation_id for event in current.execution_journal):
            raise L5ExecutionTransactionError("DUPLICATE_OPERATION", "operation_id already exists")
        if order_id is not None and order_id in current.orders:
            raise L5ExecutionTransactionError("DUPLICATE_ORDER", "order_id already exists")
        if fill_id is not None and fill_id in current.fills:
            raise L5ExecutionTransactionError("DUPLICATE_FILL", "fill_id already exists")
        if report_id in current.reports:
            raise L5ExecutionTransactionError("DUPLICATE_REPORT", "report_id already exists")

    def _validate_intent_matches_order(self, intent: ExecutionIntent, order: L5TransactionOrder) -> None:
        if (
            intent.symbol != order.symbol
            or _order_side(intent.side) != order.side
            or float(intent.quantity) != order.quantity
        ):
            raise L5ExecutionTransactionError("ORDER_INTENT_MISMATCH", "fill intent differs from pending order")

    def _build_fill_state(
        self,
        current: L5ExecutionAggregateState,
        operation_id: str,
        event_type: str,
        intent: ExecutionIntent,
        consumption: RiskAuthorizationConsumption,
        order: L5TransactionOrder,
        fill: L5TransactionFill,
        report: L5TransactionReport,
        transition: FillTransition,
        operation_inputs: Mapping[str, object],
    ) -> L5ExecutionAggregateState:
        if transition.intent_id != intent.intent_id or transition.fill_id != fill.fill_id:
            raise L5ExecutionTransactionError("FILL_TRANSITION_MISMATCH", "transition identity differs from fill")
        positions = dict(current.positions)
        positions[fill.symbol] = _next_position(positions.get(fill.symbol), fill)
        next_context, next_risk_journal = _prepare_risk_transition(current.risk_context, current.risk_journal, transition)
        _validate_position_alignment(
            positions,
            next_context,
            filled_symbol=fill.symbol,
            fill_price=fill.price,
        )
        return self._build_state(
            current=current, operation_id=operation_id, event_type=event_type,
            orders={**current.orders, order.order_id: order}, positions=positions,
            fills={**current.fills, fill.fill_id: fill}, reports={**current.reports, report.report_id: report},
            risk_context=next_context, risk_journal=next_risk_journal, consumption=consumption,
            operation_inputs=operation_inputs,
        )

    def _build_state(
        self,
        *,
        current: L5ExecutionAggregateState,
        operation_id: str,
        event_type: str,
        orders: Mapping[str, L5TransactionOrder],
        positions: Mapping[str, L5TransactionPosition],
        fills: Mapping[str, L5TransactionFill],
        reports: Mapping[str, L5TransactionReport],
        risk_context: RiskExecutionContext,
        risk_journal: tuple[RiskExecutionJournalEvent, ...],
        consumption: RiskAuthorizationConsumption,
        operation_inputs: Mapping[str, object],
    ) -> L5ExecutionAggregateState:
        base = L5ExecutionAggregateState(
            state_version=current.state_version + 1, orders=orders, positions=positions,
            fills=fills, reports=reports, risk_context=risk_context, risk_journal=risk_journal,
            execution_journal=current.execution_journal,
        )
        payload = base.components_payload()
        if consumption is not None:
            payload["consumption_hash"] = consumption.consumption_hash
        payload["operation_inputs"] = _thaw_json(_freeze_json(operation_inputs))
        event = L5ExecutionTransactionEvent.create(
            sequence_number=len(current.execution_journal) + 1, event_type=event_type,
            operation_id=operation_id, state_version_before=current.state_version,
            state_hash_before=current.state_hash, payload=payload,
            previous_event_hash=current.execution_journal[-1].event_hash,
        )
        return replace(base, execution_journal=(*current.execution_journal, event))

    def _validate_next_state(
        self,
        plan: L5ExecutionTransactionPlan,
        current: L5ExecutionAggregateState,
    ) -> None:
        next_state = plan.next_state
        if next_state.state_version != current.state_version + 1:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "next version is invalid")
        if next_state.execution_journal[:-1] != current.execution_journal:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "journal prefix differs")
        event = next_state.execution_journal[-1]
        expected_event_type = {
            "MARKET": "MARKET_COMMITTED",
            "LIMIT_PLACEMENT": "LIMIT_PLACED",
            "LIMIT_FILL": "LIMIT_FILLED",
        }[plan.operation_kind]
        if (
            event.operation_id != plan.operation_id
            or event.event_type != expected_event_type
            or event.state_version_before != current.state_version
            or event.state_hash_before != current.state_hash
            or event.previous_event_hash != current.execution_journal[-1].event_hash
            or event.payload.get("consumption_hash") != plan.consumption.consumption_hash
        ):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "transaction event differs from plan")
        payload = dict(_thaw_json(event.payload))
        payload.pop("consumption_hash", None)
        payload.pop("operation_inputs", None)
        if payload != next_state.components_payload():
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "event payload differs from next state")
        _validate_transaction_delta(current, next_state, event)
        _validate_execution_transaction_chain(
            next_state.execution_journal,
            expected_final_hash=event.event_hash,
        )


def _order_side(side: IntentSide) -> OrderSide:
    if side == IntentSide.BUY:
        return OrderSide.BUY
    if side == IntentSide.SELL:
        return OrderSide.SELL
    raise L5ExecutionTransactionError("INVALID_INTENT", "unsupported intent side")


def _next_position(
    current: L5TransactionPosition | None,
    fill: L5TransactionFill,
) -> L5TransactionPosition:
    if fill.side == OrderSide.BUY:
        if current is None or current.quantity == 0:
            return L5TransactionPosition(fill.symbol, fill.quantity, fill.price, current.realized_pnl if current else 0.0)
        total = current.quantity + fill.quantity
        average = (current.quantity * current.avg_entry_price + fill.quantity * fill.price) / total
        return L5TransactionPosition(fill.symbol, total, average, current.realized_pnl)
    if current is None or current.quantity < fill.quantity:
        raise L5ExecutionTransactionError("INSUFFICIENT_POSITION", "SELL exceeds current position")
    realized = current.realized_pnl + (fill.price - current.avg_entry_price) * fill.quantity
    remaining = current.quantity - fill.quantity
    return L5TransactionPosition(fill.symbol, remaining, current.avg_entry_price if remaining else 0.0, realized)


def _prepare_risk_transition(
    before: RiskExecutionContext,
    journal: tuple[RiskExecutionJournalEvent, ...],
    transition: FillTransition,
) -> tuple[RiskExecutionContext, tuple[RiskExecutionJournalEvent, ...]]:
    validate_journal(journal)
    _require_fill_daily_pnl(
        before,
        after_realized_pnl_total=transition.exposure_snapshot.realized_pnl_total,
        daily_realized_pnl=transition.daily_realized_pnl,
        snapshot_daily_pnl=transition.exposure_snapshot.daily_pnl,
        error_code="INVALID_FILL_TRANSITION",
    )
    peak = max(before.peak_equity, transition.current_equity)
    if transition.expected_peak_equity != peak:
        raise L5ExecutionTransactionError("INVALID_FILL_TRANSITION", "peak equity is inconsistent")
    after = RiskExecutionContext(
        provider_id=before.provider_id, state_version=before.state_version + 1,
        trading_day=before.trading_day, risk_limits=before.risk_limits,
        exposure_snapshot=transition.exposure_snapshot, signed_positions=transition.signed_positions,
        daily_realized_pnl=transition.daily_realized_pnl, current_equity=transition.current_equity,
        peak_equity=peak, execution_enabled=before.execution_enabled,
        kill_switch_active=before.kill_switch_active, legacy_hard_deny=before.legacy_hard_deny,
    )
    fill_event = RiskExecutionJournalEvent.create(
        sequence_number=len(journal) + 1, event_type="FILL_RECEIVED", provider_id=before.provider_id,
        intent_id=transition.intent_id, state_version_before=before.state_version,
        state_version_after=after.state_version, context_hash_before=before.state_hash,
        context_hash_after=after.state_hash, payload={"transition": transition.canonical()},
        previous_event_hash=journal[-1].event_hash,
    )
    commit_event = RiskExecutionJournalEvent.create(
        sequence_number=len(journal) + 2, event_type="STATE_COMMITTED", provider_id=before.provider_id,
        intent_id=transition.intent_id, state_version_before=before.state_version,
        state_version_after=after.state_version, context_hash_before=before.state_hash,
        context_hash_after=after.state_hash, payload={"context": after.canonical()},
        previous_event_hash=fill_event.event_hash,
    )
    next_journal = (*journal, fill_event, commit_event)
    replayed, _ = replay_journal(next_journal)
    if replayed != after:
        raise L5ExecutionTransactionError("INVALID_FILL_TRANSITION", "risk journal replay differs")
    return after, next_journal


def _require_fill_daily_pnl(
    before: RiskExecutionContext,
    *,
    after_realized_pnl_total: float,
    daily_realized_pnl: float,
    snapshot_daily_pnl: float,
    error_code: str,
) -> float:
    realized_delta = (
        after_realized_pnl_total
        - before.exposure_snapshot.realized_pnl_total
    )
    expected_daily_realized_pnl = before.daily_realized_pnl + realized_delta
    if (
        daily_realized_pnl != expected_daily_realized_pnl
        or snapshot_daily_pnl != expected_daily_realized_pnl
    ):
        raise L5ExecutionTransactionError(
            error_code,
            "daily realized PnL differs from the realized PnL delta",
        )
    return expected_daily_realized_pnl


def _single_added_key(before: Mapping[str, object], after: Mapping[str, object], owner: str) -> str:
    added = set(after) - set(before)
    if len(added) != 1 or not set(before).issubset(after):
        raise L5ExecutionTransactionError(
            "INVALID_TRANSACTION_JOURNAL",
            f"{owner} must add exactly one record",
        )
    key = next(iter(added))
    if any(after[item] != before[item] for item in before):
        raise L5ExecutionTransactionError(
            "INVALID_TRANSACTION_JOURNAL",
            f"existing {owner} records changed",
        )
    return key


def _validate_fill_delta(
    before: L5ExecutionAggregateState,
    after: L5ExecutionAggregateState,
    order: L5TransactionOrder,
    fill: L5TransactionFill,
    report: L5TransactionReport,
) -> None:
    if (
        order.status != OrderStatus.FILLED
        or order.filled_at != fill.filled_at
        or order.filled_price != fill.price
        or order.symbol != fill.symbol
        or order.side != fill.side
        or order.quantity != fill.quantity
        or report.order_id != order.order_id
        or report.status != OrderStatus.FILLED
        or report.occurred_at != fill.filled_at
    ):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "fill records are inconsistent")
    expected_positions = dict(before.positions)
    expected_positions[fill.symbol] = _next_position(before.positions.get(fill.symbol), fill)
    if expected_positions != dict(after.positions):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "position delta differs from fill")
    if after.risk_context.state_version != before.risk_context.state_version + 1:
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "risk context version delta is invalid")
    if after.risk_journal[:-2] != before.risk_journal or len(after.risk_journal) != len(before.risk_journal) + 2:
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "risk journal delta is invalid")
    fill_event, commit_event = after.risk_journal[-2:]
    if (
        fill_event.event_type != "FILL_RECEIVED"
        or commit_event.event_type != "STATE_COMMITTED"
        or fill_event.intent_id != fill.intent_id
        or commit_event.intent_id != fill.intent_id
    ):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "risk journal fill pair is invalid")
    transition = _thaw_json(fill_event.payload).get("transition")
    if not isinstance(transition, dict):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "risk transition payload is missing")
    if transition.get("intent_id") != fill.intent_id or transition.get("fill_id") != fill.fill_id:
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "risk transition identity differs from fill")
    if transition.get("signed_positions") != dict(after.risk_context.signed_positions):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "risk transition positions differ")
    transition_snapshot = transition.get("exposure_snapshot")
    if not isinstance(transition_snapshot, dict):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "risk transition snapshot is missing")
    _require_fill_daily_pnl(
        before.risk_context,
        after_realized_pnl_total=after.risk_context.exposure_snapshot.realized_pnl_total,
        daily_realized_pnl=after.risk_context.daily_realized_pnl,
        snapshot_daily_pnl=after.risk_context.exposure_snapshot.daily_pnl,
        error_code="INVALID_TRANSACTION_JOURNAL",
    )
    if (
        transition.get("daily_realized_pnl") != after.risk_context.daily_realized_pnl
        or transition_snapshot.get("realized_pnl_total")
        != after.risk_context.exposure_snapshot.realized_pnl_total
        or transition_snapshot.get("daily_pnl")
        != after.risk_context.exposure_snapshot.daily_pnl
    ):
        raise L5ExecutionTransactionError(
            "INVALID_TRANSACTION_JOURNAL",
            "risk transition daily PnL differs from the committed context",
        )
    _validate_position_alignment(
        after.positions,
        after.risk_context,
        filled_symbol=fill.symbol,
        fill_price=fill.price,
    )


def _validate_transaction_delta(
    before: L5ExecutionAggregateState,
    after: L5ExecutionAggregateState,
    event: L5ExecutionTransactionEvent,
    operation_inputs: Mapping[str, object] | None = None,
) -> None:
    inputs = _thaw_json(operation_inputs or event.payload.get("operation_inputs"))
    if not isinstance(inputs, dict):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "operation inputs are missing")
    if after.state_version != before.state_version + 1:
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "aggregate version delta is invalid")
    if after.execution_journal[:-1] != before.execution_journal or after.execution_journal[-1] != event:
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "execution journal prefix differs")
    if event.event_type == "LIMIT_CANCELLED":
        if set(after.orders) != set(before.orders):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "cancellation changed order keys")
        changed_orders = [key for key in before.orders if before.orders[key] != after.orders[key]]
        if len(changed_orders) != 1:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "cancellation must change one order")
        order_id = changed_orders[0]
        previous_order = before.orders[order_id]
        order = after.orders[order_id]
        report_key = _single_added_key(before.reports, after.reports, "reports")
        report = after.reports[report_key]
        cancelled_at = _parse_explicit_time(inputs.get("cancelled_at"), "cancelled_at")
        expected_order = replace(
            previous_order,
            status=OrderStatus.CANCELLED,
            cancelled_at=cancelled_at,
        )
        if (
            previous_order.order_type != OrderType.LIMIT
            or previous_order.status != OrderStatus.PENDING
            or order != expected_order
            or cancelled_at < previous_order.submitted_at
            or report.order_id != order_id
            or report.status != OrderStatus.CANCELLED
            or report.occurred_at != cancelled_at
            or inputs.get("order_id") != order_id
            or inputs.get("report_id") != report.report_id
            or after.fills != before.fills
            or after.positions != before.positions
            or after.risk_context != before.risk_context
            or after.risk_journal != before.risk_journal
            or "consumption_hash" in event.payload
        ):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "LIMIT cancellation delta is invalid")
        return
    if not isinstance(inputs.get("intent"), dict):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "intent input is missing")
    intent = inputs["intent"]
    if event.event_type == "MARKET_COMMITTED":
        order_key = _single_added_key(before.orders, after.orders, "orders")
        fill_key = _single_added_key(before.fills, after.fills, "fills")
        report_key = _single_added_key(before.reports, after.reports, "reports")
        order = after.orders[order_key]
        fill = after.fills[fill_key]
        report = after.reports[report_key]
        observation = _price_observation_from_payload(inputs.get("price_observation"))
        if order.order_type != OrderType.MARKET or order.order_id != fill.order_id:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "MARKET order delta is invalid")
        if order.placement_intent_id != fill.intent_id:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "MARKET intent linkage is invalid")
        if (
            inputs.get("order_id") != order.order_id
            or inputs.get("report_id") != report.report_id
            or inputs.get("fill_id") != fill.fill_id
            or inputs.get("fill_price") != fill.price
            or inputs.get("submitted_at") != order.submitted_at.isoformat()
            or inputs.get("filled_at") != fill.filled_at.isoformat()
            or intent.get("intent_id") != fill.intent_id
            or intent.get("estimated_price") != fill.price
            or intent.get("symbol") != fill.symbol
            or intent.get("side") != fill.side.value
            or intent.get("quantity") != fill.quantity
            or observation.symbol != fill.symbol
            or observation.price != fill.price
            or observation.observation_hash
            != inputs["price_observation"].get("observation_hash")
        ):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "MARKET operation inputs differ")
        intent_time = _parse_explicit_time(intent.get("timestamp"), "intent timestamp")
        if not observation.observed_at <= intent_time <= order.submitted_at <= fill.filled_at:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "MARKET chronology differs")
        _validate_fill_delta(before, after, order, fill, report)
        risk_transition = _thaw_json(after.risk_journal[-2].payload).get("transition")
        if inputs.get("transition") != risk_transition:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "MARKET transition differs")
        return
    if event.event_type == "LIMIT_PLACED":
        order_key = _single_added_key(before.orders, after.orders, "orders")
        report_key = _single_added_key(before.reports, after.reports, "reports")
        order = after.orders[order_key]
        report = after.reports[report_key]
        if (
            order.order_type != OrderType.LIMIT
            or order.status != OrderStatus.PENDING
            or report.order_id != order.order_id
            or report.status != OrderStatus.PENDING
            or report.occurred_at != order.submitted_at
            or after.fills != before.fills
            or after.positions != before.positions
            or after.risk_context != before.risk_context
            or after.risk_journal != before.risk_journal
            or inputs.get("order_id") != order.order_id
            or inputs.get("report_id") != report.report_id
            or inputs.get("limit_price") != order.limit_price
            or inputs.get("submitted_at") != order.submitted_at.isoformat()
            or intent.get("intent_id") != order.placement_intent_id
            or intent.get("symbol") != order.symbol
            or intent.get("side") != order.side.value
            or intent.get("quantity") != order.quantity
            or intent.get("estimated_price") != order.limit_price
            or "price_observation" in inputs
        ):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "LIMIT placement delta is invalid")
        if _parse_explicit_time(intent.get("timestamp"), "intent timestamp") > order.submitted_at:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "LIMIT placement chronology differs")
        return
    if event.event_type == "LIMIT_FILLED":
        if set(after.orders) != set(before.orders):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "LIMIT fill changed order keys")
        changed_orders = [key for key in before.orders if before.orders[key] != after.orders[key]]
        if len(changed_orders) != 1:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "LIMIT fill must change one order")
        order_key = changed_orders[0]
        previous_order = before.orders[order_key]
        order = after.orders[order_key]
        fill_key = _single_added_key(before.fills, after.fills, "fills")
        report_key = _single_added_key(before.reports, after.reports, "reports")
        fill = after.fills[fill_key]
        report = after.reports[report_key]
        expected_order = replace(
            previous_order,
            status=OrderStatus.FILLED,
            filled_at=fill.filled_at,
            filled_price=fill.price,
        )
        if (
            previous_order.order_type != OrderType.LIMIT
            or previous_order.status != OrderStatus.PENDING
            or order != expected_order
            or order.order_id != fill.order_id
            or fill.intent_id == previous_order.placement_intent_id
        ):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "LIMIT fill order delta is invalid")
        eligibility = inputs.get("eligibility")
        if not isinstance(eligibility, dict):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "LIMIT eligibility input is missing")
        supplied_eligibility = _eligibility_from_payload(eligibility)
        observation = _price_observation_from_payload(inputs.get("price_observation"))
        authoritative_eligibility = _require_authoritative_limit_eligibility(
            before,
            previous_order,
            supplied_eligibility,
            observation,
        )
        if not authoritative_eligibility.eligible:
            raise L5ExecutionTransactionError(
                "INVALID_LIMIT_ELIGIBILITY",
                "ineligible LIMIT cannot publish a fill",
            )
        if (
            inputs.get("order_id") != order.order_id
            or inputs.get("report_id") != report.report_id
            or inputs.get("fill_id") != fill.fill_id
            or inputs.get("filled_at") != fill.filled_at.isoformat()
            or eligibility.get("order_id") != order.order_id
            or eligibility.get("market_price") != fill.price
            or intent.get("intent_id") != fill.intent_id
            or intent.get("estimated_price") != fill.price
            or intent.get("symbol") != fill.symbol
            or intent.get("side") != fill.side.value
            or intent.get("quantity") != fill.quantity
            or observation.symbol != fill.symbol
            or observation.price != fill.price
        ):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "LIMIT fill inputs differ")
        observed_at = authoritative_eligibility.observed_at
        intent_time = _parse_explicit_time(intent.get("timestamp"), "intent timestamp")
        if not previous_order.submitted_at <= observed_at <= intent_time <= fill.filled_at:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "LIMIT fill chronology differs")
        _validate_fill_delta(before, after, order, fill, report)
        risk_transition = _thaw_json(after.risk_journal[-2].payload).get("transition")
        if inputs.get("transition") != risk_transition:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "LIMIT transition differs")
        return
    raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "operational event_type is unsupported")


def _validate_execution_transaction_chain(
    events: tuple[L5ExecutionTransactionEvent, ...],
    *,
    expected_final_hash: str | None = None,
) -> str:
    if not isinstance(events, tuple) or not events:
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "journal must be a non-empty tuple")
    previous = GENESIS_TRANSACTION_HASH
    seen_operations: set[str] = set()
    seen_consumptions: set[str] = set()
    for sequence, event in enumerate(events, start=1):
        if not isinstance(event, L5ExecutionTransactionEvent):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "journal event is invalid")
        if event.schema_version != TRANSACTION_SCHEMA_VERSION or event.sequence_number != sequence:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "schema or sequence differs")
        if event.previous_event_hash != previous or event.event_hash != _sha256(event.fields_without_hash()):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "journal hash chain differs")
        if sequence == 1:
            if event.event_type != "AGGREGATE_INITIALIZED" or event.operation_id is not None:
                raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "initial event is invalid")
            if "consumption_hash" in event.payload:
                raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "initial event has consumption")
        else:
            if event.event_type == "AGGREGATE_INITIALIZED" or event.operation_id is None:
                raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "operational event is invalid")
            if event.operation_id in seen_operations:
                raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "operation_id is duplicated")
            seen_operations.add(event.operation_id)
            if not isinstance(event.payload.get("operation_inputs"), Mapping):
                raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "operation inputs are missing")
            consumption_hash = event.payload.get("consumption_hash")
            if event.event_type == "LIMIT_CANCELLED":
                if consumption_hash is not None:
                    raise L5ExecutionTransactionError(
                        "INVALID_TRANSACTION_JOURNAL",
                        "LIMIT cancellation cannot publish a risk consumption",
                    )
            else:
                if not _is_hash(consumption_hash):
                    raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "consumption_hash is invalid")
                if consumption_hash in seen_consumptions:
                    raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "consumption_hash is duplicated")
                seen_consumptions.add(consumption_hash)
        previous = event.event_hash
    if expected_final_hash is not None and (
        not _is_hash(expected_final_hash) or previous != expected_final_hash
    ):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "journal final hash differs")
    return previous


def _replay_execution_transaction_journal(
    events: tuple[L5ExecutionTransactionEvent, ...],
    *,
    expected_final_hash: str | None = None,
) -> tuple[L5ExecutionAggregateState, str]:
    final_hash = _validate_execution_transaction_chain(
        events,
        expected_final_hash=expected_final_hash,
    )
    first = events[0]
    if (
        first.event_type != "AGGREGATE_INITIALIZED"
        or first.operation_id is not None
        or first.state_version_before != -1
        or first.state_hash_before != GENESIS_TRANSACTION_HASH
    ):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "initial event is invalid")
    current = _state_from_payload(first.payload, (first,))
    if current.state_version != 0:
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "initial state version differs")
    for index, event in enumerate(events[1:], start=1):
        if event.state_version_before != current.state_version or event.state_hash_before != current.state_hash:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "event before-state differs")
        payload = dict(_thaw_json(event.payload))
        payload.pop("consumption_hash", None)
        operation_inputs = payload.pop("operation_inputs", None)
        next_state = _state_from_payload(payload, events[: index + 1])
        if next_state.state_version != index:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "state version is discontinuous")
        _validate_transaction_delta(current, next_state, event, operation_inputs)
        current = next_state
    return current, final_hash


def validate_execution_transaction_journal(
    events: tuple[L5ExecutionTransactionEvent, ...],
    *,
    expected_final_hash: str | None = None,
) -> str:
    """Validate hashes and semantic deltas.

    Without ``expected_final_hash`` this proves only local integrity of the
    supplied prefix.  Pass the externally retained final hash to detect tail
    truncation.
    """
    _, final_hash = _replay_execution_transaction_journal(
        events,
        expected_final_hash=expected_final_hash,
    )
    return final_hash


def replay_execution_transaction_journal(
    events: tuple[L5ExecutionTransactionEvent, ...],
    *,
    expected_final_hash: str,
) -> tuple[L5ExecutionAggregateState, str]:
    """Strict replay anchored to an expected final transaction hash."""
    if not _is_hash(expected_final_hash):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "expected final hash is invalid")
    return _replay_execution_transaction_journal(
        events,
        expected_final_hash=expected_final_hash,
    )


def replay_l5_execution_delivery_journal(
    events: tuple[L5ExecutionDeliveryEvent, ...],
    *,
    execution_events: tuple[L5ExecutionTransactionEvent, ...],
    expected_final_hash: str,
    inbox_events: tuple[L5ExecutionInboxEvent, ...] | Mapping[str, tuple[L5ExecutionInboxEvent, ...]],
    expected_inbox_hash: str | Mapping[str, str],
) -> tuple[L5ExecutionDeliveryState, str]:
    """Strictly replay outcomes/acks and bind committed outcomes to L5 events."""
    transaction_by_hash = {
        event.event_hash: (index, event)
        for index, event in enumerate(execution_events)
    }


    expected_event_type = {
        "MARKET": "MARKET_COMMITTED",
        "LIMIT_PLACEMENT": "LIMIT_PLACED",
        "LIMIT_FILL": "LIMIT_FILLED",
        "LIMIT_CANCELLATION": "LIMIT_CANCELLED",
    }
    last_outcome_state_version = -1

    def validate_outcome(outcome: L5ExecutionOutcome) -> None:
        nonlocal last_outcome_state_version
        if outcome.aggregate_state_version < last_outcome_state_version:
            raise L5ExecutionDeliveryError(
                "INVALID_DELIVERY_JOURNAL",
                "outcome publication regresses aggregate causality",
            )
        last_outcome_state_version = outcome.aggregate_state_version
        if not outcome.committed:
            if outcome.transaction_event_hash is not None:
                raise L5ExecutionDeliveryError(
                    "INVALID_DELIVERY_JOURNAL",
                    "rejection outcome has a transaction reference",
                )
            prefix_length = outcome.aggregate_state_version + 1
            if prefix_length > len(execution_events):
                raise L5ExecutionDeliveryError(
                    "INVALID_DELIVERY_JOURNAL",
                    "rejection state version has no transaction prefix",
                )
            state, _ = _replay_execution_transaction_journal(
                execution_events[:prefix_length],
                expected_final_hash=execution_events[prefix_length - 1].event_hash,
            )
            try:
                L5ExecutionTransactionStore._validate_outcome_against_state(outcome, state)
            except L5ExecutionTransactionError as exc:
                raise L5ExecutionDeliveryError(
                    "INVALID_DELIVERY_JOURNAL",
                    "rejection differs from canonical risk evidence",
                ) from exc
            return
        transaction = transaction_by_hash.get(outcome.transaction_event_hash)
        if transaction is None:
            raise L5ExecutionDeliveryError(
                "INVALID_DELIVERY_JOURNAL",
                "committed outcome has no transaction",
            )
        index, event = transaction
        if (
            event.operation_id != outcome.operation_id
            or event.event_type != expected_event_type.get(outcome.operation_kind)
        ):
            raise L5ExecutionDeliveryError(
                "INVALID_DELIVERY_JOURNAL",
                "outcome operation differs from transaction",
            )
        state, _ = _replay_execution_transaction_journal(
            execution_events[: index + 1],
            expected_final_hash=event.event_hash,
        )
        try:
            L5ExecutionTransactionStore._validate_outcome_against_state(outcome, state)
        except L5ExecutionTransactionError as exc:
            raise L5ExecutionDeliveryError(
                "INVALID_DELIVERY_JOURNAL",
                "outcome differs from authoritative transaction state",
            ) from exc

    inbox_states: dict[str, L5ExecutionInboxState] = {}
    if isinstance(inbox_events, Mapping):
        if not isinstance(expected_inbox_hash, Mapping) or set(inbox_events) != set(expected_inbox_hash):
            raise L5ExecutionDeliveryError("INVALID_INBOX_JOURNAL", "consumer anchors differ")
        for consumer_id, consumer_events in inbox_events.items():
            inbox_state, _ = replay_inbox_journal(
                consumer_events,
                expected_final_hash=expected_inbox_hash[consumer_id],
            )
            if any(receipt.consumer_id != consumer_id for receipt in inbox_state.receipts.values()):
                raise L5ExecutionDeliveryError("INVALID_INBOX_JOURNAL", "consumer journal identity differs")
            inbox_states[consumer_id] = inbox_state
    else:
        if not isinstance(expected_inbox_hash, str):
            raise L5ExecutionDeliveryError("INVALID_INBOX_JOURNAL", "single consumer anchor is invalid")
        inbox_state, _ = replay_inbox_journal(
            inbox_events,
            expected_final_hash=expected_inbox_hash,
        )
        consumers = {receipt.consumer_id for receipt in inbox_state.receipts.values()}
        if len(consumers) > 1:
            raise L5ExecutionDeliveryError("INVALID_INBOX_JOURNAL", "single journal mixes consumers")
        if consumers:
            inbox_states[next(iter(consumers))] = inbox_state
    return replay_delivery_journal(
        events,
        expected_final_hash=expected_final_hash,
        validate_outcome=validate_outcome,
        inbox_states=inbox_states,
    )


__all__ = [
    "ELIGIBILITY_SCHEMA_VERSION",
    "GENESIS_TRANSACTION_HASH",
    "PLAN_SCHEMA_VERSION",
    "TRANSACTION_SCHEMA_VERSION",
    "AggregateRiskContextProvider",
    "L5ExecutionAggregateState",
    "L5ExecutionAuthorityState",
    "L5ExecutionTransactionError",
    "L5ExecutionTransactionEvent",
    "L5ExecutionTransactionPlan",
    "L5ExecutionTransactionStore",
    "L5LimitFillEligibility",
    "L5TransactionFill",
    "L5TransactionOrder",
    "L5TransactionPosition",
    "L5TransactionReport",
    "replay_execution_transaction_journal",
    "replay_l5_execution_delivery_journal",
    "validate_execution_transaction_journal",
]
