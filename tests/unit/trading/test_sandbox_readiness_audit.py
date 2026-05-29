from dataclasses import replace
from types import SimpleNamespace

from agicore.trading.sandbox_readiness_audit import (
    build_kill_switch_review,
    build_observability_review,
    build_paper_runtime_preparation_review,
    build_rollback_review,
    build_runtime_isolation_review,
    compute_sandbox_score,
    detect_sandbox_blockers,
    evaluate_sandbox_readiness,
    generate_sandbox_recommendations,
    render_sandbox_readiness_markdown,
)
from agicore.trading.sandbox_readiness_audit_models import (
    SandboxBlocker,
    SandboxReadinessInput,
    SandboxReadinessState,
    SandboxRecommendation,
)


def ns(**kwargs):
    return SimpleNamespace(**kwargs)


def stable_review():
    return ns(
        state="READY_FOR_SANDBOX_PREP",
        stable_score=96,
        blockers=(),
        score_breakdown=ns(runtime_score=96, sandbox_score=96, observability_score=96),
        runtime_review=ns(score=96),
        sandbox_review=ns(score=96),
        observability_review=ns(score=96),
        offline_only=True,
    )


def freeze_candidate_review():
    return ns(
        state="READY_FOR_SANDBOX",
        freeze_candidate_score=96,
        blockers=(),
        score_breakdown=ns(observability_score=96, paper_runtime_score=96),
        observability_review=ns(score=96),
        paper_runtime_review=ns(score=96),
        offline_only=True,
    )


def freeze_readiness_audit():
    return ns(
        state="READY_TO_TRY",
        blockers=(),
        snapshot=ns(
            sandbox_score=96,
            rollback_score=96,
            observability_score=96,
            replay_safety_score=96,
            paper_trading_score=96,
        ),
        offline_only=True,
    )


def stable_input():
    return SandboxReadinessInput(
        stable_review=stable_review(),
        freeze_candidate_review=freeze_candidate_review(),
        freeze_readiness_audit=freeze_readiness_audit(),
        live_execution_disabled=True,
        execution_isolated=True,
        broker_disabled=True,
        broker_credentials_absent=True,
        external_api_disabled=True,
        api_credentials_absent=True,
        sandbox_network_isolated=True,
        sandbox_filesystem_isolated=True,
        sandbox_state_clean=True,
        runtime_state_validated=True,
        state_checksum_valid=True,
        memory_persistence_isolated=True,
        memory_snapshot_reversible=True,
        kill_switch_configured=True,
        kill_switch_tested=True,
        rollback_plan_available=True,
        rollback_tested=True,
        runtime_observable=True,
        structured_logging_enabled=True,
        metrics_available=True,
        audit_events_enabled=True,
        replay_runtime_verified=True,
        replay_runtime_score=96,
        paper_runtime_prepared=True,
        paper_runtime_dependencies_ready=True,
        paper_runtime_score=96,
        isolation_score=96,
        kill_switch_score=96,
        rollback_score=96,
        observability_score=96,
        state_integrity_score=96,
        memory_persistence_score=96,
        notes=("offline sandbox fixture",),
    )


def test_evaluate_sandbox_readiness_ready_for_paper_runtime_when_all_green():
    result = evaluate_sandbox_readiness(stable_input())

    assert result.state == SandboxReadinessState.READY_FOR_PAPER_RUNTIME
    assert result.sandbox_score >= 94
    assert result.blockers == ()
    assert result.offline_only is True
    assert result.runtime_isolation_review.passed is True
    assert result.paper_runtime_preparation_review.passed is True


def test_detects_all_required_sandbox_blockers():
    data = SandboxReadinessInput(
        live_execution_disabled=False,
        execution_isolated=False,
        broker_disabled=False,
        broker_credentials_absent=False,
        external_api_disabled=False,
        api_credentials_absent=False,
        sandbox_network_isolated=False,
        sandbox_filesystem_isolated=False,
        sandbox_state_clean=False,
        runtime_state_validated=False,
        state_checksum_valid=False,
        memory_persistence_isolated=False,
        memory_snapshot_reversible=False,
        kill_switch_configured=False,
        kill_switch_tested=False,
        rollback_plan_available=False,
        rollback_tested=False,
        runtime_observable=False,
        structured_logging_enabled=False,
        metrics_available=False,
        audit_events_enabled=False,
        replay_runtime_verified=False,
        replay_runtime_score=30,
        paper_runtime_prepared=False,
        paper_runtime_dependencies_ready=False,
    )

    blockers = detect_sandbox_blockers(data)

    assert blockers == (
        SandboxBlocker.LIVE_EXECUTION_LEAK,
        SandboxBlocker.BROKER_CONNECTION_RISK,
        SandboxBlocker.API_EXPOSURE_RISK,
        SandboxBlocker.SANDBOX_ISOLATION_FAILURE,
        SandboxBlocker.STATE_CORRUPTION_RISK,
        SandboxBlocker.MEMORY_PERSISTENCE_RISK,
        SandboxBlocker.KILL_SWITCH_FAILURE,
        SandboxBlocker.ROLLBACK_FAILURE,
        SandboxBlocker.OBSERVABILITY_GAP,
        SandboxBlocker.PAPER_RUNTIME_NOT_READY,
    )


def test_live_execution_leak_forces_not_ready_and_offline_false():
    data = replace(stable_input(), live_execution_disabled=False)

    result = evaluate_sandbox_readiness(data)

    assert SandboxBlocker.LIVE_EXECUTION_LEAK in result.blockers
    assert result.state == SandboxReadinessState.NOT_READY
    assert result.offline_only is False


def test_sandbox_review_required_when_multiple_non_hard_blockers_remain():
    data = replace(
        stable_input(),
        kill_switch_tested=False,
        rollback_tested=False,
        runtime_observable=False,
    )

    result = evaluate_sandbox_readiness(data)

    assert result.state == SandboxReadinessState.SANDBOX_REVIEW_REQUIRED
    assert SandboxBlocker.KILL_SWITCH_FAILURE in result.blockers
    assert SandboxBlocker.ROLLBACK_FAILURE in result.blockers
    assert SandboxBlocker.OBSERVABILITY_GAP in result.blockers


def test_sandbox_candidate_when_single_blocker_remains():
    data = replace(stable_input(), paper_runtime_prepared=False)

    result = evaluate_sandbox_readiness(data)

    assert result.state == SandboxReadinessState.SANDBOX_CANDIDATE
    assert result.blockers == (SandboxBlocker.PAPER_RUNTIME_NOT_READY,)


def test_sandbox_ready_when_green_but_below_paper_runtime_threshold():
    data = replace(
        stable_input(),
        isolation_score=89,
        kill_switch_score=89,
        rollback_score=89,
        observability_score=89,
        paper_runtime_score=89,
        state_integrity_score=89,
        memory_persistence_score=89,
        replay_runtime_score=89,
    )

    result = evaluate_sandbox_readiness(data)

    assert result.state == SandboxReadinessState.SANDBOX_READY
    assert result.blockers == ()


def test_individual_reviews_report_expected_blockers():
    data = replace(
        stable_input(),
        broker_credentials_absent=False,
        kill_switch_configured=False,
        rollback_plan_available=False,
        metrics_available=False,
        replay_runtime_verified=False,
    )

    isolation = build_runtime_isolation_review(data)
    kill_switch = build_kill_switch_review(data)
    rollback = build_rollback_review(data)
    observability = build_observability_review(data)
    paper = build_paper_runtime_preparation_review(data)

    assert SandboxBlocker.BROKER_CONNECTION_RISK in isolation.blockers
    assert SandboxBlocker.KILL_SWITCH_FAILURE in kill_switch.blockers
    assert SandboxBlocker.ROLLBACK_FAILURE in rollback.blockers
    assert SandboxBlocker.OBSERVABILITY_GAP in observability.blockers
    assert SandboxBlocker.PAPER_RUNTIME_NOT_READY in paper.blockers


def test_score_penalizes_broker_risk_and_caps_score():
    data = stable_input()
    clean_score = compute_sandbox_score(data, ())
    blocked_score = compute_sandbox_score(data, (SandboxBlocker.BROKER_CONNECTION_RISK,))

    assert blocked_score.overall_score < clean_score.overall_score
    assert blocked_score.overall_score <= 45


def test_recommendations_cover_blockers_and_manual_review_gate():
    recommendations = generate_sandbox_recommendations(
        (
            SandboxBlocker.LIVE_EXECUTION_LEAK,
            SandboxBlocker.KILL_SWITCH_FAILURE,
        ),
        SandboxReadinessState.SANDBOX_REVIEW_REQUIRED,
    )

    assert SandboxRecommendation.HOLD_SANDBOX_ENTRY in recommendations
    assert SandboxRecommendation.SEAL_LIVE_EXECUTION_PATHS in recommendations
    assert SandboxRecommendation.VERIFY_KILL_SWITCH in recommendations
    assert SandboxRecommendation.RUN_SANDBOX_READINESS_SUITE in recommendations


def test_markdown_contains_required_sections_and_blockers():
    result = evaluate_sandbox_readiness(replace(stable_input(), rollback_tested=False))

    markdown = render_sandbox_readiness_markdown(result)

    assert "# AGIcore Sandbox Readiness Audit" in markdown
    assert "# Score Breakdown" in markdown
    assert "# Sandbox Reviews" in markdown
    assert "# Sandbox Blockers" in markdown
    assert "# Recommendations" in markdown
    assert "# Sandbox Outlook" in markdown
    assert "ROLLBACK_FAILURE" in markdown
