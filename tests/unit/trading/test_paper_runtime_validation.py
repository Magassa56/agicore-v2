import ast
from pathlib import Path

import pytest

from agicore.trading.paper_runtime_validation import (
    compute_validation_score,
    detect_validation_risks,
    evaluate_paper_runtime_validation,
    generate_validation_recommendations,
    render_paper_runtime_validation_markdown,
    validate_extended_test_evidence,
    validate_human_supervision_evidence,
    validate_kill_switch_evidence,
    validate_observability_evidence,
    validate_operational_boundaries,
    validate_release_candidate_status,
    validate_rollback_evidence,
    validate_runtime_execution_evidence,
    validate_runtime_test_evidence,
    validate_safety_evidence,
    validate_stabilization_evidence,
)
from agicore.trading.paper_runtime_validation_models import (
    PaperRuntimeValidationDecision,
    PaperRuntimeValidationInput,
    PaperRuntimeValidationRecommendation,
    PaperRuntimeValidationRisk,
    PaperRuntimeValidationState,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {
        "state": state,
        "risks": tuple(risks),
        "offline_only": True,
        "release_candidate_score": 100,
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
        "paper_runtime_release_candidate": _upstream(
            "READY_FOR_PAPER_RUNTIME_VALIDATION",
            "APPROVE_PAPER_RUNTIME_RELEASE_CANDIDATE",
        ),
        "paper_runtime_stabilization_review": _upstream(
            "READY_FOR_PAPER_RUNTIME_RELEASE_CANDIDATE",
            "APPROVE_RELEASE_CANDIDATE_PREPARATION",
        ),
        "extended_paper_runtime_test": _upstream("READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW"),
        "paper_runtime_test_run": _upstream("READY_FOR_EXTENDED_PAPER_RUNTIME_TEST"),
        "paper_trading_runtime": _upstream("COMPLETED"),
        "paper_runtime_integration_review": _upstream("READY_FOR_PAPER_RUNTIME_TEST_RUN"),
        "paper_trading_runtime_design": _upstream("READY_FOR_RUNTIME_IMPLEMENTATION"),
        "paper_runtime_decision_review": _upstream("READY_FOR_PAPER_TRADING_RUNTIME"),
        "full_paper_session": _upstream("READY_FOR_PAPER_TRADING_RUNTIME"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "release_candidate_ready": True,
        "runtime_execution_evidence_ready": True,
        "runtime_test_evidence_ready": True,
        "extended_test_evidence_ready": True,
        "stabilization_evidence_ready": True,
        "safety_evidence_ready": True,
        "observability_evidence_ready": True,
        "rollback_evidence_ready": True,
        "kill_switch_evidence_ready": True,
        "human_supervision_evidence_ready": True,
        "operational_boundaries_validated": True,
        "validation_approval_requested": True,
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
    return PaperRuntimeValidationInput(**payload)


def test_evaluate_approves_paper_runtime_validation():
    result = evaluate_paper_runtime_validation(_ready_input())

    assert result.state is PaperRuntimeValidationState.READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT
    assert result.decision is PaperRuntimeValidationDecision.APPROVE_PAPER_RUNTIME_VALIDATION
    assert result.risks == ()
    assert result.offline_only is True
    assert result.validation_score == 100


def test_validated_when_score_below_report_threshold():
    result = evaluate_paper_runtime_validation(
        _ready_input(
            release_candidate_status_score=90,
            runtime_execution_evidence_score=90,
            runtime_test_evidence_score=90,
            extended_test_evidence_score=90,
            stabilization_evidence_score=90,
            safety_evidence_score=90,
            observability_evidence_score=90,
            rollback_evidence_score=90,
            kill_switch_evidence_score=90,
            human_supervision_evidence_score=90,
            operational_boundaries_score=90,
        )
    )

    assert result.state is PaperRuntimeValidationState.VALIDATED
    assert result.decision is PaperRuntimeValidationDecision.APPROVE_PAPER_RUNTIME_VALIDATION


def test_validation_functions_detect_each_primary_risk():
    assert PaperRuntimeValidationRisk.RELEASE_CANDIDATE_NOT_READY in validate_release_candidate_status(_ready_input(release_candidate_ready=False)).risks
    assert PaperRuntimeValidationRisk.RUNTIME_EXECUTION_EVIDENCE_GAP in validate_runtime_execution_evidence(_ready_input(runtime_execution_evidence_ready=False)).risks
    assert PaperRuntimeValidationRisk.RUNTIME_TEST_EVIDENCE_GAP in validate_runtime_test_evidence(_ready_input(runtime_test_evidence_ready=False)).risks
    assert PaperRuntimeValidationRisk.EXTENDED_TEST_EVIDENCE_GAP in validate_extended_test_evidence(_ready_input(extended_test_evidence_ready=False)).risks
    assert PaperRuntimeValidationRisk.STABILIZATION_EVIDENCE_GAP in validate_stabilization_evidence(_ready_input(stabilization_evidence_ready=False)).risks
    assert PaperRuntimeValidationRisk.SAFETY_EVIDENCE_GAP in validate_safety_evidence(_ready_input(safety_evidence_ready=False)).risks
    assert PaperRuntimeValidationRisk.OBSERVABILITY_EVIDENCE_GAP in validate_observability_evidence(_ready_input(observability_evidence_ready=False)).risks
    assert PaperRuntimeValidationRisk.ROLLBACK_EVIDENCE_GAP in validate_rollback_evidence(_ready_input(rollback_evidence_ready=False)).risks
    assert PaperRuntimeValidationRisk.KILL_SWITCH_EVIDENCE_GAP in validate_kill_switch_evidence(_ready_input(kill_switch_evidence_ready=False)).risks
    assert PaperRuntimeValidationRisk.HUMAN_SUPERVISION_EVIDENCE_GAP in validate_human_supervision_evidence(_ready_input(human_supervision_evidence_ready=False)).risks
    assert PaperRuntimeValidationRisk.OPERATIONAL_BOUNDARY_VIOLATION in validate_operational_boundaries(_ready_input(operational_boundaries_validated=False)).risks


def test_detects_all_validation_risks():
    result = evaluate_paper_runtime_validation(
        _ready_input(
            release_candidate_ready=False,
            runtime_execution_evidence_ready=False,
            runtime_test_evidence_ready=False,
            extended_test_evidence_ready=False,
            stabilization_evidence_ready=False,
            safety_evidence_ready=False,
            observability_evidence_ready=False,
            rollback_evidence_ready=False,
            kill_switch_evidence_ready=False,
            human_supervision_evidence_ready=False,
            operational_boundaries_validated=False,
            validation_approval_requested=False,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(PaperRuntimeValidationRisk)
    assert result.state is PaperRuntimeValidationState.NOT_VALIDATED
    assert result.decision is PaperRuntimeValidationDecision.BLOCK_VALIDATION
    assert result.offline_only is False


def test_release_candidate_not_ready_requires_rc_fixes():
    result = evaluate_paper_runtime_validation(_ready_input(release_candidate_ready=False))

    assert result.decision is PaperRuntimeValidationDecision.REQUIRE_RELEASE_CANDIDATE_FIXES
    assert result.state is PaperRuntimeValidationState.VALIDATION_REVIEW_REQUIRED


def test_runtime_execution_gap_requires_execution_evidence():
    result = evaluate_paper_runtime_validation(_ready_input(runtime_execution_evidence_ready=False))

    assert result.decision is PaperRuntimeValidationDecision.REQUIRE_EXECUTION_EVIDENCE


def test_runtime_test_gap_requires_test_evidence():
    result = evaluate_paper_runtime_validation(_ready_input(runtime_test_evidence_ready=False))

    assert result.decision is PaperRuntimeValidationDecision.REQUIRE_TEST_EVIDENCE


def test_safety_gap_requires_safety_evidence():
    result = evaluate_paper_runtime_validation(_ready_input(safety_evidence_ready=False))

    assert result.decision is PaperRuntimeValidationDecision.REQUIRE_SAFETY_EVIDENCE


def test_premature_validation_caps_score_and_blocks():
    data = _ready_input(validation_approval_requested=False)
    risks = detect_validation_risks(data)
    score = compute_validation_score(data, risks)
    result = evaluate_paper_runtime_validation(data)

    assert PaperRuntimeValidationRisk.PREMATURE_VALIDATION_APPROVAL in risks
    assert score.overall_score <= 40
    assert result.decision is PaperRuntimeValidationDecision.BLOCK_VALIDATION


def test_upstream_network_leak_blocks_operational_boundaries():
    result = evaluate_paper_runtime_validation(
        _ready_input(paper_runtime_release_candidate=_upstream("READY_FOR_PAPER_RUNTIME_VALIDATION", risks=("NETWORK_LEAK",)))
    )

    assert PaperRuntimeValidationRisk.OPERATIONAL_BOUNDARY_VIOLATION in result.risks
    assert PaperRuntimeValidationRisk.PREMATURE_VALIDATION_APPROVAL in result.risks
    assert result.offline_only is False


def test_upstream_rollback_risk_is_detected():
    result = evaluate_paper_runtime_validation(_ready_input(rollback_verification=_upstream(risks=("ROLLBACK_FAILURE",))))

    assert PaperRuntimeValidationRisk.ROLLBACK_EVIDENCE_GAP in result.risks


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_validation_recommendations(
        (
            PaperRuntimeValidationRisk.RUNTIME_TEST_EVIDENCE_GAP,
            PaperRuntimeValidationRisk.RUNTIME_TEST_EVIDENCE_GAP,
            PaperRuntimeValidationRisk.KILL_SWITCH_EVIDENCE_GAP,
            PaperRuntimeValidationRisk.PREMATURE_VALIDATION_APPROVAL,
        ),
        PaperRuntimeValidationDecision.REQUIRE_TEST_EVIDENCE,
    )

    assert recommendations.count(PaperRuntimeValidationRecommendation.COMPLETE_RUNTIME_TEST_EVIDENCE) == 1
    assert PaperRuntimeValidationRecommendation.COMPLETE_KILL_SWITCH_EVIDENCE in recommendations
    assert PaperRuntimeValidationRecommendation.DELAY_VALIDATION_APPROVAL in recommendations
    assert PaperRuntimeValidationRecommendation.RUN_PAPER_RUNTIME_VALIDATION_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_validation_recommendations(
        (),
        PaperRuntimeValidationDecision.APPROVE_PAPER_RUNTIME_VALIDATION,
    )

    assert PaperRuntimeValidationRecommendation.APPROVE_OFFICIAL_PAPER_VALIDATION_REPORT in recommendations


def test_markdown_contains_decision_risks_and_recommendations():
    result = evaluate_paper_runtime_validation(_ready_input(kill_switch_evidence_ready=False))
    markdown = render_paper_runtime_validation_markdown(result)

    assert "# AGIcore Paper Runtime Validation" in markdown
    assert "Decision: REQUIRE_SAFETY_EVIDENCE" in markdown
    assert "# Validation Reviews" in markdown
    assert "KILL_SWITCH_EVIDENCE_GAP" in markdown
    assert "COMPLETE_KILL_SWITCH_EVIDENCE" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_paper_runtime_validation(_ready_input().__dict__)

    assert result.state is PaperRuntimeValidationState.READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (PaperRuntimeValidationRisk.RUNTIME_EXECUTION_EVIDENCE_GAP, PaperRuntimeValidationRecommendation.COMPLETE_RUNTIME_EXECUTION_EVIDENCE),
        (PaperRuntimeValidationRisk.OBSERVABILITY_EVIDENCE_GAP, PaperRuntimeValidationRecommendation.COMPLETE_OBSERVABILITY_EVIDENCE),
        (PaperRuntimeValidationRisk.HUMAN_SUPERVISION_EVIDENCE_GAP, PaperRuntimeValidationRecommendation.COMPLETE_HUMAN_SUPERVISION_EVIDENCE),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_validation_recommendations((risk,), PaperRuntimeValidationDecision.REQUIRE_TEST_EVIDENCE)


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "paper_runtime_validation.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
