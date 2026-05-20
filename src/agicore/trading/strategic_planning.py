"""Offline Strategic Planning Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime

from .context_scoring_models import TradeContextDecision
from .executive_brain_models import ExecutiveMode
from .hierarchical_supervisor_models import SupervisorDecision
from .reward_models import RewardLabel
from .strategic_planning_models import (
    StrategicHorizon,
    StrategicObjective,
    StrategicPlan,
    StrategicPlanningEvent,
    StrategicPlanningInput,
    StrategicPlanningResult,
    StrategicPlanStatus,
)


def build_strategic_plan(
    planning_input: StrategicPlanningInput | None = None,
    **kwargs,
) -> StrategicPlan:
    """Build a multi-session offline strategic plan from current evidence."""
    data = _input(planning_input, **kwargs)
    reasons: list[str] = []
    risks: list[str] = []
    recommendations: list[str] = []
    policy_to_test = _best_policy_name(data)

    if _must_pause(data, reasons, risks):
        return _plan(
            data.horizon,
            StrategicObjective.PAUSE_AND_REVIEW,
            StrategicPlanStatus.PAUSED,
            max_trades=0,
            max_loss=0.0,
            focus="review only",
            policy=policy_to_test,
            risks=risks,
            reasons=reasons,
            recommendations=("Stop active decision loops and review safety findings.",),
        )
    if _needs_recovery(data, reasons, risks):
        return _plan(
            data.horizon,
            StrategicObjective.DRAWDOWN_RECOVERY,
            StrategicPlanStatus.RECOVERY,
            max_trades=1,
            max_loss=0.25,
            focus="discipline reset and loss containment",
            policy=policy_to_test,
            risks=risks,
            reasons=reasons,
            recommendations=("Run learning-only review before increasing exposure.",),
        )
    if _needs_capital_preservation(data, reasons, risks):
        return _plan(
            data.horizon,
            StrategicObjective.CAPITAL_PRESERVATION,
            StrategicPlanStatus.DEFENSIVE,
            max_trades=1,
            max_loss=0.35,
            focus="protect capital and avoid marginal setups",
            policy=policy_to_test,
            risks=risks,
            reasons=reasons,
            recommendations=("Reduce frequency and require high-quality context.",),
        )
    if _weak_dataset(data, reasons, risks):
        return _plan(
            data.horizon,
            StrategicObjective.LEARNING_PHASE,
            StrategicPlanStatus.REVIEW_REQUIRED,
            max_trades=2,
            max_loss=0.5,
            focus="collect cleaner offline transitions",
            policy=policy_to_test,
            risks=risks,
            reasons=reasons,
            recommendations=("Improve dataset quality before policy expansion.",),
        )
    if _stable_policy_validation_context(data, reasons, recommendations):
        return _plan(
            data.horizon,
            StrategicObjective.POLICY_VALIDATION,
            StrategicPlanStatus.ACTIVE,
            max_trades=3,
            max_loss=0.75,
            focus="validate best policy in stable context",
            policy=policy_to_test,
            risks=risks,
            reasons=reasons,
            recommendations=tuple(recommendations) or ("Validate policy with strict offline paper constraints.",),
        )
    if _controlled_growth_context(data, reasons):
        return _plan(
            data.horizon,
            StrategicObjective.CONTROLLED_GROWTH,
            StrategicPlanStatus.ACTIVE,
            max_trades=4,
            max_loss=1.0,
            focus="controlled growth with risk limits",
            policy=policy_to_test,
            risks=risks,
            reasons=reasons,
            recommendations=("Maintain controlled exposure and monitor consistency.",),
        )

    reasons.append("Default strategic path favors consistency before expansion.")
    return _plan(
        data.horizon,
        StrategicObjective.CONSISTENCY_BUILDING,
        StrategicPlanStatus.ACTIVE,
        max_trades=2,
        max_loss=0.5,
        focus="consistency and rule adherence",
        policy=policy_to_test,
        risks=risks,
        reasons=reasons,
        recommendations=("Keep session objectives simple and measurable.",),
    )


def evaluate_strategic_progress(
    plan: StrategicPlan,
    planning_input: StrategicPlanningInput | None = None,
    **kwargs,
) -> StrategicPlanningResult:
    """Evaluate strategic progress against reward, stability, drawdown and violations."""
    data = _input(planning_input, **kwargs)
    score = 70
    notes: list[str] = []

    if data.reward_evaluation is not None:
        score += _bucket((data.reward_evaluation.normalized_reward - 50) * 0.4)
        notes.append(f"Reward normalized: {data.reward_evaluation.normalized_reward}.")
        if data.reward_evaluation.total_reward < 0:
            score -= 15
            notes.append("Negative reward reduces strategic progress.")
    if data.context_score is not None:
        score += _bucket((data.context_score.global_score - 60) * 0.25)
        notes.append(f"Context score: {data.context_score.global_score}.")
        if data.context_score.decision in {TradeContextDecision.HIGH_RISK_CONTEXT, TradeContextDecision.NO_TRADE}:
            score -= 20
            notes.append(f"Context risk decision: {data.context_score.decision.value}.")
    if data.dataset_quality is not None:
        score += _bucket((data.dataset_quality.quality_score - 60) * 0.2)
        notes.append(f"Dataset quality: {data.dataset_quality.quality_score}.")
        if data.dataset_quality.dangerous_decision_count:
            score -= min(20, data.dataset_quality.dangerous_decision_count * 3)
            notes.append("Dangerous decisions detected in offline dataset.")
    if data.replay_arena is not None:
        score += _bucket((data.replay_arena.robustness_score - 60) * 0.2)
        notes.append(f"Replay robustness: {data.replay_arena.robustness_score}.")
        if data.replay_arena.safe_rl_blocks:
            score -= min(25, data.replay_arena.safe_rl_blocks * 5)
            notes.append("Safe RL blocks reduced strategic stability.")
    if data.trader_memory_profile is not None:
        score += _bucket((data.trader_memory_profile.average_consistency_score - 60) * 0.2)
        if data.trader_memory_profile.average_emotional_risk_score > 70:
            score -= 15
            notes.append("High historical emotional risk weakens progress.")

    score = _clamp(score)
    updated_plan = _with_progress(plan, _progress_metrics(score, data))
    event = StrategicPlanningEvent(
        status=updated_plan.status,
        objective=updated_plan.primary_objective,
        message=f"Strategic progress evaluated at {score}/100.",
        timestamp=datetime.now(UTC),
    )
    return StrategicPlanningResult(
        plan=updated_plan,
        progress_score=score,
        progress_notes=tuple(notes) or ("No progress evidence supplied.",),
        events=(event,),
        recommendation=_recommendation(updated_plan, score),
    )


def update_strategic_plan(
    previous_plan: StrategicPlan | None = None,
    planning_input: StrategicPlanningInput | None = None,
    **kwargs,
) -> StrategicPlanningResult:
    """Build or update a strategic plan and evaluate current progress."""
    data = _input(planning_input, **kwargs)
    if previous_plan is not None and data.previous_plan is None:
        data = StrategicPlanningInput(
            executive_result=data.executive_result,
            supervisor_result=data.supervisor_result,
            replay_arena=data.replay_arena,
            rl_playground=data.rl_playground,
            policy_memory=data.policy_memory,
            dataset_quality=data.dataset_quality,
            reward_evaluation=data.reward_evaluation,
            context_score=data.context_score,
            trader_memory_profile=data.trader_memory_profile,
            previous_plan=previous_plan,
            horizon=data.horizon,
        )
    plan = build_strategic_plan(data)
    if data.previous_plan is not None and plan.primary_objective == StrategicObjective.CONSISTENCY_BUILDING:
        plan = data.previous_plan
    return evaluate_strategic_progress(plan, data)


def render_strategic_plan_markdown(result: StrategicPlanningResult) -> str:
    """Render the strategic plan as Markdown."""
    plan = result.plan
    lines = [
        "# Strategic Planning Engine",
        "",
        "## Plan strategique",
        "",
        f"- Status: {plan.status.value}",
        "",
        "## Horizon",
        "",
        f"- {plan.horizon.value}",
        "",
        "## Objectif principal",
        "",
        f"- {plan.primary_objective.value}",
        "",
        "## Objectifs de session",
        "",
        *_bullet_lines(plan.session_objectives),
        "",
        "## Contraintes de risque",
        "",
        *_bullet_lines(plan.risk_constraints),
        "",
        "## Progression",
        "",
        f"- Score: {result.progress_score}/100",
        *_metric_lines(plan.progress_metrics),
        *_bullet_lines(result.progress_notes),
        "",
        "## Risques long terme",
        "",
        *_bullet_lines(plan.long_term_risks),
        "",
        "## Recommandations AGIcore",
        "",
        *_bullet_lines(plan.recommendations + (result.recommendation,)),
        "",
        "- Offline only: no broker, no real order, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def _must_pause(data: StrategicPlanningInput, reasons: list[str], risks: list[str]) -> bool:
    if data.executive_result is not None and data.executive_result.state.mode in {ExecutiveMode.PAUSED, ExecutiveMode.SURVIVAL}:
        reasons.append(f"Executive mode requires pause: {data.executive_result.state.mode.value}.")
        risks.append("EXECUTIVE_STOP_OR_SURVIVAL")
        return True
    if data.supervisor_result is not None and (
        not data.supervisor_result.final_executable
        or data.supervisor_result.decision
        in {SupervisorDecision.OVERRIDE_TO_BLOCK, SupervisorDecision.OVERRIDE_TO_STOP_SESSION, SupervisorDecision.EMERGENCY_HALT}
    ):
        reasons.append(f"Supervisor prevents execution: {data.supervisor_result.decision.value}.")
        risks.append("SUPERVISOR_BLOCK")
        return True
    if data.context_score is not None and data.context_score.decision == TradeContextDecision.NO_TRADE:
        reasons.append("Context scoring is NO_TRADE.")
        risks.append("NO_TRADE_CONTEXT")
        return True
    return False


def _needs_recovery(data: StrategicPlanningInput, reasons: list[str], risks: list[str]) -> bool:
    if data.reward_evaluation is not None and (
        data.reward_evaluation.total_reward < 0
        or data.reward_evaluation.reward_label in {RewardLabel.BAD_DECISION, RewardLabel.DANGEROUS_DECISION}
    ):
        reasons.append(f"Reward calls for recovery: {data.reward_evaluation.reward_label.value}.")
        risks.append("NEGATIVE_OR_DANGEROUS_REWARD")
        return True
    if data.replay_arena is not None and (data.replay_arena.average_reward < 0 or data.replay_arena.robustness_score < 45):
        reasons.append("Replay arena shows weak robustness or negative average reward.")
        risks.append("REPLAY_DRAWDOWN_RISK")
        return True
    if data.previous_plan is not None and data.previous_plan.primary_objective == StrategicObjective.DRAWDOWN_RECOVERY:
        reasons.append("Previous plan was already in drawdown recovery.")
        risks.append("RECOVERY_CONTINUATION")
        return True
    return False


def _needs_capital_preservation(data: StrategicPlanningInput, reasons: list[str], risks: list[str]) -> bool:
    if data.executive_result is not None and data.executive_result.state.mode == ExecutiveMode.DEFENSIVE:
        reasons.append("Executive brain is defensive.")
        risks.append("EXECUTIVE_DEFENSIVE")
        return True
    if data.context_score is not None and data.context_score.decision in {
        TradeContextDecision.HIGH_RISK_CONTEXT,
        TradeContextDecision.REDUCE_RISK,
    }:
        reasons.append(f"Context requires reduced risk: {data.context_score.decision.value}.")
        risks.append("CONTEXT_RISK")
        return True
    if data.trader_memory_profile is not None and data.trader_memory_profile.average_emotional_risk_score > 75:
        reasons.append("Trader memory shows high emotional risk.")
        risks.append("HIGH_EMOTIONAL_MEMORY_RISK")
        return True
    return False


def _weak_dataset(data: StrategicPlanningInput, reasons: list[str], risks: list[str]) -> bool:
    if data.dataset_quality is None:
        return False
    if data.dataset_quality.quality_score < 60 or data.dataset_quality.transitions_count < 10:
        reasons.append("Offline learning dataset is not strong enough for policy expansion.")
        risks.append("WEAK_DATASET")
        return True
    return False


def _stable_policy_validation_context(
    data: StrategicPlanningInput,
    reasons: list[str],
    recommendations: list[str],
) -> bool:
    context_ok = data.context_score is not None and data.context_score.global_score >= 70 and data.context_score.decision in {
        TradeContextDecision.TRADE_ALLOWED,
        TradeContextDecision.STRONG_TRADE_ALLOWED,
    }
    dataset_ok = data.dataset_quality is None or data.dataset_quality.quality_score >= 70
    best_policy_ok = data.rl_playground is not None and data.rl_playground.best_policy is not None and data.rl_playground.best_policy.final_score >= 70
    if context_ok and dataset_ok and best_policy_ok:
        reasons.append("Stable context and strong offline policy candidate support validation.")
        recommendations.append("Validate the best policy with capped paper-only exposure.")
        return True
    return False


def _controlled_growth_context(data: StrategicPlanningInput, reasons: list[str]) -> bool:
    if data.executive_result is None or data.context_score is None:
        return False
    if data.executive_result.state.mode == ExecutiveMode.OPPORTUNITY and data.context_score.global_score >= 80:
        reasons.append("Executive brain and context both support controlled growth.")
        return True
    return False


def _best_policy_name(data: StrategicPlanningInput) -> str | None:
    if data.rl_playground is not None and data.rl_playground.best_policy is not None:
        return data.rl_playground.best_policy.candidate_name
    if data.policy_memory is None or not data.policy_memory.entries:
        return None
    entries = sorted(
        data.policy_memory.entries.values(),
        key=lambda entry: (entry.confidence_score, entry.average_reward),
        reverse=True,
    )
    return entries[0].policy_name


def _plan(
    horizon: StrategicHorizon,
    objective: StrategicObjective,
    status: StrategicPlanStatus,
    max_trades: int,
    max_loss: float,
    focus: str,
    policy: str | None,
    risks: list[str],
    reasons: list[str],
    recommendations: tuple[str, ...],
) -> StrategicPlan:
    session_objectives = (
        f"Max trades: {max_trades}",
        f"Max session loss: {max_loss:.2f}R",
        f"Focus behavior: {focus}",
        f"Policy to test: {policy or 'none'}",
    )
    constraints = (
        "offline_only",
        "no_real_orders",
        f"max_trades_per_session={max_trades}",
        f"max_session_loss_r={max_loss:.2f}",
    )
    return StrategicPlan(
        horizon=horizon,
        primary_objective=objective,
        status=status,
        session_objectives=session_objectives,
        risk_constraints=constraints,
        max_trades_per_session=max_trades,
        max_session_loss_r=max_loss,
        focus_behavior=focus,
        policy_to_test=policy,
        long_term_risks=tuple(dict.fromkeys(risks)) or ("None identified from supplied inputs.",),
        recommendations=recommendations,
        reasons=tuple(dict.fromkeys(reasons)),
    )


def _with_progress(plan: StrategicPlan, progress_metrics: dict[str, float]) -> StrategicPlan:
    return StrategicPlan(
        horizon=plan.horizon,
        primary_objective=plan.primary_objective,
        status=plan.status,
        session_objectives=plan.session_objectives,
        risk_constraints=plan.risk_constraints,
        max_trades_per_session=plan.max_trades_per_session,
        max_session_loss_r=plan.max_session_loss_r,
        focus_behavior=plan.focus_behavior,
        policy_to_test=plan.policy_to_test,
        progress_metrics=progress_metrics,
        long_term_risks=plan.long_term_risks,
        recommendations=plan.recommendations,
        reasons=plan.reasons,
    )


def _progress_metrics(score: int, data: StrategicPlanningInput) -> dict[str, float]:
    return {
        "progress_score": float(score),
        "average_reward": float(data.reward_evaluation.normalized_reward if data.reward_evaluation else 0),
        "context_score": float(data.context_score.global_score if data.context_score else 0),
        "dataset_quality": float(data.dataset_quality.quality_score if data.dataset_quality else 0),
        "replay_robustness": float(data.replay_arena.robustness_score if data.replay_arena else 0),
        "consistency": float(data.trader_memory_profile.average_consistency_score if data.trader_memory_profile else 0),
    }


def _recommendation(plan: StrategicPlan, progress_score: int) -> str:
    if plan.status == StrategicPlanStatus.PAUSED:
        return "Pause and review. Do not expand exposure."
    if plan.status == StrategicPlanStatus.RECOVERY:
        return "Stay in recovery until reward and consistency improve."
    if progress_score < 50:
        return "Tighten limits and prioritize capital preservation."
    if plan.primary_objective == StrategicObjective.POLICY_VALIDATION:
        return "Continue policy validation with strict offline paper controls."
    if plan.primary_objective == StrategicObjective.CONTROLLED_GROWTH:
        return "Allow controlled growth only while safety metrics remain stable."
    return "Continue the current strategic plan and monitor violations."


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _metric_lines(metrics: dict[str, float]) -> list[str]:
    if not metrics:
        return ["- No metrics"]
    return [f"- {name}: {value:.2f}" for name, value in metrics.items()]


def _bucket(value: float) -> int:
    return int(round(value))


def _clamp(value: int, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, value))


def _input(planning_input: StrategicPlanningInput | None = None, **kwargs) -> StrategicPlanningInput:
    if planning_input is not None:
        return planning_input
    return StrategicPlanningInput(**kwargs)


__all__ = [
    "build_strategic_plan",
    "evaluate_strategic_progress",
    "render_strategic_plan_markdown",
    "update_strategic_plan",
]
