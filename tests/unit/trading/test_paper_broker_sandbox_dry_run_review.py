import ast
from pathlib import Path

import pytest

from agicore.trading.paper_broker_sandbox_dry_run_review import (
    compute_dry_run_review_score,
    detect_dry_run_review_risks,
    evaluate_paper_broker_sandbox_dry_run_review,
    generate_dry_run_review_recommendations,
    render_paper_broker_sandbox_dry_run_review_markdown,
    review_dry_run_account_policy,
    review_dry_run_boundaries,
    review_dry_run_connection_policy,
    review_dry_run_failure_criteria,
    review_dry_run_human_supervision_policy,
    review_dry_run_journal_policy,
    review_dry_run_kill_switch_policy,
    review_dry_run_observability_policy,
    review_dry_run_order_policy,
    review_dry_run_plan_readiness,
    review_dry_run_position_policy,
    review_dry_run_rollback_policy,
    review_dry_run_scenario,
    review_dry_run_scope,
    review_dry_run_session_limits,
    review_dry_run_stop_conditions,
    review_dry_run_success_criteria,
)
from agicore.trading.paper_broker_sandbox_dry_run_review_models import (
    PaperBrokerSandboxDryRunReviewDecision,
    PaperBrokerSandboxDryRunReviewInput,
    PaperBrokerSandboxDryRunReviewRecommendation,
    PaperBrokerSandboxDryRunReviewRisk,
    PaperBrokerSandboxDryRunReviewState,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "risks": tuple(risks), "offline_only": True}
    if decision:
        payload["decision"] = decision
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
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
        "dry_run_plan_approved": True,
        "dry_run_plan_reviewed": True,
        "dry_run_scope_reviewed": True,
        "dry_run_scope_clear": True,
        "dry_run_boundaries_reviewed": True,
        "dry_run_boundaries_complete": True,
        "dry_run_scenario_reviewed": True,
        "dry_run_scenario_complete": True,
        "dry_run_session_limits_reviewed": True,
        "dry_run_session_limits_complete": True,
        "dry_run_connection_policy_reviewed": True,
        "dry_run_connection_policy_complete": True,
        "dry_run_order_policy_reviewed": True,
        "dry_run_order_policy_complete": True,
        "dry_run_position_policy_reviewed": True,
        "dry_run_position_policy_complete": True,
        "dry_run_account_policy_reviewed": True,
        "dry_run_account_policy_complete": True,
        "dry_run_observability_policy_reviewed": True,
        "dry_run_observability_policy_complete": True,
        "dry_run_rollback_policy_reviewed": True,
        "dry_run_rollback_policy_complete": True,
        "dry_run_kill_switch_policy_reviewed": True,
        "dry_run_kill_switch_policy_complete": True,
        "dry_run_human_supervision_policy_reviewed": True,
        "dry_run_human_supervision_policy_complete": True,
        "dry_run_journal_policy_reviewed": True,
        "dry_run_journal_policy_complete": True,
        "dry_run_stop_conditions_reviewed": True,
        "dry_run_stop_conditions_complete": True,
        "dry_run_success_criteria_reviewed": True,
        "dry_run_success_criteria_complete": True,
        "dry_run_failure_criteria_reviewed": True,
        "dry_run_failure_criteria_complete": True,
        "paper_broker_sandbox_dry_run_review_requested": True,
        "paper_broker_sandbox_dry_run_pre_execution_requested": False,
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
        "no_real_order": True,
        "no_real_account_access": True,
        "no_dry_run_execution": True,
        "no_pre_execution": True,
    }
    payload.update(overrides)
    return PaperBrokerSandboxDryRunReviewInput(**payload)


def test_evaluate_approves_paper_broker_sandbox_dry_run_review():
    result = evaluate_paper_broker_sandbox_dry_run_review(_ready_input())

    assert result.state is PaperBrokerSandboxDryRunReviewState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK
    assert result.decision is PaperBrokerSandboxDryRunReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW
    assert result.risks == ()
    assert result.offline_only is True
    assert result.review_score == 100


def test_dry_run_review_ready_state_below_pre_execution_threshold():
    result = evaluate_paper_broker_sandbox_dry_run_review(
        _ready_input(
            dry_run_plan_readiness_score=90,
            dry_run_scope_score=90,
            dry_run_boundaries_score=90,
            dry_run_scenario_score=90,
            dry_run_session_limits_score=90,
            dry_run_connection_policy_score=90,
            dry_run_order_policy_score=90,
            dry_run_position_policy_score=90,
            dry_run_account_policy_score=90,
            dry_run_observability_policy_score=90,
            dry_run_rollback_policy_score=90,
            dry_run_kill_switch_policy_score=90,
            dry_run_human_supervision_policy_score=90,
            dry_run_journal_policy_score=90,
            dry_run_stop_conditions_score=90,
            dry_run_success_criteria_score=90,
            dry_run_failure_criteria_score=90,
        )
    )

    assert result.state is PaperBrokerSandboxDryRunReviewState.DRY_RUN_REVIEW_READY
    assert result.decision is PaperBrokerSandboxDryRunReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW


def test_review_sections_detect_primary_risks():
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_PLAN_NOT_APPROVED in review_dry_run_plan_readiness(_ready_input(dry_run_plan_approved=False)).risks
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SCOPE_UNCLEAR in review_dry_run_scope(_ready_input(dry_run_scope_clear=False)).risks
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_BOUNDARY_INCOMPLETE in review_dry_run_boundaries(_ready_input(dry_run_boundaries_complete=False)).risks
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SCENARIO_INCOMPLETE in review_dry_run_scenario(_ready_input(dry_run_scenario_complete=False)).risks
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SESSION_LIMIT_INCOMPLETE in review_dry_run_session_limits(_ready_input(dry_run_session_limits_complete=False)).risks
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_CONNECTION_POLICY_INCOMPLETE in review_dry_run_connection_policy(_ready_input(dry_run_connection_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_ORDER_POLICY_INCOMPLETE in review_dry_run_order_policy(_ready_input(dry_run_order_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_POSITION_POLICY_INCOMPLETE in review_dry_run_position_policy(_ready_input(dry_run_position_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_ACCOUNT_POLICY_INCOMPLETE in review_dry_run_account_policy(_ready_input(dry_run_account_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_OBSERVABILITY_INCOMPLETE in review_dry_run_observability_policy(_ready_input(dry_run_observability_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_ROLLBACK_INCOMPLETE in review_dry_run_rollback_policy(_ready_input(dry_run_rollback_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_KILL_SWITCH_INCOMPLETE in review_dry_run_kill_switch_policy(_ready_input(dry_run_kill_switch_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_HUMAN_SUPERVISION_INCOMPLETE in review_dry_run_human_supervision_policy(_ready_input(dry_run_human_supervision_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_JOURNAL_INCOMPLETE in review_dry_run_journal_policy(_ready_input(dry_run_journal_policy_complete=False)).risks
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_STOP_CONDITION_INCOMPLETE in review_dry_run_stop_conditions(_ready_input(dry_run_stop_conditions_complete=False)).risks
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SUCCESS_CRITERIA_INCOMPLETE in review_dry_run_success_criteria(_ready_input(dry_run_success_criteria_complete=False)).risks
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_FAILURE_CRITERIA_INCOMPLETE in review_dry_run_failure_criteria(_ready_input(dry_run_failure_criteria_complete=False)).risks


def test_detects_all_dry_run_review_risks():
    result = evaluate_paper_broker_sandbox_dry_run_review(
        _ready_input(
            dry_run_plan_approved=False,
            dry_run_scope_clear=False,
            dry_run_boundaries_complete=False,
            dry_run_scenario_complete=False,
            dry_run_session_limits_complete=False,
            dry_run_connection_policy_complete=False,
            dry_run_order_policy_complete=False,
            dry_run_position_policy_complete=False,
            dry_run_account_policy_complete=False,
            dry_run_observability_policy_complete=False,
            dry_run_rollback_policy_complete=False,
            dry_run_kill_switch_policy_complete=False,
            dry_run_human_supervision_policy_complete=False,
            dry_run_journal_policy_complete=False,
            dry_run_stop_conditions_complete=False,
            dry_run_success_criteria_complete=False,
            dry_run_failure_criteria_complete=False,
            paper_broker_sandbox_dry_run_review_requested=False,
            paper_broker_sandbox_dry_run_pre_execution_requested=True,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(PaperBrokerSandboxDryRunReviewRisk)
    assert result.state is PaperBrokerSandboxDryRunReviewState.NOT_READY
    assert result.decision is PaperBrokerSandboxDryRunReviewDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN
    assert result.offline_only is False


def test_plan_gap_requires_plan_fixes_when_not_blocked():
    result = evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_plan_approved=False))

    assert result.decision is PaperBrokerSandboxDryRunReviewDecision.REQUIRE_DRY_RUN_PLAN_FIXES


def test_scope_boundary_scenario_and_limit_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_scope_clear=False)).decision is PaperBrokerSandboxDryRunReviewDecision.REQUIRE_SCOPE_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_boundaries_complete=False)).decision is PaperBrokerSandboxDryRunReviewDecision.REQUIRE_BOUNDARY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_scenario_complete=False)).decision is PaperBrokerSandboxDryRunReviewDecision.REQUIRE_SCENARIO_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_session_limits_complete=False)).decision is PaperBrokerSandboxDryRunReviewDecision.REQUIRE_SESSION_LIMIT_FIXES


def test_connection_order_position_and_account_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_connection_policy_complete=False)).decision is PaperBrokerSandboxDryRunReviewDecision.REQUIRE_CONNECTION_POLICY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_order_policy_complete=False)).decision is PaperBrokerSandboxDryRunReviewDecision.REQUIRE_ORDER_POLICY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_position_policy_complete=False)).decision is PaperBrokerSandboxDryRunReviewDecision.REQUIRE_POSITION_POLICY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_account_policy_complete=False)).decision is PaperBrokerSandboxDryRunReviewDecision.REQUIRE_ACCOUNT_POLICY_FIXES


