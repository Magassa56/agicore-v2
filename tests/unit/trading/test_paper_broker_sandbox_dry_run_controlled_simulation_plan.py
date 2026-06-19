import ast
from pathlib import Path

import pytest

from agicore.trading.paper_broker_sandbox_dry_run_controlled_simulation_plan import (
    compute_controlled_simulation_plan_score,
    define_controlled_simulation_abort_conditions,
    define_controlled_simulation_account_policy,
    define_controlled_simulation_boundaries,
    define_controlled_simulation_connection_policy,
    define_controlled_simulation_failure_criteria,
    define_controlled_simulation_human_supervision_policy,
    define_controlled_simulation_journal_policy,
    define_controlled_simulation_kill_switch_policy,
    define_controlled_simulation_observability_policy,
    define_controlled_simulation_order_policy,
    define_controlled_simulation_position_policy,
    define_controlled_simulation_rollback_policy,
    define_controlled_simulation_scenario,
    define_controlled_simulation_scope,
    define_controlled_simulation_session_limits,
    define_controlled_simulation_stop_conditions,
    define_controlled_simulation_success_criteria,
    detect_controlled_simulation_plan_risks,
    evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan,
    generate_controlled_simulation_plan_recommendations,
    render_paper_broker_sandbox_dry_run_controlled_simulation_plan_markdown,
    verify_execution_authorization_gate_readiness,
)
from agicore.trading.paper_broker_sandbox_dry_run_controlled_simulation_plan_models import (
    PaperBrokerSandboxDryRunControlledSimulationPlanDecision,
    PaperBrokerSandboxDryRunControlledSimulationPlanInput,
    PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation,
    PaperBrokerSandboxDryRunControlledSimulationPlanRisk,
    PaperBrokerSandboxDryRunControlledSimulationPlanState,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "risks": tuple(risks), "offline_only": True}
    if decision:
        payload["decision"] = decision
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_sandbox_dry_run_execution_authorization_gate": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN",
            "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE",
        ),
        "paper_broker_sandbox_dry_run_execution_review": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE",
            "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW",
        ),
        "paper_broker_sandbox_dry_run_pre_execution_check": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW",
            "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK",
        ),
        "paper_broker_sandbox_dry_run_review": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK",
            "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW",
        ),
        "paper_broker_sandbox_dry_run_plan": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW",
            "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PLAN",
        ),
        "paper_broker_sandbox_session_authorization_gate": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN",
            "APPROVE_PAPER_BROKER_SANDBOX_AUTHORIZATION_GATE",
        ),
        "paper_broker_sandbox_session_review": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_SESSION",
            "APPROVE_PAPER_BROKER_SANDBOX_SESSION",
        ),
        "paper_broker_sandbox_session_preparation": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_SESSION_REVIEW",
            "APPROVE_PAPER_BROKER_SANDBOX_SESSION_PREPARATION",
        ),
        "paper_runtime_forward_test_plan": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_SESSION",
            "APPROVE_PAPER_RUNTIME_FORWARD_TEST_PLAN",
        ),
        "supervised_paper_runtime_trial": _upstream("READY_FOR_PAPER_RUNTIME_FORWARD_TEST_PLAN"),
        "official_paper_validation_report": _upstream("READY_FOR_SUPERVISED_PAPER_RUNTIME_TRIAL"),
        "paper_runtime_validation": _upstream("READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT"),
        "paper_runtime_release_candidate": _upstream("READY_FOR_PAPER_RUNTIME_VALIDATION"),
        "paper_trading_runtime": _upstream("COMPLETED"),
        "paper_broker_adapter": _upstream("READY_FOR_ALPACA_PAPER_ADAPTER"),
        "alpaca_paper_adapter": _upstream("READY_FOR_END_TO_END_PAPER"),
        "broker_paper_sandbox": _upstream("READY_FOR_ALPACA_PAPER_CONNECTIVITY"),
        "mock_alpaca_session": _upstream("READY_FOR_SIMULATED_MARKET_SESSION"),
        "mock_connectivity_layer": _upstream("READY_FOR_MOCK_ALPACA_SESSION"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "execution_authorization_gate_approved": True,
        "execution_authorization_gate_reviewed": True,
        "controlled_simulation_scope_defined": True,
        "controlled_simulation_scope_clear": True,
        "controlled_simulation_boundaries_defined": True,
        "controlled_simulation_boundaries_complete": True,
        "controlled_simulation_scenario_defined": True,
        "controlled_simulation_scenario_complete": True,
        "controlled_simulation_session_limits_defined": True,
        "controlled_simulation_session_limits_complete": True,
        "controlled_simulation_connection_policy_defined": True,
        "controlled_simulation_connection_policy_complete": True,
        "controlled_simulation_order_policy_defined": True,
        "controlled_simulation_order_policy_complete": True,
        "controlled_simulation_position_policy_defined": True,
        "controlled_simulation_position_policy_complete": True,
        "controlled_simulation_account_policy_defined": True,
        "controlled_simulation_account_policy_complete": True,
        "controlled_simulation_observability_policy_defined": True,
        "controlled_simulation_observability_policy_complete": True,
        "controlled_simulation_rollback_policy_defined": True,
        "controlled_simulation_rollback_policy_complete": True,
        "controlled_simulation_kill_switch_policy_defined": True,
        "controlled_simulation_kill_switch_policy_complete": True,
        "controlled_simulation_human_supervision_policy_defined": True,
        "controlled_simulation_human_supervision_policy_complete": True,
        "controlled_simulation_journal_policy_defined": True,
        "controlled_simulation_journal_policy_complete": True,
        "controlled_simulation_stop_conditions_defined": True,
        "controlled_simulation_stop_conditions_complete": True,
        "controlled_simulation_abort_conditions_defined": True,
        "controlled_simulation_abort_conditions_complete": True,
        "controlled_simulation_success_criteria_defined": True,
        "controlled_simulation_success_criteria_complete": True,
        "controlled_simulation_failure_criteria_defined": True,
        "controlled_simulation_failure_criteria_complete": True,
        "paper_broker_sandbox_dry_run_controlled_simulation_plan_requested": True,
        "paper_broker_sandbox_dry_run_controlled_simulation_requested": False,
        "paper_broker_sandbox_dry_run_controlled_simulation_execution_requested": False,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "no_real_broker": True,
        "no_alpaca_real": True,
        "no_api_key_read": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_api": True,
        "no_external_ml": True,
        "no_external_llm": True,
        "no_live_execution": True,
        "no_dry_run_execution": True,
        "no_controlled_simulation_execution": True,
        "no_real_order": True,
        "no_real_account_access": True,
    }
    payload.update(overrides)
    return PaperBrokerSandboxDryRunControlledSimulationPlanInput(**payload)


