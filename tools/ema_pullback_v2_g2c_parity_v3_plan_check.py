"""Validate the registered V3 5000 plan and fixtures without launching workers."""

from __future__ import annotations

import argparse
import re
import sys
from types import SimpleNamespace

from agicore.trading import ema_pullback_v2_development_replay as reference
from agicore.trading import ema_pullback_v2_g2c_scaling as scaling
from agicore.trading.ema_pullback_v2_storage_format import (
    ROOT,
    canonical,
    codec_profile,
    contracts,
    parse_canonical,
    regular_read,
    require,
    sha,
)
from tools import ema_pullback_v2_g2c_parity_v3 as v3
from tools import ema_pullback_v2_g2c_supervised_v51 as v51
from tools.ema_pullback_v2_g2c_supervisor import _require_gate

REGISTRATION_SHA = "cff5ae162ec68b03904b0f8fb18e8fb68c456ecc97214da500d41206fd195424"
WORKER_SHA = "655e1b28fe44f50ccc851f7ff5565c1f2126b51349aa54e91f9f144a35dd12a9"
PLAN_PATH = ROOT / "docs/evidence/AGICORE_G2C_PARITY_V3_5000_REGISTERED_PLAN_20261116.json"
LIMITS = {
    "address_space_bytes": 2 << 30,
    "cpu_seconds": 150,
    "file_bytes": 64 << 20,
    "logical_bytes": 256 << 20,
    "physical_bytes": 256 << 20,
    "tier_physical_bytes": 1 << 30,
    "wall_seconds": 240,
}
FIXTURES = ("constant-5000", "dense-5000")
ROLES = ["producer", "verifier", "producer", "verifier", "parity"]


def check_plan(expected_plan_sha256: str) -> dict:
    """Authenticate the pinned plan, frozen sources, historical gate and invented inputs."""
    require(
        type(expected_plan_sha256) is str
        and re.fullmatch(r"[0-9a-f]{64}", expected_plan_sha256) is not None,
        "external plan SHA required",
    )
    raw = regular_read(PLAN_PATH, limit=16384)
    packet = parse_canonical([raw], limit=16384)
    require(set(packet) == {"plan", "plan_sha256"}, "canonical plan envelope")
    plan = packet["plan"]
    require(
        packet["plan_sha256"] == expected_plan_sha256 == sha(canonical(plan))
        and plan == v3.plan(REGISTRATION_SHA, 5000),
        "external plan identity or regenerated plan mismatch",
    )
    v2_plan = plan["v2_plan"]
    previous = v2_plan["v51_plan"]
    contract = v3.load_registration(REGISTRATION_SHA)
    worker_sha = sha(regular_read(ROOT / v3.ENTRY))
    require(
        worker_sha == WORKER_SHA
        and plan["v2_plan_sha256"] == sha(canonical(v2_plan))
        and v2_plan["v51_plan_sha256"] == sha(canonical(previous))
        and previous["tier"] == 5000
        and previous["fixtures"] == list(FIXTURES)
        and previous["roles"] == ROLES
        and previous["limits"] == LIMITS == contract["tiers"]["5000"]
        and previous["producer_contract_sha256"] == v3.v2.V4
        and previous["verifier_registration_sha256"] == v51.V51,
        "worker, roles, fixtures or limits mismatch",
    )
    gate_sha = contract["predecessor"]["gate_report_sha256"]
    require(previous["historical_gate_sha256"] == gate_sha, "historical gate binding")
    _require_gate(
        SimpleNamespace(gate_report=v51.GATE, gate_sha256=gate_sha, contract_sha256=v3.v2.V4),
        contract,
    )
    reference.read_frozen_replay_bindings_v2()
    contracts()
    codec = codec_profile()
    require(all(codec.get(key) == value for key, value in contract["codec"].items()), "codec")
    fixtures = {}
    for name in FIXTURES:
        raw_fixture = scaling.invented_fixture(contract, name)
        spec = contract["fixtures"][name]
        require(
            len(raw_fixture.splitlines()) == spec["observations"] == 5000
            and sha(raw_fixture) == spec["input_sha256"],
            "invented fixture identity",
        )
        fixtures[name] = {"observations": 5000, "input_sha256": spec["input_sha256"]}
    return {
        "schema": "agicore:g2c-parity-v3-5000-plan-check:v1",
        "status": "PASS",
        "plan_sha256": expected_plan_sha256,
        "plan_file_sha256": sha(raw),
        "v3_registration_sha256": REGISTRATION_SHA,
        "v3_worker_sha256": worker_sha,
        "producer_contract_sha256": v3.v2.V4,
        "source_closure_sha256": contract["source_closure_sha256"],
        "verifier_registration_sha256": v51.V51,
        "historical_gate_sha256": gate_sha,
        "fixtures": fixtures,
        "limits": LIMITS,
        "workers_launched": 0,
        "replay_executed": False,
        "host_execution_preflight": "NOT_RUN",
    }


def main() -> int:
    """Print one canonical read-only validation result."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan-sha256", required=True)
    args = parser.parse_args()
    sys.stdout.buffer.write(canonical(check_plan(args.plan_sha256)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
