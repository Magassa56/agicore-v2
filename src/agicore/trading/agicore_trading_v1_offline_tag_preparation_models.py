"""Models for AGIcore Trading v1 offline tag preparation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AGIcoreTradingV1OfflineTagPreparationState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION_INPUT_INVALID = "AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION_INPUT_INVALID"
    AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION_BLOCKED = "AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION_BLOCKED"
    AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION_COMPLETED = "AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION_COMPLETED"
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW = "READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW"


class AGIcoreTradingV1OfflineTagPreparationDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION = "BLOCK_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION"
    REQUIRE_TAG_PREPARATION_INPUT_FIXES = "REQUIRE_TAG_PREPARATION_INPUT_FIXES"
    REQUIRE_TAG_PREPARATION_ARTIFACT_FIXES = "REQUIRE_TAG_PREPARATION_ARTIFACT_FIXES"
    REQUIRE_TAG_PREPARATION_DOCUMENTATION_FIXES = "REQUIRE_TAG_PREPARATION_DOCUMENTATION_FIXES"
    REQUIRE_TAG_PREPARATION_READY_STATE_FIXES = "REQUIRE_TAG_PREPARATION_READY_STATE_FIXES"
    REQUIRE_TAG_PREPARATION_TEST_EVIDENCE_FIXES = "REQUIRE_TAG_PREPARATION_TEST_EVIDENCE_FIXES"
    REQUIRE_TAG_PREPARATION_VERSION_FIXES = "REQUIRE_TAG_PREPARATION_VERSION_FIXES"
    REQUIRE_TAG_PREPARATION_TAG_INFO_FIXES = "REQUIRE_TAG_PREPARATION_TAG_INFO_FIXES"
    REQUIRE_TAG_PREPARATION_BOUNDARY_FIXES = "REQUIRE_TAG_PREPARATION_BOUNDARY_FIXES"
    APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION = "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION"


class AGIcoreTradingV1OfflineTagPreparationRisk(StrEnum):
    TAG_PREPARATION_INPUT_MISSING = "TAG_PREPARATION_INPUT_MISSING"
    TAG_PREPARATION_ARTIFACTS_INCOMPLETE = "TAG_PREPARATION_ARTIFACTS_INCOMPLETE"
    TAG_PREPARATION_DOCUMENTATION_INCOHERENT = "TAG_PREPARATION_DOCUMENTATION_INCOHERENT"
    TAG_PREPARATION_READY_STATES_INCOHERENT = "TAG_PREPARATION_READY_STATES_INCOHERENT"
    TAG_PREPARATION_TEST_EVIDENCE_MISSING = "TAG_PREPARATION_TEST_EVIDENCE_MISSING"
    TAG_PREPARATION_VERSION_METADATA_MISSING = "TAG_PREPARATION_VERSION_METADATA_MISSING"
    TAG_PREPARATION_VERSION_NUMBER_INVALID = "TAG_PREPARATION_VERSION_NUMBER_INVALID"
    TAG_PREPARATION_TAG_INFORMATION_MISSING = "TAG_PREPARATION_TAG_INFORMATION_MISSING"
    FILE_READ_BOUNDARY_VIOLATION = "FILE_READ_BOUNDARY_VIOLATION"
    REAL_DATA_ACCESS_BOUNDARY_VIOLATION = "REAL_DATA_ACCESS_BOUNDARY_VIOLATION"
    DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION = "DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION"
    REAL_BROKER_BOUNDARY_VIOLATION = "REAL_BROKER_BOUNDARY_VIOLATION"
    REAL_SECRET_BOUNDARY_VIOLATION = "REAL_SECRET_BOUNDARY_VIOLATION"
    NETWORK_BOUNDARY_VIOLATION = "NETWORK_BOUNDARY_VIOLATION"
    ORDER_EXECUTION_BOUNDARY_VIOLATION = "ORDER_EXECUTION_BOUNDARY_VIOLATION"
    ACCOUNT_ACCESS_BOUNDARY_VIOLATION = "ACCOUNT_ACCESS_BOUNDARY_VIOLATION"
    POSITION_MUTATION_BOUNDARY_VIOLATION = "POSITION_MUTATION_BOUNDARY_VIOLATION"


class AGIcoreTradingV1OfflineTagPreparationRecommendation(StrEnum):
    PROVIDE_TAG_PREPARATION_INPUT = "PROVIDE_TAG_PREPARATION_INPUT"
    RESTORE_TAG_PREPARATION_ARTIFACTS = "RESTORE_TAG_PREPARATION_ARTIFACTS"
    RESTORE_TAG_PREPARATION_DOCUMENTATION = "RESTORE_TAG_PREPARATION_DOCUMENTATION"
    RESTORE_TAG_PREPARATION_READY_STATES = "RESTORE_TAG_PREPARATION_READY_STATES"
    RESTORE_TAG_PREPARATION_TEST_EVIDENCE = "RESTORE_TAG_PREPARATION_TEST_EVIDENCE"
    RESTORE_TAG_PREPARATION_VERSION_METADATA = "RESTORE_TAG_PREPARATION_VERSION_METADATA"
    RESTORE_TAG_PREPARATION_VERSION_NUMBER = "RESTORE_TAG_PREPARATION_VERSION_NUMBER"
    RESTORE_TAG_PREPARATION_TAG_INFORMATION = "RESTORE_TAG_PREPARATION_TAG_INFORMATION"
    REMOVE_FILE_READ = "REMOVE_FILE_READ"
    REMOVE_REAL_DATA_ACCESS = "REMOVE_REAL_DATA_ACCESS"
    REMOVE_DATA_DIRECTORY_ACCESS = "REMOVE_DATA_DIRECTORY_ACCESS"
    REMOVE_REAL_BROKER_ACCESS = "REMOVE_REAL_BROKER_ACCESS"
    REMOVE_REAL_SECRET_ACCESS = "REMOVE_REAL_SECRET_ACCESS"
    REMOVE_NETWORK_ACCESS = "REMOVE_NETWORK_ACCESS"
    REMOVE_ORDER_EXECUTION = "REMOVE_ORDER_EXECUTION"
    REMOVE_ACCOUNT_ACCESS = "REMOVE_ACCOUNT_ACCESS"
    REMOVE_POSITION_MUTATION = "REMOVE_POSITION_MUTATION"
    PREPARE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW = "PREPARE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW"


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagPreparationScore:
    overall_score: int
    input_score: int
    artifact_score: int
    documentation_score: int
    ready_state_score: int
    test_evidence_score: int
    version_metadata_score: int
    version_number_score: int
    tag_information_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagPreparationArtifact:
    path: str
    expected: bool = True
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagPreparationTestingEvidence:
    command: str
    result: str
    validated: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagPreparationReadyState:
    source: str
    state: str
    coherent: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagPreparationVersionMetadata:
    product: str
    release_name: str
    release_scope: str
    safety_profile: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagPreparationTagInformation:
    tag_name: str
    version_number: str
    target_branch: str
    tag_message: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagPreparationReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagPreparationInput:
    preparation_id: str = "agicore-trading-v1-offline-tag-preparation"
    force_artifacts_incomplete: bool = False
    force_documentation_incoherent: bool = False
    force_ready_states_incoherent: bool = False
    force_test_evidence_missing: bool = False
    force_version_metadata_missing: bool = False
    force_version_number_invalid: bool = False
    force_tag_information_missing: bool = False
    file_read_requested: bool = False
    real_data_access_requested: bool = False
    data_directory_access_requested: bool = False
    broker_connection_requested: bool = False
    secret_read_requested: bool = False
    network_requested: bool = False
    http_requested: bool = False
    websocket_requested: bool = False
    socket_requested: bool = False
    external_api_requested: bool = False
    order_execution_requested: bool = False
    account_access_requested: bool = False
    position_mutation_requested: bool = False


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagPreparationResult:
    state: AGIcoreTradingV1OfflineTagPreparationState
    decision: AGIcoreTradingV1OfflineTagPreparationDecision
    score: AGIcoreTradingV1OfflineTagPreparationScore
    risks: tuple[AGIcoreTradingV1OfflineTagPreparationRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineTagPreparationRecommendation, ...]
    artifacts: tuple[AGIcoreTradingV1OfflineTagPreparationArtifact, ...] = ()
    testing_evidence: tuple[AGIcoreTradingV1OfflineTagPreparationTestingEvidence, ...] = ()
    ready_states: tuple[AGIcoreTradingV1OfflineTagPreparationReadyState, ...] = ()
    version_metadata: AGIcoreTradingV1OfflineTagPreparationVersionMetadata | None = None
    tag_information: AGIcoreTradingV1OfflineTagPreparationTagInformation | None = None
    report: AGIcoreTradingV1OfflineTagPreparationReport | None = None
    file_read: bool = False
    data_accessed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW"
