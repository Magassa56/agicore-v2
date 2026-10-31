"""Minimal offline mission cycle with fixed worker and independent verifier.

This first adapter pair consists of local Python processes, not model calls.
It executes one allowlisted synthetic mission, with no automatic retries.
"""

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
import uuid
import zlib
from datetime import UTC, datetime
from pathlib import Path

from agicore.trading.synthetic_mission_storage_v2 import MAX_OBSERVATIONS, canonical

REPOSITORY = Path(__file__).resolve().parents[3]
MAX_TIMEOUT_SECONDS = 300
MEMORY_LIMIT_BYTES = 2 * 1024**3
FILE_LIMIT_BYTES = 128 * 1024**2
WORKER = "agicore.trading.synthetic_mission_storage_v2"
VERIFIER = "agicore.trading.synthetic_mission_verify_v2"


def _source_hashes() -> dict[str, str]:
    paths = {
        "manager": "src/agicore/manager/mission_cycle_v2.py",
        "worker": "src/agicore/trading/synthetic_mission_storage_v2.py",
        "verifier": "src/agicore/trading/synthetic_mission_verify_v2.py",
        "generator": "tools/agicore_v2_synthetic_scale_probe.py",
        "parser": "src/agicore/trading/ema_pullback_v2_development_replay.py",
        "impulse": "src/agicore/trading/directional_impulse_v2.py",
        "reversal": "src/agicore/trading/reversal_transition_v2.py",
        "context": "src/agicore/trading/regime_context_v2.py",
    }
    result = {}
    for name, path in paths.items():
        with (REPOSITORY / path).open("rb") as source:
            result[name] = hashlib.file_digest(source, "sha256").hexdigest()
    return result


def _event(root: Path, task_id: str, agent_id: str, state: str, **details: object) -> None:
    record = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "task_id": task_id,
        "agent_id": agent_id,
        "state": state,
        **details,
    }
    with (root / "events.jsonl").open("ab") as output:
        output.write(canonical(record))
        output.flush()
        os.fsync(output.fileno())


def _new_directory(path: Path) -> Path:
    if not path.is_absolute() or ".." in path.parts or "data" in path.parts:
        raise ValueError("an absolute non-data mission directory is required")
    if path.exists() or path.is_symlink():
        raise FileExistsError("mission directory already exists")
    if any(parent.is_symlink() for parent in path.parents) or not path.parent.is_dir():
        raise ValueError("mission parent must exist and contain no symlinks")
    path.mkdir(mode=0o700)
    return path


def _run_process(root: Path, module: str, role: str, observations: int, timeout: int) -> dict:
    """Run one allowlisted process and collect its own wait4 resource usage."""
    if module not in (WORKER, VERIFIER):
        raise ValueError("unregistered mission adapter")
    env = {
        "PATH": "/usr/bin:/bin",
        "PYTHONPATH": f"{REPOSITORY / 'src'}:{REPOSITORY}",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "LC_ALL": "C.UTF-8",
    }
    command = [
        sys.executable,
        "-B",
        "-m",
        module,
        "--bundle",
        str(root / "bundle"),
        "--observations",
        str(observations),
    ]

    def limits() -> None:
        resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT_BYTES, MEMORY_LIMIT_BYTES))
        resource.setrlimit(resource.RLIMIT_FSIZE, (FILE_LIMIT_BYTES, FILE_LIMIT_BYTES))
        resource.setrlimit(resource.RLIMIT_CPU, (timeout + 5, timeout + 5))

    start = time.perf_counter_ns()
    timed_out = False
    with (
        (root / f"{role}.stdout").open("xb") as stdout,
        (root / f"{role}.stderr").open("xb") as stderr,
    ):
        child = subprocess.Popen(
            command,
            cwd=REPOSITORY,
            env=env,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
            preexec_fn=limits,
        )
        while True:
            pid, status, usage = os.wait4(child.pid, os.WNOHANG)
            if pid:
                break
            if time.perf_counter_ns() - start >= timeout * 1_000_000_000:
                timed_out = True
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                pid, status, usage = os.wait4(child.pid, 0)
                break
            time.sleep(0.05)
        code = os.waitstatus_to_exitcode(status)
        child.returncode = code
    return {
        "pid": child.pid,
        "exit_code": code,
        "timeout": timed_out,
        "wall_ns": time.perf_counter_ns() - start,
        "peak_rss_bytes": usage.ru_maxrss * 1024,
        "user_cpu_seconds": usage.ru_utime,
        "system_cpu_seconds": usage.ru_stime,
        "stderr": f"{role}.stderr",
    }


