"""V1 lossless, immutable storage of predeclared small synthetic native evidence.

No execution entrypoint, RAW path loader, recovery claim or real authorization.
The producer never declares COMPLETE. Only the separate verifier can seal a bundle.
"""

from __future__ import annotations

import re
import zlib
from datetime import UTC, datetime
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

from .ema_pullback_v2_storage_format import (
    ADDENDUM_SHA,
    CHUNK_SIZE,
    MAX_NATIVE_BYTES,
    MAX_OBSERVATIONS,
    REAL_RAW_SHA,
    ROOT,
    array_counts,
    canonical,
    codec_profile,
    contracts,
    immutable_write,
    parse_canonical,
    regular_read,
    require,
    sha,
)


def encode_stream(raw: bytes, stream_id: str, directory: Path, profile: dict) -> dict:
    """Shard exact bytes deterministically; codec-only fixtures use this same path."""
    require(type(raw) is bytes and 0 < len(raw) <= MAX_NATIVE_BYTES, "bounded byte stream")
    require(profile == codec_profile(), "pinned codec/runtime mismatch")
    require(re.fullmatch(r"[a-z_]+", stream_id) is not None, "stream identity")
    chunks = []
    for ordinal, offset in enumerate(range(0, len(raw), CHUNK_SIZE)):
        decoded = raw[offset : offset + CHUNK_SIZE]
        compressor = zlib.compressobj(9, zlib.DEFLATED, -15, 8, zlib.Z_DEFAULT_STRATEGY)
        stored = compressor.compress(decoded) + compressor.flush(zlib.Z_FINISH)
        codec = "RAW_DEFLATE"
        if len(stored) >= len(decoded):
            codec, stored = "IDENTITY", decoded
        digest = sha(stored)
        relative = f"objects/{digest[:2]}/{digest}.blob"
        path = directory / relative
        if path.exists():
            require(regular_read(path) == stored, "content address collision")
            require(
                all(
                    c["codec"] == codec and c["uncompressed_sha256"] == sha(decoded)
                    for c in chunks
                    if c["stored_sha256"] == digest
                ),
                "conflicting object reuse",
            )
        else:
            immutable_write(path, stored)
        chunks.append(
            {
                "stream_id": stream_id,
                "ordinal": ordinal,
                "uncompressed_offset": offset,
                "uncompressed_size_bytes": len(decoded),
                "uncompressed_sha256": sha(decoded),
                "codec": codec,
                "codec_profile_sha256": sha(canonical(profile)),
                "stored_size_bytes": len(stored),
                "stored_sha256": digest,
                "object_identity": relative,
            }
        )
    return {
        "stream_id": stream_id,
        "uncompressed_size_bytes": len(raw),
        "uncompressed_sha256": sha(raw),
        "chunk_count": len(chunks),
        "chunks": chunks,
    }


def _witnesses(raw):
    rows, offset = [], 0
    for index, line in enumerate(raw.splitlines(keepends=True)):
        require(index < MAX_OBSERVATIONS and line.endswith(b"\n"), "bounded complete invented rows")
        fields = line.rstrip(b"\r\n").decode("ascii").split(";")
        require(len(fields) == 6, "source row")
        close = Fraction(Decimal(fields[4]))
        stamp = datetime.strptime(fields[0], "%Y%m%d %H%M%S").replace(tzinfo=UTC)
        rows.append(
            {
                "bar_index": index,
                "timestamp_utc": stamp.isoformat().replace("+00:00", "Z"),
                "raw_close_text": fields[4],
                "close_exact": {"numerator": close.numerator, "denominator": close.denominator},
                "source_row_byte_offset": offset,
                "source_row_size_bytes": len(line),
                "source_row_sha256": sha(line),
            }
        )
        offset += len(line)
    return rows


def make_bindings(document, complete_source_sha: str, verifier_source_sha: str) -> dict:
    """Explicit acyclic storage bindings, not a recovery run registration."""
    addendum, _ = contracts()
    parents = addendum["parents"]
    require(
        all(
            re.fullmatch(r"[0-9a-f]{64}", value)
            for value in (complete_source_sha, verifier_source_sha)
        ),
        "source closure hashes",
    )
    result = {
        k + "_sha256": parents[k]["sha256"]
        for k in (
            "strategy_manifest",
            "development_protocol",
            "recovery_protocol",
            "architecture_addendum",
        )
    }
    result.update(
        dataset_lineage_manifest_sha256=parents["dataset_lineage"]["sha256"],
        dataset_raw_sha256=document["run_identity"]["dataset_raw_sha256"],
        storage_addendum_sha256=ADDENDUM_SHA,
        original_failed_run_id_sha256="d2eb78fb5a1b97e71fcc323b71da216449b35e4298729a26d6d052f4f26f00f4",
        run_identity=document["run_identity"],
        run_id_sha256=document["run_id_sha256"],
        complete_source_closure_sha256=complete_source_sha,
        verifier_source_closure_sha256=verifier_source_sha,
    )
    return result


