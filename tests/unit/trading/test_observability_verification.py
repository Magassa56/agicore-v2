from types import SimpleNamespace

import pytest

from agicore.trading.observability_verification import (
    compute_observability_score,
    detect_observability_risks,
    evaluate_observability,
    generate_observability_recommendations,
    render_observability_markdown,
    verify_alerting_readiness,
    verify_audit_trail_integrity,
    verify_logging_visibility,
    verify_metrics_visibility,
    verify_trace_visibility,
)
from agicore.trading.observability_verification_models import (
    ObservabilityRecommendation,
    ObservabilityRisk,
    ObservabilityState,
    ObservabilityVerificationInput,
)


def _rollback_verification(**overrides):
    data = {
        "state": "READY_FOR_OBSERVABILITY_VERIFICATION",
        "rollback_score": 96,
        "risks": (),
        "score_breakdown": SimpleNamespace(observability_score=96),
        "offline_only": True,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def _kill_switch_verification(**overrides):
    data = {
        "state": "READY_FOR_ROLLBACK_VERIFICATION",
        "kill_switch_score": 96,
        "risks": (),
        "offline_only": True,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def _runtime_isolation_review(**overrides):
    data = {
        "state": "READY_FOR_PAPER_RUNTIME",
        "isolation_score": 96,
        "risks": (),
        "offline_only": True,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def _sandbox_audit(**overrides):
    data = {
        "state": "SANDBOX_READY",
        "sandbox_score": 96,
        "blockers": (),
        "score_breakdown": SimpleNamespace(observability_score=96),
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def _review_result(state="STABLE", score=96, blockers=(), risks=()):
    return SimpleNamespace(
        state=state,
        score=score,
        stable_score=score,
        freeze_candidate_score=score,
        blockers=blockers,
        risks=risks,
    )


def _ready_input(**overrides):
    data = {
        "rollback_verification": _rollback_verification(),
        "kill_switch_verification": _kill_switch_verification(),
        "runtime_isolation_review": _runtime_isolation_review(),
        "sandbox_readiness_audit": _sandbox_audit(),
        "stable_review": _review_result(),
        "freeze_candidate_review": _review_result(state="READY_FOR_SANDBOX"),
        "structured_logging_enabled": True,
        "log_levels_configured": True,
        "critical_events_logged": True,
        "log_correlation_ids_present": True,
        "runtime_metrics_enabled": True,
        "safety_metrics_enabled": True,
        "latency_metrics_enabled": True,
        "metric_labels_stable": True,
        "tracing_enabled": True,
        "trace_context_propagated": True,
        "runtime_spans_recorded": True,
        "failure_spans_recorded": True,
        "alerting_configured": True,
        "critical_alert_rules_present": True,
        "alert_deduplication_enabled": True,
        "alert_targets_offline_safe": True,
        "audit_trail_enabled": True,
        "audit_events_immutable": True,
        "safety_decisions_audited": True,
        "paper_runtime_events_visible": True,
        "runtime_state_visible": True,
        "failure_modes_visible": True,
        "observability_schema_stable": True,
        "ready_for_paper_runtime_prep": True,
        "logging_score": 96,
        "metrics_score": 96,
        "trace_score": 96,
        "alerting_score": 96,
        "audit_trail_score": 96,
        "runtime_visibility_score": 96,
    }
    data.update(overrides)
    return ObservabilityVerificationInput(**data)


def test_evaluate_observability_ready_for_paper_runtime_prep_when_all_visible():
    result = evaluate_observability(_ready_input())

    assert result.state is ObservabilityState.READY_FOR_PAPER_RUNTIME_PREP
    assert result.risks == ()
    assert result.observability_score >= 94
    assert result.offline_only is True
    assert result.observability_graph.visible_edges == (
        ("agicore_runtime", "logs"),
        ("agicore_runtime", "metrics"),
        ("agicore_runtime", "traces"),
        ("logs", "alerts"),
        ("agicore_runtime", "audit_trail"),
    )
    assert result.logging_visibility_review.passed is True
    assert result.metrics_visibility_review.passed is True
    assert result.trace_visibility_review.passed is True
    assert result.alerting_readiness_review.passed is True
    assert result.audit_trail_integrity_review.passed is True


def test_detect_observability_risks_reports_all_visibility_failures():
    data = _ready_input(
        structured_logging_enabled=False,
        log_levels_configured=False,
        critical_events_logged=False,
        log_correlation_ids_present=False,
        runtime_metrics_enabled=False,
        safety_metrics_enabled=False,
        latency_metrics_enabled=False,
        metric_labels_stable=False,
        tracing_enabled=False,
        trace_context_propagated=False,
        runtime_spans_recorded=False,
        failure_spans_recorded=False,
        alerting_configured=False,
        critical_alert_rules_present=False,
        alert_deduplication_enabled=False,
        alert_targets_offline_safe=False,
        audit_trail_enabled=False,
        audit_events_immutable=False,
        safety_decisions_audited=False,
        paper_runtime_events_visible=False,
        runtime_state_visible=False,
        failure_modes_visible=False,
        observability_schema_stable=False,
        logging_score=10,
        metrics_score=10,
        trace_score=10,
        alerting_score=10,
        audit_trail_score=10,
        runtime_visibility_score=10,
    )

    risks = detect_observability_risks(data)

    assert set(risks) == set(ObservabilityRisk)


def test_logging_gap_forces_not_observable():
    result = evaluate_observability(
        _ready_input(structured_logging_enabled=False, log_correlation_ids_present=False)
    )

    assert result.state is ObservabilityState.NOT_OBSERVABLE
    assert ObservabilityRisk.LOGGING_GAP in result.risks
    assert result.observability_graph.blind_edges == (("agicore_runtime", "logs"),)


def test_paper_runtime_blind_spot_forces_not_observable_and_offline_false():
    result = evaluate_observability(
        _ready_input(
            paper_runtime_events_visible=False,
            alert_targets_offline_safe=False,
        )
    )

    assert result.state is ObservabilityState.NOT_OBSERVABLE
    assert result.offline_only is False
    assert ObservabilityRisk.PAPER_RUNTIME_BLIND_SPOT in result.risks


def test_three_soft_risks_require_review_without_hard_failure():
    result = evaluate_observability(
        _ready_input(
            runtime_metrics_enabled=False,
            tracing_enabled=False,
            alerting_configured=False,
        )
    )

    assert result.state is ObservabilityState.REVIEW_REQUIRED
    assert {
        ObservabilityRisk.METRICS_GAP,
        ObservabilityRisk.TRACE_GAP,
        ObservabilityRisk.ALERTING_GAP,
    }.issubset(result.risks)


def test_single_soft_risk_yields_partially_observable():
    result = evaluate_observability(_ready_input(metric_labels_stable=False))

    assert result.state is ObservabilityState.PARTIALLY_OBSERVABLE
    assert result.risks == (ObservabilityRisk.OBSERVABILITY_DRIFT,)


def test_observable_state_when_clean_but_paper_runtime_prep_gate_not_ready():
    result = evaluate_observability(
        _ready_input(
            ready_for_paper_runtime_prep=False,
            logging_score=89,
            metrics_score=89,
            trace_score=89,
            alerting_score=89,
            audit_trail_score=89,
            runtime_visibility_score=89,
        )
    )

    assert result.state is ObservabilityState.OBSERVABLE
    assert result.risks == ()
    assert result.observability_score >= 88


def test_review_sections_expose_specific_observability_risks():
    data = _ready_input(
        critical_events_logged=False,
        runtime_metrics_enabled=False,
        failure_spans_recorded=False,
        alerting_configured=False,
        audit_trail_enabled=False,
        runtime_state_visible=False,
    )

    assert ObservabilityRisk.CRITICAL_EVENT_INVISIBLE in verify_logging_visibility(data).risks
    assert ObservabilityRisk.METRICS_GAP in verify_metrics_visibility(data).risks
    assert ObservabilityRisk.FAILURE_MODE_UNOBSERVED in verify_trace_visibility(data).risks
    assert ObservabilityRisk.ALERTING_GAP in verify_alerting_readiness(data).risks
    assert ObservabilityRisk.AUDIT_TRAIL_INCOMPLETE in verify_audit_trail_integrity(data).risks
    assert ObservabilityRisk.RUNTIME_STATE_OPAQUE in verify_audit_trail_integrity(data).risks


def test_compute_observability_score_caps_hard_blind_spots():
    data = _ready_input(critical_events_logged=False, runtime_state_visible=False)
    sections = (
        verify_logging_visibility(data),
        verify_metrics_visibility(data),
        verify_trace_visibility(data),
        verify_alerting_readiness(data),
        verify_audit_trail_integrity(data),
    )
    risks = (
        ObservabilityRisk.CRITICAL_EVENT_INVISIBLE,
        ObservabilityRisk.RUNTIME_STATE_OPAQUE,
    )

    score = compute_observability_score(data, risks, *sections)

    assert score.overall_score <= 45


def test_generate_recommendations_are_deduplicated_and_risk_driven():
    result = evaluate_observability(
        _ready_input(
            structured_logging_enabled=False,
            alerting_configured=False,
            observability_schema_stable=False,
        )
    )

    recommendations = generate_observability_recommendations(result.risks, result.state)

    assert ObservabilityRecommendation.ADD_STRUCTURED_RUNTIME_LOGGING in recommendations
    assert ObservabilityRecommendation.ADD_ALERTING_RULES in recommendations
    assert ObservabilityRecommendation.STABILIZE_OBSERVABILITY_SCHEMA in recommendations
    assert len(recommendations) == len(set(recommendations))


def test_markdown_contains_observability_report_sections():
    result = evaluate_observability(_ready_input())

    markdown = render_observability_markdown(result)

    assert "# AGIcore Observability Verification" in markdown
    assert "# Observability Graph" in markdown
    assert "# Observability Risks" in markdown
    assert "READY_FOR_PAPER_RUNTIME_PREP" in markdown


def test_evaluate_observability_accepts_mapping_input_and_compatible_upstream_results():
    result = evaluate_observability(
        {
            "rollback_verification": _rollback_verification(),
            "kill_switch_verification": _kill_switch_verification(),
            "runtime_isolation_review": _runtime_isolation_review(),
            "sandbox_readiness_audit": _sandbox_audit(),
            "stable_review": _review_result(),
            "freeze_candidate_review": _review_result(state="READY_FOR_SANDBOX"),
            "structured_logging_enabled": True,
            "log_levels_configured": True,
            "critical_events_logged": True,
            "log_correlation_ids_present": True,
            "runtime_metrics_enabled": True,
            "safety_metrics_enabled": True,
            "latency_metrics_enabled": True,
            "metric_labels_stable": True,
            "tracing_enabled": True,
            "trace_context_propagated": True,
            "runtime_spans_recorded": True,
            "failure_spans_recorded": True,
            "alerting_configured": True,
            "critical_alert_rules_present": True,
            "alert_deduplication_enabled": True,
            "alert_targets_offline_safe": True,
            "audit_trail_enabled": True,
            "audit_events_immutable": True,
            "safety_decisions_audited": True,
            "paper_runtime_events_visible": True,
            "runtime_state_visible": True,
            "failure_modes_visible": True,
            "observability_schema_stable": True,
            "ready_for_paper_runtime_prep": True,
        }
    )

    assert result.state is ObservabilityState.READY_FOR_PAPER_RUNTIME_PREP
    assert result.risks == ()


@pytest.mark.parametrize(
    ("risk", "expected"),
    [
        (
            ObservabilityRisk.AUDIT_TRAIL_INCOMPLETE,
            ObservabilityRecommendation.COMPLETE_AUDIT_TRAIL,
        ),
        (
            ObservabilityRisk.PAPER_RUNTIME_BLIND_SPOT,
            ObservabilityRecommendation.REMOVE_PAPER_RUNTIME_BLIND_SPOTS,
        ),
    ],
)
def test_recommendation_mapping_for_audit_and_paper_runtime_risks(risk, expected):
    result = evaluate_observability(_ready_input())

    assert expected in generate_observability_recommendations((risk,), result.state)
