import ast
from pathlib import Path

import pytest

from agicore.trading.paper_trading_end_to_end import (
    compute_end_to_end_score,
    detect_end_to_end_risks,
    evaluate_paper_trading_end_to_end,
    generate_end_to_end_recommendations,
    render_paper_trading_end_to_end_markdown,
    verify_adapter_pipeline,
    verify_decision_pipeline,
    verify_journal_pipeline,
    verify_observability_pipeline,
    verify_order_pipeline,
    verify_position_pipeline,
    verify_safety_pipeline,
    verify_signal_pipeline,
)
from agicore.trading.paper_trading_end_to_end_models import (
    PaperTradingEndToEndInput,
    PaperTradingEndToEndRecommendation,
    PaperTradingEndToEndRisk,
    PaperTradingEndToEndState,
)


def _upstream(state="READY", score=96, risks=(), blockers=(), **extra):
    payload = {
        "state": state,
        "score": score,
        "risks": tuple(risks),
        "blockers": tuple(blockers),
        "offline_only": True,
        "score_breakdown": {
            "alpaca_adapter_score": score,
            "adapter_score": score,
            "supervised_session_score": score,
            "human_validation_score": score,
            "controlled_paper_score": score,
            "paper_loop_score": score,
            "paper_runtime_score": score,
            "observability_score": score,
            "rollback_score": score,
            "kill_switch_score": score,
        },
    }
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
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
        "signal_input_available": True,
        "signal_validation_available": True,
        "signal_context_attached": True,
        "signal_to_decision_linked": True,
        "decision_pipeline_available": True,
        "decision_context_scored": True,
        "decision_output_deterministic": True,
        "decision_to_safety_linked": True,
        "safety_gate_available": True,
        "risk_precheck_available": True,
        "kill_switch_linked": True,
        "rollback_linked": True,
        "safety_to_adapter_linked": True,
        "paper_broker_adapter_ready": True,
        "alpaca_paper_adapter_ready": True,
        "adapter_offline_only": True,
        "adapter_to_order_linked": True,
        "paper_order_model_available": True,
        "paper_order_validation_available": True,
        "paper_order_translation_available": True,
        "paper_order_idempotent": True,
        "paper_position_model_available": True,
        "paper_position_reconciliation_available": True,
        "paper_position_checkpointed": True,
        "position_pnl_available": True,
        "paper_journal_available": True,
        "paper_journal_records_orders": True,
        "paper_journal_records_positions": True,
        "paper_journal_exports_audit": True,
        "observability_events_available": True,
        "metrics_available": True,
        "critical_alerts_available": True,
        "result_summary_available": True,
        "end_to_end_state_reconciled": True,
        "offline_mode_enforced": True,
        "ready_for_paper_dry_run": True,
        "signal_pipeline_score": 96,
        "decision_pipeline_score": 96,
        "safety_pipeline_score": 96,
        "adapter_pipeline_score": 96,
        "order_pipeline_score": 96,
        "position_pipeline_score": 96,
        "journal_pipeline_score": 96,
        "observability_pipeline_score": 96,
    }
    payload.update(overrides)
    return PaperTradingEndToEndInput(**payload)


def test_evaluate_ready_for_paper_dry_run():
    result = evaluate_paper_trading_end_to_end(_ready_input())

    assert result.state is PaperTradingEndToEndState.READY_FOR_PAPER_DRY_RUN
    assert result.risks == ()
    assert result.offline_only is True
    assert result.end_to_end_score >= 94
    reviews = (
        result.signal_pipeline_review,
        result.decision_pipeline_review,
        result.safety_pipeline_review,
        result.adapter_pipeline_review,
        result.order_pipeline_review,
        result.position_pipeline_review,
        result.journal_pipeline_review,
        result.observability_pipeline_review,
    )
    assert all(review.passed for review in reviews)
    assert ("signal", "decision") in result.end_to_end_graph.ready_edges
    assert ("observability", "result") in result.end_to_end_graph.ready_edges


