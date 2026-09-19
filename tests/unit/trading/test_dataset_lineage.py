"""Tests for the independent NQ/MNQ dataset-lineage contract."""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from agicore.trading.dataset_lineage import (
    ContractIdentityEvidence,
    DatasetInstrument,
    DatasetLineageError,
    DatasetLineageManifest,
    DatasetRole,
    OOSAccessState,
    PreparedDatasetLineageManifest,
    SourceExposure,
    TimestampSemantics,
    prepare_dataset_lineage_manifest,
    validate_dataset_lineage_registry,
    verify_dataset_lineage_manifest,
)

RAW = "1" * 64
DERIVED = "2" * 64
NEXT = "3" * 64
EVIDENCE = "a" * 64


def _manifest(**changes: object) -> DatasetLineageManifest:
    base = DatasetLineageManifest(
        lineage_id="mnq-clean-v1",
        dataset_id="mnq-03-26-development-v1",
        instrument=DatasetInstrument.MNQ,
        contract_id="MNQ 03-26",
        bar_interval="1 minute",
        timestamp_semantics=TimestampSemantics.BAR_CLOSE,
        timezone_name="America/Chicago",
        dst_policy="IANA America/Chicago DST rules",
        rollover_policy="single-contract; no rollover adjustment",
        ohlcv_semantics="exchange trade bars; OHLC from trades",
        volume_semantics="reported contract trade volume",
        session_calendar="CME equity index futures ETH",
        holiday_calendar="CME calendar with documented early closes",
        source_provider="sanitized-source-provider",
        source_software="sanitized-exporter",
        source_software_version="1.0",
        acquisition_timestamp_utc="2026-09-19T08:00:00Z",
        source_raw_filename="source.bin",
        source_raw_sha256=RAW,
        dataset_filename="dataset.bin",
        dataset_sha256=DERIVED,
        transformation_command="split --policy development-v1",
        parent_dataset_sha256=RAW,
        role=DatasetRole.DEVELOPMENT,
        source_exposure=SourceExposure.EXPOSED_DEVELOPMENT,
        oos_access_state=OOSAccessState.NOT_APPLICABLE,
        contract_identity_evidence=ContractIdentityEvidence(
            evidence_type="EXPORT_METADATA",
            evidence_reference="sanitized-export-record-1",
            evidence_sha256=EVIDENCE,
        ),
    )
    return replace(base, **changes)


def test_prepare_is_deterministic_price_free_and_normalizes_hashes() -> None:
    manifest = _manifest(source_raw_sha256=RAW.upper(), dataset_sha256=DERIVED.upper())

    first = prepare_dataset_lineage_manifest(manifest)
    second = prepare_dataset_lineage_manifest(manifest)
    payload = json.loads(first.canonical_json)

    assert first == second
    assert len(first.manifest_sha256) == 64
    assert first.manifest.source_raw_sha256 == RAW
    assert first.manifest.dataset_sha256 == DERIVED
    assert payload["instrument"] == "MNQ"
    assert payload["role"] == "DEVELOPMENT"
    assert not ({"open", "high", "low", "close", "volume", "price"} & set(payload))


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("contract_id", "UNKNOWN", "explicitly known"),
        ("dataset_sha256", "not-a-hash", "64-character SHA-256"),
        ("source_raw_filename", "C:\\private\\source.bin", "without a path"),
        ("timezone_name", "Not/A_Timezone", "recognized IANA timezone"),
        ("acquisition_timestamp_utc", "2026-09-19T08:00:00", "must be UTC"),
    ],
)
def test_prepare_rejects_unknown_or_unverifiable_required_metadata(
    field: str, value: object, message: str
) -> None:
    with pytest.raises(DatasetLineageError, match=message):
        prepare_dataset_lineage_manifest(_manifest(**{field: value}))


def test_prepare_requires_explicit_enum_instrument_not_a_label() -> None:
    with pytest.raises(DatasetLineageError, match="explicitly NQ or MNQ"):
        prepare_dataset_lineage_manifest(_manifest(instrument="MNQ"))  # type: ignore[arg-type]


def test_prepare_rejects_private_paths_in_evidence_and_transformation() -> None:
    with pytest.raises(DatasetLineageError, match="invalid identifier format"):
        prepare_dataset_lineage_manifest(
            _manifest(
                contract_identity_evidence=ContractIdentityEvidence(
                    evidence_type="EXPORT_METADATA",
                    evidence_reference="C:\\private\\receipt.json",
                    evidence_sha256=EVIDENCE,
                )
            )
        )
    with pytest.raises(DatasetLineageError, match="absolute or home path"):
        prepare_dataset_lineage_manifest(
            _manifest(transformation_command="split --input=/private/source.bin")
        )


def test_root_and_transformation_links_fail_closed() -> None:
    root = _manifest(
        dataset_sha256=RAW,
        transformation_command="NONE",
        parent_dataset_sha256=None,
    )
    assert prepare_dataset_lineage_manifest(root).manifest.dataset_sha256 == RAW

    with pytest.raises(DatasetLineageError, match="preserve the raw SHA-256"):
        prepare_dataset_lineage_manifest(replace(root, dataset_sha256=DERIVED))
    with pytest.raises(DatasetLineageError, match="must declare parent"):
        prepare_dataset_lineage_manifest(_manifest(parent_dataset_sha256=None))


