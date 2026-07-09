"""AGIcore Trading v1 offline release package builder."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_release_package_models import (
    AGIcoreTradingV1OfflineReleasePackageCapability,
    AGIcoreTradingV1OfflineReleasePackageCommand,
    AGIcoreTradingV1OfflineReleasePackageContext,
    AGIcoreTradingV1OfflineReleasePackageDecision,
    AGIcoreTradingV1OfflineReleasePackageDocument,
    AGIcoreTradingV1OfflineReleasePackageInput,
    AGIcoreTradingV1OfflineReleasePackageKnownLimitation,
    AGIcoreTradingV1OfflineReleasePackageNonGoal,
    AGIcoreTradingV1OfflineReleasePackageRecommendation,
    AGIcoreTradingV1OfflineReleasePackageReport,
    AGIcoreTradingV1OfflineReleasePackageResult,
    AGIcoreTradingV1OfflineReleasePackageRisk,
    AGIcoreTradingV1OfflineReleasePackageSafetyRule,
    AGIcoreTradingV1OfflineReleasePackageScore,
    AGIcoreTradingV1OfflineReleasePackageState,
    AGIcoreTradingV1OfflineReleasePackageTestingEvidence,
)


Risk = AGIcoreTradingV1OfflineReleasePackageRisk
Recommendation = AGIcoreTradingV1OfflineReleasePackageRecommendation
Decision = AGIcoreTradingV1OfflineReleasePackageDecision
State = AGIcoreTradingV1OfflineReleasePackageState

DOCUMENTS = (
    "AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES.md",
    "AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE.md",
    "AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK.md",
    "AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW.md",
)

CAPABILITIES = (
    "CSV Replay Input v1",
    "Synthetic Market Scenario v1",
    "Strategy Replay Engine v1",
    "Simulated Broker Stub v1",
    "Risk Guard Enforcement v1",
    "Journal Writer v1",
    "Offline Report Markdown JSON v1",
    "Offline Smoke Demo",
    "Offline Final Readiness Review",
)

TESTING_EVIDENCE = (
    ("final readiness test", "37 passed"),
    ("trading tests", "4013 passed"),
    ("unit tests", "4402 passed"),
    ("git diff --check", "OK"),
)

COMMANDS = (
    (
        "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_smoke_demo.py -q",
        "Valide la smoke demo offline.",
    ),
    (
        "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_final_readiness_review.py -q",
        "Valide la readiness finale offline.",
    ),
    ("python -m pytest tests/unit/ -q", "Lance la suite unitaire complete."),
)

SAFETY_RULES = (
    "ne jamais connecter de broker reel",
    "ne jamais configurer de cle API",
    "ne jamais lancer d'ordre reel",
    "ne jamais utiliser comme conseil financier",
    "ne jamais ajouter data/",
    "ne jamais faire git add .",
)

LIMITATIONS = (
    "strategies simples seulement",
    "donnees synthetiques ou CSV string en memoire",
    "pas de donnees reelles automatisees",
    "pas de broker connecte",
    "pas de persistance reelle",
    "pas d'interface utilisateur",
    "pas de rentabilite validee",
)

NON_GOALS = (
    "pas de trading reel",
    "pas de broker reel",
    "pas d'ordre reel",
    "pas de preuve de rentabilite",
    "pas de conseil financier",
    "pas de paper broker connecte",
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
    data: AGIcoreTradingV1OfflineReleasePackageInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineReleasePackageInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineReleasePackageInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineReleasePackageInput)}
    return AGIcoreTradingV1OfflineReleasePackageInput(**{key: value for key, value in dict(data).items() if key in allowed})


def validate_agicore_trading_v1_offline_release_package_input(
    data: AGIcoreTradingV1OfflineReleasePackageInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.package_id and assert_agicore_trading_v1_offline_release_package_boundaries(payload))


def build_release_package_context(
    data: AGIcoreTradingV1OfflineReleasePackageInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineReleasePackageContext:
    _coerce_input(data)
    return AGIcoreTradingV1OfflineReleasePackageContext(
        title="AGIcore Trading v1 Offline Release Package",
        status="offline/sandbox local release package only",
        next_step="AGIcore Trading v1 Offline Release Package Review",
    )


def _documents(data: AGIcoreTradingV1OfflineReleasePackageInput | None) -> tuple[AGIcoreTradingV1OfflineReleasePackageDocument, ...]:
    if data and data.force_documents_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineReleasePackageDocument(name) for name in DOCUMENTS)


def _capabilities(data: AGIcoreTradingV1OfflineReleasePackageInput | None) -> tuple[AGIcoreTradingV1OfflineReleasePackageCapability, ...]:
    if data and data.force_capabilities_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineReleasePackageCapability(name) for name in CAPABILITIES)


def _testing_evidence(
    data: AGIcoreTradingV1OfflineReleasePackageInput | None,
) -> tuple[AGIcoreTradingV1OfflineReleasePackageTestingEvidence, ...]:
    if data and data.force_testing_evidence_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineReleasePackageTestingEvidence(name, result) for name, result in TESTING_EVIDENCE)


def _commands(data: AGIcoreTradingV1OfflineReleasePackageInput | None) -> tuple[AGIcoreTradingV1OfflineReleasePackageCommand, ...]:
    if data and data.force_commands_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineReleasePackageCommand(command, description) for command, description in COMMANDS)


def _safety_rules(data: AGIcoreTradingV1OfflineReleasePackageInput | None) -> tuple[AGIcoreTradingV1OfflineReleasePackageSafetyRule, ...]:
    if data and data.force_safety_language_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineReleasePackageSafetyRule(text) for text in SAFETY_RULES)


def _limitations(
    data: AGIcoreTradingV1OfflineReleasePackageInput | None,
) -> tuple[AGIcoreTradingV1OfflineReleasePackageKnownLimitation, ...]:
    if data and data.force_limitations_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineReleasePackageKnownLimitation(text) for text in LIMITATIONS)


def _non_goals() -> tuple[AGIcoreTradingV1OfflineReleasePackageNonGoal, ...]:
    return tuple(AGIcoreTradingV1OfflineReleasePackageNonGoal(text) for text in NON_GOALS)


def build_release_package_summary_section() -> str:
    return "\n".join(
        (
            "## Conclusion",
            "",
            "- AGIcore Trading v1 Offline est utilisable localement en sandbox",
            "- pas pret pour trading reel",
            "- pas de broker reel",
            "- pas d'ordre reel",
            "- pas de preuve de rentabilite",
            "- pas de conseil financier",
        )
    )


def build_release_package_documents_section(
    documents: tuple[AGIcoreTradingV1OfflineReleasePackageDocument, ...],
) -> str:
    lines = ["## Documents inclus", ""]
    lines.extend(f"- {document.name}" for document in documents if document.included)
    return "\n".join(lines)


def build_release_package_capabilities_section(
    capabilities: tuple[AGIcoreTradingV1OfflineReleasePackageCapability, ...],
) -> str:
    lines = ["## Capacites livrees", ""]
    lines.extend(f"- {capability.name}" for capability in capabilities if capability.delivered)
    return "\n".join(lines)


def build_release_package_testing_evidence_section(
    testing_evidence: tuple[AGIcoreTradingV1OfflineReleasePackageTestingEvidence, ...],
) -> str:
    lines = ["## Preuves de tests", ""]
    lines.extend(f"- {evidence.name} : {evidence.result}" for evidence in testing_evidence if evidence.validated)
    return "\n".join(lines)


def build_release_package_commands_section(
    commands: tuple[AGIcoreTradingV1OfflineReleasePackageCommand, ...],
) -> str:
    lines = ["## Commandes principales", ""]
    lines.extend(f"- `{command.command}` : {command.description}" for command in commands)
    return "\n".join(lines)


def build_release_package_safety_rules_section(
    safety_rules: tuple[AGIcoreTradingV1OfflineReleasePackageSafetyRule, ...],
) -> str:
    lines = ["## Regles de securite", ""]
    lines.extend(f"- {rule.text}" for rule in safety_rules if rule.explicit)
    return "\n".join(lines)


def build_release_package_known_limitations_section(
    limitations: tuple[AGIcoreTradingV1OfflineReleasePackageKnownLimitation, ...],
) -> str:
    lines = ["## Limites connues", ""]
    lines.extend(f"- {limitation.text}" for limitation in limitations if limitation.documented)
    return "\n".join(lines)


def build_release_package_non_goals_section(non_goals: tuple[AGIcoreTradingV1OfflineReleasePackageNonGoal, ...]) -> str:
    lines = ["## Non-goals", ""]
    lines.extend(f"- {non_goal.text}" for non_goal in non_goals if non_goal.explicit)
    return "\n".join(lines)


def build_release_package_next_steps_section(context: AGIcoreTradingV1OfflineReleasePackageContext) -> str:
    return f"## Prochaine etape suggeree\n\n{context.next_step}"


def render_agicore_trading_v1_offline_release_package_markdown(
    context: AGIcoreTradingV1OfflineReleasePackageContext,
    documents: tuple[AGIcoreTradingV1OfflineReleasePackageDocument, ...],
    capabilities: tuple[AGIcoreTradingV1OfflineReleasePackageCapability, ...],
    testing_evidence: tuple[AGIcoreTradingV1OfflineReleasePackageTestingEvidence, ...],
    commands: tuple[AGIcoreTradingV1OfflineReleasePackageCommand, ...],
    safety_rules: tuple[AGIcoreTradingV1OfflineReleasePackageSafetyRule, ...],
    limitations: tuple[AGIcoreTradingV1OfflineReleasePackageKnownLimitation, ...],
    non_goals: tuple[AGIcoreTradingV1OfflineReleasePackageNonGoal, ...],
) -> str:
    sections = [
        f"# {context.title}",
        "## Statut\n\n" + context.status,
        build_release_package_summary_section(),
        build_release_package_documents_section(documents),
        build_release_package_capabilities_section(capabilities),
        build_release_package_testing_evidence_section(testing_evidence),
        build_release_package_commands_section(commands),
        build_release_package_safety_rules_section(safety_rules),
        build_release_package_known_limitations_section(limitations),
        build_release_package_non_goals_section(non_goals),
        build_release_package_next_steps_section(context),
    ]
    return "\n\n".join(sections) + "\n"


def validate_release_package_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Release Package",
        "offline/sandbox local release package only",
        "AGIcore Trading v1 Offline est utilisable localement en sandbox",
        "pas pret pour trading reel",
        "pas de broker reel",
        "pas d'ordre reel",
        "pas de preuve de rentabilite",
        "pas de conseil financier",
        "AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES.md",
        "AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE.md",
        "AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK.md",
        "AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW.md",
        "CSV Replay Input v1",
        "Synthetic Market Scenario v1",
        "Strategy Replay Engine v1",
        "Simulated Broker Stub v1",
        "Risk Guard Enforcement v1",
        "Journal Writer v1",
        "Offline Report Markdown JSON v1",
        "Offline Smoke Demo",
        "Offline Final Readiness Review",
        "final readiness test : 37 passed",
        "trading tests : 4013 passed",
        "unit tests : 4402 passed",
        "git diff --check : OK",
        "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_smoke_demo.py -q",
        "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_final_readiness_review.py -q",
        "python -m pytest tests/unit/ -q",
        "ne jamais connecter de broker reel",
        "ne jamais configurer de cle API",
        "ne jamais lancer d'ordre reel",
        "ne jamais utiliser comme conseil financier",
        "ne jamais ajouter data/",
        "ne jamais faire git add .",
        "strategies simples seulement",
        "donnees synthetiques ou CSV string en memoire",
        "pas de donnees reelles automatisees",
        "pas de broker connecte",
        "pas de persistance reelle",
        "pas d'interface utilisateur",
        "pas de rentabilite validee",
        "AGIcore Trading v1 Offline Release Package Review",
    )
    return all(item in markdown for item in required)


def validate_release_package_safety_language(markdown: str) -> bool:
    return all(item in markdown for item in SAFETY_RULES)


def validate_release_package_no_overclaims(markdown: str) -> bool:
    forbidden = (
        "live_trading_ready: true",
        "real_broker_ready: true",
        "real_order_execution: true",
        "paper_broker_connected: true",
        "profitability_proven: true",
        "financial_advice: true",
        "ready for live trading",
        "profitability proven",
    )
    lowered = markdown.lower()
    return all(item not in lowered for item in forbidden)


def _boundary_risks(data: AGIcoreTradingV1OfflineReleasePackageInput | None) -> tuple[Risk, ...]:
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


def assert_agicore_trading_v1_offline_release_package_boundaries(
    data: AGIcoreTradingV1OfflineReleasePackageInput | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def detect_agicore_trading_v1_offline_release_package_risks(
    data: AGIcoreTradingV1OfflineReleasePackageInput | Mapping[str, Any] | None,
    markdown: str = "",
    documents: tuple[AGIcoreTradingV1OfflineReleasePackageDocument, ...] = (),
    capabilities: tuple[AGIcoreTradingV1OfflineReleasePackageCapability, ...] = (),
    testing_evidence: tuple[AGIcoreTradingV1OfflineReleasePackageTestingEvidence, ...] = (),
    commands: tuple[AGIcoreTradingV1OfflineReleasePackageCommand, ...] = (),
    safety_rules: tuple[AGIcoreTradingV1OfflineReleasePackageSafetyRule, ...] = (),
    limitations: tuple[AGIcoreTradingV1OfflineReleasePackageKnownLimitation, ...] = (),
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    risks: list[Risk] = []
    if payload is None:
        risks.append(Risk.RELEASE_PACKAGE_INPUT_MISSING)
    if len(documents) != len(DOCUMENTS):
        risks.append(Risk.RELEASE_PACKAGE_DOCUMENTS_MISSING)
    if len(capabilities) != len(CAPABILITIES):
        risks.append(Risk.RELEASE_PACKAGE_CAPABILITIES_MISSING)
    if len(testing_evidence) != len(TESTING_EVIDENCE):
        risks.append(Risk.RELEASE_PACKAGE_TESTING_EVIDENCE_MISSING)
    if len(commands) != len(COMMANDS):
        risks.append(Risk.RELEASE_PACKAGE_COMMANDS_MISSING)
    if len(safety_rules) != len(SAFETY_RULES) or (markdown and not validate_release_package_safety_language(markdown)):
        risks.append(Risk.RELEASE_PACKAGE_SAFETY_LANGUAGE_MISSING)
    if len(limitations) != len(LIMITATIONS):
        risks.append(Risk.RELEASE_PACKAGE_LIMITATIONS_MISSING)
    if payload and payload.force_live_trading_overclaim:
        risks.append(Risk.LIVE_TRADING_READINESS_OVERCLAIM)
    if payload and payload.force_real_broker_overclaim:
        risks.append(Risk.REAL_BROKER_READINESS_OVERCLAIM)
    if payload and payload.force_real_order_overclaim:
        risks.append(Risk.REAL_ORDER_EXECUTION_OVERCLAIM)
    if payload and payload.force_paper_broker_overclaim:
        risks.append(Risk.PAPER_BROKER_CONNECTION_OVERCLAIM)
    if payload and payload.force_profitability_overclaim:
        risks.append(Risk.PROFITABILITY_PROOF_OVERCLAIM)
    if payload and payload.force_financial_advice_overclaim:
        risks.append(Risk.FINANCIAL_ADVICE_OVERCLAIM)
    if markdown and not validate_release_package_no_overclaims(markdown):
        lowered = markdown.lower()
        if "live_trading_ready: true" in lowered:
            risks.append(Risk.LIVE_TRADING_READINESS_OVERCLAIM)
        if "real_broker_ready: true" in lowered:
            risks.append(Risk.REAL_BROKER_READINESS_OVERCLAIM)
        if "real_order_execution: true" in lowered:
            risks.append(Risk.REAL_ORDER_EXECUTION_OVERCLAIM)
        if "paper_broker_connected: true" in lowered:
            risks.append(Risk.PAPER_BROKER_CONNECTION_OVERCLAIM)
        if "profitability_proven: true" in lowered:
            risks.append(Risk.PROFITABILITY_PROOF_OVERCLAIM)
        if "financial_advice: true" in lowered:
            risks.append(Risk.FINANCIAL_ADVICE_OVERCLAIM)
    risks.extend(_boundary_risks(payload))
    return _dedupe(risks)


def compute_agicore_trading_v1_offline_release_package_score(
    data: AGIcoreTradingV1OfflineReleasePackageInput | Mapping[str, Any] | None,
    markdown: str,
    documents: tuple[AGIcoreTradingV1OfflineReleasePackageDocument, ...],
    capabilities: tuple[AGIcoreTradingV1OfflineReleasePackageCapability, ...],
    testing_evidence: tuple[AGIcoreTradingV1OfflineReleasePackageTestingEvidence, ...],
    commands: tuple[AGIcoreTradingV1OfflineReleasePackageCommand, ...],
    safety_rules: tuple[AGIcoreTradingV1OfflineReleasePackageSafetyRule, ...],
    limitations: tuple[AGIcoreTradingV1OfflineReleasePackageKnownLimitation, ...],
    non_goals: tuple[AGIcoreTradingV1OfflineReleasePackageNonGoal, ...],
    risks: tuple[Risk, ...],
) -> AGIcoreTradingV1OfflineReleasePackageScore:
    payload = _coerce_input(data)
    input_score = 100 if validate_agicore_trading_v1_offline_release_package_input(payload) else 0
    document_score = 100 if len(documents) == len(DOCUMENTS) else 0
    capability_score = 100 if len(capabilities) == len(CAPABILITIES) else 0
    testing_score = 100 if len(testing_evidence) == len(TESTING_EVIDENCE) else 0
    command_score = 100 if len(commands) == len(COMMANDS) else 0
    safety_score = 100 if len(safety_rules) == len(SAFETY_RULES) and validate_release_package_safety_language(markdown) else 0
    limitation_score = 100 if len(limitations) == len(LIMITATIONS) else 0
    non_goal_score = 100 if len(non_goals) == len(NON_GOALS) else 0
    overclaim_score = 100 if validate_release_package_no_overclaims(markdown) and not {
        Risk.LIVE_TRADING_READINESS_OVERCLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM,
        Risk.PAPER_BROKER_CONNECTION_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM,
    } & set(risks) else 0
    boundary_score = 100 if not _boundary_risks(payload) else 0
    overall = min(
        input_score,
        document_score,
        capability_score,
        testing_score,
        command_score,
        safety_score,
        limitation_score,
        non_goal_score,
        overclaim_score,
        boundary_score,
    )
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineReleasePackageScore(
        overall_score=overall,
        input_score=input_score,
        document_score=document_score,
        capability_score=capability_score,
        testing_evidence_score=testing_score,
        command_score=command_score,
        safety_score=safety_score,
        limitation_score=limitation_score,
        non_goal_score=non_goal_score,
        overclaim_score=overclaim_score,
        boundary_score=boundary_score,
    )


def generate_agicore_trading_v1_offline_release_package_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.RELEASE_PACKAGE_INPUT_MISSING: Recommendation.PROVIDE_RELEASE_PACKAGE_INPUT,
        Risk.RELEASE_PACKAGE_DOCUMENTS_MISSING: Recommendation.RESTORE_RELEASE_PACKAGE_DOCUMENTS,
        Risk.RELEASE_PACKAGE_CAPABILITIES_MISSING: Recommendation.RESTORE_RELEASE_PACKAGE_CAPABILITIES,
        Risk.RELEASE_PACKAGE_TESTING_EVIDENCE_MISSING: Recommendation.RESTORE_RELEASE_PACKAGE_TESTING_EVIDENCE,
        Risk.RELEASE_PACKAGE_COMMANDS_MISSING: Recommendation.RESTORE_RELEASE_PACKAGE_COMMANDS,
        Risk.RELEASE_PACKAGE_SAFETY_LANGUAGE_MISSING: Recommendation.RESTORE_RELEASE_PACKAGE_SAFETY_LANGUAGE,
        Risk.RELEASE_PACKAGE_LIMITATIONS_MISSING: Recommendation.RESTORE_RELEASE_PACKAGE_LIMITATIONS,
        Risk.LIVE_TRADING_READINESS_OVERCLAIM: Recommendation.REMOVE_LIVE_TRADING_READINESS_CLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM: Recommendation.REMOVE_REAL_BROKER_READINESS_CLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM: Recommendation.REMOVE_REAL_ORDER_EXECUTION_CLAIM,
        Risk.PAPER_BROKER_CONNECTION_OVERCLAIM: Recommendation.REMOVE_PAPER_BROKER_CONNECTION_CLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM: Recommendation.REMOVE_PROFITABILITY_PROOF_CLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM: Recommendation.REMOVE_FINANCIAL_ADVICE_CLAIM,
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
        recommendations.append(Recommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE
    if Risk.RELEASE_PACKAGE_INPUT_MISSING in risks:
        return Decision.REQUIRE_RELEASE_PACKAGE_INPUT_FIXES
    if Risk.RELEASE_PACKAGE_DOCUMENTS_MISSING in risks:
        return Decision.REQUIRE_RELEASE_PACKAGE_DOCUMENT_FIXES
    if Risk.RELEASE_PACKAGE_CAPABILITIES_MISSING in risks:
        return Decision.REQUIRE_RELEASE_PACKAGE_CAPABILITY_FIXES
    if Risk.RELEASE_PACKAGE_TESTING_EVIDENCE_MISSING in risks:
        return Decision.REQUIRE_RELEASE_PACKAGE_TESTING_EVIDENCE_FIXES
    if Risk.RELEASE_PACKAGE_COMMANDS_MISSING in risks:
        return Decision.REQUIRE_RELEASE_PACKAGE_COMMAND_FIXES
    if Risk.RELEASE_PACKAGE_SAFETY_LANGUAGE_MISSING in risks:
        return Decision.REQUIRE_RELEASE_PACKAGE_SAFETY_FIXES
    if Risk.RELEASE_PACKAGE_LIMITATIONS_MISSING in risks:
        return Decision.REQUIRE_RELEASE_PACKAGE_LIMITATION_FIXES
    overclaim_risks = {
        Risk.LIVE_TRADING_READINESS_OVERCLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM,
        Risk.PAPER_BROKER_CONNECTION_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM,
    }
    if set(risks) & overclaim_risks:
        return Decision.REQUIRE_RELEASE_PACKAGE_NO_OVERCLAIM_FIXES
    return Decision.BLOCK_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE


def _state_for(data: AGIcoreTradingV1OfflineReleasePackageInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW
    return State.AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_BLOCKED


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


def render_agicore_trading_v1_offline_release_package_json_report(
    result: AGIcoreTradingV1OfflineReleasePackageResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineReleasePackageResult):
        payload = {
            "schema": "agicore_trading_v1_offline_release_package",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload_value(result.context),
            "documents": _payload_value(result.documents),
            "capabilities": _payload_value(result.capabilities),
            "testing_evidence": _payload_value(result.testing_evidence),
            "commands": _payload_value(result.commands),
            "safety_rules": _payload_value(result.safety_rules),
            "known_limitations": _payload_value(result.known_limitations),
            "non_goals": _payload_value(result.non_goals),
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


def build_agicore_trading_v1_offline_release_package(
    data: AGIcoreTradingV1OfflineReleasePackageInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineReleasePackageResult:
    payload = _coerce_input(data)
    context = build_release_package_context(payload)
    documents = _documents(payload)
    capabilities = _capabilities(payload)
    testing_evidence = _testing_evidence(payload)
    commands = _commands(payload)
    safety_rules = _safety_rules(payload)
    limitations = _limitations(payload)
    non_goals = _non_goals()
    markdown = render_agicore_trading_v1_offline_release_package_markdown(
        context,
        documents,
        capabilities,
        testing_evidence,
        commands,
        safety_rules,
        limitations,
        non_goals,
    )
    if payload and payload.force_live_trading_overclaim:
        markdown += "\nlive_trading_ready: true\n"
    if payload and payload.force_real_broker_overclaim:
        markdown += "\nreal_broker_ready: true\n"
    if payload and payload.force_real_order_overclaim:
        markdown += "\nreal_order_execution: true\n"
    if payload and payload.force_paper_broker_overclaim:
        markdown += "\npaper_broker_connected: true\n"
    if payload and payload.force_profitability_overclaim:
        markdown += "\nprofitability_proven: true\n"
    if payload and payload.force_financial_advice_overclaim:
        markdown += "\nfinancial_advice: true\n"
    risks = detect_agicore_trading_v1_offline_release_package_risks(
        payload,
        markdown,
        documents,
        capabilities,
        testing_evidence,
        commands,
        safety_rules,
        limitations,
    )
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_release_package_score(
        payload,
        markdown,
        documents,
        capabilities,
        testing_evidence,
        commands,
        safety_rules,
        limitations,
        non_goals,
        risks,
    )
    recommendations = generate_agicore_trading_v1_offline_release_package_recommendations(risks)
    base = AGIcoreTradingV1OfflineReleasePackageResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        context=context,
        documents=documents,
        capabilities=capabilities,
        testing_evidence=testing_evidence,
        commands=commands,
        safety_rules=safety_rules,
        known_limitations=limitations,
        non_goals=non_goals,
        report=None,
    )
    report = AGIcoreTradingV1OfflineReleasePackageReport(
        markdown=markdown,
        json=render_agicore_trading_v1_offline_release_package_json_report(base),
    )
    return AGIcoreTradingV1OfflineReleasePackageResult(**{**base.__dict__, "report": report})
