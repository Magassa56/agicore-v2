import ast
from pathlib import Path

import pytest

from agicore.trading.alpaca_paper_connectivity_readiness import (
    compute_connectivity_score,
    detect_connectivity_risks,
    evaluate_alpaca_paper_connectivity_readiness,
    generate_connectivity_recommendations,
    render_connectivity_markdown,
    verify_credentials_requirements,
    verify_disconnect_recovery,
    verify_endpoint_requirements,
    verify_kill_switch_compatibility,
    verify_observability_requirements,
    verify_rate_limit_requirements,
    verify_retry_requirements,
    verify_rollback_compatibility,
    verify_session_integrity,
    verify_timeout_requirements,
)
from agicore.trading.alpaca_paper_connectivity_readiness_models import (
    AlpacaPaperConnectivityInput,
    AlpacaPaperConnectivityRecommendation,
    AlpacaPaperConnectivityRisk,
    AlpacaPaperConnectivityState,
)


def _upstream(state="READY", score=96, risks=(), blockers=(), **extra):
    payload = {
        "state": state,
        "score": score,
        "risks": tuple(risks),
        "blockers": tuple(blockers),
        "offline_only": True,
        "score_breakdown": {
            "sandbox_score": score,
            "alpaca_adapter_score": score,
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
        "broker_paper_sandbox": _upstream("READY_FOR_ALPACA_PAPER_CONNECTIVITY"),
        "alpaca_paper_adapter": _upstream("READY_FOR_END_TO_END_PAPER"),
        "paper_trading_end_to_end": _upstream("READY_FOR_PAPER_DRY_RUN"),
        "paper_dry_run": _upstream("READY_FOR_SUPERVISED_PAPER_TRIAL"),
        "supervised_paper_trial": _upstream("READY_FOR_BROKER_PAPER_SANDBOX"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "credential_schema_defined": True,
        "credential_storage_externalized": True,
        "no_real_credentials_loaded": True,
        "paper_account_scope_defined": True,
        "paper_endpoint_config_defined": True,
        "endpoint_environment_locked": True,
        "endpoint_allowlist_defined": True,
        "live_endpoint_blocked": True,
        "rate_limit_budget_defined": True,
        "request_throttle_defined": True,
        "burst_guard_defined": True,
        "rate_limit_observability_defined": True,
        "retry_policy_defined": True,
        "retry_backoff_defined": True,
        "retry_idempotency_defined": True,
        "retry_stop_condition_defined": True,
        "timeout_policy_defined": True,
        "connect_timeout_defined": True,
        "read_timeout_defined": True,
        "timeout_fail_closed": True,
        "disconnect_detection_defined": True,
        "reconnect_policy_defined": True,
        "session_recovery_checkpointed": True,
        "stale_session_guard_defined": True,
        "session_state_isolated": True,
        "session_idempotency_defined": True,
        "session_audit_defined": True,
        "session_integrity_locked": True,
        "observability_events_defined": True,
        "metrics_defined": True,
        "traces_defined": True,
        "critical_alerts_defined": True,
        "kill_switch_linked": True,
        "kill_switch_fail_closed": True,
        "emergency_disconnect_defined": True,
        "operator_halt_required": True,
        "rollback_linked": True,
        "recovery_point_required": True,
        "rollback_after_disconnect_defined": True,
        "restart_guard_defined": True,
        "offline_mode_enforced": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_sdk_import": True,
        "configuration_locked": True,
        "connectivity_validated": True,
        "ready_for_mock_connectivity": True,
        "credentials_score": 96,
        "endpoint_score": 96,
        "rate_limit_score": 96,
        "retry_score": 96,
        "timeout_score": 96,
        "disconnect_recovery_score": 96,
        "session_integrity_score": 96,
        "observability_score": 96,
        "kill_switch_compatibility_score": 96,
        "rollback_compatibility_score": 96,
    }
    payload.update(overrides)
    return AlpacaPaperConnectivityInput(**payload)


def test_evaluate_ready_for_mock_connectivity():
    result = evaluate_alpaca_paper_connectivity_readiness(_ready_input())

    assert result.state is AlpacaPaperConnectivityState.READY_FOR_MOCK_CONNECTIVITY
    assert result.risks == ()
    assert result.offline_only is True
    assert result.connectivity_score >= 94
    assert result.connectivity_graph.blocked_edges == ()


def test_connectivity_validated_when_mock_gate_is_not_set():
    result = evaluate_alpaca_paper_connectivity_readiness(_ready_input(ready_for_mock_connectivity=False))

    assert result.state is AlpacaPaperConnectivityState.CONNECTIVITY_VALIDATED
    assert result.risks == ()


def test_connectivity_ready_when_not_validated_yet():
    result = evaluate_alpaca_paper_connectivity_readiness(_ready_input(connectivity_validated=False))

    assert result.state is AlpacaPaperConnectivityState.CONNECTIVITY_READY
    assert result.risks == ()


def test_detects_every_connectivity_risk_when_all_requirements_fail():
    failing_fields = {
        name: False
        for name in AlpacaPaperConnectivityInput.__dataclass_fields__
        if name.endswith(
            (
                "_defined",
                "_externalized",
                "_loaded",
                "_locked",
                "_blocked",
                "_closed",
                "_checkpointed",
                "_isolated",
                "_linked",
                "_required",
                "_enforced",
                "_transport",
                "_import",
                "_validated",
                "_connectivity",
            )
        )
    }
    score_fields = {
        name: 10
        for name in AlpacaPaperConnectivityInput.__dataclass_fields__
        if name.endswith("_score")
    }

    result = evaluate_alpaca_paper_connectivity_readiness(_ready_input(**failing_fields, **score_fields))

    assert set(result.risks) == set(AlpacaPaperConnectivityRisk)
    assert result.state is AlpacaPaperConnectivityState.NOT_READY
    assert result.offline_only is False


def test_credentials_requirements_detect_missing_credentials_and_unsafe_config():
    review = verify_credentials_requirements(
        _ready_input(credential_schema_defined=False, no_real_credentials_loaded=False)
    )

    assert review.passed is False
    assert AlpacaPaperConnectivityRisk.MISSING_CREDENTIALS in review.risks
    assert AlpacaPaperConnectivityRisk.UNSAFE_CONNECTIVITY_CONFIGURATION in review.risks


def test_endpoint_requirements_detect_invalid_endpoint_and_unsafe_config():
    review = verify_endpoint_requirements(
        _ready_input(paper_endpoint_config_defined=False, live_endpoint_blocked=False)
    )

    assert review.passed is False
    assert AlpacaPaperConnectivityRisk.INVALID_ENDPOINT_CONFIGURATION in review.risks
    assert AlpacaPaperConnectivityRisk.UNSAFE_CONNECTIVITY_CONFIGURATION in review.risks


def test_rate_limit_requirements_detect_exposure():
    review = verify_rate_limit_requirements(_ready_input(rate_limit_budget_defined=False))

    assert review.passed is False
    assert AlpacaPaperConnectivityRisk.RATE_LIMIT_EXPOSURE in review.risks


def test_retry_requirements_detect_missing_policy():
    review = verify_retry_requirements(_ready_input(retry_policy_defined=False))

    assert review.passed is False
    assert AlpacaPaperConnectivityRisk.RETRY_POLICY_MISSING in review.risks


def test_timeout_requirements_detect_exposure_and_unsafe_config():
    review = verify_timeout_requirements(
        _ready_input(timeout_policy_defined=False, timeout_fail_closed=False)
    )

    assert review.passed is False
    assert AlpacaPaperConnectivityRisk.TIMEOUT_EXPOSURE in review.risks
    assert AlpacaPaperConnectivityRisk.UNSAFE_CONNECTIVITY_CONFIGURATION in review.risks


def test_disconnect_recovery_detects_failure():
    review = verify_disconnect_recovery(_ready_input(disconnect_detection_defined=False))

    assert review.passed is False
    assert AlpacaPaperConnectivityRisk.SESSION_RECOVERY_FAILURE in review.risks


def test_session_integrity_detects_recovery_failure_and_unsafe_config():
    review = verify_session_integrity(
        _ready_input(session_state_isolated=False, session_integrity_locked=False)
    )

    assert review.passed is False
    assert AlpacaPaperConnectivityRisk.SESSION_RECOVERY_FAILURE in review.risks
    assert AlpacaPaperConnectivityRisk.UNSAFE_CONNECTIVITY_CONFIGURATION in review.risks


def test_observability_requirements_detect_gap():
    review = verify_observability_requirements(_ready_input(observability_events_defined=False))

    assert review.passed is False
    assert AlpacaPaperConnectivityRisk.OBSERVABILITY_GAP in review.risks


def test_kill_switch_compatibility_detects_incompatibility():
    review = verify_kill_switch_compatibility(_ready_input(kill_switch_linked=False))

    assert review.passed is False
    assert AlpacaPaperConnectivityRisk.KILL_SWITCH_INCOMPATIBILITY in review.risks


def test_rollback_compatibility_detects_incompatibility():
    review = verify_rollback_compatibility(_ready_input(rollback_linked=False))

    assert review.passed is False
    assert AlpacaPaperConnectivityRisk.ROLLBACK_INCOMPATIBILITY in review.risks


def test_three_soft_risks_require_review():
    result = evaluate_alpaca_paper_connectivity_readiness(
        _ready_input(rate_limit_budget_defined=False, retry_policy_defined=False, rollback_linked=False)
    )

    assert result.state is AlpacaPaperConnectivityState.REVIEW_REQUIRED
    assert AlpacaPaperConnectivityRisk.RATE_LIMIT_EXPOSURE in result.risks
    assert AlpacaPaperConnectivityRisk.RETRY_POLICY_MISSING in result.risks
    assert AlpacaPaperConnectivityRisk.ROLLBACK_INCOMPATIBILITY in result.risks


def test_single_soft_risk_is_partially_ready():
    result = evaluate_alpaca_paper_connectivity_readiness(_ready_input(rate_limit_budget_defined=False))

    assert result.state is AlpacaPaperConnectivityState.PARTIALLY_READY
    assert result.risks == (AlpacaPaperConnectivityRisk.RATE_LIMIT_EXPOSURE,)


def test_hard_risk_caps_score_and_not_ready():
    data = _ready_input(no_http_transport=False)
    risks = detect_connectivity_risks(data)
    score = compute_connectivity_score(data, risks)
    result = evaluate_alpaca_paper_connectivity_readiness(data)

    assert AlpacaPaperConnectivityRisk.UNSAFE_CONNECTIVITY_CONFIGURATION in risks
    assert score.overall_score <= 40
    assert result.state is AlpacaPaperConnectivityState.NOT_READY


def test_upstream_external_dependency_keeps_connectivity_offline_boundary_closed():
    upstream = _upstream(risks=("EXTERNAL_DEPENDENCY_RISK",))
    result = evaluate_alpaca_paper_connectivity_readiness(_ready_input(broker_paper_sandbox=upstream))

    assert result.state is AlpacaPaperConnectivityState.NOT_READY
    assert result.offline_only is False
    assert AlpacaPaperConnectivityRisk.UNSAFE_CONNECTIVITY_CONFIGURATION in result.risks


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_connectivity_recommendations(
        (
            AlpacaPaperConnectivityRisk.MISSING_CREDENTIALS,
            AlpacaPaperConnectivityRisk.MISSING_CREDENTIALS,
            AlpacaPaperConnectivityRisk.OBSERVABILITY_GAP,
            AlpacaPaperConnectivityRisk.UNSAFE_CONNECTIVITY_CONFIGURATION,
        ),
        AlpacaPaperConnectivityState.PARTIALLY_READY,
    )

    assert recommendations.count(AlpacaPaperConnectivityRecommendation.DEFINE_CREDENTIAL_REQUIREMENTS) == 1
    assert AlpacaPaperConnectivityRecommendation.RESTORE_CONNECTIVITY_OBSERVABILITY in recommendations
    assert AlpacaPaperConnectivityRecommendation.LOCK_SAFE_CONNECTIVITY_CONFIGURATION in recommendations
    assert AlpacaPaperConnectivityRecommendation.RUN_CONNECTIVITY_READINESS_SUITE in recommendations


def test_ready_state_adds_mock_connectivity_approval_recommendation():
    result = evaluate_alpaca_paper_connectivity_readiness(_ready_input())

    assert (
        AlpacaPaperConnectivityRecommendation.APPROVE_MOCK_CONNECTIVITY_AFTER_MANUAL_REVIEW
        in result.recommendations
    )


def test_markdown_rendering_contains_reviews_graph_risks_and_recommendations():
    result = evaluate_alpaca_paper_connectivity_readiness(_ready_input(credential_schema_defined=False))
    markdown = render_connectivity_markdown(result)

    assert "# AGIcore Alpaca Paper Connectivity Readiness" in markdown
    assert "# Score Breakdown" in markdown
    assert "# Connectivity Reviews" in markdown
    assert "# Connectivity Graph" in markdown
    assert "MISSING_CREDENTIALS" in markdown
    assert "DEFINE_CREDENTIAL_REQUIREMENTS" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_alpaca_paper_connectivity_readiness(_ready_input().__dict__)

    assert result.state is AlpacaPaperConnectivityState.READY_FOR_MOCK_CONNECTIVITY
    assert result.connectivity_score >= 94


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            AlpacaPaperConnectivityRisk.KILL_SWITCH_INCOMPATIBILITY,
            AlpacaPaperConnectivityRecommendation.LINK_KILL_SWITCH_COMPATIBILITY,
        ),
        (
            AlpacaPaperConnectivityRisk.ROLLBACK_INCOMPATIBILITY,
            AlpacaPaperConnectivityRecommendation.LINK_ROLLBACK_COMPATIBILITY,
        ),
    ],
)
def test_recommendation_mapping_for_compatibility_risks(risk, recommendation):
    recommendations = generate_connectivity_recommendations((risk,), AlpacaPaperConnectivityState.PARTIALLY_READY)

    assert recommendation in recommendations


def test_module_keeps_offline_import_boundary():
    module_path = (
        Path(__file__).parents[3]
        / "src"
        / "agicore"
        / "trading"
        / "alpaca_paper_connectivity_readiness.py"
    )
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
