from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_preparation import (
    compute_read_only_preparation_score,
    define_account_read_only_policy,
    define_broker_environment_boundaries,
    define_credentials_handling_policy,
    define_human_approval_policy,
    define_journal_preparation_policy,
    define_market_data_read_only_policy,
    define_mock_to_paper_boundary_policy,
    define_no_order_execution_policy,
    define_no_position_mutation_policy,
    define_observability_preparation_policy,
    define_paper_vs_real_boundary_policy,
    define_read_only_permission_policy,
    define_read_only_preparation_scope,
    define_stop_conditions_policy,
    detect_read_only_preparation_risks,
    evaluate_paper_broker_read_only_preparation,
    generate_read_only_preparation_recommendations,
    render_paper_broker_read_only_preparation_markdown,
    validate_multi_scenario_robustness_readiness,
)
from agicore.trading.paper_broker_read_only_preparation_models import (
    PaperBrokerReadOnlyPreparationDecision,
    PaperBrokerReadOnlyPreparationInput,
    PaperBrokerReadOnlyPreparationRecommendation,
    PaperBrokerReadOnlyPreparationRisk,
    PaperBrokerReadOnlyPreparationState,
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
        "recommendations": ("APPROVE_PAPER_BROKER_READ_ONLY_PREPARATION",),
        "offline_only": True,
    }
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
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


def test_nominal_read_only_preparation_is_approved():
    result = evaluate_paper_broker_read_only_preparation(_ready_input())

    assert result.state is PaperBrokerReadOnlyPreparationState.READY_FOR_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW
    assert result.decision is PaperBrokerReadOnlyPreparationDecision.APPROVE_PAPER_BROKER_READ_ONLY_PREPARATION
    assert result.preparation_score >= 98
    assert result.risks == ()
    assert result.offline_only is True
    assert result.scope.preparation_only is True
    assert "broker_connection" in result.scope.prohibited_actions
    assert result.no_order_execution_policy.order_execution_blocked is True
    assert result.no_position_mutation_policy.position_mutation_blocked is True
    assert result.credentials_handling_policy.secret_source == "none_in_this_phase"


def test_definition_functions_are_deterministic_and_pass_nominal_input():
    data = _ready_input()

    assert validate_multi_scenario_robustness_readiness(data) is True
    assert define_read_only_preparation_scope(data).defined is True
    assert define_broker_environment_boundaries(data).broker_connection_disabled is True
    assert define_read_only_permission_policy(data).risks == ()
    assert define_credentials_handling_policy(data).no_hardcoded_secrets is True
    assert define_no_order_execution_policy(data).risks == ()
    assert define_no_position_mutation_policy(data).risks == ()
    assert define_account_read_only_policy(data).active_account_access_blocked is True
    assert define_market_data_read_only_policy(data).live_subscription_disabled is True
    assert define_mock_to_paper_boundary_policy(data).mock_boundary_defined is True
    assert define_paper_vs_real_boundary_policy(data).real_boundary_blocked is True
    assert define_observability_preparation_policy(data).passed is True
    assert define_journal_preparation_policy(data).passed is True
    assert define_human_approval_policy(data).passed is True
    assert define_stop_conditions_policy(data).passed is True
    assert compute_read_only_preparation_score(data).overall_score >= 98


def test_non_approved_multi_scenario_robustness_blocks_preparation():
    result = evaluate_paper_broker_read_only_preparation(
        _ready_input(
            multi_scenario_result_report=_approved_multi_scenario_report(
                state="REPORT_BLOCKED",
                decision="REQUIRE_ROBUSTNESS_FIXES",
                risks=("MULTI_SCENARIO_ROBUSTNESS_WEAK",),
            ),
            multi_scenario_robustness_approved=False,
        )
    )

    assert PaperBrokerReadOnlyPreparationRisk.MULTI_SCENARIO_ROBUSTNESS_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlyPreparationDecision.REQUIRE_MULTI_SCENARIO_ROBUSTNESS_FIXES


@pytest.mark.parametrize(
    ("field", "risk", "decision"),
    [
        (
            "read_only_scope_defined",
            PaperBrokerReadOnlyPreparationRisk.READ_ONLY_SCOPE_UNCLEAR,
            PaperBrokerReadOnlyPreparationDecision.REQUIRE_SCOPE_FIXES,
        ),
        (
            "broker_environment_boundaries_defined",
            PaperBrokerReadOnlyPreparationRisk.BROKER_ENVIRONMENT_BOUNDARY_MISSING,
            PaperBrokerReadOnlyPreparationDecision.REQUIRE_BOUNDARY_FIXES,
        ),
        (
            "credentials_handling_policy_defined",
            PaperBrokerReadOnlyPreparationRisk.CREDENTIAL_HANDLING_POLICY_MISSING,
            PaperBrokerReadOnlyPreparationDecision.REQUIRE_CREDENTIAL_POLICY_FIXES,
        ),
        (
            "market_data_read_only_policy_defined",
            PaperBrokerReadOnlyPreparationRisk.MARKET_DATA_READ_ONLY_POLICY_MISSING,
            PaperBrokerReadOnlyPreparationDecision.REQUIRE_MARKET_DATA_READ_ONLY_FIXES,
        ),
        (
            "human_approval_policy_defined",
            PaperBrokerReadOnlyPreparationRisk.HUMAN_APPROVAL_POLICY_MISSING,
            PaperBrokerReadOnlyPreparationDecision.REQUIRE_HUMAN_APPROVAL_FIXES,
        ),
    ],
)
def test_missing_required_policies_are_reported(field, risk, decision):
    result = evaluate_paper_broker_read_only_preparation(_ready_input(**{field: False}))

    assert risk in result.risks
    assert result.decision is decision


