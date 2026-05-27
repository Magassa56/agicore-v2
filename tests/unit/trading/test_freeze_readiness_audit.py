from types import SimpleNamespace

from agicore.trading.freeze_readiness_audit import (
    build_runtime_readiness_matrix,
    build_system_stability_snapshot,
    compute_freeze_readiness_score,
    detect_freeze_blockers,
    evaluate_freeze_readiness,
    generate_freeze_recommendations,
    render_freeze_readiness_markdown,
)
from agicore.trading.freeze_readiness_audit_models import (
    FreezeBlockerRisk,
    FreezeReadinessInput,
    FreezeReadinessState,
    FreezeRecommendation,
)


def ns(**kwargs):
    return SimpleNamespace(**kwargs)


def stable_input():
    return FreezeReadinessInput(
        tests_green=True,
        unit_test_pass_rate=1.0,
        flaky_test_count=0,
        test_failure_count=0,
        engine_count=12,
        fragmented_engine_count=0,
        conflicting_engine_count=0,
        orchestrator_registered=True,
        orchestrator_route_count=8,
        runtime_observable=True,
        log_json_enabled=True,
        metrics_available=True,
        replay_deterministic=True,
        replay_uses_sandbox_data=True,
        replay_has_no_real_orders=True,
        kill_switch_configured=True,
        rollback_plan_available=True,
        rollback_tested=True,
        memory_state_consistent=True,
        memory_reconciliation_score=96,
        execution_sandboxed=True,
        broker_connection_disabled=True,
        external_api_disabled=True,
        live_execution_disabled=True,
        paper_trading_loop_ready=True,
        paper_adapter_ready=True,
        sandbox_ready=True,
        global_stability_score=94,
        safety_score=96,
        orchestration_score=95,
        observability_score=94,
        replay_safety_score=96,
        paper_readiness_score=95,
        cognitive_consensus=ns(state="CONSENSUS_REACHED", cognitive_consensus_score=94, risks=()),
        cognitive_coherence=ns(state="COHERENT", cognitive_coherence_score=93, risks=()),
        adaptive_memory=ns(adaptive_memory_score=95, risks=()),
        cognitive_memory_consolidation=ns(memory_consolidation_score=94, risks=()),
        notes=("offline audit fixture",),
    )


def test_evaluate_freeze_readiness_ready_to_try_when_all_guards_green():
    result = evaluate_freeze_readiness(stable_input())

    assert result.state == FreezeReadinessState.READY_TO_TRY
    assert result.freeze_readiness_score >= 92
    assert result.blockers == ()
    assert result.runtime_matrix.ready is True
    assert result.offline_only is True


def test_detects_all_required_freeze_blockers():
    data = FreezeReadinessInput(
        tests_green=False,
        unit_test_pass_rate=0.72,
        flaky_test_count=2,
        test_failure_count=3,
        fragmented_engine_count=2,
        conflicting_engine_count=1,
        orchestrator_registered=False,
        orchestrator_route_count=0,
        runtime_observable=False,
        log_json_enabled=False,
        metrics_available=False,
        replay_deterministic=False,
        replay_uses_sandbox_data=False,
        replay_has_no_real_orders=False,
        kill_switch_configured=False,
        rollback_plan_available=False,
        rollback_tested=False,
        memory_state_consistent=False,
        memory_reconciliation_score=30,
        execution_sandboxed=False,
        broker_connection_disabled=False,
        external_api_disabled=False,
        live_execution_disabled=False,
        paper_trading_loop_ready=False,
        paper_adapter_ready=False,
        sandbox_ready=False,
        cognitive_consensus=ns(state="CONSENSUS_FRAGMENTED", cognitive_consensus_score=35, risks=("CONFLICT",)),
    )

    blockers = detect_freeze_blockers(data)

    assert blockers == (
        FreezeBlockerRisk.TEST_INSTABILITY,
        FreezeBlockerRisk.ENGINE_FRAGMENTATION,
        FreezeBlockerRisk.ORCHESTRATION_GAP,
        FreezeBlockerRisk.RUNTIME_UNOBSERVABLE,
        FreezeBlockerRisk.REPLAY_UNSAFE,
        FreezeBlockerRisk.KILL_SWITCH_MISSING,
        FreezeBlockerRisk.ROLLBACK_UNAVAILABLE,
        FreezeBlockerRisk.MEMORY_INCONSISTENCY,
        FreezeBlockerRisk.EXECUTION_UNSAFE,
        FreezeBlockerRisk.PAPER_RUNTIME_NOT_READY,
    )


def test_execution_unsafe_forces_not_ready_and_offline_false():
    data = stable_input().__class__(
        **{
            **stable_input().__dict__,
            "execution_sandboxed": False,
            "broker_connection_disabled": False,
            "external_api_disabled": False,
            "live_execution_disabled": False,
        }
    )

    result = evaluate_freeze_readiness(data)

    assert FreezeBlockerRisk.EXECUTION_UNSAFE in result.blockers
    assert result.state == FreezeReadinessState.NOT_READY
    assert result.offline_only is False


def test_partial_readiness_when_multiple_non_execution_blockers_exist():
    data = stable_input().__class__(
        **{
            **stable_input().__dict__,
            "tests_green": False,
            "unit_test_pass_rate": 0.88,
            "kill_switch_configured": False,
            "rollback_plan_available": False,
            "rollback_tested": False,
        }
    )

    result = evaluate_freeze_readiness(data)

    assert result.state == FreezeReadinessState.PARTIALLY_READY
    assert FreezeBlockerRisk.TEST_INSTABILITY in result.blockers
    assert FreezeBlockerRisk.KILL_SWITCH_MISSING in result.blockers
    assert FreezeBlockerRisk.ROLLBACK_UNAVAILABLE in result.blockers


def test_freeze_candidate_when_single_runtime_blocker_remains():
    data = stable_input().__class__(
        **{
            **stable_input().__dict__,
            "paper_trading_loop_ready": False,
        }
    )

    result = evaluate_freeze_readiness(data)

    assert result.state == FreezeReadinessState.FREEZE_CANDIDATE
    assert result.blockers == (FreezeBlockerRisk.PAPER_RUNTIME_NOT_READY,)


def test_build_system_stability_snapshot_uses_layer_scores():
    data = FreezeReadinessInput(
        tests_green=True,
        unit_test_pass_rate=1.0,
        cognitive_stability=ns(cognitive_stability_score=88),
        system_integrity=ns(system_integrity_score=92),
        cognitive_consensus=ns(cognitive_consensus_score=84, risks=()),
        cognitive_coherence=ns(cognitive_coherence_score=86, risks=()),
        execution_sandboxed=True,
        broker_connection_disabled=True,
        external_api_disabled=True,
        live_execution_disabled=True,
        sandbox_ready=True,
    )

    snapshot = build_system_stability_snapshot(data)

    assert snapshot.global_stability_score == 90
    assert snapshot.engine_conflict_score >= 80
    assert snapshot.sandbox_score == 100


def test_runtime_readiness_matrix_maps_blockers_to_rows():
    data = stable_input().__class__(
        **{
            **stable_input().__dict__,
            "runtime_observable": False,
            "log_json_enabled": False,
        }
    )
    snapshot = build_system_stability_snapshot(data)
    blockers = detect_freeze_blockers(data, snapshot)

    matrix = build_runtime_readiness_matrix(data, blockers, snapshot)

    observability = next(row for row in matrix.rows if row.area == "observability")
    assert observability.ready is False
    assert observability.blockers == (FreezeBlockerRisk.RUNTIME_UNOBSERVABLE,)


def test_score_penalizes_blockers():
    stable_snapshot = build_system_stability_snapshot(stable_input())
    stable_score = compute_freeze_readiness_score(stable_input(), (), stable_snapshot)
    blockers = (FreezeBlockerRisk.TEST_INSTABILITY, FreezeBlockerRisk.REPLAY_UNSAFE)
    degraded_score = compute_freeze_readiness_score(stable_input(), blockers, stable_snapshot)

    assert degraded_score.overall_score < stable_score.overall_score
    assert degraded_score.overall_score <= 70


def test_recommendations_cover_blockers_and_review_gate():
    recommendations = generate_freeze_recommendations(
        (
            FreezeBlockerRisk.TEST_INSTABILITY,
            FreezeBlockerRisk.KILL_SWITCH_MISSING,
        ),
        FreezeReadinessState.PARTIALLY_READY,
    )

    assert FreezeRecommendation.KEEP_SYSTEM_FROZEN in recommendations
    assert FreezeRecommendation.FIX_TEST_INSTABILITY in recommendations
    assert FreezeRecommendation.CONFIGURE_KILL_SWITCH in recommendations
    assert FreezeRecommendation.RUN_FREEZE_REGRESSION_SUITE in recommendations


def test_markdown_contains_required_sections_and_blockers():
    result = evaluate_freeze_readiness(
        stable_input().__class__(
            **{
                **stable_input().__dict__,
                "kill_switch_configured": False,
            }
        )
    )

    markdown = render_freeze_readiness_markdown(result)

    assert "# AGIcore Freeze Readiness Audit" in markdown
    assert "# Stability Snapshot" in markdown
    assert "# Runtime Readiness Matrix" in markdown
    assert "# Freeze Blockers" in markdown
    assert "# Recommendations" in markdown
    assert "# Evidence" in markdown
    assert "KILL_SWITCH_MISSING" in markdown
