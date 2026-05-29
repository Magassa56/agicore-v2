"""Offline supervised paper trial verification for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.supervised_paper_trial_models import (
    SupervisedPaperTrialInput,
    SupervisedPaperTrialRecommendation,
    SupervisedPaperTrialResult,
    SupervisedPaperTrialReviewSection,
    SupervisedPaperTrialRisk,
    SupervisedPaperTrialScore,
    SupervisedPaperTrialState,
    SupervisedPaperTrialTrace,
)


def _coerce_input(data: SupervisedPaperTrialInput | Mapping[str, Any]) -> SupervisedPaperTrialInput:
    if isinstance(data, SupervisedPaperTrialInput):
        return data
    return SupervisedPaperTrialInput(**dict(data))


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


def _upstream_items(data: SupervisedPaperTrialInput) -> tuple[Any, ...]:
    return (
        data.paper_dry_run,
        data.paper_trading_end_to_end,
        data.alpaca_paper_adapter,
        data.paper_broker_adapter,
        data.supervised_paper_session,
        data.human_validated_paper_session,
        data.controlled_paper_run,
        data.paper_execution_loop_readiness,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
    )


def _upstream_risks(data: SupervisedPaperTrialInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: SupervisedPaperTrialInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _upstream_score(data: SupervisedPaperTrialInput, *names: str) -> int | None:
    values: list[int] = []
    for item in _upstream_items(data):
        values.extend(_score(item, name) for name in names)
        breakdown = _get(item, "score_breakdown")
        values.extend(_score(breakdown, name) for name in names)
    values = [value for value in values if value is not None]
    return _average(values) if values else None


def verify_trial_scenario(data: SupervisedPaperTrialInput | Mapping[str, Any]) -> SupervisedPaperTrialReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.trial_scenario_score) if data.trial_scenario_score is not None else _average(
        (
            _bool_score(data.trial_scenario_defined),
            _bool_score(data.scenario_inputs_fixed),
            _bool_score(data.scenario_expected_outputs_defined),
            _bool_score(data.scenario_repeatable),
            _upstream_score(data, "dry_run_score", "end_to_end_score"),
        ),
        default=45,
    )
    risks: list[SupervisedPaperTrialRisk] = []
    if (
        data.trial_scenario_defined is not True
        or data.scenario_inputs_fixed is not True
        or data.scenario_expected_outputs_defined is not True
        or score < 85
    ):
        risks.append(SupervisedPaperTrialRisk.TRIAL_SCENARIO_MISSING)
    if data.scenario_repeatable is not True:
        risks.append(SupervisedPaperTrialRisk.TRIAL_NOT_REPEATABLE)
    evidence = (
        f"trial_scenario_score={score}/100",
        f"trial_scenario_defined={data.trial_scenario_defined}",
        f"scenario_inputs_fixed={data.scenario_inputs_fixed}",
        f"scenario_expected_outputs_defined={data.scenario_expected_outputs_defined}",
        f"scenario_repeatable={data.scenario_repeatable}",
    )
    return SupervisedPaperTrialReviewSection("trial_scenario_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_supervised_execution_flow(data: SupervisedPaperTrialInput | Mapping[str, Any]) -> SupervisedPaperTrialReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.supervised_execution_score) if data.supervised_execution_score is not None else _average(
        (
            _bool_score(data.human_supervisor_assigned),
            _bool_score(data.operator_confirmation_available),
            _bool_score(data.supervision_session_active),
            _bool_score(data.human_override_available),
            _bool_score(data.dry_run_completed),
            _bool_score(data.dry_run_output_reconciled),
            _upstream_score(data, "supervised_session_score", "human_validation_score", "dry_run_score"),
        ),
        default=45,
    )
    risks: list[SupervisedPaperTrialRisk] = []
    if (
        data.human_supervisor_assigned is not True
        or data.operator_confirmation_available is not True
        or data.supervision_session_active is not True
        or data.dry_run_completed is not True
        or score < 85
        or _has_upstream_risk(data, "SUPERVISION", "HUMAN_APPROVAL")
    ):
        risks.append(SupervisedPaperTrialRisk.SUPERVISION_FLOW_BROKEN)
    if data.human_override_available is not True or _has_upstream_risk(data, "HUMAN_OVERRIDE"):
        risks.append(SupervisedPaperTrialRisk.HUMAN_OVERRIDE_FAILURE)
    if data.dry_run_output_reconciled is not True or _has_upstream_risk(data, "DRY_RUN"):
        risks.append(SupervisedPaperTrialRisk.DRY_RUN_INCONSISTENCY)
    evidence = (
        f"supervised_execution_score={score}/100",
        f"human_supervisor_assigned={data.human_supervisor_assigned}",
        f"operator_confirmation_available={data.operator_confirmation_available}",
        f"supervision_session_active={data.supervision_session_active}",
        f"human_override_available={data.human_override_available}",
        f"dry_run_completed={data.dry_run_completed}",
        f"dry_run_output_reconciled={data.dry_run_output_reconciled}",
    )
    return SupervisedPaperTrialReviewSection("supervised_execution_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_trial_safety_gate(data: SupervisedPaperTrialInput | Mapping[str, Any]) -> SupervisedPaperTrialReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.trial_safety_gate_score) if data.trial_safety_gate_score is not None else _average(
        (
            _bool_score(data.safety_gate_available),
            _bool_score(data.safety_gate_passed),
            _bool_score(data.kill_switch_linked),
            _bool_score(data.safety_bypass_blocked),
            _upstream_score(data, "safety_gate_score", "kill_switch_score"),
        ),
        default=45,
    )
    risks: list[SupervisedPaperTrialRisk] = []
    if (
        data.safety_gate_available is not True
        or data.safety_gate_passed is not True
        or data.kill_switch_linked is not True
        or score < 85
        or _has_upstream_risk(data, "SAFETY", "KILL_SWITCH")
    ):
        risks.append(SupervisedPaperTrialRisk.SAFETY_GATE_FAILURE)
    if data.safety_bypass_blocked is not True:
        risks.append(SupervisedPaperTrialRisk.HUMAN_OVERRIDE_FAILURE)
    evidence = (
        f"trial_safety_gate_score={score}/100",
        f"safety_gate_available={data.safety_gate_available}",
        f"safety_gate_passed={data.safety_gate_passed}",
        f"kill_switch_linked={data.kill_switch_linked}",
        f"safety_bypass_blocked={data.safety_bypass_blocked}",
    )
    return SupervisedPaperTrialReviewSection("trial_safety_gate_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_trial_journal(data: SupervisedPaperTrialInput | Mapping[str, Any]) -> SupervisedPaperTrialReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.trial_journal_score) if data.trial_journal_score is not None else _average(
        (
            _bool_score(data.journal_entry_written),
            _bool_score(data.journal_captures_scenario),
            _bool_score(data.journal_captures_decisions),
            _bool_score(data.final_report_available),
            _upstream_score(data, "journal_flow_score", "journal_pipeline_score"),
        ),
        default=45,
    )
    risks: list[SupervisedPaperTrialRisk] = []
    if (
        data.journal_entry_written is not True
        or data.journal_captures_scenario is not True
        or data.journal_captures_decisions is not True
        or data.final_report_available is not True
        or score < 85
        or _has_upstream_risk(data, "JOURNAL", "AUDIT")
    ):
        risks.append(SupervisedPaperTrialRisk.JOURNAL_INCOMPLETE)
    evidence = (
        f"trial_journal_score={score}/100",
        f"journal_entry_written={data.journal_entry_written}",
        f"journal_captures_scenario={data.journal_captures_scenario}",
        f"journal_captures_decisions={data.journal_captures_decisions}",
        f"final_report_available={data.final_report_available}",
    )
    return SupervisedPaperTrialReviewSection("trial_journal_review", score, not risks and score >= 85, tuple(risks), evidence)


def verify_trial_observability(data: SupervisedPaperTrialInput | Mapping[str, Any]) -> SupervisedPaperTrialReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.trial_observability_score) if data.trial_observability_score is not None else _average(
        (
            _bool_score(data.observability_events_emitted),
            _bool_score(data.metrics_recorded),
            _bool_score(data.traces_recorded),
            _bool_score(data.alerts_visible),
            _bool_score(data.paper_state_reconciled),
            _upstream_score(data, "observability_flow_score", "observability_score"),
        ),
        default=45,
    )
    risks: list[SupervisedPaperTrialRisk] = []
    if (
        data.observability_events_emitted is not True
        or data.metrics_recorded is not True
        or data.traces_recorded is not True
        or data.alerts_visible is not True
        or score < 85
        or _has_upstream_risk(data, "OBSERVABILITY")
    ):
        risks.append(SupervisedPaperTrialRisk.OBSERVABILITY_GAP)
    if data.paper_state_reconciled is not True or _has_upstream_risk(data, "DRIFT"):
        risks.append(SupervisedPaperTrialRisk.PAPER_STATE_DRIFT)
    evidence = (
        f"trial_observability_score={score}/100",
        f"observability_events_emitted={data.observability_events_emitted}",
        f"metrics_recorded={data.metrics_recorded}",
        f"traces_recorded={data.traces_recorded}",
        f"alerts_visible={data.alerts_visible}",
        f"paper_state_reconciled={data.paper_state_reconciled}",
    )
    return SupervisedPaperTrialReviewSection("trial_observability_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_trial_rollback_path(data: SupervisedPaperTrialInput | Mapping[str, Any]) -> SupervisedPaperTrialReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.trial_rollback_score) if data.trial_rollback_score is not None else _average(
        (
            _bool_score(data.rollback_path_available),
            _bool_score(data.recovery_point_verified),
            _bool_score(data.post_rollback_state_safe),
            _bool_score(data.rollback_audit_recorded),
            _upstream_score(data, "rollback_score"),
        ),
        default=45,
    )
    risks: list[SupervisedPaperTrialRisk] = []
    if (
        data.rollback_path_available is not True
        or data.recovery_point_verified is not True
        or data.post_rollback_state_safe is not True
        or data.rollback_audit_recorded is not True
        or score < 85
        or _has_upstream_risk(data, "ROLLBACK")
    ):
        risks.append(SupervisedPaperTrialRisk.ROLLBACK_PATH_UNVERIFIED)
    evidence = (
        f"trial_rollback_score={score}/100",
        f"rollback_path_available={data.rollback_path_available}",
        f"recovery_point_verified={data.recovery_point_verified}",
        f"post_rollback_state_safe={data.post_rollback_state_safe}",
        f"rollback_audit_recorded={data.rollback_audit_recorded}",
    )
    return SupervisedPaperTrialReviewSection("trial_rollback_review", score, not risks and score >= 85, tuple(risks), evidence)


def detect_trial_risks(
    data: SupervisedPaperTrialInput | Mapping[str, Any],
    trial_scenario_review: SupervisedPaperTrialReviewSection | None = None,
    supervised_execution_review: SupervisedPaperTrialReviewSection | None = None,
    trial_safety_gate_review: SupervisedPaperTrialReviewSection | None = None,
    trial_journal_review: SupervisedPaperTrialReviewSection | None = None,
    trial_observability_review: SupervisedPaperTrialReviewSection | None = None,
    trial_rollback_review: SupervisedPaperTrialReviewSection | None = None,
) -> tuple[SupervisedPaperTrialRisk, ...]:
    data = _coerce_input(data)
    sections = (
        trial_scenario_review or verify_trial_scenario(data),
        supervised_execution_review or verify_supervised_execution_flow(data),
        trial_safety_gate_review or verify_trial_safety_gate(data),
        trial_journal_review or verify_trial_journal(data),
        trial_observability_review or verify_trial_observability(data),
        trial_rollback_review or verify_trial_rollback_path(data),
    )
    risks: list[SupervisedPaperTrialRisk] = []
    for section in sections:
        risks.extend(section.risks)
    if data.trial_repeatable is not True:
        risks.append(SupervisedPaperTrialRisk.TRIAL_NOT_REPEATABLE)
    if data.offline_mode_enforced is not True or _has_upstream_risk(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK"):
        risks.append(SupervisedPaperTrialRisk.DRY_RUN_INCONSISTENCY)
    return _dedupe(risks)


def compute_trial_score(
    data: SupervisedPaperTrialInput | Mapping[str, Any],
    risks: tuple[SupervisedPaperTrialRisk, ...] = (),
    trial_scenario_review: SupervisedPaperTrialReviewSection | None = None,
    supervised_execution_review: SupervisedPaperTrialReviewSection | None = None,
    trial_safety_gate_review: SupervisedPaperTrialReviewSection | None = None,
    trial_journal_review: SupervisedPaperTrialReviewSection | None = None,
    trial_observability_review: SupervisedPaperTrialReviewSection | None = None,
    trial_rollback_review: SupervisedPaperTrialReviewSection | None = None,
) -> SupervisedPaperTrialScore:
    data = _coerce_input(data)
    scenario = trial_scenario_review or verify_trial_scenario(data)
    execution = supervised_execution_review or verify_supervised_execution_flow(data)
    safety = trial_safety_gate_review or verify_trial_safety_gate(data)
    journal = trial_journal_review or verify_trial_journal(data)
    observability = trial_observability_review or verify_trial_observability(data)
    rollback = trial_rollback_review or verify_trial_rollback_path(data)
    weighted = _weighted_average(
        (
            (scenario.score, 1.05),
            (execution.score, 1.25),
            (safety.score, 1.35),
            (journal.score, 1.0),
            (observability.score, 1.1),
            (rollback.score, 1.15),
        )
    )
    penalty = min(72, len(set(risks)) * 6)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        SupervisedPaperTrialRisk.TRIAL_SCENARIO_MISSING: 50,
        SupervisedPaperTrialRisk.SUPERVISION_FLOW_BROKEN: 45,
        SupervisedPaperTrialRisk.SAFETY_GATE_FAILURE: 40,
        SupervisedPaperTrialRisk.DRY_RUN_INCONSISTENCY: 45,
        SupervisedPaperTrialRisk.HUMAN_OVERRIDE_FAILURE: 45,
    }
    for risk, cap in critical_caps.items():
        if risk in risks:
            overall = min(overall, cap)
    return SupervisedPaperTrialScore(
        overall_score=overall,
        trial_scenario_score=scenario.score,
        supervised_execution_score=execution.score,
        trial_safety_gate_score=safety.score,
        trial_journal_score=journal.score,
        trial_observability_score=observability.score,
        trial_rollback_score=rollback.score,
    )


def _build_trace(risks: tuple[SupervisedPaperTrialRisk, ...]) -> SupervisedPaperTrialTrace:
    steps = ("scenario", "supervision", "safety_gate", "journal", "observability", "rollback", "final_report")
    blocked: list[str] = []
    if SupervisedPaperTrialRisk.TRIAL_SCENARIO_MISSING in risks:
        blocked.append("scenario")
    if SupervisedPaperTrialRisk.SUPERVISION_FLOW_BROKEN in risks or SupervisedPaperTrialRisk.HUMAN_OVERRIDE_FAILURE in risks:
        blocked.append("supervision")
    if SupervisedPaperTrialRisk.SAFETY_GATE_FAILURE in risks:
        blocked.append("safety_gate")
    if SupervisedPaperTrialRisk.JOURNAL_INCOMPLETE in risks:
        blocked.append("journal")
    if SupervisedPaperTrialRisk.OBSERVABILITY_GAP in risks or SupervisedPaperTrialRisk.PAPER_STATE_DRIFT in risks:
        blocked.append("observability")
    if SupervisedPaperTrialRisk.ROLLBACK_PATH_UNVERIFIED in risks:
        blocked.append("rollback")
    if SupervisedPaperTrialRisk.DRY_RUN_INCONSISTENCY in risks or SupervisedPaperTrialRisk.TRIAL_NOT_REPEATABLE in risks:
        blocked.append("final_report")
    completed = tuple(step for step in steps if step not in blocked)
    return SupervisedPaperTrialTrace(steps, completed, _dedupe(blocked))


def _select_state(score: int, risks: tuple[SupervisedPaperTrialRisk, ...], trial_executed: bool | None, ready_for_sandbox: bool | None) -> SupervisedPaperTrialState:
    hard = {
        SupervisedPaperTrialRisk.TRIAL_SCENARIO_MISSING,
        SupervisedPaperTrialRisk.SUPERVISION_FLOW_BROKEN,
        SupervisedPaperTrialRisk.SAFETY_GATE_FAILURE,
        SupervisedPaperTrialRisk.DRY_RUN_INCONSISTENCY,
        SupervisedPaperTrialRisk.HUMAN_OVERRIDE_FAILURE,
    }
    count = len(set(risks))
    if hard.intersection(risks) or score < 45 or count >= 6:
        return SupervisedPaperTrialState.NOT_READY
    if count >= 3 or score < 72:
        return SupervisedPaperTrialState.REVIEW_REQUIRED
    if count:
        return SupervisedPaperTrialState.PARTIALLY_READY
    if trial_executed is True and ready_for_sandbox is True and score >= 94:
        return SupervisedPaperTrialState.READY_FOR_BROKER_PAPER_SANDBOX
    if trial_executed is True and score >= 90:
        return SupervisedPaperTrialState.TRIAL_COMPLETED
    if score >= 85:
        return SupervisedPaperTrialState.TRIAL_READY
    return SupervisedPaperTrialState.PARTIALLY_READY


def generate_trial_recommendations(
    risks: tuple[SupervisedPaperTrialRisk, ...],
    state: SupervisedPaperTrialState | None = None,
) -> tuple[SupervisedPaperTrialRecommendation, ...]:
    recommendations: list[SupervisedPaperTrialRecommendation] = []
    if risks:
        recommendations.append(SupervisedPaperTrialRecommendation.HOLD_BROKER_PAPER_SANDBOX_APPROVAL)
    mapping = {
        SupervisedPaperTrialRisk.TRIAL_SCENARIO_MISSING: SupervisedPaperTrialRecommendation.DEFINE_TRIAL_SCENARIO,
        SupervisedPaperTrialRisk.SUPERVISION_FLOW_BROKEN: SupervisedPaperTrialRecommendation.REPAIR_SUPERVISION_FLOW,
        SupervisedPaperTrialRisk.SAFETY_GATE_FAILURE: SupervisedPaperTrialRecommendation.VERIFY_TRIAL_SAFETY_GATE,
        SupervisedPaperTrialRisk.JOURNAL_INCOMPLETE: SupervisedPaperTrialRecommendation.COMPLETE_TRIAL_JOURNAL,
        SupervisedPaperTrialRisk.OBSERVABILITY_GAP: SupervisedPaperTrialRecommendation.RESTORE_TRIAL_OBSERVABILITY,
        SupervisedPaperTrialRisk.ROLLBACK_PATH_UNVERIFIED: SupervisedPaperTrialRecommendation.VERIFY_ROLLBACK_PATH,
        SupervisedPaperTrialRisk.DRY_RUN_INCONSISTENCY: SupervisedPaperTrialRecommendation.RECONCILE_DRY_RUN_OUTPUT,
        SupervisedPaperTrialRisk.PAPER_STATE_DRIFT: SupervisedPaperTrialRecommendation.RECONCILE_PAPER_STATE,
        SupervisedPaperTrialRisk.HUMAN_OVERRIDE_FAILURE: SupervisedPaperTrialRecommendation.ENABLE_HUMAN_OVERRIDE,
        SupervisedPaperTrialRisk.TRIAL_NOT_REPEATABLE: SupervisedPaperTrialRecommendation.STABILIZE_TRIAL_REPEATABILITY,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(SupervisedPaperTrialRecommendation.RUN_SUPERVISED_PAPER_TRIAL_SUITE)
    if state == SupervisedPaperTrialState.READY_FOR_BROKER_PAPER_SANDBOX:
        recommendations.append(SupervisedPaperTrialRecommendation.APPROVE_BROKER_PAPER_SANDBOX_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_supervised_paper_trial(data: SupervisedPaperTrialInput | Mapping[str, Any]) -> SupervisedPaperTrialResult:
    data = _coerce_input(data)
    scenario = verify_trial_scenario(data)
    execution = verify_supervised_execution_flow(data)
    safety = verify_trial_safety_gate(data)
    journal = verify_trial_journal(data)
    observability = verify_trial_observability(data)
    rollback = verify_trial_rollback_path(data)
    risks = detect_trial_risks(data, scenario, execution, safety, journal, observability, rollback)
    score = compute_trial_score(data, risks, scenario, execution, safety, journal, observability, rollback)
    state = _select_state(score.overall_score, risks, data.trial_executed, data.ready_for_broker_paper_sandbox)
    trace = _build_trace(risks)
    recommendations = generate_trial_recommendations(risks, state)
    offline_only = data.offline_mode_enforced is True and not _has_upstream_risk(
        data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK"
    )
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return SupervisedPaperTrialResult(
        state=state,
        trial_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        trial_scenario_review=scenario,
        supervised_execution_review=execution,
        trial_safety_gate_review=safety,
        trial_journal_review=journal,
        trial_observability_review=observability,
        trial_rollback_review=rollback,
        trial_trace=trace,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_supervised_paper_trial_markdown(result: SupervisedPaperTrialResult) -> str:
    lines = [
        "# AGIcore Supervised Paper Trial",
        f"- State: {result.state.value}",
        f"- Score: {result.trial_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Scenario: {result.score_breakdown.trial_scenario_score}/100",
        f"- Supervised execution: {result.score_breakdown.supervised_execution_score}/100",
        f"- Safety gate: {result.score_breakdown.trial_safety_gate_score}/100",
        f"- Journal: {result.score_breakdown.trial_journal_score}/100",
        f"- Observability: {result.score_breakdown.trial_observability_score}/100",
        f"- Rollback: {result.score_breakdown.trial_rollback_score}/100",
        "",
        "# Trial Reviews",
    ]
    sections = (
        result.trial_scenario_review,
        result.supervised_execution_review,
        result.trial_safety_gate_review,
        result.trial_journal_review,
        result.trial_observability_review,
        result.trial_rollback_review,
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
            "# Trial Trace",
            f"- Steps: {', '.join(result.trial_trace.steps)}",
            f"- Completed: {', '.join(result.trial_trace.completed_steps) or 'none'}",
            f"- Blocked: {', '.join(result.trial_trace.blocked_steps) or 'none'}",
            "",
            "# Trial Risks",
        )
    )
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Trial Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_trial_score",
    "detect_trial_risks",
    "evaluate_supervised_paper_trial",
    "generate_trial_recommendations",
    "render_supervised_paper_trial_markdown",
    "verify_supervised_execution_flow",
    "verify_trial_journal",
    "verify_trial_observability",
    "verify_trial_rollback_path",
    "verify_trial_safety_gate",
    "verify_trial_scenario",
]
