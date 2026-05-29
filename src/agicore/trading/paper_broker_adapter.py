"""Offline paper broker adapter readiness audit for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_adapter_models import (
    PaperBrokerAdapterGraph,
    PaperBrokerAdapterInput,
    PaperBrokerAdapterRecommendation,
    PaperBrokerAdapterResult,
    PaperBrokerAdapterReviewSection,
    PaperBrokerAdapterRisk,
    PaperBrokerAdapterScore,
    PaperBrokerAdapterState,
)


def _coerce_input(data: PaperBrokerAdapterInput | Mapping[str, Any]) -> PaperBrokerAdapterInput:
    if isinstance(data, PaperBrokerAdapterInput):
        return data
    return PaperBrokerAdapterInput(**dict(data))


def _value(item: Any) -> str:
    if item is None:
        return ""
    if isinstance(item, Enum):
        return str(item.value)
    return str(item)


def _get(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _as_tuple(items: Any) -> tuple[Any, ...]:
    if items is None:
        return ()
    if isinstance(items, tuple):
        return items
    if isinstance(items, list):
        return tuple(items)
    if isinstance(items, set):
        return tuple(items)
    return (items,)


def _contains(items: Any, *needles: str) -> bool:
    text_items = tuple(_value(item).upper() for item in _as_tuple(items))
    return any(any(needle.upper() in item for item in text_items) for needle in needles)


def _clamp(value: int | float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def _average(values: Iterable[int | float | None], default: int = 0) -> int:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return default
    return _clamp(sum(usable) / len(usable))


def _weighted_average(values: Iterable[tuple[int | float | None, float]], default: int = 0) -> int:
    usable = [(float(value), weight) for value, weight in values if value is not None and weight > 0]
    if not usable:
        return default
    total_weight = sum(weight for _, weight in usable)
    return _clamp(sum(value * weight for value, weight in usable) / total_weight)


def _score(obj: Any, *names: str, default: int | None = None) -> int | None:
    for name in names:
        value = _get(obj, name)
        if isinstance(value, (int, float)):
            return _clamp(value)
    return default


def _bool_score(value: bool | None, unknown: int = 45) -> int:
    if value is True:
        return 100
    if value is False:
        return 0
    return unknown


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    result: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def _upstream_items(data: PaperBrokerAdapterInput) -> tuple[Any, ...]:
    return (
        data.supervised_paper_session,
        data.human_validated_paper_session,
        data.controlled_paper_run,
        data.paper_execution_loop_readiness,
        data.paper_runtime_preparation,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
    )


def _upstream_risks(data: PaperBrokerAdapterInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream(data: PaperBrokerAdapterInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _upstream_score(data: PaperBrokerAdapterInput, *names: str) -> int | None:
    values: list[int] = []
    for item in _upstream_items(data):
        values.extend(_score(item, name) for name in names)
        breakdown = _get(item, "score_breakdown")
        values.extend(_score(breakdown, name) for name in names)
    values = [value for value in values if value is not None]
    return _average(values) if values else None


def verify_broker_interface(
    data: PaperBrokerAdapterInput | Mapping[str, Any],
) -> PaperBrokerAdapterReviewSection:
    """Verify the standard offline paper broker interface contract."""

    data = _coerce_input(data)
    score = _clamp(data.broker_interface_score) if data.broker_interface_score is not None else _average(
        (
            _bool_score(data.broker_interface_defined),
            _bool_score(data.broker_capability_contract_defined),
            _bool_score(data.adapter_config_schema_defined),
            _bool_score(data.offline_adapter_mode_enforced),
            _bool_score(data.no_network_transport_configured),
            _upstream_score(data, "supervised_session_score"),
        ),
        default=45,
    )
    risks: list[PaperBrokerAdapterRisk] = []
    if (
        data.broker_interface_defined is not True
        or data.broker_capability_contract_defined is not True
        or score < 85
    ):
        risks.append(PaperBrokerAdapterRisk.BROKER_INTERFACE_MISSING)
    if data.adapter_config_schema_defined is not True:
        risks.append(PaperBrokerAdapterRisk.ADAPTER_CONFIGURATION_ERROR)
    if data.offline_adapter_mode_enforced is not True or data.no_network_transport_configured is not True:
        risks.append(PaperBrokerAdapterRisk.SAFETY_LAYER_MISSING)
    evidence = (
        f"broker_interface_score={score}/100",
        f"broker_interface_defined={data.broker_interface_defined}",
        f"broker_capability_contract_defined={data.broker_capability_contract_defined}",
        f"adapter_config_schema_defined={data.adapter_config_schema_defined}",
        f"offline_adapter_mode_enforced={data.offline_adapter_mode_enforced}",
        f"no_network_transport_configured={data.no_network_transport_configured}",
    )
    return PaperBrokerAdapterReviewSection("broker_interface_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_order_translation(
    data: PaperBrokerAdapterInput | Mapping[str, Any],
) -> PaperBrokerAdapterReviewSection:
    """Verify AGIcore paper order to adapter order translation contract."""

    data = _coerce_input(data)
    score = _clamp(data.order_translation_score) if data.order_translation_score is not None else _average(
        (
            _bool_score(data.order_model_mapping_defined),
            _bool_score(data.order_side_mapping_defined),
            _bool_score(data.order_type_mapping_defined),
            _bool_score(data.order_validation_contract_defined),
            _bool_score(data.order_idempotency_defined),
        ),
        default=45,
    )
    risks: list[PaperBrokerAdapterRisk] = []
    if (
        data.order_model_mapping_defined is not True
        or data.order_side_mapping_defined is not True
        or data.order_type_mapping_defined is not True
        or data.order_validation_contract_defined is not True
        or score < 85
    ):
        risks.append(PaperBrokerAdapterRisk.ORDER_TRANSLATION_FAILURE)
    if data.order_idempotency_defined is not True:
        risks.append(PaperBrokerAdapterRisk.PAPER_DRIFT_RISK)
    evidence = (
        f"order_translation_score={score}/100",
        f"order_model_mapping_defined={data.order_model_mapping_defined}",
        f"order_side_mapping_defined={data.order_side_mapping_defined}",
        f"order_type_mapping_defined={data.order_type_mapping_defined}",
        f"order_validation_contract_defined={data.order_validation_contract_defined}",
        f"order_idempotency_defined={data.order_idempotency_defined}",
    )
    return PaperBrokerAdapterReviewSection("order_translation_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_position_translation(
    data: PaperBrokerAdapterInput | Mapping[str, Any],
) -> PaperBrokerAdapterReviewSection:
    """Verify broker paper positions can be translated into AGIcore paper state."""

    data = _coerce_input(data)
    score = _clamp(data.position_translation_score) if data.position_translation_score is not None else _average(
        (
            _bool_score(data.position_model_mapping_defined),
            _bool_score(data.position_quantity_mapping_defined),
            _bool_score(data.position_pnl_mapping_defined),
            _bool_score(data.position_reconciliation_defined),
        ),
        default=45,
    )
    risks: list[PaperBrokerAdapterRisk] = []
    if (
        data.position_model_mapping_defined is not True
        or data.position_quantity_mapping_defined is not True
        or data.position_pnl_mapping_defined is not True
        or score < 85
    ):
        risks.append(PaperBrokerAdapterRisk.POSITION_TRANSLATION_FAILURE)
    if data.position_reconciliation_defined is not True:
        risks.append(PaperBrokerAdapterRisk.PAPER_DRIFT_RISK)
    evidence = (
        f"position_translation_score={score}/100",
        f"position_model_mapping_defined={data.position_model_mapping_defined}",
        f"position_quantity_mapping_defined={data.position_quantity_mapping_defined}",
        f"position_pnl_mapping_defined={data.position_pnl_mapping_defined}",
        f"position_reconciliation_defined={data.position_reconciliation_defined}",
    )
    return PaperBrokerAdapterReviewSection("position_translation_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_account_translation(
    data: PaperBrokerAdapterInput | Mapping[str, Any],
) -> PaperBrokerAdapterReviewSection:
    """Verify broker paper account payloads can be translated into AGIcore account state."""

    data = _coerce_input(data)
    score = _clamp(data.account_translation_score) if data.account_translation_score is not None else _average(
        (
            _bool_score(data.account_model_mapping_defined),
            _bool_score(data.buying_power_mapping_defined),
            _bool_score(data.equity_balance_mapping_defined),
            _bool_score(data.account_risk_limits_defined),
        ),
        default=45,
    )
    risks: list[PaperBrokerAdapterRisk] = []
    if (
        data.account_model_mapping_defined is not True
        or data.buying_power_mapping_defined is not True
        or data.equity_balance_mapping_defined is not True
        or score < 85
    ):
        risks.append(PaperBrokerAdapterRisk.ACCOUNT_TRANSLATION_FAILURE)
    if data.account_risk_limits_defined is not True:
        risks.append(PaperBrokerAdapterRisk.SAFETY_LAYER_MISSING)
    evidence = (
        f"account_translation_score={score}/100",
        f"account_model_mapping_defined={data.account_model_mapping_defined}",
        f"buying_power_mapping_defined={data.buying_power_mapping_defined}",
        f"equity_balance_mapping_defined={data.equity_balance_mapping_defined}",
        f"account_risk_limits_defined={data.account_risk_limits_defined}",
    )
    return PaperBrokerAdapterReviewSection("account_translation_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_adapter_safety(
    data: PaperBrokerAdapterInput | Mapping[str, Any],
) -> PaperBrokerAdapterReviewSection:
    """Verify adapter safety, observability, rollback and supervision gates."""

    data = _coerce_input(data)
    observability_score = data.observability_score if data.observability_score is not None else _average(
        (
            _bool_score(data.observability_events_defined),
            _upstream_score(data, "observability_score"),
        )
    )
    score = _clamp(data.adapter_safety_score) if data.adapter_safety_score is not None else _average(
        (
            _bool_score(data.safety_prechecks_required),
            _bool_score(data.kill_switch_linked),
            _bool_score(data.rollback_linked),
            _bool_score(data.supervision_required),
            _bool_score(data.observability_events_defined),
            _bool_score(data.deterministic_translation_required),
            _bool_score(data.paper_drift_monitoring_defined),
            observability_score,
            _upstream_score(data, "rollback_score", "kill_switch_score"),
        ),
        default=45,
    )
    risks: list[PaperBrokerAdapterRisk] = []
    if data.safety_prechecks_required is not True or data.kill_switch_linked is not True or score < 85:
        risks.append(PaperBrokerAdapterRisk.SAFETY_LAYER_MISSING)
    if data.observability_events_defined is not True or observability_score < 80 or _has_upstream(data, "OBSERVABILITY"):
        risks.append(PaperBrokerAdapterRisk.OBSERVABILITY_GAP)
    if data.rollback_linked is not True or _has_upstream(data, "ROLLBACK"):
        risks.append(PaperBrokerAdapterRisk.ROLLBACK_INCOMPATIBILITY)
    if data.supervision_required is not True or _has_upstream(data, "SUPERVISION"):
        risks.append(PaperBrokerAdapterRisk.SUPERVISION_CHAIN_BREAK)
    if data.deterministic_translation_required is not True or data.paper_drift_monitoring_defined is not True or _has_upstream(data, "DRIFT"):
        risks.append(PaperBrokerAdapterRisk.PAPER_DRIFT_RISK)
    evidence = (
        f"adapter_safety_score={score}/100",
        f"observability_score={observability_score}/100",
        f"safety_prechecks_required={data.safety_prechecks_required}",
        f"kill_switch_linked={data.kill_switch_linked}",
        f"rollback_linked={data.rollback_linked}",
        f"supervision_required={data.supervision_required}",
        f"observability_events_defined={data.observability_events_defined}",
        f"deterministic_translation_required={data.deterministic_translation_required}",
        f"paper_drift_monitoring_defined={data.paper_drift_monitoring_defined}",
    )
    return PaperBrokerAdapterReviewSection("adapter_safety_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def _build_adapter_graph(risks: tuple[PaperBrokerAdapterRisk, ...]) -> PaperBrokerAdapterGraph:
    nodes = (
        "broker_interface",
        "order_translation",
        "position_translation",
        "account_translation",
        "adapter_safety",
        "alpaca_paper_adapter",
    )
    edges = (
        ("broker_interface", "order_translation", "defines"),
        ("order_translation", "position_translation", "feeds"),
        ("position_translation", "account_translation", "reconciles"),
        ("account_translation", "adapter_safety", "bounds"),
        ("adapter_safety", "alpaca_paper_adapter", "gates"),
    )
    blocked: list[tuple[str, str]] = []
    if (
        PaperBrokerAdapterRisk.BROKER_INTERFACE_MISSING in risks
        or PaperBrokerAdapterRisk.ADAPTER_CONFIGURATION_ERROR in risks
    ):
        blocked.append(("broker_interface", "order_translation"))
    if PaperBrokerAdapterRisk.ORDER_TRANSLATION_FAILURE in risks:
        blocked.append(("order_translation", "position_translation"))
    if (
        PaperBrokerAdapterRisk.POSITION_TRANSLATION_FAILURE in risks
        or PaperBrokerAdapterRisk.PAPER_DRIFT_RISK in risks
    ):
        blocked.append(("position_translation", "account_translation"))
    if PaperBrokerAdapterRisk.ACCOUNT_TRANSLATION_FAILURE in risks:
        blocked.append(("account_translation", "adapter_safety"))
    if (
        PaperBrokerAdapterRisk.SAFETY_LAYER_MISSING in risks
        or PaperBrokerAdapterRisk.OBSERVABILITY_GAP in risks
        or PaperBrokerAdapterRisk.ROLLBACK_INCOMPATIBILITY in risks
        or PaperBrokerAdapterRisk.SUPERVISION_CHAIN_BREAK in risks
    ):
        blocked.append(("adapter_safety", "alpaca_paper_adapter"))
    return PaperBrokerAdapterGraph(
        nodes=nodes,
        edges=edges,
        ready_edges=(
            ("broker_interface", "order_translation"),
            ("order_translation", "position_translation"),
            ("position_translation", "account_translation"),
            ("account_translation", "adapter_safety"),
            ("adapter_safety", "alpaca_paper_adapter"),
        ),
        blocked_edges=_dedupe(blocked),
    )


def detect_adapter_risks(
    data: PaperBrokerAdapterInput | Mapping[str, Any],
    broker_interface_review: PaperBrokerAdapterReviewSection | None = None,
    order_translation_review: PaperBrokerAdapterReviewSection | None = None,
    position_translation_review: PaperBrokerAdapterReviewSection | None = None,
    account_translation_review: PaperBrokerAdapterReviewSection | None = None,
    adapter_safety_review: PaperBrokerAdapterReviewSection | None = None,
) -> tuple[PaperBrokerAdapterRisk, ...]:
    """Detect risks that block the offline paper broker adapter abstraction."""

    data = _coerce_input(data)
    sections = (
        broker_interface_review or verify_broker_interface(data),
        order_translation_review or verify_order_translation(data),
        position_translation_review or verify_position_translation(data),
        account_translation_review or verify_account_translation(data),
        adapter_safety_review or verify_adapter_safety(data),
    )
    risks: list[PaperBrokerAdapterRisk] = []
    for section in sections:
        risks.extend(section.risks)
    return _dedupe(risks)


def compute_adapter_score(
    data: PaperBrokerAdapterInput | Mapping[str, Any],
    risks: tuple[PaperBrokerAdapterRisk, ...] = (),
    broker_interface_review: PaperBrokerAdapterReviewSection | None = None,
    order_translation_review: PaperBrokerAdapterReviewSection | None = None,
    position_translation_review: PaperBrokerAdapterReviewSection | None = None,
    account_translation_review: PaperBrokerAdapterReviewSection | None = None,
    adapter_safety_review: PaperBrokerAdapterReviewSection | None = None,
) -> PaperBrokerAdapterScore:
    """Compute paper broker adapter readiness score normalized to 0..100."""

    data = _coerce_input(data)
    interface = broker_interface_review or verify_broker_interface(data)
    order = order_translation_review or verify_order_translation(data)
    position = position_translation_review or verify_position_translation(data)
    account = account_translation_review or verify_account_translation(data)
    safety = adapter_safety_review or verify_adapter_safety(data)
    observability_score = data.observability_score if data.observability_score is not None else _average(
        (
            _bool_score(data.observability_events_defined),
            _upstream_score(data, "observability_score"),
        )
    )
    weighted = _weighted_average(
        (
            (interface.score, 1.3),
            (order.score, 1.2),
            (position.score, 1.1),
            (account.score, 1.1),
            (safety.score, 1.35),
            (observability_score, 0.85),
        )
    )
    penalty = min(72, len(set(risks)) * 7)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        PaperBrokerAdapterRisk.BROKER_INTERFACE_MISSING: 45,
        PaperBrokerAdapterRisk.ORDER_TRANSLATION_FAILURE: 50,
        PaperBrokerAdapterRisk.POSITION_TRANSLATION_FAILURE: 55,
        PaperBrokerAdapterRisk.ACCOUNT_TRANSLATION_FAILURE: 55,
        PaperBrokerAdapterRisk.SAFETY_LAYER_MISSING: 45,
        PaperBrokerAdapterRisk.SUPERVISION_CHAIN_BREAK: 50,
        PaperBrokerAdapterRisk.ADAPTER_CONFIGURATION_ERROR: 55,
    }
    for risk, cap in critical_caps.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperBrokerAdapterScore(
        overall_score=overall,
        broker_interface_score=interface.score,
        order_translation_score=order.score,
        position_translation_score=position.score,
        account_translation_score=account.score,
        adapter_safety_score=safety.score,
        observability_score=_clamp(observability_score),
    )


def _select_state(
    score: int,
    risks: tuple[PaperBrokerAdapterRisk, ...],
    ready_for_alpaca_paper_adapter: bool | None,
) -> PaperBrokerAdapterState:
    count = len(set(risks))
    hard = {
        PaperBrokerAdapterRisk.BROKER_INTERFACE_MISSING,
        PaperBrokerAdapterRisk.ORDER_TRANSLATION_FAILURE,
        PaperBrokerAdapterRisk.SAFETY_LAYER_MISSING,
        PaperBrokerAdapterRisk.SUPERVISION_CHAIN_BREAK,
        PaperBrokerAdapterRisk.ADAPTER_CONFIGURATION_ERROR,
    }
    if hard.intersection(risks) or score < 45 or count >= 6:
        return PaperBrokerAdapterState.NOT_READY
    if count >= 3 or score < 72:
        return PaperBrokerAdapterState.REVIEW_REQUIRED
    if count:
        return PaperBrokerAdapterState.PARTIALLY_READY
    if score >= 94 and ready_for_alpaca_paper_adapter is True:
        return PaperBrokerAdapterState.READY_FOR_ALPACA_PAPER_ADAPTER
    if score >= 88:
        return PaperBrokerAdapterState.ADAPTER_READY
    return PaperBrokerAdapterState.PARTIALLY_READY


def generate_adapter_recommendations(
    risks: tuple[PaperBrokerAdapterRisk, ...],
    state: PaperBrokerAdapterState | None = None,
) -> tuple[PaperBrokerAdapterRecommendation, ...]:
    """Generate paper broker adapter recommendations."""

    recommendations: list[PaperBrokerAdapterRecommendation] = []
    if risks:
        recommendations.append(PaperBrokerAdapterRecommendation.HOLD_ALPACA_PAPER_ADAPTER_APPROVAL)
    mapping = {
        PaperBrokerAdapterRisk.BROKER_INTERFACE_MISSING: PaperBrokerAdapterRecommendation.DEFINE_BROKER_INTERFACE_CONTRACT,
        PaperBrokerAdapterRisk.ORDER_TRANSLATION_FAILURE: PaperBrokerAdapterRecommendation.FIX_ORDER_TRANSLATION_CONTRACT,
        PaperBrokerAdapterRisk.POSITION_TRANSLATION_FAILURE: PaperBrokerAdapterRecommendation.FIX_POSITION_TRANSLATION_CONTRACT,
        PaperBrokerAdapterRisk.ACCOUNT_TRANSLATION_FAILURE: PaperBrokerAdapterRecommendation.FIX_ACCOUNT_TRANSLATION_CONTRACT,
        PaperBrokerAdapterRisk.SAFETY_LAYER_MISSING: PaperBrokerAdapterRecommendation.ADD_ADAPTER_SAFETY_LAYER,
        PaperBrokerAdapterRisk.OBSERVABILITY_GAP: PaperBrokerAdapterRecommendation.ADD_ADAPTER_OBSERVABILITY,
        PaperBrokerAdapterRisk.ROLLBACK_INCOMPATIBILITY: PaperBrokerAdapterRecommendation.LINK_ADAPTER_ROLLBACK,
        PaperBrokerAdapterRisk.SUPERVISION_CHAIN_BREAK: PaperBrokerAdapterRecommendation.RESTORE_SUPERVISION_CHAIN,
        PaperBrokerAdapterRisk.PAPER_DRIFT_RISK: PaperBrokerAdapterRecommendation.LOCK_ADAPTER_DETERMINISM,
        PaperBrokerAdapterRisk.ADAPTER_CONFIGURATION_ERROR: PaperBrokerAdapterRecommendation.FIX_ADAPTER_CONFIGURATION,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperBrokerAdapterRecommendation.RUN_ADAPTER_READINESS_SUITE)
    if state == PaperBrokerAdapterState.READY_FOR_ALPACA_PAPER_ADAPTER:
        recommendations.append(PaperBrokerAdapterRecommendation.APPROVE_ALPACA_PAPER_ADAPTER_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_paper_broker_adapter(
    data: PaperBrokerAdapterInput | Mapping[str, Any],
) -> PaperBrokerAdapterResult:
    """Evaluate whether the offline paper broker adapter abstraction is ready."""

    data = _coerce_input(data)
    interface = verify_broker_interface(data)
    order = verify_order_translation(data)
    position = verify_position_translation(data)
    account = verify_account_translation(data)
    safety = verify_adapter_safety(data)
    risks = detect_adapter_risks(data, interface, order, position, account, safety)
    score = compute_adapter_score(data, risks, interface, order, position, account, safety)
    state = _select_state(score.overall_score, risks, data.ready_for_alpaca_paper_adapter)
    graph = _build_adapter_graph(risks)
    recommendations = generate_adapter_recommendations(risks, state)
    offline_only = (
        data.offline_adapter_mode_enforced is True
        and data.no_network_transport_configured is True
        and not _has_upstream(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK")
    )
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperBrokerAdapterResult(
        state=state,
        adapter_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        broker_interface_review=interface,
        order_translation_review=order,
        position_translation_review=position,
        account_translation_review=account,
        adapter_safety_review=safety,
        adapter_graph=graph,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_paper_broker_adapter_markdown(result: PaperBrokerAdapterResult) -> str:
    """Render an explainable paper broker adapter readiness report."""

    lines = [
        "# AGIcore Paper Broker Adapter",
        f"- State: {result.state.value}",
        f"- Score: {result.adapter_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Broker interface: {result.score_breakdown.broker_interface_score}/100",
        f"- Order translation: {result.score_breakdown.order_translation_score}/100",
        f"- Position translation: {result.score_breakdown.position_translation_score}/100",
        f"- Account translation: {result.score_breakdown.account_translation_score}/100",
        f"- Adapter safety: {result.score_breakdown.adapter_safety_score}/100",
        f"- Observability: {result.score_breakdown.observability_score}/100",
        "",
        "# Adapter Reviews",
    ]
    for section in (
        result.broker_interface_review,
        result.order_translation_review,
        result.position_translation_review,
        result.account_translation_review,
        result.adapter_safety_review,
    ):
        lines.append(
            f"- {section.name}: passed={section.passed}, score={section.score}/100, "
            f"risks={', '.join(risk.value for risk in section.risks) or 'none'}"
        )
        lines.extend(f"  - {item}" for item in section.evidence)
    lines.append("")
    lines.append("# Adapter Graph")
    lines.append(f"- Nodes: {', '.join(result.adapter_graph.nodes)}")
    lines.extend(
        f"- Edge: {source} -> {target} ({label})"
        for source, target, label in result.adapter_graph.edges
    )
    lines.append(
        "- Blocked edges: "
        + (
            ", ".join(f"{source}->{target}" for source, target in result.adapter_graph.blocked_edges)
            or "none"
        )
    )
    lines.append("")
    lines.append("# Adapter Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Adapter Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# Readiness Outlook")
    if result.state == PaperBrokerAdapterState.READY_FOR_ALPACA_PAPER_ADAPTER:
        lines.append("- Paper broker adapter abstraction is ready for Alpaca Paper adapter preparation.")
    elif result.state == PaperBrokerAdapterState.ADAPTER_READY:
        lines.append("- Paper broker adapter abstraction is ready; Alpaca Paper adapter remains gated.")
    elif result.state == PaperBrokerAdapterState.PARTIALLY_READY:
        lines.append("- Paper broker adapter abstraction is partially ready and remaining risks must be resolved.")
    else:
        lines.append("- Alpaca Paper adapter approval should remain blocked.")
    return "\n".join(lines)


__all__ = [
    "compute_adapter_score",
    "detect_adapter_risks",
    "evaluate_paper_broker_adapter",
    "generate_adapter_recommendations",
    "render_paper_broker_adapter_markdown",
    "verify_account_translation",
    "verify_adapter_safety",
    "verify_broker_interface",
    "verify_order_translation",
    "verify_position_translation",
]
