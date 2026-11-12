"""Independent verifier of unmodified V4 production with a distinct V5 seal.

Only the already reconstructed, byte-bounded native JSON stream uses the new
decoder. All witness, codec, lifecycle, accounting and provenance checks are V4.
There is no replay entry point in this module.
"""

from __future__ import annotations

import hashlib
import json
import sys
import re
from decimal import Decimal
from functools import lru_cache
from pathlib import Path

from . import ema_pullback_v2_g2c_scaling as v4
from .ema_pullback_v2_g2b_audit import audit_optimized_native
from .ema_pullback_v2_g2b_verifier import _inventory
from .ema_pullback_v2_storage_format import (
    ROOT,
    StorageProofError,
    _Parser,
    _validate_rational_contracts,
    canonical,
    canonical_parts,
    codec_profile,
    contracts,
    immutable_write,
    parse_canonical,
    regular_read,
    require,
    sha,
)

V4_SHA = "e36c6a8985c383c9794cf3188e49940ddf28d7074d070f042661f6534629961f"
PREDECESSOR = "95e836f3897a973d08e8a38e3845bc4e15d53e67996f03f718dc6f9f05445a35"
REGISTRATION = ROOT / "docs/evidence/EMA_PULLBACK_V2_G2C_VERIFIER_V5_1.json"
WORKER = "tools/ema_pullback_v2_g2c_verifier_worker_v5.py"
MODULE = "src/agicore/trading/ema_pullback_v2_g2c_verifier_v5.py"
INTEGER = re.compile(r"-?(?:0|[1-9][0-9]*)")


class _ContiguousParser(_Parser):
    """Keep V4 delimiters, nesting and sorted unique keys; scan whole tokens in C."""

    def __init__(self, raw, limit):
        super().__init__([raw], limit)
        # Per document; at most 128 bounded spellings and their exact integers.
        self.cached_int = lru_cache(maxsize=128)(self._integer)

    @staticmethod
    def _integer(token):
        # Decimal(string) and int(integral Decimal) are exact irrespective of
        # context precision. Do not relax the interpreter-wide integer limit.
        return int(token) if len(token) <= 18 else int(Decimal(token))

    def string(self):
        self.expect('"')
        start = self.cursor - 1
        value, self.cursor = json.decoder.scanstring(self.buffer, self.cursor, True)
        require(
            json.encoder.encode_basestring(value) == self.buffer[start : self.cursor],
            "noncanonical string spelling",
        )
        return value

    def value(self, depth=0):
        char = self.peek()
        if not char or char not in "-0123456789":
            return super().value(depth)
        require(depth < 128, "JSON nesting limit")
        match = INTEGER.match(self.buffer, self.cursor)
        require(match is not None, "integer spelling")
        self.cursor = match.end()
        token = match[0]
        require(token != "-0", "negative zero")
        if 18 < len(token) <= 16384:
            return self.cached_int(token)
        return self._integer(token)


def parse_native(raw: bytes, *, limit: int, schema: dict | None = None):
    """Parse a single reconstructed byte stream with V4's canonical round-trip and schema."""
    try:
        require(type(raw) is bytes and len(raw) <= limit, "bounded native byte stream")
        parser = _ContiguousParser(raw, limit)
        value = parser.value()
        parser.expect("\n")
        require(not parser.peek(), "trailing JSON bytes")
        if schema is not None:
            _validate_rational_contracts(value, schema, schema)
        digest = hashlib.sha256()
        for chunk in canonical_parts(value):
            digest.update(chunk)
        digest.update(b"\n")
        require(digest.digest() == parser.digest.digest(), "noncanonical JSON")
        return value
    except StorageProofError:
        raise
    except (UnicodeError, ValueError, TypeError, RecursionError, ArithmeticError) as exc:
        raise StorageProofError("invalid exact JSON: FAIL_CLOSED") from exc


