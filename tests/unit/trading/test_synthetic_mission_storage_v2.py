"""Behavioral checks for the distinct invented-observation mission bundle."""

from __future__ import annotations

import json

import pytest

from agicore.trading.ema_pullback_v2_recovery_storage import _witnesses
from agicore.trading.ema_pullback_v2_storage_format import MAX_OBSERVATIONS, StorageProofError
from agicore.trading.synthetic_mission_storage_v2 import canonical, produce, replay_events
from agicore.trading.synthetic_mission_verify_v2 import recompute_events, verify
from tools.agicore_v2_synthetic_scale_probe import generate_observations


def test_distinct_bundle_exceeds_historical_limit_without_changing_it(tmp_path):
    assert MAX_OBSERVATIONS == 200
    with pytest.raises(StorageProofError):
        _witnesses(generate_observations(201))
    first = produce(tmp_path / "first", 201)
    second = produce(tmp_path / "second", 201)
    receipt = verify(tmp_path / "first", 201)
    assert receipt["status"] == "PASS"
    assert receipt["replay"]["observations"] == 201
    assert first["replay"] == second["replay"] == receipt["replay"]
    assert (tmp_path / "first" / "manifest.json").read_bytes() == (
        tmp_path / "second" / "manifest.json"
    ).read_bytes()


def test_bounded_event_window_matches_full_history():
    raw = generate_observations(256)
    assert (
        replay_events(raw, bounded=True)
        == replay_events(raw, bounded=False)
        == recompute_events(raw)
    )


def test_progressive_replay_includes_a_confirmed_reversal():
    rows = [f"20990101 00{i:02}00;{i + 1};10;0;{i + 1};100\n" for i in range(5)]
    rows += ["20990101 000500;6;12;2;8;100\n", "20990101 000600;7;8;4;5;100\n"]
    raw = "".join(rows).encode("ascii")
    result = replay_events(raw)
    assert result["counts"]["reversals"] == 1
    assert result["counts"]["qualified_contexts"] == 1
    assert result == recompute_events(raw)


def test_multiple_chunks_verify_and_missing_chunk_fails(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 1_001)
    assert verify(bundle, 1_001)["observations"] == 1_001
    (bundle / "chunks" / "0001.zlib").unlink()
    with pytest.raises(ValueError, match="chunk inventory"):
        verify(bundle, 1_001)


def test_changed_chunk_fails_independent_verifier(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 64)
    chunk = bundle / "chunks" / "0000.zlib"
    data = chunk.read_bytes()
    chunk.write_bytes(bytes([data[0] ^ 1]) + data[1:])
    with pytest.raises(ValueError, match="stored chunk digest mismatch"):
        verify(bundle, 64)
    assert not (bundle / "verification.json").exists()


def test_forged_replay_hash_is_rejected(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 64)
    worker = json.loads((bundle / "worker.json").read_bytes())
    worker["replay"]["events_sha256"] = "0" * 64
    (bundle / "worker.json").write_bytes(canonical(worker))
    with pytest.raises(ValueError, match="worker output"):
        verify(bundle, 64)


def test_manifest_path_traversal_is_rejected(tmp_path):
    bundle = tmp_path / "bundle"
    produce(bundle, 64)
    manifest = json.loads((bundle / "manifest.json").read_bytes())
    manifest["chunks"][0]["name"] = "../outside"
    (bundle / "manifest.json").write_bytes(canonical(manifest))
    with pytest.raises(ValueError, match="chunk identity"):
        verify(bundle, 64)


@pytest.mark.parametrize("count", [0, -1, True, 89_842])
def test_invalid_mission_volume_rejected_before_writing(tmp_path, count):
    bundle = tmp_path / "bundle"
    with pytest.raises(ValueError):
        produce(bundle, count)
    assert not bundle.exists()
