import ast
from pathlib import Path

import pytest

from agicore.trading.paper_trading_runtime_design import (
    compute_runtime_design_score,
    define_runtime_adapter_contracts,
    define_runtime_architecture,
    define_runtime_human_supervision_hooks,
    define_runtime_inputs_outputs,
    define_runtime_kill_switch_hooks,
    define_runtime_observability_hooks,
    define_runtime_rollback_hooks,
    define_runtime_safety_boundaries,
    define_runtime_session_cycle,
    define_runtime_state_machine,
    detect_runtime_design_risks,
    evaluate_paper_trading_runtime_design,
    generate_runtime_design_recommendations,
    render_paper_trading_runtime_design_markdown,
)
from agicore.trading.paper_trading_runtime_design_models import (
    PaperTradingRuntimeDesignDecision,
    PaperTradingRuntimeDesignInput,
    PaperTradingRuntimeDesignRecommendation,
    PaperTradingRuntimeDesignRisk,
    PaperTradingRuntimeDesignState,
)


def _upstream(state="READY", risks=(), blockers=()):
    return {"state": state, "risks": tuple(risks), "blockers": tuple(blockers), "offline_only": True}


def _ready_input(**overrides):
    payload = {
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
        "architecture_components": ("entrypoint", "state_machine", "session_cycle", "adapter", "safety", "observability", "rollback", "kill_switch", "human_supervision"),
        "runtime_states": ("INIT", "AWAIT_HUMAN_APPROVAL", "RUNNING", "PAUSED", "ROLLBACK", "KILL_SWITCHED", "COMPLETED"),
        "session_cycle_steps": ("market_data", "signal", "decision", "safety_gate", "paper_order", "position", "pnl", "journal", "observability"),
        "input_contracts": ("market_data", "signals", "operator_approval", "risk_limits"),
        "output_contracts": ("paper_orders", "positions", "pnl", "journal", "events"),
        "safety_boundaries": ("offline_only", "paper_only", "no_real_order", "risk_limits", "safety_gate"),
        "observability_hooks": ("logs", "metrics", "traces", "alerts", "audit_events"),
        "rollback_hooks": ("checkpoint", "restore", "state_reconcile", "rollback_event"),
        "kill_switch_hooks": ("halt_orders", "halt_session", "lock_state", "emit_alert"),
        "human_supervision_hooks": ("human_approval", "operator_confirmation", "override", "session_authorization"),
        "adapter_contracts": ("connect", "disconnect", "account", "positions", "submit_order", "order_status", "reject_order"),
        "runtime_entrypoint": "evaluate_paper_trading_runtime",
        "runtime_scope_locked": True,
        "no_runtime_implementation_created": True,
        "design_review_approved": True,
        "ready_for_runtime_implementation": True,
        "offline_mode_enforced": True,
        "no_real_broker": True,
        "no_api_key_read": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_api": True,
        "no_real_order": True,
        "architecture_score": 96,
        "state_machine_score": 96,
        "session_cycle_score": 96,
        "inputs_outputs_score": 96,
        "safety_boundaries_score": 96,
        "observability_hooks_score": 96,
        "rollback_hooks_score": 96,
        "kill_switch_hooks_score": 96,
        "human_supervision_hooks_score": 96,
        "adapter_contracts_score": 96,
    }
    payload.update(overrides)
    return PaperTradingRuntimeDesignInput(**payload)


def test_evaluate_ready_for_runtime_implementation():
    result = evaluate_paper_trading_runtime_design(_ready_input())

    assert result.state is PaperTradingRuntimeDesignState.READY_FOR_RUNTIME_IMPLEMENTATION
    assert result.decision is PaperTradingRuntimeDesignDecision.APPROVE_RUNTIME_IMPLEMENTATION
    assert result.risks == ()
    assert result.offline_only is True
    assert result.runtime_design_score >= 94


def test_design_ready_when_implementation_gate_is_not_set():
    result = evaluate_paper_trading_runtime_design(_ready_input(ready_for_runtime_implementation=False))

    assert result.state is PaperTradingRuntimeDesignState.RUNTIME_DESIGN_READY
    assert result.decision is PaperTradingRuntimeDesignDecision.APPROVE_RUNTIME_DESIGN


