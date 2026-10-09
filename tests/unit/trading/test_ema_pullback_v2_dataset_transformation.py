"""Invented OHLCV byte strings only; never read or transform the real parent RAW."""

import hashlib
import importlib.util
import json
import sys
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "ema_pullback_v2_dataset_transformation",
    ROOT / "tools/ema_pullback_v2_dataset_transformation.py",
)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)
FIRST = datetime(2026, 6, 18, 22, 1, tzinfo=UTC)
LAST = datetime(2026, 9, 18, 13, 30, tzinfo=UTC)
WINDOW = m.TimestampWindow(FIRST, LAST)
LINES = (
    b"20260618 220000;100;101;99;100;1\r\n",
    b"20260618 220100;100.00;101.00;99.00;100.00;0\r\n",
    b"20260701 120000;1e2;101;99;100.25;98765\n",
    b"20260918 133000;200;201;199;199.25;2\r\n",
    b"20260918 133100;100;101;99;100;1",
)


def expectation(raw, *, rows=5, before=1, retained=3, after=1):
    return m.ParentExpectation(
        hashlib.sha256(raw).hexdigest(),
        len(raw),
        rows,
        FIRST - timedelta(minutes=1),
        LAST + timedelta(minutes=1),
        before,
        retained,
        after,
    )


def transform(raw, expected=None, **changes):
    arguments = {
        "expectation": expectation(raw) if expected is None else expected,
        "window": WINDOW,
        "timestamp_semantics": "NINJATRADER_END_OF_BAR",
        "timestamp_timezone": "UTC",
    }
    arguments.update(changes)
    return m.transform_bytes(raw, **arguments)


def test_inclusive_boundaries_and_one_minute_outside_removed_byte_for_byte():
    raw = b"".join(LINES)
    result = transform(raw)
    assert result.output_bytes == b"".join(LINES[1:4])
    assert result.output_sha256 == hashlib.sha256(b"".join(LINES[1:4])).hexdigest()
    assert result.changed_retained_rows == 0
    assert result.audit.parent_rows == 5
    assert (result.audit.removed_before, result.audit.retained, result.audit.removed_after) == (
        1,
        3,
        1,
    )
    assert result.audit.structural_integrity == "PASS"
    assert result.audit.gap_intervals_over_one_minute == 2
    assert raw == b"".join(LINES)


def test_original_decimal_spellings_line_endings_and_real_gaps_preserved():
    result = transform(b"".join(LINES))
    assert result.output_bytes.splitlines(keepends=True) == list(LINES[1:4])
    assert b"100.00" in result.output_bytes and b"1e2" in result.output_bytes
    assert len(result.output_bytes.splitlines()) == 3  # No synthetic gap bars.


def test_unterminated_retained_last_row_is_not_given_a_newline():
    raw = b"".join(LINES[:3]) + LINES[3].removesuffix(b"\r\n")
    expected = m.ParentExpectation(
        hashlib.sha256(raw).hexdigest(),
        len(raw),
        4,
        FIRST - timedelta(minutes=1),
        LAST,
        1,
        3,
        0,
    )
    result = transform(raw, expected)
    assert result.output_bytes == b"".join(LINES[1:3]) + LINES[3].removesuffix(b"\r\n")
    assert not result.output_bytes.endswith(b"\n")


def test_zero_and_large_volume_and_different_valid_prices_do_not_select_rows():
    raw = b"".join(LINES)
    changed = raw.replace(b"100.00;101.00;99.00;100.00;0", b"200;210;190;205;100000000")
    result = transform(changed)
    assert result.audit.retained == 3
    assert result.output_bytes == b"".join(changed.splitlines(keepends=True)[1:4])


def test_audit_does_not_construct_transformed_bytes():
    raw = b"".join(LINES)
    audit = m.audit_parent_bytes(
        raw,
        expectation=expectation(raw),
        window=WINDOW,
        timestamp_semantics="NINJATRADER_END_OF_BAR",
        timestamp_timezone="UTC",
    )
    assert audit.retained == 3
    assert not hasattr(audit, "output_bytes")


def test_two_fresh_synthetic_runs_are_identical_and_records_frozen():
    first = transform(b"".join(LINES))
    second = transform(bytes(b"".join(LINES)))
    assert first == second
    with pytest.raises(FrozenInstanceError):
        first.output_bytes = b"changed"
    with pytest.raises(FrozenInstanceError):
        first.audit.retained = 9


