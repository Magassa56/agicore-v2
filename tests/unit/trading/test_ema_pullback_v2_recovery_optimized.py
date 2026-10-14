"""Full native differential evidence; no real market file or execution authorization."""

import hashlib
import json
import os
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path

import pytest

from agicore.trading import ema_pullback_v2_development_replay as reference
from agicore.trading import ema_pullback_v2_recovery_optimized as candidate
from agicore.trading.ema_pullback_v2_recovery_evidence import (
    CanonicalEncoderV1,
    require_future_authorization_v1,
    validate_native_result_v1,
)
from agicore.trading.regime_context_v2 import RegimeDirection
from tests.unit.trading.v2_recovery_synthetic_fixtures import (
    FAMILIES,
    SCENARIOS,
    benchmark_bars,
    dense_lifecycle_resource_bars_v2,
    lifecycle_fixture,
    resource_fixture_bars,
)


@pytest.fixture(scope="module")
def bindings():
    return reference.read_frozen_replay_bindings_v2()


def _normal(document):
    identity = reference.build_replay_run_identity_v2(document["run_identity"]["dataset_raw_sha256"])
    output = dict(document)
    output["run_identity"] = asdict(identity)
    output["run_id_sha256"] = identity.sha256
    output["output_sha256"] = CanonicalEncoderV1().sha256(
        {k: v for k, v in output.items() if k != "output_sha256"})
    return CanonicalEncoderV1().bytes(output)


