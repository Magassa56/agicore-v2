from __future__ import annotations

from types import SimpleNamespace

from agicore.trading.behavioral_stability_models import BehavioralPressureLevel
from agicore.trading.cognitive_adaptation_models import CognitiveLoadLevel
from agicore.trading.global_orchestrator_models import OrchestratorDecision
from agicore.trading.intent_alignment_models import IntentAlignmentMode
from agicore.trading.learning_governance_models import LearningGovernanceDecision, LearningGovernanceMode
from agicore.trading.meta_cognition_models import CognitiveBias, MetaCognitionMode, MetaCognitiveRisk
from agicore.trading.multi_timeline_simulation_models import TimelineDecision
from agicore.trading.recursive_self_evaluation_models import SelfEvaluationStatus, SystemAutonomyRecommendation
from agicore.trading.recursive_world_model_models import WorldModelDecision, WorldModelRisk
from agicore.trading.scenario_forecast_models import ForecastDecision
from agicore.trading.self_reflection_audit import (
    build_cognitive_audit_trail,
    compute_reflection_quality,
    detect_cognitive_audit_risks,
    detect_cognitive_audit_signals,
    evaluate_self_reflection_audit,
    generate_cognitive_audit_findings,
    generate_cognitive_audit_recommendations,
    render_self_reflection_audit_markdown,
)
from agicore.trading.self_reflection_audit_models import (
    CognitiveAuditRecommendation,
    CognitiveAuditRisk,
    CognitiveAuditSignal,
    ReflectionDepth,
    ReflectionState,
)
from agicore.trading.strategic_arbitration_models import ArbitrationDecision, ArbitrationMode
from agicore.trading.strategic_memory_models import StrategicDriftSignal


def _world_model(score=80, decision=WorldModelDecision.MAINTAIN_WORLD_MODEL, risks=()):
    return SimpleNamespace(world_model_coherence_score=score, decision=decision, risks=risks)


def _orchestrator(decision=OrchestratorDecision.CONTINUE_COORDINATED_OPERATION, confidence=80):
    return SimpleNamespace(decision=decision, confidence_score=confidence)


def _meta(mode=MetaCognitionMode.SELF_AWARE, confidence=82, reasoning=80, biases=(), risks=()):
    return SimpleNamespace(mode=mode, confidence_score=confidence, reasoning_stability_score=reasoning, biases=biases, risks=risks)


def _cognitive(score=80, load=CognitiveLoadLevel.LOW):
    return SimpleNamespace(global_score=score, load_level=load)


def _behavior(score=80, pressure=BehavioralPressureLevel.LOW):
    return SimpleNamespace(stability_score=score, pressure_level=pressure)


def _timeline(score=80, degraded=False, drifts=()):
    return SimpleNamespace(strategic_health_score=score, degradation_detected=degraded, drift_signals=drifts)


def _forecast(decision=ForecastDecision.CONTINUE_CURRENT_PATH):
    return SimpleNamespace(decision=decision)


def _multi_timeline(decision=TimelineDecision.SELECT_STABLE_TIMELINE):
    return SimpleNamespace(decision=decision)


def _intent(mode=IntentAlignmentMode.FULLY_ALIGNED, confidence=80):
    return SimpleNamespace(mode=mode, alignment_confidence=confidence)


def _arbitration(decision=ArbitrationDecision.CONTINUE_OPERATION, mode=ArbitrationMode.NORMAL_OPERATION):
    return SimpleNamespace(decision=decision, mode=mode)


def _consensus(score=80):
    return SimpleNamespace(collective_confidence_score=score)


def _governance(decision=LearningGovernanceDecision.ALLOW_LEARNING, mode=LearningGovernanceMode.LEARN):
    return SimpleNamespace(decision=decision, mode=mode)


def _self_eval(status=SelfEvaluationStatus.STABLE, recommendation=SystemAutonomyRecommendation.MAINTAIN_AUTONOMY, confidence=82):
    return SimpleNamespace(status=status, autonomy_recommendation=recommendation, confidence_score=confidence)


