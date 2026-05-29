from types import SimpleNamespace

import pytest

from agicore.trading.paper_runtime_preparation import (
    compute_paper_runtime_score,
    detect_paper_runtime_blockers,
    evaluate_paper_runtime_preparation,
    generate_paper_runtime_recommendations,
    render_paper_runtime_preparation_markdown,
    verify_paper_risk_readiness,
    verify_session_runtime_readiness,
    verify_simulated_order_readiness,
    verify_simulated_position_readiness,
    verify_virtual_portfolio_readiness,
)
from agicore.trading.paper_runtime_preparation_models import (
    PaperRuntimePreparationInput,
    PaperRuntimePreparationState,
    PaperRuntimeRecommendation,
    PaperRuntimeRisk,
)


def _upstream(**overrides):
    data = {
        "state": "READY",
        "observability_score": 96,
        "rollback_score": 96,
        "kill_switch_score": 96,
        "isolation_score": 96,
        "sandbox_score": 96,
        "risks": (),
        "blockers": (),
        "offline_only": True,
        "score_breakdown": SimpleNamespace(
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
        "observability_verification": _upstream(state="READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream(state="READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream(state="READY_FOR_ROLLBACK_VERIFICATION"),
        "runtime_isolation_review": _upstream(state="READY_FOR_PAPER_RUNTIME"),
        "sandbox_readiness_audit": _upstream(state="SANDBOX_READY"),
        "stable_review": _upstream(state="STABLE"),
        "virtual_portfolio_available": True,
        "virtual_cash_configured": True,
        "virtual_equity_consistent": True,
        "portfolio_reset_supported": True,
        "simulated_order_engine_available": True,
        "market_order_simulation_supported": True,
        "order_rejection_simulation_supported": True,
        "broker_connection_absent": True,
        "simulated_position_tracking_available": True,
        "position_average_price_supported": True,
        "realized_pnl_supported": True,
        "position_state_consistent": True,
        "paper_risk_engine_available": True,
        "max_order_limits_configured": True,
        "risk_gate_enforced": True,
        "kill_switch_connected": True,
        "session_runtime_configured": True,
        "session_prechecks_defined": True,
        "session_event_stream_available": True,
        "paper_runtime_isolated": True,
        "paper_observability_available": True,
        "paper_state_checkpoint_supported": True,
        "ready_for_paper_execution_loop": True,
        "virtual_portfolio_score": 96,
        "simulated_order_score": 96,
        "simulated_position_score": 96,
        "paper_risk_score": 96,
        "session_runtime_score": 96,
        "paper_observability_score": 96,
    }
    data.update(overrides)
    return PaperRuntimePreparationInput(**data)


def test_evaluate_paper_runtime_ready_for_execution_loop_when_all_components_are_ready():
    result = evaluate_paper_runtime_preparation(_ready_input())

    assert result.state is PaperRuntimePreparationState.READY_FOR_PAPER_EXECUTION_LOOP
    assert result.blockers == ()
    assert result.paper_runtime_score >= 94
    assert result.offline_only is True
    assert result.paper_runtime_graph.ready_edges == (
        ("paper_runtime", "virtual_portfolio"),
        ("paper_runtime", "simulated_order_engine"),
        ("simulated_order_engine", "simulated_positions"),
        ("paper_risk_gate", "simulated_order_engine"),
        ("session_runtime", "paper_execution_loop"),
    )
    assert result.virtual_portfolio_review.passed is True
    assert result.simulated_order_review.passed is True
    assert result.simulated_position_review.passed is True
    assert result.paper_risk_review.passed is True
    assert result.session_runtime_review.passed is True


def test_detect_paper_runtime_blockers_reports_all_failures():
    data = _ready_input(
        virtual_portfolio_available=False,
        virtual_cash_configured=False,
        virtual_equity_consistent=False,
        portfolio_reset_supported=False,
        simulated_order_engine_available=False,
        market_order_simulation_supported=False,
        order_rejection_simulation_supported=False,
        broker_connection_absent=False,
        simulated_position_tracking_available=False,
        position_average_price_supported=False,
        realized_pnl_supported=False,
        position_state_consistent=False,
        paper_risk_engine_available=False,
        max_order_limits_configured=False,
        risk_gate_enforced=False,
        kill_switch_connected=False,
        session_runtime_configured=False,
        session_prechecks_defined=False,
        session_event_stream_available=False,
        paper_runtime_isolated=False,
        paper_observability_available=False,
        paper_state_checkpoint_supported=False,
        virtual_portfolio_score=10,
        simulated_order_score=10,
        simulated_position_score=10,
        paper_risk_score=10,
        session_runtime_score=10,
        paper_observability_score=10,
    )

    blockers = detect_paper_runtime_blockers(data)

    assert set(blockers) == set(PaperRuntimeRisk)


def test_missing_simulated_order_engine_forces_not_ready():
    result = evaluate_paper_runtime_preparation(
        _ready_input(simulated_order_engine_available=False)
    )

    assert result.state is PaperRuntimePreparationState.NOT_READY
    assert PaperRuntimeRisk.SIMULATED_ORDER_ENGINE_MISSING in result.blockers
    assert result.paper_runtime_graph.blocked_edges == (
        ("paper_runtime", "simulated_order_engine"),
    )


def test_execution_leak_forces_not_ready_and_offline_false():
    result = evaluate_paper_runtime_preparation(
        _ready_input(broker_connection_absent=False)
    )

    assert result.state is PaperRuntimePreparationState.NOT_READY
    assert result.offline_only is False
    assert PaperRuntimeRisk.PAPER_EXECUTION_LEAK_RISK in result.blockers


def test_three_soft_blockers_require_review_without_hard_failure():
    result = evaluate_paper_runtime_preparation(
        _ready_input(
            realized_pnl_supported=False,
            paper_state_checkpoint_supported=False,
            paper_observability_available=False,
        )
    )

    assert result.state is PaperRuntimePreparationState.REVIEW_REQUIRED
    assert {
        PaperRuntimeRisk.PAPER_PNL_UNVERIFIED,
        PaperRuntimeRisk.PAPER_STATE_CORRUPTION_RISK,
        PaperRuntimeRisk.PAPER_OBSERVABILITY_GAP,
    }.issubset(result.blockers)


def test_single_soft_blocker_yields_partially_ready():
    result = evaluate_paper_runtime_preparation(_ready_input(realized_pnl_supported=False))

    assert result.state is PaperRuntimePreparationState.PARTIALLY_READY
    assert result.blockers == (PaperRuntimeRisk.PAPER_PNL_UNVERIFIED,)


def test_paper_runtime_ready_when_clean_but_execution_loop_gate_not_ready():
    result = evaluate_paper_runtime_preparation(
        _ready_input(
            ready_for_paper_execution_loop=False,
            virtual_portfolio_score=89,
            simulated_order_score=89,
            simulated_position_score=89,
            paper_risk_score=89,
            session_runtime_score=89,
            paper_observability_score=89,
        )
    )

    assert result.state is PaperRuntimePreparationState.PAPER_RUNTIME_READY
    assert result.blockers == ()
    assert result.paper_runtime_score >= 88


def test_review_sections_expose_specific_paper_runtime_blockers():
    data = _ready_input(
        virtual_portfolio_available=False,
        simulated_order_engine_available=False,
        simulated_position_tracking_available=False,
        paper_risk_engine_available=False,
        session_runtime_configured=False,
    )

    assert PaperRuntimeRisk.VIRTUAL_PORTFOLIO_MISSING in verify_virtual_portfolio_readiness(data).risks
    assert PaperRuntimeRisk.SIMULATED_ORDER_ENGINE_MISSING in verify_simulated_order_readiness(data).risks
    assert PaperRuntimeRisk.SIMULATED_POSITION_TRACKING_MISSING in verify_simulated_position_readiness(data).risks
    assert PaperRuntimeRisk.PAPER_RISK_ENGINE_MISSING in verify_paper_risk_readiness(data).risks
    assert PaperRuntimeRisk.SESSION_RUNTIME_UNVERIFIED in verify_session_runtime_readiness(data).risks


def test_compute_paper_runtime_score_caps_hard_blockers():
    data = _ready_input(simulated_order_engine_available=False, broker_connection_absent=False)
    sections = (
        verify_virtual_portfolio_readiness(data),
        verify_simulated_order_readiness(data),
        verify_simulated_position_readiness(data),
        verify_paper_risk_readiness(data),
        verify_session_runtime_readiness(data),
    )
    blockers = (
        PaperRuntimeRisk.SIMULATED_ORDER_ENGINE_MISSING,
        PaperRuntimeRisk.PAPER_EXECUTION_LEAK_RISK,
    )

    score = compute_paper_runtime_score(data, blockers, *sections)

    assert score.overall_score <= 40


def test_generate_recommendations_are_deduplicated_and_blocker_driven():
    result = evaluate_paper_runtime_preparation(
        _ready_input(
            simulated_order_engine_available=False,
            paper_risk_engine_available=False,
            paper_observability_available=False,
        )
    )

    recommendations = generate_paper_runtime_recommendations(result.blockers, result.state)

    assert PaperRuntimeRecommendation.ENABLE_SIMULATED_ORDER_ENGINE in recommendations
    assert PaperRuntimeRecommendation.ENABLE_PAPER_RISK_ENGINE in recommendations
    assert PaperRuntimeRecommendation.ADD_PAPER_OBSERVABILITY in recommendations
    assert len(recommendations) == len(set(recommendations))


def test_markdown_contains_paper_runtime_preparation_sections():
    result = evaluate_paper_runtime_preparation(_ready_input())

    markdown = render_paper_runtime_preparation_markdown(result)

    assert "# AGIcore Paper Runtime Preparation" in markdown
    assert "# Paper Runtime Graph" in markdown
    assert "# Paper Runtime Blockers" in markdown
    assert "READY_FOR_PAPER_EXECUTION_LOOP" in markdown


def test_evaluate_paper_runtime_preparation_accepts_mapping_input_and_upstream_results():
    result = evaluate_paper_runtime_preparation(
        {
            "observability_verification": _upstream(state="READY_FOR_PAPER_RUNTIME_PREP"),
            "rollback_verification": _upstream(state="READY_FOR_OBSERVABILITY_VERIFICATION"),
            "kill_switch_verification": _upstream(state="READY_FOR_ROLLBACK_VERIFICATION"),
            "runtime_isolation_review": _upstream(state="READY_FOR_PAPER_RUNTIME"),
            "sandbox_readiness_audit": _upstream(state="SANDBOX_READY"),
            "stable_review": _upstream(state="STABLE"),
            "virtual_portfolio_available": True,
            "virtual_cash_configured": True,
            "virtual_equity_consistent": True,
            "portfolio_reset_supported": True,
            "simulated_order_engine_available": True,
            "market_order_simulation_supported": True,
            "order_rejection_simulation_supported": True,
            "broker_connection_absent": True,
            "simulated_position_tracking_available": True,
            "position_average_price_supported": True,
            "realized_pnl_supported": True,
            "position_state_consistent": True,
            "paper_risk_engine_available": True,
            "max_order_limits_configured": True,
            "risk_gate_enforced": True,
            "kill_switch_connected": True,
            "session_runtime_configured": True,
            "session_prechecks_defined": True,
            "session_event_stream_available": True,
            "paper_runtime_isolated": True,
            "paper_observability_available": True,
            "paper_state_checkpoint_supported": True,
            "ready_for_paper_execution_loop": True,
        }
    )

    assert result.state is PaperRuntimePreparationState.READY_FOR_PAPER_EXECUTION_LOOP
    assert result.blockers == ()


@pytest.mark.parametrize(
    ("blocker", "expected"),
    [
        (
            PaperRuntimeRisk.PAPER_RUNTIME_NOT_ISOLATED,
            PaperRuntimeRecommendation.ISOLATE_PAPER_RUNTIME,
        ),
        (
            PaperRuntimeRisk.PAPER_STATE_CORRUPTION_RISK,
            PaperRuntimeRecommendation.PROTECT_PAPER_STATE,
        ),
    ],
)
def test_recommendation_mapping_for_isolation_and_state_blockers(blocker, expected):
    result = evaluate_paper_runtime_preparation(_ready_input())

    assert expected in generate_paper_runtime_recommendations((blocker,), result.state)