def test_detects_every_end_to_end_risk_when_pipeline_is_missing():
    failing_fields = {
        name: False
        for name in PaperTradingEndToEndInput.__dataclass_fields__
        if name.endswith(
            (
                "_available",
                "_attached",
                "_linked",
                "_scored",
                "_deterministic",
                "_ready",
                "_only",
                "_idempotent",
                "_checkpointed",
                "_audit",
                "_reconciled",
                "_enforced",
                "_dry_run",
            )
        )
    }
    score_fields = {
        name: 10
        for name in PaperTradingEndToEndInput.__dataclass_fields__
        if name.endswith("_score")
    }

    result = evaluate_paper_trading_end_to_end(_ready_input(**failing_fields, **score_fields))

    assert set(result.risks) == set(PaperTradingEndToEndRisk)
    assert result.state is PaperTradingEndToEndState.NOT_READY
    assert result.offline_only is False


def test_signal_pipeline_failure_blocks_decision_edge():
    result = evaluate_paper_trading_end_to_end(_ready_input(signal_input_available=False))

    assert result.state is PaperTradingEndToEndState.NOT_READY
    assert PaperTradingEndToEndRisk.SIGNAL_PIPELINE_FAILURE in result.risks
    assert ("signal", "decision") in result.end_to_end_graph.blocked_edges


def test_decision_pipeline_detects_failure_and_state_drift():
    review = verify_decision_pipeline(
        _ready_input(decision_pipeline_available=False, decision_output_deterministic=False)
    )

    assert review.passed is False
    assert PaperTradingEndToEndRisk.DECISION_PIPELINE_FAILURE in review.risks
    assert PaperTradingEndToEndRisk.STATE_DRIFT_RISK in review.risks


def test_safety_pipeline_detects_gate_failure_and_missing_rollback():
    review = verify_safety_pipeline(_ready_input(safety_gate_available=False, rollback_linked=False))

    assert review.passed is False
    assert PaperTradingEndToEndRisk.SAFETY_GATE_FAILURE in review.risks
    assert PaperTradingEndToEndRisk.STATE_DRIFT_RISK in review.risks


def test_adapter_pipeline_detects_adapter_failure_and_offline_inconsistency():
    review = verify_adapter_pipeline(
        _ready_input(alpaca_paper_adapter_ready=False, adapter_offline_only=False)
    )

    assert review.passed is False
    assert PaperTradingEndToEndRisk.ADAPTER_PIPELINE_FAILURE in review.risks
    assert PaperTradingEndToEndRisk.END_TO_END_INCONSISTENCY in review.risks


def test_order_pipeline_detects_translation_failure_and_non_idempotence():
    review = verify_order_pipeline(
        _ready_input(paper_order_translation_available=False, paper_order_idempotent=False)
    )

    assert review.passed is False
    assert PaperTradingEndToEndRisk.ORDER_PIPELINE_FAILURE in review.risks
    assert PaperTradingEndToEndRisk.STATE_DRIFT_RISK in review.risks


def test_position_pipeline_detects_reconciliation_failure_and_missing_checkpoint():
    review = verify_position_pipeline(
        _ready_input(
            paper_position_reconciliation_available=False,
            paper_position_checkpointed=False,
        )
    )

    assert review.passed is False
    assert PaperTradingEndToEndRisk.POSITION_PIPELINE_FAILURE in review.risks
    assert PaperTradingEndToEndRisk.STATE_DRIFT_RISK in review.risks


def test_journal_pipeline_detects_audit_gap():
    review = verify_journal_pipeline(_ready_input(paper_journal_exports_audit=False))

    assert review.passed is False
    assert PaperTradingEndToEndRisk.JOURNAL_PIPELINE_FAILURE in review.risks


def test_observability_pipeline_detects_visibility_failure_and_state_drift():
    review = verify_observability_pipeline(
        _ready_input(observability_events_available=False, end_to_end_state_reconciled=False)
    )

    assert review.passed is False
    assert PaperTradingEndToEndRisk.OBSERVABILITY_FAILURE in review.risks
    assert PaperTradingEndToEndRisk.STATE_DRIFT_RISK in review.risks


def test_three_soft_risks_require_review():
    result = evaluate_paper_trading_end_to_end(
        _ready_input(
            paper_position_checkpointed=False,
            paper_journal_available=False,
            observability_events_available=False,
        )
    )

    assert result.state is PaperTradingEndToEndState.REVIEW_REQUIRED
    assert PaperTradingEndToEndRisk.STATE_DRIFT_RISK in result.risks
    assert PaperTradingEndToEndRisk.JOURNAL_PIPELINE_FAILURE in result.risks
    assert PaperTradingEndToEndRisk.OBSERVABILITY_FAILURE in result.risks


