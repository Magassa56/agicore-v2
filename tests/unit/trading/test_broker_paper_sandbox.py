import ast
from pathlib import Path

import pytest

from agicore.trading.broker_paper_sandbox import (
    compute_sandbox_score,
    detect_sandbox_risks,
    evaluate_broker_paper_sandbox,
    generate_sandbox_recommendations,
    render_broker_paper_sandbox_markdown,
    verify_account_translation,
    verify_adapter_compatibility,
    verify_kill_switch_boundaries,
    verify_observability_boundaries,
    verify_order_translation,
    verify_position_translation,
    verify_rollback_boundaries,
    verify_safety_boundaries,
)
from agicore.trading.broker_paper_sandbox_models import (
    BrokerPaperSandboxInput,
    BrokerPaperSandboxRecommendation,
    BrokerPaperSandboxRisk,
    BrokerPaperSandboxState,
)


def _upstream(state="READY", score=96, risks=(), blockers=(), **extra):
    payload = {
        "state": state,
        "score": score,
        "risks": tuple(risks),
        "blockers": tuple(blockers),
        "offline_only": True,
        "score_breakdown": {
            "trial_score": score,
            "dry_run_score": score,
            "end_to_end_score": score,
            "adapter_score": score,
            "alpaca_adapter_score": score,
            "order_translation_score": score,
            "order_mapping_score": score,
            "paper_order_translation_score": score,
            "position_translation_score": score,
            "position_mapping_score": score,
            "paper_position_translation_score": score,
            "account_translation_score": score,
            "account_mapping_score": score,
            "paper_account_translation_score": score,
            "adapter_safety_score": score,
            "safety_gate_score": score,
            "observability_score": score,
            "kill_switch_score": score,
            "rollback_score": score,
        },
    }
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
        "supervised_paper_trial": _upstream("READY_FOR_BROKER_PAPER_SANDBOX"),
        "paper_dry_run": _upstream("READY_FOR_SUPERVISED_PAPER_TRIAL"),
        "paper_trading_end_to_end": _upstream("READY_FOR_PAPER_DRY_RUN"),
        "alpaca_paper_adapter": _upstream("READY_FOR_END_TO_END_PAPER"),
        "paper_broker_adapter": _upstream("READY_FOR_ALPACA_PAPER_ADAPTER"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "controlled_paper_run": _upstream("READY_FOR_HUMAN_VALIDATED_SESSION"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "paper_broker_adapter_ready": True,
        "alpaca_adapter_ready": True,
        "adapter_contract_version_locked": True,
        "sandbox_adapter_mode_enabled": True,
        "order_mapping_defined": True,
        "order_validation_defined": True,
        "order_idempotency_defined": True,
        "order_routing_disabled": True,
        "position_mapping_defined": True,
        "position_reconciliation_defined": True,
        "position_checkpointing_defined": True,
        "position_drift_monitoring_defined": True,
        "account_mapping_defined": True,
        "account_reconciliation_defined": True,
        "buying_power_mapping_defined": True,
        "account_state_checkpointing_defined": True,
        "safety_prechecks_required": True,
        "sandbox_order_limits_defined": True,
        "no_live_order_route": True,
        "no_api_keys_required": True,
        "observability_events_defined": True,
        "sandbox_metrics_defined": True,
        "audit_trail_defined": True,
        "critical_alerts_defined": True,
        "kill_switch_linked": True,
        "emergency_stop_path_defined": True,
        "operator_halt_required": True,
        "post_halt_state_safe": True,
        "rollback_linked": True,
        "recovery_point_required": True,
        "rollback_audit_defined": True,
        "restart_guard_defined": True,
        "offline_mode_enforced": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "external_dependencies_blocked": True,
        "configuration_locked": True,
        "sandbox_validated": True,
        "ready_for_alpaca_paper_connectivity": True,
        "adapter_compatibility_score": 96,
        "order_translation_score": 96,
        "position_translation_score": 96,
        "account_translation_score": 96,
        "safety_boundary_score": 96,
        "observability_boundary_score": 96,
        "kill_switch_boundary_score": 96,
        "rollback_boundary_score": 96,
    }
    payload.update(overrides)
    return BrokerPaperSandboxInput(**payload)


def test_evaluate_ready_for_alpaca_paper_connectivity():
    result = evaluate_broker_paper_sandbox(_ready_input())

    assert result.state is BrokerPaperSandboxState.READY_FOR_ALPACA_PAPER_CONNECTIVITY
    assert result.risks == ()
    assert result.offline_only is True
    assert result.sandbox_score >= 94
    assert result.sandbox_graph.blocked_edges == ()


def test_sandbox_validated_when_connectivity_gate_is_not_set():
    result = evaluate_broker_paper_sandbox(_ready_input(ready_for_alpaca_paper_connectivity=False))

    assert result.state is BrokerPaperSandboxState.SANDBOX_VALIDATED
    assert result.risks == ()


def test_sandbox_ready_when_not_validated_yet():
    result = evaluate_broker_paper_sandbox(_ready_input(sandbox_validated=False))

    assert result.state is BrokerPaperSandboxState.SANDBOX_READY
    assert result.risks == ()


def test_detects_every_sandbox_risk_when_all_boundaries_fail():
    failing_fields = {
        name: False
        for name in BrokerPaperSandboxInput.__dataclass_fields__
        if name.endswith(
            (
                "_ready",
                "_locked",
                "_enabled",
                "_defined",
                "_disabled",
                "_required",
                "_route",
                "_linked",
                "_safe",
                "_enforced",
                "_transport",
                "_blocked",
                "_validated",
                "_connectivity",
            )
        )
    }
    score_fields = {
        name: 10
        for name in BrokerPaperSandboxInput.__dataclass_fields__
        if name.endswith("_score")
    }

    result = evaluate_broker_paper_sandbox(_ready_input(**failing_fields, **score_fields))

    assert set(result.risks) == set(BrokerPaperSandboxRisk)
    assert result.state is BrokerPaperSandboxState.NOT_READY
    assert result.offline_only is False


def test_adapter_compatibility_detects_missing_adapter_contract():
    review = verify_adapter_compatibility(_ready_input(adapter_contract_version_locked=False))

    assert review.passed is False
    assert BrokerPaperSandboxRisk.ADAPTER_INCOMPATIBILITY in review.risks


def test_order_translation_detects_failure_drift_and_external_dependency():
    review = verify_order_translation(
        _ready_input(
            order_mapping_defined=False,
            order_idempotency_defined=False,
            order_routing_disabled=False,
        )
    )

    assert review.passed is False
    assert BrokerPaperSandboxRisk.ORDER_TRANSLATION_FAILURE in review.risks
    assert BrokerPaperSandboxRisk.SANDBOX_CONFIGURATION_DRIFT in review.risks
    assert BrokerPaperSandboxRisk.EXTERNAL_DEPENDENCY_RISK in review.risks


def test_position_translation_detects_failure_and_configuration_drift():
    review = verify_position_translation(
        _ready_input(position_mapping_defined=False, position_checkpointing_defined=False)
    )

    assert review.passed is False
    assert BrokerPaperSandboxRisk.POSITION_TRANSLATION_FAILURE in review.risks
    assert BrokerPaperSandboxRisk.SANDBOX_CONFIGURATION_DRIFT in review.risks


def test_account_translation_detects_failure_and_configuration_drift():
    review = verify_account_translation(
        _ready_input(account_mapping_defined=False, account_state_checkpointing_defined=False)
    )

    assert review.passed is False
    assert BrokerPaperSandboxRisk.ACCOUNT_TRANSLATION_FAILURE in review.risks
    assert BrokerPaperSandboxRisk.SANDBOX_CONFIGURATION_DRIFT in review.risks


def test_safety_boundaries_detect_missing_boundary_and_external_dependency():
    review = verify_safety_boundaries(_ready_input(safety_prechecks_required=False, no_api_keys_required=False))

    assert review.passed is False
    assert BrokerPaperSandboxRisk.SAFETY_BOUNDARY_MISSING in review.risks
    assert BrokerPaperSandboxRisk.EXTERNAL_DEPENDENCY_RISK in review.risks


def test_observability_boundaries_detect_missing_boundary():
    review = verify_observability_boundaries(_ready_input(audit_trail_defined=False))

    assert review.passed is False
    assert BrokerPaperSandboxRisk.OBSERVABILITY_BOUNDARY_MISSING in review.risks


def test_kill_switch_boundaries_detect_missing_boundary():
    review = verify_kill_switch_boundaries(_ready_input(kill_switch_linked=False))

    assert review.passed is False
    assert BrokerPaperSandboxRisk.KILL_SWITCH_BOUNDARY_MISSING in review.risks


def test_rollback_boundaries_detect_missing_boundary():
    review = verify_rollback_boundaries(_ready_input(rollback_linked=False))

    assert review.passed is False
    assert BrokerPaperSandboxRisk.ROLLBACK_BOUNDARY_MISSING in review.risks


def test_three_soft_risks_require_review():
    result = evaluate_broker_paper_sandbox(
        _ready_input(
            position_checkpointing_defined=False,
            account_state_checkpointing_defined=False,
            audit_trail_defined=False,
            rollback_linked=False,
        )
    )

    assert result.state is BrokerPaperSandboxState.REVIEW_REQUIRED
    assert BrokerPaperSandboxRisk.SANDBOX_CONFIGURATION_DRIFT in result.risks
    assert BrokerPaperSandboxRisk.OBSERVABILITY_BOUNDARY_MISSING in result.risks
    assert BrokerPaperSandboxRisk.ROLLBACK_BOUNDARY_MISSING in result.risks


def test_single_soft_risk_is_partially_ready():
    result = evaluate_broker_paper_sandbox(_ready_input(position_checkpointing_defined=False))

    assert result.state is BrokerPaperSandboxState.PARTIALLY_READY
    assert result.risks == (BrokerPaperSandboxRisk.SANDBOX_CONFIGURATION_DRIFT,)


def test_hard_risk_caps_score_and_not_ready():
    data = _ready_input(no_http_transport=False)
    risks = detect_sandbox_risks(data)
    score = compute_sandbox_score(data, risks)
    result = evaluate_broker_paper_sandbox(data)

    assert BrokerPaperSandboxRisk.EXTERNAL_DEPENDENCY_RISK in risks
    assert score.overall_score <= 40
    assert result.state is BrokerPaperSandboxState.NOT_READY


def test_upstream_broker_or_network_risk_keeps_sandbox_offline_boundary_closed():
    upstream = _upstream(risks=("NETWORK_LEAK",))
    result = evaluate_broker_paper_sandbox(_ready_input(supervised_paper_trial=upstream))

    assert result.state is BrokerPaperSandboxState.NOT_READY
    assert result.offline_only is False
    assert BrokerPaperSandboxRisk.EXTERNAL_DEPENDENCY_RISK in result.risks


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_sandbox_recommendations(
        (
            BrokerPaperSandboxRisk.ADAPTER_INCOMPATIBILITY,
            BrokerPaperSandboxRisk.ADAPTER_INCOMPATIBILITY,
            BrokerPaperSandboxRisk.OBSERVABILITY_BOUNDARY_MISSING,
            BrokerPaperSandboxRisk.EXTERNAL_DEPENDENCY_RISK,
        ),
        BrokerPaperSandboxState.PARTIALLY_READY,
    )

    assert recommendations.count(BrokerPaperSandboxRecommendation.REPAIR_ADAPTER_COMPATIBILITY) == 1
    assert BrokerPaperSandboxRecommendation.DEFINE_OBSERVABILITY_BOUNDARY in recommendations
    assert BrokerPaperSandboxRecommendation.REMOVE_EXTERNAL_DEPENDENCY in recommendations
    assert BrokerPaperSandboxRecommendation.RUN_BROKER_PAPER_SANDBOX_SUITE in recommendations


def test_ready_state_adds_alpaca_connectivity_approval_recommendation():
    result = evaluate_broker_paper_sandbox(_ready_input())

    assert (
        BrokerPaperSandboxRecommendation.APPROVE_ALPACA_PAPER_CONNECTIVITY_AFTER_MANUAL_REVIEW
        in result.recommendations
    )


def test_markdown_rendering_contains_reviews_graph_risks_and_recommendations():
    result = evaluate_broker_paper_sandbox(_ready_input(adapter_contract_version_locked=False))
    markdown = render_broker_paper_sandbox_markdown(result)

    assert "# AGIcore Broker Paper Sandbox" in markdown
    assert "# Score Breakdown" in markdown
    assert "# Sandbox Reviews" in markdown
    assert "# Sandbox Graph" in markdown
    assert "ADAPTER_INCOMPATIBILITY" in markdown
    assert "REPAIR_ADAPTER_COMPATIBILITY" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_broker_paper_sandbox(_ready_input().__dict__)

    assert result.state is BrokerPaperSandboxState.READY_FOR_ALPACA_PAPER_CONNECTIVITY
    assert result.sandbox_score >= 94


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            BrokerPaperSandboxRisk.ROLLBACK_BOUNDARY_MISSING,
            BrokerPaperSandboxRecommendation.DEFINE_ROLLBACK_BOUNDARY,
        ),
        (
            BrokerPaperSandboxRisk.KILL_SWITCH_BOUNDARY_MISSING,
            BrokerPaperSandboxRecommendation.DEFINE_KILL_SWITCH_BOUNDARY,
        ),
    ],
)
def test_recommendation_mapping_for_boundary_risks(risk, recommendation):
    recommendations = generate_sandbox_recommendations((risk,), BrokerPaperSandboxState.PARTIALLY_READY)

    assert recommendation in recommendations


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "broker_paper_sandbox.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
