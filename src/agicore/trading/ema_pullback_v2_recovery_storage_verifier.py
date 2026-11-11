"""Separate bounded decoder, native auditor and immutable completion seal.

No import of the producer, runner or strategy components. A caller must supply
independently retained manifest/source commitments and the invented source bytes.
Neither a summary nor a self-asserted COMPLETE journal is an authority.
"""

from __future__ import annotations

import hashlib
import os
import re
import zlib
from pathlib import Path

from .ema_pullback_v2_storage_audit import audit_native
from .ema_pullback_v2_storage_format import (
    ADDENDUM_SHA,
    CHUNK_SIZE,
    MAX_NATIVE_BYTES,
    StorageProofError,
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


def decode_stream(stream, directory: Path, profile: dict):
    """Yield all exact bytes under per-object expansion and complete-stream limits."""
    require(profile == codec_profile(), "codec version/options/binary binding")
    require(
        set(stream)
        == {"stream_id", "uncompressed_size_bytes", "uncompressed_sha256", "chunk_count", "chunks"},
        "stream descriptor shape",
    )
    total = stream["uncompressed_size_bytes"]
    require(type(total) is int and 0 < total <= MAX_NATIVE_BYTES, "bounded stream size")
    require(
        type(stream["chunks"]) is list
        and type(stream["chunk_count"]) is int
        and stream["chunk_count"]
        == len(stream["chunks"])
        == (total + CHUNK_SIZE - 1) // CHUNK_SIZE,
        "stream chunk count",
    )
    fields = {
        "stream_id",
        "ordinal",
        "uncompressed_offset",
        "uncompressed_size_bytes",
        "uncompressed_sha256",
        "codec",
        "codec_profile_sha256",
        "stored_size_bytes",
        "stored_sha256",
        "object_identity",
    }
    digest = hashlib.sha256()
    seen = {}
    for ordinal, descriptor in enumerate(stream["chunks"]):
        require(set(descriptor) == fields, "chunk descriptor shape")
        require(
            type(descriptor["ordinal"]) is int
            and descriptor["ordinal"] == ordinal
            and type(descriptor["uncompressed_offset"]) is int
            and descriptor["uncompressed_offset"] == ordinal * CHUNK_SIZE,
            "chunk ordinal/offset",
        )
        size = min(CHUNK_SIZE, total - ordinal * CHUNK_SIZE)
        require(
            type(descriptor["uncompressed_size_bytes"]) is int
            and descriptor["uncompressed_size_bytes"] == size,
            "decoded size/partition",
        )
        require(
            descriptor["stream_id"] == stream["stream_id"]
            and descriptor["codec_profile_sha256"] == sha(canonical(profile)),
            "chunk codec/stream binding",
        )
        stored_hash = descriptor["stored_sha256"]
        require(
            type(stored_hash) is str and re.fullmatch(r"[0-9a-f]{64}", stored_hash) is not None,
            "stored SHA spelling",
        )
        relative = f"objects/{stored_hash[:2]}/{stored_hash}.blob"
        require(descriptor["object_identity"] == relative, "content-addressed object identity")
        identity = (descriptor["codec"], descriptor["uncompressed_sha256"], size)
        require(
            stored_hash not in seen or seen[stored_hash] == identity, "conflicting object alias"
        )
        seen[stored_hash] = identity
        stored = regular_read(directory / relative, CHUNK_SIZE)
        require(
            type(descriptor["stored_size_bytes"]) is int
            and len(stored) == descriptor["stored_size_bytes"]
            and sha(stored) == stored_hash,
            "stored object digest/size",
        )
        codec = descriptor["codec"]
        if codec == "RAW_DEFLATE":
            require(len(stored) < size, "noncanonical compressed fallback")
            decoder = zlib.decompressobj(-15)
            try:
                decoded = decoder.decompress(stored, size + 1)
            except zlib.error as exc:
                raise StorageProofError("invalid compressed object: FAIL_CLOSED") from exc
            require(
                len(decoded) <= size
                and decoder.eof
                and not decoder.unconsumed_tail
                and not decoder.unused_data,
                "truncation/expansion/trailing compressed data",
            )
        else:
            require(codec == "IDENTITY", "unknown chunk codec")
            decoded = stored
        require(
            len(decoded) == size and sha(decoded) == descriptor["uncompressed_sha256"],
            "decoded digest/size",
        )
        digest.update(decoded)
        yield decoded
    require(digest.hexdigest() == stream["uncompressed_sha256"], "full stream hash")


def _inventory(directory, manifest, completed):
    expected = {"bundle-manifest.json", "decision-summary.json", "production-receipt.json"}
    if completed:
        expected.update(("independent-verification.json", "completion-seal.json"))
    aliases = {}
    for stream in manifest["streams"]:
        for c in stream["chunks"]:
            expected.add(c["object_identity"])
            identity = (c["codec"], c["uncompressed_sha256"], c["uncompressed_size_bytes"])
            require(
                c["stored_sha256"] not in aliases or aliases[c["stored_sha256"]] == identity,
                "cross-stream conflicting alias",
            )
            aliases[c["stored_sha256"]] = identity
    actual = set()
    for root, dirs, files in os.walk(directory, followlinks=False):
        for name in (*dirs, *files):
            require(not (Path(root) / name).is_symlink(), "bundle symlink")
        actual.update(str((Path(root) / name).relative_to(directory)) for name in files)
    require(actual == expected, "missing or undeclared bundle artifacts")


def _verify(
    directory,
    *,
    expected_manifest_sha,
    expected_bindings,
    expected_profile,
    expected_native_sha,
    synthetic_raw,
    completed,
):
    manifest_bytes = regular_read(directory / "bundle-manifest.json")
    require(sha(manifest_bytes) == expected_manifest_sha, "independently committed manifest SHA")
    manifest = parse_canonical([manifest_bytes])
    addendum, protocol = contracts()
    require(
        set(manifest) == set(addendum["physical_storage_contract"]["manifest_fields"]),
        "manifest fields",
    )
    require(
        manifest["schema_id"] == addendum["layer_2_complete_audit"]["schema_id"], "manifest schema"
    )
    require(
        manifest["bindings"] == expected_bindings
        and set(expected_bindings) == set(addendum["physical_storage_contract"]["bindings"]),
        "external source/run bindings",
    )
    require(
        manifest["codec_profile"] == expected_profile == codec_profile(),
        "precommitted codec profile",
    )
    require(
        [s["stream_id"] for s in manifest["streams"]]
        == ["logical_native_result", "mark_source_witnesses"],
        "required streams/order",
    )
    _inventory(directory, manifest, completed)
    native_chunks = tuple(decode_stream(manifest["streams"][0], directory, expected_profile))
    native_bytes = b"".join(native_chunks)
    require(sha(native_bytes) == expected_native_sha, "external native byte commitment")
    document = parse_canonical(native_chunks, schema=protocol["result_schema"])
    witness_bytes = b"".join(decode_stream(manifest["streams"][1], directory, expected_profile))
    witnesses = [parse_canonical([line]) for line in witness_bytes.splitlines(keepends=True)]
    require(
        expected_bindings["run_identity"] == document["run_identity"]
        and expected_bindings["run_id_sha256"] == document["run_id_sha256"]
        and expected_bindings["dataset_raw_sha256"] == sha(synthetic_raw),
        "native/bundle/source identity",
    )
    for key, parent in (
        ("strategy_manifest_sha256", "strategy_manifest"),
        ("development_protocol_sha256", "development_protocol"),
        ("dataset_lineage_manifest_sha256", "dataset_lineage"),
        ("recovery_protocol_sha256", "recovery_protocol"),
        ("architecture_addendum_sha256", "architecture_addendum"),
    ):
        require(
            expected_bindings[key] == addendum["parents"][parent]["sha256"], "frozen parent binding"
        )
    require(expected_bindings["storage_addendum_sha256"] == ADDENDUM_SHA, "storage authority")
    counts = array_counts(document)
    counts["mark_source_witnesses"] = len(witnesses)
    require(counts == manifest["required_record_counts"], "all array counts")
    audit = audit_native(document, witnesses, synthetic_raw)
    summary_bytes = regular_read(directory / "decision-summary.json")
    summary = parse_canonical([summary_bytes])
    expected_summary = {
        k: document[k] for k in addendum["layer_1_decision_summary"]["native_projection_fields"]
    }
    expected_summary.update(
        summary_schema_id=addendum["layer_1_decision_summary"]["schema_id"],
        storage_addendum_sha256=ADDENDUM_SHA,
        complete_source_closure_sha256=expected_bindings["complete_source_closure_sha256"],
        verifier_source_closure_sha256=expected_bindings["verifier_source_closure_sha256"],
        bundle_manifest_sha256=expected_manifest_sha,
        logical_native_file_sha256=sha(native_bytes),
        logical_native_size_bytes=len(native_bytes),
    )
    require(summary == expected_summary, "exact audited summary projection")
    production_bytes = regular_read(directory / "production-receipt.json")
    production = parse_canonical([production_bytes])
    expected_production = {
        "schema": "agicore:synthetic-storage-production:v1",
        "status": "PRODUCED_INCOMPLETE",
        "bundle_manifest_sha256": expected_manifest_sha,
        "summary_sha256": sha(summary_bytes),
        "bindings": expected_bindings,
        "logical_native_file_sha256": sha(native_bytes),
        "native_output_sha256": document["output_sha256"],
        "logical_native_size_bytes": len(native_bytes),
        "required_record_counts": counts,
    }
    require(production == expected_production, "complete production journal bindings")
    verification = {
        "schema": "agicore:independent-synthetic-storage-verification:v1",
        "status": "PASS",
        "bindings": expected_bindings,
        "audit": audit,
        "bundle_manifest_sha256": expected_manifest_sha,
        "summary_sha256": sha(summary_bytes),
        "production_receipt_sha256": sha(production_bytes),
        "logical_native_file_sha256": sha(native_bytes),
        "native_output_sha256": document["output_sha256"],
        "logical_native_size_bytes": len(native_bytes),
        "required_record_counts": counts,
    }
    seal = {
        **verification,
        "schema": "agicore:synthetic-storage-completion-seal:v1",
        "status": "COMPLETE",
        "independent_verification_sha256": sha(canonical(verification)),
    }
    if completed:
        require(
            regular_read(directory / "independent-verification.json") == canonical(verification),
            "verification receipt",
        )
        require(
            regular_read(directory / "completion-seal.json") == canonical(seal), "completion seal"
        )
    return native_bytes, verification, seal


def verify_synthetic_bundle(
    directory: Path,
    *,
    expected_manifest_sha: str,
    expected_bindings: dict,
    expected_profile: dict,
    expected_native_sha: str,
    synthetic_raw: bytes,
    seal: bool = False,
) -> tuple[bytes, dict]:
    """Read-only by default; optional first sealing follows a successful full audit.

    This operation cannot create a recovery claim or authorize strategy execution.
    An existing completed bundle is independently re-read, never rewritten.
    """
    try:
        native_bytes, verification, completion = _verify(
            directory,
            expected_manifest_sha=expected_manifest_sha,
            expected_bindings=expected_bindings,
            expected_profile=expected_profile,
            expected_native_sha=expected_native_sha,
            synthetic_raw=synthetic_raw,
            completed=not seal,
        )
        if seal:
            immutable_write(directory / "independent-verification.json", canonical(verification))
            immutable_write(directory / "completion-seal.json", canonical(completion))
        return native_bytes, verification
    except StorageProofError:
        raise
    except (OSError, KeyError, IndexError, ValueError, TypeError, ArithmeticError) as exc:
        raise StorageProofError("invalid/incomplete bundle: FAIL_CLOSED") from exc
