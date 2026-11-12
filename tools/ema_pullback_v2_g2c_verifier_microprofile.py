"""Bounded differential probe of the verifier core, not a G2C production/sealing entry point."""

from __future__ import annotations

import argparse
import cProfile
import json
import pstats
import resource
import sys
import time
from pathlib import Path

from agicore.trading import ema_pullback_v2_g2c_scaling as v4
from agicore.trading import ema_pullback_v2_g2c_verifier_v5 as v5
from agicore.trading.ema_pullback_v2_storage_format import (
    canonical,
    codec_profile,
    contracts,
    immutable_write,
    parse_canonical,
    regular_read,
    require,
    sha,
)

# Exact invented dense input and native bytes, independent of codec/runtime.
CASES = {
    201: (
        "3d7c927e929737bf5fcde6351d41e16ce538be4c988c3e8e89b99df43250e274",
        "5a26a16e5d7d51ca88d1add59f1889d8c1cbc29fb4393917dcb7eb69b7d1e99d",
    ),
    401: (
        "3ff0172bb1cbfdd73da1253792a98c2724d7adb31a16e01746901b1422c3dff9",
        "d74cf6e09161955e51e7974e8e2809a5cc10687c7441b3284741e8143bb8cf3e",
    ),
    601: (
        "2a01c33f65dd0ebf3efa42f38302d45daba6f115bf34352cbb371419a1706d88",
        "9137407aaf887ae7bc0b01d5d2b9956c229bc3c44d1ce9729845dd9ddfa6d808",
    ),
}
CAPS = {resource.RLIMIT_AS: 1 << 30, resource.RLIMIT_CPU: 60, resource.RLIMIT_FSIZE: 32 << 20}


def prepare(folder, n):
    """Produce each small comparison input once; never emit a production receipt."""
    from agicore.trading import ema_pullback_v2_development_replay as ref
    from agicore.trading import ema_pullback_v2_recovery_optimized as opt
    from agicore.trading.ema_pullback_v2_g2b_storage import _witnesses
    from agicore.trading.ema_pullback_v2_recovery_evidence import CanonicalEncoderV1
    from tests.unit.trading.v2_recovery_synthetic_fixtures import dense_lifecycle_resource_bars_v2

    require(n in CASES, "microprofile size")
    folder.mkdir(parents=True, exist_ok=False)
    raw = b"".join(v4._bar_row(b) for b in dense_lifecycle_resource_bars_v2(n))
    require(sha(raw) == CASES[n][0], "registered invented input")
    doc, _ = opt.run_synthetic_native_v1(raw, bindings=ref.read_frozen_replay_bindings_v2())
    native = CanonicalEncoderV1().bytes(doc)
    require(sha(native) == CASES[n][1], "registered native bytes")
    witnesses = b"".join(canonical(w) for w in _witnesses(raw))
    immutable_write(folder / "fixture", raw)
    streams = [
        v4.encode_pages(value, name, folder, codec_profile())
        for value, name in ((native, "native_result"), (witnesses, "source_witnesses"))
    ]
    immutable_write(folder / "streams", canonical(streams))


def measure(folder, n, decoder):
    """Measure disjoint CPU phases on stored bytes; do not replay the source."""
    raw = regular_read(folder / "fixture", 1 << 16)
    require(sha(raw) == CASES[n][0] and len(raw.splitlines()) == n, "invented fixture")
    profile = codec_profile()
    streams = parse_canonical([regular_read(folder / "streams", 1 << 18)])
    schema = contracts()[1]["result_schema"]
    stages = {}

    def timed(name, fn, *args, **kwargs):
        start = time.process_time_ns()
        value = fn(*args, **kwargs)
        stages[name] = time.process_time_ns() - start
        return value

    native, rows = [
        timed("reconstruct_" + s["stream_id"], v4.decode_pages, s, folder, profile) for s in streams
    ]
    require(sha(native) == CASES[n][1], "exact native bytes")
    doc = timed(
        "native_parse_schema_roundtrip",
        v5.parse_native if decoder == "v5" else parse_canonical,
        native if decoder == "v5" else [native],
        limit=v4.MAX_LOGICAL_BYTES,
        schema=schema,
    )
    witnesses = timed(
        "parse_witnesses", lambda: [parse_canonical([w]) for w in rows.splitlines(True)]
    )
    audit = timed(
        "audit_accounting_provenance",
        v5.audit_optimized_native,
        doc,
        witnesses,
        raw,
        runner_sha=v4.RUNNER_SHA256,
        input_sha=sha(raw),
        maximum=n,
    )
    return {
        "role": decoder,
        "observations": n,
        "input_sha256": sha(raw),
        "native_sha256": sha(native),
        "native_output_sha256": doc["output_sha256"],
        "witness_sha256": sha(rows),
        "native_bytes": len(native),
        "witness_bytes": len(rows),
        "audit_sha256": sha(canonical(audit)),
        "audit_status": audit["status"],
        "closed_positions": len(doc["closed_trade_records"]),
        "cpu_ns": stages,
        "timed_cpu_ns": sum(stages.values()),
        "linux_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
    }


def main():
    """Example: timeout 75s python -m tools.ema_pullback_v2_g2c_verifier_microprofile DIR 201 v4 TRUST."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dir", type=Path)
    parser.add_argument("n", choices=tuple(CASES), type=int)
    parser.add_argument("mode", choices=("prepare", "v4", "v5", "profile-v4"))
    parser.add_argument("verifier_sha256")
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("Linux resource accounting required")
    for key, cap in CAPS.items():
        _, hard = resource.getrlimit(key)
        actual = min(hard, cap) if hard != resource.RLIM_INFINITY else cap
        soft, _ = resource.getrlimit(key)
        actual = min(actual, soft) if soft != resource.RLIM_INFINITY else actual
        resource.setrlimit(key, (actual, actual))
    folder = args.dir.absolute() / str(args.n)
    require(
        "data" not in folder.parts and not any(p.is_symlink() for p in (folder, *folder.parents)),
        "small profile path",
    )
    v5.load_registration(args.verifier_sha256)
    if args.mode == "prepare":
        prepare(folder, args.n)
        return
    if args.mode == "profile-v4":
        profiler = cProfile.Profile()
        report = profiler.runcall(measure, folder, args.n, "v4")
        watch = {
            "peek",
            "take",
            "value",
            "integer_text",
            "rational",
            "_audit_trade",
            "_lifecycle_audit",
            "_validate_rational_contracts",
            "source_witnesses",
        }
        report["instrumented_frames"] = [
            {
                "file": Path(path).name,
                "function": name,
                "calls": v[1],
                "self_s": round(v[2], 6),
                "cumulative_s": round(v[3], 6),
            }
            for (path, _, name), v in sorted(pstats.Stats(profiler).stats.items())
            if name in watch and Path(path).name.startswith("ema_pullback_v2_")
        ]
    else:
        report = measure(folder, args.n, args.mode)
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