def produce_synthetic_bundle(
    *,
    native_bytes: bytes,
    synthetic_raw: bytes,
    directory: Path,
    profile: dict,
    complete_source_sha: str,
    verifier_source_sha: str,
) -> dict:
    """Store validated reference bytes once, leaving completion to an independent audit."""
    require(
        type(native_bytes) is bytes and len(native_bytes) <= MAX_NATIVE_BYTES,
        "bounded native input",
    )
    require(
        type(synthetic_raw) is bytes and sha(synthetic_raw) != REAL_RAW_SHA, "invented input only"
    )
    registration = parse_canonical(
        [
            (
                ROOT / "docs/evidence/EMA_PULLBACK_V2_RECOVERY_STORAGE_FIXTURE_REGISTRATION_V1.json"
            ).read_bytes()
        ]
    )
    require(
        any(f["raw_sha256"] == sha(synthetic_raw) for f in registration["native_fixtures"]),
        "predeclared synthetic source",
    )
    _, protocol = contracts()
    document = parse_canonical([native_bytes], schema=protocol["result_schema"])
    require(
        document["immutable_lifecycle_records"]["terminal_states"][0]
        == {"kind": "INPUT_DOMAIN", "state": "SYNTHETIC_ONLY"},
        "synthetic native domain",
    )
    require(
        document["run_identity"]["dataset_raw_sha256"] == sha(synthetic_raw),
        "native/source binding",
    )
    # Validation only: no reference strategy evaluation takes place here.
    from .ema_pullback_v2_development_replay import (
        read_frozen_replay_bindings_v2,
        validate_development_result_v2,
    )

    validate_development_result_v2(document, read_frozen_replay_bindings_v2())
    require(not directory.exists() and not directory.is_symlink(), "new bundle directory required")
    for parent in directory.parents:
        require(not parent.is_symlink(), "symlink bundle parent")
    directory.mkdir(parents=True)
    witness_rows = _witnesses(synthetic_raw)
    witness_bytes = b"".join(canonical(w) for w in witness_rows)
    streams = [
        encode_stream(raw, name, directory, profile)
        for name, raw in (
            ("logical_native_result", native_bytes),
            ("mark_source_witnesses", witness_bytes),
        )
    ]
    bindings = make_bindings(document, complete_source_sha, verifier_source_sha)
    addendum, _ = contracts()
    counts = array_counts(document)
    counts["mark_source_witnesses"] = len(witness_rows)
    manifest = {
        "schema_id": addendum["layer_2_complete_audit"]["schema_id"],
        "bindings": bindings,
        "codec_profile": profile,
        "streams": streams,
        "required_record_counts": counts,
    }
    manifest_bytes = canonical(manifest)
    immutable_write(directory / "bundle-manifest.json", manifest_bytes)
    summary = {
        k: document[k] for k in addendum["layer_1_decision_summary"]["native_projection_fields"]
    }
    summary.update(
        summary_schema_id=addendum["layer_1_decision_summary"]["schema_id"],
        storage_addendum_sha256=ADDENDUM_SHA,
        complete_source_closure_sha256=complete_source_sha,
        verifier_source_closure_sha256=verifier_source_sha,
        bundle_manifest_sha256=sha(manifest_bytes),
        logical_native_file_sha256=sha(native_bytes),
        logical_native_size_bytes=len(native_bytes),
    )
    summary_bytes = canonical(summary)
    immutable_write(directory / "decision-summary.json", summary_bytes)
    receipt = {
        "schema": "agicore:synthetic-storage-production:v1",
        "status": "PRODUCED_INCOMPLETE",
        "bundle_manifest_sha256": sha(manifest_bytes),
        "summary_sha256": sha(summary_bytes),
        "bindings": bindings,
        "logical_native_file_sha256": sha(native_bytes),
        "native_output_sha256": document["output_sha256"],
        "logical_native_size_bytes": len(native_bytes),
        "required_record_counts": counts,
    }
    immutable_write(directory / "production-receipt.json", canonical(receipt))
    return receipt
