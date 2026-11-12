"""Invented-only G2C adapter around the unchanged G2B codec and V2 runner.

Every public operation requires an externally retained contract SHA. This module
does not expose a raw-data input, real recovery claim, broker or order interface.
The independent auditor checks recorded invariants; it does not rerun signals.
"""

from __future__ import annotations

import re
from dataclasses import asdict
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from .ema_pullback_v2_g2b_audit import audit_optimized_native
from .ema_pullback_v2_g2b_contract import (
    PROTOCOL_SHA256,
    RUNNER_SHA256,
    STRATEGY_SHA256,
    _source_files_match,
)
from .ema_pullback_v2_g2b_contract import (
    load_contract as load_g2b_contract,
)
from .ema_pullback_v2_g2b_segments import decode_segments, encode_segments
from .ema_pullback_v2_g2b_verifier import _inventory
from .ema_pullback_v2_storage_format import (
    ROOT,
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

CONTRACT_PATH = ROOT / "docs/evidence/EMA_PULLBACK_V2_G2C_SYNTHETIC_CONTRACT_V3.json"
CONTRACT_V4_PATH = ROOT / "docs/evidence/EMA_PULLBACK_V2_G2C_SYNTHETIC_CONTRACT_V4.json"
PREDECESSOR_CONTRACT_SHA256 = "5de23f01bb157b2d7575a54dcc0d36033f6ba3ae751f6338067088c895bf6663"
PARENT_SHA256 = "1d0a7b3f929825c3a7009d694b02b618643bd22b246b75865be71dc7de1567d4"
PAGE_BYTES = 33_554_432
MAX_LOGICAL_BYTES = 268_435_456
ADAPTER_PATH = "src/agicore/trading/ema_pullback_v2_g2c_scaling.py"
SUPERVISOR_PATH = "tools/ema_pullback_v2_g2c_supervisor.py"
FIXTURE_PATH = "tests/unit/trading/v2_recovery_synthetic_fixtures.py"


def load_contract(expected_sha256: str) -> dict:
    """Authenticate the registration, inherited G2B closure and G2C sources."""
    require(
        type(expected_sha256) is str and re.fullmatch(r"[0-9a-f]{64}", expected_sha256),
        "G2C external contract identity",
    )
    candidates = [regular_read(CONTRACT_PATH, limit=2_097_152)]
    if CONTRACT_V4_PATH.is_file():
        candidates.append(regular_read(CONTRACT_V4_PATH, limit=2_097_152))
    matches = [candidate for candidate in candidates if sha(candidate) == expected_sha256]
    require(len(matches) == 1, "G2C contract mismatch")
    raw = matches[0]
    contract = parse_canonical([raw], limit=2_097_152)
    parent = load_g2b_contract(PARENT_SHA256)
    require(
        contract["schema"]
        in {
            "agicore:g2c-invented-scaling-contract:v3",
            "agicore:g2c-invented-scaling-contract:v4",
        }
        and contract["g2b_contract_sha256"] == PARENT_SHA256
        and contract["runner_sha256"] == RUNNER_SHA256
        and contract["strategy_manifest_sha256"] == STRATEGY_SHA256
        and contract["development_protocol_sha256"] == PROTOCOL_SHA256
        and contract["input_domain"] == "INVENTED_ONLY"
        and contract["real_execution_authorized"] is False
        and contract["page_bytes"] == PAGE_BYTES
        and contract["maximum_logical_bytes"] == MAX_LOGICAL_BYTES,
        "G2C frozen identities and scope",
    )
    if contract["schema"].endswith(":v4"):
        previous_raw = regular_read(CONTRACT_PATH, limit=2_097_152)
        require(sha(previous_raw) == PREDECESSOR_CONTRACT_SHA256, "G2C V3 identity")
        previous = parse_canonical([previous_raw], limit=2_097_152)
        require(
            contract["predecessor"]
            == {
                "contract_sha256": PREDECESSOR_CONTRACT_SHA256,
                "gate_report_sha256": "c7b1c48c69f81439892082cc23bb7ddb34190775b93f528177df6a6d49dad555",
                "negative_report_sha256": "ead441231b611d445ece5d4489d748a0fc51e8a2c7c9e39348f2af86070e25f4",
                "bundles_sha256": "8dfa4e7aa278cbc1503aae4ea48489f0330c720b2a6f6f0d49966b065c349fa7",
                "implementation_commit": "9e6eadcd81c2aec152872aa7783b5374e9731568",
            }
            and all(
                contract[key] == previous[key]
                for key in ("fixtures", "tier_fixtures", "tiers", "codec")
            ),
            "G2C V4 historical gate and unchanged experiment",
        )
    entries = contract["source_closure"]
    require(sha(canonical(entries)) == contract["source_closure_sha256"], "G2C closure digest")
    _source_files_match(entries)
    sources = {entry["path"]: entry["sha256"] for entry in entries}
    require(
        all(sources.get(e["path"]) == e["sha256"] for e in parent["source_closure"])
        and all(p in sources for p in (ADAPTER_PATH, SUPERVISOR_PATH, FIXTURE_PATH))
        and sources.get("src/agicore/trading/ema_pullback_v2_recovery_optimized.py")
        == RUNNER_SHA256,
        "G2C complete inherited source bindings",
    )
    require(
        contract["producer"] == {"path": ADAPTER_PATH, "sha256": sources[ADAPTER_PATH]}
        and contract["verifier"] == {"path": ADAPTER_PATH, "sha256": sources[ADAPTER_PATH]}
        and contract["supervisor"] == {"path": SUPERVISOR_PATH, "sha256": sources[SUPERVISOR_PATH]},
        "G2C role identity",
    )
    require(
        contract["codec"]
        == {
            "profile_id": "EXACT_NATIVE_BYTE_SHARDS_DEFLATE_V1",
            "algorithm": "RAW_DEFLATE",
            "level": 9,
            "window_bits": -15,
            "chunk_size": 1_048_576,
        },
        "G2C codec specification",
    )
    return contract


def invented_fixture(contract: dict, name: str) -> bytes:
    """Recreate only an explicitly registered, deterministic invented fixture."""
    require(type(name) is str and name in contract["fixtures"], "G2C unknown fixture")
    spec = contract["fixtures"][name]
    count = spec["observations"]
    require(type(count) is int and count in (1000, 5000), "G2C observation tier")
    from tests.unit.trading.v2_recovery_synthetic_fixtures import (
        FAMILIES,
        dense_lifecycle_resource_bars_v2,
        resource_fixture_bars,
    )

    if spec["generator"] == "HISTORICAL_CONSTANT":
        bars = resource_fixture_bars(FAMILIES[0], count)
        raw = b"".join(_bar_row(bar) for bar in bars)
    elif spec["generator"] == "HISTORICAL_DENSE_LIFECYCLE_V2":
        raw = b"".join(_bar_row(bar) for bar in dense_lifecycle_resource_bars_v2(count))
    else:
        require(
            count == 1000 and spec["generator"] == "G2B_PREFIX_AND_FLAT_TAIL",
            "G2C generator not authorized",
        )
        from .ema_pullback_v2_g2b_contract import generate_fixture

        parent = load_g2b_contract(PARENT_SHA256)
        prefix = generate_fixture(parent, spec["prefix_fixture"])
        last = prefix.splitlines()[-1].decode("ascii").split(";")
        timestamp = datetime.strptime(last[0], "%Y%m%d %H%M%S")
        close = Decimal(last[4])
        tail = []
        for index in range(1, count - len(prefix.splitlines()) + 1):
            stamp = (timestamp + timedelta(minutes=index)).strftime("%Y%m%d %H%M%S")
            tail.append(
                (
                    f"{stamp};{close};{close + Decimal('.25')};"
                    f"{close - Decimal('.25')};{close};100\n"
                ).encode("ascii")
            )
        raw = prefix + b"".join(tail)
    require(
        len(raw.splitlines()) == count and sha(raw) == spec["input_sha256"], "G2C fixture identity"
    )
    return raw


def _bar_row(bar) -> bytes:
    return (
        ";".join(
            (
                bar.timestamp_utc.strftime("%Y%m%d %H%M%S"),
                *(str(getattr(bar, f)) for f in ("open", "high", "low", "close")),
                str(bar.volume),
            )
        )
        + "\n"
    ).encode("ascii")


def encode_pages(raw: bytes, stream_id: str, directory: Path, profile: dict) -> dict:
    """Store bounded pages by calling the unmodified G2B segmentation codec."""
    require(type(raw) is bytes and 0 < len(raw) <= MAX_LOGICAL_BYTES, "G2C logical size")
    pages = [
        encode_segments(raw[i : i + PAGE_BYTES], stream_id, directory, profile)
        for i in range(0, len(raw), PAGE_BYTES)
    ]
    return {
        "stream_id": stream_id,
        "logical_size_bytes": len(raw),
        "logical_sha256": sha(raw),
        "pages": pages,
    }


def decode_pages(stream: dict, directory: Path, profile: dict) -> bytes:
    """Reconstruct every page, retaining G2B's original segment boundaries."""
    require(
        type(stream) is dict
        and set(stream) == {"stream_id", "logical_size_bytes", "logical_sha256", "pages"},
        "G2C stream shape",
    )
    size = stream["logical_size_bytes"]
    pages = stream["pages"]
    require(
        type(size) is int
        and 0 < size <= MAX_LOGICAL_BYTES
        and type(pages) is list
        and len(pages) == (size + PAGE_BYTES - 1) // PAGE_BYTES,
        "G2C page count",
    )
    decoded = []
    for index, page in enumerate(pages):
        require(
            page["stream_id"] == stream["stream_id"]
            and page["logical_size_bytes"] == min(PAGE_BYTES, size - index * PAGE_BYTES),
            "G2C page order and size",
        )
        decoded.append(decode_segments(page, directory, profile))
    raw = b"".join(decoded)
    require(len(raw) == size and sha(raw) == stream["logical_sha256"], "G2C logical digest")
    return raw


def produce_bundle(destination: Path, fixture: str, *, expected_contract_sha256: str) -> dict:
    """Produce original optimized native bytes for one precommitted invented input."""
    from . import ema_pullback_v2_development_replay as reference
    from . import ema_pullback_v2_recovery_optimized as optimized
    from .ema_pullback_v2_g2b_storage import _witnesses
    from .ema_pullback_v2_recovery_evidence import CanonicalEncoderV1

    contract = load_contract(expected_contract_sha256)
    spec = contract["fixtures"][fixture]
    raw = invented_fixture(contract, fixture)
    destination = destination.absolute()
    require(
        "data" not in destination.parts
        and not destination.exists()
        and not any(parent.is_symlink() for parent in (destination, *destination.parents)),
        "G2C output path",
    )
    bindings = reference.read_frozen_replay_bindings_v2()
    document, identity = optimized.run_synthetic_native_v1(raw, bindings=bindings)
    encoder = CanonicalEncoderV1()
    require(
        document["run_identity"] == asdict(identity)
        and identity.runner_source_sha256 == RUNNER_SHA256
        and identity.dataset_raw_sha256 == spec["input_sha256"]
        and document["run_id_sha256"] == identity.sha256
        and document["output_sha256"]
        == encoder.sha256({k: v for k, v in document.items() if k != "output_sha256"}),
        "G2C optimized native identity",
    )
    native_bytes = encoder.bytes(document)
    require(
        len(native_bytes) <= contract["tiers"][str(spec["observations"])]["logical_bytes"],
        "G2C native byte cap",
    )
    witnesses = _witnesses(raw)
    require(len(witnesses) == spec["observations"], "G2C witness count")
    destination.mkdir(parents=True)
    immutable_write(destination / "source.synthetic.txt", raw)
    profile = codec_profile()
    streams = [
        encode_pages(native_bytes, "native_result", destination, profile),
        encode_pages(
            b"".join(canonical(w) for w in witnesses), "source_witnesses", destination, profile
        ),
    ]
    manifest = {
        "schema": "agicore:g2c-synthetic-bundle:v1",
        "contract_sha256": expected_contract_sha256,
        "source_closure_sha256": contract["source_closure_sha256"],
        "runner_sha256": RUNNER_SHA256,
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
        "schema": "agicore:g2c-production:v1",
        "status": "PRODUCED_INCOMPLETE",
        "contract_sha256": expected_contract_sha256,
        "fixture": fixture,
        "manifest_sha256": sha(manifest_bytes),
        "native_sha256": sha(native_bytes),
        "input_sha256": sha(raw),
        "runner_sha256": RUNNER_SHA256,
    }
    immutable_write(destination / "production.json", canonical(receipt))
    return receipt


def verify_bundle(
    directory: Path,
    *,
    expected_contract_sha256: str,
    expected_manifest_sha256: str,
    expected_native_sha256: str,
    seal: bool = False,
) -> dict:
    """Independently reconstruct, audit and optionally seal a G2C bundle."""
    try:
        contract = load_contract(expected_contract_sha256)
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
            and manifest["contract_sha256"] == expected_contract_sha256
            and manifest["source_closure_sha256"] == contract["source_closure_sha256"]
            and manifest["runner_sha256"] == RUNNER_SHA256,
            "G2C source binding",
        )
        require(manifest["fixture"] in contract["fixtures"], "G2C unknown fixture")
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
        native_bytes = decode_pages(streams[0], directory, profile)
        require(
            len(native_bytes) <= contract["tiers"][str(spec["observations"])]["logical_bytes"]
            and sha(native_bytes) == expected_native_sha256 == manifest["native_sha256"],
            "G2C external native SHA/size",
        )
        _, protocol = contracts()
        document = parse_canonical(
            [native_bytes], limit=MAX_LOGICAL_BYTES, schema=protocol["result_schema"]
        )
        witness_bytes = decode_pages(streams[1], directory, profile)
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
            runner_sha=RUNNER_SHA256,
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
                "contract_sha256": expected_contract_sha256,
                "fixture": manifest["fixture"],
                "manifest_sha256": expected_manifest_sha256,
                "native_sha256": expected_native_sha256,
                "input_sha256": spec["input_sha256"],
                "runner_sha256": RUNNER_SHA256,
            },
            "G2C production receipt",
        )
        verification = {
            "schema": "agicore:g2c-verification:v1",
            "status": "PASS",
            "contract_sha256": expected_contract_sha256,
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
            "schema": "agicore:g2c-completion:v1",
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
                regular_read(directory / "verification.json") == canonical(verification)
                and regular_read(directory / "completion.json") == canonical(completion),
                "G2C verification receipt and seal",
            )
        return verification
    except StorageProofError:
        raise
    except (OSError, KeyError, IndexError, TypeError, ValueError, ArithmeticError) as exc:
        raise StorageProofError("invalid G2C bundle: FAIL_CLOSED") from exc


