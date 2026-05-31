import ast
from pathlib import Path

import pytest

from agicore.trading.paper_runtime_stabilization_review import (
    compute_stabilization_score,
    detect_stabilization_risks,
    evaluate_paper_runtime_stabilization_review,
    generate_stabilization_recommendations,
    render_paper_runtime_stabilization_review_markdown,
    review_error_handling_behavior,
    review_human_supervision_stability,
    review_journal_stability,
    review_kill_switch_stability,
    review_multi_session_consistency,
    review_observability_stability,
    review_rollback_stability,
    review_runtime_stability,
    review_runtime_state_drift,
    review_scenario_repeatability,
)
from agicore.trading.paper_runtime_stabilization_review_models import (
    PaperRuntimeStabilizationDecision,
    PaperRuntimeStabilizationRecommendation,
    PaperRuntimeStabilizationReviewInput,
    PaperRuntimeStabilizationRisk,
    PaperRuntimeStabilizationState,
)


def _upstream(state="READY", decision=None, risks=(), score=100):
    payload = {
        "state": state,
        "risks": tuple(risks),
        "offline_only": True,
        "extended_runtime_score": score,
    }
    if decision:
        payload["decision"] = decision
    return payload


def _ready_input(**overrides):
    payload = {
        "extended_paper_runtime_test": _upstream("READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW", "READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW"),
        "paper_runtime_test_run": _upstream("READY_FOR_EXTENDED_PAPER_RUNTIME_TEST"),
        "paper_runtime_integration_review": _upstream("READY_FOR_PAPER_RUNTIME_TEST_RUN"),
        "paper_trading_runtime_design": _upstream("READY_FOR_RUNTIME_IMPLEMENTATION"),
        "paper_runtime_decision_review": _upstream("READY_FOR_PAPER_TRADING_RUNTIME"),
        "full_paper_session": _upstream("READY_FOR_PAPER_TRADING_RUNTIME"),
        "simulated_market_session": _upstream("READY_FOR_FULL_PAPER_SESSION"),
        "mock_alpaca_session": _upstream("READY_FOR_SIMULATED_MARKET_SESSION"),
        "mock_connectivity_layer": _upstream("READY_FOR_MOCK_ALPACA_SESSION"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "runtime_stable": True,
        "scenarios_repeatable": True,
        "multi_session_consistent": True,
        "error_handling_stable": True,
        "rollback_stable": True,
        "kill_switch_stable": True,
        "human_supervision_stable": True,
        "journal_stable": True,
        "observability_stable": True,
        "runtime_state_reconciled": True,
        "release_candidate_requested": True,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "no_real_broker": True,
        "no_api_key_read": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_api": True,
        "no_real_order": True,
    }
    payload.update(overrides)
    return PaperRuntimeStabilizationReviewInput(**payload)


def test_evaluate_approves_release_candidate_preparation():
    result = evaluate_paper_runtime_stabilization_review(_ready_input())

    assert result.state is PaperRuntimeStabilizationState.READY_FOR_PAPER_RUNTIME_RELEASE_CANDIDATE
    assert result.decision is PaperRuntimeStabilizationDecision.APPROVE_RELEASE_CANDIDATE_PREPARATION
    assert result.risks == ()
    assert result.offline_only is True
    assert result.stabilization_score == 100


def test_stable_when_score_below_release_candidate_threshold():
    result = evaluate_paper_runtime_stabilization_review(
        _ready_input(
            runtime_stability_score=90,
            scenario_repeatability_score=90,
            multi_session_consistency_score=90,
            error_handling_score=90,
            rollback_stability_score=90,
            kill_switch_stability_score=90,
            human_supervision_stability_score=90,
            journal_stability_score=90,
            observability_stability_score=90,
            runtime_state_drift_score=90,
        )
    )

    assert result.state is PaperRuntimeStabilizationState.STABLE
    assert result.decision is PaperRuntimeStabilizationDecision.APPROVE_RELEASE_CANDIDATE_PREPARATION


def test_review_functions_detect_each_primary_risk():
    assert PaperRuntimeStabilizationRisk.RUNTIME_STABILITY_FAILURE in review_runtime_stability(_ready_input(runtime_stable=False)).risks
    assert PaperRuntimeStabilizationRisk.SCENARIO_REPEATABILITY_FAILURE in review_scenario_repeatability(_ready_input(scenarios_repeatable=False)).risks
    assert PaperRuntimeStabilizationRisk.MULTI_SESSION_INCONSISTENCY in review_multi_session_consistency(_ready_input(multi_session_consistent=False)).risks
    assert PaperRuntimeStabilizationRisk.ERROR_HANDLING_GAP in review_error_handling_behavior(_ready_input(error_handling_stable=False)).risks
    assert PaperRuntimeStabilizationRisk.ROLLBACK_STABILITY_GAP in review_rollback_stability(_ready_input(rollback_stable=False)).risks
    assert PaperRuntimeStabilizationRisk.KILL_SWITCH_STABILITY_GAP in review_kill_switch_stability(_ready_input(kill_switch_stable=False)).risks
    assert PaperRuntimeStabilizationRisk.HUMAN_SUPERVISION_STABILITY_GAP in review_human_supervision_stability(_ready_input(human_supervision_stable=False)).risks
    assert PaperRuntimeStabilizationRisk.JOURNAL_STABILITY_GAP in review_journal_stability(_ready_input(journal_stable=False)).risks
    assert PaperRuntimeStabilizationRisk.OBSERVABILITY_STABILITY_GAP in review_observability_stability(_ready_input(observability_stable=False)).risks
    assert PaperRuntimeStabilizationRisk.RUNTIME_STATE_DRIFT in review_runtime_state_drift(_ready_input(runtime_state_reconciled=False)).risks


def test_detects_all_stabilization_risks():
    result = evaluate_paper_runtime_stabilization_review(
        _ready_input(
            runtime_stable=False,
            scenarios_repeatable=False,
            multi_session_consistent=False,
            error_handling_stable=False,
            rollback_stable=False,
            kill_switch_stable=False,
            human_supervision_stable=False,
            journal_stable=False,
            observability_stable=False,
            runtime_state_reconciled=False,
            release_candidate_requested=False,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(PaperRuntimeStabilizationRisk)
    assert result.state is PaperRuntimeStabilizationState.NOT_STABLE
    assert result.decision is PaperRuntimeStabilizationDecision.BLOCK_RELEASE_CANDIDATE
    assert result.offline_only is False


def test_kill_switch_gap_requires_kill_switch_fixes():
    result = evaluate_paper_runtime_stabilization_review(_ready_input(kill_switch_stable=False))

    assert result.decision is PaperRuntimeStabilizationDecision.REQUIRE_KILL_SWITCH_FIXES
    assert result.state is PaperRuntimeStabilizationState.STABILIZATION_REVIEW_REQUIRED


def test_rollback_gap_requires_rollback_fixes():
    result = evaluate_paper_runtime_stabilization_review(_ready_input(rollback_stable=False))

    assert result.decision is PaperRuntimeStabilizationDecision.REQUIRE_ROLLBACK_FIXES


def test_observability_gap_requires_observability_fixes():
    result = evaluate_paper_runtime_stabilization_review(_ready_input(observability_stable=False))

    assert result.decision is PaperRuntimeStabilizationDecision.REQUIRE_OBSERVABILITY_FIXES


def test_soft_single_gap_is_partially_stable():
    result = evaluate_paper_runtime_stabilization_review(_ready_input(journal_stable=False, journal_stability_score=80))

    assert result.state is PaperRuntimeStabilizationState.PARTIALLY_STABLE
    assert result.decision is PaperRuntimeStabilizationDecision.REQUIRE_RUNTIME_CLEANUP
    assert result.risks == (PaperRuntimeStabilizationRisk.JOURNAL_STABILITY_GAP,)


def test_release_candidate_premature_caps_score_and_blocks():
    data = _ready_input(release_candidate_requested=False)
    risks = detect_stabilization_risks(data)
    score = compute_stabilization_score(data, risks)
    result = evaluate_paper_runtime_stabilization_review(data)

    assert PaperRuntimeStabilizationRisk.RELEASE_CANDIDATE_PREMATURE in risks
    assert score.overall_score <= 40
    assert result.decision is PaperRuntimeStabilizationDecision.BLOCK_RELEASE_CANDIDATE


def test_upstream_network_leak_blocks_offline_boundary():
    result = evaluate_paper_runtime_stabilization_review(
        _ready_input(extended_paper_runtime_test=_upstream("READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW", risks=("NETWORK_LEAK",)))
    )

    assert PaperRuntimeStabilizationRisk.RELEASE_CANDIDATE_PREMATURE in result.risks
    assert result.offline_only is False


def test_upstream_runtime_drift_is_detected():
    result = evaluate_paper_runtime_stabilization_review(_ready_input(paper_runtime_test_run=_upstream(risks=("TEST_RUN_STATE_DRIFT",))))

    assert PaperRuntimeStabilizationRisk.RUNTIME_STATE_DRIFT in result.risks


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_stabilization_recommendations(
        (
            PaperRuntimeStabilizationRisk.ROLLBACK_STABILITY_GAP,
            PaperRuntimeStabilizationRisk.ROLLBACK_STABILITY_GAP,
            PaperRuntimeStabilizationRisk.OBSERVABILITY_STABILITY_GAP,
            PaperRuntimeStabilizationRisk.RELEASE_CANDIDATE_PREMATURE,
        ),
        PaperRuntimeStabilizationDecision.REQUIRE_ROLLBACK_FIXES,
    )

    assert recommendations.count(PaperRuntimeStabilizationRecommendation.REPAIR_ROLLBACK_STABILITY) == 1
    assert PaperRuntimeStabilizationRecommendation.REPAIR_OBSERVABILITY_STABILITY in recommendations
    assert PaperRuntimeStabilizationRecommendation.DELAY_RELEASE_CANDIDATE in recommendations
    assert PaperRuntimeStabilizationRecommendation.RUN_STABILIZATION_REVIEW_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_stabilization_recommendations(
        (),
        PaperRuntimeStabilizationDecision.APPROVE_RELEASE_CANDIDATE_PREPARATION,
    )

    assert PaperRuntimeStabilizationRecommendation.APPROVE_RELEASE_CANDIDATE_AFTER_MANUAL_REVIEW in recommendations


def test_markdown_contains_decision_risks_and_recommendations():
    result = evaluate_paper_runtime_stabilization_review(_ready_input(observability_stable=False))
    markdown = render_paper_runtime_stabilization_review_markdown(result)

    assert "# AGIcore Paper Runtime Stabilization Review" in markdown
    assert "Decision: REQUIRE_OBSERVABILITY_FIXES" in markdown
    assert "# Stabilization Reviews" in markdown
    assert "OBSERVABILITY_STABILITY_GAP" in markdown
    assert "REPAIR_OBSERVABILITY_STABILITY" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_paper_runtime_stabilization_review(_ready_input().__dict__)

    assert result.state is PaperRuntimeStabilizationState.READY_FOR_PAPER_RUNTIME_RELEASE_CANDIDATE


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (PaperRuntimeStabilizationRisk.RUNTIME_STABILITY_FAILURE, PaperRuntimeStabilizationRecommendation.REPAIR_RUNTIME_STABILITY),
        (PaperRuntimeStabilizationRisk.KILL_SWITCH_STABILITY_GAP, PaperRuntimeStabilizationRecommendation.REPAIR_KILL_SWITCH_STABILITY),
        (PaperRuntimeStabilizationRisk.RUNTIME_STATE_DRIFT, PaperRuntimeStabilizationRecommendation.RECONCILE_RUNTIME_STATE_DRIFT),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_stabilization_recommendations((risk,), PaperRuntimeStabilizationDecision.REQUIRE_RUNTIME_CLEANUP)


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "paper_runtime_stabilization_review.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
