import ast
from pathlib import Path

import pytest

from agicore.trading.mock_connectivity_layer import (
    compute_mock_connectivity_score,
    detect_mock_connectivity_risks,
    evaluate_mock_connectivity_layer,
    generate_mock_connectivity_recommendations,
    render_mock_connectivity_markdown,
    simulate_mock_broker_response,
    simulate_mock_connection,
    simulate_mock_disconnect,
    simulate_mock_order_rejection,
    simulate_mock_rate_limit,
    simulate_mock_retry,
    simulate_mock_timeout,
    verify_mock_session_integrity,
)
from agicore.trading.mock_connectivity_layer_models import (
    MockConnectivityInput,
    MockConnectivityRecommendation,
    MockConnectivityRisk,
    MockConnectivityState,
)


def _upstream(state="READY", score=96, risks=(), blockers=(), **extra):
    payload = {
        "state": state,
        "score": score,
        "risks": tuple(risks),
        "blockers": tuple(blockers),
        "offline_only": True,
        "score_breakdown": {
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
        "mock_transport_defined": True,
        "mock_connect_successful": True,
        "mock_handshake_valid": True,
        "mock_connection_idempotent": True,
        "disconnect_event_simulated": True,
        "disconnect_detected": True,
        "disconnect_state_safe": True,
        "reconnect_blocked_until_supervised": True,
        "timeout_event_simulated": True,
        "timeout_detected": True,
        "timeout_fail_closed": True,
        "timeout_observed": True,
        "retry_event_simulated": True,
        "retry_policy_applied": True,
        "retry_backoff_respected": True,
        "retry_stop_condition_respected": True,
        "rate_limit_event_simulated": True,
        "rate_limit_detected": True,
        "throttle_applied": True,
        "rate_limit_metric_recorded": True,
        "mock_response_generated": True,
        "mock_response_schema_valid": True,
        "mock_response_traceable": True,
        "mock_response_deterministic": True,
        "mock_order_rejection_simulated": True,
        "mock_order_rejection_handled": True,
        "rejection_reason_recorded": True,
        "no_order_routed": True,
        "session_state_isolated": True,
        "session_checkpointed": True,
        "session_recovery_verified": True,
        "session_integrity_locked": True,
        "observability_events_emitted": True,
        "metrics_recorded": True,
        "traces_recorded": True,
        "critical_alerts_recorded": True,
        "safety_gate_enforced": True,
        "kill_switch_linked": True,
        "rollback_linked": True,
        "offline_mode_enforced": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_sdk_import": True,
        "mock_layer_validated": True,
        "ready_for_mock_alpaca_session": True,
        "mock_connection_score": 96,
        "mock_disconnect_score": 96,
        "mock_timeout_score": 96,
        "mock_retry_score": 96,
        "mock_rate_limit_score": 96,
        "mock_broker_response_score": 96,
        "mock_order_rejection_score": 96,
        "mock_session_integrity_score": 96,
    }
    payload.update(overrides)
    return MockConnectivityInput(**payload)


def test_evaluate_ready_for_mock_alpaca_session():
    result = evaluate_mock_connectivity_layer(_ready_input())

    assert result.state is MockConnectivityState.READY_FOR_MOCK_ALPACA_SESSION
    assert result.risks == ()
    assert result.offline_only is True
    assert result.mock_connectivity_score >= 94
    assert result.mock_connectivity_graph.blocked_edges == ()


def test_mock_connectivity_validated_when_session_gate_is_not_set():
    result = evaluate_mock_connectivity_layer(_ready_input(ready_for_mock_alpaca_session=False))

    assert result.state is MockConnectivityState.MOCK_CONNECTIVITY_VALIDATED
    assert result.risks == ()


def test_mock_connectivity_ready_when_not_validated_yet():
    result = evaluate_mock_connectivity_layer(_ready_input(mock_layer_validated=False))

    assert result.state is MockConnectivityState.MOCK_CONNECTIVITY_READY
    assert result.risks == ()


def test_detects_every_mock_connectivity_risk_when_all_simulations_fail():
    failing_fields = {
        name: False
        for name in MockConnectivityInput.__dataclass_fields__
        if name.endswith(
            (
                "_defined",
                "_successful",
                "_valid",
                "_idempotent",
                "_simulated",
                "_detected",
                "_safe",
                "_supervised",
                "_closed",
                "_observed",
                "_applied",
                "_respected",
                "_recorded",
                "_generated",
                "_traceable",
                "_deterministic",
                "_handled",
                "_routed",
                "_isolated",
                "_checkpointed",
                "_verified",
                "_locked",
                "_emitted",
                "_enforced",
                "_linked",
                "_transport",
                "_import",
                "_validated",
                "_session",
            )
        )
    }
    score_fields = {
        name: 10
        for name in MockConnectivityInput.__dataclass_fields__
        if name.endswith("_score")
    }

    result = evaluate_mock_connectivity_layer(_ready_input(**failing_fields, **score_fields))

    assert set(result.risks) == set(MockConnectivityRisk)
    assert result.state is MockConnectivityState.NOT_READY
    assert result.offline_only is False


def test_mock_connection_detects_failure_and_session_corruption():
    simulation = simulate_mock_connection(
        _ready_input(mock_connect_successful=False, mock_connection_idempotent=False)
    )

    assert simulation.passed is False
    assert MockConnectivityRisk.MOCK_CONNECTION_FAILURE in simulation.risks
    assert MockConnectivityRisk.MOCK_SESSION_CORRUPTION in simulation.risks


def test_mock_disconnect_detects_unhandled_disconnect_and_safety_bypass():
    simulation = simulate_mock_disconnect(
        _ready_input(disconnect_detected=False, reconnect_blocked_until_supervised=False)
    )

    assert simulation.passed is False
    assert MockConnectivityRisk.MOCK_DISCONNECT_UNHANDLED in simulation.risks
    assert MockConnectivityRisk.SAFETY_BOUNDARY_BYPASS in simulation.risks


def test_mock_timeout_detects_unhandled_timeout_and_safety_bypass():
    simulation = simulate_mock_timeout(_ready_input(timeout_detected=False, timeout_fail_closed=False))

    assert simulation.passed is False
    assert MockConnectivityRisk.MOCK_TIMEOUT_UNHANDLED in simulation.risks
    assert MockConnectivityRisk.SAFETY_BOUNDARY_BYPASS in simulation.risks


def test_mock_retry_detects_policy_failure():
    simulation = simulate_mock_retry(_ready_input(retry_policy_applied=False))

    assert simulation.passed is False
    assert MockConnectivityRisk.MOCK_RETRY_POLICY_FAILURE in simulation.risks


def test_mock_rate_limit_detects_unhandled_limit_and_observability_gap():
    simulation = simulate_mock_rate_limit(
        _ready_input(rate_limit_detected=False, rate_limit_metric_recorded=False)
    )

    assert simulation.passed is False
    assert MockConnectivityRisk.MOCK_RATE_LIMIT_UNHANDLED in simulation.risks
    assert MockConnectivityRisk.OBSERVABILITY_GAP in simulation.risks


def test_mock_broker_response_detects_invalid_response_and_corruption():
    simulation = simulate_mock_broker_response(
        _ready_input(mock_response_schema_valid=False, mock_response_deterministic=False)
    )

    assert simulation.passed is False
    assert MockConnectivityRisk.MOCK_RESPONSE_INVALID in simulation.risks
    assert MockConnectivityRisk.MOCK_SESSION_CORRUPTION in simulation.risks


def test_mock_order_rejection_detects_unhandled_rejection_and_safety_bypass():
    simulation = simulate_mock_order_rejection(
        _ready_input(mock_order_rejection_handled=False, no_order_routed=False)
    )

    assert simulation.passed is False
    assert MockConnectivityRisk.MOCK_ORDER_REJECTION_UNHANDLED in simulation.risks
    assert MockConnectivityRisk.SAFETY_BOUNDARY_BYPASS in simulation.risks


def test_mock_session_integrity_detects_corruption_observability_and_safety_gaps():
    simulation = verify_mock_session_integrity(
        _ready_input(
            session_state_isolated=False,
            observability_events_emitted=False,
            safety_gate_enforced=False,
        )
    )

    assert simulation.passed is False
    assert MockConnectivityRisk.MOCK_SESSION_CORRUPTION in simulation.risks
    assert MockConnectivityRisk.OBSERVABILITY_GAP in simulation.risks
    assert MockConnectivityRisk.SAFETY_BOUNDARY_BYPASS in simulation.risks


def test_three_soft_risks_require_review():
    result = evaluate_mock_connectivity_layer(
        _ready_input(
            retry_policy_applied=False,
            rate_limit_detected=False,
            rate_limit_metric_recorded=False,
        )
    )

    assert result.state is MockConnectivityState.REVIEW_REQUIRED
    assert MockConnectivityRisk.MOCK_RETRY_POLICY_FAILURE in result.risks
    assert MockConnectivityRisk.MOCK_RATE_LIMIT_UNHANDLED in result.risks
    assert MockConnectivityRisk.OBSERVABILITY_GAP in result.risks


def test_single_soft_risk_is_partially_ready():
    result = evaluate_mock_connectivity_layer(_ready_input(retry_policy_applied=False))

    assert result.state is MockConnectivityState.PARTIALLY_READY
    assert result.risks == (MockConnectivityRisk.MOCK_RETRY_POLICY_FAILURE,)


def test_hard_risk_caps_score_and_not_ready():
    data = _ready_input(no_http_transport=False)
    risks = detect_mock_connectivity_risks(data)
    score = compute_mock_connectivity_score(data, risks)
    result = evaluate_mock_connectivity_layer(data)

    assert MockConnectivityRisk.SAFETY_BOUNDARY_BYPASS in risks
    assert score.overall_score <= 40
    assert result.state is MockConnectivityState.NOT_READY


def test_upstream_external_dependency_keeps_mock_layer_offline_boundary_closed():
    upstream = _upstream(risks=("NETWORK_LEAK",))
    result = evaluate_mock_connectivity_layer(_ready_input(alpaca_paper_connectivity_readiness=upstream))

    assert result.state is MockConnectivityState.NOT_READY
    assert result.offline_only is False
    assert MockConnectivityRisk.SAFETY_BOUNDARY_BYPASS in result.risks


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_mock_connectivity_recommendations(
        (
            MockConnectivityRisk.MOCK_CONNECTION_FAILURE,
            MockConnectivityRisk.MOCK_CONNECTION_FAILURE,
            MockConnectivityRisk.OBSERVABILITY_GAP,
            MockConnectivityRisk.SAFETY_BOUNDARY_BYPASS,
        ),
        MockConnectivityState.PARTIALLY_READY,
    )

    assert recommendations.count(MockConnectivityRecommendation.REPAIR_MOCK_CONNECTION) == 1
    assert MockConnectivityRecommendation.RESTORE_MOCK_OBSERVABILITY in recommendations
    assert MockConnectivityRecommendation.ENFORCE_MOCK_SAFETY_BOUNDARY in recommendations
    assert MockConnectivityRecommendation.RUN_MOCK_CONNECTIVITY_SUITE in recommendations


def test_ready_state_adds_mock_alpaca_session_approval_recommendation():
    result = evaluate_mock_connectivity_layer(_ready_input())

    assert (
        MockConnectivityRecommendation.APPROVE_MOCK_ALPACA_SESSION_AFTER_MANUAL_REVIEW
        in result.recommendations
    )


def test_markdown_rendering_contains_simulations_graph_risks_and_recommendations():
    result = evaluate_mock_connectivity_layer(_ready_input(mock_connect_successful=False))
    markdown = render_mock_connectivity_markdown(result)

    assert "# AGIcore Mock Connectivity Layer" in markdown
    assert "# Score Breakdown" in markdown
    assert "# Mock Simulations" in markdown
    assert "# Mock Connectivity Graph" in markdown
    assert "MOCK_CONNECTION_FAILURE" in markdown
    assert "REPAIR_MOCK_CONNECTION" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_mock_connectivity_layer(_ready_input().__dict__)

    assert result.state is MockConnectivityState.READY_FOR_MOCK_ALPACA_SESSION
    assert result.mock_connectivity_score >= 94


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            MockConnectivityRisk.MOCK_ORDER_REJECTION_UNHANDLED,
            MockConnectivityRecommendation.HANDLE_MOCK_ORDER_REJECTION,
        ),
        (
            MockConnectivityRisk.MOCK_SESSION_CORRUPTION,
            MockConnectivityRecommendation.REPAIR_MOCK_SESSION_INTEGRITY,
        ),
    ],
)
def test_recommendation_mapping_for_mock_rejection_and_session_risks(risk, recommendation):
    recommendations = generate_mock_connectivity_recommendations((risk,), MockConnectivityState.PARTIALLY_READY)

    assert recommendation in recommendations


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "mock_connectivity_layer.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
