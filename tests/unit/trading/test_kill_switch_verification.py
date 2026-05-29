from types import SimpleNamespace

import pytest

from agicore.trading.kill_switch_verification import (
    compute_kill_switch_score,
    detect_kill_switch_risks,
    evaluate_kill_switch,
    generate_kill_switch_recommendations,
    render_kill_switch_markdown,
    verify_cognitive_stop,
    verify_emergency_lockdown,
    verify_execution_stop,
    verify_runtime_halt,
    verify_shutdown_path,
)
from agicore.trading.kill_switch_verification_models import (
    KillSwitchRecommendation,
    KillSwitchRisk,
    KillSwitchState,
    KillSwitchVerificationInput,
)


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
        "score_breakdown": SimpleNamespace(kill_switch_score=96),
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def _review_result(state="STABLE", score=96, blockers=(), risks=()):
    return SimpleNamespace(
        state=state,
        score=score,
        stable_score=score,
        freeze_candidate_score=score,
        readiness_score=score,
        blockers=blockers,
        risks=risks,
    )


def _ready_input(**overrides):
    data = {
        "runtime_isolation_review": _runtime_isolation_review(),
        "sandbox_readiness_audit": _sandbox_audit(),
        "stable_review": _review_result(),
        "freeze_candidate_review": _review_result(state="READY_FOR_SANDBOX"),
        "freeze_readiness_audit": _review_result(state="READY_TO_TRY"),
        "kill_switch_present": True,
        "kill_signal_registered": True,
        "shutdown_path_tested": True,
        "shutdown_idempotent": True,
        "shutdown_latency_ms": 100,
        "max_shutdown_latency_ms": 500,
        "execution_stop_signal_propagates": True,
        "simulated_orders_cancelled": True,
        "broker_path_blocked": True,
        "execution_queue_drained": True,
        "cognitive_stop_signal_propagates": True,
        "cognitive_loops_drained": True,
        "recursive_tasks_cancelled": True,
        "new_cognitive_tasks_blocked": True,
        "runtime_halt_signal_propagates": True,
        "schedulers_stopped": True,
        "event_bus_quiesced": True,
        "background_workers_stopped": True,
        "emergency_lockdown_available": True,
        "safety_overrides_blocked": True,
        "lockdown_idempotent": True,
        "lockdown_audit_logged": True,
        "state_snapshot_persisted": True,
        "recovery_checkpoint_valid": True,
        "rollback_path_available": True,
        "ready_for_rollback_verification": True,
        "shutdown_path_score": 96,
        "execution_stop_score": 96,
        "cognitive_stop_score": 96,
        "runtime_halt_score": 96,
        "emergency_lockdown_score": 96,
        "recovery_safety_score": 96,
    }
    data.update(overrides)
    return KillSwitchVerificationInput(**data)


def test_evaluate_kill_switch_ready_for_rollback_when_all_paths_are_verified():
    result = evaluate_kill_switch(_ready_input())

    assert result.state is KillSwitchState.READY_FOR_ROLLBACK_VERIFICATION
    assert result.risks == ()
    assert result.kill_switch_score >= 94
    assert result.offline_only is True
    assert result.kill_switch_graph.stop_edges == (
        ("shutdown_path", "execution_stop"),
        ("shutdown_path", "cognitive_stop"),
        ("shutdown_path", "runtime_halt"),
    )
    assert result.shutdown_path_review.passed is True
    assert result.execution_stop_review.passed is True
    assert result.cognitive_stop_review.passed is True
    assert result.runtime_halt_review.passed is True
    assert result.emergency_lockdown_review.passed is True
    assert result.recovery_safety_review.passed is True