def test_builds_complete_audit_trail_when_core_layers_are_present() -> None:
    trail = build_cognitive_audit_trail(
        self_evaluation=_self_eval(),
        meta_cognition=_meta(),
        recursive_world_model=_world_model(),
        scenario_forecast=_forecast(),
        multi_timeline=_multi_timeline(),
        global_orchestrator=_orchestrator(),
        learning_governance=_governance(),
    )

    assert trail.trace_complete is True
    assert trail.confidence_score == 100
    assert "world_model" in trail.steps


def test_detects_incomplete_trace_and_reasoning_gap() -> None:
    signals = detect_cognitive_audit_signals(
        self_evaluation=_self_eval(SelfEvaluationStatus.CONTRADICTORY),
        meta_cognition=_meta(MetaCognitionMode.DEGRADED_REASONING),
    )
    risks = detect_cognitive_audit_risks(signals=signals)

    assert CognitiveAuditSignal.AUDIT_TRAIL_INCOMPLETE in signals
    assert CognitiveAuditSignal.REASONING_GAP in signals
    assert CognitiveAuditRisk.UNEXPLAINED_DECISION in risks
    assert CognitiveAuditRisk.INCOMPLETE_TRACEABILITY in risks


def test_detects_strategic_contradiction_from_alignment_and_arbitration() -> None:
    signals = detect_cognitive_audit_signals(
        intent_alignment=_intent(IntentAlignmentMode.MISALIGNED, 35),
        strategic_arbitration=_arbitration(ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationMode.EMERGENCY_LOCKDOWN),
        global_orchestrator=_orchestrator(OrchestratorDecision.CONTINUE_COORDINATED_OPERATION),
    )
    risks = detect_cognitive_audit_risks(signals=signals)

    assert CognitiveAuditSignal.STRATEGIC_CONTRADICTION in signals
    assert CognitiveAuditSignal.ORCHESTRATION_MISMATCH in signals
    assert CognitiveAuditRisk.STRATEGIC_SELF_CONTRADICTION in risks


def test_detects_behavioral_and_meta_cognitive_drift() -> None:
    risks = detect_cognitive_audit_risks(
        behavioral_stability=_behavior(35, BehavioralPressureLevel.EXTREME),
        strategic_timeline_analysis=_timeline(40, True, (StrategicDriftSignal.BEHAVIORAL_DRIFT,)),
        meta_cognition=_meta(MetaCognitionMode.RECALIBRATION_REQUIRED, 35, 40, (CognitiveBias.DECISION_INCONSISTENCY,), (MetaCognitiveRisk.REASONING_DEGRADATION,)),
    )

    assert CognitiveAuditRisk.BEHAVIORAL_DECAY in risks
    assert CognitiveAuditRisk.META_COGNITIVE_DRIFT in risks
    assert CognitiveAuditRisk.REPEATED_COGNITIVE_ERROR in risks


def test_detects_world_model_and_forecast_mismatch() -> None:
    signals = detect_cognitive_audit_signals(
        recursive_world_model=_world_model(35, WorldModelDecision.REBUILD_CAUSAL_GRAPH, (WorldModelRisk.WORLD_MODEL_INCOHERENCE,)),
        scenario_forecast=_forecast(ForecastDecision.CONTINUE_CURRENT_PATH),
        multi_timeline=_multi_timeline(TimelineDecision.ENTER_TIMELINE_SAFE_MODE),
    )
    risks = detect_cognitive_audit_risks(signals=signals)

    assert CognitiveAuditSignal.WORLD_MODEL_INCONSISTENCY in signals
    assert CognitiveAuditSignal.FORECAST_MISMATCH in signals
    assert CognitiveAuditRisk.WORLD_MODEL_DRIFT in risks


def test_compute_reflection_quality_penalizes_risks() -> None:
    quality = compute_reflection_quality(
        meta_cognition=_meta(MetaCognitionMode.CONTRADICTORY, 35, 35, (CognitiveBias.OVERCONFIDENCE,), (MetaCognitiveRisk.LOGICAL_INSTABILITY,)),
        behavioral_stability=_behavior(30, BehavioralPressureLevel.HIGH),
        recursive_world_model=_world_model(40, WorldModelDecision.ENTER_WORLD_MODEL_SAFE_MODE, (WorldModelRisk.SAFETY_MODEL_FAILURE,)),
        self_evaluation=_self_eval(SelfEvaluationStatus.CONTRADICTORY, confidence=30),
    )

    assert quality.reasoning_coherence_score < 60
    assert quality.behavioral_awareness_score < 60
    assert quality.world_model_alignment_score < 60


