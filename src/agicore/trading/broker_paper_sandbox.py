"""Offline-first broker paper sandbox readiness for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.broker_paper_sandbox_models import (
    BrokerPaperSandboxGraph,
    BrokerPaperSandboxInput,
    BrokerPaperSandboxRecommendation,
    BrokerPaperSandboxResult,
    BrokerPaperSandboxReviewSection,
    BrokerPaperSandboxRisk,
    BrokerPaperSandboxScore,
    BrokerPaperSandboxState,
)


def _coerce_input(data: BrokerPaperSandboxInput | Mapping[str, Any]) -> BrokerPaperSandboxInput:
    if isinstance(data, BrokerPaperSandboxInput):
        return data
    return BrokerPaperSandboxInput(**dict(data))


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


def _upstream_items(data: BrokerPaperSandboxInput) -> tuple[Any, ...]:
    return (
        data.supervised_paper_trial,
        data.paper_dry_run,
        data.paper_trading_end_to_end,
        data.alpaca_paper_adapter,
        data.paper_broker_adapter,
        data.supervised_paper_session,
        data.human_validated_paper_session,
        data.controlled_paper_run,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
    )


def _upstream_risks(data: BrokerPaperSandboxInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: BrokerPaperSandboxInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _upstream_score(data: BrokerPaperSandboxInput, *names: str) -> int | None:
    values: list[int] = []
    for item in _upstream_items(data):
        values.extend(_score(item, name) for name in names)
        breakdown = _get(item, "score_breakdown")
        values.extend(_score(breakdown, name) for name in names)
    values = [value for value in values if value is not None]
    return _average(values) if values else None


def verify_adapter_compatibility(data: BrokerPaperSandboxInput | Mapping[str, Any]) -> BrokerPaperSandboxReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.adapter_compatibility_score) if data.adapter_compatibility_score is not None else _average(
        (
            _bool_score(data.paper_broker_adapter_ready),
            _bool_score(data.alpaca_adapter_ready),
            _bool_score(data.adapter_contract_version_locked),
            _bool_score(data.sandbox_adapter_mode_enabled),
            _upstream_score(data, "adapter_score", "alpaca_adapter_score", "trial_score"),
        ),
        default=45,
    )
    risks: list[BrokerPaperSandboxRisk] = []
    if (
        data.paper_broker_adapter_ready is not True
        or data.alpaca_adapter_ready is not True
        or data.adapter_contract_version_locked is not True
        or data.sandbox_adapter_mode_enabled is not True
        or score < 85
        or _has_upstream_risk(data, "ADAPTER", "CONFIGURATION_ERROR")
    ):
        risks.append(BrokerPaperSandboxRisk.ADAPTER_INCOMPATIBILITY)
    evidence = (
        f"adapter_compatibility_score={score}/100",
        f"paper_broker_adapter_ready={data.paper_broker_adapter_ready}",
        f"alpaca_adapter_ready={data.alpaca_adapter_ready}",
        f"adapter_contract_version_locked={data.adapter_contract_version_locked}",
        f"sandbox_adapter_mode_enabled={data.sandbox_adapter_mode_enabled}",
    )
    return BrokerPaperSandboxReviewSection("adapter_compatibility_review", score, not risks and score >= 85, tuple(risks), evidence)


def verify_order_translation(data: BrokerPaperSandboxInput | Mapping[str, Any]) -> BrokerPaperSandboxReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.order_translation_score) if data.order_translation_score is not None else _average(
        (
            _bool_score(data.order_mapping_defined),
            _bool_score(data.order_validation_defined),
            _bool_score(data.order_idempotency_defined),
            _bool_score(data.order_routing_disabled),
            _upstream_score(data, "order_translation_score", "order_mapping_score", "paper_order_translation_score"),
        ),
        default=45,
    )
    risks: list[BrokerPaperSandboxRisk] = []
    if (
        data.order_mapping_defined is not True
        or data.order_validation_defined is not True
        or score < 85
        or _has_upstream_risk(data, "ORDER_TRANSLATION", "ORDER_MAPPING")
    ):
        risks.append(BrokerPaperSandboxRisk.ORDER_TRANSLATION_FAILURE)
    if data.order_idempotency_defined is not True:
        risks.append(BrokerPaperSandboxRisk.SANDBOX_CONFIGURATION_DRIFT)
    if data.order_routing_disabled is not True:
        risks.append(BrokerPaperSandboxRisk.EXTERNAL_DEPENDENCY_RISK)
    evidence = (
        f"order_translation_score={score}/100",
        f"order_mapping_defined={data.order_mapping_defined}",
        f"order_validation_defined={data.order_validation_defined}",
        f"order_idempotency_defined={data.order_idempotency_defined}",
        f"order_routing_disabled={data.order_routing_disabled}",
    )
    return BrokerPaperSandboxReviewSection("order_translation_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_position_translation(data: BrokerPaperSandboxInput | Mapping[str, Any]) -> BrokerPaperSandboxReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.position_translation_score) if data.position_translation_score is not None else _average(
        (
            _bool_score(data.position_mapping_defined),
            _bool_score(data.position_reconciliation_defined),
            _bool_score(data.position_checkpointing_defined),
            _bool_score(data.position_drift_monitoring_defined),
            _upstream_score(data, "position_translation_score", "position_mapping_score", "paper_position_translation_score"),
        ),
        default=45,
    )
    risks: list[BrokerPaperSandboxRisk] = []
    if (
        data.position_mapping_defined is not True
        or data.position_reconciliation_defined is not True
        or score < 85
        or _has_upstream_risk(data, "POSITION_TRANSLATION", "POSITION_MAPPING")
    ):
        risks.append(BrokerPaperSandboxRisk.POSITION_TRANSLATION_FAILURE)
    if data.position_checkpointing_defined is not True or data.position_drift_monitoring_defined is not True:
        risks.append(BrokerPaperSandboxRisk.SANDBOX_CONFIGURATION_DRIFT)
    evidence = (
        f"position_translation_score={score}/100",
        f"position_mapping_defined={data.position_mapping_defined}",
        f"position_reconciliation_defined={data.position_reconciliation_defined}",
        f"position_checkpointing_defined={data.position_checkpointing_defined}",
        f"position_drift_monitoring_defined={data.position_drift_monitoring_defined}",
    )
    return BrokerPaperSandboxReviewSection("position_translation_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_account_translation(data: BrokerPaperSandboxInput | Mapping[str, Any]) -> BrokerPaperSandboxReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.account_translation_score) if data.account_translation_score is not None else _average(
        (
            _bool_score(data.account_mapping_defined),
            _bool_score(data.account_reconciliation_defined),
            _bool_score(data.buying_power_mapping_defined),
            _bool_score(data.account_state_checkpointing_defined),
            _upstream_score(data, "account_translation_score", "account_mapping_score", "paper_account_translation_score"),
        ),
        default=45,
    )
    risks: list[BrokerPaperSandboxRisk] = []
    if (
        data.account_mapping_defined is not True
        or data.account_reconciliation_defined is not True
        or data.buying_power_mapping_defined is not True
        or score < 85
        or _has_upstream_risk(data, "ACCOUNT_TRANSLATION", "ACCOUNT_MAPPING")
    ):
        risks.append(BrokerPaperSandboxRisk.ACCOUNT_TRANSLATION_FAILURE)
    if data.account_state_checkpointing_defined is not True:
        risks.append(BrokerPaperSandboxRisk.SANDBOX_CONFIGURATION_DRIFT)
    evidence = (
        f"account_translation_score={score}/100",
        f"account_mapping_defined={data.account_mapping_defined}",
        f"account_reconciliation_defined={data.account_reconciliation_defined}",
        f"buying_power_mapping_defined={data.buying_power_mapping_defined}",
        f"account_state_checkpointing_defined={data.account_state_checkpointing_defined}",
    )
    return BrokerPaperSandboxReviewSection("account_translation_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_safety_boundaries(data: BrokerPaperSandboxInput | Mapping[str, Any]) -> BrokerPaperSandboxReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.safety_boundary_score) if data.safety_boundary_score is not None else _average(
        (
            _bool_score(data.safety_prechecks_required),
            _bool_score(data.sandbox_order_limits_defined),
            _bool_score(data.no_live_order_route),
            _bool_score(data.no_api_keys_required),
            _upstream_score(data, "adapter_safety_score", "safety_gate_score"),
        ),
        default=45,
    )
    risks: list[BrokerPaperSandboxRisk] = []
    if (
        data.safety_prechecks_required is not True
        or data.sandbox_order_limits_defined is not True
        or score < 85
        or _has_upstream_risk(data, "SAFETY")
    ):
        risks.append(BrokerPaperSandboxRisk.SAFETY_BOUNDARY_MISSING)
    if data.no_live_order_route is not True or data.no_api_keys_required is not True:
        risks.append(BrokerPaperSandboxRisk.EXTERNAL_DEPENDENCY_RISK)
    evidence = (
        f"safety_boundary_score={score}/100",
        f"safety_prechecks_required={data.safety_prechecks_required}",
        f"sandbox_order_limits_defined={data.sandbox_order_limits_defined}",
        f"no_live_order_route={data.no_live_order_route}",
        f"no_api_keys_required={data.no_api_keys_required}",
    )
    return BrokerPaperSandboxReviewSection("safety_boundaries_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_observability_boundaries(data: BrokerPaperSandboxInput | Mapping[str, Any]) -> BrokerPaperSandboxReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.observability_boundary_score) if data.observability_boundary_score is not None else _average(
        (
            _bool_score(data.observability_events_defined),
            _bool_score(data.sandbox_metrics_defined),
            _bool_score(data.audit_trail_defined),
            _bool_score(data.critical_alerts_defined),
            _upstream_score(data, "observability_score"),
        ),
        default=45,
    )
    risks: list[BrokerPaperSandboxRisk] = []
    if (
        data.observability_events_defined is not True
        or data.sandbox_metrics_defined is not True
        or data.audit_trail_defined is not True
        or data.critical_alerts_defined is not True
        or score < 85
        or _has_upstream_risk(data, "OBSERVABILITY")
    ):
        risks.append(BrokerPaperSandboxRisk.OBSERVABILITY_BOUNDARY_MISSING)
    evidence = (
        f"observability_boundary_score={score}/100",
        f"observability_events_defined={data.observability_events_defined}",
        f"sandbox_metrics_defined={data.sandbox_metrics_defined}",
        f"audit_trail_defined={data.audit_trail_defined}",
        f"critical_alerts_defined={data.critical_alerts_defined}",
    )
    return BrokerPaperSandboxReviewSection("observability_boundaries_review", score, not risks and score >= 85, tuple(risks), evidence)


def verify_kill_switch_boundaries(data: BrokerPaperSandboxInput | Mapping[str, Any]) -> BrokerPaperSandboxReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.kill_switch_boundary_score) if data.kill_switch_boundary_score is not None else _average(
        (
            _bool_score(data.kill_switch_linked),
            _bool_score(data.emergency_stop_path_defined),
            _bool_score(data.operator_halt_required),
            _bool_score(data.post_halt_state_safe),
            _upstream_score(data, "kill_switch_score"),
        ),
        default=45,
    )
    risks: list[BrokerPaperSandboxRisk] = []
    if (
        data.kill_switch_linked is not True
        or data.emergency_stop_path_defined is not True
        or data.operator_halt_required is not True
        or data.post_halt_state_safe is not True
        or score < 85
        or _has_upstream_risk(data, "KILL_SWITCH")
    ):
        risks.append(BrokerPaperSandboxRisk.KILL_SWITCH_BOUNDARY_MISSING)
    evidence = (
        f"kill_switch_boundary_score={score}/100",
        f"kill_switch_linked={data.kill_switch_linked}",
        f"emergency_stop_path_defined={data.emergency_stop_path_defined}",
        f"operator_halt_required={data.operator_halt_required}",
        f"post_halt_state_safe={data.post_halt_state_safe}",
    )
    return BrokerPaperSandboxReviewSection("kill_switch_boundaries_review", score, not risks and score >= 85, tuple(risks), evidence)


def verify_rollback_boundaries(data: BrokerPaperSandboxInput | Mapping[str, Any]) -> BrokerPaperSandboxReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.rollback_boundary_score) if data.rollback_boundary_score is not None else _average(
        (
            _bool_score(data.rollback_linked),
            _bool_score(data.recovery_point_required),
            _bool_score(data.rollback_audit_defined),
            _bool_score(data.restart_guard_defined),
            _upstream_score(data, "rollback_score"),
        ),
        default=45,
    )
    risks: list[BrokerPaperSandboxRisk] = []
    if (
        data.rollback_linked is not True
        or data.recovery_point_required is not True
        or data.rollback_audit_defined is not True
        or data.restart_guard_defined is not True
        or score < 85
        or _has_upstream_risk(data, "ROLLBACK")
    ):
        risks.append(BrokerPaperSandboxRisk.ROLLBACK_BOUNDARY_MISSING)
    evidence = (
        f"rollback_boundary_score={score}/100",
        f"rollback_linked={data.rollback_linked}",
        f"recovery_point_required={data.recovery_point_required}",
        f"rollback_audit_defined={data.rollback_audit_defined}",
        f"restart_guard_defined={data.restart_guard_defined}",
    )
    return BrokerPaperSandboxReviewSection("rollback_boundaries_review", score, not risks and score >= 85, tuple(risks), evidence)


def detect_sandbox_risks(
    data: BrokerPaperSandboxInput | Mapping[str, Any],
    adapter_compatibility_review: BrokerPaperSandboxReviewSection | None = None,
    order_translation_review: BrokerPaperSandboxReviewSection | None = None,
    position_translation_review: BrokerPaperSandboxReviewSection | None = None,
    account_translation_review: BrokerPaperSandboxReviewSection | None = None,
    safety_boundaries_review: BrokerPaperSandboxReviewSection | None = None,
    observability_boundaries_review: BrokerPaperSandboxReviewSection | None = None,
    kill_switch_boundaries_review: BrokerPaperSandboxReviewSection | None = None,
    rollback_boundaries_review: BrokerPaperSandboxReviewSection | None = None,
) -> tuple[BrokerPaperSandboxRisk, ...]:
    data = _coerce_input(data)
    sections = (
        adapter_compatibility_review or verify_adapter_compatibility(data),
        order_translation_review or verify_order_translation(data),
        position_translation_review or verify_position_translation(data),
        account_translation_review or verify_account_translation(data),
        safety_boundaries_review or verify_safety_boundaries(data),
        observability_boundaries_review or verify_observability_boundaries(data),
        kill_switch_boundaries_review or verify_kill_switch_boundaries(data),
        rollback_boundaries_review or verify_rollback_boundaries(data),
    )
    risks: list[BrokerPaperSandboxRisk] = []
    for section in sections:
        risks.extend(section.risks)
    if data.configuration_locked is not True:
        risks.append(BrokerPaperSandboxRisk.SANDBOX_CONFIGURATION_DRIFT)
    if (
        data.offline_mode_enforced is not True
        or data.no_http_transport is not True
        or data.no_websocket_transport is not True
        or data.no_socket_transport is not True
        or data.external_dependencies_blocked is not True
        or _has_upstream_risk(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK")
    ):
        risks.append(BrokerPaperSandboxRisk.EXTERNAL_DEPENDENCY_RISK)
    return _dedupe(risks)


def compute_sandbox_score(
    data: BrokerPaperSandboxInput | Mapping[str, Any],
    risks: tuple[BrokerPaperSandboxRisk, ...] = (),
    adapter_compatibility_review: BrokerPaperSandboxReviewSection | None = None,
    order_translation_review: BrokerPaperSandboxReviewSection | None = None,
    position_translation_review: BrokerPaperSandboxReviewSection | None = None,
    account_translation_review: BrokerPaperSandboxReviewSection | None = None,
    safety_boundaries_review: BrokerPaperSandboxReviewSection | None = None,
    observability_boundaries_review: BrokerPaperSandboxReviewSection | None = None,
    kill_switch_boundaries_review: BrokerPaperSandboxReviewSection | None = None,
    rollback_boundaries_review: BrokerPaperSandboxReviewSection | None = None,
) -> BrokerPaperSandboxScore:
    data = _coerce_input(data)
    adapter = adapter_compatibility_review or verify_adapter_compatibility(data)
    order = order_translation_review or verify_order_translation(data)
    position = position_translation_review or verify_position_translation(data)
    account = account_translation_review or verify_account_translation(data)
    safety = safety_boundaries_review or verify_safety_boundaries(data)
    observability = observability_boundaries_review or verify_observability_boundaries(data)
    kill_switch = kill_switch_boundaries_review or verify_kill_switch_boundaries(data)
    rollback = rollback_boundaries_review or verify_rollback_boundaries(data)
    weighted = _weighted_average(
        (
            (adapter.score, 1.2),
            (order.score, 1.2),
            (position.score, 1.0),
            (account.score, 1.0),
            (safety.score, 1.3),
            (observability.score, 1.0),
            (kill_switch.score, 1.15),
            (rollback.score, 1.1),
        )
    )
    penalty = min(72, len(set(risks)) * 6)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        BrokerPaperSandboxRisk.ADAPTER_INCOMPATIBILITY: 45,
        BrokerPaperSandboxRisk.ORDER_TRANSLATION_FAILURE: 50,
        BrokerPaperSandboxRisk.SAFETY_BOUNDARY_MISSING: 40,
        BrokerPaperSandboxRisk.KILL_SWITCH_BOUNDARY_MISSING: 45,
        BrokerPaperSandboxRisk.EXTERNAL_DEPENDENCY_RISK: 40,
    }
    for risk, cap in critical_caps.items():
        if risk in risks:
            overall = min(overall, cap)
    return BrokerPaperSandboxScore(
        overall_score=overall,
        adapter_compatibility_score=adapter.score,
        order_translation_score=order.score,
        position_translation_score=position.score,
        account_translation_score=account.score,
        safety_boundary_score=safety.score,
        observability_boundary_score=observability.score,
        kill_switch_boundary_score=kill_switch.score,
        rollback_boundary_score=rollback.score,
    )


def _build_graph(risks: tuple[BrokerPaperSandboxRisk, ...]) -> BrokerPaperSandboxGraph:
    nodes = ("adapter", "order", "position", "account", "safety", "observability", "kill_switch", "rollback", "sandbox")
    edges = (
        ("adapter", "order", "translates"),
        ("adapter", "position", "maps"),
        ("adapter", "account", "maps"),
        ("safety", "order", "bounds"),
        ("observability", "sandbox", "reports"),
        ("kill_switch", "sandbox", "halts"),
        ("rollback", "sandbox", "restores"),
    )
    blocked: list[tuple[str, str]] = []
    if BrokerPaperSandboxRisk.ADAPTER_INCOMPATIBILITY in risks:
        blocked.extend((("adapter", "order"), ("adapter", "position"), ("adapter", "account")))
    if BrokerPaperSandboxRisk.ORDER_TRANSLATION_FAILURE in risks:
        blocked.append(("adapter", "order"))
    if BrokerPaperSandboxRisk.POSITION_TRANSLATION_FAILURE in risks:
        blocked.append(("adapter", "position"))
    if BrokerPaperSandboxRisk.ACCOUNT_TRANSLATION_FAILURE in risks:
        blocked.append(("adapter", "account"))
    if BrokerPaperSandboxRisk.SAFETY_BOUNDARY_MISSING in risks:
        blocked.append(("safety", "order"))
    if BrokerPaperSandboxRisk.OBSERVABILITY_BOUNDARY_MISSING in risks:
        blocked.append(("observability", "sandbox"))
    if BrokerPaperSandboxRisk.KILL_SWITCH_BOUNDARY_MISSING in risks:
        blocked.append(("kill_switch", "sandbox"))
    if BrokerPaperSandboxRisk.ROLLBACK_BOUNDARY_MISSING in risks:
        blocked.append(("rollback", "sandbox"))
    return BrokerPaperSandboxGraph(nodes, edges, tuple((a, b) for a, b, _ in edges), _dedupe(blocked))


def _select_state(score: int, risks: tuple[BrokerPaperSandboxRisk, ...], sandbox_validated: bool | None, ready_for_connectivity: bool | None) -> BrokerPaperSandboxState:
    hard = {
        BrokerPaperSandboxRisk.ADAPTER_INCOMPATIBILITY,
        BrokerPaperSandboxRisk.ORDER_TRANSLATION_FAILURE,
        BrokerPaperSandboxRisk.SAFETY_BOUNDARY_MISSING,
        BrokerPaperSandboxRisk.KILL_SWITCH_BOUNDARY_MISSING,
        BrokerPaperSandboxRisk.EXTERNAL_DEPENDENCY_RISK,
    }
    count = len(set(risks))
    if hard.intersection(risks) or score < 45 or count >= 6:
        return BrokerPaperSandboxState.NOT_READY
    if count >= 3 or score < 72:
        return BrokerPaperSandboxState.REVIEW_REQUIRED
    if count:
        return BrokerPaperSandboxState.PARTIALLY_READY
    if sandbox_validated is True and ready_for_connectivity is True and score >= 94:
        return BrokerPaperSandboxState.READY_FOR_ALPACA_PAPER_CONNECTIVITY
    if sandbox_validated is True and score >= 90:
        return BrokerPaperSandboxState.SANDBOX_VALIDATED
    if score >= 85:
        return BrokerPaperSandboxState.SANDBOX_READY
    return BrokerPaperSandboxState.PARTIALLY_READY


def generate_sandbox_recommendations(
    risks: tuple[BrokerPaperSandboxRisk, ...],
    state: BrokerPaperSandboxState | None = None,
) -> tuple[BrokerPaperSandboxRecommendation, ...]:
    recommendations: list[BrokerPaperSandboxRecommendation] = []
    if risks:
        recommendations.append(BrokerPaperSandboxRecommendation.HOLD_ALPACA_CONNECTIVITY_APPROVAL)
    mapping = {
        BrokerPaperSandboxRisk.ADAPTER_INCOMPATIBILITY: BrokerPaperSandboxRecommendation.REPAIR_ADAPTER_COMPATIBILITY,
        BrokerPaperSandboxRisk.ORDER_TRANSLATION_FAILURE: BrokerPaperSandboxRecommendation.REPAIR_ORDER_TRANSLATION,
        BrokerPaperSandboxRisk.POSITION_TRANSLATION_FAILURE: BrokerPaperSandboxRecommendation.REPAIR_POSITION_TRANSLATION,
        BrokerPaperSandboxRisk.ACCOUNT_TRANSLATION_FAILURE: BrokerPaperSandboxRecommendation.REPAIR_ACCOUNT_TRANSLATION,
        BrokerPaperSandboxRisk.SAFETY_BOUNDARY_MISSING: BrokerPaperSandboxRecommendation.DEFINE_SAFETY_BOUNDARY,
        BrokerPaperSandboxRisk.OBSERVABILITY_BOUNDARY_MISSING: BrokerPaperSandboxRecommendation.DEFINE_OBSERVABILITY_BOUNDARY,
        BrokerPaperSandboxRisk.KILL_SWITCH_BOUNDARY_MISSING: BrokerPaperSandboxRecommendation.DEFINE_KILL_SWITCH_BOUNDARY,
        BrokerPaperSandboxRisk.ROLLBACK_BOUNDARY_MISSING: BrokerPaperSandboxRecommendation.DEFINE_ROLLBACK_BOUNDARY,
        BrokerPaperSandboxRisk.SANDBOX_CONFIGURATION_DRIFT: BrokerPaperSandboxRecommendation.LOCK_SANDBOX_CONFIGURATION,
        BrokerPaperSandboxRisk.EXTERNAL_DEPENDENCY_RISK: BrokerPaperSandboxRecommendation.REMOVE_EXTERNAL_DEPENDENCY,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(BrokerPaperSandboxRecommendation.RUN_BROKER_PAPER_SANDBOX_SUITE)
    if state == BrokerPaperSandboxState.READY_FOR_ALPACA_PAPER_CONNECTIVITY:
        recommendations.append(BrokerPaperSandboxRecommendation.APPROVE_ALPACA_PAPER_CONNECTIVITY_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_broker_paper_sandbox(data: BrokerPaperSandboxInput | Mapping[str, Any]) -> BrokerPaperSandboxResult:
    data = _coerce_input(data)
    adapter = verify_adapter_compatibility(data)
    order = verify_order_translation(data)
    position = verify_position_translation(data)
    account = verify_account_translation(data)
    safety = verify_safety_boundaries(data)
    observability = verify_observability_boundaries(data)
    kill_switch = verify_kill_switch_boundaries(data)
    rollback = verify_rollback_boundaries(data)
    risks = detect_sandbox_risks(data, adapter, order, position, account, safety, observability, kill_switch, rollback)
    score = compute_sandbox_score(data, risks, adapter, order, position, account, safety, observability, kill_switch, rollback)
    state = _select_state(score.overall_score, risks, data.sandbox_validated, data.ready_for_alpaca_paper_connectivity)
    graph = _build_graph(risks)
    recommendations = generate_sandbox_recommendations(risks, state)
    offline_only = (
        data.offline_mode_enforced is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.external_dependencies_blocked is True
        and not _has_upstream_risk(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK")
    )
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return BrokerPaperSandboxResult(
        state=state,
        sandbox_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        adapter_compatibility_review=adapter,
        order_translation_review=order,
        position_translation_review=position,
        account_translation_review=account,
        safety_boundaries_review=safety,
        observability_boundaries_review=observability,
        kill_switch_boundaries_review=kill_switch,
        rollback_boundaries_review=rollback,
        sandbox_graph=graph,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_broker_paper_sandbox_markdown(result: BrokerPaperSandboxResult) -> str:
    lines = [
        "# AGIcore Broker Paper Sandbox",
        f"- State: {result.state.value}",
        f"- Score: {result.sandbox_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Adapter compatibility: {result.score_breakdown.adapter_compatibility_score}/100",
        f"- Order translation: {result.score_breakdown.order_translation_score}/100",
        f"- Position translation: {result.score_breakdown.position_translation_score}/100",
        f"- Account translation: {result.score_breakdown.account_translation_score}/100",
        f"- Safety boundary: {result.score_breakdown.safety_boundary_score}/100",
        f"- Observability boundary: {result.score_breakdown.observability_boundary_score}/100",
        f"- Kill switch boundary: {result.score_breakdown.kill_switch_boundary_score}/100",
        f"- Rollback boundary: {result.score_breakdown.rollback_boundary_score}/100",
        "",
        "# Sandbox Reviews",
    ]
    sections = (
        result.adapter_compatibility_review,
        result.order_translation_review,
        result.position_translation_review,
        result.account_translation_review,
        result.safety_boundaries_review,
        result.observability_boundaries_review,
        result.kill_switch_boundaries_review,
        result.rollback_boundaries_review,
    )
    for section in sections:
        lines.append(
            f"- {section.name}: passed={section.passed}, score={section.score}/100, "
            f"risks={', '.join(risk.value for risk in section.risks) or 'none'}"
        )
        lines.extend(f"  - {item}" for item in section.evidence)
    lines.extend(
        (
            "",
            "# Sandbox Graph",
            f"- Nodes: {', '.join(result.sandbox_graph.nodes)}",
        )
    )
    lines.extend(f"- Edge: {source} -> {target} ({label})" for source, target, label in result.sandbox_graph.edges)
    lines.append(
        "- Blocked edges: "
        + (", ".join(f"{source}->{target}" for source, target in result.sandbox_graph.blocked_edges) or "none")
    )
    lines.append("")
    lines.append("# Sandbox Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Sandbox Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_sandbox_score",
    "detect_sandbox_risks",
    "evaluate_broker_paper_sandbox",
    "generate_sandbox_recommendations",
    "render_broker_paper_sandbox_markdown",
    "verify_account_translation",
    "verify_adapter_compatibility",
    "verify_kill_switch_boundaries",
    "verify_observability_boundaries",
    "verify_order_translation",
    "verify_position_translation",
    "verify_rollback_boundaries",
    "verify_safety_boundaries",
]
