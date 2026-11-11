"""G2 checks for bounded supervision and a separate storage verifier process."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("resource")

from agicore.trading.ema_pullback_v2_storage_format import (
    ROOT,
    StorageProofError,
    codec_profile,
    sha,
)
from tests.unit.trading.v2_recovery_storage_fixtures import synthetic_raw
from tools import ema_pullback_v2_storage_g2_guard as g2_guard
from tools.ema_pullback_v2_storage_g2_guard import run_precommitted_native, supervise_checked
from tools.ema_pullback_v2_storage_synthetic_proof import verify_registration

REGISTRATION = (
    ROOT / "docs/evidence/EMA_PULLBACK_V2_RECOVERY_STORAGE_CI_PORTABLE_SOURCE_REGISTRATION_V1.json"
)

# No producer, runner, or strategy is imported in this independent process.
VERIFIER = r"""
import json
import os
import resource
import sys
import time
from pathlib import Path
from agicore.trading.ema_pullback_v2_recovery_storage_verifier import verify_synthetic_bundle
from agicore.trading.ema_pullback_v2_storage_format import StorageProofError, codec_profile, sha

resource.setrlimit(resource.RLIMIT_AS, (536870912, 536870912))
args = json.load(sys.stdin)
started = time.perf_counter_ns()
try:
    decoded, verification = verify_synthetic_bundle(
        Path(args['bundle']),
        expected_manifest_sha=args['manifest_sha'],
        expected_bindings=args['bindings'],
        expected_profile=codec_profile(),
        expected_native_sha=args['native_sha'],
        synthetic_raw=Path(args['source']).read_bytes(),
    )
except StorageProofError:
    print(json.dumps({'status': 'REJECTED'}))
    raise SystemExit(2)
for forbidden in ('agicore.trading.ema_pullback_v2_recovery_storage',
                  'agicore.trading.ema_pullback_v2_development_replay',
                  'agicore.trading.ema_pullback_regime_gated_baseline_v2'):
    if forbidden in sys.modules:
        raise SystemExit('verifier imported producer or strategy')
