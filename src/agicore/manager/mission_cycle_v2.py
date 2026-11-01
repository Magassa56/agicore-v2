"""Minimal offline mission cycle with fixed worker and independent verifier.

This first adapter pair consists of local Python processes, not model calls.
It executes one allowlisted synthetic mission, with no automatic retries.
"""

from __future__ import annotations

import argparse
import contextlib
import ctypes
import fcntl
import hashlib
import json
import os
import resource
import signal
import sqlite3
import stat
import subprocess
import sys
import tempfile
import threading
import time
import uuid
import zlib
from contextlib import contextmanager
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

from sqlalchemy import select

from agicore.core.events import EventBus
from agicore.core.retry import RetryPolicy
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.init_schema import init_schema
from agicore.l2_memory.models.task import Task
from agicore.l2_memory.repositories.task_repository import TaskRepository
from agicore.l2_memory.schemas.task import TaskCreate
from agicore.l2_memory.services.memory_service import MemoryService
from agicore.l4_planning.dispatcher import Dispatcher
from agicore.l4_planning.handlers import HandlerRegistry
from agicore.l4_planning.orchestrator import AgentOrchestrator
from agicore.trading.synthetic_confirmation_fixture_v2 import (
    OBSERVATIONS as FIXTURE_OBSERVATIONS,
)
from agicore.trading.synthetic_confirmation_fixture_v2 import PROFILES
from agicore.trading.synthetic_confirmation_fixture_v2 import SCHEMA as FIXTURE_SCHEMA
from agicore.trading.synthetic_confirmation_replay_v2 import SCHEMA as CONFIRMATION_SCHEMA
from agicore.trading.synthetic_mission_storage_v2 import MAX_OBSERVATIONS, canonical

REPOSITORY = Path(__file__).resolve().parents[3]
MAX_TIMEOUT_SECONDS = 300
MEMORY_LIMIT_BYTES = 2 * 1024**3
FILE_LIMIT_BYTES = 128 * 1024**2
WORKER = "agicore.trading.synthetic_mission_storage_v2"
VERIFIER = "agicore.trading.synthetic_mission_verify_v2"
DEFAULT_OBSERVATIONS = 64


class ResumeBlockedError(RuntimeError):
    """Refuse to guess whether an interrupted operation was performed."""


@contextmanager
def _mission_lock(root: Path, *, create: bool = False):
    """Hold a per-mission, nonblocking lock across normal execution and resume."""
    flags = os.O_RDWR | os.O_NOFOLLOW | (os.O_CREAT | os.O_EXCL if create else 0)
    try:
        descriptor = os.open(root / ".mission.lock", flags, 0o600)
    except OSError as exc:
        raise ResumeBlockedError("missing or invalid mission lock") from exc
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ResumeBlockedError("invalid mission lock file")
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ResumeBlockedError("mission is already active") from exc
        yield
    finally:
        os.close(descriptor)


def _read_regular(path: Path, limit: int = 1_000_000) -> bytes:
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit:
            raise ResumeBlockedError("invalid evidence file")
        raw = stream.read(limit + 1)
        if len(raw) != info.st_size:
            raise ResumeBlockedError("evidence changed while reading")
        return raw


def _hash_regular(path: Path, limit: int = FILE_LIMIT_BYTES) -> str:
    """Hash one bounded regular file without following links or loading it all."""
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit:
            raise ResumeBlockedError("invalid evidence file")
        digest, count = hashlib.sha256(), 0
        while chunk := stream.read(1024 * 1024):
            count += len(chunk)
            if count > limit:
                raise ResumeBlockedError("evidence exceeds size limit")
            digest.update(chunk)
        if count != info.st_size:
            raise ResumeBlockedError("evidence changed while reading")
        return digest.hexdigest()


def _event_prefix(root: Path, size: int | None = None) -> dict:
    raw = _read_regular(root / "events.jsonl")
    if size is None:
        size = len(raw)
    if type(size) is not int or not 0 < size <= len(raw) or raw[size - 1 : size] != b"\n":
        raise ResumeBlockedError("invalid event checkpoint")
    return {"bytes": size, "sha256": hashlib.sha256(raw[:size]).hexdigest()}


