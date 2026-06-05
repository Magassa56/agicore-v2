import ast
from pathlib import Path

import pytest

from agicore.trading.paper_broker_sandbox_session_preparation import (
    compute_broker_sandbox_preparation_score,
    define_broker_sandbox_session_boundaries,
    define_broker_sandbox_session_scope,
    define_mock_to_broker_transition_requirements,
    define_paper_broker_adapter_requirements,
    define_sandbox_account_preconditions,
    define_sandbox_connection_preconditions,
    define_sandbox_human_supervision_requirements,
    define_sandbox_kill_switch_requirements,
    define_sandbox_observability_requirements,
    define_sandbox_order_preconditions,
    define_sandbox_position_preconditions,
    define_sandbox_rollback_requirements,
    detect_broker_sandbox_preparation_risks,
    evaluate_paper_broker_sandbox_session_preparation,
    generate_broker_sandbox_preparation_recommendations,
    render_paper_broker_sandbox_session_preparation_markdown,
    review_forward_test_plan_readiness,
)
from agicore.trading.paper_broker_sandbox_session_preparation_models import (
    PaperBrokerSandboxSessionPreparationDecision,
    PaperBrokerSandboxSessionPreparationInput,
    PaperBrokerSandboxSessionPreparationRecommendation,
    PaperBrokerSandboxSessionPreparationRisk,
    PaperBrokerSandboxSessionPreparationState,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "risks": tuple(risks), "offline_only": True}
    if decision:
        payload["decision"] = decision
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
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
        "forward_test_plan_approved": True,
        "sandbox_session_scope_defined": True,
        "sandbox_session_boundaries_defined": True,
        "paper_broker_adapter_requirements_defined": True,
        "mock_to_broker_transition_requirements_defined": True,
        "sandbox_connection_preconditions_defined": True,
        "sandbox_order_preconditions_defined": True,
        "sandbox_position_preconditions_defined": True,
        "sandbox_account_preconditions_defined": True,
        "sandbox_observability_requirements_defined": True,
        "sandbox_rollback_requirements_defined": True,
        "sandbox_kill_switch_requirements_defined": True,
        "sandbox_human_supervision_requirements_defined": True,
        "sandbox_session_requested": True,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "no_real_broker": True,
        "no_alpaca_real": True,
        "no_api_key_read": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_api": True,
        "no_real_order": True,
    }
    payload.update(overrides)
    return PaperBrokerSandboxSessionPreparationInput(**payload)


def test_evaluate_approves_broker_sandbox_session_preparation():
    result = evaluate_paper_broker_sandbox_session_preparation(_ready_input())

    assert result.state is PaperBrokerSandboxSessionPreparationState.READY_FOR_PAPER_BROKER_SANDBOX_SESSION_REVIEW
    assert result.decision is PaperBrokerSandboxSessionPreparationDecision.APPROVE_PAPER_BROKER_SANDBOX_SESSION_PREPARATION
    assert result.risks == ()
    assert result.offline_only is True
    assert result.preparation_score == 100


def test_prepared_state_below_review_threshold():
    result = evaluate_paper_broker_sandbox_session_preparation(
        _ready_input(
            forward_test_plan_readiness_score=90,
            sandbox_session_scope_score=90,
            sandbox_session_boundaries_score=90,
            paper_broker_adapter_requirements_score=90,
            mock_to_broker_transition_requirements_score=90,
            sandbox_connection_preconditions_score=90,
            sandbox_order_preconditions_score=90,
            sandbox_position_preconditions_score=90,
            sandbox_account_preconditions_score=90,
            sandbox_observability_requirements_score=90,
            sandbox_rollback_requirements_score=90,
            sandbox_kill_switch_requirements_score=90,
            sandbox_human_supervision_requirements_score=90,
        )
    )

    assert result.state is PaperBrokerSandboxSessionPreparationState.SANDBOX_SESSION_PREPARED
    assert result.decision is PaperBrokerSandboxSessionPreparationDecision.APPROVE_PAPER_BROKER_SANDBOX_SESSION_PREPARATION