def run_mission(
    output_dir: Path, observations: int, *, timeout_seconds: int = MAX_TIMEOUT_SECONDS
) -> dict:
    """Assign one synthetic mission, execute, independently verify, and report.

    The output directory must not exist. Processes are bounded but are not an
    operating-system sandbox for untrusted adapters; only fixed local code runs.
    """
    if sys.platform != "linux":
        raise RuntimeError("the bounded subprocess implementation requires Linux")
    if type(observations) is not int or not 1 <= observations <= MAX_OBSERVATIONS:
        raise ValueError("invalid synthetic observation count")
    if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= MAX_TIMEOUT_SECONDS:
        raise ValueError("invalid timeout")
    sources = _source_hashes()
    root = _new_directory(output_dir)
    task_id = str(uuid.uuid4())
    mission = {
        "schema": "agicore:mission:v2",
        "task_id": task_id,
        "kind": "INVENTED_STORAGE_AND_EVENT_REPLAY",
        "observations": observations,
        "worker": "local_python_worker",
        "verifier": "local_python_independent_verifier",
        "timeout_seconds_per_process": timeout_seconds,
        "memory_limit_bytes_per_process": MEMORY_LIMIT_BYTES,
        "retries": 0,
        "network_or_model_calls": False,
        "source_sha256": sources,
        "python": sys.version.split()[0],
        "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION,
    }
    (root / "mission.json").write_bytes(canonical(mission))
    _event(root, task_id, "manager", "CREATED")
    steps = {}
    status = "FAILED"
    error = None
    for role, module in (("worker", WORKER), ("verifier", VERIFIER)):
        _event(root, task_id, role, "ASSIGNED", adapter=module)
        _event(root, task_id, role, "STARTED")
        try:
            outcome = _run_process(root, module, role, observations, timeout_seconds)
        except (OSError, ValueError) as exc:
            error = f"{role} could not start: {type(exc).__name__}: {exc}"
            _event(root, task_id, role, "FAILED", error=error)
            break
        steps[role] = outcome
        if outcome["exit_code"] != 0 or outcome["timeout"]:
            error = f"{role} failed; inspect {outcome['stderr']}"
            _event(root, task_id, role, "FAILED", **outcome)
            break
        _event(root, task_id, role, "COMPLETED", **outcome)
    else:
        try:
            worker = json.loads((root / "bundle" / "worker.json").read_bytes())
            verification = json.loads((root / "bundle" / "verification.json").read_bytes())
            if (
                verification.get("schema") != "agicore:invented-storage-replay-verification:v2"
                or verification.get("status") != "PASS"
                or verification.get("observations") != observations
                or verification.get("manifest_sha256") != worker.get("manifest_sha256")
                or verification.get("input_sha256") != worker.get("input_sha256")
                or verification.get("replay") != worker.get("replay")
            ):
                raise ValueError("verification receipt mismatch")
            if _source_hashes() != sources:
                raise ValueError("mission sources changed during execution")
            status = "PASS"
        except (OSError, ValueError, TypeError, AttributeError) as exc:
            error = f"invalid verification receipt: {type(exc).__name__}: {exc}"
    report = {
        "schema": "agicore:mission-report:v2",
        "task_id": task_id,
        "status": status,
        "observations": observations,
        "steps": steps,
        "error": error,
        "source_sha256": sources,
        "limitations": [
            "Local deterministic adapters, not Terra or Codex model calls.",
            "Independent storage and event-pipeline verification uses the same frozen V2 predicates.",
            "No full strategy replay, historical storage certification, or profitability.",
        ],
    }
    if status == "PASS":
        report["verification"] = verification
    _event(root, task_id, "manager", status, error=error)
    (root / "report.json").write_bytes(canonical(report))
    return report


def main() -> None:
    """Execute one local synthetic mission and print its report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--observations", type=int, default=MAX_OBSERVATIONS)
    parser.add_argument("--timeout-seconds", type=int, default=MAX_TIMEOUT_SECONDS)
    args = parser.parse_args()
    report = run_mission(args.output_dir, args.observations, timeout_seconds=args.timeout_seconds)
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
