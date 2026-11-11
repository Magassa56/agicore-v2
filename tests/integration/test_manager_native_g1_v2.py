"""Versioned invented-only native V2 missions and their nonfinancial evidence."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from agicore.manager import mission_cycle_v2 as manager
from agicore.trading import ema_pullback_fees_and_slippage_v2 as accounting
from agicore.trading import ema_pullback_regime_gated_baseline_v2 as baseline
from agicore.trading import synthetic_mission_storage_v2 as producer
from agicore.trading import synthetic_mission_verify_v2 as verifier
from agicore.trading import synthetic_native_g1_v2 as native
from agicore.trading.synthetic_confirmation_fixture_v2 import PROFILES as RC1_PROFILES

# Canonical replay projections from RC1 commit 05b5af16; bundle/runtime
# measurements are excluded because they may vary across environments.
RC1_REPLAY_SHA256 = {
    "confirmation-long-v1": "7c412ec4d84b68cceb9231c5a4e2f1cacb47dc987f06563c5591f559b8cd978a",
    "confirmation-short-v1": "e9b8a62b507559e97af88013c908d7f9bb701fe0f8eabfa0f74ed78f938d597c",
    "confirmation-long-rejected-v1": "df8c5ba88cbdb234898f0064f7d8b18174a4d0b66560b8f0769ae5f642407eb5",
    "confirmation-short-rejected-v1": "ba2cba65ef72633482eb8f3f2e1f51666399b2f26709c1a534cd8092e918aeec",
    "confirmation-long-exit-stop-v1": "eda61604e948540fed94f536c0e6217030780efe39efd8daa18b068aed87f725",
    "confirmation-short-exit-stop-v1": "52ea7e3b47963b76f24e7ce5900a2a87dbf5dd1ed4869cc817e99b317938c3cb",
    "confirmation-long-exit-ema-v1": "f3579d5e982532df06919a6ada77d526d7fa03517931de0ec18d38526bbb5357",
    "confirmation-short-exit-ema-v1": "558ebf3c8644ec4374aee792c139c45d2c43a91cb34cdc55c07b24ef3e0c5aa8",
}


def _all_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _all_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_keys(item)


@pytest.mark.parametrize(
    "profile,direction", [(native.PROFILES[0], "LONG"), (native.PROFILES[1], "SHORT")]
)
def test_native_v2_two_successive_positions_and_suppressed_signal(profile, direction, monkeypatch):
    calls = []
    original = baseline.evaluate_synthetic_scenario_v2

    def record_native(**kwargs):
        calls.append(True)
        return original(**kwargs)

    monkeypatch.setattr(baseline, "evaluate_synthetic_scenario_v2", record_native)
    raw = native.generate_fixture(profile, 64)
    book = native.evaluate_profile(profile)
    result = native.project_worker(book, raw)
    assert calls == [True]
    assert len(result["positions"]) == 2 and result["end_state"] == "FLAT"
    first, second = result["positions"]
    assert [first["entry_bar_index"], second["entry_bar_index"]] == [36, 62]
    assert [first["confirmation_bar_index"], second["confirmation_bar_index"]] == [35, 61]
    assert [first["exit"]["bar_index"], second["exit"]["bar_index"]] == [56, 63]
    assert [first["exit"]["kind"], second["exit"]["kind"]] == ["EMA20", "STRUCTURAL_STOP"]
    assert first["exit"]["signal_bar_index"] + 1 == first["exit"]["bar_index"]
    assert first["exit"]["bar_index"] < second["source_bar_index"] < second["entry_bar_index"]
    assert all(
        p["direction"] == direction and p["approved_quantity"] in (1, 2)
        for p in result["positions"]
    )
    assert result["admissions"][40]["status"] == "SUPPRESSED_POSITION_OPEN"
    assert result["admissions"][40]["events"]
    assert not any(
        token in key.lower()
        for key in _all_keys(result)
        for token in ("pnl", "fee", "slippage", "profit", "performance")
    )


def test_native_evaluator_uses_existing_open_close_order(monkeypatch):
    calls = []
    original_open, original_close = (
        baseline.process_baseline_open_v2,
        baseline.process_baseline_close_v2,
    )

    def observe_open(*, previous, opening_bar):
        calls.append(("OPEN", opening_bar.bar_index))
        return original_open(previous=previous, opening_bar=opening_bar)

    def observe_close(*, previous, closed_bar):
        calls.append(("CLOSE", closed_bar.bar_index))
        return original_close(previous=previous, closed_bar=closed_bar)

    monkeypatch.setattr(baseline, "process_baseline_open_v2", observe_open)
    monkeypatch.setattr(baseline, "process_baseline_close_v2", observe_close)
    native.evaluate_profile(native.PROFILES[0])
    assert calls == [(phase, index) for index in range(64) for phase in ("OPEN", "CLOSE")]


def test_native_g1_really_uses_internal_accounting_on_invented_fills(monkeypatch):
    original = accounting.account_entry_fill_v2
    calls = []

    def record(**kwargs):
        calls.append(kwargs["decision"].confirmation_bar_index)
        return original(**kwargs)

    monkeypatch.setattr(accounting, "account_entry_fill_v2", record)
    native.evaluate_profile(native.PROFILES[0])
    assert set(calls) == {35, 61}


def test_future_bar_mutation_does_not_change_prior_native_decisions():
    raw = native.generate_fixture(native.PROFILES[0], 64)
    lines = [row.split(";") for row in raw.decode("ascii").splitlines()]
    lines[63][4] = "20017"
    altered = ("\n".join(";".join(row) for row in lines) + "\n").encode("ascii")
    original = native.project_worker(native._evaluate_invented(raw), raw)
    future_changed = native.project_worker(native._evaluate_invented(altered), altered)
    assert original["admissions"][:63] == future_changed["admissions"][:63]
    assert original["positions"][0] == future_changed["positions"][0]
    for key in (
        "source_bar_index",
        "pullback_bar_index",
        "confirmation_bar_index",
        "entry_bar_index",
        "direction",
        "approved_quantity",
    ):
        assert original["positions"][1][key] == future_changed["positions"][1][key]


def test_entry_open_is_independent_of_the_same_bar_unavailable_range():
    raw = native.generate_fixture(native.PROFILES[0], 64)
    rows = [row.split(";") for row in raw.decode("ascii").splitlines()]
    rows[36][2:5] = ["20008", "20003.5", "20005"]
    changed = ("\n".join(";".join(row) for row in rows) + "\n").encode("ascii")
    before = native._evaluate_invented(raw).policy.positions.positions[0].entry
    after = native._evaluate_invented(changed).policy.positions.positions[0].entry
    assert before == after and before.execution_bar_index == before.confirmation_bar_index + 1


def test_native_gap_stop_priority_expiry_and_open_end():
    raw = native.generate_fixture(native.PROFILES[0], 64)
    rows = [row.split(";") for row in raw.decode("ascii").splitlines()]

    def encoded(values):
        return ("\n".join(";".join(row) for row in values) + "\n").encode("ascii")

    collision = copy.deepcopy(rows)
    collision[56][1:5] = ["19998.5", "19999", "19998", "19998.75"]
    payload = encoded(collision)
    first = native.project_worker(native._evaluate_invented(payload), payload)["positions"][0]
    assert first["exit"]["kind"] == "STRUCTURAL_STOP"
    assert first["exit"]["bar_index"] == 56 and first["exit"]["phase"] == "BAR_OPEN_GAP"
    delayed = copy.deepcopy(rows)
    for row in delayed[36:]:
        stamp = datetime.strptime(row[0], "%Y%m%d %H%M%S") + timedelta(minutes=2)
        row[0] = stamp.strftime("%Y%m%d %H%M%S")
    payload = encoded(delayed)
    result = native.project_worker(native._evaluate_invented(payload), payload)
    assert all(position["entry_bar_index"] != 36 for position in result["positions"])
    payload = encoded(rows[:63])
    result = native.project_worker(native._evaluate_invented(payload), payload)
    assert len(result["positions"]) == 2 and result["positions"][-1]["exit"] is None
    assert result["end_state"] == "OPEN_UNREALIZED"


def test_native_failure_does_not_expose_internal_financial_exception(monkeypatch):
    def fail(**_kwargs):
        raise ValueError("PRIVATE_INTERNAL_FINANCIAL_VALUE")

    monkeypatch.setattr(baseline, "evaluate_synthetic_scenario_v2", fail)
    with pytest.raises(ValueError, match="native synthetic evaluation failed") as error:
        native.evaluate_profile(native.PROFILES[0])
    assert "PRIVATE_INTERNAL_FINANCIAL_VALUE" not in str(error.value)
    assert error.value.__suppress_context__ is True


@pytest.mark.parametrize("profile", native.PROFILES)
def test_verifier_recomputes_projection_without_producer_projection(profile, tmp_path, monkeypatch):
    bundle = tmp_path / "bundle"
    worker = producer.produce(bundle, 64, stage=native.STAGE, profile=profile)

    def forbidden(*_args, **_kwargs):
        pytest.fail("verifier called the producer projection")

    monkeypatch.setattr(native, "project_worker", forbidden)
    receipt = verifier.verify(bundle, 64, stage=native.STAGE, profile=profile)
    assert receipt["schema"] == native.VERIFICATION_SCHEMA
    assert receipt["scope"] == "INDEPENDENT_BUNDLE_AND_PROJECTION_SHARED_NATIVE_V2"
    assert receipt["replay"] == worker["replay"]


@pytest.mark.parametrize("field", ["quantity", "entry", "exit", "suppression", "financial"])
def test_verifier_rejects_forged_native_receipts_and_financial_fields(tmp_path, field):
    bundle = tmp_path / "bundle"
    worker = producer.produce(bundle, 64, stage=native.STAGE, profile=native.PROFILES[0])
    replay = worker["replay"]
    if field == "quantity":
        replay["positions"][1]["approved_quantity"] = 2
    elif field == "entry":
        replay["positions"][1]["entry_bar_index"] = 61
    elif field == "exit":
        replay["positions"][0]["exit"]["bar_index"] = 57
    elif field == "suppression":
        replay["admissions"][40]["status"] = "ADMITTED"
    else:
        worker["financial_result"] = "forbidden"
    (bundle / "worker.json").write_bytes(producer.canonical(worker))
    with pytest.raises(ValueError, match="independent verification"):
        verifier.verify(bundle, 64, stage=native.STAGE, profile=native.PROFILES[0])


def test_manager_precheck_rejects_noncausal_and_extra_fields():
    raw = native.generate_fixture(native.PROFILES[0], 64)
    replay = native.project_worker(native.evaluate_profile(native.PROFILES[0]), raw)
    worker = {"input_sha256": hashlib.sha256(raw).hexdigest()}
    mission = {"profile": native.PROFILES[0]}
    assert manager._valid_native_g1_replay(replay, worker, mission)
    for change in ("quantity", "entry", "exit", "suppression", "financial"):
        forged = copy.deepcopy(replay)
        if change == "quantity":
            forged["positions"][0]["approved_quantity"] = True
        elif change == "entry":
            forged["positions"][1]["entry_bar_index"] = 50
        elif change == "exit":
            forged["positions"][0]["exit"]["bar_index"] = 62
        elif change == "suppression":
            forged["admissions"][40]["status"] = "ADMITTED"
        else:
            forged["positions"][0]["pnl"] = "forbidden"
        assert not manager._valid_native_g1_replay(forged, worker, mission)


@pytest.mark.skipif(sys.platform != "linux", reason="bounded subprocess requires Linux")
@pytest.mark.parametrize("profile", native.PROFILES)
def test_two_independent_manager_runs_are_reproducible_without_financial_outputs(profile, tmp_path):
    receipts = []
    for name in ("first", "second"):
        root = tmp_path / name
        report = manager.run_mission(
            root, 64, stage=native.STAGE, profile=profile, timeout_seconds=60
        )
        contract = json.loads((root / "mission.json").read_bytes())
        assert report["status"] == "PASS" and report["schema"] == native.REPORT_SCHEMA
        assert contract["schema"] == native.MISSION_SCHEMA
        assert contract["authorizations"]["internal_accounting"] is True
        assert contract["authorizations"]["financial_output"] is False
        assert contract["authorizations"]["real_data"] is False
        assert contract["authorizations"]["orders"] is False
        source_name = "src/agicore/trading/synthetic_native_g1_v2.py"
        assert (
            contract["source_sha256"][source_name]
            == hashlib.sha256(Path(native.__file__).read_bytes()).hexdigest()
        )
        for field, value in (("schema", "agicore:mission:v2"), ("profile", "confirmation-long-v1")):
            forged = copy.deepcopy(contract)
            forged[field] = value
            with pytest.raises(manager.ResumeBlockedError):
                manager._validate_mission(forged)
        forged = copy.deepcopy(contract)
        forged["authorizations"]["financial_output"] = True
        with pytest.raises(manager.ResumeBlockedError):
            manager._validate_mission(forged)
        assert report["steps"]["worker"]["pid"] != report["steps"]["verifier"]["pid"]
        receipt = (root / "bundle" / "verification.json").read_bytes()
        receipts.append(receipt)
        for path in (
            root / "bundle" / "worker.json",
            root / "bundle" / "verification.json",
            root / "report.json",
        ):
            evidence = json.loads(path.read_bytes())
            replay = evidence.get("replay", evidence.get("verification", {}).get("replay"))
            assert not any(
                token in key.lower()
                for key in _all_keys(replay)
                for token in ("pnl", "fee", "slippage", "profit", "performance")
            )
        for path in (
            root / "worker.stdout",
            root / "worker.stderr",
            root / "verifier.stdout",
            root / "verifier.stderr",
        ):
            text = path.read_text(encoding="utf-8").lower()
            assert all(
                token not in text for token in ("net_realized_pnl", "total_fees", "profit_factor")
            )
    assert receipts[0] == receipts[1]


@pytest.mark.skipif(sys.platform != "linux", reason="bounded subprocess requires Linux")
def test_resume_runs_only_unstarted_verifier_and_rejects_source_changes(tmp_path, monkeypatch):
    class Interruption(BaseException):
        pass

    original_run = manager._run_process
    calls = []

    def record(*args, **kwargs):
        calls.append(args[2])
        return original_run(*args, **kwargs)

    def stop_after_worker(name):
        if name == "worker_completed":
            raise Interruption()

    root = tmp_path / "mission"
    monkeypatch.setattr(manager, "_run_process", record)
    monkeypatch.setattr(manager, "_checkpoint", stop_after_worker)
    with pytest.raises(Interruption):
        manager.run_mission(
            root, 64, stage=native.STAGE, profile=native.PROFILES[0], timeout_seconds=60
        )
    before = (root / "bundle" / "worker.json").read_bytes()
    assert calls == ["worker"]
    original_hashes = manager._source_hashes
    monkeypatch.setattr(manager, "_source_hashes", lambda: {"changed": "0" * 64})
    with pytest.raises(manager.ResumeBlockedError, match="sources"):
        manager.resume_mission(root)
    assert calls == ["worker"]
    monkeypatch.setattr(manager, "_source_hashes", original_hashes)
    monkeypatch.setattr(manager, "_checkpoint", lambda _name: None)
    report = manager.resume_mission(root)
    assert report["status"] == "PASS" and calls == ["worker", "verifier"]
    assert (root / "bundle" / "worker.json").read_bytes() == before
    assert manager.resume_mission(root) == report and calls == ["worker", "verifier"]


@pytest.mark.skipif(sys.platform != "linux", reason="bounded subprocess requires Linux")
def test_ambiguous_running_native_worker_is_not_reexecuted(tmp_path, monkeypatch):
    class Interruption(BaseException):
        pass

    calls = []

    def interrupt(*_args):
        calls.append("worker")
        raise Interruption()

    root = tmp_path / "mission"
    monkeypatch.setattr(manager, "_run_process", interrupt)
    with pytest.raises(Interruption):
        manager.run_mission(
            root, 64, stage=native.STAGE, profile=native.PROFILES[0], timeout_seconds=60
        )
    with pytest.raises(manager.ResumeBlockedError):
        manager.resume_mission(root)
    assert calls == ["worker"]


@pytest.mark.skipif(sys.platform != "linux", reason="bounded subprocess requires Linux")
def test_native_resume_refuses_tampered_completed_worker(tmp_path, monkeypatch):
    class Interruption(BaseException):
        pass

    def stop_after_worker(name):
        if name == "worker_completed":
            raise Interruption()

    root = tmp_path / "mission"
    monkeypatch.setattr(manager, "_checkpoint", stop_after_worker)
    with pytest.raises(Interruption):
        manager.run_mission(
            root, 64, stage=native.STAGE, profile=native.PROFILES[0], timeout_seconds=60
        )
    path = root / "bundle" / "worker.json"
    worker = json.loads(path.read_bytes())
    worker["replay"]["positions"][0]["approved_quantity"] = 1
    path.write_bytes(producer.canonical(worker))
    monkeypatch.setattr(manager, "_checkpoint", lambda _name: None)
    with pytest.raises(manager.ResumeBlockedError):
        manager.resume_mission(root)
    assert not (root / "bundle" / "verification.json").exists()


@pytest.mark.skipif(sys.platform != "linux", reason="bounded subprocess requires Linux")
@pytest.mark.parametrize("profile", RC1_PROFILES)
def test_historical_rc1_profiles_never_account_in_either_process(profile, tmp_path, monkeypatch):
    guard_dir = tmp_path / "guard"
    guard_dir.mkdir()
    (guard_dir / "sitecustomize.py").write_text(
        "import os, sys\n"
        "with open(os.environ['RC1_GUARD_LOG'], 'a', encoding='ascii') as stream:\n"
        "    stream.write(str(os.getpid()) + '\\n')\n"
        "def guard(frame, event, arg):\n"
        "    code = frame.f_code\n"
        "    if event == 'call' and code.co_filename.endswith('/ema_pullback_fees_and_slippage_v2.py') and code.co_flags & 1:\n"
        "        raise RuntimeError('RC1 accounting is forbidden')\n"
        "sys.setprofile(guard)\n",
        encoding="ascii",
    )
    probe_env = dict(os.environ)
    probe_env["PYTHONPATH"] = os.pathsep.join(
        (str(guard_dir), str(manager.REPOSITORY / "src"), str(manager.REPOSITORY))
    )
    probe_env["RC1_GUARD_LOG"] = str(tmp_path / "probe.log")
    probe = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            "from agicore.trading.ema_pullback_fees_and_slippage_v2 import report_usd_cents_v2; report_usd_cents_v2(1)",
        ],
        env=probe_env,
        capture_output=True,
        check=False,
    )
    assert probe.returncode != 0 and b"RC1 accounting is forbidden" in probe.stderr
    log = tmp_path / "guard.log"
    real_popen = subprocess.Popen

    def guarded_popen(command, **kwargs):
        env = dict(kwargs["env"])
        env["PYTHONPATH"] = str(guard_dir) + os.pathsep + env["PYTHONPATH"]
        env["RC1_GUARD_LOG"] = str(log)
        kwargs["env"] = env
        return real_popen(command, **kwargs)

    monkeypatch.setattr(manager.subprocess, "Popen", guarded_popen)
    root = tmp_path / "mission"
    report = manager.run_mission(root, 39, stage="exit", profile=profile, timeout_seconds=60)
    contract = json.loads((root / "mission.json").read_bytes())
    assert report["status"] == "PASS" and report["schema"] == "agicore:mission-report:v2"
    assert contract["schema"] == "agicore:mission:v2"
    assert "internal_accounting" not in contract["authorizations"]
    replay_bytes = producer.canonical(report["verification"]["replay"])
    assert hashlib.sha256(replay_bytes).hexdigest() == RC1_REPLAY_SHA256[profile]
    assert set(map(int, log.read_text(encoding="ascii").splitlines())) == {
        report["steps"]["worker"]["pid"],
        report["steps"]["verifier"]["pid"],
    }


def test_native_profile_cannot_escape_the_versioned_contract(tmp_path):
    root = tmp_path / "refused"
    for observations, stage, profile in (
        (63, native.STAGE, native.PROFILES[0]),
        (64, "exit", native.PROFILES[0]),
        (64, native.STAGE, "standard"),
    ):
        with pytest.raises(ValueError):
            manager.run_mission(root, observations, stage=stage, profile=profile)
        assert not root.exists()
