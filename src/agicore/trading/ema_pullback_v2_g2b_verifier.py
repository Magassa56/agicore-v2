"""Independent G2B bundle verification; no strategy or producer imports."""

from __future__ import annotations

import os
from pathlib import Path

from .ema_pullback_v2_g2b_audit import audit_optimized_native
from .ema_pullback_v2_g2b_contract import (
    MAX_LOGICAL_BYTES,
    MAX_OBSERVATIONS,
    fixture_spec,
    load_contract,
)
from .ema_pullback_v2_g2b_segments import decode_segments
from .ema_pullback_v2_storage_format import (
    StorageProofError,
    canonical,
    codec_profile,
    contracts,
    immutable_write,
    parse_canonical,
    regular_read,
    require,
    sha,
)


def _inventory(directory: Path, manifest: dict, *, completed: bool) -> None:
    expected = {"manifest.json", "production.json", "source.synthetic.txt"}
    if completed:
        expected.update(("verification.json", "completion.json"))
    aliases = {}
    for stream in manifest["streams"]:
        for segment in stream["segments"]:
            for chunk in segment["chunks"]:
                expected.add(chunk["object_identity"])
                stored = chunk["stored_sha256"]
                identity = (
                    chunk["codec"],
                    chunk["uncompressed_sha256"],
                    chunk["uncompressed_size_bytes"],
                )
                require(
                    stored not in aliases or aliases[stored] == identity,
                    "G2B conflicting object alias",
                )
                aliases[stored] = identity
    actual = set()
    for root, dirs, files in os.walk(directory, followlinks=False):
        for name in (*dirs, *files):
            require(not (Path(root) / name).is_symlink(), "G2B bundle symlink")
        actual.update(str((Path(root) / name).relative_to(directory)) for name in files)
    require(actual == expected, "G2B missing or undeclared artifacts")


def verify_bundle(
    directory: Path,
    *,
    expected_contract_sha256: str,
    expected_manifest_sha256: str,
    expected_native_sha256: str,
    seal: bool = False,
) -> tuple[bytes, dict]:
    """Reconstruct exact optimized bytes and independently audit stored evidence.

    Commitments must be retained outside the bundle. This auditor does not rerun
    the strategy and does not convert the optimized identity to a reference one.
    """
    try:
        contract = load_contract(expected_contract_sha256)
        directory = directory.absolute()
        require("data" not in directory.parts and not directory.is_symlink(), "G2B bundle path")
        manifest_bytes = regular_read(directory / "manifest.json", limit=2_097_152)
        require(sha(manifest_bytes) == expected_manifest_sha256, "G2B external manifest SHA")
        manifest = parse_canonical([manifest_bytes], limit=2_097_152)
        require(
            type(manifest) is dict
            and set(manifest)
            == {
                "schema",
                "contract_sha256",
                "source_closure_sha256",
                "runner_sha256",
                "strategy_manifest_sha256",
                "development_protocol_sha256",
                "producer_sha256",
                "storage_sha256",
                "verifier_sha256",
                "auditor_sha256",
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
            "G2B manifest fields",
        )
        require(
            manifest["schema"] == "agicore:optimized-synthetic-bundle:v1"
            and manifest["contract_sha256"] == expected_contract_sha256
            and manifest["source_closure_sha256"] == contract["source_closure_sha256"]
            and manifest["runner_sha256"] == contract["runner_sha256"]
            and manifest["strategy_manifest_sha256"] == contract["strategy_manifest_sha256"]
            and manifest["development_protocol_sha256"] == contract["development_protocol_sha256"]
            and all(
                manifest[role + "_sha256"] == contract[role]["sha256"]
                for role in ("producer", "storage", "verifier", "auditor")
            ),
            "G2B source bindings",
        )
        spec = fixture_spec(contract, manifest["fixture"])
        raw = regular_read(directory / "source.synthetic.txt", limit=1_048_576)
        require(
            sha(raw) == manifest["input_sha256"] == spec["input_sha256"]
            and manifest["observations"] == spec["observations"],
            "G2B invented source binding",
        )
        require(manifest["codec_profile"] == codec_profile(), "G2B codec identity")
        streams = manifest["streams"]
        require(
            type(streams) is list
            and [stream["stream_id"] for stream in streams]
            == ["native_result", "source_witnesses"],
            "G2B stream inventory",
        )
        _inventory(directory, manifest, completed=not seal)
        native_bytes = decode_segments(streams[0], directory, manifest["codec_profile"])
        require(
            sha(native_bytes) == expected_native_sha256 == manifest["native_sha256"],
            "G2B external native SHA",
        )
        _, protocol = contracts()
        document = parse_canonical(
            [native_bytes], limit=MAX_LOGICAL_BYTES, schema=protocol["result_schema"]
        )
        witness_bytes = decode_segments(streams[1], directory, manifest["codec_profile"])
        witnesses = [parse_canonical([line]) for line in witness_bytes.splitlines(keepends=True)]
        require(
            document["run_identity"] == manifest["run_identity"]
            and document["run_id_sha256"] == manifest["run_id_sha256"]
            and document["output_sha256"] == manifest["native_output_sha256"],
            "G2B unmodified native identity",
        )
        audit = audit_optimized_native(
            document,
            witnesses,
            raw,
            runner_sha=contract["runner_sha256"],
            input_sha=spec["input_sha256"],
            maximum=MAX_OBSERVATIONS,
        )
        production_bytes = regular_read(directory / "production.json", limit=2_097_152)
        production = parse_canonical([production_bytes])
        require(
            production
            == {
                "schema": "agicore:optimized-synthetic-production:v1",
                "status": "PRODUCED_INCOMPLETE",
                "contract_sha256": expected_contract_sha256,
                "manifest_sha256": expected_manifest_sha256,
                "native_sha256": expected_native_sha256,
                "input_sha256": spec["input_sha256"],
                "runner_sha256": contract["runner_sha256"],
            },
            "G2B production receipt",
        )
        verification = {
            "schema": "agicore:optimized-synthetic-verification:v1",
            "status": "PASS",
            "contract_sha256": expected_contract_sha256,
            "manifest_sha256": expected_manifest_sha256,
            "native_sha256": expected_native_sha256,
            "input_sha256": spec["input_sha256"],
            "runner_sha256": contract["runner_sha256"],
            "production_sha256": sha(production_bytes),
            "audit": audit,
        }
        completion = {
            "schema": "agicore:optimized-synthetic-completion:v1",
            "status": "COMPLETE",
            "verification_sha256": sha(canonical(verification)),
            "native_sha256": expected_native_sha256,
            "contract_sha256": expected_contract_sha256,
        }
        if seal:
            immutable_write(directory / "verification.json", canonical(verification))
            immutable_write(directory / "completion.json", canonical(completion))
        else:
            require(
                regular_read(directory / "verification.json") == canonical(verification),
                "G2B verification receipt",
            )
            require(
                regular_read(directory / "completion.json") == canonical(completion),
                "G2B completion seal",
            )
        return native_bytes, verification
    except StorageProofError:
        raise
    except (OSError, KeyError, IndexError, TypeError, ValueError, ArithmeticError) as exc:
        raise StorageProofError("invalid G2B bundle: FAIL_CLOSED") from exc