@pytest.mark.parametrize(
    "changed_field", ["sha256", "size_bytes", "rows", "first", "last", "counts"]
)
def test_identity_row_bounds_and_partition_mismatches_fail_closed(changed_field):
    raw = b"".join(LINES)
    expected = expectation(raw)
    changes = {
        "sha256": {"sha256": "0" * 64},
        "size_bytes": {"size_bytes": len(raw) + 1},
        "rows": {"rows": 6, "retained": 4},
        "first": {"first": expected.first - timedelta(minutes=1)},
        "last": {"last": expected.last + timedelta(minutes=1)},
        "counts": {"removed_before": 2, "retained": 2},
    }
    with pytest.raises(m.TransformationError):
        transform(raw, replace(expected, **changes[changed_field]))


@pytest.mark.parametrize(
    "semantics,zone",
    [
        ("BAR_START", "UTC"),
        (None, "UTC"),
        ("NINJATRADER_END_OF_BAR", "Europe/Paris"),
        ("NINJATRADER_END_OF_BAR", None),
    ],
)
def test_missing_or_wrong_utc_end_of_bar_evidence_rejected(semantics, zone):
    with pytest.raises(m.TransformationError, match="End-of-Bar evidence"):
        transform(b"".join(LINES), timestamp_semantics=semantics, timestamp_timezone=zone)


@pytest.mark.parametrize(
    "bad_line",
    [
        b"20260701 120000;100;101;99;100\n",
        b"20260230 120000;100;101;99;100;1\n",
        b"20260701 120001;100;101;99;100;1\n",
        b"20260701 120000;NaN;101;99;100;1\n",
        b"20260701 120000;100;Infinity;99;100;1\n",
        b"20260701 120000;100;101;99;100;NaN\n",
        b"20260701 120000;100;99;98;100;1\n",
        b"20260701 120000;100;102;101;100;1\n",
        b"20260701 120000;100;99;101;100;1\n",
        b"20260701 120000;100;101;99;100;-1\n",
        b"20260701 120000;100;101;99;100;1.5\n",
        b"20260701 120000;100;101;99;100.01;1\n",
        b"20260701 120000;100;101;99;100;1\r",
    ],
)
def test_any_malformed_or_invalid_row_aborts_entire_operation(bad_line):
    raw = b"".join((LINES[0], LINES[1], bad_line, LINES[3], LINES[4]))
    with pytest.raises(m.TransformationError):
        transform(raw)


def test_invalid_outside_window_row_must_not_be_silently_filtered():
    raw = b"".join(LINES).replace(
        b"20260618 220000;100;101;99;100;1", b"20260618 220000;NaN;101;99;100;1"
    )
    with pytest.raises(m.TransformationError):
        transform(raw)


@pytest.mark.parametrize("sequence", [(0, 1, 1, 3, 4), (0, 2, 1, 3, 4)])
def test_duplicates_and_nonchronological_rows_rejected_without_dedup_or_sort(sequence):
    with pytest.raises(m.TransformationError, match="non-chronological"):
        transform(b"".join(LINES[index] for index in sequence))


def protocol_arguments():
    protocol_bytes = (ROOT / m.PROTOCOL_PATH).read_bytes()
    return {
        "protocol_bytes": protocol_bytes,
        "claimed_sha256": hashlib.sha256(protocol_bytes).hexdigest(),
        "source_bytes": (ROOT / m.SOURCE_PATH).read_bytes(),
        "strategy_manifest_bytes": (
            ROOT / "docs/evidence/EMA_PULLBACK_V2_REGIME_GATED_BASELINE_MANIFEST.json"
        ).read_bytes(),
        "development_protocol_bytes": (
            ROOT / "docs/evidence/EMA_PULLBACK_V2_DEVELOPMENT_PROTOCOL.json"
        ).read_bytes(),
    }


