import ast
from pathlib import Path

import pytest

from agicore.trading.paper_broker_sandbox_dry_run_execution_authorization_gate import (
    compute_execution_authorization_gate_score,
    detect_execution_authorization_gate_risks,
    evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate,
    generate_execution_authorization_gate_recommendations,
    render_paper_broker_sandbox_dry_run_execution_authorization_gate_markdown,
    verify_execution_abort_condition_authorization,
    verify_execution_account_authorization,
    verify_execution_authorization_boundaries,
    verify_execution_authorization_scope,
    verify_execution_connection_authorization,
    verify_execution_human_supervision_authorization,
    verify_execution_journal_authorization,
    verify_execution_kill_switch_authorization,
    verify_execution_observability_authorization,
    verify_execution_order_authorization,
    verify_execution_position_authorization,
    verify_execution_review_approval,
    verify_execution_rollback_authorization,
    verify_execution_scenario_authorization,
    verify_execution_session_limit_authorization,
    verify_execution_stop_condition_authorization,
    verify_execution_success_failure_authorization,
)
from agicore.trading.paper_broker_sandbox_dry_run_execution_authorization_gate_models import (
    PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision,
    PaperBrokerSandboxDryRunExecutionAuthorizationGateInput,
    PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation,
    PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk,
    PaperBrokerSandboxDryRunExecutionAuthorizationGateState,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "risks": tuple(risks), "offline_only": True}
    if decision:
        payload["decision"] = decision
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_sandbox_dry_run_execution_review": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE",
            "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW",
        ),
        "paper_broker_sandbox_dry_run_pre_execution_check": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW",
            "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK",
        ),
        "paper_broker_sandbox_dry_run_review": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK",
            "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW",
        ),
        "paper_broker_sandbox_dry_run_plan": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW",
            "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PLAN",
        ),
        "paper_broker_sandbox_session_authorization_gate": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN",
            "APPROVE_PAPER_BROKER_SANDBOX_AUTHORIZATION_GATE",
        ),
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
        "execution_review_approved": True,
        "execution_review_reviewed": True,
        "execution_authorization_scope_reviewed": True,
        "execution_authorization_scope_clear": True,
        "execution_authorization_boundaries_reviewed": True,
        "execution_authorization_boundaries_complete": True,
        "execution_scenario_authorization_reviewed": True,
        "execution_scenario_authorization_complete": True,
        "execution_session_limit_authorization_reviewed": True,
        "execution_session_limit_authorization_complete": True,
        "execution_connection_authorization_reviewed": True,
        "execution_connection_authorization_complete": True,
        "execution_order_authorization_reviewed": True,
        "execution_order_authorization_complete": True,
        "execution_position_authorization_reviewed": True,
        "execution_position_authorization_complete": True,
        "execution_account_authorization_reviewed": True,
        "execution_account_authorization_complete": True,
        "execution_observability_authorization_reviewed": True,
        "execution_observability_authorization_complete": True,
        "execution_rollback_authorization_reviewed": True,
        "execution_rollback_authorization_complete": True,
        "execution_kill_switch_authorization_reviewed": True,
        "execution_kill_switch_authorization_complete": True,
        "execution_human_supervision_authorization_reviewed": True,
        "execution_human_supervision_authorization_complete": True,
        "execution_journal_authorization_reviewed": True,
        "execution_journal_authorization_complete": True,
        "execution_stop_condition_authorization_reviewed": True,
        "execution_stop_condition_authorization_complete": True,
        "execution_abort_condition_authorization_reviewed": True,
        "execution_abort_condition_authorization_complete": True,
        "execution_success_failure_authorization_reviewed": True,
        "execution_success_failure_authorization_complete": True,
        "paper_broker_sandbox_dry_run_execution_authorization_gate_requested": True,
        "paper_broker_sandbox_dry_run_execution_requested": False,
        "paper_broker_sandbox_dry_run_controlled_simulation_requested": False,
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
        "no_dry_run_execution": True,
        "no_controlled_simulation_execution": True,
        "no_real_order": True,
        "no_real_account_access": True,
    }
    payload.update(overrides)
    return PaperBrokerSandboxDryRunExecutionAuthorizationGateInput(**payload)


def test_evaluate_approves_paper_broker_sandbox_dry_run_execution_authorization_gate():
    result = evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input())

    assert result.state is PaperBrokerSandboxDryRunExecutionAuthorizationGateState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN
    assert result.decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE
    assert result.risks == ()
    assert result.offline_only is True
    assert result.authorization_score == 100


