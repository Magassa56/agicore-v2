"""Independently verify a new invented-observation bundle in another process.

The generated input is reconstructed independently of the bundle. The event
pipeline is assembled again here, using the same underlying V2 predicates; this
is not an independent reimplementation of the frozen strategy predicates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import zlib
from collections import deque
from pathlib import Path

from tools.agicore_v2_synthetic_scale_probe import generate_observations

from . import directional_impulse_v2 as impulse
from . import ema_pullback_v2_development_replay as replay
from . import regime_context_v2 as regime
from . import reversal_transition_v2 as reversal
from .synthetic_mission_storage_v2 import (
    MAX_OBSERVATIONS,
    ROWS_PER_CHUNK,
    SCHEMA,
    canonical,
    sha,
)


def recompute_events(raw: bytes) -> dict:
    """Reassemble event/context progression separately from the producer."""
    bars = replay.parse_ninjatrader_last_rows_v2(raw)
    window = deque(maxlen=impulse.IMPULSE_RANGE_LOOKBACK + 1)
    previous = None
    digest = hashlib.sha256()
    counts = {"impulses": 0, "reversals": 0, "qualified_contexts": 0, "ambiguous_contexts": 0}
    for bar in bars:
        window.append(
            (
                bar.closed_view(),
                reversal.RejectionBarV2(
                    bar.bar_index, bar.timestamp_utc, bar.close, True, bar.open, bar.high, bar.low
                ),
            )
        )
        impulse_view = {item[0].bar_index: item[0] for item in window}
        reversal_view = {item[1].bar_index: item[1] for item in window}
        detected = impulse.evaluate_directional_impulse_event_v2(
            impulse_candidate_bar_index=bar.bar_index, bars_by_index=impulse_view
        ).event
        candidate = bar.bar_index - reversal.CONFIRMATION_WINDOW_CLOSED_BARS
        reversal_event = None
        if candidate >= 0:
            reversal_event = reversal.evaluate_reversal_transition_event_v2(
                rejection_candidate_bar_index=candidate,
                closed_bar_index=bar.bar_index,
                bars_by_index=reversal_view,
            ).event
        previous = regime.advance_regime_context_v2(
            previous=previous,
            closed_bar_index=bar.bar_index,
            closed_bar_timestamp=bar.timestamp_utc,
            source_bar_closed=True,
            directional_impulse_event=detected,
            reversal_transition_event=None
            if reversal_event is None
            else reversal_event.as_regime_event(),
        )
        counts["impulses"] += detected is not None
        counts["reversals"] += reversal_event is not None
        counts["qualified_contexts"] += (
            previous.composition.status is regime.RegimeContextStatus.QUALIFIED
        )
        counts["ambiguous_contexts"] += (
            previous.composition.status is regime.RegimeContextStatus.AMBIGUOUS
        )
        digest.update(
            replay.canonical_replay_bytes_v2(
                {
                    "bar_index": bar.bar_index,
                    "impulse": detected,
                    "reversal": reversal_event,
                    "context": previous,
                }
            )
        )
    digest.update(
        replay.canonical_replay_bytes_v2({"terminal": regime.finish_regime_context_v2(previous)})
    )
    return {"observations": len(bars), "counts": counts, "events_sha256": digest.hexdigest()}


def read_regular(path: Path, limit: int) -> bytes:
    """Read one bounded regular file without following a symlink or hardlink."""
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit:
            raise ValueError("invalid evidence file")
        content = stream.read(limit + 1)
        if len(content) != info.st_size:
            raise ValueError("evidence changed during read")
        return content


def verify(bundle: Path, observations: int) -> dict:
    """Regenerate invented input, validate every chunk, and repeat the replay."""
    if type(observations) is not int or not 1 <= observations <= MAX_OBSERVATIONS:
        raise ValueError("invalid observation count")
    if bundle.is_symlink() or not bundle.is_dir():
        raise ValueError("invalid bundle directory")
    chunk_dir = bundle / "chunks"
    if chunk_dir.is_symlink() or not chunk_dir.is_dir():
        raise ValueError("invalid chunk directory")
    manifest_bytes = read_regular(bundle / "manifest.json", 1_000_000)
    manifest = json.loads(manifest_bytes)
    if canonical(manifest) != manifest_bytes or set(manifest) != {
        "schema",
        "domain",
        "observations",
        "raw_bytes",
        "raw_sha256",
        "rows_per_chunk",
        "codec",
        "zlib_runtime",
        "chunks",
    }:
        raise ValueError("invalid canonical bundle manifest")
    expected_raw = generate_observations(observations)
    rows = expected_raw.splitlines(keepends=True)
    if (
        manifest["schema"] != SCHEMA
        or manifest["domain"] != "INVENTED_GENERATOR_ONLY"
        or type(manifest["observations"]) is not int
        or manifest["observations"] != observations
        or type(manifest["raw_bytes"]) is not int
        or manifest["raw_bytes"] != len(expected_raw)
        or manifest["raw_sha256"] != sha(expected_raw)
        or type(manifest["rows_per_chunk"]) is not int
        or manifest["rows_per_chunk"] != ROWS_PER_CHUNK
        or manifest["codec"] != "ZLIB_LEVEL_9"
        or manifest["zlib_runtime"] != zlib.ZLIB_RUNTIME_VERSION
        or type(manifest["chunks"]) is not list
    ):
        raise ValueError("bundle identity mismatch")
    expected_count = (observations + ROWS_PER_CHUNK - 1) // ROWS_PER_CHUNK
    if len(manifest["chunks"]) != expected_count:
        raise ValueError("wrong chunk count")
    expected_names = {f"{i:04d}.zlib" for i in range(expected_count)}
    if set(os.listdir(chunk_dir)) != expected_names:
        raise ValueError("unexpected chunk inventory")
    for ordinal, entry in enumerate(manifest["chunks"]):
        if type(entry) is not dict or set(entry) != {
            "name",
            "first_row",
            "rows",
            "raw_bytes",
            "raw_sha256",
            "stored_bytes",
            "stored_sha256",
        }:
            raise ValueError("invalid chunk descriptor")
        start = ordinal * ROWS_PER_CHUNK
        section = rows[start : start + ROWS_PER_CHUNK]
        expected = b"".join(section)
        name = f"{ordinal:04d}.zlib"
        if (
            entry["name"] != name
            or type(entry["first_row"]) is not int
            or entry["first_row"] != start
            or type(entry["rows"]) is not int
            or entry["rows"] != len(section)
            or type(entry["raw_bytes"]) is not int
            or entry["raw_bytes"] != len(expected)
            or entry["raw_sha256"] != sha(expected)
            or type(entry["stored_bytes"]) is not int
            or not 0 < entry["stored_bytes"] <= ROWS_PER_CHUNK * 128 + 1_024
        ):
            raise ValueError("chunk identity mismatch")
        stored = read_regular(chunk_dir / name, ROWS_PER_CHUNK * 128 + 1_024)
        if len(stored) != entry["stored_bytes"] or sha(stored) != entry["stored_sha256"]:
            raise ValueError("stored chunk digest mismatch")
        decoder = zlib.decompressobj()
        decoded = decoder.decompress(stored, len(expected) + 1)
        if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail or decoded != expected:
            raise ValueError("decoded chunk differs from generated source")
    worker = json.loads(read_regular(bundle / "worker.json", 1_000_000))
    repeated = recompute_events(expected_raw)
    if (
        worker.get("schema") != "agicore:invented-storage-replay-worker:v2"
        or worker.get("domain") != "SYNTHETIC_ONLY"
        or worker.get("manifest_sha256") != sha(manifest_bytes)
        or worker.get("input_sha256") != sha(expected_raw)
        or worker.get("replay") != repeated
    ):
        raise ValueError("worker output does not match independent verification")
    receipt = {
        "schema": "agicore:invented-storage-replay-verification:v2",
        "status": "PASS",
        "observations": observations,
        "input_sha256": sha(expected_raw),
        "manifest_sha256": sha(manifest_bytes),
        "replay": repeated,
        "scope": "INDEPENDENT_BUNDLE_AND_EVENT_PIPELINE_SHARED_FROZEN_PREDICATES",
    }
    with (bundle / "verification.json").open("xb") as stream:
        stream.write(canonical(receipt))
    return receipt


def main() -> None:
    """Run the bundle verifier in a separate process."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--observations", type=int, required=True)
    args = parser.parse_args()
    verify(args.bundle, args.observations)


if __name__ == "__main__":
    main()
