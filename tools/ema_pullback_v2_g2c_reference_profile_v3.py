"""Offline instrumentation of the registered small invented dense prefixes."""
from __future__ import annotations

import argparse
import cProfile
import hashlib
import json
import pstats
import resource
import time
import tracemalloc
from collections import Counter
from pathlib import Path

from agicore.trading import ema20_pullback_v2 as ema
from agicore.trading import ema_pullback_entry_confirmation_v2 as macd
from agicore.trading import ema_pullback_exit_policy_v2 as exits
from agicore.trading import ema_pullback_v2_development_replay as reference
from agicore.trading import ema_pullback_v2_g2c_scaling as scaling
from tests.integration.test_ema_pullback_v2_g2c_parity_v2 import FIXTURES
from tests.unit.trading.v2_recovery_synthetic_fixtures import dense_lifecycle_resource_bars_v2
from tools import ema_pullback_v2_g2c_parity_v2 as v2


def source(count):
    if count not in (201, 401, 601):
        raise ValueError("small invented prefixes only")
    raw = b"".join(scaling._bar_row(bar) for bar in dense_lifecycle_resource_bars_v2(count))
    if hashlib.sha256(raw).hexdigest() != FIXTURES[count][0]:
        raise ValueError("unexpected synthetic fixture")
    return raw


def instrumented(raw):
    integers = Counter()
    buckets = Counter()
    stats = {"integer_output_characters": 0}
    original_integer = reference._integer_text

    def integer(value):
        result = original_integer(value)
        digits = len(result.lstrip("-"))
        bucket = ("1-3" if digits <= 3 else "4-9" if digits <= 9 else
                  "10-99" if digits <= 99 else "100-999" if digits <= 999 else "1000+")
        buckets[bucket] += 1
        integers[value] += 1
        stats["integer_output_characters"] += len(result)
        stats["largest_decimal_digits"] = max(stats.get("largest_decimal_digits", 0), digits)
        return result

    reference._integer_text = integer
    indicators = {"EMA20": [], "MACD": []}
    raw_prefixes = []
    original_raw = reference.assembly._raw_regime_decision

    def raw_decision(bars, index, *, end_of_data=False):
        raw_prefixes.append({"bars": len(bars), "end_of_data": end_of_data})
        return original_raw(bars, index, end_of_data=end_of_data)

    reference.assembly._raw_regime_decision = raw_decision

    def indicator(original, name):
        def measured(**kwargs):
            started = time.process_time_ns()
            try:
                return original(**kwargs)
            finally:
                indicators[name].append({
                    "through": kwargs["through_bar_index"],
                    "mapping_size": len(kwargs["bars_by_index"]),
                    "clock_bound": str(kwargs.get("before_timestamp", kwargs.get("at_timestamp"))),
                    "elapsed_cpu_ns_inclusive": time.process_time_ns() - started,
                })
        return measured

    ema_wrapped = indicator(ema.evaluate_ema20_v2, "EMA20")
    ema.evaluate_ema20_v2 = ema_wrapped
    exits.evaluate_ema20_v2 = ema_wrapped
    macd.evaluate_macd_v2 = indicator(macd.evaluate_macd_v2, "MACD")

    bindings = reference.read_frozen_replay_bindings_v2()
    fn = v2._cached_reference()
    profile = cProfile.Profile(timer=time.process_time)
    started = time.process_time_ns()
    output = profile.runcall(fn, raw, bindings=bindings)
    cpu = time.process_time_ns() - started
    rows = []
    keep = {"_integer_text", "_raw_regime_decision", "evaluate_ema20_v2", "evaluate_macd_v2"}
    for (filename, line, name), (_, calls, own, cumulative, _) in pstats.Stats(profile).stats.items():
        if name in keep and "/agicore/trading/" in filename:
            rows.append({"file": Path(filename).name, "line": line, "function": name, "calls": calls,
                         "own_cpu_s": own, "cumulative_cpu_s": cumulative})
    computed = {}
    for name, samples in indicators.items():
        selectors = Counter((x["through"], x["mapping_size"], x["clock_bound"]) for x in samples)
        computed[name] = {
            "calls": len(samples),
            "sum_requested_prefix_lengths": sum(x["through"] + 1 for x in samples),
            "min_requested_prefix_length": min((x["through"] + 1 for x in samples), default=0),
            "max_requested_prefix_length": max((x["through"] + 1 for x in samples), default=0),
            "repeated_same_selector_calls": sum(count - 1 for count in selectors.values()),
            "total_inclusive_cpu_ns_instrumented": sum(x["elapsed_cpu_ns_inclusive"] for x in samples),
            "selectors": samples,
        }
    values = list(integers.values())
    stats.update({"calls": sum(values), "distinct_values": len(values),
                  "calls_after_first_equal_value": sum(x - 1 for x in values),
                  "max_occurrences_of_one_value": max(values, default=0),
                  "decimal_digit_buckets": dict(buckets)})
    return {
        "profiled_process_cpu_ns": cpu,
        "reference_sha256": hashlib.sha256(output.canonical_utf8).hexdigest(),
        "reference_bytes": len(output.canonical_utf8),
        "integers": stats,
        "raw_regime": {"calls": len(raw_prefixes),
                       "constructed_rejection_views": sum(x["bars"] for x in raw_prefixes),
                       "finalization_calls": sum(x["end_of_data"] for x in raw_prefixes),
                       "minimum_prefix": min(x["bars"] for x in raw_prefixes),
                       "maximum_prefix": max(x["bars"] for x in raw_prefixes)},
        "indicators": computed,
        "cprofile": rows,
    }


def allocations(raw):
    bindings = reference.read_frozen_replay_bindings_v2()
    fn = v2._cached_reference()
    tracemalloc.start(8)
    before = tracemalloc.take_snapshot()
    started = time.process_time_ns()
    output = fn(raw, bindings=bindings)
    elapsed = time.process_time_ns() - started
    current, peak = tracemalloc.get_traced_memory()
    after = tracemalloc.take_snapshot()
    retained = []
    for item in after.compare_to(before, "lineno"):
        location = item.traceback[0]
        if location.filename.endswith("ema_pullback_v2_development_replay.py") and 88 <= location.lineno <= 97:
            retained.append({"line": location.lineno, "count_diff": item.count_diff,
                             "retained_bytes_diff": item.size_diff})
    tracemalloc.stop()
    return {"reference_sha256": hashlib.sha256(output.canonical_utf8).hexdigest(),
            "traced_cpu_ns": elapsed, "current_traced_bytes": current, "peak_traced_bytes": peak,
            "integer_text_retained_allocation_differences": retained}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("count", type=int, choices=(201, 401, 601))
    parser.add_argument("--allocation", action="store_true")
    args = parser.parse_args()
    raw = source(args.count)
    results = allocations(raw) if args.allocation else instrumented(raw)
    if results["reference_sha256"] != FIXTURES[args.count][1]:
        raise ValueError("reference output diverged")
    print(json.dumps({"observations": args.count, "input_sha256": FIXTURES[args.count][0],
                      "mode": "tracemalloc" if args.allocation else "cprofile_with_counters",
                      "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                      **results}, sort_keys=True))

if __name__ == "__main__":
    main()
