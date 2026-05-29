from types import SimpleNamespace

import pytest

from agicore.trading.human_validated_paper_session import (
    compute_human_validation_score,
    detect_human_validation_risks,
    evaluate_human_validated_paper_session,
    generate_human_validation_recommendations,
    render_human_validated_paper_session_markdown,
    verify_auditability_requirements,
    verify_human_approval_gate,
    verify_operator_confirmation_flow,
    verify_reversibility_requirements,
    verify_session_authorization,
)
from agicore.trading.human_validated_paper_session_models import (
    HumanValidatedPaperSessionInput,
    HumanValidatedPaperSessionState,
    HumanValidationRecommendation,
    HumanValidationRisk,
)


def _upstream(**overrides):
    data = {
        "state": "READY",
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
        "controlled_paper_run": _upstream(state="READY_FOR_HUMAN_VALIDATED_SESSION"),
        "paper_execution_loop_readiness": _upstream(state="READY_FOR_CONTROLLED_PAPER_RUN"),
        "paper_runtime_preparation": _upstream(state="READY_FOR_PAPER_EXECUTION_LOOP"),
        "observability_verification": _upstream(state="READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream(state="READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream(state="READY_FOR_ROLLBACK_VERIFICATION"),
        "runtime_isolation_review": _upstream(state="READY_FOR_PAPER_RUNTIME"),
        "sandbox_readiness_audit": _upstream(state="SANDBOX_READY"),
        "stable_review": _upstream(state="STABLE"),
        "assigned_operator_present": True,
        "explicit_approval_required": True,
        "explicit_approval_captured": True,
        "approval_timestamp_recorded": True,
        "session_scope_confirmed": True,
        "operator_identity_verified": True,
        "confirmation_challenge_completed": True,
        "risk_acknowledgement_recorded": True,
        "dry_run_acknowledged": True,
        "human_override_available": True,
        "session_id_assigned": True,
        "session_limits_authorized": True,
        "paper_only_authorized": True,
        "autonomy_disabled": True,
        "validation_bypass_blocked": True,
        "audit_trail_enabled": True,
        "decision_trace_enabled": True,
        "operator_actions_logged": True,
        "session_events_exportable": True,
        "observability_linked": True,
        "rollback_plan_attached": True,
        "kill_switch_attached": True,
        "recovery_checkpoint_available": True,
        "reversal_drill_recorded": True,
        "session_drift_monitoring_enabled": True,
        "ready_for_supervised_paper_session": True,
        "human_approval_score": 96,
        "operator_confirmation_score": 96,
        "session_authorization_score": 96,
        "auditability_score": 96,
        "reversibility_score": 96,
        "supervision_score": 96,
    }
    data.update(overrides)
    return HumanValidatedPaperSessionInput(**data)


def test_evaluate_human_validated_session_ready_when_all_gates_are_ready():
    result = evaluate_human_validated_paper_session(_ready_input())

    assert result.state is HumanValidatedPaperSessionState.READY_FOR_SUPERVISED_PAPER_SESSION
    assert result.risks == ()
    assert result.human_validation_score >= 94
    assert result.offline_only is True
    assert result.human_validation_graph.ready_edges == (
        ("human_approval_gate", "operator_confirmation"),
        ("operator_confirmation", "session_authorization"),
        ("session_authorization", "auditability"),
        ("auditability", "reversibility"),
        ("reversibility", "supervised_paper_session"),
    )
    assert result.human_approval_review.passed is True
    assert result.operator_confirmation_review.passed is True
    assert result.session_authorization_review.passed is True
    assert result.auditability_review.passed is True
    assert result.reversibility_review.passed is True


def test_detect_human_validation_risks_reports_all_failures():
    data = _ready_input(
        assigned_operator_present=False,
        explicit_approval_required=False,
        explicit_approval_captured=False,
        approval_timestamp_recorded=False,
        session_scope_confirmed=False,
        operator_identity_verified=False,
        confirmation_challenge_completed=False,
        risk_acknowledgement_recorded=False,
        dry_run_acknowledged=False,
        human_override_available=False,
        session_id_assigned=False,
        session_limits_authorized=False,
        paper_only_authorized=False,
        autonomy_disabled=False,
        validation_bypass_blocked=False,
        audit_trail_enabled=False,
        decision_trace_enabled=False,
        operator_actions_logged=False,
        session_events_exportable=False,
        observability_linked=False,
        rollback_plan_attached=False,
        kill_switch_attached=False,
        recovery_checkpoint_available=False,
        reversal_drill_recorded=False,
        session_drift_monitoring_enabled=False,
        human_approval_score=10,
        operator_confirmation_score=10,
        session_authorization_score=10,
        auditability_score=10,
        reversibility_score=10,
        supervision_score=10,
    )

    risks = detect_human_validation_risks(data)

    assert set(risks) == set(HumanValidationRisk)


def test_human_approval_gate_blocks_without_explicit_approval():
    result = evaluate_human_validated_paper_session(
        _ready_input(explicit_approval_captured=False)
    )

    assert result.state is HumanValidatedPaperSessionState.NOT_READY
    assert HumanValidationRisk.HUMAN_APPROVAL_MISSING in result.risks
    assert result.human_validation_graph.blocked_edges == (
        ("human_approval_gate", "operator_confirmation"),
    )


def test_operator_confirmation_flow_detects_missing_confirmation_and_override():
    section = verify_operator_confirmation_flow(
        _ready_input(confirmation_challenge_completed=False, human_override_available=False)
    )

    assert section.passed is False
    assert HumanValidationRisk.OPERATOR_CONFIRMATION_FAILURE in section.risks
    assert HumanValidationRisk.HUMAN_OVERRIDE_UNAVAILABLE in section.risks


def test_session_authorization_detects_missing_scope_and_validation_bypass():
    section = verify_session_authorization(
        _ready_input(session_limits_authorized=False, validation_bypass_blocked=False)
    )

    assert section.passed is False
    assert HumanValidationRisk.SESSION_AUTHORIZATION_MISSING in section.risks
    assert HumanValidationRisk.VALIDATION_BYPASS_RISK in section.risks


def test_auditability_requirements_detect_trace_and_supervision_gaps():
    section = verify_auditability_requirements(
        _ready_input(decision_trace_enabled=False, observability_linked=False)
    )

    assert section.passed is False
    assert HumanValidationRisk.DECISION_TRACEABILITY_LOSS in section.risks
    assert HumanValidationRisk.SUPERVISION_GAP in section.risks


def test_reversibility_requirements_detect_unverified_reversal_and_drift():
    section = verify_reversibility_requirements(
        _ready_input(reversal_drill_recorded=False, session_drift_monitoring_enabled=False)
    )

    assert section.passed is False
    assert HumanValidationRisk.REVERSIBILITY_NOT_VERIFIED in section.risks
    assert HumanValidationRisk.PAPER_SESSION_DRIFT in section.risks


def test_three_soft_risks_require_review_without_hard_failure():
    result = evaluate_human_validated_paper_session(
        _ready_input(
            decision_trace_enabled=False,
            observability_linked=False,
            session_drift_monitoring_enabled=False,
        )
    )

    assert result.state is HumanValidatedPaperSessionState.REVIEW_REQUIRED
    assert {
        HumanValidationRisk.DECISION_TRACEABILITY_LOSS,
        HumanValidationRisk.SUPERVISION_GAP,
        HumanValidationRisk.PAPER_SESSION_DRIFT,
    }.issubset(result.risks)


def test_single_soft_risk_yields_partially_ready():
    result = evaluate_human_validated_paper_session(
        _ready_input(session_drift_monitoring_enabled=False)
    )

    assert result.state is HumanValidatedPaperSessionState.PARTIALLY_READY
    assert result.risks == (HumanValidationRisk.PAPER_SESSION_DRIFT,)


def test_human_validation_ready_when_clean_but_supervised_session_gate_not_ready():
    result = evaluate_human_validated_paper_session(
        _ready_input(
            ready_for_supervised_paper_session=False,
            human_approval_score=89,
            operator_confirmation_score=89,
            session_authorization_score=89,
            auditability_score=89,
            reversibility_score=89,
            supervision_score=89,
        )
    )

    assert result.state is HumanValidatedPaperSessionState.HUMAN_VALIDATION_READY
    assert result.risks == ()
    assert result.human_validation_score >= 88


def test_review_sections_expose_specific_human_validation_risks():
    data = _ready_input(
        explicit_approval_captured=False,
        operator_identity_verified=False,
        paper_only_authorized=False,
        audit_trail_enabled=False,
        rollback_plan_attached=False,
    )

    assert HumanValidationRisk.HUMAN_APPROVAL_MISSING in verify_human_approval_gate(data).risks
    assert HumanValidationRisk.OPERATOR_CONFIRMATION_FAILURE in verify_operator_confirmation_flow(data).risks
    assert HumanValidationRisk.SESSION_AUTHORIZATION_MISSING in verify_session_authorization(data).risks
    assert HumanValidationRisk.AUDIT_TRAIL_INCOMPLETE in verify_auditability_requirements(data).risks
    assert HumanValidationRisk.REVERSIBILITY_NOT_VERIFIED in verify_reversibility_requirements(data).risks


def test_compute_human_validation_score_caps_hard_risks():
    data = _ready_input(explicit_approval_captured=False, validation_bypass_blocked=False)
    sections = (
        verify_human_approval_gate(data),
        verify_operator_confirmation_flow(data),
        verify_session_authorization(data),
        verify_auditability_requirements(data),
        verify_reversibility_requirements(data),
    )
    risks = (
        HumanValidationRisk.HUMAN_APPROVAL_MISSING,
        HumanValidationRisk.VALIDATION_BYPASS_RISK,
    )

    score = compute_human_validation_score(data, risks, *sections)

    assert score.overall_score <= 45


def test_generate_recommendations_are_deduplicated_and_risk_driven():
    result = evaluate_human_validated_paper_session(
        _ready_input(
            explicit_approval_captured=False,
            decision_trace_enabled=False,
            session_drift_monitoring_enabled=False,
        )
    )

    recommendations = generate_human_validation_recommendations(result.risks, result.state)

    assert HumanValidationRecommendation.CAPTURE_EXPLICIT_HUMAN_APPROVAL in recommendations
    assert HumanValidationRecommendation.RESTORE_DECISION_TRACEABILITY in recommendations
    assert HumanValidationRecommendation.LOCK_PAPER_SESSION_DETERMINISM in recommendations
    assert len(recommendations) == len(set(recommendations))


def test_markdown_contains_human_validated_session_sections():
    result = evaluate_human_validated_paper_session(_ready_input())

    markdown = render_human_validated_paper_session_markdown(result)

    assert "# AGIcore Human Validated Paper Session" in markdown
    assert "# Human Validation Graph" in markdown
    assert "# Human Validation Risks" in markdown
    assert "READY_FOR_SUPERVISED_PAPER_SESSION" in markdown


def test_evaluate_human_validated_session_accepts_mapping_input_and_upstream_results():
    result = evaluate_human_validated_paper_session(
        {
            "controlled_paper_run": _upstream(state="READY_FOR_HUMAN_VALIDATED_SESSION"),
            "paper_execution_loop_readiness": _upstream(state="READY_FOR_CONTROLLED_PAPER_RUN"),
            "paper_runtime_preparation": _upstream(state="READY_FOR_PAPER_EXECUTION_LOOP"),
            "observability_verification": _upstream(state="READY_FOR_PAPER_RUNTIME_PREP"),
            "rollback_verification": _upstream(state="READY_FOR_OBSERVABILITY_VERIFICATION"),
            "kill_switch_verification": _upstream(state="READY_FOR_ROLLBACK_VERIFICATION"),
            "runtime_isolation_review": _upstream(state="READY_FOR_PAPER_RUNTIME"),
            "sandbox_readiness_audit": _upstream(state="SANDBOX_READY"),
            "stable_review": _upstream(state="STABLE"),
            "assigned_operator_present": True,
            "explicit_approval_required": True,
            "explicit_approval_captured": True,
            "approval_timestamp_recorded": True,
            "session_scope_confirmed": True,
            "operator_identity_verified": True,
            "confirmation_challenge_completed": True,
            "risk_acknowledgement_recorded": True,
            "dry_run_acknowledged": True,
            "human_override_available": True,
            "session_id_assigned": True,
            "session_limits_authorized": True,
            "paper_only_authorized": True,
            "autonomy_disabled": True,
            "validation_bypass_blocked": True,
            "audit_trail_enabled": True,
            "decision_trace_enabled": True,
            "operator_actions_logged": True,
            "session_events_exportable": True,
            "observability_linked": True,
            "rollback_plan_attached": True,
            "kill_switch_attached": True,
            "recovery_checkpoint_available": True,
            "reversal_drill_recorded": True,
            "session_drift_monitoring_enabled": True,
            "ready_for_supervised_paper_session": True,
        }
    )

    assert result.state is HumanValidatedPaperSessionState.READY_FOR_SUPERVISED_PAPER_SESSION
    assert result.risks == ()


@pytest.mark.parametrize(
    ("risk", "expected"),
    [
        (
            HumanValidationRisk.HUMAN_OVERRIDE_UNAVAILABLE,
            HumanValidationRecommendation.ENABLE_HUMAN_OVERRIDE,
        ),
        (
            HumanValidationRisk.VALIDATION_BYPASS_RISK,
            HumanValidationRecommendation.BLOCK_VALIDATION_BYPASS,
        ),
    ],
)
def test_recommendation_mapping_for_override_and_bypass_risks(risk, expected):
    result = evaluate_human_validated_paper_session(_ready_input())

    assert expected in generate_human_validation_recommendations((risk,), result.state)
