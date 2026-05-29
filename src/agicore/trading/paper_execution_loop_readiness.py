"""Offline paper execution loop readiness audit for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_execution_loop_readiness_models import (
    PaperExecutionLoopGraph,
    PaperExecutionLoopReadinessInput,
    PaperExecutionLoopReadinessResult,
    PaperExecutionLoopReadinessState,
    PaperExecutionLoopRecommendation,
    PaperExecutionLoopReviewSection,
    PaperExecutionLoopRisk,
    PaperExecutionLoopScore,
)


def _coerce_input(data: PaperExecutionLoopReadinessInput | Mapping[str, Any]) -> PaperExecutionLoopReadinessInput:
    if isinstance(data, PaperExecutionLoopReadinessInput):
        return data
    return PaperExecutionLoopReadinessInput(**dict(data))


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


def _upstream_blockers(data: PaperExecutionLoopReadinessInput) -> tuple[Any, ...]:
    upstream = (
        data.paper_runtime_preparation,
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


def _has_upstream(data: PaperExecutionLoopReadinessInput, *needles: str) -> bool:
    return _contains(_upstream_blockers(data), *needles)


def _upstream_score(data: PaperExecutionLoopReadinessInput, *names: str) -> int | None:
    upstream = (
        data.paper_runtime_preparation,
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


def verify_signal_input_readiness(
    data: PaperExecutionLoopReadinessInput | Mapping[str, Any],
) -> PaperExecutionLoopReviewSection:
    """Verify signal inputs before a controlled paper loop."""

    data = _coerce_input(data)
    score = _clamp(data.signal_input_score) if data.signal_input_score is not None else _average(
        (
            _bool_score(data.signal_source_available),
            _bool_score(data.context_signal_available),
            _bool_score(data.strategy_signal_available),
            _bool_score(data.signal_validation_enabled),
        ),
        default=45,
    )
    risks: list[PaperExecutionLoopRisk] = []
    if (
        data.signal_source_available is not True
        or data.context_signal_available is not True
        or data.strategy_signal_available is not True
        or data.signal_validation_enabled is not True
        or score < 85
    ):
        risks.append(PaperExecutionLoopRisk.SIGNAL_INPUT_MISSING)
    evidence = (
        f"signal_input_score={score}/100",
        f"signal_source_available={data.signal_source_available}",
        f"context_signal_available={data.context_signal_available}",
        f"strategy_signal_available={data.strategy_signal_available}",
        f"signal_validation_enabled={data.signal_validation_enabled}",
    )
    return PaperExecutionLoopReviewSection("signal_input_review", score, not risks and score >= 85, tuple(risks), evidence)


def verify_decision_pipeline_readiness(
    data: PaperExecutionLoopReadinessInput | Mapping[str, Any],
) -> PaperExecutionLoopReviewSection:
    """Verify semi-auto, context and strategy decision pipeline readiness."""

    data = _coerce_input(data)
    score = _clamp(data.decision_pipeline_score) if data.decision_pipeline_score is not None else _average(
        (
            _bool_score(data.semi_auto_decision_ready),
            _bool_score(data.context_scoring_connected),
            _bool_score(data.strategy_dna_connected),
            _bool_score(data.decision_output_deterministic),
        ),
        default=45,
    )
    risks: list[PaperExecutionLoopRisk] = []
    if (
        data.semi_auto_decision_ready is not True
        or data.context_scoring_connected is not True
        or data.strategy_dna_connected is not True
        or data.decision_output_deterministic is not True
        or score < 85
    ):
        risks.append(PaperExecutionLoopRisk.DECISION_PIPELINE_INCOMPLETE)
    if data.decision_output_deterministic is not True:
        risks.append(PaperExecutionLoopRisk.PAPER_LOOP_STATE_CORRUPTION_RISK)
    evidence = (
        f"decision_pipeline_score={score}/100",
        f"semi_auto_decision_ready={data.semi_auto_decision_ready}",
        f"context_scoring_connected={data.context_scoring_connected}",
        f"strategy_dna_connected={data.strategy_dna_connected}",
        f"decision_output_deterministic={data.decision_output_deterministic}",
    )
    return PaperExecutionLoopReviewSection("decision_pipeline_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_safety_gate_readiness(
    data: PaperExecutionLoopReadinessInput | Mapping[str, Any],
) -> PaperExecutionLoopReviewSection:
    """Verify risk, kill switch and rollback gates before the loop."""

    data = _coerce_input(data)
    score = _clamp(data.safety_gate_score) if data.safety_gate_score is not None else _average(
        (
            _bool_score(data.safety_prechecks_enabled),
            _bool_score(data.risk_engine_connected),
            _bool_score(data.kill_switch_linked),
            _bool_score(data.rollback_linked),
            _upstream_score(data, "kill_switch_score", "rollback_score"),
        ),
        default=45,
    )
    risks: list[PaperExecutionLoopRisk] = []
    if data.safety_prechecks_enabled is not True or score < 85:
        risks.append(PaperExecutionLoopRisk.SAFETY_GATE_UNVERIFIED)
    if data.risk_engine_connected is not True:
        risks.append(PaperExecutionLoopRisk.RISK_ENGINE_NOT_CONNECTED)
    if data.kill_switch_linked is not True or _has_upstream(data, "KILL_SWITCH_FAILURE"):
        risks.append(PaperExecutionLoopRisk.KILL_SWITCH_NOT_LINKED)
    if data.rollback_linked is not True or _has_upstream(data, "ROLLBACK_FAILURE"):
        risks.append(PaperExecutionLoopRisk.ROLLBACK_NOT_LINKED)
    evidence = (
        f"safety_gate_score={score}/100",
        f"safety_prechecks_enabled={data.safety_prechecks_enabled}",
        f"risk_engine_connected={data.risk_engine_connected}",
        f"kill_switch_linked={data.kill_switch_linked}",
        f"rollback_linked={data.rollback_linked}",
    )
    return PaperExecutionLoopReviewSection("safety_gate_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_simulated_execution_readiness(
    data: PaperExecutionLoopReadinessInput | Mapping[str, Any],
) -> PaperExecutionLoopReviewSection:
    """Verify simulated adapter and no-broker execution path readiness."""

    data = _coerce_input(data)
    score = _clamp(data.simulated_execution_score) if data.simulated_execution_score is not None else _average(
        (
            _bool_score(data.simulated_adapter_available),
            _bool_score(data.simulated_order_path_verified),
            _bool_score(data.real_broker_blocked),
            _bool_score(data.execution_events_emitted),
            _upstream_score(data, "paper_runtime_score", "isolation_score"),
        ),
        default=45,
    )
    risks: list[PaperExecutionLoopRisk] = []
    if (
        data.simulated_adapter_available is not True
        or data.simulated_order_path_verified is not True
        or score < 85
    ):
        risks.append(PaperExecutionLoopRisk.SIMULATED_EXECUTION_UNREADY)
    if data.real_broker_blocked is not True or _has_upstream(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS"):
        risks.append(PaperExecutionLoopRisk.SIMULATED_EXECUTION_UNREADY)
    if data.execution_events_emitted is not True:
        risks.append(PaperExecutionLoopRisk.OBSERVABILITY_BLIND_SPOT)
    evidence = (
        f"simulated_execution_score={score}/100",
        f"simulated_adapter_available={data.simulated_adapter_available}",
        f"simulated_order_path_verified={data.simulated_order_path_verified}",
        f"real_broker_blocked={data.real_broker_blocked}",
        f"execution_events_emitted={data.execution_events_emitted}",
    )
    return PaperExecutionLoopReviewSection("simulated_execution_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_paper_journal_readiness(
    data: PaperExecutionLoopReadinessInput | Mapping[str, Any],
) -> PaperExecutionLoopReviewSection:
    """Verify paper journal, PnL recording and loop observability."""

    data = _coerce_input(data)
    observability_score = data.loop_observability_score if data.loop_observability_score is not None else _average(
        (
            _bool_score(data.loop_observability_connected),
            _upstream_score(data, "observability_score"),
        )
    )
    score = _clamp(data.paper_journal_score) if data.paper_journal_score is not None else _average(
        (
            _bool_score(data.paper_journal_available),
            _bool_score(data.paper_trade_events_recorded),
            _bool_score(data.paper_pnl_recorded),
            _bool_score(data.paper_audit_export_available),
            _bool_score(data.paper_loop_state_checkpointed),
            observability_score,
        ),
        default=45,
    )
    risks: list[PaperExecutionLoopRisk] = []
    if (
        data.paper_journal_available is not True
        or data.paper_trade_events_recorded is not True
        or data.paper_audit_export_available is not True
        or score < 80
    ):
        risks.append(PaperExecutionLoopRisk.PAPER_JOURNAL_MISSING)
    if data.paper_pnl_recorded is not True:
        risks.append(PaperExecutionLoopRisk.PAPER_LOOP_STATE_CORRUPTION_RISK)
    if data.loop_observability_connected is not True or observability_score < 80:
        risks.append(PaperExecutionLoopRisk.OBSERVABILITY_BLIND_SPOT)
    if data.paper_loop_state_checkpointed is not True:
        risks.append(PaperExecutionLoopRisk.PAPER_LOOP_STATE_CORRUPTION_RISK)
    evidence = (
        f"paper_journal_score={score}/100",
        f"loop_observability_score={observability_score}/100",
        f"paper_journal_available={data.paper_journal_available}",
        f"paper_pnl_recorded={data.paper_pnl_recorded}",
        f"paper_loop_state_checkpointed={data.paper_loop_state_checkpointed}",
    )
    return PaperExecutionLoopReviewSection("paper_journal_review", score, not risks and score >= 80, _dedupe(risks), evidence)


def _build_paper_loop_graph(blockers: tuple[PaperExecutionLoopRisk, ...]) -> PaperExecutionLoopGraph:
    nodes = (
        "signal_inputs",
        "decision_pipeline",
        "safety_gate",
        "simulated_execution",
        "paper_journal",
        "controlled_paper_run",
    )
    edges = (
        ("signal_inputs", "decision_pipeline", "feeds"),
        ("decision_pipeline", "safety_gate", "gates"),
        ("safety_gate", "simulated_execution", "authorizes"),
        ("simulated_execution", "paper_journal", "records"),
        ("paper_journal", "controlled_paper_run", "audits"),
    )
    blocked: list[tuple[str, str]] = []
    if PaperExecutionLoopRisk.SIGNAL_INPUT_MISSING in blockers:
        blocked.append(("signal_inputs", "decision_pipeline"))
    if PaperExecutionLoopRisk.DECISION_PIPELINE_INCOMPLETE in blockers:
        blocked.append(("decision_pipeline", "safety_gate"))
    if (
        PaperExecutionLoopRisk.SAFETY_GATE_UNVERIFIED in blockers
        or PaperExecutionLoopRisk.RISK_ENGINE_NOT_CONNECTED in blockers
        or PaperExecutionLoopRisk.KILL_SWITCH_NOT_LINKED in blockers
        or PaperExecutionLoopRisk.ROLLBACK_NOT_LINKED in blockers
    ):
        blocked.append(("safety_gate", "simulated_execution"))
    if PaperExecutionLoopRisk.SIMULATED_EXECUTION_UNREADY in blockers:
        blocked.append(("simulated_execution", "paper_journal"))
    if PaperExecutionLoopRisk.PAPER_JOURNAL_MISSING in blockers:
        blocked.append(("paper_journal", "controlled_paper_run"))
    return PaperExecutionLoopGraph(
        nodes=nodes,
        edges=edges,
        ready_edges=(
            ("signal_inputs", "decision_pipeline"),
            ("decision_pipeline", "safety_gate"),
            ("safety_gate", "simulated_execution"),
            ("simulated_execution", "paper_journal"),
            ("paper_journal", "controlled_paper_run"),
        ),
        blocked_edges=_dedupe(blocked),
    )


def detect_paper_loop_blockers(
    data: PaperExecutionLoopReadinessInput | Mapping[str, Any],
    signal_input_review: PaperExecutionLoopReviewSection | None = None,
    decision_pipeline_review: PaperExecutionLoopReviewSection | None = None,
    safety_gate_review: PaperExecutionLoopReviewSection | None = None,
    simulated_execution_review: PaperExecutionLoopReviewSection | None = None,
    paper_journal_review: PaperExecutionLoopReviewSection | None = None,
) -> tuple[PaperExecutionLoopRisk, ...]:
    """Detect blockers for a controlled offline paper execution loop."""

    data = _coerce_input(data)
    sections = (
        signal_input_review or verify_signal_input_readiness(data),
        decision_pipeline_review or verify_decision_pipeline_readiness(data),
        safety_gate_review or verify_safety_gate_readiness(data),
        simulated_execution_review or verify_simulated_execution_readiness(data),
        paper_journal_review or verify_paper_journal_readiness(data),
    )
    blockers: list[PaperExecutionLoopRisk] = []
    for section in sections:
        blockers.extend(section.risks)
    return _dedupe(blockers)


def compute_paper_loop_score(
    data: PaperExecutionLoopReadinessInput | Mapping[str, Any],
    blockers: tuple[PaperExecutionLoopRisk, ...] = (),
    signal_input_review: PaperExecutionLoopReviewSection | None = None,
    decision_pipeline_review: PaperExecutionLoopReviewSection | None = None,
    safety_gate_review: PaperExecutionLoopReviewSection | None = None,
    simulated_execution_review: PaperExecutionLoopReviewSection | None = None,
    paper_journal_review: PaperExecutionLoopReviewSection | None = None,
) -> PaperExecutionLoopScore:
    """Compute paper execution loop readiness score normalized to 0..100."""

    data = _coerce_input(data)
    signal = signal_input_review or verify_signal_input_readiness(data)
    decision = decision_pipeline_review or verify_decision_pipeline_readiness(data)
    safety = safety_gate_review or verify_safety_gate_readiness(data)
    simulated = simulated_execution_review or verify_simulated_execution_readiness(data)
    journal = paper_journal_review or verify_paper_journal_readiness(data)
    observability_score = data.loop_observability_score if data.loop_observability_score is not None else _average(
        (
            _bool_score(data.loop_observability_connected),
            _upstream_score(data, "observability_score"),
        )
    )
    weighted = _weighted_average(
        (
            (signal.score, 1.15),
            (decision.score, 1.2),
            (safety.score, 1.3),
            (simulated.score, 1.25),
            (journal.score, 1.0),
            (observability_score, 0.8),
        )
    )
    penalty = min(70, len(set(blockers)) * 7)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        PaperExecutionLoopRisk.SIGNAL_INPUT_MISSING: 50,
        PaperExecutionLoopRisk.DECISION_PIPELINE_INCOMPLETE: 50,
        PaperExecutionLoopRisk.SAFETY_GATE_UNVERIFIED: 45,
        PaperExecutionLoopRisk.SIMULATED_EXECUTION_UNREADY: 45,
        PaperExecutionLoopRisk.RISK_ENGINE_NOT_CONNECTED: 45,
        PaperExecutionLoopRisk.KILL_SWITCH_NOT_LINKED: 50,
        PaperExecutionLoopRisk.ROLLBACK_NOT_LINKED: 55,
    }
    for blocker, cap in critical_caps.items():
        if blocker in blockers:
            overall = min(overall, cap)
    return PaperExecutionLoopScore(
        overall_score=overall,
        signal_input_score=signal.score,
        decision_pipeline_score=decision.score,
        safety_gate_score=safety.score,
        simulated_execution_score=simulated.score,
        paper_journal_score=journal.score,
        loop_observability_score=_clamp(observability_score),
    )


def _select_state(
    score: int,
    blockers: tuple[PaperExecutionLoopRisk, ...],
    ready_for_controlled_paper_run: bool | None,
) -> PaperExecutionLoopReadinessState:
    count = len(set(blockers))
    hard = {
        PaperExecutionLoopRisk.SIGNAL_INPUT_MISSING,
        PaperExecutionLoopRisk.DECISION_PIPELINE_INCOMPLETE,
        PaperExecutionLoopRisk.SAFETY_GATE_UNVERIFIED,
        PaperExecutionLoopRisk.SIMULATED_EXECUTION_UNREADY,
        PaperExecutionLoopRisk.RISK_ENGINE_NOT_CONNECTED,
    }
    if hard.intersection(blockers) or score < 45 or count >= 6:
        return PaperExecutionLoopReadinessState.NOT_READY
    if count >= 3 or score < 72:
        return PaperExecutionLoopReadinessState.REVIEW_REQUIRED
    if count:
        return PaperExecutionLoopReadinessState.PARTIALLY_READY
    if score >= 94 and ready_for_controlled_paper_run is True:
        return PaperExecutionLoopReadinessState.READY_FOR_CONTROLLED_PAPER_RUN
    if score >= 88:
        return PaperExecutionLoopReadinessState.PAPER_LOOP_READY
    return PaperExecutionLoopReadinessState.PARTIALLY_READY


def generate_paper_loop_recommendations(
    blockers: tuple[PaperExecutionLoopRisk, ...],
    state: PaperExecutionLoopReadinessState | None = None,
) -> tuple[PaperExecutionLoopRecommendation, ...]:
    """Generate paper execution loop readiness recommendations."""

    recommendations: list[PaperExecutionLoopRecommendation] = []
    if blockers:
        recommendations.append(PaperExecutionLoopRecommendation.HOLD_PAPER_LOOP_APPROVAL)
    mapping = {
        PaperExecutionLoopRisk.SIGNAL_INPUT_MISSING: PaperExecutionLoopRecommendation.CONNECT_SIGNAL_INPUTS,
        PaperExecutionLoopRisk.DECISION_PIPELINE_INCOMPLETE: PaperExecutionLoopRecommendation.COMPLETE_DECISION_PIPELINE,
        PaperExecutionLoopRisk.SAFETY_GATE_UNVERIFIED: PaperExecutionLoopRecommendation.VERIFY_SAFETY_GATE,
        PaperExecutionLoopRisk.SIMULATED_EXECUTION_UNREADY: PaperExecutionLoopRecommendation.PREPARE_SIMULATED_EXECUTION,
        PaperExecutionLoopRisk.PAPER_JOURNAL_MISSING: PaperExecutionLoopRecommendation.ENABLE_PAPER_JOURNAL,
        PaperExecutionLoopRisk.RISK_ENGINE_NOT_CONNECTED: PaperExecutionLoopRecommendation.CONNECT_RISK_ENGINE,
        PaperExecutionLoopRisk.OBSERVABILITY_BLIND_SPOT: PaperExecutionLoopRecommendation.ADD_LOOP_OBSERVABILITY,
        PaperExecutionLoopRisk.KILL_SWITCH_NOT_LINKED: PaperExecutionLoopRecommendation.LINK_KILL_SWITCH,
        PaperExecutionLoopRisk.ROLLBACK_NOT_LINKED: PaperExecutionLoopRecommendation.LINK_ROLLBACK,
        PaperExecutionLoopRisk.PAPER_LOOP_STATE_CORRUPTION_RISK: PaperExecutionLoopRecommendation.PROTECT_PAPER_LOOP_STATE,
    }
    recommendations.extend(mapping[blocker] for blocker in blockers)
    recommendations.append(PaperExecutionLoopRecommendation.RUN_PAPER_LOOP_READINESS_SUITE)
    if state == PaperExecutionLoopReadinessState.READY_FOR_CONTROLLED_PAPER_RUN:
        recommendations.append(PaperExecutionLoopRecommendation.APPROVE_CONTROLLED_PAPER_RUN_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_paper_execution_loop_readiness(
    data: PaperExecutionLoopReadinessInput | Mapping[str, Any],
) -> PaperExecutionLoopReadinessResult:
    """Evaluate whether AGIcore is ready for a controlled offline paper run."""

    data = _coerce_input(data)
    signal = verify_signal_input_readiness(data)
    decision = verify_decision_pipeline_readiness(data)
    safety = verify_safety_gate_readiness(data)
    simulated = verify_simulated_execution_readiness(data)
    journal = verify_paper_journal_readiness(data)
    blockers = detect_paper_loop_blockers(data, signal, decision, safety, simulated, journal)
    score = compute_paper_loop_score(data, blockers, signal, decision, safety, simulated, journal)
    state = _select_state(score.overall_score, blockers, data.ready_for_controlled_paper_run)
    graph = _build_paper_loop_graph(blockers)
    recommendations = generate_paper_loop_recommendations(blockers, state)
    offline_only = data.real_broker_blocked is True and not _has_upstream(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS")
    summary = f"{state.value}: score={score.overall_score}, blockers={len(blockers)}, offline_only={offline_only}"
    return PaperExecutionLoopReadinessResult(
        state=state,
        paper_loop_score=score.overall_score,
        score_breakdown=score,
        blockers=blockers,
        signal_input_review=signal,
        decision_pipeline_review=decision,
        safety_gate_review=safety,
        simulated_execution_review=simulated,
        paper_journal_review=journal,
        paper_loop_graph=graph,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_paper_execution_loop_readiness_markdown(result: PaperExecutionLoopReadinessResult) -> str:
    """Render an explainable paper execution loop readiness report."""

    lines = [
        "# AGIcore Paper Execution Loop Readiness",
        f"- State: {result.state.value}",
        f"- Score: {result.paper_loop_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Signal input: {result.score_breakdown.signal_input_score}/100",
        f"- Decision pipeline: {result.score_breakdown.decision_pipeline_score}/100",
        f"- Safety gate: {result.score_breakdown.safety_gate_score}/100",
        f"- Simulated execution: {result.score_breakdown.simulated_execution_score}/100",
        f"- Paper journal: {result.score_breakdown.paper_journal_score}/100",
        f"- Loop observability: {result.score_breakdown.loop_observability_score}/100",
        "",
        "# Paper Loop Reviews",
    ]
    for section in (
        result.signal_input_review,
        result.decision_pipeline_review,
        result.safety_gate_review,
        result.simulated_execution_review,
        result.paper_journal_review,
    ):
        lines.append(
            f"- {section.name}: passed={section.passed}, score={section.score}/100, "
            f"blockers={', '.join(blocker.value for blocker in section.risks) or 'none'}"
        )
        lines.extend(f"  - {item}" for item in section.evidence)
    lines.append("")
    lines.append("# Paper Loop Graph")
    lines.append(f"- Nodes: {', '.join(result.paper_loop_graph.nodes)}")
    lines.extend(
        f"- Edge: {source} -> {target} ({label})"
        for source, target, label in result.paper_loop_graph.edges
    )
    lines.append(
        "- Blocked edges: "
        + (
            ", ".join(f"{source}->{target}" for source, target in result.paper_loop_graph.blocked_edges)
            or "none"
        )
    )
    lines.append("")
    lines.append("# Paper Loop Blockers")
    lines.extend(f"- {blocker.value}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.append("")
    lines.append("# Paper Loop Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# Readiness Outlook")
    if result.state == PaperExecutionLoopReadinessState.READY_FOR_CONTROLLED_PAPER_RUN:
        lines.append("- Paper execution loop is ready for manual controlled paper run review.")
    elif result.state == PaperExecutionLoopReadinessState.PAPER_LOOP_READY:
        lines.append("- Paper execution loop is ready; controlled paper run remains gated.")
    elif result.state == PaperExecutionLoopReadinessState.PARTIALLY_READY:
        lines.append("- Paper execution loop is partially ready and remaining blockers must be resolved.")
    else:
        lines.append("- Paper execution loop approval should remain blocked.")
    return "\n".join(lines)


__all__ = [
    "compute_paper_loop_score",
    "detect_paper_loop_blockers",
    "evaluate_paper_execution_loop_readiness",
    "generate_paper_loop_recommendations",
    "render_paper_execution_loop_readiness_markdown",
    "verify_decision_pipeline_readiness",
    "verify_paper_journal_readiness",
    "verify_safety_gate_readiness",
    "verify_signal_input_readiness",
    "verify_simulated_execution_readiness",
]
