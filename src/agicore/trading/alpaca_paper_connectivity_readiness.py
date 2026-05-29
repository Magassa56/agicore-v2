"""Offline Alpaca Paper connectivity readiness for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.alpaca_paper_connectivity_readiness_models import (
    AlpacaPaperConnectivityGraph,
    AlpacaPaperConnectivityInput,
    AlpacaPaperConnectivityRecommendation,
    AlpacaPaperConnectivityResult,
    AlpacaPaperConnectivityReviewSection,
    AlpacaPaperConnectivityRisk,
    AlpacaPaperConnectivityScore,
    AlpacaPaperConnectivityState,
)


def _coerce_input(data: AlpacaPaperConnectivityInput | Mapping[str, Any]) -> AlpacaPaperConnectivityInput:
    if isinstance(data, AlpacaPaperConnectivityInput):
        return data
    return AlpacaPaperConnectivityInput(**dict(data))


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


def _upstream_items(data: AlpacaPaperConnectivityInput) -> tuple[Any, ...]:
    return (
        data.broker_paper_sandbox,
        data.alpaca_paper_adapter,
        data.paper_trading_end_to_end,
        data.paper_dry_run,
        data.supervised_paper_trial,
        data.observability_verification,
        data.kill_switch_verification,
        data.rollback_verification,
    )


def _upstream_risks(data: AlpacaPaperConnectivityInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: AlpacaPaperConnectivityInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _upstream_score(data: AlpacaPaperConnectivityInput, *names: str) -> int | None:
    values: list[int] = []
    for item in _upstream_items(data):
        values.extend(_score(item, name) for name in names)
        breakdown = _get(item, "score_breakdown")
        values.extend(_score(breakdown, name) for name in names)
    values = [value for value in values if value is not None]
    return _average(values) if values else None


def verify_credentials_requirements(data: AlpacaPaperConnectivityInput | Mapping[str, Any]) -> AlpacaPaperConnectivityReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.credentials_score) if data.credentials_score is not None else _average(
        (
            _bool_score(data.credential_schema_defined),
            _bool_score(data.credential_storage_externalized),
            _bool_score(data.no_real_credentials_loaded),
            _bool_score(data.paper_account_scope_defined),
        ),
        default=45,
    )
    risks: list[AlpacaPaperConnectivityRisk] = []
    if (
        data.credential_schema_defined is not True
        or data.credential_storage_externalized is not True
        or data.paper_account_scope_defined is not True
        or score < 85
    ):
        risks.append(AlpacaPaperConnectivityRisk.MISSING_CREDENTIALS)
    if data.no_real_credentials_loaded is not True:
        risks.append(AlpacaPaperConnectivityRisk.UNSAFE_CONNECTIVITY_CONFIGURATION)
    evidence = (
        f"credentials_score={score}/100",
        f"credential_schema_defined={data.credential_schema_defined}",
        f"credential_storage_externalized={data.credential_storage_externalized}",
        f"no_real_credentials_loaded={data.no_real_credentials_loaded}",
        f"paper_account_scope_defined={data.paper_account_scope_defined}",
    )
    return AlpacaPaperConnectivityReviewSection("credentials_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_endpoint_requirements(data: AlpacaPaperConnectivityInput | Mapping[str, Any]) -> AlpacaPaperConnectivityReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.endpoint_score) if data.endpoint_score is not None else _average(
        (
            _bool_score(data.paper_endpoint_config_defined),
            _bool_score(data.endpoint_environment_locked),
            _bool_score(data.endpoint_allowlist_defined),
            _bool_score(data.live_endpoint_blocked),
            _upstream_score(data, "sandbox_score"),
        ),
        default=45,
    )
    risks: list[AlpacaPaperConnectivityRisk] = []
    if (
        data.paper_endpoint_config_defined is not True
        or data.endpoint_environment_locked is not True
        or data.endpoint_allowlist_defined is not True
        or score < 85
    ):
        risks.append(AlpacaPaperConnectivityRisk.INVALID_ENDPOINT_CONFIGURATION)
    if data.live_endpoint_blocked is not True:
        risks.append(AlpacaPaperConnectivityRisk.UNSAFE_CONNECTIVITY_CONFIGURATION)
    evidence = (
        f"endpoint_score={score}/100",
        f"paper_endpoint_config_defined={data.paper_endpoint_config_defined}",
        f"endpoint_environment_locked={data.endpoint_environment_locked}",
        f"endpoint_allowlist_defined={data.endpoint_allowlist_defined}",
        f"live_endpoint_blocked={data.live_endpoint_blocked}",
    )
    return AlpacaPaperConnectivityReviewSection("endpoint_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_rate_limit_requirements(data: AlpacaPaperConnectivityInput | Mapping[str, Any]) -> AlpacaPaperConnectivityReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.rate_limit_score) if data.rate_limit_score is not None else _average(
        (
            _bool_score(data.rate_limit_budget_defined),
            _bool_score(data.request_throttle_defined),
            _bool_score(data.burst_guard_defined),
            _bool_score(data.rate_limit_observability_defined),
        ),
        default=45,
    )
    risks: list[AlpacaPaperConnectivityRisk] = []
    if (
        data.rate_limit_budget_defined is not True
        or data.request_throttle_defined is not True
        or data.burst_guard_defined is not True
        or data.rate_limit_observability_defined is not True
        or score < 85
    ):
        risks.append(AlpacaPaperConnectivityRisk.RATE_LIMIT_EXPOSURE)
    evidence = (
        f"rate_limit_score={score}/100",
        f"rate_limit_budget_defined={data.rate_limit_budget_defined}",
        f"request_throttle_defined={data.request_throttle_defined}",
        f"burst_guard_defined={data.burst_guard_defined}",
        f"rate_limit_observability_defined={data.rate_limit_observability_defined}",
    )
    return AlpacaPaperConnectivityReviewSection("rate_limit_review", score, not risks and score >= 85, tuple(risks), evidence)


def verify_retry_requirements(data: AlpacaPaperConnectivityInput | Mapping[str, Any]) -> AlpacaPaperConnectivityReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.retry_score) if data.retry_score is not None else _average(
        (
            _bool_score(data.retry_policy_defined),
            _bool_score(data.retry_backoff_defined),
            _bool_score(data.retry_idempotency_defined),
            _bool_score(data.retry_stop_condition_defined),
        ),
        default=45,
    )
    risks: list[AlpacaPaperConnectivityRisk] = []
    if (
        data.retry_policy_defined is not True
        or data.retry_backoff_defined is not True
        or data.retry_idempotency_defined is not True
        or data.retry_stop_condition_defined is not True
        or score < 85
    ):
        risks.append(AlpacaPaperConnectivityRisk.RETRY_POLICY_MISSING)
    evidence = (
        f"retry_score={score}/100",
        f"retry_policy_defined={data.retry_policy_defined}",
        f"retry_backoff_defined={data.retry_backoff_defined}",
        f"retry_idempotency_defined={data.retry_idempotency_defined}",
        f"retry_stop_condition_defined={data.retry_stop_condition_defined}",
    )
    return AlpacaPaperConnectivityReviewSection("retry_review", score, not risks and score >= 85, tuple(risks), evidence)


def verify_timeout_requirements(data: AlpacaPaperConnectivityInput | Mapping[str, Any]) -> AlpacaPaperConnectivityReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.timeout_score) if data.timeout_score is not None else _average(
        (
            _bool_score(data.timeout_policy_defined),
            _bool_score(data.connect_timeout_defined),
            _bool_score(data.read_timeout_defined),
            _bool_score(data.timeout_fail_closed),
        ),
        default=45,
    )
    risks: list[AlpacaPaperConnectivityRisk] = []
    if (
        data.timeout_policy_defined is not True
        or data.connect_timeout_defined is not True
        or data.read_timeout_defined is not True
        or score < 85
    ):
        risks.append(AlpacaPaperConnectivityRisk.TIMEOUT_EXPOSURE)
    if data.timeout_fail_closed is not True:
        risks.append(AlpacaPaperConnectivityRisk.UNSAFE_CONNECTIVITY_CONFIGURATION)
    evidence = (
        f"timeout_score={score}/100",
        f"timeout_policy_defined={data.timeout_policy_defined}",
        f"connect_timeout_defined={data.connect_timeout_defined}",
        f"read_timeout_defined={data.read_timeout_defined}",
        f"timeout_fail_closed={data.timeout_fail_closed}",
    )
    return AlpacaPaperConnectivityReviewSection("timeout_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_disconnect_recovery(data: AlpacaPaperConnectivityInput | Mapping[str, Any]) -> AlpacaPaperConnectivityReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.disconnect_recovery_score) if data.disconnect_recovery_score is not None else _average(
        (
            _bool_score(data.disconnect_detection_defined),
            _bool_score(data.reconnect_policy_defined),
            _bool_score(data.session_recovery_checkpointed),
            _bool_score(data.stale_session_guard_defined),
        ),
        default=45,
    )
    risks: list[AlpacaPaperConnectivityRisk] = []
    if (
        data.disconnect_detection_defined is not True
        or data.reconnect_policy_defined is not True
        or data.session_recovery_checkpointed is not True
        or data.stale_session_guard_defined is not True
        or score < 85
    ):
        risks.append(AlpacaPaperConnectivityRisk.SESSION_RECOVERY_FAILURE)
    evidence = (
        f"disconnect_recovery_score={score}/100",
        f"disconnect_detection_defined={data.disconnect_detection_defined}",
        f"reconnect_policy_defined={data.reconnect_policy_defined}",
        f"session_recovery_checkpointed={data.session_recovery_checkpointed}",
        f"stale_session_guard_defined={data.stale_session_guard_defined}",
    )
    return AlpacaPaperConnectivityReviewSection("disconnect_recovery_review", score, not risks and score >= 85, tuple(risks), evidence)


def verify_session_integrity(data: AlpacaPaperConnectivityInput | Mapping[str, Any]) -> AlpacaPaperConnectivityReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.session_integrity_score) if data.session_integrity_score is not None else _average(
        (
            _bool_score(data.session_state_isolated),
            _bool_score(data.session_idempotency_defined),
            _bool_score(data.session_audit_defined),
            _bool_score(data.session_integrity_locked),
        ),
        default=45,
    )
    risks: list[AlpacaPaperConnectivityRisk] = []
    if (
        data.session_state_isolated is not True
        or data.session_idempotency_defined is not True
        or data.session_audit_defined is not True
        or score < 85
    ):
        risks.append(AlpacaPaperConnectivityRisk.SESSION_RECOVERY_FAILURE)
    if data.session_integrity_locked is not True:
        risks.append(AlpacaPaperConnectivityRisk.UNSAFE_CONNECTIVITY_CONFIGURATION)
    evidence = (
        f"session_integrity_score={score}/100",
        f"session_state_isolated={data.session_state_isolated}",
        f"session_idempotency_defined={data.session_idempotency_defined}",
        f"session_audit_defined={data.session_audit_defined}",
        f"session_integrity_locked={data.session_integrity_locked}",
    )
    return AlpacaPaperConnectivityReviewSection("session_integrity_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_observability_requirements(data: AlpacaPaperConnectivityInput | Mapping[str, Any]) -> AlpacaPaperConnectivityReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.observability_score) if data.observability_score is not None else _average(
        (
            _bool_score(data.observability_events_defined),
            _bool_score(data.metrics_defined),
            _bool_score(data.traces_defined),
            _bool_score(data.critical_alerts_defined),
            _upstream_score(data, "observability_score"),
        ),
        default=45,
    )
    risks: list[AlpacaPaperConnectivityRisk] = []
    if (
        data.observability_events_defined is not True
        or data.metrics_defined is not True
        or data.traces_defined is not True
        or data.critical_alerts_defined is not True
        or score < 85
        or _has_upstream_risk(data, "OBSERVABILITY")
    ):
        risks.append(AlpacaPaperConnectivityRisk.OBSERVABILITY_GAP)
    evidence = (
        f"observability_score={score}/100",
        f"observability_events_defined={data.observability_events_defined}",
        f"metrics_defined={data.metrics_defined}",
        f"traces_defined={data.traces_defined}",
        f"critical_alerts_defined={data.critical_alerts_defined}",
    )
    return AlpacaPaperConnectivityReviewSection("observability_review", score, not risks and score >= 85, tuple(risks), evidence)


def verify_kill_switch_compatibility(data: AlpacaPaperConnectivityInput | Mapping[str, Any]) -> AlpacaPaperConnectivityReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.kill_switch_compatibility_score) if data.kill_switch_compatibility_score is not None else _average(
        (
            _bool_score(data.kill_switch_linked),
            _bool_score(data.kill_switch_fail_closed),
            _bool_score(data.emergency_disconnect_defined),
            _bool_score(data.operator_halt_required),
            _upstream_score(data, "kill_switch_score"),
        ),
        default=45,
    )
    risks: list[AlpacaPaperConnectivityRisk] = []
    if (
        data.kill_switch_linked is not True
        or data.kill_switch_fail_closed is not True
        or data.emergency_disconnect_defined is not True
        or data.operator_halt_required is not True
        or score < 85
        or _has_upstream_risk(data, "KILL_SWITCH")
    ):
        risks.append(AlpacaPaperConnectivityRisk.KILL_SWITCH_INCOMPATIBILITY)
    evidence = (
        f"kill_switch_compatibility_score={score}/100",
        f"kill_switch_linked={data.kill_switch_linked}",
        f"kill_switch_fail_closed={data.kill_switch_fail_closed}",
        f"emergency_disconnect_defined={data.emergency_disconnect_defined}",
        f"operator_halt_required={data.operator_halt_required}",
    )
    return AlpacaPaperConnectivityReviewSection("kill_switch_compatibility_review", score, not risks and score >= 85, tuple(risks), evidence)


def verify_rollback_compatibility(data: AlpacaPaperConnectivityInput | Mapping[str, Any]) -> AlpacaPaperConnectivityReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.rollback_compatibility_score) if data.rollback_compatibility_score is not None else _average(
        (
            _bool_score(data.rollback_linked),
            _bool_score(data.recovery_point_required),
            _bool_score(data.rollback_after_disconnect_defined),
            _bool_score(data.restart_guard_defined),
            _upstream_score(data, "rollback_score"),
        ),
        default=45,
    )
    risks: list[AlpacaPaperConnectivityRisk] = []
    if (
        data.rollback_linked is not True
        or data.recovery_point_required is not True
        or data.rollback_after_disconnect_defined is not True
        or data.restart_guard_defined is not True
        or score < 85
        or _has_upstream_risk(data, "ROLLBACK")
    ):
        risks.append(AlpacaPaperConnectivityRisk.ROLLBACK_INCOMPATIBILITY)
    evidence = (
        f"rollback_compatibility_score={score}/100",
        f"rollback_linked={data.rollback_linked}",
        f"recovery_point_required={data.recovery_point_required}",
        f"rollback_after_disconnect_defined={data.rollback_after_disconnect_defined}",
        f"restart_guard_defined={data.restart_guard_defined}",
    )
    return AlpacaPaperConnectivityReviewSection("rollback_compatibility_review", score, not risks and score >= 85, tuple(risks), evidence)


def detect_connectivity_risks(
    data: AlpacaPaperConnectivityInput | Mapping[str, Any],
    credentials_review: AlpacaPaperConnectivityReviewSection | None = None,
    endpoint_review: AlpacaPaperConnectivityReviewSection | None = None,
    rate_limit_review: AlpacaPaperConnectivityReviewSection | None = None,
    retry_review: AlpacaPaperConnectivityReviewSection | None = None,
    timeout_review: AlpacaPaperConnectivityReviewSection | None = None,
    disconnect_recovery_review: AlpacaPaperConnectivityReviewSection | None = None,
    session_integrity_review: AlpacaPaperConnectivityReviewSection | None = None,
    observability_review: AlpacaPaperConnectivityReviewSection | None = None,
    kill_switch_compatibility_review: AlpacaPaperConnectivityReviewSection | None = None,
    rollback_compatibility_review: AlpacaPaperConnectivityReviewSection | None = None,
) -> tuple[AlpacaPaperConnectivityRisk, ...]:
    data = _coerce_input(data)
    sections = (
        credentials_review or verify_credentials_requirements(data),
        endpoint_review or verify_endpoint_requirements(data),
        rate_limit_review or verify_rate_limit_requirements(data),
        retry_review or verify_retry_requirements(data),
        timeout_review or verify_timeout_requirements(data),
        disconnect_recovery_review or verify_disconnect_recovery(data),
        session_integrity_review or verify_session_integrity(data),
        observability_review or verify_observability_requirements(data),
        kill_switch_compatibility_review or verify_kill_switch_compatibility(data),
        rollback_compatibility_review or verify_rollback_compatibility(data),
    )
    risks: list[AlpacaPaperConnectivityRisk] = []
    for section in sections:
        risks.extend(section.risks)
    if (
        data.offline_mode_enforced is not True
        or data.no_http_transport is not True
        or data.no_websocket_transport is not True
        or data.no_socket_transport is not True
        or data.no_external_sdk_import is not True
        or data.configuration_locked is not True
        or _has_upstream_risk(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "EXTERNAL_DEPENDENCY")
    ):
        risks.append(AlpacaPaperConnectivityRisk.UNSAFE_CONNECTIVITY_CONFIGURATION)
    return _dedupe(risks)


def compute_connectivity_score(
    data: AlpacaPaperConnectivityInput | Mapping[str, Any],
    risks: tuple[AlpacaPaperConnectivityRisk, ...] = (),
    credentials_review: AlpacaPaperConnectivityReviewSection | None = None,
    endpoint_review: AlpacaPaperConnectivityReviewSection | None = None,
    rate_limit_review: AlpacaPaperConnectivityReviewSection | None = None,
    retry_review: AlpacaPaperConnectivityReviewSection | None = None,
    timeout_review: AlpacaPaperConnectivityReviewSection | None = None,
    disconnect_recovery_review: AlpacaPaperConnectivityReviewSection | None = None,
    session_integrity_review: AlpacaPaperConnectivityReviewSection | None = None,
    observability_review: AlpacaPaperConnectivityReviewSection | None = None,
    kill_switch_compatibility_review: AlpacaPaperConnectivityReviewSection | None = None,
    rollback_compatibility_review: AlpacaPaperConnectivityReviewSection | None = None,
) -> AlpacaPaperConnectivityScore:
    data = _coerce_input(data)
    credentials = credentials_review or verify_credentials_requirements(data)
    endpoint = endpoint_review or verify_endpoint_requirements(data)
    rate_limit = rate_limit_review or verify_rate_limit_requirements(data)
    retry = retry_review or verify_retry_requirements(data)
    timeout = timeout_review or verify_timeout_requirements(data)
    disconnect = disconnect_recovery_review or verify_disconnect_recovery(data)
    session = session_integrity_review or verify_session_integrity(data)
    observability = observability_review or verify_observability_requirements(data)
    kill_switch = kill_switch_compatibility_review or verify_kill_switch_compatibility(data)
    rollback = rollback_compatibility_review or verify_rollback_compatibility(data)
    weighted = _weighted_average(
        (
            (credentials.score, 1.15),
            (endpoint.score, 1.15),
            (rate_limit.score, 0.95),
            (retry.score, 1.0),
            (timeout.score, 1.0),
            (disconnect.score, 1.05),
            (session.score, 1.05),
            (observability.score, 1.0),
            (kill_switch.score, 1.2),
            (rollback.score, 1.1),
        )
    )
    penalty = min(75, len(set(risks)) * 6)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        AlpacaPaperConnectivityRisk.MISSING_CREDENTIALS: 45,
        AlpacaPaperConnectivityRisk.INVALID_ENDPOINT_CONFIGURATION: 45,
        AlpacaPaperConnectivityRisk.KILL_SWITCH_INCOMPATIBILITY: 45,
        AlpacaPaperConnectivityRisk.UNSAFE_CONNECTIVITY_CONFIGURATION: 40,
    }
    for risk, cap in critical_caps.items():
        if risk in risks:
            overall = min(overall, cap)
    return AlpacaPaperConnectivityScore(
        overall_score=overall,
        credentials_score=credentials.score,
        endpoint_score=endpoint.score,
        rate_limit_score=rate_limit.score,
        retry_score=retry.score,
        timeout_score=timeout.score,
        disconnect_recovery_score=disconnect.score,
        session_integrity_score=session.score,
        observability_score=observability.score,
        kill_switch_compatibility_score=kill_switch.score,
        rollback_compatibility_score=rollback.score,
    )


def _build_graph(risks: tuple[AlpacaPaperConnectivityRisk, ...]) -> AlpacaPaperConnectivityGraph:
    nodes = ("credentials", "endpoint", "rate_limit", "retry", "timeout", "recovery", "session", "observability", "kill_switch", "rollback", "mock_connectivity")
    edges = (
        ("credentials", "endpoint", "scopes"),
        ("endpoint", "mock_connectivity", "targets"),
        ("rate_limit", "mock_connectivity", "guards"),
        ("retry", "timeout", "bounded_by"),
        ("timeout", "recovery", "triggers"),
        ("recovery", "session", "restores"),
        ("session", "mock_connectivity", "stabilizes"),
        ("observability", "mock_connectivity", "reports"),
        ("kill_switch", "mock_connectivity", "halts"),
        ("rollback", "mock_connectivity", "recovers"),
    )
    blocked: list[tuple[str, str]] = []
    mapping = {
        AlpacaPaperConnectivityRisk.MISSING_CREDENTIALS: ("credentials", "endpoint"),
        AlpacaPaperConnectivityRisk.INVALID_ENDPOINT_CONFIGURATION: ("endpoint", "mock_connectivity"),
        AlpacaPaperConnectivityRisk.RATE_LIMIT_EXPOSURE: ("rate_limit", "mock_connectivity"),
        AlpacaPaperConnectivityRisk.RETRY_POLICY_MISSING: ("retry", "timeout"),
        AlpacaPaperConnectivityRisk.TIMEOUT_EXPOSURE: ("timeout", "recovery"),
        AlpacaPaperConnectivityRisk.SESSION_RECOVERY_FAILURE: ("recovery", "session"),
        AlpacaPaperConnectivityRisk.OBSERVABILITY_GAP: ("observability", "mock_connectivity"),
        AlpacaPaperConnectivityRisk.KILL_SWITCH_INCOMPATIBILITY: ("kill_switch", "mock_connectivity"),
        AlpacaPaperConnectivityRisk.ROLLBACK_INCOMPATIBILITY: ("rollback", "mock_connectivity"),
        AlpacaPaperConnectivityRisk.UNSAFE_CONNECTIVITY_CONFIGURATION: ("session", "mock_connectivity"),
    }
    for risk, edge in mapping.items():
        if risk in risks:
            blocked.append(edge)
    return AlpacaPaperConnectivityGraph(nodes, edges, tuple((a, b) for a, b, _ in edges), _dedupe(blocked))


def _select_state(score: int, risks: tuple[AlpacaPaperConnectivityRisk, ...], validated: bool | None, ready_for_mock: bool | None) -> AlpacaPaperConnectivityState:
    hard = {
        AlpacaPaperConnectivityRisk.MISSING_CREDENTIALS,
        AlpacaPaperConnectivityRisk.INVALID_ENDPOINT_CONFIGURATION,
        AlpacaPaperConnectivityRisk.KILL_SWITCH_INCOMPATIBILITY,
        AlpacaPaperConnectivityRisk.UNSAFE_CONNECTIVITY_CONFIGURATION,
    }
    count = len(set(risks))
    if hard.intersection(risks) or score < 45 or count >= 6:
        return AlpacaPaperConnectivityState.NOT_READY
    if count >= 3 or score < 72:
        return AlpacaPaperConnectivityState.REVIEW_REQUIRED
    if count:
        return AlpacaPaperConnectivityState.PARTIALLY_READY
    if validated is True and ready_for_mock is True and score >= 94:
        return AlpacaPaperConnectivityState.READY_FOR_MOCK_CONNECTIVITY
    if validated is True and score >= 90:
        return AlpacaPaperConnectivityState.CONNECTIVITY_VALIDATED
    if score >= 85:
        return AlpacaPaperConnectivityState.CONNECTIVITY_READY
    return AlpacaPaperConnectivityState.PARTIALLY_READY


def generate_connectivity_recommendations(
    risks: tuple[AlpacaPaperConnectivityRisk, ...],
    state: AlpacaPaperConnectivityState | None = None,
) -> tuple[AlpacaPaperConnectivityRecommendation, ...]:
    recommendations: list[AlpacaPaperConnectivityRecommendation] = []
    if risks:
        recommendations.append(AlpacaPaperConnectivityRecommendation.HOLD_MOCK_CONNECTIVITY_APPROVAL)
    mapping = {
        AlpacaPaperConnectivityRisk.MISSING_CREDENTIALS: AlpacaPaperConnectivityRecommendation.DEFINE_CREDENTIAL_REQUIREMENTS,
        AlpacaPaperConnectivityRisk.INVALID_ENDPOINT_CONFIGURATION: AlpacaPaperConnectivityRecommendation.FIX_ENDPOINT_CONFIGURATION,
        AlpacaPaperConnectivityRisk.RATE_LIMIT_EXPOSURE: AlpacaPaperConnectivityRecommendation.DEFINE_RATE_LIMIT_GUARDS,
        AlpacaPaperConnectivityRisk.TIMEOUT_EXPOSURE: AlpacaPaperConnectivityRecommendation.DEFINE_TIMEOUT_POLICY,
        AlpacaPaperConnectivityRisk.RETRY_POLICY_MISSING: AlpacaPaperConnectivityRecommendation.DEFINE_RETRY_POLICY,
        AlpacaPaperConnectivityRisk.SESSION_RECOVERY_FAILURE: AlpacaPaperConnectivityRecommendation.VERIFY_SESSION_RECOVERY,
        AlpacaPaperConnectivityRisk.OBSERVABILITY_GAP: AlpacaPaperConnectivityRecommendation.RESTORE_CONNECTIVITY_OBSERVABILITY,
        AlpacaPaperConnectivityRisk.KILL_SWITCH_INCOMPATIBILITY: AlpacaPaperConnectivityRecommendation.LINK_KILL_SWITCH_COMPATIBILITY,
        AlpacaPaperConnectivityRisk.ROLLBACK_INCOMPATIBILITY: AlpacaPaperConnectivityRecommendation.LINK_ROLLBACK_COMPATIBILITY,
        AlpacaPaperConnectivityRisk.UNSAFE_CONNECTIVITY_CONFIGURATION: AlpacaPaperConnectivityRecommendation.LOCK_SAFE_CONNECTIVITY_CONFIGURATION,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(AlpacaPaperConnectivityRecommendation.RUN_CONNECTIVITY_READINESS_SUITE)
    if state == AlpacaPaperConnectivityState.READY_FOR_MOCK_CONNECTIVITY:
        recommendations.append(AlpacaPaperConnectivityRecommendation.APPROVE_MOCK_CONNECTIVITY_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_alpaca_paper_connectivity_readiness(data: AlpacaPaperConnectivityInput | Mapping[str, Any]) -> AlpacaPaperConnectivityResult:
    data = _coerce_input(data)
    credentials = verify_credentials_requirements(data)
    endpoint = verify_endpoint_requirements(data)
    rate_limit = verify_rate_limit_requirements(data)
    retry = verify_retry_requirements(data)
    timeout = verify_timeout_requirements(data)
    disconnect = verify_disconnect_recovery(data)
    session = verify_session_integrity(data)
    observability = verify_observability_requirements(data)
    kill_switch = verify_kill_switch_compatibility(data)
    rollback = verify_rollback_compatibility(data)
    risks = detect_connectivity_risks(data, credentials, endpoint, rate_limit, retry, timeout, disconnect, session, observability, kill_switch, rollback)
    score = compute_connectivity_score(data, risks, credentials, endpoint, rate_limit, retry, timeout, disconnect, session, observability, kill_switch, rollback)
    state = _select_state(score.overall_score, risks, data.connectivity_validated, data.ready_for_mock_connectivity)
    graph = _build_graph(risks)
    recommendations = generate_connectivity_recommendations(risks, state)
    offline_only = (
        data.offline_mode_enforced is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_sdk_import is True
        and data.no_real_credentials_loaded is True
        and not _has_upstream_risk(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "EXTERNAL_DEPENDENCY")
    )
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return AlpacaPaperConnectivityResult(
        state=state,
        connectivity_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        credentials_review=credentials,
        endpoint_review=endpoint,
        rate_limit_review=rate_limit,
        retry_review=retry,
        timeout_review=timeout,
        disconnect_recovery_review=disconnect,
        session_integrity_review=session,
        observability_review=observability,
        kill_switch_compatibility_review=kill_switch,
        rollback_compatibility_review=rollback,
        connectivity_graph=graph,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_connectivity_markdown(result: AlpacaPaperConnectivityResult) -> str:
    lines = [
        "# AGIcore Alpaca Paper Connectivity Readiness",
        f"- State: {result.state.value}",
        f"- Score: {result.connectivity_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Credentials: {result.score_breakdown.credentials_score}/100",
        f"- Endpoint: {result.score_breakdown.endpoint_score}/100",
        f"- Rate limit: {result.score_breakdown.rate_limit_score}/100",
        f"- Retry: {result.score_breakdown.retry_score}/100",
        f"- Timeout: {result.score_breakdown.timeout_score}/100",
        f"- Disconnect recovery: {result.score_breakdown.disconnect_recovery_score}/100",
        f"- Session integrity: {result.score_breakdown.session_integrity_score}/100",
        f"- Observability: {result.score_breakdown.observability_score}/100",
        f"- Kill switch: {result.score_breakdown.kill_switch_compatibility_score}/100",
        f"- Rollback: {result.score_breakdown.rollback_compatibility_score}/100",
        "",
        "# Connectivity Reviews",
    ]
    sections = (
        result.credentials_review,
        result.endpoint_review,
        result.rate_limit_review,
        result.retry_review,
        result.timeout_review,
        result.disconnect_recovery_review,
        result.session_integrity_review,
        result.observability_review,
        result.kill_switch_compatibility_review,
        result.rollback_compatibility_review,
    )
    for section in sections:
        lines.append(
            f"- {section.name}: passed={section.passed}, score={section.score}/100, "
            f"risks={', '.join(risk.value for risk in section.risks) or 'none'}"
        )
        lines.extend(f"  - {item}" for item in section.evidence)
    lines.append("")
    lines.append("# Connectivity Graph")
    lines.append(f"- Nodes: {', '.join(result.connectivity_graph.nodes)}")
    lines.extend(f"- Edge: {source} -> {target} ({label})" for source, target, label in result.connectivity_graph.edges)
    lines.append(
        "- Blocked edges: "
        + (", ".join(f"{source}->{target}" for source, target in result.connectivity_graph.blocked_edges) or "none")
    )
    lines.append("")
    lines.append("# Connectivity Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Connectivity Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_connectivity_score",
    "detect_connectivity_risks",
    "evaluate_alpaca_paper_connectivity_readiness",
    "generate_connectivity_recommendations",
    "render_connectivity_markdown",
    "verify_credentials_requirements",
    "verify_disconnect_recovery",
    "verify_endpoint_requirements",
    "verify_kill_switch_compatibility",
    "verify_observability_requirements",
    "verify_rate_limit_requirements",
    "verify_retry_requirements",
    "verify_rollback_compatibility",
    "verify_session_integrity",
    "verify_timeout_requirements",
]
