"""Offline preparation for a future AGIcore Paper Broker read-only safety review."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_read_only_preparation_models import (
    AccountReadOnlyPolicy,
    BrokerEnvironmentBoundary,
    CredentialsHandlingPolicy,
    MarketDataReadOnlyPolicy,
    NoOrderExecutionPolicy,
    PaperBrokerReadOnlyPreparationDecision,
    PaperBrokerReadOnlyPreparationInput,
    PaperBrokerReadOnlyPreparationRecommendation,
    PaperBrokerReadOnlyPreparationResult,
    PaperBrokerReadOnlyPreparationRisk,
    PaperBrokerReadOnlyPreparationScore,
    PaperBrokerReadOnlyPreparationState,
    PaperVsRealBoundaryPolicy,
    ReadOnlyPermissionPolicy,
    ReadOnlyPreparationFinding,
    ReadOnlyPreparationScope,
)


def _coerce_input(data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None) -> PaperBrokerReadOnlyPreparationInput:
    if data is None:
        return PaperBrokerReadOnlyPreparationInput()
    if isinstance(data, PaperBrokerReadOnlyPreparationInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerReadOnlyPreparationInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerReadOnlyPreparationInput(**payload)


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


def _contains(items: Any, *needles: str) -> bool:
    text_items = tuple(_value(item).upper() for item in _as_tuple(items))
    return any(any(needle.upper() in item for item in text_items) for needle in needles)


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


def _bool_score(value: bool | None, unknown: int = 40) -> int:
    if value is True:
        return 100
    if value is False:
        return 0
    return unknown


def _average(values: Iterable[int | float | None], default: int = 0) -> int:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return default
    return _clamp(sum(usable) / len(usable))


def _upstream_items(data: PaperBrokerReadOnlyPreparationInput) -> tuple[Any, ...]:
    return (
        data.multi_scenario_result_report,
        data.multi_scenario_controlled_simulation_result,
        data.performance_risk_validation_gate,
        data.performance_metrics_result,
        data.risk_metrics_result,
        data.controlled_simulation_result_report,
        data.controlled_simulation_offline_runner_result,
        data.paper_runtime_forward_test_plan,
        data.official_paper_validation_report,
        data.paper_runtime_validation,
        data.paper_trading_runtime,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.human_validated_paper_session,
        data.supervised_paper_session,
    )


def _upstream_risks(data: PaperBrokerReadOnlyPreparationInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerReadOnlyPreparationInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PaperBrokerReadOnlyPreparationInput) -> bool:
    return (
        data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.preparation_only is True
        and data.broker_connection_disabled is True
        and data.no_real_broker is True
        and data.no_alpaca_real is True
        and data.no_api_key_read is True
        and data.no_env_var_read is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
        and data.no_external_ml is True
        and data.no_external_llm is True
        and data.no_live_execution is True
        and data.no_real_order is True
        and data.no_position_mutation is True
        and data.no_real_account_access is True
        and data.real_execution_requested is not True
        and data.broker_connection_requested is not True
        and data.api_key_read_requested is not True
        and data.env_var_read_requested is not True
        and data.order_execution_requested is not True
        and data.position_mutation_requested is not True
        and data.account_access_requested is not True
        and data.network_transport_requested is not True
        and all(_get(item, "offline_only", True) is True for item in _upstream_items(data))
        and not _has_upstream_risk(
            data,
            "LIVE_EXECUTION",
            "BROKER_CONNECTIVITY",
            "BROKER_CONNECTION",
            "API_ACCESS",
            "NETWORK",
            "HTTP",
            "WEBSOCKET",
            "SOCKET",
            "REAL_ORDER",
            "REAL_ACCOUNT",
            "REAL_EXECUTION",
            "POSITION_MUTATION",
            "ALPACA_REAL",
        )
    )


def _data_boundary(data: PaperBrokerReadOnlyPreparationInput) -> bool:
    return (
        data.data_access_requested is not True
        and not _has_upstream_risk(data, "DATA_ACCESS", "DATA_ACCESS_VIOLATION", "REAL_DATA")
    )


def _credentials_boundary(data: PaperBrokerReadOnlyPreparationInput) -> bool:
    return (
        data.no_api_key_read is True
        and data.no_env_var_read is True
        and data.no_hardcoded_secrets is True
        and data.api_key_read_requested is not True
        and data.env_var_read_requested is not True
        and data.hardcoded_secret_detected is not True
        and not _has_upstream_risk(data, "API_KEY", "SECRET", "CREDENTIAL")
    )


def _metric_score(explicit: int | None, passed: bool, unknown: int = 40) -> int:
    if explicit is not None:
        return _clamp(explicit)
    return _bool_score(passed, unknown=unknown)


def _finding(
    name: str,
    score: int,
    passed: bool,
    risks: tuple[PaperBrokerReadOnlyPreparationRisk, ...] = (),
    details: tuple[str, ...] = (),
) -> ReadOnlyPreparationFinding:
    return ReadOnlyPreparationFinding(name=name, score=_clamp(score), passed=passed, risks=_dedupe(risks), details=details)


def validate_multi_scenario_robustness_readiness(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> bool:
    data = _coerce_input(data)
    result = data.multi_scenario_result_report
    if result is None or data.multi_scenario_robustness_approved is False:
        return False
    approved_state = _state_contains(
        result,
        "READY_FOR_PAPER_BROKER_READ_ONLY_PREPARATION",
        "APPROVE_MULTI_SCENARIO_RESULT_REPORT_ROBUSTNESS_REVIEW",
    )
    approved = data.multi_scenario_robustness_approved is True or approved_state
    return (
        approved
        and not _contains(_get(result, "risks", ()), "MULTI_SCENARIO_ROBUSTNESS_WEAK", "REAL_EXECUTION", "DATA_ACCESS")
        and not _has_upstream_risk(data, "PAPER_BROKER_READ_ONLY_PREPARATION_PREMATURE")
    )


def define_read_only_preparation_scope(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> ReadOnlyPreparationScope:
    data = _coerce_input(data)
    passed = data.read_only_scope_defined is True and data.preparation_only is True
    score = _metric_score(data.read_only_scope_score, passed)
    risks = () if passed else (PaperBrokerReadOnlyPreparationRisk.READ_ONLY_SCOPE_UNCLEAR,)
    return ReadOnlyPreparationScope(
        score=score,
        defined=data.read_only_scope_defined is True,
        preparation_only=data.preparation_only is True,
        allowed_actions=(
            "document_read_only_scope",
            "prepare_safety_review_inputs",
            "define_offline_policies",
        ),
        prohibited_actions=(
            "broker_connection",
            "api_key_read",
            "order_execution",
            "position_mutation",
            "account_write",
        ),
        risks=risks,
        details=("preparation_only", "future_safety_review_only"),
    )


def define_broker_environment_boundaries(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> BrokerEnvironmentBoundary:
    data = _coerce_input(data)
    boundary_ok = _offline_boundary(data)
    passed = data.broker_environment_boundaries_defined is True and boundary_ok
    risks: list[PaperBrokerReadOnlyPreparationRisk] = []
    if data.broker_environment_boundaries_defined is not True:
        risks.append(PaperBrokerReadOnlyPreparationRisk.BROKER_ENVIRONMENT_BOUNDARY_MISSING)
    if not boundary_ok:
        risks.append(PaperBrokerReadOnlyPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    score = _metric_score(data.broker_environment_boundary_score, passed)
    return BrokerEnvironmentBoundary(
        score=score,
        defined=data.broker_environment_boundaries_defined is True,
        offline_only=data.offline_mode_enforced is True,
        sandbox_only=data.sandbox_mode_enforced is True,
        broker_connection_disabled=data.broker_connection_disabled is True,
        network_transport_disabled=(
            data.no_http_transport is True
            and data.no_websocket_transport is True
            and data.no_socket_transport is True
            and data.network_transport_requested is not True
        ),
        risks=_dedupe(risks),
        details=("offline_sandbox_preparation", "no_connection_attempts"),
    )


def define_read_only_permission_policy(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> ReadOnlyPermissionPolicy:
    data = _coerce_input(data)
    write_blocked = (
        data.order_execution_blocked is True
        and data.position_mutation_blocked is True
        and data.account_active_access_blocked is True
        and data.no_real_order is True
        and data.no_position_mutation is True
        and data.no_real_account_access is True
    )
    passed = data.read_only_permission_policy_defined is True and write_blocked
    risks = () if passed else (PaperBrokerReadOnlyPreparationRisk.READ_ONLY_PERMISSION_POLICY_MISSING,)
    score = _metric_score(data.read_only_permission_policy_score, passed)
    return ReadOnlyPermissionPolicy(
        score=score,
        defined=data.read_only_permission_policy_defined is True,
        read_only_permissions=("metadata_review", "policy_review", "observability_schema_review"),
        write_permissions_blocked=("submit_order", "cancel_order", "mutate_position", "mutate_account", "read_secret"),
        risks=risks,
        details=("deny_all_writes", "allow_only_offline_policy_review"),
    )


def define_credentials_handling_policy(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> CredentialsHandlingPolicy:
    data = _coerce_input(data)
    credentials_ok = _credentials_boundary(data)
    risks: list[PaperBrokerReadOnlyPreparationRisk] = []
    if data.credentials_handling_policy_defined is not True or not credentials_ok:
        risks.append(PaperBrokerReadOnlyPreparationRisk.CREDENTIAL_HANDLING_POLICY_MISSING)
    if data.no_hardcoded_secrets is not True or data.hardcoded_secret_detected is True:
        risks.append(PaperBrokerReadOnlyPreparationRisk.HARDCODED_SECRET_RISK)
    passed = not risks
    score = _metric_score(data.credentials_handling_policy_score, passed)
    return CredentialsHandlingPolicy(
        score=score,
        defined=data.credentials_handling_policy_defined is True,
        no_api_key_read=data.no_api_key_read is True and data.api_key_read_requested is not True,
        no_env_var_read=data.no_env_var_read is True and data.env_var_read_requested is not True,
        no_hardcoded_secrets=data.no_hardcoded_secrets is True and data.hardcoded_secret_detected is not True,
        secret_source="none_in_this_phase",
        risks=_dedupe(risks),
        details=("no_env_read", "no_api_key_read", "no_hardcoded_secret"),
    )


def define_no_order_execution_policy(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> NoOrderExecutionPolicy:
    data = _coerce_input(data)
    passed = (
        data.no_order_execution_policy_defined is True
        and data.order_execution_blocked is True
        and data.no_real_order is True
        and data.order_execution_requested is not True
        and not _has_upstream_risk(data, "ORDER_EXECUTION", "REAL_ORDER", "EXECUTION_LEAK")
    )
    score = _metric_score(data.no_order_execution_policy_score, passed)
    risks = () if passed else (PaperBrokerReadOnlyPreparationRisk.ORDER_EXECUTION_NOT_BLOCKED,)
    return NoOrderExecutionPolicy(
        score=score,
        defined=data.no_order_execution_policy_defined is True,
        order_execution_blocked=data.order_execution_blocked is True and data.order_execution_requested is not True,
        real_order_blocked=data.no_real_order is True,
        position_mutation_blocked=data.position_mutation_blocked is True,
        risks=risks,
        details=("submit_order_disabled", "cancel_order_disabled", "replace_order_disabled"),
    )


def define_no_position_mutation_policy(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> NoOrderExecutionPolicy:
    data = _coerce_input(data)
    passed = (
        data.no_position_mutation_policy_defined is True
        and data.position_mutation_blocked is True
        and data.no_position_mutation is True
        and data.position_mutation_requested is not True
        and not _has_upstream_risk(data, "POSITION_MUTATION", "POSITION_WRITE", "POSITION_UPDATE")
    )
    score = _metric_score(data.no_position_mutation_policy_score, passed)
    risks = () if passed else (PaperBrokerReadOnlyPreparationRisk.POSITION_MUTATION_NOT_BLOCKED,)
    return NoOrderExecutionPolicy(
        name="no_position_mutation_policy",
        score=score,
        defined=data.no_position_mutation_policy_defined is True,
        order_execution_blocked=data.order_execution_blocked is True,
        real_order_blocked=data.no_real_order is True,
        position_mutation_blocked=data.position_mutation_blocked is True and data.position_mutation_requested is not True,
        risks=risks,
        details=("position_create_update_close_disabled",),
    )


def define_account_read_only_policy(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> AccountReadOnlyPolicy:
    data = _coerce_input(data)
    passed = (
        data.account_read_only_policy_defined is True
        and data.account_active_access_blocked is True
        and data.no_real_account_access is True
        and data.account_access_requested is not True
        and not _has_upstream_risk(data, "ACCOUNT_WRITE", "REAL_ACCOUNT", "ACCOUNT_ACCESS")
    )
    score = _metric_score(data.account_read_only_policy_score, passed)
    risks = () if passed else (PaperBrokerReadOnlyPreparationRisk.ACCOUNT_READ_ONLY_POLICY_MISSING,)
    return AccountReadOnlyPolicy(
        score=score,
        defined=data.account_read_only_policy_defined is True,
        active_account_access_blocked=data.account_active_access_blocked is True and data.account_access_requested is not True,
        mutations_blocked=data.no_real_account_access is True,
        risks=risks,
        details=("no_active_account_access", "no_account_mutation"),
    )


def define_market_data_read_only_policy(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> MarketDataReadOnlyPolicy:
    data = _coerce_input(data)
    passed = (
        data.market_data_read_only_policy_defined is True
        and data.market_data_live_subscription_blocked is True
        and data.network_transport_requested is not True
        and not _has_upstream_risk(data, "MARKET_DATA_WRITE", "LIVE_SUBSCRIPTION", "WEBSOCKET", "HTTP")
    )
    score = _metric_score(data.market_data_read_only_policy_score, passed)
    risks = () if passed else (PaperBrokerReadOnlyPreparationRisk.MARKET_DATA_READ_ONLY_POLICY_MISSING,)
    return MarketDataReadOnlyPolicy(
        score=score,
        defined=data.market_data_read_only_policy_defined is True,
        read_only_market_data_planned=True,
        live_subscription_disabled=data.market_data_live_subscription_blocked is True,
        risks=risks,
        details=("future_read_only_market_data_planning_only", "no_live_subscription_in_this_phase"),
    )


def define_mock_to_paper_boundary_policy(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> PaperVsRealBoundaryPolicy:
    data = _coerce_input(data)
    passed = data.mock_to_paper_boundary_defined is True and not _has_upstream_risk(data, "MOCK_TO_PAPER_BOUNDARY")
    score = _metric_score(data.mock_to_paper_boundary_score, passed)
    risks = () if passed else (PaperBrokerReadOnlyPreparationRisk.MOCK_TO_PAPER_BOUNDARY_UNCLEAR,)
    return PaperVsRealBoundaryPolicy(
        name="mock_to_paper_boundary_policy",
        score=score,
        defined=data.mock_to_paper_boundary_defined is True,
        mock_boundary_defined=data.mock_to_paper_boundary_defined is True,
        paper_boundary_defined=data.paper_vs_real_boundary_defined is True,
        real_boundary_blocked=data.no_real_broker is True,
        risks=risks,
        details=("mock_outputs_are_inputs_only", "paper_connection_not_attempted"),
    )


def define_paper_vs_real_boundary_policy(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> PaperVsRealBoundaryPolicy:
    data = _coerce_input(data)
    risks: list[PaperBrokerReadOnlyPreparationRisk] = []
    if data.paper_vs_real_boundary_defined is not True:
        risks.append(PaperBrokerReadOnlyPreparationRisk.PAPER_REAL_BOUNDARY_UNCLEAR)
    if (
        data.no_real_broker is not True
        or data.no_alpaca_real is not True
        or data.no_real_account_access is not True
        or data.real_execution_requested is True
    ):
        risks.append(PaperBrokerReadOnlyPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    score = _metric_score(data.paper_vs_real_boundary_score, not risks)
    return PaperVsRealBoundaryPolicy(
        score=score,
        defined=data.paper_vs_real_boundary_defined is True,
        mock_boundary_defined=data.mock_to_paper_boundary_defined is True,
        paper_boundary_defined=data.paper_vs_real_boundary_defined is True,
        real_boundary_blocked=data.no_real_broker is True and data.no_alpaca_real is True,
        risks=_dedupe(risks),
        details=("paper_is_future_read_only_only", "real_is_explicitly_blocked"),
    )


def define_observability_preparation_policy(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> ReadOnlyPreparationFinding:
    data = _coerce_input(data)
    passed = data.observability_preparation_policy_defined is True and not _has_upstream_risk(data, "OBSERVABILITY")
    score = _metric_score(data.observability_preparation_policy_score, passed)
    risks = () if passed else (PaperBrokerReadOnlyPreparationRisk.OBSERVABILITY_POLICY_MISSING,)
    return _finding("observability_preparation_policy", score, passed, risks, ("offline_audit_events_only",))


def define_journal_preparation_policy(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> ReadOnlyPreparationFinding:
    data = _coerce_input(data)
    passed = data.journal_preparation_policy_defined is True and not _has_upstream_risk(data, "JOURNAL")
    score = _metric_score(data.journal_preparation_policy_score, passed)
    risks = () if passed else (PaperBrokerReadOnlyPreparationRisk.JOURNAL_POLICY_MISSING,)
    return _finding("journal_preparation_policy", score, passed, risks, ("read_only_preparation_decisions_logged_offline",))


def define_human_approval_policy(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> ReadOnlyPreparationFinding:
    data = _coerce_input(data)
    passed = data.human_approval_policy_defined is True and not _has_upstream_risk(data, "HUMAN_APPROVAL", "SUPERVISION")
    score = _metric_score(data.human_approval_policy_score, passed)
    risks = () if passed else (PaperBrokerReadOnlyPreparationRisk.HUMAN_APPROVAL_POLICY_MISSING,)
    return _finding("human_approval_policy", score, passed, risks, ("explicit_human_approval_required_before_safety_review",))


def define_stop_conditions_policy(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> ReadOnlyPreparationFinding:
    data = _coerce_input(data)
    passed = data.stop_conditions_policy_defined is True
    score = _metric_score(data.stop_conditions_policy_score, passed)
    risks = () if passed else (PaperBrokerReadOnlyPreparationRisk.PREMATURE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW,)
    return _finding(
        "stop_conditions_policy",
        score,
        passed,
        risks,
        ("stop_if_network_or_credentials_or_order_path_requested",),
    )


def _all_policy_objects(data: PaperBrokerReadOnlyPreparationInput) -> tuple[Any, ...]:
    return (
        define_read_only_preparation_scope(data),
        define_broker_environment_boundaries(data),
        define_read_only_permission_policy(data),
        define_credentials_handling_policy(data),
        define_no_order_execution_policy(data),
        define_no_position_mutation_policy(data),
        define_account_read_only_policy(data),
        define_market_data_read_only_policy(data),
        define_mock_to_paper_boundary_policy(data),
        define_paper_vs_real_boundary_policy(data),
        define_observability_preparation_policy(data),
        define_journal_preparation_policy(data),
        define_human_approval_policy(data),
        define_stop_conditions_policy(data),
    )


def compute_read_only_preparation_score(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyPreparationScore:
    data = _coerce_input(data)
    robustness_passed = validate_multi_scenario_robustness_readiness(data)
    upstream_score = data.multi_scenario_robustness_score
    if upstream_score is None:
        upstream_score = _get(data.multi_scenario_result_report, "report_score")
    robustness_score = _metric_score(upstream_score, robustness_passed)
    scope = define_read_only_preparation_scope(data)
    boundary = define_broker_environment_boundaries(data)
    permission = define_read_only_permission_policy(data)
    credentials = define_credentials_handling_policy(data)
    orders = define_no_order_execution_policy(data)
    positions = define_no_position_mutation_policy(data)
    account = define_account_read_only_policy(data)
    market_data = define_market_data_read_only_policy(data)
    mock_boundary = define_mock_to_paper_boundary_policy(data)
    paper_real = define_paper_vs_real_boundary_policy(data)
    observability = define_observability_preparation_policy(data)
    journal = define_journal_preparation_policy(data)
    human = define_human_approval_policy(data)
    stops = define_stop_conditions_policy(data)
    component_scores = (
        robustness_score,
        scope.score,
        boundary.score,
        permission.score,
        credentials.score,
        orders.score,
        positions.score,
        account.score,
        market_data.score,
        mock_boundary.score,
        paper_real.score,
        observability.score,
        journal.score,
        human.score,
        stops.score,
    )
    return PaperBrokerReadOnlyPreparationScore(
        overall_score=_average(component_scores),
        multi_scenario_robustness_score=robustness_score,
        scope_score=scope.score,
        boundary_score=boundary.score,
        permission_policy_score=permission.score,
        credential_policy_score=credentials.score,
        no_order_policy_score=orders.score,
        no_position_mutation_policy_score=positions.score,
        account_read_only_score=account.score,
        market_data_read_only_score=market_data.score,
        mock_to_paper_boundary_score=mock_boundary.score,
        paper_vs_real_boundary_score=paper_real.score,
        observability_score=observability.score,
        journal_score=journal.score,
        human_approval_score=human.score,
        stop_conditions_score=stops.score,
    )


def detect_read_only_preparation_risks(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyPreparationRisk, ...]:
    data = _coerce_input(data)
    risks: list[PaperBrokerReadOnlyPreparationRisk] = []
    if not validate_multi_scenario_robustness_readiness(data):
        risks.append(PaperBrokerReadOnlyPreparationRisk.MULTI_SCENARIO_ROBUSTNESS_NOT_APPROVED)
    for policy in _all_policy_objects(data):
        risks.extend(_as_tuple(_get(policy, "risks", ())))
    if not _offline_boundary(data):
        risks.append(PaperBrokerReadOnlyPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(PaperBrokerReadOnlyPreparationRisk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_safety_review_requested is True and risks:
        risks.append(PaperBrokerReadOnlyPreparationRisk.PREMATURE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW)
    return _dedupe(risks)


def generate_read_only_preparation_recommendations(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyPreparationRecommendation, ...]:
    risks = detect_read_only_preparation_risks(data)
    if not risks:
        return (
            PaperBrokerReadOnlyPreparationRecommendation.RUN_PAPER_BROKER_READ_ONLY_PREPARATION_SUITE,
            PaperBrokerReadOnlyPreparationRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW,
        )
    mapping = {
        PaperBrokerReadOnlyPreparationRisk.MULTI_SCENARIO_ROBUSTNESS_NOT_APPROVED: PaperBrokerReadOnlyPreparationRecommendation.APPROVE_MULTI_SCENARIO_ROBUSTNESS_FIRST,
        PaperBrokerReadOnlyPreparationRisk.READ_ONLY_SCOPE_UNCLEAR: PaperBrokerReadOnlyPreparationRecommendation.CLARIFY_READ_ONLY_SCOPE,
        PaperBrokerReadOnlyPreparationRisk.BROKER_ENVIRONMENT_BOUNDARY_MISSING: PaperBrokerReadOnlyPreparationRecommendation.DEFINE_BROKER_ENVIRONMENT_BOUNDARIES,
        PaperBrokerReadOnlyPreparationRisk.READ_ONLY_PERMISSION_POLICY_MISSING: PaperBrokerReadOnlyPreparationRecommendation.DEFINE_READ_ONLY_PERMISSION_POLICY,
        PaperBrokerReadOnlyPreparationRisk.CREDENTIAL_HANDLING_POLICY_MISSING: PaperBrokerReadOnlyPreparationRecommendation.DEFINE_CREDENTIALS_HANDLING_POLICY,
        PaperBrokerReadOnlyPreparationRisk.HARDCODED_SECRET_RISK: PaperBrokerReadOnlyPreparationRecommendation.REMOVE_HARDCODED_SECRET,
        PaperBrokerReadOnlyPreparationRisk.ORDER_EXECUTION_NOT_BLOCKED: PaperBrokerReadOnlyPreparationRecommendation.BLOCK_ORDER_EXECUTION,
        PaperBrokerReadOnlyPreparationRisk.POSITION_MUTATION_NOT_BLOCKED: PaperBrokerReadOnlyPreparationRecommendation.BLOCK_POSITION_MUTATION,
        PaperBrokerReadOnlyPreparationRisk.ACCOUNT_READ_ONLY_POLICY_MISSING: PaperBrokerReadOnlyPreparationRecommendation.DEFINE_ACCOUNT_READ_ONLY_POLICY,
        PaperBrokerReadOnlyPreparationRisk.MARKET_DATA_READ_ONLY_POLICY_MISSING: PaperBrokerReadOnlyPreparationRecommendation.DEFINE_MARKET_DATA_READ_ONLY_POLICY,
        PaperBrokerReadOnlyPreparationRisk.MOCK_TO_PAPER_BOUNDARY_UNCLEAR: PaperBrokerReadOnlyPreparationRecommendation.CLARIFY_MOCK_TO_PAPER_BOUNDARY,
        PaperBrokerReadOnlyPreparationRisk.PAPER_REAL_BOUNDARY_UNCLEAR: PaperBrokerReadOnlyPreparationRecommendation.CLARIFY_PAPER_REAL_BOUNDARY,
        PaperBrokerReadOnlyPreparationRisk.OBSERVABILITY_POLICY_MISSING: PaperBrokerReadOnlyPreparationRecommendation.DEFINE_OBSERVABILITY_PREPARATION_POLICY,
        PaperBrokerReadOnlyPreparationRisk.JOURNAL_POLICY_MISSING: PaperBrokerReadOnlyPreparationRecommendation.DEFINE_JOURNAL_PREPARATION_POLICY,
        PaperBrokerReadOnlyPreparationRisk.HUMAN_APPROVAL_POLICY_MISSING: PaperBrokerReadOnlyPreparationRecommendation.REQUIRE_HUMAN_APPROVAL,
        PaperBrokerReadOnlyPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: PaperBrokerReadOnlyPreparationRecommendation.RESTORE_OFFLINE_BOUNDARIES,
        PaperBrokerReadOnlyPreparationRisk.DATA_ACCESS_VIOLATION: PaperBrokerReadOnlyPreparationRecommendation.REMOVE_DATA_ACCESS,
        PaperBrokerReadOnlyPreparationRisk.PREMATURE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW: PaperBrokerReadOnlyPreparationRecommendation.DELAY_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW,
    }
    recommendations = [PaperBrokerReadOnlyPreparationRecommendation.HOLD_PAPER_BROKER_READ_ONLY_PREPARATION]
    recommendations.extend(mapping[risk] for risk in risks if risk in mapping)
    if PaperBrokerReadOnlyPreparationRisk.PREMATURE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW in risks:
        recommendations.append(PaperBrokerReadOnlyPreparationRecommendation.DEFINE_STOP_CONDITIONS)
    return _dedupe(recommendations)


def _decision_for_risks(
    risks: tuple[PaperBrokerReadOnlyPreparationRisk, ...],
) -> PaperBrokerReadOnlyPreparationDecision:
    if not risks:
        return PaperBrokerReadOnlyPreparationDecision.APPROVE_PAPER_BROKER_READ_ONLY_PREPARATION
    if PaperBrokerReadOnlyPreparationRisk.MULTI_SCENARIO_ROBUSTNESS_NOT_APPROVED in risks:
        return PaperBrokerReadOnlyPreparationDecision.REQUIRE_MULTI_SCENARIO_ROBUSTNESS_FIXES
    if PaperBrokerReadOnlyPreparationRisk.READ_ONLY_SCOPE_UNCLEAR in risks:
        return PaperBrokerReadOnlyPreparationDecision.REQUIRE_SCOPE_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyPreparationRisk.CREDENTIAL_HANDLING_POLICY_MISSING,
            PaperBrokerReadOnlyPreparationRisk.HARDCODED_SECRET_RISK,
        )
    ):
        return PaperBrokerReadOnlyPreparationDecision.REQUIRE_CREDENTIAL_POLICY_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyPreparationRisk.ORDER_EXECUTION_NOT_BLOCKED,
            PaperBrokerReadOnlyPreparationRisk.POSITION_MUTATION_NOT_BLOCKED,
        )
    ):
        return PaperBrokerReadOnlyPreparationDecision.REQUIRE_NO_ORDER_POLICY_FIXES
    if PaperBrokerReadOnlyPreparationRisk.READ_ONLY_PERMISSION_POLICY_MISSING in risks:
        return PaperBrokerReadOnlyPreparationDecision.REQUIRE_PERMISSION_POLICY_FIXES
    if PaperBrokerReadOnlyPreparationRisk.ACCOUNT_READ_ONLY_POLICY_MISSING in risks:
        return PaperBrokerReadOnlyPreparationDecision.REQUIRE_ACCOUNT_READ_ONLY_FIXES
    if PaperBrokerReadOnlyPreparationRisk.MARKET_DATA_READ_ONLY_POLICY_MISSING in risks:
        return PaperBrokerReadOnlyPreparationDecision.REQUIRE_MARKET_DATA_READ_ONLY_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyPreparationRisk.MOCK_TO_PAPER_BOUNDARY_UNCLEAR,
            PaperBrokerReadOnlyPreparationRisk.PAPER_REAL_BOUNDARY_UNCLEAR,
        )
    ):
        return PaperBrokerReadOnlyPreparationDecision.REQUIRE_PAPER_REAL_BOUNDARY_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyPreparationRisk.BROKER_ENVIRONMENT_BOUNDARY_MISSING,
            PaperBrokerReadOnlyPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,
            PaperBrokerReadOnlyPreparationRisk.DATA_ACCESS_VIOLATION,
        )
    ):
        return PaperBrokerReadOnlyPreparationDecision.REQUIRE_BOUNDARY_FIXES
    if PaperBrokerReadOnlyPreparationRisk.HUMAN_APPROVAL_POLICY_MISSING in risks:
        return PaperBrokerReadOnlyPreparationDecision.REQUIRE_HUMAN_APPROVAL_FIXES
    return PaperBrokerReadOnlyPreparationDecision.BLOCK_PAPER_BROKER_READ_ONLY_PREPARATION


def _state_for_result(
    data: PaperBrokerReadOnlyPreparationInput,
    risks: tuple[PaperBrokerReadOnlyPreparationRisk, ...],
    score: PaperBrokerReadOnlyPreparationScore,
) -> PaperBrokerReadOnlyPreparationState:
    if data.multi_scenario_result_report is None:
        return PaperBrokerReadOnlyPreparationState.PREPARATION_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return PaperBrokerReadOnlyPreparationState.READY_FOR_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW
    if risks:
        return PaperBrokerReadOnlyPreparationState.READ_ONLY_PREPARATION_BLOCKED
    if score.overall_score >= 70:
        return PaperBrokerReadOnlyPreparationState.READ_ONLY_PREPARATION_COMPLETED_WITH_WARNINGS
    return PaperBrokerReadOnlyPreparationState.NOT_READY


def _build_findings(data: PaperBrokerReadOnlyPreparationInput) -> tuple[ReadOnlyPreparationFinding, ...]:
    scope = define_read_only_preparation_scope(data)
    boundary = define_broker_environment_boundaries(data)
    permission = define_read_only_permission_policy(data)
    credentials = define_credentials_handling_policy(data)
    orders = define_no_order_execution_policy(data)
    positions = define_no_position_mutation_policy(data)
    account = define_account_read_only_policy(data)
    market = define_market_data_read_only_policy(data)
    mock_boundary = define_mock_to_paper_boundary_policy(data)
    paper_real = define_paper_vs_real_boundary_policy(data)
    return (
        _finding(scope.name, scope.score, not scope.risks and scope.defined, scope.risks, scope.details),
        _finding(boundary.name, boundary.score, not boundary.risks and boundary.defined, boundary.risks, boundary.details),
        _finding(permission.name, permission.score, not permission.risks and permission.defined, permission.risks, permission.details),
        _finding(credentials.name, credentials.score, not credentials.risks and credentials.defined, credentials.risks, credentials.details),
        _finding(orders.name, orders.score, not orders.risks and orders.defined, orders.risks, orders.details),
        _finding(positions.name, positions.score, not positions.risks and positions.defined, positions.risks, positions.details),
        _finding(account.name, account.score, not account.risks and account.defined, account.risks, account.details),
        _finding(market.name, market.score, not market.risks and market.defined, market.risks, market.details),
        _finding(mock_boundary.name, mock_boundary.score, not mock_boundary.risks and mock_boundary.defined, mock_boundary.risks, mock_boundary.details),
        _finding(paper_real.name, paper_real.score, not paper_real.risks and paper_real.defined, paper_real.risks, paper_real.details),
        define_observability_preparation_policy(data),
        define_journal_preparation_policy(data),
        define_human_approval_policy(data),
        define_stop_conditions_policy(data),
    )


def evaluate_paper_broker_read_only_preparation(
    data: PaperBrokerReadOnlyPreparationInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyPreparationResult:
    data = _coerce_input(data)
    score = compute_read_only_preparation_score(data)
    risks = detect_read_only_preparation_risks(data)
    recommendations = generate_read_only_preparation_recommendations(data)
    decision = _decision_for_risks(risks)
    state = _state_for_result(data, risks, score)
    return PaperBrokerReadOnlyPreparationResult(
        state=state,
        decision=decision,
        preparation_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=recommendations,
        scope=define_read_only_preparation_scope(data),
        broker_environment_boundaries=define_broker_environment_boundaries(data),
        read_only_permission_policy=define_read_only_permission_policy(data),
        credentials_handling_policy=define_credentials_handling_policy(data),
        no_order_execution_policy=define_no_order_execution_policy(data),
        no_position_mutation_policy=define_no_position_mutation_policy(data),
        account_read_only_policy=define_account_read_only_policy(data),
        market_data_read_only_policy=define_market_data_read_only_policy(data),
        mock_to_paper_boundary_policy=define_mock_to_paper_boundary_policy(data),
        paper_vs_real_boundary_policy=define_paper_vs_real_boundary_policy(data),
        observability_preparation_policy=define_observability_preparation_policy(data),
        journal_preparation_policy=define_journal_preparation_policy(data),
        human_approval_policy=define_human_approval_policy(data),
        stop_conditions_policy=define_stop_conditions_policy(data),
        findings=_build_findings(data),
        offline_only=True,
        summary=(
            "Paper broker read-only preparation is approved for safety review."
            if not risks
            else "Paper broker read-only preparation is blocked until policy and boundary fixes are complete."
        ),
    )


def render_paper_broker_read_only_preparation_markdown(
    result: PaperBrokerReadOnlyPreparationResult | Mapping[str, Any],
) -> str:
    if isinstance(result, Mapping):
        result = PaperBrokerReadOnlyPreparationResult(**dict(result))
    risks = ", ".join(risk.value for risk in result.risks) or "none"
    recommendations = ", ".join(recommendation.value for recommendation in result.recommendations) or "none"
    findings = "\n".join(
        f"- {finding.name}: score={finding.score}, passed={finding.passed}, risks="
        f"{', '.join(risk.value for risk in finding.risks) or 'none'}"
        for finding in result.findings
    )
    return "\n".join(
        (
            "# Paper Broker Read-Only Preparation",
            "",
            f"- State: {result.state.value}",
            f"- Decision: {result.decision.value}",
            f"- Preparation score: {result.preparation_score}",
            f"- Offline only: {result.offline_only}",
            f"- Risks: {risks}",
            f"- Recommendations: {recommendations}",
            "",
            "## Safety Boundaries",
            "- No broker connection",
            "- No Alpaca real access",
            "- No API key or environment variable read",
            "- No HTTP, websocket, socket or external API",
            "- No order execution, position mutation or account access",
            "",
            "## Findings",
            findings,
        )
    )


__all__ = [
    "evaluate_paper_broker_read_only_preparation",
    "validate_multi_scenario_robustness_readiness",
    "define_read_only_preparation_scope",
    "define_broker_environment_boundaries",
    "define_read_only_permission_policy",
    "define_credentials_handling_policy",
    "define_no_order_execution_policy",
    "define_no_position_mutation_policy",
    "define_account_read_only_policy",
    "define_market_data_read_only_policy",
    "define_mock_to_paper_boundary_policy",
    "define_paper_vs_real_boundary_policy",
    "define_observability_preparation_policy",
    "define_journal_preparation_policy",
    "define_human_approval_policy",
    "define_stop_conditions_policy",
    "compute_read_only_preparation_score",
    "detect_read_only_preparation_risks",
    "generate_read_only_preparation_recommendations",
    "render_paper_broker_read_only_preparation_markdown",
]