def test_detect_kill_switch_risks_reports_all_failures():
    data = _ready_input(
        kill_switch_present=False,
        kill_signal_registered=False,
        shutdown_path_tested=False,
        shutdown_idempotent=False,
        shutdown_latency_ms=2500,
        execution_stop_signal_propagates=False,
        simulated_orders_cancelled=False,
        broker_path_blocked=False,
        execution_queue_drained=False,
        cognitive_stop_signal_propagates=False,
        cognitive_loops_drained=False,
        recursive_tasks_cancelled=False,
        new_cognitive_tasks_blocked=False,
        runtime_halt_signal_propagates=False,
        schedulers_stopped=False,
        event_bus_quiesced=False,
        background_workers_stopped=False,
        emergency_lockdown_available=False,
        safety_overrides_blocked=False,
        lockdown_idempotent=False,
        lockdown_audit_logged=False,
        state_snapshot_persisted=False,
        recovery_checkpoint_valid=False,
        rollback_path_available=False,
        shutdown_path_score=10,
        execution_stop_score=10,
        cognitive_stop_score=10,
        runtime_halt_score=10,
        emergency_lockdown_score=10,
        recovery_safety_score=10,
    )

    risks = detect_kill_switch_risks(data)

    assert set(risks) == set(KillSwitchRisk)


def test_missing_kill_switch_forces_not_verified():
    result = evaluate_kill_switch(
        _ready_input(kill_switch_present=False, kill_signal_registered=False)
    )

    assert result.state is KillSwitchState.NOT_VERIFIED
    assert KillSwitchRisk.KILL_SWITCH_FAILURE in result.risks
    assert result.kill_switch_graph.failed_edges == (("critical_event", "kill_switch"),)


def test_execution_continuation_forces_not_verified_and_offline_false():
    result = evaluate_kill_switch(
        _ready_input(
            execution_stop_signal_propagates=False,
            broker_path_blocked=False,
        )
    )

    assert result.state is KillSwitchState.NOT_VERIFIED
    assert result.offline_only is False
    assert KillSwitchRisk.EXECUTION_CONTINUATION in result.risks


def test_three_soft_risks_require_review_without_hard_failure():
    result = evaluate_kill_switch(
        _ready_input(
            cognitive_loops_drained=False,
            safety_overrides_blocked=False,
            state_snapshot_persisted=False,
        )
    )

    assert result.state is KillSwitchState.REVIEW_REQUIRED
    assert {
        KillSwitchRisk.COGNITIVE_LOOP_CONTINUATION,
        KillSwitchRisk.SAFETY_OVERRIDE_RISK,
        KillSwitchRisk.STATE_PERSISTENCE_FAILURE,
    }.issubset(result.risks)


def test_single_soft_risk_yields_partially_verified():
    result = evaluate_kill_switch(_ready_input(recovery_checkpoint_valid=False))

    assert result.state is KillSwitchState.PARTIALLY_VERIFIED
    assert result.risks == (KillSwitchRisk.RECOVERY_PATH_CORRUPTION,)


def test_verified_state_when_clean_but_rollback_gate_not_ready():
    result = evaluate_kill_switch(
        _ready_input(
            ready_for_rollback_verification=False,
            shutdown_path_score=89,
            execution_stop_score=89,
            cognitive_stop_score=89,
            runtime_halt_score=89,
            emergency_lockdown_score=89,
            recovery_safety_score=89,
        )
    )

    assert result.state is KillSwitchState.VERIFIED
    assert result.risks == ()
    assert result.kill_switch_score >= 88


def test_review_sections_expose_specific_kill_switch_risks():
    data = _ready_input(
        shutdown_path_tested=False,
        execution_queue_drained=False,
        recursive_tasks_cancelled=False,
        schedulers_stopped=False,
        emergency_lockdown_available=False,
        safety_overrides_blocked=False,
    )

    assert KillSwitchRisk.SHUTDOWN_PATH_FAILURE in verify_shutdown_path(data).risks
    assert KillSwitchRisk.EXECUTION_CONTINUATION in verify_execution_stop(data).risks
    assert KillSwitchRisk.COGNITIVE_LOOP_CONTINUATION in verify_cognitive_stop(data).risks
    assert KillSwitchRisk.RUNTIME_HALT_FAILURE in verify_runtime_halt(data).risks
    assert KillSwitchRisk.LOCKDOWN_FAILURE in verify_emergency_lockdown(data).risks
    assert KillSwitchRisk.SAFETY_OVERRIDE_RISK in verify_emergency_lockdown(data).risks