def _json_evidence(path: Path) -> tuple[dict, str]:
    raw = _read_regular(path)
    try:
        value = json.loads(raw)
    except (UnicodeError, ValueError) as exc:
        raise ResumeBlockedError("malformed evidence") from exc
    if type(value) is not dict or canonical(value) != raw:
        raise ResumeBlockedError("noncanonical evidence")
    return value, hashlib.sha256(raw).hexdigest()


def _seal_evidence(root: Path, role: str, mission: dict, expected: dict | None = None) -> dict:
    """Hash persisted evidence; on verifier completion check every stored object."""
    bundle = root / "bundle"
    chunks = bundle / "chunks"
    if bundle.is_symlink() or chunks.is_symlink() or not chunks.is_dir():
        raise ResumeBlockedError("invalid bundle directory")
    manifest, manifest_sha = _json_evidence(bundle / "manifest.json")
    worker, worker_sha = _json_evidence(bundle / "worker.json")
    profile = mission["profile"]
    replay = worker.get("replay")
    if mission["stage"] == "confirmation" and type(replay) is dict:
        counts, processed, reason = (
            replay.get("counts"),
            replay.get("processed_observations"),
            replay.get("stop_reason"),
        )
        valid_replay = (
            replay.get("schema") == CONFIRMATION_SCHEMA
            and type(replay.get("input_observations")) is int
            and replay["input_observations"] == mission["observations"]
            and type(processed) is int
            and 1 <= processed <= mission["observations"]
            and type(counts) is dict
            and all(type(value) is int and value >= 0 for value in counts.values())
            and type(counts.get("confirmations_qualified")) is int
            and (
                (reason == "CONFIRMED_BEFORE_RISK" and counts["confirmations_qualified"] == 1)
                or (
                    reason in ("END_OF_INPUT", "END_OF_INPUT_AWAITING_CONFIRMATION")
                    and counts["confirmations_qualified"] == 0
                    and processed == mission["observations"]
                )
            )
        )
    else:
        valid_replay = (
            type(replay) is dict
            and type(replay.get("observations")) is int
            and replay["observations"] == mission["observations"]
        )
    if (
        manifest.get("schema")
        != ("agicore:invented-observation-bundle:v2" if profile == "standard" else FIXTURE_SCHEMA)
        or manifest.get("profile", "standard") != profile
        or (profile == "standard" and "profile" in manifest)
        or manifest.get("domain") != "INVENTED_GENERATOR_ONLY"
        or type(manifest.get("observations")) is not int
        or manifest.get("observations") != mission["observations"]
        or worker.get("schema") != "agicore:invented-storage-replay-worker:v2"
        or worker.get("domain") != "SYNTHETIC_ONLY"
        or worker.get("stage") != mission["stage"]
        or worker.get("profile", "standard") != profile
        or (profile == "standard" and "profile" in worker)
        or worker.get("manifest_sha256") != manifest_sha
        or worker.get("input_sha256") != manifest.get("raw_sha256")
        or not valid_replay
    ):
        raise ResumeBlockedError("worker evidence does not match mission")
    if expected is not None and type(expected) is not dict:
        raise ResumeBlockedError("invalid stored evidence")
    checkpoint = None if expected is None else expected.get("event_prefix")
    if checkpoint is not None and type(checkpoint) is not dict:
        raise ResumeBlockedError("invalid stored event checkpoint")
    result = {
        "manifest_sha256": manifest_sha,
        "worker_sha256": worker_sha,
        "stdout_sha256": _hash_regular(root / f"{role}.stdout"),
        "stderr_sha256": _hash_regular(root / f"{role}.stderr"),
        "event_prefix": _event_prefix(
            root, None if checkpoint is None else checkpoint.get("bytes")
        ),
    }
    if role == "worker":
        return result
    if role != "verifier":
        raise ResumeBlockedError("unknown evidence role")
    receipt, receipt_sha = _json_evidence(bundle / "verification.json")
    if (
        receipt.get("schema") != "agicore:invented-storage-replay-verification:v2"
        or receipt.get("status") != "PASS"
        or receipt.get("stage") != mission["stage"]
        or receipt.get("profile", "standard") != profile
        or (profile == "standard" and "profile" in receipt)
        or type(receipt.get("observations")) is not int
        or receipt.get("observations") != mission["observations"]
        or receipt.get("manifest_sha256") != manifest_sha
        or receipt.get("input_sha256") != worker.get("input_sha256")
        or canonical(receipt.get("replay")) != canonical(worker.get("replay"))
    ):
        raise ResumeBlockedError("independent verification receipt mismatch")
    entries = manifest.get("chunks")
    if type(entries) is not list or len(entries) != (mission["observations"] + 999) // 1000:
        raise ResumeBlockedError("invalid chunk count")
    if set(os.listdir(chunks)) != {f"{i:04d}.zlib" for i in range(len(entries))}:
        raise ResumeBlockedError("unexpected chunk inventory")
    for i, entry in enumerate(entries):
        if type(entry) is not dict or entry.get("name") != f"{i:04d}.zlib":
            raise ResumeBlockedError("invalid chunk identity")
        raw = _read_regular(chunks / entry["name"], 129_024)
        if (
            type(entry.get("stored_bytes")) is not int
            or len(raw) != entry["stored_bytes"]
            or hashlib.sha256(raw).hexdigest() != entry.get("stored_sha256")
        ):
            raise ResumeBlockedError("stored chunk altered after verification")
    result["verification_sha256"] = receipt_sha
    return result


