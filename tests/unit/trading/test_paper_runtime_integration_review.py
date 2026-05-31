import ast
from pathlib import Path

import pytest

from agicore.trading.paper_runtime_integration_review import (
    compute_integration_review_score,
    detect_integration_review_risks,
    evaluate_paper_runtime_integration_review,
    generate_integration_review_recommendations,
    render_paper_runtime_integration_review_markdown,
    review_decision_review_alignment,
    review_full_session_alignment,
    review_human_supervision_integration,
    review_kill_switch_integration,
    review_mock_alpaca_alignment,
    review_mock_connectivity_alignment,
    review_observability_integration,
    review_rollback_integration,
    review_runtime_design_alignment,
    review_runtime_report_integration,
    review_simulated_market_alignment,
)
from agicore.trading.paper_runtime_integration_review_models import (
    PaperRuntimeIntegrationDecision,
    PaperRuntimeIntegrationRecommendation,
    PaperRuntimeIntegrationReviewInput,
    PaperRuntimeIntegrationReviewState,
    PaperRuntimeIntegrationRisk,
)


def _upstream(state="READY", decision=None, risks=()):
    payload = {"state": state, "risks": tuple(risks), "offline_only": True}
    if decision:
        payload["decision"] = decision
    return payload


def _runtime(state="COMPLETED", risks=(), offline_only=True, report=None):
    return {
        "state": state,
        "risks": tuple(risks),
        "offline_only": offline_only,
        "report": report or {"order_count": 1, "journal_count": 3, "observability_count": 5},
    }


