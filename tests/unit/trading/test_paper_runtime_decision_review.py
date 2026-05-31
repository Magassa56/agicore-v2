import ast
from pathlib import Path

import pytest

from agicore.trading.paper_runtime_decision_review import (
    compute_decision_review_score,
    detect_decision_review_risks,
    evaluate_paper_runtime_decision_review,
    generate_decision_review_recommendations,
    render_paper_runtime_decision_review_markdown,
    review_duplicate_layers,
    review_human_supervision_chain,
    review_mock_to_paper_transition,
    review_module_coherence,
    review_observability_chain,
    review_rollback_chain,
    review_runtime_entrypoints,
    review_runtime_readiness_decision,
    review_safety_chain,
)
from agicore.trading.paper_runtime_decision_review_models import (
    PaperRuntimeDecision,
    PaperRuntimeDecisionRecommendation,
    PaperRuntimeDecisionReviewInput,
    PaperRuntimeDecisionReviewState,
    PaperRuntimeDecisionRisk,
)


def _upstream(state="READY", risks=(), blockers=()):
    return {"state": state, "risks": tuple(risks), "blockers": tuple(blockers), "offline_only": True}


def _ready_input(**overrides):
    payload = {
        "paper_runtime_pre_review": _upstream("READY_FOR_PAPER_TRADING_RUNTIME"),
        "full_paper_session": _upstream("READY_FOR_PAPER_TRADING_RUNTIME"),
        "simulated_market_session": _upstream("READY_FOR_FULL_PAPER_SESSION"),
        "mock_alpaca_session": _upstream("READY_FOR_SIMULATED_MARKET_SESSION"),
        "mock_connectivity_layer": _upstream("READY_FOR_MOCK_ALPACA_SESSION"),
        "alpaca_paper_connectivity_readiness": _upstream("READY_FOR_MOCK_CONNECTIVITY"),
        "broker_paper_sandbox": _upstream("READY_FOR_ALPACA_PAPER_CONNECTIVITY"),
        "paper_trading_end_to_end": _upstream("READY_FOR_PAPER_DRY_RUN"),
        "paper_dry_run": _upstream("READY_FOR_SUPERVISED_PAPER_TRIAL"),
        "supervised_paper_trial": _upstream("READY_FOR_BROKER_PAPER_SANDBOX"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "module_layers": ("pre_review", "full_paper", "simulated_market", "mock", "sandbox", "paper"),
        "coherent_module_chain": True,
        "runtime_entrypoints": ("evaluate_paper_trading_runtime", "render_paper_trading_runtime_markdown"),
        "runtime_entrypoints_required": ("evaluate_paper_trading_runtime", "render_paper_trading_runtime_markdown"),
        "safety_chain_links": ("safety_gate", "risk_management", "kill_switch"),
        "rollback_chain_links": ("checkpoint", "restore", "rollback"),
        "observability_chain_links": ("logs", "metrics", "traces", "alerts"),
        "human_supervision_links": ("human_approval", "operator_confirmation", "supervision"),
        "mock_to_paper_transition_links": ("mock_connectivity", "mock_alpaca", "broker_sandbox", "paper_runtime"),
        "integration_gaps": (),
        "runtime_scope_locked": True,
        "no_runtime_implementation_created": True,
        "design_review_approved": True,
        "runtime_creation_approved": True,
        "offline_mode_enforced": True,
        "no_real_broker": True,
        "no_api_key_read": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_api": True,
        "no_real_order": True,
        "module_coherence_score": 96,
        "duplicate_score": 96,
        "entrypoint_score": 96,
        "safety_chain_score": 96,
        "rollback_chain_score": 96,
        "observability_chain_score": 96,
        "human_supervision_score": 96,
        "mock_to_paper_transition_score": 96,
        "runtime_decision_score": 96,
    }
    payload.update(overrides)
    return PaperRuntimeDecisionReviewInput(**payload)


def test_evaluate_approves_paper_trading_runtime_creation():
    result = evaluate_paper_runtime_decision_review(_ready_input())

    assert result.state is PaperRuntimeDecisionReviewState.READY_FOR_PAPER_TRADING_RUNTIME
    assert result.decision is PaperRuntimeDecision.APPROVE_PAPER_TRADING_RUNTIME_CREATION
    assert result.risks == ()
    assert result.offline_only is True
    assert result.decision_review_score >= 94


def test_approves_design_when_creation_gate_is_not_set():
    result = evaluate_paper_runtime_decision_review(_ready_input(runtime_creation_approved=False))

    assert result.state is PaperRuntimeDecisionReviewState.READY_FOR_PAPER_RUNTIME_DESIGN
    assert result.decision is PaperRuntimeDecision.APPROVE_PAPER_RUNTIME_DESIGN


def test_review_functions_detect_each_chain_risk():
    assert PaperRuntimeDecisionRisk.MODULE_COHERENCE_GAP in review_module_coherence(_ready_input(coherent_module_chain=False)).risks
    assert PaperRuntimeDecisionRisk.DUPLICATE_LAYER_CONFLICT in review_duplicate_layers(_ready_input(duplicate_layers=("runtime_a",))).risks
    assert PaperRuntimeDecisionRisk.ENTRYPOINT_AMBIGUITY in review_runtime_entrypoints(_ready_input(runtime_entrypoints=())).risks
    assert PaperRuntimeDecisionRisk.SAFETY_CHAIN_INCOMPLETE in review_safety_chain(_ready_input(safety_chain_links=())).risks
    assert PaperRuntimeDecisionRisk.ROLLBACK_CHAIN_INCOMPLETE in review_rollback_chain(_ready_input(rollback_chain_links=())).risks
    assert PaperRuntimeDecisionRisk.OBSERVABILITY_CHAIN_INCOMPLETE in review_observability_chain(_ready_input(observability_chain_links=())).risks
    assert PaperRuntimeDecisionRisk.HUMAN_SUPERVISION_GAP in review_human_supervision_chain(_ready_input(human_supervision_links=())).risks
    assert PaperRuntimeDecisionRisk.MOCK_TO_PAPER_TRANSITION_GAP in review_mock_to_paper_transition(_ready_input(mock_to_paper_transition_links=())).risks


def test_runtime_readiness_detects_scope_and_premature_runtime_risks():
    review = review_runtime_readiness_decision(
        _ready_input(runtime_scope_locked=False, no_runtime_implementation_created=False)
    )

    assert PaperRuntimeDecisionRisk.RUNTIME_SCOPE_UNCLEAR in review.risks
    assert PaperRuntimeDecisionRisk.PREMATURE_RUNTIME_CREATION in review.risks


def test_detects_all_decision_review_risks():
    result = evaluate_paper_runtime_decision_review(
        _ready_input(
            module_layers=(),
            coherent_module_chain=False,
            duplicate_layers=("dup",),
            runtime_entrypoints=(),
            safety_chain_links=(),
            rollback_chain_links=(),
            observability_chain_links=(),
            human_supervision_links=(),
            mock_to_paper_transition_links=(),
            integration_gaps=("transition_missing",),
            runtime_scope_locked=False,
            no_runtime_implementation_created=False,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(PaperRuntimeDecisionRisk)
    assert result.state is PaperRuntimeDecisionReviewState.NOT_READY
    assert result.decision is PaperRuntimeDecision.BLOCK_RUNTIME_CREATION
    assert result.offline_only is False


def test_entrypoint_risk_requires_entrypoint_fixes():
    result = evaluate_paper_runtime_decision_review(_ready_input(runtime_entrypoints=()))

    assert result.decision is PaperRuntimeDecision.REQUIRE_ENTRYPOINT_FIXES
    assert PaperRuntimeDecisionRisk.ENTRYPOINT_AMBIGUITY in result.risks


def test_duplicate_risk_requires_duplicate_reduction():
    result = evaluate_paper_runtime_decision_review(_ready_input(duplicate_layers=("paper_runtime",)))

    assert result.decision is PaperRuntimeDecision.REQUIRE_DUPLICATE_REDUCTION
    assert PaperRuntimeDecisionRisk.DUPLICATE_LAYER_CONFLICT in result.risks


def test_integration_gap_blocks_by_integration_gaps():
    result = evaluate_paper_runtime_decision_review(
        _ready_input(safety_chain_links=(), rollback_chain_links=(), observability_chain_links=())
    )

    assert result.state is PaperRuntimeDecisionReviewState.BLOCKED_BY_INTEGRATION_GAPS
    assert result.decision is PaperRuntimeDecision.REQUIRE_INTEGRATION_CLEANUP


def test_hard_scope_risk_caps_score_and_blocks_creation():
    data = _ready_input(no_http_transport=False)
    risks = detect_decision_review_risks(data)
    score = compute_decision_review_score(data, risks)
    result = evaluate_paper_runtime_decision_review(data)

    assert PaperRuntimeDecisionRisk.RUNTIME_SCOPE_UNCLEAR in risks
    assert score.overall_score <= 40
    assert result.decision is PaperRuntimeDecision.BLOCK_RUNTIME_CREATION


def test_upstream_network_leak_closes_offline_boundary():
    result = evaluate_paper_runtime_decision_review(_ready_input(paper_runtime_pre_review=_upstream(risks=("NETWORK_LEAK",))))

    assert result.offline_only is False
    assert PaperRuntimeDecisionRisk.RUNTIME_SCOPE_UNCLEAR in result.risks


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_decision_review_recommendations(
        (
            PaperRuntimeDecisionRisk.ENTRYPOINT_AMBIGUITY,
            PaperRuntimeDecisionRisk.ENTRYPOINT_AMBIGUITY,
            PaperRuntimeDecisionRisk.ROLLBACK_CHAIN_INCOMPLETE,
            PaperRuntimeDecisionRisk.PREMATURE_RUNTIME_CREATION,
        ),
        PaperRuntimeDecision.REQUIRE_ENTRYPOINT_FIXES,
    )

    assert recommendations.count(PaperRuntimeDecisionRecommendation.CLARIFY_RUNTIME_ENTRYPOINTS) == 1
    assert PaperRuntimeDecisionRecommendation.COMPLETE_ROLLBACK_CHAIN in recommendations
    assert PaperRuntimeDecisionRecommendation.KEEP_RUNTIME_CREATION_BLOCKED in recommendations
    assert PaperRuntimeDecisionRecommendation.RUN_PAPER_RUNTIME_DECISION_REVIEW_SUITE in recommendations


def test_approval_recommendations_follow_decision():
    design = generate_decision_review_recommendations((), PaperRuntimeDecision.APPROVE_PAPER_RUNTIME_DESIGN)
    creation = generate_decision_review_recommendations((), PaperRuntimeDecision.APPROVE_PAPER_TRADING_RUNTIME_CREATION)

    assert PaperRuntimeDecisionRecommendation.APPROVE_RUNTIME_DESIGN_REVIEW in design
    assert PaperRuntimeDecisionRecommendation.APPROVE_RUNTIME_CREATION_AFTER_MANUAL_REVIEW in creation


def test_markdown_rendering_contains_decision_reviews_risks_and_recommendations():
    result = evaluate_paper_runtime_decision_review(_ready_input(runtime_entrypoints=()))
    markdown = render_paper_runtime_decision_review_markdown(result)

    assert "# AGIcore Paper Trading Runtime Decision Review" in markdown
    assert "Decision: REQUIRE_ENTRYPOINT_FIXES" in markdown
    assert "# Decision Reviews" in markdown
    assert "ENTRYPOINT_AMBIGUITY" in markdown
    assert "CLARIFY_RUNTIME_ENTRYPOINTS" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_paper_runtime_decision_review(_ready_input().__dict__)

    assert result.state is PaperRuntimeDecisionReviewState.READY_FOR_PAPER_TRADING_RUNTIME
    assert result.decision is PaperRuntimeDecision.APPROVE_PAPER_TRADING_RUNTIME_CREATION


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (PaperRuntimeDecisionRisk.MODULE_COHERENCE_GAP, PaperRuntimeDecisionRecommendation.REPAIR_MODULE_COHERENCE),
        (PaperRuntimeDecisionRisk.HUMAN_SUPERVISION_GAP, PaperRuntimeDecisionRecommendation.COMPLETE_HUMAN_SUPERVISION_CHAIN),
        (PaperRuntimeDecisionRisk.MOCK_TO_PAPER_TRANSITION_GAP, PaperRuntimeDecisionRecommendation.COMPLETE_MOCK_TO_PAPER_TRANSITION),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_decision_review_recommendations((risk,), PaperRuntimeDecision.REQUIRE_INTEGRATION_CLEANUP)


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "paper_runtime_decision_review.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
