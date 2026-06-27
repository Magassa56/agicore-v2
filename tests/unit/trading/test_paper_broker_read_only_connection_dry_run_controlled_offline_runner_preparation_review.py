from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation import (
    evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review import (
    compute_offline_runner_preparation_review_score,
    detect_offline_runner_preparation_review_risks,
    evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review,
    generate_offline_runner_preparation_review_recommendations,
    render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review_markdown,
    review_offline_runner_abort_preparation_contract,
    review_offline_runner_account_snapshot_preparation_contract,
    review_offline_runner_audit_preparation_contract,
    review_offline_runner_consistency_observation_preparation_contract,
    review_offline_runner_execution_mode_preparation_contract,
    review_offline_runner_failure_criteria_preparation_contract,
    review_offline_runner_go_no_go_preparation_contract,
    review_offline_runner_human_approval_preparation_contract,
    review_offline_runner_http_websocket_socket_block_guard,
    review_offline_runner_input_preparation_contract,
    review_offline_runner_journal_preparation_contract,
    review_offline_runner_market_data_snapshot_preparation_contract,
    review_offline_runner_network_block_guard,
    review_offline_runner_no_real_broker_guard,
    review_offline_runner_no_secret_read_guard,
    review_offline_runner_observability_preparation_contract,
    review_offline_runner_order_blocking_guard,
    review_offline_runner_position_mutation_blocking_guard,
    review_offline_runner_profitability_observation_preparation_contract,
    review_offline_runner_read_only_broker_simulation_preparation_contract,
    review_offline_runner_risk_observation_preparation_contract,
    review_offline_runner_scope_preparation_contract,
    review_offline_runner_stop_conditions_preparation_contract,
    review_offline_runner_strategy_signal_observation_preparation_contract,
    review_offline_runner_success_criteria_preparation_contract,
    review_offline_runner_synthetic_market_context_preparation_contract,
    validate_offline_runner_preparation_approval,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewDecision as Decision,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewInput,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewRecommendation as Recommendation,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewRisk as Risk,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewState as State,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation import (
    _ready_input as _preparation_ready_input,
)


def _upstream(state="READY", decision=None, risks=()):
    return {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}


def _preparation_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation(
        _preparation_ready_input()
    )
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation": _preparation_result(),
        "paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION"),
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
        "offline_runner_preparation_approved": True,
    }
    payload.update(overrides)
    return PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewInput(**payload)


def test_nominal_preparation_review_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review(_ready_input())

    assert result.state is State.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN
    assert result.decision is Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW
    assert result.score.overall_score == 100
    assert result.review_score == 100
    assert result.risks == ()
    assert result.offline_only is True
    assert result.review_only is True
    assert result.runner_created is False
    assert result.runner_executed is False
    assert result.dry_run_executed is False


def test_review_functions_pass_nominal_preparation():
    data = _ready_input()

    assert validate_offline_runner_preparation_approval(data) is True
    assert review_offline_runner_scope_preparation_contract(data).no_runner_executable_created is True
    assert review_offline_runner_execution_mode_preparation_contract(data).controlled_offline_mode is True
    assert review_offline_runner_input_preparation_contract(data).synthetic_inputs_only is True
    assert review_offline_runner_synthetic_market_context_preparation_contract(data).no_data_access is True
    assert review_offline_runner_read_only_broker_simulation_preparation_contract(data).simulated_broker_only is True
    assert review_offline_runner_no_real_broker_guard(data).real_broker_blocked is True
    assert review_offline_runner_no_secret_read_guard(data).no_api_key_read is True
    assert review_offline_runner_network_block_guard(data).external_api_blocked is True
    assert review_offline_runner_http_websocket_socket_block_guard(data).socket_blocked is True
    assert review_offline_runner_account_snapshot_preparation_contract(data).active_account_access_blocked is True
    assert review_offline_runner_market_data_snapshot_preparation_contract(data).synthetic_snapshot_only is True
    assert review_offline_runner_order_blocking_guard(data).real_order_blocked is True
    assert review_offline_runner_position_mutation_blocking_guard(data).position_mutation_blocked is True
    assert review_offline_runner_strategy_signal_observation_preparation_contract(data).observation_only is True
    assert review_offline_runner_risk_observation_preparation_contract(data).observation_only is True
    assert review_offline_runner_profitability_observation_preparation_contract(data).no_profit_promise is True
    assert review_offline_runner_consistency_observation_preparation_contract(data).deterministic_consistency_checks is True
    assert review_offline_runner_journal_preparation_contract(data).offline_journal_required is True
    assert review_offline_runner_observability_preparation_contract(data).offline_events_defined is True
    assert review_offline_runner_human_approval_preparation_contract(data).human_approval_required is True
    assert review_offline_runner_stop_conditions_preparation_contract(data).stop_on_network_request is True
    assert review_offline_runner_success_criteria_preparation_contract(data).no_runner_execution_required is True
    assert review_offline_runner_failure_criteria_preparation_contract(data).fail_on_execution_request is True
    assert review_offline_runner_audit_preparation_contract(data).audit_events_defined is True
    assert review_offline_runner_go_no_go_preparation_contract(data).go_no_go_required is True
    assert review_offline_runner_abort_preparation_contract(data).abort_on_network_or_broker_request is True
    assert compute_offline_runner_preparation_review_score(data).overall_score == 100


