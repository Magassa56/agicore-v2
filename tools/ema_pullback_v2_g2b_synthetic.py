"""Separate invented-only producer and verifier for the versioned G2B contract.

Supply a trusted contract digest and externally retained manifest/native digests.
Use an external wall-time supervisor; this CLI enforces address-space and file caps.
"""

from __future__ import annotations

import argparse
import json
import resource
from pathlib import Path


def main() -> None:
    """Run one bounded role; no external market input or broker is accepted."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=("produce", "verify"), required=True)
    parser.add_argument("--contract-sha256", required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--fixture")
    parser.add_argument("--manifest-sha256")
    parser.add_argument("--native-sha256")
    parser.add_argument("--seal", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (536_870_912, 536_870_912))
    resource.setrlimit(resource.RLIMIT_FSIZE, (268_435_456, 268_435_456))
    if args.role == "produce":
        if not args.fixture or args.manifest_sha256 or args.native_sha256 or args.seal:
            parser.error("produce requires only a named fixture, contract and new bundle")
        from agicore.trading.ema_pullback_v2_g2b_storage import produce_bundle

        receipt = produce_bundle(
            args.bundle, args.fixture, expected_contract_sha256=args.contract_sha256
        )
    else:
        if args.fixture or not args.manifest_sha256 or not args.native_sha256:
            parser.error("verify requires externally retained manifest and native digests")
        from agicore.trading.ema_pullback_v2_g2b_verifier import verify_bundle

        _, receipt = verify_bundle(
            args.bundle,
            expected_contract_sha256=args.contract_sha256,
            expected_manifest_sha256=args.manifest_sha256,
            expected_native_sha256=args.native_sha256,
            seal=args.seal,
        )
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
