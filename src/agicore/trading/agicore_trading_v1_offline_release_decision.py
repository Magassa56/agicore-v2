"""AGIcore Trading v1 offline release decision."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_candidate_review import review_agicore_trading_v1_candidate
from agicore.trading.agicore_trading_v1_candidate_review_models import (
    AGIcoreTradingV1CandidateReviewDecision,
    AGIcoreTradingV1CandidateReviewInput,
    AGIcoreTradingV1CandidateReviewResult,
)
from agicore.trading.agicore_trading_v1_offline_release_decision_models import (
    AGIcoreTradingV1OfflineReleaseCapabilityReadiness,
    AGIcoreTradingV1OfflineReleaseDecisionDecision,
    AGIcoreTradingV1OfflineReleaseDecisionInput,
    AGIcoreTradingV1OfflineReleaseDecisionMetrics,
    AGIcoreTradingV1OfflineReleaseDecisionRecommendation,
    AGIcoreTradingV1OfflineReleaseDecisionReport,
    AGIcoreTradingV1OfflineReleaseDecisionResult,
    AGIcoreTradingV1OfflineReleaseDecisionRisk,
    AGIcoreTradingV1OfflineReleaseDecisionScore,
    AGIcoreTradingV1OfflineReleaseDecisionState,
    AGIcoreTradingV1OfflineReleaseDecisionSummary,
    AGIcoreTradingV1OfflineReleaseKnownLimitation,
    AGIcoreTradingV1OfflineReleaseNonGoal,
    AGIcoreTradingV1OfflineReleaseProductReadiness,
    AGIcoreTradingV1OfflineReleaseSafetyBoundary,
    AGIcoreTradingV1OfflineReleaseScope,
    AGIcoreTradingV1OfflineReleaseTestingEvidence,
)


Risk = AGIcoreTradingV1OfflineReleaseDecisionRisk
Recommendation = AGIcoreTradingV1OfflineReleaseDecisionRecommendation
Decision = AGIcoreTradingV1OfflineReleaseDecisionDecision
State = AGIcoreTradingV1OfflineReleaseDecisionState

EXPECTED_CAPABILITIES = (
    "CSV_REPLAY_INPUT",
    "SYNTHETIC_MARKET_SCENARIO",
    "STRATEGY_REPLAY_ENGINE",
    "SIMULATED_BROKER_STUB",
    "RISK_GUARD_ENFORCEMENT",
    "JOURNAL_WRITER",
    "OFFLINE_REPORT_MARKDOWN_JSON",
    "V1_CANDIDATE_REVIEW",
)

REQUIRED_NON_GOALS = (
    "NOT_READY_FOR_LIVE_TRADING",
    "NOT_READY_FOR_REAL_BROKER",
    "NOT_READY_FOR_REAL_ORDERS",
    "NOT_PROFITABILITY_PROVEN",
    "NOT_FINANCIAL_ADVICE",
    "NOT_PAPER_BROKER_CONNECTED",
    "NO_REAL_MARKET_DATA_AUTOMATION",
)

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


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    out: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return tuple(out)


def _coerce_input(
    data: AGIcoreTradingV1OfflineReleaseDecisionInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineReleaseDecisionInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineReleaseDecisionInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineReleaseDecisionInput)}
    return AGIcoreTradingV1OfflineReleaseDecisionInput(**{key: value for key, value in dict(data).items() if key in allowed})


def _review_result(data: AGIcoreTradingV1OfflineReleaseDecisionInput) -> AGIcoreTradingV1CandidateReviewResult | None:
    if data.candidate_review_result is not None:
        return data.candidate_review_result
    if data.candidate_review_input is not None:
        return review_agicore_trading_v1_candidate(data.candidate_review_input)
    return None


def validate_agicore_trading_v1_offline_release_decision_input(
    data: AGIcoreTradingV1OfflineReleaseDecisionInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and (payload.candidate_review_result is not None or payload.candidate_review_input is not None))


def validate_v1_candidate_review_approval(
    data: AGIcoreTradingV1OfflineReleaseDecisionInput | Mapping[str, Any] | None,
    review: AGIcoreTradingV1CandidateReviewResult | None = None,
) -> bool:
    payload = _coerce_input(data)
    source = review or (_review_result(payload) if payload else None)
    return bool(
        payload
        and source
        and not payload.force_candidate_review_not_approved
        and source.decision is AGIcoreTradingV1CandidateReviewDecision.APPROVE_AGICORE_TRADING_V1_CANDIDATE_REVIEW
        and not source.risks
    )


def evaluate_offline_release_scope(
    data: AGIcoreTradingV1OfflineReleaseDecisionInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineReleaseScope:
    payload = _coerce_input(data)
    valid = bool(payload and not payload.force_scope_invalid)
    return AGIcoreTradingV1OfflineReleaseScope(
        name="AGIcore Trading v1 offline sandbox release",
        offline_only=True,
        sandbox_only=True,
        in_memory_decision_only=True,
        valid=valid,
    )


def evaluate_offline_release_capability_readiness(
    data: AGIcoreTradingV1OfflineReleaseDecisionInput | Mapping[str, Any] | None,
    review: AGIcoreTradingV1CandidateReviewResult | None = None,
) -> AGIcoreTradingV1OfflineReleaseCapabilityReadiness:
    payload = _coerce_input(data)
    source = review or (_review_result(payload) if payload else None)
    confirmed = []
    if source:
        confirmed.extend(review.capability for review in source.capability_reviews if review.passed)
        if source.decision is AGIcoreTradingV1CandidateReviewDecision.APPROVE_AGICORE_TRADING_V1_CANDIDATE_REVIEW:
            confirmed.append("V1_CANDIDATE_REVIEW")
    if payload and payload.force_capability_incomplete and confirmed:
        confirmed = confirmed[:-1]
    confirmed_tuple = tuple(item for item in EXPECTED_CAPABILITIES if item in set(confirmed))
    missing = tuple(item for item in EXPECTED_CAPABILITIES if item not in set(confirmed_tuple))
    return AGIcoreTradingV1OfflineReleaseCapabilityReadiness(
        expected_capabilities=EXPECTED_CAPABILITIES,
        confirmed_capabilities=confirmed_tuple,
        missing_capabilities=missing,
        ready=not missing,
    )


def _input_boundary_flags(data: AGIcoreTradingV1OfflineReleaseDecisionInput | None) -> tuple[Risk, ...]:
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


def evaluate_offline_release_safety_boundaries(
    data: AGIcoreTradingV1OfflineReleaseDecisionInput | Mapping[str, Any] | None,
    review: AGIcoreTradingV1CandidateReviewResult | None = None,
) -> AGIcoreTradingV1OfflineReleaseSafetyBoundary:
    payload = _coerce_input(data)
    source = review or (_review_result(payload) if payload else None)
    forced = bool(payload and payload.force_safety_boundary_incomplete)
    flags = set(_input_boundary_flags(payload))
    passed = bool(source and not source.risks and not flags and not forced)
    return AGIcoreTradingV1OfflineReleaseSafetyBoundary(
        passed=passed,
        file_read=Risk.FILE_READ_BOUNDARY_VIOLATION in flags or bool(source and source.file_read),
        file_written=Risk.FILE_WRITE_BOUNDARY_VIOLATION in flags or bool(source and source.file_written),
        data_accessed=Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION in flags or Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION in flags or bool(source and source.data_accessed),
        real_broker_accessed=Risk.REAL_BROKER_BOUNDARY_VIOLATION in flags,
        real_secret_read=Risk.REAL_SECRET_BOUNDARY_VIOLATION in flags,
        network_used=Risk.NETWORK_BOUNDARY_VIOLATION in flags,
        real_order_submitted=Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION in flags or bool(source and source.real_order_submitted),
        real_account_accessed=Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION in flags or bool(source and source.real_account_accessed),
        position_mutated=Risk.POSITION_MUTATION_BOUNDARY_VIOLATION in flags or bool(source and source.position_mutated),
    )


def evaluate_offline_release_testing_evidence(
    data: AGIcoreTradingV1OfflineReleaseDecisionInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineReleaseTestingEvidence:
    payload = _coerce_input(data)
    complete = bool(
        payload
        and payload.targeted_tests_passed
        and payload.trading_tests_passed
        and payload.unit_tests_passed
        and payload.diff_check_passed
        and not payload.force_testing_evidence_missing
    )
    return AGIcoreTradingV1OfflineReleaseTestingEvidence(
        targeted_tests_passed=bool(payload and payload.targeted_tests_passed),
        trading_tests_passed=bool(payload and payload.trading_tests_passed),
        unit_tests_passed=bool(payload and payload.unit_tests_passed),
        diff_check_passed=bool(payload and payload.diff_check_passed),
        complete=complete,
    )


def evaluate_offline_release_known_limitations(
    data: AGIcoreTradingV1OfflineReleaseDecisionInput | Mapping[str, Any] | None,
    review: AGIcoreTradingV1CandidateReviewResult | None = None,
) -> tuple[AGIcoreTradingV1OfflineReleaseKnownLimitation, ...]:
    payload = _coerce_input(data)
    if payload and payload.force_limitations_missing:
        return ()
    source = review or (_review_result(payload) if payload else None)
    limitations = [
        AGIcoreTradingV1OfflineReleaseKnownLimitation("OFFLINE_SANDBOX_ONLY", "Release is offline and sandbox only."),
        AGIcoreTradingV1OfflineReleaseKnownLimitation("NO_LIVE_TRADING", "Release is not ready for live trading."),
        AGIcoreTradingV1OfflineReleaseKnownLimitation("NO_PROFITABILITY_PROOF", "Release does not prove profitability."),
        AGIcoreTradingV1OfflineReleaseKnownLimitation("NO_REAL_BROKER", "Release does not connect a real broker."),
    ]
    if source:
        for limitation in source.known_limitations:
            if limitation.code not in {item.code for item in limitations}:
                limitations.append(AGIcoreTradingV1OfflineReleaseKnownLimitation(limitation.code, limitation.description, limitation.documented))
    return tuple(limitations)


def evaluate_offline_release_non_goals(
    data: AGIcoreTradingV1OfflineReleaseDecisionInput | Mapping[str, Any] | None,
) -> tuple[AGIcoreTradingV1OfflineReleaseNonGoal, ...]:
    payload = _coerce_input(data)
    if payload and payload.force_non_goals_missing:
        return ()
    descriptions = {
        "NOT_READY_FOR_LIVE_TRADING": "No live trading readiness is claimed.",
        "NOT_READY_FOR_REAL_BROKER": "No real broker readiness is claimed.",
        "NOT_READY_FOR_REAL_ORDERS": "No real order execution is claimed.",
        "NOT_PROFITABILITY_PROVEN": "No profitability proof is claimed.",
        "NOT_FINANCIAL_ADVICE": "No financial advice is provided.",
        "NOT_PAPER_BROKER_CONNECTED": "No paper broker connection is part of this release.",
        "NO_REAL_MARKET_DATA_AUTOMATION": "No real market data automation is part of this release.",
    }
    return tuple(AGIcoreTradingV1OfflineReleaseNonGoal(code, descriptions[code]) for code in REQUIRED_NON_GOALS)


def evaluate_offline_release_no_live_trading_claim(data: AGIcoreTradingV1OfflineReleaseDecisionInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return not (payload and payload.force_live_trading_readiness_overclaim)


def evaluate_offline_release_no_profitability_claim(data: AGIcoreTradingV1OfflineReleaseDecisionInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return not (payload and payload.force_profitability_proof_overclaim)


def evaluate_offline_release_product_readiness(
    data: AGIcoreTradingV1OfflineReleaseDecisionInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineReleaseProductReadiness:
    payload = _coerce_input(data)
    live_ready = bool(payload and payload.force_live_trading_readiness_overclaim)
    broker_ready = bool(payload and payload.force_real_broker_readiness_overclaim)
    orders_ready = bool(payload and payload.force_real_order_execution_overclaim)
    profit_proven = bool(payload and payload.force_profitability_proof_overclaim)
    advice = bool(payload and payload.force_financial_advice_overclaim)
    approved = not (live_ready or broker_ready or orders_ready or profit_proven or advice)
    return AGIcoreTradingV1OfflineReleaseProductReadiness(
        release_label="AGIcore Trading v1 offline sandbox release",
        offline_release_approved=approved,
        live_trading_ready=live_ready,
        real_broker_ready=broker_ready,
        real_orders_ready=orders_ready,
        profitability_proven=profit_proven,
        financial_advice=advice,
    )


def build_offline_release_decision_summary(
    decision: Decision,
) -> AGIcoreTradingV1OfflineReleaseDecisionSummary:
    return AGIcoreTradingV1OfflineReleaseDecisionSummary(
        decision=decision.value,
        release_label="AGIcore Trading v1 offline sandbox release",
        summary="Offline/sandbox release decision only; no real trading readiness or profitability proof is claimed.",
        next_phase="AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES",
    )


def compute_agicore_trading_v1_offline_release_decision_metrics(
    capability_readiness: AGIcoreTradingV1OfflineReleaseCapabilityReadiness,
    known_limitations: tuple[AGIcoreTradingV1OfflineReleaseKnownLimitation, ...],
    non_goals: tuple[AGIcoreTradingV1OfflineReleaseNonGoal, ...],
    testing_evidence: AGIcoreTradingV1OfflineReleaseTestingEvidence,
    final_decision: str = "",
    global_score: int = 100,
) -> AGIcoreTradingV1OfflineReleaseDecisionMetrics:
    return AGIcoreTradingV1OfflineReleaseDecisionMetrics(
        expected_capability_count=len(capability_readiness.expected_capabilities),
        confirmed_capability_count=len(capability_readiness.confirmed_capabilities),
        missing_capability_count=len(capability_readiness.missing_capabilities),
        limitation_count=len(known_limitations),
        non_goal_count=len(non_goals),
        testing_evidence_complete=testing_evidence.complete,
        global_score=global_score,
        final_decision=final_decision,
    )


def detect_agicore_trading_v1_offline_release_decision_risks(
    data: AGIcoreTradingV1OfflineReleaseDecisionInput | Mapping[str, Any] | None,
    review: AGIcoreTradingV1CandidateReviewResult | None = None,
    scope: AGIcoreTradingV1OfflineReleaseScope | None = None,
    capability_readiness: AGIcoreTradingV1OfflineReleaseCapabilityReadiness | None = None,
    safety_boundary: AGIcoreTradingV1OfflineReleaseSafetyBoundary | None = None,
    testing_evidence: AGIcoreTradingV1OfflineReleaseTestingEvidence | None = None,
    known_limitations: tuple[AGIcoreTradingV1OfflineReleaseKnownLimitation, ...] = (),
    non_goals: tuple[AGIcoreTradingV1OfflineReleaseNonGoal, ...] = (),
    product_readiness: AGIcoreTradingV1OfflineReleaseProductReadiness | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    source = review or (_review_result(payload) if payload else None)
    risks: list[Risk] = []
    if not payload or not source or not validate_v1_candidate_review_approval(payload, source):
        risks.append(Risk.V1_CANDIDATE_REVIEW_NOT_APPROVED)
    if scope is not None and not scope.valid:
        risks.append(Risk.OFFLINE_RELEASE_SCOPE_INVALID)
    if capability_readiness is not None and not capability_readiness.ready:
        risks.append(Risk.OFFLINE_RELEASE_CAPABILITY_INCOMPLETE)
    if safety_boundary is not None and not safety_boundary.passed:
        risks.append(Risk.OFFLINE_RELEASE_SAFETY_BOUNDARY_INCOMPLETE)
    if testing_evidence is not None and not testing_evidence.complete:
        risks.append(Risk.OFFLINE_RELEASE_TESTING_EVIDENCE_MISSING)
    if not known_limitations or not all(item.documented for item in known_limitations):
        risks.append(Risk.OFFLINE_RELEASE_LIMITATIONS_MISSING)
    if {item.code for item in non_goals} != set(REQUIRED_NON_GOALS):
        risks.append(Risk.OFFLINE_RELEASE_NON_GOALS_MISSING)
    if product_readiness:
        if product_readiness.live_trading_ready:
            risks.append(Risk.LIVE_TRADING_READINESS_OVERCLAIM)
        if product_readiness.real_broker_ready:
            risks.append(Risk.REAL_BROKER_READINESS_OVERCLAIM)
        if product_readiness.real_orders_ready:
            risks.append(Risk.REAL_ORDER_EXECUTION_OVERCLAIM)
        if product_readiness.profitability_proven:
            risks.append(Risk.PROFITABILITY_PROOF_OVERCLAIM)
        if product_readiness.financial_advice:
            risks.append(Risk.FINANCIAL_ADVICE_OVERCLAIM)
    risks.extend(_input_boundary_flags(payload))
    return _dedupe(risks)


def compute_agicore_trading_v1_offline_release_decision_score(
    data: AGIcoreTradingV1OfflineReleaseDecisionInput | Mapping[str, Any] | None,
    review: AGIcoreTradingV1CandidateReviewResult | None = None,
    scope: AGIcoreTradingV1OfflineReleaseScope | None = None,
    capability_readiness: AGIcoreTradingV1OfflineReleaseCapabilityReadiness | None = None,
    safety_boundary: AGIcoreTradingV1OfflineReleaseSafetyBoundary | None = None,
    testing_evidence: AGIcoreTradingV1OfflineReleaseTestingEvidence | None = None,
    known_limitations: tuple[AGIcoreTradingV1OfflineReleaseKnownLimitation, ...] = (),
    non_goals: tuple[AGIcoreTradingV1OfflineReleaseNonGoal, ...] = (),
    product_readiness: AGIcoreTradingV1OfflineReleaseProductReadiness | None = None,
    risks: tuple[Risk, ...] = (),
    report_present: bool = True,
) -> AGIcoreTradingV1OfflineReleaseDecisionScore:
    payload = _coerce_input(data)
    source = review or (_review_result(payload) if payload else None)
    review_score = 100 if source and validate_v1_candidate_review_approval(payload, source) else 0
    scope_score = 100 if scope and scope.valid else 0
    capability_score = 100 if capability_readiness and capability_readiness.ready else 0
    safety_score = 100 if safety_boundary and safety_boundary.passed else 0
    testing_score = 100 if testing_evidence and testing_evidence.complete else 0
    limitation_score = 100 if known_limitations and all(item.documented for item in known_limitations) else 0
    non_goal_score = 100 if {item.code for item in non_goals} == set(REQUIRED_NON_GOALS) else 0
    product_score = 100 if product_readiness and product_readiness.offline_release_approved else 0
    report_score = 100 if report_present else 0
    overall = min(
        review_score,
        scope_score,
        capability_score,
        safety_score,
        testing_score,
        limitation_score,
        non_goal_score,
        product_score,
        report_score,
    )
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineReleaseDecisionScore(
        overall_score=overall,
        review_score=review_score,
        scope_score=scope_score,
        capability_score=capability_score,
        safety_score=safety_score,
        testing_score=testing_score,
        limitation_score=limitation_score,
        non_goal_score=non_goal_score,
        product_score=product_score,
        report_score=report_score,
    )


def generate_agicore_trading_v1_offline_release_decision_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.V1_CANDIDATE_REVIEW_NOT_APPROVED: Recommendation.FIX_V1_CANDIDATE_REVIEW_APPROVAL,
        Risk.OFFLINE_RELEASE_SCOPE_INVALID: Recommendation.CLARIFY_OFFLINE_RELEASE_SCOPE,
        Risk.OFFLINE_RELEASE_CAPABILITY_INCOMPLETE: Recommendation.COMPLETE_OFFLINE_RELEASE_CAPABILITIES,
        Risk.OFFLINE_RELEASE_SAFETY_BOUNDARY_INCOMPLETE: Recommendation.FIX_OFFLINE_RELEASE_SAFETY_BOUNDARIES,
        Risk.OFFLINE_RELEASE_TESTING_EVIDENCE_MISSING: Recommendation.PROVIDE_OFFLINE_RELEASE_TESTING_EVIDENCE,
        Risk.OFFLINE_RELEASE_LIMITATIONS_MISSING: Recommendation.DOCUMENT_OFFLINE_RELEASE_LIMITATIONS,
        Risk.OFFLINE_RELEASE_NON_GOALS_MISSING: Recommendation.DOCUMENT_OFFLINE_RELEASE_NON_GOALS,
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
        recommendations.append(Recommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION
    if any(risk in _BOUNDARY_RISKS for risk in risks):
        return Decision.REQUIRE_OFFLINE_RELEASE_SAFETY_FIXES
    if Risk.V1_CANDIDATE_REVIEW_NOT_APPROVED in risks:
        return Decision.REQUIRE_V1_CANDIDATE_REVIEW_FIXES
    if Risk.OFFLINE_RELEASE_SCOPE_INVALID in risks:
        return Decision.REQUIRE_OFFLINE_RELEASE_SCOPE_FIXES
    if Risk.OFFLINE_RELEASE_CAPABILITY_INCOMPLETE in risks:
        return Decision.REQUIRE_OFFLINE_RELEASE_CAPABILITY_FIXES
    if Risk.OFFLINE_RELEASE_SAFETY_BOUNDARY_INCOMPLETE in risks:
        return Decision.REQUIRE_OFFLINE_RELEASE_SAFETY_FIXES
    if Risk.OFFLINE_RELEASE_TESTING_EVIDENCE_MISSING in risks:
        return Decision.REQUIRE_OFFLINE_RELEASE_TESTING_EVIDENCE_FIXES
    if Risk.OFFLINE_RELEASE_LIMITATIONS_MISSING in risks:
        return Decision.REQUIRE_OFFLINE_RELEASE_LIMITATION_FIXES
    if Risk.OFFLINE_RELEASE_NON_GOALS_MISSING in risks:
        return Decision.REQUIRE_OFFLINE_RELEASE_NON_GOAL_FIXES
    overclaims = {
        Risk.LIVE_TRADING_READINESS_OVERCLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM,
    }
    if set(risks) & overclaims:
        return Decision.REQUIRE_OFFLINE_RELEASE_NON_GOAL_FIXES
    return Decision.BLOCK_AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION


def _state_for(data: AGIcoreTradingV1OfflineReleaseDecisionInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES
    return State.AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION_BLOCKED


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
        return {key: _payload_value(item) for key, item in vars(value).items() if not key.startswith("_") and key != "candidate_review_result"}
    return str(value)


def render_agicore_trading_v1_offline_release_decision_markdown_report(
    result: AGIcoreTradingV1OfflineReleaseDecisionResult | Mapping[str, Any],
) -> str:
    if not isinstance(result, AGIcoreTradingV1OfflineReleaseDecisionResult):
        return "# AGIcore Trading v1 Offline Release Decision\n"
    lines = [
        "# AGIcore Trading v1 Offline Release Decision",
        "",
        f"- decision: {result.decision.value}",
        f"- state: {result.state.value}",
        f"- score: {result.score.overall_score}",
        "- release_scope: offline sandbox only",
        "- live_trading_ready: false",
        "- real_broker_ready: false",
        "- real_orders_ready: false",
        "- profitability_proven: false",
        "- financial_advice: false",
        f"- risks: {', '.join(risk.value for risk in result.risks) if result.risks else 'none'}",
        "",
        "## Confirmed Capabilities",
    ]
    if result.capability_readiness:
        for capability in result.capability_readiness.confirmed_capabilities:
            lines.append(f"- {capability}")
    lines.extend(["", "## Known Limitations"])
    for limitation in result.known_limitations:
        lines.append(f"- {limitation.code}: {limitation.description}")
    lines.extend(["", "## Non Goals"])
    for non_goal in result.non_goals:
        lines.append(f"- {non_goal.code}: {non_goal.description}")
    return "\n".join(lines) + "\n"


def render_agicore_trading_v1_offline_release_decision_json_report(
    result: AGIcoreTradingV1OfflineReleaseDecisionResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineReleaseDecisionResult):
        payload = {
            "schema": "agicore_trading_v1_offline_release_decision",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "scope": _payload_value(result.scope),
            "capability_readiness": _payload_value(result.capability_readiness),
            "safety_boundary": _payload_value(result.safety_boundary),
            "testing_evidence": _payload_value(result.testing_evidence),
            "known_limitations": _payload_value(result.known_limitations),
            "non_goals": _payload_value(result.non_goals),
            "product_readiness": _payload_value(result.product_readiness),
            "summary": _payload_value(result.summary),
            "metrics": _payload_value(result.metrics),
            "live_trading_ready": False,
            "real_broker_ready": False,
            "real_orders_ready": False,
            "profitability_proven": False,
            "financial_advice": False,
        }
    else:
        payload = dict(result)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def assert_agicore_trading_v1_offline_release_decision_boundaries(
    data: AGIcoreTradingV1OfflineReleaseDecisionInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return not _input_boundary_flags(payload)


def evaluate_agicore_trading_v1_offline_release_decision(
    data: AGIcoreTradingV1OfflineReleaseDecisionInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineReleaseDecisionResult:
    payload = _coerce_input(data)
    review = _review_result(payload) if payload else None
    scope = evaluate_offline_release_scope(payload)
    capability = evaluate_offline_release_capability_readiness(payload, review)
    safety = evaluate_offline_release_safety_boundaries(payload, review)
    testing = evaluate_offline_release_testing_evidence(payload)
    limitations = evaluate_offline_release_known_limitations(payload, review)
    non_goals = evaluate_offline_release_non_goals(payload)
    product = evaluate_offline_release_product_readiness(payload)
    risks = detect_agicore_trading_v1_offline_release_decision_risks(
        payload,
        review,
        scope,
        capability,
        safety,
        testing,
        limitations,
        non_goals,
        product,
    )
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_release_decision_score(
        payload,
        review,
        scope,
        capability,
        safety,
        testing,
        limitations,
        non_goals,
        product,
        risks,
        report_present=not (payload and payload.force_report_missing),
    )
    summary = build_offline_release_decision_summary(decision)
    metrics = compute_agicore_trading_v1_offline_release_decision_metrics(
        capability,
        limitations,
        non_goals,
        testing,
        decision.value,
        score.overall_score,
    )
    recommendations = generate_agicore_trading_v1_offline_release_decision_recommendations(risks)
    base = AGIcoreTradingV1OfflineReleaseDecisionResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        scope=scope,
        capability_readiness=capability,
        safety_boundary=safety,
        testing_evidence=testing,
        known_limitations=limitations,
        non_goals=non_goals,
        product_readiness=product,
        summary=summary,
        metrics=metrics,
        report=None,
        candidate_review_result=review,
    )
    report = None
    if not (payload and payload.force_report_missing):
        report = AGIcoreTradingV1OfflineReleaseDecisionReport(
            markdown=render_agicore_trading_v1_offline_release_decision_markdown_report(base),
            json=render_agicore_trading_v1_offline_release_decision_json_report(base),
        )
    return AGIcoreTradingV1OfflineReleaseDecisionResult(**{**base.__dict__, "report": report})
