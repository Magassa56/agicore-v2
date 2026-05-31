import ast
from pathlib import Path

from agicore.trading.paper_trading_runtime import (
    check_human_supervision_hook,
    check_runtime_kill_switch_hook,
    check_runtime_rollback_hook,
    emit_runtime_observability_events,
    execute_decision_cycle,
    execute_market_cycle,
    execute_paper_order_simulation,
    execute_safety_gate,
    execute_signal_cycle,
    initialize_paper_runtime_session,
    render_paper_trading_runtime_markdown,
    run_paper_trading_runtime,
    stop_paper_trading_runtime,
    update_paper_position_and_pnl,
    write_runtime_journal,
)
from agicore.trading.paper_trading_runtime_models import (
    PaperTradingRuntimeInput,
    PaperTradingRuntimeRecommendation,
    PaperTradingRuntimeRisk,
    PaperTradingRuntimeState,
)


def _upstream(state="READY", risks=()):
    return {"state": state, "risks": tuple(risks), "offline_only": True}


def _ready_input(**overrides):
    payload = {
        "paper_trading_runtime_design": _upstream("READY_FOR_RUNTIME_IMPLEMENTATION"),
        "paper_runtime_decision_review": _upstream("READY_FOR_PAPER_TRADING_RUNTIME"),
        "paper_runtime_pre_review": _upstream("READY_FOR_PAPER_TRADING_RUNTIME"),
        "full_paper_session": _upstream("READY_FOR_PAPER_TRADING_RUNTIME"),
        "simulated_market_session": _upstream("READY_FOR_FULL_PAPER_SESSION"),
        "mock_alpaca_session": _upstream("READY_FOR_SIMULATED_MARKET_SESSION"),
        "mock_connectivity_layer": _upstream("READY_FOR_MOCK_ALPACA_SESSION"),
        "alpaca_paper_connectivity_readiness": _upstream("READY_FOR_MOCK_CONNECTIVITY"),
        "broker_paper_sandbox": _upstream("READY_FOR_ALPACA_PAPER_CONNECTIVITY"),
        "paper_trading_end_to_end": _upstream("READY_FOR_PAPER_DRY_RUN"),
        "paper_dry_run": _upstream("READY_FOR_SUPERVISED_PAPER_TRIAL"),
        "supervised_paper_trial": _upstream("READY_FOR_BROKER_PAPER_SANDBOX"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "session_id": "rt-1",
        "symbol": "ES.PAPER",
        "market_price": 101.0,
        "previous_price": 100.0,
        "quantity": 2.0,
        "approved_by_human": True,
        "operator_confirmed": True,
        "session_authorized": True,
        "safety_gate_enabled": True,
        "risk_limits_enforced": True,
        "paper_order_not_routed": True,
        "journal_enabled": True,
        "observability_enabled": True,
        "rollback_hook_available": True,
        "kill_switch_hook_available": True,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "no_real_broker": True,
        "no_api_key_read": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_api": True,
        "no_real_order": True,
    }
    payload.update(overrides)
    return PaperTradingRuntimeInput(**payload)


def test_run_paper_trading_runtime_completes_offline_session():
    result = run_paper_trading_runtime(_ready_input())

    assert result.state is PaperTradingRuntimeState.COMPLETED
    assert result.risks == ()
    assert result.offline_only is True
    assert result.order is not None
    assert result.order.routed is False
    assert result.position is not None
    assert result.report is not None
    assert result.report.order_count == 1
    assert result.runtime_score == 100


def test_initialize_session_rejects_scope_drift():
    step = initialize_paper_runtime_session(_ready_input(no_http_transport=False))

    assert step.passed is False
    assert PaperTradingRuntimeRisk.RUNTIME_INITIALIZATION_FAILURE in step.risks


def test_market_signal_decision_cycles_are_deterministic():
    data = _ready_input(market_price=99.0, previous_price=100.0)
    market_step, market = execute_market_cycle(data)
    signal_step, signal = execute_signal_cycle(data, market)
    decision_step, decision = execute_decision_cycle(data, signal)

    assert market_step.passed is True
    assert signal_step.passed is True
    assert decision_step.passed is True
    assert signal is not None and signal.action == "SELL"
    assert decision is not None and decision.action == "SELL"


def test_safety_gate_blocks_when_risk_limits_are_missing():
    data = _ready_input(risk_limits_enforced=False)
    _, signal = execute_signal_cycle(data)
    _, decision = execute_decision_cycle(data, signal)
    safety = execute_safety_gate(data, decision)

    assert safety.passed is False
    assert PaperTradingRuntimeRisk.SAFETY_GATE_FAILURE in safety.risks


def test_paper_order_simulation_never_routes_to_broker():
    data = _ready_input()
    _, decision = execute_decision_cycle(data)
    safety = execute_safety_gate(data, decision)
    step, order = execute_paper_order_simulation(data, decision, safety)

    assert step.passed is True
    assert order is not None
    assert order.status == "FILLED"
    assert order.routed is False


def test_position_pnl_update_changes_cash_and_position():
    data = _ready_input(quantity=3.0)
    _, decision = execute_decision_cycle(data)
    safety = execute_safety_gate(data, decision)
    _, order = execute_paper_order_simulation(data, decision, safety)
    step, position = update_paper_position_and_pnl(data, order)

    assert step.passed is True
    assert position is not None
    assert position.quantity == 3.0
    assert position.cash == 9697.0


def test_journal_and_observability_are_emitted():
    result = run_paper_trading_runtime(_ready_input())

    assert result.journal.passed is True
    assert len(result.journal_entries) == 3
    assert result.observability.passed is True
    assert len(result.observability_events) == 5


def test_journal_failure_fails_safe():
    result = run_paper_trading_runtime(_ready_input(force_journal_failure=True))

    assert result.state is PaperTradingRuntimeState.FAILED_SAFE
    assert PaperTradingRuntimeRisk.JOURNAL_WRITE_FAILURE in result.risks
    assert PaperTradingRuntimeRecommendation.REPAIR_RUNTIME_JOURNAL in result.recommendations


def test_observability_failure_fails_safe():
    result = run_paper_trading_runtime(_ready_input(force_observability_failure=True))

    assert result.state is PaperTradingRuntimeState.FAILED_SAFE
    assert PaperTradingRuntimeRisk.OBSERVABILITY_EMIT_FAILURE in result.risks


def test_rollback_hook_can_stop_runtime():
    result = run_paper_trading_runtime(_ready_input(rollback_requested=True))

    assert result.state is PaperTradingRuntimeState.STOPPED_BY_ROLLBACK
    assert result.stop.state is PaperTradingRuntimeState.STOPPED_BY_ROLLBACK


def test_rollback_hook_failure_is_detected():
    step = check_runtime_rollback_hook(_ready_input(rollback_hook_available=False, rollback_requested=True))

    assert step.passed is False
    assert PaperTradingRuntimeRisk.ROLLBACK_HOOK_FAILURE in step.risks


def test_kill_switch_hook_can_stop_runtime():
    result = run_paper_trading_runtime(_ready_input(kill_switch_triggered=True))

    assert result.state is PaperTradingRuntimeState.STOPPED_BY_KILL_SWITCH
    assert result.stop.state is PaperTradingRuntimeState.STOPPED_BY_KILL_SWITCH


def test_kill_switch_hook_failure_is_detected():
    step = check_runtime_kill_switch_hook(_ready_input(kill_switch_hook_available=False, kill_switch_triggered=True))

    assert step.passed is False
    assert PaperTradingRuntimeRisk.KILL_SWITCH_HOOK_FAILURE in step.risks


def test_human_supervision_pause_halts_session_without_live_execution():
    result = run_paper_trading_runtime(_ready_input(supervision_pause_requested=True))

    assert result.state is PaperTradingRuntimeState.PAUSED_BY_SUPERVISION
    assert PaperTradingRuntimeRisk.HUMAN_SUPERVISION_FAILURE in result.risks


def test_missing_human_approval_is_a_supervision_failure():
    step = check_human_supervision_hook(_ready_input(approved_by_human=False))

    assert step.passed is False
    assert PaperTradingRuntimeRisk.HUMAN_SUPERVISION_FAILURE in step.risks


def test_force_failures_map_to_runtime_risks():
    cases = [
        ("force_market_failure", PaperTradingRuntimeRisk.MARKET_CYCLE_FAILURE),
        ("force_signal_failure", PaperTradingRuntimeRisk.SIGNAL_CYCLE_FAILURE),
        ("force_decision_failure", PaperTradingRuntimeRisk.DECISION_CYCLE_FAILURE),
        ("force_order_failure", PaperTradingRuntimeRisk.PAPER_ORDER_SIMULATION_FAILURE),
        ("force_position_failure", PaperTradingRuntimeRisk.POSITION_PNL_UPDATE_FAILURE),
    ]
    for field, risk in cases:
        result = run_paper_trading_runtime(_ready_input(**{field: True}))
        assert result.state is PaperTradingRuntimeState.FAILED_SAFE
        assert risk in result.risks


def test_helper_functions_support_direct_journal_and_observability_calls():
    data = _ready_input()
    _, decision = execute_decision_cycle(data)
    safety = execute_safety_gate(data, decision)
    _, order = execute_paper_order_simulation(data, decision, safety)
    _, position = update_paper_position_and_pnl(data, order)
    journal_step, entries = write_runtime_journal(data, order, position)
    observability_step, events = emit_runtime_observability_events(data, entries)

    assert journal_step.passed is True
    assert observability_step.passed is True
    assert entries
    assert events


def test_stop_runtime_accepts_safe_terminal_states():
    step = stop_paper_trading_runtime(_ready_input(), PaperTradingRuntimeState.COMPLETED)

    assert step.passed is True
    assert "runtime_stopped=True" in step.events


def test_mapping_inputs_are_supported():
    result = run_paper_trading_runtime(_ready_input().__dict__)

    assert result.state is PaperTradingRuntimeState.COMPLETED


def test_markdown_contains_report_risks_and_artifacts():
    result = run_paper_trading_runtime(_ready_input(force_order_failure=True))
    markdown = render_paper_trading_runtime_markdown(result)

    assert "# AGIcore Paper Trading Runtime" in markdown
    assert "PAPER_ORDER_SIMULATION_FAILURE" in markdown
    assert "# Runtime Artifacts" in markdown
    assert "REPAIR_PAPER_ORDER_SIMULATION" in markdown


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "paper_trading_runtime.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