def load_registration(expected_sha256: str) -> dict:
    """Authenticate the additive verifier and the complete original V4 source closure."""
    raw = regular_read(REGISTRATION, limit=4096)
    require(sha(raw) == expected_sha256, "external V5 verifier identity")
    require(
        sha(regular_read(REGISTRATION.with_name("EMA_PULLBACK_V2_G2C_VERIFIER_V5.json"), 4096))
        == PREDECESSOR,
        "V5 predecessor identity",
    )
    contract = v4.load_contract(V4_SHA)
    require(
        parse_canonical([raw])
        == {
            "schema": "agicore:g2c-independent-verifier-registration:v5.1",
            "predecessor_sha256": PREDECESSOR,
            "worker": {"path": WORKER, "sha256": sha(regular_read(ROOT / WORKER))},
            "producer_contract_sha256": V4_SHA,
            "producer_source_closure_sha256": contract["source_closure_sha256"],
            "verifier": {"path": MODULE, "sha256": sha(regular_read(ROOT / MODULE))},
            "scope": "VERIFY_INVENTED_V4_PRODUCTION_ONLY",
        },
        "V5 source binding",
    )
    return contract


def verify_bundle(
    directory: Path,
    *,
    expected_verifier_sha256: str,
    expected_manifest_sha256: str,
    expected_native_sha256: str,
    seal: bool = False,
    expected_fixture: str | None = None,
) -> dict:
    """Verify V4 production and emit or recheck only V5 receipts; never rewrite a V4 seal."""
    try:
        contract = load_registration(expected_verifier_sha256)
        directory = directory.absolute()
        require(
            "data" not in directory.parts
            and not any(p.is_symlink() for p in (directory, *directory.parents)),
            "G2C bundle path",
        )
        manifest_bytes = regular_read(directory / "manifest.json", limit=2_097_152)
        require(sha(manifest_bytes) == expected_manifest_sha256, "G2C external manifest SHA")
        manifest = parse_canonical([manifest_bytes], limit=2_097_152)
        require(
            type(manifest) is dict
            and set(manifest)
            == {
                "schema",
                "contract_sha256",
                "source_closure_sha256",
                "runner_sha256",
                "fixture",
                "input_sha256",
                "observations",
                "native_sha256",
                "native_output_sha256",
                "run_identity",
                "run_id_sha256",
                "codec_profile",
                "streams",
            },
            "G2C manifest shape",
        )
        require(
            manifest["schema"] == "agicore:g2c-synthetic-bundle:v1"
            and manifest["contract_sha256"] == V4_SHA
            and manifest["source_closure_sha256"] == contract["source_closure_sha256"]
            and manifest["runner_sha256"] == v4.RUNNER_SHA256,
            "G2C source binding",
        )
        require(manifest["fixture"] in contract["fixtures"], "G2C unknown fixture")
        require(
            expected_fixture is None or expected_fixture == manifest["fixture"],
            "V5 supervised fixture mismatch",
        )
        spec = contract["fixtures"][manifest["fixture"]]
        raw = regular_read(directory / "source.synthetic.txt", limit=1_048_576)
        require(
            sha(raw) == manifest["input_sha256"] == spec["input_sha256"]
            and manifest["observations"] == spec["observations"],
            "G2C source binding",
        )
        profile = codec_profile()
        require(manifest["codec_profile"] == profile, "G2C codec profile")
        streams = manifest["streams"]
        require(
            type(streams) is list
            and [s["stream_id"] for s in streams] == ["native_result", "source_witnesses"],
            "G2C stream inventory",
        )
        inventory = {
            "streams": [
                {"segments": [segment for page in stream["pages"] for segment in page["segments"]]}
                for stream in streams
            ]
        }
        _inventory(directory, inventory, completed=not seal)
        native_bytes = v4.decode_pages(streams[0], directory, profile)
        require(
            len(native_bytes) <= contract["tiers"][str(spec["observations"])]["logical_bytes"]
            and sha(native_bytes) == expected_native_sha256 == manifest["native_sha256"],
            "G2C external native SHA/size",
        )
        _, protocol = contracts()
        document = parse_native(
            native_bytes, limit=v4.MAX_LOGICAL_BYTES, schema=protocol["result_schema"]
        )
        witness_bytes = v4.decode_pages(streams[1], directory, profile)
        witnesses = [parse_canonical([line]) for line in witness_bytes.splitlines(keepends=True)]
        require(
            document["run_identity"] == manifest["run_identity"]
            and document["run_id_sha256"] == manifest["run_id_sha256"]
            and document["output_sha256"] == manifest["native_output_sha256"],
            "G2C unmodified native identity",
        )
        audit = audit_optimized_native(
            document,
            witnesses,
            raw,
            runner_sha=v4.RUNNER_SHA256,
            input_sha=spec["input_sha256"],
            maximum=spec["observations"],
        )
        production_bytes = regular_read(directory / "production.json", limit=2_097_152)
        production = parse_canonical([production_bytes])
        require(
            production
            == {
                "schema": "agicore:g2c-production:v1",
                "status": "PRODUCED_INCOMPLETE",
                "contract_sha256": V4_SHA,
                "fixture": manifest["fixture"],
                "manifest_sha256": expected_manifest_sha256,
                "native_sha256": expected_native_sha256,
                "input_sha256": spec["input_sha256"],
                "runner_sha256": v4.RUNNER_SHA256,
            },
            "G2C production receipt",
        )
        verification = {
            "schema": "agicore:g2c-verification:v5",
            "verifier_contract_sha256": expected_verifier_sha256,
            "status": "PASS",
            "contract_sha256": V4_SHA,
            "manifest_sha256": expected_manifest_sha256,
            "native_sha256": expected_native_sha256,
            "input_sha256": sha(raw),
            "production_sha256": sha(production_bytes),
            "audit": audit,
            "closed_positions": len(document["closed_trade_records"]),
            "open_positions": len(document["open_trade_records"]),
            "metrics_counts": {
                k: document["metrics"][k]
                for k in (
                    "long_entry_fills",
                    "short_entry_fills",
                    "risk_rejections",
                    "suppressed_position_open_events",
                    "expired_contexts",
                    "structural_stop_exits",
                    "ema20_exits",
                )
            },
            "gap_stop_exits": sum(
                e.get("trigger_phase") == "BAR_OPEN_GAP"
                for e in document["immutable_lifecycle_records"]["exits"]
            ),
        }
        completion = {
            "schema": "agicore:g2c-completion:v5",
            "verifier_contract_sha256": expected_verifier_sha256,
            "status": "COMPLETE",
            "verification_sha256": sha(canonical(verification)),
            "native_sha256": expected_native_sha256,
            "contract_sha256": V4_SHA,
        }
        if expected_fixture is not None:
            _loaded_sources(contract)
        if seal:
            immutable_write(directory / "verification.json", canonical(verification))
            immutable_write(directory / "completion.json", canonical(completion))
        else:
            require(
                regular_read(directory / "verification.json") == canonical(verification)
                and regular_read(directory / "completion.json") == canonical(completion),
                "G2C verification receipt and seal",
            )
        return verification
    except StorageProofError:
        raise
    except (OSError, KeyError, IndexError, TypeError, ValueError, ArithmeticError) as exc:
        raise StorageProofError("invalid G2C V5 bundle: FAIL_CLOSED") from exc


def _loaded_sources(contract):
    """Check the actual verification imports before emitting a supervised receipt."""
    allowed = {e["path"] for e in contract["source_closure"]} | {MODULE, WORKER}
    for module in list(sys.modules.values()):
        name = getattr(module, "__file__", None)
        if name:
            path = Path(name).resolve()
            if path.suffix == ".py" and path.is_relative_to(ROOT):
                require(
                    path.relative_to(ROOT).as_posix() in allowed, "unregistered verifier source"
                )
