from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_plan import (
    evaluate_paper_broker_read_only_connection_dry_run_plan,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_safety_gate import (
    compute_dry_run_safety_gate_score,
    detect_dry_run_safety_gate_risks,
    evaluate_paper_broker_read_only_connection_dry_run_safety_gate,
    generate_dry_run_safety_gate_recommendations,
    render_paper_broker_read_only_connection_dry_run_safety_gate_markdown,
    validate_dry_run_plan_approval,
    verify_dry_run_account_read_only_safety,
    verify_dry_run_boundary_safety,
    verify_dry_run_credentials_safety,
    verify_dry_run_http_websocket_socket_block_safety,
    verify_dry_run_human_approval_safety,
    verify_dry_run_journal_safety,
    verify_dry_run_market_data_read_only_safety,
    verify_dry_run_network_block_safety,
    verify_dry_run_no_secret_read_safety,
    verify_dry_run_observability_safety,
    verify_dry_run_order_blocking_safety,
    verify_dry_run_position_mutation_block_safety,
    verify_dry_run_precondition_safety,
    verify_dry_run_scope_safety,
    verify_dry_run_stop_conditions_safety,
    verify_dry_run_success_failure_criteria_safety,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_safety_gate_models import (
    PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision,
    PaperBrokerReadOnlyConnectionDryRunSafetyGateInput,
    PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation,
    PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk,
    PaperBrokerReadOnlyConnectionDryRunSafetyGateState,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_plan import _ready_input as _plan_ready_input


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _dry_run_plan_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_plan(_plan_ready_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_dry_run_plan": _dry_run_plan_result(),
        "paper_broker_read_only_connection_preparation_review": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN",
            "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW",
        ),
        "paper_broker_read_only_connection_preparation": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW",
            "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION",
        ),
        "paper_broker_read_only_connection_safety_gate": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION",
            "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE",
        ),
        "paper_broker_read_only_connection_plan": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE",
            "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN",
        ),
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
        "dry_run_plan_approved": True,
        "dry_run_scope_safety_verified": True,
        "dry_run_boundary_safety_verified": True,
        "dry_run_precondition_safety_verified": True,
        "dry_run_credentials_safety_verified": True,
        "dry_run_no_secret_read_safety_verified": True,
        "dry_run_network_block_safety_verified": True,
        "dry_run_http_websocket_socket_block_safety_verified": True,
        "dry_run_account_read_only_safety_verified": True,
        "dry_run_market_data_read_only_safety_verified": True,
        "dry_run_order_blocking_safety_verified": True,
        "dry_run_position_mutation_block_safety_verified": True,
        "dry_run_observability_safety_verified": True,
        "dry_run_journal_safety_verified": True,
        "dry_run_human_approval_safety_verified": True,
        "dry_run_stop_conditions_safety_verified": True,
        "dry_run_success_failure_criteria_safety_verified": True,
        "paper_broker_read_only_connection_dry_run_preparation_requested": False,
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
    return PaperBrokerReadOnlyConnectionDryRunSafetyGateInput(**payload)


def test_nominal_dry_run_safety_gate_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_safety_gate(_ready_input())

    assert result.state is PaperBrokerReadOnlyConnectionDryRunSafetyGateState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE
    assert result.safety_gate_score == 100
    assert result.risks == ()
    assert result.offline_only is True
    assert result.no_secret_read_safety.no_api_key_read is True
    assert result.network_block_safety.network_execution_blocked is True
    assert result.http_websocket_socket_block_safety.socket_blocked is True
    assert result.order_blocking_safety.order_execution_blocked is True
    assert result.position_mutation_block_safety.position_mutation_blocked is True


def test_verification_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_dry_run_plan_approval(data) is True
    assert verify_dry_run_scope_safety(data).passed is True
    assert verify_dry_run_boundary_safety(data).passed is True
    assert verify_dry_run_precondition_safety(data).passed is True
    assert verify_dry_run_credentials_safety(data).passed is True
    assert verify_dry_run_no_secret_read_safety(data).passed is True
    assert verify_dry_run_network_block_safety(data).passed is True
    assert verify_dry_run_http_websocket_socket_block_safety(data).passed is True
    assert verify_dry_run_account_read_only_safety(data).passed is True
    assert verify_dry_run_market_data_read_only_safety(data).passed is True
    assert verify_dry_run_order_blocking_safety(data).passed is True
    assert verify_dry_run_position_mutation_block_safety(data).passed is True
    assert verify_dry_run_observability_safety(data).passed is True
    assert verify_dry_run_journal_safety(data).passed is True
    assert verify_dry_run_human_approval_safety(data).passed is True
    assert verify_dry_run_stop_conditions_safety(data).passed is True
    assert verify_dry_run_success_failure_criteria_safety(data).passed is True
    assert compute_dry_run_safety_gate_score(data).overall_score == 100


