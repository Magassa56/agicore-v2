from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_execution_plan import (
    compute_controlled_execution_plan_score,
    define_controlled_account_read_only_policy,
    define_controlled_audit_plan,
    define_controlled_abort_policy,
    define_controlled_credentials_reference_policy,
    define_controlled_execution_preconditions,
    define_controlled_execution_scope,
    define_controlled_execution_sequence,
    define_controlled_failure_criteria,
    define_controlled_go_no_go_policy,
    define_controlled_http_websocket_socket_block_policy,
    define_controlled_human_approval_plan,
    define_controlled_journal_plan,
    define_controlled_market_data_read_only_policy,
    define_controlled_network_block_policy,
    define_controlled_no_secret_read_policy,
    define_controlled_observability_plan,
    define_controlled_order_blocking_policy,
    define_controlled_position_mutation_block_policy,
    define_controlled_stop_conditions_plan,
    define_controlled_success_criteria,
    detect_controlled_execution_plan_risks,
    evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_plan,
    generate_controlled_execution_plan_recommendations,
    render_paper_broker_read_only_connection_dry_run_controlled_execution_plan_markdown,
    validate_dry_run_execution_final_safety_gate_approval,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_execution_plan_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanInput,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRecommendation,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanState,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_execution_final_safety_gate import (
    evaluate_paper_broker_read_only_connection_dry_run_execution_final_safety_gate,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_execution_final_safety_gate import (
    _ready_input as _final_safety_gate_ready_input,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _final_safety_gate_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_final_safety_gate(_final_safety_gate_ready_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_dry_run_execution_final_safety_gate": _final_safety_gate_result(),
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
        "dry_run_execution_final_safety_gate_approved": True,
        "controlled_execution_scope_defined": True,
        "controlled_execution_sequence_defined": True,
        "controlled_execution_preconditions_defined": True,
        "controlled_credentials_reference_policy_defined": True,
        "controlled_credentials_reference_only": True,
        "controlled_no_secret_read_policy_defined": True,
        "controlled_network_block_policy_defined": True,
        "controlled_network_blocked": True,
        "controlled_http_websocket_socket_block_policy_defined": True,
        "controlled_http_blocked": True,
        "controlled_websocket_blocked": True,
        "controlled_socket_blocked": True,
        "controlled_external_api_blocked": True,
        "controlled_account_read_only_policy_defined": True,
        "controlled_active_account_access_blocked": True,
        "controlled_account_mutations_blocked": True,
        "controlled_market_data_read_only_policy_defined": True,
        "controlled_market_data_live_subscription_blocked": True,
        "controlled_market_data_network_request_blocked": True,
        "controlled_order_blocking_policy_defined": True,
        "controlled_order_execution_blocked": True,
        "controlled_cancel_replace_blocked": True,
        "controlled_position_mutation_block_policy_defined": True,
        "controlled_position_mutation_blocked": True,
        "controlled_observability_plan_defined": True,
        "controlled_journal_plan_defined": True,
        "controlled_human_approval_plan_defined": True,
        "controlled_human_approval_required": True,
        "controlled_stop_conditions_plan_defined": True,
        "controlled_success_criteria_defined": True,
        "controlled_failure_criteria_defined": True,
        "controlled_audit_plan_defined": True,
        "controlled_go_no_go_policy_defined": True,
        "controlled_abort_policy_defined": True,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "controlled_plan_only": True,
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
    return PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanInput(**payload)


def test_nominal_controlled_plan_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_plan(_ready_input())

    assert result.state is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN
    assert result.controlled_plan_score == 100
    assert result.risks == ()
    assert result.controlled_go_no_go_policy.defined is True
    assert result.offline_only is True


def test_define_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_dry_run_execution_final_safety_gate_approval(data) is True
    assert define_controlled_execution_scope(data).dry_run_execution_disabled is True
    assert define_controlled_execution_sequence(data).connection_not_executed is True
    assert define_controlled_execution_preconditions(data).human_approval_required is True
    assert define_controlled_credentials_reference_policy(data).reference_only is True
    assert define_controlled_no_secret_read_policy(data).no_api_key_read is True
    assert define_controlled_network_block_policy(data).external_api_blocked is True
    assert define_controlled_http_websocket_socket_block_policy(data).socket_blocked is True
    assert define_controlled_account_read_only_policy(data).active_account_access_blocked is True
    assert define_controlled_market_data_read_only_policy(data).network_request_blocked is True
    assert define_controlled_order_blocking_policy(data).order_execution_blocked is True
    assert define_controlled_position_mutation_block_policy(data).position_mutation_blocked is True
    assert define_controlled_observability_plan(data).offline_events_defined is True
    assert define_controlled_journal_plan(data).offline_journal_required is True
    assert define_controlled_human_approval_plan(data).human_approval_required is True
    assert define_controlled_stop_conditions_plan(data).stop_on_network_request is True
    assert define_controlled_success_criteria(data).success_requires_all_guards_verified is True
    assert define_controlled_failure_criteria(data).failure_on_network_request is True
    assert define_controlled_audit_plan(data).offline_evidence_required is True
    assert define_controlled_go_no_go_policy(data).human_go_required is True
    assert define_controlled_abort_policy(data).abort_on_network_request is True
    assert compute_controlled_execution_plan_score(data).overall_score == 100


def test_final_safety_gate_not_approved_blocks_controlled_plan():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_plan(
        _ready_input(
            paper_broker_read_only_connection_dry_run_execution_final_safety_gate=_final_safety_gate_result(
                state="FINAL_SAFETY_GATE_BLOCKED",
                decision="REQUIRE_FINAL_GO_NO_GO_FIXES",
                risks=("FINAL_GO_NO_GO_POLICY_MISSING",),
            ),
            dry_run_execution_final_safety_gate_approved=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.DRY_RUN_EXECUTION_FINAL_SAFETY_GATE_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_FINAL_SAFETY_GATE_FIXES


@pytest.mark.parametrize(
    ("overrides", "risk", "decision"),
    [
        ({"controlled_execution_scope_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_EXECUTION_SCOPE_UNCLEAR, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_SCOPE_FIXES),
        ({"controlled_execution_sequence_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_EXECUTION_SEQUENCE_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_SEQUENCE_FIXES),
        ({"controlled_execution_preconditions_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_EXECUTION_PRECONDITION_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_PRECONDITION_FIXES),
        ({"controlled_credentials_reference_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_CREDENTIAL_POLICY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_CREDENTIAL_POLICY_FIXES),
        ({"controlled_no_secret_read_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_SECRET_READ_POLICY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_NO_SECRET_READ_FIXES),
        ({"controlled_network_block_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_NETWORK_NOT_BLOCKED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_NETWORK_BLOCK_FIXES),
        ({"controlled_http_websocket_socket_block_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_NETWORK_BLOCK_FIXES),
        ({"controlled_account_read_only_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_ACCOUNT_READ_ONLY_FIXES),
        ({"controlled_market_data_read_only_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_MARKET_DATA_READ_ONLY_FIXES),
        ({"controlled_order_blocking_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_ORDER_BLOCKING_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_ORDER_BLOCKING_FIXES),
        ({"controlled_position_mutation_block_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_POSITION_MUTATION_BLOCK_FIXES),
        ({"controlled_observability_plan_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_OBSERVABILITY_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_OBSERVABILITY_FIXES),
        ({"controlled_journal_plan_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_JOURNAL_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_JOURNAL_FIXES),
        ({"controlled_human_approval_plan_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_HUMAN_APPROVAL_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_HUMAN_APPROVAL_FIXES),
        ({"controlled_stop_conditions_plan_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_STOP_CONDITIONS_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_STOP_CONDITION_FIXES),
        ({"controlled_success_criteria_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_SUCCESS_CRITERIA_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_SUCCESS_FAILURE_FIXES),
        ({"controlled_failure_criteria_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_FAILURE_CRITERIA_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_SUCCESS_FAILURE_FIXES),
        ({"controlled_audit_plan_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_AUDIT_PLAN_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_AUDIT_FIXES),
        ({"controlled_go_no_go_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_GO_NO_GO_POLICY_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_GO_NO_GO_FIXES),
        ({"controlled_abort_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_ABORT_POLICY_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.REQUIRE_CONTROLLED_ABORT_POLICY_FIXES),
    ],
)
def test_controlled_plan_gaps_are_enforced(overrides, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_plan(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanState.CONTROLLED_EXECUTION_PLAN_BLOCKED


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
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_plan(_ready_input(**overrides))

    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN


def test_data_access_is_blocked():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_plan(_ready_input(data_access_requested=True))

    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN


def test_premature_controlled_safety_gate_is_detected():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_plan(
        _ready_input(paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE in result.risks


def test_recommendations_and_markdown_are_rendered():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_plan(_ready_input())
    markdown = render_paper_broker_read_only_connection_dry_run_controlled_execution_plan_markdown(result)

    assert generate_controlled_execution_plan_recommendations(_ready_input()) == (
        PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN_SUITE,
        PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE,
    )
    assert "Paper Broker Read-Only Connection Dry Run Controlled Execution Plan" in markdown
    assert "No broker" in markdown
    assert "controlled_go_no_go_policy" in markdown
    assert "controlled_abort_policy" in markdown


def test_mapping_input_and_missing_review_input():
    nominal = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_plan(dict(_ready_input().__dict__))
    missing = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_plan(None)

    assert nominal.controlled_plan_score == 100
    assert missing.state is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanState.CONTROLLED_EXECUTION_PLAN_INPUT_INVALID
    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.DRY_RUN_EXECUTION_FINAL_SAFETY_GATE_NOT_APPROVED in missing.risks


def test_risk_detection_helper_returns_tuple():
    risks = detect_controlled_execution_plan_risks(_ready_input(controlled_go_no_go_policy_defined=False))

    assert risks == (PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_GO_NO_GO_POLICY_MISSING,)


def test_source_has_no_real_io_or_network_imports():
    source = Path("src/agicore/trading/paper_broker_read_only_connection_dry_run_controlled_execution_plan.py").read_text()

    forbidden = ("import os", "import socket", "import requests", "from requests", "urllib", "http.client", "open(", "os.environ")
    for token in forbidden:
        assert token not in source
