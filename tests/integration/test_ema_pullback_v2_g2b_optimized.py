"""Bounded G2B parity, provenance, storage and independent verification tests."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import asdict, replace
from decimal import Decimal

import pytest

from agicore.trading import ema_pullback_v2_development_replay as reference
from agicore.trading import ema_pullback_v2_recovery_optimized as optimized
from agicore.trading.ema_pullback_v2_g2b_audit import audit_optimized_native, source_witnesses
from agicore.trading.ema_pullback_v2_g2b_contract import (
    CONTRACT_PATH,
    MAX_OBSERVATIONS,
    RUNNER_SHA256,
    _source_files_match,
    generate_fixture,
    load_contract,
)
from agicore.trading.ema_pullback_v2_g2b_segments import decode_segments, encode_segments
from agicore.trading.ema_pullback_v2_g2b_storage import produce_bundle
from agicore.trading.ema_pullback_v2_g2b_verifier import verify_bundle
from agicore.trading.ema_pullback_v2_recovery_evidence import CanonicalEncoderV1
from agicore.trading.ema_pullback_v2_storage_format import (
    MAX_NATIVE_BYTES,
    ROOT,
    StorageProofError,
    canonical,
    codec_profile,
    parse_canonical,
    sha,
)
from agicore.trading.regime_context_v2 import RegimeDirection
from tests.unit.trading.test_ema_pullback_regime_gated_baseline_v2 import _scenario
from tests.unit.trading.test_ema_pullback_v2_development_replay import _raw

CASES = (
    "impulse_profit_LONG",
    "impulse_profit_SHORT",
    "gap_stop_LONG",
    "gap_stop_SHORT",
    "position_suppressed_LONG",
    "context_elapsed_SHORT",
    "entry_gap_LONG",
    "risk_reject_SHORT",
    "open_eof_LONG",
    "dense_gapped_LONG",
    "dense_gapped_SHORT",
    "invented-scale-201-v1",
    "invented-multitrade-201-v1",
)


@pytest.fixture(scope="module")
def registered():
    """Use the checked-in contract SHA as the test's explicit trust anchor."""
    digest = hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest()
    return digest, load_contract(digest)


@pytest.mark.parametrize("fixture", CASES)
def test_frozen_reference_and_optimized_causal_financial_parity(registered, fixture):
    """Normalize two identity fields only in this temporary differential test."""
    _, contract = registered
    raw = generate_fixture(contract, fixture)
    bindings = reference.read_frozen_replay_bindings_v2()
    original = reference.evaluate_synthetic_development_replay_v2(raw, bindings=bindings)
    candidate, identity = optimized.run_synthetic_native_v1(raw, bindings=bindings)
    assert identity.runner_source_sha256 == RUNNER_SHA256
    assert candidate["run_identity"] == asdict(identity)
    encoder = CanonicalEncoderV1()
    optimized_bytes = encoder.bytes(candidate)
    assert optimized_bytes != original.canonical_utf8
    reference_identity = reference.build_replay_run_identity_v2(identity.dataset_raw_sha256)
    projected = dict(candidate)
    projected["run_identity"] = asdict(reference_identity)
    projected["run_id_sha256"] = reference_identity.sha256
    projected["output_sha256"] = encoder.sha256(
        {key: value for key, value in projected.items() if key != "output_sha256"}
    )
    assert encoder.bytes(projected) == original.canonical_utf8
    if fixture.startswith("dense_gapped_") or fixture == "invented-multitrade-201-v1":
        assert len(candidate["closed_trade_records"]) >= 2
    if fixture.startswith("gap_stop_"):
        assert (
            candidate["immutable_lifecycle_records"]["exits"][0]["trigger_phase"] == "BAR_OPEN_GAP"
        )
    if fixture == "position_suppressed_LONG":
        assert candidate["metrics"]["suppressed_position_open_events"] >= 1
    if fixture == "context_elapsed_SHORT":
        assert candidate["metrics"]["expired_contexts"] >= 1
    if fixture == "risk_reject_SHORT":
        assert candidate["metrics"]["risk_rejections"] >= 1
        assert candidate["metrics"]["entry_fills"] == 0
    if fixture == "open_eof_LONG":
        assert len(candidate["open_trade_records"]) == 1


