"""Exercise the fixed invented confirmation profiles through the unified manager."""

import json
import sqlite3

import pytest

from agicore.manager import mission_cycle_v2 as manager


@pytest.mark.parametrize("direction", ["long", "short"])
def test_confirmed_profile_passes_through_orchestrator_and_verifier(tmp_path, direction):
    profile = f"confirmation-{direction}-v1"
    root = tmp_path / direction
    report = manager.run_mission(
        root, 39, stage="confirmation", profile=profile, timeout_seconds=20
    )
    assert report["status"] == "PASS"
    assert report["orchestrator"] == "AgentOrchestrator+Dispatcher"
    assert report["profile"] == profile
    assert report["verification"]["profile"] == profile
    replay = report["verification"]["replay"]
    assert replay["input_observations"] == 39
    assert replay["processed_observations"] == 36
    assert replay["counts"]["confirmations_qualified"] == 1
    assert replay["stop_reason"] == "CONFIRMED_BEFORE_RISK"
    mission = json.loads((root / "mission.json").read_bytes())
    assert mission["profile"] == profile
    assert mission["authorizations"]["confirmation"] is True
    assert mission["authorizations"]["orders"] is False
    with sqlite3.connect(root / "orchestrator.sqlite3") as db:
        rows = db.execute("select assigned_to, status from tasks order by assigned_to").fetchall()
    assert rows == [("verifier", "completed"), ("worker", "completed")]
    assert manager.resume_mission(root) == report


def test_profile_is_bound_across_interruption_and_cannot_be_swapped(tmp_path, monkeypatch):
    class Interruption(BaseException):
        pass

    root = tmp_path / "interrupted"

    def crash(name):
        if name == "worker_completed":
            raise Interruption()

    monkeypatch.setattr(manager, "_checkpoint", crash)
    with pytest.raises(Interruption):
        manager.run_mission(
            root, 39, stage="confirmation", profile="confirmation-long-v1", timeout_seconds=20
        )
    mission_path = root / "mission.json"
    original = mission_path.read_bytes()
    mission = json.loads(original)
    mission["profile"] = "confirmation-short-v1"
    mission_path.write_bytes(manager.canonical(mission))
    with pytest.raises(manager.ResumeBlockedError, match="binding"):
        manager.resume_mission(root)
    mission_path.write_bytes(original)
    monkeypatch.setattr(manager, "_checkpoint", lambda name: None)
    report = manager.resume_mission(root)
    assert report["status"] == "PASS"
    assert report["profile"] == "confirmation-long-v1"
    assert report["verification"]["replay"]["stop_reason"] == "CONFIRMED_BEFORE_RISK"


@pytest.mark.parametrize("stage,count", [("pullback", 39), ("confirmation", 40)])
def test_invalid_profile_is_refused_before_creating_directory(tmp_path, stage, count):
    root = tmp_path / "invalid"
    with pytest.raises(ValueError, match="confirmation profiles"):
        manager.run_mission(root, count, stage=stage, profile="confirmation-long-v1")
    assert not root.exists()
