"""Deterministic, offline risk-execution context and tamper-evident journal.

This module deliberately defines data contracts only.  It neither evaluates
risk rules nor submits orders.
"""
from __future__ import annotations

import hashlib
import json
import math
import threading
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from .exposure_models import ExposureSnapshot, RiskLimits, SymbolExposure


SCHEMA_VERSION = "risk-execution-journal/1.0"
_GENESIS_VALUE = {"kind": "risk-execution-journal-genesis", "schema_version": SCHEMA_VERSION}


class RiskContextError(ValueError):
    """A controlled violation of the deterministic context contract."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


def _canonical_json(value: object) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise RiskContextError("INVALID_RISK_CONTEXT", "value is not canonically JSON serializable") from exc


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


# A SHA-256 of the documented, canonical ``_GENESIS_VALUE`` above.
GENESIS_EVENT_HASH = _sha256(_GENESIS_VALUE)


def _require_identifier(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RiskContextError("INVALID_RISK_CONTEXT", f"{field_name} must be a non-blank string")
    return value


def _require_version(value: object, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RiskContextError("INVALID_RISK_CONTEXT", f"{field_name} must be a non-negative integer")
    return value


def _require_number(value: object, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise RiskContextError("INVALID_RISK_CONTEXT", f"{field_name} must be a finite number")
    return float(value)


def _freeze_json(value: object) -> object:
    """Defensively copy and deeply freeze JSON-compatible data."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise RiskContextError("INVALID_RISK_CONTEXT", "payload contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, nested in value.items():
            if not isinstance(key, str):
                raise RiskContextError("INVALID_RISK_CONTEXT", "payload mapping keys must be strings")
            frozen[key] = _freeze_json(nested)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(item) for item in value)
    raise RiskContextError("INVALID_RISK_CONTEXT", "payload is not canonically JSON serializable")


