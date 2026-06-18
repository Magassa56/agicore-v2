import ast
from pathlib import Path

import pytest

from agicore.trading.paper_broker_sandbox_session_review import (
    compute_broker_sandbox_review_score,
    detect_broker_sandbox_review_risks,
    evaluate_paper_broker_sandbox_session_review,
    generate_broker_sandbox_review_recommendations,
    render_paper_broker_sandbox_session_review_markdown,
    review_broker_sandbox_boundaries,
    review_broker_sandbox_scope,
    review_mock_to_broker_transition_readiness,
    review_paper_broker_adapter_requirements,
    review_sandbox_account_readiness,
    review_sandbox_connection_readiness,
    review_sandbox_human_supervision_readiness,
    review_sandbox_kill_switch_readiness,
    review_sandbox_observability_readiness,
    review_sandbox_order_readiness,
    review_sandbox_position_readiness,
    review_sandbox_preparation_readiness,
    review_sandbox_rollback_readiness,
)
from agicore.trading.paper_broker_sandbox_session_review_models import (
    PaperBrokerSandboxSessionReviewDecision,
    PaperBrokerSandboxSessionReviewInput,
    PaperBrokerSandboxSessionReviewRecommendation,
    PaperBrokerSandboxSessionReviewRisk,
    PaperBrokerSandboxSessionReviewState,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "risks": tuple(risks), "offline_only": True}
    if decision:
        payload["decision"] = decision
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_sandbox_session_preparation": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_SESSION_REVIEW",
            "APPROVE_PAPER_BROKER_SANDBOX_SESSION_PREPARATION",
        ),
        "paper_runtime_forward_test_plan": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_SESSION",
            "APPROVE_PAPER_RUNTIME_FORWARD_TEST_PLAN",
        ),
        "supervised_paper_runtime_trial": _upstream("READY_FOR_PAPER_RUNTIME_FORWARD_TEST_PLAN"),
        "official_paper_validation_report": _upstream("READY_FOR_SUPERVISED_PAPER_RUNTIME_TRIAL"),
        "paper_runtime_validation": _upstream("READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT"),
        "paper_runtime_release_candidate": _upstream("READY_FOR_PAPER_RUNTIME_VALIDATION"),
        "paper_trading_runtime": _upstream("COMPLETED"),
        "paper_broker_adapter": _upstream("READY_FOR_ALPACA_PAPER_ADAPTER"),
        "alpaca_paper_adapter": _upstream("READY_FOR_END_TO_END_PAPER"),
        "broker_paper_sandbox": _upstream("READY_FOR_ALPACA_PAPER_CONNECTIVITY"),
        "mock_alpaca_session": _upstream("READY_FOR_SIMULATED_MARKET_SESSION"),
        "mock_connectivity_layer": _upstream("READY_FOR_MOCK_ALPACA_SESSION"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "sandbox_preparation_approved": True,
        "sandbox_preparation_reviewed": True,
        "broker_sandbox_scope_reviewed": True,
        "broker_sandbox_scope_clear": True,
        "broker_sandbox_boundaries_reviewed": True,
        "broker_sandbox_boundaries_complete": True,
        "paper_broker_adapter_requirements_reviewed": True,
        "paper_broker_adapter_requirements_complete": True,
        "mock_to_broker_transition_reviewed": True,
        "mock_to_broker_transition_ready": True,
        "sandbox_connection_reviewed": True,
        "sandbox_connection_ready": True,
        "sandbox_order_reviewed": True,
        "sandbox_order_ready": True,
        "sandbox_position_reviewed": True,
        "sandbox_position_ready": True,
        "sandbox_account_reviewed": True,
        "sandbox_account_ready": True,
        "sandbox_observability_reviewed": True,
        "sandbox_observability_ready": True,
        "sandbox_rollback_reviewed": True,
        "sandbox_rollback_ready": True,
        "sandbox_kill_switch_reviewed": True,
        "sandbox_kill_switch_ready": True,
        "sandbox_human_supervision_reviewed": True,
        "sandbox_human_supervision_ready": True,
        "paper_broker_sandbox_session_requested": True,
        "sandbox_session_review_requested": True,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "no_real_broker": True,
        "no_alpaca_real": True,
        "no_api_key_read": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_api": True,
        "no_external_ml": True,
        "no_external_llm": True,
        "no_live_execution": True,
        "no_real_order": True,
    }
    payload.update(overrides)
    return PaperBrokerSandboxSessionReviewInput(**payload)


