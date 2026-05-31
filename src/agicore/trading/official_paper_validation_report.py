"""Official offline validation report for the AGIcore Paper Trading Runtime."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.official_paper_validation_report_models import (
    OfficialPaperValidationEvidence,
    OfficialPaperValidationReportDecision,
    OfficialPaperValidationReportInput,
    OfficialPaperValidationReportRecommendation,
    OfficialPaperValidationReportResult,
    OfficialPaperValidationReportRisk,
    OfficialPaperValidationReportScore,
    OfficialPaperValidationReportState,
)


def _coerce_input(data: OfficialPaperValidationReportInput | Mapping[str, Any]) -> OfficialPaperValidationReportInput:
    if isinstance(data, OfficialPaperValidationReportInput):
        return data
    return OfficialPaperValidationReportInput(**dict(data))


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


def _bool_score(value: bool | None, unknown: int = 45) -> int:
    if value is True:
        return 100
    if value is False:
        return 0
    return unknown


def _average(values: Iterable[int | float | None], default: int = 0) -> int:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return default
    return _clamp(sum(usable) / len(usable))


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    result: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def _upstream_items(data: OfficialPaperValidationReportInput) -> tuple[Any, ...]:
    return (
        data.paper_runtime_validation,
        data.paper_runtime_release_candidate,
        data.paper_runtime_stabilization_review,
        data.extended_paper_runtime_test,
        data.paper_runtime_test_run,
        data.paper_trading_runtime,
        data.paper_runtime_integration_review,
        data.paper_trading_runtime_design,
        data.paper_runtime_decision_review,
        data.full_paper_session,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.human_validated_paper_session,
        data.supervised_paper_session,
    )


def _upstream_risks(data: OfficialPaperValidationReportInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: OfficialPaperValidationReportInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _evidence(
    name: str,
    score: int,
    risk: OfficialPaperValidationReportRisk,
    missing: bool,
    details: tuple[str, ...] = (),
) -> OfficialPaperValidationEvidence:
    risks = (risk,) if missing or score < 85 else ()
    return OfficialPaperValidationEvidence(name, _clamp(score), not risks and score >= 85, risks, details)


def collect_runtime_creation_evidence(data: OfficialPaperValidationReportInput | Mapping[str, Any]) -> OfficialPaperValidationEvidence:
    data = _coerce_input(data)
    runtime = data.paper_trading_runtime
    missing = data.runtime_creation_evidence_ready is not True or not _state_contains(runtime, "COMPLETED", "READY", "RUNNING") or _has_upstream_risk(data, "RUNTIME_INITIALIZATION", "RUNTIME_CREATION")
    score = data.runtime_creation_evidence_score if data.runtime_creation_evidence_score is not None else _bool_score(data.runtime_creation_evidence_ready)
    return _evidence("runtime_creation_evidence", score, OfficialPaperValidationReportRisk.RUNTIME_CREATION_EVIDENCE_MISSING, missing, (_value(_get(runtime, "state")),))


def collect_integration_review_evidence(data: OfficialPaperValidationReportInput | Mapping[str, Any]) -> OfficialPaperValidationEvidence:
    data = _coerce_input(data)
    integration = data.paper_runtime_integration_review
    missing = data.integration_review_evidence_ready is not True or not _state_contains(integration, "READY_FOR_PAPER_RUNTIME_TEST_RUN", "INTEGRATION_READY") or _has_upstream_risk(data, "INTEGRATION")
    score = data.integration_review_evidence_score if data.integration_review_evidence_score is not None else _bool_score(data.integration_review_evidence_ready)
    return _evidence("integration_review_evidence", score, OfficialPaperValidationReportRisk.INTEGRATION_EVIDENCE_MISSING, missing, (_value(_get(integration, "state")),))


def collect_test_run_evidence(data: OfficialPaperValidationReportInput | Mapping[str, Any]) -> OfficialPaperValidationEvidence:
    data = _coerce_input(data)
    test_run = data.paper_runtime_test_run
    missing = data.test_run_evidence_ready is not True or not _state_contains(test_run, "READY_FOR_EXTENDED_PAPER_RUNTIME_TEST", "TEST_RUN_COMPLETED") or _has_upstream_risk(data, "TEST_RUN")
    upstream_score = int(_get(test_run, "test_run_score", 100) or 100)
    score = data.test_run_evidence_score if data.test_run_evidence_score is not None else _average((_bool_score(data.test_run_evidence_ready), upstream_score))
    return _evidence("test_run_evidence", score, OfficialPaperValidationReportRisk.TEST_RUN_EVIDENCE_MISSING, missing)


def collect_extended_test_evidence(data: OfficialPaperValidationReportInput | Mapping[str, Any]) -> OfficialPaperValidationEvidence:
    data = _coerce_input(data)
    extended = data.extended_paper_runtime_test
    missing = data.extended_test_evidence_ready is not True or not _state_contains(extended, "READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW", "EXTENDED_TEST_COMPLETED") or _has_upstream_risk(data, "EXTENDED_TEST", "MULTI_SCENARIO")
    upstream_score = int(_get(extended, "extended_runtime_score", 100) or 100)
    score = data.extended_test_evidence_score if data.extended_test_evidence_score is not None else _average((_bool_score(data.extended_test_evidence_ready), upstream_score))
    return _evidence("extended_test_evidence", score, OfficialPaperValidationReportRisk.EXTENDED_TEST_EVIDENCE_MISSING, missing)


def collect_stabilization_evidence(data: OfficialPaperValidationReportInput | Mapping[str, Any]) -> OfficialPaperValidationEvidence:
    data = _coerce_input(data)
    stabilization = data.paper_runtime_stabilization_review
    missing = data.stabilization_evidence_ready is not True or not _state_contains(stabilization, "READY_FOR_PAPER_RUNTIME_RELEASE_CANDIDATE", "APPROVE_RELEASE_CANDIDATE_PREPARATION") or _has_upstream_risk(data, "STABILIZATION", "RUNTIME_STABILITY", "STATE_DRIFT")
    upstream_score = int(_get(stabilization, "stabilization_score", 100) or 100)
    score = data.stabilization_evidence_score if data.stabilization_evidence_score is not None else _average((_bool_score(data.stabilization_evidence_ready), upstream_score))
    return _evidence("stabilization_evidence", score, OfficialPaperValidationReportRisk.STABILIZATION_EVIDENCE_MISSING, missing)


def collect_release_candidate_evidence(data: OfficialPaperValidationReportInput | Mapping[str, Any]) -> OfficialPaperValidationEvidence:
    data = _coerce_input(data)
    rc = data.paper_runtime_release_candidate
    missing = data.release_candidate_evidence_ready is not True or not _state_contains(rc, "READY_FOR_PAPER_RUNTIME_VALIDATION", "APPROVE_PAPER_RUNTIME_RELEASE_CANDIDATE") or _has_upstream_risk(data, "RELEASE_CANDIDATE", "PREMATURE_RC")
    upstream_score = int(_get(rc, "release_candidate_score", 100) or 100)
    score = data.release_candidate_evidence_score if data.release_candidate_evidence_score is not None else _average((_bool_score(data.release_candidate_evidence_ready), upstream_score))
    return _evidence("release_candidate_evidence", score, OfficialPaperValidationReportRisk.RELEASE_CANDIDATE_EVIDENCE_MISSING, missing)


def collect_runtime_validation_evidence(data: OfficialPaperValidationReportInput | Mapping[str, Any]) -> OfficialPaperValidationEvidence:
    data = _coerce_input(data)
    validation = data.paper_runtime_validation
    missing = data.runtime_validation_evidence_ready is not True or not _state_contains(validation, "READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT", "APPROVE_PAPER_RUNTIME_VALIDATION") or _has_upstream_risk(data, "VALIDATION")
    upstream_score = int(_get(validation, "validation_score", 100) or 100)
    score = data.runtime_validation_evidence_score if data.runtime_validation_evidence_score is not None else _average((_bool_score(data.runtime_validation_evidence_ready), upstream_score))
    return _evidence("runtime_validation_evidence", score, OfficialPaperValidationReportRisk.VALIDATION_EVIDENCE_MISSING, missing, (_value(_get(validation, "state")),))


def collect_safety_evidence(data: OfficialPaperValidationReportInput | Mapping[str, Any]) -> OfficialPaperValidationEvidence:
    data = _coerce_input(data)
    missing = data.safety_evidence_ready is not True or _has_upstream_risk(data, "SAFETY", "BYPASS", "EXECUTION_LEAK")
    score = data.safety_evidence_score if data.safety_evidence_score is not None else _bool_score(data.safety_evidence_ready)
    return _evidence("safety_evidence", score, OfficialPaperValidationReportRisk.SAFETY_EVIDENCE_MISSING, missing)


def collect_observability_evidence(data: OfficialPaperValidationReportInput | Mapping[str, Any]) -> OfficialPaperValidationEvidence:
    data = _coerce_input(data)
    missing = data.observability_evidence_ready is not True or _has_upstream_risk(data, "OBSERVABILITY")
    score = data.observability_evidence_score if data.observability_evidence_score is not None else _bool_score(data.observability_evidence_ready)
    return _evidence("observability_evidence", score, OfficialPaperValidationReportRisk.OBSERVABILITY_EVIDENCE_MISSING, missing)


def collect_rollback_evidence(data: OfficialPaperValidationReportInput | Mapping[str, Any]) -> OfficialPaperValidationEvidence:
    data = _coerce_input(data)
    missing = data.rollback_evidence_ready is not True or _has_upstream_risk(data, "ROLLBACK")
    score = data.rollback_evidence_score if data.rollback_evidence_score is not None else _bool_score(data.rollback_evidence_ready)
    return _evidence("rollback_evidence", score, OfficialPaperValidationReportRisk.ROLLBACK_EVIDENCE_MISSING, missing)


def collect_kill_switch_evidence(data: OfficialPaperValidationReportInput | Mapping[str, Any]) -> OfficialPaperValidationEvidence:
    data = _coerce_input(data)
    missing = data.kill_switch_evidence_ready is not True or _has_upstream_risk(data, "KILL_SWITCH")
    score = data.kill_switch_evidence_score if data.kill_switch_evidence_score is not None else _bool_score(data.kill_switch_evidence_ready)
    return _evidence("kill_switch_evidence", score, OfficialPaperValidationReportRisk.KILL_SWITCH_EVIDENCE_MISSING, missing)


def collect_human_supervision_evidence(data: OfficialPaperValidationReportInput | Mapping[str, Any]) -> OfficialPaperValidationEvidence:
    data = _coerce_input(data)
    missing = data.human_supervision_evidence_ready is not True or _has_upstream_risk(data, "HUMAN", "SUPERVISION")
    score = data.human_supervision_evidence_score if data.human_supervision_evidence_score is not None else _bool_score(data.human_supervision_evidence_ready)
    return _evidence("human_supervision_evidence", score, OfficialPaperValidationReportRisk.HUMAN_SUPERVISION_EVIDENCE_MISSING, missing)


def collect_operational_boundary_evidence(data: OfficialPaperValidationReportInput | Mapping[str, Any]) -> OfficialPaperValidationEvidence:
    data = _coerce_input(data)
    missing = data.operational_boundary_evidence_ready is not True or not _offline_boundary(data) or _has_upstream_risk(data, "LIVE_EXECUTION", "NETWORK_LEAK", "BROKER", "EXTERNAL_DEPENDENCY")
    score = data.operational_boundary_evidence_score if data.operational_boundary_evidence_score is not None else _bool_score(data.operational_boundary_evidence_ready)
    return _evidence("operational_boundary_evidence", score, OfficialPaperValidationReportRisk.OPERATIONAL_BOUNDARY_EVIDENCE_MISSING, missing)


def _offline_boundary(data: OfficialPaperValidationReportInput) -> bool:
    return (
        data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.no_real_broker is True
        and data.no_api_key_read is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
        and data.no_real_order is True
        and _get(data.paper_runtime_validation, "offline_only", True) is True
        and not _has_upstream_risk(data, "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "BROKER", "EXTERNAL_DEPENDENCY")
    )


def detect_official_report_risks(
    data: OfficialPaperValidationReportInput | Mapping[str, Any],
    *evidences: OfficialPaperValidationEvidence,
) -> tuple[OfficialPaperValidationReportRisk, ...]:
    data = _coerce_input(data)
    if not evidences:
        evidences = _collect_all(data)
    risks: list[OfficialPaperValidationReportRisk] = []
    for evidence in evidences:
        risks.extend(evidence.risks)
    if data.supervised_trial_requested is not True or not _offline_boundary(data):
        risks.append(OfficialPaperValidationReportRisk.PREMATURE_SUPERVISED_TRIAL)
    return _dedupe(risks)


def compute_official_report_score(
    data: OfficialPaperValidationReportInput | Mapping[str, Any],
    risks: tuple[OfficialPaperValidationReportRisk, ...] = (),
    *evidences: OfficialPaperValidationEvidence,
) -> OfficialPaperValidationReportScore:
    data = _coerce_input(data)
    if not evidences:
        evidences = _collect_all(data)
    scores = tuple(evidence.score for evidence in evidences)
    overall = _clamp(_average(scores) - min(80, len(set(risks)) * 5))
    for risk, cap in {
        OfficialPaperValidationReportRisk.RUNTIME_CREATION_EVIDENCE_MISSING: 55,
        OfficialPaperValidationReportRisk.INTEGRATION_EVIDENCE_MISSING: 60,
        OfficialPaperValidationReportRisk.TEST_RUN_EVIDENCE_MISSING: 60,
        OfficialPaperValidationReportRisk.EXTENDED_TEST_EVIDENCE_MISSING: 60,
        OfficialPaperValidationReportRisk.STABILIZATION_EVIDENCE_MISSING: 55,
        OfficialPaperValidationReportRisk.RELEASE_CANDIDATE_EVIDENCE_MISSING: 50,
        OfficialPaperValidationReportRisk.VALIDATION_EVIDENCE_MISSING: 45,
        OfficialPaperValidationReportRisk.SAFETY_EVIDENCE_MISSING: 50,
        OfficialPaperValidationReportRisk.ROLLBACK_EVIDENCE_MISSING: 55,
        OfficialPaperValidationReportRisk.KILL_SWITCH_EVIDENCE_MISSING: 50,
        OfficialPaperValidationReportRisk.OPERATIONAL_BOUNDARY_EVIDENCE_MISSING: 40,
        OfficialPaperValidationReportRisk.PREMATURE_SUPERVISED_TRIAL: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return OfficialPaperValidationReportScore(overall, *scores)


def _select_decision(risks: tuple[OfficialPaperValidationReportRisk, ...], score: int) -> OfficialPaperValidationReportDecision:
    if OfficialPaperValidationReportRisk.PREMATURE_SUPERVISED_TRIAL in risks or score < 45 and OfficialPaperValidationReportRisk.OPERATIONAL_BOUNDARY_EVIDENCE_MISSING not in risks:
        return OfficialPaperValidationReportDecision.BLOCK_SUPERVISED_TRIAL
    if OfficialPaperValidationReportRisk.OPERATIONAL_BOUNDARY_EVIDENCE_MISSING in risks:
        return OfficialPaperValidationReportDecision.REQUIRE_BOUNDARY_FIXES
    if {
        OfficialPaperValidationReportRisk.VALIDATION_EVIDENCE_MISSING,
        OfficialPaperValidationReportRisk.RELEASE_CANDIDATE_EVIDENCE_MISSING,
        OfficialPaperValidationReportRisk.RUNTIME_CREATION_EVIDENCE_MISSING,
    } & set(risks):
        return OfficialPaperValidationReportDecision.REQUIRE_REPORT_COMPLETION
    if risks:
        return OfficialPaperValidationReportDecision.REQUIRE_EVIDENCE_FIXES
    return OfficialPaperValidationReportDecision.APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL


def _select_state(decision: OfficialPaperValidationReportDecision, score: int) -> OfficialPaperValidationReportState:
    if decision == OfficialPaperValidationReportDecision.BLOCK_SUPERVISED_TRIAL:
        return OfficialPaperValidationReportState.REPORT_NOT_READY
    if decision in {
        OfficialPaperValidationReportDecision.REQUIRE_REPORT_COMPLETION,
        OfficialPaperValidationReportDecision.REQUIRE_EVIDENCE_FIXES,
        OfficialPaperValidationReportDecision.REQUIRE_BOUNDARY_FIXES,
    }:
        return OfficialPaperValidationReportState.REPORT_REVIEW_REQUIRED if score < 82 else OfficialPaperValidationReportState.REPORT_PARTIALLY_READY
    if score >= 95:
        return OfficialPaperValidationReportState.READY_FOR_SUPERVISED_PAPER_RUNTIME_TRIAL
    return OfficialPaperValidationReportState.REPORT_READY


def generate_official_report_recommendations(
    risks: tuple[OfficialPaperValidationReportRisk, ...],
    decision: OfficialPaperValidationReportDecision | None = None,
) -> tuple[OfficialPaperValidationReportRecommendation, ...]:
    recommendations: list[OfficialPaperValidationReportRecommendation] = []
    if risks:
        recommendations.append(OfficialPaperValidationReportRecommendation.HOLD_SUPERVISED_TRIAL)
    mapping = {
        OfficialPaperValidationReportRisk.RUNTIME_CREATION_EVIDENCE_MISSING: OfficialPaperValidationReportRecommendation.COMPLETE_RUNTIME_CREATION_EVIDENCE,
        OfficialPaperValidationReportRisk.INTEGRATION_EVIDENCE_MISSING: OfficialPaperValidationReportRecommendation.COMPLETE_INTEGRATION_EVIDENCE,
        OfficialPaperValidationReportRisk.TEST_RUN_EVIDENCE_MISSING: OfficialPaperValidationReportRecommendation.COMPLETE_TEST_RUN_EVIDENCE,
        OfficialPaperValidationReportRisk.EXTENDED_TEST_EVIDENCE_MISSING: OfficialPaperValidationReportRecommendation.COMPLETE_EXTENDED_TEST_EVIDENCE,
        OfficialPaperValidationReportRisk.STABILIZATION_EVIDENCE_MISSING: OfficialPaperValidationReportRecommendation.COMPLETE_STABILIZATION_EVIDENCE,
        OfficialPaperValidationReportRisk.RELEASE_CANDIDATE_EVIDENCE_MISSING: OfficialPaperValidationReportRecommendation.COMPLETE_RELEASE_CANDIDATE_EVIDENCE,
        OfficialPaperValidationReportRisk.VALIDATION_EVIDENCE_MISSING: OfficialPaperValidationReportRecommendation.COMPLETE_VALIDATION_EVIDENCE,
        OfficialPaperValidationReportRisk.SAFETY_EVIDENCE_MISSING: OfficialPaperValidationReportRecommendation.COMPLETE_SAFETY_EVIDENCE,
        OfficialPaperValidationReportRisk.OBSERVABILITY_EVIDENCE_MISSING: OfficialPaperValidationReportRecommendation.COMPLETE_OBSERVABILITY_EVIDENCE,
        OfficialPaperValidationReportRisk.ROLLBACK_EVIDENCE_MISSING: OfficialPaperValidationReportRecommendation.COMPLETE_ROLLBACK_EVIDENCE,
        OfficialPaperValidationReportRisk.KILL_SWITCH_EVIDENCE_MISSING: OfficialPaperValidationReportRecommendation.COMPLETE_KILL_SWITCH_EVIDENCE,
        OfficialPaperValidationReportRisk.HUMAN_SUPERVISION_EVIDENCE_MISSING: OfficialPaperValidationReportRecommendation.COMPLETE_HUMAN_SUPERVISION_EVIDENCE,
        OfficialPaperValidationReportRisk.OPERATIONAL_BOUNDARY_EVIDENCE_MISSING: OfficialPaperValidationReportRecommendation.REINFORCE_OPERATIONAL_BOUNDARIES,
        OfficialPaperValidationReportRisk.PREMATURE_SUPERVISED_TRIAL: OfficialPaperValidationReportRecommendation.DELAY_SUPERVISED_TRIAL,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(OfficialPaperValidationReportRecommendation.RUN_OFFICIAL_REPORT_REVIEW_SUITE)
    if decision == OfficialPaperValidationReportDecision.APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL:
        recommendations.append(OfficialPaperValidationReportRecommendation.APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL)
    return _dedupe(recommendations)


def _collect_all(data: OfficialPaperValidationReportInput) -> tuple[OfficialPaperValidationEvidence, ...]:
    return (
        collect_runtime_creation_evidence(data),
        collect_integration_review_evidence(data),
        collect_test_run_evidence(data),
        collect_extended_test_evidence(data),
        collect_stabilization_evidence(data),
        collect_release_candidate_evidence(data),
        collect_runtime_validation_evidence(data),
        collect_safety_evidence(data),
        collect_observability_evidence(data),
        collect_rollback_evidence(data),
        collect_kill_switch_evidence(data),
        collect_human_supervision_evidence(data),
        collect_operational_boundary_evidence(data),
    )


def generate_official_paper_validation_report(data: OfficialPaperValidationReportInput | Mapping[str, Any]) -> OfficialPaperValidationReportResult:
    data = _coerce_input(data)
    evidences = _collect_all(data)
    risks = detect_official_report_risks(data, *evidences)
    score = compute_official_report_score(data, risks, *evidences)
    decision = _select_decision(risks, score.overall_score)
    state = _select_state(decision, score.overall_score)
    recommendations = generate_official_report_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return OfficialPaperValidationReportResult(state, decision, score.overall_score, score, risks, *evidences, recommendations, offline_only, summary)


def render_official_paper_validation_report_markdown(result: OfficialPaperValidationReportResult) -> str:
    lines = [
        "# AGIcore Official Paper Validation Report",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.report_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Consolidated Evidence",
    ]
    evidences = (
        result.runtime_creation_evidence,
        result.integration_review_evidence,
        result.test_run_evidence,
        result.extended_test_evidence,
        result.stabilization_evidence,
        result.release_candidate_evidence,
        result.runtime_validation_evidence,
        result.safety_evidence,
        result.observability_evidence,
        result.rollback_evidence,
        result.kill_switch_evidence,
        result.human_supervision_evidence,
        result.operational_boundary_evidence,
    )
    for evidence in evidences:
        lines.append(f"- {evidence.name}: present={evidence.present}, score={evidence.score}/100, risks={', '.join(risk.value for risk in evidence.risks) or 'none'}")
        lines.extend(f"  - {detail}" for detail in evidence.details if detail)
    lines.append("")
    lines.append("# Official Report Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Official Report Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "collect_extended_test_evidence",
    "collect_human_supervision_evidence",
    "collect_integration_review_evidence",
    "collect_kill_switch_evidence",
    "collect_observability_evidence",
    "collect_operational_boundary_evidence",
    "collect_release_candidate_evidence",
    "collect_rollback_evidence",
    "collect_runtime_creation_evidence",
    "collect_runtime_validation_evidence",
    "collect_safety_evidence",
    "collect_stabilization_evidence",
    "collect_test_run_evidence",
    "compute_official_report_score",
    "detect_official_report_risks",
    "generate_official_paper_validation_report",
    "generate_official_report_recommendations",
    "render_official_paper_validation_report_markdown",
]