def test_execution_authorization_gate_ready_state_below_controlled_simulation_plan_threshold():
    result = evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(
        _ready_input(
            execution_review_approval_score=90,
            execution_authorization_scope_score=90,
            execution_authorization_boundaries_score=90,
            execution_scenario_authorization_score=90,
            execution_session_limit_authorization_score=90,
            execution_connection_authorization_score=90,
            execution_order_authorization_score=90,
            execution_position_authorization_score=90,
            execution_account_authorization_score=90,
            execution_observability_authorization_score=90,
            execution_rollback_authorization_score=90,
            execution_kill_switch_authorization_score=90,
            execution_human_supervision_authorization_score=90,
            execution_journal_authorization_score=90,
            execution_stop_condition_authorization_score=90,
            execution_abort_condition_authorization_score=90,
            execution_success_failure_authorization_score=90,
        )
    )

    assert result.state is PaperBrokerSandboxDryRunExecutionAuthorizationGateState.EXECUTION_AUTHORIZATION_GATE_READY
    assert result.decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE


def test_authorization_sections_detect_primary_risks():
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_REVIEW_NOT_APPROVED in verify_execution_review_approval(_ready_input(execution_review_approved=False)).risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_AUTHORIZATION_SCOPE_UNCLEAR in verify_execution_authorization_scope(_ready_input(execution_authorization_scope_clear=False)).risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_AUTHORIZATION_BOUNDARY_GAP in verify_execution_authorization_boundaries(_ready_input(execution_authorization_boundaries_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_SCENARIO_AUTHORIZATION_GAP in verify_execution_scenario_authorization(_ready_input(execution_scenario_authorization_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_SESSION_LIMIT_AUTHORIZATION_GAP in verify_execution_session_limit_authorization(_ready_input(execution_session_limit_authorization_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_CONNECTION_AUTHORIZATION_GAP in verify_execution_connection_authorization(_ready_input(execution_connection_authorization_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ORDER_AUTHORIZATION_GAP in verify_execution_order_authorization(_ready_input(execution_order_authorization_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_POSITION_AUTHORIZATION_GAP in verify_execution_position_authorization(_ready_input(execution_position_authorization_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ACCOUNT_AUTHORIZATION_GAP in verify_execution_account_authorization(_ready_input(execution_account_authorization_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_OBSERVABILITY_AUTHORIZATION_GAP in verify_execution_observability_authorization(_ready_input(execution_observability_authorization_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ROLLBACK_AUTHORIZATION_GAP in verify_execution_rollback_authorization(_ready_input(execution_rollback_authorization_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_KILL_SWITCH_AUTHORIZATION_GAP in verify_execution_kill_switch_authorization(_ready_input(execution_kill_switch_authorization_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_HUMAN_SUPERVISION_AUTHORIZATION_GAP in verify_execution_human_supervision_authorization(_ready_input(execution_human_supervision_authorization_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_JOURNAL_AUTHORIZATION_GAP in verify_execution_journal_authorization(_ready_input(execution_journal_authorization_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_STOP_CONDITION_AUTHORIZATION_GAP in verify_execution_stop_condition_authorization(_ready_input(execution_stop_condition_authorization_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ABORT_CONDITION_AUTHORIZATION_GAP in verify_execution_abort_condition_authorization(_ready_input(execution_abort_condition_authorization_complete=False)).risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_SUCCESS_FAILURE_AUTHORIZATION_GAP in verify_execution_success_failure_authorization(_ready_input(execution_success_failure_authorization_complete=False)).risks


def test_detects_all_execution_authorization_gate_risks():
    result = evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(
        _ready_input(
            execution_review_approved=False,
            execution_authorization_scope_clear=False,
            execution_authorization_boundaries_complete=False,
            execution_scenario_authorization_complete=False,
            execution_session_limit_authorization_complete=False,
            execution_connection_authorization_complete=False,
            execution_order_authorization_complete=False,
            execution_position_authorization_complete=False,
            execution_account_authorization_complete=False,
            execution_observability_authorization_complete=False,
            execution_rollback_authorization_complete=False,
            execution_kill_switch_authorization_complete=False,
            execution_human_supervision_authorization_complete=False,
            execution_journal_authorization_complete=False,
            execution_stop_condition_authorization_complete=False,
            execution_abort_condition_authorization_complete=False,
            execution_success_failure_authorization_complete=False,
            paper_broker_sandbox_dry_run_execution_authorization_gate_requested=False,
            paper_broker_sandbox_dry_run_controlled_simulation_requested=True,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk)
    assert result.state is PaperBrokerSandboxDryRunExecutionAuthorizationGateState.NOT_AUTHORIZED
    assert result.decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION
    assert result.offline_only is False


def test_execution_review_gap_requires_review_fixes_when_not_blocked():
    result = evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_review_approved=False))

    assert result.decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_EXECUTION_REVIEW_FIXES


def test_scope_boundary_scenario_and_limit_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_authorization_scope_clear=False)).decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_SCOPE_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_authorization_boundaries_complete=False)).decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_BOUNDARY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_scenario_authorization_complete=False)).decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_SCENARIO_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_session_limit_authorization_complete=False)).decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_SESSION_LIMIT_FIXES


def test_connection_order_position_and_account_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_connection_authorization_complete=False)).decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_CONNECTION_AUTHORIZATION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_order_authorization_complete=False)).decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_ORDER_AUTHORIZATION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_position_authorization_complete=False)).decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_POSITION_AUTHORIZATION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_account_authorization_complete=False)).decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_ACCOUNT_AUTHORIZATION_FIXES


def test_observability_rollback_kill_supervision_journal_stop_abort_and_criteria_decisions():
    assert evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_observability_authorization_complete=False)).decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_OBSERVABILITY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_rollback_authorization_complete=False)).decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_ROLLBACK_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_kill_switch_authorization_complete=False)).decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_KILL_SWITCH_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_human_supervision_authorization_complete=False)).decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_SUPERVISION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_journal_authorization_complete=False)).decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_JOURNAL_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_stop_condition_authorization_complete=False)).decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_STOP_CONDITION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_success_failure_authorization_complete=False)).decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_STOP_CONDITION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_abort_condition_authorization_complete=False)).decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_ABORT_CONDITION_FIXES


