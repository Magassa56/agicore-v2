"""Measure invented V2 ingestion and directional-impulse evaluation only.

This probe generates its input in memory. It never loads market files, executes a
trading replay, creates orders or calculates profitability. Its results describe
only the parser and one signal-detection component, not full V2 feasibility.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import resource
import sys
import time
import zlib
from datetime import UTC, datetime, timedelta
from pathlib import Path

from agicore.trading import directional_impulse_v2 as impulse
from agicore.trading import ema_pullback_v2_development_replay as replay

MAX_OBSERVATIONS = 89_841
WINDOW_SIZE = impulse.IMPULSE_RANGE_LOOKBACK + 1
GENERATOR_VERSION = "invented-ohlcv-minute-v1"


def _quarter_ticks(ticks: int) -> str:
    return f"{ticks // 4}.{(ticks % 4) * 25:02d}"


def generate_observations(count: int) -> bytes:
    """Create bounded, reproducible invented Last/minute rows entirely in memory."""
    if type(count) is not int or not 1 <= count <= MAX_OBSERVATIONS:
        raise ValueError("observation count must be an integer from 1 to 89841")
    origin = datetime(2099, 1, 4, tzinfo=UTC)
    rows = []
    for index in range(count):
        phase = index % 64
        opened = 80_000 + (index // 64 % 1_000) * 8 + phase
        closed = opened + (12 if phase == 63 else 1)
        high = closed if phase == 63 else closed + 1
        low = opened - 1
        volume = 1_000 if phase == 63 else 100 + phase % 13
        timestamp = origin + timedelta(minutes=index + 3 * (index // 97))
        rows.append(
            f"{timestamp:%Y%m%d %H%M%S};{_quarter_ticks(opened)};"
            f"{_quarter_ticks(high)};{_quarter_ticks(low)};{_quarter_ticks(closed)};"
            f"{volume}\n".encode("ascii")
        )
    return b"".join(rows)


def evaluate_impulses(bars: tuple[replay.DevelopmentReplayBarV2, ...]) -> dict:
    """Hash every full impulse evaluation using the frozen V2 canonical serializer."""
    digest = hashlib.sha256()
    window: dict[int, impulse.DirectionalImpulseBarV2] = {}
    qualified = 0
    for index, bar in enumerate(bars):
        if bar.bar_index != index:
            raise ValueError("bars must have sequential indexes")
        window[index] = bar.closed_view()
        if index >= WINDOW_SIZE:
            del window[index - WINDOW_SIZE]
        result = impulse.evaluate_directional_impulse_event_v2(
            impulse_candidate_bar_index=index, bars_by_index=window
        )
        digest.update(replay.canonical_replay_bytes_v2(result))
        qualified += result.event is not None
    return {
        "evaluations": len(bars),
        "qualified_impulse_events": qualified,
        "evaluation_sha256": digest.hexdigest(),
        "maximum_retained_observations": min(len(bars), WINDOW_SIZE),
    }


def _peak_rss_bytes() -> int:
    """Return the Linux process high-water resident set size in bytes."""
    if sys.platform != "linux":
        raise RuntimeError("RSS measurement is supported only on Linux")
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


def run_probe(count: int) -> dict:
    """Run the selected nontrading pipeline and report timings and identities."""
    start_wall = time.perf_counter_ns()
    start_cpu = time.process_time_ns()
    raw = generate_observations(count)
    generation_end = time.perf_counter_ns()
    generation_peak = _peak_rss_bytes()
    input_hash = hashlib.sha256(raw).hexdigest()
    bars = replay.parse_ninjatrader_last_rows_v2(raw)
    parse_end = time.perf_counter_ns()
    parse_peak = _peak_rss_bytes()
    if len(bars) != count:
        raise AssertionError("parsed count differs from generated count")
    results = evaluate_impulses(bars)
    end_wall = time.perf_counter_ns()
    total_ns = end_wall - start_wall
    parse_ns = parse_end - generation_end
    evaluate_ns = end_wall - parse_end
    return {
        "schema": "agicore:synthetic-ingestion-impulse-scale-probe:v1",
        "scope": "INVENTED_INPUT_PARSER_AND_DIRECTIONAL_IMPULSE_ONLY",
        "generator": GENERATOR_VERSION,
        "observations": count,
        "input_bytes": len(raw),
        "input_sha256": input_hash,
        "output": results,
        "timing_ns": {
            "generation": generation_end - start_wall,
            "parse_and_input_hash": parse_ns,
            "impulse_and_output_hash": evaluate_ns,
            "total_wall": total_ns,
            "total_cpu": time.process_time_ns() - start_cpu,
        },
        "throughput_observations_per_second": {
            "parse_and_input_hash": count * 1_000_000_000 / parse_ns,
            "impulse_and_output_hash": count * 1_000_000_000 / evaluate_ns,
            "total": count * 1_000_000_000 / total_ns,
        },
        "peak_rss_bytes": {
            "after_generation": generation_peak,
            "after_parse": parse_peak,
            "whole_process": _peak_rss_bytes(),
        },
        "environment": {
            "python": platform.python_version(),
            "python_executable_sha256": hashlib.sha256(
                Path(sys.executable).read_bytes()
            ).hexdigest(),
            "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION,
            "platform": sys.platform,
        },
        "source_sha256": {
            "probe": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "replay_parser": hashlib.sha256(Path(replay.__file__).read_bytes()).hexdigest(),
            "directional_impulse": hashlib.sha256(Path(impulse.__file__).read_bytes()).hexdigest(),
        },
        "limitations": [
            "Observation count and OHLCV format are representative; price distribution is invented.",
            "No complete strategy, storage bundle, paper trading or financial performance is measured.",
            "The parser materializes all observations; the impulse window retains at most 21.",
        ],
    }


def main() -> None:
    """Run the in-memory probe with an optional bounded observation count."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observations", type=int, default=MAX_OBSERVATIONS)
    args = parser.parse_args()
    print(json.dumps(run_probe(args.observations), sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
