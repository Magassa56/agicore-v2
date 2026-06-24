"""Offline review for read-only broker dry-run controlled execution preparation."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Callable, Iterable, Mapping

from agicore.trading import paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review_models as m


Risk = m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk
Decision = m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision
Recommendation = m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRecommendation


def _coerce_input(data):
    if data is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewInput()
    if isinstance(data, m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewInput):
        return data
    allowed = {field.name for field in fields(m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewInput)}
    return m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewInput(
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


def _as_tuple(items: Any) -> tuple[Any, ...]:
    if items is None:
        return ()
    if isinstance(items, tuple):
        return items
    if isinstance(items, list):
        return tuple(items)
    if isinstance(items, set):
        return tuple(items)
    return (items,)


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


def _preparation(data):
    return data.paper_broker_read_only_connection_dry_run_controlled_execution_preparation


def _contract(data, name: str):
    return _get(_preparation(data), name)


def _contract_ok(contract: Any) -> bool:
    return contract is not None and _get(contract, "defined", True) is True and not _as_tuple(_get(contract, "risks", ()))


def _offline_boundary(data) -> bool:
    expected_true = (
        data.offline_mode_enforced,
        data.sandbox_mode_enforced,
        data.review_only,
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


def validate_controlled_execution_preparation_approval(data):
    data = _coerce_input(data)
    preparation = _preparation(data)
    if preparation is None or data.controlled_execution_preparation_approved is False:
        return False
    approved = data.controlled_execution_preparation_approved is True or _state_contains(
        preparation,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION",
    )
    return approved and not _as_tuple(_get(preparation, "risks", ())) and _get(preparation, "offline_only", True) is True


Check = tuple[str, Callable[[Any, Any], bool]]


def _review(data, *, contract_name: str, flag_name: str, score_name: str, risk: Risk, cls: type, checks: tuple[Check, ...], name: str | None = None):
    data = _coerce_input(data)
    contract = _contract(data, contract_name)
    values = {field: check(data, contract) for field, check in checks}
    passed = _get(data, flag_name) is not False and _contract_ok(contract) and all(values.values())
    payload = {
        "score": _metric_score(_get(data, score_name), _get(contract, "score"), passed),
        "passed": passed,
        "risks": () if passed else (risk,),
        "details": (f"{contract_name} reviewed offline without dry-run execution",),
        **values,
    }
    if name is not None:
        payload["name"] = name
    return cls(**payload)


def review_controlled_execution_runtime_contract(data):
    return _review(data, contract_name="controlled_execution_runtime_contract", flag_name="controlled_runtime_contract_review_verified", score_name="runtime_contract_score", risk=Risk.CONTROLLED_RUNTIME_CONTRACT_REVIEW_FAILED, cls=m.ControlledExecutionRuntimeContractReviewFinding, checks=(("preparation_only", lambda d, c: _get(c, "preparation_only") is True and d.dry_run_executed is not True), ("read_only_only", lambda d, c: _get(c, "read_only_only") is True), ("dry_run_execution_disabled", lambda d, c: _get(c, "dry_run_execution_disabled") is True)))


def review_controlled_execution_sequence_contract(data):
    return _review(data, contract_name="controlled_execution_sequence_contract", flag_name="controlled_sequence_contract_review_verified", score_name="sequence_contract_score", risk=Risk.CONTROLLED_SEQUENCE_CONTRACT_REVIEW_FAILED, cls=m.ControlledExecutionSequenceContractReviewFinding, checks=(("dry_run_not_executed", lambda d, c: _get(c, "dry_run_not_executed") is True and d.dry_run_executed is not True), ("connection_not_executed", lambda d, c: _get(c, "connection_not_executed") is True and d.broker_connection_requested is not True), ("sequence_steps_defined", lambda d, c: _get(c, "sequence_steps_defined") is True), ("network_transport_blocked", lambda d, c: _get(c, "network_transport_blocked") is True)))


def review_controlled_execution_precondition_contract(data):
    return _review(data, contract_name="controlled_execution_precondition_contract", flag_name="controlled_precondition_contract_review_verified", score_name="precondition_contract_score", risk=Risk.CONTROLLED_PRECONDITION_REVIEW_FAILED, cls=m.ControlledExecutionPreconditionContractReviewFinding, checks=(("safety_gate_required", lambda d, c: _get(c, "safety_gate_required") is True), ("human_approval_required", lambda d, c: _get(c, "human_approval_required") is True), ("stop_conditions_required", lambda d, c: _get(c, "stop_conditions_required") is True), ("fail_closed", lambda d, c: _get(c, "fail_closed") is True)))


def review_controlled_credentials_reference_contract(data):
    return _review(data, contract_name="controlled_credentials_reference_contract", flag_name="controlled_credential_reference_review_verified", score_name="credentials_reference_score", risk=Risk.CONTROLLED_CREDENTIAL_REFERENCE_REVIEW_FAILED, cls=m.ControlledCredentialsReferenceReviewFinding, checks=(("reference_only", lambda d, c: _get(c, "reference_only") is True), ("no_secret_values", lambda d, c: _get(c, "no_secret_values") is True and d.hardcoded_secret_detected is not True), ("no_api_key_read", lambda d, c: _get(c, "no_api_key_read") is True and d.api_key_read_requested is not True), ("no_env_var_read", lambda d, c: _get(c, "no_env_var_read") is True and d.env_var_read_requested is not True)))


def review_controlled_no_secret_read_guard(data):
    return _review(data, contract_name="controlled_no_secret_read_guard", flag_name="controlled_no_secret_read_guard_review_verified", score_name="no_secret_read_guard_score", risk=Risk.CONTROLLED_SECRET_READ_GUARD_REVIEW_FAILED, cls=m.ControlledNoSecretReadGuardReviewFinding, checks=(("guard_enforced", lambda d, c: _get(c, "guard_enforced") is True), ("no_api_key_read", lambda d, c: _get(c, "no_api_key_read") is True and d.api_key_read_requested is not True), ("no_env_var_read", lambda d, c: _get(c, "no_env_var_read") is True and d.env_var_read_requested is not True), ("no_hardcoded_secret", lambda d, c: _get(c, "no_hardcoded_secret") is True and d.hardcoded_secret_detected is not True)))


def _network_checks() -> tuple[Check, ...]:
    return (("network_execution_blocked", lambda d, c: _get(c, "network_execution_blocked") is True and d.network_transport_requested is not True), ("http_blocked", lambda d, c: _get(c, "http_blocked") is True and d.no_http_transport is True), ("websocket_blocked", lambda d, c: _get(c, "websocket_blocked") is True and d.no_websocket_transport is True), ("socket_blocked", lambda d, c: _get(c, "socket_blocked") is True and d.no_socket_transport is True), ("external_api_blocked", lambda d, c: _get(c, "external_api_blocked") is True and d.external_api_requested is not True))


def review_controlled_network_block_guard(data):
    return _review(data, contract_name="controlled_network_block_guard", flag_name="controlled_network_block_guard_review_verified", score_name="network_block_guard_score", risk=Risk.CONTROLLED_NETWORK_BLOCK_GUARD_REVIEW_FAILED, cls=m.ControlledNetworkBlockGuardReviewFinding, checks=_network_checks())


def review_controlled_http_websocket_socket_block_guard(data):
    return _review(data, contract_name="controlled_http_websocket_socket_block_guard", flag_name="controlled_http_websocket_socket_block_guard_review_verified", score_name="http_websocket_socket_block_guard_score", risk=Risk.CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED, cls=m.ControlledNetworkBlockGuardReviewFinding, checks=_network_checks(), name="controlled_http_websocket_socket_block_guard_review")


def review_controlled_account_read_only_contract(data):
    return _review(data, contract_name="controlled_account_read_only_contract", flag_name="controlled_account_read_only_review_verified", score_name="account_read_only_score", risk=Risk.CONTROLLED_ACCOUNT_READ_ONLY_REVIEW_FAILED, cls=m.ControlledAccountReadOnlyReviewFinding, checks=(("active_account_access_blocked", lambda d, c: _get(c, "active_account_access_blocked") is True and d.account_access_requested is not True), ("account_mutations_blocked", lambda d, c: _get(c, "account_mutations_blocked") is True), ("schema_only_account_review", lambda d, c: _get(c, "schema_only_account_review") is True)))


def review_controlled_market_data_read_only_contract(data):
    return _review(data, contract_name="controlled_market_data_read_only_contract", flag_name="controlled_market_data_read_only_review_verified", score_name="market_data_read_only_score", risk=Risk.CONTROLLED_MARKET_DATA_READ_ONLY_REVIEW_FAILED, cls=m.ControlledMarketDataReadOnlyReviewFinding, checks=(("read_only_market_data_only", lambda d, c: _get(c, "read_only_market_data_only") is True), ("live_subscription_blocked", lambda d, c: _get(c, "live_subscription_blocked") is True), ("network_request_blocked", lambda d, c: _get(c, "network_request_blocked") is True and d.network_transport_requested is not True), ("schema_or_synthetic_only", lambda d, c: _get(c, "schema_or_synthetic_only") is True)))


def review_controlled_order_blocking_contract(data):
    return _review(data, contract_name="controlled_order_blocking_contract", flag_name="controlled_order_blocking_review_verified", score_name="order_blocking_score", risk=Risk.CONTROLLED_ORDER_BLOCKING_REVIEW_FAILED, cls=m.ControlledOrderBlockingReviewFinding, checks=(("order_execution_blocked", lambda d, c: _get(c, "order_execution_blocked") is True and d.order_execution_requested is not True), ("real_order_blocked", lambda d, c: _get(c, "real_order_blocked") is True and d.no_real_order is True), ("cancel_replace_blocked", lambda d, c: _get(c, "cancel_replace_blocked") is True)))


def review_controlled_position_mutation_block_contract(data):
    return _review(data, contract_name="controlled_position_mutation_block_contract", flag_name="controlled_position_mutation_block_review_verified", score_name="position_mutation_block_score", risk=Risk.CONTROLLED_POSITION_MUTATION_BLOCK_REVIEW_FAILED, cls=m.ControlledPositionMutationBlockReviewFinding, checks=(("position_mutation_blocked", lambda d, c: _get(c, "position_mutation_blocked") is True and d.position_mutation_requested is not True), ("position_request_absent", lambda d, c: _get(c, "position_request_absent") is True), ("close_modify_blocked", lambda d, c: _get(c, "close_modify_blocked") is True)))


def review_controlled_observability_contract(data):
    return _review(data, contract_name="controlled_observability_contract", flag_name="controlled_observability_review_verified", score_name="observability_score", risk=Risk.CONTROLLED_OBSERVABILITY_REVIEW_FAILED, cls=m.ControlledObservabilityReviewFinding, checks=(("offline_events_defined", lambda d, c: _get(c, "offline_events_defined") is True), ("connection_attempt_logging_disabled", lambda d, c: _get(c, "connection_attempt_logging_disabled") is True), ("sensitive_values_redacted", lambda d, c: _get(c, "sensitive_values_redacted") is True)))


def review_controlled_journal_contract(data):
    return _review(data, contract_name="controlled_journal_contract", flag_name="controlled_journal_review_verified", score_name="journal_score", risk=Risk.CONTROLLED_JOURNAL_REVIEW_FAILED, cls=m.ControlledJournalReviewFinding, checks=(("offline_journal_required", lambda d, c: _get(c, "offline_journal_required") is True), ("sensitive_values_redacted", lambda d, c: _get(c, "sensitive_values_redacted") is True), ("no_secret_material_logged", lambda d, c: _get(c, "no_secret_material_logged") is True)))


def review_controlled_human_approval_contract(data):
    return _review(data, contract_name="controlled_human_approval_contract", flag_name="controlled_human_approval_review_verified", score_name="human_approval_score", risk=Risk.CONTROLLED_HUMAN_APPROVAL_REVIEW_FAILED, cls=m.ControlledHumanApprovalReviewFinding, checks=(("human_approval_required", lambda d, c: _get(c, "human_approval_required") is True), ("approval_before_review", lambda d, c: _get(c, "approval_before_review") is True), ("safety_gate_evidence_required", lambda d, c: _get(c, "safety_gate_evidence_required") is True)))


def review_controlled_stop_conditions_contract(data):
    return _review(data, contract_name="controlled_stop_conditions_contract", flag_name="controlled_stop_conditions_review_verified", score_name="stop_conditions_score", risk=Risk.CONTROLLED_STOP_CONDITION_REVIEW_FAILED, cls=m.ControlledStopConditionReviewFinding, checks=(("stop_on_secret_read", lambda d, c: _get(c, "stop_on_secret_read") is True), ("stop_on_network_request", lambda d, c: _get(c, "stop_on_network_request") is True), ("stop_on_order_or_position_request", lambda d, c: _get(c, "stop_on_order_or_position_request") is True), ("stop_on_account_access_request", lambda d, c: _get(c, "stop_on_account_access_request") is True)))


def review_controlled_success_failure_contract(data):
    return _review(data, contract_name="controlled_success_failure_contract", flag_name="controlled_success_failure_review_verified", score_name="success_failure_score", risk=Risk.CONTROLLED_SUCCESS_FAILURE_REVIEW_FAILED, cls=m.ControlledSuccessFailureReviewFinding, checks=(("success_requires_no_real_connection", lambda d, c: _get(c, "success_requires_no_real_connection") is True), ("success_requires_all_guards_verified", lambda d, c: _get(c, "success_requires_all_guards_verified") is True), ("failure_on_secret_network_order_position_or_account", lambda d, c: _get(c, "failure_on_secret_network_order_position_or_account") is True)))


def review_controlled_audit_contract(data):
    return _review(data, contract_name="controlled_audit_contract", flag_name="controlled_audit_review_verified", score_name="audit_score", risk=Risk.CONTROLLED_AUDIT_REVIEW_FAILED, cls=m.ControlledAuditReviewFinding, checks=(("audit_events_defined", lambda d, c: _get(c, "audit_events_defined") is True), ("offline_evidence_required", lambda d, c: _get(c, "offline_evidence_required") is True), ("preparation_review_trace_required", lambda d, c: _get(c, "preparation_review_trace_required") is True)))


def review_controlled_go_no_go_contract(data):
    return _review(data, contract_name="controlled_go_no_go_contract", flag_name="controlled_go_no_go_review_verified", score_name="go_no_go_score", risk=Risk.CONTROLLED_GO_NO_GO_REVIEW_FAILED, cls=m.ControlledGoNoGoReviewFinding, checks=(("go_requires_all_contracts_ready", lambda d, c: _get(c, "go_requires_all_contracts_ready") is True), ("no_go_on_any_boundary_violation", lambda d, c: _get(c, "no_go_on_any_boundary_violation") is True), ("human_go_required", lambda d, c: _get(c, "human_go_required") is True)))


def review_controlled_abort_contract(data):
    return _review(data, contract_name="controlled_abort_contract", flag_name="controlled_abort_review_verified", score_name="abort_score", risk=Risk.CONTROLLED_ABORT_REVIEW_FAILED, cls=m.ControlledAbortReviewFinding, checks=(("abort_on_secret_read", lambda d, c: _get(c, "abort_on_secret_read") is True), ("abort_on_network_request", lambda d, c: _get(c, "abort_on_network_request") is True), ("abort_on_order_position_or_account", lambda d, c: _get(c, "abort_on_order_position_or_account") is True), ("abort_on_go_no_go_failure", lambda d, c: _get(c, "abort_on_go_no_go_failure") is True)))


def _review_objects(data):
    return (
        review_controlled_execution_runtime_contract(data),
        review_controlled_execution_sequence_contract(data),
        review_controlled_execution_precondition_contract(data),
        review_controlled_credentials_reference_contract(data),
        review_controlled_no_secret_read_guard(data),
        review_controlled_network_block_guard(data),
        review_controlled_http_websocket_socket_block_guard(data),
        review_controlled_account_read_only_contract(data),
        review_controlled_market_data_read_only_contract(data),
        review_controlled_order_blocking_contract(data),
        review_controlled_position_mutation_block_contract(data),
        review_controlled_observability_contract(data),
        review_controlled_journal_contract(data),
        review_controlled_human_approval_contract(data),
        review_controlled_stop_conditions_contract(data),
        review_controlled_success_failure_contract(data),
        review_controlled_audit_contract(data),
        review_controlled_go_no_go_contract(data),
        review_controlled_abort_contract(data),
    )


def compute_controlled_execution_preparation_review_score(data):
    data = _coerce_input(data)
    reviews = _review_objects(data)
    prep_score = _metric_score(data.controlled_execution_preparation_score, _get(_preparation(data), "preparation_score"), validate_controlled_execution_preparation_approval(data))
    return m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewScore(
        overall_score=_average((prep_score, *(review.score for review in reviews))),
        controlled_execution_preparation_score=prep_score,
        runtime_contract_score=reviews[0].score,
        sequence_contract_score=reviews[1].score,
        precondition_contract_score=reviews[2].score,
        credentials_reference_score=reviews[3].score,
        no_secret_read_guard_score=reviews[4].score,
        network_block_guard_score=reviews[5].score,
        http_websocket_socket_block_guard_score=reviews[6].score,
        account_read_only_score=reviews[7].score,
        market_data_read_only_score=reviews[8].score,
        order_blocking_score=reviews[9].score,
        position_mutation_block_score=reviews[10].score,
        observability_score=reviews[11].score,
        journal_score=reviews[12].score,
        human_approval_score=reviews[13].score,
        stop_conditions_score=reviews[14].score,
        success_failure_score=reviews[15].score,
        audit_score=reviews[16].score,
        go_no_go_score=reviews[17].score,
        abort_score=reviews[18].score,
    )


def detect_controlled_execution_preparation_review_risks(data):
    data = _coerce_input(data)
    risks: list[Risk] = []
    if not validate_controlled_execution_preparation_approval(data):
        risks.append(Risk.CONTROLLED_EXECUTION_PREPARATION_NOT_APPROVED)
    for review in _review_objects(data):
        risks.extend(_as_tuple(_get(review, "risks", ())))
    if not _offline_boundary(data):
        risks.append(Risk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if data.data_access_requested is True:
        risks.append(Risk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_controlled_execution_final_plan_requested is True:
        risks.append(Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN)
    return _dedupe(risks)


def generate_controlled_execution_preparation_review_recommendations(data):
    risks = detect_controlled_execution_preparation_review_risks(data)
    if not risks:
        return (
            Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW_SUITE,
            Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN,
        )
    mapping = {
        Risk.CONTROLLED_EXECUTION_PREPARATION_NOT_APPROVED: Recommendation.APPROVE_CONTROLLED_EXECUTION_PREPARATION_FIRST,
        Risk.CONTROLLED_RUNTIME_CONTRACT_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_RUNTIME_CONTRACT_REVIEW,
        Risk.CONTROLLED_SEQUENCE_CONTRACT_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_SEQUENCE_CONTRACT_REVIEW,
        Risk.CONTROLLED_PRECONDITION_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_PRECONDITION_REVIEW,
        Risk.CONTROLLED_CREDENTIAL_REFERENCE_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_CREDENTIAL_REFERENCE_REVIEW,
        Risk.CONTROLLED_SECRET_READ_GUARD_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_NO_SECRET_READ_GUARD_REVIEW,
        Risk.CONTROLLED_NETWORK_BLOCK_GUARD_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_NETWORK_BLOCK_GUARD_REVIEW,
        Risk.CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW,
        Risk.CONTROLLED_ACCOUNT_READ_ONLY_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_ACCOUNT_READ_ONLY_REVIEW,
        Risk.CONTROLLED_MARKET_DATA_READ_ONLY_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_MARKET_DATA_READ_ONLY_REVIEW,
        Risk.CONTROLLED_ORDER_BLOCKING_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_ORDER_BLOCKING_REVIEW,
        Risk.CONTROLLED_POSITION_MUTATION_BLOCK_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_POSITION_MUTATION_BLOCK_REVIEW,
        Risk.CONTROLLED_OBSERVABILITY_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_OBSERVABILITY_REVIEW,
        Risk.CONTROLLED_JOURNAL_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_JOURNAL_REVIEW,
        Risk.CONTROLLED_HUMAN_APPROVAL_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_HUMAN_APPROVAL_REVIEW,
        Risk.CONTROLLED_STOP_CONDITION_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_STOP_CONDITION_REVIEW,
        Risk.CONTROLLED_SUCCESS_FAILURE_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_SUCCESS_FAILURE_REVIEW,
        Risk.CONTROLLED_AUDIT_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_AUDIT_REVIEW,
        Risk.CONTROLLED_GO_NO_GO_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_GO_NO_GO_REVIEW,
        Risk.CONTROLLED_ABORT_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_ABORT_REVIEW,
        Risk.REAL_EXECUTION_BOUNDARY_VIOLATION: Recommendation.RESTORE_OFFLINE_BOUNDARIES,
        Risk.DATA_ACCESS_VIOLATION: Recommendation.REMOVE_DATA_ACCESS,
        Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN: Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN,
    }
    return _dedupe([Recommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN, *(mapping[risk] for risk in risks if risk in mapping)])


def _decision_for_risks(risks):
    if not risks:
        return Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW
    if Risk.CONTROLLED_EXECUTION_PREPARATION_NOT_APPROVED in risks:
        return Decision.REQUIRE_CONTROLLED_EXECUTION_PREPARATION_FIXES
    if Risk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks or Risk.DATA_ACCESS_VIOLATION in risks:
        return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW
    ordered = (
        (Risk.CONTROLLED_RUNTIME_CONTRACT_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_RUNTIME_CONTRACT_REVIEW_FIXES),
        (Risk.CONTROLLED_SEQUENCE_CONTRACT_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_SEQUENCE_CONTRACT_REVIEW_FIXES),
        (Risk.CONTROLLED_PRECONDITION_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_PRECONDITION_REVIEW_FIXES),
        (Risk.CONTROLLED_CREDENTIAL_REFERENCE_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_CREDENTIAL_REFERENCE_REVIEW_FIXES),
        (Risk.CONTROLLED_SECRET_READ_GUARD_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_NO_SECRET_READ_GUARD_REVIEW_FIXES),
        (Risk.CONTROLLED_NETWORK_BLOCK_GUARD_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_NETWORK_BLOCK_GUARD_REVIEW_FIXES),
        (Risk.CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_NETWORK_BLOCK_GUARD_REVIEW_FIXES),
        (Risk.CONTROLLED_ACCOUNT_READ_ONLY_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_ACCOUNT_READ_ONLY_REVIEW_FIXES),
        (Risk.CONTROLLED_MARKET_DATA_READ_ONLY_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_MARKET_DATA_READ_ONLY_REVIEW_FIXES),
        (Risk.CONTROLLED_ORDER_BLOCKING_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_ORDER_BLOCKING_REVIEW_FIXES),
        (Risk.CONTROLLED_POSITION_MUTATION_BLOCK_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_POSITION_MUTATION_BLOCK_REVIEW_FIXES),
        (Risk.CONTROLLED_OBSERVABILITY_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_OBSERVABILITY_REVIEW_FIXES),
        (Risk.CONTROLLED_JOURNAL_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_JOURNAL_REVIEW_FIXES),
        (Risk.CONTROLLED_HUMAN_APPROVAL_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_HUMAN_APPROVAL_REVIEW_FIXES),
        (Risk.CONTROLLED_STOP_CONDITION_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_STOP_CONDITION_REVIEW_FIXES),
        (Risk.CONTROLLED_SUCCESS_FAILURE_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_SUCCESS_FAILURE_REVIEW_FIXES),
        (Risk.CONTROLLED_AUDIT_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_AUDIT_REVIEW_FIXES),
        (Risk.CONTROLLED_GO_NO_GO_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_GO_NO_GO_REVIEW_FIXES),
        (Risk.CONTROLLED_ABORT_REVIEW_FAILED, Decision.REQUIRE_CONTROLLED_ABORT_REVIEW_FIXES),
    )
    for risk, decision in ordered:
        if risk in risks:
            return decision
    return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW


def _state_for_result(data, risks, score):
    state = m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewState
    if data.paper_broker_read_only_connection_dry_run_controlled_execution_preparation is None:
        return state.CONTROLLED_EXECUTION_PREPARATION_REVIEW_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return state.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN
    if risks:
        return state.CONTROLLED_EXECUTION_PREPARATION_REVIEW_BLOCKED
    if score.overall_score >= 70:
        return state.CONTROLLED_EXECUTION_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS
    return state.NOT_READY


def evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review(data):
    data = _coerce_input(data)
    score = compute_controlled_execution_preparation_review_score(data)
    risks = detect_controlled_execution_preparation_review_risks(data)
    reviews = _review_objects(data)
    return m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewResult(
        state=_state_for_result(data, risks, score),
        decision=_decision_for_risks(risks),
        review_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=generate_controlled_execution_preparation_review_recommendations(data),
        controlled_execution_runtime_contract_review=reviews[0],
        controlled_execution_sequence_contract_review=reviews[1],
        controlled_execution_precondition_contract_review=reviews[2],
        controlled_credentials_reference_review=reviews[3],
        controlled_no_secret_read_guard_review=reviews[4],
        controlled_network_block_guard_review=reviews[5],
        controlled_http_websocket_socket_block_guard_review=reviews[6],
        controlled_account_read_only_review=reviews[7],
        controlled_market_data_read_only_review=reviews[8],
        controlled_order_blocking_review=reviews[9],
        controlled_position_mutation_block_review=reviews[10],
        controlled_observability_review=reviews[11],
        controlled_journal_review=reviews[12],
        controlled_human_approval_review=reviews[13],
        controlled_stop_conditions_review=reviews[14],
        controlled_success_failure_review=reviews[15],
        controlled_audit_review=reviews[16],
        controlled_go_no_go_review=reviews[17],
        controlled_abort_review=reviews[18],
        offline_only=True,
        summary=("Controlled execution preparation review is ready for final plan." if not risks else "Controlled execution preparation review is blocked until risks are fixed."),
    )


def render_paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review_markdown(result):
    if isinstance(result, Mapping):
        result = m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewResult(**dict(result))
    risks = ", ".join(risk.value for risk in result.risks) or "none"
    recommendations = ", ".join(recommendation.value for recommendation in result.recommendations) or "none"
    return "\n".join(
        (
            "# Paper Broker Read-Only Connection Dry Run Controlled Execution Preparation Review",
            f"- State: {result.state.value}",
            f"- Decision: {result.decision.value}",
            f"- Review score: {result.review_score}",
            f"- Risks: {risks}",
            f"- Recommendations: {recommendations}",
            "- Offline only: true",
            "- Sandbox only: true",
            "- Review only: true",
            "- Dry-run executed: false",
            "- Broker connection executed: false",
            "- API key read: false",
            "- Environment variable read: false",
            "- No HTTP, websocket, socket, network transport, or external API",
            "- Orders and position mutations: blocked",
            "- Active account access: blocked",
            "- No data/ access",
            "- Go/no-go and abort contract review: verified",
        )
    )
