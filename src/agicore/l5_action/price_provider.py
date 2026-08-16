"""Deterministic, offline price observations for canonical L5 execution."""
from __future__ import annotations

import hashlib
import json
import math
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable


PRICE_OBSERVATION_SCHEMA_VERSION = "l5-price-observation/1.0"


class L5PriceProviderError(ValueError):
    """Controlled failure of the authoritative L5 price source."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


def _identifier(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise L5PriceProviderError("INVALID_PRICE_OBSERVATION", f"{name} must be non-blank")
    return value


def _price(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise L5PriceProviderError("INVALID_PRICE_OBSERVATION", "price must be finite and > 0")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized <= 0:
        raise L5PriceProviderError("INVALID_PRICE_OBSERVATION", "price must be finite and > 0")
    return normalized


def _version(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise L5PriceProviderError("INVALID_PRICE_OBSERVATION", "price version must be a positive integer")
    return value


def _time(value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise L5PriceProviderError("INVALID_PRICE_OBSERVATION", "observed_at must be timezone-aware")
    return value


def _canonical_sha256(value: object) -> str:
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise L5PriceProviderError(
            "INVALID_PRICE_OBSERVATION",
            "price observation is not canonically serializable",
        ) from exc
    return hashlib.sha256(encoded).hexdigest()


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


@dataclass(frozen=True)
class L5PriceObservation:
    """Immutable identity of one authoritative price-source state."""

    schema_version: str
    provider_id: str
    symbol: str
    price: float
    price_version: int
    observed_at: datetime
    observation_hash: str

    def __post_init__(self) -> None:
        if self.schema_version != PRICE_OBSERVATION_SCHEMA_VERSION:
            raise L5PriceProviderError("INVALID_PRICE_OBSERVATION", "schema version is invalid")
        object.__setattr__(self, "provider_id", _identifier(self.provider_id, "provider_id"))
        object.__setattr__(self, "symbol", _identifier(self.symbol, "symbol"))
        object.__setattr__(self, "price", _price(self.price))
        object.__setattr__(self, "price_version", _version(self.price_version))
        object.__setattr__(self, "observed_at", _time(self.observed_at))
        if not _is_sha256(self.observation_hash):
            raise L5PriceProviderError("INVALID_PRICE_OBSERVATION", "observation_hash is invalid")

    @classmethod
    def create(
        cls,
        *,
        provider_id: str,
        symbol: str,
        price: float,
        price_version: int,
        observed_at: datetime,
    ) -> "L5PriceObservation":
        fields = {
            "schema_version": PRICE_OBSERVATION_SCHEMA_VERSION,
            "provider_id": _identifier(provider_id, "provider_id"),
            "symbol": _identifier(symbol, "symbol"),
            "price": _price(price),
            "price_version": _version(price_version),
            "observed_at": _time(observed_at).isoformat(),
        }
        return cls(
            observation_hash=_canonical_sha256(fields),
            observed_at=observed_at,
            **{key: value for key, value in fields.items() if key != "observed_at"},
        )

    def fields_without_hash(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "provider_id": self.provider_id,
            "symbol": self.symbol,
            "price": self.price,
            "price_version": self.price_version,
            "observed_at": self.observed_at.isoformat(),
        }

    def canonical(self) -> dict[str, object]:
        return {**self.fields_without_hash(), "observation_hash": self.observation_hash}

    def is_intact(self) -> bool:
        try:
            return (
                self.schema_version == PRICE_OBSERVATION_SCHEMA_VERSION
                and _is_sha256(self.observation_hash)
                and self.observation_hash == _canonical_sha256(self.fields_without_hash())
            )
        except Exception:
            return False


@runtime_checkable
class L5PriceProvider(Protocol):
    """Versioned offline price authority used by the canonical L5 path."""

    @property
    def provider_id(self) -> str: ...

    def snapshot(self, symbol: str) -> L5PriceObservation: ...

    def assert_current(
        self,
        *,
        provider_id: str,
        symbol: str,
        expected_version: int,
        expected_hash: str,
    ) -> None: ...

    def locked_current(
        self,
        observation: L5PriceObservation,
    ) -> AbstractContextManager[L5PriceObservation]: ...


__all__ = [
    "L5PriceObservation",
    "L5PriceProvider",
    "L5PriceProviderError",
    "PRICE_OBSERVATION_SCHEMA_VERSION",
]