def _thaw_json(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _thaw_json(nested) for key, nested in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


def _freeze_positions(value: object) -> Mapping[str, float]:
    if not isinstance(value, Mapping):
        raise RiskContextError("INVALID_RISK_CONTEXT", "signed_positions must be a mapping")
    positions: dict[str, float] = {}
    for instrument, quantity in value.items():
        _require_identifier(instrument, "signed_positions key")
        positions[instrument] = _require_number(quantity, f"signed_positions[{instrument}]")
    return MappingProxyType(positions)


def _copy_limits(value: object) -> RiskLimits:
    if not isinstance(value, RiskLimits):
        raise RiskContextError("INVALID_RISK_CONTEXT", "risk_limits must be a RiskLimits instance")
    canonical = value.model_dump(mode="json")
    _canonical_json(canonical)
    return RiskLimits.model_validate(canonical)


def _snapshot_canonical(value: ExposureSnapshot) -> dict[str, object]:
    """Serialize a snapshot even after its positions mapping was frozen."""
    return {
        "positions": {
            symbol: exposure.model_dump(mode="json")
            for symbol, exposure in sorted(value.positions.items())
        },
        "realized_pnl_total": value.realized_pnl_total,
        "daily_pnl": value.daily_pnl,
        "initial_equity": value.initial_equity,
        "peak_equity": value.peak_equity,
    }


def _copy_snapshot(value: object) -> ExposureSnapshot:
    if not isinstance(value, ExposureSnapshot):
        raise RiskContextError("INVALID_RISK_CONTEXT", "exposure_snapshot must be an ExposureSnapshot instance")
    canonical = _snapshot_canonical(value)
    _canonical_json(canonical)
    snapshot = ExposureSnapshot.model_validate(canonical)
    # Pydantic's frozen model does not freeze its ``dict`` field.  Replace it
    # with a defensive immutable copy without changing ExposureSnapshot's
    # public contract globally.
    object.__setattr__(snapshot, "positions", MappingProxyType(dict(snapshot.positions)))
    return snapshot


def _require_snapshot_metrics(
    snapshot: ExposureSnapshot,
    *,
    daily_realized_pnl: float,
    current_equity: float,
    peak_equity: float,
    owner: str,
) -> None:
    if (
        daily_realized_pnl != snapshot.daily_pnl
        or current_equity != snapshot.current_equity
        or peak_equity != snapshot.peak_equity
    ):
        raise RiskContextError("INVALID_RISK_CONTEXT", f"{owner} metrics must match exposure_snapshot")


def _require_long_only_position_consistency(
    signed_positions: Mapping[str, float],
    snapshot: ExposureSnapshot,
    *,
    owner: str,
) -> None:
    """Enforce the long-only position contract of risk-execution-journal/1.0.

    The existing RiskManager reads ``ExposureSnapshot.positions`` and models
    only long exposure.  Signed short positions are therefore rejected here
    until a separately versioned signed-exposure model exists.
    """
    normalized_signed: dict[str, float] = {}
    for symbol, quantity in signed_positions.items():
        if quantity < 0:
            raise RiskContextError("INVALID_RISK_CONTEXT", f"{owner} rejects short signed positions in schema 1.0")
        if quantity > 0:
            normalized_signed[symbol] = quantity

    published_snapshot: dict[str, float] = {}
    for symbol, exposure in snapshot.positions.items():
        if not isinstance(exposure, SymbolExposure):
            raise RiskContextError("INVALID_RISK_CONTEXT", "snapshot position must be a SymbolExposure")
        if symbol != exposure.symbol:
            raise RiskContextError("INVALID_RISK_CONTEXT", "snapshot position key must equal SymbolExposure.symbol")
        quantity = _require_number(exposure.quantity, f"snapshot quantity for {symbol}")
        if quantity <= 0:
            raise RiskContextError("INVALID_RISK_CONTEXT", "published snapshot quantity must be strictly positive")
        published_snapshot[symbol] = quantity

    if normalized_signed.keys() != published_snapshot.keys():
        raise RiskContextError("INVALID_RISK_CONTEXT", f"{owner} signed and snapshot position symbols must match")
    for symbol, quantity in normalized_signed.items():
        if quantity != published_snapshot[symbol]:
            raise RiskContextError("INVALID_RISK_CONTEXT", f"{owner} signed and snapshot quantities must match")


def _is_sha256_hex(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(character in "0123456789abcdef" for character in value)


@dataclass(frozen=True)
class RiskExecutionContext:
    provider_id: str
    state_version: int
    trading_day: str
    risk_limits: RiskLimits
    exposure_snapshot: ExposureSnapshot
    signed_positions: Mapping[str, float]
    daily_realized_pnl: float
    current_equity: float
    peak_equity: float
    execution_enabled: bool
    kill_switch_active: bool
    legacy_hard_deny: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "provider_id", _require_identifier(self.provider_id, "provider_id"))
        object.__setattr__(self, "state_version", _require_version(self.state_version, "state_version"))
        object.__setattr__(self, "trading_day", _require_identifier(self.trading_day, "trading_day"))
        object.__setattr__(self, "risk_limits", _copy_limits(self.risk_limits))
        object.__setattr__(self, "exposure_snapshot", _copy_snapshot(self.exposure_snapshot))
        object.__setattr__(self, "signed_positions", _freeze_positions(self.signed_positions))
        for name in ("daily_realized_pnl", "current_equity", "peak_equity"):
            object.__setattr__(self, name, _require_number(getattr(self, name), name))
        for name in ("execution_enabled", "kill_switch_active", "legacy_hard_deny"):
            if not isinstance(getattr(self, name), bool):
                raise RiskContextError("INVALID_RISK_CONTEXT", f"{name} must be a boolean")
        if self.peak_equity < self.current_equity:
            raise RiskContextError("INVALID_RISK_CONTEXT", "peak_equity cannot be below current_equity")
        _require_snapshot_metrics(
            self.exposure_snapshot,
            daily_realized_pnl=self.daily_realized_pnl,
            current_equity=self.current_equity,
            peak_equity=self.peak_equity,
            owner="RiskExecutionContext",
        )
        _require_long_only_position_consistency(self.signed_positions, self.exposure_snapshot, owner="RiskExecutionContext")

    def canonical(self) -> dict[str, object]:
        return {
            "provider_id": self.provider_id,
            "state_version": self.state_version,
            "trading_day": self.trading_day,
            "risk_limits": self.risk_limits.model_dump(mode="json"),
            "exposure_snapshot": _snapshot_canonical(self.exposure_snapshot),
            "signed_positions": dict(sorted(self.signed_positions.items())),
            "daily_realized_pnl": self.daily_realized_pnl,
            "current_equity": self.current_equity,
            "peak_equity": self.peak_equity,
            "execution_enabled": self.execution_enabled,
            "kill_switch_active": self.kill_switch_active,
            "legacy_hard_deny": self.legacy_hard_deny,
        }

    @property
    def state_hash(self) -> str:
        return _sha256(self.canonical())


@dataclass(frozen=True)
class FillTransition:
    intent_id: str
    fill_id: str
    signed_positions: Mapping[str, float]
    exposure_snapshot: ExposureSnapshot
    daily_realized_pnl: float
    current_equity: float
    expected_peak_equity: float
    payload: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "intent_id", _require_identifier(self.intent_id, "intent_id"))
        object.__setattr__(self, "fill_id", _require_identifier(self.fill_id, "fill_id"))
        object.__setattr__(self, "signed_positions", _freeze_positions(self.signed_positions))
        object.__setattr__(self, "exposure_snapshot", _copy_snapshot(self.exposure_snapshot))
        for name in ("daily_realized_pnl", "current_equity", "expected_peak_equity"):
            object.__setattr__(self, name, _require_number(getattr(self, name), name))
        object.__setattr__(self, "payload", _freeze_json(self.payload))
        _require_snapshot_metrics(
            self.exposure_snapshot,
            daily_realized_pnl=self.daily_realized_pnl,
            current_equity=self.current_equity,
            peak_equity=self.expected_peak_equity,
            owner="FillTransition",
        )
        _require_long_only_position_consistency(self.signed_positions, self.exposure_snapshot, owner="FillTransition")

    def canonical(self) -> dict[str, object]:
        return {
            "intent_id": self.intent_id,
            "fill_id": self.fill_id,
            "signed_positions": dict(sorted(self.signed_positions.items())),
            "exposure_snapshot": _snapshot_canonical(self.exposure_snapshot),
            "daily_realized_pnl": self.daily_realized_pnl,
            "current_equity": self.current_equity,
            "expected_peak_equity": self.expected_peak_equity,
            "payload": _thaw_json(self.payload),
        }


