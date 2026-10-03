"""Synthetic exact-body/wick tests; no market dataset or performance replay."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal, localcontext

import pytest

from agicore.trading.directional_impulse_v2 import (
    MAX_TERMINAL_WICK_TO_RANGE_RATIO,
    MIN_BODY_TO_RANGE_RATIO,
    BodyWickBarV2,
    EmergingDirectionV2Error,
    ImpulseBodyWickStatus,
    evaluate_impulse_body_wick_v2,
)
from agicore.trading.regime_context_v2 import RegimeDirection

STAMP = datetime(2026, 10, 3, 12, tzinfo=UTC)


def _bar(open_: str = "2", close: str = "8", high: str = "10", low: str = "0") -> BodyWickBarV2:
    return BodyWickBarV2(
        20, STAMP, Decimal(open_), Decimal(high), Decimal(low), Decimal(close), True
    )


def _mirror(bar: BodyWickBarV2) -> BodyWickBarV2:
    return replace(
        bar,
        open=bar.open.copy_negate(),
        close=bar.close.copy_negate(),
        high=bar.low.copy_negate(),
        low=bar.high.copy_negate(),
    )


def _evaluate(bar: BodyWickBarV2, direction: RegimeDirection | None = RegimeDirection.LONG):
    return evaluate_impulse_body_wick_v2(
        impulse_candidate_bar_index=20, bars_by_index={20: bar}, emerging_direction=direction
    )


@pytest.mark.parametrize("direction", list(RegimeDirection))
@pytest.mark.parametrize(
    ("open_", "close", "expected"),
    [
        ("2", "8", True),  # exact 60% body and 20% terminal wick
        ("1", "8", True),  # exact 20% terminal wick, larger body
        ("2", "7.9999999999999999999999999999999999999999", False),
        ("2", "8.0000000000000000000000000000000000000001", True),
        ("1", "7.9999999999999999999999999999999999999999", False),  # wick only
        ("1", "8.0000000000000000000000000000000000000001", True),
        ("0", "7", False),  # large terminal wick with a strong body
        ("8", "2", False),  # candle against emerging direction
        ("5", "5", False),  # doji
        ("0", "10", True),  # no wicks
        ("4", "10", True),  # nonterminal wick 40%, no independent bound
    ],
)
def test_inclusive_exact_thresholds_and_directional_frontiers(
    direction: RegimeDirection, open_: str, close: str, expected: bool
) -> None:
    bar = _bar(open_, close)
    if direction is RegimeDirection.SHORT:
        bar = _mirror(bar)
    with localcontext() as context:
        context.prec = 2
        result = _evaluate(bar, direction)
    assert MIN_BODY_TO_RANGE_RATIO == Decimal("0.60")
    assert MAX_TERMINAL_WICK_TO_RANGE_RATIO == Decimal("0.20")
    assert result.status is ImpulseBodyWickStatus.EVALUATED
    assert result.body_wick_qualified is expected
    assert result.emerging_direction is direction
    assert result.candidate_range == Decimal(10)


@pytest.mark.parametrize("direction", list(RegimeDirection))
def test_exact_geometry(direction: RegimeDirection) -> None:
    bar = _bar("3", "9", "10", "0")
    result = _evaluate(bar if direction is RegimeDirection.LONG else _mirror(bar), direction)
    assert result.body == Decimal(6)
    assert result.candidate_range == Decimal(10)
    assert result.upper_wick == Decimal(1 if direction is RegimeDirection.LONG else 3)
    assert result.lower_wick == Decimal(3 if direction is RegimeDirection.LONG else 1)
    assert result.body_wick_qualified is True


def test_no_emerging_direction_cannot_qualify() -> None:
    result = _evaluate(_bar(), None)
    assert result.status is ImpulseBodyWickStatus.EVALUATED
    assert result.body_wick_qualified is False


def test_zero_range_is_invalid_candidate_range() -> None:
    result = _evaluate(_bar("4", "4", "4", "4"))
    assert result.status is ImpulseBodyWickStatus.INVALID_CANDIDATE_RANGE
    assert result.body_wick_qualified is False
    assert result.candidate_range == result.body == result.upper_wick == result.lower_wick == 0


@pytest.mark.parametrize(
    "bar",
    [
        _bar(high="7"),  # high below close
        _bar(low="3"),  # low above open
        _bar(open_="-1"),  # open below low
        _bar(open_="11"),  # open above high
        _bar("4", "4", "3", "5"),  # high below low
        replace(_bar(), open=Decimal("NaN")),
        replace(_bar(), close=Decimal("sNaN")),
        replace(_bar(), high=Decimal("Infinity")),
        replace(_bar(), low=Decimal("-Infinity")),
        replace(_bar(), open=None),
        replace(_bar(), close=8.0),
    ],
)
def test_malformed_ohlc_fails_closed_with_required_status(bar: BodyWickBarV2) -> None:
    result = _evaluate(bar)
    assert result.status is ImpulseBodyWickStatus.INVALID_OHLC
    assert result.body_wick_qualified is False
    assert result.body is None


def test_only_candidate_is_read_and_future_mutation_has_no_effect() -> None:
    class CandidateOnly(dict):
        def __contains__(self, index):
            assert index == 20
            return super().__contains__(index)

        def __getitem__(self, index):
            assert index == 20
            return super().__getitem__(index)

    bars = CandidateOnly({20: _bar(), 19: object(), 21: object()})
    args = {
        "impulse_candidate_bar_index": 20,
        "bars_by_index": bars,
        "emerging_direction": RegimeDirection.LONG,
    }
    before = evaluate_impulse_body_wick_v2(**args)
    bars[19] = None
    bars[21] = None
    assert evaluate_impulse_body_wick_v2(**args) == before


@pytest.mark.parametrize(
    ("open_", "close"), [("2", "8"), ("4", "10"), ("0", "7"), ("8", "2"), ("5", "5")]
)
def test_long_short_mirror_symmetry(open_: str, close: str) -> None:
    long_result = _evaluate(_bar(open_, close), RegimeDirection.LONG)
    short_result = _evaluate(_mirror(_bar(open_, close)), RegimeDirection.SHORT)
    assert long_result.body_wick_qualified == short_result.body_wick_qualified
    assert long_result.status is short_result.status
    assert long_result.body == short_result.body
    assert long_result.candidate_range == short_result.candidate_range
    assert long_result.upper_wick == short_result.lower_wick
    assert long_result.lower_wick == short_result.upper_wick


def test_missing_open_candidate_or_inconsistent_index_is_rejected() -> None:
    args = {"impulse_candidate_bar_index": 20, "emerging_direction": RegimeDirection.LONG}
    with pytest.raises(EmergingDirectionV2Error, match="closed candidate bar is required"):
        evaluate_impulse_body_wick_v2(**args, bars_by_index={})
    with pytest.raises(EmergingDirectionV2Error, match="candidate bar must be closed"):
        _evaluate(replace(_bar(), is_closed=False))
    with pytest.raises(EmergingDirectionV2Error, match="candidate bar index is inconsistent"):
        _evaluate(replace(_bar(), bar_index=21))


def test_invalid_direction_cannot_be_inferred_from_body() -> None:
    with pytest.raises(EmergingDirectionV2Error, match="emerging_direction"):
        _evaluate(_bar(), "LONG")


def test_result_is_repeatable_and_immutable() -> None:
    result = _evaluate(_bar())
    assert result == _evaluate(_bar())
    with pytest.raises(AttributeError):
        result.body_wick_qualified = False
