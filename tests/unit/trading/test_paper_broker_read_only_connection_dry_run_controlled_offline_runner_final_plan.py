from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan import (
    compute_final_offline_runner_plan_score,
    define_final_offline_runner_abort_policy,
    define_final_offline_runner_account_snapshot_policy,
    define_final_offline_runner_audit_plan,
    define_final_offline_runner_consistency_observation_plan,
    define_final_offline_runner_execution_mode,
    define_final_offline_runner_failure_criteria,
    define_final_offline_runner_go_no_go_policy,
    define_final_offline_runner_human_approval_plan,
    define_final_offline_runner_http_websocket_socket_block_policy,
    define_final_offline_runner_input_contract,
    define_final_offline_runner_journal_plan,
    define_final_offline_runner_market_data_snapshot_policy,
    define_final_offline_runner_network_block_policy,
    define_final_offline_runner_no_real_broker_policy,
    define_final_offline_runner_no_secret_read_policy,
    define_final_offline_runner_observability_plan,
    define_final_offline_runner_order_blocking_policy,
    define_final_offline_runner_position_mutation_blocking_policy,
    define_final_offline_runner_profitability_observation_plan,
    define_final_offline_runner_read_only_broker_simulation_contract,
    define_final_offline_runner_risk_observation_plan,
    define_final_offline_runner_scope,
    define_final_offline_runner_stop_conditions_plan,
    define_final_offline_runner_strategy_signal_observation_plan,
    define_final_offline_runner_success_criteria,
    define_final_offline_runner_synthetic_market_context,
    detect_final_offline_runner_plan_risks,
    evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan,
    generate_final_offline_runner_plan_recommendations,
    render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan_markdown,
    validate_offline_runner_preparation_review_approval,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanDecision as Decision,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanInput,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanRecommendation as Recommendation,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanRisk as Risk,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanState as State,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review import (
    evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review import (
    _ready_input as _review_ready_input,
)


def _upstream(state="READY", decision=None, risks=()):
    return {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}


def _preparation_review_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review(
        _review_ready_input()
    )
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review": _preparation_review_result(),
        "paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW"),
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
        "offline_runner_preparation_review_approved": True,
    }
    payload.update(overrides)
    return PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanInput(**payload)


def test_nominal_final_plan_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan(_ready_input())

    assert result.state is State.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE
    assert result.decision is Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.offline_only is True
    assert result.final_plan_only is True
    assert result.runner_created is False
    assert result.runner_executed is False
    assert result.dry_run_executed is False
    assert result.profitability_observation_plan.no_profit_promise is True


def test_define_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_offline_runner_preparation_review_approval(data) is True
    assert define_final_offline_runner_scope(data).no_runner_executable_created is True
    assert define_final_offline_runner_execution_mode(data).controlled_offline_mode is True
    assert define_final_offline_runner_input_contract(data).synthetic_inputs_only is True
    assert define_final_offline_runner_synthetic_market_context(data).no_data_access is True
    assert define_final_offline_runner_read_only_broker_simulation_contract(data).simulated_broker_only is True
    assert define_final_offline_runner_no_real_broker_policy(data).real_broker_blocked is True
    assert define_final_offline_runner_no_secret_read_policy(data).no_api_key_read is True
    assert define_final_offline_runner_network_block_policy(data).external_api_blocked is True
    assert define_final_offline_runner_http_websocket_socket_block_policy(data).socket_blocked is True
    assert define_final_offline_runner_account_snapshot_policy(data).active_account_access_blocked is True
    assert define_final_offline_runner_market_data_snapshot_policy(data).synthetic_snapshot_only is True
    assert define_final_offline_runner_order_blocking_policy(data).real_order_blocked is True
    assert define_final_offline_runner_position_mutation_blocking_policy(data).position_mutation_blocked is True
    assert define_final_offline_runner_strategy_signal_observation_plan(data).observation_only is True
    assert define_final_offline_runner_risk_observation_plan(data).observation_only is True
    assert define_final_offline_runner_profitability_observation_plan(data).no_profit_promise is True
    assert define_final_offline_runner_consistency_observation_plan(data).deterministic_consistency_checks is True
    assert define_final_offline_runner_journal_plan(data).offline_journal_required is True
    assert define_final_offline_runner_observability_plan(data).offline_events_defined is True
    assert define_final_offline_runner_human_approval_plan(data).human_approval_required is True
    assert define_final_offline_runner_stop_conditions_plan(data).stop_on_network_request is True
    assert define_final_offline_runner_success_criteria(data).no_runner_execution_required is True
    assert define_final_offline_runner_failure_criteria(data).fail_on_execution_request is True
    assert define_final_offline_runner_audit_plan(data).audit_events_defined is True
    assert define_final_offline_runner_go_no_go_policy(data).go_no_go_required is True
    assert define_final_offline_runner_abort_policy(data).abort_on_network_or_broker_request is True
    assert compute_final_offline_runner_plan_score(data).overall_score == 100


