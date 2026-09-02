"""Pydantic schemas for Event."""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


_IDEMPOTENT_EVENT_SCHEMA = "agicore.memory-effect.v1"
_EFFECT_ID_PATTERN = re.compile(
    r"^[a-z0-9](?:[a-z0-9._:-]{0,126}[a-z0-9])?$"
)


class EventCreate(BaseModel):
    """DTO d'entrée pour créer un event."""
    event_type: str = Field(..., min_length=1, max_length=64)
    task_id: str | None = Field(default=None, max_length=64)
    agent_id: str | None = Field(default=None, max_length=64)
    session_id: str | None = Field(default=None, max_length=64)
    payload: dict[str, Any] = Field(default_factory=dict)


class EventRead(BaseModel):
    """DTO de sortie pour lire un event."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    task_id: str | None
    agent_id: str | None
    session_id: str | None
    payload: dict[str, Any]
    created_at: datetime


class IdempotentEventCreate(BaseModel):
    """Validated repository input for one canonical idempotent event."""

    model_config = ConfigDict(frozen=True)

    effect_id: str = Field(..., min_length=1, max_length=128)
    payload_hash: str = Field(..., pattern=r"^[0-9a-f]{64}$")
    occurred_at: datetime
    event_type: str = Field(..., min_length=1, max_length=64)
    task_id: str | None = Field(default=None, max_length=64)
    agent_id: str | None = Field(default=None, max_length=64)
    session_id: str | None = Field(default=None, max_length=64)
    payload: dict[str, Any]


def _canonical_json_value(value: object) -> object:
    if value is None or isinstance(value, (bool, str, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("payload numbers must be finite")
        return value
    if isinstance(value, list):
        return [_canonical_json_value(item) for item in value]
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("payload object keys must be strings")
        return {key: _canonical_json_value(value[key]) for key in sorted(value)}
    raise ValueError(f"payload contains non-canonical JSON type: {type(value).__name__}")


def _canonical_time(value: datetime) -> tuple[datetime, str]:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("occurred_at must be an explicit timezone-aware datetime")
    normalized = value.astimezone(timezone.utc)
    rendered = normalized.isoformat(timespec="microseconds").replace("+00:00", "Z")
    return normalized, rendered


def prepare_idempotent_event(
    *,
    effect_id: str,
    occurred_at: datetime,
    event_type: str,
    task_id: str | None = None,
    agent_id: str | None = None,
    session_id: str | None = None,
    payload: Mapping[str, object],
) -> IdempotentEventCreate:
    """Purely canonicalize and hash one idempotent memory event."""
    if not isinstance(effect_id, str) or _EFFECT_ID_PATTERN.fullmatch(effect_id) is None:
        raise ValueError("effect_id must be a canonical lowercase identifier")
    normalized_time, rendered_time = _canonical_time(occurred_at)
    if not isinstance(payload, Mapping):
        raise ValueError("payload must be a mapping")
    try:
        canonical_payload = _canonical_json_value(payload)
    except RecursionError as exc:
        raise ValueError("payload contains a recursive value") from exc
    if not isinstance(canonical_payload, dict):  # pragma: no cover - guarded above
        raise ValueError("payload must canonicalize to an object")

    legacy_shape = EventCreate(
        event_type=event_type,
        task_id=task_id,
        agent_id=agent_id,
        session_id=session_id,
        payload=canonical_payload,
    )
    semantic_content = {
        "schema_version": _IDEMPOTENT_EVENT_SCHEMA,
        "event_type": legacy_shape.event_type,
        "occurred_at": rendered_time,
        "task_id": legacy_shape.task_id,
        "agent_id": legacy_shape.agent_id,
        "session_id": legacy_shape.session_id,
        "payload": canonical_payload,
    }
    encoded = json.dumps(
        semantic_content,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return IdempotentEventCreate(
        effect_id=effect_id,
        payload_hash=hashlib.sha256(encoded).hexdigest(),
        occurred_at=normalized_time,
        event_type=legacy_shape.event_type,
        task_id=legacy_shape.task_id,
        agent_id=legacy_shape.agent_id,
        session_id=legacy_shape.session_id,
        payload=canonical_payload,
    )


def verify_idempotent_event(
    dto: IdempotentEventCreate,
) -> IdempotentEventCreate:
    """Rebuild a repository input and reject any forged internal representation."""
    if not isinstance(dto, IdempotentEventCreate):
        raise ValueError("idempotent event input has an invalid DTO type")
    try:
        prepared = prepare_idempotent_event(
            effect_id=dto.effect_id,
            occurred_at=dto.occurred_at,
            event_type=dto.event_type,
            task_id=dto.task_id,
            agent_id=dto.agent_id,
            session_id=dto.session_id,
            payload=dto.payload,
        )
        supplied_hash = dto.payload_hash
    except (AttributeError, TypeError) as exc:
        raise ValueError("idempotent event DTO is incomplete or malformed") from exc
    if supplied_hash != prepared.payload_hash:
        raise ValueError("payload_hash does not match canonical event content")
    return prepared


class IdempotentEventApplyStatus(str, Enum):
    APPLIED_NEW = "APPLIED_NEW"
    ALREADY_APPLIED = "ALREADY_APPLIED"
    CONFLICT = "CONFLICT"


def _freeze_json(value: object) -> object:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze_json(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    return value


@dataclass(frozen=True)
class IdempotentEventRecord:
    """Deeply immutable projection of the authoritative SQL event row."""

    id: int
    effect_id: str
    payload_hash: str
    event_type: str
    occurred_at: datetime
    task_id: str | None
    agent_id: str | None
    session_id: str | None
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", _freeze_json(dict(self.payload)))


@dataclass(frozen=True)
class IdempotentEventApplyResult:
    """Authoritative outcome of an idempotent event application."""

    status: IdempotentEventApplyStatus
    event: IdempotentEventRecord


__all__ = [
    "EventCreate",
    "EventRead",
    "IdempotentEventApplyResult",
    "IdempotentEventApplyStatus",
    "IdempotentEventCreate",
    "IdempotentEventRecord",
    "prepare_idempotent_event",
    "verify_idempotent_event",
]
