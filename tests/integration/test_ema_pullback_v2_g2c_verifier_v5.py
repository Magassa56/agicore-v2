"""Differential CPU recovery tests. No tier replay; only invented, miniature test envelopes."""

import json
import os
import shutil
import subprocess
import sys
from decimal import localcontext
from types import SimpleNamespace

import pytest

from agicore.trading import ema_pullback_v2_g2c_scaling as v4
from agicore.trading import ema_pullback_v2_g2c_verifier_v5 as v5
from agicore.trading.ema_pullback_v2_g2b_contract import generate_fixture
from agicore.trading.ema_pullback_v2_storage_format import (
    StorageProofError,
    canonical,
    codec_profile,
    contracts,
    parse_canonical,
    sha,
)

REGISTRATION = "95e836f3897a973d08e8a38e3845bc4e15d53e67996f03f718dc6f9f05445a35"


def test_external_verifier_binding_and_historical_contract(tmp_path, monkeypatch):
    contract = v5.load_registration(REGISTRATION)
    assert contract == v4.load_contract(v5.V4_SHA)
    with pytest.raises(StorageProofError):
        v5.load_registration(v5.V4_SHA)
    raw = json.loads(v5.REGISTRATION.read_bytes())
    raw["verifier"]["sha256"] = "0" * 64
    path = tmp_path / "forged"
    path.write_bytes(canonical(raw))
    monkeypatch.setattr(v5, "REGISTRATION", path)
    with pytest.raises(StorageProofError, match="source binding"):
        v5.load_registration(sha(path.read_bytes()))


@pytest.mark.parametrize(
    "raw",
    [
        b"",
        b"1",
        b"0\n\n",
        b" true\n",
        b"+1\n",
        b"-0\n",
        b"01\n",
        b"-01\n",
        b"-\n",
        b"1e3\n",
        b"1.0\n",
        b"NaN\n",
        b"{}\r\n",
        b"\xef\xbb\xbf0\n",
        b'"\xff"\n',
        b'{"z":0,"a":1}\n',
        b'{"a":0,"a":1}\n',
        b'"\\u0061"\n',
        b'"\\/"\n',
        b'"\\ud800"\n',
        b'"a\x01b"\n',
        b'{"a": [1]}\n',
        b'["unfinished]\n',
        b"[" * 128 + b"1" + b"]" * 128 + b"\n",
    ],
)
def test_v4_and_v5_reject_the_same_noncanonical_bytes(raw):
    for parse in (
        lambda raw: parse_canonical([raw]),
        lambda raw: v5.parse_native(raw, limit=len(raw)),
    ):
        with pytest.raises(StorageProofError):
            parse(raw)


def test_exact_tokens_large_fractions_digit_limit_context_and_nesting():
    limit = sys.get_int_max_str_digits()
    schema = contracts()[1]["result_schema"]
    rational = {"$defs": schema["$defs"], "$ref": "#/$defs/rational"}
    big = b"9" * 5001
    valid = b'{"denominator":2,"numerator":-' + big + b"}\n"
    with localcontext() as ctx:
        ctx.prec = 2
        old = parse_canonical([valid], schema=rational)
        new = v5.parse_native(valid, limit=len(valid), schema=rational)
        assert new == old and canonical(new) == valid
    assert sys.get_int_max_str_digits() == limit
    for value in ({"z": 'é\\\n"😀', "a": [True, None, 0, (10**18), -1]}, [], [10**501 + 1] * 130):
        raw = canonical(value)
        assert v5.parse_native(raw, limit=len(raw)) == parse_canonical([raw])
    raw = b"[" * 127 + b"1" + b"]" * 127 + b"\n"
    assert v5.parse_native(raw, limit=len(raw)) == parse_canonical([raw])
    with pytest.raises(StorageProofError):
        v5.parse_native(valid, limit=len(valid) - 1)
    for bad in (b'{"denominator":2,"numerator":2}\n', b'{"denominator":0,"numerator":1}\n'):
        for parse in (
            lambda: parse_canonical([bad], schema=rational),
            lambda: v5.parse_native(bad, limit=len(bad), schema=rational),
        ):
            with pytest.raises(StorageProofError):
                parse()


@pytest.fixture()
def miniature(tmp_path, monkeypatch):
    parent = v4.load_g2b_contract(v4.PARENT_SHA256)
    raw = generate_fixture(parent, "impulse_profit_LONG")
    count, name = len(raw.splitlines()), "TEST_ONLY_INVENTED"
    assert count <= 201
    # Private test envelope: neither receipt nor identity is released as V4 or V5 proof.
    producer, verifier = sha(b"test-only producer"), sha(b"test-only verifier")
    contract = {
        "source_closure_sha256": sha(b"test-only closure"),
        "fixtures": {name: {"input_sha256": sha(raw), "observations": count}},
        "tiers": {str(count): {"logical_bytes": 2**24}},
    }
    monkeypatch.setattr(v4, "load_contract", lambda _: contract)
    monkeypatch.setattr(v4, "invented_fixture", lambda *_: raw)
    monkeypatch.setattr(v5, "V4_SHA", producer)
    monkeypatch.setattr(v5, "load_registration", lambda _: contract)
    bundle = tmp_path / "original"
    receipt = v4.produce_bundle(bundle, name, expected_contract_sha256=producer)
    args = {
        "expected_manifest_sha256": receipt["manifest_sha256"],
        "expected_native_sha256": receipt["native_sha256"],
    }
    return bundle, args, producer, verifier


