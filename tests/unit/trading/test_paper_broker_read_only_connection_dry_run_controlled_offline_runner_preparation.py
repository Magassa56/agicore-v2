from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate import (
    evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation import (
    compute_offline_runner_preparation_score,
    detect_offline_runner_preparation_risks,
    evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation,
    generate_offline_runner_preparation_recommendations,
    prepare_offline_runner_abort_contract,
    prepare_offline_runner_account_snapshot_contract,
    prepare_offline_runner_audit_contract,
    prepare_offline_runner_consistency_observation_contract,
    prepare_offline_runner_execution_mode_contract,
    prepare_offline_runner_failure_criteria_contract,
    prepare_offline_runner_go_no_go_contract,
    prepare_offline_runner_human_approval_contract,
    prepare_offline_runner_http_websocket_socket_block_guard,
    prepare_offline_runner_input_contract,
    prepare_offline_runner_journal_contract,
    prepare_offline_runner_market_data_snapshot_contract,
    prepare_offline_runner_network_block_guard,
    prepare_offline_runner_no_real_broker_guard,
    prepare_offline_runner_no_secret_read_guard,
    prepare_offline_runner_observability_contract,
    prepare_offline_runner_order_blocking_guard,
    prepare_offline_runner_position_mutation_blocking_guard,
    prepare_offline_runner_profitability_observation_contract,
    prepare_offline_runner_read_only_broker_simulation_contract,
    prepare_offline_runner_risk_observation_contract,
    prepare_offline_runner_scope_contract,
    prepare_offline_runner_stop_conditions_contract,
    prepare_offline_runner_strategy_signal_observation_contract,
    prepare_offline_runner_success_criteria_contract,
    prepare_offline_runner_synthetic_market_context_contract,
    render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_markdown,
    validate_offline_runner_safety_gate_approval,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationDecision as Decision,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationRecommendation as Recommendation,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationRisk as Risk,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationState as State,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate import (
    _ready_input as _safety_gate_ready_input,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _safety_gate_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate(
        _safety_gate_ready_input()
    )
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate": _safety_gate_result(),
        "paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_SAFETY_GATE"),
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
        "offline_runner_safety_gate_approved": True,
    }
    payload.update(overrides)
    return PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput(**payload)


def test_nominal_offline_runner_preparation_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation(_ready_input())

    assert result.state is State.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW
    assert result.decision is Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.offline_only is True
    assert result.preparation_only is True
    assert result.runner_created is False
    assert result.runner_executed is False
    assert result.dry_run_executed is False
    assert result.profitability_observation_contract.no_profit_promise is True
    assert result.consistency_observation_contract.deterministic_consistency_checks is True


def test_prepare_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_offline_runner_safety_gate_approval(data) is True
    assert prepare_offline_runner_scope_contract(data).no_runner_executable_created is True
    assert prepare_offline_runner_execution_mode_contract(data).controlled_offline_mode is True
    assert prepare_offline_runner_input_contract(data).synthetic_inputs_only is True
    assert prepare_offline_runner_synthetic_market_context_contract(data).no_data_access is True
    assert prepare_offline_runner_read_only_broker_simulation_contract(data).simulated_broker_only is True
    assert prepare_offline_runner_no_real_broker_guard(data).real_broker_blocked is True
    assert prepare_offline_runner_no_secret_read_guard(data).no_api_key_read is True
    assert prepare_offline_runner_network_block_guard(data).external_api_blocked is True
    assert prepare_offline_runner_http_websocket_socket_block_guard(data).socket_blocked is True
    assert prepare_offline_runner_account_snapshot_contract(data).active_account_access_blocked is True
    assert prepare_offline_runner_market_data_snapshot_contract(data).synthetic_snapshot_only is True
    assert prepare_offline_runner_order_blocking_guard(data).real_order_blocked is True
    assert prepare_offline_runner_position_mutation_blocking_guard(data).position_mutation_blocked is True
    assert prepare_offline_runner_strategy_signal_observation_contract(data).observation_only is True
    assert prepare_offline_runner_risk_observation_contract(data).observation_only is True
    assert prepare_offline_runner_profitability_observation_contract(data).no_profit_promise is True
    assert prepare_offline_runner_consistency_observation_contract(data).observation_only is True
    assert prepare_offline_runner_journal_contract(data).offline_journal_required is True
    assert prepare_offline_runner_observability_contract(data).offline_events_defined is True
    assert prepare_offline_runner_human_approval_contract(data).human_approval_required is True
    assert prepare_offline_runner_stop_conditions_contract(data).stop_on_network_request is True
    assert prepare_offline_runner_success_criteria_contract(data).no_runner_execution_required is True
    assert prepare_offline_runner_failure_criteria_contract(data).fail_on_execution_request is True
    assert prepare_offline_runner_audit_contract(data).audit_events_defined is True
    assert prepare_offline_runner_go_no_go_contract(data).go_no_go_required is True
    assert prepare_offline_runner_abort_contract(data).abort_on_network_or_broker_request is True
    assert compute_offline_runner_preparation_score(data).overall_score == 100


@pytest.mark.parametrize(
    ("overrides", "risk", "decision"),
    [
        ({"offline_runner_safety_gate_approved": False}, Risk.OFFLINE_RUNNER_SAFETY_GATE_NOT_APPROVED, Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_GATE_FIXES),
        ({"offline_runner_scope_contract_prepared": False}, Risk.OFFLINE_RUNNER_SCOPE_PREPARATION_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_SCOPE_PREPARATION_FIXES),
        ({"offline_runner_execution_mode_contract_prepared": False}, Risk.OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_FIXES),
        ({"offline_runner_input_contract_prepared": False}, Risk.OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_FIXES),
        ({"offline_runner_synthetic_market_context_contract_prepared": False}, Risk.OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_FIXES),
        ({"offline_runner_read_only_broker_simulation_contract_prepared": False}, Risk.OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_FIXES),
        ({"offline_runner_no_real_broker_guard_prepared": False}, Risk.OFFLINE_RUNNER_REAL_BROKER_GUARD_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_FIXES),
        ({"offline_runner_no_secret_read_guard_prepared": False}, Risk.OFFLINE_RUNNER_SECRET_READ_GUARD_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_FIXES),
        ({"offline_runner_network_block_guard_prepared": False}, Risk.OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_FIXES),
        ({"offline_runner_http_websocket_socket_block_guard_prepared": False}, Risk.OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_FIXES),
        ({"offline_runner_account_snapshot_contract_prepared": False}, Risk.OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_FIXES),
        ({"offline_runner_market_data_snapshot_contract_prepared": False}, Risk.OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_FIXES),
        ({"offline_runner_order_blocking_guard_prepared": False}, Risk.OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_FIXES),
        ({"offline_runner_position_mutation_blocking_guard_prepared": False}, Risk.OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_FIXES),
        ({"offline_runner_strategy_signal_observation_contract_prepared": False}, Risk.OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_FIXES),
        ({"offline_runner_risk_observation_contract_prepared": False}, Risk.OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_FIXES),
        ({"offline_runner_profitability_observation_contract_prepared": False}, Risk.OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_FIXES),
        ({"offline_runner_consistency_observation_contract_prepared": False}, Risk.OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_FIXES),
        ({"offline_runner_journal_contract_prepared": False}, Risk.OFFLINE_RUNNER_JOURNAL_PREPARATION_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_JOURNAL_PREPARATION_FIXES),
        ({"offline_runner_observability_contract_prepared": False}, Risk.OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_FIXES),
        ({"offline_runner_human_approval_contract_prepared": False}, Risk.OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_FIXES),
        ({"offline_runner_stop_conditions_contract_prepared": False}, Risk.OFFLINE_RUNNER_STOP_CONDITIONS_PREPARATION_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_PREPARATION_FIXES),
        ({"offline_runner_success_criteria_contract_prepared": False}, Risk.OFFLINE_RUNNER_SUCCESS_CRITERIA_PREPARATION_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_FIXES),
        ({"offline_runner_failure_criteria_contract_prepared": False}, Risk.OFFLINE_RUNNER_FAILURE_CRITERIA_PREPARATION_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_FIXES),
        ({"offline_runner_audit_contract_prepared": False}, Risk.OFFLINE_RUNNER_AUDIT_PREPARATION_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_AUDIT_PREPARATION_FIXES),
        ({"offline_runner_go_no_go_contract_prepared": False}, Risk.OFFLINE_RUNNER_GO_NO_GO_PREPARATION_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_GO_NO_GO_PREPARATION_FIXES),
        ({"offline_runner_abort_contract_prepared": False}, Risk.OFFLINE_RUNNER_ABORT_PREPARATION_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_ABORT_PREPARATION_FIXES),
    ],
)
def test_each_missing_contract_blocks_with_targeted_risk(overrides, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is State.OFFLINE_RUNNER_PREPARATION_BLOCKED

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
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation(_ready_input(**overrides))

    assert Risk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION


def test_data_access_is_blocked():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation(
        _ready_input(data_access_requested=True)
    )

    assert Risk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION


def test_premature_preparation_review_is_blocked():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation(
        _ready_input(paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review_requested=True)
    )

    assert Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW in result.risks
    assert Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW in result.recommendations


def test_recommendations_and_markdown_nominal():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation(_ready_input())
    markdown = render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_markdown(result)

    assert Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_SUITE in result.recommendations
    assert "Controlled Offline Runner Preparation" in markdown
    assert "no executable runner creation" in markdown
    assert result.markdown_report == markdown


def test_mapping_input_and_missing_gate_are_handled():
    nominal = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation(dict(_ready_input().__dict__))
    missing = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation(None)

    assert nominal.score.overall_score == 100
    assert missing.state is State.OFFLINE_RUNNER_PREPARATION_INPUT_INVALID
    assert Risk.OFFLINE_RUNNER_SAFETY_GATE_NOT_APPROVED in missing.risks


def test_risk_detection_returns_tuple():
    risks = detect_offline_runner_preparation_risks(_ready_input(offline_runner_journal_contract_prepared=False))

    assert isinstance(risks, tuple)
    assert Risk.OFFLINE_RUNNER_JOURNAL_PREPARATION_MISSING in risks


def test_recommendations_for_failed_gate_hold_next_phase():
    recommendations = generate_offline_runner_preparation_recommendations(
        _ready_input(offline_runner_safety_gate_approved=False)
    )

    assert Recommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW in recommendations
    assert Recommendation.APPROVE_OFFLINE_RUNNER_SAFETY_GATE_FIRST in recommendations


def test_module_does_not_import_runtime_io_or_network_primitives():
    source = Path("src/agicore/trading/paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation.py").read_text()

    forbidden = ("import os", "import socket", "import requests", "from requests", "urllib", "http.client", "open(", "os.environ")
    assert not any(token in source for token in forbidden)