"""Milestone A: exact equality to immutable prefix evaluators, invented data only."""

from dataclasses import replace
from datetime import timedelta
from decimal import Decimal
from fractions import Fraction
from math import gcd

import pytest

from agicore.trading import ema20_pullback_v2 as ema
from agicore.trading import ema_pullback_entry_confirmation_v2 as macd
from agicore.trading.ema_pullback_v2_recovery_indicators import (
    ExactIncrementalIndicatorsV1,
    _FractionLane,
    _reduced,
)
from tests.unit.trading.v2_recovery_indicator_oracle import exact_indicator_polynomial_oracle
from tests.unit.trading.v2_recovery_synthetic_fixtures import (
    FAMILIES,
    ORACLE_CHECKPOINTS,
    benchmark_bars,
)


def _view(b):
    return ema.EMA20PullbackBarV2(b.bar_index, b.timestamp_utc, b.open, b.high,
                               b.low, b.close, True)


@pytest.mark.parametrize("family", FAMILIES)
def test_tick_lane_exact_prefix_records_and_previous_reference(family):
    stream = ExactIncrementalIndicatorsV1()
    bars = {}
    for i, b in enumerate(benchmark_bars(family, 1000)):
        bars[i] = _view(b)
        stream.append_closed_bar(bars[i])
        if i in ORACLE_CHECKPOINTS:
            assert stream.ema20() == ema.evaluate_ema20_v2(
                through_bar_index=i, bars_by_index=bars)
            assert stream.macd() == macd.evaluate_macd_v2(
                through_bar_index=i, bars_by_index=bars, at_timestamp=b.timestamp_utc)
            if i:
                assert stream.ema20(previous=True, before_timestamp=b.timestamp_utc) == (
                    ema.evaluate_ema20_v2(through_bar_index=i - 1, bars_by_index=bars,
                                         before_timestamp=b.timestamp_utc))


def test_generic_fraction_lane_exact_and_mixed_representation_transition():
    stream = ExactIncrementalIndicatorsV1()
    bars = {}
    for i, b in enumerate(benchmark_bars(FAMILIES[1], 80)):
        bars[i] = replace(_view(b), close=Fraction(60001 + i, 3)) if i >= 27 else _view(b)
        stream.append_closed_bar(bars[i])
        assert stream.ema20() == ema.evaluate_ema20_v2(through_bar_index=i, bars_by_index=bars)
        assert stream.macd() == macd.evaluate_macd_v2(through_bar_index=i, bars_by_index=bars)
        if i:
            assert stream.ema20(previous=True) == ema.evaluate_ema20_v2(
                through_bar_index=i - 1, bars_by_index=bars)
    assert isinstance(stream.lane, _FractionLane)


@pytest.mark.parametrize("bad", [None, Decimal("NaN"), Decimal("Infinity"), 1.0, True])
def test_invalid_close_status_precedence_and_no_later_restart(bad):
    stream = ExactIncrementalIndicatorsV1()
    bars = {}
    for i, b in enumerate(benchmark_bars(FAMILIES[0], 40)):
        bars[i] = replace(_view(b), close=bad) if i == 7 else _view(b)
        stream.append_closed_bar(bars[i])
        assert stream.ema20() == ema.evaluate_ema20_v2(through_bar_index=i, bars_by_index=bars)
        assert stream.macd() == macd.evaluate_macd_v2(through_bar_index=i, bars_by_index=bars)
    assert stream.ema20().status is ema.EMA20StatusV2.INVALID_EMA_INPUT


def test_unclosed_missing_and_clock_inconsistent_inputs_reference_errors():
    for defect in ("unclosed", "missing", "clock"):
        stream = ExactIncrementalIndicatorsV1()
        bars = {}
        for i, b in enumerate(benchmark_bars(FAMILIES[0], 40)):
            if i == 5 and defect == "missing":
                continue
            view = _view(b)
            if i == 5 and defect == "unclosed":
                view = replace(view, is_closed=False)
            if i == 5 and defect == "clock":
                view = replace(view, timestamp_utc=bars[4].timestamp_utc)
            bars[i] = view
            stream.append_closed_bar(view)
        if defect == "clock":
            with pytest.raises(ema.EMA20PullbackV2Error,
                               match="history timestamps must be causal and increasing"):
                stream.ema20()
            with pytest.raises(macd.EntryConfirmationV2Error,
                               match="history timestamps must be causal and increasing"):
                stream.macd()
        else:
            assert stream.ema20() == ema.evaluate_ema20_v2(
                through_bar_index=39, bars_by_index=bars)
            assert stream.macd() == macd.evaluate_macd_v2(
                through_bar_index=39, bars_by_index=bars)


def test_clock_query_constraints_and_negative_prefix_match_reference():
    stream = ExactIncrementalIndicatorsV1()
    with pytest.raises(ema.EMA20PullbackV2Error):
        stream.ema20()
    for b in benchmark_bars(FAMILIES[0], 40):
        stream.append_closed_bar(_view(b))
    with pytest.raises(ema.EMA20PullbackV2Error):
        stream.ema20(before_timestamp=b.timestamp_utc)
    with pytest.raises(macd.EntryConfirmationV2Error):
        stream.macd(at_timestamp=b.timestamp_utc - timedelta(minutes=1))


def test_factored_reduction_is_exact_coprime_and_signed():
    factors = ((2, 4), (3, 70), (5, 9), (13, 4))
    d = 2 ** 4 * 3 ** 70 * 5 ** 9 * 13 ** 4
    for n in (0, d, -d, d + 1, 3 ** 39 * 5 ** 2, -(3 ** 69 * 13 ** 4)):
        result = _reduced(n, d, factors)
        assert result == Fraction(n, d)
        assert gcd(result.numerator, result.denominator) == 1


def test_one_tick_pulse_denominator_invariant_not_constant_control():
    stream = ExactIncrementalIndicatorsV1()
    for b in benchmark_bars(FAMILIES[1], 250):
        stream.append_closed_bar(_view(b))
        if b.bar_index >= 20:
            m = b.bar_index - 20
            assert stream.ema20().ema20 == 20000 + Fraction(19 ** m, 42 * 21 ** m)
            assert stream.ema20().ema20.denominator == 42 * 21 ** m


def test_indicator_path_does_not_read_any_ohlc_extreme_or_future():
    class Unavailable:
        def __eq__(self, other):
            raise AssertionError("forbidden field read")
    stream = ExactIncrementalIndicatorsV1()
    for b in benchmark_bars(FAMILIES[2], 40):
        stream.append_closed_bar(replace(_view(b), open=Unavailable(),
                                        high=Unavailable(), low=Unavailable()))
    assert stream.macd().status is macd.MACDStatusV2.EVALUATED
    assert stream.ema20().status is ema.EMA20StatusV2.EVALUATED


@pytest.mark.parametrize("family", FAMILIES)
def test_independent_polynomial_oracle_matches_frozen_seed_and_prefix(family):
    invented = tuple(benchmark_bars(family, 1000))
    bars = {b.bar_index: _view(b) for b in invented}
    for q in ORACLE_CHECKPOINTS:
        oracle = exact_indicator_polynomial_oracle(invented[:q + 1])
        expected = macd.evaluate_macd_v2(through_bar_index=q, bars_by_index=bars)
        for name in ("ema12", "ema26", "macd", "signal", "histogram",
                     "previous_macd", "previous_histogram"):
            assert oracle[name] == getattr(expected, name)
        assert oracle["ema20"] == ema.evaluate_ema20_v2(
            through_bar_index=q, bars_by_index=bars).ema20
