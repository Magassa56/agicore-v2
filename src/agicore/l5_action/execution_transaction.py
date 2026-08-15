"""Deterministic aggregate transaction contract for a future L5 migration.

This module is deliberately independent from ``ExecutionService`` and
``MockBroker``.  It proves that broker state and risk context can be prepared
without side effects and published through one aggregate-state assignment.
It does not make the current L5 execution path risk-gated.
"""
from __future__ import annotations

import hashlib
import json
import math
import threading
from dataclasses import dataclass, replace
from datetime import datetime
from types import MappingProxyType
from typing import Mapping

from agicore.risk.exposure_models import ExecutionIntent, ExposureSnapshot, IntentSide, RiskLimits
from agicore.risk.risk_execution_authorization import (
    RiskAuthorizationBoundary,
    RiskAuthorizationConsumption,
)
from agicore.risk.risk_execution_context import (
    FillTransition,
    RiskContextError,
    RiskExecutionContext,
    RiskExecutionJournalEvent,
    replay_journal,
    validate_journal,
)

from .broker_models import OrderSide, OrderStatus, OrderType


TRANSACTION_SCHEMA_VERSION = "l5-execution-transaction/1.0"
PLAN_SCHEMA_VERSION = "l5-execution-plan/1.0"
ELIGIBILITY_SCHEMA_VERSION = "l5-limit-eligibility/1.0"
GENESIS_TRANSACTION_HASH = hashlib.sha256(
    b'{"schema_version":"l5-execution-transaction/1.0","type":"GENESIS"}'
).hexdigest()
OPERATION_KINDS = frozenset({"MARKET", "LIMIT_PLACEMENT", "LIMIT_FILL"})
TRANSACTION_EVENT_TYPES = frozenset(
    {"AGGREGATE_INITIALIZED", "MARKET_COMMITTED", "LIMIT_PLACED", "LIMIT_FILLED"}
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
        elif self.filled_at is not None or self.filled_price is not None:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_DATA", "non-filled order cannot publish fill fields")

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
    ) -> "L5ExecutionTransactionEvent":
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
        if not _is_hash(self.aggregate_state_hash) or not _is_hash(self.eligibility_hash):
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
        market_price: float,
        observed_at: datetime,
    ) -> "L5LimitFillEligibility":
        price = _number(market_price, "market_price", positive=True)
        observed = _explicit_time(observed_at, "observed_at")
        if order.order_type != OrderType.LIMIT or order.status != OrderStatus.PENDING or order.limit_price is None:
            raise L5ExecutionTransactionError("INVALID_LIMIT_ORDER", "order is not a pending LIMIT")
        eligible = price <= order.limit_price if order.side == OrderSide.BUY else price >= order.limit_price
        fields = {
            "schema_version": ELIGIBILITY_SCHEMA_VERSION,
            "eligibility_id": _identifier(eligibility_id, "eligibility_id"),
            "order_id": order.order_id,
            "aggregate_state_version": state.state_version,
            "aggregate_state_hash": state.state_hash,
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
        except Exception:
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
) -> L5LimitFillEligibility:
    expected = L5LimitFillEligibility._create(
        eligibility_id=eligibility.eligibility_id,
        order=order,
        state=state,
        market_price=eligibility.market_price,
        observed_at=eligibility.observed_at,
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
                or self.eligibility is not None
                or self.transition is not None
            ):
                raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "LIMIT_PLACEMENT fields are invalid")
        elif self.operation_kind == "LIMIT_FILL":
            if (
                self.fill_id is None
                or self.filled_at is None
                or self.eligibility is None
                or self.transition is None
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
        eligibility: L5LimitFillEligibility | None = None,
        transition: FillTransition | None = None,
    ) -> "L5ExecutionTransactionPlan":
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
                and (self.eligibility is None or self.eligibility.is_intact())
                and (self.transition is None or isinstance(self.transition, FillTransition))
                and self.intent_hash == _sha256(_intent_payload(self.intent))
                and self.plan_hash == _sha256(self.fields_without_hash())
                and self.next_state.state_version == self.expected_state_version + 1
            )
        except Exception:
            return False


