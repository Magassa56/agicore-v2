"""Unit tests for the offline Behavioral Stability Engine."""
from __future__ import annotations

from agicore.trading.behavioral_stability import (
    compute_behavioral_stability_score,
    detect_behavioral_risks,
    evaluate_behavioral_stability,
    evaluate_recovery_state,
    render_behavioral_stability_markdown,
)
from agicore.trading.behavioral_stability_models import (
    BehavioralPressureLevel,
    BehavioralRecoveryState,
    BehavioralRiskSignal,
)
from agicore.trading.context_scoring_models import ContextScoreBreakdown, ContextScoringResult, TradeContextDecision
from agicore.trading.reward_models import RewardBreakdown, RewardComponent, RewardEvaluationResult, RewardLabel
from agicore.trading.session_coach_models import LiveSessionCoachResult, SessionCoachDecision
from agicore.trading.strategic_memory_models import StrategicDriftSignal, StrategicTimelineAnalysis
from agicore.trading.strategic_planning_models import (
    StrategicHorizon,
    StrategicObjective,
    StrategicPlan,
    StrategicPlanningResult,
    StrategicPlanStatus,
)
from agicore.trading.tactical_execution_models import (
    TacticalExecutionEvent,
    TacticalExecutionQuality,
    TacticalExecutionResult,
    TacticalExecutionSignal,
    TacticalScoreBreakdown,
)
from agicore.trading.trade_journal_models import JournalAnalysisResult


def _context(decision: TradeContextDecision = TradeContextDecision.TRADE_ALLOWED, score: int = 70) -> ContextScoringResult:
    return ContextScoringResult(
        global_score=score,
        decision=decision,
        breakdown=ContextScoreBreakdown(score, score, score, score, score, score, score),
        favorable_factors=(),
        risk_factors=(),
        recommendations=(),
        strategy_regime_notes=(),
    )


def _reward(label: RewardLabel = RewardLabel.GOOD_DECISION, normalized: int = 70, total: int = 15) -> RewardEvaluationResult:
    component = RewardComponent("x", 0, "x")
    return RewardEvaluationResult(
        total_reward=total,
        normalized_reward=normalized,
        reward_label=label,
        breakdown=RewardBreakdown(component, component, component, component, component, component, component, component, component, component, component),
        learning_notes=(),
        improvement_actions=(),
    )


def _journal(
    playbook: float = 0.9,
    risk: float = 0.9,
    keywords: tuple[tuple[str, str], ...] = (),
) -> JournalAnalysisResult:
    return JournalAnalysisResult(
        total_trades=3,
        total_sessions=1,
        dominant_emotions=(),
        recurring_mistakes=(),
        most_noted_setups=(),
        frequent_tags=(),
        playbook_compliance_rate=playbook,
        risk_rules_compliance_rate=risk,
        missing_screenshot_trade_ids=(),
        keyword_flags=keywords,
        trades_to_review=(),
        improvement_plan=(),
    )


def _tactical(
    quality: TacticalExecutionQuality = TacticalExecutionQuality.GOOD,
    score: int = 78,
    signals: tuple[TacticalExecutionSignal, ...] = (TacticalExecutionSignal.TACTICAL_DISCIPLINE_STRONG,),
) -> TacticalExecutionResult:
    return TacticalExecutionResult(
        quality=quality,
        global_score=score,
        breakdown=TacticalScoreBreakdown(75, 75, 75, 75, 80, 75, 75),
        signals=signals,
        risks=(),
        recommendations=(),
        events=(TacticalExecutionEvent(quality, "event", __import__("datetime").datetime.now(__import__("datetime").UTC)),),
    )


def _timeline(
    health: int = 75,
    stability: int = 75,
    drifts: tuple[StrategicDriftSignal, ...] = (),
    degradation: bool = False,
    improvement: bool = False,
) -> StrategicTimelineAnalysis:
    return StrategicTimelineAnalysis(
        snapshots_count=3,
        cycle_phases=(),
        drift_signals=drifts,
        best_period=None,
        worst_period=None,
        stability_score=stability,
        strategic_health_score=health,
        improvement_detected=improvement,
        degradation_detected=degradation,
        recommendations=(),
        summary="timeline",
    )


def _coach(decision: SessionCoachDecision = SessionCoachDecision.CONTINUE, stop: bool = False, break_: bool = False) -> LiveSessionCoachResult:
    return LiveSessionCoachResult(
        alerts=(),
        recommendations=(),
        stop_recommended=stop,
        break_recommended=break_,
        reduce_size=False,
        decision=decision,
    )


def _strategic_result(status: StrategicPlanStatus = StrategicPlanStatus.ACTIVE, objective: StrategicObjective = StrategicObjective.CONSISTENCY_BUILDING) -> StrategicPlanningResult:
    plan = StrategicPlan(
        horizon=StrategicHorizon.WEEKLY,
        primary_objective=objective,
        status=status,
        session_objectives=(),
        risk_constraints=(),
        max_trades_per_session=2,
        max_session_loss_r=0.5,
        focus_behavior="discipline",
    )
    return StrategicPlanningResult(plan=plan, progress_score=70, progress_notes=(), events=(), recommendation="ok")