def test_evaluate_approves_paper_broker_sandbox_dry_run_controlled_simulation_plan():
    result = evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input())

    assert result.state is PaperBrokerSandboxDryRunControlledSimulationPlanState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_REVIEW
    assert result.decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN
    assert result.risks == ()
    assert result.offline_only is True
    assert result.plan_score == 100


def test_controlled_simulation_plan_ready_state_below_review_threshold():
    result = evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(
        _ready_input(
            execution_authorization_gate_readiness_score=90,
            controlled_simulation_scope_score=90,
            controlled_simulation_boundaries_score=90,
            controlled_simulation_scenario_score=90,
            controlled_simulation_session_limits_score=90,
            controlled_simulation_connection_policy_score=90,
            controlled_simulation_order_policy_score=90,
            controlled_simulation_position_policy_score=90,
            controlled_simulation_account_policy_score=90,
            controlled_simulation_observability_policy_score=90,
            controlled_simulation_rollback_policy_score=90,
            controlled_simulation_kill_switch_policy_score=90,
            controlled_simulation_human_supervision_policy_score=90,
            controlled_simulation_journal_policy_score=90,
            controlled_simulation_stop_conditions_score=90,
            controlled_simulation_abort_conditions_score=90,
            controlled_simulation_success_criteria_score=90,
            controlled_simulation_failure_criteria_score=90,
        )
    )

    assert result.state is PaperBrokerSandboxDryRunControlledSimulationPlanState.CONTROLLED_SIMULATION_PLAN_READY
    assert result.decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN


def test_plan_sections_detect_primary_risks():
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.EXECUTION_AUTHORIZATION_GATE_NOT_APPROVED in verify_execution_authorization_gate_readiness(_ready_input(execution_authorization_gate_approved=False)).risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SCOPE_UNCLEAR in define_controlled_simulation_scope(_ready_input(controlled_simulation_scope_clear=False)).risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_BOUNDARY_GAP in define_controlled_simulation_boundaries(_ready_input(controlled_simulation_boundaries_complete=False)).risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SCENARIO_UNDEFINED in define_controlled_simulation_scenario(_ready_input(controlled_simulation_scenario_complete=False)).risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SESSION_LIMIT_GAP in define_controlled_simulation_session_limits(_ready_input(controlled_simulation_session_limits_complete=False)).risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_CONNECTION_POLICY_GAP in define_controlled_simulation_connection_policy(_ready_input(controlled_simulation_connection_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ORDER_POLICY_GAP in define_controlled_simulation_order_policy(_ready_input(controlled_simulation_order_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_POSITION_POLICY_GAP in define_controlled_simulation_position_policy(_ready_input(controlled_simulation_position_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ACCOUNT_POLICY_GAP in define_controlled_simulation_account_policy(_ready_input(controlled_simulation_account_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_OBSERVABILITY_GAP in define_controlled_simulation_observability_policy(_ready_input(controlled_simulation_observability_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ROLLBACK_GAP in define_controlled_simulation_rollback_policy(_ready_input(controlled_simulation_rollback_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_KILL_SWITCH_GAP in define_controlled_simulation_kill_switch_policy(_ready_input(controlled_simulation_kill_switch_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_HUMAN_SUPERVISION_GAP in define_controlled_simulation_human_supervision_policy(_ready_input(controlled_simulation_human_supervision_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_JOURNAL_GAP in define_controlled_simulation_journal_policy(_ready_input(controlled_simulation_journal_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_STOP_CONDITION_GAP in define_controlled_simulation_stop_conditions(_ready_input(controlled_simulation_stop_conditions_complete=False)).risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ABORT_CONDITION_GAP in define_controlled_simulation_abort_conditions(_ready_input(controlled_simulation_abort_conditions_complete=False)).risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_GAP in define_controlled_simulation_success_criteria(_ready_input(controlled_simulation_success_criteria_complete=False)).risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_GAP in define_controlled_simulation_failure_criteria(_ready_input(controlled_simulation_failure_criteria_complete=False)).risks


def test_detects_all_controlled_simulation_plan_risks():
    result = evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(
        _ready_input(
            execution_authorization_gate_approved=False,
            controlled_simulation_scope_clear=False,
            controlled_simulation_boundaries_complete=False,
            controlled_simulation_scenario_complete=False,
            controlled_simulation_session_limits_complete=False,
            controlled_simulation_connection_policy_complete=False,
            controlled_simulation_order_policy_complete=False,
            controlled_simulation_position_policy_complete=False,
            controlled_simulation_account_policy_complete=False,
            controlled_simulation_observability_policy_complete=False,
            controlled_simulation_rollback_policy_complete=False,
            controlled_simulation_kill_switch_policy_complete=False,
            controlled_simulation_human_supervision_policy_complete=False,
            controlled_simulation_journal_policy_complete=False,
            controlled_simulation_stop_conditions_complete=False,
            controlled_simulation_abort_conditions_complete=False,
            controlled_simulation_success_criteria_complete=False,
            controlled_simulation_failure_criteria_complete=False,
            paper_broker_sandbox_dry_run_controlled_simulation_plan_requested=False,
            paper_broker_sandbox_dry_run_controlled_simulation_execution_requested=True,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(PaperBrokerSandboxDryRunControlledSimulationPlanRisk)
    assert result.state is PaperBrokerSandboxDryRunControlledSimulationPlanState.NOT_READY
    assert result.decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.BLOCK_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION
    assert result.offline_only is False


def test_execution_authorization_gap_requires_gate_fixes_when_not_blocked():
    result = evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(execution_authorization_gate_approved=False))

    assert result.decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_EXECUTION_AUTHORIZATION_GATE_FIXES


def test_scope_boundary_scenario_and_limit_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_scope_clear=False)).decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_SCOPE_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_boundaries_complete=False)).decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_BOUNDARY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_scenario_complete=False)).decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_SCENARIO_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_session_limits_complete=False)).decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_SESSION_LIMIT_FIXES


def test_connection_order_position_and_account_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_connection_policy_complete=False)).decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_CONNECTION_POLICY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_order_policy_complete=False)).decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_ORDER_POLICY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_position_policy_complete=False)).decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_POSITION_POLICY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_account_policy_complete=False)).decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_ACCOUNT_POLICY_FIXES


def test_observability_rollback_kill_supervision_journal_stop_abort_and_criteria_decisions():
    assert evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_observability_policy_complete=False)).decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_OBSERVABILITY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_rollback_policy_complete=False)).decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_ROLLBACK_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_kill_switch_policy_complete=False)).decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_KILL_SWITCH_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_human_supervision_policy_complete=False)).decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_SUPERVISION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_journal_policy_complete=False)).decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_JOURNAL_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_stop_conditions_complete=False)).decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_STOP_CONDITION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_success_criteria_complete=False)).decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_STOP_CONDITION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_failure_criteria_complete=False)).decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_STOP_CONDITION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_abort_conditions_complete=False)).decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_ABORT_CONDITION_FIXES