class RiskContextProvider(Protocol):
    def snapshot(self) -> RiskExecutionContext: ...
    def assert_current(self, expected_version: int, expected_hash: str) -> None: ...
    def commit_fill(self, expected_version: int, expected_hash: str, fill_transition: FillTransition) -> RiskExecutionContext: ...
    def start_trading_day(self, expected_version: int, expected_hash: str, new_trading_day: str) -> RiskExecutionContext: ...


@dataclass(frozen=True)
class RiskExecutionJournalEvent:
    schema_version: str
    sequence_number: int
    event_type: str
    provider_id: str
    intent_id: str | None
    state_version_before: int
    state_version_after: int
    context_hash_before: str
    context_hash_after: str
    payload: Mapping[str, object]
    previous_event_hash: str
    event_hash: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", _freeze_json(self.payload))

    @classmethod
    def create(
        cls,
        *,
        sequence_number: int,
        event_type: str,
        provider_id: str,
        intent_id: str | None,
        state_version_before: int,
        state_version_after: int,
        context_hash_before: str,
        context_hash_after: str,
        payload: Mapping[str, object],
        previous_event_hash: str,
    ) -> "RiskExecutionJournalEvent":
        frozen_payload = _freeze_json(payload)
        fields = {
            "schema_version": SCHEMA_VERSION,
            "sequence_number": sequence_number,
            "event_type": event_type,
            "provider_id": provider_id,
            "intent_id": intent_id,
            "state_version_before": state_version_before,
            "state_version_after": state_version_after,
            "context_hash_before": context_hash_before,
            "context_hash_after": context_hash_after,
            "payload": _thaw_json(frozen_payload),
            "previous_event_hash": previous_event_hash,
        }
        stored_fields = dict(fields)
        stored_fields["payload"] = frozen_payload
        return cls(event_hash=_sha256(fields), **stored_fields)

    def fields_without_hash(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "sequence_number": self.sequence_number,
            "event_type": self.event_type,
            "provider_id": self.provider_id,
            "intent_id": self.intent_id,
            "state_version_before": self.state_version_before,
            "state_version_after": self.state_version_after,
            "context_hash_before": self.context_hash_before,
            "context_hash_after": self.context_hash_after,
            "payload": _thaw_json(self.payload),
            "previous_event_hash": self.previous_event_hash,
        }


