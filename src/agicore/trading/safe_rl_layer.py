"""Offline Safe RL experiment layer for AGIcore Trading."""
from __future__ import annotations

from .behavior_models import BehaviorAnalysisResult
from .context_scoring_models import ContextScoringResult, TradeContextDecision
from .market_regime_models import MarketRegimeAnalysis
from .offline_dataset import evaluate_dataset_quality
from .offline_dataset_models import DatasetQualityReport, OfflineLearningDataset
from .policy_evaluation_models import PolicyEvaluationResult
from .reward_models import RewardEvaluationResult
from .rl_playground_models import RLPlaygroundResult
from .safe_rl_models import (
    SafeRLExperimentConfig,
    SafeRLExperimentResult,
    SafeRLGuardrail,
    SafeRLStatus,
    SafeRLValidationResult,
)
from .semi_auto_decision_models import SemiAutoDecision, SemiAutoDecisionResult


def validate_rl_experiment(
    *,
    dataset: OfflineLearningDataset | None = None,
    dataset_quality: DatasetQualityReport | None = None,
    playground_result: RLPlaygroundResult | None = None,
    policy_result: PolicyEvaluationResult | None = None,
    context_score: ContextScoringResult | None = None,
    market_regime: MarketRegimeAnalysis | None = None,
    behavior_result: BehaviorAnalysisResult | None = None,
    semi_auto_decision: SemiAutoDecisionResult | None = None,
    reward_result: RewardEvaluationResult | None = None,
    config: SafeRLExperimentConfig | None = None,
) -> SafeRLExperimentResult:
    """Validate an offline RL experiment before it can be considered safe."""
    resolved_config = config or SafeRLExperimentConfig()
    quality = dataset_quality
    if quality is None and dataset is not None:
        quality = evaluate_dataset_quality(dataset)
    if quality is None and playground_result is not None:
        quality = evaluate_dataset_quality(playground_result.dataset)

    validations: list[SafeRLValidationResult] = []
    _validate_hard_safety_config(resolved_config, validations)
    _validate_dataset_quality(quality, resolved_config, validations)
    _validate_playground(playground_result, resolved_config, validations)
    _validate_policy(policy_result, resolved_config, validations)
    _validate_context(context_score, validations)
    _validate_market(market_regime, validations)
    _validate_behavior(behavior_result, resolved_config, validations)
    _validate_semi_auto(semi_auto_decision, validations)
    _validate_reward(reward_result, resolved_config, validations)

    return build_safe_rl_report(validations)


def evaluate_rl_safety(
    *,
    dataset: OfflineLearningDataset | None = None,
    dataset_quality: DatasetQualityReport | None = None,
    playground_result: RLPlaygroundResult | None = None,
    policy_result: PolicyEvaluationResult | None = None,
    context_score: ContextScoringResult | None = None,
    market_regime: MarketRegimeAnalysis | None = None,
    behavior_result: BehaviorAnalysisResult | None = None,
    semi_auto_decision: SemiAutoDecisionResult | None = None,
    reward_result: RewardEvaluationResult | None = None,
    config: SafeRLExperimentConfig | None = None,
) -> SafeRLExperimentResult:
    """Alias for validate_rl_experiment used by higher-level callers."""
    return validate_rl_experiment(
        dataset=dataset,
        dataset_quality=dataset_quality,
        playground_result=playground_result,
        policy_result=policy_result,
        context_score=context_score,
        market_regime=market_regime,
        behavior_result=behavior_result,
        semi_auto_decision=semi_auto_decision,
        reward_result=reward_result,
        config=config,
    )


def build_safe_rl_report(validations: tuple[SafeRLValidationResult, ...] | list[SafeRLValidationResult]) -> SafeRLExperimentResult:
    """Build an aggregate safety report from guardrail validations."""
    validation_tuple = tuple(validations)
    status = _aggregate_status(validation_tuple)
    active_guardrails = tuple(dict.fromkeys(validation.guardrail for validation in validation_tuple))
    risks = tuple(
        validation.message
        for validation in validation_tuple
        if validation.status in {SafeRLStatus.BLOCKED, SafeRLStatus.REVIEW_REQUIRED, SafeRLStatus.WARNING}
    )
    blocked = tuple(
        validation.guardrail.value
        for validation in validation_tuple
        if validation.status in {SafeRLStatus.BLOCKED, SafeRLStatus.REVIEW_REQUIRED}
    )
    allowed = ("offline_dry_run_policy_evaluation",) if status in {SafeRLStatus.SAFE, SafeRLStatus.WARNING} else ()
    recommendations = _recommendations(status, risks)
    return SafeRLExperimentResult(
        status=status,
        validations=validation_tuple,
        active_guardrails=active_guardrails,
        risks_detected=risks,
        allowed_experiments=allowed,
        blocked_experiments=blocked,
        recommendations=recommendations,
        safety_summary=_summary(status),
    )