def test_evaluate_approves_paper_broker_sandbox_session_review():
    result = evaluate_paper_broker_sandbox_session_review(_ready_input())

    assert result.state is PaperBrokerSandboxSessionReviewState.READY_FOR_PAPER_BROKER_SANDBOX_SESSION
    assert result.decision is PaperBrokerSandboxSessionReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_SESSION
    assert result.risks == ()
    assert result.offline_only is True
    assert result.review_score == 100


def test_review_ready_state_below_final_session_threshold():
    result = evaluate_paper_broker_sandbox_session_review(
        _ready_input(
            sandbox_preparation_readiness_score=90,
            broker_sandbox_scope_score=90,
            broker_sandbox_boundaries_score=90,
            paper_broker_adapter_requirements_score=90,
            mock_to_broker_transition_readiness_score=90,
            sandbox_connection_readiness_score=90,
            sandbox_order_readiness_score=90,
            sandbox_position_readiness_score=90,
            sandbox_account_readiness_score=90,
            sandbox_observability_readiness_score=90,
            sandbox_rollback_readiness_score=90,
            sandbox_kill_switch_readiness_score=90,
            sandbox_human_supervision_readiness_score=90,
        )
    )

    assert result.state is PaperBrokerSandboxSessionReviewState.SANDBOX_SESSION_REVIEW_READY
    assert result.decision is PaperBrokerSandboxSessionReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_SESSION


def test_section_reviews_detect_primary_risks():
    assert PaperBrokerSandboxSessionReviewRisk.SANDBOX_PREPARATION_NOT_APPROVED in review_sandbox_preparation_readiness(_ready_input(sandbox_preparation_approved=False)).risks
    assert PaperBrokerSandboxSessionReviewRisk.SANDBOX_SCOPE_UNCLEAR in review_broker_sandbox_scope(_ready_input(broker_sandbox_scope_clear=False)).risks
    assert PaperBrokerSandboxSessionReviewRisk.SANDBOX_BOUNDARY_INCOMPLETE in review_broker_sandbox_boundaries(_ready_input(broker_sandbox_boundaries_complete=False)).risks
    assert PaperBrokerSandboxSessionReviewRisk.PAPER_BROKER_ADAPTER_REQUIREMENT_INCOMPLETE in review_paper_broker_adapter_requirements(_ready_input(paper_broker_adapter_requirements_complete=False)).risks
    assert PaperBrokerSandboxSessionReviewRisk.MOCK_TO_BROKER_TRANSITION_NOT_READY in review_mock_to_broker_transition_readiness(_ready_input(mock_to_broker_transition_ready=False)).risks
    assert PaperBrokerSandboxSessionReviewRisk.CONNECTION_READINESS_GAP in review_sandbox_connection_readiness(_ready_input(sandbox_connection_ready=False)).risks
    assert PaperBrokerSandboxSessionReviewRisk.ORDER_READINESS_GAP in review_sandbox_order_readiness(_ready_input(sandbox_order_ready=False)).risks
    assert PaperBrokerSandboxSessionReviewRisk.POSITION_READINESS_GAP in review_sandbox_position_readiness(_ready_input(sandbox_position_ready=False)).risks
    assert PaperBrokerSandboxSessionReviewRisk.ACCOUNT_READINESS_GAP in review_sandbox_account_readiness(_ready_input(sandbox_account_ready=False)).risks
    assert PaperBrokerSandboxSessionReviewRisk.OBSERVABILITY_READINESS_GAP in review_sandbox_observability_readiness(_ready_input(sandbox_observability_ready=False)).risks
    assert PaperBrokerSandboxSessionReviewRisk.ROLLBACK_READINESS_GAP in review_sandbox_rollback_readiness(_ready_input(sandbox_rollback_ready=False)).risks
    assert PaperBrokerSandboxSessionReviewRisk.KILL_SWITCH_READINESS_GAP in review_sandbox_kill_switch_readiness(_ready_input(sandbox_kill_switch_ready=False)).risks
    assert PaperBrokerSandboxSessionReviewRisk.HUMAN_SUPERVISION_READINESS_GAP in review_sandbox_human_supervision_readiness(_ready_input(sandbox_human_supervision_ready=False)).risks


