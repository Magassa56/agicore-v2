"""Offline preparation for read-only broker dry-run controlled execution."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_execution_preparation_models import (
    ControlledAbortContract,
    ControlledAccountReadOnlyContract,
    ControlledAuditContract,
    ControlledCredentialsReferenceContract,
    ControlledExecutionPreconditionContract,
    ControlledExecutionRuntimeContract,
    ControlledExecutionSequenceContract,
    ControlledGoNoGoContract,
    ControlledHumanApprovalContract,
    ControlledJournalContract,
    ControlledMarketDataReadOnlyContract,
    ControlledNetworkBlockGuard,
    ControlledNoSecretReadGuard,
    ControlledObservabilityContract,
    ControlledOrderBlockingContract,
    ControlledPositionMutationBlockContract,
    ControlledStopConditionContract,
    ControlledSuccessFailureContract,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationInput,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRecommendation,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationResult,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationScore,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationState,
)

Risk = PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk
Decision = PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision
Recommendation = PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRecommendation


def _coerce_input(data):
    if data is None:
        return PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationInput()
    if isinstance(data, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationInput)}
    return PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationInput(
        **{key: value for key, value in dict(data).items() if key in allowed}
    )


def _value(item: Any) -> str:
    if item is None:
        return ""
    if isinstance(item, Enum):
        return str(item.value)
    return str(item)


def _get(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    result: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def _clamp(value: int | float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def _average(values: Iterable[int | float | None], default: int = 0) -> int:
    usable = [float(value) for value in values if value is not None]
    return _clamp(sum(usable) / len(usable)) if usable else default


def _metric_score(explicit: int | None, fallback: Any, passed: bool) -> int:
    if explicit is not None:
        return _clamp(explicit)
    if fallback is not None:
        return _clamp(fallback)
    return 100 if passed else 0


def _state_contains(obj: Any, *needles: str) -> bool:
    state = _value(_get(obj, "state")).upper()
    decision = _value(_get(obj, "decision")).upper()
    return any(needle.upper() in state or needle.upper() in decision for needle in needles)


def _gate(data):
    return data.paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate


def _prepared(data, name: str) -> bool:
    return _get(data, f"controlled_{name}") is True or _get(data, f"controlled_execution_{name}") is True


def _secret_boundary(data) -> bool:
    return (
        data.no_api_key_read is True
        and data.no_env_var_read is True
        and data.no_hardcoded_secrets is True
        and data.api_key_read_requested is not True
        and data.env_var_read_requested is not True
        and data.hardcoded_secret_detected is not True
    )


def _offline_boundary(data) -> bool:
    expected_true = (
        data.offline_mode_enforced,
        data.sandbox_mode_enforced,
        data.preparation_only,
        data.broker_connection_disabled,
        data.no_real_broker,
        data.no_alpaca_real,
        data.no_api_key_read,
        data.no_env_var_read,
        data.no_hardcoded_secrets,
        data.no_http_transport,
        data.no_websocket_transport,
        data.no_socket_transport,
        data.no_external_api,
        data.no_external_ml,
        data.no_external_llm,
        data.no_live_execution,
        data.no_real_order,
        data.no_position_mutation,
        data.no_real_account_access,
    )
    requested = (
        data.real_execution_requested,
        data.broker_connection_requested,
        data.api_key_read_requested,
        data.env_var_read_requested,
        data.hardcoded_secret_detected,
        data.order_execution_requested,
        data.position_mutation_requested,
        data.account_access_requested,
        data.network_transport_requested,
        data.external_api_requested,
        data.dry_run_requested,
        data.dry_run_executed,
    )
    return all(item is True for item in expected_true) and not any(item is True for item in requested)


def validate_controlled_execution_safety_gate_approval(data):
    data = _coerce_input(data)
    gate = _gate(data)
    if gate is None or data.controlled_execution_safety_gate_approved is False:
        return False
    return data.controlled_execution_safety_gate_approved is True or _state_contains(
        gate,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE",
    )


def _contract(cls, data, score_attr: str, passed: bool, risk: Risk, **kwargs):
    return cls(
        score=_metric_score(_get(data, score_attr), None, passed),
        defined=passed,
        risks=() if passed else (risk,),
        **kwargs,
    )


def prepare_controlled_execution_runtime_contract(data):
    data = _coerce_input(data)
    passed = _prepared(data, "runtime_contract_prepared") and data.preparation_only is True and data.dry_run_executed is not True
    return _contract(
        ControlledExecutionRuntimeContract,
        data,
        "runtime_contract_score",
        passed,
        Risk.CONTROLLED_RUNTIME_CONTRACT_MISSING,
        preparation_only=data.preparation_only is True,
        dry_run_execution_disabled=data.dry_run_requested is not True and data.dry_run_executed is not True,
        allowed_actions=("offline_contract_preparation", "safety_metadata_review"),
        prohibited_actions=("dry_run_execution", "broker_connection", "api_key_read", "env_var_read", "http_request", "websocket_request", "socket_open", "order_execution", "position_mutation", "active_account_access"),
    )


def prepare_controlled_execution_sequence_contract(data):
    data = _coerce_input(data)
    passed = _prepared(data, "sequence_contract_prepared") and data.broker_connection_disabled is True and data.network_transport_requested is not True and data.dry_run_executed is not True
    return _contract(
        ControlledExecutionSequenceContract,
        data,
        "sequence_contract_score",
        passed,
        Risk.CONTROLLED_SEQUENCE_CONTRACT_MISSING,
        dry_run_not_executed=data.dry_run_executed is not True,
        connection_not_executed=data.broker_connection_requested is not True,
        sequence_steps_defined=_prepared(data, "sequence_contract_prepared"),
        network_transport_blocked=data.network_transport_requested is not True,
    )


def prepare_controlled_execution_precondition_contract(data):
    data = _coerce_input(data)
    passed = _prepared(data, "precondition_contract_prepared") and validate_controlled_execution_safety_gate_approval(data)
    return _contract(
        ControlledExecutionPreconditionContract,
        data,
        "precondition_contract_score",
        passed,
        Risk.CONTROLLED_PRECONDITION_CONTRACT_MISSING,
        safety_gate_required=validate_controlled_execution_safety_gate_approval(data),
        human_approval_required=data.controlled_human_approval_required is True,
        stop_conditions_required=_prepared(data, "stop_conditions_contract_prepared"),
    )


def prepare_controlled_credentials_reference_contract(data):
    data = _coerce_input(data)
    passed = _prepared(data, "credentials_reference_contract_prepared") and data.controlled_credentials_reference_only is True and _secret_boundary(data)
    return _contract(
        ControlledCredentialsReferenceContract,
        data,
        "credentials_reference_score",
        passed,
        Risk.CONTROLLED_CREDENTIAL_REFERENCE_UNSAFE,
        reference_only=data.controlled_credentials_reference_only is True,
        no_secret_values=data.no_hardcoded_secrets is True,
        no_api_key_read=data.no_api_key_read is True,
        no_env_var_read=data.no_env_var_read is True,
    )


def prepare_controlled_no_secret_read_guard(data):
    data = _coerce_input(data)
    passed = _prepared(data, "no_secret_read_guard_prepared") and data.controlled_secret_read_guard_enforced is True and _secret_boundary(data)
    return _contract(
        ControlledNoSecretReadGuard,
        data,
        "no_secret_read_guard_score",
        passed,
        Risk.CONTROLLED_SECRET_READ_GUARD_MISSING,
        guard_enforced=data.controlled_secret_read_guard_enforced is True,
        no_api_key_read=data.no_api_key_read is True,
        no_env_var_read=data.no_env_var_read is True,
        no_hardcoded_secret=data.no_hardcoded_secrets is True,
    )


def prepare_controlled_network_block_guard(data):
    data = _coerce_input(data)
    passed = _prepared(data, "network_block_guard_prepared") and data.controlled_network_blocked is True and data.controlled_external_api_blocked is True and _offline_boundary(data)
    return _contract(
        ControlledNetworkBlockGuard,
        data,
        "network_block_guard_score",
        passed,
        Risk.CONTROLLED_NETWORK_BLOCK_GUARD_MISSING,
        network_execution_blocked=data.controlled_network_blocked is True,
        http_blocked=data.controlled_http_transport_blocked is True,
        websocket_blocked=data.controlled_websocket_transport_blocked is True,
        socket_blocked=data.controlled_socket_transport_blocked is True,
        external_api_blocked=data.controlled_external_api_blocked is True,
    )


def prepare_controlled_http_websocket_socket_block_guard(data):
    data = _coerce_input(data)
    passed = (
        _prepared(data, "http_websocket_socket_block_guard_prepared")
        and data.controlled_http_transport_blocked is True
        and data.controlled_websocket_transport_blocked is True
        and data.controlled_socket_transport_blocked is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
    )
    return _contract(
        ControlledNetworkBlockGuard,
        data,
        "http_websocket_socket_block_guard_score",
        passed,
        Risk.CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING,
        name="controlled_http_websocket_socket_block_guard",
        network_execution_blocked=data.controlled_network_blocked is True,
        http_blocked=data.controlled_http_transport_blocked is True and data.no_http_transport is True,
        websocket_blocked=data.controlled_websocket_transport_blocked is True and data.no_websocket_transport is True,
        socket_blocked=data.controlled_socket_transport_blocked is True and data.no_socket_transport is True,
        external_api_blocked=data.controlled_external_api_blocked is True,
    )


def prepare_controlled_account_read_only_contract(data):
    data = _coerce_input(data)
    passed = _prepared(data, "account_read_only_contract_prepared") and data.controlled_account_active_access_blocked is True and data.controlled_account_mutations_blocked is True and data.account_access_requested is not True
    return _contract(ControlledAccountReadOnlyContract, data, "account_read_only_score", passed, Risk.CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE, active_account_access_blocked=data.controlled_account_active_access_blocked is True, account_mutations_blocked=data.controlled_account_mutations_blocked is True)


def prepare_controlled_market_data_read_only_contract(data):
    data = _coerce_input(data)
    passed = _prepared(data, "market_data_read_only_contract_prepared") and data.controlled_market_data_live_subscription_blocked is True and data.controlled_market_data_network_request_blocked is True
    return _contract(ControlledMarketDataReadOnlyContract, data, "market_data_read_only_score", passed, Risk.CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE, live_subscription_blocked=data.controlled_market_data_live_subscription_blocked is True, network_request_blocked=data.controlled_market_data_network_request_blocked is True)


def prepare_controlled_order_blocking_contract(data):
    data = _coerce_input(data)
    passed = _prepared(data, "order_blocking_contract_prepared") and data.controlled_order_execution_blocked is True and data.controlled_cancel_replace_blocked is True and data.order_execution_requested is not True
    return _contract(ControlledOrderBlockingContract, data, "order_blocking_score", passed, Risk.CONTROLLED_ORDER_BLOCKING_UNSAFE, order_execution_blocked=data.controlled_order_execution_blocked is True, real_order_blocked=data.no_real_order is True, cancel_replace_blocked=data.controlled_cancel_replace_blocked is True)


def prepare_controlled_position_mutation_block_contract(data):
    data = _coerce_input(data)
    passed = _prepared(data, "position_mutation_block_contract_prepared") and data.controlled_position_mutation_blocked is True and data.position_mutation_requested is not True
    return _contract(ControlledPositionMutationBlockContract, data, "position_mutation_block_score", passed, Risk.CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE, position_mutation_blocked=data.controlled_position_mutation_blocked is True, position_request_absent=data.position_mutation_requested is not True, close_modify_blocked=data.no_position_mutation is True)


def prepare_controlled_observability_contract(data):
    data = _coerce_input(data)
    passed = _prepared(data, "observability_contract_prepared") and _secret_boundary(data)
    return _contract(ControlledObservabilityContract, data, "observability_score", passed, Risk.CONTROLLED_OBSERVABILITY_INCOMPLETE)


def prepare_controlled_journal_contract(data):
    data = _coerce_input(data)
    passed = _prepared(data, "journal_contract_prepared") and _secret_boundary(data)
    return _contract(ControlledJournalContract, data, "journal_score", passed, Risk.CONTROLLED_JOURNAL_INCOMPLETE)


def prepare_controlled_human_approval_contract(data):
    data = _coerce_input(data)
    passed = _prepared(data, "human_approval_contract_prepared") and data.controlled_human_approval_required is True
    return _contract(ControlledHumanApprovalContract, data, "human_approval_score", passed, Risk.CONTROLLED_HUMAN_APPROVAL_MISSING, human_approval_required=data.controlled_human_approval_required is True)


def prepare_controlled_stop_conditions_contract(data):
    data = _coerce_input(data)
    passed = _prepared(data, "stop_conditions_contract_prepared") and _secret_boundary(data) and _offline_boundary(data)
    return _contract(ControlledStopConditionContract, data, "stop_conditions_score", passed, Risk.CONTROLLED_STOP_CONDITIONS_MISSING)


def prepare_controlled_success_failure_contract(data):
    data = _coerce_input(data)
    passed = _prepared(data, "success_failure_contract_prepared") and _offline_boundary(data) and data.data_access_requested is not True
    return _contract(ControlledSuccessFailureContract, data, "success_failure_score", passed, Risk.CONTROLLED_SUCCESS_FAILURE_CONTRACT_MISSING)


def prepare_controlled_audit_contract(data):
    data = _coerce_input(data)
    passed = _prepared(data, "audit_contract_prepared") and _secret_boundary(data)
    return _contract(ControlledAuditContract, data, "audit_score", passed, Risk.CONTROLLED_AUDIT_CONTRACT_MISSING)


def prepare_controlled_go_no_go_contract(data):
    data = _coerce_input(data)
    passed = _prepared(data, "go_no_go_contract_prepared") and data.controlled_human_approval_required is True and _offline_boundary(data)
    return _contract(ControlledGoNoGoContract, data, "go_no_go_score", passed, Risk.CONTROLLED_GO_NO_GO_CONTRACT_MISSING)


def prepare_controlled_abort_contract(data):
    data = _coerce_input(data)
    passed = _prepared(data, "abort_contract_prepared") and _secret_boundary(data) and _offline_boundary(data)
    return _contract(ControlledAbortContract, data, "abort_score", passed, Risk.CONTROLLED_ABORT_CONTRACT_MISSING)


def _contract_objects(data):
    return (
        prepare_controlled_execution_runtime_contract(data),
        prepare_controlled_execution_sequence_contract(data),
        prepare_controlled_execution_precondition_contract(data),
        prepare_controlled_credentials_reference_contract(data),
        prepare_controlled_no_secret_read_guard(data),
        prepare_controlled_network_block_guard(data),
        prepare_controlled_http_websocket_socket_block_guard(data),
        prepare_controlled_account_read_only_contract(data),
        prepare_controlled_market_data_read_only_contract(data),
        prepare_controlled_order_blocking_contract(data),
        prepare_controlled_position_mutation_block_contract(data),
        prepare_controlled_observability_contract(data),
        prepare_controlled_journal_contract(data),
        prepare_controlled_human_approval_contract(data),
        prepare_controlled_stop_conditions_contract(data),
        prepare_controlled_success_failure_contract(data),
        prepare_controlled_audit_contract(data),
        prepare_controlled_go_no_go_contract(data),
        prepare_controlled_abort_contract(data),
    )


def compute_controlled_execution_preparation_score(data):
    data = _coerce_input(data)
    contracts = _contract_objects(data)
    gate_score = _metric_score(data.controlled_execution_safety_gate_score, _get(_gate(data), "safety_gate_score"), validate_controlled_execution_safety_gate_approval(data))
    scores = [gate_score, *(contract.score for contract in contracts)]
    return PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationScore(
        overall_score=_average(scores),
        controlled_execution_safety_gate_score=gate_score,
        runtime_contract_score=contracts[0].score,
        sequence_contract_score=contracts[1].score,
        precondition_contract_score=contracts[2].score,
        credentials_reference_score=contracts[3].score,
        no_secret_read_guard_score=contracts[4].score,
        network_block_guard_score=contracts[5].score,
        http_websocket_socket_block_guard_score=contracts[6].score,
        account_read_only_score=contracts[7].score,
        market_data_read_only_score=contracts[8].score,
        order_blocking_score=contracts[9].score,
        position_mutation_block_score=contracts[10].score,
        observability_score=contracts[11].score,
        journal_score=contracts[12].score,
        human_approval_score=contracts[13].score,
        stop_conditions_score=contracts[14].score,
        success_failure_score=contracts[15].score,
        audit_score=contracts[16].score,
        go_no_go_score=contracts[17].score,
        abort_score=contracts[18].score,
    )


def detect_controlled_execution_preparation_risks(data):
    data = _coerce_input(data)
    risks: list[Risk] = []
    if not validate_controlled_execution_safety_gate_approval(data):
        risks.append(Risk.CONTROLLED_EXECUTION_SAFETY_GATE_NOT_APPROVED)
    for contract in _contract_objects(data):
        risks.extend(contract.risks)
    if not _offline_boundary(data):
        risks.append(Risk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if data.data_access_requested is True:
        risks.append(Risk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review_requested is True:
        risks.append(Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW)
    return _dedupe(risks)


def generate_controlled_execution_preparation_recommendations(data):
    risks = detect_controlled_execution_preparation_risks(data)
    if not risks:
        return (
            Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_SUITE,
            Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW,
        )
    mapping = {
        Risk.CONTROLLED_EXECUTION_SAFETY_GATE_NOT_APPROVED: Recommendation.APPROVE_CONTROLLED_EXECUTION_SAFETY_GATE_FIRST,
        Risk.CONTROLLED_RUNTIME_CONTRACT_MISSING: Recommendation.PREPARE_CONTROLLED_RUNTIME_CONTRACT,
        Risk.CONTROLLED_SEQUENCE_CONTRACT_MISSING: Recommendation.PREPARE_CONTROLLED_SEQUENCE_CONTRACT,
        Risk.CONTROLLED_PRECONDITION_CONTRACT_MISSING: Recommendation.PREPARE_CONTROLLED_PRECONDITION_CONTRACT,
        Risk.CONTROLLED_CREDENTIAL_REFERENCE_UNSAFE: Recommendation.HARDEN_CONTROLLED_CREDENTIAL_REFERENCE,
        Risk.CONTROLLED_SECRET_READ_GUARD_MISSING: Recommendation.INSTALL_CONTROLLED_NO_SECRET_READ_GUARD,
        Risk.CONTROLLED_NETWORK_BLOCK_GUARD_MISSING: Recommendation.INSTALL_CONTROLLED_NETWORK_BLOCK_GUARD,
        Risk.CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING: Recommendation.INSTALL_CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD,
        Risk.CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE: Recommendation.HARDEN_CONTROLLED_ACCOUNT_READ_ONLY,
        Risk.CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE: Recommendation.HARDEN_CONTROLLED_MARKET_DATA_READ_ONLY,
        Risk.CONTROLLED_ORDER_BLOCKING_UNSAFE: Recommendation.HARDEN_CONTROLLED_ORDER_BLOCKING,
        Risk.CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE: Recommendation.HARDEN_CONTROLLED_POSITION_MUTATION_BLOCK,
        Risk.CONTROLLED_OBSERVABILITY_INCOMPLETE: Recommendation.COMPLETE_CONTROLLED_OBSERVABILITY,
        Risk.CONTROLLED_JOURNAL_INCOMPLETE: Recommendation.COMPLETE_CONTROLLED_JOURNAL,
        Risk.CONTROLLED_HUMAN_APPROVAL_MISSING: Recommendation.REQUIRE_CONTROLLED_HUMAN_APPROVAL,
        Risk.CONTROLLED_STOP_CONDITIONS_MISSING: Recommendation.DEFINE_CONTROLLED_STOP_CONDITIONS,
        Risk.CONTROLLED_SUCCESS_FAILURE_CONTRACT_MISSING: Recommendation.PREPARE_CONTROLLED_SUCCESS_FAILURE_CONTRACT,
        Risk.CONTROLLED_AUDIT_CONTRACT_MISSING: Recommendation.PREPARE_CONTROLLED_AUDIT_CONTRACT,
        Risk.CONTROLLED_GO_NO_GO_CONTRACT_MISSING: Recommendation.PREPARE_CONTROLLED_GO_NO_GO_CONTRACT,
        Risk.CONTROLLED_ABORT_CONTRACT_MISSING: Recommendation.PREPARE_CONTROLLED_ABORT_CONTRACT,
        Risk.REAL_EXECUTION_BOUNDARY_VIOLATION: Recommendation.RESTORE_OFFLINE_BOUNDARIES,
        Risk.DATA_ACCESS_VIOLATION: Recommendation.REMOVE_DATA_ACCESS,
        Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW: Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW,
    }
    return _dedupe([Recommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW, *(mapping[risk] for risk in risks if risk in mapping)])


def _decision_for_risks(risks):
    if not risks:
        return Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION
    if Risk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks or Risk.DATA_ACCESS_VIOLATION in risks:
        return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION
    ordered = (
        (Risk.CONTROLLED_EXECUTION_SAFETY_GATE_NOT_APPROVED, Decision.REQUIRE_CONTROLLED_EXECUTION_SAFETY_GATE_FIXES),
        (Risk.CONTROLLED_RUNTIME_CONTRACT_MISSING, Decision.REQUIRE_CONTROLLED_RUNTIME_CONTRACT_FIXES),
        (Risk.CONTROLLED_SEQUENCE_CONTRACT_MISSING, Decision.REQUIRE_CONTROLLED_SEQUENCE_CONTRACT_FIXES),
        (Risk.CONTROLLED_PRECONDITION_CONTRACT_MISSING, Decision.REQUIRE_CONTROLLED_PRECONDITION_CONTRACT_FIXES),
        (Risk.CONTROLLED_CREDENTIAL_REFERENCE_UNSAFE, Decision.REQUIRE_CONTROLLED_CREDENTIAL_REFERENCE_FIXES),
        (Risk.CONTROLLED_SECRET_READ_GUARD_MISSING, Decision.REQUIRE_CONTROLLED_NO_SECRET_READ_GUARD_FIXES),
        (Risk.CONTROLLED_NETWORK_BLOCK_GUARD_MISSING, Decision.REQUIRE_CONTROLLED_NETWORK_BLOCK_GUARD_FIXES),
        (Risk.CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING, Decision.REQUIRE_CONTROLLED_NETWORK_BLOCK_GUARD_FIXES),
        (Risk.CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE, Decision.REQUIRE_CONTROLLED_ACCOUNT_READ_ONLY_FIXES),
        (Risk.CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE, Decision.REQUIRE_CONTROLLED_MARKET_DATA_READ_ONLY_FIXES),
        (Risk.CONTROLLED_ORDER_BLOCKING_UNSAFE, Decision.REQUIRE_CONTROLLED_ORDER_BLOCKING_FIXES),
        (Risk.CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE, Decision.REQUIRE_CONTROLLED_POSITION_MUTATION_BLOCK_FIXES),
        (Risk.CONTROLLED_OBSERVABILITY_INCOMPLETE, Decision.REQUIRE_CONTROLLED_OBSERVABILITY_FIXES),
        (Risk.CONTROLLED_JOURNAL_INCOMPLETE, Decision.REQUIRE_CONTROLLED_JOURNAL_FIXES),
        (Risk.CONTROLLED_HUMAN_APPROVAL_MISSING, Decision.REQUIRE_CONTROLLED_HUMAN_APPROVAL_FIXES),
        (Risk.CONTROLLED_STOP_CONDITIONS_MISSING, Decision.REQUIRE_CONTROLLED_STOP_CONDITION_FIXES),
        (Risk.CONTROLLED_SUCCESS_FAILURE_CONTRACT_MISSING, Decision.REQUIRE_CONTROLLED_SUCCESS_FAILURE_FIXES),
        (Risk.CONTROLLED_AUDIT_CONTRACT_MISSING, Decision.REQUIRE_CONTROLLED_AUDIT_FIXES),
        (Risk.CONTROLLED_GO_NO_GO_CONTRACT_MISSING, Decision.REQUIRE_CONTROLLED_GO_NO_GO_FIXES),
        (Risk.CONTROLLED_ABORT_CONTRACT_MISSING, Decision.REQUIRE_CONTROLLED_ABORT_FIXES),
    )
    for risk, decision in ordered:
        if risk in risks:
            return decision
    return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION


def _state_for_result(data, risks, score):
    state = PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationState
    if data.paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate is None:
        return state.CONTROLLED_EXECUTION_PREPARATION_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return state.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW
    if risks:
        return state.CONTROLLED_EXECUTION_PREPARATION_BLOCKED
    if score.overall_score >= 70:
        return state.CONTROLLED_EXECUTION_PREPARATION_COMPLETED_WITH_WARNINGS
    return state.NOT_READY


def evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation(data):
    data = _coerce_input(data)
    score = compute_controlled_execution_preparation_score(data)
    risks = detect_controlled_execution_preparation_risks(data)
    contracts = _contract_objects(data)
    return PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationResult(
        state=_state_for_result(data, risks, score),
        decision=_decision_for_risks(risks),
        preparation_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=generate_controlled_execution_preparation_recommendations(data),
        controlled_execution_runtime_contract=contracts[0],
        controlled_execution_sequence_contract=contracts[1],
        controlled_execution_precondition_contract=contracts[2],
        controlled_credentials_reference_contract=contracts[3],
        controlled_no_secret_read_guard=contracts[4],
        controlled_network_block_guard=contracts[5],
        controlled_http_websocket_socket_block_guard=contracts[6],
        controlled_account_read_only_contract=contracts[7],
        controlled_market_data_read_only_contract=contracts[8],
        controlled_order_blocking_contract=contracts[9],
        controlled_position_mutation_block_contract=contracts[10],
        controlled_observability_contract=contracts[11],
        controlled_journal_contract=contracts[12],
        controlled_human_approval_contract=contracts[13],
        controlled_stop_conditions_contract=contracts[14],
        controlled_success_failure_contract=contracts[15],
        controlled_audit_contract=contracts[16],
        controlled_go_no_go_contract=contracts[17],
        controlled_abort_contract=contracts[18],
        offline_only=True,
        summary=("Ready for controlled execution preparation review." if not risks else "Blocked until controlled preparation risks are fixed."),
    )


def render_paper_broker_read_only_connection_dry_run_controlled_execution_preparation_markdown(result):
    if isinstance(result, Mapping):
        result = PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationResult(**dict(result))
    risks = ", ".join(risk.value for risk in result.risks) or "none"
    recommendations = ", ".join(recommendation.value for recommendation in result.recommendations) or "none"
    return "\n".join(
        (
            "# Paper Broker Read-Only Connection Dry Run Controlled Execution Preparation",
            f"- State: {result.state.value}",
            f"- Decision: {result.decision.value}",
            f"- Preparation score: {result.preparation_score}",
            f"- Risks: {risks}",
            f"- Recommendations: {recommendations}",
            "- Offline only: true",
            "- Sandbox only: true",
            "- Preparation only: true",
            "- Dry-run executed: false",
            "- Broker connection executed: false",
            "- API key read: false",
            "- Environment variable read: false",
            "- No HTTP, websocket, socket, network transport, or external API",
            "- Orders and position mutations: blocked",
            "- Active account access: blocked",
            "- No data/ access",
            "- Go/no-go and abort contracts: prepared",
        )
    )
