"""Supervised invented-only resource tests. No real loader, authorization or claim."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import signal
import subprocess
import sys
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path

from agicore.trading import ema_pullback_v2_development_replay as reference
from agicore.trading import ema_pullback_v2_recovery_optimized as candidate
from agicore.trading.ema_pullback_v2_recovery_evidence import (
    CanonicalEncoderV1,
    validate_native_result_v1,
)
from tests.unit.trading.v2_recovery_indicator_oracle import exact_indicator_polynomial_oracle
from tests.unit.trading.v2_recovery_synthetic_fixtures import (
    FAMILIES,
    SIZES,
    dense_lifecycle_resource_bars_v2,
    resource_fixture_bars,
)

DEADLINES = {1000: 120, 5000: 600, 10000: 1800, 20000: 3600}
MEMORY_CAP = 4_294_967_296
OUTPUT_CAP = 8_589_934_592


def _utc():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _write(path, value):
    raw = CanonicalEncoderV1().bytes(reference._native(value))
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def _progress(path, value):
    with path.open("ab") as stream:
        stream.write((json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode())
        stream.flush()


def _usage():
    return {"cpu_time_ns": time.process_time_ns(),
            "peak_memory_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            "peak_memory_method": "Linux getrusage(RUSAGE_SELF).ru_maxrss KiB * 1024"}


def _verify_sources(plan):
    for source in plan["sources"]:
        actual = hashlib.sha256(Path(source["path"]).read_bytes()).hexdigest()
        if actual != source["sha256"]:
            raise RuntimeError("predeclared source changed: " + source["path"])


def _worker(plan, family, count, repeat, folder):
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_CAP, MEMORY_CAP))
    resource.setrlimit(resource.RLIMIT_FSIZE, (OUTPUT_CAP, OUTPUT_CAP))
    resource.setrlimit(resource.RLIMIT_CPU, (DEADLINES[count] + 5, DEADLINES[count] + 5))
    def deadline(signum, frame):
        raise TimeoutError("synthetic worker wall-clock deadline exceeded")
    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(DEADLINES[count])
    start = time.monotonic_ns()
    receipt = {"family": family, "observations": count, "repeat": repeat,
               "input_domain": "INVENTED_SYNTHETIC_ONLY", "pid": os.getpid(),
               "started_utc": _utc(), "status": "RUNNING",
               "wall_deadline_seconds": DEADLINES[count], "memory_cap_bytes": MEMORY_CAP,
               "output_cap_bytes": OUTPUT_CAP, "source_plan_sha256": plan["plan_sha256"],
               "real_recovery_invocations": 0}
    _write(folder / "START.json", receipt)
    completed, phase = -1, "START"
    serialization_ns = validation_ns = None
    try:
        _verify_sources(plan)
        bars = tuple(dense_lifecycle_resource_bars_v2(count) if family == FAMILIES[3]
                     else resource_fixture_bars(family, count))
        raw = ("\n".join(";".join((
            b.timestamp_utc.strftime("%Y%m%d %H%M%S"),
            *(str(getattr(b, n)) for n in ("open", "high", "low", "close")), str(b.volume)
        )) for b in bars) + "\n").encode("ascii")
        raw_hash = hashlib.sha256(raw).hexdigest()
        if raw_hash == reference.CANONICAL_DATASET_RAW_SHA256:
            raise RuntimeError("real dataset forbidden")
        with (folder / "invented-input.Last.txt").open("xb") as stream:
            stream.write(raw)
        latest_engine = None
        def progress(index, current_phase, engine):
            nonlocal completed, phase, latest_engine
            latest_engine = engine
            completed = index if current_phase == "CLOSE" else index - 1
            phase = current_phase
            if index % 250 == 0 or index == count - 1:
                _progress(folder / "progress.jsonl", {
                    "utc": _utc(), "last_completed_actual_bar_index": completed,
                    "phase": phase, **_usage(), "elapsed_ns": time.monotonic_ns() - start,
                })
        bindings = reference.read_frozen_replay_bindings_v2()
        document, identity = candidate.run_synthetic_native_v1(raw, bindings=bindings,
                                                              progress=progress)
        if family == FAMILIES[3]:
            metrics = document["metrics"]
            if not (metrics["long_entry_fills"] > 1 and metrics["short_entry_fills"] > 1
                    and metrics["structural_stop_exits"] > 0 and metrics["ema20_exits"] > 0
                    and metrics["quantity_1_count"] > 0 and metrics["quantity_2_count"] > 0
                    and metrics["risk_rejections"] > 0):
                raise RuntimeError("FAILED_REQUIRED_DENSE_LIFECYCLE_FIXTURE_COVERAGE")
        phase = "INDICATOR_ORACLE"
        _progress(folder / "progress.jsonl", {"utc": _utc(), "phase": phase,
            "last_completed_actual_bar_index": completed, **_usage()})
        indicators = latest_engine.indicators
        ema = indicators.ema20()
        macd = indicators.macd()
        # Algebraically independent polynomial oracle, verified against frozen
        # prefix functions at every declared checkpoint through 1,000 bars.
        expected = exact_indicator_polynomial_oracle(bars)
        actual = {"ema20": ema.ema20, **{name: getattr(macd, name) for name in (
            "ema12", "ema26", "macd", "signal", "histogram", "previous_macd",
            "previous_histogram")}}
        if actual != expected:
            _write(folder / "oracle-counterexample.json", reference._native(
                {"candidate": actual, "polynomial_oracle": expected}))
            raise RuntimeError("BLOCKED_SEMANTIC_EQUIVALENCE: independent prefix oracle differs")
        rationals = [ema.ema20, macd.ema12, macd.ema26, macd.macd, macd.signal,
                     macd.histogram, macd.previous_macd, macd.previous_histogram]
        numerator_bits = max(abs(v.numerator).bit_length() for v in rationals if v is not None)
        denominator_bits = max(v.denominator.bit_length() for v in rationals if v is not None)
        phase = "VALIDATION"
        _progress(folder / "progress.jsonl", {"utc": _utc(), "phase": phase,
            "last_completed_actual_bar_index": completed, **_usage()})
        before = time.monotonic_ns()
        validate_native_result_v1(document, bindings, identity)
        validation_ns = time.monotonic_ns() - before
        phase = "SERIALIZATION"
        _progress(folder / "progress.jsonl", {"utc": _utc(), "phase": phase,
            "last_completed_actual_bar_index": completed, **_usage()})
        before = time.monotonic_ns()
        digest = hashlib.sha256()
        output_size = 0
        with (folder / "complete-native-output.json").open("xb") as stream:
            for chunk in CanonicalEncoderV1().chunks(document):
                output_size += len(chunk)
                if output_size > OUTPUT_CAP:
                    raise RuntimeError("output size cap exceeded")
                stream.write(chunk)
                digest.update(chunk)
            stream.flush()
            os.fsync(stream.fileno())
        serialization_ns = time.monotonic_ns() - before
        receipt.update(status="PASS", input_sha256=raw_hash,
            runner_source_sha256=identity.runner_source_sha256,
            output_sha256=digest.hexdigest(), output_size_bytes=output_size,
            native_payload_sha256=document["output_sha256"],
            numerator_bit_length=numerator_bits, denominator_bit_length=denominator_bits,
            scaled_operand_bit_length=indicators.lane.denominator.bit_length(),
            independent_indicator_oracle="PASS", serialization_time_ns=serialization_ns,
            validation_time_ns=validation_ns, completed_observation_count=completed + 1,
            process_exit_status=0)
    except Exception as error:  # noqa: BLE001 -- persist traceback and fail the child, never retry
        traceback.print_exc()
        receipt.update(status="FAILED", failure_type=type(error).__name__, failure=str(error),
                       completed_observation_count=completed + 1, failure_phase=phase,
                       serialization_time_ns=serialization_ns, validation_time_ns=validation_ns,
                       process_exit_status=1)
    receipt.update(ended_utc=_utc(), wall_time_ns=time.monotonic_ns() - start, **_usage())
    signal.alarm(0)
    _write(folder / "END.json", receipt)
    return 0 if receipt["status"] == "PASS" else 1


def _supervise(plan_path, destination):
    raw_plan = plan_path.read_bytes()
    plan = json.loads(raw_plan)
    plan["plan_sha256"] = hashlib.sha256(raw_plan).hexdigest()
    _verify_sources(plan)
    destination.mkdir(parents=True, exist_ok=False)
    _write(destination / "SUITE_START.json", {"utc": _utc(), "pid": os.getpid(),
            "plan_sha256": plan["plan_sha256"], "real_recovery_invocations": 0})
    receipts = []
    for size in SIZES:
        for family in FAMILIES:
            previous = None
            for repeat in (1, 2):
                folder = destination / (family + "-" + str(size) + "-" + str(repeat))
                folder.mkdir()
                command = [sys.executable, "-B", str(Path(__file__).resolve()), "--worker",
                           "--plan", str(plan_path), "--output", str(folder),
                           "--family", family, "--count", str(size), "--repeat", str(repeat)]
                with (folder / "stdout.log").open("xb") as stdout, (
                    folder / "stderr.log").open("xb") as stderr:
                    process = subprocess.Popen(command, stdout=stdout, stderr=stderr,
                                               start_new_session=True)
                    _write(folder / "SUPERVISOR_START.json", {
                        "utc": _utc(), "child_pid": process.pid, "command": command,
                        "cwd": os.getcwd(), "deadline_seconds": DEADLINES[size]})
                    started = time.monotonic_ns()
                    timed_out = False
                    while process.poll() is None:
                        if time.monotonic_ns() - started > DEADLINES[size] * 1_000_000_000:
                            timed_out = True
                            os.killpg(process.pid, signal.SIGTERM)
                            try:
                                process.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                os.killpg(process.pid, signal.SIGKILL)
                                process.wait(timeout=5)
                            break
                        time.sleep(1)
                result = json.loads((folder / "END.json").read_bytes()) if (
                    folder / "END.json").exists() else {"status": "FAILED_NO_END_RECEIPT"}
                result.update(supervisor_exit_status=process.returncode, timed_out=timed_out,
                              family=family, observations=size, repeat=repeat)
                _write(folder / "SUPERVISOR_END.json", result)
                receipts.append(result)
                if result["status"] != "PASS" or process.returncode != 0 or timed_out:
                    _write(destination / "SUITE_END.json", {
                        "status": "BLOCKED", "utc": _utc(), "receipts": receipts,
                        "remaining_benchmarks": "NOT_EXECUTED_AFTER_MANDATORY_FAILURE"})
                    return 1
                if previous is not None and previous["output_sha256"] != result["output_sha256"]:
                    _write(destination / "SUITE_END.json", {
                        "status": "BLOCKED_SEMANTIC_EQUIVALENCE", "utc": _utc(),
                        "receipts": receipts, "failure": "fresh process output hashes differ"})
                    return 1
                previous = result
    _write(destination / "SUITE_END.json", {"status": "PASS", "utc": _utc(), "receipts": receipts})
    return 0


def main():
    """Run only a hashed, predeclared invented fixture plan under explicit caps."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--family", choices=FAMILIES)
    parser.add_argument("--count", type=int, choices=SIZES)
    parser.add_argument("--repeat", type=int, choices=(1, 2))
    args = parser.parse_args()
    if args.worker:
        raw = args.plan.read_bytes()
        plan = json.loads(raw)
        plan["plan_sha256"] = hashlib.sha256(raw).hexdigest()
        return _worker(plan, args.family, args.count, args.repeat, args.output)
    return _supervise(args.plan.resolve(), args.output.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