def render_safe_rl_markdown(result: SafeRLExperimentResult) -> str:
    """Render the Safe RL experiment report as Markdown."""
    lines = [
        "# Safe RL Experiment Layer",
        "",
        "## Statut securite RL",
        "",
        f"- Status: {result.status.value}",
        f"- Summary: {result.safety_summary}",
        "",
        "## Resume validation",
        "",
        *_validation_lines(result.validations),
        "",
        "## Guardrails actifs",
        "",
        *_guardrail_lines(result.active_guardrails),
        "",
        "## Risques detectes",
        "",
        *_bullet_lines(result.risks_detected),
        "",
        "## Experiences autorisees",
        "",
        *_bullet_lines(result.allowed_experiments),
        "",
        "## Experiences bloquees",
        "",
        *_bullet_lines(result.blocked_experiments),
        "",
        "## Recommandations AGIcore",
        "",
        *_bullet_lines(result.recommendations),
        "",
        "- Offline only: no live broker, no real order, no neural training, no external ML.",
        "",
    ]
    return "\n".join(lines)


def _validate_hard_safety_config(
    config: SafeRLExperimentConfig,
    validations: list[SafeRLValidationResult],
) -> None:
    if config.dry_run_required and not config.dry_run:
        _add(validations, SafeRLGuardrail.REQUIRE_DRY_RUN, SafeRLStatus.BLOCKED, "Dry-run validation is required before any offline RL experiment.")
    else:
        _add(validations, SafeRLGuardrail.REQUIRE_DRY_RUN, SafeRLStatus.SAFE, "Dry-run validation is active.")
    if config.allow_live_broker:
        _add(validations, SafeRLGuardrail.FORBID_LIVE_BROKER, SafeRLStatus.BLOCKED, "Live broker access is forbidden for Safe RL experiments.")
    else:
        _add(validations, SafeRLGuardrail.FORBID_LIVE_BROKER, SafeRLStatus.SAFE, "Live broker access is disabled.")
    if config.allow_real_orders:
        _add(validations, SafeRLGuardrail.FORBID_REAL_ORDER, SafeRLStatus.BLOCKED, "Real orders are forbidden for Safe RL experiments.")
    else:
        _add(validations, SafeRLGuardrail.FORBID_REAL_ORDER, SafeRLStatus.SAFE, "Real order routing is disabled.")
    if config.allow_neural_training:
        _add(validations, SafeRLGuardrail.FORBID_NEURAL_TRAINING, SafeRLStatus.BLOCKED, "Neural network training is forbidden in this phase.")
    else:
        _add(validations, SafeRLGuardrail.FORBID_NEURAL_TRAINING, SafeRLStatus.SAFE, "Neural network training is disabled.")
    if config.allow_external_ml:
        _add(validations, SafeRLGuardrail.FORBID_EXTERNAL_ML, SafeRLStatus.BLOCKED, "External ML is forbidden for this offline layer.")
    else:
        _add(validations, SafeRLGuardrail.FORBID_EXTERNAL_ML, SafeRLStatus.SAFE, "External ML is disabled.")


def _validate_dataset_quality(
    quality: DatasetQualityReport | None,
    config: SafeRLExperimentConfig,
    validations: list[SafeRLValidationResult],
) -> None:
    if quality is None:
        _add(validations, SafeRLGuardrail.DATASET_QUALITY_MINIMUM, SafeRLStatus.REVIEW_REQUIRED, "Dataset quality report is missing.")
        _add(validations, SafeRLGuardrail.MINIMUM_TRANSITIONS_COUNT, SafeRLStatus.REVIEW_REQUIRED, "Dataset transition count is unknown.")
        return
    if quality.quality_score < config.min_dataset_quality_score:
        _add(validations, SafeRLGuardrail.DATASET_QUALITY_MINIMUM, SafeRLStatus.BLOCKED, f"Dataset quality {quality.quality_score}/100 is below minimum {config.min_dataset_quality_score}.")
    else:
        _add(validations, SafeRLGuardrail.DATASET_QUALITY_MINIMUM, SafeRLStatus.SAFE, f"Dataset quality {quality.quality_score}/100 meets the threshold.")
    if quality.transitions_count < config.min_transitions_count:
        _add(validations, SafeRLGuardrail.MINIMUM_TRANSITIONS_COUNT, SafeRLStatus.BLOCKED, f"Dataset has {quality.transitions_count} transitions; minimum is {config.min_transitions_count}.")
    else:
        _add(validations, SafeRLGuardrail.MINIMUM_TRANSITIONS_COUNT, SafeRLStatus.SAFE, f"Dataset has {quality.transitions_count} transitions.")


