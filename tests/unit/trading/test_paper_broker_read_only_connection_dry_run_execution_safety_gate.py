from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_execution_plan import (
    evaluate_paper_broker_read_only_connection_dry_run_execution_plan,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_execution_safety_gate import (
    compute_read_only_connection_dry_run_execution_safety_gate_score,
    detect_read_only_connection_dry_run_execution_safety_gate_risks,
    evaluate_paper_broker_read_only_connection_dry_run_execution_safety_gate,
    generate_read_only_connection_dry_run_execution_safety_gate_recommendations,
    render_paper_broker_read_only_connection_dry_run_execution_safety_gate_markdown,
    validate_dry_run_execution_plan_approval,
    verify_dry_run_execution_account_read_only_safety,
    verify_dry_run_execution_audit_plan_safety,
    verify_dry_run_execution_credentials_reference_safety,
    verify_dry_run_execution_http_websocket_socket_block_safety,
    verify_dry_run_execution_human_approval_safety,
    verify_dry_run_execution_journal_safety,
    verify_dry_run_execution_market_data_read_only_safety,
    verify_dry_run_execution_network_block_safety,
    verify_dry_run_execution_no_secret_read_safety,
    verify_dry_run_execution_observability_safety,
    verify_dry_run_execution_order_blocking_safety,
    verify_dry_run_execution_position_mutation_block_safety,
    verify_dry_run_execution_precondition_safety,
    verify_dry_run_execution_scope_safety,
    verify_dry_run_execution_sequence_safety,
    verify_dry_run_execution_stop_conditions_safety,
    verify_dry_run_execution_success_failure_criteria_safety,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_execution_safety_gate_models import (
    PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision,
    PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput,
    PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRecommendation,
    PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk,
    PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateState,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_execution_plan import (
    _ready_input as _execution_plan_ready_input,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _execution_plan_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_plan(_execution_plan_ready_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_dry_run_execution_plan": _execution_plan_result(),
        "paper_broker_read_only_connection_dry_run_preparation_review": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN"
        ),
        "paper_broker_read_only_connection_dry_run_preparation": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW"
        ),
        "paper_broker_read_only_connection_dry_run_safety_gate": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION"
        ),
        "paper_broker_read_only_connection_dry_run_plan": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE"
        ),
        "paper_broker_read_only_connection_preparation_review": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN"
        ),
        "paper_broker_read_only_connection_preparation": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW"
        ),
        "paper_broker_read_only_connection_safety_gate": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION"
        ),
        "paper_broker_read_only_connection_plan": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE"
        ),
        "paper_broker_read_only_safety_review": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN"),
        "paper_broker_read_only_preparation": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW"),
        "multi_scenario_result_report": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_PREPARATION"),
        "multi_scenario_controlled_simulation_result": _upstream("READY_FOR_MULTI_SCENARIO_RESULT_REPORT"),
        "performance_risk_validation_gate": _upstream("READY_FOR_MULTI_SCENARIO_CONTROLLED_SIMULATION"),
        "performance_metrics_result": _upstream("READY_FOR_RISK_METRICS_ENGINE"),
        "risk_metrics_result": _upstream("READY_FOR_PERFORMANCE_RISK_VALIDATION_GATE"),
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
        "dry_run_execution_plan_approved": True,
        "dry_run_execution_scope_safety_verified": True,
        "dry_run_execution_sequence_safety_verified": True,
        "dry_run_execution_precondition_safety_verified": True,
        "dry_run_execution_credentials_reference_safety_verified": True,
        "dry_run_execution_no_secret_read_safety_verified": True,
        "dry_run_execution_network_block_safety_verified": True,
        "dry_run_execution_http_websocket_socket_block_safety_verified": True,
        "dry_run_execution_account_read_only_safety_verified": True,
        "dry_run_execution_market_data_read_only_safety_verified": True,
        "dry_run_execution_order_blocking_safety_verified": True,
        "dry_run_execution_position_mutation_block_safety_verified": True,
        "dry_run_execution_observability_safety_verified": True,
        "dry_run_execution_journal_safety_verified": True,
        "dry_run_execution_human_approval_safety_verified": True,
        "dry_run_execution_stop_conditions_safety_verified": True,
        "dry_run_execution_success_failure_criteria_safety_verified": True,
        "dry_run_execution_audit_plan_safety_verified": True,
        "paper_broker_read_only_connection_dry_run_execution_preparation_requested": False,
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
    return PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput(**payload)


