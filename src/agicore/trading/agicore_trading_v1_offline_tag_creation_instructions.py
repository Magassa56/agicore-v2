"""AGIcore Trading v1 offline tag creation instructions."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_tag_creation_instructions_models import (
    AGIcoreTradingV1OfflineTagCreationInstructionsCheck,
    AGIcoreTradingV1OfflineTagCreationInstructionsCommand,
    AGIcoreTradingV1OfflineTagCreationInstructionsContext,
    AGIcoreTradingV1OfflineTagCreationInstructionsDecision,
    AGIcoreTradingV1OfflineTagCreationInstructionsInput,
    AGIcoreTradingV1OfflineTagCreationInstructionsRecommendation,
    AGIcoreTradingV1OfflineTagCreationInstructionsReport,
    AGIcoreTradingV1OfflineTagCreationInstructionsResult,
    AGIcoreTradingV1OfflineTagCreationInstructionsRisk,
    AGIcoreTradingV1OfflineTagCreationInstructionsSafetyRule,
    AGIcoreTradingV1OfflineTagCreationInstructionsScore,
    AGIcoreTradingV1OfflineTagCreationInstructionsState,
)


Risk = AGIcoreTradingV1OfflineTagCreationInstructionsRisk
Recommendation = AGIcoreTradingV1OfflineTagCreationInstructionsRecommendation
Decision = AGIcoreTradingV1OfflineTagCreationInstructionsDecision
State = AGIcoreTradingV1OfflineTagCreationInstructionsState

EXPECTED_FINAL_REVIEW_DECISION = "APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW"
EXPECTED_TAG_NAME = "agicore-trading-v1-offline"
EXPECTED_VERSION = "v1.0.0-offline"

PRE_TAG_CHECKS = (
    ("switch main", "git switch main", "main branche active"),
    ("fetch origin", "git fetch origin", "remote refs synchronisees"),
    ("pull main", "git pull origin main", "main a jour"),
    ("unit tests", "python -m pytest tests/unit/ -q", "tests verts"),
    ("git status", "git status --short", "seulement ?? data/"),
)

MANUAL_TAG_COMMANDS = (
    (
        "git tag -a agicore-trading-v1-offline -m \"AGIcore Trading v1 Offline - sandbox release\"",
        "creer le tag annote manuellement apres validation humaine finale",
    ),
    (
        "git push origin agicore-trading-v1-offline",
        "publier le tag manuellement apres verification locale",
    ),
)

POST_TAG_CHECKS = (
    ("local tag visible", "git tag --list agicore-trading-v1-offline", "agicore-trading-v1-offline"),
    ("remote tag visible", "git ls-remote --tags origin agicore-trading-v1-offline", "tag distant present"),
    ("status clean", "git status --short", "seulement ?? data/"),
)

SAFETY_RULES = (
    "ne pas creer le tag avant validation humaine finale",
    "ne pas utiliser pour trading reel",
    "pas de broker reel",
    "pas d'ordre reel",
    "pas de preuve de rentabilite",
    "pas de conseil financier",
    "aucune lecture data/",
    "aucune ecriture data/",
    "aucune cle API",
    "aucun reseau dans cette phase",
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
    data: AGIcoreTradingV1OfflineTagCreationInstructionsInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineTagCreationInstructionsInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineTagCreationInstructionsInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineTagCreationInstructionsInput)}
    return AGIcoreTradingV1OfflineTagCreationInstructionsInput(
        **{key: value for key, value in dict(data).items() if key in allowed}
    )


def validate_agicore_trading_v1_offline_tag_creation_instructions_input(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(
        payload
        and payload.instruction_id
        and validate_tag_creation_instructions_no_git_tag_created(payload)
        and assert_agicore_trading_v1_offline_tag_creation_instructions_boundaries(payload)
    )


def build_tag_creation_safety_section(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsInput | Mapping[str, Any] | None,
) -> tuple[AGIcoreTradingV1OfflineTagCreationInstructionsSafetyRule, ...]:
    payload = _coerce_input(data)
    present = bool(payload and payload.warning_present and payload.safety_language_present)
    return tuple(AGIcoreTradingV1OfflineTagCreationInstructionsSafetyRule(rule, present) for rule in SAFETY_RULES)


def build_tag_creation_pre_checks_section(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsInput | Mapping[str, Any] | None,
) -> tuple[AGIcoreTradingV1OfflineTagCreationInstructionsCheck, ...]:
    payload = _coerce_input(data)
    present = bool(payload and payload.pre_checks_present)
    return tuple(AGIcoreTradingV1OfflineTagCreationInstructionsCheck(name, command, expected, present) for name, command, expected in PRE_TAG_CHECKS)


def build_tag_creation_commands_section(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsInput | Mapping[str, Any] | None,
) -> tuple[AGIcoreTradingV1OfflineTagCreationInstructionsCommand, ...]:
    payload = _coerce_input(data)
    if not payload or not payload.manual_commands_documented:
        return ()
    return tuple(AGIcoreTradingV1OfflineTagCreationInstructionsCommand(command, purpose) for command, purpose in MANUAL_TAG_COMMANDS)


def build_tag_creation_post_checks_section(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsInput | Mapping[str, Any] | None,
) -> tuple[AGIcoreTradingV1OfflineTagCreationInstructionsCheck, ...]:
    payload = _coerce_input(data)
    present = bool(payload and payload.post_checks_present)
    return tuple(AGIcoreTradingV1OfflineTagCreationInstructionsCheck(name, command, expected, present) for name, command, expected in POST_TAG_CHECKS)


def build_tag_creation_instructions_context(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineTagCreationInstructionsContext | None:
    payload = _coerce_input(data)
    if payload is None:
        return None
    return AGIcoreTradingV1OfflineTagCreationInstructionsContext(
        instruction_id=payload.instruction_id,
        prerequisite_decision=EXPECTED_FINAL_REVIEW_DECISION,
        tag_name=payload.tag_name,
        version=payload.version,
        pre_checks=build_tag_creation_pre_checks_section(payload),
        manual_commands=build_tag_creation_commands_section(payload),
        post_checks=build_tag_creation_post_checks_section(payload),
        safety_rules=build_tag_creation_safety_section(payload),
    )


def validate_tag_creation_instructions_no_git_tag_created(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_created and not payload.git_tag_command_executed and not payload.git_push_tag_executed)


def validate_tag_creation_instructions_no_overclaims(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(
        payload
        and not payload.live_trading_overclaim
        and not payload.real_broker_overclaim
        and not payload.real_order_overclaim
        and not payload.paper_broker_overclaim
        and not payload.profitability_overclaim
        and not payload.financial_advice_overclaim
    )


def validate_tag_creation_instructions_safety_language(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.warning_present and payload.safety_language_present)


def _boundary_risks(data: AGIcoreTradingV1OfflineTagCreationInstructionsInput | None) -> tuple[Risk, ...]:
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


def assert_agicore_trading_v1_offline_tag_creation_instructions_boundaries(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsInput | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def detect_agicore_trading_v1_offline_tag_creation_instructions_risks(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineTagCreationInstructionsContext | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    risks: list[Risk] = []
    if payload is None:
        risks.append(Risk.TAG_CREATION_INSTRUCTIONS_INPUT_MISSING)
    if not (payload and payload.final_tag_review_approved):
        risks.append(Risk.FINAL_TAG_REVIEW_NOT_APPROVED)
    if not (payload and payload.tag_name == EXPECTED_TAG_NAME):
        risks.append(Risk.TAG_CREATION_TAG_NAME_INVALID)
    if not (payload and payload.version == EXPECTED_VERSION):
        risks.append(Risk.TAG_CREATION_VERSION_INVALID)
    if not (context and context.pre_checks and all(check.present for check in context.pre_checks)):
        risks.append(Risk.TAG_CREATION_PRE_CHECKS_MISSING)
    if not (context and len(context.manual_commands) == len(MANUAL_TAG_COMMANDS)):
        risks.append(Risk.TAG_CREATION_COMMANDS_MISSING)
    if not (context and context.post_checks and all(check.present for check in context.post_checks)):
        risks.append(Risk.TAG_CREATION_POST_CHECKS_MISSING)
    if not (payload and payload.warning_present):
        risks.append(Risk.TAG_CREATION_WARNING_MISSING)
    if not validate_tag_creation_instructions_safety_language(payload):
        risks.append(Risk.TAG_CREATION_SAFETY_LANGUAGE_MISSING)
    if payload and payload.git_tag_already_created:
        risks.append(Risk.GIT_TAG_ALREADY_CREATED)
    if payload and payload.git_tag_command_executed:
        risks.append(Risk.GIT_TAG_COMMAND_EXECUTED)
    if payload and payload.git_push_tag_executed:
        risks.append(Risk.GIT_TAG_PUSH_EXECUTED)
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


def compute_agicore_trading_v1_offline_tag_creation_instructions_score(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineTagCreationInstructionsContext | None,
    risks: tuple[Risk, ...],
) -> AGIcoreTradingV1OfflineTagCreationInstructionsScore:
    payload = _coerce_input(data)
    input_score = 100 if validate_agicore_trading_v1_offline_tag_creation_instructions_input(payload) else 0
    final_review_score = 100 if payload and payload.final_tag_review_approved else 0
    tag_name_score = 100 if payload and payload.tag_name == EXPECTED_TAG_NAME else 0
    version_score = 100 if payload and payload.version == EXPECTED_VERSION else 0
    pre_check_score = 100 if context and context.pre_checks and all(check.present for check in context.pre_checks) else 0
    command_score = 100 if context and len(context.manual_commands) == len(MANUAL_TAG_COMMANDS) else 0
    post_check_score = 100 if context and context.post_checks and all(check.present for check in context.post_checks) else 0
    safety_score = 100 if validate_tag_creation_instructions_safety_language(payload) else 0
    no_execution_score = 100 if validate_tag_creation_instructions_no_git_tag_created(payload) else 0
    boundary_score = 100 if not _boundary_risks(payload) else 0
    overall = min(
        input_score,
        final_review_score,
        tag_name_score,
        version_score,
        pre_check_score,
        command_score,
        post_check_score,
        safety_score,
        no_execution_score,
        boundary_score,
    )
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineTagCreationInstructionsScore(
        overall_score=overall,
        input_score=input_score,
        final_review_score=final_review_score,
        tag_name_score=tag_name_score,
        version_score=version_score,
        pre_check_score=pre_check_score,
        command_score=command_score,
        post_check_score=post_check_score,
        safety_score=safety_score,
        no_execution_score=no_execution_score,
        boundary_score=boundary_score,
    )


def generate_agicore_trading_v1_offline_tag_creation_instructions_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.TAG_CREATION_INSTRUCTIONS_INPUT_MISSING: Recommendation.PROVIDE_TAG_CREATION_INSTRUCTIONS_INPUT,
        Risk.FINAL_TAG_REVIEW_NOT_APPROVED: Recommendation.RESTORE_FINAL_TAG_REVIEW_APPROVAL,
        Risk.TAG_CREATION_TAG_NAME_INVALID: Recommendation.RESTORE_TAG_CREATION_TAG_NAME,
        Risk.TAG_CREATION_VERSION_INVALID: Recommendation.RESTORE_TAG_CREATION_VERSION,
        Risk.TAG_CREATION_PRE_CHECKS_MISSING: Recommendation.RESTORE_TAG_CREATION_PRE_CHECKS,
        Risk.TAG_CREATION_COMMANDS_MISSING: Recommendation.RESTORE_TAG_CREATION_COMMANDS,
        Risk.TAG_CREATION_POST_CHECKS_MISSING: Recommendation.RESTORE_TAG_CREATION_POST_CHECKS,
        Risk.TAG_CREATION_WARNING_MISSING: Recommendation.RESTORE_TAG_CREATION_WARNING,
        Risk.TAG_CREATION_SAFETY_LANGUAGE_MISSING: Recommendation.RESTORE_TAG_CREATION_SAFETY_LANGUAGE,
        Risk.GIT_TAG_ALREADY_CREATED: Recommendation.DO_NOT_CREATE_GIT_TAG_IN_THIS_PHASE,
        Risk.GIT_TAG_COMMAND_EXECUTED: Recommendation.DO_NOT_CREATE_GIT_TAG_IN_THIS_PHASE,
        Risk.GIT_TAG_PUSH_EXECUTED: Recommendation.DO_NOT_PUSH_GIT_TAG_IN_THIS_PHASE,
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
        recommendations.append(Recommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS
    if Risk.TAG_CREATION_INSTRUCTIONS_INPUT_MISSING in risks:
        return Decision.REQUIRE_TAG_CREATION_INSTRUCTIONS_INPUT_FIXES
    if Risk.FINAL_TAG_REVIEW_NOT_APPROVED in risks:
        return Decision.REQUIRE_TAG_CREATION_INSTRUCTIONS_FINAL_REVIEW_FIXES
    if Risk.TAG_CREATION_TAG_NAME_INVALID in risks:
        return Decision.REQUIRE_TAG_CREATION_INSTRUCTIONS_TAG_NAME_FIXES
    if Risk.TAG_CREATION_VERSION_INVALID in risks:
        return Decision.REQUIRE_TAG_CREATION_INSTRUCTIONS_VERSION_FIXES
    if Risk.TAG_CREATION_PRE_CHECKS_MISSING in risks:
        return Decision.REQUIRE_TAG_CREATION_INSTRUCTIONS_PRE_CHECK_FIXES
    if Risk.TAG_CREATION_COMMANDS_MISSING in risks:
        return Decision.REQUIRE_TAG_CREATION_INSTRUCTIONS_COMMAND_FIXES
    if Risk.TAG_CREATION_POST_CHECKS_MISSING in risks:
        return Decision.REQUIRE_TAG_CREATION_INSTRUCTIONS_POST_CHECK_FIXES
    safety_risks = {
        Risk.TAG_CREATION_WARNING_MISSING,
        Risk.TAG_CREATION_SAFETY_LANGUAGE_MISSING,
        Risk.GIT_TAG_ALREADY_CREATED,
        Risk.GIT_TAG_COMMAND_EXECUTED,
        Risk.GIT_TAG_PUSH_EXECUTED,
    }
    if set(risks) & safety_risks:
        return Decision.REQUIRE_TAG_CREATION_INSTRUCTIONS_SAFETY_FIXES
    return Decision.REQUIRE_TAG_CREATION_INSTRUCTIONS_NO_OVERCLAIM_FIXES


def _state_for(data: AGIcoreTradingV1OfflineTagCreationInstructionsInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW
    return State.AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_BLOCKED


def render_agicore_trading_v1_offline_tag_creation_instructions_markdown(
    context: AGIcoreTradingV1OfflineTagCreationInstructionsContext | None,
) -> str:
    pre_checks = context.pre_checks if context else ()
    manual_commands = context.manual_commands if context else ()
    post_checks = context.post_checks if context else ()
    safety_rules = context.safety_rules if context else ()
    lines = [
        "# AGIcore Trading v1 Offline Tag Creation Instructions",
        "",
        "## Statut",
        "",
        "instructions only, no Git tag created",
        "",
        "## Decision prealable requise",
        "",
        f"- {context.prerequisite_decision if context else ''}",
        "",
        "## Tag propose",
        "",
        f"- {context.tag_name if context else ''}",
        "",
        "## Version proposee",
        "",
        f"- {context.version if context else ''}",
        "",
        "## Avertissement",
        "",
    ]
    lines.extend(f"- {rule.name}" for rule in safety_rules if rule.present)
    lines.extend(("", "## Verifications avant tag", ""))
    lines.extend(f"- {check.command} ; resultat attendu : {check.expected}" for check in pre_checks if check.present)
    lines.extend(("", "## Commandes proposees pour creation manuelle future", ""))
    lines.extend(f"- `{command.command}` ; {command.purpose}" for command in manual_commands if command.documentation_only)
    lines.extend(("", "## Verifications apres tag", ""))
    lines.extend(f"- {check.command} ; resultat attendu : {check.expected}" for check in post_checks if check.present)
    lines.extend(
        (
            "",
            "## Decision instructions",
            "",
            "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS",
            "",
            "## State attendu",
            "",
            "READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW",
            "",
            "## STOP",
            "",
            "STOP avant commit. Ne pas creer le tag dans cette phase.",
        )
    )
    return "\n".join(lines) + "\n"


def validate_tag_creation_instructions_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Tag Creation Instructions",
        "instructions only, no Git tag created",
        EXPECTED_FINAL_REVIEW_DECISION,
        EXPECTED_TAG_NAME,
        EXPECTED_VERSION,
        "ne pas creer le tag avant validation humaine finale",
        "ne pas utiliser pour trading reel",
        "pas de broker reel",
        "pas d'ordre reel",
        "pas de preuve de rentabilite",
        "pas de conseil financier",
        "git switch main",
        "git fetch origin",
        "git pull origin main",
        "python -m pytest tests/unit/ -q",
        "git status --short",
        "seulement ?? data/",
        "git tag -a agicore-trading-v1-offline -m \"AGIcore Trading v1 Offline - sandbox release\"",
        "git push origin agicore-trading-v1-offline",
        "git tag --list agicore-trading-v1-offline",
        "git ls-remote --tags origin agicore-trading-v1-offline",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS",
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW",
        "STOP avant commit",
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


def render_agicore_trading_v1_offline_tag_creation_instructions_json_report(
    result: AGIcoreTradingV1OfflineTagCreationInstructionsResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineTagCreationInstructionsResult):
        payload = {
            "schema": "agicore_trading_v1_offline_tag_creation_instructions",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload_value(result.context),
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


def build_agicore_trading_v1_offline_tag_creation_instructions(
    data: AGIcoreTradingV1OfflineTagCreationInstructionsInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineTagCreationInstructionsResult:
    payload = _coerce_input(data)
    context = build_tag_creation_instructions_context(payload)
    risks = detect_agicore_trading_v1_offline_tag_creation_instructions_risks(payload, context)
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_tag_creation_instructions_score(payload, context, risks)
    recommendations = generate_agicore_trading_v1_offline_tag_creation_instructions_recommendations(risks)
    base = AGIcoreTradingV1OfflineTagCreationInstructionsResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        context=context,
        report=None,
        git_tag_created=False,
        git_tag_pushed=False,
    )
    report = AGIcoreTradingV1OfflineTagCreationInstructionsReport(
        markdown=render_agicore_trading_v1_offline_tag_creation_instructions_markdown(context),
        json=render_agicore_trading_v1_offline_tag_creation_instructions_json_report(base),
    )
    return AGIcoreTradingV1OfflineTagCreationInstructionsResult(**{**base.__dict__, "report": report})