def _validate_playground(
    playground: RLPlaygroundResult | None,
    config: SafeRLExperimentConfig,
    validations: list[SafeRLValidationResult],
) -> None:
    if playground is None or playground.best_policy is None:
        _add(validations, SafeRLGuardrail.POLICY_SCORE_MINIMUM, SafeRLStatus.REVIEW_REQUIRED, "RL playground result or best policy is missing.")
        return
    best = playground.best_policy
    if best.final_score < config.min_policy_score:
        _add(validations, SafeRLGuardrail.POLICY_SCORE_MINIMUM, SafeRLStatus.BLOCKED, f"Best policy score {best.final_score}/100 is below minimum {config.min_policy_score}.")
    else:
        _add(validations, SafeRLGuardrail.POLICY_SCORE_MINIMUM, SafeRLStatus.SAFE, f"Best policy score {best.final_score}/100 meets the threshold.")
    aggressive = "aggressive" in best.candidate_name.casefold()
    high_risk = best.dangerous_decision_rate > config.max_dangerous_decision_rate
    if aggressive and high_risk:
        _add(validations, SafeRLGuardrail.BLOCK_AGGRESSIVE_HIGH_RISK, SafeRLStatus.BLOCKED, "Aggressive policy is blocked because dangerous decision rate is high.")
    elif high_risk:
        _add(validations, SafeRLGuardrail.BLOCK_AGGRESSIVE_HIGH_RISK, SafeRLStatus.WARNING, "Dangerous decision rate is above the configured threshold.")
    else:
        _add(validations, SafeRLGuardrail.BLOCK_AGGRESSIVE_HIGH_RISK, SafeRLStatus.SAFE, "Policy dangerous decision rate is within limits.")


def _validate_policy(
    policy: PolicyEvaluationResult | None,
    config: SafeRLExperimentConfig,
    validations: list[SafeRLValidationResult],
) -> None:
    if policy is None:
        return
    if policy.normalized_reward < config.min_policy_score:
        _add(validations, SafeRLGuardrail.POLICY_SCORE_MINIMUM, SafeRLStatus.BLOCKED, f"Policy evaluation normalized reward {policy.normalized_reward}/100 is too low.")
    if policy.dangerous_decisions > 0 and "AGGRESSIVE" in policy.policy.value:
        _add(validations, SafeRLGuardrail.BLOCK_AGGRESSIVE_HIGH_RISK, SafeRLStatus.BLOCKED, "Aggressive evaluated policy produced dangerous decisions.")


def _validate_context(
    context: ContextScoringResult | None,
    validations: list[SafeRLValidationResult],
) -> None:
    if context is None:
        return
    if context.decision == TradeContextDecision.NO_TRADE:
        _add(validations, SafeRLGuardrail.BLOCK_NO_TRADE_CONTEXT, SafeRLStatus.BLOCKED, "Context scoring decision is NO_TRADE.")
    else:
        _add(validations, SafeRLGuardrail.BLOCK_NO_TRADE_CONTEXT, SafeRLStatus.SAFE, f"Context decision is {context.decision.value}.")


def _validate_market(
    market: MarketRegimeAnalysis | None,
    validations: list[SafeRLValidationResult],
) -> None:
    if market is None:
        return
    if market.dangerous_market:
        _add(validations, SafeRLGuardrail.BLOCK_DANGEROUS_MARKET, SafeRLStatus.BLOCKED, "Market regime marks dangerous_market=True.")
    else:
        _add(validations, SafeRLGuardrail.BLOCK_DANGEROUS_MARKET, SafeRLStatus.SAFE, "Market regime is not marked dangerous.")