def test_single_soft_risk_is_partially_ready():
    result = evaluate_paper_trading_end_to_end(_ready_input(paper_position_checkpointed=False))

    assert result.state is PaperTradingEndToEndState.PARTIALLY_READY
    assert result.risks == (PaperTradingEndToEndRisk.STATE_DRIFT_RISK,)


def test_clean_pipeline_without_manual_gate_is_end_to_end_ready():
    result = evaluate_paper_trading_end_to_end(
        _ready_input(
            ready_for_paper_dry_run=False,
            signal_pipeline_score=89,
            decision_pipeline_score=89,
            safety_pipeline_score=89,
            adapter_pipeline_score=89,
            order_pipeline_score=89,
            position_pipeline_score=89,
            journal_pipeline_score=89,
            observability_pipeline_score=89,
        )
    )

    assert result.state is PaperTradingEndToEndState.END_TO_END_READY
    assert result.risks == ()


def test_score_is_capped_by_hard_pipeline_risks():
    data = _ready_input(signal_input_available=False, adapter_offline_only=False)
    risks = detect_end_to_end_risks(data)
    score = compute_end_to_end_score(data, risks)

    assert PaperTradingEndToEndRisk.SIGNAL_PIPELINE_FAILURE in risks
    assert PaperTradingEndToEndRisk.END_TO_END_INCONSISTENCY in risks
    assert score.overall_score <= 45


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_end_to_end_recommendations(
        (
            PaperTradingEndToEndRisk.SIGNAL_PIPELINE_FAILURE,
            PaperTradingEndToEndRisk.SIGNAL_PIPELINE_FAILURE,
            PaperTradingEndToEndRisk.OBSERVABILITY_FAILURE,
            PaperTradingEndToEndRisk.STATE_DRIFT_RISK,
        ),
        PaperTradingEndToEndState.PARTIALLY_READY,
    )

    assert recommendations.count(
        PaperTradingEndToEndRecommendation.REPAIR_SIGNAL_PIPELINE
    ) == 1
    assert PaperTradingEndToEndRecommendation.RESTORE_OBSERVABILITY in recommendations
    assert PaperTradingEndToEndRecommendation.LOCK_STATE_DETERMINISM in recommendations
    assert PaperTradingEndToEndRecommendation.RUN_END_TO_END_READINESS_SUITE in recommendations


def test_ready_state_adds_manual_dry_run_approval_recommendation():
    result = evaluate_paper_trading_end_to_end(_ready_input())

    assert (
        PaperTradingEndToEndRecommendation.APPROVE_PAPER_DRY_RUN_AFTER_MANUAL_REVIEW
        in result.recommendations
    )


def test_markdown_rendering_contains_score_reviews_graph_and_risks():
    result = evaluate_paper_trading_end_to_end(_ready_input(signal_input_available=False))
    markdown = render_paper_trading_end_to_end_markdown(result)

    assert "# AGIcore Paper Trading End-to-End" in markdown
    assert "# Score Breakdown" in markdown
    assert "# End-to-End Reviews" in markdown
    assert "# End-to-End Graph" in markdown
    assert "SIGNAL_PIPELINE_FAILURE" in markdown
    assert "REPAIR_SIGNAL_PIPELINE" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_paper_trading_end_to_end(_ready_input().__dict__)

    assert result.state is PaperTradingEndToEndState.READY_FOR_PAPER_DRY_RUN
    assert result.end_to_end_score >= 94


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            PaperTradingEndToEndRisk.ADAPTER_PIPELINE_FAILURE,
            PaperTradingEndToEndRecommendation.REPAIR_ADAPTER_PIPELINE,
        ),
        (
            PaperTradingEndToEndRisk.END_TO_END_INCONSISTENCY,
            PaperTradingEndToEndRecommendation.RECONCILE_END_TO_END_FLOW,
        ),
    ],
)
def test_recommendation_mapping_for_adapter_and_consistency_risks(risk, recommendation):
    recommendations = generate_end_to_end_recommendations(
        (risk,),
        PaperTradingEndToEndState.PARTIALLY_READY,
    )

    assert recommendation in recommendations


def test_module_keeps_offline_import_boundary():
    module_path = (
        Path(__file__).parents[3]
        / "src"
        / "agicore"
        / "trading"
        / "paper_trading_end_to_end.py"
    )
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
