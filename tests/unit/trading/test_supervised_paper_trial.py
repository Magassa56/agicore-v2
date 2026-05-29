import ast
from pathlib import Path

import pytest

from agicore.trading.supervised_paper_trial import (
    compute_trial_score,
    detect_trial_risks,
    evaluate_supervised_paper_trial,
    generate_trial_recommendations,
    render_supervised_paper_trial_markdown,
    verify_supervised_execution_flow,
    verify_trial_journal,
    verify_trial_observability,
    verify_trial_rollback_path,
    verify_trial_safety_gate,
    verify_trial_scenario,
)
from agicore.trading.supervised_paper_trial_models import (
    SupervisedPaperTrialInput,
    SupervisedPaperTrialRecommendation,
    SupervisedPaperTrialRisk,
    SupervisedPaperTrialState,
)


def _upstream(state="READY", score=96, risks=(), blockers=(), **extra):
    payload = {
        "state": state,
        "score": score,
        "risks": tuple(risks),
        "blockers": tuple(blockers),
        "offline_only": True,
        "score_breakdown": {
            "dry_run_score": score,
            "end_to_end_score": score,
            "alpaca_adapter_score": score,
            "adapter_score": score,
            "supervised_session_score": score,
            "human_validation_score": score,
            "paper_loop_score": score,
            "observability_score": score,
            "rollback_score": score,
            "kill_switch_score": score,
            "safety_gate_score": score,
            "journal_flow_score": score,
            "journal_pipeline_score": score,
            "observability_flow_score": score,
        },
    }
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_dry_run": _upstream("READY_FOR_SUPERVISED_PAPER_TRIAL"),
        "paper_trading_end_to_end": _upstream("READY_FOR_PAPER_DRY_RUN"),
        "alpaca_paper_adapter": _upstream("READY_FOR_END_TO_END_PAPER"),
        "paper_broker_adapter": _upstream("READY_FOR_ALPACA_PAPER_ADAPTER"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "controlled_paper_run": _upstream("READY_FOR_HUMAN_VALIDATED_SESSION"),
        "paper_execution_loop_readiness": _upstream("READY_FOR_CONTROLLED_PAPER_RUN"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "trial_scenario_defined": True,
        "scenario_inputs_fixed": True,
        "scenario_expected_outputs_defined": True,
        "scenario_repeatable": True,
        "human_supervisor_assigned": True,
        "operator_confirmation_available": True,
        "supervision_session_active": True,
        "human_override_available": True,
        "dry_run_completed": True,
        "dry_run_output_reconciled": True,
        "safety_gate_available": True,
        "safety_gate_passed": True,
        "kill_switch_linked": True,
        "safety_bypass_blocked": True,
        "journal_entry_written": True,
        "journal_captures_scenario": True,
        "journal_captures_decisions": True,
        "final_report_available": True,
        "observability_events_emitted": True,
        "metrics_recorded": True,
        "traces_recorded": True,
        "alerts_visible": True,
        "rollback_path_available": True,
        "recovery_point_verified": True,
        "post_rollback_state_safe": True,
        "rollback_audit_recorded": True,
        "paper_state_reconciled": True,
        "trial_repeatable": True,
        "offline_mode_enforced": True,
        "trial_executed": True,
        "ready_for_broker_paper_sandbox": True,
        "trial_scenario_score": 96,
        "supervised_execution_score": 96,
        "trial_safety_gate_score": 96,
        "trial_journal_score": 96,
        "trial_observability_score": 96,
        "trial_rollback_score": 96,
    }
    payload.update(overrides)
    return SupervisedPaperTrialInput(**payload)


def test_evaluate_ready_for_broker_paper_sandbox():
    result = evaluate_supervised_paper_trial(_ready_input())

    assert result.state is SupervisedPaperTrialState.READY_FOR_BROKER_PAPER_SANDBOX
    assert result.risks == ()
    assert result.offline_only is True
    assert result.trial_score >= 94
    assert result.trial_trace.blocked_steps == ()
    assert result.trial_trace.completed_steps[-1] == "final_report"


def test_trial_completed_when_sandbox_gate_is_not_set():
    result = evaluate_supervised_paper_trial(_ready_input(ready_for_broker_paper_sandbox=False))

    assert result.state is SupervisedPaperTrialState.TRIAL_COMPLETED
    assert result.risks == ()


def test_trial_ready_when_not_executed_yet():
    result = evaluate_supervised_paper_trial(_ready_input(trial_executed=False))

    assert result.state is SupervisedPaperTrialState.TRIAL_READY
    assert result.risks == ()


def test_detects_every_trial_risk_when_all_sections_fail():
    failing_fields = {
        name: False
        for name in SupervisedPaperTrialInput.__dataclass_fields__
        if name.endswith(
            (
                "_defined",
                "_fixed",
                "_repeatable",
                "_assigned",
                "_available",
                "_active",
                "_completed",
                "_reconciled",
                "_passed",
                "_linked",
                "_blocked",
                "_written",
                "_scenario",
                "_decisions",
                "_emitted",
                "_recorded",
                "_visible",
                "_verified",
                "_safe",
                "_enforced",
                "_executed",
                "_sandbox",
            )
        )
    }
    score_fields = {
        name: 10
        for name in SupervisedPaperTrialInput.__dataclass_fields__
        if name.endswith("_score")
    }

    result = evaluate_supervised_paper_trial(_ready_input(**failing_fields, **score_fields))

    assert set(result.risks) == set(SupervisedPaperTrialRisk)
    assert result.state is SupervisedPaperTrialState.NOT_READY
    assert result.offline_only is False


def test_trial_scenario_detects_missing_scenario_and_repeatability_gap():
    review = verify_trial_scenario(
        _ready_input(trial_scenario_defined=False, scenario_repeatable=False)
    )

    assert review.passed is False
    assert SupervisedPaperTrialRisk.TRIAL_SCENARIO_MISSING in review.risks
    assert SupervisedPaperTrialRisk.TRIAL_NOT_REPEATABLE in review.risks


def test_supervised_execution_detects_flow_break_override_and_dry_run_gap():
    review = verify_supervised_execution_flow(
        _ready_input(
            human_supervisor_assigned=False,
            human_override_available=False,
            dry_run_output_reconciled=False,
        )
    )

    assert review.passed is False
    assert SupervisedPaperTrialRisk.SUPERVISION_FLOW_BROKEN in review.risks
    assert SupervisedPaperTrialRisk.HUMAN_OVERRIDE_FAILURE in review.risks
    assert SupervisedPaperTrialRisk.DRY_RUN_INCONSISTENCY in review.risks


def test_trial_safety_gate_detects_gate_failure_and_override_gap():
    review = verify_trial_safety_gate(
        _ready_input(safety_gate_passed=False, safety_bypass_blocked=False)
    )

    assert review.passed is False
    assert SupervisedPaperTrialRisk.SAFETY_GATE_FAILURE in review.risks
    assert SupervisedPaperTrialRisk.HUMAN_OVERRIDE_FAILURE in review.risks


def test_trial_journal_detects_incomplete_final_report():
    review = verify_trial_journal(_ready_input(final_report_available=False))

    assert review.passed is False
    assert SupervisedPaperTrialRisk.JOURNAL_INCOMPLETE in review.risks


def test_trial_observability_detects_gap_and_state_drift():
    review = verify_trial_observability(
        _ready_input(observability_events_emitted=False, paper_state_reconciled=False)
    )

    assert review.passed is False
    assert SupervisedPaperTrialRisk.OBSERVABILITY_GAP in review.risks
    assert SupervisedPaperTrialRisk.PAPER_STATE_DRIFT in review.risks


def test_trial_rollback_detects_unverified_path():
    review = verify_trial_rollback_path(_ready_input(rollback_path_available=False))

    assert review.passed is False
    assert SupervisedPaperTrialRisk.ROLLBACK_PATH_UNVERIFIED in review.risks


def test_three_soft_risks_require_review():
    result = evaluate_supervised_paper_trial(
        _ready_input(
            final_report_available=False,
            paper_state_reconciled=False,
            rollback_path_available=False,
        )
    )

    assert result.state is SupervisedPaperTrialState.REVIEW_REQUIRED
    assert SupervisedPaperTrialRisk.JOURNAL_INCOMPLETE in result.risks
    assert SupervisedPaperTrialRisk.PAPER_STATE_DRIFT in result.risks
    assert SupervisedPaperTrialRisk.ROLLBACK_PATH_UNVERIFIED in result.risks


def test_single_soft_risk_is_partially_ready():
    result = evaluate_supervised_paper_trial(_ready_input(paper_state_reconciled=False))

    assert result.state is SupervisedPaperTrialState.PARTIALLY_READY
    assert result.risks == (SupervisedPaperTrialRisk.PAPER_STATE_DRIFT,)


def test_hard_risk_caps_score_and_not_ready():
    data = _ready_input(safety_gate_passed=False)
    risks = detect_trial_risks(data)
    score = compute_trial_score(data, risks)
    result = evaluate_supervised_paper_trial(data)

    assert SupervisedPaperTrialRisk.SAFETY_GATE_FAILURE in risks
    assert score.overall_score <= 40
    assert result.state is SupervisedPaperTrialState.NOT_READY


def test_upstream_broker_or_network_risk_keeps_trial_offline_boundary_closed():
    upstream = _upstream(risks=("BROKER_CONNECTION_RISK",))
    result = evaluate_supervised_paper_trial(_ready_input(paper_broker_adapter=upstream))

    assert result.state is SupervisedPaperTrialState.NOT_READY
    assert result.offline_only is False
    assert SupervisedPaperTrialRisk.DRY_RUN_INCONSISTENCY in result.risks


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_trial_recommendations(
        (
            SupervisedPaperTrialRisk.TRIAL_SCENARIO_MISSING,
            SupervisedPaperTrialRisk.TRIAL_SCENARIO_MISSING,
            SupervisedPaperTrialRisk.OBSERVABILITY_GAP,
            SupervisedPaperTrialRisk.TRIAL_NOT_REPEATABLE,
        ),
        SupervisedPaperTrialState.PARTIALLY_READY,
    )

    assert recommendations.count(SupervisedPaperTrialRecommendation.DEFINE_TRIAL_SCENARIO) == 1
    assert SupervisedPaperTrialRecommendation.RESTORE_TRIAL_OBSERVABILITY in recommendations
    assert SupervisedPaperTrialRecommendation.STABILIZE_TRIAL_REPEATABILITY in recommendations
    assert SupervisedPaperTrialRecommendation.RUN_SUPERVISED_PAPER_TRIAL_SUITE in recommendations


def test_ready_state_adds_broker_paper_sandbox_approval_recommendation():
    result = evaluate_supervised_paper_trial(_ready_input())

    assert (
        SupervisedPaperTrialRecommendation.APPROVE_BROKER_PAPER_SANDBOX_AFTER_MANUAL_REVIEW
        in result.recommendations
    )


def test_markdown_rendering_contains_reviews_trace_risks_and_recommendations():
    result = evaluate_supervised_paper_trial(_ready_input(trial_scenario_defined=False))
    markdown = render_supervised_paper_trial_markdown(result)

    assert "# AGIcore Supervised Paper Trial" in markdown
    assert "# Score Breakdown" in markdown
    assert "# Trial Reviews" in markdown
    assert "# Trial Trace" in markdown
    assert "TRIAL_SCENARIO_MISSING" in markdown
    assert "DEFINE_TRIAL_SCENARIO" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_supervised_paper_trial(_ready_input().__dict__)

    assert result.state is SupervisedPaperTrialState.READY_FOR_BROKER_PAPER_SANDBOX
    assert result.trial_score >= 94


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            SupervisedPaperTrialRisk.ROLLBACK_PATH_UNVERIFIED,
            SupervisedPaperTrialRecommendation.VERIFY_ROLLBACK_PATH,
        ),
        (
            SupervisedPaperTrialRisk.HUMAN_OVERRIDE_FAILURE,
            SupervisedPaperTrialRecommendation.ENABLE_HUMAN_OVERRIDE,
        ),
    ],
)
def test_recommendation_mapping_for_rollback_and_override_risks(risk, recommendation):
    recommendations = generate_trial_recommendations((risk,), SupervisedPaperTrialState.PARTIALLY_READY)

    assert recommendation in recommendations


def test_module_keeps_offline_import_boundary():
    module_path = (
        Path(__file__).parents[3]
        / "src"
        / "agicore"
        / "trading"
        / "supervised_paper_trial.py"
    )
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
