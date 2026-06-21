"""Models for the AGIcore Paper Broker Read-Only Safety Review layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlySafetyReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    SAFETY_REVIEW_INPUT_INVALID = "SAFETY_REVIEW_INPUT_INVALID"
    SAFETY_REVIEW_BLOCKED = "SAFETY_REVIEW_BLOCKED"
    SAFETY_REVIEW_COMPLETED_WITH_WARNINGS = "SAFETY_REVIEW_COMPLETED_WITH_WARNINGS"
    SAFETY_REVIEW_COMPLETED = "SAFETY_REVIEW_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN = "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN"


class PaperBrokerReadOnlySafetyReviewDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW = "BLOCK_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW"
    REQUIRE_READ_ONLY_PREPARATION_FIXES = "REQUIRE_READ_ONLY_PREPARATION_FIXES"
    REQUIRE_SCOPE_FIXES = "REQUIRE_SCOPE_FIXES"
    REQUIRE_BOUNDARY_FIXES = "REQUIRE_BOUNDARY_FIXES"
    REQUIRE_PERMISSION_POLICY_FIXES = "REQUIRE_PERMISSION_POLICY_FIXES"
    REQUIRE_CREDENTIAL_POLICY_FIXES = "REQUIRE_CREDENTIAL_POLICY_FIXES"
    REQUIRE_NO_ORDER_POLICY_FIXES = "REQUIRE_NO_ORDER_POLICY_FIXES"
    REQUIRE_POSITION_MUTATION_FIXES = "REQUIRE_POSITION_MUTATION_FIXES"
    REQUIRE_ACCOUNT_READ_ONLY_FIXES = "REQUIRE_ACCOUNT_READ_ONLY_FIXES"
    REQUIRE_MARKET_DATA_READ_ONLY_FIXES = "REQUIRE_MARKET_DATA_READ_ONLY_FIXES"
    REQUIRE_MOCK_PAPER_BOUNDARY_FIXES = "REQUIRE_MOCK_PAPER_BOUNDARY_FIXES"
    REQUIRE_PAPER_REAL_BOUNDARY_FIXES = "REQUIRE_PAPER_REAL_BOUNDARY_FIXES"
    REQUIRE_HUMAN_APPROVAL_FIXES = "REQUIRE_HUMAN_APPROVAL_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW = "APPROVE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW"


class PaperBrokerReadOnlySafetyReviewRisk(StrEnum):
    READ_ONLY_PREPARATION_NOT_APPROVED = "READ_ONLY_PREPARATION_NOT_APPROVED"
    READ_ONLY_SCOPE_UNCLEAR = "READ_ONLY_SCOPE_UNCLEAR"
    BROKER_ENVIRONMENT_BOUNDARY_UNSAFE = "BROKER_ENVIRONMENT_BOUNDARY_UNSAFE"
    READ_ONLY_PERMISSION_POLICY_UNSAFE = "READ_ONLY_PERMISSION_POLICY_UNSAFE"
    CREDENTIAL_HANDLING_UNSAFE = "CREDENTIAL_HANDLING_UNSAFE"
    HARDCODED_SECRET_RISK = "HARDCODED_SECRET_RISK"
    ENVIRONMENT_VARIABLE_READ_RISK = "ENVIRONMENT_VARIABLE_READ_RISK"
    ORDER_EXECUTION_NOT_BLOCKED = "ORDER_EXECUTION_NOT_BLOCKED"
    POSITION_MUTATION_NOT_BLOCKED = "POSITION_MUTATION_NOT_BLOCKED"
    ACCOUNT_READ_ONLY_POLICY_UNSAFE = "ACCOUNT_READ_ONLY_POLICY_UNSAFE"
    MARKET_DATA_READ_ONLY_POLICY_UNSAFE = "MARKET_DATA_READ_ONLY_POLICY_UNSAFE"
    MOCK_TO_PAPER_BOUNDARY_UNSAFE = "MOCK_TO_PAPER_BOUNDARY_UNSAFE"
    PAPER_REAL_BOUNDARY_UNSAFE = "PAPER_REAL_BOUNDARY_UNSAFE"
    OBSERVABILITY_POLICY_INCOMPLETE = "OBSERVABILITY_POLICY_INCOMPLETE"
    JOURNAL_POLICY_INCOMPLETE = "JOURNAL_POLICY_INCOMPLETE"
    HUMAN_APPROVAL_POLICY_INCOMPLETE = "HUMAN_APPROVAL_POLICY_INCOMPLETE"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN = "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN"


class PaperBrokerReadOnlySafetyReviewRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN"
    APPROVE_READ_ONLY_PREPARATION_FIRST = "APPROVE_READ_ONLY_PREPARATION_FIRST"
    CLARIFY_READ_ONLY_SCOPE = "CLARIFY_READ_ONLY_SCOPE"
    HARDEN_BROKER_ENVIRONMENT_BOUNDARIES = "HARDEN_BROKER_ENVIRONMENT_BOUNDARIES"
    HARDEN_READ_ONLY_PERMISSION_POLICY = "HARDEN_READ_ONLY_PERMISSION_POLICY"
    HARDEN_CREDENTIAL_HANDLING = "HARDEN_CREDENTIAL_HANDLING"
    REMOVE_HARDCODED_SECRET = "REMOVE_HARDCODED_SECRET"
    BLOCK_ENVIRONMENT_VARIABLE_READ = "BLOCK_ENVIRONMENT_VARIABLE_READ"
    BLOCK_ORDER_EXECUTION = "BLOCK_ORDER_EXECUTION"
    BLOCK_POSITION_MUTATION = "BLOCK_POSITION_MUTATION"
    HARDEN_ACCOUNT_READ_ONLY_POLICY = "HARDEN_ACCOUNT_READ_ONLY_POLICY"
    HARDEN_MARKET_DATA_READ_ONLY_POLICY = "HARDEN_MARKET_DATA_READ_ONLY_POLICY"
    CLARIFY_MOCK_TO_PAPER_BOUNDARY = "CLARIFY_MOCK_TO_PAPER_BOUNDARY"
    CLARIFY_PAPER_REAL_BOUNDARY = "CLARIFY_PAPER_REAL_BOUNDARY"
    COMPLETE_OBSERVABILITY_POLICY = "COMPLETE_OBSERVABILITY_POLICY"
    COMPLETE_JOURNAL_POLICY = "COMPLETE_JOURNAL_POLICY"
    REQUIRE_HUMAN_APPROVAL = "REQUIRE_HUMAN_APPROVAL"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN = "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN"
    RUN_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW_SUITE = "RUN_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW_SUITE"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN"


@dataclass(frozen=True)
class ReadOnlySafetyFinding:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperBrokerReadOnlySafetyReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class CredentialSafetyReview:
    score: int = 0
    passed: bool = False
    no_api_key_read: bool = False
    no_env_var_read: bool = False
    no_hardcoded_secret: bool = False
    secret_source: str = "none_in_this_phase"
    risks: tuple[PaperBrokerReadOnlySafetyReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class BrokerBoundarySafetyReview:
    score: int = 0
    passed: bool = False
    offline_only: bool = False
    sandbox_only: bool = False
    broker_connection_disabled: bool = False
    network_transport_disabled: bool = False
    risks: tuple[PaperBrokerReadOnlySafetyReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrderBlockingSafetyReview:
    score: int = 0
    passed: bool = False
    order_execution_blocked: bool = False
    real_order_blocked: bool = False
    order_request_absent: bool = True
    risks: tuple[PaperBrokerReadOnlySafetyReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PositionMutationSafetyReview:
    score: int = 0
    passed: bool = False
    position_mutation_blocked: bool = False
    mutation_request_absent: bool = True
    risks: tuple[PaperBrokerReadOnlySafetyReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class AccountReadOnlySafetyReview:
    score: int = 0
    passed: bool = False
    account_read_only: bool = False
    active_account_access_blocked: bool = False
    mutations_blocked: bool = False
    risks: tuple[PaperBrokerReadOnlySafetyReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class MarketDataReadOnlySafetyReview:
    score: int = 0
    passed: bool = False
    market_data_read_only: bool = False
    live_subscription_disabled: bool = False
    network_request_absent: bool = True
    risks: tuple[PaperBrokerReadOnlySafetyReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlySafetyReviewScore:
    overall_score: int
    preparation_approval_score: int
    scope_score: int
    boundary_score: int
    permission_policy_score: int
    credential_policy_score: int
    order_blocking_score: int
    position_mutation_score: int
    account_read_only_score: int
    market_data_read_only_score: int
    mock_to_paper_boundary_score: int
    paper_vs_real_boundary_score: int
    observability_score: int
    journal_score: int
    human_approval_score: int
    stop_conditions_score: int


@dataclass(frozen=True)
class PaperBrokerReadOnlySafetyReviewInput:
    paper_broker_read_only_preparation: Any = None
    multi_scenario_result_report: Any = None
    multi_scenario_controlled_simulation_result: Any = None
    performance_risk_validation_gate: Any = None
    performance_metrics_result: Any = None
    risk_metrics_result: Any = None
    controlled_simulation_result_report: Any = None
    controlled_simulation_offline_runner_result: Any = None
    paper_runtime_forward_test_plan: Any = None
    official_paper_validation_report: Any = None
    paper_runtime_validation: Any = None
    paper_trading_runtime: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    read_only_preparation_approved: bool | None = None
    read_only_scope_reviewed: bool | None = None
    broker_environment_boundaries_reviewed: bool | None = None
    read_only_permission_policy_reviewed: bool | None = None
    credentials_handling_policy_reviewed: bool | None = None
    no_hardcoded_secrets: bool | None = None
    no_env_var_read: bool | None = None
    no_api_key_read: bool | None = None
    no_order_execution_policy_reviewed: bool | None = None
    order_execution_blocked: bool | None = None
    no_position_mutation_policy_reviewed: bool | None = None
    position_mutation_blocked: bool | None = None
    account_read_only_policy_reviewed: bool | None = None
    account_active_access_blocked: bool | None = None
    account_mutations_blocked: bool | None = None
    market_data_read_only_policy_reviewed: bool | None = None
    market_data_live_subscription_blocked: bool | None = None
    mock_to_paper_boundary_reviewed: bool | None = None
    paper_vs_real_boundary_reviewed: bool | None = None
    observability_policy_reviewed: bool | None = None
    journal_policy_reviewed: bool | None = None
    human_approval_policy_reviewed: bool | None = None
    stop_conditions_policy_reviewed: bool | None = None
    paper_broker_read_only_connection_plan_requested: bool | None = False
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    safety_review_only: bool | None = None
    broker_connection_disabled: bool | None = None
    no_real_broker: bool | None = None
    no_alpaca_real: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_external_ml: bool | None = None
    no_external_llm: bool | None = None
    no_live_execution: bool | None = None
    no_real_order: bool | None = None
    no_position_mutation: bool | None = None
    no_real_account_access: bool | None = None
    data_access_requested: bool | None = False
    real_execution_requested: bool | None = False
    broker_connection_requested: bool | None = False
    api_key_read_requested: bool | None = False
    env_var_read_requested: bool | None = False
    hardcoded_secret_detected: bool | None = False
    order_execution_requested: bool | None = False
    position_mutation_requested: bool | None = False
    account_access_requested: bool | None = False
    network_transport_requested: bool | None = False
    preparation_approval_score: int | None = None
    scope_score: int | None = None
    boundary_score: int | None = None
    permission_policy_score: int | None = None
    credential_policy_score: int | None = None
    order_blocking_score: int | None = None
    position_mutation_score: int | None = None
    account_read_only_score: int | None = None
    market_data_read_only_score: int | None = None
    mock_to_paper_boundary_score: int | None = None
    paper_vs_real_boundary_score: int | None = None
    observability_score: int | None = None
    journal_score: int | None = None
    human_approval_score: int | None = None
    stop_conditions_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlySafetyReviewResult:
    state: PaperBrokerReadOnlySafetyReviewState
    decision: PaperBrokerReadOnlySafetyReviewDecision
    safety_score: int
    score_breakdown: PaperBrokerReadOnlySafetyReviewScore
    risks: tuple[PaperBrokerReadOnlySafetyReviewRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlySafetyReviewRecommendation, ...] = ()
    read_only_scope_review: ReadOnlySafetyFinding = field(
        default_factory=lambda: ReadOnlySafetyFinding("read_only_scope", 0, False)
    )
    broker_environment_boundary_review: BrokerBoundarySafetyReview = field(default_factory=BrokerBoundarySafetyReview)
    read_only_permission_policy_review: ReadOnlySafetyFinding = field(
        default_factory=lambda: ReadOnlySafetyFinding("read_only_permission_policy", 0, False)
    )
    credentials_handling_review: CredentialSafetyReview = field(default_factory=CredentialSafetyReview)
    order_blocking_review: OrderBlockingSafetyReview = field(default_factory=OrderBlockingSafetyReview)
    position_mutation_review: PositionMutationSafetyReview = field(default_factory=PositionMutationSafetyReview)
    account_read_only_review: AccountReadOnlySafetyReview = field(default_factory=AccountReadOnlySafetyReview)
    market_data_read_only_review: MarketDataReadOnlySafetyReview = field(default_factory=MarketDataReadOnlySafetyReview)
    mock_to_paper_boundary_review: ReadOnlySafetyFinding = field(
        default_factory=lambda: ReadOnlySafetyFinding("mock_to_paper_boundary", 0, False)
    )
    paper_vs_real_boundary_review: ReadOnlySafetyFinding = field(
        default_factory=lambda: ReadOnlySafetyFinding("paper_vs_real_boundary", 0, False)
    )
    observability_review: ReadOnlySafetyFinding = field(
        default_factory=lambda: ReadOnlySafetyFinding("observability_policy", 0, False)
    )
    journal_review: ReadOnlySafetyFinding = field(
        default_factory=lambda: ReadOnlySafetyFinding("journal_policy", 0, False)
    )
    human_approval_review: ReadOnlySafetyFinding = field(
        default_factory=lambda: ReadOnlySafetyFinding("human_approval_policy", 0, False)
    )
    stop_conditions_review: ReadOnlySafetyFinding = field(
        default_factory=lambda: ReadOnlySafetyFinding("stop_conditions_policy", 0, False)
    )
    findings: tuple[ReadOnlySafetyFinding, ...] = ()
    offline_only: bool = True
    summary: str = ""
