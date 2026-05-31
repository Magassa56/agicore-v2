import ast
from pathlib import Path

import pytest

from agicore.trading.official_paper_validation_report import (
    collect_extended_test_evidence,
    collect_human_supervision_evidence,
    collect_integration_review_evidence,
    collect_kill_switch_evidence,
    collect_observability_evidence,
    collect_operational_boundary_evidence,
    collect_release_candidate_evidence,
    collect_rollback_evidence,
    collect_runtime_creation_evidence,
    collect_runtime_validation_evidence,
    collect_safety_evidence,
    collect_stabilization_evidence,
    collect_test_run_evidence,
    compute_official_report_score,
    detect_official_report_risks,
    generate_official_paper_validation_report,
    generate_official_report_recommendations,
    render_official_paper_validation_report_markdown,
)
from agicore.trading.official_paper_validation_report_models import (
    OfficialPaperValidationReportDecision,
    OfficialPaperValidationReportInput,
    OfficialPaperValidationReportRecommendation,
    OfficialPaperValidationReportRisk,
    OfficialPaperValidationReportState,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {
        "state": state,
        "risks": tuple(risks),
        "offline_only": True,
        "validation_score": 100,
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
        "paper_runtime_validation": _upstream("READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT", "APPROVE_PAPER_RUNTIME_VALIDATION"),
        "paper_runtime_release_candidate": _upstream("READY_FOR_PAPER_RUNTIME_VALIDATION", "APPROVE_PAPER_RUNTIME_RELEASE_CANDIDATE"),
        "paper_runtime_stabilization_review": _upstream("READY_FOR_PAPER_RUNTIME_RELEASE_CANDIDATE", "APPROVE_RELEASE_CANDIDATE_PREPARATION"),
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
        "runtime_creation_evidence_ready": True,
        "integration_review_evidence_ready": True,
        "test_run_evidence_ready": True,
        "extended_test_evidence_ready": True,
        "stabilization_evidence_ready": True,
        "release_candidate_evidence_ready": True,
        "runtime_validation_evidence_ready": True,
        "safety_evidence_ready": True,
        "observability_evidence_ready": True,
        "rollback_evidence_ready": True,
        "kill_switch_evidence_ready": True,
        "human_supervision_evidence_ready": True,
        "operational_boundary_evidence_ready": True,
        "supervised_trial_requested": True,
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
    return OfficialPaperValidationReportInput(**payload)


def test_generate_report_approves_supervised_paper_runtime_trial():
    result = generate_official_paper_validation_report(_ready_input())

    assert result.state is OfficialPaperValidationReportState.READY_FOR_SUPERVISED_PAPER_RUNTIME_TRIAL
    assert result.decision is OfficialPaperValidationReportDecision.APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL
    assert result.risks == ()
    assert result.offline_only is True
    assert result.report_score == 100


def test_report_ready_when_score_below_supervised_trial_threshold():
    result = generate_official_paper_validation_report(
        _ready_input(
            runtime_creation_evidence_score=90,
            integration_review_evidence_score=90,
            test_run_evidence_score=90,
            extended_test_evidence_score=90,
            stabilization_evidence_score=90,
            release_candidate_evidence_score=90,
            runtime_validation_evidence_score=90,
            safety_evidence_score=90,
            observability_evidence_score=90,
            rollback_evidence_score=90,
            kill_switch_evidence_score=90,
            human_supervision_evidence_score=90,
            operational_boundary_evidence_score=90,
        )
    )

    assert result.state is OfficialPaperValidationReportState.REPORT_READY
    assert result.decision is OfficialPaperValidationReportDecision.APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL


def test_collectors_detect_each_primary_risk():
    assert OfficialPaperValidationReportRisk.RUNTIME_CREATION_EVIDENCE_MISSING in collect_runtime_creation_evidence(_ready_input(runtime_creation_evidence_ready=False)).risks
    assert OfficialPaperValidationReportRisk.INTEGRATION_EVIDENCE_MISSING in collect_integration_review_evidence(_ready_input(integration_review_evidence_ready=False)).risks
    assert OfficialPaperValidationReportRisk.TEST_RUN_EVIDENCE_MISSING in collect_test_run_evidence(_ready_input(test_run_evidence_ready=False)).risks
    assert OfficialPaperValidationReportRisk.EXTENDED_TEST_EVIDENCE_MISSING in collect_extended_test_evidence(_ready_input(extended_test_evidence_ready=False)).risks
    assert OfficialPaperValidationReportRisk.STABILIZATION_EVIDENCE_MISSING in collect_stabilization_evidence(_ready_input(stabilization_evidence_ready=False)).risks
    assert OfficialPaperValidationReportRisk.RELEASE_CANDIDATE_EVIDENCE_MISSING in collect_release_candidate_evidence(_ready_input(release_candidate_evidence_ready=False)).risks
    assert OfficialPaperValidationReportRisk.VALIDATION_EVIDENCE_MISSING in collect_runtime_validation_evidence(_ready_input(runtime_validation_evidence_ready=False)).risks
    assert OfficialPaperValidationReportRisk.SAFETY_EVIDENCE_MISSING in collect_safety_evidence(_ready_input(safety_evidence_ready=False)).risks
    assert OfficialPaperValidationReportRisk.OBSERVABILITY_EVIDENCE_MISSING in collect_observability_evidence(_ready_input(observability_evidence_ready=False)).risks
    assert OfficialPaperValidationReportRisk.ROLLBACK_EVIDENCE_MISSING in collect_rollback_evidence(_ready_input(rollback_evidence_ready=False)).risks
    assert OfficialPaperValidationReportRisk.KILL_SWITCH_EVIDENCE_MISSING in collect_kill_switch_evidence(_ready_input(kill_switch_evidence_ready=False)).risks
    assert OfficialPaperValidationReportRisk.HUMAN_SUPERVISION_EVIDENCE_MISSING in collect_human_supervision_evidence(_ready_input(human_supervision_evidence_ready=False)).risks
    assert OfficialPaperValidationReportRisk.OPERATIONAL_BOUNDARY_EVIDENCE_MISSING in collect_operational_boundary_evidence(_ready_input(operational_boundary_evidence_ready=False)).risks


def test_detects_all_official_report_risks():
    result = generate_official_paper_validation_report(
        _ready_input(
            runtime_creation_evidence_ready=False,
            integration_review_evidence_ready=False,
            test_run_evidence_ready=False,
            extended_test_evidence_ready=False,
            stabilization_evidence_ready=False,
            release_candidate_evidence_ready=False,
            runtime_validation_evidence_ready=False,
            safety_evidence_ready=False,
            observability_evidence_ready=False,
            rollback_evidence_ready=False,
            kill_switch_evidence_ready=False,
            human_supervision_evidence_ready=False,
            operational_boundary_evidence_ready=False,
            supervised_trial_requested=False,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(OfficialPaperValidationReportRisk)
    assert result.state is OfficialPaperValidationReportState.REPORT_NOT_READY
    assert result.decision is OfficialPaperValidationReportDecision.BLOCK_SUPERVISED_TRIAL
    assert result.offline_only is False


def test_validation_evidence_gap_requires_report_completion():
    result = generate_official_paper_validation_report(_ready_input(runtime_validation_evidence_ready=False))

    assert result.decision is OfficialPaperValidationReportDecision.REQUIRE_REPORT_COMPLETION
    assert result.state is OfficialPaperValidationReportState.REPORT_REVIEW_REQUIRED


def test_boundary_gap_requires_boundary_fixes():
    result = generate_official_paper_validation_report(_ready_input(operational_boundary_evidence_ready=False))

    assert result.decision is OfficialPaperValidationReportDecision.REQUIRE_BOUNDARY_FIXES


def test_test_run_gap_requires_evidence_fixes():
    result = generate_official_paper_validation_report(_ready_input(test_run_evidence_ready=False))

    assert result.decision is OfficialPaperValidationReportDecision.REQUIRE_EVIDENCE_FIXES


def test_premature_supervised_trial_caps_score_and_blocks():
    data = _ready_input(supervised_trial_requested=False)
    risks = detect_official_report_risks(data)
    score = compute_official_report_score(data, risks)
    result = generate_official_paper_validation_report(data)

    assert OfficialPaperValidationReportRisk.PREMATURE_SUPERVISED_TRIAL in risks
    assert score.overall_score <= 40
    assert result.decision is OfficialPaperValidationReportDecision.BLOCK_SUPERVISED_TRIAL


def test_upstream_network_leak_breaks_operational_boundary_evidence():
    result = generate_official_paper_validation_report(
        _ready_input(paper_runtime_validation=_upstream("READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT", risks=("NETWORK_LEAK",)))
    )

    assert OfficialPaperValidationReportRisk.OPERATIONAL_BOUNDARY_EVIDENCE_MISSING in result.risks
    assert OfficialPaperValidationReportRisk.PREMATURE_SUPERVISED_TRIAL in result.risks
    assert result.offline_only is False


def test_upstream_rollback_risk_is_detected():
    result = generate_official_paper_validation_report(_ready_input(rollback_verification=_upstream(risks=("ROLLBACK_FAILURE",))))

    assert OfficialPaperValidationReportRisk.ROLLBACK_EVIDENCE_MISSING in result.risks


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_official_report_recommendations(
        (
            OfficialPaperValidationReportRisk.TEST_RUN_EVIDENCE_MISSING,
            OfficialPaperValidationReportRisk.TEST_RUN_EVIDENCE_MISSING,
            OfficialPaperValidationReportRisk.KILL_SWITCH_EVIDENCE_MISSING,
            OfficialPaperValidationReportRisk.PREMATURE_SUPERVISED_TRIAL,
        ),
        OfficialPaperValidationReportDecision.REQUIRE_EVIDENCE_FIXES,
    )

    assert recommendations.count(OfficialPaperValidationReportRecommendation.COMPLETE_TEST_RUN_EVIDENCE) == 1
    assert OfficialPaperValidationReportRecommendation.COMPLETE_KILL_SWITCH_EVIDENCE in recommendations
    assert OfficialPaperValidationReportRecommendation.DELAY_SUPERVISED_TRIAL in recommendations
    assert OfficialPaperValidationReportRecommendation.RUN_OFFICIAL_REPORT_REVIEW_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_official_report_recommendations(
        (),
        OfficialPaperValidationReportDecision.APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL,
    )

    assert OfficialPaperValidationReportRecommendation.APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL in recommendations


def test_markdown_contains_decision_risks_and_recommendations():
    result = generate_official_paper_validation_report(_ready_input(kill_switch_evidence_ready=False))
    markdown = render_official_paper_validation_report_markdown(result)

    assert "# AGIcore Official Paper Validation Report" in markdown
    assert "Decision: REQUIRE_EVIDENCE_FIXES" in markdown
    assert "# Consolidated Evidence" in markdown
    assert "KILL_SWITCH_EVIDENCE_MISSING" in markdown
    assert "COMPLETE_KILL_SWITCH_EVIDENCE" in markdown


def test_mapping_inputs_are_supported():
    result = generate_official_paper_validation_report(_ready_input().__dict__)

    assert result.state is OfficialPaperValidationReportState.READY_FOR_SUPERVISED_PAPER_RUNTIME_TRIAL


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (OfficialPaperValidationReportRisk.RUNTIME_CREATION_EVIDENCE_MISSING, OfficialPaperValidationReportRecommendation.COMPLETE_RUNTIME_CREATION_EVIDENCE),
        (OfficialPaperValidationReportRisk.OBSERVABILITY_EVIDENCE_MISSING, OfficialPaperValidationReportRecommendation.COMPLETE_OBSERVABILITY_EVIDENCE),
        (OfficialPaperValidationReportRisk.HUMAN_SUPERVISION_EVIDENCE_MISSING, OfficialPaperValidationReportRecommendation.COMPLETE_HUMAN_SUPERVISION_EVIDENCE),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_official_report_recommendations((risk,), OfficialPaperValidationReportDecision.REQUIRE_EVIDENCE_FIXES)


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "official_paper_validation_report.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
