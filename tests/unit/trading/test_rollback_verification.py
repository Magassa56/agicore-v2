from types import SimpleNamespace

import pytest

from agicore.trading.rollback_verification import (
    compute_rollback_score,
    detect_rollback_risks,
    evaluate_rollback,
    generate_rollback_recommendations,
    render_rollback_markdown,
    verify_execution_rollback,
    verify_memory_restore,
    verify_recovery_point,
    verify_runtime_restore,
    verify_state_snapshot,
)
from agicore.trading.rollback_verification_models import (
    RollbackRecommendation,
    RollbackRisk,
    RollbackState,
    RollbackVerificationInput,
)


def _kill_switch_verification(**overrides):
    data = {
        "state": "READY_FOR_ROLLBACK_VERIFICATION",
        "kill_switch_score": 96,
        "risks": (),
        "score_breakdown": SimpleNamespace(
            execution_stop_score=96,
            recovery_safety_score=96,
        ),
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
        "kill_switch_verification": _kill_switch_verification(),
        "runtime_isolation_review": _runtime_isolation_review(),
        "sandbox_readiness_audit": _sandbox_audit(),
        "stable_review": _review_result(),
        "freeze_candidate_review": _review_result(state="READY_FOR_SANDBOX"),
        "snapshot_available": True,
        "snapshot_integrity_valid": True,
        "snapshot_recent": True,
        "snapshot_isolated": True,
        "recovery_point_available": True,
        "recovery_point_valid": True,
        "recovery_point_compatible": True,
        "recovery_path_available": True,
        "runtime_restore_tested": True,
        "runtime_restore_deterministic": True,
        "runtime_state_clean": True,
        "unsafe_restart_blocked": True,
        "memory_restore_tested": True,
        "memory_namespace_restored": True,
        "memory_checksum_valid": True,
        "memory_contamination_absent": True,
        "execution_rollback_tested": True,
        "simulated_orders_reverted": True,
        "broker_state_unchanged": True,
        "execution_queue_restored": True,
        "post_rollback_state_valid": True,
        "partial_rollback_detected": False,
        "rollback_observable": True,
        "rollback_audit_logged": True,
        "ready_for_observability_verification": True,
        "state_snapshot_score": 96,
        "recovery_point_score": 96,
        "runtime_restore_score": 96,
        "memory_restore_score": 96,
        "execution_rollback_score": 96,
        "rollback_safety_score": 96,
        "observability_score": 96,
    }
    data.update(overrides)
    return RollbackVerificationInput(**data)


def test_evaluate_rollback_ready_for_observability_when_all_paths_are_verified():
    result = evaluate_rollback(_ready_input())

    assert result.state is RollbackState.READY_FOR_OBSERVABILITY_VERIFICATION
    assert result.risks == ()
    assert result.rollback_score >= 94
    assert result.offline_only is True
    assert result.rollback_graph.restore_edges == (
        ("recovery_point", "runtime_restore"),
        ("recovery_point", "memory_restore"),
        ("recovery_point", "execution_rollback"),
    )
    assert result.state_snapshot_review.passed is True
    assert result.recovery_point_review.passed is True
    assert result.runtime_restore_review.passed is True
    assert result.memory_restore_review.passed is True
    assert result.execution_rollback_review.passed is True


def test_detect_rollback_risks_reports_all_failures():
    data = _ready_input(
        snapshot_available=False,
        snapshot_integrity_valid=False,
        snapshot_recent=False,
        snapshot_isolated=False,
        recovery_point_available=False,
        recovery_point_valid=False,
        recovery_point_compatible=False,
        recovery_path_available=False,
        runtime_restore_tested=False,
        runtime_restore_deterministic=False,
        runtime_state_clean=False,
        unsafe_restart_blocked=False,
        memory_restore_tested=False,
        memory_namespace_restored=False,
        memory_checksum_valid=False,
        memory_contamination_absent=False,
        execution_rollback_tested=False,
        simulated_orders_reverted=False,
        broker_state_unchanged=False,
        execution_queue_restored=False,
        post_rollback_state_valid=False,
        partial_rollback_detected=True,
        rollback_observable=False,
        rollback_audit_logged=False,
        state_snapshot_score=10,
        recovery_point_score=10,
        runtime_restore_score=10,
        memory_restore_score=10,
        execution_rollback_score=10,
        rollback_safety_score=10,
        observability_score=10,
    )

    risks = detect_rollback_risks(data)

    assert set(risks) == set(RollbackRisk)


def test_missing_snapshot_forces_not_verified():
    result = evaluate_rollback(
        _ready_input(snapshot_available=False, snapshot_isolated=False)
    )

    assert result.state is RollbackState.NOT_VERIFIED
    assert RollbackRisk.SNAPSHOT_MISSING in result.risks
    assert result.rollback_graph.failed_edges == (("error_event", "state_snapshot"),)


def test_execution_rollback_failure_forces_not_verified_and_offline_false():
    result = evaluate_rollback(
        _ready_input(execution_rollback_tested=False, broker_state_unchanged=False)
    )

    assert result.state is RollbackState.NOT_VERIFIED
    assert result.offline_only is False
    assert RollbackRisk.EXECUTION_ROLLBACK_FAILURE in result.risks


def test_three_soft_risks_require_review_without_hard_failure():
    result = evaluate_rollback(
        _ready_input(
            unsafe_restart_blocked=False,
            partial_rollback_detected=True,
            rollback_observable=False,
        )
    )

    assert result.state is RollbackState.REVIEW_REQUIRED
    assert {
        RollbackRisk.UNSAFE_RESTART_RISK,
        RollbackRisk.PARTIAL_ROLLBACK_RISK,
        RollbackRisk.ROLLBACK_OBSERVABILITY_GAP,
    }.issubset(result.risks)


