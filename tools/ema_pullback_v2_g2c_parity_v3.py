"""G2C parity V3 with bounded, invocation-local exact integer serialization."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from types import SimpleNamespace

from agicore.trading import ema_pullback_v2_development_replay as reference
from agicore.trading import ema_pullback_v2_g2c_scaling as scaling
from agicore.trading.ema_pullback_v2_recovery_evidence import CanonicalEncoderV1
from agicore.trading.ema_pullback_v2_storage_format import (
    ROOT,
    canonical,
    parse_canonical,
    regular_read,
    require,
    sha,
)
from tools import ema_pullback_v2_g2c_parity_v2 as v2
from tools import ema_pullback_v2_g2c_supervisor as supervisor

V2_SHA = "a7debadeec3b5038699216b3abb6142086617296677dcb37b9fd01f6010c9699"
ENTRY = "tools/ema_pullback_v2_g2c_parity_v3.py"
ENCODER = "src/agicore/trading/ema_pullback_v2_recovery_evidence.py"
CACHE_CAP_BYTES = 16 * 1024 * 1024
REGISTRATION = ROOT / "docs/evidence/EMA_PULLBACK_V2_G2C_REFERENCE_PARITY_V3.json"


def load_registration(expected_sha256: str) -> dict:
    """Authenticate V3, its predecessor, and the frozen producer source closure."""
    raw = regular_read(REGISTRATION, limit=4096)
    require(sha(raw) == expected_sha256, "external parity V3 registration")
    contract = v2.load_registration(V2_SHA)
    encoders = [entry for entry in contract["source_closure"] if entry["path"] == ENCODER]
    require(len(encoders) == 1, "registered exact encoder source")
    expected = {
        "schema": "agicore:g2c-reference-parity-registration:v3",
        "scope": "COMPARE_REGISTERED_INVENTED_FIXTURES_ONLY",
        "predecessor_parity_registration_sha256": V2_SHA,
        "producer_contract_sha256": v2.V4,
        "producer_source_closure_sha256": contract["source_closure_sha256"],
        "integer_encoder": {**encoders[0], "cache_cap_bytes": CACHE_CAP_BYTES},
        "worker": {"path": ENTRY, "sha256": sha(regular_read(ROOT / ENTRY))},
    }
    require(raw == canonical(expected), "parity V3 registration or source mismatch")
    return contract


def _cached_reference():
    """Keep V2's reference loop and use its existing encoder for integer text."""
    evaluate = v2._cached_reference()
    namespace = evaluate.__globals__
    encoder = CanonicalEncoderV1(cache_cap_bytes=CACHE_CAP_BYTES)

    def integer_text(value):
        return encoder._integer(value).decode("ascii")

    namespace["_integer_text"] = integer_text
    for name in (
        "_json_text",
        "canonical_replay_bytes_v2",
        "_validate_result",
        "validate_development_result_v2",
    ):
        namespace[name] = v2._rebind(getattr(reference, name), namespace)
    return evaluate


def compare_reference(fixture: str, *, registration_sha256: str) -> dict:
    """Reuse V2's complete comparison with V3's isolated reference encoder."""
    namespace = dict(vars(v2), load_registration=load_registration, _cached_reference=_cached_reference)
    compare = v2._rebind(v2.compare_reference, namespace)
    receipt = compare(fixture, registration_sha256=registration_sha256)
    receipt.update(
        schema="agicore:g2c-parity:v3",
        predecessor_parity_registration_sha256=V2_SHA,
    )
    return receipt


def _check_loaded_sources(contract):
    allowed = {entry["path"] for entry in contract["source_closure"]} | {v2.ENTRY, ENTRY}
    loaded = set()
    for module in list(sys.modules.values()):
        name = getattr(module, "__file__", None)
        if name:
            path = Path(name).resolve()
            if path.suffix == ".py" and path.is_relative_to(ROOT):
                loaded.add(str(path.relative_to(ROOT)))
    require(loaded <= allowed, f"unregistered loaded repository sources: {sorted(loaded - allowed)}")


def worker(args) -> None:
    """Run a registered synthetic comparison within the original resource gates."""
    contract = load_registration(args.registration_sha256)
    v2._worker_limits(args, contract)
    receipt = compare_reference(args.fixture, registration_sha256=args.registration_sha256)
    _check_loaded_sources(contract)
    sys.stdout.buffer.write(canonical(receipt))


def plan(registration_sha256: str, tier: int) -> dict:
    """Resolve the V3 binding and inherited V2 plan without starting a worker."""
    contract = load_registration(registration_sha256)
    previous = v2.plan(V2_SHA, tier)
    require(previous["v51_plan"]["limits"] == contract["tiers"][str(tier)], "historical limits")
    return {
        "schema": "agicore:g2c-supervised-plan:parity-v3",
        "parity_registration_sha256": registration_sha256,
        "v2_plan_sha256": sha(canonical(previous)),
        "v2_plan": previous,
    }


def _check_receipt(receipt, folder, fixture, contract, registration_sha256):
    require(
        set(receipt) == {
            "schema", "status", "fixture", "contract_sha256", "parity_registration_sha256",
            "predecessor_parity_registration_sha256", "input_sha256", "optimized_native_sha256",
            "reference_native_sha256", "comparison", "projected_output_persisted",
        }
        and receipt.get("schema") == "agicore:g2c-parity:v3"
        and receipt.get("status") == "PASS"
        and receipt.get("fixture") == fixture
        and receipt.get("contract_sha256") == v2.V4
        and receipt.get("parity_registration_sha256") == registration_sha256
        and receipt.get("predecessor_parity_registration_sha256") == V2_SHA
        and receipt.get("input_sha256") == contract["fixtures"][fixture]["input_sha256"]
        and all(
            isinstance(receipt.get(key), str)
            and re.fullmatch(r"[0-9a-f]{64}", receipt[key]) is not None
            for key in ("optimized_native_sha256", "reference_native_sha256")
        )
        and receipt.get("comparison") == "EXACT_AFTER_TEMPORARY_IDENTITY_PROJECTION"
        and receipt.get("projected_output_persisted") is False
        and regular_read(folder / "stdout.log", limit=65536) == canonical(receipt),
        "unbound or noncanonical parity V3 receipt",
    )


def _bind_parent(instance, selected, output, contract, registration_sha256):
    from tools import ema_pullback_v2_g2c_supervised_v51 as v51

    v2._bind_parent(instance, selected["v2_plan"], output, contract, V2_SHA)
    prior_dispatch, prior_canonical = instance.run_worker, instance.canonical
    previous = selected["v2_plan"]["v51_plan"]
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
            "--fixture", fixture, "--contract-sha256", v2.V4, *gate,
        ]
        require(
            command == expected and root == ROOT and caps == previous["limits"]
            and folder == output / f"{fixture}-parity",
            "unregistered parity V3 dispatch",
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
                schema="agicore:g2c-supervised-tier:parity-v3",
                parity_v3_registration_sha256=registration_sha256,
                parity_v3_plan_sha256=sha(canonical(selected)),
            )
            return canonical(report)
        return encoded

    instance.run_worker = dispatch
    instance.canonical = encode


def run_tier(registration_sha256: str, tier: int, output: Path, *, plan_sha256: str) -> dict:
    """Delegate the selected plan to the existing bounded G2C supervisor."""
    from tools import ema_pullback_v2_g2c_supervised_v51 as v51

    selected = plan(registration_sha256, tier)
    require(sha(canonical(selected)) == plan_sha256, "exact parity V3 plan not selected")
    dest = output.absolute()
    require(not {"..", "data"} & set(dest.parts), "new nonaliased output required")
    contract = load_registration(registration_sha256)
    instance = v51._private_supervisor()
    _bind_parent(instance, selected, dest, contract, registration_sha256)
    gate_sha = selected["v2_plan"]["v51_plan"]["historical_gate_sha256"]
    result = instance.run_tier(
        SimpleNamespace(
            tier=tier,
            output=dest,
            contract_sha256=v2.V4,
            gate_report=v51.GATE if gate_sha else None,
            gate_sha256=gate_sha,
        )
    )
    report = parse_canonical([regular_read(dest / "tier_report.json", limit=1 << 20)])
    require(
        report["schema"] == "agicore:g2c-supervised-tier:parity-v3"
        and report["parity_v3_registration_sha256"] == registration_sha256
        and report["parity_v3_plan_sha256"] == plan_sha256
        and report["tier"] == tier
        and (result, report["status"]) in ((0, "PASS"), (1, "BLOCKED")),
        "sealed parity V3 tier report binding",
    )
    return report


def main() -> int:
    """Select a bounded worker, a read-only plan, or one explicitly selected plan."""
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
