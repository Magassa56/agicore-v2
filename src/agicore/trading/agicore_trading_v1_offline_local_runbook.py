"""AGIcore Trading v1 offline local runbook builder."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_local_runbook_models import (
    AGIcoreTradingV1OfflineLocalRunbookCommand,
    AGIcoreTradingV1OfflineLocalRunbookContext,
    AGIcoreTradingV1OfflineLocalRunbookDecision,
    AGIcoreTradingV1OfflineLocalRunbookDiagnosticRule,
    AGIcoreTradingV1OfflineLocalRunbookGitRule,
    AGIcoreTradingV1OfflineLocalRunbookInput,
    AGIcoreTradingV1OfflineLocalRunbookKnownLimitation,
    AGIcoreTradingV1OfflineLocalRunbookRecommendation,
    AGIcoreTradingV1OfflineLocalRunbookReport,
    AGIcoreTradingV1OfflineLocalRunbookResult,
    AGIcoreTradingV1OfflineLocalRunbookRisk,
    AGIcoreTradingV1OfflineLocalRunbookSafetyRule,
    AGIcoreTradingV1OfflineLocalRunbookScore,
    AGIcoreTradingV1OfflineLocalRunbookSection,
    AGIcoreTradingV1OfflineLocalRunbookState,
)


Risk = AGIcoreTradingV1OfflineLocalRunbookRisk
Recommendation = AGIcoreTradingV1OfflineLocalRunbookRecommendation
Decision = AGIcoreTradingV1OfflineLocalRunbookDecision
State = AGIcoreTradingV1OfflineLocalRunbookState

SAFETY_RULES = (
    "pas de trading reel",
    "pas de broker reel",
    "pas d'Alpaca reel",
    "pas d'ordre reel",
    "pas d'acces compte reel",
    "pas de mutation position reelle",
    "pas de lecture data/",
    "pas d'ecriture data/",
    "pas de reseau",
    "pas de cle API",
    "pas de preuve de rentabilite",
    "pas de conseil financier",
)

SYNC_COMMANDS = (
    ("git switch main", "Se placer sur main avant synchronisation."),
    ("git fetch origin", "Recuperer les references distantes."),
    ("git pull origin main", "Synchroniser main local."),
    ("git status --short", "Verifier que seul data/ non suivi apparait."),
)

TEST_COMMANDS = (
    (
        "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_smoke_demo.py -q",
        "Valide la smoke demo offline V1.",
    ),
    (
        "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_smoke_demo_review.py -q",
        "Valide la review de smoke demo offline V1.",
    ),
    (
        "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_sandbox_usage_guide.py -q",
        "Valide le guide sandbox offline V1.",
    ),
    ("python -m pytest tests/unit/ -q", "Lance la suite unitaire complete."),
)

INTERPRETATION_LINES = (
    "APPROVE signifie seulement offline/sandbox OK",
    "score 100 ne prouve pas une rentabilite",
    "risks [] ne signifie pas absence de risque financier reel",
    "broker preview est simule uniquement",
    "read-only decision n'est pas un ordre reel",
)

DIAGNOSTIC_RULES = (
    ("ModuleNotFoundError", "verifier PYTHONPATH=src"),
    ("test flaky", "relancer le test cible puis tests/unit/"),
    ("BOM UTF-8", "corriger l'encodage puis relancer tests/unit/"),
    ("git status montre autre chose que data/", "STOP et analyser avant commit"),
    ("data/ apparait", "normal si non suivi, ne jamais l'ajouter"),
)

GIT_RULES = (
    "ne jamais faire git add .",
    "ajouter seulement les fichiers autorises",
    "verifier git diff --cached --name-only",
    "commit apres tests verts",
    "push branche dediee",
)

LIMITATIONS = (
    "strategies simples seulement",
    "donnees synthetiques ou CSV string en memoire",
    "pas de vraie persistance",
    "pas de vraie interface utilisateur",
    "pas de paper broker connecte",
    "pas de donnees reelles automatisees",
    "pas de rentabilite validee",
)

STOP_RULES = (
    "arreter si fichier hors perimetre modifie",
    "arreter si data/ est staged",
    "arreter si reseau/broker/secret apparait",
    "arreter si la formulation laisse croire a du trading reel",
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
    data: AGIcoreTradingV1OfflineLocalRunbookInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineLocalRunbookInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineLocalRunbookInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineLocalRunbookInput)}
    return AGIcoreTradingV1OfflineLocalRunbookInput(**{key: value for key, value in dict(data).items() if key in allowed})


def validate_agicore_trading_v1_offline_local_runbook_input(
    data: AGIcoreTradingV1OfflineLocalRunbookInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.runbook_id and assert_agicore_trading_v1_offline_local_runbook_boundaries(payload))


def build_local_runbook_context(
    data: AGIcoreTradingV1OfflineLocalRunbookInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineLocalRunbookContext:
    _coerce_input(data)
    return AGIcoreTradingV1OfflineLocalRunbookContext(
        title="AGIcore Trading v1 Offline Local Runbook",
        status="offline/sandbox local runbook only",
        next_step="AGIcore Trading v1 Offline Final Readiness Review",
    )


def _safety_rules(data: AGIcoreTradingV1OfflineLocalRunbookInput | None) -> tuple[AGIcoreTradingV1OfflineLocalRunbookSafetyRule, ...]:
    if data and data.force_safety_language_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineLocalRunbookSafetyRule(text) for text in SAFETY_RULES)


def _sync_commands(data: AGIcoreTradingV1OfflineLocalRunbookInput | None) -> tuple[AGIcoreTradingV1OfflineLocalRunbookCommand, ...]:
    if data and data.force_sync_commands_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineLocalRunbookCommand(command, description) for command, description in SYNC_COMMANDS)


def _test_commands(data: AGIcoreTradingV1OfflineLocalRunbookInput | None) -> tuple[AGIcoreTradingV1OfflineLocalRunbookCommand, ...]:
    if data and data.force_test_commands_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineLocalRunbookCommand(command, description) for command, description in TEST_COMMANDS)


def _diagnostic_rules(
    data: AGIcoreTradingV1OfflineLocalRunbookInput | None,
) -> tuple[AGIcoreTradingV1OfflineLocalRunbookDiagnosticRule, ...]:
    if data and data.force_diagnostics_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineLocalRunbookDiagnosticRule(symptom, action) for symptom, action in DIAGNOSTIC_RULES)


def _git_rules(data: AGIcoreTradingV1OfflineLocalRunbookInput | None) -> tuple[AGIcoreTradingV1OfflineLocalRunbookGitRule, ...]:
    if data and data.force_git_rules_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineLocalRunbookGitRule(text) for text in GIT_RULES)


def _limitations(data: AGIcoreTradingV1OfflineLocalRunbookInput | None) -> tuple[AGIcoreTradingV1OfflineLocalRunbookKnownLimitation, ...]:
    return tuple(AGIcoreTradingV1OfflineLocalRunbookKnownLimitation(text) for text in LIMITATIONS)


def build_local_runbook_safety_section(
    safety_rules: tuple[AGIcoreTradingV1OfflineLocalRunbookSafetyRule, ...],
) -> str:
    lines = ["## Avertissement securite", ""]
    lines.extend(f"- {rule.text}" for rule in safety_rules)
    return "\n".join(lines)


def build_local_runbook_prerequisites_section() -> str:
    return "\n".join(
        (
            "## 1. Prerequis",
            "",
            "- depot local propre",
            "- branche main a jour",
            "- environnement Python local",
            "- dependances installees",
            "- aucune cle API configuree",
            "- aucun broker connecte",
        )
    )


def build_local_runbook_sync_section(
    sync_commands: tuple[AGIcoreTradingV1OfflineLocalRunbookCommand, ...],
) -> str:
    lines = ["## 2. Synchronisation propre", ""]
    lines.extend(f"- `{command.command}` : {command.description}" for command in sync_commands)
    lines.extend(("", "Resultat attendu : seulement `?? data/`."))
    return "\n".join(lines)


def build_local_runbook_tests_section(
    test_commands: tuple[AGIcoreTradingV1OfflineLocalRunbookCommand, ...],
) -> str:
    lines = ["## 3. Tests recommandes", ""]
    lines.extend(f"- `{command.command}` : {command.description}" for command in test_commands)
    return "\n".join(lines)


def build_local_runbook_smoke_demo_section(
    data: AGIcoreTradingV1OfflineLocalRunbookInput | Mapping[str, Any] | None,
) -> str:
    payload = _coerce_input(data)
    if payload and payload.force_smoke_demo_missing:
        return ""
    return "\n".join(
        (
            "## 4. Smoke demo en memoire",
            "",
            "Utiliser uniquement `PYTHONPATH=src`.",
            "",
            "```python",
            "from agicore.trading.agicore_trading_v1_offline_smoke_demo import (",
            "    run_agicore_trading_v1_offline_smoke_demo,",
            ")",
            "",
            "result = run_agicore_trading_v1_offline_smoke_demo()",
            "print(result.decision)",
            "print(result.state)",
            "print(result.score.overall_score)",
            "print(result.risks)",
            "print(result.recommendations)",
            "```",
        )
    )


def build_local_runbook_interpretation_section(
    data: AGIcoreTradingV1OfflineLocalRunbookInput | Mapping[str, Any] | None,
) -> str:
    payload = _coerce_input(data)
    if payload and payload.force_interpretation_missing:
        return ""
    lines = ["## 5. Interpretation", ""]
    lines.extend(f"- {line}" for line in INTERPRETATION_LINES)
    return "\n".join(lines)


def build_local_runbook_diagnostics_section(
    diagnostic_rules: tuple[AGIcoreTradingV1OfflineLocalRunbookDiagnosticRule, ...],
) -> str:
    lines = ["## 6. Diagnostic", ""]
    lines.extend(f"- {rule.symptom} : {rule.action}" for rule in diagnostic_rules)
    return "\n".join(lines)


def build_local_runbook_git_rules_section(
    git_rules: tuple[AGIcoreTradingV1OfflineLocalRunbookGitRule, ...],
) -> str:
    lines = ["## 7. Regles Git", ""]
    lines.extend(f"- {rule.text}" for rule in git_rules)
    return "\n".join(lines)


def build_local_runbook_known_limitations_section(
    limitations: tuple[AGIcoreTradingV1OfflineLocalRunbookKnownLimitation, ...],
) -> str:
    lines = ["## 8. Limites connues", ""]
    lines.extend(f"- {limitation.text}" for limitation in limitations)
    return "\n".join(lines)


def build_local_runbook_stop_procedure_section() -> str:
    lines = ["## 9. Procedure STOP", ""]
    lines.extend(f"- {rule}" for rule in STOP_RULES)
    return "\n".join(lines)


def build_local_runbook_next_steps_section(context: AGIcoreTradingV1OfflineLocalRunbookContext) -> str:
    return f"## Prochaine etape suggeree\n\n{context.next_step}"


def render_agicore_trading_v1_offline_local_runbook_markdown(
    context: AGIcoreTradingV1OfflineLocalRunbookContext,
    safety_rules: tuple[AGIcoreTradingV1OfflineLocalRunbookSafetyRule, ...],
    sync_commands: tuple[AGIcoreTradingV1OfflineLocalRunbookCommand, ...],
    test_commands: tuple[AGIcoreTradingV1OfflineLocalRunbookCommand, ...],
    diagnostic_rules: tuple[AGIcoreTradingV1OfflineLocalRunbookDiagnosticRule, ...],
    git_rules: tuple[AGIcoreTradingV1OfflineLocalRunbookGitRule, ...],
    limitations: tuple[AGIcoreTradingV1OfflineLocalRunbookKnownLimitation, ...],
    data: AGIcoreTradingV1OfflineLocalRunbookInput | Mapping[str, Any] | None = None,
) -> str:
    sections = [
        f"# {context.title}",
        "## Statut\n\n" + context.status,
        build_local_runbook_safety_section(safety_rules),
        build_local_runbook_prerequisites_section(),
        build_local_runbook_sync_section(sync_commands),
        build_local_runbook_tests_section(test_commands),
        build_local_runbook_smoke_demo_section(data),
        build_local_runbook_interpretation_section(data),
        build_local_runbook_diagnostics_section(diagnostic_rules),
        build_local_runbook_git_rules_section(git_rules),
        build_local_runbook_known_limitations_section(limitations),
        build_local_runbook_stop_procedure_section(),
        build_local_runbook_next_steps_section(context),
    ]
    return "\n\n".join(section for section in sections if section) + "\n"


def validate_local_runbook_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Local Runbook",
        "offline/sandbox local runbook only",
        "pas de trading reel",
        "pas de broker reel",
        "pas d'Alpaca reel",
        "pas d'ordre reel",
        "pas d'acces compte reel",
        "pas de mutation position reelle",
        "pas de lecture data/",
        "pas d'ecriture data/",
        "pas de reseau",
        "pas de cle API",
        "pas de preuve de rentabilite",
        "pas de conseil financier",
        "depot local propre",
        "branche main a jour",
        "git switch main",
        "git fetch origin",
        "git pull origin main",
        "git status --short",
        "seulement `?? data/`",
        "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_smoke_demo.py -q",
        "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_smoke_demo_review.py -q",
        "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_sandbox_usage_guide.py -q",
        "python -m pytest tests/unit/ -q",
        "PYTHONPATH=src",
        "run_agicore_trading_v1_offline_smoke_demo",
        "APPROVE signifie seulement offline/sandbox OK",
        "score 100 ne prouve pas une rentabilite",
        "read-only decision n'est pas un ordre reel",
        "ModuleNotFoundError",
        "verifier PYTHONPATH=src",
        "git status montre autre chose que data/",
        "ne jamais faire git add .",
        "git diff --cached --name-only",
        "strategies simples seulement",
        "arreter si data/ est staged",
        "AGIcore Trading v1 Offline Final Readiness Review",
    )
    return all(item in markdown for item in required)


def validate_local_runbook_safety_language(markdown: str) -> bool:
    return all(item in markdown for item in SAFETY_RULES)


def validate_local_runbook_git_safety_rules(markdown: str) -> bool:
    return all(item in markdown for item in GIT_RULES) and "arreter si data/ est staged" in markdown


def validate_local_runbook_no_overclaims(markdown: str) -> bool:
    forbidden = (
        "live_trading_ready: true",
        "real_broker_ready: true",
        "real_order_execution: true",
        "profitability_proven: true",
        "financial_advice: true",
        "ready for live trading",
        "profitability proven",
    )
    lowered = markdown.lower()
    return all(item not in lowered for item in forbidden)


def _boundary_risks(data: AGIcoreTradingV1OfflineLocalRunbookInput | None) -> tuple[Risk, ...]:
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


def assert_agicore_trading_v1_offline_local_runbook_boundaries(
    data: AGIcoreTradingV1OfflineLocalRunbookInput | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def detect_agicore_trading_v1_offline_local_runbook_risks(
    data: AGIcoreTradingV1OfflineLocalRunbookInput | Mapping[str, Any] | None,
    markdown: str = "",
    sync_commands: tuple[AGIcoreTradingV1OfflineLocalRunbookCommand, ...] = (),
    test_commands: tuple[AGIcoreTradingV1OfflineLocalRunbookCommand, ...] = (),
    safety_rules: tuple[AGIcoreTradingV1OfflineLocalRunbookSafetyRule, ...] = (),
    diagnostic_rules: tuple[AGIcoreTradingV1OfflineLocalRunbookDiagnosticRule, ...] = (),
    git_rules: tuple[AGIcoreTradingV1OfflineLocalRunbookGitRule, ...] = (),
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    risks: list[Risk] = []
    if payload is None:
        risks.append(Risk.LOCAL_RUNBOOK_INPUT_MISSING)
    if len(safety_rules) != len(SAFETY_RULES) or (markdown and not validate_local_runbook_safety_language(markdown)):
        risks.append(Risk.LOCAL_RUNBOOK_SAFETY_LANGUAGE_MISSING)
    if len(sync_commands) != len(SYNC_COMMANDS):
        risks.append(Risk.LOCAL_RUNBOOK_SYNC_COMMANDS_MISSING)
    if len(test_commands) != len(TEST_COMMANDS):
        risks.append(Risk.LOCAL_RUNBOOK_TEST_COMMANDS_MISSING)
    if not markdown or "run_agicore_trading_v1_offline_smoke_demo" not in markdown:
        risks.append(Risk.LOCAL_RUNBOOK_SMOKE_DEMO_MISSING)
    if "APPROVE signifie seulement offline/sandbox OK" not in markdown:
        risks.append(Risk.LOCAL_RUNBOOK_INTERPRETATION_MISSING)
    if len(diagnostic_rules) != len(DIAGNOSTIC_RULES):
        risks.append(Risk.LOCAL_RUNBOOK_DIAGNOSTICS_MISSING)
    if len(git_rules) != len(GIT_RULES) or (markdown and not validate_local_runbook_git_safety_rules(markdown)):
        risks.append(Risk.LOCAL_RUNBOOK_GIT_RULES_MISSING)
    if payload and payload.force_live_trading_overclaim:
        risks.append(Risk.LIVE_TRADING_READINESS_OVERCLAIM)
    if payload and payload.force_real_broker_overclaim:
        risks.append(Risk.REAL_BROKER_READINESS_OVERCLAIM)
    if payload and payload.force_real_order_overclaim:
        risks.append(Risk.REAL_ORDER_EXECUTION_OVERCLAIM)
    if payload and payload.force_profitability_overclaim:
        risks.append(Risk.PROFITABILITY_PROOF_OVERCLAIM)
    if payload and payload.force_financial_advice_overclaim:
        risks.append(Risk.FINANCIAL_ADVICE_OVERCLAIM)
    risks.extend(_boundary_risks(payload))
    return _dedupe(risks)


def compute_agicore_trading_v1_offline_local_runbook_score(
    data: AGIcoreTradingV1OfflineLocalRunbookInput | Mapping[str, Any] | None,
    markdown: str,
    sync_commands: tuple[AGIcoreTradingV1OfflineLocalRunbookCommand, ...],
    test_commands: tuple[AGIcoreTradingV1OfflineLocalRunbookCommand, ...],
    safety_rules: tuple[AGIcoreTradingV1OfflineLocalRunbookSafetyRule, ...],
    diagnostic_rules: tuple[AGIcoreTradingV1OfflineLocalRunbookDiagnosticRule, ...],
    git_rules: tuple[AGIcoreTradingV1OfflineLocalRunbookGitRule, ...],
    risks: tuple[Risk, ...],
) -> AGIcoreTradingV1OfflineLocalRunbookScore:
    payload = _coerce_input(data)
    input_score = 100 if validate_agicore_trading_v1_offline_local_runbook_input(payload) else 0
    safety_score = 100 if len(safety_rules) == len(SAFETY_RULES) and validate_local_runbook_safety_language(markdown) else 0
    sync_score = 100 if len(sync_commands) == len(SYNC_COMMANDS) else 0
    test_command_score = 100 if len(test_commands) == len(TEST_COMMANDS) else 0
    smoke_demo_score = 100 if "run_agicore_trading_v1_offline_smoke_demo" in markdown and "PYTHONPATH=src" in markdown else 0
    interpretation_score = 100 if all(item in markdown for item in INTERPRETATION_LINES) else 0
    diagnostic_score = 100 if len(diagnostic_rules) == len(DIAGNOSTIC_RULES) else 0
    git_rule_score = 100 if len(git_rules) == len(GIT_RULES) and validate_local_runbook_git_safety_rules(markdown) else 0
    overclaim_score = 100 if validate_local_runbook_no_overclaims(markdown) and not {
        Risk.LIVE_TRADING_READINESS_OVERCLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM,
    } & set(risks) else 0
    boundary_score = 100 if not _boundary_risks(payload) else 0
    overall = min(
        input_score,
        safety_score,
        sync_score,
        test_command_score,
        smoke_demo_score,
        interpretation_score,
        diagnostic_score,
        git_rule_score,
        overclaim_score,
        boundary_score,
    )
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineLocalRunbookScore(
        overall_score=overall,
        input_score=input_score,
        safety_score=safety_score,
        sync_score=sync_score,
        test_command_score=test_command_score,
        smoke_demo_score=smoke_demo_score,
        interpretation_score=interpretation_score,
        diagnostic_score=diagnostic_score,
        git_rule_score=git_rule_score,
        overclaim_score=overclaim_score,
        boundary_score=boundary_score,
    )


def generate_agicore_trading_v1_offline_local_runbook_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.LOCAL_RUNBOOK_INPUT_MISSING: Recommendation.PROVIDE_LOCAL_RUNBOOK_INPUT,
        Risk.LOCAL_RUNBOOK_SAFETY_LANGUAGE_MISSING: Recommendation.RESTORE_LOCAL_RUNBOOK_SAFETY_LANGUAGE,
        Risk.LOCAL_RUNBOOK_SYNC_COMMANDS_MISSING: Recommendation.RESTORE_LOCAL_RUNBOOK_SYNC_COMMANDS,
        Risk.LOCAL_RUNBOOK_TEST_COMMANDS_MISSING: Recommendation.RESTORE_LOCAL_RUNBOOK_TEST_COMMANDS,
        Risk.LOCAL_RUNBOOK_SMOKE_DEMO_MISSING: Recommendation.RESTORE_LOCAL_RUNBOOK_SMOKE_DEMO,
        Risk.LOCAL_RUNBOOK_INTERPRETATION_MISSING: Recommendation.RESTORE_LOCAL_RUNBOOK_INTERPRETATION,
        Risk.LOCAL_RUNBOOK_DIAGNOSTICS_MISSING: Recommendation.RESTORE_LOCAL_RUNBOOK_DIAGNOSTICS,
        Risk.LOCAL_RUNBOOK_GIT_RULES_MISSING: Recommendation.RESTORE_LOCAL_RUNBOOK_GIT_RULES,
        Risk.LIVE_TRADING_READINESS_OVERCLAIM: Recommendation.REMOVE_LIVE_TRADING_READINESS_CLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM: Recommendation.REMOVE_REAL_BROKER_READINESS_CLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM: Recommendation.REMOVE_REAL_ORDER_EXECUTION_CLAIM,
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
        recommendations.append(Recommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK
    if Risk.LOCAL_RUNBOOK_INPUT_MISSING in risks:
        return Decision.REQUIRE_LOCAL_RUNBOOK_INPUT_FIXES
    if Risk.LOCAL_RUNBOOK_SAFETY_LANGUAGE_MISSING in risks:
        return Decision.REQUIRE_LOCAL_RUNBOOK_SAFETY_FIXES
    if Risk.LOCAL_RUNBOOK_SYNC_COMMANDS_MISSING in risks:
        return Decision.REQUIRE_LOCAL_RUNBOOK_SYNC_FIXES
    if Risk.LOCAL_RUNBOOK_TEST_COMMANDS_MISSING in risks:
        return Decision.REQUIRE_LOCAL_RUNBOOK_TEST_COMMAND_FIXES
    if Risk.LOCAL_RUNBOOK_SMOKE_DEMO_MISSING in risks:
        return Decision.REQUIRE_LOCAL_RUNBOOK_SMOKE_DEMO_FIXES
    if Risk.LOCAL_RUNBOOK_INTERPRETATION_MISSING in risks:
        return Decision.REQUIRE_LOCAL_RUNBOOK_INTERPRETATION_FIXES
    if Risk.LOCAL_RUNBOOK_DIAGNOSTICS_MISSING in risks:
        return Decision.REQUIRE_LOCAL_RUNBOOK_DIAGNOSTIC_FIXES
    if Risk.LOCAL_RUNBOOK_GIT_RULES_MISSING in risks:
        return Decision.REQUIRE_LOCAL_RUNBOOK_GIT_RULE_FIXES
    overclaim_risks = {
        Risk.LIVE_TRADING_READINESS_OVERCLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM,
    }
    if set(risks) & overclaim_risks:
        return Decision.REQUIRE_LOCAL_RUNBOOK_NO_OVERCLAIM_FIXES
    return Decision.BLOCK_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK


def _state_for(data: AGIcoreTradingV1OfflineLocalRunbookInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW
    return State.AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK_BLOCKED


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


def render_agicore_trading_v1_offline_local_runbook_json_report(
    result: AGIcoreTradingV1OfflineLocalRunbookResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineLocalRunbookResult):
        payload = {
            "schema": "agicore_trading_v1_offline_local_runbook",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload_value(result.context),
            "sync_commands": _payload_value(result.sync_commands),
            "test_commands": _payload_value(result.test_commands),
            "safety_rules": _payload_value(result.safety_rules),
            "diagnostic_rules": _payload_value(result.diagnostic_rules),
            "git_rules": _payload_value(result.git_rules),
            "known_limitations": _payload_value(result.known_limitations),
            "live_trading_ready": False,
            "real_broker_ready": False,
            "real_order_execution": False,
            "profitability_proven": False,
            "financial_advice": False,
        }
    else:
        payload = dict(result)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def build_agicore_trading_v1_offline_local_runbook(
    data: AGIcoreTradingV1OfflineLocalRunbookInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineLocalRunbookResult:
    payload = _coerce_input(data)
    context = build_local_runbook_context(payload)
    safety_rules = _safety_rules(payload)
    sync_commands = _sync_commands(payload)
    test_commands = _test_commands(payload)
    diagnostic_rules = _diagnostic_rules(payload)
    git_rules = _git_rules(payload)
    limitations = _limitations(payload)
    markdown = render_agicore_trading_v1_offline_local_runbook_markdown(
        context,
        safety_rules,
        sync_commands,
        test_commands,
        diagnostic_rules,
        git_rules,
        limitations,
        payload,
    )
    if payload and payload.force_live_trading_overclaim:
        markdown += "\nlive_trading_ready: true\n"
    if payload and payload.force_real_broker_overclaim:
        markdown += "\nreal_broker_ready: true\n"
    if payload and payload.force_real_order_overclaim:
        markdown += "\nreal_order_execution: true\n"
    if payload and payload.force_profitability_overclaim:
        markdown += "\nprofitability_proven: true\n"
    if payload and payload.force_financial_advice_overclaim:
        markdown += "\nfinancial_advice: true\n"
    risks = detect_agicore_trading_v1_offline_local_runbook_risks(
        payload,
        markdown,
        sync_commands,
        test_commands,
        safety_rules,
        diagnostic_rules,
        git_rules,
    )
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_local_runbook_score(
        payload,
        markdown,
        sync_commands,
        test_commands,
        safety_rules,
        diagnostic_rules,
        git_rules,
        risks,
    )
    recommendations = generate_agicore_trading_v1_offline_local_runbook_recommendations(risks)
    sections = (
        AGIcoreTradingV1OfflineLocalRunbookSection("SAFETY", build_local_runbook_safety_section(safety_rules)),
        AGIcoreTradingV1OfflineLocalRunbookSection("PREREQUISITES", build_local_runbook_prerequisites_section()),
        AGIcoreTradingV1OfflineLocalRunbookSection("SYNC", build_local_runbook_sync_section(sync_commands)),
        AGIcoreTradingV1OfflineLocalRunbookSection("TESTS", build_local_runbook_tests_section(test_commands)),
        AGIcoreTradingV1OfflineLocalRunbookSection("SMOKE_DEMO", build_local_runbook_smoke_demo_section(payload)),
        AGIcoreTradingV1OfflineLocalRunbookSection("INTERPRETATION", build_local_runbook_interpretation_section(payload)),
        AGIcoreTradingV1OfflineLocalRunbookSection("DIAGNOSTICS", build_local_runbook_diagnostics_section(diagnostic_rules)),
        AGIcoreTradingV1OfflineLocalRunbookSection("GIT_RULES", build_local_runbook_git_rules_section(git_rules)),
        AGIcoreTradingV1OfflineLocalRunbookSection("LIMITATIONS", build_local_runbook_known_limitations_section(limitations)),
        AGIcoreTradingV1OfflineLocalRunbookSection("STOP", build_local_runbook_stop_procedure_section()),
        AGIcoreTradingV1OfflineLocalRunbookSection("NEXT_STEPS", build_local_runbook_next_steps_section(context)),
    )
    base = AGIcoreTradingV1OfflineLocalRunbookResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        context=context,
        sections=sections,
        sync_commands=sync_commands,
        test_commands=test_commands,
        safety_rules=safety_rules,
        diagnostic_rules=diagnostic_rules,
        git_rules=git_rules,
        known_limitations=limitations,
        report=None,
    )
    report = AGIcoreTradingV1OfflineLocalRunbookReport(
        markdown=markdown,
        json=render_agicore_trading_v1_offline_local_runbook_json_report(base),
    )
    return AGIcoreTradingV1OfflineLocalRunbookResult(**{**base.__dict__, "report": report})