def _validate_behavior(
    behavior: BehaviorAnalysisResult | None,
    config: SafeRLExperimentConfig,
    validations: list[SafeRLValidationResult],
) -> None:
    if behavior is None:
        return
    classes = {_value(item) for item in behavior.classifications}
    if behavior.scores.emotional_risk_score >= config.max_emotional_risk_score:
        _add(validations, SafeRLGuardrail.BLOCK_HIGH_EMOTIONAL_RISK, SafeRLStatus.BLOCKED, f"Emotional risk score {behavior.scores.emotional_risk_score} is too high.")
    else:
        _add(validations, SafeRLGuardrail.BLOCK_HIGH_EMOTIONAL_RISK, SafeRLStatus.SAFE, "Emotional risk score is within limits.")
    if "OVERTRADING" in classes:
        _add(validations, SafeRLGuardrail.BLOCK_OVERTRADING, SafeRLStatus.BLOCKED, "Overtrading detected by behavior intelligence.")
    else:
        _add(validations, SafeRLGuardrail.BLOCK_OVERTRADING, SafeRLStatus.SAFE, "Overtrading was not detected.")
    if "REVENGE_TRADING_PROBABLE" in classes:
        _add(validations, SafeRLGuardrail.BLOCK_REVENGE_TRADING, SafeRLStatus.BLOCKED, "Revenge trading probable.")
    else:
        _add(validations, SafeRLGuardrail.BLOCK_REVENGE_TRADING, SafeRLStatus.SAFE, "Revenge trading was not detected.")


def _validate_semi_auto(
    semi: SemiAutoDecisionResult | None,
    validations: list[SafeRLValidationResult],
) -> None:
    if semi is None:
        return
    if semi.decision in {SemiAutoDecision.STOP_SESSION, SemiAutoDecision.BLOCK_TRADE, SemiAutoDecision.REVIEW_ONLY}:
        _add(validations, SafeRLGuardrail.BLOCK_NO_TRADE_CONTEXT, SafeRLStatus.REVIEW_REQUIRED, f"Semi-auto decision requires no-trade/review: {semi.decision.value}.")


def _validate_reward(
    reward: RewardEvaluationResult | None,
    config: SafeRLExperimentConfig,
    validations: list[SafeRLValidationResult],
) -> None:
    if reward is None:
        return
    if reward.normalized_reward < config.min_normalized_reward or reward.total_reward < config.min_total_reward:
        _add(validations, SafeRLGuardrail.BLOCK_NEGATIVE_REWARD, SafeRLStatus.BLOCKED, f"Reward is too negative: total={reward.total_reward}, normalized={reward.normalized_reward}/100.")
    else:
        _add(validations, SafeRLGuardrail.BLOCK_NEGATIVE_REWARD, SafeRLStatus.SAFE, "Reward is within configured bounds.")


def _aggregate_status(validations: tuple[SafeRLValidationResult, ...]) -> SafeRLStatus:
    statuses = {validation.status for validation in validations}
    if SafeRLStatus.BLOCKED in statuses:
        return SafeRLStatus.BLOCKED
    if SafeRLStatus.REVIEW_REQUIRED in statuses:
        return SafeRLStatus.REVIEW_REQUIRED
    if SafeRLStatus.WARNING in statuses:
        return SafeRLStatus.WARNING
    return SafeRLStatus.SAFE


def _recommendations(status: SafeRLStatus, risks: tuple[str, ...]) -> tuple[str, ...]:
    if status == SafeRLStatus.SAFE:
        return ("Continue offline dry-run evaluation only.",)
    actions = ["Keep the experiment offline and do not connect any broker or order route."]
    if risks:
        actions.append("Resolve blocked guardrails before using the dataset for future offline policy learning.")
    actions.append("Increase dataset quality and review dangerous transitions before rerunning the playground.")
    return tuple(dict.fromkeys(actions))


def _summary(status: SafeRLStatus) -> str:
    if status == SafeRLStatus.SAFE:
        return "Safe for offline dry-run analysis only."
    if status == SafeRLStatus.WARNING:
        return "Allowed only with caution inside offline dry-run boundaries."
    if status == SafeRLStatus.REVIEW_REQUIRED:
        return "Human review is required before continuing the offline experiment."
    return "Experiment is blocked by Safe RL guardrails."


def _validation_lines(values: tuple[SafeRLValidationResult, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {item.guardrail.value}: {item.status.value} - {item.message}" for item in values]


def _guardrail_lines(values: tuple[SafeRLGuardrail, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value.value}" for value in values]


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _add(
    validations: list[SafeRLValidationResult],
    guardrail: SafeRLGuardrail,
    status: SafeRLStatus,
    message: str,
) -> None:
    validations.append(SafeRLValidationResult(guardrail=guardrail, status=status, message=message))


def _value(value: object) -> str:
    return value.value if hasattr(value, "value") else str(value)


__all__ = [
    "build_safe_rl_report",
    "evaluate_rl_safety",
    "render_safe_rl_markdown",
    "validate_rl_experiment",
]
