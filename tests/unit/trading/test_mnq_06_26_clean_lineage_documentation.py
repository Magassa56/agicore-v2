"""Regression checks for the price-free MNQ 06-26 D003 evidence record."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from agicore.trading.dataset_lineage import (
    ContractIdentityEvidence,
    DatasetInstrument,
    DatasetLineageManifest,
    DatasetRole,
    OOSAccessState,
    SourceExposure,
    TimestampSemantics,
    prepare_dataset_lineage_manifest,
)

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs" / "evidence"
CLEAN = EVIDENCE / "MNQ_06-26_CLEAN_LINEAGE"
LEGACY = EVIDENCE / "MNQ_06-26_DEVELOPMENT_EVIDENCE"
NEW_RAW = "3bd8c078d40143ccb1977562e47afadfd173f9c123e3a062ba28dbcb7721ba1a"
LEGACY_RAW = "46f2e42304573bd5e9a6c8c78a83a3cd655d493c9c1c0dc66fa2ed7406793b40"


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest(payload: dict[str, object]) -> DatasetLineageManifest:
    evidence = payload["contract_identity_evidence"]
    assert isinstance(evidence, dict)
    return DatasetLineageManifest(
        lineage_id=str(payload["lineage_id"]),
        dataset_id=str(payload["dataset_id"]),
        instrument=DatasetInstrument(str(payload["instrument"])),
        contract_id=str(payload["contract_id"]),
        bar_interval=str(payload["bar_interval"]),
        timestamp_semantics=TimestampSemantics(str(payload["timestamp_semantics"])),
        timezone_name=str(payload["timezone_name"]),
        dst_policy=str(payload["dst_policy"]),
        rollover_policy=str(payload["rollover_policy"]),
        ohlcv_semantics=str(payload["ohlcv_semantics"]),
        volume_semantics=str(payload["volume_semantics"]),
        session_calendar=str(payload["session_calendar"]),
        holiday_calendar=str(payload["holiday_calendar"]),
        source_provider=str(payload["source_provider"]),
        source_software=str(payload["source_software"]),
        source_software_version=str(payload["source_software_version"]),
        acquisition_timestamp_utc=str(payload["acquisition_timestamp_utc"]),
        source_raw_filename=str(payload["source_raw_filename"]),
        source_raw_sha256=str(payload["source_raw_sha256"]),
        dataset_filename=str(payload["dataset_filename"]),
        dataset_sha256=str(payload["dataset_sha256"]),
        transformation_command=str(payload["transformation_command"]),
        parent_dataset_sha256=None,
        role=DatasetRole(str(payload["role"])),
        source_exposure=SourceExposure(str(payload["source_exposure"])),
        oos_access_state=OOSAccessState(str(payload["oos_access_state"])),
        contract_identity_evidence=ContractIdentityEvidence(
            evidence_type=str(evidence["evidence_type"]),
            evidence_reference=str(evidence["evidence_reference"]),
            evidence_sha256=str(evidence["evidence_sha256"]),
        ),
        oos_boundary_id=None,
    )


def test_clean_lineage_manifest_is_canonical_root_and_price_free() -> None:
    record = _read_json(CLEAN / "dataset_manifest.json")
    payload = record["canonical_contract_payload"]
    assert isinstance(payload, dict)

    prepared = prepare_dataset_lineage_manifest(_manifest(payload))

    assert record["gate_status"] == "PASS"
    assert prepared.manifest_sha256 == record["manifest_sha256"]
    assert json.loads(prepared.canonical_json) == payload
    assert prepared.manifest.source_raw_sha256 == NEW_RAW
    assert prepared.manifest.dataset_sha256 == NEW_RAW
    assert prepared.manifest.transformation_command == "NONE"
    assert prepared.manifest.parent_dataset_sha256 is None
    assert prepared.manifest.role is DatasetRole.DEVELOPMENT
    assert prepared.manifest.source_exposure is SourceExposure.EXPOSED_DEVELOPMENT

    public_text = (CLEAN / "dataset_manifest.json").read_text(encoding="utf-8")
    public_text += (CLEAN / "provenance_evidence.json").read_text(encoding="utf-8")
    assert re.search(r"(?m)^\d{8} \d{6};", public_text) is None
    assert re.search(r"(?m)^\d{8};", public_text) is None


def test_preservation_evidence_keeps_legacy_raw_provisional() -> None:
    evidence = _read_json(CLEAN / "provenance_evidence.json")
    legacy = evidence["legacy_provisional_source"]
    assert isinstance(legacy, dict)
    assert legacy["sha256"] == LEGACY_RAW
    assert legacy["status"] == "PROVISIONAL"
    assert legacy["is_parent_of_clean_root"] is False
    assert legacy["reclassified_as_clean"] is False

    provisional = _read_json(LEGACY / "provisional_development_profile.json")
    assert provisional["profile_status"] == "PASS_WITH_ASSUMPTIONS"
    fields = provisional["fields"]
    assert isinstance(fields, dict)
    source = fields["source_sha256"]
    assert isinstance(source, dict)
    assert source["value"] == LEGACY_RAW


def test_attestation_and_associated_raw_hashes_are_recorded_exactly() -> None:
    evidence = _read_json(CLEAN / "provenance_evidence.json")
    attestation = evidence["contract_identity_evidence"]
    assert isinstance(attestation, dict)
    assert attestation["sha256"] == (
        "043a4467a26c9494f61526a6a2d4cb0f5187837bf2fd1cc311677c729debbf59"
    )
    assert len(str(attestation["sha256"])) == hashlib.sha256().digest_size * 2

    raws = evidence["raw_sources"]
    assert isinstance(raws, dict)
    expected = {
        "ask": (
            "MNQ 06-26.Ask.txt",
            "2026-09-21T21:36:06",
            "2026-09-21T21:36:07",
            3432017,
            "604964a556d169b083fe302a055a37790241f68564a0200966c14b98da0e6d51",
        ),
        "bid": (
            "MNQ 06-26.Bid.txt",
            "2026-09-21T21:36:30",
            "2026-09-21T21:36:32",
            4159148,
            "2437ecf0950a79fd524a06d36dd8accc58a457c1faf0037da56bfa838cbe960b",
        ),
        "last": (
            "MNQ 06-26.Last.txt",
            "2026-09-21T21:36:50",
            "2026-09-21T21:36:52",
            2791485,
            NEW_RAW,
        ),
    }
    for key, (name, created, written, size, raw_hash) in expected.items():
        raw = raws[key]
        assert raw["filename"] == name
        assert raw["creation_time_local"] == created
        assert raw["last_write_time_local"] == written
        assert raw["size_bytes"] == size
        assert raw["sha256"] == raw_hash
        assert raw["bytes_hash_and_size_verified"] is True

    assert raws["ntfs_timestamp_timezone"] == "Europe/Paris"
    assert raws["ntfs_utc_offset_at_export"] == "+02:00"
    assert raws["metadata_matches_prior_read_only_audit"] is True
    assert raws["strict_creation_sequence_verified"] is True
