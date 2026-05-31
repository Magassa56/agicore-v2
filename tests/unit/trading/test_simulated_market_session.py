import ast
from pathlib import Path

import pytest

from agicore.trading.simulated_market_session import (
    compute_market_session_score,
    detect_market_session_risks,
    evaluate_simulated_market_session,
    generate_market_session_recommendations,
    render_simulated_market_session_markdown,
    simulate_decision_generation_flow,
    simulate_market_data_flow,
    simulate_paper_order_lifecycle,
    simulate_paper_pnl_flow,
    simulate_position_lifecycle,
    simulate_session_journal_flow,
    simulate_session_observability_flow,
    simulate_signal_generation_flow,
)
from agicore.trading.simulated_market_session_models import (
    SimulatedMarketSessionInput,
    SimulatedMarketSessionRecommendation,
    SimulatedMarketSessionRisk,
    SimulatedMarketSessionState,
)


def _upstream(state="READY", score=96, risks=(), blockers=(), **extra):
    payload = {
        "state": state,
        "score": score,
        "risks": tuple(risks),
        "blockers": tuple(blockers),
        "offline_only": True,
        "score_breakdown": {
            "mock_alpaca_session_score": score,
            "mock_connectivity_score": score,
            "connectivity_score": score,
            "sandbox_score": score,
            "end_to_end_score": score,
            "dry_run_score": score,
            "trial_score": score,
            "observability_score": score,
            "kill_switch_score": score,
            "rollback_score": score,
        },
    }
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
        "mock_alpaca_session": _upstream("READY_FOR_SIMULATED_MARKET_SESSION"),
        "mock_connectivity_layer": _upstream("READY_FOR_MOCK_ALPACA_SESSION"),
        "alpaca_paper_connectivity_readiness": _upstream("READY_FOR_MOCK_CONNECTIVITY"),
        "broker_paper_sandbox": _upstream("READY_FOR_ALPACA_PAPER_CONNECTIVITY"),
        "paper_trading_end_to_end": _upstream("READY_FOR_PAPER_DRY_RUN"),
        "paper_dry_run": _upstream("READY_FOR_SUPERVISED_PAPER_TRIAL"),
        "supervised_paper_trial": _upstream("READY_FOR_BROKER_PAPER_SANDBOX"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "fictive_market_data_available": True,
        "market_data_schema_valid": True,
        "market_data_sequence_ordered": True,
        "market_data_replayable": True,
        "signal_inputs_available": True,
        "signal_generation_deterministic": True,
        "signal_schema_valid": True,
        "signal_traceable": True,
        "decision_inputs_available": True,
        "decision_generation_deterministic": True,
        "decision_schema_valid": True,
        "decision_safety_checked": True,
        "paper_order_created": True,
        "paper_order_validated": True,
        "paper_order_status_progressed": True,
        "paper_order_not_routed": True,
        "position_opened": True,
        "position_updated": True,
        "position_closed_or_carried": True,
        "position_reconciled": True,
        "paper_pnl_calculated": True,
        "paper_pnl_reconciled": True,
        "paper_pnl_traceable": True,
        "paper_pnl_deterministic": True,
        "session_journal_created": True,
        "session_journal_complete": True,
        "session_journal_replayable": True,
        "session_journal_traceable": True,
        "observability_events_emitted": True,
        "metrics_recorded": True,
        "traces_recorded": True,
        "alerts_recorded": True,
        "session_state_snapshot_consistent": True,
        "session_state_replay_consistent": True,
        "session_state_recovery_verified": True,
        "session_state_isolated": True,
        "offline_mode_enforced": True,
        "no_real_broker": True,
        "no_api_key_read": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_api": True,
        "no_real_order": True,
        "safety_gate_enforced": True,
        "kill_switch_linked": True,
        "rollback_linked": True,
        "simulated_session_completed": True,
        "ready_for_full_paper_session": True,
        "market_data_score": 96,
        "signal_generation_score": 96,
        "decision_generation_score": 96,
        "paper_order_lifecycle_score": 96,
        "position_lifecycle_score": 96,
        "paper_pnl_score": 96,
        "session_journal_score": 96,
        "session_observability_score": 96,
    }
    payload.update(overrides)
    return SimulatedMarketSessionInput(**payload)


def test_evaluate_ready_for_full_paper_session():
    result = evaluate_simulated_market_session(_ready_input())

    assert result.state is SimulatedMarketSessionState.READY_FOR_FULL_PAPER_SESSION
    assert result.risks == ()
    assert result.offline_only is True
    assert result.market_session_score >= 94
    assert result.market_session_graph.blocked_edges == ()


def test_simulated_session_completed_when_full_paper_gate_is_not_set():
    result = evaluate_simulated_market_session(_ready_input(ready_for_full_paper_session=False))

    assert result.state is SimulatedMarketSessionState.SIMULATED_SESSION_COMPLETED
    assert result.risks == ()