def test_registry_accepts_one_instrument_parent_chain() -> None:
    parent = prepare_dataset_lineage_manifest(_manifest())
    child = prepare_dataset_lineage_manifest(
        _manifest(
            dataset_id="mnq-03-26-validation-v1",
            dataset_filename="validation.bin",
            dataset_sha256=NEXT,
            transformation_command="filter --policy validation-v1",
            parent_dataset_sha256=DERIVED,
            role=DatasetRole.VALIDATION,
        )
    )

    assert validate_dataset_lineage_registry((parent, child)) == (parent, child)


def test_registry_never_allows_one_raw_source_to_be_both_nq_and_mnq() -> None:
    mnq = prepare_dataset_lineage_manifest(_manifest())
    nq = prepare_dataset_lineage_manifest(
        _manifest(
            lineage_id="nq-clean-v1",
            dataset_id="nq-03-26-development-v1",
            instrument=DatasetInstrument.NQ,
            contract_id="NQ 03-26",
            dataset_filename="nq-dataset.bin",
            dataset_sha256=NEXT,
        )
    )

    with pytest.raises(DatasetLineageError, match="both NQ and MNQ"):
        validate_dataset_lineage_registry((mnq, nq))


def test_registry_rejects_cross_instrument_parent_even_with_distinct_raw_sources() -> None:
    parent = prepare_dataset_lineage_manifest(_manifest())
    child = prepare_dataset_lineage_manifest(
        _manifest(
            lineage_id="nq-clean-v1",
            dataset_id="nq-03-26-validation-v1",
            instrument=DatasetInstrument.NQ,
            contract_id="NQ 03-26",
            source_raw_sha256="4" * 64,
            dataset_filename="nq-validation.bin",
            dataset_sha256=NEXT,
            parent_dataset_sha256=DERIVED,
            role=DatasetRole.VALIDATION,
        )
    )

    with pytest.raises(DatasetLineageError, match="instruments differ"):
        validate_dataset_lineage_registry((parent, child))


def test_registered_mnq_dataset_cannot_be_redeclared_as_nq_raw_source() -> None:
    mnq = prepare_dataset_lineage_manifest(_manifest())
    nq = prepare_dataset_lineage_manifest(
        _manifest(
            lineage_id="nq-clean-v1",
            dataset_id="nq-imported-development-v1",
            instrument=DatasetInstrument.NQ,
            contract_id="NQ 03-26",
            source_raw_filename="nq-source.bin",
            source_raw_sha256=DERIVED,
            dataset_filename="nq-imported.bin",
            dataset_sha256=NEXT,
            parent_dataset_sha256=DERIVED,
        )
    )

    with pytest.raises(DatasetLineageError, match="other instrument"):
        validate_dataset_lineage_registry((mnq, nq))


def test_oos_must_be_sealed_unexposed_and_isolated_from_development() -> None:
    oos_manifest = _manifest(
        dataset_id="mnq-03-26-oos-v1",
        dataset_filename="oos.bin",
        dataset_sha256=NEXT,
        role=DatasetRole.OOS_TEST,
        source_exposure=SourceExposure.UNEXPOSED,
        oos_access_state=OOSAccessState.SEALED,
        oos_boundary_id="mnq-oos-boundary-v1",
    )
    oos = prepare_dataset_lineage_manifest(oos_manifest)
    assert oos.manifest.oos_access_state is OOSAccessState.SEALED

    with pytest.raises(DatasetLineageError, match="unexposed source"):
        prepare_dataset_lineage_manifest(
            replace(oos_manifest, source_exposure=SourceExposure.EXPOSED_DEVELOPMENT)
        )
    with pytest.raises(DatasetLineageError, match="shared with a non-OOS role"):
        validate_dataset_lineage_registry((prepare_dataset_lineage_manifest(_manifest()), oos))


def test_registry_rejects_an_unresolved_transformation_parent() -> None:
    orphan = prepare_dataset_lineage_manifest(_manifest(parent_dataset_sha256="f" * 64))
    with pytest.raises(DatasetLineageError, match="unresolved parent"):
        validate_dataset_lineage_registry((orphan,))


def test_registry_rejects_a_parent_cycle() -> None:
    first = prepare_dataset_lineage_manifest(_manifest(parent_dataset_sha256=NEXT))
    second = prepare_dataset_lineage_manifest(
        _manifest(
            dataset_id="mnq-03-26-validation-v1",
            dataset_filename="validation.bin",
            dataset_sha256=NEXT,
            parent_dataset_sha256=DERIVED,
            role=DatasetRole.VALIDATION,
        )
    )

    with pytest.raises(DatasetLineageError, match="parent cycle"):
        validate_dataset_lineage_registry((first, second))


def test_verify_rejects_a_forged_prepared_manifest_hash() -> None:
    prepared = prepare_dataset_lineage_manifest(_manifest())
    forged = PreparedDatasetLineageManifest(
        manifest=prepared.manifest,
        canonical_json=prepared.canonical_json,
        manifest_sha256="f" * 64,
    )
    with pytest.raises(DatasetLineageError, match="canonical reconstruction"):
        verify_dataset_lineage_manifest(forged)