class InMemoryRiskContextProvider:
    """Serialized compare-and-swap provider for offline tests and replay."""

    def __init__(self, context: RiskExecutionContext) -> None:
        self._context = context
        self._lock = threading.RLock()
        self._journal: list[RiskExecutionJournalEvent] = []
        self._journal.append(
            self._make_event("CONTEXT_SNAPSHOTTED", context, context, None, {"context": context.canonical()})
        )

    @property
    def journal(self) -> tuple[RiskExecutionJournalEvent, ...]:
        with self._lock:
            return tuple(self._journal)

    def snapshot(self) -> RiskExecutionContext:
        with self._lock:
            return self._context

    def assert_current(self, expected_version: int, expected_hash: str) -> None:
        _require_version(expected_version, "expected_version")
        if not isinstance(expected_hash, str) or not expected_hash:
            raise RiskContextError("STALE_RISK_CONTEXT", "expected hash is required")
        with self._lock:
            if expected_version != self._context.state_version or expected_hash != self._context.state_hash:
                raise RiskContextError("STALE_RISK_CONTEXT", "version or hash does not match current context")

    def commit_fill(self, expected_version: int, expected_hash: str, fill_transition: FillTransition) -> RiskExecutionContext:
        if not isinstance(fill_transition, FillTransition):
            raise RiskContextError("INVALID_FILL_TRANSITION", "fill_transition must be a FillTransition")
        with self._lock:
            self.assert_current(expected_version, expected_hash)
            before = self._context
            peak = max(before.peak_equity, fill_transition.current_equity)
            if fill_transition.expected_peak_equity != peak:
                raise RiskContextError("INVALID_FILL_TRANSITION", "expected peak equity is inconsistent")
            next_context = RiskExecutionContext(
                provider_id=before.provider_id,
                state_version=before.state_version + 1,
                trading_day=before.trading_day,
                risk_limits=before.risk_limits,
                exposure_snapshot=fill_transition.exposure_snapshot,
                signed_positions=fill_transition.signed_positions,
                daily_realized_pnl=fill_transition.daily_realized_pnl,
                current_equity=fill_transition.current_equity,
                peak_equity=peak,
                execution_enabled=before.execution_enabled,
                kill_switch_active=before.kill_switch_active,
                legacy_hard_deny=before.legacy_hard_deny,
            )
            fill_event = self._make_event(
                "FILL_RECEIVED", before, next_context, fill_transition.intent_id, {"transition": fill_transition.canonical()}
            )
            commit_event = self._make_event(
                "STATE_COMMITTED", before, next_context, fill_transition.intent_id,
                {"context": next_context.canonical()}, previous_hash=fill_event.event_hash,
            )
            self._context = next_context
            self._journal.extend((fill_event, commit_event))
            return next_context

    def start_trading_day(self, expected_version: int, expected_hash: str, new_trading_day: str) -> RiskExecutionContext:
        _require_identifier(new_trading_day, "new_trading_day")
        with self._lock:
            self.assert_current(expected_version, expected_hash)
            before = self._context
            if new_trading_day == before.trading_day:
                raise RiskContextError("INVALID_TRADING_DAY", "new trading day must differ from current trading day")
            reset_snapshot = ExposureSnapshot(
                positions=dict(before.exposure_snapshot.positions),
                realized_pnl_total=before.exposure_snapshot.realized_pnl_total,
                daily_pnl=0.0,
                initial_equity=before.exposure_snapshot.initial_equity,
                peak_equity=before.exposure_snapshot.peak_equity,
            )
            next_context = RiskExecutionContext(
                provider_id=before.provider_id,
                state_version=before.state_version + 1,
                trading_day=new_trading_day,
                risk_limits=before.risk_limits,
                exposure_snapshot=reset_snapshot,
                signed_positions=before.signed_positions,
                daily_realized_pnl=reset_snapshot.daily_pnl,
                current_equity=reset_snapshot.current_equity,
                peak_equity=reset_snapshot.peak_equity,
                execution_enabled=before.execution_enabled,
                kill_switch_active=before.kill_switch_active,
                legacy_hard_deny=before.legacy_hard_deny,
            )
            day_event = self._make_event("TRADING_DAY_STARTED", before, next_context, None, {"new_trading_day": new_trading_day})
            commit_event = self._make_event(
                "STATE_COMMITTED", before, next_context, None,
                {"context": next_context.canonical()}, previous_hash=day_event.event_hash,
            )
            self._context = next_context
            self._journal.extend((day_event, commit_event))
            return next_context

    def _make_event(
        self,
        event_type: str,
        before: RiskExecutionContext,
        after: RiskExecutionContext,
        intent_id: str | None,
        payload: Mapping[str, object],
        previous_hash: str | None = None,
    ) -> RiskExecutionJournalEvent:
        return RiskExecutionJournalEvent.create(
            sequence_number=len(self._journal) + 1 if previous_hash is None else len(self._journal) + 2,
            event_type=event_type,
            provider_id=before.provider_id,
            intent_id=intent_id,
            state_version_before=before.state_version,
            state_version_after=after.state_version,
            context_hash_before=before.state_hash,
            context_hash_after=after.state_hash,
            payload=payload,
            previous_event_hash=(
                GENESIS_EVENT_HASH if not self._journal and previous_hash is None
                else self._journal[-1].event_hash if previous_hash is None
                else previous_hash
            ),
        )