def test_native_result_counts_audit_and_historical_seals(miniature, tmp_path):
    original, args, producer, verifier = miniature
    new = tmp_path / "new"
    shutil.copytree(original, new)
    old = v4.verify_bundle(original, **args, expected_contract_sha256=producer, seal=True)
    result = v5.verify_bundle(new, **args, expected_verifier_sha256=verifier, seal=True)
    assert result["schema"] == "agicore:g2c-verification:v5"
    assert result["verifier_contract_sha256"] == verifier and result["closed_positions"] == 1
    assert {k: v for k, v in result.items() if k not in {"schema", "verifier_contract_sha256"}} == {
        k: v for k, v in old.items() if k != "schema"
    }
    assert result == v5.verify_bundle(new, **args, expected_verifier_sha256=verifier)
    assert (original / "production.json").read_bytes() == (new / "production.json").read_bytes()
    seals = [(original / p).read_bytes() for p in ("verification.json", "completion.json")]
    for seal in (False, True):
        with pytest.raises(StorageProofError):
            v5.verify_bundle(original, **args, expected_verifier_sha256=verifier, seal=seal)
    assert seals == [(original / p).read_bytes() for p in ("verification.json", "completion.json")]
    with pytest.raises(StorageProofError):
        v4.verify_bundle(new, **args, expected_contract_sha256=producer)
    (new / "completion.json").unlink()
    with pytest.raises(StorageProofError):
        v5.verify_bundle(new, **args, expected_verifier_sha256=verifier)


@pytest.mark.parametrize("damage", ["accounting", "witness", "object", "manifest", "fixture"])
def test_rejects_tampering_even_after_rehash(miniature, damage):
    p, args, _, verifier = miniature
    if damage in ("accounting", "witness"):
        manifest = json.loads((p / "manifest.json").read_bytes())
        receipt = json.loads((p / "production.json").read_bytes())
        profile = codec_profile()
        native, rows = (v4.decode_pages(s, p, profile) for s in manifest["streams"])
        if damage == "accounting":
            doc = parse_canonical([native])
            doc["metrics"]["long_entry_fills"] += 1
            doc["output_sha256"] = sha(
                canonical({k: v for k, v in doc.items() if k != "output_sha256"})
            )
            native = canonical(doc)
            manifest["native_output_sha256"] = doc["output_sha256"]
            manifest["native_sha256"] = receipt["native_sha256"] = args[
                "expected_native_sha256"
            ] = sha(native)
        else:
            witnesses = [json.loads(line) for line in rows.splitlines()]
            witnesses[0]["source_row_byte_offset"] += 1
            rows = b"".join(canonical(w) for w in witnesses)
        shutil.rmtree(p / "objects")  # private, ephemeral test objects only
        manifest["streams"] = [
            v4.encode_pages(raw, k, p, profile)
            for raw, k in ((native, "native_result"), (rows, "source_witnesses"))
        ]
        (p / "manifest.json").write_bytes(canonical(manifest))
        receipt["manifest_sha256"] = args["expected_manifest_sha256"] = sha(canonical(manifest))
        (p / "production.json").write_bytes(canonical(receipt))
    elif damage == "object":
        next((p / "objects").rglob("*.blob")).unlink()
    elif damage == "manifest":
        args["expected_manifest_sha256"] = "0" * 64
    else:
        args["expected_fixture"] = "wrong"
    with pytest.raises(
        StorageProofError,
        match={
            "accounting": "independent complete metrics",
            "witness": "source Close witnesses",
        }.get(damage, "FAIL_CLOSED"),
    ):
        v5.verify_bundle(p, **args, expected_verifier_sha256=verifier, seal=True)
    assert not (p / "verification.json").exists() and not (p / "completion.json").exists()


@pytest.mark.skipif(os.name != "posix", reason="Linux verifier process limits")
def test_worker_denies_an_unsupervised_process(monkeypatch):
    monkeypatch.setattr(os, "getsid", lambda _: os.getpid() + 1)
    contract = v5.load_registration(REGISTRATION)
    with pytest.raises(StorageProofError, match="process group"):
        v5._worker_limits(SimpleNamespace(fixture="dense-5000"), contract)


def test_verified_sources_in_fresh_process_without_strategy_or_producer():
    code = """
import sys
from types import ModuleType
from pathlib import Path
from agicore.trading import ema_pullback_v2_g2c_verifier_v5 as v
from agicore.trading.ema_pullback_v2_storage_format import StorageProofError
contract = v.load_registration(sys.argv[1])
v._loaded_sources(contract)
for name in ('ema_pullback_v2_g2b_storage','ema_pullback_v2_recovery_optimized',
             'ema_pullback_regime_gated_baseline_v2','ema_pullback_v2_development_replay'):
    assert 'agicore.trading.' + name not in sys.modules
module = ModuleType('unregistered_test_source')
module.__file__ = str(v.ROOT / 'unregistered_test_source.py')
sys.modules[module.__name__] = module
try:
    v._loaded_sources(contract)
except StorageProofError:
    pass
else:
    raise AssertionError('unregistered verifier code accepted')
"""
    subprocess.run(
        [sys.executable, "-B", "-c", code, REGISTRATION], cwd=v5.ROOT, timeout=20, check=True
    )


@pytest.mark.parametrize("forbidden", [1000, 5000, 89841])
def test_microprofile_refuses_tier_sizes_without_reading_or_writing(tmp_path, forbidden):
    probe = v5.ROOT / "tools/ema_pullback_v2_g2c_verifier_microprofile.py"
    result = subprocess.run(
        [sys.executable, "-B", str(probe), str(tmp_path), str(forbidden), "prepare", REGISTRATION],
        capture_output=True,
        timeout=20,
    )
    assert result.returncode == 2 and b"invalid choice" in result.stderr
    assert list(tmp_path.iterdir()) == []
