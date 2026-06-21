from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_execution_plan import (
    compute_read_only_connection_dry_run_execution_plan_score,
    define_dry_run_execution_account_read_only_policy,
    define_dry_run_execution_audit_plan,
    define_dry_run_execution_credentials_reference_policy,
    define_dry_run_execution_failure_criteria,
    define_dry_run_execution_http_websocket_socket_block_policy,
    define_dry_run_execution_human_approval_plan,
    define_dry_run_execution_journal_plan,
    define_dry_run_execution_market_data_read_only_policy,
    define_dry_run_execution_network_block_policy,
    define_dry_run_execution_no_secret_read_policy,
    define_dry_run_execution_observability_plan,
    define_dry_run_execution_order_blocking_policy,
    define_dry_run_execution_position_mutation_block_policy,
    define_dry_run_execution_preconditions,
    define_dry_run_execution_scope,
    define_dry_run_execution_sequence,
    define_dry_run_execution_stop_conditions_plan,
    define_dry_run_execution_success_criteria,
    detect_read_only_connection_dry_run_execution_plan_risks,
    evaluate_paper_broker_read_only_connection_dry_run_execution_plan,
    generate_read_only_connection_dry_run_execution_plan_recommendations,
    render_paper_broker_read_only_connection_dry_run_execution_plan_markdown,
    validate_dry_run_preparation_review_approval,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_execution_plan_models import (
    PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision,
    PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput,
    PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation,
    PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk,
    PaperBrokerReadOnlyConnectionDryRunExecutionPlanState,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_preparation_review import (
    evaluate_paper_broker_read_only_connection_dry_run_preparation_review,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_preparation_review import (
    _ready_input as _review_ready_input,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _preparation_review_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_preparation_review(_review_ready_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_dry_run_preparation_review": _preparation_review_result(),
        "paper_broker_read_only_connection_dry_run_preparation": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW",
            "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION",
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
        "paper_broker_read_only_connection_preparation": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW"),
        "paper_broker_read_only_connection_safety_gate": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION"),
        "paper_broker_read_only_connection_plan": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE"),
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
        "dry_run_preparation_review_approved": True,
        "dry_run_execution_scope_defined": True,
        "dry_run_execution_sequence_defined": True,
        "dry_run_execution_preconditions_defined": True,
        "dry_run_execution_credentials_policy_defined": True,
        "dry_run_execution_credentials_reference_only": True,
        "dry_run_execution_no_secret_read_policy_defined": True,
        "dry_run_execution_no_secret_read_enforced": True,
        "dry_run_execution_network_block_policy_defined": True,
        "dry_run_execution_network_blocked": True,
        "dry_run_execution_http_websocket_socket_block_policy_defined": True,
        "dry_run_execution_http_blocked": True,
        "dry_run_execution_websocket_blocked": True,
        "dry_run_execution_socket_blocked": True,
        "dry_run_execution_external_api_blocked": True,
        "dry_run_execution_account_read_only_policy_defined": True,
        "dry_run_execution_account_access_blocked": True,
        "dry_run_execution_account_mutations_blocked": True,
        "dry_run_execution_market_data_read_only_policy_defined": True,
        "dry_run_execution_market_data_live_subscription_blocked": True,
        "dry_run_execution_market_data_network_request_blocked": True,
        "dry_run_execution_order_blocking_policy_defined": True,
        "dry_run_execution_order_execution_blocked": True,
        "dry_run_execution_cancel_replace_blocked": True,
        "dry_run_execution_position_mutation_block_policy_defined": True,
        "dry_run_execution_position_mutation_blocked": True,
        "dry_run_execution_observability_plan_defined": True,
        "dry_run_execution_journal_plan_defined": True,
        "dry_run_execution_human_approval_plan_defined": True,
        "dry_run_execution_human_approval_required": True,
        "dry_run_execution_stop_conditions_plan_defined": True,
        "dry_run_execution_success_criteria_defined": True,
        "dry_run_execution_failure_criteria_defined": True,
        "dry_run_execution_audit_plan_defined": True,
        "paper_broker_read_only_connection_dry_run_execution_safety_gate_requested": False,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "plan_only": True,
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
    return PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput(**payload)


def test_nominal_execution_plan_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_plan(_ready_input())

    assert result.state is PaperBrokerReadOnlyConnectionDryRunExecutionPlanState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN
    assert result.execution_plan_score == 100
    assert result.risks == ()
    assert result.offline_only is True
    assert result.dry_run_execution_scope.no_real_execution is True
    assert result.dry_run_execution_network_block_policy.network_execution_blocked is True
    assert result.dry_run_execution_audit_plan.audit_events_defined is True


def test_definition_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_dry_run_preparation_review_approval(data) is True
    assert define_dry_run_execution_scope(data).defined is True
    assert define_dry_run_execution_sequence(data).dry_run_not_executed is True
    assert define_dry_run_execution_preconditions(data).fail_closed is True
    assert define_dry_run_execution_credentials_reference_policy(data).reference_only is True
    assert define_dry_run_execution_no_secret_read_policy(data).policy_enforced is True
    assert define_dry_run_execution_network_block_policy(data).external_api_blocked is True
    assert define_dry_run_execution_http_websocket_socket_block_policy(data).socket_blocked is True
    assert define_dry_run_execution_account_read_only_policy(data).active_account_access_blocked is True
    assert define_dry_run_execution_market_data_read_only_policy(data).network_request_blocked is True
    assert define_dry_run_execution_order_blocking_policy(data).order_execution_blocked is True
    assert define_dry_run_execution_position_mutation_block_policy(data).position_mutation_blocked is True
    assert define_dry_run_execution_observability_plan(data).offline_events_defined is True
    assert define_dry_run_execution_journal_plan(data).offline_journal_required is True
    assert define_dry_run_execution_human_approval_plan(data).human_approval_required is True
    assert define_dry_run_execution_stop_conditions_plan(data).stop_on_network_request is True
    assert define_dry_run_execution_success_criteria(data).requires_no_real_connection is True
    assert define_dry_run_execution_failure_criteria(data).failure_on_data_access is True
    assert define_dry_run_execution_audit_plan(data).offline_evidence_required is True
    assert compute_read_only_connection_dry_run_execution_plan_score(data).overall_score == 100


def test_preparation_review_not_approved_blocks_execution_plan():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_plan(
        _ready_input(
            paper_broker_read_only_connection_dry_run_preparation_review=_preparation_review_result(
                state="DRY_RUN_PREPARATION_REVIEW_BLOCKED",
                decision="REQUIRE_DRY_RUN_ADAPTER_BOUNDARY_REVIEW_FIXES",
                risks=("REAL_EXECUTION_BOUNDARY_VIOLATION",),
            ),
            dry_run_preparation_review_approved=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_PREPARATION_REVIEW_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_PREPARATION_REVIEW_FIXES


@pytest.mark.parametrize(
    ("overrides", "risk", "decision"),
    [
        ({"dry_run_execution_scope_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_SCOPE_UNCLEAR, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_SCOPE_FIXES),
        ({"dry_run_execution_sequence_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_SEQUENCE_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_SEQUENCE_FIXES),
        ({"dry_run_execution_preconditions_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_PRECONDITION_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_PRECONDITION_FIXES),
        ({"dry_run_execution_credentials_reference_only": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_CREDENTIAL_POLICY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_CREDENTIAL_POLICY_FIXES),
        ({"dry_run_execution_no_secret_read_enforced": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_SECRET_READ_POLICY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_NO_SECRET_READ_FIXES),
        ({"dry_run_execution_network_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_NETWORK_NOT_BLOCKED, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_FIXES),
        ({"dry_run_execution_websocket_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_FIXES),
        ({"dry_run_execution_account_access_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_FIXES),
        ({"dry_run_execution_market_data_network_request_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_FIXES),
        ({"dry_run_execution_order_execution_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_ORDER_BLOCKING_FIXES),
        ({"dry_run_execution_position_mutation_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_FIXES),
        ({"dry_run_execution_observability_plan_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_OBSERVABILITY_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_OBSERVABILITY_FIXES),
        ({"dry_run_execution_journal_plan_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_JOURNAL_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_JOURNAL_FIXES),
        ({"dry_run_execution_human_approval_required": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL_FIXES),
        ({"dry_run_execution_stop_conditions_plan_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_STOP_CONDITION_FIXES),
        ({"dry_run_execution_success_criteria_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_SUCCESS_CRITERIA_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_FIXES),
        ({"dry_run_execution_failure_criteria_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_FAILURE_CRITERIA_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_FIXES),
        ({"dry_run_execution_audit_plan_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_AUDIT_PLAN_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_AUDIT_FIXES),
    ],
)
def test_execution_plan_gaps_are_enforced(overrides, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_plan(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is PaperBrokerReadOnlyConnectionDryRunExecutionPlanState.DRY_RUN_EXECUTION_PLAN_BLOCKED


@pytest.mark.parametrize(
    ("overrides", "risk"),
    [
        ({"real_execution_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"broker_connection_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"api_key_read_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"env_var_read_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"hardcoded_secret_detected": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"network_transport_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"order_execution_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"position_mutation_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"account_access_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"dry_run_executed": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"data_access_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DATA_ACCESS_VIOLATION),
    ],
)
def test_boundary_violations_are_detected(overrides, risk):
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_plan(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_SCOPE_FIXES


def test_premature_execution_safety_gate_is_detected():
    risks = detect_read_only_connection_dry_run_execution_plan_risks(
        _ready_input(paper_broker_read_only_connection_dry_run_execution_safety_gate_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE in risks


def test_recommendations_map_risks_to_actions():
    recommendations = generate_read_only_connection_dry_run_execution_plan_recommendations(
        _ready_input(dry_run_execution_network_blocked=False)
    )

    assert PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE in recommendations
    assert PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.BLOCK_DRY_RUN_EXECUTION_NETWORK in recommendations


def test_nominal_recommendations_approve_safety_gate():
    recommendations = generate_read_only_connection_dry_run_execution_plan_recommendations(_ready_input())

    assert recommendations == (
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN_SUITE,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE,
    )


def test_markdown_render_includes_decision_score_and_boundaries():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_plan(_ready_input())
    markdown = render_paper_broker_read_only_connection_dry_run_execution_plan_markdown(result)

    assert "# Paper Broker Read-Only Connection Dry Run Execution Plan" in markdown
    assert "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN" in markdown
    assert "Execution plan score: 100" in markdown
    assert "No HTTP, websocket, socket, network transport, or external API" in markdown
    assert "No data/ access" in markdown


def test_mapping_input_is_supported():
    data = dict(_ready_input().__dict__)
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_plan(data)

    assert result.execution_plan_score == 100
    assert result.risks == ()


def test_input_without_preparation_review_is_invalid():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_plan(
        _ready_input(paper_broker_read_only_connection_dry_run_preparation_review=None)
    )

    assert result.state is PaperBrokerReadOnlyConnectionDryRunExecutionPlanState.DRY_RUN_EXECUTION_PLAN_INPUT_INVALID
    assert PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_PREPARATION_REVIEW_NOT_APPROVED in result.risks


def test_source_does_not_open_runtime_transports_or_data_access():
    source_path = Path("src/agicore/trading/paper_broker_read_only_connection_dry_run_execution_plan.py")
    source = source_path.read_text(encoding="utf-8")

    assert "import requests" not in source
    assert "import socket" not in source
    assert "websocket" in source
    assert "os.environ" not in source
    assert "Path('data" not in source
    assert 'Path("data' not in source
