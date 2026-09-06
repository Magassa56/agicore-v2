"""Deterministic in-process outcome outbox and consumer inbox for canonical L5.

The outbox is embedded in the transaction store's single authority object.
It provides at-least-once delivery with idempotent consumer acceptance; it is
not a durable or distributed exactly-once transport.
"""
from __future__ import annotations

import hashlib
import json
import math
import threading
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

OUTCOME_SCHEMA_VERSION = "l5-execution-outcome/1.1"
DELIVERY_SCHEMA_VERSION = "l5-execution-delivery/1.1"
INBOX_SCHEMA_VERSION = "l5-execution-inbox/1.1"
DELIVERY_EVENT_TYPES = frozenset({"DELIVERY_INITIALIZED", "OUTCOME_PUBLISHED", "OUTCOME_ACKNOWLEDGED"})
INBOX_EVENT_TYPES = frozenset({"INBOX_INITIALIZED", "OUTCOME_ACCEPTED", "EFFECT_COMPLETED"})
OUTCOME_OPERATION_KINDS = frozenset(
    {"MARKET", "LIMIT_PLACEMENT", "LIMIT_FILL", "LIMIT_CANCELLATION"}
)
OUTCOME_STATUSES = frozenset({"FILLED", "PENDING", "CANCELLED", "REJECTED"})
GENESIS_DELIVERY_HASH = hashlib.sha256(
    b'{"schema_version":"l5-execution-delivery/1.1","type":"GENESIS"}'
).hexdigest()
GENESIS_INBOX_HASH = hashlib.sha256(
    b'{"schema_version":"l5-execution-inbox/1.1","type":"GENESIS"}'
).hexdigest()


