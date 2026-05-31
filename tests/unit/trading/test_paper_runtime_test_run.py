import ast
from pathlib import Path

import pytest

from agicore.trading.paper_runtime_test_run import (
    compute_test_run_score,
    detect_test_run_risks,
    evaluate_paper_runtime_test_run,
    generate_test_run_recommendations,
    render_paper_runtime_test_run_markdown,
    run_runtime_test_scenario,
    verify_runtime_decision_cycle,
    verify_runtime_human_supervision_hook,
    verify_runtime_journal_output,
    verify_runtime_kill_switch_hook,
    verify_runtime_market_cycle,
    verify_runtime_observability_output,
    verify_runtime_paper_order_simulation,
    verify_runtime_position_pnl_update,
    verify_runtime_rollback_hook,
    verify_runtime_safety_gate,
    verify_runtime_session_init,
    verify_runtime_signal_cycle,
    verify_runtime_start,
    verify_runtime_stop,
)
from agicore.trading.paper_runtime_test_run_models import (
    PaperRuntimeTestRunDecision,
    PaperRuntimeTestRunInput,
    PaperRuntimeTestRunRecommendation,
    PaperRuntimeTestRunRisk,
    PaperRuntimeTestRunState,
)
from agicore.trading.paper_trading_runtime_models import PaperTradingRuntimeInput


def _upstream(state="READY", decision=None, risks=()):
    payload = {"state": state, "risks": tuple(risks), "offline_only": True}
    if decision:
        payload["decision"] = decision
    return payload


