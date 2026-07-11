"""AGIcore Trading v1 offline manual tag creation final checklist."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_manual_tag_creation_final_checklist_models import (
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistCommand,
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistContext,
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistDecision,
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput,
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistItem,
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRecommendation,
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistReport,
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistResult,
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk,
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistScore,
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistState,
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistStopRule,
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistTagMetadata,
)


Risk = AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk
Recommendation = AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRecommendation
Decision = AGIcoreTradingV1OfflineManualTagCreationFinalChecklistDecision
State = AGIcoreTradingV1OfflineManualTagCreationFinalChecklistState

EXPECTED_TAG_NAME = "agicore-trading-v1-offline"
EXPECTED_VERSION = "v1.0.0-offline"

PRE_TAG_ITEMS = (
    "etre sur main",
    "main synchronise avec origin/main",
    "tests/unit verts",
    "git status --short retourne seulement ?? data/",
    "aucun fichier en staging",
    "aucun tag existant avec le meme nom",
    "aucune cle API configuree pour cette operation",
    "aucun broker connecte",
    "confirmation humaine explicite de Bama",
)

DOCUMENTED_COMMANDS = (
    'git tag -a agicore-trading-v1-offline -m "AGIcore Trading v1 Offline - sandbox release"',
    "git push origin agicore-trading-v1-offline",
)

POST_TAG_ITEMS = (
    "verifier que le tag existe localement",
    "verifier que le tag existe sur origin",
    "verifier que main reste propre",
    "verifier que data/ na jamais ete ajoute",
)

STOP_RULES = (
    "STOP si tests rouges",
    "STOP si git status contient autre chose que data/",
    "STOP si data/ est staged",
    "STOP si un tag du meme nom existe deja",
    "STOP si une commande tente de connecter broker/API/cle",
    "STOP si la release est presentee comme trading reel ou rentable",
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
    data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput)}
    return AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput(
        **{key: value for key, value in dict(data).items() if key in allowed}
    )


def validate_agicore_trading_v1_offline_manual_tag_creation_final_checklist_input(
    data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(
        payload
        and payload.checklist_id
        and review_manual_tag_checklist_no_git_tag_created(payload)
        and review_manual_tag_checklist_no_git_tag_pushed(payload)
        and assert_agicore_trading_v1_offline_manual_tag_creation_final_checklist_boundaries(payload)
    )


def build_manual_tag_creation_final_checklist_context(
    data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineManualTagCreationFinalChecklistContext | None:
    payload = _coerce_input(data)
    if payload is None:
        return None
    prerequisites = (
        AGIcoreTradingV1OfflineManualTagCreationFinalChecklistItem(
            "Human Tag Go/No-Go approuve", payload.human_tag_go_no_go_approved
        ),
        AGIcoreTradingV1OfflineManualTagCreationFinalChecklistItem(
            "Tag Creation Instructions Review approuvee", payload.tag_creation_instructions_review_approved
        ),
        AGIcoreTradingV1OfflineManualTagCreationFinalChecklistItem(
            "Final Tag Review approuvee", payload.final_tag_review_approved
        ),
        AGIcoreTradingV1OfflineManualTagCreationFinalChecklistItem(
            "Release Package Review approuvee", payload.release_package_review_approved
        ),
        AGIcoreTradingV1OfflineManualTagCreationFinalChecklistItem(
            "Final Readiness Review approuvee", payload.final_readiness_review_approved
        ),
    )
    pre_tag_items = tuple(
        AGIcoreTradingV1OfflineManualTagCreationFinalChecklistItem(item, payload.pre_tag_items_present)
        for item in PRE_TAG_ITEMS
    )
    commands = tuple(
        AGIcoreTradingV1OfflineManualTagCreationFinalChecklistCommand(command, payload.commands_documentation_only)
        for command in DOCUMENTED_COMMANDS
    )
    post_tag_items = tuple(
        AGIcoreTradingV1OfflineManualTagCreationFinalChecklistItem(item, payload.post_tag_items_present)
        for item in POST_TAG_ITEMS
    )
    stop_rules = tuple(
        AGIcoreTradingV1OfflineManualTagCreationFinalChecklistStopRule(rule, payload.stop_rules_present)
        for rule in STOP_RULES
    )
    return AGIcoreTradingV1OfflineManualTagCreationFinalChecklistContext(
        checklist_id=payload.checklist_id,
        tag_metadata=AGIcoreTradingV1OfflineManualTagCreationFinalChecklistTagMetadata(
            tag_name=payload.tag_name,
            version=payload.version,
        ),
        prerequisites=prerequisites,
        pre_tag_items=pre_tag_items,
        commands=commands,
        post_tag_items=post_tag_items,
        stop_rules=stop_rules,
    )


def review_manual_tag_checklist_prerequisites(
    context: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistContext | None,
    data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | Mapping[str, Any] | None = None,
) -> bool:
    payload = _coerce_input(data) if data is not None else None
    prerequisites_complete = True if payload is None else payload.prerequisites_complete
    return bool(context and prerequisites_complete and all(item.present for item in context.prerequisites))


def review_manual_tag_checklist_tag_name(
    data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.tag_name == EXPECTED_TAG_NAME)


def review_manual_tag_checklist_version(
    data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.version == EXPECTED_VERSION)


def review_manual_tag_checklist_pre_tag_items(
    context: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistContext | None,
) -> bool:
    return bool(context and len(context.pre_tag_items) == len(PRE_TAG_ITEMS) and all(item.present for item in context.pre_tag_items))


def review_manual_tag_checklist_documented_commands_only(
    context: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistContext | None,
) -> bool:
    return bool(context and len(context.commands) == len(DOCUMENTED_COMMANDS) and all(command.documentation_only for command in context.commands))


def review_manual_tag_checklist_post_tag_items(
    context: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistContext | None,
) -> bool:
    return bool(context and len(context.post_tag_items) == len(POST_TAG_ITEMS) and all(item.present for item in context.post_tag_items))


def review_manual_tag_checklist_stop_procedure(
    context: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistContext | None,
) -> bool:
    return bool(context and len(context.stop_rules) == len(STOP_RULES) and all(rule.present for rule in context.stop_rules))


def review_manual_tag_checklist_no_git_tag_created(
    data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_created)


def review_manual_tag_checklist_no_git_tag_pushed(
    data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_pushed)


def review_manual_tag_checklist_no_live_trading_claim(
    data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.live_trading_overclaim)


def review_manual_tag_checklist_no_profitability_claim(
    data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.profitability_overclaim)


def review_manual_tag_checklist_no_financial_advice_claim(
    data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.financial_advice_overclaim)


def _no_overclaims(data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | None) -> bool:
    return bool(
        data
        and not data.live_trading_overclaim
        and not data.real_broker_overclaim
        and not data.real_order_overclaim
        and not data.paper_broker_overclaim
        and not data.profitability_overclaim
        and not data.financial_advice_overclaim
    )


def _boundary_risks(data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | None) -> tuple[Risk, ...]:
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


def assert_agicore_trading_v1_offline_manual_tag_creation_final_checklist_boundaries(
    data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def detect_agicore_trading_v1_offline_manual_tag_creation_final_checklist_risks(
    data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistContext | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    if payload is None:
        return (Risk.MANUAL_TAG_CHECKLIST_INPUT_MISSING,)
    risks: list[Risk] = []
    if not review_manual_tag_checklist_prerequisites(context, payload):
        risks.append(Risk.MANUAL_TAG_CHECKLIST_PREREQUISITES_INCOMPLETE)
    if not review_manual_tag_checklist_tag_name(payload):
        risks.append(Risk.MANUAL_TAG_CHECKLIST_TAG_NAME_INVALID)
    if not review_manual_tag_checklist_version(payload):
        risks.append(Risk.MANUAL_TAG_CHECKLIST_VERSION_INVALID)
    if not review_manual_tag_checklist_pre_tag_items(context):
        risks.append(Risk.MANUAL_TAG_CHECKLIST_PRE_TAG_ITEMS_MISSING)
    if not review_manual_tag_checklist_documented_commands_only(context):
        risks.append(Risk.MANUAL_TAG_CHECKLIST_COMMANDS_NOT_DOCUMENTATION_ONLY)
    if not review_manual_tag_checklist_post_tag_items(context):
        risks.append(Risk.MANUAL_TAG_CHECKLIST_POST_TAG_ITEMS_MISSING)
    if not review_manual_tag_checklist_stop_procedure(context):
        risks.append(Risk.MANUAL_TAG_CHECKLIST_STOP_RULES_MISSING)
    if payload.git_tag_already_created:
        risks.append(Risk.GIT_TAG_ALREADY_CREATED)
    if payload.git_tag_already_pushed:
        risks.append(Risk.GIT_TAG_ALREADY_PUSHED)
    if payload.live_trading_overclaim:
        risks.append(Risk.LIVE_TRADING_READINESS_OVERCLAIM)
    if payload.real_broker_overclaim:
        risks.append(Risk.REAL_BROKER_READINESS_OVERCLAIM)
    if payload.real_order_overclaim:
        risks.append(Risk.REAL_ORDER_EXECUTION_OVERCLAIM)
    if payload.paper_broker_overclaim:
        risks.append(Risk.PAPER_BROKER_CONNECTION_OVERCLAIM)
    if payload.profitability_overclaim:
        risks.append(Risk.PROFITABILITY_PROOF_OVERCLAIM)
    if payload.financial_advice_overclaim:
        risks.append(Risk.FINANCIAL_ADVICE_OVERCLAIM)
    risks.extend(_boundary_risks(payload))
    return _dedupe(risks)


def compute_agicore_trading_v1_offline_manual_tag_creation_final_checklist_score(
    data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistContext | None,
    risks: tuple[Risk, ...],
) -> AGIcoreTradingV1OfflineManualTagCreationFinalChecklistScore:
    payload = _coerce_input(data)
    input_score = 100 if validate_agicore_trading_v1_offline_manual_tag_creation_final_checklist_input(payload) else 0
    prerequisite_score = 100 if review_manual_tag_checklist_prerequisites(context, payload) else 0
    tag_name_score = 100 if review_manual_tag_checklist_tag_name(payload) else 0
    version_score = 100 if review_manual_tag_checklist_version(payload) else 0
    pre_tag_score = 100 if review_manual_tag_checklist_pre_tag_items(context) else 0
    command_score = 100 if review_manual_tag_checklist_documented_commands_only(context) else 0
    post_tag_score = 100 if review_manual_tag_checklist_post_tag_items(context) else 0
    stop_rule_score = 100 if review_manual_tag_checklist_stop_procedure(context) else 0
    no_tag_score = 100 if review_manual_tag_checklist_no_git_tag_created(payload) and review_manual_tag_checklist_no_git_tag_pushed(payload) else 0
    safety_score = 100 if _no_overclaims(payload) else 0
    boundary_score = 100 if not _boundary_risks(payload) else 0
    overall = min(
        input_score,
        prerequisite_score,
        tag_name_score,
        version_score,
        pre_tag_score,
        command_score,
        post_tag_score,
        stop_rule_score,
        no_tag_score,
        safety_score,
        boundary_score,
    )
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineManualTagCreationFinalChecklistScore(
        overall_score=overall,
        input_score=input_score,
        prerequisite_score=prerequisite_score,
        tag_name_score=tag_name_score,
        version_score=version_score,
        pre_tag_score=pre_tag_score,
        command_score=command_score,
        post_tag_score=post_tag_score,
        stop_rule_score=stop_rule_score,
        no_tag_score=no_tag_score,
        safety_score=safety_score,
        boundary_score=boundary_score,
    )


def generate_agicore_trading_v1_offline_manual_tag_creation_final_checklist_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.MANUAL_TAG_CHECKLIST_INPUT_MISSING: Recommendation.PROVIDE_MANUAL_TAG_CHECKLIST_INPUT,
        Risk.MANUAL_TAG_CHECKLIST_PREREQUISITES_INCOMPLETE: Recommendation.RESTORE_MANUAL_TAG_CHECKLIST_PREREQUISITES,
        Risk.MANUAL_TAG_CHECKLIST_TAG_NAME_INVALID: Recommendation.RESTORE_MANUAL_TAG_CHECKLIST_TAG_NAME,
        Risk.MANUAL_TAG_CHECKLIST_VERSION_INVALID: Recommendation.RESTORE_MANUAL_TAG_CHECKLIST_VERSION,
        Risk.MANUAL_TAG_CHECKLIST_PRE_TAG_ITEMS_MISSING: Recommendation.RESTORE_MANUAL_TAG_CHECKLIST_PRE_TAG_ITEMS,
        Risk.MANUAL_TAG_CHECKLIST_COMMANDS_NOT_DOCUMENTATION_ONLY: Recommendation.KEEP_MANUAL_TAG_COMMANDS_DOCUMENTATION_ONLY,
        Risk.MANUAL_TAG_CHECKLIST_POST_TAG_ITEMS_MISSING: Recommendation.RESTORE_MANUAL_TAG_CHECKLIST_POST_TAG_ITEMS,
        Risk.MANUAL_TAG_CHECKLIST_STOP_RULES_MISSING: Recommendation.RESTORE_MANUAL_TAG_CHECKLIST_STOP_RULES,
        Risk.GIT_TAG_ALREADY_CREATED: Recommendation.DO_NOT_CREATE_GIT_TAG_IN_THIS_PHASE,
        Risk.GIT_TAG_ALREADY_PUSHED: Recommendation.DO_NOT_PUSH_GIT_TAG_IN_THIS_PHASE,
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
        recommendations.append(Recommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST
    if Risk.MANUAL_TAG_CHECKLIST_INPUT_MISSING in risks:
        return Decision.REQUIRE_MANUAL_TAG_CHECKLIST_INPUT_FIXES
    if Risk.MANUAL_TAG_CHECKLIST_PREREQUISITES_INCOMPLETE in risks:
        return Decision.REQUIRE_MANUAL_TAG_CHECKLIST_PREREQUISITE_FIXES
    if Risk.MANUAL_TAG_CHECKLIST_TAG_NAME_INVALID in risks:
        return Decision.REQUIRE_MANUAL_TAG_CHECKLIST_TAG_NAME_FIXES
    if Risk.MANUAL_TAG_CHECKLIST_VERSION_INVALID in risks:
        return Decision.REQUIRE_MANUAL_TAG_CHECKLIST_VERSION_FIXES
    if Risk.MANUAL_TAG_CHECKLIST_PRE_TAG_ITEMS_MISSING in risks:
        return Decision.REQUIRE_MANUAL_TAG_CHECKLIST_PRE_TAG_FIXES
    if Risk.MANUAL_TAG_CHECKLIST_COMMANDS_NOT_DOCUMENTATION_ONLY in risks:
        return Decision.REQUIRE_MANUAL_TAG_CHECKLIST_COMMAND_DOCUMENTATION_FIXES
    if Risk.MANUAL_TAG_CHECKLIST_POST_TAG_ITEMS_MISSING in risks:
        return Decision.REQUIRE_MANUAL_TAG_CHECKLIST_POST_TAG_FIXES
    if Risk.MANUAL_TAG_CHECKLIST_STOP_RULES_MISSING in risks:
        return Decision.REQUIRE_MANUAL_TAG_CHECKLIST_STOP_RULE_FIXES
    return Decision.REQUIRE_MANUAL_TAG_CHECKLIST_NO_OVERCLAIM_FIXES


def _state_for(data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL
    return State.AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST_BLOCKED


def render_agicore_trading_v1_offline_manual_tag_creation_final_checklist_markdown(
    context: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistContext | None,
) -> str:
    metadata = context.tag_metadata if context else None
    prerequisites = context.prerequisites if context else ()
    pre_tag_items = context.pre_tag_items if context else ()
    commands = context.commands if context else ()
    post_tag_items = context.post_tag_items if context else ()
    stop_rules = context.stop_rules if context else ()
    lines = [
        "# AGIcore Trading v1 Offline Manual Tag Creation Final Checklist",
        "",
        "## Statut",
        "",
        "final checklist only, no Git tag created",
        "",
        "## Decision attendue",
        "",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST",
        "",
        "## Conclusion",
        "",
        "- checklist finale prete",
        "- tag pret pour creation manuelle future uniquement apres validation humaine",
        "- aucun tag Git cree dans cette phase",
        "- aucun tag Git pousse dans cette phase",
        "- AGIcore Trading v1 Offline reste sandbox/offline uniquement",
        "- pas pret pour trading reel",
        "- pas de broker reel",
        "- pas d'ordre reel",
        "- pas de preuve de rentabilite",
        "- pas de conseil financier",
        "",
        "## Prerequis valides",
        "",
    ]
    lines.extend(f"- {item.name}" for item in prerequisites if item.present)
    lines.extend(("", "## Tag propose", "", f"- {metadata.tag_name if metadata else ''}"))
    lines.extend(("", "## Version proposee", "", f"- {metadata.version if metadata else ''}"))
    lines.extend(("", "## Checklist avant tag", ""))
    lines.extend(f"- {item.name}" for item in pre_tag_items if item.present)
    lines.extend(("", "## Commandes futures documentees uniquement", ""))
    lines.extend(f"- {command.command}" for command in commands if command.documentation_only)
    lines.extend(("", "## Checklist apres tag", ""))
    lines.extend(f"- {item.name}" for item in post_tag_items if item.present)
    lines.extend(("", "## Procedure STOP", ""))
    lines.extend(f"- {rule.rule}" for rule in stop_rules if rule.present)
    lines.extend(("", "## Prochaine etape suggeree", "", "AGIcore Trading v1 Offline Manual Tag Creation Approval"))
    return "\n".join(lines) + "\n"


def validate_manual_tag_creation_final_checklist_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Manual Tag Creation Final Checklist",
        "final checklist only, no Git tag created",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST",
        "checklist finale prete",
        "tag pret pour creation manuelle future uniquement apres validation humaine",
        "aucun tag Git cree dans cette phase",
        "aucun tag Git pousse dans cette phase",
        "AGIcore Trading v1 Offline reste sandbox/offline uniquement",
        "pas pret pour trading reel",
        "pas de broker reel",
        "pas d'ordre reel",
        "pas de preuve de rentabilite",
        "pas de conseil financier",
        "Human Tag Go/No-Go approuve",
        "Tag Creation Instructions Review approuvee",
        "Final Tag Review approuvee",
        "Release Package Review approuvee",
        "Final Readiness Review approuvee",
        EXPECTED_TAG_NAME,
        EXPECTED_VERSION,
        "etre sur main",
        "main synchronise avec origin/main",
        "tests/unit verts",
        "git status --short retourne seulement ?? data/",
        "aucun fichier en staging",
        "aucun tag existant avec le meme nom",
        "aucune cle API configuree pour cette operation",
        "aucun broker connecte",
        "confirmation humaine explicite de Bama",
        'git tag -a agicore-trading-v1-offline -m "AGIcore Trading v1 Offline - sandbox release"',
        "git push origin agicore-trading-v1-offline",
        "verifier que le tag existe localement",
        "verifier que le tag existe sur origin",
        "verifier que main reste propre",
        "verifier que data/ na jamais ete ajoute",
        "STOP si tests rouges",
        "STOP si git status contient autre chose que data/",
        "STOP si data/ est staged",
        "STOP si un tag du meme nom existe deja",
        "STOP si une commande tente de connecter broker/API/cle",
        "STOP si la release est presentee comme trading reel ou rentable",
        "AGIcore Trading v1 Offline Manual Tag Creation Approval",
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


def render_agicore_trading_v1_offline_manual_tag_creation_final_checklist_json_report(
    result: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineManualTagCreationFinalChecklistResult):
        payload = {
            "schema": "agicore_trading_v1_offline_manual_tag_creation_final_checklist",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload_value(result.context),
            "git_tag_created": result.git_tag_created,
            "git_tag_pushed": result.git_tag_pushed,
            "commands_documented_only": True,
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


def build_agicore_trading_v1_offline_manual_tag_creation_final_checklist(
    data: AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineManualTagCreationFinalChecklistResult:
    payload = _coerce_input(data)
    context = build_manual_tag_creation_final_checklist_context(payload)
    risks = detect_agicore_trading_v1_offline_manual_tag_creation_final_checklist_risks(payload, context)
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_manual_tag_creation_final_checklist_score(payload, context, risks)
    recommendations = generate_agicore_trading_v1_offline_manual_tag_creation_final_checklist_recommendations(risks)
    base = AGIcoreTradingV1OfflineManualTagCreationFinalChecklistResult(
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
    report = AGIcoreTradingV1OfflineManualTagCreationFinalChecklistReport(
        markdown=render_agicore_trading_v1_offline_manual_tag_creation_final_checklist_markdown(context),
        json=render_agicore_trading_v1_offline_manual_tag_creation_final_checklist_json_report(base),
    )
    return AGIcoreTradingV1OfflineManualTagCreationFinalChecklistResult(**{**base.__dict__, "report": report})
