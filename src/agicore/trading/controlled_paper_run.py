"""Offline controlled paper run readiness audit for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.controlled_paper_run_models import (
    ControlledPaperRunGraph,
    ControlledPaperRunInput,
    ControlledPaperRunRecommendation,
    ControlledPaperRunResult,
    ControlledPaperRunReviewSection,
    ControlledPaperRunRisk,
    ControlledPaperRunScore,
    ControlledPaperRunState,
)


def _coerce_input(data: ControlledPaperRunInput | Mapping[str, Any]) -> ControlledPaperRunInput:
    if isinstance(data, ControlledPaperRunInput):
        return data
    return ControlledPaperRunInput(**dict(data))


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


def _upstream_items(data: ControlledPaperRunInput) -> tuple[Any, ...]:
    return (
        data.paper_execution_loop_readiness,
        data.paper_runtime_preparation,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.runtime_isolation_review,
        data.sandbox_readiness_audit,
        data.stable_review,
    )


def _upstream_risks(data: ControlledPaperRunInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream(data: ControlledPaperRunInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _upstream_score(data: ControlledPaperRunInput, *names: str) -> int | None:
    values: list[int] = []
    for item in _upstream_items(data):
        values.extend(_score(item, name) for name in names)
        breakdown = _get(item, "score_breakdown")
        values.extend(_score(breakdown, name) for name in names)
    values = [value for value in values if value is not None]
    return _average(values) if values else None


def verify_human_validation_gate(
    data: ControlledPaperRunInput | Mapping[str, Any],
) -> ControlledPaperRunReviewSection:
    """Verify that the controlled paper run is gated by explicit human validation."""

    data = _coerce_input(data)
    score = _clamp(data.human_validation_score) if data.human_validation_score is not None else _average(
        (
            _bool_score(data.human_operator_assigned),
            _bool_score(data.manual_approval_required),
            _bool_score(data.manual_approval_recorded),
            _bool_score(data.session_scope_acknowledged),
        ),
        default=45,
    )
    risks: list[ControlledPaperRunRisk] = []
    if (
        data.human_operator_assigned is not True
        or data.manual_approval_required is not True
        or data.manual_approval_recorded is not True
        or data.session_scope_acknowledged is not True
        or score < 85
    ):
        risks.append(ControlledPaperRunRisk.HUMAN_VALIDATION_MISSING)
    evidence = (
        f"human_validation_score={score}/100",
        f"human_operator_assigned={data.human_operator_assigned}",
        f"manual_approval_required={data.manual_approval_required}",
        f"manual_approval_recorded={data.manual_approval_recorded}",
        f"session_scope_acknowledged={data.session_scope_acknowledged}",
    )
    return ControlledPaperRunReviewSection("human_validation_review", score, not risks and score >= 85, tuple(risks), evidence)


def verify_simulated_trade_flow(
    data: ControlledPaperRunInput | Mapping[str, Any],
) -> ControlledPaperRunReviewSection:
    """Verify the purely simulated trade flow before any human validated session."""

    data = _coerce_input(data)
    score = _clamp(data.simulated_trade_flow_score) if data.simulated_trade_flow_score is not None else _average(
        (
            _bool_score(data.simulated_trade_flow_defined),
            _bool_score(data.paper_order_preview_available),
            _bool_score(data.paper_fill_simulation_available),
            _bool_score(data.paper_pnl_preview_available),
            _bool_score(data.flow_repeatable),
            _upstream_score(data, "paper_loop_score", "paper_runtime_score"),
        ),
        default=45,
    )
    risks: list[ControlledPaperRunRisk] = []
    if (
        data.simulated_trade_flow_defined is not True
        or data.paper_order_preview_available is not True
        or data.paper_fill_simulation_available is not True
        or data.paper_pnl_preview_available is not True
        or score < 85
    ):
        risks.append(ControlledPaperRunRisk.SIMULATED_TRADE_FLOW_INVALID)
    if data.flow_repeatable is not True:
        risks.append(ControlledPaperRunRisk.PAPER_EXECUTION_DRIFT)
    evidence = (
        f"simulated_trade_flow_score={score}/100",
        f"simulated_trade_flow_defined={data.simulated_trade_flow_defined}",
        f"paper_order_preview_available={data.paper_order_preview_available}",
        f"paper_fill_simulation_available={data.paper_fill_simulation_available}",
        f"paper_pnl_preview_available={data.paper_pnl_preview_available}",
        f"flow_repeatable={data.flow_repeatable}",
    )
    return ControlledPaperRunReviewSection("simulated_trade_flow_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_paper_session_controls(
    data: ControlledPaperRunInput | Mapping[str, Any],
) -> ControlledPaperRunReviewSection:
    """Verify bounded session controls, safety guards and repeatability."""

    data = _coerce_input(data)
    score = _clamp(data.paper_session_control_score) if data.paper_session_control_score is not None else _average(
        (
            _bool_score(data.session_limits_configured),
            _bool_score(data.risk_limits_enforced),
            _bool_score(data.safety_guards_locked),
            _bool_score(data.session_state_checkpointed),
            _bool_score(data.controlled_run_repeatable),
        ),
        default=45,
    )
    risks: list[ControlledPaperRunRisk] = []
    if data.session_limits_configured is not True or score < 85:
        risks.append(ControlledPaperRunRisk.PAPER_SESSION_CONTROL_FAILURE)
    if data.risk_limits_enforced is not True or data.safety_guards_locked is not True:
        risks.append(ControlledPaperRunRisk.SAFETY_GUARD_BYPASS)
    if data.session_state_checkpointed is not True:
        risks.append(ControlledPaperRunRisk.PAPER_SESSION_STATE_CORRUPTION)
    if data.controlled_run_repeatable is not True:
        risks.append(ControlledPaperRunRisk.CONTROLLED_RUN_NOT_REPEATABLE)
    evidence = (
        f"paper_session_control_score={score}/100",
        f"session_limits_configured={data.session_limits_configured}",
        f"risk_limits_enforced={data.risk_limits_enforced}",
        f"safety_guards_locked={data.safety_guards_locked}",
        f"session_state_checkpointed={data.session_state_checkpointed}",
        f"controlled_run_repeatable={data.controlled_run_repeatable}",
    )
    return ControlledPaperRunReviewSection("paper_session_controls_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_emergency_shutdown_path(
    data: ControlledPaperRunInput | Mapping[str, Any],
) -> ControlledPaperRunReviewSection:
    """Verify emergency shutdown can halt the simulated controlled run."""

    data = _coerce_input(data)
    score = _clamp(data.emergency_shutdown_score) if data.emergency_shutdown_score is not None else _average(
        (
            _bool_score(data.emergency_shutdown_available),
            _bool_score(data.kill_switch_linked),
            _bool_score(data.shutdown_drill_verified),
            _bool_score(data.post_shutdown_state_safe),
            _upstream_score(data, "kill_switch_score"),
        ),
        default=45,
    )
    risks: list[ControlledPaperRunRisk] = []
    if (
        data.emergency_shutdown_available is not True
        or data.kill_switch_linked is not True
        or data.shutdown_drill_verified is not True
        or score < 85
        or _has_upstream(data, "KILL_SWITCH_FAILURE", "SHUTDOWN_PATH_FAILURE")
    ):
        risks.append(ControlledPaperRunRisk.EMERGENCY_SHUTDOWN_UNAVAILABLE)
    if data.kill_switch_linked is not True:
        risks.append(ControlledPaperRunRisk.SAFETY_GUARD_BYPASS)
    if data.post_shutdown_state_safe is not True:
        risks.append(ControlledPaperRunRisk.PAPER_SESSION_STATE_CORRUPTION)
    evidence = (
        f"emergency_shutdown_score={score}/100",
        f"emergency_shutdown_available={data.emergency_shutdown_available}",
        f"kill_switch_linked={data.kill_switch_linked}",
        f"shutdown_drill_verified={data.shutdown_drill_verified}",
        f"post_shutdown_state_safe={data.post_shutdown_state_safe}",
    )
    return ControlledPaperRunReviewSection("emergency_shutdown_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_paper_recovery_path(
    data: ControlledPaperRunInput | Mapping[str, Any],
) -> ControlledPaperRunReviewSection:
    """Verify rollback-backed recovery and observability after a stopped paper run."""

    data = _coerce_input(data)
    observability_score = data.observability_score if data.observability_score is not None else _average(
        (
            _bool_score(data.observability_connected),
            _upstream_score(data, "observability_score"),
        )
    )
    score = _clamp(data.paper_recovery_score) if data.paper_recovery_score is not None else _average(
        (
            _bool_score(data.recovery_path_available),
            _bool_score(data.rollback_linked),
            _bool_score(data.recovery_drill_verified),
            _bool_score(data.post_recovery_state_consistent),
            observability_score,
            _upstream_score(data, "rollback_score"),
        ),
        default=45,
    )
    risks: list[ControlledPaperRunRisk] = []
    if (
        data.recovery_path_available is not True
        or data.rollback_linked is not True
        or data.recovery_drill_verified is not True
        or score < 85
        or _has_upstream(data, "ROLLBACK_FAILURE", "RECOVERY_PATH")
    ):
        risks.append(ControlledPaperRunRisk.RECOVERY_PATH_UNVERIFIED)
    if data.post_recovery_state_consistent is not True:
        risks.append(ControlledPaperRunRisk.PAPER_SESSION_STATE_CORRUPTION)
    if data.observability_connected is not True or observability_score < 80 or _has_upstream(data, "OBSERVABILITY"):
        risks.append(ControlledPaperRunRisk.OBSERVABILITY_LOSS)
    evidence = (
        f"paper_recovery_score={score}/100",
        f"observability_score={observability_score}/100",
        f"recovery_path_available={data.recovery_path_available}",
        f"rollback_linked={data.rollback_linked}",
        f"recovery_drill_verified={data.recovery_drill_verified}",
        f"post_recovery_state_consistent={data.post_recovery_state_consistent}",
        f"observability_connected={data.observability_connected}",
    )
    return ControlledPaperRunReviewSection("paper_recovery_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def _build_controlled_paper_graph(risks: tuple[ControlledPaperRunRisk, ...]) -> ControlledPaperRunGraph:
    nodes = (
        "human_operator",
        "validation_gate",
        "simulated_trade_flow",
        "session_controls",
        "emergency_shutdown",
        "recovery_path",
        "human_validated_session",
    )
    edges = (
        ("human_operator", "validation_gate", "approves"),
        ("validation_gate", "simulated_trade_flow", "authorizes"),
        ("simulated_trade_flow", "session_controls", "bounded_by"),
        ("session_controls", "emergency_shutdown", "guarded_by"),
        ("emergency_shutdown", "recovery_path", "falls_back_to"),
        ("recovery_path", "human_validated_session", "gates"),
    )
    blocked: list[tuple[str, str]] = []
    if ControlledPaperRunRisk.HUMAN_VALIDATION_MISSING in risks:
        blocked.append(("human_operator", "validation_gate"))
    if (
        ControlledPaperRunRisk.SIMULATED_TRADE_FLOW_INVALID in risks
        or ControlledPaperRunRisk.PAPER_EXECUTION_DRIFT in risks
    ):
        blocked.append(("validation_gate", "simulated_trade_flow"))
    if (
        ControlledPaperRunRisk.PAPER_SESSION_CONTROL_FAILURE in risks
        or ControlledPaperRunRisk.SAFETY_GUARD_BYPASS in risks
        or ControlledPaperRunRisk.PAPER_SESSION_STATE_CORRUPTION in risks
        or ControlledPaperRunRisk.CONTROLLED_RUN_NOT_REPEATABLE in risks
    ):
        blocked.append(("simulated_trade_flow", "session_controls"))
    if ControlledPaperRunRisk.EMERGENCY_SHUTDOWN_UNAVAILABLE in risks:
        blocked.append(("session_controls", "emergency_shutdown"))
    if (
        ControlledPaperRunRisk.RECOVERY_PATH_UNVERIFIED in risks
        or ControlledPaperRunRisk.OBSERVABILITY_LOSS in risks
    ):
        blocked.append(("emergency_shutdown", "recovery_path"))
    return ControlledPaperRunGraph(
        nodes=nodes,
        edges=edges,
        ready_edges=(
            ("human_operator", "validation_gate"),
            ("validation_gate", "simulated_trade_flow"),
            ("simulated_trade_flow", "session_controls"),
            ("session_controls", "emergency_shutdown"),
            ("emergency_shutdown", "recovery_path"),
            ("recovery_path", "human_validated_session"),
        ),
        blocked_edges=_dedupe(blocked),
    )


def detect_controlled_paper_risks(
    data: ControlledPaperRunInput | Mapping[str, Any],
    human_validation_review: ControlledPaperRunReviewSection | None = None,
    simulated_trade_flow_review: ControlledPaperRunReviewSection | None = None,
    paper_session_controls_review: ControlledPaperRunReviewSection | None = None,
    emergency_shutdown_review: ControlledPaperRunReviewSection | None = None,
    paper_recovery_review: ControlledPaperRunReviewSection | None = None,
) -> tuple[ControlledPaperRunRisk, ...]:
    """Detect risks that block a controlled offline paper run."""

    data = _coerce_input(data)
    sections = (
        human_validation_review or verify_human_validation_gate(data),
        simulated_trade_flow_review or verify_simulated_trade_flow(data),
        paper_session_controls_review or verify_paper_session_controls(data),
        emergency_shutdown_review or verify_emergency_shutdown_path(data),
        paper_recovery_review or verify_paper_recovery_path(data),
    )
    risks: list[ControlledPaperRunRisk] = []
    for section in sections:
        risks.extend(section.risks)
    return _dedupe(risks)


def compute_controlled_paper_score(
    data: ControlledPaperRunInput | Mapping[str, Any],
    risks: tuple[ControlledPaperRunRisk, ...] = (),
    human_validation_review: ControlledPaperRunReviewSection | None = None,
    simulated_trade_flow_review: ControlledPaperRunReviewSection | None = None,
    paper_session_controls_review: ControlledPaperRunReviewSection | None = None,
    emergency_shutdown_review: ControlledPaperRunReviewSection | None = None,
    paper_recovery_review: ControlledPaperRunReviewSection | None = None,
) -> ControlledPaperRunScore:
    """Compute controlled paper run readiness score normalized to 0..100."""

    data = _coerce_input(data)
    human = human_validation_review or verify_human_validation_gate(data)
    flow = simulated_trade_flow_review or verify_simulated_trade_flow(data)
    controls = paper_session_controls_review or verify_paper_session_controls(data)
    shutdown = emergency_shutdown_review or verify_emergency_shutdown_path(data)
    recovery = paper_recovery_review or verify_paper_recovery_path(data)
    observability_score = data.observability_score if data.observability_score is not None else _average(
        (
            _bool_score(data.observability_connected),
            _upstream_score(data, "observability_score"),
        )
    )
    weighted = _weighted_average(
        (
            (human.score, 1.35),
            (flow.score, 1.15),
            (controls.score, 1.3),
            (shutdown.score, 1.25),
            (recovery.score, 1.15),
            (observability_score, 0.85),
        )
    )
    penalty = min(72, len(set(risks)) * 7)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        ControlledPaperRunRisk.HUMAN_VALIDATION_MISSING: 45,
        ControlledPaperRunRisk.PAPER_SESSION_CONTROL_FAILURE: 50,
        ControlledPaperRunRisk.SIMULATED_TRADE_FLOW_INVALID: 50,
        ControlledPaperRunRisk.EMERGENCY_SHUTDOWN_UNAVAILABLE: 45,
        ControlledPaperRunRisk.RECOVERY_PATH_UNVERIFIED: 50,
        ControlledPaperRunRisk.SAFETY_GUARD_BYPASS: 45,
    }
    for risk, cap in critical_caps.items():
        if risk in risks:
            overall = min(overall, cap)
    return ControlledPaperRunScore(
        overall_score=overall,
        human_validation_score=human.score,
        simulated_trade_flow_score=flow.score,
        paper_session_control_score=controls.score,
        emergency_shutdown_score=shutdown.score,
        paper_recovery_score=recovery.score,
        observability_score=_clamp(observability_score),
    )


def _select_state(
    score: int,
    risks: tuple[ControlledPaperRunRisk, ...],
    ready_for_human_validated_session: bool | None,
) -> ControlledPaperRunState:
    count = len(set(risks))
    hard = {
        ControlledPaperRunRisk.HUMAN_VALIDATION_MISSING,
        ControlledPaperRunRisk.PAPER_SESSION_CONTROL_FAILURE,
        ControlledPaperRunRisk.SIMULATED_TRADE_FLOW_INVALID,
        ControlledPaperRunRisk.EMERGENCY_SHUTDOWN_UNAVAILABLE,
        ControlledPaperRunRisk.RECOVERY_PATH_UNVERIFIED,
        ControlledPaperRunRisk.SAFETY_GUARD_BYPASS,
    }
    if hard.intersection(risks) or score < 45 or count >= 6:
        return ControlledPaperRunState.NOT_READY
    if count >= 3 or score < 72:
        return ControlledPaperRunState.REVIEW_REQUIRED
    if count:
        return ControlledPaperRunState.PARTIALLY_READY
    if score >= 94 and ready_for_human_validated_session is True:
        return ControlledPaperRunState.READY_FOR_HUMAN_VALIDATED_SESSION
    if score >= 88:
        return ControlledPaperRunState.CONTROLLED_PAPER_READY
    return ControlledPaperRunState.PARTIALLY_READY


def generate_controlled_paper_recommendations(
    risks: tuple[ControlledPaperRunRisk, ...],
    state: ControlledPaperRunState | None = None,
) -> tuple[ControlledPaperRunRecommendation, ...]:
    """Generate controlled paper run recommendations."""

    recommendations: list[ControlledPaperRunRecommendation] = []
    if risks:
        recommendations.append(ControlledPaperRunRecommendation.HOLD_CONTROLLED_PAPER_RUN_APPROVAL)
    mapping = {
        ControlledPaperRunRisk.HUMAN_VALIDATION_MISSING: ControlledPaperRunRecommendation.REQUIRE_HUMAN_VALIDATION_GATE,
        ControlledPaperRunRisk.PAPER_SESSION_CONTROL_FAILURE: ControlledPaperRunRecommendation.REPAIR_PAPER_SESSION_CONTROLS,
        ControlledPaperRunRisk.SIMULATED_TRADE_FLOW_INVALID: ControlledPaperRunRecommendation.VALIDATE_SIMULATED_TRADE_FLOW,
        ControlledPaperRunRisk.EMERGENCY_SHUTDOWN_UNAVAILABLE: ControlledPaperRunRecommendation.VERIFY_EMERGENCY_SHUTDOWN_PATH,
        ControlledPaperRunRisk.RECOVERY_PATH_UNVERIFIED: ControlledPaperRunRecommendation.VERIFY_PAPER_RECOVERY_PATH,
        ControlledPaperRunRisk.PAPER_SESSION_STATE_CORRUPTION: ControlledPaperRunRecommendation.PROTECT_PAPER_SESSION_STATE,
        ControlledPaperRunRisk.PAPER_EXECUTION_DRIFT: ControlledPaperRunRecommendation.LOCK_EXECUTION_DETERMINISM,
        ControlledPaperRunRisk.SAFETY_GUARD_BYPASS: ControlledPaperRunRecommendation.ENFORCE_SAFETY_GUARDS,
        ControlledPaperRunRisk.OBSERVABILITY_LOSS: ControlledPaperRunRecommendation.RESTORE_OBSERVABILITY_COVERAGE,
        ControlledPaperRunRisk.CONTROLLED_RUN_NOT_REPEATABLE: ControlledPaperRunRecommendation.MAKE_CONTROLLED_RUN_REPEATABLE,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(ControlledPaperRunRecommendation.RUN_CONTROLLED_PAPER_READINESS_SUITE)
    if state == ControlledPaperRunState.READY_FOR_HUMAN_VALIDATED_SESSION:
        recommendations.append(ControlledPaperRunRecommendation.APPROVE_HUMAN_VALIDATED_SESSION_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_controlled_paper_run(
    data: ControlledPaperRunInput | Mapping[str, Any],
) -> ControlledPaperRunResult:
    """Evaluate whether AGIcore is ready for a supervised offline controlled paper run."""

    data = _coerce_input(data)
    human = verify_human_validation_gate(data)
    flow = verify_simulated_trade_flow(data)
    controls = verify_paper_session_controls(data)
    shutdown = verify_emergency_shutdown_path(data)
    recovery = verify_paper_recovery_path(data)
    risks = detect_controlled_paper_risks(data, human, flow, controls, shutdown, recovery)
    score = compute_controlled_paper_score(data, risks, human, flow, controls, shutdown, recovery)
    state = _select_state(score.overall_score, risks, data.ready_for_human_validated_session)
    graph = _build_controlled_paper_graph(risks)
    recommendations = generate_controlled_paper_recommendations(risks, state)
    offline_only = not _has_upstream(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK")
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return ControlledPaperRunResult(
        state=state,
        controlled_paper_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        human_validation_review=human,
        simulated_trade_flow_review=flow,
        paper_session_controls_review=controls,
        emergency_shutdown_review=shutdown,
        paper_recovery_review=recovery,
        controlled_paper_graph=graph,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_controlled_paper_markdown(result: ControlledPaperRunResult) -> str:
    """Render an explainable controlled paper run readiness report."""

    lines = [
        "# AGIcore Controlled Paper Run",
        f"- State: {result.state.value}",
        f"- Score: {result.controlled_paper_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Human validation: {result.score_breakdown.human_validation_score}/100",
        f"- Simulated trade flow: {result.score_breakdown.simulated_trade_flow_score}/100",
        f"- Paper session controls: {result.score_breakdown.paper_session_control_score}/100",
        f"- Emergency shutdown: {result.score_breakdown.emergency_shutdown_score}/100",
        f"- Paper recovery: {result.score_breakdown.paper_recovery_score}/100",
        f"- Observability: {result.score_breakdown.observability_score}/100",
        "",
        "# Controlled Paper Reviews",
    ]
    for section in (
        result.human_validation_review,
        result.simulated_trade_flow_review,
        result.paper_session_controls_review,
        result.emergency_shutdown_review,
        result.paper_recovery_review,
    ):
        lines.append(
            f"- {section.name}: passed={section.passed}, score={section.score}/100, "
            f"risks={', '.join(risk.value for risk in section.risks) or 'none'}"
        )
        lines.extend(f"  - {item}" for item in section.evidence)
    lines.append("")
    lines.append("# Controlled Paper Graph")
    lines.append(f"- Nodes: {', '.join(result.controlled_paper_graph.nodes)}")
    lines.extend(
        f"- Edge: {source} -> {target} ({label})"
        for source, target, label in result.controlled_paper_graph.edges
    )
    lines.append(
        "- Blocked edges: "
        + (
            ", ".join(f"{source}->{target}" for source, target in result.controlled_paper_graph.blocked_edges)
            or "none"
        )
    )
    lines.append("")
    lines.append("# Controlled Paper Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Controlled Paper Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# Readiness Outlook")
    if result.state == ControlledPaperRunState.READY_FOR_HUMAN_VALIDATED_SESSION:
        lines.append("- Controlled paper run is ready for a human validated paper session.")
    elif result.state == ControlledPaperRunState.CONTROLLED_PAPER_READY:
        lines.append("- Controlled paper run is ready; human validated session remains gated.")
    elif result.state == ControlledPaperRunState.PARTIALLY_READY:
        lines.append("- Controlled paper run is partially ready and remaining risks must be resolved.")
    else:
        lines.append("- Controlled paper run approval should remain blocked.")
    return "\n".join(lines)


__all__ = [
    "compute_controlled_paper_score",
    "detect_controlled_paper_risks",
    "evaluate_controlled_paper_run",
    "generate_controlled_paper_recommendations",
    "render_controlled_paper_markdown",
    "verify_emergency_shutdown_path",
    "verify_human_validation_gate",
    "verify_paper_recovery_path",
    "verify_paper_session_controls",
    "verify_simulated_trade_flow",
]