class L5ExecutionDeliveryError(ValueError):
    """Controlled outbox/inbox contract failure."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


def _canonical_json(value: object) -> str:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise L5ExecutionDeliveryError(
            "INVALID_DELIVERY_DATA",
            "value is not canonically serializable",
        ) from exc


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _is_hash(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _identifier(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise L5ExecutionDeliveryError("INVALID_DELIVERY_DATA", f"{name} must be non-blank")
    return value


def _optional_identifier(value: object, name: str) -> str | None:
    return None if value is None else _identifier(value, name)


def _integer(value: object, name: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise L5ExecutionDeliveryError("INVALID_DELIVERY_DATA", f"{name} is invalid")
    return value


def _freeze_json(value: object) -> object:
    if isinstance(value, Mapping):
        copied: dict[str, object] = {}
        for key, nested in value.items():
            if not isinstance(key, str):
                raise L5ExecutionDeliveryError(
                    "INVALID_DELIVERY_DATA",
                    "canonical mapping keys must be strings",
                )
            copied[key] = _freeze_json(nested)
        return MappingProxyType(copied)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(nested) for nested in value)
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_DATA", "numeric value must be finite")
        return value
    raise L5ExecutionDeliveryError("INVALID_DELIVERY_DATA", "payload must contain canonical JSON values")


def _thaw_json(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _thaw_json(nested) for key, nested in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(nested) for nested in value]
    return value


@dataclass(frozen=True)
class L5ExecutionOutcomeSpec:
    """Primitive, immutable inputs from which the store finalizes an outcome."""

    request_payload: Mapping[str, object]
    intent_id: str
    intent_hash: str
    operation_kind: str
    final_status: str
    committed: bool
    requested_order_id: str
    operation_id: str | None
    order_id: str | None
    fill_id: str | None
    report_id: str | None
    authorization_id: str | None
    decision_hash: str | None
    consumption_id: str | None
    consumption_hash: str | None
    provider_id: str
    risk_limits_hash: str | None
    context_state_version: int
    context_state_hash: str
    aggregate_state_version_before: int
    aggregate_state_hash_before: str
    decision_evidence: Mapping[str, object] | None
    consumption_evidence: Mapping[str, object] | None
    risk_context_evidence: Mapping[str, object]
    violation_codes: tuple[str, ...] = ()
    price_identity: Mapping[str, object] | None = None
    explicit_times: Mapping[str, object] = MappingProxyType({})
    execution_price: float | None = None
    authorized_price: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "request_payload", _freeze_json(self.request_payload))
        object.__setattr__(self, "intent_id", _identifier(self.intent_id, "intent_id"))
        object.__setattr__(self, "requested_order_id", _identifier(self.requested_order_id, "requested_order_id"))
        if self.operation_kind not in OUTCOME_OPERATION_KINDS:
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_DATA", "operation_kind is invalid")
        if self.final_status not in OUTCOME_STATUSES or not isinstance(self.committed, bool):
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_DATA", "outcome status is invalid")
        for name in (
            "operation_id", "order_id", "fill_id", "report_id", "authorization_id",
            "consumption_id", "risk_limits_hash",
        ):
            object.__setattr__(self, name, _optional_identifier(getattr(self, name), name))
        object.__setattr__(self, "provider_id", _identifier(self.provider_id, "provider_id"))
        for name in (
            "intent_hash", "decision_hash", "consumption_hash", "context_state_hash",
            "aggregate_state_hash_before",
        ):
            value = getattr(self, name)
            if value is not None and not _is_hash(value):
                raise L5ExecutionDeliveryError("INVALID_DELIVERY_DATA", f"{name} is invalid")
        object.__setattr__(self, "context_state_version", _integer(self.context_state_version, "context_state_version"))
        object.__setattr__(
            self,
            "aggregate_state_version_before",
            _integer(self.aggregate_state_version_before, "aggregate_state_version_before"),
        )
        object.__setattr__(
            self,
            "decision_evidence",
            None if self.decision_evidence is None else _freeze_json(self.decision_evidence),
        )
        object.__setattr__(
            self,
            "consumption_evidence",
            None if self.consumption_evidence is None else _freeze_json(self.consumption_evidence),
        )
        object.__setattr__(self, "risk_context_evidence", _freeze_json(self.risk_context_evidence))
        if not isinstance(self.violation_codes, tuple):
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_DATA", "violation_codes must be a tuple")
        object.__setattr__(
            self,
            "violation_codes",
            tuple(_identifier(code, "violation_code") for code in self.violation_codes),
        )
        object.__setattr__(
            self,
            "price_identity",
            None if self.price_identity is None else _freeze_json(self.price_identity),
        )
        object.__setattr__(self, "explicit_times", _freeze_json(self.explicit_times))
        for price_name in ("execution_price", "authorized_price"):
            price_value = getattr(self, price_name)
            if price_value is None:
                continue
            if (
                isinstance(price_value, bool)
                or not isinstance(price_value, (int, float))
                or not math.isfinite(float(price_value))
                or float(price_value) <= 0
            ):
                raise L5ExecutionDeliveryError("INVALID_DELIVERY_DATA", f"{price_name} is invalid")
            object.__setattr__(self, price_name, float(price_value))
        if self.committed:
            if self.final_status == "REJECTED" or self.operation_id is None or self.order_id is None or self.report_id is None:
                raise L5ExecutionDeliveryError("INVALID_DELIVERY_DATA", "committed outcome identities are incomplete")
            if self.operation_kind != "LIMIT_CANCELLATION" and (
                self.authorization_id is None
                or self.decision_hash is None
                or self.consumption_id is None
                or self.consumption_hash is None
                or self.risk_limits_hash is None
                or self.decision_evidence is None
                or self.consumption_evidence is None
            ):
                raise L5ExecutionDeliveryError("INVALID_DELIVERY_DATA", "risk evidence is incomplete")
            if self.operation_kind == "LIMIT_CANCELLATION" and any(
                value is not None
                for value in (
                    self.authorization_id,
                    self.decision_hash,
                    self.consumption_id,
                    self.consumption_hash,
                    self.risk_limits_hash,
                    self.decision_evidence,
                    self.consumption_evidence,
                )
            ):
                raise L5ExecutionDeliveryError("INVALID_DELIVERY_DATA", "cancellation cannot publish risk evidence")
        elif (
            self.final_status != "REJECTED"
            or self.decision_hash is None
            or not self.violation_codes
            or self.consumption_hash is not None
            or self.order_id is not None
            or self.fill_id is not None
            or self.report_id is not None
            or self.decision_evidence is None
            or self.consumption_evidence is not None
        ):
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_DATA", "rejection outcome is inconsistent")
        if (
            self.decision_hash is not None
            and self.authorization_id != f"risk-auth-{self.decision_hash}"
        ):
            raise L5ExecutionDeliveryError(
                "INVALID_DELIVERY_DATA",
                "authorization identity differs from the decision hash",
            )

    @property
    def request_hash(self) -> str:
        return _sha256(_thaw_json(self.request_payload))


@dataclass(frozen=True)
class L5ExecutionOutcome:
    schema_version: str
    outcome_id: str
    request_hash: str
    request_payload: Mapping[str, object]
    intent_id: str
    intent_hash: str
    operation_kind: str
    final_status: str
    committed: bool
    requested_order_id: str
    operation_id: str | None
    order_id: str | None
    fill_id: str | None
    report_id: str | None
    authorization_id: str | None
    decision_hash: str | None
    consumption_id: str | None
    consumption_hash: str | None
    provider_id: str
    risk_limits_hash: str | None
    context_state_version: int
    context_state_hash: str
    context_state_version_after: int
    context_state_hash_after: str
    aggregate_state_version_before: int
    aggregate_state_hash_before: str
    aggregate_state_version: int
    aggregate_state_hash: str
    transaction_event_hash: str | None
    transaction_sequence_number: int | None
    transaction_event_type: str | None
    decision_evidence: Mapping[str, object] | None
    consumption_evidence: Mapping[str, object] | None
    risk_context_evidence: Mapping[str, object]
    violation_codes: tuple[str, ...]
    price_identity: Mapping[str, object] | None
    explicit_times: Mapping[str, object]
    execution_price: float | None
    authorized_price: float | None
    outcome_hash: str

    def __post_init__(self) -> None:
        if self.schema_version != OUTCOME_SCHEMA_VERSION:
            raise L5ExecutionDeliveryError("INVALID_OUTCOME", "outcome schema is invalid")
        for name in ("outcome_id", "intent_id", "requested_order_id", "provider_id"):
            object.__setattr__(self, name, _identifier(getattr(self, name), name))
        if self.operation_kind not in OUTCOME_OPERATION_KINDS or self.final_status not in OUTCOME_STATUSES:
            raise L5ExecutionDeliveryError("INVALID_OUTCOME", "outcome operation or status is invalid")
        if not isinstance(self.committed, bool):
            raise L5ExecutionDeliveryError("INVALID_OUTCOME", "committed must be boolean")
        for name in ("operation_id", "order_id", "fill_id", "report_id", "authorization_id", "consumption_id"):
            object.__setattr__(self, name, _optional_identifier(getattr(self, name), name))
        for name in (
            "request_hash", "intent_hash", "context_state_hash", "context_state_hash_after",
            "aggregate_state_hash_before", "aggregate_state_hash", "outcome_hash",
            "decision_hash", "consumption_hash", "risk_limits_hash", "transaction_event_hash",
        ):
            value = getattr(self, name)
            if value is not None and not _is_hash(value):
                raise L5ExecutionDeliveryError("INVALID_OUTCOME", f"{name} is invalid")
        object.__setattr__(self, "context_state_version", _integer(self.context_state_version, "context_state_version"))
        object.__setattr__(self, "context_state_version_after", _integer(self.context_state_version_after, "context_state_version_after"))
        object.__setattr__(self, "aggregate_state_version_before", _integer(self.aggregate_state_version_before, "aggregate_state_version_before"))
        object.__setattr__(self, "aggregate_state_version", _integer(self.aggregate_state_version, "aggregate_state_version"))
        object.__setattr__(self, "request_payload", _freeze_json(self.request_payload))
        object.__setattr__(self, "explicit_times", _freeze_json(self.explicit_times))
        object.__setattr__(self, "decision_evidence", None if self.decision_evidence is None else _freeze_json(self.decision_evidence))
        object.__setattr__(self, "consumption_evidence", None if self.consumption_evidence is None else _freeze_json(self.consumption_evidence))
        object.__setattr__(self, "risk_context_evidence", _freeze_json(self.risk_context_evidence))
        object.__setattr__(
            self,
            "price_identity",
            None if self.price_identity is None else _freeze_json(self.price_identity),
        )
        if not isinstance(self.violation_codes, tuple):
            raise L5ExecutionDeliveryError("INVALID_OUTCOME", "violation_codes must be a tuple")
        object.__setattr__(self, "violation_codes", tuple(_identifier(code, "violation_code") for code in self.violation_codes))
        if self.transaction_sequence_number is not None:
            object.__setattr__(self, "transaction_sequence_number", _integer(self.transaction_sequence_number, "transaction_sequence_number", minimum=1))
        object.__setattr__(self, "transaction_event_type", _optional_identifier(self.transaction_event_type, "transaction_event_type"))
        for price_name in ("execution_price", "authorized_price"):
            price_value = getattr(self, price_name)
            if price_value is None:
                continue
            if (
                isinstance(price_value, bool)
                or not isinstance(price_value, (int, float))
                or not math.isfinite(float(price_value))
                or float(price_value) <= 0
            ):
                raise L5ExecutionDeliveryError("INVALID_OUTCOME", f"{price_name} is invalid")
            object.__setattr__(self, price_name, float(price_value))
        if self.committed:
            if self.operation_kind != "LIMIT_CANCELLATION" and any(
                value is None
                for value in (
                    self.authorization_id,
                    self.decision_hash,
                    self.consumption_id,
                    self.consumption_hash,
                    self.risk_limits_hash,
                    self.decision_evidence,
                    self.consumption_evidence,
                )
            ):
                raise L5ExecutionDeliveryError("INVALID_OUTCOME", "committed risk evidence is incomplete")
            if self.operation_kind == "LIMIT_CANCELLATION" and any(
                value is not None
                for value in (
                    self.authorization_id,
                    self.decision_hash,
                    self.consumption_id,
                    self.consumption_hash,
                    self.risk_limits_hash,
                    self.decision_evidence,
                    self.consumption_evidence,
                )
            ):
                raise L5ExecutionDeliveryError("INVALID_OUTCOME", "cancellation risk evidence is invalid")
            expected_status = {
                "MARKET": "FILLED",
                "LIMIT_PLACEMENT": "PENDING",
                "LIMIT_FILL": "FILLED",
                "LIMIT_CANCELLATION": "CANCELLED",
            }[self.operation_kind]
            if self.final_status != expected_status:
                raise L5ExecutionDeliveryError("INVALID_OUTCOME", "operation status is inconsistent")
            if (self.final_status == "FILLED") != (self.fill_id is not None):
                raise L5ExecutionDeliveryError("INVALID_OUTCOME", "fill identity is inconsistent")
        elif (
            self.authorization_id is None
            or self.decision_hash is None
            or self.consumption_id is not None
            or self.consumption_hash is not None
            or self.order_id is not None
            or self.fill_id is not None
            or self.report_id is not None
            or not self.violation_codes
            or self.decision_evidence is None
            or self.consumption_evidence is not None
        ):
            raise L5ExecutionDeliveryError("INVALID_OUTCOME", "rejection evidence is inconsistent")
        if (
            self.decision_hash is not None
            and self.authorization_id != f"risk-auth-{self.decision_hash}"
        ):
            raise L5ExecutionDeliveryError(
                "INVALID_OUTCOME",
                "authorization identity differs from the decision hash",
            )

    @classmethod
    def from_spec(
        cls,
        spec: L5ExecutionOutcomeSpec,
        *,
        aggregate_state_version: int,
        aggregate_state_hash: str,
        transaction_event_hash: str | None,
        transaction_sequence_number: int | None,
        transaction_event_type: str | None,
        context_state_version_after: int,
        context_state_hash_after: str,
    ) -> L5ExecutionOutcome:
        if not isinstance(spec, L5ExecutionOutcomeSpec):
            raise L5ExecutionDeliveryError("INVALID_OUTCOME", "outcome spec is invalid")
        identity = {
            "request_hash": spec.request_hash,
            "intent_id": spec.intent_id,
            "operation_kind": spec.operation_kind,
        }
        outcome_id = f"l5-outcome-{_sha256(identity)}"
        fields = {
            "schema_version": OUTCOME_SCHEMA_VERSION,
            "outcome_id": outcome_id,
            "request_hash": spec.request_hash,
            "request_payload": _thaw_json(spec.request_payload),
            "intent_id": spec.intent_id,
            "intent_hash": spec.intent_hash,
            "operation_kind": spec.operation_kind,
            "final_status": spec.final_status,
            "committed": spec.committed,
            "requested_order_id": spec.requested_order_id,
            "operation_id": spec.operation_id,
            "order_id": spec.order_id,
            "fill_id": spec.fill_id,
            "report_id": spec.report_id,
            "authorization_id": spec.authorization_id,
            "decision_hash": spec.decision_hash,
            "consumption_id": spec.consumption_id,
            "consumption_hash": spec.consumption_hash,
            "provider_id": spec.provider_id,
            "risk_limits_hash": spec.risk_limits_hash,
            "context_state_version": spec.context_state_version,
            "context_state_hash": spec.context_state_hash,
            "context_state_version_after": context_state_version_after,
            "context_state_hash_after": context_state_hash_after,
            "aggregate_state_version_before": spec.aggregate_state_version_before,
            "aggregate_state_hash_before": spec.aggregate_state_hash_before,
            "aggregate_state_version": aggregate_state_version,
            "aggregate_state_hash": aggregate_state_hash,
            "transaction_event_hash": transaction_event_hash,
            "transaction_sequence_number": transaction_sequence_number,
            "transaction_event_type": transaction_event_type,
            "decision_evidence": None if spec.decision_evidence is None else _thaw_json(spec.decision_evidence),
            "consumption_evidence": None if spec.consumption_evidence is None else _thaw_json(spec.consumption_evidence),
            "risk_context_evidence": _thaw_json(spec.risk_context_evidence),
            "violation_codes": list(spec.violation_codes),
            "price_identity": None if spec.price_identity is None else _thaw_json(spec.price_identity),
            "explicit_times": _thaw_json(spec.explicit_times),
            "execution_price": spec.execution_price,
            "authorized_price": spec.authorized_price,
        }
        constructor_fields = dict(fields)
        constructor_fields["violation_codes"] = tuple(spec.violation_codes)
        return cls(outcome_hash=_sha256(fields), **constructor_fields)

    def fields_without_hash(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "outcome_id": self.outcome_id,
            "request_hash": self.request_hash,
            "request_payload": _thaw_json(self.request_payload),
            "intent_id": self.intent_id,
            "intent_hash": self.intent_hash,
            "operation_kind": self.operation_kind,
            "final_status": self.final_status,
            "committed": self.committed,
            "requested_order_id": self.requested_order_id,
            "operation_id": self.operation_id,
            "order_id": self.order_id,
            "fill_id": self.fill_id,
            "report_id": self.report_id,
            "authorization_id": self.authorization_id,
            "decision_hash": self.decision_hash,
            "consumption_id": self.consumption_id,
            "consumption_hash": self.consumption_hash,
            "provider_id": self.provider_id,
            "risk_limits_hash": self.risk_limits_hash,
            "context_state_version": self.context_state_version,
            "context_state_hash": self.context_state_hash,
            "context_state_version_after": self.context_state_version_after,
            "context_state_hash_after": self.context_state_hash_after,
            "aggregate_state_version_before": self.aggregate_state_version_before,
            "aggregate_state_hash_before": self.aggregate_state_hash_before,
            "aggregate_state_version": self.aggregate_state_version,
            "aggregate_state_hash": self.aggregate_state_hash,
            "transaction_event_hash": self.transaction_event_hash,
            "transaction_sequence_number": self.transaction_sequence_number,
            "transaction_event_type": self.transaction_event_type,
            "decision_evidence": None if self.decision_evidence is None else _thaw_json(self.decision_evidence),
            "consumption_evidence": None if self.consumption_evidence is None else _thaw_json(self.consumption_evidence),
            "risk_context_evidence": _thaw_json(self.risk_context_evidence),
            "violation_codes": list(self.violation_codes),
            "price_identity": None if self.price_identity is None else _thaw_json(self.price_identity),
            "explicit_times": _thaw_json(self.explicit_times),
            "execution_price": self.execution_price,
            "authorized_price": self.authorized_price,
        }

    def canonical(self) -> dict[str, object]:
        return {**self.fields_without_hash(), "outcome_hash": self.outcome_hash}

    def is_intact(self) -> bool:
        try:
            return (
                self.schema_version == OUTCOME_SCHEMA_VERSION
                and self.outcome_id == f"l5-outcome-{_sha256({'request_hash': self.request_hash, 'intent_id': self.intent_id, 'operation_kind': self.operation_kind})}"
                and self.request_hash == _sha256(_thaw_json(self.request_payload))
                and _is_hash(self.intent_hash)
                and self.outcome_hash == _sha256(self.fields_without_hash())
                and (
                    self.decision_hash is None
                    or self.authorization_id == f"risk-auth-{self.decision_hash}"
                )
                and (
                    (
                        self.committed
                        and self.transaction_event_hash is not None
                        and self.transaction_sequence_number is not None
                        and self.transaction_event_type is not None
                        and self.aggregate_state_version == self.aggregate_state_version_before + 1
                    )
                    or (
                        not self.committed
                        and self.final_status == "REJECTED"
                        and self.transaction_event_hash is None
                        and self.transaction_sequence_number is None
                        and self.transaction_event_type is None
                        and self.aggregate_state_version == self.aggregate_state_version_before
                        and self.aggregate_state_hash == self.aggregate_state_hash_before
                    )
                )
                and ((self.committed and self.order_id is not None and self.report_id is not None) or (not self.committed and self.order_id is None and self.report_id is None and self.fill_id is None))
                and ((self.committed and not self.violation_codes) or (not self.committed and bool(self.violation_codes)))
            )
        except Exception:  # noqa: BLE001 - malformed persisted evidence must fail closed
            return False

    @classmethod
    def from_canonical(cls, value: object) -> L5ExecutionOutcome:
        if not isinstance(value, Mapping):
            raise L5ExecutionDeliveryError("INVALID_OUTCOME", "outcome payload is invalid")
        data = _thaw_json(value)
        try:
            return cls(
                **{
                    **data,
                    "violation_codes": tuple(data["violation_codes"]),
                }
            )
        except (KeyError, TypeError, ValueError, L5ExecutionDeliveryError) as exc:
            if isinstance(exc, L5ExecutionDeliveryError):
                raise
            raise L5ExecutionDeliveryError("INVALID_OUTCOME", "outcome payload is malformed") from exc


@dataclass(frozen=True)
class L5ExecutionInboxReceipt:
    schema_version: str
    receipt_id: str
    consumer_id: str
    outcome_id: str
    outcome_hash: str
    required_effects: tuple[str, ...]
    receipt_hash: str

    def __post_init__(self) -> None:
        if not isinstance(self.required_effects, tuple):
            object.__setattr__(self, "required_effects", tuple(self.required_effects))

    @classmethod
    def create(
        cls,
        consumer_id: str,
        outcome: L5ExecutionOutcome,
        required_effects: tuple[str, ...] = (),
    ) -> L5ExecutionInboxReceipt:
        if not isinstance(outcome, L5ExecutionOutcome) or not outcome.is_intact():
            raise L5ExecutionDeliveryError("INVALID_OUTCOME", "outcome integrity failed")
        consumer = _identifier(consumer_id, "consumer_id")
        if not isinstance(required_effects, tuple):
            raise L5ExecutionDeliveryError("INVALID_RECEIPT", "required_effects must be a tuple")
        effects = tuple(sorted({_identifier(item, "effect_name") for item in required_effects}))
        identity = {
            "consumer_id": consumer,
            "outcome_id": outcome.outcome_id,
            "outcome_hash": outcome.outcome_hash,
            "required_effects": list(effects),
        }
        receipt_id = f"l5-receipt-{_sha256(identity)}"
        fields = {
            "schema_version": INBOX_SCHEMA_VERSION,
            "receipt_id": receipt_id,
            **identity,
        }
        return cls(receipt_hash=_sha256(fields), required_effects=effects, **{key: value for key, value in fields.items() if key != "required_effects"})

    def fields_without_hash(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "receipt_id": self.receipt_id,
            "consumer_id": self.consumer_id,
            "outcome_id": self.outcome_id,
            "outcome_hash": self.outcome_hash,
            "required_effects": list(self.required_effects),
        }

    def canonical(self) -> dict[str, object]:
        return {**self.fields_without_hash(), "receipt_hash": self.receipt_hash}

    def is_intact(self) -> bool:
        try:
            identity = {
                "consumer_id": self.consumer_id,
                "outcome_id": self.outcome_id,
                "outcome_hash": self.outcome_hash,
                "required_effects": list(self.required_effects),
            }
            return (
                self.schema_version == INBOX_SCHEMA_VERSION
                and self.receipt_id == f"l5-receipt-{_sha256(identity)}"
                and _is_hash(self.outcome_hash)
                and self.receipt_hash == _sha256(self.fields_without_hash())
            )
        except Exception:  # noqa: BLE001 - malformed persisted evidence must fail closed
            return False


@dataclass(frozen=True)
class L5ExecutionDeliveryAcknowledgement:
    schema_version: str
    acknowledgement_id: str
    consumer_id: str
    outcome_id: str
    outcome_hash: str
    receipt_id: str
    receipt_hash: str
    acceptance_event_hash: str
    effect_event_hashes: Mapping[str, str]
    inbox_anchor_hash: str
    emission_accepted_hash: str | None
    acknowledgement_hash: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "effect_event_hashes", MappingProxyType(dict(self.effect_event_hashes)))

    @classmethod
    def create(
        cls,
        receipt: L5ExecutionInboxReceipt,
        *,
        acceptance_event_hash: str,
        effect_event_hashes: Mapping[str, str],
        inbox_anchor_hash: str,
        emission_accepted_hash: str | None = None,
    ) -> L5ExecutionDeliveryAcknowledgement:
        if not isinstance(receipt, L5ExecutionInboxReceipt) or not receipt.is_intact():
            raise L5ExecutionDeliveryError("INVALID_RECEIPT", "receipt integrity failed")
        if not all(_is_hash(value) for value in (acceptance_event_hash, inbox_anchor_hash)):
            raise L5ExecutionDeliveryError("INVALID_ACKNOWLEDGEMENT", "inbox causal hashes are invalid")
        if emission_accepted_hash is not None and not _is_hash(emission_accepted_hash):
            raise L5ExecutionDeliveryError(
                "INVALID_ACKNOWLEDGEMENT",
                "durable emission acceptance hash is invalid",
            )
        effects = dict(effect_event_hashes)
        if set(effects) != set(receipt.required_effects) or any(not _is_hash(value) for value in effects.values()):
            raise L5ExecutionDeliveryError("INCOMPLETE_EFFECTS", "required effects are not all complete")
        identity = {
            "consumer_id": receipt.consumer_id,
            "outcome_id": receipt.outcome_id,
            "outcome_hash": receipt.outcome_hash,
            "receipt_id": receipt.receipt_id,
            "receipt_hash": receipt.receipt_hash,
            "acceptance_event_hash": acceptance_event_hash,
            "effect_event_hashes": dict(sorted(effects.items())),
            "inbox_anchor_hash": inbox_anchor_hash,
            "emission_accepted_hash": emission_accepted_hash,
        }
        acknowledgement_id = f"l5-ack-{_sha256(identity)}"
        fields = {
            "schema_version": DELIVERY_SCHEMA_VERSION,
            "acknowledgement_id": acknowledgement_id,
            **identity,
        }
        return cls(
            acknowledgement_hash=_sha256(fields),
            effect_event_hashes=MappingProxyType(dict(sorted(effects.items()))),
            **{key: value for key, value in fields.items() if key != "effect_event_hashes"},
        )

    def fields_without_hash(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "acknowledgement_id": self.acknowledgement_id,
            "consumer_id": self.consumer_id,
            "outcome_id": self.outcome_id,
            "outcome_hash": self.outcome_hash,
            "receipt_id": self.receipt_id,
            "receipt_hash": self.receipt_hash,
            "acceptance_event_hash": self.acceptance_event_hash,
            "effect_event_hashes": dict(sorted(self.effect_event_hashes.items())),
            "inbox_anchor_hash": self.inbox_anchor_hash,
            "emission_accepted_hash": self.emission_accepted_hash,
        }

    def canonical(self) -> dict[str, object]:
        return {**self.fields_without_hash(), "acknowledgement_hash": self.acknowledgement_hash}

    def is_intact(self) -> bool:
        try:
            identity = {
                "consumer_id": self.consumer_id,
                "outcome_id": self.outcome_id,
                "outcome_hash": self.outcome_hash,
                "receipt_id": self.receipt_id,
                "receipt_hash": self.receipt_hash,
                "acceptance_event_hash": self.acceptance_event_hash,
                "effect_event_hashes": dict(sorted(self.effect_event_hashes.items())),
                "inbox_anchor_hash": self.inbox_anchor_hash,
                "emission_accepted_hash": self.emission_accepted_hash,
            }
            return (
                self.schema_version == DELIVERY_SCHEMA_VERSION
                and self.acknowledgement_id == f"l5-ack-{_sha256(identity)}"
                and _is_hash(self.outcome_hash)
                and _is_hash(self.receipt_hash)
                and _is_hash(self.acceptance_event_hash)
                and _is_hash(self.inbox_anchor_hash)
                and (
                    self.emission_accepted_hash is None
                    or _is_hash(self.emission_accepted_hash)
                )
                and all(_is_hash(value) for value in self.effect_event_hashes.values())
                and self.acknowledgement_hash == _sha256(self.fields_without_hash())
            )
        except Exception:  # noqa: BLE001 - malformed persisted evidence must fail closed
            return False


@dataclass(frozen=True)
class L5ExecutionDeliveryEvent:
    schema_version: str
    sequence_number: int
    event_type: str
    delivery_version_before: int
    delivery_hash_before: str
    payload: Mapping[str, object]
    previous_event_hash: str
    event_hash: str

    @classmethod
    def create(
        cls,
        *,
        sequence_number: int,
        event_type: str,
        delivery_version_before: int,
        delivery_hash_before: str,
        payload: Mapping[str, object],
        previous_event_hash: str,
    ) -> L5ExecutionDeliveryEvent:
        fields = {
            "schema_version": DELIVERY_SCHEMA_VERSION,
            "sequence_number": sequence_number,
            "event_type": event_type,
            "delivery_version_before": delivery_version_before,
            "delivery_hash_before": delivery_hash_before,
            "payload": _thaw_json(_freeze_json(payload)),
            "previous_event_hash": previous_event_hash,
        }
        return cls(event_hash=_sha256(fields), **fields)

    def __post_init__(self) -> None:
        if self.schema_version != DELIVERY_SCHEMA_VERSION or self.event_type not in DELIVERY_EVENT_TYPES:
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_EVENT", "delivery event contract is invalid")
        _integer(self.sequence_number, "sequence_number", minimum=1)
        _integer(self.delivery_version_before, "delivery_version_before")
        if not all(_is_hash(value) for value in (self.delivery_hash_before, self.previous_event_hash, self.event_hash)):
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_EVENT", "delivery event hash is invalid")
        object.__setattr__(self, "payload", _freeze_json(self.payload))

    def fields_without_hash(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "sequence_number": self.sequence_number,
            "event_type": self.event_type,
            "delivery_version_before": self.delivery_version_before,
            "delivery_hash_before": self.delivery_hash_before,
            "payload": _thaw_json(self.payload),
            "previous_event_hash": self.previous_event_hash,
        }

    def canonical(self) -> dict[str, object]:
        return {**self.fields_without_hash(), "event_hash": self.event_hash}


@dataclass(frozen=True)
class L5ExecutionDeliveryState:
    delivery_version: int
    outcomes: Mapping[str, L5ExecutionOutcome]
    intent_outcomes: Mapping[str, str]
    acknowledgements: Mapping[str, L5ExecutionDeliveryAcknowledgement]
    journal: tuple[L5ExecutionDeliveryEvent, ...]

    def __post_init__(self) -> None:
        _integer(self.delivery_version, "delivery_version")
        if not isinstance(self.journal, tuple):
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_STATE", "delivery journal must be a tuple")
        outcomes = dict(self.outcomes)
        intents = dict(self.intent_outcomes)
        acknowledgements = dict(self.acknowledgements)
        if any(key != value.outcome_id or not value.is_intact() for key, value in outcomes.items()):
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_STATE", "outcome mapping is invalid")
        if any(outcome_id not in outcomes or outcomes[outcome_id].intent_id != intent_id for intent_id, outcome_id in intents.items()):
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_STATE", "intent outcome mapping is invalid")
        if len(intents) != len(outcomes):
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_STATE", "each outcome must have one intent identity")
        if any(key != value.acknowledgement_id or not value.is_intact() for key, value in acknowledgements.items()):
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_STATE", "acknowledgement mapping is invalid")
        if any(
            acknowledgement.outcome_id not in outcomes
            or outcomes[acknowledgement.outcome_id].outcome_hash != acknowledgement.outcome_hash
            for acknowledgement in acknowledgements.values()
        ):
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_STATE", "acknowledgement is orphaned")
        consumer_outcomes = {
            (item.consumer_id, item.outcome_id)
            for item in acknowledgements.values()
        }
        if len(consumer_outcomes) != len(acknowledgements):
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_STATE", "consumer outcome acknowledgement is duplicated")
        object.__setattr__(self, "outcomes", MappingProxyType(outcomes))
        object.__setattr__(self, "intent_outcomes", MappingProxyType(intents))
        object.__setattr__(self, "acknowledgements", MappingProxyType(acknowledgements))

    def canonical_components(self) -> dict[str, object]:
        return {
            "delivery_version": self.delivery_version,
            "outcomes": {key: value.canonical() for key, value in sorted(self.outcomes.items())},
            "intent_outcomes": dict(sorted(self.intent_outcomes.items())),
            "acknowledgements": {key: value.canonical() for key, value in sorted(self.acknowledgements.items())},
        }

    @property
    def delivery_hash(self) -> str:
        return _sha256(
            {
                **self.canonical_components(),
                "journal": [event.canonical() for event in self.journal],
            }
        )

    @classmethod
    def initial(cls) -> L5ExecutionDeliveryState:
        base = cls(delivery_version=0, outcomes={}, intent_outcomes={}, acknowledgements={}, journal=())
        event = L5ExecutionDeliveryEvent.create(
            sequence_number=1,
            event_type="DELIVERY_INITIALIZED",
            delivery_version_before=0,
            delivery_hash_before=GENESIS_DELIVERY_HASH,
            payload=base.canonical_components(),
            previous_event_hash=GENESIS_DELIVERY_HASH,
        )
        return cls(delivery_version=0, outcomes={}, intent_outcomes={}, acknowledgements={}, journal=(event,))

    def publish(self, outcome: L5ExecutionOutcome) -> L5ExecutionDeliveryState:
        if not isinstance(outcome, L5ExecutionOutcome) or not outcome.is_intact():
            raise L5ExecutionDeliveryError("INVALID_OUTCOME", "outcome integrity failed")
        existing_id = self.intent_outcomes.get(outcome.intent_id)
        if existing_id is not None:
            existing = self.outcomes[existing_id]
            if existing == outcome:
                return self
            raise L5ExecutionDeliveryError("INTENT_OUTCOME_CONFLICT", "intent already has a different outcome")
        event = L5ExecutionDeliveryEvent.create(
            sequence_number=len(self.journal) + 1,
            event_type="OUTCOME_PUBLISHED",
            delivery_version_before=self.delivery_version,
            delivery_hash_before=self.delivery_hash,
            payload={"outcome": outcome.canonical()},
            previous_event_hash=self.journal[-1].event_hash,
        )
        return L5ExecutionDeliveryState(
            delivery_version=self.delivery_version + 1,
            outcomes={**self.outcomes, outcome.outcome_id: outcome},
            intent_outcomes={**self.intent_outcomes, outcome.intent_id: outcome.outcome_id},
            acknowledgements=self.acknowledgements,
            journal=(*self.journal, event),
        )

    def acknowledge(
        self,
        acknowledgement: L5ExecutionDeliveryAcknowledgement,
    ) -> L5ExecutionDeliveryState:
        if not isinstance(acknowledgement, L5ExecutionDeliveryAcknowledgement) or not acknowledgement.is_intact():
            raise L5ExecutionDeliveryError("INVALID_ACKNOWLEDGEMENT", "acknowledgement integrity failed")
        outcome = self.outcomes.get(acknowledgement.outcome_id)
        if outcome is None:
            raise L5ExecutionDeliveryError("ORPHAN_ACKNOWLEDGEMENT", "outcome does not exist")
        if outcome.outcome_hash != acknowledgement.outcome_hash:
            raise L5ExecutionDeliveryError("OUTCOME_IDENTITY_CONFLICT", "acknowledgement outcome differs")
        existing = self.acknowledgements.get(acknowledgement.acknowledgement_id)
        if existing is not None:
            if existing == acknowledgement:
                return self
            raise L5ExecutionDeliveryError("ACKNOWLEDGEMENT_CONFLICT", "acknowledgement identity conflicts")
        if any(
            item.consumer_id == acknowledgement.consumer_id
            and item.outcome_id == acknowledgement.outcome_id
            for item in self.acknowledgements.values()
        ):
            raise L5ExecutionDeliveryError(
                "ACKNOWLEDGEMENT_CONFLICT",
                "consumer outcome was already acknowledged",
            )
        event = L5ExecutionDeliveryEvent.create(
            sequence_number=len(self.journal) + 1,
            event_type="OUTCOME_ACKNOWLEDGED",
            delivery_version_before=self.delivery_version,
            delivery_hash_before=self.delivery_hash,
            payload={"acknowledgement": acknowledgement.canonical()},
            previous_event_hash=self.journal[-1].event_hash,
        )
        return L5ExecutionDeliveryState(
            delivery_version=self.delivery_version + 1,
            outcomes=self.outcomes,
            intent_outcomes=self.intent_outcomes,
            acknowledgements={**self.acknowledgements, acknowledgement.acknowledgement_id: acknowledgement},
            journal=(*self.journal, event),
        )

    def pending_for(self, consumer_id: str) -> tuple[L5ExecutionOutcome, ...]:
        consumer = _identifier(consumer_id, "consumer_id")
        acknowledged = {
            acknowledgement.outcome_id
            for acknowledgement in self.acknowledgements.values()
            if acknowledgement.consumer_id == consumer
        }
        published_ids = tuple(
            str(event.payload["outcome"]["outcome_id"])
            for event in self.journal
            if event.event_type == "OUTCOME_PUBLISHED"
        )
        return tuple(
            self.outcomes[outcome_id]
            for outcome_id in published_ids
            if outcome_id not in acknowledged
        )


@dataclass(frozen=True)
class L5ExecutionInboxEvent:
    schema_version: str
    sequence_number: int
    event_type: str
    inbox_version_before: int
    inbox_hash_before: str
    payload: Mapping[str, object]
    previous_event_hash: str
    event_hash: str

    @classmethod
    def create(cls, *, sequence_number: int, event_type: str, inbox_version_before: int, inbox_hash_before: str, payload: Mapping[str, object], previous_event_hash: str) -> L5ExecutionInboxEvent:
        fields = {
            "schema_version": INBOX_SCHEMA_VERSION,
            "sequence_number": sequence_number,
            "event_type": event_type,
            "inbox_version_before": inbox_version_before,
            "inbox_hash_before": inbox_hash_before,
            "payload": _thaw_json(_freeze_json(payload)),
            "previous_event_hash": previous_event_hash,
        }
        return cls(event_hash=_sha256(fields), **fields)

    def __post_init__(self) -> None:
        if self.schema_version != INBOX_SCHEMA_VERSION or self.event_type not in INBOX_EVENT_TYPES:
            raise L5ExecutionDeliveryError("INVALID_INBOX_EVENT", "inbox event contract is invalid")
        _integer(self.sequence_number, "sequence_number", minimum=1)
        _integer(self.inbox_version_before, "inbox_version_before")
        if not all(_is_hash(value) for value in (self.inbox_hash_before, self.previous_event_hash, self.event_hash)):
            raise L5ExecutionDeliveryError("INVALID_INBOX_EVENT", "inbox event hash is invalid")
        object.__setattr__(self, "payload", _freeze_json(self.payload))

    def fields_without_hash(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "sequence_number": self.sequence_number,
            "event_type": self.event_type,
            "inbox_version_before": self.inbox_version_before,
            "inbox_hash_before": self.inbox_hash_before,
            "payload": _thaw_json(self.payload),
            "previous_event_hash": self.previous_event_hash,
        }

    def canonical(self) -> dict[str, object]:
        return {**self.fields_without_hash(), "event_hash": self.event_hash}


@dataclass(frozen=True)
class L5ExecutionInboxState:
    inbox_version: int
    receipts: Mapping[str, L5ExecutionInboxReceipt]
    outcome_hashes: Mapping[str, str]
    acceptance_event_hashes: Mapping[str, str]
    effect_event_hashes: Mapping[str, Mapping[str, str]]
    journal: tuple[L5ExecutionInboxEvent, ...]

    def __post_init__(self) -> None:
        _integer(self.inbox_version, "inbox_version")
        if not isinstance(self.journal, tuple):
            raise L5ExecutionDeliveryError("INVALID_INBOX_STATE", "inbox journal must be a tuple")
        receipts = dict(self.receipts)
        hashes = dict(self.outcome_hashes)
        acceptance_hashes = dict(self.acceptance_event_hashes)
        effect_hashes = {
            receipt_id: MappingProxyType(dict(values))
            for receipt_id, values in self.effect_event_hashes.items()
        }
        if any(key != value.receipt_id or not value.is_intact() for key, value in receipts.items()):
            raise L5ExecutionDeliveryError("INVALID_INBOX_STATE", "receipt mapping is invalid")
        if any(not _is_hash(value) for value in hashes.values()):
            raise L5ExecutionDeliveryError("INVALID_INBOX_STATE", "outcome hash mapping is invalid")
        if any(
            receipt.outcome_id not in hashes
            or hashes[receipt.outcome_id] != receipt.outcome_hash
            for receipt in receipts.values()
        ) or len(receipts) != len(hashes):
            raise L5ExecutionDeliveryError("INVALID_INBOX_STATE", "receipt outcome mapping is invalid")
        if set(acceptance_hashes) != set(hashes) or any(not _is_hash(value) for value in acceptance_hashes.values()):
            raise L5ExecutionDeliveryError("INVALID_INBOX_STATE", "acceptance event mapping is invalid")
        if any(receipt_id not in receipts for receipt_id in effect_hashes):
            raise L5ExecutionDeliveryError("INVALID_INBOX_STATE", "effect receipt is invalid")
        for receipt_id, values in effect_hashes.items():
            if not set(values).issubset(receipts[receipt_id].required_effects) or any(
                not _is_hash(value) for value in values.values()
            ):
                raise L5ExecutionDeliveryError("INVALID_INBOX_STATE", "effect progress is invalid")
        object.__setattr__(self, "receipts", MappingProxyType(receipts))
        object.__setattr__(self, "outcome_hashes", MappingProxyType(hashes))
        object.__setattr__(self, "acceptance_event_hashes", MappingProxyType(acceptance_hashes))
        object.__setattr__(self, "effect_event_hashes", MappingProxyType(effect_hashes))

    def canonical_components(self) -> dict[str, object]:
        return {
            "inbox_version": self.inbox_version,
            "receipts": {key: value.canonical() for key, value in sorted(self.receipts.items())},
            "outcome_hashes": dict(sorted(self.outcome_hashes.items())),
            "acceptance_event_hashes": dict(sorted(self.acceptance_event_hashes.items())),
            "effect_event_hashes": {
                key: dict(sorted(value.items()))
                for key, value in sorted(self.effect_event_hashes.items())
            },
        }

    @property
    def inbox_hash(self) -> str:
        return _sha256({**self.canonical_components(), "journal": [event.canonical() for event in self.journal]})

    @classmethod
    def initial(cls) -> L5ExecutionInboxState:
        base = cls(
            inbox_version=0,
            receipts={},
            outcome_hashes={},
            acceptance_event_hashes={},
            effect_event_hashes={},
            journal=(),
        )
        event = L5ExecutionInboxEvent.create(
            sequence_number=1,
            event_type="INBOX_INITIALIZED",
            inbox_version_before=0,
            inbox_hash_before=GENESIS_INBOX_HASH,
            payload=base.canonical_components(),
            previous_event_hash=GENESIS_INBOX_HASH,
        )
        return cls(
            inbox_version=0,
            receipts={},
            outcome_hashes={},
            acceptance_event_hashes={},
            effect_event_hashes={},
            journal=(event,),
        )


@dataclass(frozen=True)
class L5ExecutionInboxAcceptance:
    receipt: L5ExecutionInboxReceipt
    accepted_new: bool


class L5ExecutionOutcomeInbox:
    """Single-consumer, in-memory idempotent receipt authority."""

    def __init__(self, consumer_id: str) -> None:
        self._consumer_id = _identifier(consumer_id, "consumer_id")
        self._state = L5ExecutionInboxState.initial()
        self._lock = threading.RLock()

    @property
    def consumer_id(self) -> str:
        return self._consumer_id

    @property
    def state(self) -> L5ExecutionInboxState:
        with self._lock:
            return self._state

    @property
    def receipts(self) -> tuple[L5ExecutionInboxReceipt, ...]:
        with self._lock:
            return tuple(value for _, value in sorted(self._state.receipts.items()))

    def accept(
        self,
        outcome: L5ExecutionOutcome,
        *,
        required_effects: tuple[str, ...] = (),
    ) -> L5ExecutionInboxAcceptance:
        if not isinstance(outcome, L5ExecutionOutcome) or not outcome.is_intact():
            raise L5ExecutionDeliveryError("INVALID_OUTCOME", "outcome integrity failed")
        with self._lock:
            existing_hash = self._state.outcome_hashes.get(outcome.outcome_id)
            if existing_hash is not None:
                if existing_hash != outcome.outcome_hash:
                    raise L5ExecutionDeliveryError("OUTCOME_IDENTITY_CONFLICT", "outcome payload differs")
                receipt = next(
                    receipt
                    for receipt in self._state.receipts.values()
                    if receipt.outcome_id == outcome.outcome_id
                )
                if receipt.required_effects != tuple(sorted(set(required_effects))):
                    raise L5ExecutionDeliveryError(
                        "CONSUMER_CONFIGURATION_CONFLICT",
                        "required effects differ for an accepted outcome",
                    )
                return L5ExecutionInboxAcceptance(receipt=receipt, accepted_new=False)
            receipt = L5ExecutionInboxReceipt.create(
                self._consumer_id,
                outcome,
                required_effects,
            )
            event = L5ExecutionInboxEvent.create(
                sequence_number=len(self._state.journal) + 1,
                event_type="OUTCOME_ACCEPTED",
                inbox_version_before=self._state.inbox_version,
                inbox_hash_before=self._state.inbox_hash,
                payload={"outcome": outcome.canonical(), "receipt": receipt.canonical()},
                previous_event_hash=self._state.journal[-1].event_hash,
            )
            next_state = L5ExecutionInboxState(
                inbox_version=self._state.inbox_version + 1,
                receipts={**self._state.receipts, receipt.receipt_id: receipt},
                outcome_hashes={**self._state.outcome_hashes, outcome.outcome_id: outcome.outcome_hash},
                acceptance_event_hashes={
                    **self._state.acceptance_event_hashes,
                    outcome.outcome_id: event.event_hash,
                },
                effect_event_hashes=self._state.effect_event_hashes,
                journal=(*self._state.journal, event),
            )
            self._publish_state(next_state)
            return L5ExecutionInboxAcceptance(receipt=receipt, accepted_new=True)

    def verify_receipt(self, receipt: L5ExecutionInboxReceipt) -> None:
        if not isinstance(receipt, L5ExecutionInboxReceipt) or not receipt.is_intact():
            raise L5ExecutionDeliveryError("INVALID_RECEIPT", "receipt integrity failed")
        with self._lock:
            if receipt.consumer_id != self._consumer_id or self._state.receipts.get(receipt.receipt_id) != receipt:
                raise L5ExecutionDeliveryError("UNISSUED_RECEIPT", "receipt was not issued by this inbox")

    def apply_effect(
        self,
        receipt: L5ExecutionInboxReceipt,
        effect_name: str,
        effect: Callable[[], None],
    ) -> bool:
        """Run one required sink once and journal successful completion.

        The inbox lock is held across the local sink call.  This gives
        deterministic in-process idempotence; it is not a distributed sink
        transaction and is intentionally not persisted across restarts.
        """
        name = _identifier(effect_name, "effect_name")
        if not callable(effect):
            raise L5ExecutionDeliveryError("INVALID_EFFECT", "effect must be callable")
        with self._lock:
            self.verify_receipt(receipt)
            if name not in receipt.required_effects:
                raise L5ExecutionDeliveryError("UNEXPECTED_EFFECT", "effect is not required by receipt")
            completed = self._state.effect_event_hashes.get(receipt.receipt_id, {})
            if name in completed:
                return False
            effect()
            effect_id = f"l5-effect-{_sha256({'receipt_hash': receipt.receipt_hash, 'effect_name': name})}"
            event = L5ExecutionInboxEvent.create(
                sequence_number=len(self._state.journal) + 1,
                event_type="EFFECT_COMPLETED",
                inbox_version_before=self._state.inbox_version,
                inbox_hash_before=self._state.inbox_hash,
                payload={
                    "effect_id": effect_id,
                    "effect_name": name,
                    "receipt": receipt.canonical(),
                },
                previous_event_hash=self._state.journal[-1].event_hash,
            )
            next_effects = {
                key: dict(value) for key, value in self._state.effect_event_hashes.items()
            }
            next_effects[receipt.receipt_id] = {**completed, name: event.event_hash}
            self._publish_state(L5ExecutionInboxState(
                inbox_version=self._state.inbox_version + 1,
                receipts=self._state.receipts,
                outcome_hashes=self._state.outcome_hashes,
                acceptance_event_hashes=self._state.acceptance_event_hashes,
                effect_event_hashes=next_effects,
                journal=(*self._state.journal, event),
            ))
            return True

    def acknowledgement_for(
        self,
        receipt: L5ExecutionInboxReceipt,
        *,
        emission_accepted_hash: str | None = None,
    ) -> L5ExecutionDeliveryAcknowledgement:
        """Build an ack only after every required effect is journalled."""
        with self._lock:
            self.verify_receipt(receipt)
            effects = self._state.effect_event_hashes.get(receipt.receipt_id, {})
            if set(effects) != set(receipt.required_effects):
                raise L5ExecutionDeliveryError("INCOMPLETE_EFFECTS", "required effects are incomplete")
            return L5ExecutionDeliveryAcknowledgement.create(
                receipt,
                acceptance_event_hash=self._state.acceptance_event_hashes[receipt.outcome_id],
                effect_event_hashes=effects,
                inbox_anchor_hash=self._state.journal[-1].event_hash,
                emission_accepted_hash=emission_accepted_hash,
            )

    def _publish_state(self, next_state: L5ExecutionInboxState) -> None:
        self._state = next_state


def replay_delivery_journal(
    events: tuple[L5ExecutionDeliveryEvent, ...],
    *,
    expected_final_hash: str,
    validate_outcome: Callable[[L5ExecutionOutcome], None],
    inbox_states: Mapping[str, L5ExecutionInboxState] = MappingProxyType({}),
    validate_emission: Callable[[L5ExecutionDeliveryAcknowledgement, L5ExecutionOutcome, int], None] | None = None,
) -> tuple[L5ExecutionDeliveryState, str]:
    """Replay an anchored delivery journal with caller-provided transaction semantics."""
    if not isinstance(events, tuple) or not events or not _is_hash(expected_final_hash):
        raise L5ExecutionDeliveryError("INVALID_DELIVERY_JOURNAL", "journal or final anchor is invalid")
    previous_event_hash = GENESIS_DELIVERY_HASH
    current = L5ExecutionDeliveryState.initial()
    if events[0] != current.journal[0]:
        raise L5ExecutionDeliveryError("INVALID_DELIVERY_JOURNAL", "initial event is invalid")
    for sequence, event in enumerate(events, start=1):
        if not isinstance(event, L5ExecutionDeliveryEvent):
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_JOURNAL", "event is invalid")
        if event.sequence_number != sequence or event.previous_event_hash != previous_event_hash:
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_JOURNAL", "sequence or hash chain differs")
        if event.event_hash != _sha256(event.fields_without_hash()):
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_JOURNAL", "event hash differs")
        previous_event_hash = event.event_hash
        if sequence == 1:
            continue
        if event.delivery_version_before != current.delivery_version or event.delivery_hash_before != current.delivery_hash:
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_JOURNAL", "delivery before-state differs")
        payload = _thaw_json(event.payload)
        if event.event_type == "OUTCOME_PUBLISHED":
            outcome = L5ExecutionOutcome.from_canonical(payload.get("outcome"))
            if not outcome.is_intact():
                raise L5ExecutionDeliveryError("INVALID_DELIVERY_JOURNAL", "outcome is not intact")
            validate_outcome(outcome)
            current = current.publish(outcome)
        elif event.event_type == "OUTCOME_ACKNOWLEDGED":
            acknowledgement_data = payload.get("acknowledgement")
            if not isinstance(acknowledgement_data, dict):
                raise L5ExecutionDeliveryError("INVALID_DELIVERY_JOURNAL", "acknowledgement is missing")
            try:
                acknowledgement = L5ExecutionDeliveryAcknowledgement(
                    **acknowledgement_data
                )
            except (TypeError, ValueError, L5ExecutionDeliveryError) as exc:
                raise L5ExecutionDeliveryError("INVALID_DELIVERY_JOURNAL", "acknowledgement is malformed") from exc
            inbox = inbox_states.get(acknowledgement.consumer_id)
            receipt = (
                inbox.receipts.get(acknowledgement.receipt_id)
                if inbox is not None
                else None
            )
            event_indexes = (
                {item.event_hash: index for index, item in enumerate(inbox.journal)}
                if inbox is not None
                else {}
            )
            anchor_index = event_indexes.get(acknowledgement.inbox_anchor_hash)
            causal_hashes = (
                acknowledgement.acceptance_event_hash,
                *acknowledgement.effect_event_hashes.values(),
            )
            if (
                inbox is None
                or receipt is None
                or receipt.receipt_hash != acknowledgement.receipt_hash
                or receipt.consumer_id != acknowledgement.consumer_id
                or receipt.outcome_id != acknowledgement.outcome_id
                or receipt.outcome_hash != acknowledgement.outcome_hash
                or inbox.acceptance_event_hashes.get(receipt.outcome_id)
                != acknowledgement.acceptance_event_hash
                or dict(inbox.effect_event_hashes.get(receipt.receipt_id, {}))
                != dict(acknowledgement.effect_event_hashes)
                or set(acknowledgement.effect_event_hashes) != set(receipt.required_effects)
                or anchor_index is None
                or any(event_indexes.get(item, anchor_index + 1) > anchor_index for item in causal_hashes)
            ):
                raise L5ExecutionDeliveryError(
                    "ORPHAN_ACKNOWLEDGEMENT",
                    "acknowledgement lacks exact prior inbox acceptance/effect causality",
                )
            if acknowledgement.emission_accepted_hash is not None or validate_emission is not None:
                if validate_emission is None:
                    raise L5ExecutionDeliveryError(
                        "UNVERIFIED_BUS_ACCEPTANCE", "durable bus proof is required"
                    )
                publication = next(
                    item for item in current.journal
                    if item.event_type == "OUTCOME_PUBLISHED"
                    and item.payload["outcome"]["outcome_id"] == acknowledgement.outcome_id
                )
                validate_emission(
                    acknowledgement,
                    current.outcomes[acknowledgement.outcome_id],
                    publication.sequence_number,
                )
            current = current.acknowledge(acknowledgement)
        else:
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_JOURNAL", "event type is invalid")
        if current.journal[-1] != event:
            raise L5ExecutionDeliveryError("INVALID_DELIVERY_JOURNAL", "event is semantically inconsistent")
    if previous_event_hash != expected_final_hash:
        raise L5ExecutionDeliveryError("INVALID_DELIVERY_JOURNAL", "journal final hash differs")
    return current, previous_event_hash


def replay_inbox_journal(
    events: tuple[L5ExecutionInboxEvent, ...],
    *,
    expected_final_hash: str,
) -> tuple[L5ExecutionInboxState, str]:
    if not isinstance(events, tuple) or not events or not _is_hash(expected_final_hash):
        raise L5ExecutionDeliveryError("INVALID_INBOX_JOURNAL", "journal or final anchor is invalid")
    current = L5ExecutionInboxState.initial()
    if events[0] != current.journal[0]:
        raise L5ExecutionDeliveryError("INVALID_INBOX_JOURNAL", "initial event is invalid")
    previous_event_hash = GENESIS_INBOX_HASH
    for sequence, event in enumerate(events, start=1):
        if not isinstance(event, L5ExecutionInboxEvent):
            raise L5ExecutionDeliveryError("INVALID_INBOX_JOURNAL", "event is invalid")
        if event.sequence_number != sequence or event.previous_event_hash != previous_event_hash:
            raise L5ExecutionDeliveryError("INVALID_INBOX_JOURNAL", "sequence or hash chain differs")
        if event.event_hash != _sha256(event.fields_without_hash()):
            raise L5ExecutionDeliveryError("INVALID_INBOX_JOURNAL", "event hash differs")
        previous_event_hash = event.event_hash
        if sequence == 1:
            continue
        if event.inbox_version_before != current.inbox_version or event.inbox_hash_before != current.inbox_hash:
            raise L5ExecutionDeliveryError("INVALID_INBOX_JOURNAL", "inbox event semantics differ")
        payload = _thaw_json(event.payload)
        if event.event_type == "OUTCOME_ACCEPTED":
            outcome = L5ExecutionOutcome.from_canonical(payload.get("outcome"))
            receipt_data = payload.get("receipt")
            if not outcome.is_intact() or not isinstance(receipt_data, dict):
                raise L5ExecutionDeliveryError("INVALID_INBOX_JOURNAL", "receipt payload is invalid")
            receipt = L5ExecutionInboxReceipt(
                **{**receipt_data, "required_effects": tuple(receipt_data["required_effects"])}
            )
            expected = L5ExecutionInboxReceipt.create(
                receipt.consumer_id,
                outcome,
                receipt.required_effects,
            )
            if receipt != expected or outcome.outcome_id in current.outcome_hashes:
                raise L5ExecutionDeliveryError("INVALID_INBOX_JOURNAL", "receipt semantics differ")
            current = L5ExecutionInboxState(
                inbox_version=current.inbox_version + 1,
                receipts={**current.receipts, receipt.receipt_id: receipt},
                outcome_hashes={**current.outcome_hashes, outcome.outcome_id: outcome.outcome_hash},
                acceptance_event_hashes={
                    **current.acceptance_event_hashes,
                    outcome.outcome_id: event.event_hash,
                },
                effect_event_hashes=current.effect_event_hashes,
                journal=(*current.journal, event),
            )
        elif event.event_type == "EFFECT_COMPLETED":
            receipt_data = payload.get("receipt")
            effect_name = payload.get("effect_name")
            if not isinstance(receipt_data, dict) or not isinstance(effect_name, str):
                raise L5ExecutionDeliveryError("INVALID_INBOX_JOURNAL", "effect payload is invalid")
            receipt = L5ExecutionInboxReceipt(
                **{**receipt_data, "required_effects": tuple(receipt_data["required_effects"])}
            )
            if current.receipts.get(receipt.receipt_id) != receipt or effect_name not in receipt.required_effects:
                raise L5ExecutionDeliveryError("INVALID_INBOX_JOURNAL", "effect receipt differs")
            completed = current.effect_event_hashes.get(receipt.receipt_id, {})
            expected_effect_id = f"l5-effect-{_sha256({'receipt_hash': receipt.receipt_hash, 'effect_name': effect_name})}"
            if effect_name in completed or payload.get("effect_id") != expected_effect_id:
                raise L5ExecutionDeliveryError("INVALID_INBOX_JOURNAL", "effect completion is duplicated or invalid")
            next_effects = {key: dict(value) for key, value in current.effect_event_hashes.items()}
            next_effects[receipt.receipt_id] = {**completed, effect_name: event.event_hash}
            current = L5ExecutionInboxState(
                inbox_version=current.inbox_version + 1,
                receipts=current.receipts,
                outcome_hashes=current.outcome_hashes,
                acceptance_event_hashes=current.acceptance_event_hashes,
                effect_event_hashes=next_effects,
                journal=(*current.journal, event),
            )
        else:
            raise L5ExecutionDeliveryError("INVALID_INBOX_JOURNAL", "inbox event type is invalid")
    if previous_event_hash != expected_final_hash:
        raise L5ExecutionDeliveryError("INVALID_INBOX_JOURNAL", "journal final hash differs")
    return current, previous_event_hash


__all__ = [
    "DELIVERY_SCHEMA_VERSION",
    "GENESIS_DELIVERY_HASH",
    "GENESIS_INBOX_HASH",
    "INBOX_SCHEMA_VERSION",
    "OUTCOME_SCHEMA_VERSION",
    "L5ExecutionDeliveryAcknowledgement",
    "L5ExecutionDeliveryError",
    "L5ExecutionDeliveryEvent",
    "L5ExecutionDeliveryState",
    "L5ExecutionInboxAcceptance",
    "L5ExecutionInboxEvent",
    "L5ExecutionInboxReceipt",
    "L5ExecutionInboxState",
    "L5ExecutionOutcome",
    "L5ExecutionOutcomeInbox",
    "L5ExecutionOutcomeSpec",
    "replay_delivery_journal",
    "replay_inbox_journal",
]
