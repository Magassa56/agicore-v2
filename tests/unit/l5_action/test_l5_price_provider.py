from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from agicore.l5_action.broker_mock import MockBroker
from agicore.l5_action.price_provider import (
    L5PriceObservation,
    L5PriceProviderError,
    PRICE_OBSERVATION_SCHEMA_VERSION,
)


NOW = datetime(2026, 8, 15, 10, 0, tzinfo=timezone.utc)


def test_price_observation_is_deterministic_immutable_and_versioned() -> None:
    left = L5PriceObservation.create(
        provider_id="offline-price", symbol="ES", price=100.0,
        price_version=1, observed_at=NOW,
    )
    right = L5PriceObservation.create(
        provider_id="offline-price", symbol="ES", price=100.0,
        price_version=1, observed_at=NOW,
    )
    assert left == right and left.is_intact()
    assert left.schema_version == PRICE_OBSERVATION_SCHEMA_VERSION
    assert len(left.observation_hash) == 64
    with pytest.raises(Exception):
        left.price = 101.0

    provider = MockBroker(provider_id="offline-price")
    first = provider.set_market_price("ES", 100.0, observed_at=NOW)
    second = provider.set_market_price("ES", 101.0, observed_at=NOW + timedelta(seconds=1))
    assert (first.price_version, second.price_version) == (1, 2)
    assert first.observation_hash != second.observation_hash


@pytest.mark.parametrize(
    ("price", "observed_at"),
    [
        (0.0, NOW),
        (-1.0, NOW),
        (float("nan"), NOW),
        (float("inf"), NOW),
        (True, NOW),
        (100.0, datetime(2026, 8, 15, 10, 0)),
    ],
)
def test_invalid_price_observations_are_rejected(price, observed_at) -> None:
    provider = MockBroker()
    with pytest.raises(L5PriceProviderError):
        provider.set_market_price("ES", price, observed_at=observed_at)


def test_stale_and_fully_rehashed_forged_observations_are_rejected() -> None:
    provider = MockBroker(provider_id="offline-price")
    current = provider.set_market_price("ES", 100.0, observed_at=NOW)
    forged = L5PriceObservation.create(
        provider_id=current.provider_id,
        symbol=current.symbol,
        price=1.0,
        price_version=current.price_version,
        observed_at=current.observed_at,
    )
    assert forged.is_intact() and forged.observation_hash != current.observation_hash
    with pytest.raises(L5PriceProviderError) as exc:
        with provider.locked_current(forged):
            pass
    assert exc.value.code == "STALE_PRICE_OBSERVATION"

    provider.set_market_price("ES", 101.0, observed_at=NOW + timedelta(seconds=1))
    with pytest.raises(L5PriceProviderError) as stale:
        provider.assert_current(
            provider_id=current.provider_id,
            symbol=current.symbol,
            expected_version=current.price_version,
            expected_hash=current.observation_hash,
        )
    assert stale.value.code == "STALE_PRICE_OBSERVATION"


def test_structurally_tampered_observation_is_not_intact() -> None:
    observation = L5PriceObservation.create(
        provider_id="offline-price", symbol="ES", price=100.0,
        price_version=1, observed_at=NOW,
    )
    assert replace(observation, price=1.0).is_intact() is False
