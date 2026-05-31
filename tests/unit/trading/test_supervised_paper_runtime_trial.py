import ast
from pathlib import Path

import pytest

from agicore.trading.supervised_paper_runtime_trial import (
    compute_supervised_trial_score,
    detect_supervised_trial_risks,
    evaluate_supervised_paper_runtime_trial,
    generate_supervised_trial_recommendations,
    render_supervised_paper_runtime_trial_markdown,
    run_supervised_runtime_trial,
    verify_human_supervision_active,
    verify_runtime_trial_cycles,
    verify_runtime_trial_human_intervention,
    verify_runtime_trial_journal,
    verify_runtime_trial_kill_switch,
    verify_runtime_trial_observability,
    verify_runtime_trial_paper_order_simulation,
    verify_runtime_trial_position_pnl,
    verify_runtime_trial_rollback,
    verify_runtime_trial_safety_gate,
    verify_runtime_trial_session_init,
    verify_runtime_trial_start,
    verify_runtime_trial_stop,
    verify_trial_authorization,
)
from agicore.trading.supervised_paper_runtime_trial_models import (
    SupervisedPaperRuntimeTrialDecision,
    SupervisedPaperRuntimeTrialInput,
    SupervisedPaperRuntimeTrialRecommendation,
    SupervisedPaperRuntimeTrialRisk,
    SupervisedPaperRuntimeTrialState,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "risks": tuple(risks), "offline_only": True, "report_score": 100}
    if decision:
        payload["decision"] = decision
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
        "official_paper_validation_report": _upstream("READY_FOR_SUPERVISED_PAPER_RUNTIME_TRIAL", "APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL"),
        "paper_runtime_validation": _upstream("READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT"),
        "paper_runtime_release_candidate": _upstream("READY_FOR_PAPER_RUNTIME_VALIDATION"),
        "paper_runtime_stabilization_review": _upstream("READY_FOR_PAPER_RUNTIME_RELEASE_CANDIDATE"),
        "extended_paper_runtime_test": _upstream("READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW"),
        "paper_runtime_test_run": _upstream("READY_FOR_EXTENDED_PAPER_RUNTIME_TEST"),
        "paper_trading_runtime": _upstream("COMPLETED"),
        "paper_runtime_integration_review": _upstream("READY_FOR_PAPER_RUNTIME_TEST_RUN"),
        "paper_trading_runtime_design": _upstream("READY_FOR_RUNTIME_IMPLEMENTATION"),
        "paper_runtime_decision_review": _upstream("READY_FOR_PAPER_TRADING_RUNTIME"),
        "full_paper_session": _upstream("READY_FOR_PAPER_TRADING_RUNTIME"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "trial_authorized": True,
        "human_supervision_active": True,
        "runtime_trial_started": True,
        "session_initialized": True,
        "runtime_cycles_completed": True,
        "safety_gate_passed": True,
        "paper_order_simulated": True,
        "position_pnl_updated": True,
        "journal_written": True,
        "observability_emitted": True,
        "rollback_verified": True,
        "kill_switch_verified": True,
        "human_intervention_verified": True,
        "runtime_trial_stopped": True,
        "forward_test_plan_requested": True,
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
    return SupervisedPaperRuntimeTrialInput(**payload)


def test_evaluate_approves_supervised_trial():
    result = evaluate_supervised_paper_runtime_trial(_ready_input())

    assert result.state is SupervisedPaperRuntimeTrialState.READY_FOR_PAPER_RUNTIME_FORWARD_TEST_PLAN
    assert result.decision is SupervisedPaperRuntimeTrialDecision.APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL
    assert result.risks == ()
    assert result.offline_only is True
    assert result.supervised_trial_score == 100


def test_run_supervised_runtime_trial_delegates_to_evaluator():
    result = run_supervised_runtime_trial(_ready_input())

    assert result.decision is SupervisedPaperRuntimeTrialDecision.APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL


def test_supervised_trial_completed_below_forward_plan_threshold():
    result = evaluate_supervised_paper_runtime_trial(
        _ready_input(
            trial_authorization_score=90,
            human_supervision_score=90,
            runtime_trial_start_score=90,
            session_init_score=90,
            runtime_cycles_score=90,
            safety_gate_score=90,
            paper_order_simulation_score=90,
            position_pnl_score=90,
            journal_score=90,
            observability_score=90,
            rollback_score=90,
            kill_switch_score=90,
            human_intervention_score=90,
            trial_stop_score=90,
        )
    )

    assert result.state is SupervisedPaperRuntimeTrialState.SUPERVISED_TRIAL_COMPLETED


def test_verifiers_detect_each_primary_risk():
    assert SupervisedPaperRuntimeTrialRisk.TRIAL_AUTHORIZATION_MISSING in verify_trial_authorization(_ready_input(trial_authorized=False)).risks
    assert SupervisedPaperRuntimeTrialRisk.HUMAN_SUPERVISION_INACTIVE in verify_human_supervision_active(_ready_input(human_supervision_active=False)).risks
    assert SupervisedPaperRuntimeTrialRisk.RUNTIME_TRIAL_START_FAILURE in verify_runtime_trial_start(_ready_input(runtime_trial_started=False)).risks
    assert SupervisedPaperRuntimeTrialRisk.SESSION_INIT_FAILURE in verify_runtime_trial_session_init(_ready_input(session_initialized=False)).risks
    assert SupervisedPaperRuntimeTrialRisk.RUNTIME_CYCLE_FAILURE in verify_runtime_trial_cycles(_ready_input(runtime_cycles_completed=False)).risks
    assert SupervisedPaperRuntimeTrialRisk.SAFETY_GATE_FAILURE in verify_runtime_trial_safety_gate(_ready_input(safety_gate_passed=False)).risks
    assert SupervisedPaperRuntimeTrialRisk.PAPER_ORDER_SIMULATION_FAILURE in verify_runtime_trial_paper_order_simulation(_ready_input(paper_order_simulated=False)).risks
    assert SupervisedPaperRuntimeTrialRisk.POSITION_PNL_FAILURE in verify_runtime_trial_position_pnl(_ready_input(position_pnl_updated=False)).risks
    assert SupervisedPaperRuntimeTrialRisk.JOURNAL_FAILURE in verify_runtime_trial_journal(_ready_input(journal_written=False)).risks
    assert SupervisedPaperRuntimeTrialRisk.OBSERVABILITY_FAILURE in verify_runtime_trial_observability(_ready_input(observability_emitted=False)).risks
    assert SupervisedPaperRuntimeTrialRisk.ROLLBACK_FAILURE in verify_runtime_trial_rollback(_ready_input(rollback_verified=False)).risks
    assert SupervisedPaperRuntimeTrialRisk.KILL_SWITCH_FAILURE in verify_runtime_trial_kill_switch(_ready_input(kill_switch_verified=False)).risks
    assert SupervisedPaperRuntimeTrialRisk.HUMAN_INTERVENTION_FAILURE in verify_runtime_trial_human_intervention(_ready_input(human_intervention_verified=False)).risks
    assert SupervisedPaperRuntimeTrialRisk.TRIAL_STOP_FAILURE in verify_runtime_trial_stop(_ready_input(runtime_trial_stopped=False)).risks


def test_detects_all_supervised_trial_risks():
    result = evaluate_supervised_paper_runtime_trial(
        _ready_input(
            trial_authorized=False,
            human_supervision_active=False,
            runtime_trial_started=False,
            session_initialized=False,
            runtime_cycles_completed=False,
            safety_gate_passed=False,
            paper_order_simulated=False,
            position_pnl_updated=False,
            journal_written=False,
            observability_emitted=False,
            rollback_verified=False,
            kill_switch_verified=False,
            human_intervention_verified=False,
            runtime_trial_stopped=False,
            forward_test_plan_requested=False,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(SupervisedPaperRuntimeTrialRisk)
    assert result.state is SupervisedPaperRuntimeTrialState.NOT_READY
    assert result.decision is SupervisedPaperRuntimeTrialDecision.BLOCK_SUPERVISED_TRIAL
    assert result.offline_only is False


def test_authorization_missing_requires_authorization_fixes():
    result = evaluate_supervised_paper_runtime_trial(_ready_input(trial_authorized=False))

    assert result.decision is SupervisedPaperRuntimeTrialDecision.REQUIRE_AUTHORIZATION_FIXES


def test_supervision_inactive_requires_supervision_fixes():
    result = evaluate_supervised_paper_runtime_trial(_ready_input(human_supervision_active=False))

    assert result.decision is SupervisedPaperRuntimeTrialDecision.REQUIRE_SUPERVISION_FIXES


def test_safety_gap_requires_safety_fixes():
    result = evaluate_supervised_paper_runtime_trial(_ready_input(safety_gate_passed=False))

    assert result.decision is SupervisedPaperRuntimeTrialDecision.REQUIRE_SAFETY_FIXES


def test_observability_gap_requires_observability_fixes():
    result = evaluate_supervised_paper_runtime_trial(_ready_input(observability_emitted=False))

    assert result.decision is SupervisedPaperRuntimeTrialDecision.REQUIRE_OBSERVABILITY_FIXES


def test_rollback_and_kill_switch_decisions():
    assert evaluate_supervised_paper_runtime_trial(_ready_input(rollback_verified=False)).decision is SupervisedPaperRuntimeTrialDecision.REQUIRE_ROLLBACK_FIXES
    assert evaluate_supervised_paper_runtime_trial(_ready_input(kill_switch_verified=False)).decision is SupervisedPaperRuntimeTrialDecision.REQUIRE_KILL_SWITCH_FIXES


def test_premature_forward_test_plan_caps_score_and_blocks():
    data = _ready_input(forward_test_plan_requested=False)
    risks = detect_supervised_trial_risks(data)
    score = compute_supervised_trial_score(data, risks)
    result = evaluate_supervised_paper_runtime_trial(data)

    assert SupervisedPaperRuntimeTrialRisk.PREMATURE_FORWARD_TEST_PLAN in risks
    assert score.overall_score <= 40
    assert result.decision is SupervisedPaperRuntimeTrialDecision.BLOCK_SUPERVISED_TRIAL


def test_upstream_network_leak_blocks_offline_boundary():
    result = evaluate_supervised_paper_runtime_trial(
        _ready_input(official_paper_validation_report=_upstream("READY_FOR_SUPERVISED_PAPER_RUNTIME_TRIAL", risks=("NETWORK_LEAK",)))
    )

    assert SupervisedPaperRuntimeTrialRisk.PREMATURE_FORWARD_TEST_PLAN in result.risks
    assert result.offline_only is False


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_supervised_trial_recommendations(
        (
            SupervisedPaperRuntimeTrialRisk.KILL_SWITCH_FAILURE,
            SupervisedPaperRuntimeTrialRisk.KILL_SWITCH_FAILURE,
            SupervisedPaperRuntimeTrialRisk.OBSERVABILITY_FAILURE,
            SupervisedPaperRuntimeTrialRisk.PREMATURE_FORWARD_TEST_PLAN,
        ),
        SupervisedPaperRuntimeTrialDecision.REQUIRE_KILL_SWITCH_FIXES,
    )

    assert recommendations.count(SupervisedPaperRuntimeTrialRecommendation.REPAIR_KILL_SWITCH) == 1
    assert SupervisedPaperRuntimeTrialRecommendation.REPAIR_OBSERVABILITY in recommendations
    assert SupervisedPaperRuntimeTrialRecommendation.DELAY_FORWARD_TEST_PLAN in recommendations
    assert SupervisedPaperRuntimeTrialRecommendation.RUN_SUPERVISED_RUNTIME_TRIAL_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    assert SupervisedPaperRuntimeTrialRecommendation.APPROVE_FORWARD_TEST_PLAN_PREPARATION in generate_supervised_trial_recommendations(
        (),
        SupervisedPaperRuntimeTrialDecision.APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL,
    )


def test_markdown_contains_decision_risks_and_recommendations():
    result = evaluate_supervised_paper_runtime_trial(_ready_input(kill_switch_verified=False))
    markdown = render_supervised_paper_runtime_trial_markdown(result)

    assert "# AGIcore Supervised Paper Runtime Trial" in markdown
    assert "Decision: REQUIRE_KILL_SWITCH_FIXES" in markdown
    assert "KILL_SWITCH_FAILURE" in markdown
    assert "REPAIR_KILL_SWITCH" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_supervised_paper_runtime_trial(_ready_input().__dict__)

    assert result.state is SupervisedPaperRuntimeTrialState.READY_FOR_PAPER_RUNTIME_FORWARD_TEST_PLAN


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (SupervisedPaperRuntimeTrialRisk.RUNTIME_CYCLE_FAILURE, SupervisedPaperRuntimeTrialRecommendation.REPAIR_RUNTIME_CYCLES),
        (SupervisedPaperRuntimeTrialRisk.JOURNAL_FAILURE, SupervisedPaperRuntimeTrialRecommendation.REPAIR_JOURNAL),
        (SupervisedPaperRuntimeTrialRisk.HUMAN_INTERVENTION_FAILURE, SupervisedPaperRuntimeTrialRecommendation.REPAIR_HUMAN_INTERVENTION),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_supervised_trial_recommendations((risk,), SupervisedPaperRuntimeTrialDecision.REQUIRE_RUNTIME_TRIAL_FIXES)


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "supervised_paper_runtime_trial.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
