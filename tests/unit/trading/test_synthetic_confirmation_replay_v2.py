"""Real synthetic V2 confirmation events, causal boundaries and verification."""

from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from decimal import Decimal
from fractions import Fraction

import pytest

from agicore.trading import synthetic_confirmation_replay_v2 as engine
from agicore.trading import synthetic_mission_storage_v2 as producer
from agicore.trading import synthetic_mission_verify_v2 as verifier
from agicore.trading.ema_pullback_entry_confirmation_v2 import EntryConfirmationStateV2
from agicore.trading.regime_context_v2 import RegimeDirection
from tests.unit.trading.test_ema_pullback_v2_pending_opportunity_audit import _bars


def _raw(bars):
    return "".join(
        f"{b.timestamp_utc:%Y%m%d %H%M%S};{b.open};{b.high};{b.low};{b.close};{b.volume}\n"
        for _, b in sorted(bars.items())
    ).encode("ascii")


@pytest.mark.parametrize("direction", list(RegimeDirection))
def test_real_confirmation_stops_before_risk_and_retains_native_provenance(direction):
    raw = _raw(_bars(direction))
    result = engine.replay_confirmation_native(raw)
    assert result.summary == verifier.recompute_confirmation_events(raw)
    assert result.summary["input_observations"] == 39
    assert result.summary["processed_observations"] == 36
    assert result.summary["stop_reason"] == "CONFIRMED_BEFORE_RISK"
    assert result.summary["counts"]["confirmations_qualified"] == 1
    assert result.summary["counts"]["events_suppressed_while_pending"] == 1
    assert result.native_confirmation.state is EntryConfirmationStateV2.CONFIRMED
    assert result.native_confirmation.confirmation.source_regime_event_direction is direction
    assert [bar.bar_index for bar in result.stop_window] == [33, 34, 35]


@pytest.mark.parametrize("direction", list(RegimeDirection))
def test_two_failed_candidates_expire_and_do_not_forge_confirmation(direction):
    bars = _bars(direction)
    for index in (34, 35):
        bars[index] = replace(bars[index], close=bars[index].open)
    raw = _raw(bars)
    result = engine.replay_confirmation_native(raw)
    assert result.summary == verifier.recompute_confirmation_events(raw)
    assert result.summary["processed_observations"] == 39
    assert result.summary["stop_reason"] == "END_OF_INPUT"
    assert result.summary["counts"]["confirmation_candidates"] == 2
    assert result.summary["counts"]["confirmations_expired"] == 1
    assert result.summary["counts"]["confirmations_qualified"] == 0
    assert result.native_confirmation is None and result.stop_window == ()


def test_confirmation_expiry_uses_real_elapsed_time_not_fabricated_bars():
    bars = _bars(RegimeDirection.LONG)
    for i in range(34, len(bars)):
        bars[i] = replace(bars[i], timestamp_utc=bars[i].timestamp_utc + timedelta(minutes=3))
    raw = _raw({i: bars[i] for i in range(35)})
    result = engine.replay_confirmation_native(raw)
    assert result.summary == verifier.recompute_confirmation_events(raw)
    assert result.summary["counts"]["confirmations_expired"] == 1
    assert result.summary["counts"]["confirmations_qualified"] == 0


def test_end_of_input_preserves_pending_state_without_fabricating_confirmation():
    bars = _bars(RegimeDirection.LONG)
    raw = _raw({i: bars[i] for i in range(34)})
    result = engine.replay_confirmation_native(raw)
    assert result.summary == verifier.recompute_confirmation_events(raw)
    assert result.summary["stop_reason"] == "END_OF_INPUT_AWAITING_CONFIRMATION"
    assert result.summary["processed_observations"] == 34
    assert result.summary["counts"]["opportunities_started"] == 1
    assert result.native_confirmation is None


