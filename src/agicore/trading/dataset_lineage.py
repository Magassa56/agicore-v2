"""Fail-closed metadata contract for independent NQ and MNQ dataset lineages.

This module validates provenance metadata only. It never opens a market-data file and a
structurally valid manifest is not, by itself, proof that the asserted instrument is correct.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

SCHEMA_VERSION = "agicore.dataset-lineage.v1"
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_UNKNOWN_VALUES = {"UNKNOWN", "UNVERIFIED", "INACCESSIBLE"}


class DatasetLineageError(ValueError):
    """Raised when provenance metadata cannot be accepted without an assumption."""


class DatasetInstrument(StrEnum):
    """Instruments supported by the independent V1 research tracks."""

    NQ = "NQ"
    MNQ = "MNQ"


class DatasetRole(StrEnum):
    """Authorized roles for a newly governed dataset."""

    DEVELOPMENT = "DEVELOPMENT"
    VALIDATION = "VALIDATION"
    OOS_TEST = "OOS_TEST"
    PAPER_REFERENCE = "PAPER_REFERENCE"


class TimestampSemantics(StrEnum):
    """Meaning of the timestamp attached to one bar."""

    BAR_OPEN = "BAR_OPEN"
    BAR_CLOSE = "BAR_CLOSE"
    EVENT_TIME = "EVENT_TIME"


class SourceExposure(StrEnum):
    """Whether the raw source has already been exposed to development work."""

    EXPOSED_DEVELOPMENT = "EXPOSED_DEVELOPMENT"
    UNEXPOSED = "UNEXPOSED"


class OOSAccessState(StrEnum):
    """Access state attached to a governed OOS dataset."""

    NOT_APPLICABLE = "NOT_APPLICABLE"
    SEALED = "SEALED"


@dataclass(frozen=True)
class ContractIdentityEvidence:
    """Sanitized reference to evidence that attests the contract identity."""

    evidence_type: str
    evidence_reference: str
    evidence_sha256: str


@dataclass(frozen=True)
class DatasetLineageManifest:
    """Immutable metadata for one dataset in exactly one instrument lineage."""

    lineage_id: str
    dataset_id: str
    instrument: DatasetInstrument
    contract_id: str
    bar_interval: str
    timestamp_semantics: TimestampSemantics
    timezone_name: str
    dst_policy: str
    rollover_policy: str
    ohlcv_semantics: str
    volume_semantics: str
    session_calendar: str
    holiday_calendar: str
    source_provider: str
    source_software: str
    source_software_version: str
    acquisition_timestamp_utc: str
    source_raw_filename: str
    source_raw_sha256: str
    dataset_filename: str
    dataset_sha256: str
    transformation_command: str
    parent_dataset_sha256: str | None
    role: DatasetRole
    source_exposure: SourceExposure
    oos_access_state: OOSAccessState
    contract_identity_evidence: ContractIdentityEvidence
    oos_boundary_id: str | None = None
    schema_version: str = SCHEMA_VERSION


@dataclass(frozen=True)
class PreparedDatasetLineageManifest:
    """Canonical manifest plus its deterministic SHA-256."""

    manifest: DatasetLineageManifest
    canonical_json: str
    manifest_sha256: str


def prepare_dataset_lineage_manifest(
    value: DatasetLineageManifest,
) -> PreparedDatasetLineageManifest:
    """Validate and canonically hash one manifest without reading its dataset."""
    if not isinstance(value, DatasetLineageManifest):
        raise DatasetLineageError("manifest must be a DatasetLineageManifest")
    if value.schema_version != SCHEMA_VERSION:
        raise DatasetLineageError(f"schema_version must be {SCHEMA_VERSION}")
    if not isinstance(value.instrument, DatasetInstrument):
        raise DatasetLineageError("instrument must be explicitly NQ or MNQ")
    if not isinstance(value.timestamp_semantics, TimestampSemantics):
        raise DatasetLineageError("timestamp_semantics is not an authorized value")
    if not isinstance(value.role, DatasetRole):
        raise DatasetLineageError("role is not an authorized dataset role")
    if not isinstance(value.source_exposure, SourceExposure):
        raise DatasetLineageError("source_exposure is not an authorized value")
    if not isinstance(value.oos_access_state, OOSAccessState):
        raise DatasetLineageError("oos_access_state is not an authorized value")

    evidence = _prepare_evidence(value.contract_identity_evidence)
    manifest = replace(
        value,
        lineage_id=_identifier(value.lineage_id, "lineage_id"),
        dataset_id=_identifier(value.dataset_id, "dataset_id"),
        contract_id=_required_text(value.contract_id, "contract_id"),
        bar_interval=_required_text(value.bar_interval, "bar_interval"),
        timezone_name=_timezone_name(value.timezone_name),
        dst_policy=_required_text(value.dst_policy, "dst_policy"),
        rollover_policy=_required_text(value.rollover_policy, "rollover_policy"),
        ohlcv_semantics=_required_text(value.ohlcv_semantics, "ohlcv_semantics"),
        volume_semantics=_required_text(value.volume_semantics, "volume_semantics"),
        session_calendar=_required_text(value.session_calendar, "session_calendar"),
        holiday_calendar=_required_text(value.holiday_calendar, "holiday_calendar"),
        source_provider=_required_text(value.source_provider, "source_provider"),
        source_software=_required_text(value.source_software, "source_software"),
        source_software_version=_required_text(
            value.source_software_version, "source_software_version"
        ),
        acquisition_timestamp_utc=_utc_timestamp(value.acquisition_timestamp_utc),
        source_raw_filename=_filename(value.source_raw_filename, "source_raw_filename"),
        source_raw_sha256=_sha256(value.source_raw_sha256, "source_raw_sha256"),
        dataset_filename=_filename(value.dataset_filename, "dataset_filename"),
        dataset_sha256=_sha256(value.dataset_sha256, "dataset_sha256"),
        transformation_command=_transformation(value.transformation_command),
        parent_dataset_sha256=(
            _sha256(value.parent_dataset_sha256, "parent_dataset_sha256")
            if value.parent_dataset_sha256 is not None
            else None
        ),
        contract_identity_evidence=evidence,
        oos_boundary_id=(
            _identifier(value.oos_boundary_id, "oos_boundary_id")
            if value.oos_boundary_id is not None
            else None
        ),
    )
    _validate_transformation(manifest)
    _validate_role(manifest)
    canonical = json.dumps(
        dataset_lineage_payload(manifest),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return PreparedDatasetLineageManifest(
        manifest=manifest,
        canonical_json=canonical,
        manifest_sha256=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    )


def verify_dataset_lineage_manifest(
    value: PreparedDatasetLineageManifest,
) -> PreparedDatasetLineageManifest:
    """Rebuild a prepared manifest and reject forged canonical fields or hashes."""
    if not isinstance(value, PreparedDatasetLineageManifest):
        raise DatasetLineageError("prepared manifest has an invalid type")
    rebuilt = prepare_dataset_lineage_manifest(value.manifest)
    if rebuilt != value:
        raise DatasetLineageError("prepared manifest differs from canonical reconstruction")
    return rebuilt


def validate_dataset_lineage_registry(
    manifests: Iterable[PreparedDatasetLineageManifest],
) -> tuple[PreparedDatasetLineageManifest, ...]:
    """Validate parent links, instrument isolation and OOS exposure across manifests."""
    prepared = tuple(verify_dataset_lineage_manifest(item) for item in manifests)
    by_dataset_id: dict[str, PreparedDatasetLineageManifest] = {}
    by_dataset_hash: dict[str, PreparedDatasetLineageManifest] = {}
    raw_instruments: dict[str, DatasetInstrument] = {}
    raw_roles: dict[str, set[DatasetRole]] = {}

    for item in prepared:
        manifest = item.manifest
        if manifest.dataset_id in by_dataset_id:
            raise DatasetLineageError(f"duplicate dataset_id: {manifest.dataset_id}")
        if manifest.dataset_sha256 in by_dataset_hash:
            raise DatasetLineageError(
                f"dataset_sha256 is assigned more than once: {manifest.dataset_sha256}"
            )
        previous_instrument = raw_instruments.setdefault(
            manifest.source_raw_sha256, manifest.instrument
        )
        if previous_instrument != manifest.instrument:
            raise DatasetLineageError("one raw source cannot belong to both NQ and MNQ")
        raw_roles.setdefault(manifest.source_raw_sha256, set()).add(manifest.role)
        by_dataset_id[manifest.dataset_id] = item
        by_dataset_hash[manifest.dataset_sha256] = item

    for source_hash, roles in raw_roles.items():
        if DatasetRole.OOS_TEST in roles and len(roles) > 1:
            raise DatasetLineageError(f"OOS source is shared with a non-OOS role: {source_hash}")

    for item in prepared:
        manifest = item.manifest
        source_owner = by_dataset_hash.get(manifest.source_raw_sha256)
        if source_owner is not None and source_owner is not item:
            owner_manifest = source_owner.manifest
            if owner_manifest.instrument != manifest.instrument:
                raise DatasetLineageError(
                    "a registered dataset cannot become raw source for the other instrument"
                )
            if owner_manifest.lineage_id != manifest.lineage_id:
                raise DatasetLineageError(
                    "a registered dataset cannot silently start a different lineage"
                )
            if manifest.role is DatasetRole.OOS_TEST and (
                owner_manifest.source_exposure is SourceExposure.EXPOSED_DEVELOPMENT
                or owner_manifest.role is not DatasetRole.OOS_TEST
            ):
                raise DatasetLineageError(
                    "an exposed registered dataset cannot become an OOS raw source"
                )
        parent_hash = manifest.parent_dataset_sha256
        if parent_hash is None:
            continue
        parent = by_dataset_hash.get(parent_hash)
        if parent_hash == manifest.source_raw_sha256 and parent is None:
            continue
        if parent is None:
            raise DatasetLineageError(f"unresolved parent_dataset_sha256 for {manifest.dataset_id}")
        parent_manifest = parent.manifest
        if parent_manifest.instrument != manifest.instrument:
            raise DatasetLineageError("parent and child instruments differ")
        if parent_manifest.lineage_id != manifest.lineage_id:
            raise DatasetLineageError("parent and child lineage_id values differ")
        if parent_manifest.source_raw_sha256 != manifest.source_raw_sha256:
            raise DatasetLineageError("parent and child raw sources differ")
        if (
            parent_manifest.role is DatasetRole.OOS_TEST
            and manifest.role is not DatasetRole.OOS_TEST
        ):
            raise DatasetLineageError("an OOS parent cannot feed a non-OOS dataset")

    _reject_cycles(by_dataset_hash)
    return prepared


def dataset_lineage_payload(manifest: DatasetLineageManifest) -> dict[str, object]:
    """Return the public, price-free payload used for deterministic hashing."""
    evidence = manifest.contract_identity_evidence
    return {
        "acquisition_timestamp_utc": manifest.acquisition_timestamp_utc,
        "bar_interval": manifest.bar_interval,
        "contract_id": manifest.contract_id,
        "contract_identity_evidence": {
            "evidence_reference": evidence.evidence_reference,
            "evidence_sha256": evidence.evidence_sha256,
            "evidence_type": evidence.evidence_type,
        },
        "dataset_filename": manifest.dataset_filename,
        "dataset_id": manifest.dataset_id,
        "dataset_sha256": manifest.dataset_sha256,
        "dst_policy": manifest.dst_policy,
        "holiday_calendar": manifest.holiday_calendar,
        "instrument": manifest.instrument.value,
        "lineage_id": manifest.lineage_id,
        "ohlcv_semantics": manifest.ohlcv_semantics,
        "oos_access_state": manifest.oos_access_state.value,
        "oos_boundary_id": manifest.oos_boundary_id,
        "parent_dataset_sha256": manifest.parent_dataset_sha256,
        "role": manifest.role.value,
        "rollover_policy": manifest.rollover_policy,
        "schema_version": manifest.schema_version,
        "session_calendar": manifest.session_calendar,
        "source_exposure": manifest.source_exposure.value,
        "source_provider": manifest.source_provider,
        "source_raw_filename": manifest.source_raw_filename,
        "source_raw_sha256": manifest.source_raw_sha256,
        "source_software": manifest.source_software,
        "source_software_version": manifest.source_software_version,
        "timestamp_semantics": manifest.timestamp_semantics.value,
        "timezone_name": manifest.timezone_name,
        "transformation_command": manifest.transformation_command,
        "volume_semantics": manifest.volume_semantics,
    }


def _prepare_evidence(value: ContractIdentityEvidence) -> ContractIdentityEvidence:
    if not isinstance(value, ContractIdentityEvidence):
        raise DatasetLineageError("contract_identity_evidence must be ContractIdentityEvidence")
    return replace(
        value,
        evidence_type=_identifier(value.evidence_type, "evidence_type"),
        evidence_reference=_identifier(value.evidence_reference, "evidence_reference"),
        evidence_sha256=_sha256(value.evidence_sha256, "evidence_sha256"),
    )


def _identifier(value: object, field: str) -> str:
    text = _required_text(value, field)
    if not _IDENTIFIER_RE.fullmatch(text):
        raise DatasetLineageError(f"{field} has an invalid identifier format")
    return text


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise DatasetLineageError(f"{field} must be text")
    text = value.strip()
    if not text or text.upper() in _UNKNOWN_VALUES:
        raise DatasetLineageError(f"{field} must be explicitly known")
    if len(text) > 2048 or any(ord(character) < 32 for character in text):
        raise DatasetLineageError(f"{field} contains invalid text")
    return text


def _filename(value: object, field: str) -> str:
    text = _required_text(value, field)
    posix = PurePosixPath(text)
    windows = PureWindowsPath(text)
    if (
        posix.is_absolute()
        or windows.is_absolute()
        or windows.drive
        or len(posix.parts) != 1
        or len(windows.parts) != 1
        or text in {".", ".."}
    ):
        raise DatasetLineageError(f"{field} must be a filename without a path")
    return text


def _sha256(value: object, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise DatasetLineageError(f"{field} must be a 64-character SHA-256")
    return value.lower()


def _timezone_name(value: object) -> str:
    name = _required_text(value, "timezone_name")
    try:
        ZoneInfo(name)
    except (ValueError, ZoneInfoNotFoundError) as exc:
        raise DatasetLineageError("timezone_name must be a recognized IANA timezone") from exc
    return name


def _utc_timestamp(value: object) -> str:
    text = _required_text(value, "acquisition_timestamp_utc")
    candidate = f"{text[:-1]}+00:00" if text.endswith("Z") else text
    try:
        timestamp = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise DatasetLineageError("acquisition_timestamp_utc must be ISO-8601") from exc
    if timestamp.tzinfo is None or timestamp.utcoffset() != UTC.utcoffset(timestamp):
        raise DatasetLineageError("acquisition_timestamp_utc must be UTC")
    normalized = timestamp.astimezone(UTC).isoformat()
    return normalized.replace("+00:00", "Z")


def _transformation(value: object) -> str:
    text = _required_text(value, "transformation_command")
    if text.upper() == "NONE":
        return "NONE"
    if re.search(r"(^|[\s=])(?:[A-Za-z]:[\\/]|/|\\\\|~[\\/])", text):
        raise DatasetLineageError(
            "transformation_command must not contain an absolute or home path"
        )
    return text


def _validate_transformation(manifest: DatasetLineageManifest) -> None:
    if manifest.transformation_command == "NONE":
        if manifest.parent_dataset_sha256 is not None:
            raise DatasetLineageError("an untransformed root cannot declare a parent")
        if manifest.dataset_sha256 != manifest.source_raw_sha256:
            raise DatasetLineageError("an untransformed root must preserve the raw SHA-256")
    elif manifest.parent_dataset_sha256 is None:
        raise DatasetLineageError("a transformed dataset must declare parent_dataset_sha256")


def _validate_role(manifest: DatasetLineageManifest) -> None:
    if manifest.role is DatasetRole.OOS_TEST:
        if manifest.source_exposure is not SourceExposure.UNEXPOSED:
            raise DatasetLineageError("OOS_TEST requires an unexposed source")
        if manifest.oos_access_state is not OOSAccessState.SEALED:
            raise DatasetLineageError("OOS_TEST must remain SEALED")
        if manifest.oos_boundary_id is None:
            raise DatasetLineageError("OOS_TEST requires oos_boundary_id")
        return
    if manifest.source_exposure is not SourceExposure.EXPOSED_DEVELOPMENT:
        raise DatasetLineageError("non-OOS roles must be marked EXPOSED_DEVELOPMENT")
    if manifest.oos_access_state is not OOSAccessState.NOT_APPLICABLE:
        raise DatasetLineageError("non-OOS roles require NOT_APPLICABLE OOS access")
    if manifest.oos_boundary_id is not None:
        raise DatasetLineageError("non-OOS roles cannot declare oos_boundary_id")


def _reject_cycles(
    by_dataset_hash: dict[str, PreparedDatasetLineageManifest],
) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(dataset_hash: str) -> None:
        if dataset_hash in visited:
            return
        if dataset_hash in visiting:
            raise DatasetLineageError("dataset lineage contains a parent cycle")
        visiting.add(dataset_hash)
        parent_hash = by_dataset_hash[dataset_hash].manifest.parent_dataset_sha256
        if parent_hash in by_dataset_hash:
            visit(parent_hash)
        visiting.remove(dataset_hash)
        visited.add(dataset_hash)

    for dataset_hash in by_dataset_hash:
        visit(dataset_hash)


__all__ = [
    "SCHEMA_VERSION",
    "ContractIdentityEvidence",
    "DatasetInstrument",
    "DatasetLineageError",
    "DatasetLineageManifest",
    "DatasetRole",
    "OOSAccessState",
    "PreparedDatasetLineageManifest",
    "SourceExposure",
    "TimestampSemantics",
    "dataset_lineage_payload",
    "prepare_dataset_lineage_manifest",
    "validate_dataset_lineage_registry",
    "verify_dataset_lineage_manifest",
]
