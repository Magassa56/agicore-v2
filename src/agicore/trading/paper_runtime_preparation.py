"""Offline paper runtime preparation audit for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_runtime_preparation_models import (
    PaperRuntimeGraph,
    PaperRuntimePreparationInput,
    PaperRuntimePreparationResult,
    PaperRuntimePreparationState,
    PaperRuntimeRecommendation,
    PaperRuntimeReviewSection,
    PaperRuntimeRisk,
    PaperRuntimeScore,
)


def _coerce_input(data: PaperRuntimePreparationInput | Mapping[str, Any]) -> PaperRuntimePreparationInput:
    if isinstance(data, PaperRuntimePreparationInput):
        return data
    return PaperRuntimePreparationInput(**dict(data))


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


def _upstream_blockers(data: PaperRuntimePreparationInput) -> tuple[Any, ...]:
    upstream = (
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.runtime_isolation_review,
        data.sandbox_readiness_audit,
        data.stable_review,
    )
    blockers: tuple[Any, ...] = ()
    for item in upstream:
        blockers += _as_tuple(_get(item, "blockers", ()))
        blockers += _as_tuple(_get(item, "risks", ()))
    return blockers


def _has_upstream(data: PaperRuntimePreparationInput, *needles: str) -> bool:
    return _contains(_upstream_blockers(data), *needles)


def _upstream_score(data: PaperRuntimePreparationInput, *names: str) -> int | None:
    upstream = (
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.runtime_isolation_review,
        data.sandbox_readiness_audit,
        data.stable_review,
    )
    values: list[int] = []
    for item in upstream:
        values.extend(_score(item, name) for name in names)
        breakdown = _get(item, "score_breakdown")
        values.extend(_score(breakdown, name) for name in names)
    values = [value for value in values if value is not None]
    return _average(values) if values else None


def verify_virtual_portfolio_readiness(
    data: PaperRuntimePreparationInput | Mapping[str, Any],
) -> PaperRuntimeReviewSection:
    """Verify virtual portfolio and account readiness."""

    data = _coerce_input(data)
    score = _clamp(data.virtual_portfolio_score) if data.virtual_portfolio_score is not None else _average(
        (
            _bool_score(data.virtual_portfolio_available),
            _bool_score(data.virtual_cash_configured),
            _bool_score(data.virtual_equity_consistent),
            _bool_score(data.portfolio_reset_supported),
        ),
        default=45,
    )
    risks: list[PaperRuntimeRisk] = []
    if (
        data.virtual_portfolio_available is not True
        or data.virtual_cash_configured is not True
        or data.portfolio_reset_supported is not True
        or score < 80
    ):
        risks.append(PaperRuntimeRisk.VIRTUAL_PORTFOLIO_MISSING)
    if data.virtual_equity_consistent is not True:
        risks.append(PaperRuntimeRisk.PAPER_STATE_CORRUPTION_RISK)
    evidence = (
        f"virtual_portfolio_score={score}/100",
        f"virtual_portfolio_available={data.virtual_portfolio_available}",
        f"virtual_cash_configured={data.virtual_cash_configured}",
        f"virtual_equity_consistent={data.virtual_equity_consistent}",
        f"portfolio_reset_supported={data.portfolio_reset_supported}",
    )
    return PaperRuntimeReviewSection("virtual_portfolio_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_simulated_order_readiness(
    data: PaperRuntimePreparationInput | Mapping[str, Any],
) -> PaperRuntimeReviewSection:
    """Verify simulated order engine readiness and broker isolation."""

    data = _coerce_input(data)
    score = _clamp(data.simulated_order_score) if data.simulated_order_score is not None else _average(
        (
            _bool_score(data.simulated_order_engine_available),
            _bool_score(data.market_order_simulation_supported),
            _bool_score(data.order_rejection_simulation_supported),
            _bool_score(data.broker_connection_absent),
            _upstream_score(data, "isolation_score", "kill_switch_score"),
        ),
        default=45,
    )
    risks: list[PaperRuntimeRisk] = []
    if (
        data.simulated_order_engine_available is not True
        or data.market_order_simulation_supported is not True
        or data.order_rejection_simulation_supported is not True
        or score < 85
    ):
        risks.append(PaperRuntimeRisk.SIMULATED_ORDER_ENGINE_MISSING)
    if data.broker_connection_absent is not True or _has_upstream(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS"):
        risks.append(PaperRuntimeRisk.PAPER_EXECUTION_LEAK_RISK)
    evidence = (
        f"simulated_order_score={score}/100",
        f"simulated_order_engine_available={data.simulated_order_engine_available}",
        f"market_order_simulation_supported={data.market_order_simulation_supported}",
        f"order_rejection_simulation_supported={data.order_rejection_simulation_supported}",
        f"broker_connection_absent={data.broker_connection_absent}",
    )
    return PaperRuntimeReviewSection("simulated_order_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_simulated_position_readiness(
    data: PaperRuntimePreparationInput | Mapping[str, Any],
) -> PaperRuntimeReviewSection:
    """Verify simulated position tracking and paper PnL readiness."""

    data = _coerce_input(data)
    score = _clamp(data.simulated_position_score) if data.simulated_position_score is not None else _average(
        (
            _bool_score(data.simulated_position_tracking_available),
            _bool_score(data.position_average_price_supported),
            _bool_score(data.realized_pnl_supported),
            _bool_score(data.position_state_consistent),
        ),
        default=45,
    )
    risks: list[PaperRuntimeRisk] = []
    if (
        data.simulated_position_tracking_available is not True
        or data.position_average_price_supported is not True
        or score < 80
    ):
        risks.append(PaperRuntimeRisk.SIMULATED_POSITION_TRACKING_MISSING)
    if data.realized_pnl_supported is not True:
        risks.append(PaperRuntimeRisk.PAPER_PNL_UNVERIFIED)
    if data.position_state_consistent is not True:
        risks.append(PaperRuntimeRisk.PAPER_STATE_CORRUPTION_RISK)
    evidence = (
        f"simulated_position_score={score}/100",
        f"simulated_position_tracking_available={data.simulated_position_tracking_available}",
        f"position_average_price_supported={data.position_average_price_supported}",
        f"realized_pnl_supported={data.realized_pnl_supported}",
        f"position_state_consistent={data.position_state_consistent}",
    )
    return PaperRuntimeReviewSection("simulated_position_review", score, not risks and score >= 80, _dedupe(risks), evidence)


def verify_paper_risk_readiness(
    data: PaperRuntimePreparationInput | Mapping[str, Any],
) -> PaperRuntimeReviewSection:
    """Verify paper risk gates, order limits and kill switch coupling."""

    data = _coerce_input(data)
    score = _clamp(data.paper_risk_score) if data.paper_risk_score is not None else _average(
        (
            _bool_score(data.paper_risk_engine_available),
            _bool_score(data.max_order_limits_configured),
            _bool_score(data.risk_gate_enforced),
            _bool_score(data.kill_switch_connected),
            _upstream_score(data, "kill_switch_score", "rollback_score"),
        ),
        default=45,
    )
    risks: list[PaperRuntimeRisk] = []
    if (
        data.paper_risk_engine_available is not True
        or data.max_order_limits_configured is not True
        or data.risk_gate_enforced is not True
        or data.kill_switch_connected is not True
        or score < 85
    ):
        risks.append(PaperRuntimeRisk.PAPER_RISK_ENGINE_MISSING)
    evidence = (
        f"paper_risk_score={score}/100",
        f"paper_risk_engine_available={data.paper_risk_engine_available}",
        f"max_order_limits_configured={data.max_order_limits_configured}",
        f"risk_gate_enforced={data.risk_gate_enforced}",
        f"kill_switch_connected={data.kill_switch_connected}",
    )
    return PaperRuntimeReviewSection("paper_risk_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_session_runtime_readiness(
    data: PaperRuntimePreparationInput | Mapping[str, Any],
) -> PaperRuntimeReviewSection:
    """Verify paper session runtime isolation, observability and state checkpoints."""

    data = _coerce_input(data)
    observability_score = data.paper_observability_score if data.paper_observability_score is not None else _average(
        (
            _bool_score(data.paper_observability_available),
            _upstream_score(data, "observability_score"),
        )
    )
    score = _clamp(data.session_runtime_score) if data.session_runtime_score is not None else _average(
        (
            _bool_score(data.session_runtime_configured),
            _bool_score(data.session_prechecks_defined),
            _bool_score(data.session_event_stream_available),
            _bool_score(data.paper_runtime_isolated),
            _bool_score(data.paper_state_checkpoint_supported),
            observability_score,
        ),
        default=45,
    )
    risks: list[PaperRuntimeRisk] = []
    if (
        data.session_runtime_configured is not True
        or data.session_prechecks_defined is not True
        or data.session_event_stream_available is not True
        or score < 80
    ):
        risks.append(PaperRuntimeRisk.SESSION_RUNTIME_UNVERIFIED)
    if data.paper_runtime_isolated is not True or _has_upstream(data, "NOT_ISOLATED", "SANDBOX_ISOLATION"):
        risks.append(PaperRuntimeRisk.PAPER_RUNTIME_NOT_ISOLATED)
    if data.paper_observability_available is not True or observability_score < 80 or _has_upstream(data, "OBSERVABILITY_GAP"):
        risks.append(PaperRuntimeRisk.PAPER_OBSERVABILITY_GAP)
    if data.paper_state_checkpoint_supported is not True:
        risks.append(PaperRuntimeRisk.PAPER_STATE_CORRUPTION_RISK)
    evidence = (
        f"session_runtime_score={score}/100",
        f"paper_observability_score={observability_score}/100",
        f"session_runtime_configured={data.session_runtime_configured}",
        f"paper_runtime_isolated={data.paper_runtime_isolated}",
        f"paper_state_checkpoint_supported={data.paper_state_checkpoint_supported}",
    )
    return PaperRuntimeReviewSection("session_runtime_review", score, not risks and score >= 80, _dedupe(risks), evidence)


def _build_paper_runtime_graph(blockers: tuple[PaperRuntimeRisk, ...]) -> PaperRuntimeGraph:
    nodes = (
        "paper_runtime",
        "virtual_portfolio",
        "simulated_order_engine",
        "simulated_positions",
        "paper_risk_gate",
        "session_runtime",
        "paper_execution_loop",
    )
    edges = (
        ("paper_runtime", "virtual_portfolio", "owns"),
        ("paper_runtime", "simulated_order_engine", "submits"),
        ("simulated_order_engine", "simulated_positions", "updates"),
        ("paper_risk_gate", "simulated_order_engine", "guards"),
        ("session_runtime", "paper_risk_gate", "checks"),
        ("session_runtime", "paper_execution_loop", "gates"),
    )
    blocked: list[tuple[str, str]] = []
    if PaperRuntimeRisk.VIRTUAL_PORTFOLIO_MISSING in blockers:
        blocked.append(("paper_runtime", "virtual_portfolio"))
    if PaperRuntimeRisk.SIMULATED_ORDER_ENGINE_MISSING in blockers or PaperRuntimeRisk.PAPER_EXECUTION_LEAK_RISK in blockers:
        blocked.append(("paper_runtime", "simulated_order_engine"))
    if PaperRuntimeRisk.SIMULATED_POSITION_TRACKING_MISSING in blockers:
        blocked.append(("simulated_order_engine", "simulated_positions"))
    if PaperRuntimeRisk.PAPER_RISK_ENGINE_MISSING in blockers:
        blocked.append(("paper_risk_gate", "simulated_order_engine"))
    if PaperRuntimeRisk.SESSION_RUNTIME_UNVERIFIED in blockers or PaperRuntimeRisk.PAPER_RUNTIME_NOT_ISOLATED in blockers:
        blocked.append(("session_runtime", "paper_execution_loop"))
    return PaperRuntimeGraph(
        nodes=nodes,
        edges=edges,
        ready_edges=(
            ("paper_runtime", "virtual_portfolio"),
            ("paper_runtime", "simulated_order_engine"),
            ("simulated_order_engine", "simulated_positions"),
            ("paper_risk_gate", "simulated_order_engine"),
            ("session_runtime", "paper_execution_loop"),
        ),
        blocked_edges=_dedupe(blocked),
    )


def detect_paper_runtime_blockers(
    data: PaperRuntimePreparationInput | Mapping[str, Any],
    virtual_portfolio_review: PaperRuntimeReviewSection | None = None,
    simulated_order_review: PaperRuntimeReviewSection | None = None,
    simulated_position_review: PaperRuntimeReviewSection | None = None,
    paper_risk_review: PaperRuntimeReviewSection | None = None,
    session_runtime_review: PaperRuntimeReviewSection | None = None,
) -> tuple[PaperRuntimeRisk, ...]:
    """Detect paper runtime preparation blockers."""

    data = _coerce_input(data)
    sections = (
        virtual_portfolio_review or verify_virtual_portfolio_readiness(data),
        simulated_order_review or verify_simulated_order_readiness(data),
        simulated_position_review or verify_simulated_position_readiness(data),
        paper_risk_review or verify_paper_risk_readiness(data),
        session_runtime_review or verify_session_runtime_readiness(data),
    )
    blockers: list[PaperRuntimeRisk] = []
    for section in sections:
        blockers.extend(section.risks)
    return _dedupe(blockers)


def compute_paper_runtime_score(
    data: PaperRuntimePreparationInput | Mapping[str, Any],
    blockers: tuple[PaperRuntimeRisk, ...] = (),
    virtual_portfolio_review: PaperRuntimeReviewSection | None = None,
    simulated_order_review: PaperRuntimeReviewSection | None = None,
    simulated_position_review: PaperRuntimeReviewSection | None = None,
    paper_risk_review: PaperRuntimeReviewSection | None = None,
    session_runtime_review: PaperRuntimeReviewSection | None = None,
) -> PaperRuntimeScore:
    """Compute paper runtime preparation score normalized to 0..100."""

    data = _coerce_input(data)
    portfolio = virtual_portfolio_review or verify_virtual_portfolio_readiness(data)
    orders = simulated_order_review or verify_simulated_order_readiness(data)
    positions = simulated_position_review or verify_simulated_position_readiness(data)
    risk = paper_risk_review or verify_paper_risk_readiness(data)
    session = session_runtime_review or verify_session_runtime_readiness(data)
    observability_score = data.paper_observability_score if data.paper_observability_score is not None else _average(
        (
            _bool_score(data.paper_observability_available),
            _upstream_score(data, "observability_score"),
        )
    )
    weighted = _weighted_average(
        (
            (portfolio.score, 1.1),
            (orders.score, 1.3),
            (positions.score, 1.05),
            (risk.score, 1.25),
            (session.score, 1.2),
            (observability_score, 0.8),
        )
    )
    penalty = min(70, len(set(blockers)) * 7)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        PaperRuntimeRisk.VIRTUAL_PORTFOLIO_MISSING: 50,
        PaperRuntimeRisk.SIMULATED_ORDER_ENGINE_MISSING: 45,
        PaperRuntimeRisk.PAPER_RISK_ENGINE_MISSING: 50,
        PaperRuntimeRisk.PAPER_EXECUTION_LEAK_RISK: 40,
        PaperRuntimeRisk.PAPER_RUNTIME_NOT_ISOLATED: 45,
        PaperRuntimeRisk.SESSION_RUNTIME_UNVERIFIED: 55,
    }
    for blocker, cap in critical_caps.items():
        if blocker in blockers:
            overall = min(overall, cap)
    return PaperRuntimeScore(
        overall_score=overall,
        virtual_portfolio_score=portfolio.score,
        simulated_order_score=orders.score,
        simulated_position_score=positions.score,
        paper_risk_score=risk.score,
        session_runtime_score=session.score,
        paper_observability_score=_clamp(observability_score),
    )


def _select_state(
    score: int,
    blockers: tuple[PaperRuntimeRisk, ...],
    ready_for_paper_execution_loop: bool | None,
) -> PaperRuntimePreparationState:
    count = len(set(blockers))
    hard = {
        PaperRuntimeRisk.VIRTUAL_PORTFOLIO_MISSING,
        PaperRuntimeRisk.SIMULATED_ORDER_ENGINE_MISSING,
        PaperRuntimeRisk.PAPER_RISK_ENGINE_MISSING,
        PaperRuntimeRisk.PAPER_EXECUTION_LEAK_RISK,
        PaperRuntimeRisk.PAPER_RUNTIME_NOT_ISOLATED,
    }
    if hard.intersection(blockers) or score < 45 or count >= 6:
        return PaperRuntimePreparationState.NOT_READY
    if count >= 3 or score < 72:
        return PaperRuntimePreparationState.REVIEW_REQUIRED
    if count:
        return PaperRuntimePreparationState.PARTIALLY_READY
    if score >= 94 and ready_for_paper_execution_loop is True:
        return PaperRuntimePreparationState.READY_FOR_PAPER_EXECUTION_LOOP
    if score >= 88:
        return PaperRuntimePreparationState.PAPER_RUNTIME_READY
    return PaperRuntimePreparationState.PARTIALLY_READY


def generate_paper_runtime_recommendations(
    blockers: tuple[PaperRuntimeRisk, ...],
    state: PaperRuntimePreparationState | None = None,
) -> tuple[PaperRuntimeRecommendation, ...]:
    """Generate paper runtime preparation recommendations."""

    recommendations: list[PaperRuntimeRecommendation] = []
    if blockers:
        recommendations.append(PaperRuntimeRecommendation.HOLD_PAPER_RUNTIME_APPROVAL)
    mapping = {
        PaperRuntimeRisk.VIRTUAL_PORTFOLIO_MISSING: PaperRuntimeRecommendation.CREATE_VIRTUAL_PORTFOLIO,
        PaperRuntimeRisk.SIMULATED_ORDER_ENGINE_MISSING: PaperRuntimeRecommendation.ENABLE_SIMULATED_ORDER_ENGINE,
        PaperRuntimeRisk.SIMULATED_POSITION_TRACKING_MISSING: PaperRuntimeRecommendation.ENABLE_SIMULATED_POSITION_TRACKING,
        PaperRuntimeRisk.PAPER_RISK_ENGINE_MISSING: PaperRuntimeRecommendation.ENABLE_PAPER_RISK_ENGINE,
        PaperRuntimeRisk.SESSION_RUNTIME_UNVERIFIED: PaperRuntimeRecommendation.VERIFY_SESSION_RUNTIME,
        PaperRuntimeRisk.PAPER_PNL_UNVERIFIED: PaperRuntimeRecommendation.VERIFY_PAPER_PNL,
        PaperRuntimeRisk.PAPER_STATE_CORRUPTION_RISK: PaperRuntimeRecommendation.PROTECT_PAPER_STATE,
        PaperRuntimeRisk.PAPER_EXECUTION_LEAK_RISK: PaperRuntimeRecommendation.SEAL_PAPER_EXECUTION_BOUNDARY,
        PaperRuntimeRisk.PAPER_OBSERVABILITY_GAP: PaperRuntimeRecommendation.ADD_PAPER_OBSERVABILITY,
        PaperRuntimeRisk.PAPER_RUNTIME_NOT_ISOLATED: PaperRuntimeRecommendation.ISOLATE_PAPER_RUNTIME,
    }
    recommendations.extend(mapping[blocker] for blocker in blockers)
    recommendations.append(PaperRuntimeRecommendation.RUN_PAPER_RUNTIME_PREPARATION_SUITE)
    if state == PaperRuntimePreparationState.READY_FOR_PAPER_EXECUTION_LOOP:
        recommendations.append(PaperRuntimeRecommendation.APPROVE_PAPER_EXECUTION_LOOP_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_paper_runtime_preparation(
    data: PaperRuntimePreparationInput | Mapping[str, Any],
) -> PaperRuntimePreparationResult:
    """Evaluate offline paper runtime readiness before the paper execution loop."""

    data = _coerce_input(data)
    portfolio = verify_virtual_portfolio_readiness(data)
    orders = verify_simulated_order_readiness(data)
    positions = verify_simulated_position_readiness(data)
    risk = verify_paper_risk_readiness(data)
    session = verify_session_runtime_readiness(data)
    blockers = detect_paper_runtime_blockers(data, portfolio, orders, positions, risk, session)
    score = compute_paper_runtime_score(data, blockers, portfolio, orders, positions, risk, session)
    state = _select_state(score.overall_score, blockers, data.ready_for_paper_execution_loop)
    graph = _build_paper_runtime_graph(blockers)
    recommendations = generate_paper_runtime_recommendations(blockers, state)
    offline_only = data.broker_connection_absent is True and not _has_upstream(data, "LIVE_EXECUTION", "API_ACCESS")
    summary = f"{state.value}: score={score.overall_score}, blockers={len(blockers)}, offline_only={offline_only}"
    return PaperRuntimePreparationResult(
        state=state,
        paper_runtime_score=score.overall_score,
        score_breakdown=score,
        blockers=blockers,
        virtual_portfolio_review=portfolio,
        simulated_order_review=orders,
        simulated_position_review=positions,
        paper_risk_review=risk,
        session_runtime_review=session,
        paper_runtime_graph=graph,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_paper_runtime_preparation_markdown(result: PaperRuntimePreparationResult) -> str:
    """Render an explainable paper runtime preparation report."""

    lines = [
        "# AGIcore Paper Runtime Preparation",
        f"- State: {result.state.value}",
        f"- Score: {result.paper_runtime_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Virtual portfolio: {result.score_breakdown.virtual_portfolio_score}/100",
        f"- Simulated order engine: {result.score_breakdown.simulated_order_score}/100",
        f"- Simulated positions: {result.score_breakdown.simulated_position_score}/100",
        f"- Paper risk: {result.score_breakdown.paper_risk_score}/100",
        f"- Session runtime: {result.score_breakdown.session_runtime_score}/100",
        f"- Paper observability: {result.score_breakdown.paper_observability_score}/100",
        "",
        "# Paper Runtime Reviews",
    ]
    for section in (
        result.virtual_portfolio_review,
        result.simulated_order_review,
        result.simulated_position_review,
        result.paper_risk_review,
        result.session_runtime_review,
    ):
        lines.append(
            f"- {section.name}: passed={section.passed}, score={section.score}/100, "
            f"blockers={', '.join(blocker.value for blocker in section.risks) or 'none'}"
        )
        lines.extend(f"  - {item}" for item in section.evidence)
    lines.append("")
    lines.append("# Paper Runtime Graph")
    lines.append(f"- Nodes: {', '.join(result.paper_runtime_graph.nodes)}")
    lines.extend(
        f"- Edge: {source} -> {target} ({label})"
        for source, target, label in result.paper_runtime_graph.edges
    )
    lines.append(
        "- Blocked edges: "
        + (
            ", ".join(f"{source}->{target}" for source, target in result.paper_runtime_graph.blocked_edges)
            or "none"
        )
    )
    lines.append("")
    lines.append("# Paper Runtime Blockers")
    lines.extend(f"- {blocker.value}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.append("")
    lines.append("# Paper Runtime Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# Preparation Outlook")
    if result.state == PaperRuntimePreparationState.READY_FOR_PAPER_EXECUTION_LOOP:
        lines.append("- Paper runtime is ready for manual paper execution loop review.")
    elif result.state == PaperRuntimePreparationState.PAPER_RUNTIME_READY:
        lines.append("- Paper runtime is ready; paper execution loop remains gated.")
    elif result.state == PaperRuntimePreparationState.PARTIALLY_READY:
        lines.append("- Paper runtime is partially ready and remaining blockers must be resolved.")
    else:
        lines.append("- Paper runtime approval should remain blocked.")
    return "\n".join(lines)


__all__ = [
    "compute_paper_runtime_score",
    "detect_paper_runtime_blockers",
    "evaluate_paper_runtime_preparation",
    "generate_paper_runtime_recommendations",
    "render_paper_runtime_preparation_markdown",
    "verify_paper_risk_readiness",
    "verify_session_runtime_readiness",
    "verify_simulated_order_readiness",
    "verify_simulated_position_readiness",
    "verify_virtual_portfolio_readiness",
]