def validate_journal(events: object) -> str:
    if not isinstance(events, tuple):
        try:
            events = tuple(events)  # type: ignore[arg-type]
        except TypeError as exc:
            raise RiskContextError("INVALID_JOURNAL", "journal must be an iterable of events") from exc
    if not events:
        raise RiskContextError("INVALID_JOURNAL", "journal must not be empty")
    previous = GENESIS_EVENT_HASH
    provider_id: str | None = None
    for index, event in enumerate(events, start=1):
        if not isinstance(event, RiskExecutionJournalEvent):
            raise RiskContextError("INVALID_JOURNAL", "journal contains an invalid event")
        if event.schema_version != SCHEMA_VERSION:
            raise RiskContextError("INVALID_JOURNAL", "unsupported schema version")
        if event.sequence_number != index or event.previous_event_hash != previous:
            raise RiskContextError("INVALID_JOURNAL", "sequence or previous hash mismatch")
        if not _is_sha256_hex(event.event_hash):
            raise RiskContextError("INVALID_JOURNAL", "event hash is invalid")
        if _sha256(event.fields_without_hash()) != event.event_hash:
            raise RiskContextError("INVALID_JOURNAL", "stored event hash mismatch")
        if provider_id is None:
            provider_id = event.provider_id
        elif event.provider_id != provider_id:
            raise RiskContextError("INVALID_JOURNAL", "provider changed")
        previous = event.event_hash
    return previous


