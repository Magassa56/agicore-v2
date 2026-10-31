"""Minimal offline mission cycle with fixed worker and independent verifier.

This first adapter pair consists of local Python processes, not model calls.
It executes one allowlisted synthetic mission, with no automatic retries.
"""

from __future__ import annotations

import argparse
import contextlib
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

from agicore.core.events import EventBus
from agicore.core.retry import RetryPolicy
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.init_schema import init_schema
from agicore.l2_memory.schemas.task import TaskCreate
from agicore.l2_memory.services.memory_service import MemoryService
from agicore.l4_planning.dispatcher import Dispatcher
from agicore.l4_planning.handlers import HandlerRegistry
from agicore.l4_planning.orchestrator import AgentOrchestrator
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
        "frozen_pullback": "src/agicore/trading/ema20_pullback_v2.py",
        "incremental_pullback": "src/agicore/trading/synthetic_pullback_replay_v2.py",
        "orchestrator": "src/agicore/l4_planning/orchestrator.py",
        "dispatcher": "src/agicore/l4_planning/dispatcher.py",
        "handler_registry": "src/agicore/l4_planning/handlers.py",
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
    if (
        not path.is_absolute()
        or ".." in path.parts
        or "data" in path.parts
        or any(x in str(path) for x in "?#")
    ):
        raise ValueError("an absolute non-data mission directory is required")
    if path.exists() or path.is_symlink():
        raise FileExistsError("mission directory already exists")
    if any(parent.is_symlink() for parent in path.parents) or not path.parent.is_dir():
        raise ValueError("mission parent must exist and contain no symlinks")
    path.mkdir(mode=0o700)
    return path


