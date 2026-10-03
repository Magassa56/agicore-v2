"""Synthetic trade-volume tests for V2; no market data, replay or OOS."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal, localcontext

import pytest

from agicore.trading.directional_impulse_v2 import (
    IMPULSE_VOLUME_LOOKBACK,
    IMPULSE_VOLUME_MEASURE,
    IMPULSE_VOLUME_MULTIPLIER,
    EmergingDirectionV2Error,
    ImpulseVolumeStatus,
    StructuralBarV2,
    TradeVolumeBarV2,
    evaluate_emerging_direction_v2,
    evaluate_impulse_volume_v2,
)
from agicore.trading.regime_context_v2 import RegimeDirection

START = datetime(2026, 10, 3, 10, 0, tzinfo=UTC)


def _bar(index: int, volume: Decimal | int | None, *, closed: bool = True) -> TradeVolumeBarV2:
    return TradeVolumeBarV2(
        index,
        START + timedelta(minutes=index),
        volume,
        closed,
        "BAR_TRADE_VOLUME",
        1,
        "Last",
    )


def _bars(
    prior_volumes: list[Decimal | int | None] | None = None,
    candidate_volume: Decimal | int | None = 150,
) -> dict[int, TradeVolumeBarV2]:
    volumes = [100] * 20 if prior_volumes is None else prior_volumes
    assert len(volumes) == 20
    return {index: _bar(index, volume) for index, volume in enumerate(volumes)} | {
        20: _bar(20, candidate_volume)
    }


@pytest.mark.parametrize(
    ("volume", "expected"),
    [
        ("150", True),
        ("149.9999999999999999999999999999999999999999", False),
        ("150.0000000000000000000000000000000000000001", True),
    ],
)
def test_exact_inclusive_threshold_without_precomparison_rounding(
    volume: str, expected: bool
) -> None:
    with localcontext() as context:
        context.prec = 2
        result = evaluate_impulse_volume_v2(
            impulse_candidate_bar_index=20,
            bars_by_index=_bars(candidate_volume=Decimal(volume)),
        )

    assert IMPULSE_VOLUME_LOOKBACK == 20
    assert IMPULSE_VOLUME_MEASURE == "BAR_TRADE_VOLUME"
    assert IMPULSE_VOLUME_MULTIPLIER == Decimal("1.50")
    assert result.status is ImpulseVolumeStatus.EVALUATED
    assert result.volume_qualified is expected
    assert result.candidate_volume == Decimal(volume)
    assert result.reference_volume == Decimal(100)
    assert result.required_volume == Decimal(150)


def test_nineteen_prior_completed_bars_are_insufficient() -> None:
    bars = {index: _bar(index, 100) for index in range(19)}
    bars[19] = _bar(19, 150)

    result = evaluate_impulse_volume_v2(impulse_candidate_bar_index=19, bars_by_index=bars)

    assert result.status is ImpulseVolumeStatus.INSUFFICIENT_WARMUP
    assert result.volume_qualified is False
    assert result.reference_volume is None


@pytest.mark.parametrize("missing", [0, 9, 19])
def test_missing_prior_bar_is_insufficient_history(missing: int) -> None:
    bars = _bars()
    del bars[missing]

    result = evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    assert result.status is ImpulseVolumeStatus.INSUFFICIENT_WARMUP
    assert result.volume_qualified is False


def test_unclosed_prior_bar_is_insufficient_completed_history() -> None:
    bars = _bars()
    bars[7] = replace(bars[7], is_closed=False)

    result = evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    assert result.status is ImpulseVolumeStatus.INSUFFICIENT_WARMUP
    assert result.volume_qualified is False


def test_even_window_median_is_exact_average_of_sorted_middle_values() -> None:
    bars = _bars([101, 100] * 10, candidate_volume=Decimal("150.75"))

    with localcontext() as context:
        context.prec = 2
        result = evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    assert result.reference_volume == Decimal("100.5")
    assert result.required_volume == Decimal("150.750")
    assert result.volume_qualified is True


def test_one_extreme_historical_volume_does_not_dominate_median() -> None:
    volumes = [100] * 20
    volumes[4] = 10**60

    result = evaluate_impulse_volume_v2(
        impulse_candidate_bar_index=20, bars_by_index=_bars(volumes)
    )

    assert result.reference_volume == Decimal(100)
    assert result.volume_qualified is True


@pytest.mark.parametrize("volumes", [[0] * 20, [0] * 19 + [10**60]])
def test_zero_reference_is_invalid_even_with_nonzero_candidate(volumes: list[int]) -> None:
    result = evaluate_impulse_volume_v2(
        impulse_candidate_bar_index=20, bars_by_index=_bars(volumes)
    )

    assert result.status is ImpulseVolumeStatus.INVALID_REFERENCE_VOLUME
    assert result.volume_qualified is False
    assert result.reference_volume == Decimal(0)
    assert result.required_volume is None


def test_zero_candidate_with_positive_reference_is_evaluated_false() -> None:
    result = evaluate_impulse_volume_v2(
        impulse_candidate_bar_index=20, bars_by_index=_bars(candidate_volume=0)
    )

    assert result.status is ImpulseVolumeStatus.EVALUATED
    assert result.volume_qualified is False


@pytest.mark.parametrize("index", [0, 9, 19, 20])
def test_any_selected_negative_volume_fails_closed(index: int) -> None:
    bars = _bars()
    bars[index] = replace(bars[index], volume=Decimal("-0.00000000000000000001"))

    result = evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    assert result.status is ImpulseVolumeStatus.INVALID_VOLUME
    assert result.volume_qualified is False
    assert result.required_volume is None


def test_missing_candidate_volume_has_explicit_status() -> None:
    result = evaluate_impulse_volume_v2(
        impulse_candidate_bar_index=20, bars_by_index=_bars(candidate_volume=None)
    )

    assert result.status is ImpulseVolumeStatus.INVALID_CANDIDATE_VOLUME
    assert result.volume_qualified is False


@pytest.mark.parametrize("index", [0, 9, 19])
def test_missing_reference_volume_is_not_treated_as_zero(index: int) -> None:
    bars = _bars()
    bars[index] = replace(bars[index], volume=None)

    result = evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    assert result.status is ImpulseVolumeStatus.INVALID_REFERENCE_VOLUME
    assert result.volume_qualified is False
    assert result.reference_volume is None


@pytest.mark.parametrize("index", [0, 20])
@pytest.mark.parametrize("value", [Decimal("NaN"), Decimal("Infinity"), 150.0, True])
def test_nonfinite_or_inexactly_typed_volume_fails_closed(index: int, value: object) -> None:
    bars = _bars()
    bars[index] = replace(bars[index], volume=value)

    result = evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    expected = (
        ImpulseVolumeStatus.INVALID_CANDIDATE_VOLUME
        if index == 20
        else ImpulseVolumeStatus.INVALID_REFERENCE_VOLUME
    )
    assert result.status is expected
    assert result.volume_qualified is False


def test_negative_volume_precedes_missing_values_with_complete_history() -> None:
    bars = _bars(candidate_volume=None)
    bars[0] = replace(bars[0], volume=-1)
    bars[1] = replace(bars[1], volume=None)

    result = evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    assert result.status is ImpulseVolumeStatus.INVALID_VOLUME
    assert result.volume_qualified is False


def test_candidate_mutation_never_changes_reference_and_t_is_excluded() -> None:
    bars = _bars(candidate_volume=149)
    before = evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)
    bars[20] = replace(bars[20], volume=10**60)
    after = evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    assert before.volume_qualified is False
    assert after.volume_qualified is True
    assert before.candidate_volume != after.candidate_volume
    assert before.reference_volume == after.reference_volume == Decimal(100)
    assert before.required_volume == after.required_volume == Decimal(150)


def test_future_bar_mutations_are_not_read_and_have_no_effect() -> None:
    class AuditedBars(dict[int, TradeVolumeBarV2]):
        def __init__(self, original: dict[int, TradeVolumeBarV2]) -> None:
            super().__init__(original)
            self.inspected: list[object] = []

        def __contains__(self, key: object) -> bool:
            self.inspected.append(key)
            return super().__contains__(key)

        def __getitem__(self, key: int) -> TradeVolumeBarV2:
            self.inspected.append(key)
            return super().__getitem__(key)

    bars = AuditedBars(_bars())
    before = evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)
    bars[21] = _bar(21, -1, closed=False)
    bars[22] = _bar(22, None, closed=False)
    after = evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)
    bars[21] = _bar(21, 10**60, closed=False)
    again = evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    assert before == after == again
    assert set(bars.inspected) == set(range(21))


def test_prior_window_is_exactly_twenty_and_ignores_earlier_data() -> None:
    bars = {index + 30: replace(bar, bar_index=index + 30) for index, bar in _bars().items()}
    bars[29] = _bar(29, -1)

    result = evaluate_impulse_volume_v2(impulse_candidate_bar_index=50, bars_by_index=bars)

    assert result.status is ImpulseVolumeStatus.EVALUATED
    assert result.reference_volume == Decimal(100)
    assert result.volume_qualified is True


@pytest.mark.parametrize("candidate_volume", [149, 150])
def test_volume_is_symmetric_and_does_not_choose_long_or_short(candidate_volume: int) -> None:
    volume_bars = _bars(candidate_volume=candidate_volume)
    results = []
    for sign, expected_direction in [(1, RegimeDirection.LONG), (-1, RegimeDirection.SHORT)]:
        structural_bars = {}
        for index in (17, 18, 19):
            close = Decimal(sign * index)
            structural_bars[index] = StructuralBarV2(
                index, START + timedelta(minutes=index), close - 1, close + 1, close, True
            )
        direction = evaluate_emerging_direction_v2(
            impulse_candidate_bar_index=20, bars_by_index=structural_bars
        )
        assert direction.emerging_direction is expected_direction
        results.append(
            evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=volume_bars)
        )

    assert results[0] == results[1]
    assert not hasattr(results[0], "event_direction")


def test_candidate_must_be_present_and_closed() -> None:
    bars = _bars()
    del bars[20]
    with pytest.raises(EmergingDirectionV2Error, match="closed candidate bar is required"):
        evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)
    bars[20] = _bar(20, 150, closed=False)
    with pytest.raises(EmergingDirectionV2Error, match="candidate bar must be closed"):
        evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)


def test_inconsistent_selected_indices_and_timestamps_fail_closed() -> None:
    bars = _bars()
    bars[20] = replace(bars[20], bar_index=21)
    with pytest.raises(EmergingDirectionV2Error, match="candidate bar index"):
        evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)
    bars = _bars()
    bars[8] = replace(bars[8], bar_index=7)
    with pytest.raises(EmergingDirectionV2Error, match="prior volume bar index"):
        evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)
    bars = _bars()
    bars[20] = replace(bars[20], timestamp_utc=bars[19].timestamp_utc)
    with pytest.raises(EmergingDirectionV2Error, match="candidate must follow"):
        evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)
    bars = _bars()
    bars[8] = replace(bars[8], timestamp_utc=bars[7].timestamp_utc)
    with pytest.raises(EmergingDirectionV2Error, match="timestamps must increase"):
        evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("volume_measure", "BID_ASK_VOLUME"),
        ("volume_measure", "DELTA"),
        ("volume_measure", "TICK_COUNT"),
        ("volume_measure", "ORDER_BOOK_IMBALANCE"),
        ("data_type", "Bid"),
        ("data_type", "Ask"),
        ("interval_minutes", 5),
    ],
)
def test_volume_source_substitutions_are_rejected(field: str, value: object) -> None:
    with pytest.raises(EmergingDirectionV2Error):
        replace(_bar(20, 150), **{field: value})


def test_repeated_evaluation_is_deterministic_and_results_are_immutable() -> None:
    bars = _bars()
    before = dict(bars)
    first = evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)
    second = evaluate_impulse_volume_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    assert first == second
    assert bars == before
    with pytest.raises(AttributeError):
        first.volume_qualified = False
    with pytest.raises(AttributeError):
        bars[20].volume = 0
