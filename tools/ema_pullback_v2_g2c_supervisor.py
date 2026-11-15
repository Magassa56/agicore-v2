"""Supervise precommitted invented-only G2C runs with finite Linux limits.

Disk totals are sampled and checked on exit, not a filesystem quota. Each child
gets its own process group, CPU/address-space/per-file rlimits and wall deadline.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import resource
import shutil
import signal
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from agicore.trading.ema_pullback_v2_g2c_scaling import load_contract
from agicore.trading.ema_pullback_v2_storage_format import (
    canonical,
    immutable_write,
    regular_read,
    sha,
)


def _utc() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _memory_available() -> int:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) * 1024
    raise RuntimeError("MemAvailable unavailable")


def _physical_size(directory: Path) -> int:
    total = 0
    for root, directories, files in os.walk(directory, followlinks=False):
        for name in (*directories, *files):
            path = Path(root) / name
            if path.is_symlink():
                raise RuntimeError("symlink in supervised output")
            if path.is_file():
                total += path.stat().st_blocks * 512
    return total


def _stop_group(pid: int) -> None:
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def run_worker(command: list[str], folder: Path, caps: dict, *, root: Path) -> tuple[dict, dict]:
    """Run a new process group; preserve logs and reject all resource overruns."""
    folder.mkdir(parents=True, exist_ok=False)
    stdout_path, stderr_path = folder / "stdout.log", folder / "stderr.log"
    started = time.monotonic_ns()
    reason = None
    prlimit = shutil.which("prlimit")
    if not prlimit:
        raise RuntimeError("prlimit unavailable: child limits cannot be enforced")
    limited_command = [
        prlimit,
        f"--as={caps['address_space_bytes']}",
        f"--cpu={caps['cpu_seconds']}",
        f"--fsize={caps['file_bytes']}",
        "--",
        *command,
    ]
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        process = subprocess.Popen(
            limited_command,
            cwd=root,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": "src:."},
        )
        while True:
            pid, status, usage = os.wait4(process.pid, os.WNOHANG)
            if pid:
                process.returncode = os.waitstatus_to_exitcode(status)
                break
            elapsed = (time.monotonic_ns() - started) / 1_000_000_000
            if elapsed > caps["wall_seconds"]:
                reason = "WALL_LIMIT"
            elif _physical_size(folder) > caps["physical_bytes"]:
                reason = "SAMPLED_PHYSICAL_LIMIT"
            if reason:
                _stop_group(process.pid)
                _, status, usage = os.wait4(process.pid, 0)
                process.returncode = os.waitstatus_to_exitcode(status)
                break
            time.sleep(0.1)
        _stop_group(process.pid)
    wall = (time.monotonic_ns() - started) / 1_000_000_000
    physical = _physical_size(folder)
    cpu = usage.ru_utime + usage.ru_stime
    peak_rss = usage.ru_maxrss * 1024
    if physical + 1_048_576 > caps["physical_bytes"]:
        reason = "FINAL_PHYSICAL_LIMIT"
    elif wall > caps["wall_seconds"]:
        reason = reason or "WALL_LIMIT"
    elif cpu > caps["cpu_seconds"]:
        reason = reason or "CPU_LIMIT"
    elif peak_rss > caps["address_space_bytes"]:
        reason = reason or "RSS_OVER_ADDRESS_LIMIT"
    elif process.returncode != 0:
        reason = reason or "WORKER_FAILED"
    report = {
        "status": "PASS" if reason is None else "FAIL",
        "reason": reason,
        "exit_code": process.returncode,
        "wall_ns": int(wall * 1_000_000_000),
        "cpu_ns": int(cpu * 1_000_000_000),
        "peak_rss_bytes": peak_rss,
        "physical_bytes": physical,
        "address_space_limit_bytes": caps["address_space_bytes"],
        "cpu_limit_seconds": caps["cpu_seconds"],
        "wall_limit_seconds": caps["wall_seconds"],
        "file_limit_bytes": caps["file_bytes"],
        "physical_limit_bytes": caps["physical_bytes"],
        "disk_control": "SAMPLED_AND_FINAL_NOT_A_REAL_TIME_FILESYSTEM_QUOTA",
    }
    immutable_write(folder / "supervisor.json", canonical(report))
    if report["status"] != "PASS":
        return report, {}
    try:
        result = json.loads(stdout_path.read_bytes())
    except (ValueError, OSError) as exc:
        report["status"], report["reason"] = "FAIL", "INVALID_WORKER_OUTPUT"
        raise RuntimeError("worker did not produce one JSON result") from exc
    return report, result


def _process_running(pid: int) -> bool:
    try:
        return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].strip().split()[0] != "Z"
    except (FileNotFoundError, ProcessLookupError):
        return False


def supervision_selfcheck(destination: Path, caps: dict, *, root: Path) -> dict:
    """Prove that a timed-out worker and its ordinary descendant both stop."""
    probe_caps = dict(caps, wall_seconds=2, cpu_seconds=3)
    code = (
        "import json,resource,subprocess,sys,time; "
        "p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)']); "
        "print(json.dumps({'pid':p.pid,'limits':[resource.getrlimit(resource.RLIMIT_AS)[0],"
        "resource.getrlimit(resource.RLIMIT_CPU)[0],resource.getrlimit(resource.RLIMIT_FSIZE)[0]]}),"
        "flush=True); time.sleep(60)"
    )
    metrics, _ = run_worker([sys.executable, "-B", "-c", code], destination, probe_caps, root=root)
    observed = json.loads((destination / "stdout.log").read_text())
    child = observed["pid"]
    for _ in range(20):
        if not _process_running(child):
            break
        time.sleep(0.05)
    if (
        metrics["reason"] != "WALL_LIMIT"
        or _process_running(child)
        or observed["limits"]
        != [probe_caps["address_space_bytes"], probe_caps["cpu_seconds"], probe_caps["file_bytes"]]
    ):
        raise RuntimeError("process-group descendant termination selfcheck failed")
    return {
        "status": "PASS",
        "worker_and_descendant_stopped": True,
        "elapsed_wall_ns": metrics["wall_ns"],
    }


def _cgroup_memory(
    *, membership_path: Path = Path("/proc/self/cgroup"), root: Path = Path("/sys/fs/cgroup")
) -> dict | None:
    """Read the visible cgroup root only when it is this process's own group.

    Nested memberships are unsupported: the mount root could conceal a stricter
    child limit, so absence or ambiguity must block the larger tier.
    """
    try:
        if membership_path.read_text().splitlines() != ["0::/"]:
            return None
        limit_path, current_path = root / "memory.max", root / "memory.current"
        if not limit_path.is_file() or not current_path.is_file():
            return None
        text = limit_path.read_text().strip()
        limit = None if text == "max" else int(text)
        current = int(current_path.read_text().strip())
        if current < 0 or (limit is not None and limit < 0):
            return None
        return {"limit_bytes": limit, "current_bytes": current}
    except (OSError, ValueError):
        return None


def _cgroup_memory_v4(
    *,
    membership_path: Path = Path("/proc/self/cgroup"),
    namespace_path: Path = Path("/proc/self/ns/cgroup"),
    mountinfo_path: Path = Path("/proc/self/mountinfo"),
    root: Path = Path("/sys/fs/cgroup"),
) -> dict | None:
    """Fail closed unless the entire initial cgroup-v2 hierarchy is visible.

    Linux exposes memory.max/current only on non-root cgroups. Both hard and
    high limits on every ancestor contribute to the conservative headroom.
    """
    try:
        if os.readlink(namespace_path) != "cgroup:[4026531835]":
            return None
        lines = membership_path.read_text().splitlines()
        if len(lines) != 1 or not lines[0].startswith("0::/"):
            return None
        parts = lines[0][4:].split("/") if lines[0] != "0::/" else []
        if any(part in ("", ".", "..") for part in parts):
            return None
        mounts = []
        for line in mountinfo_path.read_text().splitlines():
            fields = line.split(" - ", 1)
            if len(fields) != 2 or fields[1].split()[0] != "cgroup2":
                continue
            before = fields[0].split()
            unescape = lambda value: re.sub(  # noqa: E731
                r"\\([0-7]{3})", lambda match: chr(int(match[1], 8)), value
            )
            if len(before) < 5:
                return None
            mountpoint = unescape(before[4])
            if mountpoint == str(root):
                mounts.append(unescape(before[3]))
        if mounts != ["/"] or "memory" not in (root / "cgroup.controllers").read_text().split():
            return None
        if root.is_symlink() or (root / "memory.max").exists():
            return None
        node = root
        directories = []
        for part in parts:
            node = node / part
            if node.is_symlink() or not node.is_dir():
                return None
            directories.append(node)
        ancestors = []
        finite = []
        cpus = []
        for directory in reversed(directories):
            current = int((directory / "memory.current").read_text().strip())
            if current < 0:
                return None
            values = {}
            for name in ("memory.max", "memory.high"):
                value = (directory / name).read_text().strip()
                limit = None if value == "max" else int(value)
                if limit is not None:
                    if limit < 0:
                        return None
                    finite.append((max(0, limit - current), limit, current))
                values[name] = limit
            cpu = (directory / "cpu.max").read_text().split()
            if len(cpu) != 2 or int(cpu[1]) <= 0:
                return None
            quota = None if cpu[0] == "max" else int(cpu[0])
            if quota is not None and quota <= 0:
                return None
            cpus.append({"quota": quota, "period": int(cpu[1])})
            ancestors.append(
                {
                    "group": "/" + str(directory.relative_to(root)),
                    "current_bytes": current,
                    "memory_max_bytes": values["memory.max"],
                    "memory_high_bytes": values["memory.high"],
                    "cpu_quota": quota,
                    "cpu_period": int(cpu[1]),
                }
            )
        _, limit, current = min(finite) if finite else (None, None, 0)
        return {
            "limit_bytes": limit,
            "current_bytes": current,
            "ancestors": ancestors,
            "root": "INITIAL_NAMESPACE_ROOT_NO_MEMORY_MAX",
            "cpu_limits": cpus,
        }
    except (OSError, ValueError, IndexError):
        return None


def preflight(
    caps: dict,
    destination: Path,
    *,
    require_cgroup_memory: bool = False,
    cgroup_v4: bool = False,
) -> dict:
    """Check observed host headroom and inherited Linux limits before a tier."""
    if sys.platform != "linux" or not Path("/proc/meminfo").is_file():
        raise RuntimeError("Linux resource supervision unavailable")
    memory = _memory_available()
    disk = shutil.disk_usage(destination.parent).free
    group = _cgroup_memory_v4() if cgroup_v4 else _cgroup_memory()
    if require_cgroup_memory and group is None:
        raise RuntimeError("effective cgroup memory limit is not observable")
    available = memory
    if group is not None and group["limit_bytes"] is not None:
        available = min(memory, max(0, group["limit_bytes"] - group["current_bytes"]))
    disk_budget = max(caps["physical_bytes"], caps.get("tier_physical_bytes", 0))
    if available < caps["address_space_bytes"] * 2 or disk < disk_budget * 2:
        raise RuntimeError("insufficient observed memory or storage headroom")
    if (
        cgroup_v4
        and group is not None
        and any(
            item["quota"] is not None
            and item["quota"] * caps["wall_seconds"] < item["period"] * caps["cpu_seconds"]
            for item in group["cpu_limits"]
        )
    ):
        raise RuntimeError("cgroup CPU quota cannot support the committed CPU/wall budget")
    for key, requested in (
        (resource.RLIMIT_AS, caps["address_space_bytes"]),
        (resource.RLIMIT_CPU, caps["cpu_seconds"]),
        (resource.RLIMIT_FSIZE, caps["file_bytes"]),
    ):
        _, hard = resource.getrlimit(key)
        if hard != resource.RLIM_INFINITY and hard < requested:
            raise RuntimeError("requested child limit exceeds inherited hard limit")
    return {
        "status": "PASS",
        "available_memory_bytes": memory,
        "available_effective_memory_bytes": available if group is not None else None,
        "free_disk_bytes": disk,
        "cgroup_memory": group,
        "cgroup_memory_limit_note": "NOT_VERIFIED_IF_NOT_VISIBLE",
        "limits": caps,
        "utc": _utc(),
    }


def _coverage(items: list[dict]) -> None:
    """Require the registered tier-one behavioral cases to be exercised."""
    by_name = {item["fixture"]: item for item in items}

    def counts(name):
        return by_name[name]["verification"]["metrics_counts"]

    dense = counts("dense-1000")
    if not (
        dense["long_entry_fills"] >= 2
        and dense["short_entry_fills"] >= 2
        and dense["structural_stop_exits"] >= 1
        and dense["ema20_exits"] >= 1
        and dense["risk_rejections"] >= 1
    ):
        raise RuntimeError("dense lifecycle coverage not demonstrated")
    if (
        counts("constant-1000")["long_entry_fills"] != 0
        or counts("constant-1000")["short_entry_fills"] != 0
        or counts("suppressed-long-1000")["suppressed_position_open_events"] < 1
        or counts("expired-short-1000")["expired_contexts"] < 1
        or counts("risk-reject-short-1000")["risk_rejections"] < 1
        or by_name["gap-stop-short-1000"]["verification"]["gap_stop_exits"] < 1
    ):
        raise RuntimeError("registered suppression, expiration, gap or risk coverage missing")


def _storage_sizes(bundle: Path) -> dict:
    manifest = json.loads((bundle / "manifest.json").read_bytes())
    streams = manifest["streams"]
    chunks = [
        chunk
        for stream in streams
        for page in stream["pages"]
        for segment in page["segments"]
        for chunk in segment["chunks"]
    ]
    return {
        "native_logical_bytes": streams[0]["logical_size_bytes"],
        "witness_logical_bytes": streams[1]["logical_size_bytes"],
        "fragment_count": len(chunks),
        "fragment_stored_bytes_sum": sum(c["stored_size_bytes"] for c in chunks),
        "fragment_decoded_bytes_sum": sum(c["uncompressed_size_bytes"] for c in chunks),
        "bundle_physical_bytes": _physical_size(bundle),
    }


def _require_gate(args, contract: dict) -> None:
    """Require an externally pinned, completely successful tier-one report."""
    if not args.gate_report or not args.gate_sha256:
        raise RuntimeError("5000 requires externally retained complete 1000 gate")
    path = args.gate_report.absolute()
    if "data" in path.parts or any(p.is_symlink() for p in (path, *path.parents)):
        raise RuntimeError("invalid 1000 gate path")
    raw = path.read_bytes()
    gate = json.loads(raw)
    items = gate.get("fixtures", [])
    expected_contract = args.contract_sha256
    if contract.get("schema") == "agicore:g2c-invented-scaling-contract:v4":
        predecessor = contract["predecessor"]
        expected_contract = predecessor["contract_sha256"]
        evidence = Path(__file__).resolve().parents[1] / "docs/evidence"
        negative = regular_read(
            evidence / "AGICORE_G2C_1000_9E6E_NEGATIVE_20261111.json", limit=2_097_152
        )
        bundles = regular_read(
            evidence / "AGICORE_G2C_1000_9E6E_BUNDLES_20261111.zip", limit=16_777_216
        )
        checks = json.loads(negative)
        cases = checks.get("results", [])
        if (
            args.gate_sha256 != predecessor["gate_report_sha256"]
            or sha(negative) != predecessor["negative_report_sha256"]
            or sha(bundles) != predecessor["bundles_sha256"]
            or checks.get("status") != "PASS"
            or checks.get("contract_sha256") != expected_contract
            or checks.get("tier_report_sha256") != args.gate_sha256
            or len(cases) != 36
            or sum(item.get("actual") == "PASS" for item in cases) != 6
            or sum(item.get("actual") == "REJECTED" for item in cases) != 30
        ):
            raise RuntimeError("historical 1000 negative evidence identity/status mismatch")
    if (
        sha(raw) != args.gate_sha256
        or gate.get("status") != "PASS"
        or gate.get("tier") != 1000
        or gate.get("contract_sha256") != expected_contract
        or [item["fixture"] for item in items] != contract["tier_fixtures"]["1000"]
        or any(
            item.get("parity", {}).get("status") != "PASS"
            or item.get("verification", {}).get("status") != "PASS"
            or len(item.get("runs", [])) != 5
            or any(run.get("status") != "PASS" for run in item["runs"])
            for item in items
        )
    ):
        raise RuntimeError("1000 gate identity/status/coverage mismatch")
    _coverage(items)


def _worker(args) -> None:
    from agicore.trading.ema_pullback_v2_g2c_scaling import (
        compare_reference,
        produce_bundle,
        verify_bundle,
    )

    contract = load_contract(args.contract_sha256)
    if args.fixture not in contract["fixtures"]:
        raise RuntimeError("worker fixture is not registered")
    tier = contract["fixtures"][args.fixture]["observations"]
    caps = contract["tiers"][str(tier)]
    if tier == 5000:
        _require_gate(args, contract)
        preflight(
            caps,
            Path.cwd() / "g2c-worker-resource-check",
            require_cgroup_memory=True,
            cgroup_v4=contract["schema"].endswith(":v4"),
        )
    for key, expected in (
        (resource.RLIMIT_AS, caps["address_space_bytes"]),
        (resource.RLIMIT_CPU, caps["cpu_seconds"]),
        (resource.RLIMIT_FSIZE, caps["file_bytes"]),
    ):
        if resource.getrlimit(key) != (expected, expected):
            raise RuntimeError("worker resource limit not applied")
    if os.getsid(0) != os.getpid():
        raise RuntimeError("worker is not isolated in a new process group")
    if args.worker == "produce":
        result = produce_bundle(
            args.bundle, args.fixture, expected_contract_sha256=args.contract_sha256
        )
    elif args.worker == "verify":
        result = verify_bundle(
            args.bundle,
            expected_contract_sha256=args.contract_sha256,
            expected_manifest_sha256=args.manifest_sha256,
            expected_native_sha256=args.native_sha256,
            seal=True,
        )
    else:
        result = compare_reference(args.fixture, expected_contract_sha256=args.contract_sha256)
    root = Path(__file__).resolve().parents[1]
    allowed = {item["path"] for item in contract["source_closure"]}
    loaded = set()
    for module in list(sys.modules.values()):
        name = getattr(module, "__file__", None)
        if name:
            path = Path(name).resolve()
            if path.suffix == ".py" and path.is_relative_to(root):
                loaded.add(str(path.relative_to(root)))
    if not loaded <= allowed:
        raise RuntimeError(f"unregistered loaded repository sources: {sorted(loaded - allowed)}")
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


def run_tier(args) -> int:
    """Run registered fixtures in order, stopping immediately on a failed gate."""
    contract = load_contract(args.contract_sha256)
    tier = str(args.tier)
    caps = contract["tiers"][tier]
    if args.tier == 5000:
        _require_gate(args, contract)
    destination = args.output.absolute()
    if (
        "data" in destination.parts
        or destination.exists()
        or any(p.is_symlink() for p in (destination, *destination.parents))
    ):
        raise RuntimeError("invalid or existing output path")
    destination.parent.mkdir(parents=True, exist_ok=True)
    ready = preflight(
        caps,
        destination,
        require_cgroup_memory=args.tier == 5000,
        cgroup_v4=contract["schema"].endswith(":v4"),
    )
    destination.mkdir()
    root = Path(__file__).resolve().parents[1]
    ready["process_group_selfcheck"] = supervision_selfcheck(
        destination / "supervision-selfcheck", caps, root=root
    )
    immutable_write(destination / "preflight.json", canonical(ready))
    summary = {
        "schema": "agicore:g2c-tier-report:v1",
        "status": "RUNNING",
        "tier": args.tier,
        "contract_sha256": args.contract_sha256,
        "fixtures": [],
        "started_utc": _utc(),
        "real_data_accessed": False,
        "oos_accessed": False,
        "resource_scope": "per child; disk sampling is not a kernel quota",
    }
    script = str(Path(__file__).resolve())
    gate_args = (
        ["--gate-report", str(args.gate_report), "--gate-sha256", args.gate_sha256]
        if args.tier == 5000
        else []
    )
    try:
        for fixture in contract["tier_fixtures"][tier]:
            item = {"fixture": fixture, "runs": []}
            summary["fixtures"].append(item)
            productions, verifications = [], []
            for repeat in (1, 2):
                run_dir = destination / f"{fixture}-{repeat}"
                bundle = run_dir / "bundle"
                command = [
                    sys.executable,
                    "-B",
                    script,
                    "--worker",
                    "produce",
                    "--fixture",
                    fixture,
                    "--contract-sha256",
                    args.contract_sha256,
                    "--bundle",
                    str(bundle),
                ] + gate_args
                metrics, production = run_worker(command, run_dir, caps, root=root)
                item["runs"].append({"role": "producer", "repeat": repeat, **metrics})
                if metrics["status"] != "PASS":
                    raise RuntimeError(f"{fixture} producer {repeat}: {metrics['reason']}")
                productions.append(production)
                verify_dir = destination / f"{fixture}-{repeat}-verify"
                command = [
                    sys.executable,
                    "-B",
                    script,
                    "--worker",
                    "verify",
                    "--fixture",
                    fixture,
                    "--bundle",
                    str(bundle),
                    "--contract-sha256",
                    args.contract_sha256,
                    "--manifest-sha256",
                    production["manifest_sha256"],
                    "--native-sha256",
                    production["native_sha256"],
                ] + gate_args
                metrics, verification = run_worker(command, verify_dir, caps, root=root)
                item["runs"].append({"role": "verifier", "repeat": repeat, **metrics})
                if metrics["status"] != "PASS" or verification.get("status") != "PASS":
                    raise RuntimeError(f"{fixture} verifier {repeat}: {metrics['reason']}")
                verifications.append(verification)
            if productions[0] != productions[1] or verifications[0] != verifications[1]:
                raise RuntimeError(f"{fixture} independent processes differ")
            item["production"] = productions[0]
            item["verification"] = verifications[0]
            item["storage"] = _storage_sizes(destination / f"{fixture}-1" / "bundle")
            parity_dir = destination / f"{fixture}-parity"
            command = [
                sys.executable,
                "-B",
                script,
                "--worker",
                "parity",
                "--fixture",
                fixture,
                "--contract-sha256",
                args.contract_sha256,
            ] + gate_args
            metrics, parity = run_worker(command, parity_dir, caps, root=root)
            item["runs"].append({"role": "parity", **metrics})
            if metrics["status"] != "PASS" or parity.get("status") != "PASS":
                raise RuntimeError(f"{fixture} reference parity not proven: {metrics['reason']}")
            if parity["optimized_native_sha256"] != productions[0]["native_sha256"]:
                raise RuntimeError(f"{fixture} parity/producer identity mismatch")
            item["parity"] = parity
            if _physical_size(destination) > caps["tier_physical_bytes"]:
                raise RuntimeError("tier aggregate physical limit exceeded")
        if args.tier == 1000:
            _coverage(summary["fixtures"])
        summary["status"] = "PASS"
    except Exception as exc:  # noqa: BLE001 -- retain first failure and never advance a tier
        summary["status"], summary["failure"] = "BLOCKED", str(exc)
    summary["physical_bytes_before_report"] = _physical_size(destination)
    if summary["physical_bytes_before_report"] + 1_048_576 > caps["tier_physical_bytes"]:
        summary["status"], summary["failure"] = "BLOCKED", "final tier physical limit exceeded"
    summary["ended_utc"] = _utc()
    immutable_write(destination / "tier_report.json", canonical(summary))
    print(
        json.dumps(
            {
                "status": summary["status"],
                "tier": args.tier,
                "report_sha256": sha(canonical(summary)),
                "failure": summary.get("failure"),
            },
            sort_keys=True,
        )
    )
    return 0 if summary["status"] == "PASS" else 1


def main() -> int:
    """Run one bounded synthetic tier or a supervisor-owned isolated worker."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=("produce", "verify", "parity"))
    parser.add_argument("--tier", type=int, choices=(1000, 5000))
    parser.add_argument("--contract-sha256", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fixture")
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--manifest-sha256")
    parser.add_argument("--native-sha256")
    parser.add_argument("--gate-report", type=Path)
    parser.add_argument("--gate-sha256")
    args = parser.parse_args()
    if args.worker:
        _worker(args)
        return 0
    if args.tier is None or args.output is None:
        parser.error("a tier and a new output directory are required")
    return run_tier(args)


if __name__ == "__main__":
    raise SystemExit(main())
