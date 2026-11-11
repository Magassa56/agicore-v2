"""Exact canonical streaming evidence; invocation-local caches and default DENY."""

from __future__ import annotations

import hashlib
import json
from collections import OrderedDict
from dataclasses import asdict
from pathlib import Path

from . import ema_pullback_v2_development_replay as reference


def _integer_text(value: int) -> str:
    if value.bit_length() < 1024:
        return str(value)
    if value < 0:
        return "-" + _integer_text(-value)
    # An integer estimate determines only a decimal split point, never a value
    # or comparison. divmod and zero-padding reconstruct the integer exactly.
    split = max(1, value.bit_length() * 3 // 20)
    high, low = divmod(value, 10 ** split)
    return _integer_text(high) + _integer_text(low).zfill(split)


class CanonicalEncoderV1:
    """Sorted compact JSON + final LF, exact integers, a bounded local text cache."""

    def __init__(self, *, cache_cap_bytes: int = 16 * 1024 * 1024):
        self.cap = cache_cap_bytes
        self.cache = OrderedDict()
        self.cache_bytes = 0

    def _integer(self, value):
        if value.bit_length() < 1024:
            return str(value).encode("ascii")
        cached = self.cache.get(value)
        if cached is not None:
            self.cache.move_to_end(value)
            return cached
        raw = _integer_text(value).encode("ascii")
        if len(raw) <= self.cap:
            while self.cache and self.cache_bytes + len(raw) > self.cap:
                _, evicted = self.cache.popitem(last=False)
                self.cache_bytes -= len(evicted)
            self.cache[value] = raw
            self.cache_bytes += len(raw)
        return raw

    def _chunks(self, value):
        if type(value) is int:
            yield self._integer(value)
        elif type(value) is dict:
            if not all(type(k) is str for k in value):
                raise reference.DevelopmentReplayV2Error("string JSON keys required")
            yield b"{"
            for i, key in enumerate(sorted(value)):
                if i:
                    yield b","
                yield json.dumps(key, ensure_ascii=False).encode("utf-8")
                yield b":"
                yield from self._chunks(value[key])
            yield b"}"
        elif type(value) in (tuple, list):
            yield b"["
            for i, item in enumerate(value):
                if i:
                    yield b","
                yield from self._chunks(item)
            yield b"]"
        elif value is None or type(value) in (bool, str):
            yield json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
        else:
            raise reference.DevelopmentReplayV2Error("unsupported canonical type; floats forbidden")

    def chunks(self, value):
        """Yield canonical native JSON without materializing a second large string."""
        yield from self._chunks(value)
        yield b"\n"

    def bytes(self, value) -> bytes:
        """Return exact canonical bytes for bounded results and differential tests."""
        return b"".join(self.chunks(value))

    def sha256(self, value) -> str:
        """Hash the same complete stream, including final LF."""
        digest = hashlib.sha256()
        for chunk in self.chunks(value):
            digest.update(chunk)
        return digest.hexdigest()


def validate_native_result_v1(document, bindings, identity):
    """Verify candidate identity/digest before the explicit frozen-validator projection.

    The old validator hard-codes the original entrypoint identity. A transparent
    two-field identity projection is necessary to reuse its otherwise unchanged
    complete schema/provenance/accounting validation. It never changes a strategy,
    result, screening or monetary field. The native candidate is checked first.
    """
    encoder = CanonicalEncoderV1()
    reference._require(document["run_identity"] == asdict(identity), "recovery identity mismatch")
    reference._require(document["run_id_sha256"] == identity.sha256, "recovery run digest mismatch")
    payload = {k: v for k, v in document.items() if k != "output_sha256"}
    reference._require(encoder.sha256(payload) == document["output_sha256"],
                       "recovery native output digest mismatch")
    schema = bindings.protocol.document["result_schema"]
    reference._schema_check(document, schema, schema)
    projected = dict(document)
    original = reference.build_replay_run_identity_v2(identity.dataset_raw_sha256)
    projected["run_identity"] = asdict(original)
    projected["run_id_sha256"] = original.sha256
    projected["output_sha256"] = encoder.sha256(
        {k: v for k, v in projected.items() if k != "output_sha256"})
    reference.validate_development_result_v2(projected, bindings)


def require_future_authorization_v1(artifact_bytes: bytes | None, *, expected_bindings: dict):
    """Default DENY; a gate string cannot replace a separately issued bound artifact.

    This verifier creates no authorization, claim, loader or execution. Required
    expected bindings must come from separately approved implementation evidence.
    """
    names = {
        "recovery_protocol_sha256", "architecture_addendum_sha256",
        "recovery_implementation_evidence_sha256", "complete_source_closure_sha256",
        "strategy_manifest_sha256", "development_protocol_sha256",
        "dataset_lineage_manifest_sha256", "dataset_raw_sha256", "registered_recovery_run_id",
        "recovery_attempt_number", "recovery_claim_path", "output_path",
    }
    if artifact_bytes is None or type(artifact_bytes) is not bytes or set(expected_bindings) != names:
        raise reference.DevelopmentReplayV2Error("separate future recovery authorization required")
    artifact = reference._decode_json(artifact_bytes)
    if artifact.get("authorization") != "GRANTED_FOR_RECOVERY_EXECUTION_ONCE" or (
        artifact.get("issued_by") != "AGIcoreManager"
        or artifact.get("issued_after_implementation_approval") is not True
        or artifact.get("bindings") != expected_bindings
        or expected_bindings["recovery_attempt_number"] != 1
        or type(expected_bindings["recovery_attempt_number"]) is not int
    ):
        raise reference.DevelopmentReplayV2Error("future recovery authorization binding mismatch")
    for name in names:
        if name.endswith("sha256") or name == "registered_recovery_run_id":
            v = expected_bindings[name]
            if not isinstance(v, str) or len(v) != 64 or any(c not in "0123456789abcdef" for c in v):
                raise reference.DevelopmentReplayV2Error("future recovery hash binding invalid")
    claim, output = (Path(expected_bindings[n]) for n in ("recovery_claim_path", "output_path"))
    if not claim.is_absolute() or not output.is_absolute() or claim == output or (
        claim.name.endswith(".original-execution-claim")
    ):
        raise reference.DevelopmentReplayV2Error("distinct absolute future claim/output paths required")
    return artifact
