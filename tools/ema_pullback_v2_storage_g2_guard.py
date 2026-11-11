"""Final resource checks around the unchanged, registered storage proof supervisor.

The historical supervisor samples a running worker and preserves its own receipt.
A fast worker may exit between samples, so G2 must also enforce the final measured
peaks and account for the legacy receipt itself before accepting that receipt.
This guard is separately versioned; it does not change any historical source closure.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

from agicore.trading.ema_pullback_v2_storage_format import (
    ROOT,
    StorageProofError,
    canonical,
    codec_profile,
    immutable_write,
    sha,
)
from tools.ema_pullback_v2_storage_synthetic_proof import (
    footprint,
    supervise_one,
    verify_registration,
)

MAX_PROCESS_TREE_BYTES = 4_294_967_296
MAX_CASE_BYTES = 268_435_456
MAX_CASE_SECONDS = 60
REGISTRATION = (
    ROOT / "docs/evidence/EMA_PULLBACK_V2_RECOVERY_STORAGE_CI_PORTABLE_SOURCE_REGISTRATION_V1.json"
)
REGISTRATION_SHA256 = "37045900d919484f2e644a36a96f94efed597ddeb6ddd927779f1ef5525426e4"
RECEIPT_RESERVE = 1_048_576


def supervise_checked(
    command: list[str],
    destination: Path,
    timeout: float,
    output_limit: int,
    *,
    memory_limit: int = MAX_PROCESS_TREE_BYTES,
) -> dict:
    """Run the existing supervisor and reject final measurements over fixed caps.

    The supervisor's receipt and logs are retained on failure. The returned G2
    measurements cover the case directory and the three supervisor files, but
    not any subsequently exported or duplicated artifacts.

    The registered native worker used below does not spawn child workers. The
    legacy peak sums that worker and supervisor; it is not a generic descendant
    process-tree measurement or a hard real-time storage quota.
    """
    if (
        type(timeout) not in (int, float)
        or not math.isfinite(timeout)
        or not 0 < timeout <= MAX_CASE_SECONDS
        or type(output_limit) is not int
        or not 0 < output_limit <= MAX_CASE_BYTES
        or type(memory_limit) is not int
        or not 0 < memory_limit <= MAX_PROCESS_TREE_BYTES
    ):
        raise StorageProofError("invalid G2 supervision limits")

    start = time.perf_counter_ns()
    legacy = supervise_one(command, destination, timeout, output_limit)
    elapsed_ns = time.perf_counter_ns() - start
    siblings = (
        destination.parent / (destination.name + ".log"),
        destination.parent / (destination.name + ".supervision.jsonl"),
        destination.parent / (destination.name + ".receipt.json"),
    )
    physical = footprint(destination) + sum(footprint(path) for path in siblings)
    peak = legacy["peak_process_tree_memory_bytes"]
    if type(peak) is not int or peak < 0:
        raise StorageProofError("invalid final process memory measurement")
    if physical > output_limit:
        raise StorageProofError("final case storage limit exceeded")
    if peak > memory_limit:
        raise StorageProofError("final process memory limit exceeded")
    if elapsed_ns > timeout * 1_000_000_000:
        raise StorageProofError("final case elapsed time limit exceeded")
    return {
        "legacy_receipt": legacy,
        "g2_final_physical_bytes_including_receipt": physical,
        "g2_supervisor_wall_ns": elapsed_ns,
        "g2_final_peak_process_tree_memory_bytes": peak,
    }


def run_precommitted_native(destination: Path, fixture: str, *, formal: bool = True) -> dict:
    """Run one registered invented native case, retaining a distinct G2 receipt."""
    if type(formal) is not bool or type(fixture) is not str:
        raise StorageProofError("invalid G2 worker parameters")
    destination = destination.absolute()
    if (
        "data" in destination.parts
        or destination.exists()
        or any(path.is_symlink() for path in (destination, *destination.parents))
        or not destination.parent.is_dir()
    ):
        raise StorageProofError("invalid G2 output destination")
    g2_receipt = destination.parent / (destination.name + ".g2-receipt.json")
    if g2_receipt.exists() or g2_receipt.is_symlink():
        raise StorageProofError("G2 receipt already exists")
    if sha(REGISTRATION.read_bytes()) != REGISTRATION_SHA256:
        raise StorageProofError("G2 source registration identity changed")
    registration, inventory = verify_registration(REGISTRATION, formal=formal)
    if fixture not in {entry["id"] for entry in inventory["native_fixtures"]}:
        raise StorageProofError("fixture is not precommitted")
    limits = inventory["limits"]
    if (
        limits["memory_cap_bytes"] != MAX_PROCESS_TREE_BYTES
        or limits["synthetic_case_output_bytes"] != MAX_CASE_BYTES
        or limits["wall_seconds_per_native_case"] != MAX_CASE_SECONDS
    ):
        raise StorageProofError("precommitted limits changed")
    command = [
        sys.executable,
        "-B",
        "-m",
        "tools.ema_pullback_v2_storage_synthetic_proof",
        "--registration",
        str(REGISTRATION),
        "--destination",
        str(destination),
        "--worker",
        "native",
        "--fixture",
        fixture,
    ]
    if formal:
        command.append("--formal")
    checked = supervise_checked(
        command, destination, MAX_CASE_SECONDS, MAX_CASE_BYTES - RECEIPT_RESERVE
    )
    legacy_path = destination.parent / (destination.name + ".receipt.json")
    report = {
        "schema": "agicore:synthetic-storage-g2-supervision:v1",
        "status": "MEASURED_BEFORE_RECEIPT",
        "fixture": fixture,
        "codec_scope": "FORMAL_PRECOMMITTED" if formal else "PORTABLE_NONFORMAL",
        "codec_profile_sha256": sha(canonical(codec_profile())),
        "source_registration_sha256": REGISTRATION_SHA256,
        "complete_source_closure_sha256": registration["complete_source_closure_sha256"],
        "verifier_source_closure_sha256": registration["verifier_source_closure_sha256"],
        "g2_guard_sha256": sha(Path(__file__).read_bytes()),
        "legacy_supervision_receipt_sha256": sha(legacy_path.read_bytes()),
        "native_sha256": checked["legacy_receipt"]["result"]["reference_native_sha256"],
        "observations": checked["legacy_receipt"]["result"]["observations"],
        "final_peak_process_tree_memory_bytes": checked["g2_final_peak_process_tree_memory_bytes"],
        "supervisor_wall_ns": checked["g2_supervisor_wall_ns"],
        "physical_bytes_before_g2_receipt": checked["g2_final_physical_bytes_including_receipt"],
        "physical_cap_bytes": MAX_CASE_BYTES,
        "g2_receipt_reserved_bytes": RECEIPT_RESERVE,
    }
    immutable_write(g2_receipt, canonical(report))
    receipt_physical = footprint(g2_receipt)
    if receipt_physical > RECEIPT_RESERVE:
        raise StorageProofError("G2 receipt exceeds reserved storage")
    return {
        **checked,
        "g2_receipt": report,
        "g2_status": "PASS",
        "g2_total_physical_bytes": (
            checked["g2_final_physical_bytes_including_receipt"] + receipt_physical
        ),
    }


def main() -> None:
    """Run a named, invented native proof without accepting external source bytes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--portable", action="store_true")
    args = parser.parse_args()
    checked = run_precommitted_native(args.destination, args.fixture, formal=not args.portable)
    print(
        json.dumps(
            {
                "status": checked["g2_status"],
                "total_physical_bytes": checked["g2_total_physical_bytes"],
                "receipt": checked["g2_receipt"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
