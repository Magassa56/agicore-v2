import ast
from pathlib import Path

import pytest

from agicore.trading.paper_broker_sandbox_session_authorization_gate import (
    compute_authorization_gate_score,
    detect_authorization_gate_risks,
    evaluate_paper_broker_sandbox_session_authorization_gate,
    generate_authorization_gate_recommendations,
    render_paper_broker_sandbox_session_authorization_gate_markdown,
    verify_account_access_authorization,
    verify_authorization_boundaries,
    verify_authorization_scope,
    verify_broker_connection_authorization,
    verify_human_supervision_authorization,
    verify_journal_authorization,
    verify_kill_switch_authorization,
    verify_observability_authorization,
    verify_order_execution_authorization,
    verify_position_management_authorization,
    verify_rollback_authorization,
    verify_sandbox_review_approval,
    verify_stop_conditions_authorization,
)
from agicore.trading.paper_broker_sandbox_session_authorization_gate_models import (
    PaperBrokerSandboxSessionAuthorizationGateDecision,
    PaperBrokerSandboxSessionAuthorizationGateInput,
    PaperBrokerSandboxSessionAuthorizationGateRecommendation,
    PaperBrokerSandboxSessionAuthorizationGateRisk,
    PaperBrokerSandboxSessionAuthorizationGateState,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "risks": tuple(risks), "offline_only": True}
    if decision:
        payload["decision"] = decision
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_sandbox_session_review": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_SESSION",
            "APPROVE_PAPER_BROKER_SANDBOX_SESSION",
        ),
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
        "sandbox_review_approved": True,
        "sandbox_reviewed": True,
        "authorization_scope_reviewed": True,
        "authorization_scope_clear": True,
        "authorization_boundaries_reviewed": True,
        "authorization_boundaries_complete": True,
        "broker_connection_authorization_reviewed": True,
        "broker_connection_authorized": True,
        "order_execution_authorization_reviewed": True,
        "order_execution_authorized": True,
        "position_management_authorization_reviewed": True,
        "position_management_authorized": True,
        "account_access_authorization_reviewed": True,
        "account_access_authorized": True,
        "observability_authorization_reviewed": True,
        "observability_authorized": True,
        "rollback_authorization_reviewed": True,
        "rollback_authorized": True,
        "kill_switch_authorization_reviewed": True,
        "kill_switch_authorized": True,
        "human_supervision_authorization_reviewed": True,
        "human_supervision_authorized": True,
        "journal_authorization_reviewed": True,
        "journal_authorized": True,
        "stop_conditions_authorization_reviewed": True,
        "stop_conditions_authorized": True,
        "paper_broker_sandbox_dry_run_requested": True,
        "sandbox_authorization_gate_requested": True,
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
        "no_real_account_access": True,
    }
    payload.update(overrides)
    return PaperBrokerSandboxSessionAuthorizationGateInput(**payload)


def test_evaluate_approves_paper_broker_sandbox_authorization_gate():
    result = evaluate_paper_broker_sandbox_session_authorization_gate(_ready_input())

    assert result.state is PaperBrokerSandboxSessionAuthorizationGateState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN
    assert result.decision is PaperBrokerSandboxSessionAuthorizationGateDecision.APPROVE_PAPER_BROKER_SANDBOX_AUTHORIZATION_GATE
    assert result.risks == ()
    assert result.offline_only is True
    assert result.authorization_score == 100


def test_authorization_ready_state_below_dry_run_threshold():
    result = evaluate_paper_broker_sandbox_session_authorization_gate(
        _ready_input(
            sandbox_review_approval_score=90,
            authorization_scope_score=90,
            authorization_boundaries_score=90,
            broker_connection_authorization_score=90,
            order_execution_authorization_score=90,
            position_management_authorization_score=90,
            account_access_authorization_score=90,
            observability_authorization_score=90,
            rollback_authorization_score=90,
            kill_switch_authorization_score=90,
            human_supervision_authorization_score=90,
            journal_authorization_score=90,
            stop_conditions_authorization_score=90,
        )
    )

    assert result.state is PaperBrokerSandboxSessionAuthorizationGateState.SANDBOX_SESSION_AUTHORIZATION_READY
    assert result.decision is PaperBrokerSandboxSessionAuthorizationGateDecision.APPROVE_PAPER_BROKER_SANDBOX_AUTHORIZATION_GATE