def test_nominal_execution_safety_gate_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_safety_gate(_ready_input())

    assert result.state is PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE
    assert result.safety_gate_score == 100
    assert result.risks == ()
    assert result.offline_only is True
    assert result.network_block_safety.network_execution_blocked is True
    assert result.http_websocket_socket_block_safety.socket_blocked is True
    assert result.order_blocking_safety.order_execution_blocked is True


def test_verification_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_dry_run_execution_plan_approval(data) is True
    assert verify_dry_run_execution_scope_safety(data).passed is True
    assert verify_dry_run_execution_sequence_safety(data).passed is True
    assert verify_dry_run_execution_precondition_safety(data).passed is True
    assert verify_dry_run_execution_credentials_reference_safety(data).passed is True
    assert verify_dry_run_execution_no_secret_read_safety(data).passed is True
    assert verify_dry_run_execution_network_block_safety(data).passed is True
    assert verify_dry_run_execution_http_websocket_socket_block_safety(data).passed is True
    assert verify_dry_run_execution_account_read_only_safety(data).passed is True
    assert verify_dry_run_execution_market_data_read_only_safety(data).passed is True
    assert verify_dry_run_execution_order_blocking_safety(data).passed is True
    assert verify_dry_run_execution_position_mutation_block_safety(data).passed is True
    assert verify_dry_run_execution_observability_safety(data).passed is True
    assert verify_dry_run_execution_journal_safety(data).passed is True
    assert verify_dry_run_execution_human_approval_safety(data).passed is True
    assert verify_dry_run_execution_stop_conditions_safety(data).passed is True
    assert verify_dry_run_execution_success_failure_criteria_safety(data).passed is True
    assert verify_dry_run_execution_audit_plan_safety(data).passed is True
    assert compute_read_only_connection_dry_run_execution_safety_gate_score(data).overall_score == 100


