"""Synthetic closed-bar tests for the V2 emerging-direction prerequisite."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from agicore.trading.directional_impulse_v2 import (
    EMERGING_DIRECTION_LOOKBACK,
    EmergingDirectionStatus,
    EmergingDirectionV2Error,
    StructuralBarV2,
    evaluate_emerging_direction_v2,
)
from agicore.trading.regime_context_v2 import RegimeDirection

START = datetime(2026, 10, 3, 10, 0, tzinfo=UTC)


def _bar(
    index: int,
    *,
    close: str,
    low: str,
    high: str,
    closed: bool = True,
) -> StructuralBarV2:
    return StructuralBarV2(
        index, START + timedelta(minutes=index), Decimal(low), Decimal(high), Decimal(close), closed
    )


def _long_bars() -> dict[int, StructuralBarV2]:
    return {
        0: _bar(0, close="10", low="9", high="13"),
        1: _bar(1, close="11", low="9", high="14"),
        2: _bar(2, close="12", low="10", high="15"),
    }


def _short_bars() -> dict[int, StructuralBarV2]:
    return {
        0: _bar(0, close="12", low="9", high="13"),
        1: _bar(1, close="11", low="8", high="13"),
        2: _bar(2, close="10", low="7", high="13"),
    }


@pytest.mark.parametrize(
    ("bars", "direction"),
    [(_long_bars(), RegimeDirection.LONG), (_short_bars(), RegimeDirection.SHORT)],
)
def test_symmetric_directions_allow_equal_lows_or_highs(
    bars: dict[int, StructuralBarV2], direction: RegimeDirection
) -> None:
    result = evaluate_emerging_direction_v2(impulse_candidate_bar_index=3, bars_by_index=bars)

    assert EMERGING_DIRECTION_LOOKBACK == 3
    assert result.status is EmergingDirectionStatus.EVALUATED
    assert result.emerging_direction is direction
    assert result.impulse_candidate_bar_index == 3
    assert result.known_at_bar_index == 2
    assert result.known_at_timestamp == bars[2].timestamp_utc


@pytest.mark.parametrize("side", [RegimeDirection.LONG, RegimeDirection.SHORT])
@pytest.mark.parametrize("equality_pair", [(0, 1), (1, 2)])
def test_equal_closes_reject_emerging_direction(
    side: RegimeDirection, equality_pair: tuple[int, int]
) -> None:
    bars = _long_bars() if side is RegimeDirection.LONG else _short_bars()
    first, second = equality_pair
    bars[second] = replace(bars[second], close=bars[first].close)

    result = evaluate_emerging_direction_v2(impulse_candidate_bar_index=3, bars_by_index=bars)

    assert result.status is EmergingDirectionStatus.EVALUATED
    assert result.emerging_direction is None


def test_lower_low_rejects_long_despite_strictly_rising_closes() -> None:
    bars = _long_bars()
    bars[1] = replace(bars[1], low=Decimal(8))

    result = evaluate_emerging_direction_v2(impulse_candidate_bar_index=3, bars_by_index=bars)

    assert result.emerging_direction is None


def test_higher_high_rejects_short_despite_strictly_falling_closes() -> None:
    bars = _short_bars()
    bars[1] = replace(bars[1], high=Decimal(14))

    result = evaluate_emerging_direction_v2(impulse_candidate_bar_index=3, bars_by_index=bars)

    assert result.emerging_direction is None


@pytest.mark.parametrize("candidate", [0, 1, 2])
def test_too_early_candidate_has_insufficient_warmup(candidate: int) -> None:
    result = evaluate_emerging_direction_v2(
        impulse_candidate_bar_index=candidate, bars_by_index=_long_bars()
    )

    assert result.status is EmergingDirectionStatus.INSUFFICIENT_WARMUP
    assert result.emerging_direction is None
    assert result.known_at_bar_index is None
    assert result.known_at_timestamp is None


@pytest.mark.parametrize("missing", [0, 1, 2])
def test_missing_required_closed_bar_has_insufficient_warmup(missing: int) -> None:
    bars = _long_bars()
    del bars[missing]

    result = evaluate_emerging_direction_v2(impulse_candidate_bar_index=3, bars_by_index=bars)

    assert result.status is EmergingDirectionStatus.INSUFFICIENT_WARMUP
    assert result.emerging_direction is None


def test_only_t_minus_three_to_t_minus_one_required_for_later_candidate() -> None:
    bars = {index + 20: replace(bar, bar_index=index + 20) for index, bar in _short_bars().items()}

    result = evaluate_emerging_direction_v2(impulse_candidate_bar_index=23, bars_by_index=bars)

    assert result.status is EmergingDirectionStatus.EVALUATED
    assert result.emerging_direction is RegimeDirection.SHORT
    assert result.known_at_bar_index == 22


def test_candidate_and_future_mutation_cannot_change_pre_impulse_direction() -> None:
    bars = _long_bars()
    before_candidate_exists = evaluate_emerging_direction_v2(
        impulse_candidate_bar_index=3, bars_by_index=bars
    )
    bars[3] = _bar(3, close="6", low="5", high="7", closed=False)
    bars[4] = _bar(4, close="5", low="4", high="6", closed=False)
    with_candidate = evaluate_emerging_direction_v2(
        impulse_candidate_bar_index=3, bars_by_index=bars
    )
    bars[3] = _bar(3, close="20", low="18", high="22", closed=True)
    bars[4] = _bar(4, close="21", low="19", high="23", closed=True)
    after_mutation = evaluate_emerging_direction_v2(
        impulse_candidate_bar_index=3, bars_by_index=bars
    )

    assert before_candidate_exists == with_candidate == after_mutation
    assert after_mutation.known_at_bar_index == 2
    assert after_mutation.emerging_direction is RegimeDirection.LONG


def test_candidate_key_is_not_even_accessed() -> None:
    class AuditedBars(dict[int, StructuralBarV2]):
        inspected: list[object]

        def __init__(self, original: dict[int, StructuralBarV2]) -> None:
            super().__init__(original)
            self.inspected = []

        def __contains__(self, key: object) -> bool:
            self.inspected.append(key)
            return super().__contains__(key)

        def __getitem__(self, key: int) -> StructuralBarV2:
            self.inspected.append(key)
            return super().__getitem__(key)

    bars = AuditedBars(_long_bars())
    bars[3] = _bar(3, close="6", low="5", high="7", closed=False)
    bars[4] = _bar(4, close="5", low="4", high="6", closed=False)

    result = evaluate_emerging_direction_v2(impulse_candidate_bar_index=3, bars_by_index=bars)

    assert result.emerging_direction is RegimeDirection.LONG
    assert bars.inspected == [0, 1, 2, 0, 1, 2]


@pytest.mark.parametrize("not_closed_index", [0, 1, 2])
def test_pre_impulse_bar_must_be_closed(not_closed_index: int) -> None:
    bars = _long_bars()
    bars[not_closed_index] = replace(bars[not_closed_index], is_closed=False)

    with pytest.raises(EmergingDirectionV2Error, match="must be closed"):
        evaluate_emerging_direction_v2(impulse_candidate_bar_index=3, bars_by_index=bars)


def test_wrong_index_and_nonchronological_timestamps_fail_closed() -> None:
    bars = _long_bars()
    bars[1] = replace(bars[1], bar_index=10)
    with pytest.raises(EmergingDirectionV2Error, match="index is inconsistent"):
        evaluate_emerging_direction_v2(impulse_candidate_bar_index=3, bars_by_index=bars)

    bars = _long_bars()
    bars[1] = replace(bars[1], timestamp_utc=bars[0].timestamp_utc)
    with pytest.raises(EmergingDirectionV2Error, match="timestamps must increase"):
        evaluate_emerging_direction_v2(impulse_candidate_bar_index=3, bars_by_index=bars)


@pytest.mark.parametrize("index", [-1, True, "3"])
def test_invalid_candidate_index_rejected(index: object) -> None:
    with pytest.raises(EmergingDirectionV2Error, match="candidate index"):
        evaluate_emerging_direction_v2(impulse_candidate_bar_index=index, bars_by_index={})


def test_immutable_result_and_repeatability() -> None:
    bars = _short_bars()
    first = evaluate_emerging_direction_v2(impulse_candidate_bar_index=3, bars_by_index=bars)
    second = evaluate_emerging_direction_v2(impulse_candidate_bar_index=3, bars_by_index=bars)

    assert first == second
    with pytest.raises(AttributeError):
        first.emerging_direction = RegimeDirection.LONG


@pytest.mark.parametrize(
    ("change", "match"),
    [
        ({"close": Decimal("NaN")}, "finite Decimal"),
        ({"low": Decimal(12)}, "inside the low/high range"),
        ({"timestamp_utc": START.replace(tzinfo=None)}, "aware UTC"),
        ({"is_closed": 1}, "is_closed must be a boolean"),
    ],
)
def test_invalid_structural_observation_rejected(change: dict[str, object], match: str) -> None:
    with pytest.raises(EmergingDirectionV2Error, match=match):
        replace(_long_bars()[0], **change)