def test_findings_are_ordered_and_recommend_corrective_actions() -> None:
    findings = generate_cognitive_audit_findings(
        risks=(
            CognitiveAuditRisk.INCOMPLETE_TRACEABILITY,
            CognitiveAuditRisk.STRATEGIC_SELF_CONTRADICTION,
            CognitiveAuditRisk.WORLD_MODEL_DRIFT,
        )
    )

    assert findings[0].severity_score >= findings[-1].severity_score
    assert {finding.corrective_action for finding in findings} >= {
        CognitiveAuditRecommendation.REBUILD_DECISION_TRACE,
        CognitiveAuditRecommendation.CORRECT_STRATEGIC_CONFLICT,
        CognitiveAuditRecommendation.UPDATE_WORLD_MODEL,
    }


def test_recommendations_require_deep_audit_and_autonomy_reduction_on_low_quality() -> None:
    result = evaluate_self_reflection_audit(
        self_evaluation=_self_eval(SelfEvaluationStatus.CONTRADICTORY, SystemAutonomyRecommendation.FREEZE_AUTONOMY, 25),
        learning_governance=_governance(LearningGovernanceDecision.FREEZE_POLICY_UPDATE, LearningGovernanceMode.SAFETY_LOCKDOWN),
        meta_cognition=_meta(MetaCognitionMode.DEGRADED_REASONING, 30, 30, (CognitiveBias.REASONING_DRIFT,), (MetaCognitiveRisk.REASONING_DEGRADATION, MetaCognitiveRisk.LOGICAL_INSTABILITY)),
        recursive_world_model=_world_model(30, WorldModelDecision.ENTER_WORLD_MODEL_SAFE_MODE, (WorldModelRisk.WORLD_MODEL_INCOHERENCE,)),
        behavioral_stability=_behavior(25, BehavioralPressureLevel.EXTREME),
    )

    assert result.depth in {ReflectionDepth.RECURSIVE, ReflectionDepth.CRITICAL}
    assert CognitiveAuditRecommendation.REQUIRE_DEEP_AUDIT in result.recommendations
    assert CognitiveAuditRecommendation.REDUCE_AUTONOMY_DURING_AUDIT in result.recommendations
    assert CognitiveAuditRecommendation.REQUIRE_HUMAN_REVIEW in result.recommendations


def test_clear_reflection_when_trace_and_layers_are_coherent() -> None:
    result = evaluate_self_reflection_audit(
        self_evaluation=_self_eval(),
        meta_cognition=_meta(),
        recursive_world_model=_world_model(),
        scenario_forecast=_forecast(),
        multi_timeline=_multi_timeline(),
        global_orchestrator=_orchestrator(),
        learning_governance=_governance(),
        behavioral_stability=_behavior(),
        intent_alignment=_intent(),
        collective_consensus=_consensus(),
    )

    assert result.state in {ReflectionState.CLEAR_REFLECTION, ReflectionState.PARTIAL_REFLECTION}
    assert result.reflection_quality_score >= 65
    assert CognitiveAuditSignal.DECISION_TRACE_AVAILABLE in result.signals


def test_render_self_reflection_audit_markdown_contains_required_sections() -> None:
    result = evaluate_self_reflection_audit(
        self_evaluation=_self_eval(),
        meta_cognition=_meta(),
        recursive_world_model=_world_model(),
        scenario_forecast=_forecast(),
        multi_timeline=_multi_timeline(),
        global_orchestrator=_orchestrator(),
        learning_governance=_governance(),
    )
    markdown = render_self_reflection_audit_markdown(result)

    assert "Self-Reflection State" in markdown
    assert "Reflection Quality" in markdown
    assert "Audit Signals" in markdown
    assert "Audit Risks" in markdown
    assert "Cognitive Findings" in markdown
    assert "Audit Trail" in markdown
    assert "Recommendations" in markdown
    assert "AGIcore Self-Reflection Outlook" in markdown