def _atomic_report(root: Path, report: dict) -> None:
    """Publish a complete report once without overwriting existing evidence."""
    fd, name = tempfile.mkstemp(prefix=".report-", dir=root)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(canonical(report))
            stream.flush()
            os.fsync(stream.fileno())
        os.link(name, root / "report.json", follow_symlinks=False)
        directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        os.unlink(name)


def _checkpoint(name: str) -> None:
    """Fault-injection seam for interruption tests; production does nothing."""


def _validate_mission(mission: dict) -> None:
    """Reject altered, foreign or unsupported mission contracts before resume."""
    expected_keys = {
        "schema",
        "task_id",
        "kind",
        "observations",
        "stage",
        "profile",
        "worker",
        "verifier",
        "timeout_seconds_per_process",
        "memory_limit_bytes_per_process",
        "retries",
        "network_or_model_calls",
        "authorizations",
        "source_sha256",
        "python",
        "zlib_runtime",
        "runtime_packages",
    }
    if set(mission) != expected_keys:
        raise ResumeBlockedError("unsupported historical or altered mission contract")
    try:
        mission_id = str(uuid.UUID(mission["task_id"]))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ResumeBlockedError("invalid mission identity") from exc
    stage = mission["stage"]
    expected_auth = {
        "synthetic_generation": True,
        "synthetic_storage": True,
        "event_replay": True,
        "pullback": stage in ("pullback", "confirmation"),
        "confirmation": stage == "confirmation",
        "real_data": False,
        "broker": False,
        "orders": False,
        "profitability": False,
        "network": False,
        "merge": False,
    }
    auth = mission["authorizations"]
    if (
        mission_id != mission["task_id"]
        or mission["schema"] != "agicore:mission:v2"
        or mission["kind"] != "INVENTED_STORAGE_AND_REPLAY"
        or type(mission["observations"]) is not int
        or not 1 <= mission["observations"] <= MAX_OBSERVATIONS
        or stage not in ("events", "pullback", "confirmation")
        or mission["profile"] not in ("standard", *PROFILES)
        or (
            mission["profile"] != "standard"
            and (stage != "confirmation" or mission["observations"] != FIXTURE_OBSERVATIONS)
        )
        or mission["worker"] != "local_python_worker"
        or mission["verifier"] != "local_python_independent_verifier"
        or type(mission["timeout_seconds_per_process"]) is not int
        or not 1 <= mission["timeout_seconds_per_process"] <= MAX_TIMEOUT_SECONDS
        or type(mission["memory_limit_bytes_per_process"]) is not int
        or mission["memory_limit_bytes_per_process"] != MEMORY_LIMIT_BYTES
        or type(mission["retries"]) is not int
        or mission["retries"] != 0
        or mission["network_or_model_calls"] is not False
        or type(auth) is not dict
        or set(auth) != set(expected_auth)
        or any(type(v) is not bool for v in auth.values())
        or auth != expected_auth
        or mission["source_sha256"] != _source_hashes()
        or mission["python"] != sys.version.split()[0]
        or mission["zlib_runtime"] != zlib.ZLIB_RUNTIME_VERSION
        or mission["runtime_packages"] != _runtime_versions()
    ):
        raise ResumeBlockedError("mission contract, sources or runtime changed")


