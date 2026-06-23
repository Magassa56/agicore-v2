from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_execution_plan import (
    evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_plan,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate import (
    compute_controlled_execution_safety_gate_score,
    detect_controlled_execution_safety_gate_risks,
    evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate,
    generate_controlled_execution_safety_gate_recommendations,
    render_paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate_markdown,
    validate_controlled_execution_plan_approval,
    verify_controlled_account_read_only_safety,
    verify_controlled_audit_plan_safety,
    verify_controlled_abort_policy_safety,
    verify_controlled_credentials_reference_safety,
    verify_controlled_execution_precondition_safety,
    verify_controlled_execution_scope_safety,
    verify_controlled_execution_sequence_safety,
    verify_controlled_go_no_go_policy_safety,
    verify_controlled_http_websocket_socket_block_safety,
    verify_controlled_human_approval_safety,
    verify_controlled_journal_safety,
    verify_controlled_market_data_read_only_safety,
    verify_controlled_network_block_safety,
    verify_controlled_no_secret_read_safety,
    verify_controlled_observability_safety,
    verify_controlled_order_blocking_safety,
    verify_controlled_position_mutation_block_safety,
    verify_controlled_stop_conditions_safety,
    verify_controlled_success_failure_criteria_safety,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRecommendation,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateState,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_controlled_execution_plan import (
    _ready_input as _controlled_plan_ready_input,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _controlled_plan_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_plan(_controlled_plan_ready_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_dry_run_controlled_execution_plan": _controlled_plan_result(),
        "paper_broker_read_only_connection_dry_run_execution_preparation_review": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_CONTROLLED_EXECUTION_PLAN"),
        "paper_broker_read_only_connection_dry_run_execution_preparation": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW"),
        "paper_broker_read_only_connection_dry_run_execution_safety_gate": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION"),
        "paper_broker_read_only_connection_dry_run_execution_plan": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE"),
        "paper_broker_read_only_connection_dry_run_preparation_review": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN"),
        "paper_broker_read_only_connection_dry_run_preparation": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW"),
        "paper_broker_read_only_connection_dry_run_safety_gate": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION"),
        "paper_broker_read_only_connection_dry_run_plan": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE"),
        "paper_broker_read_only_connection_preparation_review": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN"),
        "paper_broker_read_only_connection_preparation": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW"),
        "paper_broker_read_only_connection_safety_gate": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION"),
        "paper_broker_read_only_connection_plan": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE"),
        "paper_broker_read_only_safety_review": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN"),
        "paper_broker_read_only_preparation": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW"),
        "controlled_execution_plan_approved": True,
        "controlled_execution_scope_safety_verified": True,
        "controlled_execution_sequence_safety_verified": True,
        "controlled_execution_precondition_safety_verified": True,
        "controlled_credentials_reference_safety_verified": True,
        "controlled_no_secret_read_safety_verified": True,
        "controlled_network_block_safety_verified": True,
        "controlled_http_websocket_socket_block_safety_verified": True,
        "controlled_account_read_only_safety_verified": True,
        "controlled_market_data_read_only_safety_verified": True,
        "controlled_order_blocking_safety_verified": True,
        "controlled_position_mutation_block_safety_verified": True,
        "controlled_observability_safety_verified": True,
        "controlled_journal_safety_verified": True,
        "controlled_human_approval_safety_verified": True,
        "controlled_stop_conditions_safety_verified": True,
        "controlled_success_failure_criteria_safety_verified": True,
        "controlled_audit_plan_safety_verified": True,
        "controlled_go_no_go_policy_safety_verified": True,
        "controlled_abort_policy_safety_verified": True,
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
        "external_api_requested": False,
        "dry_run_requested": False,
        "dry_run_executed": False,
    }
    payload.update(overrides)
    return PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput(**payload)


def test_nominal_controlled_safety_gate_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate(_ready_input())

    assert result.state is PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE
    assert result.safety_gate_score == 100
    assert result.risks == ()
    assert result.offline_only is True
    assert result.go_no_go_policy_safety.passed is True
    assert result.abort_policy_safety.passed is True


def test_verify_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_controlled_execution_plan_approval(data) is True
    assert verify_controlled_execution_scope_safety(data).passed is True
    assert verify_controlled_execution_sequence_safety(data).passed is True
    assert verify_controlled_execution_precondition_safety(data).human_approval_required is True
    assert verify_controlled_credentials_reference_safety(data).no_api_key_read is True
    assert verify_controlled_no_secret_read_safety(data).no_env_var_read is True
    assert verify_controlled_network_block_safety(data).external_api_blocked is True
    assert verify_controlled_http_websocket_socket_block_safety(data).socket_blocked is True
    assert verify_controlled_account_read_only_safety(data).active_account_access_blocked is True
    assert verify_controlled_market_data_read_only_safety(data).network_request_blocked is True
    assert verify_controlled_order_blocking_safety(data).order_execution_blocked is True
    assert verify_controlled_position_mutation_block_safety(data).position_mutation_blocked is True
    assert verify_controlled_observability_safety(data).offline_events_defined is True
    assert verify_controlled_journal_safety(data).offline_journal_required is True
    assert verify_controlled_human_approval_safety(data).human_approval_required is True
    assert verify_controlled_stop_conditions_safety(data).stop_on_network_request is True
    assert verify_controlled_success_failure_criteria_safety(data).passed is True
    assert verify_controlled_audit_plan_safety(data).offline_evidence_required is True
    assert verify_controlled_go_no_go_policy_safety(data).human_go_required is True
    assert verify_controlled_abort_policy_safety(data).abort_on_network_request is True
    assert compute_controlled_execution_safety_gate_score(data).overall_score == 100


def test_controlled_plan_not_approved_blocks_gate():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate(
        _ready_input(
            paper_broker_read_only_connection_dry_run_controlled_execution_plan=_controlled_plan_result(
                state="CONTROLLED_EXECUTION_PLAN_BLOCKED",
                decision="REQUIRE_CONTROLLED_GO_NO_GO_FIXES",
                risks=("CONTROLLED_GO_NO_GO_POLICY_MISSING",),
            ),
            controlled_execution_plan_approved=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_EXECUTION_PLAN_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_EXECUTION_PLAN_FIXES


@pytest.mark.parametrize(
    ("overrides", "risk", "decision"),
    [
        ({"controlled_execution_scope_safety_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_EXECUTION_SCOPE_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_SCOPE_SAFETY_FIXES),
        ({"controlled_execution_sequence_safety_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_EXECUTION_SEQUENCE_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_SEQUENCE_SAFETY_FIXES),
        ({"controlled_execution_precondition_safety_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_EXECUTION_PRECONDITION_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_PRECONDITION_SAFETY_FIXES),
        ({"controlled_credentials_reference_safety_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_CREDENTIAL_POLICY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_CREDENTIAL_SAFETY_FIXES),
        ({"controlled_no_secret_read_safety_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_SECRET_READ_POLICY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_NO_SECRET_READ_FIXES),
        ({"controlled_network_block_safety_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_NETWORK_NOT_BLOCKED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_NETWORK_BLOCK_FIXES),
        ({"controlled_http_websocket_socket_block_safety_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_NETWORK_BLOCK_FIXES),
        ({"controlled_account_read_only_safety_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_ACCOUNT_READ_ONLY_FIXES),
        ({"controlled_market_data_read_only_safety_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_MARKET_DATA_READ_ONLY_FIXES),
        ({"controlled_order_blocking_safety_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_ORDER_BLOCKING_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_ORDER_BLOCKING_FIXES),
        ({"controlled_position_mutation_block_safety_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_POSITION_MUTATION_BLOCK_FIXES),
        ({"controlled_human_approval_safety_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_HUMAN_APPROVAL_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_HUMAN_APPROVAL_FIXES),
        ({"controlled_stop_conditions_safety_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_STOP_CONDITIONS_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_STOP_CONDITION_FIXES),
        ({"controlled_success_failure_criteria_safety_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_SUCCESS_FAILURE_CRITERIA_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_STOP_CONDITION_FIXES),
        ({"controlled_audit_plan_safety_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_AUDIT_PLAN_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_AUDIT_FIXES),
        ({"controlled_go_no_go_policy_safety_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_GO_NO_GO_POLICY_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_GO_NO_GO_FIXES),
        ({"controlled_abort_policy_safety_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_ABORT_POLICY_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.REQUIRE_CONTROLLED_ABORT_POLICY_FIXES),
    ],
)
def test_controlled_safety_gaps_are_enforced(overrides, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateState.CONTROLLED_EXECUTION_SAFETY_GATE_BLOCKED


@pytest.mark.parametrize(
    "overrides",
    [
        {"real_execution_requested": True},
        {"broker_connection_requested": True},
        {"api_key_read_requested": True},
        {"env_var_read_requested": True},
        {"hardcoded_secret_detected": True},
        {"network_transport_requested": True},
        {"external_api_requested": True},
        {"dry_run_requested": True},
        {"dry_run_executed": True},
        {"order_execution_requested": True},
        {"position_mutation_requested": True},
        {"account_access_requested": True},
        {"no_http_transport": False},
        {"no_websocket_transport": False},
        {"no_socket_transport": False},
    ],
)
def test_real_boundaries_are_blocked(overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate(_ready_input(**overrides))

    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE


def test_data_access_is_blocked():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate(
        _ready_input(data_access_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE


def test_premature_controlled_execution_plan_is_detected():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate(
        _ready_input(paper_broker_read_only_connection_dry_run_controlled_execution_preparation_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION in result.risks


def test_recommendations_and_markdown_are_rendered():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate(_ready_input())
    markdown = render_paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate_markdown(result)

    assert generate_controlled_execution_safety_gate_recommendations(_ready_input()) == (
        PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE_SUITE,
        PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION,
    )
    assert "Paper Broker Read-Only Connection Dry Run Controlled Execution Safety Gate" in markdown
    assert "Go/no-go policy" in markdown
    assert "data/ access: blocked" in markdown


def test_mapping_input_and_missing_plan_input():
    nominal = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate(dict(_ready_input().__dict__))
    missing = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate(None)

    assert nominal.safety_gate_score == 100
    assert missing.state is PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateState.CONTROLLED_EXECUTION_SAFETY_GATE_INPUT_INVALID
    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_EXECUTION_PLAN_NOT_APPROVED in missing.risks


def test_risk_detection_helper_returns_tuple():
    risks = detect_controlled_execution_safety_gate_risks(_ready_input(controlled_go_no_go_policy_safety_verified=False))

    assert risks == (PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk.CONTROLLED_GO_NO_GO_POLICY_MISSING,)


def test_source_has_no_real_io_or_network_imports():
    source = Path("src/agicore/trading/paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate.py").read_text()

    forbidden = ("import os", "import socket", "import requests", "from requests", "urllib", "http.client", "open(", "os.environ")
    for token in forbidden:
        assert token not in source
