import ast
from pathlib import Path

import pytest

from agicore.trading.paper_broker_sandbox_dry_run_pre_execution_check import (
    compute_pre_execution_check_score,
    detect_pre_execution_check_risks,
    evaluate_paper_broker_sandbox_dry_run_pre_execution_check,
    generate_pre_execution_check_recommendations,
    render_paper_broker_sandbox_dry_run_pre_execution_check_markdown,
    verify_account_pre_execution_safety,
    verify_connection_pre_execution_safety,
    verify_dry_run_review_approval,
    verify_human_supervision_pre_execution_safety,
    verify_journal_pre_execution_safety,
    verify_kill_switch_pre_execution_safety,
    verify_observability_pre_execution_safety,
    verify_order_pre_execution_safety,
    verify_position_pre_execution_safety,
    verify_pre_execution_boundaries,
    verify_pre_execution_scope,
    verify_rollback_pre_execution_safety,
    verify_stop_conditions_pre_execution_safety,
    verify_success_failure_criteria_pre_execution_safety,
)
from agicore.trading.paper_broker_sandbox_dry_run_pre_execution_check_models import (
    PaperBrokerSandboxDryRunPreExecutionCheckDecision,
    PaperBrokerSandboxDryRunPreExecutionCheckInput,
    PaperBrokerSandboxDryRunPreExecutionCheckRecommendation,
    PaperBrokerSandboxDryRunPreExecutionCheckRisk,
    PaperBrokerSandboxDryRunPreExecutionCheckState,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "risks": tuple(risks), "offline_only": True}
    if decision:
        payload["decision"] = decision
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
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
        "dry_run_review_approved": True,
        "dry_run_review_reviewed": True,
        "pre_execution_scope_reviewed": True,
        "pre_execution_scope_clear": True,
        "pre_execution_boundaries_reviewed": True,
        "pre_execution_boundaries_complete": True,
        "connection_pre_execution_safety_reviewed": True,
        "connection_pre_execution_safe": True,
        "order_pre_execution_safety_reviewed": True,
        "order_pre_execution_safe": True,
        "position_pre_execution_safety_reviewed": True,
        "position_pre_execution_safe": True,
        "account_pre_execution_safety_reviewed": True,
        "account_pre_execution_safe": True,
        "observability_pre_execution_safety_reviewed": True,
        "observability_pre_execution_safe": True,
        "rollback_pre_execution_safety_reviewed": True,
        "rollback_pre_execution_safe": True,
        "kill_switch_pre_execution_safety_reviewed": True,
        "kill_switch_pre_execution_safe": True,
        "human_supervision_pre_execution_safety_reviewed": True,
        "human_supervision_pre_execution_safe": True,
        "journal_pre_execution_safety_reviewed": True,
        "journal_pre_execution_safe": True,
        "stop_conditions_pre_execution_safety_reviewed": True,
        "stop_conditions_pre_execution_safe": True,
        "success_failure_criteria_pre_execution_safety_reviewed": True,
        "success_failure_criteria_pre_execution_safe": True,
        "paper_broker_sandbox_dry_run_pre_execution_check_requested": True,
        "paper_broker_sandbox_dry_run_execution_requested": False,
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
    return PaperBrokerSandboxDryRunPreExecutionCheckInput(**payload)


def test_evaluate_approves_paper_broker_sandbox_dry_run_pre_execution_check():
    result = evaluate_paper_broker_sandbox_dry_run_pre_execution_check(_ready_input())

    assert result.state is PaperBrokerSandboxDryRunPreExecutionCheckState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW
    assert result.decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK
    assert result.risks == ()
    assert result.offline_only is True
    assert result.check_score == 100


def test_pre_execution_check_ready_state_below_execution_review_threshold():
    result = evaluate_paper_broker_sandbox_dry_run_pre_execution_check(
        _ready_input(
            dry_run_review_approval_score=90,
            pre_execution_scope_score=90,
            pre_execution_boundaries_score=90,
            connection_pre_execution_safety_score=90,
            order_pre_execution_safety_score=90,
            position_pre_execution_safety_score=90,
            account_pre_execution_safety_score=90,
            observability_pre_execution_safety_score=90,
            rollback_pre_execution_safety_score=90,
            kill_switch_pre_execution_safety_score=90,
            human_supervision_pre_execution_safety_score=90,
            journal_pre_execution_safety_score=90,
            stop_conditions_pre_execution_safety_score=90,
            success_failure_criteria_pre_execution_safety_score=90,
        )
    )

    assert result.state is PaperBrokerSandboxDryRunPreExecutionCheckState.PRE_EXECUTION_CHECK_READY
    assert result.decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK


def test_verification_sections_detect_primary_risks():
    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.DRY_RUN_REVIEW_NOT_APPROVED in verify_dry_run_review_approval(_ready_input(dry_run_review_approved=False)).risks
    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.PRE_EXECUTION_SCOPE_UNCLEAR in verify_pre_execution_scope(_ready_input(pre_execution_scope_clear=False)).risks
    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.PRE_EXECUTION_BOUNDARY_GAP in verify_pre_execution_boundaries(_ready_input(pre_execution_boundaries_complete=False)).risks
    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.CONNECTION_PRE_EXECUTION_SAFETY_GAP in verify_connection_pre_execution_safety(_ready_input(connection_pre_execution_safe=False)).risks
    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.ORDER_PRE_EXECUTION_SAFETY_GAP in verify_order_pre_execution_safety(_ready_input(order_pre_execution_safe=False)).risks
    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.POSITION_PRE_EXECUTION_SAFETY_GAP in verify_position_pre_execution_safety(_ready_input(position_pre_execution_safe=False)).risks
    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.ACCOUNT_PRE_EXECUTION_SAFETY_GAP in verify_account_pre_execution_safety(_ready_input(account_pre_execution_safe=False)).risks
    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.OBSERVABILITY_PRE_EXECUTION_GAP in verify_observability_pre_execution_safety(_ready_input(observability_pre_execution_safe=False)).risks
    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.ROLLBACK_PRE_EXECUTION_GAP in verify_rollback_pre_execution_safety(_ready_input(rollback_pre_execution_safe=False)).risks
    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.KILL_SWITCH_PRE_EXECUTION_GAP in verify_kill_switch_pre_execution_safety(_ready_input(kill_switch_pre_execution_safe=False)).risks
    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.HUMAN_SUPERVISION_PRE_EXECUTION_GAP in verify_human_supervision_pre_execution_safety(_ready_input(human_supervision_pre_execution_safe=False)).risks
    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.JOURNAL_PRE_EXECUTION_GAP in verify_journal_pre_execution_safety(_ready_input(journal_pre_execution_safe=False)).risks
    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.STOP_CONDITIONS_PRE_EXECUTION_GAP in verify_stop_conditions_pre_execution_safety(_ready_input(stop_conditions_pre_execution_safe=False)).risks
    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.SUCCESS_FAILURE_CRITERIA_PRE_EXECUTION_GAP in verify_success_failure_criteria_pre_execution_safety(_ready_input(success_failure_criteria_pre_execution_safe=False)).risks


