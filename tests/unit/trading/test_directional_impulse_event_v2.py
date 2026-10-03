"""Synthetic four-component event assembly and causal integration tests."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal, localcontext
from itertools import product

import pytest

from agicore.trading.directional_impulse_v2 import (
    DirectionalImpulseBarV2,
    EmergingDirectionV2Error,
    ImpulseBodyWickStatus,
    ImpulseRangeStatus,
    ImpulseVolumeStatus,
    evaluate_directional_impulse_event_v2,
)
from agicore.trading.regime_context_v2 import (
    RegimeContextStatus,
    RegimeDirection,
    RegimeEvent,
    RegimeEventType,
    compose_regime_context_v2,
)

START = datetime(2026, 10, 3, 12, tzinfo=UTC)


def _bar(index: int, open_: str, high: str, low: str, close: str, volume=100):
    return DirectionalImpulseBarV2(
        index,
        START + timedelta(minutes=index),
        Decimal(open_),
        Decimal(high),
        Decimal(low),
        Decimal(close),
        True,
        volume,
        "BAR_TRADE_VOLUME",
        1,
        "Last",
    )


def _bars(direction: RegimeDirection = RegimeDirection.LONG):
    bars = {i: _bar(i, "5", "10", "0", "5") for i in range(17)}
    bars[17] = _bar(17, "5", "11", "1", "6")
    bars[18] = _bar(18, "6", "12", "2", "7")
    bars[19] = _bar(19, "7", "13", "3", "8")
    bars[20] = _bar(20, "6", "18", "3", "15", 150)
    if direction is RegimeDirection.SHORT:
        bars = {
            index: replace(
                bar,
                open=bar.open.copy_negate(),
                close=bar.close.copy_negate(),
                high=bar.low.copy_negate(),
                low=bar.high.copy_negate(),
            )
            for index, bar in bars.items()
        }
    return bars


def _evaluate(bars, t: int = 20):
    return evaluate_directional_impulse_event_v2(impulse_candidate_bar_index=t, bars_by_index=bars)


@pytest.mark.parametrize("direction", list(RegimeDirection))
def test_four_exact_thresholds_emit_typed_closed_bar_event(direction: RegimeDirection) -> None:
    bars = _bars(direction)
    with localcontext() as context:
        context.prec = 2
        result = _evaluate(bars)
    assert result.directional_impulse_event_qualified is True
    assert result.event == RegimeEvent(
        RegimeEventType.DIRECTIONAL_IMPULSE_EVENT, direction, 20, bars[20].timestamp_utc
    )
    assert result.emerging_direction.known_at_bar_index == 19
    assert result.emerging_direction.known_at_timestamp < result.event.event_timestamp
    assert result.range.reference_range == Decimal(10)
    assert result.range.candidate_range == Decimal(15)
    assert result.volume.reference_volume == Decimal(100)
    assert result.volume.candidate_volume == Decimal(150)
    assert result.body_wick.body == Decimal(9)


@pytest.mark.parametrize(
    ("direction_ok", "range_ok", "volume_ok", "body_ok"), list(product([False, True], repeat=4))
)
def test_conjunction_never_uses_score_or_or_fallback(
    direction_ok: bool, range_ok: bool, volume_ok: bool, body_ok: bool
) -> None:
    bars = _bars()
    if not direction_ok:
        bars[19] = replace(bars[19], close=bars[18].close)
    if not range_ok:
        bars[20] = replace(bars[20], high=Decimal("17.9999999999999999999999999999999999999999"))
    if not volume_ok:
        bars[20] = replace(bars[20], volume=Decimal("149.9999999999999999999999999999999999999999"))
    if not body_ok:
        bars[20] = replace(bars[20], open=Decimal(8))
    result = _evaluate(bars)
    assert result.range.range_qualified is range_ok
    assert result.volume.volume_qualified is volume_ok
    assert result.body_wick.body_wick_qualified is (body_ok and direction_ok)
    assert result.directional_impulse_event_qualified is all(
        (direction_ok, range_ok, volume_ok, body_ok)
    )


@pytest.mark.parametrize(
    ("index", "volume", "status"),
    [
        (20, None, ImpulseVolumeStatus.INVALID_CANDIDATE_VOLUME),
        (4, None, ImpulseVolumeStatus.INVALID_REFERENCE_VOLUME),
        (20, -1, ImpulseVolumeStatus.INVALID_VOLUME),
        (4, -1, ImpulseVolumeStatus.INVALID_VOLUME),
    ],
)
def test_volume_error_status_is_preserved_and_prevents_event(index, volume, status) -> None:
    bars = _bars()
    bars[index] = replace(bars[index], volume=volume)
    result = _evaluate(bars)
    assert result.event is None
    assert result.volume.status is status


def test_zero_reference_volume_cannot_be_rescued_by_other_predicates() -> None:
    bars = _bars()
    for index in range(20):
        bars[index] = replace(bars[index], volume=0)
    result = _evaluate(bars)
    assert result.volume.status is ImpulseVolumeStatus.INVALID_REFERENCE_VOLUME
    assert result.event is None


def test_zero_reference_range_cannot_be_rescued_by_other_predicates() -> None:
    bars = _bars()
    for index in range(17):
        bars[index] = _bar(index, "0", "0", "0", "0")
    result = _evaluate(bars)
    assert result.range.status is ImpulseRangeStatus.INVALID_REFERENCE_RANGE
    assert result.body_wick.body_wick_qualified is True
    assert result.volume.volume_qualified is True
    assert result.event is None


def test_unclosed_historical_bar_prevents_qualification() -> None:
    bars = _bars()
    bars[4] = replace(bars[4], is_closed=False)
    result = _evaluate(bars)
    assert result.range.status is ImpulseRangeStatus.INSUFFICIENT_WARMUP
    assert result.volume.status is ImpulseVolumeStatus.INSUFFICIENT_WARMUP
    assert result.event is None
    bars = _bars()
    bars[19] = replace(bars[19], is_closed=False)
    with pytest.raises(EmergingDirectionV2Error, match="pre-impulse bars must be closed"):
        _evaluate(bars)


def test_invalid_candidate_ohlc_stops_with_explicit_body_status() -> None:
    bars = _bars()
    bars[20] = replace(bars[20], open=Decimal(19))
    result = _evaluate(bars)
    assert result.body_wick.status is ImpulseBodyWickStatus.INVALID_OHLC
    assert result.event is None
    assert result.range is None and result.volume is None


def test_zero_candidate_range_stops_with_explicit_body_status() -> None:
    bars = _bars()
    bars[20] = replace(bars[20], open=Decimal(4), close=Decimal(4), high=Decimal(4), low=Decimal(4))
    result = _evaluate(bars)
    assert result.body_wick.status is ImpulseBodyWickStatus.INVALID_CANDIDATE_RANGE
    assert result.event is None


@pytest.mark.parametrize("missing", [0, 17, 19])
def test_missing_prior_bar_cannot_emit_event(missing: int) -> None:
    bars = _bars()
    del bars[missing]
    result = _evaluate(bars)
    assert result.range.status is ImpulseRangeStatus.INSUFFICIENT_WARMUP
    assert result.volume.status is ImpulseVolumeStatus.INSUFFICIENT_WARMUP
    assert result.event is None


def test_nineteen_prior_closed_bars_remain_insufficient() -> None:
    bars = {i - 1: replace(bar, bar_index=i - 1) for i, bar in _bars().items() if i > 0}
    result = _evaluate(bars, 19)
    assert result.range.status is ImpulseRangeStatus.INSUFFICIENT_WARMUP
    assert result.volume.status is ImpulseVolumeStatus.INSUFFICIENT_WARMUP
    assert result.event is None


def test_only_t_and_prior_twenty_are_read_even_with_poisoned_outside_bars() -> None:
    class BoundedBars(dict):
        def __contains__(self, index):
            assert 30 <= index <= 50
            return super().__contains__(index)

        def __getitem__(self, index):
            assert 30 <= index <= 50
            return super().__getitem__(index)

    bars = BoundedBars({i + 30: replace(bar, bar_index=i + 30) for i, bar in _bars().items()})
    bars[29] = object()
    bars[51] = object()
    before = _evaluate(bars, 50)
    bars[29] = None
    bars[51] = None
    assert _evaluate(bars, 50) == before
    assert before.event.event_bar_index == 50


def test_candidate_mutation_cannot_change_prior_direction_or_references() -> None:
    bars = _bars()
    before = _evaluate(bars)
    bars[20] = replace(bars[20], open=Decimal(8), volume=149)
    after = _evaluate(bars)
    assert before.event is not None and after.event is None
    assert before.emerging_direction == after.emerging_direction
    assert before.range.reference_range == after.range.reference_range
    assert before.volume.reference_volume == after.volume.reference_volume


def test_no_prior_high_breakout_rule_is_introduced() -> None:
    bars = _bars()
    bars[20] = _bar(20, "-7", "5", "-10", "2", 150)
    assert bars[20].close < bars[19].close
    assert _evaluate(bars).event is not None


def test_closed_timestamp_and_index_guards_remain_fail_closed() -> None:
    bars = _bars()
    bars[20] = replace(bars[20], is_closed=False)
    with pytest.raises(EmergingDirectionV2Error, match="must be closed"):
        _evaluate(bars)
    bars = _bars()
    bars[20] = replace(bars[20], timestamp_utc=bars[19].timestamp_utc)
    with pytest.raises(EmergingDirectionV2Error, match="candidate must follow"):
        _evaluate(bars)
    bars = _bars()
    bars[4] = replace(bars[4], bar_index=5)
    with pytest.raises(EmergingDirectionV2Error, match="index is inconsistent"):
        _evaluate(bars)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("volume_measure", "TICK_COUNT"),
        ("data_type", "Bid"),
        ("data_type", "Ask"),
        ("interval_minutes", 2),
    ],
)
def test_canonical_source_refuses_volume_substitutes(field: str, value) -> None:
    with pytest.raises(EmergingDirectionV2Error):
        replace(_bars()[20], **{field: value})


def test_event_integrates_with_existing_distinct_family_composition() -> None:
    impulse = _evaluate(_bars()).event

    def compose(reversal):
        return compose_regime_context_v2(
            closed_bar_index=20,
            closed_bar_timestamp=impulse.event_timestamp,
            source_bar_closed=True,
            directional_impulse_event=impulse,
            reversal_transition_event=reversal,
        )

    assert compose(None).status is RegimeContextStatus.QUALIFIED
    same = RegimeEvent(
        RegimeEventType.REVERSAL_TRANSITION_EVENT, RegimeDirection.LONG, 20, impulse.event_timestamp
    )
    assert len(compose(same).events) == 2
    opposite = replace(same, event_direction=RegimeDirection.SHORT)
    assert compose(opposite).status is RegimeContextStatus.AMBIGUOUS
    assert compose(opposite).regime_context_qualified is False


def test_evaluation_and_event_are_repeatable_and_immutable() -> None:
    result = _evaluate(_bars())
    assert result == _evaluate(_bars())
    with pytest.raises(AttributeError):
        result.event = None
    with pytest.raises(AttributeError):
        result.event.event_direction = RegimeDirection.SHORT
