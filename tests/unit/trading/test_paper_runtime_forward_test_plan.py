import ast
from pathlib import Path

import pytest

from agicore.trading.paper_runtime_forward_test_plan import (
    compute_forward_test_plan_score,
    define_allowed_session_limits,
    define_failure_criteria,
    define_forward_test_duration,
    define_forward_test_scope,
    define_human_supervision_rules,
    define_journal_requirements,
    define_kill_switch_rules,
    define_observability_requirements,
    define_rollback_rules,
    define_simulated_loss_limits,
    define_stop_conditions,
    define_success_criteria,
    detect_forward_test_plan_risks,
    evaluate_paper_runtime_forward_test_plan,
    generate_forward_test_plan_recommendations,
    render_paper_runtime_forward_test_plan_markdown,
)
from agicore.trading.paper_runtime_forward_test_plan_models import (
    PaperRuntimeForwardTestPlanDecision,
    PaperRuntimeForwardTestPlanInput,
    PaperRuntimeForwardTestPlanRecommendation,
    PaperRuntimeForwardTestPlanRisk,
    PaperRuntimeForwardTestPlanState,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "risks": tuple(risks), "offline_only": True}
    if decision:
        payload["decision"] = decision
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
        "supervised_paper_runtime_trial": _upstream("READY_FOR_PAPER_RUNTIME_FORWARD_TEST_PLAN", "APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL"),
        "official_paper_validation_report": _upstream("READY_FOR_SUPERVISED_PAPER_RUNTIME_TRIAL"),
        "paper_runtime_validation": _upstream("READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT"),
        "paper_runtime_release_candidate": _upstream("READY_FOR_PAPER_RUNTIME_VALIDATION"),
        "paper_runtime_stabilization_review": _upstream("READY_FOR_PAPER_RUNTIME_RELEASE_CANDIDATE"),
        "extended_paper_runtime_test": _upstream("READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW"),
        "paper_runtime_test_run": _upstream("READY_FOR_EXTENDED_PAPER_RUNTIME_TEST"),
        "paper_trading_runtime": _upstream("COMPLETED"),
        "paper_runtime_integration_review": _upstream("READY_FOR_PAPER_RUNTIME_TEST_RUN"),
        "paper_trading_runtime_design": _upstream("READY_FOR_RUNTIME_IMPLEMENTATION"),
        "paper_runtime_decision_review": _upstream("READY_FOR_PAPER_TRADING_RUNTIME"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "forward_test_scope_defined": True,
        "duration_defined": True,
        "session_limits_defined": True,
        "simulated_loss_limits_defined": True,
        "human_supervision_rules_defined": True,
        "journal_requirements_defined": True,
        "observability_requirements_defined": True,
        "rollback_rules_defined": True,
        "kill_switch_rules_defined": True,
        "success_criteria_defined": True,
        "failure_criteria_defined": True,
        "stop_conditions_defined": True,
        "broker_sandbox_session_requested": True,
        "max_sessions": 3,
        "duration_days": 5,
        "max_simulated_loss_pct": 2.5,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "no_real_broker": True,
        "no_api_key_read": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_api": True,
        "no_real_order": True,
    }
    payload.update(overrides)
    return PaperRuntimeForwardTestPlanInput(**payload)


def test_evaluate_approves_forward_test_plan():
    result = evaluate_paper_runtime_forward_test_plan(_ready_input())

    assert result.state is PaperRuntimeForwardTestPlanState.READY_FOR_PAPER_BROKER_SANDBOX_SESSION
    assert result.decision is PaperRuntimeForwardTestPlanDecision.APPROVE_PAPER_RUNTIME_FORWARD_TEST_PLAN
    assert result.risks == ()
    assert result.offline_only is True
    assert result.forward_test_plan_score == 100


def test_plan_ready_below_broker_sandbox_threshold():
    result = evaluate_paper_runtime_forward_test_plan(
        _ready_input(
            forward_test_scope_score=90,
            forward_test_duration_score=90,
            allowed_session_limits_score=90,
            simulated_loss_limits_score=90,
            human_supervision_rules_score=90,
            journal_requirements_score=90,
            observability_requirements_score=90,
            rollback_rules_score=90,
            kill_switch_rules_score=90,
            success_criteria_score=90,
            failure_criteria_score=90,
            stop_conditions_score=90,
        )
    )

    assert result.state is PaperRuntimeForwardTestPlanState.PLAN_READY
    assert result.decision is PaperRuntimeForwardTestPlanDecision.APPROVE_PAPER_RUNTIME_FORWARD_TEST_PLAN


def test_section_builders_detect_primary_risks():
    assert PaperRuntimeForwardTestPlanRisk.FORWARD_TEST_SCOPE_UNCLEAR in define_forward_test_scope(_ready_input(forward_test_scope_defined=False)).risks
    assert PaperRuntimeForwardTestPlanRisk.DURATION_UNDEFINED in define_forward_test_duration(_ready_input(duration_defined=False)).risks
    assert PaperRuntimeForwardTestPlanRisk.SESSION_LIMITS_MISSING in define_allowed_session_limits(_ready_input(session_limits_defined=False)).risks
    assert PaperRuntimeForwardTestPlanRisk.SIMULATED_LOSS_LIMITS_MISSING in define_simulated_loss_limits(_ready_input(simulated_loss_limits_defined=False)).risks
    assert PaperRuntimeForwardTestPlanRisk.HUMAN_SUPERVISION_RULES_MISSING in define_human_supervision_rules(_ready_input(human_supervision_rules_defined=False)).risks
    assert PaperRuntimeForwardTestPlanRisk.JOURNAL_REQUIREMENTS_MISSING in define_journal_requirements(_ready_input(journal_requirements_defined=False)).risks
    assert PaperRuntimeForwardTestPlanRisk.OBSERVABILITY_REQUIREMENTS_MISSING in define_observability_requirements(_ready_input(observability_requirements_defined=False)).risks
    assert PaperRuntimeForwardTestPlanRisk.ROLLBACK_RULES_MISSING in define_rollback_rules(_ready_input(rollback_rules_defined=False)).risks
    assert PaperRuntimeForwardTestPlanRisk.KILL_SWITCH_RULES_MISSING in define_kill_switch_rules(_ready_input(kill_switch_rules_defined=False)).risks
    assert PaperRuntimeForwardTestPlanRisk.SUCCESS_CRITERIA_UNCLEAR in define_success_criteria(_ready_input(success_criteria_defined=False)).risks
    assert PaperRuntimeForwardTestPlanRisk.FAILURE_CRITERIA_UNCLEAR in define_failure_criteria(_ready_input(failure_criteria_defined=False)).risks
    assert PaperRuntimeForwardTestPlanRisk.STOP_CONDITIONS_MISSING in define_stop_conditions(_ready_input(stop_conditions_defined=False)).risks


