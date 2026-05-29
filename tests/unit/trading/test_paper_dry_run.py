import ast
from pathlib import Path

import pytest

from agicore.trading.paper_dry_run import (
    compute_dry_run_score,
    detect_dry_run_risks,
    evaluate_paper_dry_run,
    generate_dry_run_recommendations,
    render_paper_dry_run_markdown,
    simulate_decision_flow,
    simulate_journal_flow,
    simulate_observability_flow,
    simulate_paper_order_flow,
    simulate_position_update_flow,
    simulate_safety_gate_flow,
    simulate_signal_flow,
)
from agicore.trading.paper_dry_run_models import (
    PaperDryRunInput,
    PaperDryRunRecommendation,
    PaperDryRunRisk,
    PaperDryRunState,
)


def _upstream(state="READY", score=96, risks=(), blockers=(), **extra):
    payload = {
        "state": state,
        "score": score,
        "risks": tuple(risks),
        "blockers": tuple(blockers),
        "offline_only": True,
        "score_breakdown": {
            "overall_score": score,
            "end_to_end_score": score,
            "alpaca_adapter_score": score,
            "adapter_score": score,
            "paper_loop_score": score,
            "paper_runtime_score": score,
            "observability_score": score,
            "rollback_score": score,
            "kill_switch_score": score,
            "signal_pipeline_score": score,
            "decision_pipeline_score": score,
            "safety_pipeline_score": score,
            "order_pipeline_score": score,
            "position_pipeline_score": score,
            "journal_pipeline_score": score,
            "observability_pipeline_score": score,
        },
    }
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_trading_end_to_end": _upstream("READY_FOR_PAPER_DRY_RUN"),
        "alpaca_paper_adapter": _upstream("READY_FOR_END_TO_END_PAPER"),
        "paper_broker_adapter": _upstream("READY_FOR_ALPACA_PAPER_ADAPTER"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "controlled_paper_run": _upstream("READY_FOR_HUMAN_VALIDATED_SESSION"),
        "paper_execution_loop_readiness": _upstream("READY_FOR_CONTROLLED_PAPER_RUN"),
        "paper_runtime_preparation": _upstream("READY_FOR_PAPER_EXECUTION_LOOP"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "signal_event_available": True,
        "signal_payload_valid": True,
        "signal_timestamp_present": True,
        "signal_flow_repeatable": True,
        "decision_generated": True,
        "decision_uses_signal": True,
        "decision_deterministic": True,
        "decision_trace_available": True,
        "safety_gate_available": True,
        "safety_gate_passed": True,
        "safety_reason_recorded": True,
        "safety_bypass_prevented": True,
        "paper_order_created": True,
        "paper_order_validated": True,
        "paper_order_not_routed": True,
        "paper_order_idempotent": True,
        "position_updated": True,
        "position_reconciled": True,
        "position_checkpointed": True,
        "pnl_computed": True,
        "journal_entry_written": True,
        "journal_links_order_position": True,
        "journal_audit_trail_complete": True,
        "journal_repeatable": True,
        "observability_event_emitted": True,
        "metrics_recorded": True,
        "trace_recorded": True,
        "result_visible": True,
        "state_reconciled": True,
        "dry_run_repeatable": True,
        "offline_mode_enforced": True,
        "dry_run_executed": True,
        "ready_for_supervised_paper_trial": True,
        "signal_flow_score": 96,
        "decision_flow_score": 96,
        "safety_gate_score": 96,
        "paper_order_flow_score": 96,
        "position_update_score": 96,
        "journal_flow_score": 96,
        "observability_flow_score": 96,
    }
    payload.update(overrides)
    return PaperDryRunInput(**payload)


def test_evaluate_ready_for_supervised_paper_trial():
    result = evaluate_paper_dry_run(_ready_input())

    assert result.state is PaperDryRunState.READY_FOR_SUPERVISED_PAPER_TRIAL
    assert result.risks == ()
    assert result.offline_only is True
    assert result.dry_run_score >= 94
    assert result.dry_run_trace.blocked_steps == ()
    assert result.dry_run_trace.completed_steps[-1] == "result"


def test_dry_run_completed_when_trial_gate_is_not_set():
    result = evaluate_paper_dry_run(_ready_input(ready_for_supervised_paper_trial=False))

    assert result.state is PaperDryRunState.DRY_RUN_COMPLETED
    assert result.risks == ()


def test_dry_run_ready_when_not_executed_yet():
    result = evaluate_paper_dry_run(_ready_input(dry_run_executed=False))

    assert result.state is PaperDryRunState.DRY_RUN_READY
    assert result.risks == ()


def test_detects_every_dry_run_risk_when_all_flows_fail():
    failing_fields = {
        name: False
        for name in PaperDryRunInput.__dataclass_fields__
        if name.endswith(
            (
                "_available",
                "_valid",
                "_present",
                "_repeatable",
                "_generated",
                "_signal",
                "_deterministic",
                "_passed",
                "_recorded",
                "_prevented",
                "_created",
                "_validated",
                "_routed",
                "_idempotent",
                "_updated",
                "_reconciled",
                "_checkpointed",
                "_computed",
                "_written",
                "_position",
                "_complete",
                "_emitted",
                "_visible",
                "_enforced",
                "_executed",
                "_trial",
            )
        )
    }
    score_fields = {
        name: 10
        for name in PaperDryRunInput.__dataclass_fields__
        if name.endswith("_score")
    }

    result = evaluate_paper_dry_run(_ready_input(**failing_fields, **score_fields))

    assert set(result.risks) == set(PaperDryRunRisk)
    assert result.state is PaperDryRunState.NOT_READY
    assert result.offline_only is False


def test_signal_flow_detects_missing_signal_and_repeatability_gap():
    flow = simulate_signal_flow(
        _ready_input(signal_event_available=False, signal_flow_repeatable=False)
    )

    assert flow.passed is False
    assert PaperDryRunRisk.SIGNAL_FLOW_FAILURE in flow.risks
    assert PaperDryRunRisk.DRY_RUN_NOT_REPEATABLE in flow.risks


def test_decision_flow_detects_failure_and_state_drift():
    flow = simulate_decision_flow(_ready_input(decision_generated=False, decision_deterministic=False))

    assert flow.passed is False
    assert PaperDryRunRisk.DECISION_FLOW_FAILURE in flow.risks
    assert PaperDryRunRisk.STATE_DRIFT_DETECTED in flow.risks


def test_safety_gate_flow_detects_block_and_bypass_risk():
    flow = simulate_safety_gate_flow(_ready_input(safety_gate_passed=False, safety_bypass_prevented=False))

    assert flow.passed is False
    assert PaperDryRunRisk.SAFETY_GATE_BLOCKED in flow.risks
    assert PaperDryRunRisk.SAFETY_BYPASS_RISK in flow.risks


def test_paper_order_flow_detects_simulation_failure_and_non_repeatability():
    flow = simulate_paper_order_flow(_ready_input(paper_order_not_routed=False, paper_order_idempotent=False))

    assert flow.passed is False
    assert PaperDryRunRisk.PAPER_ORDER_SIMULATION_FAILURE in flow.risks
    assert PaperDryRunRisk.DRY_RUN_NOT_REPEATABLE in flow.risks


def test_position_update_flow_detects_update_failure_and_state_drift():
    flow = simulate_position_update_flow(_ready_input(position_updated=False, position_checkpointed=False))

    assert flow.passed is False
    assert PaperDryRunRisk.POSITION_UPDATE_FAILURE in flow.risks
    assert PaperDryRunRisk.STATE_DRIFT_DETECTED in flow.risks


def test_journal_flow_detects_write_failure_and_repeatability_gap():
    flow = simulate_journal_flow(_ready_input(journal_entry_written=False, journal_repeatable=False))

    assert flow.passed is False
    assert PaperDryRunRisk.JOURNAL_WRITE_FAILURE in flow.risks
    assert PaperDryRunRisk.DRY_RUN_NOT_REPEATABLE in flow.risks


def test_observability_flow_detects_missing_event_and_state_drift():
    flow = simulate_observability_flow(
        _ready_input(observability_event_emitted=False, state_reconciled=False)
    )

    assert flow.passed is False
    assert PaperDryRunRisk.OBSERVABILITY_EVENT_MISSING in flow.risks
    assert PaperDryRunRisk.STATE_DRIFT_DETECTED in flow.risks


def test_three_soft_risks_require_review():
    result = evaluate_paper_dry_run(
        _ready_input(
            position_checkpointed=False,
            journal_repeatable=False,
            observability_event_emitted=False,
        )
    )

    assert result.state is PaperDryRunState.REVIEW_REQUIRED
    assert PaperDryRunRisk.STATE_DRIFT_DETECTED in result.risks
    assert PaperDryRunRisk.DRY_RUN_NOT_REPEATABLE in result.risks
    assert PaperDryRunRisk.OBSERVABILITY_EVENT_MISSING in result.risks


def test_single_soft_risk_is_partially_ready():
    result = evaluate_paper_dry_run(_ready_input(position_checkpointed=False))

    assert result.state is PaperDryRunState.PARTIALLY_READY
    assert result.risks == (PaperDryRunRisk.STATE_DRIFT_DETECTED,)


def test_hard_risk_caps_score_and_not_ready():
    data = _ready_input(safety_gate_passed=False, safety_bypass_prevented=False)
    risks = detect_dry_run_risks(data)
    score = compute_dry_run_score(data, risks)
    result = evaluate_paper_dry_run(data)

    assert PaperDryRunRisk.SAFETY_GATE_BLOCKED in risks
    assert PaperDryRunRisk.SAFETY_BYPASS_RISK in risks
    assert score.overall_score <= 40
    assert result.state is PaperDryRunState.NOT_READY


def test_upstream_broker_or_network_risk_keeps_dry_run_offline_boundary_closed():
    upstream = _upstream(risks=("BROKER_CONNECTION_RISK",))
    result = evaluate_paper_dry_run(_ready_input(paper_broker_adapter=upstream))

    assert result.state is PaperDryRunState.NOT_READY
    assert result.offline_only is False
    assert PaperDryRunRisk.PAPER_ORDER_SIMULATION_FAILURE in result.risks


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_dry_run_recommendations(
        (
            PaperDryRunRisk.SIGNAL_FLOW_FAILURE,
            PaperDryRunRisk.SIGNAL_FLOW_FAILURE,
            PaperDryRunRisk.OBSERVABILITY_EVENT_MISSING,
            PaperDryRunRisk.DRY_RUN_NOT_REPEATABLE,
        ),
        PaperDryRunState.PARTIALLY_READY,
    )

    assert recommendations.count(PaperDryRunRecommendation.REPAIR_SIGNAL_FLOW) == 1
    assert PaperDryRunRecommendation.RESTORE_OBSERVABILITY_EVENT in recommendations
    assert PaperDryRunRecommendation.STABILIZE_REPEATABILITY in recommendations
    assert PaperDryRunRecommendation.RUN_PAPER_DRY_RUN_SUITE in recommendations


def test_ready_state_adds_supervised_trial_approval_recommendation():
    result = evaluate_paper_dry_run(_ready_input())

    assert (
        PaperDryRunRecommendation.APPROVE_SUPERVISED_PAPER_TRIAL_AFTER_MANUAL_REVIEW
        in result.recommendations
    )


def test_markdown_rendering_contains_flows_trace_risks_and_recommendations():
    result = evaluate_paper_dry_run(_ready_input(signal_event_available=False))
    markdown = render_paper_dry_run_markdown(result)

    assert "# AGIcore Paper Dry Run" in markdown
    assert "# Score Breakdown" in markdown
    assert "# Dry Run Flows" in markdown
    assert "# Dry Run Trace" in markdown
    assert "SIGNAL_FLOW_FAILURE" in markdown
    assert "REPAIR_SIGNAL_FLOW" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_paper_dry_run(_ready_input().__dict__)

    assert result.state is PaperDryRunState.READY_FOR_SUPERVISED_PAPER_TRIAL
    assert result.dry_run_score >= 94


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            PaperDryRunRisk.PAPER_ORDER_SIMULATION_FAILURE,
            PaperDryRunRecommendation.REPAIR_PAPER_ORDER_SIMULATION,
        ),
        (
            PaperDryRunRisk.SAFETY_BYPASS_RISK,
            PaperDryRunRecommendation.VERIFY_SAFETY_BYPASS_PREVENTION,
        ),
    ],
)
def test_recommendation_mapping_for_order_and_safety_risks(risk, recommendation):
    recommendations = generate_dry_run_recommendations((risk,), PaperDryRunState.PARTIALLY_READY)

    assert recommendation in recommendations


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "paper_dry_run.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