def test_observability_rollback_kill_supervision_journal_and_stop_decisions():
    assert evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_observability_policy_complete=False)).decision is PaperBrokerSandboxDryRunReviewDecision.REQUIRE_OBSERVABILITY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_rollback_policy_complete=False)).decision is PaperBrokerSandboxDryRunReviewDecision.REQUIRE_ROLLBACK_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_kill_switch_policy_complete=False)).decision is PaperBrokerSandboxDryRunReviewDecision.REQUIRE_KILL_SWITCH_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_human_supervision_policy_complete=False)).decision is PaperBrokerSandboxDryRunReviewDecision.REQUIRE_SUPERVISION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_journal_policy_complete=False)).decision is PaperBrokerSandboxDryRunReviewDecision.REQUIRE_JOURNAL_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_stop_conditions_complete=False)).decision is PaperBrokerSandboxDryRunReviewDecision.REQUIRE_STOP_CONDITION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_success_criteria_complete=False)).decision is PaperBrokerSandboxDryRunReviewDecision.REQUIRE_STOP_CONDITION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_failure_criteria_complete=False)).decision is PaperBrokerSandboxDryRunReviewDecision.REQUIRE_STOP_CONDITION_FIXES


def test_premature_pre_execution_caps_score_and_blocks():
    data = _ready_input(paper_broker_sandbox_dry_run_pre_execution_requested=True)
    risks = detect_dry_run_review_risks(data)
    score = compute_dry_run_review_score(data, risks)
    result = evaluate_paper_broker_sandbox_dry_run_review(data)

    assert PaperBrokerSandboxDryRunReviewRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION in risks
    assert score.overall_score <= 40
    assert result.decision is PaperBrokerSandboxDryRunReviewDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN


def test_no_pre_execution_gap_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_dry_run_review(_ready_input(no_pre_execution=False))

    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_BOUNDARY_INCOMPLETE in result.risks
    assert PaperBrokerSandboxDryRunReviewRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION in result.risks
    assert result.offline_only is False


def test_upstream_network_leak_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_dry_run_review(
        _ready_input(paper_broker_sandbox_dry_run_plan=_upstream("READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW", risks=("NETWORK_LEAK",)))
    )

    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_BOUNDARY_INCOMPLETE in result.risks
    assert PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_CONNECTION_POLICY_INCOMPLETE in result.risks
    assert PaperBrokerSandboxDryRunReviewRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION in result.risks
    assert result.offline_only is False


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_dry_run_review_recommendations(
        (
            PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_KILL_SWITCH_INCOMPLETE,
            PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_KILL_SWITCH_INCOMPLETE,
            PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SUCCESS_CRITERIA_INCOMPLETE,
            PaperBrokerSandboxDryRunReviewRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION,
        ),
        PaperBrokerSandboxDryRunReviewDecision.REQUIRE_KILL_SWITCH_FIXES,
    )

    assert recommendations.count(PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_KILL_SWITCH_POLICY) == 1
    assert PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_SUCCESS_CRITERIA in recommendations
    assert PaperBrokerSandboxDryRunReviewRecommendation.DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION in recommendations
    assert PaperBrokerSandboxDryRunReviewRecommendation.RUN_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_dry_run_review_recommendations(
        (),
        PaperBrokerSandboxDryRunReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW,
    )

    assert PaperBrokerSandboxDryRunReviewRecommendation.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK in recommendations


def test_markdown_contains_decision_risks_and_recommendations():
    result = evaluate_paper_broker_sandbox_dry_run_review(_ready_input(dry_run_kill_switch_policy_complete=False))
    markdown = render_paper_broker_sandbox_dry_run_review_markdown(result)

    assert "# AGIcore Paper Broker Sandbox Dry Run Review" in markdown
    assert "Decision: REQUIRE_KILL_SWITCH_FIXES" in markdown
    assert "DRY_RUN_KILL_SWITCH_INCOMPLETE" in markdown
    assert "COMPLETE_DRY_RUN_KILL_SWITCH_POLICY" in markdown


def test_mapping_inputs_are_supported_and_extra_keys_are_ignored():
    payload = dict(_ready_input().__dict__)
    payload["ignored_future_key"] = "ignored"
    result = evaluate_paper_broker_sandbox_dry_run_review(payload)

    assert result.state is PaperBrokerSandboxDryRunReviewState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_CONNECTION_POLICY_INCOMPLETE, PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_CONNECTION_POLICY),
        (PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_ORDER_POLICY_INCOMPLETE, PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_ORDER_POLICY),
        (PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_POSITION_POLICY_INCOMPLETE, PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_POSITION_POLICY),
        (PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_ACCOUNT_POLICY_INCOMPLETE, PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_ACCOUNT_POLICY),
        (PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_FAILURE_CRITERIA_INCOMPLETE, PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_FAILURE_CRITERIA),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_dry_run_review_recommendations((risk,), PaperBrokerSandboxDryRunReviewDecision.REQUIRE_BOUNDARY_FIXES)


@pytest.mark.parametrize(
    "module_name",
    [
        "paper_broker_sandbox_dry_run_review.py",
        "paper_broker_sandbox_dry_run_review_models.py",
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