def test_dry_run_plan_not_approved_blocks_gate():
    result = evaluate_paper_broker_read_only_connection_dry_run_safety_gate(
        _ready_input(
            paper_broker_read_only_connection_dry_run_plan=_dry_run_plan_result(
                state="DRY_RUN_PLAN_BLOCKED",
                decision="REQUIRE_DRY_RUN_BOUNDARY_FIXES",
                risks=("REAL_EXECUTION_BOUNDARY_VIOLATION",),
            ),
            dry_run_plan_approved=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_PLAN_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_DRY_RUN_PLAN_FIXES


@pytest.mark.parametrize(
    ("field", "risk", "decision"),
    [
        ("dry_run_scope_safety_verified", PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_SCOPE_UNSAFE, PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_SCOPE_SAFETY_FIXES),
        ("dry_run_boundary_safety_verified", PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_BOUNDARY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_BOUNDARY_SAFETY_FIXES),
        ("dry_run_precondition_safety_verified", PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_PRECONDITION_UNSAFE, PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_PRECONDITION_SAFETY_FIXES),
        ("dry_run_credentials_safety_verified", PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_CREDENTIALS_UNSAFE, PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_CREDENTIAL_SAFETY_FIXES),
        ("dry_run_no_secret_read_safety_verified", PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_SECRET_READ_POLICY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_NO_SECRET_READ_SAFETY_FIXES),
        ("dry_run_network_block_safety_verified", PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_NETWORK_NOT_BLOCKED, PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_NETWORK_BLOCK_SAFETY_FIXES),
        ("dry_run_http_websocket_socket_block_safety_verified", PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED, PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_NETWORK_BLOCK_SAFETY_FIXES),
        ("dry_run_account_read_only_safety_verified", PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_ACCOUNT_READ_ONLY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_ACCOUNT_READ_ONLY_SAFETY_FIXES),
        ("dry_run_market_data_read_only_safety_verified", PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_MARKET_DATA_READ_ONLY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_MARKET_DATA_READ_ONLY_SAFETY_FIXES),
        ("dry_run_order_blocking_safety_verified", PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_ORDER_BLOCKING_UNSAFE, PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_ORDER_BLOCKING_SAFETY_FIXES),
        ("dry_run_position_mutation_block_safety_verified", PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_POSITION_MUTATION_BLOCK_UNSAFE, PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_POSITION_MUTATION_BLOCK_SAFETY_FIXES),
        ("dry_run_observability_safety_verified", PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_OBSERVABILITY_INCOMPLETE, PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_OBSERVABILITY_SAFETY_FIXES),
        ("dry_run_journal_safety_verified", PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_JOURNAL_INCOMPLETE, PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_JOURNAL_SAFETY_FIXES),
        ("dry_run_human_approval_safety_verified", PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_HUMAN_APPROVAL_MISSING, PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_HUMAN_APPROVAL_SAFETY_FIXES),
        ("dry_run_stop_conditions_safety_verified", PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_STOP_CONDITIONS_MISSING, PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_STOP_CONDITION_SAFETY_FIXES),
        ("dry_run_success_failure_criteria_safety_verified", PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_SUCCESS_FAILURE_CRITERIA_UNSAFE, PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_SUCCESS_FAILURE_CRITERIA_SAFETY_FIXES),
    ],
)
def test_required_safety_sections_are_enforced(field, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_safety_gate(_ready_input(**{field: False}))

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is PaperBrokerReadOnlyConnectionDryRunSafetyGateState.DRY_RUN_SAFETY_BLOCKED


@pytest.mark.parametrize(
    ("overrides", "risk"),
    [
        ({"real_execution_requested": True}, PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"broker_connection_requested": True}, PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"api_key_read_requested": True}, PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"env_var_read_requested": True}, PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"hardcoded_secret_detected": True}, PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"network_transport_requested": True}, PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"order_execution_requested": True}, PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"position_mutation_requested": True}, PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"account_access_requested": True}, PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"dry_run_executed": True}, PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"data_access_requested": True}, PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DATA_ACCESS_VIOLATION),
    ],
)
def test_boundary_violations_are_detected(overrides, risk):
    result = evaluate_paper_broker_read_only_connection_dry_run_safety_gate(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_BOUNDARY_SAFETY_FIXES


def test_premature_dry_run_preparation_is_detected():
    risks = detect_dry_run_safety_gate_risks(
        _ready_input(paper_broker_read_only_connection_dry_run_preparation_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION in risks


def test_recommendations_map_risks_to_actions():
    recommendations = generate_dry_run_safety_gate_recommendations(_ready_input(dry_run_network_block_safety_verified=False))

    assert PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION in recommendations
    assert PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.BLOCK_DRY_RUN_NETWORK in recommendations


def test_nominal_recommendations_approve_next_preparation():
    recommendations = generate_dry_run_safety_gate_recommendations(_ready_input())

    assert recommendations == (
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE_SUITE,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION,
    )


def test_markdown_render_includes_decision_score_and_boundaries():
    result = evaluate_paper_broker_read_only_connection_dry_run_safety_gate(_ready_input())
    markdown = render_paper_broker_read_only_connection_dry_run_safety_gate_markdown(result)

    assert "# Paper Broker Read-Only Connection Dry Run Safety Gate" in markdown
    assert "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE" in markdown
    assert "Safety gate score: 100" in markdown
    assert "No HTTP, websocket, socket, network transport, or external API" in markdown
    assert "No data/ access" in markdown


def test_mapping_input_is_supported():
    data = dict(_ready_input().__dict__)
    result = evaluate_paper_broker_read_only_connection_dry_run_safety_gate(data)

    assert result.safety_gate_score == 100
    assert result.risks == ()


def test_input_without_dry_run_plan_is_invalid():
    result = evaluate_paper_broker_read_only_connection_dry_run_safety_gate(
        _ready_input(paper_broker_read_only_connection_dry_run_plan=None)
    )

    assert result.state is PaperBrokerReadOnlyConnectionDryRunSafetyGateState.DRY_RUN_SAFETY_INPUT_INVALID
    assert PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_PLAN_NOT_APPROVED in result.risks


def test_source_does_not_open_runtime_transports_or_data_access():
    source_path = Path("src/agicore/trading/paper_broker_read_only_connection_dry_run_safety_gate.py")
    source = source_path.read_text(encoding="utf-8")

    assert "import requests" not in source
    assert "import socket" not in source
    assert "websocket" in source
    assert "os.environ" not in source
    assert "Path('data" not in source
    assert "Path(\"data" not in source
