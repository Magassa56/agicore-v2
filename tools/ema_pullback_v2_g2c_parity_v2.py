"""Versioned G2C reference comparison and parent-side parity dispatch.

The CLI only runs registered invented fixtures under the existing supervisor.
Planning a tier is read-only. Executing one needs its separately selected plan.
"""

from __future__ import annotations

import argparse
import os
import re
import resource
import sys
from dataclasses import asdict
from pathlib import Path
from types import FunctionType, SimpleNamespace

from agicore.trading import ema_pullback_v2_development_replay as reference
from agicore.trading import ema_pullback_v2_g2c_scaling as scaling
from agicore.trading import ema_pullback_v2_recovery_optimized as optimized
from agicore.trading.ema_pullback_v2_recovery_evidence import CanonicalEncoderV1
from agicore.trading.ema_pullback_v2_storage_format import (
    ROOT,
    canonical,
    parse_canonical,
    regular_read,
    require,
    sha,
)
from tools import ema_pullback_v2_g2c_supervisor as supervisor

V4 = "e36c6a8985c383c9794cf3188e49940ddf28d7074d070f042661f6534629961f"
V51_BINDING = "d7b6179c5815286a52479eecf48528f03a32c08ceb1515774395df6854bf2006"
ENTRY = "tools/ema_pullback_v2_g2c_parity_v2.py"
REGISTRATION = ROOT / "docs/evidence/EMA_PULLBACK_V2_G2C_REFERENCE_PARITY_V2.json"


def load_registration(expected_sha256: str) -> dict:
    """Authenticate the external registration, role source, and historical closure."""
    raw = regular_read(REGISTRATION, limit=4096)
    require(sha(raw) == expected_sha256, "external parity registration")
    contract = scaling.load_contract(V4)
    expected = {
        "schema": "agicore:g2c-reference-parity-registration:v2",
        "scope": "COMPARE_REGISTERED_INVENTED_FIXTURES_ONLY",
        "producer_contract_sha256": V4,
        "producer_source_closure_sha256": contract["source_closure_sha256"],
        "supervision_v51_binding_sha256": V51_BINDING,
        "worker": {"path": ENTRY, "sha256": sha(regular_read(ROOT / ENTRY))},
    }
    require(raw == canonical(expected), "parity registration or source mismatch")
    return contract


class _PriceViews:
    """Cache a closed bar's original immutable V2 view for this comparison only."""

    def __init__(self, constructor):
        self.constructor = constructor
        self.views = {}

    def __call__(self, raw):
        views = {}
        for index, bar in raw.items():
            previous = self.views.get(index)
            if previous is None or previous[0] is not bar:
                view = self.constructor({index: bar})[index]
                self.views[index] = (bar, view)
            else:
                view = previous[1]
            views[index] = view
        return views


def _rebind(function, namespace):
    bound = FunctionType(
        function.__code__, namespace, function.__name__, function.__defaults__, function.__closure__
    )
    bound.__kwdefaults__ = function.__kwdefaults__
    return bound


def _cached_reference():
    """Use the frozen Open/Close code with a private, invocation-local price cache."""
    assembly = SimpleNamespace(**vars(reference.assembly))
    assembly._price_views = _PriceViews(reference.assembly._price_views)
    assembly.process_baseline_close_v2 = _rebind(
        reference.assembly.process_baseline_close_v2, vars(assembly)
    )
    namespace = dict(vars(reference), assembly=assembly)
    namespace["_assemble_result"] = _rebind(reference._assemble_result, namespace)
    return _rebind(reference.evaluate_synthetic_development_replay_v2, namespace)


def compare_reference(fixture: str, *, registration_sha256: str) -> dict:
    """Compare complete canonical outputs for one authenticated invented fixture."""
    contract = load_registration(registration_sha256)
    raw = scaling.invented_fixture(contract, fixture)
    bindings = reference.read_frozen_replay_bindings_v2()
    original = _cached_reference()(raw, bindings=bindings)
    candidate, identity = optimized.run_synthetic_native_v1(raw, bindings=bindings)
    encoder = CanonicalEncoderV1()
    optimized_bytes = encoder.bytes(candidate)
    projected = dict(candidate)
    reference_identity = reference.build_replay_run_identity_v2(identity.dataset_raw_sha256)
    projected["run_identity"] = asdict(reference_identity)
    projected["run_id_sha256"] = reference_identity.sha256
    projected["output_sha256"] = encoder.sha256(
        {key: value for key, value in projected.items() if key != "output_sha256"}
    )
    require(encoder.bytes(projected) == original.canonical_utf8, "G2C reference parity")
    return {
        "schema": "agicore:g2c-parity:v2",
        "status": "PASS",
        "fixture": fixture,
        "contract_sha256": V4,
        "parity_registration_sha256": registration_sha256,
        "input_sha256": sha(raw),
        "optimized_native_sha256": sha(optimized_bytes),
        "reference_native_sha256": sha(original.canonical_utf8),
        "comparison": "EXACT_AFTER_TEMPORARY_IDENTITY_PROJECTION",
        "projected_output_persisted": False,
    }


def _worker_limits(args, contract):
    require(args.fixture in contract["fixtures"], "unregistered parity fixture")
    tier = contract["fixtures"][args.fixture]["observations"]
    caps = contract["tiers"][str(tier)]
    require(os.getsid(0) == os.getpid(), "supervised parity process group")
    for key, cap in (
        (resource.RLIMIT_AS, "address_space_bytes"),
        (resource.RLIMIT_CPU, "cpu_seconds"),
        (resource.RLIMIT_FSIZE, "file_bytes"),
    ):
        require(resource.getrlimit(key) == (caps[cap], caps[cap]), "supervised parity limits")
    if tier == 5000:
        args.contract_sha256 = V4
        supervisor._require_gate(args, contract)
        supervisor.preflight(
            caps,
            Path.cwd() / "g2c-worker-resource-check",
            require_cgroup_memory=True,
            cgroup_v4=True,
        )


def _check_loaded_sources(contract):
    allowed = {entry["path"] for entry in contract["source_closure"]} | {ENTRY}
    loaded = set()
    for module in list(sys.modules.values()):
        name = getattr(module, "__file__", None)
        if name:
            path = Path(name).resolve()
            if path.suffix == ".py" and path.is_relative_to(ROOT):
                loaded.add(str(path.relative_to(ROOT)))
    require(loaded <= allowed, f"unregistered loaded repository sources: {sorted(loaded - allowed)}")


def worker(args) -> None:
    """Produce one canonical receipt only after all parity and provenance checks pass."""
    contract = load_registration(args.registration_sha256)
    _worker_limits(args, contract)
    receipt = compare_reference(args.fixture, registration_sha256=args.registration_sha256)
    _check_loaded_sources(contract)
    sys.stdout.buffer.write(canonical(receipt))


def plan(registration_sha256: str, tier: int) -> dict:
    """Resolve a new role binding without starting a worker."""
    from tools import ema_pullback_v2_g2c_supervised_v51 as v51

    contract = load_registration(registration_sha256)
    previous = v51.plan(V51_BINDING, tier)
    require(previous["limits"] == contract["tiers"][str(tier)], "historical limits changed")
    return {
        "schema": "agicore:g2c-supervised-plan:parity-v2",
        "parity_registration_sha256": registration_sha256,
        "v51_plan_sha256": sha(canonical(previous)),
        "v51_plan": previous,
    }


def _check_receipt(receipt, folder, fixture, contract, registration_sha256):
    require(
        set(receipt) == {
            "schema", "status", "fixture", "contract_sha256", "parity_registration_sha256",
            "input_sha256", "optimized_native_sha256", "reference_native_sha256", "comparison",
            "projected_output_persisted",
        }
        and receipt.get("schema") == "agicore:g2c-parity:v2"
        and receipt.get("status") == "PASS"
        and receipt.get("fixture") == fixture
        and receipt.get("contract_sha256") == V4
        and receipt.get("parity_registration_sha256") == registration_sha256
        and receipt.get("input_sha256") == contract["fixtures"][fixture]["input_sha256"]
        and all(
            isinstance(receipt.get(key), str)
            and re.fullmatch(r"[0-9a-f]{64}", receipt[key]) is not None
            for key in ("optimized_native_sha256", "reference_native_sha256")
        )
        and receipt.get("comparison") == "EXACT_AFTER_TEMPORARY_IDENTITY_PROJECTION"
        and receipt.get("projected_output_persisted") is False
        and regular_read(folder / "stdout.log", limit=65536) == canonical(receipt),
        "unbound or noncanonical parity V2 receipt",
    )


def _bind_parent(instance, selected, output, contract, registration_sha256):
    from tools import ema_pullback_v2_g2c_supervised_v51 as v51

    previous = selected["v51_plan"]
    v51._bind_parent(instance, previous, output)
    prior_dispatch, prior_canonical = instance.run_worker, instance.canonical
    gate = (
        ["--gate-report", str(v51.GATE), "--gate-sha256", previous["historical_gate_sha256"]]
        if previous["tier"] == 5000
        else []
    )

    def dispatch(command, folder, caps, *, root):
        if len(command) < 5 or command[4] != "parity":
            return prior_dispatch(command, folder, caps, root=root)
        require(
            len(command) >= 7 and command[6] in previous["fixtures"], "unregistered parity fixture"
        )
        fixture = command[6]
        expected = [
            sys.executable, "-B", str(ROOT / scaling.SUPERVISOR_PATH), "--worker", "parity",
            "--fixture", fixture, "--contract-sha256", V4, *gate,
        ]
        require(
            command == expected and root == ROOT and caps == previous["limits"]
            and folder == output / f"{fixture}-parity",
            "unregistered parity dispatch",
        )
        command = [
            sys.executable, "-B", str(ROOT / ENTRY), "worker", "--fixture", fixture,
            "--registration-sha256", registration_sha256, *gate,
        ]
        metrics, receipt = supervisor.run_worker(command, folder, caps, root=root)
        if metrics["status"] == "PASS":
            try:
                _check_receipt(receipt, folder, fixture, contract, registration_sha256)
            except (ValueError, OSError, TypeError, KeyError) as exc:
                return {**metrics, "status": "FAIL", "reason": str(exc)}, {}
        return metrics, receipt

    def encode(value):
        encoded = prior_canonical(value)
        if isinstance(value, dict) and value.get("schema") == "agicore:g2c-tier-report:v1":
            report = parse_canonical([encoded])
            report.update(
                schema="agicore:g2c-supervised-tier:parity-v2",
                parity_registration_sha256=registration_sha256,
                parity_plan_sha256=sha(canonical(selected)),
            )
            return canonical(report)
        return encoded

    instance.run_worker = dispatch
    instance.canonical = encode


def run_tier(registration_sha256: str, tier: int, output: Path, *, plan_sha256: str) -> dict:
    """Run the selected plan through the original supervisor and V5.1 verifier."""
    from tools import ema_pullback_v2_g2c_supervised_v51 as v51

    selected = plan(registration_sha256, tier)
    require(sha(canonical(selected)) == plan_sha256, "exact parity plan not selected")
    dest = output.absolute()
    require(not {"..", "data"} & set(dest.parts), "new nonaliased output required")
    contract = load_registration(registration_sha256)
    instance = v51._private_supervisor()
    _bind_parent(instance, selected, dest, contract, registration_sha256)
    gate_sha = selected["v51_plan"]["historical_gate_sha256"]
    result = instance.run_tier(
        SimpleNamespace(
            tier=tier,
            output=dest,
            contract_sha256=V4,
            gate_report=v51.GATE if gate_sha else None,
            gate_sha256=gate_sha,
        )
    )
    report = parse_canonical([regular_read(dest / "tier_report.json", limit=1 << 20)])
    require(
        report["schema"] == "agicore:g2c-supervised-tier:parity-v2"
        and report["parity_registration_sha256"] == registration_sha256
        and report["parity_plan_sha256"] == plan_sha256
        and report["tier"] == tier
        and (result, report["status"]) in ((0, "PASS"), (1, "BLOCKED")),
        "sealed parity tier report binding",
    )
    return report


def main() -> int:
    """Select a worker, a read-only plan, or one explicitly selected plan."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("worker", "plan", "run"):
        command = sub.add_parser(name)
        command.add_argument("--registration-sha256", required=True)
        if name == "worker":
            command.add_argument("--fixture", required=True)
            command.add_argument("--gate-report", type=Path)
            command.add_argument("--gate-sha256")
        else:
            command.add_argument("--tier", type=int, choices=(1000, 5000), required=True)
        if name == "run":
            command.add_argument("--plan-sha256", required=True)
            command.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "worker":
        worker(args)
        return 0
    if args.action == "plan":
        selected = plan(args.registration_sha256, args.tier)
        sys.stdout.buffer.write(canonical({"plan": selected, "plan_sha256": sha(canonical(selected))}))
        return 0
    result = run_tier(args.registration_sha256, args.tier, args.output, plan_sha256=args.plan_sha256)
    return int(result["status"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())
