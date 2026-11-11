"""Bounded invented storage contract: exact bytes, independent audit and corruption."""

from __future__ import annotations

import ast
import hashlib
from fractions import Fraction

import pytest

from agicore.trading.ema_pullback_v2_storage_audit import marked_drawdown, trade_statistics
from agicore.trading.ema_pullback_v2_storage_format import (
    CHUNK_SIZE,
    ROOT,
    StorageProofError,
    canonical,
    codec_profile,
    parse_canonical,
    regular_read,
    sha,
)
from tests.unit.trading.v2_recovery_storage_fixtures import BYTE_IDS, NATIVE_IDS, TAMPER_IDS
from tools.ema_pullback_v2_storage_synthetic_proof import (
    byte_case,
    native_case,
    statistics_cases,
    tamper_case,
    verify_registration,
)

SOURCE_REGISTRATION = (
    ROOT
    / "docs/evidence/EMA_PULLBACK_V2_RECOVERY_STORAGE_CI_PORTABLE_SOURCE_REGISTRATION_V1.json"
)


@pytest.fixture(scope="module")
def registration():
    """CI verifies the source bytes but prebinds its own installed codec version."""
    source, _ = verify_registration(SOURCE_REGISTRATION, formal=False)
    return source


@pytest.fixture(scope="module")
def complete_cases(tmp_path_factory, registration):
    root = tmp_path_factory.mktemp("invented-storage")
    result = {}
    profile = codec_profile()
    for name in NATIVE_IDS:
        path = root / name
        result[name] = path, native_case(path, name, registration, profile)
    return result


@pytest.mark.parametrize("name", NATIVE_IDS)
def test_complete_native_roundtrip(complete_cases, name):
    _, receipt = complete_cases[name]
    assert receipt["status"] == "PASS"
    assert receipt["reference_native_sha256"] == receipt["reconstructed_native_sha256"]
    assert receipt["exact_bytes"] is True


@pytest.mark.parametrize("name", BYTE_IDS)
def test_boundaries_entropy_and_split_tokens(tmp_path, name):
    result = byte_case(tmp_path / name, name, codec_profile())
    assert result["status"] == "PASS"
    assert result["source_sha256"] == result["decoded_sha256"]


@pytest.mark.parametrize("name", TAMPER_IDS)
def test_every_precommitted_corruption_rejected(tmp_path, complete_cases, name):
    base = "dense_gapped_LONG" if name == "SWAPPED_TRADE_PROVENANCE" else "impulse_profit_LONG"
    result = tamper_case(tmp_path / name, name, complete_cases[base][0], codec_profile())
    assert result["outcome"] == "REJECT"


@pytest.mark.parametrize(
    "raw",
    [
        b'{"a":1,"a":2}\n',
        b'{"b":0,"a":1}\n',
        b'{"a":1}',
        b'{"a":1}\n\n',
        b'{"a":1.0}\n',
        b'{"a":NaN}\n',
        b'{"a":-0}\n',
        b'{"a":01}\n',
        b'{"a":"\\u0061"}\n',
        b'{"a":"\xff"}\n',
    ],
)
def test_strict_canonical_parser(raw):
    with pytest.raises(StorageProofError):
        parse_canonical([raw])


def test_no_float_and_exact_large_integer():
    with pytest.raises(StorageProofError):
        canonical({"bad": 1.5})
    value = {"negative": -(10**6000 + 1), "rational": {"numerator": -3, "denominator": 4}}
    raw = canonical(value)
    assert parse_canonical([raw[i : i + 1] for i in range(len(raw))]) == value


RATIONAL_SCHEMA = {
    "$defs": {
        "rational": {
            "additionalProperties": False,
            "properties": {
                "denominator": {"minimum": 1, "type": "integer"},
                "numerator": {"type": "integer"},
            },
            "required": ["numerator", "denominator"],
            "type": "object",
        }
    },
    "$ref": "#/$defs/rational",
}


@pytest.mark.parametrize(
    "value",
    [
        {"denominator": 3, "numerator": 1},
        {"denominator": 1, "numerator": 0},
        {"denominator": 4, "numerator": -3},
        {"denominator": 10**4000 + 1, "numerator": 10**5000},
    ],
)
def test_schema_context_accepts_canonical_rationals(value):
    raw = canonical(value)
    assert parse_canonical([raw], schema=RATIONAL_SCHEMA) == value


