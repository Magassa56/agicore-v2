"""Read-only plan validation and tamper rejection without launching any worker."""

from __future__ import annotations

import json
import subprocess

import pytest

from agicore.trading.ema_pullback_v2_storage_format import StorageProofError, canonical, sha
from tools import ema_pullback_v2_g2c_parity_v3 as v3
from tools import ema_pullback_v2_g2c_parity_v3_plan_check as check
from tools import ema_pullback_v2_g2c_supervised_v51 as v51
from tools import ema_pullback_v2_g2c_supervisor as supervisor

PLAN_SHA = "4baa39605bd3b05bd177681d0c382e923237541c770af648f35b83f47dcf552c"


def test_plan_and_synthetic_fixture_identities_without_workers(monkeypatch):
    def forbidden(*_args, **_kwargs):
        pytest.fail("worker or subprocess launch forbidden")

    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(supervisor, "run_worker", forbidden)
    monkeypatch.setattr(supervisor, "run_tier", forbidden)
    monkeypatch.setattr(v3, "worker", forbidden)
    monkeypatch.setattr(v3, "run_tier", forbidden)
    monkeypatch.setattr(v3.v2, "worker", forbidden)
    monkeypatch.setattr(v3.v2, "run_tier", forbidden)
    monkeypatch.setattr(v51, "run_tier", forbidden)
    result = check.check_plan(PLAN_SHA)
    assert result["status"] == "PASS"
    assert result["workers_launched"] == 0 and result["replay_executed"] is False
    assert result["host_execution_preflight"] == "NOT_RUN"
    assert result["fixtures"] == {
        "constant-5000": {
            "observations": 5000,
            "input_sha256": "1814dda83d238dbd2b11872a87b014caece63088534d234a53b8c5ee19c8e831",
        },
        "dense-5000": {
            "observations": 5000,
            "input_sha256": "5ca76d6d3fe70d2209c72c34f3199aa378e9d3d5ef9aa4f9a6723af469799ddc",
        },
    }
    assert result["limits"] == check.LIMITS


def test_external_plan_sha_is_mandatory():
    for digest in ("0" * 64, "not-a-digest"):
        with pytest.raises(StorageProofError):
            check.check_plan(digest)


def test_changed_v3_registration_is_rejected(tmp_path, monkeypatch):
    forged = tmp_path / "registration.json"
    forged.write_bytes(v3.REGISTRATION.read_bytes() + b" ")
    monkeypatch.setattr(v3, "REGISTRATION", forged)
    with pytest.raises(StorageProofError, match="external parity V3 registration"):
        check.check_plan(PLAN_SHA)


def test_rehashed_modified_plan_and_noncanonical_bytes_are_rejected(tmp_path, monkeypatch):
    original = check.PLAN_PATH.read_bytes()
    document = json.loads(original)
    document["plan"]["v2_plan"]["v51_plan"]["roles"].reverse()
    v2_plan = document["plan"]["v2_plan"]
    v2_plan["v51_plan_sha256"] = sha(canonical(v2_plan["v51_plan"]))
    document["plan"]["v2_plan_sha256"] = sha(canonical(v2_plan))
    forged_plan_sha = sha(canonical(document["plan"]))
    document["plan_sha256"] = forged_plan_sha
    forged = tmp_path / "forged-plan.json"
    forged.write_bytes(canonical(document))
    monkeypatch.setattr(check, "PLAN_PATH", forged)
    with pytest.raises(StorageProofError, match="plan identity or regenerated plan"):
        check.check_plan(forged_plan_sha)
    forged.write_bytes(original + b" ")
    with pytest.raises(StorageProofError):
        check.check_plan(PLAN_SHA)


def test_forged_gate_is_rejected_before_fixture_generation(tmp_path, monkeypatch):
    gate = tmp_path / "gate.json"
    gate.write_bytes(v51.GATE.read_bytes() + b" ")
    monkeypatch.setattr(v51, "GATE", gate)
    monkeypatch.setattr(
        check.scaling, "invented_fixture", lambda *_: pytest.fail("fixture must not be generated")
    )
    with pytest.raises(RuntimeError, match="1000 gate identity"):
        check.check_plan(PLAN_SHA)


def test_changed_fixture_bytes_are_rejected(monkeypatch):
    monkeypatch.setattr(check.scaling, "invented_fixture", lambda *_: b"invented\n")
    with pytest.raises(StorageProofError, match="invented fixture identity"):
        check.check_plan(PLAN_SHA)
