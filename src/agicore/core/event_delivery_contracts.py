"""Canonical contracts for durable EventBus delivery authority.

This module is deliberately independent from the legacy process-local EventBus.
It provides deterministic, deeply immutable values only; it performs no I/O and
never creates identifiers or timestamps implicitly.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType


DELIVERY_SCHEMA = "agicore.event-delivery.v1"
GENESIS_HASH = "0" * 64
_IDENTITY_PATTERN = re.compile(
    r"^[a-z0-9](?:[a-z0-9._:-]{0,126}[a-z0-9])?$"
)
_HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class ApplyStatus(str, Enum):
    """Result of applying one immutable authority record."""

    APPLIED_NEW = "APPLIED_NEW"
    ALREADY_APPLIED = "ALREADY_APPLIED"
    APPLIED_CONFIRMED = "APPLIED_CONFIRMED"
    CONFLICT = "CONFLICT"


class DispatchClass(str, Enum):
    """Stable dispatch class recorded in a handler manifest."""

    DIRECT = "direct"
    WILDCARD = "wildcard"


class JournalEventType(str, Enum):
    """Allowed append-only delivery-journal transitions."""

    EMISSION_ACCEPTED = "EMISSION_ACCEPTED"
    HANDLER_CLAIMED = "HANDLER_CLAIMED"
    HANDLER_CLAIM_RECOVERED = "HANDLER_CLAIM_RECOVERED"
    HANDLER_APPLIED = "HANDLER_APPLIED"
    HANDLER_COMPLETED = "HANDLER_COMPLETED"
    EMISSION_COMPLETED = "EMISSION_COMPLETED"


class ClaimStatus(str, Enum):
    """Outcome of an authoritative claim or recovery attempt."""

    CLAIMED = "CLAIMED"
    ALREADY_CLAIMED = "ALREADY_CLAIMED"
    UNAVAILABLE = "UNAVAILABLE"


def canonical_identity(value: object, *, field: str) -> str:
    """Return one validated lowercase deterministic identity."""
    if not isinstance(value, str) or _IDENTITY_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{field} must be a canonical lowercase identity")
    return value


def canonical_hash(value: object, *, field: str) -> str:
    """Return one validated lowercase SHA-256 hexadecimal digest."""
    if not isinstance(value, str) or _HASH_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{field} must be a lowercase SHA-256 digest")
    return value


def canonical_time(value: object, *, field: str) -> tuple[datetime, str]:
    """Normalize an explicitly supplied timezone-aware datetime to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must be an explicit timezone-aware datetime")
    normalized = value.astimezone(timezone.utc)
    rendered = normalized.isoformat(timespec="microseconds").replace("+00:00", "Z")
    return normalized, rendered