def test_detects_all_pre_execution_check_risks():
    result = evaluate_paper_broker_sandbox_dry_run_pre_execution_check(
        _ready_input(
            dry_run_review_approved=False,
            pre_execution_scope_clear=False,
            pre_execution_boundaries_complete=False,
            connection_pre_execution_safe=False,
            order_pre_execution_safe=False,
            position_pre_execution_safe=False,
            account_pre_execution_safe=False,
            observability_pre_execution_safe=False,
            rollback_pre_execution_safe=False,
            kill_switch_pre_execution_safe=False,
            human_supervision_pre_execution_safe=False,
            journal_pre_execution_safe=False,
            stop_conditions_pre_execution_safe=False,
            success_failure_criteria_pre_execution_safe=False,
            paper_broker_sandbox_dry_run_pre_execution_check_requested=False,
            paper_broker_sandbox_dry_run_execution_requested=True,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(PaperBrokerSandboxDryRunPreExecutionCheckRisk)
    assert result.state is PaperBrokerSandboxDryRunPreExecutionCheckState.NOT_READY
    assert result.decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN
    assert result.offline_only is False


def test_review_gap_requires_dry_run_review_fixes_when_not_blocked():
    result = evaluate_paper_broker_sandbox_dry_run_pre_execution_check(_ready_input(dry_run_review_approved=False))

    assert result.decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_DRY_RUN_REVIEW_FIXES


def test_scope_boundary_connection_and_order_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_dry_run_pre_execution_check(_ready_input(pre_execution_scope_clear=False)).decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_SCOPE_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_pre_execution_check(_ready_input(pre_execution_boundaries_complete=False)).decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_BOUNDARY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_pre_execution_check(_ready_input(connection_pre_execution_safe=False)).decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_CONNECTION_SAFETY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_pre_execution_check(_ready_input(order_pre_execution_safe=False)).decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_ORDER_SAFETY_FIXES


def test_position_account_observability_and_rollback_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_dry_run_pre_execution_check(_ready_input(position_pre_execution_safe=False)).decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_POSITION_SAFETY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_pre_execution_check(_ready_input(account_pre_execution_safe=False)).decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_ACCOUNT_SAFETY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_pre_execution_check(_ready_input(observability_pre_execution_safe=False)).decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_OBSERVABILITY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_pre_execution_check(_ready_input(rollback_pre_execution_safe=False)).decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_ROLLBACK_FIXES


def test_kill_supervision_journal_stop_and_criteria_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_dry_run_pre_execution_check(_ready_input(kill_switch_pre_execution_safe=False)).decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_KILL_SWITCH_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_pre_execution_check(_ready_input(human_supervision_pre_execution_safe=False)).decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_SUPERVISION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_pre_execution_check(_ready_input(journal_pre_execution_safe=False)).decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_JOURNAL_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_pre_execution_check(_ready_input(stop_conditions_pre_execution_safe=False)).decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_STOP_CONDITION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_pre_execution_check(_ready_input(success_failure_criteria_pre_execution_safe=False)).decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_STOP_CONDITION_FIXES


def test_premature_execution_caps_score_and_blocks():
    data = _ready_input(paper_broker_sandbox_dry_run_execution_requested=True)
    risks = detect_pre_execution_check_risks(data)
    score = compute_pre_execution_check_score(data, risks)
    result = evaluate_paper_broker_sandbox_dry_run_pre_execution_check(data)

    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION in risks
    assert score.overall_score <= 40
    assert result.decision is PaperBrokerSandboxDryRunPreExecutionCheckDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN


def test_no_pre_execution_gap_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_dry_run_pre_execution_check(_ready_input(no_pre_execution=False))

    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.PRE_EXECUTION_BOUNDARY_GAP in result.risks
    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION in result.risks
    assert result.offline_only is False


def test_upstream_network_leak_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_dry_run_pre_execution_check(
        _ready_input(
            paper_broker_sandbox_dry_run_review=_upstream(
                "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK",
                risks=("NETWORK_LEAK",),
            )
        )
    )

    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.PRE_EXECUTION_BOUNDARY_GAP in result.risks
    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.CONNECTION_PRE_EXECUTION_SAFETY_GAP in result.risks
    assert PaperBrokerSandboxDryRunPreExecutionCheckRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION in result.risks
    assert result.offline_only is False


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_pre_execution_check_recommendations(
        (
            PaperBrokerSandboxDryRunPreExecutionCheckRisk.KILL_SWITCH_PRE_EXECUTION_GAP,
            PaperBrokerSandboxDryRunPreExecutionCheckRisk.KILL_SWITCH_PRE_EXECUTION_GAP,
            PaperBrokerSandboxDryRunPreExecutionCheckRisk.SUCCESS_FAILURE_CRITERIA_PRE_EXECUTION_GAP,
            PaperBrokerSandboxDryRunPreExecutionCheckRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION,
        ),
        PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_KILL_SWITCH_FIXES,
    )

    assert recommendations.count(PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_KILL_SWITCH_PRE_EXECUTION_SAFETY) == 1
    assert PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_SUCCESS_FAILURE_CRITERIA_PRE_EXECUTION_SAFETY in recommendations
    assert PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION in recommendations
    assert PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.RUN_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_pre_execution_check_recommendations(
        (),
        PaperBrokerSandboxDryRunPreExecutionCheckDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK,
    )

    assert PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW in recommendations


def test_markdown_contains_decision_risks_and_recommendations():
    result = evaluate_paper_broker_sandbox_dry_run_pre_execution_check(_ready_input(kill_switch_pre_execution_safe=False))
    markdown = render_paper_broker_sandbox_dry_run_pre_execution_check_markdown(result)

    assert "# AGIcore Paper Broker Sandbox Dry Run Pre-Execution Check" in markdown
    assert "Decision: REQUIRE_KILL_SWITCH_FIXES" in markdown
    assert "KILL_SWITCH_PRE_EXECUTION_GAP" in markdown
    assert "COMPLETE_KILL_SWITCH_PRE_EXECUTION_SAFETY" in markdown


def test_mapping_inputs_are_supported_and_extra_keys_are_ignored():
    payload = dict(_ready_input().__dict__)
    payload["ignored_future_key"] = "ignored"
    result = evaluate_paper_broker_sandbox_dry_run_pre_execution_check(payload)

    assert result.state is PaperBrokerSandboxDryRunPreExecutionCheckState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            PaperBrokerSandboxDryRunPreExecutionCheckRisk.CONNECTION_PRE_EXECUTION_SAFETY_GAP,
            PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_CONNECTION_PRE_EXECUTION_SAFETY,
        ),
        (
            PaperBrokerSandboxDryRunPreExecutionCheckRisk.ORDER_PRE_EXECUTION_SAFETY_GAP,
            PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_ORDER_PRE_EXECUTION_SAFETY,
        ),
        (
            PaperBrokerSandboxDryRunPreExecutionCheckRisk.POSITION_PRE_EXECUTION_SAFETY_GAP,
            PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_POSITION_PRE_EXECUTION_SAFETY,
        ),
        (
            PaperBrokerSandboxDryRunPreExecutionCheckRisk.ACCOUNT_PRE_EXECUTION_SAFETY_GAP,
            PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_ACCOUNT_PRE_EXECUTION_SAFETY,
        ),
        (
            PaperBrokerSandboxDryRunPreExecutionCheckRisk.SUCCESS_FAILURE_CRITERIA_PRE_EXECUTION_GAP,
            PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_SUCCESS_FAILURE_CRITERIA_PRE_EXECUTION_SAFETY,
        ),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_pre_execution_check_recommendations(
        (risk,),
        PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_BOUNDARY_FIXES,
    )


@pytest.mark.parametrize(
    "module_name",
    [
        "paper_broker_sandbox_dry_run_pre_execution_check.py",
        "paper_broker_sandbox_dry_run_pre_execution_check_models.py",
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
