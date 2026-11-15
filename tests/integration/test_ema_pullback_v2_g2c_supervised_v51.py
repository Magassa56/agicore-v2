"""Parent dispatch, byte identity and fail-closed tests; no replay of either registered tier."""

from __future__ import annotations

import copy
import json
import shutil
import sys
from pathlib import Path

import pytest

from agicore.trading import ema_pullback_v2_g2c_scaling as v4
from agicore.trading.ema_pullback_v2_g2b_contract import generate_fixture
from agicore.trading.ema_pullback_v2_storage_format import (
    StorageProofError,
    canonical,
    codec_profile,
    sha,
)
from tools import ema_pullback_v2_g2c_supervised_v51 as route
from tools import ema_pullback_v2_g2c_supervisor as supervisor

BINDING = "d7b6179c5815286a52479eecf48528f03a32c08ceb1515774395df6854bf2006"
REAL_V51 = "9dc2cfcaf37909004d084456dadbc6c896699033b5e3428d62ae56ece7e87bf6"
MINI_INPUT = "80d20a90099fe0564255aea18f58aaac0ee5fc4cfe82627fce396676cfaae19b"
LINUX = pytest.mark.skipif(
    sys.platform != "linux" or not shutil.which("prlimit"),
    reason="G2C supervision requires Linux and prlimit",
)


def test_planning_selects_authentic_sources_and_does_not_execute(monkeypatch, capsysbinary):
    monkeypatch.setattr(
        supervisor, "run_worker", lambda *_a, **_k: pytest.fail("no worker in plan")
    )
    monkeypatch.setattr(sys, "argv", ["plan", "--tier", "5000", "--binding-sha256", BINDING])
    assert route.main() == 0
    packet = json.loads(capsysbinary.readouterr().out)
    plan = packet["plan"]
    before = supervisor.run_worker, supervisor.canonical
    separate = route._private_supervisor()
    route._bind_parent(separate, packet["plan"], Path("not-used"))
    assert (supervisor.run_worker, supervisor.canonical) == before
    assert separate.run_tier.__code__ is supervisor.run_tier.__code__
    assert separate.run_tier.__globals__ is not supervisor.run_tier.__globals__
    assert packet["plan_sha256"] == sha(canonical(plan))
    assert plan["producer_contract_sha256"] == sha(v4.CONTRACT_V4_PATH.read_bytes())
    assert (
        plan["verifier_registration_sha256"]
        == REAL_V51
        == sha(route.verifier.REGISTRATION.read_bytes())
    )
    contract = v4.load_contract(route.V4)
    assert plan["fixtures"] == contract["tier_fixtures"]["5000"]
    assert plan["roles"] == ["producer", "verifier", "producer", "verifier", "parity"]
    assert plan["limits"] == {
        "wall_seconds": 240,
        "cpu_seconds": 150,
        "address_space_bytes": 2 << 30,
        "physical_bytes": 256 << 20,
        "tier_physical_bytes": 1 << 30,
        "logical_bytes": 256 << 20,
        "file_bytes": 64 << 20,
    }
    assert route.plan(BINDING, 1000)["limits"] == contract["tiers"]["1000"]


def test_unknown_or_rehashed_role_registration_refused(tmp_path, monkeypatch):
    with pytest.raises(StorageProofError, match="external supervision"):
        route.plan(REAL_V51, 5000)
    doc = json.loads(route.REGISTRATION.read_bytes())
    doc["roles"]["verifier"] = v4.SUPERVISOR_PATH
    path = tmp_path / "incorrect.json"
    path.write_bytes(canonical(doc))
    monkeypatch.setattr(route, "REGISTRATION", path)
    with pytest.raises(StorageProofError, match="registration or source"):
        route.plan(sha(path.read_bytes()), 5000)


def test_large_tier_gate_and_cgroup_fail_before_any_worker(tmp_path, monkeypatch):
    selected = sha(canonical(route.plan(BINDING, 5000)))
    dest = tmp_path / "never-created"
    monkeypatch.setattr(
        supervisor, "run_worker", lambda *_a, **_k: pytest.fail("no tier worker authorized")
    )
    with pytest.raises(StorageProofError, match="exact supervision plan"):
        route.run_tier(BINDING, 5000, dest, expected_plan_sha256="0" * 64)
    original_gate = route.GATE
    forged = tmp_path / "gate"
    forged.write_bytes(original_gate.read_bytes() + b" ")
    monkeypatch.setattr(route, "GATE", forged)
    with pytest.raises(RuntimeError, match="1000 gate identity"):
        route.run_tier(BINDING, 5000, dest, expected_plan_sha256=selected)
    monkeypatch.setattr(route, "GATE", original_gate)
    private = route._private_supervisor()
    monkeypatch.setattr(supervisor, "_cgroup_memory_v4", lambda: None)
    monkeypatch.setattr(route, "_private_supervisor", lambda: private)
    with pytest.raises(RuntimeError, match="cgroup memory limit is not observable"):
        route.run_tier(BINDING, 5000, dest, expected_plan_sha256=selected)
    assert not dest.exists()


# Test subprocess bootstrap: replace ONLY the invented input and the fixture registrars at the
# API boundary. Never attach a real registration or closure ID to this miniature. The production
# command has no override, test fixture, monkeypatch, alternate worker or fallback mechanism.
_BOOT = """
import json,runpy,sys
from pathlib import Path
from agicore.trading import ema_pullback_v2_g2c_scaling as prod
from agicore.trading.ema_pullback_v2_storage_format import sha,require
spec_path, script = sys.argv[1:3]
sys.argv = [script, *sys.argv[3:]]
spec=json.loads(Path(spec_path).read_bytes())
contract=spec['contract']
def lookup(supplied, wanted):
    require(supplied==wanted,'test registration pin')
    return contract
prod.load_contract=lambda digest:lookup(digest,spec['producer'])
raw=bytes.fromhex(spec['raw_hex'])
def tiny(c,name):
    require(c is contract and name=='mini-invented-only' and len(raw.splitlines())==57
            and sha(raw)==contract['fixtures'][name]['input_sha256'],'small invented fixture')
    return raw
prod.invented_fixture=tiny
if Path(script).name == 'ema_pullback_v2_g2c_verifier_worker_v5.py':
    from agicore.trading import ema_pullback_v2_g2c_verifier_v5 as ver
    ver.V4_SHA=spec['producer']
    ver.load_registration=lambda digest:lookup(digest,spec['verifier'])
runpy.run_path(script,run_name='__main__')
"""


@pytest.fixture(scope="module")
def miniature(tmp_path_factory):
    # Use genuinely separate interpreters and V4's real supervisor/run_worker, never point the
    # real contract at fewer rows. The probe is not a V4 production receipt for a registered tier.
    root = tmp_path_factory.mktemp("g2c-v51-small")
    with pytest.MonkeyPatch.context() as m:
        contract = copy.deepcopy(route._load(BINDING))
        raw = generate_fixture(v4.load_g2b_contract(v4.PARENT_SHA256), "impulse_profit_LONG")
        assert len(raw.splitlines()) == 57 and sha(raw) == MINI_INPUT
        name = "mini-invented-only"
        p, v, b = (
            sha(x)
            for x in (b"test-57-V4-producer", b"test-57-V51-verifier", b"test-57-supervision")
        )
        contract.update(
            source_closure_sha256=sha(b"private-test-closure"),
            fixtures={name: {"observations": 57, "input_sha256": sha(raw)}},
            tiers={"57": contract["tiers"]["5000"]},
            tier_fixtures={"57": [name]},
        )
        spec = root / "miniature.json"
        spec.write_bytes(
            canonical({"contract": contract, "producer": p, "verifier": v, "raw_hex": raw.hex()})
        )
        calls = []
        real = supervisor.run_worker

        def transport(command, folder, caps, *, root):
            if command[2] not in (
                str(root / v4.SUPERVISOR_PATH),
                str(root / route.verifier.WORKER),
            ):
                return real(command, folder, caps, root=root)  # keep the real descendant selfcheck
            assert caps == contract["tiers"]["57"]
            calls.append(command[2:])
            return real(
                [*command[:2], "-c", _BOOT, str(spec), *command[2:]], folder, caps, root=root
            )

        m.setattr(
            route,
            "_load",
            lambda supplied: contract if supplied == b else pytest.fail("wrong binding"),
        )
        private = route._private_supervisor()
        m.setattr(
            private,
            "load_contract",
            lambda supplied: contract if supplied == p else pytest.fail("wrong private producer"),
        )
        m.setattr(route, "_private_supervisor", lambda: private)
        m.setattr(route, "V4", p)
        m.setattr(route, "V51", v)
        m.setattr(supervisor, "run_worker", transport)
        out = root / "supervised"
        report = route.run_tier(b, 57, out, expected_plan_sha256=sha(canonical(route.plan(b, 57))))
        assert report["status"] == "PASS", (
            report.get("failure"),
            [f.read_text()[-1500:] for f in out.glob("*/stderr.log") if f.stat().st_size],
        )
        return out, report, contract, calls, name, p, v