def test_single_soft_risk_yields_partially_verified():
    result = evaluate_rollback(_ready_input(partial_rollback_detected=True))

    assert result.state is RollbackState.PARTIALLY_VERIFIED
    assert result.risks == (RollbackRisk.PARTIAL_ROLLBACK_RISK,)


def test_verified_state_when_clean_but_observability_gate_not_ready():
    result = evaluate_rollback(
        _ready_input(
            ready_for_observability_verification=False,
            state_snapshot_score=89,
            recovery_point_score=89,
            runtime_restore_score=89,
            memory_restore_score=89,
            execution_rollback_score=89,
            rollback_safety_score=89,
            observability_score=89,
        )
    )

    assert result.state is RollbackState.VERIFIED
    assert result.risks == ()
    assert result.rollback_score >= 88


def test_review_sections_expose_specific_rollback_risks():
    data = _ready_input(
        snapshot_available=False,
        recovery_point_valid=False,
        runtime_restore_tested=False,
        memory_restore_tested=False,
        execution_queue_restored=False,
    )

    assert RollbackRisk.SNAPSHOT_MISSING in verify_state_snapshot(data).risks
    assert RollbackRisk.RECOVERY_POINT_INVALID in verify_recovery_point(data).risks
    assert RollbackRisk.RUNTIME_RESTORE_FAILURE in verify_runtime_restore(data).risks
    assert RollbackRisk.MEMORY_RESTORE_FAILURE in verify_memory_restore(data).risks
    assert RollbackRisk.EXECUTION_ROLLBACK_FAILURE in verify_execution_rollback(data).risks


def test_compute_rollback_score_caps_hard_failures():
    data = _ready_input(snapshot_available=False, execution_rollback_tested=False)
    sections = (
        verify_state_snapshot(data),
        verify_recovery_point(data),
        verify_runtime_restore(data),
        verify_memory_restore(data),
        verify_execution_rollback(data),
    )
    risks = (
        RollbackRisk.SNAPSHOT_MISSING,
        RollbackRisk.EXECUTION_ROLLBACK_FAILURE,
    )

    score = compute_rollback_score(data, risks, *sections)

    assert score.overall_score <= 45


def test_generate_recommendations_are_deduplicated_and_risk_driven():
    result = evaluate_rollback(
        _ready_input(
            snapshot_available=False,
            recovery_point_valid=False,
            rollback_observable=False,
        )
    )

    recommendations = generate_rollback_recommendations(result.risks, result.state)

    assert RollbackRecommendation.CREATE_SAFE_STATE_SNAPSHOT in recommendations
    assert RollbackRecommendation.REPAIR_RECOVERY_POINT in recommendations
    assert RollbackRecommendation.ADD_ROLLBACK_OBSERVABILITY in recommendations
    assert len(recommendations) == len(set(recommendations))


def test_markdown_contains_rollback_report_sections():
    result = evaluate_rollback(_ready_input())

    markdown = render_rollback_markdown(result)

    assert "# AGIcore Rollback Verification" in markdown
    assert "# Rollback Graph" in markdown
    assert "# Rollback Risks" in markdown
    assert "READY_FOR_OBSERVABILITY_VERIFICATION" in markdown


def test_evaluate_rollback_accepts_mapping_input_and_compatible_upstream_results():
    result = evaluate_rollback(
        {
            "kill_switch_verification": _kill_switch_verification(),
            "runtime_isolation_review": _runtime_isolation_review(),
            "sandbox_readiness_audit": _sandbox_audit(),
            "stable_review": _review_result(),
            "freeze_candidate_review": _review_result(state="READY_FOR_SANDBOX"),
            "snapshot_available": True,
            "snapshot_integrity_valid": True,
            "snapshot_recent": True,
            "snapshot_isolated": True,
            "recovery_point_available": True,
            "recovery_point_valid": True,
            "recovery_point_compatible": True,
            "recovery_path_available": True,
            "runtime_restore_tested": True,
            "runtime_restore_deterministic": True,
            "runtime_state_clean": True,
            "unsafe_restart_blocked": True,
            "memory_restore_tested": True,
            "memory_namespace_restored": True,
            "memory_checksum_valid": True,
            "memory_contamination_absent": True,
            "execution_rollback_tested": True,
            "simulated_orders_reverted": True,
            "broker_state_unchanged": True,
            "execution_queue_restored": True,
            "post_rollback_state_valid": True,
            "partial_rollback_detected": False,
            "rollback_observable": True,
            "rollback_audit_logged": True,
            "ready_for_observability_verification": True,
        }
    )

    assert result.state is RollbackState.READY_FOR_OBSERVABILITY_VERIFICATION
    assert result.risks == ()


@pytest.mark.parametrize(
    ("risk", "expected"),
    [
        (
            RollbackRisk.UNSAFE_RESTART_RISK,
            RollbackRecommendation.BLOCK_UNSAFE_RESTART,
        ),
        (
            RollbackRisk.RECOVERY_PATH_MISSING,
            RollbackRecommendation.RESTORE_RECOVERY_PATH,
        ),
    ],
)
def test_recommendation_mapping_for_restart_and_recovery_path_risks(risk, expected):
    result = evaluate_rollback(_ready_input())

    assert expected in generate_rollback_recommendations((risk,), result.state)
