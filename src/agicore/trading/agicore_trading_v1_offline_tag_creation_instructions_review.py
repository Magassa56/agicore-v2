"""AGIcore Trading v1 offline tag creation instructions review."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_tag_creation_instructions_review_models import (
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewCommand,
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewContext,
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewCriterion,
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision,
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewFinding,
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewGuardrail,
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput,
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewRecommendation,
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewReport,
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewResult,
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk,
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewScore,
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewState,
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewTagMetadata,
)


Risk = AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk
Recommendation = AGIcoreTradingV1OfflineTagCreationInstructionsReviewRecommendation
Decision = AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision
State = AGIcoreTradingV1OfflineTagCreationInstructionsReviewState

EXPECTED_INSTRUCTIONS_DECISION = "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS"
EXPECTED_TAG_NAME = "agicore-trading-v1-offline"
EXPECTED_VERSION = "v1.0.0-offline"

PRE_CHECKS = (
    "git switch main",
    "git fetch origin",
    "git pull origin main",
    "python -m pytest tests/unit/ -q",
    "git status --short",
    "resultat attendu : seulement ?? data/",
)

DOCUMENTED_COMMANDS = (
    "git tag -a agicore-trading-v1-offline -m \"AGIcore Trading v1 Offline - sandbox release\"",
    "git push origin agicore-trading-v1-offline",
)

POST_CHECKS = (
    "git tag --list agicore-trading-v1-offline",
    "git ls-remote --tags origin agicore-trading-v1-offline",
    "git status --short",
)

HUMAN_GUARDRAILS = (
    "tests verts",
    "main synchronise",
    "status propre hors data/",
    "aucun fichier en staging",
    "validation explicite de Bama",
    "confirmation que la release reste offline/sandbox uniquement",
)

CRITERIA = (
    "instructions de tag existent",
    "decision prealable correcte",
    "tag propose coherent",
    "version proposee coherente",
    "pre-checks presents",
    "commandes documentees uniquement",
    "post-checks presents",
    "garde-fous humains presents",
    "aucun tag Git cree",
    "aucun tag Git pousse",
    "no-overclaim valide",
)


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    output: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            output.append(item)
    return tuple(output)


def _coerce_input(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput)}
    return AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput(
        **{key: value for key, value in dict(data).items() if key in allowed}
    )


def validate_agicore_trading_v1_offline_tag_creation_instructions_review_input(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(
        payload
        and payload.review_id
        and review_tag_creation_no_git_tag_created(payload)
        and review_tag_creation_no_git_tag_pushed(payload)
        and assert_agicore_trading_v1_offline_tag_creation_instructions_review_boundaries(payload)
    )


def build_tag_creation_instructions_review_context(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineTagCreationInstructionsReviewContext | None:
    payload = _coerce_input(data)
    if payload is None:
        return None
    pre_checks = PRE_CHECKS if payload.pre_checks_present else ()
    post_checks = POST_CHECKS if payload.post_checks_present else ()
    commands = tuple(
        AGIcoreTradingV1OfflineTagCreationInstructionsReviewCommand(command, payload.commands_documentation_only)
        for command in DOCUMENTED_COMMANDS
    )
    guardrails = tuple(
        AGIcoreTradingV1OfflineTagCreationInstructionsReviewGuardrail(name, payload.human_guardrails_present)
        for name in HUMAN_GUARDRAILS
    )
    criteria = tuple(AGIcoreTradingV1OfflineTagCreationInstructionsReviewCriterion(name, True) for name in CRITERIA)
    return AGIcoreTradingV1OfflineTagCreationInstructionsReviewContext(
        review_id=payload.review_id,
        prerequisite_decision=EXPECTED_INSTRUCTIONS_DECISION,
        tag_metadata=AGIcoreTradingV1OfflineTagCreationInstructionsReviewTagMetadata(
            tag_name=payload.tag_name,
            version=payload.version,
        ),
        pre_checks=pre_checks,
        commands=commands,
        post_checks=post_checks,
        guardrails=guardrails,
        criteria=criteria,
    )


def review_tag_creation_instructions_approval(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.instructions_approved)


def review_tag_creation_instructions_document(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.instructions_document_present)


def review_tag_creation_instructions_tag_name(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.tag_name == EXPECTED_TAG_NAME)


def review_tag_creation_instructions_version(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.version == EXPECTED_VERSION)


def review_tag_creation_pre_checks(context: AGIcoreTradingV1OfflineTagCreationInstructionsReviewContext | None) -> bool:
    return bool(context and len(context.pre_checks) == len(PRE_CHECKS))


def review_tag_creation_documented_commands_only(
    context: AGIcoreTradingV1OfflineTagCreationInstructionsReviewContext | None,
) -> bool:
    return bool(context and len(context.commands) == len(DOCUMENTED_COMMANDS) and all(command.documentation_only for command in context.commands))


def review_tag_creation_post_checks(context: AGIcoreTradingV1OfflineTagCreationInstructionsReviewContext | None) -> bool:
    return bool(context and len(context.post_checks) == len(POST_CHECKS))


def review_tag_creation_human_guardrails(
    context: AGIcoreTradingV1OfflineTagCreationInstructionsReviewContext | None,
) -> bool:
    return bool(context and len(context.guardrails) == len(HUMAN_GUARDRAILS) and all(guardrail.present for guardrail in context.guardrails))


def review_tag_creation_no_git_tag_created(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_created)


def review_tag_creation_no_git_tag_pushed(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_pushed)


def review_tag_creation_no_live_trading_claim(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.live_trading_overclaim)


def review_tag_creation_no_profitability_claim(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.profitability_overclaim)


def review_tag_creation_no_financial_advice_claim(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.financial_advice_overclaim)


def _no_overclaims(data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | None) -> bool:
    return bool(
        data
        and not data.live_trading_overclaim
        and not data.real_broker_overclaim
        and not data.real_order_overclaim
        and not data.paper_broker_overclaim
        and not data.profitability_overclaim
        and not data.financial_advice_overclaim
    )


def _boundary_risks(data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | None) -> tuple[Risk, ...]:
    if data is None:
        return ()
    risks: list[Risk] = []
    if data.file_read_requested:
        risks.append(Risk.FILE_READ_BOUNDARY_VIOLATION)
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


def assert_agicore_trading_v1_offline_tag_creation_instructions_review_boundaries(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def detect_agicore_trading_v1_offline_tag_creation_instructions_review_risks(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineTagCreationInstructionsReviewContext | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    risks: list[Risk] = []
    if payload is None:
        risks.append(Risk.TAG_CREATION_INSTRUCTIONS_REVIEW_INPUT_MISSING)
    if not review_tag_creation_instructions_approval(payload):
        risks.append(Risk.TAG_CREATION_INSTRUCTIONS_NOT_APPROVED)
    if not review_tag_creation_instructions_document(payload):
        risks.append(Risk.TAG_CREATION_INSTRUCTIONS_DOCUMENT_MISSING)
    if not review_tag_creation_instructions_tag_name(payload):
        risks.append(Risk.TAG_CREATION_TAG_NAME_INVALID)
    if not review_tag_creation_instructions_version(payload):
        risks.append(Risk.TAG_CREATION_VERSION_INVALID)
    if not review_tag_creation_pre_checks(context):
        risks.append(Risk.TAG_CREATION_PRE_CHECKS_MISSING)
    if not review_tag_creation_documented_commands_only(context):
        risks.append(Risk.TAG_CREATION_COMMANDS_NOT_DOCUMENTATION_ONLY)
    if not review_tag_creation_post_checks(context):
        risks.append(Risk.TAG_CREATION_POST_CHECKS_MISSING)
    if not review_tag_creation_human_guardrails(context):
        risks.append(Risk.TAG_CREATION_HUMAN_GUARDRAILS_MISSING)
    if payload and payload.git_tag_already_created:
        risks.append(Risk.GIT_TAG_ALREADY_CREATED)
    if payload and payload.git_tag_already_pushed:
        risks.append(Risk.GIT_TAG_ALREADY_PUSHED)
    if payload and payload.live_trading_overclaim:
        risks.append(Risk.LIVE_TRADING_READINESS_OVERCLAIM)
    if payload and payload.real_broker_overclaim:
        risks.append(Risk.REAL_BROKER_READINESS_OVERCLAIM)
    if payload and payload.real_order_overclaim:
        risks.append(Risk.REAL_ORDER_EXECUTION_OVERCLAIM)
    if payload and payload.paper_broker_overclaim:
        risks.append(Risk.PAPER_BROKER_CONNECTION_OVERCLAIM)
    if payload and payload.profitability_overclaim:
        risks.append(Risk.PROFITABILITY_PROOF_OVERCLAIM)
    if payload and payload.financial_advice_overclaim:
        risks.append(Risk.FINANCIAL_ADVICE_OVERCLAIM)
    risks.extend(_boundary_risks(payload))
    return _dedupe(risks)


def compute_agicore_trading_v1_offline_tag_creation_instructions_review_score(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineTagCreationInstructionsReviewContext | None,
    risks: tuple[Risk, ...],
) -> AGIcoreTradingV1OfflineTagCreationInstructionsReviewScore:
    payload = _coerce_input(data)
    input_score = 100 if validate_agicore_trading_v1_offline_tag_creation_instructions_review_input(payload) else 0
    approval_score = 100 if review_tag_creation_instructions_approval(payload) else 0
    document_score = 100 if review_tag_creation_instructions_document(payload) else 0
    tag_name_score = 100 if review_tag_creation_instructions_tag_name(payload) else 0
    version_score = 100 if review_tag_creation_instructions_version(payload) else 0
    pre_check_score = 100 if review_tag_creation_pre_checks(context) else 0
    command_score = 100 if review_tag_creation_documented_commands_only(context) else 0
    post_check_score = 100 if review_tag_creation_post_checks(context) else 0
    guardrail_score = 100 if review_tag_creation_human_guardrails(context) else 0
    no_tag_score = 100 if review_tag_creation_no_git_tag_created(payload) and review_tag_creation_no_git_tag_pushed(payload) else 0
    safety_score = 100 if _no_overclaims(payload) else 0
    boundary_score = 100 if not _boundary_risks(payload) else 0
    overall = min(
        input_score,
        approval_score,
        document_score,
        tag_name_score,
        version_score,
        pre_check_score,
        command_score,
        post_check_score,
        guardrail_score,
        no_tag_score,
        safety_score,
        boundary_score,
    )
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineTagCreationInstructionsReviewScore(
        overall_score=overall,
        input_score=input_score,
        approval_score=approval_score,
        document_score=document_score,
        tag_name_score=tag_name_score,
        version_score=version_score,
        pre_check_score=pre_check_score,
        command_score=command_score,
        post_check_score=post_check_score,
        guardrail_score=guardrail_score,
        no_tag_score=no_tag_score,
        safety_score=safety_score,
        boundary_score=boundary_score,
    )


def generate_agicore_trading_v1_offline_tag_creation_instructions_review_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.TAG_CREATION_INSTRUCTIONS_REVIEW_INPUT_MISSING: Recommendation.PROVIDE_TAG_CREATION_INSTRUCTIONS_REVIEW_INPUT,
        Risk.TAG_CREATION_INSTRUCTIONS_NOT_APPROVED: Recommendation.RESTORE_TAG_CREATION_INSTRUCTIONS_APPROVAL,
        Risk.TAG_CREATION_INSTRUCTIONS_DOCUMENT_MISSING: Recommendation.RESTORE_TAG_CREATION_INSTRUCTIONS_DOCUMENT,
        Risk.TAG_CREATION_TAG_NAME_INVALID: Recommendation.RESTORE_TAG_CREATION_TAG_NAME,
        Risk.TAG_CREATION_VERSION_INVALID: Recommendation.RESTORE_TAG_CREATION_VERSION,
        Risk.TAG_CREATION_PRE_CHECKS_MISSING: Recommendation.RESTORE_TAG_CREATION_PRE_CHECKS,
        Risk.TAG_CREATION_COMMANDS_NOT_DOCUMENTATION_ONLY: Recommendation.KEEP_TAG_COMMANDS_DOCUMENTATION_ONLY,
        Risk.TAG_CREATION_POST_CHECKS_MISSING: Recommendation.RESTORE_TAG_CREATION_POST_CHECKS,
        Risk.TAG_CREATION_HUMAN_GUARDRAILS_MISSING: Recommendation.RESTORE_TAG_CREATION_HUMAN_GUARDRAILS,
        Risk.GIT_TAG_ALREADY_CREATED: Recommendation.DO_NOT_CREATE_GIT_TAG_IN_REVIEW,
        Risk.GIT_TAG_ALREADY_PUSHED: Recommendation.DO_NOT_PUSH_GIT_TAG_IN_REVIEW,
        Risk.LIVE_TRADING_READINESS_OVERCLAIM: Recommendation.REMOVE_LIVE_TRADING_OVERCLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM: Recommendation.REMOVE_REAL_BROKER_OVERCLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM: Recommendation.REMOVE_REAL_ORDER_OVERCLAIM,
        Risk.PAPER_BROKER_CONNECTION_OVERCLAIM: Recommendation.REMOVE_PAPER_BROKER_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM: Recommendation.REMOVE_PROFITABILITY_OVERCLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM: Recommendation.REMOVE_FINANCIAL_ADVICE_OVERCLAIM,
        Risk.FILE_READ_BOUNDARY_VIOLATION: Recommendation.REMOVE_FILE_READ,
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
        recommendations.append(Recommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW
    if Risk.TAG_CREATION_INSTRUCTIONS_REVIEW_INPUT_MISSING in risks:
        return Decision.REQUIRE_TAG_CREATION_INSTRUCTIONS_REVIEW_INPUT_FIXES
    if Risk.TAG_CREATION_INSTRUCTIONS_NOT_APPROVED in risks or Risk.TAG_CREATION_INSTRUCTIONS_DOCUMENT_MISSING in risks:
        return Decision.REQUIRE_TAG_CREATION_INSTRUCTIONS_FIXES
    if Risk.TAG_CREATION_TAG_NAME_INVALID in risks:
        return Decision.REQUIRE_TAG_CREATION_TAG_NAME_FIXES
    if Risk.TAG_CREATION_VERSION_INVALID in risks:
        return Decision.REQUIRE_TAG_CREATION_VERSION_FIXES
    if Risk.TAG_CREATION_PRE_CHECKS_MISSING in risks:
        return Decision.REQUIRE_TAG_CREATION_PRE_CHECK_FIXES
    if Risk.TAG_CREATION_COMMANDS_NOT_DOCUMENTATION_ONLY in risks or Risk.TAG_CREATION_POST_CHECKS_MISSING in risks:
        return Decision.REQUIRE_TAG_CREATION_COMMAND_DOCUMENTATION_FIXES
    if Risk.TAG_CREATION_HUMAN_GUARDRAILS_MISSING in risks:
        return Decision.REQUIRE_TAG_CREATION_HUMAN_GUARDRAIL_FIXES
    return Decision.REQUIRE_TAG_CREATION_NO_OVERCLAIM_FIXES


def _state_for(data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO
    return State.AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW_BLOCKED


def _build_findings(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | None,
    context: AGIcoreTradingV1OfflineTagCreationInstructionsReviewContext | None,
) -> tuple[AGIcoreTradingV1OfflineTagCreationInstructionsReviewFinding, ...]:
    checks = (
        ("instructions approval", review_tag_creation_instructions_approval(data), EXPECTED_INSTRUCTIONS_DECISION),
        ("instructions document", review_tag_creation_instructions_document(data), "document present"),
        ("tag name", review_tag_creation_instructions_tag_name(data), EXPECTED_TAG_NAME),
        ("version", review_tag_creation_instructions_version(data), EXPECTED_VERSION),
        ("pre-checks", review_tag_creation_pre_checks(context), "pre-checks presents"),
        ("commands documentation only", review_tag_creation_documented_commands_only(context), "aucune execution de tag"),
        ("post-checks", review_tag_creation_post_checks(context), "post-checks presents"),
        ("human guardrails", review_tag_creation_human_guardrails(context), "validation humaine exigee"),
        ("no git tag created", review_tag_creation_no_git_tag_created(data), "aucun tag Git cree"),
        ("no git tag pushed", review_tag_creation_no_git_tag_pushed(data), "aucun tag Git pousse"),
        ("no live trading claim", review_tag_creation_no_live_trading_claim(data), "pas pret pour trading reel"),
        ("no profitability claim", review_tag_creation_no_profitability_claim(data), "pas de preuve de rentabilite"),
        ("no financial advice", review_tag_creation_no_financial_advice_claim(data), "pas de conseil financier"),
    )
    return tuple(AGIcoreTradingV1OfflineTagCreationInstructionsReviewFinding(name, passed, detail) for name, passed, detail in checks)


def render_agicore_trading_v1_offline_tag_creation_instructions_review_markdown(
    context: AGIcoreTradingV1OfflineTagCreationInstructionsReviewContext | None,
    findings: tuple[AGIcoreTradingV1OfflineTagCreationInstructionsReviewFinding, ...],
) -> str:
    tag_name = context.tag_metadata.tag_name if context else ""
    version = context.tag_metadata.version if context else ""
    pre_checks = context.pre_checks if context else ()
    commands = context.commands if context else ()
    guardrails = context.guardrails if context else ()
    lines = [
        "# AGIcore Trading v1 Offline Tag Creation Instructions Review",
        "",
        "## Statut",
        "",
        "instructions review only, no Git tag created",
        "",
        "## Decision attendue",
        "",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW",
        "",
        "## Conclusion",
        "",
        "- instructions de creation du tag completes",
        "- tag pret pour une future decision humaine",
        "- aucun tag Git cree pendant cette review",
        "- aucun tag Git pousse pendant cette review",
        "- pas pret pour trading reel",
        "- pas de broker reel",
        "- pas d'ordre reel",
        "- pas de preuve de rentabilite",
        "- pas de conseil financier",
        "",
        "## Instruction prealable verifiee",
        "",
        f"- {context.prerequisite_decision if context else ''}",
        "",
        "## Tag propose",
        "",
        f"- {tag_name}",
        "",
        "## Version proposee",
        "",
        f"- {version}",
        "",
        "## Verifications avant tag",
        "",
    ]
    lines.extend(f"- {check}" for check in pre_checks)
    lines.extend(("", "## Commandes documentees uniquement", ""))
    lines.extend(f"- {command.command}" for command in commands if command.documentation_only)
    lines.extend(("", "## Criteres humains avant creation reelle", ""))
    lines.extend(f"- {guardrail.name}" for guardrail in guardrails if guardrail.present)
    lines.extend(("", "## Findings", ""))
    lines.extend(f"- {finding.name} : {'OK' if finding.passed else 'FAIL'}" for finding in findings)
    lines.extend(
        (
            "",
            "## Prochaine etape suggeree",
            "",
            "AGIcore Trading v1 Offline Human Tag Go/No-Go",
        )
    )
    return "\n".join(lines) + "\n"


def validate_tag_creation_instructions_review_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Tag Creation Instructions Review",
        "instructions review only, no Git tag created",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW",
        "instructions de creation du tag completes",
        "tag pret pour une future decision humaine",
        "aucun tag Git cree pendant cette review",
        "aucun tag Git pousse pendant cette review",
        "pas pret pour trading reel",
        "pas de broker reel",
        "pas d'ordre reel",
        "pas de preuve de rentabilite",
        "pas de conseil financier",
        EXPECTED_INSTRUCTIONS_DECISION,
        EXPECTED_TAG_NAME,
        EXPECTED_VERSION,
        "git switch main",
        "git fetch origin",
        "git pull origin main",
        "python -m pytest tests/unit/ -q",
        "git status --short",
        "resultat attendu : seulement ?? data/",
        "git tag -a agicore-trading-v1-offline -m \"AGIcore Trading v1 Offline - sandbox release\"",
        "git push origin agicore-trading-v1-offline",
        "validation explicite de Bama",
        "confirmation que la release reste offline/sandbox uniquement",
        "AGIcore Trading v1 Offline Human Tag Go/No-Go",
    )
    return all(item in markdown for item in required)


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
        return {key: _payload_value(item) for key, item in vars(value).items() if not key.startswith("_")}
    return str(value)


def render_agicore_trading_v1_offline_tag_creation_instructions_review_json_report(
    result: AGIcoreTradingV1OfflineTagCreationInstructionsReviewResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineTagCreationInstructionsReviewResult):
        payload = {
            "schema": "agicore_trading_v1_offline_tag_creation_instructions_review",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload_value(result.context),
            "findings": _payload_value(result.findings),
            "git_tag_created": result.git_tag_created,
            "git_tag_pushed": result.git_tag_pushed,
            "live_trading_ready": False,
            "real_broker_ready": False,
            "real_order_execution": False,
            "paper_broker_connected": False,
            "profitability_proven": False,
            "financial_advice": False,
        }
    else:
        payload = dict(result)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def review_agicore_trading_v1_offline_tag_creation_instructions(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineTagCreationInstructionsReviewResult:
    payload = _coerce_input(data)
    context = build_tag_creation_instructions_review_context(payload)
    risks = detect_agicore_trading_v1_offline_tag_creation_instructions_review_risks(payload, context)
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_tag_creation_instructions_review_score(payload, context, risks)
    recommendations = generate_agicore_trading_v1_offline_tag_creation_instructions_review_recommendations(risks)
    findings = _build_findings(payload, context)
    base = AGIcoreTradingV1OfflineTagCreationInstructionsReviewResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        context=context,
        findings=findings,
        report=None,
        git_tag_created=False,
        git_tag_pushed=False,
    )
    report = AGIcoreTradingV1OfflineTagCreationInstructionsReviewReport(
        markdown=render_agicore_trading_v1_offline_tag_creation_instructions_review_markdown(context, findings),
        json=render_agicore_trading_v1_offline_tag_creation_instructions_review_json_report(base),
    )
    return AGIcoreTradingV1OfflineTagCreationInstructionsReviewResult(**{**base.__dict__, "report": report})