def _runtime_input(**overrides):
    payload = {
        "session_id": "test-run-rt",
        "symbol": "ES.TEST.PAPER",
        "market_price": 101.0,
        "previous_price": 100.0,
        "quantity": 2.0,
        "approved_by_human": True,
        "operator_confirmed": True,
        "session_authorized": True,
        "safety_gate_enabled": True,
        "risk_limits_enforced": True,
        "paper_order_not_routed": True,
        "journal_enabled": True,
        "observability_enabled": True,
        "rollback_hook_available": True,
        "kill_switch_hook_available": True,
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
    return PaperTradingRuntimeInput(**payload)


def _ready_input(**overrides):
    payload = {
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
        "runtime_input": _runtime_input(),
        "test_run_requested": True,
        "ready_for_extended_test": True,
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
    return PaperRuntimeTestRunInput(**payload)


def test_evaluate_ready_for_extended_paper_runtime_test():
    result = evaluate_paper_runtime_test_run(_ready_input())

    assert result.state is PaperRuntimeTestRunState.READY_FOR_EXTENDED_PAPER_RUNTIME_TEST
    assert result.decision is PaperRuntimeTestRunDecision.READY_FOR_EXTENDED_PAPER_RUNTIME_TEST
    assert result.risks == ()
    assert result.offline_only is True
    assert result.test_run_score == 100
    assert result.runtime_result.order.routed is False


def test_test_run_completed_without_extended_gate():
    result = evaluate_paper_runtime_test_run(_ready_input(ready_for_extended_test=False))

    assert result.state is PaperRuntimeTestRunState.TEST_RUN_COMPLETED
    assert result.decision is PaperRuntimeTestRunDecision.TEST_RUN_COMPLETED


def test_runtime_test_scenario_executes_runtime_once():
    scenario = run_runtime_test_scenario(_ready_input())

    assert scenario.runtime_result.state.value == "COMPLETED"
    assert len(scenario.checks) == 14
    assert all(check.passed for check in scenario.checks)


def test_verify_functions_pass_for_nominal_runtime():
    data = _ready_input()
    scenario = run_runtime_test_scenario(data)
    runtime = scenario.runtime_result

    assert verify_runtime_start(data, runtime).passed is True
    assert verify_runtime_session_init(data, runtime).passed is True
    assert verify_runtime_market_cycle(data, runtime).passed is True
    assert verify_runtime_signal_cycle(data, runtime).passed is True
    assert verify_runtime_decision_cycle(data, runtime).passed is True
    assert verify_runtime_safety_gate(data, runtime).passed is True
    assert verify_runtime_paper_order_simulation(data, runtime).passed is True
    assert verify_runtime_position_pnl_update(data, runtime).passed is True
    assert verify_runtime_journal_output(data, runtime).passed is True
    assert verify_runtime_observability_output(data, runtime).passed is True
    assert verify_runtime_rollback_hook(data, runtime).passed is True
    assert verify_runtime_kill_switch_hook(data, runtime).passed is True
    assert verify_runtime_human_supervision_hook(data, runtime).passed is True
    assert verify_runtime_stop(data, runtime).passed is True


def test_each_runtime_failure_maps_to_test_run_risk():
    cases = [
        ({"runtime_input": _runtime_input(session_id="")}, PaperRuntimeTestRunRisk.SESSION_INIT_FAILURE),
        ({"runtime_input": _runtime_input(force_market_failure=True)}, PaperRuntimeTestRunRisk.MARKET_CYCLE_FAILURE),
        ({"runtime_input": _runtime_input(force_signal_failure=True)}, PaperRuntimeTestRunRisk.SIGNAL_CYCLE_FAILURE),
        ({"runtime_input": _runtime_input(force_decision_failure=True)}, PaperRuntimeTestRunRisk.DECISION_CYCLE_FAILURE),
        ({"runtime_input": _runtime_input(risk_limits_enforced=False)}, PaperRuntimeTestRunRisk.SAFETY_GATE_FAILURE),
        ({"runtime_input": _runtime_input(force_order_failure=True)}, PaperRuntimeTestRunRisk.PAPER_ORDER_SIMULATION_FAILURE),
        ({"runtime_input": _runtime_input(force_position_failure=True)}, PaperRuntimeTestRunRisk.POSITION_PNL_UPDATE_FAILURE),
        ({"runtime_input": _runtime_input(force_journal_failure=True)}, PaperRuntimeTestRunRisk.JOURNAL_OUTPUT_FAILURE),
        ({"runtime_input": _runtime_input(force_observability_failure=True)}, PaperRuntimeTestRunRisk.OBSERVABILITY_OUTPUT_FAILURE),
        ({"runtime_input": _runtime_input(rollback_hook_available=False)}, PaperRuntimeTestRunRisk.ROLLBACK_HOOK_FAILURE),
        ({"runtime_input": _runtime_input(kill_switch_hook_available=False)}, PaperRuntimeTestRunRisk.KILL_SWITCH_HOOK_FAILURE),
        ({"runtime_input": _runtime_input(approved_by_human=False)}, PaperRuntimeTestRunRisk.HUMAN_SUPERVISION_HOOK_FAILURE),
    ]
    for override, risk in cases:
        result = evaluate_paper_runtime_test_run(_ready_input(**override))
        assert risk in result.risks


def test_runtime_start_failure_when_test_not_requested():
    result = evaluate_paper_runtime_test_run(_ready_input(test_run_requested=False))

    assert result.state is PaperRuntimeTestRunState.NOT_READY
    assert result.decision is PaperRuntimeTestRunDecision.TEST_RUN_BLOCKED
    assert PaperRuntimeTestRunRisk.RUNTIME_START_FAILURE in result.risks


def test_runtime_stop_failure_when_runtime_does_not_complete():
    result = evaluate_paper_runtime_test_run(_ready_input(runtime_input=_runtime_input(rollback_requested=True)))

    assert PaperRuntimeTestRunRisk.RUNTIME_STOP_FAILURE in result.risks
    assert result.state is PaperRuntimeTestRunState.TEST_REVIEW_REQUIRED


def test_scope_drift_caps_score_and_blocks_test_run():
    data = _ready_input(no_http_transport=False)
    scenario = run_runtime_test_scenario(data)
    risks = detect_test_run_risks(data, *scenario.checks)
    score = compute_test_run_score(data, risks, *scenario.checks)
    result = evaluate_paper_runtime_test_run(data)

    assert PaperRuntimeTestRunRisk.TEST_RUN_STATE_DRIFT in risks
    assert score.overall_score <= 40
    assert result.decision is PaperRuntimeTestRunDecision.TEST_RUN_BLOCKED


def test_runtime_order_routing_violation_is_detected():
    data = _ready_input(runtime_input=_runtime_input(paper_order_not_routed=False))
    result = evaluate_paper_runtime_test_run(data)

    assert PaperRuntimeTestRunRisk.TEST_RUN_STATE_DRIFT in result.risks
    assert result.offline_only is False


def test_upstream_network_leak_blocks_offline_boundary():
    result = evaluate_paper_runtime_test_run(
        _ready_input(paper_runtime_integration_review=_upstream("READY_FOR_PAPER_RUNTIME_TEST_RUN", risks=("NETWORK_LEAK",)))
    )

    assert PaperRuntimeTestRunRisk.TEST_RUN_STATE_DRIFT in result.risks
    assert result.offline_only is False


def test_single_soft_observability_gap_is_partially_ready():
    result = evaluate_paper_runtime_test_run(
        _ready_input(observability_verification=_upstream(risks=("OBSERVABILITY_GAP",)), observability_output_score=88)
    )

    assert result.state is PaperRuntimeTestRunState.TEST_PARTIALLY_READY
    assert result.decision is PaperRuntimeTestRunDecision.TEST_RUN_PARTIALLY_READY
    assert PaperRuntimeTestRunRisk.OBSERVABILITY_OUTPUT_FAILURE in result.risks


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_test_run_recommendations(
        (
            PaperRuntimeTestRunRisk.SAFETY_GATE_FAILURE,
            PaperRuntimeTestRunRisk.SAFETY_GATE_FAILURE,
            PaperRuntimeTestRunRisk.RUNTIME_STOP_FAILURE,
            PaperRuntimeTestRunRisk.TEST_RUN_STATE_DRIFT,
        ),
        PaperRuntimeTestRunDecision.TEST_RUN_REVIEW_REQUIRED,
    )

    assert recommendations.count(PaperRuntimeTestRunRecommendation.REPAIR_SAFETY_GATE) == 1
    assert PaperRuntimeTestRunRecommendation.REPAIR_RUNTIME_STOP in recommendations
    assert PaperRuntimeTestRunRecommendation.RECONCILE_TEST_RUN_STATE in recommendations
    assert PaperRuntimeTestRunRecommendation.RUN_PAPER_RUNTIME_TEST_RUN_SUITE in recommendations


def test_approval_recommendation_follows_extended_decision():
    recommendations = generate_test_run_recommendations((), PaperRuntimeTestRunDecision.READY_FOR_EXTENDED_PAPER_RUNTIME_TEST)

    assert PaperRuntimeTestRunRecommendation.APPROVE_EXTENDED_TEST_AFTER_MANUAL_REVIEW in recommendations


def test_markdown_contains_checks_risks_and_recommendations():
    result = evaluate_paper_runtime_test_run(_ready_input(runtime_input=_runtime_input(force_order_failure=True)))
    markdown = render_paper_runtime_test_run_markdown(result)

    assert "# AGIcore Paper Runtime Test Run" in markdown
    assert "Decision: TEST_RUN_REVIEW_REQUIRED" in markdown
    assert "# Runtime Test Checks" in markdown
    assert "PAPER_ORDER_SIMULATION_FAILURE" in markdown
    assert "REPAIR_PAPER_ORDER_SIMULATION" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_paper_runtime_test_run(_ready_input().__dict__)

    assert result.state is PaperRuntimeTestRunState.READY_FOR_EXTENDED_PAPER_RUNTIME_TEST


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (PaperRuntimeTestRunRisk.MARKET_CYCLE_FAILURE, PaperRuntimeTestRunRecommendation.REPAIR_MARKET_CYCLE),
        (PaperRuntimeTestRunRisk.KILL_SWITCH_HOOK_FAILURE, PaperRuntimeTestRunRecommendation.REPAIR_KILL_SWITCH_HOOK),
        (PaperRuntimeTestRunRisk.HUMAN_SUPERVISION_HOOK_FAILURE, PaperRuntimeTestRunRecommendation.REPAIR_HUMAN_SUPERVISION_HOOK),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_test_run_recommendations((risk,), PaperRuntimeTestRunDecision.TEST_RUN_REVIEW_REQUIRED)


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "paper_runtime_test_run.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
