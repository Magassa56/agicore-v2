"""Offline runtime isolation review for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable

from agicore.trading.runtime_isolation_review_models import (
    IsolationRecommendation,
    IsolationRisk,
    RuntimeIsolationGraph,
    RuntimeIsolationInput,
    RuntimeIsolationResult,
    RuntimeIsolationReviewSection,
    RuntimeIsolationScore,
    RuntimeIsolationState,
)


def _value(item: Any) -> str:
    if item is None:
        return ""
    if isinstance(item, Enum):
        return str(item.value)
    return str(item)


def _get(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default) if obj is not None else default


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


def _upstream_risks(data: RuntimeIsolationInput) -> tuple[Any, ...]:
    return (
        _as_tuple(_get(data.sandbox_readiness_audit, "blockers", ()))
        + _as_tuple(_get(data.stable_review, "blockers", ()))
        + _as_tuple(_get(data.freeze_candidate_review, "blockers", ()))
        + _as_tuple(_get(data.freeze_readiness_audit, "blockers", ()))
    )


def _has_upstream(data: RuntimeIsolationInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _sandbox_score(data: RuntimeIsolationInput, *names: str) -> int | None:
    audit = data.sandbox_readiness_audit
    if audit is None:
        return None
    breakdown = _get(audit, "score_breakdown")
    values = [_score(breakdown, name) for name in names]
    values.extend(_score(_get(audit, f"{name}_review"), "score") for name in names)
    values = [value for value in values if value is not None]
    if values:
        return _average(values)
    return _score(audit, "sandbox_score")


def _readiness_snapshot_score(data: RuntimeIsolationInput, *names: str) -> int | None:
    snapshot = _get(data.freeze_readiness_audit, "snapshot")
    values = [_score(snapshot, name) for name in names]
    return _average(values) if any(value is not None for value in values) else None


def review_execution_boundaries(data: RuntimeIsolationInput) -> RuntimeIsolationReviewSection:
    """Review live execution and broker/order execution boundaries."""

    score = _clamp(data.execution_boundary_score) if data.execution_boundary_score is not None else _average(
        (
            _bool_score(data.execution_isolated),
            _bool_score(data.live_execution_disabled),
            _bool_score(data.real_order_path_disabled),
            _bool_score(data.broker_disabled),
            _bool_score(data.broker_credentials_absent),
            _sandbox_score(data, "runtime_isolation_score"),
            _readiness_snapshot_score(data, "sandbox_score"),
        ),
        default=45,
    )
    risks: list[IsolationRisk] = []
    if data.broker_disabled is not True or data.broker_credentials_absent is not True or _has_upstream(data, "BROKER"):
        risks.append(IsolationRisk.BROKER_CONNECTIVITY)
    if (
        data.execution_isolated is not True
        or data.live_execution_disabled is not True
        or data.real_order_path_disabled is not True
        or _has_upstream(data, "LIVE_EXECUTION", "EXECUTION_LEAK", "EXECUTION_UNSAFE")
    ):
        risks.append(IsolationRisk.EXECUTION_BOUNDARY_FAILURE)
    if data.live_execution_disabled is not True or data.real_order_path_disabled is not True:
        risks.append(IsolationRisk.SANDBOX_BREAKOUT_RISK)
    evidence = (
        f"execution_boundary_score={score}/100",
        f"execution_isolated={data.execution_isolated}",
        f"live_execution_disabled={data.live_execution_disabled}",
        f"real_order_path_disabled={data.real_order_path_disabled}",
        f"broker_disabled={data.broker_disabled}",
    )
    return RuntimeIsolationReviewSection(
        name="execution_boundaries",
        score=score,
        passed=not risks and score >= 85,
        risks=_dedupe(risks),
        evidence=evidence,
    )


def review_memory_boundaries(data: RuntimeIsolationInput) -> RuntimeIsolationReviewSection:
    """Review memory namespace and cross-run contamination boundaries."""

    score = _clamp(data.memory_boundary_score) if data.memory_boundary_score is not None else _average(
        (
            _bool_score(data.memory_namespace_isolated),
            _bool_score(data.memory_snapshot_clean),
            _bool_score(data.memory_cross_run_guard),
            _sandbox_score(data, "memory_persistence_score"),
        ),
        default=45,
    )
    risks = []
    if (
        data.memory_namespace_isolated is not True
        or data.memory_snapshot_clean is not True
        or data.memory_cross_run_guard is not True
        or score < 80
        or _has_upstream(data, "MEMORY")
    ):
        risks.append(IsolationRisk.MEMORY_CROSS_CONTAMINATION)
    evidence = (
        f"memory_boundary_score={score}/100",
        f"memory_namespace_isolated={data.memory_namespace_isolated}",
        f"memory_snapshot_clean={data.memory_snapshot_clean}",
        f"memory_cross_run_guard={data.memory_cross_run_guard}",
    )
    return RuntimeIsolationReviewSection(
        name="memory_boundaries",
        score=score,
        passed=not risks and score >= 80,
        risks=tuple(risks),
        evidence=evidence,
    )


def review_storage_boundaries(data: RuntimeIsolationInput) -> RuntimeIsolationReviewSection:
    """Review filesystem and storage containment."""

    score = _clamp(data.storage_boundary_score) if data.storage_boundary_score is not None else _average(
        (
            _bool_score(data.filesystem_root_restricted),
            _bool_score(data.data_directory_readonly),
            _bool_score(data.temp_directory_isolated),
            _bool_score(data.storage_namespace_isolated),
            _bool_score(data.storage_rollback_available),
            _bool_score(data.storage_checksum_valid),
        ),
        default=45,
    )
    risks: list[IsolationRisk] = []
    if (
        data.filesystem_root_restricted is not True
        or data.data_directory_readonly is not True
        or data.temp_directory_isolated is not True
    ):
        risks.append(IsolationRisk.FILESYSTEM_ESCAPE)
    if (
        data.storage_namespace_isolated is not True
        or data.storage_rollback_available is not True
        or data.storage_checksum_valid is not True
        or score < 80
    ):
        risks.append(IsolationRisk.STORAGE_CORRUPTION_RISK)
    evidence = (
        f"storage_boundary_score={score}/100",
        f"filesystem_root_restricted={data.filesystem_root_restricted}",
        f"data_directory_readonly={data.data_directory_readonly}",
        f"storage_checksum_valid={data.storage_checksum_valid}",
    )
    return RuntimeIsolationReviewSection(
        name="storage_boundaries",
        score=score,
        passed=not risks and score >= 80,
        risks=_dedupe(risks),
        evidence=evidence,
    )


def review_network_boundaries(data: RuntimeIsolationInput) -> RuntimeIsolationReviewSection:
    """Review network, API and broker connectivity boundaries."""

    score = _clamp(data.network_boundary_score) if data.network_boundary_score is not None else _average(
        (
            _bool_score(data.network_disabled),
            _bool_score(data.network_allowlist_empty),
            _bool_score(data.external_api_disabled),
            _bool_score(data.api_credentials_absent),
            _bool_score(data.broker_disabled),
            _bool_score(data.broker_credentials_absent),
        ),
        default=45,
    )
    risks: list[IsolationRisk] = []
    if data.external_api_disabled is not True or data.api_credentials_absent is not True or _has_upstream(data, "API"):
        risks.append(IsolationRisk.EXTERNAL_API_ACCESS)
    if data.broker_disabled is not True or data.broker_credentials_absent is not True or _has_upstream(data, "BROKER"):
        risks.append(IsolationRisk.BROKER_CONNECTIVITY)
    if data.network_disabled is not True or data.network_allowlist_empty is not True or score < 85:
        risks.append(IsolationRisk.NETWORK_LEAK)
    evidence = (
        f"network_boundary_score={score}/100",
        f"network_disabled={data.network_disabled}",
        f"network_allowlist_empty={data.network_allowlist_empty}",
        f"external_api_disabled={data.external_api_disabled}",
        f"broker_disabled={data.broker_disabled}",
    )
    return RuntimeIsolationReviewSection(
        name="network_boundaries",
        score=score,
        passed=not risks and score >= 85,
        risks=_dedupe(risks),
        evidence=evidence,
    )


def review_external_dependency_boundaries(data: RuntimeIsolationInput) -> RuntimeIsolationReviewSection:
    """Review external dependencies and isolated observability."""

    observability_score = data.observability_score if data.observability_score is not None else _average(
        (
            _bool_score(data.runtime_observable),
            _bool_score(data.isolated_logging_enabled),
            _bool_score(data.isolated_metrics_enabled),
            _sandbox_score(data, "observability_score"),
        )
    )
    breakout_score = data.sandbox_breakout_score if data.sandbox_breakout_score is not None else _bool_score(
        data.sandbox_escape_tests_passed
    )
    score = _clamp(data.dependency_boundary_score) if data.dependency_boundary_score is not None else _average(
        (
            _bool_score(data.dependencies_offline),
            _bool_score(data.dependency_mocks_available),
            _bool_score(data.dependency_lock_verified),
            observability_score,
            breakout_score,
        ),
        default=45,
    )
    risks: list[IsolationRisk] = []
    if (
        data.dependencies_offline is not True
        or data.dependency_mocks_available is not True
        or data.dependency_lock_verified is not True
        or score < 80
    ):
        risks.append(IsolationRisk.DEPENDENCY_ESCAPE)
    if (
        data.runtime_observable is not True
        or data.isolated_logging_enabled is not True
        or data.isolated_metrics_enabled is not True
        or observability_score < 80
        or _has_upstream(data, "OBSERVABILITY")
    ):
        risks.append(IsolationRisk.OBSERVABILITY_ISOLATION_GAP)
    if data.sandbox_escape_tests_passed is not True or breakout_score < 85 or _has_upstream(data, "SANDBOX_ISOLATION"):
        risks.append(IsolationRisk.SANDBOX_BREAKOUT_RISK)
    evidence = (
        f"dependency_boundary_score={score}/100",
        f"observability_score={observability_score}/100",
        f"sandbox_breakout_score={breakout_score}/100",
        f"dependencies_offline={data.dependencies_offline}",
        f"dependency_mocks_available={data.dependency_mocks_available}",
    )
    return RuntimeIsolationReviewSection(
        name="external_dependency_boundaries",
        score=score,
        passed=not risks and score >= 80,
        risks=_dedupe(risks),
        evidence=evidence,
    )


def _build_isolation_graph(risks: tuple[IsolationRisk, ...]) -> RuntimeIsolationGraph:
    nodes = (
        "agicore_runtime",
        "execution_boundary",
        "memory_boundary",
        "storage_boundary",
        "network_boundary",
        "external_dependencies",
        "paper_runtime",
    )
    edges = (
        ("agicore_runtime", "execution_boundary", "guarded"),
        ("agicore_runtime", "memory_boundary", "isolated"),
        ("agicore_runtime", "storage_boundary", "contained"),
        ("agicore_runtime", "network_boundary", "blocked"),
        ("external_dependencies", "paper_runtime", "mocked"),
    )
    escape_edges: list[tuple[str, str]] = []
    if IsolationRisk.BROKER_CONNECTIVITY in risks:
        escape_edges.append(("execution_boundary", "broker"))
    if IsolationRisk.EXTERNAL_API_ACCESS in risks or IsolationRisk.NETWORK_LEAK in risks:
        escape_edges.append(("network_boundary", "external_api"))
    if IsolationRisk.FILESYSTEM_ESCAPE in risks:
        escape_edges.append(("storage_boundary", "host_filesystem"))
    if IsolationRisk.MEMORY_CROSS_CONTAMINATION in risks:
        escape_edges.append(("memory_boundary", "previous_run_state"))
    return RuntimeIsolationGraph(
        nodes=nodes,
        edges=edges,
        blocked_edges=(
            ("execution_boundary", "broker"),
            ("network_boundary", "external_api"),
            ("storage_boundary", "host_filesystem"),
        ),
        escape_edges=_dedupe(escape_edges),
    )


def detect_isolation_risks(
    data: RuntimeIsolationInput,
    execution_boundaries: RuntimeIsolationReviewSection | None = None,
    memory_boundaries: RuntimeIsolationReviewSection | None = None,
    storage_boundaries: RuntimeIsolationReviewSection | None = None,
    network_boundaries: RuntimeIsolationReviewSection | None = None,
    external_dependency_boundaries: RuntimeIsolationReviewSection | None = None,
) -> tuple[IsolationRisk, ...]:
    """Detect runtime isolation risks."""

    sections = (
        execution_boundaries or review_execution_boundaries(data),
        memory_boundaries or review_memory_boundaries(data),
        storage_boundaries or review_storage_boundaries(data),
        network_boundaries or review_network_boundaries(data),
        external_dependency_boundaries or review_external_dependency_boundaries(data),
    )
    risks: list[IsolationRisk] = []
    for section in sections:
        risks.extend(section.risks)
    return _dedupe(risks)


def compute_isolation_score(
    data: RuntimeIsolationInput,
    risks: tuple[IsolationRisk, ...] = (),
    execution_boundaries: RuntimeIsolationReviewSection | None = None,
    memory_boundaries: RuntimeIsolationReviewSection | None = None,
    storage_boundaries: RuntimeIsolationReviewSection | None = None,
    network_boundaries: RuntimeIsolationReviewSection | None = None,
    external_dependency_boundaries: RuntimeIsolationReviewSection | None = None,
) -> RuntimeIsolationScore:
    """Compute runtime isolation score normalized to 0..100."""

    execution = execution_boundaries or review_execution_boundaries(data)
    memory = memory_boundaries or review_memory_boundaries(data)
    storage = storage_boundaries or review_storage_boundaries(data)
    network = network_boundaries or review_network_boundaries(data)
    dependencies = external_dependency_boundaries or review_external_dependency_boundaries(data)
    observability_score = data.observability_score if data.observability_score is not None else _average(
        (
            _bool_score(data.runtime_observable),
            _bool_score(data.isolated_logging_enabled),
            _bool_score(data.isolated_metrics_enabled),
            _sandbox_score(data, "observability_score"),
        )
    )
    breakout_score = data.sandbox_breakout_score if data.sandbox_breakout_score is not None else _bool_score(
        data.sandbox_escape_tests_passed
    )
    weighted = _weighted_average(
        (
            (execution.score, 1.3),
            (memory.score, 1.0),
            (storage.score, 1.0),
            (network.score, 1.25),
            (dependencies.score, 1.0),
            (observability_score, 0.8),
            (breakout_score, 1.1),
        )
    )
    penalty = min(65, len(set(risks)) * 7)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        IsolationRisk.EXTERNAL_API_ACCESS: 45,
        IsolationRisk.BROKER_CONNECTIVITY: 45,
        IsolationRisk.NETWORK_LEAK: 50,
        IsolationRisk.FILESYSTEM_ESCAPE: 60,
        IsolationRisk.EXECUTION_BOUNDARY_FAILURE: 55,
        IsolationRisk.SANDBOX_BREAKOUT_RISK: 55,
    }
    for risk, cap in critical_caps.items():
        if risk in risks:
            overall = min(overall, cap)
    return RuntimeIsolationScore(
        overall_score=overall,
        execution_boundary_score=execution.score,
        memory_boundary_score=memory.score,
        storage_boundary_score=storage.score,
        network_boundary_score=network.score,
        external_dependency_score=dependencies.score,
        observability_score=_clamp(observability_score),
        sandbox_breakout_score=_clamp(breakout_score),
    )


def _select_state(score: int, risks: tuple[IsolationRisk, ...], paper_runtime_ready: bool | None) -> RuntimeIsolationState:
    risk_count = len(set(risks))
    hard_risks = {
        IsolationRisk.EXTERNAL_API_ACCESS,
        IsolationRisk.BROKER_CONNECTIVITY,
        IsolationRisk.NETWORK_LEAK,
        IsolationRisk.EXECUTION_BOUNDARY_FAILURE,
        IsolationRisk.SANDBOX_BREAKOUT_RISK,
    }
    if hard_risks.intersection(risks) or score < 45 or risk_count >= 6:
        return RuntimeIsolationState.NOT_ISOLATED
    if risk_count >= 3 or score < 72:
        return RuntimeIsolationState.ISOLATION_REVIEW_REQUIRED
    if risk_count:
        return RuntimeIsolationState.PARTIALLY_ISOLATED
    if score >= 94 and paper_runtime_ready is True:
        return RuntimeIsolationState.READY_FOR_PAPER_RUNTIME
    if score >= 88:
        return RuntimeIsolationState.ISOLATED
    return RuntimeIsolationState.PARTIALLY_ISOLATED


def generate_isolation_recommendations(
    risks: tuple[IsolationRisk, ...],
    state: RuntimeIsolationState | None = None,
) -> tuple[IsolationRecommendation, ...]:
    """Generate runtime isolation recommendations."""

    recommendations: list[IsolationRecommendation] = []
    if risks:
        recommendations.append(IsolationRecommendation.HOLD_RUNTIME_ISOLATION_APPROVAL)
    mapping = {
        IsolationRisk.EXTERNAL_API_ACCESS: IsolationRecommendation.DISABLE_EXTERNAL_API_ACCESS,
        IsolationRisk.BROKER_CONNECTIVITY: IsolationRecommendation.DISABLE_BROKER_CONNECTIVITY,
        IsolationRisk.NETWORK_LEAK: IsolationRecommendation.SEAL_NETWORK_BOUNDARY,
        IsolationRisk.FILESYSTEM_ESCAPE: IsolationRecommendation.RESTRICT_FILESYSTEM_SCOPE,
        IsolationRisk.MEMORY_CROSS_CONTAMINATION: IsolationRecommendation.ISOLATE_MEMORY_CONTEXT,
        IsolationRisk.EXECUTION_BOUNDARY_FAILURE: IsolationRecommendation.REPAIR_EXECUTION_BOUNDARY,
        IsolationRisk.DEPENDENCY_ESCAPE: IsolationRecommendation.VENDOR_OR_MOCK_EXTERNAL_DEPENDENCIES,
        IsolationRisk.STORAGE_CORRUPTION_RISK: IsolationRecommendation.PROTECT_STORAGE_STATE,
        IsolationRisk.OBSERVABILITY_ISOLATION_GAP: IsolationRecommendation.ADD_ISOLATED_OBSERVABILITY,
        IsolationRisk.SANDBOX_BREAKOUT_RISK: IsolationRecommendation.REBUILD_SANDBOX_BOUNDARY,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(IsolationRecommendation.RUN_RUNTIME_ISOLATION_SUITE)
    if state == RuntimeIsolationState.READY_FOR_PAPER_RUNTIME:
        recommendations.append(IsolationRecommendation.APPROVE_PAPER_RUNTIME_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_runtime_isolation(data: RuntimeIsolationInput) -> RuntimeIsolationResult:
    """Evaluate whether AGIcore Trading runtime is fully isolated offline."""

    execution = review_execution_boundaries(data)
    memory = review_memory_boundaries(data)
    storage = review_storage_boundaries(data)
    network = review_network_boundaries(data)
    dependencies = review_external_dependency_boundaries(data)
    risks = detect_isolation_risks(data, execution, memory, storage, network, dependencies)
    score = compute_isolation_score(data, risks, execution, memory, storage, network, dependencies)
    graph = _build_isolation_graph(risks)
    state = _select_state(score.overall_score, risks, data.paper_runtime_ready)
    recommendations = generate_isolation_recommendations(risks, state)
    offline_only = data.live_execution_disabled and data.broker_disabled and data.external_api_disabled
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return RuntimeIsolationResult(
        state=state,
        isolation_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        execution_boundaries=execution,
        memory_boundaries=memory,
        storage_boundaries=storage,
        network_boundaries=network,
        external_dependency_boundaries=dependencies,
        isolation_graph=graph,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_runtime_isolation_markdown(result: RuntimeIsolationResult) -> str:
    """Render an explainable runtime isolation review."""

    lines = [
        "# AGIcore Runtime Isolation Review",
        f"- State: {result.state.value}",
        f"- Score: {result.isolation_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Execution boundaries: {result.score_breakdown.execution_boundary_score}/100",
        f"- Memory boundaries: {result.score_breakdown.memory_boundary_score}/100",
        f"- Storage boundaries: {result.score_breakdown.storage_boundary_score}/100",
        f"- Network boundaries: {result.score_breakdown.network_boundary_score}/100",
        f"- External dependencies: {result.score_breakdown.external_dependency_score}/100",
        f"- Observability isolation: {result.score_breakdown.observability_score}/100",
        f"- Sandbox breakout: {result.score_breakdown.sandbox_breakout_score}/100",
        "",
        "# Boundary Reviews",
    ]
    for section in (
        result.execution_boundaries,
        result.memory_boundaries,
        result.storage_boundaries,
        result.network_boundaries,
        result.external_dependency_boundaries,
    ):
        lines.append(
            f"- {section.name}: passed={section.passed}, score={section.score}/100, "
            f"risks={', '.join(risk.value for risk in section.risks) or 'none'}"
        )
        lines.extend(f"  - {item}" for item in section.evidence)
    lines.append("")
    lines.append("# Runtime Isolation Graph")
    lines.append(f"- Nodes: {', '.join(result.isolation_graph.nodes)}")
    lines.extend(
        f"- Edge: {source} -> {target} ({label})"
        for source, target, label in result.isolation_graph.edges
    )
    lines.append(f"- Escape edges: {', '.join(f'{source}->{target}' for source, target in result.isolation_graph.escape_edges) or 'none'}")
    lines.append("")
    lines.append("# Isolation Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Isolation Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# Isolation Outlook")
    if result.state == RuntimeIsolationState.READY_FOR_PAPER_RUNTIME:
        lines.append("- Runtime isolation is ready for manual paper runtime preparation review.")
    elif result.state == RuntimeIsolationState.ISOLATED:
        lines.append("- Runtime isolation is established; paper runtime remains gated.")
    elif result.state == RuntimeIsolationState.PARTIALLY_ISOLATED:
        lines.append("- Runtime isolation is partial and remaining risks must be resolved.")
    else:
        lines.append("- Runtime isolation approval should remain blocked.")
    return "\n".join(lines)


__all__ = [
    "compute_isolation_score",
    "detect_isolation_risks",
    "evaluate_runtime_isolation",
    "generate_isolation_recommendations",
    "render_runtime_isolation_markdown",
    "review_execution_boundaries",
    "review_external_dependency_boundaries",
    "review_memory_boundaries",
    "review_network_boundaries",
    "review_storage_boundaries",
]
