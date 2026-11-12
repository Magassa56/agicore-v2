"""Supervised V5 verifier CLI; stdout is exactly one canonical UTF-8 receipt, never a log."""

import argparse
import os
import sys
from pathlib import Path

from agicore.trading.ema_pullback_v2_g2c_verifier_v5 import V4_SHA, load_registration, verify_bundle
from agicore.trading.ema_pullback_v2_storage_format import canonical, require


def _worker_limits(args, contract):
    """Use the V4 supervisor gates and require its exact process limits, before opening a bundle."""
    import resource
    from tools.ema_pullback_v2_g2c_supervisor import _require_gate, preflight

    require(args.fixture in contract["fixtures"], "unregistered worker fixture")
    tier = contract["fixtures"][args.fixture]["observations"]
    caps = contract["tiers"][str(tier)]
    require(os.getsid(0) == os.getpid(), "supervised verifier process group")
    for key, cap in (
        (resource.RLIMIT_AS, "address_space_bytes"),
        (resource.RLIMIT_CPU, "cpu_seconds"),
        (resource.RLIMIT_FSIZE, "file_bytes"),
    ):
        require(resource.getrlimit(key) == (caps[cap], caps[cap]), "supervised verifier limits")
    if tier == 5000:
        args.contract_sha256 = V4_SHA
        _require_gate(args, contract)
        preflight(
            caps,
            Path.cwd() / "g2c-worker-resource-check",
            require_cgroup_memory=True,
            cgroup_v4=True,
        )


def main() -> None:
    """Verify only; V5 sealing is explicit, exclusive and never runs a strategy."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--verifier-sha256", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--native-sha256", required=True)
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--gate-report", type=Path)
    parser.add_argument("--gate-sha256")
    parser.add_argument("--seal", action="store_true")
    args = parser.parse_args()
    contract = load_registration(args.verifier_sha256)
    _worker_limits(args, contract)
    sys.stdout.buffer.write(
        canonical(
            verify_bundle(
                args.bundle,
                expected_verifier_sha256=args.verifier_sha256,
                expected_manifest_sha256=args.manifest_sha256,
                expected_native_sha256=args.native_sha256,
                seal=args.seal,
                expected_fixture=args.fixture,
            )
        )
    )


if __name__ == "__main__":
    main()
