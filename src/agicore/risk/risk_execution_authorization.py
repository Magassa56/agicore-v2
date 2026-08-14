"""Deterministic, offline authorization decisions for future execution gates.

This contract intentionally does not submit an order or mutate a risk context.
``RiskManager`` remains the sole evaluator of business risk rules.
"""
from __future__ import annotations

import hashlib
import json
import math
import threading
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Mapping

from .exposure_models import ExecutionIntent, IntentSide, RiskLimits, RiskViolation
from .risk_execution_context import RiskContextError, RiskContextProvider, RiskExecutionContext
from .risk_manager import RiskManager


AUTHORIZATION_SCHEMA_VERSION = "risk-execution-authorization/1.0"
CONSUMPTION_SCHEMA_VERSION = "risk-execution-consumption/1.0"


class RiskAuthorizationError(ValueError):
    """Controlled failure of authorization verification."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


def _canonical_json(value: object) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise RiskAuthorizationError("INVALID_AUTHORIZATION_INPUT", "value is not canonically serializable") from exc


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _is_sha256_hex(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _finite_number(value: object, field_name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise RiskAuthorizationError("INVALID_AUTHORIZATION_INPUT", f"{field_name} must be a finite number or None")
    return float(value)


def _intent_canonical(intent: ExecutionIntent) -> dict[str, object]:
    if not isinstance(intent, ExecutionIntent):
        raise RiskAuthorizationError("INVALID_INTENT", "intent must be an ExecutionIntent")
    if not isinstance(intent.intent_id, str) or not intent.intent_id.strip():
        raise RiskAuthorizationError("INVALID_INTENT", "intent_id must be a non-blank string")
    if not isinstance(intent.symbol, str) or not intent.symbol.strip():
        raise RiskAuthorizationError("INVALID_INTENT", "symbol must be a non-blank string")
    if not isinstance(intent.side, IntentSide):
        raise RiskAuthorizationError("INVALID_INTENT", "side must be an IntentSide")
    if not isinstance(intent.timestamp, datetime):
        raise RiskAuthorizationError("INVALID_INTENT", "intent timestamp must be explicit")
    quantity = _finite_number(intent.quantity, "intent quantity")
    estimated_price = _finite_number(intent.estimated_price, "intent estimated_price")
    if quantity is None or quantity <= 0 or estimated_price is None or estimated_price <= 0:
        raise RiskAuthorizationError("INVALID_INTENT", "quantity and estimated_price must be strictly positive")
    return {
        "intent_id": intent.intent_id,
        "symbol": intent.symbol,
        "side": intent.side.value,
        "quantity": quantity,
        "estimated_price": estimated_price,
        "timestamp": intent.timestamp.isoformat(),
    }


def _limits_canonical(limits: RiskLimits) -> dict[str, object]:
    if not isinstance(limits, RiskLimits):
        raise RiskAuthorizationError("INVALID_AUTHORIZATION_INPUT", "limits must be RiskLimits")
    raw = limits.model_dump(mode="json")
    _canonical_json(raw)
    return raw


@dataclass(frozen=True)
class RiskAuthorizationViolation:
    """Immutable, timestamp-free projection of a RiskManager violation."""

    code: str
    level: str
    message: str
    limit_value: float | None
    actual_value: float | None

    @classmethod
    def from_risk_violation(cls, violation: RiskViolation) -> "RiskAuthorizationViolation":
        return cls(
            code=violation.code.value,
            level=violation.level.value,
            message=violation.message,
            limit_value=_finite_number(violation.limit_value, "violation limit_value"),
            actual_value=_finite_number(violation.actual_value, "violation actual_value"),
        )

    def canonical(self) -> dict[str, object]:
        return {
            "code": self.code,
            "level": self.level,
            "message": self.message,
            "limit_value": self.limit_value,
            "actual_value": self.actual_value,
        }


@dataclass(frozen=True)
class RiskAuthorizationDecision:
    """Immutable authorization evidence, not a reusable execution token."""

    schema_version: str
    authorization_id: str
    allowed: bool
    provider_id: str
    intent_id: str
    intent_hash: str
    context_state_version: int
    context_state_hash: str
    risk_limits_hash: str
    violations: tuple[RiskAuthorizationViolation, ...]
    guard_codes: tuple[str, ...]
    decision_hash: str

    @classmethod
    def create(
        cls,
        *,
        allowed: bool,
        provider_id: str,
        intent_id: str,
        intent_hash: str,
        context: RiskExecutionContext,
        risk_limits_hash: str,
        violations: tuple[RiskAuthorizationViolation, ...] = (),
        guard_codes: tuple[str, ...] = (),
    ) -> "RiskAuthorizationDecision":
        if not isinstance(allowed, bool):
            raise RiskAuthorizationError("INVALID_AUTHORIZATION", "allowed must be a boolean")
        if not isinstance(provider_id, str) or not provider_id.strip():
            raise RiskAuthorizationError("INVALID_AUTHORIZATION", "provider_id must be non-blank")
        if not isinstance(intent_id, str) or not intent_id.strip():
            raise RiskAuthorizationError("INVALID_AUTHORIZATION", "intent_id must be non-blank")
        if not _is_sha256_hex(intent_hash) or not _is_sha256_hex(risk_limits_hash):
            raise RiskAuthorizationError("INVALID_AUTHORIZATION", "authorization hashes must be SHA-256 digests")
        if not isinstance(violations, tuple) or not all(isinstance(item, RiskAuthorizationViolation) for item in violations):
            raise RiskAuthorizationError("INVALID_AUTHORIZATION", "violations must be a canonical tuple")
        if not isinstance(guard_codes, tuple) or not all(isinstance(code, str) and code.strip() for code in guard_codes):
            raise RiskAuthorizationError("INVALID_AUTHORIZATION", "guard_codes must be a canonical tuple")
        has_block_violation = any(item.level == "BLOCK" for item in violations)
        if allowed and (guard_codes or has_block_violation):
            raise RiskAuthorizationError("INVALID_AUTHORIZATION", "allowed decision cannot contain a blocking cause")
        if not allowed and not guard_codes and not violations:
            raise RiskAuthorizationError("INVALID_AUTHORIZATION", "blocked decision requires a structured cause")
        fields = {
            "schema_version": AUTHORIZATION_SCHEMA_VERSION,
            "allowed": allowed,
            "provider_id": provider_id,
            "intent_id": intent_id,
            "intent_hash": intent_hash,
            "context_state_version": context.state_version,
            "context_state_hash": context.state_hash,
            "risk_limits_hash": risk_limits_hash,
            "violations": [violation.canonical() for violation in violations],
            "guard_codes": list(guard_codes),
        }
        decision_hash = _sha256(fields)
        stored_fields = dict(fields)
        stored_fields["violations"] = tuple(violations)
        stored_fields["guard_codes"] = tuple(guard_codes)
        return cls(
            authorization_id=f"risk-auth-{decision_hash}",
            decision_hash=decision_hash,
            **stored_fields,
        )

    def fields_without_identity(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "allowed": self.allowed,
            "provider_id": self.provider_id,
            "intent_id": self.intent_id,
            "intent_hash": self.intent_hash,
            "context_state_version": self.context_state_version,
            "context_state_hash": self.context_state_hash,
            "risk_limits_hash": self.risk_limits_hash,
            "violations": [violation.canonical() for violation in self.violations],
            "guard_codes": list(self.guard_codes),
        }

    def canonical(self) -> Mapping[str, object]:
        return MappingProxyType({
            **self.fields_without_identity(),
            "authorization_id": self.authorization_id,
            "decision_hash": self.decision_hash,
        })

    def is_intact(self) -> bool:
        try:
            if self.schema_version != AUTHORIZATION_SCHEMA_VERSION:
                return False
            if not isinstance(self.allowed, bool):
                return False
            if not isinstance(self.provider_id, str) or not self.provider_id.strip():
                return False
            if not isinstance(self.intent_id, str) or not self.intent_id.strip():
                return False
            if not _is_sha256_hex(self.intent_hash) or not _is_sha256_hex(self.context_state_hash):
                return False
            if not _is_sha256_hex(self.risk_limits_hash) or not _is_sha256_hex(self.decision_hash):
                return False
            if isinstance(self.context_state_version, bool) or not isinstance(self.context_state_version, int):
                return False
            if self.context_state_version < 0:
                return False
            if not isinstance(self.violations, tuple):
                return False
            if not all(isinstance(item, RiskAuthorizationViolation) for item in self.violations):
                return False
            if not isinstance(self.guard_codes, tuple):
                return False
            if not all(isinstance(code, str) and code.strip() for code in self.guard_codes):
                return False
            has_block_violation = any(item.level == "BLOCK" for item in self.violations)
            if self.allowed and (self.guard_codes or has_block_violation):
                return False
            if not self.allowed and not self.guard_codes and not self.violations:
                return False
            return (
                self.decision_hash == _sha256(self.fields_without_identity())
                and self.authorization_id == f"risk-auth-{self.decision_hash}"
            )
        except Exception:
            return False


@dataclass(frozen=True)
class RiskAuthorizationConsumption:
    """Deterministic evidence that an issued authorization was consumed once."""

    schema_version: str
    consumption_id: str
    authorization_id: str
    decision_hash: str
    provider_id: str
    intent_id: str
    intent_hash: str
    context_state_version: int
    context_state_hash: str
    risk_limits_hash: str
    consumption_hash: str

    @classmethod
    def _from_decision(cls, decision: RiskAuthorizationDecision) -> "RiskAuthorizationConsumption":
        if not isinstance(decision, RiskAuthorizationDecision) or not decision.is_intact():
            raise RiskAuthorizationError("INVALID_AUTHORIZATION", "cannot consume an invalid decision")
        if not decision.allowed:
            raise RiskAuthorizationError("RISK_AUTHORIZATION_BLOCKED", "cannot consume a blocked decision")
        fields = {
            "schema_version": CONSUMPTION_SCHEMA_VERSION,
            "authorization_id": decision.authorization_id,
            "decision_hash": decision.decision_hash,
            "provider_id": decision.provider_id,
            "intent_id": decision.intent_id,
            "intent_hash": decision.intent_hash,
            "context_state_version": decision.context_state_version,
            "context_state_hash": decision.context_state_hash,
            "risk_limits_hash": decision.risk_limits_hash,
        }
        consumption_hash = _sha256(fields)
        return cls(
            consumption_id=f"risk-consumption-{consumption_hash}",
            consumption_hash=consumption_hash,
            **fields,
        )

    def fields_without_identity(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "authorization_id": self.authorization_id,
            "decision_hash": self.decision_hash,
            "provider_id": self.provider_id,
            "intent_id": self.intent_id,
            "intent_hash": self.intent_hash,
            "context_state_version": self.context_state_version,
            "context_state_hash": self.context_state_hash,
            "risk_limits_hash": self.risk_limits_hash,
        }

    def canonical(self) -> Mapping[str, object]:
        return MappingProxyType({
            **self.fields_without_identity(),
            "consumption_id": self.consumption_id,
            "consumption_hash": self.consumption_hash,
        })

    def is_intact(self) -> bool:
        try:
            if self.schema_version != CONSUMPTION_SCHEMA_VERSION:
                return False
            identifiers = (
                self.authorization_id,
                self.provider_id,
                self.intent_id,
                self.consumption_id,
            )
            if not all(isinstance(value, str) and value.strip() for value in identifiers):
                return False
            hashes = (
                self.decision_hash,
                self.intent_hash,
                self.context_state_hash,
                self.risk_limits_hash,
                self.consumption_hash,
            )
            if not all(_is_sha256_hex(value) for value in hashes):
                return False
            if isinstance(self.context_state_version, bool) or not isinstance(self.context_state_version, int):
                return False
            if self.context_state_version < 0:
                return False
            if self.authorization_id != f"risk-auth-{self.decision_hash}":
                return False
            return (
                self.consumption_hash == _sha256(self.fields_without_identity())
                and self.consumption_id == f"risk-consumption-{self.consumption_hash}"
            )
        except Exception:
            return False


class RiskAuthorizationBoundary:
    """Read-only boundary between an intent, exact context, and RiskManager."""

    def __init__(self, risk_manager: RiskManager, context_provider: RiskContextProvider) -> None:
        self._risk_manager = risk_manager
        self._context_provider = context_provider
        self._registry_lock = threading.RLock()
        self._issued_decisions: dict[str, RiskAuthorizationDecision] = {}
        self._consumption_state: Mapping[str, RiskAuthorizationConsumption] = MappingProxyType({})

    @property
    def consumptions(self) -> tuple[RiskAuthorizationConsumption, ...]:
        """Return a canonical, immutable audit view of successful consumptions."""
        with self._registry_lock:
            return tuple(
                sorted(
                    self._consumption_state.values(),
                    key=lambda item: (item.intent_id, item.decision_hash),
                )
            )

    def authorize(
        self,
        intent: object,
        *,
        expected_provider_id: str,
        expected_context_state_version: int,
        expected_context_state_hash: str,
    ) -> RiskAuthorizationDecision:
        try:
            context = self._context_provider.snapshot()
        except Exception as exc:
            raise RiskAuthorizationError("CONTEXT_PROVIDER_ERROR", "context provider snapshot failed") from exc
        if not isinstance(context, RiskExecutionContext):
            raise RiskAuthorizationError("CONTEXT_PROVIDER_ERROR", "context provider returned an invalid snapshot")
        intent_id, intent_hash, intent_is_valid = _safe_intent_identity(intent)
        limits_hash = _safe_limits_hash(context)
        guard_codes = self._preflight_codes(
            context,
            expected_provider_id=expected_provider_id,
            expected_version=expected_context_state_version,
            expected_hash=expected_context_state_hash,
        )
        if not intent_is_valid:
            guard_codes.append("INVALID_INTENT")
        if guard_codes:
            return self._issue(RiskAuthorizationDecision.create(
                allowed=False,
                provider_id=context.provider_id,
                intent_id=intent_id,
                intent_hash=intent_hash,
                context=context,
                risk_limits_hash=limits_hash,
                guard_codes=tuple(guard_codes),
            ))

        try:
            result = self._risk_manager.validate(intent, context.exposure_snapshot)  # type: ignore[arg-type]
            violations = tuple(RiskAuthorizationViolation.from_risk_violation(item) for item in result.violations)
            blocked = not result.passed or any(item.level == "BLOCK" for item in violations)
            return self._issue(RiskAuthorizationDecision.create(
                allowed=not blocked,
                provider_id=context.provider_id,
                intent_id=intent_id,
                intent_hash=intent_hash,
                context=context,
                risk_limits_hash=limits_hash,
                violations=violations,
                guard_codes=("RISK_MANAGER_BLOCKED",) if blocked else (),
            ))
        except Exception:
            return self._issue(RiskAuthorizationDecision.create(
                allowed=False,
                provider_id=context.provider_id,
                intent_id=intent_id,
                intent_hash=intent_hash,
                context=context,
                risk_limits_hash=limits_hash,
                guard_codes=("RISK_MANAGER_EXCEPTION",),
            ))

    def verify_for_execution(
        self,
        decision: object,
        intent: object,
    ) -> RiskAuthorizationConsumption:
        if not isinstance(decision, RiskAuthorizationDecision) or not decision.is_intact():
            raise RiskAuthorizationError("INVALID_AUTHORIZATION", "authorization decision integrity check failed")
        with self._registry_lock:
            issued = self._issued_decisions.get(decision.decision_hash)
            if issued is None or issued != decision:
                raise RiskAuthorizationError("UNISSUED_AUTHORIZATION", "decision was not issued by this boundary")
            if not decision.allowed:
                raise RiskAuthorizationError("RISK_AUTHORIZATION_BLOCKED", "authorization decision is blocked")
            intent_canonical = _intent_canonical(intent)  # type: ignore[arg-type]
            if decision.intent_id != intent_canonical["intent_id"] or decision.intent_hash != _sha256(intent_canonical):
                raise RiskAuthorizationError("AUTHORIZATION_INTENT_MISMATCH", "authorization decision does not match intent")
            if decision.decision_hash in self._consumption_state:
                raise RiskAuthorizationError(
                    "AUTHORIZATION_ALREADY_CONSUMED",
                    "authorization decision was already consumed",
                )
            if any(record.intent_id == decision.intent_id for record in self._consumption_state.values()):
                raise RiskAuthorizationError("INTENT_ALREADY_CONSUMED", "intent_id was already consumed")
            try:
                context = self._context_provider.snapshot()
            except Exception as exc:
                raise RiskAuthorizationError("CONTEXT_PROVIDER_ERROR", "context provider snapshot failed") from exc
            if not isinstance(context, RiskExecutionContext):
                raise RiskAuthorizationError("CONTEXT_PROVIDER_ERROR", "context provider returned an invalid snapshot")
            if decision.provider_id != context.provider_id:
                raise RiskAuthorizationError(
                    "AUTHORIZATION_PROVIDER_MISMATCH",
                    "authorization provider does not match current provider",
                )
            if (
                decision.context_state_version != context.state_version
                or decision.context_state_hash != context.state_hash
            ):
                raise RiskAuthorizationError("STALE_RISK_CONTEXT", "authorization context is no longer current")
            if decision.risk_limits_hash != _sha256(_limits_canonical(context.risk_limits)):
                raise RiskAuthorizationError(
                    "AUTHORIZATION_LIMITS_MISMATCH",
                    "authorization limits are no longer current",
                )
            try:
                manager_limits = _limits_canonical(self._risk_manager.limits)
            except Exception as exc:
                raise RiskAuthorizationError("RISK_LIMITS_MISMATCH", "risk manager limits are invalid") from exc
            if manager_limits != _limits_canonical(context.risk_limits):
                raise RiskAuthorizationError(
                    "RISK_LIMITS_MISMATCH",
                    "risk manager limits differ from current context",
                )
            try:
                self._context_provider.assert_current(context.state_version, context.state_hash)
            except RiskContextError as exc:
                raise RiskAuthorizationError(
                    "STALE_RISK_CONTEXT",
                    "authorization context changed during verification",
                ) from exc
            except Exception as exc:
                raise RiskAuthorizationError("CONTEXT_PROVIDER_ERROR", "context provider confirmation failed") from exc
            consumption = RiskAuthorizationConsumption._from_decision(decision)
            next_state = dict(self._consumption_state)
            next_state[decision.decision_hash] = consumption
            immutable_next_state = MappingProxyType(next_state)
            try:
                self._publish_consumption_state(immutable_next_state)
            except Exception as exc:
                raise RiskAuthorizationError(
                    "CONSUMPTION_PUBLICATION_ERROR",
                    "authorization consumption could not be published atomically",
                ) from exc
            return consumption

    def verify_consumption_evidence(
        self,
        record: object,
    ) -> RiskAuthorizationConsumption:
        """Verify structural integrity and local issuance of consumption evidence."""
        if not isinstance(record, RiskAuthorizationConsumption) or not record.is_intact():
            raise RiskAuthorizationError("INVALID_CONSUMPTION", "consumption evidence integrity check failed")
        with self._registry_lock:
            issued = self._consumption_state.get(record.decision_hash)
            if issued is None or issued != record:
                raise RiskAuthorizationError(
                    "UNISSUED_CONSUMPTION",
                    "consumption evidence was not issued by this boundary",
                )
            return issued

    def _publish_consumption_state(
        self,
        next_state: Mapping[str, RiskAuthorizationConsumption],
    ) -> None:
        """Publish a fully constructed immutable state with one assignment."""
        self._consumption_state = next_state

    def _preflight_codes(
        self,
        context: RiskExecutionContext,
        *,
        expected_provider_id: str,
        expected_version: int,
        expected_hash: str,
    ) -> list[str]:
        codes: list[str] = []
        expected_matches_snapshot = True
        if not isinstance(expected_provider_id, str) or expected_provider_id != context.provider_id:
            codes.append("PROVIDER_MISMATCH")
            expected_matches_snapshot = False
        if (
            isinstance(expected_version, bool)
            or not isinstance(expected_version, int)
            or expected_version != context.state_version
            or expected_hash != context.state_hash
        ):
            codes.append("STALE_RISK_CONTEXT")
            expected_matches_snapshot = False
        if expected_matches_snapshot:
            try:
                self._context_provider.assert_current(context.state_version, context.state_hash)
            except RiskContextError:
                codes.append("STALE_RISK_CONTEXT")
            except Exception:
                codes.append("CONTEXT_PROVIDER_ERROR")
        try:
            if _limits_canonical(self._risk_manager.limits) != _limits_canonical(context.risk_limits):
                codes.append("RISK_LIMITS_MISMATCH")
        except Exception:
            codes.append("RISK_LIMITS_MISMATCH")
        if not context.execution_enabled:
            codes.append("EXECUTION_DISABLED")
        if context.kill_switch_active:
            codes.append("KILL_SWITCH_ACTIVE")
        if context.legacy_hard_deny:
            codes.append("LEGACY_HARD_DENY")
        return codes

    def _issue(self, decision: RiskAuthorizationDecision) -> RiskAuthorizationDecision:
        with self._registry_lock:
            existing = self._issued_decisions.get(decision.decision_hash)
            if existing is not None and existing != decision:
                raise RiskAuthorizationError("AUTHORIZATION_IDENTITY_COLLISION", "decision hash collision detected")
            self._issued_decisions[decision.decision_hash] = decision
        return decision


def _safe_intent_identity(intent: object) -> tuple[str, str, bool]:
    try:
        canonical = _intent_canonical(intent)  # type: ignore[arg-type]
        return str(canonical["intent_id"]), _sha256(canonical), True
    except Exception:
        return "<invalid-intent>", _sha256({"invalid_intent": True}), False


def _safe_limits_hash(context: RiskExecutionContext) -> str:
    try:
        return _sha256(_limits_canonical(context.risk_limits))
    except RiskAuthorizationError:
        return _sha256({"invalid_limits": True})


__all__ = [
    "AUTHORIZATION_SCHEMA_VERSION", "CONSUMPTION_SCHEMA_VERSION", "RiskAuthorizationBoundary",
    "RiskAuthorizationConsumption", "RiskAuthorizationDecision", "RiskAuthorizationError",
    "RiskAuthorizationViolation",
]
