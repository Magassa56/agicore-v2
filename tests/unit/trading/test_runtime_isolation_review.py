from types import SimpleNamespace

import pytest

from agicore.trading.runtime_isolation_review import (
    compute_isolation_score,
    detect_isolation_risks,
    evaluate_runtime_isolation,
    generate_isolation_recommendations,
    render_runtime_isolation_markdown,
    review_execution_boundaries,
    review_external_dependency_boundaries,
    review_memory_boundaries,
    review_network_boundaries,
    review_storage_boundaries,
)
from agicore.trading.runtime_isolation_review_models import (
    IsolationRecommendation,
    IsolationRisk,
    RuntimeIsolationInput,
    RuntimeIsolationState,
)


def _sandbox_audit(**overrides):
    data = {
        "state": "READY_FOR_PAPER_RUNTIME",
        "sandbox_score": 96.0,
        "blockers": (),
        "offline_only": True,
        "score_breakdown": SimpleNamespace(
            runtime_isolation_score=96.0,
            kill_switch_score=96.0,
            rollback_score=96.0,
            observability_score=96.0,
            memory_persistence_score=96.0,
            paper_runtime_preparation_score=96.0,
        ),
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def _review_result(state="STABLE", score=96.0, blockers=(), risks=()):
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
        "sandbox_readiness_audit": _sandbox_audit(),
        "stable_review": _review_result(),
        "freeze_candidate_review": _review_result(state="READY_FOR_SANDBOX"),
        "freeze_readiness_audit": _review_result(state="READY_TO_TRY"),
        "execution_isolated": True,
        "live_execution_disabled": True,
        "real_order_path_disabled": True,
        "broker_disabled": True,
        "broker_credentials_absent": True,
        "external_api_disabled": True,
        "api_credentials_absent": True,
        "network_disabled": True,
        "network_allowlist_empty": True,
        "filesystem_root_restricted": True,
        "data_directory_readonly": True,
        "temp_directory_isolated": True,
        "memory_namespace_isolated": True,
        "memory_snapshot_clean": True,
        "memory_cross_run_guard": True,
        "storage_namespace_isolated": True,
        "storage_rollback_available": True,
        "storage_checksum_valid": True,
        "dependencies_offline": True,
        "dependency_mocks_available": True,
        "dependency_lock_verified": True,
        "runtime_observable": True,
        "isolated_logging_enabled": True,
        "isolated_metrics_enabled": True,
        "sandbox_escape_tests_passed": True,
        "paper_runtime_ready": True,
        "execution_boundary_score": 96.0,
        "memory_boundary_score": 96.0,
        "storage_boundary_score": 96.0,
        "network_boundary_score": 96.0,
        "dependency_boundary_score": 96.0,
        "observability_score": 96.0,
        "sandbox_breakout_score": 96.0,
    }
    data.update(overrides)
    return RuntimeIsolationInput(**data)


def test_evaluate_runtime_isolation_ready_for_paper_runtime_when_boundaries_are_clean():
    result = evaluate_runtime_isolation(_ready_input())

    assert result.state is RuntimeIsolationState.READY_FOR_PAPER_RUNTIME
    assert result.risks == ()
    assert result.isolation_score >= 94.0
    assert result.offline_only is True
    assert result.isolation_graph.blocked_edges == (
        ("execution_boundary", "broker"),
        ("network_boundary", "external_api"),
        ("storage_boundary", "host_filesystem"),
    )
    assert result.execution_boundaries.passed is True
    assert result.memory_boundaries.passed is True
    assert result.storage_boundaries.passed is True
    assert result.network_boundaries.passed is True
    assert result.external_dependency_boundaries.passed is True


def test_detect_isolation_risks_reports_all_boundary_failures():
    data = _ready_input(
        execution_isolated=False,
        live_execution_disabled=False,
        real_order_path_disabled=False,
        broker_disabled=False,
        broker_credentials_absent=False,
        external_api_disabled=False,
        api_credentials_absent=False,
        network_disabled=False,
        network_allowlist_empty=False,
        filesystem_root_restricted=False,
        data_directory_readonly=False,
        temp_directory_isolated=False,
        memory_namespace_isolated=False,
        memory_snapshot_clean=False,
        memory_cross_run_guard=False,
        storage_namespace_isolated=False,
        storage_rollback_available=False,
        storage_checksum_valid=False,
        dependencies_offline=False,
        dependency_mocks_available=False,
        dependency_lock_verified=False,
        runtime_observable=False,
        isolated_logging_enabled=False,
        isolated_metrics_enabled=False,
        sandbox_escape_tests_passed=False,
        paper_runtime_ready=False,
        execution_boundary_score=10.0,
        memory_boundary_score=10.0,
        storage_boundary_score=10.0,
        network_boundary_score=10.0,
        dependency_boundary_score=10.0,
        observability_score=10.0,
        sandbox_breakout_score=10.0,
    )

    risks = detect_isolation_risks(data)

    assert set(risks) == set(IsolationRisk)


def test_hard_external_access_risk_forces_not_isolated():
    result = evaluate_runtime_isolation(
        _ready_input(external_api_disabled=False, api_credentials_absent=False)
    )

    assert result.state is RuntimeIsolationState.NOT_ISOLATED
    assert IsolationRisk.EXTERNAL_API_ACCESS in result.risks
    assert result.offline_only is False
    assert result.isolation_graph.escape_edges == (("network_boundary", "external_api"),)


def test_three_soft_risks_require_isolation_review_without_hard_failure():
    result = evaluate_runtime_isolation(
        _ready_input(
            memory_snapshot_clean=False,
            storage_checksum_valid=False,
            runtime_observable=False,
        )
    )

    assert result.state is RuntimeIsolationState.ISOLATION_REVIEW_REQUIRED
    assert result.offline_only is True
    assert {
        IsolationRisk.MEMORY_CROSS_CONTAMINATION,
        IsolationRisk.STORAGE_CORRUPTION_RISK,
        IsolationRisk.OBSERVABILITY_ISOLATION_GAP,
    }.issubset(result.risks)


def test_single_soft_risk_yields_partially_isolated():
    result = evaluate_runtime_isolation(_ready_input(memory_snapshot_clean=False))

    assert result.state is RuntimeIsolationState.PARTIALLY_ISOLATED
    assert result.risks == (IsolationRisk.MEMORY_CROSS_CONTAMINATION,)


def test_isolated_state_when_clean_but_paper_runtime_is_not_ready_yet():
    result = evaluate_runtime_isolation(
        _ready_input(
            paper_runtime_ready=False,
            execution_boundary_score=89.0,
            memory_boundary_score=89.0,
            storage_boundary_score=89.0,
            network_boundary_score=89.0,
            dependency_boundary_score=89.0,
            observability_score=89.0,
            sandbox_breakout_score=89.0,
        )
    )

    assert result.state is RuntimeIsolationState.ISOLATED
    assert result.risks == ()
    assert result.isolation_score >= 88.0


def test_review_sections_expose_boundary_specific_risks():
    data = _ready_input(
        broker_disabled=False,
        network_disabled=False,
        filesystem_root_restricted=False,
        dependencies_offline=False,
        memory_namespace_isolated=False,
    )

    assert IsolationRisk.BROKER_CONNECTIVITY in review_execution_boundaries(data).risks
    assert IsolationRisk.MEMORY_CROSS_CONTAMINATION in review_memory_boundaries(data).risks
    assert IsolationRisk.FILESYSTEM_ESCAPE in review_storage_boundaries(data).risks
    assert IsolationRisk.NETWORK_LEAK in review_network_boundaries(data).risks
    assert (
        IsolationRisk.DEPENDENCY_ESCAPE
        in review_external_dependency_boundaries(data).risks
    )


def test_compute_isolation_score_caps_unsafe_network_and_execution_states():
    data = _ready_input(live_execution_disabled=False, network_disabled=False)
    sections = (
        review_execution_boundaries(data),
        review_memory_boundaries(data),
        review_storage_boundaries(data),
        review_network_boundaries(data),
        review_external_dependency_boundaries(data),
    )
    risks = (
        IsolationRisk.EXECUTION_BOUNDARY_FAILURE,
        IsolationRisk.NETWORK_LEAK,
    )

    score = compute_isolation_score(data, risks, *sections)

    assert score.overall_score <= 50.0


def test_generate_recommendations_are_deduplicated_and_risk_driven():
    result = evaluate_runtime_isolation(
        _ready_input(
            external_api_disabled=False,
            broker_disabled=False,
            memory_snapshot_clean=False,
        )
    )

    recommendations = generate_isolation_recommendations(result.risks, result.state)

    assert IsolationRecommendation.DISABLE_EXTERNAL_API_ACCESS in recommendations
    assert IsolationRecommendation.DISABLE_BROKER_CONNECTIVITY in recommendations
    assert IsolationRecommendation.ISOLATE_MEMORY_CONTEXT in recommendations
    assert len(recommendations) == len(set(recommendations))


def test_markdown_contains_runtime_isolation_report_sections():
    result = evaluate_runtime_isolation(_ready_input())

    markdown = render_runtime_isolation_markdown(result)

    assert "# AGIcore Runtime Isolation Review" in markdown
    assert "# Runtime Isolation Graph" in markdown
    assert "# Isolation Risks" in markdown
    assert "READY_FOR_PAPER_RUNTIME" in markdown


def test_evaluate_runtime_isolation_accepts_compatible_upstream_results():
    result = evaluate_runtime_isolation(
        _ready_input(
            sandbox_readiness_audit=_sandbox_audit(),
            stable_review=_review_result(),
            freeze_candidate_review=_review_result(state="READY_FOR_SANDBOX"),
            freeze_readiness_audit=_review_result(state="READY_TO_TRY"),
        )
    )

    assert result.state is RuntimeIsolationState.READY_FOR_PAPER_RUNTIME
    assert result.risks == ()


@pytest.mark.parametrize(
    ("risk", "expected"),
    [
        (
            IsolationRisk.FILESYSTEM_ESCAPE,
            IsolationRecommendation.RESTRICT_FILESYSTEM_SCOPE,
        ),
        (
            IsolationRisk.SANDBOX_BREAKOUT_RISK,
            IsolationRecommendation.REBUILD_SANDBOX_BOUNDARY,
        ),
    ],
)
def test_recommendation_mapping_for_storage_and_breakout_risks(risk, expected):
    result = evaluate_runtime_isolation(_ready_input())
    result = result.__class__(
        state=result.state,
        isolation_score=result.isolation_score,
        score_breakdown=result.score_breakdown,
        risks=(risk,),
        recommendations=(),
        execution_boundaries=result.execution_boundaries,
        memory_boundaries=result.memory_boundaries,
        storage_boundaries=result.storage_boundaries,
        network_boundaries=result.network_boundaries,
        external_dependency_boundaries=result.external_dependency_boundaries,
        isolation_graph=result.isolation_graph,
        offline_only=result.offline_only,
        summary=result.summary,
    )

    assert expected in generate_isolation_recommendations(result.risks, result.state)