def test_each_design_section_detects_its_primary_risk():
    assert PaperTradingRuntimeDesignRisk.ARCHITECTURE_UNCLEAR in define_runtime_architecture(_ready_input(architecture_components=())).risks
    assert PaperTradingRuntimeDesignRisk.STATE_MACHINE_INCOMPLETE in define_runtime_state_machine(_ready_input(runtime_states=())).risks
    assert PaperTradingRuntimeDesignRisk.SESSION_CYCLE_AMBIGUOUS in define_runtime_session_cycle(_ready_input(session_cycle_steps=())).risks
    assert PaperTradingRuntimeDesignRisk.INPUT_OUTPUT_CONTRACT_GAP in define_runtime_inputs_outputs(_ready_input(input_contracts=())).risks
    assert PaperTradingRuntimeDesignRisk.SAFETY_BOUNDARY_GAP in define_runtime_safety_boundaries(_ready_input(safety_boundaries=())).risks
    assert PaperTradingRuntimeDesignRisk.OBSERVABILITY_HOOK_MISSING in define_runtime_observability_hooks(_ready_input(observability_hooks=())).risks
    assert PaperTradingRuntimeDesignRisk.ROLLBACK_HOOK_MISSING in define_runtime_rollback_hooks(_ready_input(rollback_hooks=())).risks
    assert PaperTradingRuntimeDesignRisk.KILL_SWITCH_HOOK_MISSING in define_runtime_kill_switch_hooks(_ready_input(kill_switch_hooks=())).risks
    assert PaperTradingRuntimeDesignRisk.HUMAN_SUPERVISION_HOOK_MISSING in define_runtime_human_supervision_hooks(_ready_input(human_supervision_hooks=())).risks
    assert PaperTradingRuntimeDesignRisk.ADAPTER_CONTRACT_INCOMPLETE in define_runtime_adapter_contracts(_ready_input(adapter_contracts=())).risks


def test_detects_all_runtime_design_risks():
    result = evaluate_paper_trading_runtime_design(
        _ready_input(
            architecture_components=(),
            runtime_states=(),
            session_cycle_steps=(),
            input_contracts=(),
            output_contracts=(),
            safety_boundaries=(),
            observability_hooks=(),
            rollback_hooks=(),
            kill_switch_hooks=(),
            human_supervision_hooks=(),
            adapter_contracts=(),
            runtime_scope_locked=False,
            no_runtime_implementation_created=False,
        )
    )

    assert set(result.risks) == set(PaperTradingRuntimeDesignRisk)
    assert result.state is PaperTradingRuntimeDesignState.NOT_READY
    assert result.decision is PaperTradingRuntimeDesignDecision.BLOCK_RUNTIME_IMPLEMENTATION


def test_single_soft_risk_is_partially_designed():
    result = evaluate_paper_trading_runtime_design(
        _ready_input(session_cycle_steps=("market_data", "signal", "decision", "safety_gate", "paper_order", "position", "pnl", "journal"), session_cycle_score=88)
    )

    assert result.state is PaperTradingRuntimeDesignState.PARTIALLY_DESIGNED
    assert result.decision is PaperTradingRuntimeDesignDecision.REQUIRE_DESIGN_CLEANUP
    assert result.risks == (PaperTradingRuntimeDesignRisk.SESSION_CYCLE_AMBIGUOUS,)


def test_scope_drift_caps_score_and_blocks_implementation():
    data = _ready_input(no_http_transport=False)
    risks = detect_runtime_design_risks(data)
    score = compute_runtime_design_score(data, risks)
    result = evaluate_paper_trading_runtime_design(data)

    assert PaperTradingRuntimeDesignRisk.RUNTIME_SCOPE_DRIFT in risks
    assert score.overall_score <= 40
    assert result.decision is PaperTradingRuntimeDesignDecision.BLOCK_RUNTIME_IMPLEMENTATION