@pytest.mark.parametrize(
    ("overrides", "risk", "decision"),
    [
        ({"offline_runner_preparation_approved": False}, Risk.OFFLINE_RUNNER_PREPARATION_NOT_APPROVED, Decision.REQUIRE_OFFLINE_RUNNER_PREPARATION_FIXES),
        ({"offline_runner_scope_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_SCOPE_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SCOPE_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_execution_mode_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_input_contract_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_synthetic_market_context_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_read_only_broker_simulation_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_no_real_broker_guard_review_verified": False}, Risk.OFFLINE_RUNNER_REAL_BROKER_GUARD_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_REVIEW_FIXES),
        ({"offline_runner_no_secret_read_guard_review_verified": False}, Risk.OFFLINE_RUNNER_SECRET_READ_GUARD_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_REVIEW_FIXES),
        ({"offline_runner_network_block_guard_review_verified": False}, Risk.OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW_FIXES),
        ({"offline_runner_http_websocket_socket_block_guard_review_verified": False}, Risk.OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW_FIXES),
        ({"offline_runner_account_snapshot_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_market_data_snapshot_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_order_blocking_guard_review_verified": False}, Risk.OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_REVIEW_FIXES),
        ({"offline_runner_position_mutation_blocking_guard_review_verified": False}, Risk.OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_REVIEW_FIXES),
        ({"offline_runner_strategy_signal_observation_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_risk_observation_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_profitability_observation_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_consistency_observation_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_journal_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_JOURNAL_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_JOURNAL_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_observability_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_human_approval_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_stop_conditions_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_STOP_CONDITIONS_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_success_criteria_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_SUCCESS_CRITERIA_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_failure_criteria_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_FAILURE_CRITERIA_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_audit_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_AUDIT_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_AUDIT_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_go_no_go_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_GO_NO_GO_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_GO_NO_GO_PREPARATION_REVIEW_FIXES),
        ({"offline_runner_abort_preparation_review_verified": False}, Risk.OFFLINE_RUNNER_ABORT_PREPARATION_REVIEW_FAILED, Decision.REQUIRE_OFFLINE_RUNNER_ABORT_PREPARATION_REVIEW_FIXES),
    ],
)
def test_each_failed_review_blocks_with_targeted_risk(overrides, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review(
        _ready_input(**overrides)
    )

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is State.OFFLINE_RUNNER_PREPARATION_REVIEW_BLOCKED


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
    ],
)
def test_real_execution_boundaries_are_blocked(overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review(
        _ready_input(**overrides)
    )

    assert Risk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW


def test_data_access_is_blocked():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review(
        _ready_input(data_access_requested=True)
    )

    assert Risk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW


def test_premature_final_plan_is_blocked():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review(
        _ready_input(paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan_requested=True)
    )

    assert Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN in result.risks
    assert Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN in result.recommendations


def test_mapping_input_and_missing_preparation_are_handled():
    nominal = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review(
        dict(_ready_input().__dict__)
    )
    missing = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review(None)

    assert nominal.score.overall_score == 100
    assert missing.state is State.OFFLINE_RUNNER_PREPARATION_REVIEW_INPUT_INVALID
    assert Risk.OFFLINE_RUNNER_PREPARATION_NOT_APPROVED in missing.risks


def test_recommendations_and_markdown_nominal():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review(_ready_input())
    markdown = render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review_markdown(result)

    assert Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW_SUITE in result.recommendations
    assert Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN in result.recommendations
    assert "Controlled Offline Runner Preparation Review" in markdown
    assert "no executable runner creation" in markdown
    assert result.markdown_report == markdown


def test_risk_detection_and_recommendations_for_failed_review():
    risks = detect_offline_runner_preparation_review_risks(
        _ready_input(offline_runner_observability_preparation_review_verified=False)
    )
    recommendations = generate_offline_runner_preparation_review_recommendations(_ready_input(), risks)

    assert Risk.OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW_FAILED in risks
    assert Recommendation.FIX_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW in recommendations


def test_module_has_no_forbidden_runtime_imports_or_data_access():
    source = Path(
        "src/agicore/trading/paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review.py"
    ).read_text(encoding="utf-8")

    assert "requests" not in source
    assert "urllib" not in source
    assert "import websocket" not in source.lower()
    assert "import socket" not in source.lower()
    assert "socket." not in source.lower()
    assert "os.environ" not in source
    assert "open(" not in source