def test_detects_all_forward_test_plan_risks():
    result = evaluate_paper_runtime_forward_test_plan(
        _ready_input(
            forward_test_scope_defined=False,
            duration_defined=False,
            session_limits_defined=False,
            simulated_loss_limits_defined=False,
            human_supervision_rules_defined=False,
            journal_requirements_defined=False,
            observability_requirements_defined=False,
            rollback_rules_defined=False,
            kill_switch_rules_defined=False,
            success_criteria_defined=False,
            failure_criteria_defined=False,
            stop_conditions_defined=False,
            broker_sandbox_session_requested=False,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(PaperRuntimeForwardTestPlanRisk)
    assert result.state is PaperRuntimeForwardTestPlanState.PLAN_NOT_READY
    assert result.decision is PaperRuntimeForwardTestPlanDecision.BLOCK_FORWARD_TEST
    assert result.offline_only is False


def test_scope_and_duration_gaps_require_scope_fixes():
    assert evaluate_paper_runtime_forward_test_plan(_ready_input(forward_test_scope_defined=False)).decision is PaperRuntimeForwardTestPlanDecision.REQUIRE_SCOPE_FIXES
    assert evaluate_paper_runtime_forward_test_plan(_ready_input(duration_defined=False)).decision is PaperRuntimeForwardTestPlanDecision.REQUIRE_SCOPE_FIXES


def test_supervision_gap_requires_supervision_fixes():
    result = evaluate_paper_runtime_forward_test_plan(_ready_input(human_supervision_rules_defined=False))

    assert result.decision is PaperRuntimeForwardTestPlanDecision.REQUIRE_SUPERVISION_FIXES


def test_limit_gaps_require_limit_fixes():
    assert evaluate_paper_runtime_forward_test_plan(_ready_input(session_limits_defined=False)).decision is PaperRuntimeForwardTestPlanDecision.REQUIRE_LIMIT_FIXES
    assert evaluate_paper_runtime_forward_test_plan(_ready_input(simulated_loss_limits_defined=False)).decision is PaperRuntimeForwardTestPlanDecision.REQUIRE_LIMIT_FIXES


def test_observability_gap_requires_observability_fixes():
    result = evaluate_paper_runtime_forward_test_plan(_ready_input(observability_requirements_defined=False))

    assert result.decision is PaperRuntimeForwardTestPlanDecision.REQUIRE_OBSERVABILITY_FIXES


def test_rollback_and_kill_switch_decisions():
    assert evaluate_paper_runtime_forward_test_plan(_ready_input(rollback_rules_defined=False)).decision is PaperRuntimeForwardTestPlanDecision.REQUIRE_ROLLBACK_FIXES
    assert evaluate_paper_runtime_forward_test_plan(_ready_input(kill_switch_rules_defined=False)).decision is PaperRuntimeForwardTestPlanDecision.REQUIRE_KILL_SWITCH_FIXES


def test_premature_broker_sandbox_session_caps_score_and_blocks():
    data = _ready_input(broker_sandbox_session_requested=False)
    risks = detect_forward_test_plan_risks(data)
    score = compute_forward_test_plan_score(data, risks)
    result = evaluate_paper_runtime_forward_test_plan(data)

    assert PaperRuntimeForwardTestPlanRisk.PREMATURE_BROKER_SANDBOX_SESSION in risks
    assert score.overall_score <= 40
    assert result.decision is PaperRuntimeForwardTestPlanDecision.BLOCK_FORWARD_TEST


def test_upstream_network_leak_blocks_offline_boundary():
    result = evaluate_paper_runtime_forward_test_plan(
        _ready_input(supervised_paper_runtime_trial=_upstream("READY_FOR_PAPER_RUNTIME_FORWARD_TEST_PLAN", risks=("NETWORK_LEAK",)))
    )

    assert PaperRuntimeForwardTestPlanRisk.PREMATURE_BROKER_SANDBOX_SESSION in result.risks
    assert result.offline_only is False


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_forward_test_plan_recommendations(
        (
            PaperRuntimeForwardTestPlanRisk.KILL_SWITCH_RULES_MISSING,
            PaperRuntimeForwardTestPlanRisk.KILL_SWITCH_RULES_MISSING,
            PaperRuntimeForwardTestPlanRisk.OBSERVABILITY_REQUIREMENTS_MISSING,
            PaperRuntimeForwardTestPlanRisk.PREMATURE_BROKER_SANDBOX_SESSION,
        ),
        PaperRuntimeForwardTestPlanDecision.REQUIRE_KILL_SWITCH_FIXES,
    )

    assert recommendations.count(PaperRuntimeForwardTestPlanRecommendation.DEFINE_KILL_SWITCH_RULES) == 1
    assert PaperRuntimeForwardTestPlanRecommendation.DEFINE_OBSERVABILITY_REQUIREMENTS in recommendations
    assert PaperRuntimeForwardTestPlanRecommendation.DELAY_BROKER_SANDBOX_SESSION in recommendations
    assert PaperRuntimeForwardTestPlanRecommendation.RUN_FORWARD_TEST_PLAN_REVIEW_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_forward_test_plan_recommendations(
        (),
        PaperRuntimeForwardTestPlanDecision.APPROVE_PAPER_RUNTIME_FORWARD_TEST_PLAN,
    )

    assert PaperRuntimeForwardTestPlanRecommendation.APPROVE_PAPER_BROKER_SANDBOX_SESSION_PREP in recommendations


def test_markdown_contains_decision_risks_and_recommendations():
    result = evaluate_paper_runtime_forward_test_plan(_ready_input(kill_switch_rules_defined=False))
    markdown = render_paper_runtime_forward_test_plan_markdown(result)

    assert "# AGIcore Paper Runtime Forward Test Plan" in markdown
    assert "Decision: REQUIRE_KILL_SWITCH_FIXES" in markdown
    assert "KILL_SWITCH_RULES_MISSING" in markdown
    assert "DEFINE_KILL_SWITCH_RULES" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_paper_runtime_forward_test_plan(_ready_input().__dict__)

    assert result.state is PaperRuntimeForwardTestPlanState.READY_FOR_PAPER_BROKER_SANDBOX_SESSION


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (PaperRuntimeForwardTestPlanRisk.SUCCESS_CRITERIA_UNCLEAR, PaperRuntimeForwardTestPlanRecommendation.DEFINE_SUCCESS_CRITERIA),
        (PaperRuntimeForwardTestPlanRisk.FAILURE_CRITERIA_UNCLEAR, PaperRuntimeForwardTestPlanRecommendation.DEFINE_FAILURE_CRITERIA),
        (PaperRuntimeForwardTestPlanRisk.STOP_CONDITIONS_MISSING, PaperRuntimeForwardTestPlanRecommendation.DEFINE_STOP_CONDITIONS),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_forward_test_plan_recommendations((risk,), PaperRuntimeForwardTestPlanDecision.REQUIRE_SCOPE_FIXES)


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "paper_runtime_forward_test_plan.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
