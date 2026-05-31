import ast
from pathlib import Path

import pytest

from agicore.trading.paper_runtime_pre_review import (
    compute_pre_review_score,
    detect_pre_review_risks,
    detect_runtime_duplicates,
    evaluate_paper_runtime_pre_review,
    generate_pre_review_recommendations,
    map_trading_modules,
    render_paper_runtime_pre_review_markdown,
    review_runtime_dependencies,
    review_runtime_entrypoints,
    review_runtime_integration_gaps,
)
from agicore.trading.paper_runtime_pre_review_models import (
    PaperRuntimePreReviewInput,
    PaperRuntimePreReviewRecommendation,
    PaperRuntimePreReviewRisk,
    PaperRuntimePreReviewState,
)


def _upstream(state="READY", score=96, risks=(), blockers=()):
    return {"state": state, "score": score, "risks": tuple(risks), "blockers": tuple(blockers), "offline_only": True}


def _ready_input(**overrides):
    modules = (
        "full_paper_session",
        "simulated_market_session",
        "mock_alpaca_session",
        "mock_connectivity_layer",
        "paper_trading_end_to_end",
        "paper_dry_run",
        "supervised_paper_trial",
        "observability_verification",
        "rollback_verification",
        "kill_switch_verification",
    )
    payload = {
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
        "trading_modules": modules,
        "runtime_candidates": ("paper_trading_runtime",),
        "dependencies_declared": ("full_paper_session", "observability", "rollback", "kill_switch"),
        "dependencies_required": ("full_paper_session", "observability", "rollback", "kill_switch"),
        "entrypoints_declared": ("evaluate_paper_trading_runtime", "render_paper_trading_runtime_markdown"),
        "entrypoints_required": ("evaluate_paper_trading_runtime", "render_paper_trading_runtime_markdown"),
        "integration_gaps": (),
        "observability_links": ("observability_verification",),
        "safety_links": ("risk_management", "safety_gate"),
        "rollback_links": ("rollback_verification",),
        "kill_switch_links": ("kill_switch_verification",),
        "runtime_scope_locked": True,
        "no_runtime_implementation_created": True,
        "offline_mode_enforced": True,
        "no_real_broker": True,
        "no_api_key_read": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_api": True,
        "no_real_order": True,
        "pre_review_validated": True,
        "ready_for_paper_trading_runtime": True,
        "module_map_score": 96,
        "duplicate_score": 96,
        "dependency_score": 96,
        "entrypoint_score": 96,
        "integration_score": 96,
    }
    payload.update(overrides)
    return PaperRuntimePreReviewInput(**payload)


def test_evaluate_ready_for_paper_trading_runtime():
    result = evaluate_paper_runtime_pre_review(_ready_input())

    assert result.state is PaperRuntimePreReviewState.READY_FOR_PAPER_TRADING_RUNTIME
    assert result.risks == ()
    assert result.offline_only is True
    assert result.pre_review_score >= 94


def test_runtime_pre_review_ready_without_runtime_gate():
    result = evaluate_paper_runtime_pre_review(_ready_input(ready_for_paper_trading_runtime=False))

    assert result.state is PaperRuntimePreReviewState.RUNTIME_PRE_REVIEW_READY
    assert result.risks == ()


def test_module_mapping_detects_incomplete_map():
    module_map = map_trading_modules(_ready_input(trading_modules=("full_paper_session",), module_map_score=None))

    assert PaperRuntimePreReviewRisk.MODULE_MAP_INCOMPLETE in module_map.risks
    assert "simulated_market_session" in module_map.missing_expected_modules


def test_duplicate_runtime_layer_detection():
    review = detect_runtime_duplicates(
        _ready_input(runtime_candidates=("paper_trading_runtime", "paper_runtime"), duplicate_score=None)
    )

    assert review.passed is False
    assert review.risks == (PaperRuntimePreReviewRisk.DUPLICATE_RUNTIME_LAYER,)


def test_dependency_entrypoint_and_integration_reviews_detect_gaps():
    dependency = review_runtime_dependencies(
        _ready_input(dependencies_declared=("full_paper_session",), dependency_score=None)
    )
    entrypoint = review_runtime_entrypoints(_ready_input(entrypoints_declared=(), entrypoint_score=None))
    integration = review_runtime_integration_gaps(
        _ready_input(observability_links=(), safety_links=(), rollback_links=(), kill_switch_links=())
    )

    assert PaperRuntimePreReviewRisk.DEPENDENCY_GAP in dependency.risks
    assert PaperRuntimePreReviewRisk.ENTRYPOINT_MISSING in entrypoint.risks
    assert PaperRuntimePreReviewRisk.OBSERVABILITY_GAP in integration.risks
    assert PaperRuntimePreReviewRisk.SAFETY_LINK_MISSING in integration.risks
    assert PaperRuntimePreReviewRisk.ROLLBACK_LINK_MISSING in integration.risks
    assert PaperRuntimePreReviewRisk.KILL_SWITCH_LINK_MISSING in integration.risks


