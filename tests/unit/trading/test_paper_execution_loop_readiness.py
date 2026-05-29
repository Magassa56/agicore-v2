from types import SimpleNamespace

import pytest

from agicore.trading.paper_execution_loop_readiness import (
    compute_paper_loop_score,
    detect_paper_loop_blockers,
    evaluate_paper_execution_loop_readiness,
    generate_paper_loop_recommendations,
    render_paper_execution_loop_readiness_markdown,
    verify_decision_pipeline_readiness,
    verify_paper_journal_readiness,
    verify_safety_gate_readiness,
    verify_signal_input_readiness,
    verify_simulated_execution_readiness,
)
from agicore.trading.paper_execution_loop_readiness_models import (
    PaperExecutionLoopReadinessInput,
    PaperExecutionLoopReadinessState,
    PaperExecutionLoopRecommendation,
    PaperExecutionLoopRisk,
)


def _upstream(**overrides):
    data = {
        "state": "READY",
        "paper_runtime_score": 96,
        "observability_score": 96,
        "rollback_score": 96,
        "kill_switch_score": 96,
        "isolation_score": 96,
        "sandbox_score": 96,
        "risks": (),
        "blockers": (),
        "offline_only": True,
        "score_breakdown": SimpleNamespace(
            paper_runtime_score=96,
            observability_score=96,
            rollback_score=96,
            kill_switch_score=96,
            isolation_score=96,
        ),
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def _ready_input(**overrides):
    data = {
        "paper_runtime_preparation": _upstream(state="READY_FOR_PAPER_EXECUTION_LOOP"),
        "observability_verification": _upstream(state="READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream(state="READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream(state="READY_FOR_ROLLBACK_VERIFICATION"),
        "runtime_isolation_review": _upstream(state="READY_FOR_PAPER_RUNTIME"),
        "sandbox_readiness_audit": _upstream(state="SANDBOX_READY"),
        "stable_review": _upstream(state="STABLE"),
        "signal_source_available": True,
        "context_signal_available": True,
        "strategy_signal_available": True,
        "signal_validation_enabled": True,
        "semi_auto_decision_ready": True,
        "context_scoring_connected": True,
        "strategy_dna_connected": True,
        "decision_output_deterministic": True,
        "safety_prechecks_enabled": True,
        "risk_engine_connected": True,
        "kill_switch_linked": True,
        "rollback_linked": True,
        "simulated_adapter_available": True,
        "simulated_order_path_verified": True,
        "real_broker_blocked": True,
        "execution_events_emitted": True,
        "paper_journal_available": True,
        "paper_trade_events_recorded": True,
        "paper_pnl_recorded": True,
        "paper_audit_export_available": True,
        "loop_observability_connected": True,
        "paper_loop_state_checkpointed": True,
        "ready_for_controlled_paper_run": True,
        "signal_input_score": 96,
        "decision_pipeline_score": 96,
        "safety_gate_score": 96,
        "simulated_execution_score": 96,
        "paper_journal_score": 96,
        "loop_observability_score": 96,
    }
    data.update(overrides)
    return PaperExecutionLoopReadinessInput(**data)


def test_evaluate_paper_loop_ready_for_controlled_run_when_all_components_are_ready():
    result = evaluate_paper_execution_loop_readiness(_ready_input())

    assert result.state is PaperExecutionLoopReadinessState.READY_FOR_CONTROLLED_PAPER_RUN
    assert result.blockers == ()
    assert result.paper_loop_score >= 94
    assert result.offline_only is True
    assert result.paper_loop_graph.ready_edges == (
        ("signal_inputs", "decision_pipeline"),
        ("decision_pipeline", "safety_gate"),
        ("safety_gate", "simulated_execution"),
        ("simulated_execution", "paper_journal"),
        ("paper_journal", "controlled_paper_run"),
    )
    assert result.signal_input_review.passed is True
    assert result.decision_pipeline_review.passed is True
    assert result.safety_gate_review.passed is True
    assert result.simulated_execution_review.passed is True
    assert result.paper_journal_review.passed is True


def test_detect_paper_loop_blockers_reports_all_failures():
    data = _ready_input(
        signal_source_available=False,
        context_signal_available=False,
        strategy_signal_available=False,
        signal_validation_enabled=False,
        semi_auto_decision_ready=False,
        context_scoring_connected=False,
        strategy_dna_connected=False,
        decision_output_deterministic=False,
        safety_prechecks_enabled=False,
        risk_engine_connected=False,
        kill_switch_linked=False,
        rollback_linked=False,
        simulated_adapter_available=False,
        simulated_order_path_verified=False,
        real_broker_blocked=False,
        execution_events_emitted=False,
        paper_journal_available=False,
        paper_trade_events_recorded=False,
        paper_pnl_recorded=False,
        paper_audit_export_available=False,
        loop_observability_connected=False,
        paper_loop_state_checkpointed=False,
        signal_input_score=10,
        decision_pipeline_score=10,
        safety_gate_score=10,
        simulated_execution_score=10,
        paper_journal_score=10,
        loop_observability_score=10,
    )

    blockers = detect_paper_loop_blockers(data)

    assert set(blockers) == set(PaperExecutionLoopRisk)


def test_missing_signal_input_forces_not_ready():
    result = evaluate_paper_execution_loop_readiness(
        _ready_input(signal_source_available=False)
    )

    assert result.state is PaperExecutionLoopReadinessState.NOT_READY
    assert PaperExecutionLoopRisk.SIGNAL_INPUT_MISSING in result.blockers
    assert result.paper_loop_graph.blocked_edges == (
        ("signal_inputs", "decision_pipeline"),
    )


def test_simulated_execution_unready_forces_not_ready_and_offline_false():
    result = evaluate_paper_execution_loop_readiness(
        _ready_input(simulated_adapter_available=False, real_broker_blocked=False)
    )

    assert result.state is PaperExecutionLoopReadinessState.NOT_READY
    assert result.offline_only is False
    assert PaperExecutionLoopRisk.SIMULATED_EXECUTION_UNREADY in result.blockers


def test_three_soft_blockers_require_review_without_hard_failure():
    result = evaluate_paper_execution_loop_readiness(
        _ready_input(
            paper_journal_available=False,
            loop_observability_connected=False,
            paper_loop_state_checkpointed=False,
        )
    )

    assert result.state is PaperExecutionLoopReadinessState.REVIEW_REQUIRED
    assert {
        PaperExecutionLoopRisk.PAPER_JOURNAL_MISSING,
        PaperExecutionLoopRisk.OBSERVABILITY_BLIND_SPOT,
        PaperExecutionLoopRisk.PAPER_LOOP_STATE_CORRUPTION_RISK,
    }.issubset(result.blockers)


def test_single_soft_blocker_yields_partially_ready():
    result = evaluate_paper_execution_loop_readiness(_ready_input(paper_pnl_recorded=False))

    assert result.state is PaperExecutionLoopReadinessState.PARTIALLY_READY
    assert result.blockers == (PaperExecutionLoopRisk.PAPER_LOOP_STATE_CORRUPTION_RISK,)


def test_paper_loop_ready_when_clean_but_controlled_run_gate_not_ready():
    result = evaluate_paper_execution_loop_readiness(
        _ready_input(
            ready_for_controlled_paper_run=False,
            signal_input_score=89,
            decision_pipeline_score=89,
            safety_gate_score=89,
            simulated_execution_score=89,
            paper_journal_score=89,
            loop_observability_score=89,
        )
    )

    assert result.state is PaperExecutionLoopReadinessState.PAPER_LOOP_READY
    assert result.blockers == ()
    assert result.paper_loop_score >= 88


def test_review_sections_expose_specific_paper_loop_blockers():
    data = _ready_input(
        signal_source_available=False,
        context_scoring_connected=False,
        risk_engine_connected=False,
        simulated_adapter_available=False,
        paper_journal_available=False,
    )

    assert PaperExecutionLoopRisk.SIGNAL_INPUT_MISSING in verify_signal_input_readiness(data).risks
    assert PaperExecutionLoopRisk.DECISION_PIPELINE_INCOMPLETE in verify_decision_pipeline_readiness(data).risks
    assert PaperExecutionLoopRisk.RISK_ENGINE_NOT_CONNECTED in verify_safety_gate_readiness(data).risks
    assert PaperExecutionLoopRisk.SIMULATED_EXECUTION_UNREADY in verify_simulated_execution_readiness(data).risks
    assert PaperExecutionLoopRisk.PAPER_JOURNAL_MISSING in verify_paper_journal_readiness(data).risks


def test_compute_paper_loop_score_caps_hard_blockers():
    data = _ready_input(safety_prechecks_enabled=False, simulated_adapter_available=False)
    sections = (
        verify_signal_input_readiness(data),
        verify_decision_pipeline_readiness(data),
        verify_safety_gate_readiness(data),
        verify_simulated_execution_readiness(data),
        verify_paper_journal_readiness(data),
    )
    blockers = (
        PaperExecutionLoopRisk.SAFETY_GATE_UNVERIFIED,
        PaperExecutionLoopRisk.SIMULATED_EXECUTION_UNREADY,
    )

    score = compute_paper_loop_score(data, blockers, *sections)

    assert score.overall_score <= 45


def test_generate_recommendations_are_deduplicated_and_blocker_driven():
    result = evaluate_paper_execution_loop_readiness(
        _ready_input(
            signal_source_available=False,
            risk_engine_connected=False,
            loop_observability_connected=False,
        )
    )

    recommendations = generate_paper_loop_recommendations(result.blockers, result.state)

    assert PaperExecutionLoopRecommendation.CONNECT_SIGNAL_INPUTS in recommendations
    assert PaperExecutionLoopRecommendation.CONNECT_RISK_ENGINE in recommendations
    assert PaperExecutionLoopRecommendation.ADD_LOOP_OBSERVABILITY in recommendations
    assert len(recommendations) == len(set(recommendations))


def test_markdown_contains_paper_loop_readiness_sections():
    result = evaluate_paper_execution_loop_readiness(_ready_input())

    markdown = render_paper_execution_loop_readiness_markdown(result)

    assert "# AGIcore Paper Execution Loop Readiness" in markdown
    assert "# Paper Loop Graph" in markdown
    assert "# Paper Loop Blockers" in markdown
    assert "READY_FOR_CONTROLLED_PAPER_RUN" in markdown


def test_evaluate_paper_loop_readiness_accepts_mapping_input_and_upstream_results():
    result = evaluate_paper_execution_loop_readiness(
        {
            "paper_runtime_preparation": _upstream(state="READY_FOR_PAPER_EXECUTION_LOOP"),
            "observability_verification": _upstream(state="READY_FOR_PAPER_RUNTIME_PREP"),
            "rollback_verification": _upstream(state="READY_FOR_OBSERVABILITY_VERIFICATION"),
            "kill_switch_verification": _upstream(state="READY_FOR_ROLLBACK_VERIFICATION"),
            "runtime_isolation_review": _upstream(state="READY_FOR_PAPER_RUNTIME"),
            "sandbox_readiness_audit": _upstream(state="SANDBOX_READY"),
            "stable_review": _upstream(state="STABLE"),
            "signal_source_available": True,
            "context_signal_available": True,
            "strategy_signal_available": True,
            "signal_validation_enabled": True,
            "semi_auto_decision_ready": True,
            "context_scoring_connected": True,
            "strategy_dna_connected": True,
            "decision_output_deterministic": True,
            "safety_prechecks_enabled": True,
            "risk_engine_connected": True,
            "kill_switch_linked": True,
            "rollback_linked": True,
            "simulated_adapter_available": True,
            "simulated_order_path_verified": True,
            "real_broker_blocked": True,
            "execution_events_emitted": True,
            "paper_journal_available": True,
            "paper_trade_events_recorded": True,
            "paper_pnl_recorded": True,
            "paper_audit_export_available": True,
            "loop_observability_connected": True,
            "paper_loop_state_checkpointed": True,
            "ready_for_controlled_paper_run": True,
        }
    )

    assert result.state is PaperExecutionLoopReadinessState.READY_FOR_CONTROLLED_PAPER_RUN
    assert result.blockers == ()


@pytest.mark.parametrize(
    ("blocker", "expected"),
    [
        (
            PaperExecutionLoopRisk.KILL_SWITCH_NOT_LINKED,
            PaperExecutionLoopRecommendation.LINK_KILL_SWITCH,
        ),
        (
            PaperExecutionLoopRisk.PAPER_LOOP_STATE_CORRUPTION_RISK,
            PaperExecutionLoopRecommendation.PROTECT_PAPER_LOOP_STATE,
        ),
    ],
)
def test_recommendation_mapping_for_kill_switch_and_state_blockers(blocker, expected):
    result = evaluate_paper_execution_loop_readiness(_ready_input())

    assert expected in generate_paper_loop_recommendations((blocker,), result.state)