def _existing_directory(path: Path) -> Path:
    if (
        not path.is_absolute()
        or ".." in path.parts
        or "data" in path.parts
        or any(x in str(path) for x in "?#")
        or path.is_symlink()
        or any(parent.is_symlink() for parent in path.parents)
        or not path.is_dir()
    ):
        raise ResumeBlockedError("invalid existing mission directory")
    return path


def _bound_database(root: Path, task_id: str, contract_sha: str) -> None:
    """Check an existing DB and its durable mission seal without creating files."""
    path = root / "orchestrator.sqlite3"
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        try:
            info = os.fstat(descriptor)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise ResumeBlockedError("invalid orchestration database")
        finally:
            os.close(descriptor)
        with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
            rows = db.execute(
                "select mission_id, contract_sha256 from mission_contract_binding"
            ).fetchall()
            if rows != [(task_id, contract_sha)]:
                raise ResumeBlockedError("mission database binding mismatch")
    except (OSError, sqlite3.Error) as exc:
        raise ResumeBlockedError("missing or unsealed orchestration database") from exc


def _validate_lifecycle(
    root: Path, engine: SqlAlchemyEngine, task, mission_id: str, role: str
) -> None:
    """Reject partial task/audit transitions instead of silently repairing them."""
    expected = {
        "pending": (["task.created"], ["ASSIGNED"]),
        "completed": (
            ["task.created", "task.started", "task.dispatched", "task.completed"],
            ["ASSIGNED", "STARTED", "DISPATCHED", "COMPLETED"],
        ),
    }
    if task.status not in expected:
        raise ResumeBlockedError("task state is running, failed or otherwise ambiguous")
    with engine.engine.connect() as connection:
        kinds = list(
            connection.exec_driver_sql(
                "SELECT event_type FROM events WHERE task_id = ? ORDER BY id", (task.id,)
            ).scalars()
        )
    try:
        raw = _read_regular(root / "events.jsonl", 1_000_000)
        rows = raw.splitlines(keepends=True)
        parsed = [json.loads(row) for row in rows]
        if any(type(item) is not dict or canonical(item) != row for item, row in zip(parsed, rows)):
            raise ValueError("noncanonical event")
        relevant = [item for item in parsed if item.get("orchestrator_task_id") == task.id]
    except (OSError, ValueError, TypeError) as exc:
        raise ResumeBlockedError("mission event lifecycle is missing or invalid") from exc
    if (
        kinds != expected[task.status][0]
        or [item.get("state") for item in relevant] != expected[task.status][1]
        or any(
            item.get("task_id") != mission_id or item.get("agent_id") != role for item in relevant
        )
    ):
        raise ResumeBlockedError("persisted task lifecycle and audit do not agree")


