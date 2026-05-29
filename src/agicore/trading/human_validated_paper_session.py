"""Offline human validated paper session readiness audit for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.human_validated_paper_session_models import (
    HumanValidatedPaperSessionGraph,
    HumanValidatedPaperSessionInput,
    HumanValidatedPaperSessionResult,
    HumanValidatedPaperSessionReviewSection,
    HumanValidatedPaperSessionScore,
    HumanValidatedPaperSessionState,
    HumanValidationRecommendation,
    HumanValidationRisk,
)


def _coerce_input(
    data: HumanValidatedPaperSessionInput | Mapping[str, Any],
) -> HumanValidatedPaperSessionInput:
    if isinstance(data, HumanValidatedPaperSessionInput):
        return data
    return HumanValidatedPaperSessionInput(**dict(data))


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


def _upstream_items(data: HumanValidatedPaperSessionInput) -> tuple[Any, ...]:
    return (
        data.controlled_paper_run,
        data.paper_execution_loop_readiness,
        data.paper_runtime_preparation,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.runtime_isolation_review,
        data.sandbox_readiness_audit,
        data.stable_review,
    )


def _upstream_risks(data: HumanValidatedPaperSessionInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream(data: HumanValidatedPaperSessionInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _upstream_score(data: HumanValidatedPaperSessionInput, *names: str) -> int | None:
    values: list[int] = []
    for item in _upstream_items(data):
        values.extend(_score(item, name) for name in names)
        breakdown = _get(item, "score_breakdown")
        values.extend(_score(breakdown, name) for name in names)
    values = [value for value in values if value is not None]
    return _average(values) if values else None


def verify_human_approval_gate(
    data: HumanValidatedPaperSessionInput | Mapping[str, Any],
) -> HumanValidatedPaperSessionReviewSection:
    """Verify explicit human approval before a supervised paper session."""

    data = _coerce_input(data)
    score = _clamp(data.human_approval_score) if data.human_approval_score is not None else _average(
        (
            _bool_score(data.assigned_operator_present),
            _bool_score(data.explicit_approval_required),
            _bool_score(data.explicit_approval_captured),
            _bool_score(data.approval_timestamp_recorded),
            _bool_score(data.session_scope_confirmed),
        ),
        default=45,
    )
    risks: list[HumanValidationRisk] = []
    if (
        data.assigned_operator_present is not True
        or data.explicit_approval_required is not True
        or data.explicit_approval_captured is not True
        or data.approval_timestamp_recorded is not True
        or data.session_scope_confirmed is not True
        or score < 85
        or _has_upstream(data, "HUMAN_VALIDATION_MISSING")
    ):
        risks.append(HumanValidationRisk.HUMAN_APPROVAL_MISSING)
    evidence = (
        f"human_approval_score={score}/100",
        f"assigned_operator_present={data.assigned_operator_present}",
        f"explicit_approval_required={data.explicit_approval_required}",
        f"explicit_approval_captured={data.explicit_approval_captured}",
        f"approval_timestamp_recorded={data.approval_timestamp_recorded}",
        f"session_scope_confirmed={data.session_scope_confirmed}",
    )
    return HumanValidatedPaperSessionReviewSection("human_approval_review", score, not risks and score >= 85, tuple(risks), evidence)


def verify_operator_confirmation_flow(
    data: HumanValidatedPaperSessionInput | Mapping[str, Any],
) -> HumanValidatedPaperSessionReviewSection:
    """Verify operator identity, confirmation and override availability."""

    data = _coerce_input(data)
    score = (
        _clamp(data.operator_confirmation_score)
        if data.operator_confirmation_score is not None
        else _average(
            (
                _bool_score(data.operator_identity_verified),
                _bool_score(data.confirmation_challenge_completed),
                _bool_score(data.risk_acknowledgement_recorded),
                _bool_score(data.dry_run_acknowledged),
                _bool_score(data.human_override_available),
            ),
            default=45,
        )
    )
    risks: list[HumanValidationRisk] = []
    if (
        data.operator_identity_verified is not True
        or data.confirmation_challenge_completed is not True
        or data.risk_acknowledgement_recorded is not True
        or data.dry_run_acknowledged is not True
        or score < 85
    ):
        risks.append(HumanValidationRisk.OPERATOR_CONFIRMATION_FAILURE)
    if data.human_override_available is not True:
        risks.append(HumanValidationRisk.HUMAN_OVERRIDE_UNAVAILABLE)
    evidence = (
        f"operator_confirmation_score={score}/100",
        f"operator_identity_verified={data.operator_identity_verified}",
        f"confirmation_challenge_completed={data.confirmation_challenge_completed}",
        f"risk_acknowledgement_recorded={data.risk_acknowledgement_recorded}",
        f"dry_run_acknowledged={data.dry_run_acknowledged}",
        f"human_override_available={data.human_override_available}",
    )
    return HumanValidatedPaperSessionReviewSection("operator_confirmation_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_session_authorization(
    data: HumanValidatedPaperSessionInput | Mapping[str, Any],
) -> HumanValidatedPaperSessionReviewSection:
    """Verify scoped authorization for offline paper-only supervised execution."""

    data = _coerce_input(data)
    score = (
        _clamp(data.session_authorization_score)
        if data.session_authorization_score is not None
        else _average(
            (
                _bool_score(data.session_id_assigned),
                _bool_score(data.session_limits_authorized),
                _bool_score(data.paper_only_authorized),
                _bool_score(data.autonomy_disabled),
                _bool_score(data.validation_bypass_blocked),
                _upstream_score(data, "controlled_paper_score", "paper_loop_score"),
            ),
            default=45,
        )
    )
    risks: list[HumanValidationRisk] = []
    if (
        data.session_id_assigned is not True
        or data.session_limits_authorized is not True
        or data.paper_only_authorized is not True
        or score < 85
    ):
        risks.append(HumanValidationRisk.SESSION_AUTHORIZATION_MISSING)
    if data.autonomy_disabled is not True:
        risks.append(HumanValidationRisk.SUPERVISION_GAP)
    if data.validation_bypass_blocked is not True:
        risks.append(HumanValidationRisk.VALIDATION_BYPASS_RISK)
    evidence = (
        f"session_authorization_score={score}/100",
        f"session_id_assigned={data.session_id_assigned}",
        f"session_limits_authorized={data.session_limits_authorized}",
        f"paper_only_authorized={data.paper_only_authorized}",
        f"autonomy_disabled={data.autonomy_disabled}",
        f"validation_bypass_blocked={data.validation_bypass_blocked}",
    )
    return HumanValidatedPaperSessionReviewSection("session_authorization_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_auditability_requirements(
    data: HumanValidatedPaperSessionInput | Mapping[str, Any],
) -> HumanValidatedPaperSessionReviewSection:
    """Verify audit trail, decision traceability and observability requirements."""

    data = _coerce_input(data)
    supervision_score = data.supervision_score if data.supervision_score is not None else _average(
        (
            _bool_score(data.observability_linked),
            _upstream_score(data, "observability_score"),
        )
    )
    score = _clamp(data.auditability_score) if data.auditability_score is not None else _average(
        (
            _bool_score(data.audit_trail_enabled),
            _bool_score(data.decision_trace_enabled),
            _bool_score(data.operator_actions_logged),
            _bool_score(data.session_events_exportable),
            _bool_score(data.observability_linked),
            supervision_score,
        ),
        default=45,
    )
    risks: list[HumanValidationRisk] = []
    if (
        data.audit_trail_enabled is not True
        or data.operator_actions_logged is not True
        or data.session_events_exportable is not True
        or score < 85
    ):
        risks.append(HumanValidationRisk.AUDIT_TRAIL_INCOMPLETE)
    if data.decision_trace_enabled is not True:
        risks.append(HumanValidationRisk.DECISION_TRACEABILITY_LOSS)
    if data.observability_linked is not True or supervision_score < 80 or _has_upstream(data, "OBSERVABILITY"):
        risks.append(HumanValidationRisk.SUPERVISION_GAP)
    evidence = (
        f"auditability_score={score}/100",
        f"supervision_score={supervision_score}/100",
        f"audit_trail_enabled={data.audit_trail_enabled}",
        f"decision_trace_enabled={data.decision_trace_enabled}",
        f"operator_actions_logged={data.operator_actions_logged}",
        f"session_events_exportable={data.session_events_exportable}",
        f"observability_linked={data.observability_linked}",
    )
    return HumanValidatedPaperSessionReviewSection("auditability_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_reversibility_requirements(
    data: HumanValidatedPaperSessionInput | Mapping[str, Any],
) -> HumanValidatedPaperSessionReviewSection:
    """Verify rollback, kill switch and drift controls for supervised paper recovery."""

    data = _coerce_input(data)
    score = _clamp(data.reversibility_score) if data.reversibility_score is not None else _average(
        (
            _bool_score(data.rollback_plan_attached),
            _bool_score(data.kill_switch_attached),
            _bool_score(data.recovery_checkpoint_available),
            _bool_score(data.reversal_drill_recorded),
            _bool_score(data.session_drift_monitoring_enabled),
            _upstream_score(data, "rollback_score", "kill_switch_score"),
        ),
        default=45,
    )
    risks: list[HumanValidationRisk] = []
    if (
        data.rollback_plan_attached is not True
        or data.kill_switch_attached is not True
        or data.recovery_checkpoint_available is not True
        or data.reversal_drill_recorded is not True
        or score < 85
        or _has_upstream(data, "ROLLBACK", "KILL_SWITCH", "RECOVERY_PATH_UNVERIFIED")
    ):
        risks.append(HumanValidationRisk.REVERSIBILITY_NOT_VERIFIED)
    if data.session_drift_monitoring_enabled is not True or _has_upstream(data, "DRIFT"):
        risks.append(HumanValidationRisk.PAPER_SESSION_DRIFT)
    evidence = (
        f"reversibility_score={score}/100",
        f"rollback_plan_attached={data.rollback_plan_attached}",
        f"kill_switch_attached={data.kill_switch_attached}",
        f"recovery_checkpoint_available={data.recovery_checkpoint_available}",
        f"reversal_drill_recorded={data.reversal_drill_recorded}",
        f"session_drift_monitoring_enabled={data.session_drift_monitoring_enabled}",
    )
    return HumanValidatedPaperSessionReviewSection("reversibility_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def _build_human_validation_graph(risks: tuple[HumanValidationRisk, ...]) -> HumanValidatedPaperSessionGraph:
    nodes = (
        "human_approval_gate",
        "operator_confirmation",
        "session_authorization",
        "auditability",
        "reversibility",
        "supervised_paper_session",
    )
    edges = (
        ("human_approval_gate", "operator_confirmation", "requires"),
        ("operator_confirmation", "session_authorization", "confirms"),
        ("session_authorization", "auditability", "records"),
        ("auditability", "reversibility", "observes"),
        ("reversibility", "supervised_paper_session", "gates"),
    )
    blocked: list[tuple[str, str]] = []
    if HumanValidationRisk.HUMAN_APPROVAL_MISSING in risks:
        blocked.append(("human_approval_gate", "operator_confirmation"))
    if (
        HumanValidationRisk.OPERATOR_CONFIRMATION_FAILURE in risks
        or HumanValidationRisk.HUMAN_OVERRIDE_UNAVAILABLE in risks
    ):
        blocked.append(("operator_confirmation", "session_authorization"))
    if (
        HumanValidationRisk.SESSION_AUTHORIZATION_MISSING in risks
        or HumanValidationRisk.VALIDATION_BYPASS_RISK in risks
        or HumanValidationRisk.SUPERVISION_GAP in risks
    ):
        blocked.append(("session_authorization", "auditability"))
    if (
        HumanValidationRisk.AUDIT_TRAIL_INCOMPLETE in risks
        or HumanValidationRisk.DECISION_TRACEABILITY_LOSS in risks
    ):
        blocked.append(("auditability", "reversibility"))
    if (
        HumanValidationRisk.REVERSIBILITY_NOT_VERIFIED in risks
        or HumanValidationRisk.PAPER_SESSION_DRIFT in risks
    ):
        blocked.append(("reversibility", "supervised_paper_session"))
    return HumanValidatedPaperSessionGraph(
        nodes=nodes,
        edges=edges,
        ready_edges=(
            ("human_approval_gate", "operator_confirmation"),
            ("operator_confirmation", "session_authorization"),
            ("session_authorization", "auditability"),
            ("auditability", "reversibility"),
            ("reversibility", "supervised_paper_session"),
        ),
        blocked_edges=_dedupe(blocked),
    )


def detect_human_validation_risks(
    data: HumanValidatedPaperSessionInput | Mapping[str, Any],
    human_approval_review: HumanValidatedPaperSessionReviewSection | None = None,
    operator_confirmation_review: HumanValidatedPaperSessionReviewSection | None = None,
    session_authorization_review: HumanValidatedPaperSessionReviewSection | None = None,
    auditability_review: HumanValidatedPaperSessionReviewSection | None = None,
    reversibility_review: HumanValidatedPaperSessionReviewSection | None = None,
) -> tuple[HumanValidationRisk, ...]:
    """Detect risks that block a human validated paper session."""

    data = _coerce_input(data)
    sections = (
        human_approval_review or verify_human_approval_gate(data),
        operator_confirmation_review or verify_operator_confirmation_flow(data),
        session_authorization_review or verify_session_authorization(data),
        auditability_review or verify_auditability_requirements(data),
        reversibility_review or verify_reversibility_requirements(data),
    )
    risks: list[HumanValidationRisk] = []
    for section in sections:
        risks.extend(section.risks)
    return _dedupe(risks)


def compute_human_validation_score(
    data: HumanValidatedPaperSessionInput | Mapping[str, Any],
    risks: tuple[HumanValidationRisk, ...] = (),
    human_approval_review: HumanValidatedPaperSessionReviewSection | None = None,
    operator_confirmation_review: HumanValidatedPaperSessionReviewSection | None = None,
    session_authorization_review: HumanValidatedPaperSessionReviewSection | None = None,
    auditability_review: HumanValidatedPaperSessionReviewSection | None = None,
    reversibility_review: HumanValidatedPaperSessionReviewSection | None = None,
) -> HumanValidatedPaperSessionScore:
    """Compute human validation readiness score normalized to 0..100."""

    data = _coerce_input(data)
    approval = human_approval_review or verify_human_approval_gate(data)
    operator = operator_confirmation_review or verify_operator_confirmation_flow(data)
    authorization = session_authorization_review or verify_session_authorization(data)
    auditability = auditability_review or verify_auditability_requirements(data)
    reversibility = reversibility_review or verify_reversibility_requirements(data)
    supervision_score = data.supervision_score if data.supervision_score is not None else _average(
        (
            _bool_score(data.observability_linked),
            _bool_score(data.human_override_available),
            _upstream_score(data, "observability_score", "controlled_paper_score"),
        )
    )
    weighted = _weighted_average(
        (
            (approval.score, 1.35),
            (operator.score, 1.2),
            (authorization.score, 1.3),
            (auditability.score, 1.15),
            (reversibility.score, 1.2),
            (supervision_score, 0.9),
        )
    )
    penalty = min(72, len(set(risks)) * 7)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        HumanValidationRisk.HUMAN_APPROVAL_MISSING: 45,
        HumanValidationRisk.OPERATOR_CONFIRMATION_FAILURE: 50,
        HumanValidationRisk.SESSION_AUTHORIZATION_MISSING: 50,
        HumanValidationRisk.REVERSIBILITY_NOT_VERIFIED: 50,
        HumanValidationRisk.HUMAN_OVERRIDE_UNAVAILABLE: 55,
        HumanValidationRisk.VALIDATION_BYPASS_RISK: 45,
    }
    for risk, cap in critical_caps.items():
        if risk in risks:
            overall = min(overall, cap)
    return HumanValidatedPaperSessionScore(
        overall_score=overall,
        human_approval_score=approval.score,
        operator_confirmation_score=operator.score,
        session_authorization_score=authorization.score,
        auditability_score=auditability.score,
        reversibility_score=reversibility.score,
        supervision_score=_clamp(supervision_score),
    )


def _select_state(
    score: int,
    risks: tuple[HumanValidationRisk, ...],
    ready_for_supervised_paper_session: bool | None,
) -> HumanValidatedPaperSessionState:
    count = len(set(risks))
    hard = {
        HumanValidationRisk.HUMAN_APPROVAL_MISSING,
        HumanValidationRisk.OPERATOR_CONFIRMATION_FAILURE,
        HumanValidationRisk.SESSION_AUTHORIZATION_MISSING,
        HumanValidationRisk.REVERSIBILITY_NOT_VERIFIED,
        HumanValidationRisk.HUMAN_OVERRIDE_UNAVAILABLE,
        HumanValidationRisk.VALIDATION_BYPASS_RISK,
    }
    if hard.intersection(risks) or score < 45 or count >= 6:
        return HumanValidatedPaperSessionState.NOT_READY
    if count >= 3 or score < 72:
        return HumanValidatedPaperSessionState.REVIEW_REQUIRED
    if count:
        return HumanValidatedPaperSessionState.PARTIALLY_READY
    if score >= 94 and ready_for_supervised_paper_session is True:
        return HumanValidatedPaperSessionState.READY_FOR_SUPERVISED_PAPER_SESSION
    if score >= 88:
        return HumanValidatedPaperSessionState.HUMAN_VALIDATION_READY
    return HumanValidatedPaperSessionState.PARTIALLY_READY


def generate_human_validation_recommendations(
    risks: tuple[HumanValidationRisk, ...],
    state: HumanValidatedPaperSessionState | None = None,
) -> tuple[HumanValidationRecommendation, ...]:
    """Generate human validated paper session recommendations."""

    recommendations: list[HumanValidationRecommendation] = []
    if risks:
        recommendations.append(HumanValidationRecommendation.HOLD_SUPERVISED_PAPER_SESSION_APPROVAL)
    mapping = {
        HumanValidationRisk.HUMAN_APPROVAL_MISSING: HumanValidationRecommendation.CAPTURE_EXPLICIT_HUMAN_APPROVAL,
        HumanValidationRisk.OPERATOR_CONFIRMATION_FAILURE: HumanValidationRecommendation.REPAIR_OPERATOR_CONFIRMATION_FLOW,
        HumanValidationRisk.SESSION_AUTHORIZATION_MISSING: HumanValidationRecommendation.AUTHORIZE_SESSION_SCOPE,
        HumanValidationRisk.AUDIT_TRAIL_INCOMPLETE: HumanValidationRecommendation.COMPLETE_AUDIT_TRAIL,
        HumanValidationRisk.DECISION_TRACEABILITY_LOSS: HumanValidationRecommendation.RESTORE_DECISION_TRACEABILITY,
        HumanValidationRisk.REVERSIBILITY_NOT_VERIFIED: HumanValidationRecommendation.VERIFY_REVERSIBILITY_PATH,
        HumanValidationRisk.HUMAN_OVERRIDE_UNAVAILABLE: HumanValidationRecommendation.ENABLE_HUMAN_OVERRIDE,
        HumanValidationRisk.SUPERVISION_GAP: HumanValidationRecommendation.CLOSE_SUPERVISION_GAP,
        HumanValidationRisk.PAPER_SESSION_DRIFT: HumanValidationRecommendation.LOCK_PAPER_SESSION_DETERMINISM,
        HumanValidationRisk.VALIDATION_BYPASS_RISK: HumanValidationRecommendation.BLOCK_VALIDATION_BYPASS,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(HumanValidationRecommendation.RUN_HUMAN_VALIDATION_READINESS_SUITE)
    if state == HumanValidatedPaperSessionState.READY_FOR_SUPERVISED_PAPER_SESSION:
        recommendations.append(HumanValidationRecommendation.APPROVE_SUPERVISED_PAPER_SESSION_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_human_validated_paper_session(
    data: HumanValidatedPaperSessionInput | Mapping[str, Any],
) -> HumanValidatedPaperSessionResult:
    """Evaluate whether AGIcore is ready for an offline supervised paper session."""

    data = _coerce_input(data)
    approval = verify_human_approval_gate(data)
    operator = verify_operator_confirmation_flow(data)
    authorization = verify_session_authorization(data)
    auditability = verify_auditability_requirements(data)
    reversibility = verify_reversibility_requirements(data)
    risks = detect_human_validation_risks(data, approval, operator, authorization, auditability, reversibility)
    score = compute_human_validation_score(data, risks, approval, operator, authorization, auditability, reversibility)
    state = _select_state(score.overall_score, risks, data.ready_for_supervised_paper_session)
    graph = _build_human_validation_graph(risks)
    recommendations = generate_human_validation_recommendations(risks, state)
    offline_only = not _has_upstream(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK")
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return HumanValidatedPaperSessionResult(
        state=state,
        human_validation_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        human_approval_review=approval,
        operator_confirmation_review=operator,
        session_authorization_review=authorization,
        auditability_review=auditability,
        reversibility_review=reversibility,
        human_validation_graph=graph,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_human_validated_paper_session_markdown(result: HumanValidatedPaperSessionResult) -> str:
    """Render an explainable human validated paper session report."""

    lines = [
        "# AGIcore Human Validated Paper Session",
        f"- State: {result.state.value}",
        f"- Score: {result.human_validation_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Human approval: {result.score_breakdown.human_approval_score}/100",
        f"- Operator confirmation: {result.score_breakdown.operator_confirmation_score}/100",
        f"- Session authorization: {result.score_breakdown.session_authorization_score}/100",
        f"- Auditability: {result.score_breakdown.auditability_score}/100",
        f"- Reversibility: {result.score_breakdown.reversibility_score}/100",
        f"- Supervision: {result.score_breakdown.supervision_score}/100",
        "",
        "# Human Validation Reviews",
    ]
    for section in (
        result.human_approval_review,
        result.operator_confirmation_review,
        result.session_authorization_review,
        result.auditability_review,
        result.reversibility_review,
    ):
        lines.append(
            f"- {section.name}: passed={section.passed}, score={section.score}/100, "
            f"risks={', '.join(risk.value for risk in section.risks) or 'none'}"
        )
        lines.extend(f"  - {item}" for item in section.evidence)
    lines.append("")
    lines.append("# Human Validation Graph")
    lines.append(f"- Nodes: {', '.join(result.human_validation_graph.nodes)}")
    lines.extend(
        f"- Edge: {source} -> {target} ({label})"
        for source, target, label in result.human_validation_graph.edges
    )
    lines.append(
        "- Blocked edges: "
        + (
            ", ".join(f"{source}->{target}" for source, target in result.human_validation_graph.blocked_edges)
            or "none"
        )
    )
    lines.append("")
    lines.append("# Human Validation Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Human Validation Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# Readiness Outlook")
    if result.state == HumanValidatedPaperSessionState.READY_FOR_SUPERVISED_PAPER_SESSION:
        lines.append("- Human validation is ready for a supervised paper session.")
    elif result.state == HumanValidatedPaperSessionState.HUMAN_VALIDATION_READY:
        lines.append("- Human validation is ready; supervised paper session remains gated.")
    elif result.state == HumanValidatedPaperSessionState.PARTIALLY_READY:
        lines.append("- Human validation is partially ready and remaining risks must be resolved.")
    else:
        lines.append("- Supervised paper session approval should remain blocked.")
    return "\n".join(lines)


__all__ = [
    "compute_human_validation_score",
    "detect_human_validation_risks",
    "evaluate_human_validated_paper_session",
    "generate_human_validation_recommendations",
    "render_human_validated_paper_session_markdown",
    "verify_auditability_requirements",
    "verify_human_approval_gate",
    "verify_operator_confirmation_flow",
    "verify_reversibility_requirements",
    "verify_session_authorization",
]