def test_detects_all_broker_sandbox_review_risks():
    result = evaluate_paper_broker_sandbox_session_review(
        _ready_input(
            sandbox_preparation_approved=False,
            broker_sandbox_scope_clear=False,
            broker_sandbox_boundaries_complete=False,
            paper_broker_adapter_requirements_complete=False,
            mock_to_broker_transition_ready=False,
            sandbox_connection_ready=False,
            sandbox_order_ready=False,
            sandbox_position_ready=False,
            sandbox_account_ready=False,
            sandbox_observability_ready=False,
            sandbox_rollback_ready=False,
            sandbox_kill_switch_ready=False,
            sandbox_human_supervision_ready=False,
            paper_broker_sandbox_session_requested=False,
            sandbox_session_review_requested=False,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(PaperBrokerSandboxSessionReviewRisk)
    assert result.state is PaperBrokerSandboxSessionReviewState.NOT_READY
    assert result.decision is PaperBrokerSandboxSessionReviewDecision.BLOCK_PAPER_BROKER_SANDBOX_SESSION
    assert result.offline_only is False


def test_preparation_gap_requires_preparation_fixes_when_not_blocked():
    result = evaluate_paper_broker_sandbox_session_review(_ready_input(sandbox_preparation_approved=False))

    assert result.decision is PaperBrokerSandboxSessionReviewDecision.REQUIRE_PREPARATION_FIXES


def test_scope_and_boundary_gaps_require_boundary_fixes():
    assert evaluate_paper_broker_sandbox_session_review(_ready_input(broker_sandbox_scope_clear=False)).decision is PaperBrokerSandboxSessionReviewDecision.REQUIRE_BOUNDARY_FIXES
    assert evaluate_paper_broker_sandbox_session_review(_ready_input(broker_sandbox_boundaries_complete=False)).decision is PaperBrokerSandboxSessionReviewDecision.REQUIRE_BOUNDARY_FIXES


def test_adapter_and_transition_gaps_require_adapter_fixes():
    assert evaluate_paper_broker_sandbox_session_review(_ready_input(paper_broker_adapter_requirements_complete=False)).decision is PaperBrokerSandboxSessionReviewDecision.REQUIRE_ADAPTER_FIXES
    assert evaluate_paper_broker_sandbox_session_review(_ready_input(mock_to_broker_transition_ready=False)).decision is PaperBrokerSandboxSessionReviewDecision.REQUIRE_ADAPTER_FIXES


def test_connection_order_position_account_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_session_review(_ready_input(sandbox_connection_ready=False)).decision is PaperBrokerSandboxSessionReviewDecision.REQUIRE_CONNECTION_FIXES
    assert evaluate_paper_broker_sandbox_session_review(_ready_input(sandbox_order_ready=False)).decision is PaperBrokerSandboxSessionReviewDecision.REQUIRE_ORDER_FIXES
    assert evaluate_paper_broker_sandbox_session_review(_ready_input(sandbox_position_ready=False)).decision is PaperBrokerSandboxSessionReviewDecision.REQUIRE_POSITION_FIXES
    assert evaluate_paper_broker_sandbox_session_review(_ready_input(sandbox_account_ready=False)).decision is PaperBrokerSandboxSessionReviewDecision.REQUIRE_ACCOUNT_FIXES


def test_observability_rollback_kill_switch_and_supervision_decisions():
    assert evaluate_paper_broker_sandbox_session_review(_ready_input(sandbox_observability_ready=False)).decision is PaperBrokerSandboxSessionReviewDecision.REQUIRE_OBSERVABILITY_FIXES
    assert evaluate_paper_broker_sandbox_session_review(_ready_input(sandbox_rollback_ready=False)).decision is PaperBrokerSandboxSessionReviewDecision.REQUIRE_ROLLBACK_FIXES
    assert evaluate_paper_broker_sandbox_session_review(_ready_input(sandbox_kill_switch_ready=False)).decision is PaperBrokerSandboxSessionReviewDecision.REQUIRE_KILL_SWITCH_FIXES
    assert evaluate_paper_broker_sandbox_session_review(_ready_input(sandbox_human_supervision_ready=False)).decision is PaperBrokerSandboxSessionReviewDecision.REQUIRE_SUPERVISION_FIXES


def test_premature_sandbox_session_caps_score_and_blocks():
    data = _ready_input(paper_broker_sandbox_session_requested=False, sandbox_session_review_requested=False)
    risks = detect_broker_sandbox_review_risks(data)
    score = compute_broker_sandbox_review_score(data, risks)
    result = evaluate_paper_broker_sandbox_session_review(data)

    assert PaperBrokerSandboxSessionReviewRisk.PREMATURE_BROKER_SANDBOX_SESSION in risks
    assert score.overall_score <= 40
    assert result.decision is PaperBrokerSandboxSessionReviewDecision.BLOCK_PAPER_BROKER_SANDBOX_SESSION


def test_upstream_network_leak_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_session_review(
        _ready_input(paper_runtime_forward_test_plan=_upstream("READY_FOR_PAPER_BROKER_SANDBOX_SESSION", risks=("NETWORK_LEAK",)))
    )

    assert PaperBrokerSandboxSessionReviewRisk.SANDBOX_BOUNDARY_INCOMPLETE in result.risks
    assert PaperBrokerSandboxSessionReviewRisk.CONNECTION_READINESS_GAP in result.risks
    assert PaperBrokerSandboxSessionReviewRisk.PREMATURE_BROKER_SANDBOX_SESSION in result.risks
    assert result.offline_only is False


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_broker_sandbox_review_recommendations(
        (
            PaperBrokerSandboxSessionReviewRisk.KILL_SWITCH_READINESS_GAP,
            PaperBrokerSandboxSessionReviewRisk.KILL_SWITCH_READINESS_GAP,
            PaperBrokerSandboxSessionReviewRisk.OBSERVABILITY_READINESS_GAP,
            PaperBrokerSandboxSessionReviewRisk.PREMATURE_BROKER_SANDBOX_SESSION,
        ),
        PaperBrokerSandboxSessionReviewDecision.REQUIRE_KILL_SWITCH_FIXES,
    )

    assert recommendations.count(PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_SANDBOX_KILL_SWITCH_REVIEW) == 1
    assert PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_SANDBOX_OBSERVABILITY_REVIEW in recommendations
    assert PaperBrokerSandboxSessionReviewRecommendation.DELAY_PAPER_BROKER_SANDBOX_SESSION in recommendations
    assert PaperBrokerSandboxSessionReviewRecommendation.RUN_PAPER_BROKER_SANDBOX_SESSION_REVIEW_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_broker_sandbox_review_recommendations(
        (),
        PaperBrokerSandboxSessionReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_SESSION,
    )

    assert PaperBrokerSandboxSessionReviewRecommendation.APPROVE_PAPER_BROKER_SANDBOX_SESSION in recommendations


def test_markdown_contains_decision_risks_and_recommendations():
    result = evaluate_paper_broker_sandbox_session_review(_ready_input(sandbox_kill_switch_ready=False))
    markdown = render_paper_broker_sandbox_session_review_markdown(result)

    assert "# AGIcore Paper Broker Sandbox Session Review" in markdown
    assert "Decision: REQUIRE_KILL_SWITCH_FIXES" in markdown
    assert "KILL_SWITCH_READINESS_GAP" in markdown
    assert "COMPLETE_SANDBOX_KILL_SWITCH_REVIEW" in markdown


def test_mapping_inputs_are_supported_and_extra_keys_are_ignored():
    payload = dict(_ready_input().__dict__)
    payload["ignored_future_key"] = "ignored"
    result = evaluate_paper_broker_sandbox_session_review(payload)

    assert result.state is PaperBrokerSandboxSessionReviewState.READY_FOR_PAPER_BROKER_SANDBOX_SESSION


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (PaperBrokerSandboxSessionReviewRisk.CONNECTION_READINESS_GAP, PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_SANDBOX_CONNECTION_REVIEW),
        (PaperBrokerSandboxSessionReviewRisk.ORDER_READINESS_GAP, PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_SANDBOX_ORDER_REVIEW),
        (PaperBrokerSandboxSessionReviewRisk.POSITION_READINESS_GAP, PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_SANDBOX_POSITION_REVIEW),
        (PaperBrokerSandboxSessionReviewRisk.ACCOUNT_READINESS_GAP, PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_SANDBOX_ACCOUNT_REVIEW),
        (PaperBrokerSandboxSessionReviewRisk.HUMAN_SUPERVISION_READINESS_GAP, PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_SANDBOX_HUMAN_SUPERVISION_REVIEW),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_broker_sandbox_review_recommendations((risk,), PaperBrokerSandboxSessionReviewDecision.REQUIRE_ADAPTER_FIXES)


@pytest.mark.parametrize(
    "module_name",
    [
        "paper_broker_sandbox_session_review.py",
        "paper_broker_sandbox_session_review_models.py",
    ],
)
def test_module_keeps_offline_import_boundary(module_name):
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / module_name
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots

