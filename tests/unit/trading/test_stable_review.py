from dataclasses import replace
from types import SimpleNamespace

from agicore.trading.stable_review import (
    build_codebase_stability_review,
    build_observability_stability_review,
    build_runtime_stability_review,
    build_sandbox_stability_review,
    build_testing_stability_review,
    compute_stable_score,
    detect_stability_blockers,
    evaluate_stable_review,
    generate_stable_recommendations,
    render_stable_review_markdown,
)
from agicore.trading.stable_review_models import (
    StabilityBlocker,
    StableRecommendation,
    StableReviewInput,
    StableReviewState,
)


def ns(**kwargs):
    return SimpleNamespace(**kwargs)


def stable_freeze_candidate_review():
    return ns(
        state="READY_FOR_SANDBOX",
        freeze_candidate_score=96,
        score_breakdown=ns(
            architecture_score=96,
            runtime_score=96,
            observability_score=96,
            paper_runtime_score=96,
        ),
        blockers=(),
        architecture_review=ns(score=96, blockers=()),
        runtime_review=ns(score=96, blockers=()),
        observability_review=ns(score=96, blockers=()),
        paper_runtime_review=ns(score=96, blockers=()),
        offline_only=True,
    )


def stable_freeze_readiness_audit():
    return ns(
        state="READY_TO_TRY",
        freeze_readiness_score=96,
        snapshot=ns(
            test_coverage_score=100,
            cognitive_fragmentation_score=96,
            engine_conflict_score=96,
            global_stability_score=96,
            runtime_coherence_score=96,
            observability_score=96,
            replay_safety_score=96,
            sandbox_score=96,
            paper_trading_score=96,
        ),
        blockers=(),
        offline_only=True,
    )


def stable_input():
    return StableReviewInput(
        freeze_candidate_review=stable_freeze_candidate_review(),
        freeze_readiness_audit=stable_freeze_readiness_audit(),
        tests_green=True,
        unit_test_pass_rate=1.0,
        flaky_test_count=0,
        test_failure_count=0,
        codebase_stable=True,
        module_fragmentation_count=0,
        module_coherence_score=96,
        import_structure_valid=True,
        import_coherence_score=96,
        runtime_state_clear=True,
        runtime_state_score=96,
        runtime_recoverable=True,
        logging_consistent=True,
        structured_logging_enabled=True,
        runtime_observable=True,
        metrics_available=True,
        replay_runtime_verified=True,
        replay_runtime_score=96,
        kill_switch_verified=True,
        rollback_verified=True,
        sandbox_prep_complete=True,
        paper_runtime_ready=True,
        execution_isolated=True,
        broker_disabled=True,
        external_api_disabled=True,
        live_execution_disabled=True,
        notes=("offline stable fixture",),
    )


def test_evaluate_stable_review_ready_for_sandbox_prep_when_all_green():
    result = evaluate_stable_review(stable_input())

    assert result.state == StableReviewState.READY_FOR_SANDBOX_PREP
    assert result.stable_score >= 94
    assert result.blockers == ()
    assert result.offline_only is True
    assert result.codebase_review.passed is True
    assert result.sandbox_review.passed is True


def test_detects_all_required_stability_blockers():
    data = StableReviewInput(
        tests_green=False,
        unit_test_pass_rate=0.71,
        flaky_test_count=2,
        test_failure_count=2,
        codebase_stable=False,
        module_fragmentation_count=3,
        module_coherence_score=35,
        import_structure_valid=False,
        import_coherence_score=35,
        runtime_state_clear=False,
        runtime_state_score=30,
        runtime_recoverable=False,
        logging_consistent=False,
        structured_logging_enabled=False,
        runtime_observable=False,
        metrics_available=False,
        replay_runtime_verified=False,
        replay_runtime_score=30,
        kill_switch_verified=False,
        rollback_verified=False,
        sandbox_prep_complete=False,
        paper_runtime_ready=False,
        execution_isolated=False,
        broker_disabled=False,
        external_api_disabled=False,
        live_execution_disabled=False,
    )

    blockers = detect_stability_blockers(data)

    assert blockers == (
        StabilityBlocker.CODEBASE_FRAGMENTATION,
        StabilityBlocker.IMPORT_STRUCTURE_RISK,
        StabilityBlocker.RUNTIME_STATE_AMBIGUITY,
        StabilityBlocker.TEST_SUITE_INSTABILITY,
        StabilityBlocker.LOGGING_INCONSISTENCY,
        StabilityBlocker.OBSERVABILITY_GAP,
        StabilityBlocker.SANDBOX_PREP_INCOMPLETE,
        StabilityBlocker.REPLAY_RUNTIME_UNVERIFIED,
        StabilityBlocker.KILL_SWITCH_UNVERIFIED,
        StabilityBlocker.ROLLBACK_UNVERIFIED,
    )


def test_not_stable_when_many_blockers_and_offline_false():
    data = replace(
        stable_input(),
        tests_green=False,
        unit_test_pass_rate=0.7,
        codebase_stable=False,
        module_fragmentation_count=2,
        import_structure_valid=False,
        runtime_state_clear=False,
        logging_consistent=False,
        runtime_observable=False,
        sandbox_prep_complete=False,
        execution_isolated=False,
        broker_disabled=False,
    )

    result = evaluate_stable_review(data)

    assert result.state == StableReviewState.NOT_STABLE
    assert result.offline_only is False


def test_stability_review_required_when_multiple_blockers_remain():
    data = replace(
        stable_input(),
        tests_green=False,
        unit_test_pass_rate=0.9,
        replay_runtime_verified=False,
        kill_switch_verified=False,
    )

    result = evaluate_stable_review(data)

    assert result.state == StableReviewState.STABILITY_REVIEW_REQUIRED
    assert StabilityBlocker.TEST_SUITE_INSTABILITY in result.blockers
    assert StabilityBlocker.REPLAY_RUNTIME_UNVERIFIED in result.blockers
    assert StabilityBlocker.KILL_SWITCH_UNVERIFIED in result.blockers


def test_stable_candidate_when_single_blocker_remains():
    data = replace(stable_input(), sandbox_prep_complete=False)

    result = evaluate_stable_review(data)

    assert result.state == StableReviewState.STABLE_CANDIDATE
    assert result.blockers == (StabilityBlocker.SANDBOX_PREP_INCOMPLETE,)


def test_stable_state_when_green_but_below_sandbox_prep_threshold():
    candidate = ns(
        state="STABLE",
        freeze_candidate_score=89,
        score_breakdown=ns(
            architecture_score=89,
            runtime_score=89,
            observability_score=89,
            paper_runtime_score=89,
        ),
        blockers=(),
        architecture_review=ns(score=89, blockers=()),
        runtime_review=ns(score=89, blockers=()),
        observability_review=ns(score=89, blockers=()),
        paper_runtime_review=ns(score=89, blockers=()),
        offline_only=True,
    )
    data = replace(
        stable_input(),
        freeze_candidate_review=candidate,
        codebase_score=89,
        runtime_score=89,
        testing_score=89,
        observability_score=89,
        sandbox_score=89,
        module_coherence_score=89,
        import_coherence_score=89,
        runtime_state_score=89,
        replay_runtime_score=89,
    )

    result = evaluate_stable_review(data)

    assert result.state == StableReviewState.STABLE
    assert result.blockers == ()


def test_individual_reviews_report_expected_blockers():
    data = replace(
        stable_input(),
        import_structure_valid=False,
        runtime_state_clear=False,
        tests_green=False,
        logging_consistent=False,
        sandbox_prep_complete=False,
    )

    codebase = build_codebase_stability_review(data)
    runtime = build_runtime_stability_review(data)
    testing = build_testing_stability_review(data)
    observability = build_observability_stability_review(data)
    sandbox = build_sandbox_stability_review(data)

    assert StabilityBlocker.IMPORT_STRUCTURE_RISK in codebase.blockers
    assert StabilityBlocker.RUNTIME_STATE_AMBIGUITY in runtime.blockers
    assert StabilityBlocker.TEST_SUITE_INSTABILITY in testing.blockers
    assert StabilityBlocker.LOGGING_INCONSISTENCY in observability.blockers
    assert StabilityBlocker.SANDBOX_PREP_INCOMPLETE in sandbox.blockers


def test_score_penalizes_test_instability_and_caps_score():
    data = stable_input()
    clean_score = compute_stable_score(data, ())
    blocked_score = compute_stable_score(data, (StabilityBlocker.TEST_SUITE_INSTABILITY,))

    assert blocked_score.overall_score < clean_score.overall_score
    assert blocked_score.overall_score <= 72


def test_recommendations_cover_blockers_and_manual_review_gate():
    recommendations = generate_stable_recommendations(
        (
            StabilityBlocker.CODEBASE_FRAGMENTATION,
            StabilityBlocker.KILL_SWITCH_UNVERIFIED,
        ),
        StableReviewState.STABILITY_REVIEW_REQUIRED,
    )

    assert StableRecommendation.HOLD_STABLE_PROMOTION in recommendations
    assert StableRecommendation.CONSOLIDATE_CODEBASE_MODULES in recommendations
    assert StableRecommendation.VERIFY_KILL_SWITCH in recommendations
    assert StableRecommendation.RUN_STABLE_REVIEW_SUITE in recommendations


def test_markdown_contains_required_sections_and_blockers():
    result = evaluate_stable_review(replace(stable_input(), rollback_verified=False))

    markdown = render_stable_review_markdown(result)

    assert "# AGIcore Stable Review" in markdown
    assert "# Score Breakdown" in markdown
    assert "# Stability Sections" in markdown
    assert "# Stability Blockers" in markdown
    assert "# Recommendations" in markdown
    assert "# Stable Outlook" in markdown
    assert "ROLLBACK_UNVERIFIED" in markdown