def _source_hashes() -> dict[str, str]:
    # A conservative source snapshot covers imported internal modules, not
    # third-party wheel bytes or the operating system. Never traverse data/.
    roots = ("core", "l2_memory", "l4_planning", "manager", "trading")
    files = [REPOSITORY / "src/agicore/__init__.py"]
    for root in roots:
        files.extend((REPOSITORY / "src/agicore" / root).rglob("*.py"))
    files.extend((REPOSITORY / "tools").glob("*.py"))
    result = {}
    for path in sorted(files):
        relative = path.relative_to(REPOSITORY)
        if "data" in relative.parts or path.is_symlink() or not path.is_file():
            raise ResumeBlockedError("invalid source snapshot path")
        with path.open("rb") as source:
            result[str(relative)] = hashlib.file_digest(source, "sha256").hexdigest()
    return result


def _runtime_versions() -> dict[str, str]:
    return {name: version(name) for name in ("SQLAlchemy", "pydantic", "structlog")}


def _event(root: Path, task_id: str, agent_id: str, state: str, **details: object) -> None:
    record = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "task_id": task_id,
        "agent_id": agent_id,
        "state": state,
        **details,
    }
    fd = os.open(
        root / "events.jsonl", os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o600
    )
    with os.fdopen(fd, "ab") as output:
        info = os.fstat(output.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ResumeBlockedError("invalid mission event file")
        output.write(canonical(record))
        output.flush()
        os.fsync(output.fileno())


def _final_event(root: Path, task_id: str, status: str, error: str | None, *, create: bool) -> bool:
    """Record or validate one terminal manager event, including after a crash."""
    try:
        raw = _read_regular(root / "events.jsonl")
        lines = raw.splitlines(keepends=True)
        rows = [json.loads(line) for line in lines]
        if any(type(row) is not dict or canonical(row) != line for row, line in zip(rows, lines)):
            raise ValueError("noncanonical event")
    except (OSError, ValueError, TypeError) as exc:
        raise ResumeBlockedError("invalid terminal event log") from exc
    outcomes = [
        row
        for row in rows
        if row.get("agent_id") == "manager"
        and row.get("task_id") == task_id
        and row.get("state") in ("PASS", "FAILED")
    ]
    if outcomes:
        if (
            len(outcomes) != 1
            or outcomes[0].get("state") != status
            or outcomes[0].get("error") != error
        ):
            raise ResumeBlockedError("contradictory terminal events")
    elif create:
        _event(root, task_id, "manager", status, error=error)
        return True
    else:
        raise ResumeBlockedError("terminal manager event is missing")
    return False


def _bind_event_checkpoint(root: Path, role: str, *, create: bool) -> dict:
    """Anchor event bytes in SQLite at each durable completed-task checkpoint."""
    database = root / "orchestrator.sqlite3"
    if database.is_symlink() or not database.is_file():
        raise ResumeBlockedError("invalid orchestration database")
    with sqlite3.connect(database.as_uri() + "?mode=rw", uri=True) as connection:
        if create:
            checkpoint = _event_prefix(root)
            connection.execute(
                "INSERT INTO mission_event_binding VALUES (?, ?, ?)",
                (role, checkpoint["bytes"], checkpoint["sha256"]),
            )
        else:
            row = connection.execute(
                "SELECT byte_count, sha256 FROM mission_event_binding WHERE role = ?", (role,)
            ).fetchone()
            if row is None:
                raise ResumeBlockedError("missing durable event checkpoint")
            checkpoint = _event_prefix(root, row[0])
            if checkpoint["sha256"] != row[1]:
                raise ResumeBlockedError("event log changed after checkpoint")
            if role == "manager_final" and checkpoint != _event_prefix(root):
                raise ResumeBlockedError("event log changed after final checkpoint")
    return checkpoint


def _store_outcome(root: Path, role: str, outcome: dict) -> None:
    """Write the subprocess result separately before the task can complete."""
    with (root / f"{role}.outcome.json").open("xb") as stream:
        stream.write(canonical(outcome))
        stream.flush()
        os.fsync(stream.fileno())


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
    root: Path,
    module: str,
    role: str,
    observations: int,
    timeout: int,
    stage: str,
    profile: str = "standard",
) -> dict:
    """Run one allowlisted process and collect its own wait4 resource usage."""
    if module not in (WORKER, VERIFIER):
        raise ValueError("unregistered mission adapter")
    if threading.active_count() != 1:
        raise RuntimeError("the supervisor must be single-threaded while launching an adapter")
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
    if profile != "standard":
        command.extend(("--profile", profile))

    supervisor_pid = os.getpid()

    def limits() -> None:
        # Linux sends SIGKILL to this direct child if its supervisor dies.
        # Check the race where the parent exited before prctl was installed.
        libc = ctypes.CDLL(None, use_errno=True)
        if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0:  # PR_SET_PDEATHSIG
            raise OSError(ctypes.get_errno(), "cannot bind child lifetime to supervisor")
        if os.getppid() != supervisor_pid:
            os.kill(os.getpid(), signal.SIGKILL)
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
            preexec_fn=limits,  # noqa: PLW1509 - guarded single-threaded supervisor
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
    profile: str = "standard",
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
    if stage not in ("events", "pullback", "confirmation"):
        raise ValueError("unsupported replay stage")
    if profile not in ("standard", *PROFILES):
        raise ValueError("unsupported invented profile")
    if profile != "standard" and (stage != "confirmation" or observations != FIXTURE_OBSERVATIONS):
        raise ValueError("confirmation profiles require confirmation and 39 observations")
    sources = _source_hashes()
    root = _new_directory(output_dir)
    task_id = str(uuid.uuid4())
    mission = {
        "schema": "agicore:mission:v2",
        "task_id": task_id,
        "kind": "INVENTED_STORAGE_AND_REPLAY",
        "observations": observations,
        "stage": stage,
        "profile": profile,
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
            "pullback": stage in ("pullback", "confirmation"),
            "confirmation": stage == "confirmation",
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
        "runtime_packages": _runtime_versions(),
    }
    _validate_mission(mission)
    with _mission_lock(root, create=True):
        with (root / "mission.json").open("xb") as stream:
            stream.write(canonical(mission))
            stream.flush()
            os.fsync(stream.fileno())
        _event(root, task_id, "manager", "CREATED")
        return _execute_mission(root, mission, resume=False)


