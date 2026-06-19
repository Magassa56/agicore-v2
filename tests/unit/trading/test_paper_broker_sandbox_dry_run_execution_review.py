import ast
from pathlib import Path

import pytest

from agicore.trading.paper_broker_sandbox_dry_run_execution_review import (
    compute_execution_review_score,
    detect_execution_review_risks,
    evaluate_paper_broker_sandbox_dry_run_execution_review,
    generate_execution_review_recommendations,
    render_paper_broker_sandbox_dry_run_execution_review_markdown,
    review_execution_abort_conditions,
    review_execution_account_control,
    review_execution_boundaries,
    review_execution_connection_control,
    review_execution_human_supervision_control,
    review_execution_journal_control,
    review_execution_kill_switch_control,
    review_execution_observability_control,
    review_execution_order_control,
    review_execution_position_control,
    review_execution_rollback_control,
    review_execution_scenario,
    review_execution_scope,
    review_execution_session_limits,
    review_execution_stop_conditions,
    review_execution_success_failure_criteria,
    review_pre_execution_check_approval,
)
from agicore.trading.paper_broker_sandbox_dry_run_execution_review_models import (
    PaperBrokerSandboxDryRunExecutionReviewDecision,
    PaperBrokerSandboxDryRunExecutionReviewInput,
    PaperBrokerSandboxDryRunExecutionReviewRecommendation,
    PaperBrokerSandboxDryRunExecutionReviewRisk,
    PaperBrokerSandboxDryRunExecutionReviewState,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "risks": tuple(risks), "offline_only": True}
    if decision:
        payload["decision"] = decision
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
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
        "pre_execution_check_approved": True,
        "pre_execution_check_reviewed": True,
        "execution_scope_reviewed": True,
        "execution_scope_clear": True,
        "execution_boundaries_reviewed": True,
        "execution_boundaries_complete": True,
        "execution_scenario_reviewed": True,
        "execution_scenario_complete": True,
        "execution_session_limits_reviewed": True,
        "execution_session_limits_complete": True,
        "execution_connection_control_reviewed": True,
        "execution_connection_control_complete": True,
        "execution_order_control_reviewed": True,
        "execution_order_control_complete": True,
        "execution_position_control_reviewed": True,
        "execution_position_control_complete": True,
        "execution_account_control_reviewed": True,
        "execution_account_control_complete": True,
        "execution_observability_control_reviewed": True,
        "execution_observability_control_complete": True,
        "execution_rollback_control_reviewed": True,
        "execution_rollback_control_complete": True,
        "execution_kill_switch_control_reviewed": True,
        "execution_kill_switch_control_complete": True,
        "execution_human_supervision_control_reviewed": True,
        "execution_human_supervision_control_complete": True,
        "execution_journal_control_reviewed": True,
        "execution_journal_control_complete": True,
        "execution_stop_conditions_reviewed": True,
        "execution_stop_conditions_complete": True,
        "execution_success_failure_criteria_reviewed": True,
        "execution_success_failure_criteria_complete": True,
        "execution_abort_conditions_reviewed": True,
        "execution_abort_conditions_complete": True,
        "paper_broker_sandbox_dry_run_execution_review_requested": True,
        "paper_broker_sandbox_dry_run_execution_requested": False,
        "paper_broker_sandbox_dry_run_real_execution_requested": False,
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
        "no_real_execution": True,
        "no_real_order": True,
        "no_real_account_access": True,
    }
    payload.update(overrides)
    return PaperBrokerSandboxDryRunExecutionReviewInput(**payload)


def test_evaluate_approves_paper_broker_sandbox_dry_run_execution_review():
    result = evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input())

    assert result.state is PaperBrokerSandboxDryRunExecutionReviewState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE
    assert result.decision is PaperBrokerSandboxDryRunExecutionReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW
    assert result.risks == ()
    assert result.offline_only is True
    assert result.review_score == 100


def test_execution_review_ready_state_below_authorization_gate_threshold():
    result = evaluate_paper_broker_sandbox_dry_run_execution_review(
        _ready_input(
            pre_execution_check_approval_score=90,
            execution_scope_score=90,
            execution_boundaries_score=90,
            execution_scenario_score=90,
            execution_session_limits_score=90,
            execution_connection_control_score=90,
            execution_order_control_score=90,
            execution_position_control_score=90,
            execution_account_control_score=90,
            execution_observability_control_score=90,
            execution_rollback_control_score=90,
            execution_kill_switch_control_score=90,
            execution_human_supervision_control_score=90,
            execution_journal_control_score=90,
            execution_stop_conditions_score=90,
            execution_success_failure_criteria_score=90,
            execution_abort_conditions_score=90,
        )
    )

    assert result.state is PaperBrokerSandboxDryRunExecutionReviewState.DRY_RUN_EXECUTION_REVIEW_READY
    assert result.decision is PaperBrokerSandboxDryRunExecutionReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW


