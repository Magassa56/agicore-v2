import ast
from pathlib import Path

import pytest

from agicore.trading.paper_broker_sandbox_controlled_simulation_review_precheck import (
    compute_controlled_simulation_review_precheck_score,
    detect_controlled_simulation_review_precheck_risks,
    evaluate_paper_broker_sandbox_controlled_simulation_review_precheck,
    generate_controlled_simulation_review_precheck_recommendations,
    render_controlled_simulation_review_precheck_markdown,
    review_controlled_simulation_abort_conditions,
    review_controlled_simulation_account_policy,
    review_controlled_simulation_boundaries,
    review_controlled_simulation_connection_policy,
    review_controlled_simulation_human_supervision_policy,
    review_controlled_simulation_journal_policy,
    review_controlled_simulation_kill_switch_policy,
    review_controlled_simulation_observability_policy,
    review_controlled_simulation_order_policy,
    review_controlled_simulation_plan_readiness,
    review_controlled_simulation_position_policy,
    review_controlled_simulation_rollback_policy,
    review_controlled_simulation_scenario,
    review_controlled_simulation_scope,
    review_controlled_simulation_session_limits,
    review_controlled_simulation_stop_conditions,
    review_controlled_simulation_success_failure_criteria,
    verify_controlled_simulation_human_approval_required,
    verify_controlled_simulation_no_real_execution,
    verify_controlled_simulation_offline_boundaries,
    verify_controlled_simulation_pre_execution_safety,
)
from agicore.trading.paper_broker_sandbox_controlled_simulation_review_precheck_models import (
    PaperBrokerSandboxControlledSimulationReviewPrecheckDecision,
    PaperBrokerSandboxControlledSimulationReviewPrecheckInput,
    PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation,
    PaperBrokerSandboxControlledSimulationReviewPrecheckRisk,
    PaperBrokerSandboxControlledSimulationReviewPrecheckState,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "risks": tuple(risks), "offline_only": True}
    if decision:
        payload["decision"] = decision
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_sandbox_dry_run_controlled_simulation_plan": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_REVIEW",
            "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN",
        ),
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
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "controlled_simulation_plan_approved": True,
        "controlled_simulation_plan_reviewed": True,
        "controlled_simulation_scope_reviewed": True,
        "controlled_simulation_scope_clear": True,
        "controlled_simulation_boundaries_reviewed": True,
        "controlled_simulation_boundaries_complete": True,
        "controlled_simulation_scenario_reviewed": True,
        "controlled_simulation_scenario_complete": True,
        "controlled_simulation_session_limits_reviewed": True,
        "controlled_simulation_session_limits_complete": True,
        "controlled_simulation_connection_policy_reviewed": True,
        "controlled_simulation_connection_policy_complete": True,
        "controlled_simulation_order_policy_reviewed": True,
        "controlled_simulation_order_policy_complete": True,
        "controlled_simulation_position_policy_reviewed": True,
        "controlled_simulation_position_policy_complete": True,
        "controlled_simulation_account_policy_reviewed": True,
        "controlled_simulation_account_policy_complete": True,
        "controlled_simulation_observability_policy_reviewed": True,
        "controlled_simulation_observability_policy_complete": True,
        "controlled_simulation_rollback_policy_reviewed": True,
        "controlled_simulation_rollback_policy_complete": True,
        "controlled_simulation_kill_switch_policy_reviewed": True,
        "controlled_simulation_kill_switch_policy_complete": True,
        "controlled_simulation_human_supervision_policy_reviewed": True,
        "controlled_simulation_human_supervision_policy_complete": True,
        "controlled_simulation_journal_policy_reviewed": True,
        "controlled_simulation_journal_policy_complete": True,
        "controlled_simulation_stop_conditions_reviewed": True,
        "controlled_simulation_stop_conditions_complete": True,
        "controlled_simulation_abort_conditions_reviewed": True,
        "controlled_simulation_abort_conditions_complete": True,
        "controlled_simulation_success_failure_criteria_reviewed": True,
        "controlled_simulation_success_failure_criteria_complete": True,
        "controlled_simulation_pre_execution_safety_reviewed": True,
        "controlled_simulation_pre_execution_safe": True,
        "controlled_simulation_human_approval_required": True,
        "controlled_simulation_human_approval_confirmed": True,
        "controlled_simulation_review_precheck_requested": True,
        "controlled_simulation_offline_runner_requested": False,
        "controlled_simulation_real_execution_requested": False,
        "controlled_simulation_execution_requested": False,
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
    return PaperBrokerSandboxControlledSimulationReviewPrecheckInput(**payload)


