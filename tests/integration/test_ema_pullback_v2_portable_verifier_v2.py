"""V9 synthetic protocol matrix; historical V7/P03 is never executed by pytest."""
from __future__ import annotations

import copy
import os
from pathlib import Path
import sys
import time
import traceback

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tests.unit import test_ema_pullback_v2_portable_verifier_v2 as t

CASES = [
    ('S01','PASS'), ('S02','PASS'), ('S03','PASS'),
    ('SN01','reconstruction.reference_equality'), ('SN02','reference.reported_hash'),
    ('SN03','reconstruction.reported_hash'), ('SN04','native.embedded_output'),
    ('SN05','native.reported_output'), ('SN06','native.output_required'),
    ('SN07','native.final_lf'), ('SN08','native.trailing_lf'), ('SN09','native.crlf'),
    ('SN10','native.duplicate_key'), ('SN11','native.integer_spelling'),
    ('SN12','native.json_syntax'), ('SN13','native.integer_only'), ('SN14','native.integer_only'),
    ('SN15','native.key_order'), ('SN16','native.canonical'), ('SN17','bindings.run'),
    ('SN18','bindings.source'), ('SN19','independent.native'), ('SN20','independent.native'),
    ('SN21','independent.output'), ('SN22','manifest.commitment'), ('SN23','independent.status'),
    ('SN24','seal.status'), ('SN25','seal.independent_digest'), ('SN26','seal.bindings'),
    ('SN27','bundle.inventory'), ('SN28','shard.stored'), ('SN29','summary.digest'),
    ('SN30','production.digest')]


def execute_synthetic_case(case_id, expected_layer, directory):
    """Preserve exact synthetic inputs/outcomes, including the first counterexample."""
    original, original_trust = t.repository_fixture()
    raw, trust = original, copy.deepcopy(original_trust)
    entry = dict(case_id=case_id, expected_layer=expected_layer,
        mode='REPOSITORY_SELF_CONTAINED_NONWORKER_TESTS', synthetic_fixture_schema=t.FIXTURE_SCHEMA,
        fixture_sha256=t.FIXTURE_SHA256, historical_p03_executed=False,
        execution_plan_sha256=os.environ.get('AGICORE_PORTABLE_PLAN_SHA256'),
        source_sha256={n:t.digest((t.BASE/n).read_bytes()) for n in [
            'tools/ema_pullback_v2_portable_verifier_v2.py',
            'tests/unit/test_ema_pullback_v2_portable_verifier_v2.py',
            'tests/integration/test_ema_pullback_v2_portable_verifier_v2.py']})
    started = time.perf_counter_ns()
    try:
        if case_id == 'S01':
            result = t.v.verify_archive(raw, trust)
            assert result['full_native_sha256'] == t.EXPECTED_NATIVE_SHA256
            assert result['full_native_sha256'] != result['embedded_output_sha256']
            assert result['exact_reference_equality'] and result['complete_seal_validation'] == 'PASS'
            entry.update(receipt=result, extensions=t.positive_extensions(original, original_trust))
            assert len(entry['extensions']) == 21
        elif case_id == 'S02':
            fixture = t.Fixture(original, original_trust)
            doc = fixture.read_json(fixture.worker+'reference-native.json')
            doc['metrics']['average_trade_usd'] = dict(numerator=10**5000, denominator=3)
            native = fixture.coherent_native(doc)
            assert b'"numerator":1'+b'0'*5000 in native
            assert t.v.canonical(doc) == t.oracle(doc) == native
            parsed = t.v.parse_json(native, 'native')
            assert parsed['metrics']['average_trade_usd'] == dict(numerator=10**5000, denominator=3)
            raw, trust = fixture.pack()
            entry.update(receipt=t.v.verify_archive(raw, trust), integer_decimal_digits=5001,
                         independent_oracle='digit-by-digit decimal emitter')
        elif case_id == 'S03':
            result = t.v.verify_archive(raw, trust)
            assert t.SYNTHETIC_PATH.read_bytes() == original
            synthetic_receipt = dict(result, status='PASS_SYNTHETIC_FIXTURE_INTEGRITY',
                runtime=t.v.runtime_identity(), fixture_schema=t.FIXTURE_SCHEMA,
                historical_evidence_verified=False, supplemental_evidence_only=True)
            with (directory/'synthetic-receipt.json').open('xb') as f:
                f.write(t.oracle(synthetic_receipt))
            entry['receipt'] = result
        else:
            raw, trust = t.mutate(case_id[1:], original, original_trust)
            entry.update(t.expect_rejection(raw, trust, expected_layer))
        entry.update(status='PASS', observed_layer=expected_layer, runtime=t.v.runtime_identity())
        assert t.SYNTHETIC_PATH.read_bytes() == original
    except BaseException as exc:
        raw = getattr(exc, 'counterexample_raw', raw)
        trust = getattr(exc, 'counterexample_trust', trust)
        entry.update(status='FAIL', exception=repr(exc), traceback=traceback.format_exc())
        raise
    finally:
        entry.update(input_sha256=t.digest(raw), trust_sha256=t.digest(t.oracle(trust)),
                     elapsed_ns=time.perf_counter_ns()-started, resources=t.v.resource_snapshot())
        for name, data in [('input.zip',raw), ('trust.json',t.oracle(trust)), ('result.json',t.oracle(entry))]:
            with (directory/name).open('xb') as f:
                f.write(data)


@pytest.mark.parametrize('case_id,expected_layer', CASES, ids=[c[0] for c in CASES])
def test_synthetic_matrix(case_id, expected_layer, tmp_path):
    """Run one declared synthetic case; pytest -x supplies the first-failure boundary."""
    parent = Path(os.environ.get('AGICORE_PORTABLE_EVIDENCE', str(tmp_path)))
    directory = t.v.create_output_directory(parent)
    execute_synthetic_case(case_id, expected_layer, directory)