def _compare(raw, bindings, label):
    results = []
    for repeat in (1, 2):
        original = reference.evaluate_synthetic_development_replay_v2(raw, bindings=bindings)
        optimized = candidate.evaluate_synthetic_recovery_v1(raw, bindings=bindings)
        original_doc, optimized_doc = original.document, optimized.document
        # Both actual original output hashes are validated BEFORE normalization.
        reference.validate_development_result_v2(original_doc, bindings)
        identity = candidate.build_recovery_identity_v1(hashlib.sha256(raw).hexdigest())
        validate_native_result_v1(optimized_doc, bindings, identity)
        left, right = _normal(original_doc), _normal(optimized_doc)
        if left != right:
            p = Path(os.environ.get("V2_RECOVERY_COUNTEREXAMPLES", "/tmp"))
            p.mkdir(parents=True, exist_ok=True)
            stem = p / ("native-counterexample-" + label)
            stem.with_suffix(".Last.txt").write_bytes(raw)
            Path(str(stem) + ".reference.json").write_bytes(original.canonical_utf8)
            Path(str(stem) + ".candidate.json").write_bytes(optimized.canonical_utf8)
            pytest.fail("BLOCKED_SEMANTIC_EQUIVALENCE: " + str(stem))
        results.append((original.canonical_utf8, optimized.canonical_utf8))
        receipt = {
            "scenario": label, "repeat": repeat, "input_sha256": hashlib.sha256(raw).hexdigest(),
            "reference_native_sha256": hashlib.sha256(original.canonical_utf8).hexdigest(),
            "candidate_native_sha256": hashlib.sha256(optimized.canonical_utf8).hexdigest(),
            "normalized_output_sha256": hashlib.sha256(left).hexdigest(),
            "exact_output_equality": True,
        }
        target = os.environ.get("V2_RECOVERY_DIFFERENTIAL_RECEIPTS")
        if target:
            with Path(target).open("ab") as stream:
                stream.write((json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n").encode())
    assert results[0] == results[1]


@pytest.mark.parametrize("name", SCENARIOS)
@pytest.mark.parametrize("direction", tuple(RegimeDirection))
def test_complete_native_output_exact_twice(name, direction, bindings):
    _compare(lifecycle_fixture(name, direction), bindings, name + direction)


@pytest.mark.parametrize("family", FAMILIES)
def test_medium_predeclared_family_native_output_exact_twice(family, bindings):
    bars = benchmark_bars(family, 1000)
    raw = ("\n".join(";".join((
        b.timestamp_utc.strftime("%Y%m%d %H%M%S"),
        *(str(getattr(b, f)) for f in ("open", "high", "low", "close")), str(b.volume)
    )) for b in bars) + "\n").encode("ascii")
    _compare(raw, bindings, family + "1000")


def test_canonical_encoder_exact_with_huge_integers_and_no_global_digit_mutation():
    import sys
    limit = sys.get_int_max_str_digits()
    value = reference._native({"é": Fraction(10 ** 6000 + 51, 3), "n": -(10 ** 12001),
                               "mixed": [False, None, "a\n", {"z": 2, "a": 1}]})
    encoder = CanonicalEncoderV1(cache_cap_bytes=1024)
    actual = encoder.bytes(value)
    assert actual == reference.canonical_replay_bytes_v2(value)
    assert encoder.sha256(value) == hashlib.sha256(actual).hexdigest()
    assert encoder.cache_bytes <= 1024
    assert sys.get_int_max_str_digits() == limit
    with pytest.raises(reference.DevelopmentReplayV2Error, match="floats forbidden"):
        encoder.bytes({"float": 1.0})


def test_real_entrypoint_and_gate_string_cannot_authorize_any_access(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("path access before authorization")
    monkeypatch.setattr(Path, "read_bytes", forbidden)
    with pytest.raises(reference.DevelopmentReplayV2Error, match="real recovery execution forbidden"):
        candidate.execute_real_recovery_v1(execution_gate=reference.EXECUTION_GATE)
    with pytest.raises(reference.DevelopmentReplayV2Error, match="separate future"):
        require_future_authorization_v1(None, expected_bindings={})


def test_open_end_has_marks_without_liquidation(bindings):
    raw = lifecycle_fixture("open_eof", RegimeDirection.LONG)
    document, _ = candidate.run_synthetic_native_v1(raw, bindings=bindings)
    assert document["open_trade_records"][0]["net_realized_pnl_usd"] is None
    assert document["open_trade_records"][0]["state"] == "OPEN_UNREALIZED"
    assert len(document["marked_equity_samples"]) == len(raw.splitlines())
    assert document["dataset_first_timestamp_utc"] == reference._native(
        reference.parse_ninjatrader_last_rows_v2(raw)[0].timestamp_utc)


def test_explicit_invented_saturday_rows_are_not_filtered(bindings):
    bars = tuple(resource_fixture_bars(FAMILIES[3], 57))
    assert bars[0].timestamp_utc.weekday() == 5
    raw = ("\n".join(";".join((
        b.timestamp_utc.strftime("%Y%m%d %H%M%S"),
        *(str(getattr(b, f)) for f in ("open", "high", "low", "close")), str(b.volume)
    )) for b in bars) + "\n").encode("ascii")
    _compare(raw, bindings, "INVENTED_SATURDAY_57")
    document, _ = candidate.run_synthetic_native_v1(raw, bindings=bindings)
    assert len(document["marked_equity_samples"]) == 57


@pytest.mark.parametrize("field", (
    "recovery_protocol_sha256", "architecture_addendum_sha256",
    "recovery_implementation_evidence_sha256", "complete_source_closure_sha256",
    "strategy_manifest_sha256", "development_protocol_sha256",
    "dataset_lineage_manifest_sha256", "dataset_raw_sha256", "registered_recovery_run_id",
    "recovery_attempt_number", "recovery_claim_path", "output_path",
))
def test_missing_future_authorization_binding_is_denied_without_any_claim(field):
    expected = {key: "a" * 64 for key in (
        "recovery_protocol_sha256", "architecture_addendum_sha256",
        "recovery_implementation_evidence_sha256", "complete_source_closure_sha256",
        "strategy_manifest_sha256", "development_protocol_sha256",
        "dataset_lineage_manifest_sha256", "dataset_raw_sha256", "registered_recovery_run_id",
    )}
    expected.update(recovery_attempt_number=1, recovery_claim_path="/tmp/invented-recovery-only",
                    output_path="/tmp/invented-output-only")
    del expected[field]
    with pytest.raises(reference.DevelopmentReplayV2Error, match="separate future"):
        require_future_authorization_v1(b"{}", expected_bindings=expected)


@pytest.mark.parametrize("count", (57, 114, 1000))
def test_predeclared_dense_v2_native_output_and_actual_lifecycle_coverage(count, bindings):
    raw = ("\n".join(";".join((
        b.timestamp_utc.strftime("%Y%m%d %H%M%S"),
        *(str(getattr(b, f)) for f in ("open", "high", "low", "close")), str(b.volume)
    )) for b in dense_lifecycle_resource_bars_v2(count)) + "\n").encode("ascii")
    _compare(raw, bindings, "DENSE_V2_" + str(count))
    if count == 1000:
        document, _ = candidate.run_synthetic_native_v1(raw, bindings=bindings)
        metrics = document["metrics"]
        assert metrics["long_entry_fills"] > 1 and metrics["short_entry_fills"] > 1
        assert metrics["structural_stop_exits"] > 0 and metrics["ema20_exits"] > 0
        assert metrics["quantity_1_count"] > 0 and metrics["quantity_2_count"] > 0
        assert metrics["risk_rejections"] > 0