def replay_journal(events: object, expected_final_hash: str | None = None) -> tuple[RiskExecutionContext, str]:
    if not isinstance(events, tuple):
        try:
            events = tuple(events)  # type: ignore[arg-type]
        except TypeError as exc:
            raise RiskContextError("INVALID_JOURNAL", "journal must be an iterable of events") from exc
    journal_hash = validate_journal(events)
    if expected_final_hash is not None and not _is_sha256_hex(expected_final_hash):
        raise RiskContextError("INVALID_JOURNAL", "expected final hash must be a SHA-256 hexadecimal digest")
    if expected_final_hash is not None and journal_hash != expected_final_hash:
        raise RiskContextError("INVALID_JOURNAL", "journal final hash does not match expected anchor")
    first = events[0]
    if first.event_type != "CONTEXT_SNAPSHOTTED" or first.intent_id is not None or first.previous_event_hash != GENESIS_EVENT_HASH:
        raise RiskContextError("INVALID_JOURNAL", "first event must be a genesis-linked context snapshot")
    context = _context_from_payload(first.payload)
    if (
        first.provider_id != context.provider_id
        or first.state_version_before != context.state_version
        or first.state_version_after != context.state_version
        or first.context_hash_before != context.state_hash
        or first.context_hash_after != context.state_hash
    ):
        raise RiskContextError("INVALID_JOURNAL", "initial snapshot metadata is inconsistent")
    if _thaw_json(first.payload) != {"context": context.canonical()}:
        raise RiskContextError("INVALID_JOURNAL", "initial snapshot payload is inconsistent")

    index = 1
    while index < len(events):
        if index + 1 >= len(events):
            raise RiskContextError("INVALID_JOURNAL", "orphan operational event")
        operation, committed = events[index], events[index + 1]
        if operation.event_type not in {"FILL_RECEIVED", "TRADING_DAY_STARTED"} or committed.event_type != "STATE_COMMITTED":
            raise RiskContextError("INVALID_JOURNAL", "orphan operational or state committed event")
        if committed.intent_id != operation.intent_id:
            raise RiskContextError("INVALID_JOURNAL", "operation and committed intent identifiers differ")
        if operation.provider_id != context.provider_id or committed.provider_id != context.provider_id:
            raise RiskContextError("INVALID_JOURNAL", "provider changed")
        for event in (operation, committed):
            if event.state_version_before != context.state_version or event.context_hash_before != context.state_hash:
                raise RiskContextError("INVALID_JOURNAL", "before state metadata is inconsistent")
        next_context = _context_from_payload(committed.payload)
        if next_context.provider_id != context.provider_id:
            raise RiskContextError("INVALID_JOURNAL", "committed context provider changed")
        if next_context.state_version != context.state_version + 1:
            raise RiskContextError("INVALID_JOURNAL", "state version did not increment by one")
        for event in (operation, committed):
            if event.state_version_after != next_context.state_version or event.context_hash_after != next_context.state_hash:
                raise RiskContextError("INVALID_JOURNAL", "after state metadata is inconsistent")
        if _thaw_json(committed.payload) != {"context": next_context.canonical()}:
            raise RiskContextError("INVALID_JOURNAL", "committed context payload is inconsistent")
        if operation.event_type == "FILL_RECEIVED":
            _validate_fill_operation(operation, context, next_context)
        else:
            _validate_trading_day_operation(operation, context, next_context)
        context = next_context
        index += 2
    return context, journal_hash


def _context_from_payload(payload: Mapping[str, object]) -> RiskExecutionContext:
    value = _thaw_json(payload)
    if not isinstance(value, dict) or set(value) != {"context"} or not isinstance(value["context"], dict):
        raise RiskContextError("INVALID_JOURNAL", "context payload is missing or malformed")
    context = value["context"]
    try:
        return RiskExecutionContext(
            provider_id=context["provider_id"], state_version=context["state_version"], trading_day=context["trading_day"],
            risk_limits=RiskLimits.model_validate(context["risk_limits"]), exposure_snapshot=ExposureSnapshot.model_validate(context["exposure_snapshot"]),
            signed_positions=context["signed_positions"], daily_realized_pnl=context["daily_realized_pnl"], current_equity=context["current_equity"],
            peak_equity=context["peak_equity"], execution_enabled=context["execution_enabled"], kill_switch_active=context["kill_switch_active"], legacy_hard_deny=context["legacy_hard_deny"],
        )
    except (KeyError, TypeError, RiskContextError, ValueError) as exc:
        raise RiskContextError("INVALID_JOURNAL", "context payload is invalid") from exc