@pytest.mark.parametrize("direction", list(RegimeDirection))
def test_future_prices_cannot_change_the_first_confirmation(direction):
    bars = _bars(direction)
    baseline = engine.replay_confirmation_native(_raw(bars)).summary
    prefix = engine.replay_confirmation_native(_raw({i: bars[i] for i in range(36)})).summary
    for i in range(36, len(bars)):
        b = bars[i]
        bars[i] = replace(b, open=b.open + 10, high=b.high + 10, low=b.low + 10, close=b.close + 10)
    changed_raw = _raw(bars)
    changed = engine.replay_confirmation_native(changed_raw).summary
    assert changed == verifier.recompute_confirmation_events(changed_raw)
    assert baseline["events_sha256"] == prefix["events_sha256"] == changed["events_sha256"]
    assert baseline["counts"] == prefix["counts"] == changed["counts"]
    assert baseline["processed_observations"] == prefix["processed_observations"] == 36


def test_confirmation_timestamp_changes_projection_and_replay_fingerprint():
    bars = _bars(RegimeDirection.LONG)
    bars[34] = replace(bars[34], high=Decimal("20006.25"), close=Decimal("20006.00"))
    original_raw = _raw(bars)
    original = engine.replay_confirmation_native(original_raw)
    delayed = {
        i: replace(b, timestamp_utc=b.timestamp_utc + timedelta(minutes=1)) if i >= 34 else b
        for i, b in bars.items()
    }
    delayed_raw = _raw(delayed)
    after = engine.replay_confirmation_native(delayed_raw)
    assert original.native_confirmation.confirmation.confirmation_bar_index == 34
    assert after.native_confirmation.confirmation.confirmation_bar_index == 34
    assert (
        original.native_confirmation.confirmation.confirmation_timestamp
        != after.native_confirmation.confirmation.confirmation_timestamp
    )
    assert original.summary["events_sha256"] != after.summary["events_sha256"]
    assert original.summary == verifier.recompute_confirmation_events(original_raw)
    assert after.summary == verifier.recompute_confirmation_events(delayed_raw)
    assert original.summary["schema"] == "agicore:synthetic-event-confirmation-replay:v2"


def test_confirmation_projection_binds_context_and_exact_pullback_body():
    result = engine.replay_confirmation_native(_raw(_bars(RegimeDirection.LONG)))
    value = result.native_confirmation
    snapshot = engine.confirmation_snapshot(value)
    context = value.opportunity.consumed_context
    assert snapshot["source_event_types"] == [x.value for x in context.source_event_types]
    assert snapshot["source_event_timestamp"] == context.source_event_timestamp
    assert snapshot["pullback_timestamp"] == context.pullback_timestamp
    assert snapshot["candidate"]["timestamp"] == value.candidate.confirmation_timestamp
    assert snapshot["confirmation_timestamp"] == value.confirmation.confirmation_timestamp
    changed = replace(
        value,
        opportunity=replace(
            value.opportunity,
            pullback_body_low=value.opportunity.pullback_body_low - Fraction(1, 4),
            pullback_body_high=value.opportunity.pullback_body_high + Fraction(1, 4),
        ),
    )
    altered = engine.confirmation_snapshot(changed)
    assert snapshot["pullback_body_low_sha256"] != altered["pullback_body_low_sha256"]
    assert snapshot["pullback_body_high_sha256"] != altered["pullback_body_high_sha256"]


def test_prefix_mapping_refuses_future_reads_and_history_scans():
    history = {0: object(), 1: object()}
    guarded = engine.ClosedPrefix(history, 0)
    assert guarded[0] is history[0]
    with pytest.raises(ValueError, match="future"):
        guarded[1]
    with pytest.raises(TypeError):
        list(guarded)
    with pytest.raises(TypeError):
        len(guarded)


@pytest.mark.parametrize("direction", list(RegimeDirection))
def test_synthetic_bundle_uses_independent_confirmation_verifier(tmp_path, monkeypatch, direction):
    raw = _raw(_bars(direction))
    monkeypatch.setattr(producer, "generate_observations", lambda count: raw)
    monkeypatch.setattr(verifier, "generate_observations", lambda count: raw)
    bundle = tmp_path / "bundle"
    worker = producer.produce(bundle, 39, stage="confirmation")
    monkeypatch.setattr(
        engine, "replay_confirmation_native", lambda raw: pytest.fail("producer reused")
    )
    receipt = verifier.verify(bundle, 39, stage="confirmation")
    assert receipt["status"] == "PASS"
    assert receipt["replay"] == worker["replay"]
    assert receipt["replay"]["stop_reason"] == "CONFIRMED_BEFORE_RISK"
