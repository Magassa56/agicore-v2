"""Offline Autonomous System Integrity Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState
from .cognitive_adaptation_models import CognitiveLoadLevel
from .hierarchical_supervisor_models import SupervisorDecision, SupervisorOverride
from .learning_governance_models import LearningGovernanceDecision, LearningGovernanceMode
from .multi_agent_models import AgentConsensusStatus, AgentVote
from .recursive_self_evaluation_models import (
    SelfEvaluationStatus,
    SystemAutonomyRecommendation,
)
from .safe_rl_models import SafeRLStatus
from .scenario_replay_models import ReplayArenaStatus
from .strategic_memory_models import StrategicDriftSignal
from .strategic_planning_models import StrategicPlanStatus
from .system_integrity_models import (
    ModuleHealthStatus,
    ModuleIntegrityReport,
    SystemIntegrityEvent,
    SystemIntegrityInput,
    SystemIntegrityResult,
    SystemIntegrityRisk,
    SystemIntegrityStatus,
)


def evaluate_system_integrity(
    integrity_input: SystemIntegrityInput | None = None,
    **kwargs,
) -> SystemIntegrityResult:
    """Evaluate global integrity, risk accumulation and module health."""
    data = _input(integrity_input, **kwargs)
    module_reports = compute_module_health(data)
    risks = detect_system_integrity_risks(data, module_reports=module_reports)
    integrity_score = _integrity_score(module_reports, risks)
    status = _status(integrity_score, risks)
    recommended_action, actions = recommend_integrity_action(
        data,
        risks=risks,
        module_reports=module_reports,
        status=status,
    )
    event = SystemIntegrityEvent(
        status=status,
        message=f"System integrity {integrity_score}/100; status {status.value}.",
        timestamp=datetime.now(UTC),
    )
    modules_to_isolate = tuple(report.module_name for report in module_reports if report.isolate_recommended)
    return SystemIntegrityResult(
        status=status,
        integrity_score=integrity_score,
        risks=risks,
        module_reports=module_reports,
        modules_to_isolate=modules_to_isolate,
        recommended_action=recommended_action,
        recommended_actions=actions,
        events=(event,),
        summary=f"Integrity {integrity_score}/100 with {len(risks)} risk(s) and {len(modules_to_isolate)} module(s) to isolate.",
    )


def detect_system_integrity_risks(
    integrity_input: SystemIntegrityInput | None = None,
    *,
    module_reports: tuple[ModuleIntegrityReport, ...] | None = None,
    **kwargs,
) -> tuple[SystemIntegrityRisk, ...]:
    """Detect cross-layer integrity risks from available offline outputs."""
    data = _input(integrity_input, **kwargs)
    reports = module_reports or compute_module_health(data)
    risks: list[SystemIntegrityRisk] = []

    if data.self_evaluation is not None:
        if data.self_evaluation.status == SelfEvaluationStatus.CONTRADICTORY:
            risks.extend((SystemIntegrityRisk.LOGIC_CONFLICT, SystemIntegrityRisk.LAYER_CONTRADICTION))
        if data.self_evaluation.confidence_score < 50:
            risks.append(SystemIntegrityRisk.LOW_SYSTEM_CONFIDENCE)
        if data.self_evaluation.autonomy_recommendation in {
            SystemAutonomyRecommendation.FREEZE_AUTONOMY,
            SystemAutonomyRecommendation.REQUIRE_HUMAN_REVIEW,
            SystemAutonomyRecommendation.RECALIBRATE_SYSTEM,
        }:
            risks.append(SystemIntegrityRisk.AUTONOMY_UNSAFE)
        if data.self_evaluation.autonomy_recommendation == SystemAutonomyRecommendation.RECALIBRATE_SYSTEM:
            risks.append(SystemIntegrityRisk.RECALIBRATION_REQUIRED)

    if data.learning_governance is not None:
        if data.learning_governance.mode in {LearningGovernanceMode.SAFETY_LOCKDOWN, LearningGovernanceMode.FREEZE_LEARNING}:
            risks.extend((SystemIntegrityRisk.GOVERNANCE_FAILURE, SystemIntegrityRisk.SAFETY_LOCKDOWN_REQUIRED))
        if data.learning_governance.decision in {
            LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN,
            LearningGovernanceDecision.FREEZE_POLICY_UPDATE,
            LearningGovernanceDecision.LOCK_DANGEROUS_POLICY,
        }:
            risks.append(SystemIntegrityRisk.GOVERNANCE_FAILURE)

    if data.safe_rl_result is not None and data.safe_rl_result.status == SafeRLStatus.BLOCKED:
        risks.append(SystemIntegrityRisk.SAFETY_LOCKDOWN_REQUIRED)

    if data.cognitive_adaptation is not None and data.cognitive_adaptation.load_level == CognitiveLoadLevel.OVERLOADED:
        risks.append(SystemIntegrityRisk.COGNITIVE_OVERLOAD)

    if data.strategic_timeline_analysis is not None and (
        data.strategic_timeline_analysis.degradation_detected
        or StrategicDriftSignal.STRATEGIC_DEGRADATION in data.strategic_timeline_analysis.drift_signals
    ):
        risks.append(SystemIntegrityRisk.STRATEGIC_DRIFT)

    if data.behavioral_stability is not None and (
        data.behavioral_stability.stability_score < 50
        or data.behavioral_stability.pressure_level == BehavioralPressureLevel.EXTREME
        or data.behavioral_stability.recovery_state in {BehavioralRecoveryState.DETERIORATING, BehavioralRecoveryState.CRITICAL}
    ):
        risks.append(SystemIntegrityRisk.BEHAVIORAL_DRIFT)

    if _cross_layer_conflict(data):
        risks.extend((SystemIntegrityRisk.LOGIC_CONFLICT, SystemIntegrityRisk.LAYER_CONTRADICTION))

    unhealthy_reports = [
        report for report in reports if report.health_status in {ModuleHealthStatus.WARNING, ModuleHealthStatus.UNSTABLE, ModuleHealthStatus.BLOCKED, ModuleHealthStatus.ISOLATE}
    ]
    blocked_reports = [
        report for report in reports if report.health_status in {ModuleHealthStatus.BLOCKED, ModuleHealthStatus.ISOLATE}
    ]
    if unhealthy_reports:
        risks.append(SystemIntegrityRisk.MODULE_INSTABILITY)
    if len(unhealthy_reports) >= 3 or len(blocked_reports) >= 2:
        risks.append(SystemIntegrityRisk.RISK_ACCUMULATION)

    return tuple(dict.fromkeys(risks))


def compute_module_health(
    integrity_input: SystemIntegrityInput | None = None,
    **kwargs,
) -> tuple[ModuleIntegrityReport, ...]:
    """Build module-level health reports for all provided inputs."""
    data = _input(integrity_input, **kwargs)
    reports: list[ModuleIntegrityReport] = []
    if data.self_evaluation is not None:
        reports.append(_self_evaluation_health(data))
    if data.learning_governance is not None:
        reports.append(_learning_governance_health(data))
    if data.cognitive_adaptation is not None:
        reports.append(_cognitive_health(data))
    if data.behavioral_stability is not None:
        reports.append(_behavioral_health(data))
    if data.supervisor_result is not None:
        reports.append(_supervisor_health(data))
    if data.agent_coordination is not None:
        reports.append(_agent_health(data))
    if data.strategic_timeline_analysis is not None:
        reports.append(_strategic_timeline_health(data))
    if data.strategic_result is not None:
        reports.append(_strategic_planning_health(data))
    if data.safe_rl_result is not None:
        reports.append(_safe_rl_health(data))
    if data.replay_arena is not None:
        reports.append(_replay_arena_health(data))
    if data.executive_result is not None:
        reports.append(_executive_health(data))
    return tuple(reports)


def recommend_integrity_action(
    integrity_input: SystemIntegrityInput | None = None,
    *,
    risks: tuple[SystemIntegrityRisk, ...] | None = None,
    module_reports: tuple[ModuleIntegrityReport, ...] | None = None,
    status: SystemIntegrityStatus | None = None,
    **kwargs,
) -> tuple[str, tuple[str, ...]]:
    """Recommend protection, isolation or logical rollback actions."""
    data = _input(integrity_input, **kwargs)
    reports = module_reports or compute_module_health(data)
    resolved_risks = risks or detect_system_integrity_risks(data, module_reports=reports)
    resolved_status = status or _status(_integrity_score(reports, resolved_risks), resolved_risks)
    actions: list[str] = []

    if resolved_status == SystemIntegrityStatus.ROLLBACK_RECOMMENDED:
        primary = "ROLLBACK_RECOMMENDED"
        actions.append("Recommend logical rollback to the last stable offline configuration.")
    elif resolved_status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.PROTECTION_MODE}:
        primary = "PROTECTION_MODE"
        actions.append("Enter protection mode and block autonomous escalation.")
    elif resolved_status == SystemIntegrityStatus.UNSTABLE:
        primary = "ISOLATE_UNSTABLE_MODULES"
        actions.append("Isolate unstable modules and require review before resuming autonomy.")
    elif resolved_status == SystemIntegrityStatus.DEGRADED:
        primary = "REDUCE_AUTONOMY_AND_MONITOR"
        actions.append("Reduce autonomy and monitor module health.")
    else:
        primary = "MAINTAIN_MONITORED_OPERATION"
        actions.append("Maintain monitored offline operation.")

    if any(report.isolate_recommended for report in reports):
        actions.append("Isolate modules flagged by integrity health reports.")
    if SystemIntegrityRisk.RECALIBRATION_REQUIRED in resolved_risks:
        actions.append("Recalibrate conflicting decision layers before policy updates.")
    if SystemIntegrityRisk.SAFETY_LOCKDOWN_REQUIRED in resolved_risks:
        actions.append("Keep Safe RL and learning workflows locked down.")
    if SystemIntegrityRisk.STRATEGIC_DRIFT in resolved_risks:
        actions.append("Review strategic timeline drift before further adaptation.")
    if SystemIntegrityRisk.BEHAVIORAL_DRIFT in resolved_risks:
        actions.append("Switch behavior-sensitive flows to recovery or observe-only mode.")

    return primary, tuple(dict.fromkeys(actions))


def render_system_integrity_markdown(result: SystemIntegrityResult) -> str:
    """Render system integrity result as Markdown."""
    lines = [
        "# Autonomous System Integrity Engine",
        "",
        "## Integrite systeme",
        "",
        f"- {result.summary}",
        "",
        "## Score global",
        "",
        f"- {result.integrity_score}/100",
        "",
        "## Statut",
        "",
        f"- {result.status.value}",
        "",
        "## Risques detectes",
        "",
        *_bullet_lines(tuple(risk.value for risk in result.risks)),
        "",
        "## Sante des modules",
        "",
        *_module_lines(result.module_reports),
        "",
        "## Modules a isoler",
        "",
        *_bullet_lines(result.modules_to_isolate),
        "",
        "## Recommandation protection/rollback",
        "",
        f"- {result.recommended_action}",
        "",
        "## Actions AGIcore",
        "",
        *_bullet_lines(result.recommended_actions),
        "",
        "- Offline only: no broker, no real order, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def _self_evaluation_health(data: SystemIntegrityInput) -> ModuleIntegrityReport:
    result = data.self_evaluation
    assert result is not None
    risks: list[SystemIntegrityRisk] = []
    notes = [result.summary]
    score = result.confidence_score
    if result.status == SelfEvaluationStatus.CONTRADICTORY:
        risks.extend((SystemIntegrityRisk.LOGIC_CONFLICT, SystemIntegrityRisk.LAYER_CONTRADICTION))
        score -= 25
    if result.confidence_score < 50:
        risks.append(SystemIntegrityRisk.LOW_SYSTEM_CONFIDENCE)
    if result.autonomy_recommendation in {
        SystemAutonomyRecommendation.FREEZE_AUTONOMY,
        SystemAutonomyRecommendation.REQUIRE_HUMAN_REVIEW,
        SystemAutonomyRecommendation.RECALIBRATE_SYSTEM,
    }:
        risks.append(SystemIntegrityRisk.AUTONOMY_UNSAFE)
    if result.autonomy_recommendation == SystemAutonomyRecommendation.RECALIBRATE_SYSTEM:
        risks.append(SystemIntegrityRisk.RECALIBRATION_REQUIRED)
    health_score = _clamp(score)
    return _report("recursive_self_evaluation", health_score, tuple(risks), tuple(notes))


def _learning_governance_health(data: SystemIntegrityInput) -> ModuleIntegrityReport:
    result = data.learning_governance
    assert result is not None
    score = 80
    risks: list[SystemIntegrityRisk] = []
    if result.mode in {LearningGovernanceMode.SAFETY_LOCKDOWN, LearningGovernanceMode.FREEZE_LEARNING}:
        score -= 45
        risks.extend((SystemIntegrityRisk.GOVERNANCE_FAILURE, SystemIntegrityRisk.SAFETY_LOCKDOWN_REQUIRED))
    elif result.decision in {LearningGovernanceDecision.REQUIRE_HUMAN_REVIEW, LearningGovernanceDecision.PAUSE_LEARNING}:
        score -= 18
    if result.risks:
        score -= min(25, len(result.risks) * 5)
    return _report("learning_governance", _clamp(score), tuple(risks), (result.safety_summary,))


def _cognitive_health(data: SystemIntegrityInput) -> ModuleIntegrityReport:
    result = data.cognitive_adaptation
    assert result is not None
    score = result.global_score
    risks: list[SystemIntegrityRisk] = []
    if result.load_level == CognitiveLoadLevel.OVERLOADED:
        score -= 30
        risks.append(SystemIntegrityRisk.COGNITIVE_OVERLOAD)
    elif result.load_level == CognitiveLoadLevel.HIGH:
        score -= 12
    return _report("cognitive_adaptation", _clamp(score), tuple(risks), tuple(result.risks or result.recommendations))


def _behavioral_health(data: SystemIntegrityInput) -> ModuleIntegrityReport:
    result = data.behavioral_stability
    assert result is not None
    score = result.stability_score
    risks: list[SystemIntegrityRisk] = []
    if result.pressure_level == BehavioralPressureLevel.EXTREME:
        score -= 25
        risks.append(SystemIntegrityRisk.BEHAVIORAL_DRIFT)
    if result.recovery_state in {BehavioralRecoveryState.DETERIORATING, BehavioralRecoveryState.CRITICAL}:
        score -= 20
        risks.append(SystemIntegrityRisk.BEHAVIORAL_DRIFT)
    return _report("behavioral_stability", _clamp(score), tuple(risks), tuple(result.risks or result.recommendations))


def _supervisor_health(data: SystemIntegrityInput) -> ModuleIntegrityReport:
    result = data.supervisor_result
    assert result is not None
    score = 85
    risks: list[SystemIntegrityRisk] = []
    if result.decision in {SupervisorDecision.EMERGENCY_HALT, SupervisorDecision.OVERRIDE_TO_BLOCK, SupervisorDecision.OVERRIDE_TO_STOP_SESSION}:
        score -= 35
        risks.append(SystemIntegrityRisk.SAFETY_LOCKDOWN_REQUIRED)
    if not result.final_executable:
        score -= 15
    if any(override != SupervisorOverride.NONE for override in result.applied_overrides):
        score -= 15
        risks.append(SystemIntegrityRisk.LAYER_CONTRADICTION)
    if result.critical_risks:
        score -= min(20, len(result.critical_risks) * 5)
    return _report("hierarchical_supervisor", _clamp(score), tuple(risks), result.critical_risks or (result.recommendation,))


def _agent_health(data: SystemIntegrityInput) -> ModuleIntegrityReport:
    result = data.agent_coordination
    assert result is not None
    score = result.consensus_score
    risks: list[SystemIntegrityRisk] = []
    if result.consensus_status == AgentConsensusStatus.NO_CONSENSUS:
        score -= 20
        risks.append(SystemIntegrityRisk.LAYER_CONTRADICTION)
    if result.final_vote in {AgentVote.BLOCK, AgentVote.STOP_SESSION}:
        score -= 10
    if result.disagreements:
        score -= min(20, len(result.disagreements) * 5)
    return _report("multi_agent_coordination", _clamp(score), tuple(risks), result.risks_detected or result.disagreements)


def _strategic_timeline_health(data: SystemIntegrityInput) -> ModuleIntegrityReport:
    result = data.strategic_timeline_analysis
    assert result is not None
    score = result.strategic_health_score
    risks: list[SystemIntegrityRisk] = []
    if result.degradation_detected or StrategicDriftSignal.STRATEGIC_DEGRADATION in result.drift_signals:
        score -= 25
        risks.append(SystemIntegrityRisk.STRATEGIC_DRIFT)
    if StrategicDriftSignal.BEHAVIORAL_DRIFT in result.drift_signals:
        risks.append(SystemIntegrityRisk.BEHAVIORAL_DRIFT)
    return _report("strategic_timeline", _clamp(score), tuple(risks), result.recommendations or (result.summary,))


def _strategic_planning_health(data: SystemIntegrityInput) -> ModuleIntegrityReport:
    result = data.strategic_result
    assert result is not None
    score = result.progress_score
    risks: list[SystemIntegrityRisk] = []
    if result.plan.status in {StrategicPlanStatus.PAUSED, StrategicPlanStatus.RECOVERY, StrategicPlanStatus.REVIEW_REQUIRED}:
        score -= 18
        risks.append(SystemIntegrityRisk.STRATEGIC_DRIFT)
    return _report("strategic_planning", _clamp(score), tuple(risks), result.progress_notes or (result.recommendation,))


def _safe_rl_health(data: SystemIntegrityInput) -> ModuleIntegrityReport:
    result = data.safe_rl_result
    assert result is not None
    score = 85
    risks: list[SystemIntegrityRisk] = []
    if result.status == SafeRLStatus.BLOCKED:
        score = 20
        risks.append(SystemIntegrityRisk.SAFETY_LOCKDOWN_REQUIRED)
    elif result.status == SafeRLStatus.REVIEW_REQUIRED:
        score = 45
        risks.append(SystemIntegrityRisk.MODULE_INSTABILITY)
    elif result.status == SafeRLStatus.WARNING:
        score = 60
    return _report("safe_rl_layer", score, tuple(risks), result.risks_detected or (result.safety_summary,))


def _replay_arena_health(data: SystemIntegrityInput) -> ModuleIntegrityReport:
    result = data.replay_arena
    assert result is not None
    score = result.robustness_score
    risks: list[SystemIntegrityRisk] = []
    if result.status == ReplayArenaStatus.BLOCKED_BY_SAFETY:
        score -= 25
        risks.append(SystemIntegrityRisk.SAFETY_LOCKDOWN_REQUIRED)
    if result.dangerous_decisions:
        score -= min(20, result.dangerous_decisions * 5)
        risks.append(SystemIntegrityRisk.RISK_ACCUMULATION)
    return _report("replay_arena", _clamp(score), tuple(risks), result.risks_detected or result.recommendations)


def _executive_health(data: SystemIntegrityInput) -> ModuleIntegrityReport:
    result = data.executive_result
    assert result is not None
    score = 80
    risks: list[SystemIntegrityRisk] = []
    if result.decision.stop_session or not result.decision.allow_execution:
        score -= 15
    if result.decision.allow_execution and data.supervisor_result is not None and not data.supervisor_result.final_executable:
        score -= 35
        risks.extend((SystemIntegrityRisk.LOGIC_CONFLICT, SystemIntegrityRisk.LAYER_CONTRADICTION))
    return _report("executive_brain", _clamp(score), tuple(risks), tuple(result.state.reasons or (result.recommendation,)))


def _report(
    module_name: str,
    health_score: int,
    risks: tuple[SystemIntegrityRisk, ...],
    notes: tuple[str, ...],
) -> ModuleIntegrityReport:
    status = _module_status(health_score, risks)
    return ModuleIntegrityReport(
        module_name=module_name,
        health_status=status,
        health_score=health_score,
        risks=tuple(dict.fromkeys(risks)),
        notes=notes or ("No integrity note.",),
        isolate_recommended=status in {ModuleHealthStatus.ISOLATE, ModuleHealthStatus.BLOCKED},
    )


def _module_status(health_score: int, risks: tuple[SystemIntegrityRisk, ...]) -> ModuleHealthStatus:
    if health_score < 25 or SystemIntegrityRisk.RECALIBRATION_REQUIRED in risks:
        return ModuleHealthStatus.ISOLATE
    if health_score < 40 or SystemIntegrityRisk.SAFETY_LOCKDOWN_REQUIRED in risks:
        return ModuleHealthStatus.BLOCKED
    if health_score < 55 or any(risk in risks for risk in _critical_risks()):
        return ModuleHealthStatus.UNSTABLE
    if health_score < 70 or risks:
        return ModuleHealthStatus.WARNING
    return ModuleHealthStatus.HEALTHY


def _cross_layer_conflict(data: SystemIntegrityInput) -> bool:
    return bool(
        data.executive_result is not None
        and data.executive_result.decision.allow_execution
        and (
            (data.supervisor_result is not None and not data.supervisor_result.final_executable)
            or (
                data.agent_coordination is not None
                and data.agent_coordination.final_vote in {AgentVote.BLOCK, AgentVote.STOP_SESSION}
            )
        )
    )


def _integrity_score(
    reports: tuple[ModuleIntegrityReport, ...],
    risks: tuple[SystemIntegrityRisk, ...],
) -> int:
    if not reports:
        base = 65
    else:
        base = int(round(sum(report.health_score for report in reports) / len(reports)))
    base -= 6 * len(risks)
    base -= 8 * sum(1 for risk in risks if risk in _critical_risks())
    return _clamp(base)


def _status(score: int, risks: tuple[SystemIntegrityRisk, ...]) -> SystemIntegrityStatus:
    critical_count = sum(1 for risk in risks if risk in _critical_risks())
    if SystemIntegrityRisk.RECALIBRATION_REQUIRED in risks or (score < 25 and critical_count >= 2):
        return SystemIntegrityStatus.ROLLBACK_RECOMMENDED
    if critical_count >= 4:
        return SystemIntegrityStatus.PROTECTION_MODE
    if score < 35 or critical_count >= 3:
        return SystemIntegrityStatus.COMPROMISED
    if score < 55 or critical_count >= 2:
        return SystemIntegrityStatus.UNSTABLE
    if score < 75 or risks:
        return SystemIntegrityStatus.DEGRADED
    return SystemIntegrityStatus.HEALTHY


def _critical_risks() -> set[SystemIntegrityRisk]:
    return {
        SystemIntegrityRisk.LOGIC_CONFLICT,
        SystemIntegrityRisk.LAYER_CONTRADICTION,
        SystemIntegrityRisk.GOVERNANCE_FAILURE,
        SystemIntegrityRisk.AUTONOMY_UNSAFE,
        SystemIntegrityRisk.COGNITIVE_OVERLOAD,
        SystemIntegrityRisk.SAFETY_LOCKDOWN_REQUIRED,
        SystemIntegrityRisk.LOW_SYSTEM_CONFIDENCE,
        SystemIntegrityRisk.RECALIBRATION_REQUIRED,
    }


def _module_lines(reports: tuple[ModuleIntegrityReport, ...]) -> list[str]:
    if not reports:
        return ["- None"]
    return [
        f"- {report.module_name}: {report.health_status.value} ({report.health_score}/100)"
        for report in reports
    ]


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _input(integrity_input: SystemIntegrityInput | None = None, **kwargs: Any) -> SystemIntegrityInput:
    if integrity_input is not None:
        return integrity_input
    return SystemIntegrityInput(**kwargs)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "compute_module_health",
    "detect_system_integrity_risks",
    "evaluate_system_integrity",
    "recommend_integrity_action",
    "render_system_integrity_markdown",
]