def test_detects_all_pre_review_risks():
    data = _ready_input(
        trading_modules=(),
        runtime_candidates=("paper_runtime_a", "paper_runtime_b"),
        dependencies_declared=(),
        entrypoints_declared=(),
        integration_gaps=("adapter_contract_missing",),
        observability_links=(),
        safety_links=(),
        rollback_links=(),
        kill_switch_links=(),
        runtime_scope_locked=False,
        no_runtime_implementation_created=False,
        no_http_transport=False,
    )

    result = evaluate_paper_runtime_pre_review(data)

    assert set(result.risks) == set(PaperRuntimePreReviewRisk)
    assert result.state is PaperRuntimePreReviewState.NOT_READY
    assert result.offline_only is False


def test_single_soft_risk_is_partially_ready():
    result = evaluate_paper_runtime_pre_review(
        _ready_input(
            dependencies_declared=("full_paper_session", "observability", "rollback"),
            dependency_score=88,
        )
    )

    assert result.state is PaperRuntimePreReviewState.PARTIALLY_READY
    assert result.risks == (PaperRuntimePreReviewRisk.DEPENDENCY_GAP,)


def test_hard_risk_caps_score_and_not_ready():
    data = _ready_input(no_http_transport=False)
    risks = detect_pre_review_risks(data)
    score = compute_pre_review_score(data, risks)
    result = evaluate_paper_runtime_pre_review(data)

    assert PaperRuntimePreReviewRisk.RUNTIME_SCOPE_DRIFT in risks
    assert score.overall_score <= 40
    assert result.state is PaperRuntimePreReviewState.NOT_READY


def test_upstream_network_leak_closes_offline_boundary():
    result = evaluate_paper_runtime_pre_review(_ready_input(full_paper_session=_upstream(risks=("NETWORK_LEAK",))))

    assert result.state is PaperRuntimePreReviewState.NOT_READY
    assert result.offline_only is False
    assert PaperRuntimePreReviewRisk.RUNTIME_SCOPE_DRIFT in result.risks


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_pre_review_recommendations(
        (
            PaperRuntimePreReviewRisk.DEPENDENCY_GAP,
            PaperRuntimePreReviewRisk.DEPENDENCY_GAP,
            PaperRuntimePreReviewRisk.KILL_SWITCH_LINK_MISSING,
            PaperRuntimePreReviewRisk.RUNTIME_SCOPE_DRIFT,
        ),
        PaperRuntimePreReviewState.REVIEW_REQUIRED,
    )

    assert recommendations.count(PaperRuntimePreReviewRecommendation.RESOLVE_RUNTIME_DEPENDENCIES) == 1
    assert PaperRuntimePreReviewRecommendation.LINK_RUNTIME_KILL_SWITCH in recommendations
    assert PaperRuntimePreReviewRecommendation.FREEZE_RUNTIME_SCOPE in recommendations
    assert PaperRuntimePreReviewRecommendation.RUN_PAPER_RUNTIME_PRE_REVIEW_SUITE in recommendations


def test_ready_state_adds_runtime_implementation_approval():
    result = evaluate_paper_runtime_pre_review(_ready_input())

    assert PaperRuntimePreReviewRecommendation.APPROVE_PAPER_TRADING_RUNTIME_IMPLEMENTATION in result.recommendations


def test_markdown_rendering_contains_reviews_risks_and_recommendations():
    result = evaluate_paper_runtime_pre_review(_ready_input(entrypoints_declared=()))
    markdown = render_paper_runtime_pre_review_markdown(result)

    assert "# AGIcore Paper Trading Runtime Pre-Review" in markdown
    assert "# Trading Module Map" in markdown
    assert "# Runtime Reviews" in markdown
    assert "ENTRYPOINT_MISSING" in markdown
    assert "DEFINE_RUNTIME_ENTRYPOINTS" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_paper_runtime_pre_review(_ready_input().__dict__)

    assert result.state is PaperRuntimePreReviewState.READY_FOR_PAPER_TRADING_RUNTIME
    assert result.pre_review_score >= 94


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (PaperRuntimePreReviewRisk.MODULE_MAP_INCOMPLETE, PaperRuntimePreReviewRecommendation.COMPLETE_TRADING_MODULE_MAP),
        (PaperRuntimePreReviewRisk.INTEGRATION_GAP, PaperRuntimePreReviewRecommendation.CLOSE_RUNTIME_INTEGRATION_GAPS),
        (PaperRuntimePreReviewRisk.ROLLBACK_LINK_MISSING, PaperRuntimePreReviewRecommendation.LINK_RUNTIME_ROLLBACK),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_pre_review_recommendations((risk,), PaperRuntimePreReviewState.PARTIALLY_READY)


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "paper_runtime_pre_review.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
