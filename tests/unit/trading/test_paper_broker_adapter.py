from types import SimpleNamespace

import pytest

from agicore.trading.paper_broker_adapter import (
    compute_adapter_score,
    detect_adapter_risks,
    evaluate_paper_broker_adapter,
    generate_adapter_recommendations,
    render_paper_broker_adapter_markdown,
    verify_account_translation,
    verify_adapter_safety,
    verify_broker_interface,
    verify_order_translation,
    verify_position_translation,
)
from agicore.trading.paper_broker_adapter_models import (
    PaperBrokerAdapterInput,
    PaperBrokerAdapterRecommendation,
    PaperBrokerAdapterRisk,
    PaperBrokerAdapterState,
)


def _upstream(**overrides):
    data = {
        "state": "READY",
        "supervised_session_score": 96,
        "human_validation_score": 96,
        "controlled_paper_score": 96,
        "paper_loop_score": 96,
        "paper_runtime_score": 96,
        "observability_score": 96,
        "rollback_score": 96,
        "kill_switch_score": 96,
        "risks": (),
        "blockers": (),
        "offline_only": True,
        "score_breakdown": SimpleNamespace(
            supervised_session_score=96,
            human_validation_score=96,
            controlled_paper_score=96,
            paper_loop_score=96,
            paper_runtime_score=96,
            observability_score=96,
            rollback_score=96,
            kill_switch_score=96,
        ),
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def _ready_input(**overrides):
    data = {
        "supervised_paper_session": _upstream(state="READY_FOR_PAPER_BROKER_ADAPTER"),
        "human_validated_paper_session": _upstream(state="READY_FOR_SUPERVISED_PAPER_SESSION"),
        "controlled_paper_run": _upstream(state="READY_FOR_HUMAN_VALIDATED_SESSION"),
        "paper_execution_loop_readiness": _upstream(state="READY_FOR_CONTROLLED_PAPER_RUN"),
        "paper_runtime_preparation": _upstream(state="READY_FOR_PAPER_EXECUTION_LOOP"),
        "observability_verification": _upstream(state="READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream(state="READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream(state="READY_FOR_ROLLBACK_VERIFICATION"),
        "broker_interface_defined": True,
        "broker_capability_contract_defined": True,
        "adapter_config_schema_defined": True,
        "offline_adapter_mode_enforced": True,
        "no_network_transport_configured": True,
        "order_model_mapping_defined": True,
        "order_side_mapping_defined": True,
        "order_type_mapping_defined": True,
        "order_validation_contract_defined": True,
        "order_idempotency_defined": True,
        "position_model_mapping_defined": True,
        "position_quantity_mapping_defined": True,
        "position_pnl_mapping_defined": True,
        "position_reconciliation_defined": True,
        "account_model_mapping_defined": True,
        "buying_power_mapping_defined": True,
        "equity_balance_mapping_defined": True,
        "account_risk_limits_defined": True,
        "safety_prechecks_required": True,
        "kill_switch_linked": True,
        "rollback_linked": True,
        "supervision_required": True,
        "observability_events_defined": True,
        "deterministic_translation_required": True,
        "paper_drift_monitoring_defined": True,
        "ready_for_alpaca_paper_adapter": True,
        "broker_interface_score": 96,
        "order_translation_score": 96,
        "position_translation_score": 96,
        "account_translation_score": 96,
        "adapter_safety_score": 96,
        "observability_score": 96,
    }
    data.update(overrides)
    return PaperBrokerAdapterInput(**data)


def test_evaluate_adapter_ready_for_alpaca_paper_adapter_when_abstraction_is_ready():
    result = evaluate_paper_broker_adapter(_ready_input())

    assert result.state is PaperBrokerAdapterState.READY_FOR_ALPACA_PAPER_ADAPTER
    assert result.risks == ()
    assert result.adapter_score >= 94
    assert result.offline_only is True
    assert result.adapter_graph.ready_edges == (
        ("broker_interface", "order_translation"),
        ("order_translation", "position_translation"),
        ("position_translation", "account_translation"),
        ("account_translation", "adapter_safety"),
        ("adapter_safety", "alpaca_paper_adapter"),
    )
    assert result.broker_interface_review.passed is True
    assert result.order_translation_review.passed is True
    assert result.position_translation_review.passed is True
    assert result.account_translation_review.passed is True
    assert result.adapter_safety_review.passed is True


def test_detect_adapter_risks_reports_all_failures():
    data = _ready_input(
        broker_interface_defined=False,
        broker_capability_contract_defined=False,
        adapter_config_schema_defined=False,
        offline_adapter_mode_enforced=False,
        no_network_transport_configured=False,
        order_model_mapping_defined=False,
        order_side_mapping_defined=False,
        order_type_mapping_defined=False,
        order_validation_contract_defined=False,
        order_idempotency_defined=False,
        position_model_mapping_defined=False,
        position_quantity_mapping_defined=False,
        position_pnl_mapping_defined=False,
        position_reconciliation_defined=False,
        account_model_mapping_defined=False,
        buying_power_mapping_defined=False,
        equity_balance_mapping_defined=False,
        account_risk_limits_defined=False,
        safety_prechecks_required=False,
        kill_switch_linked=False,
        rollback_linked=False,
        supervision_required=False,
        observability_events_defined=False,
        deterministic_translation_required=False,
        paper_drift_monitoring_defined=False,
        broker_interface_score=10,
        order_translation_score=10,
        position_translation_score=10,
        account_translation_score=10,
        adapter_safety_score=10,
        observability_score=10,
    )

    risks = detect_adapter_risks(data)

    assert set(risks) == set(PaperBrokerAdapterRisk)


def test_missing_broker_interface_forces_not_ready():
    result = evaluate_paper_broker_adapter(_ready_input(broker_interface_defined=False))

    assert result.state is PaperBrokerAdapterState.NOT_READY
    assert PaperBrokerAdapterRisk.BROKER_INTERFACE_MISSING in result.risks
    assert result.adapter_graph.blocked_edges == (
        ("broker_interface", "order_translation"),
    )


def test_broker_interface_detects_config_and_offline_transport_failures():
    section = verify_broker_interface(
        _ready_input(adapter_config_schema_defined=False, no_network_transport_configured=False)
    )

    assert section.passed is False
    assert PaperBrokerAdapterRisk.ADAPTER_CONFIGURATION_ERROR in section.risks
    assert PaperBrokerAdapterRisk.SAFETY_LAYER_MISSING in section.risks


def test_order_translation_detects_mapping_failure_and_drift():
    section = verify_order_translation(
        _ready_input(order_side_mapping_defined=False, order_idempotency_defined=False)
    )

    assert section.passed is False
    assert PaperBrokerAdapterRisk.ORDER_TRANSLATION_FAILURE in section.risks
    assert PaperBrokerAdapterRisk.PAPER_DRIFT_RISK in section.risks


def test_position_translation_detects_mapping_failure_and_drift():
    section = verify_position_translation(
        _ready_input(position_pnl_mapping_defined=False, position_reconciliation_defined=False)
    )

    assert section.passed is False
    assert PaperBrokerAdapterRisk.POSITION_TRANSLATION_FAILURE in section.risks
    assert PaperBrokerAdapterRisk.PAPER_DRIFT_RISK in section.risks


def test_account_translation_detects_mapping_and_safety_failures():
    section = verify_account_translation(
        _ready_input(account_model_mapping_defined=False, account_risk_limits_defined=False)
    )

    assert section.passed is False
    assert PaperBrokerAdapterRisk.ACCOUNT_TRANSLATION_FAILURE in section.risks
    assert PaperBrokerAdapterRisk.SAFETY_LAYER_MISSING in section.risks


def test_adapter_safety_detects_observability_rollback_supervision_and_drift_gaps():
    section = verify_adapter_safety(
        _ready_input(
            safety_prechecks_required=False,
            observability_events_defined=False,
            rollback_linked=False,
            supervision_required=False,
            paper_drift_monitoring_defined=False,
        )
    )

    assert section.passed is False
    assert PaperBrokerAdapterRisk.SAFETY_LAYER_MISSING in section.risks
    assert PaperBrokerAdapterRisk.OBSERVABILITY_GAP in section.risks
    assert PaperBrokerAdapterRisk.ROLLBACK_INCOMPATIBILITY in section.risks
    assert PaperBrokerAdapterRisk.SUPERVISION_CHAIN_BREAK in section.risks
    assert PaperBrokerAdapterRisk.PAPER_DRIFT_RISK in section.risks


def test_three_soft_risks_require_review_without_hard_failure():
    result = evaluate_paper_broker_adapter(
        _ready_input(
            order_idempotency_defined=False,
            observability_events_defined=False,
            rollback_linked=False,
        )
    )

    assert result.state is PaperBrokerAdapterState.REVIEW_REQUIRED
    assert {
        PaperBrokerAdapterRisk.PAPER_DRIFT_RISK,
        PaperBrokerAdapterRisk.OBSERVABILITY_GAP,
        PaperBrokerAdapterRisk.ROLLBACK_INCOMPATIBILITY,
    }.issubset(result.risks)


def test_single_soft_risk_yields_partially_ready():
    result = evaluate_paper_broker_adapter(_ready_input(order_idempotency_defined=False))

    assert result.state is PaperBrokerAdapterState.PARTIALLY_READY
    assert result.risks == (PaperBrokerAdapterRisk.PAPER_DRIFT_RISK,)


def test_adapter_ready_when_clean_but_alpaca_gate_not_ready():
    result = evaluate_paper_broker_adapter(
        _ready_input(
            ready_for_alpaca_paper_adapter=False,
            broker_interface_score=89,
            order_translation_score=89,
            position_translation_score=89,
            account_translation_score=89,
            adapter_safety_score=89,
            observability_score=89,
        )
    )

    assert result.state is PaperBrokerAdapterState.ADAPTER_READY
    assert result.risks == ()
    assert result.adapter_score >= 88


def test_review_sections_expose_specific_adapter_risks():
    data = _ready_input(
        broker_interface_defined=False,
        order_model_mapping_defined=False,
        position_model_mapping_defined=False,
        account_model_mapping_defined=False,
        safety_prechecks_required=False,
    )

    assert PaperBrokerAdapterRisk.BROKER_INTERFACE_MISSING in verify_broker_interface(data).risks
    assert PaperBrokerAdapterRisk.ORDER_TRANSLATION_FAILURE in verify_order_translation(data).risks
    assert PaperBrokerAdapterRisk.POSITION_TRANSLATION_FAILURE in verify_position_translation(data).risks
    assert PaperBrokerAdapterRisk.ACCOUNT_TRANSLATION_FAILURE in verify_account_translation(data).risks
    assert PaperBrokerAdapterRisk.SAFETY_LAYER_MISSING in verify_adapter_safety(data).risks


def test_compute_adapter_score_caps_hard_risks():
    data = _ready_input(broker_interface_defined=False, safety_prechecks_required=False)
    sections = (
        verify_broker_interface(data),
        verify_order_translation(data),
        verify_position_translation(data),
        verify_account_translation(data),
        verify_adapter_safety(data),
    )
    risks = (
        PaperBrokerAdapterRisk.BROKER_INTERFACE_MISSING,
        PaperBrokerAdapterRisk.SAFETY_LAYER_MISSING,
    )

    score = compute_adapter_score(data, risks, *sections)

    assert score.overall_score <= 45


def test_generate_recommendations_are_deduplicated_and_risk_driven():
    result = evaluate_paper_broker_adapter(
        _ready_input(
            broker_interface_defined=False,
            observability_events_defined=False,
            rollback_linked=False,
        )
    )

    recommendations = generate_adapter_recommendations(result.risks, result.state)

    assert PaperBrokerAdapterRecommendation.DEFINE_BROKER_INTERFACE_CONTRACT in recommendations
    assert PaperBrokerAdapterRecommendation.ADD_ADAPTER_OBSERVABILITY in recommendations
    assert PaperBrokerAdapterRecommendation.LINK_ADAPTER_ROLLBACK in recommendations
    assert len(recommendations) == len(set(recommendations))


def test_markdown_contains_adapter_sections():
    result = evaluate_paper_broker_adapter(_ready_input())

    markdown = render_paper_broker_adapter_markdown(result)

    assert "# AGIcore Paper Broker Adapter" in markdown
    assert "# Adapter Graph" in markdown
    assert "# Adapter Risks" in markdown
    assert "READY_FOR_ALPACA_PAPER_ADAPTER" in markdown


def test_evaluate_paper_broker_adapter_accepts_mapping_input_and_upstream_results():
    result = evaluate_paper_broker_adapter(
        {
            "supervised_paper_session": _upstream(state="READY_FOR_PAPER_BROKER_ADAPTER"),
            "human_validated_paper_session": _upstream(state="READY_FOR_SUPERVISED_PAPER_SESSION"),
            "controlled_paper_run": _upstream(state="READY_FOR_HUMAN_VALIDATED_SESSION"),
            "paper_execution_loop_readiness": _upstream(state="READY_FOR_CONTROLLED_PAPER_RUN"),
            "paper_runtime_preparation": _upstream(state="READY_FOR_PAPER_EXECUTION_LOOP"),
            "observability_verification": _upstream(state="READY_FOR_PAPER_RUNTIME_PREP"),
            "rollback_verification": _upstream(state="READY_FOR_OBSERVABILITY_VERIFICATION"),
            "kill_switch_verification": _upstream(state="READY_FOR_ROLLBACK_VERIFICATION"),
            "broker_interface_defined": True,
            "broker_capability_contract_defined": True,
            "adapter_config_schema_defined": True,
            "offline_adapter_mode_enforced": True,
            "no_network_transport_configured": True,
            "order_model_mapping_defined": True,
            "order_side_mapping_defined": True,
            "order_type_mapping_defined": True,
            "order_validation_contract_defined": True,
            "order_idempotency_defined": True,
            "position_model_mapping_defined": True,
            "position_quantity_mapping_defined": True,
            "position_pnl_mapping_defined": True,
            "position_reconciliation_defined": True,
            "account_model_mapping_defined": True,
            "buying_power_mapping_defined": True,
            "equity_balance_mapping_defined": True,
            "account_risk_limits_defined": True,
            "safety_prechecks_required": True,
            "kill_switch_linked": True,
            "rollback_linked": True,
            "supervision_required": True,
            "observability_events_defined": True,
            "deterministic_translation_required": True,
            "paper_drift_monitoring_defined": True,
            "ready_for_alpaca_paper_adapter": True,
        }
    )

    assert result.state is PaperBrokerAdapterState.READY_FOR_ALPACA_PAPER_ADAPTER
    assert result.risks == ()


@pytest.mark.parametrize(
    ("risk", "expected"),
    [
        (
            PaperBrokerAdapterRisk.ORDER_TRANSLATION_FAILURE,
            PaperBrokerAdapterRecommendation.FIX_ORDER_TRANSLATION_CONTRACT,
        ),
        (
            PaperBrokerAdapterRisk.ADAPTER_CONFIGURATION_ERROR,
            PaperBrokerAdapterRecommendation.FIX_ADAPTER_CONFIGURATION,
        ),
    ],
)
def test_recommendation_mapping_for_translation_and_configuration_risks(risk, expected):
    result = evaluate_paper_broker_adapter(_ready_input())

    assert expected in generate_adapter_recommendations((risk,), result.state)
