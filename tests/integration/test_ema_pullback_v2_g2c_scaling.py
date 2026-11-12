"""Small G2C contract, storage, provenance and supervision regressions."""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from agicore.trading import ema_pullback_v2_g2c_scaling as g2c
from agicore.trading.ema_pullback_v2_g2b_contract import generate_fixture, load_contract
from agicore.trading.ema_pullback_v2_storage_format import StorageProofError, codec_profile, sha
from tools import ema_pullback_v2_g2c_supervisor as supervisor
from tools.ema_pullback_v2_g2c_supervisor import _require_gate, supervision_selfcheck


@pytest.fixture()
def small_bundle(tmp_path, monkeypatch):
    parent = load_contract(g2c.PARENT_SHA256)
    raw = generate_fixture(parent, "impulse_profit_LONG")
    count = len(raw.splitlines())
    digest = "a" * 64
    contract = {
        "fixtures": {"invented-unit": {"observations": count, "input_sha256": sha(raw)}},
        "tiers": {str(count): {"logical_bytes": 33_554_432}},
        "source_closure_sha256": "b" * 64,
    }
    monkeypatch.setattr(g2c, "load_contract", lambda _: contract)
    monkeypatch.setattr(g2c, "invented_fixture", lambda *_: raw)
    bundle = tmp_path / "bundle"
    receipt = g2c.produce_bundle(bundle, "invented-unit", expected_contract_sha256=digest)
    verified = g2c.verify_bundle(
        bundle,
        expected_contract_sha256=digest,
        expected_manifest_sha256=receipt["manifest_sha256"],
        expected_native_sha256=receipt["native_sha256"],
        seal=True,
    )
    return bundle, receipt, digest, verified


def test_small_native_bundle_reconstructed_and_sealed(small_bundle):
    bundle, receipt, digest, verified = small_bundle
    assert verified["status"] == "PASS"
    assert verified["closed_positions"] == 1
    assert verified["audit"]["strategy_recomputed"] is False
    assert (
        g2c.verify_bundle(
            bundle,
            expected_contract_sha256=digest,
            expected_manifest_sha256=receipt["manifest_sha256"],
            expected_native_sha256=receipt["native_sha256"],
        )
        == verified
    )


@pytest.mark.parametrize("damage", ["object", "source", "seal", "native_hash"])
def test_small_forged_or_partial_bundle_fails_closed(small_bundle, tmp_path, damage):
    original, receipt, digest, _ = small_bundle
    bundle = tmp_path / "changed"
    shutil.copytree(original, bundle)
    native = receipt["native_sha256"]
    if damage == "object":
        path = next((bundle / "objects").rglob("*.blob"))
        content = path.read_bytes()
        path.write_bytes(bytes([content[0] ^ 1]) + content[1:])
    elif damage == "source":
        path = bundle / "source.synthetic.txt"
        path.write_bytes(path.read_bytes() + b"X")
    elif damage == "seal":
        (bundle / "completion.json").unlink()
    else:
        native = "0" * 64
    with pytest.raises(StorageProofError):
        g2c.verify_bundle(
            bundle,
            expected_contract_sha256=digest,
            expected_manifest_sha256=receipt["manifest_sha256"],
            expected_native_sha256=native,
        )


def test_g2c_pages_are_exact_and_reordering_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(g2c, "PAGE_BYTES", 64)
    raw = bytes(range(256)) * 2
    descriptor = g2c.encode_pages(raw, "invented_probe", tmp_path, codec_profile())
    assert len(descriptor["pages"]) == 8
    assert g2c.decode_pages(descriptor, tmp_path, codec_profile()) == raw
    forged = copy.deepcopy(descriptor)
    forged["pages"].reverse()
    with pytest.raises(StorageProofError):
        g2c.decode_pages(forged, tmp_path, codec_profile())


def test_5000_rejects_missing_or_forged_gate(tmp_path):
    args = SimpleNamespace(gate_report=None, gate_sha256=None, contract_sha256="a" * 64)
    with pytest.raises(RuntimeError, match="complete 1000 gate"):
        _require_gate(args, {})
    path = tmp_path / "gate.json"
    path.write_text(json.dumps({"status": "PASS", "tier": 1000}))
    args.gate_report, args.gate_sha256 = path, "0" * 64
    with pytest.raises(RuntimeError, match="gate identity"):
        _require_gate(args, {"tier_fixtures": {"1000": []}})


