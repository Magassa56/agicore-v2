from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_preparation import evaluate_paper_broker_read_only_preparation
from agicore.trading.paper_broker_read_only_preparation_models import PaperBrokerReadOnlyPreparationInput
from agicore.trading.paper_broker_read_only_safety_review import (
    compute_read_only_safety_score,
    detect_read_only_safety_risks,
    evaluate_paper_broker_read_only_safety_review,
    generate_read_only_safety_recommendations,
    render_paper_broker_read_only_safety_review_markdown,
    review_account_read_only_policy,
    review_broker_environment_boundaries,
    review_credentials_handling_policy,
    review_human_approval_policy,
    review_journal_policy,
    review_market_data_read_only_policy,
    review_mock_to_paper_boundary_policy,
    review_no_order_execution_policy,
    review_no_position_mutation_policy,
    review_observability_policy,
    review_paper_vs_real_boundary_policy,
    review_read_only_permission_policy,
    review_read_only_scope,
    review_stop_conditions_policy,
    validate_read_only_preparation_approval,
)
from agicore.trading.paper_broker_read_only_safety_review_models import (
    PaperBrokerReadOnlySafetyReviewDecision,
    PaperBrokerReadOnlySafetyReviewInput,
    PaperBrokerReadOnlySafetyReviewRecommendation,
    PaperBrokerReadOnlySafetyReviewRisk,
    PaperBrokerReadOnlySafetyReviewState,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _approved_multi_scenario_report(**overrides):
    payload = {
        "state": "READY_FOR_PAPER_BROKER_READ_ONLY_PREPARATION",
        "decision": "APPROVE_MULTI_SCENARIO_RESULT_REPORT_ROBUSTNESS_REVIEW",
        "report_score": 98,
        "risks": (),
        "offline_only": True,
    }
    payload.update(overrides)
    return payload


def _preparation_input(**overrides):
    payload = {
        "multi_scenario_result_report": _approved_multi_scenario_report(),
        "multi_scenario_controlled_simulation_result": _upstream(
            "READY_FOR_MULTI_SCENARIO_RESULT_REPORT",
            "APPROVE_MULTI_SCENARIO_CONTROLLED_SIMULATION",
        ),
        "performance_risk_validation_gate": _upstream(
            "READY_FOR_MULTI_SCENARIO_CONTROLLED_SIMULATION",
            "APPROVE_PERFORMANCE_RISK_VALIDATION_GATE",
        ),
        "performance_metrics_result": _upstream("READY_FOR_RISK_METRICS_ENGINE", "APPROVE_PERFORMANCE_METRICS_ENGINE"),
        "risk_metrics_result": _upstream("READY_FOR_PERFORMANCE_RISK_VALIDATION_GATE", "APPROVE_RISK_METRICS_ENGINE"),
        "controlled_simulation_result_report": _upstream("READY_FOR_PERFORMANCE_METRICS_ENGINE"),
        "controlled_simulation_offline_runner_result": _upstream("READY_FOR_CONTROLLED_SIMULATION_RESULT_REPORT"),
        "paper_runtime_forward_test_plan": _upstream("READY_FOR_PAPER_BROKER_SANDBOX_SESSION"),
        "official_paper_validation_report": _upstream("READY_FOR_SUPERVISED_PAPER_RUNTIME_TRIAL"),
        "paper_runtime_validation": _upstream("READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT"),
        "paper_trading_runtime": _upstream("COMPLETED"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "multi_scenario_robustness_approved": True,
        "read_only_scope_defined": True,
        "broker_environment_boundaries_defined": True,
        "read_only_permission_policy_defined": True,
        "credentials_handling_policy_defined": True,
        "no_hardcoded_secrets": True,
        "no_env_var_read": True,
        "no_order_execution_policy_defined": True,
        "order_execution_blocked": True,
        "no_position_mutation_policy_defined": True,
        "position_mutation_blocked": True,
        "account_read_only_policy_defined": True,
        "account_active_access_blocked": True,
        "market_data_read_only_policy_defined": True,
        "market_data_live_subscription_blocked": True,
        "mock_to_paper_boundary_defined": True,
        "paper_vs_real_boundary_defined": True,
        "observability_preparation_policy_defined": True,
        "journal_preparation_policy_defined": True,
        "human_approval_policy_defined": True,
        "stop_conditions_policy_defined": True,
        "paper_broker_read_only_safety_review_requested": False,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "preparation_only": True,
        "broker_connection_disabled": True,
        "no_real_broker": True,
        "no_alpaca_real": True,
        "no_api_key_read": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_api": True,
        "no_external_ml": True,
        "no_external_llm": True,
        "no_live_execution": True,
        "no_real_order": True,
        "no_position_mutation": True,
        "no_real_account_access": True,
        "data_access_requested": False,
        "real_execution_requested": False,
        "broker_connection_requested": False,
        "api_key_read_requested": False,
        "env_var_read_requested": False,
        "hardcoded_secret_detected": False,
        "order_execution_requested": False,
        "position_mutation_requested": False,
        "account_access_requested": False,
        "network_transport_requested": False,
    }
    payload.update(overrides)
    return PaperBrokerReadOnlyPreparationInput(**payload)


def _preparation_result(**overrides):
    result = evaluate_paper_broker_read_only_preparation(_preparation_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_preparation": _preparation_result(),
        "multi_scenario_result_report": _approved_multi_scenario_report(),
        "multi_scenario_controlled_simulation_result": _upstream(
            "READY_FOR_MULTI_SCENARIO_RESULT_REPORT",
            "APPROVE_MULTI_SCENARIO_CONTROLLED_SIMULATION",
        ),
        "performance_risk_validation_gate": _upstream(
            "READY_FOR_MULTI_SCENARIO_CONTROLLED_SIMULATION",
            "APPROVE_PERFORMANCE_RISK_VALIDATION_GATE",
        ),
        "performance_metrics_result": _upstream("READY_FOR_RISK_METRICS_ENGINE", "APPROVE_PERFORMANCE_METRICS_ENGINE"),
        "risk_metrics_result": _upstream("READY_FOR_PERFORMANCE_RISK_VALIDATION_GATE", "APPROVE_RISK_METRICS_ENGINE"),
        "controlled_simulation_result_report": _upstream("READY_FOR_PERFORMANCE_METRICS_ENGINE"),
        "controlled_simulation_offline_runner_result": _upstream("READY_FOR_CONTROLLED_SIMULATION_RESULT_REPORT"),
        "paper_runtime_forward_test_plan": _upstream("READY_FOR_PAPER_BROKER_SANDBOX_SESSION"),
        "official_paper_validation_report": _upstream("READY_FOR_SUPERVISED_PAPER_RUNTIME_TRIAL"),
        "paper_runtime_validation": _upstream("READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT"),
        "paper_trading_runtime": _upstream("COMPLETED"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "read_only_preparation_approved": True,
        "read_only_scope_reviewed": True,
        "broker_environment_boundaries_reviewed": True,
        "read_only_permission_policy_reviewed": True,
        "credentials_handling_policy_reviewed": True,
        "no_hardcoded_secrets": True,
        "no_env_var_read": True,
        "no_api_key_read": True,
        "no_order_execution_policy_reviewed": True,
        "order_execution_blocked": True,
        "no_position_mutation_policy_reviewed": True,
        "position_mutation_blocked": True,
        "account_read_only_policy_reviewed": True,
        "account_active_access_blocked": True,
        "account_mutations_blocked": True,
        "market_data_read_only_policy_reviewed": True,
        "market_data_live_subscription_blocked": True,
        "mock_to_paper_boundary_reviewed": True,
        "paper_vs_real_boundary_reviewed": True,
        "observability_policy_reviewed": True,
        "journal_policy_reviewed": True,
        "human_approval_policy_reviewed": True,
        "stop_conditions_policy_reviewed": True,
        "paper_broker_read_only_connection_plan_requested": False,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "safety_review_only": True,
        "broker_connection_disabled": True,
        "no_real_broker": True,
        "no_alpaca_real": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_api": True,
        "no_external_ml": True,
        "no_external_llm": True,
        "no_live_execution": True,
        "no_real_order": True,
        "no_position_mutation": True,
        "no_real_account_access": True,
        "data_access_requested": False,
        "real_execution_requested": False,
        "broker_connection_requested": False,
        "api_key_read_requested": False,
        "env_var_read_requested": False,
        "hardcoded_secret_detected": False,
        "order_execution_requested": False,
        "position_mutation_requested": False,
        "account_access_requested": False,
        "network_transport_requested": False,
    }
    payload.update(overrides)
    return PaperBrokerReadOnlySafetyReviewInput(**payload)


def test_nominal_safety_review_is_approved():
    result = evaluate_paper_broker_read_only_safety_review(_ready_input())

    assert result.state is PaperBrokerReadOnlySafetyReviewState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN
    assert result.decision is PaperBrokerReadOnlySafetyReviewDecision.APPROVE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW
    assert result.safety_score == 100
    assert result.risks == ()
    assert result.offline_only is True
    assert result.credentials_handling_review.no_api_key_read is True
    assert result.credentials_handling_review.no_env_var_read is True
    assert result.order_blocking_review.order_execution_blocked is True
    assert result.position_mutation_review.position_mutation_blocked is True


def test_review_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_read_only_preparation_approval(data) is True
    assert review_read_only_scope(data).passed is True
    assert review_broker_environment_boundaries(data).passed is True
    assert review_read_only_permission_policy(data).passed is True
    assert review_credentials_handling_policy(data).passed is True
    assert review_no_order_execution_policy(data).passed is True
    assert review_no_position_mutation_policy(data).passed is True
    assert review_account_read_only_policy(data).passed is True
    assert review_market_data_read_only_policy(data).passed is True
    assert review_mock_to_paper_boundary_policy(data).passed is True
    assert review_paper_vs_real_boundary_policy(data).passed is True
    assert review_observability_policy(data).passed is True
    assert review_journal_policy(data).passed is True
    assert review_human_approval_policy(data).passed is True
    assert review_stop_conditions_policy(data).passed is True
    assert compute_read_only_safety_score(data).overall_score == 100


def test_preparation_not_approved_blocks_safety_review():
    result = evaluate_paper_broker_read_only_safety_review(
        _ready_input(
            paper_broker_read_only_preparation=_preparation_result(
                state="READ_ONLY_PREPARATION_BLOCKED",
                decision="REQUIRE_BOUNDARY_FIXES",
                risks=("REAL_EXECUTION_BOUNDARY_VIOLATION",),
            ),
            read_only_preparation_approved=False,
        )
    )

    assert PaperBrokerReadOnlySafetyReviewRisk.READ_ONLY_PREPARATION_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_READ_ONLY_PREPARATION_FIXES


@pytest.mark.parametrize(
    ("field", "risk", "decision"),
    [
        (
            "read_only_scope_reviewed",
            PaperBrokerReadOnlySafetyReviewRisk.READ_ONLY_SCOPE_UNCLEAR,
            PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_SCOPE_FIXES,
        ),
        (
            "broker_environment_boundaries_reviewed",
            PaperBrokerReadOnlySafetyReviewRisk.BROKER_ENVIRONMENT_BOUNDARY_UNSAFE,
            PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_BOUNDARY_FIXES,
        ),
        (
            "read_only_permission_policy_reviewed",
            PaperBrokerReadOnlySafetyReviewRisk.READ_ONLY_PERMISSION_POLICY_UNSAFE,
            PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_PERMISSION_POLICY_FIXES,
        ),
        (
            "human_approval_policy_reviewed",
            PaperBrokerReadOnlySafetyReviewRisk.HUMAN_APPROVAL_POLICY_INCOMPLETE,
            PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_HUMAN_APPROVAL_FIXES,
        ),
    ],
)
def test_required_review_sections_are_enforced(field, risk, decision):
    result = evaluate_paper_broker_read_only_safety_review(_ready_input(**{field: False}))

    assert risk in result.risks
    assert result.decision is decision


def test_credential_api_key_read_is_unsafe():
    result = evaluate_paper_broker_read_only_safety_review(_ready_input(api_key_read_requested=True))

    assert PaperBrokerReadOnlySafetyReviewRisk.CREDENTIAL_HANDLING_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_CREDENTIAL_POLICY_FIXES


def test_hardcoded_secret_is_rejected():
    result = evaluate_paper_broker_read_only_safety_review(
        _ready_input(no_hardcoded_secrets=False, hardcoded_secret_detected=True)
    )

    assert PaperBrokerReadOnlySafetyReviewRisk.HARDCODED_SECRET_RISK in result.risks
    assert PaperBrokerReadOnlySafetyReviewRecommendation.REMOVE_HARDCODED_SECRET in result.recommendations


def test_environment_variable_read_is_rejected():
    result = evaluate_paper_broker_read_only_safety_review(
        _ready_input(no_env_var_read=False, env_var_read_requested=True)
    )

    assert PaperBrokerReadOnlySafetyReviewRisk.ENVIRONMENT_VARIABLE_READ_RISK in result.risks
    assert PaperBrokerReadOnlySafetyReviewRecommendation.BLOCK_ENVIRONMENT_VARIABLE_READ in result.recommendations


def test_order_execution_not_blocked_is_rejected():
    result = evaluate_paper_broker_read_only_safety_review(
        _ready_input(order_execution_blocked=False, order_execution_requested=True)
    )

    assert PaperBrokerReadOnlySafetyReviewRisk.ORDER_EXECUTION_NOT_BLOCKED in result.risks
    assert result.decision is PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_NO_ORDER_POLICY_FIXES


def test_position_mutation_not_blocked_is_rejected():
    result = evaluate_paper_broker_read_only_safety_review(
        _ready_input(position_mutation_blocked=False, position_mutation_requested=True)
    )

    assert PaperBrokerReadOnlySafetyReviewRisk.POSITION_MUTATION_NOT_BLOCKED in result.risks
    assert result.decision is PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_POSITION_MUTATION_FIXES


def test_account_policy_unsafe_is_rejected():
    result = evaluate_paper_broker_read_only_safety_review(
        _ready_input(account_active_access_blocked=False, account_access_requested=True)
    )

    assert PaperBrokerReadOnlySafetyReviewRisk.ACCOUNT_READ_ONLY_POLICY_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_ACCOUNT_READ_ONLY_FIXES


def test_market_data_policy_unsafe_is_rejected():
    result = evaluate_paper_broker_read_only_safety_review(
        _ready_input(market_data_live_subscription_blocked=False, network_transport_requested=True)
    )

    assert PaperBrokerReadOnlySafetyReviewRisk.MARKET_DATA_READ_ONLY_POLICY_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_MARKET_DATA_READ_ONLY_FIXES


def test_mock_and_paper_real_boundaries_are_enforced():
    result = evaluate_paper_broker_read_only_safety_review(
        _ready_input(mock_to_paper_boundary_reviewed=False, paper_vs_real_boundary_reviewed=False)
    )

    assert PaperBrokerReadOnlySafetyReviewRisk.MOCK_TO_PAPER_BOUNDARY_UNSAFE in result.risks
    assert PaperBrokerReadOnlySafetyReviewRisk.PAPER_REAL_BOUNDARY_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_MOCK_PAPER_BOUNDARY_FIXES


def test_real_execution_boundary_violation_is_rejected():
    result = evaluate_paper_broker_read_only_safety_review(
        _ready_input(no_real_broker=False, broker_connection_requested=True, real_execution_requested=True)
    )

    assert PaperBrokerReadOnlySafetyReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_PAPER_REAL_BOUNDARY_FIXES


def test_data_access_violation_is_rejected():
    result = evaluate_paper_broker_read_only_safety_review(_ready_input(data_access_requested=True))

    assert PaperBrokerReadOnlySafetyReviewRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_BOUNDARY_FIXES


def test_premature_connection_plan_request_is_rejected():
    result = evaluate_paper_broker_read_only_safety_review(
        _ready_input(paper_broker_read_only_connection_plan_requested=True)
    )

    assert PaperBrokerReadOnlySafetyReviewRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN in result.risks
    assert PaperBrokerReadOnlySafetyReviewRecommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN in result.recommendations


def test_recommendations_and_markdown_for_nominal_case():
    data = _ready_input()
    result = evaluate_paper_broker_read_only_safety_review(data)
    markdown = render_paper_broker_read_only_safety_review_markdown(result)

    assert generate_read_only_safety_recommendations(data) == (
        PaperBrokerReadOnlySafetyReviewRecommendation.RUN_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW_SUITE,
        PaperBrokerReadOnlySafetyReviewRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN,
    )
    assert "Paper Broker Read-Only Safety Review" in markdown
    assert "No API key or environment variable read" in markdown
    assert PaperBrokerReadOnlySafetyReviewDecision.APPROVE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW.value in markdown


def test_mapping_input_ignores_unknown_fields_and_detects_risks():
    data = dict(_ready_input().__dict__)
    data["unknown"] = "ignored"
    data["order_execution_requested"] = True

    risks = detect_read_only_safety_risks(data)

    assert PaperBrokerReadOnlySafetyReviewRisk.ORDER_EXECUTION_NOT_BLOCKED in risks


def test_module_does_not_import_network_secret_or_environment_clients():
    source = Path("src/agicore/trading/paper_broker_read_only_safety_review.py").read_text(encoding="utf-8")

    forbidden_imports = (
        "import requests",
        "from requests",
        "import urllib",
        "from urllib",
        "import httpx",
        "import aiohttp",
        "import websockets",
        "import socket",
        "import os",
    )
    assert all(pattern not in source for pattern in forbidden_imports)