def _run_process(
    root: Path, module: str, role: str, observations: int, timeout: int, stage: str
) -> dict:
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
        "--stage",
        stage,
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
    output_dir: Path,
    observations: int,
    *,
    timeout_seconds: int = MAX_TIMEOUT_SECONDS,
    stage: str = "pullback",
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
    if stage not in ("events", "pullback"):
        raise ValueError("unsupported replay stage")
    sources = _source_hashes()
    root = _new_directory(output_dir)
    task_id = str(uuid.uuid4())
    mission = {
        "schema": "agicore:mission:v2",
        "task_id": task_id,
        "kind": "INVENTED_STORAGE_AND_REPLAY",
        "observations": observations,
        "stage": stage,
        "worker": "local_python_worker",
        "verifier": "local_python_independent_verifier",
        "timeout_seconds_per_process": timeout_seconds,
        "memory_limit_bytes_per_process": MEMORY_LIMIT_BYTES,
        "retries": 0,
        "network_or_model_calls": False,
        "authorizations": {
            "synthetic_generation": True,
            "synthetic_storage": True,
            "event_replay": True,
            "pullback": stage == "pullback",
            "real_data": False,
            "broker": False,
            "orders": False,
            "profitability": False,
            "network": False,
            "merge": False,
        },
        "source_sha256": sources,
        "python": sys.version.split()[0],
        "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION,
    }
    (root / "mission.json").write_bytes(canonical(mission))
    _event(root, task_id, "manager", "CREATED")
    steps = {}
    tasks = {}
    status = "FAILED"
    error = None
    engine = None
    try:
        engine = SqlAlchemyEngine(f"sqlite:///{root / 'orchestrator.sqlite3'}")
        init_schema(engine)
        memory, bus, registry = MemoryService(engine), EventBus(), HandlerRegistry()
        orchestrator = AgentOrchestrator(
            memory=memory,
            engine=engine,
            dispatcher=Dispatcher(registry, bus),
            event_bus=bus,
            retry_policy=RetryPolicy(max_attempts=1),
        )
        roles = {
            f"{task_id}-worker": ("worker", WORKER),
            f"{task_id}-verifier": ("verifier", VERIFIER),
        }
        trace_errors = []

        def trace(event):
            states = {
                "task.created": "ASSIGNED",
                "task.started": "STARTED",
                "task.dispatched": "DISPATCHED",
                "task.completed": "COMPLETED",
                "task.failed": "FAILED",
            }
            tid = event.payload.get("task_id")
            if tid not in roles or event.event_type not in states:
                return
            role, module = roles[tid]
            details = {"orchestrator_task_id": tid}
            if event.event_type == "task.created":
                details["adapter"] = module
            if event.event_type == "task.dispatched":
                try:
                    memory.create_event(
                        "task.dispatched",
                        task_id=tid,
                        agent_id=role,
                        payload={"task_type": event.payload.get("task_type")},
                    )
                except Exception as exc:
                    trace_errors.append(str(exc))
            try:
                _event(root, task_id, role, states[event.event_type], **details)
            except OSError as exc:
                trace_errors.append(str(exc))

        bus.subscribe("*", trace)
        payload = {
            "mission_id": task_id,
            "observations": observations,
            "stage": stage,
            "timeout_seconds": timeout_seconds,
        }

        def register(role, module):
            task_type = f"agicore.synthetic.{role}.v2"
            expected_id = f"{task_id}-{role}"

            def execute(task):
                if trace_errors:
                    raise RuntimeError("task audit projection failed before execution")
                if (
                    task.id != expected_id
                    or task.assigned_to != role
                    or task.task_type != task_type
                    or task.payload != payload
                ):
                    raise PermissionError("task exceeds the synthetic mission contract")
                outcome = _run_process(root, module, role, observations, timeout_seconds, stage)
                steps[role] = outcome
                if outcome["exit_code"] != 0 or outcome["timeout"]:
                    raise RuntimeError(f"{role} failed; inspect {outcome['stderr']}")
                return outcome

            registry.register(task_type, execute)
            return task_type, expected_id

        for role, module in (("worker", WORKER), ("verifier", VERIFIER)):
            task_type, tid = register(role, module)
            orchestrator.submit_task(
                TaskCreate(id=tid, task_type=task_type, assigned_to=role, payload=dict(payload))
            )
            if trace_errors:
                raise RuntimeError("task audit projection failed")
            finished = orchestrator.execute_one(tid)
            tasks[role] = {
                "id": tid,
                "task_type": task_type,
                "assigned_to": finished.assigned_to,
                "status": finished.status,
                "error": finished.error,
            }
            if trace_errors:
                raise RuntimeError("task audit projection failed")
            if finished.status != "completed":
                error = f"{role} failed: {finished.error}"
                break
        else:
            try:
                worker = json.loads((root / "bundle" / "worker.json").read_bytes())
                verification = json.loads((root / "bundle" / "verification.json").read_bytes())
            except (OSError, ValueError) as exc:
                raise ValueError(
                    "invalid verification receipt: missing or malformed evidence"
                ) from exc
            if (
                verification.get("schema") != "agicore:invented-storage-replay-verification:v2"
                or verification.get("status") != "PASS"
                or verification.get("observations") != observations
                or verification.get("stage") != stage
                or worker.get("stage") != stage
                or verification.get("manifest_sha256") != worker.get("manifest_sha256")
                or verification.get("input_sha256") != worker.get("input_sha256")
                or verification.get("replay") != worker.get("replay")
            ):
                raise ValueError("invalid verification receipt")
            if _source_hashes() != sources:
                raise ValueError("mission sources changed during execution")
            status = "PASS"
    except Exception as exc:
        error = f"mission failed: {type(exc).__name__}: {exc}"
    finally:
        if engine is not None:
            engine.dispose()
    report = {
        "schema": "agicore:mission-report:v2",
        "task_id": task_id,
        "status": status,
        "observations": observations,
        "stage": stage,
        "orchestrator": "AgentOrchestrator+Dispatcher",
        "tasks": tasks,
        "task_history": "orchestrator.sqlite3",
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
    parser.add_argument("--stage", choices=("events", "pullback"), default="pullback")
    args = parser.parse_args()
    with contextlib.redirect_stdout(sys.stderr):
        report = run_mission(
            args.output_dir,
            args.observations,
            timeout_seconds=args.timeout_seconds,
            stage=args.stage,
        )
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
