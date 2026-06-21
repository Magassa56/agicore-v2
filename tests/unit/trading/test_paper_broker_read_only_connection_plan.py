from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_plan import (
    compute_read_only_connection_plan_score,
    define_account_read_only_connection_policy,
    define_connection_environment_boundaries,
    define_connection_human_approval_plan,
    define_connection_journal_plan,
    define_connection_observability_plan,
    define_connection_preconditions,
    define_connection_stop_conditions_plan,
    define_credentials_reference_policy,
    define_http_websocket_socket_block_policy,
    define_market_data_read_only_connection_policy,
    define_network_execution_block_policy,
    define_no_secret_read_policy,
    define_order_blocking_connection_policy,
    define_position_mutation_block_policy,
    define_read_only_connection_scope,
    detect_read_only_connection_plan_risks,
    evaluate_paper_broker_read_only_connection_plan,
    generate_read_only_connection_plan_recommendations,
    render_paper_broker_read_only_connection_plan_markdown,
    validate_read_only_safety_review_approval,
)
from agicore.trading.paper_broker_read_only_connection_plan_models import (
    PaperBrokerReadOnlyConnectionPlanDecision,
    PaperBrokerReadOnlyConnectionPlanInput,
    PaperBrokerReadOnlyConnectionPlanRecommendation,
    PaperBrokerReadOnlyConnectionPlanRisk,
    PaperBrokerReadOnlyConnectionPlanState,
)
from agicore.trading.paper_broker_read_only_safety_review import evaluate_paper_broker_read_only_safety_review
from tests.unit.trading.test_paper_broker_read_only_safety_review import _ready_input as _safety_ready_input


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _safety_result(**overrides):
    result = evaluate_paper_broker_read_only_safety_review(_safety_ready_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_safety_review": _safety_result(),
        "paper_broker_read_only_preparation": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW",
            "APPROVE_PAPER_BROKER_READ_ONLY_PREPARATION",
        ),
        "multi_scenario_result_report": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_PREPARATION",
            "APPROVE_MULTI_SCENARIO_RESULT_REPORT_ROBUSTNESS_REVIEW",
        ),
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
        "read_only_safety_review_approved": True,
        "read_only_connection_scope_defined": True,
        "connection_environment_boundaries_defined": True,
        "connection_preconditions_defined": True,
        "credentials_reference_policy_defined": True,
        "credentials_reference_only": True,
        "no_secret_read_policy_defined": True,
        "secret_read_blocked": True,
        "network_execution_block_policy_defined": True,
        "network_execution_blocked": True,
        "http_websocket_socket_block_policy_defined": True,
        "http_transport_blocked": True,
        "websocket_transport_blocked": True,
        "socket_transport_blocked": True,
        "account_read_only_connection_policy_defined": True,
        "account_active_access_blocked": True,
        "account_mutations_blocked": True,
        "market_data_read_only_connection_policy_defined": True,
        "market_data_live_subscription_blocked": True,
        "order_blocking_connection_policy_defined": True,
        "order_execution_blocked": True,
        "position_mutation_block_policy_defined": True,
        "position_mutation_blocked": True,
        "connection_observability_plan_defined": True,
        "connection_journal_plan_defined": True,
        "connection_human_approval_plan_defined": True,
        "connection_stop_conditions_plan_defined": True,
        "paper_broker_read_only_connection_safety_gate_requested": False,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "plan_only": True,
        "broker_connection_disabled": True,
        "no_real_broker": True,
        "no_alpaca_real": True,
        "no_api_key_read": True,
        "no_env_var_read": True,
        "no_hardcoded_secrets": True,
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
    return PaperBrokerReadOnlyConnectionPlanInput(**payload)


