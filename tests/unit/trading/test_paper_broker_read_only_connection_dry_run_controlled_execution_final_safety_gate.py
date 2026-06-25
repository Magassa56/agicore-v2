from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_execution_final_plan import (
    evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_final_plan,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate import (
    compute_final_safety_gate_score,
    detect_final_safety_gate_risks,
    evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate,
    generate_final_safety_gate_recommendations,
    render_paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate_markdown,
    validate_final_controlled_execution_plan_approval,
    validate_final_safety_abort_boundary,
    validate_final_safety_account_read_only_boundary,
    validate_final_safety_audit_boundary,
    validate_final_safety_consistency_observation_boundary,
    validate_final_safety_credentials_boundary,
    validate_final_safety_go_no_go_boundary,
    validate_final_safety_http_websocket_socket_block_boundary,
    validate_final_safety_human_approval_boundary,
    validate_final_safety_journal_boundary,
    validate_final_safety_market_data_read_only_boundary,
    validate_final_safety_network_block_boundary,
    validate_final_safety_no_secret_read_boundary,
    validate_final_safety_observability_boundary,
    validate_final_safety_offline_sandbox_boundary,
    validate_final_safety_order_blocking_boundary,
    validate_final_safety_position_mutation_blocking_boundary,
    validate_final_safety_profitability_observation_boundary,
    validate_final_safety_runtime_boundary,
    validate_final_safety_stop_conditions_boundary,
    validate_final_safety_success_failure_boundary,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateDecision as Decision,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateInput,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateRecommendation as Recommendation,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateRisk as Risk,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateState as State,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_controlled_execution_final_plan import (
    _ready_input as _final_plan_ready_input,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _final_plan_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_final_plan(_final_plan_ready_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_dry_run_controlled_execution_final_plan": _final_plan_result(),
        "paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN"),
        "paper_broker_read_only_connection_dry_run_controlled_execution_preparation": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW"),
        "paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION"),
        "paper_broker_read_only_connection_dry_run_controlled_execution_plan": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE"),
        "paper_broker_read_only_connection_dry_run_execution_final_safety_gate": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN"),
        "paper_broker_read_only_connection_dry_run_execution_final_plan": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE"),
        "paper_broker_read_only_connection_dry_run_execution_preparation_review": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN"),
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
        "final_controlled_execution_plan_approved": True,
        "final_safety_runtime_boundary_verified": True,
        "final_safety_offline_sandbox_boundary_verified": True,
        "final_safety_credentials_boundary_verified": True,
        "final_safety_no_secret_read_boundary_verified": True,
        "final_safety_network_block_boundary_verified": True,
        "final_safety_http_websocket_socket_block_boundary_verified": True,
        "final_safety_account_read_only_boundary_verified": True,
        "final_safety_market_data_read_only_boundary_verified": True,
        "final_safety_order_blocking_boundary_verified": True,
        "final_safety_position_mutation_blocking_boundary_verified": True,
        "final_safety_observability_boundary_verified": True,
        "final_safety_journal_boundary_verified": True,
        "final_safety_human_approval_boundary_verified": True,
        "final_safety_stop_conditions_boundary_verified": True,
        "final_safety_success_failure_boundary_verified": True,
        "final_safety_audit_boundary_verified": True,
        "final_safety_go_no_go_boundary_verified": True,
        "final_safety_abort_boundary_verified": True,
        "final_safety_profitability_observation_boundary_verified": True,
        "final_safety_consistency_observation_boundary_verified": True,
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
    return PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateInput(**payload)

def test_nominal_final_safety_gate_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate(_ready_input())

    assert result.state is State.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN
    assert result.decision is Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE
    assert result.safety_gate_score == 100
    assert result.risks == ()
    assert result.offline_only is True
    assert result.profitability_observation_boundary.no_profit_promise is True
    assert result.consistency_observation_boundary.observation_only is True


def test_validate_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_final_controlled_execution_plan_approval(data) is True
    assert validate_final_safety_runtime_boundary(data).dry_run_not_executed is True
    assert validate_final_safety_offline_sandbox_boundary(data).offline_only is True
    assert validate_final_safety_credentials_boundary(data).no_api_key_read is True
    assert validate_final_safety_no_secret_read_boundary(data).no_env_var_read is True
    assert validate_final_safety_network_block_boundary(data).external_api_blocked is True
    assert validate_final_safety_http_websocket_socket_block_boundary(data).socket_blocked is True
    assert validate_final_safety_account_read_only_boundary(data).active_account_access_blocked is True
    assert validate_final_safety_market_data_read_only_boundary(data).network_request_blocked is True
    assert validate_final_safety_order_blocking_boundary(data).order_execution_blocked is True
    assert validate_final_safety_position_mutation_blocking_boundary(data).position_mutation_blocked is True
    assert validate_final_safety_observability_boundary(data).offline_events_defined is True
    assert validate_final_safety_journal_boundary(data).offline_journal_required is True
    assert validate_final_safety_human_approval_boundary(data).human_approval_required is True
    assert validate_final_safety_stop_conditions_boundary(data).stop_on_network_request is True
    assert validate_final_safety_success_failure_boundary(data).failure_on_boundary_violation is True
    assert validate_final_safety_audit_boundary(data).offline_evidence_required is True
    assert validate_final_safety_go_no_go_boundary(data).human_go_required is True
    assert validate_final_safety_abort_boundary(data).abort_on_boundary_violation is True
    assert validate_final_safety_profitability_observation_boundary(data).no_profit_promise is True
    assert validate_final_safety_consistency_observation_boundary(data).deterministic_checks_required is True
    assert compute_final_safety_gate_score(data).overall_score == 100


def test_final_plan_not_approved_blocks_gate():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate(
        _ready_input(
            paper_broker_read_only_connection_dry_run_controlled_execution_final_plan=_final_plan_result(
                state="FINAL_CONTROLLED_EXECUTION_PLAN_BLOCKED",
                decision="REQUIRE_FINAL_CONTROLLED_GO_NO_GO_FIXES",
                risks=("FINAL_CONTROLLED_GO_NO_GO_POLICY_MISSING",),
            ),
            final_controlled_execution_plan_approved=False,
        )
    )

    assert Risk.FINAL_CONTROLLED_EXECUTION_PLAN_NOT_APPROVED in result.risks
    assert result.decision is Decision.REQUIRE_FINAL_CONTROLLED_EXECUTION_PLAN_FIXES


@pytest.mark.parametrize(
    ("overrides", "risk", "decision"),
    [
        ({"final_safety_runtime_boundary_verified": False}, Risk.FINAL_SAFETY_RUNTIME_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_RUNTIME_BOUNDARY_FIXES),
        ({"final_safety_offline_sandbox_boundary_verified": False}, Risk.FINAL_SAFETY_OFFLINE_SANDBOX_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_OFFLINE_SANDBOX_FIXES),
        ({"final_safety_credentials_boundary_verified": False}, Risk.FINAL_SAFETY_CREDENTIAL_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_CREDENTIAL_BOUNDARY_FIXES),
        ({"final_safety_no_secret_read_boundary_verified": False}, Risk.FINAL_SAFETY_SECRET_READ_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_NO_SECRET_READ_FIXES),
        ({"final_safety_network_block_boundary_verified": False}, Risk.FINAL_SAFETY_NETWORK_BLOCK_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_NETWORK_BLOCK_FIXES),
        ({"final_safety_http_websocket_socket_block_boundary_verified": False}, Risk.FINAL_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_NETWORK_BLOCK_FIXES),
        ({"final_safety_account_read_only_boundary_verified": False}, Risk.FINAL_SAFETY_ACCOUNT_READ_ONLY_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_ACCOUNT_READ_ONLY_FIXES),
        ({"final_safety_market_data_read_only_boundary_verified": False}, Risk.FINAL_SAFETY_MARKET_DATA_READ_ONLY_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_MARKET_DATA_READ_ONLY_FIXES),
        ({"final_safety_order_blocking_boundary_verified": False}, Risk.FINAL_SAFETY_ORDER_BLOCKING_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_ORDER_BLOCKING_FIXES),
        ({"final_safety_position_mutation_blocking_boundary_verified": False}, Risk.FINAL_SAFETY_POSITION_MUTATION_BLOCKING_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_POSITION_MUTATION_BLOCKING_FIXES),
        ({"final_safety_observability_boundary_verified": False}, Risk.FINAL_SAFETY_OBSERVABILITY_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_OBSERVABILITY_FIXES),
        ({"final_safety_journal_boundary_verified": False}, Risk.FINAL_SAFETY_JOURNAL_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_JOURNAL_FIXES),
        ({"final_safety_human_approval_boundary_verified": False}, Risk.FINAL_SAFETY_HUMAN_APPROVAL_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_HUMAN_APPROVAL_FIXES),
        ({"final_safety_stop_conditions_boundary_verified": False}, Risk.FINAL_SAFETY_STOP_CONDITION_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_STOP_CONDITION_FIXES),
        ({"final_safety_success_failure_boundary_verified": False}, Risk.FINAL_SAFETY_SUCCESS_FAILURE_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_SUCCESS_FAILURE_FIXES),
        ({"final_safety_audit_boundary_verified": False}, Risk.FINAL_SAFETY_AUDIT_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_AUDIT_FIXES),
        ({"final_safety_go_no_go_boundary_verified": False}, Risk.FINAL_SAFETY_GO_NO_GO_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_GO_NO_GO_FIXES),
        ({"final_safety_abort_boundary_verified": False}, Risk.FINAL_SAFETY_ABORT_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_ABORT_FIXES),
        ({"final_safety_profitability_observation_boundary_verified": False}, Risk.FINAL_SAFETY_PROFITABILITY_OBSERVATION_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_PROFITABILITY_OBSERVATION_FIXES),
        ({"final_safety_consistency_observation_boundary_verified": False}, Risk.FINAL_SAFETY_CONSISTENCY_OBSERVATION_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_CONSISTENCY_OBSERVATION_FIXES),
    ],
)
def test_final_safety_gaps_are_enforced(overrides, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is State.FINAL_SAFETY_GATE_BLOCKED


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
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate(_ready_input(**overrides))

    assert Risk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE


def test_data_access_is_blocked():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate(_ready_input(data_access_requested=True))

    assert Risk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE


def test_premature_runner_plan_is_detected():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate(
        _ready_input(paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan_requested=True)
    )

    assert Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN in result.risks


def test_recommendations_and_markdown_are_rendered():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate(_ready_input())
    markdown = render_paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate_markdown(result)

    assert generate_final_safety_gate_recommendations(_ready_input()) == (
        Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE_SUITE,
        Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN,
    )
    assert "Paper Broker Read-Only Connection Dry Run Controlled Execution Final Safety Gate" in markdown
    assert "No dry-run execution" in markdown
    assert "do not promise profit" in markdown
    assert "profitability_observation_boundary" in markdown


def test_mapping_input_and_missing_plan_input():
    nominal = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate(dict(_ready_input().__dict__))
    missing = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate(None)

    assert nominal.safety_gate_score == 100
    assert missing.state is State.FINAL_SAFETY_GATE_INPUT_INVALID
    assert Risk.FINAL_CONTROLLED_EXECUTION_PLAN_NOT_APPROVED in missing.risks


def test_risk_detection_helper_returns_tuple():
    risks = detect_final_safety_gate_risks(_ready_input(final_safety_abort_boundary_verified=False))

    assert risks == (Risk.FINAL_SAFETY_ABORT_BOUNDARY_FAILED,)


def test_source_has_no_real_io_or_network_imports():
    source = Path("src/agicore/trading/paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate.py").read_text()

    forbidden = ("import os", "import socket", "import requests", "from requests", "urllib", "http.client", "open(", "os.environ")
    for token in forbidden:
        assert token not in source