def test_order_execution_not_blocked_is_rejected():
    result = evaluate_paper_broker_read_only_preparation(
        _ready_input(order_execution_blocked=False, order_execution_requested=True)
    )

    assert PaperBrokerReadOnlyPreparationRisk.ORDER_EXECUTION_NOT_BLOCKED in result.risks
    assert result.decision is PaperBrokerReadOnlyPreparationDecision.REQUIRE_NO_ORDER_POLICY_FIXES


def test_position_mutation_not_blocked_is_rejected():
    result = evaluate_paper_broker_read_only_preparation(
        _ready_input(position_mutation_blocked=False, position_mutation_requested=True)
    )

    assert PaperBrokerReadOnlyPreparationRisk.POSITION_MUTATION_NOT_BLOCKED in result.risks
    assert result.decision is PaperBrokerReadOnlyPreparationDecision.REQUIRE_NO_ORDER_POLICY_FIXES


def test_hardcoded_secret_or_credential_read_is_rejected():
    result = evaluate_paper_broker_read_only_preparation(
        _ready_input(no_hardcoded_secrets=False, hardcoded_secret_detected=True)
    )

    assert PaperBrokerReadOnlyPreparationRisk.HARDCODED_SECRET_RISK in result.risks
    assert PaperBrokerReadOnlyPreparationRisk.CREDENTIAL_HANDLING_POLICY_MISSING in result.risks
    assert result.decision is PaperBrokerReadOnlyPreparationDecision.REQUIRE_CREDENTIAL_POLICY_FIXES
    assert PaperBrokerReadOnlyPreparationRecommendation.REMOVE_HARDCODED_SECRET in result.recommendations


def test_real_execution_boundary_violation_is_rejected():
    result = evaluate_paper_broker_read_only_preparation(
        _ready_input(no_real_broker=False, broker_connection_requested=True, real_execution_requested=True)
    )

    assert PaperBrokerReadOnlyPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyPreparationDecision.REQUIRE_BOUNDARY_FIXES


def test_data_access_violation_is_rejected():
    result = evaluate_paper_broker_read_only_preparation(_ready_input(data_access_requested=True))

    assert PaperBrokerReadOnlyPreparationRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyPreparationDecision.REQUIRE_BOUNDARY_FIXES


def test_paper_real_and_mock_boundaries_are_checked():
    result = evaluate_paper_broker_read_only_preparation(
        _ready_input(mock_to_paper_boundary_defined=False, paper_vs_real_boundary_defined=False)
    )

    assert PaperBrokerReadOnlyPreparationRisk.MOCK_TO_PAPER_BOUNDARY_UNCLEAR in result.risks
    assert PaperBrokerReadOnlyPreparationRisk.PAPER_REAL_BOUNDARY_UNCLEAR in result.risks
    assert result.decision is PaperBrokerReadOnlyPreparationDecision.REQUIRE_PAPER_REAL_BOUNDARY_FIXES


def test_stop_conditions_missing_blocks_premature_safety_review():
    result = evaluate_paper_broker_read_only_preparation(
        _ready_input(stop_conditions_policy_defined=False, paper_broker_read_only_safety_review_requested=True)
    )

    assert PaperBrokerReadOnlyPreparationRisk.PREMATURE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW in result.risks
    assert PaperBrokerReadOnlyPreparationRecommendation.DELAY_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW in result.recommendations


def test_recommendations_and_markdown_for_nominal_case():
    result = evaluate_paper_broker_read_only_preparation(_ready_input())
    markdown = render_paper_broker_read_only_preparation_markdown(result)

    assert generate_read_only_preparation_recommendations(_ready_input()) == (
        PaperBrokerReadOnlyPreparationRecommendation.RUN_PAPER_BROKER_READ_ONLY_PREPARATION_SUITE,
        PaperBrokerReadOnlyPreparationRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW,
    )
    assert "Paper Broker Read-Only Preparation" in markdown
    assert "No API key or environment variable read" in markdown
    assert PaperBrokerReadOnlyPreparationDecision.APPROVE_PAPER_BROKER_READ_ONLY_PREPARATION.value in markdown


def test_mapping_input_ignores_unknown_fields_and_detects_risks():
    data = dict(_ready_input().__dict__)
    data["unknown"] = "ignored"
    data["order_execution_requested"] = True

    risks = detect_read_only_preparation_risks(data)

    assert PaperBrokerReadOnlyPreparationRisk.ORDER_EXECUTION_NOT_BLOCKED in risks


def test_module_does_not_import_network_or_secret_clients():
    source = Path("src/agicore/trading/paper_broker_read_only_preparation.py").read_text(encoding="utf-8")

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
