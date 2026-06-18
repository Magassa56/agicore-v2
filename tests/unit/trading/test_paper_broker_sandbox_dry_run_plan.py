import ast
from pathlib import Path

import pytest

from agicore.trading.paper_broker_sandbox_dry_run_plan import (
    compute_dry_run_plan_score,
    define_dry_run_account_policy,
    define_dry_run_boundaries,
    define_dry_run_connection_policy,
    define_dry_run_failure_criteria,
    define_dry_run_human_supervision_policy,
    define_dry_run_journal_policy,
    define_dry_run_kill_switch_policy,
    define_dry_run_observability_policy,
    define_dry_run_order_policy,
    define_dry_run_position_policy,
    define_dry_run_rollback_policy,
    define_dry_run_scenario,
    define_dry_run_scope,
    define_dry_run_session_limits,
    define_dry_run_stop_conditions,
    define_dry_run_success_criteria,
    detect_dry_run_plan_risks,
    evaluate_paper_broker_sandbox_dry_run_plan,
    generate_dry_run_plan_recommendations,
    render_paper_broker_sandbox_dry_run_plan_markdown,
    verify_authorization_gate_readiness,
)
from agicore.trading.paper_broker_sandbox_dry_run_plan_models import (
    PaperBrokerSandboxDryRunPlanDecision,
    PaperBrokerSandboxDryRunPlanInput,
    PaperBrokerSandboxDryRunPlanRecommendation,
    PaperBrokerSandboxDryRunPlanRisk,
    PaperBrokerSandboxDryRunPlanState,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "risks": tuple(risks), "offline_only": True}
    if decision:
        payload["decision"] = decision
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
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
        "authorization_gate_approved": True,
        "authorization_gate_reviewed": True,
        "dry_run_scope_defined": True,
        "dry_run_scope_clear": True,
        "dry_run_boundaries_defined": True,
        "dry_run_boundaries_complete": True,
        "dry_run_scenario_defined": True,
        "dry_run_session_limits_defined": True,
        "dry_run_connection_policy_defined": True,
        "dry_run_order_policy_defined": True,
        "dry_run_position_policy_defined": True,
        "dry_run_account_policy_defined": True,
        "dry_run_observability_policy_defined": True,
        "dry_run_rollback_policy_defined": True,
        "dry_run_kill_switch_policy_defined": True,
        "dry_run_human_supervision_policy_defined": True,
        "dry_run_journal_policy_defined": True,
        "dry_run_stop_conditions_defined": True,
        "dry_run_success_criteria_defined": True,
        "dry_run_failure_criteria_defined": True,
        "paper_broker_sandbox_dry_run_plan_requested": True,
        "paper_broker_sandbox_dry_run_execution_requested": False,
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
        "no_dry_run_execution": True,
    }
    payload.update(overrides)
    return PaperBrokerSandboxDryRunPlanInput(**payload)


def test_evaluate_approves_paper_broker_sandbox_dry_run_plan():
    result = evaluate_paper_broker_sandbox_dry_run_plan(_ready_input())

    assert result.state is PaperBrokerSandboxDryRunPlanState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW
    assert result.decision is PaperBrokerSandboxDryRunPlanDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PLAN
    assert result.risks == ()
    assert result.offline_only is True
    assert result.plan_score == 100


def test_dry_run_plan_ready_state_below_review_threshold():
    result = evaluate_paper_broker_sandbox_dry_run_plan(
        _ready_input(
            authorization_gate_readiness_score=90,
            dry_run_scope_score=90,
            dry_run_boundaries_score=90,
            dry_run_scenario_score=90,
            dry_run_session_limits_score=90,
            dry_run_connection_policy_score=90,
            dry_run_order_policy_score=90,
            dry_run_position_policy_score=90,
            dry_run_account_policy_score=90,
            dry_run_observability_policy_score=90,
            dry_run_rollback_policy_score=90,
            dry_run_kill_switch_policy_score=90,
            dry_run_human_supervision_policy_score=90,
            dry_run_journal_policy_score=90,
            dry_run_stop_conditions_score=90,
            dry_run_success_criteria_score=90,
            dry_run_failure_criteria_score=90,
        )
    )

    assert result.state is PaperBrokerSandboxDryRunPlanState.DRY_RUN_PLAN_READY
    assert result.decision is PaperBrokerSandboxDryRunPlanDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PLAN


