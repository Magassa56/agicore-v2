"""Offline Autonomous Cognitive Stability Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState
from .cognitive_adaptation_models import CognitiveLoadLevel
from .cognitive_governance_models import CognitiveGovernanceMode, CognitiveGovernanceRisk
from .cognitive_policy_models import CognitivePolicyMode, CognitivePolicyRisk
from .cognitive_stability_models import (
    CognitiveStabilityEvent,
    CognitiveStabilityInput,
    CognitiveStabilityMode,
    CognitiveStabilityRecommendation,
    CognitiveStabilityResult,
    CognitiveStabilityRisk,
    CognitiveStabilityScore,
    CognitiveStabilitySignal,
    CognitiveStabilityState,
    StabilityTrend,
    StabilityWindow,
)
from .collective_consensus_models import ConsensusDecision, ConsensusMode
from .global_orchestrator_models import OrchestratorDecision, OrchestratorMode
from .mission_continuity_models import MissionContinuityMode
from .operational_awareness_models import OperationalAwarenessMode
from .recursive_world_model_models import WorldModelDecision, WorldModelRisk
from .recovery_resilience_models import RecoveryMode
from .self_reflection_audit_models import CognitiveAuditRisk, ReflectionState
from .strategic_arbitration_models import ArbitrationDecision, ArbitrationMode
from .system_integrity_models import SystemIntegrityStatus


def evaluate_cognitive_stability(
    stability_input: CognitiveStabilityInput | None = None,
    **kwargs,
) -> CognitiveStabilityResult:
    """Run the full offline cognitive stability evaluation pipeline."""
    data = _input(stability_input, **kwargs)
    window = build_stability_window(data)
    risks = detect_stability_risks(data, stability_window=window)
    signals = _signals_from_risks(data, risks)
    score_breakdown = compute_cognitive_stability_score(data, risks=risks, stability_window=window)
    score = _overall_score(score_breakdown)
    trend = analyze_stability_trend(data, stability_window=window, risks=risks)
    state = _stability_state(data, score, trend, risks)
    mode = _stability_mode(data, state, risks)
    recommendations = generate_stability_recommendations(data, state=state, risks=risks)
    event = CognitiveStabilityEvent(state, mode, f"cognitive stability state={state.value}", datetime.now(UTC))
    return CognitiveStabilityResult(
        state,
        mode,
        score,
        score_breakdown,
        trend,
        window,
        signals,
        risks,
        recommendations,
        (event,),
        f"{state.value}: {mode.value} with stability score {score}/100",
    )


def detect_stability_risks(
    stability_input: CognitiveStabilityInput | None = None,
    *,
    stability_window: StabilityWindow | None = None,
    **kwargs,
) -> tuple[CognitiveStabilityRisk, ...]:
    """Detect cognitive stability risks from current and historical state."""
    data = _input(stability_input, **kwargs)
    window = stability_window or build_stability_window(data)
    risks: list[CognitiveStabilityRisk] = []

    if _drift_detected(data):
        risks.append(CognitiveStabilityRisk.COGNITIVE_DRIFT)
    if _recursive_instability(data):
        risks.append(CognitiveStabilityRisk.RECURSIVE_INSTABILITY)
    if detect_decision_oscillation(stability_window=window):
        risks.append(CognitiveStabilityRisk.DECISION_OSCILLATION)
    if _policy_fragmentation(data):
        risks.append(CognitiveStabilityRisk.POLICY_FRAGMENTATION)
    if _consensus_conflict(data):
        risks.append(CognitiveStabilityRisk.CONSENSUS_CONFLICT)
    if _orchestrator_overload(data):
        risks.append(CognitiveStabilityRisk.ORCHESTRATOR_OVERLOAD)
    if _world_model_incoherent(data):
        risks.append(CognitiveStabilityRisk.WORLD_MODEL_INCOHERENCE)
    if _behavioral_instability(data):
        risks.append(CognitiveStabilityRisk.BEHAVIORAL_INSTABILITY)
    if _runaway_recursion(data):
        risks.append(CognitiveStabilityRisk.RUNAWAY_RECURSION)
    if _collapse_risk(data, window):
        risks.append(CognitiveStabilityRisk.SYSTEM_COLLAPSE_RISK)
    return tuple(dict.fromkeys(risks))


def analyze_stability_trend(
    stability_input: CognitiveStabilityInput | None = None,
    *,
    stability_window: StabilityWindow | None = None,
    risks: tuple[CognitiveStabilityRisk, ...] | None = None,
    **kwargs,
) -> StabilityTrend:
    """Analyze trend across the stability window."""
    data = _input(stability_input, **kwargs)
    window = stability_window or build_stability_window(data)
    resolved_risks = risks if risks is not None else detect_stability_risks(data, stability_window=window)
    if CognitiveStabilityRisk.SYSTEM_COLLAPSE_RISK in resolved_risks:
        return StabilityTrend.COLLAPSING
    if CognitiveStabilityRisk.DECISION_OSCILLATION in resolved_risks:
        return StabilityTrend.OSCILLATING
    if window.snapshots_count < 2:
        return StabilityTrend.UNKNOWN
    first = window.score_sequence[0]
    latest = window.latest_score
    if latest >= first + 8:
        return StabilityTrend.IMPROVING
    if latest <= first - 12:
        return StabilityTrend.DEGRADING
    if resolved_risks:
        return StabilityTrend.WATCH
    return StabilityTrend.STABLE


def compute_cognitive_stability_score(
    stability_input: CognitiveStabilityInput | None = None,
    *,
    risks: tuple[CognitiveStabilityRisk, ...] | None = None,
    stability_window: StabilityWindow | None = None,
    **kwargs,
) -> CognitiveStabilityScore:
    """Compute cognitive stability component scores."""
    data = _input(stability_input, **kwargs)
    window = stability_window or build_stability_window(data)
    resolved_risks = risks if risks is not None else detect_stability_risks(data, stability_window=window)
    risk_penalty = 7 * len(resolved_risks)
    governance = _clamp(_governance_score(data) - 20 * _has(resolved_risks, CognitiveStabilityRisk.COGNITIVE_DRIFT))
    policy = _clamp(_policy_score(data) - 25 * _has(resolved_risks, CognitiveStabilityRisk.POLICY_FRAGMENTATION))
    consensus = _clamp(_consensus_score(data) - 25 * _has(resolved_risks, CognitiveStabilityRisk.CONSENSUS_CONFLICT))
    orchestration = _clamp(_orchestration_score(data) - 25 * _has(resolved_risks, CognitiveStabilityRisk.ORCHESTRATOR_OVERLOAD))
    world = _clamp(_world_score(data) - 25 * _has(resolved_risks, CognitiveStabilityRisk.WORLD_MODEL_INCOHERENCE))
    behavioral = _clamp(_behavior_score(data) - 25 * _has(resolved_risks, CognitiveStabilityRisk.BEHAVIORAL_INSTABILITY))
    recursive = _clamp(90 - risk_penalty - 30 * _has(resolved_risks, CognitiveStabilityRisk.RUNAWAY_RECURSION) - 10 * window.oscillation_count)
    return CognitiveStabilityScore(governance, policy, consensus, orchestration, world, behavioral, recursive)


def detect_decision_oscillation(
    stability_input: CognitiveStabilityInput | None = None,
    *,
    stability_window: StabilityWindow | None = None,
    **kwargs,
) -> bool:
    """Detect repeated swings between opposing decisions."""
    data = _input(stability_input, **kwargs) if stability_input is not None or kwargs else None
    window = stability_window or build_stability_window(data)
    if window.oscillation_count >= 2:
        return True
    sequence = window.decision_sequence
    return any(_opposed(left, right) for left, right in zip(sequence, sequence[1:]))


def build_stability_window(
    stability_input: CognitiveStabilityInput | None = None,
    **kwargs,
) -> StabilityWindow:
    """Build a compact stability window from historical snapshots plus current state."""
    data = _input(stability_input, **kwargs) if stability_input is not None or kwargs else CognitiveStabilityInput()
    snapshots = tuple(data.historical_snapshots) + (_snapshot(data),)
    decisions = tuple(_snapshot_decision(snapshot) for snapshot in snapshots)
    scores = tuple(_snapshot_score(snapshot) for snapshot in snapshots)
    risk_sequence = tuple(_snapshot_risks(snapshot) for snapshot in snapshots)
    oscillations = sum(1 for left, right in zip(decisions, decisions[1:]) if _opposed(left, right))
    latest = scores[-1] if scores else 50
    average = _avg(list(scores), latest)
    return StabilityWindow(len(snapshots), decisions, scores, risk_sequence, oscillations, average, latest)


def generate_stability_recommendations(
    stability_input: CognitiveStabilityInput | None = None,
    *,
    state: CognitiveStabilityState | None = None,
    risks: tuple[CognitiveStabilityRisk, ...] | None = None,
    **kwargs,
) -> tuple[CognitiveStabilityRecommendation, ...]:
    """Generate ordered cognitive stability recommendations."""
    data = _input(stability_input, **kwargs)
    resolved_risks = risks if risks is not None else detect_stability_risks(data)
    resolved_state = state or _stability_state(data, _overall_score(compute_cognitive_stability_score(data, risks=resolved_risks)), StabilityTrend.UNKNOWN, resolved_risks)
    recommendations: list[CognitiveStabilityRecommendation] = []

    if CognitiveStabilityRisk.COGNITIVE_DRIFT in resolved_risks:
        recommendations.append(CognitiveStabilityRecommendation.REDUCE_AUTONOMY)
    if CognitiveStabilityRisk.RECURSIVE_INSTABILITY in resolved_risks or CognitiveStabilityRisk.RUNAWAY_RECURSION in resolved_risks:
        recommendations.append(CognitiveStabilityRecommendation.FREEZE_RECURSIVE_UPDATES)
    if CognitiveStabilityRisk.POLICY_FRAGMENTATION in resolved_risks:
        recommendations.append(CognitiveStabilityRecommendation.STABILIZE_POLICY_SET)
    if CognitiveStabilityRisk.CONSENSUS_CONFLICT in resolved_risks:
        recommendations.append(CognitiveStabilityRecommendation.REBUILD_CONSENSUS)
    if CognitiveStabilityRisk.WORLD_MODEL_INCOHERENCE in resolved_risks:
        recommendations.append(CognitiveStabilityRecommendation.PROTECT_WORLD_MODEL)
    if len(resolved_risks) >= 3 or resolved_state in {CognitiveStabilityState.UNSTABLE, CognitiveStabilityState.CRITICAL}:
        recommendations.append(CognitiveStabilityRecommendation.ENTER_SAFE_STABILITY_MODE)
    if resolved_state in {CognitiveStabilityState.CRITICAL, CognitiveStabilityState.COLLAPSING}:
        recommendations.append(CognitiveStabilityRecommendation.REQUIRE_HUMAN_REVIEW)
    if _recovery_stabilizing(data):
        recommendations.append(CognitiveStabilityRecommendation.INITIATE_RECOVERY_STABILIZATION)
    if CognitiveStabilityRisk.SYSTEM_COLLAPSE_RISK in resolved_risks or resolved_state == CognitiveStabilityState.COLLAPSING:
        recommendations.append(CognitiveStabilityRecommendation.LOCK_SYSTEM_STABILITY)
    recommendations.append(CognitiveStabilityRecommendation.CONTINUE_MONITORING)
    return tuple(dict.fromkeys(recommendations))


def render_cognitive_stability_markdown(result: CognitiveStabilityResult) -> str:
    """Render cognitive stability result as Markdown."""
    lines = [
        "# Autonomous Cognitive Stability Engine",
        "",
        "## Cognitive Stability State",
        "",
        f"- State: {result.state.value}",
        f"- Mode: {result.mode.value}",
        "",
        "## Stability Score",
        "",
        f"- Overall: {result.stability_score}/100",
        f"- Recursive safety: {result.score_breakdown.recursive_safety_score}/100",
        "",
        "## Stability Trend",
        "",
        f"- {result.trend.value}",
        "",
        "## Stability Window",
        "",
        f"- Snapshots: {result.stability_window.snapshots_count}",
        f"- Average score: {result.stability_window.average_score}/100",
        f"- Oscillations: {result.stability_window.oscillation_count}",
        "",
        "## Detected Signals",
        "",
        *_bullet_lines(tuple(signal.value for signal in result.signals)),
        "",
        "## Stability Risks",
        "",
        *_bullet_lines(tuple(risk.value for risk in result.risks)),
        "",
        "## Recommendations",
        "",
        *_bullet_lines(tuple(recommendation.value for recommendation in result.recommendations)),
        "",
        "## AGIcore Stability Outlook",
        "",
        result.summary,
    ]
    return "\n".join(lines)


def _input(stability_input: CognitiveStabilityInput | None = None, **kwargs) -> CognitiveStabilityInput:
    if stability_input is not None and kwargs:
        raise ValueError("Pass either CognitiveStabilityInput or keyword inputs, not both")
    if stability_input is not None:
        return stability_input
    return CognitiveStabilityInput(**kwargs)


def _signals_from_risks(
    data: CognitiveStabilityInput,
    risks: tuple[CognitiveStabilityRisk, ...],
) -> tuple[CognitiveStabilitySignal, ...]:
    signals: list[CognitiveStabilitySignal] = []
    if not risks:
        signals.append(CognitiveStabilitySignal.STABILITY_CONFIRMED)
    if CognitiveStabilityRisk.COGNITIVE_DRIFT in risks:
        signals.append(CognitiveStabilitySignal.EARLY_DRIFT_WARNING)
    if CognitiveStabilityRisk.DECISION_OSCILLATION in risks:
        signals.append(CognitiveStabilitySignal.OSCILLATION_DETECTED)
    if CognitiveStabilityRisk.POLICY_FRAGMENTATION in risks:
        signals.append(CognitiveStabilitySignal.POLICY_CONFLICT_DETECTED)
    if CognitiveStabilityRisk.CONSENSUS_CONFLICT in risks:
        signals.append(CognitiveStabilitySignal.CONSENSUS_UNSTABLE)
    if CognitiveStabilityRisk.WORLD_MODEL_INCOHERENCE in risks:
        signals.append(CognitiveStabilitySignal.WORLD_MODEL_UNSTABLE)
    if CognitiveStabilityRisk.ORCHESTRATOR_OVERLOAD in risks:
        signals.append(CognitiveStabilitySignal.ORCHESTRATION_STRESS)
    if CognitiveStabilityRisk.RECURSIVE_INSTABILITY in risks or CognitiveStabilityRisk.RUNAWAY_RECURSION in risks:
        signals.append(CognitiveStabilitySignal.RECURSIVE_LOOP_WARNING)
    if CognitiveStabilityRisk.SYSTEM_COLLAPSE_RISK in risks:
        signals.append(CognitiveStabilitySignal.COLLAPSE_WARNING)
    if _recovery_stabilizing(data):
        signals.append(CognitiveStabilitySignal.RECOVERY_STABILIZATION_DETECTED)
    return tuple(dict.fromkeys(signals))


def _stability_state(
    data: CognitiveStabilityInput,
    score: int,
    trend: StabilityTrend,
    risks: tuple[CognitiveStabilityRisk, ...],
) -> CognitiveStabilityState:
    if CognitiveStabilityRisk.SYSTEM_COLLAPSE_RISK in risks:
        return CognitiveStabilityState.COLLAPSING
    if CognitiveStabilityRisk.RUNAWAY_RECURSION in risks or score < 30:
        return CognitiveStabilityState.CRITICAL
    if _recovery_stabilizing(data):
        return CognitiveStabilityState.RECOVERY_STABILIZING
    if len(risks) >= 5 or score < 45:
        return CognitiveStabilityState.UNSTABLE
    if len(risks) >= 3 or trend == StabilityTrend.DEGRADING or score < 60:
        return CognitiveStabilityState.DEGRADED
    if risks or trend in {StabilityTrend.WATCH, StabilityTrend.OSCILLATING}:
        return CognitiveStabilityState.WATCH
    return CognitiveStabilityState.STABLE


def _stability_mode(
    data: CognitiveStabilityInput,
    state: CognitiveStabilityState,
    risks: tuple[CognitiveStabilityRisk, ...],
) -> CognitiveStabilityMode:
    if state == CognitiveStabilityState.COLLAPSING:
        return CognitiveStabilityMode.LOCKED_STABILITY
    if state == CognitiveStabilityState.CRITICAL or CognitiveStabilityRisk.RUNAWAY_RECURSION in risks:
        return CognitiveStabilityMode.EMERGENCY_STABILIZATION
    if state == CognitiveStabilityState.RECOVERY_STABILIZING or _recovery_stabilizing(data):
        return CognitiveStabilityMode.RECOVERY_STABILITY_MODE
    if len(risks) >= 3:
        return CognitiveStabilityMode.SAFE_STABILITY_MODE
    if state in {CognitiveStabilityState.DEGRADED, CognitiveStabilityState.UNSTABLE}:
        return CognitiveStabilityMode.STABILIZATION_MODE
    if state == CognitiveStabilityState.WATCH:
        return CognitiveStabilityMode.MONITORING_MODE
    return CognitiveStabilityMode.NORMAL_STABILITY


def _drift_detected(data: CognitiveStabilityInput) -> bool:
    return (
        _governance_score(data) < 60
        and _policy_score(data) < 65
        and _world_score(data) < 65
    ) or (
        _value(_get(data.cognitive_governance, "mode")) in {CognitiveGovernanceMode.DEGRADED_GOVERNANCE, CognitiveGovernanceMode.SAFE_GOVERNANCE}
        and _value(_get(data.cognitive_policy, "mode")) in {CognitivePolicyMode.POLICY_RESTRICTED, CognitivePolicyMode.POLICY_SAFE_MODE, CognitivePolicyMode.POLICY_WORLD_MODEL_PROTECTED}
    )


def _recursive_instability(data: CognitiveStabilityInput) -> bool:
    world_risks = set(_get(data.recursive_world_model, "risks", ()) or ())
    audit_risks = set(_get(data.self_reflection_audit, "risks", ()) or ())
    policy_risks = set(_get(data.cognitive_policy, "risks", ()) or ())
    return (
        _value(_get(data.recursive_world_model, "decision")) in {
            WorldModelDecision.FREEZE_RECURSIVE_UPDATES,
            WorldModelDecision.ENTER_WORLD_MODEL_SAFE_MODE,
            WorldModelDecision.REBUILD_CAUSAL_GRAPH,
        }
        or WorldModelRisk.RECURSIVE_FEEDBACK_LOOP in world_risks
        or CognitiveAuditRisk.WORLD_MODEL_DRIFT in audit_risks
        or CognitivePolicyRisk.WORLD_MODEL_UNPROTECTED in policy_risks
    )


def _policy_fragmentation(data: CognitiveStabilityInput) -> bool:
    policy = data.cognitive_policy
    risks = set(_get(policy, "risks", ()) or ())
    violations = tuple(_get(policy, "violations", ()) or ())
    return (
        _value(_get(policy, "mode")) in {CognitivePolicyMode.POLICY_SAFE_MODE, CognitivePolicyMode.POLICY_LOCKED}
        or len(violations) >= 2
        or bool({CognitivePolicyRisk.POLICY_CONFLICT, CognitivePolicyRisk.GOVERNANCE_POLICY_MISMATCH, CognitivePolicyRisk.SAFETY_CRITICAL_BYPASS}.intersection(risks))
    )


def _consensus_conflict(data: CognitiveStabilityInput) -> bool:
    return (
        _get(data.collective_consensus, "collective_confidence_score", 75) < 55
        or _value(_get(data.collective_consensus, "mode")) in {
            ConsensusMode.DEGRADED_CONSENSUS,
            ConsensusMode.CONSENSUS_COLLAPSE,
            ConsensusMode.EMERGENCY_CONSENSUS,
        }
        or _value(_get(data.collective_consensus, "decision")) in {
            ConsensusDecision.NO_CONSENSUS,
            ConsensusDecision.BLOCK_COLLECTIVE_ACTION,
            ConsensusDecision.EMERGENCY_HALT,
        }
    )


def _orchestrator_overload(data: CognitiveStabilityInput) -> bool:
    return (
        _get(data.global_orchestrator, "confidence_score", 75) < 55
        or _value(_get(data.global_orchestrator, "decision")) in {
            OrchestratorDecision.ENTER_SAFE_GLOBAL_MODE,
            OrchestratorDecision.ACTIVATE_SURVIVAL_MODE,
            OrchestratorDecision.EMERGENCY_HALT_ROUTING,
        }
        or _value(_get(data.global_orchestrator, "system_state", object()), "mode") in {
            OrchestratorMode.DEGRADED_OPERATION,
            OrchestratorMode.EMERGENCY_ORCHESTRATION,
            OrchestratorMode.SURVIVAL_ORCHESTRATION,
        }
    )


def _world_model_incoherent(data: CognitiveStabilityInput) -> bool:
    world_risks = set(_get(data.recursive_world_model, "risks", ()) or ())
    return _world_score(data) < 55 or WorldModelRisk.WORLD_MODEL_INCOHERENCE in world_risks


def _behavioral_instability(data: CognitiveStabilityInput) -> bool:
    return (
        _get(data.behavioral_stability, "stability_score", 75) < 55
        or _value(_get(data.behavioral_stability, "pressure_level")) in {BehavioralPressureLevel.HIGH, BehavioralPressureLevel.EXTREME}
        or _value(_get(data.behavioral_stability, "recovery_state")) in {BehavioralRecoveryState.DETERIORATING, BehavioralRecoveryState.CRITICAL}
    )


def _runaway_recursion(data: CognitiveStabilityInput) -> bool:
    return _recursive_instability(data) and _policy_fragmentation(data) and (
        _value(_get(data.self_reflection_audit, "state")) in {ReflectionState.CONTRADICTORY_REFLECTION, ReflectionState.CRITICAL_REVIEW}
        or _get(data.self_reflection_audit, "reflection_quality_score", 75) < 45
    )


def _collapse_risk(data: CognitiveStabilityInput, window: StabilityWindow) -> bool:
    return (
        _value(_get(data.system_integrity, "status")) in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.ROLLBACK_RECOMMENDED}
        or _value(_get(data.mission_continuity, "mode")) in {MissionContinuityMode.SURVIVAL_CONTINUITY, MissionContinuityMode.SAFE_PAUSE}
        or window.latest_score < 25
    )


def _recovery_stabilizing(data: CognitiveStabilityInput) -> bool:
    return (
        _value(_get(data.recovery_resilience, "mode")) in {RecoveryMode.STABILIZE, RecoveryMode.REBUILD_CONFIDENCE}
        and _get(data.recovery_resilience, "resilience_score", 0) >= 60
    )


def _snapshot(data: CognitiveStabilityInput) -> dict[str, Any]:
    return {
        "decision": _current_decision(data),
        "score": _current_score(data),
        "risks": tuple(risk.value for risk in _current_risks(data)),
    }


def _current_decision(data: CognitiveStabilityInput) -> str:
    values = (
        _value(_get(data.cognitive_policy, "mode")),
        _value(_get(data.cognitive_governance, "decision")),
        _value(_get(data.collective_consensus, "decision")),
        _value(_get(data.global_orchestrator, "decision")),
    )
    return "|".join(str(value) for value in values if value is not None) or "UNKNOWN"


def _current_score(data: CognitiveStabilityInput) -> int:
    return _avg(
        [
            _policy_score(data),
            _governance_score(data),
            _consensus_score(data),
            _orchestration_score(data),
            _world_score(data),
            _behavior_score(data),
        ],
        60,
    )


def _current_risks(data: CognitiveStabilityInput) -> tuple[CognitiveStabilityRisk, ...]:
    risks: list[CognitiveStabilityRisk] = []
    if _policy_fragmentation(data):
        risks.append(CognitiveStabilityRisk.POLICY_FRAGMENTATION)
    if _world_model_incoherent(data):
        risks.append(CognitiveStabilityRisk.WORLD_MODEL_INCOHERENCE)
    if _consensus_conflict(data):
        risks.append(CognitiveStabilityRisk.CONSENSUS_CONFLICT)
    return tuple(risks)


def _snapshot_decision(snapshot: Any) -> str:
    if isinstance(snapshot, dict):
        return str(snapshot.get("decision", "UNKNOWN"))
    return str(_get(snapshot, "decision", _get(snapshot, "mode", "UNKNOWN")))


def _snapshot_score(snapshot: Any) -> int:
    if isinstance(snapshot, dict):
        return _clamp(snapshot.get("score", 50))
    return _clamp(_get(snapshot, "score", _get(snapshot, "stability_score", 50)))


def _snapshot_risks(snapshot: Any) -> tuple[str, ...]:
    if isinstance(snapshot, dict):
        risks = snapshot.get("risks", ())
    else:
        risks = _get(snapshot, "risks", ())
    return tuple(str(getattr(risk, "value", risk)) for risk in (risks or ()))


def _opposed(left: str, right: str) -> bool:
    positive = ("ALLOW", "APPROVE", "NORMAL", "CONTINUE", "STABLE")
    negative = ("DENY", "BLOCK", "LOCK", "EMERGENCY", "SAFE", "FREEZE", "STOP", "COLLAPS")
    left_pos = any(token in left for token in positive)
    left_neg = any(token in left for token in negative)
    right_pos = any(token in right for token in positive)
    right_neg = any(token in right for token in negative)
    return (left_pos and right_neg) or (left_neg and right_pos)


def _policy_score(data: CognitiveStabilityInput) -> int:
    return _clamp(_get(data.cognitive_policy, "cognitive_policy_score", 70))


def _governance_score(data: CognitiveStabilityInput) -> int:
    return _clamp(_get(data.cognitive_governance, "governance_score", 70))


def _consensus_score(data: CognitiveStabilityInput) -> int:
    return _clamp(_get(data.collective_consensus, "collective_confidence_score", 70))


def _orchestration_score(data: CognitiveStabilityInput) -> int:
    return _clamp(_get(data.global_orchestrator, "confidence_score", _get(data.operational_awareness, "operational_confidence_score", 70)))


def _world_score(data: CognitiveStabilityInput) -> int:
    return _clamp(_get(data.recursive_world_model, "world_model_coherence_score", 70))


def _behavior_score(data: CognitiveStabilityInput) -> int:
    return _clamp(_get(data.behavioral_stability, "stability_score", _get(data.cognitive_adaptation, "global_score", 70)))


def _overall_score(score: CognitiveStabilityScore) -> int:
    return _avg(
        [
            score.governance_stability_score,
            score.policy_stability_score,
            score.consensus_stability_score,
            score.orchestration_stability_score,
            score.world_model_stability_score,
            score.behavioral_stability_score,
            score.recursive_safety_score,
        ],
        50,
    )


def _has(risks: tuple[CognitiveStabilityRisk, ...], risk: CognitiveStabilityRisk) -> int:
    return 1 if risk in risks else 0


def _get(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default) if obj is not None else default


def _value(value: Any, nested: str | None = None) -> Any:
    if nested is not None:
        value = _get(value, nested)
    return getattr(value, "value", value)


def _avg(values: list[int], default: int) -> int:
    values = [int(value) for value in values if value is not None]
    if not values:
        return default
    return _clamp(sum(values) / len(values))


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _clamp(value: float | int | None, low: int = 0, high: int = 100) -> int:
    if value is None:
        value = low
    return max(low, min(high, int(round(float(value)))))


__all__ = [
    "analyze_stability_trend",
    "build_stability_window",
    "compute_cognitive_stability_score",
    "detect_decision_oscillation",
    "detect_stability_risks",
    "evaluate_cognitive_stability",
    "generate_stability_recommendations",
    "render_cognitive_stability_markdown",
]