@pytest.mark.parametrize(
    "value",
    [
        {"denominator": 2, "numerator": "1"},
        {"denominator": "2", "numerator": 1},
        {"denominator": 0, "numerator": 1},
        {"denominator": True, "numerator": 1},
        {"denominator": 1, "numerator": False},
        {"denominator": 2, "numerator": 2},
    ],
)
def test_schema_context_rejects_malformed_or_noncanonical_rationals(value):
    with pytest.raises(StorageProofError):
        parse_canonical([canonical(value)], schema=RATIONAL_SCHEMA)


def test_schema_definition_and_ordinary_rational_named_objects_are_not_retyped():
    protocol = parse_canonical(
        [(ROOT / "docs/evidence/EMA_PULLBACK_V2_DEVELOPMENT_PROTOCOL.json").read_bytes()]
    )
    declaration = protocol["result_schema"]["$defs"]["rational"]["properties"]
    assert set(declaration) == {"numerator", "denominator"}
    ordinary = {"denominator": 2, "numerator": 2}
    assert parse_canonical([canonical(ordinary)]) == ordinary
    ordinary_schema = {
        "properties": {
            "denominator": {"type": "integer"},
            "numerator": {"type": "integer"},
        },
        "type": "object",
    }
    assert parse_canonical([canonical(ordinary)], schema=ordinary_schema) == ordinary


def test_nested_ordinary_object_does_not_trigger_rational_semantics():
    value = {"outer": {"denominator": 0, "numerator": "schema-like"}}
    schema = {"properties": {"outer": {"type": "object"}}, "type": "object"}
    assert parse_canonical([canonical(value)], schema=schema) == value


def test_large_integer_token_spans_storage_chunk_boundary():
    numerator = 10**200
    value = {"padding": "", "rational": {"denominator": 3, "numerator": numerator}}
    base = canonical(value)
    marker = str(numerator).encode()
    start = base.index(marker)
    value["padding"] = "x" * (CHUNK_SIZE - 50 - start)
    raw = canonical(value)
    start = raw.index(marker)
    assert start < CHUNK_SIZE < start + len(marker)
    schema = {
        "$defs": RATIONAL_SCHEMA["$defs"],
        "properties": {
            "padding": {"type": "string"},
            "rational": {"$ref": "#/$defs/rational"},
        },
        "type": "object",
    }
    assert parse_canonical([raw[:CHUNK_SIZE], raw[CHUNK_SIZE:]], schema=schema) == value


def test_reject_path_aliases(tmp_path):
    target = tmp_path / "target"
    target.write_bytes(b"x")
    link = tmp_path / "symlink"
    link.symlink_to(target)
    with pytest.raises(StorageProofError):
        regular_read(link)
    hard = tmp_path / "hardlink"
    hard.hardlink_to(target)
    with pytest.raises(StorageProofError):
        regular_read(hard)


def test_exact_statistics_and_screening():
    assert statistics_cases()["status"] == "PASS"
    assert trade_statistics(map(Fraction, [-1, -1, 0, -1]))["maximum_consecutive_losses"] == 2
    assert marked_drawdown(map(Fraction, [-1, 3, 1, -4, 2])) == Fraction(7)


def test_verifier_has_no_strategy_or_producer_imports():
    allowed_local = {"ema_pullback_v2_storage_audit", "ema_pullback_v2_storage_format"}
    for name in ("ema_pullback_v2_recovery_storage_verifier", "ema_pullback_v2_storage_audit"):
        source = ROOT / "src/agicore/trading" / (name + ".py")
        for node in ast.walk(ast.parse(source.read_bytes())):
            if isinstance(node, ast.ImportFrom) and node.level:
                assert node.module in allowed_local
            if isinstance(node, ast.Name):
                assert node.id != "execute_registered_development_replay_v2"


def test_precommitted_generator_preserved():
    path = ROOT / "tests/unit/trading/v2_recovery_storage_fixtures.py"
    assert (
        hashlib.sha256(path.read_bytes()).hexdigest()
        == "180c31c95b73274372732f23ad604ed561a1a86c6b025481f753d38e4b5ff6f9"
    )
    assert sha(canonical(codec_profile()))