class AggregateRiskContextProvider:
    """Read-only RiskContextProvider view over the aggregate state."""

    def __init__(self, store: "L5ExecutionTransactionStore") -> None:
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
        initial_positions: Mapping[str, L5TransactionPosition] | None = None,
    ) -> None:
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
        self._state = replace(base, execution_journal=(genesis,))
        self._lock = threading.RLock()
        self._context_provider = AggregateRiskContextProvider(self)

    @property
    def state(self) -> L5ExecutionAggregateState:
        with self._lock:
            return self._state

    @property
    def context_provider(self) -> AggregateRiskContextProvider:
        return self._context_provider

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
    ) -> L5ExecutionTransactionPlan:
        self._validate_consumption_provenance(boundary, consumption)
        with self._lock:
            current = self._state
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
            current = self._state
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
        market_price: float,
        observed_at: datetime,
    ) -> L5LimitFillEligibility:
        with self._lock:
            order = self._state.orders.get(order_id)
            if order is None:
                raise L5ExecutionTransactionError("ORDER_NOT_FOUND", "pending order does not exist")
            return L5LimitFillEligibility._create(
                eligibility_id=eligibility_id, order=order, state=self._state,
                market_price=market_price, observed_at=observed_at,
            )

    def prepare_limit_fill(
        self,
        *,
        boundary: RiskAuthorizationBoundary,
        intent: ExecutionIntent,
        consumption: RiskAuthorizationConsumption,
        eligibility: L5LimitFillEligibility,
        operation_id: str,
        fill_id: str,
        report_id: str,
        filled_at: datetime,
        transition: FillTransition,
    ) -> L5ExecutionTransactionPlan:
        self._validate_consumption_provenance(boundary, consumption)
        with self._lock:
            current = self._state
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
    ) -> L5ExecutionTransactionPlan:
        _intent_payload(intent)
        submitted = _explicit_time(submitted_at, "submitted_at")
        filled = _explicit_time(filled_at, "filled_at")
        price = _number(fill_price, "fill_price", positive=True)
        if intent.timestamp > submitted or submitted > filled:
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_CHRONOLOGY", "MARKET chronology is invalid")
        if price != float(intent.estimated_price):
            raise L5ExecutionTransactionError("AUTHORIZED_PRICE_MISMATCH", "fill price differs from authorized price")
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
    ) -> L5ExecutionTransactionPlan:
        _intent_payload(intent)
        filled = _explicit_time(filled_at, "filled_at")
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
        authoritative_eligibility = _require_authoritative_limit_eligibility(current, order, eligibility)
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
            eligibility=eligibility,
            transition=transition,
        )

    def commit(
        self,
        plan: L5ExecutionTransactionPlan,
        *,
        boundary: RiskAuthorizationBoundary,
    ) -> L5ExecutionAggregateState:
        if not isinstance(plan, L5ExecutionTransactionPlan) or not plan.is_intact():
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_PLAN", "plan integrity check failed")
        self._validate_consumption_provenance(boundary, plan.consumption)
        with self._lock:
            current = self._state
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
            expected_plan = self._reconstruct_plan(plan, current)
            if expected_plan != plan:
                raise L5ExecutionTransactionError(
                    "INVALID_TRANSACTION_SEMANTICS",
                    "plan differs from deterministic reconstruction",
                )
            self._validate_next_state(expected_plan, current)
            try:
                self._publish_state(expected_plan.next_state)
            except Exception as exc:
                raise L5ExecutionTransactionError("TRANSACTION_PUBLICATION_FAILED", "aggregate publication failed") from exc
            return self._state

    def _publish_state(self, next_state: L5ExecutionAggregateState) -> None:
        self._state = next_state

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
    if not isinstance(inputs, dict) or not isinstance(inputs.get("intent"), dict):
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "operation inputs are missing")
    intent = inputs["intent"]
    if after.state_version != before.state_version + 1:
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "aggregate version delta is invalid")
    if after.execution_journal[:-1] != before.execution_journal or after.execution_journal[-1] != event:
        raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "execution journal prefix differs")
    if event.event_type == "MARKET_COMMITTED":
        order_key = _single_added_key(before.orders, after.orders, "orders")
        fill_key = _single_added_key(before.fills, after.fills, "fills")
        report_key = _single_added_key(before.reports, after.reports, "reports")
        order = after.orders[order_key]
        fill = after.fills[fill_key]
        report = after.reports[report_key]
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
        ):
            raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "MARKET operation inputs differ")
        intent_time = _parse_explicit_time(intent.get("timestamp"), "intent timestamp")
        if not intent_time <= order.submitted_at <= fill.filled_at:
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
        authoritative_eligibility = _require_authoritative_limit_eligibility(
            before,
            previous_order,
            supplied_eligibility,
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
            consumption_hash = event.payload.get("consumption_hash")
            if not _is_hash(consumption_hash):
                raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "consumption_hash is invalid")
            if not isinstance(event.payload.get("operation_inputs"), Mapping):
                raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "operation inputs are missing")
            if consumption_hash in seen_consumptions:
                raise L5ExecutionTransactionError("INVALID_TRANSACTION_JOURNAL", "consumption_hash is duplicated")
            seen_consumptions.add(consumption_hash)
        previous = event.event_hash
    if expected_final_hash is not None:
        if not _is_hash(expected_final_hash) or previous != expected_final_hash:
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


__all__ = [
    "AggregateRiskContextProvider", "ELIGIBILITY_SCHEMA_VERSION", "GENESIS_TRANSACTION_HASH",
    "L5ExecutionAggregateState", "L5ExecutionTransactionError", "L5ExecutionTransactionEvent",
    "L5ExecutionTransactionPlan", "L5ExecutionTransactionStore", "L5LimitFillEligibility",
    "L5TransactionFill", "L5TransactionOrder", "L5TransactionPosition", "L5TransactionReport",
    "PLAN_SCHEMA_VERSION", "TRANSACTION_SCHEMA_VERSION", "replay_execution_transaction_journal",
    "validate_execution_transaction_journal",
]