def test_section_builders_detect_primary_risks():
    assert PaperBrokerSandboxSessionPreparationRisk.FORWARD_TEST_PLAN_NOT_APPROVED in review_forward_test_plan_readiness(_ready_input(forward_test_plan_approved=False)).risks
    assert PaperBrokerSandboxSessionPreparationRisk.SANDBOX_SCOPE_UNCLEAR in define_broker_sandbox_session_scope(_ready_input(sandbox_session_scope_defined=False)).risks
    assert PaperBrokerSandboxSessionPreparationRisk.SANDBOX_BOUNDARY_GAP in define_broker_sandbox_session_boundaries(_ready_input(sandbox_session_boundaries_defined=False)).risks
    assert PaperBrokerSandboxSessionPreparationRisk.PAPER_BROKER_ADAPTER_REQUIREMENT_GAP in define_paper_broker_adapter_requirements(_ready_input(paper_broker_adapter_requirements_defined=False)).risks
    assert PaperBrokerSandboxSessionPreparationRisk.MOCK_TO_BROKER_TRANSITION_GAP in define_mock_to_broker_transition_requirements(_ready_input(mock_to_broker_transition_requirements_defined=False)).risks
    assert PaperBrokerSandboxSessionPreparationRisk.CONNECTION_PRECONDITION_GAP in define_sandbox_connection_preconditions(_ready_input(sandbox_connection_preconditions_defined=False)).risks
    assert PaperBrokerSandboxSessionPreparationRisk.ORDER_PRECONDITION_GAP in define_sandbox_order_preconditions(_ready_input(sandbox_order_preconditions_defined=False)).risks
    assert PaperBrokerSandboxSessionPreparationRisk.POSITION_PRECONDITION_GAP in define_sandbox_position_preconditions(_ready_input(sandbox_position_preconditions_defined=False)).risks
    assert PaperBrokerSandboxSessionPreparationRisk.ACCOUNT_PRECONDITION_GAP in define_sandbox_account_preconditions(_ready_input(sandbox_account_preconditions_defined=False)).risks
    assert PaperBrokerSandboxSessionPreparationRisk.OBSERVABILITY_REQUIREMENT_GAP in define_sandbox_observability_requirements(_ready_input(sandbox_observability_requirements_defined=False)).risks
    assert PaperBrokerSandboxSessionPreparationRisk.ROLLBACK_REQUIREMENT_GAP in define_sandbox_rollback_requirements(_ready_input(sandbox_rollback_requirements_defined=False)).risks
    assert PaperBrokerSandboxSessionPreparationRisk.KILL_SWITCH_REQUIREMENT_GAP in define_sandbox_kill_switch_requirements(_ready_input(sandbox_kill_switch_requirements_defined=False)).risks
    assert PaperBrokerSandboxSessionPreparationRisk.HUMAN_SUPERVISION_REQUIREMENT_GAP in define_sandbox_human_supervision_requirements(_ready_input(sandbox_human_supervision_requirements_defined=False)).risks