@LINUX
def test_separate_supervised_workers_with_original_canonical_bytes(
    miniature, tmp_path, monkeypatch
):
    out, report, contract, calls, name, producer, verifier = miniature
    item = report["fixtures"][0]
    assert json.loads((out / "preflight.json").read_bytes())["process_group_selfcheck"][
        "worker_and_descendant_stopped"
    ]
    assert (out / "tier_report.json").read_bytes() == canonical(report)
    assert [Path(c[0]).name for c in calls] == [
        Path(x).name
        for x in (
            v4.SUPERVISOR_PATH,
            route.verifier.WORKER,
            v4.SUPERVISOR_PATH,
            route.verifier.WORKER,
            v4.SUPERVISOR_PATH,
        )
    ]
    assert all(
        "--seal" in c and c[c.index("--verifier-sha256") + 1] == verifier for c in calls[1:4:2]
    )
    assert (
        calls[0][calls[0].index("--worker") + 1] == "produce"
        and calls[-1][calls[-1].index("--worker") + 1] == "parity"
    )
    assert len(item["runs"]) == 5
    for r in item["runs"]:
        assert r["status"] == "PASS" and r["exit_code"] == 0
        assert (
            r["cpu_limit_seconds"],
            r["wall_limit_seconds"],
            r["address_space_limit_bytes"],
            r["file_limit_bytes"],
            r["physical_limit_bytes"],
        ) == (150, 240, 2 << 30, 64 << 20, 256 << 20)
    bundles = [out / f"{name}-{i}" / "bundle" for i in (1, 2)]

    def inventory(p):
        return {f.relative_to(p): sha(f.read_bytes()) for f in p.rglob("*") if f.is_file()}

    assert inventory(bundles[0]) == inventory(bundles[1])
    manifest = json.loads((bundles[0] / "manifest.json").read_bytes())
    native, witnesses = [
        v4.decode_pages(s, bundles[0], codec_profile()) for s in manifest["streams"]
    ]
    assert len(witnesses.splitlines()) == 57
    assert (
        sha(native)
        == item["production"]["native_sha256"]
        == item["parity"]["optimized_native_sha256"]
    )
    audit = item["verification"]
    assert audit["audit"]["observation_count"] == 57 and audit["closed_positions"] == 1
    assert audit["contract_sha256"] == producer and audit["verifier_contract_sha256"] == verifier
    legacy = tmp_path / "V4"
    shutil.copytree(
        bundles[0], legacy, ignore=shutil.ignore_patterns("verification.json", "completion.json")
    )
    monkeypatch.setattr(v4, "load_contract", lambda _: contract)
    prior = v4.verify_bundle(
        legacy,
        expected_contract_sha256=producer,
        expected_manifest_sha256=item["production"]["manifest_sha256"],
        expected_native_sha256=sha(native),
        seal=True,
    )
    assert {k: r for k, r in audit.items() if k not in ("schema", "verifier_contract_sha256")} == {
        k: r for k, r in prior.items() if k != "schema"
    }
    assert (
        json.loads((bundles[0] / "completion.json").read_bytes())["schema"]
        == "agicore:g2c-completion:v5"
    )


