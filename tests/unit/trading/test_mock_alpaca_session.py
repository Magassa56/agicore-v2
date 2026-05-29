import ast
from pathlib import Path

import pytest

from agicore.trading.mock_alpaca_session import (
    compute_mock_alpaca_session_score,
    detect_mock_alpaca_session_risks,
    evaluate_mock_alpaca_session,
    generate_mock_alpaca_session_recommendations,
    render_mock_alpaca_session_markdown,
    simulate_mock_account_fetch,
    simulate_mock_journal_update,
    simulate_mock_observability_events,
    simulate_mock_order_status,
    simulate_mock_order_submit,
    simulate_mock_positions_fetch,
    simulate_mock_session_connect,
    simulate_mock_session_disconnect,
)
from agicore.trading.mock_alpaca_session_models import (
    MockAlpacaSessionInput,
    MockAlpacaSessionRecommendation,
    MockAlpacaSessionRisk,
    MockAlpacaSessionState,
)


def _upstream(state="READY", score=96, risks=(), blockers=(), **extra):
    payload = {
        "state": state,
        "score": score,
        "risks": tuple(risks),
        "blockers": tuple(blockers),
        "offline_only": True,
        "score_breakdown": {
            "mock_connectivity_score": score,
            "connectivity_score": score,
            "sandbox_score": score,
            "alpaca_adapter_score": score,
            "adapter_score": score,
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
        "mock_connectivity_layer": _upstream("READY_FOR_MOCK_ALPACA_SESSION"),
        "alpaca_paper_connectivity_readiness": _upstream("READY_FOR_MOCK_CONNECTIVITY"),
        "broker_paper_sandbox": _upstream("READY_FOR_ALPACA_PAPER_CONNECTIVITY"),
        "alpaca_paper_adapter": _upstream("READY_FOR_END_TO_END_PAPER"),
        "paper_broker_adapter": _upstream("READY_FOR_ALPACA_PAPER_ADAPTER"),
        "paper_trading_end_to_end": _upstream("READY_FOR_PAPER_DRY_RUN"),
        "paper_dry_run": _upstream("READY_FOR_SUPERVISED_PAPER_TRIAL"),
        "supervised_paper_trial": _upstream("READY_FOR_BROKER_PAPER_SANDBOX"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "mock_session_transport_ready": True,
        "mock_session_connect_successful": True,
        "mock_session_handshake_valid": True,
        "mock_session_idempotent": True,
        "mock_account_fetch_simulated": True,
        "mock_account_schema_valid": True,
        "mock_account_balances_consistent": True,
        "mock_account_fetch_traceable": True,
        "mock_positions_fetch_simulated": True,
        "mock_positions_schema_valid": True,
        "mock_positions_reconciled": True,
        "mock_positions_fetch_traceable": True,
        "mock_order_submit_simulated": True,
        "mock_order_payload_valid": True,
        "mock_order_safety_checked": True,
        "mock_order_not_routed": True,
        "mock_order_status_simulated": True,
        "mock_order_status_schema_valid": True,
        "mock_order_status_reconciled": True,
        "mock_order_status_traceable": True,
        "mock_journal_update_simulated": True,
        "mock_journal_entry_complete": True,
        "mock_journal_traceable": True,
        "mock_journal_replayable": True,
        "mock_observability_events_simulated": True,
        "mock_metrics_recorded": True,
        "mock_traces_recorded": True,
        "mock_alerts_recorded": True,
        "mock_session_disconnect_simulated": True,
        "mock_session_disconnect_detected": True,
        "mock_session_shutdown_safe": True,
        "mock_session_reconnect_blocked": True,
        "mock_state_snapshot_consistent": True,
        "mock_state_replay_consistent": True,
        "mock_state_recovery_verified": True,
        "mock_state_isolated": True,
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
        "session_completed": True,
        "ready_for_simulated_market_session": True,
        "mock_session_connect_score": 96,
        "mock_account_fetch_score": 96,
        "mock_positions_fetch_score": 96,
        "mock_order_submit_score": 96,
        "mock_order_status_score": 96,
        "mock_journal_update_score": 96,
        "mock_observability_events_score": 96,
        "mock_session_disconnect_score": 96,
    }
    payload.update(overrides)
    return MockAlpacaSessionInput(**payload)


def test_evaluate_ready_for_simulated_market_session():
    result = evaluate_mock_alpaca_session(_ready_input())

    assert result.state is MockAlpacaSessionState.READY_FOR_SIMULATED_MARKET_SESSION
    assert result.risks == ()
    assert result.offline_only is True
    assert result.mock_alpaca_session_score >= 94
    assert result.mock_session_graph.blocked_edges == ()


def test_mock_session_completed_when_market_gate_is_not_set():
    result = evaluate_mock_alpaca_session(_ready_input(ready_for_simulated_market_session=False))

    assert result.state is MockAlpacaSessionState.MOCK_SESSION_COMPLETED
    assert result.risks == ()


def test_mock_session_ready_when_not_completed_yet():
    result = evaluate_mock_alpaca_session(_ready_input(session_completed=False))

    assert result.state is MockAlpacaSessionState.MOCK_SESSION_READY
    assert result.risks == ()


def test_detects_every_mock_alpaca_session_risk_when_all_simulations_fail():
    failing_fields = {
        name: False
        for name in MockAlpacaSessionInput.__dataclass_fields__
        if name.startswith(("mock_", "no_", "offline_", "safety_", "kill_", "rollback_", "session_", "ready_"))
        and not name.endswith("_score")
        and name != "mock_connectivity_layer"
    }
    score_fields = {
        name: 10
        for name in MockAlpacaSessionInput.__dataclass_fields__
        if name.endswith("_score")
    }

    result = evaluate_mock_alpaca_session(_ready_input(**failing_fields, **score_fields))

    assert set(result.risks) == set(MockAlpacaSessionRisk)
    assert result.state is MockAlpacaSessionState.NOT_READY
    assert result.offline_only is False


def test_mock_session_connect_detects_connect_failure_and_state_drift():
    simulation = simulate_mock_session_connect(
        _ready_input(mock_session_connect_successful=False, mock_session_idempotent=False)
    )

    assert simulation.passed is False
    assert MockAlpacaSessionRisk.MOCK_SESSION_CONNECT_FAILURE in simulation.risks
    assert MockAlpacaSessionRisk.MOCK_SESSION_STATE_DRIFT in simulation.risks


def test_mock_account_fetch_detects_fetch_failure_observability_and_drift():
    simulation = simulate_mock_account_fetch(
        _ready_input(
            mock_account_schema_valid=False,
            mock_account_balances_consistent=False,
            mock_account_fetch_traceable=False,
        )
    )

    assert simulation.passed is False
    assert MockAlpacaSessionRisk.MOCK_ACCOUNT_FETCH_FAILURE in simulation.risks
    assert MockAlpacaSessionRisk.MOCK_OBSERVABILITY_EVENT_MISSING in simulation.risks
    assert MockAlpacaSessionRisk.MOCK_SESSION_STATE_DRIFT in simulation.risks


def test_mock_positions_fetch_detects_fetch_failure_observability_and_drift():
    simulation = simulate_mock_positions_fetch(
        _ready_input(
            mock_positions_schema_valid=False,
            mock_positions_reconciled=False,
            mock_positions_fetch_traceable=False,
        )
    )

    assert simulation.passed is False
    assert MockAlpacaSessionRisk.MOCK_POSITIONS_FETCH_FAILURE in simulation.risks
    assert MockAlpacaSessionRisk.MOCK_OBSERVABILITY_EVENT_MISSING in simulation.risks
    assert MockAlpacaSessionRisk.MOCK_SESSION_STATE_DRIFT in simulation.risks


def test_mock_order_submit_detects_submit_failure_and_safety_bypass():
    simulation = simulate_mock_order_submit(
        _ready_input(mock_order_payload_valid=False, mock_order_not_routed=False)
    )

    assert simulation.passed is False
    assert MockAlpacaSessionRisk.MOCK_ORDER_SUBMIT_FAILURE in simulation.risks
    assert MockAlpacaSessionRisk.SAFETY_BOUNDARY_BYPASS in simulation.risks


def test_mock_order_status_detects_status_failure_observability_and_drift():
    simulation = simulate_mock_order_status(
        _ready_input(
            mock_order_status_schema_valid=False,
            mock_order_status_reconciled=False,
            mock_order_status_traceable=False,
        )
    )

    assert simulation.passed is False
    assert MockAlpacaSessionRisk.MOCK_ORDER_STATUS_FAILURE in simulation.risks
    assert MockAlpacaSessionRisk.MOCK_OBSERVABILITY_EVENT_MISSING in simulation.risks
    assert MockAlpacaSessionRisk.MOCK_SESSION_STATE_DRIFT in simulation.risks


def test_mock_journal_update_detects_journal_failure_observability_and_drift():
    simulation = simulate_mock_journal_update(
        _ready_input(
            mock_journal_entry_complete=False,
            mock_journal_traceable=False,
            mock_journal_replayable=False,
        )
    )

    assert simulation.passed is False
    assert MockAlpacaSessionRisk.MOCK_JOURNAL_UPDATE_FAILURE in simulation.risks
    assert MockAlpacaSessionRisk.MOCK_OBSERVABILITY_EVENT_MISSING in simulation.risks
    assert MockAlpacaSessionRisk.MOCK_SESSION_STATE_DRIFT in simulation.risks


def test_mock_observability_events_detect_missing_events():
    simulation = simulate_mock_observability_events(_ready_input(mock_metrics_recorded=False))

    assert simulation.passed is False
    assert simulation.risks == (MockAlpacaSessionRisk.MOCK_OBSERVABILITY_EVENT_MISSING,)


def test_mock_session_disconnect_detects_disconnect_failure_and_safety_bypass():
    simulation = simulate_mock_session_disconnect(
        _ready_input(mock_session_disconnect_detected=False, mock_session_reconnect_blocked=False)
    )

    assert simulation.passed is False
    assert MockAlpacaSessionRisk.MOCK_SESSION_DISCONNECT_FAILURE in simulation.risks
    assert MockAlpacaSessionRisk.SAFETY_BOUNDARY_BYPASS in simulation.risks


def test_three_soft_risks_require_review():
    result = evaluate_mock_alpaca_session(
        _ready_input(
            mock_account_schema_valid=False,
            mock_positions_schema_valid=False,
            mock_journal_entry_complete=False,
            mock_account_balances_consistent=True,
            mock_positions_reconciled=True,
            mock_journal_replayable=True,
        )
    )

    assert result.state is MockAlpacaSessionState.REVIEW_REQUIRED
    assert MockAlpacaSessionRisk.MOCK_ACCOUNT_FETCH_FAILURE in result.risks
    assert MockAlpacaSessionRisk.MOCK_POSITIONS_FETCH_FAILURE in result.risks
    assert MockAlpacaSessionRisk.MOCK_JOURNAL_UPDATE_FAILURE in result.risks


def test_single_soft_risk_is_partially_ready():
    result = evaluate_mock_alpaca_session(
        _ready_input(mock_account_schema_valid=False, mock_account_fetch_score=86)
    )

    assert result.state is MockAlpacaSessionState.PARTIALLY_READY
    assert result.risks == (MockAlpacaSessionRisk.MOCK_ACCOUNT_FETCH_FAILURE,)


def test_hard_risk_caps_score_and_not_ready():
    data = _ready_input(no_http_transport=False)
    risks = detect_mock_alpaca_session_risks(data)
    score = compute_mock_alpaca_session_score(data, risks)
    result = evaluate_mock_alpaca_session(data)

    assert MockAlpacaSessionRisk.SAFETY_BOUNDARY_BYPASS in risks
    assert score.overall_score <= 40
    assert result.state is MockAlpacaSessionState.NOT_READY


def test_upstream_network_leak_keeps_mock_session_offline_boundary_closed():
    upstream = _upstream(risks=("NETWORK_LEAK",))
    result = evaluate_mock_alpaca_session(_ready_input(mock_connectivity_layer=upstream))

    assert result.state is MockAlpacaSessionState.NOT_READY
    assert result.offline_only is False
    assert MockAlpacaSessionRisk.SAFETY_BOUNDARY_BYPASS in result.risks


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_mock_alpaca_session_recommendations(
        (
            MockAlpacaSessionRisk.MOCK_ORDER_SUBMIT_FAILURE,
            MockAlpacaSessionRisk.MOCK_ORDER_SUBMIT_FAILURE,
            MockAlpacaSessionRisk.MOCK_OBSERVABILITY_EVENT_MISSING,
            MockAlpacaSessionRisk.SAFETY_BOUNDARY_BYPASS,
        ),
        MockAlpacaSessionState.PARTIALLY_READY,
    )

    assert recommendations.count(MockAlpacaSessionRecommendation.REPAIR_MOCK_ORDER_SUBMIT) == 1
    assert MockAlpacaSessionRecommendation.RESTORE_MOCK_OBSERVABILITY_EVENTS in recommendations
    assert MockAlpacaSessionRecommendation.ENFORCE_MOCK_SESSION_SAFETY_BOUNDARY in recommendations
    assert MockAlpacaSessionRecommendation.RUN_MOCK_ALPACA_SESSION_SUITE in recommendations


def test_ready_state_adds_simulated_market_session_approval_recommendation():
    result = evaluate_mock_alpaca_session(_ready_input())

    assert (
        MockAlpacaSessionRecommendation.APPROVE_SIMULATED_MARKET_SESSION_AFTER_MANUAL_REVIEW
        in result.recommendations
    )


def test_markdown_rendering_contains_simulations_graph_risks_and_recommendations():
    result = evaluate_mock_alpaca_session(_ready_input(mock_order_payload_valid=False))
    markdown = render_mock_alpaca_session_markdown(result)

    assert "# AGIcore Mock Alpaca Session" in markdown
    assert "# Score Breakdown" in markdown
    assert "# Mock Alpaca Session Simulations" in markdown
    assert "# Mock Alpaca Session Graph" in markdown
    assert "MOCK_ORDER_SUBMIT_FAILURE" in markdown
    assert "REPAIR_MOCK_ORDER_SUBMIT" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_mock_alpaca_session(_ready_input().__dict__)

    assert result.state is MockAlpacaSessionState.READY_FOR_SIMULATED_MARKET_SESSION
    assert result.mock_alpaca_session_score >= 94


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            MockAlpacaSessionRisk.MOCK_ACCOUNT_FETCH_FAILURE,
            MockAlpacaSessionRecommendation.REPAIR_MOCK_ACCOUNT_FETCH,
        ),
        (
            MockAlpacaSessionRisk.MOCK_SESSION_STATE_DRIFT,
            MockAlpacaSessionRecommendation.RECONCILE_MOCK_SESSION_STATE,
        ),
        (
            MockAlpacaSessionRisk.MOCK_SESSION_DISCONNECT_FAILURE,
            MockAlpacaSessionRecommendation.REPAIR_MOCK_SESSION_DISCONNECT,
        ),
    ],
)
def test_recommendation_mapping_for_session_risks(risk, recommendation):
    recommendations = generate_mock_alpaca_session_recommendations((risk,), MockAlpacaSessionState.PARTIALLY_READY)

    assert recommendation in recommendations


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "mock_alpaca_session.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
