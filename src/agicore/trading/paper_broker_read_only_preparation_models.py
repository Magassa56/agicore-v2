"""Models for the AGIcore Paper Broker Read-Only Preparation layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyPreparationState(StrEnum):
    NOT_READY = "NOT_READY"
    PREPARATION_INPUT_INVALID = "PREPARATION_INPUT_INVALID"
    READ_ONLY_PREPARATION_BLOCKED = "READ_ONLY_PREPARATION_BLOCKED"
    READ_ONLY_PREPARATION_COMPLETED_WITH_WARNINGS = "READ_ONLY_PREPARATION_COMPLETED_WITH_WARNINGS"
    READ_ONLY_PREPARATION_COMPLETED = "READ_ONLY_PREPARATION_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW = "READY_FOR_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW"


class PaperBrokerReadOnlyPreparationDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_PREPARATION = "BLOCK_PAPER_BROKER_READ_ONLY_PREPARATION"
    REQUIRE_MULTI_SCENARIO_ROBUSTNESS_FIXES = "REQUIRE_MULTI_SCENARIO_ROBUSTNESS_FIXES"
    REQUIRE_SCOPE_FIXES = "REQUIRE_SCOPE_FIXES"
    REQUIRE_BOUNDARY_FIXES = "REQUIRE_BOUNDARY_FIXES"
    REQUIRE_PERMISSION_POLICY_FIXES = "REQUIRE_PERMISSION_POLICY_FIXES"
    REQUIRE_CREDENTIAL_POLICY_FIXES = "REQUIRE_CREDENTIAL_POLICY_FIXES"
    REQUIRE_NO_ORDER_POLICY_FIXES = "REQUIRE_NO_ORDER_POLICY_FIXES"
    REQUIRE_ACCOUNT_READ_ONLY_FIXES = "REQUIRE_ACCOUNT_READ_ONLY_FIXES"
    REQUIRE_MARKET_DATA_READ_ONLY_FIXES = "REQUIRE_MARKET_DATA_READ_ONLY_FIXES"
    REQUIRE_PAPER_REAL_BOUNDARY_FIXES = "REQUIRE_PAPER_REAL_BOUNDARY_FIXES"
    REQUIRE_HUMAN_APPROVAL_FIXES = "REQUIRE_HUMAN_APPROVAL_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_PREPARATION = "APPROVE_PAPER_BROKER_READ_ONLY_PREPARATION"


class PaperBrokerReadOnlyPreparationRisk(StrEnum):
    MULTI_SCENARIO_ROBUSTNESS_NOT_APPROVED = "MULTI_SCENARIO_ROBUSTNESS_NOT_APPROVED"
    READ_ONLY_SCOPE_UNCLEAR = "READ_ONLY_SCOPE_UNCLEAR"
    BROKER_ENVIRONMENT_BOUNDARY_MISSING = "BROKER_ENVIRONMENT_BOUNDARY_MISSING"
    READ_ONLY_PERMISSION_POLICY_MISSING = "READ_ONLY_PERMISSION_POLICY_MISSING"
    CREDENTIAL_HANDLING_POLICY_MISSING = "CREDENTIAL_HANDLING_POLICY_MISSING"
    HARDCODED_SECRET_RISK = "HARDCODED_SECRET_RISK"
    ORDER_EXECUTION_NOT_BLOCKED = "ORDER_EXECUTION_NOT_BLOCKED"
    POSITION_MUTATION_NOT_BLOCKED = "POSITION_MUTATION_NOT_BLOCKED"
    ACCOUNT_READ_ONLY_POLICY_MISSING = "ACCOUNT_READ_ONLY_POLICY_MISSING"
    MARKET_DATA_READ_ONLY_POLICY_MISSING = "MARKET_DATA_READ_ONLY_POLICY_MISSING"
    MOCK_TO_PAPER_BOUNDARY_UNCLEAR = "MOCK_TO_PAPER_BOUNDARY_UNCLEAR"
    PAPER_REAL_BOUNDARY_UNCLEAR = "PAPER_REAL_BOUNDARY_UNCLEAR"
    OBSERVABILITY_POLICY_MISSING = "OBSERVABILITY_POLICY_MISSING"
    JOURNAL_POLICY_MISSING = "JOURNAL_POLICY_MISSING"
    HUMAN_APPROVAL_POLICY_MISSING = "HUMAN_APPROVAL_POLICY_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW = "PREMATURE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW"


class PaperBrokerReadOnlyPreparationRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_PREPARATION = "HOLD_PAPER_BROKER_READ_ONLY_PREPARATION"
    APPROVE_MULTI_SCENARIO_ROBUSTNESS_FIRST = "APPROVE_MULTI_SCENARIO_ROBUSTNESS_FIRST"
    CLARIFY_READ_ONLY_SCOPE = "CLARIFY_READ_ONLY_SCOPE"
    DEFINE_BROKER_ENVIRONMENT_BOUNDARIES = "DEFINE_BROKER_ENVIRONMENT_BOUNDARIES"
    DEFINE_READ_ONLY_PERMISSION_POLICY = "DEFINE_READ_ONLY_PERMISSION_POLICY"
    DEFINE_CREDENTIALS_HANDLING_POLICY = "DEFINE_CREDENTIALS_HANDLING_POLICY"
    REMOVE_HARDCODED_SECRET = "REMOVE_HARDCODED_SECRET"
    BLOCK_ORDER_EXECUTION = "BLOCK_ORDER_EXECUTION"
    BLOCK_POSITION_MUTATION = "BLOCK_POSITION_MUTATION"
    DEFINE_ACCOUNT_READ_ONLY_POLICY = "DEFINE_ACCOUNT_READ_ONLY_POLICY"
    DEFINE_MARKET_DATA_READ_ONLY_POLICY = "DEFINE_MARKET_DATA_READ_ONLY_POLICY"
    CLARIFY_MOCK_TO_PAPER_BOUNDARY = "CLARIFY_MOCK_TO_PAPER_BOUNDARY"
    CLARIFY_PAPER_REAL_BOUNDARY = "CLARIFY_PAPER_REAL_BOUNDARY"
    DEFINE_OBSERVABILITY_PREPARATION_POLICY = "DEFINE_OBSERVABILITY_PREPARATION_POLICY"
    DEFINE_JOURNAL_PREPARATION_POLICY = "DEFINE_JOURNAL_PREPARATION_POLICY"
    REQUIRE_HUMAN_APPROVAL = "REQUIRE_HUMAN_APPROVAL"
    DEFINE_STOP_CONDITIONS = "DEFINE_STOP_CONDITIONS"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW = "DELAY_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW"
    RUN_PAPER_BROKER_READ_ONLY_PREPARATION_SUITE = "RUN_PAPER_BROKER_READ_ONLY_PREPARATION_SUITE"
    APPROVE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW = "APPROVE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW"


@dataclass(frozen=True)
class ReadOnlyPreparationScope:
    name: str = "read_only_preparation_scope"
    score: int = 0
    defined: bool = False
    preparation_only: bool = True
    allowed_actions: tuple[str, ...] = ()
    prohibited_actions: tuple[str, ...] = ()
    risks: tuple[PaperBrokerReadOnlyPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class BrokerEnvironmentBoundary:
    name: str = "broker_environment_boundaries"
    score: int = 0
    defined: bool = False
    offline_only: bool = True
    sandbox_only: bool = True
    broker_connection_disabled: bool = True
    network_transport_disabled: bool = True
    risks: tuple[PaperBrokerReadOnlyPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReadOnlyPermissionPolicy:
    name: str = "read_only_permission_policy"
    score: int = 0
    defined: bool = False
    read_only_permissions: tuple[str, ...] = ()
    write_permissions_blocked: tuple[str, ...] = ()
    risks: tuple[PaperBrokerReadOnlyPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class CredentialsHandlingPolicy:
    name: str = "credentials_handling_policy"
    score: int = 0
    defined: bool = False
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    no_hardcoded_secrets: bool = True
    secret_source: str = "none_in_this_phase"
    risks: tuple[PaperBrokerReadOnlyPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class NoOrderExecutionPolicy:
    name: str = "no_order_execution_policy"
    score: int = 0
    defined: bool = False
    order_execution_blocked: bool = False
    real_order_blocked: bool = True
    position_mutation_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class AccountReadOnlyPolicy:
    name: str = "account_read_only_policy"
    score: int = 0
    defined: bool = False
    active_account_access_blocked: bool = True
    mutations_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class MarketDataReadOnlyPolicy:
    name: str = "market_data_read_only_policy"
    score: int = 0
    defined: bool = False
    read_only_market_data_planned: bool = True
    live_subscription_disabled: bool = True
    risks: tuple[PaperBrokerReadOnlyPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperVsRealBoundaryPolicy:
    name: str = "paper_vs_real_boundary_policy"
    score: int = 0
    defined: bool = False
    mock_boundary_defined: bool = False
    paper_boundary_defined: bool = False
    real_boundary_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReadOnlyPreparationFinding:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperBrokerReadOnlyPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyPreparationScore:
    overall_score: int
    multi_scenario_robustness_score: int
    scope_score: int
    boundary_score: int
    permission_policy_score: int
    credential_policy_score: int
    no_order_policy_score: int
    no_position_mutation_policy_score: int
    account_read_only_score: int
    market_data_read_only_score: int
    mock_to_paper_boundary_score: int
    paper_vs_real_boundary_score: int
    observability_score: int
    journal_score: int
    human_approval_score: int
    stop_conditions_score: int


@dataclass(frozen=True)
class PaperBrokerReadOnlyPreparationInput:
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
    multi_scenario_robustness_approved: bool | None = None
    read_only_scope_defined: bool | None = None
    broker_environment_boundaries_defined: bool | None = None
    read_only_permission_policy_defined: bool | None = None
    credentials_handling_policy_defined: bool | None = None
    no_hardcoded_secrets: bool | None = None
    no_env_var_read: bool | None = None
    no_order_execution_policy_defined: bool | None = None
    order_execution_blocked: bool | None = None
    no_position_mutation_policy_defined: bool | None = None
    position_mutation_blocked: bool | None = None
    account_read_only_policy_defined: bool | None = None
    account_active_access_blocked: bool | None = None
    market_data_read_only_policy_defined: bool | None = None
    market_data_live_subscription_blocked: bool | None = None
    mock_to_paper_boundary_defined: bool | None = None
    paper_vs_real_boundary_defined: bool | None = None
    observability_preparation_policy_defined: bool | None = None
    journal_preparation_policy_defined: bool | None = None
    human_approval_policy_defined: bool | None = None
    stop_conditions_policy_defined: bool | None = None
    paper_broker_read_only_safety_review_requested: bool | None = False
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    preparation_only: bool | None = None
    broker_connection_disabled: bool | None = None
    no_real_broker: bool | None = None
    no_alpaca_real: bool | None = None
    no_api_key_read: bool | None = None
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
    multi_scenario_robustness_score: int | None = None
    read_only_scope_score: int | None = None
    broker_environment_boundary_score: int | None = None
    read_only_permission_policy_score: int | None = None
    credentials_handling_policy_score: int | None = None
    no_order_execution_policy_score: int | None = None
    no_position_mutation_policy_score: int | None = None
    account_read_only_policy_score: int | None = None
    market_data_read_only_policy_score: int | None = None
    mock_to_paper_boundary_score: int | None = None
    paper_vs_real_boundary_score: int | None = None
    observability_preparation_policy_score: int | None = None
    journal_preparation_policy_score: int | None = None
    human_approval_policy_score: int | None = None
    stop_conditions_policy_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyPreparationResult:
    state: PaperBrokerReadOnlyPreparationState
    decision: PaperBrokerReadOnlyPreparationDecision
    preparation_score: int
    score_breakdown: PaperBrokerReadOnlyPreparationScore
    risks: tuple[PaperBrokerReadOnlyPreparationRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyPreparationRecommendation, ...] = ()
    scope: ReadOnlyPreparationScope = field(default_factory=ReadOnlyPreparationScope)
    broker_environment_boundaries: BrokerEnvironmentBoundary = field(default_factory=BrokerEnvironmentBoundary)
    read_only_permission_policy: ReadOnlyPermissionPolicy = field(default_factory=ReadOnlyPermissionPolicy)
    credentials_handling_policy: CredentialsHandlingPolicy = field(default_factory=CredentialsHandlingPolicy)
    no_order_execution_policy: NoOrderExecutionPolicy = field(default_factory=NoOrderExecutionPolicy)
    no_position_mutation_policy: NoOrderExecutionPolicy = field(
        default_factory=lambda: NoOrderExecutionPolicy(name="no_position_mutation_policy")
    )
    account_read_only_policy: AccountReadOnlyPolicy = field(default_factory=AccountReadOnlyPolicy)
    market_data_read_only_policy: MarketDataReadOnlyPolicy = field(default_factory=MarketDataReadOnlyPolicy)
    mock_to_paper_boundary_policy: PaperVsRealBoundaryPolicy = field(
        default_factory=lambda: PaperVsRealBoundaryPolicy(name="mock_to_paper_boundary_policy")
    )
    paper_vs_real_boundary_policy: PaperVsRealBoundaryPolicy = field(default_factory=PaperVsRealBoundaryPolicy)
    observability_preparation_policy: ReadOnlyPreparationFinding = field(
        default_factory=lambda: ReadOnlyPreparationFinding("observability_preparation_policy", 0, False)
    )
    journal_preparation_policy: ReadOnlyPreparationFinding = field(
        default_factory=lambda: ReadOnlyPreparationFinding("journal_preparation_policy", 0, False)
    )
    human_approval_policy: ReadOnlyPreparationFinding = field(
        default_factory=lambda: ReadOnlyPreparationFinding("human_approval_policy", 0, False)
    )
    stop_conditions_policy: ReadOnlyPreparationFinding = field(
        default_factory=lambda: ReadOnlyPreparationFinding("stop_conditions_policy", 0, False)
    )
    findings: tuple[ReadOnlyPreparationFinding, ...] = ()
    offline_only: bool = True
    summary: str = ""
