"""Produce bounded G2B bundles from registered invented fixtures only."""

from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

from . import ema_pullback_v2_development_replay as reference
from . import ema_pullback_v2_recovery_optimized as optimized
from .ema_pullback_v2_g2b_contract import (
    MAX_LOGICAL_BYTES,
    fixture_spec,
    generate_fixture,
    load_contract,
)
from .ema_pullback_v2_g2b_segments import encode_segments
from .ema_pullback_v2_recovery_evidence import CanonicalEncoderV1
from .ema_pullback_v2_storage_format import canonical, codec_profile, immutable_write, require, sha

MANIFEST_SCHEMA = "agicore:optimized-synthetic-bundle:v1"


def _witnesses(raw: bytes) -> list[dict]:
    """Create row witnesses from the frozen parser and exact source bytes."""
    bars = reference.parse_ninjatrader_last_rows_v2(raw)
    lines = raw.splitlines(keepends=True)
    require(len(bars) == len(lines), "G2B witness row count")
    result, offset = [], 0
    for bar, line in zip(bars, lines, strict=True):
        close_text = line.rstrip(b"\r\n").decode("ascii").split(";")[4]
        close = Fraction(Decimal(close_text))
        result.append(
            {
                "bar_index": bar.bar_index,
                "timestamp_utc": bar.timestamp_utc.isoformat().replace("+00:00", "Z"),
                "raw_close_text": close_text,
                "close_exact": {"numerator": close.numerator, "denominator": close.denominator},
                "source_row_byte_offset": offset,
                "source_row_size_bytes": len(line),
                "source_row_sha256": sha(line),
            }
        )
        offset += len(line)
    return result


def produce_bundle(destination: Path, fixture: str, *, expected_contract_sha256: str) -> dict:
    """Run the unchanged optimized loop and persist its original identity and bytes."""
    contract = load_contract(expected_contract_sha256)
    spec = fixture_spec(contract, fixture)
    raw = generate_fixture(contract, fixture)
    destination = destination.absolute()
    require(
        "data" not in destination.parts
        and not destination.exists()
        and not destination.is_symlink()
        and not any(parent.is_symlink() for parent in destination.parents),
        "G2B output path",
    )
    bindings = reference.read_frozen_replay_bindings_v2()
    document, identity = optimized.run_synthetic_native_v1(raw, bindings=bindings)
    encoder = CanonicalEncoderV1()
    require(
        document["run_identity"] == asdict(identity)
        and identity.runner_source_sha256 == contract["runner_sha256"]
        and identity.dataset_raw_sha256 == spec["input_sha256"]
        and document["run_id_sha256"] == identity.sha256
        and document["output_sha256"]
        == encoder.sha256({k: v for k, v in document.items() if k != "output_sha256"}),
        "G2B optimized native identity",
    )
    native_bytes = encoder.bytes(document)
    require(len(native_bytes) <= MAX_LOGICAL_BYTES, "G2B native byte limit")
    witnesses = _witnesses(raw)
    require(len(witnesses) == spec["observations"], "G2B observation count")
    witness_bytes = b"".join(canonical(w) for w in witnesses)
    destination.mkdir(parents=True)
    immutable_write(destination / "source.synthetic.txt", raw)
    profile = codec_profile()
    streams = [
        encode_segments(native_bytes, "native_result", destination, profile),
        encode_segments(witness_bytes, "source_witnesses", destination, profile),
    ]
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "contract_sha256": expected_contract_sha256,
        "source_closure_sha256": contract["source_closure_sha256"],
        "runner_sha256": contract["runner_sha256"],
        "strategy_manifest_sha256": contract["strategy_manifest_sha256"],
        "development_protocol_sha256": contract["development_protocol_sha256"],
        "producer_sha256": contract["producer"]["sha256"],
        "storage_sha256": contract["storage"]["sha256"],
        "verifier_sha256": contract["verifier"]["sha256"],
        "auditor_sha256": contract["auditor"]["sha256"],
        "fixture": fixture,
        "input_sha256": sha(raw),
        "observations": len(witnesses),
        "native_sha256": sha(native_bytes),
        "native_output_sha256": document["output_sha256"],
        "run_identity": document["run_identity"],
        "run_id_sha256": document["run_id_sha256"],
        "codec_profile": profile,
        "streams": streams,
    }
    manifest_bytes = canonical(manifest)
    immutable_write(destination / "manifest.json", manifest_bytes)
    receipt = {
        "schema": "agicore:optimized-synthetic-production:v1",
        "status": "PRODUCED_INCOMPLETE",
        "contract_sha256": expected_contract_sha256,
        "manifest_sha256": sha(manifest_bytes),
        "native_sha256": sha(native_bytes),
        "input_sha256": sha(raw),
        "runner_sha256": identity.runner_source_sha256,
    }
    immutable_write(destination / "production.json", canonical(receipt))
    return receipt