def test_verifiers_detect_primary_risks():
    assert PaperBrokerSandboxSessionAuthorizationGateRisk.SANDBOX_REVIEW_NOT_APPROVED in verify_sandbox_review_approval(_ready_input(sandbox_review_approved=False)).risks
    assert PaperBrokerSandboxSessionAuthorizationGateRisk.AUTHORIZATION_SCOPE_UNCLEAR in verify_authorization_scope(_ready_input(authorization_scope_clear=False)).risks
    assert PaperBrokerSandboxSessionAuthorizationGateRisk.AUTHORIZATION_BOUNDARY_GAP in verify_authorization_boundaries(_ready_input(authorization_boundaries_complete=False)).risks
    assert PaperBrokerSandboxSessionAuthorizationGateRisk.BROKER_CONNECTION_AUTHORIZATION_GAP in verify_broker_connection_authorization(_ready_input(broker_connection_authorized=False)).risks
    assert PaperBrokerSandboxSessionAuthorizationGateRisk.ORDER_EXECUTION_AUTHORIZATION_GAP in verify_order_execution_authorization(_ready_input(order_execution_authorized=False)).risks
    assert PaperBrokerSandboxSessionAuthorizationGateRisk.POSITION_MANAGEMENT_AUTHORIZATION_GAP in verify_position_management_authorization(_ready_input(position_management_authorized=False)).risks
    assert PaperBrokerSandboxSessionAuthorizationGateRisk.ACCOUNT_ACCESS_AUTHORIZATION_GAP in verify_account_access_authorization(_ready_input(account_access_authorized=False)).risks
    assert PaperBrokerSandboxSessionAuthorizationGateRisk.OBSERVABILITY_AUTHORIZATION_GAP in verify_observability_authorization(_ready_input(observability_authorized=False)).risks
    assert PaperBrokerSandboxSessionAuthorizationGateRisk.ROLLBACK_AUTHORIZATION_GAP in verify_rollback_authorization(_ready_input(rollback_authorized=False)).risks
    assert PaperBrokerSandboxSessionAuthorizationGateRisk.KILL_SWITCH_AUTHORIZATION_GAP in verify_kill_switch_authorization(_ready_input(kill_switch_authorized=False)).risks
    assert PaperBrokerSandboxSessionAuthorizationGateRisk.HUMAN_SUPERVISION_AUTHORIZATION_GAP in verify_human_supervision_authorization(_ready_input(human_supervision_authorized=False)).risks
    assert PaperBrokerSandboxSessionAuthorizationGateRisk.JOURNAL_AUTHORIZATION_GAP in verify_journal_authorization(_ready_input(journal_authorized=False)).risks
    assert PaperBrokerSandboxSessionAuthorizationGateRisk.STOP_CONDITIONS_AUTHORIZATION_GAP in verify_stop_conditions_authorization(_ready_input(stop_conditions_authorized=False)).risks


