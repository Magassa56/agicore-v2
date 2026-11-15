"""G2C V4 resource ancestry and the immutable V3 predecessor gate."""

from pathlib import Path
from types import SimpleNamespace

import pytest

from agicore.trading import ema_pullback_v2_g2c_scaling as scaling
from agicore.trading.ema_pullback_v2_storage_format import sha
from tools import ema_pullback_v2_g2c_supervisor as supervisor


@pytest.fixture()
def hierarchy(tmp_path):
    root = tmp_path / "cgroup"
    leaf = root / "system.slice" / "agent.service"
    leaf.mkdir(parents=True)
    (root / "cgroup.controllers").write_text("cpu memory\n")
    for directory, current, maximum, high in (
        (root / "system.slice", 10, 900, 500),
        (leaf, 20, 700, 600),
    ):
        (directory / "memory.current").write_text(str(current))
        (directory / "memory.max").write_text(str(maximum))
        (directory / "memory.high").write_text(str(high))
        (directory / "cpu.max").write_text("max 100000")
    membership = tmp_path / "membership"
    membership.write_text("0::/system.slice/agent.service\n")
    namespace = tmp_path / "namespace"
    namespace.symlink_to("cgroup:[4026531835]")
    mountinfo = tmp_path / "mountinfo"
    mountinfo.write_text(f"1 0 0:1 / {root} rw - cgroup2 cgroup rw\n")
    return SimpleNamespace(
        root=root, leaf=leaf, membership=membership, namespace=namespace, mountinfo=mountinfo
    )


def read_hierarchy(hierarchy):
    return supervisor._cgroup_memory_v4(
        root=hierarchy.root,
        membership_path=hierarchy.membership,
        namespace_path=hierarchy.namespace,
        mountinfo_path=hierarchy.mountinfo,
    )


def test_all_ancestors_and_high_limit_are_counted(hierarchy):
    result = read_hierarchy(hierarchy)
    assert result["limit_bytes"] == 500
    assert result["current_bytes"] == 10
    assert [entry["group"] for entry in result["ancestors"]] == [
        "/system.slice/agent.service",
        "/system.slice",
    ]
    assert result["root"] == "INITIAL_NAMESPACE_ROOT_NO_MEMORY_MAX"


@pytest.mark.parametrize("damage", ["namespace", "mount", "missing", "escape", "controller"])
def test_ambiguous_hierarchy_is_rejected(hierarchy, damage):
    if damage == "namespace":
        hierarchy.namespace.unlink()
        hierarchy.namespace.symlink_to("cgroup:[1234]")
    elif damage == "mount":
        hierarchy.mountinfo.write_text(f"1 0 0:1 /hidden {hierarchy.root} rw - cgroup2 cgroup rw\n")
    elif damage == "missing":
        (hierarchy.root / "system.slice" / "memory.high").unlink()
    elif damage == "escape":
        hierarchy.membership.write_text("0::/system.slice/../agent.service\n")
    else:
        (hierarchy.root / "cgroup.controllers").write_text("cpu\n")
    assert read_hierarchy(hierarchy) is None


def test_preflight_rejects_cpu_and_memory_ancestor_limits(tmp_path, monkeypatch):
    caps = {
        "address_space_bytes": 100,
        "cpu_seconds": 60,
        "wall_seconds": 100,
        "file_bytes": 100,
        "physical_bytes": 100,
    }
    monkeypatch.setattr(supervisor, "_memory_available", lambda: 1000)
    monkeypatch.setattr(supervisor.shutil, "disk_usage", lambda _: SimpleNamespace(free=1000))
    group = {
        "limit_bytes": 250,
        "current_bytes": 100,
        "cpu_limits": [{"quota": None, "period": 100}],
    }
    monkeypatch.setattr(supervisor, "_cgroup_memory_v4", lambda: group)
    with pytest.raises(RuntimeError, match="memory or storage"):
        supervisor.preflight(caps, tmp_path / "probe", require_cgroup_memory=True, cgroup_v4=True)
    group["limit_bytes"] = None
    group["cpu_limits"] = [{"quota": 50, "period": 100}]
    with pytest.raises(RuntimeError, match="CPU quota"):
        supervisor.preflight(caps, tmp_path / "probe", require_cgroup_memory=True, cgroup_v4=True)


def test_v4_accepts_only_pinned_historical_gate_without_replaying_it(tmp_path):
    digest = sha(scaling.CONTRACT_V4_PATH.read_bytes())
    contract = scaling.load_contract(digest)
    predecessor = contract["predecessor"]
    root = Path(__file__).resolve().parents[2]
    gate = root / "docs/evidence/AGICORE_G2C_1000_9E6E_TIER_REPORT_20261111.json"
    args = SimpleNamespace(
        gate_report=gate, gate_sha256=predecessor["gate_report_sha256"], contract_sha256=digest
    )
    supervisor._require_gate(args, contract)
    altered = tmp_path / "gate.json"
    altered.write_bytes(gate.read_bytes() + b" ")
    args.gate_report, args.gate_sha256 = altered, sha(altered.read_bytes())
    with pytest.raises(RuntimeError, match="historical 1000 negative evidence"):
        supervisor._require_gate(args, contract)


def test_tampered_negative_predecessor_is_rejected(monkeypatch):
    digest = sha(scaling.CONTRACT_V4_PATH.read_bytes())
    contract = scaling.load_contract(digest)
    gate = (
        Path(__file__).resolve().parents[2]
        / "docs/evidence/AGICORE_G2C_1000_9E6E_TIER_REPORT_20261111.json"
    )
    args = SimpleNamespace(
        gate_report=gate,
        gate_sha256=contract["predecessor"]["gate_report_sha256"],
        contract_sha256=digest,
    )
    original_read = supervisor.regular_read

    def tampered(path, **kwargs):
        value = original_read(path, **kwargs)
        return value + b" " if "NEGATIVE_20261111" in path.name else value

    monkeypatch.setattr(supervisor, "regular_read", tampered)
    with pytest.raises(RuntimeError, match="historical 1000 negative evidence"):
        supervisor._require_gate(args, contract)
