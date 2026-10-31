"""Invented-only observation bundles and a nonfinancial V2 replay stage.

This format has its own identity. It does not change, extend, or certify the
historical 200-witness native-result bundle. It cannot accept external data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import resource
import time
import zlib
from pathlib import Path

from tools.agicore_v2_synthetic_scale_probe import generate_observations

from . import directional_impulse_v2 as impulse
from . import ema_pullback_v2_development_replay as replay
from . import regime_context_v2 as regime
from . import reversal_transition_v2 as reversal

SCHEMA = "agicore:invented-observation-bundle:v2"
MAX_OBSERVATIONS = 89_841
ROWS_PER_CHUNK = 1_000
WINDOW_SIZE = impulse.IMPULSE_RANGE_LOOKBACK + 1


def canonical(value: object) -> bytes:
    """Encode this new bundle's JSON deterministically."""
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode()


def sha(raw: bytes) -> str:
    """Return the SHA-256 digest of bytes."""
    return hashlib.sha256(raw).hexdigest()


def replay_events(raw: bytes, *, bounded: bool = True) -> dict:
    """Replay event and context stages only; do not evaluate entries or PnL.

    Reversal and impulse use the existing V2 predicates. Context lifetime is
    advanced without a pullback callback; this is not a complete strategy replay.
    """
    bars = replay.parse_ninjatrader_last_rows_v2(raw)
    windows = {}
    rejection = {}
    previous = None
    digest = hashlib.sha256()
    counts = {"impulses": 0, "reversals": 0, "qualified_contexts": 0, "ambiguous_contexts": 0}
    for bar in bars:
        i = bar.bar_index
        view = bar.closed_view()
        windows[i] = view
        rejection[i] = reversal.RejectionBarV2(
            i, bar.timestamp_utc, bar.close, True, bar.open, bar.high, bar.low
        )
        if bounded and i >= WINDOW_SIZE:
            del windows[i - WINDOW_SIZE]
            del rejection[i - WINDOW_SIZE]
        detected = impulse.evaluate_directional_impulse_event_v2(
            impulse_candidate_bar_index=i, bars_by_index=windows
        )
        reversal_result = None
        if i >= reversal.CONFIRMATION_WINDOW_CLOSED_BARS:
            reversal_result = reversal.evaluate_reversal_transition_event_v2(
                rejection_candidate_bar_index=i - reversal.CONFIRMATION_WINDOW_CLOSED_BARS,
                closed_bar_index=i,
                bars_by_index=rejection,
            )
        reversal_event = None if reversal_result is None else reversal_result.event
        previous = regime.advance_regime_context_v2(
            previous=previous,
            closed_bar_index=i,
            closed_bar_timestamp=bar.timestamp_utc,
            source_bar_closed=True,
            directional_impulse_event=detected.event,
            reversal_transition_event=None
            if reversal_event is None
            else reversal_event.as_regime_event(),
        )
        counts["impulses"] += detected.event is not None
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
                    "bar_index": i,
                    "impulse": detected.event,
                    "reversal": reversal_event,
                    "context": previous,
                }
            )
        )
    terminal = regime.finish_regime_context_v2(previous)
    digest.update(replay.canonical_replay_bytes_v2({"terminal": terminal}))
    return {"observations": len(bars), "counts": counts, "events_sha256": digest.hexdigest()}


def produce(bundle: Path, observations: int) -> dict:
    """Write one new synthetic bundle, then replay its event/context stages."""
    if type(observations) is not int or not 1 <= observations <= MAX_OBSERVATIONS:
        raise ValueError("observation count outside invented mission bounds")
    start = time.perf_counter_ns()
    raw = generate_observations(observations)
    if sha(raw) == replay.CANONICAL_DATASET_RAW_SHA256:
        raise ValueError("canonical market identity is not a synthetic input")
    lines = raw.splitlines(keepends=True)
    if len(lines) != observations or any(
        not line.endswith(b"\n") or len(line) > 128 for line in lines
    ):
        raise ValueError("invented generator produced invalid rows")
    bundle.mkdir(mode=0o700, exist_ok=False)
    chunk_dir = bundle / "chunks"
    chunk_dir.mkdir(mode=0o700)
    chunks = []
    for start_row in range(0, observations, ROWS_PER_CHUNK):
        section = lines[start_row : start_row + ROWS_PER_CHUNK]
        decoded = b"".join(section)
        encoded = zlib.compress(decoded, level=9)
        name = f"{len(chunks):04d}.zlib"
        with (chunk_dir / name).open("xb") as stream:
            stream.write(encoded)
        chunks.append(
            {
                "name": name,
                "first_row": start_row,
                "rows": len(section),
                "raw_bytes": len(decoded),
                "raw_sha256": sha(decoded),
                "stored_bytes": len(encoded),
                "stored_sha256": sha(encoded),
            }
        )
    manifest = {
        "schema": SCHEMA,
        "domain": "INVENTED_GENERATOR_ONLY",
        "observations": observations,
        "raw_bytes": len(raw),
        "raw_sha256": sha(raw),
        "rows_per_chunk": ROWS_PER_CHUNK,
        "codec": "ZLIB_LEVEL_9",
        "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION,
        "chunks": chunks,
    }
    manifest_bytes = canonical(manifest)
    with (bundle / "manifest.json").open("xb") as stream:
        stream.write(manifest_bytes)
    storage_end = time.perf_counter_ns()
    stage = replay_events(raw)
    result = {
        "schema": "agicore:invented-storage-replay-worker:v2",
        "domain": "SYNTHETIC_ONLY",
        "manifest_sha256": sha(manifest_bytes),
        "input_sha256": sha(raw),
        "replay": stage,
        "storage_wall_ns": storage_end - start,
        "replay_wall_ns": time.perf_counter_ns() - storage_end,
        "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
    }
    with (bundle / "worker.json").open("xb") as stream:
        stream.write(canonical(result))
    return result


def main() -> None:
    """Run the fixed invented-input producer in a separate process."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--observations", type=int, required=True)
    args = parser.parse_args()
    produce(args.bundle, args.observations)


if __name__ == "__main__":
    main()