def test_section_builders_detect_primary_risks():
    assert PaperBrokerSandboxDryRunPlanRisk.AUTHORIZATION_GATE_NOT_APPROVED in verify_authorization_gate_readiness(_ready_input(authorization_gate_approved=False)).risks
    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_SCOPE_UNCLEAR in define_dry_run_scope(_ready_input(dry_run_scope_clear=False)).risks
    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_BOUNDARY_GAP in define_dry_run_boundaries(_ready_input(dry_run_boundaries_complete=False)).risks
    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_SCENARIO_UNDEFINED in define_dry_run_scenario(_ready_input(dry_run_scenario_defined=False)).risks
    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_SESSION_LIMIT_GAP in define_dry_run_session_limits(_ready_input(dry_run_session_limits_defined=False)).risks
    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_CONNECTION_POLICY_GAP in define_dry_run_connection_policy(_ready_input(dry_run_connection_policy_defined=False)).risks
    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_ORDER_POLICY_GAP in define_dry_run_order_policy(_ready_input(dry_run_order_policy_defined=False)).risks
    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_POSITION_POLICY_GAP in define_dry_run_position_policy(_ready_input(dry_run_position_policy_defined=False)).risks
    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_ACCOUNT_POLICY_GAP in define_dry_run_account_policy(_ready_input(dry_run_account_policy_defined=False)).risks
    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_OBSERVABILITY_GAP in define_dry_run_observability_policy(_ready_input(dry_run_observability_policy_defined=False)).risks
    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_ROLLBACK_GAP in define_dry_run_rollback_policy(_ready_input(dry_run_rollback_policy_defined=False)).risks
    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_KILL_SWITCH_GAP in define_dry_run_kill_switch_policy(_ready_input(dry_run_kill_switch_policy_defined=False)).risks
    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_HUMAN_SUPERVISION_GAP in define_dry_run_human_supervision_policy(_ready_input(dry_run_human_supervision_policy_defined=False)).risks
    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_JOURNAL_GAP in define_dry_run_journal_policy(_ready_input(dry_run_journal_policy_defined=False)).risks
    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_STOP_CONDITION_GAP in define_dry_run_stop_conditions(_ready_input(dry_run_stop_conditions_defined=False)).risks
    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_STOP_CONDITION_GAP in define_dry_run_success_criteria(_ready_input(dry_run_success_criteria_defined=False)).risks
    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_STOP_CONDITION_GAP in define_dry_run_failure_criteria(_ready_input(dry_run_failure_criteria_defined=False)).risks


def test_detects_all_dry_run_plan_risks():
    result = evaluate_paper_broker_sandbox_dry_run_plan(
        _ready_input(
            authorization_gate_approved=False,
            dry_run_scope_clear=False,
            dry_run_boundaries_complete=False,
            dry_run_scenario_defined=False,
            dry_run_session_limits_defined=False,
            dry_run_connection_policy_defined=False,
            dry_run_order_policy_defined=False,
            dry_run_position_policy_defined=False,
            dry_run_account_policy_defined=False,
            dry_run_observability_policy_defined=False,
            dry_run_rollback_policy_defined=False,
            dry_run_kill_switch_policy_defined=False,
            dry_run_human_supervision_policy_defined=False,
            dry_run_journal_policy_defined=False,
            dry_run_stop_conditions_defined=False,
            paper_broker_sandbox_dry_run_plan_requested=False,
            paper_broker_sandbox_dry_run_execution_requested=True,
            no_http_transport=False,
        )
    )

    assert set(result.risks) == set(PaperBrokerSandboxDryRunPlanRisk)
    assert result.state is PaperBrokerSandboxDryRunPlanState.NOT_READY
    assert result.decision is PaperBrokerSandboxDryRunPlanDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN
    assert result.offline_only is False


def test_authorization_gate_gap_requires_authorization_gate_fixes_when_not_blocked():
    result = evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(authorization_gate_approved=False))

    assert result.decision is PaperBrokerSandboxDryRunPlanDecision.REQUIRE_AUTHORIZATION_GATE_FIXES


def test_scope_boundary_scenario_and_limit_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(dry_run_scope_clear=False)).decision is PaperBrokerSandboxDryRunPlanDecision.REQUIRE_SCOPE_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(dry_run_boundaries_complete=False)).decision is PaperBrokerSandboxDryRunPlanDecision.REQUIRE_BOUNDARY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(dry_run_scenario_defined=False)).decision is PaperBrokerSandboxDryRunPlanDecision.REQUIRE_SCENARIO_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(dry_run_session_limits_defined=False)).decision is PaperBrokerSandboxDryRunPlanDecision.REQUIRE_SESSION_LIMIT_FIXES


def test_connection_order_position_and_account_decisions_are_specific():
    assert evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(dry_run_connection_policy_defined=False)).decision is PaperBrokerSandboxDryRunPlanDecision.REQUIRE_CONNECTION_POLICY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(dry_run_order_policy_defined=False)).decision is PaperBrokerSandboxDryRunPlanDecision.REQUIRE_ORDER_POLICY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(dry_run_position_policy_defined=False)).decision is PaperBrokerSandboxDryRunPlanDecision.REQUIRE_POSITION_POLICY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(dry_run_account_policy_defined=False)).decision is PaperBrokerSandboxDryRunPlanDecision.REQUIRE_ACCOUNT_POLICY_FIXES


