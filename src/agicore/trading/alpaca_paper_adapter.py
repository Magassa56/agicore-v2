"""Offline Alpaca Paper adapter readiness audit for AGIcore Trading.

This module intentionally models contracts only. It does not import Alpaca
libraries, open sockets, use HTTP, or submit any order.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.alpaca_paper_adapter_models import (
    AlpacaPaperAdapterGraph,
    AlpacaPaperAdapterInput,
    AlpacaPaperAdapterRecommendation,
    AlpacaPaperAdapterResult,
    AlpacaPaperAdapterReviewSection,
    AlpacaPaperAdapterRisk,
    AlpacaPaperAdapterScore,
    AlpacaPaperAdapterState,
)


def _coerce_input(data: AlpacaPaperAdapterInput | Mapping[str, Any]) -> AlpacaPaperAdapterInput:
    if isinstance(data, AlpacaPaperAdapterInput):
        return data
    return AlpacaPaperAdapterInput(**dict(data))


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


def _upstream_items(data: AlpacaPaperAdapterInput) -> tuple[Any, ...]:
    return (
        data.paper_broker_adapter,
        data.supervised_paper_session,
        data.human_validated_paper_session,
        data.controlled_paper_run,
        data.paper_execution_loop_readiness,
        data.paper_runtime_preparation,
    )


def _upstream_risks(data: AlpacaPaperAdapterInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream(data: AlpacaPaperAdapterInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _upstream_score(data: AlpacaPaperAdapterInput, *names: str) -> int | None:
    values: list[int] = []
    for item in _upstream_items(data):
        values.extend(_score(item, name) for name in names)
        breakdown = _get(item, "score_breakdown")
        values.extend(_score(breakdown, name) for name in names)
    values = [value for value in values if value is not None]
    return _average(values) if values else None


def verify_account_mapping(
    data: AlpacaPaperAdapterInput | Mapping[str, Any],
) -> AlpacaPaperAdapterReviewSection:
    """Verify AGIcore account fields map to an Alpaca Paper account model."""

    data = _coerce_input(data)
    score = _clamp(data.account_mapping_score) if data.account_mapping_score is not None else _average(
        (
            _bool_score(data.account_id_mapping_defined),
            _bool_score(data.account_status_mapping_defined),
            _bool_score(data.account_equity_mapping_defined),
            _bool_score(data.account_buying_power_mapping_defined),
            _bool_score(data.account_currency_mapping_defined),
        ),
        default=45,
    )
    risks: list[AlpacaPaperAdapterRisk] = []
    if (
        data.account_id_mapping_defined is not True
        or data.account_status_mapping_defined is not True
        or data.account_equity_mapping_defined is not True
        or data.account_buying_power_mapping_defined is not True
        or score < 85
    ):
        risks.append(AlpacaPaperAdapterRisk.ACCOUNT_MAPPING_FAILURE)
    if data.account_currency_mapping_defined is not True:
        risks.append(AlpacaPaperAdapterRisk.CONFIGURATION_ERROR)
    evidence = (
        f"account_mapping_score={score}/100",
        f"account_id_mapping_defined={data.account_id_mapping_defined}",
        f"account_status_mapping_defined={data.account_status_mapping_defined}",
        f"account_equity_mapping_defined={data.account_equity_mapping_defined}",
        f"account_buying_power_mapping_defined={data.account_buying_power_mapping_defined}",
        f"account_currency_mapping_defined={data.account_currency_mapping_defined}",
    )
    return AlpacaPaperAdapterReviewSection("account_mapping_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_order_mapping(
    data: AlpacaPaperAdapterInput | Mapping[str, Any],
) -> AlpacaPaperAdapterReviewSection:
    """Verify AGIcore order fields map to an Alpaca Paper order model."""

    data = _coerce_input(data)
    score = _clamp(data.order_mapping_score) if data.order_mapping_score is not None else _average(
        (
            _bool_score(data.order_symbol_mapping_defined),
            _bool_score(data.order_side_mapping_defined),
            _bool_score(data.order_type_mapping_defined),
            _bool_score(data.order_time_in_force_mapping_defined),
            _bool_score(data.order_qty_mapping_defined),
        ),
        default=45,
    )
    risks: list[AlpacaPaperAdapterRisk] = []
    if (
        data.order_symbol_mapping_defined is not True
        or data.order_side_mapping_defined is not True
        or data.order_type_mapping_defined is not True
        or data.order_qty_mapping_defined is not True
        or score < 85
    ):
        risks.append(AlpacaPaperAdapterRisk.ORDER_MAPPING_FAILURE)
    if data.order_time_in_force_mapping_defined is not True:
        risks.append(AlpacaPaperAdapterRisk.CONFIGURATION_ERROR)
    evidence = (
        f"order_mapping_score={score}/100",
        f"order_symbol_mapping_defined={data.order_symbol_mapping_defined}",
        f"order_side_mapping_defined={data.order_side_mapping_defined}",
        f"order_type_mapping_defined={data.order_type_mapping_defined}",
        f"order_time_in_force_mapping_defined={data.order_time_in_force_mapping_defined}",
        f"order_qty_mapping_defined={data.order_qty_mapping_defined}",
    )
    return AlpacaPaperAdapterReviewSection("order_mapping_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_position_mapping(
    data: AlpacaPaperAdapterInput | Mapping[str, Any],
) -> AlpacaPaperAdapterReviewSection:
    """Verify AGIcore position fields map to an Alpaca Paper position model."""

    data = _coerce_input(data)
    score = _clamp(data.position_mapping_score) if data.position_mapping_score is not None else _average(
        (
            _bool_score(data.position_symbol_mapping_defined),
            _bool_score(data.position_qty_mapping_defined),
            _bool_score(data.position_avg_entry_mapping_defined),
            _bool_score(data.position_market_value_mapping_defined),
            _bool_score(data.position_unrealized_pnl_mapping_defined),
        ),
        default=45,
    )
    risks: list[AlpacaPaperAdapterRisk] = []
    if (
        data.position_symbol_mapping_defined is not True
        or data.position_qty_mapping_defined is not True
        or data.position_avg_entry_mapping_defined is not True
        or data.position_market_value_mapping_defined is not True
        or data.position_unrealized_pnl_mapping_defined is not True
        or score < 85
    ):
        risks.append(AlpacaPaperAdapterRisk.POSITION_MAPPING_FAILURE)
    evidence = (
        f"position_mapping_score={score}/100",
        f"position_symbol_mapping_defined={data.position_symbol_mapping_defined}",
        f"position_qty_mapping_defined={data.position_qty_mapping_defined}",
        f"position_avg_entry_mapping_defined={data.position_avg_entry_mapping_defined}",
        f"position_market_value_mapping_defined={data.position_market_value_mapping_defined}",
        f"position_unrealized_pnl_mapping_defined={data.position_unrealized_pnl_mapping_defined}",
    )
    return AlpacaPaperAdapterReviewSection("position_mapping_review", score, not risks and score >= 85, tuple(risks), evidence)


def verify_paper_order_translation(
    data: AlpacaPaperAdapterInput | Mapping[str, Any],
) -> AlpacaPaperAdapterReviewSection:
    """Verify paper order translation remains offline, safe and deterministic."""

    data = _coerce_input(data)
    score = (
        _clamp(data.paper_order_translation_score)
        if data.paper_order_translation_score is not None
        else _average(
            (
                _bool_score(data.paper_order_translation_defined),
                _bool_score(data.paper_order_validation_defined),
                _bool_score(data.paper_order_idempotency_defined),
                _bool_score(data.paper_order_network_disabled),
                _bool_score(data.paper_order_routing_blocked),
                _upstream_score(data, "adapter_score"),
            ),
            default=45,
        )
    )
    risks: list[AlpacaPaperAdapterRisk] = []
    if (
        data.paper_order_translation_defined is not True
        or data.paper_order_validation_defined is not True
        or score < 85
    ):
        risks.append(AlpacaPaperAdapterRisk.PAPER_TRANSLATION_FAILURE)
    if data.paper_order_network_disabled is not True or data.paper_order_routing_blocked is not True:
        risks.append(AlpacaPaperAdapterRisk.UNSAFE_ORDER_ROUTING)
    if data.paper_order_idempotency_defined is not True:
        risks.append(AlpacaPaperAdapterRisk.PAPER_STATE_DRIFT)
    evidence = (
        f"paper_order_translation_score={score}/100",
        f"paper_order_translation_defined={data.paper_order_translation_defined}",
        f"paper_order_validation_defined={data.paper_order_validation_defined}",
        f"paper_order_idempotency_defined={data.paper_order_idempotency_defined}",
        f"paper_order_network_disabled={data.paper_order_network_disabled}",
        f"paper_order_routing_blocked={data.paper_order_routing_blocked}",
    )
    return AlpacaPaperAdapterReviewSection("paper_order_translation_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_paper_account_translation(
    data: AlpacaPaperAdapterInput | Mapping[str, Any],
) -> AlpacaPaperAdapterReviewSection:
    """Verify Alpaca Paper account payloads translate to AGIcore account state."""

    data = _coerce_input(data)
    score = (
        _clamp(data.paper_account_translation_score)
        if data.paper_account_translation_score is not None
        else _average(
            (
                _bool_score(data.paper_account_translation_defined),
                _bool_score(data.paper_account_reconciliation_defined),
                _bool_score(data.paper_account_state_checkpointed),
            ),
            default=45,
        )
    )
    risks: list[AlpacaPaperAdapterRisk] = []
    if data.paper_account_translation_defined is not True or score < 85:
        risks.append(AlpacaPaperAdapterRisk.PAPER_TRANSLATION_FAILURE)
    if data.paper_account_reconciliation_defined is not True or data.paper_account_state_checkpointed is not True:
        risks.append(AlpacaPaperAdapterRisk.PAPER_STATE_DRIFT)
    evidence = (
        f"paper_account_translation_score={score}/100",
        f"paper_account_translation_defined={data.paper_account_translation_defined}",
        f"paper_account_reconciliation_defined={data.paper_account_reconciliation_defined}",
        f"paper_account_state_checkpointed={data.paper_account_state_checkpointed}",
    )
    return AlpacaPaperAdapterReviewSection("paper_account_translation_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_paper_position_translation(
    data: AlpacaPaperAdapterInput | Mapping[str, Any],
) -> AlpacaPaperAdapterReviewSection:
    """Verify Alpaca Paper position payloads translate to AGIcore position state."""

    data = _coerce_input(data)
    score = (
        _clamp(data.paper_position_translation_score)
        if data.paper_position_translation_score is not None
        else _average(
            (
                _bool_score(data.paper_position_translation_defined),
                _bool_score(data.paper_position_reconciliation_defined),
                _bool_score(data.paper_position_state_checkpointed),
                _bool_score(data.deterministic_mapping_required),
            ),
            default=45,
        )
    )
    risks: list[AlpacaPaperAdapterRisk] = []
    if data.paper_position_translation_defined is not True or score < 85:
        risks.append(AlpacaPaperAdapterRisk.PAPER_TRANSLATION_FAILURE)
    if (
        data.paper_position_reconciliation_defined is not True
        or data.paper_position_state_checkpointed is not True
        or data.deterministic_mapping_required is not True
        or _has_upstream(data, "DRIFT")
    ):
        risks.append(AlpacaPaperAdapterRisk.PAPER_STATE_DRIFT)
    evidence = (
        f"paper_position_translation_score={score}/100",
        f"paper_position_translation_defined={data.paper_position_translation_defined}",
        f"paper_position_reconciliation_defined={data.paper_position_reconciliation_defined}",
        f"paper_position_state_checkpointed={data.paper_position_state_checkpointed}",
        f"deterministic_mapping_required={data.deterministic_mapping_required}",
    )
    return AlpacaPaperAdapterReviewSection("paper_position_translation_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def _adapter_safety_risks(data: AlpacaPaperAdapterInput) -> tuple[AlpacaPaperAdapterRisk, ...]:
    risks: list[AlpacaPaperAdapterRisk] = []
    observability_score = data.observability_score if data.observability_score is not None else _average(
        (
            _bool_score(data.observability_events_defined),
            _upstream_score(data, "observability_score"),
        )
    )
    if (
        data.offline_mode_enforced is not True
        or data.no_api_keys_required is not True
        or data.no_http_transport is not True
        or data.no_websocket_transport is not True
    ):
        risks.append(AlpacaPaperAdapterRisk.CONFIGURATION_ERROR)
    if data.paper_order_network_disabled is not True or data.paper_order_routing_blocked is not True:
        risks.append(AlpacaPaperAdapterRisk.UNSAFE_ORDER_ROUTING)
    if data.observability_events_defined is not True or observability_score < 80 or _has_upstream(data, "OBSERVABILITY"):
        risks.append(AlpacaPaperAdapterRisk.OBSERVABILITY_GAP)
    if data.rollback_linked is not True or _has_upstream(data, "ROLLBACK"):
        risks.append(AlpacaPaperAdapterRisk.ROLLBACK_INCOMPATIBILITY)
    if data.supervision_required is not True or _has_upstream(data, "SUPERVISION"):
        risks.append(AlpacaPaperAdapterRisk.SUPERVISION_BREAK)
    if data.paper_state_drift_monitoring_defined is not True or _has_upstream(data, "DRIFT"):
        risks.append(AlpacaPaperAdapterRisk.PAPER_STATE_DRIFT)
    return _dedupe(risks)


def _build_adapter_graph(risks: tuple[AlpacaPaperAdapterRisk, ...]) -> AlpacaPaperAdapterGraph:
    nodes = (
        "agicore_models",
        "alpaca_paper_models",
        "paper_translation",
        "adapter_safety",
        "observability_rollback",
        "end_to_end_paper",
    )
    edges = (
        ("agicore_models", "alpaca_paper_models", "maps_to"),
        ("alpaca_paper_models", "paper_translation", "translates"),
        ("paper_translation", "adapter_safety", "gated_by"),
        ("adapter_safety", "observability_rollback", "observed_by"),
        ("observability_rollback", "end_to_end_paper", "gates"),
    )
    blocked: list[tuple[str, str]] = []
    if (
        AlpacaPaperAdapterRisk.ACCOUNT_MAPPING_FAILURE in risks
        or AlpacaPaperAdapterRisk.ORDER_MAPPING_FAILURE in risks
        or AlpacaPaperAdapterRisk.POSITION_MAPPING_FAILURE in risks
    ):
        blocked.append(("agicore_models", "alpaca_paper_models"))
    if AlpacaPaperAdapterRisk.PAPER_TRANSLATION_FAILURE in risks:
        blocked.append(("alpaca_paper_models", "paper_translation"))
    if (
        AlpacaPaperAdapterRisk.UNSAFE_ORDER_ROUTING in risks
        or AlpacaPaperAdapterRisk.CONFIGURATION_ERROR in risks
    ):
        blocked.append(("paper_translation", "adapter_safety"))
    if (
        AlpacaPaperAdapterRisk.OBSERVABILITY_GAP in risks
        or AlpacaPaperAdapterRisk.ROLLBACK_INCOMPATIBILITY in risks
        or AlpacaPaperAdapterRisk.SUPERVISION_BREAK in risks
    ):
        blocked.append(("adapter_safety", "observability_rollback"))
    if AlpacaPaperAdapterRisk.PAPER_STATE_DRIFT in risks:
        blocked.append(("observability_rollback", "end_to_end_paper"))
    return AlpacaPaperAdapterGraph(
        nodes=nodes,
        edges=edges,
        ready_edges=(
            ("agicore_models", "alpaca_paper_models"),
            ("alpaca_paper_models", "paper_translation"),
            ("paper_translation", "adapter_safety"),
            ("adapter_safety", "observability_rollback"),
            ("observability_rollback", "end_to_end_paper"),
        ),
        blocked_edges=_dedupe(blocked),
    )


def detect_alpaca_adapter_risks(
    data: AlpacaPaperAdapterInput | Mapping[str, Any],
    account_mapping_review: AlpacaPaperAdapterReviewSection | None = None,
    order_mapping_review: AlpacaPaperAdapterReviewSection | None = None,
    position_mapping_review: AlpacaPaperAdapterReviewSection | None = None,
    paper_order_translation_review: AlpacaPaperAdapterReviewSection | None = None,
    paper_account_translation_review: AlpacaPaperAdapterReviewSection | None = None,
    paper_position_translation_review: AlpacaPaperAdapterReviewSection | None = None,
) -> tuple[AlpacaPaperAdapterRisk, ...]:
    """Detect risks that block the offline Alpaca Paper adapter."""

    data = _coerce_input(data)
    sections = (
        account_mapping_review or verify_account_mapping(data),
        order_mapping_review or verify_order_mapping(data),
        position_mapping_review or verify_position_mapping(data),
        paper_order_translation_review or verify_paper_order_translation(data),
        paper_account_translation_review or verify_paper_account_translation(data),
        paper_position_translation_review or verify_paper_position_translation(data),
    )
    risks: list[AlpacaPaperAdapterRisk] = []
    for section in sections:
        risks.extend(section.risks)
    risks.extend(_adapter_safety_risks(data))
    return _dedupe(risks)


def compute_alpaca_adapter_score(
    data: AlpacaPaperAdapterInput | Mapping[str, Any],
    risks: tuple[AlpacaPaperAdapterRisk, ...] = (),
    account_mapping_review: AlpacaPaperAdapterReviewSection | None = None,
    order_mapping_review: AlpacaPaperAdapterReviewSection | None = None,
    position_mapping_review: AlpacaPaperAdapterReviewSection | None = None,
    paper_order_translation_review: AlpacaPaperAdapterReviewSection | None = None,
    paper_account_translation_review: AlpacaPaperAdapterReviewSection | None = None,
    paper_position_translation_review: AlpacaPaperAdapterReviewSection | None = None,
) -> AlpacaPaperAdapterScore:
    """Compute Alpaca Paper adapter readiness score normalized to 0..100."""

    data = _coerce_input(data)
    account = account_mapping_review or verify_account_mapping(data)
    order = order_mapping_review or verify_order_mapping(data)
    position = position_mapping_review or verify_position_mapping(data)
    paper_order = paper_order_translation_review or verify_paper_order_translation(data)
    paper_account = paper_account_translation_review or verify_paper_account_translation(data)
    paper_position = paper_position_translation_review or verify_paper_position_translation(data)
    observability_score = data.observability_score if data.observability_score is not None else _average(
        (
            _bool_score(data.observability_events_defined),
            _upstream_score(data, "observability_score"),
        )
    )
    safety_score = data.adapter_safety_score if data.adapter_safety_score is not None else _average(
        (
            _bool_score(data.offline_mode_enforced),
            _bool_score(data.no_api_keys_required),
            _bool_score(data.no_http_transport),
            _bool_score(data.no_websocket_transport),
            _bool_score(data.rollback_linked),
            _bool_score(data.supervision_required),
            _bool_score(data.paper_state_drift_monitoring_defined),
            observability_score,
        ),
        default=45,
    )
    weighted = _weighted_average(
        (
            (account.score, 1.05),
            (order.score, 1.2),
            (position.score, 1.05),
            (paper_order.score, 1.25),
            (paper_account.score, 1.0),
            (paper_position.score, 1.0),
            (safety_score, 1.35),
            (observability_score, 0.8),
        )
    )
    penalty = min(72, len(set(risks)) * 7)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        AlpacaPaperAdapterRisk.ACCOUNT_MAPPING_FAILURE: 55,
        AlpacaPaperAdapterRisk.ORDER_MAPPING_FAILURE: 50,
        AlpacaPaperAdapterRisk.POSITION_MAPPING_FAILURE: 55,
        AlpacaPaperAdapterRisk.PAPER_TRANSLATION_FAILURE: 50,
        AlpacaPaperAdapterRisk.UNSAFE_ORDER_ROUTING: 45,
        AlpacaPaperAdapterRisk.SUPERVISION_BREAK: 50,
        AlpacaPaperAdapterRisk.CONFIGURATION_ERROR: 45,
    }
    for risk, cap in critical_caps.items():
        if risk in risks:
            overall = min(overall, cap)
    return AlpacaPaperAdapterScore(
        overall_score=overall,
        account_mapping_score=account.score,
        order_mapping_score=order.score,
        position_mapping_score=position.score,
        paper_order_translation_score=paper_order.score,
        paper_account_translation_score=paper_account.score,
        paper_position_translation_score=paper_position.score,
        adapter_safety_score=_clamp(safety_score),
        observability_score=_clamp(observability_score),
    )


def _select_state(
    score: int,
    risks: tuple[AlpacaPaperAdapterRisk, ...],
    ready_for_end_to_end_paper: bool | None,
) -> AlpacaPaperAdapterState:
    count = len(set(risks))
    hard = {
        AlpacaPaperAdapterRisk.ORDER_MAPPING_FAILURE,
        AlpacaPaperAdapterRisk.PAPER_TRANSLATION_FAILURE,
        AlpacaPaperAdapterRisk.UNSAFE_ORDER_ROUTING,
        AlpacaPaperAdapterRisk.SUPERVISION_BREAK,
        AlpacaPaperAdapterRisk.CONFIGURATION_ERROR,
    }
    if hard.intersection(risks) or score < 45 or count >= 6:
        return AlpacaPaperAdapterState.NOT_READY
    if count >= 3 or score < 72:
        return AlpacaPaperAdapterState.REVIEW_REQUIRED
    if count:
        return AlpacaPaperAdapterState.PARTIALLY_READY
    if score >= 94 and ready_for_end_to_end_paper is True:
        return AlpacaPaperAdapterState.READY_FOR_END_TO_END_PAPER
    if score >= 88:
        return AlpacaPaperAdapterState.ADAPTER_READY
    return AlpacaPaperAdapterState.PARTIALLY_READY


def generate_alpaca_adapter_recommendations(
    risks: tuple[AlpacaPaperAdapterRisk, ...],
    state: AlpacaPaperAdapterState | None = None,
) -> tuple[AlpacaPaperAdapterRecommendation, ...]:
    """Generate Alpaca Paper adapter recommendations."""

    recommendations: list[AlpacaPaperAdapterRecommendation] = []
    if risks:
        recommendations.append(AlpacaPaperAdapterRecommendation.HOLD_END_TO_END_PAPER_APPROVAL)
    mapping = {
        AlpacaPaperAdapterRisk.ACCOUNT_MAPPING_FAILURE: AlpacaPaperAdapterRecommendation.FIX_ACCOUNT_MAPPING,
        AlpacaPaperAdapterRisk.ORDER_MAPPING_FAILURE: AlpacaPaperAdapterRecommendation.FIX_ORDER_MAPPING,
        AlpacaPaperAdapterRisk.POSITION_MAPPING_FAILURE: AlpacaPaperAdapterRecommendation.FIX_POSITION_MAPPING,
        AlpacaPaperAdapterRisk.PAPER_TRANSLATION_FAILURE: AlpacaPaperAdapterRecommendation.FIX_PAPER_TRANSLATION,
        AlpacaPaperAdapterRisk.UNSAFE_ORDER_ROUTING: AlpacaPaperAdapterRecommendation.BLOCK_UNSAFE_ORDER_ROUTING,
        AlpacaPaperAdapterRisk.OBSERVABILITY_GAP: AlpacaPaperAdapterRecommendation.ADD_ADAPTER_OBSERVABILITY,
        AlpacaPaperAdapterRisk.SUPERVISION_BREAK: AlpacaPaperAdapterRecommendation.RESTORE_SUPERVISION_CHAIN,
        AlpacaPaperAdapterRisk.ROLLBACK_INCOMPATIBILITY: AlpacaPaperAdapterRecommendation.LINK_ADAPTER_ROLLBACK,
        AlpacaPaperAdapterRisk.PAPER_STATE_DRIFT: AlpacaPaperAdapterRecommendation.LOCK_PAPER_STATE_DETERMINISM,
        AlpacaPaperAdapterRisk.CONFIGURATION_ERROR: AlpacaPaperAdapterRecommendation.FIX_ADAPTER_CONFIGURATION,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(AlpacaPaperAdapterRecommendation.RUN_ALPACA_ADAPTER_READINESS_SUITE)
    if state == AlpacaPaperAdapterState.READY_FOR_END_TO_END_PAPER:
        recommendations.append(AlpacaPaperAdapterRecommendation.APPROVE_END_TO_END_PAPER_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_alpaca_paper_adapter(
    data: AlpacaPaperAdapterInput | Mapping[str, Any],
) -> AlpacaPaperAdapterResult:
    """Evaluate whether the offline Alpaca Paper adapter model is ready."""

    data = _coerce_input(data)
    account = verify_account_mapping(data)
    order = verify_order_mapping(data)
    position = verify_position_mapping(data)
    paper_order = verify_paper_order_translation(data)
    paper_account = verify_paper_account_translation(data)
    paper_position = verify_paper_position_translation(data)
    risks = detect_alpaca_adapter_risks(data, account, order, position, paper_order, paper_account, paper_position)
    score = compute_alpaca_adapter_score(data, risks, account, order, position, paper_order, paper_account, paper_position)
    state = _select_state(score.overall_score, risks, data.ready_for_end_to_end_paper)
    graph = _build_adapter_graph(risks)
    recommendations = generate_alpaca_adapter_recommendations(risks, state)
    offline_only = (
        data.offline_mode_enforced is True
        and data.no_api_keys_required is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and not _has_upstream(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK")
    )
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return AlpacaPaperAdapterResult(
        state=state,
        alpaca_adapter_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        account_mapping_review=account,
        order_mapping_review=order,
        position_mapping_review=position,
        paper_order_translation_review=paper_order,
        paper_account_translation_review=paper_account,
        paper_position_translation_review=paper_position,
        adapter_graph=graph,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_alpaca_adapter_markdown(result: AlpacaPaperAdapterResult) -> str:
    """Render an explainable Alpaca Paper adapter readiness report."""

    lines = [
        "# AGIcore Alpaca Paper Adapter",
        f"- State: {result.state.value}",
        f"- Score: {result.alpaca_adapter_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Account mapping: {result.score_breakdown.account_mapping_score}/100",
        f"- Order mapping: {result.score_breakdown.order_mapping_score}/100",
        f"- Position mapping: {result.score_breakdown.position_mapping_score}/100",
        f"- Paper order translation: {result.score_breakdown.paper_order_translation_score}/100",
        f"- Paper account translation: {result.score_breakdown.paper_account_translation_score}/100",
        f"- Paper position translation: {result.score_breakdown.paper_position_translation_score}/100",
        f"- Adapter safety: {result.score_breakdown.adapter_safety_score}/100",
        f"- Observability: {result.score_breakdown.observability_score}/100",
        "",
        "# Alpaca Adapter Reviews",
    ]
    for section in (
        result.account_mapping_review,
        result.order_mapping_review,
        result.position_mapping_review,
        result.paper_order_translation_review,
        result.paper_account_translation_review,
        result.paper_position_translation_review,
    ):
        lines.append(
            f"- {section.name}: passed={section.passed}, score={section.score}/100, "
            f"risks={', '.join(risk.value for risk in section.risks) or 'none'}"
        )
        lines.extend(f"  - {item}" for item in section.evidence)
    lines.append("")
    lines.append("# Alpaca Adapter Graph")
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
    lines.append("# Alpaca Adapter Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Alpaca Adapter Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# Readiness Outlook")
    if result.state == AlpacaPaperAdapterState.READY_FOR_END_TO_END_PAPER:
        lines.append("- Alpaca Paper adapter model is ready for end-to-end paper preparation.")
    elif result.state == AlpacaPaperAdapterState.ADAPTER_READY:
        lines.append("- Alpaca Paper adapter model is ready; end-to-end paper remains gated.")
    elif result.state == AlpacaPaperAdapterState.PARTIALLY_READY:
        lines.append("- Alpaca Paper adapter model is partially ready and remaining risks must be resolved.")
    else:
        lines.append("- End-to-end paper approval should remain blocked.")
    return "\n".join(lines)


__all__ = [
    "compute_alpaca_adapter_score",
    "detect_alpaca_adapter_risks",
    "evaluate_alpaca_paper_adapter",
    "generate_alpaca_adapter_recommendations",
    "render_alpaca_adapter_markdown",
    "verify_account_mapping",
    "verify_order_mapping",
    "verify_paper_account_translation",
    "verify_paper_order_translation",
    "verify_paper_position_translation",
    "verify_position_mapping",
]
