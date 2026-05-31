import ast
from pathlib import Path

import pytest

from agicore.trading.paper_runtime_release_candidate import (
    compute_release_candidate_score,
    detect_release_candidate_risks,
    evaluate_paper_runtime_release_candidate,
    generate_release_candidate_recommendations,
    render_paper_runtime_release_candidate_markdown,
    review_release_candidate_scope,
    review_runtime_documentation_readiness,
    review_runtime_freeze_status,
    review_runtime_human_supervision_readiness,
    review_runtime_kill_switch_readiness,
    review_runtime_observability_readiness,
    review_runtime_operational_boundaries,
    review_runtime_rollback_readiness,
    review_runtime_safety_guards,
    review_runtime_stability_evidence,
    review_runtime_test_coverage,
)
from agicore.trading.paper_runtime_release_candidate_models import (
    PaperRuntimeReleaseCandidateDecision,
    PaperRuntimeReleaseCandidateInput,
    PaperRuntimeReleaseCandidateRecommendation,
    PaperRuntimeReleaseCandidateRisk,
    PaperRuntimeReleaseCandidateState,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {
        "state": state,
        "risks": tuple(risks),
        "offline_only": True,
        "stabilization_score": 100,
        "extended_runtime_score": 100,
        "test_run_score": 100,
    }
    if decision:
        payload["decision"] = decision
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_runtime_stabilization_review": _upstream(
            "READY_FOR_PAPER_RUNTIME_RELEASE_CANDIDATE",
            "APPROVE_RELEASE_CANDIDATE_PREPARATION",
        ),
        "extended_paper_runtime_test": _upstream("READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW"),
        "paper_runtime_test_run": _upstream("READY_FOR_EXTENDED_PAPER_RUNTIME_TEST"),
        "paper_trading_runtime": _upstream("COMPLETED"),
        "paper_runtime_integration_review": _upstream("READY_FOR_PAPER_RUNTIME_TEST_RUN"),
        "paper_trading_runtime_design": _upstream("READY_FOR_RUNTIME_IMPLEMENTATION"),
        "paper_runtime_decision_review": _upstream("READY_FOR_PAPER_TRADING_RUNTIME", "APPROVE_PAPER_TRADING_RUNTIME_CREATION"),
        "full_paper_session": _upstream("READY_FOR_PAPER_TRADING_RUNTIME"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "rc_scope_defined": True,
        "runtime_frozen": True,
        "test_coverage_ready": True,
        "stability_evidence_complete": True,
        "documentation_ready": True,
        "operational_boundaries_enforced": True,
        "safety_guards_ready": True,
        "observability_ready": True,
        "rollback_ready": True,
        "kill_switch_ready": True,
        "human_supervision_ready": True,
        "rc_approval_requested": True,
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
    return PaperRuntimeReleaseCandidateInput(**payload)


def test_evaluate_approves_paper_runtime_release_candidate():
    result = evaluate_paper_runtime_release_candidate(_ready_input())

    assert result.state is PaperRuntimeReleaseCandidateState.READY_FOR_PAPER_RUNTIME_VALIDATION
    assert result.decision is PaperRuntimeReleaseCandidateDecision.APPROVE_PAPER_RUNTIME_RELEASE_CANDIDATE
    assert result.risks == ()
    assert result.offline_only is True
    assert result.release_candidate_score == 100


def test_release_candidate_ready_when_score_below_validation_threshold():
    result = evaluate_paper_runtime_release_candidate(
        _ready_input(
            release_candidate_scope_score=90,
            runtime_freeze_score=90,
            runtime_test_coverage_score=90,
            runtime_stability_evidence_score=90,
            runtime_documentation_score=90,
            runtime_operational_boundaries_score=90,
            runtime_safety_guards_score=90,
            runtime_observability_score=90,
            runtime_rollback_score=90,
            runtime_kill_switch_score=90,
            runtime_human_supervision_score=90,
        )
    )

    assert result.state is PaperRuntimeReleaseCandidateState.RELEASE_CANDIDATE_READY
    assert result.decision is PaperRuntimeReleaseCandidateDecision.APPROVE_PAPER_RUNTIME_RELEASE_CANDIDATE


def test_review_functions_detect_each_primary_risk():
    assert PaperRuntimeReleaseCandidateRisk.RC_SCOPE_UNCLEAR in review_release_candidate_scope(_ready_input(rc_scope_defined=False)).risks
    assert PaperRuntimeReleaseCandidateRisk.RUNTIME_NOT_FROZEN in review_runtime_freeze_status(_ready_input(runtime_frozen=False)).risks
    assert PaperRuntimeReleaseCandidateRisk.TEST_COVERAGE_GAP in review_runtime_test_coverage(_ready_input(test_coverage_ready=False)).risks
    assert PaperRuntimeReleaseCandidateRisk.STABILITY_EVIDENCE_INCOMPLETE in review_runtime_stability_evidence(_ready_input(stability_evidence_complete=False)).risks
    assert PaperRuntimeReleaseCandidateRisk.DOCUMENTATION_GAP in review_runtime_documentation_readiness(_ready_input(documentation_ready=False)).risks
    assert PaperRuntimeReleaseCandidateRisk.OPERATIONAL_BOUNDARY_GAP in review_runtime_operational_boundaries(_ready_input(operational_boundaries_enforced=False)).risks
    assert PaperRuntimeReleaseCandidateRisk.SAFETY_GUARD_GAP in review_runtime_safety_guards(_ready_input(safety_guards_ready=False)).risks
    assert PaperRuntimeReleaseCandidateRisk.OBSERVABILITY_READINESS_GAP in review_runtime_observability_readiness(_ready_input(observability_ready=False)).risks
    assert PaperRuntimeReleaseCandidateRisk.ROLLBACK_READINESS_GAP in review_runtime_rollback_readiness(_ready_input(rollback_ready=False)).risks
    assert PaperRuntimeReleaseCandidateRisk.KILL_SWITCH_READINESS_GAP in review_runtime_kill_switch_readiness(_ready_input(kill_switch_ready=False)).risks
    assert PaperRuntimeReleaseCandidateRisk.HUMAN_SUPERVISION_READINESS_GAP in review_runtime_human_supervision_readiness(_ready_input(human_supervision_ready=False)).risks


def test_detects_all_release_candidate_risks():
    result = evaluate_paper_runtime_release_candidate(
        _ready_input(
            rc_scope_defined=False,
            runtime_frozen=False,
            test_coverage_ready=False,
            stability_evidence_complete=False,
            documentation_ready=False,
            operational_boundaries_enforced=False,
            safety_guards_ready=False,
            observability_ready=False,
            rollback_ready=False,
            kill_switch_ready=False,
            human_supervision_ready=False,
            rc_approval_requested=False,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(PaperRuntimeReleaseCandidateRisk)
    assert result.state is PaperRuntimeReleaseCandidateState.NOT_READY
    assert result.decision is PaperRuntimeReleaseCandidateDecision.BLOCK_RELEASE_CANDIDATE
    assert result.offline_only is False


def test_runtime_not_frozen_requires_freeze():
    result = evaluate_paper_runtime_release_candidate(_ready_input(runtime_frozen=False))

    assert result.decision is PaperRuntimeReleaseCandidateDecision.REQUIRE_RUNTIME_FREEZE
    assert result.state is PaperRuntimeReleaseCandidateState.RC_REVIEW_REQUIRED


def test_test_coverage_gap_requires_test_coverage_fixes():
    result = evaluate_paper_runtime_release_candidate(_ready_input(test_coverage_ready=False))

    assert result.decision is PaperRuntimeReleaseCandidateDecision.REQUIRE_TEST_COVERAGE_FIXES


def test_stability_evidence_gap_requires_stability_evidence():
    result = evaluate_paper_runtime_release_candidate(_ready_input(stability_evidence_complete=False))

    assert result.decision is PaperRuntimeReleaseCandidateDecision.REQUIRE_STABILITY_EVIDENCE


def test_documentation_gap_requires_documentation_fixes():
    result = evaluate_paper_runtime_release_candidate(_ready_input(documentation_ready=False, runtime_documentation_score=80))

    assert result.decision is PaperRuntimeReleaseCandidateDecision.REQUIRE_DOCUMENTATION_FIXES
    assert result.state is PaperRuntimeReleaseCandidateState.PARTIALLY_READY


def test_scope_gap_blocks_release_candidate():
    result = evaluate_paper_runtime_release_candidate(_ready_input(rc_scope_defined=False))

    assert result.decision is PaperRuntimeReleaseCandidateDecision.BLOCK_RELEASE_CANDIDATE
    assert result.state is PaperRuntimeReleaseCandidateState.NOT_READY


def test_premature_rc_approval_caps_score_and_blocks():
    data = _ready_input(rc_approval_requested=False)
    risks = detect_release_candidate_risks(data)
    score = compute_release_candidate_score(data, risks)
    result = evaluate_paper_runtime_release_candidate(data)

    assert PaperRuntimeReleaseCandidateRisk.PREMATURE_RC_APPROVAL in risks
    assert score.overall_score <= 40
    assert result.decision is PaperRuntimeReleaseCandidateDecision.BLOCK_RELEASE_CANDIDATE


def test_upstream_network_leak_breaks_offline_boundary():
    result = evaluate_paper_runtime_release_candidate(
        _ready_input(paper_runtime_stabilization_review=_upstream("READY_FOR_PAPER_RUNTIME_RELEASE_CANDIDATE", risks=("NETWORK_LEAK",)))
    )

    assert PaperRuntimeReleaseCandidateRisk.PREMATURE_RC_APPROVAL in result.risks
    assert PaperRuntimeReleaseCandidateRisk.OPERATIONAL_BOUNDARY_GAP in result.risks
    assert result.offline_only is False


def test_upstream_stability_drift_is_detected():
    result = evaluate_paper_runtime_release_candidate(_ready_input(extended_paper_runtime_test=_upstream(risks=("RUNTIME_STATE_DRIFT",))))

    assert PaperRuntimeReleaseCandidateRisk.STABILITY_EVIDENCE_INCOMPLETE in result.risks
    assert PaperRuntimeReleaseCandidateRisk.RUNTIME_NOT_FROZEN in result.risks


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_release_candidate_recommendations(
        (
            PaperRuntimeReleaseCandidateRisk.RUNTIME_NOT_FROZEN,
            PaperRuntimeReleaseCandidateRisk.RUNTIME_NOT_FROZEN,
            PaperRuntimeReleaseCandidateRisk.DOCUMENTATION_GAP,
            PaperRuntimeReleaseCandidateRisk.PREMATURE_RC_APPROVAL,
        ),
        PaperRuntimeReleaseCandidateDecision.REQUIRE_RUNTIME_FREEZE,
    )

    assert recommendations.count(PaperRuntimeReleaseCandidateRecommendation.FREEZE_RUNTIME_SURFACE) == 1
    assert PaperRuntimeReleaseCandidateRecommendation.COMPLETE_RUNTIME_DOCUMENTATION in recommendations
    assert PaperRuntimeReleaseCandidateRecommendation.DELAY_RC_APPROVAL in recommendations
    assert PaperRuntimeReleaseCandidateRecommendation.RUN_RELEASE_CANDIDATE_REVIEW_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_release_candidate_recommendations(
        (),
        PaperRuntimeReleaseCandidateDecision.APPROVE_PAPER_RUNTIME_RELEASE_CANDIDATE,
    )

    assert PaperRuntimeReleaseCandidateRecommendation.APPROVE_FOR_PAPER_RUNTIME_VALIDATION in recommendations


def test_markdown_contains_decision_risks_and_recommendations():
    result = evaluate_paper_runtime_release_candidate(_ready_input(documentation_ready=False))
    markdown = render_paper_runtime_release_candidate_markdown(result)

    assert "# AGIcore Paper Runtime Release Candidate" in markdown
    assert "Decision: REQUIRE_DOCUMENTATION_FIXES" in markdown
    assert "# Release Candidate Reviews" in markdown
    assert "DOCUMENTATION_GAP" in markdown
    assert "COMPLETE_RUNTIME_DOCUMENTATION" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_paper_runtime_release_candidate(_ready_input().__dict__)

    assert result.state is PaperRuntimeReleaseCandidateState.READY_FOR_PAPER_RUNTIME_VALIDATION


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (PaperRuntimeReleaseCandidateRisk.TEST_COVERAGE_GAP, PaperRuntimeReleaseCandidateRecommendation.REPAIR_TEST_COVERAGE),
        (PaperRuntimeReleaseCandidateRisk.KILL_SWITCH_READINESS_GAP, PaperRuntimeReleaseCandidateRecommendation.REPAIR_KILL_SWITCH_READINESS),
        (PaperRuntimeReleaseCandidateRisk.HUMAN_SUPERVISION_READINESS_GAP, PaperRuntimeReleaseCandidateRecommendation.REPAIR_HUMAN_SUPERVISION_READINESS),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_release_candidate_recommendations((risk,), PaperRuntimeReleaseCandidateDecision.REQUIRE_STABILITY_EVIDENCE)


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "paper_runtime_release_candidate.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