def test_detects_all_broker_sandbox_preparation_risks():
    result = evaluate_paper_broker_sandbox_session_preparation(
        _ready_input(
            forward_test_plan_approved=False,
            sandbox_session_scope_defined=False,
            sandbox_session_boundaries_defined=False,
            paper_broker_adapter_requirements_defined=False,
            mock_to_broker_transition_requirements_defined=False,
            sandbox_connection_preconditions_defined=False,
            sandbox_order_preconditions_defined=False,
            sandbox_position_preconditions_defined=False,
            sandbox_account_preconditions_defined=False,
            sandbox_observability_requirements_defined=False,
            sandbox_rollback_requirements_defined=False,
            sandbox_kill_switch_requirements_defined=False,
            sandbox_human_supervision_requirements_defined=False,
            sandbox_session_requested=False,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(PaperBrokerSandboxSessionPreparationRisk)
    assert result.state is PaperBrokerSandboxSessionPreparationState.NOT_READY
    assert result.decision is PaperBrokerSandboxSessionPreparationDecision.BLOCK_BROKER_SANDBOX_SESSION
    assert result.offline_only is False


def test_forward_plan_gap_requires_forward_plan_fixes_when_not_blocked():
    result = evaluate_paper_broker_sandbox_session_preparation(
        _ready_input(
            forward_test_plan_approved=False,
            paper_runtime_forward_test_plan=_upstream("READY_FOR_PAPER_BROKER_SANDBOX_SESSION", "REVIEW_REQUIRED"),
        )
    )

    assert result.decision is PaperBrokerSandboxSessionPreparationDecision.REQUIRE_FORWARD_TEST_PLAN_FIXES


def test_scope_and_boundary_gaps_require_boundary_fixes():
    assert evaluate_paper_broker_sandbox_session_preparation(_ready_input(sandbox_session_scope_defined=False)).decision is PaperBrokerSandboxSessionPreparationDecision.REQUIRE_BOUNDARY_FIXES
    assert evaluate_paper_broker_sandbox_session_preparation(_ready_input(sandbox_session_boundaries_defined=False)).decision is PaperBrokerSandboxSessionPreparationDecision.REQUIRE_BOUNDARY_FIXES


def test_adapter_and_precondition_gaps_require_adapter_requirement_fixes():
    assert evaluate_paper_broker_sandbox_session_preparation(_ready_input(paper_broker_adapter_requirements_defined=False)).decision is PaperBrokerSandboxSessionPreparationDecision.REQUIRE_ADAPTER_REQUIREMENT_FIXES
    assert evaluate_paper_broker_sandbox_session_preparation(_ready_input(mock_to_broker_transition_requirements_defined=False)).decision is PaperBrokerSandboxSessionPreparationDecision.REQUIRE_ADAPTER_REQUIREMENT_FIXES
    assert evaluate_paper_broker_sandbox_session_preparation(_ready_input(sandbox_connection_preconditions_defined=False)).decision is PaperBrokerSandboxSessionPreparationDecision.REQUIRE_ADAPTER_REQUIREMENT_FIXES
    assert evaluate_paper_broker_sandbox_session_preparation(_ready_input(sandbox_order_preconditions_defined=False)).decision is PaperBrokerSandboxSessionPreparationDecision.REQUIRE_ADAPTER_REQUIREMENT_FIXES
    assert evaluate_paper_broker_sandbox_session_preparation(_ready_input(sandbox_position_preconditions_defined=False)).decision is PaperBrokerSandboxSessionPreparationDecision.REQUIRE_ADAPTER_REQUIREMENT_FIXES
    assert evaluate_paper_broker_sandbox_session_preparation(_ready_input(sandbox_account_preconditions_defined=False)).decision is PaperBrokerSandboxSessionPreparationDecision.REQUIRE_ADAPTER_REQUIREMENT_FIXES


def test_observability_rollback_kill_switch_and_supervision_decisions():
    assert evaluate_paper_broker_sandbox_session_preparation(_ready_input(sandbox_observability_requirements_defined=False)).decision is PaperBrokerSandboxSessionPreparationDecision.REQUIRE_OBSERVABILITY_FIXES
    assert evaluate_paper_broker_sandbox_session_preparation(_ready_input(sandbox_rollback_requirements_defined=False)).decision is PaperBrokerSandboxSessionPreparationDecision.REQUIRE_ROLLBACK_FIXES
    assert evaluate_paper_broker_sandbox_session_preparation(_ready_input(sandbox_kill_switch_requirements_defined=False)).decision is PaperBrokerSandboxSessionPreparationDecision.REQUIRE_KILL_SWITCH_FIXES
    assert evaluate_paper_broker_sandbox_session_preparation(_ready_input(sandbox_human_supervision_requirements_defined=False)).decision is PaperBrokerSandboxSessionPreparationDecision.REQUIRE_SUPERVISION_FIXES


def test_premature_sandbox_session_caps_score_and_blocks():
    data = _ready_input(sandbox_session_requested=False)
    risks = detect_broker_sandbox_preparation_risks(data)
    score = compute_broker_sandbox_preparation_score(data, risks)
    result = evaluate_paper_broker_sandbox_session_preparation(data)

    assert PaperBrokerSandboxSessionPreparationRisk.PREMATURE_SANDBOX_SESSION in risks
    assert score.overall_score <= 40
    assert result.decision is PaperBrokerSandboxSessionPreparationDecision.BLOCK_BROKER_SANDBOX_SESSION


def test_upstream_network_leak_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_session_preparation(
        _ready_input(paper_runtime_forward_test_plan=_upstream("READY_FOR_PAPER_BROKER_SANDBOX_SESSION", risks=("NETWORK_LEAK",)))
    )

    assert PaperBrokerSandboxSessionPreparationRisk.SANDBOX_BOUNDARY_GAP in result.risks
    assert PaperBrokerSandboxSessionPreparationRisk.PREMATURE_SANDBOX_SESSION in result.risks
    assert result.offline_only is False


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_broker_sandbox_preparation_recommendations(
        (
            PaperBrokerSandboxSessionPreparationRisk.KILL_SWITCH_REQUIREMENT_GAP,
            PaperBrokerSandboxSessionPreparationRisk.KILL_SWITCH_REQUIREMENT_GAP,
            PaperBrokerSandboxSessionPreparationRisk.OBSERVABILITY_REQUIREMENT_GAP,
            PaperBrokerSandboxSessionPreparationRisk.PREMATURE_SANDBOX_SESSION,
        ),
        PaperBrokerSandboxSessionPreparationDecision.REQUIRE_KILL_SWITCH_FIXES,
    )

    assert recommendations.count(PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_SANDBOX_KILL_SWITCH_REQUIREMENTS) == 1
    assert PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_SANDBOX_OBSERVABILITY_REQUIREMENTS in recommendations
    assert PaperBrokerSandboxSessionPreparationRecommendation.DELAY_SANDBOX_SESSION in recommendations
    assert PaperBrokerSandboxSessionPreparationRecommendation.RUN_BROKER_SANDBOX_PREPARATION_REVIEW_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_broker_sandbox_preparation_recommendations(
        (),
        PaperBrokerSandboxSessionPreparationDecision.APPROVE_PAPER_BROKER_SANDBOX_SESSION_PREPARATION,
    )

    assert PaperBrokerSandboxSessionPreparationRecommendation.APPROVE_PAPER_BROKER_SANDBOX_SESSION_REVIEW in recommendations


def test_markdown_contains_decision_risks_and_recommendations():
    result = evaluate_paper_broker_sandbox_session_preparation(_ready_input(sandbox_kill_switch_requirements_defined=False))
    markdown = render_paper_broker_sandbox_session_preparation_markdown(result)

    assert "# AGIcore Paper Broker Sandbox Session Preparation" in markdown
    assert "Decision: REQUIRE_KILL_SWITCH_FIXES" in markdown
    assert "KILL_SWITCH_REQUIREMENT_GAP" in markdown
    assert "DEFINE_SANDBOX_KILL_SWITCH_REQUIREMENTS" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_paper_broker_sandbox_session_preparation(_ready_input().__dict__)

    assert result.state is PaperBrokerSandboxSessionPreparationState.READY_FOR_PAPER_BROKER_SANDBOX_SESSION_REVIEW


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (PaperBrokerSandboxSessionPreparationRisk.CONNECTION_PRECONDITION_GAP, PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_SANDBOX_CONNECTION_PRECONDITIONS),
        (PaperBrokerSandboxSessionPreparationRisk.ORDER_PRECONDITION_GAP, PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_SANDBOX_ORDER_PRECONDITIONS),
        (PaperBrokerSandboxSessionPreparationRisk.POSITION_PRECONDITION_GAP, PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_SANDBOX_POSITION_PRECONDITIONS),
        (PaperBrokerSandboxSessionPreparationRisk.ACCOUNT_PRECONDITION_GAP, PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_SANDBOX_ACCOUNT_PRECONDITIONS),
        (PaperBrokerSandboxSessionPreparationRisk.HUMAN_SUPERVISION_REQUIREMENT_GAP, PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_SANDBOX_HUMAN_SUPERVISION_REQUIREMENTS),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_broker_sandbox_preparation_recommendations((risk,), PaperBrokerSandboxSessionPreparationDecision.REQUIRE_ADAPTER_REQUIREMENT_FIXES)


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "paper_broker_sandbox_session_preparation.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
