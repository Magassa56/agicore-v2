from types import SimpleNamespace

import pytest

from agicore.trading.supervised_paper_session import (
    compute_supervised_session_score,
    detect_supervised_session_risks,
    evaluate_supervised_paper_session,
    generate_supervised_session_recommendations,
    render_supervised_paper_session_markdown,
    verify_decision_traceability,
    verify_emergency_intervention,
    verify_operator_visibility,
    verify_session_monitoring,
    verify_supervision_chain,
)
from agicore.trading.supervised_paper_session_models import (
    SupervisedPaperSessionInput,
    SupervisedPaperSessionRecommendation,
    SupervisedPaperSessionRisk,
    SupervisedPaperSessionState,
)


def _upstream(**overrides):
    data = {
        "state": "READY",
        "human_validation_score": 96,
        "controlled_paper_score": 96,
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
            human_validation_score=96,
            controlled_paper_score=96,
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
        "human_validated_paper_session": _upstream(state="READY_FOR_SUPERVISED_PAPER_SESSION"),
        "controlled_paper_run": _upstream(state="READY_FOR_HUMAN_VALIDATED_SESSION"),
        "paper_execution_loop_readiness": _upstream(state="READY_FOR_CONTROLLED_PAPER_RUN"),
        "paper_runtime_preparation": _upstream(state="READY_FOR_PAPER_EXECUTION_LOOP"),
        "observability_verification": _upstream(state="READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream(state="READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream(state="READY_FOR_ROLLBACK_VERIFICATION"),
        "runtime_isolation_review": _upstream(state="READY_FOR_PAPER_RUNTIME"),
        "sandbox_readiness_audit": _upstream(state="SANDBOX_READY"),
        "stable_review": _upstream(state="STABLE"),
        "human_supervisor_assigned": True,
        "supervision_protocol_defined": True,
        "continuous_supervision_required": True,
        "supervision_handoff_blocked": True,
        "operator_dashboard_available": True,
        "live_session_state_visible": True,
        "risk_state_visible": True,
        "paper_position_visible": True,
        "human_override_available": True,
        "emergency_stop_available": True,
        "kill_switch_linked": True,
        "emergency_drill_verified": True,
        "operator_can_halt_session": True,
        "post_halt_state_safe": True,
        "session_metrics_streaming": True,
        "critical_alerts_enabled": True,
        "audit_events_streaming": True,
        "rollback_linked": True,
        "observability_linked": True,
        "decision_trace_enabled": True,
        "decision_inputs_recorded": True,
        "decision_outputs_recorded": True,
        "operator_decisions_logged": True,
        "session_drift_monitoring_enabled": True,
        "safety_bypass_blocked": True,
        "ready_for_paper_broker_adapter": True,
        "supervision_chain_score": 96,
        "operator_visibility_score": 96,
        "emergency_intervention_score": 96,
        "session_monitoring_score": 96,
        "decision_traceability_score": 96,
        "observability_score": 96,
    }
    data.update(overrides)
    return SupervisedPaperSessionInput(**data)


def test_evaluate_supervised_session_ready_for_paper_broker_adapter_when_all_components_are_ready():
    result = evaluate_supervised_paper_session(_ready_input())

    assert result.state is SupervisedPaperSessionState.READY_FOR_PAPER_BROKER_ADAPTER
    assert result.risks == ()
    assert result.supervised_session_score >= 94
    assert result.offline_only is True
    assert result.supervised_session_graph.ready_edges == (
        ("supervision_chain", "operator_visibility"),
        ("operator_visibility", "emergency_intervention"),
        ("emergency_intervention", "session_monitoring"),
        ("session_monitoring", "decision_traceability"),
        ("decision_traceability", "paper_broker_adapter"),
    )
    assert result.supervision_chain_review.passed is True
    assert result.operator_visibility_review.passed is True
    assert result.emergency_intervention_review.passed is True
    assert result.session_monitoring_review.passed is True
    assert result.decision_traceability_review.passed is True


def test_detect_supervised_session_risks_reports_all_failures():
    data = _ready_input(
        human_supervisor_assigned=False,
        supervision_protocol_defined=False,
        continuous_supervision_required=False,
        supervision_handoff_blocked=False,
        operator_dashboard_available=False,
        live_session_state_visible=False,
        risk_state_visible=False,
        paper_position_visible=False,
        human_override_available=False,
        emergency_stop_available=False,
        kill_switch_linked=False,
        emergency_drill_verified=False,
        operator_can_halt_session=False,
        post_halt_state_safe=False,
        session_metrics_streaming=False,
        critical_alerts_enabled=False,
        audit_events_streaming=False,
        rollback_linked=False,
        observability_linked=False,
        decision_trace_enabled=False,
        decision_inputs_recorded=False,
        decision_outputs_recorded=False,
        operator_decisions_logged=False,
        session_drift_monitoring_enabled=False,
        safety_bypass_blocked=False,
        supervision_chain_score=10,
        operator_visibility_score=10,
        emergency_intervention_score=10,
        session_monitoring_score=10,
        decision_traceability_score=10,
        observability_score=10,
    )

    risks = detect_supervised_session_risks(data)

    assert set(risks) == set(SupervisedPaperSessionRisk)


def test_broken_supervision_chain_forces_not_ready():
    result = evaluate_supervised_paper_session(_ready_input(human_supervisor_assigned=False))

    assert result.state is SupervisedPaperSessionState.NOT_READY
    assert SupervisedPaperSessionRisk.SUPERVISION_CHAIN_BROKEN in result.risks
    assert result.supervised_session_graph.blocked_edges == (
        ("supervision_chain", "operator_visibility"),
    )


def test_operator_visibility_detects_dashboard_and_override_failures():
    section = verify_operator_visibility(
        _ready_input(operator_dashboard_available=False, human_override_available=False)
    )

    assert section.passed is False
    assert SupervisedPaperSessionRisk.OPERATOR_VISIBILITY_LOSS in section.risks
    assert SupervisedPaperSessionRisk.HUMAN_OVERRIDE_FAILURE in section.risks


def test_emergency_intervention_detects_halt_failure_and_drift():
    section = verify_emergency_intervention(
        _ready_input(emergency_stop_available=False, post_halt_state_safe=False)
    )

    assert section.passed is False
    assert SupervisedPaperSessionRisk.EMERGENCY_INTERVENTION_FAILURE in section.risks
    assert SupervisedPaperSessionRisk.PAPER_SESSION_DRIFT in section.risks


def test_session_monitoring_detects_observability_and_rollback_gaps():
    section = verify_session_monitoring(
        _ready_input(session_metrics_streaming=False, observability_linked=False, rollback_linked=False)
    )

    assert section.passed is False
    assert SupervisedPaperSessionRisk.SESSION_MONITORING_GAP in section.risks
    assert SupervisedPaperSessionRisk.OBSERVABILITY_DEGRADATION in section.risks
    assert SupervisedPaperSessionRisk.ROLLBACK_UNAVAILABLE in section.risks


def test_decision_traceability_detects_traceability_drift_and_safety_bypass():
    section = verify_decision_traceability(
        _ready_input(
            decision_trace_enabled=False,
            session_drift_monitoring_enabled=False,
            safety_bypass_blocked=False,
        )
    )

    assert section.passed is False
    assert SupervisedPaperSessionRisk.DECISION_TRACEABILITY_LOSS in section.risks
    assert SupervisedPaperSessionRisk.PAPER_SESSION_DRIFT in section.risks
    assert SupervisedPaperSessionRisk.SAFETY_BYPASS_RISK in section.risks


def test_three_soft_risks_require_review_without_hard_failure():
    result = evaluate_supervised_paper_session(
        _ready_input(
            decision_trace_enabled=False,
            observability_linked=False,
            session_drift_monitoring_enabled=False,
        )
    )

    assert result.state is SupervisedPaperSessionState.REVIEW_REQUIRED
    assert {
        SupervisedPaperSessionRisk.DECISION_TRACEABILITY_LOSS,
        SupervisedPaperSessionRisk.OBSERVABILITY_DEGRADATION,
        SupervisedPaperSessionRisk.PAPER_SESSION_DRIFT,
    }.issubset(result.risks)


def test_single_soft_risk_yields_partially_ready():
    result = evaluate_supervised_paper_session(
        _ready_input(session_drift_monitoring_enabled=False)
    )

    assert result.state is SupervisedPaperSessionState.PARTIALLY_READY
    assert result.risks == (SupervisedPaperSessionRisk.PAPER_SESSION_DRIFT,)


def test_supervised_session_ready_when_clean_but_broker_adapter_gate_not_ready():
    result = evaluate_supervised_paper_session(
        _ready_input(
            ready_for_paper_broker_adapter=False,
            supervision_chain_score=89,
            operator_visibility_score=89,
            emergency_intervention_score=89,
            session_monitoring_score=89,
            decision_traceability_score=89,
            observability_score=89,
        )
    )

    assert result.state is SupervisedPaperSessionState.SUPERVISED_SESSION_READY
    assert result.risks == ()
    assert result.supervised_session_score >= 88


def test_review_sections_expose_specific_supervised_session_risks():
    data = _ready_input(
        supervision_protocol_defined=False,
        operator_dashboard_available=False,
        kill_switch_linked=False,
        critical_alerts_enabled=False,
        decision_inputs_recorded=False,
    )

    assert SupervisedPaperSessionRisk.SUPERVISION_CHAIN_BROKEN in verify_supervision_chain(data).risks
    assert SupervisedPaperSessionRisk.OPERATOR_VISIBILITY_LOSS in verify_operator_visibility(data).risks
    assert SupervisedPaperSessionRisk.EMERGENCY_INTERVENTION_FAILURE in verify_emergency_intervention(data).risks
    assert SupervisedPaperSessionRisk.SESSION_MONITORING_GAP in verify_session_monitoring(data).risks
    assert SupervisedPaperSessionRisk.DECISION_TRACEABILITY_LOSS in verify_decision_traceability(data).risks


def test_compute_supervised_session_score_caps_hard_risks():
    data = _ready_input(human_supervisor_assigned=False, safety_bypass_blocked=False)
    sections = (
        verify_supervision_chain(data),
        verify_operator_visibility(data),
        verify_emergency_intervention(data),
        verify_session_monitoring(data),
        verify_decision_traceability(data),
    )
    risks = (
        SupervisedPaperSessionRisk.SUPERVISION_CHAIN_BROKEN,
        SupervisedPaperSessionRisk.SAFETY_BYPASS_RISK,
    )

    score = compute_supervised_session_score(data, risks, *sections)

    assert score.overall_score <= 45


def test_generate_recommendations_are_deduplicated_and_risk_driven():
    result = evaluate_supervised_paper_session(
        _ready_input(
            human_supervisor_assigned=False,
            observability_linked=False,
            rollback_linked=False,
        )
    )

    recommendations = generate_supervised_session_recommendations(result.risks, result.state)

    assert SupervisedPaperSessionRecommendation.REPAIR_SUPERVISION_CHAIN in recommendations
    assert SupervisedPaperSessionRecommendation.RESTORE_OBSERVABILITY in recommendations
    assert SupervisedPaperSessionRecommendation.LINK_ROLLBACK in recommendations
    assert len(recommendations) == len(set(recommendations))


def test_markdown_contains_supervised_session_sections():
    result = evaluate_supervised_paper_session(_ready_input())

    markdown = render_supervised_paper_session_markdown(result)

    assert "# AGIcore Supervised Paper Session" in markdown
    assert "# Supervised Session Graph" in markdown
    assert "# Supervised Session Risks" in markdown
    assert "READY_FOR_PAPER_BROKER_ADAPTER" in markdown


def test_evaluate_supervised_session_accepts_mapping_input_and_upstream_results():
    result = evaluate_supervised_paper_session(
        {
            "human_validated_paper_session": _upstream(state="READY_FOR_SUPERVISED_PAPER_SESSION"),
            "controlled_paper_run": _upstream(state="READY_FOR_HUMAN_VALIDATED_SESSION"),
            "paper_execution_loop_readiness": _upstream(state="READY_FOR_CONTROLLED_PAPER_RUN"),
            "paper_runtime_preparation": _upstream(state="READY_FOR_PAPER_EXECUTION_LOOP"),
            "observability_verification": _upstream(state="READY_FOR_PAPER_RUNTIME_PREP"),
            "rollback_verification": _upstream(state="READY_FOR_OBSERVABILITY_VERIFICATION"),
            "kill_switch_verification": _upstream(state="READY_FOR_ROLLBACK_VERIFICATION"),
            "runtime_isolation_review": _upstream(state="READY_FOR_PAPER_RUNTIME"),
            "sandbox_readiness_audit": _upstream(state="SANDBOX_READY"),
            "stable_review": _upstream(state="STABLE"),
            "human_supervisor_assigned": True,
            "supervision_protocol_defined": True,
            "continuous_supervision_required": True,
            "supervision_handoff_blocked": True,
            "operator_dashboard_available": True,
            "live_session_state_visible": True,
            "risk_state_visible": True,
            "paper_position_visible": True,
            "human_override_available": True,
            "emergency_stop_available": True,
            "kill_switch_linked": True,
            "emergency_drill_verified": True,
            "operator_can_halt_session": True,
            "post_halt_state_safe": True,
            "session_metrics_streaming": True,
            "critical_alerts_enabled": True,
            "audit_events_streaming": True,
            "rollback_linked": True,
            "observability_linked": True,
            "decision_trace_enabled": True,
            "decision_inputs_recorded": True,
            "decision_outputs_recorded": True,
            "operator_decisions_logged": True,
            "session_drift_monitoring_enabled": True,
            "safety_bypass_blocked": True,
            "ready_for_paper_broker_adapter": True,
        }
    )

    assert result.state is SupervisedPaperSessionState.READY_FOR_PAPER_BROKER_ADAPTER
    assert result.risks == ()


@pytest.mark.parametrize(
    ("risk", "expected"),
    [
        (
            SupervisedPaperSessionRisk.HUMAN_OVERRIDE_FAILURE,
            SupervisedPaperSessionRecommendation.ENABLE_HUMAN_OVERRIDE,
        ),
        (
            SupervisedPaperSessionRisk.SAFETY_BYPASS_RISK,
            SupervisedPaperSessionRecommendation.BLOCK_SAFETY_BYPASS,
        ),
    ],
)
def test_recommendation_mapping_for_override_and_safety_risks(risk, expected):
    result = evaluate_supervised_paper_session(_ready_input())

    assert expected in generate_supervised_session_recommendations((risk,), result.state)