@pytest.mark.parametrize(
    ("overrides", "risk", "decision"),
    [
        ({"offline_runner_preparation_review_approved": False}, Risk.OFFLINE_RUNNER_PREPARATION_REVIEW_NOT_APPROVED, Decision.REQUIRE_OFFLINE_RUNNER_PREPARATION_REVIEW_FIXES),
        ({"final_offline_runner_scope_defined": False}, Risk.FINAL_OFFLINE_RUNNER_SCOPE_UNCLEAR, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SCOPE_FIXES),
        ({"final_offline_runner_execution_mode_defined": False}, Risk.FINAL_OFFLINE_RUNNER_EXECUTION_MODE_UNSAFE, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_EXECUTION_MODE_FIXES),
        ({"final_offline_runner_input_contract_defined": False}, Risk.FINAL_OFFLINE_RUNNER_INPUT_CONTRACT_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_INPUT_CONTRACT_FIXES),
        ({"final_offline_runner_synthetic_market_context_defined": False}, Risk.FINAL_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_FIXES),
        ({"final_offline_runner_read_only_broker_simulation_defined": False}, Risk.FINAL_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_UNSAFE, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_FIXES),
        ({"final_offline_runner_no_real_broker_policy_defined": False}, Risk.FINAL_OFFLINE_RUNNER_REAL_BROKER_POLICY_UNSAFE, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_NO_REAL_BROKER_FIXES),
        ({"final_offline_runner_no_secret_read_policy_defined": False}, Risk.FINAL_OFFLINE_RUNNER_SECRET_READ_POLICY_UNSAFE, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_NO_SECRET_READ_FIXES),
        ({"final_offline_runner_network_block_policy_defined": False}, Risk.FINAL_OFFLINE_RUNNER_NETWORK_NOT_BLOCKED, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_NETWORK_BLOCK_FIXES),
        ({"final_offline_runner_http_websocket_socket_block_policy_defined": False}, Risk.FINAL_OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_NETWORK_BLOCK_FIXES),
        ({"final_offline_runner_account_snapshot_policy_defined": False}, Risk.FINAL_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_UNSAFE, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_FIXES),
        ({"final_offline_runner_market_data_snapshot_policy_defined": False}, Risk.FINAL_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_UNSAFE, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_FIXES),
        ({"final_offline_runner_order_blocking_policy_defined": False}, Risk.FINAL_OFFLINE_RUNNER_ORDER_BLOCKING_UNSAFE, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_ORDER_BLOCKING_FIXES),
        ({"final_offline_runner_position_mutation_blocking_policy_defined": False}, Risk.FINAL_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_UNSAFE, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_FIXES),
        ({"final_offline_runner_strategy_signal_observation_plan_defined": False}, Risk.FINAL_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_FIXES),
        ({"final_offline_runner_risk_observation_plan_defined": False}, Risk.FINAL_OFFLINE_RUNNER_RISK_OBSERVATION_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_RISK_OBSERVATION_FIXES),
        ({"final_offline_runner_profitability_observation_plan_defined": False}, Risk.FINAL_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_FIXES),
        ({"final_offline_runner_consistency_observation_plan_defined": False}, Risk.FINAL_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_FIXES),
        ({"final_offline_runner_journal_plan_defined": False}, Risk.FINAL_OFFLINE_RUNNER_JOURNAL_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_JOURNAL_FIXES),
        ({"final_offline_runner_observability_plan_defined": False}, Risk.FINAL_OFFLINE_RUNNER_OBSERVABILITY_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_OBSERVABILITY_FIXES),
        ({"final_offline_runner_human_approval_plan_defined": False}, Risk.FINAL_OFFLINE_RUNNER_HUMAN_APPROVAL_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_HUMAN_APPROVAL_FIXES),
        ({"final_offline_runner_stop_conditions_plan_defined": False}, Risk.FINAL_OFFLINE_RUNNER_STOP_CONDITIONS_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_STOP_CONDITION_FIXES),
        ({"final_offline_runner_success_criteria_defined": False}, Risk.FINAL_OFFLINE_RUNNER_SUCCESS_CRITERIA_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SUCCESS_FAILURE_FIXES),
        ({"final_offline_runner_failure_criteria_defined": False}, Risk.FINAL_OFFLINE_RUNNER_FAILURE_CRITERIA_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SUCCESS_FAILURE_FIXES),
        ({"final_offline_runner_audit_plan_defined": False}, Risk.FINAL_OFFLINE_RUNNER_AUDIT_PLAN_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_AUDIT_FIXES),
        ({"final_offline_runner_go_no_go_policy_defined": False}, Risk.FINAL_OFFLINE_RUNNER_GO_NO_GO_POLICY_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_GO_NO_GO_FIXES),
        ({"final_offline_runner_abort_policy_defined": False}, Risk.FINAL_OFFLINE_RUNNER_ABORT_POLICY_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_ABORT_FIXES),
    ],
)
def test_each_missing_final_plan_component_blocks_with_targeted_risk(overrides, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is State.FINAL_OFFLINE_RUNNER_PLAN_BLOCKED


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
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan(_ready_input(**overrides))

    assert Risk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN


def test_data_access_is_blocked():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan(
        _ready_input(data_access_requested=True)
    )

    assert Risk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN


def test_premature_final_safety_gate_is_blocked():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan(
        _ready_input(paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_safety_gate_requested=True)
    )

    assert Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE in result.risks
    assert Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE in result.recommendations


def test_mapping_input_and_missing_review_are_handled():
    nominal = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan(dict(_ready_input().__dict__))
    missing = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan(None)

    assert nominal.score.overall_score == 100
    assert missing.state is State.FINAL_OFFLINE_RUNNER_PLAN_INPUT_INVALID
    assert Risk.OFFLINE_RUNNER_PREPARATION_REVIEW_NOT_APPROVED in missing.risks


def test_recommendations_and_markdown_nominal():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan(_ready_input())
    markdown = render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan_markdown(result)

    assert Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN_SUITE in result.recommendations
    assert Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE in result.recommendations
    assert "Controlled Offline Runner Final Plan" in markdown
    assert "no executable runner creation" in markdown
    assert result.markdown_report == markdown


def test_risk_detection_and_recommendations_for_failed_component():
    risks = detect_final_offline_runner_plan_risks(_ready_input(final_offline_runner_observability_plan_defined=False))
    recommendations = generate_final_offline_runner_plan_recommendations(_ready_input(), risks)

    assert Risk.FINAL_OFFLINE_RUNNER_OBSERVABILITY_MISSING in risks
    assert Recommendation.FIX_FINAL_OFFLINE_RUNNER_OBSERVABILITY in recommendations


def test_module_has_no_forbidden_runtime_imports_or_data_access():
    source = Path(
        "src/agicore/trading/paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan.py"
    ).read_text(encoding="utf-8")

    assert "requests" not in source
    assert "urllib" not in source
    assert "import websocket" not in source.lower()
    assert "import socket" not in source.lower()
    assert "socket." not in source.lower()
    assert "os.environ" not in source
    assert "open(" not in source
