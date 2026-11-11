"""Checks for the bounded invented-only V2 ingestion and impulse probe."""

from __future__ import annotations

import hashlib

import pytest

from agicore.trading import directional_impulse_v2 as impulse
from agicore.trading import ema_pullback_v2_development_replay as replay
from agicore.trading.ema_pullback_v2_recovery_storage import _witnesses
from agicore.trading.ema_pullback_v2_storage_format import MAX_OBSERVATIONS, StorageProofError
from tools import agicore_v2_synthetic_scale_probe as probe


def test_generated_input_and_results_repeat_with_nontrivial_events():
    first = probe.run_probe(128)
    second = probe.run_probe(128)
    assert first["input_sha256"] == second["input_sha256"]
    assert first["output"] == second["output"]
    assert first["output"]["evaluations"] == 128
    assert first["output"]["qualified_impulse_events"] > 0
    assert first["output"]["maximum_retained_observations"] == 21
    assert set(first["address_space_limit_bytes"]) == {"soft", "hard"}
    assert first["scope"] == "INVENTED_INPUT_PARSER_AND_DIRECTIONAL_IMPULSE_ONLY"


def test_rolling_window_matches_direct_full_history_evaluations():
    bars = replay.parse_ninjatrader_last_rows_v2(probe.generate_observations(128))
    all_bars = {bar.bar_index: bar.closed_view() for bar in bars}
    expected = hashlib.sha256()
    for index in range(len(bars)):
        result = impulse.evaluate_directional_impulse_event_v2(
            impulse_candidate_bar_index=index, bars_by_index=all_bars
        )
        expected.update(replay.canonical_replay_bytes_v2(result))
    assert probe.evaluate_impulses(bars)["evaluation_sha256"] == expected.hexdigest()


@pytest.mark.parametrize("count", [0, -1, True, probe.MAX_OBSERVATIONS + 1])
def test_generator_rejects_invalid_or_excessive_counts(count):
    with pytest.raises(ValueError):
        probe.generate_observations(count)


def test_frozen_storage_witness_limit_is_not_bypassed():
    assert MAX_OBSERVATIONS == 200
    raw = probe.generate_observations(201)
    with pytest.raises(StorageProofError, match="bounded complete invented rows"):
        _witnesses(raw)