def _validate_fill_operation(event: RiskExecutionJournalEvent, before: RiskExecutionContext, after: RiskExecutionContext) -> None:
    payload = _thaw_json(event.payload)
    if not isinstance(payload, dict) or set(payload) != {"transition"} or not isinstance(payload["transition"], dict):
        raise RiskContextError("INVALID_JOURNAL", "fill transition payload is malformed")
    data = payload["transition"]
    try:
        transition = FillTransition(
            intent_id=data["intent_id"], fill_id=data["fill_id"], signed_positions=data["signed_positions"],
            exposure_snapshot=ExposureSnapshot.model_validate(data["exposure_snapshot"]), daily_realized_pnl=data["daily_realized_pnl"],
            current_equity=data["current_equity"], expected_peak_equity=data["expected_peak_equity"], payload=data["payload"],
        )
    except (KeyError, TypeError, RiskContextError, ValueError) as exc:
        raise RiskContextError("INVALID_JOURNAL", "fill transition is invalid") from exc
    if event.intent_id != transition.intent_id:
        raise RiskContextError("INVALID_JOURNAL", "fill intent does not match event")
    if (
        dict(after.signed_positions) != dict(transition.signed_positions)
        or after.exposure_snapshot != transition.exposure_snapshot
        or after.daily_realized_pnl != transition.daily_realized_pnl
        or after.current_equity != transition.current_equity
        or after.peak_equity != transition.expected_peak_equity
        or after.trading_day != before.trading_day
        or after.risk_limits != before.risk_limits
        or after.execution_enabled != before.execution_enabled
        or after.kill_switch_active != before.kill_switch_active
        or after.legacy_hard_deny != before.legacy_hard_deny
    ):
        raise RiskContextError("INVALID_JOURNAL", "fill transition does not match committed context")


def _validate_trading_day_operation(event: RiskExecutionJournalEvent, before: RiskExecutionContext, after: RiskExecutionContext) -> None:
    payload = _thaw_json(event.payload)
    if not isinstance(payload, dict) or set(payload) != {"new_trading_day"} or event.intent_id is not None:
        raise RiskContextError("INVALID_JOURNAL", "trading day payload is malformed")
    new_day = _require_identifier(payload["new_trading_day"], "new_trading_day")
    if (
        new_day != after.trading_day
        or new_day == before.trading_day
        or after.daily_realized_pnl != 0.0
        or dict(after.signed_positions) != dict(before.signed_positions)
        or dict(after.exposure_snapshot.positions) != dict(before.exposure_snapshot.positions)
        or after.exposure_snapshot.realized_pnl_total != before.exposure_snapshot.realized_pnl_total
        or after.exposure_snapshot.initial_equity != before.exposure_snapshot.initial_equity
        or after.exposure_snapshot.peak_equity != before.exposure_snapshot.peak_equity
        or after.exposure_snapshot.daily_pnl != 0.0
        or after.current_equity != before.current_equity
        or after.peak_equity != before.peak_equity
        or after.risk_limits != before.risk_limits
        or after.execution_enabled != before.execution_enabled
        or after.kill_switch_active != before.kill_switch_active
        or after.legacy_hard_deny != before.legacy_hard_deny
    ):
        raise RiskContextError("INVALID_JOURNAL", "trading day transition does not match committed context")


__all__ = [
    "FillTransition", "GENESIS_EVENT_HASH", "InMemoryRiskContextProvider", "RiskContextError", "RiskContextProvider",
    "RiskExecutionContext", "RiskExecutionJournalEvent", "SCHEMA_VERSION", "replay_journal", "validate_journal",
]