def test_detects_tilt_from_loss_and_frustration() -> None:
    signals = detect_behavioral_risks(
        reward_evaluation=_reward(RewardLabel.BAD_DECISION, 25, -20),
        journal_result=_journal(keywords=(("t1", "tilt"),)),
        tactical_execution=_tactical(TacticalExecutionQuality.WEAK, 45),
    )

    assert BehavioralRiskSignal.TILT_RISK in signals


def test_detects_revenge_from_journal_keyword() -> None:
    signals = detect_behavioral_risks(journal_result=_journal(keywords=(("t1", "revenge"),)))

    assert BehavioralRiskSignal.REVENGE_RISK in signals


def test_detects_fatigue_from_coach_break() -> None:
    signals = detect_behavioral_risks(session_coach_result=_coach(break_=True))

    assert BehavioralRiskSignal.FATIGUE_RISK in signals
    assert BehavioralRiskSignal.SESSION_OVERLOAD in signals


def test_detects_overconfidence_after_large_gain_in_risky_context() -> None:
    signals = detect_behavioral_risks(
        reward_evaluation=_reward(RewardLabel.EXCELLENT_DECISION, 95, 80),
        context_score=_context(TradeContextDecision.HIGH_RISK_CONTEXT, 45),
    )

    assert BehavioralRiskSignal.OVERCONFIDENCE_RISK in signals


def test_detects_discipline_decay_from_journal_and_timeline() -> None:
    signals = detect_behavioral_risks(
        journal_result=_journal(playbook=0.5, risk=0.6),
        strategic_timeline_analysis=_timeline(drifts=(StrategicDriftSignal.VIOLATIONS_INCREASE,), degradation=True),
    )

    assert BehavioralRiskSignal.DISCIPLINE_DECAY in signals


def test_recovery_state_can_be_recovering() -> None:
    state = evaluate_recovery_state(
        strategic_result=_strategic_result(StrategicPlanStatus.RECOVERY, StrategicObjective.DRAWDOWN_RECOVERY)
    )

    assert state == BehavioralRecoveryState.RECOVERING


def test_recovery_state_is_critical_when_coach_stops() -> None:
    state = evaluate_recovery_state(session_coach_result=_coach(SessionCoachDecision.STOP_TRADING, stop=True))

    assert state == BehavioralRecoveryState.CRITICAL


def test_compute_score_penalizes_bad_behavior() -> None:
    score = compute_behavioral_stability_score(
        tactical_execution=_tactical(TacticalExecutionQuality.DANGEROUS, 25, (TacticalExecutionSignal.TACTICAL_DISCIPLINE_WEAK,)),
        reward_evaluation=_reward(RewardLabel.DANGEROUS_DECISION, 10, -50),
        journal_result=_journal(playbook=0.4, risk=0.4, keywords=(("t1", "tilt"), ("t2", "fatigue"))),
    )

    assert score.discipline_score < 50
    assert score.emotional_control_score < 60
    assert score.fatigue_score < 80


def test_evaluate_behavioral_stability_extreme_pressure_recommends_pause() -> None:
    result = evaluate_behavioral_stability(
        strategic_timeline_analysis=_timeline(
            health=25,
            stability=35,
            drifts=(StrategicDriftSignal.PERSISTENT_DRAWDOWN, StrategicDriftSignal.STABILITY_DECLINE),
            degradation=True,
        ),
        reward_evaluation=_reward(RewardLabel.BAD_DECISION, 20, -30),
        session_coach_result=_coach(SessionCoachDecision.STOP_TRADING, stop=True),
    )

    assert result.pressure_level == BehavioralPressureLevel.EXTREME
    assert result.recovery_state == BehavioralRecoveryState.CRITICAL
    assert result.stability_score < 50
    assert any("Pause" in item for item in result.recommendations)


def test_evaluate_behavioral_stability_marks_stable_behavior() -> None:
    result = evaluate_behavioral_stability(
        tactical_execution=_tactical(TacticalExecutionQuality.EXCELLENT, 90),
        journal_result=_journal(0.95, 0.95),
        strategic_timeline_analysis=_timeline(health=85, stability=85, improvement=True),
        reward_evaluation=_reward(RewardLabel.GOOD_DECISION, 80, 25),
    )

    assert BehavioralRiskSignal.STABLE_BEHAVIOR in result.signals
    assert BehavioralRiskSignal.CONSISTENT_DISCIPLINE in result.signals
    assert result.stability_score >= 70


def test_render_behavioral_stability_markdown_contains_required_sections() -> None:
    result = evaluate_behavioral_stability(
        tactical_execution=_tactical(),
        journal_result=_journal(),
        strategic_timeline_analysis=_timeline(),
    )

    markdown = render_behavioral_stability_markdown(result)

    assert "# Behavioral Stability Engine" in markdown
    assert "## Stabilite comportementale" in markdown
    assert "## Score global" in markdown
    assert "## Pression psychologique" in markdown
    assert "## Risques detectes" in markdown
    assert "## Etat recuperation" in markdown
    assert "## Discipline" in markdown
    assert "## Fatigue" in markdown
    assert "## Tilt/Revenge" in markdown
    assert "## Recommandations AGIcore" in markdown
    assert "no broker" in markdown