def test_simulated_session_ready_when_not_completed_yet():
    result = evaluate_simulated_market_session(_ready_input(simulated_session_completed=False))

    assert result.state is SimulatedMarketSessionState.SIMULATED_SESSION_READY
    assert result.risks == ()


def test_detects_every_market_session_risk_when_all_flows_fail():
    failing_fields = {
        name: False
        for name in SimulatedMarketSessionInput.__dataclass_fields__
        if (
            name.endswith(
                (
                    "_available",
                    "_valid",
                    "_ordered",
                    "_replayable",
                    "_deterministic",
                    "_traceable",
                    "_checked",
                    "_created",
                    "_validated",
                    "_progressed",
                    "_routed",
                    "_opened",
                    "_updated",
                    "_carried",
                    "_reconciled",
                    "_calculated",
                    "_complete",
                    "_emitted",
                    "_recorded",
                    "_consistent",
                    "_verified",
                    "_isolated",
                    "_enforced",
                    "_broker",
                    "_read",
                    "_transport",
                    "_api",
                    "_order",
                    "_linked",
                    "_completed",
                    "_session",
                )
            )
            and not name.endswith("_score")
        )
    }
    score_fields = {
        name: 10
        for name in SimulatedMarketSessionInput.__dataclass_fields__
        if name.endswith("_score")
    }

    result = evaluate_simulated_market_session(_ready_input(**failing_fields, **score_fields))

    assert set(result.risks) == set(SimulatedMarketSessionRisk)
    assert result.state is SimulatedMarketSessionState.NOT_READY
    assert result.offline_only is False


def test_market_data_flow_detects_missing_data_and_state_drift():
    flow = simulate_market_data_flow(_ready_input(fictive_market_data_available=False, market_data_replayable=False))

    assert flow.passed is False
    assert SimulatedMarketSessionRisk.MARKET_DATA_MISSING in flow.risks
    assert SimulatedMarketSessionRisk.SESSION_STATE_DRIFT in flow.risks


def test_signal_generation_flow_detects_failure_and_observability_gap():
    flow = simulate_signal_generation_flow(_ready_input(signal_schema_valid=False, signal_traceable=False))

    assert flow.passed is False
    assert SimulatedMarketSessionRisk.SIGNAL_GENERATION_FAILURE in flow.risks
    assert SimulatedMarketSessionRisk.OBSERVABILITY_GAP in flow.risks


def test_decision_generation_flow_detects_failure_and_safety_bypass():
    flow = simulate_decision_generation_flow(_ready_input(decision_schema_valid=False, decision_safety_checked=False))

    assert flow.passed is False
    assert SimulatedMarketSessionRisk.DECISION_GENERATION_FAILURE in flow.risks
    assert SimulatedMarketSessionRisk.SAFETY_BOUNDARY_BYPASS in flow.risks


def test_paper_order_lifecycle_detects_order_failure_and_safety_bypass():
    flow = simulate_paper_order_lifecycle(_ready_input(paper_order_validated=False, paper_order_not_routed=False))

    assert flow.passed is False
    assert SimulatedMarketSessionRisk.ORDER_LIFECYCLE_FAILURE in flow.risks
    assert SimulatedMarketSessionRisk.SAFETY_BOUNDARY_BYPASS in flow.risks


def test_position_lifecycle_detects_position_failure_and_state_drift():
    flow = simulate_position_lifecycle(_ready_input(position_updated=False, position_reconciled=False))

    assert flow.passed is False
    assert SimulatedMarketSessionRisk.POSITION_LIFECYCLE_FAILURE in flow.risks
    assert SimulatedMarketSessionRisk.SESSION_STATE_DRIFT in flow.risks


def test_paper_pnl_flow_detects_pnl_failure_and_observability_gap():
    flow = simulate_paper_pnl_flow(_ready_input(paper_pnl_reconciled=False, paper_pnl_traceable=False))

    assert flow.passed is False
    assert SimulatedMarketSessionRisk.PNL_CALCULATION_FAILURE in flow.risks
    assert SimulatedMarketSessionRisk.OBSERVABILITY_GAP in flow.risks


def test_session_journal_flow_detects_incomplete_journal_observability_and_drift():
    flow = simulate_session_journal_flow(
        _ready_input(
            session_journal_complete=False,
            session_journal_replayable=False,
            session_journal_traceable=False,
        )
    )

    assert flow.passed is False
    assert SimulatedMarketSessionRisk.JOURNAL_INCOMPLETE in flow.risks
    assert SimulatedMarketSessionRisk.OBSERVABILITY_GAP in flow.risks
    assert SimulatedMarketSessionRisk.SESSION_STATE_DRIFT in flow.risks


def test_session_observability_flow_detects_gap():
    flow = simulate_session_observability_flow(_ready_input(metrics_recorded=False))

    assert flow.passed is False
    assert flow.risks == (SimulatedMarketSessionRisk.OBSERVABILITY_GAP,)