def test_optimized_future_mutation_does_not_change_prior_decisions():
    """A later invented bar cannot revise prior entries or marked samples."""
    bars = _scenario("impulse_profit", RegimeDirection.LONG)
    changed = dict(bars)
    changed[56] = replace(
        bars[56], open=Decimal(20100), high=Decimal(20101), low=Decimal(19999), close=Decimal(20020)
    )
    bindings = reference.read_frozen_replay_bindings_v2()
    original, _ = optimized.run_synthetic_native_v1(_raw(bars), bindings=bindings)
    mutated, _ = optimized.run_synthetic_native_v1(_raw(changed), bindings=bindings)
    assert original["marked_equity_samples"][:56] == mutated["marked_equity_samples"][:56]
    for name in (
        "events",
        "contexts",
        "pullbacks",
        "confirmations",
        "stops",
        "risk_decisions",
        "entries",
    ):
        assert (
            original["immutable_lifecycle_records"][name]
            == mutated["immutable_lifecycle_records"][name]
        )


@pytest.fixture(scope="module")
def completed_bundle(tmp_path_factory, registered):
    digest, _ = registered
    bundle = tmp_path_factory.mktemp("g2b-invented") / "bundle"
    base = [
        sys.executable,
        "-B",
        "-m",
        "tools.ema_pullback_v2_g2b_synthetic",
        "--contract-sha256",
        digest,
        "--bundle",
        str(bundle),
    ]
    producer = subprocess.run(
        base + ["--role", "produce", "--fixture", "invented-multitrade-201-v1"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert producer.returncode == 0, producer.stderr
    receipt = json.loads(producer.stdout)
    command = base + [
        "--role",
        "verify",
        "--manifest-sha256",
        receipt["manifest_sha256"],
        "--native-sha256",
        receipt["native_sha256"],
    ]
    verifier = subprocess.run(
        command + ["--seal"], cwd=ROOT, capture_output=True, text=True, timeout=60, check=False
    )
    assert verifier.returncode == 0, verifier.stderr
    assert json.loads(verifier.stdout)["audit"]["observation_count"] == 201
    repeated = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True, timeout=60, check=False
    )
    assert repeated.returncode == 0, repeated.stderr
    assert json.loads(repeated.stdout) == json.loads(verifier.stdout)
    return bundle, receipt, digest


def test_separate_producer_verifier_preserves_original_identity(completed_bundle):
    bundle, receipt, digest = completed_bundle
    native_bytes, audit = verify_bundle(
        bundle,
        expected_contract_sha256=digest,
        expected_manifest_sha256=receipt["manifest_sha256"],
        expected_native_sha256=receipt["native_sha256"],
    )
    document = parse_canonical([native_bytes], limit=33_554_432)
    assert document["run_identity"]["runner_source_sha256"] == RUNNER_SHA256
    assert len(document["closed_trade_records"]) == 2
    assert audit["runner_sha256"] == RUNNER_SHA256
    assert audit["audit"]["strategy_recomputed"] is False
    assert sha(native_bytes) == receipt["native_sha256"]


def test_stored_two_trade_result_receives_independent_financial_audit(registered, tmp_path):
    digest, _ = registered
    bundle = tmp_path / "bundle"
    receipt = produce_bundle(bundle, "dense_gapped_LONG", expected_contract_sha256=digest)
    command = [
        sys.executable,
        "-B",
        "-m",
        "tools.ema_pullback_v2_g2b_synthetic",
        "--role",
        "verify",
        "--bundle",
        str(bundle),
        "--contract-sha256",
        digest,
        "--manifest-sha256",
        receipt["manifest_sha256"],
        "--native-sha256",
        receipt["native_sha256"],
        "--seal",
    ]
    result = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True, timeout=60, check=False
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["audit"]["status"] == "PASS"
    native_bytes, verification = verify_bundle(
        bundle,
        expected_contract_sha256=digest,
        expected_manifest_sha256=receipt["manifest_sha256"],
        expected_native_sha256=receipt["native_sha256"],
    )
    document = parse_canonical([native_bytes], limit=33_554_432)
    assert len(document["closed_trade_records"]) == 2
    assert verification["audit"]["status"] == "PASS"
    assert document["run_identity"]["runner_source_sha256"] == RUNNER_SHA256


def test_second_independent_producer_has_identical_bytes(completed_bundle, tmp_path):
    _, receipt, digest = completed_bundle
    command = [
        sys.executable,
        "-B",
        "-m",
        "tools.ema_pullback_v2_g2b_synthetic",
        "--role",
        "produce",
        "--contract-sha256",
        digest,
        "--bundle",
        str(tmp_path / "second"),
        "--fixture",
        "invented-multitrade-201-v1",
    ]
    result = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True, timeout=60, check=False
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == receipt


def test_verifier_process_never_imports_strategy_or_producer(completed_bundle):
    bundle, receipt, digest = completed_bundle
    script = """
import json,sys
from pathlib import Path
from agicore.trading.ema_pullback_v2_g2b_verifier import verify_bundle
p=json.load(sys.stdin)
_,v=verify_bundle(Path(p['bundle']),expected_contract_sha256=p['contract'],
    expected_manifest_sha256=p['manifest'],expected_native_sha256=p['native'])
for n in ('agicore.trading.ema_pullback_v2_g2b_storage',
          'agicore.trading.ema_pullback_v2_recovery_optimized',
          'agicore.trading.ema_pullback_regime_gated_baseline_v2'):
    assert n not in sys.modules
print(v['status'])
"""
    result = subprocess.run(
        [sys.executable, "-B", "-c", script],
        cwd=ROOT,
        input=json.dumps(
            {
                "bundle": str(bundle),
                "contract": digest,
                "manifest": receipt["manifest_sha256"],
                "native": receipt["native_sha256"],
            }
        ),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "PASS"


@pytest.mark.parametrize(
    "fixture", ["impulse_profit_LONG", "invented-scale-201-v1", "invented-multitrade-201-v1"]
)
def test_producer_loaded_repository_sources_are_registered(registered, tmp_path, fixture):
    digest, _ = registered
    script = """
import json,sys
from pathlib import Path
from agicore.trading.ema_pullback_v2_g2b_contract import load_contract
from agicore.trading.ema_pullback_v2_g2b_storage import produce_bundle
p=json.load(sys.stdin);root=Path.cwd().resolve()
contract=load_contract(p['contract'])
produce_bundle(Path(p['bundle']),p['fixture'],expected_contract_sha256=p['contract'])
allowed={x['path'] for x in contract['source_closure']}; loaded=set()
for mod in list(sys.modules.values()):
    name=getattr(mod,'__file__',None)
    if name:
        path=Path(name).resolve()
        if path.suffix=='.py' and path.is_relative_to(root):
            loaded.add(str(path.relative_to(root)))
assert loaded <= allowed, sorted(loaded-allowed)
print(len(loaded))
"""
    result = subprocess.run(
        [sys.executable, "-B", "-c", script],
        cwd=ROOT,
        input=json.dumps(
            {"bundle": str(tmp_path / "bundle"), "contract": digest, "fixture": fixture}
        ),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert int(result.stdout.strip()) > 0


@pytest.mark.parametrize("damage", ["object", "source", "seal", "runner", "external_native"])
def test_forged_or_incomplete_bundle_is_rejected(completed_bundle, tmp_path, damage):
    original, receipt, digest = completed_bundle
    bundle = tmp_path / "bundle"
    shutil.copytree(original, bundle)
    expected_manifest = receipt["manifest_sha256"]
    expected_native = receipt["native_sha256"]
    if damage == "object":
        obj = next((bundle / "objects").rglob("*.blob"))
        raw = obj.read_bytes()
        obj.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
    elif damage == "source":
        source = bundle / "source.synthetic.txt"
        raw = source.read_bytes()
        source.write_bytes(raw[:-2] + b"1\n")
    elif damage == "seal":
        (bundle / "completion.json").unlink()
    elif damage == "runner":
        path = bundle / "manifest.json"
        manifest = json.loads(path.read_bytes())
        manifest["runner_sha256"] = "0" * 64
        raw = canonical(manifest)
        path.write_bytes(raw)
        expected_manifest = sha(raw)
    else:
        expected_native = "0" * 64
    with pytest.raises(StorageProofError):
        verify_bundle(
            bundle,
            expected_contract_sha256=digest,
            expected_manifest_sha256=expected_manifest,
            expected_native_sha256=expected_native,
        )


def test_independent_auditor_rejects_rehashed_false_metrics(completed_bundle, registered):
    bundle, receipt, digest = completed_bundle
    _, contract = registered
    native_bytes, _ = verify_bundle(
        bundle,
        expected_contract_sha256=digest,
        expected_manifest_sha256=receipt["manifest_sha256"],
        expected_native_sha256=receipt["native_sha256"],
    )
    document = parse_canonical([native_bytes], limit=33_554_432)
    document["metrics"]["entry_fills"] += 1
    document["output_sha256"] = sha(
        canonical({k: v for k, v in document.items() if k != "output_sha256"})
    )
    raw = (bundle / "source.synthetic.txt").read_bytes()
    witnesses = source_witnesses(raw, sha(raw), maximum=MAX_OBSERVATIONS)
    with pytest.raises(StorageProofError, match="independent complete metrics"):
        audit_optimized_native(
            document,
            witnesses,
            raw,
            runner_sha=contract["runner_sha256"],
            input_sha=sha(raw),
            maximum=MAX_OBSERVATIONS,
        )


def test_independent_auditor_rejects_rehashed_false_trade_pnl(registered):
    _, contract = registered
    raw = generate_fixture(contract, "impulse_profit_LONG")
    document, _ = optimized.run_synthetic_native_v1(
        raw, bindings=reference.read_frozen_replay_bindings_v2()
    )
    assert len(document["closed_trade_records"]) == 1
    document["closed_trade_records"][0]["net_realized_pnl_usd"]["numerator"] += 1
    document["output_sha256"] = sha(
        canonical({k: v for k, v in document.items() if k != "output_sha256"})
    )
    witnesses = source_witnesses(raw, sha(raw), maximum=MAX_OBSERVATIONS)
    with pytest.raises(StorageProofError):
        audit_optimized_native(
            document,
            witnesses,
            raw,
            runner_sha=RUNNER_SHA256,
            input_sha=sha(raw),
            maximum=MAX_OBSERVATIONS,
        )


def test_unknown_contract_fixture_and_changed_source_fail_closed(registered, tmp_path):
    digest, contract = registered
    with pytest.raises(StorageProofError, match="contract mismatch"):
        load_contract("0" * 64)
    with pytest.raises(StorageProofError, match="unknown fixture"):
        generate_fixture(contract, "unregistered-input")
    (tmp_path / "changed.py").write_text("changed\n")
    with pytest.raises(StorageProofError, match="source drift"):
        _source_files_match([{"path": "changed.py", "sha256": "0" * 64}], root=tmp_path)
    assert digest == sha(CONTRACT_PATH.read_bytes())


def test_storage_segments_beyond_historical_16_mib_without_changing_it(tmp_path):
    raw = (b"invented-g2b-segment-" * (MAX_NATIVE_BYTES // 21 + 2))[: MAX_NATIVE_BYTES + 1]
    assert len(raw) == MAX_NATIVE_BYTES + 1
    descriptor = encode_segments(raw, "codec_probe", tmp_path, codec_profile())
    assert len(descriptor["segments"]) == 2
    assert decode_segments(descriptor, tmp_path, codec_profile()) == raw
    forged = copy.deepcopy(descriptor)
    forged["segments"].reverse()
    with pytest.raises(StorageProofError):
        decode_segments(forged, tmp_path, codec_profile())


def test_producer_does_not_call_historical_identity_projection(registered, tmp_path, monkeypatch):
    digest, _ = registered
    monkeypatch.setattr(
        optimized, "validate_native_result_v1", lambda *_: pytest.fail("projection called")
    )
    receipt = produce_bundle(
        tmp_path / "bundle", "impulse_profit_LONG", expected_contract_sha256=digest
    )
    assert receipt["runner_sha256"] == RUNNER_SHA256


def test_real_recovery_entrypoint_remains_denied():
    with pytest.raises(
        reference.DevelopmentReplayV2Error, match="real recovery execution forbidden"
    ):
        optimized.execute_real_recovery_v1()