def _ready_input(**overrides):
    payload = {
        "paper_trading_runtime": _runtime(),
        "paper_trading_runtime_design": _upstream("READY_FOR_RUNTIME_IMPLEMENTATION", "APPROVE_RUNTIME_IMPLEMENTATION"),
        "paper_runtime_decision_review": _upstream("READY_FOR_PAPER_TRADING_RUNTIME", "APPROVE_PAPER_TRADING_RUNTIME_CREATION"),
        "paper_runtime_pre_review": _upstream("READY_FOR_PAPER_TRADING_RUNTIME"),
        "full_paper_session": _upstream("READY_FOR_PAPER_TRADING_RUNTIME"),
        "simulated_market_session": _upstream("READY_FOR_FULL_PAPER_SESSION"),
        "mock_alpaca_session": _upstream("READY_FOR_SIMULATED_MARKET_SESSION"),
        "mock_connectivity_layer": _upstream("READY_FOR_MOCK_ALPACA_SESSION"),
        "alpaca_paper_connectivity_readiness": _upstream("READY_FOR_MOCK_CONNECTIVITY"),
        "broker_paper_sandbox": _upstream("READY_FOR_ALPACA_PAPER_CONNECTIVITY"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "runtime_entrypoint_present": True,
        "runtime_state_machine_aligned": True,
        "runtime_design_approved": True,
        "decision_review_approved": True,
        "full_session_chain_aligned": True,
        "simulated_market_chain_aligned": True,
        "mock_alpaca_chain_aligned": True,
        "mock_connectivity_chain_aligned": True,
        "observability_events_linked": True,
        "observability_reported": True,
        "rollback_hook_linked": True,
        "rollback_stop_state_supported": True,
        "kill_switch_hook_linked": True,
        "kill_switch_stop_state_supported": True,
        "human_supervision_hook_linked": True,
        "human_pause_state_supported": True,
        "runtime_report_available": True,
        "runtime_report_complete": True,
        "integration_scope_locked": True,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "no_real_broker": True,
        "no_api_key_read": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_api": True,
        "no_real_order": True,
        "ready_for_test_run": True,
        "runtime_design_alignment_score": 96,
        "decision_review_alignment_score": 96,
        "full_session_alignment_score": 96,
        "simulated_market_alignment_score": 96,
        "mock_alpaca_alignment_score": 96,
        "mock_connectivity_alignment_score": 96,
        "observability_integration_score": 96,
        "rollback_integration_score": 96,
        "kill_switch_integration_score": 96,
        "human_supervision_integration_score": 96,
        "runtime_report_score": 96,
    }
    payload.update(overrides)
    return PaperRuntimeIntegrationReviewInput(**payload)


def test_evaluate_ready_for_paper_runtime_test_run():
    result = evaluate_paper_runtime_integration_review(_ready_input())

    assert result.state is PaperRuntimeIntegrationReviewState.READY_FOR_PAPER_RUNTIME_TEST_RUN
    assert result.decision is PaperRuntimeIntegrationDecision.READY_FOR_PAPER_RUNTIME_TEST_RUN
    assert result.risks == ()
    assert result.offline_only is True
    assert result.integration_review_score >= 94


def test_integration_ready_without_test_run_gate():
    result = evaluate_paper_runtime_integration_review(_ready_input(ready_for_test_run=False))

    assert result.state is PaperRuntimeIntegrationReviewState.INTEGRATION_READY
    assert result.decision is PaperRuntimeIntegrationDecision.INTEGRATION_READY


def test_review_functions_detect_each_primary_risk():
    assert PaperRuntimeIntegrationRisk.RUNTIME_DESIGN_MISMATCH in review_runtime_design_alignment(_ready_input(runtime_entrypoint_present=False)).risks
    assert PaperRuntimeIntegrationRisk.DECISION_REVIEW_MISMATCH in review_decision_review_alignment(_ready_input(decision_review_approved=False)).risks
    assert PaperRuntimeIntegrationRisk.FULL_SESSION_MISMATCH in review_full_session_alignment(_ready_input(full_session_chain_aligned=False)).risks
    assert PaperRuntimeIntegrationRisk.SIMULATED_MARKET_MISMATCH in review_simulated_market_alignment(_ready_input(simulated_market_chain_aligned=False)).risks
    assert PaperRuntimeIntegrationRisk.MOCK_ALPACA_MISMATCH in review_mock_alpaca_alignment(_ready_input(mock_alpaca_chain_aligned=False)).risks
    assert PaperRuntimeIntegrationRisk.MOCK_CONNECTIVITY_MISMATCH in review_mock_connectivity_alignment(_ready_input(mock_connectivity_chain_aligned=False)).risks
    assert PaperRuntimeIntegrationRisk.OBSERVABILITY_INTEGRATION_GAP in review_observability_integration(_ready_input(observability_events_linked=False)).risks
    assert PaperRuntimeIntegrationRisk.ROLLBACK_INTEGRATION_GAP in review_rollback_integration(_ready_input(rollback_hook_linked=False)).risks
    assert PaperRuntimeIntegrationRisk.KILL_SWITCH_INTEGRATION_GAP in review_kill_switch_integration(_ready_input(kill_switch_hook_linked=False)).risks
    assert PaperRuntimeIntegrationRisk.HUMAN_SUPERVISION_INTEGRATION_GAP in review_human_supervision_integration(_ready_input(human_supervision_hook_linked=False)).risks
    assert PaperRuntimeIntegrationRisk.RUNTIME_REPORT_GAP in review_runtime_report_integration(_ready_input(runtime_report_available=False)).risks


def test_detects_all_integration_review_risks():
    result = evaluate_paper_runtime_integration_review(
        _ready_input(
            paper_trading_runtime=_runtime("FAILED_SAFE", risks=("NETWORK_LEAK",), offline_only=False, report=None),
            paper_trading_runtime_design=_upstream("NOT_READY"),
            paper_runtime_decision_review=_upstream("NOT_READY"),
            full_paper_session=_upstream("NOT_READY"),
            simulated_market_session=_upstream("NOT_READY"),
            mock_alpaca_session=_upstream("NOT_READY"),
            mock_connectivity_layer=_upstream("NOT_READY"),
            runtime_entrypoint_present=False,
            runtime_state_machine_aligned=False,
            runtime_design_approved=False,
            decision_review_approved=False,
            full_session_chain_aligned=False,
            simulated_market_chain_aligned=False,
            mock_alpaca_chain_aligned=False,
            mock_connectivity_chain_aligned=False,
            observability_events_linked=False,
            observability_reported=False,
            rollback_hook_linked=False,
            rollback_stop_state_supported=False,
            kill_switch_hook_linked=False,
            kill_switch_stop_state_supported=False,
            human_supervision_hook_linked=False,
            human_pause_state_supported=False,
            runtime_report_available=False,
            runtime_report_complete=False,
            integration_scope_locked=False,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(PaperRuntimeIntegrationRisk)
    assert result.state is PaperRuntimeIntegrationReviewState.NOT_READY
    assert result.decision is PaperRuntimeIntegrationDecision.INTEGRATION_BLOCKED
    assert result.offline_only is False


def test_scope_drift_caps_score_and_blocks():
    data = _ready_input(no_http_transport=False)
    risks = detect_integration_review_risks(data)
    score = compute_integration_review_score(data, risks)
    result = evaluate_paper_runtime_integration_review(data)

    assert PaperRuntimeIntegrationRisk.INTEGRATION_SCOPE_DRIFT in risks
    assert score.overall_score <= 40
    assert result.decision is PaperRuntimeIntegrationDecision.INTEGRATION_BLOCKED


def test_hard_mismatch_requires_cleanup():
    result = evaluate_paper_runtime_integration_review(_ready_input(kill_switch_hook_linked=False))

    assert result.state is PaperRuntimeIntegrationReviewState.REVIEW_REQUIRED
    assert result.decision is PaperRuntimeIntegrationDecision.INTEGRATION_CLEANUP_REQUIRED
    assert PaperRuntimeIntegrationRisk.KILL_SWITCH_INTEGRATION_GAP in result.risks


def test_soft_single_gap_is_partially_integrated():
    result = evaluate_paper_runtime_integration_review(
        _ready_input(mock_alpaca_chain_aligned=False, mock_alpaca_alignment_score=88)
    )

    assert result.state is PaperRuntimeIntegrationReviewState.PARTIALLY_INTEGRATED
    assert result.decision is PaperRuntimeIntegrationDecision.INTEGRATION_PARTIALLY_READY
    assert result.risks == (PaperRuntimeIntegrationRisk.MOCK_ALPACA_MISMATCH,)


def test_observability_requires_runtime_report_counts():
    result = evaluate_paper_runtime_integration_review(
        _ready_input(paper_trading_runtime=_runtime(report={"order_count": 1, "journal_count": 3, "observability_count": 0}))
    )

    assert PaperRuntimeIntegrationRisk.OBSERVABILITY_INTEGRATION_GAP in result.risks


def test_runtime_report_requires_journal_count():
    result = evaluate_paper_runtime_integration_review(
        _ready_input(paper_trading_runtime=_runtime(report={"order_count": 1, "journal_count": 0, "observability_count": 5}))
    )

    assert PaperRuntimeIntegrationRisk.RUNTIME_REPORT_GAP in result.risks


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_integration_review_recommendations(
        (
            PaperRuntimeIntegrationRisk.ROLLBACK_INTEGRATION_GAP,
            PaperRuntimeIntegrationRisk.ROLLBACK_INTEGRATION_GAP,
            PaperRuntimeIntegrationRisk.RUNTIME_REPORT_GAP,
            PaperRuntimeIntegrationRisk.INTEGRATION_SCOPE_DRIFT,
        ),
        PaperRuntimeIntegrationDecision.INTEGRATION_CLEANUP_REQUIRED,
    )

    assert recommendations.count(PaperRuntimeIntegrationRecommendation.REPAIR_ROLLBACK_INTEGRATION) == 1
    assert PaperRuntimeIntegrationRecommendation.COMPLETE_RUNTIME_REPORT in recommendations
    assert PaperRuntimeIntegrationRecommendation.LOCK_INTEGRATION_SCOPE in recommendations
    assert PaperRuntimeIntegrationRecommendation.RUN_INTEGRATION_REVIEW_SUITE in recommendations


def test_approval_recommendations_follow_decision():
    integration = generate_integration_review_recommendations((), PaperRuntimeIntegrationDecision.INTEGRATION_READY)
    test_run = generate_integration_review_recommendations((), PaperRuntimeIntegrationDecision.READY_FOR_PAPER_RUNTIME_TEST_RUN)

    assert PaperRuntimeIntegrationRecommendation.APPROVE_INTEGRATION_AFTER_MANUAL_REVIEW in integration
    assert PaperRuntimeIntegrationRecommendation.APPROVE_TEST_RUN_AFTER_MANUAL_REVIEW in test_run


def test_markdown_rendering_contains_decision_risks_and_recommendations():
    result = evaluate_paper_runtime_integration_review(_ready_input(rollback_hook_linked=False))
    markdown = render_paper_runtime_integration_review_markdown(result)

    assert "# AGIcore Paper Runtime Integration Review" in markdown
    assert "Decision: INTEGRATION_PARTIALLY_READY" in markdown
    assert "# Integration Reviews" in markdown
    assert "ROLLBACK_INTEGRATION_GAP" in markdown
    assert "REPAIR_ROLLBACK_INTEGRATION" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_paper_runtime_integration_review(_ready_input().__dict__)

    assert result.state is PaperRuntimeIntegrationReviewState.READY_FOR_PAPER_RUNTIME_TEST_RUN
    assert result.decision is PaperRuntimeIntegrationDecision.READY_FOR_PAPER_RUNTIME_TEST_RUN


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (PaperRuntimeIntegrationRisk.RUNTIME_DESIGN_MISMATCH, PaperRuntimeIntegrationRecommendation.ALIGN_RUNTIME_DESIGN),
        (PaperRuntimeIntegrationRisk.MOCK_CONNECTIVITY_MISMATCH, PaperRuntimeIntegrationRecommendation.ALIGN_MOCK_CONNECTIVITY),
        (PaperRuntimeIntegrationRisk.HUMAN_SUPERVISION_INTEGRATION_GAP, PaperRuntimeIntegrationRecommendation.REPAIR_HUMAN_SUPERVISION_INTEGRATION),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_integration_review_recommendations((risk,), PaperRuntimeIntegrationDecision.INTEGRATION_CLEANUP_REQUIRED)


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "paper_runtime_integration_review.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
