"""Exercise frozen stops from real synthetic confirmations, without entries."""

from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from fractions import Fraction

import pytest

from agicore.trading.ema_pullback_entry_confirmation_v2 import EntryConfirmationStateV2
from agicore.trading.ema_pullback_initial_stop_v2 import InitialStopStatusV2, InitialStopV2Error
from agicore.trading.regime_context_v2 import RegimeDirection
from agicore.trading.synthetic_confirmation_replay_v2 import replay_confirmation_native
from agicore.trading.synthetic_stop_handoff_v2 import capture_synthetic_stop_v2
from tests.unit.trading.test_ema_pullback_v2_pending_opportunity_audit import _bars


def _raw(bars):
    return "".join(
        f"{bar.timestamp_utc:%Y%m%d %H%M%S};"
        f"{bar.open};{bar.high};{bar.low};{bar.close};{bar.volume}\n"
        for _, bar in sorted(bars.items())
    ).encode("ascii")


def _confirmation(direction=RegimeDirection.LONG):
    result = replay_confirmation_native(_raw(_bars(direction)))
    assert result.summary["stop_reason"] == "CONFIRMED_BEFORE_RISK"
    assert result.summary["processed_observations"] == 36
    assert result.native_confirmation is not None
    assert [bar.bar_index for bar in result.stop_window] == [33, 34, 35]
    return result


@pytest.mark.parametrize("direction", list(RegimeDirection))
def test_real_confirmation_yields_causal_immutable_stop_without_entry(direction):
    upstream = _confirmation(direction)
    result = capture_synthetic_stop_v2(
        confirmation=upstream.native_confirmation, closed_window=upstream.stop_window
    )
    evaluation = result.evaluation
    record = evaluation.initial_stop_record
    confirmation = upstream.native_confirmation.confirmation
    assert evaluation.status is InitialStopStatusV2.EVALUATED
    assert record is not None
    assert record.confirmation == confirmation
    assert record.source_regime_event_direction is direction
    assert (record.structural_window_first_bar, record.structural_window_last_bar) == (33, 35)
    assert record.initial_stop_price == Fraction(20000)
    assert record.stop_buffer_ticks * record.tick_size == Fraction(1, 4)
    if direction is RegimeDirection.LONG:
        assert record.structural_extreme == Fraction(20000) + Fraction(1, 4)
    else:
        assert record.structural_extreme == Fraction(20000) - Fraction(1, 4)
    assert record.stop_known_at_bar_index == confirmation.confirmation_bar_index == 35
    assert record.stop_known_at_timestamp == confirmation.confirmation_timestamp
    assert evaluation.at_entry is None
    assert evaluation.stop_state is None
    assert result.book.for_confirmation(confirmation) is evaluation

    repeated = capture_synthetic_stop_v2(
        confirmation=upstream.native_confirmation,
        closed_window=(object(), object(), object()),
        previous=result.book,
    )
    assert repeated.book is result.book
    assert repeated.evaluation is evaluation


@pytest.mark.parametrize("direction", list(RegimeDirection))
def test_future_prices_and_appended_bar_cannot_change_stop(direction):
    bars = _bars(direction)
    upstream = replay_confirmation_native(_raw(bars))
    before = capture_synthetic_stop_v2(
        confirmation=upstream.native_confirmation, closed_window=upstream.stop_window
    )
    for index in range(36, len(bars)):
        bar = bars[index]
        bars[index] = replace(
            bar, open=bar.open + 10, high=bar.high + 10, low=bar.low + 10, close=bar.close + 10
        )
    changed = replay_confirmation_native(_raw(bars))
    after = capture_synthetic_stop_v2(
        confirmation=changed.native_confirmation, closed_window=changed.stop_window
    )
    assert changed.summary["processed_observations"] == 36
    assert before.evaluation == after.evaluation
    with pytest.raises(ValueError, match="after confirmation"):
        capture_synthetic_stop_v2(
            confirmation=upstream.native_confirmation,
            closed_window=(*upstream.stop_window, object()),
        )


def test_missing_and_unclosed_window_bars_fail_closed():
    upstream = _confirmation()
    first, middle, last = upstream.stop_window
    incomplete = capture_synthetic_stop_v2(
        confirmation=upstream.native_confirmation, closed_window=(first, None, last)
    )
    assert incomplete.evaluation.status is InitialStopStatusV2.INCOMPLETE_STRUCTURAL_STOP_WINDOW
    assert incomplete.evaluation.initial_stop is None
    assert incomplete.evaluation.at_entry is None
    invalid = capture_synthetic_stop_v2(
        confirmation=upstream.native_confirmation,
        closed_window=(first, replace(middle, is_closed=False), last),
    )
    assert invalid.evaluation.status is InitialStopStatusV2.INVALID_STRUCTURAL_STOP_INPUT
    assert invalid.evaluation.initial_stop is None
    assert invalid.evaluation.at_entry is None
    repeated = capture_synthetic_stop_v2(
        confirmation=upstream.native_confirmation,
        closed_window=upstream.stop_window,
        previous=incomplete.book,
    )
    assert repeated.evaluation is incomplete.evaluation


@pytest.mark.parametrize("field", ["timestamp_utc", "bar_index"])
def test_wrong_window_metadata_is_rejected(field):
    upstream = _confirmation()
    first, middle, last = upstream.stop_window
    if field == "timestamp_utc":
        last = replace(last, timestamp_utc=last.timestamp_utc + timedelta(minutes=1))
    else:
        middle = replace(middle, bar_index=middle.bar_index + 1)
    with pytest.raises(InitialStopV2Error, match="metadata"):
        capture_synthetic_stop_v2(
            confirmation=upstream.native_confirmation, closed_window=(first, middle, last)
        )


def test_nonqualified_or_changed_source_provenance_is_rejected():
    upstream = _confirmation()
    native = upstream.native_confirmation
    pending = replace(
        native, state=EntryConfirmationStateV2.AWAITING_CONFIRMATION, confirmation=None
    )
    with pytest.raises(ValueError, match="qualified confirmation"):
        capture_synthetic_stop_v2(confirmation=pending, closed_window=())

    altered_record = replace(
        native.confirmation,
        source_regime_event_bar_index=native.confirmation.source_regime_event_bar_index + 1,
    )
    with pytest.raises(InitialStopV2Error, match="provenance"):
        capture_synthetic_stop_v2(
            confirmation=replace(native, confirmation=altered_record),
            closed_window=upstream.stop_window,
        )

    original = capture_synthetic_stop_v2(confirmation=native, closed_window=upstream.stop_window)
    altered_record = replace(native.confirmation, macd=native.confirmation.macd + 1)
    with pytest.raises(InitialStopV2Error, match="provenance"):
        capture_synthetic_stop_v2(
            confirmation=replace(native, confirmation=altered_record),
            closed_window=(),
            previous=original.book,
        )