def test_observability_rollback_kill_supervision_journal_and_stop_decisions():
    assert evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(dry_run_observability_policy_defined=False)).decision is PaperBrokerSandboxDryRunPlanDecision.REQUIRE_OBSERVABILITY_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(dry_run_rollback_policy_defined=False)).decision is PaperBrokerSandboxDryRunPlanDecision.REQUIRE_ROLLBACK_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(dry_run_kill_switch_policy_defined=False)).decision is PaperBrokerSandboxDryRunPlanDecision.REQUIRE_KILL_SWITCH_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(dry_run_human_supervision_policy_defined=False)).decision is PaperBrokerSandboxDryRunPlanDecision.REQUIRE_SUPERVISION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(dry_run_journal_policy_defined=False)).decision is PaperBrokerSandboxDryRunPlanDecision.REQUIRE_JOURNAL_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(dry_run_stop_conditions_defined=False)).decision is PaperBrokerSandboxDryRunPlanDecision.REQUIRE_STOP_CONDITION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(dry_run_success_criteria_defined=False)).decision is PaperBrokerSandboxDryRunPlanDecision.REQUIRE_STOP_CONDITION_FIXES
    assert evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(dry_run_failure_criteria_defined=False)).decision is PaperBrokerSandboxDryRunPlanDecision.REQUIRE_STOP_CONDITION_FIXES


def test_premature_dry_run_execution_caps_score_and_blocks():
    data = _ready_input(paper_broker_sandbox_dry_run_execution_requested=True)
    risks = detect_dry_run_plan_risks(data)
    score = compute_dry_run_plan_score(data, risks)
    result = evaluate_paper_broker_sandbox_dry_run_plan(data)

    assert PaperBrokerSandboxDryRunPlanRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION in risks
    assert score.overall_score <= 40
    assert result.decision is PaperBrokerSandboxDryRunPlanDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN


def test_no_dry_run_execution_gap_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(no_dry_run_execution=False))

    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_BOUNDARY_GAP in result.risks
    assert PaperBrokerSandboxDryRunPlanRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION in result.risks
    assert result.offline_only is False


def test_upstream_network_leak_blocks_offline_boundary():
    result = evaluate_paper_broker_sandbox_dry_run_plan(
        _ready_input(paper_broker_sandbox_session_authorization_gate=_upstream("READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN", risks=("NETWORK_LEAK",)))
    )

    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_BOUNDARY_GAP in result.risks
    assert PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_CONNECTION_POLICY_GAP in result.risks
    assert PaperBrokerSandboxDryRunPlanRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION in result.risks
    assert result.offline_only is False


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_dry_run_plan_recommendations(
        (
            PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_KILL_SWITCH_GAP,
            PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_KILL_SWITCH_GAP,
            PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_STOP_CONDITION_GAP,
            PaperBrokerSandboxDryRunPlanRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION,
        ),
        PaperBrokerSandboxDryRunPlanDecision.REQUIRE_KILL_SWITCH_FIXES,
    )

    assert recommendations.count(PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_KILL_SWITCH_POLICY) == 1
    assert PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_STOP_CONDITIONS in recommendations
    assert PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_SUCCESS_AND_FAILURE_CRITERIA in recommendations
    assert PaperBrokerSandboxDryRunPlanRecommendation.DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION in recommendations
    assert PaperBrokerSandboxDryRunPlanRecommendation.RUN_PAPER_BROKER_SANDBOX_DRY_RUN_PLAN_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_dry_run_plan_recommendations(
        (),
        PaperBrokerSandboxDryRunPlanDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PLAN,
    )

    assert PaperBrokerSandboxDryRunPlanRecommendation.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW in recommendations


def test_markdown_contains_decision_risks_and_recommendations():
    result = evaluate_paper_broker_sandbox_dry_run_plan(_ready_input(dry_run_kill_switch_policy_defined=False))
    markdown = render_paper_broker_sandbox_dry_run_plan_markdown(result)

    assert "# AGIcore Paper Broker Sandbox Dry Run Plan" in markdown
    assert "Decision: REQUIRE_KILL_SWITCH_FIXES" in markdown
    assert "DRY_RUN_KILL_SWITCH_GAP" in markdown
    assert "DEFINE_DRY_RUN_KILL_SWITCH_POLICY" in markdown


def test_mapping_inputs_are_supported_and_extra_keys_are_ignored():
    payload = dict(_ready_input().__dict__)
    payload["ignored_future_key"] = "ignored"
    result = evaluate_paper_broker_sandbox_dry_run_plan(payload)

    assert result.state is PaperBrokerSandboxDryRunPlanState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_CONNECTION_POLICY_GAP, PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_CONNECTION_POLICY),
        (PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_ORDER_POLICY_GAP, PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_ORDER_POLICY),
        (PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_POSITION_POLICY_GAP, PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_POSITION_POLICY),
        (PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_ACCOUNT_POLICY_GAP, PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_ACCOUNT_POLICY),
        (PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_JOURNAL_GAP, PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_JOURNAL_POLICY),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_dry_run_plan_recommendations((risk,), PaperBrokerSandboxDryRunPlanDecision.REQUIRE_BOUNDARY_FIXES)


@pytest.mark.parametrize(
    "module_name",
    [
        "paper_broker_sandbox_dry_run_plan.py",
        "paper_broker_sandbox_dry_run_plan_models.py",
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

