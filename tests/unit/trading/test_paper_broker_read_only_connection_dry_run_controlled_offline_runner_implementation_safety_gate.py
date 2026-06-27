from pathlib import Path

import pytest

from agicore.trading import paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate as gate
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan import (
    evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanRisk,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateDecision as Decision,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateInput,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateRecommendation as Recommendation,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateRisk as Risk,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateState as State,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan import (
    _ready_input as _implementation_plan_ready_input,
)


SPECS = (
    ("scope_boundary", "validate_offline_runner_implementation_safety_scope_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SCOPE_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SCOPE_FIXES"),
    ("architecture_boundary", "validate_offline_runner_implementation_safety_architecture_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ARCHITECTURE_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ARCHITECTURE_FIXES"),
    ("sequence_boundary", "validate_offline_runner_implementation_safety_sequence_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SEQUENCE_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SEQUENCE_FIXES"),
    ("runtime_contract_boundary", "validate_offline_runner_implementation_safety_runtime_contract_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RUNTIME_CONTRACT_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RUNTIME_CONTRACT_FIXES"),
    ("input_adapter_boundary", "validate_offline_runner_implementation_safety_input_adapter_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_INPUT_ADAPTER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_INPUT_ADAPTER_FIXES"),
    ("synthetic_market_context_adapter_boundary", "validate_offline_runner_implementation_safety_synthetic_market_context_adapter_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SYNTHETIC_MARKET_CONTEXT_ADAPTER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SYNTHETIC_MARKET_CONTEXT_ADAPTER_FIXES"),
    ("simulated_broker_adapter_boundary", "validate_offline_runner_implementation_safety_simulated_broker_adapter_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SIMULATED_BROKER_ADAPTER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SIMULATED_BROKER_ADAPTER_FIXES"),
    ("account_snapshot_adapter_boundary", "validate_offline_runner_implementation_safety_account_snapshot_adapter_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ACCOUNT_SNAPSHOT_ADAPTER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ACCOUNT_SNAPSHOT_ADAPTER_FIXES"),
    ("market_data_snapshot_adapter_boundary", "validate_offline_runner_implementation_safety_market_data_snapshot_adapter_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_MARKET_DATA_SNAPSHOT_ADAPTER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_MARKET_DATA_SNAPSHOT_ADAPTER_FIXES"),
    ("strategy_signal_probe_boundary", "validate_offline_runner_implementation_safety_strategy_signal_probe_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STRATEGY_SIGNAL_PROBE_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STRATEGY_SIGNAL_PROBE_FIXES"),
    ("risk_observer_boundary", "validate_offline_runner_implementation_safety_risk_observer_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RISK_OBSERVER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RISK_OBSERVER_FIXES"),
    ("profitability_observer_boundary", "validate_offline_runner_implementation_safety_profitability_observer_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_PROFITABILITY_OBSERVER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_PROFITABILITY_OBSERVER_FIXES"),
    ("consistency_observer_boundary", "validate_offline_runner_implementation_safety_consistency_observer_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_CONSISTENCY_OBSERVER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_CONSISTENCY_OBSERVER_FIXES"),
    ("journal_writer_boundary", "validate_offline_runner_implementation_safety_journal_writer_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_JOURNAL_WRITER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_JOURNAL_WRITER_FIXES"),
    ("observability_boundary", "validate_offline_runner_implementation_safety_observability_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_OBSERVABILITY_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_OBSERVABILITY_FIXES"),
    ("human_approval_boundary", "validate_offline_runner_implementation_safety_human_approval_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HUMAN_APPROVAL_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HUMAN_APPROVAL_FIXES"),
    ("stop_condition_boundary", "validate_offline_runner_implementation_safety_stop_condition_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STOP_CONDITION_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STOP_CONDITION_FIXES"),
    ("success_failure_boundary", "validate_offline_runner_implementation_safety_success_failure_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SUCCESS_FAILURE_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SUCCESS_FAILURE_FIXES"),
    ("audit_boundary", "validate_offline_runner_implementation_safety_audit_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_AUDIT_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_AUDIT_FIXES"),
    ("go_no_go_boundary", "validate_offline_runner_implementation_safety_go_no_go_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GO_NO_GO_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GO_NO_GO_FIXES"),
    ("abort_boundary", "validate_offline_runner_implementation_safety_abort_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ABORT_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ABORT_FIXES"),
    ("no_real_broker_boundary", "validate_offline_runner_implementation_safety_no_real_broker_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_REAL_BROKER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NO_REAL_BROKER_FIXES"),
    ("no_secret_read_boundary", "validate_offline_runner_implementation_safety_no_secret_read_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SECRET_READ_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NO_SECRET_READ_FIXES"),
    ("network_block_boundary", "validate_offline_runner_implementation_safety_network_block_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NETWORK_BLOCK_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NETWORK_BLOCK_FIXES"),
    ("http_websocket_socket_block_boundary", "validate_offline_runner_implementation_safety_http_websocket_socket_block_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NETWORK_BLOCK_FIXES"),
    ("order_blocking_boundary", "validate_offline_runner_implementation_safety_order_blocking_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ORDER_BLOCKING_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ORDER_BLOCKING_FIXES"),
    ("position_mutation_blocking_boundary", "validate_offline_runner_implementation_safety_position_mutation_blocking_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_POSITION_MUTATION_BLOCKING_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_POSITION_MUTATION_BLOCKING_FIXES"),
    ("data_access_boundary", "validate_offline_runner_implementation_safety_data_access_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_DATA_ACCESS_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_DATA_ACCESS_FIXES"),
    ("test_strategy_boundary", "validate_offline_runner_implementation_safety_test_strategy_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_TEST_STRATEGY_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_TEST_STRATEGY_FIXES"),
    ("rollback_strategy_boundary", "validate_offline_runner_implementation_safety_rollback_strategy_boundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ROLLBACK_STRATEGY_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ROLLBACK_STRATEGY_FIXES"),
)


def _implementation_plan():
    return evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan(
        _implementation_plan_ready_input()
    )


def _ready_input(**overrides):
    values = {
        "paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan": _implementation_plan(),
        "offline_runner_implementation_plan_approved": True,
    }
    values.update(overrides)
    return PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateInput(**values)


def test_nominal_implementation_safety_gate_is_approved():
    result = gate.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate(_ready_input())

    assert result.state is State.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION
    assert result.decision is Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.runner_created is False
    assert result.runner_executed is False
    assert result.dry_run_executed is False
    assert len(result.boundaries) == len(SPECS)
    assert result.no_secret_read_boundary.no_secret_read is True
    assert result.network_block_boundary.network_blocked is True
    assert result.data_access_boundary.data_access_blocked is True


def test_approval_validation_rejects_unapproved_or_risky_plan():
    assert gate.validate_offline_runner_implementation_plan_approval(_ready_input()) is True

    plan = _implementation_plan()
    risky_plan = plan.__class__(
        **{
            **plan.__dict__,
            "risks": (PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,),
        }
    )
    data = _ready_input(
        paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan=risky_plan
    )
    assert gate.validate_offline_runner_implementation_plan_approval(data) is False


def test_all_boundary_functions_pass_nominally():
    data = _ready_input()
    for _key, function_name, _risk, _decision in SPECS:
        assert hasattr(gate, function_name)
        assert getattr(gate, function_name)(data).passed is True


@pytest.mark.parametrize(
    ("key", "risk_name", "decision_name"),
    [("plan", "OFFLINE_RUNNER_IMPLEMENTATION_PLAN_NOT_APPROVED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_PLAN_FIXES")]
    + [(key, risk_name, decision_name) for key, _fn, risk_name, decision_name in SPECS],
)
def test_each_missing_or_unsafe_boundary_blocks(key, risk_name, decision_name):
    overrides = {"offline_runner_implementation_plan_approved": False}
    if key != "plan":
        overrides = {f"offline_runner_implementation_safety_{key}_valid": False}

    result = gate.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate(
        _ready_input(**overrides)
    )

    assert getattr(Risk, risk_name) in result.risks
    assert result.decision is getattr(Decision, decision_name)
    assert result.score.overall_score < 100


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
    result = gate.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate(
        _ready_input(**overrides)
    )

    assert Risk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE


def test_data_access_is_blocked():
    result = gate.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate(
        _ready_input(data_access_requested=True)
    )

    assert Risk.DATA_ACCESS_VIOLATION in result.risks
    assert Risk.OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_DATA_ACCESS_BOUNDARY_FAILED in result.risks


def test_premature_implementation_preparation_is_blocked():
    result = gate.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate(
        _ready_input(
            paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_requested=True
        )
    )

    assert Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION in result.risks
    assert result.decision is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE


def test_mapping_input_and_missing_plan_are_handled():
    nominal = gate.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate(
        dict(_ready_input().__dict__)
    )
    missing = gate.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate({})

    assert nominal.decision is Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE
    assert missing.state is State.OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_INPUT_INVALID
    assert Risk.OFFLINE_RUNNER_IMPLEMENTATION_PLAN_NOT_APPROVED in missing.risks


def test_recommendations_and_markdown_nominal():
    result = gate.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate(_ready_input())
    markdown = gate.render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate_markdown(result)

    assert Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_SUITE in result.recommendations
    assert Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION in result.recommendations
    assert "Implementation Safety Gate" in markdown
    assert "no executable runner creation" in markdown


def test_score_risks_and_recommendations_helpers():
    data = _ready_input(offline_runner_implementation_safety_observability_boundary_valid=False)
    score = gate.compute_offline_runner_implementation_safety_gate_score(data)
    risks = gate.detect_offline_runner_implementation_safety_gate_risks(data)
    recommendations = gate.generate_offline_runner_implementation_safety_gate_recommendations(data, risks)

    assert score.observability_boundary_score == 0
    assert Risk.OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_OBSERVABILITY_BOUNDARY_FAILED in risks
    assert Recommendation.FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_OBSERVABILITY in recommendations


def test_module_has_no_forbidden_runtime_imports_or_data_access():
    source = Path(
        "src/agicore/trading/paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate.py"
    ).read_text(encoding="utf-8")
    forbidden = ["requests", "urllib", "import websocket", "import socket", "socket.", "os.environ", "open("]
    for token in forbidden:
        assert token not in source
