from types import SimpleNamespace

import pytest

from agicore.trading.controlled_paper_run import (
    compute_controlled_paper_score,
    detect_controlled_paper_risks,
    evaluate_controlled_paper_run,
    generate_controlled_paper_recommendations,
    render_controlled_paper_markdown,
    verify_emergency_shutdown_path,
    verify_human_validation_gate,
    verify_paper_recovery_path,
    verify_paper_session_controls,
    verify_simulated_trade_flow,
)
from agicore.trading.controlled_paper_run_models import (
    ControlledPaperRunInput,
    ControlledPaperRunRecommendation,
    ControlledPaperRunRisk,
    ControlledPaperRunState,
)


def _upstream(**overrides):
    data = {
        "state": "READY",
        "paper_loop_score": 96,
        "paper_runtime_score": 96,
        "observability_score": 96,
        "rollback_score": 96,
        "kill_switch_score": 96,
        "isolation_score": 96,
        "sandbox_score": 96,
        "risks": (),
        "blockers": (),
        "offline_only": True,
        "score_breakdown": SimpleNamespace(
            paper_loop_score=96,
            paper_runtime_score=96,
            observability_score=96,
            rollback_score=96,
            kill_switch_score=96,
            isolation_score=96,
        ),
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def _ready_input(**overrides):
    data = {
        "paper_execution_loop_readiness": _upstream(state="READY_FOR_CONTROLLED_PAPER_RUN"),
        "paper_runtime_preparation": _upstream(state="READY_FOR_PAPER_EXECUTION_LOOP"),
        "observability_verification": _upstream(state="READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream(state="READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream(state="READY_FOR_ROLLBACK_VERIFICATION"),
        "runtime_isolation_review": _upstream(state="READY_FOR_PAPER_RUNTIME"),
        "sandbox_readiness_audit": _upstream(state="SANDBOX_READY"),
        "stable_review": _upstream(state="STABLE"),
        "human_operator_assigned": True,
        "manual_approval_required": True,
        "manual_approval_recorded": True,
        "session_scope_acknowledged": True,
        "simulated_trade_flow_defined": True,
        "paper_order_preview_available": True,
        "paper_fill_simulation_available": True,
        "paper_pnl_preview_available": True,
        "flow_repeatable": True,
        "session_limits_configured": True,
        "risk_limits_enforced": True,
        "safety_guards_locked": True,
        "session_state_checkpointed": True,
        "controlled_run_repeatable": True,
        "emergency_shutdown_available": True,
        "kill_switch_linked": True,
        "shutdown_drill_verified": True,
        "post_shutdown_state_safe": True,
        "recovery_path_available": True,
        "rollback_linked": True,
        "recovery_drill_verified": True,
        "post_recovery_state_consistent": True,
        "observability_connected": True,
        "ready_for_human_validated_session": True,
        "human_validation_score": 96,
        "simulated_trade_flow_score": 96,
        "paper_session_control_score": 96,
        "emergency_shutdown_score": 96,
        "paper_recovery_score": 96,
        "observability_score": 96,
    }
    data.update(overrides)
    return ControlledPaperRunInput(**data)


def test_evaluate_controlled_paper_ready_for_human_session_when_all_components_are_ready():
    result = evaluate_controlled_paper_run(_ready_input())

    assert result.state is ControlledPaperRunState.READY_FOR_HUMAN_VALIDATED_SESSION
    assert result.risks == ()
    assert result.controlled_paper_score >= 94
    assert result.offline_only is True
    assert result.controlled_paper_graph.ready_edges == (
        ("human_operator", "validation_gate"),
        ("validation_gate", "simulated_trade_flow"),
        ("simulated_trade_flow", "session_controls"),
        ("session_controls", "emergency_shutdown"),
        ("emergency_shutdown", "recovery_path"),
        ("recovery_path", "human_validated_session"),
    )
    assert result.human_validation_review.passed is True
    assert result.simulated_trade_flow_review.passed is True
    assert result.paper_session_controls_review.passed is True
    assert result.emergency_shutdown_review.passed is True
    assert result.paper_recovery_review.passed is True


def test_detect_controlled_paper_risks_reports_all_failures():
    data = _ready_input(
        human_operator_assigned=False,
        manual_approval_required=False,
        manual_approval_recorded=False,
        session_scope_acknowledged=False,
        simulated_trade_flow_defined=False,
        paper_order_preview_available=False,
        paper_fill_simulation_available=False,
        paper_pnl_preview_available=False,
        flow_repeatable=False,
        session_limits_configured=False,
        risk_limits_enforced=False,
        safety_guards_locked=False,
        session_state_checkpointed=False,
        controlled_run_repeatable=False,
        emergency_shutdown_available=False,
        kill_switch_linked=False,
        shutdown_drill_verified=False,
        post_shutdown_state_safe=False,
        recovery_path_available=False,
        rollback_linked=False,
        recovery_drill_verified=False,
        post_recovery_state_consistent=False,
        observability_connected=False,
        human_validation_score=10,
        simulated_trade_flow_score=10,
        paper_session_control_score=10,
        emergency_shutdown_score=10,
        paper_recovery_score=10,
        observability_score=10,
    )

    risks = detect_controlled_paper_risks(data)

    assert set(risks) == set(ControlledPaperRunRisk)


def test_missing_human_validation_forces_not_ready():
    result = evaluate_controlled_paper_run(_ready_input(manual_approval_recorded=False))

    assert result.state is ControlledPaperRunState.NOT_READY
    assert ControlledPaperRunRisk.HUMAN_VALIDATION_MISSING in result.risks
    assert result.controlled_paper_graph.blocked_edges == (
        ("human_operator", "validation_gate"),
    )


def test_emergency_shutdown_missing_forces_not_ready():
    result = evaluate_controlled_paper_run(
        _ready_input(emergency_shutdown_available=False, kill_switch_linked=False)
    )

    assert result.state is ControlledPaperRunState.NOT_READY
    assert ControlledPaperRunRisk.EMERGENCY_SHUTDOWN_UNAVAILABLE in result.risks
    assert ControlledPaperRunRisk.SAFETY_GUARD_BYPASS in result.risks


def test_three_soft_risks_require_review_without_hard_failure():
    result = evaluate_controlled_paper_run(
        _ready_input(
            flow_repeatable=False,
            controlled_run_repeatable=False,
            observability_connected=False,
        )
    )

    assert result.state is ControlledPaperRunState.REVIEW_REQUIRED
    assert {
        ControlledPaperRunRisk.PAPER_EXECUTION_DRIFT,
        ControlledPaperRunRisk.CONTROLLED_RUN_NOT_REPEATABLE,
        ControlledPaperRunRisk.OBSERVABILITY_LOSS,
    }.issubset(result.risks)


def test_single_soft_risk_yields_partially_ready():
    result = evaluate_controlled_paper_run(_ready_input(flow_repeatable=False))

    assert result.state is ControlledPaperRunState.PARTIALLY_READY
    assert result.risks == (ControlledPaperRunRisk.PAPER_EXECUTION_DRIFT,)


def test_controlled_paper_ready_when_clean_but_human_session_gate_not_ready():
    result = evaluate_controlled_paper_run(
        _ready_input(
            ready_for_human_validated_session=False,
            human_validation_score=89,
            simulated_trade_flow_score=89,
            paper_session_control_score=89,
            emergency_shutdown_score=89,
            paper_recovery_score=89,
            observability_score=89,
        )
    )

    assert result.state is ControlledPaperRunState.CONTROLLED_PAPER_READY
    assert result.risks == ()
    assert result.controlled_paper_score >= 88


def test_review_sections_expose_specific_controlled_paper_risks():
    data = _ready_input(
        human_operator_assigned=False,
        simulated_trade_flow_defined=False,
        risk_limits_enforced=False,
        emergency_shutdown_available=False,
        recovery_path_available=False,
    )

    assert ControlledPaperRunRisk.HUMAN_VALIDATION_MISSING in verify_human_validation_gate(data).risks
    assert ControlledPaperRunRisk.SIMULATED_TRADE_FLOW_INVALID in verify_simulated_trade_flow(data).risks
    assert ControlledPaperRunRisk.SAFETY_GUARD_BYPASS in verify_paper_session_controls(data).risks
    assert ControlledPaperRunRisk.EMERGENCY_SHUTDOWN_UNAVAILABLE in verify_emergency_shutdown_path(data).risks
    assert ControlledPaperRunRisk.RECOVERY_PATH_UNVERIFIED in verify_paper_recovery_path(data).risks


def test_compute_controlled_paper_score_caps_hard_risks():
    data = _ready_input(manual_approval_recorded=False, safety_guards_locked=False)
    sections = (
        verify_human_validation_gate(data),
        verify_simulated_trade_flow(data),
        verify_paper_session_controls(data),
        verify_emergency_shutdown_path(data),
        verify_paper_recovery_path(data),
    )
    risks = (
        ControlledPaperRunRisk.HUMAN_VALIDATION_MISSING,
        ControlledPaperRunRisk.SAFETY_GUARD_BYPASS,
    )

    score = compute_controlled_paper_score(data, risks, *sections)

    assert score.overall_score <= 45


def test_generate_recommendations_are_deduplicated_and_risk_driven():
    result = evaluate_controlled_paper_run(
        _ready_input(
            manual_approval_recorded=False,
            risk_limits_enforced=False,
            observability_connected=False,
        )
    )

    recommendations = generate_controlled_paper_recommendations(result.risks, result.state)

    assert ControlledPaperRunRecommendation.REQUIRE_HUMAN_VALIDATION_GATE in recommendations
    assert ControlledPaperRunRecommendation.ENFORCE_SAFETY_GUARDS in recommendations
    assert ControlledPaperRunRecommendation.RESTORE_OBSERVABILITY_COVERAGE in recommendations
    assert len(recommendations) == len(set(recommendations))


def test_markdown_contains_controlled_paper_sections():
    result = evaluate_controlled_paper_run(_ready_input())

    markdown = render_controlled_paper_markdown(result)

    assert "# AGIcore Controlled Paper Run" in markdown
    assert "# Controlled Paper Graph" in markdown
    assert "# Controlled Paper Risks" in markdown
    assert "READY_FOR_HUMAN_VALIDATED_SESSION" in markdown


def test_evaluate_controlled_paper_run_accepts_mapping_input_and_upstream_results():
    result = evaluate_controlled_paper_run(
        {
            "paper_execution_loop_readiness": _upstream(state="READY_FOR_CONTROLLED_PAPER_RUN"),
            "paper_runtime_preparation": _upstream(state="READY_FOR_PAPER_EXECUTION_LOOP"),
            "observability_verification": _upstream(state="READY_FOR_PAPER_RUNTIME_PREP"),
            "rollback_verification": _upstream(state="READY_FOR_OBSERVABILITY_VERIFICATION"),
            "kill_switch_verification": _upstream(state="READY_FOR_ROLLBACK_VERIFICATION"),
            "runtime_isolation_review": _upstream(state="READY_FOR_PAPER_RUNTIME"),
            "sandbox_readiness_audit": _upstream(state="SANDBOX_READY"),
            "stable_review": _upstream(state="STABLE"),
            "human_operator_assigned": True,
            "manual_approval_required": True,
            "manual_approval_recorded": True,
            "session_scope_acknowledged": True,
            "simulated_trade_flow_defined": True,
            "paper_order_preview_available": True,
            "paper_fill_simulation_available": True,
            "paper_pnl_preview_available": True,
            "flow_repeatable": True,
            "session_limits_configured": True,
            "risk_limits_enforced": True,
            "safety_guards_locked": True,
            "session_state_checkpointed": True,
            "controlled_run_repeatable": True,
            "emergency_shutdown_available": True,
            "kill_switch_linked": True,
            "shutdown_drill_verified": True,
            "post_shutdown_state_safe": True,
            "recovery_path_available": True,
            "rollback_linked": True,
            "recovery_drill_verified": True,
            "post_recovery_state_consistent": True,
            "observability_connected": True,
            "ready_for_human_validated_session": True,
        }
    )

    assert result.state is ControlledPaperRunState.READY_FOR_HUMAN_VALIDATED_SESSION
    assert result.risks == ()


@pytest.mark.parametrize(
    ("risk", "expected"),
    [
        (
            ControlledPaperRunRisk.SAFETY_GUARD_BYPASS,
            ControlledPaperRunRecommendation.ENFORCE_SAFETY_GUARDS,
        ),
        (
            ControlledPaperRunRisk.CONTROLLED_RUN_NOT_REPEATABLE,
            ControlledPaperRunRecommendation.MAKE_CONTROLLED_RUN_REPEATABLE,
        ),
    ],
)
def test_recommendation_mapping_for_safety_and_repeatability_risks(risk, expected):
    result = evaluate_controlled_paper_run(_ready_input())

    assert expected in generate_controlled_paper_recommendations((risk,), result.state)