def test_execution_plan_not_approved_blocks_gate():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_safety_gate(
        _ready_input(
            paper_broker_read_only_connection_dry_run_execution_plan=_execution_plan_result(
                state="DRY_RUN_EXECUTION_PLAN_BLOCKED",
                decision="REQUIRE_DRY_RUN_EXECUTION_SCOPE_FIXES",
                risks=("DRY_RUN_EXECUTION_SCOPE_UNCLEAR",),
            ),
            dry_run_execution_plan_approved=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_PLAN_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_PLAN_FIXES


@pytest.mark.parametrize(
    ("field", "risk", "decision"),
    [
        ("dry_run_execution_scope_safety_verified", PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_SCOPE_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_SCOPE_SAFETY_FIXES),
        ("dry_run_execution_sequence_safety_verified", PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_SEQUENCE_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_SEQUENCE_SAFETY_FIXES),
        ("dry_run_execution_precondition_safety_verified", PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_PRECONDITION_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_PRECONDITION_SAFETY_FIXES),
        ("dry_run_execution_credentials_reference_safety_verified", PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_CREDENTIAL_POLICY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_CREDENTIAL_SAFETY_FIXES),
        ("dry_run_execution_no_secret_read_safety_verified", PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_SECRET_READ_POLICY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_NO_SECRET_READ_FIXES),
        ("dry_run_execution_network_block_safety_verified", PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_NETWORK_NOT_BLOCKED, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_FIXES),
        ("dry_run_execution_http_websocket_socket_block_safety_verified", PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_FIXES),
        ("dry_run_execution_account_read_only_safety_verified", PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_FIXES),
        ("dry_run_execution_market_data_read_only_safety_verified", PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_FIXES),
        ("dry_run_execution_order_blocking_safety_verified", PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_ORDER_BLOCKING_FIXES),
        ("dry_run_execution_position_mutation_block_safety_verified", PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_FIXES),
        ("dry_run_execution_observability_safety_verified", PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_OBSERVABILITY_INCOMPLETE, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_AUDIT_FIXES),
        ("dry_run_execution_journal_safety_verified", PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_JOURNAL_INCOMPLETE, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_AUDIT_FIXES),
        ("dry_run_execution_human_approval_safety_verified", PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL_FIXES),
        ("dry_run_execution_stop_conditions_safety_verified", PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_STOP_CONDITION_FIXES),
        ("dry_run_execution_success_failure_criteria_safety_verified", PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_SUCCESS_FAILURE_CRITERIA_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_STOP_CONDITION_FIXES),
        ("dry_run_execution_audit_plan_safety_verified", PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DRY_RUN_EXECUTION_AUDIT_PLAN_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_AUDIT_FIXES),
    ],
)
def test_required_safety_sections_are_enforced(field, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_safety_gate(_ready_input(**{field: False}))

    assert risk in result.risks
    assert result.decision is decision


@pytest.mark.parametrize(
    "override",
    [
        {"real_execution_requested": True},
        {"broker_connection_requested": True},
        {"api_key_read_requested": True},
        {"env_var_read_requested": True},
        {"hardcoded_secret_detected": True},
        {"network_transport_requested": True},
        {"external_api_requested": True},
        {"order_execution_requested": True},
        {"position_mutation_requested": True},
        {"account_access_requested": True},
        {"dry_run_requested": True},
        {"dry_run_executed": True},
    ],
)
def test_real_execution_boundary_violation_is_detected(override):
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_safety_gate(_ready_input(**override))

    assert PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision.REQUIRE_DRY_RUN_EXECUTION_SCOPE_SAFETY_FIXES


def test_data_access_violation_is_detected():
    risks = detect_read_only_connection_dry_run_execution_safety_gate_risks(
        _ready_input(data_access_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.DATA_ACCESS_VIOLATION in risks


def test_premature_execution_preparation_is_detected():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_safety_gate(
        _ready_input(paper_broker_read_only_connection_dry_run_execution_preparation_requested=True)
    )

    assert (
        PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION
        in result.risks
    )


def test_recommendations_and_markdown():
    nominal = _ready_input()
    recommendations = generate_read_only_connection_dry_run_execution_safety_gate_recommendations(nominal)
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_safety_gate(nominal)
    markdown = render_paper_broker_read_only_connection_dry_run_execution_safety_gate_markdown(result)

    assert Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION in recommendations
    assert "Paper Broker Read-Only Connection Dry Run Execution Safety Gate" in markdown
    assert "HTTP/websocket/socket/API external calls: blocked" in markdown
    assert "data/ access: blocked" in markdown


def test_mapping_input_and_missing_plan_invalid():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_safety_gate(dict(_ready_input().__dict__))
    missing = evaluate_paper_broker_read_only_connection_dry_run_execution_safety_gate({})

    assert result.safety_gate_score == 100
    assert missing.state is PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateState.DRY_RUN_EXECUTION_SAFETY_GATE_INPUT_INVALID


def test_source_does_not_use_real_network_secret_or_data_access():
    source = Path("src/agicore/trading/paper_broker_read_only_connection_dry_run_execution_safety_gate.py").read_text()

    forbidden = ("import requests", "import socket", "http.client", "os.environ", "Path('data", 'Path("data')
    assert not any(token in source for token in forbidden)


Recommendation = PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRecommendation
