from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_plan import evaluate_paper_broker_read_only_connection_plan
from agicore.trading.paper_broker_read_only_connection_safety_gate import (
    compute_read_only_connection_safety_gate_score,
    detect_read_only_connection_safety_gate_risks,
    evaluate_paper_broker_read_only_connection_safety_gate,
    generate_read_only_connection_safety_gate_recommendations,
    render_paper_broker_read_only_connection_safety_gate_markdown,
    validate_read_only_connection_plan_approval,
    verify_account_read_only_connection_safety,
    verify_connection_environment_boundary_safety,
    verify_connection_precondition_safety,
    verify_connection_scope_safety,
    verify_credentials_reference_safety,
    verify_http_websocket_socket_block_safety,
    verify_human_approval_connection_safety,
    verify_journal_connection_safety,
    verify_market_data_read_only_connection_safety,
    verify_network_execution_block_safety,
    verify_no_secret_read_safety,
    verify_observability_connection_safety,
    verify_order_blocking_connection_safety,
    verify_position_mutation_block_safety,
    verify_stop_conditions_connection_safety,
)
from agicore.trading.paper_broker_read_only_connection_safety_gate_models import (
    PaperBrokerReadOnlyConnectionSafetyGateDecision,
    PaperBrokerReadOnlyConnectionSafetyGateInput,
    PaperBrokerReadOnlyConnectionSafetyGateRecommendation,
    PaperBrokerReadOnlyConnectionSafetyGateRisk,
    PaperBrokerReadOnlyConnectionSafetyGateState,
)
from tests.unit.trading.test_paper_broker_read_only_connection_plan import _ready_input as _plan_ready_input


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _connection_plan_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_plan(_plan_ready_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_plan": _connection_plan_result(),
        "paper_broker_read_only_safety_review": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN",
            "APPROVE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW",
        ),
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
        "read_only_connection_plan_approved": True,
        "connection_scope_safety_verified": True,
        "connection_environment_boundary_safety_verified": True,
        "connection_precondition_safety_verified": True,
        "credentials_reference_safety_verified": True,
        "no_secret_read_safety_verified": True,
        "network_execution_block_safety_verified": True,
        "http_websocket_socket_block_safety_verified": True,
        "account_read_only_connection_safety_verified": True,
        "market_data_read_only_connection_safety_verified": True,
        "order_blocking_connection_safety_verified": True,
        "position_mutation_block_safety_verified": True,
        "observability_connection_safety_verified": True,
        "journal_connection_safety_verified": True,
        "human_approval_connection_safety_verified": True,
        "stop_conditions_connection_safety_verified": True,
        "paper_broker_read_only_connection_preparation_requested": False,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "safety_gate_only": True,
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
    return PaperBrokerReadOnlyConnectionSafetyGateInput(**payload)


def test_nominal_connection_safety_gate_is_approved():
    result = evaluate_paper_broker_read_only_connection_safety_gate(_ready_input())

    assert result.state is PaperBrokerReadOnlyConnectionSafetyGateState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION
    assert result.decision is PaperBrokerReadOnlyConnectionSafetyGateDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE
    assert result.safety_gate_score == 100
    assert result.risks == ()
    assert result.offline_only is True
    assert result.credential_reference_safety.no_api_key_read is True
    assert result.network_block_safety.network_execution_blocked is True
    assert result.order_blocking_safety.order_execution_blocked is True
    assert result.position_mutation_block_safety.position_mutation_blocked is True


def test_verification_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_read_only_connection_plan_approval(data) is True
    assert verify_connection_scope_safety(data).passed is True
    assert verify_connection_environment_boundary_safety(data).passed is True
    assert verify_connection_precondition_safety(data).passed is True
    assert verify_credentials_reference_safety(data).passed is True
    assert verify_no_secret_read_safety(data).passed is True
    assert verify_network_execution_block_safety(data).passed is True
    assert verify_http_websocket_socket_block_safety(data).passed is True
    assert verify_account_read_only_connection_safety(data).passed is True
    assert verify_market_data_read_only_connection_safety(data).passed is True
    assert verify_order_blocking_connection_safety(data).passed is True
    assert verify_position_mutation_block_safety(data).passed is True
    assert verify_observability_connection_safety(data).passed is True
    assert verify_journal_connection_safety(data).passed is True
    assert verify_human_approval_connection_safety(data).passed is True
    assert verify_stop_conditions_connection_safety(data).passed is True
    assert compute_read_only_connection_safety_gate_score(data).overall_score == 100


def test_connection_plan_not_approved_blocks_gate():
    result = evaluate_paper_broker_read_only_connection_safety_gate(
        _ready_input(
            paper_broker_read_only_connection_plan=_connection_plan_result(
                state="CONNECTION_PLAN_BLOCKED",
                decision="REQUIRE_BOUNDARY_FIXES",
                risks=("REAL_EXECUTION_BOUNDARY_VIOLATION",),
            ),
            read_only_connection_plan_approved=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionSafetyGateRisk.READ_ONLY_CONNECTION_PLAN_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_CONNECTION_PLAN_FIXES


@pytest.mark.parametrize(
    ("field", "risk", "decision"),
    [
        (
            "connection_scope_safety_verified",
            PaperBrokerReadOnlyConnectionSafetyGateRisk.CONNECTION_SCOPE_UNSAFE,
            PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_SCOPE_SAFETY_FIXES,
        ),
        (
            "connection_environment_boundary_safety_verified",
            PaperBrokerReadOnlyConnectionSafetyGateRisk.CONNECTION_ENVIRONMENT_BOUNDARY_UNSAFE,
            PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_BOUNDARY_SAFETY_FIXES,
        ),
        (
            "connection_precondition_safety_verified",
            PaperBrokerReadOnlyConnectionSafetyGateRisk.CONNECTION_PRECONDITION_UNSAFE,
            PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_PRECONDITION_SAFETY_FIXES,
        ),
    ],
)
def test_required_safety_sections_are_enforced(field, risk, decision):
    result = evaluate_paper_broker_read_only_connection_safety_gate(_ready_input(**{field: False}))

    assert risk in result.risks
    assert result.decision is decision


def test_credential_reference_unsafe_is_rejected():
    result = evaluate_paper_broker_read_only_connection_safety_gate(
        _ready_input(credentials_reference_safety_verified=False)
    )

    assert PaperBrokerReadOnlyConnectionSafetyGateRisk.CREDENTIAL_REFERENCE_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_CREDENTIAL_REFERENCE_FIXES


def test_secret_read_unsafe_is_rejected():
    result = evaluate_paper_broker_read_only_connection_safety_gate(
        _ready_input(no_secret_read_safety_verified=False)
    )

    assert PaperBrokerReadOnlyConnectionSafetyGateRisk.SECRET_READ_POLICY_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_SECRET_READ_BLOCK_FIXES


def test_hardcoded_secret_and_env_read_are_rejected():
    result = evaluate_paper_broker_read_only_connection_safety_gate(
        _ready_input(no_hardcoded_secrets=False, hardcoded_secret_detected=True, env_var_read_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionSafetyGateRisk.SECRET_READ_POLICY_UNSAFE in result.risks
    assert PaperBrokerReadOnlyConnectionSafetyGateRecommendation.HARDEN_SECRET_READ_BLOCK in result.recommendations


def test_network_execution_not_blocked_is_rejected():
    result = evaluate_paper_broker_read_only_connection_safety_gate(
        _ready_input(network_execution_block_safety_verified=False, broker_connection_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionSafetyGateRisk.NETWORK_EXECUTION_NOT_BLOCKED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_NETWORK_BLOCK_FIXES


def test_http_websocket_socket_not_blocked_is_rejected():
    result = evaluate_paper_broker_read_only_connection_safety_gate(
        _ready_input(
            http_websocket_socket_block_safety_verified=False,
            no_http_transport=False,
            no_websocket_transport=False,
            no_socket_transport=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionSafetyGateRisk.HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_NETWORK_BLOCK_FIXES


def test_order_blocking_unsafe_is_rejected():
    result = evaluate_paper_broker_read_only_connection_safety_gate(
        _ready_input(order_blocking_connection_safety_verified=False, order_execution_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionSafetyGateRisk.ORDER_BLOCKING_CONNECTION_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_ORDER_BLOCKING_FIXES


def test_position_mutation_block_unsafe_is_rejected():
    result = evaluate_paper_broker_read_only_connection_safety_gate(
        _ready_input(position_mutation_block_safety_verified=False, position_mutation_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionSafetyGateRisk.POSITION_MUTATION_BLOCK_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_POSITION_MUTATION_BLOCK_FIXES


def test_account_read_only_unsafe_is_rejected():
    result = evaluate_paper_broker_read_only_connection_safety_gate(
        _ready_input(account_read_only_connection_safety_verified=False, account_access_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionSafetyGateRisk.ACCOUNT_READ_ONLY_CONNECTION_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_ACCOUNT_READ_ONLY_FIXES


def test_market_data_read_only_unsafe_is_rejected():
    result = evaluate_paper_broker_read_only_connection_safety_gate(
        _ready_input(market_data_read_only_connection_safety_verified=False)
    )

    assert PaperBrokerReadOnlyConnectionSafetyGateRisk.MARKET_DATA_READ_ONLY_CONNECTION_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_MARKET_DATA_READ_ONLY_FIXES


def test_human_approval_missing_is_rejected():
    result = evaluate_paper_broker_read_only_connection_safety_gate(
        _ready_input(human_approval_connection_safety_verified=False)
    )

    assert PaperBrokerReadOnlyConnectionSafetyGateRisk.HUMAN_APPROVAL_CONNECTION_MISSING in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_HUMAN_APPROVAL_FIXES


def test_real_execution_boundary_violation_is_rejected():
    result = evaluate_paper_broker_read_only_connection_safety_gate(
        _ready_input(no_real_broker=False, real_execution_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_BOUNDARY_SAFETY_FIXES


def test_data_access_violation_is_rejected():
    result = evaluate_paper_broker_read_only_connection_safety_gate(_ready_input(data_access_requested=True))

    assert PaperBrokerReadOnlyConnectionSafetyGateRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_BOUNDARY_SAFETY_FIXES


def test_premature_connection_preparation_request_is_rejected():
    result = evaluate_paper_broker_read_only_connection_safety_gate(
        _ready_input(paper_broker_read_only_connection_preparation_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionSafetyGateRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION in result.risks
    assert (
        PaperBrokerReadOnlyConnectionSafetyGateRecommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION
        in result.recommendations
    )


def test_recommendations_and_markdown_for_nominal_case():
    data = _ready_input()
    result = evaluate_paper_broker_read_only_connection_safety_gate(data)
    markdown = render_paper_broker_read_only_connection_safety_gate_markdown(result)

    assert generate_read_only_connection_safety_gate_recommendations(data) == (
        PaperBrokerReadOnlyConnectionSafetyGateRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE_SUITE,
        PaperBrokerReadOnlyConnectionSafetyGateRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION,
    )
    assert "Paper Broker Read-Only Connection Safety Gate" in markdown
    assert "No API key or environment variable read" in markdown
    assert PaperBrokerReadOnlyConnectionSafetyGateDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE.value in markdown


def test_mapping_input_ignores_unknown_fields_and_detects_risks():
    data = dict(_ready_input().__dict__)
    data["unknown"] = "ignored"
    data["network_transport_requested"] = True

    risks = detect_read_only_connection_safety_gate_risks(data)

    assert PaperBrokerReadOnlyConnectionSafetyGateRisk.NETWORK_EXECUTION_NOT_BLOCKED in risks


def test_module_does_not_import_network_secret_or_environment_clients():
    source = Path("src/agicore/trading/paper_broker_read_only_connection_safety_gate.py").read_text(encoding="utf-8")

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