def canonical_json_value(value: object) -> object:
    """Create a detached canonical JSON value, rejecting ambiguity."""
    if value is None or isinstance(value, (bool, str, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("JSON numbers must be finite")
        return value
    if isinstance(value, (list, tuple)):
        return [canonical_json_value(item) for item in value]
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("JSON object keys must be strings")
        return {key: canonical_json_value(value[key]) for key in sorted(value)}
    raise ValueError(f"non-canonical JSON type: {type(value).__name__}")


def canonical_json_text(value: object) -> str:
    """Serialize a canonical JSON value without platform-dependent spacing."""
    try:
        canonical = canonical_json_value(value)
    except RecursionError as exc:
        raise ValueError("JSON value is recursive") from exc
    return json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_canonical(value: object) -> str:
    """Hash one canonical JSON value as UTF-8."""
    return hashlib.sha256(canonical_json_text(value).encode("utf-8")).hexdigest()


def freeze_json(value: object) -> object:
    """Create a deeply immutable projection of canonical JSON."""
    canonical = canonical_json_value(value)

    def freeze(item: object) -> object:
        if isinstance(item, dict):
            return MappingProxyType({key: freeze(child) for key, child in item.items()})
        if isinstance(item, list):
            return tuple(freeze(child) for child in item)
        return item

    return freeze(canonical)


@dataclass(frozen=True)
class HandlerManifestEntry:
    """One stable handler declaration owned by the delivery authority."""

    handler_id: str
    handler_version: str
    required: bool
    ordinal: int
    dispatch_class: DispatchClass

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "handler_id", canonical_identity(self.handler_id, field="handler_id")
        )
        object.__setattr__(
            self,
            "handler_version",
            canonical_identity(self.handler_version, field="handler_version"),
        )
        if not isinstance(self.required, bool):
            raise ValueError("required must be a boolean")
        if not isinstance(self.ordinal, int) or isinstance(self.ordinal, bool) or self.ordinal < 0:
            raise ValueError("ordinal must be a non-negative integer")
        try:
            dispatch = DispatchClass(self.dispatch_class)
        except (TypeError, ValueError) as exc:
            raise ValueError("dispatch_class is invalid") from exc
        object.__setattr__(self, "dispatch_class", dispatch)
        if self.required and (
            self.handler_id.startswith("anonymous") or "lambda" in self.handler_id
        ):
            raise ValueError("an anonymous callable can never be required")

    def canonical(self) -> Mapping[str, object]:
        """Return the immutable canonical representation."""
        return freeze_json(
            {
                "handler_id": self.handler_id,
                "handler_version": self.handler_version,
                "required": self.required,
                "ordinal": self.ordinal,
                "dispatch_class": self.dispatch_class.value,
            }
        )  # type: ignore[return-value]


@dataclass(frozen=True)
class PreparedManifest:
    """Canonical immutable handler-manifest snapshot."""

    runtime_profile_id: str
    event_type: str
    manifest_version: str
    entries: tuple[HandlerManifestEntry, ...]
    manifest_hash: str
    canonical_json: str


@dataclass(frozen=True)
class ManifestRecord:
    """Deeply immutable projection of a persisted manifest."""

    runtime_profile_id: str
    event_type: str
    manifest_version: str
    entries: tuple[HandlerManifestEntry, ...]
    manifest_hash: str
    registered_at: datetime


@dataclass(frozen=True)
class ManifestApplyResult:
    """Result of registering a bus-owned manifest."""

    status: ApplyStatus
    manifest: ManifestRecord


def prepare_manifest(
    *,
    runtime_profile_id: str,
    event_type: str,
    manifest_version: str,
    entries: Sequence[HandlerManifestEntry],
) -> PreparedManifest:
    """Validate and hash one authority-owned manifest definition."""
    profile = canonical_identity(runtime_profile_id, field="runtime_profile_id")
    event = canonical_identity(event_type, field="event_type")
    version = canonical_identity(manifest_version, field="manifest_version")
    if isinstance(entries, (str, bytes)) or not isinstance(entries, Sequence):
        raise ValueError("entries must be an explicit sequence")
    immutable_entries = tuple(entries)
    if any(not isinstance(item, HandlerManifestEntry) for item in immutable_entries):
        raise ValueError("entries must contain HandlerManifestEntry values")
    identities = [(item.handler_id, item.handler_version) for item in immutable_entries]
    ordinals = [item.ordinal for item in immutable_entries]
    if len(identities) != len(set(identities)):
        raise ValueError("handler_id/version must be unique in one manifest")
    if len(ordinals) != len(set(ordinals)):
        raise ValueError("handler ordinals must be unique in one manifest")
    ordered = tuple(sorted(immutable_entries, key=lambda item: item.ordinal))
    content = {
        "schema": DELIVERY_SCHEMA,
        "runtime_profile_id": profile,
        "event_type": event,
        "manifest_version": version,
        "handlers": [dict(item.canonical()) for item in ordered],
    }
    canonical = canonical_json_text(content)
    return PreparedManifest(
        runtime_profile_id=profile,
        event_type=event,
        manifest_version=version,
        entries=ordered,
        manifest_hash=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        canonical_json=canonical,
    )


def verify_manifest(value: PreparedManifest) -> PreparedManifest:
    """Reconstruct a prepared manifest and reject forged internal values."""
    if not isinstance(value, PreparedManifest):
        raise ValueError("manifest input has an invalid prepared type")
    rebuilt = prepare_manifest(
        runtime_profile_id=value.runtime_profile_id,
        event_type=value.event_type,
        manifest_version=value.manifest_version,
        entries=value.entries,
    )
    if rebuilt != value:
        raise ValueError("prepared manifest differs from canonical reconstruction")
    return rebuilt


@dataclass(frozen=True)
class PreparedEmission:
    """Canonical immutable emission ready for SQL acceptance."""

    authority_id: str
    authority_version: str
    runtime_profile_id: str
    manifest_version: str
    source_identity: str
    consumer_id: str
    outcome_id: str
    outcome_hash: str
    receipt_hash: str
    source_sequence: int
    event_type: str
    occurred_at: datetime
    occurred_at_text: str
    accepted_at: datetime
    accepted_at_text: str
    payload: Mapping[str, object]
    payload_json: str
    payload_hash: str
    manifest_hash: str
    emission_effect_id: str


@dataclass(frozen=True)
class EmissionRecord:
    """Deeply immutable projection of one durable emission."""

    source_identity: str
    consumer_id: str
    outcome_id: str
    outcome_hash: str
    receipt_hash: str
    source_sequence: int
    event_type: str
    occurred_at: datetime
    accepted_at: datetime
    payload: Mapping[str, object]
    payload_hash: str
    runtime_profile_id: str
    manifest_version: str
    manifest_hash: str
    emission_effect_id: str
    accepted_sequence: int
    status: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", freeze_json(self.payload))


@dataclass(frozen=True)
class DeliveryRecord:
    """Immutable projection of one handler-delivery state."""

    emission_effect_id: str
    handler_effect_id: str
    consumer_id: str
    source_sequence: int
    accepted_sequence: int
    handler_id: str
    handler_version: str
    required: bool
    ordinal: int
    dispatch_class: DispatchClass
    status: str
    fencing_generation: int
    worker_identity: str | None
    claimed_at: datetime | None
    result_status: ApplyStatus | None
    result_hash: str | None
    result: Mapping[str, object] | None

    def __post_init__(self) -> None:
        if self.result is not None:
            object.__setattr__(self, "result", freeze_json(self.result))


@dataclass(frozen=True)
class EmissionApplyResult:
    """Atomic emission-acceptance result and exact delivery snapshot."""

    status: ApplyStatus
    emission: EmissionRecord
    deliveries: tuple[DeliveryRecord, ...]
    emission_accepted_hash: str
    emission_completed_hash: str | None


@dataclass(frozen=True)
class ClaimResult:
    """Result of claiming or explicitly recovering one delivery."""

    status: ClaimStatus
    delivery: DeliveryRecord


@dataclass(frozen=True)
class AnchorRecord:
    """Immutable final anchor for one delivery journal."""

    authority_id: str
    authority_version: str
    last_sequence: int
    last_hash: str


@dataclass(frozen=True)
class ReplayResult:
    """Verified projection reconstructed from the append-only journal."""

    anchor: AnchorRecord
    emissions: tuple[EmissionRecord, ...]
    deliveries: tuple[DeliveryRecord, ...]


def prepare_emission(
    *,
    authority_id: str,
    authority_version: str,
    runtime_profile_id: str,
    manifest_version: str,
    manifest_hash: str,
    source_identity: str,
    consumer_id: str,
    outcome_id: str,
    outcome_hash: str,
    receipt_hash: str,
    source_sequence: int,
    event_type: str,
    occurred_at: datetime,
    accepted_at: datetime,
    payload: Mapping[str, object],
) -> PreparedEmission:
    """Canonicalize an emission after the authority resolved its manifest."""
    identities = {
        "authority_id": canonical_identity(authority_id, field="authority_id"),
        "authority_version": canonical_identity(authority_version, field="authority_version"),
        "runtime_profile_id": canonical_identity(
            runtime_profile_id, field="runtime_profile_id"
        ),
        "manifest_version": canonical_identity(manifest_version, field="manifest_version"),
        "source_identity": canonical_identity(source_identity, field="source_identity"),
        "consumer_id": canonical_identity(consumer_id, field="consumer_id"),
        "outcome_id": canonical_identity(outcome_id, field="outcome_id"),
        "event_type": canonical_identity(event_type, field="event_type"),
    }
    outcome_digest = canonical_hash(outcome_hash, field="outcome_hash")
    receipt_digest = canonical_hash(receipt_hash, field="receipt_hash")
    manifest_digest = canonical_hash(manifest_hash, field="manifest_hash")
    source_sequence = canonical_source_sequence(source_sequence)
    event_time, event_time_text = canonical_time(occurred_at, field="occurred_at")
    acceptance_time, acceptance_time_text = canonical_time(accepted_at, field="accepted_at")
    if not isinstance(payload, Mapping):
        raise ValueError("payload must be a mapping")
    payload_value = canonical_json_value(payload)
    if not isinstance(payload_value, dict):  # pragma: no cover - guarded above
        raise ValueError("payload must canonicalize to an object")
    payload_json = canonical_json_text(payload_value)
    payload_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
    effect_content = {
        "schema": DELIVERY_SCHEMA,
        "runtime_profile_id": identities["runtime_profile_id"],
        "consumer_id": identities["consumer_id"],
        "outcome_id": identities["outcome_id"],
        "outcome_hash": outcome_digest,
        "receipt_hash": receipt_digest,
        "source_sequence": source_sequence,
        "event_type": identities["event_type"],
        "occurred_at": event_time_text,
        "payload_hash": payload_hash,
        "manifest_hash": manifest_digest,
    }
    return PreparedEmission(
        **identities,
        outcome_hash=outcome_digest,
        receipt_hash=receipt_digest,
        source_sequence=source_sequence,
        occurred_at=event_time,
        occurred_at_text=event_time_text,
        accepted_at=acceptance_time,
        accepted_at_text=acceptance_time_text,
        payload=freeze_json(payload_value),  # type: ignore[arg-type]
        payload_json=payload_json,
        payload_hash=payload_hash,
        manifest_hash=manifest_digest,
        emission_effect_id=sha256_canonical(effect_content),
    )


def canonical_source_sequence(value: int) -> int:
    """Require the strictly positive causal sequence supplied by the source."""
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError("source_sequence must be a positive integer")
    return value


def verify_emission(value: PreparedEmission) -> PreparedEmission:
    """Reconstruct a prepared emission and reject forged internal values."""
    if not isinstance(value, PreparedEmission):
        raise ValueError("emission input has an invalid prepared type")
    rebuilt = prepare_emission(
        authority_id=value.authority_id,
        authority_version=value.authority_version,
        runtime_profile_id=value.runtime_profile_id,
        manifest_version=value.manifest_version,
        manifest_hash=value.manifest_hash,
        source_identity=value.source_identity,
        consumer_id=value.consumer_id,
        outcome_id=value.outcome_id,
        outcome_hash=value.outcome_hash,
        receipt_hash=value.receipt_hash,
        source_sequence=value.source_sequence,
        event_type=value.event_type,
        occurred_at=value.occurred_at,
        accepted_at=value.accepted_at,
        payload=value.payload,
    )
    if rebuilt != value:
        raise ValueError("prepared emission differs from canonical reconstruction")
    return rebuilt


def handler_effect_id(
    *, emission_effect_id: str, handler_id: str, handler_version: str
) -> str:
    """Derive the deterministic identity of one handler effect."""
    return sha256_canonical(
        {
            "schema": DELIVERY_SCHEMA,
            "emission_effect_id": canonical_hash(
                emission_effect_id, field="emission_effect_id"
            ),
            "handler_id": canonical_identity(handler_id, field="handler_id"),
            "handler_version": canonical_identity(
                handler_version, field="handler_version"
            ),
        }
    )


def synthetic_result_hash(
    *, handler_effect_digest: str, status: ApplyStatus, payload: Mapping[str, object]
) -> tuple[str, str, Mapping[str, object]]:
    """Canonicalize one synthetic B1 handler result and derive its hash."""
    effect = canonical_hash(handler_effect_digest, field="handler_effect_id")
    try:
        result_status = ApplyStatus(status)
    except (TypeError, ValueError) as exc:
        raise ValueError("handler result status is invalid") from exc
    if not isinstance(payload, Mapping):
        raise ValueError("handler result payload must be a mapping")
    canonical_payload = canonical_json_value(payload)
    if not isinstance(canonical_payload, dict):  # pragma: no cover
        raise ValueError("handler result payload must canonicalize to an object")
    payload_json = canonical_json_text(canonical_payload)
    digest = sha256_canonical(
        {
            "schema": DELIVERY_SCHEMA,
            "handler_effect_id": effect,
            "status": result_status.value,
            "payload_hash": hashlib.sha256(payload_json.encode("utf-8")).hexdigest(),
        }
    )
    return digest, payload_json, freeze_json(canonical_payload)  # type: ignore[return-value]


def journal_event_hash(
    *,
    sequence: int,
    authority_id: str,
    authority_version: str,
    event_type: JournalEventType,
    emission_effect_id: str,
    handler_effect_digest: str | None,
    fencing_generation: int,
    occurred_at: datetime,
    payload_hash: str,
    previous_hash: str,
) -> str:
    """Reconstruct the hash of one immutable journal event."""
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence <= 0:
        raise ValueError("journal sequence must be a positive integer")
    if type(fencing_generation) is not int or fencing_generation < 0:
        raise ValueError("fencing_generation must be non-negative")
    _, rendered_time = canonical_time(occurred_at, field="journal occurred_at")
    return sha256_canonical(
        {
            "schema": DELIVERY_SCHEMA,
            "sequence": sequence,
            "authority_id": canonical_identity(authority_id, field="authority_id"),
            "authority_version": canonical_identity(
                authority_version, field="authority_version"
            ),
            "event_type": JournalEventType(event_type).value,
            "emission_effect_id": canonical_hash(
                emission_effect_id, field="emission_effect_id"
            ),
            "handler_effect_id": (
                canonical_hash(handler_effect_digest, field="handler_effect_id")
                if handler_effect_digest is not None
                else None
            ),
            "fencing_generation": fencing_generation,
            "occurred_at": rendered_time,
            "payload_hash": canonical_hash(payload_hash, field="payload_hash"),
            "previous_hash": canonical_hash(previous_hash, field="previous_hash"),
        }
    )


__all__ = [
    "ApplyStatus",
    "AnchorRecord",
    "ClaimResult",
    "ClaimStatus",
    "DELIVERY_SCHEMA",
    "DeliveryRecord",
    "DispatchClass",
    "EmissionApplyResult",
    "EmissionRecord",
    "GENESIS_HASH",
    "HandlerManifestEntry",
    "JournalEventType",
    "ManifestApplyResult",
    "ManifestRecord",
    "PreparedEmission",
    "PreparedManifest",
    "ReplayResult",
    "canonical_hash",
    "canonical_identity",
    "canonical_json_text",
    "canonical_json_value",
    "canonical_source_sequence",
    "canonical_time",
    "freeze_json",
    "handler_effect_id",
    "journal_event_hash",
    "prepare_emission",
    "prepare_manifest",
    "sha256_canonical",
    "synthetic_result_hash",
    "verify_emission",
    "verify_manifest",
]
