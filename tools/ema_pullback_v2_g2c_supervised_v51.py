"""Versioned parent-side role binding for the frozen G2C supervisor.

No workflow invokes this entry point. The default is an offline plan; executing
that exact plan requires a separate Manager decision. Reuse V4's worker transport,
preflight, process-group selfcheck and storage/coverage checks without importing
this adapter in either child. The historical V4 supervisor remains usable as-is.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import FunctionType, SimpleNamespace

from agicore.trading import ema_pullback_v2_g2c_verifier_v5 as verifier
from agicore.trading.ema_pullback_v2_g2c_scaling import RUNNER_SHA256, SUPERVISOR_PATH
from agicore.trading.ema_pullback_v2_storage_format import (
    ROOT,
    canonical,
    parse_canonical,
    regular_read,
    require,
    sha,
)
from tools import ema_pullback_v2_g2c_supervisor as supervisor

V4 = verifier.V4_SHA
V51 = "9dc2cfcaf37909004d084456dadbc6c896699033b5e3428d62ae56ece7e87bf6"
ENTRY = "tools/ema_pullback_v2_g2c_supervised_v51.py"
REGISTRATION = ROOT / "docs/evidence/EMA_PULLBACK_V2_G2C_SUPERVISION_V5_1.json"
GATE = ROOT / "docs/evidence/AGICORE_G2C_1000_9E6E_TIER_REPORT_20261111.json"


def _load(binding_sha):
    raw = regular_read(REGISTRATION, limit=4096)
    require(sha(raw) == binding_sha, "external supervision binding")
    contract = verifier.load_registration(V51)
    require(
        raw
        == canonical(
            {
                "schema": "agicore:g2c-supervision-binding:v5.1",
                "parent": {"path": ENTRY, "sha256": sha(regular_read(ROOT / ENTRY))},
                "transport": contract["supervisor"],
                "producer_contract_sha256": V4,
                "verifier_registration_sha256": V51,
                "roles": {
                    "producer": SUPERVISOR_PATH,
                    "verifier": verifier.WORKER,
                    "parity": SUPERVISOR_PATH,
                },
            }
        ),
        "supervision registration or source mismatch",
    )
    return contract


def _plan(binding_sha, tier, contract):
    key = str(tier)
    require(key in contract["tier_fixtures"] and key in contract["tiers"], "unregistered tier")
    return {
        "schema": "agicore:g2c-supervised-plan:v5.1",
        "binding_sha256": binding_sha,
        "producer_contract_sha256": V4,
        "verifier_registration_sha256": V51,
        "tier": tier,
        "limits": contract["tiers"][key],
        "fixtures": contract["tier_fixtures"][key],
        "roles": ["producer", "verifier", "producer", "verifier", "parity"],
        "historical_gate_sha256": contract["predecessor"]["gate_report_sha256"]
        if tier == 5000
        else None,
    }


def plan(binding_sha: str, tier: int) -> dict:
    """Resolve trusted role identities and budgets without starting a process or opening a fixture."""
    return _plan(binding_sha, tier, _load(binding_sha))


def _check_verification(bundle, folder, receipt, production):
    recorded = regular_read(bundle / "verification.json", limit=65536)
    require(
        receipt["schema"] == "agicore:g2c-verification:v5"
        and receipt["status"] == "PASS"
        and receipt["verifier_contract_sha256"] == V51
        and receipt["contract_sha256"] == V4
        and all(
            receipt[k] == production[k]
            for k in ("input_sha256", "native_sha256", "manifest_sha256")
        )
        and receipt["production_sha256"] == sha(canonical(production))
        and recorded == regular_read(folder / "stdout.log", limit=65536) == canonical(receipt),
        "unbound or noncanonical V5.1 worker receipt",
    )
    require(
        regular_read(bundle / "completion.json", limit=65536)
        == canonical(
            {
                "schema": "agicore:g2c-completion:v5",
                "status": "COMPLETE",
                "contract_sha256": V4,
                "verifier_contract_sha256": V51,
                "native_sha256": production["native_sha256"],
                "verification_sha256": sha(recorded),
            }
        ),
        "V5.1 completion seal",
    )


def _private_supervisor():
    """Bind the *same* pinned V4 loop to a private parent namespace for this call.

    V4 has no callback parameter and its file is covered by both registrations.
    Reuse the immutable code object and its original helpers; only dispatch and
    the tier report encoder change. No source is executed again, no global in
    the historical module changes, and concurrent legacy calls keep their V4 worker.
    """
    loop = supervisor.run_tier
    parent = SimpleNamespace(**vars(supervisor))
    parent.run_tier = FunctionType(
        loop.__code__, vars(parent), loop.__name__, loop.__defaults__, loop.__closure__
    )
    return parent


def _bind_parent(instance, selected, output):
    plan_sha = sha(canonical(selected))
    gate_args = (
        ["--gate-report", str(GATE), "--gate-sha256", selected["historical_gate_sha256"]]
        if selected["tier"] == 5000
        else []
    )
    prefix = [sys.executable, "-B", str(ROOT / SUPERVISOR_PATH), "--worker"]

    def dispatch(command, folder, caps, *, root):
        require(root == ROOT, "supervisor worker root")
        require(
            command[:4] == prefix
            and len(command) >= 7
            and command[5] == "--fixture"
            and command[6] in selected["fixtures"]
            and caps == selected["limits"],
            "unregistered supervisor dispatch",
        )
        role, name = command[4], command[6]
        if role in ("produce", "parity"):
            return supervisor.run_worker(command, folder, caps, root=root)
        require(
            role == "verify"
            and len(command) == 15 + len(gate_args)
            and command[7] == "--bundle"
            and command[9:12] == ["--contract-sha256", V4, "--manifest-sha256"]
            and command[13] == "--native-sha256"
            and command[15:] == gate_args,
            "unrecognized V4 verifier request",
        )
        bundle = Path(command[8])
        require(
            any(
                bundle == output / f"{name}-{i}" / "bundle"
                and folder == output / f"{name}-{i}-verify"
                for i in (1, 2)
            ),
            "supervised bundle and verifier folder",
        )
        production = parse_canonical([regular_read(bundle / "production.json", limit=65536)])
        require(
            production.get("schema") == "agicore:g2c-production:v1"
            and production.get("status") == "PRODUCED_INCOMPLETE"
            and (
                production["contract_sha256"],
                production["runner_sha256"],
                production["fixture"],
                production["manifest_sha256"],
                production["native_sha256"],
            )
            == (V4, RUNNER_SHA256, name, command[12], command[14]),
            "V4 producer-to-verifier binding",
        )
        args = [
            sys.executable,
            "-B",
            str(ROOT / verifier.WORKER),
            "--fixture",
            name,
            "--bundle",
            str(bundle),
            "--verifier-sha256",
            V51,
            "--manifest-sha256",
            command[12],
            "--native-sha256",
            command[14],
            "--seal",
            *gate_args,
        ]
        metrics, receipt = supervisor.run_worker(args, folder, caps, root=root)
        if metrics["status"] == "PASS":
            try:
                _check_verification(bundle, folder, receipt, production)
                require(
                    supervisor._physical_size(bundle.parent) + 1048576 <= caps["physical_bytes"],
                    "sealed production physical limit",
                )
            except (ValueError, OSError, TypeError, KeyError) as exc:
                # The subprocess resource report is still true; record the parent's
                # rejection in the role result and the enclosing tier report.
                return {**metrics, "status": "FAIL", "reason": str(exc)}, {}
        return metrics, receipt

    def encode(value):
        if isinstance(value, dict) and value.get("schema") == "agicore:g2c-tier-report:v1":
            value = dict(value)
            require(value.pop("contract_sha256") == V4, "tier report producer")
            value.update(
                schema="agicore:g2c-supervised-tier:v5.1",
                plan_sha256=plan_sha,
                binding_sha256=selected["binding_sha256"],
                producer_contract_sha256=V4,
                verifier_registration_sha256=V51,
            )
        return canonical(value)

    instance.run_worker = dispatch
    instance.canonical = encode


def run_tier(binding_sha: str, tier: int, output: Path, *, expected_plan_sha256: str) -> dict:
    """Delegate the exact plan to V4's run_tier; retain its gate, order, coverage and stop policy."""
    selected = plan(binding_sha, tier)
    require(sha(canonical(selected)) == expected_plan_sha256, "exact supervision plan not selected")
    dest = output.absolute()
    require(not {"..", "data"} & set(dest.parts), "new nonaliased output required")
    instance = _private_supervisor()
    _bind_parent(instance, selected, dest)
    gate_sha = selected["historical_gate_sha256"]
    result = instance.run_tier(
        SimpleNamespace(
            tier=tier,
            output=dest,
            contract_sha256=V4,
            gate_report=GATE if gate_sha else None,
            gate_sha256=gate_sha,
        )
    )
    report = parse_canonical([regular_read(dest / "tier_report.json", limit=1 << 20)])
    require(
        report["schema"] == "agicore:g2c-supervised-tier:v5.1"
        and (
            report["producer_contract_sha256"],
            report["verifier_registration_sha256"],
            report["binding_sha256"],
            report["plan_sha256"],
            report["tier"],
        )
        == (V4, V51, binding_sha, expected_plan_sha256, tier)
        and (result, report["status"]) in ((0, "PASS"), (1, "BLOCKED")),
        "sealed tier report binding",
    )
    return report


def main() -> int:
    """Print a plan by default; a plan digest selects bytes, not managerial permission."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binding-sha256", required=True)
    parser.add_argument("--tier", required=True, choices=(1000, 5000), type=int)
    parser.add_argument("--execute-plan-sha256")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if (args.execute_plan_sha256 is None) != (args.output is None):
        parser.error("--execute-plan-sha256 and --output must be supplied together")
    if args.output is None:
        selected = plan(args.binding_sha256, args.tier)
        sys.stdout.buffer.write(
            canonical({"plan": selected, "plan_sha256": sha(canonical(selected))})
        )
        return 0
    result = run_tier(
        args.binding_sha256, args.tier, args.output, expected_plan_sha256=args.execute_plan_sha256
    )
    return int(result["status"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())