def resume_mission(output_dir: Path) -> dict:
    """Resume only from durable completed/pending checkpoints; never guess."""
    if sys.platform != "linux":
        raise RuntimeError("the bounded subprocess implementation requires Linux")
    root = _existing_directory(output_dir)
    with _mission_lock(root):
        try:
            mission, _ = _json_evidence(root / "mission.json")
        except OSError as exc:
            raise ResumeBlockedError("missing or inaccessible mission contract") from exc
        _validate_mission(mission)
        return _execute_mission(root, mission, resume=True)


def _execute_mission(root: Path, mission: dict, *, resume: bool) -> dict:
    task_id = mission["task_id"]
    observations = mission["observations"]
    stage = mission["stage"]
    profile = mission["profile"]
    timeout_seconds = mission["timeout_seconds_per_process"]
    sources = mission["source_sha256"]
    contract_sha = hashlib.sha256(canonical(mission)).hexdigest()
    steps = {}
    tasks = {}
    status = "FAILED"
    error = None
    engine = None
    if resume:
        _bound_database(root, task_id, contract_sha)
    try:
        engine = SqlAlchemyEngine(f"sqlite:///{root / 'orchestrator.sqlite3'}")
        if not resume:
            init_schema(engine)
            with engine.engine.begin() as connection:
                connection.exec_driver_sql(
                    "CREATE TABLE mission_contract_binding "
                    "(mission_id TEXT PRIMARY KEY, contract_sha256 TEXT NOT NULL)"
                )
                connection.exec_driver_sql(
                    "INSERT INTO mission_contract_binding VALUES (?, ?)", (task_id, contract_sha)
                )
                connection.exec_driver_sql(
                    "CREATE TABLE mission_event_binding "
                    "(role TEXT PRIMARY KEY, byte_count INTEGER NOT NULL, sha256 TEXT NOT NULL)"
                )
            _checkpoint("contract_bound")
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
                except Exception as exc:  # noqa: BLE001 - fail closed on any audit failure
                    trace_errors.append(str(exc))
            try:
                _event(root, task_id, role, states[event.event_type], **details)
            except (OSError, ResumeBlockedError) as exc:
                trace_errors.append(str(exc))

        bus.subscribe("*", trace)
        payload = {
            "mission_id": task_id,
            "observations": observations,
            "stage": stage,
            "profile": profile,
            "timeout_seconds": timeout_seconds,
            "contract_sha256": contract_sha,
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
                    or type(task.payload) is not dict
                    or canonical(task.payload) != canonical(payload)
                ):
                    raise PermissionError("task exceeds the synthetic mission contract")
                if profile == "standard":
                    outcome = _run_process(root, module, role, observations, timeout_seconds, stage)
                else:
                    outcome = _run_process(
                        root, module, role, observations, timeout_seconds, stage, profile
                    )
                steps[role] = outcome
                if (
                    type(outcome.get("exit_code")) is not int
                    or outcome["exit_code"] != 0
                    or outcome.get("timeout") is not False
                ):
                    raise RuntimeError(f"{role} failed; inspect {outcome['stderr']}")
                outcome["contract_sha256"] = contract_sha
                try:
                    outcome["evidence"] = _seal_evidence(root, role, mission)
                    _store_outcome(root, role, outcome)
                except (OSError, ValueError, AttributeError, ResumeBlockedError) as exc:
                    raise RuntimeError(f"invalid verification receipt: {exc}") from exc
                return outcome

            registry.register(task_type, execute)
            return task_type, expected_id

        with engine.session() as session:
            present_ids = set(session.execute(select(Task.id)).scalars().all())
        if not present_ids <= set(roles):
            raise ResumeBlockedError("unexpected tasks in mission database")
        with engine.session() as session:
            existing = {tid: TaskRepository(session).get(tid) for tid in present_ids}
        worker_id, verifier_id = f"{task_id}-worker", f"{task_id}-verifier"
        report_path = root / "report.json"
        if (
            resume
            and (report_path.exists() or report_path.is_symlink())
            and (
                set(existing) != set(roles)
                or any(task.status != "completed" for task in existing.values())
            )
        ):
            raise ResumeBlockedError("existing report conflicts with noncompleted tasks")
        if verifier_id in existing and (
            worker_id not in existing or existing[worker_id].status != "completed"
        ):
            raise ResumeBlockedError("verifier exists before completed worker")

        for role, module in (("worker", WORKER), ("verifier", VERIFIER)):
            task_type, tid = register(role, module)
            previous = existing.get(tid)
            if previous is not None and (
                previous.task_type != task_type
                or previous.assigned_to != role
                or type(previous.payload) is not dict
                or canonical(previous.payload) != canonical(payload)
            ):
                raise ResumeBlockedError("persisted task does not match the mission contract")
            if resume and previous is not None:
                _validate_lifecycle(root, engine, previous, task_id, role)
            if previous is not None and previous.status == "completed":
                outcome = previous.result
                _bind_event_checkpoint(root, role, create=False)
                stored_outcome, _ = _json_evidence(root / f"{role}.outcome.json")
                if (
                    type(outcome) is not dict
                    or canonical(outcome) != canonical(stored_outcome)
                    or type(outcome.get("exit_code")) is not int
                    or outcome.get("exit_code") != 0
                    or outcome.get("timeout") is not False
                    or outcome.get("contract_sha256") != contract_sha
                    or canonical(outcome.get("evidence"))
                    != canonical(_seal_evidence(root, role, mission, outcome.get("evidence")))
                ):
                    raise ResumeBlockedError("completed task evidence or binding changed")
                steps[role] = outcome
                finished = previous
            else:
                if previous is not None and previous.status != "pending":
                    raise ResumeBlockedError("task state is running, failed or otherwise ambiguous")
                reserved = [
                    root / f"{role}.stdout",
                    root / f"{role}.stderr",
                    root / f"{role}.outcome.json",
                ]
                reserved.append(
                    root / "bundle" if role == "worker" else root / "bundle" / "verification.json"
                )
                if any(path.exists() or path.is_symlink() for path in reserved):
                    raise ResumeBlockedError("unstarted task has ambiguous existing output")
                if previous is None:
                    orchestrator.submit_task(
                        TaskCreate(
                            id=tid, task_type=task_type, assigned_to=role, payload=dict(payload)
                        )
                    )
                    _checkpoint(f"{role}_submitted")
                if trace_errors:
                    raise RuntimeError("task audit projection failed")
                finished = orchestrator.execute_one(tid)
                if finished.status == "completed":
                    _bind_event_checkpoint(root, role, create=True)
                _checkpoint(f"{role}_completed")
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
                or type(verification.get("observations")) is not int
                or verification.get("observations") != observations
                or verification.get("stage") != stage
                or worker.get("stage") != stage
                or verification.get("profile", "standard") != profile
                or worker.get("profile", "standard") != profile
                or verification.get("manifest_sha256") != worker.get("manifest_sha256")
                or verification.get("input_sha256") != worker.get("input_sha256")
                or canonical(verification.get("replay")) != canonical(worker.get("replay"))
            ):
                raise ValueError("invalid verification receipt")
            if _source_hashes() != sources:
                raise ValueError("mission sources changed during execution")
            status = "PASS"
    except ResumeBlockedError:
        raise
    except Exception as exc:
        if resume:
            raise ResumeBlockedError(f"resume failed safely: {type(exc).__name__}: {exc}") from exc
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
        "profile": profile,
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
            "Local hashes and runtime versions are not signatures or an operating-system sandbox.",
            "Child lifetime protection covers direct Linux children, not arbitrary descendants.",
            "The synchronous Linux supervisor must not start other threads while launching children.",
        ],
    }
    if status == "PASS":
        report["verification"] = verification
    report_path = root / "report.json"
    if report_path.exists() or report_path.is_symlink():
        if not resume:
            raise ResumeBlockedError("mission report already exists")
        _final_event(root, task_id, status, error, create=False)
        report["event_checkpoint"] = _bind_event_checkpoint(root, "manager_final", create=False)
        saved, _ = _json_evidence(report_path)
        if status != "PASS" or canonical(saved) != canonical(report):
            raise ResumeBlockedError("existing mission report does not match sealed evidence")
        return saved
    _checkpoint("before_report")
    created_final_event = _final_event(root, task_id, status, error, create=True)
    report["event_checkpoint"] = _bind_event_checkpoint(
        root, "manager_final", create=created_final_event
    )
    _checkpoint("after_report_event")
    _atomic_report(root, report)
    return report


def main() -> None:
    """Execute one local synthetic mission and print its report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--observations", type=int)
    parser.add_argument("--timeout-seconds", type=int)
    parser.add_argument("--stage", choices=("events", "pullback", "confirmation"))
    parser.add_argument("--profile", choices=("standard", *PROFILES))
    args = parser.parse_args()
    if args.resume and any(
        value is not None
        for value in (args.observations, args.timeout_seconds, args.stage, args.profile)
    ):
        parser.error("resume uses the sealed mission contract and accepts no overrides")
    with contextlib.redirect_stdout(sys.stderr):
        if args.resume:
            report = resume_mission(args.output_dir)
        else:
            report = run_mission(
                args.output_dir,
                DEFAULT_OBSERVATIONS if args.observations is None else args.observations,
                timeout_seconds=MAX_TIMEOUT_SECONDS
                if args.timeout_seconds is None
                else args.timeout_seconds,
                stage="pullback" if args.stage is None else args.stage,
                profile="standard" if args.profile is None else args.profile,
            )
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