def test_5000_preflight_fails_if_cgroup_memory_is_unknown(tmp_path, monkeypatch):
    monkeypatch.setattr(supervisor, "_cgroup_memory", lambda: None)
    caps = {
        "address_space_bytes": 100_000_000,
        "cpu_seconds": 10,
        "file_bytes": 1_000_000,
        "physical_bytes": 1_000_000,
        "wall_seconds": 10,
    }
    with pytest.raises(RuntimeError, match="cgroup memory limit is not observable"):
        supervisor.preflight(caps, tmp_path / "probe", require_cgroup_memory=True)


def test_nested_cgroup_cannot_be_mistaken_for_mount_root(tmp_path):
    membership = tmp_path / "membership"
    root = tmp_path / "cgroup"
    root.mkdir()
    (root / "memory.max").write_text("1000\n")
    (root / "memory.current").write_text("100\n")
    membership.write_text("0::/restricted-child\n")
    assert supervisor._cgroup_memory(membership_path=membership, root=root) is None
    membership.write_text("0::/\n")
    assert supervisor._cgroup_memory(membership_path=membership, root=root) == {
        "limit_bytes": 1000,
        "current_bytes": 100,
    }


def test_preflight_uses_tier_disk_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(supervisor, "_cgroup_memory", lambda: None)
    monkeypatch.setattr(supervisor, "_memory_available", lambda: 10_000_000_000)
    monkeypatch.setattr(supervisor.shutil, "disk_usage", lambda _: SimpleNamespace(free=3_000_000))
    caps = {
        "address_space_bytes": 100_000_000,
        "cpu_seconds": 10,
        "file_bytes": 1_000_000,
        "physical_bytes": 1_000_000,
        "tier_physical_bytes": 2_000_000,
        "wall_seconds": 10,
    }
    with pytest.raises(RuntimeError, match="insufficient observed memory or storage"):
        supervisor.preflight(caps, tmp_path / "probe")


def test_external_contract_and_registered_invented_1000_inputs():
    # V3 receipts retain their original code closure; V4 is the current closure.
    assert sha(g2c.CONTRACT_PATH.read_bytes()) == g2c.PREDECESSOR_CONTRACT_SHA256
    with pytest.raises(StorageProofError):
        g2c.load_contract(g2c.PREDECESSOR_CONTRACT_SHA256)
    digest = sha(g2c.CONTRACT_V4_PATH.read_bytes())
    contract = g2c.load_contract(digest)
    assert contract["g2b_contract_sha256"] == g2c.PARENT_SHA256
    assert contract["tier_fixtures"]["5000"] == ["constant-5000", "dense-5000"]
    for fixture in contract["tier_fixtures"]["1000"]:
        raw = g2c.invented_fixture(contract, fixture)
        assert len(raw.splitlines()) == 1000
        assert sha(raw) == contract["fixtures"][fixture]["input_sha256"]
    with pytest.raises(StorageProofError):
        g2c.load_contract("0" * 64)
    with pytest.raises(StorageProofError):
        g2c.invented_fixture(contract, "unknown")


def test_verifier_import_has_no_strategy_or_producer():
    script = """
import sys
from agicore.trading.ema_pullback_v2_g2c_scaling import verify_bundle
for name in ('agicore.trading.ema_pullback_v2_g2b_storage',
             'agicore.trading.ema_pullback_v2_recovery_optimized',
             'agicore.trading.ema_pullback_regime_gated_baseline_v2'):
    assert name not in sys.modules
"""
    result = subprocess.run(
        [sys.executable, "-B", "-c", script],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.skipif(sys.platform != "linux" or not shutil.which("prlimit"), reason="Linux prlimit")
def test_supervisor_kills_worker_and_descendant(tmp_path):
    caps = {
        "address_space_bytes": 536_870_912,
        "cpu_seconds": 10,
        "file_bytes": 16_777_216,
        "physical_bytes": 16_777_216,
        "wall_seconds": 10,
    }
    result = supervision_selfcheck(tmp_path / "probe", caps, root=Path.cwd())
    assert result["worker_and_descendant_stopped"] is True
