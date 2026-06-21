from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_plan import (
    compute_read_only_connection_dry_run_plan_score,
    define_dry_run_account_read_only_policy,
    define_dry_run_credentials_reference_policy,
    define_dry_run_environment_boundaries,
    define_dry_run_failure_criteria,
    define_dry_run_http_websocket_socket_block_policy,
    define_dry_run_human_approval_plan,
    define_dry_run_journal_plan,
    define_dry_run_market_data_read_only_policy,
    define_dry_run_network_block_policy,
    define_dry_run_no_secret_read_policy,
    define_dry_run_observability_plan,
    define_dry_run_order_blocking_policy,
    define_dry_run_position_mutation_block_policy,
    define_dry_run_preconditions,
    define_dry_run_scope,
    define_dry_run_stop_conditions_plan,
    define_dry_run_success_criteria,
    detect_read_only_connection_dry_run_plan_risks,
    evaluate_paper_broker_read_only_connection_dry_run_plan,
    generate_read_only_connection_dry_run_plan_recommendations,
    render_paper_broker_read_only_connection_dry_run_plan_markdown,
    validate_connection_preparation_review_approval,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_plan_models import (
    PaperBrokerReadOnlyConnectionDryRunPlanDecision,
    PaperBrokerReadOnlyConnectionDryRunPlanInput,
    PaperBrokerReadOnlyConnectionDryRunPlanRecommendation,
    PaperBrokerReadOnlyConnectionDryRunPlanRisk,
    PaperBrokerReadOnlyConnectionDryRunPlanState,
)
from agicore.trading.paper_broker_read_only_connection_preparation_review import (
    evaluate_paper_broker_read_only_connection_preparation_review,
)
from tests.unit.trading.test_paper_broker_read_only_connection_preparation_review import (
    _ready_input as _review_ready_input,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _review_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_preparation_review(_review_ready_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_preparation_review": _review_result(),
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
        "connection_preparation_review_approved": True,
        "dry_run_scope_defined": True,
        "dry_run_environment_boundaries_defined": True,
        "dry_run_preconditions_defined": True,
        "dry_run_credentials_reference_policy_defined": True,
        "dry_run_credentials_reference_only": True,
        "dry_run_no_secret_read_policy_defined": True,
        "dry_run_secret_read_blocked": True,
        "dry_run_network_block_policy_defined": True,
        "dry_run_network_blocked": True,
        "dry_run_http_websocket_socket_block_policy_defined": True,
        "dry_run_http_blocked": True,
        "dry_run_websocket_blocked": True,
        "dry_run_socket_blocked": True,
        "dry_run_external_api_blocked": True,
        "dry_run_account_read_only_policy_defined": True,
        "dry_run_account_access_blocked": True,
        "dry_run_account_mutations_blocked": True,
        "dry_run_market_data_read_only_policy_defined": True,
        "dry_run_market_data_live_subscription_blocked": True,
        "dry_run_market_data_network_request_blocked": True,
        "dry_run_order_blocking_policy_defined": True,
        "dry_run_order_execution_blocked": True,
        "dry_run_cancel_replace_blocked": True,
        "dry_run_position_mutation_block_policy_defined": True,
        "dry_run_position_mutation_blocked": True,
        "dry_run_observability_plan_defined": True,
        "dry_run_journal_plan_defined": True,
        "dry_run_human_approval_plan_defined": True,
        "dry_run_human_approval_required": True,
        "dry_run_stop_conditions_plan_defined": True,
        "dry_run_success_criteria_defined": True,
        "dry_run_failure_criteria_defined": True,
        "paper_broker_read_only_connection_dry_run_safety_gate_requested": False,
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
    return PaperBrokerReadOnlyConnectionDryRunPlanInput(**payload)


def test_nominal_dry_run_plan_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_plan(_ready_input())

    assert result.state is PaperBrokerReadOnlyConnectionDryRunPlanState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunPlanDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN
    assert result.dry_run_plan_score == 100
    assert result.risks == ()
    assert result.offline_only is True
    assert result.no_secret_read_policy.policy_enforced is True
    assert result.network_block_policy.network_execution_blocked is True
    assert result.http_websocket_socket_block_policy.http_blocked is True
    assert result.order_blocking_policy.order_execution_blocked is True
    assert result.position_mutation_block_policy.position_mutation_blocked is True


def test_plan_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_connection_preparation_review_approval(data) is True
    assert define_dry_run_scope(data).defined is True
    assert define_dry_run_environment_boundaries(data).data_access_blocked is True
    assert define_dry_run_preconditions(data).human_approval_required is True
    assert define_dry_run_credentials_reference_policy(data).reference_only is True
    assert define_dry_run_no_secret_read_policy(data).no_api_key_read is True
    assert define_dry_run_network_block_policy(data).external_api_blocked is True
    assert define_dry_run_http_websocket_socket_block_policy(data).socket_blocked is True
    assert define_dry_run_account_read_only_policy(data).active_account_access_blocked is True
    assert define_dry_run_market_data_read_only_policy(data).network_request_blocked is True
    assert define_dry_run_order_blocking_policy(data).cancel_replace_blocked is True
    assert define_dry_run_position_mutation_block_policy(data).position_request_absent is True
    assert define_dry_run_observability_plan(data).defined is True
    assert define_dry_run_journal_plan(data).offline_journal_required is True
    assert define_dry_run_human_approval_plan(data).human_approval_required is True
    assert define_dry_run_stop_conditions_plan(data).stop_on_network_request is True
    assert define_dry_run_success_criteria(data).all_guards_verified is True
    assert define_dry_run_failure_criteria(data).fail_on_network_attempt is True
    assert compute_read_only_connection_dry_run_plan_score(data).overall_score == 100


def test_non_approved_preparation_review_blocks_plan():
    result = evaluate_paper_broker_read_only_connection_dry_run_plan(
        _ready_input(
            paper_broker_read_only_connection_preparation_review=_review_result(
                state="CONNECTION_PREPARATION_REVIEW_BLOCKED",
                decision="REQUIRE_NETWORK_BLOCK_GUARD_REVIEW_FIXES",
                risks=("NETWORK_EXECUTION_BLOCK_GUARD_REVIEW_FAILED",),
            ),
            connection_preparation_review_approved=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionDryRunPlanRisk.CONNECTION_PREPARATION_REVIEW_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_CONNECTION_PREPARATION_REVIEW_FIXES


@pytest.mark.parametrize(
    ("overrides", "risk", "decision"),
    [
        (
            {"dry_run_scope_defined": False},
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_SCOPE_UNCLEAR,
            PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_SCOPE_FIXES,
        ),
        (
            {"dry_run_environment_boundaries_defined": False},
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_ENVIRONMENT_BOUNDARY_MISSING,
            PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_BOUNDARY_FIXES,
        ),
        (
            {"dry_run_preconditions_defined": False},
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_PRECONDITION_MISSING,
            PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_PRECONDITION_FIXES,
        ),
        (
            {"dry_run_credentials_reference_only": False},
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_CREDENTIAL_POLICY_UNSAFE,
            PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_CREDENTIAL_POLICY_FIXES,
        ),
        (
            {"dry_run_secret_read_blocked": False},
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_SECRET_READ_POLICY_UNSAFE,
            PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_NO_SECRET_READ_FIXES,
        ),
        (
            {"dry_run_network_blocked": False},
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_NETWORK_NOT_BLOCKED,
            PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_NETWORK_BLOCK_FIXES,
        ),
        (
            {"dry_run_websocket_blocked": False},
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED,
            PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_NETWORK_BLOCK_FIXES,
        ),
        (
            {"dry_run_account_access_blocked": False},
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_ACCOUNT_READ_ONLY_UNSAFE,
            PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_ACCOUNT_READ_ONLY_FIXES,
        ),
        (
            {"dry_run_market_data_network_request_blocked": False},
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_MARKET_DATA_READ_ONLY_UNSAFE,
            PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_MARKET_DATA_READ_ONLY_FIXES,
        ),
        (
            {"dry_run_order_execution_blocked": False},
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_ORDER_BLOCKING_UNSAFE,
            PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_ORDER_BLOCKING_FIXES,
        ),
        (
            {"dry_run_position_mutation_blocked": False},
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_POSITION_MUTATION_BLOCK_UNSAFE,
            PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_POSITION_MUTATION_BLOCK_FIXES,
        ),
        (
            {"dry_run_observability_plan_defined": False},
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_OBSERVABILITY_PLAN_MISSING,
            PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_OBSERVABILITY_FIXES,
        ),
        (
            {"dry_run_journal_plan_defined": False},
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_JOURNAL_PLAN_MISSING,
            PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_JOURNAL_FIXES,
        ),
        (
            {"dry_run_human_approval_plan_defined": False},
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_HUMAN_APPROVAL_MISSING,
            PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_HUMAN_APPROVAL_FIXES,
        ),
        (
            {"dry_run_success_criteria_defined": False},
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_SUCCESS_CRITERIA_MISSING,
            PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_SUCCESS_FAILURE_CRITERIA_FIXES,
        ),
        (
            {"dry_run_failure_criteria_defined": False},
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_FAILURE_CRITERIA_MISSING,
            PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_SUCCESS_FAILURE_CRITERIA_FIXES,
        ),
    ],
)

def test_policy_gaps_block_with_specific_decision(overrides, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_plan(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is PaperBrokerReadOnlyConnectionDryRunPlanState.DRY_RUN_PLAN_BLOCKED


def test_stop_conditions_missing_are_detected():
    result = evaluate_paper_broker_read_only_connection_dry_run_plan(
        _ready_input(dry_run_stop_conditions_plan_defined=False)
    )

    assert PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_STOP_CONDITIONS_MISSING in result.risks
    assert result.decision in {
        PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_PRECONDITION_FIXES,
        PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_STOP_CONDITION_FIXES,
    }


@pytest.mark.parametrize(
    ("overrides", "risk"),
    [
        ({"real_execution_requested": True}, PaperBrokerReadOnlyConnectionDryRunPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"broker_connection_requested": True}, PaperBrokerReadOnlyConnectionDryRunPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"api_key_read_requested": True}, PaperBrokerReadOnlyConnectionDryRunPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"env_var_read_requested": True}, PaperBrokerReadOnlyConnectionDryRunPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"hardcoded_secret_detected": True}, PaperBrokerReadOnlyConnectionDryRunPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"network_transport_requested": True}, PaperBrokerReadOnlyConnectionDryRunPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"order_execution_requested": True}, PaperBrokerReadOnlyConnectionDryRunPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"position_mutation_requested": True}, PaperBrokerReadOnlyConnectionDryRunPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"account_access_requested": True}, PaperBrokerReadOnlyConnectionDryRunPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"dry_run_executed": True}, PaperBrokerReadOnlyConnectionDryRunPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"data_access_requested": True}, PaperBrokerReadOnlyConnectionDryRunPlanRisk.DATA_ACCESS_VIOLATION),
    ],
)

def test_boundary_violations_are_detected(overrides, risk):
    result = evaluate_paper_broker_read_only_connection_dry_run_plan(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_BOUNDARY_FIXES


def test_premature_safety_gate_is_detected():
    risks = detect_read_only_connection_dry_run_plan_risks(
        _ready_input(paper_broker_read_only_connection_dry_run_safety_gate_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionDryRunPlanRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE in risks


def test_recommendations_map_risks_to_actions():
    recommendations = generate_read_only_connection_dry_run_plan_recommendations(
        _ready_input(dry_run_network_blocked=False)
    )

    assert PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE in recommendations
    assert PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.BLOCK_DRY_RUN_NETWORK in recommendations


def test_nominal_recommendations_approve_next_safety_gate():
    recommendations = generate_read_only_connection_dry_run_plan_recommendations(_ready_input())

    assert recommendations == (
        PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN_SUITE,
        PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE,
    )


def test_markdown_render_includes_decision_score_and_boundaries():
    result = evaluate_paper_broker_read_only_connection_dry_run_plan(_ready_input())
    markdown = render_paper_broker_read_only_connection_dry_run_plan_markdown(result)

    assert "# Paper Broker Read-Only Connection Dry Run Plan" in markdown
    assert "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN" in markdown
    assert "Dry run plan score: 100" in markdown
    assert "No HTTP, websocket, socket, network transport, or external API" in markdown
    assert "No data/ access" in markdown


def test_mapping_input_is_supported():
    data = dict(_ready_input().__dict__)
    result = evaluate_paper_broker_read_only_connection_dry_run_plan(data)

    assert result.dry_run_plan_score == 100
    assert result.risks == ()


def test_input_without_preparation_review_is_invalid():
    result = evaluate_paper_broker_read_only_connection_dry_run_plan(
        _ready_input(paper_broker_read_only_connection_preparation_review=None)
    )

    assert result.state is PaperBrokerReadOnlyConnectionDryRunPlanState.DRY_RUN_PLAN_INPUT_INVALID
    assert PaperBrokerReadOnlyConnectionDryRunPlanRisk.CONNECTION_PREPARATION_REVIEW_NOT_APPROVED in result.risks


def test_source_does_not_open_runtime_transports_or_data_access():
    source_path = Path("src/agicore/trading/paper_broker_read_only_connection_dry_run_plan.py")
    source = source_path.read_text(encoding="utf-8")

    assert "import requests" not in source
    assert "import socket" not in source
    assert "websocket" in source
    assert "os.environ" not in source
    assert "Path('data" not in source
    assert "Path(\"data" not in source
