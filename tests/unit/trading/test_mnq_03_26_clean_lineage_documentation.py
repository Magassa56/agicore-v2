"""Fail-closed checks for the price-free MNQ 03-26 replication lineage."""

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
CLEAN = ROOT / "docs/evidence/MNQ_03-26_CLEAN_LINEAGE"
PROTOCOL = ROOT / "docs/evidence/EMA_PULLBACK_V1B_MNQ_03_26_REPLICATION_PROTOCOL.json"
V1B_MODULE = ROOT / "src/agicore/trading/ema_pullback_v1b_mnq.py"
RAW_SHA256 = "2122722f25dbc865dad154905309b5e76d2190561ffc64acdaa955365ccb9efc"
ATTESTATION_SHA256 = "081386347dcf52ba6eff9b66143b9e217881f11f2cd0a9ab0c4439c7df7c65d7"


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


def test_clean_lineage_is_a_canonical_exposed_development_root() -> None:
    record = _read_json(CLEAN / "dataset_manifest.json")
    payload = record["canonical_contract_payload"]
    assert isinstance(payload, dict)

    prepared = prepare_dataset_lineage_manifest(_manifest(payload))

    assert record["gate_status"] == "PASS"
    assert record["validation_status"] == "PASS"
    assert prepared.manifest_sha256 == record["manifest_sha256"]
    assert json.loads(prepared.canonical_json) == payload
    assert prepared.manifest.instrument is DatasetInstrument.MNQ
    assert prepared.manifest.contract_id == "MNQ 03-26"
    assert prepared.manifest.source_raw_sha256 == RAW_SHA256
    assert prepared.manifest.dataset_sha256 == RAW_SHA256
    assert prepared.manifest.transformation_command == "NONE"
    assert prepared.manifest.parent_dataset_sha256 is None
    assert prepared.manifest.role is DatasetRole.DEVELOPMENT
    assert prepared.manifest.source_exposure is SourceExposure.EXPOSED_DEVELOPMENT
    assert prepared.manifest.oos_access_state is OOSAccessState.NOT_APPLICABLE


def test_final_attestation_and_source_metadata_are_exact() -> None:
    evidence = _read_json(CLEAN / "provenance_evidence.json")
    attestation = evidence["contract_identity_evidence"]
    raw = evidence["raw_source"]
    assert isinstance(attestation, dict)
    assert isinstance(raw, dict)

    assert attestation["sha256"] == ATTESTATION_SHA256
    assert attestation["size_bytes"] == 1844
    assert attestation["classification"] == "FINAL_RETROSPECTIVE_OPERATOR_ATTESTATION"
    assert attestation["owner_supplied_sha256_matches_audited_bytes"] is True
    assert attestation["exact_raw_sha256_binding"] is True
    assert raw["sha256"] == RAW_SHA256
    assert raw["size_bytes"] == 3946060
    assert raw["row_count"] == 74308
    assert raw["first_timestamp_utc"] == "2026-01-01T01:22:00Z"
    assert raw["last_timestamp_utc"] == "2026-03-20T13:30:00Z"
    assert raw["last_write_time_utc"] == "2026-09-30T17:45:23Z"


def test_source_contract_and_evidence_classes_remain_explicit() -> None:
    evidence = _read_json(CLEAN / "provenance_evidence.json")
    source = evidence["source_configuration"]
    classes = evidence["evidence_classification"]
    legacy = evidence["legacy_exclusion"]
    assert isinstance(source, dict)
    assert isinstance(classes, dict)
    assert isinstance(legacy, dict)

    assert source["instrument"] == "MNQ"
    assert source["contract_id"] == "MNQ 03-26"
    assert source["bar_interval"] == "1 minute"
    assert source["data_type"] == "Last"
    assert source["merge_policy"] == "DoNotMerge"
    assert source["continuous_contract"] is False
    assert source["trading_hours_template"] == "CME US Index Futures ETH"
    assert source["account_provider"] == "Apex Trader Funding"
    assert source["market_data_provider_or_routing"] == "Rithmic"
    assert source["software_version"] == "8.0.28.0 64-bit"
    assert source["source_timestamp_timezone"] == "UTC"
    assert source["source_timestamp_semantics"] == "BAR_END"
    assert source["transformation_after_export"] == "NONE"
    assert source["parent_dataset_sha256"] is None
    assert "RETROSPECTIVE" in str(classes["holiday_and_early_close_policy"])
    assert "HISTORICAL" in str(classes["software_version"])
    assert legacy["relationship_to_clean_root"] == "NONE"
    assert legacy["is_parent_of_clean_root"] is False
    assert legacy["used_for_replication"] is False


def test_precommitted_strategy_and_protocol_remain_byte_for_byte_unchanged() -> None:
    assert hashlib.sha256(PROTOCOL.read_bytes()).hexdigest() == (
        "c431c991c290f000bfdd9f39f01372ccfc05c963911e11534184d1ab95b07d37"
    )
    assert hashlib.sha256(V1B_MODULE.read_bytes()).hexdigest() == (
        "c61703033504539cda5067798c5b38832f406484e069228c9b6e3eb0533ee717"
    )


def test_public_lineage_contains_no_market_rows_prices_accounts_or_oos_access() -> None:
    manifest = _read_json(CLEAN / "dataset_manifest.json")
    evidence = _read_json(CLEAN / "provenance_evidence.json")
    supplemental = manifest["supplemental_source_facts"]
    privacy = evidence["privacy"]
    governance = evidence["governance"]
    assert isinstance(supplemental, dict)
    assert isinstance(privacy, dict)
    assert isinstance(governance, dict)

    assert supplemental["market_rows_committed"] == 0
    assert supplemental["prices_committed"] == 0
    assert supplemental["oos_data_accessed"] is False
    assert privacy["raw_files_committed"] is False
    assert privacy["screenshots_committed"] is False
    assert privacy["account_identifiers_committed"] is False
    assert privacy["credentials_committed"] is False
    assert privacy["oos_accessed"] is False
    assert governance["dataset_role"] == "EXPOSED_DEVELOPMENT_REPLICATION"
    assert governance["oos"] is False

    public_text = "\n".join(path.read_text(encoding="utf-8") for path in CLEAN.glob("*.json"))
    assert re.search(r"(?m)^\d{8} \d{6};", public_text) is None
    assert re.search(r"(?m)^\d{8};", public_text) is None
    assert "account_number" not in public_text.lower()
    assert re.search(r'(?i)"(?:password|api_key|access_token|secret)"\s*:', public_text) is None