def test_premature_implementation_risk_blocks_runtime():
    result = evaluate_paper_trading_runtime_design(_ready_input(no_runtime_implementation_created=False))

    assert PaperTradingRuntimeDesignRisk.PREMATURE_IMPLEMENTATION_RISK in result.risks
    assert result.decision is PaperTradingRuntimeDesignDecision.BLOCK_RUNTIME_IMPLEMENTATION


def test_upstream_network_leak_closes_offline_boundary():
    result = evaluate_paper_trading_runtime_design(_ready_input(paper_runtime_decision_review=_upstream(risks=("NETWORK_LEAK",))))

    assert result.offline_only is False
    assert PaperTradingRuntimeDesignRisk.RUNTIME_SCOPE_DRIFT in result.risks


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_runtime_design_recommendations(
        (
            PaperTradingRuntimeDesignRisk.STATE_MACHINE_INCOMPLETE,
            PaperTradingRuntimeDesignRisk.STATE_MACHINE_INCOMPLETE,
            PaperTradingRuntimeDesignRisk.KILL_SWITCH_HOOK_MISSING,
            PaperTradingRuntimeDesignRisk.RUNTIME_SCOPE_DRIFT,
        ),
        PaperTradingRuntimeDesignDecision.REQUIRE_DESIGN_CLEANUP,
    )

    assert recommendations.count(PaperTradingRuntimeDesignRecommendation.COMPLETE_RUNTIME_STATE_MACHINE) == 1
    assert PaperTradingRuntimeDesignRecommendation.ADD_KILL_SWITCH_HOOKS in recommendations
    assert PaperTradingRuntimeDesignRecommendation.FREEZE_RUNTIME_SCOPE in recommendations
    assert PaperTradingRuntimeDesignRecommendation.RUN_RUNTIME_DESIGN_REVIEW_SUITE in recommendations


def test_approval_recommendations_follow_decision():
    design = generate_runtime_design_recommendations((), PaperTradingRuntimeDesignDecision.APPROVE_RUNTIME_DESIGN)
    implementation = generate_runtime_design_recommendations((), PaperTradingRuntimeDesignDecision.APPROVE_RUNTIME_IMPLEMENTATION)

    assert PaperTradingRuntimeDesignRecommendation.APPROVE_RUNTIME_DESIGN_AFTER_MANUAL_REVIEW in design
    assert PaperTradingRuntimeDesignRecommendation.APPROVE_IMPLEMENTATION_AFTER_MANUAL_REVIEW in implementation


def test_markdown_rendering_contains_design_sections_risks_and_recommendations():
    result = evaluate_paper_trading_runtime_design(_ready_input(kill_switch_hooks=()))
    markdown = render_paper_trading_runtime_design_markdown(result)

    assert "# AGIcore Paper Trading Runtime Design" in markdown
    assert "Decision: REQUIRE_DESIGN_CLEANUP" in markdown
    assert "# Runtime Design Sections" in markdown
    assert "KILL_SWITCH_HOOK_MISSING" in markdown
    assert "ADD_KILL_SWITCH_HOOKS" in markdown


def test_mapping_inputs_are_supported():
    result = evaluate_paper_trading_runtime_design(_ready_input().__dict__)

    assert result.state is PaperTradingRuntimeDesignState.READY_FOR_RUNTIME_IMPLEMENTATION
    assert result.decision is PaperTradingRuntimeDesignDecision.APPROVE_RUNTIME_IMPLEMENTATION


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (PaperTradingRuntimeDesignRisk.ARCHITECTURE_UNCLEAR, PaperTradingRuntimeDesignRecommendation.CLARIFY_RUNTIME_ARCHITECTURE),
        (PaperTradingRuntimeDesignRisk.ROLLBACK_HOOK_MISSING, PaperTradingRuntimeDesignRecommendation.ADD_ROLLBACK_HOOKS),
        (PaperTradingRuntimeDesignRisk.ADAPTER_CONTRACT_INCOMPLETE, PaperTradingRuntimeDesignRecommendation.COMPLETE_ADAPTER_CONTRACTS),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_runtime_design_recommendations((risk,), PaperTradingRuntimeDesignDecision.REQUIRE_DESIGN_CLEANUP)


def test_module_keeps_offline_import_boundary():
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / "paper_trading_runtime_design.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