def test_nominal_connection_plan_is_approved():
    result = evaluate_paper_broker_read_only_connection_plan(_ready_input())

    assert result.state is PaperBrokerReadOnlyConnectionPlanState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE
    assert result.decision is PaperBrokerReadOnlyConnectionPlanDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN
    assert result.connection_plan_score == 100
    assert result.risks == ()
    assert result.offline_only is True
    assert result.credentials_reference_policy.reference_only is True
    assert result.no_secret_read_policy.no_api_key_read is True
    assert result.network_execution_block_policy.network_execution_blocked is True
    assert result.http_websocket_socket_block_policy.socket_blocked is True


def test_definition_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_read_only_safety_review_approval(data) is True
    assert define_read_only_connection_scope(data).defined is True
    assert define_connection_environment_boundaries(data).connection_execution_disabled is True
    assert define_connection_preconditions(data).safety_review_required is True
    assert define_credentials_reference_policy(data).reference_only is True
    assert define_no_secret_read_policy(data).risks == ()
    assert define_network_execution_block_policy(data).risks == ()
    assert define_http_websocket_socket_block_policy(data).http_blocked is True
    assert define_account_read_only_connection_policy(data).active_account_access_blocked is True
    assert define_market_data_read_only_connection_policy(data).live_subscription_blocked is True
    assert define_order_blocking_connection_policy(data).order_execution_blocked is True
    assert define_position_mutation_block_policy(data).risks == ()
    assert define_connection_observability_plan(data).defined is True
    assert define_connection_journal_plan(data).defined is True
    assert define_connection_human_approval_plan(data).defined is True
    assert define_connection_stop_conditions_plan(data).defined is True
    assert compute_read_only_connection_plan_score(data).overall_score == 100