def test_premature_controlled_simulation_execution_caps_score_and_blocks():
    data = _ready_input(paper_broker_sandbox_dry_run_controlled_simulation_execution_requested=True)
    risks = detect_controlled_simulation_plan_risks(data)
    score = compute_controlled_simulation_plan_score(data, risks)
    result = evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(data)

    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.PREMATURE_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_EXECUTION in risks
    assert score.overall_score <= 40
    assert result.decision is PaperBrokerSandboxDryRunControlledSimulationPlanDecision.BLOCK_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION


def test_no_controlled_simulation_execution_gap_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(no_controlled_simulation_execution=False))

    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_BOUNDARY_GAP in result.risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.PREMATURE_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_EXECUTION in result.risks
    assert result.offline_only is False


def test_upstream_network_leak_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(
        _ready_input(
            paper_broker_sandbox_dry_run_execution_authorization_gate=_upstream(
                "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN",
                risks=("NETWORK_LEAK",),
            )
        )
    )

    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_BOUNDARY_GAP in result.risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_CONNECTION_POLICY_GAP in result.risks
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRisk.PREMATURE_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_EXECUTION in result.risks
    assert result.offline_only is False


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_controlled_simulation_plan_recommendations(
        (
            PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_KILL_SWITCH_GAP,
            PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_KILL_SWITCH_GAP,
            PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ABORT_CONDITION_GAP,
            PaperBrokerSandboxDryRunControlledSimulationPlanRisk.PREMATURE_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_EXECUTION,
        ),
        PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_KILL_SWITCH_FIXES,
    )

    assert recommendations.count(PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_KILL_SWITCH_POLICY) == 1
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_ABORT_CONDITIONS in recommendations
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.DELAY_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_EXECUTION in recommendations
    assert PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.RUN_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_PLAN_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_controlled_simulation_plan_recommendations(
        (),
        PaperBrokerSandboxDryRunControlledSimulationPlanDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN,
    )

    assert PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_REVIEW in recommendations


def test_markdown_contains_decision_risks_and_recommendations():
    result = evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(_ready_input(controlled_simulation_kill_switch_policy_complete=False))
    markdown = render_paper_broker_sandbox_dry_run_controlled_simulation_plan_markdown(result)

    assert "# AGIcore Paper Broker Sandbox Dry Run Controlled Simulation Plan" in markdown
    assert "Decision: REQUIRE_KILL_SWITCH_FIXES" in markdown
    assert "CONTROLLED_SIMULATION_KILL_SWITCH_GAP" in markdown
    assert "COMPLETE_CONTROLLED_SIMULATION_KILL_SWITCH_POLICY" in markdown


def test_mapping_inputs_are_supported_and_extra_keys_are_ignored():
    payload = dict(_ready_input().__dict__)
    payload["ignored_future_key"] = "ignored"
    result = evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(payload)

    assert result.state is PaperBrokerSandboxDryRunControlledSimulationPlanState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_REVIEW


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_CONNECTION_POLICY_GAP,
            PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_CONNECTION_POLICY,
        ),
        (
            PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ORDER_POLICY_GAP,
            PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_ORDER_POLICY,
        ),
        (
            PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_POSITION_POLICY_GAP,
            PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_POSITION_POLICY,
        ),
        (
            PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ACCOUNT_POLICY_GAP,
            PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_ACCOUNT_POLICY,
        ),
        (
            PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_GAP,
            PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA,
        ),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_controlled_simulation_plan_recommendations(
        (risk,),
        PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_BOUNDARY_FIXES,
    )


@pytest.mark.parametrize(
    "module_name",
    [
        "paper_broker_sandbox_dry_run_controlled_simulation_plan.py",
        "paper_broker_sandbox_dry_run_controlled_simulation_plan_models.py",
    ],
)
def test_module_keeps_offline_import_boundary(module_name):
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / module_name
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
