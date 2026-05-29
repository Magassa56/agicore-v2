import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from agicore.trading.alpaca_paper_adapter import (
    compute_alpaca_adapter_score,
    detect_alpaca_adapter_risks,
    evaluate_alpaca_paper_adapter,
    generate_alpaca_adapter_recommendations,
    render_alpaca_adapter_markdown,
    verify_account_mapping,
    verify_order_mapping,
    verify_paper_account_translation,
    verify_paper_order_translation,
    verify_paper_position_translation,
    verify_position_mapping,
)
from agicore.trading.alpaca_paper_adapter_models import (
    AlpacaPaperAdapterInput,
    AlpacaPaperAdapterRecommendation,
    AlpacaPaperAdapterRisk,
    AlpacaPaperAdapterState,
)


def _upstream(**overrides):
    data = {
        "state": "READY",
        "adapter_score": 96,
        "supervised_session_score": 96,
        "human_validation_score": 96,
        "controlled_paper_score": 96,
        "paper_loop_score": 96,
        "paper_runtime_score": 96,
        "observability_score": 96,
        "risks": (),
        "blockers": (),
        "offline_only": True,
        "score_breakdown": SimpleNamespace(
            adapter_score=96,
            supervised_session_score=96,
            human_validation_score=96,
            controlled_paper_score=96,
            paper_loop_score=96,
            paper_runtime_score=96,
            observability_score=96,
        ),
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def _ready_input(**overrides):
    data = {
        "paper_broker_adapter": _upstream(state="READY_FOR_ALPACA_PAPER_ADAPTER"),
        "supervised_paper_session": _upstream(state="READY_FOR_PAPER_BROKER_ADAPTER"),
        "human_validated_paper_session": _upstream(state="READY_FOR_SUPERVISED_PAPER_SESSION"),
        "controlled_paper_run": _upstream(state="READY_FOR_HUMAN_VALIDATED_SESSION"),
        "paper_execution_loop_readiness": _upstream(state="READY_FOR_CONTROLLED_PAPER_RUN"),
        "paper_runtime_preparation": _upstream(state="READY_FOR_PAPER_EXECUTION_LOOP"),
        "account_id_mapping_defined": True,
        "account_status_mapping_defined": True,
        "account_equity_mapping_defined": True,
        "account_buying_power_mapping_defined": True,
        "account_currency_mapping_defined": True,
        "order_symbol_mapping_defined": True,
        "order_side_mapping_defined": True,
        "order_type_mapping_defined": True,
        "order_time_in_force_mapping_defined": True,
        "order_qty_mapping_defined": True,
        "position_symbol_mapping_defined": True,
        "position_qty_mapping_defined": True,
        "position_avg_entry_mapping_defined": True,
        "position_market_value_mapping_defined": True,
        "position_unrealized_pnl_mapping_defined": True,
        "paper_order_translation_defined": True,
        "paper_order_validation_defined": True,
        "paper_order_idempotency_defined": True,
        "paper_order_network_disabled": True,
        "paper_order_routing_blocked": True,
        "paper_account_translation_defined": True,
        "paper_account_reconciliation_defined": True,
        "paper_account_state_checkpointed": True,
        "paper_position_translation_defined": True,
        "paper_position_reconciliation_defined": True,
        "paper_position_state_checkpointed": True,
        "offline_mode_enforced": True,
        "no_api_keys_required": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "observability_events_defined": True,
        "rollback_linked": True,
        "supervision_required": True,
        "deterministic_mapping_required": True,
        "paper_state_drift_monitoring_defined": True,
        "ready_for_end_to_end_paper": True,
        "account_mapping_score": 96,
        "order_mapping_score": 96,
        "position_mapping_score": 96,
        "paper_order_translation_score": 96,
        "paper_account_translation_score": 96,
        "paper_position_translation_score": 96,
        "adapter_safety_score": 96,
        "observability_score": 96,
    }
    data.update(overrides)
    return AlpacaPaperAdapterInput(**data)


def test_evaluate_alpaca_adapter_ready_for_end_to_end_paper_when_all_contracts_are_ready():
    result = evaluate_alpaca_paper_adapter(_ready_input())

    assert result.state is AlpacaPaperAdapterState.READY_FOR_END_TO_END_PAPER
    assert result.risks == ()
    assert result.alpaca_adapter_score >= 94
    assert result.offline_only is True
    assert result.adapter_graph.ready_edges == (
        ("agicore_models", "alpaca_paper_models"),
        ("alpaca_paper_models", "paper_translation"),
        ("paper_translation", "adapter_safety"),
        ("adapter_safety", "observability_rollback"),
        ("observability_rollback", "end_to_end_paper"),
    )
    assert result.account_mapping_review.passed is True
    assert result.order_mapping_review.passed is True
    assert result.position_mapping_review.passed is True
    assert result.paper_order_translation_review.passed is True
    assert result.paper_account_translation_review.passed is True
    assert result.paper_position_translation_review.passed is True


def test_detect_alpaca_adapter_risks_reports_all_failures():
    data = _ready_input(
        account_id_mapping_defined=False,
        account_status_mapping_defined=False,
        account_equity_mapping_defined=False,
        account_buying_power_mapping_defined=False,
        account_currency_mapping_defined=False,
        order_symbol_mapping_defined=False,
        order_side_mapping_defined=False,
        order_type_mapping_defined=False,
        order_time_in_force_mapping_defined=False,
        order_qty_mapping_defined=False,
        position_symbol_mapping_defined=False,
        position_qty_mapping_defined=False,
        position_avg_entry_mapping_defined=False,
        position_market_value_mapping_defined=False,
        position_unrealized_pnl_mapping_defined=False,
        paper_order_translation_defined=False,
        paper_order_validation_defined=False,
        paper_order_idempotency_defined=False,
        paper_order_network_disabled=False,
        paper_order_routing_blocked=False,
        paper_account_translation_defined=False,
        paper_account_reconciliation_defined=False,
        paper_account_state_checkpointed=False,
        paper_position_translation_defined=False,
        paper_position_reconciliation_defined=False,
        paper_position_state_checkpointed=False,
        offline_mode_enforced=False,
        no_api_keys_required=False,
        no_http_transport=False,
        no_websocket_transport=False,
        observability_events_defined=False,
        rollback_linked=False,
        supervision_required=False,
        deterministic_mapping_required=False,
        paper_state_drift_monitoring_defined=False,
        account_mapping_score=10,
        order_mapping_score=10,
        position_mapping_score=10,
        paper_order_translation_score=10,
        paper_account_translation_score=10,
        paper_position_translation_score=10,
        adapter_safety_score=10,
        observability_score=10,
    )

    risks = detect_alpaca_adapter_risks(data)

    assert set(risks) == set(AlpacaPaperAdapterRisk)


def test_order_mapping_failure_forces_not_ready():
    result = evaluate_alpaca_paper_adapter(_ready_input(order_symbol_mapping_defined=False))

    assert result.state is AlpacaPaperAdapterState.NOT_READY
    assert AlpacaPaperAdapterRisk.ORDER_MAPPING_FAILURE in result.risks
    assert result.adapter_graph.blocked_edges == (
        ("agicore_models", "alpaca_paper_models"),
    )


def test_account_mapping_detects_mapping_and_configuration_failures():
    section = verify_account_mapping(
        _ready_input(account_equity_mapping_defined=False, account_currency_mapping_defined=False)
    )

    assert section.passed is False
    assert AlpacaPaperAdapterRisk.ACCOUNT_MAPPING_FAILURE in section.risks
    assert AlpacaPaperAdapterRisk.CONFIGURATION_ERROR in section.risks


def test_order_mapping_detects_order_and_configuration_failures():
    section = verify_order_mapping(
        _ready_input(order_type_mapping_defined=False, order_time_in_force_mapping_defined=False)
    )

    assert section.passed is False
    assert AlpacaPaperAdapterRisk.ORDER_MAPPING_FAILURE in section.risks
    assert AlpacaPaperAdapterRisk.CONFIGURATION_ERROR in section.risks


def test_position_mapping_detects_position_mapping_failure():
    section = verify_position_mapping(_ready_input(position_market_value_mapping_defined=False))

    assert section.passed is False
    assert section.risks == (AlpacaPaperAdapterRisk.POSITION_MAPPING_FAILURE,)


def test_paper_order_translation_detects_translation_routing_and_drift_failures():
    section = verify_paper_order_translation(
        _ready_input(
            paper_order_translation_defined=False,
            paper_order_network_disabled=False,
            paper_order_idempotency_defined=False,
        )
    )

    assert section.passed is False
    assert AlpacaPaperAdapterRisk.PAPER_TRANSLATION_FAILURE in section.risks
    assert AlpacaPaperAdapterRisk.UNSAFE_ORDER_ROUTING in section.risks
    assert AlpacaPaperAdapterRisk.PAPER_STATE_DRIFT in section.risks


def test_paper_account_translation_detects_translation_and_state_drift():
    section = verify_paper_account_translation(
        _ready_input(paper_account_translation_defined=False, paper_account_state_checkpointed=False)
    )

    assert section.passed is False
    assert AlpacaPaperAdapterRisk.PAPER_TRANSLATION_FAILURE in section.risks
    assert AlpacaPaperAdapterRisk.PAPER_STATE_DRIFT in section.risks


def test_paper_position_translation_detects_translation_and_state_drift():
    section = verify_paper_position_translation(
        _ready_input(paper_position_translation_defined=False, deterministic_mapping_required=False)
    )

    assert section.passed is False
    assert AlpacaPaperAdapterRisk.PAPER_TRANSLATION_FAILURE in section.risks
    assert AlpacaPaperAdapterRisk.PAPER_STATE_DRIFT in section.risks


def test_three_soft_risks_require_review_without_hard_failure():
    result = evaluate_alpaca_paper_adapter(
        _ready_input(
            paper_account_reconciliation_defined=False,
            observability_events_defined=False,
            rollback_linked=False,
        )
    )

    assert result.state is AlpacaPaperAdapterState.REVIEW_REQUIRED
    assert {
        AlpacaPaperAdapterRisk.PAPER_STATE_DRIFT,
        AlpacaPaperAdapterRisk.OBSERVABILITY_GAP,
        AlpacaPaperAdapterRisk.ROLLBACK_INCOMPATIBILITY,
    }.issubset(result.risks)


def test_single_soft_risk_yields_partially_ready():
    result = evaluate_alpaca_paper_adapter(
        _ready_input(paper_account_reconciliation_defined=False)
    )

    assert result.state is AlpacaPaperAdapterState.PARTIALLY_READY
    assert result.risks == (AlpacaPaperAdapterRisk.PAPER_STATE_DRIFT,)


def test_adapter_ready_when_clean_but_end_to_end_gate_not_ready():
    result = evaluate_alpaca_paper_adapter(
        _ready_input(
            ready_for_end_to_end_paper=False,
            account_mapping_score=89,
            order_mapping_score=89,
            position_mapping_score=89,
            paper_order_translation_score=89,
            paper_account_translation_score=89,
            paper_position_translation_score=89,
            adapter_safety_score=89,
            observability_score=89,
        )
    )

    assert result.state is AlpacaPaperAdapterState.ADAPTER_READY
    assert result.risks == ()
    assert result.alpaca_adapter_score >= 88


def test_compute_alpaca_adapter_score_caps_hard_risks():
    data = _ready_input(order_symbol_mapping_defined=False, paper_order_routing_blocked=False)
    sections = (
        verify_account_mapping(data),
        verify_order_mapping(data),
        verify_position_mapping(data),
        verify_paper_order_translation(data),
        verify_paper_account_translation(data),
        verify_paper_position_translation(data),
    )
    risks = (
        AlpacaPaperAdapterRisk.ORDER_MAPPING_FAILURE,
        AlpacaPaperAdapterRisk.UNSAFE_ORDER_ROUTING,
    )

    score = compute_alpaca_adapter_score(data, risks, *sections)

    assert score.overall_score <= 45


def test_generate_recommendations_are_deduplicated_and_risk_driven():
    result = evaluate_alpaca_paper_adapter(
        _ready_input(
            order_symbol_mapping_defined=False,
            observability_events_defined=False,
            rollback_linked=False,
        )
    )

    recommendations = generate_alpaca_adapter_recommendations(result.risks, result.state)

    assert AlpacaPaperAdapterRecommendation.FIX_ORDER_MAPPING in recommendations
    assert AlpacaPaperAdapterRecommendation.ADD_ADAPTER_OBSERVABILITY in recommendations
    assert AlpacaPaperAdapterRecommendation.LINK_ADAPTER_ROLLBACK in recommendations
    assert len(recommendations) == len(set(recommendations))


def test_markdown_contains_alpaca_adapter_sections():
    result = evaluate_alpaca_paper_adapter(_ready_input())

    markdown = render_alpaca_adapter_markdown(result)

    assert "# AGIcore Alpaca Paper Adapter" in markdown
    assert "# Alpaca Adapter Graph" in markdown
    assert "# Alpaca Adapter Risks" in markdown
    assert "READY_FOR_END_TO_END_PAPER" in markdown


def test_evaluate_alpaca_adapter_accepts_mapping_input_and_upstream_results():
    result = evaluate_alpaca_paper_adapter(
        {
            "paper_broker_adapter": _upstream(state="READY_FOR_ALPACA_PAPER_ADAPTER"),
            "supervised_paper_session": _upstream(state="READY_FOR_PAPER_BROKER_ADAPTER"),
            "human_validated_paper_session": _upstream(state="READY_FOR_SUPERVISED_PAPER_SESSION"),
            "controlled_paper_run": _upstream(state="READY_FOR_HUMAN_VALIDATED_SESSION"),
            "paper_execution_loop_readiness": _upstream(state="READY_FOR_CONTROLLED_PAPER_RUN"),
            "paper_runtime_preparation": _upstream(state="READY_FOR_PAPER_EXECUTION_LOOP"),
            "account_id_mapping_defined": True,
            "account_status_mapping_defined": True,
            "account_equity_mapping_defined": True,
            "account_buying_power_mapping_defined": True,
            "account_currency_mapping_defined": True,
            "order_symbol_mapping_defined": True,
            "order_side_mapping_defined": True,
            "order_type_mapping_defined": True,
            "order_time_in_force_mapping_defined": True,
            "order_qty_mapping_defined": True,
            "position_symbol_mapping_defined": True,
            "position_qty_mapping_defined": True,
            "position_avg_entry_mapping_defined": True,
            "position_market_value_mapping_defined": True,
            "position_unrealized_pnl_mapping_defined": True,
            "paper_order_translation_defined": True,
            "paper_order_validation_defined": True,
            "paper_order_idempotency_defined": True,
            "paper_order_network_disabled": True,
            "paper_order_routing_blocked": True,
            "paper_account_translation_defined": True,
            "paper_account_reconciliation_defined": True,
            "paper_account_state_checkpointed": True,
            "paper_position_translation_defined": True,
            "paper_position_reconciliation_defined": True,
            "paper_position_state_checkpointed": True,
            "offline_mode_enforced": True,
            "no_api_keys_required": True,
            "no_http_transport": True,
            "no_websocket_transport": True,
            "observability_events_defined": True,
            "rollback_linked": True,
            "supervision_required": True,
            "deterministic_mapping_required": True,
            "paper_state_drift_monitoring_defined": True,
            "ready_for_end_to_end_paper": True,
        }
    )

    assert result.state is AlpacaPaperAdapterState.READY_FOR_END_TO_END_PAPER
    assert result.risks == ()


def test_alpaca_adapter_module_has_no_forbidden_runtime_imports():
    module_text = Path("src/agicore/trading/alpaca_paper_adapter.py").read_text()
    tree = ast.parse(module_text)
    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)

    forbidden = ("alpaca", "requests", "websocket", "socket", "http")
    assert not any(
        module == forbidden_name or module.startswith(f"{forbidden_name}.")
        for module in imported_modules
        for forbidden_name in forbidden
    )


@pytest.mark.parametrize(
    ("risk", "expected"),
    [
        (
            AlpacaPaperAdapterRisk.UNSAFE_ORDER_ROUTING,
            AlpacaPaperAdapterRecommendation.BLOCK_UNSAFE_ORDER_ROUTING,
        ),
        (
            AlpacaPaperAdapterRisk.CONFIGURATION_ERROR,
            AlpacaPaperAdapterRecommendation.FIX_ADAPTER_CONFIGURATION,
        ),
    ],
)
def test_recommendation_mapping_for_routing_and_configuration_risks(risk, expected):
    result = evaluate_alpaca_paper_adapter(_ready_input())

    assert expected in generate_alpaca_adapter_recommendations((risk,), result.state)
