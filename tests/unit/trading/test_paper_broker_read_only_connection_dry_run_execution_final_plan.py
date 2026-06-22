from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_execution_final_plan import (
    compute_dry_run_execution_final_plan_score,
    define_final_account_read_only_policy,
    define_final_audit_plan,
    define_final_credentials_reference_policy,
    define_final_dry_run_execution_preconditions,
    define_final_dry_run_execution_scope,
    define_final_dry_run_execution_sequence,
    define_final_failure_criteria,
    define_final_go_no_go_policy,
    define_final_http_websocket_socket_block_policy,
    define_final_human_approval_plan,
    define_final_journal_plan,
    define_final_market_data_read_only_policy,
    define_final_network_block_policy,
    define_final_no_secret_read_policy,
    define_final_observability_plan,
    define_final_order_blocking_policy,
    define_final_position_mutation_block_policy,
    define_final_stop_conditions_plan,
    define_final_success_criteria,
    detect_dry_run_execution_final_plan_risks,
    evaluate_paper_broker_read_only_connection_dry_run_execution_final_plan,
    generate_dry_run_execution_final_plan_recommendations,
    render_paper_broker_read_only_connection_dry_run_execution_final_plan_markdown,
    validate_dry_run_execution_preparation_review_approval,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_execution_final_plan_models import (
    PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision,
    PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanInput,
    PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRecommendation,
    PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk,
    PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanState,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_execution_preparation_review import (
    evaluate_paper_broker_read_only_connection_dry_run_execution_preparation_review,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_execution_preparation_review import (
    _ready_input as _review_ready_input,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _review_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation_review(_review_ready_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_dry_run_execution_preparation_review": _review_result(),
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
        "dry_run_execution_preparation_review_approved": True,
        "final_execution_scope_defined": True,
        "final_execution_sequence_defined": True,
        "final_execution_preconditions_defined": True,
        "final_credentials_reference_policy_defined": True,
        "final_credentials_reference_only": True,
        "final_no_secret_read_policy_defined": True,
        "final_network_block_policy_defined": True,
        "final_network_blocked": True,
        "final_http_websocket_socket_block_policy_defined": True,
        "final_http_blocked": True,
        "final_websocket_blocked": True,
        "final_socket_blocked": True,
        "final_external_api_blocked": True,
        "final_account_read_only_policy_defined": True,
        "final_active_account_access_blocked": True,
        "final_account_mutations_blocked": True,
        "final_market_data_read_only_policy_defined": True,
        "final_market_data_live_subscription_blocked": True,
        "final_market_data_network_request_blocked": True,
        "final_order_blocking_policy_defined": True,
        "final_order_execution_blocked": True,
        "final_cancel_replace_blocked": True,
        "final_position_mutation_block_policy_defined": True,
        "final_position_mutation_blocked": True,
        "final_observability_plan_defined": True,
        "final_journal_plan_defined": True,
        "final_human_approval_plan_defined": True,
        "final_human_approval_required": True,
        "final_stop_conditions_plan_defined": True,
        "final_success_criteria_defined": True,
        "final_failure_criteria_defined": True,
        "final_audit_plan_defined": True,
        "final_go_no_go_policy_defined": True,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "final_plan_only": True,
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
    return PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanInput(**payload)


def test_nominal_final_plan_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_final_plan(_ready_input())

    assert result.state is PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN
    assert result.final_plan_score == 100
    assert result.risks == ()
    assert result.final_go_no_go_policy.defined is True
    assert result.offline_only is True


def test_define_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_dry_run_execution_preparation_review_approval(data) is True
    assert define_final_dry_run_execution_scope(data).dry_run_execution_disabled is True
    assert define_final_dry_run_execution_sequence(data).connection_not_executed is True
    assert define_final_dry_run_execution_preconditions(data).human_approval_required is True
    assert define_final_credentials_reference_policy(data).reference_only is True
    assert define_final_no_secret_read_policy(data).no_api_key_read is True
    assert define_final_network_block_policy(data).external_api_blocked is True
    assert define_final_http_websocket_socket_block_policy(data).socket_blocked is True
    assert define_final_account_read_only_policy(data).active_account_access_blocked is True
    assert define_final_market_data_read_only_policy(data).network_request_blocked is True
    assert define_final_order_blocking_policy(data).order_execution_blocked is True
    assert define_final_position_mutation_block_policy(data).position_mutation_blocked is True
    assert define_final_observability_plan(data).offline_events_defined is True
    assert define_final_journal_plan(data).offline_journal_required is True
    assert define_final_human_approval_plan(data).human_approval_required is True
    assert define_final_stop_conditions_plan(data).stop_on_network_request is True
    assert define_final_success_criteria(data).success_requires_all_guards_verified is True
    assert define_final_failure_criteria(data).failure_on_network_request is True
    assert define_final_audit_plan(data).offline_evidence_required is True
    assert define_final_go_no_go_policy(data).human_go_required is True
    assert compute_dry_run_execution_final_plan_score(data).overall_score == 100


def test_preparation_review_not_approved_blocks_final_plan():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_final_plan(
        _ready_input(
            paper_broker_read_only_connection_dry_run_execution_preparation_review=_review_result(
                state="DRY_RUN_EXECUTION_PREPARATION_REVIEW_BLOCKED",
                decision="REQUIRE_DRY_RUN_EXECUTION_RUNTIME_CONTRACT_REVIEW_FIXES",
                risks=("DRY_RUN_EXECUTION_RUNTIME_CONTRACT_REVIEW_FAILED",),
            ),
            dry_run_execution_preparation_review_approved=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.DRY_RUN_EXECUTION_PREPARATION_REVIEW_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_DRY_RUN_EXECUTION_PREPARATION_REVIEW_FIXES


@pytest.mark.parametrize(
    ("overrides", "risk", "decision"),
    [
        ({"final_execution_scope_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_EXECUTION_SCOPE_UNCLEAR, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_EXECUTION_SCOPE_FIXES),
        ({"final_execution_sequence_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_EXECUTION_SEQUENCE_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_EXECUTION_SEQUENCE_FIXES),
        ({"final_execution_preconditions_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_EXECUTION_PRECONDITION_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_EXECUTION_PRECONDITION_FIXES),
        ({"final_credentials_reference_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_CREDENTIAL_POLICY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_CREDENTIAL_POLICY_FIXES),
        ({"final_no_secret_read_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_SECRET_READ_POLICY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_NO_SECRET_READ_FIXES),
        ({"final_network_block_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_NETWORK_NOT_BLOCKED, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_NETWORK_BLOCK_FIXES),
        ({"final_http_websocket_socket_block_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_NETWORK_BLOCK_FIXES),
        ({"final_account_read_only_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_ACCOUNT_READ_ONLY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_ACCOUNT_READ_ONLY_FIXES),
        ({"final_market_data_read_only_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_MARKET_DATA_READ_ONLY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_MARKET_DATA_READ_ONLY_FIXES),
        ({"final_order_blocking_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_ORDER_BLOCKING_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_ORDER_BLOCKING_FIXES),
        ({"final_position_mutation_block_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_POSITION_MUTATION_BLOCK_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_POSITION_MUTATION_BLOCK_FIXES),
        ({"final_observability_plan_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_OBSERVABILITY_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_OBSERVABILITY_FIXES),
        ({"final_journal_plan_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_JOURNAL_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_JOURNAL_FIXES),
        ({"final_human_approval_plan_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_HUMAN_APPROVAL_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_HUMAN_APPROVAL_FIXES),
        ({"final_stop_conditions_plan_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_STOP_CONDITIONS_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_STOP_CONDITION_FIXES),
        ({"final_success_criteria_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_SUCCESS_CRITERIA_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_SUCCESS_FAILURE_FIXES),
        ({"final_failure_criteria_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_FAILURE_CRITERIA_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_SUCCESS_FAILURE_FIXES),
        ({"final_audit_plan_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_AUDIT_PLAN_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_AUDIT_FIXES),
        ({"final_go_no_go_policy_defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_GO_NO_GO_POLICY_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.REQUIRE_FINAL_GO_NO_GO_FIXES),
    ],
)
def test_final_plan_gaps_are_enforced(overrides, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_final_plan(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanState.DRY_RUN_EXECUTION_FINAL_PLAN_BLOCKED


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
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_final_plan(_ready_input(**overrides))

    assert PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN


def test_data_access_is_blocked():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_final_plan(_ready_input(data_access_requested=True))

    assert PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN


def test_premature_final_safety_gate_is_detected():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_final_plan(
        _ready_input(paper_broker_read_only_connection_dry_run_execution_final_safety_gate_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE in result.risks


def test_recommendations_and_markdown_are_rendered():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_final_plan(_ready_input())
    markdown = render_paper_broker_read_only_connection_dry_run_execution_final_plan_markdown(result)

    assert generate_dry_run_execution_final_plan_recommendations(_ready_input()) == (
        PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN_SUITE,
        PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE,
    )
    assert "Paper Broker Read-Only Connection Dry Run Execution Final Plan" in markdown
    assert "No broker" in markdown
    assert "final_go_no_go_policy" in markdown


def test_mapping_input_and_missing_review_input():
    nominal = evaluate_paper_broker_read_only_connection_dry_run_execution_final_plan(dict(_ready_input().__dict__))
    missing = evaluate_paper_broker_read_only_connection_dry_run_execution_final_plan(None)

    assert nominal.final_plan_score == 100
    assert missing.state is PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanState.DRY_RUN_EXECUTION_FINAL_PLAN_INPUT_INVALID
    assert PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.DRY_RUN_EXECUTION_PREPARATION_REVIEW_NOT_APPROVED in missing.risks


def test_risk_detection_helper_returns_tuple():
    risks = detect_dry_run_execution_final_plan_risks(_ready_input(final_go_no_go_policy_defined=False))

    assert risks == (PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_GO_NO_GO_POLICY_MISSING,)


def test_source_has_no_real_io_or_network_imports():
    source = Path("src/agicore/trading/paper_broker_read_only_connection_dry_run_execution_final_plan.py").read_text()

    forbidden = ("import os", "import socket", "import requests", "from requests", "urllib", "http.client", "open(", "os.environ")
    for token in forbidden:
        assert token not in source