def test_evaluate_approves_controlled_simulation_review_precheck():
    result = evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input())

    assert result.state is PaperBrokerSandboxControlledSimulationReviewPrecheckState.READY_FOR_CONTROLLED_SIMULATION_OFFLINE_RUNNER
    assert result.decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.APPROVE_CONTROLLED_SIMULATION_REVIEW_PRECHECK
    assert result.risks == ()
    assert result.offline_only is True
    assert result.review_precheck_score == 100


def test_review_precheck_ready_state_below_runner_threshold():
    result = evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(
        _ready_input(
            controlled_simulation_plan_readiness_score=90,
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
            controlled_simulation_success_failure_criteria_score=90,
            controlled_simulation_pre_execution_safety_score=90,
            controlled_simulation_no_real_execution_score=90,
            controlled_simulation_offline_boundaries_score=90,
            controlled_simulation_human_approval_score=90,
        )
    )

    assert result.state is PaperBrokerSandboxControlledSimulationReviewPrecheckState.CONTROLLED_SIMULATION_REVIEW_PRECHECK_READY
    assert result.decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.APPROVE_CONTROLLED_SIMULATION_REVIEW_PRECHECK


def test_review_precheck_sections_detect_primary_risks():
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_PLAN_NOT_APPROVED in review_controlled_simulation_plan_readiness(_ready_input(controlled_simulation_plan_approved=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SCOPE_UNCLEAR in review_controlled_simulation_scope(_ready_input(controlled_simulation_scope_clear=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_BOUNDARY_INCOMPLETE in review_controlled_simulation_boundaries(_ready_input(controlled_simulation_boundaries_complete=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SCENARIO_INCOMPLETE in review_controlled_simulation_scenario(_ready_input(controlled_simulation_scenario_complete=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SESSION_LIMIT_INCOMPLETE in review_controlled_simulation_session_limits(_ready_input(controlled_simulation_session_limits_complete=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_CONNECTION_POLICY_INCOMPLETE in review_controlled_simulation_connection_policy(_ready_input(controlled_simulation_connection_policy_complete=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ORDER_POLICY_INCOMPLETE in review_controlled_simulation_order_policy(_ready_input(controlled_simulation_order_policy_complete=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_POSITION_POLICY_INCOMPLETE in review_controlled_simulation_position_policy(_ready_input(controlled_simulation_position_policy_complete=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ACCOUNT_POLICY_INCOMPLETE in review_controlled_simulation_account_policy(_ready_input(controlled_simulation_account_policy_complete=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_OBSERVABILITY_INCOMPLETE in review_controlled_simulation_observability_policy(_ready_input(controlled_simulation_observability_policy_complete=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ROLLBACK_INCOMPLETE in review_controlled_simulation_rollback_policy(_ready_input(controlled_simulation_rollback_policy_complete=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_KILL_SWITCH_INCOMPLETE in review_controlled_simulation_kill_switch_policy(_ready_input(controlled_simulation_kill_switch_policy_complete=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_HUMAN_SUPERVISION_INCOMPLETE in review_controlled_simulation_human_supervision_policy(_ready_input(controlled_simulation_human_supervision_policy_complete=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_JOURNAL_INCOMPLETE in review_controlled_simulation_journal_policy(_ready_input(controlled_simulation_journal_policy_complete=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_STOP_CONDITION_INCOMPLETE in review_controlled_simulation_stop_conditions(_ready_input(controlled_simulation_stop_conditions_complete=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ABORT_CONDITION_INCOMPLETE in review_controlled_simulation_abort_conditions(_ready_input(controlled_simulation_abort_conditions_complete=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_INCOMPLETE in review_controlled_simulation_success_failure_criteria(_ready_input(controlled_simulation_success_failure_criteria_complete=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in verify_controlled_simulation_pre_execution_safety(_ready_input(controlled_simulation_pre_execution_safe=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in verify_controlled_simulation_no_real_execution(_ready_input(no_controlled_simulation_execution=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in verify_controlled_simulation_offline_boundaries(_ready_input(no_http_transport=False)).risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_HUMAN_SUPERVISION_INCOMPLETE in verify_controlled_simulation_human_approval_required(_ready_input(controlled_simulation_human_approval_confirmed=False)).risks


def test_detects_all_review_precheck_risks():
    result = evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(
        _ready_input(
            controlled_simulation_plan_approved=False,
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
            controlled_simulation_success_failure_criteria_complete=False,
            controlled_simulation_pre_execution_safe=False,
            controlled_simulation_human_approval_confirmed=False,
            controlled_simulation_review_precheck_requested=False,
            controlled_simulation_offline_runner_requested=True,
            no_controlled_simulation_execution=False,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(PaperBrokerSandboxControlledSimulationReviewPrecheckRisk)
    assert result.state is PaperBrokerSandboxControlledSimulationReviewPrecheckState.NOT_READY
    assert result.decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.BLOCK_CONTROLLED_SIMULATION
    assert result.offline_only is False


def test_plan_gap_requires_controlled_simulation_plan_fixes_when_not_blocked():
    result = evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(
        _ready_input(controlled_simulation_plan_approved=False)
    )

    assert result.decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_CONTROLLED_SIMULATION_PLAN_FIXES


def test_scope_boundary_scenario_and_limit_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input(controlled_simulation_scope_clear=False)).decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_SCOPE_FIXES
    assert evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input(controlled_simulation_boundaries_complete=False)).decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_BOUNDARY_FIXES
    assert evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input(controlled_simulation_scenario_complete=False)).decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_SCENARIO_FIXES
    assert evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input(controlled_simulation_session_limits_complete=False)).decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_SESSION_LIMIT_FIXES


def test_connection_order_position_and_account_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input(controlled_simulation_connection_policy_complete=False)).decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_CONNECTION_POLICY_FIXES
    assert evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input(controlled_simulation_order_policy_complete=False)).decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_ORDER_POLICY_FIXES
    assert evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input(controlled_simulation_position_policy_complete=False)).decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_POSITION_POLICY_FIXES
    assert evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input(controlled_simulation_account_policy_complete=False)).decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_ACCOUNT_POLICY_FIXES


def test_observability_rollback_kill_supervision_journal_stop_abort_and_criteria_decisions():
    assert evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input(controlled_simulation_observability_policy_complete=False)).decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_OBSERVABILITY_FIXES
    assert evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input(controlled_simulation_rollback_policy_complete=False)).decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_ROLLBACK_FIXES
    assert evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input(controlled_simulation_kill_switch_policy_complete=False)).decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_KILL_SWITCH_FIXES
    assert evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input(controlled_simulation_human_supervision_policy_complete=False)).decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_SUPERVISION_FIXES
    assert evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input(controlled_simulation_journal_policy_complete=False)).decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_JOURNAL_FIXES
    assert evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input(controlled_simulation_stop_conditions_complete=False)).decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_STOP_CONDITION_FIXES
    assert evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input(controlled_simulation_abort_conditions_complete=False)).decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_ABORT_CONDITION_FIXES
    assert evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input(controlled_simulation_success_failure_criteria_complete=False)).decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_SUCCESS_FAILURE_CRITERIA_FIXES


def test_pre_execution_gap_requires_boundary_fixes_when_not_premature():
    result = evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(
        _ready_input(controlled_simulation_pre_execution_safe=False)
    )

    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_BOUNDARY_FIXES


def test_premature_offline_runner_caps_score_and_blocks():
    data = _ready_input(controlled_simulation_offline_runner_requested=True)
    risks = detect_controlled_simulation_review_precheck_risks(data)
    score = compute_controlled_simulation_review_precheck_score(data, risks)
    result = evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(data)

    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.PREMATURE_CONTROLLED_SIMULATION_OFFLINE_RUNNER in risks
    assert score.overall_score <= 40
    assert result.decision is PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.BLOCK_CONTROLLED_SIMULATION


def test_no_real_execution_gap_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(
        _ready_input(no_controlled_simulation_execution=False)
    )

    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.PREMATURE_CONTROLLED_SIMULATION_OFFLINE_RUNNER in result.risks
    assert result.offline_only is False


def test_network_transport_gap_blocks_connection_and_offline_boundary():
    result = evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(_ready_input(no_http_transport=False))

    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_CONNECTION_POLICY_INCOMPLETE in result.risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_BOUNDARY_INCOMPLETE in result.risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.PREMATURE_CONTROLLED_SIMULATION_OFFLINE_RUNNER in result.risks
    assert result.offline_only is False


def test_upstream_network_leak_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(
        _ready_input(
            paper_broker_sandbox_dry_run_controlled_simulation_plan=_upstream(
                "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_REVIEW",
                "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN",
                risks=("NETWORK_LEAK",),
            )
        )
    )

    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_BOUNDARY_INCOMPLETE in result.risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_CONNECTION_POLICY_INCOMPLETE in result.risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.PREMATURE_CONTROLLED_SIMULATION_OFFLINE_RUNNER in result.risks
    assert result.offline_only is False


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_controlled_simulation_review_precheck_recommendations(
        (
            PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_KILL_SWITCH_INCOMPLETE,
            PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_KILL_SWITCH_INCOMPLETE,
            PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,
            PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.PREMATURE_CONTROLLED_SIMULATION_OFFLINE_RUNNER,
        ),
        PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_KILL_SWITCH_FIXES,
    )

    assert recommendations.count(PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_KILL_SWITCH_POLICY) == 1
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.RESTORE_REAL_EXECUTION_BOUNDARIES in recommendations
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.DELAY_CONTROLLED_SIMULATION_OFFLINE_RUNNER in recommendations
    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.RUN_CONTROLLED_SIMULATION_REVIEW_PRECHECK_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_controlled_simulation_review_precheck_recommendations(
        (),
        PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.APPROVE_CONTROLLED_SIMULATION_REVIEW_PRECHECK,
    )

    assert PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.APPROVE_CONTROLLED_SIMULATION_OFFLINE_RUNNER in recommendations


def test_markdown_contains_decision_risks_and_recommendations():
    result = evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(
        _ready_input(controlled_simulation_kill_switch_policy_complete=False)
    )
    markdown = render_controlled_simulation_review_precheck_markdown(result)

    assert "# AGIcore Controlled Simulation Review + Precheck" in markdown
    assert "Decision: REQUIRE_KILL_SWITCH_FIXES" in markdown
    assert "CONTROLLED_SIMULATION_KILL_SWITCH_INCOMPLETE" in markdown
    assert "COMPLETE_CONTROLLED_SIMULATION_KILL_SWITCH_POLICY" in markdown


def test_mapping_inputs_are_supported_and_extra_keys_are_ignored():
    payload = dict(_ready_input().__dict__)
    payload["ignored_future_key"] = "ignored"
    result = evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(payload)

    assert result.state is PaperBrokerSandboxControlledSimulationReviewPrecheckState.READY_FOR_CONTROLLED_SIMULATION_OFFLINE_RUNNER


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_CONNECTION_POLICY_INCOMPLETE,
            PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_CONNECTION_POLICY,
        ),
        (
            PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ORDER_POLICY_INCOMPLETE,
            PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_ORDER_POLICY,
        ),
        (
            PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_POSITION_POLICY_INCOMPLETE,
            PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_POSITION_POLICY,
        ),
        (
            PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ACCOUNT_POLICY_INCOMPLETE,
            PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_ACCOUNT_POLICY,
        ),
        (
            PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_INCOMPLETE,
            PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA,
        ),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_controlled_simulation_review_precheck_recommendations(
        (risk,),
        PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_BOUNDARY_FIXES,
    )


@pytest.mark.parametrize(
    "module_name",
    [
        "paper_broker_sandbox_controlled_simulation_review_precheck.py",
        "paper_broker_sandbox_controlled_simulation_review_precheck_models.py",
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
