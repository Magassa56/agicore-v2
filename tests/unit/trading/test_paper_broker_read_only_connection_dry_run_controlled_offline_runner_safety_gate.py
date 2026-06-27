from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan import (
    evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate import (
    compute_offline_runner_safety_gate_score,
    detect_offline_runner_safety_gate_risks,
    evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate,
    generate_offline_runner_safety_gate_recommendations,
    render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate_markdown,
    validate_offline_runner_plan_approval,
    validate_offline_runner_safety_abort_boundary,
    validate_offline_runner_safety_account_snapshot_boundary,
    validate_offline_runner_safety_audit_boundary,
    validate_offline_runner_safety_consistency_observation_boundary,
    validate_offline_runner_safety_execution_mode_boundary,
    validate_offline_runner_safety_go_no_go_boundary,
    validate_offline_runner_safety_http_websocket_socket_block_boundary,
    validate_offline_runner_safety_human_approval_boundary,
    validate_offline_runner_safety_input_contract_boundary,
    validate_offline_runner_safety_journal_boundary,
    validate_offline_runner_safety_market_data_snapshot_boundary,
    validate_offline_runner_safety_network_block_boundary,
    validate_offline_runner_safety_no_real_broker_boundary,
    validate_offline_runner_safety_no_secret_read_boundary,
    validate_offline_runner_safety_observability_boundary,
    validate_offline_runner_safety_order_blocking_boundary,
    validate_offline_runner_safety_position_mutation_blocking_boundary,
    validate_offline_runner_safety_profitability_observation_boundary,
    validate_offline_runner_safety_read_only_broker_simulation_boundary,
    validate_offline_runner_safety_risk_observation_boundary,
    validate_offline_runner_safety_scope_boundary,
    validate_offline_runner_safety_stop_conditions_boundary,
    validate_offline_runner_safety_strategy_signal_observation_boundary,
    validate_offline_runner_safety_success_failure_boundary,
    validate_offline_runner_safety_synthetic_market_context_boundary,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerSafetyGateDecision as Decision,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerSafetyGateInput,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerSafetyGateRecommendation as Recommendation,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerSafetyGateRisk as Risk,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerSafetyGateState as State,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan import (
    _ready_input as _plan_ready_input,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _offline_runner_plan_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan(_plan_ready_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan": _offline_runner_plan_result(),
        "paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN"),
        "paper_broker_read_only_connection_dry_run_controlled_execution_final_plan": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE"),
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
        "offline_runner_plan_approved": True,
    }
    payload.update(overrides)
    return PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerSafetyGateInput(**payload)


def test_nominal_offline_runner_safety_gate_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate(_ready_input())

    assert result.state is State.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION
    assert result.decision is Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_SAFETY_GATE
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.offline_only is True
    assert result.safety_gate_only is True
    assert result.runner_created is False
    assert result.runner_executed is False
    assert result.dry_run_executed is False
    assert result.profitability_observation_boundary.no_profit_promise is True
    assert result.consistency_observation_boundary.deterministic_consistency_checks is True


def test_validate_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_offline_runner_plan_approval(data) is True
    assert validate_offline_runner_safety_scope_boundary(data).runner_not_created is True
    assert validate_offline_runner_safety_execution_mode_boundary(data).no_dry_run_execution is True
    assert validate_offline_runner_safety_input_contract_boundary(data).no_real_credentials is True
    assert validate_offline_runner_safety_synthetic_market_context_boundary(data).no_data_access is True
    assert validate_offline_runner_safety_read_only_broker_simulation_boundary(data).simulated_broker_only is True
    assert validate_offline_runner_safety_no_real_broker_boundary(data).real_broker_blocked is True
    assert validate_offline_runner_safety_no_secret_read_boundary(data).no_api_key_read is True
    assert validate_offline_runner_safety_network_block_boundary(data).external_api_blocked is True
    assert validate_offline_runner_safety_http_websocket_socket_block_boundary(data).socket_blocked is True
    assert validate_offline_runner_safety_account_snapshot_boundary(data).active_account_access_blocked is True
    assert validate_offline_runner_safety_market_data_snapshot_boundary(data).synthetic_snapshot_only is True
    assert validate_offline_runner_safety_order_blocking_boundary(data).real_order_blocked is True
    assert validate_offline_runner_safety_position_mutation_blocking_boundary(data).position_mutation_blocked is True
    assert validate_offline_runner_safety_strategy_signal_observation_boundary(data).observation_only is True
    assert validate_offline_runner_safety_risk_observation_boundary(data).observation_only is True
    assert validate_offline_runner_safety_profitability_observation_boundary(data).no_profit_promise is True
    assert validate_offline_runner_safety_consistency_observation_boundary(data).observation_only is True
    assert validate_offline_runner_safety_journal_boundary(data).offline_journal_required is True
    assert validate_offline_runner_safety_observability_boundary(data).offline_events_defined is True
    assert validate_offline_runner_safety_human_approval_boundary(data).human_approval_required is True
    assert validate_offline_runner_safety_stop_conditions_boundary(data).stop_on_network_request is True
    assert validate_offline_runner_safety_success_failure_boundary(data).failure_on_boundary_violation is True
    assert validate_offline_runner_safety_audit_boundary(data).audit_events_defined is True
    assert validate_offline_runner_safety_go_no_go_boundary(data).go_no_go_required is True
    assert validate_offline_runner_safety_abort_boundary(data).abort_on_network_or_broker_request is True
    assert compute_offline_runner_safety_gate_score(data).overall_score == 100


@pytest.mark.parametrize(
    ("overrides", "risk", "decision"),
    [
        ({"offline_runner_plan_approved": False}, Risk.OFFLINE_RUNNER_PLAN_NOT_APPROVED, Decision.REQUIRE_OFFLINE_RUNNER_PLAN_FIXES),
        ({"offline_runner_safety_scope_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_SCOPE_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_SCOPE_FIXES),
        ({"offline_runner_safety_execution_mode_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_EXECUTION_MODE_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_EXECUTION_MODE_FIXES),
        ({"offline_runner_safety_input_contract_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_INPUT_CONTRACT_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_INPUT_CONTRACT_FIXES),
        ({"offline_runner_safety_synthetic_market_context_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_SYNTHETIC_MARKET_CONTEXT_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_SYNTHETIC_MARKET_CONTEXT_FIXES),
        ({"offline_runner_safety_read_only_broker_simulation_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_READ_ONLY_BROKER_SIMULATION_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_READ_ONLY_BROKER_SIMULATION_FIXES),
        ({"offline_runner_safety_no_real_broker_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_REAL_BROKER_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_NO_REAL_BROKER_FIXES),
        ({"offline_runner_safety_no_secret_read_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_SECRET_READ_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_NO_SECRET_READ_FIXES),
        ({"offline_runner_safety_network_block_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_NETWORK_BLOCK_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_NETWORK_BLOCK_FIXES),
        ({"offline_runner_safety_http_websocket_socket_block_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_NETWORK_BLOCK_FIXES),
        ({"offline_runner_safety_account_snapshot_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_ACCOUNT_SNAPSHOT_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_ACCOUNT_SNAPSHOT_FIXES),
        ({"offline_runner_safety_market_data_snapshot_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_MARKET_DATA_SNAPSHOT_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_MARKET_DATA_SNAPSHOT_FIXES),
        ({"offline_runner_safety_order_blocking_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_ORDER_BLOCKING_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_ORDER_BLOCKING_FIXES),
        ({"offline_runner_safety_position_mutation_blocking_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_POSITION_MUTATION_BLOCKING_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_POSITION_MUTATION_BLOCKING_FIXES),
        ({"offline_runner_safety_strategy_signal_observation_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_STRATEGY_SIGNAL_OBSERVATION_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_STRATEGY_SIGNAL_OBSERVATION_FIXES),
        ({"offline_runner_safety_risk_observation_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_RISK_OBSERVATION_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_RISK_OBSERVATION_FIXES),
        ({"offline_runner_safety_profitability_observation_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_PROFITABILITY_OBSERVATION_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_PROFITABILITY_OBSERVATION_FIXES),
        ({"offline_runner_safety_consistency_observation_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_CONSISTENCY_OBSERVATION_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_CONSISTENCY_OBSERVATION_FIXES),
        ({"offline_runner_safety_journal_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_JOURNAL_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_JOURNAL_FIXES),
        ({"offline_runner_safety_observability_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_OBSERVABILITY_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_OBSERVABILITY_FIXES),
        ({"offline_runner_safety_human_approval_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_HUMAN_APPROVAL_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_HUMAN_APPROVAL_FIXES),
        ({"offline_runner_safety_stop_conditions_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_STOP_CONDITION_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_STOP_CONDITION_FIXES),
        ({"offline_runner_safety_success_failure_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_SUCCESS_FAILURE_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_SUCCESS_FAILURE_FIXES),
        ({"offline_runner_safety_audit_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_AUDIT_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_AUDIT_FIXES),
        ({"offline_runner_safety_go_no_go_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_GO_NO_GO_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_GO_NO_GO_FIXES),
        ({"offline_runner_safety_abort_boundary_verified": False}, Risk.OFFLINE_RUNNER_SAFETY_ABORT_BOUNDARY_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_ABORT_FIXES),
    ],
)
def test_each_failed_boundary_blocks_with_targeted_risk(overrides, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is State.OFFLINE_RUNNER_SAFETY_GATE_BLOCKED


@pytest.mark.parametrize(
    "overrides",
    [
        {"real_execution_requested": True},
        {"runner_creation_requested": True},
        {"runner_execution_requested": True},
        {"dry_run_requested": True},
        {"dry_run_executed": True},
        {"broker_connection_requested": True},
        {"api_key_read_requested": True},
        {"env_var_read_requested": True},
        {"hardcoded_secret_detected": True},
        {"network_transport_requested": True},
        {"external_api_requested": True},
        {"order_execution_requested": True},
        {"position_mutation_requested": True},
        {"account_access_requested": True},
        {"no_http_transport": False},
        {"no_websocket_transport": False},
        {"no_socket_transport": False},
        {"no_real_broker": False},
    ],
)
def test_real_execution_boundaries_are_blocked(overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate(_ready_input(**overrides))

    assert Risk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_SAFETY_GATE


def test_data_access_is_blocked():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate(
        _ready_input(data_access_requested=True)
    )

    assert Risk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_SAFETY_GATE


def test_premature_preparation_is_blocked():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate(
        _ready_input(paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_requested=True)
    )

    assert Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION in result.risks
    assert Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION in result.recommendations


def test_recommendations_and_markdown_nominal():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate(_ready_input())
    markdown = render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate_markdown(result)

    assert Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_SAFETY_GATE_SUITE in result.recommendations
    assert "Controlled Offline Runner Safety Gate" in markdown
    assert "no runner creation" in markdown
    assert result.markdown_report == markdown


def test_mapping_input_and_missing_plan_are_handled():
    nominal = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate(dict(_ready_input().__dict__))
    missing = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate(None)

    assert nominal.score.overall_score == 100
    assert missing.state is State.OFFLINE_RUNNER_SAFETY_GATE_INPUT_INVALID
    assert Risk.OFFLINE_RUNNER_PLAN_NOT_APPROVED in missing.risks


def test_risk_detection_returns_tuple():
    risks = detect_offline_runner_safety_gate_risks(_ready_input(offline_runner_safety_journal_boundary_verified=False))

    assert isinstance(risks, tuple)
    assert Risk.OFFLINE_RUNNER_SAFETY_JOURNAL_BOUNDARY_FAILED in risks


def test_recommendations_for_failed_plan_hold_next_phase():
    recommendations = generate_offline_runner_safety_gate_recommendations(
        _ready_input(offline_runner_plan_approved=False)
    )

    assert Recommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION in recommendations
    assert Recommendation.APPROVE_OFFLINE_RUNNER_PLAN_FIRST in recommendations


def test_module_does_not_import_runtime_io_or_network_primitives():
    source = Path("src/agicore/trading/paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate.py").read_text()

    forbidden = ("import os", "import socket", "import requests", "from requests", "urllib", "http.client", "open(", "os.environ")
    assert not any(token in source for token in forbidden)