def test_detects_all_authorization_gate_risks():
    result = evaluate_paper_broker_sandbox_session_authorization_gate(
        _ready_input(
            sandbox_review_approved=False,
            authorization_scope_clear=False,
            authorization_boundaries_complete=False,
            broker_connection_authorized=False,
            order_execution_authorized=False,
            position_management_authorized=False,
            account_access_authorized=False,
            observability_authorized=False,
            rollback_authorized=False,
            kill_switch_authorized=False,
            human_supervision_authorized=False,
            journal_authorized=False,
            stop_conditions_authorized=False,
            paper_broker_sandbox_dry_run_requested=False,
            sandbox_authorization_gate_requested=False,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(PaperBrokerSandboxSessionAuthorizationGateRisk)
    assert result.state is PaperBrokerSandboxSessionAuthorizationGateState.NOT_AUTHORIZED
    assert result.decision is PaperBrokerSandboxSessionAuthorizationGateDecision.BLOCK_PAPER_BROKER_SANDBOX_SESSION
    assert result.offline_only is False


def test_review_gap_requires_sandbox_review_fixes_when_not_blocked():
    result = evaluate_paper_broker_sandbox_session_authorization_gate(_ready_input(sandbox_review_approved=False))

    assert result.decision is PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_SANDBOX_REVIEW_FIXES


def test_scope_and_boundary_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_session_authorization_gate(_ready_input(authorization_scope_clear=False)).decision is PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_SCOPE_FIXES
    assert evaluate_paper_broker_sandbox_session_authorization_gate(_ready_input(authorization_boundaries_complete=False)).decision is PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_BOUNDARY_FIXES


def test_connection_order_position_account_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_session_authorization_gate(_ready_input(broker_connection_authorized=False)).decision is PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_CONNECTION_AUTHORIZATION_FIXES
    assert evaluate_paper_broker_sandbox_session_authorization_gate(_ready_input(order_execution_authorized=False)).decision is PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_ORDER_AUTHORIZATION_FIXES
    assert evaluate_paper_broker_sandbox_session_authorization_gate(_ready_input(position_management_authorized=False)).decision is PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_POSITION_AUTHORIZATION_FIXES
    assert evaluate_paper_broker_sandbox_session_authorization_gate(_ready_input(account_access_authorized=False)).decision is PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_ACCOUNT_AUTHORIZATION_FIXES


def test_observability_rollback_kill_switch_and_supervision_decisions():
    assert evaluate_paper_broker_sandbox_session_authorization_gate(_ready_input(observability_authorized=False)).decision is PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_OBSERVABILITY_AUTHORIZATION_FIXES
    assert evaluate_paper_broker_sandbox_session_authorization_gate(_ready_input(rollback_authorized=False)).decision is PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_ROLLBACK_AUTHORIZATION_FIXES
    assert evaluate_paper_broker_sandbox_session_authorization_gate(_ready_input(kill_switch_authorized=False)).decision is PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_KILL_SWITCH_AUTHORIZATION_FIXES
    assert evaluate_paper_broker_sandbox_session_authorization_gate(_ready_input(human_supervision_authorized=False)).decision is PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_SUPERVISION_AUTHORIZATION_FIXES


def test_journal_and_stop_condition_decisions_use_allowed_decision_set():
    assert evaluate_paper_broker_sandbox_session_authorization_gate(_ready_input(journal_authorized=False)).decision is PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_SUPERVISION_AUTHORIZATION_FIXES
    assert evaluate_paper_broker_sandbox_session_authorization_gate(_ready_input(stop_conditions_authorized=False)).decision is PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_BOUNDARY_FIXES


def test_premature_dry_run_caps_score_and_blocks():
    data = _ready_input(paper_broker_sandbox_dry_run_requested=False, sandbox_authorization_gate_requested=False)
    risks = detect_authorization_gate_risks(data)
    score = compute_authorization_gate_score(data, risks)
    result = evaluate_paper_broker_sandbox_session_authorization_gate(data)

    assert PaperBrokerSandboxSessionAuthorizationGateRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN in risks
    assert score.overall_score <= 40
    assert result.decision is PaperBrokerSandboxSessionAuthorizationGateDecision.BLOCK_PAPER_BROKER_SANDBOX_SESSION


def test_real_account_access_gap_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_session_authorization_gate(_ready_input(no_real_account_access=False))

    assert PaperBrokerSandboxSessionAuthorizationGateRisk.AUTHORIZATION_BOUNDARY_GAP in result.risks
    assert PaperBrokerSandboxSessionAuthorizationGateRisk.ACCOUNT_ACCESS_AUTHORIZATION_GAP in result.risks
    assert PaperBrokerSandboxSessionAuthorizationGateRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN in result.risks
    assert result.offline_only is False


def test_upstream_network_leak_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_session_authorization_gate(
        _ready_input(paper_broker_sandbox_session_review=_upstream("READY_FOR_PAPER_BROKER_SANDBOX_SESSION", risks=("NETWORK_LEAK",)))
    )

    assert PaperBrokerSandboxSessionAuthorizationGateRisk.AUTHORIZATION_BOUNDARY_GAP in result.risks
    assert PaperBrokerSandboxSessionAuthorizationGateRisk.BROKER_CONNECTION_AUTHORIZATION_GAP in result.risks
    assert PaperBrokerSandboxSessionAuthorizationGateRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN in result.risks
    assert result.offline_only is False


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_authorization_gate_recommendations(
        (
            PaperBrokerSandboxSessionAuthorizationGateRisk.KILL_SWITCH_AUTHORIZATION_GAP,
            PaperBrokerSandboxSessionAuthorizationGateRisk.KILL_SWITCH_AUTHORIZATION_GAP,
            PaperBrokerSandboxSessionAuthorizationGateRisk.JOURNAL_AUTHORIZATION_GAP,
            PaperBrokerSandboxSessionAuthorizationGateRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN,
        ),
        PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_KILL_SWITCH_AUTHORIZATION_FIXES,
    )

    assert recommendations.count(PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_KILL_SWITCH_AUTHORIZATION) == 1
    assert PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_JOURNAL_AUTHORIZATION in recommendations
    assert PaperBrokerSandboxSessionAuthorizationGateRecommendation.DELAY_PAPER_BROKER_SANDBOX_DRY_RUN in recommendations
    assert PaperBrokerSandboxSessionAuthorizationGateRecommendation.RUN_PAPER_BROKER_SANDBOX_AUTHORIZATION_GATE_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_authorization_gate_recommendations(
        (),
        PaperBrokerSandboxSessionAuthorizationGateDecision.APPROVE_PAPER_BROKER_SANDBOX_AUTHORIZATION_GATE,
    )

    assert PaperBrokerSandboxSessionAuthorizationGateRecommendation.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN in recommendations


def test_markdown_contains_decision_risks_and_recommendations():
    result = evaluate_paper_broker_sandbox_session_authorization_gate(_ready_input(kill_switch_authorized=False))
    markdown = render_paper_broker_sandbox_session_authorization_gate_markdown(result)

    assert "# AGIcore Paper Broker Sandbox Session Authorization Gate" in markdown
    assert "Decision: REQUIRE_KILL_SWITCH_AUTHORIZATION_FIXES" in markdown
    assert "KILL_SWITCH_AUTHORIZATION_GAP" in markdown
    assert "COMPLETE_KILL_SWITCH_AUTHORIZATION" in markdown


def test_mapping_inputs_are_supported_and_extra_keys_are_ignored():
    payload = dict(_ready_input().__dict__)
    payload["ignored_future_key"] = "ignored"
    result = evaluate_paper_broker_sandbox_session_authorization_gate(payload)

    assert result.state is PaperBrokerSandboxSessionAuthorizationGateState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (PaperBrokerSandboxSessionAuthorizationGateRisk.BROKER_CONNECTION_AUTHORIZATION_GAP, PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_BROKER_CONNECTION_AUTHORIZATION),
        (PaperBrokerSandboxSessionAuthorizationGateRisk.ORDER_EXECUTION_AUTHORIZATION_GAP, PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_ORDER_EXECUTION_AUTHORIZATION),
        (PaperBrokerSandboxSessionAuthorizationGateRisk.POSITION_MANAGEMENT_AUTHORIZATION_GAP, PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_POSITION_MANAGEMENT_AUTHORIZATION),
        (PaperBrokerSandboxSessionAuthorizationGateRisk.ACCOUNT_ACCESS_AUTHORIZATION_GAP, PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_ACCOUNT_ACCESS_AUTHORIZATION),
        (PaperBrokerSandboxSessionAuthorizationGateRisk.STOP_CONDITIONS_AUTHORIZATION_GAP, PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_STOP_CONDITIONS_AUTHORIZATION),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_authorization_gate_recommendations((risk,), PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_BOUNDARY_FIXES)


@pytest.mark.parametrize(
    "module_name",
    [
        "paper_broker_sandbox_session_authorization_gate.py",
        "paper_broker_sandbox_session_authorization_gate_models.py",
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

