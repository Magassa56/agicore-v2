"""Offline market-price fixture with fail-closed legacy broker mutation APIs.

Canonical L5 orders are published only by ``L5ExecutionTransactionStore``.
This historical class remains useful as a deterministic price source, but it
cannot create, fill, cancel, or expose mutable order/position state.
"""
from __future__ import annotations

import threading
from contextlib import contextmanager
from datetime import datetime
from typing import Iterator

from .broker_models import Broker, ExecutionReport, Order, OrderRequest, Position
from .execution_service import L5RiskGateRequiredError
from .price_provider import L5PriceObservation, L5PriceProviderError


class MockBroker:
    """Read-only offline price source; raw broker actions fail closed."""

    NAME = "mock_broker"

    def __init__(self, *, provider_id: str = "mock-broker-price") -> None:
        if not isinstance(provider_id, str) or not provider_id.strip():
            raise L5PriceProviderError("INVALID_PRICE_PROVIDER", "provider_id must be non-blank")
        self._lock = threading.RLock()
        self._provider_id = provider_id
        self._version = 0
        self._observations: dict[str, L5PriceObservation] = {}

    @property
    def provider_id(self) -> str:
        return self._provider_id

    def set_market_price(
        self,
        symbol: str,
        price: float,
        *,
        observed_at: datetime,
    ) -> L5PriceObservation:
        with self._lock:
            next_version = self._version + 1
            observation = L5PriceObservation.create(
                provider_id=self._provider_id,
                symbol=symbol,
                price=price,
                price_version=next_version,
                observed_at=observed_at,
            )
            self._version = next_version
            self._observations[observation.symbol] = observation
            return observation

    def snapshot(self, symbol: str) -> L5PriceObservation:
        if not isinstance(symbol, str) or not symbol.strip():
            raise L5PriceProviderError("INVALID_PRICE_OBSERVATION", "symbol must be non-blank")
        with self._lock:
            observation = self._observations.get(symbol)
            if observation is None:
                raise L5PriceProviderError("MISSING_PRICE_OBSERVATION", f"no price for {symbol}")
            return observation

    def assert_current(
        self,
        *,
        provider_id: str,
        symbol: str,
        expected_version: int,
        expected_hash: str,
    ) -> None:
        with self._lock:
            self._assert_current_locked(
                provider_id=provider_id,
                symbol=symbol,
                expected_version=expected_version,
                expected_hash=expected_hash,
            )

    @contextmanager
    def locked_current(
        self,
        observation: L5PriceObservation,
    ) -> Iterator[L5PriceObservation]:
        if not isinstance(observation, L5PriceObservation) or not observation.is_intact():
            raise L5PriceProviderError("INVALID_PRICE_OBSERVATION", "observation is not intact")
        with self._lock:
            self._assert_current_locked(
                provider_id=observation.provider_id,
                symbol=observation.symbol,
                expected_version=observation.price_version,
                expected_hash=observation.observation_hash,
            )
            yield self._observations[observation.symbol]

    def _assert_current_locked(
        self,
        *,
        provider_id: str,
        symbol: str,
        expected_version: int,
        expected_hash: str,
    ) -> None:
        current = self._observations.get(symbol)
        if (
            provider_id != self._provider_id
            or current is None
            or current.price_version != expected_version
            or current.observation_hash != expected_hash
        ):
            raise L5PriceProviderError(
                "STALE_PRICE_OBSERVATION",
                "price provider version/hash differs",
            )

    def get_market_price(self, symbol: str) -> float | None:
        with self._lock:
            observation = self._observations.get(symbol)
            return observation.price if observation is not None else None

    def submit_order(self, request: OrderRequest) -> ExecutionReport:
        raise L5RiskGateRequiredError("MockBroker.submit_order cannot publish L5 state")

    def cancel_order(self, order_id: str) -> ExecutionReport:
        raise L5RiskGateRequiredError("MockBroker.cancel_order cannot publish L5 state")

    def get_position(self, symbol: str) -> Position | None:
        return None

    def get_open_orders(self) -> list[Order]:
        return []

    def get_order(self, order_id: str) -> Order | None:
        return None

    def get_all_orders(self) -> list[Order]:
        return []

    def reset(self) -> None:
        with self._lock:
            self._version += 1
            self._observations.clear()

    def _fill_order(self, *args: object, **kwargs: object) -> ExecutionReport:
        raise L5RiskGateRequiredError("direct MockBroker fill is disabled")

    def _apply_fill_to_position(self, *args: object, **kwargs: object) -> None:
        raise L5RiskGateRequiredError("direct MockBroker position mutation is disabled")


_: Broker = MockBroker()

__all__ = ["MockBroker"]