def test_canonical_production_protocol_source_and_all_bindings_precommitted():
    arguments = protocol_arguments()
    verified = m.verify_transformation_protocol(**arguments)
    assert verified.protocol_bytes == m.canonical_bytes(verified.document)
    assert verified.document["parent_raw"] == m.precommitted_parent()
    assert verified.document["timestamp_predicate"] == m.precommitted_predicate()
    assert verified.document["expected_row_counts"] == m.precommitted_counts()
    assert verified.document["execution_in_this_gate"] == "FORBIDDEN"
    assert verified.document["transformed_raw_sha256"] is None
    assert verified.document["real_strategy_replay"] == "NOT_EXECUTED"
    assert (
        arguments["claimed_sha256"]
        in (
            ROOT / "docs/evidence/EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION.md"
        ).read_text()
    )
    altered = verified.document
    altered["parent_raw"]["data_rows"] = 1
    assert verified.document["parent_raw"]["data_rows"] == 101962
    with pytest.raises(FrozenInstanceError):
        verified.protocol_bytes = b"changed"


@pytest.mark.parametrize(
    "field",
    [
        "claimed_sha256",
        "source_bytes",
        "strategy_manifest_bytes",
        "development_protocol_bytes",
        "protocol_bytes",
    ],
)
def test_wrong_hash_or_document_bytes_fail_closed(field):
    arguments = protocol_arguments()
    arguments[field] = "0" * 64 if field == "claimed_sha256" else arguments[field] + b" "
    with pytest.raises(m.TransformationError):
        m.verify_transformation_protocol(**arguments)


@pytest.mark.parametrize(
    "field",
    [
        "parent_raw",
        "timestamp_predicate",
        "expected_row_counts",
        "retained_row_policy",
        "phase",
        "status",
    ],
)
def test_altered_frozen_policy_fails_even_with_its_recomputed_document_hash(field):
    arguments = protocol_arguments()
    document = json.loads(arguments["protocol_bytes"])
    document[field] = "changed"
    arguments["protocol_bytes"] = m.canonical_bytes(document)
    arguments["claimed_sha256"] = hashlib.sha256(arguments["protocol_bytes"]).hexdigest()
    with pytest.raises(m.TransformationError):
        m.verify_transformation_protocol(**arguments)


def test_mutable_protocol_bytes_not_accepted():
    arguments = protocol_arguments()
    arguments["protocol_bytes"] = bytearray(arguments["protocol_bytes"])
    with pytest.raises(m.TransformationError, match="immutable"):
        m.verify_transformation_protocol(**arguments)


def test_default_cli_verifies_only_no_raw_access(capsys):
    arguments = protocol_arguments()
    assert m.main(["--protocol-sha256", arguments["claimed_sha256"]]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["real_transformation"] == "NOT_EXECUTED"


@pytest.mark.parametrize(
    "extra",
    [
        ["--input", "/not-an-upload/parent.txt"],
        ["--execute", "--execution-gate", "WRONG_GATE"],
        ["--execute"],
    ],
)
def test_cli_rejects_unseparated_execution_before_reading_input(extra, capsys):
    assert m.main(["--protocol-sha256", "0" * 64, *extra]) == 2
    assert "FAIL_CLOSED" in capsys.readouterr().err


def test_cli_wrong_synthetic_parent_never_creates_output_or_changes_input(tmp_path, capsys):
    incoming = tmp_path / "invented-parent.txt"
    outgoing = tmp_path / "not-created.txt"
    incoming.write_bytes(b"".join(LINES))
    arguments = protocol_arguments()
    assert (
        m.main(
            [
                "--protocol-sha256",
                arguments["claimed_sha256"],
                "--execute",
                "--execution-gate",
                m.EXECUTION_GATE,
                "--input",
                str(incoming),
                "--output",
                str(outgoing),
            ]
        )
        == 2
    )
    assert not outgoing.exists()
    assert incoming.read_bytes() == b"".join(LINES)
    assert "parent SHA-256 mismatch" in capsys.readouterr().err


def test_cli_never_overwrites_existing_output(tmp_path, capsys):
    incoming = tmp_path / "invented-parent.txt"
    outgoing = tmp_path / "existing.txt"
    incoming.write_bytes(b"".join(LINES))
    outgoing.write_bytes(b"untouched")
    arguments = protocol_arguments()
    assert (
        m.main(
            [
                "--protocol-sha256",
                arguments["claimed_sha256"],
                "--execute",
                "--execution-gate",
                m.EXECUTION_GATE,
                "--input",
                str(incoming),
                "--output",
                str(outgoing),
            ]
        )
        == 2
    )
    assert outgoing.read_bytes() == b"untouched"
    assert incoming.read_bytes() == b"".join(LINES)
    assert "may not overwrite" in capsys.readouterr().err
