"""Mission lifecycle, bounded execution and failure behavior."""

from __future__ import annotations

import json

import pytest

from agicore.manager import mission_cycle_v2 as manager


def test_end_to_end_mission_assigns_runs_verifies_and_reports(tmp_path):
    directory = tmp_path / "mission"
    report = manager.run_mission(directory, 64, timeout_seconds=20)
    assert report["status"] == "PASS"
    assert report["verification"]["observations"] == 64
    assert report["steps"]["worker"]["exit_code"] == 0
    assert report["steps"]["verifier"]["exit_code"] == 0
    assert report["steps"]["worker"]["pid"] > 0
    assert report["steps"]["verifier"]["pid"] > 0
    assert json.loads((directory / "report.json").read_bytes()) == report
    mission = json.loads((directory / "mission.json").read_bytes())
    assert mission["retries"] == 0 and mission["network_or_model_calls"] is False
    events = [json.loads(row) for row in (directory / "events.jsonl").read_bytes().splitlines()]
    assert [(e["agent_id"], e["state"]) for e in events] == [
        ("manager", "CREATED"),
        ("worker", "ASSIGNED"),
        ("worker", "STARTED"),
        ("worker", "COMPLETED"),
        ("verifier", "ASSIGNED"),
        ("verifier", "STARTED"),
        ("verifier", "COMPLETED"),
        ("manager", "PASS"),
    ]
    assert all(
        e["task_id"] == report["task_id"] and e["timestamp_utc"].endswith("+00:00") for e in events
    )


def test_worker_failure_prevents_verification_and_is_reported(tmp_path, monkeypatch):
    called = []

    def fail_once(root, module, role, observations, timeout):
        called.append(role)
        return {"exit_code": 1, "timeout": False, "stderr": "worker.stderr"}

    monkeypatch.setattr(manager, "_run_process", fail_once)
    report = manager.run_mission(tmp_path / "failed", 64)
    assert report["status"] == "FAILED" and called == ["worker"]
    assert "verifier" not in report["steps"]
    assert json.loads((tmp_path / "failed" / "report.json").read_bytes())["error"]


def test_zero_exit_without_receipts_never_passes(tmp_path, monkeypatch):
    def fake_success(root, module, role, observations, timeout):
        return {"exit_code": 0, "timeout": False, "stderr": f"{role}.stderr"}

    monkeypatch.setattr(manager, "_run_process", fake_success)
    report = manager.run_mission(tmp_path / "no-receipts", 64)
    assert report["status"] == "FAILED"
    assert "invalid verification receipt" in report["error"]


def test_timeout_stops_without_starting_verifier(tmp_path):
    report = manager.run_mission(tmp_path / "timeout", 89_841, timeout_seconds=1)
    assert report["status"] == "FAILED"
    assert report["steps"]["worker"]["timeout"] is True
    assert "verifier" not in report["steps"]


def test_existing_directory_and_data_path_are_refused(tmp_path):
    existing = tmp_path / "existing"
    existing.mkdir()
    with pytest.raises(FileExistsError):
        manager.run_mission(existing, 1)
    data = tmp_path / "data"
    with pytest.raises(ValueError, match="non-data"):
        manager.run_mission(data / "forbidden", 1)
    assert not data.exists()


def test_symlink_parent_is_refused(tmp_path):
    link = tmp_path / "alias"
    link.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ValueError, match="symlinks"):
        manager.run_mission(link / "mission", 1)


@pytest.mark.parametrize("count,timeout", [(0, 1), (89_842, 1), (1, 0), (1, 301)])
def test_invalid_limits_are_rejected_without_output(tmp_path, count, timeout):
    directory = tmp_path / "invalid"
    with pytest.raises(ValueError):
        manager.run_mission(directory, count, timeout_seconds=timeout)
    assert not directory.exists()
