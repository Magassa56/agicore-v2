"""Decision-oriented review for AGIcore Trading v1 offline smoke demo."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_smoke_demo import run_agicore_trading_v1_offline_smoke_demo
from agicore.trading.agicore_trading_v1_offline_smoke_demo_models import (
    AGIcoreTradingV1OfflineSmokeDemoDecision,
    AGIcoreTradingV1OfflineSmokeDemoResult,
    AGIcoreTradingV1OfflineSmokeDemoStepStatus,
)
from agicore.trading.agicore_trading_v1_offline_smoke_demo_review_models import (
    AGIcoreTradingV1OfflineSmokeDemoBoundaryReview,
    AGIcoreTradingV1OfflineSmokeDemoReviewDecision,
    AGIcoreTradingV1OfflineSmokeDemoReviewFinding,
    AGIcoreTradingV1OfflineSmokeDemoReviewInput,
    AGIcoreTradingV1OfflineSmokeDemoReviewMetrics,
    AGIcoreTradingV1OfflineSmokeDemoReviewRecommendation,
    AGIcoreTradingV1OfflineSmokeDemoReviewReport,
    AGIcoreTradingV1OfflineSmokeDemoReviewResult,
    AGIcoreTradingV1OfflineSmokeDemoReviewRisk,
    AGIcoreTradingV1OfflineSmokeDemoReviewScore,
    AGIcoreTradingV1OfflineSmokeDemoReviewState,
    AGIcoreTradingV1OfflineSmokeDemoSandboxUsabilityReview,
    AGIcoreTradingV1OfflineSmokeDemoStepReview,
)


Risk = AGIcoreTradingV1OfflineSmokeDemoReviewRisk
Recommendation = AGIcoreTradingV1OfflineSmokeDemoReviewRecommendation
Decision = AGIcoreTradingV1OfflineSmokeDemoReviewDecision
State = AGIcoreTradingV1OfflineSmokeDemoReviewState

CSV_REPLAY_INPUT_STEP = "CSV_REPLAY_INPUT_STEP"
STRATEGY_REPLAY_ENGINE_STEP = "STRATEGY_REPLAY_ENGINE_STEP"
RISK_GUARD_STEP = "RISK_GUARD_STEP"
SIMULATED_BROKER_PREVIEW_STEP = "SIMULATED_BROKER_PREVIEW_STEP"
JOURNAL_WRITER_STEP = "JOURNAL_WRITER_STEP"
OFFLINE_REPORT_STEP = "OFFLINE_REPORT_STEP"
END_TO_END_VALIDATION_STEP = "END_TO_END_VALIDATION_STEP"

EXPECTED_STEPS: tuple[str, ...] = (
    CSV_REPLAY_INPUT_STEP,
    STRATEGY_REPLAY_ENGINE_STEP,
    RISK_GUARD_STEP,
    SIMULATED_BROKER_PREVIEW_STEP,
    JOURNAL_WRITER_STEP,
    OFFLINE_REPORT_STEP,
    END_TO_END_VALIDATION_STEP,
)

_STEP_RISKS: dict[str, Risk] = {
    CSV_REPLAY_INPUT_STEP: Risk.SMOKE_DEMO_CSV_REPLAY_STEP_FAILED,
    STRATEGY_REPLAY_ENGINE_STEP: Risk.SMOKE_DEMO_STRATEGY_REPLAY_STEP_FAILED,
    RISK_GUARD_STEP: Risk.SMOKE_DEMO_RISK_GUARD_STEP_FAILED,
    SIMULATED_BROKER_PREVIEW_STEP: Risk.SMOKE_DEMO_BROKER_PREVIEW_STEP_FAILED,
    JOURNAL_WRITER_STEP: Risk.SMOKE_DEMO_JOURNAL_STEP_FAILED,
    OFFLINE_REPORT_STEP: Risk.SMOKE_DEMO_OFFLINE_REPORT_STEP_FAILED,
    END_TO_END_VALIDATION_STEP: Risk.SMOKE_DEMO_END_TO_END_REVIEW_FAILED,
}

_FORCE_STEP_FAILURES: dict[str, str] = {
    CSV_REPLAY_INPUT_STEP: "force_csv_replay_step_failed",
    STRATEGY_REPLAY_ENGINE_STEP: "force_strategy_replay_step_failed",
    RISK_GUARD_STEP: "force_risk_guard_step_failed",
    SIMULATED_BROKER_PREVIEW_STEP: "force_broker_preview_step_failed",
    JOURNAL_WRITER_STEP: "force_journal_step_failed",
    OFFLINE_REPORT_STEP: "force_offline_report_step_failed",
    END_TO_END_VALIDATION_STEP: "force_end_to_end_review_failed",
}

_BOUNDARY_RISKS = {
    Risk.FILE_READ_BOUNDARY_VIOLATION,
    Risk.FILE_WRITE_BOUNDARY_VIOLATION,
    Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION,
    Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION,
    Risk.REAL_BROKER_BOUNDARY_VIOLATION,
    Risk.REAL_SECRET_BOUNDARY_VIOLATION,
    Risk.NETWORK_BOUNDARY_VIOLATION,
    Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION,
    Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION,
    Risk.POSITION_MUTATION_BOUNDARY_VIOLATION,
}


def _value(item: Any) -> str:
    return item.value if isinstance(item, Enum) else str(item)


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    out: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return tuple(out)


def _coerce_input(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineSmokeDemoReviewInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineSmokeDemoReviewInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineSmokeDemoReviewInput)}
    return AGIcoreTradingV1OfflineSmokeDemoReviewInput(**{key: value for key, value in dict(data).items() if key in allowed})


def _smoke_demo_result(data: AGIcoreTradingV1OfflineSmokeDemoReviewInput) -> AGIcoreTradingV1OfflineSmokeDemoResult | None:
    if data.smoke_demo_result is not None:
        return data.smoke_demo_result
    if data.smoke_demo_input is not None:
        return run_agicore_trading_v1_offline_smoke_demo(data.smoke_demo_input)
    return None


def _step(result: AGIcoreTradingV1OfflineSmokeDemoResult | None, name: str) -> Any | None:
    if result is None:
        return None
    for step in result.steps:
        if step.name == name:
            return step
    return None


def _input_boundary_risks(data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | None) -> tuple[Risk, ...]:
    if data is None:
        return ()
    risks: list[Risk] = []
    if data.file_read_requested:
        risks.append(Risk.FILE_READ_BOUNDARY_VIOLATION)
    if data.file_write_requested:
        risks.append(Risk.FILE_WRITE_BOUNDARY_VIOLATION)
    if data.real_data_access_requested:
        risks.append(Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION)
    if data.data_directory_access_requested:
        risks.append(Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION)
    if data.broker_connection_requested:
        risks.append(Risk.REAL_BROKER_BOUNDARY_VIOLATION)
    if data.secret_read_requested:
        risks.append(Risk.REAL_SECRET_BOUNDARY_VIOLATION)
    if data.network_requested or data.http_requested or data.websocket_requested or data.socket_requested or data.external_api_requested:
        risks.append(Risk.NETWORK_BOUNDARY_VIOLATION)
    if data.order_execution_requested:
        risks.append(Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION)
    if data.account_access_requested:
        risks.append(Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION)
    if data.position_mutation_requested:
        risks.append(Risk.POSITION_MUTATION_BOUNDARY_VIOLATION)
    return _dedupe(risks)


def _source_boundary_risks(result: AGIcoreTradingV1OfflineSmokeDemoResult | None) -> tuple[Risk, ...]:
    if result is None:
        return ()
    risks: list[Risk] = []
    source_risk_names = {_value(risk) for risk in result.risks}
    for risk in _BOUNDARY_RISKS:
        if risk.value in source_risk_names:
            risks.append(risk)
    if result.file_read:
        risks.append(Risk.FILE_READ_BOUNDARY_VIOLATION)
    if result.file_written:
        risks.append(Risk.FILE_WRITE_BOUNDARY_VIOLATION)
    if result.data_accessed:
        risks.append(Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION)
    if result.real_order_submitted:
        risks.append(Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION)
    if result.real_account_accessed:
        risks.append(Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION)
    if result.position_mutated:
        risks.append(Risk.POSITION_MUTATION_BOUNDARY_VIOLATION)
    if not result.offline_only:
        risks.append(Risk.NETWORK_BOUNDARY_VIOLATION)
    if not result.in_memory_only:
        risks.append(Risk.FILE_READ_BOUNDARY_VIOLATION)
    return _dedupe(risks)


def validate_agicore_trading_v1_offline_smoke_demo_review_input(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and (payload.smoke_demo_result is not None or payload.smoke_demo_input is not None))


def review_smoke_demo_approval(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
    smoke_demo: AGIcoreTradingV1OfflineSmokeDemoResult | None = None,
) -> AGIcoreTradingV1OfflineSmokeDemoReviewFinding:
    payload = _coerce_input(data)
    result = smoke_demo or (_smoke_demo_result(payload) if payload else None)
    passed = bool(
        result
        and result.decision is AGIcoreTradingV1OfflineSmokeDemoDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO
        and not (payload and payload.force_smoke_demo_not_approved)
    )
    return AGIcoreTradingV1OfflineSmokeDemoReviewFinding(
        finding_id="SMOKE_DEMO_APPROVAL",
        category="APPROVAL",
        passed=passed,
        message="smoke demo is approved" if passed else "smoke demo is not approved",
        risk=None if passed else Risk.SMOKE_DEMO_NOT_APPROVED,
    )


def _review_step(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | None,
    smoke_demo: AGIcoreTradingV1OfflineSmokeDemoResult | None,
    step_name: str,
) -> AGIcoreTradingV1OfflineSmokeDemoStepReview:
    source_step = _step(smoke_demo, step_name)
    forced = bool(data and getattr(data, _FORCE_STEP_FAILURES[step_name]))
    passed = bool(source_step and source_step.status is AGIcoreTradingV1OfflineSmokeDemoStepStatus.PASSED and not forced)
    return AGIcoreTradingV1OfflineSmokeDemoStepReview(
        step_name=step_name,
        passed=passed,
        status="PASSED" if passed else "FAILED",
        message=f"{step_name} reviewed" if passed else f"{step_name} failed review",
        risk=None if passed else _STEP_RISKS[step_name],
    )


def review_smoke_demo_csv_replay_step(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
    smoke_demo: AGIcoreTradingV1OfflineSmokeDemoResult | None = None,
) -> AGIcoreTradingV1OfflineSmokeDemoStepReview:
    payload = _coerce_input(data)
    return _review_step(payload, smoke_demo or (_smoke_demo_result(payload) if payload else None), CSV_REPLAY_INPUT_STEP)


def review_smoke_demo_strategy_replay_step(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
    smoke_demo: AGIcoreTradingV1OfflineSmokeDemoResult | None = None,
) -> AGIcoreTradingV1OfflineSmokeDemoStepReview:
    payload = _coerce_input(data)
    return _review_step(payload, smoke_demo or (_smoke_demo_result(payload) if payload else None), STRATEGY_REPLAY_ENGINE_STEP)


def review_smoke_demo_risk_guard_step(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
    smoke_demo: AGIcoreTradingV1OfflineSmokeDemoResult | None = None,
) -> AGIcoreTradingV1OfflineSmokeDemoStepReview:
    payload = _coerce_input(data)
    return _review_step(payload, smoke_demo or (_smoke_demo_result(payload) if payload else None), RISK_GUARD_STEP)


def review_smoke_demo_broker_preview_step(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
    smoke_demo: AGIcoreTradingV1OfflineSmokeDemoResult | None = None,
) -> AGIcoreTradingV1OfflineSmokeDemoStepReview:
    payload = _coerce_input(data)
    return _review_step(payload, smoke_demo or (_smoke_demo_result(payload) if payload else None), SIMULATED_BROKER_PREVIEW_STEP)


def review_smoke_demo_journal_step(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
    smoke_demo: AGIcoreTradingV1OfflineSmokeDemoResult | None = None,
) -> AGIcoreTradingV1OfflineSmokeDemoStepReview:
    payload = _coerce_input(data)
    return _review_step(payload, smoke_demo or (_smoke_demo_result(payload) if payload else None), JOURNAL_WRITER_STEP)


def review_smoke_demo_offline_report_step(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
    smoke_demo: AGIcoreTradingV1OfflineSmokeDemoResult | None = None,
) -> AGIcoreTradingV1OfflineSmokeDemoStepReview:
    payload = _coerce_input(data)
    return _review_step(payload, smoke_demo or (_smoke_demo_result(payload) if payload else None), OFFLINE_REPORT_STEP)


def review_smoke_demo_end_to_end_flow(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
    smoke_demo: AGIcoreTradingV1OfflineSmokeDemoResult | None = None,
) -> AGIcoreTradingV1OfflineSmokeDemoReviewFinding:
    payload = _coerce_input(data)
    result = smoke_demo or (_smoke_demo_result(payload) if payload else None)
    step_review = _review_step(payload, result, END_TO_END_VALIDATION_STEP)
    names = {step.name for step in result.steps} if result else set()
    passed = step_review.passed and all(name in names for name in EXPECTED_STEPS)
    return AGIcoreTradingV1OfflineSmokeDemoReviewFinding(
        finding_id="SMOKE_DEMO_END_TO_END_FLOW",
        category="END_TO_END",
        passed=passed,
        message="smoke demo end-to-end flow passed" if passed else "smoke demo end-to-end flow failed",
        risk=None if passed else Risk.SMOKE_DEMO_END_TO_END_REVIEW_FAILED,
    )


def review_smoke_demo_read_only_decision(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
    smoke_demo: AGIcoreTradingV1OfflineSmokeDemoResult | None = None,
) -> AGIcoreTradingV1OfflineSmokeDemoReviewFinding:
    payload = _coerce_input(data)
    result = smoke_demo or (_smoke_demo_result(payload) if payload else None)
    metrics = getattr(result, "metrics", None)
    passed = bool(
        metrics
        and metrics.read_only_decision
        and metrics.broker_preview_read_only
        and not (payload and payload.force_read_only_decision_invalid)
    )
    return AGIcoreTradingV1OfflineSmokeDemoReviewFinding(
        finding_id="SMOKE_DEMO_READ_ONLY_DECISION",
        category="READ_ONLY",
        passed=passed,
        message="smoke demo decision is read-only only" if passed else "smoke demo read-only decision is invalid",
        risk=None if passed else Risk.SMOKE_DEMO_READ_ONLY_DECISION_INVALID,
    )


def review_smoke_demo_no_live_trading_claim(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineSmokeDemoReviewFinding:
    payload = _coerce_input(data)
    passed = not (payload and payload.force_live_trading_overclaim)
    return AGIcoreTradingV1OfflineSmokeDemoReviewFinding(
        finding_id="NO_LIVE_TRADING_CLAIM",
        category="OVERCLAIM",
        passed=passed,
        message="review does not claim live trading readiness" if passed else "review overclaims live trading readiness",
        risk=None if passed else Risk.LIVE_TRADING_READINESS_OVERCLAIM,
    )


def review_smoke_demo_no_profitability_claim(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineSmokeDemoReviewFinding:
    payload = _coerce_input(data)
    passed = not (payload and payload.force_profitability_overclaim)
    return AGIcoreTradingV1OfflineSmokeDemoReviewFinding(
        finding_id="NO_PROFITABILITY_CLAIM",
        category="OVERCLAIM",
        passed=passed,
        message="review does not claim profitability proof" if passed else "review overclaims profitability proof",
        risk=None if passed else Risk.PROFITABILITY_PROOF_OVERCLAIM,
    )


def review_smoke_demo_sandbox_usability(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
    smoke_demo: AGIcoreTradingV1OfflineSmokeDemoResult | None = None,
) -> AGIcoreTradingV1OfflineSmokeDemoSandboxUsabilityReview:
    payload = _coerce_input(data)
    result = smoke_demo or (_smoke_demo_result(payload) if payload else None)
    report = getattr(result, "report", None)
    no_live = review_smoke_demo_no_live_trading_claim(payload).passed
    no_profit = review_smoke_demo_no_profitability_claim(payload).passed
    passed = bool(
        result
        and result.offline_only
        and result.in_memory_only
        and report
        and report.markdown
        and report.json
        and no_live
        and no_profit
        and not (payload and payload.force_sandbox_usability_incomplete)
    )
    return AGIcoreTradingV1OfflineSmokeDemoSandboxUsabilityReview(
        passed=passed,
        local_sandbox_usable=passed,
        deterministic=True,
        in_memory_reports=bool(report and report.markdown and report.json),
        no_live_trading_claim=no_live,
        no_profitability_claim=no_profit,
    )


def review_smoke_demo_boundaries(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
    smoke_demo: AGIcoreTradingV1OfflineSmokeDemoResult | None = None,
) -> AGIcoreTradingV1OfflineSmokeDemoBoundaryReview:
    payload = _coerce_input(data)
    result = smoke_demo or (_smoke_demo_result(payload) if payload else None)
    risks = _dedupe((*_source_boundary_risks(result), *_input_boundary_risks(payload)))
    return AGIcoreTradingV1OfflineSmokeDemoBoundaryReview(
        passed=not risks,
        offline_only=bool(result and result.offline_only),
        in_memory_only=bool(result and result.in_memory_only),
        file_read=bool(result and result.file_read),
        file_written=bool(result and result.file_written),
        data_accessed=bool(result and result.data_accessed),
        real_order_submitted=bool(result and result.real_order_submitted),
        real_account_accessed=bool(result and result.real_account_accessed),
        position_mutated=bool(result and result.position_mutated),
        risks=risks,
    )


def compute_agicore_trading_v1_offline_smoke_demo_review_metrics(
    step_reviews: tuple[AGIcoreTradingV1OfflineSmokeDemoStepReview, ...],
    findings: tuple[AGIcoreTradingV1OfflineSmokeDemoReviewFinding, ...],
    sandbox_usability_review: AGIcoreTradingV1OfflineSmokeDemoSandboxUsabilityReview | None,
    boundary_review: AGIcoreTradingV1OfflineSmokeDemoBoundaryReview | None,
    final_decision: str = "",
) -> AGIcoreTradingV1OfflineSmokeDemoReviewMetrics:
    failed = sum(1 for review in step_reviews if not review.passed)
    finding_map = {finding.finding_id: finding.passed for finding in findings}
    return AGIcoreTradingV1OfflineSmokeDemoReviewMetrics(
        expected_step_count=len(EXPECTED_STEPS),
        reviewed_step_count=len(step_reviews),
        failed_step_count=failed,
        end_to_end_passed=bool(finding_map.get("SMOKE_DEMO_END_TO_END_FLOW")),
        read_only_decision_passed=bool(finding_map.get("SMOKE_DEMO_READ_ONLY_DECISION")),
        sandbox_usability_passed=bool(sandbox_usability_review and sandbox_usability_review.passed),
        boundary_passed=bool(boundary_review and boundary_review.passed),
        findings_count=len(findings),
        global_score=100,
        final_decision=final_decision,
    )


def detect_agicore_trading_v1_offline_smoke_demo_review_risks(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
    smoke_demo: AGIcoreTradingV1OfflineSmokeDemoResult | None = None,
    step_reviews: tuple[AGIcoreTradingV1OfflineSmokeDemoStepReview, ...] = (),
    findings: tuple[AGIcoreTradingV1OfflineSmokeDemoReviewFinding, ...] = (),
    sandbox_usability_review: AGIcoreTradingV1OfflineSmokeDemoSandboxUsabilityReview | None = None,
    boundary_review: AGIcoreTradingV1OfflineSmokeDemoBoundaryReview | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    result = smoke_demo or (_smoke_demo_result(payload) if payload else None)
    risks: list[Risk] = []
    if not payload or not result or payload.force_smoke_demo_not_approved:
        risks.append(Risk.SMOKE_DEMO_NOT_APPROVED)
    elif result.decision is not AGIcoreTradingV1OfflineSmokeDemoDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO:
        risks.append(Risk.SMOKE_DEMO_NOT_APPROVED)
    for review in step_reviews:
        if not review.passed and review.risk is not None:
            risks.append(review.risk)
    for finding in findings:
        if not finding.passed and finding.risk is not None:
            risks.append(finding.risk)
    if sandbox_usability_review is not None and not sandbox_usability_review.passed:
        risks.append(Risk.SMOKE_DEMO_SANDBOX_USABILITY_INCOMPLETE)
    if boundary_review is not None:
        risks.extend(boundary_review.risks)
    if payload:
        if payload.force_real_broker_overclaim:
            risks.append(Risk.REAL_BROKER_READINESS_OVERCLAIM)
        if payload.force_real_order_overclaim:
            risks.append(Risk.REAL_ORDER_EXECUTION_OVERCLAIM)
        if payload.force_financial_advice_overclaim:
            risks.append(Risk.FINANCIAL_ADVICE_OVERCLAIM)
    return _dedupe(risks)


def compute_agicore_trading_v1_offline_smoke_demo_review_score(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
    approval: AGIcoreTradingV1OfflineSmokeDemoReviewFinding | None = None,
    end_to_end: AGIcoreTradingV1OfflineSmokeDemoReviewFinding | None = None,
    step_reviews: tuple[AGIcoreTradingV1OfflineSmokeDemoStepReview, ...] = (),
    read_only: AGIcoreTradingV1OfflineSmokeDemoReviewFinding | None = None,
    sandbox_usability_review: AGIcoreTradingV1OfflineSmokeDemoSandboxUsabilityReview | None = None,
    boundary_review: AGIcoreTradingV1OfflineSmokeDemoBoundaryReview | None = None,
    no_live_claim: AGIcoreTradingV1OfflineSmokeDemoReviewFinding | None = None,
    no_profit_claim: AGIcoreTradingV1OfflineSmokeDemoReviewFinding | None = None,
    risks: tuple[Risk, ...] = (),
    report_present: bool = True,
) -> AGIcoreTradingV1OfflineSmokeDemoReviewScore:
    _coerce_input(data)
    approval_score = 100 if approval and approval.passed else 0
    end_to_end_score = 100 if end_to_end and end_to_end.passed else 0
    step_score = 100 if len(step_reviews) == len(EXPECTED_STEPS) and all(review.passed for review in step_reviews) else 0
    read_only_score = 100 if read_only and read_only.passed else 0
    sandbox_score = 100 if sandbox_usability_review and sandbox_usability_review.passed else 0
    boundary_score = 100 if boundary_review and boundary_review.passed else 0
    overclaim_score = 100 if no_live_claim and no_live_claim.passed and no_profit_claim and no_profit_claim.passed else 0
    report_score = 100 if report_present else 0
    overall = min(
        approval_score,
        end_to_end_score,
        step_score,
        read_only_score,
        sandbox_score,
        boundary_score,
        overclaim_score,
        report_score,
    )
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineSmokeDemoReviewScore(
        overall_score=overall,
        approval_score=approval_score,
        end_to_end_score=end_to_end_score,
        step_score=step_score,
        read_only_score=read_only_score,
        sandbox_usability_score=sandbox_score,
        boundary_score=boundary_score,
        overclaim_score=overclaim_score,
        report_score=report_score,
    )


def generate_agicore_trading_v1_offline_smoke_demo_review_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.SMOKE_DEMO_NOT_APPROVED: Recommendation.FIX_SMOKE_DEMO_APPROVAL,
        Risk.SMOKE_DEMO_END_TO_END_REVIEW_FAILED: Recommendation.FIX_SMOKE_DEMO_END_TO_END_FLOW,
        Risk.SMOKE_DEMO_CSV_REPLAY_STEP_FAILED: Recommendation.FIX_SMOKE_DEMO_CSV_REPLAY_STEP,
        Risk.SMOKE_DEMO_STRATEGY_REPLAY_STEP_FAILED: Recommendation.FIX_SMOKE_DEMO_STRATEGY_REPLAY_STEP,
        Risk.SMOKE_DEMO_RISK_GUARD_STEP_FAILED: Recommendation.FIX_SMOKE_DEMO_RISK_GUARD_STEP,
        Risk.SMOKE_DEMO_BROKER_PREVIEW_STEP_FAILED: Recommendation.FIX_SMOKE_DEMO_BROKER_PREVIEW_STEP,
        Risk.SMOKE_DEMO_JOURNAL_STEP_FAILED: Recommendation.FIX_SMOKE_DEMO_JOURNAL_STEP,
        Risk.SMOKE_DEMO_OFFLINE_REPORT_STEP_FAILED: Recommendation.FIX_SMOKE_DEMO_OFFLINE_REPORT_STEP,
        Risk.SMOKE_DEMO_READ_ONLY_DECISION_INVALID: Recommendation.KEEP_SMOKE_DEMO_READ_ONLY,
        Risk.SMOKE_DEMO_SANDBOX_USABILITY_INCOMPLETE: Recommendation.CLARIFY_SANDBOX_USAGE,
        Risk.LIVE_TRADING_READINESS_OVERCLAIM: Recommendation.REMOVE_LIVE_TRADING_READINESS_CLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM: Recommendation.REMOVE_REAL_BROKER_READINESS_CLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM: Recommendation.REMOVE_REAL_ORDER_EXECUTION_CLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM: Recommendation.REMOVE_PROFITABILITY_PROOF_CLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM: Recommendation.REMOVE_FINANCIAL_ADVICE_CLAIM,
        Risk.FILE_READ_BOUNDARY_VIOLATION: Recommendation.REMOVE_FILE_READ,
        Risk.FILE_WRITE_BOUNDARY_VIOLATION: Recommendation.REMOVE_FILE_WRITE,
        Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_DATA_ACCESS,
        Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_DATA_DIRECTORY_ACCESS,
        Risk.REAL_BROKER_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_BROKER_ACCESS,
        Risk.REAL_SECRET_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_SECRET_ACCESS,
        Risk.NETWORK_BOUNDARY_VIOLATION: Recommendation.REMOVE_NETWORK_ACCESS,
        Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION: Recommendation.REMOVE_ORDER_EXECUTION,
        Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_ACCOUNT_ACCESS,
        Risk.POSITION_MUTATION_BOUNDARY_VIOLATION: Recommendation.REMOVE_POSITION_MUTATION,
    }
    recommendations = [mapping[risk] for risk in risks if risk in mapping]
    if not recommendations:
        recommendations.append(Recommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE)
    return _dedupe(recommendations)


def _payload_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _payload_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_payload_value(item) for item in value]
    if hasattr(value, "__dict__"):
        return {key: _payload_value(item) for key, item in vars(value).items() if not key.startswith("_") and key != "smoke_demo_result"}
    return str(value)


def render_agicore_trading_v1_offline_smoke_demo_review_markdown_report(
    result: AGIcoreTradingV1OfflineSmokeDemoReviewResult | Mapping[str, Any],
) -> str:
    if not isinstance(result, AGIcoreTradingV1OfflineSmokeDemoReviewResult):
        return "# AGIcore Trading v1 Offline Smoke Demo Review\n"
    lines = [
        "# AGIcore Trading v1 Offline Smoke Demo Review",
        "",
        f"- decision: {result.decision.value}",
        f"- state: {result.state.value}",
        f"- score: {result.score.overall_score}",
        "- status: offline/sandbox review only",
        "- local_sandbox_usable: true",
        "- live_trading_ready: false",
        "- real_broker_ready: false",
        "- real_order_execution: false",
        "- profitability_proven: false",
        "- financial_advice: false",
        f"- risks: {', '.join(risk.value for risk in result.risks) if result.risks else 'none'}",
        "",
        "## Step Review",
    ]
    for review in result.step_reviews:
        lines.append(f"- {review.step_name}: {'PASS' if review.passed else 'FAIL'} - {review.message}")
    lines.extend(
        [
            "",
            "## Safety Boundaries",
            f"- file_read: {str(result.file_read).lower()}",
            f"- file_written: {str(result.file_written).lower()}",
            f"- data_accessed: {str(result.data_accessed).lower()}",
            f"- real_order_submitted: {str(result.real_order_submitted).lower()}",
            f"- real_account_accessed: {str(result.real_account_accessed).lower()}",
            f"- position_mutated: {str(result.position_mutated).lower()}",
        ]
    )
    return "\n".join(lines) + "\n"


def render_agicore_trading_v1_offline_smoke_demo_review_json_report(
    result: AGIcoreTradingV1OfflineSmokeDemoReviewResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineSmokeDemoReviewResult):
        payload = {
            "schema": "agicore_trading_v1_offline_smoke_demo_review",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "findings": _payload_value(result.findings),
            "step_reviews": _payload_value(result.step_reviews),
            "boundary_review": _payload_value(result.boundary_review),
            "sandbox_usability_review": _payload_value(result.sandbox_usability_review),
            "metrics": _payload_value(result.metrics),
            "local_sandbox_usable": bool(result.sandbox_usability_review and result.sandbox_usability_review.passed),
            "live_trading_ready": False,
            "real_broker_ready": False,
            "real_order_execution": False,
            "profitability_proven": False,
            "financial_advice": False,
            "file_read": result.file_read,
            "file_written": result.file_written,
            "data_accessed": result.data_accessed,
            "real_order_submitted": result.real_order_submitted,
            "real_account_accessed": result.real_account_accessed,
            "position_mutated": result.position_mutated,
        }
    else:
        payload = dict(result)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def assert_agicore_trading_v1_offline_smoke_demo_review_boundaries(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return not _input_boundary_risks(payload)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW
    if any(risk in _BOUNDARY_RISKS for risk in risks):
        return Decision.REQUIRE_SMOKE_DEMO_BOUNDARY_FIXES
    if Risk.SMOKE_DEMO_NOT_APPROVED in risks:
        return Decision.REQUIRE_SMOKE_DEMO_FIXES
    if Risk.SMOKE_DEMO_END_TO_END_REVIEW_FAILED in risks:
        return Decision.REQUIRE_SMOKE_DEMO_END_TO_END_FIXES
    step_risks = {
        Risk.SMOKE_DEMO_CSV_REPLAY_STEP_FAILED,
        Risk.SMOKE_DEMO_STRATEGY_REPLAY_STEP_FAILED,
        Risk.SMOKE_DEMO_RISK_GUARD_STEP_FAILED,
        Risk.SMOKE_DEMO_BROKER_PREVIEW_STEP_FAILED,
        Risk.SMOKE_DEMO_JOURNAL_STEP_FAILED,
        Risk.SMOKE_DEMO_OFFLINE_REPORT_STEP_FAILED,
    }
    if any(risk in step_risks for risk in risks):
        return Decision.REQUIRE_SMOKE_DEMO_STEP_REVIEW_FIXES
    if Risk.SMOKE_DEMO_READ_ONLY_DECISION_INVALID in risks:
        return Decision.REQUIRE_SMOKE_DEMO_READ_ONLY_DECISION_FIXES
    overclaims = {
        Risk.LIVE_TRADING_READINESS_OVERCLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM,
    }
    if any(risk in overclaims for risk in risks):
        return Decision.REQUIRE_SMOKE_DEMO_NO_OVERCLAIM_FIXES
    if Risk.SMOKE_DEMO_SANDBOX_USABILITY_INCOMPLETE in risks:
        return Decision.REQUIRE_SMOKE_DEMO_SANDBOX_USABILITY_FIXES
    return Decision.BLOCK_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW


def _state_for(data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE
    return State.AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW_BLOCKED


def review_agicore_trading_v1_offline_smoke_demo(
    data: AGIcoreTradingV1OfflineSmokeDemoReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineSmokeDemoReviewResult:
    payload = _coerce_input(data)
    smoke_demo = _smoke_demo_result(payload) if payload else None
    approval = review_smoke_demo_approval(payload, smoke_demo)
    end_to_end = review_smoke_demo_end_to_end_flow(payload, smoke_demo)
    read_only = review_smoke_demo_read_only_decision(payload, smoke_demo)
    no_live = review_smoke_demo_no_live_trading_claim(payload)
    no_profit = review_smoke_demo_no_profitability_claim(payload)
    step_reviews = (
        review_smoke_demo_csv_replay_step(payload, smoke_demo),
        review_smoke_demo_strategy_replay_step(payload, smoke_demo),
        review_smoke_demo_risk_guard_step(payload, smoke_demo),
        review_smoke_demo_broker_preview_step(payload, smoke_demo),
        review_smoke_demo_journal_step(payload, smoke_demo),
        review_smoke_demo_offline_report_step(payload, smoke_demo),
        _review_step(payload, smoke_demo, END_TO_END_VALIDATION_STEP),
    ) if payload else ()
    sandbox_review = review_smoke_demo_sandbox_usability(payload, smoke_demo) if payload else None
    boundary_review = review_smoke_demo_boundaries(payload, smoke_demo) if payload else None
    findings = (approval, end_to_end, read_only, no_live, no_profit)
    risks = detect_agicore_trading_v1_offline_smoke_demo_review_risks(
        payload,
        smoke_demo,
        step_reviews,
        findings,
        sandbox_review,
        boundary_review,
    )
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    report_present = not (payload and payload.force_report_missing)
    score = compute_agicore_trading_v1_offline_smoke_demo_review_score(
        payload,
        approval,
        end_to_end,
        step_reviews,
        read_only,
        sandbox_review,
        boundary_review,
        no_live,
        no_profit,
        risks,
        report_present,
    )
    metrics = compute_agicore_trading_v1_offline_smoke_demo_review_metrics(
        step_reviews,
        findings,
        sandbox_review,
        boundary_review,
        decision.value,
    )
    metrics = AGIcoreTradingV1OfflineSmokeDemoReviewMetrics(
        expected_step_count=metrics.expected_step_count,
        reviewed_step_count=metrics.reviewed_step_count,
        failed_step_count=metrics.failed_step_count,
        end_to_end_passed=metrics.end_to_end_passed,
        read_only_decision_passed=metrics.read_only_decision_passed,
        sandbox_usability_passed=metrics.sandbox_usability_passed,
        boundary_passed=metrics.boundary_passed,
        findings_count=metrics.findings_count,
        global_score=score.overall_score,
        final_decision=decision.value,
    )
    recommendations = generate_agicore_trading_v1_offline_smoke_demo_review_recommendations(risks)
    base_result = AGIcoreTradingV1OfflineSmokeDemoReviewResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        findings=findings,
        step_reviews=step_reviews,
        boundary_review=boundary_review,
        sandbox_usability_review=sandbox_review,
        metrics=metrics,
        report=None,
        smoke_demo_result=smoke_demo,
        offline_only=True,
        in_memory_only=True,
        file_read=False,
        file_written=False,
        data_accessed=False,
        real_order_submitted=False,
        real_account_accessed=False,
        position_mutated=False,
    )
    report = None
    if report_present:
        report = AGIcoreTradingV1OfflineSmokeDemoReviewReport(
            markdown=render_agicore_trading_v1_offline_smoke_demo_review_markdown_report(base_result),
            json=render_agicore_trading_v1_offline_smoke_demo_review_json_report(base_result),
        )
    return AGIcoreTradingV1OfflineSmokeDemoReviewResult(**{**base_result.__dict__, "report": report})
