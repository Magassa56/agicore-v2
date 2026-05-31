import ast
from pathlib import Path

import pytest

from agicore.trading.full_paper_session import (
    compute_full_session_score,
    detect_full_session_risks,
    evaluate_full_paper_session,
    generate_full_session_recommendations,
    render_full_paper_session_markdown,
    simulate_session_decision_cycles,
    simulate_session_journal,
    simulate_session_market_cycles,
    simulate_session_observability,
    simulate_session_order_cycles,
    simulate_session_pnl_cycles,
    simulate_session_position_cycles,
    simulate_session_risk_management,
    simulate_session_signal_cycles,
    verify_session_kill_switch,
    verify_session_rollback,
)
from agicore.trading.full_paper_session_models import (
    FullPaperSessionInput,
    FullPaperSessionRecommendation,
    FullPaperSessionRisk,
    FullPaperSessionState,
)


def _upstream(state="READY", score=96, risks=(), blockers=()):
    return {
        "state": state,
        "score": score,
        "risks": tuple(risks),
        "blockers": tuple(blockers),
        "offline_only": True,
        "score_breakdown": {"observability_score": score, "rollback_score": score, "kill_switch_score": score},
    }


def _ready_input(**overrides):
    payload = {
        "simulated_market_session": _upstream("READY_FOR_FULL_PAPER_SESSION"),
        "mock_alpaca_session": _upstream("READY_FOR_SIMULATED_MARKET_SESSION"),
        "mock_connectivity_layer": _upstream("READY_FOR_MOCK_ALPACA_SESSION"),
        "paper_trading_end_to_end": _upstream("READY_FOR_PAPER_DRY_RUN"),
        "paper_dry_run": _upstream("READY_FOR_SUPERVISED_PAPER_TRIAL"),
        "supervised_paper_trial": _upstream("READY_FOR_BROKER_PAPER_SANDBOX"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "market_cycles_available": True,
        "market_cycles_schema_valid": True,
        "market_cycles_replayable": True,
        "market_cycles_count_valid": True,
        "signal_cycles_generated": True,
        "signal_cycles_deterministic": True,
        "signal_cycles_traceable": True,
        "signal_cycles_count_aligned": True,
        "decision_cycles_generated": True,
        "decision_cycles_deterministic": True,
        "decision_cycles_safety_checked": True,
        "decision_cycles_traceable": True,
        "order_cycles_created": True,
        "order_cycles_validated": True,
        "order_cycles_status_progressed": True,
        "order_cycles_not_routed": True,
        "position_cycles_updated": True,
        "position_cycles_reconciled": True,
        "position_cycles_isolated": True,
        "position_cycles_traceable": True,
        "pnl_cycles_calculated": True,
        "pnl_cycles_reconciled": True,
        "pnl_cycles_deterministic": True,
        "pnl_cycles_traceable": True,
        "risk_limits_defined": True,
        "risk_limits_enforced": True,
        "risk_breaches_blocked": True,
        "risk_state_traceable": True,
        "journal_created": True,
        "journal_complete": True,
        "journal_replayable": True,
        "journal_traceable": True,
        "observability_events_emitted": True,
        "metrics_recorded": True,
        "traces_recorded": True,
        "alerts_recorded": True,
        "rollback_checkpoint_created": True,
        "rollback_restore_verified": True,
        "rollback_state_reconciled": True,
        "rollback_observed": True,
        "kill_switch_available": True,
        "kill_switch_halts_orders": True,
        "kill_switch_halts_session": True,
        "kill_switch_observed": True,
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
        "full_session_completed": True,
        "ready_for_paper_trading_runtime": True,
        "market_cycles_score": 96,
        "signal_cycles_score": 96,
        "decision_cycles_score": 96,
        "order_cycles_score": 96,
        "position_cycles_score": 96,
        "pnl_cycles_score": 96,
        "risk_management_score": 96,
        "journal_score": 96,
        "observability_score": 96,
        "rollback_score": 96,
        "kill_switch_score": 96,
    }
    payload.update(overrides)
    return FullPaperSessionInput(**payload)


def test_evaluate_ready_for_paper_trading_runtime():
    result = evaluate_full_paper_session(_ready_input())

    assert result.state is FullPaperSessionState.READY_FOR_PAPER_TRADING_RUNTIME
    assert result.risks == ()
    assert result.offline_only is True
    assert result.full_session_score >= 94
    assert result.session_graph.blocked_edges == ()


def test_completed_and_ready_states():
    assert evaluate_full_paper_session(_ready_input(ready_for_paper_trading_runtime=False)).state is FullPaperSessionState.FULL_SESSION_COMPLETED
    assert evaluate_full_paper_session(_ready_input(full_session_completed=False)).state is FullPaperSessionState.FULL_SESSION_READY


def test_detects_every_full_session_risk_when_all_checks_fail():
    failing = {
        name: False
        for name in FullPaperSessionInput.__dataclass_fields__
        if not name.endswith("_score") and name not in {
            "simulated_market_session", "mock_alpaca_session", "mock_connectivity_layer",
            "paper_trading_end_to_end", "paper_dry_run", "supervised_paper_trial",
            "observability_verification", "kill_switch_verification", "rollback_verification", "notes",
        }
    }
    scores = {name: 10 for name in FullPaperSessionInput.__dataclass_fields__ if name.endswith("_score")}

    result = evaluate_full_paper_session(_ready_input(**failing, **scores))

    assert set(result.risks) == set(FullPaperSessionRisk)
    assert result.state is FullPaperSessionState.NOT_READY
    assert result.offline_only is False


def test_market_signal_decision_order_cycle_risks():
    assert FullPaperSessionRisk.MARKET_CYCLE_FAILURE in simulate_session_market_cycles(_ready_input(market_cycles_available=False)).risks
    assert FullPaperSessionRisk.SIGNAL_CYCLE_FAILURE in simulate_session_signal_cycles(_ready_input(signal_cycles_generated=False)).risks
    assert FullPaperSessionRisk.DECISION_CYCLE_FAILURE in simulate_session_decision_cycles(_ready_input(decision_cycles_generated=False)).risks
    assert FullPaperSessionRisk.ORDER_CYCLE_FAILURE in simulate_session_order_cycles(_ready_input(order_cycles_created=False)).risks


def test_position_pnl_risk_journal_observability_risks():
    assert FullPaperSessionRisk.POSITION_CYCLE_FAILURE in simulate_session_position_cycles(_ready_input(position_cycles_updated=False)).risks
    assert FullPaperSessionRisk.PNL_CYCLE_FAILURE in simulate_session_pnl_cycles(_ready_input(pnl_cycles_calculated=False)).risks
    assert FullPaperSessionRisk.RISK_MANAGEMENT_FAILURE in simulate_session_risk_management(_ready_input(risk_limits_defined=False)).risks
    assert FullPaperSessionRisk.JOURNAL_INCOMPLETE in simulate_session_journal(_ready_input(journal_complete=False)).risks
    assert FullPaperSessionRisk.OBSERVABILITY_GAP in simulate_session_observability(_ready_input(metrics_recorded=False)).risks


def test_rollback_and_kill_switch_risks():
    rollback = verify_session_rollback(_ready_input(rollback_restore_verified=False, rollback_state_reconciled=False))
    kill_switch = verify_session_kill_switch(_ready_input(kill_switch_available=False, kill_switch_halts_orders=False))

    assert FullPaperSessionRisk.ROLLBACK_FAILURE in rollback.risks
    assert FullPaperSessionRisk.SESSION_STATE_DRIFT in rollback.risks
    assert FullPaperSessionRisk.KILL_SWITCH_FAILURE in kill_switch.risks
    assert FullPaperSessionRisk.SAFETY_BOUNDARY_BYPASS in kill_switch.risks


def test_three_soft_risks_require_review():
    result = evaluate_full_paper_session(
        _ready_input(
            signal_cycles_generated=False,
            pnl_cycles_calculated=False,
            journal_complete=False,
            signal_cycles_traceable=True,
            pnl_cycles_traceable=True,
            journal_replayable=True,
            journal_traceable=True,
        )
    )

    assert result.state is FullPaperSessionState.REVIEW_REQUIRED
    assert FullPaperSessionRisk.SIGNAL_CYCLE_FAILURE in result.risks
    assert FullPaperSessionRisk.PNL_CYCLE_FAILURE in result.risks
    assert FullPaperSessionRisk.JOURNAL_INCOMPLETE in result.risks


def test_single_soft_risk_is_partially_ready():
    result = evaluate_full_paper_session(_ready_input(signal_cycles_generated=False, signal_cycles_score=86))

    assert result.state is FullPaperSessionState.PARTIALLY_READY
    assert result.risks == (FullPaperSessionRisk.SIGNAL_CYCLE_FAILURE,)


def test_hard_risk_caps_score_and_not_ready():
    data = _ready_input(no_http_transport=False)
    risks = detect_full_session_risks(data)
    score = compute_full_session_score(data, risks)
    result = evaluate_full_paper_session(data)

    assert FullPaperSessionRisk.SAFETY_BOUNDARY_BYPASS in risks
    assert score.overall_score <= 40
    assert result.state is FullPaperSessionState.NOT_READY


def test_upstream_network_leak_keeps_session_offline_boundary_closed():
    result = evaluate_full_paper_session(_ready_input(simulated_market_session=_upstream(risks=("NETWORK_LEAK",))))

    assert result.state is FullPaperSessionState.NOT_READY
    assert result.offline_only is False
    assert FullPaperSessionRisk.SAFETY_BOUNDARY_BYPASS in result.risks


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_full_session_recommendations(
        (
            FullPaperSessionRisk.ORDER_CYCLE_FAILURE,
            FullPaperSessionRisk.ORDER_CYCLE_FAILURE,
            FullPaperSessionRisk.OBSERVABILITY_GAP,
            FullPaperSessionRisk.KILL_SWITCH_FAILURE,
        ),
        FullPaperSessionState.PARTIALLY_READY,
    )

    assert recommendations.count(FullPaperSessionRecommendation.REPAIR_ORDER_CYCLES) == 1
    assert FullPaperSessionRecommendation.RESTORE_FULL_SESSION_OBSERVABILITY in recommendations
    assert FullPaperSessionRecommendation.REPAIR_SESSION_KILL_SWITCH in recommendations
    assert FullPaperSessionRecommendation.RUN_FULL_PAPER_SESSION_SUITE in recommendations


def test_ready_state_adds_runtime_approval_recommendation():
    result = evaluate_full_paper_session(_ready_input())

    assert FullPaperSessionRecommendation.APPROVE_PAPER_TRADING_RUNTIME_AFTER_MANUAL_REVIEW in result.recommendations


def test_markdown_rendering_contains_checks_graph_risks_and_recommendations():
    result = evaluate_full_paper_session(_ready_input(order_cycles_created=False))
    markdown = render_full_paper_session_markdown(result)

    assert "# AGIcore Full Paper Session" in markdown
    assert "# Score Breakdown" in markdown
    assert "# Full Paper Session Checks" in markdown
    assert "# Full Paper Session Graph" in markdown
    assert "ORDER_CYCLE_FAILURE" in markdown
    assert "REPAIR_ORDER_CYCLES" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_full_paper_session(_ready_input().__dict__)

    assert result.state is FullPaperSessionState.READY_FOR_PAPER_TRADING_RUNTIME
    assert result.full_session_score >= 94


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (FullPaperSessionRisk.MARKET_CYCLE_FAILURE, FullPaperSessionRecommendation.REPAIR_MARKET_CYCLES),
        (FullPaperSessionRisk.ROLLBACK_FAILURE, FullPaperSessionRecommendation.REPAIR_SESSION_ROLLBACK),
        (FullPaperSessionRisk.SESSION_STATE_DRIFT, FullPaperSessionRecommendation.RECONCILE_FULL_SESSION_STATE),
    ],
)
def test_recommendation_mapping_for_full_session_risks(risk, recommendation):
    assert recommendation in generate_full_session_recommendations((risk,), FullPaperSessionState.PARTIALLY_READY)


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "full_paper_session.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