def test_review_sections_detect_primary_risks():
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.PRE_EXECUTION_CHECK_NOT_APPROVED in review_pre_execution_check_approval(_ready_input(pre_execution_check_approved=False)).risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SCOPE_UNCLEAR in review_execution_scope(_ready_input(execution_scope_clear=False)).risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_BOUNDARY_GAP in review_execution_boundaries(_ready_input(execution_boundaries_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SCENARIO_GAP in review_execution_scenario(_ready_input(execution_scenario_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SESSION_LIMIT_GAP in review_execution_session_limits(_ready_input(execution_session_limits_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_CONNECTION_CONTROL_GAP in review_execution_connection_control(_ready_input(execution_connection_control_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ORDER_CONTROL_GAP in review_execution_order_control(_ready_input(execution_order_control_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_POSITION_CONTROL_GAP in review_execution_position_control(_ready_input(execution_position_control_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ACCOUNT_CONTROL_GAP in review_execution_account_control(_ready_input(execution_account_control_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_OBSERVABILITY_GAP in review_execution_observability_control(_ready_input(execution_observability_control_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ROLLBACK_GAP in review_execution_rollback_control(_ready_input(execution_rollback_control_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_KILL_SWITCH_GAP in review_execution_kill_switch_control(_ready_input(execution_kill_switch_control_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_HUMAN_SUPERVISION_GAP in review_execution_human_supervision_control(_ready_input(execution_human_supervision_control_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_JOURNAL_GAP in review_execution_journal_control(_ready_input(execution_journal_control_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_STOP_CONDITION_GAP in review_execution_stop_conditions(_ready_input(execution_stop_conditions_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SUCCESS_FAILURE_CRITERIA_GAP in review_execution_success_failure_criteria(_ready_input(execution_success_failure_criteria_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ABORT_CONDITION_GAP in review_execution_abort_conditions(_ready_input(execution_abort_conditions_complete=False)).risks


def test_detects_all_execution_review_risks():
    result = evaluate_paper_broker_sandbox_dry_run_execution_review(
        _ready_input(
            pre_execution_check_approved=False,
            execution_scope_clear=False,
            execution_boundaries_complete=False,
            execution_scenario_complete=False,
            execution_session_limits_complete=False,
            execution_connection_control_complete=False,
            execution_order_control_complete=False,
            execution_position_control_complete=False,
            execution_account_control_complete=False,
            execution_observability_control_complete=False,
            execution_rollback_control_complete=False,
            execution_kill_switch_control_complete=False,
            execution_human_supervision_control_complete=False,
            execution_journal_control_complete=False,
            execution_stop_conditions_complete=False,
            execution_success_failure_criteria_complete=False,
            execution_abort_conditions_complete=False,
            paper_broker_sandbox_dry_run_execution_review_requested=False,
            paper_broker_sandbox_dry_run_real_execution_requested=True,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(PaperBrokerSandboxDryRunExecutionReviewRisk)
    assert result.state is PaperBrokerSandboxDryRunExecutionReviewState.NOT_READY
    assert result.decision is PaperBrokerSandboxDryRunExecutionReviewDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION
    assert result.offline_only is False


def test_pre_execution_gap_requires_pre_execution_check_fixes_when_not_blocked():
    result = evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(pre_execution_check_approved=False))

    assert result.decision is PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_PRE_EXECUTION_CHECK_FIXES


def test_scope_boundary_scenario_and_limit_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(execution_scope_clear=False)).decision is PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_SCOPE_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(execution_boundaries_complete=False)).decision is PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_BOUNDARY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(execution_scenario_complete=False)).decision is PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_SCENARIO_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(execution_session_limits_complete=False)).decision is PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_SESSION_LIMIT_FIXES


def test_connection_order_position_and_account_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(execution_connection_control_complete=False)).decision is PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_CONNECTION_CONTROL_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(execution_order_control_complete=False)).decision is PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_ORDER_CONTROL_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(execution_position_control_complete=False)).decision is PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_POSITION_CONTROL_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(execution_account_control_complete=False)).decision is PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_ACCOUNT_CONTROL_FIXES


def test_observability_rollback_kill_supervision_journal_stop_and_abort_decisions():
    assert evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(execution_observability_control_complete=False)).decision is PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_OBSERVABILITY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(execution_rollback_control_complete=False)).decision is PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_ROLLBACK_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(execution_kill_switch_control_complete=False)).decision is PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_KILL_SWITCH_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(execution_human_supervision_control_complete=False)).decision is PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_SUPERVISION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(execution_journal_control_complete=False)).decision is PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_JOURNAL_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(execution_stop_conditions_complete=False)).decision is PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_STOP_CONDITION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(execution_success_failure_criteria_complete=False)).decision is PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_STOP_CONDITION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(execution_abort_conditions_complete=False)).decision is PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_ABORT_CONDITION_FIXES


def test_premature_real_execution_caps_score_and_blocks():
    data = _ready_input(paper_broker_sandbox_dry_run_real_execution_requested=True)
    risks = detect_execution_review_risks(data)
    score = compute_execution_review_score(data, risks)
    result = evaluate_paper_broker_sandbox_dry_run_execution_review(data)

    assert PaperBrokerSandboxDryRunExecutionReviewRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_REAL_EXECUTION in risks
    assert score.overall_score <= 40
    assert result.decision is PaperBrokerSandboxDryRunExecutionReviewDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION


def test_no_real_execution_gap_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(no_real_execution=False))

    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_BOUNDARY_GAP in result.risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_REAL_EXECUTION in result.risks
    assert result.offline_only is False


def test_upstream_network_leak_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_dry_run_execution_review(
        _ready_input(
            paper_broker_sandbox_dry_run_pre_execution_check=_upstream(
                "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW",
                risks=("NETWORK_LEAK",),
            )
        )
    )

    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_BOUNDARY_GAP in result.risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_CONNECTION_CONTROL_GAP in result.risks
    assert PaperBrokerSandboxDryRunExecutionReviewRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_REAL_EXECUTION in result.risks
    assert result.offline_only is False


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_execution_review_recommendations(
        (
            PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_KILL_SWITCH_GAP,
            PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_KILL_SWITCH_GAP,
            PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ABORT_CONDITION_GAP,
            PaperBrokerSandboxDryRunExecutionReviewRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_REAL_EXECUTION,
        ),
        PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_KILL_SWITCH_FIXES,
    )

    assert recommendations.count(PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_KILL_SWITCH_CONTROL) == 1
    assert PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_ABORT_CONDITIONS in recommendations
    assert PaperBrokerSandboxDryRunExecutionReviewRecommendation.DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_REAL_EXECUTION in recommendations
    assert PaperBrokerSandboxDryRunExecutionReviewRecommendation.RUN_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_execution_review_recommendations(
        (),
        PaperBrokerSandboxDryRunExecutionReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW,
    )

    assert PaperBrokerSandboxDryRunExecutionReviewRecommendation.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE in recommendations


def test_markdown_contains_decision_risks_and_recommendations():
    result = evaluate_paper_broker_sandbox_dry_run_execution_review(_ready_input(execution_kill_switch_control_complete=False))
    markdown = render_paper_broker_sandbox_dry_run_execution_review_markdown(result)

    assert "# AGIcore Paper Broker Sandbox Dry Run Execution Review" in markdown
    assert "Decision: REQUIRE_KILL_SWITCH_FIXES" in markdown
    assert "EXECUTION_KILL_SWITCH_GAP" in markdown
    assert "COMPLETE_EXECUTION_KILL_SWITCH_CONTROL" in markdown


def test_mapping_inputs_are_supported_and_extra_keys_are_ignored():
    payload = dict(_ready_input().__dict__)
    payload["ignored_future_key"] = "ignored"
    result = evaluate_paper_broker_sandbox_dry_run_execution_review(payload)

    assert result.state is PaperBrokerSandboxDryRunExecutionReviewState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_CONNECTION_CONTROL_GAP, PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_CONNECTION_CONTROL),
        (PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ORDER_CONTROL_GAP, PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_ORDER_CONTROL),
        (PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_POSITION_CONTROL_GAP, PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_POSITION_CONTROL),
        (PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ACCOUNT_CONTROL_GAP, PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_ACCOUNT_CONTROL),
        (PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SUCCESS_FAILURE_CRITERIA_GAP, PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_SUCCESS_FAILURE_CRITERIA),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_execution_review_recommendations((risk,), PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_BOUNDARY_FIXES)


@pytest.mark.parametrize(
    "module_name",
    [
        "paper_broker_sandbox_dry_run_execution_review.py",
        "paper_broker_sandbox_dry_run_execution_review_models.py",
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
