"""Explicit, source-bound G2B contract for named invented observations only."""

from __future__ import annotations

import re
from pathlib import Path

from .ema_pullback_v2_storage_format import (
    ROOT,
    canonical,
    parse_canonical,
    regular_read,
    require,
    sha,
)

CONTRACT_PATH = ROOT / "docs/evidence/EMA_PULLBACK_V2_G2B_SYNTHETIC_CONTRACT_V1.json"
SCHEMA = "agicore:optimized-synthetic-contract:v1"
RUNNER_SHA256 = "854a6cbe7b89f3c6f0e9f49a8a5095745baf20693c2e89b115dfcadbfacbdf56"
STRATEGY_SHA256 = "965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a"
PROTOCOL_SHA256 = "68dc6e6409aea4efb88e4a19e09a7ba17a68043a79f14ec23e569d3353267402"
FIXTURE_REGISTRATION_SHA256 = "60038227f5b57bf777149fad00e37ce764fc77169c5d26443aeeda664b98a714"
SCALE_201_SHA256 = "878a37c771595d1d98c6c9b20e6933137ddcf099a9e0be0b125aa9b13fac7a12"
MAX_OBSERVATIONS = 201
MAX_LOGICAL_BYTES = 33_554_432


def _source_files_match(entries: list, *, root: Path = ROOT) -> None:
    """Reject unbound, aliased, missing or altered registered source files."""
    require(type(entries) is list and entries, "G2B source closure")
    names = []
    for entry in entries:
        require(type(entry) is dict and set(entry) == {"path", "sha256"}, "G2B source entry")
        name = entry["path"]
        require(type(name) is str, "G2B source path")
        path = Path(name)
        require(
            not path.is_absolute()
            and path.suffix == ".py"
            and all(part not in (".", "..", "data") for part in path.parts),
            "G2B source path boundary",
        )
        digest = entry["sha256"]
        require(type(digest) is str and re.fullmatch(r"[0-9a-f]{64}", digest), "G2B source SHA")
        require(sha(regular_read(root / path, limit=4_194_304)) == digest, "G2B source drift")
        names.append(name)
    require(names == sorted(set(names)), "G2B source order/duplicates")


def load_contract(expected_sha256: str) -> dict:
    """Verify an externally precommitted contract and every declared source byte."""
    require(
        type(expected_sha256) is str and re.fullmatch(r"[0-9a-f]{64}", expected_sha256),
        "G2B external contract identity",
    )
    raw = regular_read(CONTRACT_PATH, limit=2_097_152)
    require(sha(raw) == expected_sha256, "G2B external contract mismatch")
    contract = parse_canonical([raw], limit=2_097_152)
    require(contract["schema"] == SCHEMA, "G2B contract schema")
    require(
        contract["runner_sha256"] == RUNNER_SHA256
        and contract["strategy_manifest_sha256"] == STRATEGY_SHA256
        and contract["development_protocol_sha256"] == PROTOCOL_SHA256
        and contract["historical_fixture_registration_sha256"] == FIXTURE_REGISTRATION_SHA256,
        "G2B frozen identities",
    )
    require(
        contract["maximum_observations"] == MAX_OBSERVATIONS
        and contract["maximum_logical_bytes"] == MAX_LOGICAL_BYTES
        and contract["input_domain"] == "INVENTED_ONLY"
        and contract["real_execution_authorized"] is False
        and contract["resource_caps"]
        == {
            "address_space_bytes": 536_870_912,
            "file_bytes": 268_435_456,
            "worker_wall_seconds": 60,
        },
        "G2B limits",
    )
    sources = contract["source_closure"]
    require(sha(canonical(sources)) == contract["source_closure_sha256"], "G2B closure digest")
    _source_files_match(sources)
    source_map = {entry["path"]: entry["sha256"] for entry in sources}
    required = {
        "src/agicore/trading/ema_pullback_v2_g2b_contract.py",
        "src/agicore/trading/ema_pullback_v2_recovery_optimized.py",
        "src/agicore/trading/ema_pullback_v2_recovery_indicators.py",
        "src/agicore/trading/ema_pullback_v2_recovery_lifecycle.py",
        "src/agicore/trading/ema_pullback_v2_recovery_accounting.py",
        "src/agicore/trading/ema_pullback_v2_recovery_evidence.py",
        "src/agicore/trading/ema_pullback_v2_recovery_storage.py",
        "src/agicore/trading/ema_pullback_v2_recovery_storage_verifier.py",
        "src/agicore/trading/ema_pullback_v2_storage_audit.py",
        "src/agicore/trading/ema_pullback_v2_storage_format.py",
        "tools/ema_pullback_v2_g2b_synthetic.py",
    }
    require(
        required <= source_map.keys()
        and source_map.get("src/agicore/trading/ema_pullback_v2_recovery_optimized.py")
        == RUNNER_SHA256
        and all(
            contract[role]["path"] in source_map
            and source_map[contract[role]["path"]] == contract[role]["sha256"]
            for role in ("producer", "storage", "verifier", "auditor")
        ),
        "G2B implementation identities",
    )
    fixtures = contract["fixtures"]
    require(type(fixtures) is dict and fixtures, "G2B invented fixtures")
    return contract