def compare_reference(fixture: str, *, expected_contract_sha256: str) -> dict:
    """Compare full native outputs; identity projection exists only in memory."""
    from . import ema_pullback_v2_development_replay as reference
    from . import ema_pullback_v2_recovery_optimized as optimized
    from .ema_pullback_v2_recovery_evidence import CanonicalEncoderV1

    contract = load_contract(expected_contract_sha256)
    raw = invented_fixture(contract, fixture)
    bindings = reference.read_frozen_replay_bindings_v2()
    original = reference.evaluate_synthetic_development_replay_v2(raw, bindings=bindings)
    candidate, identity = optimized.run_synthetic_native_v1(raw, bindings=bindings)
    encoder = CanonicalEncoderV1()
    optimized_bytes = encoder.bytes(candidate)
    projected = dict(candidate)
    reference_identity = reference.build_replay_run_identity_v2(identity.dataset_raw_sha256)
    projected["run_identity"] = asdict(reference_identity)
    projected["run_id_sha256"] = reference_identity.sha256
    projected["output_sha256"] = encoder.sha256(
        {k: v for k, v in projected.items() if k != "output_sha256"}
    )
    require(encoder.bytes(projected) == original.canonical_utf8, "G2C reference parity")
    return {
        "schema": "agicore:g2c-parity:v1",
        "status": "PASS",
        "fixture": fixture,
        "contract_sha256": expected_contract_sha256,
        "input_sha256": sha(raw),
        "optimized_native_sha256": sha(optimized_bytes),
        "reference_native_sha256": sha(original.canonical_utf8),
        "comparison": "EXACT_AFTER_TEMPORARY_IDENTITY_PROJECTION",
        "projected_output_persisted": False,
    }
