from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_safety_gate import (
    evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_safety_gate,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan import (
    compute_offline_runner_implementation_plan_score,
    detect_offline_runner_implementation_plan_risks,
    evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan,
    generate_offline_runner_implementation_plan_recommendations,
    render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan_markdown,
    validate_final_offline_runner_safety_gate_approval,
    define_offline_runner_implementation_scope,
    define_offline_runner_implementation_architecture,
    define_offline_runner_implementation_sequence,
    define_offline_runner_runtime_contract,
    define_offline_runner_input_adapter_contract,
    define_offline_runner_synthetic_market_context_adapter,
    define_offline_runner_simulated_broker_adapter_contract,
    define_offline_runner_account_snapshot_adapter_contract,
    define_offline_runner_market_data_snapshot_adapter_contract,
    define_offline_runner_strategy_signal_probe_contract,
    define_offline_runner_risk_observer_contract,
    define_offline_runner_profitability_observer_contract,
    define_offline_runner_consistency_observer_contract,
    define_offline_runner_journal_writer_contract,
    define_offline_runner_observability_contract,
    define_offline_runner_human_approval_contract,
    define_offline_runner_stop_condition_contract,
    define_offline_runner_success_criteria_contract,
    define_offline_runner_failure_criteria_contract,
    define_offline_runner_audit_contract,
    define_offline_runner_go_no_go_contract,
    define_offline_runner_abort_contract,
    define_offline_runner_no_real_broker_guard,
    define_offline_runner_no_secret_read_guard,
    define_offline_runner_network_block_guard,
    define_offline_runner_http_websocket_socket_block_guard,
    define_offline_runner_order_blocking_guard,
    define_offline_runner_position_mutation_blocking_guard,
    define_offline_runner_data_access_guard,
    define_offline_runner_test_strategy,
    define_offline_runner_rollback_strategy,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanDecision as Decision,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanInput,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanRecommendation as Recommendation,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanRisk as Risk,
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanState as State,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_safety_gate import (
    _ready_input as _gate_ready_input,
)


def _gate_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_safety_gate(_gate_ready_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload

def _upstream(state="READY", decision=None, risks=()):
    return {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}

def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_safety_gate": _gate_result(),
        "paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE"),
        "paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review": _upstream(),
        "paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation": _upstream(),
        "paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate": _upstream(),
        "paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan": _upstream(),
        "final_offline_runner_safety_gate_approved": True,
    }
    payload.update(overrides)
    return PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanInput(**payload)


def test_nominal_implementation_plan_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan(_ready_input())

    assert result.state is State.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE
    assert result.decision is Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.runner_created is False
    assert result.runner_executed is False
    assert result.dry_run_executed is False
    assert result.implementation_scope.no_runner_created is True
    assert result.network_block_guard.http_blocked is True
    assert result.data_access_guard.data_access_blocked is True

def test_define_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_final_offline_runner_safety_gate_approval(data) is True
    assert define_offline_runner_implementation_scope(data).defined is True
    assert define_offline_runner_implementation_architecture(data).defined is True
    assert define_offline_runner_implementation_sequence(data).defined is True
    assert define_offline_runner_runtime_contract(data).defined is True
    assert define_offline_runner_input_adapter_contract(data).defined is True
    assert define_offline_runner_synthetic_market_context_adapter(data).defined is True
    assert define_offline_runner_simulated_broker_adapter_contract(data).defined is True
    assert define_offline_runner_account_snapshot_adapter_contract(data).defined is True
    assert define_offline_runner_market_data_snapshot_adapter_contract(data).defined is True
    assert define_offline_runner_strategy_signal_probe_contract(data).defined is True
    assert define_offline_runner_risk_observer_contract(data).defined is True
    assert define_offline_runner_profitability_observer_contract(data).defined is True
    assert define_offline_runner_consistency_observer_contract(data).defined is True
    assert define_offline_runner_journal_writer_contract(data).defined is True
    assert define_offline_runner_observability_contract(data).defined is True
    assert define_offline_runner_human_approval_contract(data).defined is True
    assert define_offline_runner_stop_condition_contract(data).defined is True
    assert define_offline_runner_success_criteria_contract(data).defined is True
    assert define_offline_runner_failure_criteria_contract(data).defined is True
    assert define_offline_runner_audit_contract(data).defined is True
    assert define_offline_runner_go_no_go_contract(data).defined is True
    assert define_offline_runner_abort_contract(data).defined is True
    assert define_offline_runner_no_real_broker_guard(data).defined is True
    assert define_offline_runner_no_secret_read_guard(data).defined is True
    assert define_offline_runner_network_block_guard(data).defined is True
    assert define_offline_runner_http_websocket_socket_block_guard(data).defined is True
    assert define_offline_runner_order_blocking_guard(data).defined is True
    assert define_offline_runner_position_mutation_blocking_guard(data).defined is True
    assert define_offline_runner_data_access_guard(data).defined is True
    assert define_offline_runner_test_strategy(data).defined is True
    assert define_offline_runner_rollback_strategy(data).defined is True
    assert compute_offline_runner_implementation_plan_score(data).overall_score == 100

@pytest.mark.parametrize(
    ("overrides", "risk", "decision"),
    [
        ({"final_offline_runner_safety_gate_approved": False}, Risk.FINAL_OFFLINE_RUNNER_SAFETY_GATE_NOT_APPROVED, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_GATE_FIXES),
        ({"offline_runner_implementation_scope_defined": False}, Risk.OFFLINE_RUNNER_IMPLEMENTATION_SCOPE_UNCLEAR, Decision.REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SCOPE_FIXES),
        ({"offline_runner_implementation_architecture_defined": False}, Risk.OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE_FIXES),
        ({"offline_runner_implementation_sequence_defined": False}, Risk.OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE_FIXES),
        ({"offline_runner_runtime_contract_defined": False}, Risk.OFFLINE_RUNNER_RUNTIME_CONTRACT_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_RUNTIME_CONTRACT_FIXES),
        ({"offline_runner_input_adapter_contract_defined": False}, Risk.OFFLINE_RUNNER_INPUT_ADAPTER_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_INPUT_ADAPTER_FIXES),
        ({"offline_runner_synthetic_market_context_adapter_defined": False}, Risk.OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER_FIXES),
        ({"offline_runner_simulated_broker_adapter_contract_defined": False}, Risk.OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER_FIXES),
        ({"offline_runner_account_snapshot_adapter_contract_defined": False}, Risk.OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER_FIXES),
        ({"offline_runner_market_data_snapshot_adapter_contract_defined": False}, Risk.OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER_FIXES),
        ({"offline_runner_strategy_signal_probe_contract_defined": False}, Risk.OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE_FIXES),
        ({"offline_runner_risk_observer_contract_defined": False}, Risk.OFFLINE_RUNNER_RISK_OBSERVER_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_RISK_OBSERVER_FIXES),
        ({"offline_runner_profitability_observer_contract_defined": False}, Risk.OFFLINE_RUNNER_PROFITABILITY_OBSERVER_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVER_FIXES),
        ({"offline_runner_consistency_observer_contract_defined": False}, Risk.OFFLINE_RUNNER_CONSISTENCY_OBSERVER_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVER_FIXES),
        ({"offline_runner_journal_writer_contract_defined": False}, Risk.OFFLINE_RUNNER_JOURNAL_WRITER_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_JOURNAL_WRITER_FIXES),
        ({"offline_runner_observability_contract_defined": False}, Risk.OFFLINE_RUNNER_OBSERVABILITY_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_FIXES),
        ({"offline_runner_human_approval_contract_defined": False}, Risk.OFFLINE_RUNNER_HUMAN_APPROVAL_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_FIXES),
        ({"offline_runner_stop_condition_contract_defined": False}, Risk.OFFLINE_RUNNER_STOP_CONDITIONS_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_FIXES),
        ({"offline_runner_success_criteria_contract_defined": False}, Risk.OFFLINE_RUNNER_SUCCESS_CRITERIA_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_FIXES),
        ({"offline_runner_failure_criteria_contract_defined": False}, Risk.OFFLINE_RUNNER_FAILURE_CRITERIA_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_FIXES),
        ({"offline_runner_audit_contract_defined": False}, Risk.OFFLINE_RUNNER_AUDIT_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_AUDIT_FIXES),
        ({"offline_runner_go_no_go_contract_defined": False}, Risk.OFFLINE_RUNNER_GO_NO_GO_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_GO_NO_GO_FIXES),
        ({"offline_runner_abort_contract_defined": False}, Risk.OFFLINE_RUNNER_ABORT_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_ABORT_FIXES),
        ({"offline_runner_no_real_broker_guard_defined": False}, Risk.OFFLINE_RUNNER_REAL_BROKER_GUARD_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_FIXES),
        ({"offline_runner_no_secret_read_guard_defined": False}, Risk.OFFLINE_RUNNER_SECRET_READ_GUARD_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_FIXES),
        ({"offline_runner_network_block_guard_defined": False}, Risk.OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_FIXES),
        ({"offline_runner_http_websocket_socket_block_guard_defined": False}, Risk.OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_FIXES),
        ({"offline_runner_order_blocking_guard_defined": False}, Risk.OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_FIXES),
        ({"offline_runner_position_mutation_blocking_guard_defined": False}, Risk.OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_FIXES),
        ({"offline_runner_data_access_guard_defined": False}, Risk.OFFLINE_RUNNER_DATA_ACCESS_GUARD_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_DATA_ACCESS_GUARD_FIXES),
        ({"offline_runner_test_strategy_defined": False}, Risk.OFFLINE_RUNNER_TEST_STRATEGY_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_TEST_STRATEGY_FIXES),
        ({"offline_runner_rollback_strategy_defined": False}, Risk.OFFLINE_RUNNER_ROLLBACK_STRATEGY_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_ROLLBACK_STRATEGY_FIXES),
    ],
)
def test_each_missing_or_unsafe_component_blocks(overrides, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is State.OFFLINE_RUNNER_IMPLEMENTATION_PLAN_BLOCKED

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
        {"no_api_key_read": False},
        {"no_env_var_read": False},
    ],
)
def test_real_execution_boundaries_are_blocked(overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan(_ready_input(**overrides))

    assert Risk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN

def test_data_access_is_blocked():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan(_ready_input(data_access_requested=True))

    assert Risk.DATA_ACCESS_VIOLATION in result.risks
    assert Risk.OFFLINE_RUNNER_DATA_ACCESS_GUARD_UNSAFE in result.risks

def test_premature_safety_gate_is_blocked():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan(
        _ready_input(paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate_requested=True)
    )

    assert Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE in result.risks
    assert Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE in result.recommendations

def test_mapping_input_and_missing_gate_are_handled():
    nominal = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan(dict(_ready_input().__dict__))
    missing = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan(None)

    assert nominal.score.overall_score == 100
    assert missing.state is State.OFFLINE_RUNNER_IMPLEMENTATION_PLAN_INPUT_INVALID
    assert Risk.FINAL_OFFLINE_RUNNER_SAFETY_GATE_NOT_APPROVED in missing.risks

def test_recommendations_and_markdown_nominal():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan(_ready_input())
    markdown = render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan_markdown(result)

    assert Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN_SUITE in result.recommendations
    assert Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE in result.recommendations
    assert "Implementation Plan" in markdown
    assert "no executable runner creation" in markdown
    assert result.markdown_report == markdown

def test_risk_detection_and_recommendations_for_failed_component():
    risks = detect_offline_runner_implementation_plan_risks(_ready_input(offline_runner_observability_contract_defined=False))
    recommendations = generate_offline_runner_implementation_plan_recommendations(_ready_input(), risks)

    assert Risk.OFFLINE_RUNNER_OBSERVABILITY_MISSING in risks
    assert Recommendation.FIX_OFFLINE_RUNNER_OBSERVABILITY in recommendations

def test_module_has_no_forbidden_runtime_imports_or_data_access():
    source = Path("src/agicore/trading/paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan.py").read_text(encoding="utf-8")

    assert "requests" not in source
    assert "urllib" not in source
    assert "import websocket" not in source.lower()
    assert "import socket" not in source.lower()
    assert "socket." not in source.lower()
    assert "os.environ" not in source
    assert "open(" not in source