print(json.dumps({'status': verification['status'], 'native_sha': sha(decoded), 'pid': os.getpid(),
                  'wall_ns': time.perf_counter_ns() - started,
                  'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024}))
"""


@pytest.fixture(scope="module")
def proof_cases(tmp_path_factory):
    """Create two separately bounded executions of a precommitted invented fixture."""
    root = tmp_path_factory.mktemp("g2-precommitted")
    source, inventory = verify_registration(REGISTRATION, formal=False)
    fixture = "impulse_profit_LONG"
    results = []
    for number in (1, 2):
        destination = root / f"native-{number}"
        checked = run_precommitted_native(
            destination, fixture, formal=codec_profile() == inventory["codec_profile"]
        )
        assert checked["g2_status"] == "PASS"
        assert (
            checked["g2_total_physical_bytes"] <= inventory["limits"]["synthetic_case_output_bytes"]
        )
        persisted = json.loads((root / f"native-{number}.g2-receipt.json").read_bytes())
        assert persisted == checked["g2_receipt"]
        assert persisted["status"] == "MEASURED_BEFORE_RECEIPT"
        assert persisted["g2_guard_sha256"] == sha(Path(g2_guard.__file__).read_bytes())
        production = json.loads((destination / "bundle/production-receipt.json").read_bytes())
        assert (
            production["bindings"]["complete_source_closure_sha256"]
            == source["complete_source_closure_sha256"]
        )
        assert (
            production["bindings"]["verifier_source_closure_sha256"]
            == source["verifier_source_closure_sha256"]
        )
        assert (destination / "synthetic-source.Last.txt").read_bytes() == synthetic_raw(fixture)
        results.append((destination, checked, production))
    return results


def verify_in_fresh_process(case: Path, production: dict, *, bundle=None, source=None):
    """Pass externally retained commitments to a separately imported verifier."""
    arguments = {
        "bundle": str(bundle or case / "bundle"),
        "source": str(source or case / "synthetic-source.Last.txt"),
        "manifest_sha": production["bundle_manifest_sha256"],
        "bindings": production["bindings"],
        "native_sha": production["logical_native_file_sha256"],
    }
    return subprocess.run(
        [sys.executable, "-B", "-c", VERIFIER],
        input=json.dumps(arguments),
        text=True,
        capture_output=True,
        timeout=30,
        cwd=ROOT,
        check=False,
    )


def test_fresh_bounded_workers_reconstruct_identical_native_bytes(proof_cases):
    """Repetition does not normalize or omit any native output fields."""
    first, second = proof_cases
    first_raw = (first[0] / "reference-native.json").read_bytes()
    second_raw = (second[0] / "reference-native.json").read_bytes()
    assert first_raw == second_raw
    assert sha(first_raw) == first[2]["logical_native_file_sha256"]
    assert sha(second_raw) == second[2]["logical_native_file_sha256"]
    assert all(case[1]["legacy_receipt"]["result"]["exact_bytes"] for case in proof_cases)


def test_reconstruction_is_a_separate_process_without_strategy_imports(proof_cases):
    case, _, production = proof_cases[0]
    result = verify_in_fresh_process(case, production)
    assert result.returncode == 0, result.stderr
    proof = json.loads(result.stdout)
    assert proof["status"] == "PASS"
    assert proof["native_sha"] == production["logical_native_file_sha256"]
    assert type(proof["pid"]) is int and proof["pid"] > 0
    assert proof["pid"] != json.loads((case / "START.json").read_bytes())["pid"]
    assert proof["wall_ns"] > 0 and proof["peak_rss_bytes"] > 0


@pytest.mark.parametrize("corruption", ["object", "seal", "source"])
def test_separate_verifier_rejects_tampering_and_partial_output(proof_cases, tmp_path, corruption):
    case, _, production = proof_cases[0]
    bundle = tmp_path / "bundle"
    shutil.copytree(case / "bundle", bundle)
    source = tmp_path / "invented-source.txt"
    source.write_bytes((case / "synthetic-source.Last.txt").read_bytes())
    if corruption == "object":
        obj = next((bundle / "objects").rglob("*.blob"))
        raw = obj.read_bytes()
        obj.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
    elif corruption == "seal":
        (bundle / "completion-seal.json").unlink()
    else:
        raw = source.read_bytes()
        source.write_bytes(raw[:-2] + b"1\n")
    result = verify_in_fresh_process(case, production, bundle=bundle, source=source)
    assert result.returncode == 2, result.stderr
    assert json.loads(result.stdout) == {"status": "REJECTED"}


def simulated_legacy_pass(_command, destination, _timeout, _limit):
    """Represent a worker that exited successfully between resource samples."""
    destination.mkdir()
    (destination / "END.json").write_text('{"completion":"PASS"}\n')
    for suffix in (".log", ".supervision.jsonl", ".receipt.json"):
        (destination.parent / (destination.name + suffix)).write_bytes(b"legacy\n")
    return {"peak_process_tree_memory_bytes": 2}


def test_final_storage_cap_rejects_fast_worker_and_preserves_legacy_receipt(tmp_path, monkeypatch):
    destination = tmp_path / "fast-storage"
    monkeypatch.setattr(g2_guard, "supervise_one", simulated_legacy_pass)
    with pytest.raises(StorageProofError, match="final case storage limit exceeded"):
        supervise_checked([], destination, 5, 1)
    assert (tmp_path / "fast-storage.receipt.json").is_file()


def test_final_memory_cap_rejects_worker_after_exit(tmp_path, monkeypatch):
    destination = tmp_path / "fast-memory"
    monkeypatch.setattr(g2_guard, "supervise_one", simulated_legacy_pass)
    with pytest.raises(StorageProofError, match="final process memory limit exceeded"):
        supervise_checked([], destination, 5, 1_000_000, memory_limit=1)


def test_final_timeout_rejects_worker_that_finishes_between_samples(tmp_path, monkeypatch):
    destination = tmp_path / "fast-timeout"
    monkeypatch.setattr(g2_guard, "supervise_one", simulated_legacy_pass)
    times = iter((0, 2_000_000_000))
    monkeypatch.setattr(g2_guard.time, "perf_counter_ns", lambda: next(times, 2_000_000_000))
    with pytest.raises(StorageProofError, match="final case elapsed time limit exceeded"):
        supervise_checked([], destination, 1, 1_000_000)


def test_g2_runner_rejects_unregistered_fixture_before_start(tmp_path):
    destination = tmp_path / "bad-fixture"
    with pytest.raises(StorageProofError, match="fixture is not precommitted"):
        run_precommitted_native(destination, "unregistered-invented-fixture", formal=False)
    assert not destination.exists()


def test_g2_runner_rejects_source_registration_drift_before_start(tmp_path, monkeypatch):
    destination = tmp_path / "bad-registration"
    monkeypatch.setattr(g2_guard, "REGISTRATION_SHA256", "0" * 64)
    with pytest.raises(StorageProofError, match="source registration identity changed"):
        run_precommitted_native(destination, "impulse_profit_LONG", formal=False)
    assert not destination.exists()
