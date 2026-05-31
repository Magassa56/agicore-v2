import ast
from pathlib import Path

import pytest

from agicore.trading.extended_paper_runtime_test import (
    compute_extended_runtime_score,
    detect_extended_runtime_risks,
    evaluate_extended_paper_runtime_test,
    generate_extended_runtime_recommendations,
    render_extended_paper_runtime_test_markdown,
    run_extended_runtime_scenarios,
    run_human_supervision_pause_scenario,
    run_journal_failure_scenario,
    run_kill_switch_scenario,
    run_nominal_runtime_scenario,
    run_observability_gap_scenario,
    run_rollback_scenario,
    run_runtime_state_drift_scenario,
    run_safety_gate_block_scenario,
    verify_multi_scenario_consistency,
)
from agicore.trading.extended_paper_runtime_test_models import (
    ExtendedPaperRuntimeTestDecision,
    ExtendedPaperRuntimeTestInput,
    ExtendedPaperRuntimeTestRecommendation,
    ExtendedPaperRuntimeTestRisk,
    ExtendedPaperRuntimeTestState,
)


def _upstream(state="READY", decision=None, risks=()):
    payload = {"state": state, "risks": tuple(risks), "offline_only": True}
    if decision:
        payload["decision"] = decision
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_runtime_test_run": _upstream("READY_FOR_EXTENDED_PAPER_RUNTIME_TEST", "READY_FOR_EXTENDED_PAPER_RUNTIME_TEST"),
        "paper_runtime_integration_review": _upstream("READY_FOR_PAPER_RUNTIME_TEST_RUN", "READY_FOR_PAPER_RUNTIME_TEST_RUN"),
        "paper_trading_runtime_design": _upstream("READY_FOR_RUNTIME_IMPLEMENTATION", "APPROVE_RUNTIME_IMPLEMENTATION"),
        "paper_runtime_decision_review": _upstream("READY_FOR_PAPER_TRADING_RUNTIME", "APPROVE_PAPER_TRADING_RUNTIME_CREATION"),
        "full_paper_session": _upstream("READY_FOR_PAPER_TRADING_RUNTIME"),
        "simulated_market_session": _upstream("READY_FOR_FULL_PAPER_SESSION"),
        "mock_alpaca_session": _upstream("READY_FOR_SIMULATED_MARKET_SESSION"),
        "mock_connectivity_layer": _upstream("READY_FOR_MOCK_ALPACA_SESSION"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "extended_test_requested": True,
        "ready_for_stabilization_review": True,
        "scenarios_repeatable": True,
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
    return ExtendedPaperRuntimeTestInput(**payload)


def test_evaluate_ready_for_stabilization_review():
    result = evaluate_extended_paper_runtime_test(_ready_input())

    assert result.state is ExtendedPaperRuntimeTestState.READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW
    assert result.decision is ExtendedPaperRuntimeTestDecision.READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW
    assert result.risks == ()
    assert result.offline_only is True
    assert result.extended_runtime_score == 100


def test_extended_test_completed_without_stabilization_gate():
    result = evaluate_extended_paper_runtime_test(_ready_input(ready_for_stabilization_review=False))

    assert result.state is ExtendedPaperRuntimeTestState.EXTENDED_TEST_COMPLETED
    assert result.decision is ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_COMPLETED


def test_all_required_scenarios_run_and_are_handled():
    scenarios = run_extended_runtime_scenarios(_ready_input())

    assert tuple(scenario.name for scenario in scenarios) == (
        "nominal",
        "safety_gate_block",
        "rollback",
        "kill_switch",
        "human_supervision_pause",
        "journal_failure",
        "observability_gap",
        "runtime_state_drift",
    )
    assert all(scenario.handled for scenario in scenarios)
    assert all(scenario.passed for scenario in scenarios)


def test_individual_scenarios_expect_safe_terminal_states():
    data = _ready_input()

    assert run_nominal_runtime_scenario(data).actual_state == "COMPLETED"
    assert run_safety_gate_block_scenario(data).actual_state == "FAILED_SAFE"
    assert run_rollback_scenario(data).actual_state == "STOPPED_BY_ROLLBACK"
    assert run_kill_switch_scenario(data).actual_state == "STOPPED_BY_KILL_SWITCH"
    assert run_human_supervision_pause_scenario(data).actual_state == "PAUSED_BY_SUPERVISION"
    assert run_journal_failure_scenario(data).actual_state == "FAILED_SAFE"
    assert run_observability_gap_scenario(data).actual_state == "FAILED_SAFE"
    assert run_runtime_state_drift_scenario(data).actual_state == "FAILED_SAFE"


def test_multi_scenario_consistency_passes_for_ready_input():
    scenarios = run_extended_runtime_scenarios(_ready_input())
    consistency = verify_multi_scenario_consistency(_ready_input(), scenarios)

    assert consistency.passed is True
    assert consistency.risks == ()
    assert consistency.score == 100


def test_nominal_scenario_failure_blocks_extended_test():
    result = evaluate_extended_paper_runtime_test(_ready_input(nominal_score=40))

    assert ExtendedPaperRuntimeTestRisk.NOMINAL_SCENARIO_FAILURE in result.risks
    assert result.decision is ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_BLOCKED
    assert result.state is ExtendedPaperRuntimeTestState.NOT_READY


def test_each_scenario_risk_can_be_detected_by_score_override():
    cases = [
        ("safety_gate_block_score", ExtendedPaperRuntimeTestRisk.SAFETY_GATE_BLOCK_FAILURE),
        ("rollback_score", ExtendedPaperRuntimeTestRisk.ROLLBACK_SCENARIO_FAILURE),
        ("kill_switch_score", ExtendedPaperRuntimeTestRisk.KILL_SWITCH_SCENARIO_FAILURE),
        ("human_supervision_pause_score", ExtendedPaperRuntimeTestRisk.HUMAN_SUPERVISION_PAUSE_FAILURE),
        ("journal_failure_score", ExtendedPaperRuntimeTestRisk.JOURNAL_FAILURE_UNHANDLED),
        ("observability_gap_score", ExtendedPaperRuntimeTestRisk.OBSERVABILITY_GAP_UNHANDLED),
        ("runtime_state_drift_score", ExtendedPaperRuntimeTestRisk.RUNTIME_STATE_DRIFT_UNHANDLED),
    ]
    for field, risk in cases:
        result = evaluate_extended_paper_runtime_test(_ready_input(**{field: 40}))
        assert risk in result.risks


def test_not_repeatable_produces_consistency_risk():
    result = evaluate_extended_paper_runtime_test(_ready_input(scenarios_repeatable=False))

    assert ExtendedPaperRuntimeTestRisk.EXTENDED_TEST_NOT_REPEATABLE in result.risks
    assert result.state is ExtendedPaperRuntimeTestState.EXTENDED_TEST_PARTIALLY_READY


def test_scope_drift_caps_score_and_blocks():
    data = _ready_input(no_http_transport=False)
    scenarios = run_extended_runtime_scenarios(data)
    consistency = verify_multi_scenario_consistency(data, scenarios)
    risks = detect_extended_runtime_risks(data, scenarios, consistency)
    score = compute_extended_runtime_score(data, risks, scenarios, consistency)
    result = evaluate_extended_paper_runtime_test(data)

    assert ExtendedPaperRuntimeTestRisk.RUNTIME_STABILITY_RISK in risks
    assert score.overall_score <= 40
    assert result.decision is ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_BLOCKED
    assert result.offline_only is False


def test_upstream_network_leak_blocks_extended_test():
    result = evaluate_extended_paper_runtime_test(_ready_input(paper_runtime_test_run=_upstream(risks=("NETWORK_LEAK",))))

    assert ExtendedPaperRuntimeTestRisk.RUNTIME_STABILITY_RISK in result.risks
    assert result.offline_only is False


def test_multiple_hard_scenario_risks_require_review():
    result = evaluate_extended_paper_runtime_test(_ready_input(rollback_score=40, kill_switch_score=40))

    assert result.decision is ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_REVIEW_REQUIRED
    assert result.state is ExtendedPaperRuntimeTestState.EXTENDED_TEST_REVIEW_REQUIRED


def test_soft_single_scenario_risk_is_partially_ready():
    result = evaluate_extended_paper_runtime_test(_ready_input(journal_failure_score=80))

    assert result.decision is ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_PARTIALLY_READY
    assert result.state is ExtendedPaperRuntimeTestState.EXTENDED_TEST_PARTIALLY_READY
    assert result.risks == (ExtendedPaperRuntimeTestRisk.JOURNAL_FAILURE_UNHANDLED,)


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_extended_runtime_recommendations(
        (
            ExtendedPaperRuntimeTestRisk.KILL_SWITCH_SCENARIO_FAILURE,
            ExtendedPaperRuntimeTestRisk.KILL_SWITCH_SCENARIO_FAILURE,
            ExtendedPaperRuntimeTestRisk.MULTI_SCENARIO_INCONSISTENCY,
            ExtendedPaperRuntimeTestRisk.RUNTIME_STABILITY_RISK,
        ),
        ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_REVIEW_REQUIRED,
    )

    assert recommendations.count(ExtendedPaperRuntimeTestRecommendation.REPAIR_KILL_SWITCH_SCENARIO) == 1
    assert ExtendedPaperRuntimeTestRecommendation.RECONCILE_MULTI_SCENARIO_CONSISTENCY in recommendations
    assert ExtendedPaperRuntimeTestRecommendation.REPAIR_RUNTIME_STABILITY in recommendations
    assert ExtendedPaperRuntimeTestRecommendation.RUN_EXTENDED_PAPER_RUNTIME_TEST_SUITE in recommendations


def test_approval_recommendation_follows_stabilization_decision():
    recommendations = generate_extended_runtime_recommendations(
        (),
        ExtendedPaperRuntimeTestDecision.READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW,
    )

    assert ExtendedPaperRuntimeTestRecommendation.APPROVE_STABILIZATION_REVIEW_AFTER_MANUAL_REVIEW in recommendations


def test_markdown_contains_scenarios_risks_and_recommendations():
    result = evaluate_extended_paper_runtime_test(_ready_input(kill_switch_score=40))
    markdown = render_extended_paper_runtime_test_markdown(result)

    assert "# AGIcore Extended Paper Runtime Test" in markdown
    assert "Decision: EXTENDED_TEST_REVIEW_REQUIRED" in markdown
    assert "# Runtime Scenarios" in markdown
    assert "KILL_SWITCH_SCENARIO_FAILURE" in markdown
    assert "REPAIR_KILL_SWITCH_SCENARIO" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_extended_paper_runtime_test(_ready_input().__dict__)

    assert result.state is ExtendedPaperRuntimeTestState.READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (ExtendedPaperRuntimeTestRisk.SAFETY_GATE_BLOCK_FAILURE, ExtendedPaperRuntimeTestRecommendation.REPAIR_SAFETY_GATE_BLOCK_HANDLING),
        (ExtendedPaperRuntimeTestRisk.OBSERVABILITY_GAP_UNHANDLED, ExtendedPaperRuntimeTestRecommendation.HANDLE_OBSERVABILITY_GAP),
        (ExtendedPaperRuntimeTestRisk.EXTENDED_TEST_NOT_REPEATABLE, ExtendedPaperRuntimeTestRecommendation.STABILIZE_REPEATABILITY),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_extended_runtime_recommendations((risk,), ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_REVIEW_REQUIRED)


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "extended_paper_runtime_test.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