def test_three_soft_risks_require_review():
    result = evaluate_simulated_market_session(
        _ready_input(
            signal_schema_valid=False,
            paper_pnl_reconciled=False,
            session_journal_complete=False,
            paper_pnl_traceable=True,
            session_journal_replayable=True,
            session_journal_traceable=True,
        )
    )

    assert result.state is SimulatedMarketSessionState.REVIEW_REQUIRED
    assert SimulatedMarketSessionRisk.SIGNAL_GENERATION_FAILURE in result.risks
    assert SimulatedMarketSessionRisk.PNL_CALCULATION_FAILURE in result.risks
    assert SimulatedMarketSessionRisk.JOURNAL_INCOMPLETE in result.risks


def test_single_soft_risk_is_partially_ready():
    result = evaluate_simulated_market_session(_ready_input(signal_schema_valid=False, signal_generation_score=86))

    assert result.state is SimulatedMarketSessionState.PARTIALLY_READY
    assert result.risks == (SimulatedMarketSessionRisk.SIGNAL_GENERATION_FAILURE,)


def test_hard_risk_caps_score_and_not_ready():
    data = _ready_input(no_http_transport=False)
    risks = detect_market_session_risks(data)
    score = compute_market_session_score(data, risks)
    result = evaluate_simulated_market_session(data)

    assert SimulatedMarketSessionRisk.SAFETY_BOUNDARY_BYPASS in risks
    assert score.overall_score <= 40
    assert result.state is SimulatedMarketSessionState.NOT_READY


def test_upstream_network_leak_keeps_market_session_offline_boundary_closed():
    upstream = _upstream(risks=("NETWORK_LEAK",))
    result = evaluate_simulated_market_session(_ready_input(mock_alpaca_session=upstream))

    assert result.state is SimulatedMarketSessionState.NOT_READY
    assert result.offline_only is False
    assert SimulatedMarketSessionRisk.SAFETY_BOUNDARY_BYPASS in result.risks


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_market_session_recommendations(
        (
            SimulatedMarketSessionRisk.ORDER_LIFECYCLE_FAILURE,
            SimulatedMarketSessionRisk.ORDER_LIFECYCLE_FAILURE,
            SimulatedMarketSessionRisk.OBSERVABILITY_GAP,
            SimulatedMarketSessionRisk.SAFETY_BOUNDARY_BYPASS,
        ),
        SimulatedMarketSessionState.PARTIALLY_READY,
    )

    assert recommendations.count(SimulatedMarketSessionRecommendation.REPAIR_ORDER_LIFECYCLE) == 1
    assert SimulatedMarketSessionRecommendation.RESTORE_SESSION_OBSERVABILITY in recommendations
    assert SimulatedMarketSessionRecommendation.ENFORCE_MARKET_SESSION_SAFETY_BOUNDARY in recommendations
    assert SimulatedMarketSessionRecommendation.RUN_SIMULATED_MARKET_SESSION_SUITE in recommendations


def test_ready_state_adds_full_paper_session_approval_recommendation():
    result = evaluate_simulated_market_session(_ready_input())

    assert (
        SimulatedMarketSessionRecommendation.APPROVE_FULL_PAPER_SESSION_AFTER_MANUAL_REVIEW
        in result.recommendations
    )


def test_markdown_rendering_contains_flows_graph_risks_and_recommendations():
    result = evaluate_simulated_market_session(_ready_input(paper_order_validated=False))
    markdown = render_simulated_market_session_markdown(result)

    assert "# AGIcore Simulated Market Session" in markdown
    assert "# Score Breakdown" in markdown
    assert "# Simulated Market Flows" in markdown
    assert "# Simulated Market Session Graph" in markdown
    assert "ORDER_LIFECYCLE_FAILURE" in markdown
    assert "REPAIR_ORDER_LIFECYCLE" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_simulated_market_session(_ready_input().__dict__)

    assert result.state is SimulatedMarketSessionState.READY_FOR_FULL_PAPER_SESSION
    assert result.market_session_score >= 94


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            SimulatedMarketSessionRisk.MARKET_DATA_MISSING,
            SimulatedMarketSessionRecommendation.RESTORE_MARKET_DATA_FLOW,
        ),
        (
            SimulatedMarketSessionRisk.SESSION_STATE_DRIFT,
            SimulatedMarketSessionRecommendation.RECONCILE_SESSION_STATE,
        ),
        (
            SimulatedMarketSessionRisk.PNL_CALCULATION_FAILURE,
            SimulatedMarketSessionRecommendation.REPAIR_PNL_CALCULATION,
        ),
    ],
)
def test_recommendation_mapping_for_market_session_risks(risk, recommendation):
    recommendations = generate_market_session_recommendations((risk,), SimulatedMarketSessionState.PARTIALLY_READY)

    assert recommendation in recommendations


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "simulated_market_session.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
