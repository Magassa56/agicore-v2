"""Synthetic exact-range tests for V2, without a market dataset or replay."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal, localcontext

import pytest

from agicore.trading.directional_impulse_v2 import (
    IMPULSE_RANGE_LOOKBACK,
    IMPULSE_RANGE_MULTIPLIER,
    EmergingDirectionV2Error,
    ImpulseRangeStatus,
    StructuralBarV2,
    evaluate_impulse_range_v2,
)

START = datetime(2026, 10, 3, 10, 0, tzinfo=UTC)


def _bar(
    index: int,
    span: str,
    *,
    closed: bool = True,
    close: str = "0",
) -> StructuralBarV2:
    return StructuralBarV2(
        index,
        START + timedelta(minutes=index),
        Decimal(0),
        Decimal(span),
        Decimal(close),
        closed,
    )


def _bars(
    prior_spans: list[str] | None = None, candidate_span: str = "1.50"
) -> dict[int, StructuralBarV2]:
    spans = ["1"] * 20 if prior_spans is None else prior_spans
    assert len(spans) == 20
    return {index: _bar(index, span) for index, span in enumerate(spans)} | {
        20: _bar(20, candidate_span)
    }


@pytest.mark.parametrize(
    ("candidate_span", "expected"),
    [
        ("1.50", True),
        ("1.4999999999999999999999999999999999999999", False),
        ("1.5000000000000000000000000000000000000001", True),
    ],
)
def test_exact_inclusive_threshold_without_precomparison_rounding(
    candidate_span: str, expected: bool
) -> None:
    result = evaluate_impulse_range_v2(
        impulse_candidate_bar_index=20,
        bars_by_index=_bars(candidate_span=candidate_span),
    )

    assert IMPULSE_RANGE_LOOKBACK == 20
    assert IMPULSE_RANGE_MULTIPLIER == Decimal("1.50")
    assert result.status is ImpulseRangeStatus.EVALUATED
    assert result.range_qualified is expected
    assert result.reference_range == Decimal(1)
    assert result.required_range == Decimal("1.50")
    assert result.candidate_range == Decimal(candidate_span)


def test_nineteen_prior_bars_are_insufficient() -> None:
    bars = {index: _bar(index, "1") for index in range(19)}
    bars[19] = _bar(19, "1.50")

    result = evaluate_impulse_range_v2(impulse_candidate_bar_index=19, bars_by_index=bars)

    assert result.status is ImpulseRangeStatus.INSUFFICIENT_WARMUP
    assert result.range_qualified is False
    assert result.reference_range is None


@pytest.mark.parametrize("missing", [0, 9, 19])
def test_gap_inside_prior_twenty_is_insufficient(missing: int) -> None:
    bars = _bars()
    del bars[missing]

    result = evaluate_impulse_range_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    assert result.status is ImpulseRangeStatus.INSUFFICIENT_WARMUP
    assert result.range_qualified is False


def test_even_window_median_averages_both_middle_values_exactly() -> None:
    bars = _bars(["1"] * 10 + ["2"] * 10, candidate_span="2.25")

    with localcontext() as context:
        context.prec = 2
        result = evaluate_impulse_range_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    assert result.status is ImpulseRangeStatus.EVALUATED
    assert result.reference_range == Decimal("1.5")
    assert result.required_range == Decimal("2.250")
    assert result.range_qualified is True


def test_single_reference_outlier_does_not_change_median() -> None:
    spans = ["1"] * 20
    spans[4] = "1000"

    result = evaluate_impulse_range_v2(impulse_candidate_bar_index=20, bars_by_index=_bars(spans))

    assert result.reference_range == Decimal(1)
    assert result.required_range == Decimal("1.50")
    assert result.range_qualified is True


@pytest.mark.parametrize("spans", [["0"] * 20, ["0"] * 19 + ["1000"]])
def test_zero_reference_fails_closed(spans: list[str]) -> None:
    result = evaluate_impulse_range_v2(impulse_candidate_bar_index=20, bars_by_index=_bars(spans))

    assert result.status is ImpulseRangeStatus.INVALID_REFERENCE_RANGE
    assert result.range_qualified is False
    assert result.reference_range == Decimal(0)
    assert result.required_range is None


def test_candidate_mutation_changes_range_only_and_candidate_is_excluded_from_median() -> None:
    bars = _bars(candidate_span="1.49")
    before = evaluate_impulse_range_v2(impulse_candidate_bar_index=20, bars_by_index=bars)
    bars[20] = _bar(20, "1000")
    after = evaluate_impulse_range_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    assert before.range_qualified is False
    assert after.range_qualified is True
    assert before.reference_range == after.reference_range == Decimal(1)
    assert before.required_range == after.required_range == Decimal("1.50")
    assert before.candidate_range != after.candidate_range


def test_future_bars_are_never_read_or_used() -> None:
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

    bars = AuditedBars(_bars())
    baseline = evaluate_impulse_range_v2(impulse_candidate_bar_index=20, bars_by_index=bars)
    bars[21] = _bar(21, "1000", closed=False)
    bars[22] = _bar(22, "0", closed=False)
    after = evaluate_impulse_range_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    assert baseline == after
    assert set(bars.inspected) == set(range(21))
    assert 21 not in bars.inspected and 22 not in bars.inspected


def test_prior_window_is_exactly_twenty_for_later_candidate() -> None:
    bars = {index + 30: replace(bar, bar_index=index + 30) for index, bar in _bars().items()}

    result = evaluate_impulse_range_v2(impulse_candidate_bar_index=50, bars_by_index=bars)

    assert result.status is ImpulseRangeStatus.EVALUATED
    assert result.range_qualified is True


def test_candidate_must_be_present_and_closed() -> None:
    bars = _bars()
    del bars[20]
    with pytest.raises(EmergingDirectionV2Error, match="closed candidate bar is required"):
        evaluate_impulse_range_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    bars[20] = _bar(20, "1.50", closed=False)
    with pytest.raises(EmergingDirectionV2Error, match="candidate bar must be closed"):
        evaluate_impulse_range_v2(impulse_candidate_bar_index=20, bars_by_index=bars)


def test_unclosed_prior_bar_is_insufficient_completed_history() -> None:
    bars = _bars()
    bars[7] = replace(bars[7], is_closed=False)

    result = evaluate_impulse_range_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    assert result.status is ImpulseRangeStatus.INSUFFICIENT_WARMUP
    assert result.range_qualified is False


def test_candidate_and_prior_timestamp_inconsistency_fails_closed() -> None:
    bars = _bars()
    bars[20] = replace(bars[20], timestamp_utc=bars[19].timestamp_utc)
    with pytest.raises(EmergingDirectionV2Error, match="candidate must follow"):
        evaluate_impulse_range_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    bars = _bars()
    bars[8] = replace(bars[8], timestamp_utc=bars[7].timestamp_utc)
    with pytest.raises(EmergingDirectionV2Error, match="timestamps must increase"):
        evaluate_impulse_range_v2(impulse_candidate_bar_index=20, bars_by_index=bars)


def test_range_is_independent_of_close_and_direction() -> None:
    bars = _bars()
    first = evaluate_impulse_range_v2(impulse_candidate_bar_index=20, bars_by_index=bars)
    bars[20] = replace(bars[20], close=Decimal("1.50"))
    second = evaluate_impulse_range_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    assert first == second


def test_repeatable_and_immutable_result() -> None:
    bars = _bars()
    first = evaluate_impulse_range_v2(impulse_candidate_bar_index=20, bars_by_index=bars)
    second = evaluate_impulse_range_v2(impulse_candidate_bar_index=20, bars_by_index=bars)

    assert first == second
    with pytest.raises(AttributeError):
        first.range_qualified = False