def test_premature_controlled_simulation_caps_score_and_blocks():
    data = _ready_input(paper_broker_sandbox_dry_run_controlled_simulation_requested=True)
    risks = detect_execution_authorization_gate_risks(data)
    score = compute_execution_authorization_gate_score(data, risks)
    result = evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(data)

    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION in risks
    assert score.overall_score <= 40
    assert result.decision is PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION


def test_no_controlled_simulation_gap_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(no_controlled_simulation_execution=False))

    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_AUTHORIZATION_BOUNDARY_GAP in result.risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION in result.risks
    assert result.offline_only is False


def test_upstream_network_leak_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(
        _ready_input(
            paper_broker_sandbox_dry_run_execution_review=_upstream(
                "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE",
                risks=("NETWORK_LEAK",),
            )
        )
    )

    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_AUTHORIZATION_BOUNDARY_GAP in result.risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_CONNECTION_AUTHORIZATION_GAP in result.risks
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION in result.risks
    assert result.offline_only is False


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_execution_authorization_gate_recommendations(
        (
            PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_KILL_SWITCH_AUTHORIZATION_GAP,
            PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_KILL_SWITCH_AUTHORIZATION_GAP,
            PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ABORT_CONDITION_AUTHORIZATION_GAP,
            PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION,
        ),
        PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_KILL_SWITCH_FIXES,
    )

    assert recommendations.count(PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_KILL_SWITCH_AUTHORIZATION) == 1
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_ABORT_CONDITION_AUTHORIZATION in recommendations
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION in recommendations
    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.RUN_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_execution_authorization_gate_recommendations(
        (),
        PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE,
    )

    assert PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN in recommendations


def test_markdown_contains_decision_risks_and_recommendations():
    result = evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(_ready_input(execution_kill_switch_authorization_complete=False))
    markdown = render_paper_broker_sandbox_dry_run_execution_authorization_gate_markdown(result)

    assert "# AGIcore Paper Broker Sandbox Dry Run Execution Authorization Gate" in markdown
    assert "Decision: REQUIRE_KILL_SWITCH_FIXES" in markdown
    assert "EXECUTION_KILL_SWITCH_AUTHORIZATION_GAP" in markdown
    assert "COMPLETE_EXECUTION_KILL_SWITCH_AUTHORIZATION" in markdown


def test_mapping_inputs_are_supported_and_extra_keys_are_ignored():
    payload = dict(_ready_input().__dict__)
    payload["ignored_future_key"] = "ignored"
    result = evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(payload)

    assert result.state is PaperBrokerSandboxDryRunExecutionAuthorizationGateState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_CONNECTION_AUTHORIZATION_GAP,
            PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_CONNECTION_AUTHORIZATION,
        ),
        (
            PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ORDER_AUTHORIZATION_GAP,
            PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_ORDER_AUTHORIZATION,
        ),
        (
            PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_POSITION_AUTHORIZATION_GAP,
            PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_POSITION_AUTHORIZATION,
        ),
        (
            PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ACCOUNT_AUTHORIZATION_GAP,
            PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_ACCOUNT_AUTHORIZATION,
        ),
        (
            PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_SUCCESS_FAILURE_AUTHORIZATION_GAP,
            PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_SUCCESS_FAILURE_AUTHORIZATION,
        ),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_execution_authorization_gate_recommendations(
        (risk,),
        PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_BOUNDARY_FIXES,
    )


@pytest.mark.parametrize(
    "module_name",
    [
        "paper_broker_sandbox_dry_run_execution_authorization_gate.py",
        "paper_broker_sandbox_dry_run_execution_authorization_gate_models.py",
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