@LINUX
@pytest.mark.parametrize("tamper", ["stdout", "identity", "seal"])
def test_parent_refuses_substituted_worker_evidence(miniature, tmp_path, monkeypatch, tamper):
    out, report, _, _, name, p, v = miniature
    m = report["fixtures"][0]
    src = out / f"{name}-1" / "bundle"
    for file in ("verification.json", "completion.json"):
        shutil.copyfile(src / file, tmp_path / file)
    shutil.copyfile(out / f"{name}-1-verify" / "stdout.log", tmp_path / "stdout.log")
    receipt = dict(m["verification"])
    monkeypatch.setattr(route, "V4", p)
    monkeypatch.setattr(route, "V51", v)
    if tamper == "stdout":
        (tmp_path / "stdout.log").write_bytes(canonical(receipt) + b" ")
    elif tamper == "identity":
        receipt["verifier_contract_sha256"] = route.verifier.PREDECESSOR
        for f in ("stdout.log", "verification.json"):
            (tmp_path / f).write_bytes(canonical(receipt))
    else:
        seal = json.loads((tmp_path / "completion.json").read_bytes())
        seal["native_sha256"] = "0" * 64
        (tmp_path / "completion.json").write_bytes(canonical(seal))
    with pytest.raises(StorageProofError):
        route._check_verification(tmp_path, tmp_path, receipt, m["production"])


@LINUX
def test_real_worker_rejects_miniature_without_test_registrar(miniature, tmp_path):
    out, report, _, _, name, _, _ = miniature
    m = report["fixtures"][0]["production"]
    bundle = tmp_path / "foreign"
    shutil.copytree(
        out / f"{name}-1" / "bundle",
        bundle,
        ignore=shutil.ignore_patterns("verification.json", "completion.json"),
    )
    caps = route.plan(BINDING, 1000)["limits"]
    metrics, result = supervisor.run_worker(
        [
            sys.executable,
            "-B",
            str(route.ROOT / route.verifier.WORKER),
            "--verifier-sha256",
            REAL_V51,
            "--fixture",
            "constant-1000",
            "--manifest-sha256",
            m["manifest_sha256"],
            "--native-sha256",
            m["native_sha256"],
            "--bundle",
            str(bundle),
            "--seal",
        ],
        tmp_path / "rejected",
        caps,
        root=route.ROOT,
    )
    assert metrics["status"] == "FAIL" and not result
    assert "G2C source binding" in (tmp_path / "rejected/stderr.log").read_text()
    assert not (bundle / "verification.json").exists() and not (bundle / "completion.json").exists()


@LINUX
def test_dispatch_requires_and_forwards_the_exact_large_tier_gate_without_a_replay(
    miniature, monkeypatch
):
    out, report, _, _, name, p, v = miniature
    selected = route.plan(BINDING, 5000)
    # Use only the test-bound production below, never represent it as a registered 5000 fixture.
    selected = {
        **selected,
        "fixtures": [name],
        "producer_contract_sha256": p,
        "verifier_registration_sha256": v,
    }
    monkeypatch.setattr(route, "V4", p)
    monkeypatch.setattr(route, "V51", v)
    gate = ["--gate-report", str(route.GATE), "--gate-sha256", selected["historical_gate_sha256"]]
    production = report["fixtures"][0]["production"]
    bundle = out / f"{name}-1" / "bundle"
    folder = out / f"{name}-1-verify"
    original = [
        sys.executable,
        "-B",
        str(route.ROOT / v4.SUPERVISOR_PATH),
        "--worker",
        "verify",
        "--fixture",
        name,
        "--bundle",
        str(bundle),
        "--contract-sha256",
        p,
        "--manifest-sha256",
        production["manifest_sha256"],
        "--native-sha256",
        production["native_sha256"],
    ]
    calls = []

    def record(command, path, caps, *, root):
        calls.append((command, path, caps, root))
        return {"status": "FAIL", "reason": "NO_PROCESS_IN_ROUTING_TEST"}, {}

    monkeypatch.setattr(supervisor, "run_worker", record)
    parent = route._private_supervisor()
    route._bind_parent(parent, selected, out)
    for bad in ([], [*gate[:-1], "0" * 64]):
        with pytest.raises(StorageProofError, match="unrecognized V4 verifier request"):
            parent.run_worker(original + bad, folder, selected["limits"], root=route.ROOT)
    assert not calls
    metrics, _ = parent.run_worker(original + gate, folder, selected["limits"], root=route.ROOT)
    assert metrics["status"] == "FAIL"
    expected = [
        sys.executable,
        "-B",
        str(route.ROOT / route.verifier.WORKER),
        "--fixture",
        name,
        "--bundle",
        str(bundle),
        "--verifier-sha256",
        v,
        "--manifest-sha256",
        production["manifest_sha256"],
        "--native-sha256",
        production["native_sha256"],
        "--seal",
        *gate,
    ]
    assert calls == [(expected, folder, selected["limits"], route.ROOT)]


@LINUX
@pytest.mark.parametrize("fault", ["CPU_LIMIT", "legacy_receipt"])
def test_first_verifier_failure_stops_the_real_tier_loop(miniature, tmp_path, monkeypatch, fault):
    """Reuse the miniature's producer bytes; simulate only the failing worker response."""
    out, previous, contract, _, name, p, v = miniature
    original = previous["fixtures"][0]
    b = previous["binding_sha256"]
    monkeypatch.setattr(route, "V4", p)
    monkeypatch.setattr(route, "V51", v)
    monkeypatch.setattr(route, "_load", lambda _: contract)
    private = route._private_supervisor()
    monkeypatch.setattr(private, "load_contract", lambda _: contract)
    monkeypatch.setattr(route, "_private_supervisor", lambda: private)
    observed_selfcheck = json.loads((out / "preflight.json").read_bytes())[
        "process_group_selfcheck"
    ]
    monkeypatch.setattr(private, "supervision_selfcheck", lambda *a, **kw: observed_selfcheck)
    calls = []

    def stopped(command, folder, caps, *, root):
        calls.append(Path(command[2]).name)
        if len(calls) == 1:
            assert command[4] == "produce"
            shutil.copytree(
                out / f"{name}-1" / "bundle",
                folder / "bundle",
                ignore=shutil.ignore_patterns("verification.json", "completion.json"),
            )
            return {"status": "PASS", "reason": None}, original["production"]
        assert len(calls) == 2 and command[2] == str(route.ROOT / route.verifier.WORKER)
        if fault == "CPU_LIMIT":
            return {"status": "FAIL", "reason": fault}, {}
        receipt = {
            k: r for k, r in original["verification"].items() if k != "verifier_contract_sha256"
        }
        receipt["schema"] = "agicore:g2c-verification:v1"
        bundle = Path(command[command.index("--bundle") + 1])
        (bundle / "verification.json").write_bytes(canonical(receipt))
        folder.mkdir()
        (folder / "stdout.log").write_bytes(canonical(receipt))
        return {"status": "PASS", "reason": None}, receipt

    monkeypatch.setattr(supervisor, "run_worker", stopped)
    dest = tmp_path / "failed"
    result = route.run_tier(b, 57, dest, expected_plan_sha256=sha(canonical(route.plan(b, 57))))
    assert result["status"] == "BLOCKED" and "verifier 1" in result["failure"]
    reason = "CPU_LIMIT" if fault == "CPU_LIMIT" else "unbound or noncanonical V5.1 worker receipt"
    assert reason in result["failure"]
    assert calls == [Path(v4.SUPERVISOR_PATH).name, Path(route.verifier.WORKER).name]
    assert [r["status"] for r in result["fixtures"][0]["runs"]] == ["PASS", "FAIL"]
    assert (dest / "tier_report.json").read_bytes() == canonical(result)
