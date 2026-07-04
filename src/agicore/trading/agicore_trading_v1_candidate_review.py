"""AGIcore Trading v1 offline candidate review."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_candidate import evaluate_agicore_trading_v1_candidate
from agicore.trading.agicore_trading_v1_candidate_models import (
    AGIcoreTradingV1CandidateDecision,
    AGIcoreTradingV1CandidateResult,
    AGIcoreTradingV1CapabilityName,
)
from agicore.trading.agicore_trading_v1_candidate_review_models import (
    AGIcoreTradingV1CandidateReviewDecision,
    AGIcoreTradingV1CandidateReviewFinding,
    AGIcoreTradingV1CandidateReviewInput,
    AGIcoreTradingV1CandidateReviewMetrics,
    AGIcoreTradingV1CandidateReviewRecommendation,
    AGIcoreTradingV1CandidateReviewReport,
    AGIcoreTradingV1CandidateReviewResult,
    AGIcoreTradingV1CandidateReviewRisk,
    AGIcoreTradingV1CandidateReviewScore,
    AGIcoreTradingV1CandidateReviewState,
    AGIcoreTradingV1CapabilityReview,
    AGIcoreTradingV1KnownLimitation,
    AGIcoreTradingV1ProductReadinessReview,
    AGIcoreTradingV1SafetyBoundaryReview,
    AGIcoreTradingV1SmokeReplayReview,
)


Risk = AGIcoreTradingV1CandidateReviewRisk
Recommendation = AGIcoreTradingV1CandidateReviewRecommendation
Decision = AGIcoreTradingV1CandidateReviewDecision
State = AGIcoreTradingV1CandidateReviewState
Capability = AGIcoreTradingV1CapabilityName

EXPECTED_CAPABILITIES: tuple[Capability, ...] = tuple(Capability)

_CAPABILITY_RISKS: dict[Capability, Risk] = {
    Capability.CSV_REPLAY_INPUT: Risk.CSV_REPLAY_CAPABILITY_REVIEW_FAILED,
    Capability.SYNTHETIC_MARKET_SCENARIO: Risk.SYNTHETIC_MARKET_CAPABILITY_REVIEW_FAILED,
    Capability.STRATEGY_REPLAY_ENGINE: Risk.STRATEGY_REPLAY_CAPABILITY_REVIEW_FAILED,
    Capability.SIMULATED_BROKER_STUB: Risk.SIMULATED_BROKER_CAPABILITY_REVIEW_FAILED,
    Capability.RISK_GUARD_ENFORCEMENT: Risk.RISK_GUARD_CAPABILITY_REVIEW_FAILED,
    Capability.JOURNAL_WRITER: Risk.JOURNAL_CAPABILITY_REVIEW_FAILED,
    Capability.OFFLINE_REPORT_MARKDOWN_JSON: Risk.OFFLINE_REPORT_CAPABILITY_REVIEW_FAILED,
}

_FORCE_REVIEW_FAILURES: dict[Capability, str] = {
    Capability.CSV_REPLAY_INPUT: "force_csv_replay_review_failed",
    Capability.SYNTHETIC_MARKET_SCENARIO: "force_synthetic_market_review_failed",
    Capability.STRATEGY_REPLAY_ENGINE: "force_strategy_replay_review_failed",
    Capability.SIMULATED_BROKER_STUB: "force_simulated_broker_review_failed",
    Capability.RISK_GUARD_ENFORCEMENT: "force_risk_guard_review_failed",
    Capability.JOURNAL_WRITER: "force_journal_review_failed",
    Capability.OFFLINE_REPORT_MARKDOWN_JSON: "force_offline_report_review_failed",
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
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1CandidateReviewInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1CandidateReviewInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1CandidateReviewInput)}
    return AGIcoreTradingV1CandidateReviewInput(**{key: value for key, value in dict(data).items() if key in allowed})


def _candidate_result(data: AGIcoreTradingV1CandidateReviewInput) -> AGIcoreTradingV1CandidateResult | None:
    if data.candidate_result is not None:
        return data.candidate_result
    if data.candidate_input is not None:
        return evaluate_agicore_trading_v1_candidate(data.candidate_input)
    return None


def _candidate_check(candidate: AGIcoreTradingV1CandidateResult | None, capability: Capability) -> Any | None:
    if candidate is None:
        return None
    for check in candidate.capability_checks:
        if Capability(check.capability) is capability:
            return check
    return None


def _forced_or_failed(
    data: AGIcoreTradingV1CandidateReviewInput | None,
    capability: Capability,
    candidate: AGIcoreTradingV1CandidateResult | None,
) -> AGIcoreTradingV1CapabilityReview:
    check = _candidate_check(candidate, capability)
    forced = bool(data and getattr(data, _FORCE_REVIEW_FAILURES[capability]))
    passed = bool(check and check.passed and not forced)
    detail = f"{capability.value} reviewed as offline/sandbox capability"
    if check is None:
        detail = f"{capability.value} source check missing"
    if forced:
        detail = f"{capability.value} review forced failed"
    return AGIcoreTradingV1CapabilityReview(
        capability=capability.value,
        passed=passed,
        detail=detail,
        source_decision=getattr(check, "component_decision", "") if check else "",
        source_risks=tuple(getattr(check, "risks", ())) if check else (),
    )


def _candidate_boundary_risks(candidate: AGIcoreTradingV1CandidateResult | None) -> tuple[Risk, ...]:
    if candidate is None:
        return ()
    risks: list[Risk] = []
    candidate_risk_names = {_value(risk) for risk in candidate.risks}
    for risk in _BOUNDARY_RISKS:
        if risk.value in candidate_risk_names:
            risks.append(risk)
    if candidate.file_read:
        risks.append(Risk.FILE_READ_BOUNDARY_VIOLATION)
    if candidate.file_written:
        risks.append(Risk.FILE_WRITE_BOUNDARY_VIOLATION)
    if candidate.data_accessed:
        risks.append(Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION)
    if candidate.real_order_submitted:
        risks.append(Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION)
    if candidate.real_account_accessed:
        risks.append(Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION)
    if candidate.position_mutated:
        risks.append(Risk.POSITION_MUTATION_BOUNDARY_VIOLATION)
    if not candidate.offline_only:
        risks.append(Risk.NETWORK_BOUNDARY_VIOLATION)
    if not candidate.in_memory_only:
        risks.append(Risk.FILE_READ_BOUNDARY_VIOLATION)
    return _dedupe(risks)


def _input_boundary_risks(data: AGIcoreTradingV1CandidateReviewInput | None) -> tuple[Risk, ...]:
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


def validate_agicore_trading_v1_candidate_review_input(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and (payload.candidate_result is not None or payload.candidate_input is not None))


def review_v1_candidate_capability_coverage(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
    candidate: AGIcoreTradingV1CandidateResult | None = None,
) -> AGIcoreTradingV1CandidateReviewFinding:
    payload = _coerce_input(data)
    source = candidate or (_candidate_result(payload) if payload else None)
    source_capabilities = {Capability(check.capability) for check in source.capability_checks} if source else set()
    passed = bool(source and source_capabilities == set(EXPECTED_CAPABILITIES) and not (payload and payload.force_capability_coverage_incomplete))
    return AGIcoreTradingV1CandidateReviewFinding(
        finding_id="V1_CAPABILITY_COVERAGE",
        category="CAPABILITY_COVERAGE",
        passed=passed,
        message="all mandatory V1 capabilities are covered" if passed else "mandatory V1 capability coverage is incomplete",
        risk=None if passed else Risk.V1_CAPABILITY_COVERAGE_INCOMPLETE,
    )


def review_v1_candidate_csv_replay_capability(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
    candidate: AGIcoreTradingV1CandidateResult | None = None,
) -> AGIcoreTradingV1CapabilityReview:
    payload = _coerce_input(data)
    return _forced_or_failed(payload, Capability.CSV_REPLAY_INPUT, candidate or (_candidate_result(payload) if payload else None))


def review_v1_candidate_synthetic_market_capability(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
    candidate: AGIcoreTradingV1CandidateResult | None = None,
) -> AGIcoreTradingV1CapabilityReview:
    payload = _coerce_input(data)
    return _forced_or_failed(payload, Capability.SYNTHETIC_MARKET_SCENARIO, candidate or (_candidate_result(payload) if payload else None))


def review_v1_candidate_strategy_replay_capability(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
    candidate: AGIcoreTradingV1CandidateResult | None = None,
) -> AGIcoreTradingV1CapabilityReview:
    payload = _coerce_input(data)
    return _forced_or_failed(payload, Capability.STRATEGY_REPLAY_ENGINE, candidate or (_candidate_result(payload) if payload else None))


def review_v1_candidate_simulated_broker_capability(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
    candidate: AGIcoreTradingV1CandidateResult | None = None,
) -> AGIcoreTradingV1CapabilityReview:
    payload = _coerce_input(data)
    return _forced_or_failed(payload, Capability.SIMULATED_BROKER_STUB, candidate or (_candidate_result(payload) if payload else None))


def review_v1_candidate_risk_guard_capability(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
    candidate: AGIcoreTradingV1CandidateResult | None = None,
) -> AGIcoreTradingV1CapabilityReview:
    payload = _coerce_input(data)
    return _forced_or_failed(payload, Capability.RISK_GUARD_ENFORCEMENT, candidate or (_candidate_result(payload) if payload else None))


def review_v1_candidate_journal_capability(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
    candidate: AGIcoreTradingV1CandidateResult | None = None,
) -> AGIcoreTradingV1CapabilityReview:
    payload = _coerce_input(data)
    return _forced_or_failed(payload, Capability.JOURNAL_WRITER, candidate or (_candidate_result(payload) if payload else None))


def review_v1_candidate_offline_report_capability(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
    candidate: AGIcoreTradingV1CandidateResult | None = None,
) -> AGIcoreTradingV1CapabilityReview:
    payload = _coerce_input(data)
    return _forced_or_failed(payload, Capability.OFFLINE_REPORT_MARKDOWN_JSON, candidate or (_candidate_result(payload) if payload else None))


def review_v1_candidate_smoke_replay(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
    candidate: AGIcoreTradingV1CandidateResult | None = None,
) -> AGIcoreTradingV1SmokeReplayReview:
    payload = _coerce_input(data)
    source = candidate or (_candidate_result(payload) if payload else None)
    smoke = source.smoke_replay if source else None
    forced = bool(payload and payload.force_smoke_replay_failed)
    passed = bool(smoke and smoke.passed and smoke.read_only and smoke.offline_only and not forced)
    return AGIcoreTradingV1SmokeReplayReview(
        passed=passed,
        status="PASSED" if passed else "FAILED",
        read_only=bool(smoke and smoke.read_only),
        offline_only=bool(smoke and smoke.offline_only),
        real_order_submitted=bool(smoke and smoke.real_order_submitted),
        real_account_accessed=bool(smoke and smoke.real_account_accessed),
        position_mutated=bool(smoke and smoke.position_mutated),
    )


def review_v1_candidate_safety_boundaries(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
    candidate: AGIcoreTradingV1CandidateResult | None = None,
) -> AGIcoreTradingV1SafetyBoundaryReview:
    payload = _coerce_input(data)
    source = candidate or (_candidate_result(payload) if payload else None)
    risks = _dedupe((*_candidate_boundary_risks(source), *_input_boundary_risks(payload)))
    return AGIcoreTradingV1SafetyBoundaryReview(
        passed=not risks,
        offline_only=bool(source and source.offline_only),
        in_memory_only=bool(source and source.in_memory_only),
        file_read=bool(source and source.file_read),
        file_written=bool(source and source.file_written),
        data_accessed=bool(source and source.data_accessed),
        real_order_submitted=bool(source and source.real_order_submitted),
        real_account_accessed=bool(source and source.real_account_accessed),
        position_mutated=bool(source and source.position_mutated),
        risks=risks,
    )


def review_v1_candidate_no_live_trading_claim(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1CandidateReviewFinding:
    payload = _coerce_input(data)
    passed = not (payload and payload.force_live_trading_readiness_overclaim)
    return AGIcoreTradingV1CandidateReviewFinding(
        finding_id="NO_LIVE_TRADING_CLAIM",
        category="PRODUCT_CLAIM",
        passed=passed,
        message="review states offline candidate only" if passed else "review overclaims live trading readiness",
        risk=None if passed else Risk.LIVE_TRADING_READINESS_OVERCLAIM,
    )


def review_v1_candidate_no_profitability_claim(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1CandidateReviewFinding:
    payload = _coerce_input(data)
    passed = not (payload and payload.force_profitability_claim)
    return AGIcoreTradingV1CandidateReviewFinding(
        finding_id="NO_PROFITABILITY_CLAIM",
        category="PRODUCT_CLAIM",
        passed=passed,
        message="review makes no profitability proof claim" if passed else "review includes unsupported profitability claim",
        risk=None if passed else Risk.PROFITABILITY_PROOF_MISSING,
    )


def review_v1_candidate_product_readiness(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1ProductReadinessReview:
    payload = _coerce_input(data)
    no_live = review_v1_candidate_no_live_trading_claim(payload).passed
    no_profit = review_v1_candidate_no_profitability_claim(payload).passed
    forced = bool(payload and payload.force_product_readiness_incomplete)
    passed = no_live and no_profit and not forced
    return AGIcoreTradingV1ProductReadinessReview(
        passed=passed,
        offline_candidate_only=True,
        product_decision="ready for offline release decision" if passed else "requires review fixes before offline release decision",
        no_live_trading_claim=no_live,
        no_profitability_claim=no_profit,
    )


def review_v1_candidate_known_limitations(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
) -> tuple[AGIcoreTradingV1KnownLimitation, ...]:
    payload = _coerce_input(data)
    documented = not (payload and payload.force_limitations_not_documented)
    return (
        AGIcoreTradingV1KnownLimitation("OFFLINE_SANDBOX_ONLY", "Candidate is limited to offline sandbox runs.", documented),
        AGIcoreTradingV1KnownLimitation("NO_LIVE_EXECUTION", "No broker connection or live order execution is supported.", documented),
        AGIcoreTradingV1KnownLimitation("NO_PROFITABILITY_PROOF", "Replay outcomes do not prove profitability.", documented),
        AGIcoreTradingV1KnownLimitation("IN_MEMORY_INPUTS_ONLY", "Inputs and reports remain in memory for this V1 candidate.", documented),
    )


def compute_agicore_trading_v1_candidate_review_metrics(
    capability_reviews: tuple[AGIcoreTradingV1CapabilityReview, ...],
    smoke_replay_review: AGIcoreTradingV1SmokeReplayReview | None,
    safety_boundary_review: AGIcoreTradingV1SafetyBoundaryReview | None,
    known_limitations: tuple[AGIcoreTradingV1KnownLimitation, ...],
    findings: tuple[AGIcoreTradingV1CandidateReviewFinding, ...],
    final_decision: str = "",
) -> AGIcoreTradingV1CandidateReviewMetrics:
    reviewed = len(capability_reviews)
    failed = sum(1 for review in capability_reviews if not review.passed)
    return AGIcoreTradingV1CandidateReviewMetrics(
        expected_capability_count=len(EXPECTED_CAPABILITIES),
        reviewed_capability_count=reviewed,
        failed_capability_count=failed,
        smoke_replay_passed=bool(smoke_replay_review and smoke_replay_review.passed),
        safety_boundaries_passed=bool(safety_boundary_review and safety_boundary_review.passed),
        known_limitations_count=len(known_limitations),
        findings_count=len(findings),
        global_score=100,
        final_decision=final_decision,
    )


def detect_agicore_trading_v1_candidate_review_risks(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
    candidate: AGIcoreTradingV1CandidateResult | None = None,
    capability_reviews: tuple[AGIcoreTradingV1CapabilityReview, ...] = (),
    smoke_replay_review: AGIcoreTradingV1SmokeReplayReview | None = None,
    safety_boundary_review: AGIcoreTradingV1SafetyBoundaryReview | None = None,
    product_readiness_review: AGIcoreTradingV1ProductReadinessReview | None = None,
    known_limitations: tuple[AGIcoreTradingV1KnownLimitation, ...] = (),
    findings: tuple[AGIcoreTradingV1CandidateReviewFinding, ...] = (),
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    source = candidate or (_candidate_result(payload) if payload else None)
    risks: list[Risk] = []
    if not payload or not source or payload.force_candidate_not_approved:
        risks.append(Risk.AGICORE_TRADING_V1_CANDIDATE_NOT_APPROVED)
    elif source.decision is not AGIcoreTradingV1CandidateDecision.APPROVE_AGICORE_TRADING_V1_CANDIDATE:
        risks.append(Risk.AGICORE_TRADING_V1_CANDIDATE_NOT_APPROVED)
    for finding in findings:
        if not finding.passed and finding.risk is not None:
            risks.append(finding.risk)
    for review in capability_reviews:
        capability = Capability(review.capability)
        if not review.passed:
            risks.append(_CAPABILITY_RISKS[capability])
    if smoke_replay_review is not None and not smoke_replay_review.passed:
        risks.append(Risk.V1_SMOKE_REPLAY_REVIEW_FAILED)
    if safety_boundary_review is not None:
        risks.extend(safety_boundary_review.risks)
    if product_readiness_review is not None and not product_readiness_review.passed:
        risks.append(Risk.V1_PRODUCT_READINESS_INCOMPLETE)
    if known_limitations and not all(limitation.documented for limitation in known_limitations):
        risks.append(Risk.V1_LIMITATIONS_NOT_DOCUMENTED)
    return _dedupe(risks)


def compute_agicore_trading_v1_candidate_review_score(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
    candidate: AGIcoreTradingV1CandidateResult | None = None,
    capability_reviews: tuple[AGIcoreTradingV1CapabilityReview, ...] = (),
    smoke_replay_review: AGIcoreTradingV1SmokeReplayReview | None = None,
    safety_boundary_review: AGIcoreTradingV1SafetyBoundaryReview | None = None,
    product_readiness_review: AGIcoreTradingV1ProductReadinessReview | None = None,
    known_limitations: tuple[AGIcoreTradingV1KnownLimitation, ...] = (),
    risks: tuple[Risk, ...] = (),
    report_present: bool = True,
) -> AGIcoreTradingV1CandidateReviewScore:
    payload = _coerce_input(data)
    source = candidate or (_candidate_result(payload) if payload else None)
    candidate_score = 100 if source and source.decision is AGIcoreTradingV1CandidateDecision.APPROVE_AGICORE_TRADING_V1_CANDIDATE else 0
    capability_score = 100 if len(capability_reviews) == len(EXPECTED_CAPABILITIES) and all(review.passed for review in capability_reviews) else 0
    smoke_score = 100 if smoke_replay_review and smoke_replay_review.passed else 0
    safety_score = 100 if safety_boundary_review and safety_boundary_review.passed else 0
    product_score = 100 if product_readiness_review and product_readiness_review.passed else 0
    limitations_score = 100 if known_limitations and all(limitation.documented for limitation in known_limitations) else 0
    claim_score = 100 if not ({Risk.LIVE_TRADING_READINESS_OVERCLAIM, Risk.PROFITABILITY_PROOF_MISSING} & set(risks)) else 0
    report_score = 100 if report_present else 0
    overall = min(
        candidate_score,
        capability_score,
        smoke_score,
        safety_score,
        product_score,
        limitations_score,
        claim_score,
        report_score,
    )
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1CandidateReviewScore(
        overall_score=overall,
        candidate_score=candidate_score,
        capability_score=capability_score,
        smoke_replay_score=smoke_score,
        safety_boundary_score=safety_score,
        product_readiness_score=product_score,
        limitations_score=limitations_score,
        claim_score=claim_score,
        report_score=report_score,
    )


def generate_agicore_trading_v1_candidate_review_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.AGICORE_TRADING_V1_CANDIDATE_NOT_APPROVED: Recommendation.FIX_AGICORE_TRADING_V1_CANDIDATE_APPROVAL,
        Risk.V1_CAPABILITY_COVERAGE_INCOMPLETE: Recommendation.COMPLETE_V1_CAPABILITY_COVERAGE,
        Risk.CSV_REPLAY_CAPABILITY_REVIEW_FAILED: Recommendation.FIX_CSV_REPLAY_CAPABILITY_REVIEW,
        Risk.SYNTHETIC_MARKET_CAPABILITY_REVIEW_FAILED: Recommendation.FIX_SYNTHETIC_MARKET_CAPABILITY_REVIEW,
        Risk.STRATEGY_REPLAY_CAPABILITY_REVIEW_FAILED: Recommendation.FIX_STRATEGY_REPLAY_CAPABILITY_REVIEW,
        Risk.SIMULATED_BROKER_CAPABILITY_REVIEW_FAILED: Recommendation.FIX_SIMULATED_BROKER_CAPABILITY_REVIEW,
        Risk.RISK_GUARD_CAPABILITY_REVIEW_FAILED: Recommendation.FIX_RISK_GUARD_CAPABILITY_REVIEW,
        Risk.JOURNAL_CAPABILITY_REVIEW_FAILED: Recommendation.FIX_JOURNAL_CAPABILITY_REVIEW,
        Risk.OFFLINE_REPORT_CAPABILITY_REVIEW_FAILED: Recommendation.FIX_OFFLINE_REPORT_CAPABILITY_REVIEW,
        Risk.V1_SMOKE_REPLAY_REVIEW_FAILED: Recommendation.FIX_V1_SMOKE_REPLAY_REVIEW,
        Risk.V1_PRODUCT_READINESS_INCOMPLETE: Recommendation.CLARIFY_OFFLINE_PRODUCT_READINESS,
        Risk.V1_LIMITATIONS_NOT_DOCUMENTED: Recommendation.DOCUMENT_V1_LIMITATIONS,
        Risk.LIVE_TRADING_READINESS_OVERCLAIM: Recommendation.REMOVE_LIVE_TRADING_READINESS_CLAIM,
        Risk.PROFITABILITY_PROOF_MISSING: Recommendation.REMOVE_PROFITABILITY_CLAIM,
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
        recommendations.append(Recommendation.PROCEED_TO_OFFLINE_RELEASE_DECISION)
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
    if isinstance(value, tuple):
        return [_payload_value(item) for item in value]
    if isinstance(value, list):
        return [_payload_value(item) for item in value]
    if hasattr(value, "__dict__"):
        return {key: _payload_value(item) for key, item in vars(value).items() if not key.startswith("_") and key != "candidate_result"}
    return str(value)


def render_agicore_trading_v1_candidate_review_markdown_report(
    result: AGIcoreTradingV1CandidateReviewResult | Mapping[str, Any],
) -> str:
    if not isinstance(result, AGIcoreTradingV1CandidateReviewResult):
        return "# AGIcore Trading v1 Candidate Review\n"
    lines = [
        "# AGIcore Trading v1 Candidate Review",
        "",
        f"- decision: {result.decision.value}",
        f"- state: {result.state.value}",
        f"- score: {result.score.overall_score}",
        "- product_scope: offline sandbox candidate only",
        "- live_trading_ready: false",
        "- profitability_proven: false",
        f"- risks: {', '.join(risk.value for risk in result.risks) if result.risks else 'none'}",
        "",
        "## Capability Review",
    ]
    for review in result.capability_reviews:
        lines.append(f"- {review.capability}: {'PASS' if review.passed else 'FAIL'} - {review.detail}")
    lines.extend(["", "## Known Limitations"])
    for limitation in result.known_limitations:
        lines.append(f"- {limitation.code}: {limitation.description}")
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


def render_agicore_trading_v1_candidate_review_json_report(
    result: AGIcoreTradingV1CandidateReviewResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1CandidateReviewResult):
        payload = {
            "schema": "agicore_trading_v1_candidate_review",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "capability_reviews": _payload_value(result.capability_reviews),
            "smoke_replay_review": _payload_value(result.smoke_replay_review),
            "safety_boundary_review": _payload_value(result.safety_boundary_review),
            "product_readiness_review": _payload_value(result.product_readiness_review),
            "known_limitations": _payload_value(result.known_limitations),
            "metrics": _payload_value(result.metrics),
            "live_trading_ready": False,
            "profitability_proven": False,
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


def assert_agicore_trading_v1_candidate_review_offline_boundaries(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return not _input_boundary_risks(payload)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_CANDIDATE_REVIEW
    if any(risk in _BOUNDARY_RISKS for risk in risks):
        return Decision.REQUIRE_V1_SAFETY_BOUNDARY_FIXES
    if Risk.AGICORE_TRADING_V1_CANDIDATE_NOT_APPROVED in risks:
        return Decision.REQUIRE_AGICORE_TRADING_V1_CANDIDATE_FIXES
    capability_risks = {Risk.V1_CAPABILITY_COVERAGE_INCOMPLETE, *_CAPABILITY_RISKS.values()}
    if any(risk in capability_risks for risk in risks):
        return Decision.REQUIRE_V1_CAPABILITY_COVERAGE_FIXES
    if Risk.V1_SMOKE_REPLAY_REVIEW_FAILED in risks:
        return Decision.REQUIRE_V1_SMOKE_REPLAY_FIXES
    if Risk.V1_LIMITATIONS_NOT_DOCUMENTED in risks:
        return Decision.REQUIRE_V1_LIMITATION_DOCUMENTATION_FIXES
    if {
        Risk.V1_PRODUCT_READINESS_INCOMPLETE,
        Risk.LIVE_TRADING_READINESS_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_MISSING,
    } & set(risks):
        return Decision.REQUIRE_V1_PRODUCT_READINESS_FIXES
    return Decision.BLOCK_AGICORE_TRADING_V1_CANDIDATE_REVIEW


def _state_for(data: AGIcoreTradingV1CandidateReviewInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_CANDIDATE_REVIEW_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_CANDIDATE_REVIEW:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION
    return State.AGICORE_TRADING_V1_CANDIDATE_REVIEW_BLOCKED


def review_agicore_trading_v1_candidate(
    data: AGIcoreTradingV1CandidateReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1CandidateReviewResult:
    payload = _coerce_input(data)
    candidate = _candidate_result(payload) if payload else None
    coverage = review_v1_candidate_capability_coverage(payload, candidate)
    capability_reviews = (
        review_v1_candidate_csv_replay_capability(payload, candidate),
        review_v1_candidate_synthetic_market_capability(payload, candidate),
        review_v1_candidate_strategy_replay_capability(payload, candidate),
        review_v1_candidate_simulated_broker_capability(payload, candidate),
        review_v1_candidate_risk_guard_capability(payload, candidate),
        review_v1_candidate_journal_capability(payload, candidate),
        review_v1_candidate_offline_report_capability(payload, candidate),
    ) if payload else ()
    smoke_review = review_v1_candidate_smoke_replay(payload, candidate) if payload else None
    safety_review = review_v1_candidate_safety_boundaries(payload, candidate) if payload else None
    live_claim = review_v1_candidate_no_live_trading_claim(payload)
    profit_claim = review_v1_candidate_no_profitability_claim(payload)
    product_readiness = review_v1_candidate_product_readiness(payload) if payload else None
    known_limitations = review_v1_candidate_known_limitations(payload) if payload else ()
    findings = (coverage, live_claim, profit_claim)
    risks = detect_agicore_trading_v1_candidate_review_risks(
        payload,
        candidate,
        capability_reviews,
        smoke_review,
        safety_review,
        product_readiness,
        known_limitations,
        findings,
    )
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_candidate_review_score(
        payload,
        candidate,
        capability_reviews,
        smoke_review,
        safety_review,
        product_readiness,
        known_limitations,
        risks,
        report_present=not (payload and payload.force_report_missing),
    )
    metrics = compute_agicore_trading_v1_candidate_review_metrics(
        capability_reviews,
        smoke_review,
        safety_review,
        known_limitations,
        findings,
        decision.value,
    )
    metrics = AGIcoreTradingV1CandidateReviewMetrics(
        expected_capability_count=metrics.expected_capability_count,
        reviewed_capability_count=metrics.reviewed_capability_count,
        failed_capability_count=metrics.failed_capability_count,
        smoke_replay_passed=metrics.smoke_replay_passed,
        safety_boundaries_passed=metrics.safety_boundaries_passed,
        known_limitations_count=metrics.known_limitations_count,
        findings_count=metrics.findings_count,
        global_score=score.overall_score,
        final_decision=decision.value,
    )
    recommendations = generate_agicore_trading_v1_candidate_review_recommendations(risks)
    base_result = AGIcoreTradingV1CandidateReviewResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        findings=findings,
        capability_reviews=capability_reviews,
        smoke_replay_review=smoke_review,
        safety_boundary_review=safety_review,
        product_readiness_review=product_readiness,
        known_limitations=known_limitations,
        metrics=metrics,
        report=None,
        candidate_result=candidate,
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
    if not (payload and payload.force_report_missing):
        report = AGIcoreTradingV1CandidateReviewReport(
            markdown=render_agicore_trading_v1_candidate_review_markdown_report(base_result),
            json=render_agicore_trading_v1_candidate_review_json_report(base_result),
        )
    return AGIcoreTradingV1CandidateReviewResult(**{**base_result.__dict__, "report": report})