def test_safety_review_not_approved_blocks_connection_plan():
    result = evaluate_paper_broker_read_only_connection_plan(
        _ready_input(
            paper_broker_read_only_safety_review=_safety_result(
                state="SAFETY_REVIEW_BLOCKED",
                decision="REQUIRE_BOUNDARY_FIXES",
                risks=("REAL_EXECUTION_BOUNDARY_VIOLATION",),
            ),
            read_only_safety_review_approved=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionPlanRisk.READ_ONLY_SAFETY_REVIEW_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_READ_ONLY_SAFETY_REVIEW_FIXES


@pytest.mark.parametrize(
    ("field", "risk", "decision"),
    [
        (
            "read_only_connection_scope_defined",
            PaperBrokerReadOnlyConnectionPlanRisk.READ_ONLY_CONNECTION_SCOPE_UNCLEAR,
            PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_SCOPE_FIXES,
        ),
        (
            "connection_environment_boundaries_defined",
            PaperBrokerReadOnlyConnectionPlanRisk.CONNECTION_ENVIRONMENT_BOUNDARY_MISSING,
            PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_BOUNDARY_FIXES,
        ),
        (
            "connection_preconditions_defined",
            PaperBrokerReadOnlyConnectionPlanRisk.CONNECTION_PRECONDITION_MISSING,
            PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_PRECONDITION_FIXES,
        ),
    ],
)
def test_required_plan_sections_are_enforced(field, risk, decision):
    result = evaluate_paper_broker_read_only_connection_plan(_ready_input(**{field: False}))

    assert risk in result.risks
    assert result.decision is decision


def test_credential_reference_policy_missing_is_rejected():
    result = evaluate_paper_broker_read_only_connection_plan(
        _ready_input(credentials_reference_policy_defined=False, credentials_reference_only=False)
    )

    assert PaperBrokerReadOnlyConnectionPlanRisk.CREDENTIAL_REFERENCE_POLICY_MISSING in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_CREDENTIAL_REFERENCE_POLICY_FIXES


def test_secret_read_policy_unsafe_is_rejected():
    result = evaluate_paper_broker_read_only_connection_plan(
        _ready_input(no_secret_read_policy_defined=False, secret_read_blocked=False, api_key_read_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionPlanRisk.SECRET_READ_POLICY_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_CREDENTIAL_REFERENCE_POLICY_FIXES


def test_network_execution_not_blocked_is_rejected():
    result = evaluate_paper_broker_read_only_connection_plan(
        _ready_input(network_execution_blocked=False, broker_connection_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionPlanRisk.NETWORK_EXECUTION_NOT_BLOCKED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_NETWORK_BLOCK_POLICY_FIXES


def test_http_websocket_socket_not_blocked_is_rejected():
    result = evaluate_paper_broker_read_only_connection_plan(
        _ready_input(
            http_transport_blocked=False,
            websocket_transport_blocked=False,
            socket_transport_blocked=False,
            no_http_transport=False,
            no_websocket_transport=False,
            no_socket_transport=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionPlanRisk.HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_NETWORK_BLOCK_POLICY_FIXES


def test_order_blocking_policy_unsafe_is_rejected():
    result = evaluate_paper_broker_read_only_connection_plan(
        _ready_input(order_execution_blocked=False, order_execution_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionPlanRisk.ORDER_BLOCKING_CONNECTION_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_ORDER_BLOCKING_FIXES


def test_position_mutation_block_policy_unsafe_is_rejected():
    result = evaluate_paper_broker_read_only_connection_plan(
        _ready_input(position_mutation_blocked=False, position_mutation_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionPlanRisk.POSITION_MUTATION_BLOCK_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_POSITION_MUTATION_BLOCK_FIXES


def test_account_read_only_connection_policy_unsafe_is_rejected():
    result = evaluate_paper_broker_read_only_connection_plan(
        _ready_input(account_active_access_blocked=False, account_access_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionPlanRisk.ACCOUNT_READ_ONLY_CONNECTION_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_ACCOUNT_READ_ONLY_FIXES


def test_market_data_read_only_connection_policy_unsafe_is_rejected():
    result = evaluate_paper_broker_read_only_connection_plan(_ready_input(market_data_live_subscription_blocked=False))

    assert PaperBrokerReadOnlyConnectionPlanRisk.MARKET_DATA_READ_ONLY_CONNECTION_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_MARKET_DATA_READ_ONLY_FIXES


def test_data_access_violation_is_rejected():
    result = evaluate_paper_broker_read_only_connection_plan(_ready_input(data_access_requested=True))

    assert PaperBrokerReadOnlyConnectionPlanRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_BOUNDARY_FIXES


def test_real_execution_boundary_violation_is_rejected():
    result = evaluate_paper_broker_read_only_connection_plan(
        _ready_input(no_real_broker=False, real_execution_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_BOUNDARY_FIXES


def test_premature_safety_gate_request_is_rejected():
    result = evaluate_paper_broker_read_only_connection_plan(
        _ready_input(paper_broker_read_only_connection_safety_gate_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionPlanRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE in result.risks
    assert (
        PaperBrokerReadOnlyConnectionPlanRecommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE
        in result.recommendations
    )


def test_recommendations_and_markdown_for_nominal_case():
    data = _ready_input()
    result = evaluate_paper_broker_read_only_connection_plan(data)
    markdown = render_paper_broker_read_only_connection_plan_markdown(result)

    assert generate_read_only_connection_plan_recommendations(data) == (
        PaperBrokerReadOnlyConnectionPlanRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN_SUITE,
        PaperBrokerReadOnlyConnectionPlanRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE,
    )
    assert "Paper Broker Read-Only Connection Plan" in markdown
    assert "No API key or environment variable read" in markdown
    assert PaperBrokerReadOnlyConnectionPlanDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN.value in markdown


def test_mapping_input_ignores_unknown_fields_and_detects_risks():
    data = dict(_ready_input().__dict__)
    data["unknown"] = "ignored"
    data["network_transport_requested"] = True

    risks = detect_read_only_connection_plan_risks(data)

    assert PaperBrokerReadOnlyConnectionPlanRisk.NETWORK_EXECUTION_NOT_BLOCKED in risks


def test_module_does_not_import_network_secret_or_environment_clients():
    source = Path("src/agicore/trading/paper_broker_read_only_connection_plan.py").read_text(encoding="utf-8")

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