def test_compute_kill_switch_score_caps_hard_failures():
    data = _ready_input(kill_switch_present=False, runtime_halt_signal_propagates=False)
    sections = (
        verify_shutdown_path(data),
        verify_execution_stop(data),
        verify_cognitive_stop(data),
        verify_runtime_halt(data),
        verify_emergency_lockdown(data),
    )
    risks = (
        KillSwitchRisk.KILL_SWITCH_FAILURE,
        KillSwitchRisk.RUNTIME_HALT_FAILURE,
    )

    score = compute_kill_switch_score(data, risks, *sections)

    assert score.overall_score <= 40


def test_generate_recommendations_are_deduplicated_and_risk_driven():
    result = evaluate_kill_switch(
        _ready_input(
            kill_switch_present=False,
            execution_queue_drained=False,
            safety_overrides_blocked=False,
        )
    )

    recommendations = generate_kill_switch_recommendations(result.risks, result.state)

    assert KillSwitchRecommendation.INSTALL_KILL_SWITCH_GUARD in recommendations
    assert KillSwitchRecommendation.FORCE_EXECUTION_STOP_PROPAGATION in recommendations
    assert KillSwitchRecommendation.BLOCK_SAFETY_OVERRIDES in recommendations
    assert len(recommendations) == len(set(recommendations))


def test_markdown_contains_kill_switch_report_sections():
    result = evaluate_kill_switch(_ready_input())

    markdown = render_kill_switch_markdown(result)

    assert "# AGIcore Kill Switch Verification" in markdown
    assert "# Kill Switch Graph" in markdown
    assert "# Kill Switch Risks" in markdown
    assert "READY_FOR_ROLLBACK_VERIFICATION" in markdown


def test_evaluate_kill_switch_accepts_mapping_input_and_compatible_upstream_results():
    result = evaluate_kill_switch(
        {
            "runtime_isolation_review": _runtime_isolation_review(),
            "sandbox_readiness_audit": _sandbox_audit(),
            "stable_review": _review_result(),
            "freeze_candidate_review": _review_result(state="READY_FOR_SANDBOX"),
            "freeze_readiness_audit": _review_result(state="READY_TO_TRY"),
            "kill_switch_present": True,
            "kill_signal_registered": True,
            "shutdown_path_tested": True,
            "shutdown_idempotent": True,
            "shutdown_latency_ms": 100,
            "execution_stop_signal_propagates": True,
            "simulated_orders_cancelled": True,
            "broker_path_blocked": True,
            "execution_queue_drained": True,
            "cognitive_stop_signal_propagates": True,
            "cognitive_loops_drained": True,
            "recursive_tasks_cancelled": True,
            "new_cognitive_tasks_blocked": True,
            "runtime_halt_signal_propagates": True,
            "schedulers_stopped": True,
            "event_bus_quiesced": True,
            "background_workers_stopped": True,
            "emergency_lockdown_available": True,
            "safety_overrides_blocked": True,
            "lockdown_idempotent": True,
            "lockdown_audit_logged": True,
            "state_snapshot_persisted": True,
            "recovery_checkpoint_valid": True,
            "rollback_path_available": True,
            "ready_for_rollback_verification": True,
        }
    )

    assert result.state is KillSwitchState.READY_FOR_ROLLBACK_VERIFICATION
    assert result.risks == ()


@pytest.mark.parametrize(
    ("risk", "expected"),
    [
        (
            KillSwitchRisk.EMERGENCY_RESPONSE_DELAY,
            KillSwitchRecommendation.REDUCE_EMERGENCY_RESPONSE_LATENCY,
        ),
        (
            KillSwitchRisk.RECOVERY_PATH_CORRUPTION,
            KillSwitchRecommendation.REPAIR_RECOVERY_CHECKPOINT,
        ),
    ],
)
def test_recommendation_mapping_for_latency_and_recovery_risks(risk, expected):
    result = evaluate_kill_switch(_ready_input())

    assert expected in generate_kill_switch_recommendations((risk,), result.state)