def fixture_spec(contract: dict, name: str) -> dict:
    """Resolve one explicitly registered synthetic input identity."""
    require(type(name) is str and name in contract["fixtures"], "G2B unknown fixture")
    spec = contract["fixtures"][name]
    require(
        type(spec) is dict
        and set(spec) == {"input_sha256", "observations", "generator"}
        and type(spec["observations"]) is int
        and 2 <= spec["observations"] <= MAX_OBSERVATIONS
        and type(spec["input_sha256"]) is str
        and re.fullmatch(r"[0-9a-f]{64}", spec["input_sha256"]),
        "G2B fixture specification",
    )
    if spec["generator"] == "HISTORICAL_PRECOMMITTED_FIXTURE":
        path = ROOT / "docs/evidence/EMA_PULLBACK_V2_RECOVERY_STORAGE_FIXTURE_REGISTRATION_V1.json"
        raw = regular_read(path, limit=2_097_152)
        require(sha(raw) == FIXTURE_REGISTRATION_SHA256, "historical fixture registration drift")
        inventory = parse_canonical([raw], limit=2_097_152)
        require(
            any(
                row["id"] == name
                and row["raw_sha256"] == spec["input_sha256"]
                and row["observations"] == spec["observations"]
                for row in inventory["native_fixtures"]
            ),
            "G2B fixture is not historically registered",
        )
    else:
        require(
            name == "invented-scale-201-v1"
            and spec["generator"] == "INVENTED_OHLCV_MINUTE_V1"
            and spec["input_sha256"] == SCALE_201_SHA256
            and spec["observations"] == 201,
            "G2B generator not authorized",
        )
    return spec


def generate_fixture(contract: dict, name: str) -> bytes:
    """Generate registered observations internally; external input is not accepted."""
    spec = fixture_spec(contract, name)
    if spec["generator"] == "HISTORICAL_PRECOMMITTED_FIXTURE":
        from tests.unit.trading.v2_recovery_storage_fixtures import synthetic_raw

        raw = synthetic_raw(name)
    else:
        require(
            name == "invented-scale-201-v1"
            and spec["generator"] == "INVENTED_OHLCV_MINUTE_V1"
            and spec["input_sha256"] == SCALE_201_SHA256
            and spec["observations"] == 201,
            "G2B generator not authorized",
        )
        from tools.agicore_v2_synthetic_scale_probe import generate_observations

        raw = generate_observations(201)
    require(
        sha(raw) == spec["input_sha256"] and len(raw.splitlines()) == spec["observations"],
        "G2B input drift",
    )
    return raw
